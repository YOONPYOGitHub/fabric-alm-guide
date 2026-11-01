import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from tools import annotate_screenshots


class ScreenshotAnnotationTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        self.originals = root / "originals"
        self.originals.mkdir()
        self.output = root / "annotated"
        self.manifest = root / "annotations.json"
        self.original = self.originals / "sample.png"
        Image.new("RGB", (80, 60), "#808080").save(self.original)
        self.specification = {
            "sample.png": {
                "size": [80, 60],
                "boxes": [{"label": "Selected control", "rect": [10, 10, 40, 35]}],
            }
        }
        self.write_manifest()
        replacements = patch.multiple(
            annotate_screenshots,
            ORIGINALS=self.originals,
            OUTPUT=self.output,
            MANIFEST=self.manifest,
        )
        replacements.start()
        self.addCleanup(replacements.stop)

    def write_manifest(self) -> None:
        self.manifest.write_text(json.dumps(self.specification), encoding="utf-8")

    def test_adds_outline_without_changing_original_or_interior(self) -> None:
        original_bytes = self.original.read_bytes()
        with redirect_stdout(StringIO()):
            annotate_screenshots.main()
        self.assertEqual(self.original.read_bytes(), original_bytes)
        with Image.open(self.output / "sample.png") as result:
            self.assertEqual(result.size, (80, 60))
            self.assertEqual(result.getpixel((10, 10)), (255, 0, 0))
            self.assertEqual(result.getpixel((20, 20)), (128, 128, 128))
            self.assertEqual(result.getpixel((0, 0)), (128, 128, 128))

    def test_rejects_changed_capture_dimensions(self) -> None:
        self.specification["sample.png"]["size"] = [81, 60]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "dimensions changed"):
            annotate_screenshots.main()

    def test_rejects_rectangle_at_or_beyond_image_boundary(self) -> None:
        self.specification["sample.png"]["boxes"][0]["rect"] = [10, 10, 80, 35]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "outside image"):
            annotate_screenshots.main()

    def test_requires_manifest_entry_for_every_original(self) -> None:
        self.manifest.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "every original PNG"):
            annotate_screenshots.main()

    def test_rejects_more_than_two_callouts(self) -> None:
        box = self.specification["sample.png"]["boxes"][0]
        self.specification["sample.png"]["boxes"] = [box, box, box]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "at most 2"):
            annotate_screenshots.main()

    def test_empty_callouts_require_explicit_overview(self) -> None:
        self.specification["sample.png"]["boxes"] = []
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "No callouts"):
            annotate_screenshots.main()

    def test_overview_preserves_every_pixel_without_callouts(self) -> None:
        self.specification = {
            "sample.png": {"size": [80, 60], "boxes": [], "overview": True}
        }
        self.write_manifest()
        with redirect_stdout(StringIO()):
            annotate_screenshots.main()
        with Image.open(self.original) as original, Image.open(
            self.output / "sample.png"
        ) as annotated:
            self.assertEqual(original.tobytes(), annotated.tobytes())

    def test_supports_chapter_directories(self) -> None:
        chapter = self.originals / "03"
        chapter.mkdir()
        nested = chapter / "01-local-clone-feature-v1.png"
        self.original.rename(nested)
        original_bytes = nested.read_bytes()
        self.specification = {
            "03/01-local-clone-feature-v1.png": self.specification["sample.png"]
        }
        self.write_manifest()
        with redirect_stdout(StringIO()):
            annotate_screenshots.main()
        self.assertEqual(nested.read_bytes(), original_bytes)
        with Image.open(self.output / "03/01-local-clone-feature-v1.png") as result:
            self.assertEqual(result.size, (80, 60))
            self.assertEqual(result.getpixel((10, 10)), (255, 0, 0))
            self.assertEqual(result.getpixel((20, 20)), (128, 128, 128))

    def test_rejects_unsafe_or_noncanonical_paths(self) -> None:
        for filename in (
            "../escape.png",
            "03/../escape.png",
            "/tmp/escape.png",
            "./sample.png",
            "03//sample.png",
            r"03\sample.png",
            "C:/sample.png",
            "03/sample.jpg",
        ):
            with self.subTest(filename=filename):
                self.specification = {filename: {"size": [80, 60], "boxes": []}}
                self.write_manifest()
                with self.assertRaisesRegex(ValueError, "Invalid screenshot name"):
                    annotate_screenshots.main()


if __name__ == "__main__":
    unittest.main()

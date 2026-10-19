import hashlib
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageChops, ImageDraw

from tools.annotate_screenshots import STROKE_WIDTH

ROOT = Path(__file__).resolve().parents[1]


class GuideIntegrityTests(unittest.TestCase):
    def test_relative_markdown_links_exist(self) -> None:
        for document in ROOT.glob("*.md"):
            text = document.read_text(encoding="utf-8")
            for match in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                target = urlsplit(match.group(1))
                if target.scheme or not target.path:
                    continue
                path = (document.parent / unquote(target.path)).resolve()
                with self.subTest(document=document.name, link=match.group(1)):
                    self.assertTrue(path.is_relative_to(ROOT))
                    self.assertTrue(path.exists(), str(path))

    def test_every_capture_is_documented_and_generated(self) -> None:
        annotations = json.loads(
            (ROOT / "tools/screenshot_annotations.json").read_text()
        )
        referenced = set()
        for document in ROOT.glob("*.md"):
            referenced.update(
                re.findall(
                    r"!\[[^\]]*\]\(screenshots/([^)]+\.png)\)",
                    document.read_text(encoding="utf-8"),
                )
            )
        self.assertEqual(set(annotations), referenced)
        self.assertEqual(
            set(annotations),
            {path.name for path in (ROOT / "screenshots-originals").glob("*.png")},
        )
        self.assertEqual(
            set(annotations),
            {path.name for path in (ROOT / "screenshots").glob("*.png")},
        )

    def test_original_hashes_and_all_pixels_outside_outlines_are_preserved(
        self,
    ) -> None:
        annotations = json.loads(
            (ROOT / "tools/screenshot_annotations.json").read_text()
        )
        for filename, specification in annotations.items():
            with self.subTest(capture=filename):
                original_path = ROOT / "screenshots-originals" / filename
                self.assertEqual(
                    hashlib.sha256(original_path.read_bytes()).hexdigest(),
                    specification["originalSha256"],
                )
                with (
                    Image.open(original_path) as raw,
                    Image.open(ROOT / "screenshots" / filename) as annotated,
                ):
                    self.assertEqual(raw.size, tuple(specification["size"]))
                    self.assertEqual(raw.size, annotated.size)
                    before = raw.convert("RGB")
                    after = annotated.convert("RGB")
                    outside = Image.new("RGB", before.size, "white")
                    draw = ImageDraw.Draw(outside)
                    self.assertLessEqual(len(specification["boxes"]), 2)
                    for box in specification["boxes"]:
                        draw.rectangle(box["rect"], outline="black", width=STROKE_WIDTH)
                        left, top, _, _ = box["rect"]
                        self.assertEqual(after.getpixel((left, top)), (255, 0, 0))
                    difference = ImageChops.multiply(
                        ImageChops.difference(before, after), outside
                    )
                    self.assertIsNone(difference.getbbox())

    def test_record_distinguishes_verified_data_from_pending_approvals(self) -> None:
        evidence = json.loads(
            (ROOT / "evidence/workshop-verification.json").read_text()
        )
        self.assertFalse(evidence["workshopComplete"])
        self.assertEqual(
            evidence["approvalStatus"]["humanReview"], "conversation-authorized"
        )
        self.assertTrue(evidence["approvalStatus"]["merged"])
        self.assertFalse(evidence["approvalStatus"]["independentGitHubApproval"])
        self.assertEqual(
            evidence["sourceMerge"]["mergeCommit"], evidence["git"]["main"]
        )
        self.assertEqual(evidence["sourceMerge"]["head"], evidence["git"]["feature"])
        self.assertEqual(evidence["sourceMerge"]["base"], evidence["git"]["baseline"])
        self.assertFalse(evidence["approvalStatus"]["productionReleaseApproved"])
        self.assertFalse(evidence["approvalStatus"]["productionDeployed"])
        self.assertEqual(evidence["production"]["items"], [])
        self.assertEqual(
            {(run["stage"], run["metrics"]["release"]) for run in evidence["runs"]},
            {
                ("development", "v1"),
                ("feature", "v2"),
                ("test", "v1"),
                ("development", "v2"),
                ("test", "v2"),
            },
        )
        self.assertEqual(
            len({run["metrics"]["workspaceId"] for run in evidence["runs"]}), 3
        )
        self.assertEqual(
            len({run["metrics"]["lakehouseId"] for run in evidence["runs"]}), 3
        )
        for run in evidence["runs"]:
            metrics = run["metrics"]
            self.assertEqual(run["status"], "Completed")
            self.assertEqual(metrics["rows"], 10)
            self.assertEqual(metrics["unique_ids"], 10)
            self.assertEqual((metrics["min_id"], metrics["max_id"]), (0, 9))
            self.assertEqual(metrics["release_versions"], 1)
            self.assertEqual(
                metrics["sum_value"], {"v1": 45, "v2": 90}[metrics["release"]]
            )
            self.assertTrue(
                metrics["deltaLocation"].startswith(
                    f"abfss://{metrics['workspaceId']}@onelake.dfs.fabric.microsoft.com/"
                )
            )
            self.assertTrue(
                metrics["deltaLocation"].endswith(
                    f"/{metrics['lakehouseId']}/Tables/dbo/cicd_smoke"
                )
            )
        self.assertEqual(evidence["testTableBefore"]["httpStatus"], 404)
        self.assertEqual(evidence["testTableBefore"]["errorCode"], "PathNotFound")
        self.assertEqual(evidence["testTableAfter"]["httpStatus"], 200)
        operations = evidence["pipeline"]["operations"]
        self.assertEqual(len(operations), 2)
        self.assertTrue(all(op["status"] == "Succeeded" for op in operations))
        self.assertEqual(
            {op["preDeploymentDiffInformation"]["newItemsCount"] for op in operations},
            {0, 2},
        )
        release = next(
            op for op in operations if op["note"]["content"].startswith("Approved v2;")
        )
        self.assertEqual(
            release["preDeploymentDiffInformation"]["differentItemsCount"], 1
        )
        self.assertIn(evidence["git"]["main"], release["note"]["content"])
        self.assertTrue(
            evidence["deploymentRules"]["Test"]["nextDeploymentEffectVerified"]
        )


if __name__ == "__main__":
    unittest.main()

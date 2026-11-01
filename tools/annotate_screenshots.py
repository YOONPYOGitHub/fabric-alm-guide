"""Add guide callouts without changing the original screenshots."""

import json
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "screenshots-originals"
OUTPUT = ROOT / "screenshots"
MANIFEST = Path(__file__).with_name("screenshot_annotations.json")
COLOR = "#FF0000"
STROKE_WIDTH = 4
MAX_CALLOUTS = 2


def main() -> None:
    annotations = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for filename in annotations:
        relative = PurePosixPath(filename)
        if (
            relative.is_absolute()
            or relative.as_posix() != filename
            or ".." in relative.parts
            or "\\" in filename
            or ":" in filename
            or relative.suffix != ".png"
        ):
            raise ValueError(f"Invalid screenshot name: {filename}")
    original_names = {
        path.relative_to(ORIGINALS).as_posix() for path in ORIGINALS.rglob("*.png")
    }
    if set(annotations) != original_names:
        raise ValueError("Annotation manifest must match every original PNG exactly.")
    OUTPUT.mkdir(exist_ok=True)
    count = 0
    for filename, specification in annotations.items():
        with Image.open(ORIGINALS / filename) as original:
            if original.format != "PNG" or original.size != tuple(specification["size"]):
                raise ValueError(f"Original image dimensions changed: {filename}")
            annotated = original.copy()
        rectangles = specification["boxes"]
        if not rectangles and specification.get("overview") is not True:
            raise ValueError(f"No callouts specified: {filename}")
        if len(rectangles) > MAX_CALLOUTS:
            raise ValueError(f"Too many callouts; use at most {MAX_CALLOUTS}: {filename}")
        draw = ImageDraw.Draw(annotated)
        for rectangle in rectangles:
            coordinates = rectangle["rect"]
            if (
                not rectangle["label"]
                or len(coordinates) != 4
                or any(type(value) is not int for value in coordinates)
            ):
                raise ValueError(f"Invalid callout: {filename}")
            left, top, right, bottom = coordinates
            if not (
                0 <= left < right < annotated.width
                and 0 <= top < bottom < annotated.height
                and right - left > STROKE_WIDTH * 2
                and bottom - top > STROKE_WIDTH * 2
            ):
                raise ValueError(f"Callout outside image: {filename}: {coordinates}")
            draw.rectangle((left, top, right, bottom), outline=COLOR, width=STROKE_WIDTH)
            count += 1
        destination = OUTPUT / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        annotated.save(destination, format="PNG", optimize=True)
    print(f"Processed {len(annotations)} screenshots with {count} red callouts.")


if __name__ == "__main__":
    main()

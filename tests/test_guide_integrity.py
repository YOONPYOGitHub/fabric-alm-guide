import hashlib
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageChops, ImageDraw

from tools.annotate_screenshots import STROKE_WIDTH

ROOT = Path(__file__).resolve().parents[1]


class GuideIntegrityTests(unittest.TestCase):
    def test_linux_shell_examples_use_python3(self) -> None:
        for document in (*ROOT.glob("*.md"), *ROOT.glob("examples/**/*.md")):
            text = document.read_text(encoding="utf-8")
            for block in re.findall(r"```(?:bash|sh|shell)\n(.*?)```", text, re.S):
                with self.subTest(document=document.name, block=block):
                    self.assertNotRegex(block, r"(?m)^\s*(?:\$\s+)?python(?:\s|$)")

    def test_instructions_do_not_depend_on_the_completed_lab_repository(self) -> None:
        for document in (*ROOT.glob("*.md"), *ROOT.glob("examples/**/*.md")):
            if document.name == "06-execution-record.md":
                continue
            with self.subTest(document=document.name):
                self.assertNotRegex(
                    document.read_text(encoding="utf-8"),
                    r"https://github\.com/YOONPYOGitHub/fabric-alm-lab(?:[/)#\s]|$)",
                )

    def test_relative_markdown_links_exist(self) -> None:
        for document in (*ROOT.glob("*.md"), *ROOT.glob("examples/**/*.md")):
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

    def test_completed_record_requires_real_approvals_and_stage_local_data(
        self,
    ) -> None:
        evidence = json.loads(
            (ROOT / "evidence/workshop-verification.json").read_text()
        )
        self.assertIs(evidence["workshopComplete"], True)
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
        self.assertIs(evidence["approvalStatus"]["productionReleaseApproved"], True)
        self.assertIs(evidence["approvalStatus"]["productionDeployed"], True)
        approval = evidence["approvalStatus"]["productionAuthorization"]
        self.assertIs(approval["approved"], True)
        self.assertIs(approval["costAcknowledged"], True)
        self.assertIs(approval["nativeFabricApprovalWorkflowConfigured"], False)
        self.assertEqual(approval["workspaceId"], evidence["production"]["workspaceId"])
        self.assertEqual(approval["sourceMainCommit"], evidence["git"]["main"])
        self.assertEqual((approval["expectedRows"], approval["expectedSum"]), (10, 90))
        self.assertEqual(
            {item["type"] for item in evidence["production"]["items"]},
            {"Lakehouse", "Notebook", "SQLEndpoint"},
        )
        self.assertEqual(
            {(run["stage"], run["metrics"]["release"]) for run in evidence["runs"]},
            {
                ("development", "v1"),
                ("feature", "v2"),
                ("test", "v1"),
                ("development", "v2"),
                ("test", "v2"),
                ("production", "v2"),
            },
        )
        self.assertEqual(
            len({run["metrics"]["workspaceId"] for run in evidence["runs"]}), 4
        )
        self.assertEqual(
            len({run["metrics"]["lakehouseId"] for run in evidence["runs"]}), 4
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
        self.assertEqual(len(operations), 3)
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
        production = next(
            op
            for op in operations
            if op["note"]["content"].startswith("Approved Production v2;")
        )
        self.assertEqual(production["preDeploymentDiffInformation"]["newItemsCount"], 2)
        self.assertEqual(
            (production["sourceStageId"], production["targetStageId"]),
            (
                "c563f05c-e04b-467f-b544-6a3a08710e95",
                "90d5d2db-45d4-41bd-b62e-21385fafb6b6",
            ),
        )
        self.assertIn(evidence["git"]["main"], production["note"]["content"])
        approved_at = datetime.fromisoformat(approval["approvedAtUtc"])
        deployed_at = datetime.fromisoformat(production["executionStartTime"]).replace(
            tzinfo=timezone.utc
        )
        self.assertLess(approved_at, deployed_at)
        self.assertEqual(evidence["productionTableBefore"]["httpStatus"], 404)
        self.assertEqual(evidence["productionTableBefore"]["errorCode"], "PathNotFound")
        self.assertEqual(evidence["productionTableAfter"]["httpStatus"], 200)
        definitions = evidence["definitionVerification"]["stages"]
        self.assertEqual(
            set(definitions), {"development", "feature", "test", "production"}
        )
        self.assertEqual(
            len({item["normalizedAstSha256"] for item in definitions.values()}), 1
        )
        for stage, definition in definitions.items():
            current_run = next(
                run
                for run in evidence["runs"]
                if run["stage"] == stage and run["metrics"]["release"] == "v2"
            )
            self.assertEqual(
                definition["workspaceId"], current_run["metrics"]["workspaceId"]
            )
            self.assertEqual(
                definition["lakehouseId"], current_run["metrics"]["lakehouseId"]
            )
            self.assertEqual(definition["sourceCommit"], evidence["git"]["main"])
            self.assertEqual(definition["cells"], 3)


if __name__ == "__main__":
    unittest.main()

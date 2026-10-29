import ast
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
CELL_MARKER = "# CELL ********************"


class WorkshopExampleTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        cicd = self.root / "workshops" / "cicd"
        notebook = cicd / "fabric" / "CI_CD_Smoke.Notebook"
        lakehouse = cicd / "fabric" / "CI_CD_Demo.Lakehouse"
        tests = cicd / "tests"
        for path in (notebook, lakehouse, tests):
            path.mkdir(parents=True)
        self.source = notebook / "notebook-content.py"
        self.settings = notebook / "notebook-settings.json"
        metadata = {
            "dependencies": {
                "lakehouse": {
                    "default_lakehouse": "test-logical-id",
                    "default_lakehouse_workspace_id": "00000000-0000-0000-0000-000000000000",
                }
            }
        }
        header = "\n".join(
            f"# META {line}" for line in json.dumps(metadata, indent=2).splitlines()
        )
        self.source.write_text(
            header + "\n\n" + (EXAMPLES / "notebook-v1.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (lakehouse / ".platform").write_text(
            json.dumps({"config": {"logicalId": "test-logical-id"}}), encoding="utf-8"
        )
        self.settings.write_text(
            json.dumps({"auto-binding": {"lakehouse": "on"}}), encoding="utf-8"
        )
        shutil.copyfile(EXAMPLES / "test_smoke_contract.py", tests / "test_smoke_contract.py")

    def run_contract(self) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "workshops/cicd/tests",
                "-v",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("Ran 9 tests", result.stderr)
        return result

    def test_example_has_three_code_cells_and_no_environment_metadata(self) -> None:
        source = (EXAMPLES / "notebook-v1.py").read_text(encoding="utf-8")
        self.assertNotIn("# META", source)
        cells = source.split(CELL_MARKER)
        self.assertEqual(cells[0].strip(), "")
        self.assertEqual(len(cells), 4)
        for cell in cells[1:]:
            self.assertTrue(ast.parse(cell).body)
        self.assertNotRegex(
            source, r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}"
        )

    def test_copied_contract_passes_for_v1(self) -> None:
        result = self.run_contract()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_copied_contract_passes_for_v2(self) -> None:
        source = self.source.read_text(encoding="utf-8")
        self.source.write_text(
            source.replace('RELEASE = "v1"', 'RELEASE = "v2"').replace(
                "MULTIPLIER = 1", "MULTIPLIER = 2"
            ),
            encoding="utf-8",
        )
        result = self.run_contract()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_copied_contract_rejects_mismatched_release(self) -> None:
        self.source.write_text(
            self.source.read_text(encoding="utf-8").replace(
                'RELEASE = "v1"', 'RELEASE = "v2"'
            ),
            encoding="utf-8",
        )
        result = self.run_contract()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAILED (failures=1)", result.stderr)
        self.assertIn("FAIL: test_release_and_multiplier_agree", result.stderr)

    def test_copied_contract_rejects_wrong_logical_binding(self) -> None:
        self.source.write_text(
            self.source.read_text(encoding="utf-8").replace(
                "test-logical-id", "another-logical-id"
            ),
            encoding="utf-8",
        )
        result = self.run_contract()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAILED (failures=1)", result.stderr)
        self.assertIn("FAIL: test_git_binding_matches", result.stderr)

    def test_copied_contract_rejects_disabled_auto_binding(self) -> None:
        self.settings.write_text(
            json.dumps({"auto-binding": {"lakehouse": "off"}}), encoding="utf-8"
        )
        result = self.run_contract()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAILED (failures=1)", result.stderr)
        self.assertIn("FAIL: test_git_binding_matches", result.stderr)

    def test_copied_contract_rejects_missing_export(self) -> None:
        self.source.unlink()
        result = self.run_contract()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("FAILED (errors=9)", result.stderr)


if __name__ == "__main__":
    unittest.main()

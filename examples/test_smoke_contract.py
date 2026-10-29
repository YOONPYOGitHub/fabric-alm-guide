"""Offline source/binding checks; copy to the lab's workshops/cicd/tests directory."""

import ast
import json
import unittest
from collections.abc import Callable, Mapping
from pathlib import Path
from types import FunctionType

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "fabric" / "CI_CD_Smoke.Notebook"
SOURCE = NOTEBOOK / "notebook-content.py"


def load_guard() -> Callable[[Mapping[str, object]], dict[str, str]]:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "require_local_lakehouse"
    )
    namespace: dict[str, object] = {"Mapping": Mapping}
    exec(
        compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), "exec"),
        namespace,
    )
    guard = namespace["require_local_lakehouse"]
    if not isinstance(guard, FunctionType):
        raise TypeError("Expected the source-defined Lakehouse guard.")
    return guard


class SmokeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = load_guard()
        self.context: dict[str, object] = {
            "currentWorkspaceName": "Development",
            "currentWorkspaceId": "development-workspace",
            "defaultLakehouseName": "CI_CD_Demo",
            "defaultLakehouseId": "development-lakehouse",
            "defaultLakehouseWorkspaceId": "development-workspace",
        }

    def test_accepts_stage_local_binding(self) -> None:
        self.assertEqual(self.guard(self.context), self.context)

    def test_workspace_identity_is_case_insensitive(self) -> None:
        self.context["defaultLakehouseWorkspaceId"] = "DEVELOPMENT-WORKSPACE"
        self.assertEqual(self.guard(self.context), self.context)

    def test_rejects_each_missing_context_field(self) -> None:
        for key in self.context:
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                self.guard({k: v for k, v in self.context.items() if k != key})

    def test_rejects_empty_and_non_string_context_values(self) -> None:
        for key in self.context:
            for value in ("", None, 42):
                with self.subTest(key=key, value=value), self.assertRaises(RuntimeError):
                    self.guard({**self.context, key: value})

    def test_rejects_source_workspace_binding(self) -> None:
        self.context["defaultLakehouseWorkspaceId"] = "another-workspace"
        with self.assertRaisesRegex(RuntimeError, "different workspace"):
            self.guard(self.context)

    def test_rejects_unexpected_lakehouse_name(self) -> None:
        self.context["defaultLakehouseName"] = "Unexpected"
        with self.assertRaisesRegex(RuntimeError, "stage-local"):
            self.guard(self.context)

    def test_guard_runs_before_any_spark_action(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        guard_line = next(
            node.lineno
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "require_local_lakehouse"
        )
        spark_lines = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and node.id == "spark"
        ]
        self.assertTrue(spark_lines)
        self.assertLess(guard_line, min(spark_lines))

    def test_release_and_multiplier_agree(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        values = {
            target.id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name) and target.id in ("RELEASE", "MULTIPLIER")
        }
        self.assertIn(values["RELEASE"], ("v1", "v2"))
        self.assertEqual(values["MULTIPLIER"], {"v1": 1, "v2": 2}[values["RELEASE"]])
        self.assertEqual(
            len(SOURCE.read_text(encoding="utf-8").split("# CELL ********************")),
            4,
        )

    def test_git_binding_matches_versioned_lakehouse_logical_id(self) -> None:
        source = SOURCE.read_text(encoding="utf-8").split("# CELL", 1)[0]
        metadata = json.loads(
            "\n".join(
                line.removeprefix("# META ")
                for line in source.splitlines()
                if line.startswith("# META ")
            )
        )
        platform = json.loads(
            (ROOT / "fabric" / "CI_CD_Demo.Lakehouse" / ".platform").read_text()
        )
        settings = json.loads((NOTEBOOK / "notebook-settings.json").read_text())
        binding = metadata["dependencies"]["lakehouse"]
        self.assertEqual(binding["default_lakehouse"], platform["config"]["logicalId"])
        self.assertEqual(
            binding["default_lakehouse_workspace_id"],
            "00000000-0000-0000-0000-000000000000",
        )
        self.assertEqual(settings["auto-binding"]["lakehouse"], "on")


if __name__ == "__main__":
    unittest.main()

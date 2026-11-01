import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class GuideIntegrityTests(unittest.TestCase):
    def test_linux_shell_examples_use_python3(self) -> None:
        for document in (*ROOT.glob("*.md"), *ROOT.glob("examples/**/*.md")):
            text = document.read_text(encoding="utf-8")
            for block in re.findall(
                r"^[ \t]*```(?:bash|sh|shell)\n(.*?)^[ \t]*```", text, re.M | re.S
            ):
                with self.subTest(document=document.name, block=block):
                    self.assertNotRegex(block, r"(?m)^\s*(?:\$\s+)?python(?:\s|$)")

    def test_instructions_do_not_depend_on_the_completed_lab_repository(self) -> None:
        for document in (*ROOT.glob("*.md"), *ROOT.glob("examples/**/*.md")):
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
                if target.scheme:
                    continue
                path = (
                    (document.parent / unquote(target.path)).resolve()
                    if target.path
                    else document
                )
                with self.subTest(document=document.name, link=match.group(1)):
                    self.assertTrue(path.is_relative_to(ROOT))
                    self.assertTrue(path.exists(), str(path))
                    if not target.fragment or path.suffix != ".md":
                        continue
                    destination = path.read_text(encoding="utf-8")
                    anchors = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', destination))
                    counts: dict[str, int] = {}
                    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", destination, re.M):
                        slug = re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                        count = counts.get(slug, 0)
                        anchors.add(f"{slug}-{count}" if count else slug)
                        counts[slug] = count + 1
                    self.assertIn(unquote(target.fragment), anchors)

    def test_readme_focuses_on_git_and_pipeline_overview(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(
            re.findall(r"^## (\d+)\. (.+)$", readme, re.M),
            [
                ("1", "무엇을 배우는가"),
                ("2", "전체 구성과 Workspace 역할"),
                ("3", "실습 순서"),
                ("4", "시작 전에 알아둘 사항"),
                ("5", "참고 자료"),
            ],
        )
        self.assertLessEqual(len(readme.splitlines()), 165)
        self.assertIn("GitHub branch ↔ Workspace", readme)
        self.assertIn("Development → Test → Production", readme)
        self.assertIn("Fabric Source control의 **Commit**", readme)
        self.assertIn("**Update**로 GitHub의 변경을 Workspace에 반영", readme)
        self.assertIn("환경별 Workspace를 Pipeline 단계에 할당", readme)
        self.assertIn("GitHub의 PR 병합과 Workspace 간 배포는 별개의 작업", readme)
        self.assertNotIn("1~6장이 핵심 핸즈온입니다", readme)
        self.assertIn("Pipeline에는 포함하지 않음", readme)
        self.assertIn("아이템 정의입니다", readme)
        self.assertIn("단계 배포로 복사되지 않습니다", readme)
        self.assertIn("각 Workspace의 Notebook을 실행", readme)
        self.assertIn("PR 병합 승인과 Production 릴리스 승인은 별개", readme)
        self.assertIn("Spark는 CU를, Delta 데이터는 저장소를 사용합니다", readme)
        self.assertNotIn("현재 확인한 결과", readme)
        self.assertNotRegex(readme, r"\b(?:4ea83edb|09b03c28|0cf51fd)\b")
        for summary in (
            "운영 적용 시 권한과 역할 분리",
            "가이드 유지보수·검증 기록·보관 캡처",
        ):
            self.assertIn(f"<details>\n<summary>{summary}</summary>", readme)

    def test_readme_diagram_separates_git_sync_and_pipeline_deployment(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        diagrams = re.findall(r"^```mermaid\n(.*?)^```", readme, re.M | re.S)
        self.assertEqual(len(diagrams), 1)
        diagram = diagrams[0]
        self.assertIn('subgraph github["GitHub"]', diagram)
        self.assertIn('subgraph fabric["Microsoft Fabric"]', diagram)
        self.assertIn('featureGit <-->|"Git integration"| featureWs', diagram)
        self.assertIn('mainGit <-->|"Git integration"| devWs', diagram)
        self.assertIn('-->|"PR 검토·병합"| mainGit', diagram)
        self.assertIn('devWs["Development Workspace"]:::workspace -->|"배포"| testWs', diagram)
        self.assertIn('testWs -->|"Test 검증 + 릴리스 승인 후 배포"| prodWs', diagram)
        pipeline = re.search(
            r'subgraph pipeline\["Deployment pipelines"\]\n(.*?)\n\s*end',
            diagram,
            re.S,
        )
        self.assertIsNotNone(pipeline)
        assert pipeline is not None
        self.assertEqual(re.findall(r"(\w+)\[", pipeline.group(1)), ["devWs", "testWs", "prodWs"])

    def test_workshop_chapters_follow_sequential_navigation(self) -> None:
        chapters = (
            "01-prerequisites.md",
            "02-lakehouse-notebook.md",
            "03-git-integration.md",
            "04-deployment-pipelines.md",
            "05-pr-merge-dev-update.md",
            "06-test-production-release.md",
            "07-validation-and-recovery.md",
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        overview = re.findall(r"^\| [1-7] \| \[[^\]]+\]\(([^)]+)\)", readme, re.M)
        self.assertEqual(overview, list(chapters))
        for number, name in enumerate(chapters, start=1):
            with self.subTest(chapter=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertRegex(text, rf"^# {number}\. ")
                sections = re.findall(r"^## (\d+)-(\d+)\. ", text, re.M)
                self.assertTrue(sections)
                self.assertEqual(
                    sections,
                    [(str(number), str(index)) for index in range(1, len(sections) + 1)],
                )
                previous = chapters[number - 2] if number > 1 else "README.md"
                following = chapters[number] if number < len(chapters) else "README.md"
                footer = text.split("## 다음으로 이동", 1)[1]
                self.assertIn(f"]({previous})", footer)
                self.assertIn(f"]({following})", footer)
                self.assertIn(f"]({following})", text.splitlines()[2])

    def test_handson_ends_at_closing_chapter(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        closing = (ROOT / "07-validation-and-recovery.md").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "08-execution-record.md").exists())
        self.assertNotRegex(readme, r"(?m)^\| 별첨 \|")
        self.assertNotIn("08-execution-record.md", readme)
        self.assertNotIn("08-execution-record.md", closing)
        self.assertEqual(re.findall(r"^## 7-(\d+)\.", closing, re.M), ["1", "2", "3"])
        self.assertIn("기본 핸즈온은 종료됩니다", closing)
        self.assertIn("Capacity 비용이 중지되지는 않습니다", closing)
        self.assertIn("Workspace 삭제 전에는 Pipeline 단계 할당을 해제", closing)

    def test_baseline_precedes_merge_and_release_actions(self) -> None:
        git = (ROOT / "03-git-integration.md").read_text(encoding="utf-8")
        baseline = (ROOT / "04-deployment-pipelines.md").read_text(encoding="utf-8")
        merge = (ROOT / "05-pr-merge-dev-update.md").read_text(encoding="utf-8")
        release = (ROOT / "06-test-production-release.md").read_text(encoding="utf-8")
        self.assertIn("PR은 **Open**", git)
        self.assertNotIn("<a id=\"merge-and-dev-update\">", git)
        self.assertIn("PR은 아직 Open", baseline)
        self.assertIn("10행·합계 45", baseline)
        self.assertNotIn("<a id=\"release-v2\">", baseline)
        self.assertIn("Test v1의 10행·합계 45를 확인", merge)
        self.assertIn("**Merge pull request**를 선택", merge)
        self.assertIn("Test는 아직 v1·합계 45", merge)
        self.assertIn("Dev v2의 실제 10행·합계 90", release)
        self.assertIn("승인이 없으면 Production 배포를 진행하지 않습니다", release)
        self.assertLess(
            release.index("## 6-1. Dev v2 → Test v2"),
            release.index("## 6-2. 릴리스 승인 후 Test → Production"),
        )

    def test_action_chapters_do_not_use_historical_commit_ids(self) -> None:
        for path in ROOT.glob("0[3-6]-*.md"):
            with self.subTest(document=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"\b(?:4ea83edb|09b03c28|0cf51fd)\b")
                self.assertNotIn("그래 계속 진행해", text)

    def test_every_final_capture_is_documented(self) -> None:
        referenced = set()
        for document in ROOT.glob("*.md"):
            referenced.update(
                re.findall(
                    r"!\[[^\]]*\]\(screenshots/([^)]+\.png)\)",
                    document.read_text(encoding="utf-8"),
                )
            )
        self.assertTrue(referenced)
        self.assertEqual(
            referenced,
            {
                path.relative_to(ROOT / "screenshots").as_posix()
                for path in (ROOT / "screenshots").rglob("*.png")
            },
        )

    def test_screenshots_follow_chapter_appearance_order(self) -> None:
        filenames = {
            path.relative_to(ROOT / "screenshots").as_posix()
            for path in (ROOT / "screenshots").rglob("*.png")
        }
        owners = {"00": ROOT / "README.md", "08": ROOT / "README.md"}
        owners.update(
            {
                document.name[:2]: document
                for document in ROOT.glob("0[1-8]-*.md")
                if not document.name.endswith("_old.md")
            }
        )
        for filename in filenames:
            with self.subTest(capture=filename):
                self.assertRegex(filename, r"^[0-9]{2}/[0-9]{2}-[a-z0-9-]+\.png$")
                chapter = filename.split("/", 1)[0]
                self.assertIn(chapter, owners)
        for chapter, document in owners.items():
            images = re.findall(
                rf"!\[[^\]]*\]\(screenshots/({chapter}/[^)]+\.png)\)",
                document.read_text(encoding="utf-8"),
            )
            with self.subTest(document=document.name):
                self.assertEqual(len(images), len(set(images)))
                self.assertEqual(
                    [Path(image).name[:2] for image in images],
                    [f"{number:02}" for number in range(1, len(images) + 1)],
                )
                self.assertEqual(
                    set(images),
                    {filename for filename in filenames if filename.startswith(f"{chapter}/")},
                )

    def test_final_captures_have_png_headers(self) -> None:
        for image in (ROOT / "screenshots").rglob("*.png"):
            with self.subTest(capture=image.relative_to(ROOT).as_posix()):
                with image.open("rb") as stream:
                    header = stream.read(24)
                self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(header[8:12], b"\x00\x00\x00\r")
                self.assertEqual(header[12:16], b"IHDR")
                self.assertGreater(int.from_bytes(header[16:20], "big"), 0)
                self.assertGreater(int.from_bytes(header[20:24], "big"), 0)

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

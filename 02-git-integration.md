# 3. GitHub 연결, Feature branch, PR과 Dev Update

[처음으로](README.md) · [이전: Lakehouse + Notebook](02a-lakehouse-notebook.md) · [다음: 배포](03-deployment-pipelines.md)

**목표:** Workspace → Git Commit과 Git → Workspace Update를 구분하고, 실제 Feature
데이터 검증과 사람의 PR 검토를 거쳐 main에 반영합니다.

## 3-1. Dev를 main의 새 Git directory에 연결

**경로:** `FabricLab-Dev → Workspace settings → Git integration → Connection details`.

1. GitHub를 선택합니다. 회색이면 [필수 tenant 설정](01-prerequisites.md)을 먼저 확인합니다.
2. 올바른 repository-scoped 계정을 선택하고 **Connect**를 누릅니다.
   새 계정이 필요한 경우만 Add account에서 PAT를 등록합니다.
3. Branch는 `main`, Git folder는 `/workshops/cicd/fabric`으로 지정합니다.

![실제 Dev의 main과 새 Git directory 입력](screenshots/w16-dev-main-git-folder.png)

4. **Connect and sync**를 누릅니다.
5. 폴더가 없다는 확인 창에서 정확한 경로를 대조하고 **Create and sync**를 선택합니다.

![새 directory 생성과 동기화 확인 창](screenshots/w17-create-git-folder-confirmation.png)

### 초기 동기화 방향을 확인

이번 Dev에는 Lakehouse와 Notebook이 있고 원격의 이 directory는 없었습니다.
실제 UI가 directory를 만든 뒤 **Workspace → Git**으로 두 정의를 커밋했습니다.
양방향 선택 창이 표시되었다고 설명하지 않습니다.

반대로 Feature처럼 Workspace가 비어 있고 Git 정의가 있으면 **Git → Workspace**가
초기 방향입니다. 양쪽에 내용이 있거나 삭제·덮어쓰기 경고가 나오면 멈춰 비교합니다.
빈 directory로 Workspace를 덮어쓰지 않습니다.

![두 아이템 최초 동기화 후 Synced 상태](screenshots/w19-dev-initial-sync-complete.png)

**실제 기록:** directory 생성 `f510589f`, 두 정의 최초 Commit `2398332f`.
Git에 다음 구조가 생겼습니다.

```text
workshops/cicd/fabric/
  CI_CD_Demo.Lakehouse/
    .platform
    alm.settings.json
    lakehouse.metadata.json
    shortcuts.metadata.json
  CI_CD_Smoke.Notebook/
    .platform
    notebook-content.py
```

SQL analytics endpoint는 Lakehouse가 관리하는 항목입니다. 별도 source definition이나
Delta 테이블 행을 Git에 추가하지 않습니다.

## 3-2. Git으로 분기할 때 Lakehouse 바인딩 설정

**경로:** Dev Notebook **Settings → Git settings → Git binding**.

1. **Lakehouse in new workspace**를 선택합니다.
2. 변경이 다음 Commit에 반영된다는 안내를 확인합니다.
3. Workspace로 돌아와 **Source control → Changes**를 엽니다.
4. Notebook 하나의 변경을 검토하고 Commit 메시지를 입력합니다.
5. 해당 Notebook을 선택하고 **Commit**합니다.

![새 Workspace의 Lakehouse를 사용하도록 선택](screenshots/w20-notebook-git-local-lakehouse-binding.png)

![Workspace에서 바인딩 설정 변경을 검토하고 Commit](screenshots/w21-commit-stage-local-binding.png)

**실제 기록:** Commit `4ea83edb`. Fabric이 `notebook-settings.json`을 만들고 lakehouse
물리 ID를 logical ID로 바꾸었습니다. Workspace ID의
`00000000-0000-0000-0000-000000000000`은 이 Git 바인딩 표현의 일부이지 배포할 실제
Workspace ID가 아닙니다. 이 설정 파일이나 logical ID를 수동으로 고치지 않습니다.

Lakehouse와 Notebook을 **함께** 버전 관리하고, 동기화 후에는 실제 물리 ID가 새 환경으로
해결되었는지 다시 확인합니다. 설정이 on이라는 사실만으로 안전한 바인딩이 증명되지는 않습니다.

## 3-3. Feature branch와 Feature Workspace

**경로:** GitHub 소스 저장소 **Branches → New branch**.

1. Source가 최신 `main`인지 확인합니다.
2. 새 이름 `feature/smoke-v2`를 입력하고 **Create new branch**를 선택합니다.

![실제 GitHub에서 main을 기준으로 Feature branch 생성](screenshots/w24-create-feature-branch-from-main.png)

**실제 기록:** 새 branch의 시작 Commit이 `4ea83edb`와 같음을 API로 대조했습니다.
오래 열린 GitHub 화면의 오래된 Commit을 분기 기준으로 추측하지 않습니다.

3. `FabricLab-Feature → Workspace settings → Git integration`을 엽니다.
4. 같은 repository-scoped 계정을 선택합니다.

![Feature에서도 기존 source repository 계정을 선택](screenshots/w22-feature-existing-github-account.png)

5. `feature/smoke-v2`, `/workshops/cicd/fabric`에 연결합니다.
6. 비어 있는 Workspace에 Git의 Lakehouse와 Notebook 정의를 가져옵니다.

**실제 수행 방식:** 계정 선택 준비는 UI로 했고 Feature의 연결·초기화·첫 Update는
공식 Core Git API로 수행했습니다. UI branch 목록이 새 branch를 즉시 반영하지 않아,
동일하게 승인된 기존 connection을 재사용했습니다. UI에서 이 연결을 확정했다고 기록하지 않습니다.

API를 사용할 때도 다음 순서와 검증을 지킵니다.

```text
GET  /v1/workspaces/{devWorkspaceId}/git/myGitCredentials
GET  /v1/workspaces/{featureWorkspaceId}/git/connection
POST /v1/workspaces/{featureWorkspaceId}/git/connect
POST /v1/workspaces/{featureWorkspaceId}/git/initializeConnection
POST /v1/workspaces/{featureWorkspaceId}/git/updateFromGit
GET  /v1/workspaces/{featureWorkspaceId}/git/status
```

- `connect`: 실제 owner/repository, feature branch, directory와 기존 connection ID를 전달합니다.
- `initializeConnection`: `requiredAction=UpdateFromGit`인지 확인합니다.
- Update에는 조회한 `workspaceHead`, `remoteCommitHash`를 사용합니다. 임의 SHA를 만들지 않습니다.
- 202이면 `x-ms-operation-id`로 canonical operations API에서 완료를 확인합니다.
  결과 본문이 없는 성공 작업에 `/result`를 무조건 요구하거나 작업을 중복 제출하지 않습니다.
- 최종 `ConnectedAndInitialized`, 같은 원격/Workspace SHA와 변경 목록 0을 확인합니다.

![실제 Feature branch와 directory 연결 결과](screenshots/w43-feature-connected-branch-and-folder.png)

**실제 확인:** 가져온 v1 전체 코드 AST는 Dev v1과 같았고, Notebook의 물리 기본 Lakehouse는
Feature 자체 Lakehouse로 해결되었습니다. Dev의 Lakehouse를 가리키지 않았습니다.

## 3-4. Feature에서 v2 변경·검증

이번 코드 변경은 **로컬 Git 편집·Commit·Push**로 수행했습니다. Fabric 셀 출력이나
다운로드한 실행 결과를 편집한 것이 아닙니다.

```bash
git clone https://github.com/YOONPYOGitHub/fabric-alm-lab.git
cd fabric-alm-lab
git switch feature/smoke-v2
```

`workshops/cicd/fabric/CI_CD_Smoke.Notebook/notebook-content.py`의 두 상수만 바꿉니다.
Fabric metadata·셀 구분·검증 로직은 보존합니다.

```python
RELEASE = "v2"
MULTIPLIER = 2
```

1. 소스 저장소의 오프라인 검사를 수행합니다.

```bash
python -m unittest discover -s workshops/cicd/tests -v
git diff --check
```

2. 수정한 파일만 Commit하고 feature branch로 Push합니다. main에 직접 v2를 Push하지 않습니다.
3. Feature의 **Source control → Updates**에서 변경을 검토하고 **Update all**을 누릅니다.

![Feature에서 실제로 수행한 Git v2 Update all](screenshots/w28-feature-update-from-git-v2.png)

4. `Synced`, Workspace/원격 SHA 일치와 변경 목록 0을 확인합니다.
5. 내보낸 Notebook 전체 코드가 Git v2와 같고 기본 Lakehouse가 여전히 Feature인지 대조합니다.
6. Feature Notebook을 실행해 실제 Delta 데이터를 다시 읽어 검증합니다.

![Feature v2의 실제 Delta 10행·합계 90·환경 ID·위치](screenshots/w30-feature-v2-verified-output.png)

**실제 기록:** feature HEAD `09b03c28`, unittest 9개·Ruff·Pyright 통과.
UI Update 후 실제 실행 스냅샷에서 10행·유일한 ID 0–9·모든 행 값과 release·합계 90을 확인했습니다.
실행은 Job Scheduler API였으며 UI의 Run all로 실행한 것으로 기록하지 않습니다.

## 3-5. 실제 Pull request와 사람의 검토 — 현재 대기 지점

**경로:** GitHub **Compare & pull request**, base `main`, compare `feature/smoke-v2`.

1. 제목·변경 이유·오프라인 결과·Feature 실제 데이터 결과·바인딩 근거를 적습니다.
2. base와 compare 방향, 바뀐 두 상수와 테스트·문서 변경을 확인합니다.
3. **Create pull request**를 선택합니다. 이 버튼은 merge가 아닙니다.

![검증 결과를 적고 실제 PR을 생성한 화면](screenshots/w31-create-v2-pull-request.png)

4. **Files changed**에서 코드·metadata·테스트·문서를 검토합니다.

![실제 열린 PR의 v1 → v2 두 상수 변경, 기존 diff 색상은 그대로 보존](screenshots/w44-review-v2-pr-diff-clean.png)

**현재 상태:** [YOONPYOGitHub/fabric-alm-lab#1](https://github.com/YOONPYOGitHub/fabric-alm-lab/pull/1)은
열려 있고 사람의 검토를 기다립니다. GitHub Checks는 구성하지 않았습니다. 오프라인 검사를
GitHub 필수 status check가 통과한 것으로 표현하지 않습니다.

검토자가 diff와 검증 근거를 확인하고 실제 병합 승인을 남겨야 합니다. 저장소 정책이
독립 리뷰어 승인을 요구한다면 별도의 적격 리뷰어가 필요합니다. 승인 요청에 응답이 없으면
대기하며 자동 승인·작성자의 자기 승인을 독립 리뷰로 기록하지 않습니다.

## 3-6. 검토·병합 후 Dev Update — 아직 미실행

아래는 승인 후 진행할 절차이며 완료된 실행 기록이 아닙니다.

1. 승인된 PR의 HEAD가 검토한 SHA와 같은지 확인하고 main으로 merge합니다.
2. GitHub에서 실제 merge Commit SHA를 기록합니다.
3. `FabricLab-Dev → Source control → Updates`에서 변경을 검토합니다.
4. 충돌·삭제·로컬 미커밋 변경이 없는지 확인하고 **Update all**을 선택합니다.
5. Dev의 Git HEAD가 실제 main과 같고 변경 목록이 비었는지 확인합니다.
6. Dev 코드가 v2이며 물리 기본 Lakehouse는 Dev인지 확인합니다.
7. Dev에서 실제 10행·합계 90을 검증한 후 [v2 Test 배포](03-deployment-pipelines.md)를 진행합니다.

Feature HEAD와 merge Commit SHA는 다를 수 있습니다. 버전 문자열 하나나 Saved 표시만 보지
말고 실제 코드와 branch HEAD, 환경별 물리 바인딩을 각각 대조합니다.

# 3. GitHub 연결, Feature v2 검증과 PR 생성

[처음으로](README.md) · [이전: Lakehouse + Notebook](02-lakehouse-notebook.md) · [다음: Test v1 초기 배포](04-deployment-pipelines.md)

**목표:** Git 연결 후 Feature에서 v2를 검증하고, main으로 반영할 PR을 생성·검토합니다.
이 장에서는 PR을 Open으로 유지하고 main과 Dev는 v1으로 둡니다.

## 3-1. Dev를 main의 새 Git directory에 연결

**경로:** `FabricLab-Dev → Workspace settings → Git integration → Connection details`.

**필수 권한:** 실습 계정은 Dev Workspace Admin이어야 하며, GitHub 실습 저장소의
읽기·쓰기와 PR 작업에 필요한 권한 및 유효한 인증이 있어야 합니다.

Workspace 역할과 GitHub 저장소 권한은 별개입니다. Workspace Admin이어도 GitHub 접근 권한이나
유효한 인증이 없으면 연결·Commit·Update를 할 수 없습니다.

처음부터 실습하는 독자는 [자신의 새 소스 저장소](01-prerequisites.md#source-repository)를
사용합니다. 이 가이드의 실습 저장소 이름은 `fabric-alm-lab`이며 owner는 본인 계정입니다.
캡처의 계정 대신 본인의 저장소 URL을 입력합니다.

1. GitHub를 선택합니다. 회색이면 [필수 tenant 설정](01-prerequisites.md)을 먼저 확인합니다.
2. 올바른 repository-scoped 계정을 선택하고 **Connect**를 누릅니다.
   새 계정이 필요한 경우 **Add account**에서 Display name, 본인 저장소의 Repository URL,
   사전 준비에서 만든 PAT를 입력합니다. PAT는 보안 입력란에만 입력하며 화면에 노출하지 않습니다.
3. Branch는 `main`, Git folder는 `/workshops/cicd/fabric`으로 지정합니다.

![실제 Dev의 main과 새 Git directory 입력](screenshots/03/01-dev-main-git-folder.png)

4. **Connect and sync**를 누릅니다.
5. 폴더가 없다는 확인 창에서 정확한 경로를 대조하고 **Create and sync**를 선택합니다.

![새 directory 생성과 동기화 확인 창](screenshots/03/02-create-git-folder-confirmation.png)

### 초기 동기화 방향과 완료 상태 확인

앞 단계에서 Dev에 만든 Lakehouse와 Notebook의 정의를 GitHub 저장소에 처음 저장합니다.
**Create and sync**를 선택하면 GitHub에 `/workshops/cicd/fabric` 폴더가 생성되고
두 아이템의 정의가 저장됩니다. 동기화 방향은 **Dev Workspace → GitHub**입니다.

GitHub의 대상 폴더에 이미 아이템 정의가 있거나 삭제·덮어쓰기 경고가 나오면
진행을 멈추고 Workspace와 GitHub의 내용을 비교합니다.

동기화가 끝나면 Dev Workspace의 아이템 목록에서 `CI_CD_Demo` Lakehouse와
`CI_CD_Smoke` Notebook의 **Git status**가 모두 **Synced**인지 확인합니다.

![Dev Lakehouse와 Notebook의 Git status가 모두 Synced인 상태](screenshots/03/03-dev-initial-sync-complete.png)

SQL analytics endpoint 행의 `—`는 별도 Git 동기화 대상이 아니므로 정상입니다.
**Synced**는 정의의 동기화 상태이며, Notebook 실행이나 실제 데이터 검증 성공을 뜻하지는 않습니다.

**기대 결과:** 두 아이템의 정의가 GitHub의 `main` 브랜치와 `/workshops/cicd/fabric` 폴더에 저장됩니다.

GitHub 저장소의 **Code** 탭에서 `main` 브랜치를 선택하고 다음 폴더와 파일이 생성되었는지 확인합니다.

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

![새 Workspace의 Lakehouse를 사용하도록 선택](screenshots/03/04-notebook-git-local-lakehouse-binding.png)

3. Workspace로 돌아와 **Source control → Changes**를 엽니다.
4. Notebook 하나의 변경을 검토하고 Commit 메시지를 입력합니다.
5. 해당 Notebook을 선택하고 **Commit**합니다.

![Workspace에서 바인딩 설정 변경을 검토하고 Commit](screenshots/03/05-commit-stage-local-binding.png)

Fabric은 이 설정을 Git에 반영할 때 `notebook-settings.json`을 만들고 Lakehouse
물리 ID를 logical ID로 표현합니다. Workspace ID의
`00000000-0000-0000-0000-000000000000`은 이 Git 바인딩 표현의 일부이지 배포할 실제
Workspace ID가 아닙니다. 이 설정 파일이나 logical ID를 수동으로 고치지 않습니다.

Lakehouse와 Notebook을 **함께** 버전 관리하고, 동기화 후에는 실제 물리 ID가 새 환경으로
해결되었는지 다시 확인합니다. 설정이 on이라는 사실만으로 안전한 바인딩이 증명되지는 않습니다.

## 3-3. Feature branch와 Feature Workspace

**경로:** GitHub 소스 저장소 **Branches → New branch**.

1. Source가 최신 `main`인지 확인합니다.
   새 실습의 main에는 앞 절에서 내보낸 **v1·MULTIPLIER=1**이 있어야 합니다.
   이미 v2라면 아래 변경을 반복하지 말고 새 실습의 시작 상태를 확인합니다.
2. 새 이름 `feature/smoke-v2`를 입력하고 **Create new branch**를 선택합니다.

![실제 GitHub에서 main을 기준으로 Feature branch 생성](screenshots/03/06-create-feature-branch-from-main.png)

새 branch가 최신 v1 main에서 시작했는지 GitHub의 Commit을 확인합니다.

3. `FabricLab-Feature → Workspace settings → Git integration`을 엽니다.
4. 같은 repository-scoped 계정을 선택합니다.

![Feature에서도 기존 source repository 계정을 선택](screenshots/03/07-feature-existing-github-account.png)

5. `feature/smoke-v2`, `/workshops/cicd/fabric`에 연결합니다.
6. 비어 있는 Feature Workspace에 Git의 Lakehouse와 Notebook 정의를 가져옵니다.
   이 단계의 동기화 방향은 **GitHub → Feature Workspace**입니다.

![Feature branch와 Git folder 연결 상태](screenshots/03/08-feature-connected-branch-and-folder.png)

**기대 결과:** Feature Workspace에 `CI_CD_Demo` Lakehouse와 `CI_CD_Smoke` Notebook이 생성되고,
Git 연결이 `feature/smoke-v2`와 `/workshops/cicd/fabric`을 가리킵니다.
두 아이템의 Git status가 **Synced**인지 확인합니다.

가져온 Notebook 코드가 Dev와 같은 `RELEASE = "v1"`, `MULTIPLIER = 1`인지 확인합니다.
기본 Lakehouse는 Dev가 아닌 **Feature의 `CI_CD_Demo`**여야 하며 실제 연결 대상 ID도 대조합니다.

## 3-4. Feature에서 v2 변경·검증

로컬 PC의 터미널에서 Feature branch의 Notebook 코드를 v2로 변경하고 GitHub에 Push합니다.
이후 Fabric의 Feature Workspace에서 변경 사항을 가져와 실행·검증합니다.

### 로컬에서 Feature branch 준비

Git과 본인 실습 저장소의 GitHub 인증을 준비하고, `python3 --version`으로 Python 3.12 이상인지 확인합니다.
아래 명령은 **로컬 Linux 터미널**에서 실행합니다.
`<YOUR_OWNER>`는 본인 계정으로 바꿉니다. clone하면 저장소와 같은 이름의 `fabric-alm-lab` 폴더가 생성됩니다.
저장소 이름이 다르면 아래 URL과 `cd` 명령의 `fabric-alm-lab`을 모두 자신의 저장소 이름으로 바꿉니다.

처음 clone하는 경우에만 아래 블록을 실행합니다. 이미 같은 실습 저장소를 clone했다면
기존 폴더에서 `git branch --show-current`로 `feature/smoke-v2`인지 확인하고,
다른 branch라면 `git switch feature/smoke-v2`로 전환합니다. clone은 다시 실행하지 않습니다.

```bash
git clone https://github.com/<YOUR_OWNER>/fabric-alm-lab.git &&
cd fabric-alm-lab &&
git switch feature/smoke-v2 &&
git grep -n -E '^(RELEASE|MULTIPLIER) =' -- workshops/cicd/fabric/CI_CD_Smoke.Notebook/notebook-content.py
```

![로컬 clone과 Feature branch 전환 후 v1 상수 확인](screenshots/03/09-local-clone-feature-v1.png)

캡처의 로컬 폴더명은 이전 예시이며, GitHub와 Fabric의 연결 대상에는 영향을 주지 않습니다.

**기대 결과:** `feature/smoke-v2`로 전환되고, 소스에 `RELEASE = "v1"`, `MULTIPLIER = 1`이 표시됩니다.
두 줄이 이미 v2/2이면 여기서 멈추고, 본인이 준비한 v1에서 분기했는지 확인합니다.

<a id="prepare-smoke-tests"></a>

### 오프라인 테스트 준비

Fabric이 내보낸 아이템 정의에는 테스트 코드가 없으므로 가이드의 테스트 파일을 추가합니다.
이후 로컬 명령은 모두 **방금 clone한 본인 실습 저장소의 루트**에서 실행합니다.

1. [실습용 테스트 파일](examples/test_smoke_contract.py)을 **Download raw file**로 받아
   `workshops/cicd/tests/test_smoke_contract.py`로 저장합니다. 디렉터리가 없으면 만듭니다.
   가이드를 로컬로 받았다면 `examples/test_smoke_contract.py`를 해당 위치로 복사해도 됩니다.
2. v1 상태에서 테스트를 실행합니다.

    ```bash
    python3 -m unittest discover -s workshops/cicd/tests -v
    ```

**기대 결과:** v1 상태에서 **9개 테스트가 모두 통과**합니다.
파일 누락·오류가 있거나 테스트가 0개이면 다음 단계로 진행하지 않습니다.

파일 배치와 검사 범위는 [예제 사용 안내](examples/README.md#실습용-오프라인-테스트)를 참고합니다.

### v2 변경·검사·Push

1. `workshops/cicd/fabric/CI_CD_Smoke.Notebook/notebook-content.py`에서 아래 두 상수만 바꾸고 **Ctrl+S로 저장**합니다.
   가이드의 예제 파일이나 첨부파일이 아닌 **clone한 실습 저장소의 파일**을 편집합니다.
   Fabric metadata·셀 구분·검증 로직과 `.platform`·`notebook-settings.json`은 수정하지 않습니다.

   줄 번호 예시는 **32번째 줄의 `RELEASE`, 33번째 줄의 `MULTIPLIER`**입니다.
   내보낸 metadata에 따라 줄 번호가 달라질 수 있으므로 변수 이름도 함께 확인합니다.

    ```python
    RELEASE = "v2"
    MULTIPLIER = 2
    ```

2. 저장된 파일의 두 값이 `"v2"`와 `2`인지 확인한 뒤 테스트와 diff 검사를 실행합니다.
   테스트는 v1도 통과하므로, 테스트 성공만으로 v2 변경을 판단하지 않습니다.

    ```bash
    git grep -n -E '^(RELEASE|MULTIPLIER) =' -- workshops/cicd/fabric/CI_CD_Smoke.Notebook/notebook-content.py
    ```

    두 값이 v2/2인 것을 확인한 뒤 실행합니다.

    ```bash
    python3 -m unittest discover -s workshops/cicd/tests -v &&
    git diff --check
    ```

    ![로컬 테스트 9개 통과와 diff 검사 결과](screenshots/03/10-local-tests-and-diff-check.png)

    **9개 테스트가 모두 통과**해야 합니다.
    테스트 실패·0개 실행 또는 공백 오류·충돌 표시가 있으면 다음 단계로 진행하지 않습니다.

3. Commit 전에 Git 작성자 이름·이메일을 확인합니다. GitHub 로그인·PAT와는 별개의 설정입니다.

    ```bash
    git var GIT_AUTHOR_IDENT
    ```

    이름·이메일 오류가 나면 아래 예시 값을 본인의 정보로 바꿔 **현재 저장소에만** 설정합니다.
    이미 올바르게 설정되어 있다면 변경하지 않습니다.
    이메일은 GitHub 개인 **Settings → Emails**의 등록 이메일 또는 제공되는 `noreply` 주소를 사용합니다.

    ```bash
    git config --local user.name "<YOUR_NAME>" &&
    git config --local user.email "<YOUR_GITHUB_EMAIL>" &&
    git var GIT_AUTHOR_IDENT
    ```

4. 작성자 확인까지 성공하면 Notebook 소스와 추가한 테스트 파일만 staging하고,
   staged 변경을 검사한 뒤 Commit·Push합니다. main에 직접 v2를 Push하지 않습니다.

    ```bash
    git add workshops/cicd/fabric/CI_CD_Smoke.Notebook/notebook-content.py workshops/cicd/tests/test_smoke_contract.py &&
    git diff --cached --check &&
    git commit -m "Validate stage-local Delta smoke data for release v2" &&
    git push origin feature/smoke-v2
    ```

    ![새 Commit 생성과 Feature branch Push 완료](screenshots/03/11-local-commit-push-feature.png)

    변경 파일 수는 앞서 Commit한 파일에 따라 달라질 수 있습니다.

테스트 실행으로 생긴 `__pycache__`나 토큰·로컬 설정을 Commit하지 않습니다.
`&&`로 연결한 명령은 앞 명령이 실패하면 중단됩니다. Commit이 실패했다면 Push 완료로 간주하지 않습니다.

### Fabric에서 변경 반영·실행

**경로:** `FabricLab-Feature → Source control → Updates`.

1. Git에서 가져올 Notebook 변경을 검토하고 **Update all**을 누릅니다.

![Git에서 가져올 Notebook 변경과 Update all 버튼](screenshots/03/12-feature-update-from-git-v2.png)

2. Git status가 **Synced**이고 변경 목록이 0인지 확인합니다.
   Workspace의 Git 동기화 정보에 표시된 **Commit SHA**를 GitHub **Code** 탭의
   `feature/smoke-v2` 최신 Commit과 대조합니다.

   Commit SHA는 특정 Git 변경 이력을 식별하는 값입니다. 두 곳이 같은 Commit을 가리키면
   해당 변경까지 동기화된 것입니다. 배포 note의 SHA는 기록용이며, 입력한 Commit을 선택해 배포하는 설정이 아닙니다.

3. 저장된 Notebook 전체 코드가 Git의 v2 소스와 같고, 실제 기본 Lakehouse ID가
   **Feature의 `CI_CD_Demo`**를 가리키는지 대조합니다.
4. Feature Notebook을 열어 **Run all**로 실행하고, 셀 아래의 실제 테이블 검증 결과를 확인합니다.

![Feature Notebook의 v2 실행 결과와 Feature 자체 Delta 위치](screenshots/03/13-feature-v2-verified-output.png)

**기대 결과:** Feature 자체 Lakehouse의 실제 Delta 테이블이 10행·고유 ID 0–9이며,
모든 행이 `value=id*2`, `release=v2`이고 합계가 **90**입니다.
출력의 Workspace ID·Lakehouse ID·Delta 위치도 Feature 환경을 가리켜야 합니다.

## 3-5. PR 생성과 변경 검토

Feature branch에 저장한 v2 변경을 main에 반영하기 위한 PR을 만듭니다.
Commit·Push나 Fabric의 Update만으로 다른 branch인 main까지 변경되지는 않습니다.

1. 본인 GitHub 실습 저장소의 **Code** 탭에서 branch를 **feature/smoke-v2**로 선택합니다.
2. 최근 Push 안내 배너의 **Compare & pull request**를 선택합니다.
   배너가 없으면 **Contribute → Open pull request**로 들어갑니다.
3. 비교 화면 상단에서 **base: main**, **compare: feature/smoke-v2**인지 확인합니다.
   base는 변경을 받을 branch, compare는 변경을 가져올 branch입니다.
4. 제목과 설명을 작성합니다.
   - 제목 예시: `Update smoke notebook from v1 to v2`
   - 변경 내용: `RELEASE`를 `"v1"`에서 `"v2"`로, `MULTIPLIER`를 `1`에서 `2`로 변경
   - 검증 근거: 오프라인 테스트 9개 통과, Feature에서 실제 10행·합계 90 확인,
     기본 Lakehouse와 출력의 환경 ID·Delta 위치가 Feature 자체를 가리킴
5. 아래 변경 목록에서 두 상수와 추가한 테스트 파일을 확인합니다.
   metadata·바인딩에 의도하지 않은 변경이 없는지 확인하고, 문서를 수정했다면 함께 검토합니다.
6. **Create pull request**를 선택합니다.
   **Open pull request**는 생성 화면으로 들어가는 버튼이고, **Create pull request**가 실제 PR 생성입니다.

![PR 제목·설명 작성 후 Create pull request를 선택하는 화면](screenshots/03/14-create-v2-pull-request.png)

7. 생성된 PR의 **Files changed**에서 코드·metadata·테스트와 본인이 변경한 문서를 검토합니다.

![실제 열린 PR의 v1 → v2 두 상수 변경, 기존 diff 색상은 그대로 보존](screenshots/03/15-review-v2-pr-diff-clean.png)

**기대 결과:** PR은 **Open** 상태이며, 병합 전이므로 main은 v1, Feature branch는 v2로 유지됩니다.
**Merge pull request는 아직 누르지 않습니다.**

---

## 다음으로 이동

4장에서 Dev v1을 Test에 처음 배포합니다. PR 검토·병합과 Dev v2 반영은 그다음 5장에서 진행합니다.

| 이전 단계 | 전체 목차 | 다음 단계 |
|---|---|---|
| [← Lakehouse와 Notebook v1](02-lakehouse-notebook.md) | [실습 순서](README.md#workshop-order) | [Pipeline과 Test v1 초기 배포 →](04-deployment-pipelines.md) |

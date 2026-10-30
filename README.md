# Microsoft Fabric Git integration and deployment pipelines

**Lakehouse + Notebook + 실제 Delta 데이터**로 익히는 GitHub CI/CD 단계별 실습입니다.
필수 관리자 설정부터 feature branch, PR 검토, Dev 동기화, Test 검증과 Production 승인까지
하나의 흐름으로 설명합니다. 메뉴 이름은 실제 영문 UI 기준입니다.

로컬 터미널 명령은 **Linux/WSL의 Bash와 `python3`**를 기준으로 합니다.

설명·캡처·[v1 Notebook 코드와 실습용 테스트](examples/README.md)를 이 저장소에서 모두 제공합니다.
별도 예제 저장소의 접근 권한 없이 따라 할 수 있습니다.
기존 환경에서 검증한 결과는 [실제 수행 기록](06-execution-record.md)에 따로 보관합니다.

## 1. 먼저 구분할 것

| 저장소 | 역할 |
|---|---|
| 이 저장소 `fabric-alm-guide` | 설명, 캡처, 예제 코드, 실습용 테스트, 검증 기록 |
| 본인 계정에 새로 만드는 `fabric-alm-lab` | Fabric과 동기화하는 본인의 Lakehouse·Notebook 정의와 복사한 실습용 테스트 |

Fabric의 Git 연결에는 **본인의 실습 저장소**의 `main /workshops/cicd/fabric`을 지정합니다.
가이드 저장소를 Fabric Workspace에 연결하지 않습니다.

실습에 필요한 파일은 각 장에서 사용할 때 안내합니다. 지금 미리 모두 복사할 필요는 없습니다.
저장소 URL의 owner는 본인 계정으로 입력하며, 캡처의 계정·환경 ID·Commit SHA는 예시입니다.
이미 다른 이름으로 만든 새 실습 저장소가 있다면 그 이름을 일관되게 사용해도 됩니다.

```text
GitHub feature/smoke-v2 ←→ Feature Workspace
          │ PR + 사람의 검토
          ▼
GitHub main ←→ Development Workspace
                     │ Deployment pipeline
                     ▼
               Test Workspace
                     │ 실제 데이터 검증 + 릴리스 승인
                     ▼
             Production Workspace
```

**Git과 Deployment pipeline이 전달하는 것은 아이템 정의입니다.**
Lakehouse의 Delta 테이블 행은 Git에 들어가지 않으며, 단계 배포로 복사되지 않습니다.
각 Workspace의 Notebook을 실행해 그 환경의 데이터를 만들고 검증합니다.

<a id="workshop-order"></a>

## 2. 실습 순서

| 순서 | 문서 | 다음 단계로 넘어갈 조건 |
|---|---|---|
| 1 | [사전 준비와 필수 설정](01-prerequisites.md) | 계정·Capacity·권한·4개 관리자 설정·GitHub 인증 확인 |
| 2 | [Lakehouse와 Notebook v1](02-lakehouse-notebook.md) | 실제 10행, 고유 ID 0–9, v1 합계 45 |
| 3 | [GitHub 연결·Feature·PR 생성까지](03-git-integration.md) | 3-1~3-5의 PR 생성까지; Feature v2 합계 90, main은 아직 v1 |
| 4 | [Pipeline과 v1 초기 배포](04-deployment-pipelines.md#baseline-preparation) | 4-1~4-6; PR 승인 전 main v1 → Test v1 검증 |
| 5 | [사용자 승인·PR 병합·Dev Update](03-git-integration.md#merge-and-dev-update) | 3-5의 승인·병합부터 3-6까지; Dev v2 합계 90 |
| 6 | [Test v2와 Production 승격](04-deployment-pipelines.md#release-v2) | 4-7~4-8; Test v2 검증 → 별도 승인 → Production v2 검증 |
| 7 | [검증·복구·비용 정리](05-validation-and-recovery.md) | 정의·바인딩·데이터·승인 근거를 함께 보관 |
| 별첨 | [실제 수행 기록과 검증 범위](06-execution-record.md) | 수행 방식, Commit·job·배포 ID와 제한사항 확인 |

처음 읽는 경우 순서대로 진행합니다. 이미 구성된 환경에서는 확인 후 재사용하며,
캡처를 만들기 위해 설정을 껐다 켜거나 같은 리소스를 중복 생성하지 않습니다.
장 번호는 주제별 분류입니다. 위 표는 실제 실행 순서이며, PR 승인을 기다리는 동안 v1
Pipeline 준비를 진행한 뒤 승인·병합으로 돌아옵니다. 이미 main을 v2로 바꾼 경우에는
v1 초기 배포 절을 현재 실행 단계로 오해하거나 캡처 재현을 위해 코드를 되돌리지 않습니다.

## 3. 실습 구성과 비용

| 대상 | 촬영 환경의 이름 / 설정 |
|---|---|
| Development | `FabricLab-Dev`, Git `main` |
| Feature | `FabricLab-Feature`, Git `feature/smoke-v2` |
| Test / Production | `FabricLab-Test` / `FabricLab-Prod` |
| Git directory | `/workshops/cicd/fabric` |
| Pipeline | `FabricLab-Release`, Development → Test → Production |
| Lakehouse / Notebook | `CI_CD_Demo` / `CI_CD_Smoke` |
| 테이블 | 기본 Lakehouse의 `dbo.cicd_smoke` |
| Capacity | 기존 `fb001`, F16, Korea Central |
| v1 / v2 | 10행·합계 45 / 10행·합계 90 |

이름은 예시입니다. 자신의 tenant, 계정, 승인된 Capacity와 저장소로 바꿉니다.
F16이 모든 실습 환경의 최소 SKU라는 뜻은 아닙니다. 라이선스와 기능 지원은 공식 문서를 확인합니다.
Spark 실행은 CU를, Delta 데이터는 저장소를 사용합니다. 작업을 멈추거나 브라우저를 닫아도
Capacity가 자동 중지되지 않습니다.

## 4. 캡처 읽는 방법

- 빨간 박스는 **화면당 핵심 한 곳**이 원칙이며, 필요한 경우에만 최대 두 곳입니다.
- 큰 코드 블록, 설정 패널 전체, 이미 색상으로 표시된 diff를 다시 두르지 않습니다.
- 결과·전체 구성·비교 화면은 박스 없이 보존할 수 있습니다.
- 캡처마다 본문에 **무엇을 선택하는지, 왜 필요한지, 기대 결과**를 설명합니다.
- 본문은 [강조본](screenshots/)을 사용하고 [원본](screenshots-originals/)은 변경하지 않습니다.
  [주석 정의](tools/screenshot_annotations.json)에 크기·좌표·원본 SHA-256을 보관합니다.
- 실제 화면의 UI·값·성공 상태를 합성하지 않았습니다. 토큰 발급 결과나 암호·MFA 화면은
  캡처하지 않습니다.

이번 재작성의 Workspace 생성과 Lakehouse/Notebook 준비, Git 변경, 배포 화면은 새 실습
리소스에서 촬영했습니다. 이미 승인·구성된 GitHub 정책의 변경 전후와 PAT 준비 화면은
**같은 설정의 기존 실제 기록**임을 해당 단계에 표시했습니다.

원본·강조본은 각각 **66장** 보관합니다. 이전 저장소 생성·외부 테스트 다운로드 화면
w61–w63은 현재 실습 지시와 구분해 [과거 화면 기록](06-execution-record.md#이전-저장소-준비와-다운로드-화면)에
보존합니다. 기존 화면의 이름이나 UI를 합성해 변경하지 않습니다.

## 5. 현재 확인한 결과

아래는 2026-10-19–20 KST 실행 기록이지 실시간 상태판이 아닙니다.

| 환경 / 구간 | 실제 결과 |
|---|---|
| Dev v1 | 실제 Delta 10행·고유 ID 10개·모든 값 검증·합계 45 |
| Feature v2 | 실제 Delta 10행·고유 ID 10개·모든 값 검증·합계 90 |
| Git 바인딩 | Feature가 Dev가 아닌 자신의 Lakehouse를 참조함을 내보낸 정의로 확인 |
| Dev → Test v1 초기 배포 | UI에서 Lakehouse + Notebook 두 정의 배포, Succeeded |
| Test v1 | 배포 후 테이블 경로 부재 → Notebook 실행 후 생성·10행·합계 45 |
| 오프라인 소스 검사 | unittest 9개, Ruff, Pyright 통과 |
| PR·main 병합 | 사용자 대화상 승인 후 실제 UI 병합, merge `0cf51fd`; 독립 GitHub review와 구분 |
| Dev/Test v2 | 두 환경 모두 실제 Delta 10행·합계 90, Test 배포 규칙·물리 바인딩 확인 |
| Production | 명시적 별도 승인 후 Test → Prod 두 정의 배포·Prod 자체 바인딩·실제 10행·합계 90 검증 |

[기계 판독 가능한 검증 기록](evidence/workshop-verification.json)과
[실행 스냅샷 링크](06-execution-record.md)에서 근거를 확인할 수 있습니다.
기록에 포함된 과거 Private GitHub 저장소와 Fabric 링크는 해당 대상의 접근 권한이 있어야 열립니다.
이 링크는 참고용이며 현재 실습에 필요한 코드·테스트는 이 저장소에 포함되어 있습니다.

![Production에서 실제 확인한 v2 10행 전체와 합계 90·환경 ID·Delta 위치](screenshots/w60-production-v2-ten-row-table.png)

## 6. 범위와 공식 근거

핵심 트랙은 수동 Git 통합과 Deployment pipelines, 환경별 데이터 검증입니다.
GitHub Actions/OIDC·서비스 주체 자동화, Variable Library 확장, Power BI 모델·보고서와
RLS는 별도로 설계·승인할 확장 트랙이며 이 실행에서 구성하지 않았습니다.
Feature Workspace, 10행·합계 45/90, 수동 승인 체크포인트는 공식 필수 구성이 아니라
이 가이드가 선택한 실습 설계입니다. 제품 동작·권한 조건은 아래 공식 문서를 기준으로 합니다.

### 권한 구분과 운영 시 역할 분리

기본 실습은 같은 실습 계정으로 환경 구성·개발·배포를 진행합니다.
아래는 운영 적용 시 담당자별 권한을 나누기 위한 참고이며,
이번 실습에서 추가 계정을 만들거나 기존 Admin 역할을 낮추라는 실행 단계가 아닙니다.
Tenant settings 변경은 별도로 Fabric Administrator 또는 해당 설정을 위임받은 관리자가 수행합니다.

| 담당 / 작업 | 필요한 권한과 범위 |
|---|---|
| 환경 구성 담당 | Git 연결에는 해당 Workspace Admin, Pipeline 단계 할당에는 해당 Workspace Admin과 Pipeline Admin |
| 개발 담당 | 연결된 Dev·Feature에서 코드 변경·Git Commit·Update를 수행하려면 Workspace Contributor 이상과 해당 아이템의 쓰기 권한, 작업에 맞는 GitHub 저장소 권한·인증 |
| 배포 담당 | 이미 Workspace가 할당된 단계 간 배포에는 Pipeline Admin과 배포 원본·대상 Workspace의 Contributor 이상 |
| Notebook 배포 규칙 담당 | Pipeline Admin, 대상 Workspace Contributor 이상, 규칙을 설정할 대상 Notebook의 아이템 소유자 조건을 모두 충족 |
| PR 검토·릴리스 승인 담당 | 검토 근거에 필요한 조회 권한과 조직의 승인 자격. 독립 GitHub 리뷰가 필요한 경우 PR 작성자와 별도의 적격 리뷰어 |

Workspace Admin, Pipeline Admin, 아이템 소유자, GitHub 권한은 서로 대체되지 않습니다.
Git Commit·Update에는 테넌트의 소유자 제한이나 외부 의존성 권한 등 추가 조건이 적용될 수 있습니다.
개발·배포 담당에게는 업무에 필요한 환경만 허용하며, 모든 환경에 일괄 Admin을 부여하는 운영 기준이 아닙니다.
Workspace Contributor도 아이템을 직접 수정할 수 있고, Pipeline Admin도 Pipeline을 관리할 수 있으므로
이 역할 조합만으로 “Pipeline을 통한 배포만 허용”하는 통제가 구성되지는 않습니다.

Fabric 권한을 나누어도 GitHub의 main 직접 Push·PR 병합 권한까지 제한되지는 않습니다.
독립 리뷰를 강제하려면 지원되는 branch protection/ruleset과 실제 리뷰어를 별도로 구성해야 합니다.
이 실습의 수동 승인은 그러한 강제 통제를 구성한 것으로 간주하지 않습니다.
여러 사용자가 참여하는 운영에서는 각자의 인증 정보를 사용하고 관리자 PAT를 공유하지 않습니다.

### 공식 근거

- [Get started with Git integration — GitHub](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started?tabs=github%2CGitHub%2Ccommit-to-git)
- [Git integration permissions](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process#permissions)
- [Get started using deployment pipelines — new UI](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines?tabs=from-fabric%2Cnew-ui)
- [Deployment pipelines permissions](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process#permissions)
- [Notebook source control, auto-binding, deployment rules](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment)
- [Lakehouse source control and deployment](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-git-deployment-pipelines)
- [Git integration administrator settings](https://learn.microsoft.com/en-us/fabric/admin/git-integration-admin-settings)

## 7. 캡처 재생성과 오프라인 검사

Linux/WSL에서 `python3 --version`으로 Python 3.12 이상인지 확인한 뒤 가이드 저장소 루트에서 실행합니다.
패키지 설치는 registry에 접근할 수 있지만 이후 명령은 Azure/Fabric에 배포하지 않습니다.

Ubuntu/WSL에서 가상환경 생성 시 `ensurepip is not available` 오류가 나면
사용 중인 Python 버전에 맞는 venv 패키지를 설치한 뒤 다시 생성합니다.
Python 3.12 환경의 설치 명령은 `sudo apt install python3.12-venv`입니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r tools/requirements.txt
python3 tools/annotate_screenshots.py
python3 -m unittest discover -s tests -v
```

Windows PowerShell에서는 `py -3 -m venv .venv`로 생성한 뒤
`.\.venv\Scripts\Activate.ps1`로 활성화합니다.
활성화 후에는 위 블록의 나머지 `python3`를 `python`으로 바꿔 실행합니다.
검사는 링크·이미지 목록과 크기·주석 제한·원본 해시·박스 선 밖의 모든 픽셀 보존을 확인합니다.
예제의 세 코드 셀과 환경 ID 미포함 여부, 실습용 테스트를 임시 실습 저장소로 복사한 뒤
v1·v2 정상 상태 및 잘못된 상수·바인딩·누락 파일의 실패도 검증합니다. 실제 Spark는 실행하지 않습니다.

이 명령은 **가이드 유지보수용 검사**입니다. 독자가 본인의 실습 저장소에서 실행할 9개 검사는
[Git 장의 테스트 준비](03-git-integration.md#prepare-smoke-tests)에서 안내합니다.

---

## 다음으로 이동

| 실습 시작 | 전체 목차 | 실행 결과 먼저 보기 |
|---|---|---|
| [1단계: 사전 준비와 필수 설정 →](01-prerequisites.md) | [실습 순서로 이동](#workshop-order) | [실제 수행 기록과 검증 범위](06-execution-record.md) |

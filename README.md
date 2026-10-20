# Microsoft Fabric Git integration and deployment pipelines

**Lakehouse + Notebook + 실제 Delta 데이터**로 익히는 GitHub CI/CD 단계별 실습입니다.
필수 관리자 설정부터 feature branch, PR 검토, Dev 동기화, Test 검증과 Production 승인까지
하나의 흐름으로 설명합니다. 메뉴 이름은 실제 영문 UI 기준입니다.

> **실제 실행 검증 완료:** 사용자 승인 후
> [소스 PR](https://github.com/YOONPYOGitHub/fabric-alm-lab/pull/1)을 병합하고,
> 별도의 Production 릴리스 승인을 거쳐 **Dev·Test·Production 모두 실제 Delta 10행·합계 90**을
> 검증했습니다. 이 실행의 승인은 대화에 기록된 수동 승인입니다. 독립 GitHub 리뷰어 승인이나
> 네이티브 자동 승인 Workflow를 구성한 것으로 표시하지 않습니다.

## 1. 먼저 구분할 것

| 저장소 | 역할 |
|---|---|
| [fabric-alm-guide](https://github.com/YOONPYOGitHub/fabric-alm-guide) | 설명, 실제 화면 원본·강조본, 검증 기록 |
| [fabric-alm-lab](https://github.com/YOONPYOGitHub/fabric-alm-lab) | Fabric과 동기화하는 Lakehouse·Notebook 정의와 오프라인 테스트 |

Fabric의 Git 연결에는 **소스 저장소**의 `main /workshops/cicd/fabric`을 지정합니다.
가이드 저장소를 Fabric Workspace에 연결하지 않습니다.

### 완료된 예제 조회와 새 실습 시작을 구분

촬영에 사용한 `YOONPYOGitHub/fabric-alm-lab`의 `main`과 `feature/smoke-v2`는 이미 **v2**입니다.
이 저장소를 그대로 clone해 두 상수를 v2로 바꾸는 것은 새 변경이나 PR을 만들지 않습니다.

- **결과 조회:** 기존 저장소의 Commit·PR·아이템 정의를 읽습니다.
- **처음부터 실습:** [사전 준비의 저장소 구성](01-prerequisites.md#source-repository)에서
  자신의 새 소스 저장소를 준비하고, Dev에서 만든 v1을 Git으로 내보내 시작합니다.
  아래 `main /workshops/cicd/fabric`과 branch 이름은 그 새 저장소에 적용합니다.
- 촬영 환경의 branch를 되돌리거나 강제로 Push하지 않습니다. 본문의 실제 SHA는 실행 기록이며,
  새 실습에서는 자신의 실제 SHA를 기록합니다.

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
| 2 | [Lakehouse와 Notebook v1](02a-lakehouse-notebook.md) | 실제 10행, 고유 ID 0–9, v1 합계 45 |
| 3 | [GitHub 연결·Feature·PR 생성까지](02-git-integration.md) | 3-1~3-5의 PR 생성까지; Feature v2 합계 90, main은 아직 v1 |
| 4 | [Pipeline과 v1 초기 배포](03-deployment-pipelines.md#baseline-preparation) | 4-1~4-6; PR 승인 전 main v1 → Test v1 검증 |
| 5 | [사용자 승인·PR 병합·Dev Update](02-git-integration.md#merge-and-dev-update) | 3-5의 승인·병합부터 3-6까지; Dev v2 합계 90 |
| 6 | [Test v2와 Production 승격](03-deployment-pipelines.md#release-v2) | 4-7~4-8; Test v2 검증 → 별도 승인 → Production v2 검증 |
| 7 | [검증·복구·비용 정리](04-validation-and-recovery.md) | 정의·바인딩·데이터·승인 근거를 함께 보관 |
| 별첨 | [실제 수행 기록과 검증 범위](05-execution-record.md) | 수행 방식, Commit·job·배포 ID와 제한사항 확인 |

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

2026-10-20 KST의 문서 보완에서는 실제 화면 **6장(w61–w66)**을 추가해 원본·강조본을
각각 **66장** 보관합니다. 새 저장소 양식의 이름·Private·README 준비, 고정 테스트 원본의
다운로드 위치, 기존 Test Notebook 소유자, OneLake Govern의 관리자 설정 경로를 담았습니다.
새 저장소 생성 완료나 새 실습의 실행 증거가 아니라 **각 절차의 준비·선택·조회 화면**입니다.
기존 60장과 실제 배포·데이터 검증 기록은 변경하지 않았습니다.

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
[실행 스냅샷 링크](05-execution-record.md)에서 근거를 확인할 수 있습니다.
Private GitHub 저장소와 Fabric 링크는 해당 대상의 접근 권한이 있어야 열립니다.

![Production에서 실제 확인한 v2 10행 전체와 합계 90·환경 ID·Delta 위치](screenshots/w60-production-v2-ten-row-table.png)

## 6. 범위와 공식 근거

핵심 트랙은 수동 Git 통합과 Deployment pipelines, 환경별 데이터 검증입니다.
GitHub Actions/OIDC·서비스 주체 자동화, Variable Library 확장, Power BI 모델·보고서와
RLS는 별도로 설계·승인할 확장 트랙이며 이 실행에서 구성하지 않았습니다.
Feature Workspace, 10행·합계 45/90, 수동 승인 체크포인트는 공식 필수 구성이 아니라
이 가이드가 선택한 실습 설계입니다. 제품 동작·권한 조건은 아래 공식 문서를 기준으로 합니다.

- [Get started with Git integration — GitHub](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started?tabs=github%2CGitHub%2Ccommit-to-git)
- [Get started using deployment pipelines — new UI](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines?tabs=from-fabric%2Cnew-ui)
- [Notebook source control, auto-binding, deployment rules](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment)
- [Lakehouse source control and deployment](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-git-deployment-pipelines)
- [Git integration administrator settings](https://learn.microsoft.com/en-us/fabric/admin/git-integration-admin-settings)

## 7. 캡처 재생성과 오프라인 검사

Python 3.12 이상으로 저장소 루트에서 실행합니다. 패키지 설치는 registry에 접근할 수 있지만
이후 명령은 Azure/Fabric에 배포하지 않습니다.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements.txt
python tools/annotate_screenshots.py
python -m unittest discover -s tests -v
```

Windows PowerShell에서는 `source` 대신 `.\.venv\Scripts\Activate.ps1`로 활성화합니다.
검사는 링크·이미지 목록과 크기·주석 제한·원본 해시·박스 선 밖의 모든 픽셀 보존을 확인합니다.
최초 Notebook-only 판은 두 저장소의 `notebook-demo-v1` 태그에 보존되어 있습니다.

---

## 다음으로 이동

| 실습 시작 | 전체 목차 | 실행 결과 먼저 보기 |
|---|---|---|
| [1단계: 사전 준비와 필수 설정 →](01-prerequisites.md) | [실습 순서로 이동](#workshop-order) | [실제 수행 기록과 검증 범위](05-execution-record.md) |

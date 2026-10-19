# Microsoft Fabric Git integration and deployment pipelines

**Lakehouse + Notebook + 실제 Delta 데이터**로 익히는 GitHub CI/CD 단계별 실습입니다.
필수 관리자 설정부터 feature branch, PR 검토, Dev 동기화, Test 검증과 Production 승인까지
하나의 흐름으로 설명합니다. 메뉴 이름은 실제 영문 UI 기준입니다.

> **재작성판 검토 중:** Dev v1, Feature v2, Dev → Test v1 배포와 실제 데이터 검증까지
> 수행했습니다. [소스 PR](https://github.com/YOONPYOGitHub/fabric-alm-lab/pull/1)은 사람의 검토
> 대기 상태이며, main 병합·Dev/Test v2·Production 승격은 아직 수행하지 않았습니다.
> 이 가이드를 완료된 Production 실행 보고서로 읽지 않습니다.

## 1. 먼저 구분할 것

| 저장소 | 역할 |
|---|---|
| [fabric-alm-guide](https://github.com/YOONPYOGitHub/fabric-alm-guide) | 설명, 실제 화면 원본·강조본, 검증 기록 |
| [fabric-alm-lab](https://github.com/YOONPYOGitHub/fabric-alm-lab) | Fabric과 동기화하는 Lakehouse·Notebook 정의와 오프라인 테스트 |

Fabric의 Git 연결에는 **소스 저장소**의 `main /workshops/cicd/fabric`을 지정합니다.
가이드 저장소를 Fabric Workspace에 연결하지 않습니다.

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

## 2. 실습 순서

| 순서 | 문서 | 다음 단계로 넘어갈 조건 |
|---|---|---|
| 1 | [사전 준비와 필수 설정](01-prerequisites.md) | 계정·Capacity·권한·4개 관리자 설정·GitHub 인증 확인 |
| 2 | [Lakehouse와 Notebook v1](02a-lakehouse-notebook.md) | 실제 10행, 고유 ID 0–9, v1 합계 45 |
| 3 | [GitHub 연결, Feature, PR, Dev Update](02-git-integration.md) | Feature v2 합계 90, 실제 검토·병합, Dev v2 검증 |
| 4 | [Deployment pipelines와 단계별 검증](03-deployment-pipelines.md) | Test v2 검증 → 승인 → Production v2 검증 |
| 5 | [검증·복구·비용 정리](04-validation-and-recovery.md) | 정의·바인딩·데이터·승인 근거를 함께 보관 |
| 별첨 | [실제 수행 기록과 미완료 구간](05-execution-record.md) | 수행 방식, Commit·job·배포 ID와 제한사항 확인 |

처음 읽는 경우 순서대로 진행합니다. 이미 구성된 환경에서는 확인 후 재사용하며,
캡처를 만들기 위해 설정을 껐다 켜거나 같은 리소스를 중복 생성하지 않습니다.

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

## 5. 현재 확인한 결과

아래는 2026-10-19 실행 기록이지 실시간 상태판이 아닙니다.

| 환경 / 구간 | 실제 결과 |
|---|---|
| Dev v1 | 실제 Delta 10행·고유 ID 10개·모든 값 검증·합계 45 |
| Feature v2 | 실제 Delta 10행·고유 ID 10개·모든 값 검증·합계 90 |
| Git 바인딩 | Feature가 Dev가 아닌 자신의 Lakehouse를 참조함을 내보낸 정의로 확인 |
| Dev → Test v1 초기 배포 | UI에서 Lakehouse + Notebook 두 정의 배포, Succeeded |
| Test v1 | 배포 후 테이블 경로 부재 → Notebook 실행 후 생성·10행·합계 45 |
| 오프라인 소스 검사 | unittest 9개, Ruff, Pyright 통과 |
| PR 검토·main 병합 | **검토 대기**, 자동 승인·자기 승인을 기록하지 않음 |
| Dev/Test v2·Production | **미실행**, Production Workspace는 아직 비어 있음 |

[기계 판독 가능한 검증 기록](evidence/workshop-verification.json)과
[실행 스냅샷 링크](05-execution-record.md)에서 근거를 확인할 수 있습니다.
Private GitHub 저장소와 Fabric 링크는 해당 대상의 접근 권한이 있어야 열립니다.

## 6. 범위와 공식 근거

핵심 트랙은 수동 Git 통합과 Deployment pipelines, 환경별 데이터 검증입니다.
GitHub Actions/OIDC·서비스 주체 자동화, Variable Library 확장, Power BI 모델·보고서와
RLS는 별도로 설계·승인할 확장 트랙이며 이 실행에서 구성하지 않았습니다.

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

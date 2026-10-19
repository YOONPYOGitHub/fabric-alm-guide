# 실제 수행 기록과 미완료 구간

[처음으로](README.md) · [검증·복구](04-validation-and-recovery.md) ·
[검증 JSON](evidence/workshop-verification.json)

아래는 2026-10-19의 실제 기록입니다. 문서의 재현 절차와 완료된 작업을 구분합니다.
이름은 촬영 환경의 예시이며 다른 사용자의 환경에 그대로 사용할 배포 기본값이 아닙니다.
토큰·암호·인증 헤더·발급 응답은 포함하지 않았습니다.

## 실행 상태

| 단계 | 상태 | 실제 수행 방식 / 근거 |
|---|---|---|
| 필수 관리자 설정 | 확인 완료 | Fabric items, Create workspaces, 일반 Git Enabled; GitHub는 승인 그룹 한정 |
| Workspace 4개 | 완료 | 모두 UI 생성, 실제 ID·기존 F16 할당 API 대조 |
| Dev Lakehouse/Notebook | 완료 | UI 생성·이름 지정·기본 Lakehouse 자동 연결 |
| Notebook 소스 준비 | 완료 | 자동 입력의 구문 오류를 실행 전 발견; 검증 ipynb를 updateDefinition으로 반영·재내보내기 |
| Dev v1 실제 데이터 | 완료 | API job + 스냅샷; 10행·고유 ID 0–9·모든 값·합계 45 |
| Dev Git 초기 동기화 | 완료 | UI Connect/Create and sync로 두 아이템 정의 Commit |
| Git 새 Workspace 바인딩 | 완료 | UI 설정 변경·UI Commit; logical ID와 설정 파일 확인 |
| Feature branch | 완료 | 실제 GitHub UI 생성, 기준 main SHA 확인 |
| Feature Git 초기 연결 | 완료 | UI 계정 준비 후 Core Git API 연결·초기화·Update |
| Feature v2 변경 | 완료 | 로컬 Git에서 두 상수 수정·오프라인 검사·Commit·Push |
| Feature v2 Update | 완료 | 실제 Fabric UI Update all, Git SHA·코드·물리 바인딩 대조 |
| Feature v2 데이터 | 완료 | API job + 스냅샷; 실제 10행·모든 v2 값·합계 90 |
| 소스 PR | **검토 대기** | 실제 GitHub UI 생성; 사람 응답 없이 merge하지 않음 |
| Pipeline/단계 할당 | 완료 | UI 생성·Dev/Test/Prod UI 할당; API stages·Pipeline Admin 대조 |
| Dev → Test 초기 배포 | 완료 | 실제 UI, **v1** 두 정의, 오류 시 계속 옵션 해제, note 검증 |
| Test v1 바인딩·데이터 | 완료 | 코드 AST·Test 물리 ID 확인, API job + 스냅샷; 10행·합계 45 |
| Test 기본 Lakehouse 규칙 | 저장·재조회 확인 | Test 자체 Lakehouse 지정, 페이지 reload 후 저장 값 대조; 다음 배포의 적용 효과는 미검증 |
| main 병합·Dev/Test v2 | **미실행** | 실제 PR 검토 승인 필요 |
| Production 정의·데이터 | **미실행** | Workspace 할당만 완료, 대상은 아직 비어 있음 |
| Actions/OIDC·Power BI·RLS | 미구성 | 확장 트랙 |

## Git 기록

| 기록 | SHA / 상태 |
|---|---|
| Git directory 생성 | `f510589f0b541d9c94cdce1a1daaaaaba2b15929` |
| Lakehouse + Notebook 초기 Commit | `2398332f2092bb479db5ad671f9fc8dcf85303f8` |
| 새 Workspace Lakehouse 바인딩 Commit / main v1 | `4ea83edb06a7d2b381ab961a1a25fb8925db6ce4` |
| Feature v2 코드·문서·테스트 | `53f7908` |
| Feature HEAD, cache 제외 포함 | `09b03c28ab58e623e0f7ac1f185778ea3e5425dc` |
| 실제 PR | [YOONPYOGitHub/fabric-alm-lab#1](https://github.com/YOONPYOGitHub/fabric-alm-lab/pull/1), Open |

오프라인 unittest 9개·Ruff·Pyright가 통과했습니다. GitHub Actions나 필수 status check를
구성한 것은 아닙니다. 필수 branch review를 강제하지 않는 Private 저장소의 제약을 공개하고,
검토자가 없는 상태를 가상의 승인으로 대체하지 않았습니다.

## 실제 환경 ID

| 환경 | Workspace ID | Lakehouse ID | Notebook ID |
|---|---|---|---|
| Dev | `4dc4b490-8851-4d99-a75b-1e9067dc78e5` | `3bacc56f-a551-402d-a0b8-7f0da7e0af63` | `e5df67de-adf6-43f0-a1af-491c4b646556` |
| Feature | `91e5839f-c981-47ea-9500-ef557b1634c0` | `f2ff7fc8-e138-4086-93bd-7337ce0becb4` | `72ea01ad-7cb4-4fe3-b89c-dfb6a51a5616` |
| Test | `9c1f123f-6c38-4222-b761-1f94a8d9bc23` | `24b6d3df-a2cc-429b-b6c4-04f78b37545d` | `a828a86d-355e-4c24-87f2-3a9ca8c6e0b7` |
| Production | `fbd6013c-889c-4d9e-83af-c1f4248be5a1` | 미생성 | 미생성 |

모든 아이템 정의를 포괄적으로 검증했다는 뜻은 아닙니다. Notebook의 공통 코드와 실제로
실행한 각 환경의 물리 바인딩을 대조했습니다.

## 실제 데이터 실행

| 환경 | Job / 스냅샷 | 실제 결과 |
|---|---|---|
| Dev v1 | [c244d130-949a-40e3-ae70-5db82ce50d5a](https://app.fabric.microsoft.com/groups/4dc4b490-8851-4d99-a75b-1e9067dc78e5/synapsenotebooks/e5df67de-adf6-43f0-a1af-491c4b646556/snapshots/c244d130-949a-40e3-ae70-5db82ce50d5a) | 10행·합계 45 |
| Feature v2 | [cc23f044-b7a6-4dae-b591-e5e9f9fec2ce](https://app.fabric.microsoft.com/groups/91e5839f-c981-47ea-9500-ef557b1634c0/synapsenotebooks/72ea01ad-7cb4-4fe3-b89c-dfb6a51a5616/snapshots/cc23f044-b7a6-4dae-b591-e5e9f9fec2ce) | 10행·합계 90 |
| Test v1 | [163383c0-720c-4aea-86fd-a5a78a28ddf0](https://app.fabric.microsoft.com/groups/9c1f123f-6c38-4222-b761-1f94a8d9bc23/synapsenotebooks/a828a86d-355e-4c24-87f2-3a9ca8c6e0b7/snapshots/163383c0-720c-4aea-86fd-a5a78a28ddf0) | 10행·합계 45 |

각 Notebook은 `spark.table`로 읽은 모든 행과 aggregate를 검증한 뒤 환경 ID·UTC 시각·실제
Delta 위치를 반환했습니다. 해당 결과를 API에서도 대조했습니다. 단순 Completed·배포 배지·
새 Delta commit을 데이터 성공의 근거로 사용하지 않았습니다.

## 실제 배포와 데이터 비복사 확인

- Pipeline: `FabricLab-Release`, `faa1c755-7778-4a6f-9b7f-4e1bcc414350`.
- Development → Test v1: `1fa47585-6501-4c8d-b628-4f46c582b056`, **Succeeded**.
- 새 아이템 2개, main `4ea83edb`, 방향·note·완료 상태를 대조했습니다.
- 배포 후 Test 실행 전, 실제 `Tables/dbo/cicd_smoke` 경로는 404 **PathNotFound**였습니다.
- Test Notebook 실행 후에만 그 경로가 200으로 존재하고 실제 10행·합계 45를 확인했습니다.
- schema-enabled Tables List API의 미지원 오류를 빈 목록으로 취급하지 않았습니다.
- 이후 Test Notebook의 Default lakehouse 규칙을 UI에서 Test 자체 Lakehouse로 저장하고
  페이지를 reload해 같은 ID·이름·Workspace ID와 미수정 상태를 확인했습니다.
  다음 배포는 아직 하지 않았으므로 이 규칙을 적용한 재배포·실행 성공을 주장하지 않습니다.

## 남은 승인과 정확한 재개 순서

1. 사람이 소스 PR의 실제 diff와 Feature 결과를 검토하고 main 병합을 승인합니다.
2. 승인한 HEAD가 바뀌지 않았는지 확인하고 merge합니다.
3. Dev Update → 코드·바인딩 확인 → 실제 v2 합계 90을 검증합니다.
4. Dev → Test v2 배포 → 실제 Test v2 합계 90을 검증합니다.
5. 사람이 Production 대상·변경·비용과 Test 결과를 검토해 릴리스를 승인합니다.
6. Test → Production 배포·바인딩·실제 v2 데이터를 검증하고 누락된 실제 캡처를 추가합니다.
7. 재작성판 검증을 마친 뒤 가이드 main에 반영합니다.

현재는 검토용 재작성 branch를 사용하며 완료된 Production 실습으로 게시하지 않습니다.
Capacity와 Workspace는 중지·삭제하지 않았으므로 비용이 계속 발생할 수 있습니다.

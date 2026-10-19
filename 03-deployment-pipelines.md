# 4. Deployment pipelines와 단계별 데이터 검증

[처음으로](README.md) · [이전: Git과 PR](02-git-integration.md) · [다음: 검증·복구](04-validation-and-recovery.md)

**목표:** 정의 배포, 환경 바인딩, 데이터 실행, 사람의 승인을 분리합니다.
현재 실제 배포·검증한 것은 **Dev v1 → Test v1 초기 배포**입니다. PR 검토를 기다리는 동안
배포 메커니즘을 확인한 준비 단계이며, 아직 v2 릴리스를 완료한 것이 아닙니다.

## 4-1. 새 Deployment pipeline 생성

**경로:** Dev Workspace 상단 **Create deployment pipeline** 또는 좌측 **Deployment pipelines**.

1. 이름에 `FabricLab-Release`를 입력합니다.
2. Description에 Lakehouse 데이터 검증을 포함한 실습 설명을 입력합니다.
3. 입력 검증이 끝나 **Next**가 활성화되면 선택합니다.

![실제 Pipeline 이름과 설명 입력](screenshots/w26-create-release-pipeline.png)

4. **Development → Test → Production**의 세 단계를 확인합니다.
5. **Create and continue**로 생성합니다.

![실제로 생성할 세 단계와 Create and continue](screenshots/w27-release-pipeline-three-stages.png)

**기대 결과:** Pipeline이 생성됩니다. 생성·관리 권한은 Workspace 역할과 별도입니다.
촬영 환경은 UI에서 Pipeline을 생성했고 현재 계정의 Pipeline Admin도 API로 확인했습니다.

## 4-2. 각 단계에 Workspace 할당

**경로:** 단계 카드의 **Assign a workspace → 이름 선택 → Assign**.
이름을 드롭다운에서 선택하는 것만으로는 할당이 끝나지 않습니다.

| 단계 | Workspace |
|---|---|
| Development | `FabricLab-Dev` |
| Test | `FabricLab-Test` |
| Production | `FabricLab-Prod` |

![Dev Workspace를 선택한 뒤 Assign으로 확정](screenshots/w29-assign-development-workspace.png)

![Test Workspace를 선택한 뒤 Assign으로 확정](screenshots/w32-assign-test-workspace.png)

![Production Workspace 할당만 수행, 데이터 승격 아님](screenshots/w33-assign-production-workspace-only.png)

세 단계 할당은 모두 실제 UI로 수행했고 stages API의 실제 Workspace ID와 대조했습니다.
Feature Workspace는 이 Pipeline에 넣지 않습니다.

**기대 결과:** 세 카드가 정확한 Workspace를 가리킵니다. Workspace를 연결했다고
아이템 정의·테이블 데이터가 자동으로 배포되는 것은 아닙니다.

## 4-3. Dev v1 → Test v1 초기 배포 — 실제 수행

1. Dev v1의 실제 Delta 결과가 10행·합계 45인지 확인합니다.
2. **대상인 Test 카드**를 선택합니다.
3. 하단 **Deploy from = Development**를 확인합니다.
4. 목록이 가려지면 캔버스 접기 버튼으로 전체 아이템 목록을 보이게 합니다.
5. `CI_CD_Demo` Lakehouse와 `CI_CD_Smoke` Notebook **두 아이템**을 선택합니다.

![Test 대상·Development 원본과 Deploy 2 선택](screenshots/w35-test-target-two-item-selection.png)

첫 배포에서 Notebook만 배포하고 Lakehouse가 생겼을 것이라고 가정하지 않습니다.
Lakehouse가 관리하는 SQL analytics endpoint를 별도 source item으로 선택하지 않습니다.

6. **Deploy**로 확인 창을 엽니다.
7. Development → Test, 두 아이템의 이름, New/Modified 범위를 확인합니다.
8. **Continue deployment in case 1 or more items fail**을 해제합니다.
9. **Add a note**에 Git SHA, v1, Dev 실제 검증 결과와 다음 Test 검증 계획을 적습니다.
10. 최종 **Deploy**를 선택하고 배포 완료를 기다립니다.

![실제 v1 초기 배포의 방향·두 아이템·Git SHA·검증 노트](screenshots/w37-confirm-dev-to-test-v1-baseline.png)

**실제 결과:** 배포 `1fa47585-6501-4c8d-b628-4f46c582b056`가 Succeeded였습니다.
source/target stage ID, 두 새 정의와 note의 `main 4ea83edb`를 API로도 대조했습니다.
이 배포를 v2 배포라고 기록하지 않았습니다.

## 4-4. 배포 직후: 정의와 바인딩, 데이터 부재 확인

1. Test Workspace에 `CI_CD_Demo`와 `CI_CD_Smoke`가 생성됐는지 확인합니다.
2. Notebook을 실행하지 말고 먼저 저장된 정의를 확인합니다.
3. 전체 코드가 v1과 같고 기본 Lakehouse의 ID와 Workspace ID가 **Test 자체**인지 대조합니다.
4. Test Lakehouse **Tables → dbo**를 펼칩니다.

![정의 배포 완료 후에도 비어 있는 Test Lakehouse](screenshots/w38-test-lakehouse-empty-after-definition-deploy.png)

**실제 확인:** 코드 AST는 Dev v1과 같았고, 물리 기본 Lakehouse는 Test로 자동 바인딩됐습니다.
배포 직후 `dbo.cicd_smoke`의 OneLake 경로는 404 **PathNotFound**였으며 아직 실행하지
않았음을 함께 확인했습니다. 임의 오류를 빈 테이블로 처리한 결과가 아닙니다.

이것이 **정의 배포는 Lakehouse 데이터를 복사하지 않는다**는 점을 확인하는 체크포인트입니다.

## 4-5. Test에서 Notebook 실행·실제 데이터 검증

1. Test의 기본 Lakehouse를 다시 확인합니다.
2. 배포된 v1 Notebook을 실행합니다.
3. 현재 Workspace가 Test인지, 실제 Delta 경로가 Test Lakehouse인지 확인합니다.
4. 10행·고유 ID 0–9·모든 값과 release=v1·합계 45를 확인합니다.

![Test v1의 실제 실행 결과와 Test 환경의 물리 Delta 위치](screenshots/w39-test-v1-verified-output.png)

**실제 수행:** Job Scheduler API로 실행하고 실제 실행 스냅샷과 결과를 확인했습니다.
실행 후에만 OneLake 테이블 경로가 200으로 존재했습니다. 생성된 Delta commit이나
Completed라는 상태만으로 데이터 정합성을 주장하지 않았습니다.

> schema-enabled Lakehouse에는 현재 Tables List API가 지원되지 않아
> `UnsupportedOperationForSchemasEnabledLakehouse`를 반환했습니다. 이 응답을 빈 목록으로
> 무시하지 않았으며, 실제 UI·OneLake 경로·Spark의 테이블 읽기를 사용했습니다.

## 4-6. 환경별 기본 Lakehouse 규칙

Git의 Feature 분기는 [Git binding 설정](02-git-integration.md), 단계 간 배포는
Pipeline의 의존성 auto-binding으로 확인했습니다. 두 기능을 같은 설정이라고 혼동하지 않습니다.

특정 대상 Lakehouse를 고정해야 한다면 **대상 Test 또는 Production 단계**에서 Notebook
배포 규칙을 설정합니다. Development에 대상 환경 규칙을 만들지 않습니다.

1. 첫 정의 배포로 대상 Lakehouse와 Notebook의 pairing을 확인합니다.
2. 대상 단계 **Deployment rules → CI_CD_Smoke → Default lakehouse → Add rule**을 엽니다.
3. **From**에서 source 단계의 실제 `CI_CD_Demo`를 선택합니다.
4. **To → Other**를 선택하고 대상의 실제 Lakehouse ID·이름·Workspace ID를 입력합니다.
5. 대상이 같은 단계의 Lakehouse인지 대조한 뒤 Save합니다.

![Test 단계에서 확인하는 기본 Lakehouse 배포 규칙](screenshots/w40-test-default-lakehouse-rule.png)

규칙은 auto-binding보다 우선합니다. Source와 같은 Lakehouse를 유지하는 옵션을 고르면
다른 환경을 참조할 수 있습니다. 이 실습의 쓰기 전 guard는 그런 실행을 거부합니다.
규칙을 저장한 것과 그 규칙이 적용된 **다음 배포·실행 검증**은 구분합니다.
규칙 설정의 실제 저장 여부·검증 범위는 [실행 기록](05-execution-record.md)을 확인합니다.

## 4-7. PR 승인 후 Dev v2 → Test v2 — 아직 미실행

아래는 실제 PR 검토·병합과 [Dev v2 Update/실행](02-git-integration.md)을 마친 뒤 진행합니다.

1. Dev가 승인된 main과 같고 실제 v2 결과가 10행·합계 90인지 확인합니다.
2. Test 대상, Development 원본으로 변경을 비교합니다.
3. Notebook의 v1 → v2 두 상수와 의도된 metadata 변경을 확인합니다.
4. 필요한 Lakehouse 의존성·대상 규칙을 확인하고 배포합니다.
5. 실제 merge SHA와 검증 근거를 note에 남깁니다.
6. Test 코드·바인딩을 확인하고 실행해 실제 v2 10행·합계 90을 검증합니다.

기존 Test v1 합계 45를 v2 검증으로 재사용하지 않습니다. Git Commit이나 Definition 배포만으로
기존 Test 데이터가 v2로 바뀌지 않습니다.

## 4-8. Test 검증 후 승인 → Production — 아직 미실행

**현재 Production은 단계에 연결만 되어 있고 아이템·테이블은 생성하지 않았습니다.**
아래 구간의 성공 화면이나 결과를 합성하지 않았습니다.

1. 사람이 PR/merge SHA, Test v2 실제 결과, 대상·변경·비용을 검토하고 릴리스를 승인합니다.
2. **대상 Production**, **Deploy from = Test**를 확인합니다.
3. 첫 배포라면 Lakehouse와 Notebook을 함께 선택합니다.
4. 방향·아이템·실제 승인된 SHA·검증 note를 확인하고 배포합니다.
5. Production에 생긴 실제 Lakehouse ID와 Notebook의 물리 바인딩을 확인합니다.
6. 필요하면 Production에 그 Lakehouse를 대상으로 하는 규칙을 구성합니다.
7. 쓰기 전 guard를 통과한 뒤 Production Notebook을 실행합니다.
8. **실제 Production 데이터**의 10행·유일한 ID·모든 v2 값·합계 90과 물리 위치를 확인합니다.
9. 배포 이력과 데이터 검증 결과를 함께 기록합니다.

Dev의 데이터·Feature의 성공·Test의 v1 결과는 Production 검증을 대신하지 않습니다.
승인이 없거나 대상 바인딩이 불명확하면 이 단계에서 멈춥니다.

# 7. 실습 완료 확인과 정리

[처음으로](README.md) · [이전: Test v2와 Production](06-test-production-release.md) · [실습 목차](README.md#workshop-order)

**목표:** 6장까지의 검증 결과를 확인·보관하고, 실습 리소스의 유지 여부와 비용을 정리합니다.
정상 결과를 이미 확인했다면 이 장을 위해 다시 배포하거나 Notebook을 실행할 필요는 없습니다.

## 7-1. 최종 결과 확인

| 대상 | 완료 기준 |
|---|---|
| GitHub main / PR | main의 코드는 v2이며 PR은 Merged |
| Dev / Feature | 각 Workspace의 Lakehouse에서 v2·10행·합계 90 검증 완료 |
| Test / Production | 각 Workspace의 Lakehouse에서 v2·10행·합계 90 검증 완료 |
| 배포 이력 | Dev → Test v1 초기 배포, Dev → Test v2 업데이트, Test → Production 배포 성공 확인 |

실행 결과의 Workspace·Lakehouse ID와 Delta 위치가 각 환경을 가리키는지 확인합니다.
데이터는 모든 ID가 0–9이고 `value=id*2`, `release=v2`여야 합니다.
Git 동기화나 배포 성공 표시만으로 실제 데이터 검증을 대신하지 않습니다.

## 7-2. 결과 보관

1. 본인의 PR과 배포 이력을 보관합니다.
2. 환경별 Notebook 검증 출력이나 실행 스냅샷을 보관합니다.
   과거 예제의 ID·결과를 본인의 실습 결과로 사용하지 않습니다.

## 7-3. 리소스와 비용 정리

1. 실행이 끝난 Notebook의 **Stop session**으로 남아 있는 Spark 세션을 종료합니다.
2. 리소스를 삭제하려면 실습 전용인지, 공유 사용자·의존성·진행 중 job이 없는지 확인하고,
   필요한 자료를 보관한 뒤 데이터 손실과 삭제 범위를 승인받습니다.
   Workspace 삭제 전에는 Pipeline 단계 할당을 해제합니다.
3. 사용이 끝난 PAT는 다른 연결에서 쓰이지 않는지 확인한 뒤 폐기합니다.
4. 공유 Capacity와 보안 그룹·Tenant settings는 임의로 변경하지 않습니다.
   Capacity 중지·삭제는 소유자와 사용 범위·비용 영향을 확인하고 별도로 승인받습니다.

**브라우저 종료나 Spark 세션 종료만으로 Capacity 비용이 중지되지는 않습니다.**
리소스를 유지한다면 비용도 계속 확인합니다.

**완료:** 결과 보관과 리소스·비용 확인까지 마치면 기본 핸즈온은 종료됩니다.

---

## 다음으로 이동

| 이전 단계 | 전체 목차 | 실습 종료 |
|---|---|---|
| [← Test v2 배포·Production 승격](06-test-production-release.md) | [실습 순서](README.md#workshop-order) | [가이드 소개로 돌아가기](README.md) |

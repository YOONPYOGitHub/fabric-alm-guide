# 5. 검증, 장애 대응, 복구와 비용 정리

[처음으로](README.md) · [이전: 배포](04-deployment-pipelines.md) · [실제 기록](06-execution-record.md)

## 5-1. 네 가지 근거를 함께 확인

| 구분 | 확인할 것 | 이것만으로 부족한 것 |
|---|---|---|
| Git | branch, directory, 실제 SHA, 변경 목록 0 | Commit 메시지의 v2 문자열 |
| 정의 | 전체 Notebook 코드, 셀 수, Lakehouse 의존성 | 이름·Saved·초록 배지 |
| 배포 | source/target stage ID, 아이템 목록, note, 완료 상태 | Pipeline 카드 연결 |
| 데이터 | 환경 ID·물리 Delta 위치·시각·10행·고유 ID·전체 값·합계 | Running·Completed·새 Delta commit |

환경마다 물리 Workspace/Lakehouse ID가 다른 것이 정상입니다. 공통 코드는 AST 또는
코드 영역으로 대조하고 metadata는 각 환경의 실제 대상과 비교합니다. metadata까지 포함한
전체 파일 hash가 모든 환경에서 같아야 한다고 가정하지 않습니다.

이 가이드의 [실습용 오프라인 테스트](examples/test_smoke_contract.py)를
[Git 장의 준비 단계](03-git-integration.md#prepare-smoke-tests)에서 본인의 실습 저장소에 복사했다면,
그 실습 저장소 루트에서 추가 패키지 없이 실행할 수 있습니다.

```bash
python3 -m unittest discover -s workshops/cicd/tests -v
```

이 검사는 구문·release/multiplier 계약·guard의 정상/오류 입력·쓰기 전 실행 순서·Git logical
의존성을 검사합니다. Spark나 라이브 tenant를 검증하는 테스트가 아닙니다.
가이드 자체의 오프라인 검사 명령은 [README](README.md)에 있습니다.

## 5-2. 자주 멈추는 지점

| 증상 | 확인 / 대응 |
|---|---|
| GitHub 공급자가 회색 | 일반 Git, GitHub 정책, 실제 그룹 멤버와 적용 시간을 먼저 확인. PAT 반복 발급 금지 |
| GitHub 404 또는 로그인 만료 | 올바른 계정의 Private 저장소 접근과 브라우저 로그인을 확인. 암호·MFA는 사용자가 처리 |
| branch 목록이 오래됨 | GitHub의 실제 branch HEAD를 확인하고 UI를 새로 고침. 동명 branch/Workspace를 중복 생성하지 않음 |
| UI가 일시적으로 Premium 필요라고 표시 | 실제 Capacity 할당·Active 상태와 권한을 조회하고 화면 로딩을 확인. 즉시 SKU·RBAC·정책을 바꾸지 않음 |
| Lakehouse 생성 화면이 멈춤 | 실제 아이템 목록을 먼저 대조. 이미 생성됐을 수 있으므로 맹목적 재제출 금지 |
| Python 들여쓰기 오류 | 실행 전에 저장된 원본을 내보내 구문 검사. 셀 출력 파일이 아니라 작성 원본·정의를 보정 |
| 기본 Lakehouse 누락 / 다른 Workspace | 실행 중단. Git binding 또는 대상 규칙·실제 metadata 확인. guard 삭제나 source 경로 하드코딩 금지 |
| schema-enabled Tables API 오류 | 오류를 빈 목록으로 대체하지 않음. UI와 실제 OneLake/Spark로 확인 |
| API job Completed인데 검증 값 없음 | 실제 응답의 `properties.exitValue`와 실행 스냅샷을 확인. 상태만으로 데이터 성공 처리 금지 |
| Git LRO Succeeded 뒤 OperationHasNoResult | 결과 없는 mutation인지 확인하고 실제 Git 상태를 재조회. 성공한 작업을 반복 제출하지 않음 |
| 일부 아이템만 배포됨 | 실패·pairing·의존성을 확인하고 중단. 성공했다고 덮거나 Production에 계속 배포하지 않음 |
| Test 합계가 여전히 45 | 정의만 v2로 바뀌었는지, 올바른 환경에서 Notebook을 실행했는지, 실제 release·행 값을 대조 |
| 행 수·schema·값이 기대와 다름 | 소스·바인딩·실제 데이터를 보존해 분석. 자동 DROP/overwrite/수동 행 삭제 금지 |

UI 캡처가 비활성 버튼을 보여줄 수 있습니다. 입력 검증·서버 응답이 끝나 활성화된 뒤
확정해야 합니다. 클릭을 시도했다는 기록만으로 변경 성공을 주장하지 않습니다.

## 5-3. API 실행을 확인하는 경우

이번 실행은 공식 Job Scheduler API를 사용하고 실제 Notebook 스냅샷을 촬영했습니다.

```text
POST /v1/workspaces/{workspaceId}/items/{notebookId}/jobs/RunNotebook/instances
GET  /v1/workspaces/{workspaceId}/items/{notebookId}/jobs/instances/{jobId}
GET  /v1/workspaces/{workspaceId}/notebooks/{notebookId}/jobs/execute/instances/{jobId}?beta=true
```

202의 실제 Location과 Retry-After를 보관하고 제한 시간 안에서 상태를 확인합니다.
토큰·헤더·자격 증명은 출력·보관하지 않습니다. 재시도 전에 이전 job과 실제 대상 상태를
확인해 중복 실행을 피합니다.

현재 실행에서 검증 JSON은 마지막 응답의 **`properties.exitValue`**에 있었습니다.
[공식 문서](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-public-api)의 축약 예시에
있는 최상위 `exitValue`를 무조건 가정하지 않습니다. JSON의 환경 ID·release·수치와 스냅샷의
실제 테이블 출력을 대조합니다.

## 5-4. 코드 복구와 데이터 복구는 다름

- 잘못된 코드의 되돌리기는 정상 Git revert/수정 PR과 검토·재배포로 처리합니다.
  force-push나 `reset --hard`로 검토 이력을 지우지 않습니다.
- Notebook 정의를 되돌려도 Delta 데이터가 과거 상태로 자동 복구되지는 않습니다.
- 이 예제의 ID MERGE는 10개의 합성 ID를 다룹니다. 분산 전체의 exactly-once나
  이력 보존·손실 데이터 복구를 보장하지 않습니다.
- Delta 복구, 역사 데이터 재처리, DROP·overwrite·watermark 초기화 등은 별도의 영향 검토와
  승인 범위입니다. 검증을 통과시키기 위한 자동 정리로 사용하지 않습니다.
- 규칙을 바꾼 뒤에는 다음 배포의 실제 metadata와 쓰기 전 guard, 실행 결과를 다시 검증합니다.

## 5-5. 종료·정리 체크리스트

정리도 변경 작업입니다. 아래는 **승인 후 수행할 체크리스트**이며 이 실행에서 삭제·중지하지
않았습니다.

1. Git branch·Commit·PR·배포 note·실행 스냅샷과 검증 기록을 보관합니다.
2. 각 Workspace의 실제 ID와 사용자를 확인하고 진행 중 job·공유 의존성이 없는지 확인합니다.
3. 실습용 아이템/Workspace/Pipeline의 삭제 범위와 데이터 손실을 승인받습니다.
4. 만료/폐기할 PAT가 다른 연결에서 쓰이지 않는지 확인한 뒤 관리합니다.
5. 보안 그룹·tenant 정책은 다른 사용자에게 미치는 영향을 검토한 뒤 관리자가 정리합니다.
6. Capacity는 이 가이드가 임의로 중지·삭제하지 않습니다. 공유 사용 여부와 비용 영향을
   소유자에게 확인하고 별도로 승인받습니다.

브라우저 종료, 작업 일시중단, Git disconnect는 비용 중지를 뜻하지 않습니다.

---

## 다음으로 이동

| 이전 단계 | 전체 목차 | 다음 단계 |
|---|---|---|
| [← Test v2 배포·Production 승격](04-deployment-pipelines.md#release-v2) | [실습 순서](README.md#workshop-order) | [실제 수행 기록과 검증 범위 →](06-execution-record.md) |

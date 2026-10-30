# 실습용 코드와 테스트

[처음으로](../README.md) · [Notebook 준비](../02-lakehouse-notebook.md) · [Git과 PR](../03-git-integration.md)

**목표:** 이 폴더의 코드와 테스트로 실습을 준비합니다.
별도 예제 저장소의 접근 권한은 필요하지 않습니다.

| 파일 | 사용 시점 | 사용 방법 |
|---|---|---|
| [notebook-v1.py](notebook-v1.py) | [Notebook 준비](../02-lakehouse-notebook.md#2-3-세-개의-코드-셀-준비) | `# CELL` 구분자 줄을 제외한 세 영역의 코드만 Dev Notebook의 세 셀에 복사 |
| [test_smoke_contract.py](test_smoke_contract.py) | [Git 장의 테스트 준비](../03-git-integration.md#prepare-smoke-tests) | 본인 실습 저장소의 `workshops/cicd/tests/test_smoke_contract.py`로 저장 |

## Notebook 코드

`notebook-v1.py`는 Fabric의 **PySpark (Python)** Notebook에서 실행할 코드입니다.
로컬 Python에서 직접 실행하지 않습니다. v1은 `RELEASE = "v1"`, `MULTIPLIER = 1`입니다.
Feature 단계에서만 두 값을 `"v2"`와 `2`로 바꿉니다.

`# CELL ********************` 줄은 영역을 나누는 표시이므로 Notebook 셀에 복사하지 않습니다.
Fabric이 Git으로 내보낼 때 구분자를 자동으로 추가하므로, 셀에 포함하면 구분자가 중복되어
오프라인 테스트의 세 코드 셀 검사가 실패합니다.

이 파일에는 기존 환경의 metadata·Workspace ID·Lakehouse ID를 넣지 않았습니다.
Dev에 Lakehouse와 Notebook을 직접 만들고 기본 Lakehouse를 연결한 뒤 코드를 복사합니다.
`.platform`, `notebook-settings.json` 등 Git 아이템 정의는 본인의 Fabric에서 생성·내보냅니다.

## 실습용 오프라인 테스트

테스트 파일은 가이드 폴더에서 바로 실행하는 파일이 아닙니다.
Git 장의 바인딩 설정·최초 내보내기를 마친 **본인 실습 저장소**에 아래처럼 배치합니다.

```text
workshops/cicd/
  fabric/
    CI_CD_Demo.Lakehouse/
      .platform
    CI_CD_Smoke.Notebook/
      notebook-content.py
      notebook-settings.json
      .platform
  tests/
    test_smoke_contract.py
```

아이템 정의 파일은 복사하지 않고 Fabric이 만든 파일을 그대로 사용합니다.
Linux/WSL의 터미널에서 본인 실습 저장소 루트를 기준으로 실행합니다.

```bash
python3 -m unittest discover -s workshops/cicd/tests -v
```

Python 3.12 이상이며 추가 패키지·GitHub 토큰·Fabric 인증 없이 **9개 테스트**가 실행됩니다.
v1과 v2의 상수 조합, 쓰기 전 환경 확인 함수, Git의 Lakehouse logical ID와 바인딩 설정을 검사합니다.
Spark 실행이나 실제 Delta 데이터 검증은 하지 않습니다. 필수 파일이 없으면 실패해야 정상이며,
테스트가 0개인 결과를 성공으로 처리하지 않습니다.

가이드 자체와 이 예제 묶음의 회귀 검사는 [가이드의 검사 안내](../README.md#7-캡처-재생성과-오프라인-검사)를 따릅니다.

---

## 다음으로 이동

| 이전 단계 | 전체 목차 | 다음 단계 |
|---|---|---|
| [← Lakehouse와 Notebook v1](../02-lakehouse-notebook.md) | [실습 순서](../README.md#workshop-order) | [GitHub 연결·Feature·PR 생성 →](../03-git-integration.md) |

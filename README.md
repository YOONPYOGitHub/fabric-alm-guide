# Microsoft Fabric Git integration and deployment pipelines

합성 데이터 Notebook으로 GitHub 소스 관리와 Development → Test → Production 배포를 익히는 단계별 실습 가이드입니다. 화면의 영문 메뉴 이름을 기준으로 설명하며, 캡처는 실제 Fabric/GitHub 화면에서 Playwright로 촬영했습니다.

## 저장소 역할

| 저장소 | 역할 |
|---|---|
| [fabric-alm-guide](https://github.com/YOONPYOGitHub/fabric-alm-guide) | 이 가이드의 문서 4개와 실제 화면 캡처 36장: 빨간 박스 강조본과 원본 |
| [fabric-alm-lab](https://github.com/YOONPYOGitHub/fabric-alm-lab) | Fabric과 Git으로 동기화하는 Notebook 등 아이템 정의 |

Fabric Dev Workspace의 Git 설정에는 **fabric-alm-lab / main / /fabric**을 사용합니다. 가이드 저장소를 만들더라도 이 연결은 그대로 유지합니다.

## 캡처 읽는 방법

**빨간 박스는 화면당 핵심 한 곳을 원칙으로 하며, 필요한 경우에만 최대 두 곳**을 표시합니다. 넓은 코드·설명 영역이나 모든 설정 항목을 동시에 두르지 않습니다. 전체 구성이나 이미 색상으로 차이가 표시된 비교 화면은 박스 없이 보존할 수 있습니다. 실제 UI의 선택 상태나 데이터는 변경하지 않았습니다. 비활성 버튼은 필수 입력을 마친 뒤 활성화될 수 있습니다.

본문에는 [강조본](screenshots/)을 사용하고, 주석 없는 [원본 36장](screenshots-originals/)도 함께 보관합니다. 박스 위치와 대상 설명은 [주석 정의](tools/screenshot_annotations.json)에서 확인할 수 있습니다.

## 읽는 순서

1. [사전 준비와 Fabric 관리자 설정](01-prerequisites.md)을 수행합니다.
2. [3장의 3-1: Notebook v1 작성과 실행](03-deployment-pipelines.md)까지 진행합니다.
3. [GitHub 연결, Commit, Update from Git](02-git-integration.md)을 수행합니다.
4. [3장의 나머지: Deployment pipelines 생성과 단계별 배포](03-deployment-pipelines.md)를 진행합니다.

이미 준비된 실습 환경에서는 같은 이름의 리소스를 다시 만들지 않습니다. 일부 캡처에는 준비된 파이프라인의 단계 배지가 표시됩니다. Git 연결과 Notebook 작성은 배포 파이프라인 생성 전에도 수행할 수 있습니다.

## 구성

```text
GitHub: fabric-alm-lab / main / fabric
               ↕ Git integration
Development Workspace → Test Workspace → Production Workspace
               Deployment pipeline: dp-fabric-alm-lab
```

| 대상 | 캡처에 사용한 이름 |
|---|---|
| GitHub 저장소 | [YOONPYOGitHub/fabric-alm-lab](https://github.com/YOONPYOGitHub/fabric-alm-lab), Private |
| Git branch / directory | `main` / `/fabric` |
| GitHub 기능 허용 그룹 | `grp-fabric-alm-lab-users`, 실습 계정 한 명 |
| Development | `ws-fabric-alm-lab-dev` |
| Test | `ws-fabric-alm-lab-test` |
| Production | `ws-fabric-alm-lab-prod` |
| Capacity | `fb001`, F16, Korea Central |
| 배포 파이프라인 | `dp-fabric-alm-lab` |
| Notebook | `nb_cicd_demo` |

다른 환경에서 따라 할 때는 자신의 계정, 저장소, Workspace 및 Capacity로 바꿉니다. Private 저장소와 Workspace 링크는 해당 대상에 접근 권한이 있어야 열립니다. Workspace와 Notebook 실행은 Capacity/CU 및 저장소 사용량에 영향을 줄 수 있습니다.

## 실제 수행 상태

아래는 **2026-10-19 검증 기록**이며 현재 시점의 서비스 상태를 보장하는 상태판은 아닙니다.

| 구간 | 실제 결과 | 수행 방식 / 남은 작업 |
|---|---|---|
| GitHub 로그인·Private 저장소 | 확인 완료 | 저장소 설명과 README에 실습 설명 반영 |
| Fabric Workspace 3개·Capacity | 준비 완료 | Dev는 UI 생성, Test/Prod는 Core REST API 생성 |
| GitHub PAT | 저장소 한정 토큰 발급·Fabric 등록 | Contents RW / Metadata RO, 7일; 토큰 값 미촬영·미저장 |
| Fabric GitHub 테넌트 설정 | **실습 그룹에만 Enabled** | 승인 후 적용, 그룹 한 명·관리자 위임 없음 확인 |
| Dev Git 연결·최초 동기화 | 완료 | `main /fabric`, 실제 Notebook 정의 생성 |
| Workspace → Git Commit | 완료 | UI에서 v1 → v1.1 Commit, `c653df75` |
| Git → Workspace Update | 완료 | Git의 v2 Commit `a1017399`를 UI에서 Update, Synced 확인 |
| Dev Notebook v2 | 실제 실행 완료 | `release=v2`, `rows=3`, `total=70` |
| Dev → Test v2 | 배포 성공 | 실제 UI 선택·Compare·확정 수행 |
| Test Notebook v2 | 실제 실행 완료 | `release=v2`, `rows=3`, `total=70` |
| Test → Prod v2 | 배포 성공 | 공식 Core REST API로 Notebook 하나만 승격 |
| Prod Notebook v2 | 실제 실행 완료 | `release=v2`, `rows=3`, `total=70` |
| 세 단계 정의와 Git 대조 | 일치 | 전체 소스·정규화 SHA-256 일치, Git 변경 0 |
| GitHub Actions 자동 CI/CD | 미구성 | 본 실습의 수동/API 배포와 구분 |

GitHub 기능의 **비활성 → 그룹 범위 지정 → 적용 완료 → Workspace 연결**까지 [사전 구성 장](01-prerequisites.md)에 실제 캡처를 포함했습니다. 토큰 값이나 가상의 UI는 캡처에 넣지 않았습니다.

Git integration은 아이템 정의를 버전 관리하고, Deployment pipelines는 단계 사이에 아이템 정의를 배포합니다. Git Commit만으로 테스트나 Production 배포가 자동 실행되지는 않습니다. 자동 CI/CD에는 별도의 실행 주체, 인증, 테스트, 승인 및 트리거 구성이 필요합니다.

## 검증된 배포 결과

![Production에서 실제로 실행한 Git v2 Notebook의 합계 70](screenshots/37-production-notebook-v2-executed-output-70.png)

최종 확인은 2026-10-19 15:18 KST 기준입니다. 세 Workspace의 전체 Notebook 소스가 Git Commit `a1017399`와 같고 Git 변경 목록이 비었으며, 두 v2 승격의 **Succeeded** 상태와 방향·배포 노트를 대조했습니다.

배포 성공은 Notebook 실행 성공과 다릅니다. 실행 출력과 대상 정의를 각각 확인하는 방법은 [배포 가이드](03-deployment-pipelines.md)를 참고합니다.

## 공식 문서

- [Get started with Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started?tabs=github%2CGitHub%2Ccommit-to-git)
- [Get started using deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines?tabs=from-fabric%2Cnew-ui)
- [Git integration admin settings](https://learn.microsoft.com/en-us/fabric/admin/git-integration-admin-settings)

## 캡처 주석 다시 생성하기

Python 3.12 가상 환경에서 아래 명령으로 원본에서 강조본을 재생성할 수 있습니다. Windows PowerShell에서는 `source` 대신 `.\.venv\Scripts\Activate.ps1`로 활성화합니다.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements.txt
python tools/annotate_screenshots.py
python -m unittest discover -s tests
```

도구는 원본을 덮어쓰지 않습니다. 캡처를 바꾸면 주석 정의의 이미지 크기와 박스 좌표도 실제 화면에 맞춰 갱신해야 하며, 크기가 다르거나 박스가 이미지 밖이면 오류로 중단합니다.

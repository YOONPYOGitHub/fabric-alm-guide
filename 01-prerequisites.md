# 1. 사전 준비와 필수 설정

[처음으로](README.md) · [다음: Lakehouse + Notebook](02a-lakehouse-notebook.md)

**목표:** 기능을 사용할 수 있는 계정·Capacity·정책·권한을 먼저 준비합니다.
이미 Enabled인 설정도 확인 경로와 적용 범위를 검토하고 기록합니다.

## 1-1. 계정, 라이선스, Capacity, 역할

1. [Fabric](https://app.fabric.microsoft.com)에 로그인하고 계정 메뉴에서 tenant를 확인합니다.
2. 사용할 Capacity의 지역·SKU·Active 상태와 Workspace 할당 권한을 확인합니다.
3. 각 Workspace의 **Manage access**에서 실습 계정의 역할을 확인합니다.
4. Pipeline을 만든 뒤에는 별도로 **Manage Access**의 역할을 확인합니다.

| 작업 | 필요한 권한 / 조건 |
|---|---|
| Tenant settings 변경 | Fabric Administrator 또는 해당 설정을 위임받은 관리자 |
| Workspace 생성·Capacity 할당 | 생성 정책 허용, 해당 Capacity 사용·할당 권한 |
| Workspace Git 연결과 단계 할당 | 해당 Workspace Admin |
| Pipeline 생성·관리·단계 연결 | Pipeline Admin; Workspace Admin과 별개 |
| Git 읽기·쓰기와 PR | 해당 GitHub 저장소 권한 및 유효한 인증 |
| Notebook 실행 | Fabric Capacity와 해당 아이템·Lakehouse 접근 권한 |

Azure 구독의 Owner 역할이 Fabric Workspace/Pipeline Admin을 자동 부여하지 않습니다.
실습을 위해 Global Administrator나 조직 전체 권한을 새로 부여하지 않습니다.

![Workspace Manage access에서 실습 계정의 Admin 확인](screenshots/w36-prerequisite-workspace-admin.png)

**빨간 박스:** 현재 계정의 Workspace 역할입니다. `Add people or groups`로 임의의 멤버를
추가하는 단계가 아닙니다.

![Pipeline Manage Access에서 별도의 Admin 확인](screenshots/w41-prerequisite-pipeline-admin.png)

**기대 결과:** 각 작업의 담당자와 권한이 확인됩니다. 촬영 환경은 기존 F16을 재사용했으며
새 Capacity를 만들거나 일시 중지 상태를 임의로 해제하지 않았습니다.

## 1-2. 반드시 확인할 네 가지 Tenant settings

**경로:** 우측 **Settings → Admin portal → Tenant settings → Filter by keyword**.
Admin portal이 보이지 않으면 관리자에게 아래 설정의 상태·범위 확인을 요청합니다.

| 검색할 설정 | 확인할 사항 |
|---|---|
| **Users can create Fabric items** | Notebook·Lakehouse를 만들 실습 사용자에게 Enabled |
| **Create workspaces** | 실습 사용자에게 Workspace 생성 허용 |
| **Users can synchronize workspace items with their Git repositories** | 일반 Git 통합 허용 |
| **Users can sync workspace items with GitHub repositories** | GitHub 공급자와 실습 사용자/그룹 허용 |

### Fabric 아이템 생성

설정을 펼쳐 Enabled 상태를 확인합니다. **이미 활성화되어 있으면 변경 없이 확인만** 합니다.

![이미 Enabled인 Fabric 아이템 생성 필수 설정](screenshots/w13-mandatory-fabric-items-enabled.png)

### Workspace 생성

실습 사용자가 포함된 범위에 생성이 허용되어야 합니다. 아래 화면의 서비스 주체 설정과
사람이 Workspace를 만드는 설정은 서로 다릅니다.

![이미 Enabled인 Create workspaces 필수 설정](screenshots/w08-mandatory-create-workspaces-enabled.png)

### 일반 Git 통합

GitHub 로그인이나 PAT 발급만으로 Fabric의 Git 정책이 활성화되지는 않습니다.

![일반 Git 통합 Enabled 확인, 설정 변경 없음](screenshots/w23-prerequisite-git-enabled.png)

### GitHub 공급자: 필요한 경우에만 그룹 한정 허용

이 설정은 최초 준비 당시 Disabled였습니다. 아래 두 장은 **같은 테넌트에서 이미 승인 후
수행한 실제 사전 구성 기록**입니다. 캡처를 위해 다시 Disabled로 바꾸지 않았습니다.

![최초 사전 구성에서 확인한 GitHub 공급자 Disabled](screenshots/17-tenant-github-setting-disabled.png)

변경이 필요한 환경에서만 다음을 수행합니다.

1. 대상 tenant·GitHub 저장소·허용 범위와 메타데이터 내보내기 영향을 검토하고 승인을 받습니다.
2. Entra Security 그룹을 준비하고 실제 실습 사용자만 멤버로 포함합니다.
3. GitHub 설정을 Enabled로 바꾸고 **Specific security groups**를 선택합니다.
4. 그룹을 검색한 뒤 **검색 결과를 선택**합니다. 이름만 입력한 상태로 저장하지 않습니다.
5. 전체 조직 허용, 제외 그룹, 관리자 위임을 불필요하게 추가하지 않습니다.
6. **Apply** 후 적용 상태와 그룹 멤버를 다시 확인합니다.

![최초 승인 후 Specific security groups와 실습 그룹 지정](screenshots/18-tenant-github-specific-group-before-apply.png)

촬영 환경의 그룹 이름은 `grp-fabric-alm-lab-users`이며 실습 계정 한 명만 포함했습니다.
아래는 재작성 시 다시 확인한 **현재 적용 상태**입니다.

![현재 GitHub 설정과 승인된 보안 그룹, 변경 없이 확인](screenshots/w25-prerequisite-github-approved-group.png)

**기대 결과:** `Enabled for a subset of the organization`과 올바른 그룹이 유지됩니다.
정책 반영에는 시간이 걸릴 수 있으므로 공식 안내의 최대 15분을 고려합니다.

GitHub에는 multi-geo 제한 스위치의 적용이 강제되지 않는다는 현재 UI·공식 문서의 안내가
있습니다. 연결 오류를 이유로 **Users can export items to Git repositories in other
geographical locations**까지 일괄 활성화하지 않습니다. 레이블이 있는 아이템의 내보내기
정책도 별도로 확인하며 임의로 완화하지 않습니다.

본 트랙은 사용자 인증을 사용합니다. 서비스 주체의 Workspace 생성 설정이나 Fabric API
설정, AI 정책을 바꾸는 단계가 아닙니다.

## 1-3. 네 개의 Workspace 생성

**경로:** **Workspaces → New workspace**. 먼저 동명 Workspace가 이미 있는지 확인합니다.

| 이름 | Description 예시 |
|---|---|
| `FabricLab-Dev` | `Microsoft Fabric CI/CD workshop - Development stage.` |
| `FabricLab-Feature` | `Microsoft Fabric CI/CD workshop - Feature development.` |
| `FabricLab-Test` | `Microsoft Fabric CI/CD workshop - Test stage.` |
| `FabricLab-Prod` | `Microsoft Fabric CI/CD workshop - Production stage.` |

1. Dev의 이름과 설명을 입력합니다.
2. **Advanced → Workspace type → Fabric**을 선택합니다.
3. **Details**에서 승인된 Capacity를 선택합니다.
4. 이름·유형·Capacity를 대조한 뒤 **Apply**를 선택합니다.

![Dev 생성 시 입력한 Workspace 이름](screenshots/w01-create-development-workspace-name.png)

![Fabric 유형과 기존 fb001 Capacity를 선택한 실제 화면](screenshots/w02-confirm-fabric-f16-capacity.png)

**빨간 박스:** Capacity 선택란입니다. `fb001 - Korea Central`은 촬영 환경의 이름이며,
F16 SKU와 Active 상태는 Capacity 조회로 별도 대조했습니다.

5. 같은 방식으로 Feature, Test, Prod를 생성합니다. 네 Workspace는 **모두 실제 UI로 생성**
   했고 동일한 승인 Capacity에 할당된 것을 API로도 확인했습니다.

![Feature Workspace의 이름 입력](screenshots/w03-create-feature-workspace.png)

![Test Workspace의 이름 입력](screenshots/w04-create-test-workspace.png)

![Production Workspace의 이름 입력](screenshots/w05-create-production-workspace.png)

**기대 결과:** 네 Workspace가 존재하며 실습 계정이 접근할 수 있습니다. Feature는 배포
Pipeline 단계가 아니라 Git feature branch를 검증할 Workspace입니다.

## 1-4. GitHub 저장소와 최소 범위 인증

1. 소스용 `fabric-alm-lab`과 설명용 `fabric-alm-guide`를 구분합니다.
2. 이 실습은 Private 저장소를 사용합니다. 자신의 저장소 owner와 접근 권한을 확인합니다.
3. **Settings → Developer settings → Personal access tokens → Fine-grained tokens**
   에서 필요한 경우 토큰을 발급합니다.
4. **Only select repositories → fabric-alm-lab** 하나만 선택합니다.
5. **Contents: Read and write**, **Metadata: Read-only**를 확인합니다.
6. 짧은 만료 기간을 사용하고 조직 승인·SSO 요구사항이 있다면 따릅니다.

![실제로 사용한 저장소 한정 fine-grained PAT 준비 화면, 발급 값 없음](screenshots/13-github-fine-grained-token-scope.png)

위 화면은 최초 준비 기록이며 토큰 값이 아닌 범위와 권한만 보여줍니다. 촬영 환경의 토큰은
7일 만료였고, 재개 시 등록된 `YOONPYOGitHub-alm` 계정을 재사용했습니다.
현재 유효한 토큰을 캡처를 위해 재발급·교체하지 않습니다.

Fabric **Workspace settings → Git integration → GitHub → Add account**에서 Display name,
Repository URL, PAT를 입력합니다. 토큰은 해당 보안 입력란에서만 취급하고 채팅·문서·Git·로그·
화면 캡처에 남기지 않습니다. 이미 올바른 계정이 등록되어 있다면 그것을 선택합니다.

## 1-5. PR 검토를 실제로 할 수 있는지 확인

**경로:** GitHub 소스 저장소 **Settings → Branches / Rulesets**, **Collaborators**.

![현재 저장소에 필수 branch protection이 구성되지 않은 실제 화면](screenshots/w42-prerequisite-review-enforcement-limitation.png)

촬영 환경은 Private이고 owner가 Admin이지만 `main` 보호가 없었습니다. Rulesets API는
Pro 업그레이드 또는 Public 전환을 요구하는 403을 반환했습니다. 요금제 이름을 추측하거나
결제·공개 범위·협업자를 자동 변경하지 않았습니다.

따라서 이 실행에서는 **필수 리뷰가 기술적으로 강제된다고 주장하지 않습니다.**
협업자는 owner 한 명이었고 작성자의 자기 승인을 독립 리뷰어 승인으로 기록하지 않습니다.
실제 사람이 diff와 검증 근거를 검토하고 병합 의사를 표시해야 다음 단계로 갑니다.
독립 리뷰어 승인이 필요한 조직은 적절한 저장소 정책·요금제·리뷰어를 먼저 준비해야 합니다.

**체크포인트:** 네 설정, Capacity, Workspace/Pipeline 역할, source repository, 인증 범위와
검토 방식이 확인되어야 [Lakehouse 준비](02a-lakehouse-notebook.md)를 시작합니다.

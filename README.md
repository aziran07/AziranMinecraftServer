# Aziran Minecraft Server

Minecraft Java Edition 26.3 NeoForge 서버를 준비하며 웹 관리·모니터링 구성도 함께 관리합니다. 기존 1.21 데이터는 `server-data/`에, Fabric 준비 데이터는 `server-data-26.3/`에 보존하고, 현재 구성은 `server-data-26.3-neoforge/`를 사용합니다. 설치 모드와 준비 상태는 [모드 설치 안내](docs/MODS_26_3.md), 로더 결정 근거는 [로더 비교](docs/LOADER_COMPARISON_26_3.md)를 참고하세요.

게임 서버와 웹 관리·모니터링 서비스 구성은 Docker Compose로 관리합니다. 자체 게임 로직 소스는 없으며, 서비스 구성은 이 저장소에서, 게임 기능은 외부 모드와 로컬 서버 데이터에서 관리합니다.

접속 안내 웹사이트는 **https://aziran.uk**, 게임 서버 주소는 **`mc.aziran.uk`**입니다. 웹사이트에서 클라이언트 `.mrpack`을 다운로드하고 설치 순서를 확인할 수 있습니다. 웹사이트 소스와 배포 구성은 [웹사이트 운영 안내](docs/JOIN_GUIDE.md)를 참고하세요.

현재 Compose는 **Minecraft, 웹 RCON, 지도 HTTPS 원본(`webmap-nginx`)을 실행**합니다(Chunky 무인 프리젠 사이드카는 별도 캠페인용). Portainer·Grafana·Prometheus·cAdvisor·Nginx는 주석 처리되어 있습니다. 웹 RCON은 Docker 내부에서만 접근하며 공개 웹사이트에는 관리 기능을 제공하지 않습니다.

웹 지도는 26.3 서버에 BlueMap `5.27-neoforge` JAR을 설치해 운영 중입니다(2026-09-24, 오프라인 백업 확인 후 설치). 서버는 healthy·재시작 0회이며 BlueMap은 Compose 네트워크의 `minecraft:8100`에서 HTTP 200으로 응답하고 렌더링이 진행 중입니다. `8100`은 호스트에 게시하지 않습니다. 공개 주소 **https://mcmap.aziran.uk**는 Cloudflare 프록시(주황 구름) `A` 레코드 → 서버 호스트 `443`의 `webmap-nginx`(Let's Encrypt `mcmap.aziran.uk` 인증서로 TLS 종료) → `minecraft:8100` 경로로 공개합니다. 2026-09-24 DNS 레코드를 만들고 공개 HTTPS 200을 확인했습니다. 원본 인증서는 **2026-12-23에 만료되며 자동 갱신이 없어** 그 전에 수동 DNS-01로 갱신해야 합니다(Cloudflare Origin 인증서는 `526`으로 거부돼 교체). (이전 계획이던 Cloudflare Tunnel은 터널 생성 API 인증 오류로 만들지 못해 폐기했습니다.) 남은 절차는 [BlueMap 배포 안내](docs/BLUEMAP.md)를 따릅니다. 옛 1.21 서버의 Dynmap(`8123`)은 26.3에서 사용하지 않습니다.

## 작업 시작

1. [AGENTS.md](AGENTS.md): Codex/Claude 역할, Orca 협업 절차, 데이터 보호·검증 규칙.
2. [프로젝트 지도](docs/PROJECT_MAP.md): 기능별 구현 위치, 네트워크, 로컬 모드, 변경·검증 기준.
3. [CLAUDE.md](CLAUDE.md): Claude 구현 작업 시작 시 확인할 사항.

| 목적 | 먼저 볼 파일 |
| --- | --- |
| 게임 버전·메모리·난이도, 서비스 구성 | [docker-compose.yml](docker-compose.yml) |
| 도메인·HTTPS·관리 UI·WebSocket | [default.conf.template](nginx/templates/default.conf.template) |
| 웹 지도(BlueMap)·HTTPS 원본·배포·롤백 | [docs/BLUEMAP.md](docs/BLUEMAP.md) |
| 게임 TCP 전달(비활성 Nginx) | [minecraft.conf.template](nginx/templates/minecraft.conf.template) |
| 컨테이너 지표 수집 | [prometheus.yml](prometheus.yml) |
| 정기 월드 백업·전체 데이터 보호 백업·복원 | [docs/BACKUPS.md](docs/BACKUPS.md) |
| 설치 모드·버전·해시 고정 | [mods-26.3.lock.json](mods-26.3.lock.json) |

## 실행 전 확인

- Docker와 Docker Compose 플러그인이 필요합니다.
- `.env`를 별도로 준비해야 합니다. 필요한 변수 이름은 프로젝트 지도에 있습니다. `nginx/cert.pem`, `nginx/key.pem`(Git 제외 Let's Encrypt 인증서 fullchain·키)은 `webmap-nginx`가 읽기 전용으로 마운트하므로 필요합니다. 보관·수동 갱신 절차는 [BlueMap 배포 안내](docs/BLUEMAP.md#원본-인증서-관리)를 따릅니다.
- 모드, 월드, Grafana 대시보드 등 영속 데이터는 Git에 포함되지 않습니다. 새 clone만으로 기존 운영 서버를 재현할 수 없습니다. 모드 JAR은 `mods-26.3.lock.json`의 URL과 해시로 다시 받을 수 있습니다. Fabric 준비 당시의 목록은 `mods-26.3-fabric-historical.lock.json`에 보존돼 있습니다.
- 활성 Compose 서비스는 호스트의 `25565`(게임, `minecraft`)와 `443`(지도 HTTPS, `webmap-nginx`) TCP 포트만 게시합니다. 호스트 `80`·`3733`은 이 저장소와 무관한 다른 Nginx가 씁니다. 안내 웹사이트는 GitHub Pages에서 HTTPS로 제공합니다.

설정 검사:

```sh
docker compose config --quiet
bash -n mc_backup.sh
git diff --check
```

실제 서버를 시작하기로 한 작업에서만 실행합니다. 현재 Compose는 Minecraft 26.3, NeoForge `26.3.0.8-beta`, 데이터 경로 `server-data-26.3-neoforge/`를 사용합니다. 26.3 계열 NeoForge는 베타 채널만 배포되므로 버전을 명시적으로 고정합니다. 시작 전 [남은 준비 사항](docs/MODS_26_3.md)을 확인하세요.

```sh
docker compose up -d --no-deps minecraft   # 게임 서버만 시작 (컨테이너 `aziran-minecraft-26-3`)
docker compose ps
```

게임 `25565`는 Minecraft 컨테이너가 직접 게시합니다. 지도 `8100`은 Compose 네트워크에만 열려 있습니다. 지도 HTTPS 원본은 `webmap-nginx`가 호스트 `443`만 게시해 `https://mcmap.aziran.uk` → `http://minecraft:8100`으로 넘깁니다(`docker compose up -d --no-deps webmap-nginx`, 설정 `nginx/webmap.conf`). 주석 처리된 기존 Nginx(`80`/`443`)는 복원하지 않습니다(호스트 `80` 사용 중, `www`/apex는 GitHub Pages).

운영 사용자의 cron은 매시 30분에 [mc_backup.sh](mc_backup.sh)를 실행합니다. 현재 26.3 NeoForge의 `world/`만 `minecraft_backups/`에 보관하며, 성공한 새 백업 뒤 710분이 지난 정기 백업 파일만 삭제합니다. 실행 결과와 복원 범위는 [월드 백업 안내](docs/BACKUPS.md)를 참고하세요.

## 클라이언트 모드팩

현재 버전은 `1.1.6`이며 Minecraft `26.3`, NeoForge `26.3.0.8-beta`, Java `25`용 모드 19개와 셰이더 팩 1개로 구성했습니다. 서버와 공유하는 모드 14개는 서버와 같은 파일이고, ImmediatelyFast·Mouse Tweaks·JourneyMap·Sodium·Iris 5개는 서버에 설치하지 않는 클라이언트 전용 모드입니다. `1.1.6`은 `1.1.5`에 서버와 같은 무덤 모드 Simple Tomb `1.9.0`만 더했습니다. `1.1.5`의 모드·셰이더 구성은 `1.1.4`와 같고, 새 인스턴스의 멀티플레이 목록에 `Aziran`(`mc.aziran.uk`) 서버를 미리 넣는 기본 `servers.dat`만 더했습니다. `1.1.4`는 `1.1.3`의 모드 16개를 바이트 단위로 그대로 두고 셰이더를 위해 Iris·Sodium과 Complementary Reimagined 셰이더 팩을 더한 판입니다.

`1.1.6`은 GitHub **사전 릴리스(prerelease)** [`client-1.1.6`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.6)으로 공개되어 있으며, 접속 안내 사이트(GitHub Pages)는 이 Release의 `.mrpack`을 가리킵니다. 서버가 Simple Tomb을 활성화하면 이 모드가 없는 `1.1.5` 이하 팩으로는 접속할 수 없으므로 `client-1.1.6` Release 공개 → 사이트 배포 → 서버 재시작(모드 활성화) 순서로 진행합니다. 사전 릴리스로 두는 이유는 **공식 출시 전 실험 단계의 Iris(미병합 PR 빌드)를 담았기 때문입니다.** 이전 버전 `1.1.5`와 `1.1.4`는 사전 릴리스 [`client-1.1.5`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.5), [`client-1.1.4`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.4)에 `.mrpack`과 설치 안내·라이선스 문서·체크섬으로 공개되어 있고 그대로 둡니다. 서버가 Simple Tomb을 활성화한 뒤에는 두 판으로 접속할 수 없습니다.

- 런처 가져오기(권장): [Modrinth 형식 팩](dist/aziran-26.3-client-1.1.6.mrpack)
- MultiMC 가져오기: [인스턴스 ZIP](dist/aziran-26.3-client-1.1.6-multimc.zip)
- 수동 설치: [모드 ZIP](dist/aziran-26.3-client-1.1.6-manual.zip)
- [설치 안내](dist/README.md), [라이선스](dist/LICENSES.md), [고정 목록](mods-26.3-client.lock.json)
- [클라이언트 모드 호환성 검토](docs/CLIENT_MOD_COMPATIBILITY_26_3.md)

### 먼저 읽을 것: JourneyMap과 셰이더 팩은 ZIP 두 개에 들어 있지 않습니다

아래 두 파일은 **수동 ZIP과 MultiMC 인스턴스 ZIP에 담겨 있지 않습니다.** 라이선스가 모드팩에 파일을 직접 담는 것을 금지하고, CurseForge 또는 Modrinth에서 설치 중에 내려받는 방식만 허용하기 때문입니다.

- JourneyMap `26.3-6.0.9+neoforge` — [공식 라이선스](https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/)가 번들·재호스팅을 금지합니다.
- Complementary Reimagined `r5.9.3` — Complementary License Agreement 1.7의 1.2.d가 Modrinth·CurseForge 시스템으로만 모드팩에 넣도록 하고 직접 파일 업로드 재배포를 금지합니다.

**`.mrpack`을 쓰는 쪽을 권합니다.** 런처가 설치 중에 Modrinth CDN에서 두 파일을 받으므로 모드 19개와 셰이더 팩이 모두 갖춰집니다. MultiMC도 `Add Instance` → `Import from zip`에서 `.mrpack`을 가져올 수 있습니다([MultiMC 위키](https://github.com/MultiMC/Launcher/wiki/Import-Instance), 실제 가져오기는 시험하지 않았습니다). ZIP 두 개를 쓰면 모드 18개만 설치되며, 팩 안 `README.md`가 두 파일을 공식 배포처에서 받아 `mods/`와 `shaderpacks/`에 넣는 절차와 SHA-512를 안내합니다.

### 1.1.6: Simple Tomb 추가

서버에 설치한 무덤 모드 Simple Tomb `1.9.0`(CurseForge 파일 `8925463`, `simpletomb-26.3-1.9.0.jar`, LGPL-2.1)과 **같은 파일**을 더했습니다. 죽으면 그 자리에 소지품을 담은 무덤이 생기고, 무덤 위에서 웅크리면 아이템을 되찾습니다. 무덤 블록과 열쇠 아이템을 등록하는 모드라 클라이언트에도 필요합니다. Modrinth CDN에 없는 CurseForge 배포 파일이라 `.mrpack`에도 JAR을 `client-overrides/mods/`로 직접 담았습니다. 나머지 모드 18개, 셰이더 팩, `options.txt`, `servers.dat`는 `1.1.5`와 같습니다. `1.1.6` 아카이브로 새로 만든 인스턴스는 아직 게임에서 실행해 보지 않았습니다.

### 1.1.5: 기본 멀티플레이 서버 목록

모드 18개와 셰이더 팩 1개는 `1.1.4`와 같은 파일입니다. 새로 만든 인스턴스의 멀티플레이 화면에 `mc.aziran.uk`가 이미 들어 있도록 `servers.dat`만 더했습니다. 자세한 내용은 아래 [멀티플레이 서버 목록](#멀티플레이-서버-목록serversdat)을 참고하세요. `1.1.5` 아카이브로 새로 만든 인스턴스는 아직 게임에서 실행해 보지 않았습니다.

### 1.1.4: 셰이더(Iris + Sodium + Complementary Reimagined)

- **Iris** `1.11.6-snapshot+mc26.3-local`: NeoForge 26.3 지원이 아직 병합되지 않은 [Iris PR #3354](https://github.com/IrisShaders/Iris/pull/3354)의 커밋 `10d3598cd96b0566497b66efe66256f468cd977e`를 수정 없이 로컬 빌드한 JAR입니다. 공식 릴리스가 아니고 Modrinth에 없으므로 `.mrpack`에도 JAR을 직접 담았습니다. LGPL-3.0(Iris)·AGPL-3.0(내장 glsl-transformer) 조건에 따라 대응 소스와 라이선스 전문을 세 아카이브 모두의 `sources/iris/`에 함께 담았습니다. 이 디렉터리는 게임 디렉터리 밖이라 설치되지 않습니다.
- **Sodium** `0.9.2`: Iris의 필수 의존성입니다. `1.1.0`의 Windows 크래시(`0xc0000409`) 때문에 `1.1.1`부터 빼 두었던 **같은 파일**이며, 그 원인은 규명하지 않았습니다.
- **Complementary Reimagined** `r5.9.3`: 기본으로 켜 두지 않습니다. 게임에서 `Options` → `Video Settings` → `Shader Packs...`에서 `ComplementaryReimagined_r5.9.3`을 골라 적용합니다.

사용자의 이전 1.1.4 시험 인스턴스는 `options.txt`를 초기화한 첫 실행에서 Complementary 셰이더 적용과 서버 접속에 성공했습니다. 실패한 것은 두 번째 실행이며, 원인은 아래 Occultism 단축키 문제입니다.

사용자가 배포한 1.1.4 팩으로 새로 만든 인스턴스를 Windows에서 두 번 연속 실행하는 데 성공했다고 알려 왔습니다. 이 보고는 두 번의 실행 성공만 다루며, 그 두 실행에서의 서버 접속과 셰이더 적용 여부는 보고에 없습니다.

### Occultism 사역마 단축키 우회(options.txt)

Occultism 26.3 소스(커밋 `631457c`)의 `ClientSetupEventHandler.java` 218행은 사역마 단축키 18개를 `Type.KEYBOARD, -1`로 등록합니다. 첫 실행 뒤 `options.txt`에 `key.keyboard.-1`로 저장되고, 두 번째 실행에서 `InputConstants.isKeyDown`이 `IndexOutOfBoundsException`으로 실패합니다. 이 상류 결함은 팩이 고치지 못합니다.

그래서 `1.1.4`부터 팩은 `version:5023`과 사역마 단축키 18개를 `key.keyboard.unknown`(미지정)으로 적은 최소 `options.txt`를 담습니다(`.mrpack`의 `client-overrides/options.txt`, 수동 ZIP의 `options.txt`, MultiMC ZIP의 `.minecraft/options.txt`). 그래픽·언어·마지막 접속 서버·계정 같은 개인 설정은 넣지 않았습니다. 사용자가 기존 인스턴스 복사본에서 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꾸자 두 번 연속 실행·서버 접속에 성공했고 `-1`이 다시 생기지 않았습니다.

- 이 `options.txt`는 **새 인스턴스**에서만 그대로 쓰입니다. 이미 `options.txt`가 있는 인스턴스·게임 디렉터리에는 기존 파일이 남아 적용되지 않을 수 있습니다. 그런 경우 게임을 끈 상태에서 `.minecraft/options.txt`의 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꿉니다. 통째로 덮어쓰면 개인 설정이 사라집니다.
- 조작 설정에서 사역마 단축키를 기본값으로 초기화하면 다시 `-1`이 저장되어 같은 오류가 납니다.

### 멀티플레이 서버 목록(servers.dat)

빌더는 멀티플레이 목록에 `Aziran` 서버(주소 `mc.aziran.uk`) 하나만 적은 압축하지 않은 NBT `servers.dat`를 세 아카이브에 담습니다(`.mrpack`의 `client-overrides/servers.dat`, 수동 ZIP의 `servers.dat`, MultiMC ZIP의 `.minecraft/servers.dat`). 새 인스턴스는 멀티플레이 화면에 이 서버가 이미 들어 있습니다.

- 이미 만든 인스턴스나 게임 디렉터리의 서버 목록은 소급해서 바뀌지 않습니다. 기존 인스턴스에서는 `mc.aziran.uk`를 직접 추가합니다.
- 수동 설치 때 게임 디렉터리에 `servers.dat`가 **없을 때만** 복사합니다. 이미 있으면 덮어쓰지 않습니다. 덮어쓰면 저장해 둔 다른 서버 목록이 사라집니다.
- 이 파일은 `1.1.5`부터 들어 있습니다. 이미 공개한 GitHub Release `client-1.1.4`의 파일에는 없습니다.

### 설치 시 주의

기존 인스턴스나 설치 디렉터리에 덮어쓰지 말고 **새 인스턴스로 가져옵니다.** 팩은 기존 `mods/`를 정리하지 않으므로 이전 인스턴스를 재사용하면 `xaerominimap-neoforge-26.3-26.5.3.jar` 같은 이전 JAR과 기존 `options.txt`가 남습니다.

빌더는 옛 구성을 실수로 다시 가져오는 일을 막기 위해 `dist/`에 **이번 버전의 MultiMC 인스턴스 ZIP만 남기고 이전 버전 인스턴스 ZIP은 데스크톱 휴지통으로 보냅니다.** 영구 삭제가 아니라 `gio trash`를 쓰므로 파일 관리자나 `gio trash --restore`로 되돌릴 수 있습니다. `gio`가 없거나 실패하면 빌드를 중단합니다. 이전 버전의 `.mrpack`과 수동 ZIP은 그대로 둡니다. **런처에 이미 가져와 둔 인스턴스는 영향을 받지 않습니다.**

MultiMC 인스턴스 ZIP의 인스턴스 이름은 `Aziran 26.3 Client 1.1.6`입니다. Minecraft `26.3`과 NeoForge `26.3.0.8-beta`는 `mmc-pack.json`의 컴포넌트로만 지정해 런처가 공식 메타데이터에서 내려받으므로 첫 실행에 인터넷 연결과 로그인한 계정이 필요합니다. Java `25` 경로는 `Edit Instance` → `Settings` → `Java`에서 직접 지정합니다.

클라이언트 전용 모드와 셰이더 팩의 고정 목록은 [mods-26.3-client-extra.lock.json](mods-26.3-client-extra.lock.json)이며, JAR·셰이더 팩·Iris 소스 번들은 Git에서 제외한 `client-mods-cache/`에 둡니다. 생성 파일은 `dist/`에 있으며 Git에는 포함하지 않습니다. `python3 scripts/build_client_pack.py`로 다시 생성합니다. 파일 무결성·의존성·아카이브 구성은 리눅스에서 검증했고, `1.1.4` 팩으로 새로 만든 인스턴스의 Windows 두 번 연속 실행 성공은 사용자 보고로 확인했습니다(서버 접속·셰이더 적용 여부는 그 보고에 없음). `1.1.5`는 `servers.dat` 구성만 파일 수준에서 검증했고, `1.1.6`은 세 아카이브의 Simple Tomb JAR이 서버 파일과 같은 SHA-512인지 파일 수준에서 검증했습니다. 두 버전 모두 게임 실행은 확인하지 않았습니다.

## 기존 참고 자료

- [구축 참고 글](https://velog.io/@windsekirun/Deploy-Minecraft-by-Docker)
- [기존 README 이미지](https://github.com/aziran07/AziranWebServer/assets/161091473/8bd8483b-b211-409e-ac08-e5d0f8c16f8d)

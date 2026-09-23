# Aziran Minecraft Server

Minecraft Java Edition 26.3 NeoForge 서버를 준비하며 웹 관리·모니터링 구성도 함께 관리합니다. 기존 1.21 데이터는 `server-data/`에, Fabric 준비 데이터는 `server-data-26.3/`에 보존하고, 현재 구성은 `server-data-26.3-neoforge/`를 사용합니다. 설치 모드와 준비 상태는 [모드 설치 안내](docs/MODS_26_3.md), 로더 결정 근거는 [로더 비교](docs/LOADER_COMPARISON_26_3.md)를 참고하세요.

게임 서버와 웹 관리·모니터링 서비스 구성은 Docker Compose로 관리합니다. 자체 게임 로직 소스는 없으며, 서비스 구성은 이 저장소에서, 게임 기능은 외부 모드와 로컬 서버 데이터에서 관리합니다.

접속 안내 웹사이트는 **https://aziran.uk**, 게임 서버 주소는 **`mc.aziran.uk`**입니다. 웹사이트에서 클라이언트 `.mrpack`을 다운로드하고 설치 순서를 확인할 수 있습니다. 웹사이트 소스와 배포 구성은 [웹사이트 운영 안내](docs/JOIN_GUIDE.md)를 참고하세요.

현재 Compose는 **Minecraft와 웹 RCON만 활성화**합니다. Portainer·Grafana·Prometheus·cAdvisor·Nginx는 주석 처리되어 있습니다. 웹 RCON은 Docker 내부에서만 접근하며 공개 웹사이트에는 관리 기능을 제공하지 않습니다.

## 작업 시작

1. [AGENTS.md](AGENTS.md): Codex/Claude 역할, Orca 협업 절차, 데이터 보호·검증 규칙.
2. [프로젝트 지도](docs/PROJECT_MAP.md): 기능별 구현 위치, 네트워크, 로컬 모드, 변경·검증 기준.
3. [CLAUDE.md](CLAUDE.md): Claude 구현 작업 시작 시 확인할 사항.

| 목적 | 먼저 볼 파일 |
| --- | --- |
| 게임 버전·메모리·난이도, 서비스 구성 | [docker-compose.yml](docker-compose.yml) |
| 도메인·HTTPS·관리 UI·WebSocket | [default.conf.template](nginx/templates/default.conf.template) |
| 게임 접속·지도 TCP 전달 | [minecraft.conf.template](nginx/templates/minecraft.conf.template) |
| 컨테이너 지표 수집 | [prometheus.yml](prometheus.yml) |
| 월드 백업·보존 기간 | [mc_backup.sh](mc_backup.sh) |
| 설치 모드·버전·해시 고정 | [mods-26.3.lock.json](mods-26.3.lock.json) |

## 실행 전 확인

- Docker와 Docker Compose 플러그인이 필요합니다.
- `.env`를 별도로 준비해야 합니다. 필요한 변수 이름은 프로젝트 지도에 있습니다. `nginx/cert.pem`, `nginx/key.pem`은 주석 처리된 기존 Nginx를 복원할 때만 필요합니다.
- 모드, 월드, Grafana 대시보드 등 영속 데이터는 Git에 포함되지 않습니다. 새 clone만으로 기존 운영 서버를 재현할 수 없습니다. 모드 JAR은 `mods-26.3.lock.json`의 URL과 해시로 다시 받을 수 있습니다. Fabric 준비 당시의 목록은 `mods-26.3-fabric-historical.lock.json`에 보존돼 있습니다.
- 활성 Compose 서비스는 호스트의 `25565` TCP 포트만 게시합니다. 안내 웹사이트는 GitHub Pages에서 HTTPS로 제공합니다.

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

게임 `25565`는 Minecraft 컨테이너가 직접 게시합니다. Nginx는 `80`·`443`·`8123`만 게시하므로 게임 접속에 Nginx를 거치지 않습니다.

백업 스크립트는 오래된 백업을 삭제하므로 검사용으로 실행하지 않습니다. 현재 동작과 확인된 제약은 프로젝트 지도를 참고하세요.

## 클라이언트 모드팩

현재 버전은 `1.1.3`이며 Minecraft `26.3`, NeoForge `26.3.0.8-beta`, Java `25`용 모드 16개로 구성했습니다. 서버와 공유하는 모드 13개는 서버와 같은 파일이고, ImmediatelyFast·Mouse Tweaks·JourneyMap 3개는 서버에 설치하지 않는 클라이언트 전용 모드입니다. `1.1.2`에 있던 Xaero's Minimap은 Windows 크래시 때문에 JourneyMap으로 교체했고, `1.1.0`에 있던 Sodium은 `1.1.1`부터 계속 뺀 상태입니다.

- 런처 가져오기(권장): [Modrinth 형식 팩](dist/aziran-26.3-client-1.1.3.mrpack)
- MultiMC 가져오기: [인스턴스 ZIP](dist/aziran-26.3-client-1.1.3-multimc.zip)
- 수동 설치: [모드 ZIP](dist/aziran-26.3-client-1.1.3-manual.zip)
- [설치 안내](dist/README.md), [고정 목록](mods-26.3-client.lock.json)
- [클라이언트 모드 호환성 검토](docs/CLIENT_MOD_COMPATIBILITY_26_3.md)

### 먼저 읽을 것: JourneyMap은 ZIP 두 개에 들어 있지 않습니다

**JourneyMap JAR은 수동 ZIP과 MultiMC 인스턴스 ZIP에 담겨 있지 않습니다.** [공식 라이선스](https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/)가 JAR을 모드팩에 담거나 재호스팅하는 것을 금지하고, 모드팩은 설치·실행 과정에서 CurseForge 또는 Modrinth에서 직접 내려받을 때만 허용하기 때문입니다. 빠뜨린 것이 아니라 라이선스를 지키려고 뺀 것입니다.

- **`.mrpack`을 쓰는 쪽을 권합니다.** 런처가 설치 중에 Modrinth에서 JourneyMap을 직접 받으므로 라이선스 조건을 만족하면서 모드 16개가 모두 갖춰집니다. MultiMC도 `Add Instance` → `Import from zip`에서 `.mrpack`을 가져올 수 있습니다([MultiMC 위키](https://github.com/MultiMC/Launcher/wiki/Import-Instance)가 가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있습니다. 최소 버전은 명시돼 있지 않고, 실제 가져오기를 시험해 보지는 않았습니다).
- ZIP 두 개를 쓰면 모드 15개만 설치됩니다. 남은 JourneyMap은 [Modrinth 프로젝트](https://modrinth.com/mod/journeymap)나 CurseForge 공식 페이지에서 `journeymap-neoforge-26.3-6.0.9.jar`(4352830바이트, SHA-1 `e4d81a338a2997d6d517d5f7b51b607277f21733`)를 직접 받아 `mods/`에 넣습니다. 팩 안 `README.md`가 SHA-512까지 포함한 절차를 안내합니다.

### 1.1.3: Xaero's Minimap을 JourneyMap으로 교체

16개를 모두 켠 `1.1.2`가 Windows에서 네이티브 종료 코드 `0xc0000005`(액세스 위반)로 크래시했습니다. 같은 인스턴스에서 `xaerominimap-neoforge-26.3-26.5.3.jar` **하나만** 비활성화하면 정상 실행됐고, `1.1.1`과 `1.1.2`의 최상위 모드 JAR 차이도 이 파일 하나뿐이었습니다(나머지 15개는 SHA-512까지 동일). 따라서 그 모드·드라이버·런타임 조합에서 크래시의 방아쇠는 Xaero's Minimap으로 확인됐습니다.

다만 **왜** 네이티브 액세스 위반까지 갔는지는 모릅니다. 모드 자체의 결함인지, 그 PC의 그래픽 드라이버·GPU와의 조합인지, NeoForge 26.3 베타나 다른 모드와의 상호작용인지 구분하지 않았습니다. 이 모드가 다른 환경에서도 같은 문제를 일으킨다는 뜻이 아니며, 다른 버전의 Xaero's Minimap도 시험하지 않았습니다.

미니맵 기능은 계속 필요하므로 같은 자리에 [JourneyMap](https://modrinth.com/mod/journeymap) `26.3-6.0.9+neoforge`를 넣었습니다. Modrinth 표시가 `client_side=optional`, `server_side=optional`이고 지도 표시와 웨이포인트는 클라이언트만으로 동작하므로, **서버에는 설치하지 않았고 서버 구성도 바꾸지 않았습니다.**

**`1.1.3`이 Windows에서 실행되는지, 서버에 접속되는지는 아직 확인하지 않았습니다.** JourneyMap이 `1.1.2`의 크래시를 해결한다는 확인도 없습니다. 실행과 서버 접속이 함께 확인된 유일한 구성은 여전히 Sodium을 꺼 둔 `1.1.0` 인스턴스입니다.

### Sodium 제외 유지

`1.1.0` 인스턴스에서 Sodium JAR만 비활성화한 뒤 Windows MultiMC가 정상 실행되고 서버 접속까지 된다는 사용자 확인을 받았습니다. 그래서 `1.1.1`부터 `1.1.3`까지 Sodium을 넣지 않습니다.

다만 크래시 로그에 남아 있던 네이티브 종료 코드 `0xc0000409`의 정확한 원인은 확정하지 못했습니다. 로그에는 Sodium의 Nvidia 드라이버 워크어라운드가 `IllegalStateException: Command line is already modified`로 실패한 기록이 있었지만, 그 예외가 종료의 직접 원인인지 드라이버·런처·다른 요소와의 조합이 관여했는지는 알 수 없습니다. 확인된 사실은 "Sodium이 없으면 이 PC에서 실행·접속된다"까지입니다. Sodium이 빠졌으므로 `1.1.0`에서 기대하던 렌더링 성능 향상은 없습니다.

### 설치 시 주의

기존 인스턴스나 설치 디렉터리에 덮어쓰지 말고 **새 인스턴스로 가져옵니다.** 팩은 기존 `mods/`를 정리하지 않으므로 이전 인스턴스를 재사용하면 `sodium-neoforge-0.9.2+mc26.3.jar`나 `xaerominimap-neoforge-26.3-26.5.3.jar`가 남아 이번 구성과 달라집니다. 수동 설치라면 그 JAR들을 먼저 지웁니다.

빌더는 옛 구성을 실수로 다시 가져오는 일을 막기 위해 `dist/`에 **이번 버전의 MultiMC 인스턴스 ZIP만 남기고 이전 버전 인스턴스 ZIP은 데스크톱 휴지통으로 보냅니다.** 영구 삭제가 아니라 `gio trash`를 쓰므로 파일 관리자나 `gio trash --restore`로 되돌릴 수 있고, 휴지통에 원래 경로가 함께 기록됩니다. `gio`가 없거나 실패하면 조용히 넘어가지 않고 빌드를 중단합니다. 이전 버전의 `.mrpack`과 수동 ZIP은 그대로 둡니다. 이 정리는 `dist/`의 설치용 파일에만 해당하며, **런처에 이미 가져와 둔 인스턴스는 별개 파일이라 영향을 받지 않습니다.** Sodium을 꺼 두고 쓰던 `1.1.0` 인스턴스는 MultiMC에 그대로 남아 있으므로 되돌아갈 곳으로 남겨 둡니다.

MultiMC 인스턴스 ZIP을 쓴다면 가져온 인스턴스 이름은 `Aziran 26.3 Client 1.1.3`이라 이전 인스턴스와 목록에서 구분됩니다. 모드 JAR 15개는 팩 안에 들어 있고, Minecraft `26.3`과 NeoForge `26.3.0.8-beta`는 `mmc-pack.json`의 컴포넌트로만 지정해 런처가 공식 메타데이터에서 내려받습니다. 따라서 첫 실행에 인터넷 연결과 로그인한 Minecraft 계정이 필요합니다. Java `25` 경로는 팩에 넣지 않았으므로 `Edit Instance` → `Settings` → `Java`에서 직접 지정합니다.

클라이언트 전용 모드의 고정 목록은 [mods-26.3-client-extra.lock.json](mods-26.3-client-extra.lock.json)이며, JAR은 Git에서 제외한 `client-mods-cache/`에 둡니다. 생성 파일은 `dist/`에 있으며 Git에는 포함하지 않습니다. 서버 모드 파일과 클라이언트 캐시가 준비된 환경에서 `python3 scripts/build_client_pack.py`로 다시 생성할 수 있습니다. 파일 무결성과 의존성을 검증했으며 `1.1.3` 구성으로 실제 클라이언트 실행·접속은 확인하지 않았습니다. MultiMC 인스턴스 ZIP도 아카이브 구조와 컴포넌트 UID·버전을 파일 수준에서만 확인했고, 런처로 실제 가져오기나 실행을 해 보지 않았습니다.

## 기존 참고 자료

- [구축 참고 글](https://velog.io/@windsekirun/Deploy-Minecraft-by-Docker)
- [기존 README 이미지](https://github.com/aziran07/AziranWebServer/assets/161091473/8bd8483b-b211-409e-ac08-e5d0f8c16f8d)

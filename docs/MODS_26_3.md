# Minecraft 26.3 모드 구성 (NeoForge)

현재 상태(2026-09-22): 설치 이후 사용자 요청으로 서버를 기동했다. `aziran-minecraft-26-3`은 healthy·재시작 0회이며 호스트 25565의 Minecraft 상태 조회와 RCON을 Codex가 독립 확인했다. Structures와 Towns and Towers의 구조물 위치 탐색도 성공했다. 아래 미기동 표현은 설치 당시 기록이며 최신 실행 결과와 남은 경고는 [최초 기동 결과](SERVER_26_3_PREPARATION.md#최초-기동-결과-2026-09-22)를 참고한다. Chunky 프리젠은 목표 반경의 1/10까지 완료했다(오버월드 원형 반경 800, 네더 원형 반경 100, 엔드 미실행). 현황과 최종 목표는 [Chunky 청크 프리젠 현황](CHUNK_PREGEN.md)에 기록한다. 실제 플레이 검증은 아직 하지 않았다.

2026-09-22 사용자 결정에 따라 로더를 NeoForge로 전환하고 베타 배포 사용을 허용했다. Occultism, 비공식 NeoForge 이식판 Farmer's Delight, 추가 요청된 Structures를 포함한다. 신규 모드는 `server-data-26.3-neoforge/mods/`에 설치했다. 기존 1.21 `server-data/`와 Fabric 준비용 `server-data-26.3/`은 건드리지 않았다. 서버를 시작하거나 월드를 생성하지 않았다.

## 서버 구성

| 항목 | 고정 값 | 근거 |
| --- | --- | --- |
| Minecraft | `26.3` | Compose `VERSION` |
| 로더 | `NEOFORGE` | Compose `TYPE` |
| NeoForge | `26.3.0.8-beta` | [NeoForged Maven 메타데이터](https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml)의 26.3 계열 최신 버전 |
| 이미지 | `itzg/minecraft-server:java25-alpine` | 26.x의 Java 25 요구사항 |
| 데이터 경로 | `./server-data-26.3-neoforge:/data` | 기존 경로와 분리 |

26.3 계열 NeoForge는 현재 `26.3.0.0-beta` ~ `26.3.0.8-beta`만 배포된다. itzg 이미지의 `NEOFORGE_VERSION` 기본값은 "요청한 Minecraft 버전의 최신 non-beta"이므로 26.3에서는 해결되지 않는다. 따라서 정확한 버전을 명시적으로 고정했다. itzg 문서의 `TYPE=NEOFORGE` + `VERSION` + `NEOFORGE_VERSION` 조합과, 설치 스크립트가 호출하는 `mc-image-helper install-neoforge`의 버전 해석 코드에서 26.x의 4자리 연도 기반 버전 체계(`isYearBased`, 예: `26.1.0.15-beta`)를 처리한다는 점을 확인했다. 지정한 설치 파일 `neoforge-26.3.0.8-beta-installer.jar`가 Maven에 존재하는 것도 확인했다(HTTP 200, 3690990 바이트).

버전 해석 코드는 특정 버전을 지정하면 beta 접미사를 무시하고 숫자 네 자리로 대조한다. 이 고정 값은 실제 다운로드까지 확인한 것이 아니라 메타데이터와 아티팩트 존재만 확인한 값이다.

## 설치 명세

현재 lock은 서버 전용 Curios 배낭 패치까지 포함해 25개다. 최초 설치 20개에 BlueMap `5.27-neoforge`를 2026-09-24, SableCraft Standards `1.10.0+mc26.3`과 Simple Tomb `1.9.0`을 2026-09-25 추가했다. 같은 날 Modonomicon을 `2.6.0`에서 `2.7.0`으로 교체했고, Traveler's Backpack `11.4.0`을 추가했다(아래 절). 2026-09-26에는 원본 24개 JAR을 유지하고 Curios 배낭 패치를 더했다. Simple Tomb은 `client-1.1.6` 공개 뒤 서버를 재시작해 활성화했다(아래 절)([BlueMap 배포 안내](BLUEMAP.md)). 아래 설치 검증 기록은 최초 20개 기준이다. 배포 채널, 다운로드 URL 또는 로컬 소스·빌드 명령, 파일 크기, SHA-1/SHA-512, 선언된 모드 ID, 필수 의존성 범위, 내부 번들 JAR은 [mods-26.3.lock.json](../mods-26.3.lock.json)에 기록한다.

### Traveler's Backpack 추가 (2026-09-25)

**2026-09-26 후속 조사:** Curios 착용 상태에서 배낭을 닫았다 열면 내용물이
사라지는 결함을 사용자가 재현했다. 설치된 JAR의 복사본 반환·저장 경로를
확인했으며 처음에는 월드 보호 백업 후 `backSlotIntegration=false`로 자체 착용을 적용했다.
이후 사용자 요청에 따라 서버 전용 `Aziran Backpack Curios Persistence 1.0.0`을
만들어 Curios Back 슬롯 저장 경로를 수정했다. 원본 모드 JAR은 유지하며
`backSlotIntegration=true`로 연동한다. 설치 대상은 기존 24개와 패치 1개다.
소스와 재현 빌드는 [compat/backpack-curios](../compat/backpack-curios/README.md),
버전 고정·설계 제약은 [패치 설계](BACKPACK_CURIOS_FIX_DESIGN.md)에 있다.
최초 서버 배포 때는 패치를 클라이언트 빌더에서 제외했다. 이후 사용자 요청으로
클라이언트 1.1.12에는 동일한 패치 JAR을 포함한다. 서버 로직을 고치는 모드이며
멀티플레이 클라이언트 설치는 선택 사항이다. 싱글플레이의 통합 서버에서 사용할
목적으로 포함하지만, 사용자 지시에 따라 추가 게임 실행 검증은 하지 않는다.
전체 운영 모드 구성을 넣은 임시 서버에서 Codex가 17개 회귀 검사를 통과시켰다.
[원인·설정·실제 검증 상태](BACKPACK_PERSISTENCE.md)를 참고한다.
아래 기본 설정과 미검증 표시는 2026-09-25 최초 설치 당시의 기록이다.

사용자 요청으로 배낭 모드 [Traveler's Backpack](https://modrinth.com/mod/travelersbackpack)(Modrinth 프로젝트 `rlloIFEV`, 버전 `Gdy0zkAN` `26.3-11.4.0`, 2026-09-24 공개, `travelersbackpack-neoforge-26.3-11.4.0.jar`, 1475945바이트, SHA-512 `0ec5ad7a…5f0fce1`)을 lock에 더해 24개가 됐다. CurseForge 프로젝트(`travelers-backpack`)와 같은 제작자(Tiviacz1337)의 공식 Modrinth 배포 파일이며 수정하지 않았다. Modrinth 메타데이터는 NeoForge, `26.3`, `client_and_server`(서버·클라이언트 모두 required)이다.

호환성·의존성: JAR의 `neoforge.mods.toml`은 모드 ID `travelersbackpack` `11.4.0`, 필수 의존성 Minecraft `[26.3]`·NeoForge `[26.3.0.1-beta,)`만 선언하고 JarJar 번들 JAR이 없다. 현재 NeoForge `26.3.0.8-beta`가 범위를 충족하며 추가 필수 라이브러리는 없다. Modrinth의 선택 의존성(Curios, JEI 등) 중 Curios `17.0.0-beta+26.3`과 JEI `31.4.0.21`은 이미 설치되어 있고, 다른 선택 모드는 더하지 않았다. JAR에 `assets/travelersbackpack/lang/ko_kr.json`이 있다. 라이선스는 Modrinth 메타데이터의 LGPL-3.0-only(JAR은 `GNU LESSER GENERAL PUBLIC LICENSE`로 표기)이고, 제작자 프로젝트 설명이 "You are allowed to use this mod in public/private modpacks."라고 모드팩 사용을 허락한다. 소스는 https://github.com/Tiviacz1337/Travelers-Backpack 이다.

설정 기본값(26.3 JAR 바이트코드와 상류 26.1 소스로 확인): `backSlotIntegration=true`(Curios가 설치된 이 서버에서는 배낭을 Curios의 Back 슬롯에만 착용), `backpackDeathPlace=true`(죽을 때 멘 배낭을 그 자리에 블록으로 놓음), `backpackForceDeathPlace=false`. **Simple Tomb 무덤과의 사망 처리, Curios 착용은 게임에서 확인하지 않았다.** 이전 기동 로그에 Occultism의 Curios 통합 대체(`Failed to initialize Curios integration`) 경고가 있으나 Traveler's Backpack의 Curios 연동과는 별개이며 이 연동도 확인하지 않았다.

2026-09-25 운영 서버에 설치했다. 초안 릴리스 `client-1.1.9`의 6개 자산 검증 뒤 사용자가 요청한 즉시 재시작으로 진행했고, 접속자는 0명이었다. 서버 기동을 확인한 뒤 Codex가 [`client-1.1.9`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.9)를 일반 릴리스(latest)로 공개했다.

| 단계 | 시각(UTC) | 결과 |
| --- | --- | --- |
| 사전 확인 | 13:43 | `StopTimeout=660`, `STOP_DURATION=600`, healthy·재시작 0회, `world/` 11GB, 여유 1.1TB, 접속자 0명, 설치할 JAR의 크기 1475945바이트·SHA-512 확인 |
| 정상 종료 3-B | 13:44:53 → 13:44:54 | RCON 재시작 공지 후 `docker compose stop minecraft` 종료 상태 0, `exited exit=0 oom=false`, `Stopping server` → `Saving players` → `Saving worlds` → 세 차원 `Saving chunks for level` → 러너 `Done`, 저장 오류 없음 |
| 월드 보호 백업 | 13:45:04 → 13:45:31 | [오프라인 월드 보호 백업](BACKUPS.md#오프라인-월드-보호-백업) 절차로 `server-data-26.3-neoforge/world/`만 묶었다. `/home/pilon1945/aziran-26.3-protected-backups/pre-travelersbackpack-world-2026-09-25-134504.tar`(11450746880바이트, SHA-256 `80bd0722c6444f9a54c0b76acc6c7a5f98a1301049ba72f1f8e11893e6ff4830`). 목록 3830개 항목이 모두 `world/` 아래이고 `level.dat`와 세 차원 `region/` 4개 필수 항목이 있다. `BACKUP VERIFIED`, 종료 상태 0, 파일 `600`·디렉터리 `700`. 모드·설정·BlueMap은 백업하지 않았고 다른 백업은 건드리지 않았다 |
| JAR 설치 | 13:45:39 | 공식 JAR을 `mods/travelersbackpack-neoforge-26.3-11.4.0.jar`로 다른 JAR과 같은 소유자·권한(`pilon1945`, `664`)으로 설치. `mods/` 24개 파일이 모두 lock의 SHA-512와 일치, 기존 23개 SHA-256 설치 전후 동일 |
| 기동 | 13:45:43 → 13:45:59 | `docker compose start minecraft` 종료 상태 0, 13:45:57 `Done (0.533s)`, RCON 기동, `running healthy` 재시작 0회, `rcon-cli list` 응답(0명) |

기동 로그의 모드 목록에 `Traveler's Backpack 11.4.0 (travelersbackpack)`(`mods/travelersbackpack-neoforge-26.3-11.4.0.jar`)과 `Modonomicon 2.7.0`이 있다. 13:18 UTC 기동과 비교해 새 경고·오류는 없고, 그때의 Modonomicon 버전 차이 알림은 사라졌다. 남은 경고는 모두 이전부터 있던 것이다: 모드 refmap 3건, udev, Occultism의 Curios 통합 대체(`Failed to initialize Curios integration`와 `ClassNotFoundException: ...CuriosIntegrationImpl`), `apothic_enchanting` 데이터 맵, log4j `DebugFile` 부록의 `io.netty.channel.kqueue.Native` 예외. 처음 기동하며 만든 `config/travelersbackpack-server.toml`은 `backSlotIntegration = true`, `backpackDeathPlace = true`, `backpackForceDeathPlace = false`이고 `travelersbackpack-common.toml`은 `enableLoot = true`, `enableVillagerTrade = true`다. 설정은 수정하지 않았다.

설치 뒤 Python 검사 69개(`tests/test_travelers_backpack_deployment.py` 서버 검사 포함)와 JavaScript 검사 2개가 통과했고, Codex가 서버 상태·JAR 해시·백업 목록·검사를 따로 확인했다. **배낭 화면, Curios Back 슬롯 착용, `Y` 단축키, Simple Tomb과의 사망 처리, 1.1.8 이하 클라이언트의 접속 거부는 게임에서 확인하지 않았다.** 롤백이 필요하면 서버를 정상 종료한 뒤 이 JAR을 빼고 lock을 이전 커밋으로 되돌린다. 배낭 모드가 월드에 남긴 블록·아이템 데이터 때문에 되돌릴 월드가 필요하면 위 월드 백업으로 [보호 월드 백업 복원](BACKUPS.md#보호-월드-백업-복원)을 판단한다.

### Modonomicon 2.7.0 교체 (2026-09-25)

lock의 Modonomicon을 `26.3-2.6.0`(`CPBu0enR`)에서 공식 Modrinth 버전 `SFKjMnCe` `26.3-2.7.0`(`modonomicon-26.3-neoforge-2.7.0.jar`, 2987945바이트, SHA-512 `7d16cb18…904d70e`)으로 바꿨다. Minecraft 26.3부터 마우스 버튼 번호가 SDL 기준(왼쪽 = 1)이라 2.6.0의 `BookCategoryNodeScreen.mouseDragged`가 `event.button() != 0` 비교로 왼쪽 끌기를 거부해 책 노드 화면을 움직일 수 없었다. 2.7.0은 이를 `InputConstants.MOUSE_BUTTON_LEFT` 비교로 고친 상류 커밋 [`d74b6f2dbba9956182f11808f82e1a22911cb5ee`](https://github.com/klikli-dev/modonomicon/commit/d74b6f2dbba9956182f11808f82e1a22911cb5ee)를 담는다(2.7.0 변경 기록에 포함). **게임 화면에서 끌기가 고쳐졌는지는 확인하지 않았다.**

받은 JAR의 크기·SHA-512는 Modrinth 메타데이터와 일치한다. `neoforge.mods.toml`은 모드 ID `modonomicon`, 선언 버전 `2.7.0`, 필수 의존성 NeoForge `[26.3.0.3-beta,)`, 선택 의존성 JEI·Patchouli로 2.6.0과 같고, JarJar의 commonmark 0.30.0 JAR 3개도 크기·SHA-512가 2.6.0과 같다. Occultism의 요구 `[2.5.0,)`를 충족한다.

`client-1.1.8`([사전 릴리스](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.8)) 공개와 Codex의 자산 크기·SHA-256 검증 뒤 운영 서버에 적용했다. 유일한 접속자였던 사용자가 즉시 재시작을 요청해 시간차 공지 없이 RCON으로 재시작 공지만 보냈다.

| 단계 | 시각(UTC) | 결과 |
| --- | --- | --- |
| 사전 확인 | 13:12 | `StopTimeout=660`, `STOP_DURATION=600`, healthy·재시작 0회, 데이터 34GB, 여유 1.1TB, 접속자 1명(사용자) |
| 정상 종료 3-B | 13:13:40 → 13:13:42 | `docker compose stop minecraft` 종료 상태 0, `exited exit=0 oom=false`, `Stopping server` → `Saving players` → `Saving worlds` → 세 차원 `Saving chunks for level` → 러너 `Done`, 저장 오류 없음 |
| 보호 백업 | 13:13:51 → 13:18:23 | 당시 문서 절차대로 데이터 디렉터리 **전체** tar(`pre-modonomicon-2.7-2026-09-25-131351.tar`, 35616133120바이트, `.list`·`.sha256` 포함)를 만들고 `BACKUP VERIFIED`를 확인했다. 사용자가 월드만 백업하도록 정하고 이 전체 백업의 삭제를 지시해 **13:23:21에 tar·`.list`·`.sha256`을 영구 삭제했다.** 이 배포의 보호 백업은 남아 있지 않으며 이 백업으로는 복원할 수 없다. 종료 직전의 월드 사본은 정기 백업 `minecraft_backups/26.3-world-20260925-123013.tar`(12:30:13 생성)가 가장 가깝다 |
| JAR 교체 | 13:18:41 | 2.6.0 JAR을 `/home/pilon1945/aziran-26.3-protected-backups/modonomicon-26.3-neoforge-2.6.0.jar.pre-modonomicon-2.7`로 옮겼다(SHA-512 lock 기록과 일치). 월드만 백업하는 사용자 방침이 정해지기 전에 한 조치이며, 이후 배포에서는 모드 JAR 사본을 만들지 않는다. 2.7.0을 이전 파일과 같은 소유자·권한(`pilon1945`, `664`)으로 설치. `mods/` JAR 23개가 모두 lock의 SHA-512와 일치, 2.6.0 없음, 나머지 22개 SHA-256 교체 전후 동일 |
| 기동 | 13:18:47 → 13:19:06 | `docker compose start minecraft` 종료 상태 0, 13:19:02 `Done (0.594s)`, RCON 기동, `running healthy` 재시작 0회, `rcon-cli list` 응답(0명) |

기동 로그의 모드 목록에 `modonomicon (jar(mods/modonomicon-26.3-neoforge-2.7.0.jar))`와 `Modonomicon 2.7.0`이 있고, commonmark JarJar 3개도 2.7.0 JAR에서 읽었다. 이전 기동(05:37 UTC)과 비교해 새로 생긴 경고는 NeoForge `CommonHooks`의 `modonomicon (version 2.6.0 -> 2.7.0)` 버전 차이 알림 하나다. 월드에 기록된 모드 버전과 달라서 나오는 알림으로 교체에 따른 예상 결과다. 기존 경고(모드 refmap, udev, Occultism의 Curios 통합 대체, `apothic_enchanting` 데이터 맵, log4j `DebugFile` 부록의 `io.netty.channel.kqueue.Native` 예외)는 이전 기동에도 있었다. 이전 기동 로그의 Modonomicon 레시피 경고(`null recipe book category`, 레시피 3개 `not found`)는 이번 기동 직후에는 아직 나오지 않았고 플레이어 접속 등으로 책을 불러올 때 다시 나올 수 있다. 월드·청크 로드 오류는 없었다. `chunky-idle-pregen` 컨테이너는 이번 작업 전(2일 전)에 이미 정상 종료(`Exited (0)`)한 상태라 재연결 대상이 아니었고, 웹 RCON `rcon` 컨테이너는 계속 실행 중이다.

교체 뒤 `tests/test_modonomicon_update.py`를 포함한 관련 검사 34개와 전체 Python 검사 67개, JavaScript 검사 2개가 통과했다. **책 화면 끌기 수정과 1.1.8 클라이언트 접속은 게임에서 확인하지 않았다.** 1.1.7 이하 클라이언트가 2.7.0 서버에 접속되는지도 확인하지 않았다. 롤백이 필요하면 서버를 정상 종료한 뒤 2.7.0 JAR을 빼고, 이전 lock(커밋 `464e9ae`)에 고정된 공식 Modrinth URL `https://cdn.modrinth.com/data/692GClaE/versions/CPBu0enR/modonomicon-26.3-neoforge-2.6.0.jar`에서 2.6.0을 다시 받아 크기 2973738바이트·SHA-512를 확인해 설치하고 lock을 되돌린다. 월드 복원이 필요하면 [월드 백업](BACKUPS.md#월드-복원-시-주의)을 쓴다. 이 배포의 전체 백업은 삭제되어 복원에 쓸 수 없다.

### SableCraft Standards 명령 설정 (2026-09-25)

`standards-1.10.0+mc26.3.jar`는 서버에만 설치했다. `config/standards-common.toml`에서 명령군 `homes`, `back`, `tpa`, `spawn`만 켰고 `warps`, `top`, `economy`를 포함한 나머지 명령군은 껐다. `/home`, `/sethome`, `/homes`, `/delhome`, `/back`, `/tpa`, `/spawn`은 일반 유저에게 기본 허용된다. 사망 지점 `/back`은 `commands.backOnDeathAccess = "everyone"`와 `teleport.backOnDeath = true`로 허용했다. 관리자용 `/setspawn` 등은 일반 유저에게 열지 않았다. 모드가 항상 등록하는 `/actions`, `/perm`, `/rank`, `/standards`는 명령군 설정으로 끌 수 없으며 관리자 기능은 별도 권한을 요구한다.

설치 전 접속자는 0명이었다. 전체 데이터 백업은 사용자 요청에 따라 실행하지 않았다. 정상 종료 후 JAR과 설정을 설치하고 서버를 시작했으며, 컨테이너는 `healthy`, 재시작 0회였다. 설치된 22개 JAR 모두 lock의 SHA-512와 일치했다. RCON 도움말에서 `/home`과 `/back`을 확인하고 `/warp`, `/top`은 등록되지 않은 것을 확인했다. 일반 유저가 직접 사용하거나 사망 지점으로 복귀하는 실제 플레이 검증은 아직 하지 않았다.

### Simple Tomb 설치 (2026-09-25)

사망 시 소지품을 담은 무덤 블록을 만드는 Simple Tomb `1.9.0`(CurseForge 프로젝트 `399669`, 파일 `8925463`, `simpletomb-26.3-1.9.0.jar`)을 lock에 고정하고 `mods/`에 넣었다. 공식 CDN(`mediafilez.forgecdn.net`)에서 받은 파일의 크기 285662바이트와 SHA-512가 CurseForge 보고 크기·지정 해시와 일치한 뒤에만 설치했다. JAR의 `neoforge.mods.toml`은 모드 ID `simpletomb`, 필수 의존성 NeoForge `[26.2.0.0-alpha,)`·Minecraft `[26.2,)`를 선언하며 현재 `26.3.0.8-beta`·`26.3`이 이를 만족한다. 라이선스는 JAR 메타데이터 `LGPL2`, 제작자 GitHub 저장소 LGPL-2.1이다.

무덤 블록과 열쇠 아이템을 등록하는 모드라 클라이언트에도 같은 파일이 필요하다. 그래서 클라이언트 팩을 `1.1.6`으로 올려 같은 JAR을 담았다(아래 클라이언트 모드팩 절). 서버가 이 모드를 로드한 뒤에는 이 모드가 없는 `1.1.5` 이하 클라이언트가 접속할 수 없으므로, GitHub 사전 릴리스 `client-1.1.6` 공개와 접속 안내 사이트 배포를 확인한 뒤에 재시작했다. 설치 시점의 최신 정기 월드 백업은 `26.3-world-20260925-043011.tar`이며 tar 목록을 읽을 수 있고 `level.dat`를 포함함을 확인했다.

2026-09-25 05:30 UTC 정기 백업 `26.3-world-20260925-053014.tar`(`world/level.dat` 포함 확인) 뒤, 접속자 0명 상태에서 15분·5분·1분 전 공지를 하고 [정상 종료 절차](BACKUPS.md#오프라인-월드-보호-백업) 3-B(`StopTimeout=660`, `STOP_DURATION=600`)로 `docker compose stop minecraft`를 실행했다. 종료 상태 0, `exited exit=0 oom=false`, 세 차원의 `Saving chunks for level`과 러너 `Done`을 확인한 뒤 `docker compose start minecraft`로 기동했다. 기동 로그에 `Simple Tombstone 26.3-1.9.0 (simpletomb)`와 `mods/simpletomb-26.3-1.9.0.jar`가 나왔고 `Done`까지 도달했으며, 컨테이너는 `healthy`, 재시작 0회였다. 기동 로그의 Occultism `CuriosIntegrationImpl` `ClassNotFoundException`과 log4j `DebugFile` 어펜더의 netty `kqueue.Native` 오류는 변경 전 기동에도 있던 기존 로그다. 무덤 생성·회수 실제 플레이는 아직 확인하지 않았다.

### 사용자가 지정한 모드

| 모드 | 고정 버전 | 채널 | 출처 |
| --- | --- | --- | --- |
| [Occultism](https://modrinth.com/mod/occultism) | 26.3-neoforge-1.256.0 | 정식 | Modrinth |
| [Farmer's Delight 26 Neo Ver](https://www.curseforge.com/minecraft/mc-mods/farmers-delight-26-neo-ver) | 26.3-1.3.3-fix4 | 베타 | CurseForge |
| [Chunky](https://modrinth.com/mod/chunky) | 1.5.4 | 정식 | Modrinth |
| [Structures](https://www.curseforge.com/minecraft/mc-mods/structures-modd) | 4.1 | 정식 | CurseForge |

Farmer's Delight는 원본 프로젝트에 26.3 배포가 없다. 설치한 파일은 vectorwing의 1.21.1-1.3.3을 기반으로 한 비공식 NeoForge 이식판이며, 제작자가 CurseForge에 게시한 아티팩트를 CurseForge 공식 CDN(`edge.forgecdn.net`, 파일 ID `8928319`)에서 받았다. 소스에서 직접 빌드하거나 URL을 추정하지 않았다. 모드 ID는 원본과 같은 `farmersdelight`다.

Structures(GaraKrral, 프로젝트 ID `1391238`, 파일 ID `8849254`, `Structures v4.1.jar`)도 같은 방식으로 CurseForge 공식 CDN에서 받았다. 정식 배포이며 CurseForge 배포 메타데이터가 NeoForge와 `26.3`을 명시한다. 선언된 필수 의존성은 `neoforge [21.0.0,)`와 `minecraft [1.20,)`뿐이고, CurseForge가 표시한 관계 모드 3개는 모두 선택 사항이라 추가 설치하지 않았다. 모드 ID는 `structures`다.

이 JAR은 데이터팩을 모드로 포장한 다중 로더 파일이다(`neoforge.mods.toml`, `mods.toml`, `fabric.mod.json` 동시 포함). 구버전 경로(`loot_tables/`, `structures/`)와 신버전 경로(`loot_table/`, `structure/`)를 함께 담고 있으며, `pack.mcmeta`의 `pack_format`은 오래된 값 `48`이다. 배포처의 26.3 지원 표시와 별개로 실제 로딩과 구조물 생성은 검증하지 않았다. 선언 버전 범위(`minecraft [1.20,)`)도 매우 넓다. Towns and Towers와의 구조물 배치 중첩 및 생성 밀도도 월드 생성 시 확인해야 한다.

### Occultism 의존성

| 모드 | 고정 버전 | 채널 | 비고 |
| --- | --- | --- | --- |
| [Modonomicon](https://modrinth.com/mod/modonomicon) | 26.3-2.7.0 | 정식 | Occultism 요구 `[2.5.0,)` 충족. 2026-09-25 2.6.0에서 교체(위 절) |
| [GeckoLib](https://modrinth.com/mod/geckolib) | 5.5.7 | 정식 | Occultism 요구 `[5.5.6,)` 충족. 자체적으로 NeoForge `[26.3.0.7-beta,)` 요구 |
| [Curios API](https://modrinth.com/mod/curios) | 17.0.0-beta+26.3 | 베타 | 아래 제한 사항 참고 |

Occultism JAR은 `codedefinedgui 1.13.0`과 `magicparticleslib 1.8.0`을 JarJar로 내장하므로 별도 설치가 필요 없다.

### 기존 구성에서 복원한 모드

| 모드 | 고정 버전 | 채널 | 역할 |
| --- | --- | --- | --- |
| [Clumps](https://modrinth.com/mod/clumps) | 26.3.2 | 정식 | 경험치 오브 병합 |
| [Jade](https://modrinth.com/mod/jade) | 26.3.1+neoforge | 정식 | 블록·엔티티 정보 표시 |
| [Let Me Despawn](https://modrinth.com/mod/lmd) | 1.26.9.2 | 정식 | 몹 디스폰 정리 |
| [Almanac](https://modrinth.com/mod/almanac) | 1.26.9.1 | 정식 | Let Me Despawn 필수 의존성 |
| [Lithium](https://modrinth.com/mod/lithium) | mc26.3-0.26.1-neoforge | 정식 | 서버 틱 최적화 |
| [Packet Fixer](https://modrinth.com/mod/packet-fixer) | 3.3.7 | 정식 | 대용량 패킷 처리 |
| [spark](https://modrinth.com/mod/spark) | 1.10.187-neoforge | 정식 | 프로파일링 |
| [Tom's Simple Storage](https://modrinth.com/mod/toms-storage) | 26.3-2.12.0 | 정식 | 저장 시스템 |
| [Cooking for Blockheads](https://modrinth.com/mod/cooking-for-blockheads) | 26.3.0.1+neoforge-26.3 | 정식 | 주방·요리 편의 |
| [Balm](https://modrinth.com/mod/balm) | 26.3.0.1+neoforge-26.3 | 정식 | Cooking for Blockheads 필수 의존성 |
| [Towns and Towers](https://modrinth.com/datapack/towns-and-towers) | 1.13.12 | 정식 | 마을·구조물 |
| [Cristel Lib](https://modrinth.com/mod/cristel-lib) | neoforge-26.3-3.1.13 | 정식 | Towns and Towers 필수 의존성 |
| [JEI](https://modrinth.com/mod/jei) | 31.4.0.21 | 베타 | 레시피 조회. 베타 허용 결정으로 포함 |

Towns and Towers의 배포 파일명은 `t_and_t-fabric-neoforge-1.13.12.jar`로 두 로더를 함께 담은 JAR이다. NeoForge 메타데이터와 `neoforge [26.3.0.1-beta,)` 의존성을 포함하므로 Fabric 전용 파일이 아니다.

Balm은 `kuma_api`, Cooking for Blockheads는 `shogi_api`, Modonomicon은 commonmark 라이브러리, Cristel Lib은 jankson을 각각 JarJar로 내장한다.

JEI는 `mezz_config 0.6.3`을 내장하며, 같은 파일을 Modrinth에서 단독으로도 받을 수 있다. 두 파일이 바이트 단위로 동일함을 확인한 뒤 모드 ID 중복을 피하려고 단독 JAR은 설치하지 않았다. JEI가 요구하는 `mezz_config [0.6.3,1.0.0)`은 내장 JAR로 충족된다.

## Curios 연동의 확인된 제한

Modrinth의 Occultism 배포 메타데이터는 Curios를 **필수** 의존성으로 표시하지만, 실제 배포된 JAR에서는 이 의존성이 주석 처리돼 있다. 제작자의 26.3 빌드 설정도 Curios 구현을 소스 세트에서 제외한다.

설치한 `occultism-26.3-neoforge-1.256.0.jar`를 직접 확인한 결과는 다음과 같다.

- `META-INF/neoforge.mods.toml`의 `modId = "curios"` 블록 전체가 `#`으로 주석 처리돼 있다. 즉 로더는 Curios를 요구하지 않는다.
- JAR에는 `integration/curios/CuriosIntegration`(추상 진입점)과 `CuriosIntegrationDummy`(빈 구현)만 들어 있다.
- `CuriosIntegration`은 실제 구현 클래스 `com.klikli_dev.occultism.integration.curios.impl.CuriosIntegrationImpl`을 이름으로 찾아 초기화하지만, **그 클래스는 JAR에 없다**. 초기화 실패 시 문자열 `Failed to initialize Curios integration, falling back to dummy implementation.`을 남기고 더미 구현으로 되돌아간다.

따라서 **Curios를 설치해도 이 Occultism 빌드의 장신구 연동은 동작하지 않는다.** 패밀리어 링 등 Curios 슬롯을 사용하는 기능은 더미 구현으로 처리된다. Curios를 설치한 이유는 배포 메타데이터가 선언한 필수 의존성을 만족시키고, Occultism이 함께 배포하는 `data/occultism/curios/slots/*.json` 슬롯 정의가 등록될 수 있게 하기 위해서다. 연동 복구를 기대해서가 아니다. 모드 ID 충돌은 없다(`curios`는 단독 JAR 한 곳에서만 선언).

이 제한은 실제 기동 로그에서 위 메시지로 재확인해야 한다. Curios 제거를 원하면 JAR 삭제만으로 충분하며 Occultism 로딩에는 영향이 없다. 단, 배포 메타데이터상으로는 필수 의존성 미충족 상태가 된다.

## 설치하지 않은 모드

| 대상 | 사유 |
| --- | --- |
| Tech Reborn, Reborn Core | 사용자 요청으로 제외 |
| Carpet, Universal Graves, Polymer, Text Placeholder API | Fabric 전용. 26.3 NeoForge 배포 없음 |
| Farmer's Delight Refabricated | Fabric 전용 이식판. NeoForge 구성에서는 위 CurseForge 이식판으로 대체 |
| Architectury, PolyLib, Resourceful Lib, MidnightLib | NeoForge 26.3 배포는 있으나 이번 구성의 어떤 모드도 필수 의존성으로 요구하지 않아 제외 |
| Dynmap, Neruina, Compact Storage, Wider Ender Chests, Handcrafted, Macaw's 시리즈, Terralith, Structory/Towers, Nullscape, The Bumblezone, Explorify, Croptopia, Create 계열, FTB 계열 | 조회한 배포처에 26.3 파일 없음 |
| Sodium, ImmediatelyFast, Mouse Tweaks | 클라이언트 전용(Modrinth `server_side=unsupported`). 서버에는 설치하지 않는다. ImmediatelyFast·Mouse Tweaks는 클라이언트 모드팩에 담는다. Sodium은 Windows 크래시 때문에 `1.1.1`~`1.1.3`에서 뺐고, `1.1.4`에서 Iris 필수 의존성으로 되돌렸다. Iris(로컬 빌드)도 클라이언트 전용이다 |
| Xaero's Minimap | 클라이언트 모드팩 `1.1.2`에만 담았던 클라이언트 전용 모드. Windows 크래시(`0xc0000005`)의 방아쇠로 A/B 확인돼 `1.1.3`에서 뺐다. 서버에는 처음부터 설치하지 않았다 |
| JourneyMap | 클라이언트 모드팩 `1.1.3`에서 Xaero's Minimap을 대신하는 클라이언트 전용 모드. Modrinth는 `server_side=optional`로 표시하며 지도 표시는 클라이언트만으로 동작하므로 서버에는 설치하지 않았다. 라이선스상 JAR을 재배포할 수 없어 `.mrpack`의 Modrinth 다운로드 항목으로만 설치한다 |
| Indium, Mod Menu | Fabric 전용. 26.3 NeoForge 배포 없음. Indium은 Sodium 0.6 이상과 호환되지 않으며 이 Sodium 빌드가 `indium`을 대신 제공한다 |
| mezz_config 단독 JAR | JEI 내장본과 동일 파일. 모드 ID 중복 방지 |

Architectury·PolyLib·Resourceful Lib·MidnightLib은 필요해지면 그대로 추가할 수 있도록 확인한 26.3 NeoForge 정식 배포 버전을 기록해 둔다: `22.0.2+neoforge`, `2.0.15`, `6.0.0`, `1.9.3.1+26.3-neoforge`.

## 검증

아래는 Claude의 설치 검증 결과다. 이후 Codex가 18개 Modrinth 버전을 API에서 다시 조회하고 CurseForge 파일 2개를 공식 CDN에서 독립적으로 다시 받아 대조했다. 최종 20개 파일의 설치 명세·크기·SHA-512·ZIP 무결성, 중첩 모드의 필수 의존성과 버전 범위, Compose 설정을 확인했다. 기존 Fabric 24개 JAR은 작업 전 SHA-512와 동일하다. 실제 서버 기동·접속·월드 생성은 수행하지 않았으며 파일 검증이 게임 내 동작 검증을 대신하지 않는다.

- Modrinth 18개 JAR은 배포처의 크기·SHA-1·SHA-512와 대조했다. CurseForge 2개는 조회된 SHA-1·MD5·크기와 대조했으며 SHA-512는 다운로드 파일에서 계산해 기록했다. 20개 모두 ZIP 무결성을 통과했다.
- 20개 JAR 전부: NeoForge 메타데이터 보유, Modrinth/CurseForge 배포 메타데이터의 `26.3` + `neoforge` 선언 확인.
- 선언된 모드 ID 25개(내장 JAR 포함)에 중복 없음.
- 모든 `required` 의존성이 설치본 또는 내장 JAR로 충족됨.
- 고정한 NeoForge `26.3.0.8-beta`와 Minecraft `26.3`이 각 JAR이 선언한 버전 범위를 모두 만족함. 가장 높은 하한은 GeckoLib의 `[26.3.0.7-beta,)`다.
- `chunky`, `farmersdelight`, `occultism`, `structures` 존재 확인. `techreborn`, `reborncore` 부재 확인.
- 총 161개 검사 전부 통과.
- `docker compose config --quiet` 성공(기존 최상위 `version` 속성 obsolete 경고는 남음), `bash -n mc_backup.sh` 성공, `git diff --check` 통과.
- `git check-ignore`로 신규 JAR이 Git 추적 대상이 아님을 확인했다.

## 남은 준비 사항

- 서버 기동과 BlueMap 배포는 확인했다. 베타 아티팩트(NeoForge 26.3.0.8-beta, JEI, Curios, Farmer's Delight 이식판)의 장기 런타임 안정성은 확인되지 않았다.
- 기동 로그에서 Occultism의 Curios 연동 폴백 메시지를 확인했다([BlueMap 배포 안내](BLUEMAP.md#검증-기록)).
- Structures의 구조물이 26.3 월드에서 실제로 생성되는지 확인해야 한다. 파일 검증만으로는 판단할 수 없다.
- `mc_backup.sh`는 현재 `server-data-26.3-neoforge/world/`를 매시 30분 백업한다. 월드 외의 모드·설정은 포함하지 않는다([월드 백업 안내](BACKUPS.md)).
- Dynmap은 26.3 배포가 없어 설치하지 않았고, 옛 `8123` 지도 경로는 제거했다. 대신 BlueMap `5.27-neoforge`(Modrinth `1EXOwqA2`)를 lock에 고정했다. 웹 지도는 호스트에 `8100`을 게시하지 않고, 호스트 `443`의 `webmap-nginx`가 Let's Encrypt 인증서로 TLS를 종료해 `minecraft:8100`으로 넘긴다. `https://mcmap.aziran.uk`는 Cloudflare 프록시 `A` 레코드로 이 원본에 연결한다. JAR은 2026-09-24 설치했고 서버 healthy·재시작 0회, Compose 네트워크 `minecraft:8100` HTTP 200, 렌더링 진행 중이다. 로컬 HTTPS 원본과 공개 HTTPS 모두 200을 확인했다. 이전 Cloudflare Tunnel 계획은 터널 생성 API 인증 오류(`10000`)로 폐기했다. 배포·검증·롤백 절차는 [BlueMap 배포 안내](BLUEMAP.md)에 있다.
- Compose의 고정 컨테이너 이름 `minecraft`는 다른 프로젝트의 종료된 컨테이너와 충돌할 수 있다. 공개 기동 전에 대상 컨테이너와 포트를 정리해야 한다.
- 클라이언트는 NeoForge 26.3.0.8-beta와 서버의 콘텐츠 모드 및 클라이언트 필수 의존성을 같은 버전으로 설치해야 한다. Jade, JEI 표시 기능은 클라이언트 설치가 필요하다. Simple Tomb과 Traveler's Backpack도 블록·아이템을 등록하므로 클라이언트에 필요하다. Almanac·Let Me Despawn·BlueMap·SableCraft Standards 등 서버 전용 모드는 제외하며 서버의 파일 전체(lock 25개)를 클라이언트 필수 목록으로 간주하지 않는다. Curios 배낭 패치는 멀티플레이 클라이언트에는 선택 사항이지만, 1.1.12부터 싱글플레이 사용을 위해 팩에 포함한다(통합 서버 실행 미검증).

## 클라이언트 모드팩

클라이언트 팩 `1.1.10`은 `1.1.9`에 클라이언트 전용 Nemo's Inventory Sorting `26.3-1.22.1`(Modrinth `aeA0nhgf`)을 더한 판이다(모드 21개: 서버 공통 15개·클라이언트 전용 6개, 수동·MultiMC ZIP에 담는 JAR 19개. JourneyMap과 Nemo는 라이선스상 `.mrpack` 다운로드 전용). 서버 lock·서버 `mods/`는 바꾸지 않았으므로 서버 백업·재시작이 필요 없다. 세 아카이브에 Nemo 설정 `config/nemos-inventory-sorting/general.json`을 더했고 `options.txt`·`servers.dat`·셰이더 팩·리소스팩은 `1.1.9`와 같다. GitHub 일반 릴리스(latest) [`client-1.1.10`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.10)로 2026-09-25 공개했고 사이트도 배포했다. 근거는 [클라이언트 모드 호환성 검토](CLIENT_MOD_COMPATIBILITY_26_3.md#1110-nemos-inventory-sorting과-mouse-tweaks)에 있다.

클라이언트 팩 `1.1.9`는 `1.1.8`에 서버와 같은 Traveler's Backpack `11.4.0`을 더한 판이다(모드 20개: 서버 공통 15개·클라이언트 전용 5개, 수동·MultiMC ZIP에 담는 JAR 19개. JourneyMap은 계속 `.mrpack` 다운로드 전용). 셰이더 팩, 리소스팩 3개와 기본 활성화, `servers.dat`는 `1.1.8`과 같고, `options.txt`에는 배낭 열기를 상류 기본값 `B` 대신 `Y`로 적은 한 줄(`key_key.travelersbackpack.inventory:key.keyboard.y`)만 더했다. GitHub 일반 릴리스(latest) [`client-1.1.9`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.9)로 2026-09-25 공개했고, 서버에도 같은 날 설치했다(위 절). Iris는 계속 미병합 PR 로컬 빌드다. `B` 중복과 `Y`를 고른 근거는 [클라이언트 모드 호환성 검토](CLIENT_MOD_COMPATIBILITY_26_3.md#119-travelers-backpack-단축키-중복)에 적었다.

클라이언트 팩 `1.1.8`은 `1.1.7`에서 Modonomicon만 `26.3-2.7.0`으로 바꾼 판이다(모드 19개, 셰이더 팩 1개, 리소스팩 3개, `options.txt`·`servers.dat`는 `1.1.7`과 같다). GitHub 사전 릴리스 [`client-1.1.8`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.8)으로 2026-09-25 공개했고, 서버도 같은 날 2.7.0으로 교체했다. 1.1.7 이하 클라이언트의 접속 여부는 확인하지 않았다. 아래는 이전 판 기록이다.

클라이언트 팩 `1.1.6`은 `1.1.5`의 구성(모드 18개, 셰이더 팩 1개, `options.txt`, 기본 멀티플레이 목록 `servers.dat`)에 서버와 같은 Simple Tomb `1.9.0` JAR을 더해 모드 19개를 담는다. GitHub 사전 릴리스 [`client-1.1.6`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.6)으로 공개되어 있다. `1.1.6` 아카이브로 새로 만든 인스턴스의 게임 실행은 아직 확인하지 않았다. 이전 버전 `1.1.5`·`1.1.4`는 사전 릴리스 `client-1.1.5`·`client-1.1.4`로 공개되어 있으며, 서버가 Simple Tomb을 활성화했으므로 이 판들로는 접속할 수 없다. 빌더는 `scripts/build_client_pack.py`이고, 산출물은 Git에서 제외한 `dist/`에 생성되며 설치 안내와 라이선스 표기를 함께 담는다. 생성된 고정 목록은 [mods-26.3-client.lock.json](../mods-26.3-client.lock.json)이다.

`1.1.5` 공개 뒤 빌더에 추가한 SableCraft 제외 사유는 `1.1.6` 산출물과 클라이언트 lock부터 반영된다.

모드는 두 갈래다.

- **서버 공통 15개**: 서버 lock(`mods-26.3.lock.json`)에서 고르고 JAR은 `server-data-26.3-neoforge/mods/`에서 읽는다. Balm, Clumps, Cooking for Blockheads, Curios API, Farmer's Delight, GeckoLib, Jade, JEI, Lithium, Modonomicon, Occultism, Packet Fixer, Simple Tomb, Tom's Simple Storage, Traveler's Backpack. Farmer's Delight 이식판과 Simple Tomb은 Modrinth CDN에 없어 `.mrpack`의 `client-overrides/mods/`에 JAR을 담는다. 서버에도 같은 파일이 있으므로 버전을 맞춰야 한다.
- **클라이언트 전용 5개**: 서버에 설치하지 않는 모드다. 입력 고정 목록은 [mods-26.3-client-extra.lock.json](../mods-26.3-client-extra.lock.json)이고 JAR은 Git에서 제외한 `client-mods-cache/`에 둔다. ImmediatelyFast `1.17.1+26.3-neoforge`, Mouse Tweaks `26.3-2.31-neoforge`, JourneyMap `26.3-6.0.9+neoforge`, Sodium `mc26.3-0.9.2-neoforge`, Iris `1.11.6-snapshot+mc26.3-local`(PR #3354 커밋 `10d3598c…` 로컬 빌드).
- **셰이더 팩 1개**: Complementary Reimagined `r5.9.3`. 입력 lock의 `shaderpacks`에 두며 `.mrpack`의 Modrinth CDN 다운로드 항목으로만 설치한다. 기본으로 켜지 않는다.

`1.1.4`의 Iris 대응 소스 번들, Sodium 복귀 근거, Occultism 사역마 단축키용 `options.txt` 우회는 [클라이언트 모드 호환성 검토](CLIENT_MOD_COMPATIBILITY_26_3.md)에 적었다.

서버에만 두고 제외한 8개: Almanac, Chunky, Cristel Lib, Let Me Despawn, SableCraft Standards, Structures, Towns and Towers, spark. Structures와 Towns and Towers는 클래스 파일이 0개인 데이터팩 JAR이다. SableCraft Standards는 서버 설치만으로 명령이 동작하며 클라이언트 설치는 선택 사항이다. Lithium과 Clumps는 1.0.0에서 "서버 측 동작"으로 제외했으나, 클라이언트에서도 동작하는 모드라 1.1.0부터 서버와 같은 파일을 함께 담는다. 둘 다 이미 서버에 설치돼 있어 서버 구성은 바꾸지 않았다.

### 1.1.3에서 Xaero's Minimap을 JourneyMap으로 교체

`1.1.2`에 담았던 Xaero's Minimap(`xaerominimap-neoforge-26.3-26.5.3.jar`)을 빼고 JourneyMap `26.3-6.0.9+neoforge`를 같은 자리에 넣었다. 16개를 모두 켠 `1.1.2`가 Windows에서 네이티브 종료 코드 `0xc0000005`(액세스 위반)로 크래시했고, 사용자가 같은 인스턴스에서 그 JAR 하나만 비활성화하자 실행됐기 때문이다. `1.1.1`과 `1.1.2`의 최상위 JAR 차이도 그 파일 하나뿐이었으므로 그 조합에서의 방아쇠는 Xaero's Minimap으로 확인됐다. 다만 네이티브 실패 메커니즘은 규명하지 않았고, 모드 자체의 결함이라고 단정하지 않았다.

Modrinth 프로젝트 `lfHFW1mp`의 버전 `OCuB6UWq`(`journeymap-neoforge-26.3-6.0.9.jar`, 4352830바이트, SHA-1 `e4d81a33…`)를 캐시에 받아 크기·SHA-1·SHA-512를 배포처 메타데이터와 대조했다. JAR의 `neoforge.mods.toml`은 모드 ID `journeymap`과 NeoForge `[26.1.2.22-beta,)`, `commonnetworking [1.0.22,)`를 필수로 선언한다. 고정한 `26.3.0.8-beta`가 첫 범위를 만족하고, `commonnetworking`은 내장 JAR `common-networking-neoforge-26.3-1.1.1.jar`가 제공한다. 내장 JAR은 그 밖에 `journeymap_api`와 모드 ID가 없는 `pngj-2.1.0.jar`를 포함한다. Modrinth 버전 메타데이터의 `dependencies`는 비어 있으므로, 필수 의존성은 JAR 메타데이터 쪽이 기준이다. 루트의 `fabric.mod.json`은 `id=journeymap-wrongloader`인 안내용 스텁이며 이 JAR은 NeoForge 전용이다.

**서버에는 설치하지 않았다.** Modrinth 표시는 `client_side=optional`, `server_side=optional`이고 지도 표시와 웨이포인트는 클라이언트만으로 동작한다. 서버 구성·모드 디렉터리·서버 lock은 건드리지 않았다. `.mrpack` 항목의 `env.server`는 이 팩이 서버에 아무것도 설치하지 않는다는 뜻으로 `unsupported`를 쓴다.

**라이선스 때문에 JAR을 팩에 담지 않는다.** [공식 라이선스 문서](https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/)는 "Create a modpack containing JourneyMap, as long as JourneyMap is downloaded from CurseForge or Modrinth as part of the modpack installation or launch process"만 허용하고 "Re-host, redistribute or bundle the mod in any way, including as part of a larger distribution such as a modpack"을 금지한다. JAR 루트의 `license.txt`도 같은 취지로 재배포를 금지한다. 그래서 `.mrpack`에는 Modrinth CDN 다운로드 항목으로만 넣고, JAR을 담는 수동 ZIP과 MultiMC 인스턴스 ZIP에서는 뺐다. 두 ZIP은 나머지 15개만 담으며, 생성되는 `README.md`가 맨 앞에서 그 사실과 공식 배포처에서 직접 받아 넣는 절차(파일 이름·크기·SHA-1·SHA-512 대조 포함)를 안내한다. MultiMC 사용자에게는 `.mrpack` 가져오기를 권한다. [MultiMC 위키의 Import Instance 문서](https://github.com/MultiMC/Launcher/wiki/Import-Instance)가 가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있다(최소 버전은 명시하지 않는다). `client-mods-cache/`의 로컬 사본은 해시·메타데이터 검증용이며 산출물에는 들어가지 않는다.

빌더는 입력 lock의 `bundle_jar=false` 표시를 읽어 이 동작을 결정한다. `bundle_jar=false`인데 Modrinth CDN URL이 없으면 설치 경로가 없으므로 빌드를 중단한다. 생성된 고정 목록에는 `bundled_jar_count`와 `external_download_only` 항목으로 남는다.

### Sodium 제외 기록 (`1.1.1`~`1.1.3`)

`1.1.4`는 Iris 필수 의존성으로 같은 Sodium 파일을 되돌렸다. 아래는 제외했던 기간의 기록이다.

`1.1.1`은 `1.1.0`에서 Sodium `mc26.3-0.9.2-neoforge`만 뺀 구성이었고, `1.1.2`·`1.1.3`도 Sodium을 넣지 않는다. 사용자가 `1.1.0` 인스턴스에서 Sodium JAR만 비활성화한 뒤 Windows MultiMC 실행과 서버 접속에 성공했다고 알려 왔기 때문이다. 다만 크래시 로그에 남았던 네이티브 종료 코드 `0xc0000409`의 정확한 원인은 확정하지 못했다. 로그에는 Sodium의 Nvidia 드라이버 워크어라운드가 `IllegalStateException: Command line is already modified`로 실패한 기록이 있었지만, 그 예외가 종료의 직접 원인인지 드라이버·런처·다른 요소와의 조합이 관여했는지는 알 수 없다. 확인된 사실은 "Sodium이 없으면 해당 PC에서 실행·접속된다"까지다. 입력 lock에서는 항목을 지우고 `removed`에 근거와 이후 관찰 결과를 남겼다. 사용자는 이전 인스턴스를 재사용하지 말고 새 MultiMC 인스턴스로 가져와야 이전 Sodium JAR이 남지 않는다.

Farmer's Delight와 Simple Tomb(`1.1.6`부터)은 CurseForge 배포라 Modrinth CDN 화이트리스트를 쓸 수 없고, Iris는 공식 배포처에 없는 로컬 빌드라 셋 다 `.mrpack`의 `client-overrides/mods/`에 직접 담는다. 나머지 16개 모드와 셰이더 팩은 런처가 Modrinth CDN에서 받는다.

빌더는 패키징 전에 두 lock의 크기·SHA-512를 실제 JAR과 대조하고, 서버 공통 모드와 클라이언트 전용 모드의 모드 ID 충돌도 검사한다.

재빌드는 이번 버전 산출물 3개를 만든 뒤 `dist/`에서 **이전 버전의 MultiMC 인스턴스 ZIP만 휴지통으로 보낸다**(`prune_old_multimc_zips`). MultiMC 가져오기는 고른 파일 하나만 보므로 이전 인스턴스 ZIP이 남아 있으면 Sodium이나 Xaero's Minimap이 든 옛 구성을 다시 가져올 수 있기 때문이다.

영구 삭제가 아니다. `gio trash`로 데스크톱 휴지통에 넣으므로 `~/.local/share/Trash/`에 원래 경로(`Path=...dist/...`)와 삭제 시각이 `.trashinfo`로 남고, 파일 관리자나 `gio trash --restore`로 `dist/`에 되돌릴 수 있다. `gio`를 찾지 못하거나 명령이 실패하면 `SystemExit`로 빌드를 중단하며, 되돌릴 수 없는 삭제로 대체하지 않는다. 이전 버전의 `.mrpack`과 수동 ZIP은 건드리지 않는다. 런처에 이미 가져와 둔 인스턴스는 `dist/`의 이 파일들과 별개라 영향을 받지 않는다.

선택·제외 근거와 라이선스, 해시는 [클라이언트 모드 호환성 검토](CLIENT_MOD_COMPATIBILITY_26_3.md)에 정리했다.

### 1.1.2의 Windows 크래시: 방아쇠는 Xaero's Minimap

16개를 모두 켠 `1.1.2`는 Windows에서 네이티브 종료 코드 `0xc0000005`(액세스 위반)로 크래시한다. `1.1.0`에서 나던 `0xc0000409`와는 다른 코드다.

사용자가 같은 인스턴스에서 `xaerominimap-neoforge-26.3-26.5.3.jar` **하나만** 비활성화해 실행했고 정상 실행됨을 확인했다. 산출물 대조로도 `1.1.1`과 `1.1.2`의 최상위 모드 JAR 차이는 이 파일 하나뿐이며 공통 15개는 SHA-512까지 같다. 바뀐 변수가 이 JAR 하나이므로 **이 모드·드라이버·런타임 조합에서 크래시의 방아쇠는 Xaero's Minimap**(내장 `xaerolib` 포함)이라고 확인됐다.

확인되지 않은 것은 네이티브 실패 메커니즘이다. 모드 결함인지, 해당 PC의 그래픽 드라이버·GPU와의 조합인지, NeoForge 26.3 베타나 다른 모드와의 상호작용인지 구분하지 않았다. 이전 `0xc0000409` 크래시와 같은 뿌리인지도 모른다. 이 결과는 해당 환경에 한정되며 이 모드가 일반적으로 깨졌다는 뜻이 아니다.

운용상으로는 `1.1.2`를 설치한 뒤 이 JAR을 빼면 `1.1.1`과 같은 15개 구성이 되어 실행된다. 실행과 서버 접속이 함께 확인된 구성은 Sodium을 꺼 둔 `1.1.0` 인스턴스이고, Xaero를 뺀 `1.1.2`는 실행까지 확인됐다. 미니맵이 필요하면 다른 버전이나 다른 미니맵 모드를 검토해야 하며, 모드 구성 변경은 이번 문서 갱신 범위에 넣지 않았다.

## 이전 Fabric 구성의 보존

Fabric 준비 당시의 고정 목록은 [mods-26.3-fabric-historical.lock.json](../mods-26.3-fabric-historical.lock.json)으로 이름을 바꿔 보존했다. 해당 JAR 24개는 `server-data-26.3/mods/`에 그대로 남아 있으며 이번 작업에서 수정하지 않았다. 활성 구성은 `mods-26.3.lock.json`이며 `loader`, `data_directory` 필드로 구분한다.

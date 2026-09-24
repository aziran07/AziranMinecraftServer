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

lock의 21개 항목에 해당하는 JAR 21개를 설치했다. 최초 설치 20개에 BlueMap `5.27-neoforge`를 2026-09-24 추가 설치했다([BlueMap 배포 안내](BLUEMAP.md)). 아래 설치 검증 기록은 최초 20개 기준이다. 배포 채널, 다운로드 URL, 파일 크기, SHA-1/SHA-512, 선언된 모드 ID, 필수 의존성 범위, 내부 번들 JAR은 [mods-26.3.lock.json](../mods-26.3.lock.json)에 기록한다.

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
| [Modonomicon](https://modrinth.com/mod/modonomicon) | 26.3-2.6.0 | 정식 | Occultism 요구 `[2.5.0,)` 충족 |
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
- 클라이언트는 NeoForge 26.3.0.8-beta와 서버의 콘텐츠 모드 및 클라이언트 필수 의존성을 같은 버전으로 설치해야 한다. Jade, JEI 표시 기능은 클라이언트 설치가 필요하다. Almanac·Let Me Despawn·BlueMap 등 서버 전용 모드는 제외하며 서버의 21개 파일 전체를 클라이언트 필수 목록으로 간주하지 않는다.

## 클라이언트 모드팩

현재 클라이언트 팩 `1.1.5`는 `1.1.4`와 같은 모드 18개와 셰이더 팩 1개에 기본 멀티플레이 목록 `servers.dat`(`mc.aziran.uk`)를 더해 담으며, GitHub 사전 릴리스 [`client-1.1.5`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.5)로 공개되어 있다. `1.1.5` 아카이브로 새로 만든 인스턴스의 게임 실행은 아직 확인하지 않았다. 이전 버전 `1.1.4`는 사전 릴리스 `client-1.1.4`로 공개되어 있다. 빌더는 `scripts/build_client_pack.py`이고, 산출물은 Git에서 제외한 `dist/`에 생성되며 설치 안내와 라이선스 표기를 함께 담는다. 생성된 고정 목록은 [mods-26.3-client.lock.json](../mods-26.3-client.lock.json)이다.

모드는 두 갈래다.

- **서버 공통 13개**: 서버 lock(`mods-26.3.lock.json`)에서 고르고 JAR은 `server-data-26.3-neoforge/mods/`에서 읽는다. Balm, Clumps, Cooking for Blockheads, Curios API, Farmer's Delight, GeckoLib, Jade, JEI, Lithium, Modonomicon, Occultism, Packet Fixer, Tom's Simple Storage. 서버에도 같은 파일이 있으므로 버전을 맞춰야 한다.
- **클라이언트 전용 5개**: 서버에 설치하지 않는 모드다. 입력 고정 목록은 [mods-26.3-client-extra.lock.json](../mods-26.3-client-extra.lock.json)이고 JAR은 Git에서 제외한 `client-mods-cache/`에 둔다. ImmediatelyFast `1.17.1+26.3-neoforge`, Mouse Tweaks `26.3-2.31-neoforge`, JourneyMap `26.3-6.0.9+neoforge`, Sodium `mc26.3-0.9.2-neoforge`, Iris `1.11.6-snapshot+mc26.3-local`(PR #3354 커밋 `10d3598c…` 로컬 빌드).
- **셰이더 팩 1개**: Complementary Reimagined `r5.9.3`. 입력 lock의 `shaderpacks`에 두며 `.mrpack`의 Modrinth CDN 다운로드 항목으로만 설치한다. 기본으로 켜지 않는다.

`1.1.4`의 Iris 대응 소스 번들, Sodium 복귀 근거, Occultism 사역마 단축키용 `options.txt` 우회는 [클라이언트 모드 호환성 검토](CLIENT_MOD_COMPATIBILITY_26_3.md)에 적었다.

서버에만 두고 제외한 7개: Almanac, Chunky, Cristel Lib, Let Me Despawn, Structures, Towns and Towers, spark. 제외 근거는 각 모드의 Modrinth `client_side` 값과 JAR 검사 결과다. Structures와 Towns and Towers는 클래스 파일이 0개인 데이터팩 JAR이고, 제외한 7개 중 NeoForge 네트워크 페이로드를 등록하는 모드는 없다. Lithium과 Clumps는 1.0.0에서 "서버 측 동작"으로 제외했으나, 클라이언트에서도 동작하는 모드라 1.1.0부터 서버와 같은 파일을 함께 담는다. 둘 다 이미 서버에 설치돼 있어 서버 구성은 바꾸지 않았다.

### 1.1.3에서 Xaero's Minimap을 JourneyMap으로 교체

`1.1.2`에 담았던 Xaero's Minimap(`xaerominimap-neoforge-26.3-26.5.3.jar`)을 빼고 JourneyMap `26.3-6.0.9+neoforge`를 같은 자리에 넣었다. 16개를 모두 켠 `1.1.2`가 Windows에서 네이티브 종료 코드 `0xc0000005`(액세스 위반)로 크래시했고, 사용자가 같은 인스턴스에서 그 JAR 하나만 비활성화하자 실행됐기 때문이다. `1.1.1`과 `1.1.2`의 최상위 JAR 차이도 그 파일 하나뿐이었으므로 그 조합에서의 방아쇠는 Xaero's Minimap으로 확인됐다. 다만 네이티브 실패 메커니즘은 규명하지 않았고, 모드 자체의 결함이라고 단정하지 않았다.

Modrinth 프로젝트 `lfHFW1mp`의 버전 `OCuB6UWq`(`journeymap-neoforge-26.3-6.0.9.jar`, 4352830바이트, SHA-1 `e4d81a33…`)를 캐시에 받아 크기·SHA-1·SHA-512를 배포처 메타데이터와 대조했다. JAR의 `neoforge.mods.toml`은 모드 ID `journeymap`과 NeoForge `[26.1.2.22-beta,)`, `commonnetworking [1.0.22,)`를 필수로 선언한다. 고정한 `26.3.0.8-beta`가 첫 범위를 만족하고, `commonnetworking`은 내장 JAR `common-networking-neoforge-26.3-1.1.1.jar`가 제공한다. 내장 JAR은 그 밖에 `journeymap_api`와 모드 ID가 없는 `pngj-2.1.0.jar`를 포함한다. Modrinth 버전 메타데이터의 `dependencies`는 비어 있으므로, 필수 의존성은 JAR 메타데이터 쪽이 기준이다. 루트의 `fabric.mod.json`은 `id=journeymap-wrongloader`인 안내용 스텁이며 이 JAR은 NeoForge 전용이다.

**서버에는 설치하지 않았다.** Modrinth 표시는 `client_side=optional`, `server_side=optional`이고 지도 표시와 웨이포인트는 클라이언트만으로 동작한다. 서버 구성·모드 디렉터리·서버 lock은 건드리지 않았다. `.mrpack` 항목의 `env.server`는 이 팩이 서버에 아무것도 설치하지 않는다는 뜻으로 `unsupported`를 쓴다.

**라이선스 때문에 JAR을 팩에 담지 않는다.** [공식 라이선스 문서](https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/)는 "Create a modpack containing JourneyMap, as long as JourneyMap is downloaded from CurseForge or Modrinth as part of the modpack installation or launch process"만 허용하고 "Re-host, redistribute or bundle the mod in any way, including as part of a larger distribution such as a modpack"을 금지한다. JAR 루트의 `license.txt`도 같은 취지로 재배포를 금지한다. 그래서 `.mrpack`에는 Modrinth CDN 다운로드 항목으로만 넣고, JAR을 담는 수동 ZIP과 MultiMC 인스턴스 ZIP에서는 뺐다. 두 ZIP은 나머지 15개만 담으며, 생성되는 `README.md`가 맨 앞에서 그 사실과 공식 배포처에서 직접 받아 넣는 절차(파일 이름·크기·SHA-1·SHA-512 대조 포함)를 안내한다. MultiMC 사용자에게는 `.mrpack` 가져오기를 권한다. [MultiMC 위키의 Import Instance 문서](https://github.com/MultiMC/Launcher/wiki/Import-Instance)가 가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있다(최소 버전은 명시하지 않는다). `client-mods-cache/`의 로컬 사본은 해시·메타데이터 검증용이며 산출물에는 들어가지 않는다.

빌더는 입력 lock의 `bundle_jar=false` 표시를 읽어 이 동작을 결정한다. `bundle_jar=false`인데 Modrinth CDN URL이 없으면 설치 경로가 없으므로 빌드를 중단한다. 생성된 고정 목록에는 `bundled_jar_count`와 `external_download_only` 항목으로 남는다.

### Sodium 제외 기록 (`1.1.1`~`1.1.3`)

`1.1.4`는 Iris 필수 의존성으로 같은 Sodium 파일을 되돌렸다. 아래는 제외했던 기간의 기록이다.

`1.1.1`은 `1.1.0`에서 Sodium `mc26.3-0.9.2-neoforge`만 뺀 구성이었고, `1.1.2`·`1.1.3`도 Sodium을 넣지 않는다. 사용자가 `1.1.0` 인스턴스에서 Sodium JAR만 비활성화한 뒤 Windows MultiMC 실행과 서버 접속에 성공했다고 알려 왔기 때문이다. 다만 크래시 로그에 남았던 네이티브 종료 코드 `0xc0000409`의 정확한 원인은 확정하지 못했다. 로그에는 Sodium의 Nvidia 드라이버 워크어라운드가 `IllegalStateException: Command line is already modified`로 실패한 기록이 있었지만, 그 예외가 종료의 직접 원인인지 드라이버·런처·다른 요소와의 조합이 관여했는지는 알 수 없다. 확인된 사실은 "Sodium이 없으면 해당 PC에서 실행·접속된다"까지다. 입력 lock에서는 항목을 지우고 `removed`에 근거와 이후 관찰 결과를 남겼다. 사용자는 이전 인스턴스를 재사용하지 말고 새 MultiMC 인스턴스로 가져와야 이전 Sodium JAR이 남지 않는다.

Farmer's Delight는 CurseForge 배포라 Modrinth CDN 화이트리스트를 쓸 수 없고, Iris는 공식 배포처에 없는 로컬 빌드라 둘 다 `.mrpack`의 `client-overrides/mods/`에 직접 담는다. 나머지 16개 모드와 셰이더 팩은 런처가 Modrinth CDN에서 받는다.

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

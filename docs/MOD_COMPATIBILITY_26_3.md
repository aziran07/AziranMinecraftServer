# 기존 모드의 26.3 Fabric 지원 조사

> 이 문서는 Fabric 유지를 검토하던 시점의 조사 기록이다. 2026-09-22 사용자가 NeoForge 전환을 승인해 현재 구성은 NeoForge다. 현행 설치 목록은 [모드 설치 안내](MODS_26_3.md), 로더별 비교와 결정 근거는 [로더 비교](LOADER_COMPARISON_26_3.md)를 참고한다.

2026-09-22 조사. 이전 1.21 Fabric 모드 파일명 기록을 기준으로 조회했다. 현재 `server-data/mods/`는 비어 있으며, 같은 파일명 목록이 남아 있는 `minecraftMin/data/mods/`를 읽기 전용으로 교차 확인했다. 실제 설치 대상은 이 저장소의 `server-data-26.3/mods/`다.

Modrinth 버전 API에서 `game_versions=["26.3"]`, `loaders=["fabric"]`로 조회하고 서버에 사용할 수 있는 정식 배포판을 우선한다. 조회 실패나 결과 없음은 다른 배포처까지 포함한 절대적인 미지원 판정이 아니다.

| 모드 | 조회 결과 |
| --- | --- |
| [chunky](https://modrinth.com/project/chunky) | 정식 배포 1.5.3 |
| [clumps](https://modrinth.com/project/clumps) | 정식 배포 26.3.2 |
| [dynmap](https://modrinth.com/project/dynmap) | 26.3 Fabric 배포 조회 결과 없음 |
| [jade](https://modrinth.com/project/jade) | 정식 배포 26.3.1+fabric |
| [neruina](https://modrinth.com/project/neruina) | 26.3 Fabric 배포 조회 결과 없음 |
| [reborncore](https://modrinth.com/project/reborncore) | 사용자 요청으로 제외 (26.3 베타판만 확인) |
| [techreborn](https://modrinth.com/project/techreborn) | 사용자 요청으로 제외 (26.3 베타판만 확인) |
| [architectury-api](https://modrinth.com/project/architectury-api) | 정식 배포 22.0.2+fabric |
| [compact-storage](https://modrinth.com/project/compact-storage) | 26.3 Fabric 배포 조회 결과 없음 |
| [carpet](https://modrinth.com/project/carpet) | 정식 배포 26.3 |
| [wider-ender-chests](https://modrinth.com/project/wider-ender-chests) | 26.3 Fabric 배포 조회 결과 없음 |
| [ftb-chunks](https://modrinth.com/project/ftb-chunks) | Modrinth slug 조회 실패 — 지원 미확인 |
| [ftb-essentials](https://modrinth.com/project/ftb-essentials) | Modrinth slug 조회 실패 — 지원 미확인 |
| [ftb-library](https://modrinth.com/project/ftb-library) | Modrinth slug 조회 실패 — 지원 미확인 |
| [ftb-teams](https://modrinth.com/project/ftb-teams) | Modrinth slug 조회 실패 — 지원 미확인 |
| [universal-graves](https://modrinth.com/project/universal-graves) | 정식 배포 3.13.0+26.3 |
| [handcrafted](https://modrinth.com/project/handcrafted) | 26.3 Fabric 배포 조회 결과 없음 |
| [indium](https://modrinth.com/project/indium) | 클라이언트 전용 — 서버 설치 제외 |
| [jei](https://modrinth.com/project/jei) | 정식 배포 없음 — 베타/알파판 보류 |
| [let-me-despawn](https://modrinth.com/project/lmd) | 정확한 slug는 lmd — 정식 1.26.9.2 확인 (Almanac 필요) |
| [lithium](https://modrinth.com/project/lithium) | 정식 배포 mc26.3-0.26.1-fabric |
| [macaws-bridges](https://modrinth.com/project/macaws-bridges) | 26.3 Fabric 배포 조회 결과 없음 |
| [macaws-doors](https://modrinth.com/project/macaws-doors) | 26.3 Fabric 배포 조회 결과 없음 |
| [macaws-fences-and-walls](https://modrinth.com/project/macaws-fences-and-walls) | 26.3 Fabric 배포 조회 결과 없음 |
| [macaws-lights-and-lamps](https://modrinth.com/project/macaws-lights-and-lamps) | 26.3 Fabric 배포 조회 결과 없음 |
| [macaws-paths-and-pavings](https://modrinth.com/project/macaws-paths-and-pavings) | 26.3 Fabric 배포 조회 결과 없음 |
| [macaws-trapdoors](https://modrinth.com/project/macaws-trapdoors) | 26.3 Fabric 배포 조회 결과 없음 |
| [midnightlib](https://modrinth.com/project/midnightlib) | 정식 배포 1.9.3+26.3-fabric |
| [modmenu](https://modrinth.com/project/modmenu) | 클라이언트 전용 — 서버 설치 제외 |
| [packet-fixer](https://modrinth.com/project/packet-fixer) | 정식 배포 3.3.6 |
| [placeholder-api](https://modrinth.com/project/placeholder-api) | 정식 배포 3.2.0+26.3 |
| [polylib](https://modrinth.com/project/polylib) | 정식 배포 2.0.15 |
| [resourceful-lib](https://modrinth.com/project/resourceful-lib) | 정식 배포 6.0.0 |
| [sodium](https://modrinth.com/project/sodium) | 클라이언트 전용 — 서버 설치 제외 |
| [spark](https://modrinth.com/project/spark) | 정식 배포 1.10.187-fabric |
| [toms-storage](https://modrinth.com/project/toms-storage) | 정식 배포 26.3-2.12.0-fabric |
| [epherolib](https://modrinth.com/project/epherolib) | 26.3 Fabric 배포 조회 결과 없음 |

이미 설치된 Fabric API·Cloth Config와 지난 조사에서 보류한 Croptopia·Terralith·Structory/Towers·Nullscape·The Bumblezone도 [설치 안내](MODS_26_3.md)를 참고한다.

FTB는 Modrinth slug 조회만으로 미지원 판단을 내리지 않았다. [FTB Chunks](https://www.curseforge.com/minecraft/mc-mods/ftb-chunks-fabric), [FTB Library](https://www.curseforge.com/minecraft/mc-mods/ftb-library-fabric), [FTB Teams](https://www.curseforge.com/minecraft/mc-mods/ftb-teams-fabric)의 제작자 배포 페이지에서 26.1.2 계열까지 확인했으며 26.3 배포는 확인하지 못했다. FTB Essentials Fabric 페이지 조회는 실패했으므로 지원 미확인으로 남긴다.

추가 의존성: Universal Graves → Polymer 0.18.2+26.3, Let Me Despawn → Almanac 1.26.9.1. Almanac의 파일명은 26.2를 포함하지만 제작자 메타데이터에는 정식 26.3 지원이 명시돼 있다.

Create는 설치하지 않았다. 2026-09-22 조회에서 [원본 Create](https://modrinth.com/mod/create/versions)는 1.21.1, [Create Fabric](https://modrinth.com/mod/create-fabric/versions)은 1.20.1, 별도 이식판 [Create Fly](https://modrinth.com/mod/create-fly/versions)는 26.2까지 표시된다. 확인한 배포에 26.3 지원 파일은 없다.

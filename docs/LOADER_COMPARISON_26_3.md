# Minecraft 26.3 로더 비교와 최종 결정

2026-09-22 조사. 기존 모드와 추천 후보를 대상으로 Modrinth의 프로젝트별 버전 API에 `game_versions=["26.3"]`를 적용해 로더별 배포를 비교했다. 전체 생태계의 모드 수 순위가 아니며 라이브러리와 클라이언트 전용 모드는 집계하지 않았다. 배포 존재 확인과 실제 기동 검증은 다르다.

## 결정: NeoForge

2026-09-22 사용자가 **NeoForge 전환과 베타 배포 사용을 승인**했다. Occultism과 Farmer's Delight(비공식 NeoForge 이식판)를 반드시 포함하고, Tech Reborn·Reborn Core는 제외한다. 같은 날 추가 요청으로 [Structures](https://www.curseforge.com/minecraft/mc-mods/structures-modd) 4.1도 포함했다. 확정된 구성은 Minecraft `26.3`, NeoForge `26.3.0.8-beta`, 데이터 경로 `server-data-26.3-neoforge/`다. 설치 결과는 [모드 설치 안내](MODS_26_3.md)와 [mods-26.3.lock.json](../mods-26.3.lock.json)에 있다.

이 결정 이전의 잠정 결론은 Fabric 유지였다. 정식 배포 수만 비교하면 Fabric이 근소하게 많았으나, 사용자가 요구한 Occultism이 NeoForge 전용이고 Farmer's Delight의 26.3 배포도 NeoForge 이식판만 존재해 요구사항을 만족하는 로더는 NeoForge뿐이다. 베타 허용으로 JEI도 양쪽 모두 설치 가능해졌다.

## 후보군의 로더별 배포 수

| 후보군 | Fabric | NeoForge | Forge |
| --- | ---: | ---: | ---: |
| Chunky, spark | 2 | 2 | 2 |
| Clumps, Jade, Let Me Despawn, Lithium, Packet Fixer, Tom's Storage, Cooking for Blockheads, Towns and Towers | 8 | 8 | 0 |
| Carpet, Universal Graves | 2 | 0 | 0 |
| Farmer's Delight Refabricated(비공식 Fabric 이식) | 1 | 0 | 0 |
| Farmer's Delight 26 Neo Ver(비공식 NeoForge 이식, CurseForge) | 0 | 1 | 0 |
| Occultism | 0 | 1 | 0 |
| JEI(베타) | 1 | 1 | 0 |
| Structures(CurseForge, 다중 로더) | 1 | 1 | 1 |
| 합계 | 15 | 14 | 3 |

정식 배포만 세면 Fabric 13 / NeoForge 11이었다. 여기에 사용자가 요구한 Occultism과 베타 허용분을 반영한 값이 위 표다. Fabric 쪽 우위는 Carpet·Universal Graves처럼 Polymer 계열 Fabric 전용 모드에서 나온다.

## 로더 전용으로 확인된 항목

- **NeoForge 전용:** Occultism(+ Modonomicon, GeckoLib, Curios), Farmer's Delight 26 Neo Ver.
- **Fabric 전용:** Carpet, Universal Graves와 그 의존성 Polymer·Text Placeholder API, Farmer's Delight Refabricated.
- **양쪽 지원:** Chunky, Clumps, Jade, Let Me Despawn(+Almanac), Lithium, Packet Fixer, spark, Tom's Storage, Cooking for Blockheads(+Balm), Towns and Towers(+Cristel Lib), JEI(베타), Structures.

Cloth Config는 26.3 NeoForge 배포가 조회되지 않았다. Fabric 구성에서는 Cristel Lib의 필수 의존성이었으나, NeoForge용 Cristel Lib `3.1.13`의 `neoforge.mods.toml`은 Cloth Config를 요구하지 않고 jankson을 내장하므로 이번 구성에는 필요하지 않다.

## 어느 로더에서도 26.3 배포를 찾지 못한 모드

Dynmap, Neruina, Compact Storage, Wider Ender Chests, Handcrafted, Macaw's Bridges/Doors/Fences and Walls/Lights and Lamps/Paths and Pavings/Trapdoors, Terralith, Structory, Structory Towers, Nullscape, The Bumblezone, Explorify, 원본 Farmer's Delight, Aquaculture, Create/Create Fabric/Create Fly. 다른 배포처나 별도 이식 프로젝트까지 포함한 미지원 판정은 아니다.

Modrinth 조회가 실패한 프로젝트는 제작자 CurseForge 배포로 보완했다.

- [Croptopia](https://www.curseforge.com/minecraft/mc-mods/croptopia): 26.2까지 확인, 26.3 미확인.
- [FTB Chunks NeoForge](https://www.curseforge.com/minecraft/mc-mods/ftb-chunks-forge), [FTB Essentials](https://www.curseforge.com/minecraft/mc-mods/ftb-essentials): 26.1.2까지 확인, 26.3 미확인.
- [Dungeon Crawl](https://www.curseforge.com/minecraft/mc-mods/dungeon-crawl): 26.2까지 확인.
- [Twilight Forest](https://www.curseforge.com/minecraft/mc-mods/the-twilight-forest): 1.21.1까지 확인.

## Occultism의 의존성과 Curios 제한

[공식 26.3 파일](https://www.curseforge.com/minecraft/mc-mods/occultism/files/8939674): `occultism-26.3-neoforge-1.256.0.jar`, Modrinth 버전 ID `gayRu2vd`.

| 구성 | 고정 버전 | 요구 사항 |
| --- | --- | --- |
| Occultism | 1.256.0 | NeoForge `[26.3.0.3-beta,)` |
| Modonomicon | 2.6.0 | Occultism 요구 `[2.5.0,)` 충족 |
| GeckoLib | 5.5.7 | Occultism 요구 `[5.5.6,)` 충족. 자체적으로 NeoForge `[26.3.0.7-beta,)` 필요 |
| Code Defined GUI | 1.13.0 | Occultism이 JarJar로 내장 |
| Magic Particles Lib | 1.8.0 | Occultism이 JarJar로 내장 |
| Curios API | 17.0.0-beta+26.3 | 배포 메타데이터상 필수. 실제 연동은 동작하지 않음 |

GeckoLib의 하한 때문에 NeoForge 고정 버전은 `26.3.0.7-beta` 이상이어야 한다. 26.3 계열 최신인 `26.3.0.8-beta`를 사용한다.

Modrinth 배포 메타데이터는 Curios를 필수로 표시하지만 실제 JAR에서는 해당 의존성이 주석 처리돼 있고, 연동 구현 클래스가 빌드에서 빠져 있다. Curios를 설치해도 이 빌드의 장신구 연동은 복구되지 않는다. 확인 근거와 결정 이유는 [모드 설치 안내](MODS_26_3.md#curios-연동의-확인된-제한)에 기록했다.

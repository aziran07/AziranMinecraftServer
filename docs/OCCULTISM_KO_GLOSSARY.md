# Occultism 한국어 용어집과 번역 기준

상태: **용어 기준 확정 — 2026-09-25 사용자 결정 반영 완료**

이 문서는 누락 번역에 사용할 프로젝트 용어 기준이다. 기존 번역 기록과 채택 표기를 구분하며, 실제 번역에서는 **채택 표기**를 사용한다. 이 문서에 수록한 변경·신규 표기는 사용자의 일괄 채택 결정과 원문을 확인한 추가 용어 결정으로 확정했다. [한국어 리소스팩](OCCULTISM_KO_TRANSLATION.md)에 반영했으며 상류 프로젝트의 공식 번역과는 별개다.

확정 사항: Machine Operator는 **기계 조작자**, Essence Decay는 **진액 부패**다. Djinni는 **지니**, Spirit은 **영혼**, Demon은 **악마**, Familiar는 **사역마**, Lumberjack은 **벌목꾼**, Transporter는 **운반꾼**으로 통일한다. 고유명사 **악령의 꿈**과 Afrit의 **악령**은 유지한다.

## 기준 파일과 조사 방법

- 조사일: 2026-09-25
- 대상: Minecraft 26.3 / Occultism `1.256.0`
- 로컬 JAR: `server-data-26.3-neoforge/mods/occultism-26.3-neoforge-1.256.0.jar`
- SHA-256: `118d02366adffbd8ebbe0024f484c88d8720eff43fb70b1adfd7d0fde74ddb51`
- 배포 기준: [클라이언트 lock](../mods-26.3-client.lock.json)의 Occultism 항목과 실제 JAR의 SHA-256 일치 확인.
- JAR 내부 원문: `assets/occultism/lang/en_us.json`
- JAR 내부 기존 번역: `assets/occultism/lang/ko_kr.json`

두 JSON의 **동일한 키**를 기준으로 대조했다. 영문 키 이름에서 영어 표시명을 추정하지 않는다. 이름 대응표에서는 영어 원문과 한국어 값이 모두 같은 항목만 한 행으로 묶고, 근거 키를 모두 남긴다. 문장 속 단어를 추출한 핵심 용어는 별도 표에서 추출임을 표시한다.

| 범위 | 영어 키 수 | 대응 한국어 값에 한글 포함 | 한국어 값이 영어 원문과 동일 | 한국어 파일에 키 없음 |
|---|---:|---:|---:|---:|
| 전체 | 4,332 | 389 | 2,915 | 866 |
| 안내서 (`book.*`) | 1,542 | 9 | 1,023 | 389 |
| 아이템·블록 (`item.*`, `block.*`, 설명 포함) | 1,181 | 133 | 830 | 197 |

한글 포함 수는 번역 완료율이 아니다. 원문과 다른 영어만 남은 항목 등도 있어 표의 세 집계 열의 합계가 전체와 일치하지 않는다. 한국어 파일 자체에는 3,583개 키가 있으며 현재 영어 파일에 없는 키가 117개다. 그중 한글이 있는 8개는 아래 별도 표에 기록한다. 영어 파일과 공통인 한글 포함 항목 389개에 이 8개를 더하면 397개다.

## 핵심 용어와 사용 원칙

`유지`는 기존 표기를 채택한 것이고, `변경 채택`은 기존 표기의 충돌·의미 문제를 해결한 것이며, `신규 채택`은 한국어 이름을 새로 정한 것이다. 모두 확정된 기준이다. 관련 이름·툴팁·안내서·디버그 이름에도 동일한 기준을 적용한다. 앞으로 추가로 발견하는 용어는 현재 원문과 이 기준에 맞춰 문서에 보충한다.

| 영어 개념 | 확인한 기존 표기 | 채택 표기 | 상태 | 근거와 주의점 |
|---|---|---|---|---|
| Foliot | 폴리오트 | 폴리오트 | 유지 | `item.occultism.book_of_binding_foliot`에서 추출. 엔티티 이름 자체는 영어다. |
| Djinni | 정령 / 지니 | 지니 | 변경 채택 | 책 이름 `item.occultism.book_of_binding_djinni`는 정령, 같은 키의 `.tooltip`은 지니. 특정 등급 이름임을 드러내도록 지니로 통일. |
| Afrit | 악령 | 악령 | 유지 | `item.occultism.book_of_binding_afrit`에서 추출. 일반적인 Demon과 혼동하지 않도록 문맥을 구분한다. |
| Marid | 마령 | 마령 | 유지 | `item.occultism.book_of_binding_marid`에서 추출. |
| Spirit | 영혼 / 정신 | 영혼 | 변경 채택 | `occultism.jei.crushing`은 영혼, `debug.occultism.debug_wand.no_spirit_selected`는 정신. 상위 개념이며 Djinni 등 특정 등급과 구분한다. |
| Demon | 단독 용어의 한국어 대응은 미확인 | 악마 | 신규 채택 | 기존 `block.occultism.datura`의 대응은 **Demon's Dream → 악령의 꿈**이다. 이는 식물 이름 전체의 번역이며 Demon 하나를 악령의 꿈으로 번역한 것이 아니다. 안내서 `book.occultism.dictionary_of_spirits.spirits.overview.intro.text`는 Demon을 Spirit의 다른 호칭으로 설명한다. 일반명사는 악마로 옮기되 기존 식물 이름 악령의 꿈은 유지한다. |
| Familiar | 확인한 이름 대응표에는 없음 | 사역마 | 신규 채택 | `item.occultism.familiar_ring`은 영어. 이 저장소 README에서 이미 사역마를 쓰지만, 이는 모드 내 기존 한국어 번역과 구분한다. |
| Book of Binding | 구속의 책 | 구속의 책 | 유지 | 등급별 책 이름에서 추출. |
| Book of Calling | 호출의 책 | 호출의 책 | 유지 | `item.occultism.book_of_calling_foliot_lumberjack` 등에서 추출. |
| Bound / Unbound | 구속 / 구속되지 않은 | 구속 / 구속되지 않은 | 유지 | 구속된 책 이름과 `item.occultism.spawn_egg.afrit_unbound`에서 추출. |
| Summon | 호출 | 소환 | 변경 채택 | 구속된 책 툴팁의 Summon은 소환으로 옮겨 Calling과 구분한다. 아이템 고유명사 호출의 책은 유지한다. |
| Pentacle | 펜타클 | 펜타클 | 유지 | `occultism.jei.pentacle`. 안내서 첫 등장에 의식용 마법진이라는 설명을 덧붙일 수 있다. |
| Ritual / Occult Ritual | 의식 / 오컬트 의식 | 의식 / 오컬트 의식 | 유지 | `ritual.occultism.unknown.started`, `occultism.jei.ritual`. |
| Iesnium | 이스늄 | 이스늄 | 유지 | 광석·괴·가루의 공통 부분에서 추출. |
| Otherstone | 내세석 | 내세석 | 유지 | `block.occultism.otherstone`. |
| Otherworld | 내세나무 (나무 계열 이름) | 장소·속성은 내세, 나무 이름은 내세나무 | 변경 채택 | `block.occultism.otherworld_leaves` 등에서 추출. 모든 Otherworld를 내세나무로 치환하면 도구·장소 이름이 잘못된다. |
| Spiritfire | 영혼 불 | 영혼 불 | 유지 | `block.occultism.spirit_fire`, `occultism.jei.spirit_fire`. |
| Storage Actuator | 저장소 작동기 / 액추에이터 | 저장소 작동기 | 변경 채택 | `block.occultism.storage_controller` 및 `item.occultism.storage_remote.message.linked`. 키의 controller와 영어 표시명 Actuator를 구분한다. |
| Storage Accessor | 저장소 접속기 | 저장소 접속기 | 유지 | `item.occultism.storage_remote`. |
| Storage Stabilizer | 차원 저장소 안정기 | 차원 저장소 안정기 | 유지 | `block.occultism.storage_stabilizer_tier1` 등에서 추출. |
| Tier | 티어 | 티어 | 유지 | 기존 이름의 `1티어`~`4티어` 표기를 따른다. |
| Spirit Attuned | 영혼과 조화된 | 영혼과 조화된 | 유지 | 수정·보석 이름에서 추출. 도구를 블록에 attune하는 조작 문장에는 의미에 맞는 별도 동사를 쓴다. |
| Possessed | 홀린 | 홀린 | 유지 | `item.occultism.spawn_egg.possessed_enderman` 등에서 추출. 의식 이름의 Possession은 빙의로 옮긴다. |
| Wild Hunt | 야생 사냥 | 야생 사냥 | 유지 | `entity.occultism.wild_hunt_skeleton`에서 추출. |
| Machine Operator | 기계 연산기 | 기계 조작자 | 변경 채택 | 2026-09-25 사용자와 역할 확인 후 결정. 직업명과 호출의 책의 합성 이름에도 동일하게 적용한다. |
| Essence Decay | 진액 부패 | 진액 부패 | 유지 | `gui.occultism.spirit.age`. 기존 한국어 파일에서 부식 표기는 발견되지 않았다. 이 현상의 Essence는 진액, Decay는 부패로 통일한다. |
| Lumberjack | 벌목기 | 벌목꾼 | 변경 채택 | `job.occultism.lumberjack`. 벌목을 담당하는 영혼의 역할명. |
| Transporter | 수송기 | 운반꾼 | 변경 채택 | `job.occultism.transport_items`. 아이템 운반을 담당하는 영혼의 역할명. |
| Trader | 거래기 | 상인 | 변경 채택 | `item.occultism.debug_foliot_trader`의 합성 이름에서 추출. 디버그 이름에도 동일하게 적용. |

### 일을 맡긴 영혼과 사역마의 구분

현재 JAR의 안내서는 Lumberjack과 Transporter를 각각 **Foliot Lumberjack**, **Foliot Transporter**로 부르며, 호출의 책으로 작업 위치를 지정하는 영혼으로 설명한다. 벌목과 운반 역할을 맡긴 폴리오트이므로 벌목꾼·운반꾼으로 옮긴다. 근거는 `book.occultism.dictionary_of_spirits.summoning_rituals.summon_lumberjack.intro.title`, 같은 항목의 `book_of_calling.text`, `book.occultism.dictionary_of_spirits.summoning_rituals.summon_transport_items.intro.title` 및 `intro2.text`다.

Familiar(사역마)는 안내서에서 별도 범주로 다룬다. 보통 동물의 몸에 깃들어 소환자에게 강화 효과를 주거나 소환자를 보호하는 영혼이다 (`book.occultism.dictionary_of_spirits.familiar_rituals.overview.intro.text`). 따라서 벌목·운반 영혼을 모두 사역마로 표기하지 않는다.

Machine Operator도 **Djinni Machine Operator**라는 영혼이며, 기계에 재료를 전달하고 결과물을 저장소로 돌려보낸다 (`book.occultism.dictionary_of_spirits.summoning_rituals.summon_manage_machine.intro.title`, 같은 항목의 `intro.text` 및 `book_of_calling.text`). 기계를 관리하는 영혼의 역할을 드러내도록 한국어 이름은 **기계 조작자**로 채택한다.

### 기존 표기를 유지하는 문맥

Miner는 마법 램프에 구속되어 차원 수갱을 통해 일하는 영혼이다 (`book.occultism.dictionary_of_spirits.crafting_rituals.craft_foliot_miner.intro.text`). 램프 아이템 이름은 기존의 **채굴기 폴리오트**, **광석 채굴기 지니**를 사용하고, 본문에서는 채굴을 맡은 영혼임을 설명한다. Crusher 역시 광석을 가루로 만드는 영혼이다 (`book.occultism.dictionary_of_spirits.summoning_rituals.summon_crusher_t1.about_crushers.text`). 기존 기능명 **파쇄기**, **파쇄기 영혼**과 저속·고속·초고속 표기를 유지한다. 이 이름들의 `기`가 기계라는 분류를 뜻하지는 않는다.

Infused Lenses는 폴리오트가 구속된 렌즈다 (`book.occultism.dictionary_of_spirits.crafting_rituals.craft_otherworld_goggles.lenses_spotlight.text`). 기존 이름 **주입된 렌즈**를 유지하고, 본문에 무엇이 주입되었는지 설명한다. Otherworld Wood도 기존 이름 **내세나무 원목**을 유지한다. `block.occultism.otherworld_log`는 별도 키이므로 Wood의 번역을 근거로 Log에 같은 이름을 자동 적용하지 않는다.

## 기존 번역의 통일·수정 결정

아래 결정은 후속 번역에서 관련 이름·설명·태그·안내서에 함께 적용한다.

| 대상 | 기존 표기·문제 | 확정한 처리 | 근거 키 |
|---|---|---|---|
| Djinni 계열 | 이름은 정령, 설명은 지니 | 지니로 통일. 구속의 책·스폰 알·채굴기·호출의 책·엔티티 이름까지 함께 반영 | `item.occultism.book_of_binding_djinni`, `item.occultism.book_of_binding_djinni.tooltip` |
| Spirit 계열 | 영혼과 정신 혼용 | 영혼으로 통일. 날씨 역할은 맑은 날씨를 부르는 영혼 / 비를 부르는 영혼 / 뇌우를 부르는 영혼 | `occultism.jei.crushing`, `debug.occultism.debug_wand.no_spirit_selected`, `job.occultism.clear_weather` |
| Demon’s Dream Fruit | 아이템은 악령의 꿈 열매, 태그는 악령의 꿈 | 열매 항목은 악령의 꿈 열매로 통일 | `item.occultism.datura`, `tag.item.c.crops.datura` |
| Stable Wormhole | 이름은 안정한 웜홀, 메시지는 안정적인 웜홀 | 고유명사 참조는 안정한 웜홀로 통일 | `block.occultism.stable_wormhole`, `block.occultism.stable_wormhole.message.set_storage_controller` |
| Storage Actuator | 작동기와 액추에이터 혼용, `접속기을` 오타 | 저장소 접속기를 저장소 작동기에 연결했습니다. | `item.occultism.storage_remote.message.linked` |
| Storage Actuator Base | 저장소 작동기 기반 | 저장소 작동기 받침대. 작동기를 구성하는 기반 블록의 이름으로 사용 | `block.occultism.storage_controller_base` |
| Crushed End Stone | 부셔진 엔드 돌 | 분쇄된 엔드 돌 | `item.occultism.crushed_end_stone`, `tag.item.c.dusts.end_stone` |
| Tallow | 수지 | 동물성 기름. 수지는 樹脂와 혼동하기 쉬우므로 재료 의미를 명확히 표현 | `item.occultism.tallow`, `tag.item.c.tallow` |
| Lumberjack | 벌목기 | 벌목꾼. 호출의 책과 디버그 이름에도 동일하게 적용 | `job.occultism.lumberjack` |
| Machine Operator | 기계 연산기 | 기계 조작자로 변경 채택. 기계를 관리하는 영혼의 역할을 표현 | `job.occultism.manage_machine` |
| Transporter | 수송기 | 운반꾼 | `job.occultism.transport_items` |
| Miner / Crusher | 채굴기 / 파쇄기 | 기존 채굴기·파쇄기 이름 유지. 영혼이라는 분류는 위 문맥 규칙과 본문 설명에 명시 | `item.occultism.miner_foliot_unspecialized`, `job.occultism.crush_tier2` |
| Divination Rod | 이름은 영어, 설명은 점봉 | 탐지봉. 이름과 연결·공명 설명을 함께 통일 | `item.occultism.divination_rod`, `item.occultism.divination_rod.message.linked_block` |
| Essence Decay | 진액 부패 | 진액 부패 유지. 안내서는 영혼의 몸이 점차 부패하는 현상으로 설명한다. 이 현상에는 진액과 부패를 사용하며 부식과 혼용하지 않음 | `gui.occultism.spirit.age`, `book.occultism.dictionary_of_spirits.spirits.essence_decay.intro.text` |
| Extract Facing / Insert Facing | 대면 추출 / 대면 삽입 | 추출 면 / 삽입 면 | `gui.occultism.book_of_calling.manage_machine.extract`, `gui.occultism.book_of_calling.manage_machine.insert` |
| Crafting Rituals | 한국어 파일에도 영어이며 구버전 표현 Binding Rituals가 남음 | 현재 영어 원문 기준 제작 의식 | `book.occultism.dictionary_of_spirits.rituals.crafting_rituals.name` |

용어 통일과 별개로 설명의 누락·의미 변경도 발견했다. `item.occultism.book_of_calling.message_target_uuid_no_match`의 한국어에는 Shift 클릭으로 구속하는 두 번째 문장이 빠져 있다. `item.occultism.miner_foliot_unspecialized.tooltip`은 원문의 basic ores를 임의의 블록으로 옮겼다. 본문 번역 단계에서 현재 영어 원문을 기준으로 수정한다.

## 한국어 이름이 없던 주요 항목의 채택 표기

아래 기존 값은 모두 현재 JAR에서 확인했다. 채택한 새 이름은 기존 한국어 번역 실적으로 계산하지 않는다.

| 영어 원문 | 현재 한국어 파일 값 | 채택 표기 | 근거 키 |
|---|---|---|---|
| Dictionary of Spirits | Dictionary of Spirits | 영혼 사전 | `book.occultism.dictionary_of_spirits.name` |
| Foliot | Foliot | 폴리오트 — 기존 책 이름에서 가져옴 | `entity.occultism.foliot` |
| Djinni | Djinni | 지니 | `entity.occultism.djinni` |
| Afrit | Afrit | 악령 — 기존 책 이름에서 가져옴 | `entity.occultism.afrit` |
| Marid | Marid | 마령 — 기존 책 이름에서 가져옴 | `entity.occultism.marid` |
| Familiar Ring | Familiar Ring | 사역마 반지 | `item.occultism.familiar_ring` |
| Divination Rod | Divination Rod | 탐지봉 | `item.occultism.divination_rod` |
| Otherworld Goggles | Otherworld Goggles | 내세 고글 | `item.occultism.otherworld_goggles` |
| The Third Eye | The Third Eye | 제3의 눈 | `book.occultism.dictionary_of_spirits.getting_started.third_eye.name` |
| True Names | True Names | 진명 | `book.occultism.dictionary_of_spirits.spirits.true_names.name` |
| Possession Rituals | Possession Rituals | 빙의 의식 | `book.occultism.dictionary_of_spirits.rituals.possession_rituals.name` |

## 번역 중 추가한 공통 이름

2026-09-25 번역 과정에서 추가한 이름이다. 확정 용어집의 원칙에 따라 Codex가 원문을 확인하고 세 번역 담당자에게 같은 표기를 전달했다. 아래 대표 키 외에도 영어 표시명이 정확히 같은 항목에는 같은 한국어 이름을 사용한다.

| 영어 표시명 | 채택 표기 | 대표 근거 키 |
|---|---|---|
| Items | 아이템 | `occultism.configuration.items` |
| Divination c:ores | c:ores 광석 탐지 | `occultism.configuration.anyOreDivinationRod` |
| Uses | 용도 | `book.occultism.dictionary_of_spirits.getting_started.iesnium.uses.title` |
| Devil Familiar | 마귀 사역마 | `entity.occultism.devil_familiar` |
| Drikwing Familiar | 드릭윙 사역마 | `entity.occultism.drikwing_familiar` |
| Wingnis Familiar | 윙니스 사역마 | `entity.occultism.wingnis_familiar` |
| Headless Ratman Familiar | 머리 없는 쥐인간 사역마 | `book.occultism.dictionary_of_spirits.familiar_rituals.familiar_headless.name` |
| Dimensional Matrix | 차원 수정 모체 | `book.occultism.dictionary_of_spirits.crafting_rituals.craft_dimensional_matrix.name` |
| Fracture Soul | 영혼 분쇄 | `enchantment.occultism.fracture_soul` |
| Knowledge Tablet | 지식의 석판 | `item.occultism.knowledge_tablet` |
| Wormhole Tablet | 웜홀 석판 | `item.occultism.wormhole_tablet` |
| Familiar Tablet | 사역마 석판 | `item.occultism.familiar_tablet` |
| Vitality Compass | 생명력 나침반 | `item.occultism.vitality_compass` |
| Trinity Gem | 삼위일체 보석 | `item.occultism.trinity_gem` |
| True Sight Staff | 진실의 시야 지팡이 | `item.occultism.true_sight_staff` |
| Gray Paste | 회색 반죽 | `item.occultism.gray_paste` |
| Flaming Paste | 불꽃 반죽 | `item.occultism.flaming_paste` |
| Nature Paste | 자연 반죽 | `item.occultism.nature_paste` |
| Wild Evoker | 야생 소환사 | `entity.occultism.possessed_evoker` |
| Afrit Essence | 악령의 진액 | `item.occultism.afrit_essence` |
| Marid Essence | 마령의 진액 | `item.occultism.marid_essence` |
| Demon's Dream Essence | 악령의 꿈 진액 | `item.occultism.demons_dream_essence` |
| Otherworld Essence | 내세 진액 | `item.occultism.otherworld_essence` |
| Cruelty Essence | 잔혹의 진액 | `item.occultism.cruelty_essence` |
| Aviar's Circle | 아비아르의 원 | `multiblock.occultism.summon_foliot` |
| Ophyx' Calling | 오픽스의 부름 | `multiblock.occultism.summon_djinni` |
| Abras' Conjure | 아브라스의 강령 | `multiblock.occultism.summon_afrit` |
| Fatma's Incentivized Attraction | 파트마의 보상 유인 | `multiblock.occultism.summon_marid` |
| Kandar's Opened Conjure | 칸다르의 열린 강령 | `multiblock.occultism.summon_unbound_afrit` |
| Kandar's Open Conjure | 칸다르의 열린 강령 | `book.occultism.dictionary_of_spirits.pentacles.summon_unbound_afrit.intro.title` |
| Tibira's Attraction | 티비라의 유인 | `multiblock.occultism.summon_unbound_marid` |
| Eziveus' Spectral Compulsion | 에지베우스의 유령 강제 | `multiblock.occultism.craft_foliot` |
| Strigeor's Higher Binding | 스트리게오르의 상위 구속 | `multiblock.occultism.craft_djinni` |
| Sevira's Permanent Confinement | 세비라의 영구 감금 | `multiblock.occultism.craft_afrit` |
| Uphyxes Inverted Tower | 우픽세스의 거꾸로 선 탑 | `multiblock.occultism.craft_marid` |
| Hedyrin's Lure | 헤디린의 유혹 | `multiblock.occultism.possess_foliot` |
| Ihagan's Enthrallment | 이하간의 매혹 | `multiblock.occultism.possess_djinni` |
| Posuc's Convocation | 포수크의 소집 | `multiblock.occultism.possess_afrit` |
| Xeovrenth Adjure | 제오브렌스의 명령 | `multiblock.occultism.possess_marid` |
| Odus' Open Convocation | 오두스의 열린 소집 | `multiblock.occultism.possess_unbound_afrit` |
| Susje's Simple Circle | 수스예의 단순한 원 | `multiblock.occultism.resurrect_spirit` |
| Ronaza's Contact | 로나자의 접촉 | `multiblock.occultism.contact_eldritch_spirit` |
| Osorin's Unbound Calling | 오소린의 해방된 부름 | `multiblock.occultism.contact_wild_spirit` |
| Golden Ritual Bowl | 황금 의식 그릇 | `block.occultism.golden_sacrificial_bowl` |
| Book of Binding: Empty | 구속의 책: 빈 책 | `item.occultism.book_of_binding_empty` |
| Awakened Feather | 각성한 깃털 | `item.occultism.awakened_feather` |
| Purified Ink | 정화된 잉크 | `item.occultism.purified_ink` |
| Taboo Book | 금기의 책 | `item.occultism.taboo_book` |
| Otherworld Log | 내세나무 통나무 | `block.occultism.otherworld_log` |
| Otherrock | 내세암 | `block.occultism.otherrock` |
| Othercobblestone | 내세 조약돌 | `block.occultism.othercobblestone` |
| Othercobblerock | 내세 조약암 | `block.occultism.othercobblerock` |
| Otherglass | 내세 유리 | `block.occultism.otherglass` |
| Smelter | 제련기 | `job.occultism.smelt_tier2` |
| Crystallizer | 결정화기 | `job.occultism.crystal_tier2` |
| Janitor | 청소부 | `job.occultism.cleaner` |
| Farmer | 농부 | `job.occultism.farmer` |
| Infusion Rituals | 주입 의식 | `book.occultism.dictionary_of_spirits.getting_started.crafting_rituals.intro.title` |
| Binding Rituals | 구속 의식 | `book.occultism.dictionary_of_spirits.crafting_rituals.name` |
| Summoning Rituals | 소환 의식 | `book.occultism.dictionary_of_spirits.getting_started.summoning_rituals.intro.title` |
| Familiar Rituals | 사역마 의식 | `book.occultism.dictionary_of_spirits.familiar_rituals.name` |
| Soul Gem | 영혼 보석 | `item.occultism.soul_gem` |
| Apprentice Ritual Satchel | 견습생의 의식 가방 | `item.occultism.ritual_satchel_t1` |
| Artisanal Ritual Satchel | 장인의 의식 가방 | `item.occultism.ritual_satchel_t2` |

장소 고유명사 The Other Place는 **저편**으로 쓴다. Drikwing / Wingnis는 **드릭윙 / 윙니스**로 음역한다.

합성어 규칙: Infused는 **주입된**, Eldritch는 형용사로 **섬뜩한**, 영혼을 가리킬 때 **섬뜩한 영혼**으로 쓴다. Mining Dimension은 **채굴 차원**, Miner Spirit은 **채굴기 영혼**, Ritual Satchel은 **의식 가방**, Otherworld Grove는 **내세 숲**, Wild Spirits는 **야생 영혼**으로 쓴다. Apprentice / Artisanal은 가방 이름에서 **견습생의 / 장인의**로 옮긴다. 단독 이름이 아닌 구절에도 이 규칙을 적용한다.

## 번역 문체와 형식 규칙

1. 아이템·블록·생물 이름은 명사형으로 쓴다. 안내서와 툴팁 설명은 `~합니다`, 행동 지시는 `~하세요`로 쓴다. 부정·조건·수량·시간·단계를 빠뜨리지 않는다.
2. 고유명사는 이 용어집을 먼저 확인한다. 새 고유명사는 임시 음역과 이유를 기록한 뒤 일관되게 사용한다. 바닐라 이름은 대상 Minecraft 버전의 한국어 표시명을 확인한다. 기존 표를 검증 없이 바닐라 표준으로 간주하지 않는다.
3. 같은 아이템을 가리키는 안내서 링크 제목과 툴팁은 해당 아이템의 채택 이름을 쓴다. 처음 나오는 생소한 용어는 필요하면 영어 이름이나 짧은 뜻풀이를 병기한다.
4. 조작 설명은 `우클릭`, `Shift + 우클릭`, `Shift를 누른 채 스크롤`처럼 행동이 분명한 표현을 쓴다. 원문의 실제 조작과 기본키·변경 가능한 단축키 여부를 확인한다.
5. JSON 키, 아이템·엔티티 ID, `item://`, `entry://` 등의 링크 대상, 색상 코드, 서식 제어 구문은 보존한다. Modonomicon 링크의 표시 텍스트만 번역한다. 구조를 바꾸지 않고 원문과 대조한다.
6. `%s`, `%d`, `%%`, 번호가 붙은 치환자 등은 수·타입·대응 관계를 보존한다. 한국어 어순 때문에 위치를 바꿔야 하면 해당 서식 기능을 확인하고 명시적 인덱스를 사용한다. 순서를 무작정 바꾸지 않는다.
7. 현재 `en_us.json`을 의미와 키 목록의 기준으로 쓴다. `ko_kr.json`에 영어가 있거나 원문과 다르면 최신 의미와 대조한다. 기존 영어와 다른 문자열이라고 해서 번역 완료로 처리하지 않는다.
8. 용어 변경은 부분 문자열 일괄 치환으로 처리하지 않는다. 예를 들어 Demon’s Dream의 악령과 등급 Afrit의 악령은 서로 다른 근거를 가진다. Otherworld도 재료·나무·장소 문맥을 구분한다.

## 후속 작업과 완료 기준

| 순서 | 작업 | 상태 | 완료 기준 |
|---|---|---|---|
| 1 | 기존 용어 조사 | 완료 | 근거 키로 영어·한국어를 재확인하고 기존 표기와 채택 표기를 구분 |
| 2 | 용어 기준 확정 | 완료 | 사용자 결정 반영, 문맥별 규칙과 관련 키 기록 |
| 3 | 이름·툴팁·화면 문구 번역 | 완료 | 아이템 이름과 설명에서 같은 대상에 같은 표기 사용 |
| 4 | 안내서 번역 | 완료 | 안내서 1,542개 키 번역, 원문 구조와 채택 표기 검사 |
| 5 | 리소스팩 제작·검증 | 제작·정적 검증 완료 / 게임 화면 확인 대기 | 대상 버전 형식, JSON 중복 키·문법, 누락 키, 치환자, 링크·서식 보존 검사 완료 |

용어·설계·검증은 Codex가 담당한다. 실제 번역 리소스와 팩 생성·배포 코드의 구현은 저장소 [작업 규칙](../AGENTS.md)에 따라 Orca orchestration으로 Claude에게 위임한다. 게임에서는 한국어 선택과 리소스팩 적용 후 안내서 링크, 아이템 이름, 치환값, 글자 잘림을 확인해야 한다. 현재 단계는 JAR 정적 대조이며 런타임 검증은 수행하지 않았다.

## 기존 이름 대응표

아래 표의 영어 원문·기존 한국어 열은 JAR에 있는 값을 그대로 옮긴다. 기존 오타도 보존한다. **채택 표기** 열이 번역 작업에 사용할 확정 값이다. `유지`와 `변경 채택`은 기존 번역과의 차이를 나타낸다.

추출 범위는 아이템·블록·엔티티·효과의 직접 이름, 스폰 알, 태그, 영혼의 직업명, JEI/EMI 분류명, 한글이 포함된 안내서 제목·짧은 설명, 분필·음차 자막 이름이다. 일반 알림 문장·방향·설정 동사는 이름 표에서 제외하고 필요한 문장 속 개념은 위의 핵심 용어·수정 결정 표에 기록했다.

**135개 키, 중복을 묶은 105개 영어–한국어 대응쌍.**

| 영어 원문 | 기존 한국어 | 채택 표기 | 상태 | 근거 키 |
|---|---|---|---|---|
| Afrit Spawn Egg | 악령 스폰 알 | 악령 스폰 알 | 유지 | `item.occultism.spawn_egg.afrit` |
| Block of Iesnium | 이스늄 블록 | 이스늄 블록 | 유지 | `block.occultism.iesnium_block` |
| Block of Silver | 은 블록 | 은 블록 | 유지 | `block.occultism.silver_block` |
| Book of Binding: Afrit | 구속의 책: 악령 | 구속의 책: 악령 | 유지 | `item.occultism.book_of_binding_afrit` |
| Book of Binding: Afrit (Bound) | 구속의 책: 악령 (구속) | 구속의 책: 악령 (구속) | 유지 | `item.occultism.book_of_binding_bound_afrit` |
| Book of Binding: Djinni | 구속의 책: 정령 | 구속의 책: 지니 | 변경 채택 | `item.occultism.book_of_binding_djinni` |
| Book of Binding: Djinni (Bound) | 구속의 책: 정령 (구속) | 구속의 책: 지니 (구속) | 변경 채택 | `item.occultism.book_of_binding_bound_djinni` |
| Book of Binding: Foliot | 구속의 책: 폴리오트 | 구속의 책: 폴리오트 | 유지 | `item.occultism.book_of_binding_foliot` |
| Book of Binding: Foliot (Bound) | 구속의 책: 폴리오트 (구속) | 구속의 책: 폴리오트 (구속) | 유지 | `item.occultism.book_of_binding_bound_foliot` |
| Book of Binding: Marid | 구속의 책: 마령 | 구속의 책: 마령 | 유지 | `item.occultism.book_of_binding_marid` |
| Book of Binding: Marid (Bound) | 구속의 책: 마령 (구속) | 구속의 책: 마령 (구속) | 유지 | `item.occultism.book_of_binding_bound_marid` |
| Book of Calling: Djinni Machine Operator | 호출의 책: 정령 기계 연산기 | 호출의 책: 지니 기계 조작자 | 변경 채택 | `item.occultism.book_of_calling_djinni_manage_machine` |
| Book of Calling: Foliot Lumberjack | 호출의 책: 폴리오트 벌목기 | 호출의 책: 폴리오트 벌목꾼 | 변경 채택 | `item.occultism.book_of_calling_foliot_lumberjack` |
| Book of Calling: Foliot Transporter | 호출의 책: 폴리오트 수송기 | 호출의 책: 폴리오트 운반꾼 | 변경 채택 | `item.occultism.book_of_calling_foliot_transport_items` |
| Burnt Otherstone | 탄 내세석 | 탄 내세석 | 유지 | `item.occultism.burnt_otherstone` |
| Butcher Knife | 도살자 칼 | 도살자 칼 | 유지 | `item.occultism.butcher_knife` |
| Chalk | 분필 | 분필 | 유지 | `occultism.subtitle.chalk` |
| Chalk Brush | 분필 붓 | 분필 붓 | 유지 | `item.occultism.brush` |
| Copper Dust | 구리 가루 | 구리 가루 | 유지 | `item.occultism.copper_dust`<br>`tag.item.c.dusts.copper` |
| Crushed End Stone | 부셔진 엔드 돌 | 분쇄된 엔드 돌 | 변경 채택 | `item.occultism.crushed_end_stone`<br>`tag.item.c.dusts.end_stone` |
| Crusher | 파쇄기 | 파쇄기 | 유지 | `job.occultism.crush_tier2` |
| Crusher Spirit | 파쇄기 영혼 | 파쇄기 영혼 | 유지 | `occultism.jei.crushing` |
| Debug Miner | 디버그 채굴기 | 디버그 채굴기 | 유지 | `item.occultism.miner_debug_unspecialized` |
| Debug Wand | 디버그 지팡이 | 디버그 지팡이 | 유지 | `item.occultism.debug_wand` |
| Demon's Dream | 악령의 꿈 | 악령의 꿈 | 유지 | `block.occultism.datura` |
| Demon's Dream Fruit | 악령의 꿈 | 악령의 꿈 열매 | 변경 채택 | `tag.item.c.crops.datura` |
| Demon's Dream Fruit | 악령의 꿈 열매 | 악령의 꿈 열매 | 유지 | `item.occultism.datura` |
| Demon's Dream Seeds | 악령의 꿈 씨앗 | 악령의 꿈 씨앗 | 유지 | `block.occultism.datura_seeds`<br>`tag.item.c.seeds.datura` |
| Dimensional Crystal Matrix | 차원 수정 모체 | 차원 수정 모체 | 유지 | `item.occultism.dimensional_matrix` |
| Dimensional Mineshaft | 차원 수갱 | 차원 수갱 | 유지 | `block.occultism.dimensional_mineshaft`<br>`book.occultism.dictionary_of_spirits.crafting_rituals.craft_dimensional_mineshaft.name`<br>`book.occultism.dictionary_of_spirits.getting_started.mineshaft.name`<br>`emi.category.occultism.miner`<br>`occultism.jei.miner` |
| Dimensional Storage Actuator | 차원 저장소 작동기 | 차원 저장소 작동기 | 유지 | `block.occultism.storage_controller` |
| Djinni Spawn Egg | 정령 스폰 알 | 지니 스폰 알 | 변경 채택 | `item.occultism.spawn_egg.djinni` |
| Empty Magic Lamp | 빈 마법 램프 | 빈 마법 램프 | 유지 | `item.occultism.magic_lamp_empty` |
| Empty Soul Gem | 빈 영혼 보석 | 빈 영혼 보석 | 유지 | `item.occultism.soul_gem_empty` |
| Fast Crusher | 고속 파쇄기 | 고속 파쇄기 | 유지 | `job.occultism.crush_tier3` |
| Foliot Spawn Egg | 폴리오트 스폰 알 | 폴리오트 스폰 알 | 유지 | `item.occultism.spawn_egg.foliot` |
| Glass Lenses | 유리 렌즈 | 유리 렌즈 | 유지 | `item.occultism.lenses` |
| Gold Dust | 금 가루 | 금 가루 | 유지 | `item.occultism.gold_dust`<br>`tag.item.c.dusts.gold` |
| Iesnium Dust | 이스늄 가루 | 이스늄 가루 | 유지 | `item.occultism.iesnium_dust`<br>`tag.item.c.dusts.iesnium` |
| Iesnium Ingot | 이스늄괴 | 이스늄괴 | 유지 | `item.occultism.iesnium_ingot`<br>`tag.item.c.ingots.iesnium` |
| Iesnium Nugget | 이스늄 조각 | 이스늄 조각 | 유지 | `item.occultism.iesnium_nugget`<br>`tag.item.c.nuggets.iesnium` |
| Iesnium Ore | 이스늄 광석 | 이스늄 광석 | 유지 | `block.occultism.iesnium_ore`<br>`book.occultism.dictionary_of_spirits.getting_started.iesnium.name`<br>`tag.block.c.ores.iesnium`<br>`tag.item.c.ores.iesnium` |
| Impure Purple Chalk | 불순한 보라색 분필 | 불순한 보라색 분필 | 유지 | `item.occultism.chalk_purple_impure` |
| Impure Red Chalk | 불순한 빨간색 분필 | 불순한 빨간색 분필 | 유지 | `item.occultism.chalk_red_impure` |
| Impure White Chalk | 불순한 하얀색 분필 | 불순한 하얀색 분필 | 유지 | `item.occultism.chalk_white_impure` |
| Inert Storage Accessor | 비활성 저장소 접속기 | 비활성 저장소 접속기 | 유지 | `item.occultism.storage_remote_inert` |
| Infused Lenses | 주입된 렌즈 | 주입된 렌즈 | 유지 | `item.occultism.infused_lenses` |
| Iron Dust | 철 가루 | 철 가루 | 유지 | `item.occultism.iron_dust`<br>`tag.item.c.dusts.iron` |
| Lens Frame | 렌즈 틀 | 렌즈 틀 | 유지 | `item.occultism.lens_frame` |
| Lumberjack | 벌목기 | 벌목꾼 | 변경 채택 | `job.occultism.lumberjack` |
| Machine Operator | 기계 연산기 | 기계 조작자 | 변경 채택 | `job.occultism.manage_machine` |
| Miner Foliot | 채굴기 폴리오트 | 채굴기 폴리오트 | 유지 | `item.occultism.miner_foliot_unspecialized` |
| Multi Jump | 다중 점프 | 다중 점프 | 유지 | `effect.occultism.double_jump` |
| Obsidian Dust | 흑요석 가루 | 흑요석 가루 | 유지 | `item.occultism.obsidian_dust` |
| Occult Ritual | 오컬트 의식 | 오컬트 의식 | 유지 | `occultism.jei.ritual` |
| Ore Miner Djinni | 광석 채굴기 정령 | 광석 채굴기 지니 | 변경 채택 | `item.occultism.miner_djinni_ores` |
| Otherstone | 내세석 | 내세석 | 유지 | `block.occultism.otherstone`<br>`tag.item.occultism.otherstone` |
| Otherstone Frame | 내세석 틀 | 내세석 틀 | 유지 | `item.occultism.otherstone_frame` |
| Otherstone Pedestal | 내세석 받침대 | 내세석 받침대 | 유지 | `block.occultism.otherstone_pedestal` |
| Otherstone Slab | 내세석 반 블록 | 내세석 반 블록 | 유지 | `block.occultism.otherstone_slab` |
| Otherworld Ashes | 내세나무 재 | 내세나무 재 | 유지 | `item.occultism.otherworld_ashes` |
| Otherworld Leaves | 내세나무 잎 | 내세나무 잎 | 유지 | `block.occultism.otherworld_leaves` |
| Otherworld Sapling | 내세나무 묘목 | 내세나무 묘목 | 유지 | `block.occultism.otherworld_sapling`<br>`item.occultism.otherworld_sapling` |
| Otherworld Wood | 내세나무 원목 | 내세나무 원목 | 유지 | `block.occultism.otherworld_wood` |
| Pentacle | 펜타클 | 펜타클 | 유지 | `occultism.jei.pentacle` |
| Possessed Enderman Spawn Egg | 홀린 엔더맨 스폰 알 | 홀린 엔더맨 스폰 알 | 유지 | `item.occultism.spawn_egg.possessed_enderman` |
| Possessed Endermite Spawn Egg | 홀린 엔더마이트 스폰 알 | 홀린 엔더마이트 스폰 알 | 유지 | `item.occultism.spawn_egg.possessed_endermite` |
| Possessed Skeleton Spawn Egg | 홀린 스켈레톤 스폰 알 | 홀린 스켈레톤 스폰 알 | 유지 | `item.occultism.spawn_egg.possessed_skeleton` |
| Purple Chalk | 보라색 분필 | 보라색 분필 | 유지 | `book.occultism.dictionary_of_spirits.pentacles.purple_chalk.description`<br>`item.occultism.chalk_purple` |
| Rainy Weather Spirit | 우천 정신 | 비를 부르는 영혼 | 변경 채택 | `job.occultism.rain_weather` |
| Red Chalk | 빨간색 분필 | 빨간색 분필 | 유지 | `book.occultism.dictionary_of_spirits.pentacles.red_chalk.description`<br>`item.occultism.chalk_red` |
| Sacrificial Bowl | 제물 그릇 | 제물 그릇 | 유지 | `block.occultism.sacrificial_bowl` |
| Silver Dust | 은 가루 | 은 가루 | 유지 | `item.occultism.silver_dust`<br>`tag.item.c.dusts.silver` |
| Silver Ingot | 은괴 | 은괴 | 유지 | `item.occultism.silver_ingot`<br>`tag.item.c.ingots.silver` |
| Silver Nugget | 은 조각 | 은 조각 | 유지 | `item.occultism.silver_nugget`<br>`tag.item.c.nuggets.silver` |
| Silver Ore | 은 광석 | 은 광석 | 유지 | `block.occultism.silver_ore`<br>`tag.block.c.ores.silver`<br>`tag.item.c.ores.silver` |
| Slow Crusher | 저속 파쇄기 | 저속 파쇄기 | 유지 | `job.occultism.crush_tier1` |
| Spirit Attuned Crystal | 영혼과 조화된 수정 | 영혼과 조화된 수정 | 유지 | `block.occultism.spirit_attuned_crystal` |
| Spirit Attuned Gem | 영혼과 조화된 보석 | 영혼과 조화된 보석 | 유지 | `item.occultism.spirit_attuned_gem` |
| Spiritfire | 영혼 불 | 영혼 불 | 유지 | `block.occultism.spirit_fire`<br>`occultism.jei.spirit_fire` |
| Stable Wormhole | 안정한 웜홀 | 안정한 웜홀 | 유지 | `block.occultism.stable_wormhole`<br>`book.occultism.dictionary_of_spirits.crafting_rituals.craft_stable_wormhole.name`<br>`book.occultism.dictionary_of_spirits.storage.craft_stable_wormhole.name` |
| Storage Accessor | 저장소 접속기 | 저장소 접속기 | 유지 | `item.occultism.storage_remote` |
| Storage Actuator Base | 저장소 작동기 기반 | 저장소 작동기 받침대 | 변경 채택 | `block.occultism.storage_controller_base`<br>`book.occultism.dictionary_of_spirits.crafting_rituals.craft_storage_controller_base.name` |
| Summon Debug Djinni Manage Machine | 디버그 호출 정령 관리기 | 디버그 소환 지니 기계 조작자 | 변경 채택 | `item.occultism.debug_djinni_manage_machine` |
| Summon Debug Djinni Test | 디버그 호출 정령 테스트 | 디버그 소환 지니 테스트 | 변경 채택 | `item.occultism.debug_djinni_test` |
| Summon Debug Foliot Lumberjack | 디버그 호출 폴리오트 벌목기 | 디버그 소환 폴리오트 벌목꾼 | 변경 채택 | `item.occultism.debug_foliot_lumberjack` |
| Summon Debug Foliot Trader | 디버그 호출 폴리오트 거래기 | 디버그 소환 폴리오트 상인 | 변경 채택 | `item.occultism.debug_foliot_trader` |
| Summon Debug Foliot Transporter | 디버그 호출 폴리오트 수송기 | 디버그 소환 폴리오트 운반꾼 | 변경 채택 | `item.occultism.debug_foliot_transport_items` |
| Sunshine Spirit | 맑음 정신 | 맑은 날씨를 부르는 영혼 | 변경 채택 | `job.occultism.clear_weather` |
| Tallow | 수지 | 동물성 기름 | 변경 채택 | `item.occultism.tallow`<br>`tag.item.c.tallow` |
| Thunderstorm Spirit | 폭풍 정신 | 뇌우를 부르는 영혼 | 변경 채택 | `job.occultism.thunder_weather` |
| Tier 1 Dimensional Storage Stabilizer | 1티어 차원 저장소 안정기 | 1티어 차원 저장소 안정기 | 유지 | `block.occultism.storage_stabilizer_tier1` |
| Tier 2 Dimensional Storage Stabilizer | 2티어 차원 저장소 안정기 | 2티어 차원 저장소 안정기 | 유지 | `block.occultism.storage_stabilizer_tier2` |
| Tier 3 Dimensional Storage Stabilizer | 3티어 차원 저장소 안정기 | 3티어 차원 저장소 안정기 | 유지 | `block.occultism.storage_stabilizer_tier3` |
| Tier 4 Dimensional Storage Stabilizer | 4티어 차원 저장소 안정기 | 4티어 차원 저장소 안정기 | 유지 | `block.occultism.storage_stabilizer_tier4` |
| Transporter | 수송기 | 운반꾼 | 변경 채택 | `job.occultism.transport_items` |
| Tuning Fork | 음차 | 음차 | 유지 | `occultism.subtitle.tuning_fork` |
| Unbound Afrit Spawn Egg | 구속되지 않은 악령 스폰 알 | 구속되지 않은 악령 스폰 알 | 유지 | `item.occultism.spawn_egg.afrit_unbound` |
| Unstable Otherworld Sapling | 불안정한 내세나무 묘목 | 불안정한 내세나무 묘목 | 유지 | `item.occultism.otherworld_sapling_natural` |
| Very Fast Crusher | 초고속 파쇄기 | 초고속 파쇄기 | 유지 | `job.occultism.crush_tier4` |
| White Chalk | 하얀색 분필 | 하얀색 분필 | 유지 | `book.occultism.dictionary_of_spirits.pentacles.white_chalk.description`<br>`item.occultism.chalk_white` |
| Wild Hunt Skeleton | 야생 사냥 스켈레톤 | 야생 사냥 스켈레톤 | 유지 | `entity.occultism.wild_hunt_skeleton` |
| Wild Hunt Skeleton Spawn Egg | 야생 사냥 스켈레톤 스폰 알 | 야생 사냥 스켈레톤 스폰 알 | 유지 | `item.occultism.spawn_egg.wild_hunt_skeleton` |
| Wild Hunt Wither Skeleton | 야생 사냥 위더 스켈레톤 | 야생 사냥 위더 스켈레톤 | 유지 | `entity.occultism.wild_hunt_wither_skeleton` |
| Wild Hunt Wither Skeleton Spawn Egg | 야생 사냥 위더 스켈레톤 스폰 알 | 야생 사냥 위더 스켈레톤 스폰 알 | 유지 | `item.occultism.spawn_egg.wild_hunt_wither_skeleton` |


## 현재 영어 파일에 대응 키가 없는 한국어 항목

현재 영어 파일에서 이름을 검증할 수 없으므로 번역 완료나 활성 용어 수에 포함하지 않는다. 이 목록만으로 게임에서 사용되지 않는다고 단정하지 않으며, 후속 작업에서 키의 사용 여부를 확인한다. 특히 `otherworld_bird`의 드리큉을 새 `drikwing` 키로 자동 이식하지 않는다.

| 한국어 파일 키 | 기존 한국어 | 현재 영어 원문 |
|---|---|---|
| `entity.occultism.afrit_wild` | 구속되지 않은 악령 | 대응 키 없음 |
| `entity.occultism.otherworld_bird` | 드리큉 | 대응 키 없음 |
| `item.occultism.spawn_egg.otherworld_bird` | 드리큉 스폰 알 | 대응 키 없음 |
| `item.occultism.spirit_attuned_pickaxe_head` | 영혼과 조화된 곡괭이 머리 | 대응 키 없음 |
| `ritual.occultism.familiar_otherworld_bird.conditions` | 이 의식의 모든 요구사항이 충족되는 것은 아닙니다. | 대응 키 없음 |
| `ritual.occultism.possess_unbound_otherworld_bird.conditions` | 이 의식의 모든 요구사항이 충족되는 것은 아닙니다. | 대응 키 없음 |
| `ritual.occultism.possess_unbound_parrot.conditions` | 이 의식의 모든 요구사항이 충족되는 것은 아닙니다. | 대응 키 없음 |
| `ritual.occultism.possess_zombie_piglin.conditions` | 이 의식의 모든 요구사항이 충족되는 것은 아닙니다. | 대응 키 없음 |

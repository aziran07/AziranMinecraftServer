# Occultism 한국어 번역 작업

## 범위와 기준

기본 번역은 Minecraft 26.3 / Occultism 1.256.0의 영어 키 4,332개 전체를 대상으로 한다.
후속 확장은 안내서 누락 문자열 9개와 Modonomicon 2.7.0의 영어 키 309개를 포함한다.
[확정 용어집](OCCULTISM_KO_GLOSSARY.md)을 적용해 기존 한국어도 현재 원문과 대조한다.
결과물은 한국어를 선택한 클라이언트에 적용할 독립 리소스팩이다.
모드 JAR, 서버 설정·월드, 공개 다운로드와 기존 배포 팩은 변경 범위에 포함하지 않는다.

기준 JAR: `server-data-26.3-neoforge/mods/occultism-26.3-neoforge-1.256.0.jar`.
SHA-256: `118d02366adffbd8ebbe0024f484c88d8720eff43fb70b1adfd7d0fde74ddb51`.
원문 경로: `assets/occultism/lang/en_us.json`.
기존 한국어: `assets/occultism/lang/ko_kr.json`.
현재 영어에 없는 구버전 키는 새 팩에 포함하지 않는다. 단, 현재 안내서 페이지에서 실제 참조하는
누락 키와 언어 파일 밖의 본문은 아래의 확장 범위에 따라 별도로 검증한다.

## 안내서 및 Modonomicon 번역 확장 (2026-09-25)

사용자 화면에서 내세나무 묘목·통나무 제목만 한국어이고 본문은 영어인 문제가 확인됐다.
기존 검증은 `en_us.json`의 4,332개 키만 대상으로 삼아, 페이지 JSON에 직접 적힌 영어를 놓쳤다.
기존 16개 테스트가 통과해도 이 문제는 발견되지 않았다.

확장 범위와 구현 전 검증 기준:

- Occultism의 `data/occultism/modonomicon/books/**/*.json`에 있는 `text`, `title`,
  `name`, `description` 값을 언어 파일과 대조한다. 원문에 없는 문자열은 정확히 9개다.
- 직접 적힌 영어 본문 5개: 내세나무 묘목, 통나무, 자연산 변종, Otherstone, Otherrock.
  `translations/occultism/ko_kr/book_overrides.json`에 원문 문자열을 **마지막 개행까지 그대로**
  키로 삼아 한국어를 넣는다.
- 같은 파일에서 원문에 빠진 키 4개도 보완한다. 엔더맨·엔더마이트·가스트 빙의 설명 제목은
  해당 항목 이름의 기존 번역을 사용한다. `craft_eldritch_chalice.ritual2.text`는 연결된
  `misc_celestial_chalice` 제작법의 실제 결과물을 바탕으로 짧은 제작 의식 설명을 넣는다.
  이는 없는 영어 문장을 추측해 번역하는 것이 아니라, 확인한 페이지 맥락으로 누락 표기를 보완하는 결정이다.
- Modonomicon 2.7.0의 영어 키 309개 전체를 `translations/modonomicon/ko_kr.json`에 번역한다.
  버튼·검색·북마크·설정·명령·연구 알림·예제 안내서를 포함한다. 브랜드·기호·순수 서식은 보존한다.
  예제의 크기 조정용 Lorem ipsum, 코드 식별자, 로그 검색용 원문 문구도 용도에 맞게 보존한다.
  기준 JAR은 `server-data-26.3-neoforge/mods/modonomicon-26.3-neoforge-2.7.0.jar`,
  SHA-256은 `27e1ca11f161012cc95c114beb5b58a96081d189857301c0d8a93466a4ad370a`다.
- 기존 ZIP 파일명과 활성화 ID를 유지하고, 그 안에 Occultism 4,341개 키와
  `assets/modonomicon/lang/ko_kr.json` 309개 키를 담는다. 기존 클라이언트 빌더도 같은 ZIP을 포함한다.
- 추가 입력도 고정 JAR·정확한 키 집합·중복·문자열 타입을 확인한다. 빌드는 오프라인·결정적·원자적으로
  수행하고 실패하면 기존 ZIP을 유지한다. 치환자·링크·서식 코드 보존과 실제 한국어 여부를 검사한다.
- 자동 검증은 `tests/test_book_translation.py`와 기존 번역·클라이언트 팩 검사로 수행한다.
  실제 게임 화면에서 줄바꿈·글자 잘림까지 확인한 것으로 보고하지 않는다.

[Modonomicon의 BookTextHolder 소스](https://github.com/klikli-dev/modonomicon/blob/version/26.3/common/src/main/java/com/klikli_dev/modonomicon/book/BookTextHolder.java)는
일반 문자열도 `I18n.get(this.string)`으로 조회한다. 따라서 원문 문장 자체를 언어 키로 추가하면 된다.
설치된 2.7.0 JAR의 `BookTextHolder.class`도 독립적으로 읽어 `getString()`의 일반 문자열 분기에서
`I18n.get(String, Object[])` 호출을 확인했다. Modonomicon 자체 안내서의 같은 필드도 검사했으며
영어 언어 파일 밖에 남은 문자열은 없었다.
서버 데이터팩·모드 JAR·월드 변경이나 서버 재시작은 필요하지 않다.

Modonomicon 번역의 출처·변경 사실·CC-BY-SA-4.0 고지를 팩에 추가한다.
[상류 README](https://github.com/klikli-dev/modonomicon#licensing)와 라이선스 전문은 에셋을
CC-BY-SA-4.0으로 명시한다. 상류 파일명이 `LICENSES/CC-BY-4.0.txt`이고 모드 메타데이터가
`CC-BY-4.0`이라고 적힌 것과 차이가 있으므로 실제 전문을 보존한다. Occultism의 MIT 고지는 유지한다.

### 확장 결과와 검증

- Occultism 4,341개 키(기존 4,332개 + 안내서 보완 9개), Modonomicon 309개 키를 포함한다.
- `python3 scripts/build_occultism_resource_pack.py`를 Codex가 독립 실행해 동일 산출물을 확인했다.
  ZIP은 121,472바이트, SHA-256은
  `206fe5460f3cbe3bc84ace4a981ec5924dd52301dddf605895c992409e091c0d`다.
- `python3 -m unittest discover -s tests -v`: Codex 독립 실행 **64개 통과**.
  안내서 본문 누락 회귀 검사, Modonomicon 전체 키·한국어·치환자·링크·서식·숫자 검사,
  잘못된 입력에서 기존 산출물 보존, 세 클라이언트 배포 형식에 동일 ZIP 포함을 확인했다.
- Modonomicon의 화면·설정·명령·연구 안내와 예제 본문을 원문과 대조했다. 기존 Occultism의
  세 번역 파일은 변경하지 않았다.
- 로컬 클라이언트 아카이브와 생성 lock도 새 번역으로 다시 만들었다. 버전명은 아직 `1.1.10`이므로
  현재 작업 폴더의 아카이브·생성 lock 해시는 기존 공개 `client-1.1.10` 릴리스와 다르다.
  **공개 릴리스 파일은 교체하지 않았다.** 다음 클라이언트 공개 시에는 새 버전으로 발행해야 한다.
- 기존 인스턴스에는 새 `occultism-ko-1.256.0-mc26.3.zip`으로 같은 이름의 파일을 교체하고
  한국어·리소스팩 활성화 상태를 확인한다. 기존 팩 활성화 ID는 유지했다.
  게임 내 줄바꿈·글자 잘림·링크 이동은 아직 확인하지 않았다.

## 파일 소유권과 분할

Codex는 이 설계 문서, 용어집, `tests/test_occultism_translation.py`와 독립 검증을 담당한다.
Claude는 아래 번역 JSON과 후속 빌드 스크립트·팩 메타데이터를 구현한다.
동일 브랜치와 체크아웃에서 각 작업자는 자신에게 배정된 파일만 편집한다.

| 파일 | 담당 범위 |
|---|---|
| `translations/occultism/ko_kr/interface.json` | `book.`으로 시작하지 않는 모든 키 |
| `translations/occultism/ko_kr/guide_basics.json` | 안내서 getting_started, spirits, pentacles, rituals, summoning_rituals 범주 |
| `translations/occultism/ko_kr/guide_advanced.json` | 나머지 모든 `book.` 키. crafting_rituals, familiar_rituals, possession_rituals, storage 및 책 이름·툴팁 포함 |

범주 판별은 `book.occultism.dictionary_of_spirits.` 다음의 첫 경로 부분으로 한다.
각 파일은 번역 키에서 한국어 문자열로의 JSON 객체다. 합치면 원문 키 집합과 정확히 일치해야 한다.
번역 작업용 임시 스크립트는 저장소에 남기지 않는다. 디버그·설정·의식 메시지도 범위에 포함한다.
새 고유명사는 용어집의 표기 원칙을 적용하되 의미를 바꿀 설계 변경은 Codex에 먼저 보고한다.

## 구현 전 정의한 검증 기준

1. 원문 JAR 해시 확인. 분할별 키 누락·추가·중복이 없어야 한다.
2. 이름 135개 키는 용어집의 채택 표기와 일치해야 한다.
3. 모든 번역 대상 문자열에 실제 한국어가 있어야 한다. 빈 원문, `...`, `Occultism`, `%s`, `x2`·`x3`·`x4`·`x6`은 그대로 보존한다. 원문을 추가 대조하여 자연어가 아닌 작업 범위 `16x16`·`32x32`·`64x64`와 저장소 용량 서식 `%d/%d`도 보존 대상으로 확인했다. 추가 예외는 원문 근거를 Codex가 검토한다.
4. `%s`·`%d`·`%%`의 타입·순서와 Markdown 링크 대상, 색상 제어 대상, `§` 코드, 굵게 표시를 보존한다. 링크 표시명은 번역한다. 서식 검사와 별도로 원문 의미·조건·부정을 수동 대조한다.
5. 숫자·티어·재료·조작·금지 조건을 유지한다. 문장에 한글을 덧붙이거나 원문을 남겨 검사를 통과하는 방식은 번역 완료로 인정하지 않는다.
6. 안내서 본문과 이름의 용어가 일치해야 한다. 반복 의식 메시지는 동작을 유지한 한국어 템플릿으로 번역할 수 있다.
7. 빌드 결과 `dist/occultism-ko-1.256.0-mc26.3.zip`의 루트에 `pack.mcmeta`, `assets/occultism/lang/ko_kr.json`이 있어야 한다. 모드·데이터팩 기능을 추가하지 않는다.
8. 로컬 Minecraft 26.3 클라이언트 JAR의 `version.json`은 resource version 97.1이다. 팩의 `min_format`·`max_format`은 `[97, 1]`로 제한하고 빌드 시 형식을 확인한다. 배열 형식의 근거는 [Mojang의 팩 메타데이터 설명](https://www.minecraft.net/en-us/article/minecraft-snapshot-25w31a)이다.
9. 빌드에 실패하면 오류를 드러낸다. 원문 영어를 채우거나 기존 산출물을 성공으로 보고하지 않는다.

빌드 스크립트는 `scripts/build_occultism_resource_pack.py`로 한다. 기본 실행은 위의 고정 경로를 사용하며,
검증과 재현을 위해 `--source-jar`, `--translations-dir`(세 JSON이 있는 폴더), `--output`을 받는다.
잘못된 원문 SHA-256, 누락 키, 중복 JSON 키는 구체적인 오류와 실패 종료 코드로 알리고 새 ZIP을 만들지 않는다.
팩 메타데이터와 라이선스·출처 파일은 `translations/occultism/` 아래에 둔다.

빌드 및 전체 검증 명령:

```sh
python3 scripts/build_occultism_resource_pack.py
python3 -m unittest discover -s tests -p test_occultism_translation.py -v
```

번역 중에는 해당 클래스만 실행한다. 완성된 팩 검사도 포함하므로 전체 검사는 빌드 후 실행한다.
게임 화면에서 안내서 링크·조작·글자 잘림을 확인하기 전에는 런타임 검증 완료로 보고하지 않는다.

## 설치와 확인 방법

결과물: [occultism-ko-1.256.0-mc26.3.zip](../dist/occultism-ko-1.256.0-mc26.3.zip). `dist/`는 Git 제외 경로이며 위 명령으로 다시 만들 수 있다.

1. Occultism 1.256.0을 사용하는 Minecraft 26.3 인스턴스의 `resourcepacks` 폴더에 ZIP을 그대로 넣는다.
2. 게임의 리소스 팩 화면에서 이 팩을 켜고, 같은 모드의 언어 파일을 덮어쓰는 다른 팩보다 우선하도록 배치한다.
3. 게임 언어를 한국어로 선택한다.
4. 영혼 사전, 아이템 툴팁, 소환·저장 설명에서 한국어 표시와 링크 이동을 확인한다.

이 팩은 `ko_kr` 번역만 제공한다. 버전이 다른 모드에는 새 키·변경된 설명이 있을 수 있으므로 동일한 번역 범위를 보장하지 않는다.
Occultism 원문과 기존 번역의 출처 및 [상류 MIT 라이선스](https://raw.githubusercontent.com/klikli-dev/occultism/version/26.3/LICENSE)를 팩에 포함한다.

## 최초 제작 검증 기록 (확장 전)

**번역·팩 제작·정적 검증 완료 (2026-09-25).**

| 내용 | 결과 |
|---|---|
| 전체 키 | 4,332개, 현재 영어 원문과 정확히 일치 |
| 이름·화면·설명·의식 메시지 | 2,790개 |
| 입문·펜타클·영혼·소환 안내서 | 831개 |
| 제작·사역마·빙의·저장 안내서 및 책 이름 | 711개 |
| 한글 포함 / 보존한 기호·서식·브랜드 | 4,276개 / 56개 |
| 채택 이름 검사 | 기존 용어집과 추가 공통 이름을 합쳐 310개 키 확인 |
| 자동 검증 | Codex 독립 실행 21개 통과 |
| ZIP 크기 | 105,993바이트 |
| ZIP SHA-256 | `5affd2607b882309e6a93013654c4f6fadb512a21b50c74fb2fabc18d7242f44` |

Claude가 번역과 빌드를 구현하고 Codex가 결과를 검토했다. Codex는 최종 소스로 다시 빌드하여 같은 해시를 확인했고,
키 집합·중복·숫자·치환자·링크·색상·채택 이름·팩 형식과 잘못된 입력의 빌드 실패를 검증했다.
전체 문자열에서 긴 영어 문장 잔존, 과도한 축약 후보, 변경 대상이었던 옛 이름을 검사했으며,
소환·채굴·영혼 보석·저장·조작·툴팁의 주요 문단을 원문과 표본 대조했다.
기존 번역에서 빠졌던 구속 조작 설명과 기본 광석 채굴 설명도 현재 원문에 맞게 보완했다.
원작 라이선스와 기존 한국어 번역 기여자의 출처를 ZIP에 포함했다.

**게임 내 검증은 아직 수행하지 않았다.** 팩 로딩, 안내서 링크의 실제 이동, 글자 잘림과 조작 화면 표시는 게임에서 확인해야 한다.
서버 재시작, 기존 배포 팩 교체, 공개 배포는 수행하지 않았다.

## 원문에서 발견한 표기 문제

- `book.occultism.dictionary_of_spirits.storage.storage_stabilizer.build_instructions.text`는 설치 대상을 Storage controllers로 부르지만, 저장소 안정기 항목에서 모체를 바라보는 위치와 거리 제한을 설명하는 문맥이다. 번역에서는 이 문맥에 맞춰 **저장소 안정기**로 표기했다. 원문 단어와 다르게 옮긴 교정 사항이다.
- `book.occultism.dictionary_of_spirits.familiar_rituals.familiar_wingnis.name`의 현재 영어 값은 Drikwing Familiar다. 원문 제목대로 **드릭윙 사역마**를 사용했다. Wingnis와 Drikwing이라는 원문 대상의 구분 자체를 번역에서 재설계하지 않았다.
- 원문은 제작 범주의 표시명에 Binding / Infusion / Crafting Rituals를 혼용한다. 각각 구속 / 주입 / 제작 의식으로 옮기고 동일한 영어 표시명의 한국어는 통일했다. 이 원문 분류명 차이는 남아 있다.
- `item.occultism.book_of_calling_djinni.tooltip.deposit`의 원문에는 `%s` 대신 `% s`가 들어 있다. 이번 번역도 이 원문 서식을 보존했다. 해당 위치 표시의 원문 오타는 이 팩에서 해결하지 않았다.

바닐라 재료 이름은 Minecraft 26.3 한국어 자산과 대조했다. 안내서의 Budding Amethyst와 Reinforced Deepslate에는 각각 **싹 틔우는 자수정**, **보강된 심층암**을 사용한다.


## 클라이언트 팩 통합

후속 작업인 클라이언트 `1.1.7`부터 이 번역 ZIP을 기본 활성화 상태로 포함한다. 클라이언트 빌더가 번역 빌더를 먼저 실행하며 게임 언어를 한국어로 지정한다. 기존 독립 리소스팩도 계속 생성한다. 설치·배포 상태는 [클라이언트 안내](../README.md#클라이언트-모드팩)를 참고한다. 위의 서버·공개 배포 제외 범위는 독립 번역 제작 당시의 범위다.

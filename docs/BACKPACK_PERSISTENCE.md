# 착용 배낭 내용물 저장 결함과 검증

## 원인 (2026-09-26)

Minecraft 26.3 / NeoForge `26.3.0.8-beta`, Traveler's Backpack `11.4.0`,
Curios `17.0.0-beta+26.3` 조합에서 Curios Back 슬롯에 착용한 배낭에 넣은
아이템이 화면을 닫았다 열면 사라진다. 사용자가 실제 서버에서 재현했다.

설치된 JAR을 역컴파일하여 확인한 경로:

1. Curios `CuriosStacksResourceHandler.getStackInSlot()`은 NeoForge
   `ItemUtil.getStack()` → `ItemResource.toStack()`을 통해 복사본을 반환한다.
2. Traveler's Backpack `AttachmentUtils.getWearingBackpack()`은
   `findFirstCurio(...).stack()`으로 이 복사본을 가져온다.
3. `BackpackWrapper.setSlotChanged()`는 복사본의 `BACKPACK_CONTAINER` 등을
   갱신한다. Curios 슬롯에 수정한 스택을 다시 기록하지 않는다.
4. 메뉴를 닫으면 다음 열기에서 변경 전 스택을 다시 읽는다. 재접속해도
   실제 저장된 내용만 읽으므로 같은 현상이 발생한다.

플레이어의 현재 `dat`/`dat_old` 및 시간별 월드 백업 12개(플레이어 파일
24개)를 읽어 확인했으며, 착용 배낭에 `travelersbackpack:backpack_container`
항목이 없었다. 초기 `starter_upgrades`도 그대로였다. 해당 재접속 구간에
배낭 저장 오류 로그는 없었다.

기존 GitHub 신고를 확인한 뒤, 이번 결함을
[Traveler's Backpack #1618](https://github.com/Tiviacz1337/Travelers-Backpack/issues/1618)에
등록했다. 공식 [연동 문서](https://github.com/Tiviacz1337/Travelers-Backpack/wiki/Integrations-with-other-Mods#forge--neoforge)는
Curios Back 슬롯 착용을 지원한다고 명시한다. 비슷한 증상의
[Traveler's Backpack #1431](https://github.com/Tiviacz1337/Travelers-Backpack/issues/1431)은
1.21.1에서 원인이 확정되지 않은 신고다.
[Curios #630](https://github.com/TheIllusiveC4/Curios/issues/630)은
1.20.1의 End's Phantasm 충돌이며,
[Traveler's Backpack #1613](https://github.com/Tiviacz1337/Travelers-Backpack/issues/1613)은
이전 버전에서 26.2로 이행하는 저장 형식 문제다. 이번 원인과 같다고 보지 않는다.

## Curios 연동 패치

서버 전용 `aziran-backpack-curios-1.0.0.jar`를 만들어 실제 저장 경로를 수정했다.
소스·재현 빌드는 [compat/backpack-curios](../compat/backpack-curios/README.md),
설계 판단과 한계는 [패치 설계](BACKPACK_CURIOS_FIX_DESIGN.md)에 있다.

배낭 모드의 `getWearingBackpack`과 `curioTick` 두 경로에 한정해 Curios가
실제로 보관하는 배낭 객체를 전달한다. 초기 업그레이드 적용, 저장·도구·업그레이드
슬롯, 설정, 주기적 기능 변경이 그 객체에 기록되고 Curios의 기존 저장·동기화
처리가 이를 읽는다. Curios의 공개 getter는 계속 복사본을 반환한다.
슬롯의 배낭이 옮겨지거나 동일한 내용의 다른 배낭으로 교체돼도 이전 화면과
wrapper를 재사용하지 않도록 객체 동일성을 검사한다.

이 패치는 Curios 내부 구현에 의존하므로 Minecraft `26.3`, NeoForge
`26.3.0.8-beta`, Traveler's Backpack `11.4.0`, Curios `17.0.0-beta+26.3`에
정확히 고정한다. 버전 변경은 새 검토·재현 검사가 필요하다. 원본 JAR, 아이템
형식은 바꾸지 않으며 추가 네트워크 메시지나 레지스트리를 만들지 않는다.
최초 서버 배포에서는 클라이언트 팩을 유지했다. 이후 사용자 요청으로 같은
패치 JAR을 클라이언트 1.1.12에도 포함한다. 실제 클라이언트 접속과 화면 조작
확인은 자동 검사와 별도로 기록한다.

배포 설정은 `backSlotIntegration=true`다. 사용자는 앞서 자체 착용했던 배낭을
일반 인벤토리로 꺼냈다고 확인했고, Codex도 RCON 읽기 전용 조회로 자체 착용
attachment의 `Backpack`이 `{}`임을 확인했다. 전환 후에는 Curios Back 슬롯에
넣고 기존 `Y`로 연다. 아이템 복구나 플레이어 NBT 수정은 하지 않는다.

## 임시 자체 착용 조치 기록

`server-data-26.3-neoforge/config/travelersbackpack-server.toml`의
`server.backpackSettings.backSlotIntegration`을 `false`로 설정하여 모드의
자체 착용 기능을 사용한다. JAR, 클라이언트 팩, 아이템 형식은 바꾸지 않는다.
이 설정은 공식 Curios 연동 코드 자체의 패치가 아니며, 해당 결함이 있는
착용 방식을 서버에서 사용하지 않도록 하는 구성 변경이다.

자체 착용의 `BackpackAttachment`는 실제 배낭 스택과 wrapper를 함께 보관하고,
serializer가 그 스택을 `Backpack`으로 저장한다. 운영 설정 파일은 Git 제외
대상이므로 새 서버를 구성할 때도 위 설정을 적용해야 한다.

기존 배낭은 Curios Back 슬롯에서 일반 인벤토리로 꺼내고, 손에 든 채
우클릭하여 배낭 화면의 착용 버튼으로 멘다. 이후 열기 단축키는 기존 `Y`다.
Curios 자체와 다른 장신구는 유지한다. 사망 시 배낭 배치 설정도 변경하지
않지만, 자체 착용과 Simple Tomb의 사망 처리 조합은 별도 게임 검증 대상이다.

변경 전 [월드 보호 백업 절차](BACKUPS.md#오프라인-월드-보호-백업)를 따른다.
월드 전체를 정상 종료 후 백업하며, 플레이어 NBT를 직접 수정하거나 아이템을
지급하지 않는다.

## 자동 검사와 합격 기준

- `python3 tests/backpack-runtime/run.py`: 원본 JAR만으로 소실과 이전 화면
  재사용 결함을 재현한다. 최종 기준 검사 16개 중 10개 실패, 대조 검사 등
  6개 통과. 실패 종료 상태 1이 예상된다.
- `python3 compat/backpack-curios/build.py`: 고정한 의존성 해시를 검사하고
  네트워크 없는 Java 25 컨테이너에서 서버 패치를 만든다.
- `python3 tests/backpack-runtime/run.py --patch dist/backpack-curios/aziran-backpack-curios-1.0.0.jar --full-modset`:
  운영 모드 24개와 패치·테스트 전용 모드를 임시 월드에서 실행한다. 운영
  월드·설정은 마운트하지 않는다. 저장 검증 후 별도 JVM을 시작해 파일에 쓴
  Curios inventory를 새 플레이어로 불러온다.
- Codex 독립 검사: 위 16개 및 별도 JVM 읽기 1개, 총 17개 통과.
  화면 다시 열기·수량 감소·비우기, 저장 round-trip, 도구·업그레이드·설정,
  초기 업그레이드 중복 방지, 주기적 처리와 Curios 동기화 snapshot, 슬롯
  교체·제거와 설정 화면 무효화, 손·자체 착용·설치형 콜백 보존을 확인했다.
  결과: `/tmp/aziran-backpack-test-3d6roffn/`, 두 서버 exit 0 및 runner exit 0.
- Codex 독립 재빌드 SHA-256:
  `edffa69c4b391a1ee650458905a9ef031b541e3ec915ef28d8ce631af19ea755`.
  Claude 빌드와 바이트가 같았다. 테스트 클래스는 운영 JAR에 들어가지 않는다.
- 네트워크 없는 전체 모드 테스트에서 BlueMap의 외부 리소스 다운로드 경고가
  발생했다. 지도 렌더링을 검증한 실행이 아니며 경고를 숨기거나 정상으로
  간주하지 않는다. 패치의 mixin·배낭 오류는 없었다.
- 배포 검사: `tests/test_backpack_persistence_config.py`는 연동 활성화,
  고정된 서버 패치 설치, 정확한 의존성·필수 mixin, 테스트 클래스 미포함,
  클라이언트 1.1.12의 동일 JAR 포함을 검사한다. 실제 플레이어 접속 검사를 대신하지 않는다.
- 실제 클라이언트 접속·Curios 착용·닫기/열기·재접속, 탱크/호스와 모든 개별
  업그레이드, 사망·Simple Tomb 조합은 실제 수행한 경우에만 통과로 기록한다.

### 임시 자체 착용의 당시 합격 기준

- 배포 설정 검사: `python3 -m unittest discover -s tests -p test_backpack_persistence_config.py -v`.
  변경 전 실패를 확인했다. 이 검사는 위험한 착용 모드의 재활성화를 감지하며,
  게임 내 저장 동작을 증명하는 테스트는 아니다.
- 설정 비교: 위 플래그 이외의 TOML 값과 설치된 JAR 해시는 동일해야 한다.
- 정상 종료, 모든 차원 월드 보호 백업의 목록·해시 검증, 정상 기동, RCON 응답.
- 실제 플레이어가 자체 착용한 배낭에 식별 가능한 아이템을 넣고 화면을 닫았다
  열어도 같은 아이템과 수량이 남아야 한다.
- 서버의 읽기 전용 `data get entity` 조회로 자체 배낭 attachment의 `Backpack`
  아래 `travelersbackpack:backpack_container`에 같은 아이템이 기록돼야 한다.
- 로그아웃 후 저장된 플레이어 NBT와 재접속 후 배낭의 내용이 같아야 한다.
- 추가 서버 재시작 후 유지와 Simple Tomb 사망 처리는 실제 수행했을 때만
  통과로 기록한다. 설정 검사나 기동 성공으로 대체하지 않는다.

## 임시 자체 착용 배포 기록 (2026-09-26 UTC)

- 02:09:43~02:09:44 정상 종료: `exit=0`, `oom=false`, 플레이어·월드·세 차원
  저장 로그와 러너 `Done`을 확인했다.
- 보호 백업: `/home/pilon1945/aziran-26.3-protected-backups/pre-backpack-native-world-2026-09-26-020955.tar`.
  11,450,880,000바이트, 3,830개 항목. Codex가 아카이브를 다시 읽어 모든
  항목이 `world/`에 속하고 `level.dat` 및 세 차원 region이 있음을 검증했다.
  SHA-256을 독립 재계산해 `.sha256`과 일치함을 확인했다:
  `2c2df7c4838429df67571f7f373e42b631bc2f8f88aaff22862a82decc811968`.
- 설정은 `backSlotIntegration = true` → `false` 한 줄만 바뀌었으며 나머지
  바이트와 설치된 24개 JAR의 SHA-256은 변경 전과 동일하다.
- 02:10:31 기존 컨테이너 시작, 02:10:45 서버 `Done`, 이후 `running healthy`와
  RCON 응답을 Codex가 확인했다. 기존 Occultism Curios 연동 경고, refmap·udev·
  apothic_enchanting 경고는 남아 있다. 이 작업으로 해결한 경고가 아니다.
- Codex 독립 검사: Python 65개, JavaScript 2개 통과. 설정 회귀 검사는
  변경 전 실패, 변경 후 통과했다.
- 게임 내 다시 열기·재접속·플레이어 NBT 검증은 사용자 확인을 기다리는 중이다.
  수정 후 아이템을 저장한 상태에서의 추가 서버 재시작과 사망 처리는 미검증이다.
  이후 사용자는 자체 착용은 된다고 확인했지만, Curios에서도 동작하도록
  수정할 것을 요청했다. 따라서 위 임시 조치의 저장 동작을 추가 검증하는
  대신 Curios 패치로 진행했다.

## Curios 패치 운영 배포 기록

- 2026-09-26 03:19:48 UTC 정상 종료 시작, 03:19:49 `exit=0`, `oom=false`.
  Codex가 플레이어 저장과 overworld·the_nether·the_end 저장 로그를 확인했다.
- 보호 백업:
  `/home/pilon1945/aziran-26.3-protected-backups/pre-backpack-curios-world-2026-09-26-032000.tar`.
  11,450,880,000바이트, 3,833개 항목. Codex가 tar를 독립적으로 다시 열어
  모든 항목이 `server-data-26.3-neoforge/world/` 안에 있고 `level.dat`와
  세 차원의 region 경로가 있음을 확인했다. 전체 파일 SHA-256 재계산도
  `.sha256` 기록과 일치했다:
  `f9f5303232f2e034eeb8b4b4a3c24270b9c8d9df4328c884734fe3782b7fda87`.
- 12,040바이트의 패치 JAR을 `1000:1000`, 권한 `664`로 설치했다. Codex가
  설치 파일과 독립 검사한 빌드 파일의 바이트 일치를 확인했다. 기존 24개
  JAR의 해시와 lock 메타데이터는 모두 이전 커밋과 동일하다.
- 설정은 `backSlotIntegration=false` → `true` 한 줄만 바꿨다. 설정 파일
  SHA-256은 `e35ded3b1d1d1952d3eebad4bb902ad2827b8377bedddf1af67ef91496e9a98f`다.
- 03:20:40 기존 컨테이너 시작, 03:20:54 `Done`. Codex가 `healthy`, RCON
  응답과 `Aziran Backpack Curios Persistence 1.0.0` 로드를 확인했다.
  기존 Occultism Curios 통합, refmap, udev, apothic_enchanting 경고는 남아
  있으며 이번 패치로 해결한 문제가 아니다. 새 패치·mixin 오류는 없었다.
- 최초 서버 배포 때는 기존 클라이언트 팩·릴리스 파일을 바꾸지 않고 패치를
  클라이언트 빌더의 제외 목록에 등록했다. 이후 1.1.12 포함 요청으로 해당
  제외 항목을 제거했다(아래 절).
- Codex 독립 최종 검사: Python 66개, JavaScript 2개 통과. 추가한 클라이언트
  제외 검사의 반환형 착오를 Codex가 바로잡은 뒤 전체 Python 검사를 다시 실행했다.
- 재기동 후 사용자가 기존 클라이언트로 재접속해 Curios Back 슬롯에 착용한
  배낭에 아이템을 넣고 화면을 닫았다 다시 열어도 그대로 있다고 확인했다.
  Codex의 읽기 전용 entity 조회에서도 직렬화된 `curios:inventory` 안에
  `travelersbackpack:standard`와 `travelersbackpack:backpack_container`가 확인됐다.
  따라서 기존 클라이언트의 접속·Curios 착용·닫기/열기는 실제 게임에서도 확인됐다.
- 아이템을 넣은 뒤 실제 사용자가 다시 로그아웃/로그인하는 경우와 추가 운영
  서버 재시작, 사망/무덤 및 모든 개별 업그레이드는 미검증이다. 별도 JVM의
  Curios 데이터 저장·읽기 자동 검사와 구분한다.

## 클라이언트 팩 1.1.12 포함

사용자가 싱글플레이에서도 패치를 사용할 수 있도록 팩에 넣되 추가 검증은
하지 말라고 요청했다. 따라서 동일한 `aziran-backpack-curios-1.0.0.jar`를
`.mrpack`의 `client-overrides/mods/`, 수동 ZIP의 `mods/`, MultiMC ZIP의
`.minecraft/mods/`에 넣는다. 기존 21개 모드에 패치 하나를 더해 총 22개이며,
멀티플레이 클라이언트에 필수인 모드가 새로 생긴 것은 아니다.

이번 작업에서는 게임·통합 서버 실행 검증을 수행하지 않는다. 검사 범위는
아카이브 구성, 원본 JAR과 해시 일치, 기존 모드·설정 보존 및 배포 파일이다.
싱글플레이에서 정상 동작한다고 검증한 릴리스로 표기하지 않는다. 운영 서버의
JAR·설정·월드를 변경하거나 다시 시작하지 않는다.

패키징 결과: Codex의 파일·배포 구성 검사 12개와 사이트 JavaScript 검사 2개가
통과했다. 이전 1.1.11과 세 아카이브를 비교해 패치 JAR만 추가됐고, 기존 모드·
설정·리소스는 동일함을 확인했다. 세 패치 사본은 운영 서버 JAR과 바이트가 같다.

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

GitHub 이슈·PR을 2026-09-26에 확인했지만 이 26.3 복사본 저장 결함과
일치하는 신고나 수정판은 찾지 못했다. 비슷한 증상의
[Traveler's Backpack #1431](https://github.com/Tiviacz1337/Travelers-Backpack/issues/1431)은
1.21.1에서 원인이 확정되지 않은 신고다.
[Curios #630](https://github.com/TheIllusiveC4/Curios/issues/630)은
1.20.1의 End's Phantasm 충돌이며,
[Traveler's Backpack #1613](https://github.com/Tiviacz1337/Travelers-Backpack/issues/1613)은
이전 버전에서 26.2로 이행하는 저장 형식 문제다. 이번 원인과 같다고 보지 않는다.

## 선택한 수정과 범위

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

## 합격 기준

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

## 배포와 독립 검증 (2026-09-26 UTC)

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

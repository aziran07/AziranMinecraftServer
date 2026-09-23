# 클라이언트 모드 호환성 검토 (26.3 NeoForge)

기존 1.21 Fabric 구성(`~/minecraftMin/data/mods`)에서 쓰던 최적화·편의 모드 중 어떤 것을
26.3 NeoForge 클라이언트 팩에 넣었고 무엇을 뺐는지, 그 근거를 기록한다.
팩 산출물과 고정 목록은 [클라이언트 모드팩](MODS_26_3.md#클라이언트-모드팩)을 참고한다.

대상 환경은 Minecraft `26.3`, NeoForge `26.3.0.8-beta`, Java `25`다. 이 값은 서버와 동일하며
이번 작업에서 바꾸지 않았다.

아래 "이번에 추가한 모드"는 팩 `1.1.0` 기준에 `1.1.2`·`1.1.3`에서 더한 모드를 합쳐 적었다.
`1.1.3`은 여기서 Sodium과 Xaero's Minimap을 빼고 JourneyMap을 더한 모드 16개였다.
현재 후보 `1.1.4`는 `1.1.3`에 Sodium을 되돌리고 Iris 로컬 빌드를 더한 모드 18개와 셰이더 팩 1개다.

## 1.1.4: 셰이더(Iris·Sodium·Complementary Reimagined)와 options.txt 우회

- **Iris** `1.11.6-snapshot+mc26.3-local`: NeoForge 26.3 지원은 미병합
  [PR #3354](https://github.com/IrisShaders/Iris/pull/3354)에만 있다. 커밋
  `10d3598cd96b0566497b66efe66256f468cd977e`를 수정 없이 JDK 25로 로컬 빌드한 JAR이며 빌드 당시
  NeoForge 26.3.0.7-beta 기준으로 컴파일했다. 메타데이터상 필수 의존성은 `minecraft [1.21.3,)`,
  `neoforge [21.3.9-beta,)`, `sodium [0.6,)`로 모두 충족된다. 내장 JAR은 glsl-transformer
  3.0.0-pre3(AGPL-3.0), jcpp 1.4.14(Apache-2.0), antlr4-runtime 4.13.1(BSD-3-Clause)이다.
  공식 배포처에 없으므로 `.mrpack`에도 JAR을 담고, LGPL-3.0·AGPL-3.0의 대응 소스 조건에 따라
  세 아카이브의 `sources/iris/`에 커밋 소스 tar.gz(GitHub 커밋 아카이브와 압축 해제 내용 동일),
  내장 라이브러리 소스 JAR 3개, 라이선스 전문을 함께 담는다. JAR의 클래스 745개 중 743개가 소스
  트리의 `.java`에 대응하며, 나머지 2개(`BuildConfig`, `DesktopBuildConfig`)는 빌드 때 생성된다.
  같은 커밋을 다시 빌드해 바이트 단위로 같은 JAR이 나오는지는 확인하지 않았다.
- **Sodium** `mc26.3-0.9.2-neoforge`: Iris 필수 의존성이라 `1.1.1`에서 뺀 같은 파일을 되돌렸다.
  아래 "1.1.1 이후: Sodium 제외"의 `0xc0000409` 원인은 여전히 규명하지 않았다. PolyForm Shield
  1.0.0은 사본 배포를 허용하고 전문 동봉을 요구하며, JAR 루트 `LICENSE.md`가 이를 충족한다.
- **Complementary Reimagined** `r5.9.3`: Complementary License Agreement 1.7의 1.2.d가 모드팩에는
  Modrinth·CurseForge 시스템으로만 넣고 직접 파일 업로드 재배포를 금지하므로, `.mrpack`의
  Modrinth CDN 다운로드 항목(`shaderpacks/`)으로만 넣고 두 ZIP에는 담지 않는다. 기본으로 켜지 않는다.
- **options.txt**: Occultism 26.3(커밋 `631457c`) `ClientSetupEventHandler.java` 218행이 사역마
  단축키 18개를 `Type.KEYBOARD, -1`로 등록해, 첫 실행 뒤 `key.keyboard.-1`이 저장되고 두 번째
  실행이 `InputConstants.isKeyDown`의 `IndexOutOfBoundsException`으로 실패한다. 상류 결함은 그대로
  두고, `version:5023`과 사역마 단축키 18개를 `key.keyboard.unknown`으로 적은 최소 `options.txt`를
  세 아카이브에 넣어 우회한다.

관찰 기록: 사용자의 이전 1.1.4 시험 인스턴스는 `options.txt`를 초기화한 첫 실행에서 Complementary
셰이더 적용과 서버 접속에 성공했고, 두 번째 실행이 위 단축키 문제로 실패했다. 기존 인스턴스
복사본에서 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꾸자 두 번 연속 실행·접속에
성공했고 `-1`이 다시 생기지 않았다. **1.1.4 아카이브로 새로 만든 인스턴스의 두 번 실행은 아직
확인하지 않았다.**

## 1.1.3: Xaero's Minimap을 JourneyMap으로 교체

미니맵 모드를 [Xaero's Minimap](https://modrinth.com/mod/xaeros-minimap) `neoforge-26.3-26.5.3`에서
[JourneyMap](https://modrinth.com/mod/journeymap) `26.3-6.0.9+neoforge`로 바꿨다. 모드 수는 16개
그대로이고 나머지 15개 JAR은 `1.1.1`·`1.1.2`와 바이트 단위로 동일하다. Sodium은 계속 제외한다.

### 교체 근거: `1.1.2`의 Windows 크래시

16개를 모두 켠 `1.1.2`는 해당 Windows PC에서 네이티브 종료 코드 `0xc0000005`(액세스 위반)로
크래시했다. Sodium을 끈 `1.1.0` 인스턴스에서 나던 `0xc0000409`(스택 버퍼 오버런)와는 다른 코드다.

A/B 결과로 방아쇠가 좁혀졌다.

- 사용자가 같은 `1.1.2` 인스턴스에서 `xaerominimap-neoforge-26.3-26.5.3.jar` **하나만**
  비활성화해 실행했고, 정상 실행됨을 확인했다.
- 산출물 대조로도 `1.1.1`과 `1.1.2`의 최상위 모드 JAR 차이는 이 파일 하나뿐이었다. 공통 15개는
  SHA-512까지 동일하다.
- 바뀐 변수가 이 JAR 하나이므로, **이 모드·드라이버·런타임 조합에서 크래시를 일으키는 것은
  Xaero's Minimap**(내장 `xaerolib` 포함)이라고 확인할 수 있다.

미니맵 요구는 남아 있으므로 같은 환경에서 시험되지 않은 다른 미니맵으로 바꾸는 쪽을 택했다.
이것은 **Xaero's Minimap에 결함이 있다는 판정이 아니다.** 네이티브 실패 메커니즘은 규명하지
않았고, 모드 결함인지 그 PC의 드라이버·GPU와의 조합인지 NeoForge 26.3 베타나 다른 모드와의
상호작용인지 구분하지 않았다. 다른 버전의 Xaero's Minimap도 시험하지 않았다.
**JourneyMap이 이 크래시를 해결한다는 확인도 아직 없다.** `1.1.3`을 Windows에서 실행해 보지
않았기 때문이다.

### 서버에는 설치하지 않는다

Modrinth는 JourneyMap을 `client_side=optional`, `server_side=optional`로 표시한다. 지도 표시와
웨이포인트는 클라이언트만으로 동작하므로 이번 작업에서 서버 모드 디렉터리·서버 lock·Compose
설정은 건드리지 않았다. `.mrpack` 항목의 `env.server=unsupported`는 "이 팩이 서버에 아무것도
설치하지 않는다"는 뜻이며, 모드 자체의 서버 지원 여부와는 다른 값이다.

### 라이선스 때문에 JAR을 팩에 담지 않는다

JourneyMap은 All Rights Reserved이고, [공식 라이선스 문서](https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/)가
허용과 금지를 명시한다.

- 허용: "Create a modpack containing JourneyMap, as long as JourneyMap is downloaded from
  CurseForge or Modrinth as part of the modpack installation or launch process."
- 금지: "Re-host, redistribute or bundle the mod in any way, including as part of a larger
  distribution such as a modpack."

JAR 루트의 `license.txt`도 "may not be altered, file-hosted, re-packaged, reverse-engineered, or
distributed in part or in whole without express written permission"이라고 적는다.

그래서 산출물마다 처리를 다르게 했다.

| 산출물 | JourneyMap 처리 | 근거 |
| --- | --- | --- |
| `.mrpack` | `modrinth.index.json`의 `files` 항목으로만 지정. 런처가 설치 중 Modrinth CDN에서 받는다 | 허용 조건인 "설치 과정 중 공식 배포처 다운로드"에 해당 |
| 수동 ZIP | 담지 않는다(JAR 15개) | 아카이브에 넣으면 금지된 번들·재배포가 된다 |
| MultiMC 인스턴스 ZIP | 담지 않는다(JAR 15개) | 같은 이유 |

두 ZIP에는 생성된 `README.md`가 맨 앞 절에서 JourneyMap이 없다는 사실과 공식 배포처에서 직접
받아 `mods/`에 넣는 절차를 안내한다. 절차에는 고정한 파일 이름·크기·SHA-1·SHA-512가 들어 있어
사용자가 받은 파일을 대조할 수 있다. 같은 `README.md`가 **MultiMC 사용자에게는 이 ZIP 대신
`.mrpack` 가져오기를 권한다.** [MultiMC 위키의 Import Instance 문서](https://github.com/MultiMC/Launcher/wiki/Import-Instance)가
가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있다. 위키는 최소 버전을 명시하지 않으며,
실제 가져오기를 시험해 보지는 않았다.

빌더는 이 동작을 입력 lock의 `bundle_jar` 값으로 결정한다. `bundle_jar=false`인 모드는 수동
ZIP·MultiMC ZIP·`manifest.json`에서 빠지고, Modrinth CDN URL이 없으면 설치 경로가 없으므로
빌드를 중단한다. `client-mods-cache/`의 로컬 사본은 크기·해시·메타데이터 검증에만 쓰이고
산출물에는 들어가지 않는다.

## 1.1.1 이후: Sodium 제외

Windows MultiMC에서 `1.1.0` 인스턴스가 실행 직후 종료된 크래시 로그를 받았다. 로그에는 Sodium의
Nvidia 드라이버 워크어라운드가 `IllegalStateException: Command line is already modified`로 실패한
기록이 남았고, 곧이어 프로세스가 네이티브 종료 코드 `0xc0000409`(스택 버퍼 오버런)로 끝났다.
`1.1.1`은 그 로그에 이름이 나온 Sodium만 뺀 구성이었다.

이후 사용자가 `1.1.0` 인스턴스에서 **Sodium JAR만 비활성화한 뒤 Windows MultiMC 실행과 서버 접속에
성공**했다고 알려 왔다. 그래서 `1.1.2`·`1.1.3`에서도 Sodium을 넣지 않는다.

이 관찰로 알 수 있는 것과 없는 것:

- 알 수 있는 것: Sodium을 뺀 나머지 구성은 해당 PC에서 실행되고 서버 접속도 된다. 크래시가
  나머지 15개 모드 조합만으로 재현되지는 않는다.
- 알 수 없는 것: 네이티브 종료 코드의 정확한 원인. 로그의 `IllegalStateException`이 종료의 직접
  원인인지, 드라이버·런처 실행 인자·Sodium 설정 중 무엇이 관여했는지는 확정하지 못했다.
  "Sodium이 없으면 동작한다"가 "Sodium이 단독 원인이다"를 뜻하지는 않는다.

하지 않은 것:

- 크래시 원인을 규명하지 않았다. 런타임 수정이나 우회 설정(JVM 인자, Sodium 옵션, 드라이버 설정)도
  넣지 않았다.
- **`1.1.3` 팩 자체를 Windows에서 실행해 보지 않았다.** 사용자가 실행과 접속을 함께 확인한 것은
  Sodium을 꺼 둔 `1.1.0` 인스턴스뿐이다. `1.1.3`은 리눅스 개발 환경에서 파일 수준 검증만 했다.
- Sodium이 빠진 만큼 `1.1.0`에서 기대하던 렌더링 성능 향상은 없다. 프레임 차이는 측정하지 않았다.

입력 lock(`mods-26.3-client-extra.lock.json`)에서는 Sodium 항목을 지우고 같은 근거와 이후 관찰
결과를 `removed`에 남겼다. 빌더가 조용히 건너뛰는 경로는 없다. 사용자는 이전 인스턴스를 재사용하지
말고 **새 MultiMC 인스턴스**로 가져와야 이전 `sodium-neoforge-0.9.2+mc26.3.jar`가 남지 않는다.
수동 설치라면 그 JAR을 먼저 지운다.

빌더는 재빌드 때 `dist/`에 이번 버전의 MultiMC 인스턴스 ZIP만 남기고 이전 버전 인스턴스 ZIP은
**휴지통으로 보낸다**. 옛 구성을 실수로 다시 가져오는 경로를 없애기 위해서다. 영구 삭제가 아니라
`gio trash`를 쓰므로 `~/.local/share/Trash/`에 파일과 `.trashinfo`(원래 `dist/` 경로, 삭제 시각)가
남고 언제든 되돌릴 수 있다. `gio`가 없거나 명령이 실패하면 빌드를 중단하며 되돌릴 수 없는 삭제로
대체하지 않는다. 이전 버전의 `.mrpack`과 수동 ZIP은 비교용으로 `dist/`에 그대로 둔다. 이 정리는
설치용 파일에만 해당하고, **런처에 이미 가져와 둔 인스턴스는 별개 파일이라 영향을 받지 않는다.**
사용자가 Sodium을 꺼 두고 쓰던 `1.1.0` 인스턴스는 MultiMC 안에 그대로 남아 있다.

## 이번에 추가한 모드

| 모드 | 고정 버전 | 채널 | 출처 | 배포 위치 |
| --- | --- | --- | --- | --- |
| [Lithium](https://modrinth.com/mod/lithium) | `mc26.3-0.26.1-neoforge` | release | 서버 lock | 서버·클라이언트 공통 |
| [Clumps](https://modrinth.com/mod/clumps) | `26.3.2` | release | 서버 lock | 서버·클라이언트 공통 |
| [Sodium](https://modrinth.com/mod/sodium) | `mc26.3-0.9.2-neoforge` | release | 클라이언트 입력 lock | 클라이언트 전용 (`1.1.1`~`1.1.3` 제외, `1.1.4`에서 Iris 의존성으로 복귀) |
| [ImmediatelyFast](https://modrinth.com/mod/immediatelyfast) | `1.17.1+26.3-neoforge` | release | 클라이언트 입력 lock | 클라이언트 전용 |
| [Mouse Tweaks](https://modrinth.com/mod/mouse-tweaks) | `26.3-2.31-neoforge` | release | 클라이언트 입력 lock | 클라이언트 전용 |
| [Xaero's Minimap](https://modrinth.com/mod/xaeros-minimap) | `neoforge-26.3-26.5.3` | release | 클라이언트 입력 lock | 클라이언트 전용 (`1.1.2`에만 포함, `1.1.3`에서 제외) |
| [JourneyMap](https://modrinth.com/mod/journeymap) | `26.3-6.0.9+neoforge` | release | 클라이언트 입력 lock | 클라이언트 전용 (`1.1.3`에서 추가, JAR은 팩에 담지 않음) |

Jade(`26.3.1+neoforge`)와 Packet Fixer(`3.3.7`)는 1.0.0 팩에 이미 들어 있었고 이번에 바꾸지
않았다. 사용자가 요청한 Jade는 새로 추가하지 않고 기존 항목 하나를 그대로 쓴다.

### 고정한 파일과 해시

| 파일 | 크기 | SHA-1 | 대조 기준 |
| --- | --- | --- | --- |
| `lithium-neoforge-0.26.1+mc26.3.jar` | 904073 | `5ba04eef3fde45de80ff4ce10d057f10c2cfe01f` | `mods-26.3.lock.json` |
| `Clumps-neoforge-26.3-26.3.2.jar` | 18766 | `aeb6689f2f3840021a8af0b02248ece388d262ab` | `mods-26.3.lock.json` |
| `sodium-neoforge-0.9.2+mc26.3.jar` | 1208169 | `9015607e5ae2c5b9692ebf05113f9caca6ec41bf` | Modrinth 버전 `VHtnT9Q4` |
| `ImmediatelyFast-NeoForge-1.17.1+26.3.jar` | 109497 | `a072863c3b4e7cfed81899d8d3115839a161a708` | Modrinth 버전 `4SovUFpn` |
| `MouseTweaks-neoforge-mc26.3-2.31.jar` | 74133 | `de224d4e3c270b749345c3a6703b51336a3ce5d3` | Modrinth 버전 `f4tPRGDq` |
| `xaerominimap-neoforge-26.3-26.5.3.jar` | 2178209 | `16bf8eae1710a57bc398b796cd4475d0dcce7564` | Modrinth 버전 `6zzKPjLq` |
| `journeymap-neoforge-26.3-6.0.9.jar` | 4352830 | `e4d81a338a2997d6d517d5f7b51b607277f21733` | Modrinth 버전 `OCuB6UWq` |

Xaero's Minimap 행은 지난 구성의 기록이며 현재 팩에는 들어가지 않는다. Sodium은 `1.1.4`에서 다시 들어간다.
JourneyMap은 해시를 대조하지만 JAR을 팩에 담지는 않는다. 위 "라이선스 때문에 JAR을 팩에 담지
않는다" 절을 참고한다.

SHA-512와 전체 메타데이터는 [mods-26.3-client-extra.lock.json](../mods-26.3-client-extra.lock.json)과
빌더가 생성하는 [mods-26.3-client.lock.json](../mods-26.3-client.lock.json)에 있다. 빌더는
패키징 전에 두 lock의 크기·SHA-512를 실제 JAR과 대조하고, 불일치하면 중단한다. JAR을 담지 않는
모드도 같은 대조를 거치며, 검증에 쓴 로컬 사본은 산출물에 들어가지 않는다.

### 선택 근거

- **Sodium**: Modrinth 프로젝트 `AANobbMI`의 26.3 NeoForge 파일 중 `version_type=release`인
  `VHtnT9Q4`를 골랐다. 더 최신 파일은 alpha 채널이라 쓰지 않는다. 배포 파일이 하나뿐이라
  primary JAR 선택 문제가 없다. JAR의 `neoforge.mods.toml`은 `neoforge [26.1.2.10-beta,)`만
  필수로 선언하며 고정한 `26.3.0.8-beta`가 이를 만족한다.
- **Lithium**: 서버 lock에 이미 있는 `efIED0FC`(release)를 그대로 쓴다. Modrinth가
  `client_side=optional`, `server_side=optional`로 표시하고 JAR이 `minecraft [26.3, 26.4)`만
  요구한다. 서버와 클라이언트 양쪽에서 동작하므로 서버와 **같은 파일**을 팩에 담아
  버전 불일치를 막는다. 1.0.0 팩의 "클라이언트 필수 아님" 제외 근거는 이번에 철회했다.
- **Clumps**: 서버 lock에 이미 있는 `kV095inH`(release)를 그대로 쓴다. Modrinth가
  `client_side=optional`, `server_side=optional`로 표시한다. 멀티플레이에서는 이미 서버가
  경험치 오브를 병합하므로 클라이언트 설치는 싱글플레이(통합 서버)에서 같은 동작을 얻기
  위한 것이다. 서버 구성은 바꾸지 않았고 재시작도 하지 않았다.
- **ImmediatelyFast**: Modrinth 프로젝트 `5ZwdcRci`의 `4SovUFpn`(release)를 골랐다. 이
  릴리스의 변경 사항이 "Fixed crash on NeoForge"다. 배포 파일이 하나뿐이고 외부 API 모드를
  필수 의존성으로 요구하지 않는다. JAR은 `minecraft [26.3.0]`와 `neoforge [26.3.0.0,26.4.0.0)`를
  `side = "CLIENT"`로 선언하며, `type`을 생략했으므로 NeoForge 기본값인 `required`로 본다.
  고정한 Minecraft `26.3`과 NeoForge `26.3.0.8-beta`가 두 범위를 모두 만족한다.
- **Mouse Tweaks**: Modrinth 프로젝트 `aC3cM3Vq`의 `f4tPRGDq`(release)를 골랐다. 이 버전은
  파일 3개를 배포하며 `primary=true`인 `MouseTweaks-neoforge-mc26.3-2.31.jar`만 담는다.
  `-api.jar`(`file_type=dev-jar`)와 `-src.jar`(`file_type=sources-jar`)는 개발용이라 제외했다.
  JAR은 필수 의존성을 선언하지 않는다.
- **Xaero's Minimap**: Modrinth 프로젝트 `1bokaNcj`의 `6zzKPjLq`(release, 26.3 NeoForge)를 골라
  `1.1.2`에 담았다. 메타데이터상 버전 범위와 내장 `xaerolib` 의존성은 모두 충족됐지만, 위 크래시
  A/B 때문에 `1.1.3`에서 뺐다. 파일 검증이 런타임 동작을 보증하지 않는다는 사례다.
- **JourneyMap**: Modrinth 프로젝트 `lfHFW1mp`의 `OCuB6UWq`(release, 26.3 NeoForge)를 골랐다.
  배포 파일이 `primary=true`인 하나뿐이다. JAR의 `neoforge.mods.toml`은 모드 ID `journeymap`,
  NeoForge `[26.1.2.22-beta,)`, `commonnetworking [1.0.22,)`를 필수로 선언한다. 고정한
  `26.3.0.8-beta`가 첫 범위를 만족하고 `commonnetworking`은 내장 JAR이 제공한다.
  **Modrinth 버전 메타데이터의 `dependencies`는 비어 있으므로 필수 의존성은 JAR 메타데이터가
  기준이다.** JAR 루트에 `fabric.mod.json`이 있으나 `id=journeymap-wrongloader`,
  `version="not a fabric mod"`인 안내용 스텁이며 이 파일은 NeoForge 전용 배포물이다.

### 내장(JarJar) 의존성

JourneyMap은 `META-INF/jarjar/`에 세 JAR을 내장한다. `common-networking-neoforge-26.3-1.1.1.jar`가
모드 ID `commonnetworking`을, `journeymap-api-neoforge-26.3-2.0.0.jar`가 `journeymap_api`를 선언하며,
`pngj-2.1.0.jar`는 모드 메타데이터가 없는 라이브러리다. 앞 두 JAR은 `neoforge`(또는 `minecraft`)만
요구하고 더 이상 중첩된 JAR이 없다. 필수 의존 `commonnetworking`이 이렇게 충족되므로 따로 설치할
모드가 없다.

Xaero's Minimap(`1.1.2` 기준 기록)은 `META-INF/jarjar/xaerolib-neoforge-26.3-1.7.17.jar`를 내장했고,
이 내부 JAR이 모드 ID `xaerolib`를 선언해 필수 의존성을 충족했다.

Sodium은 `META-INF/jarjar/net.caffeinemc.sodium-neoforge-0.9.2+mc26.3-mod.jar`를 내장한다.
이 내부 JAR도 같은 모드 ID `sodium`을 선언하는 공식 배포 구조다(`1.1.0` 기준 기록이며 `1.1.1`부터
팩에는 Sodium이 없다). Lithium, Clumps, ImmediatelyFast, Mouse Tweaks에는 내장 JAR이 없다.

추가한 JAR 중 JourneyMap을 뺀 나머지는 `fabric.mod.json`이 없고 `META-INF/neoforge.mods.toml`만
가진다. JourneyMap은 두 파일을 모두 갖지만 `fabric.mod.json`이 위에 적은 안내용 스텁이라 Fabric
배포물이 아니다. Fabric 전용 모드는 팩에 들어가지 않는다.

## 라이선스

| 모드 | 라이선스 | 근거 |
| --- | --- | --- |
| Lithium | `LGPL-3.0-only` | JAR의 `neoforge.mods.toml` 선언과 Modrinth 프로젝트 메타데이터가 일치 |
| Clumps | `MIT` | JAR의 `neoforge.mods.toml` 선언과 Modrinth 프로젝트 메타데이터가 일치 |
| ImmediatelyFast | `LGPL-3.0-or-later` | JAR의 `neoforge.mods.toml` 선언, 루트 `LICENSE_ImmediatelyFast` 사본, Modrinth 프로젝트 메타데이터가 일치 |
| Sodium | `LicenseRef-Polyform-Shield-1.0.0` | JAR 루트 `LICENSE.md`(PolyForm Shield 1.0.0)와 `neoforge.mods.toml`의 `Polyform-Shield-1.0.0` 선언 |
| Mouse Tweaks | `BSD-3-Clause` | JAR의 `neoforge.mods.toml` 선언과 Modrinth 프로젝트 메타데이터가 일치 |
| Xaero's Minimap | `LicenseRef-All-Rights-Reserved` | JAR의 `neoforge.mods.toml` 선언, 루트 `LICENSE_xaerohud` 사본, Modrinth 프로젝트 메타데이터가 일치 |
| JourneyMap | `LicenseRef-All-Rights-Reserved` | JAR의 `neoforge.mods.toml`이 `All rights reserved`를 선언하고 루트 `license.txt`가 재배포를 금지, Modrinth 프로젝트 메타데이터도 일치 |

PolyForm Shield 1.0.0은 원본 사본 배포를 허용하고 경쟁 제품 용도만 금지한다. 이 팩은 Aziran
서버 접속용 비공개 배포물이며 공개 재업로드·재호스팅에는 쓰지 않는다. 세부 표기는 팩에 함께
담기는 `LICENSES.md`에 생성된다.

JourneyMap도 All Rights Reserved지만 조건이 다르다. Xaero's Minimap은 출처 링크를 표기하면
모드팩에 JAR을 담는 것을 허가했던 반면, **JourneyMap은 번들 자체를 금지하고 설치·실행 과정에서
CurseForge 또는 Modrinth에서 내려받는 모드팩만 허가한다.** 그래서 표기만으로는 부족하고 산출물
구성을 바꿔야 했다. 처리 내용은 위 "라이선스 때문에 JAR을 팩에 담지 않는다" 절에 있다. 출처 표기는
팩의 `README.md`("모드 출처 표기" 절)와 `LICENSES.md`에 공식 사이트·Modrinth·라이선스 문서 링크를
넣어 지켰다.

`1.1.2`까지 적용했던 Xaero's Minimap의 표기 조건은 다음과 같았다. 수익화는 CurseForge·Modrinth를
통해서만 허용되고, CurseForge·Modrinth 밖에서 배포하는 모드팩은 공식 페이지 링크로 제작자를
표기해야 하며, 모드팩 이름·설명이 제작자 모드와 혼동되면 안 된다. `1.1.3`에는 이 모드가 없다.

## 넣지 않은 모드

| 대상 | 판단 |
| --- | --- |
| [Indium](https://modrinth.com/mod/indium) | Fabric 전용이라 NeoForge 26.3 배포가 없다. 제작자가 Sodium 0.6 이상과 호환되지 않는다고 밝혔고, 이 Sodium 빌드는 `neoforge.mods.toml`에서 `"fabric:provides" = ["indium"]`로 Indium이 제공하던 렌더 API를 직접 제공한다. 필요하지 않다. |
| Let Me Despawn (+ Almanac) | 이미 서버에 설치돼 있다. Modrinth가 `client_side=unsupported`로 표시한다. |
| Chunky | 청크 프리젠 도구이고 서버 콘솔에서만 쓴다. 클라이언트 렌더링 최적화가 아니다. 서버 구성은 건드리지 않았다. |
| spark | 프로파일링 도구다. 클라이언트 렌더링 최적화가 아니다. |
| Carpet | Fabric 전용이며 26.3 NeoForge 배포가 없다. 클라이언트 렌더링 최적화도 아니다. |
| Neruina | 조회한 배포처에 26.3 파일이 없다. 틱 오류 복구용이라 클라이언트 렌더링 최적화가 아니다. |
| Mod Menu | Fabric 전용 설정 UI다. NeoForge에는 로더 기본 모드 목록 화면이 있어 필요하지 않다. |
| Iris / 셰이더 | 이 Sodium 버전의 배포 노트가 "Iris is not yet compatible"이라고 명시한다. 추가하지 않았다. `1.1.1`부터 Sodium 자체가 없다. |
| [Xaero's Minimap](https://modrinth.com/mod/xaeros-minimap) | `1.1.2`에 담았다가 `1.1.3`에서 뺐다. Windows `0xc0000005` 크래시의 방아쇠로 A/B 확인됐기 때문이다. 모드 결함 판정은 아니며 다른 버전은 시험하지 않았다. |
| [Open Parties and Claims](https://modrinth.com/mod/open-parties-and-claims), [Xaero's World Map](https://modrinth.com/mod/xaeros-world-map) | Xaero's Minimap의 **선택** 의존성이었다. 그 모드를 뺀 `1.1.3`에는 근거 자체가 없다. |
| [JourneyMap 서버 설치](https://modrinth.com/mod/journeymap) | 모드는 클라이언트 팩에 넣지만 서버에는 설치하지 않는다. Modrinth `server_side=optional`이고 지도 표시는 클라이언트만으로 동작한다. |

Chunky·spark·Let Me Despawn은 서버 전용 구성 항목이다. 이번 작업에서 서버 모드 디렉터리,
서버 lock, Compose 설정은 수정하지 않았다. Clumps와 Lithium은 이미 서버에 설치돼 있어
새로 설치할 것이 없었고, 클라이언트 팩에 같은 파일을 담기만 했다.

## 검증한 것과 하지 않은 것

검증한 것:

- `1.1.3`의 수동 ZIP과 MultiMC ZIP은 모드 JAR 15개를 담는다. JourneyMap JAR은 라이선스 때문에
  두 ZIP 어디에도 없다. `.mrpack`은 Modrinth CDN 다운로드 항목 15개(JourneyMap 포함)와
  `client-overrides`의 내장 JAR 1개(Farmer's Delight)로 모드 16개를 설치한다.
- 세 산출물 어디에도 Sodium JAR과 Xaero's Minimap JAR이 없다.
- 16개 전부의 크기·SHA-1·SHA-512가 서버 lock 또는 Modrinth 배포 메타데이터와 일치한다.
  `1.1.1`·`1.1.2`에서 이어진 15개는 바이트 단위로 동일하다(`1.1.2` 수동 ZIP과 직접 대조).
- 새로 받은 `journeymap-neoforge-26.3-6.0.9.jar`는 Modrinth API가 알려 준 크기 4352830,
  SHA-1 `e4d81a33…`, SHA-512 `1ed0fc68…`와 일치하고 ZIP 무결성을 통과한다.
- `.mrpack`의 JourneyMap 항목은 `https://cdn.modrinth.com/data/lfHFW1mp/versions/OCuB6UWq/…`
  하나만 `downloads`로 가지며 해시·크기가 고정 목록과 일치한다.
- 내장 JAR을 포함한 모든 `required` 의존성이 팩 안에서 충족된다. JourneyMap의
  `commonnetworking`은 내장 JAR이 제공한다.
- 고정한 NeoForge `26.3.0.8-beta`와 Minecraft `26.3`이 각 JAR이 선언한 버전 범위를 만족한다.
- Fabric 전용 모드, Indium, 서버 전용 모드, 서버 설정·월드·백업 파일이 들어 있지 않다.
- 재빌드가 `dist/`의 이전 버전 `.mrpack`과 수동 ZIP을 지우지 않는다. 이전 버전의 MultiMC 인스턴스
  ZIP만 `gio trash`로 휴지통에 보내며 `~/.local/share/Trash/`에서 복구할 수 있다.
- 서버 lock, `server-data-26.3-neoforge/`, Compose 설정, 월드, 백업은 바꾸지 않았다.

검증하지 않은 것:

- **`1.1.3`을 Windows에서 실행하거나 서버에 접속해 보지 않았다.** 리눅스 개발 환경에서 파일·메타
  데이터 검증만 했다. **JourneyMap이 `1.1.2`의 크래시를 해결한다는 확인은 없다.**
- 실행과 서버 접속이 함께 확인된 유일한 구성은 여전히 Sodium JAR을 꺼 둔 `1.1.0` 인스턴스다.
- `1.1.2`의 `0xc0000005`는 A/B로 방아쇠가 Xaero's Minimap임을 확인했을 뿐, 네이티브 실패
  메커니즘은 규명하지 않았다. `1.1.0`의 `0xc0000409`도 마찬가지이며 두 크래시가 같은 뿌리인지
  모른다. A/B로 방아쇠를 특정한 것이 원인 분석을 대신하지는 않는다.
- JourneyMap의 지도·웨이포인트 동작과 다른 모드와의 렌더링 충돌 여부를 확인하지 않았다.
- `.mrpack`을 MultiMC로 실제 가져와 보지 않았다. MultiMC 위키가 `.mrpack`을 가져올 수 있는
  형식으로 적고 있다는 문서 근거까지만 확인했고, 위키는 최소 버전을 명시하지 않는다.
- 사용자가 README 절차대로 JourneyMap을 직접 받아 넣었을 때의 동작도 확인하지 않았다.
- MultiMC 인스턴스 ZIP은 아카이브 구조와 컴포넌트 UID·버전을 파일 수준에서만 확인했다.
- Lithium·ImmediatelyFast·Mouse Tweaks의 성능 개선 폭은 파일 검증으로 알 수 없다. Sodium을 뺀
  만큼 `1.1.0`보다 프레임이 낮아질 수 있으나 측정하지 않았다.
- 세 산출물 ZIP은 항목 시각을 담으므로 재빌드해도 바이트 단위로 같지 않다. 아카이브 SHA-256은
  빌드마다 달라지며, 고정 목록에는 마지막 빌드 값이 기록된다. 안에 담긴 모드 JAR은 동일하다.
- NeoForge `26.3.0.8-beta`와 베타 모드(JEI, Curios, Farmer's Delight 이식판)의 런타임
  안정성은 이전과 마찬가지로 확인되지 않았다.

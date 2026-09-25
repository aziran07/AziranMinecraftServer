# 서버 접속 안내 웹사이트

## 구성

- 웹 주소: `https://aziran.uk`
- 게임 주소: `mc.aziran.uk` (Java Edition 기본 포트 25565)
- 웹 원본: `site/`의 정적 HTML·CSS·JavaScript
- 호스팅: GitHub Pages, `.github/workflows/pages.yml`로 `site/`만 배포
- 다운로드: 사이트 소스의 다운로드 링크·팩 이름·모드 수(21개)는 `client-1.1.10`으로 바꿨고 인벤토리 정렬 안내 절(`#sorting`)을 더했다. **`client-1.1.10`은 2026-09-25 14:16 UTC 일반 릴리스(latest)로 공개했다**(https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.10). 순서는 소스 커밋 `f65d6c2`에 태그만 푸시 → 초안 릴리스에 6개 자산 업로드 후 내려받아 크기·SHA-256 확인 → 일반 릴리스 공개 → `main` 푸시였다. Pages 배포 실행 `36146375828`이 성공했고, 공개 사이트가 HTTP 200으로 `client-1.1.10` 링크·팩 이름·모드 21개·`#sorting` 절을 제공하며 링크된 `.mrpack`과 배포 페이지가 HTTP 200임을 확인했다. 새 버전은 Release를 먼저 공개한 뒤 사이트를 배포해야 하며, 순서가 바뀌면 다운로드 링크가 동작하지 않는다. 1.1.10은 1.1.9에 클라이언트 전용 Nemo's Inventory Sorting만 더해 서버를 바꾸지 않는다. 아래는 1.1.9 기록이다. GitHub Release `client-1.1.9`의 `.mrpack`과 설치·라이선스 문서. 1.1.9 당시 사이트 소스의 다운로드 링크·팩 이름·모드 수(20개)는 `client-1.1.9`로 바꿨고 Traveler's Backpack 안내 절(`#backpack`)을 더했다. **`client-1.1.9`는 2026-09-25 일반 릴리스(latest)로 공개했다**(https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.9). 1.1.9는 1.1.8에 Traveler's Backpack을 더한 판이다. 순서는 초안 릴리스에 자산을 올려 크기·SHA-256 확인 → 월드만 보호 백업한 뒤 서버에 설치·재시작(13:44~13:46 UTC, healthy 확인) → 초안을 일반 릴리스로 공개였다. 사용자 결정으로 1.1.9부터 일반 릴리스로 공개하며, Iris는 계속 미병합 PR 로컬 빌드라고 밝힌다. 작업 브랜치에서는 아래와 같이 Pages 보호 규칙 때문에 사이트가 배포되지 않았고, PR #7을 `main`에 병합(`0a0056b`)한 뒤 배포 실행 `36144033527`이 성공해 해결됐다(2026-09-25). 아래는 1.1.8 기록이다. **`client-1.1.8` 사전 릴리스는 2026-09-25 공개했고**(https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.8) 6개 자산의 크기·SHA-256을 로컬 산출물과 대조했다. 1.1.8은 Modonomicon만 26.3-2.7.0으로 바꾼 판이다. 순서는 Release 공개 → 서버 Modonomicon 교체·재시작(2026-09-25 13:13~13:19 UTC 완료. 이때 만든 전체 데이터 백업은 사용자 요청으로 13:23 UTC 영구 삭제해 남아 있지 않다) → 사이트 배포다. **사이트 배포는 아래 1.1.7과 같은 Pages 환경 보호 규칙 때문에 당시에는 되지 않았다**(PR #7 병합 뒤 해결). 서버가 2.7.0으로 바뀌었으므로 1.1.7 이하 클라이언트의 접속 여부는 확인하지 않았다. 아래는 1.1.7 기록이다. `client-1.1.7` 사전 릴리스는 2026-09-25 공개했다. 세 아카이브와 `README.md`, `LICENSES.md`, `SHA256SUMS.txt`가 업로드되어 있고 크기·SHA-256을 확인했다. 1.1.7 당시 사이트 소스의 링크는 `client-1.1.7`을 가리켰지만 [배포 실행](https://github.com/aziran07/AziranMinecraftServer/actions/runs/36117840610)은 `github-pages` 환경 브랜치 보호 규칙에 거부됐다. 허용 브랜치는 `main`과 `feat/join-guide`이며, 당시 작업 브랜치는 제외되어 있었다. PR #7을 `main`에 병합한 뒤 배포 실행 `36144033527`이 성공했다. 환경 보호 규칙은 변경하지 않았다. 1.1.7은 모드 구성이 1.1.6과 같고 리소스팩만 더했으므로 서버 재시작이 필요 없었고, 당시 1.1.6 인스턴스도 접속할 수 있었다(서버 2.7.0 교체 이후는 확인하지 않음). (1.1.6은 GitHub 사전 릴리스(prerelease) [`client-1.1.6`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.6)으로 공개했다. 미병합 PR 빌드인 실험 단계 Iris를 담았기 때문에 사전 릴리스로 둔다. 이전 버전 1.1.5·1.1.4는 사전 릴리스 `client-1.1.5`·`client-1.1.4`로 공개했고 그대로 둔다. 새 버전은 Release를 먼저 만든 뒤 사이트를 배포하며, 순서가 바뀌면 다운로드 링크가 동작하지 않는다. 1.1.6은 서버에 넣은 무덤 모드 Simple Tomb을 담았고, 서버가 이 모드를 활성화하면 1.1.5 이하로는 접속할 수 없으므로 Release 공개 → 사이트 배포 → 서버 재시작 순서를 지켰다. 2026-09-25 이 순서로 활성화했다)
- DNS: Cloudflare에서 웹 도메인은 GitHub Pages로, 게임 도메인은 서버 공인 IP로 연결

Cloudflare Workers API는 현재 연결 권한으로 인증 오류를 반환해 사용할 수 없었다.
웹 호스팅은 GitHub Pages로 구성하며, Cloudflare DNS only와 GitHub Pages의 HTTPS 인증서를 사용한다.
기존 서버의 Nginx·Portainer·Grafana·Prometheus·cAdvisor는 이 웹사이트를 위해 실행하지 않는다.

## 안내 내용과 확인 범위

Prism Launcher 설치와 Minecraft Java 계정 로그인, `.mrpack`을 새 인스턴스로 가져오기,
멀티플레이 접속 순서로 안내한다. 이전 팩을 쓰던 사람에게는 1.1.10을 새 인스턴스로 다시 가져오도록 안내하고, 1.1.10은 클라이언트 전용 모드만 더했으므로 1.1.9 인스턴스도 접속할 수 있다고 밝힌다(서버 조건이 같다는 판단이며 접속 시험은 하지 않음). 정렬 절은 Sort·Move Same 등 버튼(이름은 영어), Shift로 핫바 포함, `Alt` 슬롯 잠금, `Ctrl`+`F` 검색, 단축키는 미지정이라 조작 설정에서 지정한다는 점, Nemo의 끌기·분할·휠 이동은 팩 설정에서 껐고 기존 Mouse Tweaks 조작은 그대로라는 점, 기존 인스턴스는 모드와 `config/nemos-inventory-sorting/general.json`을 직접 넣어야 한다는 점, 모드 전용 화면에서의 호환은 확인하지 않았다는 점을 안내한다. 서버에 Traveler's Backpack을 설치했으므로(2026-09-25) 이 모드가 없는 1.1.8 이하 인스턴스는 접속할 수 없다고 밝힌다(실제 접속 거부는 시험하지 않음). 배낭 절은 Curios Back 슬롯 착용, 팩의 단축키(배낭 열기 `Y`, 도구 바꾸기 `Z`)와 상류 기본값 `B`가 Occultism 가방·Tom's Simple Storage 터미널·JourneyMap 웨이포인트와 겹쳐 새 인스턴스만 `Y`로 정했다는 점, 기존 인스턴스는 조작 설정에서 바꾸는 방법, 서버 기본 설정의 사망 시 배낭 처리를 안내하고 무덤 모드·Curios와의 동작은 확인하지 않았다고 밝힌다. 1.1.5 이후 팩으로 새로 만든 인스턴스는 팩의 `servers.dat` 덕분에 멀티플레이 목록에
`Aziran`(`mc.aziran.uk`) 서버가 이미 들어 있으며, 목록에 없는 기존 인스턴스는 `mc.aziran.uk`를 직접 추가하도록 안내한다. `.mrpack`을 압축 해제하거나 기존 모드
폴더에 덮어쓰지 않는다. 팩은 Minecraft 26.3, NeoForge 26.3.0.8-beta, Java 25를 사용한다.

사용자가 배포한 팩 1.1.4로 새로 만든 인스턴스를 Windows에서 두 번 연속 실행하는 데 성공했다고
보고했다. 이 보고는 실행 성공만 다루며 그 두 실행의 서버 접속·셰이더 적용 여부는 포함하지 않는다.
그 전 사용자의 1.1.4 시험 인스턴스는 첫 실행에서 셰이더 적용과 서버 접속에 성공했고, 두 번째
실행은 Occultism 사역마 단축키(`key.keyboard.-1`) 문제로 실패했다. 기존 인스턴스 복사본에서
그 값을 `key.keyboard.unknown`으로 바꾸자 두 번 연속 실행·접속에 성공했다. 1.1.5는 모드·셰이더 구성이
1.1.4와 같고 `servers.dat`만 더했다. 1.1.6은 1.1.5에 Simple Tomb 1.9.0만 더했다. 1.1.7은 1.1.6의 모드·셰이더·`servers.dat`에 리소스팩 세 개와
`options.txt`의 언어(`lang:ko_kr`)·기본 리소스팩 줄을 더했다. 1.1.8은 1.1.7에서 Modonomicon만 26.3-2.7.0으로 바꿨다(상류 커밋 `d74b6f2`). 1.1.9는 1.1.8에 Traveler's Backpack 11.4.0을 더했다. 1.1.10은 1.1.9에 Nemo's Inventory Sorting 26.3-1.22.1을 더했다. 1.1.5~1.1.10 아카이브로 새로 만든 인스턴스의
게임 실행과 멀티플레이 목록 표시, 1.1.7의 번역 표시·리소스팩 적용, 1.1.8의 책 화면 끌기 수정, 1.1.9의 배낭 사용, 1.1.10의 정렬 버튼은 아직 확인하지 않았다. 안내 페이지의 다운로드
제공과 파일 검증은 게임 실행 검증을 뜻하지 않는다. JourneyMap·Nemo's Inventory Sorting JAR과 Complementary Reimagined
셰이더 팩, Vanilla Experience+ 리소스팩은 팩 안에 포함하지 않으며, 런처가 설치 중 공식 Modrinth 배포처에서 받는다.
페이지는 셰이더 켜는 법, 리소스팩 기본값(한국어·번역 팩 켜짐, Stay True·Vanilla Experience+ 꺼짐)과
켜고 끄는 법·우선순위, JourneyMap 전체 지도 단축키, 기존 인스턴스의 `options.txt` 수정 방법을
함께 안내한다. Stay True는 1.21.5용이라 26.3 호환을 확인하지 않았고 일부 표현은 OptiFine이 필요하다고 밝힌다.

## 검증

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_join_guide.py -v
node --check site/app.js
node --test tests/test_join_guide_copy.cjs
```

배포 후 HTTPS 페이지·CSS·JavaScript 응답과 모바일 화면, 주소 복사 버튼을 확인한다.
다운로드한 `.mrpack`의 SHA-256을 `mods-26.3-client.lock.json`의 `archives` 값과 대조한다.
HTTP 접속은 HTTPS로 리다이렉트해야 하며 `mc.aziran.uk`의 게임 서버 연결도 유지되어야 한다.

2026-09-22 배포 검증 결과(당시 공개 팩 `client-1.1.3` 기준):

- 공개 HTTPS 페이지·CSS·JavaScript가 모두 200으로 응답하고 인증서 검증을 통과했다.
- 실제 공개 사이트를 Chromium의 1280px·360px 화면에서 확인했다. 가로 넘침과 JavaScript
  오류가 없었고, 주소 복사 결과가 `mc.aziran.uk`와 일치했다.
- Python 테스트 6개와 JavaScript 테스트 2개가 통과했다.
- 공개 릴리스에서 다시 받은 `.mrpack`의 SHA-256이 잠금 파일과 일치했다.
- GitHub Pages의 HTTPS 강제를 활성화했다. `/index.html`의 HTTP→HTTPS 및 `www`→루트
  리다이렉트는 확인했다. 설정 직후 루트 HTTP 응답에는 이전 200 응답의 CDN 캐시가 남아 있었다.
- 외부 Minecraft 상태 조회에서 26.3 서버가 온라인이었다. 서버 컨테이너 재시작은 없었다.

## 업데이트

사이트 내용은 `site/`에서 수정한다. GitHub Actions가 `site/`만 업로드하므로 저장소 루트의
서버 구성·운영 데이터가 웹사이트에 공개되지 않는다. 최초 작업 브랜치는 `feat/join-guide`다.
`github-pages` 배포 환경에서는 `main`과 `feat/join-guide`만 허용한다. 워크플로는 두 브랜치의
사이트 변경 시 배포하며, 최초 브랜치를 병합·삭제한 후에는 `main`에서 갱신한다.
팩을 변경할 때는 새 버전의 릴리스를 만들고 다운로드 링크와 페이지의 버전을 함께 갱신한다.
이미 공개한 버전의 파일을 덮어쓰지 않는다.

## 관리 서비스

루트 Compose에서는 Minecraft와 웹 RCON만 활성화한다. 웹 RCON은 Docker 내부 포트만
사용하므로 공개 웹사이트에 관리자 화면이나 RCON 자격 증명을 제공하지 않는다.
나머지 보조 서비스 정의는 복원할 수 있도록 주석으로 보존한다.


### 1.1.7 독립 검증 기록

Codex가 클라이언트 빌더를 다시 실행했고, 클라이언트·번역·가이드 관련 Python 검사 30개와 JavaScript 검사 2개가 통과했다. 내부 링크·앵커와 HTML ID 중복을 확인했고, 기존 모드 19개의 목록·해시, 셰이더, 서버 목록이 유지됨을 확인했다. 공개한 6개 Release 자산의 크기·SHA-256이 로컬 파일과 일치한다. Orca 브라우저 스냅샷은 `runtime_unavailable`(연결 종료)로 실패해 시각적 화면 검증을 완료하지 못했다. 게임 내 확인도 아직 수행하지 않았다.

# 서버 접속 안내 웹사이트

## 구성

- 웹 주소: `https://aziran.uk`
- 게임 주소: `mc.aziran.uk` (Java Edition 기본 포트 25565)
- 웹 원본: `site/`의 정적 HTML·CSS·JavaScript
- 호스팅: GitHub Pages, `.github/workflows/pages.yml`로 `site/`만 배포
- 다운로드: GitHub Release `client-1.1.5`의 `.mrpack`과 설치·라이선스 문서 (1.1.5는 GitHub 사전 릴리스(prerelease) [`client-1.1.5`](https://github.com/aziran07/AziranMinecraftServer/releases/tag/client-1.1.5)로 공개했다. 미병합 PR 빌드인 실험 단계 Iris를 담았기 때문에 사전 릴리스로 둔다. 이전 버전 1.1.4는 사전 릴리스 `client-1.1.4`로 공개했고 그대로 둔다. 새 버전은 Release를 먼저 만든 뒤 사이트를 배포하며, 순서가 바뀌면 다운로드 링크가 동작하지 않는다)
- DNS: Cloudflare에서 웹 도메인은 GitHub Pages로, 게임 도메인은 서버 공인 IP로 연결

Cloudflare Workers API는 현재 연결 권한으로 인증 오류를 반환해 사용할 수 없었다.
웹 호스팅은 GitHub Pages로 구성하며, Cloudflare DNS only와 GitHub Pages의 HTTPS 인증서를 사용한다.
기존 서버의 Nginx·Portainer·Grafana·Prometheus·cAdvisor는 이 웹사이트를 위해 실행하지 않는다.

## 안내 내용과 확인 범위

Prism Launcher 설치와 Minecraft Java 계정 로그인, `.mrpack`을 새 인스턴스로 가져오기,
멀티플레이 접속 순서로 안내한다. 1.1.5로 새로 만든 인스턴스는 팩의 `servers.dat` 덕분에 멀티플레이 목록에
`Aziran`(`mc.aziran.uk`) 서버가 이미 들어 있으며, 목록에 없는 기존 인스턴스는 `mc.aziran.uk`를 직접 추가하도록 안내한다. `.mrpack`을 압축 해제하거나 기존 모드
폴더에 덮어쓰지 않는다. 팩은 Minecraft 26.3, NeoForge 26.3.0.8-beta, Java 25를 사용한다.

사용자가 배포한 팩 1.1.4로 새로 만든 인스턴스를 Windows에서 두 번 연속 실행하는 데 성공했다고
보고했다. 이 보고는 실행 성공만 다루며 그 두 실행의 서버 접속·셰이더 적용 여부는 포함하지 않는다.
그 전 사용자의 1.1.4 시험 인스턴스는 첫 실행에서 셰이더 적용과 서버 접속에 성공했고, 두 번째
실행은 Occultism 사역마 단축키(`key.keyboard.-1`) 문제로 실패했다. 기존 인스턴스 복사본에서
그 값을 `key.keyboard.unknown`으로 바꾸자 두 번 연속 실행·접속에 성공했다. 1.1.5는 모드·셰이더 구성이
1.1.4와 같고 `servers.dat`만 더했다. 1.1.5 아카이브로 새로 만든 인스턴스의 게임 실행과 멀티플레이 목록 표시는
아직 확인하지 않았다. 안내 페이지의 다운로드
제공과 파일 검증은 게임 실행 검증을 뜻하지 않는다. JourneyMap JAR과 Complementary Reimagined
셰이더 팩은 팩 안에 포함하지 않으며, 런처가 설치 중 공식 Modrinth 배포처에서 받는다.
페이지는 셰이더 켜는 법, JourneyMap 전체 지도 단축키, 기존 인스턴스의 `options.txt` 수정 방법을
함께 안내한다.

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

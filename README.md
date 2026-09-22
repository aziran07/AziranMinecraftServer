# Aziran Minecraft Server

Minecraft Java Edition 1.21 Fabric 서버와 웹 관리·모니터링 서비스를 Docker Compose로 운영하는 저장소입니다. 자체 게임 로직 소스는 없으며, 서비스 구성은 이 저장소에서, 게임 기능은 외부 모드와 로컬 서버 데이터에서 관리합니다.

## 작업 시작

1. [AGENTS.md](AGENTS.md): Codex/Claude 역할, Orca 협업 절차, 데이터 보호·검증 규칙.
2. [프로젝트 지도](docs/PROJECT_MAP.md): 기능별 구현 위치, 네트워크, 로컬 모드, 변경·검증 기준.
3. [CLAUDE.md](CLAUDE.md): Claude 구현 작업 시작 시 확인할 사항.

| 목적 | 먼저 볼 파일 |
| --- | --- |
| 게임 버전·메모리·난이도, 서비스 구성 | [docker-compose.yml](docker-compose.yml) |
| 도메인·HTTPS·관리 UI·WebSocket | [default.conf.template](nginx/templates/default.conf.template) |
| 게임 접속·지도 TCP 전달 | [minecraft.conf.template](nginx/templates/minecraft.conf.template) |
| 컨테이너 지표 수집 | [prometheus.yml](prometheus.yml) |
| 월드 백업·보존 기간 | [mc_backup.sh](mc_backup.sh) |

## 실행 전 확인

- Docker와 Docker Compose 플러그인이 필요합니다.
- `.env`와 `nginx/cert.pem`, `nginx/key.pem`을 별도로 준비해야 합니다. 필요한 변수 이름은 프로젝트 지도에 있습니다.
- 모드, 월드, Grafana 대시보드 등 영속 데이터는 Git에 포함되지 않습니다. 새 clone만으로 기존 운영 서버를 재현할 수 없습니다.
- Compose는 호스트의 `80`, `443`, `25565`, `8123` TCP 포트를 사용합니다.

설정 검사:

```sh
docker compose config --quiet
bash -n mc_backup.sh
git diff --check
```

실제 서버를 시작하기로 한 작업에서만 실행합니다. 기존 `server-data/`가 있으면 해당 월드와 설정을 사용합니다.

```sh
docker compose up -d --build
docker compose ps
```

백업 스크립트는 오래된 백업을 삭제하므로 검사용으로 실행하지 않습니다. 현재 동작과 확인된 제약은 프로젝트 지도를 참고하세요.

## 기존 참고 자료

- [구축 참고 글](https://velog.io/@windsekirun/Deploy-Minecraft-by-Docker)
- [기존 README 이미지](https://github.com/aziran07/AziranWebServer/assets/161091473/8bd8483b-b211-409e-ac08-e5d0f8c16f8d)

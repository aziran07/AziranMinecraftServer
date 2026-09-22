# Minecraft 26.3 새 서버 준비

2026-09-22 기준. 기존 서버 데이터 백업과 준비 문서 작성까지 완료했다. 운영 설정 변경, 모드 설치, 새 월드 생성 및 새 서버 기동은 수행하지 않았다. 실제 구현은 후속 작업에서 **새 브랜치**로 진행한다.

## 작업 대상

- 저장소: `/home/pilon1945/AziranMinecraftServer`
- 구성: `docker-compose.yml`, Minecraft `1.21`, `FABRIC`, Java 21 이미지
- 데이터: `./server-data:/data`, 즉 이 저장소의 `server-data/`
- Docker에 남아 있는 이름이 `minecraft`인 종료된 컨테이너는 별도 프로젝트 `/home/pilon1945/minecraft202506`에 속한다. 이름만 보고 이 저장소의 서버로 판단하지 않는다.

## 백업 완료 기록

- 위치: `/home/pilon1945/minecraft-preservation-20260922-wdMZzW/legacy-fabric-1.21.tar`
- 크기: `127125217280` 바이트 (약 119 GiB)
- 체크섬 파일: 같은 경로의 `legacy-fabric-1.21.tar.sha256`
- 포함 경로: `server-data`, `docker-compose.yml`, `mc_backup.sh`, `.env`, `nginx`, `prometheus.yml`
- 검증: tar 생성, `tar --acls --xattrs --compare` 원본 대조, SHA-256 기록을 순서대로 실행했고 전체 명령이 종료 코드 0으로 완료됐다.
- 백업 디렉터리는 권한 700, 아카이브는 권한 600으로 보존한다. 인증서와 자격 증명이 포함되므로 Git에 추가하거나 공개하지 않는다.
- 원본 데이터는 유지했다. 이번 백업은 기존 자동 삭제 대상 디렉터리 밖에 저장했으며, 기존 백업 삭제 기능이 있는 `mc_backup.sh`는 실행하지 않았다.
- 기존 백업 아카이브와 Grafana/Prometheus/Portainer의 영속 데이터는 이번 게임 서버 백업 범위에 포함하지 않는다.
- 원본 대조는 완료했지만 별도 환경에서 실제 서버를 복원해 기동하는 검증은 수행하지 않았다.

## 새 서버 설계

1. Minecraft 버전은 `26.3`으로 고정한다. 새 월드를 기본 설계로 하고, 기존 데이터 디렉터리를 새 버전의 `/data`에 연결하지 않는다.
2. 사용할 모드/모드팩의 26.3 지원을 확인한 뒤 로더를 결정한다. 기존 Fabric 구성을 참고하되 구형 JAR을 그대로 복사하지 않는다.
3. 26.x의 Java 25 요구사항에 맞는 이미지와 선택한 로더의 정확한 배포 버전을 검증한다.
4. 별도 Compose 프로젝트와 데이터 경로를 사용하고 컨테이너 이름 및 호스트 포트 충돌을 점검한다. 기존 프록시 변경은 신규 구성 검증 후 진행한다.
5. 모드 설치 명세에는 버전과 다운로드 출처를 기록한다. 모드 목록 확정 전에는 모드 서버 개설 완료로 보고하지 않는다.
6. 사용자 요청에 따라 여기서 준비 작업을 마무리한다. 후속 구현은 새 브랜치에서 진행한다.

공식 자료:

- [Minecraft Java 26.3](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3)
- [Fabric 26.3 안내](https://www.fabricmc.net/2026/09/15/263.html)
- [NeoForged Java 25 전환 안내](https://neoforged.net/news/26.1release/)

## 모드 검토 방향

사용자는 모드가 아직 미정이며 농사와 탐험 구조물을 중심으로 원한다. 이 저장소의 `server-data/mods`에서 확인한 관련 모드는 다음과 같다. 파일 존재만 확인했으며 실제 로드 여부와 26.3 호환성을 검증한 목록은 아니다.

| 기존 모드 | 확인한 JAR 버전 |
| --- | --- |
| Croptopia | 1.21-FABRIC-3.0.5 |
| Terralith | 1.21 v2.5.3 |
| Structory | 1.21 v1.3.5 |
| Structory Towers | 1.21 v1.0.7 |
| Nullscape | 1.21 v1.2.6 |
| The Bumblezone | 7.6.10+1.21-fabric |

이 목록을 기준으로 농사·탐험 콘텐츠를 검토한다. 별도 NeoForge 프로젝트에서 조사했던 Farmer’s Delight, Cooking for Blockheads, Towns and Towers, Twilight Forest 등은 이 저장소의 기존 설치 모드로 취급하지 않는다. 새로 추가할 후보와 로더는 후속 작업에서 결정한다.

## 후속 구현의 수용 기준

- 구성: `docker compose config --quiet` 성공, 버전 26.3/Java 25/선택한 로더 일치, 기존 데이터 마운트와 컨테이너 이름 및 호스트 포트 충돌 없음.
- 모드: 각 모드와 의존성이 26.3 및 선택한 로더를 지원한다는 배포 메타데이터 확인.
- 실행: 별도 검증 환경에서 정상 기동 로그, 로더/모드 로드 및 정상 종료 확인.
- 역할: Codex가 설계·검증·테스트를 소유하고 Claude가 운영 구성과 스크립트를 구현한다.

이번 작업에서 기존 구성의 `docker compose config --quiet`와 `bash -n mc_backup.sh`는 통과했다. Compose의 기존 `version` 속성 obsolete 경고는 남아 있다. 이는 새 26.3 구성이나 실제 서버 실행을 검증한 결과가 아니다.

## 구현 환경의 제약

설치된 스킬의 실행 파일 탐색 규칙에 따라 선택한 `orca-ide`로 CLI 가이드를 조회했으나 `zsh:1: command not found: orca-ide` (종료 코드 127)가 발생했다. 저장소 AGENTS.md에 따라 운영 구현은 시작하지 않았다. 후속 작업은 Orca/Claude 실행 환경 복구 또는 사용자의 명시적인 작업 방식 변경이 필요하다.

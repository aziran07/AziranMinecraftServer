# Chunky 청크 프리젠 현황

대상 서버는 `aziran-minecraft-26-3` 컨테이너(데이터 경로 `server-data-26.3-neoforge/`)이며 Chunky 1.5.4를 사용한다. 명령은 `docker exec aziran-minecraft-26-3 rcon-cli "<command>"`로 실행한다. 공식 명령 문법은 [Chunky Commands](https://github.com/pop4959/Chunky/wiki/Commands)를 따른다.

## 최종 목표

사용자가 정한 최종 목표는 아래 반경의 원형(circle) 영역이다. 중심은 `0, 0`으로 적용했다.

| 차원 | 목표 반경(블록) | 2026-09-22 완료 반경 | 당시 반지름 비율 |
| --- | --- | --- | --- |
| `minecraft:overworld` | 8000 | 800 | 1/10 |
| `minecraft:the_nether` | 1000 | 100 | 1/10 |
| `minecraft:the_end` | 8000 | 0 (미실행) | 0 |

2026-09-22에는 목표 전체를 실행하거나 예약하지 않았다. 당시 작업은 사용자가 명시적으로 지시한 "목표 반경의 1/10"만 수행했다. 엔드는 당시 지시에 따라 프리젠하지 않았고, 월드 폴더에도 `dimensions/minecraft/the_end/region`이 생성되지 않은 상태였다. 2026-09-23에는 사용자가 엔드를 포함한 전체 목표를 승인해 아래의 무인 프리젠 캠페인을 시작했다.

## 2026-09-22 실행 결과

네더를 먼저 끝낸 뒤 오버월드를 실행하는 순차 방식으로 부하를 제한했다. 각 작업 전에 `chunky world` / `chunky shape` / `chunky center` / `chunky radius`를 명시적으로 지정하고 `chunky selection`으로 확인한 뒤 `chunky start`를 실행했다. 실행 시점의 접속 플레이어는 0명이었다.

| 차원 | 선택 | 처리 청크 | 소요 시간 | 서버 로그 시각 |
| --- | --- | --- | --- | --- |
| `minecraft:the_nether` | circle, center 0 0, radius 100 | 225 (100.00%) | 0:00:01 | 21:31:55 시작 → 21:31:56 완료 |
| `minecraft:overworld` | circle, center 0 0, radius 800 | 10201 (100.00%) | 0:00:48 | 21:32:21 시작 → 21:33:07 완료 |

완료 근거는 서버 로그의 `[Chunky] Task finished ... (100.00%)` 두 줄이며, 이후 `chunky progress`는 `No tasks running.`을 반환한다. 처리 속도는 오버월드 기준 85~190 cps 범위였다.

작업 이전 Chunky 선택값은 `minecraft:overworld` / square / center 0, 0 / radius 500(기본값)이었고 실행 중인 작업은 없었다. 작업 후 남아 있는 선택값은 마지막으로 지정한 `minecraft:overworld` / circle / center 0, 0 / radius 800이다.

## 실행 후 상태 확인

- 컨테이너: `status=running`, `health=healthy`, `RestartCount=0`. 프리젠 전후로 변화 없음.
- 프리젠 구간(21:31~21:33) 로그에는 Chunky 진행 메시지와 RCON 접속 기록 외의 항목이 없다. 오류, 예외, `Can't keep up`, 워치독 경고는 발생하지 않았다.
- 기동 시점(21:24)의 기존 경고(JNA/Unsafe 네이티브 접근 경고, udev 미탐지, Occultism의 Curios 통합 더미 폴백, `apothic_enchanting` 데이터맵 경고, macOS 전용 netty kqueue 로그 어펜더 예외)은 프리젠 이전부터 있던 기존 항목이며 이번 작업과 무관하다. 자세한 내용은 [최초 기동 결과](SERVER_26_3_PREPARATION.md#최초-기동-결과-2026-09-22)를 참고한다.
- 리전 파일: `world/dimensions/minecraft/overworld/region` 16개(103M), `.../the_nether/region` 4개(5.5M). `.../the_end/`에는 `region` 디렉터리가 없다. 26.3은 `DIM-1`/`DIM1` 대신 `dimensions/<namespace>/<dimension>/` 구조를 사용한다.

## 남은 작업과 주의점

- 목표 반경까지의 잔여 프리젠은 아래 [무인 프리젠 컨트롤러](#무인-프리젠-컨트롤러)로 진행 중이다. 오버월드 8000은 이전 800 대비 100배 면적이다. 실제 디스크 사용량은 지형·엔티티·압축에 따라 달라진다.
- `chunky continue` 는 저장된 작업 전체를 재개하므로, 특정 차원만 진행하려면 사용하지 않는다. `chunky trim`은 선택 영역 밖 청크를 삭제하므로 사용하지 않는다.
- `server-data-26.3-neoforge/`의 정기 백업 정책은 아직 없다. 기존 `mc_backup.sh`는 `server-data/world`를 대상으로 한다. 캠페인 시작 전 별도 일회성 백업을 만들었다(아래 기록).

## 2026-09-23 캠페인 시작 기록

- 시작 직전 접속자 0명, Chunky 실행 작업 없음 확인 후 서버를 정상 중지했다.
- `server-data-26.3-neoforge/` 전체를 `/home/pilon1945/aziran-26.3-protected-backups/pre-chunky-2026-09-23-0536.tar`로 백업했다. 크기 301,342,720바이트, SHA-256 `6a3fa086925c47b867c41cff1579c897284dc41ede8367ca9c22620ed57ad168`. `tar -tf`로 `world/level.dat`, `server.properties`, `config/chunky/config.json` 포함을 확인했다. 기존 자동 삭제 대상 `minecraft_backups/` 밖에 보관한다.
- 기능 브랜치의 Compose 파일을 메인 체크아웃의 프로젝트 디렉터리·`.env`에 적용하고, 스크립트 마운트만 기능 worktree의 파일로 지정했다. 서버는 `pause-when-empty-seconds=-1`, `healthy`, 재시작 0회, 접속자 0명으로 기동했다.
- 컨트롤러가 네더 반경 1000을 14:37:02 KST에 시작해 14:37:34 KST에 완료로 기록했고, 오버월드 반경 8000을 14:37:35 KST에 시작했다. 14:37경 RCON `chunky progress`에서 오버월드 진행률 1.00%를 확인했다. 엔드는 아직 시작하지 않았다. 이후 진행 상태는 `docker logs aziran-chunky-idle-pregen`, `docker exec aziran-minecraft-26-3 rcon-cli 'chunky progress'`, `chunky-idle-state/chunky_idle_state.json`으로 확인한다.

## 무인 프리젠 컨트롤러

`scripts/chunky_idle_controller.py`는 접속자가 0명일 때만 목표 반경까지 프리젠을 진행한다. Compose 서비스 `chunky-idle-pregen`(컨테이너 `aziran-chunky-idle-pregen`)이 서버와 같은 `itzg/minecraft-server:java25-alpine` 이미지의 `python3`로 실행한다. 표준 라이브러리만 쓰며 RCON 비밀번호는 `RCON_PASSWORD` 환경변수에서만 읽고 로그에 남기지 않는다.

### 대상과 순서

모두 `circle`, 중심 `0 0`이며 앞 대상의 완료가 확인된 뒤에만 다음 대상을 시작한다. 엔드는 사용자가 이번 캠페인에 명시적으로 포함했다.

| 순서 | 차원 | 반경 | 실행 명령 |
| --- | --- | --- | --- |
| 1 | `minecraft:the_nether` | 1000 | `chunky start minecraft:the_nether circle 0 0 1000` |
| 2 | `minecraft:overworld` | 8000 | `chunky start minecraft:overworld circle 0 0 8000` |
| 3 | `minecraft:the_end` | 8000 | `chunky start minecraft:the_end circle 0 0 8000` |

재개와 일시정지는 차원을 지정한 `chunky continue <world>` / `chunky pause <world>`만 쓴다. Chunky 1.5.4 JAR의 명령 클래스에서 두 명령이 월드 인자를 받는 것을 확인했다. `chunky cancel`, `chunky trim`, `chunky confirm`은 사용하지 않는다. `confirm`을 쓰지 않으므로 Chunky가 확인을 요구하는 응답(같은 월드의 재개 가능 작업 존재, 디스크 부족 경고)은 오류로 멈춘다.

### 동작

1. 약 1초마다 RCON `list`를 실행한다. RCON 연결은 계속 유지해 폴링마다 새 접속 로그가 생기지 않게 한다.
2. 접속자가 1명 이상이면 현재 대상에 `chunky pause <world>`를 보내 진행 상황을 저장하고 멈춘다.
3. 접속자가 0명이면 `chunky progress`로 실행 상태를 보고, 멈춰 있으면 `config/chunky/tasks/<namespace>/<world>.properties`를 읽어 처음이면 `start`, 저장된 작업(`cancelled=false`)이면 `continue`한다. 두 명령은 `execute unless entity @a run chunky start ...` / `execute unless entity @a run chunky continue <world>`로 보내 서버가 실행 직전에 접속자를 다시 확인한다(26.3 실서버에서 `execute unless entity @a run chunky progress` 동작 확인). 응답이 비어 있으면 그 사이 플레이어가 들어와 명령이 실행되지 않은 것으로 보고, 상태 파일을 명령 전 값으로 되돌린 뒤 재개 대기(`--resume-delay`)부터 다시 시작한다.
4. 플레이어를 본 뒤에는 `--resume-delay`(기본 30초) 동안 접속자가 계속 0명이어야 재개한다. 재접속이 잦을 때 시작·정지가 반복되지 않게 하기 위한 값이다.
5. 컨트롤러가 SIGTERM(`docker compose stop`)이나 오류로 끝날 때는 현재 대상을 pause한 뒤 종료한다.

### 일시정지 지연(유한함)

즉시 정지가 아니라 폴링 기반이다. 플레이어가 `list`에 잡힌 뒤(로그인 완료 후)부터 최대 폴링 간격 1초 + RCON 왕복 시간 안에 `pause`를 보낸다. Chunky는 pause를 받은 뒤 이미 요청한 청크 생성이 끝나야 작업 스레드를 멈추므로, 접속 직후 몇 초 동안은 생성 부하가 남을 수 있다. `list`가 0명을 반환한 직후 접속한 경우는 `execute unless entity @a` 조건이 서버에서 명령 실행과 같은 시점에 확인하므로 `start`/`continue`가 실행되지 않는다. 다만 플레이어 엔티티가 생기기 전(로그인 처리 중)에는 조건이 0명으로 보므로, 그 순간 시작된 작업은 다음 폴링에서 멈춘다.

### 오류 처리

- `list`나 `chunky progress` 응답을 해석할 수 없으면 시작·재개하지 않고, 현재 대상을 pause한 뒤 exit 1로 끝난다(Compose `restart: on-failure`가 재시작하며 원인이 남아 있으면 같은 오류가 반복되어 드러난다).
- RCON 연결 실패(서버 중지·재시작)는 아무 명령도 보내지 않고 오류를 로그에 남긴 뒤 연결될 때까지 기다린다. 첫 실패와 이후 60초마다 로그를 남긴다. 인증 실패는 즉시 exit 1.
- 이 캠페인이 시작하지 않은 Chunky 작업이 돌고 있거나, 상태 파일과 Chunky 작업 파일이 어긋나면 exit 1.
- 시작 시 `config/chunky/config.json`의 `continueOnRestart`가 `false`가 아니면 exit 1. `true`면 서버 기동 시 Chunky가 접속자 확인 없이 작업을 재개하기 때문이다.
- 상태 디렉터리의 잠금 파일(`chunky_idle_state.lock`)로 컨트롤러 중복 실행을 막는다.

### 완료 판정

Chunky는 작업이 끝나거나 취소되면 둘 다 작업 파일에 `cancelled=true`를 저장한다. 그래서 컨트롤러는 다음 두 조건이 모두 맞을 때만 대상을 완료로 기록하고 다음 차원으로 넘어간다.

- 작업 파일이 대상과 같은 선택(`circle`, 중심 0/0, 대상 반경)이고 `cancelled=true`
- 마지막 `start`/`continue` 직전에 기록한 `logs/latest.log` 위치 이후에 `[Chunky] Task finished for <world>. Processed: N chunks (100.00%)` 줄이 있음

`cancelled=true`인데 완료 줄이 15초 안에 보이지 않으면(외부에서 cancel한 경우 등) exit 1. 그 사이 서버가 재시작해 `latest.log`가 교체됐다면 완료를 확인할 수 없으므로 역시 exit 1로 멈춘다. 이때 `logs/*.log.gz`에서 완료 줄을 직접 확인한 뒤 상태 파일을 수동으로 고친다(아래 참고).

### 상태와 재시작

- 캠페인 상태: 호스트 `./chunky-idle-state/chunky_idle_state.json`(컨테이너 `/state`, Git 제외). `completed`(완료 차원 목록), `active`(진행 중 대상, `phase`, 로그 위치)를 원자적으로 저장한다.
- 차원별 진행률: Chunky 자체 작업 파일(`server-data-26.3-neoforge/config/chunky/tasks/`). 컨트롤러는 읽기 전용으로 마운트한다.
- 서버가 재시작되면 Chunky가 작업을 저장한 채 멈춰 있고(`continueOnRestart=false`), 컨트롤러가 접속자 0명을 확인한 뒤 `continue`한다. 컨트롤러가 재시작되면 상태 파일로 이어서 진행한다.
- `start` 전에 `phase: starting`을 먼저 기록하므로, 명령 직후 중단돼도 재기동 시 작업 파일을 보고 `start`를 다시 보내거나 `continue`한다.
- 상태 파일 수동 수정은 컨트롤러를 멈춘 상태에서만 한다. 완료를 직접 확인한 차원은 `completed` 끝에 추가하고 `active`를 `null`로 둔다.

### 운영 절차

배포 전 확인: 백업, 디스크 여유(오버월드 8000은 이전 800의 100배 면적), `.env`의 `RCON_PASSWORD`.

- 백업은 기존 `mc_backup.sh`와 `minecraft_backups/`를 쓰지 않는다. 그 스크립트는 해당 디렉터리의 파일을 삭제한다. 26.3용 별도 보호 경로를 먼저 정한다.
- Compose 상대 경로(`./server-data-26.3-neoforge`, `./chunky-idle-state`, 기본 스크립트 경로)는 `--project-directory` 기준이다. 기능 worktree를 프로젝트 디렉터리로 쓰지 않고, 실제 서버 데이터가 있는 메인 체크아웃(`/home/pilon1945/AziranMinecraftServer`)과 그 `.env`를 쓴다.
- 컨트롤러 스크립트 마운트 경로는 `CHUNKY_IDLE_CONTROLLER_SCRIPT`로 바꿀 수 있고 기본값은 `./scripts/chunky_idle_controller.py`다. PR 병합 전에는 스크립트가 기능 worktree에만 있으므로, 메인 체크아웃에 파일을 만들지 않고 이 변수로 worktree의 스크립트를 가리킨다. 병합 후에는 변수 없이 메인 체크아웃에서 실행한다.

PR 병합 전 후보 배포(기능 worktree의 Compose 설정과 스크립트, 메인 체크아웃의 데이터와 `.env`):

```sh
MAIN=/home/pilon1945/AziranMinecraftServer
FEATURE=/home/pilon1945/AziranMinecraftServer-chunky-idle-pregen
mkdir -p "$MAIN/chunky-idle-state"   # 컨테이너 사용자 1000:1000이 쓸 수 있어야 한다
export CHUNKY_IDLE_CONTROLLER_SCRIPT="$FEATURE/scripts/chunky_idle_controller.py"
compose() { docker compose --project-directory "$MAIN" --env-file "$MAIN/.env" -f "$FEATURE/docker-compose.yml" "$@"; }
compose config --quiet
compose up -d minecraft                    # PAUSE_WHEN_EMPTY_SECONDS=-1 반영(컨테이너 재생성)
compose up -d --no-deps chunky-idle-pregen
compose logs -f chunky-idle-pregen
```

병합 후 배포(메인 체크아웃에서):

```sh
cd /home/pilon1945/AziranMinecraftServer
mkdir -p chunky-idle-state
docker compose up -d minecraft
docker compose up -d --no-deps chunky-idle-pregen
docker compose logs -f chunky-idle-pregen
```

- `--no-deps`는 컨트롤러를 올릴 때 `minecraft` 컨테이너가 의도치 않게 다시 만들어지지 않게 한다. 서버 재생성은 앞 줄에서 명시적으로만 한다.
- 컨트롤러는 한 번만 판단하고 끝나는 모드를 두지 않는다. 시작·재개한 작업은 항상 같은 프로세스가 접속자를 감시한다.
- 캠페인 중에는 Chunky를 직접 조작하지 않는다. 컨트롤러가 pause를 확인한 뒤 접속자가 있는 동안에는 `list`만 폴링하므로, 그 사이 수동 `chunky continue`는 감지하지 못한다.
- 컨트롤러가 SIGKILL이나 호스트 장애로 pause 없이 죽으면 생성이 감시 없이 계속될 수 있다. 서버 재시작 시에는 Chunky가 자동 재개하지 않는다.
- 모든 대상이 끝나면 컨트롤러는 exit 0으로 멈춘다. 그 뒤 `PAUSE_WHEN_EMPTY_SECONDS` 설정과 `chunky-idle-pregen` 서비스를 docker-compose.yml에서 제거한다.

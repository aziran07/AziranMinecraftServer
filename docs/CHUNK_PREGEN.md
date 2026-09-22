# Chunky 청크 프리젠 현황

대상 서버는 `aziran-minecraft-26-3` 컨테이너(데이터 경로 `server-data-26.3-neoforge/`)이며 Chunky 1.5.4를 사용한다. 명령은 `docker exec aziran-minecraft-26-3 rcon-cli "<command>"`로 실행한다. 공식 명령 문법은 [Chunky Commands](https://github.com/pop4959/Chunky/wiki/Commands)를 따른다.

## 최종 목표

사용자가 정한 최종 목표는 아래 반경의 원형(circle) 영역이다. 중심은 `0, 0`으로 적용했다.

| 차원 | 목표 반경(블록) | 현재 완료 반경 | 반지름 비율 |
| --- | --- | --- | --- |
| `minecraft:overworld` | 8000 | 800 | 1/10 |
| `minecraft:the_nether` | 1000 | 100 | 1/10 |
| `minecraft:the_end` | 8000 | 0 (미실행) | 0 |

목표 전체는 아직 실행하거나 예약하지 않았다. 이번 작업은 사용자가 명시적으로 지시한 "목표 반경의 1/10"만 수행했다. 엔드는 사용자 지시에 따라 프리젠하지 않았고, 월드 폴더에도 `dimensions/minecraft/the_end/region`이 생성되지 않은 상태다.

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

- 목표 반경까지의 잔여 프리젠은 사용자 지시가 있을 때만 실행한다. 오버월드 8000은 이번 800 대비 100배 면적이다. 현재 생성 범위는 목표 면적의 약 1%이며, 실제 디스크 사용량은 지형·엔티티·압축에 따라 달라진다. 실행 전 디스크 여유와 백업 정책을 확인해야 한다.
- `chunky continue` 는 저장된 작업 전체를 재개하므로, 특정 차원만 진행하려면 사용하지 않는다. `chunky trim`은 선택 영역 밖 청크를 삭제하므로 사용하지 않는다.
- `server-data-26.3-neoforge/` 용 백업 정책이 아직 없다. 기존 `mc_backup.sh`는 `server-data/world`를 대상으로 한다.

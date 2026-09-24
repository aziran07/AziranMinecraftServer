# 26.3 서버 백업과 복원

정기 백업은 운영 서버의 `server-data-26.3-neoforge/world/` 전체(모든 차원)를 `minecraft_backups/`에 tar로 저장한다. 2026-09-24에 첫 수동 백업을 실행해 11GB 파일 생성, `world/level.dat` 확인, 서버 healthy·재시작 0회를 확인했다. 정기 백업은 **월드만** 포함하고 원본과 같은 호스트에 있다. 모드·설정까지 필요한 배포 전 보호 백업과 전체 데이터 복원은 아래 별도 절차를 따른다.

## 정기 월드 백업

### 일정과 동작

운영 사용자 `pilon1945`의 crontab에 다음 한 줄이 활성화돼 있다. 기존의 다른 cron 항목은 그대로 둔다.

```cron
30 * * * * /bin/bash /home/pilon1945/AziranMinecraftServer/mc_backup.sh >> /home/pilon1945/AziranMinecraftServer/minecraft_backups/mc_backup.log 2>&1
```

스크립트는 겹치는 실행을 막고, RCON으로 `save-off` → `save-all flush`를 보낸 뒤 월드 tar를 임시 파일에 만든다. tar 작성 직후 `save-on`을 보내므로 **게임 서버와 플레이는 멈추지 않지만**, 작성 중에는 자동 디스크 저장이 중단된다. 이 구간에 서버가 비정상 종료되면 그 사이의 변경을 잃을 수 있다. 2026-09-24의 11GB 첫 백업에서 `save-off`부터 `save-on`까지 약 13초였다. 이후 tar에서 `world/level.dat`를 읽어 검증하고 `26.3-world-YYYYmmdd-HHMMSS.tar`로 이름을 바꾼다. 실패하면 임시 파일을 제거하고 저장 재개를 시도하며 오류를 로그와 종료 코드에 남긴다.

성공한 백업 뒤 `minecraft_backups/`의 `26.3-world-*.tar` 중 710분 초과 파일만 삭제한다. 다른 파일과 `/home/pilon1945/aziran-26.3-protected-backups/`의 일회성 보호 백업은 삭제하지 않는다. 백업 로그는 자동 순환하지 않으므로 크기를 확인해야 한다.

### 상태 확인

```sh
crontab -l | grep mc_backup.sh
tail -n 30 /home/pilon1945/AziranMinecraftServer/minecraft_backups/mc_backup.log
find /home/pilon1945/AziranMinecraftServer/minecraft_backups -maxdepth 1 -name '26.3-world-*.tar' -type f -ls
BACKUP=/home/pilon1945/AziranMinecraftServer/minecraft_backups/26.3-world-YYYYmmdd-HHMMSS.tar
tar -tf "$BACKUP" | grep '^world/level.dat$'
```

`BACKUP`의 날짜·시각은 실제 파일 이름으로 바꾼다. 로그에서 `backup finished`와 `saving re-enabled`를 확인한다. `save-on failed`가 있으면 서버의 저장 상태를 즉시 확인하고 복구해야 한다. 백업 tar 하나가 있다고 해서 모드·서버 설정 전체를 복원할 수 있는 것은 아니다.

### 월드 복원 시 주의

복원은 자동화돼 있지 않다. 먼저 아래 [정상 종료 절차](#오프라인-전체-데이터-보호-백업)로 Minecraft를 멈추고 `exited exit=0 oom=false`와 월드 저장 로그를 확인한다. 선택한 tar가 읽히고 `world/level.dat`를 포함하는지 검사한다. 현재 `world/`를 삭제하지 말고 별도 보호 경로로 옮긴 뒤, 서버가 멈춘 상태에서 `server-data-26.3-neoforge/` 아래에 tar를 풀어 `world/`를 복원한다. 복원된 `world/level.dat`와 소유권을 확인한 뒤 서버를 시작한다. 백업은 월드만 포함하므로 모드·설정 변경까지 되돌려야 하는 경우에는 별도의 전체 데이터 백업을 사용한다.

## 오프라인 전체 데이터 보호 백업

모드 설치나 서버 구성 변경 전에 **전체 데이터 디렉터리**가 필요한 경우의 절차다. 정기 `mc_backup.sh`는 `world/`만 포함하고 오래된 정기 백업을 삭제하므로 여기에는 쓰지 않는다. 보호 백업은 자동 삭제 대상 밖인 `/home/pilon1945/aziran-26.3-protected-backups/`에 둔다.

백업은 서버를 **완전히 멈춘 뒤** 뜬다. 실행 중 `save-off`/`save-all` 상태로 `tar`를 돌리면 월드 밖 파일(모드 데이터, 설정 등)은 계속 바뀔 수 있고, 절차가 중간에 끊기면 자동 저장이 꺼진 채 남는다. 이 절차에서는 `save-off`를 쓰지 않는다.

1. 디스크 여유를 확인한다. 백업 크기는 대략 데이터 디렉터리 크기다. 여유가 부족하면 서버를 멈추기 전에 중단한다.

   ```sh
   cd /home/pilon1945/AziranMinecraftServer
   du -sh server-data-26.3-neoforge
   df -h /home/pilon1945
   ```

2. 접속자를 확인하고 공지한다. 접속자가 있으면 공지 후 몇 분 기다린다.

   ```sh
   docker exec aziran-minecraft-26-3 rcon-cli list
   docker exec aziran-minecraft-26-3 rcon-cli "say 서버 점검으로 5분 뒤 재시작합니다."
   ```

3. 서버를 정상 종료한다.

   **종료 시간 제한이 두 겹이다.** Docker의 `-t`/`stop_grace_period`는 Docker가 SIGKILL을 보내기까지의 시간일 뿐이다. 컨테이너 안에서는 itzg의 `mc-server-runner`가 SIGTERM을 받으면 서버에 `stop`을 보내고 `STOP_DURATION`(기본 60초)이 지나면 Java를 직접 죽인다. 첫 배포 시도에서 `docker compose stop -t 300 minecraft`를 썼지만 러너가 60초에 Java를 죽여 `exit=255`로 끝났다(프리젠된 약 11GB 월드 저장이 60초를 넘김). 그래서 Compose에 `STOP_DURATION: "600"`과 `stop_grace_period: 660s`를 넣었다. 다만 이 값은 **컨테이너를 다시 만들어야** 적용된다.

   현재 컨테이너에 어떤 한도가 적용돼 있는지 먼저 확인한다.

   ```sh
   docker inspect --format 'StopTimeout={{.Config.StopTimeout}} restart={{.HostConfig.RestartPolicy.Name}}' aziran-minecraft-26-3
   docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' aziran-minecraft-26-3 | grep '^STOP_DURATION=' \
     || echo "STOP_DURATION not set (runner default 60s)"
   ```

   `StopTimeout=660`과 `STOP_DURATION=600`이 모두 보이면 3-B로 간다. 하나라도 다르면(2026-09-24 이전에 만든 컨테이너) 3-A를 쓴다. 이전 컨테이너에서 `docker compose stop`/`docker stop`은 `-t`를 얼마로 주든 60초에 Java가 죽으므로 쓰지 않는다.

   **3-A. 이전 컨테이너: 게임 안 `stop`으로 직접 종료**

   게임 안 `stop`은 러너의 60초 타이머를 거치지 않는다. Java가 저장을 마치고 스스로 끝나면 러너도 같은 종료 코드로 끝난다. 기존 컨테이너의 재시작 정책은 `always`라서 그대로 두면 Java가 끝나자마자 Docker가 다시 띄우므로, 먼저 정책을 `no`로 바꾼다. 이 변경은 이 컨테이너에만 적용된다. 정상 기동 전에 재시작 정책을 `always`로 되돌린다.

   ```sh
   docker update --restart=no aziran-minecraft-26-3
   docker inspect --format 'restart={{.HostConfig.RestartPolicy.Name}}' aziran-minecraft-26-3   # restart=no
   ```

   `restart=no`가 아니면 `stop`을 보내지 않는다. 확인됐으면 로그 기준 시각을 남기고 종료한 뒤, 컨테이너가 끝날 때까지 최대 15분 기다린다. 명령은 한 줄씩 실행하고 각 상태를 확인한다.

   ```sh
   STOP_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ); echo "STOP_AT=$STOP_AT"
   docker exec aziran-minecraft-26-3 rcon-cli stop
   timeout 900 docker wait aziran-minecraft-26-3; echo "wait status=$?"
   docker inspect --format '{{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} restart={{.HostConfig.RestartPolicy.Name}}' aziran-minecraft-26-3
   docker logs --since "$STOP_AT" aziran-minecraft-26-3 2>&1 | grep -iE 'stopping server|saving worlds|saving chunks for level|done|error|exception'
   ```

   정상 종료 조건은 모두 만족해야 한다.

   - `rcon-cli stop`의 종료 상태가 0이다(`Stopping the server` 응답).
   - `docker wait`이 `0`을 출력하고 `wait status=0`이다. `wait status=124`는 15분 안에 끝나지 않았다는 뜻이다.
   - `exited exit=0 oom=false restart=no`.
   - `STOP_AT` 이후 로그에 `Stopping server` → `Saving players` → `Saving worlds` → 세 차원 모두의 `Saving chunks for level '...'/minecraft:overworld`·`minecraft:the_nether`·`minecraft:the_end`가 있고, 마지막에 `mc-server-runner`의 `Done`이 찍히며, 그 사이 저장 오류·예외가 없다. `--since`를 쓰는 이유는 이 컨테이너 로그에 첫 시도(exit 255)의 종료 기록이 남아 있기 때문이다.

   26.3(NeoForge `26.3.0.8-beta`) 서버는 종료 시 `All dimensions are saved`를 찍지 않는다. 이 문구를 완료 표시로 기다리지 않는다. 판정은 위의 RCON 성공, `exit=0 oom=false`, 세 차원의 `Saving chunks`, 러너 `Done`, 저장 오류 없음을 모두 본다.

   하나라도 어긋나면 **백업과 후속 변경을 하지 않는다.** 상태에 따라 아래처럼 되돌린 뒤 원인을 확인한다.

   - `rcon-cli stop`이 실패했다(RCON 연결 불가 등): 서버는 아직 돌고 있다. 정책만 되돌린다: `docker update --restart=always aziran-minecraft-26-3`.
   - `wait status=124`(아직 실행 중): 저장이 길어지는 중일 수 있다. `docker stop`/`docker kill`로 끊지 말고 `docker logs --since "$STOP_AT" -f aziran-minecraft-26-3`로 저장 진행을 보며 `timeout 900 docker wait aziran-minecraft-26-3`를 다시 기다린다. 끝나면 위 조건으로 다시 판정한다. 로그가 멈춰 진행이 없으면 멈춘 채 두고 원인을 조사한다.
   - 컨테이너가 끝났지만 `exit≠0`, `oom=true`, 또는 저장 완료 로그가 없다(비정상 종료): 기존 컨테이너를 **다시 만들지 않고** 정책을 되돌려 그대로 시작한다. 월드는 다음 기동 때 마지막 저장 상태로 올라온다.

     ```sh
     docker update --restart=always aziran-minecraft-26-3
     docker start aziran-minecraft-26-3
     docker inspect --format '{{.State.Status}} {{.State.Health.Status}} restart={{.HostConfig.RestartPolicy.Name}}' aziran-minecraft-26-3   # running healthy restart=always
     ```

     `healthy`가 될 때까지 몇 분 걸린다. 기동 로그의 청크·월드 로드 오류를 확인하고 원인이 풀리기 전에는 이행을 다시 시도하지 않는다.

   **3-B. 재생성 이후: Docker로 종료**

   `StopTimeout=660`, `STOP_DURATION=600`이 적용된 컨테이너는 Docker 종료로 충분하다. `-t`를 주지 않으면 Compose의 `stop_grace_period`(660초)를 쓴다.

   ```sh
   STOP_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ); echo "STOP_AT=$STOP_AT"
   docker compose stop minecraft
   docker inspect --format '{{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' aziran-minecraft-26-3
   docker logs --since "$STOP_AT" aziran-minecraft-26-3 2>&1 | grep -iE 'stopping server|saving worlds|saving chunks for level|done|error|exception'
   ```

   `docker compose stop`의 종료 상태가 0이고, `exited exit=0 oom=false`이며, `STOP_AT` 이후 로그에 `Stopping server` → `Saving worlds` → 세 차원(`overworld`·`the_nether`·`the_end`)의 `Saving chunks for level` → 러너 `Done`이 보여야 한다(3-A와 같은 판정. 26.3은 `All dimensions are saved`를 찍지 않는다). `exit=137`(Docker SIGKILL), `exit=255`/`143`(러너가 Java를 죽임), `oom=true`, 세 차원 중 `Saving chunks` 누락, 러너 `Done` 누락, 저장 중 오류 중 하나라도 있으면 백업이나 후속 변경으로 넘어가지 않고 원인을 먼저 확인한다.

   두 경우 모두 `chunky-idle-pregen` 컨트롤러는 이 동안 RCON 연결 실패를 기록하며 재연결을 기다린다.

4. 데이터 디렉터리 전체를 보호 경로에 묶고 검증한다. 아래 예시의 `BACKUP_LABEL=pre-change`는 작업 이름으로 바꾼다. 서버가 멈춘 상태에서만 실행한다.

   아래 블록은 별도 `bash -euo pipefail` 프로세스에서 돈다. 백업 생성(`tar -cf`), 목록 추출(`tar -tf`), 필수 항목 검사, 해시 생성·검증 중 하나라도 실패하면 그 자리에서 멈춘다. 실패 시에는 그때까지 만든 백업·목록·해시 파일 이름에 `.failed`를 붙여 성공한 백업처럼 보이지 않게 하고 `BACKUP FAILED: <원인>`을 출력한 뒤 종료 상태 1로 끝난다. 성공 표시는 모든 검사가 통과한 뒤 마지막 줄에만 나온다.

   ```sh
   cd /home/pilon1945/AziranMinecraftServer
   bash -euo pipefail <<'EOF'
   BACKUP_DIR=/home/pilon1945/aziran-26.3-protected-backups
   BACKUP_LABEL=pre-change
   BACKUP="$BACKUP_DIR/$BACKUP_LABEL-$(date +%F-%H%M%S).tar"
   if [ "$(docker inspect --format '{{.State.Running}}' aziran-minecraft-26-3)" != false ]; then
     echo "BACKUP FAILED: aziran-minecraft-26-3 is not stopped" >&2; exit 1
   fi
   for f in "$BACKUP" "$BACKUP.list" "$BACKUP.sha256"; do
     if [ -e "$f" ]; then echo "BACKUP FAILED: $f already exists" >&2; exit 1; fi
   done
   fail() {
     echo "BACKUP FAILED: $1" >&2
     for f in "$BACKUP" "$BACKUP.list" "$BACKUP.sha256"; do
       if [ -e "$f" ]; then mv -- "$f" "$f.failed" || echo "could not rename $f" >&2; fi
     done
     exit 1
   }
   mkdir -p "$BACKUP_DIR" || fail "mkdir $BACKUP_DIR"
   chmod 700 "$BACKUP_DIR" || fail "chmod $BACKUP_DIR"
   tar -cf "$BACKUP" server-data-26.3-neoforge || fail "tar create"
   tar -tf "$BACKUP" > "$BACKUP.list" || fail "tar list"
   REQUIRED=$(grep -cE '^server-data-26\.3-neoforge/(world/level\.dat|server\.properties|mods/)$' "$BACKUP.list") \
     || fail "required entries missing from archive list"
   [ "$REQUIRED" = 3 ] || fail "required entry count $REQUIRED != 3"
   sha256sum "$BACKUP" > "$BACKUP.sha256" || fail "sha256 create"
   sha256sum -c "$BACKUP.sha256" || fail "sha256 verify"
   chmod 600 "$BACKUP" "$BACKUP.list" "$BACKUP.sha256" || fail "chmod backup files"
   echo "BACKUP VERIFIED: $BACKUP"
   EOF
   ```

   마지막 줄이 `BACKUP VERIFIED: <경로>`이고 셸의 종료 상태(`echo $?`)가 `0`이어야 다음 단계로 간다. `BACKUP FAILED`가 나오거나 종료 상태가 0이 아니면 **여기서 수동으로 멈춘다.** 후속 변경을 실행하지 않는다. 원인을 먼저 확인한다. `.failed`가 붙은 파일은 불완전한 백업이므로 롤백에 쓰지 않는다. 설치 없이 서버만 되살릴 때는 기존 컨테이너를 재생성 없이 그대로 시작한다. 3-A로 멈췄다면 재시작 정책부터 되돌린다(`docker update --restart=always aziran-minecraft-26-3` 후 `docker start aziran-minecraft-26-3`, `restart=always`와 `healthy` 확인). 출력된 백업 경로는 후속 변경과 복원에 쓰므로 기록해 둔다. 백업에는 `server.properties` 등 운영 데이터가 들어 있으므로 Git이나 공개 위치에 두지 않는다. 작업 후 데이터 증가량을 고려해 디스크 여유도 계속 확인한다.

## 전체 데이터 복원

위 오프라인 보호 백업으로 **서버 데이터 디렉터리 전체**를 되돌릴 때만 사용한다. 정기 `26.3-world-*.tar`는 형식과 범위가 다르므로 이 절차에 넣지 않는다. 접속자에게 알리고 [정상 종료 절차](#오프라인-전체-데이터-보호-백업)에 따라 서버가 완전히 멈췄는지 확인한다. 백업 tar와 `.sha256` 파일은 같은 보호 경로에 있어야 한다. 아래 `BACKUP` 값을 실제 검증된 파일 경로로 바꾼다.

```sh
cd /home/pilon1945/AziranMinecraftServer
BACKUP=/home/pilon1945/aziran-26.3-protected-backups/pre-change-YYYY-mm-dd-HHMMSS.tar
BACKUP="$BACKUP" bash -euo pipefail <<'EOF'
[ -f "$BACKUP" ] && [ -f "$BACKUP.sha256" ] || { echo "RESTORE ABORTED: backup or checksum missing" >&2; exit 1; }
if [ "$(docker inspect --format '{{.State.Running}}' aziran-minecraft-26-3)" != false ]; then
  echo "RESTORE ABORTED: aziran-minecraft-26-3 is not stopped" >&2; exit 1
fi
sha256sum -c "$BACKUP.sha256"
tar -tf "$BACKUP" | awk '$0 == "server-data-26.3-neoforge/world/level.dat" { found = 1 } END { exit !found }'
[ -d server-data-26.3-neoforge ] || { echo "RESTORE ABORTED: current data directory missing" >&2; exit 1; }
SAVED="/home/pilon1945/aziran-26.3-protected-backups/server-data-26.3-neoforge.before-restore-$(date +%F-%H%M%S)"
[ ! -e "$SAVED" ] || { echo "RESTORE ABORTED: $SAVED already exists" >&2; exit 1; }
mv server-data-26.3-neoforge "$SAVED"
tar -xf "$BACKUP"
[ -f server-data-26.3-neoforge/world/level.dat ] || { echo "RESTORE FAILED: world/level.dat missing" >&2; exit 1; }
echo "RESTORE EXTRACTED: $BACKUP; previous data retained at $SAVED"
EOF
```

해시 확인과 tar 목록 확인이 실패하면 기존 데이터는 움직이지 않는다. `RESTORE EXTRACTED`와 종료 상태 `0`이 나오지 않으면 서버를 시작하지 말고 현재 폴더와 옮겨 둔 폴더 상태를 확인한다. 복원된 파일의 소유권과 해당 작업에서 필요한 모드·설정 조합을 확인한 뒤 서버를 시작한다. 이전 데이터 폴더는 복원 결과를 확인하기 전까지 삭제하지 않는다.

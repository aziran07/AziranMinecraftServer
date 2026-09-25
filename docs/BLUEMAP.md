# BlueMap 웹 지도 (26.3 NeoForge)

현재 상태(2026-09-24): 브랜치 `bluemap-26-3`으로 운영 서버에 **BlueMap을 설치하고 Compose 네트워크 안에서 웹 지도를 띄웠다(배포 절차 1~6단계 완료).** 3-A로 정상 종료한 뒤 오프라인 보호 백업을 떴고, JAR을 설치해 `minecraft` 컨테이너를 다시 만들었으며, 운영자 결정에 따라 `accept-download: true`로 리소스를 받아 렌더링이 진행 중이다. **지도 HTTPS 원본 `webmap-nginx`를 호스트 `443`에 띄우고 로컬에서 확인했다(7단계 완료).** **프록시 `A` 레코드 `mcmap`을 만들어 `https://mcmap.aziran.uk`를 공개했고, 공개 HTTPS 200을 확인했다(8단계 완료).** 처음 계획한 Cloudflare Tunnel은 터널 생성 API가 `10000 Authentication error`로 거부돼 만들지 못했고, 운영자 승인에 따라 직접 HTTPS 원본 방식으로 바꿨다. 기존 Cloudflare Origin 인증서는 Full (strict)에서 `526`으로 거부돼, `mcmap.aziran.uk` 전용 Let's Encrypt 인증서로 바꿨다(**90일마다 수동 DNS 갱신 필요**, "원본 인증서 관리"). 결과는 아래 "검증 기록"에 있다. 아래 절차는 운영 폴더에서 실행한다.

기존 1.21 서버의 Dynmap(`8123`)은 26.3 배포가 없어 새 서버에 설치하지 않았다. 26.3 서버의 웹 지도는 BlueMap이 대신하고, 내장 웹서버 포트는 BlueMap 기본값 `8100`이다. 공개 주소는 **`https://mcmap.aziran.uk`**이며, Cloudflare 프록시(주황 구름) `A` 레코드가 서버 공인 IP의 `443`으로 연결하고, 호스트 `443`을 게시한 `webmap-nginx`가 Let's Encrypt 인증서(`mcmap.aziran.uk`)로 TLS를 종료해 Compose 네트워크 안의 `http://minecraft:8100`으로 넘긴다.

```mermaid
flowchart LR
    B[브라우저] -->|HTTPS mcmap.aziran.uk| CF[Cloudflare 엣지<br/>프록시 A 레코드]
    CF -->|HTTPS 서버 IP:443<br/>공개 인증서 strict 검증| WN[webmap-nginx 컨테이너]
    WN -->|HTTP minecraft:8100<br/>aziran-mc-network| MC[minecraft 컨테이너<br/>BlueMap 웹서버]
```

## 고정한 버전

| 항목 | 값 |
| --- | --- |
| 모드 | [BlueMap](https://modrinth.com/plugin/bluemap) (Modrinth 프로젝트 `swbUV1cr`) |
| 버전 | `5.27-neoforge`, Modrinth 버전 ID `1EXOwqA2`, release |
| 파일 | `bluemap-5.27-neoforge.jar`, 7000336바이트 |
| SHA-1 | `90507749a09c3fc2039147a4b388c2e53dd157a5` |
| SHA-512 | `10d4739243996b40d20330a78582ef405715351fb50b543194595da8cea8f9bbf9ee6d7aba8586653f42a7f6113c9f0e04b5bf61e42ac5a47c3152ea0c4b7c82` |
| 대상 | Minecraft `26.3`, 로더 `neoforge` (배포 메타데이터 `game_versions`에 26.1~26.3 포함) |
| 환경 | `server_side=required`, `client_side=unsupported`. 서버 전용 |

전체 메타데이터(URL, 내장 JAR `bluenbt`·`flow-math`, 필수 의존성)는 [mods-26.3.lock.json](../mods-26.3.lock.json)의 `BlueMap` 항목에 있다. 클라이언트 모드팩 빌더는 BlueMap을 `EXCLUSIONS`에 두어 팩에 넣지 않는다. 지도는 서버가 렌더링해 브라우저로 제공하기 때문이다.

## 저장소에서 바뀐 구성

| 파일 | 변경 |
| --- | --- |
| `docker-compose.yml` | `minecraft` 서비스가 `8100`을 호스트에 게시하지 않고 `expose`로 Compose 네트워크에만 연다. `webmap-nginx` 서비스(`nginx:1.30-alpine`, 매니페스트 목록 다이제스트 고정)를 추가했다. 호스트 `443`만 게시하고 `nginx/webmap.conf`, `nginx/cert.pem`, `nginx/key.pem`을 읽기 전용으로 마운트한다. 옛 Dynmap용 `expose: 8123`과 주석 처리된 Nginx의 `8123` 게시를 지웠다 |
| `nginx/webmap.conf` | 새 파일. `mcmap.aziran.uk` SNI만 받는 `listen 443 ssl` server 블록, `/etc/nginx/cert.pem`·`key.pem`, `proxy_pass http://minecraft:8100`. 다른 SNI는 `ssl_reject_handshake`로 거절 |
| `mods-26.3.lock.json` | BlueMap 항목 추가, `mod_count` 21 |
| `nginx/templates/default.conf.template` | `mcmap.aziran.uk`, `www.aziran.uk`/`aziran.uk`의 HTTPS 프록시 대상을 `http://minecraft:8100`으로 변경 |
| `nginx/templates/minecraft.conf.template` | Dynmap `8123` stream 블록 삭제. 게임 `25565` stream만 남는다 |
| `scripts/build_client_pack.py` | `EXCLUSIONS`에 BlueMap 추가 |

기존 `nginx` 서비스(Dockerfile로 인증서를 이미지에 복사, `80`/`443` 게시)는 Compose에서 **주석 처리된 채 비활성**이며 복원하지 않는다. 지도는 그와 별개인 `webmap-nginx`가 처리한다. 호스트 `80`·`3733`은 이 저장소와 무관한 다른 Nginx가 쓰고 있고, `www.aziran.uk`/`aziran.uk`는 GitHub Pages 사이트다. 템플릿 변경은 나중에 Nginx를 복원할 때의 경로를 맞춰 둔 것일 뿐 지금은 아무 요청도 처리하지 않는다. 웹 RCON(`4326`/`4327`)은 여전히 호스트에 게시하지 않는다.

## 공개 범위와 제약

- 지도의 공개 주소는 `https://mcmap.aziran.uk` 하나다. 브라우저 쪽 TLS는 Cloudflare 엣지가 종료하고(Universal SSL), 엣지부터 서버까지는 HTTPS로 서버 `443`에 연결한다. 서버에서는 `webmap-nginx`가 Let's Encrypt 인증서(`mcmap.aziran.uk` 단일 이름)로 TLS를 종료한다. `webmap-nginx` → `minecraft:8100` 구간만 Compose 네트워크 안의 평문 HTTP다.
- Cloudflare 영역은 원본 인증서를 strict로 검증한다(2026-09-24 공개 확인에서 Origin 인증서가 `526`으로 거부된 것이 근거다. 현재 OAuth 권한으로는 SSL 모드를 직접 읽지 못한다). 그래서 원본 인증서는 공개 CA가 발급한 것이어야 하고, 만료되면 공개 주소가 `526`을 낸다. `Flexible`이면 엣지가 서버의 `80`으로 평문 연결해 **이 저장소와 무관한 다른 Nginx**에 닿으므로 모드를 바꾸지 않는다.
- 호스트에 게시하는 것은 `webmap-nginx`의 TCP `443` 하나다. `80`은 게시하지 않으며(HTTP→HTTPS 리다이렉트는 Cloudflare 엣지 설정에 맡긴다), `8100`과 웹 RCON(`4326`/`4327`)도 게시하지 않는다. 그래서 `http://<서버 주소>:8100/` 직접 접속은 되지 않는다.
- `webmap-nginx`는 SNI가 `mcmap.aziran.uk`인 연결만 받는다. 다른 이름이나 SNI 없이 서버 IP의 `443`에 붙으면 TLS 핸드셰이크에서 `unrecognized_name`으로 거절한다.
- 서버 공인 IP의 `443`은 인터넷에서 닿을 수 있어야 한다. 공유기 포트 포워딩·호스트 방화벽 상태는 이 저장소에서 확인하지 못했다(8단계에서 공개 경로로 확인).
- DNS는 `mcmap` 레코드만 새로 만든다: 프록시된 `A mcmap → <서버 공인 IP>`(현재 `mc.aziran.uk`의 `A`와 같은 IP). 기존 `mc`, `www`, apex(`aziran.uk`) 레코드는 건드리지 않는다. `mc.aziran.uk`는 게임 접속용 레코드이므로 지도에 쓰지 않는다.
- BlueMap 웹 지도에는 로그인이 없다. 접근할 수 있는 사람은 모두 렌더링된 월드와 (기본 설정이면) 접속 중인 플레이어 위치를 본다. 접근 제한이 필요하면 Cloudflare Access 정책을 따로 정한다(현재 설계 범위 밖).

## 원본 인증서 관리

- `nginx/cert.pem`(fullchain)과 `nginx/key.pem`은 Git에서 제외된 로컬 파일이다(`.gitignore`의 `*.pem`). 이미지에 넣지 않고 `webmap-nginx`에 읽기 전용으로 마운트한다.
- 현재 인증서: Let's Encrypt(발급자 `YE2`), SAN `mcmap.aziran.uk` 하나, 2026-09-24 발급, **2026-12-23 03:09:27 UTC 만료**. certbot 5.8.0 수동 DNS-01로 받았다. 이전 Cloudflare Origin 인증서(`*.aziran.uk`, 2039-06-30 만료)는 Cloudflare가 `526`으로 거부해 교체했고, 원본은 `/home/pilon1945/aziran-26.3-protected-backups/nginx-origin-cert-2026-09-24-040714/`(디렉터리 `700`, 파일 `600`)에 보관했다.
- certbot 상태는 `sudo` 없이 사용자 디렉터리에 둔다(모두 `700`, 저장소 밖): 설정·계정·인증서 `~/.config/letsencrypt`, 작업 `~/.local/share/letsencrypt`, 로그 `~/.local/state/letsencrypt`. ACME 계정은 이메일 없이 등록했으므로 **만료 알림 메일이 오지 않는다.**
- 두 파일 모두 `600`으로 둔다(컨테이너의 Nginx 마스터 프로세스는 root로 읽는다). 키 내용을 명령 출력·채팅·로그에 붙이지 않는다.
- Compose는 두 파일을 **파일 단위**로 바인드 마운트한다. 교체할 때 `mv`·`ln`으로 새 파일을 만들면 컨테이너가 옛 inode를 계속 본다. 반드시 `cp`로 기존 파일에 덮어쓴다.
- 인증서와 키가 짝인지는 내용 대신 공개키 해시로 비교한다.

  ```sh
  openssl x509 -in nginx/cert.pem -noout -pubkey | sha256sum
  openssl pkey -in nginx/key.pem -pubout | sha256sum      # 위와 같아야 한다
  openssl x509 -in nginx/cert.pem -noout -subject -enddate -ext subjectAltName
  ```

- 인증서를 바꾸면 두 파일을 교체한 뒤 `docker compose exec webmap-nginx nginx -t`와 `docker compose exec webmap-nginx nginx -s reload`로 반영한다. 키가 노출됐으면 `certbot revoke --cert-name mcmap.aziran.uk`(아래와 같은 디렉터리 옵션)로 폐기하고 새로 발급한다.

### 수동 갱신 (만료 30일 전, 2026-11-23 무렵까지)

**자동 갱신은 없다.** certbot이 발급 뒤 "scheduled task" 안내를 찍지만, 시스템 `certbot.timer`는 root로 `/etc/letsencrypt`만 갱신하고, 수동 DNS-01 인증서는 TXT 레코드를 사람이 넣어야 해서 비대화식으로 갱신되지 않는다. 만료 전에 운영자가 직접 아래를 실행한다. `minecraft` 컨테이너와 다른 DNS 레코드는 건드리지 않는다.

1. 발급을 시작한다. certbot이 `_acme-challenge.mcmap.aziran.uk`에 넣을 TXT 값을 보여 주고 Enter를 기다린다.

   ```sh
   D="--config-dir $HOME/.config/letsencrypt --work-dir $HOME/.local/share/letsencrypt --logs-dir $HOME/.local/state/letsencrypt"
   certbot certonly $D --manual --preferred-challenges dns --cert-name mcmap.aziran.uk -d mcmap.aziran.uk --force-renewal
   ```

2. Cloudflare `aziran.uk` 영역에 TXT 레코드 `_acme-challenge.mcmap`(값은 certbot이 준 문자열, TTL 60)을 추가한다. 이름이 같은 옛 TXT가 남아 있으면 먼저 지운다. `dig +short TXT _acme-challenge.mcmap.aziran.uk @1.1.1.1`로 값이 보이면 Enter를 누른다.
3. `Successfully received certificate`가 나오면 **그 TXT 레코드만** 지운다. `mc`, `mcmap`, `www`, apex 레코드는 그대로 둔다.
4. 새 인증서와 키가 짝인지 확인하고 설치·반영한다.

   ```sh
   L=$HOME/.config/letsencrypt/live/mcmap.aziran.uk
   openssl x509 -in $L/fullchain.pem -noout -pubkey | sha256sum
   openssl pkey -in $L/privkey.pem -pubout | sha256sum          # 위와 같아야 한다
   B=/home/pilon1945/aziran-26.3-protected-backups/nginx-cert-$(date +%F-%H%M%S)
   mkdir -m 700 "$B" && cp -p nginx/cert.pem nginx/key.pem "$B"/ && chmod 600 "$B"/*.pem
   cp $L/fullchain.pem nginx/cert.pem && cp $L/privkey.pem nginx/key.pem && chmod 600 nginx/cert.pem nginx/key.pem
   docker compose exec webmap-nginx nginx -t && docker compose exec webmap-nginx nginx -s reload
   ```

5. 8단계 3번의 공개 경로 확인을 다시 하고, `openssl x509 -in nginx/cert.pem -noout -enddate`로 새 만료일을 이 문서에 적는다. 실패하면 백업한 두 파일을 같은 방식(`cp`)으로 되돌리고 다시 reload한다.

## 배포 절차

배포하기로 결정한 뒤에만 실행한다. (이전 계획의 0단계 Cloudflare 터널·토큰 준비는 폐기했다.) 이 브랜치를 운영 폴더 `/home/pilon1945/AziranMinecraftServer`에 체크아웃한 상태를 전제로 한다. `8100` `expose`와 JAR을 반영하려면 `minecraft` 컨테이너를 다시 만들어야 하므로 **서버가 재시작된다.** 백업은 서버를 정상 종료한 오프라인 상태에서 뜨므로 공지부터 재기동까지 서버가 내려가 있다. 2단계 백업 검증이 통과하지 않으면 설치로 넘어가지 않는다.

### 1. JAR 받기와 검증

운영 모드 디렉터리 밖에서 받아 해시를 확인한다. 아래 블록은 별도 `bash -euo pipefail` 프로세스에서 돌므로 어느 명령이든 실패하면 그 자리에서 멈추고 0이 아닌 상태로 끝난다(현재 대화형 셸은 닫히지 않는다).

```sh
cd /home/pilon1945/AziranMinecraftServer
bash -euo pipefail <<'EOF'
JAR=/tmp/bluemap-download/bluemap-5.27-neoforge.jar
mkdir -p /tmp/bluemap-download
curl -fL -o "$JAR" \
  https://cdn.modrinth.com/data/swbUV1cr/versions/1EXOwqA2/bluemap-5.27-neoforge.jar
SIZE=$(stat -c %s "$JAR")
[ "$SIZE" = 7000336 ] || { echo "JAR CHECK FAILED: size $SIZE != 7000336" >&2; exit 1; }
echo "10d4739243996b40d20330a78582ef405715351fb50b543194595da8cea8f9bbf9ee6d7aba8586653f42a7f6113c9f0e04b5bf61e42ac5a47c3152ea0c4b7c82  $JAR" | sha512sum -c -
unzip -tq "$JAR"
echo "JAR CHECK PASSED: $JAR"
EOF
```

마지막 줄에 `JAR CHECK PASSED`가 나오고 셸의 종료 상태(`echo $?`)가 `0`이어야 다음 단계로 간다. `JAR CHECK FAILED`, `sha512sum`의 `FAILED`, `curl`·`unzip` 오류가 나오거나 종료 상태가 0이 아니면 설치하지 않는다. 기대 크기와 SHA-512는 위 표(= lock 항목)와 같다.

### 2. 접속자 공지, 정상 종료, 오프라인 백업

BlueMap JAR 설치 전에 서버를 정상 종료하고 `server-data-26.3-neoforge/` 전체를 보호 백업한다. (2026-09-24 당시 절차다. 2026-09-25부터 배포 전 보호 백업은 `world/`만 대상으로 하며, BlueMap 지도 데이터는 다시 렌더링해 복구한다.) [서버 백업 안내의 오프라인 보호 백업](BACKUPS.md#오프라인-월드-보호-백업)을 순서대로 실행하면서 예시의 `BACKUP_LABEL=pre-change`를 `pre-bluemap`으로 바꾼다. BlueMap 배포 당시에는 이전 컨테이너이므로 해당 안내의 3-A 방식으로 종료했다. 현재 컨테이너의 종료 제한을 확인해 3-A/3-B를 고른다.

`BACKUP VERIFIED: <경로>`와 종료 상태 `0`을 확인하기 전에는 JAR을 설치하지 않는다. 출력된 tar 경로와 `.sha256`을 3단계 설치와 아래 롤백에 사용한다. 정기 월드 백업 tar는 전체 데이터 백업을 대신하지 않는다.

### 3. 설치와 재생성

2단계가 `BACKUP VERIFIED`로 끝나고 서버가 멈춘 상태에서만 실행한다. `BACKUP=`에 2단계가 출력한 경로를 넣는다. 블록은 백업 해시 재검증, 서버 정지 상태, JAR SHA-512, Compose 설정 검사 중 하나라도 실패하면 JAR을 설치하거나 컨테이너를 만들기 전에 멈추고 0이 아닌 상태로 끝난다.

```sh
cd /home/pilon1945/AziranMinecraftServer
BACKUP=/home/pilon1945/aziran-26.3-protected-backups/pre-bluemap-YYYY-mm-dd-HHMMSS.tar   # 2단계 BACKUP VERIFIED 경로
BACKUP="$BACKUP" bash -euo pipefail <<'EOF'
JAR=/tmp/bluemap-download/bluemap-5.27-neoforge.jar
[ -f "$BACKUP" ] && [ -f "$BACKUP.sha256" ] || { echo "INSTALL ABORTED: verified backup not found: $BACKUP" >&2; exit 1; }
sha256sum -c "$BACKUP.sha256"
if [ "$(docker inspect --format '{{.State.Running}}' aziran-minecraft-26-3)" != false ]; then
  echo "INSTALL ABORTED: aziran-minecraft-26-3 is not stopped" >&2; exit 1
fi
echo "10d4739243996b40d20330a78582ef405715351fb50b543194595da8cea8f9bbf9ee6d7aba8586653f42a7f6113c9f0e04b5bf61e42ac5a47c3152ea0c4b7c82  $JAR" | sha512sum -c -
docker compose config --quiet
install -m 644 "$JAR" server-data-26.3-neoforge/mods/bluemap-5.27-neoforge.jar
docker compose up -d --no-deps minecraft
echo "INSTALL STARTED"
EOF
```

`INSTALL STARTED`와 종료 상태 `0`이 아니면 설치·기동이 끝나지 않은 것이다. `INSTALL ABORTED`나 검증 실패로 멈췄다면 JAR은 설치되지 않았다. `install` 뒤 `docker compose up`만 실패했다면 JAR이 이미 `mods/`에 있으므로 롤백 1번으로 치우거나 원인을 고친 뒤 `docker compose up -d --no-deps minecraft`를 다시 실행한다.

`chunky-idle-pregen` 컨트롤러는 서버가 내려간 동안 RCON 재연결을 기다린다. 재시작 뒤 컨트롤러 로그로 작업이 다시 pause/continue 판정을 하는지 확인한다([CHUNK_PREGEN.md](CHUNK_PREGEN.md#무인-프리젠-컨트롤러)).

### 4. 첫 기동: core.conf 생성과 리소스 다운로드 동의

첫 기동 시 BlueMap이 `server-data-26.3-neoforge/config/bluemap/`에 `core.conf`, `webserver.conf`, `webapp.conf`, `maps/` 등 기본 설정을 만든다. 이 상태에서는 렌더링하지 않는다. 블록 텍스처를 얻으려면 Mojang의 Minecraft 클라이언트 리소스를 내려받아야 하고, BlueMap은 그 동의를 `core.conf`의 `accept-download`로 받는다.

1. 로그에서 BlueMap 로드와 설정 생성 메시지를 확인한다.

   ```sh
   docker logs --tail 200 aziran-minecraft-26-3 2>&1 | grep -i bluemap
   ```

2. 운영자가 동의하기로 결정했으면 `server-data-26.3-neoforge/config/bluemap/core.conf`의 `accept-download: false`를 `accept-download: true`로 바꾼다. 이 값은 Mojang 리소스 다운로드에 대한 운영자 동의이므로 대신 켜지 않는다. 2026-09-24 배포에서는 운영자 결정에 따라 켰다(`sed -i 's/^accept-download: false$/accept-download: true/' core.conf`, 원본은 편집 전에 복사해 뒀다). 이 파일은 Git 제외 운영 데이터 경로에 있다.
3. `webserver.conf`의 `enabled: true`와 `port: 8100`을 확인한다. 포트를 바꾸면 Compose `expose`, `nginx/webmap.conf`의 `proxy_pass`, 비활성 Nginx 템플릿도 함께 바꿔야 한다.
4. 설정을 다시 읽는다.

   ```sh
   docker exec aziran-minecraft-26-3 rcon-cli "bluemap reload"
   ```

`bluemap reload` 뒤 BlueMap이 리소스를 받고 월드별 지도 렌더링을 시작한다. 기본 지도 설정 파일 이름과 개수는 `config/bluemap/maps/`에서 확인한다. 정상이면 로그에 `Downloading 'https://piston-data.mojang.com/.../client.jar' to 'bluemap/minecraft-client-26.3.jar'` → `Resources loaded.` → 지도별 `Loading map '...'` → `WebServer bound to all network interfaces on port 8100` → `WebServer started.`가 이어진다. 재시작 없이 적용되므로 서버는 내려가지 않는다.

### 5. 서버 상태 확인

```sh
docker inspect --format '{{.State.Status}} {{.State.Health.Status}} restarts={{.RestartCount}}' aziran-minecraft-26-3
docker exec aziran-minecraft-26-3 rcon-cli list
docker logs --tail 300 aziran-minecraft-26-3 2>&1 | grep -iE 'error|exception|bluemap'
docker inspect --format 'StopTimeout={{.Config.StopTimeout}} restart={{.HostConfig.RestartPolicy.Name}}' aziran-minecraft-26-3
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' aziran-minecraft-26-3 | grep '^STOP_DURATION='
```

`running healthy`, 재시작 0회, RCON 응답, 모드 로드 오류가 없는 것을 확인한다. 기존 20개 모드와 BlueMap이 모두 로드돼야 한다. 재생성된 컨테이너에 새 종료 한도와 재시작 정책이 적용됐는지도 본다: `StopTimeout=660 restart=always`, `STOP_DURATION=600`. 이후의 종료는 [서버 백업 안내의 3-B](BACKUPS.md#오프라인-월드-보호-백업)(Docker 종료)를 쓴다.

### 6. HTTP·렌더링 확인

호스트에 `8100`을 게시하지 않으므로 컨테이너 안에서 확인한다.

```sh
docker exec aziran-minecraft-26-3 curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8100/   # 200
docker exec aziran-minecraft-26-3 curl -fsS http://127.0.0.1:8100/settings.json | head -c 400; echo
docker exec aziran-minecraft-26-3 rcon-cli bluemap                          # 렌더 작업·진행 상태
docker exec aziran-minecraft-26-3 rcon-cli "bluemap maps"
# webmap-nginx와 같은 경로: Compose 네트워크의 다른 컨테이너에서 서비스 이름으로 접속
docker run --rm --pull never --network aziranminecraftserver_aziran-mc-network curlimages/curl:latest \
  -sS -o /dev/null -w '%{http_code}\n' http://minecraft:8100/                   # 200
ss -ltn | grep -E ':8100\b' || echo "8100 NOT PUBLISHED ON HOST"
```

- 루트가 200을 반환하고 `settings.json`에 지도 ID 목록이 있어야 한다.
- `bluemap` 상태 출력에서 렌더 작업이 진행되거나 끝났는지 본다. 첫 렌더링은 프리젠 반경에 비례해 오래 걸리고 CPU를 쓴다. Chunky 프리젠과 겹치면 둘 다 느려진다.
- 타일과 웹 파일은 기본적으로 `server-data-26.3-neoforge/bluemap/`에 저장된다(Git 제외 데이터 경로 안).

### 7. HTTPS 원본(webmap-nginx) 기동과 로컬 확인

호스트 `443`이 비어 있고, 키 권한이 `600`인지 먼저 본다. `80`·`3733`은 다른 Nginx가 쓰므로 건드리지 않는다.

```sh
cd /home/pilon1945/AziranMinecraftServer
ss -ltn | grep -E ':443\b' || echo "443 FREE"
stat -c '%a %n' nginx/key.pem                                               # 600
docker compose config --quiet && echo "COMPOSE CONFIG OK"
docker compose run --rm --no-deps webmap-nginx nginx -t                     # syntax is ok / test is successful
```

`minecraft`를 다시 만들지 않도록 `--no-deps`로 시작하고, `minecraft` 컨테이너 ID·시작 시각이 그대로인지 확인한다.

```sh
docker inspect -f '{{.Id}} {{.State.StartedAt}}' aziran-minecraft-26-3      # 기동 전후 같아야 한다
docker compose up -d --no-deps webmap-nginx
docker inspect -f '{{.Id}} {{.State.StartedAt}}' aziran-minecraft-26-3
docker inspect -f '{{.State.Status}} restarts={{.RestartCount}}' aziran-webmap-nginx   # running restarts=0
docker port aziran-webmap-nginx                                             # 443/tcp만
```

로컬에서 `mcmap.aziran.uk` SNI·Host로 원본을 확인한다. 원본 인증서가 공개 CA(Let's Encrypt)이므로 `-k` 없이 검증이 통과해야 하고, 서버가 내보내는 인증서 지문도 파일과 비교한다.

```sh
curl -sS --resolve mcmap.aziran.uk:443:127.0.0.1 -o /dev/null -w '%{http_code} %{ssl_verify_result} %{content_type}\n' https://mcmap.aziran.uk/   # 200 0 text/html
curl -sS --resolve mcmap.aziran.uk:443:127.0.0.1 https://mcmap.aziran.uk/settings.json | head -c 400; echo                 # 6단계와 같은 지도 ID
echo | openssl s_client -connect 127.0.0.1:443 -servername mcmap.aziran.uk 2>/dev/null | openssl x509 -noout -fingerprint -sha256
openssl x509 -in nginx/cert.pem -noout -fingerprint -sha256                 # 위와 같아야 한다
curl -sS -k --resolve other.example:443:127.0.0.1 https://other.example/    # unrecognized name 오류(거절)가 정상
ss -ltn | grep -E ':(80|443|8100|3733)\b'                                    # 443 추가, 8100 없음, 80·3733 그대로
docker inspect -f '{{.State.Status}} {{.State.Health.Status}}' aziran-minecraft-26-3   # running healthy
docker exec aziran-minecraft-26-3 rcon-cli list
```

### 8. DNS 레코드와 공개 주소 확인

7단계가 통과한 뒤에만 한다.

1. Cloudflare `aziran.uk` 영역의 SSL/TLS 암호화 모드는 바꾸지 않는다(strict 검증이므로 원본 인증서가 공개 CA이고 만료 전이어야 한다. `Flexible`이면 엣지가 서버 `80`의 다른 Nginx로 간다).
2. DNS에 레코드를 하나 추가한다: 유형 `A`, 이름 `mcmap`, 값 = 현재 `mc.aziran.uk`의 `A`와 같은 서버 공인 IP, 프록시 **켬**(주황 구름), TTL 자동. 같은 이름의 레코드가 이미 있으면 덮어쓰지 말고 원인을 확인한다. 다른 레코드(`mc`, `www`, apex)는 바꾸지 않는다. (2026-09-24 생성, 레코드 ID `2afc94d2082cfc5b05953ddce1e6b02c`.)
3. 공개 경로를 확인한다.

```sh
dig +short mcmap.aziran.uk                                                   # Cloudflare 애니캐스트 IP(프록시). 서버 IP가 아니어야 한다
curl -fsS -o /dev/null -w '%{http_code} %{ssl_verify_result}\n' https://mcmap.aziran.uk/   # 200 0
curl -fsS https://mcmap.aziran.uk/settings.json | head -c 400; echo          # 6단계와 같은 지도 ID
curl -sSI https://mcmap.aziran.uk/ | grep -iE '^(server|cf-ray):'            # server: cloudflare, cf-ray 존재
curl -sS -o /dev/null -w '%{http_code}\n' https://aziran.uk/                 # 기존 GitHub Pages 그대로(200 또는 301)
dig +short mc.aziran.uk                                                      # 기존 게임 레코드 그대로
ss -ltnp | grep -E ':8100\b' || echo "8100 NOT PUBLISHED ON HOST"            # 호스트 미게시 확인
```

- 브라우저에서 `https://mcmap.aziran.uk`를 열어 타일과 (접속자가 있으면) 플레이어 마커가 보이는지 확인한다.
- `521`(원본 연결 거부)·`522`(시간 초과)는 엣지가 서버 `443`에 닿지 못한 경우다. 공유기 포트 포워딩·방화벽과 `webmap-nginx` 상태를 본다. `525`(SSL 핸드셰이크 실패)는 SNI·인증서 문제, `526`(유효하지 않은 인증서)은 엣지가 원본 인증서를 신뢰하지 않은 경우다(만료, 공개 CA가 아닌 인증서, 이름 불일치). `openssl x509 -in nginx/cert.pem -noout -issuer -enddate`로 확인하고 "수동 갱신"을 따른다. `502`는 `webmap-nginx`가 `minecraft:8100`에 닿지 못한 경우다(BlueMap 웹서버 꺼짐·포트 불일치, `docker logs aziran-webmap-nginx`). 6·7단계를 다시 확인한다.
- `aziran.uk`, `www.aziran.uk`, `mc.aziran.uk`의 응답·레코드가 배포 전과 같아야 한다.

## 롤백

0. 먼저 접속자에게 공지하고 [서버 백업 안내의 정상 종료 절차](BACKUPS.md#오프라인-월드-보호-백업)에 따라 서버를 멈춘다. 설치 뒤 재생성된 컨테이너라면 종료 제한을 확인한 뒤 3-B(`docker compose stop minecraft`)를 쓴다. `exited exit=0 oom=false`와 `STOP_AT` 이후 세 차원의 `Saving chunks`·러너 `Done`을 확인한다. 실행 중인 서버의 모드 JAR은 옮기지 않는다.
1. JAR을 모드 디렉터리에서 치운다(삭제 대신 보관).

   ```sh
   mkdir -p /home/pilon1945/aziran-26.3-protected-backups/removed-mods
   mv server-data-26.3-neoforge/mods/bluemap-5.27-neoforge.jar \
     /home/pilon1945/aziran-26.3-protected-backups/removed-mods/
   ```

2. 월드 이상 징후가 있으면 서버를 시작하기 전에 4번의 전체 데이터 복원을 판단한다. 그렇지 않으면 `docker compose up -d --no-deps minecraft`로 JAR 없이 다시 시작한다. `expose: 8100`은 Compose 네트워크 안에서만 열리므로 남겨 둬도 된다. 이 브랜치 이전의 `docker-compose.yml`로 돌아갈 때는 먼저 아래 "지도 공개만 끄기"로 `webmap-nginx`를 치운다. 이전 Compose에는 `webmap-nginx` 정의가 없어 그 컨테이너가 고아로 남기 때문이다.
3. BlueMap은 월드 데이터를 바꾸지 않으므로 보통 JAR 제거로 충분하다. `config/bluemap/`과 `bluemap/`(렌더 결과)은 남아도 서버 동작에 영향이 없다. 공간이 필요하면 보관 후 지운다.
4. 기동 실패나 월드 이상이 있으면 2번에서 서버를 다시 시작하지 않는다(이미 시작했다면 0번처럼 정상 종료한다). 2단계의 `pre-bluemap-*.tar`로 [전체 데이터 복원](BACKUPS.md#전체-데이터-복원-이전-전체-백업-전용)을 수행한다. 백업 해시가 맞지 않거나 복원이 끝나지 않으면 서버를 시작하지 않는다. 복원 뒤 BlueMap JAR 제거와 지도 공개 설정을 롤백 상태에 맞춘 다음 `docker compose up -d --no-deps minecraft`로 시작한다.
5. 5단계 상태 확인을 다시 수행한다.

### 지도 공개만 끄기(서버는 유지)

서버 재시작 없이 `mcmap.aziran.uk`만 내린다.

1. Cloudflare DNS에서 `mcmap` 레코드만 지운다(다른 레코드는 그대로). 레코드를 남긴 채 원본만 내리면 엣지가 `521`을 반환한다.
2. 원본을 멈추고 지운다. 호스트 `443`이 비워진다.

   ```sh
   cd /home/pilon1945/AziranMinecraftServer
   docker compose stop webmap-nginx && docker compose rm -f webmap-nginx
   ss -ltn | grep -E ':443\b' || echo "443 FREE"
   ```

3. 8단계의 `aziran.uk`, `mc.aziran.uk` 확인을 다시 해 기존 레코드가 그대로인지 본다.

## 검증 기록

- 저장소 검증: `python3 -m unittest tests.test_bluemap_deployment -v`, `python3 -m unittest discover -s tests`, `CLOUDFLARE_TUNNEL_TOKEN` 없이 `docker compose config --quiet`, `git diff --check`.
- `nginx:1.30-alpine`은 Docker Hub 공식 이미지(`library/nginx`)의 stable 계열이다. 2026-09-24에 `docker buildx imagetools inspect`로 매니페스트 목록 다이제스트 `sha256:98522025…bce2b`를 확인해 Compose에 고정했다. 그 시점 `stable-alpine`과 같은 다이제스트였고, 받은 이미지의 `NGINX_VERSION`은 `1.30.5`다.
- 운영 배포(2026-09-24, 1~6단계). 시각은 UTC, 서버 로그의 괄호 시각은 서버 시간대(UTC+9)다.
  - 정상 종료(3-A): `rcon-cli stop` 종료 상태 0(`Stopping the server`), 컨테이너 `exited exit=0 oom=false`. 서버 로그 `12:23:34`에 `Stopping server` → `Saving players` → `Saving worlds` → `Saving chunks for level 'ServerLevel[world]'/minecraft:overworld`·`minecraft:the_nether`·`minecraft:the_end` → `Thread RCON Listener stopped`, 러너 `Done`, 저장 오류 없음. `All dimensions are saved`는 26.3에서 찍히지 않으므로 판정에 쓰지 않았다.
  - 백업: `/home/pilon1945/aziran-26.3-protected-backups/pre-bluemap-2026-09-24-032421.tar`, 약 11.6GB, 4205항목, `sha256sum -c` 통과, 디렉터리 `700`·파일 `600`.
  - 설치·재생성: 검증한 JAR(SHA-512 일치)을 `mods/`에 `644`로 설치하고 `minecraft`를 다시 만들었다. 재생성 뒤 `running healthy restarts=0`, `StopTimeout=660 restart=always`, `STOP_DURATION=600`, 호스트 게시는 `25565`만(`8100/tcp`는 `expose`만, 호스트 바인딩 없음). BlueMap 5.27과 기존 20개 모드가 함께 로드됐다.
  - 리소스 동의: 첫 기동에서 `BlueMap is missing important resources!`, `You must accept the required file download` 경고만 나오고 웹서버는 뜨지 않았다. `accept-download: true`로 바꾸고 `03:30:07Z`에 `rcon-cli "bluemap reload"`(응답 `Reloading BlueMap...`, 종료 상태 0)를 실행했다. Mojang `client.jar`를 `bluemap/minecraft-client-26.3.jar`(41483720바이트)로 받았고 `Resources loaded.`, 지도 3개(`world`, `world_the_nether`, `world_the_end`) 로드, `WebServer started.`(포트 8100)를 확인했다. 재시작은 없었다.
  - HTTP: 컨테이너 안 `http://127.0.0.1:8100/` 200, `settings.json`의 `maps`가 `["world","world_the_nether","world_the_end"]`. Compose 네트워크의 별도 `curlimages/curl` 컨테이너에서 `http://minecraft:8100/` 200, `maps/world/settings.json` 200. 호스트 `ss -ltn`에 `8100` 리스너 없음, 기본 브리지 게이트웨이 `172.17.0.1:8100`은 연결 거부.
  - 렌더링: `rcon-cli bluemap`에서 렌더 스레드 3개 실행, `world` 갱신 진행 중(시작 직후 0.234%, 예상 남은 시간 약 4시간), `world_the_nether`·`world_the_end`는 대기 작업 1개씩. 시작 직후 타일 데이터 `server-data-26.3-neoforge/bluemap/` 약 104MB, 루트 파일시스템 여유 1.2TB.
  - 게임·RCON: 호스트 `25565` 리스닝, `mc-health` 응답(`version=26.3 online=0 max=20`), `rcon-cli list` 응답.
  - 로그 오류 구분: `reload` 이후 BlueMap 로그와 `bluemap/logs/`에 오류·경고가 없다. 기동 로그의 오류는 BlueMap과 무관하다. `Appender DebugFile`의 `NoClassDefFoundError: io.netty.channel.kqueue.Native`(`Only supported on OSX/BSD`)는 스택이 바닐라 `ServerConnectionListener.startTcpServerListener`의 netty kqueue 탐지에서 나오고, Occultism의 `CuriosIntegrationImpl` `ClassNotFoundException`(Curios 미설치로 더미 구현 사용)과 `apothic_enchanting:enchantment_info` 데이터 맵 경고는 BlueMap 설치 전 기동 로그(`logs/2026-09-24-2.log.gz`)에도 있다. kqueue 오류는 이 로그 파일 밖(stdout)에만 찍혀 설치 전 발생 여부를 파일로는 확인하지 못했다.
  - 터널 계획 폐기: Cloudflare 터널 생성 API가 `10000 Authentication error`로 거부됐다(읽기 전용 DNS·터널 조회는 동작, 브라우저 대시보드는 로그인·봇 확인 화면으로 막힘). 터널·토큰은 만들어지지 않았고, 운영자 승인으로 직접 HTTPS 원본 방식으로 바꿨다. `cloudflared` 서비스와 `CLOUDFLARE_TUNNEL_TOKEN` 요구를 Compose에서 지웠다.
- HTTPS 원본(2026-09-24, 7단계).
  - 사전: 호스트 `443` 미사용, `80`·`3733`은 다른 Nginx(건드리지 않음). `nginx/cert.pem`은 Cloudflare Origin CA 발급 `*.aziran.uk`, 2039-06-30 만료이며 키와 공개키가 일치했다. 키 권한 `664`를 `600`으로 바꿨다(내용은 출력하지 않음).
  - `docker compose run --rm --no-deps webmap-nginx nginx -t`: `syntax is ok`, `test is successful`.
  - `docker compose up -d --no-deps webmap-nginx`: `running restarts=0`, `restart=unless-stopped`, 게시 포트는 `443/tcp -> 0.0.0.0:443`, `[::]:443`뿐. `minecraft` 컨테이너 ID·시작 시각은 기동 전후 같았다(재생성 없음).
  - `--resolve mcmap.aziran.uk:443:127.0.0.1`로 `https://mcmap.aziran.uk/` → `200 text/html`, `<title>BlueMap</title>`; `settings.json`의 `maps`가 `["world","world_the_nether","world_the_end"]`. `[::1]`로도 200.
  - 서버가 내보낸 인증서 SHA-256 지문이 `nginx/cert.pem`과 같았다(`C8:79:49:1D:…:91:4F`, CN `CloudFlare Origin Certificate`).
  - SNI `other.example`은 `tlsv1 unrecognized name`(alert 112)으로 거절.
  - `ss -ltn`: `443` 추가, `80`·`3733`·`25565` 그대로, `8100` 없음. `minecraft`는 `running healthy restarts=0`, `rcon-cli list` 응답.
- 공개 DNS·인증서 교체(2026-09-24, 8단계). Cloudflare 조작은 Cloudflare API(MCP)로 했고, SSL 모드·터널은 바꾸지 않았다.
  - 첫 시도: 프록시 `A mcmap → 114.200.114.174`를 만들자 엣지 TLS는 정상이지만 `https://mcmap.aziran.uk/`가 `526`(cf-ray `a3fee5576bce0439-HKG`)이었다. 원본은 `-k`로 200, 지문이 `nginx/cert.pem`과 같았고, 계정의 Origin CA 인증서 목록(`/certificates?zone_id=…`)은 비어 있었다. 설계 범위 안에서 고칠 수 없어 그 레코드만 지웠다.
  - 인증서 교체: 기존 `cert.pem`·`key.pem`을 보호 백업 경로에 해시 일치로 보관한 뒤 certbot 5.8.0 수동 DNS-01로 `mcmap.aziran.uk` 인증서를 받았다. 임시 TXT `_acme-challenge.mcmap.aziran.uk`는 검증 뒤 지웠다. 공개키 해시가 키와 일치했고 `openssl verify`로 체인이 통과했다. `cp` 덮어쓰기(inode 유지)로 설치하고 `600`으로 둔 뒤 `webmap-nginx`에서 `nginx -t` 통과·`nginx -s reload`만 했다(`minecraft` 재시작 없음). 로컬에서 `-k` 없이 200.
  - DNS: 프록시 `A mcmap.aziran.uk → 114.200.114.174`, TTL 자동, ID `2afc94d2082cfc5b05953ddce1e6b02c`. 다시 읽은 영역에는 이 레코드와 기존 `mc` `A`(`04dfcb70…30ca`, 비프록시), apex·`www` `CNAME`만 있다. `dig @1.1.1.1 mcmap.aziran.uk`는 Cloudflare IP(`104.21.73.98`, `172.67.160.233`).
  - 공개 확인(`-k` 없이): `/` `200 text/html` `ssl_verify_result=0`, `server: cloudflare`, `<title>BlueMap</title>`; `assets/index-DJzYl7wx.js` 200, `assets/index-C6zAnFcX.css` 200, `settings.json` 200(`maps` 3개), `maps/world/settings.json` 200. `https://aziran.uk/` 200, `mc.aziran.uk`는 `114.200.114.174` 그대로, 서버 공인 IP의 `25565` 연결 성공·`8100` 연결 불가, `minecraft`는 `healthy`.
- 하지 않은 것: Cloudflare SSL/TLS 모드 직접 조회(OAuth 권한 부족, `9109`), 브라우저에서 타일·플레이어 마커 육안 확인, 첫 전체 렌더링 완료 확인. 인증서 자동 갱신은 없다(2026-12-23 만료 전 수동 갱신 필요).
- 추적된 `mods-26.3-client.lock.json`의 `excluded` 목록은 다음 클라이언트 팩 재빌드 때 BlueMap이 반영된다. 팩 구성(모드 18개)은 바뀌지 않는다.

#!/usr/bin/env python3
"""Aziran 26.3 NeoForge 서버용 클라이언트 모드팩 빌더.

모드는 두 곳에서 온다.

- 서버와 공유하는 모드: 서버 lock(mods-26.3.lock.json)에서 고르고
  JAR은 server-data-26.3-neoforge/mods/에서 읽는다.
- 클라이언트 전용 추가 모드: 클라이언트 입력 lock(mods-26.3-client-extra.lock.json)에서
  고르고 JAR은 client-mods-cache/에서 읽는다. 서버에는 설치하지 않는다.

두 경로 모두 lock의 크기·SHA-512와 실제 JAR을 대조한 뒤에만 패키징한다.
결과물은 Modrinth .mrpack, 수동 설치용 ZIP, MultiMC 인스턴스 ZIP으로 dist/에 만든다.

입력 lock이 bundle_jar=false로 표시한 모드는 라이선스가 JAR 재배포를 금지하므로 JAR을 담지
않는다. 이런 모드는 .mrpack의 Modrinth CDN 다운로드 항목으로만 설치되고, JAR을 담는 수동 ZIP과
MultiMC 인스턴스 ZIP에서는 빠진다. 대신 README가 공식 배포처에서 직접 받는 절차를 안내한다.
"""

import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SERVER_LOCK = REPO / "mods-26.3.lock.json"
SERVER_MODS = REPO / "server-data-26.3-neoforge" / "mods"
CLIENT_EXTRA_LOCK = REPO / "mods-26.3-client-extra.lock.json"
CLIENT_CACHE = REPO / "client-mods-cache"
CLIENT_LOCK = REPO / "mods-26.3-client.lock.json"
DIST = REPO / "dist"

PACK_NAME = "Aziran 26.3 Client"
PACK_VERSION = "1.1.3"
PACK_SUMMARY = "Aziran Minecraft 26.3 NeoForge 서버 접속용 클라이언트 모드 구성"

# 1.1.3 구성의 근거. 입력 lock의 removed 항목과 같은 내용을 산출물에도 남긴다.
RELEASE_NOTE = (
    "1.1.3은 1.1.2에서 Xaero's Minimap을 빼고 같은 자리에 JourneyMap 26.3-6.0.9+neoforge를 "
    "넣은 구성이다. Sodium은 1.1.1부터와 같이 계속 제외한다. "
    "16개를 모두 켠 1.1.2는 Windows에서 네이티브 종료 코드 0xc0000005로 크래시했고, 같은 "
    "인스턴스에서 xaerominimap-neoforge-26.3-26.5.3.jar 하나만 비활성화하면 실행됐다(A/B 확인). "
    "따라서 그 조합에서 크래시의 방아쇠는 Xaero's Minimap으로 확인됐지만, 네이티브 실패 "
    "메커니즘은 규명하지 않았고 다른 환경에서도 재현된다는 뜻은 아니다. "
    "JourneyMap JAR은 라이선스상 재배포·번들이 금지돼 있어 .mrpack에만 Modrinth CDN 다운로드 "
    "항목으로 넣고, 수동 ZIP과 MultiMC 인스턴스 ZIP에는 나머지 15개 JAR만 담는다. "
    "1.1.3 구성으로 Windows 실행과 서버 접속은 아직 확인하지 않았다. 실행과 접속이 함께 확인된 "
    "구성은 Sodium을 꺼 둔 1.1.0 인스턴스뿐이다."
)

# 서버와 공유하는 모드 중 클라이언트에도 설치할 모드. 서버 lock의 title을 키로 쓴다.
CLIENT_TITLES = [
    "Balm",
    "Clumps",
    "Cooking for Blockheads",
    "Curios API",
    "Farmer's Delight 26 Neo Ver",
    "Geckolib",
    "Jade \U0001f50d",
    "Just Enough Items (JEI)",
    "Lithium",
    "Modonomicon",
    "Occultism",
    "Packet Fixer",
    "Tom's Simple Storage Mod",
]

# 제외한 모드와 근거. 서버에만 두고 클라이언트에서는 뺀다.
EXCLUSIONS = {
    "Almanac": "Modrinth client_side=unsupported. Let Me Despawn 전용 서버 라이브러리.",
    "Chunky": "청크 프리젠 도구. 서버 콘솔에서만 사용하며 레지스트리·네트워크 페이로드가 없다.",
    "Cristel Lib": "Towns and Towers용 데이터팩 설정 라이브러리. 콘텐츠 레지스트리가 없다.",
    "Let Me Despawn": "Modrinth client_side=unsupported. 몹 디스폰 정리는 서버 전용이다.",
    "Structures – Structures & Exploration": "클래스 0개의 데이터팩 JAR. 구조물은 서버가 생성해 전송한다.",
    "Towns and Towers": "클래스 0개의 데이터팩 JAR. 구조물은 서버가 생성해 전송한다.",
    "spark": "프로파일링 도구. 서버 콘솔에서만 사용한다.",
}

# 배포 라이선스와 근거 URL. 수동 ZIP에 JAR을 넣을 근거로 쓴다.
LICENSES = {
    "Balm": {
        "id": "LicenseRef-All-Rights-Reserved",
        "name": "All Rights Reserved (모드팩 사용 허가 있음)",
        "url": "https://mods.twelveiterations.com/permissions",
        "note": "제작자 허가 페이지: \"Use in modpacks is allowed on all supported platforms.\" "
                "같은 페이지가 공개 재업로드·재호스팅은 금지한다.",
    },
    "Cooking for Blockheads": {
        "id": "LicenseRef-All-Rights-Reserved",
        "name": "All Rights Reserved (모드팩 사용 허가 있음)",
        "url": "https://mods.twelveiterations.com/permissions",
        "note": "Balm과 같은 제작자(BlayTheNinth)의 같은 허가 페이지를 따른다.",
    },
    "Clumps": {
        "id": "MIT",
        "name": "MIT License",
        "url": None,
        "note": "JAR의 neoforge.mods.toml이 license=\"MIT\"를 선언하며 Modrinth 프로젝트 메타데이터와 같다.",
    },
    "Curios API": {"id": "LGPL-3.0-or-later", "name": "GNU LGPL v3.0 or later", "url": None, "note": ""},
    "Farmer's Delight 26 Neo Ver": {
        "id": "MIT",
        "name": "MIT License",
        "url": "https://github.com/vectorwing/FarmersDelight",
        "note": "vectorwing의 원본 Farmer's Delight(MIT)를 기반으로 한 비공식 NeoForge 26.3 이식판. "
                "JAR 메타데이터가 license=\"MIT License\"를 선언한다.",
    },
    "Geckolib": {"id": "MIT", "name": "MIT License", "url": None, "note": ""},
    "Jade \U0001f50d": {
        "id": "CC-BY-NC-SA-4.0",
        "name": "Creative Commons BY-NC-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "note": "비상업적 사용에 한해 저작자 표시와 동일조건변경허락 조건으로 재배포할 수 있다.",
    },
    "Just Enough Items (JEI)": {"id": "MIT", "name": "MIT License", "url": None, "note": ""},
    "Lithium": {
        "id": "LGPL-3.0-only",
        "name": "GNU LGPL v3.0 only",
        "url": None,
        "note": "JAR의 neoforge.mods.toml이 license=\"LGPL-3.0-only\"를 선언하며 Modrinth 프로젝트 메타데이터와 같다.",
    },
    "Modonomicon": {
        "id": "MIT AND CC-BY-4.0",
        "name": "MIT License, Creative Commons Attribution 4.0",
        "url": "https://github.com/klikli-dev/modonomicon#licensing",
        "note": "코드는 MIT, 에셋은 CC-BY-4.0이다.",
    },
    "Occultism": {
        "id": "MIT",
        "name": "MIT License",
        "url": "https://github.com/klikli-dev/occultism#licensing",
        "note": "",
    },
    "Packet Fixer": {"id": "MIT", "name": "MIT License", "url": None, "note": ""},
    "Tom's Simple Storage Mod": {"id": "MIT", "name": "MIT License", "url": None, "note": ""},
}

# mrpack의 downloads에 쓸 수 있는 호스트. Modrinth가 허용한 CDN만 사용한다.
ALLOWED_DOWNLOAD_PREFIX = "https://cdn.modrinth.com/"

# MultiMC 인스턴스 이름과 컴포넌트 UID.
# NeoForge UID는 MultiMC 공식 메타(MultiMC/meta-multimc)의 net.neoforged를 쓴다.
# Prism Launcher가 쓰는 net.neoforged.neoforge는 MultiMC 메타에 없어 가져오기가 실패한다.
MULTIMC_INSTANCE_NAME = f"{PACK_NAME} {PACK_VERSION}"
MULTIMC_MINECRAFT_UID = "net.minecraft"
MULTIMC_NEOFORGE_UID = "net.neoforged"


def file_hashes(path):
    data = path.read_bytes()
    return {
        "size": len(data),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_client_mods():
    """서버 lock에서 클라이언트 모드를 고르고, 로컬 JAR 해시를 lock과 대조한다."""
    server_lock = json.loads(SERVER_LOCK.read_text(encoding="utf-8"))
    by_title = {mod["title"]: mod for mod in server_lock["mods"]}

    missing = [title for title in CLIENT_TITLES if title not in by_title]
    if missing:
        raise SystemExit(f"서버 lock에 없는 모드: {missing}")

    unaccounted = set(by_title) - set(CLIENT_TITLES) - set(EXCLUSIONS)
    if unaccounted:
        raise SystemExit(f"포함·제외 어느 쪽에도 분류되지 않은 모드: {sorted(unaccounted)}")

    mods = []
    for title in CLIENT_TITLES:
        mod = by_title[title]
        jar = SERVER_MODS / mod["filename"]
        if not jar.is_file():
            raise SystemExit(f"서버 mods 디렉터리에 JAR이 없다: {jar}")
        actual = file_hashes(jar)
        if actual["sha512"] != mod["sha512"] or actual["size"] != mod["size"]:
            raise SystemExit(f"lock과 JAR이 일치하지 않는다: {mod['filename']}")

        url = mod.get("url", "")
        from_cdn = mod["source"] == "modrinth" and url.startswith(ALLOWED_DOWNLOAD_PREFIX)
        mods.append({
            "title": title,
            "filename": mod["filename"],
            # 서버에도 설치된 모드다. JAR을 서버 mods 디렉터리에서 읽는다.
            "origin": "server-lock",
            "source": mod["source"],
            "version_number": mod["version_number"],
            "project_slug": mod.get("project_slug"),
            "url": url if from_cdn else None,
            "size": actual["size"],
            "sha1": actual["sha1"],
            "sha512": actual["sha512"],
            "sha256": actual["sha256"],
            "license": LICENSES[title],
            # 서버와 같은 파일을 담는 모드다. JAR 재배포를 막는 라이선스는 없다.
            "bundle_jar": True,
            "declared_mod_ids": mod["declared_mod_ids"],
            "bundled_jars": [
                {"filename": nested["filename"], "declared_mod_ids": nested["declared_mod_ids"]}
                for nested in mod.get("bundled_jars", [])
            ],
            "required_dependencies": mod["required_dependencies"],
            # Modrinth CDN에서 받을 수 있으면 mrpack의 files 항목, 아니면 client-overrides에 넣는다.
            "mrpack_delivery": "download" if from_cdn else "client-overrides",
        })
    return server_lock, mods


def load_client_extras():
    """클라이언트 입력 lock에서 추가 모드를 읽고, 캐시 JAR 해시를 lock과 대조한다."""
    extra_lock = json.loads(CLIENT_EXTRA_LOCK.read_text(encoding="utf-8"))

    mods = []
    for mod in extra_lock["mods"]:
        jar = CLIENT_CACHE / mod["filename"]
        if not jar.is_file():
            raise SystemExit(
                f"클라이언트 캐시에 JAR이 없다: {jar}\n"
                f"  {mod['url']} 를 받아 이 경로에 두고 다시 실행한다."
            )
        actual = file_hashes(jar)
        if actual["sha512"] != mod["sha512"] or actual["size"] != mod["size"]:
            raise SystemExit(f"클라이언트 lock과 JAR이 일치하지 않는다: {mod['filename']}")

        url = mod["url"]
        from_cdn = mod["source"] == "modrinth" and url.startswith(ALLOWED_DOWNLOAD_PREFIX)
        # JAR 재배포를 금지하는 라이선스는 lock에서 bundle_jar=false로 표시한다.
        # 이런 모드는 런처가 설치 중에 공식 CDN에서 직접 받아야 하므로 CDN URL이 반드시 있어야 한다.
        bundle_jar = mod.get("bundle_jar", True)
        if not bundle_jar and not from_cdn:
            raise SystemExit(
                f"bundle_jar=false인 모드에 Modrinth CDN URL이 없어 설치 경로가 없다: {mod['filename']}"
            )
        mods.append({
            "title": mod["title"],
            "filename": mod["filename"],
            # 서버에는 없는 클라이언트 전용 모드다. JAR을 캐시 디렉터리에서 읽는다.
            "origin": "client-extra-lock",
            "source": mod["source"],
            "version_number": mod["version_number"],
            "project_slug": mod.get("project_slug"),
            "url": url if from_cdn else None,
            "size": actual["size"],
            "sha1": actual["sha1"],
            "sha512": actual["sha512"],
            "sha256": actual["sha256"],
            "license": mod["license"],
            "bundle_jar": bundle_jar,
            "bundle_jar_reason": mod.get("bundle_jar_reason"),
            "declared_mod_ids": mod["declared_mod_ids"],
            "bundled_jars": [
                {"filename": nested["filename"], "declared_mod_ids": nested["declared_mod_ids"]}
                for nested in mod.get("bundled_jars", [])
            ],
            "required_dependencies": mod["required_dependencies"],
            "mrpack_delivery": "download" if from_cdn else "client-overrides",
        })
    return extra_lock, mods


def jar_path(mod):
    """origin에 따라 JAR을 읽을 위치를 고른다."""
    if mod["origin"] == "server-lock":
        return SERVER_MODS / mod["filename"]
    return CLIENT_CACHE / mod["filename"]


def bundled_mods(mods):
    """JAR을 아카이브에 담아도 되는 모드만 고른다. 나머지는 런처가 공식 CDN에서 받는다."""
    return [mod for mod in mods if mod["bundle_jar"]]


def check_dependency_closure(mods):
    """선택한 모드만으로 required 의존성이 모두 충족되는지 확인한다."""
    provided = {"minecraft", "neoforge"}
    for mod in mods:
        provided.update(mod["declared_mod_ids"])
        for nested in mod["bundled_jars"]:
            provided.update(nested["declared_mod_ids"])

    unmet = []
    for mod in mods:
        for dep in mod["required_dependencies"]:
            if dep["mod_id"] not in provided:
                unmet.append(f"{mod['title']} -> {dep['mod_id']} {dep['version_range']}")
    if unmet:
        raise SystemExit("충족되지 않은 필수 의존성: " + ", ".join(unmet))
    return sorted(provided)


def render_readme(server_lock, mods):
    external = [mod for mod in mods if not mod["bundle_jar"]]
    lines = [
        f"# {PACK_NAME} {PACK_VERSION}",
        "",
        f"Aziran Minecraft `{server_lock['minecraft_version']}` NeoForge 서버에 접속하기 위한 클라이언트 모드 구성이다.",
        "서버와 공유하는 모드는 서버와 같은 파일을 담았고, 여기에 서버가 쓰지 않는 클라이언트 전용",
        "최적화·편의 모드를 더했다. 서버 전용 모드와 서버 설정·월드·로그는 포함하지 않는다.",
        "",
    ]

    if external:
        names = ", ".join(mod["title"] for mod in external)
        lines += [
            f"## 먼저 읽을 것: {names}은 ZIP 두 개에 들어 있지 않다",
            "",
            f"**{names}의 JAR은 `{manual_zip_name()}`과 `{multimc_zip_name()}`에 담겨 있지 않다.**",
            "제작자 라이선스가 JAR을 다시 배포하거나 모드팩 안에 담는 것을 금지하고, 모드팩 사용은",
            "설치·실행 과정에서 CurseForge 또는 Modrinth에서 직접 내려받을 때만 허용하기 때문이다.",
            "빠뜨린 것이 아니라 라이선스를 지키려고 뺀 것이다.",
            "",
            f"- **권장: `{mrpack_name()}`을 쓴다.** 런처가 설치 중에 Modrinth에서 이 모드를 직접",
            f"  내려받으므로 라이선스 조건을 만족하면서 모드 {len(mods)}개가 모두 갖춰진다.",
            "  MultiMC도 `Add Instance` → `Import from zip`에서 `.mrpack`을 가져올 수 있다.",
            "  MultiMC 위키의 Import Instance 문서가 가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있다",
            "  (https://github.com/MultiMC/Launcher/wiki/Import-Instance).",
            f"- ZIP 두 개를 쓰면 모드 {len(mods) - len(external)}개만 설치된다. 나머지는 아래 절차로 직접 받아 넣는다.",
            "",
            "### 직접 받아 넣는 절차 (ZIP으로 설치할 때만)",
            "",
        ]
        for mod in external:
            lines += [
                f"**{mod['title']} {mod['version_number']}**",
                "",
                f"1. 공식 Modrinth 프로젝트에서 받는다: https://modrinth.com/mod/{mod['project_slug']}",
                f"   이 팩이 고정한 파일의 직접 링크는 {mod['url']} 이다.",
                "   CurseForge의 공식 프로젝트 페이지에서 같은 버전을 받아도 된다.",
                "2. 받은 파일이 팩이 고정한 것과 같은지 대조한다.",
                f"   - 파일 이름: `{mod['filename']}`",
                f"   - 크기: {mod['size']} 바이트",
                f"   - SHA-1: `{mod['sha1']}`",
                f"   - SHA-512: `{mod['sha512']}`",
                "3. 게임 디렉터리(MultiMC라면 인스턴스의 `.minecraft`)의 `mods/` 폴더에 그 JAR을 넣는다.",
                "4. 다른 곳에서 재배포된 사본은 쓰지 않는다. 라이선스가 금지한다.",
                "",
                f"   라이선스 근거: {mod['license']['url']}",
                "",
            ]

    lines += [
        "## 1.1.3 변경: Xaero's Minimap을 JourneyMap으로 교체",
        "",
        "1.1.2는 미니맵으로 Xaero's Minimap을 담았지만, 16개를 모두 켠 그 구성이 Windows에서",
        "네이티브 종료 코드 `0xc0000005`(액세스 위반)로 크래시했다. 같은 인스턴스에서",
        "`xaerominimap-neoforge-26.3-26.5.3.jar` **하나만** 비활성화하면 실행됐고, 1.1.1과 1.1.2의",
        "최상위 모드 JAR 차이도 이 파일 하나뿐이었다(나머지 15개는 SHA-512까지 동일). 그래서 그",
        "모드·드라이버·런타임 조합에서 크래시의 방아쇠는 Xaero's Minimap으로 확인됐다.",
        "",
        "**왜** 네이티브 액세스 위반까지 갔는지는 규명하지 않았다. 모드 자체의 결함인지, 그 PC의",
        "그래픽 드라이버·GPU와의 조합인지, NeoForge 26.3 베타나 다른 모드와의 상호작용인지 구분하지",
        "않았다. 이 모드가 다른 환경에서도 같은 문제를 일으킨다는 뜻은 아니다.",
        "",
        "미니맵 기능은 계속 필요하므로 1.1.3은 같은 자리에 JourneyMap을 넣었다. 고정한 버전은 아래",
        f"\"포함 모드 {len(mods)}개\" 표에 있다. 모드 수는 {len(mods)}개로 1.1.2와 같고,",
        "나머지 15개 JAR은 1.1.1·1.1.2와 바이트 단위로 동일하다.",
        "",
        "### Sodium은 계속 제외",
        "",
        "1.1.0 인스턴스에서 Sodium JAR만 비활성화하면 Windows MultiMC가 정상 실행되고 서버 접속까지",
        "된다는 사용자 확인을 받았다. 그래서 1.1.1·1.1.2에 이어 1.1.3에서도 Sodium을 넣지 않는다.",
        "크래시 로그에 남아 있던 네이티브 종료 코드 `0xc0000409`의 정확한 원인은 확정하지 못했다.",
        "확인된 사실은 \"Sodium이 없으면 그 PC에서 실행·접속된다\"까지다.",
        "Sodium을 뺐으므로 1.1.0에서 기대하던 렌더링 성능 향상은 없다. 프레임이 낮아질 수 있다.",
        "",
        "### JourneyMap은 서버에 설치하지 않는다",
        "",
        "Modrinth는 이 모드를 `client_side=optional`, `server_side=optional`로 표시한다. 지도 표시와",
        "웨이포인트는 클라이언트만으로 동작하므로 이번 작업에서 서버 구성·서버 모드 디렉터리는 바꾸지",
        "않았다. 서버에 넣지 않아도 접속과 지도 사용에는 문제가 없다.",
        "",
        "`.mrpack` 항목의 `env.server=unsupported`는 \"이 팩이 서버에 아무것도 설치하지 않는다\"는 뜻이며,",
        "모드 자체의 서버 지원 여부와는 다른 값이다.",
        "",
        "JourneyMap JAR은 `commonnetworking`을 필수 의존성으로 선언하지만, 내장 JAR",
        "`common-networking-neoforge-26.3-1.1.1.jar`가 그 모드를 제공하므로 따로 설치하지 않는다.",
        "",
        "## 필요 환경",
        "",
        f"- Minecraft `{server_lock['minecraft_version']}`",
        f"- NeoForge `{server_lock['loader_version']}` (베타 채널)",
        f"- Java {server_lock['java_version']}",
        "",
        "NeoForge 26.3 계열은 현재 베타만 배포된다. 서버와 같은 "
        f"`{server_lock['loader_version']}`를 설치해야 한다.",
        "",
        "## 설치 방법",
        "",
        "### 1. .mrpack (런처 가져오기) — 권장",
        "",
        f"`{mrpack_name()}`은 Modrinth 모드팩 형식이다. Modrinth App, Prism Launcher, ATLauncher,",
        "MultiMC 등 모드팩 가져오기를 지원하는 런처에서 파일을 열면 Minecraft와 NeoForge, 모드를",
        f"함께 설치한다. 모드 {len(mods)}개가 모두 갖춰지는 방식은 이것뿐이다.",
        "모드 대부분은 런처가 Modrinth CDN에서 직접 내려받고, Farmer's Delight 이식판만 팩 안에 들어 있다.",
        "이전 버전(1.1.0·1.1.1·1.1.2) 인스턴스에 덮어쓰지 말고 **새 인스턴스로 만든다.** 이 팩은 기존",
        "`mods/`를 정리하지 않으므로 덮어쓰면 이전 구성의 Sodium·Xaero JAR이 그대로 남는다.",
        "",
        "### 2. 수동 ZIP",
        "",
        f"`{manual_zip_name()}`은 런처를 쓰지 않는 설치용이다.",
        f"모드 JAR {len(mods) - len(external)}개가 들어 있고, 위에서 안내한 모드는 직접 받아 넣어야 한다.",
        "",
        "1. Minecraft 런처에 NeoForge "
        f"`{server_lock['loader_version']}` 설치 프로파일을 먼저 만든다.",
        "2. 해당 프로파일의 게임 디렉터리를 연다(기본값은 `.minecraft`).",
        "3. 이전 버전을 설치했던 디렉터리라면 `mods/sodium-neoforge-0.9.2+mc26.3.jar`와",
        "   `mods/xaerominimap-neoforge-26.3-26.5.3.jar`를 먼저 지운다.",
        "4. ZIP 안의 `mods/` 폴더 내용을 게임 디렉터리의 `mods/` 폴더에 넣는다.",
        "5. 위 \"직접 받아 넣는 절차\"대로 나머지 모드를 같은 `mods/` 폴더에 넣는다.",
        "6. `manifest.json`의 SHA-1/SHA-512와 실제 파일을 대조해 무결성을 확인한다.",
        "   `manifest.json`에는 ZIP에 담은 파일만 적혀 있다.",
        "",
        "### 3. MultiMC 인스턴스 ZIP",
        "",
        f"`{multimc_zip_name()}`은 MultiMC 인스턴스 내보내기 형식이다.",
        f"모드 JAR {len(mods) - len(external)}개가 팩 안에 들어 있다.",
        "**MultiMC를 쓴다면 이 ZIP 대신 `.mrpack`을 가져오는 쪽을 권한다.** `.mrpack`은 나머지 모드까지",
        "런처가 받아 주므로 수작업이 없다.",
        "",
        "이전 버전 인스턴스를 그대로 쓰지 말고 **새 인스턴스로 가져온다.** 가져오기는 기존 인스턴스의",
        "`mods/`를 지우지 않으므로, 이전 인스턴스를 재사용하면 Sodium·Xaero JAR이 남아 이번 구성과 달라진다.",
        "Sodium을 끄고 쓰던 1.1.0 인스턴스는 지우지 말고 남겨 둔다. 실행과 서버 접속이 함께 확인된 구성은",
        "지금으로서는 그 인스턴스뿐이다. 가져온 인스턴스 이름은",
        f"`{MULTIMC_INSTANCE_NAME}`이라 런처 목록에서 이전 인스턴스와 구분된다.",
        "",
        "1. MultiMC에서 `Add Instance`(인스턴스 추가)를 누른다.",
        "2. 왼쪽 목록에서 `Import from zip`(ZIP에서 가져오기)을 고른다.",
        f"3. 내려받은 `{multimc_zip_name()}`을 선택하고 `OK`를 누른다.",
        "4. 만들어진 인스턴스의 `Edit Instance` → `Settings` → `Java`에서 "
        f"Java {server_lock['java_version']} 실행 파일을 고른다. "
        "팩에는 Java 경로를 넣지 않았으므로 런처에서 직접 지정해야 한다.",
        "5. `Edit Instance` → `Folder`로 인스턴스 폴더를 열고, `.minecraft/mods/`에 위 \"직접 받아 넣는",
        "   절차\"대로 나머지 모드를 넣는다.",
        "6. 인스턴스를 실행한다.",
        "",
        f"Minecraft `{server_lock['minecraft_version']}`와 NeoForge "
        f"`{server_lock['loader_version']}`는 팩에 담지 않고 인스턴스 정의(`mmc-pack.json`)로만 지정했다.",
        "MultiMC가 가져오기 후 첫 실행 때 공식 메타데이터를 보고 게임 파일과 로더를 내려받으므로,",
        "인터넷 연결과 로그인한 Minecraft 계정이 필요하다. 계정 정보와 서버 주소는 팩에 넣지 않았다.",
        "",
        "세 방식이 설치하는 모드 구성은 같다. 다만 ZIP 두 개는 위에서 안내한 모드를 직접 넣어야",
        "`.mrpack`과 같은 구성이 된다.",
        "",
        f"## 포함 모드 {len(mods)}개",
        "",
        "`서버 공통`은 서버에도 같은 파일이 설치돼 있어 버전을 맞춰야 하는 모드다.",
        "`클라이언트 전용`은 서버에 설치하지 않는 모드이며, 빼도 서버 접속에는 영향이 없다.",
        "`팩 포함`은 JAR을 아카이브에 담았는지, 설치 중 Modrinth에서 받는지를 나타낸다.",
        "",
        "| 모드 | 버전 | 구분 | 팩 포함 | 라이선스 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mod in mods:
        kind = "서버 공통" if mod["origin"] == "server-lock" else "클라이언트 전용"
        delivery = "JAR 포함" if mod["bundle_jar"] else "설치 중 Modrinth 다운로드"
        lines.append(
            f"| {mod['title']} | {mod['version_number']} | {kind} | {delivery} | {mod['license']['id']} |"
        )

    lines += [
        "",
        "JEI, Occultism, Modonomicon, Balm은 각각 `mezz_config`, `codedefinedgui`·`magicparticleslib`,",
        "`commonmark`, `kuma_api`를 JAR 안에 내장하므로 따로 설치하지 않는다.",
        "JourneyMap도 `commonnetworking`, `journeymap_api`, `pngj`를 내장한다.",
        "",
        "Lithium과 Clumps는 서버와 클라이언트 양쪽에서 동작하는 모드라 서버와 같은 파일을 함께 담는다.",
        "멀티플레이 동작은 이미 서버가 처리하며, 클라이언트 설치는 싱글플레이(통합 서버)에서 같은",
        "동작을 얻기 위한 것이다.",
        "",
        "Mouse Tweaks와 ImmediatelyFast는 Modrinth가 `client_side=required`,",
        "`server_side=unsupported`로 표시한 클라이언트 전용 모드라 서버에는 설치하지 않는다.",
        "Mouse Tweaks는 같은 버전의 배포 파일 3개 중 실행용 primary JAR만 담고",
        "`-api.jar`·`-src.jar`는 제외한다.",
        "",
        "## 모드 출처 표기",
        "",
        "이 팩은 CurseForge·Modrinth 밖에서 배포하는 비공개 모드팩이므로, 제작자가 요구하는 출처 링크를",
        "여기에 둔다. 각 모드의 저작권은 제작자에게 있다.",
        "",
        "- JourneyMap (Techbrew, Mysticdrew)",
        "  - 공식 사이트: http://journeymap.info/",
        "  - Modrinth: https://modrinth.com/mod/journeymap",
        "  - 라이선스: https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/",
        "",
        "나머지 모드의 라이선스와 출처는 `LICENSES.md`에 있다.",
        "",
        "## 서버에만 두고 제외한 모드",
        "",
        "| 모드 | 제외 근거 |",
        "| --- | --- |",
    ]
    for title in sorted(EXCLUSIONS):
        lines.append(f"| {title} | {EXCLUSIONS[title]} |")

    lines += [
        "",
        "제외한 모드는 모두 NeoForge 네트워크 페이로드를 등록하지 않으며, 클라이언트가 알아야 할",
        "블록·아이템 레지스트리도 추가하지 않는다. Structures와 Towns and Towers는 클래스 파일이",
        "하나도 없는 데이터팩 JAR이라 구조물 데이터를 서버가 만들어 보낸다.",
        "",
        "Sodium은 1.1.1부터 넣지 않는다. 서버 전용이어서가 아니라 Windows 크래시 때문이다.",
        "Xaero's Minimap은 1.1.3에서 뺐다. 같은 이유이며 JourneyMap이 그 자리를 대신한다.",
        "",
        "## 확인하지 않은 사항",
        "",
        "- **1.1.3 구성으로 Windows에서 실행하거나 서버에 접속해 보지 않았다.** 파일 무결성·의존성·",
        "  메타데이터만 리눅스에서 검증했다. JourneyMap이 1.1.2의 크래시를 해결한다는 확인은 아직 없다.",
        "- 실행과 서버 접속이 함께 확인된 유일한 구성은 Sodium JAR을 꺼 둔 1.1.0 인스턴스다.",
        "- 1.1.2의 `0xc0000005` 크래시는 A/B로 방아쇠가 Xaero's Minimap임을 확인했을 뿐, 네이티브",
        "  실패 메커니즘은 규명하지 않았다. 모드 결함인지 드라이버·GPU·NeoForge 베타와의 조합인지",
        "  구분하지 않았고, 다른 환경에서도 같은 크래시가 난다는 뜻이 아니다.",
        "- 1.1.0의 `0xc0000409` 크래시 원인도 규명하지 않았다. 두 크래시가 같은 뿌리인지 모른다.",
        "- JourneyMap의 지도·웨이포인트 동작과 다른 모드와의 렌더링 충돌 여부를 확인하지 않았다.",
        "- `.mrpack`을 MultiMC로 실제 가져와 보지 않았다. MultiMC 위키가 `.mrpack` 가져오기를",
        "  지원 형식으로 적고 있다는 문서 근거까지만 확인했고, 위키는 최소 버전을 명시하지 않는다.",
        "- MultiMC 인스턴스 ZIP은 아카이브 구조와 컴포넌트 UID·버전을 파일 수준에서만 확인했다.",
        "- NeoForge 26.3.0.8-beta와 일부 베타 모드(JEI, Curios, Farmer's Delight 이식판)의",
        "  런타임 안정성은 확인되지 않았다.",
        "- Lithium·ImmediatelyFast·Mouse Tweaks의 실제 성능 개선 효과는 확인하지 않았다.",
        "",
        "라이선스와 출처 표기는 `LICENSES.md`를 참고한다.",
    ]
    return "\n".join(lines) + "\n"


def render_licenses(mods):
    lines = [
        "# 라이선스와 출처 표기",
        "",
        "이 팩은 각 모드의 원본 JAR을 수정 없이 담거나 원본 배포 URL을 참조한다.",
        "모든 저작권은 각 제작자에게 있다. 이 팩은 Aziran 서버 접속용 비공개 배포물이며,",
        "공개 재업로드나 재호스팅 용도로 쓰지 않는다.",
        "",
    ]
    for mod in mods:
        lic = mod["license"]
        lines.append(f"## {mod['title']} {mod['version_number']}")
        lines.append("")
        lines.append(f"- 라이선스: {lic['name']} (`{lic['id']}`)")
        if mod["url"]:
            lines.append(f"- 원본 배포: {mod['url']}")
        elif mod["project_slug"]:
            lines.append(f"- 프로젝트: {mod['project_slug']}")
        if lic["url"]:
            lines.append(f"- 근거: {lic['url']}")
        if lic["note"]:
            lines.append(f"- 비고: {lic['note']}")
        if lic.get("distribution_note"):
            lines.append(f"- 배포 범위: {lic['distribution_note']}")
        if mod["bundle_jar"]:
            lines.append("- 팩 포함 방식: 원본 JAR을 수동 ZIP·MultiMC 인스턴스 ZIP에 수정 없이 담는다.")
        else:
            lines.append(
                "- 팩 포함 방식: JAR을 담지 않는다. `.mrpack`이 Modrinth CDN 다운로드 항목으로만 "
                "지정하며, 수동 ZIP과 MultiMC 인스턴스 ZIP에는 들어 있지 않다."
            )
            if mod.get("bundle_jar_reason"):
                lines.append(f"- 제외 근거: {mod['bundle_jar_reason']}")
        lines.append("")
    return "\n".join(lines)


def mrpack_name():
    return f"aziran-26.3-client-{PACK_VERSION}.mrpack"


def manual_zip_name():
    return f"aziran-26.3-client-{PACK_VERSION}-manual.zip"


def multimc_zip_name():
    return f"aziran-26.3-client-{PACK_VERSION}-multimc.zip"


def render_manifest(mods):
    """수동 설치·MultiMC 양쪽에서 쓰는 무결성 확인용 파일 목록. 경로는 .minecraft 기준이다.

    아카이브에 담은 JAR만 적는다. 라이선스 때문에 담지 않은 모드는 이 목록에 없다.
    """
    return {
        "pack": PACK_NAME,
        "version": PACK_VERSION,
        "install_root": ".minecraft",
        "files": [
            {
                "path": f"mods/{mod['filename']}",
                "size": mod["size"],
                "sha1": mod["sha1"],
                "sha512": mod["sha512"],
            }
            for mod in bundled_mods(mods)
        ],
    }


def build_mrpack(server_lock, mods, readme, licenses):
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": PACK_VERSION,
        "name": PACK_NAME,
        "summary": PACK_SUMMARY,
        "files": [],
        "dependencies": {
            "minecraft": server_lock["minecraft_version"],
            "neoforge": server_lock["loader_version"],
        },
    }
    for mod in mods:
        if mod["mrpack_delivery"] != "download":
            continue
        index["files"].append({
            "path": f"mods/{mod['filename']}",
            "hashes": {"sha1": mod["sha1"], "sha512": mod["sha512"]},
            # 이 팩은 클라이언트 전용이다. 서버에는 이 팩으로 아무것도 설치하지 않는다.
            "env": {"client": "required", "server": "unsupported"},
            "downloads": [mod["url"]],
            "fileSize": mod["size"],
        })

    out = DIST / mrpack_name()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n")
        zf.writestr("README.md", readme)
        zf.writestr("LICENSES.md", licenses)
        for mod in mods:
            if mod["mrpack_delivery"] == "client-overrides":
                zf.write(jar_path(mod), f"client-overrides/mods/{mod['filename']}")
    return out, index


def build_manual_zip(mods, readme, licenses):
    manifest = render_manifest(mods)
    out = DIST / manual_zip_name()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.md", readme)
        zf.writestr("LICENSES.md", licenses)
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for mod in bundled_mods(mods):
            zf.write(jar_path(mod), f"mods/{mod['filename']}")
    return out, manifest


def build_multimc_zip(server_lock, mods, readme, licenses):
    """MultiMC 인스턴스 내보내기 형식으로 묶는다.

    Minecraft와 NeoForge는 파일로 담지 않고 mmc-pack.json의 컴포넌트로만 지정한다.
    MultiMC가 공식 메타데이터에서 해당 버전을 찾아 직접 내려받는다.
    어느 PC에서 풀어도 같게 동작하도록 Java 경로·계정·서버 주소·실행 훅은 넣지 않는다.
    JAR 재배포가 금지된 모드는 담지 않으므로 이 ZIP만으로는 팩 구성이 완성되지 않는다.
    README가 해당 모드를 공식 배포처에서 받아 넣는 절차를 안내한다.
    """
    pack = {
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedVersion": server_lock["minecraft_version"],
                "important": True,
                "uid": MULTIMC_MINECRAFT_UID,
                "version": server_lock["minecraft_version"],
            },
            {
                "cachedName": "NeoForge",
                "cachedRequires": [
                    {"equals": server_lock["minecraft_version"], "uid": MULTIMC_MINECRAFT_UID}
                ],
                "cachedVersion": server_lock["loader_version"],
                "uid": MULTIMC_NEOFORGE_UID,
                "version": server_lock["loader_version"],
            },
        ],
        "formatVersion": 1,
    }
    # OneSix 인스턴스의 기본값만 쓴다. Override*가 모두 false라 런처의 전역 설정을 따른다.
    instance_cfg = "\n".join([
        "InstanceType=OneSix",
        f"name={MULTIMC_INSTANCE_NAME}",
        "iconKey=default",
        f"notes={PACK_SUMMARY}",
        "OverrideCommands=false",
        "OverrideConsole=false",
        "OverrideJavaArgs=false",
        "OverrideJavaLocation=false",
        "OverrideMemory=false",
        "OverrideWindow=false",
    ]) + "\n"
    manifest = render_manifest(mods)
    out = DIST / multimc_zip_name()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mmc-pack.json", json.dumps(pack, ensure_ascii=False, indent=4) + "\n")
        zf.writestr("instance.cfg", instance_cfg)
        zf.writestr("README.md", readme)
        zf.writestr("LICENSES.md", licenses)
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for mod in bundled_mods(mods):
            zf.write(jar_path(mod), f".minecraft/mods/{mod['filename']}")
    return out, pack


def prune_old_multimc_zips():
    """이번 버전이 아닌 MultiMC 인스턴스 ZIP을 dist/에서 휴지통으로 옮긴다.

    MultiMC 가져오기는 고른 파일 하나만 보므로, dist/에 이전 버전 인스턴스 ZIP이 남아 있으면
    Sodium이 들어간 옛 구성을 실수로 다시 가져올 수 있다. 이미 런처에 가져와 둔 인스턴스는
    이 파일과 별개라 영향을 받지 않는다. .mrpack과 수동 ZIP은 건드리지 않는다.

    영구 삭제하지 않고 `gio trash`로 데스크톱 휴지통에 넣어 되돌릴 수 있게 한다. 휴지통은
    원래 경로를 함께 기록하므로 파일 관리자나 `gio trash --restore`로 dist/에 복구할 수 있다.
    gio가 없거나 명령이 실패하면 조용히 넘어가지 않고 빌드를 중단한다. 되돌릴 수 없는
    삭제로 대체하지 않는다.
    """
    current = multimc_zip_name()
    stale = [path for path in sorted(DIST.glob("aziran-26.3-client-*-multimc.zip"))
             if path.name != current]
    if not stale:
        return []

    gio = shutil.which("gio")
    if gio is None:
        raise SystemExit(
            "이전 MultiMC 인스턴스 ZIP을 휴지통으로 보낼 gio를 찾지 못했다: "
            + ", ".join(path.name for path in stale)
            + "\n  gio를 설치하거나(glib2 계열 패키지) 해당 파일을 직접 옮긴 뒤 다시 실행한다."
        )

    result = subprocess.run(
        [gio, "trash", "--", *(str(path) for path in stale)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "gio trash가 실패해 이전 MultiMC 인스턴스 ZIP을 정리하지 못했다: "
            + (result.stderr.strip() or f"종료 코드 {result.returncode}")
        )

    left = [path.name for path in stale if path.exists()]
    if left:
        raise SystemExit(f"gio trash 이후에도 파일이 남아 있다: {', '.join(left)}")
    return [path.name for path in stale]


def write_client_lock(server_lock, mods, provided_mod_ids, archives):
    lock = {
        "pack_name": PACK_NAME,
        "pack_version": PACK_VERSION,
        "minecraft_version": server_lock["minecraft_version"],
        "loader": server_lock["loader"],
        "loader_version": server_lock["loader_version"],
        "java_version": server_lock["java_version"],
        "release_note": RELEASE_NOTE,
        "source_locks": [SERVER_LOCK.name, CLIENT_EXTRA_LOCK.name],
        "mod_count": len(mods),
        "shared_with_server_count": sum(1 for mod in mods if mod["origin"] == "server-lock"),
        "client_only_count": sum(1 for mod in mods if mod["origin"] == "client-extra-lock"),
        "bundled_jar_count": len(bundled_mods(mods)),
        "external_download_only": [
            {
                "title": mod["title"],
                "filename": mod["filename"],
                "url": mod["url"],
                "reason": mod.get("bundle_jar_reason"),
            }
            for mod in mods if not mod["bundle_jar"]
        ],
        "provided_mod_ids": provided_mod_ids,
        "excluded": [{"title": t, "reason": EXCLUSIONS[t]} for t in sorted(EXCLUSIONS)],
        "archives": archives,
        "mods": mods,
    }
    CLIENT_LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    server_lock, shared_mods = load_client_mods()
    _, extra_mods = load_client_extras()
    mods = shared_mods + extra_mods

    duplicate_ids = sorted(
        {mod_id for mod in shared_mods for mod_id in mod["declared_mod_ids"]}
        & {mod_id for mod in extra_mods for mod_id in mod["declared_mod_ids"]}
    )
    if duplicate_ids:
        raise SystemExit(f"서버 공통 모드와 클라이언트 전용 모드의 모드 ID가 겹친다: {duplicate_ids}")

    provided = check_dependency_closure(mods)

    DIST.mkdir(exist_ok=True)

    readme = render_readme(server_lock, mods)
    licenses = render_licenses(mods)
    mrpack_path, index = build_mrpack(server_lock, mods, readme, licenses)
    zip_path, manifest = build_manual_zip(mods, readme, licenses)
    multimc_path, _ = build_multimc_zip(server_lock, mods, readme, licenses)

    archives = {}
    for path in (mrpack_path, zip_path, multimc_path):
        digest = file_hashes(path)
        archives[path.name] = {"size": digest["size"], "sha256": digest["sha256"]}

    removed_zips = prune_old_multimc_zips()

    (DIST / "README.md").write_text(readme, encoding="utf-8")
    (DIST / "LICENSES.md").write_text(licenses, encoding="utf-8")
    (DIST / "SHA256SUMS.txt").write_text(
        "".join(f"{archives[name]['sha256']}  {name}\n" for name in sorted(archives)),
        encoding="utf-8",
    )
    write_client_lock(server_lock, mods, provided, archives)

    external = [mod for mod in mods if not mod["bundle_jar"]]
    print(f"모드 {len(mods)}개(서버 공통 {len(shared_mods)}개, 클라이언트 전용 {len(extra_mods)}개), "
          f"mrpack files {len(index['files'])}개, "
          f"client-overrides {len(mods) - len(index['files'])}개")
    print(f"JAR을 담은 아카이브(수동 ZIP·MultiMC ZIP) 모드 {len(mods) - len(external)}개")
    for mod in external:
        print(f"라이선스상 JAR을 담지 않는다(설치 중 Modrinth에서 받음): {mod['filename']}")
    for name, info in sorted(archives.items()):
        print(f"{name}: {info['size']} bytes sha256={info['sha256']}")
    for name in removed_zips:
        print(f"이전 MultiMC 인스턴스 ZIP을 휴지통으로 보냈다(복구 가능): {name}")


if __name__ == "__main__":
    main()

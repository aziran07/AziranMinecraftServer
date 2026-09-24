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
입력 lock의 셰이더 팩(shaderpacks)도 같은 규칙을 따른다.

공식 배포처에 없는 로컬 빌드 JAR(Iris)은 입력 lock의 source_bundle에 적힌 대응 소스와 라이선스
전문을 JAR과 함께 모든 아카이브의 sources/ 아래에 담는다.

세 아카이브 모두 Occultism 사역마 단축키만 미지정으로 적은 최소 options.txt를 담는다.
OCCULTISM_FAMILIARS의 설명을 참고한다.

세 아카이브 모두 멀티플레이 목록에 Aziran 서버 하나만 적은 servers.dat도 담는다.
render_servers_dat의 설명을 참고한다.
"""

import hashlib
import json
import struct
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
PACK_VERSION = "1.1.5"
PACK_SUMMARY = "Aziran Minecraft 26.3 NeoForge 서버 접속용 클라이언트 모드 구성"

# 1.1.5 구성과 그 바탕인 1.1.4 구성의 근거. 입력 lock의 restored·removed 항목과 같은 내용을
# 산출물에도 남긴다.
RELEASE_NOTE = (
    "1.1.5는 1.1.4와 같은 모드 18개와 셰이더 팩 1개를 그대로 두고, 멀티플레이 목록에 Aziran 서버"
    "(mc.aziran.uk) 하나만 적은 기본 servers.dat를 더한 판이다. 새로 만든 인스턴스는 멀티플레이 화면에 "
    "이 서버가 이미 들어 있으며, 이미 만든 인스턴스의 서버 목록은 소급해서 바뀌지 않는다. 1.1.5 "
    "아카이브로 새로 만든 인스턴스의 실행은 아직 확인하지 않았다. 이하는 1.1.4 기록이다. "
    "1.1.4는 1.1.3에 셰이더 구성을 더한 판이다. Iris 미병합 PR #3354의 커밋 "
    "10d3598cd96b0566497b66efe66256f468cd977e를 로컬 빌드한 JAR과 그 필수 의존성인 Sodium 0.9.2를 "
    "넣고, Complementary Reimagined r5.9.3 셰이더 팩을 .mrpack의 Modrinth CDN 다운로드 항목으로 "
    "지정한다(기본으로 켜지 않는다). Sodium은 1.1.0의 Windows 크래시(0xc0000409) 때문에 1.1.1부터 "
    "뺐던 같은 파일이며 그 원인은 규명하지 않았다. 사용자의 이전 1.1.4 시험 인스턴스는 options.txt를 "
    "초기화한 첫 실행에서 셰이더 적용과 서버 접속에 성공했지만, 두 번째 실행에서 Occultism 사역마 "
    "단축키가 key.keyboard.-1로 저장된 options.txt 때문에 InputConstants.isKeyDown의 "
    "IndexOutOfBoundsException으로 실패했다. Occultism 26.3 소스(커밋 631457c)의 "
    "ClientSetupEventHandler.java 218행이 사역마 단축키 18개를 Type.KEYBOARD, -1로 등록하는 것이 "
    "상류 결함이다. 1.1.4는 이를 고치지 못하며, 사역마 단축키 18개를 key.keyboard.unknown(미지정)으로 "
    "적은 최소 options.txt를 함께 담아 우회한다. 사용자가 기존 인스턴스의 복사본에서 -1을 unknown으로 "
    "바꾼 뒤 두 번 연속 실행·접속에 성공했다. 1.1.4 공개 뒤 사용자가 1.1.4 팩으로 새로 만든 "
    "인스턴스를 Windows에서 두 번 연속 실행하는 데 성공했다고 알려 왔다(서버 접속·셰이더 적용 여부는 "
    "보고에 없다)."
)

# Occultism 26.3(커밋 631457c) ClientSetupEventHandler.java 218행은 사역마마다 단축키를
# Type.KEYBOARD, -1로 등록한다. 첫 실행이 끝날 때 이 기본값이 options.txt에 key.keyboard.-1로
# 저장되고, 두 번째 실행에서 그 값을 읽어 InputConstants.isKeyDown이 IndexOutOfBoundsException으로
# 실패한다. 상류 결함은 그대로이며, 여기서는 해당 단축키를 미지정(key.keyboard.unknown)으로 적은
# options.txt를 처음부터 넣어 -1이 저장되지 않게 우회한다. 이름은 Occultism의 사역마 엔티티 ID다.
OCCULTISM_FAMILIARS = [
    "greedy_familiar",
    "drikwing",
    "wingnis",
    "bat_familiar",
    "deer_familiar",
    "cthulhu_familiar",
    "devil_familiar",
    "dragon_familiar",
    "blacksmith_familiar",
    "guardian_familiar",
    "headless_familiar",
    "chimera_familiar",
    "goat_familiar",
    "shub_niggurath_familiar",
    "beholder_familiar",
    "fairy_familiar",
    "mummy_familiar",
    "beaver_familiar",
]

# Minecraft 26.3이 options.txt에 쓰는 데이터 버전. 이보다 낮으면 게임이 옛 형식으로 보고 변환한다.
OPTIONS_DATA_VERSION = 5023
UNBOUND_KEY = "key.keyboard.unknown"

# 새 인스턴스의 멀티플레이 목록에 미리 넣어 두는 서버 항목.
SERVER_LIST_NAME = "Aziran"
SERVER_LIST_ADDRESS = "mc.aziran.uk"

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
    "BlueMap": "Modrinth client_side=unsupported. 웹 지도는 서버가 렌더링해 브라우저로 제공한다.",
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
            if mod["url"]:
                hint = f"{mod['url']} 를 받아 이 경로에 두고 다시 실행한다."
            else:
                hint = f"공식 배포처에 없는 로컬 빌드다. lock의 build 항목대로 빌드해 이 경로에 둔다: {mod.get('build')}"
            raise SystemExit(f"클라이언트 캐시에 JAR이 없다: {jar}\n  {hint}")
        actual = file_hashes(jar)
        if actual["sha512"] != mod["sha512"] or actual["size"] != mod["size"]:
            raise SystemExit(f"클라이언트 lock과 JAR이 일치하지 않는다: {mod['filename']}")

        url = mod["url"] or ""
        from_cdn = mod["source"] == "modrinth" and url.startswith(ALLOWED_DOWNLOAD_PREFIX)
        # 공식 배포처에 없는 로컬 빌드는 목적 코드와 함께 대응 소스를 담아야 한다.
        if mod["source"] == "local-build" and "source_bundle" not in mod:
            raise SystemExit(f"로컬 빌드 JAR에 source_bundle이 없어 대응 소스를 담을 수 없다: {mod['filename']}")
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
            "build": mod.get("build"),
            "source_bundle": verified_source_bundle(mod),
        })
    return extra_lock, mods


def verified_source_bundle(mod):
    """로컬 빌드 JAR의 대응 소스 파일을 lock의 크기·SHA-256과 대조한다. 없으면 None."""
    bundle = mod.get("source_bundle")
    if bundle is None:
        return None
    directory = REPO / bundle["directory"]
    listed = {entry["filename"] for entry in bundle["files"]}
    present = {path.name for path in directory.iterdir()} if directory.is_dir() else set()
    if listed != present:
        raise SystemExit(
            f"{mod['title']} 소스 번들 디렉터리 {directory}의 파일이 lock과 다르다. "
            f"lock에만 있음: {sorted(listed - present)}, 디렉터리에만 있음: {sorted(present - listed)}"
        )
    for entry in bundle["files"]:
        actual = file_hashes(directory / entry["filename"])
        if actual["sha256"] != entry["sha256"] or actual["size"] != entry["size"]:
            raise SystemExit(f"{mod['title']} 소스 번들 파일이 lock과 일치하지 않는다: {entry['filename']}")
    return bundle


def load_shaderpacks(extra_lock):
    """입력 lock의 셰이더 팩을 읽고 캐시 사본을 lock과 대조한다.

    셰이더 팩은 라이선스상 .mrpack의 Modrinth CDN 다운로드 항목으로만 넣으므로 CDN URL이 필수다.
    """
    packs = []
    for pack in extra_lock.get("shaderpacks", []):
        path = CLIENT_CACHE / pack["filename"]
        if not path.is_file():
            raise SystemExit(
                f"클라이언트 캐시에 셰이더 팩이 없다: {path}\n"
                f"  {pack['url']} 를 받아 이 경로에 두고 다시 실행한다."
            )
        actual = file_hashes(path)
        if actual["sha512"] != pack["sha512"] or actual["size"] != pack["size"]:
            raise SystemExit(f"클라이언트 lock과 셰이더 팩이 일치하지 않는다: {pack['filename']}")
        if pack["bundle_jar"] or not pack["url"].startswith(ALLOWED_DOWNLOAD_PREFIX):
            raise SystemExit(
                f"셰이더 팩은 Modrinth CDN 다운로드로만 넣는다(bundle_jar=false, CDN URL 필요): {pack['filename']}"
            )
        packs.append({
            "title": pack["title"],
            "filename": pack["filename"],
            "path": f"shaderpacks/{pack['filename']}",
            "source": pack["source"],
            "project_slug": pack["project_slug"],
            "version_number": pack["version_number"],
            "url": pack["url"],
            "size": actual["size"],
            "sha1": actual["sha1"],
            "sha512": actual["sha512"],
            "sha256": actual["sha256"],
            "license": pack["license"],
            "bundle_jar": False,
            "bundle_jar_reason": pack["bundle_jar_reason"],
            "enabled_by_default": pack["enabled_by_default"],
        })
    return packs


def render_options_txt():
    """사역마 단축키 18개만 미지정으로 적은 최소 options.txt. 나머지 설정은 게임 기본값을 따른다.

    그래픽·언어·마지막 접속 서버 같은 개인 설정은 넣지 않는다.
    """
    lines = [f"version:{OPTIONS_DATA_VERSION}"]
    lines += [f"key_key.occultism.familiar.{name}:{UNBOUND_KEY}" for name in OCCULTISM_FAMILIARS]
    return "\n".join(lines) + "\n"


def nbt_string(value):
    """NBT 문자열 본문: 부호 없는 2바이트 빅엔디언 길이 + UTF-8 바이트."""
    data = value.encode("utf-8")
    return struct.pack(">H", len(data)) + data


def render_servers_dat():
    """멀티플레이 목록에 Aziran 서버 하나만 적은 servers.dat.

    Minecraft가 쓰는 것과 같은 압축하지 않은 NBT다. 이름 없는 루트 compound 안에 compound 목록
    `servers`가 있고, 각 항목은 문자열 `name`과 `ip`만 가진다. 다른 서버나 개인 설정은 넣지 않는다.
    """
    entry = (
        b"\x08" + nbt_string("name") + nbt_string(SERVER_LIST_NAME)
        + b"\x08" + nbt_string("ip") + nbt_string(SERVER_LIST_ADDRESS)
        + b"\x00"
    )
    return (
        b"\x0a" + nbt_string("")
        + b"\x09" + nbt_string("servers") + b"\x0a" + struct.pack(">i", 1)
        + entry
        + b"\x00"
    )


def source_bundle_entries(mods):
    """아카이브에 담을 (로컬 파일, 아카이브 경로) 목록. JAR을 담는 로컬 빌드 모드의 소스만 고른다."""
    entries = []
    for mod in bundled_mods(mods):
        bundle = mod.get("source_bundle")
        if bundle is None:
            continue
        for entry in bundle["files"]:
            entries.append((
                REPO / bundle["directory"] / entry["filename"],
                f"{bundle['archive_path']}/{entry['filename']}",
            ))
    return entries


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


def render_readme(server_lock, mods, shaderpacks):
    external = [mod for mod in mods if not mod["bundle_jar"]]
    bundled_count = len(mods) - len(external)
    iris = next(mod for mod in mods if mod["declared_mod_ids"] == ["iris"])
    lines = [
        f"# {PACK_NAME} {PACK_VERSION}",
        "",
        f"Aziran Minecraft `{server_lock['minecraft_version']}` NeoForge 서버에 접속하기 위한 클라이언트 모드 구성이다.",
        "서버와 공유하는 모드는 서버와 같은 파일을 담았고, 여기에 서버가 쓰지 않는 클라이언트 전용",
        "최적화·편의·셰이더 모드를 더했다. 서버 전용 모드와 서버 설정·월드·로그는 포함하지 않는다.",
        "",
        "## 먼저 읽을 것: ZIP 두 개에는 모든 파일이 들어 있지 않다",
        "",
        f"**`{manual_zip_name()}`과 `{multimc_zip_name()}`에는 아래 파일이 담겨 있지 않다.**",
        "제작자 라이선스가 파일을 다시 배포하거나 모드팩 안에 직접 담는 것을 금지하고, 모드팩에는",
        "CurseForge 또는 Modrinth에서 직접 내려받는 방식으로만 넣도록 허용하기 때문이다.",
        "빠뜨린 것이 아니라 라이선스를 지키려고 뺀 것이다.",
        "",
    ]
    for mod in external:
        lines.append(f"- 모드 {mod['title']} {mod['version_number']} (`mods/`)")
    for pack in shaderpacks:
        lines.append(f"- 셰이더 팩 {pack['title']} {pack['version_number']} (`shaderpacks/`)")
    lines += [
        "",
        f"- **권장: `{mrpack_name()}`을 쓴다.** 런처가 설치 중에 Modrinth에서 위 파일을 직접 내려받으므로",
        f"  라이선스 조건을 만족하면서 모드 {len(mods)}개와 셰이더 팩이 모두 갖춰진다.",
        "  MultiMC도 `Add Instance` → `Import from zip`에서 `.mrpack`을 가져올 수 있다.",
        "  MultiMC 위키의 Import Instance 문서가 가져올 수 있는 형식으로 Modrinth `.mrpack`을 적고 있다",
        "  (https://github.com/MultiMC/Launcher/wiki/Import-Instance).",
        f"- ZIP 두 개를 쓰면 모드 {bundled_count}개만 설치되고 셰이더 팩은 없다. 나머지는 아래 절차로 직접 받아 넣는다.",
        "",
        "### 직접 받아 넣는 절차 (ZIP으로 설치할 때만)",
        "",
    ]
    downloads = [(mod, "mod", "mods") for mod in external] + [(pack, "shader", "shaderpacks") for pack in shaderpacks]
    for item, kind, folder in downloads:
        lines += [
            f"**{item['title']} {item['version_number']}**",
            "",
            f"1. 공식 Modrinth 프로젝트에서 받는다: https://modrinth.com/{kind}/{item['project_slug']}",
            f"   이 팩이 고정한 파일의 직접 링크는 {item['url']} 이다.",
            "   CurseForge의 공식 프로젝트 페이지에서 같은 버전을 받아도 된다.",
            "2. 받은 파일이 팩이 고정한 것과 같은지 대조한다.",
            f"   - 파일 이름: `{item['filename']}`",
            f"   - 크기: {item['size']} 바이트",
            f"   - SHA-1: `{item['sha1']}`",
            f"   - SHA-512: `{item['sha512']}`",
            f"3. 게임 디렉터리(MultiMC라면 인스턴스의 `.minecraft`)의 `{folder}/` 폴더에 받은 파일을",
            "   압축을 풀지 않고 그대로 넣는다. 폴더가 없으면 만든다.",
            "4. 다른 곳에서 재배포된 사본은 쓰지 않는다. 라이선스가 금지한다.",
            "",
            f"   라이선스 근거: {item['license']['url']}",
            "",
        ]

    lines += [
        "## 1.1.5 변경: 기본 멀티플레이 서버 목록 추가",
        "",
        "모드 18개와 셰이더 팩 1개는 1.1.4와 같다. 멀티플레이 목록에",
        f"`{SERVER_LIST_NAME}`(`{SERVER_LIST_ADDRESS}`) 서버 하나만 적은 `servers.dat`만 더했다.",
        "새로 만든 인스턴스는 멀티플레이 화면에 이 서버가 이미 들어 있다. 아래 설명 참고.",
        "",
        "## 1.1.4 변경: 셰이더 구성 추가",
        "",
        "1.1.3의 모드 16개는 바이트 단위로 그대로 두고 아래를 더했다.",
        "",
        f"- **Iris {iris['version_number']}** — 셰이더 모드. Iris 공식 릴리스가 아니다. NeoForge 26.3 지원은",
        f"  아직 병합되지 않은 Iris PR {iris['build']['pull_request']}에만 있어, 그 PR의 커밋",
        f"  `{iris['build']['commit']}`을 수정 없이 로컬에서 빌드한 JAR을 담았다.",
        "  Modrinth·CurseForge에 이 파일이 없으므로 `.mrpack`에도 JAR을 직접 넣었다.",
        "  빌드에 쓴 대응 소스와 라이선스 전문을 모든 아카이브의 `sources/iris/`에 함께 담았다.",
        "- **Sodium 0.9.2** — Iris의 필수 의존성이다. 1.1.0의 Windows 크래시(`0xc0000409`) 때문에 1.1.1부터",
        "  빼 두었던 것과 **같은 파일**이다. 그 크래시의 원인은 규명하지 않았으므로 다시 날 수 있다.",
        "- **Complementary Reimagined r5.9.3** — 셰이더 팩. `.mrpack`으로 설치하면 런처가 Modrinth에서",
        "  받아 `shaderpacks/`에 넣는다. **기본으로 켜 두지 않는다.** 아래 절차로 직접 켠다.",
        "- **`options.txt`** — Occultism 사역마 단축키 18개를 미지정으로 적은 최소 설정 파일. 아래 설명 참고.",
        "",
        "### 셰이더 켜는 법",
        "",
        "1. 게임을 실행하고 `Options`(설정) → `Video Settings`(비디오 설정)로 간다.",
        "2. `Shader Packs...`(셰이더 팩)을 누른다. 이 버튼은 Iris가 추가한다.",
        "3. 목록에서 `ComplementaryReimagined_r5.9.3`을 골라 `Apply`(적용) 후 `Done`(완료)을 누른다.",
        "4. 끄려면 같은 화면에서 셰이더를 `OFF`로 바꾼다. 셰이더를 켠 채 실행이 안 되면 인스턴스의",
        "   `.minecraft/config/iris.properties`를 지우면 셰이더가 꺼진 상태로 돌아간다.",
        "",
        "셰이더는 그래픽 부하가 크다. 프레임이 낮으면 셰이더 설정 화면에서 품질 프로필을 낮추거나 끈다.",
        "",
        "### Occultism 사역마 단축키 문제와 options.txt",
        "",
        "Occultism 26.3 소스(커밋 `631457c`)의 `ClientSetupEventHandler.java` 218행은 사역마 단축키",
        "18개를 `Type.KEYBOARD, -1`로 등록한다. 첫 실행을 마칠 때 이 값이 `options.txt`에",
        "`key.keyboard.-1`로 저장되고, **두 번째 실행**에서 그 값을 읽은 게임이 `InputConstants.isKeyDown`의",
        "`IndexOutOfBoundsException`으로 멈춘다. 이것은 Occultism의 상류 결함이며 이 팩이 고치지 못한다.",
        "",
        "이전 1.1.4 시험 인스턴스에서 실제로 이렇게 됐다. `options.txt`를 초기화한 첫 실행에서는 셰이더",
        "적용과 서버 접속까지 성공했지만, 두 번째 실행이 위 오류로 실패했다.",
        "",
        "그래서 이 팩은 사역마 단축키 18개를 `key.keyboard.unknown`(미지정)으로 적은 최소 `options.txt`를",
        "함께 담는다(`.mrpack`은 `client-overrides/options.txt`, 수동 ZIP은 `options.txt`, MultiMC ZIP은",
        "`.minecraft/options.txt`). 파일에는 `version` 줄과 이 18줄만 있고, 그래픽·언어·마지막 접속 서버·",
        "계정 같은 개인 설정은 없다. 나머지 설정은 게임 기본값으로 시작한다.",
        "사용자가 기존 인스턴스의 복사본에서 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꾸자",
        "두 번 연속 실행과 서버 접속에 성공했고 `-1`이 다시 생기지 않았다.",
        "",
        "주의할 점:",
        "",
        "- 사역마 단축키는 미지정 상태로 시작한다. 쓰려면 `Controls`(조작) → `Key Binds`에서 원하는 키를 지정한다.",
        "- 조작 화면에서 사역마 단축키를 **기본값으로 초기화(Reset)하지 않는다.** Occultism의 기본값이",
        "  `-1`이라 다시 `key.keyboard.-1`이 저장되고 다음 실행에서 같은 오류가 난다.",
        "- 이 `options.txt`는 **새 인스턴스**를 만들 때만 그대로 쓰인다. 이미 `options.txt`가 있는 인스턴스나",
        "  게임 디렉터리에 설치하면 런처·설치 방법에 따라 기존 파일이 남아 이 설정이 적용되지 않을 수 있다.",
        "",
        "**이미 있는 인스턴스를 고치는 방법:** 게임을 끈 상태에서 인스턴스의 `.minecraft/options.txt`를",
        "텍스트 편집기로 열어 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꾸고 저장한다.",
        "다른 줄은 건드리지 않아도 된다. 이 팩의 `options.txt`로 통째로 덮어쓰면 기존 개인 설정이 사라진다.",
        "",
        "### 멀티플레이 서버 목록(servers.dat)",
        "",
        f"이 팩은 멀티플레이 목록에 `{SERVER_LIST_NAME}` 서버(주소 `{SERVER_LIST_ADDRESS}`) 하나만 적은",
        "`servers.dat`를 함께 담는다(`.mrpack`은 `client-overrides/servers.dat`, 수동 ZIP은 `servers.dat`,",
        "MultiMC ZIP은 `.minecraft/servers.dat`). 새 인스턴스에서 게임을 켜고 `Multiplayer`(멀티플레이)로",
        "들어가면 이 서버가 이미 목록에 있으므로 주소를 직접 입력하지 않아도 된다.",
        "",
        "- 이 파일은 **새로 만드는 인스턴스**에만 적용된다. 이미 만들어 둔 인스턴스나 게임 디렉터리의",
        "  서버 목록은 이 팩이 소급해서 바꾸지 않는다. 기존 인스턴스에서는 `Add Server`(서버 추가)로",
        f"  `{SERVER_LIST_ADDRESS}`를 직접 추가한다.",
        "- 수동으로 설치할 때 게임 디렉터리에 `servers.dat`가 이미 있으면 **덮어쓰지 않는다.** 덮어쓰면",
        "  기존에 저장해 둔 다른 서버 목록이 모두 사라진다.",
        "",
        "### JourneyMap (미니맵·지도)",
        "",
        "1.1.3부터 미니맵은 Xaero's Minimap 대신 JourneyMap이다. 게임에 들어가면 화면 구석에 미니맵이",
        "보이고, 전체 지도는 JourneyMap 단축키(기본값 `J`, `Controls`에서 바꿀 수 있다)로 연다.",
        "`.mrpack`으로 설치하면 런처가 Modrinth에서 JourneyMap을 받는다. ZIP으로 설치했다면 위 \"직접",
        "받아 넣는 절차\"대로 넣어야 한다.",
        "",
        "Modrinth는 이 모드를 `client_side=optional`, `server_side=optional`로 표시한다. 지도 표시와",
        "웨이포인트는 클라이언트만으로 동작하므로 서버 구성·서버 모드 디렉터리는 바꾸지 않았다.",
        "JourneyMap JAR은 `commonnetworking`을 필수 의존성으로 선언하지만, 내장 JAR",
        "`common-networking-neoforge-26.3-1.1.1.jar`가 그 모드를 제공하므로 따로 설치하지 않는다.",
        "",
        "`.mrpack` 항목의 `env.server=unsupported`는 \"이 팩이 서버에 아무것도 설치하지 않는다\"는 뜻이며,",
        "모드 자체의 서버 지원 여부와는 다른 값이다.",
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
        f"함께 설치한다. 모드 {len(mods)}개와 셰이더 팩이 모두 갖춰지는 방식은 이것뿐이다.",
        "모드 대부분과 셰이더 팩은 런처가 Modrinth CDN에서 직접 내려받고, Farmer's Delight 이식판과",
        "Iris 로컬 빌드는 팩 안에 들어 있다. 사역마 단축키용 `options.txt`와 Aziran 서버를 적은",
        "`servers.dat`도 함께 설치된다.",
        "이전 버전 인스턴스에 덮어쓰지 말고 **새 인스턴스로 만든다.** 이 팩은 기존 `mods/`를 정리하지",
        "않으므로 덮어쓰면 이전 구성의 JAR(예: Xaero's Minimap)이 남고, 기존 `options.txt`가 남을 수 있다.",
        "런처에 따라 기존 인스턴스에 덮어쓸 때 `servers.dat`가 팩의 파일로 바뀌어 저장해 둔 서버 목록이",
        "사라질 수도 있다.",
        "",
        "### 2. 수동 ZIP",
        "",
        f"`{manual_zip_name()}`은 런처를 쓰지 않는 설치용이다.",
        f"모드 JAR {bundled_count}개와 `options.txt`, `servers.dat`가 들어 있고, 위에서 안내한 파일은 직접 받아",
        "넣어야 한다.",
        "",
        "1. Minecraft 런처에 NeoForge "
        f"`{server_lock['loader_version']}` 설치 프로파일을 먼저 만든다.",
        "2. 해당 프로파일의 게임 디렉터리를 연다(기본값은 `.minecraft`). 가능하면 새 디렉터리를 쓴다.",
        "3. 이전 버전을 설치했던 디렉터리라면 `mods/xaerominimap-neoforge-26.3-26.5.3.jar`를 먼저 지운다.",
        "4. ZIP 안의 `mods/` 폴더 내용을 게임 디렉터리의 `mods/` 폴더에 넣는다.",
        "5. 게임 디렉터리에 `options.txt`가 **없으면** ZIP의 `options.txt`를 넣는다. **이미 있으면 덮어쓰지",
        "   말고** 위 \"이미 있는 인스턴스를 고치는 방법\"대로 `key.keyboard.-1`만 바꾼다.",
        "6. 게임 디렉터리에 `servers.dat`가 **없으면** ZIP의 `servers.dat`를 넣는다. **이미 있으면 덮어쓰지",
        f"   말고** 게임의 멀티플레이 화면에서 `{SERVER_LIST_ADDRESS}`를 직접 추가한다. 덮어쓰면 기존 서버 목록이",
        "   사라진다.",
        "7. 위 \"직접 받아 넣는 절차\"대로 나머지 모드와 셰이더 팩을 넣는다.",
        "8. `manifest.json`의 SHA-1/SHA-512와 실제 파일을 대조해 무결성을 확인한다.",
        "   `manifest.json`에는 ZIP에 담은 모드 JAR만 적혀 있다.",
        "",
        "`sources/` 폴더는 Iris 대응 소스라 게임 디렉터리에 넣지 않아도 된다.",
        "",
        "### 3. MultiMC 인스턴스 ZIP",
        "",
        f"`{multimc_zip_name()}`은 MultiMC 인스턴스 내보내기 형식이다.",
        f"모드 JAR {bundled_count}개와 `.minecraft/options.txt`, `.minecraft/servers.dat`가 팩 안에 들어 있다.",
        "**MultiMC를 쓴다면 이 ZIP 대신 `.mrpack`을 가져오는 쪽을 권한다.** `.mrpack`은 나머지 모드와",
        "셰이더 팩까지 런처가 받아 주므로 수작업이 없다.",
        "",
        "이전 버전 인스턴스를 그대로 쓰지 말고 **새 인스턴스로 가져온다.** 가져오기는 기존 인스턴스의",
        "`mods/`를 지우지 않으므로, 이전 인스턴스를 재사용하면 이전 JAR이 남아 이번 구성과 달라진다.",
        f"가져온 인스턴스 이름은 `{MULTIMC_INSTANCE_NAME}`이라 런처 목록에서 이전 인스턴스와 구분된다.",
        "",
        "1. MultiMC에서 `Add Instance`(인스턴스 추가)를 누른다.",
        "2. 왼쪽 목록에서 `Import from zip`(ZIP에서 가져오기)을 고른다.",
        f"3. 내려받은 `{multimc_zip_name()}`을 선택하고 `OK`를 누른다.",
        "4. 만들어진 인스턴스의 `Edit Instance` → `Settings` → `Java`에서 "
        f"Java {server_lock['java_version']} 실행 파일을 고른다. "
        "팩에는 Java 경로를 넣지 않았으므로 런처에서 직접 지정해야 한다.",
        "5. `Edit Instance` → `Folder`로 인스턴스 폴더를 열고, 위 \"직접 받아 넣는 절차\"대로",
        "   `.minecraft/mods/`에 나머지 모드를, `.minecraft/shaderpacks/`에 셰이더 팩을 넣는다.",
        "6. 인스턴스를 실행한다.",
        "",
        f"Minecraft `{server_lock['minecraft_version']}`와 NeoForge "
        f"`{server_lock['loader_version']}`는 팩에 담지 않고 인스턴스 정의(`mmc-pack.json`)로만 지정했다.",
        "MultiMC가 가져오기 후 첫 실행 때 공식 메타데이터를 보고 게임 파일과 로더를 내려받으므로,",
        "인터넷 연결과 로그인한 Minecraft 계정이 필요하다. 계정 정보는 팩에 넣지 않았다. 서버 주소는",
        "인스턴스 설정이 아니라 `.minecraft/servers.dat`의 멀티플레이 목록으로만 들어 있다.",
        "",
        "세 방식이 설치하는 구성은 같다. 다만 ZIP 두 개는 위에서 안내한 파일을 직접 넣어야",
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
        "## 셰이더 팩",
        "",
        "| 셰이더 팩 | 버전 | 설치 위치 | 팩 포함 | 기본 상태 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for pack in shaderpacks:
        state = "켜짐" if pack["enabled_by_default"] else "꺼짐(직접 켠다)"
        lines.append(
            f"| {pack['title']} | {pack['version_number']} | `{pack['path']}` | "
            f".mrpack 설치 중 Modrinth 다운로드 | {state} |"
        )

    lines += [
        "",
        "JEI, Occultism, Modonomicon, Balm은 각각 `mezz_config`, `codedefinedgui`·`magicparticleslib`,",
        "`commonmark`, `kuma_api`를 JAR 안에 내장하므로 따로 설치하지 않는다.",
        "JourneyMap도 `commonnetworking`, `journeymap_api`, `pngj`를 내장한다.",
        "Iris는 `glsl-transformer`, `jcpp`, `antlr4-runtime` 라이브러리를 내장한다.",
        "",
        "Lithium과 Clumps는 서버와 클라이언트 양쪽에서 동작하는 모드라 서버와 같은 파일을 함께 담는다.",
        "멀티플레이 동작은 이미 서버가 처리하며, 클라이언트 설치는 싱글플레이(통합 서버)에서 같은",
        "동작을 얻기 위한 것이다.",
        "",
        "Mouse Tweaks, ImmediatelyFast, Sodium, Iris는 Modrinth가 `client_side=required`,",
        "`server_side=unsupported`로 표시한 클라이언트 전용 모드라 서버에는 설치하지 않는다.",
        "Mouse Tweaks는 같은 버전의 배포 파일 3개 중 실행용 primary JAR만 담고",
        "`-api.jar`·`-src.jar`는 제외한다.",
        "",
        "## 출처 표기",
        "",
        "이 팩은 CurseForge·Modrinth 밖에서 배포하는 비공개 모드팩이므로, 제작자가 요구하는 출처 링크를",
        "여기에 둔다. 각 모드와 셰이더 팩의 저작권은 제작자에게 있다.",
        "",
        "- JourneyMap (Techbrew, Mysticdrew)",
        "  - 공식 사이트: http://journeymap.info/",
        "  - Modrinth: https://modrinth.com/mod/journeymap",
        "  - 라이선스: https://teamjm.github.io/journeymap-docs/6.0.x/about/licensing/",
        "- Complementary Shaders - Reimagined (Complementary Development, EminGT)",
        "  - 공식 사이트: https://www.complementary.dev/",
        "  - Modrinth: https://modrinth.com/shader/complementary-reimagined",
        "  - 라이선스: Complementary License Agreement 1.7 (셰이더 ZIP 안의 `License.txt`)",
        "  - 이 팩은 셰이더 팩 파일을 수정하거나 직접 담지 않고, `.mrpack`이 Modrinth에서 받게 한다.",
        "    이 팩에서 생기는 문제의 책임은 셰이더 제작자가 아니라 이 모드팩 운영자에게 있다.",
        f"- Iris (coderbot, IMS212) — 로컬 빌드, 소스: {iris['build']['repository']}"
        f" 커밋 `{iris['build']['commit']}`",
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
        "Xaero's Minimap은 1.1.3에서 뺐다. 16개를 모두 켠 1.1.2가 Windows에서 `0xc0000005`로",
        "크래시했고 그 JAR 하나만 끄면 실행됐기 때문이며(A/B 확인), JourneyMap이 그 자리를 대신한다.",
        "",
        "## 확인한 사항과 확인하지 않은 사항",
        "",
        "확인한 것:",
        "",
        "- 사용자의 이전 1.1.4 시험 인스턴스(Iris·Sodium·Complementary 포함)는 `options.txt`를 초기화한",
        "  첫 실행에서 Complementary 셰이더 적용과 서버 접속에 성공했다. 두 번째 실행은 위의",
        "  `key.keyboard.-1` 문제로 실패했다.",
        "- 사용자가 그 인스턴스의 복사본에서 `key.keyboard.-1`을 모두 `key.keyboard.unknown`으로 바꾸자",
        "  첫 실행과 두 번째 실행 모두 월드·서버 접속에 성공했고 `-1`이 다시 생기지 않았다.",
        "- 사용자가 공개한 1.1.4 팩으로 새로 만든 인스턴스를 Windows에서 두 번 연속 실행하는 데 성공했다고",
        "  알려 왔다. 그 보고는 실행 성공만 다루며, 두 실행의 서버 접속과 셰이더 적용 여부는 보고에 없다.",
        "- 리눅스에서 파일 무결성(크기·SHA-512), 모드 메타데이터의 필수 의존성, 아카이브 구성을 검증했다.",
        f"- 세 아카이브의 `servers.dat`가 `{SERVER_LIST_ADDRESS}` 서버 하나만 담은 NBT인지 파일 수준에서 검증했다.",
        "",
        "확인하지 않은 것:",
        "",
        "- **이 1.1.5 아카이브로 새로 만든 인스턴스는 아직 실행해 보지 않았다.** 멀티플레이 화면에 서버가",
        "  실제로 보이는지도 게임에서 확인하지 않았다. 1.1.5는 1.1.4와 모드·셰이더 파일이 같다.",
        "- Iris는 미병합 PR의 로컬 빌드다. 빌드 당시 NeoForge 26.3.0.7-beta를 기준으로 컴파일했으며,",
        "  공식 릴리스가 아니므로 다른 PC·드라이버에서의 안정성은 알 수 없다.",
        "- Sodium이 1.1.0에서 일으킨 `0xc0000409` 크래시의 원인은 규명하지 않았다. 다른 PC에서 재발할 수 있다.",
        "- 1.1.2의 `0xc0000005` 크래시는 A/B로 방아쇠가 Xaero's Minimap임을 확인했을 뿐, 네이티브",
        "  실패 메커니즘은 규명하지 않았다.",
        "- `.mrpack`을 MultiMC로 실제 가져와 보지 않았다. MultiMC 위키가 `.mrpack` 가져오기를",
        "  지원 형식으로 적고 있다는 문서 근거까지만 확인했다.",
        "- MultiMC 인스턴스 ZIP은 아카이브 구조와 컴포넌트 UID·버전을 파일 수준에서만 확인했다.",
        "- NeoForge 26.3.0.8-beta와 일부 베타 모드(JEI, Curios, Farmer's Delight 이식판)의",
        "  런타임 안정성은 확인되지 않았다.",
        "- Lithium·ImmediatelyFast·Mouse Tweaks·Sodium의 실제 성능 개선 효과는 측정하지 않았다.",
        "",
        "라이선스와 출처 표기는 `LICENSES.md`를 참고한다.",
    ]
    return "\n".join(lines) + "\n"


def render_licenses(mods, shaderpacks):
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
        if mod.get("build"):
            build = mod["build"]
            lines.append(f"- 빌드 원본: {build['repository']} 커밋 `{build['commit']}` ({build['pull_request']})")
            lines.append(f"- 빌드 비고: {build['note']}")
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
        bundle = mod.get("source_bundle")
        if bundle:
            lines.append(
                f"- 대응 소스: JAR을 담은 모든 아카이브(.mrpack·수동 ZIP·MultiMC ZIP)의 "
                f"`{bundle['archive_path']}/`에 함께 담는다. {bundle['note']}"
            )
            for entry in bundle["files"]:
                lines.append(f"  - `{entry['filename']}` ({entry['size']} 바이트, SHA-256 `{entry['sha256']}`)")
        lines.append("")
    for pack in shaderpacks:
        lic = pack["license"]
        lines += [
            f"## {pack['title']} {pack['version_number']} (셰이더 팩)",
            "",
            f"- 라이선스: {lic['name']} (`{lic['id']}`)",
            f"- 원본 배포: {pack['url']}",
            f"- 근거: {lic['url']}",
            f"- 비고: {lic['note']}",
            f"- 배포 범위: {lic['distribution_note']}",
            "- 팩 포함 방식: 파일을 담지 않는다. `.mrpack`이 Modrinth CDN 다운로드 항목"
            f"(`{pack['path']}`)으로만 지정하며, 수동 ZIP과 MultiMC 인스턴스 ZIP에는 들어 있지 않다.",
            f"- 제외 근거: {pack['bundle_jar_reason']}",
            "",
        ]
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


def build_mrpack(server_lock, mods, shaderpacks, readme, licenses, options_txt, servers_dat):
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
    # 셰이더 팩은 라이선스상 팩에 담지 않고 런처가 설치 중에 Modrinth CDN에서 받게 한다.
    for pack in shaderpacks:
        index["files"].append({
            "path": pack["path"],
            "hashes": {"sha1": pack["sha1"], "sha512": pack["sha512"]},
            "env": {"client": "required", "server": "unsupported"},
            "downloads": [pack["url"]],
            "fileSize": pack["size"],
        })

    out = DIST / mrpack_name()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n")
        zf.writestr("README.md", readme)
        zf.writestr("LICENSES.md", licenses)
        zf.writestr("client-overrides/options.txt", options_txt)
        zf.writestr("client-overrides/servers.dat", servers_dat)
        for mod in mods:
            if mod["mrpack_delivery"] == "client-overrides":
                zf.write(jar_path(mod), f"client-overrides/mods/{mod['filename']}")
        # 대응 소스는 게임 디렉터리에 설치하지 않도록 overrides 밖(팩 루트)에 둔다.
        for source, archive_path in source_bundle_entries(mods):
            zf.write(source, archive_path)
    return out, index


def build_manual_zip(mods, readme, licenses, options_txt, servers_dat):
    manifest = render_manifest(mods)
    out = DIST / manual_zip_name()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.md", readme)
        zf.writestr("LICENSES.md", licenses)
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        zf.writestr("options.txt", options_txt)
        zf.writestr("servers.dat", servers_dat)
        for mod in bundled_mods(mods):
            zf.write(jar_path(mod), f"mods/{mod['filename']}")
        for source, archive_path in source_bundle_entries(mods):
            zf.write(source, archive_path)
    return out, manifest


def build_multimc_zip(server_lock, mods, readme, licenses, options_txt, servers_dat):
    """MultiMC 인스턴스 내보내기 형식으로 묶는다.

    Minecraft와 NeoForge는 파일로 담지 않고 mmc-pack.json의 컴포넌트로만 지정한다.
    MultiMC가 공식 메타데이터에서 해당 버전을 찾아 직접 내려받는다.
    어느 PC에서 풀어도 같게 동작하도록 Java 경로·계정·실행 훅은 넣지 않는다.
    서버 주소는 인스턴스 설정이 아니라 .minecraft/servers.dat의 멀티플레이 목록으로만 넣는다.
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
        zf.writestr(".minecraft/options.txt", options_txt)
        zf.writestr(".minecraft/servers.dat", servers_dat)
        for mod in bundled_mods(mods):
            zf.write(jar_path(mod), f".minecraft/mods/{mod['filename']}")
        # 소스는 인스턴스 폴더 루트에 둔다. .minecraft 밖이라 게임이 읽지 않는다.
        for source, archive_path in source_bundle_entries(mods):
            zf.write(source, archive_path)
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


def write_client_lock(server_lock, mods, shaderpacks, provided_mod_ids, archives):
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
        "shaderpacks": shaderpacks,
        "seeded_options": {
            "archive_paths": {
                mrpack_name(): "client-overrides/options.txt",
                manual_zip_name(): "options.txt",
                multimc_zip_name(): ".minecraft/options.txt",
            },
            "version": OPTIONS_DATA_VERSION,
            "unbound_key_mappings": [f"key_key.occultism.familiar.{name}" for name in OCCULTISM_FAMILIARS],
            "value": UNBOUND_KEY,
            "reason": "Occultism 26.3(커밋 631457c) ClientSetupEventHandler.java 218행이 사역마 단축키를 "
                      "Type.KEYBOARD, -1로 등록해 key.keyboard.-1이 저장되고 다음 실행에서 "
                      "InputConstants.isKeyDown이 IndexOutOfBoundsException으로 실패하는 상류 결함의 우회.",
        },
        "seeded_servers": {
            "archive_paths": {
                mrpack_name(): "client-overrides/servers.dat",
                manual_zip_name(): "servers.dat",
                multimc_zip_name(): ".minecraft/servers.dat",
            },
            "format": "압축하지 않은 NBT",
            "servers": [{"name": SERVER_LIST_NAME, "ip": SERVER_LIST_ADDRESS}],
        },
        "provided_mod_ids": provided_mod_ids,
        "excluded": [{"title": t, "reason": EXCLUSIONS[t]} for t in sorted(EXCLUSIONS)],
        "archives": archives,
        "mods": mods,
    }
    CLIENT_LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    server_lock, shared_mods = load_client_mods()
    extra_lock, extra_mods = load_client_extras()
    shaderpacks = load_shaderpacks(extra_lock)
    mods = shared_mods + extra_mods

    duplicate_ids = sorted(
        {mod_id for mod in shared_mods for mod_id in mod["declared_mod_ids"]}
        & {mod_id for mod in extra_mods for mod_id in mod["declared_mod_ids"]}
    )
    if duplicate_ids:
        raise SystemExit(f"서버 공통 모드와 클라이언트 전용 모드의 모드 ID가 겹친다: {duplicate_ids}")

    provided = check_dependency_closure(mods)

    DIST.mkdir(exist_ok=True)

    readme = render_readme(server_lock, mods, shaderpacks)
    licenses = render_licenses(mods, shaderpacks)
    options_txt = render_options_txt()
    servers_dat = render_servers_dat()
    mrpack_path, index = build_mrpack(server_lock, mods, shaderpacks, readme, licenses,
                                      options_txt, servers_dat)
    zip_path, manifest = build_manual_zip(mods, readme, licenses, options_txt, servers_dat)
    multimc_path, _ = build_multimc_zip(server_lock, mods, readme, licenses, options_txt, servers_dat)

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
    write_client_lock(server_lock, mods, shaderpacks, provided, archives)

    external = [mod for mod in mods if not mod["bundle_jar"]]
    overrides = [mod for mod in mods if mod["mrpack_delivery"] == "client-overrides"]
    print(f"모드 {len(mods)}개(서버 공통 {len(shared_mods)}개, 클라이언트 전용 {len(extra_mods)}개), "
          f"셰이더 팩 {len(shaderpacks)}개, mrpack files {len(index['files'])}개, "
          f"client-overrides 모드 {len(overrides)}개")
    print(f"JAR을 담은 아카이브(수동 ZIP·MultiMC ZIP) 모드 {len(mods) - len(external)}개")
    for mod in external:
        print(f"라이선스상 JAR을 담지 않는다(설치 중 Modrinth에서 받음): {mod['filename']}")
    for pack in shaderpacks:
        print(f"라이선스상 셰이더 팩을 담지 않는다(설치 중 Modrinth에서 받음): {pack['filename']}")
    for name, info in sorted(archives.items()):
        print(f"{name}: {info['size']} bytes sha256={info['sha256']}")
    for name in removed_zips:
        print(f"이전 MultiMC 인스턴스 ZIP을 휴지통으로 보냈다(복구 가능): {name}")


if __name__ == "__main__":
    main()

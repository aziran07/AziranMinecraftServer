#!/usr/bin/env python3
"""Occultism 1.256.0 한국어 번역 리소스팩 빌더.

고정한 Occultism JAR의 en_us.json 키 집합을 기준으로 세 번역 JSON
(interface, guide_basics, guide_advanced)을 검증하고 합쳐 리소스팩 ZIP을 만든다.

- 원문 JAR의 SHA-256이 고정값과 다르면 중단한다.
- 번역 JSON의 중복 키, 객체가 아닌 최상위 값, 문자열이 아닌 값, 분할 범위를 벗어난 키,
  파일 사이의 겹치는 키, 원문 대비 누락·추가 키를 모두 모아 알리고 중단한다.
- 검증을 모두 통과한 뒤에만 같은 폴더의 임시 파일에 쓰고 교체하므로, 실패하면
  기존 산출물은 그대로 남고 새 ZIP은 생기지 않는다.
- 빌드 중에는 아무것도 내려받지 않는다. 팩 메타데이터와 라이선스·출처 파일은
  translations/occultism/ 아래의 저장된 파일을 그대로 담는다.

ZIP 항목 순서와 시각·권한은 고정해 같은 입력이면 같은 바이트가 나온다.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_JAR = REPO / "server-data-26.3-neoforge/mods/occultism-26.3-neoforge-1.256.0.jar"
DEFAULT_TRANSLATIONS = REPO / "translations/occultism/ko_kr"
DEFAULT_OUTPUT = REPO / "dist/occultism-ko-1.256.0-mc26.3.zip"
PACK_FILES = REPO / "translations/occultism"

SOURCE_SHA256 = "118d02366adffbd8ebbe0024f484c88d8720eff43fb70b1adfd7d0fde74ddb51"
SOURCE_LANG = "assets/occultism/lang/en_us.json"
TARGET_LANG = "assets/occultism/lang/ko_kr.json"
# 로컬 Minecraft 26.3 클라이언트 JAR의 version.json이 밝힌 resource version 97.1.
PACK_FORMAT = [97, 1]

SHARDS = ("interface", "guide_basics", "guide_advanced")
GUIDE_PREFIX = "book.occultism.dictionary_of_spirits."
BASICS_CATEGORIES = {"getting_started", "spirits", "pentacles", "rituals", "summoning_rituals"}

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_FILE_MODE = 0o644


class BuildError(Exception):
    """사용자에게 그대로 보여 줄 빌드 실패."""


def shard_for_key(key):
    """설계 문서의 분할 규칙에 따라 키가 속할 번역 파일 이름을 돌려준다."""
    if not key.startswith("book."):
        return "interface"
    if key.startswith(GUIDE_PREFIX) and key[len(GUIDE_PREFIX):].split(".")[0] in BASICS_CATEGORIES:
        return "guide_basics"
    return "guide_advanced"


def parse_json_object(text, label):
    """중복 키를 거부하며 JSON 객체를 읽는다. 문제는 label을 붙여 BuildError로 알린다."""
    duplicates = []

    def collect_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    try:
        data = json.loads(text, object_pairs_hook=collect_pairs)
    except json.JSONDecodeError as error:
        raise BuildError(f"{label}: JSON 문법 오류: {error}") from error
    if duplicates:
        raise BuildError(f"{label}: 중복 JSON 키 {len(duplicates)}개: " + ", ".join(duplicates))
    if not isinstance(data, dict):
        raise BuildError(f"{label}: 최상위 값은 JSON 객체여야 합니다 (현재 {type(data).__name__}).")
    return data


def read_source(jar_path):
    if not jar_path.is_file():
        raise BuildError(f"원문 JAR이 없습니다: {jar_path}")
    digest = hashlib.sha256(jar_path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise BuildError(
            f"원문 JAR의 SHA-256이 고정값과 다릅니다: {jar_path}\n"
            f"  기대값: {SOURCE_SHA256}\n  실제값: {digest}")
    with zipfile.ZipFile(jar_path) as archive:
        text = archive.read(SOURCE_LANG).decode("utf-8")
    return parse_json_object(text, f"{jar_path}!{SOURCE_LANG}")


def read_translations(translations_dir, source):
    """세 번역 파일을 검증해 원문 키 순서로 합친 사전을 돌려준다."""
    problems = []
    shards = {}
    for name in SHARDS:
        path = translations_dir / f"{name}.json"
        if not path.is_file():
            problems.append(f"{path}: 번역 파일이 없습니다.")
            continue
        try:
            shards[name] = parse_json_object(path.read_text(encoding="utf-8"), str(path))
        except BuildError as error:
            problems.append(str(error))
    if problems:
        raise BuildError("\n".join(problems))

    owners = {}
    for name, data in shards.items():
        path = translations_dir / f"{name}.json"
        non_strings = sorted(key for key, value in data.items() if not isinstance(value, str))
        if non_strings:
            problems.append(f"{path}: 문자열이 아닌 값 {len(non_strings)}개: " + ", ".join(non_strings))
        misplaced = sorted(key for key in data if key in source and shard_for_key(key) != name)
        if misplaced:
            problems.append(f"{path}: 다른 분할 파일에 속하는 키 {len(misplaced)}개: " + ", ".join(
                f"{key} -> {shard_for_key(key)}.json" for key in misplaced))
        for key in data:
            owners.setdefault(key, []).append(name)

    overlapping = sorted(key for key, names in owners.items() if len(names) > 1)
    if overlapping:
        problems.append(f"여러 번역 파일에 겹치는 키 {len(overlapping)}개: " + ", ".join(
            f"{key} ({', '.join(owners[key])})" for key in overlapping))
    extra = sorted(key for key in owners if key not in source)
    if extra:
        problems.append(f"원문에 없는 키 {len(extra)}개: " + ", ".join(
            f"{key} ({', '.join(owners[key])})" for key in extra))
    missing = [key for key in source if key not in owners]
    if missing:
        problems.append(f"번역이 없는 원문 키 {len(missing)}개: " + ", ".join(
            f"{key} -> {shard_for_key(key)}.json" for key in missing))
    if problems:
        raise BuildError("\n".join(problems))

    merged = {}
    for name in SHARDS:
        merged.update(shards[name])
    return {key: merged[key] for key in source}


def read_pack_files():
    """저장된 pack.mcmeta, LICENSE, NOTICE.md를 확인하고 ZIP 경로별 바이트로 돌려준다."""
    files = {}
    for name in ("pack.mcmeta", "LICENSE", "NOTICE.md"):
        path = PACK_FILES / name
        if not path.is_file() or not path.read_bytes().strip():
            raise BuildError(f"팩 파일이 없거나 비어 있습니다: {path}")
        files[name] = path.read_bytes()
    metadata = parse_json_object(files["pack.mcmeta"].decode("utf-8"), str(PACK_FILES / "pack.mcmeta"))
    pack = metadata.get("pack")
    if not isinstance(pack, dict):
        raise BuildError("pack.mcmeta: \"pack\" 객체가 없습니다.")
    for field in ("min_format", "max_format"):
        if pack.get(field) != PACK_FORMAT:
            raise BuildError(f"pack.mcmeta: {field}는 {PACK_FORMAT}이어야 합니다 (현재 {pack.get(field)!r}).")
    if not isinstance(pack.get("description"), str) or not pack["description"].strip():
        raise BuildError("pack.mcmeta: description 문자열이 필요합니다.")
    return files


def write_pack(output, entries):
    """검증이 끝난 항목을 임시 파일에 쓴 뒤 output으로 교체한다."""
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(entries):
                info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = ZIP_FILE_MODE << 16
                archive.writestr(info, entries[name])
        os.chmod(temporary, 0o644)
        os.replace(temporary, output)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description="Occultism 한국어 번역 리소스팩을 만듭니다.")
    parser.add_argument("--source-jar", type=Path, default=DEFAULT_SOURCE_JAR,
                        help=f"고정한 Occultism JAR (기본값: {DEFAULT_SOURCE_JAR.relative_to(REPO)})")
    parser.add_argument("--translations-dir", type=Path, default=DEFAULT_TRANSLATIONS,
                        help="interface/guide_basics/guide_advanced.json이 있는 폴더 "
                             f"(기본값: {DEFAULT_TRANSLATIONS.relative_to(REPO)})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"만들 ZIP 경로 (기본값: {DEFAULT_OUTPUT.relative_to(REPO)})")
    args = parser.parse_args()

    try:
        source = read_source(args.source_jar)
        translations = read_translations(args.translations_dir, source)
        entries = read_pack_files()
        entries[TARGET_LANG] = (json.dumps(translations, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        write_pack(args.output, entries)
    except BuildError as error:
        print(f"빌드 실패: {error}", file=sys.stderr)
        print(f"새 ZIP을 만들지 않았습니다: {args.output}", file=sys.stderr)
        return 1

    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"{args.output}: 번역 키 {len(translations)}개, {args.output.stat().st_size} bytes, SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

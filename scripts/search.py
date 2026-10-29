#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""search.py — 在本地官方手册纯文本索引中检索。

用法：
  python3 search.py "eAvalanche"                 # 在所有手册里搜
  python3 search.py "Quasistationary" -t sdevice # 只搜 SDevice 手册
  python3 search.py "AddParam" -t swb -n 10      # 最多 10 条
  python3 search.py -r "HeavyIon.*Time" -c 2     # 正则 + 前后 2 行上下文
  python3 search.py "MGOALS" --training          # 同时搜 Sentaurus_Training HTML

说明：
- 结果带 PDF 页码（pdftotext 用换页符分页，页码=换页符计数+1）。
- 默认索引位于 skill 的 references/manual_index/<release>/text。
- MANUAL_TEXT_DIR 可覆盖索引；SENTAURUS_TRAINING_DIR 可覆盖教程路径。
"""

import argparse
import os
from pathlib import Path
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
STROOT = os.environ.get("STROOT") or "/home/synopsys/sentaurus/W-2024.09-SP1"
STRELEASE = os.environ.get("STRELEASE") or "W-2024.09-SP1"
TEXT_DIR = Path(
    os.environ.get("MANUAL_TEXT_DIR")
    or SKILL_DIR / "references" / "manual_index" / STRELEASE / "text"
).expanduser()
TRAINING_DIR = Path(
    os.environ.get("SENTAURUS_TRAINING_DIR")
    or Path(STROOT) / "tcad" / STRELEASE / "Sentaurus_Training"
).expanduser()
MAX_LINE = 300


def iter_matches(path, pattern):
    """yield (page, lineno, line) for lines matching pattern."""
    page = 1
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for lineno, line in enumerate(stream, 1):
                page += line.count("\f")
                if pattern.search(line):
                    yield page, lineno, line.strip()
    except OSError as exc:
        print(f"!! cannot read {path}: {exc}", file=sys.stderr)


def search_texts(args, pattern):
    hits = 0
    for path in sorted(TEXT_DIR.rglob("*.txt")):
        relative_name = path.relative_to(TEXT_DIR).as_posix()
        if args.tool and args.tool.lower() not in relative_name.lower():
            continue
        shown_file = False
        for page, lineno, line in iter_matches(path, pattern):
            if not shown_file:
                print(f"\n== {relative_name} ==")
                shown_file = True
            print(f"  p.{page} L{lineno}: {line[:MAX_LINE]}")
            hits += 1
            if hits >= args.max_total:
                print("\n...(达到 --max-total 上限，请加限定词或 -t 缩小范围)")
                return hits
    return hits


TAG_RE = re.compile(r"<[^>]+>")


def search_training(args, pattern):
    hits = 0
    for path in sorted(TRAINING_DIR.rglob("*.html")):
        try:
            text = TAG_RE.sub(" ", path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                relative_name = path.relative_to(TRAINING_DIR).as_posix()
                print(f"  [training] {relative_name} L{lineno}: {line.strip()[:MAX_LINE]}")
                hits += 1
                if hits >= args.max_total:
                    return hits
    return hits


def main():
    ap = argparse.ArgumentParser(description="Search Sentaurus official manuals (local text index)")
    ap.add_argument("query", help="search text (case-insensitive) or regex with -r")
    ap.add_argument("-t", "--tool", help="only files containing this in name, e.g. sdevice, swb")
    ap.add_argument("-n", "--max-total", type=int, default=30, help="max hits total (default 30)")
    ap.add_argument("-r", "--regex", action="store_true", help="treat query as regex")
    ap.add_argument("--training", action="store_true", help="also search Sentaurus_Training HTML")
    ap.add_argument("-c", "--context", type=int, default=0, help="unused, reserved")
    args = ap.parse_args()

    flags = 0 if args.regex else re.IGNORECASE
    pattern = re.compile(args.query, flags)

    if not TEXT_DIR.is_dir():
        sys.exit(
            f"text index not found: {TEXT_DIR}\n"
            f"请先在本机运行: bash {SCRIPT_DIR / 'build_index.sh'}"
        )
    if args.training and not TRAINING_DIR.is_dir():
        sys.exit(
            f"training directory not found: {TRAINING_DIR}\n"
            "请设置 SENTAURUS_TRAINING_DIR 指向本地教程目录"
        )
    hits = search_texts(args, pattern)
    if args.training:
        hits += search_training(args, pattern)
    print(f"\n共 {hits} 条命中。文本库: {TEXT_DIR}")
    if hits == 0:
        print("建议: 换关键词、拆词、或用 -t 指定手册后再试。")


if __name__ == "__main__":
    main()

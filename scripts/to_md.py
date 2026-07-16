#!/usr/bin/env python3
"""Merge docs/ and exercises/ into two single files with TOC anchors.

Usage:
    python3 to_md.py /abs/path/to/<topic> <topic> [book title] [--lang en|zh]

Language defaults to "language" in <skill root>/config.json (falls back
to en). Output file names and headings follow the chosen language.

Examples:
    python3 to_md.py ~/Study/Docker Docker
    python3 to_md.py ~/Study/Linux Linux "Linux Server Ops: The Complete Tutorial"
    python3 to_md.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh
"""
import glob
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config.json")

# Per-language file names, titles and UI strings ({topic} is substituted).
STRINGS = {
    "en": {
        "html_lang": "en",
        "toc": "Contents",
        "top_link": "↑ Back to contents",
        "tutorial_file": "{topic}-tutorial",
        "exercises_file": "{topic}-exercises",
        "tutorial_title": "{topic} Complete Tutorial",
        "exercises_title": "{topic} Exercises",
    },
    "zh": {
        "html_lang": "zh-CN",
        "toc": "目录",
        "top_link": "↑ 返回目录",
        "tutorial_file": "{topic}完整教程",
        "exercises_file": "{topic}练习完整版",
        "tutorial_title": "{topic} 完整教程",
        "exercises_title": "{topic} 练习完整版",
    },
}


def default_lang():
    """Read the default language from config.json; fall back to en."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            lang = json.load(f).get("language", "en")
        return lang if lang in STRINGS else "en"
    except (OSError, ValueError):
        return "en"


def cli(argv, usage):
    """Parse the shared CLI: BASE TOPIC [TITLE] [--lang en|zh]."""
    args = list(argv)
    lang = None
    if "--lang" in args:
        i = args.index("--lang")
        if i + 1 >= len(args):
            sys.exit("error: --lang requires an argument (en|zh)")
        lang = args[i + 1]
        del args[i:i + 2]
    if lang is None:
        lang = default_lang()
    if lang not in STRINGS:
        sys.exit(f"error: unsupported language {lang!r} (supported: {', '.join(STRINGS)})")
    if len(args) < 2:
        sys.exit(usage)
    base = os.path.abspath(os.path.expanduser(args[0]))
    topic = args[1]
    title = args[2] if len(args) > 2 else None
    return base, topic, title, lang


def exercise_label(title, lang):
    """Drop the 'Exercises' wording so TOC entries line up with the tutorial's."""
    if lang == "zh":
        return title.replace("练习：", "：").replace("练习", "")
    return title.replace(" Exercises: ", ": ").replace(" Exercises", "")


def chapters(folder):
    """Read chapters ordered by leading number; return [(index, first-line title, text)]."""
    files = sorted(
        glob.glob(os.path.join(folder, "*.md")),
        key=lambda p: int(re.match(r"(\d+)", os.path.basename(p)).group(1)),
    )
    result = []
    for i, path in enumerate(files, 1):
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        title = text.splitlines()[0].lstrip("#").strip()
        result.append((i, title, text))
    return result


def build(folder, out_path, book_title, label, s):
    chs = chapters(folder)
    if not chs:
        sys.exit(f"error: no chapter files found in {folder}")
    toc = "\n".join(f"- [{label(t)}](#ch{i:02d})" for i, t, _ in chs)
    body = "\n\n---\n\n".join(
        f'<a id="ch{i:02d}"></a>\n\n{text}' for i, _, text in chs
    )
    content = f"# {book_title}\n\n## {s['toc']}\n\n{toc}\n\n---\n\n{body}\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {out_path} with {len(chs)} chapters")


def main():
    base, topic, title, lang = cli(sys.argv[1:], __doc__)
    s = STRINGS[lang]
    build(
        os.path.join(base, "docs"),
        os.path.join(base, s["tutorial_file"].format(topic=topic) + ".md"),
        title or s["tutorial_title"].format(topic=topic),
        lambda t: t,
        s,
    )
    build(
        os.path.join(base, "exercises"),
        os.path.join(base, s["exercises_file"].format(topic=topic) + ".md"),
        s["exercises_title"].format(topic=topic),
        lambda t: exercise_label(t, lang),
        s,
    )


if __name__ == "__main__":
    main()

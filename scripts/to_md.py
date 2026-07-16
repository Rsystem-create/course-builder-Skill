#!/usr/bin/env python3
"""Merge docs/ and exercises/ into the final Markdown deliverable(s).

Two organizations:
    integrated  one tutor book: ch1, its exercises, ch2, its exercises, ... (default)
    separated   two files: full tutorial + full exercise book

Usage:
    python3 to_md.py /abs/path/to/<topic> <topic> [book title]
                     [--lang en|zh] [--mode integrated|separated]

--lang / --mode default to "language" / "organization" in
<skill root>/config.json (falling back to en / integrated when unset).
Output file names and headings follow the chosen language.

Examples:
    python3 to_md.py ~/Study/Docker Docker
    python3 to_md.py ~/Study/Docker Docker --mode separated
    python3 to_md.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh
"""
import glob
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config.json")

MODES = ("integrated", "separated")

# Per-language file names, titles and UI strings ({topic} is substituted).
STRINGS = {
    "en": {
        "html_lang": "en",
        "toc": "Contents",
        "top_link": "↑ Back to contents",
        "ex_link": "Exercises",
        "book_file": "{topic}-book",
        "book_title": "{topic} Tutorial",
        "tutorial_file": "{topic}-tutorial",
        "exercises_file": "{topic}-exercises",
        "tutorial_title": "{topic} Complete Tutorial",
        "exercises_title": "{topic} Exercises",
    },
    "zh": {
        "html_lang": "zh-CN",
        "toc": "目录",
        "top_link": "↑ 返回目录",
        "ex_link": "练习",
        "book_file": "{topic}教程",
        "book_title": "{topic} 教程",
        "tutorial_file": "{topic}完整教程",
        "exercises_file": "{topic}练习完整版",
        "tutorial_title": "{topic} 完整教程",
        "exercises_title": "{topic} 练习完整版",
    },
}


def _config():
    """Read config.json; missing/broken file just means no preferences."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def default_lang():
    lang = _config().get("language")
    return lang if lang in STRINGS else "en"


def default_mode():
    mode = _config().get("organization")
    return mode if mode in MODES else "integrated"


def cli(argv, usage):
    """Parse the shared CLI: BASE TOPIC [TITLE] [--lang ...] [--mode ...]."""
    args = list(argv)

    def option(flag, allowed, default):
        if flag not in args:
            value = default()
        else:
            i = args.index(flag)
            if i + 1 >= len(args):
                sys.exit(f"error: {flag} requires an argument ({'|'.join(allowed)})")
            value = args[i + 1]
            del args[i:i + 2]
        if value not in allowed:
            sys.exit(f"error: unsupported {flag.lstrip('-')} {value!r} "
                     f"(supported: {', '.join(allowed)})")
        return value

    lang = option("--lang", tuple(STRINGS), default_lang)
    mode = option("--mode", MODES, default_mode)
    if len(args) < 2:
        sys.exit(usage)
    base = os.path.abspath(os.path.expanduser(args[0]))
    topic = args[1]
    title = args[2] if len(args) > 2 else None
    return base, topic, title, lang, mode


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


def paired(base):
    """Docs and exercises chapters, checked to line up one-to-one."""
    docs = chapters(os.path.join(base, "docs"))
    exs = chapters(os.path.join(base, "exercises"))
    if not docs:
        sys.exit(f"error: no chapter files found in {os.path.join(base, 'docs')}")
    if len(docs) != len(exs):
        sys.exit(f"error: {len(docs)} docs chapters but {len(exs)} exercise chapters")
    return docs, exs


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


def build_book(base, out_path, book_title, s):
    """Integrated tutor book: each chapter immediately followed by its exercises."""
    docs, exs = paired(base)
    toc = "\n".join(
        f"- [{t}](#ch{i:02d}) · [{s['ex_link']}](#ex{i:02d})" for i, t, _ in docs
    )
    body = "\n\n---\n\n".join(
        f'<a id="ch{i:02d}"></a>\n\n{doc}\n\n<a id="ex{i:02d}"></a>\n\n{ex}'
        for (i, _, doc), (_, _, ex) in zip(docs, exs)
    )
    content = f"# {book_title}\n\n## {s['toc']}\n\n{toc}\n\n---\n\n{body}\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {out_path} with {len(docs)} chapters + exercises")


def main():
    base, topic, title, lang, mode = cli(sys.argv[1:], __doc__)
    s = STRINGS[lang]
    if mode == "integrated":
        build_book(
            base,
            os.path.join(base, s["book_file"].format(topic=topic) + ".md"),
            title or s["book_title"].format(topic=topic),
            s,
        )
        return
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

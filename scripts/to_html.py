#!/usr/bin/env python3
"""Render docs/ and exercises/ as the final HTML deliverable(s) (external style.css).

Two organizations:
    integrated  one tutor-book HTML: ch1, its exercises, ch2, ... (default)
    separated   two HTML files: full tutorial + full exercise book

Usage:
    python3 to_html.py /abs/path/to/<topic> <topic> [book title]
                       [--lang en|zh] [--mode integrated|separated]

Writes the HTML file(s) and copies style.css from this directory into
<topic>/; the HTML references it via <link>. --lang / --mode default to
config.json ("language" / "organization"). Standard library only;
Markdown coverage matches this skill's chapter format contract.

Examples:
    python3 to_html.py ~/Study/Docker Docker
    python3 to_html.py ~/Study/Docker Docker --mode separated
    python3 to_html.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh
"""
import html
import os
import re
import shutil
import sys

from to_md import STRINGS, chapters, cli, exercise_label, paired

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_NAME = "style.css"


def _inline(text):
    """转换行内元素：先转义，再依次处理行内代码、加粗、斜体、图片、链接。"""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def _parse_list(lines, i, out):
    """解析（可能嵌套的）列表，返回消费到的下一行下标。"""
    n = len(lines)
    stack = []  # [(indent, tag)]
    while i < n:
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)", lines[i])
        if not m:
            break
        indent = len(m.group(1))
        tag = "ol" if m.group(2)[0].isdigit() else "ul"
        if not stack or indent > stack[-1][0]:
            stack.append((indent, tag))
            out.append(f"<{tag}>")
        elif indent < stack[-1][0]:
            while len(stack) > 1 and indent < stack[-1][0]:
                out.append(f"</{stack.pop()[1]}>")
        out.append(f"<li>{_inline(m.group(3))}</li>")
        i += 1
    while stack:
        out.append(f"</{stack.pop()[1]}>")
    return i


def md_to_html(md):
    """把本技能约束格式的 Markdown 章节转成 HTML 片段。"""
    out = []
    lines = md.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 空行
        if not stripped:
            i += 1
            continue

        # 围栏代码块
        m = re.match(r"^```(\S*)", stripped)
        if m:
            lang = m.group(1)
            block = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # 跳过闭合围栏
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(block))}\n</code></pre>")
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # 分隔线
        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # 引用块
        if stripped.startswith(">"):
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote><p>{_inline(' '.join(quote))}</p></blockquote>")
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [_inline(c.strip()) for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([_inline(c.strip()) for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{c}</th>" for c in header)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows
            )
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue

        # 列表（支持用缩进表达的嵌套）
        if re.match(r"^(\s*)([-*+]|\d+\.)\s+", line):
            i = _parse_list(lines, i, out)
            continue

        # 普通段落：聚合到下一个空行或块级元素
        para = [stripped]
        i += 1
        while i < n:
            nxt = lines[i]
            ns = nxt.strip()
            if (not ns or ns.startswith(("#", ">", "```", "|"))
                    or re.match(r"^(\s*)([-*+]|\d+\.)\s+", nxt)
                    or re.match(r"^(-{3,}|\*{3,})$", ns)):
                break
            para.append(ns)
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")

    return "\n".join(out)


def _document(book_title, toc, sections, s):
    """完整 HTML 页面骨架：标题 + 目录卡片 + 各章节。"""
    return (
        f'<!DOCTYPE html>\n<html lang="{s["html_lang"]}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(book_title)}</title>\n"
        f'<link rel="stylesheet" href="{CSS_NAME}">\n</head>\n<body>\n<main>\n'
        f'<h1 id="top">{html.escape(book_title)}</h1>\n'
        f'<nav class="toc">\n<h2>{s["toc"]}</h2>\n<ol>\n{toc}\n</ol>\n</nav>\n<hr>\n'
        f"{sections}\n</main>\n</body>\n</html>\n"
    )


def build_html(folder, out_path, book_title, label, s):
    chs = chapters(folder)
    if not chs:
        sys.exit(f"error: no chapter files found in {folder}")
    toc = "\n".join(
        f'<li><a href="#ch{i:02d}">{html.escape(label(t))}</a></li>' for i, t, _ in chs
    )
    sections = "\n<hr>\n".join(
        f'<section id="ch{i:02d}">\n{md_to_html(text)}\n'
        f'<a class="top-link" href="#top">{s["top_link"]}</a>\n</section>'
        for i, _, text in chs
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(_document(book_title, toc, sections, s))
    print(f"wrote {out_path} with {len(chs)} chapters")


def build_book_html(base, out_path, book_title, s):
    """交错模式：每章正文后紧跟对应练习（含答案），合成一本教程全书。"""
    docs, exs = paired(base)
    toc = "\n".join(
        f'<li><a href="#ch{i:02d}">{html.escape(t)}</a> · '
        f'<a href="#ex{i:02d}">{s["ex_link"]}</a></li>'
        for i, t, _ in docs
    )
    sections = "\n<hr>\n".join(
        f'<section id="ch{i:02d}">\n{md_to_html(doc)}\n</section>\n'
        f'<section id="ex{i:02d}" class="exercises">\n{md_to_html(ex)}\n'
        f'<a class="top-link" href="#top">{s["top_link"]}</a>\n</section>'
        for (i, _, doc), (_, _, ex) in zip(docs, exs)
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(_document(book_title, toc, sections, s))
    print(f"wrote {out_path} with {len(docs)} chapters + exercises")


def main():
    base, topic, title, lang, mode = cli(sys.argv[1:], __doc__)
    s = STRINGS[lang]
    if mode == "integrated":
        build_book_html(
            base,
            os.path.join(base, s["book_file"].format(topic=topic) + ".html"),
            title or s["book_title"].format(topic=topic),
            s,
        )
    else:
        build_html(
            os.path.join(base, "docs"),
            os.path.join(base, s["tutorial_file"].format(topic=topic) + ".html"),
            title or s["tutorial_title"].format(topic=topic),
            lambda t: t,
            s,
        )
        build_html(
            os.path.join(base, "exercises"),
            os.path.join(base, s["exercises_file"].format(topic=topic) + ".html"),
            s["exercises_title"].format(topic=topic),
            lambda t: exercise_label(t, lang),
            s,
        )
    shutil.copy(os.path.join(SCRIPT_DIR, CSS_NAME), os.path.join(base, CSS_NAME))
    print(f"copied {CSS_NAME} -> {base}")


if __name__ == "__main__":
    main()

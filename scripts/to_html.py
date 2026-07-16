#!/usr/bin/env python3
"""Render docs/ and exercises/ as two HTML single files (external style.css).

Usage:
    python3 to_html.py /abs/path/to/<topic> <topic> [book title] [--lang en|zh]

Writes the two merged HTML files and copies style.css from this
directory into <topic>/; the HTML references it via <link>.
Language defaults to "language" in <skill root>/config.json.
Standard library only; Markdown coverage matches this skill's
chapter format contract.

Examples:
    python3 to_html.py ~/Study/Docker Docker
    python3 to_html.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh
"""
import html
import os
import re
import shutil
import sys

from merge import STRINGS, chapters, cli, exercise_label

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
    doc = (
        f'<!DOCTYPE html>\n<html lang="{s["html_lang"]}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(book_title)}</title>\n"
        f'<link rel="stylesheet" href="{CSS_NAME}">\n</head>\n<body>\n<main>\n'
        f'<h1 id="top">{html.escape(book_title)}</h1>\n'
        f'<nav class="toc">\n<h2>{s["toc"]}</h2>\n<ol>\n{toc}\n</ol>\n</nav>\n<hr>\n'
        f"{sections}\n</main>\n</body>\n</html>\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote {out_path} with {len(chs)} chapters")


def main():
    base, topic, title, lang = cli(sys.argv[1:], __doc__)
    s = STRINGS[lang]
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

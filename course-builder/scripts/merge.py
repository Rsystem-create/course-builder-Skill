#!/usr/bin/env python3
"""合并 docs/ 与 exercises/ 为两个带目录锚点的单文件。

用法:
    python3 merge.py /abs/path/to/<主题> <主题> [教程大标题]

例:
    python3 merge.py ~/Documents/Study/Dev/Java/Python Python
    python3 merge.py ~/Documents/Study/Dev/Java/Linux Linux "Linux 服务器运维完整教程"
"""
import glob
import os
import re
import sys


def chapters(folder):
    """按文件名开头的数字序号读入所有章节，返回 [(序号, 首行标题, 全文)]。"""
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


def build(folder, out_path, book_title, label):
    chs = chapters(folder)
    if not chs:
        sys.exit(f"错误: {folder} 下没有找到章节文件")
    toc = "\n".join(f"- [{label(t)}](#ch{i:02d})" for i, t, _ in chs)
    body = "\n\n---\n\n".join(
        f'<a id="ch{i:02d}"></a>\n\n{text}' for i, _, text in chs
    )
    content = f"# {book_title}\n\n## 目录\n\n{toc}\n\n---\n\n{body}\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {out_path} with {len(chs)} chapters")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    base = os.path.abspath(os.path.expanduser(sys.argv[1]))
    topic = sys.argv[2]
    doc_title = sys.argv[3] if len(sys.argv) > 3 else f"{topic} 完整教程"

    build(
        os.path.join(base, "docs"),
        os.path.join(base, f"{topic}完整教程.md"),
        doc_title,
        lambda t: t,
    )
    build(
        os.path.join(base, "exercises"),
        os.path.join(base, f"{topic}练习完整版.md"),
        f"{topic} 练习完整版",
        # 目录里去掉「练习」字样，让条目和教程目录对得上
        lambda t: t.replace("练习：", "：").replace("练习", ""),
    )


if __name__ == "__main__":
    main()

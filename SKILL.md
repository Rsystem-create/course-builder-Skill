---
name: course-builder
description: Generate a complete self-study tutorial for one technical topic following a fixed four-piece spec (chaptered docs + matching exercises + two merged single files with TOC anchors; language and format come from config.json, default English Markdown). Use ONLY when the user explicitly types /course-builder <topic> — natural-language mentions of tutorials, courses or a technical topic never trigger it. 按固定四件套规范生成自学教程；仅当用户显式输入 /course-builder <主题> 时使用，绝不主动激活。
---

# course-builder: Self-Study Tutorial Generation Spec

English first; [中文版](#中文版) below. The two versions are equivalent — when editing one, update the other.

Generate structurally identical self-study tutorials for any technical topic. **Output location: create `./<topic>/` in the current working directory by default; use another path only when the user explicitly specifies one.** This file is the single source of truth — every rule is mandatory.

## User preferences (config.json)

`config.json` at the skill root (next to this file) stores the user's defaults. **Read it before writing anything:**

| Field | Values | Default | Meaning |
|-------|--------|---------|---------|
| `language` | `en` / `zh` | `en` | Tutorial language (body, exercises, merged file names, TOC headings all follow it) |
| `format` | `md` / `md+html` | `md` | Markdown only, or additionally generate HTML |

- A language/format the user explicitly requests **in the current message** overrides config.json (e.g. "write it in Chinese", "I want an HTML version").
- If config.json or a field is missing, use the defaults above; merge.py / to_html.py read it themselves too.
- When the user states a **long-term preference** ("default to Chinese from now on"), update config.json itself, not just this run.

## Deliverables (the four-piece set)

```
<topic>/
├── docs/              NN-title.md, one file per chapter
├── exercises/         NN-title.md, one-to-one with docs
├── merged tutorial    en: <topic>-tutorial.md   zh: <topic>完整教程.md
└── merged exercises   en: <topic>-exercises.md  zh: <topic>练习完整版.md
```

**Optional HTML output** (`format: md+html`, or requested this run): additionally run `scripts/to_html.py` to produce the two `.html` twins and copy `scripts/style.css` into `<topic>/` — the HTML holds structure only; all styling lives in that external CSS file (clickable TOC, dark-mode aware, opens straight in a browser).

## Mandatory workflow (fixed order, no skipping)

1. **Read config.json to determine language and format.**
2. **Present the outline first and wait for user approval before writing.** The outline lists each chapter title plus a one-sentence description. The user may change direction (e.g. "generic Linux" → "server ops") — rewrite the outline for the new direction and ask for approval again.
3. Write `docs/01..NN` (save each chapter as soon as it's done; don't batch).
4. Write `exercises/01..NN` (same numbers and topic words as docs).
5. Generate the two merged files with `scripts/merge.py`; also run `to_html.py` if the format calls for it.
6. Verify (below), then report: file tree + chapter table + how the style rules were honored.

## Outline rules

- **Chapter count is not fixed** — it follows the topic's size (usually 8–15; simple topics can be fewer). Whatever the user approves becomes the reference for all later checks.
- Arrange every tutorial along a narrative arc: fundamentals → core data/concepts → what makes this technology unique → engineering practice → **the final chapter is always a hands-on project tying the whole book together**.
- Aim the direction at the user's actual goals (practical, goal-driven), not an encyclopedia.

## docs chapter format contract

- File name: `NN-title.md` (two-digit NN). zh titles in Chinese, full-width colon allowed (e.g. `12-实战：命令行待办工具.md`); en titles in lowercase-kebab English (e.g. `12-project-cli-todo-app.md`).
- Chapter structure (the two languages correspond item by item):
  1. Chapter heading — zh: `# 第N章：标题` (N in Chinese numerals: 第一章、第十二章); en: `# Chapter N: Title`
  2. `>` one-sentence chapter intro
  3. Opening paragraph (analogy, motivation)
  4. Body sections separated by `---`
  5. Recap — zh: `## 小结`; en: `## Summary` — bullet recap
  6. One closing line pointing to the next chapter (final chapter: a closing line for the whole book)
- Proactively flag **common pitfalls** in the body (e.g. ufw: allow 22 before enable; Python mutable default args; `w` mode truncates the file).

## exercises chapter format contract

- File names match docs exactly (same number, same topic words).
- Structure (the two languages correspond item by item):
  1. Title — zh: `# 第N章练习：标题`; en: `# Chapter N Exercises: Title`
  2. Link back to the corresponding docs chapter
  3. Tip line — zh: 「建议先合上教程，独立完成后再对照末尾参考答案。」; en: "Try these with the tutorial closed, then check your work against the solutions at the end."
  4. Concept check — zh: `## 一、概念自测`; en: `## Part 1: Concept Check`
  5. Code reading — zh: `## 二、读码题`; en: `## Part 2: Code Reading` (rename per topic: CLI-ish → zh「读命令题」/ en "Command Reading"; theory-ish → zh「理解题」/ en "Comprehension")
  6. Programming — zh: `## 三、编程题`（或「动手题」）; en: `## Part 3: Programming Exercises` (or "Hands-on")
  7. Solutions — zh: `## 参考答案`; en: `## Solutions` — **written out directly, never folded in `<details>`**, numbered to match every exercise.
- Exercise files live in `exercises/`, never mixed into `docs/`.

## Merge & verify

1. Run the bundled scripts with absolute paths (never rely on cwd; `--lang` omitted = scripts read config.json themselves):
   ```bash
   python3 <skill dir>/scripts/merge.py /abs/path/to/<topic> <topic> [book title] [--lang en|zh]
   ```
   The third argument is optional, for when the book title differs from the default (e.g. Linux titled "Linux 服务器运维完整教程").
2. When HTML is wanted, also run (same arguments):
   ```bash
   python3 <skill dir>/scripts/to_html.py /abs/path/to/<topic> <topic> [book title] [--lang en|zh]
   ```
3. Verify anchor count = approved chapter count (**must pass `-a`**, or grep treats CJK-containing md as binary; substitute the actual language's file names):
   ```bash
   grep -a -c '<a id="ch' <merged-tutorial>.md <merged-exercises>.md
   ```
   If HTML was generated, likewise:
   ```bash
   grep -a -c '<section id="ch' <merged-tutorial>.html <merged-exercises>.html
   ```
4. Eyeball the TOC of both merged files (zh `## 目录` / en `## Contents`): entry count, chapter names, anchors consecutive with no gaps.

## Style rules (all mandatory)

- **Language consistency**: body, code comments, exercises and solutions all in the chosen language. zh: give the English term on first occurrence, e.g. 「虚拟环境（virtual environment, venv）」; en: English throughout, no Chinese mixed in.
- **Beginner-friendly, never needlessly hard**; but where depth matters (core concepts, common mistakes) **never skimp** — prefer extra analogies and step-by-step walk-throughs.
- **Every tutorial is fully self-contained**: no references to or dependencies on other tutorials in the library. Soft nods are fine ("X does this differently"), but every concept must be explained in place.

## Known pitfalls (learned the hard way — avoid)

- Counting anchors with grep requires `-a`: md files containing CJK are treated as binary.
- Hard-code absolute paths when running scripts; the Bash tool's cwd persists across calls and relative paths have caused failures.
- Temp scripts go in the session scratchpad, never the user's project (this skill's merge.py / to_html.py are official scripts — the exception).
- Resuming an interrupted session: first check which files already exist, continue from the break point, never redo finished chapters.

---

<a id="中文版"></a>

# course-builder：自学教程生成规范（中文版）

为任意技术主题生成结构完全一致的自学教程。**输出位置：默认在当前工作目录下新建 `./<主题>/`；仅当用户明确指定其他路径时才用指定路径。** 本文件是唯一规范来源，所有条款必须严格遵守。

## 用户偏好（config.json）

技能根目录（本文件旁）的 `config.json` 保存用户默认偏好，**动笔前必须先读**：

| 字段 | 取值 | 默认 | 含义 |
|------|------|------|------|
| `language` | `en` / `zh` | `en` | 教程语言（正文、练习、合并文件名、目录标题全部随之切换） |
| `format` | `md` / `md+html` | `md` | 只出 Markdown，或额外生成 HTML |

- 用户在**本次请求里**明确指定的语言/格式优先于 config.json（如「用中文写」「要 HTML 版」）。
- config.json 缺失或字段缺失时按上表默认值处理；merge.py / to_html.py 也会自己读它。
- 用户表达**长期偏好**（如「以后默认中文」）时，更新 config.json 本身，而不是只改本次。

## 产出物（四件套）

```
<主题>/
├── docs/            NN-标题.md，正文分章
├── exercises/       NN-标题.md，与 docs 一一对应的配套练习
├── 合并教程单文件    en: <主题>-tutorial.md   zh: <主题>完整教程.md
└── 合并练习单文件    en: <主题>-exercises.md  zh: <主题>练习完整版.md
```

**可选 HTML 输出**（`format: md+html` 或用户本次要求时）：另跑 `scripts/to_html.py`，额外生成两个同名 `.html`，并把 `scripts/style.css` 复制到 `<主题>/` 下——HTML 只含结构，全部样式在这个外链 CSS 文件里（可点击目录、深色模式自适配，双击即可在浏览器阅读）。

## 强制流程（顺序写死，不许跳步）

1. **读 config.json 确定语言和格式。**
2. **先给大纲，等用户批准才动笔。** 大纲列出每章标题和一句话内容说明。用户可能修改方向（例如把「通用 Linux」改成「服务器运维」）——按新方向重写大纲再次征求批准。
3. 写 `docs/01..NN`（每写完一章即保存，不攒批）。
4. 写 `exercises/01..NN`（文件名与 docs 同序号同主题词）。
5. 用 `scripts/merge.py` 生成两个合并单文件；按格式偏好决定是否再跑 `to_html.py`。
6. 验证（见下），然后向用户报告：文件树 + 章节表 + 风格规矩如何落实。

## 大纲规则

- **章数不固定**，由主题体量决定（一般 8~15 章，简单主题可更少）。用户批准的大纲有几章就是几章，后续所有校验以此为准。
- 每套教程按叙事弧线编排：基础 → 核心数据/概念 → 该技术的独特气质 → 工程化 → **末章必是串起全书的实战项目**。
- 主题方向要贴合用户实际目标（practical、goal-driven），不是百科全书式罗列。

## docs 章节格式契约

- 文件名：`NN-标题.md`（NN 两位数字）。zh 标题用中文，可含全角冒号（如 `12-实战：命令行待办工具.md`）；en 标题用小写连字符英文（如 `12-project-cli-todo-app.md`）。
- 章内结构（两种语言逐条对应）：
  1. 章标题一行 —— zh：`# 第N章：标题`（N 用汉字：第一章、第十二章）；en：`# Chapter N: Title`
  2. `>` 一句话本章导语
  3. 引入段落（类比、动机）
  4. 若干正文小节，小节间用 `---` 分隔
  5. 小结 —— zh：`## 小结`；en：`## Summary`，要点 bullet 回顾
  6. 结尾一句下一章指引（末章改为全书收尾语）
- 正文里主动标注**常见坑**（如 ufw 先 allow 22 再 enable、Python 可变默认参数、`w` 模式清空文件等）。

## exercises 章节格式契约

- 文件名与 docs 完全同序号同主题词。
- 结构（两种语言逐条对应）：
  1. 标题 —— zh：`# 第N章练习：标题`；en：`# Chapter N Exercises: Title`
  2. 链回对应 docs 章节
  3. 提示语 —— zh：「建议先合上教程，独立完成后再对照末尾参考答案。」；en："Try these with the tutorial closed, then check your work against the solutions at the end."
  4. 概念自测 —— zh：`## 一、概念自测`；en：`## Part 1: Concept Check`
  5. 读码题 —— zh：`## 二、读码题`；en：`## Part 2: Code Reading`（按主题换名：命令行类 zh「读命令题」/ en "Command Reading"，理论类 zh「理解题」/ en "Comprehension"）
  6. 编程题 —— zh：`## 三、编程题`（或「动手题」）；en：`## Part 3: Programming Exercises`（或 "Hands-on"）
  7. 参考答案 —— zh：`## 参考答案`；en：`## Solutions`。**直接写出，绝不折叠在 `<details>` 里**，按题号完整对应。
- 练习文件放 `exercises/` 目录，绝不混进 `docs/`。

## 合并与验证

1. 运行本技能自带脚本（脚本内用绝对路径，不依赖 cwd；`--lang` 缺省时脚本自己读 config.json）：
   ```bash
   python3 <本技能目录>/scripts/merge.py /abs/path/to/<主题> <主题> [教程大标题] [--lang en|zh]
   ```
   第三个参数可选，用于大标题与默认标题不同的情况（如 Linux 的大标题是「Linux 服务器运维完整教程」）。
2. 需要 HTML 时再跑（参数同 merge.py）：
   ```bash
   python3 <本技能目录>/scripts/to_html.py /abs/path/to/<主题> <主题> [教程大标题] [--lang en|zh]
   ```
3. 验证锚点数 = 大纲章数（**必须加 `-a`**，否则 grep 把含中文的 md 当二进制返回空；文件名代入实际语言的命名）：
   ```bash
   grep -a -c '<a id="ch' <合并教程单文件>.md <合并练习单文件>.md
   ```
   若生成了 HTML，同样验证：
   ```bash
   grep -a -c '<section id="ch' <合并教程单文件>.html <合并练习单文件>.html
   ```
4. 目视检查两个合并文件的目录（zh `## 目录` / en `## Contents`）：条目数、章名、锚点连续无跳号。

## 风格规矩（全部强制）

- **语言一致性**：正文、代码注释、练习、答案全部用选定语言。zh 时术语首次出现附英文原词，如「虚拟环境（virtual environment, venv）」；en 时通篇英文，不夹中文。
- **面向新手，不搞太难**；但该讲透的地方（核心概念、易错点）**绝不省笔墨**，宁可多写类比和分步推演。
- **每套教程完全自成体系**：不引用、不依赖库里其他教程。允许「软呼应」（如提一句别的技术怎么做），但概念必须就地讲清。

## 已知坑（历史踩过，必须规避）

- `grep` 数锚点必须 `-a`：含 CJK 的 md 会被当成二进制文件。
- 合并脚本里写死绝对路径；Bash 工具的 cwd 在多次调用间持续存在，靠相对路径曾出过错。
- 临时脚本放会话 scratchpad，不留在用户项目目录里（本技能的 merge.py / to_html.py 是正式脚本，例外）。
- 会话被打断后续写时，先确认哪些文件已存在，从断点继续，不重做已完成的章。

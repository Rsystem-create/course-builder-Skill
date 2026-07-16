---
name: course-builder
description: Generate a complete self-study tutorial for one technical topic (chaptered docs + matching exercises with full solutions, delivered as one integrated tutor book or separated tutorial/exercise files, Markdown or HTML, with or without source folders; each option resolves as explicit request > config.json preference > fixed default). Use ONLY when the user explicitly types /course-builder <topic> — natural-language mentions of tutorials, courses or a technical topic never trigger it. 按固定规范生成自学教程；仅当用户显式输入 /course-builder <主题> 时使用，绝不主动激活。
---

# course-builder: Self-Study Tutorial Generation Spec

English first; [中文版](#中文版) below. The two versions are equivalent — when editing one, update the other.

Generate structurally identical self-study tutorials for any technical topic. **Output location: create `./<topic>/` in the current working directory by default; use another path only when the user explicitly specifies one.** This file is the single source of truth — every rule is mandatory.

## Output options & resolution order

Every run is shaped by four options. Resolve each one top-down — **the first source that yields a value wins**:

| Option | Values | Resolution order |
|--------|--------|------------------|
| `language` | `en` / `zh` | explicit in this request → config.json → the language the user is currently communicating in |
| `format` | `md` / `html` | explicit → config.json → `md` |
| `folder` | `yes` / `no` | explicit → config.json → `no` |
| `organization` | `integrated` / `separated` | explicit → config.json → `integrated` |

- **`organization: integrated`** — one single book: chapter 1, its exercises, chapter 2, its exercises, … (file: en `<topic>-book`, zh `<主题>教程`).
- **`organization: separated`** — two files: the full tutorial and the full exercise book (en `<topic>-tutorial` + `<topic>-exercises`, zh `<主题>完整教程` + `<主题>练习完整版`).
- **`folder: yes`** — keep the per-chapter sources `docs/` and `exercises/` next to the merged output; **`no`** — delete them after the merged output is verified, leaving only the final file(s).
- **Solutions are always included**, written out in full — never omitted, never folded away.

### Preferences (config.json)

`config.json` at the skill root stores long-term preferences for the same four fields; `null` means "no preference" (fall through to the next source in the table). **Write to it only when the user's wording signals a lasting preference** — e.g. "all the time", "in the future", "from now on", "prefer", "remember" (zh:「以后」「一直」「默认」「记住」). A one-off request ("make this one html") never touches the file.

```json
{ "language": null, "format": null, "folder": null, "organization": null }
```

## Deliverables

Everything goes into `./<topic>/`. What remains there depends on the options:

| organization | format | final files in `<topic>/` |
|--------------|--------|---------------------------|
| integrated | md | `<topic>-book.md` (zh: `<主题>教程.md`) |
| integrated | html | `<topic>-book.html` + `style.css` (zh: `<主题>教程.html`) |
| separated | md | `<topic>-tutorial.md` + `<topic>-exercises.md` (zh: `完整教程` / `练习完整版`) |
| separated | html | the two `.html` twins + `style.css` |

`folder: yes` additionally keeps `docs/` and `exercises/` (chapter sources, `NN-title.md`, one-to-one). The HTML holds structure only; all styling lives in the external `style.css` (clickable TOC, dark-mode aware, exercise sections visually set off in integrated mode).

## Mandatory workflow (fixed order, no skipping)

1. **Resolve the four options** using the table above; if the request states a lasting preference, update config.json first.
2. **Present the confirmation form and wait for explicit approval. Nothing is written before the user says OK.** Exact shape — options as a bulleted list, outline as a table:

   ```
   **<Book title>**
   - language: en|zh
   - format: md|html
   - folder: yes|no
   - organization: integrated|separated

   outline:

   | # | Chapter | Description |
   |---|---------|-------------|
   | 1 | <Chapter title> | <one-sentence description> |
   | 2 | … | … |

   [confirm/reject/modify]
   ```

   Emit the form as **top-level plain markdown** — never inside a blockquote, code fence, or indentation — so the outline renders as a **real table**, not raw `|` pipes. The form ends with the literal line `[confirm/reject/modify]` — written plain text, **no pop-up question tool**, no closing sentences, no explanations. The form is the whole message; the user replies with their choice (and what to change, for modify).

   The book title must be **serious and factual — never boastful**: no "Master", "Ultimate", "Complete Guide", 「从入门到精通」「速成」 or similar hype. Default is simply "\<Topic\> Tutorial" / 「\<主题\> 教程」.

   **This form is the final gate. Whenever anything in it changes — a single option, one chapter title, any tiny adjustment — re-present the whole form and get approval again before taking any action.** No exceptions.
3. Write the chapter sources into `docs/` and `exercises/` (same numbers and topic words; save each file as soon as it's done, don't batch). **Writing order follows the organization:**
   - `integrated`: chapter by chapter in reading order — `docs/01`, then `exercises/01`, then `docs/02`, then `exercises/02`, … so each exercise is written while its chapter is fresh.
   - `separated`: all of `docs/01..NN` first, then all of `exercises/01..NN`.
4. Run the matching script: `scripts/to_md.py` for `format: md`, `scripts/to_html.py` for `format: html` — always passing `--lang` and `--mode` explicitly.
5. Verify (below). If `folder: no`, delete `docs/` and `exercises/` **after** verification passes. Report: file tree + chapter table + how the style rules were honored.

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

1. Run the bundled script matching the format, with absolute paths (never rely on cwd) and explicit `--lang`/`--mode`:
   ```bash
   python3 <skill dir>/scripts/to_md.py   /abs/path/to/<topic> <topic> [book title] --lang en|zh --mode integrated|separated
   python3 <skill dir>/scripts/to_html.py /abs/path/to/<topic> <topic> [book title] --lang en|zh --mode integrated|separated
   ```
   The third argument is optional, for when the book title differs from the default (e.g. Linux titled "Linux 服务器运维完整教程"). `to_html.py` also copies `style.css` into `<topic>/`.
2. Verify anchor count = approved chapter count (**must pass `-a`**, or grep treats CJK-containing md as binary; substitute the actual language's file names):
   - integrated md — both must equal N:
     ```bash
     grep -a -c '<a id="ch' <book>.md
     grep -a -c '<a id="ex' <book>.md
     ```
   - separated md:
     ```bash
     grep -a -c '<a id="ch' <tutorial>.md <exercises>.md
     ```
   - html: same checks with `'<section id="ch'` / `'<section id="ex'` on the `.html` file(s).
3. Eyeball the TOC (zh `## 目录` / en `## Contents`): entry count, chapter names, anchors consecutive with no gaps; in integrated mode every entry carries both the chapter link and the exercises link.
4. Only after all checks pass: if `folder: no`, delete `docs/` and `exercises/`.

## Style rules (all mandatory)

- **Language consistency**: body, code comments, exercises and solutions all in the chosen language. zh: give the English term on first occurrence, e.g. 「虚拟环境（virtual environment, venv）」; en: English throughout, no Chinese mixed in.
- **Beginner-friendly, never needlessly hard**; but where depth matters (core concepts, common mistakes) **never skimp** — prefer extra analogies and step-by-step walk-throughs.
- **Every tutorial is fully self-contained**: no references to or dependencies on other tutorials in the library. Soft nods are fine ("X does this differently"), but every concept must be explained in place.

## Known pitfalls (learned the hard way — avoid)

- Counting anchors with grep requires `-a`: md files containing CJK are treated as binary.
- Hard-code absolute paths when running scripts; the Bash tool's cwd persists across calls and relative paths have caused failures.
- Temp scripts go in the session scratchpad, never the user's project (this skill's to_md.py / to_html.py are official scripts — the exception).
- Resuming an interrupted session: first check which files already exist, continue from the break point, never redo finished chapters.
- Never skip the confirmation form, even when the change since the last approved form seems trivial.

---

<a id="中文版"></a>

# course-builder：自学教程生成规范（中文版）

为任意技术主题生成结构完全一致的自学教程。**输出位置：默认在当前工作目录下新建 `./<主题>/`；仅当用户明确指定其他路径时才用指定路径。** 本文件是唯一规范来源，所有条款必须严格遵守。

## 输出选项与决策顺序

每次生成由四个选项决定。每个选项自上而下解析，**最先给出取值的来源生效**：

| 选项 | 取值 | 决策顺序 |
|------|------|----------|
| `language` | `en` / `zh` | 本次请求明确指定 → config.json → 用户当前交流所用语言 |
| `format` | `md` / `html` | 明确指定 → config.json → `md` |
| `folder` | `yes` / `no` | 明确指定 → config.json → `no` |
| `organization` | `integrated` / `separated` | 明确指定 → config.json → `integrated` |

- **`organization: integrated`**——单本教程：第1章正文、第1章练习、第2章正文、第2章练习……（文件名：en `<topic>-book`，zh `<主题>教程`）。
- **`organization: separated`**——两个文件：完整教程 + 完整练习册（en `<topic>-tutorial` + `<topic>-exercises`，zh `<主题>完整教程` + `<主题>练习完整版`）。
- **`folder: yes`**——保留按章源文件 `docs/` 和 `exercises/`；**`no`**——合并产物验证通过后删除这两个目录，只留最终文件。
- **参考答案永远包含**，完整写出——绝不省略、绝不折叠。

### 用户偏好（config.json）

技能根目录的 `config.json` 保存这四个字段的长期偏好；`null` 表示「无偏好」（继续走上表的下一级）。**仅当用户措辞表明是长期偏好时才写入**——如 "all the time"、"in the future"、"prefer"、"remember"（中文：「以后」「一直」「默认」「记住」）。一次性的要求（「这次要 html」）绝不写入文件。

```json
{ "language": null, "format": null, "folder": null, "organization": null }
```

## 产出物

全部输出进 `./<主题>/`，最终留下什么由选项决定：

| organization | format | `<主题>/` 里的最终文件 |
|--------------|--------|------------------------|
| integrated | md | `<主题>教程.md`（en：`<topic>-book.md`） |
| integrated | html | `<主题>教程.html` + `style.css` |
| separated | md | `<主题>完整教程.md` + `<主题>练习完整版.md` |
| separated | html | 两个同名 `.html` + `style.css` |

`folder: yes` 时额外保留 `docs/` 和 `exercises/`（按章源文件 `NN-标题.md`，一一对应）。HTML 只含结构，全部样式在外链 `style.css` 里（可点击目录、深色模式自适配，integrated 模式下练习区块有视觉区分）。

## 强制流程（顺序写死，不许跳步）

1. **按上表解析四个选项**；若本次请求表达了长期偏好，先更新 config.json。
2. **给出确认单，等用户明确批准。用户说 OK 之前不写任何文件。** 格式固定——选项用带点的列表，大纲用表格：

   ```
   **<教程大标题>**
   - language: en|zh
   - format: md|html
   - folder: yes|no
   - organization: integrated|separated

   outline:

   | # | 章标题 | 一句话说明 |
   |---|--------|------------|
   | 1 | <章标题> | <一句话说明> |
   | 2 | …… | …… |

   [confirm/reject/modify]
   ```

   确认单必须以**顶层普通 markdown** 输出——绝不放进引用块、代码块或缩进里——这样大纲才会渲染成**真正的表格**，而不是一堆裸 `|` 竖线。单子以字面一行 `[confirm/reject/modify]` 结尾——直接写在回复里，**不用弹出式提问工具**，不写收尾长句、不解释。单子就是整条消息；用户直接回复选择（modify 时附上要改什么）。

   大标题必须**严肃、如实，绝不夸口**：不用 "Master"、"Ultimate"、「从入门到精通」「速成」「终极指南」之类的营销词。默认就是「\<主题\> 教程」/ "\<Topic\> Tutorial"。

   **这张确认单是最后一道关口。单子上任何内容发生变化——哪怕只改一个选项、一个章名、再小的调整——都必须重新出示整张单子、再次获得批准后才能动手。** 没有例外。
3. 把按章源文件写进 `docs/` 和 `exercises/`（同序号同主题词；每写完一个文件即保存，不攒批）。**写作顺序跟随 organization：**
   - `integrated`：按阅读顺序逐章交错——`docs/01`、`exercises/01`、`docs/02`、`exercises/02`……趁每章内容还新鲜时就写它的练习。
   - `separated`：先写完全部 `docs/01..NN`，再写全部 `exercises/01..NN`。
4. 按 format 跑对应脚本：`md` 用 `scripts/to_md.py`，`html` 用 `scripts/to_html.py`——始终显式传 `--lang` 和 `--mode`。
6. 验证（见下）。`folder: no` 时**验证通过后**再删 `docs/` 和 `exercises/`。向用户报告：文件树 + 章节表 + 风格规矩如何落实。

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

1. 按 format 跑对应脚本（脚本内用绝对路径，不依赖 cwd；显式传 `--lang`/`--mode`）：
   ```bash
   python3 <本技能目录>/scripts/to_md.py   /abs/path/to/<主题> <主题> [教程大标题] --lang en|zh --mode integrated|separated
   python3 <本技能目录>/scripts/to_html.py /abs/path/to/<主题> <主题> [教程大标题] --lang en|zh --mode integrated|separated
   ```
   第三个参数可选，用于大标题与默认标题不同的情况（如 Linux 的大标题是「Linux 服务器运维完整教程」）。`to_html.py` 会顺带把 `style.css` 复制到 `<主题>/`。
2. 验证锚点数 = 大纲章数（**必须加 `-a`**，否则 grep 把含中文的 md 当二进制返回空；文件名代入实际语言的命名）：
   - integrated md——两个都必须等于章数 N：
     ```bash
     grep -a -c '<a id="ch' <教程>.md
     grep -a -c '<a id="ex' <教程>.md
     ```
   - separated md：
     ```bash
     grep -a -c '<a id="ch' <完整教程>.md <练习完整版>.md
     ```
   - html：同样的检查，把模式换成 `'<section id="ch'` / `'<section id="ex'`。
3. 目视检查目录（zh `## 目录` / en `## Contents`）：条目数、章名、锚点连续无跳号；integrated 模式下每条目录项都要同时有章链接和练习链接。
4. 全部检查通过后：`folder: no` 时才删 `docs/` 和 `exercises/`。

## 风格规矩（全部强制）

- **语言一致性**：正文、代码注释、练习、答案全部用选定语言。zh 时术语首次出现附英文原词，如「虚拟环境（virtual environment, venv）」；en 时通篇英文，不夹中文。
- **面向新手，不搞太难**；但该讲透的地方（核心概念、易错点）**绝不省笔墨**，宁可多写类比和分步推演。
- **每套教程完全自成体系**：不引用、不依赖库里其他教程。允许「软呼应」（如提一句别的技术怎么做），但概念必须就地讲清。

## 已知坑（历史踩过，必须规避）

- `grep` 数锚点必须 `-a`：含 CJK 的 md 会被当成二进制文件。
- 合并脚本里写死绝对路径；Bash 工具的 cwd 在多次调用间持续存在，靠相对路径曾出过错。
- 临时脚本放会话 scratchpad，不留在用户项目目录里（本技能的 to_md.py / to_html.py 是正式脚本，例外）。
- 会话被打断后续写时，先确认哪些文件已存在，从断点继续，不重做已完成的章。
- 确认单绝不能跳过——哪怕相比上次批准的单子只有极小的变化。

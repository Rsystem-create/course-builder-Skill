# course-builder

**English** | [中文](#中文版)

A [Claude Code](https://claude.com/claude-code) skill: generate structurally identical **self-study tutorials** for any technical topic — chaptered docs plus matching exercises with full solutions, delivered as one integrated "tutor book" or as separated tutorial/exercise files, in Markdown or HTML.

## Output options

Every run is shaped by four options; each resolves as **explicit request → `config.json` preference → default**:

| Option | Values | Default (when neither specified nor preferred) |
|--------|--------|------------------------------------------------|
| `language` | `en` / `zh` | the language you're currently talking in |
| `format` | `md` / `html` | `md` |
| `folder` | `yes` / `no` | `no` — only the final file(s), no source folders |
| `organization` | `integrated` / `separated` | `integrated` — ch1, ex1, ch2, ex2, … one tutor book |

What lands in `./<topic>/`:

| organization | format | final files |
|--------------|--------|-------------|
| integrated | md | `<topic>-book.md` |
| integrated | html | `<topic>-book.html` + `style.css` |
| separated | md | `<topic>-tutorial.md` + `<topic>-exercises.md` |
| separated | html | the two `.html` twins + `style.css` |

`folder: yes` additionally keeps the per-chapter sources `docs/` and `exercises/`. Solutions are always included, written out in full. The HTML holds structure only — all styling lives in the external `style.css` (clickable TOC, dark-mode aware).

## User preferences (config.json)

`config.json` at the skill root stores long-term preferences; `null` = no preference:

```json
{
  "language": null,
  "format": null,
  "folder": null,
  "organization": null
}
```

Preferences are updated when your wording signals persistence — "I want html **all the time**", "**from now on** use Chinese", "**remember** this" — while a one-off request ("make this one html") only affects the current run.

## Install

Copy (or symlink) this directory into Claude Code's skills directory:

```bash
# global (all projects)
cp -r course-builder ~/.claude/skills/

# or current project only
cp -r course-builder .claude/skills/
```

## Usage

In Claude Code, type:

```
/course-builder <topic>
```

e.g. `/course-builder Docker`. **Only this explicit command triggers generation** — mentioning tutorials or courses in natural language never activates the skill.

The workflow is fixed:

1. Claude resolves the four options (request → config.json → defaults).
2. It presents a **confirmation form** — title, the four options, and the chapter outline — and waits for your approval. This form is the final gate: any change, however small, means the form is shown again before anything is written.

   > **Docker Tutorial**
   > - language: en
   > - format: md
   > - folder: no
   > - organization: integrated
   >
   > outline:
   >
   > | # | Chapter | Description |
   > |---|---------|-------------|
   > | 1 | Chapter 1: … | … |
   >
   > [confirm/reject/modify]

   The form ends with the literal `[confirm/reject/modify]` line; you reply with your choice.
3. It writes the chapter sources — in reading order for `integrated` (`docs/01`, `exercises/01`, `docs/02`, …), or all docs then all exercises for `separated`.
4. It runs `scripts/to_md.py` (or `to_html.py` for HTML) and self-checks anchor counts.
5. If `folder: no`, the source folders are removed after verification; then it reports the file tree and chapter table.

## Running the scripts manually

```bash
python3 course-builder/scripts/to_md.py /abs/path/to/<topic> <topic> [book title] [--lang en|zh] [--mode integrated|separated]

# e.g. a separated Chinese build with a custom book title
python3 course-builder/scripts/to_md.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh --mode separated

# for the HTML version (same arguments; also copies style.css into the topic folder)
python3 course-builder/scripts/to_html.py ~/Study/Docker Docker
```

When `--lang` / `--mode` are omitted the scripts read `config.json` themselves (falling back to `en` / `integrated`). Python 3 standard library only. Both scripts expect `docs/` and `exercises/` under the topic folder.

## Style conventions (summary)

- Body, code comments and exercises all in the chosen language; Chinese tutorials give the English term on first occurrence.
- Beginner-friendly; core concepts and common mistakes are never skimped on.
- Every tutorial is fully self-contained, with no dependencies on other tutorials in your library.
- Chapter count follows the topic's size (usually 8–15); the final chapter is always a hands-on project tying the book together.

Full spec: [`SKILL.md`](SKILL.md).

---

<a id="中文版"></a>

# course-builder（中文版）

一个 [Claude Code](https://claude.com/claude-code) 技能（Skill）：为任意技术主题生成结构完全一致的**自学教程**——正文分章 + 配套练习（含完整参考答案），可合成一本「教程全书式」的单文件（正文与练习逐章交错），也可拆成教程/练习两个文件，支持 Markdown 或 HTML。

## 输出选项

每次生成由四个选项决定，每项按**本次明确指定 → `config.json` 偏好 → 默认值**解析：

| 选项 | 取值 | 默认（既没指定也没偏好时） |
|------|------|----------------------------|
| `language` | `en` / `zh` | 你当前交流所用的语言 |
| `format` | `md` / `html` | `md` |
| `folder` | `yes` / `no` | `no`——只留最终文件，不留源目录 |
| `organization` | `integrated` / `separated` | `integrated`——第1章、练1、第2章、练2……合成一本全书 |

`./<主题>/` 里最终留下什么：

| organization | format | 最终文件 |
|--------------|--------|----------|
| integrated | md | `<主题>教程.md` |
| integrated | html | `<主题>教程.html` + `style.css` |
| separated | md | `<主题>完整教程.md` + `<主题>练习完整版.md` |
| separated | html | 两个同名 `.html` + `style.css` |

`folder: yes` 时额外保留按章源文件 `docs/` 和 `exercises/`。参考答案永远完整写出。HTML 只含结构，全部样式在外链 `style.css` 里（可点击目录、深色模式自适配）。

## 用户偏好（config.json）

技能根目录的 `config.json` 保存长期偏好；`null` 表示无偏好：

```json
{
  "language": null,
  "format": null,
  "folder": null,
  "organization": null
}
```

只有措辞表明长期偏好时才会写入——「**以后**都用 html」「**一直**用中文」「**记住**这个设置」；一次性要求（「这次要 html」）只影响本次。

## 安装

将本目录复制（或软链）到 Claude Code 的技能目录：

```bash
# 全局安装（所有项目可用）
cp -r course-builder ~/.claude/skills/

# 或仅当前项目
cp -r course-builder .claude/skills/
```

## 使用

在 Claude Code 中输入：

```
/course-builder <主题>
```

例如 `/course-builder Docker`。**只有显式输入这条命令才会触发生成**；自然语言聊到教程/课程不会激活本技能。

流程是固定的：

1. Claude 解析四个选项（本次请求 → config.json → 默认值）。
2. 给出**确认单**——大标题、四个选项、章节大纲——等你批准。确认单是最后一道关口：单子上任何内容变化（再小也算）都会重新出示，批准后才动笔。

   > **Docker 教程**
   > - language: zh
   > - format: md
   > - folder: no
   > - organization: integrated
   >
   > outline:
   >
   > | # | 章标题 | 一句话说明 |
   > |---|--------|------------|
   > | 1 | 第一章：…… | …… |
   >
   > [confirm/reject/modify]

   确认单以字面一行 `[confirm/reject/modify]` 结尾；你直接回复你的选择即可。
3. 写按章源文件——`integrated` 按阅读顺序交错（`docs/01`、`exercises/01`、`docs/02`……），`separated` 则先写完全部 docs 再写全部 exercises。
4. 运行 `scripts/to_md.py`（HTML 则 `to_html.py`）并自检锚点数。
5. `folder: no` 时验证通过后删除源目录；最后报告文件树和章节表。

## 手动运行脚本

```bash
python3 course-builder/scripts/to_md.py /abs/path/to/<主题> <主题> [教程大标题] [--lang en|zh] [--mode integrated|separated]

# 例：分离模式的中文版，大标题自定义
python3 course-builder/scripts/to_md.py ~/Study/Linux Linux "Linux 服务器运维完整教程" --lang zh --mode separated

# 需要 HTML 版时另跑（参数同 to_md.py，会顺带复制 style.css 到主题目录）
python3 course-builder/scripts/to_html.py ~/Study/Docker Docker
```

`--lang` / `--mode` 缺省时脚本自动读 `config.json`（再缺省为 `en` / `integrated`）。仅依赖 Python 3 标准库。两个脚本都要求主题目录下有 `docs/` 和 `exercises/`。

## 风格约定（摘要）

- 正文、代码注释、练习全部用选定语言；中文教程里术语首次出现附英文原词。
- 面向新手，核心概念和易错点不省笔墨。
- 每套教程完全自成体系，不依赖库里其他教程。
- 章数由主题体量决定（一般 8~15 章），末章必是串起全书的实战项目。

完整规范见 [`SKILL.md`](SKILL.md)。

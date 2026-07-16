# course-builder

一个 [Claude Code](https://claude.com/claude-code) 技能（Skill）：按固定「四件套」规范，为任意技术主题生成结构完全一致的**中文自学教程**（正文分章 + 配套练习 + 两个带目录锚点的合并单文件）。

## 产出物

对每个主题，生成如下结构：

```
<主题>/
├── docs/                     NN-标题.md，正文分章
├── exercises/                NN-标题.md，与 docs 一一对应的配套练习
├── <主题>完整教程.md          docs 合并单文件（含目录 + 锚点）
└── <主题>练习完整版.md        exercises 合并单文件（含目录 + 锚点）
```

- **docs**：每章含导语、引入类比、正文小节、小结和下一章指引，主动标注常见坑。
- **exercises**：概念自测 + 读码题 + 编程题，参考答案直接写出、按题号完整对应。
- **合并单文件**：由 `scripts/merge.py` 自动生成，带 `## 目录` 和 `<a id="chNN">` 锚点，方便单文件通读或导出。

## 安装

将 `course-builder/` 目录复制（或软链）到 Claude Code 的技能目录：

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

例如 `/course-builder Docker`。也可以直接用自然语言请求「给我生成一套 XX 教程」。

流程是固定的：

1. Claude 先给出**大纲**（每章标题 + 一句话说明），等你批准后才动笔；你可以在这一步调整方向。
2. 逐章写 `docs/`，再逐章写 `exercises/`。
3. 运行 `scripts/merge.py` 生成两个合并单文件并自检锚点数。
4. 报告文件树和章节表。

## 手动运行合并脚本

```bash
python3 course-builder/scripts/merge.py /abs/path/to/<主题> <主题> [教程大标题]

# 例：大标题与文件夹名不同时传第三个参数
python3 course-builder/scripts/merge.py ~/Study/Linux Linux "Linux 服务器运维完整教程"
```

仅依赖 Python 3 标准库。

## 风格约定（摘要）

- 全中文写作，代码注释也用中文；术语首次出现附英文原词。
- 面向新手，核心概念和易错点不省笔墨。
- 每套教程完全自成体系，不依赖库里其他教程。
- 章数由主题体量决定（一般 8~15 章），末章必是串起全书的实战项目。

完整规范见 [`course-builder/SKILL.md`](course-builder/SKILL.md)。

# Stanford AI 公开课中文学习笔记

四门 Stanford 公开课（YouTube 上的 Stanford Online 频道）的中文学习笔记，三种形式：**带图网页版**、**手机尺寸的离线 PDF**、**Markdown 源文件**。

**网页版入口：<https://felisachow.github.io/stanford-ai-notes/>**

| 课程 | 内容 | 讲数 | 网页版 | PDF | 源文件 |
|---|---|---|---|---|---|
| CS329A | Self-Improving AI Agents（2025 秋 · Aakanksha Chowdhery、Azalia Mirhoseini） | 9 | [打开](https://felisachow.github.io/stanford-ai-notes/cs329a/) | [下载](docs/pdf/cs329a-notes.pdf) | [cs329a/](cs329a/) |
| CME295 | Transformers & Large Language Models（2025 秋 · Afshine Amidi、Shervine Amidi） | 9 | [打开](https://felisachow.github.io/stanford-ai-notes/cme295/) | [下载](docs/pdf/cme295-notes.pdf) | [cme295/](cme295/) |
| CS224R | Deep Reinforcement Learning（2025 春 · Chelsea Finn） | 19 | [打开](https://felisachow.github.io/stanford-ai-notes/cs224r/) | [下载](docs/pdf/cs224r-notes.pdf) | [cs224r/](cs224r/) |
| CS336 | Language Modeling from Scratch（2026 春 · Percy Liang、Tatsunori Hashimoto） | 18 | [打开](https://felisachow.github.io/stanford-ai-notes/cs336/) | [下载](docs/pdf/cs336-notes.pdf) | [cs336/](cs336/) |

建议阅读顺序：CME295（基础概念）→ CS329A（智能体）→ CS224R（强化学习）→ CS336（从零造模型）。

## 每讲的结构

一句话 → 时间轴 → 核心内容（自绘示意图、公式、短伪代码）→ 关键图表速查 → 提到的工作 → 术语对照 → 字幕勘误 → 带走的问题。

- 时间戳都是链接，直接跳到视频对应位置；图注里的「▶ 看原幻灯片」跳到老师讲那一页的时刻。
- 图是用 Mermaid 重新画的示意图，用来解释机制，不是课件截图。GitHub 会直接渲染 Markdown 里的 Mermaid 图和 `$$` 公式块。
- 「小注」是补充的课外事实或对口误的更正；「应为 / 应出自」表示根据内容推断、老师没有明说。
- 英文字幕多为自动生成，每讲末尾的「字幕勘误」列出会影响理解的识别错误。

## 说明

非官方个人笔记，根据公开课视频的字幕整理，用自己的话写；没有逐字稿、全文翻译和课件截图。视频与课件的版权归 Stanford 与各位讲者所有，学习请以原视频为准。

## 目录与重建

```
cs329a/ cme295/ cs224r/ cs336/   每门课的 README（总览）+ 每讲一个 Markdown，_site/ 里是生成网页的脚本
docs/                            GitHub Pages 站点：docs/index.html 首页，docs/<课程>/index.html 网页版，docs/pdf/ 离线 PDF
tools/build_pages.py             用各课的 _site/build.py 生成 docs/（需要 markdown-it-py）
tools/sync_from_desktop.py       从本机的笔记目录同步源文件（把 ```latex 围栏转成 $$ 块）
```

```bash
pip install markdown-it-py
python3 tools/build_pages.py
```

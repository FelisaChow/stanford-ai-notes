#!/usr/bin/env python3
"""Build the CS224R notes page: markdown notes -> one static HTML file for the Artifact."""
import html
import pathlib
import re
import sys

from markdown_it import MarkdownIt

SITE = pathlib.Path(__file__).resolve().parent
SRC = SITE.parent
OUT = SITE / "cs224r-notes.html"

# (file, rail number, rail title, duration)
PAGES = [
    ("README.md", "·", "总览与课程地图", ""),
    ("01-class-intro.md", "1", "课程介绍", "52:58"),
    ("02-imitation-learning.md", "2", "模仿学习", "1:07:05"),
    ("03-policy-gradients.md", "3", "策略梯度", "1:02:37"),
    ("04-actor-critic.md", "4", "Actor-Critic", "1:03:30"),
    ("05-off-policy-actor-critic.md", "5", "Off-Policy Actor-Critic", "1:09:21"),
    ("06-q-learning.md", "6", "Q-learning", "1:01:40"),
    ("06t-q-learning-review.md", "6+", "Q-learning 复习课", "50:39"),
    ("07-offline-rl.md", "7", "离线 RL", "1:07:50"),
    ("08-reward-learning.md", "8", "奖励学习", "1:05:58"),
    ("09-rl-for-llms.md", "9", "RL for LLMs：偏好优化", "1:02:51"),
    ("10-rl-for-llm-reasoning.md", "10", "RL for LLM 推理", "1:10:30"),
    ("11-model-based-rl.md", "11", "基于模型的 RL", "1:13:20"),
    ("12-multi-task-rl.md", "12", "多任务与目标条件 RL", "1:10:29"),
    ("13-meta-rl.md", "13", "元强化学习", "1:09:10"),
    ("14-exploration.md", "14", "探索", "1:12:42"),
    ("15-hierarchical-rl-il.md", "15", "分层 RL 与 IL", "1:09:32"),
    ("16-rl-for-robots.md", "16", "机器人 RL：自主学习", "1:05:44"),
    ("17-advancing-robot-intelligence.md", "17", "推进机器人智能（客座）", "49:48"),
    ("18-frontiers.md", "18", "前沿", "1:10:49"),
]

md = MarkdownIt("commonmark").enable("table")


def render_fence(self, tokens, idx, options, env):
    tok = tokens[idx]
    info = tok.info.strip().split()[0] if tok.info.strip() else ""
    if info == "mermaid":
        return '<pre class="mermaid">' + html.escape(tok.content, quote=False) + "</pre>\n"
    if info == "latex":
        return '<div class="math"><code>' + html.escape(tok.content.strip(), quote=False) + "</code></div>\n"
    return '<pre class="code"><code>' + html.escape(tok.content, quote=False) + "</code></pre>\n"


md.add_render_rule("fence", render_fence)

LINK_RE = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.S)
FIG_RE = re.compile(r'(<pre class="mermaid">.*?</pre>)\s*<p><em>(图.*?)</em></p>', re.S)
BARE_FIG_RE = re.compile(r'(?<!<div class="fig-scroll">)(<pre class="mermaid">.*?</pre>)', re.S)


def fix_link(m):
    href, text = m.group(1), m.group(2)
    attrs = ""
    if href.startswith("http"):
        attrs += ' target="_blank" rel="noopener"'
    if "youtube.com/watch" in href and "t=" in href:
        attrs += ' class="jump"' if text.strip().startswith("▶") else ' class="ts"'
    return f'<a href="{href}"{attrs}>{text}</a>'


DOLLAR_RE = re.compile(r"^\$\$\n(.*?)\n\$\$$", re.M | re.S)


def convert(text):
    text = DOLLAR_RE.sub(lambda m: "```latex\n" + m.group(1) + "\n```", text)
    out = md.render(text)
    out = FIG_RE.sub(
        r'<figure class="fig"><div class="fig-scroll">\1</div><figcaption>\2</figcaption></figure>', out
    )
    out = BARE_FIG_RE.sub(r'<figure class="fig"><div class="fig-scroll">\1</div></figure>', out)
    out = LINK_RE.sub(fix_link, out)
    out = out.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    out = out.replace("<p><strong>一句话</strong>", '<p class="lead"><strong>一句话</strong>')
    # first blockquote right after the h1 is the meta block; 小注 blockquotes are notes
    out = re.sub(r"(</h1>\s*)<blockquote>", r'\1<blockquote class="meta">', out, count=1)
    out = re.sub(r"<blockquote>(\s*<p>小注)", r'<blockquote class="note">\1', out)
    return out


def main():
    rail, lectures, problems = [], [], []
    present = [(i, p) for i, p in enumerate(PAGES) if (SRC / p[0]).exists()]
    for pos, (k, (fname, num, title, dur)) in enumerate(present):
        body = convert((SRC / fname).read_text(encoding="utf-8"))
        if "**" in re.sub(r"<pre.*?</pre>", "", body, flags=re.S):
            problems.append(f"{fname}: literal ** left in output (emphasis did not parse)")
        n_fig = body.count('<pre class="mermaid">')
        pager = []
        if pos > 0:
            pk, pp = present[pos - 1]
            pager.append(f'<a class="prev" href="#l{pk}">← {html.escape(pp[2])}</a>')
        if pos < len(present) - 1:
            nk, np_ = present[pos + 1]
            pager.append(f'<a class="next" href="#l{nk}">{html.escape(np_[2])} →</a>')
        lectures.append(
            f'<article class="lec off" id="l{k}" data-k="{k}">\n{body}\n<nav class="pager" aria-label="上一讲与下一讲">{"".join(pager)}</nav>\n</article>'
        )
        d = f'<span class="d">{dur}</span>' if dur else ""
        rail.append(
            f'      <li><a href="#l{k}" data-k="{k}"><span class="n">{html.escape(num)}</span><span class="t">{html.escape(title)}</span>{d}</a></li>'
        )
        print(f"{fname}: {len(body) // 1024} KB html, {n_fig} diagrams")
    missing = [p[0] for p in PAGES if not (SRC / p[0]).exists()]
    page = (SITE / "template.html").read_text(encoding="utf-8")
    page = page.replace("<!--RAIL-->", "\n".join(rail)).replace("<!--LECTURES-->", "\n".join(lectures))
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    if missing:
        print("missing:", ", ".join(missing))
    for p in problems:
        print("WARN", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())

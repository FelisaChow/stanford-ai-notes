#!/usr/bin/env python3
"""Build the CME295 notes page: markdown notes -> one static HTML file for the Artifact."""
import html
import pathlib
import re
import sys

from markdown_it import MarkdownIt

SITE = pathlib.Path(__file__).resolve().parent
SRC = SITE.parent
OUT = SITE / "cme295-notes.html"

# (file, rail number, rail title, duration)
PAGES = [
    ("README.md", "·", "总览与课程地图", ""),
    ("01-transformer.md", "1", "Transformer", ""),
    ("02-transformer-models-tricks.md", "2", "Transformer 系模型与技巧", ""),
    ("03-large-language-models.md", "3", "大语言模型", ""),
    ("04-llm-training.md", "4", "LLM 训练", ""),
    ("05-llm-tuning.md", "5", "LLM 微调", ""),
    ("06-llm-reasoning.md", "6", "LLM 推理", ""),
    ("07-agentic-llms.md", "7", "Agentic LLM", ""),
    ("08-llm-evaluation.md", "8", "LLM 评测", ""),
    ("09-recap-current-trends.md", "9", "回顾与趋势", ""),
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

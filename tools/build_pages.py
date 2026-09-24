#!/usr/bin/env python3
"""Build the GitHub Pages site under docs/: one page per course plus a landing page.

Each course's own _site/build.py renders its Markdown into a single HTML file; this
script points it at docs/<course>/index.html, adds a Mermaid renderer (the notes'
diagrams are Mermaid source), copies the PDFs, and writes docs/index.html.
Run: python3 tools/build_pages.py
"""
import html
import importlib.util
import pathlib
import re
import shutil
import subprocess

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
PDF_SRC = pathlib.Path.home() / "Desktop" / "cs-notes-pdf"
COURSES = [
    # dir, code, English title, PDF file on the Desktop
    ("cs329a", "CS329A", "Self-Improving AI Agents", "CS329A 学习笔记.pdf"),
    ("cme295", "CME295", "Transformers & Large Language Models", "CME295 学习笔记.pdf"),
    ("cs224r", "CS224R", "Deep Reinforcement Learning", "CS224R 学习笔记.pdf"),
    ("cs336", "CS336", "Language Modeling from Scratch", "CS336 学习笔记.pdf"),
]

MERMAID = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
(async function () {
  if (!window.mermaid) return;
  mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'loose', fontFamily: 'PingFang SC, Hiragino Sans GB, Noto Sans SC, sans-serif' });
  var nodes = Array.prototype.slice.call(document.querySelectorAll('pre.mermaid'));
  for (var i = 0; i < nodes.length; i++) {
    var pre = nodes[i];
    try {
      var r = await mermaid.render('mmd' + i, pre.textContent);
      var wrap = document.createElement('div'); wrap.innerHTML = r.svg;
      var el = wrap.firstElementChild; el.removeAttribute('height'); pre.replaceWith(el);
    } catch (e) { pre.classList.add('mermaid-error'); }
  }
})();
</script>
"""

HOME_LINK = '<div class="brand-home"><a href="../">← 全部课程</a></div>'
HOME_CSS = "<style>.brand-home{margin-top:.45rem;font-size:.8rem}.brand-home a{color:var(--muted)}</style>\n"

LANDING = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stanford AI 公开课中文学习笔记</title>
<meta name="description" content="Stanford CS329A、CME295、CS224R、CS336 四门公开课的中文学习笔记：自绘示意图、公式、时间戳跳转，网页版与手机 PDF。">
<style>
:root { --ground:#F4F7F5; --surface:#FFFFFF; --ink:#1B2521; --muted:#5A6A63; --rule:#D8E1DC; --accent:#1B6350; --accent-soft:#E1EFE9; --mark:#85590D; --mark-soft:#FAEFD8; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ground:#101613; --surface:#171F1B; --ink:#E2E9E5; --muted:#93A39B; --rule:#29342E; --accent:#7FC4AE; --accent-soft:#1E2E28; --mark:#E0B45C; --mark-soft:#332A14; } }
:root[data-theme="dark"] { --ground:#101613; --surface:#171F1B; --ink:#E2E9E5; --muted:#93A39B; --rule:#29342E; --accent:#7FC4AE; --accent-soft:#1E2E28; --mark:#E0B45C; --mark-soft:#332A14; }
* { box-sizing:border-box; }
body { margin:0; background:var(--ground); color:var(--ink); font-family:"IBM Plex Sans","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif; line-height:1.7; font-size:16px; }
.wrap { max-width:960px; margin:0 auto; padding:2.5rem 16px 4rem; }
h1 { font-size:1.9rem; line-height:1.25; margin:0 0 .6rem; }
.lead { color:var(--muted); margin:0 0 2rem; max-width:64ch; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px; }
.card { background:var(--surface); border:1px solid var(--rule); border-radius:10px; padding:1.1rem 1.2rem 1rem; display:flex; flex-direction:column; gap:.35rem; }
.code { font-size:.8rem; letter-spacing:.06em; color:var(--accent); font-weight:600; }
.card h2 { font-size:1.15rem; margin:0; line-height:1.35; }
.card .en { color:var(--muted); font-size:.9rem; }
.card .meta { color:var(--muted); font-size:.85rem; margin-top:.2rem; }
.links { display:flex; flex-wrap:wrap; gap:8px; margin-top:.7rem; }
.links a { display:inline-block; padding:.3rem .75rem; border-radius:999px; border:1px solid var(--rule); color:var(--ink); text-decoration:none; font-size:.88rem; }
.links a.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
.links a:hover { border-color:var(--accent); }
.note { margin-top:2.4rem; padding:1rem 1.2rem; background:var(--mark-soft); border-radius:8px; font-size:.92rem; }
.note p { margin:.3rem 0; }
footer { margin-top:2rem; color:var(--muted); font-size:.85rem; }
a { color:var(--accent); }
</style>
</head>
<body>
<div class="wrap">
  <h1>Stanford AI 公开课中文学习笔记</h1>
  <p class="lead">四门 Stanford 公开课（YouTube 上的 Stanford Online 频道）的中文笔记。每讲固定结构：一句话 → 时间轴 → 核心内容（自绘示意图、公式、短伪代码）→ 关键图表速查 → 提到的工作 → 术语对照 → 字幕勘误 → 带走的问题。时间戳都能点，直接跳到视频对应位置。</p>
  <div class="grid">
{cards}
  </div>
  <div class="note">
    <p><strong>非官方个人笔记。</strong>根据公开课视频的字幕整理，用自己的话写；图是重新画的示意图，不是课件截图；没有逐字稿和全文翻译。视频与课件的版权归 Stanford 与各位讲者所有，学习请以原视频为准。</p>
    <p>建议阅读顺序：CME295（基础概念）→ CS329A（智能体）→ CS224R（强化学习）→ CS336（从零造模型）。</p>
  </div>
  <footer>源文件（Markdown）与生成脚本在 <a href="https://github.com/FelisaChow/stanford-ai-notes">GitHub 仓库</a>。</footer>
</div>
</body>
</html>
"""

CARD = """    <div class="card">
      <div class="code">{code}</div>
      <h2>{title}</h2>
      <div class="en">{en}</div>
      <div class="meta">{sub}</div>
      <div class="meta">{n} 讲 · PDF {pages} 页 · {mb} MB</div>
      <div class="links">
        <a class="primary" href="{dir}/">网页版</a>
        <a href="pdf/{pdf}">手机 PDF</a>
        <a href="https://github.com/FelisaChow/stanford-ai-notes/tree/main/{dir}">Markdown</a>
        <a href="{playlist}">YouTube 播放列表</a>
      </div>
    </div>"""


def course_page(cdir):
    site = REPO / cdir / "_site"
    spec = importlib.util.spec_from_file_location(f"build_{cdir}", site / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out_dir = DOCS / cdir
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUT = out_dir / "index.html"
    mod.main()
    page = mod.OUT.read_text(encoding="utf-8")
    if not page.lstrip().lower().startswith("<!doctype"):
        page = "<!doctype html>\n<html lang=\"zh-CN\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" + HOME_CSS + page
    page = re.sub(r'(<div class="brand-sub">.*?</div>)', r"\1\n      " + HOME_LINK, page, count=1)
    page = page.replace("</body>", MERMAID + "</body>", 1) if "</body>" in page else page + MERMAID
    mod.OUT.write_text(page, encoding="utf-8")
    return page.count('<pre class="mermaid">')


def readme_meta(cdir):
    text = (REPO / cdir / "README.md").read_text(encoding="utf-8")
    m = re.search(r"^# (.+)$", text, re.M)
    title = m.group(1).strip() if m else cdir
    quote = re.search(r"^> (.+)$", text, re.M)
    sub = quote.group(1).strip() if quote else ""
    pl = re.search(r"\[播放列表\]\((https?://[^)]+)\)", text)
    playlist = pl.group(1) if pl else "https://www.youtube.com/@stanfordonline"
    n = len([p for p in (REPO / cdir).glob("[0-9][0-9]*-*.md")])
    return title, sub, playlist, n


def pdf_pages(path):
    try:
        return subprocess.run(["qpdf", "--show-npages", str(path)], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "?"


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    cards = []
    for cdir, code, en, pdf_name in COURSES:
        n_fig = course_page(cdir)
        title, sub, playlist, n = readme_meta(cdir)
        pdf_out = DOCS / "pdf" / f"{cdir}-notes.pdf"
        src = PDF_SRC / pdf_name
        if src.exists():
            shutil.copy(src, pdf_out)
        pages = pdf_pages(pdf_out) if pdf_out.exists() else "?"
        mb = f"{pdf_out.stat().st_size / 1e6:.1f}" if pdf_out.exists() else "?"
        cards.append(CARD.format(code=code, title=html.escape(title), en=html.escape(en), sub=html.escape(sub),
                                 n=n, pages=pages, mb=mb, dir=cdir, pdf=pdf_out.name, playlist=html.escape(playlist)))
        print(f"{cdir}: page built ({n} lectures, {n_fig} diagrams), pdf {pages} pages")
    (DOCS / "index.html").write_text(LANDING.replace("{cards}", "\n".join(cards)), encoding="utf-8")
    print("wrote docs/index.html")


if __name__ == "__main__":
    main()

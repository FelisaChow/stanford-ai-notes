#!/usr/bin/env python3
"""Copy the note sources from ~/Desktop/<course>-notes/ into this repo.

Formula blocks are converted from ```latex fences (what the build scripts expect)
to $$ … $$ blocks (what GitHub renders in Markdown); build.py understands both.
Run: python3 tools/sync_from_desktop.py
"""
import pathlib
import re
import shutil

REPO = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
COURSES = ["cs329a", "cme295", "cs224r", "cs336"]
FENCE_RE = re.compile(r"^```latex\n(.*?)\n```$", re.M | re.S)
PATCH_OLD = "def convert(text):\n    out = md.render(text)"
PATCH_NEW = (
    'DOLLAR_RE = re.compile(r"^\\$\\$\\n(.*?)\\n\\$\\$$", re.M | re.S)\n\n\n'
    "def convert(text):\n"
    '    text = DOLLAR_RE.sub(lambda m: "```latex\\n" + m.group(1) + "\\n```", text)\n'
    "    out = md.render(text)"
)


def main():
    for c in COURSES:
        src = HOME / "Desktop" / f"{c}-notes"
        dst = REPO / c
        dst.mkdir(exist_ok=True)
        n = 0
        for f in sorted(src.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            text, k = FENCE_RE.subn(lambda m: "$$\n" + m.group(1) + "\n$$", text)
            (dst / f.name).write_text(text, encoding="utf-8")
            n += 1
        site = dst / "_site"
        site.mkdir(exist_ok=True)
        shutil.copy(src / "_site" / "template.html", site / "template.html")
        build = (src / "_site" / "build.py").read_text(encoding="utf-8")
        if PATCH_OLD not in build and "DOLLAR_RE" not in build:
            raise SystemExit(f"{c}: build.py has an unexpected convert(); patch by hand")
        build = build.replace(PATCH_OLD, PATCH_NEW)
        (site / "build.py").write_text(build, encoding="utf-8")
        print(f"{c}: {n} markdown files, build.py patched for $$ blocks")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Repository-wide zero-dependency structural, local-link, and release guard checks."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
SKIP={".git","__pycache__"}
REQUIRED=[
 "README.md","AGENTS.md","demo/index.html","demo/README.md","demo/PRESENTER.md","demo/validate.py",
 "pitch/index.html","pitch/deck.md","pitch/styles.css","pitch/script.js","pitch/README.md","pitch/validate.py",
 "pitch/quiet-channel-evidence-deck.pptx","pitch/build_pptx.py","pitch/validate_pptx.py","pitch/pptx-build.json",
 "pitch/deck-4-slide.md","pitch/quiet-channel-4-slide-deck.pptx","pitch/build_4_slide_pptx.py","pitch/validate_4_slide_pptx.py","pitch/quiet-channel-4-slide-build.json","pitch/quiet-channel-4-slide-qa.md",
 "research/landscape.md","research/evidence-matrix.md","research/claim-boundary.md","research/claim-ledger.md",
 "research/references.md","research/presentation-review.md","research/scout-review.md",
 "provenance/source-record.md","provenance/decisions.md","provenance/media-catalogue.md"
]

class Links(HTMLParser):
 def __init__(self): super().__init__(); self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for key in ("href","src"):
   if key in a:self.refs.append(a[key])

def local_target(source:Path,ref:str):
 ref=unquote(ref.split("#",1)[0].split("?",1)[0])
 if not ref or ref.startswith(("http://","https://","mailto:","data:","javascript:")):return None
 return (source.parent/ref).resolve()

def main():
 errors=[]
 for name in REQUIRED:
  if not (ROOT/name).is_file():errors.append(f"missing required file: {name}")
 files=[p for p in ROOT.rglob("*") if p.is_file() and not any(part in SKIP for part in p.parts)]
 for p in files:
  rel=p.relative_to(ROOT)
  approved_documents={"pitch/quiet-channel-evidence-deck.pptx","pitch/quiet-channel-4-slide-deck.pptx"}
  if p.suffix.lower() in {".ppt",".pptx",".pdf",".doc",".docx"} and rel.as_posix() not in approved_documents: errors.append(f"unapproved/vendored binary document prohibited: {rel}")
  if p.stat().st_size>1_000_000:errors.append(f"unexpected file over 1 MB: {rel}")
  if "__pycache__" in p.parts or p.suffix==".pyc":errors.append(f"generated Python artifact: {rel}")
  if p.suffix.lower()==".md":
   text=p.read_text(errors="replace")
   for ref in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',text):
    target=local_target(p,ref.strip().split()[0])
    if target is not None and not target.exists():errors.append(f"broken Markdown link in {rel}: {ref}")
  if p.suffix.lower()==".html":
   parser=Links();parser.feed(p.read_text(errors="replace"))
   for ref in parser.refs:
    target=local_target(p,ref)
    if target is not None and not target.exists():errors.append(f"broken HTML ref in {rel}: {ref}")
 all_text="\n".join(p.read_text(errors="ignore") for p in files if p.suffix.lower() in {".md",".html",".js",".css",".py",".svg",".tsv"})
 for phrase in ("dcf87f08345a942d5cb84113d0e76a2cbb12050f335c5d54585c3b27143dff0b","AED 1,000,000","CONCEPT / SIMULATED","Browser-rendered"):
  if phrase.lower() not in all_text.lower():errors.append(f"release invariant missing: {phrase}")
 for secret in (r'AKIA[0-9A-Z]{16}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9_]{30,}',r'https?://i\.getmoshi\.app/[A-Za-z0-9_-]+'):
  if re.search(secret,all_text):errors.append(f"possible secret pattern: {secret}")
 svg_names={p.name for p in (ROOT/"pitch/assets").glob("*.svg")}
 catalogue=(ROOT/"provenance/media-catalogue.md").read_text()
 for name in svg_names:
  if name not in catalogue:errors.append(f"SVG absent from media catalogue: {name}")
 if errors:
  print("project validation failed:",*[f"- {e}" for e in errors],sep="\n");return 1
 print(f"project validation passed: {len(files)} files, local references, release boundaries, media catalogue, and secret guard")
 return 0
if __name__=="__main__":raise SystemExit(main())

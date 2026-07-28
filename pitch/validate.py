#!/usr/bin/env python3
"""Dependency-free structural and claim-boundary checks for the local deck.

This does not validate browser rendering, external-source truth, legal conclusions,
media permissions beyond the local catalogue, or technical performance.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
HTML=ROOT/"index.html"; MD=ROOT/"deck.md"; CSS=ROOT/"styles.css"; JS=ROOT/"script.js"; README=ROOT/"README.md"
PPTX=ROOT/"quiet-channel-evidence-deck.pptx"; PPTX_BUILDER=ROOT/"build_pptx.py"; PPTX_VALIDATOR=ROOT/"validate_pptx.py"; PPTX_EVIDENCE=ROOT/"pptx-build.json"
REFERENCES=ROOT.parent/"research"/"references.md"

class Parser(HTMLParser):
    VOID={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
    def __init__(self): super().__init__(); self.stack=[]; self.errors=[]; self.ids=set(); self.images=[]; self.scripts=[]; self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:self.errors.append(f"duplicate id {a['id']}")
            self.ids.add(a["id"])
        if tag=="img": self.images.append((a.get("src",""),a.get("alt")))
        if tag=="script" and a.get("src"): self.scripts.append(a["src"])
        if tag=="link" and a.get("href"): self.links.append(a["href"])
        if tag not in self.VOID:self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag in self.VOID:return
        if not self.stack:self.errors.append(f"unexpected </{tag}>");return
        expected=self.stack.pop()
        if expected!=tag:self.errors.append(f"expected </{expected}>, got </{tag}>")
    def close(self):
        super().close()
        if self.stack:self.errors.append("unclosed tags: "+", ".join(self.stack[-6:]))

def require(ok,msg,errors):
    if not ok: errors.append(msg)

def main():
    errors=[]
    for path in (HTML,MD,CSS,JS,README,PPTX,PPTX_BUILDER,PPTX_VALIDATOR,PPTX_EVIDENCE,REFERENCES): require(path.is_file(),f"missing {path.name}",errors)
    if errors:return fail(errors)
    html=HTML.read_text();md=MD.read_text();css=CSS.read_text();js=JS.read_text();refs=REFERENCES.read_text()
    p=Parser();p.feed(html);p.close();errors.extend(f"HTML: {e}" for e in p.errors)
    html_slides=re.findall(r'<section class="slide(?: active)?" id="slide-(\d+)"',html)
    md_slides=re.findall(r'^## Slide (\d+) —',md,flags=re.M)
    notes=re.findall(r'<template id="notes-(\d+)">',html)
    expected=[str(i) for i in range(1,14)]
    require(html_slides==expected,"HTML must contain exactly 13 ordered slides",errors)
    require(md_slides==expected,"Markdown must contain exactly 13 ordered slides",errors)
    require(notes==expected,"HTML must contain notes templates 1–13",errors)
    for phrase in ("CONCEPT / SIMULATED", "AED 1,000,000", "frontline retail advisors", "field technicians", "77.5", "59.3", "n=4", "eight commands plus rest", "preprint", "2.47 ms", "not end-to-end", "authored", "TBD", "claim ledger", "go / change / stop"):
        require(phrase.lower() in (html+md).lower(),f"missing required claim/boundary: {phrase}",errors)
    for forbidden in ("[BEACHHEAD", "[BUSINESS MODEL", "CURRENCY TBD", "post-stroke aphasia", "audible to the wearer only", "no new AI to build", "this stopped being research", "Whisper/AAC"):
        require(forbidden.lower() not in (html+md).lower(),f"unresolved/prohibited deck wording: {forbidden}",errors)
    for system,ref in (("EarCommand","R38"),("EchoSpeech","R39"),("MuteIt","R40"),("Whispp","R41")):
        require(system in html and system in md,f"named comparator missing from deck: {system}",errors)
        require(f"**{ref} ·" in refs,f"named comparator lacks source record: {system} / {ref}",errors)
    require("R38–R41" in html and "R38–R41" in md,"named comparator source range missing from deck",errors)
    require("AED 1M" in html and "AED 1,000,000" in html,"approved pilot fee must appear clearly",errors)
    require("per-seat annual" in html.lower() and "acquisition/exit" in html.lower(),"both approved business paths must appear",errors)
    require("prefers-reduced-motion" in css and "@media print" in css and "focus-visible" in css,"accessibility/print styles missing",errors)
    require("touchstart" in js and "keydown" in js and "fullscreen" in js,"keyboard/touch/fullscreen controls missing",errors)
    require('closest("a,button,input,select,textarea,summary,[contenteditable]")' in js,"presentation shortcuts must ignore interactive targets",errors)
    for src,alt in p.images:
        require(bool(alt),f"image lacks alt: {src}",errors)
        require(not re.match(r'https?://',src),f"remote image dependency: {src}",errors)
        path=ROOT/src
        require(path.is_file(),f"missing image asset: {src}",errors)
        if path.suffix==".svg" and path.is_file():
            try: ET.parse(path)
            except ET.ParseError as e: errors.append(f"invalid SVG {src}: {e}")
    for ref in p.scripts+p.links:
        require(not re.match(r'https?://',ref),f"remote runtime dependency: {ref}",errors)
        require((ROOT/ref).is_file(),f"missing local runtime dependency: {ref}",errors)
    require("<iframe" not in html and "<video" not in html and "<audio" not in html,"embedded media is prohibited in offline deck",errors)
    require("url(http" not in css.lower() and "@import" not in css.lower(),"remote CSS dependency/import",errors)
    return fail(errors) if errors else success(len(p.images))

def fail(errors): print("pitch validation failed:",*[f"- {e}" for e in errors],sep="\n");return 1
def success(images): print(f"pitch validation passed: 13 slides, 13 notes, approved decisions, boundaries, and {images} local SVG uses");return 0
if __name__=="__main__":raise SystemExit(main())

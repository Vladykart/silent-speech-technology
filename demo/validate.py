#!/usr/bin/env python3
"""Dependency-free static validation for the offline concept demo.

This checks structure and guardrails, not visual rendering or sensing performance.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent

class Parser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    def __init__(self):
        super().__init__(); self.stack=[]; self.errors=[]; self.ids=set(); self.labels=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids: self.errors.append(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "label" and "for" in attrs: self.labels.append(attrs["for"])
        if tag not in self.VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack: self.errors.append(f"unexpected </{tag}>"); return
        expected=self.stack.pop()
        if expected != tag: self.errors.append(f"expected </{expected}>, got </{tag}>")
    def close(self):
        super().close()
        if self.stack: self.errors.append("unclosed: " + ", ".join(self.stack[-5:]))

def main():
    errors=[]
    required=["index.html","styles.css","core.js","script.js","README.md","PRESENTER.md","tests/core.test.js"]
    for name in required:
        if not (ROOT/name).is_file(): errors.append(f"missing {name}")
    if errors: return fail(errors)
    html=(ROOT/"index.html").read_text()
    css=(ROOT/"styles.css").read_text()
    js=(ROOT/"script.js").read_text()
    core=(ROOT/"core.js").read_text()
    parser=Parser(); parser.feed(html); parser.close(); errors.extend(parser.errors)
    for target in parser.labels:
        if target not in parser.ids: errors.append(f"label target missing: {target}")
    for phrase in ["CONCEPT / SIMULATED PIPELINE", "authored fixture", "measured accuracy", "No media APIs", "No network requests", "human confirmation", "reject threshold", "LOCKED", "12 commands", "authored repair", "WHAT LEFT THE CONCEPT DEVICE"]:
        if phrase.lower() not in html.lower(): errors.append(f"missing boundary phrase: {phrase}")
    for forbidden in ["navigator.mediaDevices", "getUserMedia", "MediaRecorder", "localStorage", "sessionStorage", "fetch(", "XMLHttpRequest", "WebSocket"]:
        if forbidden in html+js+core: errors.append(f"forbidden API/dependency: {forbidden}")
    if re.search(r'https?://', html+css+js+core): errors.append("demo runtime contains a remote URL")
    if "@media (prefers-reduced-motion: reduce)" not in css: errors.append("reduced-motion style missing")
    if "aria-live" not in html or "focus-visible" not in css: errors.append("accessibility feedback/focus treatment missing")
    if "module.exports" not in core: errors.append("core is not testable under Node")
    return fail(errors) if errors else success()

def fail(errors):
    print("demo validation failed:", *[f"- {e}" for e in errors], sep="\n"); return 1

def success():
    print("demo validation passed: offline structure, evidence labels, privacy gates, and accessibility hooks present"); return 0

if __name__ == "__main__": raise SystemExit(main())

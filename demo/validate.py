#!/usr/bin/env python3
"""Dependency-free validation for the static concept demo and its public artifact."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

sys.dont_write_bytecode = True
import generate_manifest

ROOT = Path(__file__).resolve().parent


class Parser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.ids: set[str] = set()
        self.labels: list[str] = []
        self.starts: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.starts.append((tag, attributes))
        if "id" in attributes:
            if attributes["id"] in self.ids:
                self.errors.append(f"duplicate id: {attributes['id']}")
            self.ids.add(attributes["id"])
        if tag == "label" and "for" in attributes:
            self.labels.append(attributes["for"])
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}>")
            return
        expected = self.stack.pop()
        if expected != tag:
            self.errors.append(f"expected </{expected}>, got </{tag}>")

    def close(self):
        super().close()
        if self.stack:
            self.errors.append("unclosed: " + ", ".join(self.stack[-5:]))


def parse_html(path: Path) -> Parser:
    parser = Parser()
    parser.feed(path.read_text())
    parser.close()
    return parser


def main() -> int:
    errors: list[str] = []
    required = [
        "index.html", "404.html", "styles.css", "core.js", "script.js", "robots.txt",
        "README.md", "PRESENTER.md", "DEPLOYMENT.md", "CLAIM_BOUNDARY.md", "SOURCE_LINEAGE.md",
        "LAB_FOUNDATION.md", "THIRD_PARTY_NOTICES.md", "artifact-manifest.json",
        "generate_manifest.py", "tests/core.test.js",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return fail(errors)

    html = (ROOT / "index.html").read_text()
    css = (ROOT / "styles.css").read_text()
    js = (ROOT / "script.js").read_text()
    core = (ROOT / "core.js").read_text()
    runtime = html + css + js + core
    parser = parse_html(ROOT / "index.html")
    errors.extend(parser.errors)
    for target in parser.labels:
        if target not in parser.ids:
            errors.append(f"label target missing: {target}")

    tags = [tag for tag, _ in parser.starts]
    for landmark in ("header", "main", "footer", "aside"):
        if landmark not in tags:
            errors.append(f"accessibility landmark missing: {landmark}")
    if "h1" not in tags or tags.count("h2") < 4:
        errors.append("heading hierarchy is incomplete")
    for tag, attrs in parser.starts:
        if "style" in attrs:
            errors.append(f"inline style prohibited on <{tag}>")
        if tag == "button" and attrs.get("type") != "button":
            errors.append("every button must declare type=button")
        if tag == "form":
            errors.append("forms are prohibited")
        for attribute in ("href", "src"):
            reference = attrs.get(attribute)
            if not reference:
                continue
            scheme = urlparse(reference).scheme
            if scheme in {"http", "https"}:
                if tag != "a" or attribute != "href":
                    errors.append(f"remote runtime dependency: <{tag} {attribute}={reference}>")
                if scheme != "https":
                    errors.append(f"external citation must use HTTPS: {reference}")
                rel = set((attrs.get("rel") or "").split())
                if not {"external", "noopener", "noreferrer"}.issubset(rel):
                    errors.append(f"external link missing safe rel tokens: {reference}")

    boundary_phrases = [
        "CONCEPT / SIMULATED", "Temporary research demo", "No trained model or inference",
        "authored stage timing", "not calibrated probabilities", "8 synthetic normalized channels",
        "CTC-style candidate stream", "Abstain · uncertain fixture", "Choose authored repair",
        "Mandatory confirmation", "No external runtime requests", "No local storage", "No cookies",
        "CONCEPT / SIMULATED OUTPUT", "NO TRANSMISSION", "low-consequence", "safety-sensitive",
    ]
    for phrase in boundary_phrases:
        if phrase.lower() not in html.lower() and phrase.lower() not in js.lower():
            errors.append(f"missing boundary/state phrase: {phrase}")
    if html.lower().count("concept / simulated") < 4:
        errors.append("truth label is not retained across screen/output/footer states")

    source_phrases = [
        "a89357c2086609b432919b9d14ffc0be5d8983d5", "dgaddy/silent_speech",
        "recognition_model.py", "read_emg.py", "architecture.py", "Copyright © 2021 David Gaddy",
        "approximately 36% open-vocabulary WER", "EMNLP 2020", "ACL 2021",
        "Consented EMG capture hardware", "pre-hardware lab foundation", "project claim boundary",
    ]
    for phrase in source_phrases:
        if phrase.lower() not in html.lower():
            errors.append(f"visible source/prerequisite boundary missing: {phrase}")

    forbidden_apis = [
        "navigator.mediaDevices", "getUserMedia", "MediaRecorder", "AudioContext", "webkitAudioContext",
        "RTCPeerConnection", "localStorage", "sessionStorage", "indexedDB", "document.cookie",
        "fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "serviceWorker", "new Worker",
    ]
    for forbidden in forbidden_apis:
        if forbidden in runtime:
            errors.append(f"forbidden runtime API/dependency: {forbidden}")
    script_runtime = (css + js + core).replace("http://www.w3.org/2000/svg", "")
    if re.search(r"https?://", script_runtime):
        errors.append("CSS/JavaScript runtime contains a remote URL other than the local SVG namespace")
    if re.search(r"<script(?![^>]+src=)[^>]*>", html, re.IGNORECASE):
        errors.append("inline script is prohibited")
    if "connect-src 'none'" not in html or "media-src 'none'" not in html or "form-action 'none'" not in html:
        errors.append("restrictive page CSP metadata missing")
    if "noindex, nofollow, noarchive" not in html:
        errors.append("no-index metadata missing")

    for css_hook in (":focus-visible", "@media (prefers-reduced-motion: reduce)", "@media print", "@media (max-width: 560px)", "@keyframes signal-stream"):
        if css_hook not in css:
            errors.append(f"responsive/accessibility style missing: {css_hook}")
    for js_hook in ("addEventListener(\"keydown\"", "event.key === \" \"", "[\"1\", \"2\", \"3\"]", "event.altKey", "replaceChildren"):
        if js_hook not in js:
            errors.append(f"keyboard/safe DOM behavior missing: {js_hook}")
    if "aria-live" not in html or "role=\"status\"" not in html or "skip-link" not in html:
        errors.append("accessible feedback/navigation hooks missing")
    if "module.exports" not in core:
        errors.append("core is not testable under Node")

    robots = (ROOT / "robots.txt").read_text()
    if "User-agent: *" not in robots or "Disallow: /" not in robots:
        errors.append("robots exclusion missing")
    not_found = (ROOT / "404.html").read_text()
    not_found_parser = parse_html(ROOT / "404.html")
    errors.extend(f"404: {error}" for error in not_found_parser.errors)
    for phrase in ("HTTP 404", "CONCEPT / SIMULATED", "noindex"):
        if phrase.lower() not in not_found.lower():
            errors.append(f"404 boundary missing: {phrase}")

    deployment = (ROOT / "DEPLOYMENT.md").read_text()
    for phrase in ("GET` and `HEAD` only", "directory listing", "true HTTP 404", "X-Content-Type-Options", "frame-ancestors 'none'", "no credentials", "Do not inject analytics"):
        if phrase.lower() not in deployment.lower():
            errors.append(f"deployment control missing: {phrase}")

    expected_manifest = generate_manifest.encoded_manifest()
    if (ROOT / "artifact-manifest.json").read_bytes() != expected_manifest:
        errors.append("artifact manifest does not match current demo tree")
    else:
        manifest = json.loads(expected_manifest)
        listed = {record["path"] for record in manifest["files"]}
        discovered = {path.relative_to(ROOT).as_posix() for path in generate_manifest.public_files()}
        if listed != discovered:
            errors.append("artifact manifest coverage mismatch")
        if manifest.get("algorithm") != "sha256" or manifest.get("selfHashExcluded") != "artifact-manifest.json":
            errors.append("artifact manifest schema/hash rule mismatch")

    return fail(errors) if errors else success(len(json.loads(expected_manifest)["files"]))


def fail(errors: list[str]) -> int:
    print("demo validation failed:", *[f"- {error}" for error in errors], sep="\n")
    return 1


def success(file_count: int) -> int:
    print(f"demo validation passed: offline runtime, truth/source labels, accessibility, deployment controls, and {file_count}-file manifest verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

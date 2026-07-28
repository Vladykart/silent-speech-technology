#!/usr/bin/env python3
"""Validate the generated Quiet Channel PPTX without third-party packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
PPTX = ROOT / "quiet-channel-4-slide-deck.pptx"
EVIDENCE = ROOT / "quiet-channel-4-slide-build.json"
BUILDER = ROOT / "build_4_slide_pptx.py"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

REQUIRED_TEXT = [
    "THE QUIET CHANNEL", "privacy-first silent command interface",
    "e& retail advisors", "Field technicians", "CONCEPT · NOT FINISHED HARDWARE",
    "surface-EMG concept", "12-command grammar", "On device", "confirm / repair",
    "existing agent / CRM", "NOT open-vocabulary transcription", "NOT mind reading",
    "NOT autonomous billing changes", "NO working physical prototype",
    "PREPRINT · R26", "n=4", "14 neck sEMG channels", "8 commands + rest",
    "77.5±6.6%", "59.3±2.2%", "PEER-REVIEWED · R03–R04",
    "Gesture: Meta wrist sEMG", "Optical/contactless", "Implanted",
    "Raw signals stay on device during use", "Decoded text remains personal data",
    "Calibration requires explicit opt-in", "No emotion or medical inference is produced",
    "AED 1,000,000", "e& beachhead", "NO-GO", "SEPARATE DEPLOYMENT DECISION AFTER EVIDENCE",
    "per-seat pricing TBD", "strategic funding / acquisition optional, unpriced upside",
]
REQUIRED_MEDIA = {"ppt/media/concept-research-rig.svg"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_for_rels(name: str) -> str:
    if name == "_rels/.rels":
        return ""
    directory, filename = posixpath.split(name)
    parent = posixpath.dirname(directory)
    return posixpath.join(parent, filename[:-5])


def target_for(source: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), target))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", nargs="?", type=Path, default=PPTX)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--no-rebuild", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    if not args.pptx.is_file():
        return fail([f"missing PPTX: {args.pptx}"])
    try:
        with ZipFile(args.pptx) as zf:
            bad = zf.testzip()
            if bad: errors.append(f"ZIP CRC failure: {bad}")
            infos = zf.infolist(); names = zf.namelist(); name_set = set(names)
            if len(names) != len(name_set): errors.append("duplicate ZIP part names")
            if names != sorted(names): errors.append("ZIP parts are not deterministically sorted")
            for info in infos:
                if info.date_time != FIXED_TIME: errors.append(f"non-deterministic timestamp: {info.filename} {info.date_time}")
            required_parts = {
                "[Content_Types].xml", "_rels/.rels", "docProps/core.xml", "docProps/app.xml",
                "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels",
                "ppt/slideMasters/slideMaster1.xml", "ppt/slideLayouts/slideLayout1.xml",
                "ppt/notesMasters/notesMaster1.xml", "ppt/theme/theme1.xml",
            } | REQUIRED_MEDIA
            for name in required_parts:
                if name not in name_set: errors.append(f"missing required OOXML part: {name}")
            roots: dict[str, ET.Element] = {}
            for name in names:
                if name.endswith((".xml", ".rels", ".svg")):
                    try: roots[name] = ET.fromstring(zf.read(name))
                    except ET.ParseError as exc: errors.append(f"malformed XML {name}: {exc}")
            ct = roots.get("[Content_Types].xml")
            if ct is not None:
                defaults = {(e.attrib.get("Extension"), e.attrib.get("ContentType")) for e in ct.findall(f"{{{CT}}}Default")}
                if ("svg", "image/svg+xml") not in defaults: errors.append("SVG content type is not declared")
            for name, root in roots.items():
                if not name.endswith(".rels"): continue
                source = source_for_rels(name)
                for rel in root.findall(f"{{{PKG_R}}}Relationship"):
                    if rel.attrib.get("TargetMode") == "External": errors.append(f"remote/external relationship in {name}: {rel.attrib}")
                    target = target_for(source, rel.attrib.get("Target", ""))
                    if target not in name_set: errors.append(f"broken relationship in {name}: {target}")
            pres = roots.get("ppt/presentation.xml")
            pres_rels = roots.get("ppt/_rels/presentation.xml.rels")
            ordered_slides: list[str] = []
            if pres is not None and pres_rels is not None:
                rel_map = {e.attrib["Id"]: e.attrib["Target"] for e in pres_rels.findall(f"{{{PKG_R}}}Relationship")}
                for node in pres.findall(f".//{{{P}}}sldId"):
                    rid = node.attrib.get(f"{{{R}}}id", "")
                    if rid not in rel_map: errors.append(f"presentation slide relationship missing: {rid}")
                    else: ordered_slides.append(target_for("ppt/presentation.xml", rel_map[rid]))
            expected_slides = [f"ppt/slides/slide{i}.xml" for i in range(1, 5)]
            if ordered_slides != expected_slides: errors.append(f"slide count/order mismatch: {ordered_slides}")
            expected_notes = [f"ppt/notesSlides/notesSlide{i}.xml" for i in range(1, 5)]
            if [n for n in expected_notes if n in name_set] != expected_notes: errors.append("must contain exactly 4 ordered notes slides")
            actual_slide_parts = sorted(n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
            actual_note_parts = sorted(n for n in names if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml"))
            if actual_slide_parts != expected_slides: errors.append(f"must contain exactly 4 slide parts: {actual_slide_parts}")
            if actual_note_parts != expected_notes: errors.append(f"must contain exactly 4 speaker-note parts: {actual_note_parts}")
            slide_texts = []
            editable_shapes = 0
            for name in expected_slides:
                root = roots.get(name)
                if root is None: continue
                text = " ".join((n.text or "") for n in root.findall(f".//{{{A}}}t"))
                slide_texts.append(text)
                editable_shapes += len(root.findall(f".//{{{P}}}sp"))
            all_slide_text = "\n".join(slide_texts)
            for phrase in REQUIRED_TEXT:
                if phrase.lower() not in all_slide_text.lower(): errors.append(f"required decision/boundary text absent: {phrase}")
            if editable_shapes < 55: errors.append(f"too few editable DrawingML shapes: {editable_shapes}")
            for i, name in enumerate(expected_notes, 1):
                root = roots.get(name)
                if root is None: continue
                note_text = " ".join((n.text or "") for n in root.findall(f".//{{{A}}}t"))
                if len(note_text) < 120: errors.append(f"speaker notes too short on slide {i}")
                if not any(key in note_text for key in ("SOURCE", "SOURCES")): errors.append(f"notes lack source section on slide {i}")
                if not root.findall(f".//{{{P}}}ph[@type='body']"): errors.append(f"notes body placeholder missing on slide {i}")
            if not REQUIRED_MEDIA.issubset(name_set): errors.append("required project-authored SVG is not embedded")
            forbidden = [n for n in names if n.endswith((".exe", ".bin", ".vbaProject.bin")) or "embeddings/" in n]
            if forbidden: errors.append(f"forbidden embedded binary/macro parts: {forbidden}")
    except BadZipFile as exc:
        return fail([f"not a valid ZIP/OOXML package: {exc}"])

    if not args.evidence.is_file():
        errors.append(f"missing deterministic build evidence: {args.evidence}")
    else:
        try: evidence = json.loads(args.evidence.read_text())
        except (json.JSONDecodeError, OSError) as exc: errors.append(f"invalid build evidence JSON: {exc}"); evidence = {}
        if evidence.get("sha256") != digest(args.pptx): errors.append("PPTX SHA-256 does not match build evidence")
        if evidence.get("slides") != 4 or evidence.get("notes_slides") != 4: errors.append("build evidence slide counts wrong")
        if evidence.get("builder_sha256") != digest(BUILDER): errors.append("builder SHA-256 does not match evidence")
        if evidence.get("source_markdown_sha256") != digest(ROOT / "deck.md"): errors.append("deck Markdown SHA-256 does not match evidence")

    if not args.no_rebuild:
        with tempfile.TemporaryDirectory(prefix="quiet-channel-pptx-") as tmp:
            rebuilt = Path(tmp) / "rebuilt.pptx"
            result = subprocess.run([sys.executable, str(BUILDER), "--output", str(rebuilt), "--no-evidence"], capture_output=True, text=True)
            if result.returncode != 0: errors.append(f"deterministic rebuild failed: {result.stderr.strip()}")
            elif rebuilt.read_bytes() != args.pptx.read_bytes(): errors.append(f"deterministic rebuild mismatch: {digest(rebuilt)} != {digest(args.pptx)}")
    if errors: return fail(errors)
    print(f"PPTX validation passed: 4 slides, 4 notes, editable shapes, project-authored SVG, valid relationships, no remote relationships, deterministic sha256={digest(args.pptx)}")
    return 0


def fail(errors: list[str]) -> int:
    print("PPTX validation failed:", *[f"- {e}" for e in errors], sep="\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

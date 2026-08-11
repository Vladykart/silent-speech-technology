#!/usr/bin/env python3
"""Validate the four-slide executive PPTX, including static visual lint.

This validator proves deterministic OOXML structure, narrative/source alignment,
word/type/geometry constraints, native connector/chart requirements, notes,
security, and legacy 13-slide byte stability. It does not replace target-
PowerPoint rendered rehearsal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
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
SOURCE = ROOT / "deck-4-slide.md"
LEGACY_PPTX = ROOT / "quiet-channel-evidence-deck.pptx"
LEGACY_BUILD = ROOT / "pptx-build.json"
LEGACY_PPTX_SHA256 = "48ccde3da66aaac5c834f20691930e2b996d2c58e418ee590548908670e0647c"
LEGACY_BUILD_SHA256 = "00cb793eedd4731e8b1d3940e60814f2d7b6a51e02678cf05bf07a2ed12b7655"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
SW, SH = 12192000, 6858000
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
ALLOWED_URLS = {"https://arxiv.org/abs/2603.02847v2"}
SMALL_TEXT_NAMES = {
    "Deck label", "Status label", "Slide number", "Eyebrow", "Repair label",
    "Raw boundary label", "Chart gap label", "Proof title", "Evidence caption",
    "Source footer", "Pilot label",
}
SMALL_TEXT_PREFIXES = ("Chart label ", "Ask label ")
REQUIRED_TEXT = [
    "A quiet command lane", "for frontline work.",
    "One opt-in, low-consequence workflow", "Connect to the existing assistant.", "RETAIL", "FIELD", "QUIET", "COMMAND",
    "A fixed command channel.", "A human gate before action.",
    "DELIBERATE", "PROPOSED", "sEMG", "FIXED", "CANDIDATES", "PREVIEW", "CONFIRM", "REPAIR",
    "RAW SIGNAL STOPS HERE", "not implemented hardware, security, latency, or integration",
    "The signal is plausible.", "Cross-session transfer is the risk.",
    "77.5±6.6%", "59.3±2.2%", "−18.2 POINTS", "PILOT MUST PROVE",
    "SilentWear v2 preprint", "n=4", "14 neck sEMG channels", "8 commands + rest",
    "top-1 accuracy", "not this project", "arXiv:2603.02847v2",
    "Approve the 90-day pilot.", "Buy a go / change / stop decision.",
    "AED", "1,000,000", "FIXED FEE · 90 DAYS", "GO / CHANGE", "/ STOP",
    "Annual pricing, strategic funding, valuation", "acquisition/exit amounts remain TBD",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_story() -> dict:
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError("missing fenced JSON story")
    return json.loads(match.group(1))


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


def shape_name(shape: ET.Element, kind: str = "sp") -> str:
    if kind == "cxnSp":
        node = shape.find(f"./{{{P}}}nvCxnSpPr/{{{P}}}cNvPr")
    else:
        node = shape.find(f"./{{{P}}}nvSpPr/{{{P}}}cNvPr")
    return node.attrib.get("name", "") if node is not None else ""


def geometry(shape: ET.Element) -> tuple[int, int, int, int] | None:
    xfrm = shape.find(f"./{{{P}}}spPr/{{{A}}}xfrm")
    if xfrm is None:
        return None
    off = xfrm.find(f"{{{A}}}off"); ext = xfrm.find(f"{{{A}}}ext")
    if off is None or ext is None:
        return None
    return tuple(int(v) for v in (off.attrib["x"], off.attrib["y"], ext.attrib["cx"], ext.attrib["cy"]))


def intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return min(ax+aw, bx+bw) > max(ax, bx) and min(ay+ah, by+bh) > max(ay, by)


def fail(errors: list[str]) -> int:
    print("PPTX validation failed:", *[f"- {e}" for e in errors], sep="\n")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", nargs="?", type=Path, default=PPTX)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--no-rebuild", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        story = load_story()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail([f"invalid four-slide narrative source: {exc}"])
    if len(story.get("slides", [])) != 4:
        errors.append("narrative source must contain exactly four slides")
    if not args.pptx.is_file():
        return fail([f"missing PPTX: {args.pptx}"])

    if not LEGACY_PPTX.is_file() or digest(LEGACY_PPTX) != LEGACY_PPTX_SHA256:
        errors.append("13-slide PPTX changed; it must remain byte-unchanged in this scope")
    if not LEGACY_BUILD.is_file() or digest(LEGACY_BUILD) != LEGACY_BUILD_SHA256:
        errors.append("13-slide build evidence changed; it must remain byte-unchanged in this scope")

    word_counts: list[int] = []
    try:
        with ZipFile(args.pptx) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"ZIP CRC failure: {bad}")
            infos = zf.infolist(); names = zf.namelist(); name_set = set(names)
            if len(names) != len(name_set):
                errors.append("duplicate ZIP part names")
            if names != sorted(names):
                errors.append("ZIP parts are not deterministically sorted")
            for info in infos:
                if info.date_time != FIXED_TIME:
                    errors.append(f"non-deterministic timestamp: {info.filename} {info.date_time}")
            required = {
                "[Content_Types].xml", "_rels/.rels", "docProps/core.xml", "docProps/app.xml",
                "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels",
                "ppt/slideMasters/slideMaster1.xml", "ppt/slideLayouts/slideLayout1.xml",
                "ppt/notesMasters/notesMaster1.xml", "ppt/theme/theme1.xml",
            }
            for name in required:
                if name not in name_set:
                    errors.append(f"missing required OOXML part: {name}")
            roots: dict[str, ET.Element] = {}
            for name in names:
                if name.endswith((".xml", ".rels", ".svg")):
                    try:
                        roots[name] = ET.fromstring(zf.read(name))
                    except ET.ParseError as exc:
                        errors.append(f"malformed XML {name}: {exc}")
            for name, root in roots.items():
                if not name.endswith(".rels"):
                    continue
                source = source_for_rels(name)
                for rel in root.findall(f"{{{PKG_R}}}Relationship"):
                    if rel.attrib.get("TargetMode") == "External":
                        errors.append(f"remote/external relationship in {name}: {rel.attrib}")
                    target = target_for(source, rel.attrib.get("Target", ""))
                    if target not in name_set:
                        errors.append(f"broken relationship in {name}: {target}")

            forbidden_parts = [
                n for n in names if n.startswith(("ppt/media/", "ppt/charts/", "ppt/embeddings/"))
                or n.endswith((".exe", ".bin", ".vbaProject.bin"))
            ]
            if forbidden_parts:
                errors.append(f"four-slide deck must use native shapes only; forbidden parts: {forbidden_parts}")

            pres = roots.get("ppt/presentation.xml"); pres_rels = roots.get("ppt/_rels/presentation.xml.rels")
            ordered_slides: list[str] = []
            if pres is not None and pres_rels is not None:
                rel_map = {e.attrib["Id"]: e.attrib["Target"] for e in pres_rels.findall(f"{{{PKG_R}}}Relationship")}
                for node in pres.findall(f".//{{{P}}}sldId"):
                    rid = node.attrib.get(f"{{{R}}}id", "")
                    if rid not in rel_map:
                        errors.append(f"presentation slide relationship missing: {rid}")
                    else:
                        ordered_slides.append(target_for("ppt/presentation.xml", rel_map[rid]))
            expected_slides = [f"ppt/slides/slide{i}.xml" for i in range(1, 5)]
            expected_notes = [f"ppt/notesSlides/notesSlide{i}.xml" for i in range(1, 5)]
            if ordered_slides != expected_slides:
                errors.append(f"slide count/order mismatch: {ordered_slides}")
            actual_slides = sorted(n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
            actual_notes = sorted(n for n in names if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml"))
            if actual_slides != expected_slides:
                errors.append(f"must contain exactly four slide parts: {actual_slides}")
            if actual_notes != expected_notes:
                errors.append(f"must contain exactly four notes parts: {actual_notes}")

            all_slide_text: list[str] = []
            all_package_text: list[str] = []
            for i, name in enumerate(expected_slides, 1):
                root = roots.get(name)
                if root is None:
                    continue
                texts = [(n.text or "") for n in root.findall(f".//{{{A}}}t")]
                all_slide_text.extend(texts); all_package_text.extend(texts)
                count = sum(
                    1 for text in texts for token in text.split()
                    if re.search(r"[A-Za-z0-9]", token)
                )
                word_counts.append(count)
                cap = int(story["slides"][i-1]["max_words"])
                if count > cap:
                    errors.append(f"slide {i} word cap exceeded: {count} > {cap}")
                if "CONCEPT / SIMULATED" not in texts:
                    errors.append(f"slide {i} lacks visible concept/simulated status")

                shapes = root.findall(f".//{{{P}}}sp")
                connectors = root.findall(f".//{{{P}}}cxnSp")
                text_boxes: list[tuple[str, tuple[int, int, int, int]]] = []
                for shape in shapes + connectors:
                    kind = "cxnSp" if shape.tag == f"{{{P}}}cxnSp" else "sp"
                    name_value = shape_name(shape, kind)
                    box = geometry(shape)
                    if box is None:
                        continue
                    x, y, w, h = box
                    if x < 0 or y < 0 or x+w > SW or y+h > SH:
                        errors.append(f"slide {i} object outside bounds: {name_value} {box}")
                    if kind == "sp":
                        runs = shape.findall(f".//{{{A}}}rPr")
                        run_text = " ".join((n.text or "") for n in shape.findall(f".//{{{A}}}t"))
                        if run_text:
                            text_boxes.append((name_value, box))
                            sizes = [int(r.attrib["sz"]) for r in runs if "sz" in r.attrib]
                            if not sizes:
                                errors.append(f"slide {i} text lacks explicit size: {name_value}")
                            else:
                                minimum = min(sizes)
                                allowed_small = name_value in SMALL_TEXT_NAMES or name_value.startswith(SMALL_TEXT_PREFIXES)
                                required_min = 950 if allowed_small else 1300
                                if minimum < required_min:
                                    errors.append(f"slide {i} text too small: {name_value} {minimum/100:.1f} pt < {required_min/100:.1f} pt")
                            for run in runs:
                                latin = run.find(f"{{{A}}}latin")
                                if latin is None or latin.attrib.get("typeface") != "Arial":
                                    errors.append(f"slide {i} text does not explicitly use Arial: {name_value}")
                for left in range(len(text_boxes)):
                    for right in range(left+1, len(text_boxes)):
                        if intersects(text_boxes[left][1], text_boxes[right][1]):
                            errors.append(f"slide {i} overlapping text boxes: {text_boxes[left][0]} / {text_boxes[right][0]}")
                title_shapes = [s for s in shapes if shape_name(s) == "Title"]
                if len(title_shapes) != 1:
                    errors.append(f"slide {i} must have exactly one Title text box")
                elif min(int(r.attrib["sz"]) for r in title_shapes[0].findall(f".//{{{A}}}rPr")) < 4200:
                    errors.append(f"slide {i} title is below 42 pt")
                if any("Card" in shape_name(s) for s in shapes):
                    errors.append(f"slide {i} contains rejected card-grid naming")

                connector_names = {shape_name(c, "cxnSp") for c in connectors}
                if i == 2:
                    if len(connectors) < 10:
                        errors.append(f"slide 2 needs explicit flow/repair/boundary connectors; found {len(connectors)}")
                    for required_name in ("Flow connector 1", "Confirmed handoff connector", "Repair loop return", "Raw signal boundary"):
                        if required_name not in connector_names:
                            errors.append(f"slide 2 missing connector: {required_name}")
                if i == 3:
                    names_here = {shape_name(s) for s in shapes}
                    for required_name in ("Chart bar Global", "Chart bar Held-out", "Chart value Global", "Chart value Held-out", "Evidence caption"):
                        if required_name not in names_here:
                            errors.append(f"slide 3 missing native evidence primitive: {required_name}")
                if i == 4:
                    amount = [s for s in shapes if shape_name(s) == "Pilot amount"]
                    if len(amount) != 1:
                        errors.append("slide 4 must have exactly one Pilot amount")
                    else:
                        amount_sizes = [int(r.attrib["sz"]) for r in amount[0].findall(f".//{{{A}}}rPr")]
                        all_sizes = [int(r.attrib["sz"]) for s in shapes for r in s.findall(f".//{{{A}}}rPr") if "sz" in r.attrib]
                        if not amount_sizes or min(amount_sizes) < 6000 or max(amount_sizes) != max(all_sizes):
                            errors.append("slide 4 amount must be 60+ pt and the deck's dominant type on that slide")

            combined = "\n".join(all_slide_text)
            for phrase in REQUIRED_TEXT:
                if phrase.lower() not in combined.lower():
                    errors.append(f"required narrative/evidence text absent: {phrase}")

            for i, name in enumerate(expected_notes, 1):
                root = roots.get(name)
                if root is None:
                    continue
                texts = [(n.text or "") for n in root.findall(f".//{{{A}}}t")]
                all_package_text.extend(texts)
                note_text = "\n".join(texts)
                if len(note_text) < 450:
                    errors.append(f"speaker notes too short on slide {i}")
                for section in ("ROLE", "TALK TRACK", "BOUNDARY", "SOURCES"):
                    if section not in texts:
                        errors.append(f"slide {i} notes lack {section} section")
                if not root.findall(f".//{{{P}}}ph[@type='body']"):
                    errors.append(f"notes body placeholder missing on slide {i}")
            package_text = "\n".join(all_package_text)
            urls = set(re.findall(r"https?://[^\s;]+", package_text))
            if urls != ALLOWED_URLS:
                errors.append(f"unexpected or missing URL in slide/notes text: {sorted(urls)}")
            if re.search(r"https?://i\.getmoshi\.app/", package_text, re.I):
                errors.append("confidential capability URL is forbidden")
            if "concept-research-rig" in package_text.lower() or "behind-the-ear" in package_text.lower():
                errors.append("fake-device/form-factor language is forbidden in the four-slide artifact")
    except BadZipFile as exc:
        return fail([f"not a valid ZIP/OOXML package: {exc}"])

    if not args.evidence.is_file():
        errors.append(f"missing deterministic build evidence: {args.evidence}")
    else:
        try:
            evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"invalid build evidence JSON: {exc}"); evidence = {}
        if evidence.get("sha256") != digest(args.pptx):
            errors.append("PPTX SHA-256 does not match build evidence")
        if evidence.get("slides") != 4 or evidence.get("notes_slides") != 4:
            errors.append("build evidence slide counts wrong")
        if evidence.get("media") != []:
            errors.append("four-slide build evidence must declare no embedded media")
        if evidence.get("builder_sha256") != digest(BUILDER):
            errors.append("builder SHA-256 does not match evidence")
        if evidence.get("source") != "pitch/deck-4-slide.md":
            errors.append("build evidence points to wrong narrative source")
        if evidence.get("source_markdown_sha256") != digest(SOURCE):
            errors.append("four-slide source Markdown SHA-256 does not match evidence")

    if not args.no_rebuild:
        with tempfile.TemporaryDirectory(prefix="quiet-channel-4-pptx-") as tmp:
            rebuilt = Path(tmp) / "rebuilt.pptx"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(rebuilt), "--no-evidence"],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                errors.append(f"deterministic rebuild failed: {result.stderr.strip()}")
            elif rebuilt.read_bytes() != args.pptx.read_bytes():
                errors.append(f"deterministic rebuild mismatch: {digest(rebuilt)} != {digest(args.pptx)}")
    if errors:
        return fail(errors)
    print(
        "PPTX validation passed: 4 editorial slides, 4 notes, "
        f"word counts={word_counts}, room-readable type, native connectors/chart, bounded geometry, "
        "no media/remote relationships/confidential URL, deterministic bytes, and unchanged 13-slide artifacts; "
        "target-PowerPoint visual rehearsal remains required; "
        f"sha256={digest(args.pptx)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

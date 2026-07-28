#!/usr/bin/env python3
"""Build the four-slide Quiet Channel executive PPTX with the standard library.

The editable narrative comes from deck-4-slide.md. Slides are native DrawingML
text, shapes, connectors, and chart primitives: no template, logo, or media is
embedded. The same scene graph can emit representative SVG/HTML previews for
local geometry QA; those previews are not exact PowerPoint rendering.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import html
import json
from pathlib import Path
import re
from typing import Any
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "deck-4-slide.md"
DEFAULT_OUTPUT = ROOT / "quiet-channel-4-slide-deck.pptx"
DEFAULT_EVIDENCE = ROOT / "quiet-channel-4-slide-build.json"
EMU = 914400
SW, SH = 12192000, 6858000
SLIDE_W, SLIDE_H = 13.333, 7.5
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

C = {
    "night": "101816", "surface": "17231F", "surface2": "1C2925",
    "ink": "F4F0E6", "muted": "B8B7AD", "quiet": "858B85",
    "line": "53665F", "teal": "5CD3BD", "coral": "FF8B5C",
    "acid": "DDEB79", "red": "FF857E",
}


def inch(value: float) -> int:
    return int(round(value * EMU))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xml_decl(body: str) -> bytes:
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + body).encode("utf-8")


def load_story() -> dict[str, Any]:
    text = SOURCE.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError(f"missing fenced JSON story in {SOURCE}")
    story = json.loads(match.group(1))
    slides = story.get("slides", [])
    if len(slides) != 4:
        raise ValueError("four-slide source must contain exactly four slides")
    if [s.get("id") for s in slides] != ["opportunity", "mechanism", "evidence", "decision"]:
        raise ValueError("four-slide source order must be opportunity/mechanism/evidence/decision")
    return story


def group_root() -> str:
    return (
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    )


@dataclass
class Element:
    kind: str
    name: str
    x: float
    y: float
    w: float
    h: float
    options: dict[str, Any] = field(default_factory=dict)


class Slide:
    def __init__(self, number: int, story: dict[str, Any], deck_label: str, status_label: str):
        self.number = number
        self.story = story
        self.deck_label = deck_label
        self.status_label = status_label
        self.elements: list[Element] = []
        self.next_id = 2
        self._base()

    def _id(self) -> int:
        value = self.next_id
        self.next_id += 1
        return value

    def rect(self, x: float, y: float, w: float, h: float, fill: str, *,
             line: str | None = None, line_width: float = .75, line_alpha: int = 100000,
             radius: float = 0.0, name: str = "Shape", fill_alpha: int = 100000) -> None:
        self.elements.append(Element("rect", name, x, y, w, h, {
            "fill": fill, "line": line, "line_width": line_width, "line_alpha": line_alpha,
            "radius": radius, "fill_alpha": fill_alpha,
        }))

    def text(self, x: float, y: float, w: float, h: float, lines: str | list[str], *,
             size: float, color: str = C["ink"], bold: bool = False, align: str = "l",
             valign: str = "t", name: str = "Text", tracking: float = 0,
             line_spacing: int = 100000) -> None:
        if isinstance(lines, str):
            lines = [lines]
        self.elements.append(Element("text", name, x, y, w, h, {
            "lines": lines, "size": size, "color": color, "bold": bold, "align": align,
            "valign": valign, "tracking": tracking, "line_spacing": line_spacing,
        }))

    def connector(self, x1: float, y1: float, x2: float, y2: float, *,
                  color: str = C["teal"], width: float = 2.0, arrow: bool = True,
                  dash: bool = False, name: str = "Connector") -> None:
        self.elements.append(Element("line", name, min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1), {
            "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color,
            "width": width, "arrow": arrow, "dash": dash,
        }))

    def _base(self) -> None:
        self.rect(0, 0, SLIDE_W, SLIDE_H, C["night"], name="Background")
        self.text(.72, .30, 3.2, .25, self.deck_label, size=10.5, color=C["teal"], bold=True,
                  tracking=1.1, name="Deck label")
        self.text(10.15, .30, 1.85, .25, self.status_label, size=9.5, color=C["muted"], bold=True,
                  tracking=.8, align="r", name="Status label")
        self.text(12.12, .30, .49, .25, f"{self.number:02d}/04", size=9.5, color=C["quiet"], bold=True,
                  align="r", name="Slide number")
        self.connector(9.82, .43, 10.03, .43, color=C["line"], width=.75, arrow=False, name="Header separator")
        self.text(.72, .65, 3.5, .24, self.story["eyebrow"], size=10.5, color=C["coral"], bold=True,
                  tracking=1.0, name="Eyebrow")

    def add_footer(self) -> None:
        self.connector(.72, 6.96, 12.61, 6.96, color=C["line"], width=.75, arrow=False,
                       name="Footer separator")
        self.text(.72, 7.06, 11.89, .22, self.story["footer"], size=9.5, color=C["quiet"],
                  name="Source footer")

    def _run_xml(self, text: str, size: float, color: str, bold: bool, tracking: float) -> str:
        b = ' b="1"' if bold else ""
        spc = f' spc="{int(round(tracking * 100))}"' if tracking else ""
        sz = int(round(size * 100))
        return (
            f'<a:r><a:rPr lang="en-US" sz="{sz}"{b}{spc} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Arial"/>'
            f'</a:rPr><a:t>{escape(text)}</a:t></a:r>'
        )

    def _para_xml(self, text: str, opts: dict[str, Any]) -> str:
        size = opts["size"]
        return (
            f'<a:p><a:pPr algn="{opts["align"]}" marL="0" indent="0">'
            f'<a:lnSpc><a:spcPct val="{opts["line_spacing"]}"/></a:lnSpc>'
            '<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft>'
            '<a:buNone/></a:pPr>'
            f'{self._run_xml(text, size, opts["color"], opts["bold"], opts["tracking"])}'
            f'<a:endParaRPr lang="en-US" sz="{int(round(size*100))}"/></a:p>'
        )

    def _rect_xml(self, element: Element) -> str:
        sid = self._id(); o = element.options
        geom = "roundRect" if o["radius"] else "rect"
        av = '<a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst>' if o["radius"] else '<a:avLst/>'
        fill_alpha = f'<a:alpha val="{o["fill_alpha"]}"/>' if o["fill_alpha"] != 100000 else ""
        if o["line"]:
            line_alpha = f'<a:alpha val="{o["line_alpha"]}"/>' if o["line_alpha"] != 100000 else ""
            line = (
                f'<a:ln w="{int(round(o["line_width"]*12700))}"><a:solidFill>'
                f'<a:srgbClr val="{o["line"]}">{line_alpha}</a:srgbClr></a:solidFill>'
                '<a:prstDash val="solid"/></a:ln>'
            )
        else:
            line = '<a:ln><a:noFill/></a:ln>'
        return (
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name={quoteattr(element.name)}/>'
            '<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{inch(element.x)}" y="{inch(element.y)}"/>'
            f'<a:ext cx="{inch(element.w)}" cy="{inch(element.h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}">{av}</a:prstGeom><a:solidFill>'
            f'<a:srgbClr val="{o["fill"]}">{fill_alpha}</a:srgbClr></a:solidFill>{line}</p:spPr>'
            '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>'
        )

    def _text_xml(self, element: Element) -> str:
        sid = self._id(); o = element.options
        return (
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name={quoteattr(element.name)}/>'
            '<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{inch(element.x)}" y="{inch(element.y)}"/>'
            f'<a:ext cx="{inch(element.w)}" cy="{inch(element.h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln>'
            f'</p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{o["valign"]}"/>'
            f'<a:lstStyle/>{"".join(self._para_xml(line, o) for line in o["lines"])}</p:txBody></p:sp>'
        )

    def _line_xml(self, element: Element) -> str:
        sid = self._id(); o = element.options
        x1, y1, x2, y2 = o["x1"], o["y1"], o["x2"], o["y2"]
        flip_h = ' flipH="1"' if x2 < x1 else ""
        flip_v = ' flipV="1"' if y2 < y1 else ""
        dash = "dash" if o["dash"] else "solid"
        tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if o["arrow"] else '<a:tailEnd type="none"/>'
        return (
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name={quoteattr(element.name)}/>'
            '<p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr>'
            f'<a:xfrm{flip_h}{flip_v}><a:off x="{inch(min(x1,x2))}" y="{inch(min(y1,y2))}"/>'
            f'<a:ext cx="{inch(abs(x2-x1))}" cy="{inch(abs(y2-y1))}"/></a:xfrm>'
            '<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{int(round(o["width"]*12700))}" cap="round"><a:solidFill>'
            f'<a:srgbClr val="{o["color"]}"/></a:solidFill><a:prstDash val="{dash}"/>'
            f'<a:round/><a:headEnd type="none"/>{tail}</a:ln></p:spPr></p:cxnSp>'
        )

    def slide_xml(self) -> bytes:
        items = []
        for element in self.elements:
            if element.kind == "rect": items.append(self._rect_xml(element))
            elif element.kind == "text": items.append(self._text_xml(element))
            else: items.append(self._line_xml(element))
        title = " ".join(self.story["headline"])
        return xml_decl(
            f'<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" showMasterSp="0">'
            f'<p:cSld name={quoteattr(f"Slide {self.number}: {title}")}><p:bg><p:bgPr><a:solidFill>'
            f'<a:srgbClr val="{C["night"]}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>'
            + group_root() + "".join(items) +
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
        )

    def rels_xml(self) -> bytes:
        return relationships([
            ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml"),
            ("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide", f"../notesSlides/notesSlide{self.number}.xml"),
        ])

    def svg(self) -> str:
        rendered = []
        for element in self.elements:
            o = element.options
            if element.kind == "rect":
                stroke = f'#{o["line"]}' if o["line"] else "none"
                stroke_opacity = o["line_alpha"] / 100000
                fill_opacity = o["fill_alpha"] / 100000
                rendered.append(
                    f'<rect x="{element.x}" y="{element.y}" width="{element.w}" height="{element.h}" '
                    f'rx="{o["radius"]}" fill="#{o["fill"]}" fill-opacity="{fill_opacity:.3f}" '
                    f'stroke="{stroke}" stroke-opacity="{stroke_opacity:.3f}" stroke-width="{o["line_width"]/72:.4f}"/>'
                )
            elif element.kind == "line":
                marker = f' marker-end="url(#arrow-{o["color"].lower()})"' if o["arrow"] else ""
                dash = ' stroke-dasharray="0.07 0.055"' if o["dash"] else ""
                rendered.append(
                    f'<line x1="{o["x1"]}" y1="{o["y1"]}" x2="{o["x2"]}" y2="{o["y2"]}" '
                    f'stroke="#{o["color"]}" stroke-width="{o["width"]/72:.4f}" stroke-linecap="round"{dash}{marker}/>'
                )
            else:
                size_u = o["size"] / 72
                line_u = size_u * o["line_spacing"] / 100000
                count = len(o["lines"])
                total = count * line_u
                if o["valign"] == "ctr": start_y = element.y + (element.h-total)/2 + size_u*.82
                elif o["valign"] == "b": start_y = element.y + element.h-total + size_u*.82
                else: start_y = element.y + size_u*.82
                if o["align"] == "ctr": tx, anchor = element.x + element.w/2, "middle"
                elif o["align"] == "r": tx, anchor = element.x + element.w, "end"
                else: tx, anchor = element.x, "start"
                tspans = "".join(
                    f'<tspan x="{tx}" y="{start_y+i*line_u}">{html.escape(line)}</tspan>'
                    for i, line in enumerate(o["lines"])
                )
                rendered.append(
                    f'<text text-anchor="{anchor}" fill="#{o["color"]}" font-family="Arial, sans-serif" '
                    f'font-size="{size_u}" font-weight="{"700" if o["bold"] else "400"}" '
                    f'letter-spacing="{o["tracking"]/72}">{tspans}</text>'
                )
        markers = "".join(
            f'<marker id="arrow-{color.lower()}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="#{color}"/></marker>'
            for color in (C["teal"], C["coral"], C["acid"])
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SLIDE_W} {SLIDE_H}" width="1920" height="1080" role="img">'
            f'<defs>{markers}</defs>' + "".join(rendered) + '</svg>'
        )


def node(slide: Slide, x: float, y: float, w: float, h: float, label: str, *,
         accent: str = C["teal"], dominant: bool = False, name: str) -> None:
    fill = C["surface2"] if dominant else C["surface"]
    slide.rect(x, y, w, h, fill, line=accent, line_width=1.5 if dominant else .75,
               line_alpha=100000 if dominant else 45000, radius=.13, name=f"{name} shape")
    if " / " in label:
        label_lines = [part.strip() for part in label.split(" / ")]
    elif len(label.split()) == 2:
        label_lines = label.split()
    else:
        label_lines = [label]
    slide.text(x+.12, y+.08, w-.24, h-.16, label_lines,
               size=17 if dominant else 14, color=C["ink"], bold=True, align="ctr", valign="ctr",
               line_spacing=92000, name=f"{name} label")


def build_slide_1(slide: Slide) -> None:
    s = slide.story
    slide.text(.72, .96, 7.20, 1.42, s["headline"], size=42, bold=True, line_spacing=94000,
               name="Title")
    slide.text(.74, 2.72, 6.55, 1.05, s["premise"], size=19, color=C["muted"],
               line_spacing=112000, name="Premise")
    slide.connector(7.68, 1.32, 7.68, 5.82, color=C["line"], width=.75, arrow=False,
                    name="Editorial divider")
    node(slide, 8.02, 1.82, 1.48, .82, s["contexts"][0], name="Retail context")
    node(slide, 8.02, 4.26, 1.48, .82, s["contexts"][1], name="Field context")
    node(slide, 10.02, 3.02, 1.30, .94, s["command"], accent=C["acid"], dominant=True,
         name="Quiet command")
    node(slide, 11.45, 3.02, 1.16, .94, s["assistant"], name="Existing assistant")
    slide.connector(9.50, 2.23, 10.02, 3.34, name="Retail to command")
    slide.connector(9.50, 4.67, 10.02, 3.64, name="Field to command")
    slide.connector(11.32, 3.49, 11.45, 3.49, color=C["acid"], name="Command to assistant")
    slide.add_footer()


def build_slide_2(slide: Slide) -> None:
    s = slide.story
    slide.text(.72, .96, 9.80, 1.38, s["headline"], size=42, bold=True, line_spacing=94000,
               name="Title")
    xs = [.72, 2.78, 4.84, 6.98, 10.10]
    widths = [1.64, 1.64, 1.72, 2.60, 1.78]
    for i, (x, w, label) in enumerate(zip(xs, widths, s["nodes"])):
        node(slide, x, 2.92 if i != 3 else 2.72, w, 1.10 if i != 3 else 1.50, label,
             accent=C["acid"] if i == 3 else C["teal"], dominant=i == 3, name=f"Flow node {i+1}")
    centers = [(xs[i]+widths[i], 3.47) for i in range(3)]
    starts = [(xs[i+1], 3.47) for i in range(3)]
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(centers, starts), 1):
        slide.connector(x1+.06, y1, x2-.06, y2, name=f"Flow connector {i}")
    slide.connector(xs[3]+widths[3]+.06, 3.47, xs[4]-.06, 3.47, color=C["acid"],
                    name="Confirmed handoff connector")
    # Repair loop: down, back, then up into candidates.
    slide.connector(8.28, 4.22, 8.28, 4.68, color=C["coral"], arrow=False, name="Repair loop down")
    slide.connector(8.28, 4.68, 5.70, 4.68, color=C["coral"], arrow=False, name="Repair loop back")
    slide.connector(5.70, 4.68, 5.70, 4.04, color=C["coral"], name="Repair loop return")
    slide.text(6.02, 4.47, 1.90, .28, s["repair"], size=10.5, color=C["coral"], bold=True,
               tracking=.5, align="ctr", name="Repair label")
    slide.connector(.72, 5.38, 6.62, 5.38, color=C["coral"], width=1.5, arrow=False, dash=True,
                    name="Raw signal boundary")
    slide.text(.72, 5.52, 2.85, .25, s["raw_boundary"], size=10.5, color=C["coral"], bold=True,
               tracking=.5, name="Raw boundary label")
    slide.text(.72, 6.12, 11.89, .32, s["qualifier"], size=13, color=C["muted"],
               name="Architecture qualifier")
    slide.add_footer()


def build_slide_3(slide: Slide) -> None:
    s = slide.story; chart = s["chart"]
    slide.text(.72, .96, 11.89, 1.38, s["headline"], size=42, bold=True, line_spacing=94000,
               name="Title")
    baseline, plot_h = 5.92, 3.20
    slide.connector(1.05, baseline, 6.98, baseline, color=C["line"], width=1.0, arrow=False,
                    name="Chart baseline")
    bars = [
        (1.44, chart["global_height"], chart["global_value"], chart["global_label"], C["teal"], "Global"),
        (4.35, chart["held_height"], chart["held_value"], chart["held_label"], C["coral"], "Held-out"),
    ]
    for x, value, value_text, label, color, key in bars:
        h = plot_h * value / 100
        y = baseline - h
        slide.rect(x, y, 1.48, h, color, radius=.10, fill_alpha=90000, name=f"Chart bar {key}")
        slide.text(x-.25, y-.58, 1.98, .45, value_text, size=26, color=color, bold=True,
                   align="ctr", name=f"Chart value {key}")
        slide.text(x-.18, baseline+.17, 1.84, .27, label, size=10.5, color=C["muted"], bold=True,
                   tracking=.5, align="ctr", name=f"Chart label {key}")
    slide.connector(3.13, 3.58, 4.02, 3.98, color=C["acid"], width=1.5, arrow=False, dash=True,
                    name="Chart gap annotation")
    slide.text(2.90, 4.06, 1.58, .30, chart["gap"], size=11, color=C["acid"], bold=True,
               align="ctr", name="Chart gap label")
    slide.connector(7.58, 2.60, 7.58, 6.12, color=C["line"], width=.75, arrow=False,
                    name="Evidence divider")
    slide.text(8.00, 2.68, 3.20, .28, s["proof_title"], size=11, color=C["teal"], bold=True,
               tracking=.8, name="Proof title")
    for i, proof in enumerate(s["proofs"]):
        y = 3.28 + i*.88
        slide.connector(8.00, y+.13, 8.30, y+.13, color=C["coral"] if i == 0 else C["teal"],
                        width=2.25, arrow=False, name=f"Proof rule {i+1}")
        slide.text(8.48, y-.02, 3.70, .35, proof, size=17, color=C["ink"], bold=True,
                   name=f"Proof item {i+1}")
    slide.text(.72, 6.48, 11.89, .42, s["caption"], size=10.5, color=C["muted"],
               name="Evidence caption")
    slide.add_footer()


def build_slide_4(slide: Slide) -> None:
    s = slide.story
    slide.text(.72, .96, 11.89, 1.30, s["headline"], size=42, bold=True, line_spacing=94000,
               name="Title")
    slide.rect(.72, 2.42, 5.10, 3.82, C["surface"], line=C["coral"], line_width=1.5,
               line_alpha=70000, radius=.16, name="Decision amount panel")
    slide.text(1.04, 2.78, 4.46, .28, s["pilot_label"], size=11, color=C["coral"], bold=True,
               tracking=.8, align="ctr", name="Pilot label")
    amount_lines = s["amount"].split(" ", 1)
    slide.text(1.02, 3.18, 4.50, 1.48, amount_lines, size=62, color=C["coral"], bold=True,
               align="ctr", valign="ctr", line_spacing=88000, name="Pilot amount")
    slide.text(1.02, 5.28, 4.50, .65, s["boundary"], size=13, color=C["muted"],
               align="ctr", line_spacing=110000, name="Pilot boundary")
    # Three-phase evidence spine ending in a decision block.
    slide.connector(6.50, 3.42, 11.02, 3.42, color=C["teal"], width=2.0, arrow=False,
                    name="Decision spine")
    phase_xs = [6.66, 8.16, 9.66]
    for i, (x, label) in enumerate(zip(phase_xs, s["phases"])):
        slide.rect(x-.13, 3.29, .26, .26, C["night"], line=C["teal"], line_width=2.0,
                   radius=.13, name=f"Phase marker {i+1}")
        slide.text(x-.62, 3.78, 1.24, .55, label.split(" ", 1), size=13.5, color=C["ink"], bold=True,
                   align="ctr", line_spacing=92000, name=f"Phase label {i+1}")
    slide.connector(10.02, 3.42, 10.56, 3.42, color=C["acid"], width=2.0,
                    name="Decision output connector")
    slide.rect(10.62, 2.85, 1.99, 1.20, C["surface2"], line=C["acid"], line_width=1.5,
               radius=.14, name="Decision output shape")
    slide.text(10.78, 2.98, 1.67, .94, ["GO / CHANGE", "/ STOP"], size=17, color=C["acid"], bold=True,
               align="ctr", valign="ctr", line_spacing=92000, name="Decision output label")
    for i, (x, label) in enumerate(zip([6.32, 8.43, 10.54], s["asks"])):
        slide.connector(x, 5.33, x+.26, 5.33, color=C["coral"], width=2.25, arrow=False,
                        name=f"Ask rule {i+1}")
        slide.text(x+.36, 5.16, 1.55, .42, label.split(" ", 1), size=10.5, color=C["muted"], bold=True,
                   line_spacing=92000, name=f"Ask label {i+1}")
    slide.add_footer()


def build_slides(story: dict[str, Any]) -> list[Slide]:
    slides = [Slide(i, item, story["deck_label"], story["status_label"])
              for i, item in enumerate(story["slides"], 1)]
    for builder, slide in zip((build_slide_1, build_slide_2, build_slide_3, build_slide_4), slides):
        builder(slide)
    return slides


def relationships(items: list[tuple[str, str, str]]) -> bytes:
    body = "".join(f'<Relationship Id="{rid}" Type="{typ}" Target={quoteattr(target)}/>' for rid, typ, target in items)
    return xml_decl(f'<Relationships xmlns="{REL}">{body}</Relationships>')


def notes_slide_xml(number: int, lines: list[str]) -> bytes:
    paras = []
    for line in lines:
        heading = line in {"ROLE", "TALK TRACK", "BOUNDARY", "SOURCE", "SOURCES"}
        size, color, bold = (1100, C["teal"], True) if heading else (1150, "222222", False)
        before, after = (320, 120) if heading else (0, 120)
        paras.append(
            f'<a:p><a:pPr algn="l" marL="0" indent="0"><a:spcBef><a:spcPts val="{before}"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="{after}"/></a:spcAft><a:buNone/></a:pPr>'
            f'<a:r><a:rPr lang="en-US" sz="{size}"{" b=\"1\"" if bold else ""} dirty="0"><a:solidFill>'
            f'<a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>{escape(line)}</a:t></a:r>'
            f'<a:endParaRPr lang="en-US" sz="{size}"/></a:p>'
        )
    body_shape = (
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Text Placeholder 1"/><p:cNvSpPr txBox="1"/>'
        '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr>'
        f'<a:xfrm><a:off x="{inch(.65)}" y="{inch(.65)}"/><a:ext cx="{inch(6.2)}" cy="{inch(8.3)}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="91440" rIns="91440" bIns="91440"/>'
        '<a:lstStyle/>' + "".join(paras) + '</p:txBody></p:sp>'
    )
    return xml_decl(
        f'<p:notes xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld name="Slide {number} presenter notes">'
        f'<p:spTree>{group_root()}{body_shape}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
    )


def theme_xml() -> bytes:
    return xml_decl(f'''<a:theme xmlns:a="{NS_A}" name="Quiet Channel Executive"><a:themeElements><a:clrScheme name="Quiet Channel"><a:dk1><a:srgbClr val="{C['night']}"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="{C['surface']}"/></a:dk2><a:lt2><a:srgbClr val="{C['ink']}"/></a:lt2><a:accent1><a:srgbClr val="{C['teal']}"/></a:accent1><a:accent2><a:srgbClr val="{C['coral']}"/></a:accent2><a:accent3><a:srgbClr val="{C['acid']}"/></a:accent3><a:accent4><a:srgbClr val="93B9FF"/></a:accent4><a:accent5><a:srgbClr val="{C['red']}"/></a:accent5><a:accent6><a:srgbClr val="858B85"/></a:accent6><a:hlink><a:srgbClr val="5CD3BD"/></a:hlink><a:folHlink><a:srgbClr val="FF8B5C"/></a:folHlink></a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Quiet Channel"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="accent1"/></a:solidFill><a:solidFill><a:schemeClr val="accent2"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="dk1"/></a:solidFill><a:solidFill><a:schemeClr val="dk2"/></a:solidFill><a:solidFill><a:schemeClr val="lt1"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>''')


def master_xml(kind: str) -> bytes:
    if kind == "slide":
        return xml_decl(f'<p:sldMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" preserve="1"><p:cSld name="Quiet Channel Master"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="dk1" bg2="dk2" folHlink="folHlink" hlink="hlink" tx1="lt1" tx2="lt2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr algn="l"><a:defRPr sz="4200" b="1"/></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr marL="0" indent="0"><a:defRPr sz="1600"/></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:otherStyle></p:txStyles></p:sldMaster>')
    return xml_decl(f'<p:notesMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld name="Quiet Channel Notes Master"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:hf hdr="0" ftr="0" dt="0" sldNum="0"/><p:notesStyle><a:lvl1pPr marL="0" indent="0"><a:defRPr sz="1150"/></a:lvl1pPr></p:notesStyle></p:notesMaster>')


def package_parts(story: dict[str, Any], slides: list[Slide]) -> dict[str, bytes]:
    parts: dict[str, bytes] = {}
    overrides = [
        ("/ppt/presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
        ("/ppt/slideMasters/slideMaster1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"),
        ("/ppt/slideLayouts/slideLayout1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"),
        ("/ppt/notesMasters/notesMaster1.xml", "application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"),
        ("/ppt/theme/theme1.xml", "application/vnd.openxmlformats-officedocument.theme+xml"),
        ("/ppt/presProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"),
        ("/ppt/viewProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"),
        ("/ppt/tableStyles.xml", "application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"),
        ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
        ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml"),
    ]
    for i in range(1, 5):
        overrides.extend([
            (f"/ppt/slides/slide{i}.xml", "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"),
            (f"/ppt/notesSlides/notesSlide{i}.xml", "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"),
        ])
    ct_body = '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' + "".join(f'<Override PartName="{p}" ContentType="{t}"/>' for p, t in overrides)
    parts["[Content_Types].xml"] = xml_decl(f'<Types xmlns="{CT}">{ct_body}</Types>')
    parts["_rels/.rels"] = relationships([
        ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "ppt/presentation.xml"),
        ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
        ("rId3", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", "docProps/app.xml"),
    ])
    parts["docProps/core.xml"] = xml_decl('<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Quiet Channel — Four-Slide Executive Decision Deck</dc:title><dc:subject>Evidence-gated silent command research proposal</dc:subject><dc:creator>Silent Speech Technology project</dc:creator><cp:keywords>silent speech; concept; simulated; evidence; e&amp;</cp:keywords><dc:description>Deterministic editable executive deck. No product-performance claim.</dc:description><cp:lastModifiedBy>Standard-library OOXML builder</cp:lastModifiedBy><cp:revision>2</cp:revision><dcterms:created xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:modified></cp:coreProperties>')
    titles = "".join(f'<vt:lpstr>{escape(" ".join(s["headline"]))}</vt:lpstr>' for s in story["slides"])
    parts["docProps/app.xml"] = xml_decl(f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Python Standard Library OOXML Builder</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>4</Slides><Notes>4</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips><ScaleCrop>false</ScaleCrop><HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Slide Titles</vt:lpstr></vt:variant><vt:variant><vt:i4>4</vt:i4></vt:variant></vt:vector></HeadingPairs><TitlesOfParts><vt:vector size="4" baseType="lpstr">{titles}</vt:vector></TitlesOfParts><Company>Silent Speech Technology project</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>')
    sld_ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{2+i}"/>' for i in range(1, 5))
    parts["ppt/presentation.xml"] = xml_decl(f'<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst><p:sldIdLst>{sld_ids}</p:sldIdLst><p:sldSz cx="{SW}" cy="{SH}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle></p:presentation>')
    pres_rels = [
        ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "slideMasters/slideMaster1.xml"),
        ("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster", "notesMasters/notesMaster1.xml"),
    ] + [(f"rId{2+i}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"slides/slide{i}.xml") for i in range(1, 5)] + [
        ("rId7", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps", "presProps.xml"),
        ("rId8", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps", "viewProps.xml"),
        ("rId9", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "theme/theme1.xml"),
        ("rId10", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles", "tableStyles.xml"),
    ]
    parts["ppt/_rels/presentation.xml.rels"] = relationships(pres_rels)
    parts["ppt/theme/theme1.xml"] = theme_xml()
    parts["ppt/slideMasters/slideMaster1.xml"] = master_xml("slide")
    parts["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = relationships([
        ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml"),
        ("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "../theme/theme1.xml"),
    ])
    parts["ppt/slideLayouts/slideLayout1.xml"] = xml_decl(f'<p:sldLayout xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
    parts["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = relationships([("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "../slideMasters/slideMaster1.xml")])
    parts["ppt/notesMasters/notesMaster1.xml"] = master_xml("notes")
    parts["ppt/notesMasters/_rels/notesMaster1.xml.rels"] = relationships([("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "../theme/theme1.xml")])
    parts["ppt/presProps.xml"] = xml_decl(f'<p:presentationPr xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"/>')
    parts["ppt/viewProps.xml"] = xml_decl(f'<p:viewPr xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" lastView="sldView"><p:normalViewPr/><p:slideViewPr><p:cSldViewPr snapToGrid="1" snapToObjects="1"/></p:slideViewPr><p:notesTextViewPr><p:cViewPr varScale="1"><p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale><p:origin x="0" y="0"/></p:cViewPr></p:notesTextViewPr><p:gridSpacing cx="109728" cy="109728"/></p:viewPr>')
    parts["ppt/tableStyles.xml"] = xml_decl(f'<a:tblStyleLst xmlns:a="{NS_A}" def="{{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}}"/>')
    for i, (slide, source_slide) in enumerate(zip(slides, story["slides"]), 1):
        parts[f"ppt/slides/slide{i}.xml"] = slide.slide_xml()
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = slide.rels_xml()
        parts[f"ppt/notesSlides/notesSlide{i}.xml"] = notes_slide_xml(i, source_slide["notes"])
        parts[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = relationships([
            ("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster", "../notesMasters/notesMaster1.xml"),
            ("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"../slides/slide{i}.xml"),
        ])
    return parts


def write_zip(parts: dict[str, bytes], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for name in sorted(parts):
            info = ZipInfo(name, FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zf.writestr(info, parts[name], compress_type=ZIP_DEFLATED, compresslevel=9)


def write_evidence(output: Path, evidence: Path, parts: dict[str, bytes]) -> None:
    payload = {
        "artifact": output.name,
        "sha256": sha256(output.read_bytes()),
        "bytes": output.stat().st_size,
        "zip_parts": len(parts),
        "slides": 4,
        "notes_slides": 4,
        "media": [],
        "builder": "pitch/build_4_slide_pptx.py",
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "source": "pitch/deck-4-slide.md",
        "source_markdown_sha256": sha256(SOURCE.read_bytes()),
        "deterministic_zip_timestamp": "1980-01-01T00:00:00",
        "runtime_dependencies": "Python standard library only",
        "visual_qa": "Representative SVG/Chromium preview only; exact PowerPoint rehearsal still required",
    }
    evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_previews(slides: list[Slide], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for i, slide in enumerate(slides, 1):
        (directory / f"slide-{i}.svg").write_text(slide.svg(), encoding="utf-8")
    single = "".join(f'<a href="slide-{i}.svg"><img src="slide-{i}.svg" alt="Representative slide {i}"></a>' for i in range(1, 5))
    (directory / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Representative four-slide geometry QA</title>'
        '<style>html,body{margin:0;background:#080d0b;color:#fff;font-family:Arial,sans-serif}'
        'body{display:grid;gap:24px;padding:24px}img{display:block;width:100%;height:auto;box-shadow:0 8px 30px #0008}'
        'a{display:block}</style>' + single, encoding="utf-8")
    contact = "".join(f'<img src="slide-{i}.svg" alt="Representative slide {i}">' for i in range(1, 5))
    (directory / "contact-sheet.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Representative four-up geometry QA</title>'
        '<style>html,body{width:1920px;height:1080px;margin:0;overflow:hidden;background:#080d0b}'
        'body{box-sizing:border-box;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;'
        'gap:24px;padding:24px}img{display:block;max-width:100%;max-height:100%;margin:auto;box-shadow:0 5px 20px #000a}</style>'
        + contact, encoding="utf-8")
    (directory / "README.txt").write_text(
        "Representative geometry-matched SVG/Chromium QA only. Not exact PowerPoint rendering.\n",
        encoding="utf-8")
    print(f"wrote representative previews to {directory}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--no-evidence", action="store_true")
    parser.add_argument("--preview-dir", type=Path)
    args = parser.parse_args()
    story = load_story()
    slides = build_slides(story)
    parts = package_parts(story, slides)
    write_zip(parts, args.output)
    if not args.no_evidence:
        write_evidence(args.output, args.evidence, parts)
    if args.preview_dir:
        write_previews(slides, args.preview_dir)
    print(f"built {args.output} ({args.output.stat().st_size} bytes, sha256={sha256(args.output.read_bytes())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

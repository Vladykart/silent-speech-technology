#!/usr/bin/env python3
"""Build the editable Quiet Channel Lab PPTX with Python's standard library only.

The package is intentionally simple: native DrawingML text/shapes plus the four
project-authored SVGs already catalogued in provenance/media-catalogue.md.
No network, office suite, third-party package, or template is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "quiet-channel-4-slide-deck.pptx"
DEFAULT_EVIDENCE = ROOT / "quiet-channel-4-slide-build.json"
EMU = 914400
SW, SH = 12192000, 6858000
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)

C = {
    "night": "101816", "panel": "1C2925", "panel2": "22342E", "line": "53665F",
    "ink": "F4F0E6", "muted": "B8B7AD", "quiet": "858B85", "teal": "5CD3BD",
    "orange": "FF8B5C", "acid": "DDEB79", "red": "FF857E", "warm": "2A211E",
}

SLIDES = [
    ("The opportunity", "THE QUIET CHANNEL", "Concept proposal · e& frontline retail advisors and field technicians · C04–C06, H01."),
    ("How it works", "A fixed command channel—with a human gate", "Proposed architecture; no physical prototype, model, or project performance · C05, C19, C21–C23."),
    ("Evidence, differentiation & privacy", "Published signals. Explicit boundaries.", "External evidence only · R03–R04, R21, R26, R28, R30, R32–R33, R38–R40."),
    ("The 90-day pilot decision", "Buy evidence before deployment", "Captain decision · AED 1,000,000 applies only to the fixed-fee pilot · H02–H03."),
]

NOTES = [
    "TALK TRACK\nThe Quiet Channel is a privacy-first silent command interface concept for e& frontline retail advisors and field technicians. It is a research proposition, not finished hardware, a customer claim, or a working physical prototype.\nBOUNDARY\nOne low-consequence workflow must still be selected and compared with touch, voice, and existing controls.\nSOURCE\nresearch/claim-ledger.md C04–C06; provenance/decisions.md H01.",
    "TALK TRACK\nA wearable surface-EMG concept maps deliberate muscle activity into one of 12 fixed commands. Decode is proposed on device; low confidence abstains, and every consequential handoff requires confirm or repair before the existing agent/CRM receives text.\nBOUNDARY\nNot open-vocabulary transcription, mind reading, autonomous billing changes, or implemented hardware. The 12-command grammar is proposed pilot scope, not measured performance.\nSOURCE\nresearch/claim-boundary.md; research/claim-ledger.md C05, C19, C21–C23.",
    "TALK TRACK\nSeparate evidence types and conditions. SilentWear is a preprint with four participants; Gaddy and Klein are peer-reviewed facial-sEMG speech studies. Gesture, optical/contactless, acoustic/IMU, and implanted systems answer different questions. Privacy is a governed flow, not a no-microphone slogan.\nBOUNDARY\nRaw signals staying on device is an in-use design requirement, not an implemented security claim. Decoded text remains personal data. Calibration needs explicit opt-in and may require separately consented paired audio. No emotion or medical inference is produced.\nSOURCES\nR03–R04; R11; R21; R26; R28; R30; R32–R33; R38–R40; claim-ledger C07, C18–C20, C27.",
    "TALK TRACK\nThe decision is a fixed-fee 90-day evidence programme with explicit go, change, and stop gates. e& is the selected beachhead, not a claimed customer. A separate deployment decision follows pilot evidence.\nBOUNDARY\nAED 1,000,000 is only the pilot fee. Per-seat deployment pricing is TBD. Strategic funding, negotiated IP/data rights, and acquisition or exit remain optional upside with no invented amounts.\nSOURCE\nprovenance/decisions.md H01–H03; research/claim-ledger.md C29.",
]


def inch(value: float) -> int:
    return int(round(value * EMU))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xml_decl(body: str) -> bytes:
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + body).encode("utf-8")


def group_root() -> str:
    return (
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    )


def run_xml(text: str, size: int, color: str, bold: bool = False, font: str = "Arial") -> str:
    b = ' b="1"' if bold else ""
    return (
        f'<a:r><a:rPr lang="en-US" sz="{size}"{b} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{escape(font)}"/>'
        f'</a:rPr><a:t>{escape(text)}</a:t></a:r>'
    )


def para_xml(text: str, size: int = 1800, color: str = C["ink"], bold: bool = False,
             align: str = "l", before: int = 0, after: int = 0) -> str:
    return (
        f'<a:p><a:pPr algn="{align}" marL="0" indent="0"><a:spcBef><a:spcPts val="{before}"/>'
        f'</a:spcBef><a:spcAft><a:spcPts val="{after}"/></a:spcAft><a:buNone/></a:pPr>'
        f'{run_xml(text, size, color, bold)}<a:endParaRPr lang="en-US" sz="{size}"/></a:p>'
    )


class Slide:
    def __init__(self, number: int, title: str, subtitle: str, source: str):
        self.number, self.title, self.subtitle, self.source = number, title, subtitle, source
        self.items: list[str] = []
        self.rels: list[tuple[str, str, str]] = []
        self.next_id = 2
        self._base()

    def _id(self) -> int:
        value = self.next_id; self.next_id += 1; return value

    def _base(self) -> None:
        self.rect(0, 0, 13.333, 7.5, C["night"], C["night"], radius=False, name="Background")
        self.rect(0, 0, 13.333, .045, C["orange"], C["orange"], radius=False, name="Accent line")
        self.text(.45, .20, 5.6, .32, [para_xml("QUIET CHANNEL LAB", 900, C["teal"], True)], name="Brand")
        self.text(11.55, .20, 1.3, .32, [para_xml(f"{self.number:02d} / 04", 850, C["muted"], True, "r")], name="Slide number")
        self.text(.62, .76, 12.0, .82, [para_xml(self.title, 2850 if self.number != 1 else 3200, C["ink"], True)], name="Title")
        if self.subtitle:
            self.text(.65, 1.55, 11.7, .58, [para_xml(self.subtitle, 1280, C["muted"])], name="Subtitle")

    def rect(self, x: float, y: float, w: float, h: float, fill: str, line: str,
             radius: bool = True, name: str = "Shape", alpha: int | None = None) -> None:
        sid = self._id(); alpha_xml = f'<a:alpha val="{alpha}"/>' if alpha is not None else ""
        prst = "roundRect" if radius else "rect"
        self.items.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name={quoteattr(name)}/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}">{alpha_xml}</a:srgbClr></a:solidFill>'
            f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln></p:spPr>'
            '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>'
        )

    def text(self, x: float, y: float, w: float, h: float, paras: list[str], name: str = "Text",
             margin: int = 0, valign: str = "t") -> None:
        sid = self._id()
        self.items.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name={quoteattr(name)}/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{margin}" tIns="{margin}" rIns="{margin}" bIns="{margin}" anchor="{valign}"/>'
            f'<a:lstStyle/>{"".join(paras)}</p:txBody></p:sp>'
        )

    def card(self, x: float, y: float, w: float, h: float, label: str, title: str, body: str,
             accent: str = C["teal"], fill: str = C["panel"]) -> None:
        self.rect(x, y, w, h, fill, C["line"], name=f"Card {title}")
        self.rect(x, y, .06, h, accent, accent, radius=False, name=f"Card accent {title}")
        self.text(x + .18, y + .15, w - .34, .28, [para_xml(label.upper(), 680, accent, True)], name=f"Label {title}")
        self.text(x + .18, y + .48, w - .34, .38, [para_xml(title, 1250, C["ink"], True)], name=f"Card title {title}")
        self.text(x + .18, y + .93, w - .34, h - 1.02, [para_xml(body, 900, C["muted"])], name=f"Card body {title}")

    def image(self, asset: str, x: float, y: float, w: float, h: float, descr: str) -> None:
        rid = f"rId{len(self.rels) + 2}"
        media_name = Path(asset).name
        self.rels.append((rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{media_name}"))
        sid = self._id()
        self.items.append(
            f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name={quoteattr(media_name)} descr={quoteattr(descr)}/>'
            '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln><a:noFill/></a:ln></p:spPr></p:pic>'
        )

    def finish(self) -> bytes:
        self.text(.62, 7.12, 12.0, .22, [para_xml(self.source, 610, C["quiet"])], name="Source footer")
        return xml_decl(
            f'<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" showMasterSp="0">'
            f'<p:cSld name={quoteattr(f"Slide {self.number}: {self.title}")}><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{C["night"]}"/>'
            '</a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>' + group_root() + "".join(self.items) +
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
        )

    def rels_xml(self) -> bytes:
        rels = [('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout', '../slideLayouts/slideLayout1.xml')] + self.rels
        rels.append((f"rId{len(self.rels) + 2}", 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide', f'../notesSlides/notesSlide{self.number}.xml'))
        return relationships(rels)


def add_bullets(s: Slide, items: list[str], x: float, y: float, w: float, size: int = 1120, gap: float = .55) -> None:
    for i, item in enumerate(items):
        s.text(x, y + i * gap, w, .42, [para_xml("• " + item, size, C["muted"])], name=f"Bullet {i+1}")


def build_slide(index: int) -> Slide:
    title, subtitle, source = SLIDES[index - 1]
    s = Slide(index, title, subtitle, source)
    if index == 1:
        s.text(.67, 2.10, 6.1, .72, [para_xml("THE QUIET CHANNEL", 2500, C["teal"], True)], name="Hero")
        s.text(.68, 2.92, 5.9, 1.15, [para_xml("A privacy-first silent command interface for frontline moments where voice or touch gets in the way.", 1500, C["ink"], True)], name="Thesis")
        s.card(.68, 4.35, 2.82, 1.42, "Beachhead", "e& retail advisors", "Private lookup while preserving the customer conversation.", C["teal"])
        s.card(3.72, 4.35, 2.82, 1.42, "Beachhead", "Field technicians", "Eyes-up, hands-busy access to an existing assistant.", C["acid"])
        s.image("concept-research-rig.svg", 7.25, 1.90, 5.25, 4.48, "Project-authored unvalidated surface-EMG research rig concept")
        s.rect(7.48, 5.88, 4.78, .52, C["warm"], C["orange"], name="Concept badge")
        s.text(7.65, 6.02, 4.42, .24, [para_xml("CONCEPT · NOT FINISHED HARDWARE", 820, C["orange"], True, "ctr")], name="Concept label")
    elif index == 2:
        steps=[("01", "SENSE", "Wearable surface-EMG concept"),("02", "DECODE", "On device · fixed 12-command grammar"),("03", "GATE", "Confidence → abstain / confirm / repair"),("04", "HAND OFF", "Confirmed text → existing agent / CRM")]
        for i,(num,head,body) in enumerate(steps):
            s.card(.68+i*3.03, 2.28, 2.78, 2.22, num, head, body, C["orange"] if i==2 else C["teal"], C["warm"] if i==2 else C["panel"])
        s.rect(.68, 4.88, 11.86, 1.12, C["panel2"], C["acid"], name="Human control")
        s.text(.96, 5.12, 11.30, .62, [para_xml("HUMAN CONTROL  Low confidence stops. Confirmation precedes action. Repair is part of the interface.", 1120, C["ink"], True, "ctr")], name="Human gate")
        s.text(.80, 6.30, 11.60, .35, [para_xml("NOT open-vocabulary transcription · NOT mind reading · NOT autonomous billing changes · NO working physical prototype", 900, C["orange"], True, "ctr")], name="Exclusions")
    elif index == 3:
        s.card(.68, 2.14, 3.72, 1.56, "PREPRINT · R26", "SilentWear", "n=4 · 14 neck sEMG channels · 8 commands + rest · 77.5±6.6% global CV; 59.3±2.2% held-out session. Not this project.", C["teal"])
        s.card(.68, 3.92, 3.72, 1.56, "PEER-REVIEWED · R03–R04", "Gaddy & Klein", "Facial-sEMG silent-speech research; single-speaker research line. No product or transfer claim.", C["acid"])
        s.card(4.66, 2.14, 3.62, 3.34, "DIFFERENT CATEGORIES", "Do not collapse the field", "Gesture: Meta wrist sEMG\nOptical/contactless: Q Cue patent\nAcoustic / IMU: EarCommand, EchoSpeech, MuteIt\nImplanted: clinical neuroprostheses\n\nDifferent sensing, tasks, status and risk.", C["orange"], C["warm"])
        s.card(8.54, 2.14, 3.82, 3.34, "IN-USE PRIVACY REQUIREMENTS", "Minimize by design", "Raw signals stay on device during use. Decoded text remains personal data. Calibration requires explicit opt-in. No emotion or medical inference is produced.", C["teal"])
        s.text(.75, 5.83, 11.72, .62, [para_xml("Design targets—not certification: explicit lock · contact required · confirmation · least privilege · deletion · conventional fallback", 910, C["muted"], True, "ctr")], name="Privacy boundary")
    elif index == 4:
        s.rect(.68, 2.12, 3.35, 3.58, C["warm"], C["orange"], name="Pilot ask")
        s.text(.95, 2.48, 2.80, .30, [para_xml("FIXED FEE · 90 DAYS", 820, C["orange"], True, "ctr")], name="Pilot label")
        s.text(.83, 3.10, 3.02, .78, [para_xml("AED 1,000,000", 2250, C["orange"], True, "ctr")], name="Pilot price")
        s.text(1.00, 4.18, 2.70, .86, [para_xml("e& beachhead · one low-consequence workflow · go / change / stop report", 990, C["muted"], False, "ctr")], name="Pilot scope")
        gates=[("SUCCESS", "Problem + user", "Current input loses on whole-task value; voluntary users prefer the channel."),("SUCCESS", "Bench + field", "Errors are contained; transfer, complete latency, wear, fallback and task value pass pre-agreed thresholds."),("NO-GO", "Stop on purpose", "Existing input wins, consent is compromised, errors escape confirmation, burden defeats value, or governance vetoes.")]
        for i,(lab,head,body) in enumerate(gates):
            s.card(4.34+i*2.72, 2.12, 2.50, 2.62, lab, head, body, C["red"] if lab=="NO-GO" else C["teal"], C["warm"] if lab=="NO-GO" else C["panel"])
        s.rect(4.34, 5.05, 7.94, 1.02, C["panel2"], C["acid"], name="Next decision")
        s.text(4.58, 5.25, 7.48, .58, [para_xml("SEPARATE DEPLOYMENT DECISION AFTER EVIDENCE  ·  per-seat pricing TBD  ·  strategic funding / acquisition optional, unpriced upside", 920, C["ink"], True, "ctr")], name="Next decision text")
    return s

def relationships(items: list[tuple[str, str, str]]) -> bytes:
    body = ''.join(f'<Relationship Id="{rid}" Type="{typ}" Target={quoteattr(target)}/>' for rid, typ, target in items)
    return xml_decl(f'<Relationships xmlns="{REL}">{body}</Relationships>')


def notes_slide_xml(number: int, text: str) -> bytes:
    paras = []
    for line in text.splitlines():
        if line in {"TALK TRACK", "BOUNDARY", "SOURCE", "SOURCES", "OPERATOR", "LICENCES"}:
            paras.append(para_xml(line, 1000, C["teal"], True, before=300, after=120))
        else:
            paras.append(para_xml(line or " ", 1050, "222222", False, after=100))
    body_shape = (
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Text Placeholder 1"/><p:cNvSpPr txBox="1"/>'
        '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{inch(.65)}" y="{inch(.65)}"/><a:ext cx="{inch(6.2)}" cy="{inch(8.3)}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="91440" rIns="91440" bIns="91440"/><a:lstStyle/>'
        + ''.join(paras) + '</p:txBody></p:sp>'
    )
    return xml_decl(f'<p:notes xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld name="Slide {number} presenter notes"><p:spTree>{group_root()}{body_shape}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')


def theme_xml() -> bytes:
    return xml_decl(f'''<a:theme xmlns:a="{NS_A}" name="Quiet Channel Theme"><a:themeElements><a:clrScheme name="Quiet Channel"><a:dk1><a:srgbClr val="{C['night']}"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="{C['panel']}"/></a:dk2><a:lt2><a:srgbClr val="{C['ink']}"/></a:lt2><a:accent1><a:srgbClr val="{C['teal']}"/></a:accent1><a:accent2><a:srgbClr val="{C['orange']}"/></a:accent2><a:accent3><a:srgbClr val="{C['acid']}"/></a:accent3><a:accent4><a:srgbClr val="93B9FF"/></a:accent4><a:accent5><a:srgbClr val="{C['red']}"/></a:accent5><a:accent6><a:srgbClr val="858B85"/></a:accent6><a:hlink><a:srgbClr val="5CD3BD"/></a:hlink><a:folHlink><a:srgbClr val="FF8B5C"/></a:folHlink></a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Quiet Channel"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="accent1"/></a:solidFill><a:solidFill><a:schemeClr val="accent2"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="12700" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/><a:round/><a:headEnd type="none" w="med" len="med"/><a:tailEnd type="none" w="med" len="med"/></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="dk1"/></a:solidFill><a:solidFill><a:schemeClr val="dk2"/></a:solidFill><a:solidFill><a:schemeClr val="lt1"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>''')


def master_xml(kind: str) -> bytes:
    if kind == "slide":
        return xml_decl(f'<p:sldMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" preserve="1"><p:cSld name="Quiet Channel Master"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="dk1" bg2="dk2" folHlink="folHlink" hlink="hlink" tx1="lt1" tx2="lt2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr algn="l"><a:defRPr sz="2800" b="1"/></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr marL="0" indent="0"><a:defRPr sz="1800"/></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:otherStyle></p:txStyles></p:sldMaster>')
    return xml_decl(f'<p:notesMaster xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld name="Quiet Channel Notes Master"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:hf hdr="0" ftr="0" dt="0" sldNum="0"/><p:notesStyle><a:lvl1pPr marL="0" indent="0"><a:defRPr sz="1050"/></a:lvl1pPr></p:notesStyle></p:notesMaster>')


def package_parts() -> dict[str, bytes]:
    parts: dict[str, bytes] = {}
    slides = [build_slide(i) for i in range(1, 5)]
    overrides = [
        ('/ppt/presentation.xml', 'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'),
        ('/ppt/slideMasters/slideMaster1.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml'),
        ('/ppt/slideLayouts/slideLayout1.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml'),
        ('/ppt/notesMasters/notesMaster1.xml', 'application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml'),
        ('/ppt/theme/theme1.xml', 'application/vnd.openxmlformats-officedocument.theme+xml'),
        ('/ppt/presProps.xml', 'application/vnd.openxmlformats-officedocument.presentationml.presProps+xml'),
        ('/ppt/viewProps.xml', 'application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml'),
        ('/ppt/tableStyles.xml', 'application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml'),
        ('/docProps/core.xml', 'application/vnd.openxmlformats-package.core-properties+xml'),
        ('/docProps/app.xml', 'application/vnd.openxmlformats-officedocument.extended-properties+xml'),
    ]
    for i in range(1, 5):
        overrides += [
            (f'/ppt/slides/slide{i}.xml', 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),
            (f'/ppt/notesSlides/notesSlide{i}.xml', 'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'),
        ]
    ct_body = '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="svg" ContentType="image/svg+xml"/>' + ''.join(f'<Override PartName="{p}" ContentType="{t}"/>' for p, t in overrides)
    parts['[Content_Types].xml'] = xml_decl(f'<Types xmlns="{CT}">{ct_body}</Types>')
    parts['_rels/.rels'] = relationships([
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument', 'ppt/presentation.xml'),
        ('rId2', 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties', 'docProps/core.xml'),
        ('rId3', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties', 'docProps/app.xml'),
    ])
    parts['docProps/core.xml'] = xml_decl('<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>The Quiet Channel — Four-Slide Decision Deck</dc:title><dc:subject>Editable four-slide silent command interface concept</dc:subject><dc:creator>Silent Speech Technology project</dc:creator><cp:keywords>silent speech; concept; simulated; evidence; e&amp;</cp:keywords><dc:description>Generated deterministically from repository evidence. No product-performance claim.</dc:description><cp:lastModifiedBy>Standard-library OOXML builder</cp:lastModifiedBy><cp:revision>1</cp:revision><dcterms:created xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:modified></cp:coreProperties>')
    titles = ''.join(f'<vt:lpstr>{escape(t[0])}</vt:lpstr>' for t in SLIDES)
    parts['docProps/app.xml'] = xml_decl(f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Python Standard Library OOXML Builder</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>4</Slides><Notes>4</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips><ScaleCrop>false</ScaleCrop><HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Slide Titles</vt:lpstr></vt:variant><vt:variant><vt:i4>4</vt:i4></vt:variant></vt:vector></HeadingPairs><TitlesOfParts><vt:vector size="4" baseType="lpstr">{titles}</vt:vector></TitlesOfParts><Company>Silent Speech Technology project</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>')
    sld_ids = ''.join(f'<p:sldId id="{255+i}" r:id="rId{2+i}"/>' for i in range(1, 5))
    parts['ppt/presentation.xml'] = xml_decl(f'<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst><p:sldIdLst>{sld_ids}</p:sldIdLst><p:sldSz cx="{SW}" cy="{SH}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle></p:presentation>')
    pres_rels = [
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster', 'slideMasters/slideMaster1.xml'),
        ('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster', 'notesMasters/notesMaster1.xml'),
    ] + [(f'rId{2+i}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide', f'slides/slide{i}.xml') for i in range(1, 5)] + [
        ('rId7', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps', 'presProps.xml'),
        ('rId8', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps', 'viewProps.xml'),
        ('rId9', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme', 'theme/theme1.xml'),
        ('rId10', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles', 'tableStyles.xml'),
    ]
    parts['ppt/_rels/presentation.xml.rels'] = relationships(pres_rels)
    parts['ppt/theme/theme1.xml'] = theme_xml()
    parts['ppt/slideMasters/slideMaster1.xml'] = master_xml('slide')
    parts['ppt/slideMasters/_rels/slideMaster1.xml.rels'] = relationships([
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout', '../slideLayouts/slideLayout1.xml'),
        ('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme', '../theme/theme1.xml'),
    ])
    parts['ppt/slideLayouts/slideLayout1.xml'] = xml_decl(f'<p:sldLayout xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
    parts['ppt/slideLayouts/_rels/slideLayout1.xml.rels'] = relationships([('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster', '../slideMasters/slideMaster1.xml')])
    parts['ppt/notesMasters/notesMaster1.xml'] = master_xml('notes')
    parts['ppt/notesMasters/_rels/notesMaster1.xml.rels'] = relationships([('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme', '../theme/theme1.xml')])
    parts['ppt/presProps.xml'] = xml_decl(f'<p:presentationPr xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"/>')
    parts['ppt/viewProps.xml'] = xml_decl(f'<p:viewPr xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}" lastView="sldView"><p:normalViewPr/><p:slideViewPr><p:cSldViewPr snapToGrid="1" snapToObjects="1"/></p:slideViewPr><p:notesTextViewPr><p:cViewPr varScale="1"><p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale><p:origin x="0" y="0"/></p:cViewPr></p:notesTextViewPr><p:gridSpacing cx="78028800" cy="78028800"/></p:viewPr>')
    parts['ppt/tableStyles.xml'] = xml_decl(f'<a:tblStyleLst xmlns:a="{NS_A}" def="{{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}}"/>')
    for i, slide in enumerate(slides, 1):
        parts[f'ppt/slides/slide{i}.xml'] = slide.finish()
        parts[f'ppt/slides/_rels/slide{i}.xml.rels'] = slide.rels_xml()
        parts[f'ppt/notesSlides/notesSlide{i}.xml'] = notes_slide_xml(i, NOTES[i-1])
        parts[f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels'] = relationships([
            ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster', '../notesMasters/notesMaster1.xml'),
            ('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide', f'../slides/slide{i}.xml'),
        ])
    for asset in ('concept-research-rig.svg',):
        parts[f'ppt/media/{asset}'] = (ROOT / 'assets' / asset).read_bytes()
    return parts


def write_zip(parts: dict[str, bytes], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', compression=ZIP_DEFLATED, compresslevel=9) as zf:
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
        "media": sorted(name for name in parts if name.startswith('ppt/media/')),
        "builder": "pitch/build_4_slide_pptx.py",
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "source_markdown_sha256": sha256((ROOT / 'deck.md').read_bytes()),
        "deterministic_zip_timestamp": "1980-01-01T00:00:00",
        "runtime_dependencies": "Python standard library only",
    }
    evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--evidence', type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument('--no-evidence', action='store_true')
    args = parser.parse_args()
    parts = package_parts()
    write_zip(parts, args.output)
    if not args.no_evidence:
        write_evidence(args.output, args.evidence, parts)
    print(f"built {args.output} ({args.output.stat().st_size} bytes, sha256={sha256(args.output.read_bytes())})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

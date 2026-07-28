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
DEFAULT_OUTPUT = ROOT / "quiet-channel-evidence-deck.pptx"
DEFAULT_EVIDENCE = ROOT / "pptx-build.json"
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
    ("A quiet path into the assistant you already run.", "A confirmation-first silent command channel for e& frontline work—proposed as research, not presented as mind reading.", "Claim boundary: C01–C06, C21–C30. Original concept schematic; no device exists."),
    ("Voice can be costly. Touch can break the moment.", "Test whether a deliberate private-input path helps when an advisor or technician needs information without losing eyes, hands, or the customer conversation.", "Commercial problem hypothesis—not validated customer evidence. C06, C24, C29."),
    ("Three category signals. None proves this product.", "Sensors are entering wearables. Speech transfer across sessions is still research. That gap is both the opportunity and the risk.", "SilentWear preprint; Meta official announcement; Q Cue patent metadata. C07–C17; R26–R31."),
    ("e& frontline retail advisors and field technicians.", "Start opt in, non-medical, and low consequence. Stage 0 chooses one workflow and tests the two roles separately before biosignal collection.", "Captain decision, 2026-07-28; provenance/decisions.md. Beachhead decision—not traction."),
    ("Capture → decode → human gate → existing assistant.", "Alternatives, abstention and confirmation stay visible. The decoder is the new AI; the downstream assistant can be reused.", "Architecture intent, not implementation. SilentWear 2.47 ms is model inference—not complete latency."),
    ("Show the miss. Make repair the product.", "The offline demo starts locked, rejects an authored ambiguous case, requires a manual authored repair, and keeps output behind confirmation.", "CONCEPT / SIMULATED PIPELINE. All traces, scores, thresholds, timing and failures are authored."),
    ("External evidence shows a transfer gap.", "We would rather show the gap than have diligence find it.", "SilentWear arXiv:2603.02847v2, preprint, n=4, 14 channels, 8 commands + rest. Not this project."),
    ("A lock. A data flow. A governance veto.", "No-air-audio is not anonymity. Privacy requires purpose, minimization, access, deletion, confirmation and prohibited uses.", "UAE official PDPL page; EU Regulation 2024/1689 Art. 5(1)(f); NIST Privacy Framework."),
    ("Five categories. No borrowed validation.", "Name the closest alternatives and distinguish papers, preprints, shipping gesture products, patents, assistive products and clinical research.", "R03–R05, R21, R26–R31, R38–R41; research/competitors.md. Named-system conditions remain separate."),
    ("A Gulf bilingual corpus—governed before owned.", "No public Arabic surface-EMG silent-speech corpus was identified in this bounded review; cited sEMG performance exemplars are English.", "Bounded negative finding. Exact licences/revisions: C24–C26; R34–R37. No artifacts downloaded."),
    ("Operating value first. Strategic upside second.", "Lead: fixed-fee 90-day pilot, then per-seat annual deployment only if evidence gates pass. IP/data funding and acquisition/exit optionality are unpriced upside.", "Captain decision. AED 1M applies only to the 90-day pilot; later prices and amounts are TBD."),
    ("Fund a 90-day decision—not an enclosure.", "AED 1,000,000 fixed fee for a gated pilot with an explicit go / change / stop report.", "Fee approved by Captain for this pilot only. Cohort, thresholds, allocations, team and later amounts remain TBD."),
    ("Go. Change. Or stop on purpose.", "Pre-commit to problem, bench, transfer, language and field gates. Numeric thresholds are frozen before data—not invented for the pitch.", "Claim ledger: safe = simulated interaction + attributed external evidence. All project performance remains unknown."),
]

NOTES = [
    "TALK TRACK\nThis is a command-channel research proposal. Tomorrow's executable proof is interaction and failure handling, not sensing.\nBOUNDARY\nDo not say device, reads thoughts, open vocabulary, accurate, behind-ear, private, customer or deployed.\nSOURCE\nresearch/claim-boundary.md; research/claim-ledger.md.",
    "TALK TRACK\nKeep the concrete frontline moments, then volunteer that no user discovery was supplied. Existing shortcuts may be the correct answer.\nBOUNDARY\nBeachhead is selected; pain and willingness to pay remain hypotheses.\nSOURCE\nresearch/presentation-review.md.",
    "TALK TRACK\nSeparate category evidence: SilentWear is a four-person command preprint; Meta is wrist gesture input; Q Cue is optical. None validates this product.\nBOUNDARY\nApple terms are undisclosed; do not state a deal price.\nSOURCES\narxiv.org/abs/2603.02847; about.fb.com official product page; US20240119938A1 / US12204627B2 metadata.",
    "TALK TRACK\nCaptain selected e& frontline retail advisors and field technicians. Stage 0 still selects one workflow and measures role differences.\nBOUNDARY\nVoluntary enrollment, conventional fallback and no performance-management use.\nSOURCE\nprovenance/decisions.md.",
    "TALK TRACK\nThe decoder is new AI. Candidate alternatives, abstention and confirmation stay visible.\nBOUNDARY\n2.47 ms is external model inference after a 0.8–1.4 s sensing window, not end-to-end latency.\nSOURCE\nSilentWear arXiv:2603.02847v2; research/scout-review.md.",
    "OPERATOR\nOpen demo/index.html. Unlock. Scenario 1: confirm and show egress. Scenario 2: reject, authored repair, confirm. Never mouth a phrase as if the browser sensed it.\nBOUNDARY\nAll delay, failure, score and waveform behavior is authored.\nSOURCE\ndemo/PRESENTER.md.",
    "TALK TRACK\nRead conditions before numbers. SilentWear: preprint; n=4; 14 differential neck channels; 8 commands plus rest. Silent accuracy 77.5±6.6% global cross-validation and 59.3±2.2% held-out session. GAP9 2.47 ms inference and 20.5 mW; 27.1 h estimated with 150 mAh.\nBOUNDARY\nExternal study—not this project; comfort and complete latency unknown.\nSOURCE\narXiv:2603.02847v2.",
    "TALK TRACK\nPrivacy is not 'no microphone.' It is purpose, lock, minimization, access, deletion, incident handling and a veto on surveillance uses.\nBOUNDARY\nNo compliance certification; UAE Executive Regulations and legal interpretation require counsel.\nSOURCES\nu.ae data protection laws; eur-lex.europa.eu/eli/reg/2024/1689/oj/eng; NIST Privacy Framework.",
    "TALK TRACK\nName AlterEgo before the audience does. Meta is gesture and Q Cue is optical. EarCommand, EchoSpeech and MuteIt are peer-reviewed systems with different sensing assumptions. Whispp describes acoustic apps; clinical systems are separate.\nBOUNDARY\nNo funding total, regional leadership, approval, FTO or competitor product-performance claim. Whispp status is company-described.\nSOURCES\nDOI 10.1145/3534613; DOI 10.1145/3544548.3580801; DOI 10.1145/3550281; whispp.com; research/references.md.",
    "TALK TRACK\nThe bounded scan did not identify an Arabic sEMG corpus; do not turn a negative search into certainty. A corpus is a governed liability before a moat.\nLICENCES\nGaddy code MIT/data CC BY 4.0; SilentWear code Apache-2.0; checked Meta assets non-commercial; two BCI repos had no LICENSE.\nBOUNDARY\nNo artifact was downloaded or reused.\nSOURCE\nresearch/references.md; research/evidence-matrix.md.",
    "TALK TRACK\nLead with operating path: AED 1M for the 90-day pilot; annual per-seat only if gates pass. Strategic IP/data ownership is negotiated upside.\nBOUNDARY\nAnnual pricing, strategic funding, valuation and acquisition/exit amounts are TBD.\nSOURCE\nprovenance/decisions.md.",
    "TALK TRACK\nAsk for AED 1,000,000 and accountable workflow/data-governance owners. Work starts with discovery and approvals—not immediate biometric collection or enclosure design.\nBOUNDARY\nFee applies only to fixed 90-day pilot; allocations and all later amounts remain TBD.\nSOURCE\nprovenance/decisions.md.",
    "TALK TRACK\nA sponsor should know what stops the work. Thresholds are approved before collection by workflow, statistics, safety/ethics and governance owners.\nBOUNDARY\nA negative product result can be a successful evidence programme.\nSOURCE\nresearch/claim-ledger.md; research/evidence-matrix.md.",
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
        self.text(11.55, .20, 1.3, .32, [para_xml(f"{self.number:02d} / 13", 850, C["muted"], True, "r")], name="Slide number")
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
        s.image("concept-research-rig.svg", 7.45, 2.10, 5.25, 4.45, "Original unvalidated surface EMG research rig concept")
        s.card(.65, 2.42, 2.0, 2.18, "Tomorrow", "Interaction proof", "Offline concept / simulated pipeline. Authored traces and failure behavior.", C["teal"])
        s.card(2.82, 2.42, 2.0, 2.18, "Next proof", "Fixed grammar", "Surface-EMG research rig, one workflow, pre-agreed gates.", C["acid"])
        s.card(4.99, 2.42, 2.0, 2.18, "Not claimed", "No conversation", "No wearable, model, project accuracy, AAC indication or deployment.", C["orange"], C["warm"])
        s.text(.68, 5.05, 6.2, .85, [para_xml("PRIVATE INPUT, WITHOUT PRETENDING THE RESEARCH IS DONE", 1220, C["orange"], True)], name="Thesis")
    elif index == 2:
        s.card(.65, 2.35, 3.72, 2.15, "Scenes to test", "Frontline moments", "Busy retail interaction · customer-site work · private lookup in a meeting.")
        s.card(4.55, 2.35, 3.72, 2.15, "Current alternatives", "The baseline can win", "Touch · keyboard · push-to-talk · ordinary voice · earpiece · whisper/contact mic · colleague · no system.", C["acid"])
        s.card(8.45, 2.35, 3.72, 2.15, "Win bar", "Whole-task value", "Improve setup + completion + correction + fallback + user preference—not only inference.", C["orange"], C["warm"])
        s.rect(.65, 4.85, 11.52, 1.15, C["warm"], C["orange"], name="Discovery gap")
        s.text(.92, 5.08, 11.0, .62, [para_xml("DISCOVERY GAP  No interviews, observed frequency, baseline task result, user preference, buyer or willingness-to-pay evidence has been supplied.", 1050, C["ink"], True)], name="Discovery gap text")
    elif index == 3:
        s.card(.65, 2.40, 3.72, 2.70, "Preprint / wearable research", "SilentWear", "Four participants · 14 neck channels · 8 commands plus rest · on-MCU classification. Held-out-session gap remains material.", C["teal"])
        s.card(4.55, 2.40, 3.72, 2.70, "Company / shipping gesture input", "Meta Neural Band", "US$799 bundle available September 2025. Wrist gestures and handwriting—not speech from muscle.", C["acid"])
        s.card(8.45, 2.40, 3.72, 2.70, "Patent + acquisition context", "Q Cue / Apple", "Coherent-light facial micromovement approach, not electrodes. Terms undisclosed; no product performance.", C["orange"], C["warm"])
        s.text(.8, 5.52, 11.8, .5, [para_xml("SENSORS ARE ENTERING WEARABLES. SPEECH TRANSFER ACROSS SESSIONS IS STILL RESEARCH.", 1250, C["orange"], True, "ctr")], name="Why now conclusion")
    elif index == 4:
        s.card(.65, 2.34, 2.75, 2.30, "User-value gate", "Current controls must lose", "Recurring private-input job, named baseline and voluntary user preference.")
        s.card(3.58, 2.34, 2.75, 2.30, "Consent gate", "Voluntary means voluntary", "Non-biometric alternative; no employment or performance-management consequence.", C["acid"])
        s.card(6.51, 2.34, 2.75, 2.30, "Error gate", "Confirmation contains harm", "Grammar and fallback must survive false accepts and false rejects.", C["orange"])
        s.card(9.44, 2.34, 2.75, 2.30, "Operations gate", "Contact must fit", "Setup, skin, fatigue, motion and reapplication are product costs.", C["red"], C["warm"])
        s.rect(.65, 4.98, 11.54, .98, C["warm"], C["orange"], name="Out of scope")
        s.text(.9, 5.16, 11.0, .52, [para_xml("OUT OF STAGE 1  Record changes · payments · access control · scoring · emergencies · diagnosis · replacement AAC", 1050, C["ink"], True, "ctr")], name="Out of scope text")
    elif index == 5:
        s.image("pipeline-gates.svg", .65, 2.20, 12.02, 4.31, "Original proposed confirmation-first data-flow diagram")
    elif index == 6:
        steps = [("01", "DECLARE", "Concept / simulated. No sensor or project accuracy."), ("02", "UNLOCK", "Deliberate page state + illustrative fixed grammar."), ("03", "INSPECT", "Authored signal, features and alternatives."), ("04", "FAIL + REPAIR", "Reject ambiguous case; manual repair stays gated."), ("05", "AUDIT", "Confirmed text increments; raw-fixture egress stays zero.")]
        for i, (num, head, body) in enumerate(steps):
            x = .65 + i * 2.36
            s.card(x, 2.38, 2.17, 2.72, num, head, body, C["acid"] if i == 3 else C["teal"], C["warm"] if i == 3 else C["panel"])
        s.rect(.65, 5.42, 11.56, .78, C["warm"], C["orange"], name="Demo boundary")
        s.text(.9, 5.60, 11.0, .38, [para_xml("DO NOT FAKE LIVE  The presenter never mouths a command as if the browser sensed it.", 1020, C["ink"], True, "ctr")], name="Demo boundary text")
    elif index == 7:
        s.image("evidence-gap.svg", .52, 2.10, 7.15, 4.55, "Original chart of external SilentWear transfer results")
        s.text(.95, 6.42, 6.25, .28, [para_xml("77.5±6.6% global CV  →  59.3±2.2% held-out session", 790, C["muted"], True, "ctr")], name="Native evidence values")
        s.card(7.88, 2.15, 4.45, 1.20, "External edge result", "2.47 ms inference · 20.5 mW", "27.1 h estimated with 150 mAh. Not complete latency.", C["teal"])
        s.card(7.88, 3.54, 4.45, 1.20, "Open vocabulary / preprint", "12.2% WER", "Single-speaker Gaddy benchmark with LLM rescoring—not edge/cross-user.", C["acid"])
        s.card(7.88, 4.93, 4.45, 1.20, "Missing here", "Every project metric", "Hardware · transfer · complete latency · comfort · Arabic · security · user value.", C["orange"], C["warm"])
    elif index == 8:
        s.image("privacy-flow.svg", 7.50, 2.05, 5.18, 4.82, "Original proposed privacy state machine")
        s.card(.65, 2.30, 2.02, 3.10, "Before collection", "Voluntary + reviewed", "Purpose-limited consent · non-biometric alternative · ethics/electrical/labor/jurisdiction review · separate calibration consent.", C["teal"])
        s.card(2.86, 2.30, 2.02, 3.10, "System targets", "Lock + minimize", "Explicit lock · contact required · raw retention/egress off · least privilege · deletion · confirmation.", C["acid"])
        s.card(5.07, 2.30, 2.02, 3.10, "Prohibited", "No surveillance", "Emotion/stress/engagement · productivity scoring · covert sensing · unrelated model training.", C["red"], C["warm"])
    elif index == 9:
        rows = [("sEMG speech", "Gaddy/Klein · SilentWear · AlterEgo lineage", "Closest modality; no transfer"), ("wrist sEMG", "Meta shipping gesture/handwriting input", "Not speech"), ("optical", "Q Cue patent + acquisition context", "No released performance"), ("ear/acoustic/IMU", "EarCommand · EchoSpeech · MuteIt papers [R38–R40]", "Different sensing/tasks"), ("assistive / implanted", "Whispp company apps [R41] · AAC · clinical studies", "Different intended use/status")]
        s.text(.7, 2.20, 2.4, .3, [para_xml("CATEGORY", 740, C["teal"], True)], name="Matrix header 1")
        s.text(3.25, 2.20, 5.1, .3, [para_xml("ACTUAL STATUS", 740, C["teal"], True)], name="Matrix header 2")
        s.text(8.65, 2.20, 3.5, .3, [para_xml("BOUNDARY", 740, C["teal"], True)], name="Matrix header 3")
        for i, (a, b, c) in enumerate(rows):
            y = 2.58 + i * .72
            s.rect(.65, y, 11.55, .62, C["panel"] if i % 2 == 0 else C["panel2"], C["line"], radius=False, name=f"Matrix row {i+1}")
            s.text(.82, y + .13, 2.2, .3, [para_xml(a, 870, C["ink"], True)], name=f"Category {i+1}")
            s.text(3.25, y + .13, 5.1, .3, [para_xml(b, 850, C["muted"])], name=f"Status {i+1}")
            s.text(8.65, y + .13, 3.2, .3, [para_xml(c, 850, C["muted"])], name=f"Boundary {i+1}")
    elif index == 10:
        s.card(.65, 2.30, 2.78, 2.65, "Permissive records", "Gaddy / SilentWear", "Gaddy code MIT; data record CC BY 4.0. SilentWear code Apache-2.0. Data/model/dependencies remain separate.", C["teal"])
        s.card(3.58, 2.30, 2.78, 2.65, "Not commercial inputs", "Meta terms", "Checked generic-neuromotor code CC BY-NC; emg2qwerty CC BY-NC-SA.", C["orange"], C["warm"])
        s.card(6.51, 2.30, 2.78, 2.65, "No licence", "Named BCI repos", "Two checked implanted-BCI repositories have no root LICENSE file; no default reuse permission.", C["red"], C["warm"])
        s.card(9.44, 2.30, 2.78, 2.65, "Rights before moat", "Governed corpus", "Native-user scope · consent · withdrawal/deletion · labor separation · security · no silent secondary use.", C["acid"])
        s.rect(.65, 5.30, 11.56, .82, C["warm"], C["orange"], name="Corpus boundary")
        s.text(.90, 5.48, 11.0, .38, [para_xml("A CORPUS IS A LIABILITY-BEARING RESEARCH RECORD BEFORE IT IS A MOAT.", 1100, C["ink"], True, "ctr")], name="Corpus boundary text")
    elif index == 11:
        s.rect(.65, 2.30, 3.35, 3.65, C["warm"], C["orange"], name="Pilot price")
        s.text(.95, 2.65, 2.75, .30, [para_xml("FIXED 90-DAY PILOT", 820, C["orange"], True, "ctr")], name="Pilot label")
        s.text(.88, 3.20, 2.90, .72, [para_xml("AED 1M", 3150, C["orange"], True, "ctr")], name="Pilot amount")
        s.text(.95, 4.20, 2.75, .85, [para_xml("Captain-approved fee only—not annual pricing, strategic funding, valuation or exit value.", 920, C["muted"], False, "ctr")], name="Pilot boundary")
        s.card(4.35, 2.30, 3.72, 1.45, "Lead path", "Pilot → annual seats", "Per-seat annual price TBD; only after evidence gates and operating economics.", C["teal"])
        s.card(4.35, 4.02, 3.72, 1.45, "Strategic upside / unpriced", "IP + governed corpus", "e& may fund and negotiate foreground ownership; participant/data rights remain.", C["acid"])
        s.card(8.42, 2.30, 3.72, 3.17, "Not a return forecast", "Acquisition is optionality", "No valuation, strategic amount or exit amount. Pilot evidence is never replaced by corporate narrative.", C["orange"], C["warm"])
    elif index == 12:
        s.rect(.65, 2.23, 4.05, 3.92, C["warm"], C["orange"], name="Ask amount")
        s.text(.95, 2.65, 3.45, .30, [para_xml("FIXED FEE · 90 DAYS", 850, C["orange"], True, "ctr")], name="Ask label")
        s.text(.82, 3.22, 3.70, .70, [para_xml("AED 1,000,000", 2450, C["orange"], True, "ctr")], name="Ask amount text")
        s.text(1.02, 4.20, 3.30, 1.10, [para_xml("One gated go / change / stop report. Later per-seat pricing, strategic funding and acquisition/exit amounts: TBD.", 1020, C["muted"], False, "ctr")], name="Ask boundary")
        s.card(5.05, 2.23, 3.35, 1.58, "Owners", "Name accountability", "One workflow owner + one data-governance owner.", C["teal"])
        s.card(8.72, 2.23, 3.35, 1.58, "Discovery", "Voluntary access", "Retail-advisor / field-technician discovery; no biosignals before approvals.", C["acid"])
        s.card(5.05, 4.16, 3.35, 1.58, "Sandbox", "After gates", "Assistant sandbox only after discovery, protocol, privacy and security gates.", C["teal"])
        s.card(8.72, 4.16, 3.35, 1.58, "Use of funds", "Allocations TBD", "Users · sensing/study · privacy/security/ethics/FTO · evaluation/fallback · approved roles.", C["orange"], C["warm"])
    elif index == 13:
        gates = [("0", "PROBLEM", "Whole task vs current input", "Stop if existing input wins"), ("1", "BENCH", "False accept/reject + complete latency", "Change if error cannot be contained"), ("2", "TRANSFER", "Reapply · days · motion · adaptation", "Stop if burden defeats value"), ("3", "LANGUAGE", "Native-user bilingual command scope", "Re-scope if gap/cost exceeds plan"), ("4", "FIELD", "Task · fallback · wear · controls", "Hard stop if no net value")]
        for i, (num, head, body, stop) in enumerate(gates):
            x = .65 + i * 2.36
            s.card(x, 2.35, 2.17, 2.82, f"Gate {num}", head, body + "\n\n" + stop, C["orange"] if i == 4 else C["teal"], C["warm"] if i == 4 else C["panel"])
        s.rect(.65, 5.50, 11.56, .72, C["panel2"], C["acid"], name="Claim ledger")
        s.text(.88, 5.66, 11.1, .34, [para_xml("CLAIM LEDGER  SAFE: simulated interaction + attributed evidence   ·   UNKNOWN: all project performance/value   ·   PROHIBITED: hardware/accuracy/AAC/privacy/traction claims", 850, C["acid"], True, "ctr")], name="Claim ledger text")
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
    slides = [build_slide(i) for i in range(1, 14)]
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
    for i in range(1, 14):
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
    parts['docProps/core.xml'] = xml_decl('<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Quiet Channel Lab — Evidence-Gated Decision Deck</dc:title><dc:subject>Editable 13-slide silent command interface proposal</dc:subject><dc:creator>Silent Speech Technology project</dc:creator><cp:keywords>silent speech; concept; simulated; evidence; e&amp;</cp:keywords><dc:description>Generated deterministically from repository evidence. No product-performance claim.</dc:description><cp:lastModifiedBy>Standard-library OOXML builder</cp:lastModifiedBy><cp:revision>1</cp:revision><dcterms:created xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-07-28T00:00:00Z</dcterms:modified></cp:coreProperties>')
    titles = ''.join(f'<vt:lpstr>{escape(t[0])}</vt:lpstr>' for t in SLIDES)
    parts['docProps/app.xml'] = xml_decl(f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Python Standard Library OOXML Builder</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>13</Slides><Notes>13</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips><ScaleCrop>false</ScaleCrop><HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Slide Titles</vt:lpstr></vt:variant><vt:variant><vt:i4>13</vt:i4></vt:variant></vt:vector></HeadingPairs><TitlesOfParts><vt:vector size="13" baseType="lpstr">{titles}</vt:vector></TitlesOfParts><Company>Silent Speech Technology project</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>')
    sld_ids = ''.join(f'<p:sldId id="{255+i}" r:id="rId{2+i}"/>' for i in range(1, 14))
    parts['ppt/presentation.xml'] = xml_decl(f'<p:presentation xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst><p:sldIdLst>{sld_ids}</p:sldIdLst><p:sldSz cx="{SW}" cy="{SH}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle></p:presentation>')
    pres_rels = [
        ('rId1', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster', 'slideMasters/slideMaster1.xml'),
        ('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster', 'notesMasters/notesMaster1.xml'),
    ] + [(f'rId{2+i}', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide', f'slides/slide{i}.xml') for i in range(1, 14)] + [
        ('rId16', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps', 'presProps.xml'),
        ('rId17', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps', 'viewProps.xml'),
        ('rId18', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme', 'theme/theme1.xml'),
        ('rId19', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles', 'tableStyles.xml'),
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
    for asset in ('concept-research-rig.svg', 'pipeline-gates.svg', 'evidence-gap.svg', 'privacy-flow.svg'):
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
        "slides": 13,
        "notes_slides": 13,
        "media": sorted(name for name in parts if name.startswith('ppt/media/')),
        "builder": "pitch/build_pptx.py",
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

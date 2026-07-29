# Quiet Channel Lab — four-slide executive decision deck

> **Authority:** this file is the editable narrative source for `quiet-channel-4-slide-deck.pptx`.
> **Status:** concept / simulated interaction; no sensor, model, user study, customer, project performance, or product.
> **Decision:** e& frontline retail advisors and field technicians; AED 1,000,000 fixed-fee 90-day pilot only. Later pricing, strategic funding, valuation, and acquisition/exit amounts remain TBD.
> **Visual direction:** editorial evidence spine; one message and one native visual mechanism per slide; no device hero, third-party media, or logos.

The builder reads the JSON block below so the editable story and generated artifact cannot silently drift.

```json
{
  "deck_label": "QUIET CHANNEL",
  "status_label": "CONCEPT / SIMULATED",
  "slides": [
    {
      "id": "opportunity",
      "eyebrow": "OPPORTUNITY",
      "headline": [
        "A quiet command lane",
        "for frontline work."
      ],
      "premise": [
        "One opt-in, low-consequence workflow.",
        "Connect to the existing assistant.",
        "Test against voice, touch and shortcuts."
      ],
      "contexts": ["RETAIL MOMENT", "FIELD MOMENT"],
      "command": "QUIET COMMAND",
      "assistant": "EXISTING ASSISTANT",
      "footer": "Beachhead decision; workflow and demand unvalidated · C06 / H01",
      "max_words": 48,
      "notes": [
        "ROLE",
        "Open on a narrow, testable operating opportunity—not a device reveal.",
        "TALK TRACK",
        "e& frontline retail advisors and field technicians are the captain-selected beachhead. Stage 0 still selects one exact low-consequence workflow and compares the two roles separately. The test is whether a quiet command lane beats voice, touch, shortcuts, or no new system on whole-task value.",
        "BOUNDARY",
        "No hardware, model, user research, customer, integration, project performance, or validated demand exists. The contexts are hypotheses, not observed pain or traction.",
        "SOURCES",
        "research/claim-ledger.md C06; provenance/decisions.md H01."
      ]
    },
    {
      "id": "mechanism",
      "eyebrow": "TRUSTED MECHANISM",
      "headline": [
        "A fixed command channel.",
        "A human gate before action."
      ],
      "nodes": [
        "DELIBERATE START",
        "PROPOSED sEMG",
        "FIXED CANDIDATES",
        "PREVIEW / CONFIRM / REPAIR",
        "EXISTING ASSISTANT"
      ],
      "repair": "ABSTAIN / REPAIR",
      "raw_boundary": "RAW SIGNAL STOPS HERE",
      "qualifier": "Proposed architecture—not implemented hardware, security, latency, or integration.",
      "footer": "Design targets · C05, C19, C21–C23",
      "max_words": 55,
      "notes": [
        "ROLE",
        "Make the human gate—not an imagined wearable—the product idea.",
        "TALK TRACK",
        "A deliberate start opens a proposed surface-EMG research path into a fixed command candidate list. Low confidence abstains. A user previews, confirms, rejects, or repairs before confirmed text reaches an existing assistant. In the demo, the signal, candidates, scores, failure, repair, and timing are authored fixtures.",
        "BOUNDARY",
        "This is proposed architecture. There is no physical prototype, model, on-device benchmark, implemented data flow, security proof, complete latency result, or assistant integration. It is not open-vocabulary transcription, mind reading, autonomous billing, payment, access control, or a medical/AAC system.",
        "SOURCES",
        "research/claim-boundary.md; research/claim-ledger.md C05, C19, C21–C23; demo/PRESENTER.md."
      ]
    },
    {
      "id": "evidence",
      "eyebrow": "EVIDENCE / RISK",
      "headline": [
        "The signal is plausible.",
        "Cross-session transfer is the risk."
      ],
      "chart": {
        "global_label": "GLOBAL CV",
        "global_value": "77.5±6.6%",
        "global_height": 77.5,
        "held_label": "HELD-OUT SESSION",
        "held_value": "59.3±2.2%",
        "held_height": 59.3,
        "gap": "−18.2 POINTS"
      },
      "proof_title": "PILOT MUST PROVE",
      "proofs": [
        "Stable after reapplication",
        "Whole-task value",
        "Voluntary governance + fallback"
      ],
      "caption": "SilentWear v2 preprint · n=4 · 14 neck sEMG channels · 8 commands + rest · top-1 accuracy · not this project · arXiv:2603.02847v2.",
      "footer": "External evidence · C07/C13/C22",
      "max_words": 65,
      "notes": [
        "ROLE",
        "Use the held-out-session drop to explain what the pilot must buy down.",
        "TALK TRACK",
        "SilentWear v2 is the closest cited analogue: a preprint with four participants, 14 differential neck sEMG channels, eight commands plus rest, and top-1 command accuracy. It reports 77.5±6.6% average global cross-validated silent accuracy and 59.3±2.2% average held-out-session accuracy. The 18.2-point gap is derived from those reported means. Read the conditions before the values.",
        "BOUNDARY",
        "These are external study results, not this project's results or expectations. Gesture, optical, acoustic/IMU, open-vocabulary, and implanted systems answer different questions. Inference time is not complete latency. Hardware, transfer, task value, comfort, Arabic/Gulf behavior, privacy, and security remain unknown here.",
        "SOURCES",
        "SilentWear v2 preprint: https://arxiv.org/abs/2603.02847v2 ; research/claim-ledger.md C07, C13, C22; research/references.md R26."
      ]
    },
    {
      "id": "decision",
      "eyebrow": "DECISION",
      "headline": [
        "Approve the 90-day pilot.",
        "Buy a go / change / stop decision."
      ],
      "amount": "AED 1,000,000",
      "pilot_label": "FIXED FEE · 90 DAYS",
      "phases": [
        "SELECT WORKFLOW",
        "TEST FAILURE",
        "COMPARE TASK"
      ],
      "decision": "GO / CHANGE / STOP",
      "asks": [
        "WORKFLOW OWNER",
        "GOVERNANCE OWNER",
        "VOLUNTARY ACCESS"
      ],
      "boundary": [
        "Pilot fee only.",
        "Annual pricing, strategic funding, valuation,",
        "and acquisition/exit amounts remain TBD."
      ],
      "footer": "Captain · H02–H03",
      "max_words": 55,
      "notes": [
        "ROLE",
        "Close on the fixed-fee decision programme and accountable owners.",
        "TALK TRACK",
        "The ask is AED 1,000,000 for a fixed-fee 90-day evidence programme. It selects one workflow, tests signal and failure containment, compares whole-task value and governance, and returns an explicit go, change, or stop report. e& is the selected beachhead, not a claimed customer or agreed pilot.",
        "BOUNDARY",
        "The fee applies only to this 90-day pilot. Per-seat annual pricing, strategic IP or governed-dataset funding, valuation, and acquisition/exit amounts remain TBD and unpromised. No biosignal collection starts before workflow, consent, ethics/safety, privacy, labor, data-governance, and jurisdiction gates. Cohort, thresholds, allocations, team, sandbox, and deployment remain unagreed.",
        "SOURCES",
        "provenance/decisions.md H01–H03; research/claim-ledger.md C29."
      ]
    }
  ]
}
```

## Presenter rhythm

1. **Opportunity:** one narrow frontline job worth testing.
2. **Mechanism:** a fixed channel whose human gate contains error.
3. **Evidence:** a published transfer gap defines the risk.
4. **Decision:** fund a 90-day go/change/stop answer, not a fictional product.

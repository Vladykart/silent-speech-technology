(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.SilentSpeechDemoCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const REJECTION_THRESHOLD = 0.72;
  const STAGE_COUNT = 6;

  function syntheticChannels(pattern) {
    return Object.freeze(Array.from({ length: 8 }, (_, channel) => Object.freeze(
      pattern.map((value, index) => {
        const texture = ((index + channel * 3) % 5 - 2) * 1.6;
        const scaled = value * (0.86 + channel * 0.035) + texture + (channel % 2 ? 2 : -1);
        return Math.max(8, Math.min(92, Math.round(scaled)));
      })
    )));
  }

  function fixture(definition) {
    return Object.freeze({
      ...definition,
      channels: syntheticChannels(definition.signalPattern),
      signalPattern: undefined,
      features: Object.freeze(definition.features),
      ctcFrames: Object.freeze(definition.ctcFrames),
      timings: Object.freeze(definition.timings),
      candidates: Object.freeze(definition.candidates.map((candidate) => Object.freeze(candidate))),
      repairCandidate: definition.repairCandidate ? Object.freeze(definition.repairCandidate) : undefined
    });
  }

  const FIXTURES = Object.freeze({
    inventory: fixture({
      id: "inventory",
      label: "Clear command",
      consequence: "low-consequence lookup",
      authoredPhrase: "check stock for router model seven",
      signalPattern: [18, 19, 18, 21, 25, 34, 49, 65, 73, 67, 52, 39, 34, 39, 53, 68, 76, 66, 48, 34, 27, 23, 21, 19, 18, 18, 19, 18],
      features: { envelope: "0.68", timing: "0.42", stability: "0.81", window: "36 ms*" },
      ctcFrames: ["▁check", "▁stock", "▁for", "▁router", "▁model", "▁seven"],
      timings: [0, 96, 182, 344, 468, 612],
      candidates: [
        { text: "check stock for router model seven", intent: "inventory.lookup", confidence: 0.84 },
        { text: "check status for router model seven", intent: "service.lookup", confidence: 0.11 },
        { text: "unresolved", intent: "none", confidence: 0.05 }
      ],
      requiresConfirmation: true,
      safetySensitive: false,
      confirmedOutput: "SIMULATED request staged · inventory.lookup · router model 7"
    }),
    ambiguous: fixture({
      id: "ambiguous",
      label: "Ambiguous + repair",
      consequence: "uncertain command",
      authoredPhrase: "open order notes",
      signalPattern: [20, 20, 19, 21, 24, 29, 36, 43, 48, 46, 41, 36, 33, 34, 38, 43, 47, 45, 40, 34, 29, 25, 23, 22, 21, 20, 20, 20],
      features: { envelope: "0.43", timing: "0.39", stability: "0.52", window: "36 ms*" },
      ctcFrames: ["▁open", "▁order", "▁no…", "blank", "▁status?"],
      timings: [0, 104, 196, 358, 492, 646],
      candidates: [
        { text: "open order notes", intent: "orders.notes", confidence: 0.54 },
        { text: "open order status", intent: "orders.status", confidence: 0.38 },
        { text: "unresolved", intent: "none", confidence: 0.08 }
      ],
      repairCandidate: { text: "open work order", intent: "orders.open", source: "manual authored repair" },
      requiresConfirmation: true,
      safetySensitive: false,
      confirmedOutput: "SIMULATED request staged · orders.open · repaired and confirmed"
    }),
    cancel: fixture({
      id: "cancel",
      label: "Safety-sensitive",
      consequence: "state-changing cancellation",
      authoredPhrase: "cancel last request",
      signalPattern: [17, 18, 17, 20, 28, 43, 61, 72, 66, 49, 35, 29, 34, 48, 66, 75, 69, 51, 36, 28, 23, 20, 19, 18, 17, 17, 18, 17],
      features: { envelope: "0.64", timing: "0.47", stability: "0.86", window: "36 ms*" },
      ctcFrames: ["▁cancel", "▁last", "▁request", "blank"],
      timings: [0, 99, 188, 351, 481, 631],
      candidates: [
        { text: "cancel last request", intent: "request.cancel", confidence: 0.91 },
        { text: "confirm last request", intent: "request.confirm", confidence: 0.06 },
        { text: "unresolved", intent: "none", confidence: 0.03 }
      ],
      requiresConfirmation: true,
      safetySensitive: true,
      confirmedOutput: "SIMULATED cancellation staged · explicit human confirmation recorded"
    })
  });

  function evaluateFixture(id, threshold = REJECTION_THRESHOLD) {
    if (!Object.prototype.hasOwnProperty.call(FIXTURES, id)) throw new Error(`Unknown fixture: ${id}`);
    if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) throw new Error("Threshold must be between 0 and 1");
    const selected = FIXTURES[id];
    const candidates = selected.candidates.slice().sort((a, b) => b.confidence - a.confidence);
    const total = candidates.reduce((sum, item) => sum + item.confidence, 0);
    if (Math.abs(total - 1) > 1e-9) throw new Error(`Fixture ${id} candidate confidences must sum to 1`);
    const top = candidates[0];
    return Object.freeze({
      fixture: selected,
      candidates: Object.freeze(candidates),
      threshold,
      decision: top.confidence >= threshold ? "candidate" : "reject",
      top
    });
  }

  function stageLabel(stage, result) {
    const labels = [
      "Synthetic eight-channel fixture loaded",
      "Authored filtering and windowing replayed",
      "Designed feature snapshot produced",
      "CTC-style candidate stream produced",
      result.decision === "reject" ? "Abstained below fixture threshold" : "Candidate held for human confirmation",
      "Human/output gate resolved"
    ];
    return labels[Math.max(0, Math.min(labels.length - 1, stage))];
  }

  function advanceStage(stage, decision, repairSelected = false) {
    if (!Number.isInteger(stage) || stage < 0 || stage >= STAGE_COUNT) throw new Error(`Stage must be an integer between 0 and ${STAGE_COUNT - 1}`);
    if (!["candidate", "reject"].includes(decision)) throw new Error(`Unknown decision: ${decision}`);
    if (stage < 4) return Object.freeze({ stage: stage + 1, resolution: null });
    if (stage === 4 && decision === "reject" && !repairSelected) return Object.freeze({ stage: 5, resolution: "rejected" });
    return Object.freeze({ stage, resolution: null });
  }

  function canResolve(decision, repairSelected, value) {
    if (!["candidate", "reject"].includes(decision)) throw new Error(`Unknown decision: ${decision}`);
    if (!["confirmed", "rejected"].includes(value)) throw new Error(`Unknown resolution: ${value}`);
    return value === "rejected" || decision === "candidate" || repairSelected;
  }

  function canEmit(selectedFixture, decision, repairSelected, resolution, confirmationEnabled) {
    if (!selectedFixture || selectedFixture.requiresConfirmation !== true) return false;
    return confirmationEnabled === true && resolution === "confirmed" && (decision === "candidate" || repairSelected === true);
  }

  return Object.freeze({ FIXTURES, REJECTION_THRESHOLD, STAGE_COUNT, evaluateFixture, stageLabel, advanceStage, canResolve, canEmit });
});

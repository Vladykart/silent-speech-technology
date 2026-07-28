(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.SilentSpeechDemoCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const REJECTION_THRESHOLD = 0.72;
  const FIXTURES = Object.freeze({
    inventory: Object.freeze({
      id: "inventory",
      label: "Clear command",
      authoredPhrase: "check stock for router model seven",
      channels: Object.freeze([
        Object.freeze([18, 20, 19, 23, 29, 42, 58, 71, 64, 48, 38, 34, 41, 57, 69, 73, 60, 43, 31, 24, 21, 19]),
        Object.freeze([21, 22, 20, 24, 31, 37, 46, 55, 61, 59, 49, 40, 35, 39, 47, 53, 51, 42, 33, 26, 23, 22]),
        Object.freeze([16, 18, 17, 20, 25, 34, 49, 62, 68, 57, 44, 36, 33, 46, 59, 66, 55, 39, 28, 22, 18, 17])
      ]),
      features: Object.freeze({ envelope: "0.68", timing: "0.42", stability: "0.81" }),
      candidates: Object.freeze([
        Object.freeze({ text: "check stock for router model seven", intent: "inventory.lookup", confidence: 0.84 }),
        Object.freeze({ text: "check status for router model seven", intent: "service.lookup", confidence: 0.11 }),
        Object.freeze({ text: "unresolved", intent: "none", confidence: 0.05 })
      ]),
      confirmedOutput: "SIMULATED request staged · inventory.lookup · router model 7"
    }),
    ambiguous: Object.freeze({
      id: "ambiguous",
      label: "Ambiguous input",
      authoredPhrase: "open order notes",
      channels: Object.freeze([
        Object.freeze([20, 21, 19, 23, 28, 35, 43, 48, 45, 38, 33, 31, 35, 42, 46, 44, 37, 31, 27, 24, 22, 21]),
        Object.freeze([22, 21, 22, 24, 28, 32, 38, 43, 42, 37, 34, 33, 36, 40, 42, 41, 37, 32, 28, 25, 23, 22]),
        Object.freeze([18, 19, 18, 21, 25, 31, 39, 45, 43, 36, 32, 30, 34, 40, 44, 42, 35, 29, 25, 22, 20, 19])
      ]),
      features: Object.freeze({ envelope: "0.43", timing: "0.39", stability: "0.52" }),
      candidates: Object.freeze([
        Object.freeze({ text: "open order notes", intent: "orders.notes", confidence: 0.54 }),
        Object.freeze({ text: "open order status", intent: "orders.status", confidence: 0.38 }),
        Object.freeze({ text: "unresolved", intent: "none", confidence: 0.08 })
      ]),
      repairCandidate: Object.freeze({ text: "open work order", intent: "orders.open", source: "manual authored repair" }),
      confirmedOutput: "SIMULATED request staged · orders.open · repaired and confirmed"
    }),
    cancel: Object.freeze({
      id: "cancel",
      label: "Safety command",
      authoredPhrase: "cancel last request",
      channels: Object.freeze([
        Object.freeze([17, 18, 17, 22, 35, 54, 67, 61, 44, 32, 29, 38, 56, 70, 65, 49, 33, 26, 22, 19, 18, 17]),
        Object.freeze([19, 20, 19, 23, 30, 43, 54, 52, 41, 34, 31, 37, 48, 57, 55, 45, 35, 28, 24, 21, 20, 19]),
        Object.freeze([15, 17, 16, 21, 33, 49, 62, 58, 42, 30, 27, 36, 52, 66, 61, 46, 31, 24, 20, 18, 16, 16])
      ]),
      features: Object.freeze({ envelope: "0.64", timing: "0.47", stability: "0.86" }),
      candidates: Object.freeze([
        Object.freeze({ text: "cancel last request", intent: "request.cancel", confidence: 0.91 }),
        Object.freeze({ text: "confirm last request", intent: "request.confirm", confidence: 0.06 }),
        Object.freeze({ text: "unresolved", intent: "none", confidence: 0.03 })
      ]),
      confirmedOutput: "SIMULATED cancellation staged · human confirmation recorded"
    })
  });

  function evaluateFixture(id, threshold = REJECTION_THRESHOLD) {
    if (!Object.prototype.hasOwnProperty.call(FIXTURES, id)) throw new Error(`Unknown fixture: ${id}`);
    if (!Number.isFinite(threshold) || threshold < 0 || threshold > 1) throw new Error("Threshold must be between 0 and 1");
    const fixture = FIXTURES[id];
    const candidates = fixture.candidates.slice().sort((a, b) => b.confidence - a.confidence);
    const total = candidates.reduce((sum, item) => sum + item.confidence, 0);
    if (Math.abs(total - 1) > 1e-9) throw new Error(`Fixture ${id} candidate confidences must sum to 1`);
    const top = candidates[0];
    return Object.freeze({
      fixture,
      candidates: Object.freeze(candidates),
      threshold,
      decision: top.confidence >= threshold ? "candidate" : "reject",
      top
    });
  }

  function stageLabel(stage, result) {
    const labels = [
      "Authored sensor fixture loaded",
      "Deterministic preprocessing complete",
      "Candidate list produced",
      result.decision === "reject" ? "Rejected below threshold" : "Awaiting user confirmation",
      "Output gate resolved"
    ];
    return labels[Math.max(0, Math.min(labels.length - 1, stage))];
  }

  function advanceStage(stage, decision, repairSelected = false) {
    if (!Number.isInteger(stage) || stage < 0 || stage > 4) throw new Error("Stage must be an integer between 0 and 4");
    if (!["candidate", "reject"].includes(decision)) throw new Error(`Unknown decision: ${decision}`);
    if (stage < 3) return Object.freeze({ stage: stage + 1, resolution: null });
    if (stage === 3 && decision === "reject" && !repairSelected) return Object.freeze({ stage: 4, resolution: "rejected" });
    return Object.freeze({ stage, resolution: null });
  }

  function canResolve(decision, repairSelected, value) {
    if (!["candidate", "reject"].includes(decision)) throw new Error(`Unknown decision: ${decision}`);
    if (!["confirmed", "rejected"].includes(value)) throw new Error(`Unknown resolution: ${value}`);
    return value === "rejected" || decision === "candidate" || repairSelected;
  }

  return Object.freeze({ FIXTURES, REJECTION_THRESHOLD, evaluateFixture, stageLabel, advanceStage, canResolve });
});

(function exposeReplayContract(root, factory) {
  "use strict";
  const contract = factory();
  if (typeof module === "object" && module.exports) module.exports = contract;
  else root.ReplayContract = contract;
})(typeof globalThis === "undefined" ? this : globalThis, () => {
  "use strict";

  const STAGES = Object.freeze([
    Object.freeze({id: "recorded-source", number: 1, label: "Recorded source"}),
    Object.freeze({id: "released-model", number: 2, label: "Released model"}),
    Object.freeze({id: "human-decision", number: 3, label: "Human decision"}),
  ]);
  const EVENT_ORDER = Object.freeze([
    "asset_checks_passed",
    "source_opened",
    "replay_started",
    "source_complete",
    "preprocessing_complete",
    "branches_aligned",
    "model_forward_complete",
    "decoder_complete",
    "metadata_revealed",
    "decision_required",
  ]);
  const RECORDED_EXAMPLES = Object.freeze(Array.from({length: 10}, (_, index) => Object.freeze({
    sampleId: `QC-R${String(index + 1).padStart(2, "0")}`,
    classification: "official_recorded_example",
    executable: true,
    secondTake: index === 1 ? "QC-R02-T2" : null,
  })));
  const SECOND_TAKE = Object.freeze({sampleId: "QC-R02-T2", classification: "official_recorded_second_take", executable: true, parent: "QC-R02"});

  function initialState() {
    return {
      stage: "recorded-source",
      expectedEventIndex: 0,
      modelComplete: false,
      decoderComplete: false,
      metadataVisible: false,
      boundaryViolation: false,
      terminalState: "ready",
    };
  }

  function reduce(state, event) {
    const next = {...state};
    if (["error", "local_stopped", "local_confirmed", "local_rejected"].includes(event.event)) {
      next.stage = "human-decision";
      next.terminalState = event.event.replace("local_", "");
      return next;
    }
    const expected = EVENT_ORDER[next.expectedEventIndex];
    if (event.event !== expected || Number(event.sequence) !== next.expectedEventIndex + 1) {
      next.boundaryViolation = true;
      next.metadataVisible = false;
      next.terminalState = "boundary_error";
      return next;
    }
    next.expectedEventIndex += 1;
    if (["asset_checks_passed", "source_opened", "replay_started", "source_complete"].includes(event.event)) {
      next.stage = "recorded-source";
      next.terminalState = "running";
    }
    if (["preprocessing_complete", "branches_aligned", "model_forward_complete", "decoder_complete", "metadata_revealed"].includes(event.event)) {
      next.stage = "released-model";
    }
    if (event.event === "model_forward_complete") next.modelComplete = true;
    if (event.event === "decoder_complete") next.decoderComplete = next.modelComplete;
    if (event.event === "metadata_revealed") {
      if (!next.modelComplete || !next.decoderComplete) next.boundaryViolation = true;
      else next.metadataVisible = true;
    }
    if (event.event === "decision_required") {
      next.stage = "human-decision";
      next.terminalState = event.state || "decision";
      if (!next.metadataVisible) next.boundaryViolation = true;
    }
    if (next.boundaryViolation) next.metadataVisible = false;
    return next;
  }

  function validManifest(items) {
    if (!Array.isArray(items) || items.length !== RECORDED_EXAMPLES.length) return false;
    return RECORDED_EXAMPLES.every((expected, index) => {
      const actual = items[index];
      return actual && actual.id === expected.sampleId && actual.classification === expected.classification;
    });
  }

  return Object.freeze({STAGES, EVENT_ORDER, RECORDED_EXAMPLES, SECOND_TAKE, initialState, reduce, validManifest});
});

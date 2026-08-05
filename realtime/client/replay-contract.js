(function exposeReplayContract(root, factory) {
  "use strict";
  const contract = factory();
  if (typeof module === "object" && module.exports) module.exports = contract;
  else root.ReplayContract = contract;
})(typeof globalThis === "undefined" ? this : globalThis, () => {
  "use strict";

  const STAGES = Object.freeze([
    Object.freeze({id: "data-collection", number: 1, label: "Data collection"}),
    Object.freeze({id: "model", number: 2, label: "Model"}),
    Object.freeze({id: "process-result", number: 3, label: "Process result"}),
  ]);

  // These are safe UI references, not participant IDs, archive paths, or prompt labels.
  const RECORDED_EXAMPLES = Object.freeze([
    Object.freeze({scenario: "clear", exampleId: "QC-R01", classification: "official_recorded_example", executable: true, recordedTakes: 1}),
    Object.freeze({scenario: "ambiguous", exampleId: "QC-R02", classification: "official_recorded_example", executable: true, recordedTakes: 2}),
    Object.freeze({scenario: "safety", exampleId: "QC-R03", classification: "official_recorded_example", executable: true, recordedTakes: 1}),
  ]);

  const FUTURE_COMMAND_EXAMPLES = Object.freeze([
    "Turn on the desk light",
    "Open my notes",
    "Next slide",
    "Pause playback",
    "Set a ten-minute timer",
    "Reply yes",
    "Go back",
    "Volume down",
  ].map((text, index) => Object.freeze({
    id: `F-${String(index + 1).padStart(2, "0")}`,
    text,
    classification: "authored_future_example",
    executable: false,
    recorded: false,
  })));

  function initialState() {
    return {
      stage: "data-collection",
      inferenceComplete: false,
      metadataVisible: false,
      boundaryViolation: false,
      terminalState: "ready",
    };
  }

  function reduce(state, event) {
    const next = {...state};
    switch (event.event) {
      case "acquisition_started":
      case "raw_frame":
        next.stage = "data-collection";
        next.terminalState = "running";
        break;
      case "preprocessing":
      case "features":
        next.stage = "model";
        break;
      case "inference":
        next.stage = "model";
        next.inferenceComplete = true;
        break;
      case "record_reference":
        if (!next.inferenceComplete) {
          next.boundaryViolation = true;
          next.metadataVisible = false;
        } else {
          next.metadataVisible = true;
        }
        break;
      case "decision":
        next.stage = "process-result";
        next.terminalState = event.state || "decision";
        if (!next.inferenceComplete) next.boundaryViolation = true;
        break;
      case "stopped":
      case "error":
        next.stage = "process-result";
        next.terminalState = event.event;
        break;
      case "local_confirmed":
        next.stage = "process-result";
        next.terminalState = "confirmed";
        break;
      case "local_rejected":
        next.stage = "process-result";
        next.terminalState = "rejected";
        break;
      default:
        break;
    }
    return next;
  }

  return Object.freeze({STAGES, RECORDED_EXAMPLES, FUTURE_COMMAND_EXAMPLES, initialState, reduce});
});

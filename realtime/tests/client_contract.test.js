"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const contract = require("../client/replay-contract.js");

const ROOT = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "client/index.html"), "utf8");
const css = fs.readFileSync(path.join(ROOT, "client/styles.css"), "utf8");
const app = fs.readFileSync(path.join(ROOT, "client/app.js"), "utf8");

assert.deepEqual(
  contract.STAGES.map(({id, number, label}) => ({id, number, label})),
  [
    {id: "data-collection", number: 1, label: "Data collection"},
    {id: "model", number: 2, label: "Model"},
    {id: "process-result", number: 3, label: "Process result"},
  ],
  "the primary replay contract must contain exactly three ordered stages",
);

let state = contract.initialState();
assert.equal(state.stage, "data-collection");
state = contract.reduce(state, {event: "acquisition_started"});
assert.equal(state.stage, "data-collection");
state = contract.reduce(state, {event: "preprocessing"});
assert.equal(state.stage, "model");
state = contract.reduce(state, {event: "features"});
assert.equal(state.stage, "model");
state = contract.reduce(state, {event: "inference"});
assert.equal(state.inferenceComplete, true);
assert.equal(state.metadataVisible, false);
state = contract.reduce(state, {event: "record_reference"});
assert.equal(state.metadataVisible, true);
assert.equal(state.boundaryViolation, false);
state = contract.reduce(state, {event: "decision", state: "confirm_required"});
assert.equal(state.stage, "process-result");
assert.equal(state.terminalState, "confirm_required");
state = contract.reduce(state, {event: "local_rejected"});
assert.equal(state.terminalState, "rejected");

const earlyReference = contract.reduce(contract.initialState(), {event: "record_reference"});
assert.equal(earlyReference.metadataVisible, false);
assert.equal(earlyReference.boundaryViolation, true, "metadata must remain hidden before inference");
const earlyDecision = contract.reduce(contract.initialState(), {event: "decision", state: "confirm_required"});
assert.equal(earlyDecision.boundaryViolation, true, "a decision must not precede inference");
const stopped = contract.reduce(contract.initialState(), {event: "stopped"});
assert.equal(stopped.stage, "process-result");
assert.equal(stopped.terminalState, "stopped");

assert.deepEqual(
  contract.RECORDED_EXAMPLES.map(({scenario, exampleId, recordedTakes}) => ({scenario, exampleId, recordedTakes})),
  [
    {scenario: "clear", exampleId: "QC-R01", recordedTakes: 1},
    {scenario: "ambiguous", exampleId: "QC-R02", recordedTakes: 2},
    {scenario: "safety", exampleId: "QC-R03", recordedTakes: 1},
  ],
);
assert.ok(contract.RECORDED_EXAMPLES.every((item) => item.classification === "official_recorded_example" && item.executable === true));
assert.ok(contract.FUTURE_COMMAND_EXAMPLES.length >= 8, "future examples should substantially expand the idea set");
assert.ok(contract.FUTURE_COMMAND_EXAMPLES.every((item) => item.classification === "authored_future_example" && item.executable === false && item.recorded === false));

const stagePanels = [...html.matchAll(/data-stage-panel="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(stagePanels, ["data-collection", "model", "process-result"], "HTML must expose exactly three top-level stage panels");
const progressStages = [...html.matchAll(/data-progress-stage="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(progressStages, stagePanels, "navigation and panels must share the same three-stage order");
for (const item of contract.RECORDED_EXAMPLES) {
  assert.match(html, new RegExp(`data-scenario="${item.scenario}" data-example-id="${item.exampleId}"`));
}
for (const phrase of ["What news?", "09:48 AM", "Keep back!"]) {
  assert.ok(!html.includes(phrase), `record reference ${phrase} must not be present before inference`);
}
assert.match(html, /<fieldset id="scenario-list">[\s\S]*?<legend>/);
assert.match(html, /role="alert"/);
assert.match(html, /aria-live="polite"/);
assert.match(html, /<meter id="score-meter"/);
assert.match(html, /class="skip-link"/);
assert.match(css, /:focus-visible/);
assert.match(css, /prefers-reduced-motion:\s*reduce/);
assert.match(css, /@media \(min-width: 2200px\)/);
assert.match(css, /overflow-x:\s*hidden/);

const browserAssets = `${html}\n${css}\n${app}`;
assert.ok(!/https?:\/\//i.test(browserAssets), "browser assets must not contain external URLs");
for (const forbidden of ["sendBeacon", "localStorage", "sessionStorage", "getUserMedia", "mediaDevices", "WebSocket", "EventSource", "indexedDB", "RTCPeerConnection"]) {
  assert.ok(!browserAssets.includes(forbidden), `browser assets must not use ${forbidden}`);
}
assert.match(app, /replayState\.metadataVisible \|\| replayState\.boundaryViolation/);
assert.match(app, /safety_acknowledged: elements\.safetyAck\.checked/);
assert.match(app, /action: "confirm"/);
assert.match(app, /action: "reject"/);
assert.match(app, /No final local result/);

console.log("realtime client contract tests passed: three stages, recorded/future classification, metadata boundary, human gate, no egress, and accessibility semantics");

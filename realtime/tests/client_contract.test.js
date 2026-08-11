"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const contract = require("../client/replay-contract.js");

const ROOT = path.resolve(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "client/index.html"), "utf8");
const css = fs.readFileSync(path.join(ROOT, "client/styles.css"), "utf8");
const app = fs.readFileSync(path.join(ROOT, "client/app.js"), "utf8");

assert.deepEqual(contract.STAGES, [
  {id: "recorded-source", number: 1, label: "Recorded source"},
  {id: "released-model", number: 2, label: "Released model"},
  {id: "human-decision", number: 3, label: "Human decision"},
]);
assert.equal(contract.RECORDED_EXAMPLES.length, 10);
assert.deepEqual(contract.RECORDED_EXAMPLES.map((item) => item.sampleId), Array.from({length: 10}, (_, index) => `QC-R${String(index + 1).padStart(2, "0")}`));
assert.ok(contract.RECORDED_EXAMPLES.every((item) => item.classification === "official_recorded_example" && item.executable));
assert.equal(contract.SECOND_TAKE.sampleId, "QC-R02-T2");
assert.equal(contract.SECOND_TAKE.parent, "QC-R02");

let state = contract.initialState();
contract.EVENT_ORDER.forEach((event, index) => {
  state = contract.reduce(state, {event, sequence: index + 1, state: event === "decision_required" ? "confirm_required" : undefined});
  assert.equal(state.boundaryViolation, false, `${event} must be accepted at its exact position`);
});
assert.equal(state.stage, "human-decision");
assert.equal(state.modelComplete, true);
assert.equal(state.decoderComplete, true);
assert.equal(state.metadataVisible, true);
assert.equal(state.terminalState, "confirm_required");
state = contract.reduce(state, {event: "local_rejected"});
assert.equal(state.terminalState, "rejected");

const earlyMetadata = contract.reduce(contract.initialState(), {event: "metadata_revealed", sequence: 9});
assert.equal(earlyMetadata.boundaryViolation, true);
assert.equal(earlyMetadata.metadataVisible, false);
let missingDecoder = contract.initialState();
for (let index = 0; index < 7; index += 1) missingDecoder = contract.reduce(missingDecoder, {event: contract.EVENT_ORDER[index], sequence: index + 1});
missingDecoder = contract.reduce(missingDecoder, {event: "metadata_revealed", sequence: 9});
assert.equal(missingDecoder.boundaryViolation, true, "metadata cannot skip decoder completion");
const duplicate = contract.reduce(contract.reduce(contract.initialState(), {event: "asset_checks_passed", sequence: 1}), {event: "asset_checks_passed", sequence: 1});
assert.equal(duplicate.boundaryViolation, true, "duplicate events must fail closed");
const stopped = contract.reduce(contract.initialState(), {event: "local_stopped"});
assert.equal(stopped.stage, "human-decision");
assert.equal(stopped.terminalState, "stopped");

const stagePanels = [...html.matchAll(/data-stage-panel="([^"]+)"/g)].map((match) => match[1]);
const stageProgress = [...html.matchAll(/data-progress-stage="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(stagePanels, contract.STAGES.map((item) => item.id));
assert.deepEqual(stageProgress, stagePanels);
assert.equal((html.match(/data-sample-id="QC-R/g) || []).length, 10);
for (const sample of contract.RECORDED_EXAMPLES) assert.match(html, new RegExp(`data-sample-id="${sample.sampleId}"`));
assert.match(html, /<fieldset id="sample-list">[\s\S]*?<legend>/);
assert.match(html, /<h1[^>]*>/);
assert.equal((html.match(/<h1/g) || []).length, 1);
assert.match(html, /role="alert"/);
assert.match(html, /aria-live="polite"/);
assert.match(html, /<meter id="score-meter"/);
assert.match(html, /class="skip-link"/);
assert.match(html, /RECORDED SOURCE TRACE · TRANSFORMED DISPLAY ENVELOPE/);
assert.match(html, /EXECUTED MODEL 1 OF 1/);
assert.match(html, /PROJECT BOUNDED DECODER · NOT THE RELEASED MODEL/);
assert.match(html, /NOT EXECUTED HERE/);
assert.match(html, /Bounded transformed evidence is sent to this authorized browser/);
assert.match(css, /:focus-visible/);
assert.match(css, /prefers-reduced-motion:\s*reduce/);
assert.match(css, /@media \(max-width: 1100px\)/);
assert.match(css, /@media \(min-width: 2200px\)/);
assert.ok(!/overflow-x:\s*hidden/.test(css), "layout must not mask horizontal overflow");

const browserAssets = `${html}\n${css}\n${app}`;
assert.ok(!/https?:\/\//i.test(browserAssets));
for (const forbidden of ["sendBeacon", "localStorage", "sessionStorage", "indexedDB", "serviceWorker", "WebSocket", "EventSource", "RTCPeerConnection", "getUserMedia", "mediaDevices", "SimulatedSignalSource", "authored_future"]) {
  assert.ok(!browserAssets.includes(forbidden), `browser assets must not use ${forbidden}`);
}
for (const value of ["0.84", "0.54", "0.91", "0.72"]) assert.ok(!browserAssets.includes(value), `authored fixture ${value} must not enter realtime`);
assert.match(app, /state\.metadataVisible \|\| state\.boundaryViolation/);
assert.match(app, /safety_acknowledged: elements\.safetyAck\.checked/);
assert.match(app, /event\.key === " "/);
assert.match(app, /event\.key === "Escape"/);
assert.match(app, /action: "confirm"/);
assert.match(app, /action: "reject"/);
assert.match(app, /No final result/);

console.log("realtime client contract passed: 10 sealed official samples, exact event reducer, bounded evidence, human gates, accessibility, and no synthetic/external/persistent path");

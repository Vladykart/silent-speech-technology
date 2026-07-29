"use strict";
const assert = require("node:assert/strict");
const core = require("../core.js");

assert.deepEqual(Object.keys(core.FIXTURES), ["inventory", "ambiguous", "cancel"]);
assert.equal(core.REJECTION_THRESHOLD, 0.72);
assert.equal(core.STAGE_COUNT, 6);

const inventory = core.evaluateFixture("inventory");
assert.equal(inventory.decision, "candidate");
assert.equal(inventory.top.intent, "inventory.lookup");
assert.equal(inventory.top.confidence, 0.84);
assert.equal(inventory.fixture.consequence, "low-consequence lookup");
assert.equal(core.stageLabel(3, inventory), "CTC-style candidate stream produced");
assert.equal(core.stageLabel(4, inventory), "Candidate held for human confirmation");

const ambiguous = core.evaluateFixture("ambiguous");
assert.equal(ambiguous.decision, "reject");
assert.equal(ambiguous.top.confidence, 0.54);
assert.equal(ambiguous.fixture.repairCandidate.intent, "orders.open");
assert.equal(core.stageLabel(4, ambiguous), "Abstained below fixture threshold");

const cancel = core.evaluateFixture("cancel");
assert.equal(cancel.decision, "candidate");
assert.equal(cancel.top.intent, "request.cancel");
assert.equal(cancel.fixture.safetySensitive, true);
assert.equal(cancel.fixture.requiresConfirmation, true);

// Six-stage transitions stop candidate paths at the human gate.
assert.deepEqual(core.advanceStage(0, inventory.decision), { stage: 1, resolution: null });
assert.deepEqual(core.advanceStage(1, inventory.decision), { stage: 2, resolution: null });
assert.deepEqual(core.advanceStage(2, inventory.decision), { stage: 3, resolution: null });
assert.deepEqual(core.advanceStage(3, inventory.decision), { stage: 4, resolution: null });
assert.deepEqual(core.advanceStage(4, inventory.decision), { stage: 4, resolution: null });

// Ambiguity abstains automatically unless the explicit authored repair is selected.
assert.deepEqual(core.advanceStage(4, ambiguous.decision), { stage: 5, resolution: "rejected" });
assert.deepEqual(core.advanceStage(4, ambiguous.decision, true), { stage: 4, resolution: null });
assert.equal(core.canResolve(ambiguous.decision, false, "confirmed"), false);
assert.equal(core.canResolve(ambiguous.decision, false, "rejected"), true);
assert.equal(core.canResolve(ambiguous.decision, true, "confirmed"), true);

// No fixture, especially the safety-sensitive path, can emit without explicit confirmation policy.
assert.equal(core.canEmit(inventory.fixture, inventory.decision, false, "confirmed", true), true);
assert.equal(core.canEmit(inventory.fixture, inventory.decision, false, null, true), false);
assert.equal(core.canEmit(cancel.fixture, cancel.decision, false, "confirmed", false), false);
assert.equal(core.canEmit(cancel.fixture, cancel.decision, false, "rejected", true), false);
assert.equal(core.canEmit(cancel.fixture, cancel.decision, false, "confirmed", true), true);
assert.equal(core.canEmit(ambiguous.fixture, ambiguous.decision, true, "confirmed", true), true);
assert.equal(core.canEmit(ambiguous.fixture, ambiguous.decision, false, "confirmed", true), false);

for (const fixture of Object.values(core.FIXTURES)) {
  assert.equal(fixture.channels.length, 8);
  assert.ok(fixture.channels.every((channel) => channel.length === 28));
  assert.ok(fixture.channels.every((channel) => channel.every((value) => Number.isInteger(value) && value >= 8 && value <= 92)));
  assert.equal(fixture.timings.length, core.STAGE_COUNT);
  assert.ok(fixture.timings.every((value, index) => index === 0 || value > fixture.timings[index - 1]));
  assert.equal(fixture.candidates.reduce((sum, item) => sum + item.confidence, 0), 1);
  assert.equal(Object.isFrozen(fixture), true);
  assert.equal(Object.isFrozen(fixture.channels), true);
}

assert.throws(() => core.evaluateFixture("missing"), /Unknown fixture/);
assert.throws(() => core.evaluateFixture("inventory", 2), /Threshold/);
assert.throws(() => core.advanceStage(6, "candidate"), /Stage/);
assert.throws(() => core.canResolve("candidate", false, "missing"), /resolution/);
console.log("demo core tests passed: deterministic scenarios, abstention/repair, confirmation, safety gate, timing, and fixture invariants");

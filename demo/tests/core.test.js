"use strict";
const assert = require("node:assert/strict");
const core = require("../core.js");

assert.deepEqual(Object.keys(core.FIXTURES), ["inventory", "ambiguous", "cancel"]);
assert.equal(core.REJECTION_THRESHOLD, 0.72);

const inventory = core.evaluateFixture("inventory");
assert.equal(inventory.decision, "candidate");
assert.equal(inventory.top.intent, "inventory.lookup");
assert.equal(inventory.top.confidence, 0.84);

const ambiguous = core.evaluateFixture("ambiguous");
assert.equal(ambiguous.decision, "reject");
assert.equal(ambiguous.top.confidence, 0.54);
assert.equal(ambiguous.fixture.repairCandidate.intent, "orders.open");

const cancel = core.evaluateFixture("cancel");
assert.equal(cancel.decision, "candidate");
assert.equal(cancel.top.intent, "request.cancel");
assert.equal(core.stageLabel(3, cancel), "Awaiting user confirmation");
assert.equal(core.stageLabel(3, ambiguous), "Rejected below threshold");
assert.deepEqual(core.advanceStage(2, inventory.decision), { stage: 3, resolution: null });
assert.deepEqual(core.advanceStage(3, inventory.decision), { stage: 3, resolution: null });
assert.deepEqual(core.advanceStage(3, ambiguous.decision), { stage: 4, resolution: "rejected" });
assert.deepEqual(core.advanceStage(3, ambiguous.decision, true), { stage: 3, resolution: null });
assert.equal(core.canResolve(inventory.decision, false, "confirmed"), true);
assert.equal(core.canResolve(ambiguous.decision, false, "confirmed"), false);
assert.equal(core.canResolve(ambiguous.decision, false, "rejected"), true);
assert.equal(core.canResolve(ambiguous.decision, true, "confirmed"), true);

for (const fixture of Object.values(core.FIXTURES)) {
  assert.equal(fixture.channels.length, 3);
  assert.ok(fixture.channels.every((channel) => channel.length === 22));
  assert.equal(fixture.candidates.reduce((sum, item) => sum + item.confidence, 0), 1);
}

assert.throws(() => core.evaluateFixture("missing"), /Unknown fixture/);
assert.throws(() => core.evaluateFixture("inventory", 2), /Threshold/);
assert.throws(() => core.advanceStage(5, "candidate"), /Stage/);
assert.throws(() => core.canResolve("candidate", false, "missing"), /resolution/);
console.log("demo core tests passed: deterministic fixtures, candidate/rejection gates, and invariants");

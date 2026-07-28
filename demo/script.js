(() => {
  "use strict";
  const core = window.SilentSpeechDemoCore;
  const select = document.getElementById("fixture-select");
  const advance = document.getElementById("advance");
  const autoRun = document.getElementById("auto-run");
  const resetButton = document.getElementById("reset");
  const confirmButton = document.getElementById("confirm");
  const repairButton = document.getElementById("repair");
  const rejectButton = document.getElementById("reject");
  const lockToggle = document.getElementById("lock-toggle");
  const confirmationControl = document.getElementById("confirmation-control");
  const ephemeralControl = document.getElementById("ephemeral-control");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let stage = 0;
  let resolution = null;
  let repairSelected = false;
  let unlocked = false;
  let textEgress = 0;
  let lastEgressEvent = "Nothing transmitted. This log is simulated page state.";
  let timer = null;

  function result() { return core.evaluateFixture(select.value); }
  function stopTimer() { if (timer) window.clearInterval(timer); timer = null; autoRun.textContent = "Auto-run fixture"; }
  function linePath(values, channel) {
    const xStep = 680 / (values.length - 1);
    const yBase = 45 + channel * 58;
    return values.map((value, index) => `${index ? "L" : "M"}${40 + index * xStep},${yBase - (value - 40) * .58}`).join(" ");
  }
  function renderChart(fixture) {
    const colors = ["#d8ef67", "#65d4c3", "#e5a43b"];
    const grid = [45, 103, 161].map((y) => `<path class="chart-grid" d="M40 ${y}H730"/>`).join("");
    const lines = fixture.channels.map((values, index) => `<path class="chart-line" stroke="${colors[index]}" d="${linePath(values, index)}"/><text class="chart-label" x="5" y="${49 + index * 58}">C${index + 1}</text>`).join("");
    document.getElementById("signal-chart").innerHTML = `${grid}${lines}`;
  }
  function setUnlocked(id, unlocked, stateText) {
    const card = document.getElementById(id);
    card.classList.toggle("locked", !unlocked);
    card.querySelector(".card-state").textContent = stateText;
  }
  function renderCandidates(evaluation) {
    const list = document.getElementById("candidate-list");
    if (stage < 2) { list.innerHTML = "<p>No candidates yet.</p>"; return; }
    list.replaceChildren(...evaluation.candidates.map((candidate) => {
      const row = document.createElement("div");
      row.className = "candidate";
      row.style.setProperty("--score", `${candidate.confidence * 100}%`);
      const text = document.createElement("span"); text.textContent = candidate.text;
      const score = document.createElement("strong"); score.textContent = candidate.confidence.toFixed(2);
      row.append(text, score); return row;
    }));
  }
  function renderDecision(evaluation) {
    const box = document.getElementById("decision-state");
    const title = box.querySelector("strong");
    const copy = box.querySelector("p");
    const icon = box.querySelector(".decision-icon");
    box.className = "decision-state waiting";
    confirmButton.disabled = true; repairButton.disabled = true; rejectButton.disabled = true;
    rejectButton.textContent = "Reject candidate";
    if (!unlocked) {
      icon.textContent = "⌁"; title.textContent = "Decoder locked";
      copy.textContent = "Unlock is deliberate. The concept pipeline does not advance in this state.";
      return;
    }
    if (stage < 3) {
      icon.textContent = "···"; title.textContent = "Waiting for candidate";
      copy.textContent = "The output channel stays closed until the confidence rule and human gate resolve.";
      return;
    }
    if (evaluation.decision === "reject" && repairSelected) {
      box.className = "decision-state candidate"; icon.textContent = "↺";
      title.textContent = resolution ? "Repair gate resolved" : "Authored repair selected";
      copy.textContent = resolution ? (resolution === "confirmed" ? "The repaired candidate was confirmed by the operator." : "The repaired candidate was rejected by the operator.") : `Manual fallback selected “${evaluation.fixture.repairCandidate.text}”. It still has not been sent.`;
      confirmButton.disabled = Boolean(resolution) || !confirmationControl.checked;
      rejectButton.disabled = Boolean(resolution);
      rejectButton.textContent = "Reject repaired candidate";
      return;
    }
    if (evaluation.decision === "reject") {
      const finalized = resolution === "rejected";
      box.className = "decision-state reject"; icon.textContent = "×";
      title.textContent = finalized ? "Automatic rejection finalized" : "Uncertain · reject";
      copy.textContent = finalized ? "The below-threshold candidate was rejected automatically. No output." : `Top candidate ${evaluation.top.confidence.toFixed(2)} is below the illustrative ${evaluation.threshold.toFixed(2)} gate. No output.`;
      repairButton.disabled = finalized || !evaluation.fixture.repairCandidate;
      rejectButton.disabled = finalized;
      rejectButton.textContent = "Finalize automatic rejection";
    } else {
      box.className = "decision-state candidate"; icon.textContent = "?";
      title.textContent = resolution ? "Gate resolved" : "Confirmation required";
      copy.textContent = resolution ? (resolution === "confirmed" ? "The candidate was confirmed by the operator." : "The candidate was rejected by the operator.") : `“${evaluation.top.text}” cleared the illustrative threshold; it has not been sent.`;
      confirmButton.disabled = Boolean(resolution) || !confirmationControl.checked;
      rejectButton.disabled = Boolean(resolution);
    }
  }
  function renderOutput(evaluation) {
    const title = document.getElementById("output-title");
    const copy = document.getElementById("output-copy");
    if (evaluation.decision === "reject" && stage >= 3 && !repairSelected) {
      title.textContent = "Rejected safely"; copy.textContent = "No request emitted · choose the authored repair, another input, or recalibration."; return;
    }
    if (resolution === "confirmed") { title.textContent = repairSelected ? "Repaired + confirmed · simulated" : "Confirmed · still simulated"; copy.textContent = evaluation.fixture.confirmedOutput; return; }
    if (resolution === "rejected") { title.textContent = "Operator rejected candidate"; copy.textContent = "No request emitted · rejection retained only in this page state."; return; }
    title.textContent = "Nothing leaves the gate"; copy.textContent = "No command has been emitted.";
  }
  function render() {
    const evaluation = result();
    document.getElementById("authored-phrase").textContent = evaluation.fixture.authoredPhrase;
    document.getElementById("lock-state").textContent = unlocked ? "READY · SIMULATED" : "LOCKED";
    lockToggle.textContent = unlocked ? "Lock concept" : "Unlock concept";
    document.getElementById("raw-egress").textContent = "0";
    document.getElementById("text-egress").textContent = String(textEgress);
    document.getElementById("egress-event").textContent = lastEgressEvent;
    renderChart(evaluation.fixture);
    document.querySelectorAll(".stage-rail li").forEach((item, index) => {
      item.classList.toggle("complete", index < stage);
      item.classList.toggle("current", index === stage);
    });
    document.getElementById("stage-status").textContent = `${stage === 0 ? "Ready" : `Stage ${stage + 1} / 5`} · ${core.stageLabel(stage, evaluation)}`;
    setUnlocked("feature-card", stage >= 1, stage >= 1 ? "AUTHORED VALUES" : "WAITING");
    setUnlocked("candidate-card", stage >= 2, stage >= 2 ? "SCRIPTED OUTPUT" : "WAITING");
    for (const name of ["envelope", "timing", "stability"]) document.getElementById(`feature-${name}`).textContent = stage >= 1 ? evaluation.fixture.features[name] : "—";
    renderCandidates(evaluation); renderDecision(evaluation); renderOutput(evaluation);
    const unresolvedHumanGate = stage === 3 && (evaluation.decision === "candidate" || repairSelected);
    advance.disabled = !unlocked || stage >= 4 || unresolvedHumanGate;
    autoRun.disabled = !unlocked || stage >= 3;
    select.disabled = !unlocked;
    advance.querySelector("span").textContent = !unlocked ? "Unlock to begin" : (stage >= 4 ? "Pipeline complete" : (unresolvedHumanGate ? "Resolve human gate" : (stage === 3 ? "Finalize rejection" : "Run next stage")));
  }
  function reset() {
    stopTimer(); stage = 0; resolution = null; repairSelected = false; textEgress = 0;
    lastEgressEvent = "Reset complete · no simulated egress retained.";
    render();
    if (ephemeralControl.checked) document.getElementById("stage-status").textContent = "Reset · fixture view reconstructed from authored constants";
  }
  function nextStage() {
    if (!unlocked) return;
    const evaluation = result();
    const transition = core.advanceStage(stage, evaluation.decision, repairSelected);
    stage = transition.stage;
    if (transition.resolution) resolution = transition.resolution;
    render();
    if (stage >= 3) stopTimer();
  }
  function resolve(value) {
    const evaluation = result();
    if (stage !== 3 || !unlocked || !core.canResolve(evaluation.decision, repairSelected, value)) return;
    resolution = value; stage = 4; stopTimer();
    if (value === "confirmed") { textEgress += 1; lastEgressEvent = `SIMULATED confirmed text staged · ${repairSelected ? evaluation.fixture.repairCandidate.intent : evaluation.top.intent}`; }
    else lastEgressEvent = "Operator rejection · no simulated text egress.";
    render();
  }
  function startAuto() {
    if (!unlocked) return;
    if (timer) { stopTimer(); return; }
    if (stage >= 4) reset();
    autoRun.textContent = "Pause auto-run";
    const delay = reducedMotion ? 350 : 850;
    timer = window.setInterval(nextStage, delay);
  }
  select.addEventListener("change", reset);
  advance.addEventListener("click", nextStage);
  autoRun.addEventListener("click", startAuto);
  resetButton.addEventListener("click", reset);
  lockToggle.addEventListener("click", () => {
    unlocked = !unlocked;
    if (!unlocked) { stopTimer(); stage = 0; resolution = null; repairSelected = false; lastEgressEvent = "Concept locked · output gate closed."; }
    else lastEgressEvent = "Concept unlocked deliberately · no data transmitted.";
    render();
  });
  confirmButton.addEventListener("click", () => resolve("confirmed"));
  repairButton.addEventListener("click", () => { repairSelected = true; resolution = null; lastEgressEvent = "Manual authored repair selected · still behind confirmation gate."; render(); });
  rejectButton.addEventListener("click", () => resolve("rejected"));
  confirmationControl.addEventListener("change", render);
  document.addEventListener("keydown", (event) => {
    if (["SELECT", "INPUT", "BUTTON"].includes(event.target.tagName) && event.key === " ") return;
    if (event.key === " ") { event.preventDefault(); nextStage(); }
    if (event.key.toLowerCase() === "r") reset();
    if (event.key.toLowerCase() === "l") lockToggle.click();
    if (["1", "2", "3"].includes(event.key) && unlocked) { select.selectedIndex = Number(event.key) - 1; reset(); }
  });
  render();
})();

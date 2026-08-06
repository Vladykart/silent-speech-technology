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
  const svgNamespace = "http://www.w3.org/2000/svg";

  let stage = 0;
  let resolution = null;
  let repairSelected = false;
  let unlocked = false;
  let textEgress = 0;
  let lastEgressEvent = "Nothing transmitted. This is ephemeral page state.";
  let timer = null;

  function evaluation() {
    return core.evaluateFixture(select.value);
  }

  function stopTimer() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
    autoRun.textContent = "Play to human gate";
  }

  function createSvgElement(name, attributes) {
    const element = document.createElementNS(svgNamespace, name);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
    return element;
  }

  function linePath(values, channel) {
    const xStep = 700 / (values.length - 1);
    const baseline = 21 + channel * 28;
    return values.map((value, index) => `${index === 0 ? "M" : "L"}${44 + index * xStep},${baseline - (value - 43) * 0.19}`).join(" ");
  }

  function renderChart(selectedFixture) {
    const chart = document.getElementById("signal-chart");
    const fragment = document.createDocumentFragment();
    selectedFixture.channels.forEach((values, channel) => {
      const baseline = 21 + channel * 28;
      fragment.append(createSvgElement("path", { class: "chart-grid", d: `M44 ${baseline}H756` }));
      fragment.append(createSvgElement("path", {
        class: `signal-line channel-${channel + 1}`,
        d: linePath(values, channel),
        pathLength: "100"
      }));
      const label = createSvgElement("text", { class: "chart-label", x: "7", y: baseline + 3 });
      label.textContent = `S${channel + 1}`;
      fragment.append(label);
    });
    chart.replaceChildren(fragment);
  }

  function setCardState(id, available, stateText) {
    const card = document.getElementById(id);
    card.classList.toggle("locked", !available);
    card.querySelector(".card-state").textContent = stateText;
  }

  function renderCandidates(result) {
    const list = document.getElementById("candidate-list");
    const tokens = document.getElementById("token-stream");
    if (stage < 3) {
      tokens.textContent = "—";
      const waiting = document.createElement("p");
      waiting.textContent = "No candidates yet.";
      list.replaceChildren(waiting);
      return;
    }

    tokens.textContent = result.fixture.ctcFrames.join(" · ");
    list.replaceChildren(...result.candidates.map((candidate) => {
      const row = document.createElement("div");
      row.className = "candidate";
      const text = document.createElement("span");
      text.textContent = candidate.text;
      const score = document.createElement("strong");
      score.textContent = candidate.confidence.toFixed(2);
      const meter = document.createElement("progress");
      meter.max = 1;
      meter.value = candidate.confidence;
      meter.setAttribute("aria-label", `Authored score ${candidate.confidence.toFixed(2)} for ${candidate.text}`);
      row.append(text, score, meter);
      return row;
    }));
  }

  function renderDecision(result) {
    const box = document.getElementById("decision-state");
    const title = box.querySelector("strong");
    const copy = box.querySelector("p");
    const icon = box.querySelector(".decision-icon");
    box.className = "decision-state waiting";
    confirmButton.disabled = true;
    repairButton.disabled = true;
    rejectButton.disabled = true;
    rejectButton.textContent = "Reject candidate";

    if (!unlocked) {
      icon.textContent = "⌁";
      title.textContent = "Concept decoder locked";
      copy.textContent = "Unlock is deliberate. The staged output channel is closed.";
      return;
    }

    if (stage < 4) {
      icon.textContent = "···";
      title.textContent = "Awaiting policy gate";
      copy.textContent = "Synthetic playback is local. No output can occur before abstention and explicit human review.";
      return;
    }

    if (resolution !== null) {
      box.className = `decision-state ${resolution === "confirmed" ? "resolved" : "reject"}`;
      icon.textContent = resolution === "confirmed" ? "✓" : "×";
      title.textContent = resolution === "confirmed" ? "Human gate resolved" : "Output rejected";
      copy.textContent = resolution === "confirmed" ? "The operator explicitly confirmed this simulated state." : "The candidate was rejected. No output was staged.";
      return;
    }

    if (result.decision === "reject" && repairSelected) {
      box.className = "decision-state candidate";
      icon.textContent = "↺";
      title.textContent = "Authored repair selected";
      copy.textContent = `Manual fallback “${result.fixture.repairCandidate.text}” is still blocked pending explicit confirmation.`;
      confirmButton.disabled = !confirmationControl.checked;
      rejectButton.disabled = false;
      rejectButton.textContent = "Reject repaired candidate";
      return;
    }

    if (result.decision === "reject") {
      box.className = "decision-state reject";
      icon.textContent = "×";
      title.textContent = "Abstain · uncertain fixture";
      copy.textContent = `Top authored score ${result.top.confidence.toFixed(2)} is below the illustrative ${result.threshold.toFixed(2)} rule. Output is blocked.`;
      repairButton.disabled = !result.fixture.repairCandidate;
      rejectButton.disabled = false;
      rejectButton.textContent = "Finalize abstention";
      return;
    }

    box.className = "decision-state candidate";
    icon.textContent = result.fixture.safetySensitive ? "!" : "?";
    title.textContent = result.fixture.safetySensitive ? "Mandatory confirmation · state change" : "Explicit confirmation required";
    copy.textContent = confirmationControl.checked
      ? `“${result.top.text}” cleared the authored rule but remains blocked until confirmation.`
      : "Confirmation policy is off, so output remains blocked. Turning it off never bypasses the gate.";
    confirmButton.disabled = !confirmationControl.checked;
    rejectButton.disabled = false;
  }

  function renderOutput(result) {
    const title = document.getElementById("output-title");
    const copy = document.getElementById("output-copy");

    if (result.decision === "reject" && stage >= 4 && !repairSelected && resolution !== "rejected") {
      title.textContent = "Abstained safely · simulated";
      copy.textContent = "No request staged · choose the authored repair, another input, or stop.";
      return;
    }
    if (resolution === "confirmed") {
      title.textContent = repairSelected ? "Repaired + confirmed · simulated" : "Confirmed · simulated only";
      copy.textContent = result.fixture.confirmedOutput;
      return;
    }
    if (resolution === "rejected") {
      title.textContent = "Rejected · gate closed";
      copy.textContent = "No request staged. Rejection exists only in current page memory.";
      return;
    }
    title.textContent = "Nothing leaves the gate";
    copy.textContent = "No command has been emitted.";
  }

  function renderProcessing() {
    document.getElementById("filter-step").classList.toggle("active", stage >= 1);
    document.getElementById("window-step").classList.toggle("active", stage >= 1);
    document.getElementById("encoder-step").classList.toggle("active", stage >= 3);
  }

  function render() {
    const result = evaluation();
    document.getElementById("authored-phrase").textContent = result.fixture.authoredPhrase;
    document.getElementById("fixture-consequence").textContent = result.fixture.consequence.toUpperCase();
    document.getElementById("lock-state").textContent = unlocked ? "READY · SIMULATED" : "LOCKED";
    document.getElementById("fixture-clock").textContent = `AUTHORED ELAPSED · ${String(result.fixture.timings[stage]).padStart(3, "0")} ms*`;
    lockToggle.textContent = unlocked ? "Lock concept" : "Unlock concept";
    document.getElementById("raw-egress").textContent = "0";
    document.getElementById("text-egress").textContent = String(textEgress);
    document.getElementById("egress-event").textContent = lastEgressEvent;

    document.querySelectorAll(".stage-rail li").forEach((item, index) => {
      item.classList.toggle("complete", index < stage);
      item.classList.toggle("current", index === stage);
    });

    document.getElementById("stage-status").textContent = `${stage === 0 ? "Ready" : `Stage ${stage + 1} / ${core.STAGE_COUNT}`} · ${core.stageLabel(stage, result)}`;
    setCardState("feature-card", stage >= 2, stage >= 2 ? "AUTHORED VALUES" : "WAITING");
    setCardState("candidate-card", stage >= 3, stage >= 3 ? "SCRIPTED OUTPUT" : "WAITING");
    for (const name of ["envelope", "timing", "stability"]) {
      document.getElementById(`feature-${name}`).textContent = stage >= 2 ? result.fixture.features[name] : "—";
    }

    renderProcessing();
    renderCandidates(result);
    renderDecision(result);
    renderOutput(result);

    const unresolvedHumanGate = stage === 4 && (result.decision === "candidate" || repairSelected);
    advance.disabled = !unlocked || stage >= 5 || unresolvedHumanGate;
    autoRun.disabled = !unlocked || stage >= 4;
    select.disabled = !unlocked;
    advance.querySelector("span").textContent = !unlocked
      ? "Unlock to begin"
      : stage >= 5
        ? "Pipeline complete"
        : unresolvedHumanGate
          ? "Resolve human gate"
          : stage === 4
            ? "Finalize abstention"
            : "Run next stage";
  }

  function reset() {
    stopTimer();
    stage = 0;
    resolution = null;
    repairSelected = false;
    textEgress = 0;
    lastEgressEvent = "Reset complete · no simulated egress retained.";
    renderChart(evaluation().fixture);
    render();
    if (ephemeralControl.checked) document.getElementById("stage-status").textContent = "Reset · synthetic fixture reconstructed from bundled constants";
  }

  function nextStage() {
    if (!unlocked) return;
    const result = evaluation();
    const transition = core.advanceStage(stage, result.decision, repairSelected);
    stage = transition.stage;
    if (transition.resolution !== null) resolution = transition.resolution;
    render();
    if (stage >= 4) stopTimer();
  }

  function resolve(value) {
    const result = evaluation();
    if (stage !== 4 || !unlocked || !core.canResolve(result.decision, repairSelected, value)) return;
    if (value === "confirmed" && !confirmationControl.checked) return;

    resolution = value;
    stage = 5;
    stopTimer();
    if (core.canEmit(result.fixture, result.decision, repairSelected, resolution, confirmationControl.checked)) {
      textEgress += 1;
      const intent = repairSelected ? result.fixture.repairCandidate.intent : result.top.intent;
      lastEgressEvent = `SIMULATED text staged locally · ${intent} · no network transmission.`;
    } else {
      lastEgressEvent = "Operator rejection · no simulated text egress and no network transmission.";
    }
    render();
  }

  function startAuto() {
    if (!unlocked) return;
    if (timer !== null) {
      stopTimer();
      return;
    }
    if (stage >= 5) reset();
    autoRun.textContent = "Pause fixture playback";
    const playbackPace = reducedMotion ? 180 : 620;
    timer = window.setInterval(nextStage, playbackPace);
  }

  select.addEventListener("change", reset);
  advance.addEventListener("click", nextStage);
  autoRun.addEventListener("click", startAuto);
  resetButton.addEventListener("click", reset);
  lockToggle.addEventListener("click", () => {
    unlocked = !unlocked;
    if (!unlocked) {
      stopTimer();
      stage = 0;
      resolution = null;
      repairSelected = false;
      textEgress = 0;
      lastEgressEvent = "Concept locked · output gate closed · no network transmission.";
    } else {
      lastEgressEvent = "Concept unlocked deliberately · no data transmitted.";
      renderChart(evaluation().fixture);
    }
    render();
  });
  confirmButton.addEventListener("click", () => resolve("confirmed"));
  repairButton.addEventListener("click", () => {
    const result = evaluation();
    if (stage !== 4 || result.decision !== "reject" || !result.fixture.repairCandidate) return;
    repairSelected = true;
    resolution = null;
    lastEgressEvent = "Manual authored repair selected · still behind confirmation · no transmission.";
    render();
  });
  rejectButton.addEventListener("click", () => resolve("rejected"));
  confirmationControl.addEventListener("change", render);

  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (["SELECT", "INPUT", "BUTTON", "TEXTAREA", "A"].includes(event.target.tagName)) return;
    if (event.key === " ") {
      event.preventDefault();
      nextStage();
    } else if (event.key.toLowerCase() === "r") {
      reset();
    } else if (event.key.toLowerCase() === "l") {
      lockToggle.click();
    } else if (["1", "2", "3"].includes(event.key) && unlocked) {
      select.selectedIndex = Number(event.key) - 1;
      reset();
    }
  });

  renderChart(evaluation().fixture);
  render();
})();

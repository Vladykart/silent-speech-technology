(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const health = $("#service-health");
  const startButton = $("#start");
  const stopButton = $("#stop");
  const captureState = $("#capture-state");
  const elapsed = $("#elapsed");
  const sampleCount = $("#sample-count");
  const featureShape = $("#feature-shape");
  const featureBars = $("#feature-bars");
  const latency = $("#latency");
  const candidates = $("#candidates");
  const rawCtc = $("#raw-ctc");
  const confidence = $("#confidence");
  const decisionBox = $("#decision-box");
  const decisionLabel = $("#decision-label");
  const decisionTitle = $("#decision-title");
  const decisionReason = $("#decision-reason");
  const stagedOutput = $("#staged-output");
  const outputStatus = $("#output-status");
  const confirmButton = $("#confirm");
  const rejectButton = $("#reject");
  const repairButton = $("#repair");
  const safetyRow = $("#safety-row");
  const safetyAck = $("#safety-ack");
  const eventLog = $("#event-log");
  const canvas = $("#signal-canvas");
  const context = canvas.getContext("2d");
  let sessionId = null;
  let streamAbort = null;
  let startedAt = 0;
  let ticker = null;
  let points = [[], [], [], []];
  let totalSamples = 0;
  let safetySensitive = false;

  function log(message) {
    if (eventLog.children.length === 1 && eventLog.textContent.includes("Ready.")) eventLog.innerHTML = "";
    const item = document.createElement("li");
    const time = document.createElement("time");
    const text = document.createElement("span");
    time.textContent = new Date().toLocaleTimeString([], {hour12: false});
    text.textContent = message;
    item.append(time, text);
    eventLog.prepend(item);
  }

  function setState(state, label = state.toUpperCase()) {
    captureState.className = `state ${state}`;
    captureState.textContent = label;
  }

  function stage(name) {
    const stages = ["raw_signal", "features", "model", "decision"];
    const active = stages.indexOf(name);
    document.querySelectorAll(".rail li").forEach((item, index) => {
      item.classList.toggle("active", index === active);
      item.classList.toggle("done", index < active);
    });
  }

  function resetDisplay() {
    points = [[], [], [], []]; totalSamples = 0; drawSignal();
    sampleCount.textContent = "0 samples";
    featureShape.textContent = "—";
    featureBars.innerHTML = "<p>Waiting for real preprocessing…</p>";
    latency.textContent = "— ms";
    candidates.innerHTML = "<p>Forward pass pending…</p>";
    rawCtc.textContent = "—"; confidence.textContent = "—";
    stagedOutput.textContent = "—"; outputStatus.textContent = "Nothing committed";
    safetyRow.classList.add("hidden"); safetyAck.checked = false;
    safetySensitive = false;
    confirmButton.disabled = true; rejectButton.disabled = true;
    repairButton.classList.add("hidden");
    decisionBox.className = "decision-box idle";
    decisionLabel.textContent = "CAPTURING";
    decisionTitle.textContent = "Pipeline in progress";
    decisionReason.textContent = "Raw frames are volatile and remain local.";
    document.querySelectorAll(".rail li").forEach(item => item.classList.remove("active", "done"));
  }

  function drawSignal() {
    const width = canvas.width, height = canvas.height;
    context.fillStyle = "#101510"; context.fillRect(0, 0, width, height);
    context.strokeStyle = "#273329"; context.lineWidth = 1;
    for (let row = 0; row < 4; row++) {
      const center = (row + .5) * height / 4;
      context.beginPath(); context.moveTo(0, center); context.lineTo(width, center); context.stroke();
      context.fillStyle = "#637363"; context.font = "18px ui-monospace"; context.fillText(`CH ${row + 1}`, 12, center - 8);
    }
    const colors = ["#c8ff3d", "#63d5b8", "#68a7ff", "#f0a254"];
    points.forEach((channel, row) => {
      if (channel.length < 2) return;
      context.strokeStyle = colors[row]; context.lineWidth = 2; context.beginPath();
      channel.forEach((value, index) => {
        const x = index / (channel.length - 1) * width;
        const y = (row + .5) * height / 4 - Math.max(-1.8, Math.min(1.8, value)) * 21;
        if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
      });
      context.stroke();
    });
  }

  function addRawFrame(event) {
    event.preview.forEach(sample => sample.forEach((value, channel) => points[channel].push(value)));
    points = points.map(channel => channel.slice(-420));
    totalSamples += event.sample_count;
    sampleCount.textContent = `${totalSamples.toLocaleString()} samples`;
    drawSignal();
  }

  function showFeatures(event) {
    featureShape.textContent = event.shape.join(" × ");
    const values = event.preview.flat().slice(0, 80);
    const maximum = Math.max(...values.map(Math.abs), .001);
    featureBars.innerHTML = values.map(value => `<i style="--height:${Math.max(3, Math.abs(value) / maximum * 100).toFixed(1)}%" title="${Number(value).toFixed(4)}"></i>`).join("");
  }

  function showInference(event) {
    latency.textContent = `${Number(event.latency_ms).toFixed(1)} ms`;
    rawCtc.textContent = event.raw_ctc || "∅";
    confidence.textContent = Number(event.confidence).toFixed(3);
    candidates.innerHTML = event.candidates.map((candidate, index) =>
      `<div class="candidate"><i>${index + 1}</i><b>${escapeHtml(candidate.text)}</b><span>${Number(candidate.score).toFixed(3)}</span></div>`
    ).join("");
    log(`Real forward pass: ${event.parameter_count.toLocaleString()} trained parameters / ${Number(event.latency_ms).toFixed(1)} ms.`);
  }

  function showDecision(event) {
    setState(event.state, event.state === "confirm_required" ? "CONFIRM" : event.state.toUpperCase());
    decisionBox.className = `decision-box ${event.state}`;
    decisionReason.textContent = event.reason;
    stagedOutput.textContent = event.prediction;
    safetySensitive = event.safety_sensitive;
    if (event.state === "abstain") {
      decisionLabel.textContent = "ABSTAINED";
      decisionTitle.textContent = "No output committed";
      outputStatus.textContent = "Rejected below threshold";
      repairButton.classList.remove("hidden");
      decisionBox.querySelector(".decision-icon").textContent = "×";
      log("Decoder abstained. Output remains empty; repair is available.");
    } else {
      decisionLabel.textContent = event.safety_sensitive ? "SAFETY HOLD" : "HUMAN HOLD";
      decisionTitle.textContent = event.safety_sensitive ? "Explicit review required" : "Confirm decoded command";
      outputStatus.textContent = "Staged—not committed";
      confirmButton.disabled = event.safety_sensitive;
      rejectButton.disabled = false;
      safetyRow.classList.toggle("hidden", !event.safety_sensitive);
      decisionBox.querySelector(".decision-icon").textContent = "?";
      log(event.safety_sensitive ? "Safety-sensitive candidate held for acknowledgement." : "Candidate held for operator confirmation.");
    }
  }

  function escapeHtml(value) {
    const element = document.createElement("span"); element.textContent = value; return element.innerHTML;
  }

  async function handleEvent(event) {
    if (event.stage) stage(event.stage);
    switch (event.event) {
      case "acquisition_started": setState("running", "CAPTURING"); log("Simulated noisy acquisition started; no sensor is connected."); break;
      case "raw_frame": addRawFrame(event); break;
      case "preprocessing": log("Real high-pass, normalization and feature extraction running."); break;
      case "features": showFeatures(event); break;
      case "inference": showInference(event); break;
      case "decision": showDecision(event); stopButton.disabled = true; startButton.disabled = false; clearInterval(ticker); break;
      case "stopped": setState("stopped"); log("Capture stopped; no output committed."); break;
      case "error": setState("error"); log(event.detail || "Local pipeline error."); startButton.disabled = false; stopButton.disabled = true; break;
    }
  }

  async function consume(path) {
    streamAbort = new AbortController();
    const response = await fetch(path, {signal: streamAbort.signal});
    if (!response.ok || !response.body) throw new Error(`stream failed (${response.status})`);
    const reader = response.body.getReader(), decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const {done, value} = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), {stream: !done});
      const lines = buffer.split("\n"); buffer = lines.pop() || "";
      for (const line of lines) if (line.trim()) await handleEvent(JSON.parse(line));
      if (done) break;
    }
  }

  async function createAndRun() {
    resetDisplay();
    const scenario = document.querySelector('input[name="scenario"]:checked').value;
    const response = await fetch("/api/sessions", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({scenario})});
    if (!response.ok) throw new Error("could not create local session");
    const session = await response.json(); sessionId = session.id;
    startedAt = performance.now();
    elapsed.textContent = "0.0 S";
    ticker = setInterval(() => elapsed.textContent = `${((performance.now() - startedAt) / 1000).toFixed(1)} S`, 100);
    startButton.disabled = true; stopButton.disabled = false;
    await consume(session.stream);
  }

  startButton.addEventListener("click", () => createAndRun().catch(error => { setState("error"); log(error.message); startButton.disabled = false; stopButton.disabled = true; }));
  stopButton.addEventListener("click", async () => {
    if (!sessionId) return;
    await fetch(`/api/sessions/${sessionId}/stop`, {method: "POST"});
    if (streamAbort) streamAbort.abort();
    clearInterval(ticker); setState("stopped"); startButton.disabled = false; stopButton.disabled = true; log("Operator stopped simulated capture.");
  });
  confirmButton.addEventListener("click", async () => {
    const response = await fetch(`/api/sessions/${sessionId}/decision`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({action: "confirm", safety_acknowledged: safetyAck.checked})});
    const result = await response.json();
    if (!response.ok) { log(result.detail || "Confirmation refused."); return; }
    setState("confirmed"); decisionBox.className = "decision-box confirmed"; decisionLabel.textContent = "CONFIRMED"; decisionTitle.textContent = "Local output committed"; decisionReason.textContent = "Human confirmation completed the command-channel gate."; outputStatus.textContent = "Committed locally"; confirmButton.disabled = true; rejectButton.disabled = true; safetyRow.classList.add("hidden"); decisionBox.querySelector(".decision-icon").textContent = "✓"; log(`Operator confirmed local output: ${result.output}.`);
  });
  rejectButton.addEventListener("click", async () => {
    const response = await fetch(`/api/sessions/${sessionId}/decision`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({action: "reject"})});
    const result = await response.json();
    if (!response.ok) { log(result.detail); return; }
    setState("abstain", "REJECTED"); decisionBox.className = "decision-box abstain"; decisionLabel.textContent = "REJECTED"; decisionTitle.textContent = "No output committed"; decisionReason.textContent = "The operator rejected the model candidate."; outputStatus.textContent = "Rejected by operator"; confirmButton.disabled = true; rejectButton.disabled = true; safetyRow.classList.add("hidden"); repairButton.classList.toggle("hidden", !result.repair_available); log("Operator rejected candidate; no output committed.");
  });
  repairButton.addEventListener("click", async () => {
    const response = await fetch(`/api/sessions/${sessionId}/repair`, {method: "POST"});
    const result = await response.json();
    if (!response.ok) { log(result.detail); return; }
    resetDisplay(); setState("running", "REPAIR"); startButton.disabled = true; stopButton.disabled = false; startedAt = performance.now(); ticker = setInterval(() => elapsed.textContent = `${((performance.now() - startedAt) / 1000).toFixed(1)} S`, 100); log("Repair: new lower-noise simulated acquisition; downstream code is unchanged.");
    consume(result.stream).catch(error => { setState("error"); log(error.message); });
  });
  safetyAck.addEventListener("change", () => { if (safetySensitive) confirmButton.disabled = !safetyAck.checked; });
  document.querySelectorAll('.scenario input').forEach(input => input.addEventListener("change", () => document.querySelectorAll(".scenario").forEach(label => label.classList.toggle("selected", label.querySelector("input").checked))));
  $("#clear-log").addEventListener("click", () => { eventLog.innerHTML = "<li><time>—</time><span>Log cleared locally.</span></li>"; });

  fetch("/api/health").then(response => response.json()).then(data => { health.textContent = `LOCAL SERVICE · ${data.model.parameters.toLocaleString()} PARAMS`; health.classList.add("online"); }).catch(() => { health.textContent = "LOCAL SERVICE · OFFLINE"; setState("error", "BACKEND OFFLINE"); });
  drawSignal();
})();

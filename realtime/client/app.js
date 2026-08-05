(() => {
  "use strict";

  const contract = globalThis.ReplayContract;
  if (!contract) throw new Error("replay contract did not load");
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const elements = {
    health: $("#service-health"),
    errorBanner: $("#error-banner"),
    errorMessage: $("#error-message"),
    stageAnnouncer: $("#stage-announcer"),
    captureState: $("#capture-state"),
    modelStageState: $("#model-stage-state"),
    resultStageState: $("#result-stage-state"),
    progressDataState: $("#progress-data-state"),
    progressModelState: $("#progress-model-state"),
    progressResultState: $("#progress-result-state"),
    scenarioList: $("#scenario-list"),
    scenarioContractState: $("#scenario-contract-state"),
    futureList: $("#future-command-list"),
    selectedExample: $("#selected-example"),
    datasetLabel: $("#dataset-label"),
    actualModelInput: $("#actual-model-input"),
    inputCandidate: $("#input-candidate"),
    startButton: $("#start"),
    stopButton: $("#stop"),
    modelTensorShape: $("#model-tensor-shape"),
    sampleCount: $("#sample-count"),
    canvas: $("#signal-canvas"),
    modelRunTitle: $("#model-run-title"),
    latency: $("#latency"),
    featureShape: $("#feature-shape"),
    featureBars: $("#feature-bars"),
    rawCtc: $("#raw-ctc"),
    candidates: $("#candidates"),
    candidateHold: $("#candidate-hold"),
    diagnosticScore: $("#diagnostic-score"),
    scoreMeter: $("#score-meter"),
    recordReference: $("#record-reference"),
    referenceStatus: $("#reference-status"),
    decisionBox: $("#decision-box"),
    decisionIcon: $(".decision-icon", $("#decision-box")),
    decisionLabel: $("#decision-label"),
    decisionTitle: $("#decision-title"),
    decisionReason: $("#decision-reason"),
    heldCandidate: $("#held-candidate"),
    heldStatus: $("#held-status"),
    safetyRow: $("#safety-row"),
    safetyAck: $("#safety-ack"),
    confirmButton: $("#confirm"),
    rejectButton: $("#reject"),
    repairButton: $("#repair"),
    finalCard: $("#final-card"),
    finalOutput: $("#final-output"),
    outputStatus: $("#output-status"),
    eventLog: $("#event-log"),
    clearLog: $("#clear-log"),
  };

  const context = elements.canvas.getContext("2d");
  const exampleByScenario = new Map(contract.RECORDED_EXAMPLES.map((example) => [example.scenario, example]));
  const revealedReferences = new Map();
  let replayState = contract.initialState();
  let currentProgressStage = "data-collection";
  let sessionId = null;
  let sessionScenario = "clear";
  let streamAbort = null;
  let points = [[], [], [], []];
  let totalSamples = 0;
  let currentCandidate = "";
  let safetySensitive = false;
  let operatorStopped = false;

  function selectedScenario() {
    return $('input[name="scenario"]:checked', elements.scenarioList)?.value || "clear";
  }

  function selectedExample() {
    return exampleByScenario.get(selectedScenario());
  }

  function setPill(element, state, label) {
    element.className = `state ${state}`;
    element.textContent = label;
  }

  function renderProgress(stage, announce = true) {
    const stageIndex = contract.STAGES.findIndex((item) => item.id === stage);
    if (stageIndex < 0) return;
    $$("[data-progress-stage]").forEach((item, index) => {
      item.classList.toggle("active", index === stageIndex);
      item.classList.toggle("complete", index < stageIndex);
      const link = $("a", item);
      if (index === stageIndex) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    $$('[data-stage-panel]').forEach((panel) => panel.classList.toggle("active", panel.dataset.stagePanel === stage));
    if (announce && currentProgressStage !== stage) {
      const definition = contract.STAGES[stageIndex];
      elements.stageAnnouncer.textContent = `Stage ${definition.number} of 3, ${definition.label}.`;
    }
    currentProgressStage = stage;
  }

  function log(message) {
    if (elements.eventLog.children.length === 1 && elements.eventLog.textContent.includes("Ready.")) elements.eventLog.innerHTML = "";
    const item = document.createElement("li");
    const time = document.createElement("time");
    const text = document.createElement("span");
    time.textContent = new Date().toLocaleTimeString([], {hour12: false});
    text.textContent = message;
    item.append(time, text);
    elements.eventLog.prepend(item);
  }

  function clearError() {
    elements.errorBanner.hidden = true;
    elements.errorMessage.textContent = "";
  }

  function showError(message, focus = false) {
    const safeMessage = message || "The local replay failed. No output was accepted.";
    elements.errorMessage.textContent = safeMessage;
    elements.errorBanner.hidden = false;
    setPill(elements.captureState, "error", "ERROR");
    setPill(elements.resultStageState, "error", "NO RESULT");
    elements.progressResultState.textContent = "Error · no final result";
    elements.startButton.disabled = false;
    elements.stopButton.disabled = true;
    setScenarioLocked(false);
    replayState = contract.reduce(replayState, {event: "error"});
    renderProgress(replayState.stage);
    elements.finalOutput.textContent = "No final local result";
    elements.outputStatus.textContent = "Error path · nothing accepted";
    elements.decisionBox.className = "decision-box error";
    elements.decisionLabel.textContent = "ERROR";
    elements.decisionTitle.textContent = "No result available";
    elements.decisionReason.textContent = "The replay stopped safely. No candidate was accepted or executed.";
    log(safeMessage);
    if (focus) elements.errorBanner.focus();
  }

  function setScenarioLocked(locked) {
    elements.scenarioList.disabled = locked;
  }

  function renderFutureExamples() {
    const fragment = document.createDocumentFragment();
    contract.FUTURE_COMMAND_EXAMPLES.forEach((example) => {
      const item = document.createElement("li");
      const label = document.createElement("small");
      const phrase = document.createElement("q");
      label.textContent = `${example.id} · FUTURE ONLY`;
      phrase.textContent = example.text;
      item.append(label, phrase);
      fragment.append(item);
    });
    elements.futureList.replaceChildren(fragment);
  }

  function updateSelectedExample() {
    const scenario = selectedScenario();
    const example = exampleByScenario.get(scenario);
    $$(".recorded-example", elements.scenarioList).forEach((card) => card.classList.toggle("selected", card.dataset.scenario === scenario));
    if (!example) {
      elements.startButton.disabled = true;
      showError("Recorded-example binding is unavailable. No replay started.");
      return;
    }
    elements.selectedExample.textContent = `${example.exampleId} · official recorded example`;
    const revealed = revealedReferences.get(scenario);
    elements.datasetLabel.textContent = revealed || "Sealed until this run completes inference";
    elements.actualModelInput.textContent = `Recorded sEMG tensor only · 1 kHz · 8 channels · ${example.exampleId}`;
    elements.inputCandidate.textContent = "Not available until the released model runs";
    elements.progressDataState.textContent = `${example.exampleId} selected`;
  }

  function resetRunDisplay() {
    clearError();
    replayState = contract.initialState();
    renderProgress("data-collection", false);
    points = [[], [], [], []];
    totalSamples = 0;
    currentCandidate = "";
    safetySensitive = false;
    operatorStopped = false;
    drawSignal();
    elements.sampleCount.textContent = "0 samples";
    elements.modelTensorShape.textContent = "Recorded sEMG tensor";
    elements.modelRunTitle.textContent = "Waiting for recorded input";
    elements.latency.textContent = "—";
    elements.featureShape.textContent = "—";
    elements.featureBars.innerHTML = "<span>Waiting for preprocessing…</span>";
    elements.featureBars.setAttribute("aria-label", "Feature tensor waiting for preprocessing");
    elements.rawCtc.textContent = "—";
    elements.candidates.innerHTML = "<p>Released-model forward pass pending.</p>";
    elements.candidateHold.textContent = "NO CANDIDATE";
    elements.diagnosticScore.textContent = "—";
    elements.scoreMeter.value = 0;
    elements.scoreMeter.textContent = "0";
    elements.recordReference.textContent = "Sealed until inference completes";
    elements.referenceStatus.textContent = "Never passed to the model or decoder";
    elements.decisionBox.className = "decision-box idle";
    elements.decisionIcon.textContent = "···";
    elements.decisionLabel.textContent = "WAITING";
    elements.decisionTitle.textContent = "No candidate staged";
    elements.decisionReason.textContent = "A model candidate never executes automatically. Nothing becomes a final local result without human review.";
    elements.heldCandidate.textContent = "—";
    elements.heldStatus.textContent = "Nothing staged";
    elements.safetyRow.classList.add("hidden");
    elements.safetyAck.checked = false;
    elements.confirmButton.disabled = true;
    elements.rejectButton.disabled = true;
    elements.repairButton.classList.add("hidden");
    elements.finalCard.classList.remove("accepted");
    elements.finalOutput.textContent = "—";
    elements.outputStatus.textContent = "No result accepted";
    setPill(elements.captureState, "ready", "READY");
    setPill(elements.modelStageState, "waiting", "WAITING");
    setPill(elements.resultStageState, "waiting", "WAITING");
    elements.progressModelState.textContent = "Waiting for replay";
    elements.progressResultState.textContent = "No candidate";
    updateSelectedExample();
    elements.datasetLabel.textContent = "Sealed until this run completes inference";
  }

  function resizeCanvas() {
    const rect = elements.canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const ratio = Math.min(globalThis.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rect.width * ratio));
    const height = Math.max(1, Math.round(rect.height * ratio));
    if (elements.canvas.width !== width || elements.canvas.height !== height) {
      elements.canvas.width = width;
      elements.canvas.height = height;
    }
    drawSignal();
  }

  function drawSignal() {
    const width = elements.canvas.width;
    const height = elements.canvas.height;
    context.fillStyle = "#0f1511";
    context.fillRect(0, 0, width, height);
    context.strokeStyle = "#2d3931";
    context.lineWidth = Math.max(1, width / 1600);
    const fontSize = Math.max(12, Math.round(width / 85));
    for (let row = 0; row < 4; row += 1) {
      const center = (row + .5) * height / 4;
      context.beginPath();
      context.moveTo(0, center);
      context.lineTo(width, center);
      context.stroke();
      context.fillStyle = "#7e8d81";
      context.font = `${fontSize}px ui-monospace, monospace`;
      context.fillText(`CH ${row + 1}`, Math.round(width * .012), center - Math.round(height * .035));
    }
    const colors = ["#c9ff45", "#63d5b8", "#68a7ff", "#f0a254"];
    points.forEach((channel, row) => {
      if (channel.length < 2) return;
      const mean = channel.reduce((sum, value) => sum + value, 0) / channel.length;
      const scale = Math.max(...channel.map((value) => Math.abs(value - mean)), 1);
      context.strokeStyle = colors[row];
      context.lineWidth = Math.max(1.5, width / 850);
      context.beginPath();
      channel.forEach((value, index) => {
        const x = index / (channel.length - 1) * width;
        const y = (row + .5) * height / 4 - (value - mean) / scale * height * .09;
        if (index === 0) context.moveTo(x, y);
        else context.lineTo(x, y);
      });
      context.stroke();
    });
  }

  function addRawFrame(event) {
    if (!Array.isArray(event.preview)) return;
    event.preview.forEach((sample) => sample.forEach((value, channel) => {
      if (points[channel]) points[channel].push(Number(value));
    }));
    points = points.map((channel) => channel.slice(-520));
    totalSamples += Number(event.sample_count) || 0;
    elements.sampleCount.textContent = `${totalSamples.toLocaleString()} samples`;
    drawSignal();
  }

  function showPreprocessing(event) {
    const shape = Array.isArray(event.input_shape) ? event.input_shape.map(Number) : [];
    if (shape.length === 2) {
      const label = `${shape[0].toLocaleString()} × ${shape[1]} recorded sEMG tensor only`;
      elements.modelTensorShape.textContent = label;
      elements.actualModelInput.textContent = `${label} · 1 kHz`;
    }
    setPill(elements.modelStageState, "model", "PREPROCESSING");
    elements.modelRunTitle.textContent = "Source-faithful preprocessing";
    elements.progressModelState.textContent = "Preprocessing recorded tensor";
    log("Stage 2: source-faithful preprocessing began; metadata text remains outside inference.");
  }

  function showFeatures(event) {
    const shape = Array.isArray(event.shape) ? event.shape.map(Number) : [];
    elements.featureShape.textContent = shape.length ? shape.join(" × ") : "—";
    const values = Array.isArray(event.preview) ? event.preview.flat().slice(0, 80).map(Number).filter(Number.isFinite) : [];
    const maximum = Math.max(...values.map(Math.abs), .001);
    const fragment = document.createDocumentFragment();
    values.forEach((value) => {
      const bar = document.createElement("i");
      bar.style.setProperty("--height", `${Math.max(3, Math.abs(value) / maximum * 100).toFixed(1)}%`);
      bar.title = Number(value).toFixed(4);
      fragment.append(bar);
    });
    elements.featureBars.replaceChildren(fragment);
    elements.featureBars.setAttribute("aria-label", `Extracted feature tensor, shape ${shape.join(" by ")}`);
    elements.modelRunTitle.textContent = "Running official released weights";
    elements.progressModelState.textContent = "Official weights running";
  }

  function appendCandidate(candidate, index) {
    const row = document.createElement("div");
    row.className = "candidate";
    const rank = document.createElement("i");
    const text = document.createElement("b");
    const score = document.createElement("span");
    rank.textContent = String(index + 1);
    text.textContent = String(candidate.text || "—");
    score.textContent = `ranking diagnostic ${Number(candidate.score).toFixed(3)}`;
    row.append(rank, text, score);
    elements.candidates.append(row);
  }

  function showInference(event) {
    const candidateRows = Array.isArray(event.candidates) ? event.candidates : [];
    elements.candidates.innerHTML = "";
    candidateRows.forEach(appendCandidate);
    if (!candidateRows.length) elements.candidates.innerHTML = "<p>No decoder candidates were returned.</p>";
    currentCandidate = String(candidateRows[0]?.text || "");
    elements.inputCandidate.textContent = currentCandidate ? `${currentCandidate} · model candidate only, not a final result` : "No model candidate";
    elements.heldCandidate.textContent = currentCandidate || "—";
    elements.heldStatus.textContent = currentCandidate ? "Generated by model/decoder · not accepted" : "No candidate staged";
    elements.candidateHold.textContent = "HELD · NOT EXECUTED";
    const score = Number(event.confidence);
    elements.diagnosticScore.textContent = Number.isFinite(score) ? score.toFixed(3) : "—";
    elements.scoreMeter.value = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
    elements.scoreMeter.textContent = Number.isFinite(score) ? score.toFixed(3) : "0";
    elements.rawCtc.textContent = Array.isArray(event.raw_phonemes) && event.raw_phonemes.length ? event.raw_phonemes.join(" · ") : "∅";
    elements.latency.textContent = `${Number(event.latency_ms).toFixed(1)} ms`;
    elements.modelRunTitle.textContent = "Official-weight forward pass complete";
    setPill(elements.modelStageState, "model", "MODEL COMPLETE");
    elements.progressModelState.textContent = "Inference complete";
    elements.progressResultState.textContent = "Candidate held for gate";
    log(`Released-model forward pass completed locally: ${Number(event.parameter_count).toLocaleString()} parameters; candidate held.`);
  }

  function revealReference(event) {
    if (!replayState.metadataVisible || replayState.boundaryViolation) {
      showError("Metadata boundary check failed. The dataset label remains hidden and no result can be accepted.", true);
      return;
    }
    const prompt = String(event.prompt || "Unavailable");
    revealedReferences.set(sessionScenario, prompt);
    elements.recordReference.textContent = prompt;
    elements.referenceStatus.textContent = "Revealed after inference · audit metadata only";
    elements.datasetLabel.textContent = `${prompt} · revealed after inference`;
    const card = $(`.recorded-example[data-scenario="${sessionScenario}"]`, elements.scenarioList);
    if (card) {
      const label = $(".recorded-label", card);
      label.textContent = `Post-inference dataset label: ${prompt}`;
      label.classList.add("revealed");
    }
    log("Official dataset command label revealed after inference; it was not model or decoder input.");
  }

  function showDecision(event) {
    renderProgress("process-result");
    elements.startButton.disabled = false;
    elements.stopButton.disabled = true;
    setScenarioLocked(false);
    safetySensitive = Boolean(event.safety_sensitive);
    elements.decisionBox.className = `decision-box ${event.state}`;
    elements.decisionReason.textContent = String(event.reason || "Human review is required.");
    elements.heldCandidate.textContent = currentCandidate || String(event.prediction || "—");
    elements.finalOutput.textContent = "—";
    elements.finalCard.classList.remove("accepted");
    elements.confirmButton.disabled = true;
    elements.rejectButton.disabled = true;
    elements.safetyRow.classList.add("hidden");
    elements.safetyAck.checked = false;
    elements.repairButton.classList.add("hidden");

    if (event.state === "abstain") {
      setPill(elements.captureState, "abstain", "ABSTAINED");
      setPill(elements.resultStageState, "abstain", "ABSTAINED");
      elements.decisionIcon.textContent = "×";
      elements.decisionLabel.textContent = "ABSTAINED";
      elements.decisionTitle.textContent = "No final result available";
      elements.heldStatus.textContent = "Candidate below diagnostic boundary · not accepted";
      elements.outputStatus.textContent = "Abstained below 0.60 · nothing accepted";
      elements.progressResultState.textContent = "Abstained · no final result";
      if (sessionScenario === "ambiguous") elements.repairButton.classList.remove("hidden");
      log("Diagnostic score fell below 0.60. The system abstained; no result was accepted.");
    } else {
      setPill(elements.captureState, "confirm_required", "HUMAN HOLD");
      setPill(elements.resultStageState, "confirm_required", safetySensitive ? "SAFETY HOLD" : "REVIEW REQUIRED");
      elements.decisionIcon.textContent = "?";
      elements.decisionLabel.textContent = safetySensitive ? "SAFETY HOLD" : "HUMAN HOLD";
      elements.decisionTitle.textContent = safetySensitive ? "Acknowledge before review" : "Accept or reject the candidate";
      elements.heldStatus.textContent = "Staged for human review · not a final result";
      elements.outputStatus.textContent = "Waiting for human decision";
      elements.confirmButton.disabled = safetySensitive;
      elements.rejectButton.disabled = false;
      elements.safetyRow.classList.toggle("hidden", !safetySensitive);
      elements.progressResultState.textContent = safetySensitive ? "Safety acknowledgement required" : "Human decision required";
      log(safetySensitive ? "Safety-sensitive candidate held; explicit acknowledgement is required." : "Candidate held for human confirmation or rejection.");
    }
  }

  function showStopped() {
    replayState = contract.reduce(replayState, {event: "stopped"});
    renderProgress(replayState.stage);
    setPill(elements.captureState, "stopped", "STOPPED");
    setPill(elements.resultStageState, "stopped", "NO RESULT");
    elements.decisionBox.className = "decision-box stopped";
    elements.decisionIcon.textContent = "×";
    elements.decisionLabel.textContent = "STOPPED";
    elements.decisionTitle.textContent = "Replay stopped locally";
    elements.decisionReason.textContent = "The operator stopped the replay. No candidate was accepted or executed.";
    elements.finalOutput.textContent = "No final local result";
    elements.outputStatus.textContent = "Stopped by operator · nothing accepted";
    elements.progressResultState.textContent = "Stopped · no final result";
    elements.startButton.disabled = false;
    elements.stopButton.disabled = true;
    elements.confirmButton.disabled = true;
    elements.rejectButton.disabled = true;
    setScenarioLocked(false);
  }

  async function handleEvent(event) {
    replayState = contract.reduce(replayState, event);
    renderProgress(replayState.stage);
    if (replayState.boundaryViolation) {
      showError("Replay event ordering violated the post-inference metadata boundary. No output was accepted.", true);
      if (streamAbort) streamAbort.abort();
      return;
    }
    switch (event.event) {
      case "acquisition_started":
        setPill(elements.captureState, "running", event.attempt === "repair" ? "SECOND TAKE" : "REPLAYING");
        elements.progressDataState.textContent = event.attempt === "repair" ? "Replaying second official take" : "Replaying official array";
        log("Stage 1: official recorded sEMG array replay started; no person or sensor is connected.");
        break;
      case "raw_frame":
        addRawFrame(event);
        break;
      case "preprocessing":
        showPreprocessing(event);
        break;
      case "features":
        showFeatures(event);
        break;
      case "inference":
        showInference(event);
        break;
      case "record_reference":
        revealReference(event);
        break;
      case "decision":
        showDecision(event);
        break;
      case "stopped":
        showStopped();
        log("Recorded replay stopped; no final local result was accepted.");
        break;
      case "error":
        showError(String(event.detail || "The local replay pipeline failed. No output was accepted."));
        break;
      default:
        break;
    }
  }

  async function fetchJson(path, options) {
    const response = await fetch(path, options);
    let payload = {};
    try { payload = await response.json(); } catch (_) { payload = {}; }
    if (!response.ok) throw new Error(String(payload.detail || `local request failed (${response.status})`));
    return payload;
  }

  async function consume(path) {
    const controller = new AbortController();
    streamAbort = controller;
    const response = await fetch(path, {signal: controller.signal});
    if (!response.ok || !response.body) throw new Error(`local replay stream failed (${response.status})`);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const {done, value} = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), {stream: !done});
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) if (line.trim()) await handleEvent(JSON.parse(line));
      if (done) break;
    }
    if (buffer.trim()) await handleEvent(JSON.parse(buffer));
  }

  async function runSelected() {
    resetRunDisplay();
    sessionScenario = selectedScenario();
    const example = exampleByScenario.get(sessionScenario);
    if (!example) throw new Error("selected replay is not bound to an official recorded example");
    setScenarioLocked(true);
    elements.startButton.disabled = true;
    elements.stopButton.disabled = false;
    setPill(elements.captureState, "running", "STARTING");
    const session = await fetchJson("/api/sessions", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({scenario: sessionScenario}),
    });
    if (session.example_id && session.example_id !== example.exampleId) throw new Error("recorded-example binding mismatch; replay cancelled");
    sessionId = session.id;
    await consume(session.stream);
  }

  function handleRunError(error) {
    if (error?.name === "AbortError" && operatorStopped) return;
    showError(String(error?.message || "The local replay could not run. No output was accepted."), true);
  }

  async function stopReplay() {
    if (!sessionId) return;
    operatorStopped = true;
    try {
      await fetchJson(`/api/sessions/${sessionId}/stop`, {method: "POST"});
      if (streamAbort) streamAbort.abort();
      showStopped();
      log("Operator stopped the recorded replay. No result was accepted.");
    } catch (error) {
      handleRunError(error);
    }
  }

  async function confirmCandidate() {
    try {
      const result = await fetchJson(`/api/sessions/${sessionId}/decision`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({action: "confirm", safety_acknowledged: elements.safetyAck.checked}),
      });
      replayState = contract.reduce(replayState, {event: "local_confirmed"});
      renderProgress(replayState.stage);
      setPill(elements.captureState, "confirmed", "ACCEPTED");
      setPill(elements.resultStageState, "confirmed", "FINAL LOCAL RESULT");
      elements.decisionBox.className = "decision-box confirmed";
      elements.decisionIcon.textContent = "✓";
      elements.decisionLabel.textContent = "HUMAN ACCEPTED";
      elements.decisionTitle.textContent = "Final local result recorded";
      elements.decisionReason.textContent = "Human review completed the local gate. No external action or actuation occurred.";
      elements.heldStatus.textContent = "Reviewed and accepted locally";
      elements.finalOutput.textContent = String(result.output || currentCandidate || "—");
      elements.outputStatus.textContent = "Accepted in this browser/service session · no actuation";
      elements.finalCard.classList.add("accepted");
      elements.confirmButton.disabled = true;
      elements.rejectButton.disabled = true;
      elements.safetyRow.classList.add("hidden");
      elements.progressResultState.textContent = "Human accepted local result";
      log(`Human accepted a final local result: ${String(result.output || currentCandidate)}. No action was connected.`);
      elements.finalCard.focus();
    } catch (error) {
      showError(String(error?.message || "The local service refused confirmation. No result was accepted."), true);
    }
  }

  async function rejectCandidate() {
    try {
      const result = await fetchJson(`/api/sessions/${sessionId}/decision`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({action: "reject"}),
      });
      replayState = contract.reduce(replayState, {event: "local_rejected"});
      renderProgress(replayState.stage);
      setPill(elements.captureState, "rejected", "REJECTED");
      setPill(elements.resultStageState, "rejected", "NO RESULT");
      elements.decisionBox.className = "decision-box rejected";
      elements.decisionIcon.textContent = "×";
      elements.decisionLabel.textContent = "REJECTED";
      elements.decisionTitle.textContent = "No final result accepted";
      elements.decisionReason.textContent = "The human reviewer rejected the model candidate. It was not executed.";
      elements.heldStatus.textContent = "Rejected by human reviewer";
      elements.finalOutput.textContent = "No final local result";
      elements.outputStatus.textContent = "Rejected by human reviewer · nothing accepted";
      elements.confirmButton.disabled = true;
      elements.rejectButton.disabled = true;
      elements.safetyRow.classList.add("hidden");
      elements.repairButton.classList.toggle("hidden", !result.repair_available);
      elements.progressResultState.textContent = "Rejected · no final result";
      log("Human reviewer rejected the model candidate; no result was accepted or executed.");
      elements.finalCard.focus();
    } catch (error) {
      showError(String(error?.message || "The local service could not reject the candidate safely."), true);
    }
  }

  async function repairReplay() {
    try {
      const result = await fetchJson(`/api/sessions/${sessionId}/repair`, {method: "POST"});
      resetRunDisplay();
      sessionScenario = "ambiguous";
      setScenarioLocked(true);
      elements.startButton.disabled = true;
      elements.stopButton.disabled = false;
      setPill(elements.captureState, "running", "SECOND TAKE");
      log("Repair selected: a second official recorded take of the same prompt; downstream code is unchanged.");
      await consume(result.stream);
    } catch (error) {
      handleRunError(error);
    }
  }

  function validateScenarioContract(payload) {
    if (!Array.isArray(payload.items)) throw new Error("scenario contract unavailable");
    contract.RECORDED_EXAMPLES.forEach((expected) => {
      const item = payload.items.find((candidate) => candidate.id === expected.scenario);
      if (!item || item.example_id !== expected.exampleId || item.classification !== expected.classification || item.executable !== true || item.recorded_takes !== expected.recordedTakes) {
        throw new Error(`recorded-example binding mismatch for ${expected.exampleId}`);
      }
    });
    const references = ["What news?", "09:48 AM", "Keep back!"];
    const serialized = JSON.stringify(payload);
    if (references.some((reference) => serialized.includes(reference))) throw new Error("scenario contract revealed a dataset label before inference");
    elements.scenarioContractState.textContent = "3 RECORDED PATHS · 4 LOCAL ARRAYS";
  }

  elements.startButton.addEventListener("click", () => runSelected().catch(handleRunError));
  elements.stopButton.addEventListener("click", stopReplay);
  elements.confirmButton.addEventListener("click", confirmCandidate);
  elements.rejectButton.addEventListener("click", rejectCandidate);
  elements.repairButton.addEventListener("click", repairReplay);
  elements.safetyAck.addEventListener("change", () => {
    if (safetySensitive) elements.confirmButton.disabled = !elements.safetyAck.checked;
  });
  elements.scenarioList.addEventListener("change", updateSelectedExample);
  elements.clearLog.addEventListener("click", () => {
    elements.eventLog.innerHTML = "<li><time>—</time><span>Log cleared locally.</span></li>";
  });

  renderFutureExamples();
  updateSelectedExample();
  drawSignal();
  if ("ResizeObserver" in globalThis) new ResizeObserver(resizeCanvas).observe(elements.canvas);
  else globalThis.addEventListener("resize", resizeCanvas);

  Promise.all([
    fetchJson("/api/health").then((data) => {
      elements.health.textContent = `LOCAL SERVICE · ${Number(data.model.parameters).toLocaleString()} PARAMS`;
      elements.health.classList.add("online");
    }),
    fetchJson("/api/scenarios").then(validateScenarioContract),
  ]).catch((error) => {
    elements.health.textContent = "LOCAL SERVICE · OFFLINE OR CONTRACT ERROR";
    setPill(elements.captureState, "error", "BACKEND OFFLINE");
    elements.startButton.disabled = true;
    elements.errorMessage.textContent = String(error?.message || "Local service unavailable. No replay can start.");
    elements.errorBanner.hidden = false;
  });
})();

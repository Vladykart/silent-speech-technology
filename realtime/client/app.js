(() => {
  "use strict";

  const contract = globalThis.ReplayContract;
  if (!contract) throw new Error("replay contract unavailable");
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const elements = {
    health: $("#service-health"), openEvidence: $("#open-evidence"), footerEvidence: $("#footer-evidence"), closeEvidence: $("#close-evidence"), drawer: $("#evidence-drawer"),
    errorBanner: $("#error-banner"), errorMessage: $("#error-message"), catalogueState: $("#catalogue-state"), selectionDisclosure: $("#selection-disclosure"), sampleList: $("#sample-list"), selectedId: $("#selected-id"),
    featured: $("#run-featured"), start: $("#start"), stop: $("#stop"), sourceProgress: $("#source-progress"), modelProgress: $("#model-progress"), decisionProgress: $("#decision-progress"), announcer: $("#stage-announcer"),
    sourceState: $("#source-state"), sourceId: $("#source-id"), sourceShape: $("#source-shape"), sourceRateDuration: $("#source-rate-duration"), sourceCanvas: $("#source-canvas"), traceBins: $("#trace-bins"), channelSummary: $("#channel-summary"),
    modelState: $("#model-state"), comparisonCanvas: $("#comparison-canvas"), provenanceBody: $("#provenance-body"), featureCanvas: $("#feature-canvas"), featureShape: $("#feature-shape"), featureDescription: $("#feature-description"),
    modelFingerprint: $("#model-fingerprint"), melCanvas: $("#mel-canvas"), melShape: $("#mel-shape"), melDescription: $("#mel-description"), phonemeShape: $("#phoneme-shape"), phonemeFrames: $("#phoneme-frames"), phonemeSequence: $("#phoneme-sequence"), collapsedPath: $("#collapsed-path"), modelTime: $("#model-time"), decoderTime: $("#decoder-time"), timeline: $("#event-timeline"),
    decisionState: $("#decision-state"), candidates: $("#candidates"), diagnosticScore: $("#diagnostic-score"), scoreMeter: $("#score-meter"), recordReference: $("#record-reference"), referenceStatus: $("#reference-status"), decisionBox: $("#decision-box"), decisionLabel: $("#decision-label"), decisionTitle: $("#decision-title"), decisionReason: $("#decision-reason"), heldCandidate: $("#held-candidate"), heldStatus: $("#held-status"), safetyRow: $("#safety-row"), safetyAck: $("#safety-ack"), confirm: $("#confirm"), reject: $("#reject"), secondTake: $("#second-take"), finalCard: $("#final-card"), finalOutput: $("#final-output"), outputStatus: $("#output-status"),
    modelRegistry: $("#model-registry"), activeProvenance: $("#active-provenance"),
  };

  let state = contract.initialState();
  let manifest = null;
  let runId = null;
  let runEventsPath = null;
  let activeCardId = "QC-R01";
  let activeSampleId = "QC-R01";
  let currentCandidate = "";
  let safetySensitive = false;
  let streamController = null;
  let animationFrame = 0;
  const reducedMotion = globalThis.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true;

  function selectedSampleId() {
    return $('input[name="sample"]:checked', elements.sampleList)?.value || "QC-R01";
  }

  function setStatePill(element, kind, text) {
    element.className = `state ${kind}`;
    element.textContent = text;
  }

  function renderStage(stage, announce = true) {
    const index = contract.STAGES.findIndex((item) => item.id === stage);
    $$('[data-progress-stage]').forEach((item, itemIndex) => {
      item.classList.toggle("active", itemIndex === index);
      item.classList.toggle("complete", itemIndex < index);
    });
    $$('[data-stage-panel]').forEach((panel, itemIndex) => panel.classList.toggle("active", itemIndex === index));
    if (announce && index >= 0) elements.announcer.textContent = `Stage ${index + 1} of 3, ${contract.STAGES[index].label}.`;
  }

  function setTimelineComplete(event) {
    const row = $(`[data-event="${event.event}"]`, elements.timeline);
    if (row) {
      row.classList.add("complete");
      row.title = `Completed at +${Number(event.relative_ms).toFixed(1)} ms local sequence time`;
    }
  }

  function clearError() {
    elements.errorBanner.hidden = true;
    elements.errorMessage.textContent = "";
  }

  function safeError(message, focus = false) {
    const text = message || "The real replay failed. No result is available.";
    elements.errorMessage.textContent = text;
    elements.errorBanner.hidden = false;
    state = contract.reduce(state, {event: "error"});
    renderStage(state.stage);
    setStatePill(elements.sourceState, "error", "ERROR");
    setStatePill(elements.modelState, "error", "NO OUTPUT");
    setStatePill(elements.decisionState, "error", "NO RESULT");
    elements.decisionBox.className = "decision-box error";
    elements.decisionLabel.textContent = "ERROR";
    elements.decisionTitle.textContent = "Replay stopped safely";
    elements.decisionReason.textContent = "No candidate or final result is available. No fallback was substituted.";
    elements.finalOutput.textContent = "No final result";
    elements.outputStatus.textContent = "Error · nothing committed";
    elements.start.disabled = false;
    elements.featured.disabled = false;
    elements.stop.disabled = true;
    elements.sampleList.disabled = false;
    if (focus) elements.errorBanner.focus();
  }

  function updateSelection() {
    const selected = selectedSampleId();
    $$(".sample-card", elements.sampleList).forEach((card) => card.classList.toggle("selected", card.dataset.sampleId === selected));
    elements.selectedId.textContent = selected;
    const card = manifest?.samples.find((item) => item.id === selected);
    if (card) {
      elements.sourceId.textContent = selected;
      elements.sourceShape.textContent = `${Number(card.sample_count).toLocaleString()} × 8 · native float64`;
      elements.sourceRateDuration.textContent = `1 kHz · ${Number(card.duration_seconds).toFixed(3)} s`;
    }
  }

  function resetRunDisplay() {
    cancelAnimationFrame(animationFrame);
    clearError();
    state = contract.initialState();
    renderStage("recorded-source", false);
    currentCandidate = "";
    safetySensitive = false;
    $$("li", elements.timeline).forEach((item) => { item.classList.remove("complete"); item.removeAttribute("title"); });
    elements.sourceProgress.textContent = "Awaiting recorded replay";
    elements.modelProgress.textContent = "Not started";
    elements.decisionProgress.textContent = "No candidate";
    setStatePill(elements.sourceState, "", "READY");
    setStatePill(elements.modelState, "", "WAITING");
    setStatePill(elements.decisionState, "", "WAITING");
    elements.traceBins.textContent = "AWAITING RUN";
    elements.channelSummary.textContent = "Waiting for bounded transformed evidence";
    elements.provenanceBody.innerHTML = '<tr><td data-label="Operation">Waiting for a run</td><td data-label="Rate">—</td><td data-label="Shape / dtype">—</td><td data-label="Model input?">—</td></tr>';
    elements.featureShape.textContent = "—";
    elements.melShape.textContent = "—";
    elements.phonemeShape.textContent = "—";
    elements.phonemeFrames.innerHTML = "<span>Waiting for model output</span>";
    elements.phonemeSequence.innerHTML = "<li>Waiting for model output</li>";
    elements.collapsedPath.textContent = "—";
    elements.modelTime.textContent = "—";
    elements.decoderTime.textContent = "—";
    elements.candidates.innerHTML = "<p>Run an official recording to produce model output and then decoder candidates.</p>";
    elements.diagnosticScore.textContent = "—";
    elements.scoreMeter.value = 0;
    elements.scoreMeter.textContent = "0";
    elements.recordReference.textContent = "Sealed until model and decoder complete";
    elements.referenceStatus.textContent = "Audit only · never model or per-sample decoder input";
    elements.decisionBox.className = "decision-box idle";
    elements.decisionLabel.textContent = "WAITING";
    elements.decisionTitle.textContent = "No candidate staged";
    elements.decisionReason.textContent = "Nothing becomes a final result without confirmation. No action is connected.";
    elements.heldCandidate.textContent = "—";
    elements.heldStatus.textContent = "No candidate";
    elements.safetyRow.hidden = true;
    elements.safetyAck.checked = false;
    elements.confirm.disabled = true;
    elements.reject.disabled = true;
    elements.secondTake.hidden = true;
    elements.finalCard.classList.remove("accepted");
    elements.finalOutput.textContent = "—";
    elements.outputStatus.textContent = "No result committed";
    blankCanvas(elements.sourceCanvas, "#0e1511");
    blankCanvas(elements.comparisonCanvas, "#14201a");
    blankCanvas(elements.featureCanvas, "#15211b");
    blankCanvas(elements.melCanvas, "#15211b");
  }

  function canvasSize(canvas) {
    const rectangle = canvas.getBoundingClientRect();
    const ratio = Math.min(globalThis.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rectangle.width * ratio));
    const height = Math.max(1, Math.round(rectangle.height * ratio));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    return {context: canvas.getContext("2d"), width, height, ratio};
  }

  function blankCanvas(canvas, color) {
    const {context, width, height} = canvasSize(canvas);
    context.fillStyle = color;
    context.fillRect(0, 0, width, height);
  }

  function drawEnvelope(canvas, payload, progress = 1) {
    const {context, width, height, ratio} = canvasSize(canvas);
    context.fillStyle = "#0e1511";
    context.fillRect(0, 0, width, height);
    const channels = payload?.channels || [];
    const visibleCount = Math.max(1, Math.floor((payload?.display_bins || 1) * progress));
    const colors = ["#baf13f", "#55cfb5", "#67a8ef", "#f2aa55", "#c982e8", "#e57878", "#7bd77b", "#e6d36d"];
    context.font = `${10 * ratio}px ui-monospace, monospace`;
    for (let channel = 0; channel < 8; channel += 1) {
      const center = (channel + .5) * height / 8;
      context.strokeStyle = "#344139";
      context.lineWidth = ratio;
      context.beginPath(); context.moveTo(0, center); context.lineTo(width, center); context.stroke();
      context.fillStyle = "#9aa79f";
      context.fillText(`CH ${channel + 1}`, 8 * ratio, center - 7 * ratio);
      const bins = (channels[channel] || []).slice(0, visibleCount);
      context.strokeStyle = colors[channel];
      context.lineWidth = Math.max(ratio, width / 1200);
      bins.forEach((range, index) => {
        const x = bins.length === 1 ? 0 : index / Math.max(1, (payload.display_bins - 1)) * width;
        const y1 = center - Number(range[1]) / 127 * height * .045;
        const y2 = center - Number(range[0]) / 127 * height * .045;
        context.beginPath(); context.moveTo(x, y1); context.lineTo(x, y2); context.stroke();
      });
    }
  }

  function animateEnvelope(payload, durationSeconds) {
    const started = performance.now();
    const duration = reducedMotion ? 1 : Math.max(500, Number(durationSeconds) * 1000);
    const step = (now) => {
      const progress = Math.min(1, (now - started) / duration);
      drawEnvelope(elements.sourceCanvas, payload, progress);
      if (progress < 1) animationFrame = requestAnimationFrame(step);
    };
    animationFrame = requestAnimationFrame(step);
  }

  function drawComparison(payload) {
    const {context, width, height, ratio} = canvasSize(elements.comparisonCanvas);
    context.fillStyle = "#14201a"; context.fillRect(0, 0, width, height);
    context.font = `${9 * ratio}px ui-monospace, monospace`;
    for (let channel = 0; channel < 8; channel += 1) {
      const center = (channel + .5) * height / 8;
      context.strokeStyle = "#344139"; context.beginPath(); context.moveTo(0, center); context.lineTo(width, center); context.stroke();
      context.fillStyle = "#9ba79f"; context.fillText(`CH ${channel + 1}`, 7 * ratio, center - 7 * ratio);
      [[payload.source, "#8d9a91", .035], [payload.filtered, "#baf13f", .035]].forEach(([branch, color, amplitude]) => {
        const bins = branch[channel] || [];
        context.strokeStyle = color; context.lineWidth = Math.max(1, ratio);
        bins.forEach((range, index) => {
          const x = index / Math.max(1, bins.length - 1) * width;
          context.beginPath();
          context.moveTo(x, center - Number(range[1]) / 127 * height * amplitude);
          context.lineTo(x, center - Number(range[0]) / 127 * height * amplitude);
          context.stroke();
        });
      });
    }
    context.fillStyle = "#8d9a91"; context.fillRect(width - 175 * ratio, 10 * ratio, 12 * ratio, 3 * ratio);
    context.fillStyle = "#c9d0cb"; context.fillText("source-derived", width - 158 * ratio, 16 * ratio);
    context.fillStyle = "#baf13f"; context.fillRect(width - 175 * ratio, 27 * ratio, 12 * ratio, 3 * ratio);
    context.fillStyle = "#c9d0cb"; context.fillText("filtered", width - 158 * ratio, 33 * ratio);
  }

  function heatColor(value) {
    const normalized = Math.max(-127, Math.min(127, Number(value))) / 127;
    if (normalized >= 0) return `rgb(${Math.round(28 + 140 * normalized)},${Math.round(99 + 125 * normalized)},${Math.round(91 - 25 * normalized)})`;
    const magnitude = Math.abs(normalized);
    return `rgb(${Math.round(25 + 36 * magnitude)},${Math.round(45 + 48 * magnitude)},${Math.round(39 + 103 * magnitude)})`;
  }

  function drawHeatmap(canvas, payload) {
    const {context, width, height} = canvasSize(canvas);
    context.fillStyle = "#15211b"; context.fillRect(0, 0, width, height);
    const rows = payload.values || [];
    if (!rows.length) return;
    const cellWidth = width / rows.length;
    const cellHeight = height / payload.value_bins;
    rows.forEach((row, x) => row.forEach((value, y) => {
      context.fillStyle = heatColor(value);
      context.fillRect(Math.floor(x * cellWidth), Math.floor(y * cellHeight), Math.ceil(cellWidth + .5), Math.ceil(cellHeight + .5));
    }));
  }

  function heatmapInteraction(canvas, payload, description, names, kind) {
    canvas.tabIndex = 0;
    let x = 0; let y = 0;
    const announce = () => {
      const rows = payload.values || [];
      if (!rows.length) return;
      x = Math.max(0, Math.min(rows.length - 1, x));
      y = Math.max(0, Math.min(payload.value_bins - 1, y));
      const label = names?.[y] || `${kind} bin ${y + 1}`;
      const channel = names ? `, source channel ${Math.floor(y / 14) + 1}` : "";
      description.textContent = `${label}${channel}, display time bin ${x + 1} of ${rows.length}, rounded signed display value ${rows[x][y]}. Transformed evidence only.`;
    };
    canvas.onpointermove = (event) => {
      const rectangle = canvas.getBoundingClientRect();
      x = Math.floor((event.clientX - rectangle.left) / rectangle.width * payload.display_bins);
      y = Math.floor((event.clientY - rectangle.top) / rectangle.height * payload.value_bins);
      announce();
    };
    canvas.onkeydown = (event) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) return;
      event.preventDefault();
      if (event.key === "ArrowLeft") x -= 1;
      if (event.key === "ArrowRight") x += 1;
      if (event.key === "ArrowUp") y -= 1;
      if (event.key === "ArrowDown") y += 1;
      announce();
    };
    canvas.onfocus = announce;
  }

  function renderPhonemes(payload) {
    const fragment = document.createDocumentFragment();
    (payload.frames || []).forEach((frame) => {
      const item = document.createElement("span");
      item.setAttribute("aria-hidden", "true");
      item.textContent = frame.token;
      item.title = `frame ${frame.frame + 1}: ${frame.token}; rounded top-class diagnostic ${Number(frame.top_class_diagnostic).toFixed(3)}`;
      item.style.setProperty("--phoneme-height", `${Math.max(12, Number(frame.top_class_diagnostic) * 100).toFixed(1)}%`);
      fragment.append(item);
    });
    elements.phonemeFrames.replaceChildren(fragment);
    elements.phonemeFrames.setAttribute("aria-label", `${payload.frames.length} model frames; exact top classes and rounded diagnostics are available in the adjacent disclosure; collapsed path is provided as text.`);
    const sequence = document.createDocumentFragment();
    (payload.frames || []).forEach((frame) => {
      const row = document.createElement("li");
      row.textContent = `F${frame.frame + 1} · ${frame.token} · ${Number(frame.top_class_diagnostic).toFixed(3)}`;
      sequence.append(row);
    });
    elements.phonemeSequence.replaceChildren(sequence);
    elements.collapsedPath.textContent = payload.collapsed_path.length ? payload.collapsed_path.join(" · ") : "No non-silence class after collapse";
  }

  function renderProvenance(rows) {
    const fragment = document.createDocumentFragment();
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      const rate = `${row.input_rate_hz} → ${row.output_rate_hz} Hz`;
      const shape = `${row.input_shape.join("×")} ${row.input_dtype} → ${row.output_shape.join("×")} ${row.output_dtype}`;
      [["Operation", row.operation], ["Rate", rate], ["Shape / dtype", shape], ["Model input?", row.model_input ? "YES · released raw branch" : (row.note || "NO")]].forEach(([label, text]) => {
        const td = document.createElement("td"); td.dataset.label = label; td.textContent = text; tr.append(td);
      });
      fragment.append(tr);
    });
    elements.provenanceBody.replaceChildren(fragment);
  }

  function renderCandidates(event) {
    elements.candidates.innerHTML = "";
    (event.candidates || []).forEach((candidate, index) => {
      const row = document.createElement("div"); row.className = "candidate";
      const rank = document.createElement("i"); rank.textContent = String(index + 1);
      const text = document.createElement("b"); text.textContent = String(candidate.text || "—");
      const diagnostic = document.createElement("span"); diagnostic.textContent = `rank diagnostic ${Number(candidate.diagnostic_score).toFixed(3)} · edit distance ${Number(candidate.phoneme_distance)}`;
      row.append(rank, text, diagnostic); elements.candidates.append(row);
    });
    if (!(event.candidates || []).length) elements.candidates.innerHTML = "<p>No candidates were returned. No result is available.</p>";
    currentCandidate = String(event.candidates?.[0]?.text || "");
    elements.heldCandidate.textContent = currentCandidate || "—";
    elements.heldStatus.textContent = currentCandidate ? "Project decoder candidate · not a final result" : "No candidate";
    const score = Number(event.phoneme_alignment_score);
    elements.diagnosticScore.textContent = Number.isFinite(score) ? score.toFixed(3) : "—";
    elements.scoreMeter.value = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
    elements.scoreMeter.textContent = Number.isFinite(score) ? score.toFixed(3) : "0";
    elements.decoderTime.textContent = `${Number(event.project_decoder_ms).toFixed(1)} ms`;
  }

  function revealMetadata(event) {
    if (!state.metadataVisible || state.boundaryViolation) {
      safeError("Prompt-sealing boundary failed. No result is available.", true);
      streamController?.abort();
      return;
    }
    elements.recordReference.textContent = String(event.prompt || "Unavailable");
    elements.referenceStatus.textContent = `${event.matches_top_candidate ? "Matches" : "Does not match"} top candidate · audit observation, not an accuracy score`;
  }

  function markCardOutcome(outcome) {
    const card = $(`.sample-card[data-sample-id="${activeCardId}"]`);
    const line = card ? $("i", card) : null;
    if (line) { line.textContent = `Last run: ${outcome} · volatile browser state`; line.classList.add("outcome"); }
  }

  function renderDecision(event) {
    safetySensitive = Boolean(event.safety_sensitive);
    elements.stop.disabled = true;
    elements.start.disabled = false;
    elements.featured.disabled = false;
    elements.sampleList.disabled = false;
    elements.decisionBox.className = `decision-box ${event.state}`;
    elements.decisionReason.textContent = String(event.reason || "Human review is required.");
    elements.heldCandidate.textContent = currentCandidate || String(event.prediction || "—");
    elements.confirm.disabled = true;
    elements.reject.disabled = true;
    elements.secondTake.hidden = true;
    elements.safetyRow.hidden = true;
    elements.safetyAck.checked = false;
    if (event.state === "abstain") {
      setStatePill(elements.sourceState, "complete", "REPLAY COMPLETE");
      setStatePill(elements.modelState, "complete", "OUTPUT INSPECTABLE");
      setStatePill(elements.decisionState, "abstain", "ABSTAIN · NO RESULT");
      elements.decisionLabel.textContent = "ABSTAINED";
      elements.decisionTitle.textContent = "No final result available";
      elements.heldStatus.textContent = "Below diagnostic boundary · not committable";
      elements.outputStatus.textContent = "Abstained · nothing committed";
      elements.decisionProgress.textContent = "Abstained · no final result";
      elements.secondTake.hidden = !event.second_official_take_available;
      markCardOutcome("abstained");
    } else if (event.state === "confirm_required") {
      setStatePill(elements.sourceState, "complete", "REPLAY COMPLETE");
      setStatePill(elements.modelState, "complete", "MODEL COMPLETE");
      setStatePill(elements.decisionState, "hold", safetySensitive ? "SAFETY HOLD" : "CONFIRMATION REQUIRED");
      elements.decisionLabel.textContent = safetySensitive ? "SAFETY HOLD" : "HUMAN HOLD";
      elements.decisionTitle.textContent = safetySensitive ? "Acknowledge, then confirm or reject" : "Confirm or reject the held candidate";
      elements.confirm.disabled = safetySensitive;
      elements.reject.disabled = false;
      elements.safetyRow.hidden = !safetySensitive;
      elements.decisionProgress.textContent = safetySensitive ? "Acknowledgement + confirmation required" : "Human confirmation required";
      markCardOutcome("held for decision");
    }
  }

  async function handleEvent(event) {
    state = contract.reduce(state, event);
    if (state.boundaryViolation) {
      safeError("Ordered run evidence failed its sealing contract. No result is available.", true);
      streamController?.abort();
      return;
    }
    renderStage(state.stage);
    setTimelineComplete(event);
    switch (event.event) {
      case "asset_checks_passed":
        setStatePill(elements.sourceState, "running", "ASSETS VERIFIED");
        elements.sourceProgress.textContent = "Asset checks passed";
        break;
      case "source_opened":
        activeSampleId = String(event.sample_id);
        elements.sourceId.textContent = activeSampleId;
        elements.sourceShape.textContent = `${Number(event.sample_count).toLocaleString()} × ${event.channels} · native ${event.native_dtype}`;
        elements.sourceRateDuration.textContent = `1 kHz · ${Number(event.duration_seconds).toFixed(3)} s`;
        elements.sourceProgress.textContent = `${activeSampleId} official source opened`;
        break;
      case "replay_started":
        animateEnvelope(event.source_display, event.visualization_duration_seconds);
        elements.traceBins.textContent = `${event.source_display.display_bins} BINS · ${event.source_display.source_samples_per_bin}:1`;
        elements.channelSummary.textContent = `Channels 1–8 present; ${event.source_display.display_bins} chronological min/max bins each; signed 8-bit transformed display`;
        setStatePill(elements.sourceState, "running", "RECORDED DISPLAY");
        break;
      case "source_complete":
        elements.sourceProgress.textContent = "Recorded source replay complete";
        elements.modelProgress.textContent = "Preprocessing official source";
        break;
      case "preprocessing_complete":
        renderProvenance(event.provenance || []);
        drawComparison(event.comparison_display);
        setStatePill(elements.modelState, "running", "PREPROCESSING COMPLETE");
        elements.modelProgress.textContent = "Filtering complete";
        break;
      case "branches_aligned":
        drawHeatmap(elements.featureCanvas, event.feature_display);
        heatmapInteraction(elements.featureCanvas, event.feature_display, elements.featureDescription, event.feature_display.names, "feature");
        elements.featureShape.textContent = `${event.feature_shape.join(" × ")} · ≤${event.feature_display.display_bins} display bins`;
        elements.modelProgress.textContent = "Feature and model branches aligned";
        break;
      case "model_forward_complete":
        drawHeatmap(elements.melCanvas, event.mel_display);
        heatmapInteraction(elements.melCanvas, event.mel_display, elements.melDescription, null, "mel");
        renderPhonemes(event.phoneme_display);
        elements.melShape.textContent = event.output_shapes.mel.join(" × ");
        elements.phonemeShape.textContent = event.output_shapes.phoneme_logits.join(" × ");
        elements.modelTime.textContent = `${Number(event.model_forward_ms).toFixed(1)} ms`;
        setStatePill(elements.modelState, "complete", "MODEL FORWARD COMPLETE");
        elements.modelProgress.textContent = "Released model forward complete";
        break;
      case "decoder_complete":
        renderCandidates(event);
        elements.modelProgress.textContent = "Project decoder complete";
        break;
      case "metadata_revealed":
        revealMetadata(event);
        break;
      case "decision_required":
        renderDecision(event);
        break;
      case "error":
        safeError(String(event.detail || "Real replay pipeline failed. No result is available."));
        break;
      default:
        break;
    }
    elements.activeProvenance.innerHTML = `<div><dt>Active run</dt><dd>${activeSampleId} · event ${Math.min(state.expectedEventIndex, 10)} of 10 · ${state.terminalState}</dd></div>`;
  }

  async function fetchJson(path, options = {}) {
    const response = await fetch(path, options);
    let payload = {};
    try { payload = await response.json(); } catch (_) { payload = {}; }
    if (!response.ok) throw new Error(String(payload.detail || `same-origin request failed (${response.status})`));
    return payload;
  }

  async function consume(path) {
    const controller = new AbortController();
    streamController = controller;
    const response = await fetch(path, {signal: controller.signal, cache: "no-store"});
    if (!response.ok || !response.body) throw new Error(`run event stream failed (${response.status})`);
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

  function runError(error) {
    if (error?.name === "AbortError") return;
    safeError(String(error?.message || "The real replay could not continue. No result is available."), true);
  }

  async function runSelected(forcedId = null) {
    resetRunDisplay();
    activeCardId = forcedId || selectedSampleId();
    activeSampleId = activeCardId;
    const radio = $(`input[value="${activeCardId}"]`, elements.sampleList);
    if (radio) { radio.checked = true; updateSelection(); }
    elements.sampleList.disabled = true;
    elements.start.disabled = true;
    elements.featured.disabled = true;
    elements.stop.disabled = false;
    setStatePill(elements.sourceState, "running", "STARTING");
    const created = await fetchJson("/api/v1/runs", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({sample_id: activeCardId}),
    });
    if (created.sample_id !== activeCardId) throw new Error("safe sample binding mismatch; run cancelled");
    runId = created.id;
    runEventsPath = created.events;
    await consume(runEventsPath);
  }

  async function stopRun() {
    if (!runId) return;
    try {
      await fetchJson(`/api/v1/runs/${runId}/stop`, {method: "POST"});
      streamController?.abort();
      state = contract.reduce(state, {event: "local_stopped"});
      renderStage(state.stage);
      setStatePill(elements.sourceState, "stopped", "STOPPED");
      setStatePill(elements.modelState, "stopped", "STOPPED");
      setStatePill(elements.decisionState, "stopped", "NO RESULT");
      elements.decisionBox.className = "decision-box stopped";
      elements.decisionLabel.textContent = "STOPPED";
      elements.decisionTitle.textContent = "Operator stopped the replay";
      elements.decisionReason.textContent = "No candidate or final result was committed.";
      elements.finalOutput.textContent = "No final result";
      elements.outputStatus.textContent = "Stopped · nothing committed";
      elements.stop.disabled = true; elements.start.disabled = false; elements.featured.disabled = false; elements.sampleList.disabled = false;
      markCardOutcome("stopped");
    } catch (error) { runError(error); }
  }

  async function confirmRun() {
    try {
      const payload = await fetchJson(`/api/v1/runs/${runId}/decision`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({action: "confirm", safety_acknowledged: elements.safetyAck.checked}),
      });
      state = contract.reduce(state, {event: "local_confirmed"}); renderStage(state.stage);
      setStatePill(elements.decisionState, "confirmed", "CONFIRMED · NO ACTUATION");
      elements.decisionBox.className = "decision-box confirmed";
      elements.decisionLabel.textContent = "HUMAN CONFIRMED";
      elements.decisionTitle.textContent = "Final local result";
      elements.decisionReason.textContent = "The human gate completed. Nothing was sent to an action or actuator.";
      elements.finalOutput.textContent = String(payload.output || currentCandidate || "—");
      elements.outputStatus.textContent = "Confirmed in volatile service/browser memory · no actuation";
      elements.finalCard.classList.add("accepted");
      elements.confirm.disabled = true; elements.reject.disabled = true; elements.safetyRow.hidden = true;
      markCardOutcome("confirmed"); elements.finalCard.focus();
    } catch (error) { runError(error); }
  }

  async function rejectRun() {
    try {
      const payload = await fetchJson(`/api/v1/runs/${runId}/decision`, {
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({action: "reject"}),
      });
      state = contract.reduce(state, {event: "local_rejected"}); renderStage(state.stage);
      setStatePill(elements.decisionState, "rejected", "REJECTED · NO RESULT");
      elements.decisionBox.className = "decision-box rejected";
      elements.decisionLabel.textContent = "REJECTED";
      elements.decisionTitle.textContent = "No final result";
      elements.decisionReason.textContent = "The human reviewer rejected the held candidate. Nothing was committed or actuated.";
      elements.finalOutput.textContent = "No final result"; elements.outputStatus.textContent = "Rejected · nothing committed";
      elements.confirm.disabled = true; elements.reject.disabled = true; elements.safetyRow.hidden = true;
      elements.secondTake.hidden = !payload.second_official_take_available;
      markCardOutcome("rejected"); elements.finalCard.focus();
    } catch (error) { runError(error); }
  }

  async function runSecondTake() {
    try {
      const payload = await fetchJson(`/api/v1/runs/${runId}/second-take`, {method: "POST"});
      resetRunDisplay();
      activeSampleId = "QC-R02-T2";
      elements.sourceId.textContent = activeSampleId;
      elements.sourceProgress.textContent = "Second official take selected";
      elements.sampleList.disabled = true; elements.start.disabled = true; elements.featured.disabled = true; elements.stop.disabled = false;
      setStatePill(elements.sourceState, "running", "SECOND OFFICIAL TAKE");
      runEventsPath = payload.events;
      await consume(runEventsPath);
    } catch (error) { runError(error); }
  }

  function renderRegistry(items) {
    const fragment = document.createDocumentFragment();
    items.forEach((item) => {
      const article = document.createElement("article");
      const name = document.createElement("b"); name.textContent = item.name;
      const status = document.createElement("span"); status.textContent = "NOT EXECUTED HERE";
      const reason = document.createElement("p"); reason.textContent = item.reason;
      article.append(name, status, reason); fragment.append(article);
    });
    elements.modelRegistry.replaceChildren(fragment);
  }

  function validateManifest(payload) {
    if (!contract.validManifest(payload.samples)) throw new Error("frozen public catalogue contract mismatch");
    if (payload.executed_model?.parameters !== 54187136 || payload.executed_model?.label !== "Executed model 1 of 1") throw new Error("one-model execution contract mismatch");
    const serialized = JSON.stringify(payload.samples);
    if (/prompt"\s*:\s*"(?!sealed)/i.test(serialized)) throw new Error("sample prompt appeared before inference");
    manifest = payload;
    elements.selectionDisclosure.textContent = payload.selection_disclosure;
    elements.catalogueState.textContent = "10 VERIFIED CARDS · PROMPTS SEALED";
    elements.modelFingerprint.textContent = `${payload.executed_model.fingerprint_prefix}… · short identifier, not integrity proof`;
    renderRegistry(payload.evidence_only_registry || []);
    updateSelection();
  }

  function openDrawer() {
    elements.drawer.hidden = false;
    elements.openEvidence.setAttribute("aria-expanded", "true");
    elements.closeEvidence.focus();
  }
  function closeDrawer() {
    elements.drawer.hidden = true;
    elements.openEvidence.setAttribute("aria-expanded", "false");
    elements.openEvidence.focus();
  }
  function selectTab(button) {
    $$("[role=tab]", elements.drawer).forEach((tab) => tab.setAttribute("aria-selected", String(tab === button)));
    $$("[role=tabpanel]", elements.drawer).forEach((panel) => { panel.hidden = panel.id !== button.getAttribute("aria-controls"); });
  }

  elements.sampleList.addEventListener("change", updateSelection);
  elements.start.addEventListener("click", () => runSelected().catch(runError));
  elements.featured.addEventListener("click", () => runSelected("QC-R01").catch(runError));
  elements.stop.addEventListener("click", stopRun);
  elements.confirm.addEventListener("click", confirmRun);
  elements.confirm.addEventListener("keydown", (event) => { if (event.key === " ") event.preventDefault(); });
  elements.reject.addEventListener("click", rejectRun);
  elements.secondTake.addEventListener("click", runSecondTake);
  elements.safetyAck.addEventListener("change", () => { if (safetySensitive) elements.confirm.disabled = !elements.safetyAck.checked; });
  elements.openEvidence.addEventListener("click", openDrawer);
  elements.footerEvidence.addEventListener("click", openDrawer);
  elements.closeEvidence.addEventListener("click", closeDrawer);
  elements.drawer.addEventListener("click", (event) => { const tab = event.target.closest("[role=tab]"); if (tab) selectTab(tab); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !elements.drawer.hidden) closeDrawer(); });
  globalThis.addEventListener("resize", () => {
    if (state.expectedEventIndex === 0) {
      blankCanvas(elements.sourceCanvas, "#0e1511"); blankCanvas(elements.comparisonCanvas, "#14201a"); blankCanvas(elements.featureCanvas, "#15211b"); blankCanvas(elements.melCanvas, "#15211b");
    }
  });

  resetRunDisplay();
  updateSelection();
  Promise.all([
    fetchJson("/api/v1/health").then((payload) => {
      if (payload.status !== "ready" || payload.executed_models !== 1) throw new Error("service did not prove one ready executed model");
      elements.health.textContent = `SERVICE READY · ${String(payload.revision).toUpperCase()}`;
      elements.health.className = "ready";
    }),
    fetchJson("/api/v1/manifest").then(validateManifest),
  ]).catch((error) => {
    elements.health.textContent = "SERVICE BLOCKED";
    elements.health.className = "error";
    elements.start.disabled = true; elements.featured.disabled = true;
    safeError(String(error?.message || "Service or evidence contract unavailable. No replay can start."));
  });
})();

#!/usr/bin/env node
/* Loopback-only rendered/network QA using the project-pinned Playwright-cache Chromium binary. */
"use strict";

import {spawn} from "node:child_process";
import {mkdir, rm, writeFile} from "node:fs/promises";
import path from "node:path";

const origin = process.env.REPLAY_QA_ORIGIN || "http://127.0.0.1:8879";
if (!/^http:\/\/127\.0\.0\.1:\d+$/.test(origin)) throw new Error("QA origin must be exact IPv4 loopback HTTP");
const chromium = process.env.CHROMIUM_PATH || "/root/.cache/ms-playwright/chromium-1181/chrome-linux/chrome";
const outputRoot = path.resolve("realtime/local_assets/rendered-qa");
const profile = path.join(outputRoot, "isolated-profile");
const debugPort = Number(process.env.REPLAY_QA_DEBUG_PORT || 9339);
const viewports = [[320,568],[375,812],[768,1024],[1024,768],[1366,768],[1920,1080],[3840,2160]];
const interactionWidths = new Set([768, 1366, 1920]);
await rm(outputRoot, {recursive: true, force: true});
await mkdir(profile, {recursive: true});

const chrome = spawn(chromium, [
  "--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
  `--remote-debugging-port=${debugPort}`, "--remote-debugging-address=127.0.0.1",
  `--user-data-dir=${profile}`, "--no-first-run", "--disable-background-networking",
  "--disable-component-update", "--disable-default-apps", "--disable-sync", "--metrics-recording-only",
  "--disable-breakpad", "--disable-extensions", "--disable-domain-reliability",
  "--disable-client-side-phishing-detection", "--safebrowsing-disable-auto-update",
  "--disable-features=OptimizationHints,MediaRouter,DialMediaRouteProvider,Translate",
  "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1", "about:blank",
], {stdio: ["ignore", "ignore", "pipe"]});
let stderr = "";
chrome.stderr.on("data", (chunk) => { stderr += String(chunk); });

async function waitDebug() {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${debugPort}/json/list`);
      const pages = await response.json();
      if (pages[0]?.webSocketDebuggerUrl) return pages[0].webSocketDebuggerUrl;
    } catch (_) { /* local bridge not ready */ }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`pinned Chromium did not expose loopback debugging: ${stderr.slice(-500)}`);
}

class CDP {
  constructor(socket) {
    this.socket = socket; this.next = 1; this.pending = new Map(); this.events = [];
    socket.addEventListener("message", (message) => {
      const value = JSON.parse(String(message.data));
      if (value.id) {
        const pending = this.pending.get(value.id);
        if (!pending) return;
        this.pending.delete(value.id);
        if (value.error) pending.reject(new Error(`${pending.method}: ${value.error.message}`));
        else pending.resolve(value.result || {});
      } else this.events.push(value);
    });
  }
  send(method, params = {}) {
    const id = this.next++;
    this.socket.send(JSON.stringify({id, method, params}));
    return new Promise((resolve, reject) => this.pending.set(id, {resolve, reject, method}));
  }
}

const wsUrl = await waitDebug();
const socket = new WebSocket(wsUrl);
await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, {once: true}); socket.addEventListener("error", reject, {once: true}); });
const cdp = new CDP(socket);
await cdp.send("Page.enable");
await cdp.send("Runtime.enable");
await cdp.send("Network.enable", {maxTotalBufferSize: 1000000, maxResourceBufferSize: 200000});
await cdp.send("Log.enable");

async function evaluate(expression) {
  const result = await cdp.send("Runtime.evaluate", {expression, awaitPromise: true, returnByValue: true, userGesture: true});
  if (result.exceptionDetails) throw new Error(`browser evaluation failed: ${result.exceptionDetails.text}`);
  return result.result?.value;
}
async function waitFor(expression, timeout = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    if (await evaluate(expression)) return;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`browser condition timed out: ${expression}`);
}
async function navigate() {
  await cdp.send("Page.navigate", {url: `${origin}/`});
  await waitFor("document.readyState === 'complete' && document.querySelector('#service-health')?.classList.contains('ready')");
}
async function viewport(width, height) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {width, height, deviceScaleFactor: 1, mobile: false});
}
async function geometry(label) {
  const value = await evaluate(`(() => {
    const visible = (element) => { const style=getComputedStyle(element); const box=element.getBoundingClientRect(); return style.display!=='none' && style.visibility!=='hidden' && box.width>0 && box.height>0; };
    const overflow=[]; const clipped=[]; const controls=[];
    for (const element of document.querySelectorAll('body *')) {
      if (!visible(element)) continue;
      const box=element.getBoundingClientRect();
      const layoutWidth=document.documentElement.clientWidth;
      if (box.left < -1 || box.right > layoutWidth + 1) overflow.push({tag:element.tagName,id:element.id,cls:element.className,left:Math.round(box.left),right:Math.round(box.right)});
      const style=getComputedStyle(element);
      if (!element.classList.contains('sr-only') && element.children.length===0 && element.textContent.trim() && element.scrollWidth > element.clientWidth + 2 && !['auto','scroll'].includes(style.overflowX)) clipped.push({tag:element.tagName,id:element.id,cls:element.className});
    }
    for (const element of document.querySelectorAll('button,input,a[href],summary,[tabindex="0"]')) {
      if (!visible(element) || element.disabled) continue;
      const box=element.getBoundingClientRect();
      controls.push({name:(element.getAttribute('aria-label')||element.textContent||element.value||'').trim().slice(0,80),width:Math.round(box.width),height:Math.round(box.height)});
    }
    const bar=document.querySelector('.truth-bar').getBoundingClientRect();
    return {innerWidth,innerHeight,layoutWidth:document.documentElement.clientWidth,documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,overflow,clipped,controls,truthTop:Math.round(bar.top),truthWidth:Math.round(bar.width),h1:document.querySelectorAll('h1').length,externalAnchors:[...document.querySelectorAll('a')].map(a=>a.href).filter(h=>!h.startsWith(location.origin)&&!h.startsWith('data:'))};
  })()`);
  if (value.documentWidth !== value.layoutWidth || value.bodyWidth !== value.layoutWidth || value.overflow.length || value.clipped.length || value.h1 !== 1 || value.externalAnchors.length) {
    throw new Error(`${label} geometry failed: ${JSON.stringify(value)}`);
  }
  if (value.controls.some((item) => !item.name || item.width < 18 || item.height < 18)) throw new Error(`${label} inaccessible control: ${JSON.stringify(value.controls)}`);
  await evaluate("scrollTo(0, document.documentElement.scrollHeight)");
  const sticky = await evaluate("(() => { const a=document.querySelector('.truth-bar').getBoundingClientRect(); const b=document.querySelector('.limitation-line').getBoundingClientRect(); return {top:Math.round(a.top),visible:b.top<innerHeight&&b.bottom>0,right:Math.round(a.right)}; })()");
  if (sticky.top !== 0 || !sticky.visible || sticky.right !== value.layoutWidth) throw new Error(`${label} permanent truth failed: ${JSON.stringify(sticky)}`);
  await evaluate("scrollTo(0,0)");
  return value;
}
async function screenshot(name, full = false) {
  const result = await cdp.send("Page.captureScreenshot", {format: "png", captureBeyondViewport: full, fromSurface: true});
  await writeFile(path.join(outputRoot, `${name}.png`), Buffer.from(result.data, "base64"));
}
async function click(selector) {
  const result = await evaluate(`(() => { const element=document.querySelector(${JSON.stringify(selector)}); if(!element || element.disabled || element.hidden) return false; element.click(); return true; })()`);
  if (!result) throw new Error(`control unavailable: ${selector}`);
}
async function selectSample(id) {
  const success = await evaluate(`(() => { const input=document.querySelector('input[value="${id}"]'); if(!input) return false; input.checked=true; input.dispatchEvent(new Event('change',{bubbles:true})); return true; })()`);
  if (!success) throw new Error(`sample selection unavailable: ${id}`);
}
async function waitDecision(text) {
  await waitFor(`document.querySelector('#decision-state')?.textContent.includes(${JSON.stringify(text)})`, 20000);
}
async function paths(width) {
  const challengeDefault = await evaluate("document.querySelector('#mode-challenge').checked && document.querySelector('#guided-phrase-text').textContent.includes('sealed')");
  if (!challengeDefault) throw new Error("challenge mode did not remain the sealed default");
  await click("#run-featured"); await waitDecision("CONFIRMATION REQUIRED");
  await evaluate("(() => { const slider=document.querySelector('#noise-slider'); slider.value='35'; slider.dispatchEvent(new Event('input',{bubbles:true})); })()");
  const noiseBoundary = await evaluate("document.querySelector('#noise-state').textContent === 'NOISE PREVIEW MODE' && document.querySelector('#noise-status').textContent.includes('Not used for official evidence')");
  if (!noiseBoundary) throw new Error("synthetic noise sandbox boundary was not explicit");
  await click("#noise-reset");
  if (!(await evaluate("document.querySelector('#noise-level').textContent === '0%'"))) throw new Error("noise sandbox did not restore its baseline");
  await click("#reject"); await waitDecision("REJECTED");
  await selectSample("QC-R02"); await click("#start"); await waitDecision("ABSTAIN"); await click("#second-take"); await waitDecision("CONFIRMATION REQUIRED"); await click("#confirm"); await waitDecision("CONFIRMED");
  await selectSample("QC-R03"); await click("#start"); await waitDecision("SAFETY HOLD");
  const safetyBefore = await evaluate("document.querySelector('#confirm').disabled && !document.querySelector('#safety-row').hidden");
  if (!safetyBefore) throw new Error("safety acknowledgement did not remain additional to confirmation");
  await evaluate("(() => { const input=document.querySelector('#safety-ack'); input.checked=true; input.dispatchEvent(new Event('change',{bubbles:true})); })()");
  if (await evaluate("document.querySelector('#confirm').disabled")) throw new Error("acknowledged safety confirmation stayed inaccessible");
  await click("#confirm"); await waitDecision("CONFIRMED");
  await click("#open-evidence");
  if (await evaluate("document.querySelector('#evidence-drawer').hidden")) throw new Error("evidence drawer did not open");
  await click("#tab-registry");
  const readiness = await evaluate("(() => { const panel=document.querySelector('#drawer-registry'); return !panel.hidden && panel.querySelectorAll('.registry article').length===5 && panel.textContent.includes('READINESS · weights') && panel.textContent.includes('Why not comparable'); })()");
  if (!readiness) throw new Error("model-readiness matrix did not expose five bounded evidence-only roles");
  await click("#tab-plan");
  const plan = await evaluate("(() => { const panel=document.querySelector('#drawer-plan'); return !panel.hidden && panel.textContent.includes('PROTOCOL ONLY · NO RESULTS') && panel.textContent.includes('Unknown; no cohort is labelled held out') && panel.textContent.includes('Every frozen selection remains in the denominator'); })()");
  if (!plan) throw new Error("protocol-only next-proof plan crossed or omitted its boundary");
  await evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))");
  if (!(await evaluate("document.querySelector('#evidence-drawer').hidden"))) throw new Error("Escape did not close evidence drawer");
  await evaluate("(() => { document.documentElement.style.scrollBehavior='auto'; const top=document.querySelector('#stage-model').offsetTop-document.querySelector('.truth-bar').offsetHeight; scrollTo(0,Math.max(0,top)); })()");
  await new Promise((resolve) => setTimeout(resolve, 100));
  await screenshot(`${width}-executed-output`);
  await evaluate("(() => { const top=document.querySelector('#feature-canvas').closest('.evidence-card').offsetTop-document.querySelector('.truth-bar').offsetHeight; scrollTo(0,Math.max(0,top)); })()");
  await new Promise((resolve) => setTimeout(resolve, 100));
  await screenshot(`${width}-tensor-output`);
  return geometry(`${width}-dynamic`);
}

const results = [];
try {
  for (const [width, height] of viewports) {
    await viewport(width, height); await navigate();
    const initial = await geometry(`${width}x${height}-initial`);
    await screenshot(`${width}x${height}-top`);
    let dynamic = null;
    if (interactionWidths.has(width)) dynamic = await paths(width);
    results.push({width, height, initial: {documentWidth: initial.documentWidth, overflow: 0, clipped: 0, controls: initial.controls.length}, dynamic: dynamic ? {documentWidth: dynamic.documentWidth, overflow: 0, clipped: 0, controls: dynamic.controls.length} : null});
  }
  const requests = cdp.events.filter((item) => item.method === "Network.requestWillBeSent").map((item) => item.params.request.url);
  const external = requests.filter((url) => !url.startsWith(`${origin}/`) && !url.startsWith("data:") && url !== "about:blank");
  if (external.length) throw new Error(`external browser request detected: ${JSON.stringify(external)}`);
  const consoleErrors = cdp.events.filter((item) => item.method === "Runtime.consoleAPICalled" && ["error","warning"].includes(item.params.type));
  const allLogErrors = cdp.events.filter((item) => item.method === "Log.entryAdded" && ["error","warning"].includes(item.params.entry.level));
  const knownPolicyWarnings = allLogErrors.filter((item) => item.params.entry.level === "warning" && item.params.entry.text === "Error with Permissions-Policy header: Unrecognized feature: 'bluetooth'.");
  const logErrors = allLogErrors.filter((item) => !knownPolicyWarnings.includes(item));
  if (consoleErrors.length || logErrors.length) throw new Error(`browser console/log error detected: ${JSON.stringify(consoleErrors.map(item=>item.params).concat(logErrors.map(item=>item.params)))}`);
  const storage = await evaluate(`(async () => ({local:localStorage.length,session:sessionStorage.length,indexed:(await indexedDB.databases()).length,caches:(await caches.keys()).length,workers:(await navigator.serviceWorker.getRegistrations()).length}))()`);
  const cookies = await cdp.send("Network.getAllCookies");
  if (Object.values(storage).some(Boolean) || cookies.cookies.length) throw new Error(`browser persistence detected: ${JSON.stringify(storage)}/${cookies.cookies.length}`);
  const ax = await cdp.send("Accessibility.getFullAXTree");
  const unnamedButtons = ax.nodes.filter((node) => node.role?.value === "button" && !node.ignored && !node.name?.value);
  if (unnamedButtons.length) throw new Error(`accessible tree has ${unnamedButtons.length} unnamed buttons`);
  const report = {schema_version: 1, chromium: "Playwright-cache Chromium 139.0.7258.5", origin: "loopback-only", viewports: results, interaction_matrix: ["featured QC-R01", "QC-R02 abstain + QC-R02-T2", "QC-R03 acknowledgement + confirmation", "noise sandbox enters preview mode and resets without changing official evidence", "five-row model readiness plus protocol-only no-result plan"], interaction_widths: [...interactionWidths], network: {request_count: requests.length, external_requests: 0}, console_errors: 0, known_permissions_policy_warnings: {count: knownPolicyWarnings.length, reason: "Pinned Chromium does not recognize the mandated deny-only bluetooth directive; header remains fail-closed."}, persistence: storage, cookies: 0, unnamed_accessible_buttons: 0};
  await writeFile(path.join(outputRoot, "result.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  socket.close(); chrome.kill("SIGTERM");
}

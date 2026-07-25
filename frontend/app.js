const API = "";
let productId = null;
let cameraStream = null;

function showOnly(id) {
  ["scan-section","loading-section","not-found-section","intel-section"]
    .forEach(s => document.getElementById(s).style.display = s === id ? "block" : "none");
}

// ── Camera ────────────────────────────────────────────────────────────────────
async function openCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    const v = document.getElementById("camera-preview");
    v.srcObject    = cameraStream;
    v.style.display = "block";
    document.getElementById("capture-btn").style.display = "block";
  } catch (e) { alert("Camera access denied. Use Upload instead."); }
}

function capturePhoto() {
  const v = document.getElementById("camera-preview");
  const c = document.getElementById("snap-canvas");
  c.width = v.videoWidth; c.height = v.videoHeight;
  c.getContext("2d").drawImage(v, 0, 0);
  stopCamera();
  c.toBlob(blob => submitImage(blob), "image/jpeg", 0.9);
}

function stopCamera() {
  if (cameraStream) { cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; }
  document.getElementById("camera-preview").style.display  = "none";
  document.getElementById("capture-btn").style.display     = "none";
}

function handleUpload(e) { if (e.target.files[0]) submitImage(e.target.files[0]); }

// ── Scan ──────────────────────────────────────────────────────────────────────
async function submitImage(blob) {
  showOnly("loading-section");
  document.getElementById("loading-text").textContent = "Identifying product...";
  const form = new FormData();
  form.append("file", blob, "product.jpg");
  try {
    const r = await fetch("/api/scan", { method: "POST", body: form });
    const d = await r.json();
    handleResult(d);
  } catch (e) { showNotFound("Connection error."); }
}

async function searchByName() {
  const q = document.getElementById("search-input").value.trim();
  if (!q) return;
  showOnly("loading-section");
  document.getElementById("loading-text").textContent = "Searching catalog...";
  try {
    const r = await fetch("/api/search?q=" + encodeURIComponent(q));
    const d = await r.json();
    handleResult(d);
  } catch (e) { showNotFound("Connection error."); }
}

function handleResult(d) {
  if (!d.found) { showNotFound(d.message || "Product not in catalog."); return; }
  productId = d.product_id;
  loadIntelligence();
}

// ── Intelligence ──────────────────────────────────────────────────────────────
async function loadIntelligence() {
  document.getElementById("loading-text").textContent = "Building product intelligence...";
  showOnly("loading-section");
  try {
    const r = await fetch("/api/product/" + productId);
    const d = await r.json();
    render(d);
    showOnly("intel-section");
  } catch (e) { showNotFound("Failed to load product intelligence."); }
}

function render(d) {
  // Header
  set("r-brand",          d.brand         || "");
  set("r-category",       d.category      || "");
  set("r-name",           d.product_name  || "");
  set("r-variant",        d.variant ? "Variant: " + d.variant : "");
  set("r-outcome-reason", d.outcome_reason || "");
  set("r-finish",         d.finish_texture || "");
  set("r-sentiment",      (d.review_intelligence || {}).overall_sentiment || "");
  set("r-who-likes",      (d.review_intelligence || {}).who_likes         || "");
  set("r-who-dislikes",   (d.review_intelligence || {}).who_dislikes      || "");
  set("r-why-differs",    (d.review_intelligence || {}).why_opinions_differ || "");
  set("r-irritation",     d.potential_irritation_risk || "");

  // Outcome badge
  const map = { good_match: ["Good Match ✓","good"], mixed_match: ["Mixed Match ~","mixed"], not_recommended: ["Not Recommended ✗","bad"] };
  const [lbl, cls] = map[d.outcome_state] || ["Unknown","mixed"];
  const badge = document.getElementById("r-outcome-badge");
  badge.textContent = lbl; badge.className = "outcome-badge " + cls;

  // Skin tags
  const tagsEl = document.getElementById("r-skin-tags");
  tagsEl.innerHTML = "";
  Object.entries(d.skin_suitability || {}).forEach(([k, v]) => {
    const s = document.createElement("span");
    s.className   = "tag " + (v ? "yes" : "no");
    s.textContent = k.charAt(0).toUpperCase() + k.slice(1);
    tagsEl.appendChild(s);
  });

  // Intent tags
  const intentEl = document.getElementById("r-intent");
  intentEl.innerHTML = "";
  (d.ingredient_intent || []).forEach(i => {
    const s = document.createElement("span");
    s.className = "intent-tag"; s.textContent = i;
    intentEl.appendChild(s);
  });

  // Ingredients
  const ingEl = document.getElementById("r-ingredients");
  ingEl.innerHTML = "";
  (d.ingredient_notes || []).forEach(i => {
    const li = document.createElement("li");
    li.innerHTML = "<strong>" + (i.name || "") + "</strong> — " + (i.plain_explanation || "");
    ingEl.appendChild(li);
  });

  list("r-pros",        d.pros          || []);
  list("r-cons",        d.cons          || []);
  list("r-dealbreakers",d.deal_breakers || []);
  document.getElementById("r-dealbreakers-card").style.display =
    (d.deal_breakers && d.deal_breakers.length) ? "block" : "none";

  const ri = d.review_intelligence || {};
  list("r-praise",    ri.praise_themes    || []);
  list("r-complaints",ri.complaint_themes || []);

  // Reset fit
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  document.getElementById("fit-grid").innerHTML    = "";
  document.getElementById("fit-results-area").style.display = "none";
  document.getElementById("fit-detail").style.display       = "none";
  document.getElementById("alt-section").style.display      = "none";
}

// ── Skin type ─────────────────────────────────────────────────────────────────
async function selectSkin(btn, type) {
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  btn.classList.add("active");

  const grid = document.getElementById("fit-grid");
  if (!grid.childElementCount) {
    try {
      const r = await fetch("/api/fit/all/" + productId);
      const d = await r.json();
      grid.innerHTML = "";
      (d.scores || []).forEach(s => {
        const pct = s.fit_percentage || 0;
        const cls = pct >= 75 ? "good" : pct >= 45 ? "mixed" : "bad";
        const c   = document.createElement("div");
        c.className    = "fit-card";
        c.dataset.skin = s.skin_type;
        c.innerHTML    =
          "<div class='fit-skin-label'>" + s.skin_type + "</div>" +
          "<div class='fit-pct "  + cls + "'>" + pct + "%</div>" +
          "<div class='fit-label-text'>" + (s.label || "") + "</div>";
        grid.appendChild(c);
      });
      document.getElementById("fit-results-area").style.display = "block";
    } catch (e) { console.error(e); }
  }

  document.querySelectorAll(".fit-card").forEach(c =>
    c.classList.toggle("active-skin", c.dataset.skin === type));

  // Fit detail
  try {
    const r = await fetch("/api/fit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, skin_type: type })
    });
    const d = await r.json();
    set("fit-explanation", d.explanation || "");
    document.getElementById("fit-detail").style.display = "block";
  } catch (e) { console.error(e); }

  // Alternatives
  try {
    const r    = await fetch("/api/alternatives/" + productId + "?skin_type=" + type);
    const d    = await r.json();
    const alts = d.alternatives || [];
    const al   = document.getElementById("alt-list");
    al.innerHTML = "";
    alts.forEach(a => {
      const tc  = (a.price_tier || "mid-range").replace(" ", "-");
      const el  = document.createElement("div");
      el.className = "alt-card";
      el.innerHTML =
        "<div>" +
          "<div class='alt-brand'>"  + (a.brand        || "") + "</div>" +
          "<div class='alt-name'>"   + (a.product_name || "") + "</div>" +
          "<div class='alt-reason'>" + (a.reason        || "") + "</div>" +
        "</div>" +
        "<span class='price-tier-badge " + tc + "'>" + (a.price_tier || "mid-range") + "</span>";
      al.appendChild(el);
    });
    document.getElementById("alt-section").style.display = alts.length ? "block" : "none";
  } catch (e) { console.error(e); }
}

// ── Not Found ─────────────────────────────────────────────────────────────────
function showNotFound(msg) {
  set("not-found-msg", msg);
  showOnly("not-found-section");
}
function retryCamera() { showOnly("scan-section"); openCamera(); }
function retryUpload() { showOnly("scan-section"); document.getElementById("file-upload").click(); }
function retrySearch() { showOnly("scan-section"); document.getElementById("search-input").focus(); }

// ── Reset ─────────────────────────────────────────────────────────────────────
function resetApp() {
  productId = null; stopCamera();
  document.getElementById("search-input").value = "";
  document.getElementById("file-upload").value  = "";
  showOnly("scan-section");
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function set(id, val) { const e = document.getElementById(id); if (e) e.textContent = val; }

function list(id, items) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = "";
  items.forEach(t => { const li = document.createElement("li"); li.textContent = t; el.appendChild(li); });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("search-input").addEventListener("keydown", e => {
    if (e.key === "Enter") searchByName();
  });
});

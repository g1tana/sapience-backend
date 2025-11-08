import express from "express";
import fs from "fs";
import path from "path";
import bodyParser from "body-parser";
import fetch from "node-fetch"; // add to package.json deps if missing

// ... existing imports and app setup

const PY_HEALTH_URL = process.env.PY_HEALTH_URL || "http://127.0.0.1:5000/health";
const PY_ALIGN_URL = process.env.PY_ALIGN_URL || "http://127.0.0.1:5000/run_alignment";

// Proxy health
app.get("/api/services/health", async (req, res) => {
  try {
    const r = await fetch(PY_HEALTH_URL);
    if (!r.ok) {
      return res.status(502).json({ ok: false, error: "python_health_bad", status: r.status });
    }
    const json = await r.json();
    return res.json({ ok: true, python: json });
  } catch (err) {
    return res.status(502).json({ ok: false, error: "python_unreachable", detail: String(err) });
  }
});

// Proxy run_alignment (optional)
app.post("/api/services/run_alignment", async (req, res) => {
  try {
    const r = await fetch(PY_ALIGN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body || {})
    });
    const json = await r.json();
    res.json({ ok: true, result: json });
  } catch (err) {
    res.status(502).json({ ok: false, error: "python_unreachable", detail: String(err) });
  }
});

const app = express();
app.use(bodyParser.json());

const DB_PATH = path.join(process.cwd(), "server", "hud-config.json");
if (!fs.existsSync(DB_PATH)) {
  fs.writeFileSync(DB_PATH, JSON.stringify({
    history: [],
    latest: {
      overlayWorld: [0.02, 0.18, 0.001],
      overlayScale: 0.98,
      orbWorld: [0, 0, -0.001],
      orbOffset: [0, 0],
      orbRadius: 3.1,
      fractalZoom: 1.6,
      rotationSpeed: 0.006,
      updatedAt: new Date().toISOString(),
      v: 1
    }
  }, null, 2));
}

function load() { return JSON.parse(fs.readFileSync(DB_PATH, "utf-8")); }
function save(db) { fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2)); }

app.get("/api/health", (req, res) => res.json({ ok: true, ts: Date.now() }));

app.get("/api/hud/config", (req, res) => {
  const db = load();
  res.setHeader("ETag", db.latest.v.toString());
  res.json(db.latest);
});

app.get("/api/hud/config/:version", (req, res) => {
  const db = load();
  const v = parseInt(req.params.version, 10);
  if (db.latest.v === v) return res.json(db.latest);
  const found = db.history.find(h => h.v === v);
  if (!found) return res.status(404).json({ error: "version_not_found" });
  res.json(found);
});

app.put("/api/hud/config", (req, res) => {
  const ifMatch = req.headers["if-match"];
  if (!ifMatch) return res.status(428).json({ error: "missing_if_match" });
  const db = load();
  const currentV = db.latest.v.toString();
  if (currentV !== ifMatch) return res.status(412).json({ error: "version_mismatch", expected: currentV, got: ifMatch });

  const allowedKeys = ["overlayWorld","overlayScale","orbWorld","orbOffset","orbRadius","fractalZoom","rotationSpeed"];
  const next = { ...db.latest };
  for (const k of allowedKeys) { if (req.body[k] !== undefined) next[k] = req.body[k]; }

  db.history.push({ ...db.latest });
  next.v = db.latest.v + 1;
  next.updatedAt = new Date().toISOString();
  db.latest = next;
  save(db);
  res.setHeader("ETag", next.v.toString());
  res.json(next);
});

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`HUD config API listening on http://localhost:${port}`));

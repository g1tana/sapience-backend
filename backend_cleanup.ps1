# backend_cleanup.ps1
# Run from D:\Sapience\backend
param(
  [string]$Root = "D:\Sapience\backend"
)

Write-Host "Starting backend cleanup in $Root" -ForegroundColor Cyan
Set-Location $Root

# 1) Create target structure
$dirs = @(
  "server",
  "server\routes",
  "server\lib",
  "server\tests",
  "py",
  "py\services",
  "py\utils",
  "py\tests",
  "config",
  "logs",
  "scripts",
  "archive"
)
foreach ($d in $dirs) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
}

# 2) Move Node files → server/
$nodeFiles = @(
  "server.js",
  "voice.js",
  "package.json",
  "package-lock.json"
)
foreach ($f in $nodeFiles) {
  if (Test-Path $f) { Move-Item -Force $f "server\" }
}

# 3) Move Python and related → py/ or py/services/
$pyRootFiles = @(
  "main.py","config.py","requirements.txt","utils.py","db.py","ingest.py","tasks.py",
  "vision.py","speech.py","speech_recognition_loop.py","voice.py","multi_modal.py",
  "orchestrator.py","agent.py","chat.py","learning_store.py","memory.py","memory_store.py",
  "memory_view.py","recognition.py","tools.py","azure_test.py","test_azure.py","trace.py","registry.py"
)

foreach ($f in $pyRootFiles) {
  if (Test-Path $f) {
    # move service-like files into services
    if ($f -match "agent|chat|orchestrator|speech|voice|vision|multi_modal") {
      Move-Item -Force $f "py\services\"
    } else {
      Move-Item -Force $f "py\"
    }
  }
}

# 4) Move folders into py/
$toPyFolders = @("commands","intents","plugins","vision","voice","tests")
foreach ($fd in $toPyFolders) {
  if (Test-Path $fd) {
    Move-DirSafe -Source $fd -Dest (Join-Path "py" (Split-Path $fd -Leaf))
  }
}

# 5) Move data, logs, envs to dedicated locations
if (Test-Path "backend.log") { Move-Item -Force "backend.log" "logs\backend.log" }
if (Test-Path "response.wav") { Move-Item -Force "response.wav" "archive\response.wav" }
if (Test-Path "data") { Move-Item -Force "data" "archive\data" }
if (Test-Path "data_proposals.json") { Move-Item -Force "data_proposals.json" "archive\data_proposals.json" }
if (Test-Path "data_unknown.json") { Move-Item -Force "data_unknown.json" "archive\data_unknown.json" }

# 6) Consolidate venvs → archive (manual pick later)
$venvs = @("venv","venv310","venv311")
foreach ($v in $venvs) { if (Test-Path $v) { Move-Item -Force $v "archive\$v" } }

# 7) Keep .env at root; move config files to config/
$cfgFiles = @("config.yaml",".env","profile.json","init.py","sapience_core.py","sapience_chat.py","text_utils.py","orb.py","orb_log.py")
foreach ($f in $cfgFiles) {
  if (Test-Path $f) {
    switch ($f) {
      ".env" { # Leave in root
        Write-Host ".env retained at root" -ForegroundColor Yellow
      }
      default { Move-Item -Force $f "py\" }
    }
  }
}

# 8) Node API: create server/index.js if missing
$serverIndex = "server\index.js"
if (-not (Test-Path $serverIndex)) {
$indexContent = @'
import express from "express";
import fs from "fs";
import path from "path";
import bodyParser from "body-parser";

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
'@
  Set-Content -Path $serverIndex -Value $indexContent -Encoding UTF8
  Write-Host "Created server/index.js" -ForegroundColor Green
}

# 9) Node package.json (ESM) if missing
$serverPkg = "server\package.json"
if (-not (Test-Path $serverPkg)) {
$pkgContent = @'
{
  "name": "sapience-backend",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "node server/index.js",
    "dev": "node server/index.js",
    "lint": "eslint .",
    "format": "prettier -w ."
  },
  "dependencies": {
    "express": "^4.19.2",
    "body-parser": "^1.20.2"
  },
  "devDependencies": {
    "eslint": "^9.0.0",
    "prettier": "^3.3.3"
  }
}
'@
  Set-Content -Path $serverPkg -Value $pkgContent -Encoding UTF8
  Write-Host "Created server/package.json" -ForegroundColor Green
}

# 10) Write .gitignore
$gitignore = @'
logs/
node_modules/
server/hud-config.json
archive/
venv/
venv310/
venv311/
.env
*.wav
'@
Set-Content -Path ".gitignore" -Value $gitignore -Encoding UTF8

# 11) Write README.md skeleton
$readme = @'
# Sapience backend

## Structure
- server/: Node API for HUD config (/api/hud/config), health (/api/health)
- py/: Python services (agent, speech, vision, voice)
- config/: centralized configs
- logs/: runtime logs
- scripts/: ops

## Run
- Node API: cd server && npm install && npm run dev
- Python: create venv (3.11+), pip install -r py/requirements.txt

## Frontend proxy (Vite)
Proxy /api → http://localhost:4000

## HUD config endpoints
GET  /api/hud/config
PUT  /api/hud/config   (If-Match: current version)
GET  /api/hud/config/:version
'@
Set-Content -Path "README.md" -Value $readme -Encoding UTF8

# 12) Confirmation
Write-Host "Cleanup completed. Review 'server', 'py', 'config', 'logs', 'scripts', and 'archive'." -ForegroundColor Cyan
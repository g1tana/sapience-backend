import express from "express";
import path from "path";

const app = express();
const __dirname = path.resolve();

// -----------------------------
// CSP middleware
// -----------------------------
app.use((req, res, next) => {
  const csp = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "connect-src 'self' http://localhost:3001",
    "frame-ancestors 'none'"
  ].join("; ");
  res.setHeader("Content-Security-Policy", csp);
  next();
});

// -----------------------------
// Serve well-known probe files
// -----------------------------
app.use(
  "/.well-known/appspecific",
  express.static(path.join(__dirname, "well-known", "appspecific"), { dotfiles: "allow" })
);

// -----------------------------
// Optional explicit route (safe fallback)
// -----------------------------
app.get("/.well-known/appspecific/com.chrome.devtools.json", (req, res) => {
  res.json({
    name: "com.chrome.devtools",
    version: "1.0.0",
    description: "DevTools probe response",
    host: "http://localhost:3001"
  });
});

// -----------------------------
// Example app routes (adjust as needed)
// -----------------------------
app.get("/", (req, res) => {
  res.send("Sapience proxy running");
});

// -----------------------------
// Start server
// -----------------------------
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Listening on http://localhost:${PORT}`);
});
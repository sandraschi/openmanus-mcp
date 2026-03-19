import { Activity, Box, Layers, Server } from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";
import Fleet from "./Fleet";

type Health = { ok: boolean; service: string; version: string };
type Status = {
  version: string;
  openmanus_root: string | null;
  openmanus_valid: boolean;
  openmanus_details: {
    has_main_py: boolean;
    has_config_example: boolean;
    python_hint: string;
  } | null;
};

type View = "dashboard" | "fleet";

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [health, setHealth] = useState<Health | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [h, s] = await Promise.all([
          fetch("/api/v1/health").then((r) => r.json()),
          fetch("/api/v1/status").then((r) => r.json()),
        ]);
        if (!cancelled) {
          setHealth(h);
          setStatus(s);
        }
      } catch (e) {
        if (!cancelled) setErr(String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const navBtn = (id: View, label: string, icon: ReactNode) => (
    <button
      type="button"
      onClick={() => setView(id)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        width: "100%",
        textAlign: "left",
        padding: "8px 10px",
        marginBottom: 4,
        borderRadius: 8,
        border: "none",
        background: view === id ? "rgba(255,255,255,0.08)" : "transparent",
        color: view === id ? "var(--text)" : "var(--muted)",
        cursor: "pointer",
        fontSize: 14,
      }}
    >
      {icon}
      {label}
    </button>
  );

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        style={{
          width: 220,
          borderRight: "1px solid var(--border)",
          padding: "1.25rem",
          backdropFilter: "blur(12px)",
          background: "var(--panel)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24 }}>
          <Box size={22} color="var(--accent)" />
          <strong>openmanus-mcp</strong>
        </div>
        <nav>
          {navBtn("dashboard", "Dashboard", <Activity size={16} />)}
          {navBtn("fleet", "Fleet", <Layers size={16} />)}
          <div style={{ color: "var(--muted)", fontSize: 14, marginTop: 16, marginBottom: 8 }}>MCP</div>
          <div style={{ color: "var(--muted)", fontSize: 13, paddingLeft: 8 }}>stdio: openmanus_bridge</div>
        </nav>
      </aside>
      <main style={{ flex: 1, padding: "2rem" }}>
        {view === "fleet" ? (
          <Fleet />
        ) : (
          <>
            <header style={{ marginBottom: "2rem" }}>
              <h1 style={{ fontSize: "1.5rem", fontWeight: 600, margin: "0 0 0.5rem" }}>Dashboard</h1>
              <p style={{ color: "var(--muted)", margin: 0, maxWidth: 560 }}>
                FastMCP 3.1 + OpenManus (FOSS). Ports <strong>10769</strong> (UI) / <strong>10768</strong> (API). Use{" "}
                <strong>Fleet</strong> to clone curated MCP repos into <code>fleet/</code>.
              </p>
            </header>

            {err && (
              <div
                style={{
                  padding: 12,
                  borderRadius: 8,
                  border: "1px solid hsl(0 60% 40%)",
                  marginBottom: 16,
                }}
              >
                API unreachable: {err}. Start backend: <code>uv run python -m openmanus_mcp.run_api</code>
              </div>
            )}

            <div
              style={{
                display: "grid",
                gap: 16,
                gridTemplateColumns: "repeat(auto-fill,minmax(260px,1fr))",
              }}
            >
              <article
                style={{
                  padding: 20,
                  borderRadius: 12,
                  border: "1px solid var(--border)",
                  background: "var(--panel)",
                  backdropFilter: "blur(12px)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <Activity size={18} />
                  <strong>API health</strong>
                </div>
                <pre style={{ fontSize: 13, margin: 0, whiteSpace: "pre-wrap" }}>
                  {health ? JSON.stringify(health, null, 2) : "Loading…"}
                </pre>
              </article>

              <article
                style={{
                  padding: 20,
                  borderRadius: 12,
                  border: "1px solid var(--border)",
                  background: "var(--panel)",
                  backdropFilter: "blur(12px)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <Server size={18} />
                  <strong>OpenManus path</strong>
                </div>
                <pre style={{ fontSize: 13, margin: 0, whiteSpace: "pre-wrap" }}>
                  {status ? JSON.stringify(status, null, 2) : "Loading…"}
                </pre>
              </article>
            </div>

            <footer style={{ marginTop: "3rem", color: "var(--muted)", fontSize: 13 }}>
              MCP tool: <code>openmanus_bridge</code>
            </footer>
          </>
        )}
      </main>
    </div>
  );
}

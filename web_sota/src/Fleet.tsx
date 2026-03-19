import { CheckCircle2, ExternalLink, Loader2, Package, Rocket, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

export type FleetCatalogMember = {
  id: string;
  name: string;
  category: string;
  description: string;
  github_repo: string;
  install: { kind: string };
  webapp: { kind: string; script_relative: string } | null;
  onboarded: boolean;
  clone_path: string | null;
  install_ok: boolean | null;
};

type OnboardResult = {
  member_id: string;
  success: boolean;
  message: string;
  clone_path: string | null;
};

export default function Fleet() {
  const [members, setMembers] = useState<FleetCatalogMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [modal, setModal] = useState<{
    open: boolean;
    loading: boolean;
    results: OnboardResult[];
  }>({ open: false, loading: false, results: [] });

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const r = await fetch("/api/v1/fleet/catalog");
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      if (!data.success || !Array.isArray(data.members)) throw new Error("Bad catalog response");
      setMembers(data.members);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const onboardOne = async (id: string) => {
    setBusyId(id);
    setModal({ open: true, loading: true, results: [] });
    try {
      const r = await fetch("/api/v1/fleet/onboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ member_ids: [id] }),
      });
      const data = await r.json();
      const results: OnboardResult[] = data.results ?? [];
      setModal({ open: true, loading: false, results });
      await load();
    } catch (e) {
      setModal({
        open: true,
        loading: false,
        results: [{ member_id: id, success: false, message: String(e), clone_path: null }],
      });
    } finally {
      setBusyId(null);
    }
  };

  const startWebapp = async (id: string) => {
    setBusyId(id);
    try {
      const r = await fetch("/api/v1/fleet/webapp/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ member_id: id }),
      });
      const data = await r.json();
      if (!data.success) {
        setModal({
          open: true,
          loading: false,
          results: [{ member_id: id, success: false, message: data.message ?? "Failed", clone_path: null }],
        });
      } else {
        setModal({
          open: true,
          loading: false,
          results: [
            {
              member_id: id,
              success: true,
              message: `${data.message} (pid ${data.pid})`,
              clone_path: null,
            },
          ],
        });
      }
    } catch (e) {
      setModal({
        open: true,
        loading: false,
        results: [{ member_id: id, success: false, message: String(e), clone_path: null }],
      });
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div style={{ maxWidth: 960 }}>
      <header style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <Rocket size={28} color="var(--accent)" />
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600, margin: 0 }}>Fleet onboarding</h1>
        </div>
        <p style={{ color: "var(--muted)", margin: 0, maxWidth: 720, lineHeight: 1.5 }}>
          Curated MCP repos (RoboFang-style). <strong>Onboard</strong> clones into your{" "}
          <code style={{ fontSize: 12 }}>fleet/</code> workspace (or{" "}
          <code style={{ fontSize: 12 }}>OPENMANUS_FLEET_ROOT</code>) and runs install steps. Connect MCP clients to
          those clones separately — generated snippets can be added later per member.
        </p>
      </header>

      {error && (
        <div
          style={{
            padding: 12,
            borderRadius: 8,
            border: "1px solid hsl(0 60% 40%)",
            marginBottom: 16,
            fontSize: 14,
          }}
        >
          {error}{" "}
          <button type="button" onClick={() => void load()} style={{ marginLeft: 8 }}>
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading catalog…</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {members.map((m) => (
            <article
              key={m.id}
              style={{
                padding: 16,
                borderRadius: 12,
                border: "1px solid var(--border)",
                background: "var(--panel)",
                backdropFilter: "blur(12px)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div style={{ flex: "1 1 280px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <Package size={18} />
                    <strong>{m.name}</strong>
                    <span style={{ color: "var(--muted)", fontSize: 12 }}>{m.category}</span>
                  </div>
                  <p style={{ margin: "0 0 8px", fontSize: 14, color: "var(--muted)", lineHeight: 1.45 }}>
                    {m.description}
                  </p>
                  <a
                    href={`https://github.com/${m.github_repo}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: 13, display: "inline-flex", alignItems: "center", gap: 4 }}
                  >
                    <ExternalLink size={14} />
                    {m.github_repo}
                  </a>
                  {m.onboarded && m.clone_path && (
                    <div style={{ marginTop: 8, fontSize: 12, fontFamily: "ui-monospace, monospace" }}>
                      <span style={{ color: "var(--muted)" }}>Clone: </span>
                      {m.clone_path}
                    </div>
                  )}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "stretch" }}>
                  <button
                    type="button"
                    disabled={busyId !== null}
                    onClick={() => void onboardOne(m.id)}
                    style={{
                      padding: "8px 16px",
                      borderRadius: 8,
                      border: "1px solid var(--accent)",
                      background: m.onboarded && m.install_ok ? "transparent" : "var(--accent)",
                      color: m.onboarded && m.install_ok ? "var(--accent)" : "#0a0a0a",
                      fontWeight: 600,
                      cursor: busyId ? "wait" : "pointer",
                      opacity: busyId && busyId !== m.id ? 0.5 : 1,
                    }}
                  >
                    {busyId === m.id ? (
                      <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <Loader2 size={16} className="spin" /> Working…
                      </span>
                    ) : m.onboarded && m.install_ok ? (
                      "Re-run onboard"
                    ) : m.onboarded && m.install_ok === false ? (
                      "Retry install"
                    ) : (
                      "Onboard"
                    )}
                  </button>
                  {m.webapp ? (
                    <button
                      type="button"
                      disabled={busyId !== null || !m.onboarded || !m.install_ok}
                      onClick={() => void startWebapp(m.id)}
                      style={{
                        padding: "8px 16px",
                        borderRadius: 8,
                        border: "1px solid var(--border)",
                        background: "transparent",
                        color: "var(--text)",
                        cursor: busyId ? "wait" : "pointer",
                      }}
                    >
                      Start webapp
                    </button>
                  ) : (
                    <span style={{ fontSize: 11, color: "var(--muted)", textAlign: "center" }}>No webapp in catalog</span>
                  )}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {modal.open && (
        <div
          role="dialog"
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 50,
            padding: 16,
          }}
          onClick={() => !modal.loading && setModal({ open: false, loading: false, results: [] })}
        >
          <div
            style={{
              background: "var(--panel)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              padding: 20,
              maxWidth: 480,
              width: "100%",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ margin: "0 0 12px" }}>Onboard result</h3>
            {modal.loading ? (
              <p style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Loader2 size={18} className="spin" /> Cloning / installing…
              </p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 0, listStyle: "none" }}>
                {modal.results.map((res) => (
                  <li
                    key={res.member_id}
                    style={{
                      display: "flex",
                      gap: 8,
                      alignItems: "flex-start",
                      marginBottom: 10,
                      fontSize: 14,
                    }}
                  >
                    {res.success ? (
                      <CheckCircle2 size={18} color="hsl(142 70% 45%)" style={{ flexShrink: 0 }} />
                    ) : (
                      <XCircle size={18} color="hsl(0 70% 50%)" style={{ flexShrink: 0 }} />
                    )}
                    <div>
                      <strong>{res.member_id}</strong>
                      <div style={{ color: "var(--muted)", marginTop: 4 }}>{res.message}</div>
                      {res.clone_path && (
                        <code style={{ fontSize: 11, display: "block", marginTop: 6 }}>{res.clone_path}</code>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
            {!modal.loading && (
              <button
                type="button"
                onClick={() => setModal({ open: false, loading: false, results: [] })}
                style={{ marginTop: 16 }}
              >
                Close
              </button>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        .spin { animation: spin 0.9s linear infinite; }
      `}</style>
    </div>
  );
}

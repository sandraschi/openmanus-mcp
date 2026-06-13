import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

type Glom = { reachable: boolean; status_code?: number; error?: string; body?: unknown };
type RuntimeSettings = Record<string, unknown>;

type SupervisorSlice = {
  supervisor_enabled: boolean;
  supervisor_tick_s: number;
  supervisor_schedules: number;
  supervisor_heartbeat: {
    running: boolean;
    uptime_s: number | null;
    tick_count: number;
    last_tick_age_s: number | null;
    last_error: string | null;
    schedules_fired_total: number;
  };
};

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <div className="space-y-3">
            <select className="h-9 w-full rounded-md border border-border/50 bg-background/20 px-3 text-sm" value={selectedProvider} onChange={(e) => { setSelectedProvider(e.target.value); save(e.target.value, ""); }}>
                <option value="ollama">Ollama</option>
                <option value="lm_studio">LM Studio</option>
            </select>
            <select className="h-9 w-full rounded-md border border-border/50 bg-background/20 px-3 text-sm" value={selectedModel} onChange={(e) => { setSelectedModel(e.target.value); save(selectedProvider, e.target.value); }}>
                {models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
            </select>
        </div>
    );
}

export default function SettingsPage() {
  const [ollama, setOllama] = useState<Glom | null>(null);
  const [lm, setLm] = useState<Glom | null>(null);
  const [runtime, setRuntime] = useState<RuntimeSettings | null>(null);
  const [supervisor, setSupervisor] = useState<SupervisorSlice | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const root = document.documentElement;
    const current = root.classList.contains("dark") ? "dark" : "light";
    setTheme(current);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("openmanus-theme", theme);
  }, [theme]);

  useEffect(() => {
    let c = false;
    void (async () => {
      setLoading(true);
      try {
        const [o, l, r, st] = await Promise.all([
          fetch("/api/v1/glom/ollama").then((r) => r.json()),
          fetch("/api/v1/glom/lmstudio").then((r) => r.json()),
          fetch("/api/v1/settings/runtime").then((r) => r.json()),
          fetch("/api/v1/status").then((r) => r.json()),
        ]);
        if (!c) {
          setOllama(o as Glom);
          setLm(l as Glom);
          setRuntime(r as RuntimeSettings);
          const s = st as Record<string, unknown>;
          if (
            typeof s.supervisor_enabled === "boolean" &&
            typeof s.supervisor_tick_s === "number" &&
            typeof s.supervisor_schedules === "number" &&
            s.supervisor_heartbeat &&
            typeof s.supervisor_heartbeat === "object"
          ) {
            setSupervisor(s as unknown as SupervisorSlice);
          } else {
            setSupervisor(null);
          }
        }
      } catch {
        if (!c) {
          setOllama({ reachable: false, error: "fetch failed" });
          setLm({ reachable: false, error: "fetch failed" });
          setSupervisor(null);
        }
      } finally {
        if (!c) setLoading(false);
      }
    })();
    return () => {
      c = true;
    };
  }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          <strong>Glom On</strong> — server-side probes (no browser CORS): Ollama <code className="rounded bg-muted px-1">11434</code>, LM
          Studio <code className="rounded bg-muted px-1">1234</code>.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Theme</CardTitle>
          <CardDescription>Persisted in localStorage key `openmanus-theme`.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Button variant={theme === "dark" ? "default" : "outline"} onClick={() => setTheme("dark")}>
            Dark
          </Button>
          <Button variant={theme === "light" ? "default" : "outline"} onClick={() => setTheme("light")}>
            Light
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Local LLM</CardTitle>
          <CardDescription>Provider and model selection</CardDescription>
        </CardHeader>
        <CardContent>
          <LLMSettings />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Supervisor</CardTitle>
          <CardDescription>
            From <code className="rounded bg-muted px-1">GET /api/v1/status</code> — enable with{" "}
            <code className="rounded bg-muted px-1">OPENMANUS_SUPERVISOR_ENABLED=true</code>. Detail:{" "}
            <code className="rounded bg-muted px-1">/api/v1/supervisor/heartbeat</code>, schedules{" "}
            <code className="rounded bg-muted px-1">/api/v1/supervisor/schedules</code>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-24 w-full" />
          ) : supervisor ? (
            <div className="space-y-2 text-sm">
              <div>
                <strong>Enabled (config):</strong> {supervisor.supervisor_enabled ? "yes" : "no"} ·{" "}
                <strong>Tick:</strong> {supervisor.supervisor_tick_s}s · <strong>Schedules:</strong> {supervisor.supervisor_schedules}
              </div>
              <div className="rounded-md border border-border/60 bg-muted/30 p-3 font-mono text-xs">
                <div>
                  <strong>Loop running:</strong> {supervisor.supervisor_heartbeat.running ? "yes" : "no"}
                </div>
                <div>
                  <strong>Uptime (s):</strong> {supervisor.supervisor_heartbeat.uptime_s ?? "—"} · <strong>Ticks:</strong>{" "}
                  {supervisor.supervisor_heartbeat.tick_count} · <strong>Last tick age (s):</strong>{" "}
                  {supervisor.supervisor_heartbeat.last_tick_age_s ?? "—"}
                </div>
                <div>
                  <strong>Schedules fired (total):</strong> {supervisor.supervisor_heartbeat.schedules_fired_total}
                </div>
                {supervisor.supervisor_heartbeat.last_error ? (
                  <div className="mt-2 text-destructive">
                    <strong>Last error:</strong> {supervisor.supervisor_heartbeat.last_error}
                  </div>
                ) : null}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Supervisor fields unavailable (status parse failed).</p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Ollama</CardTitle>
            <CardDescription>127.0.0.1:11434/api/tags</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-20 w-full" />
            ) : (
              <pre className="whitespace-pre-wrap break-words font-mono text-xs">{JSON.stringify(ollama, null, 2)}</pre>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">LM Studio</CardTitle>
            <CardDescription>127.0.0.1:1234/v1/models</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-20 w-full" />
            ) : (
              <pre className="whitespace-pre-wrap break-words font-mono text-xs">{JSON.stringify(lm, null, 2)}</pre>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Runtime settings</CardTitle>
          <CardDescription>GET `/api/v1/settings/runtime`</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <pre className="whitespace-pre-wrap break-words font-mono text-xs">{JSON.stringify(runtime, null, 2)}</pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

type Glom = { reachable: boolean; status_code?: number; error?: string; body?: unknown };
type RuntimeSettings = Record<string, unknown>;

export default function SettingsPage() {
  const [ollama, setOllama] = useState<Glom | null>(null);
  const [lm, setLm] = useState<Glom | null>(null);
  const [runtime, setRuntime] = useState<RuntimeSettings | null>(null);
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
        const [o, l, r] = await Promise.all([
          fetch("/api/v1/glom/ollama").then((r) => r.json()),
          fetch("/api/v1/glom/lmstudio").then((r) => r.json()),
          fetch("/api/v1/settings/runtime").then((r) => r.json()),
        ]);
        if (!c) {
          setOllama(o as Glom);
          setLm(l as Glom);
          setRuntime(r as RuntimeSettings);
        }
      } catch {
        if (!c) {
          setOllama({ reachable: false, error: "fetch failed" });
          setLm({ reachable: false, error: "fetch failed" });
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

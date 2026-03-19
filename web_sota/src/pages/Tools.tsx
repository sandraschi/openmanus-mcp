import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useLogger } from "@/contexts/LoggerContext";

export default function ToolsPage() {
  const { appendLog } = useLogger();
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [operation, setOperation] = useState("run_prompt");
  const [prompt, setPrompt] = useState("");
  const [entryPoint, setEntryPoint] = useState("main.py");
  const [dryRunResult, setDryRunResult] = useState<unknown>(null);
  const [dryRunBusy, setDryRunBusy] = useState(false);

  useEffect(() => {
    let c = false;
    void (async () => {
      setLoading(true);
      try {
        const r = await fetch("/api/v1/mcp/tools");
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const j = await r.json();
        if (!c) setData(j);
      } catch (e) {
        if (!c) setErr(String(e));
      } finally {
        if (!c) setLoading(false);
      }
    })();
    return () => {
      c = true;
    };
  }, []);

  const dryRun = async () => {
    setDryRunBusy(true);
    setDryRunResult(null);
    try {
      const payload: Record<string, unknown> = {
        operation,
      };
      if (operation === "run_prompt" || operation === "run_prompt_async") {
        payload.prompt = prompt;
        payload.entry_point = entryPoint;
      }
      const res = await fetch("/api/v1/mcp/dry-run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const out = await res.json();
      setDryRunResult(out);
      appendLog("INFO", "dry-run executed via /api/v1/mcp/dry-run");
    } catch (e) {
      const msg = String(e);
      appendLog("ERROR", msg);
      setDryRunResult({ success: false, error: msg });
    } finally {
      setDryRunBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">MCP inspector</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Schema for <code className="rounded bg-muted px-1">openmanus_bridge</code> (GET{" "}
          <code className="rounded bg-muted px-1">/api/v1/mcp/tools</code>).
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base">Tool manifest</CardTitle>
            <CardDescription>Operations and REST mirrors</CardDescription>
          </div>
          <Button type="button" variant="secondary" onClick={() => void dryRun()} disabled={dryRunBusy}>
            {dryRunBusy ? "Running…" : "Run dry-run"}
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-4 grid gap-3 rounded-md border border-border/60 p-3 md:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="op">Operation</Label>
              <select
                id="op"
                value={operation}
                onChange={(e) => setOperation(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background/80 px-3 text-sm"
              >
                <option value="status">status</option>
                <option value="validate">validate</option>
                <option value="run_prompt">run_prompt</option>
                <option value="run_prompt_async">run_prompt_async</option>
                <option value="job_status">job_status</option>
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="entry">Entry point</Label>
              <select
                id="entry"
                value={entryPoint}
                onChange={(e) => setEntryPoint(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background/80 px-3 text-sm"
              >
                <option value="main.py">main.py</option>
                <option value="run_flow.py">run_flow.py</option>
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="prompt">Prompt</Label>
              <Input id="prompt" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Prompt for run_* ops" />
            </div>
          </div>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-4/6" />
            </div>
          ) : err ? (
            <p className="text-sm text-destructive">{err}</p>
          ) : (
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border/60 bg-muted/30 p-4 font-mono text-xs">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
          {dryRunResult ? (
            <pre className="mt-4 max-h-[280px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border/60 bg-muted/30 p-4 font-mono text-xs">
              {JSON.stringify(dryRunResult, null, 2)}
            </pre>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}

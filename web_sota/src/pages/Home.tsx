import { Activity, PlayCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useLogger } from "@/contexts/LoggerContext";

type Health = { ok: boolean; service: string; version: string };
type Status = {
  version: string;
  openmanus_root: string | null;
  openmanus_valid: boolean;
  runner_timeout_s: number;
  async_jobs_pending?: number;
  async_jobs_stored?: number;
  job_store_max_completed?: number;
};

export default function HomePage() {
  const { appendLog } = useLogger();
  const [health, setHealth] = useState<Health | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let c = false;
    void (async () => {
      setLoading(true);
      setErr(null);
      try {
        const [h, s] = await Promise.all([
          fetch("/api/v1/health").then((r) => r.json()),
          fetch("/api/v1/status").then((r) => r.json()),
        ]);
        if (!c) {
          setHealth(h as Health);
          setStatus(s as Status);
        }
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

  useEffect(() => {
    appendLog("INFO", "Dashboard loaded");
  }, [appendLog]);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          FastMCP 3.1 + OpenManus. UI <strong>10769</strong> · API <strong>10768</strong>. Use{" "}
          <Link to="/run" className="text-primary underline-offset-4 hover:underline">
            Run
          </Link>{" "}
          or{" "}
          <Link to="/fleet" className="text-primary underline-offset-4 hover:underline">
            Fleet
          </Link>
          .
        </p>
      </header>

      {err && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm">
          API unreachable: {err}. Start backend from repo root:{" "}
          <code className="rounded bg-muted px-1 py-0.5 text-xs">uv run python -m openmanus_mcp.run_api</code>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Activity className="h-4 w-4" />
              API health
            </CardTitle>
            <CardDescription>GET /api/v1/health</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            ) : (
              <pre className="whitespace-pre-wrap break-words font-mono text-xs">{JSON.stringify(health, null, 2)}</pre>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <PlayCircle className="h-4 w-4" />
              OpenManus + runner
            </CardTitle>
            <CardDescription>GET /api/v1/status</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ) : (
              <pre className="whitespace-pre-wrap break-words font-mono text-xs">
                {JSON.stringify(
                  status
                    ? {
                        openmanus_root: status.openmanus_root,
                        openmanus_valid: status.openmanus_valid,
                        runner_timeout_s: status.runner_timeout_s,
                        async_jobs_pending: status.async_jobs_pending,
                        async_jobs_stored: status.async_jobs_stored,
                        job_store_max_completed: status.job_store_max_completed,
                      }
                    : null,
                  null,
                  2,
                )}
              </pre>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button asChild>
          <Link to="/run">Open Run</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/tools">MCP tools</Link>
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        MCP stdio tool: <code className="rounded bg-muted px-1">openmanus_bridge</code>
      </p>
    </div>
  );
}

import { Activity, Bot, PlayCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useLogger } from "@/contexts/LoggerContext";

type Status = {
  version: string;
  openmanus_root: string | null;
  openmanus_valid: boolean;
  runner_timeout_s: number;
  async_jobs_pending?: number;
  async_jobs_stored?: number;
  job_store_max_completed?: number;
  job_store_path?: string;
};

export default function HomePage() {
  const { appendLog } = useLogger();
  const [status, setStatus] = useState<Status | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let c = false;
    void (async () => {
      setLoading(true);
      setErr(null);
      try {
        const s = await fetch("/api/v1/status").then((r) => r.json());
        if (!c) {
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
    <div className="mx-auto max-w-5xl space-y-8 pb-10">
      <header>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <Activity className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Fleet Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Modernized OpenManus Control Plane · <strong>FastMCP 3.2.0</strong>
            </p>
          </div>
        </div>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-muted-foreground/80">
          The <strong>OpenManus MCP Bridge</strong> provides a high-performance orchestration layer for the FOSS OpenManus agent. 
          Managed via persistent job stores and integrated with physical robotics hardware.
        </p>
      </header>

      {err && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm">
          API unreachable: {err}. Start backend from repo root:{" "}
          <code className="rounded bg-muted px-1 py-0.5 text-xs">uv run python -m openmanus_mcp.run_api</code>
        </div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {/* Core Status Card */}
        <Card className="border-border/60 bg-card/40 backdrop-blur-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <PlayCircle className="h-4 w-4 text-primary" />
              OpenManus Core
            </CardTitle>
            <CardDescription>Install & Runner Status</CardDescription>
          </CardHeader>
          <CardContent className="text-sm">
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            ) : status ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Valid Root</span>
                  <span className={status.openmanus_valid ? "text-emerald-500 font-medium" : "text-amber-500 font-medium"}>
                    {status.openmanus_valid ? "YES" : "NO"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Timeout</span>
                  <span className="font-mono">{status.runner_timeout_s}s</span>
                </div>
                <div className="overflow-hidden text-ellipsis whitespace-nowrap text-[10px] text-muted-foreground/60">
                  {status.openmanus_root || "Not Set"}
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground italic">No data</p>
            )}
          </CardContent>
        </Card>

        {/* Persistence Card */}
        <Card className="border-border/60 bg-card/40 backdrop-blur-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <Activity className="h-4 w-4 text-blue-400" />
              Job Persistence
            </CardTitle>
            <CardDescription>File-based Storage</CardDescription>
          </CardHeader>
          <CardContent className="text-sm">
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ) : status ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Stored Jobs</span>
                  <span className="font-bold">{status.async_jobs_stored ?? 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Pending</span>
                  <span className={status.async_jobs_pending ? "text-blue-400 font-bold" : "text-muted-foreground"}>
                    {status.async_jobs_pending ?? 0}
                  </span>
                </div>
                <div className="overflow-hidden text-ellipsis whitespace-nowrap text-[10px] text-muted-foreground/60">
                  {status.job_store_path || "In-Memory"}
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground italic">No data</p>
            )}
          </CardContent>
        </Card>

        {/* Robotics Alpha Card */}
        <Card className="border-border/60 bg-card/40 backdrop-blur-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <Bot className="h-4 w-4 text-primary" />
              Hardware Shield
            </CardTitle>
            <CardDescription>Robotics Bridge Alpha</CardDescription>
          </CardHeader>
          <CardContent className="text-sm italic text-muted-foreground">
            Discovered local units in current network fleet. Yahboom + Unitree support.
            <div className="mt-4">
              <Button asChild size="sm" variant="outline" className="w-full text-xs">
                <Link to="/robots">Open Robot Deck</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap items-center gap-4 pt-4 text-sm font-medium">
        <Link to="/run" className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-primary-foreground shadow-sm hover:brightness-110">
          <PlayCircle className="h-4 w-4" /> Start Agent Run
        </Link>
        <Link to="/fleet" className="flex items-center gap-2 rounded-lg border border-border/60 bg-card/60 px-4 py-2 hover:bg-card/80">
          Fleet Explorer
        </Link>
        <Link to="/tools" className="flex items-center gap-2 rounded-lg border border-border/60 bg-card/60 px-4 py-2 hover:bg-card/80">
          MCP Tools
        </Link>
      </div>

      <footer className="mt-10 border-t border-border/20 pt-6">
        <div className="flex flex-col gap-4 text-xs text-muted-foreground/60 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <code className="rounded bg-muted/30 px-1 py-0.5">openmanus_bridge</code>
            <span>Portmanteau Standard v1.2</span>
          </div>
          <div>
            Built with <strong>Next-SOTA Design System</strong> · Vienna 2026
          </div>
        </div>
      </footer>
    </div>
  );
}

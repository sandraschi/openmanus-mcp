import { Activity, PlayCircle, Server, ListTree, Cpu, HardDrive, Terminal, AppWindow } from "lucide-react";
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

function StatCard({ icon: Icon, label, value, sub }: { icon: any; label: string; value: string | number; sub?: string }) {
  return (
    <Card className="border-border/60 bg-card/40 backdrop-blur-md">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-primary" />
          <CardTitle className="text-base font-semibold">{label}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {sub && <div className="text-xs text-muted-foreground mt-0.5">{sub}</div>}
      </CardContent>
    </Card>
  );
}

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
        if (!c) setStatus(s as Status);
      } catch (e) {
        if (!c) setErr(String(e));
      } finally {
        if (!c) setLoading(false);
      }
    })();
    return () => { c = true; };
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
            <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              OpenManus MCP Bridge · <strong>FastMCP 3.2</strong>
            </p>
          </div>
        </div>
      </header>

      {err && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm">
          API unreachable: {err}. Start backend from repo root:{" "}
          <code className="rounded bg-muted px-1 py-0.5 text-xs">uv run python -m openmanus_mcp.run_api</code>
        </div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Server} label="Status" value={status?.openmanus_valid ? "Ready" : "Unconfigured"} sub={status?.version || "?"} />
        <StatCard icon={ListTree} label="Stored Jobs" value={status?.async_jobs_stored ?? 0} sub={`${status?.async_jobs_pending ?? 0} pending`} />
        <StatCard icon={Terminal} label="Timeout" value={`${status?.runner_timeout_s ?? "?"}s`} sub="runner timeout" />
        <StatCard icon={HardDrive} label="Tier" value="FastMCP 3.2" sub="SOTA compliant" />
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
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

        <Card className="border-border/60 bg-card/40 backdrop-blur-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <AppWindow className="h-4 w-4 text-primary" />
              Quick Actions
            </CardTitle>
            <CardDescription>Common operations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild size="sm" variant="outline" className="w-full">
              <Link to="/run"><PlayCircle className="mr-2 h-4 w-4" /> Start Agent Run</Link>
            </Button>
            <Button asChild size="sm" variant="outline" className="w-full">
              <Link to="/tools"><Terminal className="mr-2 h-4 w-4" /> MCP Tools</Link>
            </Button>
            <Button asChild size="sm" variant="outline" className="w-full">
              <Link to="/status"><Activity className="mr-2 h-4 w-4" /> Status & Audit</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <footer className="mt-10 border-t border-border/20 pt-6">
        <div className="flex flex-col gap-4 text-xs text-muted-foreground/60 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <code className="rounded bg-muted/30 px-1 py-0.5">openmanus_bridge</code>
            <span>Portmanteau Standard v1.2</span>
          </div>
          <div>Built with SOTA Design System · Vienna 2026</div>
        </div>
      </footer>
    </div>
  );
}

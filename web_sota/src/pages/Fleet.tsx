import { CheckCircle2, ExternalLink, Loader2, Package, PlaySquare, RefreshCcw, Rocket, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

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

export default function FleetPage() {
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
    <div className="mx-auto max-w-5xl space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Rocket className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">Fleet Onboarding</h1>
          </div>
          <p className="max-w-2xl text-muted-foreground">
            Curated MCP repository catalog. <strong>Onboard</strong> clones into your local fleet root 
            and prepares the environment automatically.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
          <RefreshCcw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
          Refresh Catalog
        </Button>
      </header>

      {error ? (
        <Alert variant="destructive" className="bg-destructive/10">
          <XCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription className="flex items-center gap-4">
            {error}
            <Button variant="outline" size="sm" onClick={() => void load()}>Retry</Button>
          </AlertDescription>
        </Alert>
      ) : null}

      {loading ? (
        <div className="grid gap-6 sm:grid-cols-2">
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
          <Skeleton className="h-40 w-full rounded-xl" />
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2">
          {members.map((m) => (
            <Card key={m.id} className="group relative overflow-hidden border-border/60 bg-card/60 backdrop-blur-xl transition-all hover:border-primary/40 hover:shadow-lg">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Package className="h-6 w-6" />
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <Badge variant={m.onboarded ? "default" : "secondary"} className={m.onboarded ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" : ""}>
                      {m.onboarded ? "ONBOARDED" : "AVAILABLE"}
                    </Badge>
                    {m.category && (
                      <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">{m.category}</span>
                    )}
                  </div>
                </div>
                <CardTitle className="mt-4 text-xl">{m.name}</CardTitle>
                <CardDescription className="line-clamp-2 min-h-[2.5rem] leading-relaxed">
                  {m.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <a
                    href={`https://github.com/${m.github_repo}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
                  >
                    <ExternalLink className="h-3 w-3" />
                    GitHub Source
                  </a>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    disabled={busyId !== null}
                    variant={m.onboarded && m.install_ok ? "outline" : "default"}
                    className={cn("flex-1", m.onboarded && m.install_ok && "border-primary/50 text-primary hover:bg-primary/5")}
                    onClick={() => void onboardOne(m.id)}
                  >
                    {busyId === m.id ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Working...
                      </>
                    ) : m.onboarded && m.install_ok ? (
                      "Update"
                    ) : (
                      "Onboard"
                    )}
                  </Button>
                  
                  {m.webapp && (
                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={busyId !== null || !m.onboarded || !m.install_ok}
                      className="px-3"
                      onClick={() => void startWebapp(m.id)}
                      title="Start Webapp"
                    >
                      <PlaySquare className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
              {/* Subtle accent hover effect */}
              <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/5 blur-3xl transition-colors group-hover:bg-primary/10" />
            </Card>
          ))}
        </div>
      )}

      {modal.open ? (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onClick={() => !modal.loading && setModal({ open: false, loading: false, results: [] })}
        >
          <div
            className="w-full max-w-md rounded-xl border border-border/80 bg-card p-5 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-3 text-lg font-semibold">Result</h3>
            {modal.loading ? (
              <p className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Cloning / installing…
              </p>
            ) : (
              <ul className="list-none space-y-3 p-0">
                {modal.results.map((res) => (
                  <li key={res.member_id} className="flex gap-2 text-sm">
                    {res.success ? (
                      <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />
                    ) : (
                      <XCircle className="h-5 w-5 shrink-0 text-red-400" />
                    )}
                    <div>
                      <strong>{res.member_id}</strong>
                      <div className="mt-1 text-muted-foreground">{res.message}</div>
                      {res.clone_path ? <code className="mt-2 block text-[11px]">{res.clone_path}</code> : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
            {!modal.loading ? (
              <Button type="button" className="mt-4" variant="secondary" onClick={() => setModal({ open: false, loading: false, results: [] })}>
                Close
              </Button>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}

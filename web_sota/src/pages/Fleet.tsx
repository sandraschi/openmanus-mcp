import { CheckCircle2, ExternalLink, Loader2, Package, Rocket, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <div className="mb-2 flex items-center gap-2">
          <Rocket className="h-7 w-7 text-primary" />
          <h1 className="text-2xl font-semibold tracking-tight">Fleet onboarding</h1>
        </div>
        <p className="max-w-3xl text-sm text-muted-foreground">
          Curated MCP repos. <strong>Onboard</strong> clones into <code className="rounded bg-muted px-1 text-xs">fleet/</code> (or{" "}
          <code className="rounded bg-muted px-1 text-xs">OPENMANUS_FLEET_ROOT</code>) and runs install steps.
        </p>
      </header>

      {error ? (
        <div className="flex flex-wrap items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm">
          {error}
          <Button type="button" variant="outline" size="sm" onClick={() => void load()}>
            Retry
          </Button>
        </div>
      ) : null}

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {members.map((m) => (
            <Card key={m.id} className="border-border/80 bg-card/70 backdrop-blur-xl transition-colors hover:border-border">
              <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:justify-between">
                <div className="min-w-0 flex-1 space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <Package className="h-4 w-4 shrink-0 text-primary" />
                    <span className="font-semibold">{m.name}</span>
                    <span className="text-xs text-muted-foreground">{m.category}</span>
                  </div>
                  <p className="text-sm leading-relaxed text-muted-foreground">{m.description}</p>
                  <a
                    href={`https://github.com/${m.github_repo}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-primary underline-offset-4 hover:underline"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    {m.github_repo}
                  </a>
                  {m.onboarded && m.clone_path ? (
                    <div className="font-mono text-xs text-muted-foreground">
                      Clone: <span className="text-foreground/90">{m.clone_path}</span>
                    </div>
                  ) : null}
                </div>
                <div className="flex shrink-0 flex-col gap-2 sm:w-44">
                  <Button
                    type="button"
                    disabled={busyId !== null}
                    variant={m.onboarded && m.install_ok ? "outline" : "default"}
                    className={cn("w-full", m.onboarded && m.install_ok && "border-primary text-primary")}
                    onClick={() => void onboardOne(m.id)}
                  >
                    {busyId === m.id ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" /> Working…
                      </span>
                    ) : m.onboarded && m.install_ok ? (
                      "Re-run onboard"
                    ) : m.onboarded && m.install_ok === false ? (
                      "Retry install"
                    ) : (
                      "Onboard"
                    )}
                  </Button>
                  {m.webapp ? (
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={busyId !== null || !m.onboarded || !m.install_ok}
                      className="w-full"
                      onClick={() => void startWebapp(m.id)}
                    >
                      Start webapp
                    </Button>
                  ) : (
                    <span className="text-center text-[11px] text-muted-foreground">No webapp in catalog</span>
                  )}
                </div>
              </CardContent>
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

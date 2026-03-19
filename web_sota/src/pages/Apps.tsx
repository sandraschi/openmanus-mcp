import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function AppsPage() {
  const [glama, setGlama] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let c = false;
    void (async () => {
      setLoading(true);
      try {
        const r = await fetch("/api/v1/glama");
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const j = (await r.json()) as Record<string, unknown>;
        if (!c) setGlama(j);
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

  const homepage = typeof glama?.homepage === "string" ? glama.homepage : null;
  const repo = glama?.repository as { url?: string } | undefined;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Apps hub</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Glama discovery payload from <code className="rounded bg-muted px-1">GET /api/v1/glama</code> (repo{" "}
          <code className="rounded bg-muted px-1">glama.json</code>).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Manifest</CardTitle>
          <CardDescription>Fleet / registry alignment</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ) : err ? (
            <p className="text-sm text-destructive">{err}</p>
          ) : (
            <>
              <div className="flex flex-wrap gap-3 text-sm">
                {homepage ? (
                  <a
                    href={homepage}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
                  >
                    Homepage <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                ) : null}
                {repo?.url ? (
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
                  >
                    Repository <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                ) : null}
              </div>
              <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border/60 bg-muted/30 p-4 font-mono text-xs">
                {JSON.stringify(glama, null, 2)}
              </pre>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

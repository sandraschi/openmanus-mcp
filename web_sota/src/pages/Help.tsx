import { useEffect, useState } from "react";
import { ExternalLink } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";

export default function HelpPage() {
  const [docs, setDocs] = useState<string[]>([]);
  const [doc, setDoc] = useState("");
  const [text, setText] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let c = false;
    void (async () => {
      try {
        const res = await fetch("/api/v1/docs");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const payload = (await res.json()) as { documents?: string[] };
        const names = Array.isArray(payload.documents) ? payload.documents : [];
        if (!c) {
          setDocs(names);
          setDoc((prev) => prev || names[0] || "");
        }
      } catch (e) {
        if (!c) setErr(String(e));
      }
    })();
    return () => {
      c = true;
    };
  }, []);

  useEffect(() => {
    if (!doc) return;
    let c = false;
    void (async () => {
      setLoading(true);
      setErr(null);
      try {
        const r = await fetch(`/api/v1/docs/${encodeURIComponent(doc)}`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const t = await r.text();
        if (!c) setText(t);
      } catch (e) {
        if (!c) {
          setErr(String(e));
          setText(null);
        }
      } finally {
        if (!c) setLoading(false);
      }
    })();
    return () => {
      c = true;
    };
  }, [doc]);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Help</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Project docs from <code className="rounded bg-muted px-1">docs/</code> via API. Central standards: MCP Central Docs{" "}
          <strong>WEBAPP_STANDARDS.md</strong>.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">LM Studio integration</CardTitle>
          <CardDescription>Recommended local model setup for OpenManus and dashboard chat</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <ol className="list-decimal space-y-2 pl-5">
            <li>Install LM Studio and start the local server (OpenAI-compatible API).</li>
            <li>
              Set <code className="rounded bg-muted px-1">OPENMANUS_LMSTUDIO_BASE_URL</code> (default{" "}
              <code className="rounded bg-muted px-1">http://127.0.0.1:1234</code>).
            </li>
            <li>
              In OpenManus <code className="rounded bg-muted px-1">config/config.toml</code>, set{" "}
              <code className="rounded bg-muted px-1">api_type = \"openai\"</code> and point to LM Studio base URL.
            </li>
            <li>Use Settings page probes (Glom On) to verify `/v1/models` reachability.</li>
          </ol>
          <div className="flex flex-wrap gap-3">
            <a
              href="https://lmstudio.ai/docs/app/api/endpoints/openai"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
            >
              LM Studio API docs <ExternalLink className="h-3.5 w-3.5" />
            </a>
            <a
              href="https://lmstudio.ai"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline"
            >
              Download LM Studio <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Documentation</CardTitle>
          <CardDescription>Select a markdown file</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="doc-select">Document</Label>
            <select
              id="doc-select"
              value={doc}
              onChange={(e) => setDoc(e.target.value)}
              className="flex h-10 w-full max-w-xs rounded-md border border-input bg-background/80 px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {docs.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : err ? (
            <p className="text-sm text-destructive">{err}</p>
          ) : (
            <pre className="max-h-[min(70vh,640px)] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border/60 bg-muted/20 p-4 font-mono text-xs leading-relaxed text-muted-foreground">
              {text}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

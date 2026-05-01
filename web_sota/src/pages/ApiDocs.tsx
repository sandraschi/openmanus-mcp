import { useState } from "react";
import { Code2, BookOpen, ExternalLink } from "lucide-react";

const BACKEND = "";

export default function ApiDocsPage() {
  const [view, setView] = useState<"swagger" | "redoc">("swagger");
  const src = view === "swagger" ? `${BACKEND}/docs` : `${BACKEND}/redoc`;

  const endpoints = [
    "GET /api/v1/health",
    "GET /api/v1/status",
    "GET /api/v1/mcp/tools",
    "GET /api/v1/docs",
    "GET /api/v1/glama",
    "GET /api/v1/capabilities",
    "GET /api/settings",
    "PUT /api/settings",
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">API Docs</h1>
          <p className="text-sm text-muted-foreground">FastAPI auto-generated documentation</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setView("swagger")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              view === "swagger"
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            Swagger UI
          </button>
          <button
            onClick={() => setView("redoc")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              view === "redoc"
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            ReDoc
          </button>
          <a
            href={`${BACKEND}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Open in browser
          </a>
        </div>
      </div>

      <div className="rounded-xl border border-border/60 bg-card/40 backdrop-blur-md overflow-hidden">
        <div className="flex gap-2 px-4 py-2 border-b border-border/60 overflow-x-auto">
          {endpoints.map((ep) => (
            <span key={ep} className="text-xs font-mono text-muted-foreground bg-muted/50 px-2 py-1 rounded whitespace-nowrap">
              {ep}
            </span>
          ))}
        </div>
        <div className="w-full h-[600px]">
          <iframe
            src={src}
            className="w-full h-full border-0"
            title="API Documentation"
            sandbox="allow-scripts allow-same-origin"
          />
        </div>
      </div>
    </div>
  );
}

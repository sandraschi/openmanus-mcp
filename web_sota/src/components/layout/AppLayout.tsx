import * as React from "react";
import {
  Activity,
  Box,
  CircleHelp,
  Code2,
  Home,
  Layers,
  LayoutGrid,
  Menu,
  MessageSquare,
  PlayCircle,
  Settings as SettingsIcon,
  Terminal,
  X,
} from "lucide-react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { LoggerPanel } from "@/components/LoggerPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { Button } from "@/components/ui/button";
import { useLogger } from "@/contexts/LoggerContext";
import { cn } from "@/lib/utils";

type Health = { ok: boolean; service: string; version: string };

const PATH_TITLE: Record<string, string> = {
  "/": "Home",
  "/tools": "Tools",
  "/apps": "Apps",
  "/help": "Help",
  "/settings": "Settings",
  "/run": "Run",
  "/fleet": "Fleet",
  "/status": "Status",
  "/chat": "Chat",
  "/api-docs": "API Docs",
};

const coreNav: { to: string; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { to: "/", label: "Home", icon: Home },
  { to: "/tools", label: "Tools", icon: Terminal },
  { to: "/apps", label: "Apps", icon: LayoutGrid },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
  { to: "/help", label: "Help", icon: CircleHelp },
  { to: "/status", label: "Status", icon: Activity },
];

const projectNav: { to: string; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { to: "/run", label: "Run", icon: PlayCircle },
  { to: "/fleet", label: "Fleet", icon: Layers },
  { to: "/api-docs", label: "API Docs", icon: Code2 },
];

function SidebarNav({
  collapsed,
  onNavigate,
}: {
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const { appendLog } = useLogger();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
      isActive ? "bg-secondary text-secondary-foreground" : "hover:bg-accent/60 hover:text-accent-foreground",
      collapsed && "justify-center px-2",
    );

  const Item = ({ to, label, icon: Icon }: (typeof coreNav)[0]) => (
    <NavLink
      to={to}
      end={to === "/"}
      onClick={() => {
        onNavigate?.();
        appendLog("DEBUG", `nav → ${label}`);
      }}
      className={linkClass}
    >
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span>{label}</span>}
    </NavLink>
  );

  return (
    <>
      <div className="space-y-1">
        {coreNav.map((n) => (
          <Item key={n.to} {...n} />
        ))}
      </div>
      <div className="my-4 border-t border-border/50" />
      <div className="space-y-1">
        {!collapsed && <div className="px-3 pb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Project</div>}
        {projectNav.map((n) => (
          <Item key={n.to} {...n} />
        ))}
      </div>
    </>
  );
}

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [chatOpen, setChatOpen] = React.useState(false);
  const [health, setHealth] = React.useState<Health | null>(null);
  const { logs, clearLogs } = useLogger();
  const location = useLocation();
  const pageTitle = PATH_TITLE[location.pathname] ?? "Page";

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setChatOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  React.useEffect(() => {
    let c = false;
    void (async () => {
      try {
        const r = await fetch("/api/v1/health");
        const h = (await r.json()) as Health;
        if (!c) setHealth(h);
      } catch {
        if (!c) setHealth(null);
      }
    })();
    return () => {
      c = true;
    };
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-background font-sans selection:bg-accent selection:text-accent-foreground md:flex-row">
      {/* Desktop sidebar */}
      <aside
        className={cn(
          "sticky top-0 z-40 hidden h-screen shrink-0 flex-col border-r border-border/80 bg-card/50 backdrop-blur-xl transition-all duration-300 md:flex",
          sidebarOpen ? "w-64" : "w-20",
        )}
      >
        <div className="flex h-16 items-center border-b border-border/80 px-4">
          <NavLink to="/" className="flex items-center gap-2 font-bold tracking-tight" end>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Box className="h-5 w-5 text-primary-foreground" />
            </div>
            {sidebarOpen && (
              <span className="bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-lg text-transparent">
                openmanus-mcp
              </span>
            )}
          </NavLink>
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-6">
          <SidebarNav collapsed={!sidebarOpen} />
        </div>
        <div className="border-t border-border/80 p-3">
          <Button variant="ghost" className="w-full" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle sidebar">
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          {sidebarOpen && <p className="mt-2 text-center text-xs text-muted-foreground">Iron Shell · 10769</p>}
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen ? (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            aria-label="Close menu"
            onClick={() => setMobileOpen(false)}
          />
          <div className="absolute left-0 top-0 flex h-full w-72 flex-col border-r border-border/80 bg-card shadow-xl">
            <div className="flex h-14 items-center justify-between border-b border-border/80 px-4">
              <span className="font-semibold">Menu</span>
              <Button variant="ghost" size="icon" onClick={() => setMobileOpen(false)} aria-label="Close">
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto px-3 py-4">
              <SidebarNav collapsed={false} onNavigate={() => setMobileOpen(false)} />
            </div>
          </div>
        </div>
      ) : null}

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-50 flex h-16 shrink-0 items-center gap-3 border-b border-border/80 bg-background/85 px-4 shadow-sm backdrop-blur-md md:px-6">
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileOpen(true)} aria-label="Open menu">
            <Menu className="h-5 w-5" />
          </Button>
          <span className="text-sm text-muted-foreground">Home</span>
          <span className="text-muted-foreground">/</span>
          <span className="font-semibold">{pageTitle}</span>
          <span className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
            <Activity className="h-3.5 w-3.5" />
            API {health?.ok ? <span className="text-emerald-400">●</span> : <span className="text-red-400">●</span>}
            {health?.version ?? "…"}
          </span>
          <Button variant="outline" size="sm" className="ml-2 hidden md:inline-flex" onClick={() => setChatOpen(true)}>
            <MessageSquare className="mr-2 h-4 w-4" /> Chat
          </Button>
        </header>

        <main className="min-h-0 flex-1 overflow-y-auto p-4 md:p-8">
          <Outlet />
        </main>

        <LoggerPanel logs={logs} onClear={clearLogs} />
      </div>
      <button
        type="button"
        className="fixed bottom-20 right-6 z-50 inline-flex h-12 w-12 items-center justify-center rounded-full border border-border bg-primary text-primary-foreground shadow-lg md:hidden"
        onClick={() => setChatOpen(true)}
        aria-label="Open chat"
      >
        <MessageSquare className="h-5 w-5" />
      </button>
      <ChatPanel open={chatOpen} onOpenChange={setChatOpen} />
    </div>
  );
}

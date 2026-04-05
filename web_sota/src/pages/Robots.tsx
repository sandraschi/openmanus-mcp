import { Bot, Cpu, ExternalLink, Info, Loader2, RefreshCcw, Wifi } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type Robot = {
  id: string;
  name: string;
  type: string;
  status: "online" | "offline" | "busy";
  battery?: number;
  last_seen?: string;
};

export default function RobotsPage() {
  const [robots, setRobots] = useState<Robot[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRobots = useCallback(async () => {
    setLoading(true);
    // Mocking for now as the robotics-mcp integration is ALPHA/Planned
    setTimeout(() => {
      setRobots([
        { id: "raspbot-01", name: "Raspbot v2", type: "Yahboom", status: "online", battery: 82, last_seen: "Just now" },
        { id: "go2-01", name: "Go2-Alpha", type: "Unitree", status: "offline", last_seen: "2h ago" },
      ]);
      setLoading(false);
    }, 800);
  }, []);

  useEffect(() => {
    void loadRobots();
  }, [loadRobots]);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Bot className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">My Robots</h1>
          </div>
          <p className="text-muted-foreground">
            Control and monitor your physical hardware fleet via MCP bridge.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void loadRobots()} disabled={loading}>
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCcw className="mr-2 h-4 w-4" />}
          Refresh Fleet
        </Button>
      </header>

      <Alert className="border-primary/20 bg-primary/5">
        <Info className="h-4 w-4 text-primary" />
        <AlertTitle>Hardware Bridge Alpha</AlertTitle>
        <AlertDescription>
          Robotics integration is currently in <strong>Alpha</strong>. This page monitors local units discovered via 
          <code className="mx-1 rounded bg-muted px-1 text-xs">yahboom-mcp</code> and <code className="mx-1 rounded bg-muted px-1 text-xs">unitree-mcp</code>.
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="animate-pulse border-border/40 bg-card/40">
              <CardHeader className="h-24" />
              <CardContent className="h-32" />
            </Card>
          ))
        ) : robots.length > 0 ? (
          robots.map((robot) => (
            <Card key={robot.id} className="group relative overflow-hidden border-border/60 bg-card/60 backdrop-blur-xl transition-all hover:border-primary/40 hover:shadow-lg">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <Badge variant={robot.status === "online" ? "default" : "secondary"} className={robot.status === "online" ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20" : ""}>
                    <Wifi className="mr-1 h-3 w-3" />
                    {robot.status.toUpperCase()}
                  </Badge>
                  {robot.battery !== undefined && (
                    <span className="text-xs font-medium text-muted-foreground">{robot.battery}% Battery</span>
                  )}
                </div>
                <CardTitle className="mt-2 text-xl">{robot.name}</CardTitle>
                <CardDescription className="flex items-center gap-1">
                  <Cpu className="h-3 w-3" /> {robot.type} Platform
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">ID</span>
                    <code className="text-xs font-semibold">{robot.id}</code>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Seen</span>
                    <span className="font-medium">{robot.last_seen}</span>
                  </div>
                  <Button className="mt-2 w-full" variant="outline" size="sm" disabled={robot.status !== "online"}>
                    Open Control Bridge
                  </Button>
                </div>
              </CardContent>
              {/* Subtle accent gradient */}
              <div className="absolute -right-4 -top-4 h-24 w-24 bg-primary/5 blur-3xl transition-colors group-hover:bg-primary/10" />
            </Card>
          ))
        ) : (
          <div className="col-span-full py-20 text-center">
            <p className="text-muted-foreground">No hardware units discovered in the local network.</p>
          </div>
        )}

        <Card className="flex flex-col items-center justify-center border-dashed border-border/80 bg-transparent py-10 transition-colors hover:bg-muted/30 sm:py-0">
          <Bot className="mb-2 h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm font-medium text-muted-foreground">Add New Unit</p>
          <Button variant="link" size="sm" className="text-xs">
            View Setup Guide <ExternalLink className="ml-1 h-3 w-3" />
          </Button>
        </Card>
      </div>
    </div>
  );
}

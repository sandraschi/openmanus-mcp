import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Cpu, HardDrive, Monitor, Container } from "lucide-react";
import { useLogger } from "@/contexts/LoggerContext";

type SystemInfo = {
  cpu: number;
  memory: { total: number; used: number; percent: number };
  platform: string;
  gpu?: string;
};

function LogLine({ timestamp, level, message }: { timestamp: string; level: string; message: string }) {
  const levelColors: Record<string, string> = {
    DEBUG: "text-zinc-500",
    INFO: "text-blue-400",
    "SOTA-WARN": "text-yellow-400",
    ERROR: "text-red-400",
  };
  return (
    <div className="flex gap-2 text-xs font-mono leading-5">
      <span className="text-zinc-500 w-20 flex-shrink-0">{timestamp}</span>
      <span className={`w-20 flex-shrink-0 ${levelColors[level] || "text-zinc-400"}`}>
        [{level}]
      </span>
      <span className="text-zinc-300">{message}</span>
    </div>
  );
}

export default function StatusAuditPage() {
  const { logs } = useLogger();
  const [sysInfo, setSysInfo] = useState<SystemInfo | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch("/api/v1/system");
        const j = await r.json();
        setSysInfo(j as SystemInfo);
      } catch {}
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (autoScroll && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleScroll = () => {
    if (!logRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = logRef.current;
    setAutoScroll(scrollHeight - scrollTop - clientHeight < 30);
  };

  const StatCard = ({ icon: Icon, label, value, bar }: { icon: any; label: string; value: string; bar?: number }) => (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-border/60 bg-card/40 p-4 backdrop-blur-md"
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 text-primary" />
        <span className="text-xs text-muted-foreground uppercase">{label}</span>
      </div>
      <div className="text-2xl font-semibold">{value}</div>
      {bar !== undefined && (
        <div className="mt-2 h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${bar > 80 ? "bg-red-500" : "bg-primary"}`}
            style={{ width: `${bar}%` }}
          />
        </div>
      )}
    </motion.div>
  );

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Status & Audit</h1>
        <p className="mt-2 text-sm text-muted-foreground">System resources and live event log</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Cpu} label="CPU" value={`${sysInfo?.cpu ?? "?"}%`} bar={sysInfo?.cpu} />
        <StatCard icon={HardDrive} label="Memory" value={`${sysInfo?.memory?.percent ?? "?"}%`} bar={sysInfo?.memory?.percent} />
        <StatCard icon={Monitor} label="Platform" value={sysInfo?.platform ?? "?"} />
        <StatCard icon={Container} label="GPU" value={sysInfo?.gpu && sysInfo.gpu.length > 35 ? sysInfo.gpu.slice(0, 35) + "..." : sysInfo?.gpu ?? "?"} />
      </div>

      <div className="rounded-xl border border-border/60 bg-card/40 backdrop-blur-md overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-border/60">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-semibold">Live Log</span>
            <span className="text-xs text-muted-foreground">{logs.length} entries</span>
          </div>
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`text-xs px-2 py-1 rounded transition-colors ${
              autoScroll ? "bg-primary/10 text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {autoScroll ? "Auto-scroll ON" : "Auto-scroll OFF"}
          </button>
        </div>
        <div ref={logRef} onScroll={handleScroll} className="overflow-auto p-3 space-y-0.5 max-h-[400px]">
          {logs.length === 0 ? (
            <p className="text-xs text-muted-foreground italic">No log entries yet</p>
          ) : (
            logs.map((entry: any, i: number) => (
              <LogLine key={i} timestamp={entry.timestamp || ""} level={entry.level || "INFO"} message={entry.message || ""} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

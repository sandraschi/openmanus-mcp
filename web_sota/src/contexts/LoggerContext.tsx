import * as React from "react";

import type { LogLine } from "@/components/LoggerPanel";

type LoggerCtx = {
  logs: LogLine[];
  appendLog: (level: string, msg: string) => void;
  clearLogs: () => void;
};

const LoggerContext = React.createContext<LoggerCtx | null>(null);

export function LoggerProvider({ children }: { children: React.ReactNode }) {
  const [logs, setLogs] = React.useState<LogLine[]>([]);

  const appendLog = React.useCallback((level: string, msg: string) => {
    const ts = new Date().toISOString().replace("T", " ").slice(0, 23);
    setLogs((prev) => [...prev.slice(-500), { ts, level, msg }]);
  }, []);

  const clearLogs = React.useCallback(() => setLogs([]), []);

  const value = React.useMemo(() => ({ logs, appendLog, clearLogs }), [logs, appendLog, clearLogs]);

  return <LoggerContext.Provider value={value}>{children}</LoggerContext.Provider>;
}

export function useLogger() {
  const ctx = React.useContext(LoggerContext);
  if (!ctx) throw new Error("useLogger must be used within LoggerProvider");
  return ctx;
}

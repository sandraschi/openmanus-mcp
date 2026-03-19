import { ChevronDown, ChevronUp, Terminal } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type LogLine = { ts: string; level: string; msg: string };

function levelClass(level: string): string {
  if (level === "ERROR") return "text-red-300";
  if (level === "WARN" || level === "SOTA-WARN") return "text-amber-300";
  if (level === "DEBUG") return "text-slate-400";
  return "text-foreground";
}

/** Sticky logger: auto-scroll unless user scrolls up (WEBAPP_STANDARDS §6.3). */
export function LoggerPanel({
  logs,
  onClear,
}: {
  logs: LogLine[];
  onClear?: () => void;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState(true);
  const [userPaused, setUserPaused] = useState(false);

  useEffect(() => {
    if (!expanded || userPaused) return;
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs, expanded, userPaused]);

  const onScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 48;
    setUserPaused(!nearBottom);
  };

  return (
    <div className="z-40 shrink-0 border-t border-border/80 bg-card/70 backdrop-blur-xl transition-colors">
      <div className="flex items-center gap-2 border-b border-border/60 px-3 py-2 md:px-4">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="flex flex-1 items-center gap-2 text-left text-sm text-muted-foreground hover:text-foreground"
        >
          <Terminal className="h-4 w-4 shrink-0" />
          <span>Logger</span>
          {userPaused ? <span className="text-amber-400/90">(auto-scroll paused)</span> : null}
          {expanded ? (
            <ChevronDown className="ml-auto h-4 w-4 shrink-0" />
          ) : (
            <ChevronUp className="ml-auto h-4 w-4 shrink-0" />
          )}
        </button>
        {onClear ? (
          <Button type="button" variant="outline" size="sm" className="h-8 text-xs" onClick={() => onClear()}>
            Clear
          </Button>
        ) : null}
      </div>
      {expanded ? (
        <div
          ref={scrollRef}
          onScroll={onScroll}
          className="max-h-[200px] overflow-y-auto px-3 py-2 pb-3 font-mono text-xs leading-relaxed md:px-4"
        >
          {logs.length === 0 ? (
            <div className="text-muted-foreground">No events yet. Run a prompt, use Fleet, or open Tools.</div>
          ) : (
            logs.map((l, i) => (
              <div key={i} className={cn("mb-1.5", levelClass(l.level))}>
                <span className="opacity-55">{l.ts}</span> <span className="font-semibold">{l.level}</span> {l.msg}
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
      ) : null}
    </div>
  );
}

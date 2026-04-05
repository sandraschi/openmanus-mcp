import { History, Loader2, Play, Rocket, Star } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { AutoResizeTextarea } from "@/components/AutoResizeTextarea";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogger } from "@/contexts/LoggerContext";

const MAX_RUN_SKILL_IDS = 8;

type Status = {
  openmanus_valid: boolean;
  openmanus_root: string | null;
  runner_timeout_s: number;
  job_store_max_completed?: number;
  async_jobs_pending?: number;
};

type CatalogSkill = {
  id: string;
  name: string;
  description: string;
  location: string;
  source: string;
};

type PromptPreset = {
  id: string;
  title: string;
  category: "onboarding" | "research" | "automation" | "debug";
  prompt: string;
  entryPoint: "main.py" | "run_flow.py";
};

type Activity = {
  id: string;
  title: string;
  outcome: string;
  category: "build" | "ops" | "research" | "debug" | "comms" | "robots" | "media";
  entryPoint: "main.py" | "run_flow.py";
  prompt: string;
  estMin: number;
};

type PromptHistoryItem = {
  id: string;
  prompt: string;
  entryPoint: "main.py" | "run_flow.py";
  favorite: boolean;
  uses: number;
  lastUsedAt: string;
  source: "preset" | "custom";
  title: string;
};

const HISTORY_KEY = "openmanus-run-history-v1";
const HISTORY_MAX = 50;

const PRESETS: PromptPreset[] = [
  {
    id: "first-task-map",
    title: "First run: task map + next steps",
    category: "onboarding",
    entryPoint: "main.py",
    prompt:
      "I am new here. Inspect the current project context and produce: 1) what this project does, 2) top 5 practical things I can do with it this week, 3) a prioritized step-by-step plan.",
  },
  {
    id: "bug-repro-min",
    title: "Repro + minimal fix proposal",
    category: "debug",
    entryPoint: "main.py",
    prompt:
      "Given a failing behavior, produce a concise repro plan, likely root causes ranked by probability, and the smallest safe fix to try first.",
  },
  {
    id: "mcp-integration-audit",
    title: "MCP integration audit",
    category: "research",
    entryPoint: "main.py",
    prompt:
      "Audit my MCP integration quality. List missing capabilities, broken paths, and concrete next implementation tasks with acceptance criteria.",
  },
  {
    id: "ops-weekly-review",
    title: "Weekly ops review draft",
    category: "automation",
    entryPoint: "main.py",
    prompt:
      "Prepare a weekly engineering review template with sections for incidents, delivery status, quality metrics, and top priorities for next week.",
  },
  {
    id: "docs-gap-analysis",
    title: "Docs gap analysis",
    category: "research",
    entryPoint: "main.py",
    prompt:
      "Analyze current documentation quality and output missing docs sections, stale content risks, and exact files that should be updated first.",
  },
  {
    id: "workflow-multistep",
    title: "Multi-agent workflow attempt",
    category: "automation",
    entryPoint: "run_flow.py",
    prompt:
      "Use run flow to propose a multi-step plan for feature delivery with risks, milestones, and a test strategy.",
  },
];

const ACTIVITIES: Activity[] = [
  {
    id: "activity-release-notes",
    title: "Release Notes Draft",
    outcome: "A concise changelog-style draft based on current repo context.",
    category: "ops",
    entryPoint: "main.py",
    estMin: 5,
    prompt:
      "Create draft release notes in markdown with sections: highlights, fixes, risks, and test notes. Keep it practical and concise.",
  },
  {
    id: "activity-qa-checklist",
    title: "QA Smoke Checklist",
    outcome: "A runnable validation checklist for current feature state.",
    category: "build",
    entryPoint: "main.py",
    estMin: 6,
    prompt:
      "Generate a smoke-test checklist for this project: API, UI, config, error paths, and regression checks. Include pass/fail criteria.",
  },
  {
    id: "activity-root-cause",
    title: "Root Cause Triage",
    outcome: "Top likely causes and the first safe fix path.",
    category: "debug",
    entryPoint: "main.py",
    estMin: 8,
    prompt:
      "Given a failing behavior, provide top 3 likely root causes and a minimal risk-first fix sequence with verification steps.",
  },
  {
    id: "activity-roadmap-sprint",
    title: "Sprint Roadmap Draft",
    outcome: "Prioritized next-sprint plan with sequencing and risk tags.",
    category: "research",
    entryPoint: "run_flow.py",
    estMin: 10,
    prompt:
      "Draft a one-sprint roadmap for this repo with themes, milestones, dependencies, and risk labels. Keep it execution-ready.",
  },
];

function loadHistory(): PromptHistoryItem[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as PromptHistoryItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveHistory(items: PromptHistoryItem[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, HISTORY_MAX)));
}

export default function RunPage() {
  const { appendLog } = useLogger();
  const [prompt, setPrompt] = useState("");
  const [entryPoint, setEntryPoint] = useState("main.py");
  const [selectedPreset, setSelectedPreset] = useState(PRESETS[0]?.id ?? "");
  const [activityFilter, setActivityFilter] = useState<"all" | Activity["category"]>("all");
  const [history, setHistory] = useState<PromptHistoryItem[]>([]);
  const [timeoutStr, setTimeoutStr] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [busy, setBusy] = useState<"sync" | "async" | "poll" | null>(null);
  const [resultJson, setResultJson] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [catalogSkills, setCatalogSkills] = useState<CatalogSkill[]>([]);
  const [skillsLoadError, setSkillsLoadError] = useState<string | null>(null);
  const [runSkillIds, setRunSkillIds] = useState<string[]>([]);
  const [appendingSkills, setAppendingSkills] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const r = await fetch("/api/v1/status");
      const data = (await r.json()) as Status;
      setStatus(data);
    } catch (e) {
      appendLog("ERROR", `status fetch: ${String(e)}`);
    }
  }, [appendLog]);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  useEffect(() => {
    let c = false;
    void (async () => {
      try {
        const r = await fetch("/api/v1/skills");
        const data = (await r.json()) as { skills?: CatalogSkill[] };
        if (!c && Array.isArray(data.skills)) {
          setCatalogSkills(data.skills);
          setSkillsLoadError(null);
        }
      } catch (e) {
        if (!c) setSkillsLoadError(String(e));
      }
    })();
    return () => {
      c = true;
    };
  }, []);

  useEffect(() => {
    setHistory(loadHistory());
  }, []);

  const upsertHistory = useCallback(
    (source: "preset" | "custom", title: string) => {
      const p = prompt.trim();
      if (!p) return;
      setHistory((prev) => {
        const idx = prev.findIndex((h) => h.prompt === p && h.entryPoint === entryPoint);
        const now = new Date().toISOString();
        let next = [...prev];
        if (idx >= 0) {
          next[idx] = {
            ...next[idx],
            uses: next[idx].uses + 1,
            lastUsedAt: now,
            source,
            title,
          };
        } else {
          next.unshift({
            id: crypto.randomUUID(),
            prompt: p,
            entryPoint: entryPoint as "main.py" | "run_flow.py",
            favorite: false,
            uses: 1,
            lastUsedAt: now,
            source,
            title,
          });
        }
        next = next
          .sort((a, b) => Number(b.favorite) - Number(a.favorite) || b.lastUsedAt.localeCompare(a.lastUsedAt))
          .slice(0, HISTORY_MAX);
        saveHistory(next);
        return next;
      });
    },
    [entryPoint, prompt],
  );

  const bodyPayload = () => {
    const timeout_s = timeoutStr.trim() === "" ? null : Number.parseFloat(timeoutStr);
    const t = Number.isFinite(timeout_s as number) ? timeout_s : null;
    const ids = runSkillIds.slice(0, MAX_RUN_SKILL_IDS);
    return {
      prompt: prompt.trim(),
      entry_point: entryPoint,
      ...(ids.length > 0 ? { skill_ids: ids } : {}),
      ...(t != null ? { timeout_s: t } : {}),
    };
  };

  const toggleRunSkill = (id: string) => {
    setRunSkillIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_RUN_SKILL_IDS) {
        appendLog("SOTA-WARN", `At most ${MAX_RUN_SKILL_IDS} skills per run.`);
        return prev;
      }
      return [...prev, id];
    });
  };

  const appendSelectedSkillBodies = async () => {
    if (runSkillIds.length === 0) {
      appendLog("SOTA-WARN", "Select at least one skill to append.");
      return;
    }
    setAppendingSkills(true);
    try {
      const parts: string[] = [];
      for (const id of runSkillIds.slice(0, MAX_RUN_SKILL_IDS)) {
        const r = await fetch(`/api/v1/skills/${encodeURIComponent(id)}`);
        if (!r.ok) {
          appendLog("ERROR", `skills/${id}: HTTP ${r.status}`);
          continue;
        }
        const j = (await r.json()) as { body?: string };
        if (j.body) parts.push(`<!-- skill: ${id} -->\n${j.body.trim()}`);
      }
      if (parts.length === 0) return;
      const block = parts.join("\n\n---\n\n");
      setPrompt((p) => (p.trim() ? `${p.trim()}\n\n---\n\n${block}` : block));
      appendLog("INFO", `Appended ${parts.length} SKILL.md body(ies) to prompt (client-side).`);
    } catch (e) {
      appendLog("ERROR", String(e));
    } finally {
      setAppendingSkills(false);
    }
  };

  const runSync = async () => {
    if (!prompt.trim()) {
      appendLog("SOTA-WARN", "Prompt is empty.");
      return;
    }
    setBusy("sync");
    setResultJson(null);
    const fromPreset = PRESETS.find((p) => p.prompt === prompt.trim() && p.entryPoint === entryPoint);
    upsertHistory(fromPreset ? "preset" : "custom", fromPreset?.title ?? "Custom prompt");
    appendLog("INFO", `POST /api/v1/run (${entryPoint})`);
    try {
      const r = await fetch("/api/v1/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyPayload()),
      });
      const data = await r.json();
      setResultJson(JSON.stringify(data, null, 2));
      if (data.success) appendLog("INFO", "Run complete (exit success).");
      else appendLog("SOTA-WARN", data.message || "Run finished with success=false.");
    } catch (e) {
      appendLog("ERROR", String(e));
      setResultJson(String(e));
    } finally {
      setBusy(null);
      void loadStatus();
    }
  };

  const runAsync = async () => {
    if (!prompt.trim()) {
      appendLog("SOTA-WARN", "Prompt is empty.");
      return;
    }
    setBusy("async");
    setResultJson(null);
    const fromPreset = PRESETS.find((p) => p.prompt === prompt.trim() && p.entryPoint === entryPoint);
    upsertHistory(fromPreset ? "preset" : "custom", fromPreset?.title ?? "Custom prompt");
    appendLog("INFO", "POST /api/v1/run/async");
    try {
      const r = await fetch("/api/v1/run/async", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyPayload()),
      });
      const data = await r.json();
      if (!data.success || !data.job_id) {
        appendLog("ERROR", data.message || "async queue failed");
        setResultJson(JSON.stringify(data, null, 2));
        setBusy(null);
        return;
      }
      setJobId(data.job_id);
      appendLog("INFO", `job_id=${data.job_id} — polling…`);
      setBusy("poll");
      const id = data.job_id as string;
      const poll = async () => {
        for (let i = 0; i < 600; i++) {
          await new Promise((r0) => setTimeout(r0, 500));
          const pr = await fetch(`/api/v1/run/jobs/${encodeURIComponent(id)}`);
          const pj = await pr.json();
          if (pj.status === "complete") {
            setResultJson(JSON.stringify(pj, null, 2));
            appendLog("INFO", "Async job complete.");
            setBusy(null);
            void loadStatus();
            return;
          }
          if (pj.status === "not_found") {
            appendLog("ERROR", "Job lost (not_found).");
            setBusy(null);
            return;
          }
        }
        appendLog("SOTA-WARN", "Poll stopped after 5 minutes.");
        setBusy(null);
      };
      void poll();
    } catch (e) {
      appendLog("ERROR", String(e));
      setBusy(null);
    }
  };

  const applyPreset = () => {
    const p = PRESETS.find((x) => x.id === selectedPreset);
    if (!p) return;
    setPrompt(p.prompt);
    setEntryPoint(p.entryPoint);
    appendLog("INFO", `preset loaded: ${p.title}`);
  };

  const toggleFavorite = (id: string) => {
    setHistory((prev) => {
      const next = prev.map((h) => (h.id === id ? { ...h, favorite: !h.favorite } : h));
      saveHistory(next);
      return next;
    });
  };

  const applyActivity = (a: Activity) => {
    setPrompt(a.prompt);
    setEntryPoint(a.entryPoint);
    setSelectedPreset("");
    appendLog("INFO", `activity loaded: ${a.title}`);
  };

  const visibleActivities = ACTIVITIES.filter((a) => activityFilter === "all" || a.category === activityFilter);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Run OpenManus</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          <code className="rounded bg-muted px-1">POST /api/v1/run</code> (sync) or{" "}
          <code className="rounded bg-muted px-1">/api/v1/run/async</code> (optional <strong>skill_ids</strong>). Requires{" "}
          <strong>OPENMANUS_ROOT</strong> on the API. Supervisor:{" "}
          <code className="rounded bg-muted px-1">/api/v1/supervisor/heartbeat</code> · schedules under{" "}
          <code className="rounded bg-muted px-1">/api/v1/supervisor/schedules</code> (enable with{" "}
          <code className="rounded bg-muted px-1">OPENMANUS_SUPERVISOR_ENABLED=true</code>). Stdio MCP:{" "}
          <code className="rounded bg-muted px-1">openmanus_bridge</code>.
        </p>
      </header>

      {status ? (
        <div
          className={`rounded-lg border px-4 py-3 text-sm ${
            status.openmanus_valid ? "border-emerald-500/40 bg-emerald-500/5" : "border-destructive/40 bg-destructive/5"
          }`}
        >
          <strong>OpenManus:</strong> {status.openmanus_valid ? "path OK" : "not configured or invalid"}{" "}
          {status.openmanus_root ? (
            <span className="text-muted-foreground">
              — <code className="text-xs">{status.openmanus_root}</code>
            </span>
          ) : null}
          <div className="mt-1 text-xs text-muted-foreground">
            Default timeout {status.runner_timeout_s}s · job store cap {status.job_store_max_completed ?? "—"} · pending jobs{" "}
            {status.async_jobs_pending ?? 0}
          </div>
        </div>
      ) : null}

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div>
            <p className="text-sm font-medium">Prompt library</p>
            <p className="text-xs text-muted-foreground">Start fast with proven OpenManus/OpenClaw-style activities.</p>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1">
              <Label htmlFor="preset">Example prompt</Label>
              <select
                id="preset"
                value={selectedPreset}
                onChange={(e) => setSelectedPreset(e.target.value)}
                className="flex h-10 min-w-[340px] max-w-[520px] rounded-md border border-input bg-background/80 px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <optgroup label="Onboarding">
                  {PRESETS.filter((p) => p.category === "onboarding").map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Research">
                  {PRESETS.filter((p) => p.category === "research").map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Automation">
                  {PRESETS.filter((p) => p.category === "automation").map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Debug">
                  {PRESETS.filter((p) => p.category === "debug").map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </optgroup>
              </select>
            </div>
            <Button type="button" variant="secondary" onClick={applyPreset}>
              Use preset
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="space-y-4 pt-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium">Activities</p>
              <p className="text-xs text-muted-foreground">Outcome-oriented starts for users who do not know what to ask yet.</p>
            </div>
            <select
              value={activityFilter}
              onChange={(e) => setActivityFilter(e.target.value as "all" | Activity["category"])}
              className="flex h-9 rounded-md border border-input bg-background/80 px-3 text-sm"
              aria-label="Filter activities"
            >
              <option value="all">All categories</option>
              <option value="build">Build</option>
              <option value="ops">Ops</option>
              <option value="research">Research</option>
              <option value="debug">Debug</option>
              <option value="comms">Comms</option>
              <option value="robots">Robots</option>
              <option value="media">Media</option>
            </select>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {visibleActivities.map((a) => (
              <div key={a.id} className="rounded-md border border-border/60 p-3">
                <div className="text-sm font-medium">{a.title}</div>
                <div className="mt-1 text-xs text-muted-foreground">{a.outcome}</div>
                <div className="mt-2 text-[11px] text-muted-foreground">
                  {a.category} · {a.entryPoint} · ~{a.estMin}m
                </div>
                <Button type="button" size="sm" className="mt-3" variant="secondary" onClick={() => applyActivity(a)}>
                  Use activity
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="space-y-3 pt-6">
          <div>
            <p className="text-sm font-medium">Skills for this run</p>
            <p className="text-xs text-muted-foreground">
              Checked ids are sent as <code className="rounded bg-muted px-1">skill_ids</code> — the API prepends full playbooks server-side (max {MAX_RUN_SKILL_IDS}).{" "}
              <strong>Append to prompt</strong> copies raw <code className="rounded bg-muted px-1">SKILL.md</code> into the box below for editing.
            </p>
          </div>
          {skillsLoadError ? (
            <p className="text-xs text-destructive">Skills catalog: {skillsLoadError}</p>
          ) : catalogSkills.length === 0 ? (
            <p className="text-xs text-muted-foreground">Loading skills…</p>
          ) : (
            <ul className="space-y-2">
              {catalogSkills.map((s) => (
                <li key={s.id} className="flex gap-3 rounded-md border border-border/60 p-2">
                  <input
                    type="checkbox"
                    id={`run-skill-${s.id}`}
                    className="mt-1 h-4 w-4 shrink-0"
                    checked={runSkillIds.includes(s.id)}
                    onChange={() => toggleRunSkill(s.id)}
                  />
                  <label htmlFor={`run-skill-${s.id}`} className="min-w-0 cursor-pointer text-sm">
                    <span className="font-medium">{s.name}</span>{" "}
                    <code className="text-[11px] text-muted-foreground">({s.id})</code>
                    <div className="text-xs text-muted-foreground">{s.description}</div>
                  </label>
                </li>
              ))}
            </ul>
          )}
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" size="sm" disabled={appendingSkills || runSkillIds.length === 0} onClick={() => void appendSelectedSkillBodies()}>
              {appendingSkills ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Append to prompt
            </Button>
            {runSkillIds.length > 0 ? (
              <span className="self-center text-xs text-muted-foreground">
                {runSkillIds.length} selected for <code className="rounded bg-muted px-1">skill_ids</code>
              </span>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <div className="space-y-2">
        <Label htmlFor="prompt">Prompt</Label>
        <AutoResizeTextarea
          id="prompt"
          value={prompt}
          onChange={setPrompt}
          placeholder="Task for the agent (single-line may use main.py --prompt; multiline uses stdin)"
          minRows={4}
        />
      </div>

      <div className="flex flex-wrap items-end gap-4">
        <div className="space-y-2">
          <Label htmlFor="entry">Entry point</Label>
          <select
            id="entry"
            value={entryPoint}
            onChange={(e) => setEntryPoint(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background/80 px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="main.py">main.py</option>
            <option value="run_flow.py">run_flow.py</option>
          </select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="to">Timeout override (s)</Label>
          <Input
            id="to"
            type="text"
            inputMode="decimal"
            value={timeoutStr}
            onChange={(e) => setTimeoutStr(e.target.value)}
            placeholder={`default ${status?.runner_timeout_s ?? 300}`}
            className="w-32"
          />
        </div>
        <Button type="button" disabled={busy !== null} onClick={() => void runSync()} className="gap-2">
          {busy === "sync" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run (sync)
        </Button>
        <Button type="button" variant="outline" disabled={busy !== null} onClick={() => void runAsync()} className="gap-2">
          {busy === "poll" || busy === "async" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Rocket className="h-4 w-4" />}
          Run async
        </Button>
      </div>

      {history.length > 0 ? (
        <Card>
          <CardContent className="space-y-3 pt-6">
            <div className="flex items-center gap-2 text-sm font-medium">
              <History className="h-4 w-4" /> Prompt history
            </div>
            <div className="space-y-2">
              {history.slice(0, 8).map((h) => (
                <div key={h.id} className="flex items-start justify-between gap-3 rounded-md border border-border/60 p-3">
                  <div className="min-w-0">
                    <div className="text-xs text-muted-foreground">
                      {h.title} · {h.entryPoint} · uses {h.uses}
                    </div>
                    <p className="line-clamp-2 text-sm">{h.prompt}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Button
                      type="button"
                      size="icon"
                      variant={h.favorite ? "default" : "outline"}
                      onClick={() => toggleFavorite(h.id)}
                      aria-label="Toggle favorite"
                    >
                      <Star className="h-4 w-4" />
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        setPrompt(h.prompt);
                        setEntryPoint(h.entryPoint);
                      }}
                    >
                      Reuse
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {jobId ? (
        <p className="text-xs text-muted-foreground">
          Last job_id: <code className="rounded bg-muted px-1">{jobId}</code>
        </p>
      ) : null}

      {resultJson ? (
        <Card>
          <CardContent className="pt-6">
            <p className="mb-3 text-sm font-medium">Last response</p>
            <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words font-mono text-xs">{resultJson}</pre>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

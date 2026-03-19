import * as Dialog from "@radix-ui/react-dialog";
import { Loader2, MessageSquare, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Persona = { id: string; label: string; description: string };

type SkillRow = { id: string; name: string; description: string; location: string; source: string };

export function ChatPanel({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [skills, setSkills] = useState<SkillRow[]>([]);
  const [provider, setProvider] = useState<"ollama" | "lmstudio">("ollama");
  const [persona, setPersona] = useState("reductionist");
  const [intent, setIntent] = useState<"chat" | "refine">("chat");
  const [skillsMode, setSkillsMode] = useState<"off" | "index">("index");
  const [skillIds, setSkillIds] = useState<string[]>([]);
  const [prompt, setPrompt] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);

  const loadPersonas = async () => {
    if (personas.length > 0) return;
    try {
      const r = await fetch("/api/v1/chat/personas");
      const j = (await r.json()) as { personas: Persona[] };
      setPersonas(Array.isArray(j.personas) ? j.personas : []);
    } catch {
      setPersonas([
        { id: "reductionist", label: "Reductionist", description: "" },
        { id: "debugger", label: "Debugger", description: "" },
      ]);
    }
  };

  const loadSkills = async () => {
    try {
      const r = await fetch("/api/v1/skills");
      const j = (await r.json()) as { skills: SkillRow[] };
      setSkills(Array.isArray(j.skills) ? j.skills : []);
    } catch {
      setSkills([]);
    }
  };

  const toggleSkill = (id: string) => {
    setSkillIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const run = async () => {
    if (!prompt.trim()) return;
    setBusy(true);
    try {
      const res = await fetch("/api/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider,
          persona,
          intent,
          skills_mode: skillsMode,
          skill_ids: skillIds,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      const out = (await res.json()) as {
        success?: boolean;
        message?: { content?: string };
        error?: string;
      };
      const text =
        out?.message?.content ??
        (out?.error ? `Error: ${out.error}` : null) ??
        JSON.stringify(out, null, 2);
      setReply(text);
    } catch (e) {
      setReply(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        onOpenChange(next);
        if (next) {
          void loadPersonas();
          void loadSkills();
        }
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[95vw] max-w-3xl -translate-x-1/2 -translate-y-1/2 rounded-lg border border-border bg-card p-4 shadow-xl">
          <div className="mb-3 flex items-center justify-between">
            <Dialog.Title className="flex items-center gap-2 text-base font-semibold">
              <MessageSquare className="h-4 w-4" /> SOTA Chat
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="Close chat">
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="mb-3 grid gap-3 md:grid-cols-3">
            <div className="space-y-1 md:col-span-3">
              <Label>OpenClaw-style skills</Label>
              <p className="text-xs text-muted-foreground">
                <strong>Index</strong> adds a compact skill list to the system prompt; check skills below to
                also inject full <code className="rounded bg-muted px-1">SKILL.md</code> (e.g. MCP builder).
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <Label htmlFor="skillsMode" className="sr-only">
                  Skills mode
                </Label>
                <select
                  id="skillsMode"
                  value={skillsMode}
                  onChange={(e) => setSkillsMode(e.target.value as "off" | "index")}
                  className="flex h-10 rounded-md border border-input bg-background/80 px-3 text-sm"
                  disabled={intent === "refine"}
                >
                  <option value="index">skills: compact index (chat)</option>
                  <option value="off">skills: off</option>
                </select>
                {intent === "refine" ? (
                  <span className="text-xs text-muted-foreground">Index skipped in refine mode.</span>
                ) : null}
              </div>
              {skills.length > 0 ? (
                <div className="mt-2 flex max-h-24 flex-wrap gap-2 overflow-y-auto rounded-md border border-border/60 p-2">
                  {skills.map((s) => (
                    <label
                      key={s.id}
                      className="flex cursor-pointer items-center gap-1.5 text-xs"
                    >
                      <input
                        type="checkbox"
                        checked={skillIds.includes(s.id)}
                        onChange={() => toggleSkill(s.id)}
                        className="rounded border-input"
                      />
                      <span title={s.description}>{s.name}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="mt-1 text-xs text-muted-foreground">No skills discovered (bundled + extra dirs).</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="provider">Provider</Label>
              <select
                id="provider"
                value={provider}
                onChange={(e) => setProvider(e.target.value as "ollama" | "lmstudio")}
                className="flex h-10 w-full rounded-md border border-input bg-background/80 px-3 text-sm"
              >
                <option value="ollama">ollama</option>
                <option value="lmstudio">lmstudio</option>
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="persona">Persona</Label>
              <select
                id="persona"
                value={persona}
                onChange={(e) => setPersona(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background/80 px-3 text-sm"
              >
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="intent">Intent</Label>
              <select
                id="intent"
                value={intent}
                onChange={(e) => setIntent(e.target.value as "chat" | "refine")}
                className="flex h-10 w-full rounded-md border border-input bg-background/80 px-3 text-sm"
              >
                <option value="chat">chat</option>
                <option value="refine">refine</option>
              </select>
            </div>
          </div>

          <div className="mb-3 flex gap-2">
            <Input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Ask or paste text to refine..." />
            <Button onClick={() => void run()} disabled={busy}>
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : "Send"}
            </Button>
          </div>

          <pre className="max-h-[45vh] overflow-auto whitespace-pre-wrap break-words rounded-md border border-border/60 bg-muted/20 p-3 text-xs">
            {reply || "No response yet."}
          </pre>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

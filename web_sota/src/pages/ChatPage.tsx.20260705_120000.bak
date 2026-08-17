import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Bot, Cpu, Cloud, Loader2 } from "lucide-react";
import { useLogger } from "@/contexts/LoggerContext";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

const PERSONAS = [
  { id: "reductionist", label: "Reductionist", desc: "Industrial, technically exhaustive" },
  { id: "debugger", label: "Debugger", desc: "Trace-focused, edge cases" },
  { id: "explainer", label: "Explainer", desc: "Architectural patterns & concepts" },
];

export default function ChatPage() {
  const { appendLog } = useLogger();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [persona, setPersona] = useState(PERSONAS[0].id);
  const [provider, setProvider] = useState<"local" | "cloud">("local");
  const [streaming, setStreaming] = useState(false);
  const [ollamaOk, setOllamaOk] = useState<boolean | null>(null);
  const [refined, setRefined] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/v1/ollama")
      .then((r) => r.json())
      .then((d) => setOllamaOk(d.reachable))
      .catch(() => setOllamaOk(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleRefine = async () => {
    if (!input.trim() || !ollamaOk) return;
    try {
      const res = await fetch("http://127.0.0.1:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama3.2:latest",
          prompt: `Rewrite this prompt to be more clear and specific. Return ONLY the rewritten prompt:\n\n${input}`,
          stream: false,
        }),
      });
      const data = await res.json();
      setRefined(data.response?.trim() || null);
    } catch {
      setRefined(null);
    }
  };

  const sendMessage = async () => {
    let finalInput = input;
    if (refined) { finalInput = refined; setRefined(null); }
    if (!finalInput.trim()) return;

    const userMsg: Message = { role: "user", content: finalInput, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);
    const assistantMsg: Message = { role: "assistant", content: "", timestamp: Date.now() };
    setMessages((prev) => [...prev, assistantMsg]);
    appendLog("INFO", `Chat: sent message (persona=${persona}, provider=${provider})`);

    try {
      if (ollamaOk) {
        const res = await fetch("http://127.0.0.1:11434/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model: "llama3.2:latest",
            prompt: `You are a ${persona} assistant. ${finalInput}`,
            stream: false,
          }),
        });
        const data = await res.json();
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { ...updated[updated.length - 1], content: data.response || "(no response)" };
          return updated;
        });
      } else {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { ...updated[updated.length - 1], content: "No local LLM detected. Configure in Settings or start Ollama." };
          return updated;
        });
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: "Error: Could not reach LLM." };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl flex flex-col h-[calc(100vh-10rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Chat</h1>
          <p className="text-sm text-muted-foreground">Context-aware chat with local LLM</p>
        </div>
        <div className="flex items-center gap-2">
          {ollamaOk === true && (
            <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">
              <Cpu className="w-3 h-3" />
              Ollama
            </span>
          )}
          {ollamaOk === false && (
            <span className="flex items-center gap-1 text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded-full">
              <Cloud className="w-3 h-3" />
              No local LLM
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        {PERSONAS.map((p) => (
          <button
            key={p.id}
            onClick={() => setPersona(p.id)}
            className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              persona === p.id
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:text-foreground"
            }`}
            title={p.desc}
          >
            {p.label}
          </button>
        ))}
        <div className="flex-1" />
        <button
          onClick={() => setProvider(provider === "local" ? "cloud" : "local")}
          className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg border transition-colors ${
            provider === "local" ? "border-emerald-500/30 text-emerald-400" : "border-blue-500/30 text-blue-400"
          }`}
        >
          {provider === "local" ? <><Cpu className="w-3 h-3" /> Local</> : <><Cloud className="w-3 h-3" /> Cloud</>}
        </button>
      </div>

      <div className="flex-1 overflow-auto space-y-3 mb-4 px-1">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-16">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Send a message to start chatting</p>
            <p className="text-xs mt-1">Local Ollama will be used if available</p>
          </div>
        )}
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="p-1.5 bg-primary/10 rounded-lg h-fit mt-1">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
              )}
              <div className={`max-w-[70%] rounded-xl px-4 py-2.5 text-sm ${
                msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"
              }`}>
                {msg.content || <span className="italic text-muted-foreground">Streaming...</span>}
              </div>
              {msg.role === "user" && (
                <div className="p-1.5 bg-muted rounded-lg h-fit mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      <div className="flex-shrink-0">
        <AnimatePresence>
          {refined && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="mb-2 p-3 bg-muted/50 border border-border rounded-lg"
            >
              <div className="flex items-center gap-1 text-xs text-muted-foreground mb-1">
                <Sparkles className="w-3 h-3" />
                Refined prompt
              </div>
              <p className="text-sm text-foreground/80">{refined}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex gap-2">
          <button
            onClick={handleRefine}
            disabled={!input.trim() || !ollamaOk}
            className="p-2.5 bg-muted hover:bg-muted/80 rounded-lg transition-colors disabled:opacity-30"
            title="Refine prompt"
            aria-label="Refine prompt"
          >
            <Sparkles className="w-4 h-4" />
          </button>
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder={ollamaOk ? "Ask something..." : "No local LLM detected. Start Ollama..."}
              rows={1}
              className="w-full bg-background border border-input rounded-lg px-4 py-2.5 text-sm resize-none focus:outline-none focus:border-primary/50 transition-colors"
              style={{ maxHeight: "120px" }}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!input.trim() || streaming}
            className="p-2.5 bg-primary hover:brightness-110 rounded-lg transition-colors disabled:opacity-30 text-primary-foreground"
            title="Send"
            aria-label="Send"
          >
            {streaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}

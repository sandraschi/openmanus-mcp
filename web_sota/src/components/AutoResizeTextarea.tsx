import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

const LINE_PX = 22;

type Props = {
  id?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  minRows?: number;
  maxHeightPx?: number;
  className?: string;
};

/** Accordance rule: grow with content, cap height, scroll inside (WEBAPP_STANDARDS §6.1). */
export function AutoResizeTextarea({
  id,
  value,
  onChange,
  placeholder,
  minRows = 3,
  maxHeightPx = 280,
  className,
}: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    const minH = minRows * LINE_PX;
    const h = Math.max(minH, Math.min(el.scrollHeight, maxHeightPx));
    el.style.height = `${h}px`;
  }, [value, minRows, maxHeightPx]);

  return (
    <textarea
      id={id}
      ref={ref}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={minRows}
      className={cn(
        "w-full resize-y overflow-y-auto rounded-md border border-input bg-background/80 px-3.5 py-3 text-sm leading-[22px] text-foreground shadow-none transition-shadow placeholder:text-muted-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-0",
        className,
      )}
      style={{ maxHeight: maxHeightPx }}
    />
  );
}

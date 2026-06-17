import { useState } from "react";
import { ArrowUp } from "lucide-react";

export default function ClarificationBar({ question, onSubmit, disabled }) {
  const [text, setText] = useState("");

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (text.trim() && !disabled) handleSubmit();
    }
  }

  function handleSubmit() {
    if (!text.trim() || disabled) return;
    onSubmit(text.trim());
    setText("");
  }

  return (
    <div className="p-3 sm:p-6 bg-[var(--background)] border-t-2 border-[var(--foreground)]">
      <div className="max-w-3xl mx-auto">
        <p
          className="text-xs text-[var(--muted-foreground)] mb-3 uppercase tracking-widest"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          Clarification needed
        </p>
        <div className="p-4 flex flex-col gap-3 focus-within:ring-1 focus-within:ring-[var(--foreground)]">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Answer the clarification question..."
            disabled={disabled}
            rows={2}
            className="w-full bg-[var(--background)] text-[var(--foreground)] resize-none border-none outline-none placeholder:text-[var(--muted-foreground)]"
            style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: "13px",
            }}
            autoFocus
          />
          <div className="flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={!text.trim() || disabled}
              className={`w-9 h-9 flex items-center justify-center border-none cursor-pointer transition-colors duration-100 ${
                text.trim() && !disabled
                  ? "bg-[var(--foreground)] text-[var(--background)] hover:bg-[var(--muted-foreground)]"
                  : "bg-[var(--border-light)] text-[var(--foreground)] cursor-not-allowed"
              }`}
            >
              <ArrowUp size={18} strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
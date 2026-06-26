import { useState, useRef } from "react";
import { Paperclip, ArrowUp } from "lucide-react";
import FileChip from "./FileChip";

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState("");
  const [files, setFiles] = useState([]);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const canSend = (text.trim().length > 0 || files.length > 0) && !disabled;

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (canSend) handleSend();
    }
  }

  function handleSend() {
    if (!canSend) return;
    onSend(text.trim(), files);
    setText("");
    setFiles([]);
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleFileChange(e) {
    const newFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...newFiles]);
    // Reset input so the same file can be re-added if removed
    e.target.value = "";
  }

  function removeFile(fileToRemove) {
    setFiles((prev) => prev.filter((f) => f !== fileToRemove));
  }

  function handleTextareaInput(e) {
    const textarea = e.target;
    textarea.style.height = "auto";
    const maxHeight = 6 * 24; // approx 6 lines
    textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + "px";
  }

  return (
    <div className="p-3 sm:p-6 bg-[var(--background)] border-t border-[var(--border-light)]">
      <div className="max-w-3xl mx-auto p-4 flex flex-col gap-3 focus-within:ring-1 focus-within:ring-[var(--foreground)]">
        {/* File preview row */}
        {files.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-2 border-b border-[var(--border-light)]">
            {files.map((file, idx) => (
              <FileChip key={`${file.name}-${idx}`} file={file} onRemove={removeFile} />
            ))}
          </div>
        )}

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleTextareaInput}
          placeholder="Ask about a paper, compare methods, or explore a topic..."
          disabled={disabled}
          rows={1}
          className="w-full bg-[var(--background)] text-[var(--foreground)] resize-none border-none outline-none placeholder:text-[var(--muted-foreground)]"
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: "13px",
            maxHeight: `${6 * 24}px`,
          }}
        />

        {/* Bottom row: attach + send */}
        <div className="flex justify-between items-center mt-1">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-transparent border-none cursor-pointer p-1 text-[var(--foreground)] hover:text-[var(--muted-foreground)] transition-colors duration-100"
            aria-label="Attach files"
          >
            <Paperclip size={20} strokeWidth={1.5} />
          </button>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="*/*"
            onChange={handleFileChange}
            className="hidden"
          />

          <button
            id="send-button"
            onClick={handleSend}
            disabled={!canSend}
            className={`w-9 h-9 flex items-center justify-center border-none cursor-pointer transition-colors duration-100 ${
              canSend
                ? "bg-[var(--foreground)] text-[var(--background)] hover:bg-[var(--muted-foreground)]"
                : "bg-[var(--border-light)] text-[var(--foreground)] cursor-not-allowed"
            }`}
            aria-label="Send message"
          >
            <ArrowUp size={18} strokeWidth={1.5} />
          </button>
        </div>
      </div>
    </div>
  );
}

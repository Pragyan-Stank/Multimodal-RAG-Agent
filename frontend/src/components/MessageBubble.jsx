import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Copy, Check } from "lucide-react";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";
  const [copied, setCopied] = useState(false);

  const timestamp = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  function handleCopy() {
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  if (isError) {
    return (
      <div className="flex justify-start">
        <div className="max-w-[75%] border-l-[3px] border-[#E24B4A] p-4">
          <p
            className="text-sm italic text-[var(--muted-foreground)]"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            Error: {message.content}
          </p>
        </div>
      </div>
    );
  }

  if (isUser) {
    return (
      <div className="group flex flex-col items-end">
        <div className="max-w-[60%] border-r-[3px] border-[var(--foreground)] text-[var(--foreground)] p-4">
          {message.files && message.files.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-1">
              {message.files.map((fileName, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 bg-[var(--muted)] border border-[var(--border-light)] text-[var(--muted-foreground)]"
                  style={{ fontFamily: '"JetBrains Mono", monospace' }}
                >
                  {fileName}
                </span>
              ))}
            </div>
          )}
          <p
            className="text-base leading-relaxed whitespace-pre-wrap font-serif text-[var(--foreground)]"
            style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
          >
            {message.content}
          </p>
        </div>
        {timestamp && (
          <span
            className="text-xs text-[var(--muted-foreground)] mt-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            {timestamp}
          </span>
        )}
      </div>
    );
  }

  // Assistant message
  return (
    <div className="group flex flex-col items-start">
      <div className="relative max-w-[75%] bg-[var(--background)] p-4 pr-6 pl-0">
        <div
          className="markdown-content text-base leading-relaxed"
          style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Copy button — appears on hover */}
        {message.content && (
          <button
            onClick={handleCopy}
            className="absolute top-3 right-0 opacity-0 group-hover:opacity-100 transition-opacity duration-150 bg-transparent border-none cursor-pointer p-1 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
            aria-label="Copy message"
          >
            {copied ? (
              <Check size={14} strokeWidth={1.5} />
            ) : (
              <Copy size={14} strokeWidth={1.5} />
            )}
          </button>
        )}
      </div>
      {timestamp && (
        <span
          className="text-xs text-[var(--muted-foreground)] mt-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          {timestamp}
        </span>
      )}
    </div>
  );
}

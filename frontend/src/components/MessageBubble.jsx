import ReactMarkdown from "react-markdown";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";

  const timestamp = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  if (isError) {
    return (
      <div className="flex justify-start">
        <div className="max-w-[75%] border border-[var(--foreground)] p-4">
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
      <div className="flex flex-col items-end">
        <div className="max-w-[65%] bg-[var(--muted)] text-[var(--foreground)] p-4">
          {message.files && message.files.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-1">
              {message.files.map((fileName, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 bg-[var(--background)] border border-[var(--border-light)] text-[var(--muted-foreground)]"
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
            className="text-xs text-[var(--muted-foreground)] mt-1"
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
    <div className="flex flex-col items-start">
      <div className="max-w-[75%] bg-[var(--background)] p-4 pr-6 pl-0">
        <div
          className="markdown-content text-base leading-relaxed"
          style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      </div>
      {timestamp && (
        <span
          className="text-xs text-[var(--muted-foreground)] mt-1"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          {timestamp}
        </span>
      )}
    </div>
  );
}

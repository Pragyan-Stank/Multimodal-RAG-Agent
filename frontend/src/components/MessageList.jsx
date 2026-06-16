import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";

export default function MessageList({ messages, isStreaming }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  if (!messages || messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-8">
        <h2
          className="text-5xl font-bold tracking-tight text-center"
          style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
        >
          Ask anything.
        </h2>
        <p
          className="text-lg text-[var(--muted-foreground)] mt-4 text-center"
          style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
        >
          Upload files, paste URLs, or just type.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 flex flex-col gap-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isStreaming && (
        <div className="flex justify-start">
          <div className="max-w-[75%] bg-[var(--background)] p-4 pr-6 pl-0">
            <div className="flex gap-2 items-center h-6">
              <span className="streaming-dot text-lg leading-none">●</span>
              <span className="streaming-dot text-lg leading-none">●</span>
              <span className="streaming-dot text-lg leading-none">●</span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

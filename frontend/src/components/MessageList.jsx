import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import StepList from "./StepList";

export default function MessageList({ messages, isStreaming, steps }) {
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
          Ask anything research.
        </h2>
        <p
          className="text-lg text-[var(--muted-foreground)] mt-4 text-center"
          style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
        >
          Upload papers, lecture recordings, or ask a research question.
        </p>
      </div>
    );
  }

  // Check if the last assistant message already has content (tokens have arrived)
  const lastMessage = messages[messages.length - 1];
  const hasTokens =
    lastMessage?.role === "assistant" && lastMessage?.content?.length > 0;

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6">
      <div className="max-w-3xl mx-auto flex flex-col gap-8">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Streaming & Step List indicator */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="max-w-[75%] bg-[var(--background)] p-4 pr-6 pl-0 w-full">
              <StepList steps={steps} collapsed={hasTokens} />
              
              {!hasTokens && (
                <div className="flex gap-2 items-center h-6">
                  <div className="streaming-dot" />
                  <div className="streaming-dot" />
                  <div className="streaming-dot" />
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}


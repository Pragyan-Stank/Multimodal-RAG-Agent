export default function ConversationList({
  conversations,
  activeConversationId,
  onSelect,
}) {
  if (!conversations || conversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center px-6">
        <p
          className="text-xs text-[var(--muted-foreground)] text-center"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          No conversations yet
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div
        className="px-6 py-3"
      >
        <span
          className="text-xs tracking-widest text-[var(--muted-foreground)] uppercase"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          Conversations
        </span>
      </div>

      {conversations.map((conv) => {
        const isActive = conv.id === activeConversationId;
        const timestamp = new Date(conv.createdAt).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        });

        return (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`w-full text-left px-6 py-3.5 cursor-pointer transition-colors duration-100 block ${
              isActive
                ? "bg-[var(--muted)] text-[var(--foreground)]"
                : "bg-[var(--background)] text-[var(--foreground)] hover:bg-[var(--muted)]"
            }`}
          >
            <div
              className="text-sm font-medium truncate"
              style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
            >
              {conv.title}
            </div>
            <div
              className="text-xs mt-1 text-[var(--muted-foreground)]"
              style={{ fontFamily: '"JetBrains Mono", monospace' }}
            >
              {timestamp}
            </div>
          </button>
        );
      })}
    </div>
  );
}

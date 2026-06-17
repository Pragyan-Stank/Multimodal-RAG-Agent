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
      {conversations.map((conv) => {
        const isActive = conv.id === activeConversationId;
        const timestamp = new Date(conv.createdAt).toLocaleDateString([], {
          month: "short",
          day: "numeric",
        });

        // Get a snippet from the last message if available
        const lastMessage = conv.messages && conv.messages.length > 0
          ? conv.messages[conv.messages.length - 1]
          : null;
        const snippet = lastMessage?.content
          ? lastMessage.content.substring(0, 30)
          : "";

        return (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`sidebar-item w-full text-left px-6 py-3 cursor-pointer block ${
              isActive
                ? "bg-[var(--muted)] text-[var(--foreground)] border-l-2 border-[var(--foreground)]"
                : "bg-[var(--background)] text-[var(--foreground)] hover:bg-[var(--muted)] border-l-2 border-transparent"
            }`}
          >
            <div
              className="text-sm font-medium truncate"
              style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
            >
              {conv.title}
            </div>
            <div
              className="text-xs mt-1 text-[var(--muted-foreground)] truncate flex items-center gap-1"
              style={{ fontFamily: '"JetBrains Mono", monospace' }}
            >
              <span>{timestamp}</span>
              {snippet && (
                <>
                  <span className="text-[var(--border-light)]">·</span>
                  <span className="truncate opacity-60">{snippet}</span>
                </>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}

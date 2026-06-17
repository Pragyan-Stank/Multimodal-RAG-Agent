import ConversationList from "./ConversationList";
import UserAccountBlock from "./UserAccountBlock";
import { useChat } from "../context/ChatContext";

export default function Sidebar() {
  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    createConversation,
  } = useChat();

  return (
    <div className="w-[var(--sidebar-width)] shrink-0 border-r border-[var(--border-light)] h-screen flex flex-col bg-[var(--background)]">
      {/* App name */}
      <div className="p-6 pb-4">
        <h1
          className="text-lg font-bold tracking-widest uppercase text-[var(--foreground)]"
          style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
        >
          Neutron
        </h1>
      </div>

      {/* Divider */}
      <div className="h-px bg-[var(--border-light)]" />

      {/* New Chat button */}
      <div className="px-4 pt-4 pb-2">
        <button
          id="new-chat-button"
          onClick={createConversation}
          className="w-full bg-transparent text-[var(--foreground)] border border-[var(--border-light)] py-2.5 uppercase tracking-widest cursor-pointer hover:bg-[var(--foreground)] hover:text-[var(--background)] hover:border-[var(--foreground)] transition-colors duration-100"
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: "11px",
          }}
        >
          + New Chat
        </button>
      </div>

      {/* Conversation list */}
      <ConversationList
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelect={setActiveConversationId}
      />

      {/* User account block */}
      <UserAccountBlock />
    </div>
  );
}

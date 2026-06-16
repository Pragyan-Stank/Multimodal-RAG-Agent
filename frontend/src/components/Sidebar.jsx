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
    <div className="w-[280px] shrink-0 border-r border-[var(--border-light)] h-screen flex flex-col bg-[var(--background)]">
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
      <div className="p-4">
        <button
          id="new-chat-button"
          onClick={createConversation}
          className="w-full border border-[var(--border-light)] text-[var(--foreground)] bg-transparent py-2.5 uppercase tracking-widest text-xs font-semibold cursor-pointer hover:bg-[var(--muted)] hover:border-[var(--foreground)] transition-colors duration-100"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
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

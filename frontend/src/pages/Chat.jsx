import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import Sidebar from "../components/Sidebar";
import MessageList from "../components/MessageList";
import InputBar from "../components/InputBar";
import ClarificationBar from "../components/ClarificationBar";
import { useChat } from "../context/ChatContext";
import { uploadFiles, streamMessage, streamClarification } from "../api/chat";

export default function Chat() {
  const {
    activeConversation,
    activeConversationId,
    isStreaming,
    createConversation,
    addMessage,
    updateLastAssistantMessage,
    setThreadId,
    setIsStreaming,
    pendingClarification,
    setPendingClarification,
  } = useChat();

  const [uploadedFilePaths, setUploadedFilePaths] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [statusLabel, setStatusLabel] = useState("");
  const streamedTextRef = useRef("");

  // Shared SSE callbacks builder
  function buildCallbacks(convId) {
    return {
      onToken: (payload) => {
        streamedTextRef.current += payload.content;
        updateLastAssistantMessage(convId, streamedTextRef.current);
      },
      onStatus: (payload) => {
        setStatusLabel(payload.message || "");
      },
      onDone: (payload) => {
        if (payload.thread_id) {
          setThreadId(convId, payload.thread_id);
        }
        setPendingClarification(null);
        setIsStreaming(false);
        setStatusLabel("");
      },
      onError: (payload) => {
        updateLastAssistantMessage(convId, "");
        addMessage(convId, {
          id: uuidv4(),
          role: "error",
          content: payload.message || "Failed to get a response.",
          timestamp: new Date().toISOString(),
        });
        setPendingClarification(null);
        setIsStreaming(false);
        setStatusLabel("");
      },
      onClarification: (payload) => {
        if (payload.thread_id) {
          setThreadId(convId, payload.thread_id);
        }
        // Show question as assistant message
        updateLastAssistantMessage(
          convId,
          payload.message || "I need more information to proceed."
        );
        // Store pending clarification state — switches InputBar to ClarificationBar
        setPendingClarification({
          threadId: payload.thread_id || activeConversation?.threadId,
          question: payload.message,
          conversationId: convId,
        });
        setIsStreaming(false);
        setStatusLabel("");
      },
    };
  }

  const handleSend = useCallback(
    async (text, files) => {
      let convId = activeConversationId;
      if (!convId) {
        convId = createConversation();
      }

      let filePaths = [...uploadedFilePaths];
      let fileNames = [];

      if (files && files.length > 0) {
        setIsUploading(true);
        try {
          const uploadResult = await uploadFiles(files);
          filePaths = [...filePaths, ...uploadResult.file_paths];
          fileNames = files.map((f) => f.name);
        } catch (err) {
          addMessage(convId, {
            id: uuidv4(),
            role: "error",
            content: err.response?.data?.detail || err.message || "Failed to upload files.",
            timestamp: new Date().toISOString(),
          });
          setIsUploading(false);
          return;
        }
        setIsUploading(false);
      }

      addMessage(convId, {
        id: uuidv4(),
        role: "user",
        content: text,
        files: fileNames,
        timestamp: new Date().toISOString(),
      });

      setUploadedFilePaths([]);

      addMessage(convId, {
        id: uuidv4(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      });

      streamedTextRef.current = "";
      setIsStreaming(true);
      setStatusLabel("");

      try {
        await streamMessage(
          {
            query: text,
            file_paths: filePaths,
            thread_id: activeConversation?.threadId || null,
          },
          buildCallbacks(convId)
        );
      } catch (err) {
        updateLastAssistantMessage(convId, "");
        addMessage(convId, {
          id: uuidv4(),
          role: "error",
          content: err.message || "Failed to get a response.",
          timestamp: new Date().toISOString(),
        });
        setIsStreaming(false);
        setStatusLabel("");
      }
    },
    [activeConversationId, activeConversation, uploadedFilePaths]
  );

  const handleClarification = useCallback(
    async (answer) => {
      if (!pendingClarification) return;

      const { conversationId, threadId } = pendingClarification;

      // Add user's clarification answer as a message
      addMessage(conversationId, {
        id: uuidv4(),
        role: "user",
        content: answer,
        timestamp: new Date().toISOString(),
      });

      // Add placeholder for assistant response
      addMessage(conversationId, {
        id: uuidv4(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      });

      streamedTextRef.current = "";
      setIsStreaming(true);
      setStatusLabel("");

      try {
        await streamClarification(
          { query: answer, thread_id: threadId },
          buildCallbacks(conversationId)
        );
      } catch (err) {
        updateLastAssistantMessage(conversationId, "");
        addMessage(conversationId, {
          id: uuidv4(),
          role: "error",
          content: err.message || "Failed to get a response.",
          timestamp: new Date().toISOString(),
        });
        setPendingClarification(null);
        setIsStreaming(false);
        setStatusLabel("");
      }
    },
    [pendingClarification]
  );

  const chatTitle = activeConversation?.title || "Select a conversation";
  const messages = activeConversation?.messages || [];
  const visibleMessages = messages.filter(
    (m) => !(m.role === "assistant" && m.content === "" && !isStreaming)
  );

  return (
    <div className="flex h-screen bg-[var(--background)]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-8 py-5 border-b border-[var(--border-light)]">
          <h2
            className="text-lg font-bold truncate"
            style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
          >
            {chatTitle}
          </h2>
        </div>

        <MessageList
          messages={visibleMessages}
          isStreaming={isStreaming}
          statusLabel={statusLabel}
        />

        {/* Show clarification input or normal input */}
        {pendingClarification ? (
          <ClarificationBar
            question={pendingClarification.question}
            onSubmit={handleClarification}
            disabled={isStreaming}
          />
        ) : (
          <InputBar onSend={handleSend} disabled={isStreaming || isUploading} />
        )}
      </div>
    </div>
  );
}
import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import Sidebar from "../components/Sidebar";
import MessageList from "../components/MessageList";
import InputBar from "../components/InputBar";
import { useChat } from "../context/ChatContext";
import { uploadFiles, streamMessage } from "../api/chat";

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
  } = useChat();

  const [uploadedFilePaths, setUploadedFilePaths] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [statusLabel, setStatusLabel] = useState("");

  // Ref to accumulate streamed tokens without stale-closure issues
  const streamedTextRef = useRef("");

  const handleSend = useCallback(
    async (text, files) => {
      // Ensure we have an active conversation
      let convId = activeConversationId;
      if (!convId) {
        convId = createConversation();
      }

      // Upload files first if any
      let filePaths = [...uploadedFilePaths];
      let fileNames = [];

      if (files && files.length > 0) {
        setIsUploading(true);
        try {
          const uploadResult = await uploadFiles(files);
          filePaths = [...filePaths, ...uploadResult.file_paths];
          fileNames = files.map((f) => f.name);
        } catch (err) {
          // Add error message
          addMessage(convId, {
            id: uuidv4(),
            role: "error",
            content:
              err.response?.data?.detail ||
              err.message ||
              "Failed to upload files.",
            timestamp: new Date().toISOString(),
          });
          setIsUploading(false);
          return;
        }
        setIsUploading(false);
      }

      // Add user message
      const userMessage = {
        id: uuidv4(),
        role: "user",
        content: text,
        files: fileNames,
        timestamp: new Date().toISOString(),
      };
      addMessage(convId, userMessage);

      // Clear uploaded file paths
      setUploadedFilePaths([]);

      // Add placeholder assistant message
      const assistantMessageId = uuidv4();
      addMessage(convId, {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      });

      // Reset streamed text accumulator
      streamedTextRef.current = "";

      // Stream from API via SSE
      setIsStreaming(true);
      setStatusLabel("");

      try {
        await streamMessage(
          {
            query: text,
            file_paths: filePaths,
            thread_id: activeConversation?.threadId || null,
          },
          {
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
              setIsStreaming(false);
              setStatusLabel("");
            },
            onError: (payload) => {
              // Replace the empty/partial assistant message with error
              updateLastAssistantMessage(convId, "");
              addMessage(convId, {
                id: uuidv4(),
                role: "error",
                content:
                  payload.message || "Failed to get a response. Please try again.",
                timestamp: new Date().toISOString(),
              });
              setIsStreaming(false);
              setStatusLabel("");
            },
            onClarification: (payload) => {
              // Show clarification question as assistant message, re-enable input
              updateLastAssistantMessage(
                convId,
                payload.message || "I need more information to proceed."
              );
              setIsStreaming(false);
              setStatusLabel("");
            },
          }
        );
      } catch (err) {
        // Network-level error (fetch itself failed)
        updateLastAssistantMessage(convId, "");
        addMessage(convId, {
          id: uuidv4(),
          role: "error",
          content: err.message || "Failed to get a response. Please try again.",
          timestamp: new Date().toISOString(),
        });
        setIsStreaming(false);
        setStatusLabel("");
      }
    },
    [
      activeConversationId,
      activeConversation,
      uploadedFilePaths,
      createConversation,
      addMessage,
      updateLastAssistantMessage,
      setThreadId,
      setIsStreaming,
    ]
  );

  const chatTitle = activeConversation
    ? activeConversation.title
    : "Select a conversation";

  const messages = activeConversation ? activeConversation.messages : [];
  // Filter out empty assistant messages — but keep them visible during streaming
  // so the placeholder shows while tokens arrive
  const visibleMessages = messages.filter(
    (m) => !(m.role === "assistant" && m.content === "" && !isStreaming)
  );

  return (
    <div className="flex h-screen bg-[var(--background)]">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <div className="px-8 py-5 border-b border-[var(--border-light)]">
          <h2
            className="text-lg font-bold truncate"
            style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
          >
            {chatTitle}
          </h2>
        </div>

        {/* Messages area */}
        <MessageList
          messages={visibleMessages}
          isStreaming={isStreaming}
          statusLabel={statusLabel}
        />

        {/* Input bar */}
        <InputBar onSend={handleSend} disabled={isStreaming || isUploading} />
      </div>
    </div>
  );
}

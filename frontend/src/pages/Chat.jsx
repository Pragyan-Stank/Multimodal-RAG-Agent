import { useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import Sidebar from "../components/Sidebar";
import MessageList from "../components/MessageList";
import InputBar from "../components/InputBar";
import { useChat } from "../context/ChatContext";
import { uploadFiles, sendMessage } from "../api/chat";

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

      // Send to API
      setIsStreaming(true);
      try {
        const result = await sendMessage({
          query: text,
          file_paths: filePaths,
          thread_id: activeConversation?.threadId || null,
        });

        // Update assistant message with response
        updateLastAssistantMessage(convId, result.final_answer);

        // Store thread_id for conversation continuity
        if (result.thread_id) {
          setThreadId(convId, result.thread_id);
        }
      } catch (err) {
        // Replace the empty assistant message with an error
        updateLastAssistantMessage(
          convId,
          ""
        );
        addMessage(convId, {
          id: uuidv4(),
          role: "error",
          content:
            err.response?.data?.detail ||
            err.message ||
            "Failed to get a response. Please try again.",
          timestamp: new Date().toISOString(),
        });
      } finally {
        setIsStreaming(false);
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
  // Filter out empty assistant messages (placeholder that was replaced by error)
  const visibleMessages = messages.filter(
    (m) => !(m.role === "assistant" && m.content === "")
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
        <MessageList messages={visibleMessages} isStreaming={isStreaming} />

        {/* Input bar */}
        <InputBar onSend={handleSend} disabled={isStreaming || isUploading} />
      </div>
    </div>
  );
}

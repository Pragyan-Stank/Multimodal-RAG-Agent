import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import Sidebar from "../components/Sidebar";
import MessageList from "../components/MessageList";
import InputBar from "../components/InputBar";
import ClarificationBar from "../components/ClarificationBar";
import { useChat } from "../context/ChatContext";
import { uploadFiles, streamMessage, streamClarification } from "../api/chat";


// ---------------------------------
// Outside component — no stale closure risk
// ---------------------------------

function buildCallbacks(convId, ctx) {
  return {
    onToken: (payload) => {
      ctx.streamedTextRef.current += payload.content;
      ctx.updateLastAssistantMessage(convId, ctx.streamedTextRef.current);
    },
    onStatus: (payload) => {
      ctx.setStatusLabel(payload.message || "");
    },
    onDone: (payload) => {
      if (payload.thread_id) {
        ctx.setThreadId(convId, payload.thread_id);
      }
      ctx.setPendingClarification(null);
      ctx.setIsStreaming(false);
      ctx.setStatusLabel("");
    },
    onError: (payload) => {
      ctx.updateLastAssistantMessage(convId, "");
      ctx.addMessage(convId, {
        id: uuidv4(),
        role: "error",
        content: payload.message || "Failed to get a response.",
        timestamp: new Date().toISOString(),
      });
      ctx.setPendingClarification(null);
      ctx.setIsStreaming(false);
      ctx.setStatusLabel("");
    },
    onClarification: (payload) => {
      if (payload.thread_id) {
        ctx.setThreadId(convId, payload.thread_id);
      }
      ctx.updateLastAssistantMessage(
        convId,
        payload.message || "I need more information to proceed."
      );
      ctx.setPendingClarification({
        threadId: payload.thread_id,
        question: payload.message,
        conversationId: convId,
      });
      ctx.setIsStreaming(false);
      ctx.setStatusLabel("");
    },
  };
}


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

  // contextRef always points to latest values — no stale closures during streaming
  const contextRef = useRef({});
  contextRef.current = {
    updateLastAssistantMessage,
    addMessage,
    setThreadId,
    setIsStreaming,
    setStatusLabel,
    setPendingClarification,
    streamedTextRef,
  };

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
          contextRef.current.addMessage(convId, {
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

      contextRef.current.addMessage(convId, {
        id: uuidv4(),
        role: "user",
        content: text,
        files: fileNames,
        timestamp: new Date().toISOString(),
      });

      setUploadedFilePaths([]);

      contextRef.current.addMessage(convId, {
        id: uuidv4(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      });

      streamedTextRef.current = "";
      contextRef.current.setIsStreaming(true);
      contextRef.current.setStatusLabel("");

      try {
        await streamMessage(
          {
            query: text,
            file_paths: filePaths,
            thread_id: activeConversation?.threadId || null,
          },
          buildCallbacks(convId, contextRef.current)
        );
      } catch (err) {
        contextRef.current.updateLastAssistantMessage(convId, "");
        contextRef.current.addMessage(convId, {
          id: uuidv4(),
          role: "error",
          content: err.message || "Failed to get a response.",
          timestamp: new Date().toISOString(),
        });
        contextRef.current.setIsStreaming(false);
        contextRef.current.setStatusLabel("");
      }
    },
    [activeConversationId, activeConversation?.threadId, uploadedFilePaths, createConversation]
  );

  const handleClarification = useCallback(
    async (answer) => {
      if (!pendingClarification) return;

      const { conversationId, threadId } = pendingClarification;

      contextRef.current.addMessage(conversationId, {
        id: uuidv4(),
        role: "user",
        content: answer,
        timestamp: new Date().toISOString(),
      });

      contextRef.current.addMessage(conversationId, {
        id: uuidv4(),
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      });

      streamedTextRef.current = "";
      contextRef.current.setIsStreaming(true);
      contextRef.current.setStatusLabel("");

      try {
        await streamClarification(
          { query: answer, thread_id: threadId },
          buildCallbacks(conversationId, contextRef.current)
        );
      } catch (err) {
        contextRef.current.updateLastAssistantMessage(conversationId, "");
        contextRef.current.addMessage(conversationId, {
          id: uuidv4(),
          role: "error",
          content: err.message || "Failed to get a response.",
          timestamp: new Date().toISOString(),
        });
        contextRef.current.setPendingClarification(null);
        contextRef.current.setIsStreaming(false);
        contextRef.current.setStatusLabel("");
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
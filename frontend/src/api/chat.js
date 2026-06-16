import client from "./client";

/**
 * Upload files to the backend.
 * @param {File[]} files - Array of File objects
 * @returns {Promise<{ file_paths: string[], file_names: string[], count: number }>}
 */
export async function uploadFiles(files) {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await client.post("/api/v1/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}

/**
 * Send a chat message to the backend.
 * @param {{ query: string, file_paths: string[], thread_id: string | null }} params
 * @returns {Promise<{ thread_id: string, final_answer: string, task: string }>}
 */
export async function sendMessage({ query, file_paths = [], thread_id = null }) {
  const response = await client.post("/api/v1/chat", {
    query,
    file_paths,
    thread_id,
  });

  return response.data;
}

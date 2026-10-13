
import api from '../api'

export async function sendChatMessage(message, conversationId) {
  const { data } = await api.post('/chat/', {
    message,
    conversation_id: conversationId,
  })

  return data
}

export async function resumeChat(conversationId, approved) {
  const { data } = await api.post('/chat/resume', {
    conversation_id: conversationId,
    approved,
  })

  return data
}

export async function getChatHistory(conversationId) {
  const { data } = await api.get(
    `/chat/history/${conversationId}`
  );

  return data;
}
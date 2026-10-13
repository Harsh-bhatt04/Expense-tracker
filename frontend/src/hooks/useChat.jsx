
import { useRef, useState, useEffect} from 'react'
import {
  sendChatMessage,
  resumeChat,
  getChatHistory
} from '../services/chatService'

export default function useChat() {
  const [conversationId, setConversationId] = useState(() => {
  const savedId = localStorage.getItem("moneymate_conversation_id");

  if (savedId) return savedId;

  const newId = crypto.randomUUID();
  localStorage.setItem("moneymate_conversation_id", newId);

  return newId;
});
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [pendingApproval, setPendingApproval] = useState(null)

  const conversationRef = useRef(conversationId)
  const busyRef = useRef(false)

  useEffect(() => {
  let cancelled = false;

  async function restoreHistory() {
    try {
      const data = await getChatHistory(conversationId);

      if (cancelled) return;

      setMessages(
        data.messages.map((message) => ({
          id: crypto.randomUUID(),
          role: message.role,
          content: message.content,
        }))
      );

      setPendingApproval(data.pending_approval ?? null);
      setError(null);

    } catch (error) {
      if (!cancelled) {
        console.error("Failed to restore chat:", error);
        setError("Unable to restore conversation.");
      }
    }
  }

  restoreHistory();

  return () => {
    cancelled = true;
  };
}, [conversationId]);

  const appendAssistant = (content) => {
    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        content,
      },
    ])
  }

  const processResponse = (data) => {
    if (data.status === 'approval_required') {
      setPendingApproval(data.approval)
    } else {
      setPendingApproval(null)
    }

    if (data.response) {
      appendAssistant(data.response)
    }
  }

  const sendMessage = async (message) => {
    const content = message.trim()

    if (!content || busyRef.current || pendingApproval) return

    const currentId = conversationRef.current
    busyRef.current = true
    setLoading(true)
    setError('')

    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content,
      },
    ])

    try {
      const data = await sendChatMessage(content, currentId)

      if (conversationRef.current === currentId) {
        processResponse(data)
      }
    } catch (err) {
      console.error(err)
      if (conversationRef.current === currentId) {
        setError('Unable to send message. Please try again.')
      }
    } finally {
      busyRef.current = false
      setLoading(false)
    }
  }

  const respondToApproval = async (approved) => {
    if (!pendingApproval || busyRef.current) return

    const currentId = conversationRef.current
    busyRef.current = true
    setLoading(true)
    setError('')

    try {
      const data = await resumeChat(currentId, approved)

      if (conversationRef.current === currentId) {
        processResponse(data)
      }
    } catch (err) {
      console.error(err)
      if (conversationRef.current === currentId) {
        setError('Unable to process approval. Please retry.')
      }
    } finally {
      busyRef.current = false
      setLoading(false)
    }
  }

  const clearChat = () => {
  const newId = crypto.randomUUID();

  localStorage.setItem("moneymate_conversation_id", newId);

  setConversationId(newId);
  setMessages([]);
  setPendingApproval(null);
  setError(null);
};

  return {
    conversationId,
    messages,
    loading,
    error,
    pendingApproval,
    sendMessage,
    respondToApproval,
    clearChat,
  }
}

import { useRef, useState } from 'react'
import {
  sendChatMessage,
  resumeChat,
} from '../services/chatService'

export default function useChat() {
  const [conversationId, setConversationId] = useState(
    () => crypto.randomUUID()
  )
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [pendingApproval, setPendingApproval] = useState(null)

  const conversationRef = useRef(conversationId)
  const busyRef = useRef(false)

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
    if (busyRef.current) return

    const id = crypto.randomUUID()
    conversationRef.current = id
    setConversationId(id)
    setMessages([])
    setPendingApproval(null)
    setError('')
  }

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
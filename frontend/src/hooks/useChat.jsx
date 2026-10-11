
import { useState } from 'react'
import { sendChatMessage } from '../services/chatService'

export default function useChat() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async (message) => {
    const content = message.trim()
    if (!content || loading) return

    setError('')
    setLoading(true)

    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content,
      },
    ])

    try {
      const response = await sendChatMessage(content)

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response,
        },
      ])
    } catch (err) {
      console.error('Chat error:', err)
      setError('Unable to get a response. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setError('')
  }

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  }
}

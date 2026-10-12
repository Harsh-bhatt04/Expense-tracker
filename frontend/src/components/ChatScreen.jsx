
import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useChatContext } from '../context/ChatContext'
import ChatMessage from './ChatMessage'

import {
  ArrowUp,
  ChartNoAxesColumn,
  MessageCircle,
  Plus,
  ReceiptText,
  Sparkles,
  Wallet,
  ShieldCheck,
} from 'lucide-react'

const suggestions = [
  {
    icon: Wallet,
    title: 'Account Balance',
    prompt: 'What is my total balance across all accounts?',
    color: 'from-violet-500/20 to-indigo-500/10',
  },
  {
    icon: ReceiptText,
    title: 'My Expenses',
    prompt: 'How much have I spent this month?',
    color: 'from-pink-500/20 to-rose-500/10',
  },
  {
    icon: ChartNoAxesColumn,
    title: 'Spending Insights',
    prompt: 'Show my category-wise spending this month.',
    color: 'from-cyan-500/20 to-blue-500/10',
  },
]

export default function ChatScreen() {
  const {
    messages,
    loading,
    error,
    pendingApproval,
    sendMessage,
    respondToApproval,
    clearChat,
  } = useChatContext()

  const [message, setMessage] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    })
  }, [messages, loading, pendingApproval])

  const handleSend = (text = message) => {
    const content = text.trim()

    if (!content || loading || pendingApproval) return

    sendMessage(content)
    setMessage('')
  }

  const handleNewChat = () => {
    if (loading) return

    clearChat()
    setMessage('')
  }

  return (
    <div className="flex h-full flex-col bg-slate-950">
      <header className="flex items-center justify-between border-b border-white/10 px-5 py-4 sm:px-8">
        <div className="flex items-center gap-3">
          <MessageCircle
            className="text-violet-400"
            size={22}
          />

          <div>
            <h1 className="font-semibold">
              AI Finance Assistant
            </h1>

            <p className="text-xs text-slate-400">
              Your personal money companion
            </p>
          </div>
        </div>

        <button
          onClick={handleNewChat}
          disabled={loading}
          className="flex cursor-pointer items-center gap-2 rounded-xl bg-violet-600 px-3 py-2 text-sm font-medium hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Plus size={17} />

          <span className="hidden sm:inline">
            New Chat
          </span>
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-8 sm:px-8">
        <div className="mx-auto max-w-3xl">
          {messages.length === 0 && !pendingApproval ? (
            <div className="pt-6 text-center sm:pt-14">
              <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-600/20 text-violet-400">
                <Sparkles size={32} />
              </div>

              <h2 className="text-2xl font-bold sm:text-3xl">
                Your money, made simple.
              </h2>

              <p className="mt-3 text-sm text-slate-400">
                Ask questions about your finances or explore your dashboard.
              </p>

              <div className="mt-9 grid gap-3 sm:grid-cols-3">
                {suggestions.map((item) => {
                  const Icon = item.icon

                  return (
                    <button
                      key={item.title}
                      onClick={() => handleSend(item.prompt)}
                      disabled={loading}
                      className={`cursor-pointer rounded-2xl border border-white/10 bg-gradient-to-br ${item.color} p-4 text-left transition hover:border-violet-400/50 disabled:opacity-50`}
                    >
                      <Icon
                        size={23}
                        className="mb-4 text-violet-300"
                      />

                      <p className="font-semibold">
                        {item.title}
                      </p>

                      <p className="mt-2 text-xs leading-5 text-slate-400">
                        {item.prompt}
                      </p>
                    </button>
                  )
                })}
              </div>

              <Link
                to="/dashboard"
                className="mt-7 inline-block text-sm text-violet-400 hover:text-violet-300"
              >
                Explore your financial dashboard →
              </Link>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((item) => (
                <ChatMessage
                  key={item.id}
                  message={item}
                />
              ))}

              {pendingApproval && (
                <div className="max-w-xl rounded-2xl border border-amber-500/30 bg-slate-900 p-5">
                  <div className="mb-3 flex items-center gap-2 text-amber-300">
                    <ShieldCheck size={20} />

                    <h3 className="font-semibold">
                      Transaction Approval Required
                    </h3>
                  </div>

                  <p className="mb-4 text-sm text-slate-400">
                    Please review the details before saving
                    this transaction.
                  </p>

                  {pendingApproval.actions?.map(
                    (action, index) => (
                      <div
                        key={index}
                        className="mb-4 rounded-xl border border-white/10 bg-slate-950 p-4"
                      >
                        <p className="mb-3 text-sm font-semibold text-violet-300">
                          {action.tool
                            .replaceAll('_', ' ')
                            .toUpperCase()}
                        </p>

                        <div className="space-y-2">
                          {Object.entries(
                            action.arguments || {}
                          ).map(([key, value]) => (
                            <div
                              key={key}
                              className="flex justify-between gap-4 text-sm"
                            >
                              <span className="capitalize text-slate-400">
                                {key.replaceAll('_', ' ')}
                              </span>

                              <span className="break-all text-right text-white">
                                {String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  )}

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => respondToApproval(true)}
                      disabled={loading}
                      className="cursor-pointer rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Approve
                    </button>

                    <button
                      type="button"
                      onClick={() => respondToApproval(false)}
                      disabled={loading}
                      className="cursor-pointer rounded-lg bg-red-600 px-4 py-2 text-sm font-medium hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {loading && (
                <div className="flex justify-start">
                  <div className="animate-pulse rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-sm text-violet-400">
                    MoneyMate is thinking...
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {error && (
            <p className="mt-4 text-sm text-red-400">
              {error}
            </p>
          )}
        </div>
      </div>

      <div className="border-t border-white/10 px-4 py-4 sm:px-8">
        <form
          onSubmit={(event) => {
            event.preventDefault()
            handleSend()
          }}
          className="mx-auto flex max-w-3xl items-end gap-3 rounded-2xl border border-white/10 bg-slate-900 p-3 focus-within:border-violet-500/60"
        >
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (
                event.key === 'Enter' &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault()
                handleSend()
              }
            }}
            disabled={loading || !!pendingApproval}
            rows={2}
            placeholder={
              pendingApproval
                ? 'Approve or cancel the pending transaction...'
                : 'Ask anything about your finances...'
            }
            className="max-h-36 min-h-12 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-white outline-none placeholder:text-slate-500 disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={
              loading ||
              !!pendingApproval ||
              !message.trim()
            }
            className="cursor-pointer rounded-xl bg-violet-600 p-3 hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-40"
            aria-label="Send message"
          >
            <ArrowUp size={20} />
          </button>
        </form>

        <p className="mt-2 text-center text-xs text-slate-500">
          Powered by Gemini
        </p>
      </div>
    </div>
  )
}
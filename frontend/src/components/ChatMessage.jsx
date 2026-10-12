
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div
      className={`flex ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-[85%] min-w-0 rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? 'rounded-br-md bg-violet-600 text-white whitespace-pre-wrap'
            : 'rounded-bl-md border border-white/10 bg-slate-900 text-slate-100'
        }`}
      >
        {isUser ? (
          message.content
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => (
                <p className="mb-3 last:mb-0">{children}</p>
              ),
              h1: ({ children }) => (
                <h1 className="mb-3 text-lg font-bold">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="mb-2 text-base font-semibold">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="mb-2 font-semibold">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="mb-3 list-disc space-y-1 pl-5">
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-3 list-decimal space-y-1 pl-5">
                  {children}
                </ol>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-white">
                  {children}
                </strong>
              ),
              code: ({ children, className }) => (
                <code
                  className={`${className || ''} rounded bg-slate-800 px-1 py-0.5 text-violet-300`}
                >
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre className="my-3 overflow-x-auto rounded-lg bg-slate-950 p-3">
                  {children}
                </pre>
              ),
              table: ({ children }) => (
                <div className="my-3 overflow-x-auto">
                  <table className="min-w-full border-collapse text-left">
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th className="border border-white/20 px-3 py-2 font-semibold">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="border border-white/20 px-3 py-2">
                  {children}
                </td>
              ),
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-violet-400 underline"
                >
                  {children}
                </a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}
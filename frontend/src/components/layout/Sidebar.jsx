
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageCircle,
  Sparkles,
  Wallet,
} from 'lucide-react'

export default function Sidebar() {
  const navClass = ({ isActive }) =>
    `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
      isActive
        ? 'bg-violet-600 text-white'
        : 'text-slate-300 hover:bg-white/10 hover:text-white'
    }`

  return (
    <aside className="flex w-17 shrink-0 flex-col border-r border-white/10 bg-slate-900 px-2 py-5 sm:w-64 sm:px-4">
      <div className="mb-9 flex items-center gap-3 px-2">
        <div className="rounded-xl bg-violet-600 p-2">
          <Wallet size={22} />
        </div>
        <div className="hidden sm:block">
          <h1 className="font-bold">MoneyMate</h1>
          <p className="text-xs text-slate-400">
            Personal Finance AI
          </p>
        </div>
      </div>

      <nav className="space-y-2">
        <NavLink to="/" end className={navClass}>
          <MessageCircle size={20} />
          <span className="hidden sm:inline">AI Chat</span>
        </NavLink>

        <NavLink to="/dashboard" className={navClass}>
          <LayoutDashboard size={20} />
          <span className="hidden sm:inline">Dashboard</span>
        </NavLink>
      </nav>

      <NavLink
        to="/dashboard"
        className="mt-auto hidden rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-700 p-4 transition hover:brightness-110 sm:block"
      >
        <Sparkles size={22} className="mb-3" />
        <h2 className="font-semibold">Smart Money Tracking</h2>
        <p className="mt-2 text-xs leading-5 text-violet-100">
          View your expenses, account balances, and financial insights.
        </p>
        <p className="mt-3 text-sm font-medium">
          Explore dashboard →
        </p>
      </NavLink>
    </aside>
  )
}
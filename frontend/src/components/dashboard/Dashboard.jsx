
import { RefreshCw } from 'lucide-react'
import useDashboard from '../../hooks/useDashboard'
import BalanceOverview from './BalanceOverview'
import ExpenseOverview from './ExpenseOverview'
import RecentTransactions from './RecentTransactions'

export default function Dashboard() {
  const {
    balances,
    expenses,
    categories,
    transactions,
    loading,
    errors,
    refreshDashboard,
  } = useDashboard()

  return (
    <main className="h-full overflow-y-auto bg-slate-950 px-5 py-7 sm:px-8">
      <div className="mx-auto max-w-6xl space-y-7">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold sm:text-3xl">
              Financial Dashboard
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              Track your balances, expenses and transactions.
            </p>
          </div>

          <button
            onClick={refreshDashboard}
            disabled={loading}
            className="flex cursor-pointer items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2 text-sm transition hover:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </header>

        <BalanceOverview
          balances={balances}
          error={errors.balances}
          loading={loading}
        />

        <ExpenseOverview
          expenses={expenses}
          categories={categories}
          errors={errors}
          loading={loading}
        />

        <RecentTransactions
          transactions={transactions}
          error={errors.transactions}
          loading={loading}
        />
      </div>
    </main>
  )
}
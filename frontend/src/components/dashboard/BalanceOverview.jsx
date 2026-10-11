
import { Landmark, Wallet } from 'lucide-react'

const formatCurrency = (amount, currency = 'INR') =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(Number(amount) || 0)

export default function BalanceOverview({ balances, error, loading }) {
  if (!balances) {
    return (
      <div className="rounded-2xl border border-white/10 bg-slate-900 p-5 text-sm text-slate-400">
        {error || (loading ? 'Loading balances...' : 'No balance data available.')}
      </div>
    )
  }

  const accounts = balances.accounts ?? []

  return (
    <section className="space-y-5">
      <div className="rounded-2xl bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700 p-6 shadow-xl shadow-violet-950/20">
        <div className="flex items-center gap-3 text-violet-100">
          <Wallet size={22} />
          <span className="text-sm font-medium">Total Balance</span>
        </div>

        <h2 className="mt-4 text-3xl font-bold sm:text-4xl">
          {formatCurrency(balances.total_balance)}
        </h2>

        <p className="mt-3 text-sm text-violet-100">
          Combined balance across {accounts.length} accounts
        </p>
      </div>

      <div>
        <h3 className="mb-3 text-lg font-semibold">Bank Accounts</h3>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {accounts.map((account) => (
            <article
              key={account.account_id}
              className="rounded-2xl border border-white/10 bg-slate-900 p-5"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-indigo-500/15 p-3 text-indigo-400">
                  <Landmark size={21} />
                </div>
                <p className="font-medium">{account.account_name}</p>
              </div>

              <p className="mt-5 text-2xl font-bold">
                {formatCurrency(
                  account.current_balance,
                  account.currency
                )}
              </p>

              <div className="mt-5 space-y-2 border-t border-white/10 pt-4 text-sm">
                <div className="flex justify-between gap-2 text-slate-400">
                  <span>Income</span>
                  <span className="text-emerald-400">
                    {formatCurrency(
                      account.total_income,
                      account.currency
                    )}
                  </span>
                </div>

                <div className="flex justify-between gap-2 text-slate-400">
                  <span>Expenses</span>
                  <span className="text-rose-400">
                    {formatCurrency(
                      account.total_expenses,
                      account.currency
                    )}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
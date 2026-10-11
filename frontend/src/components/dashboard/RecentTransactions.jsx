
import { ArrowDownLeft, ArrowUpRight, ReceiptText } from 'lucide-react'

const money = (amount) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number(amount) || 0)

export default function RecentTransactions({
  transactions,
  error,
  loading,
}) {
  const rows = Array.isArray(transactions)
    ? transactions
    : transactions?.transactions ?? transactions?.items ?? []

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900 p-5">
      <div className="mb-5 flex items-center gap-3">
        <ReceiptText size={21} className="text-violet-400" />
        <h3 className="text-lg font-semibold">Recent Transactions</h3>
      </div>

      {error && <p className="text-sm text-rose-400">{error}</p>}

      {!error && loading && !transactions && (
        <p className="text-sm text-slate-400">Loading transactions...</p>
      )}

      {!error && !loading && rows.length === 0 && (
        <p className="text-sm text-slate-400">
          No transactions found.
        </p>
      )}

      <div className="divide-y divide-white/10">
        {rows.map((transaction, index) => {
          const type = transaction.type ?? transaction.transaction_type
          const income = type === 'income' || type === 'transfer_in'
          const Icon = income ? ArrowDownLeft : ArrowUpRight

          return (
            <div
              key={transaction.id ?? transaction.transaction_id ?? index}
              className="flex items-center justify-between gap-4 py-4"
            >
              <div className="flex min-w-0 items-center gap-3">
                <div
                  className={`rounded-xl p-3 ${
                    income
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'bg-rose-500/10 text-rose-400'
                  }`}
                >
                  <Icon size={19} />
                </div>

                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">
                    {transaction.description ??
                      transaction.category ??
                      type ??
                      'Transaction'}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    {transaction.date ??
                      transaction.transaction_date ??
                      transaction.created_at ??
                      'Date unavailable'}
                  </p>
                </div>
              </div>

              <p
                className={`shrink-0 text-sm font-semibold ${
                  income ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {income ? '+' : '-'}
                {money(transaction.amount)}
              </p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
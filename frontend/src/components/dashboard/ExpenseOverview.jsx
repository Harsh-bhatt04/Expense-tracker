
import { ReceiptText, Tags } from 'lucide-react'

const money = (value) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number(value) || 0)

function SummaryCard({ title, icon: Icon, data, error, loading, type }) {
  const total =
  type === 'expenses'
    ? Array.isArray(data?.categories)
      ? data.categories.reduce(
          (sum, item) => sum + Number(item.total ?? 0),
          0
        )
      : null
    : null

  const rows = Array.isArray(data)
    ? data
    : type === 'categories'
      ? data?.categories ?? data?.breakdown ?? data?.data
      : data?.expenses ?? data?.breakdown ?? data?.data

  return (
    <article className="rounded-2xl border border-white/10 bg-slate-900 p-5">
      <div className="mb-5 flex items-center gap-3">
        <div className="rounded-xl bg-violet-500/15 p-3 text-violet-400">
          <Icon size={22} />
        </div>
        <h3 className="font-semibold">{title}</h3>
      </div>

      {error && <p className="text-sm text-rose-400">{error}</p>}

      {!data && !error && (
        <p className="text-sm text-slate-400">
          {loading ? 'Loading...' : 'No data available.'}
        </p>
      )}

      {total != null && (
        <p className="mb-4 text-3xl font-bold">{money(total)}</p>
      )}

      {Array.isArray(rows) && rows.length > 0 && (
        <div className="space-y-3">
          {rows.map((item, index) => {
            const label =
              item.category_name ??
              item.category ??
              item.name ??
              item.date ??
              item.period ??
              `Item ${index + 1}`

            const amount =
              item.total_amount ??
              item.total_expenses ??
              item.amount ??
              item.total ??
              item.value

            return (
              <div
                key={`${label}-${index}`}
                className="flex justify-between gap-3 border-b border-white/5 pb-3 text-sm"
              >
                <span className="text-slate-400">{label}</span>
                <span className="font-medium">
                  {amount == null ? '—' : money(amount)}
                </span>
              </div>
            )
          })}
        </div>
      )}

      {data && total == null && (!Array.isArray(rows) || rows.length === 0) && (
        <p className="text-sm text-slate-400">
          No summary values available for this period.
        </p>
      )}
    </article>
  )
}

export default function ExpenseOverview({
  expenses,
  categories,
  errors,
  loading,
}) {
  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <SummaryCard
        title="Monthly Expenses"
        icon={ReceiptText}
        data={expenses}
        error={errors.expenses}
        loading={loading}
        type="expenses"
      />

      <SummaryCard
        title="Category Breakdown"
        icon={Tags}
        data={categories}
        error={errors.categories}
        loading={loading}
        type="categories"
      />
    </section>
  )
}
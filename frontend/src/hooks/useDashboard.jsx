
import { useCallback, useEffect, useState } from 'react'
import {
  getBalances,
  getCategorySummary,
  getExpenseSummary,
  getTransactions,
} from '../services/dashboardServices'

export default function useDashboard() {
  const [balances, setBalances] = useState(null)
  const [expenses, setExpenses] = useState(null)
  const [categories, setCategories] = useState(null)
  const [transactions, setTransactions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState({})

  const refreshDashboard = useCallback(async () => {
    setLoading(true)
    setErrors({})

    const requests = [
      ['balances', getBalances],
      ['expenses', () => getCategorySummary('month')],
      ['categories', getCategorySummary],
      ['transactions', () => getTransactions({ limit: 10 })],
    ]

    const results = await Promise.allSettled(
      requests.map(([, request]) => request())
    )

    const nextErrors = {}

    results.forEach((result, index) => {
      const name = requests[index][0]

      if (result.status === 'fulfilled') {
        const value = result.value

        if (name === 'balances') setBalances(value)
        if (name === 'expenses') setExpenses(value)
        if (name === 'categories') setCategories(value)
        if (name === 'transactions') setTransactions(value)
      } else {
        nextErrors[name] = `Unable to load ${name}.`
        console.error(`${name} API failed:`, result.reason)
      }
    })

    setErrors(nextErrors)
    setLoading(false)
  }, [])

  useEffect(() => {
    refreshDashboard()
  }, [refreshDashboard])

  return {
    balances,
    expenses,
    categories,
    transactions,
    loading,
    errors,
    refreshDashboard,
  }
}
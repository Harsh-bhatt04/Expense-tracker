
import api from '../api'

export async function getBalances() {
  const { data } = await api.get('/summary/balances')
  return data
}

export async function getAccounts() {
  const { data } = await api.get('/accounts/')
  return data
}

export async function getTransactions(filters = {}) {
  const { data } = await api.get('/transactions/', {
    params: filters,
  })
  return data
}

export async function getCategorySummary(period = 'month') {
  const { data } = await api.get('/summary/categories', {
    params: { period },
  })
  return data
}

export async function getExpenseSummary(period = 'month') {
  const { data } = await api.get('/summary/expenses', {
    params: { period },
  })
  return data
}
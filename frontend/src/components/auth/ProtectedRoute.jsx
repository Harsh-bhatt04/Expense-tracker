
import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function ProtectedRoute() {
  const { authenticated, checking } = useAuth()

  if (checking) {
    return (
      <div className="flex h-dvh items-center justify-center bg-slate-950 text-slate-300">
        Restoring your session...
      </div>
    )
  }

  return authenticated
    ? <Outlet />
    : <Navigate to="/login" replace />
}

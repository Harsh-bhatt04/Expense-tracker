
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
  return (
    <div className="flex h-dvh overflow-hidden bg-slate-950 text-white">
      <Sidebar />

      <div className="min-w-0 flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  )
}
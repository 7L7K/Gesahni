import { useContext, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { EnrollContext } from '../context/EnrollContext'

export default function Welcome() {
  const nav = useNavigate()
  const ctx = useContext(EnrollContext)
  useEffect(() => {
    if (ctx && !ctx.userId) {
      ctx.setUserId(crypto.randomUUID())
    }
  }, [])
  return (
    <div className="h-screen flex flex-col items-center justify-center text-center space-y-4">
      <div className="text-6xl">👋</div>
      <h1 className="text-3xl font-bold">Hi, Gloria…</h1>
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={() => nav('/voice')}>Let's Start</button>
    </div>
  )
}

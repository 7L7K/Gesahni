import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { EnrollContext } from '../context/EnrollContext'
import { signInAnonymously } from 'firebase/auth'
import { auth as firebaseAuth } from '../firebase'

export default function Login() {
  const nav = useNavigate()
  const authCtx = useContext(AuthContext)!
  const enroll = useContext(EnrollContext)
  const [userId, setUserId] = useState('')

  async function submit() {
    if (!firebaseAuth.currentUser) {
      await signInAnonymously(firebaseAuth)
    }
    const token = await firebaseAuth.currentUser!.getIdToken()
    const resp = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ user_id: userId })
    })
    if (resp.ok) {
      authCtx.setUserId(userId)
      enroll?.setUserId(userId)
      const s = await fetch(`/api/users/${userId}/enrollment-status`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const d = await s.json()
      authCtx.setEnrolled(d.status === 'complete')
      if (d.status === 'complete') nav('/app/voice-ai')
      else nav('/app/enroll/voice')
    }
  }

  return (
    <div className="p-4 space-y-2 text-center">
      <h1 className="text-2xl font-bold">Welcome Back!</h1>
      <input className="border w-full" placeholder="Enter your ID" value={userId} onChange={e => setUserId(e.target.value)} />
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={submit}>Continue</button>
      <p className="underline cursor-pointer text-sm" onClick={() => alert('Please contact support')}>Forgot my ID?</p>
    </div>
  )
}

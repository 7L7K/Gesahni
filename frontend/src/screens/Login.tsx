import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { EnrollContext } from '../context/EnrollContext'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth as firebaseAuth } from '../firebase'

export default function Login() {
  const nav = useNavigate()
  const authCtx = useContext(AuthContext)!
  const enroll = useContext(EnrollContext)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  async function submit() {
    const cred = await signInWithEmailAndPassword(firebaseAuth, email, password)
    const token = await cred.user.getIdToken()
    const resp = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ user_id: cred.user.uid })
    })
    if (resp.ok) {
      authCtx.setUserId(cred.user.uid)
      enroll?.setUserId(cred.user.uid)
      const s = await fetch(`/api/users/${cred.user.uid}/enrollment-status`, {
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
      <input className="border w-full" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input className="border w-full" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={submit}>Continue</button>
    </div>
  )
}

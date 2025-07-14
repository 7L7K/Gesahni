import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { EnrollContext } from '../context/EnrollContext'

export default function Register() {
  const nav = useNavigate()
  const auth = useContext(AuthContext)!
  const enroll = useContext(EnrollContext)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  async function submit() {
    const resp = await fetch('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email })
    })
    const data = await resp.json()
    auth.setUserId(data.user_id)
    enroll?.setUserId(data.user_id)
    nav('/app/enroll/voice')
  }

  return (
    <div className="p-4 space-y-2 text-center">
      <h1 className="text-2xl font-bold">Let's set up your profile</h1>
      <input className="border w-full" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <input className="border w-full" placeholder="Email (optional)" value={email} onChange={e => setEmail(e.target.value)} />
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={submit}>Create My Profile</button>
    </div>
  )
}

import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { EnrollContext } from '../context/EnrollContext'
import { createUserWithEmailAndPassword } from 'firebase/auth'
import { auth as firebaseAuth } from '../firebase'

export default function Register() {
  const nav = useNavigate()
  const authCtx = useContext(AuthContext)!
  const enroll = useContext(EnrollContext)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  async function submit() {
    const cred = await createUserWithEmailAndPassword(firebaseAuth, email, password)
    authCtx.setUserId(cred.user.uid)
    enroll?.setUserId(cred.user.uid)
    nav('/app/enroll/voice')
  }

  return (
    <div className="p-4 space-y-2 text-center">
      <h1 className="text-2xl font-bold">Let's set up your profile</h1>
      <input className="border w-full" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <input className="border w-full" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input className="border w-full" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={submit}>Create My Profile</button>
    </div>
  )
}

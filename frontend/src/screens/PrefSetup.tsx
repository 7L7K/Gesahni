import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EnrollContext } from '../context/EnrollContext'
import { AuthContext } from '../context/AuthContext'

export default function PrefSetup() {
  const { userId, setPrefs } = useContext(EnrollContext)!
  const { token } = useContext(AuthContext)!
  const nav = useNavigate()
  const [name, setName] = useState('')
  const [greeting, setGreeting] = useState('')
  const [reminder, setReminder] = useState('sms')

  async function submit() {
    const prefs = { name, greeting, reminder_type: reminder }
    await fetch(`/api/enroll/prefs/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(prefs)
    })
    setPrefs(prefs)
    nav('/app/enroll/finish')
  }

  return (
    <div className="p-4 space-y-2">
      <input className="border" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <input className="border" placeholder="Greeting" value={greeting} onChange={e => setGreeting(e.target.value)} />
      <div>
        <label><input type="radio" checked={reminder==='sms'} onChange={()=>setReminder('sms')} /> SMS</label>
        <label className="ml-2"><input type="radio" checked={reminder==='email'} onChange={()=>setReminder('email')} /> Email</label>
      </div>
      <button className="px-4 py-2 bg-blue-500 text-white" onClick={submit}>Save</button>
    </div>
  )
}

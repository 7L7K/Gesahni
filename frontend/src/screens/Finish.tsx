import { useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EnrollContext } from '../context/EnrollContext'
import { AuthContext } from '../context/AuthContext'

export default function Finish() {
  const { userId } = useContext(EnrollContext)!
  const { token } = useContext(AuthContext)!
  const nav = useNavigate()
  const [audioUrl, setAudioUrl] = useState('')

  useEffect(() => {
    fetch(`/api/enroll/complete/${userId}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => setAudioUrl(d.audio_url))
  }, [])

  return (
    <div className="p-4 text-center space-y-2">
      <p>Enrollment complete!</p>
      {audioUrl && <audio controls src={audioUrl} autoPlay />}
      <button className="px-4 py-2 bg-green-500 text-white" onClick={() => nav('/app/voice-ai')}>Start Using Assistant</button>
    </div>
  )
}

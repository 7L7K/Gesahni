import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { EnrollContext } from '../context/EnrollContext'
import useRecorder from '../hooks/useRecorder'

const phrases = [
  'Today is a beautiful day',
  'I love open source',
  'FastAPI makes APIs easy'
]

export default function VoiceEnroll() {
  const { userId } = useContext(EnrollContext)!
  const nav = useNavigate()
  const { isRecording, start, stop, audioBlob } = useRecorder()

  async function handleStop() {
    stop()
    if (!audioBlob) return
    const form = new FormData()
    form.append('file', audioBlob, 'voice.wav')
    await fetch(`/enroll/voice/${userId}`, { method: 'POST', body: form })
    nav('/face')
  }

  return (
    <div className="p-4 space-y-4 text-center">
      {phrases.map(p => <p key={p}>{p}</p>)}
      <button className="text-4xl" onMouseDown={start} onMouseUp={handleStop}>
        🎤
      </button>
    </div>
  )
}

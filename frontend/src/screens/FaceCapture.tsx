import { useContext, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EnrollContext } from '../context/EnrollContext'
import { AuthContext } from '../context/AuthContext'

export default function FaceCapture() {
  const { userId } = useContext(EnrollContext)!
  const { token } = useContext(AuthContext)!
  const nav = useNavigate()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [step, setStep] = useState(0)

  async function startCamera() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.current) videoRef.current.srcObject = stream
  }

  async function capture() {
    if (!videoRef.current || !canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')!
    ctx.drawImage(videoRef.current, 0, 0, 640, 480)
    const blob = await new Promise<Blob | null>(res => canvasRef.current?.toBlob(res, 'image/jpeg'))
    if (!blob) return
    captures.push(blob)
    if (step < prompts.length - 1) {
      setStep(s => s + 1)
    } else {
      await submit()
    }
  }

  const captures: Blob[] = []
  const prompts = ['front', 'left', 'right']

  async function submit() {
    const form = new FormData()
    form.append('front', captures[0], 'front.jpg')
    form.append('left', captures[1], 'left.jpg')
    form.append('right', captures[2], 'right.jpg')
    await fetch(`/api/enroll/face/${userId}`, {
      method: 'POST',
      body: form,
      headers: { Authorization: `Bearer ${token}` }
    })
    nav('/app/enroll/prefs')
  }

  return (
    <div className="p-4 space-y-2 text-center">
      <video ref={videoRef} autoPlay className="mx-auto" onCanPlay={startCamera} width={320} height={240}></video>
      <canvas ref={canvasRef} width={640} height={480} className="hidden" />
      <p>Look {prompts[step]}</p>
      <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={capture}>Capture</button>
    </div>
  )
}

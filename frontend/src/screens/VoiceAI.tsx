import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'

export default function VoiceAI() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [messages, setMessages] = useState<string[]>([])
  const [recording, setRecording] = useState(false)
  const socketRef = useRef<Socket>()
  const mediaRef = useRef<MediaRecorder>()

  useEffect(() => {
    let stream: MediaStream | null = null

    async function init() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        if (videoRef.current) videoRef.current.srcObject = stream
        mediaRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' })
        mediaRef.current.ondataavailable = e => {
          if (socketRef.current && e.data.size > 0) {
            socketRef.current.emit('chunk', e.data)
          }
        }
      } catch (err) {
        alert('Could not access camera/mic: ' + err)
      }
    }
    init()
    return () => {
      mediaRef.current?.stop()
      stream?.getTracks().forEach(track => track.stop())
      socketRef.current?.disconnect()
    }
  }, [])

  function start() {
    if (!mediaRef.current) return
    if (!socketRef.current) {
      socketRef.current = io()
      socketRef.current.on('transcription', (d: { text: string }) => {
        setMessages(prev => [...prev, d.text])
      })
    }
    mediaRef.current.start(1000)
    setRecording(true)
  }

  function stop() {
    mediaRef.current?.stop()
    socketRef.current?.disconnect()
    socketRef.current = undefined
    setRecording(false)
  }

  return (
    <div className="p-4 h-screen flex bg-gray-100">
      <div className="flex-1 flex items-center justify-center">
        <video ref={videoRef} autoPlay playsInline className="rounded-2xl shadow-lg w-full h-full object-cover" />
      </div>
      <div className="flex-1 flex flex-col space-y-2 p-4">
        <div className="flex-1 overflow-y-auto border rounded-2xl bg-white p-4 shadow">
          {messages.length === 0 ? (
            <div className="text-gray-400 text-center mt-8">AI will transcribe your speech here…</div>
          ) : (
            messages.map((m, i) => <div key={i} className="mb-2">{m}</div>)
          )}
        </div>
        <div className="space-y-2 pt-4">
          <button
            onClick={recording ? stop : start}
            className={`px-4 py-2 font-bold rounded-2xl w-full shadow ${
              recording ? 'bg-red-500' : 'bg-blue-600'
            } text-white transition`}
          >
            {recording ? 'Stop Listening' : 'Start Listening'}
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-2xl w-full shadow">Play my Gospel Playlist</button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-2xl w-full shadow">What did I watch yesterday?</button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-2xl w-full shadow">Set Reminder</button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-2xl w-full shadow">TV Controls</button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-2xl w-full shadow">Journal</button>
          <button className="px-4 py-2 bg-red-400 text-white rounded-2xl w-full shadow">Log Out</button>
        </div>
      </div>
    </div>
  )
}

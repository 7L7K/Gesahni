import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'

export default function VoiceAI() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [messages, setMessages] = useState<string[]>([])
  const [recording, setRecording] = useState(false)
  const socketRef = useRef<Socket>()
  const mediaRef = useRef<MediaRecorder>()

  useEffect(() => {
    async function init() {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      if (videoRef.current) videoRef.current.srcObject = stream
      mediaRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' })
      mediaRef.current.ondataavailable = e => {
        if (socketRef.current && e.data.size > 0) {
          socketRef.current.emit('chunk', e.data)
        }
      }
    }
    init()
  }, [])

  function start() {
    if (!mediaRef.current) return
    socketRef.current = io()
    socketRef.current.on('transcription', (d: { text: string }) => {
      setMessages(prev => [...prev, d.text])
    })
    mediaRef.current.start(1000)
    setRecording(true)
  }

  function stop() {
    mediaRef.current?.stop()
    socketRef.current?.disconnect()
    setRecording(false)
  }

  return (
    <div className="p-4 h-screen flex">
      <div className="flex-1">
        <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
      </div>
      <div className="flex-1 flex flex-col space-y-2 p-4">
        <div className="flex-1 overflow-y-auto border p-2">
          {messages.map((m, i) => <div key={i}>{m}</div>)}
        </div>
        <div className="space-y-2">
          <button onClick={recording ? stop : start} className="px-2 py-1 bg-blue-500 text-white rounded w-full">
            {recording ? 'Stop Listening' : 'Start Listening'}
          </button>
          <button className="px-2 py-1 bg-green-500 text-white rounded w-full">Play my Gospel Playlist</button>
          <button className="px-2 py-1 bg-green-500 text-white rounded w-full">What did I watch yesterday?</button>
          <button className="px-2 py-1 bg-green-500 text-white rounded w-full">Set Reminder</button>
          <button className="px-2 py-1 bg-green-500 text-white rounded w-full">TV Controls</button>
          <button className="px-2 py-1 bg-green-500 text-white rounded w-full">Journal</button>
          <button className="px-2 py-1 bg-red-500 text-white rounded w-full">Log Out</button>
        </div>
      </div>
    </div>
  )
}

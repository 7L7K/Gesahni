import { useState, useRef } from 'react'

export default function useRecorder() {
  const [isRecording, setRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRef = useRef<MediaRecorder>()

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRef.current = new MediaRecorder(stream)
    const chunks: BlobPart[] = []
    mediaRef.current.ondataavailable = e => chunks.push(e.data)
    mediaRef.current.onstop = () => {
      setAudioBlob(new Blob(chunks, { type: 'audio/wav' }))
    }
    mediaRef.current.start()
    setRecording(true)
  }

  function stop() {
    mediaRef.current?.stop()
    setRecording(false)
  }

  return { isRecording, start, stop, audioBlob }
}

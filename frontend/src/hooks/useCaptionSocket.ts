import { useEffect, useRef } from 'react'
import { auth } from '../firebase'

export function useCaptionSocket(onText: (t: string) => void) {
  const wsRef = useRef<WebSocket>()

  useEffect(() => {
    let active = true
    const connect = async () => {
      const token = auth.currentUser ? await auth.currentUser.getIdToken() : ''
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${proto}://${location.host}/ws/caption?token=${encodeURIComponent(token)}`
      const ws = new WebSocket(url)
      ws.onmessage = e => onText(e.data)
      ws.onclose = () => { if (active) setTimeout(connect, 1000) }
      wsRef.current = ws
    }
    connect()
    return () => { active = false; wsRef.current?.close() }
  }, [onText])

  const send = (data: Blob | ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(data)
  }

  return { send }
}

import { act, renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import useRecorder from '../useRecorder'

global.MediaRecorder = class {
  ondataavailable: ((e: any) => void) | null = null
  onstop: (() => void) | null = null
  start = vi.fn()
  stop = vi.fn(() => {
    this.ondataavailable?.({ data: new Blob(['a']) })
    this.onstop?.()
  })
  constructor(stream: MediaStream) {}
} as any

global.MediaStream = class {} as any

describe('useRecorder', () => {
  it('records and produces blob', async () => {
    const getUserMedia = vi.fn().mockResolvedValue(new MediaStream())
    // @ts-ignore
    navigator.mediaDevices = { getUserMedia }
    const { result } = renderHook(() => useRecorder())
    await act(async () => {
      await result.current.start()
      result.current.stop()
    })
    expect(getUserMedia).toHaveBeenCalled()
    expect(result.current.isRecording).toBe(false)
    expect(result.current.audioBlob).toBeInstanceOf(Blob)
  })

  it('handles permission denied', async () => {
    const err = new Error('denied')
    const getUserMedia = vi.fn().mockRejectedValue(err)
    // @ts-ignore
    navigator.mediaDevices = { getUserMedia }
    const { result } = renderHook(() => useRecorder())
    await expect(result.current.start()).rejects.toThrow('denied')
  })
})

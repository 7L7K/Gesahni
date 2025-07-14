import { renderHook, act, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import useRecorder from '../hooks/useRecorder'

class MockMediaRecorder {
  ondataavailable: ((e: { data: Blob }) => void) | null = null
  onstop: (() => void) | null = null
  start = vi.fn()
  stop = vi.fn(() => {
    this.ondataavailable?.({ data: new Blob(['a']) })
    this.onstop?.()
  })
  constructor(_stream: MediaStream) {}
}

describe('useRecorder', () => {
  const origGetUserMedia = navigator.mediaDevices?.getUserMedia
  const origMediaRecorder = (global as any).MediaRecorder

  beforeEach(() => {
    Object.defineProperty(navigator, 'mediaDevices', {
      value: { getUserMedia: vi.fn(() => Promise.resolve({} as any)) },
      configurable: true
    })
    ;(global as any).MediaRecorder = MockMediaRecorder as any
  })

  afterEach(() => {
    Object.defineProperty(navigator, 'mediaDevices', {
      value: { getUserMedia: origGetUserMedia },
      configurable: true
    })
    ;(global as any).MediaRecorder = origMediaRecorder
    vi.restoreAllMocks()
  })

  it('start sets isRecording', async () => {
    const { result } = renderHook(() => useRecorder())
    await act(async () => {
      await result.current.start()
    })
    expect(result.current.isRecording).toBe(true)
  })

  it('stop resolves with an audio blob', async () => {
    const { result } = renderHook(() => useRecorder())
    await act(async () => {
      await result.current.start()
    })
    act(() => {
      result.current.stop()
    })
    await waitFor(() => {
      expect(result.current.audioBlob).toBeInstanceOf(Blob)
    })
  })
})

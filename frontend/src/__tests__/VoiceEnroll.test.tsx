import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import VoiceEnroll from '../screens/VoiceEnroll'
import { EnrollContext } from '../context/EnrollContext'
import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

const start = vi.fn()
const stop = vi.fn()
vi.mock('../hooks/useRecorder', () => ({
  default: () => ({ isRecording: false, start, stop, audioBlob: new Blob(['a']) })
}))

describe('VoiceEnroll screen', () => {
  it('uploads voice and navigates to face', async () => {
    const fetchMock = vi.fn(() => Promise.resolve({}))
    // @ts-ignore
    global.fetch = fetchMock
    const ctx = { userId: '123', prefs: {}, setUserId: vi.fn(), setPrefs: vi.fn() }
    render(
      <EnrollContext.Provider value={ctx}>
        <VoiceEnroll />
      </EnrollContext.Provider>
    )
    const btn = screen.getByRole('button')
    fireEvent.mouseDown(btn)
    fireEvent.mouseUp(btn)

    await waitFor(() => expect(stop).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledWith(`/enroll/voice/${ctx.userId}`, expect.any(Object))
    expect(navigate).toHaveBeenCalledWith('/face')
  })
})

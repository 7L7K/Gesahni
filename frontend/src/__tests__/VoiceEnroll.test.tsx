import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import VoiceEnroll from '../screens/VoiceEnroll'
import { EnrollContext } from '../context/EnrollContext'
import { AuthContext } from '../context/AuthContext'
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
    const authCtx = { userId: '123', enrolled: false, token: 'tok', setUserId: vi.fn(), setEnrolled: vi.fn() }
    render(
      <AuthContext.Provider value={authCtx}>
        <EnrollContext.Provider value={ctx}>
          <VoiceEnroll />
        </EnrollContext.Provider>
      </AuthContext.Provider>
    )
    const btn = screen.getByRole('button')
    fireEvent.mouseDown(btn)
    fireEvent.mouseUp(btn)

    await waitFor(() => expect(stop).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledWith(`/api/enroll/voice/${ctx.userId}`, expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer tok' })
    }))
    expect(navigate).toHaveBeenCalledWith('/app/enroll/face')
  })
})

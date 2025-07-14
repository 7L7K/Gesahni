import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Finish from '../screens/Finish'
import { EnrollContext } from '../context/EnrollContext'
import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

describe('Finish screen', () => {
  it('loads audio and navigates home', async () => {
    const fetchMock = vi.fn(() => Promise.resolve({ json: () => Promise.resolve({ audio_url: 'final.mp3' }) }))
    // @ts-ignore
    global.fetch = fetchMock
    const ctx = { userId: 'uid', prefs: {}, setUserId: vi.fn(), setPrefs: vi.fn() }
    const { container } = render(
      <EnrollContext.Provider value={ctx}>
        <Finish />
      </EnrollContext.Provider>
    )

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    await waitFor(() => {
      const audio = container.querySelector('audio')
      expect(audio?.getAttribute('src')).toBe('final.mp3')
    })

    await userEvent.click(screen.getByRole('button'))
    expect(navigate).toHaveBeenCalledWith('/')
  })
})

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PrefSetup from '../screens/PrefSetup'
import { EnrollContext } from '../context/EnrollContext'
import { AuthContext } from '../context/AuthContext'
import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

describe('PrefSetup screen', () => {
  it('saves preferences and navigates to finish', async () => {
    const fetchMock = vi.fn(() => Promise.resolve({}))
    // @ts-ignore
    global.fetch = fetchMock
    const setPrefs = vi.fn()
    const ctx = { userId: 'u1', prefs: {}, setUserId: vi.fn(), setPrefs }
    const authCtx = { userId: 'u1', enrolled: false, token: 'tok', setUserId: vi.fn(), setEnrolled: vi.fn() }
    render(
      <AuthContext.Provider value={authCtx}>
        <EnrollContext.Provider value={ctx}>
          <PrefSetup />
        </EnrollContext.Provider>
      </AuthContext.Provider>
    )

    await userEvent.type(screen.getByPlaceholderText(/name/i), 'Bob')
    await userEvent.type(screen.getByPlaceholderText(/greeting/i), 'Hi')
    await userEvent.click(screen.getByLabelText(/Email/i))
    await userEvent.click(screen.getByRole('button', { name: /save/i }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledWith(`/api/enroll/prefs/${ctx.userId}`, expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer tok' })
    }))
    expect(setPrefs).toHaveBeenCalledWith({ name: 'Bob', greeting: 'Hi', reminder_type: 'email' })
    expect(navigate).toHaveBeenCalledWith('/app/enroll/finish')
  })
})

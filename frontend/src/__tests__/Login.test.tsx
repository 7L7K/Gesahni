import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})
vi.mock('../firebase', () => ({
  auth: { currentUser: { getIdToken: vi.fn(() => Promise.resolve('tok')) } }
}))
vi.mock('firebase/auth', async () => {
  const actual: any = await vi.importActual('firebase/auth')
  return { ...actual, signInAnonymously: vi.fn(() => Promise.resolve()) }
})

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from '../screens/Login'
import { AuthContext } from '../context/AuthContext'
import { EnrollContext } from '../context/EnrollContext'
import { signInAnonymously } from 'firebase/auth'

describe('Login screen', () => {
  it('sends auth token in header', async () => {
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({}) }))
    // @ts-ignore
    global.fetch = fetchMock
    const authCtx = { userId: '', enrolled: false, token: '', setUserId: vi.fn(), setEnrolled: vi.fn() }
    const enrollCtx = { userId: '', prefs: {}, setUserId: vi.fn(), setPrefs: vi.fn() }
    render(
      <AuthContext.Provider value={authCtx}>
        <EnrollContext.Provider value={enrollCtx}>
          <Login />
        </EnrollContext.Provider>
      </AuthContext.Provider>
    )

    await userEvent.type(screen.getByPlaceholderText(/enter your id/i), 'abc')
    await userEvent.click(screen.getByRole('button', { name: /continue/i }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledWith('/api/auth/login', expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer tok' })
    }))
  })
})

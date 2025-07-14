import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Welcome from '../screens/Welcome'
import { EnrollContext, Prefs } from '../context/EnrollContext'
import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

describe('Welcome screen', () => {
  it('sets user id on mount and navigates to voice', async () => {
    const setUserId = vi.fn()
    const context = { userId: '', prefs: {}, setUserId, setPrefs: vi.fn() }
    render(
      <EnrollContext.Provider value={context}>
        <Welcome />
      </EnrollContext.Provider>
    )
    expect(setUserId).toHaveBeenCalledTimes(1)
    const btn = screen.getByRole('button', { name: /let's start/i })
    await userEvent.click(btn)
    expect(navigate).toHaveBeenCalledWith('/voice')
  })
})

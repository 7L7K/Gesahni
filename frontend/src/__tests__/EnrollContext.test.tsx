import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EnrollProvider, EnrollContext } from '../context/EnrollContext'
import { useContext } from 'react'

function Consumer() {
  const { userId, prefs, setUserId, setPrefs } = useContext(EnrollContext)!
  return (
    <div>
      <span data-testid="user">{userId}</span>
      <span data-testid="greeting">{prefs.greeting ?? ''}</span>
      <button onClick={() => setUserId('u2')}>Set User</button>
      <button onClick={() => setPrefs({ greeting: 'hi' })}>Set Prefs</button>
    </div>
  )
}

describe('EnrollProvider', () => {
  it('updates context state via setters', async () => {
    render(
      <EnrollProvider>
        <Consumer />
      </EnrollProvider>
    )
    expect(screen.getByTestId('user').textContent).toBe('')
    expect(screen.getByTestId('greeting').textContent).toBe('')

    await userEvent.click(screen.getByRole('button', { name: /set user/i }))
    expect(screen.getByTestId('user').textContent).toBe('u2')

    await userEvent.click(screen.getByRole('button', { name: /set prefs/i }))
    expect(screen.getByTestId('greeting').textContent).toBe('hi')
  })
})

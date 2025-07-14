import { render, screen, fireEvent } from '@testing-library/react'
import { useContext } from 'react'
import { describe, it, expect } from 'vitest'
import { EnrollProvider, EnrollContext } from '../EnrollContext'

function Consumer() {
  const ctx = useContext(EnrollContext)!
  return (
    <div>
      <span data-testid="uid">{ctx.userId}</span>
      <span data-testid="name">{ctx.prefs.name ?? ''}</span>
      <button onClick={() => ctx.setUserId('user')}>setId</button>
      <button onClick={() => ctx.setPrefs({ name: 'bob' })}>setPrefs</button>
    </div>
  )
}

describe('EnrollContext', () => {
  it('provides default values', () => {
    render(
      <EnrollProvider>
        <Consumer />
      </EnrollProvider>
    )
    expect(screen.getByTestId('uid').textContent).toBe('')
    expect(screen.getByTestId('name').textContent).toBe('')
  })

  it('updates state via setters', () => {
    render(
      <EnrollProvider>
        <Consumer />
      </EnrollProvider>
    )
    fireEvent.click(screen.getByText('setId'))
    fireEvent.click(screen.getByText('setPrefs'))
    expect(screen.getByTestId('uid').textContent).toBe('user')
    expect(screen.getByTestId('name').textContent).toBe('bob')
  })
})

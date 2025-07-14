import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FaceCapture from '../screens/FaceCapture'
import { EnrollContext } from '../context/EnrollContext'
import { vi } from 'vitest'

const navigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigate }
})

describe('FaceCapture screen', () => {
  it.skip('captures images and navigates to prefs', async () => {
    const fetchMock = vi.fn(() => Promise.resolve({}))
    // @ts-ignore
    global.fetch = fetchMock
    const ctx = { userId: 'id1', prefs: {}, setUserId: vi.fn(), setPrefs: vi.fn() }
    const { container } = render(
      <EnrollContext.Provider value={ctx}>
        <FaceCapture />
      </EnrollContext.Provider>
    )

    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ drawImage: vi.fn() } as any)
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation(cb => cb(new File(['img'], 'img.jpg', { type: 'image/jpeg' })))

    const btn = screen.getByRole('button', { name: /capture/i })
    await userEvent.click(btn)
    await waitFor(() => screen.getByText(/look left/i))
    await userEvent.click(btn)
    await waitFor(() => screen.getByText(/look right/i))
    await userEvent.click(btn)

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    expect(fetchMock).toHaveBeenCalledWith(`/enroll/face/${ctx.userId}`, expect.any(Object))
    expect(navigate).toHaveBeenCalledWith('/prefs')
  })
})

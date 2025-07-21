import { vi, expect, test } from 'vitest'
vi.mock('../firebase', () => ({
  auth: { currentUser: { getIdToken: vi.fn(() => Promise.resolve('tok')) } }
}))
import { apiFetch } from '../api'

test('attaches id token', async () => {
  const fetchMock: any = vi.fn(() => Promise.resolve({ ok: true }))
  // @ts-ignore
  global.fetch = fetchMock
  await apiFetch('/x')
  const init = fetchMock.mock.calls[0][1]
  expect(init.headers.get('Authorization')).toBe('Bearer tok')
})

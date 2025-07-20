import '@testing-library/jest-dom'

// Mock Firebase auth to avoid initializing real app during tests
import { vi } from 'vitest'

vi.mock('./src/firebase.js', () => ({
  auth: { currentUser: { getIdToken: vi.fn(() => Promise.resolve('test-token')) } }
}))

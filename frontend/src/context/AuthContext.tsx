import { createContext, useState, ReactNode } from 'react'

interface AuthValue {
  userId: string
  enrolled: boolean
  setUserId: (id: string) => void
  setEnrolled: (b: boolean) => void
}

export const AuthContext = createContext<AuthValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState('')
  const [enrolled, setEnrolled] = useState(false)
  return (
    <AuthContext.Provider value={{ userId, enrolled, setUserId, setEnrolled }}>
      {children}
    </AuthContext.Provider>
  )
}

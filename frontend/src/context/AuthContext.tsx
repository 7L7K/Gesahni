import { createContext, useState, ReactNode, useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../firebase'

interface AuthValue {
  userId: string
  enrolled: boolean
  token: string
  setUserId: (id: string) => void
  setEnrolled: (b: boolean) => void
}

export const AuthContext = createContext<AuthValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState('')
  const [enrolled, setEnrolled] = useState(false)
  const [token, setToken] = useState('')

  useEffect(() => {
    return onAuthStateChanged(auth, async user => {
      if (user) {
        const t = await user.getIdToken()
        setToken(t)
      } else {
        setToken('')
      }
    })
  }, [])
  return (
    <AuthContext.Provider value={{ userId, enrolled, token, setUserId, setEnrolled }}>
      {children}
    </AuthContext.Provider>
  )
}

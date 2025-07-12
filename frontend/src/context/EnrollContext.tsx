import { createContext, useState, ReactNode } from 'react'

export interface Prefs {
  name?: string
  greeting?: string
  reminder_type?: string
}

interface EnrollContextValue {
  userId: string
  prefs: Prefs
  setUserId: (id: string) => void
  setPrefs: (p: Prefs) => void
}

export const EnrollContext = createContext<EnrollContextValue | undefined>(undefined)

export function EnrollProvider({ children }: { children: ReactNode }) {
  const [userId, setUserId] = useState('')
  const [prefs, setPrefs] = useState<Prefs>({})
  return (
    <EnrollContext.Provider value={{ userId, prefs, setUserId, setPrefs }}>
      {children}
    </EnrollContext.Provider>
  )
}

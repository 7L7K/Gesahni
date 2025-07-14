import { useContext, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { AuthContext } from './AuthContext'

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const { userId, enrolled } = useContext(AuthContext)!
  const nav = useNavigate()
  const loc = useLocation()
  useEffect(() => {
    if (!userId) {
      nav('/login')
    } else if (!enrolled && !loc.pathname.startsWith('/app/enroll')) {
      nav('/app/enroll/voice')
    }
  }, [userId, enrolled, loc.pathname])
  return userId ? children : null
}

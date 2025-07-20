import { useContext, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { AuthContext } from './AuthContext'

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const { userId, enrolled, token } = useContext(AuthContext)!
  const nav = useNavigate()
  const loc = useLocation()
  useEffect(() => {
    if (!token) {
      nav('/login')
    } else if (!enrolled && !loc.pathname.startsWith('/app/enroll')) {
      nav('/app/enroll/voice')
    }
  }, [token, enrolled, loc.pathname])
  return token ? children : null
}

// src/App.tsx
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { EnrollProvider } from './context/EnrollContext'
import RequireAuth from './context/RequireAuth'

import Landing     from './screens/Landing'
import Register    from './screens/Register'
import Login       from './screens/Login'
import VoiceEnroll from './screens/VoiceEnroll'
import FaceCapture from './screens/FaceCapture'
import PrefSetup   from './screens/PrefSetup'
import Finish      from './screens/Finish'
import VoiceAI     from './screens/VoiceAI'

export default function App() {
  return (
    <AuthProvider>
      <EnrollProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />

          {/* Protected app routes */}
          <Route path="/app/voice-ai" element={<RequireAuth><VoiceAI /></RequireAuth>} />
          <Route path="/app/enroll/voice" element={<RequireAuth><VoiceEnroll /></RequireAuth>} />
          <Route path="/app/enroll/face" element={<RequireAuth><FaceCapture /></RequireAuth>} />
          <Route path="/app/enroll/prefs" element={<RequireAuth><PrefSetup /></RequireAuth>} />
          <Route path="/app/enroll/finish" element={<RequireAuth><Finish /></RequireAuth>} />
        </Routes>
      </EnrollProvider>
    </AuthProvider>
  )
}

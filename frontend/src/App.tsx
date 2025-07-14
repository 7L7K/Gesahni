// src/App.tsx
import { Routes, Route } from 'react-router-dom'
import { EnrollProvider } from './context/EnrollContext'
import Welcome      from './screens/Welcome'
import VoiceEnroll  from './screens/VoiceEnroll'
import FaceCapture  from './screens/FaceCapture'
import PrefSetup    from './screens/PrefSetup'
import Finish       from './screens/Finish'

export default function App() {
  return (
    <EnrollProvider>     {/* ← Provider only */}
      <Routes>
        <Route path="/"      element={<Welcome />} />
        <Route path="/voice" element={<VoiceEnroll />} />
        <Route path="/face"  element={<FaceCapture />} />
        <Route path="/prefs" element={<PrefSetup />} />
        <Route path="/finish" element={<Finish />} />
      </Routes>
    </EnrollProvider>
  )
}

import { Routes, Route } from 'react-router-dom'
import Welcome from './screens/Welcome'
import VoiceEnroll from './screens/VoiceEnroll'
import FaceCapture from './screens/FaceCapture'
import PrefSetup from './screens/PrefSetup'
import Finish from './screens/Finish'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Welcome />} />
      <Route path="/voice" element={<VoiceEnroll />} />
      <Route path="/face" element={<FaceCapture />} />
      <Route path="/prefs" element={<PrefSetup />} />
      <Route path="/finish" element={<Finish />} />
    </Routes>
  )
}

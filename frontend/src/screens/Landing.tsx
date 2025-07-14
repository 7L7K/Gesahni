import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const nav = useNavigate()
  return (
    <div className="h-screen flex flex-col items-center justify-center text-center space-y-4">
      <h1 className="text-4xl font-bold">Welcome to Grandma AI</h1>
      <div className="space-x-2">
        <button className="px-4 py-2 bg-green-600 text-white rounded" onClick={() => nav('/register')}>Join Grandma AI</button>
        <button className="px-4 py-2 bg-blue-500 text-white rounded" onClick={() => nav('/login')}>Already Joined? Log in!</button>
      </div>
    </div>
  )
}

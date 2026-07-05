import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import { useState, useEffect } from 'react'
import { verifyToken } from './components/api/client'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userName, setUserName] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      async function checkToken() {
        let data = await verifyToken(token)
        if (data.auth) {
          setIsAuthenticated(true)
          setUserName(data.username)
          navigate("/home")
        } else {
          localStorage.removeItem("token")
        }
        setLoading(false)
      }
      checkToken()
    } else {
      setLoading(false)
    }
  },[navigate])

  if (loading) return null

  return (
      <Routes>
        <Route path='/' element={<AuthPage setIsAuthenticated={setIsAuthenticated} setUserName={setUserName}/>} />
        <Route path='/home' element={isAuthenticated ? <HomePage userName={userName}/> : <Navigate to='/' replace />} /> 
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
  )
}
export default App

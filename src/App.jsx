import { Navigate, Route, Routes } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import { useState } from 'react'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userName, setUserName] = useState('')

  return (
      <Routes>
        <Route path='/' element={<AuthPage setIsAuthenticated={setIsAuthenticated} setUserName={setUserName}/>} />
        <Route path='/home' element={isAuthenticated ? <HomePage userName={userName}/> : <Navigate to='/' replace />} /> 
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
  )
}
export default App

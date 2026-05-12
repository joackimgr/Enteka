import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import { useState } from 'react'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  let homePage = function() {
    if (isAuthenticated) {
      return (
        <Route path='/home' element={<HomePage />} />
      )
    }
  }

  return (
      <Routes>
        <Route path='/' element={<AuthPage isAuthenticated={setIsAuthenticated}/>} />
        {homePage()}   
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
  )
}
export default App

import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import AppPage from './pages/AppPage'
import Home from './pages/Home'
import TweetsPage from './pages/TweetsPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/app" element={<AppPage />} />
        <Route path="/tweets" element={<TweetsPage />} />
      </Routes>
    </Router>
  )
}

export default App

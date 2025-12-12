import React, { useState } from 'react'

const providers = [
  { 
    name: 'Google', 
    path: 'google', 
    color: '#4285f4',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24">
        <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
    )
  },
  { 
    name: 'Twitter', 
    path: 'twitter', 
    color: '#0f1419',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24">
        <path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    )
  }
]

// Use runtime config from window.CONFIG (generated at container startup)
const API_BASE_URL = window.CONFIG?.DEPLOYMENT_URL || 'http://localhost:8000'

function Home() {
  const [mode, setMode] = useState('login') // 'login' or 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const handleOAuthLogin = (path) => {
    window.location.href = `${API_BASE_URL}/auth/${path}`
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setStatus('')
    setError('')

    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const details = await response.json()
      setError(details.detail || 'Registration failed')
      return
    }

    setStatus('Registration successful! Check your inbox to validate your account.')
    setPassword('')
  }

  const handlePasswordLogin = async (event) => {
    event.preventDefault()
    setStatus('')
    setError('')

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      redirect: 'follow',
      body: JSON.stringify({ email, password }),
    })

    if (response.redirected) {
      window.location.href = response.url
      return
    }

    if (!response.ok) {
      const details = await response.json()
      setError(details.detail || 'Unable to login')
      return
    }

    setStatus('Logged in successfully! Redirecting...')
  }

  const handleSubmit = mode === 'login' ? handlePasswordLogin : handleRegister

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f4f6fb',
      padding: '24px'
    }}>
      <div style={{
        maxWidth: '400px',
        width: '100%',
        padding: '32px',
        borderRadius: '12px',
        backgroundColor: 'white',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
      }}>
        {/* Mode Toggle Buttons */}
        <div style={{
          display: 'flex',
          marginBottom: '24px',
          borderRadius: '8px',
          overflow: 'hidden',
          border: '1px solid #e0e0e0'
        }}>
          <button
            type="button"
            onClick={() => { setMode('login'); setStatus(''); setError('') }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              backgroundColor: mode === 'login' ? '#fff' : '#f5f5f5',
              color: mode === 'login' ? '#333' : '#888',
              borderBottom: mode === 'login' ? '2px solid #3344dd' : '2px solid transparent',
              transition: 'all 0.2s'
            }}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => { setMode('register'); setStatus(''); setError('') }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              backgroundColor: mode === 'register' ? '#fff' : '#f5f5f5',
              color: mode === 'register' ? '#333' : '#888',
              borderBottom: mode === 'register' ? '2px solid #3344dd' : '2px solid transparent',
              transition: 'all 0.2s'
            }}
          >
            Register
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
            Username or Email
            <input
              type="email"
              placeholder="Enter your username or email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px',
                marginTop: '6px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </label>
          <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
            Password
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              style={{
                width: '100%',
                padding: '12px',
                marginTop: '6px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </label>
          <button type="submit" style={{
            padding: '14px',
            backgroundColor: '#3344dd',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '16px'
          }}>
            {mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        {/* Divider */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          margin: '24px 0',
          color: '#888'
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
          <span style={{ padding: '0 12px', fontSize: '14px' }}>or continue with</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
        </div>

        {/* OAuth Buttons */}
        <div style={{ display: 'flex', gap: '12px' }}>
          {providers.map((provider) => (
            <button
              key={provider.path}
              onClick={() => handleOAuthLogin(provider.path)}
              style={{
                flex: 1,
                padding: '12px',
                fontSize: '14px',
                backgroundColor: '#fff',
                color: '#333',
                border: '1px solid #ddd',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontWeight: 500
              }}
            >
              {provider.icon}
              {provider.name}
            </button>
          ))}
        </div>
      </div>

      {(status || error) && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '12px 16px',
          borderRadius: '8px',
          backgroundColor: status ? '#e8f6ef' : '#fdeaea',
          color: status ? '#1e8449' : '#c0392b',
          boxShadow: '0 4px 10px rgba(0,0,0,0.08)'
        }}>
          {status || error}
        </div>
      )}
    </div>
  )
}

export default Home

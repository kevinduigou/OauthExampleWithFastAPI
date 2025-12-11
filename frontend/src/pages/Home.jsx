import React, { useState } from 'react'

const providers = [
  { name: 'Google', path: 'google', color: '#4285f4' },
  { name: 'Facebook', path: 'facebook', color: '#1877f2' },
  { name: 'Twitter', path: 'twitter', color: '#0f1419' }
]

const API_BASE_URL = 'http://localhost:8000'

function Home() {
  const [registerEmail, setRegisterEmail] = useState('')
  const [registerPassword, setRegisterPassword] = useState('')
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
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
      body: JSON.stringify({ email: registerEmail, password: registerPassword }),
    })

    if (!response.ok) {
      const details = await response.json()
      setError(details.detail || 'Registration failed')
      return
    }

    setStatus('Registration successful! Check your inbox to validate your account.')
    setRegisterPassword('')
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
      body: JSON.stringify({ email: loginEmail, password: loginPassword }),
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
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '20px',
        maxWidth: '1080px',
        width: '100%'
      }}>
        <div style={{
          padding: '24px',
          borderRadius: '12px',
          backgroundColor: 'white',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <h1 style={{ marginBottom: '8px' }}>Sign in</h1>
          <p style={{ marginTop: 0, color: '#555' }}>Use your email and password</p>
          <form onSubmit={handlePasswordLogin} style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
            <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
              Email
              <input
                type="email"
                value={loginEmail}
                onChange={(event) => setLoginEmail(event.target.value)}
                required
                style={{ width: '100%', padding: '10px', marginTop: '6px' }}
              />
            </label>
            <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
              Password
              <input
                type="password"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
                required
                style={{ width: '100%', padding: '10px', marginTop: '6px' }}
              />
            </label>
            <button type="submit" style={{
              padding: '12px',
              backgroundColor: '#3344dd',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}>
              Login
            </button>
          </form>
        </div>

        <div style={{
          padding: '24px',
          borderRadius: '12px',
          backgroundColor: 'white',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <h2 style={{ marginBottom: '8px' }}>Create account</h2>
          <p style={{ marginTop: 0, color: '#555' }}>Receive a validation email via Brevo</p>
          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
            <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
              Email
              <input
                type="email"
                value={registerEmail}
                onChange={(event) => setRegisterEmail(event.target.value)}
                required
                style={{ width: '100%', padding: '10px', marginTop: '6px' }}
              />
            </label>
            <label style={{ textAlign: 'left', fontWeight: 600, color: '#333' }}>
              Password
              <input
                type="password"
                value={registerPassword}
                onChange={(event) => setRegisterPassword(event.target.value)}
                required
                style={{ width: '100%', padding: '10px', marginTop: '6px' }}
              />
            </label>
            <button type="submit" style={{
              padding: '12px',
              backgroundColor: '#22aa66',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}>
              Register & Validate
            </button>
          </form>
        </div>

        <div style={{
          padding: '24px',
          borderRadius: '12px',
          backgroundColor: 'white',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
        }}>
          <h2 style={{ marginBottom: '8px' }}>Or continue with OAuth</h2>
          <p style={{ marginTop: 0, color: '#555' }}>Use your existing provider account</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
            {providers.map((provider) => (
              <button
                key={provider.path}
                onClick={() => handleOAuthLogin(provider.path)}
                style={{
                  padding: '12px 18px',
                  fontSize: '16px',
                  backgroundColor: provider.color,
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                Sign in with {provider.name}
              </button>
            ))}
          </div>
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

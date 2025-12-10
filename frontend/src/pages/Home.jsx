import React from 'react'

const providers = [
  { name: 'Google', path: 'google', color: '#4285f4' },
  { name: 'Facebook', path: 'facebook', color: '#1877f2' },
  { name: 'Twitter', path: 'twitter', color: '#0f1419' }
]

function Home() {
  const handleLogin = (path) => {
    // Redirect to backend OAuth endpoint
    window.location.href = `http://localhost:8000/auth/${path}`
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>OAuth Example</h1>
      <p>Choose a provider to continue</p>
      <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
        {providers.map((provider) => (
          <button
            key={provider.path}
            onClick={() => handleLogin(provider.path)}
            style={{
              padding: '12px 18px',
              fontSize: '16px',
              backgroundColor: provider.color,
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Sign in with {provider.name}
          </button>
        ))}
      </div>
    </div>
  )
}

export default Home

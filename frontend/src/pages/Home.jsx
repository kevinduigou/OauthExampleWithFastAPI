import React from 'react'

function Home() {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = 'http://localhost:8000/auth/google'
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
      <p>Click the button below to sign in with Google</p>
      <button 
        onClick={handleGoogleLogin}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: '#4285f4',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          marginTop: '20px'
        }}
      >
        Sign in with Google
      </button>
    </div>
  )
}

export default Home

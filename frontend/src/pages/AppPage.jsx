import React from 'react'
import JobMonitor from '../components/JobMonitor'

function AppPage() {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      padding: '40px 20px',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>Welcome to the App!</h1>
      <div style={{ textAlign: 'center', width: '100%', maxWidth: '900px' }}>
        <p style={{ color: 'green', fontSize: '18px', marginTop: '20px' }}>
          ✓ Successfully authenticated with OAuth
        </p>
        <p style={{ marginTop: '10px', color: '#666' }}>
          Your access token has been stored in an HttpOnly cookie
        </p>
        
        {/* Job Monitor Component */}
        <JobMonitor />

        {/* Navigation to Tweet Scheduler */}
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          backgroundColor: '#e8f4fd', 
          borderRadius: '8px',
          maxWidth: '500px',
          margin: '30px auto 0'
        }}>
          <h3>🐦 Tweet Scheduler</h3>
          <p style={{ color: '#666', marginBottom: '15px' }}>
            Schedule tweets to be posted at a specific date and time
          </p>
          <a 
            href="/tweets" 
            style={{ 
              display: 'inline-block',
              padding: '10px 20px',
              backgroundColor: '#1da1f2',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '6px',
              fontWeight: 'bold'
            }}
          >
            Go to Tweet Scheduler →
          </a>
        </div>

        {/* Cookie Details */}
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          backgroundColor: '#f5f5f5', 
          borderRadius: '8px',
          maxWidth: '500px',
          margin: '30px auto 0'
        }}>
          <h3>Cookie Details:</h3>
          <ul style={{ textAlign: 'left', lineHeight: '1.8' }}>
            <li>Name: access_token</li>
            <li>HttpOnly: true (protected from JavaScript)</li>
            <li>Secure: false (set to true in production)</li>
            <li>SameSite: lax</li>
            <li>Max Age: 15 minutes</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default AppPage

import React from 'react'
import TweetScheduler from '../components/TweetScheduler'

function TweetsPage() {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      padding: '40px 20px',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>Tweet Scheduler</h1>
      <div style={{ textAlign: 'center', width: '100%', maxWidth: '900px' }}>
        <p style={{ color: '#666', fontSize: '16px', marginTop: '10px' }}>
          Schedule your tweets to be posted at a specific date and time
        </p>
        
        {/* Tweet Scheduler Component */}
        <TweetScheduler />

        {/* Navigation */}
        <div style={{ 
          marginTop: '30px', 
          padding: '20px', 
          backgroundColor: '#f5f5f5', 
          borderRadius: '8px',
          maxWidth: '500px',
          margin: '30px auto 0'
        }}>
          <a 
            href="/app" 
            style={{ 
              color: '#3498db', 
              textDecoration: 'none',
              fontSize: '14px'
            }}
          >
            ← Back to App Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}

export default TweetsPage

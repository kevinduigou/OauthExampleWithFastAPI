import React, { useState, useEffect } from 'react'

function AppPage() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [movies, setMovies] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    // Fetch movies from the backend
    const fetchMovies = async () => {
      try {
        const response = await fetch('http://localhost:8000/movies', {
          credentials: 'include', // Include cookies in the request
        })
        
        if (!response.ok) {
          throw new Error('Failed to fetch movies')
        }
        
        const data = await response.json()
        setMovies(data.movies)
        setUser({ authenticated: true, user_id: data.user_id })
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    fetchMovies()
  }, [])

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        fontFamily: 'Arial, sans-serif'
      }}>
        <p>Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        fontFamily: 'Arial, sans-serif'
      }}>
        <h1>Error</h1>
        <p style={{ color: 'red', marginTop: '20px' }}>{error}</p>
        <p style={{ marginTop: '10px' }}>Please <a href="/">sign in</a> to access this page.</p>
      </div>
    )
  }

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
      {user && user.authenticated ? (
        <div style={{ textAlign: 'center', width: '100%', maxWidth: '900px' }}>
          <p style={{ color: 'green', fontSize: '18px', marginTop: '20px' }}>
            ✓ Successfully authenticated with OAuth
          </p>
          <p style={{ marginTop: '10px', color: '#666' }}>
            Your access token has been stored in an HttpOnly cookie
          </p>
          
          {/* Movies List */}
          <div style={{ 
            marginTop: '40px', 
            padding: '30px', 
            backgroundColor: '#f9f9f9', 
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ marginBottom: '20px', color: '#333' }}>🎬 Best Movies Ever</h2>
            <div style={{ 
              display: 'grid', 
              gap: '15px',
              textAlign: 'left'
            }}>
              {movies.map((movie) => (
                <div 
                  key={movie.id} 
                  style={{ 
                    padding: '15px 20px', 
                    backgroundColor: 'white', 
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    transition: 'transform 0.2s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ margin: '0 0 5px 0', color: '#2c3e50' }}>
                        {movie.id}. {movie.title}
                      </h3>
                      <p style={{ margin: 0, color: '#7f8c8d', fontSize: '14px' }}>
                        Directed by {movie.director} • {movie.year}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
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
      ) : (
        <p>Not authenticated. Please go back and sign in.</p>
      )}
    </div>
  )
}

export default AppPage

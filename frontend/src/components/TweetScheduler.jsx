/**
 * Tweet Scheduler Component for scheduling tweets.
 *
 * This component allows users to:
 * - Enter tweet content
 * - Select a specific date and time
 * - Schedule the tweet for future posting
 * - View and cancel scheduled tweets
 */

import React, { useCallback, useEffect, useState } from 'react'

const API_BASE_URL = 'http://localhost:8000'

function TweetScheduler() {
  const [content, setContent] = useState('')
  const [scheduledDate, setScheduledDate] = useState('')
  const [scheduledTime, setScheduledTime] = useState('')
  const [scheduledTweets, setScheduledTweets] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)

  // Fetch scheduled tweets on component mount
  const fetchScheduledTweets = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tweets/scheduled`, {
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        setScheduledTweets(data.tweets || [])
      }
    } catch (err) {
      console.error('Failed to fetch scheduled tweets:', err)
    }
  }, [])

  useEffect(() => {
    fetchScheduledTweets()
  }, [fetchScheduledTweets])

  const handleScheduleTweet = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccessMessage(null)
    setIsLoading(true)

    if (!content.trim()) {
      setError('Tweet content is required')
      setIsLoading(false)
      return
    }

    if (!scheduledDate || !scheduledTime) {
      setError('Please select both date and time')
      setIsLoading(false)
      return
    }

    // Combine date and time into ISO format
    const scheduledAt = new Date(`${scheduledDate}T${scheduledTime}`).toISOString()

    try {
      const response = await fetch(`${API_BASE_URL}/tweets/schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          content: content.trim(),
          scheduled_at: scheduledAt,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to schedule tweet')
      }

      const data = await response.json()
      setSuccessMessage(`Tweet scheduled successfully! ID: ${data.tweet_id}`)
      setContent('')
      setScheduledDate('')
      setScheduledTime('')
      
      // Refresh the list
      fetchScheduledTweets()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancelTweet = async (tweetId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tweets/${tweetId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to cancel tweet')
      }

      setSuccessMessage('Tweet cancelled successfully')
      fetchScheduledTweets()
    } catch (err) {
      setError(err.message)
    }
  }

  const getStatusBadge = (status) => {
    const colors = {
      pending: { bg: '#3498db', text: 'white' },
      sent: { bg: '#27ae60', text: 'white' },
      failed: { bg: '#e74c3c', text: 'white' },
      cancelled: { bg: '#95a5a6', text: 'white' },
    }
    const color = colors[status] || colors.pending

    return (
      <span style={{
        padding: '4px 12px',
        backgroundColor: color.bg,
        color: color.text,
        borderRadius: '20px',
        fontSize: '12px',
        textTransform: 'capitalize',
      }}>
        {status}
      </span>
    )
  }

  const formatDateTime = (isoString) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleString()
  }

  // Get minimum date/time (now)
  const now = new Date()
  const minDate = now.toISOString().split('T')[0]

  return (
    <div style={{
      backgroundColor: '#f9f9f9',
      borderRadius: '12px',
      padding: '30px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      marginTop: '40px',
    }}>
      <h2 style={{ marginBottom: '20px', color: '#333' }}>
        🐦 Schedule a Tweet
      </h2>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '10px 15px',
          backgroundColor: '#fdeaea',
          color: '#e74c3c',
          borderRadius: '6px',
          marginBottom: '20px',
        }}>
          ❌ {error}
        </div>
      )}

      {/* Success Display */}
      {successMessage && (
        <div style={{
          padding: '10px 15px',
          backgroundColor: '#e8f8f0',
          color: '#27ae60',
          borderRadius: '6px',
          marginBottom: '20px',
        }}>
          ✅ {successMessage}
        </div>
      )}

      {/* Schedule Form */}
      <form onSubmit={handleScheduleTweet}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>
            Tweet Content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            maxLength={280}
            placeholder="What's happening?"
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #ddd',
              fontSize: '16px',
              resize: 'vertical',
              boxSizing: 'border-box',
            }}
          />
          <div style={{ textAlign: 'right', color: '#999', fontSize: '12px', marginTop: '4px' }}>
            {content.length}/280
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>
              Date
            </label>
            <input
              type="date"
              value={scheduledDate}
              onChange={(e) => setScheduledDate(e.target.value)}
              min={minDate}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '16px',
                boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>
              Time
            </label>
            <input
              type="time"
              value={scheduledTime}
              onChange={(e) => setScheduledTime(e.target.value)}
              step="1"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '16px',
                boxSizing: 'border-box',
              }}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '12px 24px',
            backgroundColor: isLoading ? '#95a5a6' : '#1da1f2',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          {isLoading ? '⏳ Scheduling...' : '📅 Schedule Tweet'}
        </button>
      </form>

      {/* Scheduled Tweets List */}
      <div style={{ marginTop: '40px' }}>
        <h3 style={{ marginBottom: '15px', color: '#555' }}>
          📋 Scheduled Tweets ({scheduledTweets.length})
        </h3>

        {scheduledTweets.length === 0 ? (
          <div style={{
            padding: '20px',
            backgroundColor: '#f0f0f0',
            borderRadius: '8px',
            textAlign: 'center',
            color: '#999',
          }}>
            No scheduled tweets yet
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {scheduledTweets.map((tweet) => (
              <div
                key={tweet.id}
                style={{
                  padding: '15px',
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  border: '1px solid #eee',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: '0 0 10px 0', color: '#333', fontSize: '15px' }}>
                      {tweet.content}
                    </p>
                    <div style={{ display: 'flex', gap: '20px', fontSize: '13px', color: '#666' }}>
                      <span>📅 Scheduled: {formatDateTime(tweet.scheduled_at)}</span>
                      {tweet.sent_at && <span>✅ Sent: {formatDateTime(tweet.sent_at)}</span>}
                    </div>
                    {tweet.error_message && (
                      <p style={{ margin: '10px 0 0 0', color: '#e74c3c', fontSize: '13px' }}>
                        ⚠️ {tweet.error_message}
                      </p>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {getStatusBadge(tweet.status)}
                    {tweet.status === 'pending' && (
                      <button
                        onClick={() => handleCancelTweet(tweet.id)}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: '#e74c3c',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '12px',
                        }}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TweetScheduler

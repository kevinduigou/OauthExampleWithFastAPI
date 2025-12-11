/**
 * Job Monitor Component for tracking async job progress.
 *
 * This component demonstrates how to:
 * - Start long-running jobs via API
 * - Monitor job status and progress
 * - Display job metadata in real-time
 * - Handle job completion and errors
 */

import React, { useCallback, useEffect, useRef, useState } from 'react'

const API_BASE_URL = 'http://localhost:8000'

function JobMonitor() {
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState('Not started')
  const [progress, setProgress] = useState(0)
  const [currentItem, setCurrentItem] = useState(0)
  const [totalItems, setTotalItems] = useState(0)
  const [events, setEvents] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState(null)
  
  const timerRef = useRef(null)
  const eventsLogRef = useRef(null)

  // Auto-scroll events log to bottom
  useEffect(() => {
    if (eventsLogRef.current) {
      eventsLogRef.current.scrollTop = eventsLogRef.current.scrollHeight
    }
  }, [events])

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const checkJobStatus = useCallback(async (jobIdToCheck) => {
    if (!jobIdToCheck) return

    try {
      // Get job status
      const statusResponse = await fetch(`${API_BASE_URL}/jobs/${jobIdToCheck}/status`, {
        credentials: 'include',
      })
      
      if (!statusResponse.ok) {
        throw new Error('Failed to get job status')
      }
      
      const statusData = await statusResponse.json()
      setStatus(statusData.status)

      // Get job metadata
      const metaResponse = await fetch(`${API_BASE_URL}/jobs/${jobIdToCheck}/meta`, {
        credentials: 'include',
      })
      
      if (metaResponse.ok) {
        const metaData = await metaResponse.json()
        const metadata = metaData.metadata || {}
        
        setProgress(metadata.progress || 0)
        setCurrentItem(metadata.current_item || 0)
        setTotalItems(metadata.total || 0)
        
        if (metadata.events && Array.isArray(metadata.events)) {
          setEvents(metadata.events)
        }
      }

      // Check if job is finished
      if (['finished', 'failed', 'canceled'].includes(statusData.status)) {
        stopMonitoring()
        setIsRunning(false)
      }
    } catch (err) {
      setError(err.message)
      stopMonitoring()
      setIsRunning(false)
    }
  }, [])

  const startMonitoring = useCallback((jobIdToMonitor) => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    // Call immediately first, then set up interval for subsequent checks
    checkJobStatus(jobIdToMonitor)
    timerRef.current = setInterval(() => {
      checkJobStatus(jobIdToMonitor)
    }, 1000)
  }, [checkJobStatus])

  const stopMonitoring = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const startJob = async () => {
    setError(null)
    setEvents([])
    setProgress(0)
    setCurrentItem(0)
    setTotalItems(0)
    setStatus('Starting...')

    try {
      const response = await fetch(`${API_BASE_URL}/jobs/start?total_items=100`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Failed to start job')
      }

      const data = await response.json()
      setJobId(data.job_id)
      setIsRunning(true)
      setStatus('started')
      
      // Start monitoring this specific job
      startMonitoring(data.job_id)
    } catch (err) {
      setError(err.message)
      setStatus('Error')
    }
  }

  const cancelJob = async () => {
    if (!jobId) return

    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/cancel`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Failed to cancel job')
      }

      stopMonitoring()
      setStatus('canceled')
      setIsRunning(false)
    } catch (err) {
      setError(err.message)
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'finished':
        return '#27ae60'
      case 'failed':
        return '#e74c3c'
      case 'canceled':
        return '#f39c12'
      case 'started':
      case 'processing':
        return '#3498db'
      default:
        return '#7f8c8d'
    }
  }

  return (
    <div style={{
      backgroundColor: '#f9f9f9',
      borderRadius: '12px',
      padding: '30px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      marginTop: '40px',
    }}>
      <h2 style={{ marginBottom: '20px', color: '#333' }}>
        🔄 Long-Running Task Monitor
      </h2>

      {/* Control Buttons */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {!isRunning ? (
          <button
            onClick={startJob}
            style={{
              padding: '10px 20px',
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            ▶️ Start Task
          </button>
        ) : (
          <button
            onClick={cancelJob}
            style={{
              padding: '10px 20px',
              backgroundColor: '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            ⏹️ Cancel Task
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '10px 15px',
          backgroundColor: '#fdeaea',
          color: '#e74c3c',
          borderRadius: '6px',
          marginBottom: '20px',
        }}>
          ❌ Error: {error}
        </div>
      )}

      {/* Status Display */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '20px',
      }}>
        <span style={{ fontWeight: 'bold', color: '#555' }}>Status:</span>
        <span style={{
          padding: '4px 12px',
          backgroundColor: getStatusColor(),
          color: 'white',
          borderRadius: '20px',
          fontSize: '14px',
          textTransform: 'capitalize',
        }}>
          {status}
        </span>
        {jobId && (
          <span style={{ color: '#999', fontSize: '12px' }}>
            (Job ID: {jobId.substring(0, 8)}...)
          </span>
        )}
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '5px',
        }}>
          <span style={{ color: '#555' }}>Progress</span>
          <span style={{ color: '#555' }}>
            {progress}% ({currentItem}/{totalItems} items)
          </span>
        </div>
        <div style={{
          width: '100%',
          height: '20px',
          backgroundColor: '#e0e0e0',
          borderRadius: '10px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            backgroundColor: '#3498db',
            transition: 'width 0.3s ease',
            borderRadius: '10px',
          }} />
        </div>
      </div>

      {/* Events Log */}
      <div>
        <h3 style={{ marginBottom: '10px', color: '#555' }}>📋 Job Events</h3>
        <div
          ref={eventsLogRef}
          style={{
            backgroundColor: '#2c3e50',
            color: '#ecf0f1',
            padding: '15px',
            borderRadius: '8px',
            height: '200px',
            overflowY: 'auto',
            fontFamily: 'monospace',
            fontSize: '13px',
          }}
        >
          {events.length === 0 ? (
            <div style={{ color: '#7f8c8d' }}>No events yet...</div>
          ) : (
            events.map((event, index) => (
              <div key={index} style={{ marginBottom: '4px' }}>
                {event}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default JobMonitor

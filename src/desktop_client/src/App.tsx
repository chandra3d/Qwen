import { useState, useEffect } from 'react'

// Tauri API invoke function (placeholder for actual Tauri integration)
const invoke = async (cmd: string, args?: any) => {
  // @ts-ignore - Tauri will be available at runtime
  if (window.__TAURI__) {
    // @ts-ignore
    return window.__TAURI__.invoke(cmd, args)
  }
  console.log(`[Mock] ${cmd}`, args)
  return true
}

function App() {
  const [connected, setConnected] = useState(false)
  const [recording, setRecording] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState('Disconnected')

  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const checkStatus = async () => {
    try {
      const status: any = await invoke('get_session_status')
      setConnected(status.connected)
      setRecording(status.recording)
      setSessionId(status.session_id)
      setStatusMessage(status.connected ? 'Connected to Backend' : 'Disconnected')
    } catch (error) {
      console.error('Error checking status:', error)
    }
  }

  const handleConnect = async () => {
    try {
      setStatusMessage('Connecting...')
      const result = await invoke('connect_backend')
      if (result) {
        setConnected(true)
        setStatusMessage('Connected to Backend')
      }
    } catch (error) {
      console.error('Connection error:', error)
      setStatusMessage('Connection Failed')
    }
  }

  const handleDisconnect = async () => {
    try {
      setStatusMessage('Disconnecting...')
      const result = await invoke('disconnect_backend')
      if (result) {
        setConnected(false)
        setRecording(false)
        setSessionId(null)
        setStatusMessage('Disconnected')
      }
    } catch (error) {
      console.error('Disconnect error:', error)
    }
  }

  const handleStartRecording = async () => {
    try {
      setStatusMessage('Starting recording...')
      const result = await invoke('start_recording')
      if (result) {
        setRecording(true)
        setSessionId(`session_${Date.now()}`)
        setStatusMessage('Recording Active')
      }
    } catch (error) {
      console.error('Start recording error:', error)
      setStatusMessage('Failed to Start Recording')
    }
  }

  const handleStopRecording = async () => {
    try {
      setStatusMessage('Stopping recording...')
      const result = await invoke('stop_recording')
      if (result) {
        setRecording(false)
        setStatusMessage('Recording Stopped')
      }
    } catch (error) {
      console.error('Stop recording error:', error)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>🎨 Blender AI Copilot</h1>
        <p className="subtitle">Multimodal AI Assistant for Blender</p>
      </header>

      <main className="main-content">
        <div className="status-card">
          <h2>Status</h2>
          <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
            <span className="dot"></span>
            <span>{statusMessage}</span>
          </div>
          
          {sessionId && (
            <div className="session-info">
              <p>Session ID: <code>{sessionId}</code></p>
            </div>
          )}
        </div>

        <div className="controls-card">
          <h2>Controls</h2>
          
          <div className="control-group">
            <h3>Backend Connection</h3>
            {!connected ? (
              <button onClick={handleConnect} className="btn btn-primary">
                Connect to Backend
              </button>
            ) : (
              <button onClick={handleDisconnect} className="btn btn-secondary">
                Disconnect
              </button>
            )}
          </div>

          <div className="control-group">
            <h3>Session Recording</h3>
            <div className="button-row">
              {!recording ? (
                <button 
                  onClick={handleStartRecording} 
                  className="btn btn-success"
                  disabled={!connected}
                >
                  ▶ Start Recording
                </button>
              ) : (
                <button 
                  onClick={handleStopRecording} 
                  className="btn btn-danger"
                >
                  ⏹ Stop Recording
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="info-card">
          <h2>Active Monitoring</h2>
          <ul className="feature-list">
            <li>📺 Screen Capture</li>
            <li>⌨️ Keyboard Tracking</li>
            <li>🖱️ Mouse Tracking</li>
            <li>🎤 Voice Recording</li>
            <li>🧊 Blender State Integration</li>
          </ul>
        </div>
      </main>

      <footer className="footer">
        <p>Blender AI Copilot v0.1.0 | Windows 10+ | Blender 4.5+</p>
      </footer>
    </div>
  )
}

export default App

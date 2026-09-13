import { api } from './desktop'
import { useState } from 'react'
import AnimatedBackground from './components/AnimatedBackground'
import SearchBar from './components/SearchBar'
import VideoOptions from './components/VideoOptions'
import PlaylistView from './components/PlaylistView'
import LoadingState from './components/LoadingState'

function App() {
  const [view, setView] = useState('home');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (link) => {
    setView('loading');
    setError('');

    try {
      const result = await (await api()).analyze(link);

      if (result.type === 'video') {
        setData(result);
        setView('video');
      } else if (result.type === 'playlist') {
        setData(result);
        setView('playlist');
      } else {
        setError(result.message || 'Something went wrong');
        setView('error');
      }
    } catch (err) {
      setError('Failed to analyze the link. Please check the URL and try again.');
      setView('error');
    }
  };

  const handleBack = () => {
    setView('home');
    setData(null);
    setError('');
  };

  return (
    <>
      <AnimatedBackground />
      <div className="app-container">
        <nav className="navbar" onClick={handleBack} role="button" tabIndex={0}>
          <img src="./static/downloader/pictures/Logo.png" alt="S-Downloader" className="nav-logo" />
        </nav>

        <main className="main-content">
          {view === 'home' && (
            <div className="fade-in-up">
              <SearchBar onSubmit={handleSubmit} />
            </div>
          )}

          {view === 'loading' && (
            <div className="fade-in">
              <LoadingState />
            </div>
          )}

          {view === 'video' && data && (
            <div className="fade-in-up">
              <VideoOptions data={data} onBack={handleBack} />
            </div>
          )}

          {view === 'playlist' && data && (
            <div className="fade-in-up">
              <PlaylistView data={data} onSubmit={handleSubmit} onBack={handleBack} />
            </div>
          )}

          {view === 'error' && (
            <div className="fade-in-up error-state">
              <div className="error-icon-wrapper">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
              </div>
              <h2 className="error-title">Oops! Something went wrong</h2>
              <p className="error-message">{error}</p>
              <button className="btn-primary" onClick={handleBack}>
                <span>Try Again</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 4v6h6" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                </svg>
              </button>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>S-Downloader Technology &copy; {new Date().getFullYear()}</p>
        </footer>
      </div>
    </>
  );
}

export default App

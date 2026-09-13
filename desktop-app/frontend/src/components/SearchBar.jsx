import { useState, useRef } from 'react'

function SearchBar({ onSubmit }) {
  const [link, setLink] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (link.trim()) {
      onSubmit(link.trim());
    }
  };

  const handlePaste = async () => {
    try {
      // Try the modern Clipboard API first
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setLink(text);
          return;
        }
      }
    } catch {
      // Permission denied or not available
    }

    // Fallback: focus input, use execCommand paste
    try {
      const input = inputRef.current;
      if (input) {
        input.focus();
        // Clear current value and paste
        input.value = '';
        document.execCommand('paste');
        // Read the pasted value
        if (input.value) {
          setLink(input.value);
          return;
        }
      }
    } catch {
      // execCommand not supported
    }

    // Final fallback: focus the input so user can Ctrl+V manually
    if (inputRef.current) {
      inputRef.current.focus();
      alert('Please press Ctrl+V to paste your link');
    }
  };

  return (
    <div className="hero">
      <h1 className="hero-title">
        Download Videos <span className="gradient-text">Instantly</span>
      </h1>
      <p className="hero-subtitle">
        Paste a YouTube video or playlist link to get started — fast, free, and secure.
      </p>

      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-wrapper">
          <input
            ref={inputRef}
            id="search-input"
            type="text"
            className="search-input"
            placeholder="Paste your YouTube link here..."
            value={link}
            onChange={(e) => setLink(e.target.value)}
            autoComplete="off"
            required
          />
          <button type="button" className="paste-btn" onClick={handlePaste} title="Paste from clipboard">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          </button>
          <button type="submit" className="search-btn" id="analyze-btn">
            <span>Analyze</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </form>

      <div className="features">
        <div className="feature-badge">⚡ Lightning Fast</div>
        <div className="feature-badge">🆓 100% Free</div>
        <div className="feature-badge">🔒 Secure & Private</div>
      </div>
    </div>
  );
}

export default SearchBar

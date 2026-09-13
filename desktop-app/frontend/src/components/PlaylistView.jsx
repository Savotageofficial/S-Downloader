function PlaylistView({ data, onSubmit, onBack }) {
  return (
    <div className="results-page">
      <button className="back-btn" onClick={onBack}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        <span>Back</span>
      </button>

      <div className="playlist-header">
        <h2>{data.title || 'Playlist'}</h2>
        <p className="playlist-duration">
          📀 {data.videos.length} video{data.videos.length !== 1 ? 's' : ''} &nbsp;•&nbsp; ⏱️ {data.length} min total
        </p>
      </div>

      <div className="playlist-grid">
        {data.videos.map((vid, i) => (
          <div className="playlist-card glass-card" key={i}>
            {vid.thumbnail && (
              <img
                className="playlist-thumbnail"
                src={vid.thumbnail}
                alt={vid.title}
                loading="lazy"
              />
            )}
            <div className="playlist-card-body">
              <h4 className="playlist-card-title">{vid.title}</h4>
              <button className="btn-primary" onClick={() => onSubmit(vid.watch_url)}>
                <span>Download</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PlaylistView

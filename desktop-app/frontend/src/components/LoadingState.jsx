function LoadingState() {
  return (
    <div className="loading-state">
      <div className="loading-logo">
        <img src="/static/downloader/pictures/Logo.png" alt="S-Downloader" />
      </div>
      <div className="loading-bar-container">
        <div className="loading-bar-fill" />
      </div>
      <p className="loading-text">
        Analyzing your link<span className="loading-dots" />
      </p>
    </div>
  );
}

export default LoadingState

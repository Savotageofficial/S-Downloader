const logo = new URL('./static/downloader/pictures/Logo.png', document.baseURI).href;

function LoadingState() {
  return (
    <div className="loading-state" role="status" aria-live="polite" aria-busy="true">
      <div className="loading-logo" aria-hidden="true">
        <img className="loading-logo-base" src={logo} alt="" />
        <img className="loading-logo-fill" src={logo} alt="" />
        <img className="loading-logo-wordmark" src={logo} alt="" />
        <span className="loading-logo-shine" style={{ '--logo-mask': `url("${logo}")` }} />
      </div>
      <p className="loading-text">Analyzing your link</p>
      <p className="loading-caption">Finding available video and audio formats</p>
    </div>
  );
}

export default LoadingState;

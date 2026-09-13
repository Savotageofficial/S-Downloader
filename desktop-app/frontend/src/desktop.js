export async function api() {
  if (!window.pywebview?.api) {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Please open S-Downloader Desktop to use this feature.')), 10000)
      window.addEventListener('pywebviewready', () => { clearTimeout(timer); resolve() }, { once: true })
    })
  }
  return window.pywebview.api
}

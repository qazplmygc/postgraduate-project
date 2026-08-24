/** EdgeNexus: local PDF API + online helpers */
(function (global) {
  function isLocalDev() {
    const h = location.hostname;
    return h === '127.0.0.1' || h === 'localhost' || h === '';
  }

  function detectBasePath() {
    const meta = document.querySelector('meta[name="edgenexus-base"]');
    if (meta && meta.content) {
      const b = meta.content.trim();
      return b.endsWith('/') ? b : b + '/';
    }
    const parts = location.pathname.split('/').filter(Boolean);
    const sections = ['search', 'patents', 'reproduce', 'videos', 'waic', 'projects', 'briefing'];
    for (let i = 0; i < parts.length; i++) {
      if (sections.includes(parts[i])) {
        return i === 0 ? '/' : '/' + parts.slice(0, i).join('/') + '/';
      }
    }
    return '/';
  }

  const basePath = detectBasePath();

  function pdfApiUrl(relativePath) {
    if (!relativePath || !isLocalDev()) return null;
    const rel = String(relativePath).replace(/\\/g, '/');
    return basePath.replace(/\/$/, '') + '/api/pdf?path=' + encodeURIComponent(rel);
  }

  function staticAssetUrl(relativeFromRoot) {
    const rel = String(relativeFromRoot).replace(/\\/g, '/').replace(/^\//, '');
    return basePath + rel;
  }

  function openPdfSmart(opts) {
    const o = typeof opts === 'string' ? { path: opts } : (opts || {});
    const api = o.apiPath ? pdfApiUrl(o.apiPath) : pdfApiUrl(o.relativePath || o.path);
    if (api) {
      window.open(api, '_blank', 'noopener');
      return true;
    }
    if (o.staticPath) {
      window.open(staticAssetUrl(o.staticPath), '_blank', 'noopener');
      return true;
    }
    if (o.doi) {
      const d = o.doi.replace(/^https?:\/\/doi\.org\//i, '');
      window.open('https://doi.org/' + d, '_blank', 'noopener');
      return true;
    }
    if (o.filePath && isLocalDev()) {
      window.open('file:///' + String(o.filePath).replace(/\\/g, '/'), '_blank');
      return true;
    }
    alert(
      '在线版无法打开本地 PDF。\n\n' +
      '请在本机运行 search\\open.bat 后打开。' +
      (o.doi ? '\n或尝试 DOI 链接。' : '')
    );
    return false;
  }

  global.EdgeNexus = { isLocalDev, basePath, pdfApiUrl, staticAssetUrl, openPdfSmart };
})(typeof window !== 'undefined' ? window : globalThis);

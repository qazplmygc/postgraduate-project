/** EdgeNexus: local dev vs static hosting (GitHub Pages / Cloudflare Pages) */
(function (global) {
  function isLocalDev() {
    const h = location.hostname;
    return h === '127.0.0.1' || h === 'localhost' || h === '';
  }

  /** GitHub project site base, e.g. /edgenexus/ from /edgenexus/search/index.html */
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

  /** Static file inside repo, e.g. patents/files/x.pdf */
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
      '在线版无法打开本地 PDF 库（D:\\刚需\\…）。\n\n' +
      '• 在家/实验室：双击 search\\open.bat 用本地服务打开\n' +
      (o.doi ? '• 已尝试 DOI 链接；若无 DOI 请在本机查看' : '• 或在本机 EdgeNexus 中打开该条目')
    );
    return false;
  }

  function injectStaticBanner() {
    if (isLocalDev()) return;
    if (document.getElementById('edgenexus-static-banner')) return;
    const bar = document.createElement('div');
    bar.id = 'edgenexus-static-banner';
    bar.style.cssText =
      'background:#fff8e1;border-bottom:1px solid #ffe082;padding:8px 16px;' +
      'font-size:.82rem;color:#5d4037;text-align:center;line-height:1.5;';
    bar.innerHTML =
      '🌐 <strong>在线预览模式</strong> · 检索/笔记/汇报均可浏览 · ' +
      '本地 PDF 需在本机运行 <code style="background:#fff3cd;padding:1px 6px;border-radius:4px">search/open.bat</code>';
    document.body.insertBefore(bar, document.body.firstChild);
  }

  global.EdgeNexus = {
    isLocalDev,
    basePath,
    pdfApiUrl,
    staticAssetUrl,
    openPdfSmart,
    injectStaticBanner,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStaticBanner);
  } else {
    injectStaticBanner();
  }
})(typeof window !== 'undefined' ? window : globalThis);

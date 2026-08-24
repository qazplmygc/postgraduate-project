/** EdgeNexus: local dev vs GitHub Pages / Gitee Pages */
(function (global) {
  const GITEE_PAGES = 'https://qazplmygc.gitee.io/postgraduate-project';
  const GITHUB_PAGES = 'https://qazplmygc.github.io/postgraduate-project';

  function isLocalDev() {
    const h = location.hostname;
    return h === '127.0.0.1' || h === 'localhost' || h === '';
  }

  function hostKind() {
    const h = location.hostname;
    if (isLocalDev()) return 'local';
    if (h.includes('gitee.io')) return 'gitee';
    if (h.includes('github.io')) return 'github';
    if (h.includes('jsdelivr.net') || h.includes('statically.io') || h.includes('raw.githubusercontent.com')) {
      return 'bad-cdn';
    }
    return 'other';
  }

  function detectBasePath() {
    const meta = document.querySelector('meta[name="edgenexus-base"]');
    if (meta && meta.content) {
      const b = meta.content.trim();
      return b.endsWith('/') ? b : b + '/';
    }
    const parts = location.pathname.split('/').filter(Boolean);
    const sections = ['search', 'patents', 'reproduce', 'videos', 'waic', 'projects', 'briefing', 'cn'];
    for (let i = 0; i < parts.length; i++) {
      if (sections.includes(parts[i])) {
        return i === 0 ? '/' : '/' + parts.slice(0, i).join('/') + '/';
      }
    }
    return '/';
  }

  const basePath = detectBasePath();
  const kind = hostKind();

  function pdfApiUrl(relativePath) {
    if (!relativePath || !isLocalDev()) return null;
    const rel = String(relativePath).replace(/\\/g, '/');
    return basePath.replace(/\/$/, '') + '/api/pdf?path=' + encodeURIComponent(rel);
  }

  function staticAssetUrl(relativeFromRoot) {
    const rel = String(relativeFromRoot).replace(/\\/g, '/').replace(/^\//, '');
    return basePath + rel;
  }

  function pagesUrl(section) {
    const path = section.startsWith('/') ? section.slice(1) : section;
    if (kind === 'gitee') return GITEE_PAGES + '/' + path;
    return GITHUB_PAGES + '/' + path;
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
      '• 在家/实验室：双击 search\\open.bat\n' +
      (o.doi ? '• 或点击 DOI 链接' : '• 或在本机 EdgeNexus 打开')
    );
    return false;
  }

  function injectStaticBanner() {
    if (isLocalDev()) return;
    if (document.getElementById('edgenexus-static-banner')) return;

    if (kind === 'bad-cdn') {
      const path = location.pathname.split('/').slice(-2).join('/');
      const target = pagesUrl(path || 'search/index.html');
      location.replace(target);
      return;
    }

    const bar = document.createElement('div');
    bar.id = 'edgenexus-static-banner';
    bar.style.cssText =
      'padding:8px 14px;font-size:.8rem;text-align:center;line-height:1.55;border-bottom:1px solid #ddd;';

    if (kind === 'gitee') {
      bar.style.background = '#e8f5e9';
      bar.style.color = '#1b5e20';
      bar.innerHTML = '✓ <strong>Gitee 国内站</strong> · 本地 PDF 请用 <code style="background:#c8e6c9;padding:1px 6px;border-radius:4px">search/open.bat</code>';
    } else if (kind === 'github') {
      bar.style.background = '#fff8e1';
      bar.style.color = '#5d4037';
      bar.innerHTML =
        'GitHub Pages · 国内慢可改用 <a href="' + GITEE_PAGES + '/search/index.html" style="font-weight:700">Gitee 国内站</a> · ' +
        '<a href="' + GITHUB_PAGES.replace('/search/index.html', '') + '/go.html" style="font-weight:700">访问说明</a>';
    } else {
      bar.style.background = '#fff8e1';
      bar.style.color = '#5d4037';
      bar.innerHTML =
        '在线预览 · 正确入口见 <a href="' + pagesUrl('go.html') + '">go.html</a> · 本地 PDF：<code>search/open.bat</code>';
    }
    document.body.insertBefore(bar, document.body.firstChild);
  }

  global.EdgeNexus = {
    isLocalDev,
    hostKind,
    basePath,
    GITEE_PAGES,
    GITHUB_PAGES,
    pdfApiUrl,
    staticAssetUrl,
    pagesUrl,
    openPdfSmart,
    injectStaticBanner,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStaticBanner);
  } else {
    injectStaticBanner();
  }
})(typeof window !== 'undefined' ? window : globalThis);

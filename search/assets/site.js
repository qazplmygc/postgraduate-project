/** EdgeNexus: local dev vs static hosting (GitHub / jsDelivr / Gitee) */
(function (global) {
  const CDN_ROOT = 'https://cdn.jsdelivr.net/gh/qazplmygc/postgraduate-project@main';
  const GITEE_PAGES = 'https://qazplmygc.gitee.io/postgraduate-project';

  function isLocalDev() {
    const h = location.hostname;
    return h === '127.0.0.1' || h === 'localhost' || h === '';
  }

  function hostKind() {
    const h = location.hostname;
    if (isLocalDev()) return 'local';
    if (h.includes('jsdelivr.net')) return 'cdn';
    if (h.includes('gitee.io')) return 'gitee';
    if (h.includes('github.io')) return 'github';
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

  function mirrorUrl(section) {
    const path = section.startsWith('/') ? section.slice(1) : section;
    return CDN_ROOT + '/' + path;
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
    const bar = document.createElement('div');
    bar.id = 'edgenexus-static-banner';
    bar.style.cssText =
      'background:#fff8e1;border-bottom:1px solid #ffe082;padding:8px 14px;' +
      'font-size:.8rem;color:#5d4037;text-align:center;line-height:1.55;';
    if (kind === 'cdn' || kind === 'gitee') {
      bar.style.background = '#e8f5e9';
      bar.style.borderColor = '#a5d6a7';
      bar.style.color = '#1b5e20';
      bar.innerHTML = '✓ <strong>国内加速</strong> · 无需 VPN · 本地 PDF 请用 <code style="background:#c8e6c9;padding:1px 6px;border-radius:4px">search/open.bat</code>';
    } else if (kind === 'github') {
      bar.style.background = '#ffebee';
      bar.style.borderColor = '#ef9a9a';
      bar.style.color = '#b71c1c';
      bar.innerHTML =
        '⚠ GitHub 在国内较慢 · <a href="' + mirrorUrl('search/index.html') + '" style="color:#c62828;font-weight:700">点此切换国内加速</a>（免 VPN）';
    } else {
      bar.innerHTML =
        '🌐 在线预览 · 本地 PDF 需 <code style="background:#fff3cd;padding:1px 6px;border-radius:4px">search/open.bat</code> · ' +
        '<a href="' + mirrorUrl('search/index.html') + '">国内加速</a>';
    }
    document.body.insertBefore(bar, document.body.firstChild);
  }

  global.EdgeNexus = {
    isLocalDev,
    hostKind,
    basePath,
    CDN_ROOT,
    GITEE_PAGES,
    pdfApiUrl,
    staticAssetUrl,
    mirrorUrl,
    openPdfSmart,
    injectStaticBanner,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStaticBanner);
  } else {
    injectStaticBanner();
  }
})(typeof window !== 'undefined' ? window : globalThis);

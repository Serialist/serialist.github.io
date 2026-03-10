const SITE_CONFIG = {
            PAGE_ROOT: '/page/',
            DEFAULT_PAGE: '/',
            IN_TITLE: "(｡･∀･)ﾉﾞSerialist的博客",
            OUT_TITLE: "┭┮﹏┭┮不要走开",
            ARTICLE_LIST: '/article.json',
            LIGHT_STYLE: 'https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-light.min.css',
            DARK_STYLE: 'https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-dark.min.css'
        };

const mask = document.getElementById('page-mask');

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/**
 * 核心路径转换逻辑
 * 1. 去掉所有 .md 后缀
 * 2. 如果是 / 结尾或为空，代表 index
 * 3. 始终确保返回相对于根目录的干净路径
 */
function resolvePath(rawPath) {
    if (!rawPath) return SITE_CONFIG.DEFAULT_PAGE;
    let path = rawPath.replace(/\.md$/, ''); // 移除 .md
    if (path.endsWith('/index')) path = path.slice(0, -5); // folder/index -> folder/
    if (path.startsWith('/')) path = path.substring(1); // 统一去掉开头的斜杠
    return path;
}

/**
 * 获取实际 fetch 的物理文件路径
 */
function getPhysicalPath(displayPath) {
    if (!displayPath || displayPath.endsWith('/')) {
        return (displayPath || '') + 'index.md';
    }
    return displayPath + '.md';
}

// 核心加载函数
async function loadPage(rawPath) {
    const displayPath = resolvePath(rawPath);

    // 同步浏览器 URL 参数
    const url = new URL(window.location);
    if (url.searchParams.get('p') !== displayPath) {
        url.searchParams.set('p', displayPath);
        window.history.pushState({ path: displayPath }, '', url);
    }

    mask.classList.remove('exit');
    mask.classList.add('active');
    await sleep(500);

    const mainContent = document.getElementById('main-content');
    renderPathNav(displayPath);

    const targetFile = getPhysicalPath(displayPath);

    try {
        const response = await fetch(SITE_CONFIG.PAGE_ROOT + targetFile);
        if (!response.ok) throw new Error('404');

        let mdContent = await response.text();
        // 仅在渲染时过滤掉顶部的 YAML，保留 mdContent 原始变量供其他用途（如需要解析元数据）
        const contentToRender = mdContent.replace(/^---\s*[\s\S]*?\n---\s*/, '');
        mainContent.innerHTML = marked.parse(contentToRender);

        postProcess(mainContent, displayPath);

    } catch (e) {
        // 404 逻辑：尝试寻找当前层级的 404.md
        const dir = targetFile.substring(0, targetFile.lastIndexOf('/') + 1);
        const errorRes = await fetch(SITE_CONFIG.PAGE_ROOT + dir + '404.md');
        const errorText = errorRes.ok ? await errorRes.text() : "# 404\n页面丢失了";
        mainContent.innerHTML = marked.parse(errorText);
    }

    MathJax.typesetPromise([mainContent]).catch(console.error);
    mask.classList.remove('active');
    mask.classList.add('exit');
}

// 渲染自定义模块
function postProcess(container, currentPath) {
    // 友链图标
    container.querySelectorAll('avatar-link').forEach(el => {
        if (typeof Avatar_Link === 'function')
            el.innerHTML = Avatar_Link(el.getAttribute('site-name'), el.getAttribute('stie-url'), el.getAttribute('avatar-url'));
    });

    // 博客列表 - 匹配 blog 或 blog/
    if (currentPath === 'blog' || currentPath === 'blog/') {
        renderBlogList(container);
    }
}

// 博客列表
async function renderBlogList(container) {
    try {
        const res = await fetch(SITE_CONFIG.ARTICLE_LIST);
        const articles = await res.json();

        articles.sort((a, b) => new Date(b.created) - new Date(a.created));

        const groups = {};
        articles.forEach(a => {
            const year = new Date(a.created).getFullYear();
            if (!groups[year]) groups[year] = [];
            groups[year].push(a);
        });

        let html = '<div class="timeline-container">';
        const years = Object.keys(groups).sort((a, b) => b - a);

        years.forEach(year => {
            html += `<h2 class="timeline-year">${year}</h2>`;
            html += '<ul class="timeline-list">';

            groups[year].forEach(a => {
                const dateObj = new Date(a.created);
                const monthDay = `${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;

                // 这里 data-path 不再带 .md
                html += `
                <li class="timeline-item">
                    <span class="timeline-date">${monthDay}</span>
                    <a href="#" data-path="blog/${a.id}">${a.title}</a>
                </li>`;
            });
            html += '</ul>';
        });

        html += '</div>';
        container.innerHTML += html;
    } catch (e) {
        container.innerHTML += '<p>无法加载文章列表</p>';
    }
}

// 路径导航
function renderPathNav(displayPath) {
    const parts = displayPath.split('/').filter(p => p);
    let html = `<a data-path="">首页</a><span>/</span>`;
    let current = "";

    parts.forEach((part, i) => {
        const isLast = i === parts.length - 1;
        // 如果原始路径是以 / 结尾，或者这不是最后一项，则视为目录
        const isDir = displayPath.endsWith('/') || !isLast;
        current += part + (isDir ? "/" : "");

        if (isLast && !displayPath.endsWith('/')) {
            html += `<span>${decodeURIComponent(part)}</span>`;
        } else {
            html += `<a data-path="${current}">${decodeURIComponent(part)}</a><span>/</span>`;
        }
    });
    document.getElementById('path-nav').innerHTML = html;
}

// 统一跳转函数
function navigateTo(path) {
    loadPage(path);
}

window.addEventListener('popstate', () => {
    const params = new URLSearchParams(window.location.search);
    loadPage(params.get('p') || SITE_CONFIG.DEFAULT_PAGE);
});

document.addEventListener('click', e => {
    const link = e.target.closest('[data-path]');
    if (link) {
        e.preventDefault();
        navigateTo(link.getAttribute('data-path'));
    }
});

// 主题逻辑
function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const style = document.getElementById('markdown-style');

    const set = (isDark) => {
        document.body.classList.toggle('dark-mode', isDark);
        if (style) style.href = isDark ? SITE_CONFIG.DARK_STYLE : SITE_CONFIG.LIGHT_STYLE;
        if (icon) icon.setAttribute('name', isDark ? 'dark_mode' : 'light_mode');
        localStorage.setItem('darkMode', isDark);
        syncThemeIcon();
    };

    if (btn) btn.onclick = () => set(!document.body.classList.contains('dark-mode'));

    const isDarkSaved = localStorage.getItem('darkMode') === 'true';
    set(isDarkSaved);
}

function syncThemeIcon() {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        const isDark = document.body.classList.contains('dark-mode');
        icon.innerText = isDark ? 'dark_mode' : 'light_mode';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const params = new URLSearchParams(window.location.search);
    // 首次加载也经过标准路由处理
    loadPage(params.get('p') || SITE_CONFIG.DEFAULT_PAGE);
});

window.onfocus = () => document.title = SITE_CONFIG.IN_TITLE;
window.onblur = () => document.title = SITE_CONFIG.OUT_TITLE;

// 抽屉控制
const drawer = document.getElementById('side-drawer');
const menuBtn = document.getElementById('menu-btn');
const drawerOverlay = document.getElementById('drawer-overlay');

function toggleDrawer(open) {
    if (open) {
        drawer.classList.add('active');
        document.body.style.overflow = 'hidden';
    } else {
        drawer.classList.remove('active');
        document.body.style.overflow = '';
    }
}

menuBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleDrawer(true);
});

drawerOverlay?.addEventListener('click', () => toggleDrawer(false));

drawer?.querySelector('.drawer-links').addEventListener('click', (e) => {
    if (e.target.closest('[data-path]')) {
        toggleDrawer(false);
    }
});
const mask = document.getElementById('page-mask');

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// 核心加载函数
async function loadPage(pagePath) {
    mask.classList.remove('exit');
    mask.classList.add('active');
    await sleep(500);

    const mainContent = document.getElementById('main-content');
    renderPathNav(pagePath);

    try {
        const response = await fetch(SITE_CONFIG.PAGE_ROOT + pagePath);
        if (!response.ok) throw new Error('404');

        let mdContent = await response.text();
        mainContent.innerHTML = marked.parse(mdContent);
        postProcess(mainContent, pagePath);

    } catch (e) {
        const dir = pagePath.substring(0, pagePath.lastIndexOf('/') + 1);
        const errorRes = await fetch(SITE_CONFIG.PAGE_ROOT + dir + '404.md');
        const errorText = errorRes.ok ? await errorRes.text() : "# 404\n页面丢失了";
        mainContent.innerHTML = marked.parse(errorText);
    }

    MathJax.typesetPromise([mainContent]).catch(console.error);
    mask.classList.remove('active');
    mask.classList.add('exit');
}

// 渲染 Markdown
function postProcess(container, currentPath) {
    container.querySelectorAll('avatar-link').forEach(el => {
        if (typeof Avatar_Link === 'function')
            el.innerHTML = Avatar_Link(el.getAttribute('site-name'), el.getAttribute('stie-url'), el.getAttribute('avatar-url'));
    });

    if (currentPath.endsWith('blog.md')) {
        renderBlogList(container);
    }
}

// 博客列表
async function renderBlogList(container) {
    try {
        const res = await fetch('/articles.json');
        const articles = await res.json();

        // 1. 按日期倒序排列
        articles.sort((a, b) => new Date(b.created) - new Date(a.created));

        // 2. 按年份分组
        const groups = {};
        articles.forEach(a => {
            const year = new Date(a.created).getFullYear();
            if (!groups[year]) groups[year] = [];
            groups[year].push(a);
        });

        // 3. 构建 HTML
        let html = '<div class="timeline-container">';

        // 获取排序后的年份（从新到旧）
        const years = Object.keys(groups).sort((a, b) => b - a);

        years.forEach(year => {
            html += `<h2 class="timeline-year">${year}</h2>`;
            html += '<ul class="timeline-list">';

            groups[year].forEach(a => {
                // 提取月-日格式，例如 "03-04"
                const dateObj = new Date(a.created);
                const monthDay = `${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;

                html += `
                <li class="timeline-item">
                    <span class="timeline-date">${monthDay}</span>
                    <a href="#" class="timeline-link" data-path="blog/${a.id}.md">${a.title}</a>
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
function renderPathNav(pagePath) {
    const parts = decodeURIComponent(pagePath).split('/');
    let html = `<a data-path="${SITE_CONFIG.DEFAULT_PAGE}">首页</a><span>/</span>`;
    let current = "";
    parts.forEach((part, i) => {
        if (i === parts.length - 1) {
            html += `<span>${part}</span>`;
        } else {
            current += part + "/";
            html += `<a data-path="${current}index.md">${part}</a><span>/</span>`;
        }
    });
    document.getElementById('path-nav').innerHTML = html;
}

// 路径导航点击事件
function navigateTo(path) {
    const url = new URL(window.location);
    url.searchParams.set('p', path);
    window.history.pushState({ path }, '', url);
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

// 主题切换逻辑完善
function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const style = document.getElementById('markdown-style');

    const set = (isDark) => {
        document.body.classList.toggle('dark-mode', isDark);
        style.href = isDark ? SITE_CONFIG.DARK_STYLE : SITE_CONFIG.LIGHT_STYLE;
        // 图标
        icon.setAttribute('name', isDark ? 'dark_mode' : 'light_mode');
        localStorage.setItem('darkMode', isDark);
    };

    btn.onclick = () => set(!document.body.classList.contains('dark-mode'));

    // 检查 cookie 中保存的主题
    const isDarkSaved = localStorage.getItem('darkMode') === 'true';
    set(isDarkSaved);
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const params = new URLSearchParams(window.location.search);
    loadPage(params.get('p') || SITE_CONFIG.DEFAULT_PAGE);
});

// 标题切换效果
window.onfocus = () => document.title = SITE_CONFIG.IN_TITLE;
window.onblur = () => document.title = SITE_CONFIG.OUT_TITLE;

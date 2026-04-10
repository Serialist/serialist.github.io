/**
 * 核心配置与状态管理
 */
const mask = document.getElementById('page-mask');
const mainContent = document.getElementById('main-content');

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

/**
 * 路径转换逻辑：规范化 URL 路径
 */
function resolvePath(rawPath) {
	if (!rawPath) return SITE_CONFIG.DEFAULT_PAGE;
	let path = rawPath.replace(/\.md$/, '');
	if (path.endsWith('/index')) path = path.slice(0, -6); // 修复原逻辑 index 长度计算
	if (path.startsWith('/')) path = path.substring(1);
	return path;
}

/**
 * 获取物理文件路径
 */
function getPhysicalPath(displayPath) {
	if (!displayPath || displayPath.endsWith('/')) {
		return (displayPath || '') + 'index.md';
	}
	return displayPath + '.md';
}

/**
 * 公式保护与还原工具
 */
const MathProtector = {
	blockMath: [],
	inlineMath: [],

	protect(md) {
		this.blockMath = [];
		this.inlineMath = [];

		return md.replace(/(```[\s\S]*?```|`[^`\n]+`)|(\$\$[\s\S]+?\$\$)|(\$[^$\n]+\$)/g, (match, code, block, inline) => {
			// 如果代码块，不动，防止代码块被误处理
			if (code) return code;

			// 如果行间公式
			if (block) {
				const formula = block.slice(2, -2);
				const index = this.blockMath.length;
				this.blockMath.push(`$$ \n\\displaylines{${formula}} \n$$`);
				return `\n\n<div id="BLOCK_MATH_${index}"></div>\n\n`;
			}

			// 如果行内公式
			if (inline) {
				const formula = inline.slice(1, -1);
				// 如果只有一个$就跳过
				if (formula.trim().length === 0) return inline;
				const index = this.inlineMath.length;
				this.inlineMath.push(`$${formula}$`);
				return `INLINE_MATH_${index}`;
			}

			return match;
		});
	},

	restore(html) {
		// 还原行内
		this.inlineMath.forEach((math, i) => {
			html = html.replace(`INLINE_MATH_${i}`, math);
		});
		return html;
	},

	restoreBlocks(container) {
		// 还原块级
		this.blockMath.forEach((math, i) => {
			const el = container.querySelector(`#BLOCK_MATH_${i}`);
			if (el) el.outerHTML = math;
		});
	}
};

/**
 * 页面加载核心函数
 */
async function loadPage(rawPath) {
	const displayPath = resolvePath(rawPath);

	// 1. URL 状态同步
	const url = new URL(window.location);
	if (url.searchParams.get('p') !== displayPath) {
		url.searchParams.set('p', displayPath);
		window.history.pushState({ path: displayPath }, '', url);
	}

	// 2. 切换动画：显示遮罩
	mask.classList.remove('exit');
	mask.classList.add('active');
	await sleep(300);

	const renderer = new marked.Renderer();
	renderer.code = ({ text, lang }) => {
		return `<pre class="tex2jax_ignore"><code class="language-${lang}">${text}</code></pre>`;
	};

	renderPathNav(displayPath);
	const targetFile = getPhysicalPath(displayPath);

	try {
		const response = await fetch(SITE_CONFIG.PAGE_ROOT + targetFile);
		if (!response.ok) throw new Error('404');

		let mdContent = await response.text();

		mdContent = MathProtector.protect(mdContent);

		// 解析 Markdown
		// let htmlResult = marked.parse(mdContent, { renderer });
		let htmlResult = marked.parse(mdContent);

		// 还原行内公式并注入 DOM
		mainContent.innerHTML = MathProtector.restore(htmlResult);

		// 还原块级公式
		MathProtector.restoreBlocks();

		// 渲染 Mermaid
		if (window.mermaid) {
			await mermaid.run({
				nodes: mainContent.querySelectorAll('.language-mermaid')
			}).catch(err => console.error('Mermaid Error:', err));
		}

		postProcess(mainContent, displayPath);

	} catch (e) {
		console.error(e);
		await renderError(targetFile);
	}

	// 4. 渲染 MathJax
	if (window.MathJax) {
		MathJax.typesetClear([mainContent]);
		MathJax.typesetPromise([mainContent]).catch(console.error);
	}

	// 5. 切换动画：隐藏遮罩
	mask.classList.remove('active');
	mask.classList.add('exit');
}

/**
 * 错误处理渲染
 */
async function renderError(targetFile) {
	const dir = targetFile.substring(0, targetFile.lastIndexOf('/') + 1);
	const errorRes = await fetch(SITE_CONFIG.PAGE_ROOT + dir + '404.md');
	const errorText = errorRes.ok ? await errorRes.text() : "# 404\n页面丢失了";
	mainContent.innerHTML = marked.parse(errorText);
}

/**
 * 后处理插件逻辑
 */
function postProcess(container, currentPath) {
	container.querySelectorAll('avatar-link').forEach(el => {
		if (typeof Avatar_Link === 'function') {
			el.innerHTML = Avatar_Link(
				el.getAttribute('site-name'),
				el.getAttribute('stie-url'),
				el.getAttribute('avatar-url')
			);
		}
	});

	if (currentPath.replace(/\/$/, '') === 'blog') {
		renderBlogList(container);
	}
}

/**
 * 渲染博客列表
 */
async function renderBlogList(container) {
	try {
		const res = await fetch('/articles.json');
		const articles = await res.json();
		articles.sort((a, b) => new Date(b.created) - new Date(a.created));

		const groups = articles.reduce((acc, a) => {
			const year = new Date(a.created).getFullYear();
			if (!acc[year]) acc[year] = [];
			acc[year].push(a);
			return acc;
		}, {});

		let html = '<div class="timeline-container">';
		Object.keys(groups).sort((a, b) => b - a).forEach(year => {
			html += `<h2 class="timeline-year">${year}</h2><ul class="timeline-list">`;
			groups[year].forEach(a => {
				const date = new Date(a.created);
				const monthDay = `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
				html += `
                <li class="timeline-item">
                    <span class="timeline-date">${monthDay}</span>
                    <a href="#" data-path="blog/${a.id}">${a.title}</a>
                </li>`;
			});
			html += '</ul>';
		});
		container.innerHTML += html + '</div>';
	} catch (e) {
		container.innerHTML += '<p>无法加载文章列表</p>';
	}
}

/**
 * 路径导航条
 */
function renderPathNav(displayPath) {
	const parts = displayPath.split('/').filter(p => p);
	let html = `<a data-path="">首页</a><span>/</span>`;
	let current = "";

	parts.forEach((part, i) => {
		const isLast = i === parts.length - 1;
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

/**
 * 主题管理
 */
const ThemeManager = {
	btn: document.getElementById('theme-toggle'),
	icon: document.getElementById('theme-icon'),
	style: document.getElementById('markdown-style'),

	init() {
		const isDarkSaved = localStorage.getItem('darkMode') === 'true';
		this.set(isDarkSaved);
		if (this.btn) this.btn.onclick = () => this.set(!document.body.classList.contains('dark-mode'));
	},

	set(isDark) {
		document.body.classList.toggle('dark-mode', isDark);
		if (this.style) this.style.href = isDark ? SITE_CONFIG.DARK_STYLE : SITE_CONFIG.LIGHT_STYLE;
		if (this.icon) {
			this.icon.setAttribute('name', isDark ? 'dark_mode' : 'light_mode');
			this.icon.innerText = isDark ? 'dark_mode' : 'light_mode';
		}
		localStorage.setItem('darkMode', isDark);
	}
};

/**
 * 事件监听与初始化
 */
document.addEventListener('click', e => {
	const link = e.target.closest('[data-path]');
	if (link) {
		e.preventDefault();
		loadPage(link.getAttribute('data-path'));
	}
});

window.addEventListener('popstate', () => {
	const params = new URLSearchParams(window.location.search);
	loadPage(params.get('p') || SITE_CONFIG.DEFAULT_PAGE);
});

document.addEventListener('DOMContentLoaded', () => {
	ThemeManager.init();
	const params = new URLSearchParams(window.location.search);
	loadPage(params.get('p') || SITE_CONFIG.DEFAULT_PAGE);
});

// 侧边栏逻辑
const drawer = {
	el: document.getElementById('side-drawer'),
	overlay: document.getElementById('drawer-overlay'),
	toggle(open) {
		this.el?.classList.toggle('active', open);
		document.body.style.overflow = open ? 'hidden' : '';
	}
};

document.getElementById('menu-btn')?.addEventListener('click', (e) => {
	e.stopPropagation();
	drawer.toggle(true);
});

drawer.overlay?.addEventListener('click', () => drawer.toggle(false));
drawer.el?.querySelector('.drawer-links').addEventListener('click', (e) => {
	if (e.target.closest('[data-path]')) drawer.toggle(false);
});

window.onfocus = () => document.title = SITE_CONFIG.IN_TITLE;
window.onblur = () => document.title = SITE_CONFIG.OUT_TITLE;
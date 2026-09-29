/**
 * 静态站点的纯 UI 逻辑：主题切换、侧边抽屉、标题闪烁、Mermaid/MathJax 渲染触发。
 * 正文内容已在构建时由 build.js 预渲染为 HTML，这里不再做 markdown 解析。
 */

// 主题管理
const ThemeManager = {
	btn: document.getElementById('theme-toggle'),
	icon: document.getElementById('theme-icon'),
	style: document.getElementById('markdown-style'),

	init() {
		const isDarkSaved = localStorage.getItem('darkMode') === 'true';
		this.set(isDarkSaved);
		if (this.btn) this.btn.onclick = () => this.set(!document.documentElement.classList.contains('dark-mode'));
	},

	set(isDark) {
		document.documentElement.classList.toggle('dark-mode', isDark);
		if (this.style) this.style.href = isDark ? SITE_CONFIG.DARK_STYLE : SITE_CONFIG.LIGHT_STYLE;
		if (this.icon) {
			this.icon.setAttribute('name', isDark ? 'dark_mode' : 'light_mode');
			this.icon.innerText = isDark ? 'dark_mode' : 'light_mode';
		}
		localStorage.setItem('darkMode', isDark);
	}
};

// 侧边抽屉
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
drawer.el?.querySelector('.drawer-links')?.addEventListener('click', (e) => {
	if (e.target.closest('a')) drawer.toggle(false);
});

// 标题闪烁
window.onfocus = () => { document.title = SITE_CONFIG.IN_TITLE; };
window.onblur = () => { document.title = SITE_CONFIG.OUT_TITLE; };

// 右下角看板娘 gif：宽屏显示、窄屏隐藏（从原 inline onload 抽出）
const kawaii = document.getElementById('sirinkawaii');
if (kawaii) {
	const checkKawaii = () => { kawaii.style.display = window.innerWidth >= 768 ? 'block' : 'none'; };
	if (kawaii.complete) checkKawaii();
	else kawaii.addEventListener('load', checkKawaii);
	window.addEventListener('resize', checkKawaii);
}

// 初始化与渲染触发
document.addEventListener('DOMContentLoaded', () => {
	ThemeManager.init();

	// MathJax 公式（保留浏览器渲染）
	const runMath = () => {
		if (window.MathJax) {
			MathJax.typesetClear();
			MathJax.typesetPromise().catch(console.error);
		}
	};

	// Mermaid 图表（保留浏览器渲染），完成后渲染公式（顺序与原 global.js 一致）
	if (window.mermaid) {
		mermaid.run({
			nodes: document.querySelectorAll('.language-mermaid')
		}).catch((err) => console.error('Mermaid Error:', err)).finally(runMath);
	} else {
		runMath();
	}
});

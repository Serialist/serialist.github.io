/**
 * config.js —— 站点全局配置（从页面内联 script 抽出，减少 HTML 体积、利于 SEO）
 * 加载顺序：mermaid（可选）→ config.js → mathjax（可选）→ site.js（defer）
 */

const SITE_CONFIG = {
	PAGE_ROOT: '/page/',
	DEFAULT_PAGE: '/',
	IN_TITLE: "(｡･∀･)ﾉﾞSerialist的博客",
	OUT_TITLE: "┭┮﹏┭┮不要走开",
	LIGHT_STYLE: 'https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-light.min.css',
	DARK_STYLE: 'https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-dark.min.css'
};

// MathJax 配置需在 mathjax 脚本加载前就绪
window.MathJax = {
	tex: {
		inlineMath: [['$', '$'], ['\\(', '\\)']],
		displayMath: [['$$', '$$'], ['\\[', '\\]']],
		processEscapes: true
	},
	options: {
		skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'annotation', 'annotation-xml'],
	}
};

// Mermaid 配置需在 mermaid 脚本加载后就绪（仅当本页含图表时才加载 mermaid）
if (window.mermaid) {
	mermaid.initialize({
		startOnLoad: false, // 动态页面必须为 false
		theme: 'default',
		securityLevel: 'loose'
	});
}

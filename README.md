# Serialist 的博客网站

这里是 Serialist 的博客网站，基于 Gemini 和手搓，目标是写出最轻量的博客网站。

已加入 [开往](https://www.travellings.cn/go.html) 和 [萌 ICP](https://icp.gov.moe/?keyword=20261207)，欢迎加入！

## 网站结构

assets 文件夹储存 css、js 和图片等资源文件。

page 为放置 markdown 文件的根目录，其中的 index.md 是网站的实际首页。（不过其实哪里都可以访问就是 www）

网站为静态，不使用前端框架，样式借用 github markdown 样式。markdown 渲染使用 markded.js，tex 公式渲染使用 Mathjax。

网站使用单页面结构，通过 url?p=\<markdown path\> 的格式接口，获得 /page 文件夹下的 md 文件并渲染。

## 目前实现的功能

- 支持行内，行间 tex 数学公式渲染

- 朴素的切换页面转场动画

- 白天/黑天颜色主题切换

- 电脑/手机多端显示适配，包括窄屏端自动添加抽屉形式的目录

- 一个可带图标和名称的卡片小零件，用于显示友链


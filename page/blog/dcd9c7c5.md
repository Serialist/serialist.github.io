# CSS 入门

## CSS是什么

CSS 定义了**如何显示** HTML 元素。

因为多个样式定义可层叠为一个，所以叫层叠样式表（**C**ascading **S**tyle **S**heets）。

> CSS在[MDN](https://developer.mozilla.org/zh-CN/docs/Web/CSS)上的定义：
>
> **层叠样式表**（Cascading Style Sheets，缩写为 **CSS**）是一种样式表语言，用来描述 HTML 或 XML（包括如 SVG、MathML 或 XHTML 之类的 XML 分支语言）文档的呈现方式。CSS 描述了在屏幕、纸质、音频等其他媒体上的元素应该如何被渲染的问题。

## 为什么用CSS

CSS可以从HTML中**分离出样式的定义**。

- 浏览器（Netscape 和 Internet Explorer）**曾**不断地向 HTML 规范中添加新的**标签**和**属性**（比如字体标签和颜色属性），使**文档内容难以阅读**。HTML 4.0 中添加了样式，实现了**内容**与**表现**分离
- 外部样式表可以极大提高工作效率，只编辑一个 CSS 文档就可以改变所有页面的布局和外观

## 基本语法

### 规则集

css的基本元素是**规则集**（ruleset，简称为**规则**）。一段css代码可以有多个规则。

```css
rule
rule
```

一条规则包括**选择器**（selector）和**声明**（declaration）。声明可以有多个。

- 声明应在成对的大括号里（`{}`）
- 在规则集里，声明要用分号（`;`）分隔

```css
selector {
    declaration;
    declaration;
}
selector {
    declaration;
    declaration;
}
```

一个声明包括**属性**（properties）和**属性值**（property value）。

- 属性与属性值要用冒号（`:`）分隔
- 声明用分号（ ; ）结尾

```css
selector {
    properties: property_value;
    properties: property_value;
}
selector {
    properties: property_value;
    properties: property_value;
}
```

### 注释

CSS的注释标注在 /* 和 */ 之间，可以换行。



最后来看一段完整的css代码。

```css
/*注释1*/
mytag {
    color: red;
    width: 256px;
}
.myClass {
    /*注释2*/
    color: blue;
    heigth: 64px;
}
#myID {
    color: yellow;
    heigth: 16px;
}
```
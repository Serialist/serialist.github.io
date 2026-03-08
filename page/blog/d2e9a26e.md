# 卷积和拉普拉斯变换

对于自动控制理论，我们的讨论都是在线性时不变系统下进行的。

## 线性时不变系统

线性时不变系统（LTI System）有两个性质，线性（**L**inear）和时不变（**T**ime **I**nvariant）。

对于输入 $f(t)$ 和输出 $x(t)$，设有系统为 $O()$，即 $O(f(t)) = x(t)$。

**线性**（linear），即满足叠加原理，即满足：
$$
O\{\ a_1\cdot f_1(t) \ +\ a_2 \cdot f_2(t) \ \} = a_1 \cdot x_1(y) + a_2 \cdot x_2(t)
$$
就是线性的。

**时不变**（time invariant），即无论在什么时间点，输入相同，输出就相同：
$$
O\{ f(t) \} = x(t) \Rightarrow O\{ f(t - \tau) \} = x(t - \tau)
$$

时不变系统，也称为定常系统。

## 线性时不变系统的性质

一个弹簧阻尼系统，就是经典的 LTI 系统。

在弹簧上有一个物块，施加力 $f(t)$，输出位移 $x(t)$。

$f(t)$、$x(t)$ 的拉氏变换为 $F(s)$、$X(s)$，有：
$$
F(s)H(s) = X(s)
$$
 其中 $H(s)$ 是传递函数的拉氏变换。

对两边进行拉普拉斯逆变换：
$$
\mathcal{L}^{-1}[\ F(s)H(s)\ ] = \mathcal{L}^{-1}[\ X(s) \ ]
$$
得到：
$$
f(t) * h(t) = x(t)
$$
其中 $*$ 表示卷积

可见卷积和和内积有拉普拉斯变换的关系

那么什么是卷积？

## 冲激函数

在推导卷积之前，引入冲激函数（Unit Impulse，或狄拉克函数 Dirac Delta）。它在计算时可以起到类似 “单位 1” 的作用。

定义一个函数 $\delta(t)$，满足：
$$
\delta(t) = 0, t \neq 0 \\
且 \int^{\infty}_{-\infty} \delta(t)dt = 1
$$
$\delta(t)$ 就叫做冲激函数，它的面积为 1、宽度为 0。

为了方便理解，可以写成离散的形式：
$$
\delta(t) \quad = \quad
\lim_{\Delta T \rightarrow 0} \delta_\Delta(t) \quad = \quad
\delta_{\Delta}(t) \quad = \quad
\left\{\begin{array}{lc}
\frac1{\Delta T} & 0 < t < \Delta T \\
0 & else \\
\end{array}\right. \\
$$
在坐标系中，它实际上就是宽度为 $\Delta T$，高度为 $\frac{1}{\Delta T}$ 的矩形。当 $\Delta T \rightarrow 0$， 它就是冲击函数。

![QQ_1759822983594](..\..\src\QQ_1759822983594.png)
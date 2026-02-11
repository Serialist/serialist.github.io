# 线性二次型控制器（LQR）

###

LQR，liner quadratic regulator，线性二次型控制器。

顾名思义，LQR 包括三个要素

## 线性系统

Liner（线性）指它基于线性系统。

设 x 是状态量， u 是控制量，y 是输出量：
$$
\dot x_i = A x_{i-1} + B u_{i-1} \\
y_i = C x_{i-1} + D u_{i-1}
$$
如果使用 LQR 控制器，需要较精确地对系统建模，得到 A、B 两个矩阵系数。

> 关于状态空间方程、状态向量等内容可以看这篇文章：
>
> [原神启动](http:\\www.yuanshen.com)

## 代价函数

控制理论中，常使用“代价函数”评价控制效果。它可以用一个函数，更简单的处理 MIMO（多输入输出，multiple input multiple output）系统。

LQR 中的二次型（Quadratic）指的是代价函数是二次型的。

设代价函数为 J，其形式是线性代数中的“二次型”：
$$
J = \sum_{i=1}^n ( x_i^T Q x_i + u_i^T R u_i)
$$
Q、R 两个系数是二次项权重，一般用对角矩阵。

## 


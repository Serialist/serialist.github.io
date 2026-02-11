# 模、余数、取整

## 取整

取模包括很多种。

- floor 向下取整（数学符号：$\lfloor x \rfloor$）

  ```
  floor(3.14) = 3
  floor(-3.14) = -4
  ```

- ceil 向上取整（数学符号：$\lceil x \rceil$）

  ```
  ceil(3.14) = 4
  ceil(-3.14) = -3
  ```

- round 四舍五入（你会的）

- trunc 截断取整：直接抛弃小数部分

  ```
  trunc(3.14) = 3
  trunc(-3.14) = -3
  ```

## 模和余数

数论中，求余数（remainder）和取模运算（mod）是完全相同的：
$$
remainder = a \mod b = a - b \lfloor \frac ab \rfloor
$$
编程实现应当为：

```
a - b * floor(a / b)
```

但是在编程语言中的实现却不是这样。

C 语言 math 库的 fmod 函数，实际相当于：

```
a - b * trunc(a / b)
```

另一个 remainder 函数，相当于：

```
a - b * round(a / b)
```

## 其他（？）

### 其他语言的取模

把任意角（范围无穷）限制在一个周期里（0 到 360），本质就是取模。

但在 c 语言， -90 度得到了：

```
fmod(-90, 360) = -90
```

在 python 却得到了 270：

```
>> -90 % 360
270
```

而 python 的 math 库实现的 fmod 和 C 语言结果相同：

```
>> import math
>> math.fmod(-90, 360)
-90
```

实际上，java、javascript 和 C 语言相同，而 python 默认取模、matlab 均是标准定义。

（~~我说 python 是对的~~）

### 银行家舍入法

>[IEEE 754 - HandWiki - 定向四舍五入](https://handwiki.org/wiki/IEEE_754#Roundings_to_nearest)

银行家舍入法，统计学和商业上用于减少误差，同样定义在 IEEE 754 中。

在某个要舍入的位上（四舍六入五成双）：

1. 此位小于 5 舍去
2. 此位大于 5 进位
3. 若后面位中存在非零，进位
4. 等于 5 且后面位均为 0，则看前一位数字，奇数进位，偶数舍去

### C 其他的取整函数

还有 nearbyint 和 rint，它们默认使用银行家舍入。（似乎也可在库中改为其他舍入方式）

他们的区别仅在于，rint 在发现精度损失时会报错：

> [rint(3): round to nearest integer - Linux man page](https://linux.die.net/man/3/rint):
>
> The **rint**() functions do the same, but will raise the *inexact* exception (**FE_INEXACT**, checkable via **[fetestexcept](https://linux.die.net/man/3/fetestexcept)**(3)) when the result differs in value from the argument.

### C 的 rint 和 round？

> [round(3) - Linux man page](https://linux.die.net/man/3/round)

均是四舍五入。但是在 0.5、1.5 等半值时（）

- rint 取最近的偶数（银行家舍入）

  ```
  rint(0.5) = 0
  rint(1.5) = 2
  ```

- round 取绝对值大的（远离零的）

  ```
  round(0.5) = 1
  round(-0.5) = -1
  ```

### IEEE 754

IEEE 标准系列远古力作，定义了浮点数实现标准（太长不看（x））

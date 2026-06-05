# RM 开源资料汇总

> 持续更新ing

## 前言

1. 相当建议观看中科大麻神的【中科大RM电控合集】，相当全面，适合 RMer 宝宝体质。

2. 多用搜索引擎，找一些文章看，如博客园、CSDN、知乎、个人博客网站。

3. 多看 [RM 官方论坛](https://bbs.robomaster.com)，学会看开源，有时候自己的经验和奇思妙想都只是现有的理论，少走弯路不造不必要的轮子。


---

## 数学与控制

控制理论相关知识，全面通俗：[DR_CAN 控制理论](https://space.bilibili.com/230105574)

非常及其强烈建议看的数学内容。3B1B的其他视频同样推荐，适合初学数学时建立直观的数学印象：[【官方双语/合集】线性代数的本质 - 系列合集](https://www.bilibili.com/video/BV1ys411472E/?share_source=copy_web&vd_source=a0b30c57e9db0024aafc5b552bf0e321)

王洪玺笔记：[【知乎】韭菜的菜 - 状态估计/控制算法实践](https://www.zhihu.com/column/c_1296379521394929664)

基于 py 的卡尔曼滤波教程：[github@rlabbe Kalman-and-Bayesian-Filters-in-Python](https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python)

## 物品使用

大疆电池：[【分享帖】RM-大疆智能电池使用手册-RoboMaster 社区](https://bbs.robomaster.com/article/9289)

大疆遥控器&接收器：[【分享帖】RoboMaster DT7&DR16遥控接收系统 使用与维护手册-RoboMaster 社区](https://bbs.robomaster.com/article/9629?source=4)

## 编程与程序设计

[电控组代码规范 | Javen的技术博客](https://shen-jiewen.github.io/2024/11/18/电控组代码规范/)

## 个人博客

[闲居](https://xianmengxi.github.io/)

## 电控 - 通用

超清晰动画 stm32 入门教程 up 主：[keysking STM32 基础教程 + Freertos 教程](https://space.bilibili.com/6100925)

RMer 宝宝胎教视频，相当全面基础：[合集 中科大 RoboMaster 电控教程](https://space.bilibili.com/337732684/lists/1043942?type=season)

上面视频的配套资料：[【RM2025-电控教学资料开源】中国科学技术大学RoboWalker战队](https://bbs.robomaster.com/wiki/4574/18267?source=7)

交爷博客：[上海交通大学 RoboMaster 交龙战队博客 | 云汉交龙](https://sjtu-robomaster-team.github.io/)

浙爷博客：[Hello World 技术知识库](https://zju-helloworld.github.io/Wiki/)

大佬优秀分析：[AddisionHarry的知识库](https://www.yuque.com/addisionharry/technologycompetition)

COD王草凡大神开源，达妙stm32h7工程模板：[GrassFanWang / COD-H7-Template](https://github.com/GrassFanWang/COD-H7-Template)

入门级平衡车和LQR：[基于无刷电机的平衡小车](https://wenke-chen.github.io/p/segway/)

## 电控 - 调试

stm32 跑飞进 HardFault 的 debug 指南：[STM32卡死、跑飞、进入HardFault_Handler如何精准的确定问题](https://blog.csdn.net/m0_74676415/article/details/144341038)

## 电控 - 底盘控制

这篇文章看起来比较简单，但不涉及标准的运算：[麦克纳姆轮系运动学模型解算与分析](https://blog.csdn.net/m0_55933541/article/details/134040714)

更适合 RMer 宝宝体质的超进化麦轮解算 ：[麦克纳姆轮运动模型 - 知乎](https://zhuanlan.zhihu.com/p/609678279)

这个对于入门有些啰嗦，但全面：[【中科大RM电控合集】各种底盘各种解算一网打尽-哔哩哔哩](https://b23.tv/oPFHF2i)

## 电控 - 姿态解算

王洪玺大神开源，RM C 板开源陀螺仪解算，kalman 滤波：[WangHongxi2001 / RoboMaster-C-Board-INS-Example](https://github.com/WangHongxi2001/RoboMaster-C-Board-INS-Example)（建议搭配 [【知乎】韭菜的菜 - 状态估计/控制算法实践](https://www.zhihu.com/column/c_1296379521394929664) 系列教程使用）

同样王工开源，Mahony 算法：[Mahony姿态解算算法笔记 - WangHongxi - 博客园](https://www.cnblogs.com/WangHongxi/category/1655021.html)

## 电控 - 功率限制

我们用过的经典开源：[【RM2023-电机功率模型与功率控制开源】西交利物浦大学-RoboMaster 社区](https://bbs.robomaster.com/article/9438?source=4)

RLS拟合参数和大P分配，c++，注意github和论坛附件不一样github版本新一点：[【RM2024-功率控制算法开源（含舵轮，轮腿，全自动调参）】香港科技大学ENTERPRIZE战队-RoboMaster 社区](https://bbs.robomaster.com/article/54121?source=4)

## 电控 - 轮足

哈工程王洪玺开源，轮腿圣经：[RoboMaster平衡步兵机器人控制系统设计 - 知乎](https://zhuanlan.zhihu.com/p/563048952)

上交建模开源：[【RM2023-平衡步兵控制系统开源】上海交通大学-云汉交龙-RoboMaster 社区](https://bbs.robomaster.com/article/9430)

柳幸之进阶控制思路：[【RM AWARD 2024】电子科技大学中山学院 RoboBraver 柳幸之 部分技术成果说明](https://bbs.robomaster.com/article/22843?source=0)

一些轮腿经验：[标签: 轮腿平衡步兵 | 闲居](https://xianmengxi.github.io/tags/轮腿平衡步兵/)

[WilliamGwok / RP_Balance](https://github.com/WilliamGwok/RP_Balance)

[【RM2025 个人开源】山海机甲平衡步兵完全开源-RoboMaster 社区](https://bbs.robomaster.com/article/810688?source=4)

[【RM2024-轮腿平衡电控代码、建模开源及机械&电控经验分享】香港大学 HerKules战队-RoboMaster 社区](https://bbs.robomaster.com/article/54291?source=1)

[【RM2024-技术报告开源】南方科技大学ARTINX战队-RoboMaster 社区](https://bbs.robomaster.com/article/55220)

这个是开链四连杆结构，比较特殊：[【开链四连杆轮腿步兵技术报告+同济大学SuperPower+RM2025 技术报告开源】-RoboMaster 社区](https://bbs.robomaster.com/article/769697)

[【RM AWARD 2025】中国矿业大学 CUBOT 李腾宇 工程与轮腿机器人部分技术报告-RoboMaster 社区](https://bbs.robomaster.com/article/814277?source=4)

[【RM2026 轮腿代码开源】中国石油大学（北京）SPR轮腿步兵代码开源-RoboMaster 社区](https://bbs.robomaster.com/article/1884251)

[【RM2026 偏置并联腿(整车)电控开源】 南京航空航天大学金城学院-Born Of Fire战队-RoboMaster 社区](https://bbs.robomaster.com/article/1883510?source=1)

## 机械 - 轮足

关于轮腿的机械设计，长文：[ACE战队 2024-2025赛季轮腿机器人技术文档-机械-RoboMaster 社区](https://bbs.robomaster.com/article/728195?source=4)

## 算法 - 视觉

上科大大佬开源视觉——从入门到入土：[上海科技大学2026视觉技术方案开源](https://fcn47qghdcqf.feishu.cn/wiki/Hcw1wxTMZicx0xkinuQcKHetn5d?from=from_copylink)

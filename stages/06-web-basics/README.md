这个阶段的课文还没有建。学到上一阶段七成时，对导师说“准备阶段 6”。

# 阶段 6：Web 基础

> **规划用时** 80～120 小时 ｜ **前置** 阶段 5（只学 HTML 和 CSS 的部分，阶段 1 就够）｜ **核实日期** 2026-11-19 ｜ 回到[路线图](../../ROADMAP.md)

下面是计划，建这个阶段时会按你的真实进度和当时的工具重新定。

## 目标

系统地学网页的三样基本功：内容（HTML）、样子（CSS）、动作（JavaScript，让网页动起来的编程语言）。学会用浏览器自带的检查工具。弄懂浏览器的几条安全规则。

## 作品

一个手写的网页，不借助成套的现成工具（行话叫框架），从你的数据窗口取数并显示出来。打开它，你看到的是一张随数据库更新的汇率表，而不是写死在文件里的几行字。它是产品第一个真正有用的界面。

## 这个阶段会学到的规范（计划）

表里只标规则类型，而且是计划；约束力、谁说的、核对日期在建这个阶段时定，写在每条规范的卡片上。表里的英文名字是这些规范的正式名称，学到时再讲；现在把它们当书名看就行。

| 规范 | 规则类型 |
|---|---|
| 网页内容按 HTML 现行标准书写 | 标准 |
| 用含义明确的标签（HTML 里标明“这是什么”的记号）组织内容：标题就用标题标签，按钮就用按钮标签 | 标准（HTML 现行标准本身要求按含义使用标签） |
| 无障碍（让看不见、只用键盘的人也能用）达到 WCAG 2.2（万维网联盟发布的无障碍标准）的基本要求 | 标准 |
| JavaScript 按语言标准 ECMAScript 的现行写法 | 标准 |
| 用户提供的内容显示到页面之前先做无害化处理 | 惯例·事实标准（公开的应用安全检查表 OWASP ASVS 5.0.0） |
| 网站全程使用加密连接 | 惯例·平台与工具（浏览器本身的做法：Google 2025 年宣布、2026-10-21 公告已对所有用户默认打开：第一次打开没加密的公开网站前先问你；浏览器拦你、提醒你，不算惩罚，所以不是行业要求） |
| 页面跨网站取数要由对方服务器明确放行 | 标准（网页取数的标准，浏览器强制执行） |
| 打开速度用公开的指标衡量 | 惯例·平台与工具（谷歌公布的网页体验指标和它的测速工具） |

## 过关方式

网页只用键盘也能操作，过得了自动的无障碍和速度检查；阶段验收里有一道“页面取不到数，用检查工具找出原因”，做这一道时不用 AI。

## 前置

阶段 5，因为网页要从你自己的数据窗口取数。HTML 和 CSS 的部分只要求阶段 1。

## 规划用时

80～120 小时。

## 对标

| 对标 | 语言 | 网址 | 和本课程的差别 |
|---|---|---|---|
| MDN（Mozilla 维护的网页技术资料站）《学习 Web 开发》核心模块 | 中文 | https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Core | 本课程的网页从你自己的数据窗口取数 |
| 《现代 JavaScript 教程》 | 中文 | https://zh.javascript.info/ | 篇幅大；本课程只取前两部分的主干 |

两个网址都在 2026-11-19 打开过。

## 技术清单（现在看不懂没关系）

- HTML：文档骨架、语义化元素、链接、图片、列表、表格、表单与 label；HTML Living Standard（WHATWG）。
- CSS：层叠与优先级、盒模型、单位、flexbox、grid、自定义属性、响应式（媒体查询与容器查询、`clamp`）、嵌套、`:has()`、明暗两套配色。
- JavaScript（ECMAScript 2026）：值与类型、函数、数组与对象、模块、错误、Promise、`async` / `await`。
- 浏览器：DOM、事件、表单、`fetch`、JSON、`localStorage`；渲染流程与事件循环。
- 工具：DevTools 的 Elements、Console、Network、Application；Lighthouse 与 Core Web Vitals。
- 安全：same-origin policy、CORS（WHATWG Fetch Standard）、Cookie 与它的三个标志、`innerHTML` 对 `textContent`（XSS）、HTTPS 与证书、SRI。
- 无障碍：WCAG 2.2 的四条原则，三项基本检查。
- 交付：GitHub Pages 改用 Actions 发布；用 `dig` 和 `curl -v` 观察 DNS 与 TLS。
- 这个阶段末尾第一次接触 Node.js 和 npm，安装第三方包的安全习惯从这里讲起。
- 规则类型的出处：HTML Living Standard（WHATWG）；WCAG 2.2（W3C）；ECMA-262；OWASP ASVS 5.0.0 V1；Google 2026-10-21 公告 “Chrome now warns before insecure HTTP connections”（调研简报 cs-fundamentals）；WHATWG Fetch Standard；web.dev 的 Core Web Vitals 与 Lighthouse。
- 关卡编号（暂定）：`gate-6`。

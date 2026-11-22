### PUB-01 公开仓库三件套：README、LICENSE、.gitignore

- **约束力**：必须（适用范围：本课程）；推荐（适用范围：所有项目）
- **规则类型**：惯例·平台与工具
- **规则**：一个仓库公开之前，根目录里要有三样东西：说明这是什么的 `README.md`，写明别人能怎样使用的 `LICENSE`，挡住不该公开的文件的 `.gitignore`。
- **谁说的**：GitHub Docs「Creating a new repository」第 7 步（新建仓库时可以顺手创建的正是这三样：README、.gitignore、许可证）https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository ；GitHub Docs「About community profiles for public repositories」（GitHub 给公开仓库检查的“社区健康文件”里有 README 和 LICENSE，没有 .gitignore）https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories ；GitHub Docs「Licensing a repository」（没有许可证时默认的版权法适用，作者保留所有权利；许可证文件放在仓库根目录，常见的名字是 LICENSE.txt、LICENSE.md）https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository ；choosealicense.com「No License」页 https://choosealicense.com/no-permission/ 和 MIT 页（文件名写 LICENSE 或 LICENSE.txt）https://choosealicense.com/licenses/mit/ 。把这三样合称“三件套”是本课程的归纳，GitHub 没有这样叫。
- **核对日期**：2026-11-20；**复核周期**：12 个月，或者 GitHub 改了新建仓库页面时
- **谁来管**：在本课程里是检查 1.13a；别的项目里没有人会拦你，GitHub 照样让你公开；**不遵守的后果**：别人看不懂这个仓库，也不能合法地复用你的代码，杂物和草稿还可能跟着一起公开。
- **为什么**：公开仓库的读者是陌生人。README 告诉他这是什么、怎么看；LICENSE 告诉他能不能用、怎么用，没有它就是“保留所有权利”，别人只能看和 fork，不能复制、修改、分发；.gitignore 让系统杂物、草稿和密钥文件从一开始就不进仓库，公开以后不会被所有人看到。常见误解：“放到 GitHub 上公开就等于开源了”。开源（open source）是说任何人都可以看、改、再分发源代码，前提是有一份许可证写明允许；没有许可证，公开的仓库也只能看和 fork。
- **正例**：

      my-site/
      ├── .gitignore
      ├── LICENSE        （MIT 许可证，版权行写着年份和你的名字或笔名）
      ├── README.md      （最后一节写明用的是什么许可证，并链接到 LICENSE）
      ├── index.html
      └── style.css

- **反例**：仓库已经公开了，根目录只有 `index.html` 和 `style.css`；或者 LICENSE 里还留着 `[year]` 和 `[fullname]` 两个占位符。
- **怎么检查**：人工检查：在仓库根目录运行 `ls -a`，三样都在，名字的大小写也对，再用 `head -n 3 LICENSE` 看版权那一行填好了；复习题 1.13-no-license。在本课程里这条是必须的：你的 my-site 在第 1.13 课公开之前三样都要有，`python3 tools/course.py check 1.13a` 会看。
- **例外**：只放自己笔记、永远不打算让别人复用的公开仓库，可以不加许可证，但要知道这样别人就不能合法地复用；仓库里确实没有任何需要忽略的文件时，可以暂时没有 .gitignore。选哪种许可证是作者自己的决定。
- **旧教程提醒**：无
- **学于**：1.13

# 规范手册

阶段 0 和阶段 1 的 30 条规则，按类别分成 14 章。第一次来，先读[怎么读一张规则卡片](00-how-to-read-a-rule.md)。

卡片的原文在每一课文件夹的 `rules.md` 里。这里的章节是工具照抄生成的：卡片改了，手册跟着重新生成；两边对不上时，以 `rules.md` 为准。

每条规则用你自己的话写在 `notes/my-rules.md` 里，那个文件是你的。

<!-- 以下内容由工具生成，请不要手改：python3 tools/dev/build_reference.py -->

## 各章

| 章 | 类别 | 规则 |
|---|---|---|
| [学习工作区和命名](01-workspace-and-naming.md) | WS | WS-01、WS-02 |
| [终端安全](02-terminal-safety.md) | TERM | TERM-01、TERM-02 |
| [编辑器](03-editor.md) | ED | ED-01、ED-02 |
| [文档](04-documents.md) | DOC | DOC-01、DOC-02 |
| [Git](05-git.md) | GIT | GIT-01、GIT-02、GIT-03、GIT-04 |
| [提交](06-commits.md) | COMMIT | COMMIT-01、COMMIT-02 |
| [什么不该进仓库](07-repository-hygiene.md) | REPO | REPO-01、REPO-02 |
| [账号和身份](08-accounts-and-identity.md) | ACC | ACC-01、ACC-02 |
| [远程仓库和备份](09-remotes-and-backup.md) | REMOTE | REMOTE-01、REMOTE-02 |
| [公开发布](10-publishing.md) | PUB | PUB-01 |
| [求助和与时俱进](11-help-and-staying-current.md) | HELP、FRESH | HELP-01、FRESH-01 |
| [和 AI 一起干活](12-working-with-ai.md) | AI | AI-01、AI-02 |
| [管理工作](13-managing-work.md) | PM | PM-01、PM-02、PM-03 |
| [关于规则本身](14-about-rules.md) | META | META-01、META-02 |

## 全部规则（按上课顺序）

一共 30 条。

| 编号 | 标题 | 约束力 | 规则类型 | 哪一课 | 链接 |
|---|---|---|---|---|---|
| META-01 | 报错三问：谁在报错，关键词是什么，我刚才敲了什么 | 必须（本课程） | 规范·本课程约定 | [0.1](../stages/00-orientation/01-first-steps/lesson.md) | [卡片](14-about-rules.md#meta-01-报错三问谁在报错关键词是什么我刚才敲了什么) |
| WS-01 | 代码不放网盘同步目录 | 必须（所有项目） | 惯例·平台与工具 | [0.2](../stages/00-orientation/02-files-and-paths/lesson.md) | [卡片](01-workspace-and-naming.md#ws-01-代码不放网盘同步目录) |
| WS-02 | 命名用小写英文加短横线 | 必须（本课程）；推荐（所有项目） | 规范·组织 | [0.2](../stages/00-orientation/02-files-and-paths/lesson.md) | [卡片](01-workspace-and-naming.md#ws-02-命名用小写英文加短横线) |
| META-02 | 每条规范问三件事：谁说的、多强制、哪年的版本 | 推荐（本课程） | 规范·本课程约定 | [0.3](../stages/00-orientation/03-how-software-is-made/lesson.md) | [卡片](14-about-rules.md#meta-02-每条规范问三件事谁说的多强制哪年的版本) |
| PM-01 | 每个任务有明确的完成标准 | 推荐（所有项目）；必须（本课程） | 惯例·事实标准 | [0.4](../stages/00-orientation/04-manage-your-learning/lesson.md) | [卡片](13-managing-work.md#pm-01-每个任务有明确的完成标准) |
| PM-02 | 固定周期复盘 | 推荐（所有项目）；必须（本课程） | 惯例·事实标准 | [0.4](../stages/00-orientation/04-manage-your-learning/lesson.md) | [卡片](13-managing-work.md#pm-02-固定周期复盘) |
| TERM-01 | 不照抄看不懂的命令 | 必须（本课程）；推荐（所有项目） | 规范·本课程约定 | [1.1](../stages/01-foundations/01-create-and-view/lesson.md) | [卡片](02-terminal-safety.md#term-01-不照抄看不懂的命令) |
| TERM-02 | 删除前先看清要删什么 | 必须（本课程）；推荐（所有项目） | 规范·本课程约定 | [1.2](../stages/01-foundations/02-copy-move-delete/lesson.md) | [卡片](02-terminal-safety.md#term-02-删除前先看清要删什么) |
| ED-01 | 打开文件夹而不是单个文件 | 推荐（所有项目） | 惯例·平台与工具 | [1.4](../stages/01-foundations/04-editor/lesson.md) | [卡片](03-editor.md#ed-01-打开文件夹而不是单个文件) |
| ED-02 | 文本统一 UTF-8 和 LF，用 .editorconfig 说明 | 推荐（所有项目）；必须（本课程） | 惯例·事实标准 | [1.4](../stages/01-foundations/04-editor/lesson.md) | [卡片](03-editor.md#ed-02-文本统一-utf-8-和-lf用-editorconfig-说明) |
| DOC-01 | 每个项目根目录有 README.md | 必须（本课程）；推荐（所有项目） | 惯例·平台与工具 | [1.5](../stages/01-foundations/05-markdown-readme/lesson.md) | [卡片](04-documents.md#doc-01-每个项目根目录有-readmemd) |
| DOC-02 | README 回答五个问题 | 必须（本课程）；推荐（所有项目） | 规范·本课程约定 | [1.5](../stages/01-foundations/05-markdown-readme/lesson.md) | [卡片](04-documents.md#doc-02-readme-回答五个问题) |
| GIT-01 | 一个项目一个仓库，在项目根目录初始化 | 推荐（所有项目）；必须（本课程） | 惯例·平台与工具 | [1.6](../stages/01-foundations/06-first-commit/lesson.md) | [卡片](05-git.md#git-01-一个项目一个仓库在项目根目录初始化) |
| GIT-02 | 提交前确认身份设置 | 推荐（所有项目）；必须（本课程） | 惯例·平台与工具 | [1.6](../stages/01-foundations/06-first-commit/lesson.md) | [卡片](05-git.md#git-02-提交前确认身份设置) |
| GIT-03 | 提交前先看改了什么 | 必须（本课程）；推荐（所有项目） | 惯例·平台与工具 | [1.7](../stages/01-foundations/07-read-diff/lesson.md) | [卡片](05-git.md#git-03-提交前先看改了什么) |
| GIT-04 | 执行会丢数据的命令前先看状态 | 必须（本课程）；推荐（所有项目） | 规范·本课程约定 | [1.8](../stages/01-foundations/08-undo-uncommitted/lesson.md) | [卡片](05-git.md#git-04-执行会丢数据的命令前先看状态) |
| REPO-01 | 密钥、密码、令牌永不入库 | 必须（所有项目） | 惯例·事实标准 | [1.9](../stages/01-foundations/09-gitignore/lesson.md) | [卡片](07-repository-hygiene.md#repo-01-密钥密码令牌永不入库) |
| REPO-02 | .gitignore 从官方模板起步 | 推荐（所有项目） | 惯例·平台与工具 | [1.9](../stages/01-foundations/09-gitignore/lesson.md) | [卡片](07-repository-hygiene.md#repo-02-gitignore-从官方模板起步) |
| COMMIT-01 | 提交说明遵循 Conventional Commits | 必须（本课程）；推荐（所有项目）；必须（所在团队） | 惯例·事实标准 | [1.10](../stages/01-foundations/10-commit-conventions/lesson.md) | [卡片](06-commits.md#commit-01-提交说明遵循-conventional-commits) |
| COMMIT-02 | 一次提交一件事 | 必须（本课程）；推荐（所有项目） | 惯例·平台与工具 | [1.10](../stages/01-foundations/10-commit-conventions/lesson.md) | [卡片](06-commits.md#commit-02-一次提交一件事) |
| ACC-01 | GitHub 账号开启双重验证 | 必须（本课程）；推荐（所有项目） | 行业要求 | [1.11](../stages/01-foundations/11-github-account/lesson.md) | [卡片](08-accounts-and-identity.md#acc-01-github-账号开启双重验证) |
| ACC-02 | 提交邮箱用 GitHub 的隐私地址 | 推荐（所有项目） | 惯例·平台与工具 | [1.11](../stages/01-foundations/11-github-account/lesson.md) | [卡片](08-accounts-and-identity.md#acc-02-提交邮箱用-github-的隐私地址) |
| REMOTE-01 | 重要仓库在别处有第二份，并且试过能恢复 | 必须（本课程）；推荐（所有项目） | 惯例·平台与工具 | [1.12](../stages/01-foundations/12-push-and-backup/lesson.md) | [卡片](09-remotes-and-backup.md#remote-01-重要仓库在别处有第二份并且试过能恢复) |
| REMOTE-02 | 推送或公开之前，先查有没有密钥和隐私 | 必须（所有项目） | 行业要求 | [1.12](../stages/01-foundations/12-push-and-backup/lesson.md) | [卡片](09-remotes-and-backup.md#remote-02-推送或公开之前先查有没有密钥和隐私) |
| PUB-01 | 公开仓库三件套：README、LICENSE、.gitignore | 必须（本课程）；推荐（所有项目） | 惯例·平台与工具 | [1.13](../stages/01-foundations/13-publish-site/lesson.md) | [卡片](10-publishing.md#pub-01-公开仓库三件套readmelicensegitignore) |
| HELP-01 | 提问给出目标、做法、期望、实际报错原文、版本 | 推荐（所有项目）；必须（本课程） | 惯例·平台与工具 | [1.14](../stages/01-foundations/14-errors-help-fresh/lesson.md) | [卡片](11-help-and-staying-current.md#help-01-提问给出目标做法期望实际报错原文版本) |
| FRESH-01 | 用一个做法前确认它的版本和日期 | 必须（本课程）；推荐（所有项目） | 规范·本课程约定 | [1.14](../stages/01-foundations/14-errors-help-fresh/lesson.md) | [卡片](11-help-and-staying-current.md#fresh-01-用一个做法前确认它的版本和日期) |
| AI-01 | AI 的改动先看 diff 再接受 | 必须（本课程）；推荐（所有项目） | 规范·组织 | [1.15](../stages/01-foundations/15-review-ai-changes/lesson.md) | [卡片](12-working-with-ai.md#ai-01-ai-的改动先看-diff-再接受) |
| AI-02 | AI 参与的提交如实署名 | 推荐（所有项目）；必须（本课程） | 惯例·平台与工具 | [1.15](../stages/01-foundations/15-review-ai-changes/lesson.md) | [卡片](12-working-with-ai.md#ai-02-ai-参与的提交如实署名) |
| PM-03 | 每个阶段结束做一次复盘 | 必须（本课程）；推荐（所有项目） | 惯例·事实标准 | [1.16](../stages/01-foundations/16-stage-project-and-gate/lesson.md) | [卡片](13-managing-work.md#pm-03-每个阶段结束做一次复盘) |

# 导师手册：每一句话怎么做

这是导师规则（`CLAUDE.md`）的配套文件。`CLAUDE.md` 第 3 节的表里，每一句话对应下面一节。学习者说了那句话，先读对应的一节再动手。这里的每一步都按工具今天的行为写（2026-11-19 或 2026-11-20 在模拟环境里运行过的，注明「已实测」；只对照了官方文档的，注明出处）。

所有 `python3 tools/course.py …` 命令都在学习工作区里运行：`cd ~/Developer/fullstack-from-zero`。命令一般由学习者在他自己的终端里敲；写明“你运行”的，才由你在自己这边运行。

<!-- 维护说明：改这里的步骤，要同时看 CLAUDE.md 第 3 节的表和 docs/authoring/tutor-tests.md。 -->

---

## §1 “开始上课”

1. 状态行（`CLAUDE.md` 第 1 节）。
2. 没有 `learner/state.json`，或者还没有任何一站通过：这是第一次。说一两句欢迎，然后打开第 0.1 课 `stages/00-orientation/01-first-steps/lesson.md` 和一个终端（应用给了你打开文件、打开终端的工具就用；没有就告诉他：会话最上面有一排小图标，鼠标停上去会显示名字；点 **Files**，依次点开 `stages` → `00-orientation` → `01-first-steps` → `lesson.md`；点 **Terminal** 或按 Ctrl+`；找不到图标就点那排图标旁边的 **⋮**，从菜单里选，和第 0.1 课说的一样）。请他从课文开头读起（先是「先想一想」，接着是「第 1 站」）。不要先讲课，不要先做问卷：问卷是第 1 站「自己做」，他说“我们来做入学问卷”时再做（§9）。复习题这时还没有，不用提。
3. 已经学过：
   - 距离上次学习超过 10 天（`status` 会打印“距离上次学习：N 天。隔得有点久……”）：先走回归流程（§12）。
   - 否则请他运行 `python3 tools/course.py review`；他说“跳过”就跳过。
4. 找出下一个没做完的步骤，按这个顺序看：一场还没批改完的考试（`exam_attempts` 里有没结果的题）→ 一课的站都通过了、但全课检查还没通过（这一课的收尾）→ 下一站 → 到期的关卡。`status` 打印的「下一步」一行就是工具的判断，用它，不要自己猜。例外：第 1.13 课按 §5“急救：Pages 用不了”选了别的路的（他说过，或者日志里记着），`status` 会一直停在 1.13b：不再把他送回 1.13b、1.13c，看 `learner/state.json` 的 `stations`，从第 1.14 课起第一个没通过的站（或那一课的收尾）接着上（§2 第 2 步）。
5. 说出下一步是什么、大约多少分钟，打开那一课的课文，跳到那一站的标题。到关卡时按 §3。

## §2 接着上：“从 1.6b 继续”“从 1.6 的收尾继续”“从 1.7 开始”

1. 读 `learner/state.json` 的 `stations`，和他说的那一步对一对。
2. 前面还有没做完的步骤（比如上一课的收尾、更早的一站）：说出是哪一步，建议先回去做；他明确说要跳过，就按他说的走。不替他把任何一步记成通过。例外：第 1.13 课按 §5“急救：Pages 用不了”选了别的路的（他说过，或者日志里记着），1.13b、1.13c 一直不通过是正常的，他说“从 1.14 开始”就照做，不再劝他回去。
3. “从 <站> 继续”：打开课文，跳到那一站。
4. “从 <课> 的收尾继续”：打开课文的「## 收尾」，按顺序陪他做（这一课的「本课行规」一节在最后一个存档点和收尾之间，他还没读过的，先请他读那一节，再写行规笔记）：
   1. 全课检查 `python3 tools/course.py check <课>`；
   2. 行规笔记（课文的收尾有这一步才做；写着「本课没有新行规」的课没有）：`code notes/my-rules.md`，在这一课每条行规的小标题下面用自己的话写一两句，再写一个自己的例子，⌘S 保存（你不替他写）；
   3. 一句话日志 `python3 tools/course.py journal`；
   4. 第 1.12 课起：备份（§18）。
   然后说课文最后一行给的下一句：“从 <下一课> 开始”或“做小关卡 <关卡>”。
5. “从 <课> 开始”：打开那一课，从「先想一想」开始。
6. 旧说法照这张表换：“从收尾继续”“从 1.6 收尾继续”“做 0.3 的收尾”“从本课行规继续”“从本课的收尾接着做” → 当前这一课的收尾；“从 0.4c 的小关卡继续” → “做小关卡 gate-0”；收尾没做完却说“从 <下一站或下一课> 继续” → 先提醒收尾。

## §3 “做小关卡 gate-a”

1. 四个关卡：gate-0 起步小关卡（第 0.1～0.4 课，在第 0.4 课第 3 站的备份之后）、gate-a 终端与文档关卡（第 1.1～1.5 课）、gate-b 本地 Git 关卡（第 1.6～1.10 课）、gate-1 阶段 1 验收（第 1.11～1.16 课，在第 1.16 课第 2 站）。
2. 这个关卡的实操题已经全部通过、只差讲解题：直接按 §4。
3. 开考前说清三件事：这是单独的一段整块时间（开考时工具会打印题数和预计用时）；考试中没有提示，你也不回答题目；做不出来的题空着就行。说用时的时候注意：`status`、`check` 在开考前打印的是估的数，开考时按抽到的题重算，两个数会差几分钟（gate-b 最多差 4 分钟，gate-1 最多差 5 分钟）；不要说它们一样。
4. 请他运行 `python3 tools/course.py exam <关卡>`。每道题在 `~/Developer/playground/exam-<关卡>/<题号>/` 里做；做完回到学习工作区运行 `python3 tools/course.py exam <关卡> --grade`。再运行一次 `exam <关卡>` 不会重新出题，题和他做的改动都还在；想整场重来是 `--new`。
5. 考试中（这个关卡有一场还没批改完，`exam_attempts` 里有它没结果的题）：对这个关卡的考题，不给提示、不给答案、不碰考题文件夹。关卡不挡下一课：他把这一场放着去上后面的课，后面的课照常教，同时提醒他这一场还开着，做完批改是 `python3 tools/course.py exam <关卡> --grade`，想放弃这一场重新出题是 `--new`。工具不一定替你提醒：gate-0 和 gate-1 在课里考（第 0.4 课第 3 站、第 1.16 课第 2 站），那一站没通过之前 `status` 不列这一场，只有 `check 0.4c`、`check 1.16b` 会说“这一场还没有批改”；是不是有一场开着，以 `learner/state.json` 的 `exam_attempts` 为准。他问题目，就说：“考试中我不给提示；做不出来就空着，批改后会告诉你练什么。”只有环境坏了或「检查器出问题」时按急救处理，而且只修环境，不碰题。
6. 批改以后读他贴来的结果或 `learner/last-result.json`。没通过的题，工具列出练习清单（哪一课、哪道题）；下一场只考没通过的题，换另一套题面。一课有一道题通过就够了，不要求一课的题全部通过。
7. 实操题都过了（工具会提示说“请问我 <关卡> 的讲解题”）：按 §4。
8. gate-0：第 0.4 课第 3 站的检查只要求 gate-0 有成绩记录，不要求每题都通过。gate-1：第 1.16 课第 2 站先做排错题（`python3 tools/course.py scenario 1.16b`），再开考，讲解题写进 `notes/gate-1-explain.md`（§4）。

## §4 “请问我 gate-0 的讲解题”

也算这一句：“讲给导师听”加关卡名，以及“gate-0 的动手题做完了，请问我讲解题”这类旧说法。没说关卡名就问是哪个关卡。讲解题有几道、问什么，以 `gates/<关卡>/rubric.md` 为准；gate-0、gate-a、gate-b 另有一道排错题，照 rubric 一起问。对学习者不要说一共几道题。

1. 先看 `learner/state.json`：这个关卡批改过一场吗（`exams` 里有这个关卡的结果）？没有，就说讲解题放在实操题批改以后，先做 §3（这时工具也不收 `--explain`，会说“还没有批改过一场考试”）。通常在工具说“实操题都通过了。还差讲解题”以后问；实操还有没过的课、他也想先讲，可以讲，但要说清实操的补考还在等着（这时记下的“通过”会留着，工具会打印「讲解题的“通过”先记着」）。
2. 读 `gates/<关卡>/rubric.md` 的「讲解题」和「排错题」两节。`explain` 里这个关卡还没有记录，用问法 A；记录是 `again`（上次没过），用问法 B。
3. 一道一道问，问完一道等他答完再问下一道。gate-0、gate-a、gate-b 接着做排错题（rubric 里写着，给他看一段报错，请他答报错三问和改法）。gate-1 的排错题是第 1.16 课第 2 站的「自己做」，这里不再问。
4. 评的时候不提示、不追问到他答对、不教。每条标准引用他的原话，标出「够了」或「还不够」，只按 rubric 里写的「够了的回答里有」和「这样还不够」判。拿不准，就算还不够。
5. 告诉他结果：
   - 都够了：“讲解题通过。”
   - 有一题还不够：说哪一题、缺的是哪一点、回去看哪一课的哪一节；过几天换个问法再讲一次。这时考试已经结束，可以把缺的那一点讲给他听。
6. 请他自己运行命令记下结果：`python3 tools/course.py exam <关卡> --explain pass`，或者 `--explain again`（已实测，2026-11-19：记进 `learner/state.json` 的 `explain`，`again` 时工具提示“准备好了再对导师说‘请问我 <关卡> 的讲解题’”）。不要靠下一次对话记得。
7. gate-1 另有一条路：他在一个**不以学习工作区为项目文件夹**的新对话里，把 `gates/gate-1/examiner-prompt.md` 的全文发过去；考官会再要三样：`notes/gate-1-explain.md` 的全文、`exam gate-1 --grade` 最后一次的输出、`check 1.16b` 的输出（第 1.16 课这样告诉他）。由那个考官评。他回来告诉你考官的结论，同样用第 6 步的命令记下。你来评时，先读 `notes/gate-1-explain.md`，再请他不看笔记口头讲一遍（第 1.16 课这样告诉他）；两样合起来按 rubric 评。写下的和讲出来的意思对不上时，按 `gates/gate-1/rubric.md` 的规定以讲出来的为准，并在反馈里说一句；讲出来的本身拿不准，算还不够。

## §5 “急救：<一句话说现象>”

通用步骤：

1. 第二行写「急救模式：」。先看现象：他贴来的文字、终端面板（应用给了你读终端面板的工具才读）、`learner/last-result.json`。
2. 先只读地查原因（看文件、`git status`、`git config get …`、`doctor`）。用报错三问把原因说成一两句大白话。
3. 修：能口述的就口述准确的命令，由他敲。会删东西、改写历史、改全局设置的：先讲后果，先做安全副本，由他亲手执行。你自己只运行不会改东西的命令，或者这一节明确写了由你做的事。
4. 修完说清原因和以后怎么避免；请他记一条日志：`python3 tools/course.py journal --done "急救：<现象>，已解决" --stuck "<原因>" --next "从 <站> 继续"`（下一步是新的一课时，照 `status` 打印的那句写 `"从 <课> 开始"`）。暴露出一个误解的，记进 `learner/misconceptions.md`；是课文写错了的，按 §8。

课文点名的情况：

- **“急救：终端不在学习工作区”**（第 0.1、0.2 课；旧说法“急救：终端不在 Engineering 文件夹”“急救：终端不在 fullstack-from-zero 文件夹”）：他还没学 `cd`。先用 `pwd -P` 在你这边确认学习工作区的真实位置，再口述一整行：`cd ~/Desktop/fullstack-from-zero`（这只是举例，换成真实位置；路径里有空格就整段加双引号），然后请他敲 `pwd` 看结尾是不是 `fullstack-from-zero`。
- **切换输入法**（第 0.1 课“不会切就问导师”；命令里混进全角空格、全角短横线也是这个原因）：不要假定某个快捷键，这台电脑设过什么你不知道。请他点屏幕最上面菜单栏右边的输入法菜单（输入法图标），选英文那一项（名字常见的是 ABC 或 U.S.），回到终端重敲。也可以试 Control-空格（切回上一个输入法）；Fn 或地球仪键要先在键盘设置里打开才管用。（Apple Mac User Guide「Use input sources to type in other languages」，macOS 27 版，support.apple.com/guide/mac-help/mchlp1406，2026-11-20 核对。）
- **进了 vi 出不来**（`less` 里按了 v，或者 `git commit` 忘了写 `-m`）：按 Esc，输入 `:q!`（英文冒号、q、感叹号），按回车，就是不保存退出；从 `less` 进去的，回到 `less` 以后再按 q。第 1.1、1.6、1.14 课都这样写。
- **弹出“命令行开发者工具”的安装窗口**（新 Mac 上第一次敲 `git` 或 `python3`）：这是 Apple 的安装程序，请他点 Install，等装完再敲一次那条命令（README「怎么拿到这门课」；《Pro Git》第 1.5 节）。
- **“急救：code 命令找不到”**（第 0.1 课）：先问他装没装 VS Code（「应用程序」文件夹里有没有 Visual Studio Code）。没装：按 `CLAUDE.md` 第 8 节「装软件」，和他一起读 README「怎么拿到这门课」里 VS Code 那一条和官网的说明，由他自己下载、拖进「应用程序」。装好了再做下面的。请他打开 VS Code，按 ⇧⌘P 打开命令面板，输入并运行 Shell Command: Install 'code' and optionally 'copilot' commands in PATH；问要不要装 Copilot CLI 时选 No（只加 `code`，这门课用不到别的）；然后关掉终端标签再开一个新的。（VS Code 文档「Visual Studio Code on macOS」，页面日期 11/18/2026。）
- **“急救：convert.py 改坏了”**（第 0.1 课）：`starter/hello-fx/convert.py` 是学习者自己改的文件，不用工具恢复，也不偷偷覆盖。请他运行 `python3 tools/course.py scenario 0.1`，工具会在 `~/Developer/playground/0.1-start/hello-fx/` 放一份原样。用 `diff ~/Developer/playground/0.1-start/hello-fx/convert.py starter/hello-fx/convert.py` 一起看差别，由他在 VS Code 里改回去（第 0.1 课第 3 站改过的那两个数照课文重新改上）。
- **“急救：starter 被改动了”**（`doctor` 提示的句子；第 1.4 课的检查也会提到起始文件）：你运行 `python3 tools/dev/build_starter_manifest.py --check`，把列出的文件念给他，问这些改动对他有没有用；他同意的，你运行 `python3 tools/dev/build_starter_manifest.py --restore <路径>`。改过的那一份会留在旁边的 `<路径>.changed`，不删；他确认不要了，由他把它移进练习场（`mv <路径>.changed ~/Developer/playground/`），免得第 1.12 课把它一起存进仓库。`convert.py` 是学习者照课文自己改的文件：`--check` 把它单独列出、不算问题，`--restore` 不带 `--force` 不恢复它（见上一条）。告诉他练习场景和考试用的都是工具里存的原样，不受这次改动影响（`doctor` 那一行也这样说）。这个脚本的 `--write` 只给建课的人用，绝不在学习者的学习工作区里运行：它会把改过的文件记成新的原样。
- **“急救：学习工作区里多了 .git”**（`doctor` 提示的句子；第 1.6 课 `git init` 的路径以 `fullstack-from-zero/.git/` 结尾时也说它）：先看他学到哪一课。`doctor` 只在他学到第 1.12 课之前提这一行（第 1.11 课的站都通过了，或者通过了 1.12a 或更后面的站，就不再提）。`status` 的下一步是第 1.11 课的一站时，光看状态分不出这个 `.git` 是第 1.12 课第 1 站自己建的，还是建错了地方（两种都是空的）：先什么命令都不给，只问一句“刚才的 `git init` 是在做第 1.12 课第 1 站吗？”。他说是，或者已经说过在做第 1.12 课（第 1.11 课还有一站没通过时，`doctor` 在 1.12a 的 `git init` 以后仍会提这一行）：那个 `.git` 是第 1.12 课第 1 站自己的 `git init`，什么都不移，告诉他这一行可以不管，并提醒他把第 1.11 课没通过的那一站做完，`doctor` 就不再提这一行（1.12a 通过以后也不再提）。他说不是、说不清，或者还没学到第 1.11 课：学习工作区不该是仓库，多半是在错的文件夹里运行了 `git init`。只读地看：`git -C ~/Developer/fullstack-from-zero log --oneline -3`（刚建错的仓库会说 `does not have any commits yet`，说明里面什么也没存）。讲清楚以后，请他把它移进练习场而不是删掉：`mv ~/Developer/fullstack-from-zero/.git ~/Developer/playground/stray-git-<今天日期>`，再运行 `doctor` 确认那一行没了。
- **“急救：学习工作区里多了一个 －p 文件夹”**（第 0.2 课第 3 站：`mkdir -p ~/Developer` 的短横线打成了全角，学习工作区最外层多出一个空文件夹 `－p`）：只读地看 `ls -la ./－p`（终端在学习工作区里），确认它是空的（只有 `.` 和 `..` 两行）。讲清楚：它不碍事，但不能留着，第 1.12 课会把学习工作区里的东西都存进仓库。不删，由他移进练习场：`mv ./－p ~/Developer/playground/stray-p-<今天日期>`（练习场还没有就先 `mkdir -p ~/Developer/playground`）。名字里的 `－` 就用中文输入法打，和刚才打错的那一下一样；其余部分切回英文打。再运行 `ls`，确认 `－p` 不在了，然后切到英文输入法重敲 `mkdir -p ~/Developer`。（已实测：模拟环境，2026-11-20。）
- **“急救：git init 建错了地方”**（第 1.6 课第 2、3 站，`git init` 打印的路径不以 `diary/.git/` 或 `my-site/.git/` 结尾；第 1.6 课的检查也会说）：请他把 Git 打印的那一行发来（`Initialized empty Git repository in …/.git/`），`.git/` 前面就是建错的那个文件夹。只读地看：`git -C <那个文件夹> rev-parse --show-toplevel`，再 `git -C <它打印的位置> log --oneline -3`。分情况：
  - 位置是学习工作区（`~/Developer/fullstack-from-zero`）：按“急救：学习工作区里多了 .git”做。
  - 在练习场 `~/Developer/playground/1.6b` 里面：不用移，请他运行 `python3 tools/course.py scenario 1.6b --reset` 重搭，再按课文 `cd` 进去、`pwd` 确认以后重新 `git init`。
  - 别的地方（常见的是 `~/Developer` 或 `~`）：讲清楚删掉 `.git` 撤不回来；由他移进练习场：`mv <那个位置>/.git ~/Developer/playground/stray-git-<今天日期>`；再在那个文件夹里运行 `git status`，应该看到 `fatal: not a git repository`。
  然后回到他本来要建仓库的文件夹，从那一步重来，再运行那一站的检查。（已实测：在 `~/Developer` 建错再移走，模拟环境，2026-11-20。）
- **“急救：外层有一个建错地方的仓库”**（第 1.12 课的检查 1.12a、1.12b、1.12c 打印的句子：学习工作区或练习文件夹本身不是仓库，却在别的仓库里面）：做法同上一条“别的地方”。从检查点名的那个文件夹开始：`git -C <那个文件夹> rev-parse --show-toplevel` 打印外层仓库的位置；只读地看 `git -C <那个位置> log --oneline -3`；讲清楚；由他把 `<那个位置>/.git` 移进 `~/Developer/playground/stray-git-<今天日期>`，不删；然后回到学习工作区再运行那一站的检查。外层是 `~/Developer` 或 `~` 时，`~/Developer/my-site` 也在它里面，移走以后 my-site 用的是它自己的仓库，不受影响。
- **“急救：my-site 已经在一个仓库里了”**（第 1.6 课：在 `~/Developer/my-site` 运行 `git status` 看到 `On branch`；第 1.12 课的检查也会说外层有仓库）：你运行 `git -C ~/Developer/my-site rev-parse --show-toplevel`，它打印外层那个仓库的位置（常见的是 `~/Developer` 或 `~`）。只读地看 `git -C <那个位置> log --oneline -3`。讲清楚：那是一次放错地方的 `git init`，删掉它的 `.git` 不能撤回。请他移进练习场：`mv <那个位置>/.git ~/Developer/playground/stray-git-<今天日期>`；再回 `~/Developer/my-site` 运行 `git status`，应该看到 `fatal: not a git repository`，然后接着上课。my-site 已经有自己的仓库、外层也有一个时（第 1.6 课第 3 站的检查这样说），`git -C ~/Developer/my-site rev-parse --show-toplevel` 打印的是 my-site 自己，要从上一层问：`git -C ~/Developer rev-parse --show-toplevel`。移走的只是外层那个 `.git`，my-site 自己的 `.git` 不动；移完在 my-site 里 `git status` 看到的是 `On branch main`，再运行 `python3 tools/course.py check 1.6c`。
- **“急救：学习工作区还在同步盘里”**（第 1.12 课第 1 站，`doctor` 说学习工作区在同步盘里、他拿不准搬不搬时）：这是第 0.2 课说好的“再问一次”。课文自己已经问了，检查 1.12a 会请他选一次、记下决定；你只在他拿不准时帮他想清楚，他说“帮我把课程安置到 ~/Developer”就按 §10 做（搬完在新位置从 1.12a 重来，仓库跟着文件夹一起搬）。用一两句讲 WS-01：仓库放在云同步的文件夹里容易被同步弄坏（Git 官方 FAQ gitfaq）。问他：搬（§10），还是留在原处。留在原处：不再劝，说明一次风险，告诉他检查 1.12a 会再问一次并记下这个决定；有入口的照常用 `cd ~/Developer/fullstack-from-zero`，没有入口的先建（§11）；然后接着上第 1.12 课。
- **“急救：提交签名”**（第 1.12 课第 1 站，`doctor` 的提交签名一行在「需要处理」里；第 1.14 课检查 1.14a 提交没成功时；第 1.11 课提交报 `cannot run gpg` 时）：回到第 1.6 课第 1 站的做法。只读地看 `git config get commit.gpgsign`、`git config get gpg.format`、`git config get gpg.ssh.program`。不用签名的，他自己敲 `git config set --global commit.gpgsign false`；第 1.11 课选了 SSH 签名、但 `gpg.ssh.program` 是空的，他自己敲 `git config unset --global gpg.ssh.program`。改之前先照第 1.6 课备份 `~/.gitconfig`。
- **“急救：学习仓库成了公开的”**（第 1.12 课）：口述，由他在学习工作区里敲：`gh repo edit --visibility private --accept-visibility-change-consequences`（gh 手册 gh repo edit：用 `--visibility` 时必须同时写 `--accept-visibility-change-consequences`）。再请他运行 `gh repo view --json visibility`，应该看到 `"visibility": "PRIVATE"`。然后照第 1.12 课收尾的密钥检查看推上去的内容；推上去过真的密钥、令牌，先作废它（REPO-01），再考虑别的。你不在 GitHub 上替他操作。
- **“急救：git 要我输入 GitHub 用户名”**（第 1.12 课第 3 站，`git clone` 问 `Username for 'https://github.com':`）：先确认他按了 Ctrl+C、什么也没输入：不要在这一行里输入用户名、密码或令牌（2021 年 8 月 13 日起 GitHub 不再接受账号密码做 Git 操作，第 1.11 课讲过）。请他运行 `gh auth status`，把输出发来（令牌那一行只露开头，你不复述）。没登录或令牌失效：陪他按第 1.11 课第 2 站第 4 步再登录一遍，第四个问题 `Authenticate Git with your GitHub credentials?` 选 Yes（让 Git 也用这份登录凭据）。已登录：由他运行 `gh auth setup-git`（让 Git 用 gh 存好的凭据）。它往全局设置 `~/.gitconfig` 里写几行：先讲后果（以后 `gh auth logout` 了，Git 也拿不到登录），先请他照第 1.6 课备份（`cp ~/.gitconfig ~/.gitconfig.backup-<日期>`），再由他敲。然后从 `cd ~/Developer` 那一步重新 `git clone`。验证码和浏览器里的授权他自己做。（gh 手册 gh auth status、gh auth setup-git，cli.github.com/manual，2026-11-20 核对：`setup-git` 把 gh 设成 Git 的凭据助手；`status` 只有加 `--show-token` 才显示令牌，这个选项不用。）
- **“急救：my-site 的状态不对”**（第 1.13 课开头）：请他运行 `python3 tools/course.py scenario 1.13`，工具打印出它搭好的那一份 my-site（一般在 `~/Developer/playground/1.13-start/my-site`）。先把旧的整份移开当安全副本：`mv ~/Developer/my-site ~/Developer/playground/my-site-old-<今天日期>`；再复制新的：`cp -R ~/Developer/playground/1.13-start/my-site ~/Developer/my-site`；最后 `cd ~/Developer/my-site` 和 `git log --oneline` 确认有七个提交，最上面一个是 `feat: 调大标题的字号`（以工具打印的「N 个提交」为准；已实测，模拟环境，2026-11-20：`scenario 1.13` 打印「7 个提交」）。告诉他：这一份的提交作者是 `练习场 <playground@example.invalid>`，以后会和网页一起公开，不涉及隐私；他自己在旧那一份里的改动要的话，可以对照着重新改。
- **“急救：公开前发现历史里有密钥文件”**（第 1.13 课）：先停下，不建远程、不推送。第一步永远是作废那把密钥、换一把新的（REPO-01）。然后才改写历史，先在练习场的副本上演练：`cp -R ~/Developer/my-site ~/Developer/playground/rewrite-test`，在副本里由他运行 `git filter-branch --index-filter "git rm -q --cached --ignore-unmatch <文件名>" -- --all`（它会先打印一大段警告并等十秒，正常），再运行 `git update-ref -d refs/original/refs/heads/main`，用 `git log --all --stat` 确认那个文件名不再出现、提交个数没变，然后把文件名写进 `.gitignore` 再提交。副本没问题，再在 `~/Developer/my-site` 上照做（先 `cp -R` 一份安全副本）。注意：这条命令会把那个文件从文件夹里也拿掉。（已实测：Git 2.54.0，模拟环境，2026-11-19。）
- **“急救：公开前发现旧提交里有我的真实邮箱”**（第 1.13 课第 1 站，或者检查 1.13a 说许可证那次提交的邮箱不是隐私地址）：改写历史不可逆，先讲后果：每个提交的编号都会变，作者日期会变成今天；仓库还没公开时做最省事，已经公开过的，别人那里可能还留着旧的副本。先确认他的全局邮箱已经是第 1.11 课的隐私地址（`git config get user.email`，你不念出它的值，只问他对不对）。在练习场副本上演练：`cp -R ~/Developer/my-site ~/Developer/playground/rewrite-test`，进副本由他运行 `git rebase -r --root --exec "git commit --amend --no-edit --reset-author"`，再用 `git log --format='%h %an <%ae> %s'` 看作者都换了、提交个数和说明没变。没问题再在 `~/Developer/my-site` 上照做（先做安全副本）。（已实测：Git 2.54.0，模拟环境，2026-11-19。）
- **“急救：公开前发现旧提交里有我的真名”**（第 1.13 课第 1 站：真名在旧提交的作者那一行，或者在旧提交的文件内容里，比如第 1.4 课的网页标题、第 1.5 课 README 的作者）：先停下，不建远程、不推送。你不问他的真名，也不念出来；命令里的 `<真名>` 由他自己换上。
  1. 先讲后果，和真实邮箱那一条一样：改写历史不可逆，每个提交的编号都会变，作者日期会变成今天；现在仓库还没公开，做起来最省事。课程不单独教改写历史，这里只照着做一次。现在推荐的改写工具是 git-filter-repo，要另外安装；这里用 Git 自带的 `git filter-branch`（Git 手册不鼓励它，所以一定先在副本上演练）。
  2. 当前的文件里还有真名的，先由他照第 1.4、1.5 课改成笔名，照常提交。`git status` 要是干净的。
  3. 在练习场副本上演练：`cp -R ~/Developer/my-site ~/Developer/playground/rewrite-test`，`cd` 进副本，由他运行：
     - 找出在哪里：`git grep -n "<真名>" $(git rev-list --all)` 列出还带着它的旧文件（每行开头是提交编号和文件名）；`git log --all --format='%h %an %cn'` 看作者和提交者两栏。
     - 先改作者那一行：`git config get user.name` 先确认全局名字已经是笔名（你不念出它，只问他对不对），再运行真实邮箱那一条的 `git rebase -r --root --exec "git commit --amend --no-edit --reset-author"`。这一步一定在改文件内容之前做：先改内容会让某些提交变成空的，`--amend` 会停下来。
     - 再改文件内容：`git filter-branch --tree-filter "find . -type f -exec perl -pi -e 's/<真名>/<笔名>/g' {} +" -- --all`（会先打印一段警告并等十秒，正常），然后 `git update-ref -d refs/original/refs/heads/main`。
     - 核对：`git grep -n "<真名>" $(git rev-list --all)` 什么都不输出；`git log --all --format='%h %an %cn'` 里没有真名；`git log --oneline | wc -l` 和改之前一样多；`git status` 干净。
  4. 副本没问题，再先做一份安全副本（`cp -R ~/Developer/my-site ~/Developer/playground/my-site-before-rewrite-<今天日期>`），然后在 `~/Developer/my-site` 上照做、照样核对。（已实测：Git 2.54.0，perl 5.34，模拟环境，2026-11-20：9 个提交改完还是 9 个，作者、提交者和旧文件里都没有了那个名字，文件权限没变。）
- **“急救：gh 登录不上”**（第 1.13 课第 2 站：`gh repo create` 要他先运行 `gh auth login`，照第 1.11 课再登录一次还是不行）：请他运行 `gh auth status`，把输出发来。令牌只露开头、后面是星号的那一行没关系，你也不复述它；带“显示令牌”选项的写法，第 1.11 课说过永远不用。看输出：没登录、或者说令牌失效的，陪他按第 1.11 课第 2 站第 4 步的顺序再登录一遍（`gh auth login`，选 GitHub.com、Login with a web browser、HTTPS、Yes），每条命令他自己敲，一次性验证码和浏览器里的授权他自己做，你不看、不填。登录状态正常、`gh repo create` 还报错的：把报错原文发来，一起用报错三问读，先查 gh 手册（cli.github.com/manual）再说改法，不凭记忆给选项。
- **“急救：Pages 用不了”**（第 1.13 课）：先和他对一遍 Pages 设置（Deploy from a branch、main、/ (root)、点了 Save），再等十分钟。他不愿意公开仓库，或者看网页的人打不开 `github.io`：说出备选，Render 的免费静态网站（render.com 文档「Static Sites」），账号由他自己注册，你不替他注册；或者先在本机 `open index.html`。他选了这两条路之一：告诉他检查 1.13b 会一直不通过（没有 GitHub 仓库的，1.13c 也不通过），`status` 的“下一步”会停在 1.13b，这不挡后面的课；照他选的路陪他做完能做的部分，再从第 1.14 课接着上（对导师说“从 1.14 开始”）。不要替他标记通过，也不要劝他公开仓库。
- **“急救：zip 报 Operation not permitted”**（第 0.4 课）：多半是 macOS 问过要不要允许访问「文稿」而没点允许。请他打开 System Settings（系统设置）> Privacy & Security（隐私与安全性）> Files and Folders（文件和文件夹），给他运行命令的那个应用打开 Documents Folder（「文稿」），然后再运行一次。〔对照文档，界面可能不同：建课时没有在这台电脑的系统设置里点过〕这是他自己的设置，由他改。
- **“急救：brew 装 gh 报 Error”“急救：ssh-keygen 问要不要覆盖”**（第 1.11 课；gpg 报错也按这一条）：先停下，一起读那几行。`Overwrite` 那一题默认答 n，除非他确定旧钥匙没在用；你不替他回答。
- **第 1.12 课第一次推送报 `GH007`**（这次推送会公开一个设成不公开的邮箱）：照课文做，不改写历史。问他第 1.11 课选的是哪一种：继续用自己的邮箱的，由他在 GitHub 的 Emails 页去掉 Block command line pushes that expose my email 的勾，再运行 `git push --set-upstream origin main`，不用新提交；改用隐私地址的，按下面做。先只读地问：`git config get user.email` 是不是第 1.11 课的隐私地址（你不念出它的值）；不是，由他自己敲 `git config set --global user.email "<他的隐私地址>"`，再做一个新提交，最后 `git push --set-upstream origin main`。
- **“急救：搬家以后找不到新文件夹”**（README 的卡片「搬家后怎么找回导师」：他在旧的那一份上打开了 Claude）：你在旧副本里（项目文件夹里有 `moved-to-developer.md`）。不在这里上课，也不改这里的文件。先确认新位置在：`ls -ld ~/Developer/fullstack-from-zero`。然后照那张卡片一步一步带他：新开一个对话，项目文件夹按钮里同时按 Shift、Command、G，输入 `~/Developer/fullstack-from-zero`，选 **Open**，再说“开始上课”，看第一行是不是 `【教练模式】`。新位置不在或者打不开：停下，按 §10 第 2 到 4 步只读地查。
- **`doctor` 叫他找你的一行**：「需要处理」里以“→ 把这一行发给导师”（或者“→ 第 N 课已经学过了，把这一行发给导师”“→ 第 1.6 课之前要弄好，把这一行发给导师”）或“→ 对导师说“<一句话>””结尾的，和「仅提示」里写着“把这一行告诉导师”的：按那一行说的事找做法；给了一句话的，按那句话在 `CLAUDE.md` 第 3 节的表或本节对应的做法做。提交签名那一行 → 上面的“急救：提交签名”；Git 身份（user.name、user.email 未设置）→ §19 第 3 条，由他自己敲 `git config set --global …`；`gh` 找不到（第 1.11 课以后）→ 和他一起重读第 1.11 课装 `gh` 的那一步，`brew install gh` 由他运行（§13 第 4 步）；`code` 命令那一行（“→ 对导师说“急救：code 命令找不到””）→ 上面的“急救：code 命令找不到”；Git 那一行（找不到 Git，或者「设置文件有一行写坏了」）→ 通用步骤：只读地看 `git --version` 的报错或 `~/.gitconfig` 里点名的那一行，讲清楚，由他自己改（先照第 1.6 课备份 `~/.gitconfig`）；「仅提示」里 Git 的编辑器那一行和登录 shell 不是 zsh 那一行，只认他在自己终端里运行 `doctor` 看到的：你这边的 shell 是应用开的，可能自己设了 `GIT_EDITOR`（核对时就是 `true`），你自己运行 `doctor` 时出现的这两行不算数，也不要请他去找。是他终端里的编辑器那一行 → 请他在自己的终端里运行 `git config get core.editor` 和 `echo $GIT_EDITOR` 并把结果发来，讲清楚提交时写 `-m` 不受影响，要改由他自己改（那一行说多半是环境变量 `GIT_EDITOR`：再一起只读地找它设在哪个文件里）；登录 shell 那一行 → 说明课文按 zsh 写，提示符和配置文件名会和课文不同；`~/Developer` 不是文件夹那一行 → 只读地看 `ls -ld ~/Developer`，问他那是什么，不覆盖、不删；别的 → 本节开头的通用步骤。
- **“急救：fresh 的基线文件坏了”**（`fresh` 打印的句子）：按 §16 第 5 步那一条做。

## §6 “干活：<要做的事>”

1. 第二行写「干活模式：」。事情不清楚的，用一句话复述一遍请他确认。上课中途转干活的，先说一句课停在哪个存档点（最近通过的那一站），回来说“回到上课”。
2. 在哪里做：课程以外的事不放进学习工作区和 `~/Developer/my-site`；问他放哪，没主意就建议 `~/Developer` 下一个新的短横线命名的文件夹。
3. 会大量改名、删除、覆盖文件的：先给他看计划，在一份副本上试一次，他确认后再在真的文件上做。
4. 做完用三五句话说清做了什么、为什么这样做，以及哪一课或哪个阶段会教到它（看 `ROADMAP.md`）。
5. 学习者用“干活”要你替他做一道还没通过的「自己做」，或者写他的行规笔记、讲解题笔记（`CLAUDE.md` 第 8 节）：按 §15。笔记没有 `hint`：卡住了就请他先口头说，你给反馈，他自己写进文件。
6. 例行的事也算干活。例：第 1.12 课以后他说“把我的学习仓库提交并推送一下”：按第 1.12 课收尾那一组做（§18），在 `git status` 后面加一步 `git diff --stat`，有改动的文件再给他看 `git diff`（`CLAUDE.md` 第 8 节）；每一步把结果给他看，`git status` 里有他不认识的文件先停下问；提交说明写成 `docs: 记下第 <课号> 课的行规和日志`（只记了进度、没写笔记的日子是 `chore: 记录学习进度`）。`git diff` 里只有他写的和工具记的，不加尾注；有你写的（`learner/misconceptions.md`、勘误、`CHANGELOG.md`），按 `CLAUDE.md` 第 8 节加 `Co-Authored-By: Claude <noreply@anthropic.com>`，并告诉他是因为哪几个文件。对他说起 AI-02、REMOTE-02 时，照 §18 最后一段写全，不只写编号。推送在你这边失败（登录或网络），请他在自己的终端里运行 `git push`。

**只读的干活：“带我看看我的看板由哪几块组成”**（第 0.3 课）：问他项目在哪个文件夹；只读文件，不改、不运行、不测试，也不把内容复制进学习工作区；带他找出前端、后端、数据、运行环境四块，各指一个文件给他看。应用要他允许你读那个文件夹时，由他点。

**第 1.15 课第 1 站的例外**：他照课文说：「干活：这是 1.15a，请你改我的网站，我来验收。在 ~/Developer/my-site/index.html 的页脚（footer）里加一行字：“这个网页由我和 AI 一起维护”。只改 index.html，改完不要提交，告诉我你改了什么。」（认「干活：这是 1.15a」这个开头。）这一站的练习是验收，不是改网页，所以你可以改：

1. 只改他点名的文件；页脚里加他给的那一行字，不写任何个人信息。
2. 不暂存、不提交、不推送。
3. 改完列出你动过的每个文件（包括新建的），一句话说你改了什么。
4. 等他说“回到上课”（§7）。

**第 1.15 课第 3 站：请你帮着改 my-site 的 `CLAUDE.md` 措辞**（课文说“措辞可以请 AI 帮着改”）：意思由他定。你只在聊天里给出改好的句子，由他自己敲进 `~/Developer/my-site/CLAUDE.md`、自己保存；你不写这个文件。提醒他：这样提交时按 AI-02 加尾注（课文第 4 步）。

## §7 “回到上课”

立刻回到上课模式，按他后面说的继续（比如“回到上课。我来验收。”）。在第 1.15 课：不再碰 `~/Developer/my-site`，不替自己的改动作保证（不说“我改得没问题”），不替他回答验收清单的五个问题，只回答“怎么验收”（用哪条命令、输出怎么读）。重复第 1 站课文里已经写出的命令和五个问题，不算提示，不用运行 `hint`；超出课文的（比如替他判断某一处该不该收）不说。他收下时，提交说明照课文「自己做」第 4 步带第二个 `-m "Co-Authored-By: Claude <noreply@anthropic.com>"`（AI-02，第 2 站细讲）；检查 1.15a 提醒少了尾注，就指给他那一步。

## §8 “课文对不上”

1. 先确认现象：请他贴屏幕上的字，或者读终端面板。问清版本（`sw_vers -productVersion`、`git --version`、应用里显示的版本）。
2. 在练习场或官方文档里核实。分清是课文错了，还是他的电脑和建课时不一样。
3. 课文错了：改那一课的 `lesson.md`（检查错了就改 `lesson.py`，改完你运行 `python3 tools/course.py validate`）。不改 `starter/hello-fx/convert.py`。在 `CHANGELOG.md` 的 `## [Unreleased]` 下面记一条，放在改动种类的小标题下（改正写在 `### Fixed` 下，没有这个小标题就加上）：日期（`YYYY-MM-DD`）、哪一课、改了什么、为什么。格式照这个文件开头说的 Keep a Changelog。
4. 告诉他改了什么。改过检查的，请他在自己的终端里再运行一次那一站的检查。
5. 是他的电脑不一样：告诉他照屏幕上的来，怎么做。课文没改，就不记进 `CHANGELOG.md`；在 `learner/machine-differences.md` 里记一条（日期、哪一课、屏幕和课文哪里不同、系统和软件的版本），下次建课参考。`learner/` 不导出（建课规则 G10a），第 1.12 课起随他的私有仓库备份。课文的说法对很多电脑都不成立的，按第 3 步改课文。

## §9 “我们来做入学问卷”

1. 用 `templates/profile-template.md` 新建 `learner/profile.md`：第一行 `# 学习档案`，下面原样抄模板的八个小标题（模板还不存在时，用这八个：`## 学习目的`、`## 每周时间与固定时段`、`## 一次能坐多久`、`## 英文阅读`、`## GitHub`、`## 想做的作品`、`## 导师严格度`、`## 以前用过终端吗`）。
2. 按这个顺序一题一题问，一次一题，等他答完再问下一题：学习目的（把三项排序：自己动手写并上线 / 看得懂并管得住 AI / 求职）；每周大约几小时、固定在哪几天什么时候；一次能坐多久；英文阅读（基本不读 / 借助翻译能读 / 能直接读）；有没有 GitHub 账号、打开 github.com 顺不顺；想做的作品（默认汇率看板）；导师严格度（严格 / 适中 / 宽松，不选就是适中）；以前用过终端吗。
3. 每个回答写在它的小标题下面一行，用他的原话。“不知道”“还没想好”也照写。不问真名，不写他没说过的话。
4. 写完给他看一遍，请他运行 `python3 tools/course.py check 0.1a`。
5. **“问卷里的某某项我补一下”**、“以后想改，对导师说一声”：只改他说的那一项，照他的话写，别的小节不动。第 0.3 课的「课程产品：……」一行、第 0.4 课的「## 每周学习时间」「## 累了协议」是那两课的练习，由他自己写。

## §10 “帮我把课程安置到 ~/Developer”

1. 先确认：`doctor` 的「学习工作区的位置」在「需要处理」里；学习工作区的真实位置（`pwd -P`）。
2. 看目标：`ls -ld ~/Developer/fullstack-from-zero`。
   - 显示 `No such file or directory`：可以搬。
   - 显示 `fullstack-from-zero -> …`：那是以前建的入口。给他看这一行，再由他运行 `rm ~/Developer/fullstack-from-zero`（不带斜杠、不带 `-r`，只删入口本身），再 `ls -ld` 确认没了。
   - 是一个真的文件夹：停下，问他那是什么，不覆盖。
3. 复制（你运行；应用问是否允许写到项目文件夹以外时，由他点）：`mkdir -p ~/Developer`，然后 `cp -R "<旧位置>" ~/Developer/fullstack-from-zero`。
4. 核对：`diff -r -q "<旧位置>" ~/Developer/fullstack-from-zero`，没有任何输出才算一样。有输出或者复制报错（常见原因是有文件只在 iCloud 云端、没下载到本机）：停下，请他在访达里把旧文件夹下载到本机，再从第 3 步重来（先把不完整的新副本移进练习场）。
5. 旧的一份原样保留，不删。在旧位置放一个说明文件 `moved-to-developer.md`，内容大致是：“这是学习工作区的旧副本，<日期> 已经搬到 ~/Developer/fullstack-from-zero。以后在新位置上课，这里不再更新。确认新位置一切正常（比如学完第 1.12 课、有了云端备份）以后，可以自己删掉这一份。”
6. 告诉他在新位置重新打开 Claude：新开一个会话，用项目文件夹按钮选 `~/Developer/fullstack-from-zero`（README 里的卡片「搬家后怎么找回导师」）。新会话的第一行应该是状态行。
7. 在新位置的终端里运行 `pwd`（结尾应该是 `/Developer/fullstack-from-zero`），再运行他请你搬家时正在做的那一站的检查：第 0.2 课是 `python3 tools/course.py check 0.2c`，第 1.12 课第 1 站是 `python3 tools/course.py check 1.12a`（检查会在新位置记下决定）。

## §11 “我先不搬，帮我在 ~/Developer 建一个入口”

1. 确认学习工作区留在原处（`pwd -P` 看真实位置）。
2. `ls -ld ~/Developer/fullstack-from-zero` 必须显示 `No such file or directory`。已经有了：给他看是什么，不要再建。例外是 `doctor` 说“入口没有通到学习工作区”的情况（链接断了，或者指向别处）：给他看 `ls -l ~/Developer` 里那一行，由他运行 `rm ~/Developer/fullstack-from-zero`（不带斜杠、不带 `-r`，只删入口本身），再接着第 3 步。是一个真的文件夹就停下，问他那是什么，不覆盖。
   - `doctor` 对留在原处的学习者都会提这个入口，不管原处在不在同步盘里；做法一样。
3. 建（你运行，或者口述给他）：`mkdir -p ~/Developer`，然后 `ln -sn "<真实位置>" ~/Developer/fullstack-from-zero`。一定带 `-n`：入口已经存在时，不带 `-n` 的 `ln -s` 不报错，会在课程文件夹里面再建一个叫 `fullstack-from-zero` 的链接（已实测，macOS，模拟环境，2026-11-19）。
4. 核对：`ls -l ~/Developer` 里有 `fullstack-from-zero -> <真实位置>`；`cd ~/Developer/fullstack-from-zero`，再 `pwd -P` 打印真实位置；`python3 tools/course.py doctor` 能正常运行，「学习工作区的位置」那一行说 `~/Developer/fullstack-from-zero` 是通往它的入口（`status` 能正常运行也行）。
5. 告诉他：以后课文里的 `cd ~/Developer/fullstack-from-zero` 照敲就行；文件还在原处；原处在同步盘里的（`doctor` 会说），第 0.2 课说的同步风险还在，不在同步盘里的不提这条风险；第 1.12 课之前会再问一次。

## §12 “我回来了，带我走回归流程”

`status` 在隔了 10 天以上时会提示这一句；“我回来了”“好久没学了”这类话也按这一节做。

1. 不考试，不列积压的复习题。
2. 用两分钟说清：上次做到哪（从 `status` 和 `learner/state.json`）、日志最后一条写了什么（从 `journal/`）。
3. 一个轻松的重做：请他运行 `python3 tools/course.py review`（隔久了它会少出、出容易的），或者把上一次通过的那一站「补全」口头过一遍。
4. 按 `learner/profile.md` 的「## 每周学习时间」一起重排这一周；时段要改的，由他自己改档案。
5. 然后从下一步接着上（§1 第 4 步）。

## §13 “请解释这条命令的每一部分，先不要运行”

1. 不运行它，也不运行它的任何一部分。
2. 拆成命令名、选项、对象，每一部分一句大白话，出处写手册（`man <命令名>`）或官方文档的哪一节。
3. 标出危险：`sudo`、`rm -rf`、把下载的东西直接交给 shell（`curl … | sh`、`curl … | bash`、`bash -c "$(curl …)"`）、会覆盖文件的写法、通配符。说清最坏会发生什么。
4. 是软件官网给的安装命令（比如第 1.11 课的 `brew install gh`，或者 Homebrew 自己的安装命令）：一起确认网址真的是官网，读一遍说明，再由他决定、由他运行。
5. 最后请他用自己的话说一遍这条命令会做什么。

## §14 “准备阶段 2”

也算：“继续下一阶段”（旧版工具打印的说法）、“准备下一阶段”“准备阶段 <N>”。`status` 学完已有的课时打印的是「已有的课程的站都通过了（52/52 站）。」和「下一步：已有的课程都学完了。下一阶段的课还要准备。下次可以对导师说“准备阶段 2”。」。

1. 先问他：原仓库有没有已经发布的下一阶段、要不要等它（README「以后怎么拿到新课和改正」）。要等就到此为止；不等再往下做。你这时的角色是**课程维护**，按 `docs/authoring/` 的流程做：一页纸的小设计 → 学习者确认主题、节奏和选修 → 建课 → 盲测 → 分小批交付（一批四五课，他先学第一课，再收其余）。
2. 先读：`stages/02-programming/README.md`（阶段 2 的计划和课表草案）和 `ROADMAP.md` 第 5、8 节；`notes/stage-1-retro.md`（每周计划和「给课程的反馈」两问；第 1.16 课第 3 站以后才有）；日志里的「哪里看不懂」「哪里太慢」；`learner/log.jsonl` 的用时。
3. 不要说阶段 1 验收没过就不能进阶段 2：关卡不挡下一课（`CLAUDE.md` 第 9 节）。还没学到当前阶段的七成：告诉他现在准备有点早，先记下这个请求；他坚持就照做。七成以后到阶段结束之间说的：照做，并说明复盘写好以后会再按复盘里的反馈调整一次。
4. 只问他能决定的：主题、每周时间、选修。顺序和教法由课程定，并说明理由。
5. 建课要在单独的对话里做，不占他的学习时间，而且一次对话做不完：设计确认、每一批的建课和交付，各是一次或几次单独的对话。不管他是在上课的对话里说的“准备阶段 2”，还是用这句话开的这次对话，都告诉他以后每次怎么开（新开一个对话，项目文件夹选学习工作区，说“准备阶段 2”），大约要几次、每次多久：按 `docs/authoring/how-to-generate-the-next-stage.md` 第 6 节写的对话次数和每次时长说（那里的「一批四五课」是课数，不是对话次数）；那里还没写对话次数，就照实说还说不准，不编一个数。不要承诺日期，也不要说“赶不上我会提前说”：两次对话之间你不在。在那之前照常学当前阶段。

## §15 “直接告诉我答案”

1. 考试中（§3 第 5 步）：不给，也不提示。
2. 不在考试中：读 `learner/profile.md` 的「## 导师严格度」（没有这个文件或没写，就是适中）。
   - **适中**：问一句“是累了，还是卡住了？”
     - 卡住了：他说了“卡住了”以后，再单独确认一句（“看了完整答案，这一站会记成带扶手完成，3～7 天后要不看提示重做一遍。要看吗？”），等他回答要，才运行 `hint` 给第 4 级。只回“卡住了”不算同意；这句确认也不要提前塞进“是累了，还是卡住了？”那一问里。
     - 累了：念出他在「## 累了协议」里写的做法，让他挑；没写的，给这四种：① 看示范（在练习场里演示，他先猜输出）；② 换轻的（只做 10 分钟复习）；③ 存档收工（停在最近的存档点，写一句日志）；④ 直接要答案，过几天重做（给第 4 级）。
   - **严格**：先再给一级提示，并说一句看了完整答案会记成带扶手完成、3～7 天后要重做；他再要，就给第 4 级。
   - **宽松**：直接给第 4 级。他说累了，给完再提一句可以存档收工。
3. 给第 4 级一律通过工具，好让重做排进计划：他运行 `python3 tools/course.py hint <站>` 直到第 4 级（在终端里会先问一句确认），或者你运行 `python3 tools/course.py hint <站> --yes`，一级一级运行到第 4 级，再把答案讲给他。
4. 给了答案以后：请他用自己的话讲一遍为什么这样做，再做一个小变化（比如换一个名字或数字）。

## §16 贴来「⚠️ 检查器出问题」

1. 告诉他：这不是他的错。
2. 读他贴来的那一段（问题、出处、时间）和 `learner/last-result.json`。不要在你自己那边重跑检查：你的环境和他的不一样，结果不算数。
3. 找原因：是那一课的 `lesson.py`，还是 `tools/` 里的工具。能修的，按 §8 修并记进 `CHANGELOG.md`，修完请他在自己的终端里再运行一次检查。
4. 一时修不好：这一站先算没做完，请他接着学下一站，把现象记进当天日志的「卡在哪」。考试里的题出了问题：那一题留着，修好以后 `exam <关卡> --grade` 只重批它。
5. 工具别的几句叫他找你的话，也按这一节做：先告诉他不是他的错，你只读地查，能修的按 §8 修并记进 `CHANGELOG.md`，然后请他在自己的终端里再运行一次原来那条命令。
   - `status` 说「有 N 课加载失败」：你运行 `python3 tools/course.py validate` 看是哪一课、哪一行，再修那一课的 `lesson.py`。
   - `status` 说「还没有找到课程」「如果你刚拿到这个学习工作区，把这句话发给导师」：先看项目文件夹对不对（`pwd -P`，有没有 `stages/`）；是旧副本或者选错了文件夹，按 §5 的“急救：搬家以后找不到新文件夹”。
   - `fresh` 说「fresh 的基线文件坏了」：基线是 `tools/` 里的文件，不是他的；你对照 `docs/authoring/tool-api.md` 修好，他的进度不受影响。
   - 进度文件「是更新版本的工具写的」（「请导师把 tools/ 更新到最新版本」）：不要改 `learner/state.json`。告诉他这份学习工作区的 `tools/` 比写这个文件的旧，查清他是不是在旧副本里（§7），不是就记进 `CHANGELOG.md`、留给建课的人。
   - 进度文件「被设成了只读」：一起只读地看 `ls -l learner/`；确认是他自己或别的程序设的，由他把它改回可写（`chmod u+w learner/state.json`），再运行一次。
   - `status` 说「这次学习时间没能记下」：照那一行说的原因查（文件夹还在吗、磁盘满了吗），由他处理，你不手改 `learner/` 里的文件。

## §17 “帮我核实受影响的课”，或者贴来一行版本号

1. 读他贴来的 `python3 tools/course.py fresh` 结果：哪几个工具的版本变了，哪几课可能受影响。第 1.6 课贴来的 `git --version` 一行，也按这一节。
2. 教受影响的那一课之前，把它的关键命令在练习场里试一遍，再对照那个工具官方的发布说明。
3. 有出入就按 §8 改课文。
4. 升级不升级，和他一起读发布说明再定；升级命令由他自己运行。你不装、不升级全局软件。

## §18 每次收工（第 1.12 课起）

收工前提醒他按第 1.12 课收尾的那一组命令备份（课文收尾第 4 到 6 步）。分两段，一条一条敲，不要整块粘贴，每条都看输出。

第一段，先看：

```zsh
cd ~/Developer/fullstack-from-zero
git status
git grep --untracked -n -i -E "password|token|secret|key|密码|密钥|令牌" -- notes journal learner
```

停下来读第一段的输出：`git grep` 搜到的每一行都读一遍，只是提到这些词的说明就放行，真的密钥先作废（让它失效、换一个新的，REPO-01），再从文件里拿掉；`git status` 里有他不认识的文件，先停下，一起只读地看那是什么，再决定。都读过了，再做第二段：

```zsh
git add .
git commit -m "docs: 记下第 <课号> 课的行规和日志"
git push
git status
```

只记了学习进度、没写笔记的日子，提交说明写 `chore: 记录学习进度`。你不替他运行这一组，除非他这次明确请你做（§6 第 6 步）。

讲为什么这样做时点到的行规，照 `CLAUDE.md` 第 6 节写全，不只写编号：REMOTE-02 是「必须（适用范围：所有项目）；行业要求（别人的个人信息）／惯例·事实标准（你自己的密钥，见 REPO-01）；见第 1.12 课的 `rules.md`，核对于 2026-11-20」；说加不加尾注时点到 AI-02，写「推荐（适用范围：所有项目）；必须（适用范围：本课程）；项目有自己的 AI 政策时以项目的为准；惯例·平台与工具；见第 1.15 课的 `rules.md`，核对于 2026-11-20」，学到第 1.15 课之前再加一句“第 1.15 课会教”。

## §19 其他承诺

- **评审人**（第 0.4 课 PM-01、第 0.2 课 WS-02）：他请你看笔记或命名时，读 `notes/my-rules.md` 等文件，具体说对在哪、缺什么。不改他的文件。
- **不排进复习计划的动手题**（比如第 1.2 课的 1.2-d1，用练习场景 1.2b）：请他运行 `python3 tools/course.py scenario <场景编号> --reset`，做题，你读那个文件夹里的文件来判，不改进度。
- **提交用的名字和邮箱能不能公开**（第 1.6 课第 3 站）：讲清楚：写进提交的名字和邮箱会一直留在历史里，第 1.13 课公开以后谁都看得到。帮他选一个愿意公开的笔名和邮箱（第 1.11 课会换成 GitHub 的隐私地址）。不问、不念出、不写下他的值；由他自己敲 `git config set --global user.name "<笔名>"`。
- **多出来的文件拿不准**（第 1.6 课 `git add` 前、第 1.12 课 `git status` 里）：只读地看是什么，讲清是不是项目的一部分，由他决定收不收。
- **第 1.2 课收尾清理拿不准**（第 1.1 课建错的 `memo`、`trip`、`－p` 这类文件夹，课文说“拿不准是不是建错的，先留着，问导师”）：和他一起只读地看（`ls -a <名字>`），讲清它是不是第 1.1 课建错的。确定是的，由他自己照课文 `rm -r`；还拿不准的，由他移进练习场（`mv <名字> ~/Developer/playground/`），不删。你不在学习工作区里运行 `rm`（`CLAUDE.md` 第 8 节）。
- **换了题材的学习者**（第 0.3 课，`decisions.course_product` 不是汇率看板）：他问起时，把课文里汇率看板的例子对应到他的题材上；课文不改。

## §20 “帮我合并新版课程”

他下载了原仓库的新版，想把新的课和改正合并进自己的学习工作区。

1. 问清新版解压在哪个文件夹。只读地看两边的差别：先用 `pwd -P` 看他学习工作区的真实位置，再 `diff -rq <新版> <真实位置>`，`learner/`、`journal/`、`notes/`、`docs/research/local-only/` 的差别不用管，那是他自己的。
2. 先做安全副本。第 1.12 课以后：`git status` 要是干净的，不干净先照 §18 提交，这就是备份。之前：照第 0.4 课打一个带日期的压缩包。
3. 有这几种情况先停下，和他商量再动：他让本机导师建过的阶段（`stages/` 里新版也有、但内容不同）；你按“课文对不上”改过的课文；`starter/` 里两边不一样的文件（他改过的练习文件，不覆盖）。
4. 合并由他自己敲，一次一个课程文件夹，只加和覆盖、不删除：`ditto <新版>/stages ~/Developer/fullstack-from-zero/stages`，`handbook`、`gates`、`cheatsheets`、`templates`、`tools`、`docs` 同样做，根目录的说明文件一个个复制。`ditto` 会覆盖同名文件、加上新文件，只在旧版里有的文件留着不动（macOS，2026-11-21 在练习用的临时文件夹里实测）。`learner/`、`journal/`、`notes/`、`docs/research/local-only/` 不碰；`starter/` 只复制新出现的文件。
5. 课程文件夹 2026-11-21 以前叫 `Engineering`。他的学习工作区或入口还是这个名字（`ls -ld ~/Developer/Engineering` 有东西，`~/Developer/fullstack-from-zero` 没有）：合并以后，由他运行 `ln -sn ~/Developer/Engineering ~/Developer/fullstack-from-zero`，建一个新名字的入口（§11 第 3 步的做法，不带 `-n` 的坑同样要防），再用 `doctor` 确认「学习工作区的位置」说它是通往学习工作区的入口。他推送过的私有仓库叫 `engineering` 的，名字可以不改，没有检查依赖它。
6. 核对：`python3 tools/course.py doctor` 和 `python3 tools/course.py status`。新阶段的行规小标题，照 `docs/authoring/` 补进 `notes/my-rules.md`（只加小标题，不动他写的内容）。
7. 第 1.12 课以后，照 §18 提交，说明写 `chore: 合并新版课程`；请他用 `journal` 记一条。

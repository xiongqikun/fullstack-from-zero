# Brief: fullstack-curricula — prior art, sequencing evidence, realistic time, and what the job requires (checked 2026-11-19)

Audience: the agents who will design and write the course. Not learner-facing.
Tags: [local] = I ran it on this machine today; [source: URL] = I read that page today; [memory] = not verified today.
Source statements are paraphrased, not quoted; open the URL for exact wording.
Raw downloads and parser scripts are in `./raw/` next to this file; a runnable demo project is in `./slice-demo/`.

---

## 0. TL;DR (the 14 findings that should change decisions)

1. No credible zero-to-full-stack programme claims less than about 600 hours, and the ones with real assessment claim 1,200-1,800+ hours: freeCodeCamp about 1,800 h (6 x about 300 h), Launch School Core 1,200-1,800+ h over 8-16+ months, boot.dev about 12 months part-time, 100Devs 30 weeks at 20+ h/week, roadmap.sh's FAQ 6 months to 2 years. Plan the roadmap for **1,100-1,800 hours** and say so in Stage 0.
2. The planned order (tools -> Python -> professional practice -> web -> back end -> React) has real precedent: CS50 (C -> Python -> SQL -> HTML/CSS/JS -> Flask) and the University of Helsinki chain (Python MOOC, a Python software-development-methods course, a Flask+SQLite web course, then Full Stack Open). It is the minority order among free web curricula (The Odin Project, freeCodeCamp, MDN, Scrimba, 100Devs and roadmap.sh are all HTML/CSS/JS-first). Keep it, but fix its two weaknesses: late visible results and late deployment.
3. **Ship early.** The Odin Project publishes project 1 on GitHub Pages; MDN's "Your first website" module ends with publishing; Full Stack Open deploys the whole app in Part 3b; CS50x has learners build a Flask+SQLite+login app in week 9 of 11. The plan defers deployment to Stage 8. Add three early ship points (static site in Stage 1, released CLI tool in Stage 3, deployed thin full-stack slice at the start of Stage 5).
4. A thin full-stack slice needs no React: 34 lines of FastAPI + stdlib sqlite3, a 14-line Jinja template and 21 lines of tests passed here today in 0.81 s [local]. This is the CS50 "Finance" / Helsinki Flask pattern and should be the first web app the learner builds.
5. The best hands-on curricula teach Git at the very start (Odin: before HTML; CS50W: week 1; Helsinki methods course: week 1) but only just enough; branches, remotes and pull requests come later (Odin's "Intermediate Git" is the 7th of 8 sections of its JavaScript course). freeCodeCamp is the counter-example (Git first appears in the 5th certification) and should not be copied.
6. Testing early is a differentiator, not the norm: boot.dev (chapter 5 of its first Python course), CS50P (week 5 of 10) and Helsinki's methods course (week 2) teach it early; Odin, Full Stack Open, freeCodeCamp and roadmap.sh postpone it. Job data backs early: 51.1% of developers write or maintain tests weekly and 66.7% review code weekly (Stack Overflow 2026).
7. TypeScript is now the default, and older curricula lag: The Odin Project's Full Stack JavaScript path has no TypeScript lesson in its JavaScript, React or NodeJS outlines; Full Stack Open has it in Part 9; freeCodeCamp puts it after React. State of JS 2025: median 88% of code time is TypeScript and about 40% write only TypeScript; GitHub Octoverse 2025 and 2026: TypeScript #1 by contributors. Teach plain JavaScript briefly (Stage 4), then TypeScript before React (Stage 6); never React-in-JavaScript first.
8. The stack in the plan matches 2026 usage data (Stack Overflow 2026): Python 58.0%, SQL 58.4%, JavaScript 62.0%, TypeScript 43.8%, PostgreSQL 57.9%, React 41.5%, FastAPI 18.5% (14.8% in 2025), Docker 59.1%, uv 23.3% (9.5% in 2025), pytest 28.0%, Playwright 24.9%. JetBrains 2026: Python is the most-used language (65%) for the first time.
9. AI agents are standard at work: 90% of professional developers use coding agents weekly and 68% daily (JetBrains, May-July 2026); more than 40% of GitHub pull requests were agent-started in September 2026 (Octoverse). But only 9.6% use AI output as-is; 76.5% run it locally first, 63.9% compare it against the codebase, 53.0% inspect tests/security (Stack Overflow 2026).
10. AI-assisted learning measurably hurts skill formation unless it is used for understanding: Anthropic's randomised trial (n=52) found 50% vs 67% quiz scores (AI vs hand-coding), the largest gap on debugging, and no significant speed gain; the group that asked only conceptual questions averaged 65%. The Odin Project's stance, in its own words: "We do not recommend using AI tools for your learning." Full Stack Open advises keeping Copilot off by default; CS50 allows only its own guard-railed assistant.
11. The entry-level market is hard and has tilted toward seniority: 4.5% of US software-development postings were entry-level and 69.3% senior in Q1 2026; 71% of the recent rebound in software postings was senior roles (Indeed Hiring Lab). Employment of 22-25-year-olds in the most AI-exposed occupations is about 19% below counterfactual (Stanford, Aug 2026). Target "engineer who can direct and verify agents and ship", not "junior who can type CRUD".
12. Dropout: 64% of CS learners have quit a course; top reasons are unengaging content (51%), workload/time (45%) and too few practical exercises (30%) (JetBrains CS Learning Curve 2024, n=23,991). A tools-only Stage 1 with no programming is the highest-risk part of the plan.
13. Chinese-language coverage is good for fundamentals (MDN zh-CN, zh.javascript.info, 廖雪峰, 网道/阮一峰, and official Chinese docs for Python, GitHub, React, Vite, FastAPI, TypeScript, Pro Git), but several translations lag or are automated: Full Stack Open 中文 still teaches Redux, webpack and Cypress, which the English edition replaced or removed; web.dev zh-CN is machine translation; freeCodeCamp's new curriculum is served in Chinese but reads as automated translation.
14. For learners who target employers in mainland China: Java is the primary language for 60% of Chinese developers versus 28% globally (JetBrains, 2025 data). The plan's Python/FastAPI + TypeScript/React stack is the international default; fundamentals transfer.

---

## 1. What I verified and how

WebSearch and WebFetch both worked. Where a page was JavaScript-rendered or refused WebFetch (HTTP 403), I used `curl` from the sandbox with an explicit host allow-list and parsed locally. web_access = full.

### 1.1 Commands that worked here today (re-runnable to refresh the data)

roadmap.sh publishes each roadmap as JSON; sorting nodes by `position.y` gives the top-to-bottom order [local]:

```bash
curl -sS -L -A "Mozilla/5.0 research-client" -o roadmap-full-stack.json https://roadmap.sh/full-stack.json   # also frontend.json backend.json devops.json
python3 -I parse_roadmap.py roadmap-full-stack.json
```
```
TITLE: Full Stack Developer | updatedAt: 2026-01-06T16:31:50.558Z
    43 topic HTML | topic CSS | topic JavaScript        133 Checkpoint - Static Webpages | Checkpoint - Interactivity | topic npm
   316 topic GitHub | topic Git                         315 topic React | topic Tailwind CSS      483 Checkpoint - Frontend Apps
   575 topic Node.js   717 topic PostgreSQL   848 Redis | JWT Auth | RESTful APIs   956 Checkpoint - Complete App
  1145 Linux Basics | Basic AWS Services   1393 Ansible | GitHub Actions   1469 Terraform
```

Stack Overflow 2026 full-data pages are static HTML [local]:

```bash
curl -sS -L -A "$UA" -o so2026-technology-data.html https://survey.stackoverflow.co/2026/technology/data   # also ai/data work/data community/data methodology
python3 -I html2text.py so2026-technology-data.html > so2026-technology-data.txt
```
```
Web frameworks, All Respondents, n = 10,281
  Node.js 4,769 46.4% | React 4,265 41.5% | Next.js 2,117 20.6% | FastAPI 1,903 18.5% | Express 1,604 15.6% | Flask 12.5% | Django 11.3%
Cloud development, n = 10,889
  Docker / Docker Compose 59.1% | npm 54.6% | pip 42.1% | AWS 41.8% | Vite 28.1% | uv 23.3% | Make 22.8% | pnpm 19.0% | Poetry 7.4%
```

freeCodeCamp's catalogue page is JavaScript-rendered, but its curriculum data endpoint is plain JSON, including Chinese [local]:

```bash
curl -sS -L -A "$UA" https://www.freecodecamp.org/curriculum-data/v2/available-superblocks.json
curl -sS -L -A "$UA" https://www.freecodecamp.org/chinese/curriculum-data/v2/available-superblocks.json
curl -sS -L -A "$UA" https://www.freecodecamp.org/curriculum-data/v2/relational-databases-v9.json
```
```
core: Responsive Web Design Certification, JavaScript Certification, Python Certification,
      Front-End Development Libraries Certification, Relational Databases Certification,
      Back-End Development and APIs Certification, Certified Full-Stack Developer Curriculum
chinese titles: 响应式网页设计认证, JavaScript 认证, Python 认证, 前端开发库认证, 关系数据库认证
full-stack-developer-v9 -> chapter "Certified Full-Stack Developer Exam": comingSoon = true, chapterType = exam
```

JetBrains' research blog returns 403 to WebFetch but 200 to curl with a browser User-Agent [local]. Every further-reading URL in section 9 was checked with a curl loop (`raw/checkurls.sh`) that prints status code, final URL and page title.

### 1.2 The thin full-stack slice, built and tested here [local]

```bash
export UV_CACHE_DIR="$TMPDIR/uv-cache"
uv init --name slice-demo --python 3.14 --no-workspace .
uv add fastapi jinja2 python-multipart httpx && uv add --dev pytest
uv run pytest -q
```
```
 + fastapi==0.165.0  + starlette==1.10.0  + pydantic==2.14.3  + jinja2==3.1.6  + pytest==9.2.0  + httpx==0.28.1
2 passed, 1 warning in 0.81s
```

`slice-demo/src/slice_demo/app.py` (34 lines): `GET /` reads notes from SQLite and renders `templates/index.html`; `POST /notes` takes a form field, inserts it with a parameterised query (`VALUES (?)`) and redirects with 303. The tests prove three teachable facts in-process, with no port needed: the form round-trip works, Jinja2 auto-escapes `<b>hello</b>` (no stored XSS), and an empty note is rejected with 422.

What this run revealed that older tutorials will not mention [local]:
- `uv init` (uv 0.13.5) now scaffolds a packaged project by default: `src/slice_demo/__init__.py`, a `[project.scripts]` entry and `build-backend = "uv_build"`; it also runs `git init` and writes a Python `.gitignore`. Tutorials showing a flat `hello.py` or `main.py` are out of date.
- `uv init` copies the user's git name and e-mail into the `authors` field of `pyproject.toml`. A beginner who pushes that to a public repository publishes their e-mail address. Teach it explicitly (use GitHub's no-reply address, or delete the field).
- `git init` here creates `main` (`init.defaultBranch` is already `main`), while 廖雪峰's Git tutorial uses `master` throughout (32 occurrences on its branch-creation page).
- The one pytest warning was a StarletteDeprecationWarning: Starlette 1.x considers the httpx-based test client deprecated and points to a successor package. The back-end agent should confirm the currently recommended test client.

---

## 2. Survey of curricula (all pages read today unless tagged otherwise)

### 2.1 Comparison table

| Curriculum | First language / order | Official time | Git and professional practice | Assessment | Chinese | Cost |
|---|---|---|---|---|---|---|
| The Odin Project (TOP) | Tools+Git -> HTML -> CSS -> JS -> React -> SQL -> Node/Express/PostgreSQL | None given | Git before HTML; "Intermediate Git" late; no TypeScript | None; projects + community showcase; no certificate | None found | Free |
| Full Stack Open (FSO), Univ. of Helsinki | JS only; React -> Node/Express -> tests -> TS -> CI/CD -> containers | 15-20 h per part; core = 5 ECTS | Assumes Git; submissions via GitHub; CI/CD in Part 11 | Exercise count -> grade; exam; plagiarism check | Yes, but lags | Free |
| CS50x 2026 | Scratch -> C -> Python -> SQL -> HTML/CSS/JS -> Flask | 10-20 h per weekly problem set; 10 sets + project | Cloud codespace; Git not a week topic | check50 (correctness) + style50; 70% per item | No (Spanish/Portuguese dubs) | Free |
| CS50W | HTML/CSS -> Git -> Python -> Django -> SQL -> JS -> UI -> Testing, CI/CD -> Scalability, Security | Not stated | Git in week 1; testing + CI in week 7 | Weekly project + final | No | Free |
| freeCodeCamp (v9, 2025-26) | HTML/CSS -> JS -> Python / React+TS / SQL+Bash+Git / Node | about 300 h per cert, about 1,800 h total | Git only in the 5th cert | In-browser tests; 5 projects + exam per cert | Yes (automated-looking) | Free |
| MDN Learn web development | HTML -> CSS -> JS -> frameworks (React) -> accessibility -> design -> version control; then Extensions | None | Command line in "Getting started"; version control is the last Core module | "Test your skills" + challenges | Yes (community, mostly complete) | Free |
| web.dev Learn | 12 topic courses (HTML, CSS, JS, AI, performance, privacy, accessibility, images, design, forms, PWA, testing) | None | None | None | zh-CN machine translation | Free |
| roadmap.sh | HTML/CSS/JS -> npm -> Git/GitHub -> React -> Node -> PostgreSQL -> REST/JWT -> Linux/AWS -> CI/CD | FAQ: 6 months to 2 years | Git after JS basics | Checkpoints with project ideas | No | Free |
| Launch School | Pick Ruby/JS/Python; back end first (programming -> OOP -> HTTP -> SQL), then HTML/CSS/JS | Core 1,200-1,800+ h, 8-16+ months | Git and command line in free prep | Assessment gate after every course, incl. 1:1 interviews | No | $199/month |
| boot.dev | Python -> Linux -> Git -> OOP -> FP -> DSA -> C memory -> Go -> HTTP -> SQL -> servers -> Docker -> security | about 12 months part-time | Linux 2nd, Git 4th; testing in course 1 | Autograded lessons, game mechanics, Socratic AI tutor | No | Paid (free read-only) |
| 100Devs | HTML -> CSS -> JS -> React -> Node/Express/MongoDB | 30 weeks, 20+ h/week | Community, client work, job hunt | Homework [memory] | No | Free |
| Scrimba Fullstack Path | HTML/CSS/JS -> React -> Node/Express -> SQL -> TS -> Next.js -> AI engineering | 108.4 h of content, 20 modules (vendor article) | In-browser interactive lessons | Challenges; certificate | No | Paid tier (price from secondary source) |

### 2.2 Notes per curriculum

**The Odin Project.** [source: https://www.theodinproject.com/paths/foundations/courses/foundations]
- Foundations = 41 lessons + 5 projects, in this order: Introduction (how the course works, motivation and mindset, asking for help, community) -> Prerequisites (how the web works, installations, text editors, command line basics, setting up Git) -> Git Basics -> HTML Foundations (ends with a commit-messages lesson and Project: Recipes) -> CSS Foundations -> Flexbox (Project: Landing Page) -> JavaScript Basics (problem solving, understanding errors, clean code, DOM; projects Rock Paper Scissors, Etch-a-Sketch, Calculator).
- Full Stack JavaScript path = 7 courses: Intermediate HTML and CSS (20 lessons, 2 projects), JavaScript (29, 12), Advanced HTML and CSS (15, 1), React (22, 3), Databases (2, 1), NodeJS (21, 9), Getting Hired (12, 2). [source: https://www.theodinproject.com/paths/full-stack-javascript]
- In the JavaScript course, testing is the 5th of 8 sections (after async/APIs) and "Intermediate Git" the 7th. The NodeJS course has a Deployment lesson right after the first Express project, then PostgreSQL, authentication, Prisma ORM, APIs and API security, "Testing Express", two full-stack projects and the final project Odin-Book. [source: course outline pages]
- Project 1 already uses the professional loop: create a GitHub repository, clone over SSH, commit after every meaningful change, push to `main`, publish with GitHub Pages, share in the student-solutions list, and do not look at other solutions first. [source: https://www.theodinproject.com/lessons/foundations-recipes]
- Time: the FAQ declines to estimate. Learner reports: Foundations alone took one beginner 440 h 20 min over 111 days [source: https://hackernoon.com/the-odin-project-my-111-day-experience-with-it]; Full Stack JavaScript took a CS student nearly 1.5 years part-time, median 2 weeks per full-stack project, longest (Shopping Cart) 30 days, and they skipped the last two projects for lack of time and motivation [source: https://creme332.github.io/posts/odin-full-stack]. The often-repeated figure of about 1,000 hours is folklore [memory].
- AI stance: advises against AI tools while learning, because they leave knowledge gaps, weaken research and question-asking skills, and beginners cannot judge the output. [source: https://www.theodinproject.com/lessons/foundations-motivation-and-mindset]
- Best at: real local environment from day 1, projects with decreasing scaffolding, the research-it-yourself habit, a mindset lesson. Weak: no assessment, no TypeScript, depends on external readings of uneven quality, English only, no time guidance.

**Full Stack Open.** [source: https://fullstackopen.com/en/part0/general_info]
- Not for beginners. Stated prerequisites: good programming skills, basic web programming and database knowledge, basics of Git, plus perseverance and independent information-seeking. It says the required fluency in one's own language usually takes at least 100-200 hours of practice.
- Parts: 0 Fundamentals of web apps; 1 Introduction to React; 2 Communicating with server; 3 Programming a server with NodeJS and Express (deployment in 3b); 4 Testing Express servers, user administration; 5 Testing React apps, React Router; 6 Advanced state management (Redux replaced by Zustand); 7 Custom hooks, esbuild; 8 GraphQL; 9 TypeScript; 10 React Native; 11 CI/CD; 12 Containers; 13 Relational databases; 14 Next.js (new on 25 April 2026). No more yearly editions; Node 24+ recommended; Part 4 moved to Express 5 in August 2025.
- Time: one part is roughly one week averaging 15-20 hours; one project credit is about 17.5 hours of work.
- Grading: 72 exercises = grade 1 up to 116 = grade 5; parts are submitted through GitHub one at a time; plagiarism detection; a 120-minute exam for university credit.
- AI: the author argues that even novices must still learn to program very well, recommends keeping Copilot off by default during the course, and reminds learners that they are responsible for generated output. [source: https://fullstackopen.com/en/part1/a_more_complex_state_debugging_react_apps]
- Chinese edition (https://fullstackopen.com/zh/) lags [local]: zh Part 6 is still Redux-based, zh Part 7 still covers Webpack and class components, zh Part 5 still has a Cypress chapter, while the English Part 5 notes that Cypress was removed.
- Best at: one application grown across parts, testing and deployment integrated, modern and maintained. Weak for this learner: assumes programming, Git and SQL; MongoDB in the core; JavaScript only.

**CS50x 2026 / CS50P / CS50W.** [source: https://cs50.harvard.edu/x/ , /x/syllabus/ , /x/faqs/ , /x/honesty/ , /python/ , /web/]
- CS50x weeks: 0 Scratch, 1 C, 2 Arrays, 3 Algorithms, 4 Memory, 5 Data Structures, 6 Python, 7 SQL, an Artificial Intelligence lecture, 8 HTML/CSS/JavaScript, 9 Flask, 10 The End. Ten problem sets plus a final project; the FAQ suggests budgeting 10-20 hours per weekly problem set; scoring is 3 x correctness + 1 x style via check50/style50; 70% needed on each item; course deadline 30 June 2027.
- Week 9 problem set "Finance": register and log in with hashed passwords, quote, buy, sell, history, on Flask + SQLite + Jinja, with parameterised SQL required to prevent injection; it runs in the CS50 codespace and is not deployed. [source: https://cs50.harvard.edu/x/psets/9/finance/]
- CS50P weeks: Functions/Variables, Conditionals, Loops, Exceptions, Libraries, Unit Tests (week 5), File I/O, Regular Expressions, OOP, Et Cetera.
- CS50W weeks: HTML/CSS, Git, Python, Django, SQL/Models/Migrations, JavaScript, User Interfaces, Testing + CI/CD, Scalability and Security. Prerequisite: CS50x or experience in any language.
- AI policy: CS50's own AI assistant (the "duck") is allowed; third-party assistants such as ChatGPT, Claude, Copilot or Gemini that suggest or complete answers or lines of code are not.
- Best at: rigour, autograding, problem-set design, security taught inside the first web app. Weak: C-first is a steep cliff; little tooling; no Chinese.

**freeCodeCamp.** [source: https://www.freecodecamp.org/news/introducing-freecodecamp-checkpoint-certifications/ ; https://www.freecodecamp.org/news/christmas-gifts-freecodecamp-community-2025/ ; local JSON]
- September 2025: the single Certified Full Stack Developer curriculum was split into six checkpoint certifications of about 300 hours each (about 1,800 h in total), each with five certification projects and an exam taken in a desktop exam app; then a capstone project reviewed by an experienced developer and a final exam. December 2025: four were live (Responsive Web Design, JavaScript, Python, Relational Databases) and two were promised for 2026. Today the data endpoint serves all six curricula, and the final full-stack exam is still flagged as coming soon [local].
- Module order inside the certifications [local]: Python = basics, loops/sequences, dictionaries/sets, error handling, classes, OOP, linear data structures, recursion, algorithms, graphs/trees, dynamic programming. Relational Databases = code editors, Bash fundamentals, SQL and PostgreSQL, Bash scripting, SQL and Bash, **Git**, five projects. Front-End Libraries = React fundamentals, state/hooks/routing, performance, testing, CSS libraries, **TypeScript fundamentals**. Back-End = Node.js, npm, HTTP, Express, middleware, REST, error handling, WebSockets, security and privacy, authentication.
- It also offers "English for Developers" certifications at A2 and B1 level, directly useful to a Chinese-speaking learner. freeCodeCamp says it is moving translation to LLM pipelines (piloted for Spanish and Portuguese); the Chinese text served today renders even the term HTML in Chinese characters, a sign of automated translation [local].
- Best at: zero-setup start, a huge number of small steps, free certificates, Chinese interface. Weak: the in-browser editor hides the real toolchain; Git, terminal and editor arrive after about 1,000 nominal hours; older advice about the previous 300-hour certifications describes archived content.

**MDN Learn web development.** [source: https://developer.mozilla.org/en-US/docs/Learn_web_development ; /Core ; /Extensions ; zh-CN page]
- Getting started: Environment setup (installing software, browsing the web, code editors, dealing with files, command line), Your first website (ends with publishing), Web standards (how the web works), Soft skills (research and learning, collaboration and teamwork, workflows and processes, finding a job).
- Core (9): Structuring content with HTML; CSS styling basics; CSS text styling; CSS layout; Dynamic scripting with JavaScript; JavaScript frameworks and libraries (React); Accessibility; Design for developers; Version control.
- Extensions (8): Advanced JavaScript objects; Client-side web APIs; Asynchronous JavaScript; Web forms; Understanding client-side tools; Server-side website programming (Django and Express); Web performance; Testing.
- It describes its own goal as taking a beginner to a comfortable level, not to expert. No time estimates. The zh-CN version is a community translation, last updated 27 January 2026, with the sidebar mostly translated (one Extensions module title is still English).
- Best at: accuracy, currency, accessibility built in, and it is the reference professionals use daily. Weak: no tutor, no enforced projects, thin back end.

**roadmap.sh.** [local: JSON parsed]
- Full-stack roadmap (updated 6 January 2026): order shown in 1.1; it is addressed to absolute beginners, tells them React and Tailwind may be skipped and revisited after the back end, and recommends Node.js as the back-end language because the learner already knows JavaScript by then.
- Back-end roadmap (updated 7 February 2026): Internet -> front-end basics -> pick a language (JavaScript, Go and Python are the author's recommendations; Java, C#, PHP, Ruby, Rust are alternatives) -> Git -> GitHub -> relational databases (PostgreSQL recommended) -> APIs -> a note that this is enough to get a job -> authentication, caching, web servers, web security (OWASP risks, hashing, HTTPS, CORS, CSP) -> **AI in Development** (how LLMs work, AI-assisted coding with Claude Code as the recommended tool and Cursor, Copilot, Antigravity as alternatives, prompting techniques, agents, MCP, skills) -> testing, CI/CD -> advanced topics.
- Front-end roadmap (updated 15 July 2026) has the same AI block between "Learn a Framework" and "Advanced Frontend"; recommended picks include npm, Git, GitHub, React, Tailwind, Vite, ESLint, Prettier, Vitest, Playwright.
- Best at: a checklist of the territory and its vocabulary. Weak: no pedagogy, no rationale for the order, a DevOps section heavy on AWS, Ansible and Terraform.

**Launch School.** [source: https://launchschool.com/courses ; https://public.launchschool.com/pedagogy ; https://launchschool.com/]
- Positions itself as the slow path: mastery-based rather than time-based, with an assessment (written and 1-on-1 interview) guarding every step.
- Core, Python track: PY101 basics -> PY109 assessment -> PY110 -> PY119 -> PY120 OOP -> PY129 -> PY130 -> PY139 -> LS170 Networking Foundations -> LS171 -> PY175 Networked Applications -> LS180 Database Foundations -> LS181 -> PY185 Database Applications -> PY189; then front end: LS202 HTML and CSS -> JS210 -> LS215 Computational Thinking and Problem Solving -> JS225 -> JS230 DOM -> JS235 Async and APIs -> JS239. Git, GitHub and the command line are in the free preparatory courses.
- Core takes 8-16+ months, roughly 1,200-1,800+ hours; then a paid Capstone of 4-7+ months. $199/month.
- Best at: gating progress on demonstrated mastery; back end first, with a whole course on HTTP before any framework. Weak: slow, paid, English only.

**boot.dev.** [source: https://www.boot.dev/ ; https://www.boot.dev/tracks/backend-python-golang]
- Path order: Learn Python -> Learn Linux -> Build a BookBot -> Learn Git -> OOP -> Build Asteroids -> Functional Programming -> Build an AI Agent -> Data Structures and Algorithms -> Static Site Generator -> Memory Management (C) -> personal project -> Go -> HTTP Clients -> SQL -> HTTP Servers -> File Servers and CDNs -> Docker -> Web Security -> Pub/Sub -> **Learn AI Coding** (23rd of 25) -> Capstone -> job search. 17 courses + 8 projects; most students need about 12 months.
- Its AI tutor is built to question the learner Socratically instead of handing out answers; the site tells learners to spend most of their time writing code rather than watching videos or generating code with AI.
- Best at: Python first with tools right after, testing and debugging inside the first course, AI-agent skills taught last. Weak: no front end, paid.

**100Devs / Scrimba / web.dev.** 100Devs: a free 30-week programme that demands 20+ hours a week, teaching HTML, CSS, JavaScript, React, Node, Express and MongoDB live on Twitch, and insisting that the learner's network matters more than code for the first job; the page footer is dated 2024, so the 2026 cohort status is unknown [source: https://100devs.org/about]. Scrimba's own article: Fullstack Developer Path 108.4 hours and 20 modules; its roadmap runs front end (months 1-3) -> back end (4-5) -> integration with Next.js, an ORM, deployment and testing (6-7) -> CI/CD and AI integration (8-10), and it claims job-readiness after 8-12 months full-time or 12-18 months part-time (vendor claim) [source: https://scrimba.com/articles/how-to-become-a-full-stack-developer-in-2026-complete-roadmap/]. web.dev: 12 short expert-written courses; its Chinese pages carry `lang="zh-CN-x-mtfrom-en"`, i.e. machine translation, and only sub-pages such as `/learn/html/welcome?hl=zh-cn` are served in Chinese [local].

### 2.3 University prior art worth copying (found while checking FSO's prerequisites)

- **Python Programming MOOC 2026** (Helsinki): Introduction to Programming (parts 1-7, 5 ECTS) + Advanced Course (parts 8-14, 5 ECTS); exercises 50% + exam 50%; at least 25% of the exercise points in every part to sit the exam; a learner suspected of cheating is asked to explain their solutions in a short remote interview. The 2026 instance closes at the end of 2026; a 2027 address is likely (my inference). [source: https://programming-26.mooc.fi/ ; /grading-and-exams]
- **Ohjelmistotekniikka** (software development methods, Helsinki): the closest existing analogue of planned Stage 3. Seven weeks at a recommended 10-15 h/week, Python 3.14+, no exam: week 1 command line and Git exercises; week 2 requirements document and unittest; week 3 code skeleton with class and sequence diagrams; week 4 basic functionality, tests, Pylint; week 5 first release and higher coverage; week 6 second release, docstrings, architecture document, review of a peer's code; week 7 final submission. [source: https://ohjelmistotekniikka-hy.github.io/]
- **Tietokannat ja web-ohjelmointi** (databases and web programming, Helsinki): Python + Flask + SQLite, SQL written directly and all HTML written by hand; parts: introduction, database, login, example app, permissions and inputs, more features, large data, **security**, usability, appearance; graded by a project with peer reviews; names Full Stack Open as the follow-up. [source: https://hy-tikawe.github.io/materiaali/]
- **MIT Missing Semester 2026**: course overview + shell; command-line environment; development environment and tools; debugging and profiling; version control and Git; packaging and shipping code; **agentic coding**; beyond the code; code quality. AI tools are folded into every lecture. A Chinese translation exists, with the 2026 edition partly translated. [source: https://missing.csail.mit.edu/ ; local check of https://missing-semester-cn.github.io/]

### 2.4 Chinese resources (all load today)

| Resource | What it is | Currency check | Use it for |
|---|---|---|---|
| 现代 JavaScript 教程 https://zh.javascript.info/ | Full translation: language, browser (DOM/events), extras | Last modified 18 November 2026 [source] | Stage 4 main JavaScript text |
| 廖雪峰 Python 教程 https://liaoxuefeng.com/books/python/introduction/index.html | Free, from zero, targets current Python 3 | Contents include unittest, venv (as a module), SQLite/SQLAlchemy, WSGI, asyncio; no pip/uv chapter, no type hints [source] | Stage 2 second explanation; not for tooling |
| 廖雪峰 Git 教程 https://liaoxuefeng.com/books/git/introduction/index.html | Version history, remotes, branches, tags, GitHub, Gitee | Uses `master`; covers `git switch`; no pull-request chapter in the outline [local] | Stage 1 analogies; warn about master/main |
| 廖雪峰 SQL 教程 https://liaoxuefeng.com/books/sql/introduction/index.html | SQL you can run in the browser | Loads [local] | Stage 5 SQL drills |
| 阮一峰 ES6 入门 https://es6.ruanyifeng.com/ | Reference-style book, CC BY-NC | Continuously revised; no version cut-off stated [source] | Stage 4/6 reference, not a first read |
| 网道 https://wangdoc.com/ | HTML, JavaScript, ES6, TypeScript, Web API, C, Bash, SSH tutorials, CC licence | Loads [local] | Bash (Stage 1), TypeScript (Stage 6) |
| MDN 中文 https://developer.mozilla.org/zh-CN/docs/Learn_web_development | Community translation of the structured course | Updated 27 January 2026 [source] | Stage 4 spine |
| Official Chinese docs | Python tutorial (zh-cn docs show 3.15.2), GitHub Docs, React, Vite, FastAPI, TypeScript, Pro Git | All HTTP 200 today [local] | Reference at every stage |

---

## 3. What the best curricula agree on, and where they split

Agreement (treat as design constraints):
1. Projects are the curriculum; reading is support. Every strong programme gates progress on built artefacts (Odin 35 projects; freeCodeCamp 5 per certification; CS50 10 problem sets + final; FSO one app grown over parts; Helsinki weekly project milestones).
2. Fundamentals before frameworks: HTML/CSS and DOM-level JavaScript before React (Odin, freeCodeCamp, MDN; roadmap.sh places a milestone for building framework-free JavaScript applications before any framework); HTTP before server frameworks (Launch School LS170; FSO Part 0).
3. Git from the start in hands-on programmes, used as the submission channel (Odin, FSO, Helsinki, CS50W).
4. Relational SQL is the default first database (Odin, freeCodeCamp, Launch School, roadmap.sh: PostgreSQL; CS50, Helsinki: SQLite). FSO core and 100Devs (MongoDB) are the exceptions.
5. Teach how to learn: asking good questions, reading documentation, researching independently (Odin lessons 3-4; FSO's developer's oath; MDN "Research and learning"). Stack Overflow 2026: technical documentation is the top way developers learned in the past year (58.9%), ahead of AI tools (52.6%), videos (41.1%), online courses (29.3%) and bootcamps (6.3%).
6. Restrict generative AI while fundamentals form (Odin, FSO, CS50, boot.dev), then teach AI tooling explicitly near the end (boot.dev's AI coding course, Missing Semester's agentic-coding lecture, roadmap.sh's AI block after the first framework).
7. End with a capstone that the learner specifies.

Disagreement (choose deliberately):
- First language: JavaScript (Odin, freeCodeCamp, FSO, 100Devs, Scrimba, MDN), Python (boot.dev, Helsinki, Launch School option), C (CS50).
- Front end first (most web curricula) versus back end first (Launch School, boot.dev, Helsinki, CS50).
- Testing early (boot.dev, CS50P, Helsinki) versus late (Odin, FSO, freeCodeCamp, roadmap.sh).
- Real local toolchain (Odin, FSO, Launch School, Helsinki) versus in-browser (freeCodeCamp, Scrimba, CS50 codespace).
- Assessment: none (Odin, MDN), autograder (CS50, freeCodeCamp, boot.dev, Helsinki), human-gated mastery (Launch School).

Design patterns worth borrowing for the workspace:
- Separate correctness checks from style checks and score both (CS50: check50 and style50, weighted 3:1).
- A minimum score in every part before the gate opens (Helsinki: 25% per part), so no part is skipped.
- An explain-and-modify oral check at each gate, run by the AI tutor (Helsinki's explanation interview; Launch School's live assessments).
- One or two long-lived projects carried across stages (FSO), ideally starting from the learner's existing project (if any).
- A mindset and pitfalls lesson in Stage 0, and a how-to-ask-for-help lesson before the first hard exercise (Odin).
- A tutor that asks questions instead of giving answers (boot.dev's tutor, CS50's duck).

---

## 4. Sequencing evidence

**Python-first versus JavaScript-first.** There is no controlled study of adults learning full-stack that compares the two. Related evidence is mixed: a controlled Python-versus-C CS1 experiment (Wainer and Xavier 2018, 391 students) favoured Python on every measure except dropout, with the failure-rate difference not significant; two later studies found Python learners struggle about as much as C++ or Java learners on small exercises (Alzahrani et al. 2018; Gordon et al. 2022) [source: search-result summaries only; papers not read]. Learner behaviour: 71.8% of people learning to code use Python, 66.6% HTML/CSS, 62.8% JavaScript (Stack Overflow 2025) [source: https://survey.stackoverflow.co/2025/technology]. Conclusion: Python-first is defensible, not proven superior; method (small steps, projects, feedback) matters more than language. For this course the deciding facts are practical: the course tooling is Python, FastAPI is the planned back end, and uv + ruff + pytest is one coherent toolchain versus a fragmented JavaScript one (State of JS 2025: respondents use 4.4 testing tools on average; the top pain points are code architecture, state management and dependency management).
The cost is a second language later. Using FSO's yardstick (100-200 h for fluency in a first language), budget 60-100 h for JavaScript after Python (my estimate).

**Git.** Teach on the first days of hands-on work, limited to init/status/add/commit/log/diff/push on `main`. Teach branches, pull requests, conflict resolution and history rewriting once the learner has code worth protecting (Stage 3). Precedent: Odin's Git Basics (lessons 11-12 of 46) versus its late Intermediate Git; Helsinki methods course week 1; CS50W week 1.

**Testing.** Introduce `assert` and one pytest test while functions are being taught (Stage 2), as boot.dev and CS50P do; make tests the definition of done from Stage 3. The workspace's auto-check scripts should themselves be pytest files the learner can read.

**TypeScript.** After plain JavaScript and the DOM, before React. Python type hints in Stage 3 make this an easy transfer. Supporting data: Octoverse 2025 argues that typed contracts catch LLM errors before production and cites a study in which 94% of LLM-generated compilation errors were type-check failures [source: https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/].

**Frameworks.** Build the thing once without the framework, then adopt it: one raw HTTP exchange and a hand-written HTML form before FastAPI templates; a vanilla-DOM to-do list before React.

**Databases.** SQL before or alongside the first server framework (CS50: SQL in week 7, Flask in week 9; boot.dev: SQL before HTTP servers; Launch School: database foundations before database applications). Start with the already-installed sqlite3 3.54 [local]; move to PostgreSQL when deployment or concurrent access requires it.

**Deployment.** Static deploy in the first weeks, back-end deploy with the first server app, operations depth later (Odin, MDN, FSO precedent in section 2).

**Front end or back end first.** Both work; the evidence is precedent, not experiment. For a Python-first path the lowest-load order is CLI -> SQL -> HTTP API -> server-rendered HTML -> browser JavaScript -> TypeScript + React, which is the plan's 4 -> 5 -> 6 with a small swap (section 7, item 6).

---

## 5. Realistic time, dropout, and what keeps learners going

Hours to a first working full-stack app (local): CS50x reaches a login + database + templates app in week 9, roughly 120-220 h including lectures (my arithmetic from 10-20 h per set). FSO reaches a deployed React + Express app in Part 3, about 60-80 h on top of prerequisites of 100-200 h of programming plus basic web, SQL and Git. Odin reaches a deployed Express + PostgreSQL app only in its sixth course.

Hours to junior-employable: 1,200-1,800+ h is the range claimed by programmes with real assessment (Launch School Core; freeCodeCamp nominal). Bootcamps compress to roughly 14 weeks full-time [secondary sources citing Course Report; not verified]. At 10-15 h/week, 1,450 h is 1.9-2.8 years. JetBrains' learner survey: 38% of CS learners study 3-8 h/week and 58% study 3-16 h/week, so most adults will be at the slow end.

Dropout evidence:
- 64% of learners have quit a course; reasons: not engaging 51%, workload/time 45%, too few practical exercises 30%, too simple 26%, not relevant 25%. Frustrations: abstract concepts 51%, poor documentation 40%, getting stuck 39%, vastness of the field 38%, imposter syndrome 35%. [source: https://lp.jetbrains.com/cs-learning-curve-report-2024/]
- MOOC completion rates did not improve over six years, and most MOOC learners never return after their first year (Reich and Ruiperez-Valiente, Science 2019) [source: https://tsl.mit.edu/research/the-mooc-pivot/]; the specific figures usually quoted (about 3% completion; about half never open the courseware) are [memory].
- University CS1 fails roughly 28-33% of students worldwide (Bennedsen and Caspersen 2007 and 2019; Watson and Li 2014) [source: search-result summaries].

What the strong programmes do about it: short daily sessions instead of weekly marathons, Pomodoro, no self-imposed deadlines, comparison only with one's past self, and a named list of pitfalls (procrastination, no breaks, digital and physical distractions, rabbit holes, comparison, copy-style note-taking) [source: Odin "Motivation and Mindset"]; a published project every 1-2 weeks (Odin); community accountability (100Devs); streaks and visible progress (boot.dev); gates that stop learners building on sand (Launch School).

---

## 6. What the job requires in 2026, and what AI changed

### 6.1 What developers do each week (Stack Overflow 2026, n=24,714) [local]
Writing/editing/generating code 89.9%; debugging 83.2%; reviewing code or pull requests 66.7%; technical design decisions 63.4%; answering questions from teammates or users 59.7%; planning, scoping, estimating 57.5%; documentation 56.3%; deploying or releasing 51.8%; writing or maintaining tests 51.1%; changing production systems 49.9%; investigating incidents 46.5%; monitoring 44.3%. Full-stack developer is the most common title (27.3%; back end 13.5%, front end 3.6%). Unclear requirements (16.6%) and inefficient processes (14.6%) top the list of what makes the job harder. This is the empirical case for the plan's emphasis on engineering norms.

### 6.2 Technology usage (Stack Overflow 2026 unless stated) [local]
- Languages: JavaScript 62.0, SQL 58.4, HTML/CSS 58.2, Python 58.0, Bash/Shell 51.3, TypeScript 43.8, Java 27.6, C# 27.1.
- Databases: PostgreSQL 57.9, SQLite 42.1, MySQL 35.1, Redis 28.3, MongoDB 19.0.
- Web: Node.js 46.4, React 41.5, Next.js 20.6, FastAPI 18.5, Vue 17.2, Angular 16.0, Express 15.6, Flask 12.5, Django 11.3.
- Tooling: Docker 59.1, npm 54.6, pip 42.1, AWS 41.8, Vite 28.1, Homebrew 27.3, Kubernetes 26.0, uv 23.3, Make 22.8, pnpm 19.0, Terraform 18.3, Poetry 7.4.
- Quality: ESLint 37.1, Postman 32.6, pytest 28.0, Playwright 24.9, Jest 20.8, Vitest 19.4, Cypress 8.2. Editors: VS Code 70.9, Cursor 14.9.
- Caveat: 2026 had 30,903 valid responses (fielded 23 June - 5 August 2026) versus 49,000+ in 2025, with reworded questions; treat year-on-year moves as indicative.
- JetBrains 2026 (28,945 developers, 198 countries, May-July 2026): Python most used at 65%, ahead of JavaScript for the first time; TypeScript use more than tripled since 2017; Language Promise Index led by TypeScript, Rust, Python; PostgreSQL 59% (+9 points); only 18% call their local job market favourable. [local: https://blog.jetbrains.com/research/2026/11/state-of-developer-ecosystem-2026/]
- Job-board analyses (vendor data, directional only): full-stack postings name React 54-61%, TypeScript 39-45%, CI/CD 42-49%, JavaScript 41-44%, AWS 37-40%, SQL 35-37%, Python 33.5%, Java 33-40%, Docker 28-34%, PostgreSQL 26%, Agile 32-33%; entry-level share 3.4%. [source: https://interviewstack.io/blog/fullstack-developer-skills-companies-want-2026 ; https://jobspipe.dev/job-description/full-stack-developer]

### 6.3 The labour market [source: hiringlab.indeed.com posts of 2026-07-23, 2026-11-12, 2026-11-18; https://digitaleconomy.stanford.edu/news/canariesaug26/]
- US software-development postings: +23.8% year on year to 23 October 2026, still 19.2% below February 2020. Entry-level share 4.5%, senior 69.3% (Q1 2026; all sectors: 46% entry, 14% senior). Senior roles made up 71% of the increase in software postings, and 37% of the increase had AI in the job title. Postings containing AI terms doubled from 3.6% to 7.2% between September 2025 and September 2026.
- Stanford (ADP payroll data to June 2026): no economy-wide displacement, but 22-25-year-olds in the most AI-exposed occupations are about 19% below counterfactual (15% a year earlier); experienced workers show no gap; the adjustment is through reduced hiring; declines sit where knowledge is codified, growth where it is tacit. The authors stress these are descriptive patterns, not causal estimates.

### 6.4 How AI coding agents changed the work (evidence, not hype)
- Adoption: 90% weekly and 68% daily among professional developers; Claude Code 39% at work (18% in January 2026), GitHub Copilot 21% (29% a year earlier), Codex 16%, Cursor 12%. More than half of developers now write under 20% of their code by hand and one in five writes none without AI. Profiles: agentic coders about 31%, AI-assisted about 47%, manual about 23%. [local: JetBrains research blog, August 2026]
- GitHub: agent-started pull requests rose from 17% (March) to more than 40% (September 2026); new repositories with an agent configuration file logged 8x the commits of those without; AI-assisted code review usage grew more than 90%. [source: https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/]
- Trust is conditional: 48.0% trust AI output only when it is easy to verify; 6.6% trust it for important decisions; 16.0% say it handles complex tasks very well. Least delegated: deploying or operating production (19.9% use AI for it; 36.0% do not plan to). [local: Stack Overflow 2026 AI data]
- Willingness to delegate, 2025 -> 2026: application logic 18% -> 50%; tests 50% -> 75%; refactoring 38% -> 60%; code review only 43% ready; debugging 54% not ready. 79% expect employers to require proficiency with AI tools. Senior developers go beyond prompts and give agents guidelines, specifications and ways to verify; 60% of developers with 1-2 years' experience rate AI solutions above their own, versus 47% of those with 16+ years. [local: JetBrains posts of October and November 2026]
- Productivity: METR's early-2025 trial found experienced open-source developers took 19% longer with AI; its February 2026 follow-up (57 developers, 800+ tasks) estimated an 18% speed-up for returning participants (confidence interval from 38% faster to 9% slower), but METR itself calls the data unreliable because many developers now decline to work without AI. [source: https://metr.org/blog/2026-02-24-uplift-update/]
- Learning: Anthropic RCT, 29 January 2026: AI group 50% vs 67% on a comprehension quiz (d=0.738, p=0.01), no significant time saving, largest gap on debugging. Low-scoring usage patterns: full delegation (39%), progressive reliance (35%), iterative AI debugging (24%). High-scoring: generate then ask to understand (86%), code plus explanation (68%), conceptual questions only (65%). [source: https://www.anthropic.com/research/AI-assistance-coding-skills]

Skills that gained value: reading and reviewing code you did not write; specifying work precisely (requirements, acceptance tests, agent instruction files); verification (tests, running locally, reading diffs); debugging; type systems; architecture and decomposition; production operations and security; communication. GitHub's interviews with 22 advanced AI users found delegation and verification had become their main activities [source: https://github.blog/news-insights/octoverse/the-new-identity-of-a-developer-what-changes-and-what-doesnt-in-the-ai-era/].
Skills that lost value: typing boilerplate, memorising syntax and API details, and "can produce a CRUD app" as a hiring signal. What did not lose value: fundamentals. Every source that addresses the point says so (FSO, GitHub, and the State of JS 2025 conclusion, which argues that recognising good code matters more than ever).

---

## 7. Critique of the planned stage order, with concrete changes

The order 0-10 is sound in outline. Recommended changes, strongest first:

1. **Add early ship points; do not wait for Stage 8.** (a) Stage 1: publish the personal handbook (Markdown) with GitHub Pages, which gives Markdown, Git and GitHub an immediate purpose. (b) Stage 3: tag and release a small CLI tool. (c) Opening of Stage 5: build the thin slice from 1.2, then deploy it to a free platform host. Stage 8 remains for Linux, Docker, continuous delivery and monitoring in depth.
2. **Make Stage 1 short and never code-free.** Cap it at about 40-60 h and use the learner's existing project (if any; for example one an AI helped write) as the practice object: open it in the editor, run it from the terminal, change one line, commit, push. Teach only just-enough Git here. Reason: unengaging content and too little practice are the top reasons learners quit.
3. **Pull three tools forward into Stage 2:** `uv run`, one `ruff` command, and one pytest test per exercise. They are how the learner runs and checks code anyway, and boot.dev and CS50P show beginners cope. Stage 3 then covers project-level practice: structure, typing, refactoring, configuration and logging, documentation, versioning and releases, and issue -> branch -> pull request -> review.
4. **Put CI in Stage 3, not Stage 8.** A small GitHub Actions workflow running ruff and pytest on every pull request makes the review flow real. Continuous delivery stays in Stage 8.
5. **Spread security instead of concentrating it in Stage 7.** Stages 1-3: never commit secrets, `.gitignore`, the e-mail-in-pyproject trap. Stage 5: parameterised SQL, password hashing, input validation, HTTPS basics (CS50 and Helsinki teach these inside the first web app). Stage 7: OWASP Top 10:2025, sessions versus tokens, CSRF/XSS/CORS, dependency risk.
6. **Reorder inside Stages 4-5:** how the web works + HTML + a little CSS -> SQL with SQLite -> FastAPI JSON API and server-rendered pages -> deploy -> then browser JavaScript and the DOM calling that API. This yields a full-stack result before the JavaScript learning curve, mirrors CS50 and Helsinki, and makes JavaScript immediately purposeful. Stage 6 starts with TypeScript, then React.
7. **Dissolve most of Stage 9 into earlier stages and repurpose it.** Issues, pull requests, reviews and changelogs run from Stage 3 onward. Stage 9 becomes "working with other people and with agents": a real contribution to an open-source project, reviewing someone else's code, estimating and planning a milestone, and delegating a specified task to an agent and verifying the result.
8. **Add an explicit AI-use ladder with AI-off gates.** Stages 1-2: tutor only (explain, hint, quiz; never writes exercise code), which is the high-scoring conceptual-inquiry pattern. Stage 3: reviewer of learner-written code. Stages 5-7: pair for boilerplate, only after the learner has hand-built the same thing once. Stages 8-10: delegated agent working from the learner's specification and tests. Every stage gate includes tasks done without AI plus the oral explain-and-modify check.
9. **Add three continuous threads the plan does not name:** debugging and reading error messages (83.2% of developers do it weekly, and it is the skill AI reliance erodes most); reading English documentation (the top way developers learn; freeCodeCamp's English for Developers is a ready supplement); computer-science basics in small doses (data structures and complexity in Stage 2, HTTP and networking in Stage 4, data modelling and concurrency in Stage 5).
10. **Add accessibility and basic design to Stages 4 and 6** (MDN makes both Core modules).
11. **Define exit ramps** so that a 2-3 year plan pays off early: after Stage 3, "can build, test, version and review a Python tool, and supervise an agent doing the same"; after Stage 5, "can ship a database-backed web service"; after Stage 7, "junior full-stack"; after Stage 10, "can own a small product end to end".
12. **State the market caveat in Stage 0:** entry-level postings are scarce, and the dominant stack differs in mainland China. The goal is professional capability and a portfolio of shipped, reviewed work, not a certificate.

Sensible defaults confirmed by the data: SQLite then PostgreSQL, FastAPI, React + TypeScript + Vite, pytest, Playwright, Docker, GitHub Actions, VS Code, uv.

---

## 8. Hours estimate per stage (my synthesis from the sources above; ranges, not promises)

| Stage | Hours | Basis |
|---|---|---|
| 0 Orientation | 5-10 | Odin intro lessons; one sitting plus a setup check |
| 1 Foundations (terminal, editor, Markdown, just-enough Git/GitHub, asking for help) | 40-60 | Missing Semester's 9 lectures with exercises; Odin prerequisites + Git Basics; Helsinki methods week 1 |
| 2 Python fundamentals | 180-250 | Helsinki intro course (5 ECTS) plus part of the advanced course; FSO's 100-200 h fluency bar; CS50P's 10 weeks |
| 3 Professional practice | 100-150 | Helsinki methods course, 7 weeks x 10-15 h = 70-105 h, plus typing, uv, releases, PR flow, CI |
| 4 Web basics (HTTP, HTML, CSS, JavaScript + DOM) | 120-200 | Odin Foundations learner reports of 100-440 h from zero; faster with prior Python |
| 5 Back end and databases | 150-220 | Helsinki Flask + SQL course; CS50 SQL and Flask weeks; FSO Parts 3, 4, 13 |
| 6 TypeScript + React | 150-220 | FSO Parts 1, 2, 5, 9 at 15-20 h each plus practice; Odin React projects took one learner 10-30 days each |
| 7 Integration + security | 120-180 | FSO Parts 4-5 (auth, end-to-end tests); Odin authentication, API and full-stack projects |
| 8 Delivery + operations | 100-150 | FSO Parts 11-12; Helsinki DevOps with Docker; Linux basics |
| 9 Collaboration with people and agents | 40-80 | Mostly embedded earlier; one open-source contribution plus planning practice |
| 10 Architecture + capstone | 150-250 | FSO project, 5-10 credits x 17.5 h = 88-175 h, plus design reading |
| **Total** | **about 1,150-1,770** | Consistent with Launch School's 1,200-1,800+ and freeCodeCamp's about 1,800 |

First deployed thin full-stack app if section 7 is adopted: about 400-500 h (end of Stage 3 plus the first third of Stages 4-5). Without the changes: about 700-900 h for the app and 1,100+ h before deployment is taught.

---

## 9. Free further reading per stage (every URL returned HTTP 200 today via curl unless noted) [local]

Stage 0: https://roadmap.sh/full-stack (map of the territory, English) · https://csdiy.wiki/ (CS自学指南) · https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md (提问的智慧) · https://www.theodinproject.com/lessons/foundations-motivation-and-mindset · https://www.anthropic.com/research/AI-assistance-coding-skills · https://www.norvig.com/21-days.html
Stage 1: https://missing-semester-cn.github.io/ (计算机教育中缺失的一课) · https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Getting_started/Environment_setup/Command_line · https://wangdoc.com/bash/ · https://liaoxuefeng.com/books/git/introduction/index.html · https://git-scm.com/book/zh/v2 · https://learngitbranching.js.org/?locale=zh_CN · https://docs.github.com/zh/get-started · https://docs.github.com/zh/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax · https://learn.microsoft.com/zh-cn/training/modules/intro-to-git/
Stage 2: https://docs.python.org/zh-cn/3/tutorial/index.html · https://liaoxuefeng.com/books/python/introduction/index.html · https://programming-26.mooc.fi/ (English, autograded) · https://cs50.harvard.edu/python/ · https://pythontutor.com/ · https://exercism.org/tracks/python (serves a zh-CN interface when the browser prefers Chinese)
Stage 3: https://docs.astral.sh/uv/ · https://uv.doczh.com/ (unofficial Chinese uv docs; check against the official ones) · https://docs.astral.sh/ruff/ · https://docs.pytest.org/en/stable/ · https://fastapi.tiangolo.com/zh/python-types/ (Python 类型提示简介) · https://typing.python.org/en/latest/ · https://packaging.python.org/en/latest/ · https://www.conventionalcommits.org/zh-hans/v1.0.0/ · https://semver.org/lang/zh-CN/ · https://keepachangelog.com/zh-CN/1.1.0/ · https://refactoringguru.cn/refactoring · https://google.github.io/eng-practices/ with Chinese translation https://github.com/xindoo/eng-practices-cn · https://docs.github.com/zh/get-started/using-github/github-flow · https://docs.github.com/zh/pull-requests · https://12factor.net/zh_cn/ · https://diataxis.fr/ · https://cbea.ms/git-commit/
Stage 4: https://developer.mozilla.org/zh-CN/docs/Learn_web_development · https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Guides/Overview · https://zh.javascript.info/ · https://wangdoc.com/html/ · https://wangdoc.com/javascript/ · https://es6.ruanyifeng.com/ · https://fullstackopen.com/zh/part0 · https://flexboxfroggy.com/#zh-cn · https://cssgridgarden.com/#zh-cn · https://web.dev/learn/html/welcome?hl=zh-cn (machine-translated)
Stage 5: https://liaoxuefeng.com/books/sql/introduction/index.html · https://sqlbolt.com/ · https://sqlzoo.net/wiki/SQL_Tutorial/zh · https://cs50.harvard.edu/sql/ · https://fastapi.tiangolo.com/zh/ · https://sqlmodel.tiangolo.com/ · https://www.postgresql.org/docs/current/tutorial.html (PostgreSQL 18) · http://www.postgres.cn/docs/current/index.html (PostgreSQL 18.3 手册; plain HTTP only, HTTPS failed) · https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Extensions/Server-side · https://www.ruanyifeng.com/blog/2018/10/restful-api-best-practices.html
Stage 6: https://wangdoc.com/typescript/ · https://www.typescriptlang.org/zh/docs/ · https://zh-hans.react.dev/learn · https://cn.vite.dev/guide/ · https://fullstackopen.com/en/ (use the English edition for Parts 5-7; the Chinese one is outdated there) · https://2025.stateofjs.com/zh-Hans/ · https://tailwindcss.com/docs
Stage 7: https://top10.owasp.org/ (OWASP Top 10:2025; https://owasp.org/Top10/ redirects there; the zh_CN paths I guessed returned 404) · https://cheatsheetseries.owasp.org/ · https://developer.mozilla.org/zh-CN/docs/Web/Security · https://fastapi.tiangolo.com/zh/tutorial/security/ · https://playwright.dev/docs/intro · https://web.dev/learn/testing
Stage 8: https://docs.docker.com/get-started/ (redirects to /learn/) · https://yeasy.gitbook.io/docker_practice/ (Docker 从入门到实践) · https://courses.mooc.fi/org/uh-cs/courses/devops-with-docker-spring-2026 (devopswithdocker.com redirects here) · https://docs.github.com/zh/actions · https://fullstackopen.com/zh/part11 · https://fullstackopen.com/zh/part12 · https://linux.vbird.org/ (鳥哥, 繁體) · https://billie66.github.io/TLCL/ · https://sre.google/sre-book/table-of-contents/ · https://roadmap.sh/devops
Stage 9: https://opensource.guide/zh-hans/ · https://docs.github.com/zh/issues · https://www.atlassian.com/zh/agile · https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Chinese-Simplified.pdf · https://missing.csail.mit.edu/ (lectures on agentic coding, beyond the code, code quality)
Stage 10: https://icyfenix.cn/ (凤凰架构) · https://ddia.vonng.com/ (设计数据密集型应用, 2nd-edition translation) · https://github.com/donnemartin/system-design-primer/blob/master/README-zh-Hans.md · https://c4model.com/ · https://adr.github.io/ · https://martinfowler.com/architecture/

---

## 10. What changed recently compared with older tutorials

- freeCodeCamp's familiar 300-hour certifications are legacy/archived; the catalogue is now six v9 checkpoint certifications plus a capstone exam that is not yet released. [source + local]
- Full Stack Open: no yearly editions; Redux -> Zustand, webpack -> esbuild, Cypress removed, Express 5, a Next.js part added; the Chinese edition has not followed. [source + local]
- MIT Missing Semester was rewritten for 2026; the 2020 lecture list (Vim, data wrangling, metaprogramming) is superseded. [source]
- roadmap.sh's front-end and back-end roadmaps gained an "AI in Development" block in 2026. [local]
- TypeScript overtook Python and JavaScript on GitHub in August 2025 and stayed #1 in 2026; Vite's downloads passed webpack's (State of JS 2025 conclusion). Tutorials built on create-react-app or hand-configured webpack are obsolete [memory for create-react-app's status].
- uv went from 9.5% (2025) to 23.3% (2026) usage; Poetry is at 7.4%; `uv init` now scaffolds a `src/` package with the `uv_build` backend. [source + local]
- FastAPI (18.5%) is now above Express (15.6%), Flask and Django in the Stack Overflow survey. [local]
- Starlette is at 1.x and warns about the httpx-based test client. [local]
- PostgreSQL's current documentation is version 18; Python's zh-cn documentation shows 3.15.2 while this machine runs 3.14.9. [local]
- OWASP Top 10 moved to top10.owasp.org with a 2025 edition. [local]
- Some large employers are starting to allow AI in coding interviews [secondary reports only; unverified].

---

## 11. Pitfalls a beginner will hit

1. Believing three-months-to-a-job marketing; the honest figure is 1,100-1,800 hours.
2. Tutorial hell: watching or reading without building.
3. Letting the agent write the exercise. It feels productive and removes exactly the debugging practice that builds skill (Anthropic RCT). Many beginners start from that habit.
4. Following a stale Chinese translation or blog without checking the date of the English original (FSO 中文; `master` in 廖雪峰's Git tutorial; pip/venv-only Python tutorials; webpack-era React setups).
5. Tool overload in week 1 with nothing built; quitting before the first visible result.
6. Skipping Git until later, or the opposite: trying to learn branching, rebasing and conflicts before having any code.
7. Avoiding English documentation, then being unable to read error messages or official docs.
8. Rabbit holes and perfectionism; comparing progress with others (Odin's named pitfalls).
9. Copy-style note-taking: a handbook of pasted tutorials. Odin's advice is that notes should be prompts for further research, written in one's own words.
10. Weekly marathon sessions instead of short daily ones.
11. Looking at solutions before finishing (Odin's projects and CS50's honesty policy both forbid it).
12. Committing secrets or personal data (the `authors` e-mail that `uv init` writes; API keys).
13. Treating passing auto-checks as understanding; without an explain-it-back step, checks can be satisfied with AI.
14. Starting React before understanding HTTP, the DOM and plain JavaScript; starting FastAPI before understanding a single HTTP request.

---

## 12. Plain-Chinese analogies that fit the evidence

- 全栈 = 一家餐厅：前厅（浏览器里的界面）、后厨（后端程序）、仓库（数据库）、传菜口和点菜单（API / HTTP 请求与响应）、开店营业（部署）、巡店和报警（监控）。全栈工程师是前厅后厨都懂、还能把店开起来的人。
- Git = 游戏存档 / 时光机：commit 是存档点，branch 是平行草稿，pull request 是"请同事审稿后再合稿"。
- 测试 = 出餐前试菜；CI = 自动质检流水线，每次交稿都自动试一遍。
- 类型标注 / TypeScript = 给每个抽屉贴标签，放错东西当场就被发现。
- 虚拟环境 / uv = 每道菜自己的调料盒，互不串味。
- Docker = 标准集装箱：把厨房整套设备装箱，运到哪里都能原样开工。
- AI 代理 = 手脚很快的施工队；你是监理兼总工，要会看图纸（读代码）、会验收（测试、本地运行、看 diff）、敢要求返工。只会下单不会验收，房子出了问题责任还是你的。
- 让 AI 替你做练习 = 学车一直坐副驾驶；看再多也拿不到驾照。
- 阶段关卡 = 驾考科目一到科目四：过了才上路。
- Tutorial hell = 天天看做菜视频但从不下厨。
- 1,100-1,800 小时 = 把一门外语学到能工作的量级；每天一小时、坚持两三年，比偶尔通宵有效。

---

## 13. Not verified / caveats

- The Odin Project total hours: no official figure; only two individual learner reports read.
- Scrimba path details come from Scrimba's own article; the course page is JavaScript-rendered and was not read; its price is from a secondary source.
- 100Devs: whether a cohort ran in 2026 is unknown.
- freeCodeCamp: whether the Front-End Libraries and Back-End certification exams are open today (the curricula are served; the `public: false` flags in the JSON may refer to the mobile app).
- Python-versus-other-language studies and CS1 failure rates: read only as search-result summaries.
- MOOC completion percentages, bootcamp average length (about 14 weeks), CS50P weekly hours, the ECTS-to-hours conversion (about 27 h) and the credit value of Helsinki's methods course: memory or secondary.
- JetBrains State of Developer Ecosystem 2026: the key-findings blog post was read; the full report site was not.
- State of React 2025 and the State of JS chart values are interactive and were not extracted; only text commentary and the usage page.
- DORA: the "AI as amplifier" headline was read on dora.dev; the capabilities model and any 2026 report were not.
- Interview-format changes (large employers allowing AI; vendor survey figures): secondary reports only.
- Vue's dominance in mainland China: memory. Java's 60% share: read today.
- Launch School, boot.dev and 100Devs internals behind the paywall or community were not inspected.
- Stage-hour estimates and the 400-500 h figure for a first deployed app are my synthesis, not measurements.

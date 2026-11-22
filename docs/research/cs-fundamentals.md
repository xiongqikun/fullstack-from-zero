# Brief: CS / how-things-work fundamentals for a zero-to-full-stack learner (topic key: cs-fundamentals)

Research date: 2026-11-19. Audience: the agents that will design and write the lessons. Not a message to the learner.
Tags: **[local]** = I ran it on this machine today; **[source: URL]** = read in a primary source today; **[memory]** = not verified today.
Reusable demo files (all ran successfully here) are in `<scratch>/lab/` where `<scratch>` is this brief's directory:
`bigo_demo.py`, `index_demo.sql`, `tx_demo.py`, `conc_demo.py`, `conc_demo2.py`, `raw_http.py`, `encoding_demo.py`, `env_demo.sh`, `whoami.py`.

---

## 0. TL;DR for course designers

1. **Do not make "CS fundamentals" a stage. Make it a thread ("原理线") with a ledger.** Every concept below has a first stage where the learner *needs* it; teach a 10–20 minute "原理小课" there (one picture, one experiment the learner runs, one predict-then-verify question, one glossary entry), then revisit it at the later stages listed in the matrix (section 2). No established curriculum I read front-loads all of this for beginners; CS50x spends weeks 1–5 on C/memory/data structures before Python/SQL/web, which is the wrong order for this learner's goal. [source: https://cs50.harvard.edu/x/]
2. **Every hard concept can be shown with a 3–15 line experiment on this exact machine using only tools already installed** (python3 3.14.9, sqlite3 3.54, node 26, git 2.54, curl, dig, jq). Section 4 gives the commands and real outputs. Prefer "predict, run, explain" over reading.
3. **The AI tutor's Bash sandbox cannot observe processes, ports or DNS** (`ps`, `top`, `sysctl`, `dig`, port binding and `multiprocessing` pools all fail with "Operation not permitted" in this session) [local]. Labs on processes / ports / DNS must be typed by the learner in their own terminal, and auto-checks for those labs should grade saved output files, not re-run the commands inside the tutor.
4. **Teach OS-level concepts in Stage 1, not Stage 8.** Path, program-vs-process, exit code, environment variable, PATH, stdin/stdout are needed the first day in a terminal. Stage 8 "Linux" should cover what is *different* on a server, not introduce processes for the first time.
5. **Start Stage 4 with a "一次请求的旅程" lab** (URL → DNS → TCP → TLS → HTTP → render) using browser DevTools Network + `curl -v`, before any HTML. Full Stack Open opens the same way: its Part 0 teaches HTTP through the DevTools Network tab before any framework (it does not cover DNS/TCP/TLS). [source: https://fullstackopen.com/en/part0/fundamentals_of_web_apps]
6. **Teach relational fundamentals (tables, keys, SQL, transactions, indexes) on SQLite first**, then move to PostgreSQL. SQLite needs zero setup here and shows scan-vs-index and rollback in seconds [local]. PostgreSQL current stable is 18 (18.7); 19 is at RC2 today — re-check when Stage 5 is generated. [source: https://www.postgresql.org/support/versioning/]
7. **Data structures / Big-O essentials belong in Stage 2 as Python built-ins plus timing experiments**, not as an algorithms course. Trees and graphs are met as the DOM, the directory tree, the Git commit graph, the dependency graph and the B-tree index — awareness only.
8. **Best free Chinese-friendly resources exist but none fits end to end.** MDN zh-CN (maintained, right level) is the backbone for web topics; 《Hello 算法》 for data structures; Crash Course CS with Chinese subtitles for the Stage 0–1 big picture; 小林coding and 阮一峰 are useful but interview-oriented / dated and need caveats (section 6).
9. **Old tutorials now mislead on many points** (section 5): HTTP/3 is on 41% of sites, TLS 1.3 has a new RFC, Chrome warns before plain HTTP by default, `asyncio.get_event_loop()` raises on Python 3.14, `docs.python.org/3/` now documents 3.15 while this machine runs 3.14, the sqlite3 shell changed its interactive output format.
10. **Analogies must ship with their failure point.** Section 7 gives a tested analogy, the misleading analogy to avoid, and the experiment that shows the real mechanism, for each of the 13 requested concepts and a few more.

---

## 1. What was verified and how

### 1.1 Local environment actually exercised [local]

| Item | Observed today |
|---|---|
| OS / arch | macOS 27.2.1 (26B131), arm64, little-endian |
| Python | `python3` and `python` → uv-managed 3.14.9 (a uv-installed interpreter first on PATH); GIL enabled (`sys._is_gil_enabled()` → True); `multiprocessing` start method `spawn`; bundled SQLite library 3.53.1; OpenSSL 3.5.9; `unicodedata` 16.0.0; `/usr/bin/python3` is 3.9.6 |
| SQLite CLI | `/usr/bin/sqlite3` 3.54.0 (Apple build) |
| Node | v26.12.0 (V8 14.6, ICU/Unicode 17.0) |
| Git | 2.54.0 (Apple Git-157); new repos: ref format `files`, object format `sha1` |
| curl | 8.7.1 (LibreSSL 3.3.6, nghttp2): features include HTTP2, **no HTTP3** |
| Present | `dig nslookup host nc lsof netstat ifconfig traceroute ping openssl whois curl ssh scp rsync top ps jq sqlite3 make xxd hexdump file man` |
| Missing | `tree`, `htop` (plus the tools the task already listed) |
| File system | case-insensitive: writing `casetest.txt` overwrote `CaseTest.txt` (one file, content of the second write) |
| Locale notes | Do not assume the learner's system language or time zone; ask first (`defaults read -g AppleLanguages`, `date +%z` in the learner's terminal show them). Lessons should name macOS UI items in English with a Chinese gloss and must not hard-code Asia/Shanghai, or any other zone, in time-zone examples or auto-checks. |
| `/etc/hosts` | Lessons should be "look, don't edit"; checks must not assume a default hosts file (a learner's may hold custom entries besides the three default lines). |

### 1.2 What this session's sandbox blocks (matters for the AI tutor and for auto-checks) [local]

| Attempt | Result here |
|---|---|
| `ps`, `top` | `operation not permitted: ps` / `top` |
| `sysctl -n hw.ncpu` etc. | `sysctl: ... Operation not permitted` (use `python3 -c "import os; print(os.cpu_count())"` instead; `vm_stat`, `df -h`, `uptime` work) |
| `dig`, `nslookup`, `host` | `bind: Operation not permitted`; Python `getaddrinfo('example.com')` fails; `ping` cannot resolve. `localhost` does resolve (127.0.0.1, ::1). |
| bind a port | `PermissionError [Errno 1] Operation not permitted` for `127.0.0.1:8000` |
| `ProcessPoolExecutor` / `multiprocessing` | `PermissionError [Errno 1]` (plain `subprocess.Popen` works, so process-parallelism can still be shown) |
| HTTPS from Bash | goes through a filtering proxy; `curl` returned `200` over HTTP/2 for pypi.org and www.iana.org, but **`https://example.com/` failed certificate verification** in both system curl (exit 60) and Python `urllib` (`CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`). Cause not determined; may be specific to the sandbox. Node's built-in `fetch` failed with `ENOTFOUND` (presumably because it ignores the proxy variables by default [memory]). |
| `curl -v` | prints proxy credentials and would print `Authorization`/`Cookie` headers. Teach "never paste `-v` output publicly without redacting". |

Assume sandboxed Bash may be normal in the learner's own tutor sessions too, not only in this research run (I did not test an interactive session).
Consequence: the learner's own terminal app is the only place where process, port, DNS and server labs behave normally. I could not test that terminal, so every command in section 4 that needs those capabilities is marked "learner terminal, not run here".

### 1.3 Web access

WebSearch and WebFetch both worked. Exceptions: `www.hello-algo.com` returned HTTP 429 ("Vercel Security Checkpoint") to both WebFetch and curl, and `www.cloudflare.com/zh-cn/learning/...` returned 403 to WebFetch — both are bot protections; I could not confirm how they load in a normal browser today. `howdns.works` and `howhttps.works` now 301-redirect to `dnsimple.com/comics/...`.

---

## 2. Stage map (where each concept is first needed, and where it returns)

Legend: `s` = see it (recognise the word, have a picture) · `U` = use it hands-on · `E` = explain it in own words and debug with it · `D` = optional depth. Stages S0–S10 as in the planned roadmap.

| # | Concept | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Hardware picture: CPU / memory / disk; bytes | s | U | E | | | | | | D | | |
| 2 | Program vs process, PID, exit code, signals (Ctrl-C) | | U | s | U | | U | | | E | | |
| 3 | What the OS does: files, permissions, users | | s | | | | | | | E | | |
| 4 | stdin / stdout / stderr, pipes, redirection | | U | | E | | | | | U | | |
| 5 | Environment variables, PATH | | U | | E | | U | | U | E | | |
| 6 | Paths, hidden files, text vs binary, extensions | | E | U | | U | | | | U | | |
| 7 | Text encodings: bytes vs str, UTF-8, line endings | | s | E | | U | U | | | | | |
| 8 | Numbers: binary/hex, int vs float, Decimal, sizes | | s | E | | U | U | | | | | |
| 9 | Time: Unix time, UTC, ISO 8601, time zones | | | s | | | E | U | | | | |
| 10 | Hash vs encoding vs encryption | | s | s | | | | | E | U | | |
| 11 | Client / server, request / response | s | s | | | E | U | U | | | | |
| 12 | IP address, localhost, ports | | | | | E | U | | | E | | |
| 13 | DNS | | | | | s | | | | E | | s |
| 14 | TCP / UDP / QUIC (reliable stream, handshake) | | | | | s | | | | E | | D |
| 15 | TLS / HTTPS / certificates | | s | | | s | | | E | U | | |
| 16 | HTTP message: method, status, headers, body; stateless | | | | | E | U | U | U | | | |
| 17 | HTTP/1.1 vs 2 vs 3 | | | | | s | | | | s | | s |
| 18 | URL anatomy, relative URLs, origin | | s | | | E | U | U | E | | | |
| 19 | Cookies, sessions, web storage | | | | | s | | U | E | | | |
| 20 | Browser pipeline: DOM, CSSOM, layout, paint; JS blocks | | | | | E | | E | | | | s |
| 21 | API as a contract; REST / JSON / OpenAPI | | | s | | s | E | U | U | | U | E |
| 22 | list / dict / set / tuple; stack / queue | | | E | U | | | U | | | | |
| 23 | Big-O intuition | | | E | s | | U | s | | | | U |
| 24 | Trees and graphs (awareness) | | s | s | s | U | s | U | | s | | |
| 25 | Recursion | | | s | | U | | U | | | | |
| 26 | Relational model, keys, SQL, NULL | | | | | | E | | | | | |
| 27 | Transactions / ACID | | | | | | E | | U | | | D |
| 28 | Indexes, query plans | | | | | | E | | | | | U |
| 29 | Concurrency: I/O-bound vs CPU-bound; event loop; async / threads / processes | | | | | E | E | U | | E | | U |
| 30 | Race conditions, locks, idempotency | | | | | | s | s | U | | | E |
| 31 | Caching (and staleness) | | | s | s | U | U | U | | E | | E |
| 32 | Small-system design (pieces, boundaries, trade-offs) | | | | | | s | | U | E | s | E |
| 33 | Dependency, lockfile, virtual environment | | | s | E | | | U | | U | | |
| 34 | Container / image / VM | | | | | | s | | | E | | |
| 35 | Deployment (dev vs prod, build → release → run) | s | | | s | | | | | E | U | E |
| 36 | Version control as snapshots + pointers; commit graph | | E | | U | | | | | | E | |

### 2.1 Per-stage "原理线" content (what to actually put in each stage)

- **S0 Orientation (about 60–90 min of concepts).** One big picture only: a computer = CPU + memory + storage running programs; the internet = computers asking other computers for things; "full stack" = browser + server + database + the delivery pipeline. Watching, not doing: Crash Course CS episodes with Chinese subtitles are the right level (section 6). No terminology test.
- **S1 Foundations.** In this order: (a) paths and files (absolute/relative, `~ . ..`, hidden files, extension is just a name, `file`, text vs binary); (b) a command is a program found via PATH (`which`, `type`, "command not found"); (c) program vs process, PID, exit code, Ctrl-C (learner terminal: `ps`, Activity Monitor); (d) stdin/stdout/stderr and pipes; (e) environment variables (`env_demo.sh`); (f) a first look at "text is bytes" (`xxd` on a file containing 中文) so that 乱码 is not magic later; (g) Git mental model = snapshots + movable pointers (branch = 41-byte file, shown in 4.14), GitHub = a server you talk to over HTTPS/SSH (first, light "client/server").
- **S2 Python fundamentals.** Memory vs disk (4.2); `int` vs `float`, `0.1 + 0.2`, `Decimal`, `//` and `%` (4.4); `str` vs `bytes`, always `encoding="utf-8"` (4.3); list / dict / set / tuple chosen by operation, with `bigo_demo.py` (4.5); stack and queue as usage patterns of list and `deque`; mutability and hashability (`TypeError: cannot use 'list' as a dict key`); recursion as a concept with the 1000-frame limit; a function signature as a tiny API. Tool: Python Tutor for references and the call stack.
- **S3 Professional practice.** Exit codes as the language of automation (`&&`, Make, pytest, CI); stderr vs stdout and logging; configuration through environment variables and why secrets stay out of Git (12-factor "配置"); dependency vs lockfile vs virtual environment (4.13); dependency graph as a first graph (`uv tree`); caches you already rely on (`__pycache__`, the uv cache); "measure before optimising" with `timeit`.
- **S4 Web basics.** Open with the request-journey lab (4.9–4.11): URL anatomy; DNS (learner terminal: `dig +short`); localhost and ports at the moment the first local server starts; HTTP request/response read in DevTools Network and in `raw_http.py`; HTTPS = HTTP inside TLS; then the browser pipeline when HTML/CSS arrive (DOM is a tree; a `<script>` blocks parsing); then the JS event loop when JavaScript arrives (Node demo in 4.8); cookies and the cache seen in DevTools. HTTP/2 and HTTP/3 only as "same messages, different transport" plus the Protocol column in DevTools.
- **S5 Backend and databases.** Why a database instead of files; relational model, primary/foreign keys, NULL; SQL; **transactions with `tx_demo.py`; indexes with `index_demo.sql`**; SQL injection in two lines (4.7); API as contract (path, method, status code, JSON schema, OpenAPI); idempotency of methods; time stored as UTC; money as integer cents or NUMERIC; `async def` vs `def` in FastAPI with `conc_demo.py`; the three-box system picture (browser, app, database).
- **S6 Modern front end.** Component tree and re-rendering in terms of the S4 pipeline; async data fetching and UI race conditions; JS number limits and big IDs in JSON (4.4); `Map`/`Set`/array costs; client-side caching and stale data.
- **S7 Integration and security.** Prerequisite recap card: origin (scheme + host + port), cookies and their attributes, sessions vs tokens, hash vs encoding vs encryption (4.15), what TLS does and does not protect, parameterised queries, trust boundaries drawn on the learner's own system diagram.
- **S8 Delivery and operations.** Linux as "the same ideas, case-sensitive and without a GUI"; process supervision and SIGTERM; `0.0.0.0` vs `127.0.0.1`; DNS records and TTL when pointing a domain; certificates issued automatically; container = isolated process from an image (and the VM that Docker Desktop hides on a Mac); 12-factor in full; CDN and build caches; connection refused vs timeout vs TLS error vs HTTP error as a diagnosis ladder.
- **S9 Collaboration.** Commit graph, merge vs rebase as graph operations; API and schema changes as contract changes between people.
- **S10 Architecture and capstone.** Small-system design: monolith first, one database, vertical scaling before horizontal, when a cache / queue / CDN earns its place, back-of-envelope estimates with Big-O and latency numbers, failure modes, isolation levels and idempotency as depth topics.

### 2.2 Depth target: "professionally sufficient" means the learner can do these

- Read an unfamiliar error and place it in a layer: shell (command not found, permission denied), process (exit code, traceback), network (DNS, refused, timeout, TLS), HTTP (4xx vs 5xx), database (constraint, lock), browser (console, network tab).
- Explain in two minutes, without notes, what happens between pressing Enter on a URL and seeing the page, naming DNS, TCP/QUIC, TLS, HTTP request/response, HTML/CSS/JS parsing and rendering.
- Choose between list, dict and set and justify it with the cost of the operation they need; spot an accidental O(n²).
- Design a small relational schema, wrap a multi-step change in a transaction, read a query plan well enough to tell scan from index search, and state the cost of an index.
- Say whether a slow task is waiting or computing, and pick async, threads or processes accordingly; recognise a blocked event loop.
- Draw their own application as boxes and arrows with ports, protocols, where state lives, and what is cached where.

### 2.3 Postpone or keep at awareness level (evidence: none of these is needed to build and ship the capstone)

OSI seven-layer memorisation; subnet/CIDR arithmetic; TCP congestion control and the four-way close; implementing sorting algorithms, linked lists, heaps or balanced trees by hand; dynamic programming and LeetCode-style practice; B-tree internals; CPU caches, virtual memory internals, assembly, compilers; CAP theorem formalities, consensus, sharding, microservices, Kubernetes. Teach Yourself CS budgets 100–200 hours for *each* of nine such subjects and addresses working engineers — a post-capstone map, not a prerequisite. [source: https://teachyourselfcs.com/]
One open decision for the learner: if the goal includes interviewing at Chinese tech companies, algorithm drills and "八股" (the 小林coding style of material) become a real requirement and deserve an optional track after S10.

---

## 3. Lesson unit suggested for every concept ("概念卡")

Fields: 名称（中 / English）· 一句话定义 · 比喻 · 比喻在哪里失效 · 亲手实验（命令 + 预期输出）· 先预测再运行的问题 · 常见误解 · 以后在哪个阶段再遇到 · 延伸阅读（已验证链接）.
A ledger file in the handbook (for example `handbook/concepts.md`) tracks each concept's level (见 / 用 / 讲). The AI tutor can check the "讲" level by asking for a three-sentence explanation and comparing it with the misconception lists in section 7 — a script cannot check understanding.

---

## 4. Experiments that ran here, with real output [local unless marked]

### 4.1 Paths, PATH, exit codes
```console
$ type cd; type ls; which python3
cd is a shell builtin
ls is /bin/ls
<uv-bin-dir>/python3
$ echo "$PATH" | tr ':' '\n' | wc -l        # PATH is an ordered list of directories
24
$ ls /nonexistent-dir-xyz; echo "exit code: $?"
ls: /nonexistent-dir-xyz: No such file or directory
exit code: 1
$ python3 -c 'import sys; sys.exit(3)'; echo $?
3
$ python3 -c "import time; time.sleep(30)" & kill -TERM $!; wait $!; echo $?
143                                          # 128 + 15 (SIGTERM)
```

### 4.2 Program vs process; memory vs disk; source → bytecode
```console
$ file whoami.py /bin/ls
whoami.py: ASCII text
/bin/ls:   Mach-O universal binary with 3 architectures: [x86_64 ...] [arm64e ...] ...
$ python3 whoami.py; python3 whoami.py       # same program, two processes
I am process 44483 started by 44479
I am process 44484 started by 44479
$ python3 -c "x = 42; open('saved.txt','w').write(str(x))"
$ python3 -c "print(x)"                       # new process: memory is gone, the file is not
NameError: name 'x' is not defined
$ python3 -c "import dis; dis.dis(lambda price: price * 1.13)"
   LOAD_FAST_BORROW 0 (price) / LOAD_CONST 0 (1.13) / BINARY_OP 5 (*) / RETURN_VALUE
```
Learner terminal, not run here (blocked by sandbox): `ps -o pid,ppid,comm -p $$`, `top`, Activity Monitor.

### 4.3 Text is bytes (`encoding_demo.py`)
```console
$ printf '中文A' > zh.txt; wc -c zh.txt; xxd zh.txt; file zh.txt
7 zh.txt
00000000: e4b8 ade6 9687 41
zh.txt: Unicode text, UTF-8 text, with no line terminators
$ wc -m < zh.txt                 # 7 here because LANG was unset (C locale)
$ LC_ALL=en_US.UTF-8 wc -m < zh.txt
3
```
```text
'中' | len: 1 | UTF-8: b'\xe4\xb8\xad' | GBK: b'\xd6\xd0' | code point: U+4E2D
UTF-8 bytes read as GBK -> 浣犲ソ锛屼笘鐣�
GBK bytes read as UTF-8 -> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4 in position 0
'é' len = 1 | 'é' len = 2 | family emoji: Python len 5, 18 UTF-8 bytes
JS: "👨‍👩‍👧".length = 8, [...s].length = 5, Intl.Segmenter graphemes = 1
utf-8-sig file bytes: b'\xef\xbb\xbfa\n'      CRLF file: b'line1\r\nline2\r\n'
json.dumps({"名字": "小明"})                    -> {"名字": "小明"}
json.dumps(..., ensure_ascii=False)            -> {"名字": "小明"}
sorted(["张伟","李娜","王芳","阿强"])            -> ['张伟','李娜','王芳','阿强']  (code-point order, not pinyin; SQLite ORDER BY gives the same)
int('１２３') = 123, '１２３'.isdigit() = True, 'Ａ' == 'A' is False   (full-width input from a Chinese IME)
```
Python 3.14.9 here: `locale.getencoding()` → `UTF-8`; `sys.flags.utf8_mode` is 1 when LANG is unset and 0 with `LANG=zh_CN.UTF-8` (encoding still UTF-8). macOS file names: a file created with an NFC name is found through the NFD spelling (`os.path.exists` → True) and `listdir` returns the bytes as created.

### 4.4 Numbers
```text
Python: 0.1 + 0.2 = 0.30000000000000004 ; == 0.3 False ; math.isclose True
        Decimal('0.1') + Decimal('0.2') = 0.3 ; Decimal(0.1) = 0.1000000000000000055511151231257827...
        2**64 = 18446744073709551616 (int never overflows) ; 2**53 + 1.0 = 9007199254740992.0 (float lost the +1)
        round(2.5) = 2, round(3.5) = 4 ; 5/2 = 2.5, 5//2 = 2, -7//2 = -4, -7 % 3 = 2
        bin(10) = 0b1010 ; hex(255) = 0xff ; -5 in 8-bit two's complement = 11111011 ; 1 KB = 1000 vs 1 KiB = 1024
Node:   0.1 + 0.2 = 0.30000000000000004 ; Number.MAX_SAFE_INTEGER = 9007199254740991 ; Math.round(2.5) = 3
        JSON.parse('{"id": 12345678901234567890}').id -> 12345678901234567000   (silent precision loss) ; 2n**64n works (BigInt)
```

### 4.5 Big-O you can feel (`bigo_demo.py`, about 13 s total)
```text
membership, value not present      list            set          ratio
n=    1,000                        4.34 us      0.027 us          163x
n=  100,000                      486.41 us      0.033 us       14,780x
n=1,000,000                     4911.17 us      0.033 us      147,351x
queue of n items drained        list.pop(0)   deque.popleft()
n=100,000                          0.698 s        0.0021 s
n=400,000                         11.407 s        0.0091 s
duplicates in n items           nested loops   set()
n=1,000 / 2,000 / 4,000         0.010 / 0.041 / 0.163 s   (x4 when n doubles)   about 16-24 us
binary search: 1,000 -> 10 steps ; 1,000,000 -> 20 ; 1,000,000,000 -> 30
```
Official cost table to cite: "Time complexity of operations on built-in types" in the Python docs (list `x in l` O(n), `l.pop(0)` O(n), dict/set lookup O(1) average, sort O(n log n), string concatenation in a loop quadratic). The old wiki page now says it "has moved to the official Python documentation". [source: https://docs.python.org/3/builtins/time-complexity.html ; https://wiki.python.org/python/language/TimeComplexity.html]

### 4.6 Index vs full scan (`sqlite3 -batch :memory: < index_demo.sql`, 1,000,000 rows)
```text
QUERY PLAN `--SCAN orders                                             Run Time: real 0.029655
CREATE INDEX idx_orders_user_email ON orders(user_email);             Run Time: real 0.313265
QUERY PLAN `--SEARCH orders USING INDEX idx_orders_user_email (user_email=?)   real 0.000051   (about 580x faster)
... WHERE user_email LIKE '%4242@example.com'
QUERY PLAN `--SCAN orders USING COVERING INDEX idx_orders_user_email   real 0.044876   (index cannot seek on a leading wildcard)
```
On an on-disk copy: table 54.7 MB, the one index 30.7 MB (`dbstat`); lookup by `INTEGER PRIMARY KEY` took 0.000044 s; `WHERE lower(user_email) = ...` also fell back to a scan. Three lessons in one run: an index turns O(n) into O(log n); it costs space and write time; it only helps queries shaped like the index.

### 4.7 Transactions, isolation, a real lock error, SQL injection (`tx_demo.py`, stdlib only)
```text
start                                              {'alice': 10000, 'bob': 5000}
transfer alice->bob 3000: COMMIT
transfer alice->bob 999999: ROLLBACK because CHECK constraint failed: balance_cents >= 0
after a failed transfer (atomic: nothing changed)  {'alice': 7000, 'bob': 8000}
writer sees its own uncommitted change             {'alice': 7000, 'bob': 0}
another connection still sees                      {'alice': 7000, 'bob': 8000}
journal_mode: delete
writer while a reader's transaction is still open -> OperationalError: database is locked
autocommit: half a transfer is already permanent   {'alice': 6000, 'bob': 8000}    total 14000 (was 15000)
f-string query matches: 2 rows (injection!)        parameterised query matches: 0 rows
```
Uses `sqlite3.connect(path, autocommit=False)` (Python 3.12+). The docs call `False` "the recommended value", say it means "sqlite3 ensures a transaction is always open", and that the default is still `LEGACY_TRANSACTION_CONTROL` and "will change to `False` in a future Python release". [source: https://docs.python.org/3/library/sqlite3.html] My first version of this script hit `database is locked` by accident because a reading connection never ended its transaction — a realistic beginner trap worth keeping in the lesson.
Also shown in the shell: `SELECT NULL = NULL` prints an empty cell (NULL), `NULL IS NULL` prints 1, `1 + NULL` is NULL.

### 4.8 Concurrency (`conc_demo.py`, `conc_demo2.py`, and a Node one-liner)
```text
python 3.14.9 | GIL enabled: True | cpu cores: 16 | mp start method: spawn
8 I/O-bound tasks (0.5 s wait each):  sequential 4.03 s | 8 threads 0.50 s | asyncio TaskGroup (1 thread) 0.50 s
4 CPU-bound tasks:                    sequential 0.65 s | 4 threads 0.64 s (no gain under the GIL)
                                      4 child processes one after another 0.73 s | at the same time 0.19 s (4 distinct PIDs)
asyncio with time.sleep inside async def (blocks the loop): 2.01 s instead of 0.5 s
race: read, yield, write without a lock: expected 40,000 got 10,007 | with threading.Lock: 40,000
plain `counter += 1`, 4 threads x 1,000,000: got 4,000,000 (the textbook race does NOT reproduce on this build)
asyncio.get_event_loop() -> RuntimeError: There is no current event loop in thread 'MainThread'.
calling an async function without await gives: coroutine
Node:  0 ms sync code first | 1 ms promise microtask | 1 ms timer 0 fired | 3 x 500 ms waits in parallel took 499 ms
       a 300 ms busy loop delayed a 10 ms timer until the loop finished (single thread)
```
`ProcessPoolExecutor` could not run inside this sandbox (1.2); the child-process timing above used `subprocess.Popen`.

### 4.9 A raw HTTP exchange without opening a port (`raw_http.py`: `socket.socketpair()` + `http.server.BaseHTTPRequestHandler`)
```text
>>> REQUEST                              <<< RESPONSE
GET /api/todos?done=false HTTP/1.1\r\n   HTTP/1.1 200 OK
Host: example.test\r\n                   Content-Type: application/json; charset=utf-8
Accept: application/json\r\n             Set-Cookie: session=abc123; HttpOnly; SameSite=Lax; Path=/
User-Agent: course-demo/0.1\r\n          Content-Length: 50
\r\n                                     Connection: close
                                         (blank line)
                                         [{"id": 1, "title": "学习 HTTP", "done": false}]     body is 50 bytes
GET /nope ...                            HTTP/1.1 404 Not Found   {"detail":"Not Found"}
```
Works inside the sandbox, so the tutor can run it. Good first contact with "a request is just structured text" before any framework. Caveat to state in the lesson: this text form is HTTP/1.1; HTTP/2 and HTTP/3 carry the same fields in binary frames.

### 4.10 URL anatomy (Python and Node agree)
```text
urlsplit('https://shop.example.com:8443/products/42?color=red&size=M#reviews')
 -> scheme='https', netloc='shop.example.com:8443', path='/products/42', query='color=red&size=M', fragment='reviews'
quote('中文 搜索') -> %E4%B8%AD%E6%96%87%20%E6%90%9C%E7%B4%A2
new URL("https://例子.测试/路径").href -> https://xn--fsqu00a.xn--0zwm56d/%E8%B7%AF%E5%BE%84
new URL("https://example.com:443/").port -> ""         (default port is dropped)
origin of http://localhost:3000 vs http://localhost:8000 -> different   (this is why front end and API on two ports need CORS)
```

### 4.11 Network commands for the learner's own terminal (not run here; the tools exist on this Mac)
`dig +short example.com` · `dig example.com` (look at the TTL column) · `curl -I https://www.iana.org/help/example-domains` · `curl -v https://... 2>&1 | less` (shows TLS handshake lines, then `>` request headers and `<` response headers) · `curl -s -o /dev/null -w '%{http_code} http/%{http_version} %{time_connect} %{time_appconnect} %{time_starttransfer} %{time_total}\n' URL` (these `-w` variables ran here: `200 http/2 ... t_tls=0.219 t_first_byte=0.381 t_total=0.574` for pypi.org through the proxy; `%{time_namelookup}` for the DNS step exists too [memory], it is meaningless behind this proxy) · `lsof -i :8000` · `nc -vz localhost 8000`.
- System curl here cannot speak HTTP/3. To show `h3`, use the Protocol column in browser DevTools Network instead. [local: `curl --version` features]
- `python3 -m http.server` binds to **all interfaces** by default, port 8000, protocol HTTP/1.0 (help text, Python 3.14.9). Teach `python3 -m http.server --bind 127.0.0.1` so the folder is not served to the whole Wi-Fi network. [local]
- Do not build an exercise on `curl https://example.com` until it has been tried in the learner's real terminal (it failed certificate verification in this sandbox; see 1.2).

### 4.12 Environment variables (`env_demo.sh`)
```text
child sees: parent                 child changed it to: changed_in_child        parent still has: parent
child sees NOT_EXPORTED=[]         python child sees ONE_SHOT = yes             after the one-shot command: []
```

### 4.13 A virtual environment is a small folder (`uv venv --python 3.14` in a scratch dir)
```text
.venv/ contains: .gitignore  CACHEDIR.TAG  bin  lib  pyvenv.cfg          size: 60K
pyvenv.cfg: home = <uv-python-dir>/cpython-3.14.9-macos-aarch64-none/bin ; include-system-site-packages = false ; uv = 0.13.5
.venv/bin/python -> symlink to the base interpreter (not a copy of Python)
inside:  sys.prefix = <proj>/.venv ; sys.base_prefix = <uv-python-dir>/cpython-3.14.9-... ; site-packages = <proj>/.venv/lib/python3.14/site-packages
activate does two things: VIRTUAL_ENV='<absolute path>/.venv' and PATH="$VIRTUAL_ENV/bin:$PATH"   (absolute path: moving the project breaks it)
```
The default `python3` carries an `EXTERNALLY-MANAGED` marker file (present for the uv-managed 3.14.9, absent for `/usr/bin/python3` 3.9.6) [local]; that marker is the mechanism behind "pip refuses to install globally" [memory: PEP 668; I did not run pip].

### 4.14 A branch is a pointer, not a copy (throw-away repo, global config untouched)
```text
$ cat .git/refs/heads/main        -> 4a69e2fe32124c70998785f3e9f2823b657026e7     (41 bytes: 40 hex chars + newline)
$ cat .git/HEAD                   -> ref: refs/heads/main
$ git branch experiment           -> .git grew from 124 KB to 132 KB; the new file holds the same commit id
$ git log --oneline --graph --all -> * bb7fec1 (HEAD -> experiment) try an idea / * 4a69e2f (main) second snapshot / * 35b626e first snapshot
```
Matches Pro Git's wording: a branch is "指向提交对象的可变指针", creating one is "往一个文件中写入 41 个字节", and Git stores "快照" rather than differences. [source: https://git-scm.com/book/zh/v2/Git-分支-分支简介] This depends on the `files` ref backend, which is what `git init` produced here; a future default of `reftable` would hide these files [memory: Git 3.0 plans].

### 4.15 Caching, time, hashing
```text
no cache: 5 identical 0.2 s calls 1.03 s | functools.lru_cache 0.21 s | CacheInfo(hits=4, misses=1, maxsize=128, currsize=1)
price changed from 3 to 5 -> cached function still returns 3 until cache_clear()      (staleness in three lines)
unix time 1795091548 = 2026-11-19T12:32:28+00:00 = 2026-11-19T20:32:28+08:00 (Shanghai) ; datetime(2026,11,19,15,0).tzinfo is None
base64 of '密码123' -> b'5a+G56CBMTIz' and back (encoding: anyone can reverse it)
sha256(b'hello') = 2cf24dba... ; sha256(b'hellp') = fdd7585e... (hash: one-way, tiny change -> unrelated output) ; sha1 hex length 40 = a Git commit id
```

---

## 5. What changed recently (older tutorials will mislead here)

**Web and protocols**
- HTTP/3 is used by 41.2% of websites and HTTP/2 by 35.6% (W3Techs, November 2026). "HTTP is a text protocol over TCP" is only true of HTTP/1.1. [source: https://w3techs.com/technologies/details/ce-http3 ; .../ce-http2] MDN zh-CN states it plainly: "HTTP/2 是二进制协议而不是文本协议" and HTTP/3 "使用 QUIC 而不是 TCP". [source: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Guides/Evolution_of_HTTP]
- Current HTTP specs: RFC 9110 (semantics), 9111 (caching), 9112 (HTTP/1.1), 9113 (HTTP/2), 9114 (HTTP/3). A new method, QUERY (safe, body-carrying), became RFC 10008 in June 2026; teach GET/POST/PUT/PATCH/DELETE and mention QUERY only as "new, check support". [source: https://httpwg.org/specs/ ; https://www.rfc-editor.org/info/rfc10008]
- TLS 1.3 is now specified by RFC 9846 (July 2026), which obsoletes RFC 8446. Chinese articles that explain "the client encrypts a random number with the server's public key" describe the RSA key exchange that TLS 1.3 removed. [source: https://www.rfc-editor.org/info/rfc9846 ; RSA removal: memory]
- Chrome now asks before loading a plain-HTTP public site for all users by default (Google post dated 2026-10-21); per the post, local IP addresses and single-label host names are exempt. `http://localhost:8000` is expected to keep working, but I did not test a browser. [source: https://blog.google/security/chrome-now-warns-before-insecure-http-connections/]
- Maximum public certificate lifetime is being cut from 398 days to 47 days between March 2026 and March 2029 (CA/Browser Forum ballot SC-081v3, passed). Manual certificate handling is no longer a viable thing to teach; automation is. [source: https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/]
- Cookies: Chrome keeps third-party cookies as a user choice and retired most Privacy Sandbox APIs (post dated 2025-10-17); Safari has blocked cross-site cookies by default since 13.1 (2020); Firefox blocks known tracking cookies by default; a cookie without `SameSite` is treated as `Lax`. Tutorials saying "third-party cookies are being removed from Chrome" are out of date. The cookie RFC is still RFC 6265; its replacement (rfc6265bis-22) sits in the RFC Editor queue. [source: https://privacysandbox.google.com/blog/update-on-plans-for-privacy-sandbox-technologies ; https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/ ; https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Guides/Cookies ; https://datatracker.ietf.org/doc/draft-ietf-httpbis-rfc6265bis/]
- About half of Google's users now connect over IPv6 (APNIC blog post "Google hits 50% IPv6", April 2026 — seen in search results, not fetched). Addresses in logs and tools will often be IPv6; `localhost` resolves to both `127.0.0.1` and `::1` here [local].
- MDN moved its learning area to `/docs/Learn_web_development/...` and its HTTP guides to `/docs/Web/HTTP/Guides/...`; the URLs in section 6 are the current ones. `howdns.works` / `howhttps.works` now redirect to dnsimple.com.

**Python**
- `docs.python.org/3/` now serves Python **3.15.2** documentation (3.15 was released in October 2026), while this machine runs 3.14.9. Link lessons to versioned URLs (`/3.14/` or `/zh-cn/3.14/`) so the learner does not meet features that are absent locally (`lazy import`, `frozendict`, `TaskGroup.cancel`). [source: https://docs.python.org/3/whatsnew/3.15.html ; https://docs.python.org/zh-cn/3.14/howto/a-conceptual-overview-of-asyncio.html shows "3.14.10 文档"]
- Python 3.15 makes UTF-8 the default text encoding everywhere (PEP 686). On 3.14 the default is the locale's encoding, which is UTF-8 on this Mac [local], so nothing breaks here, but files will travel to machines where it is not. Keep `encoding="utf-8"` explicit as the house rule. [source: whatsnew/3.15]
- Python 3.15 error messages now coach people arriving from other languages (`[1,2,3].push(4)` → "Did you mean '.append'?"). Not on 3.14. [source: whatsnew/3.15]
- Free-threaded CPython is officially supported since 3.14 (PEP 779), but it is a separate build; the interpreter here has the GIL on [local]. "Python threads can never run in parallel" is now "depends on the build". Since 3.14 the default `multiprocessing` start method on Linux is `forkserver`; macOS stays `spawn` [local]. [source: https://docs.python.org/3/whatsnew/3.14.html]
- `asyncio.get_event_loop()` raises `RuntimeError` when no loop is running since 3.14 (reproduced here), and the policy system goes away in 3.16. Any tutorial built on `loop = asyncio.get_event_loop(); loop.run_until_complete(...)` fails on this machine. Use `asyncio.run()` and `asyncio.TaskGroup`. [source: https://docs.python.org/3/library/asyncio-eventloop.html]
- The classic "two threads doing `counter += 1` lose updates" demo did not reproduce on 3.14.9 (4.8). Show the race with an explicit yield between read and write, then fix it with a lock.
- The CPython wiki's TimeComplexity page has moved into the official docs (4.5).

**Databases and tools**
- sqlite3 shell: since 3.53.0 (April 2026) interactive sessions print Unicode box tables by default while batch/piped sessions keep the old `a|b|c` format; 3.54.0 changed header behaviour again. Here, piped output was `1|a@example.com|上海` and `.mode box` drew rounded boxes. Auto-checks must set the mode explicitly (`sqlite3 -batch -csv`, `-json`, or `.mode list`) and never compare screenshots of default output. [source: https://www.sqlite.org/changes.html ; local]
- PostgreSQL: supported majors are 18 (18.7), 17, 16, 15; version 19 is at RC2. Every statement outside `BEGIN` runs in its own implicit transaction. [source: https://www.postgresql.org/support/versioning/ ; https://www.postgresql.org/docs/current/tutorial-transactions.html]
- Docker's own docs now define a container as "an ordinary process on your computer ... that runs in isolation" and state that "Docker Desktop runs your Linux containers inside a small Linux VM". [source: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/]

**Curricula**
- The Missing Semester has a 2026 edition (9 lectures, including "Agentic Coding", "Packaging and Shipping Code", "Code Quality"; AI use is folded into every lecture). The Chinese site tracks 2026, but three lecture titles (debugging/profiling, version control, packaging) are still in English there today. [source: https://missing.csail.mit.edu/ ; https://missing-semester-cn.github.io/]
- CS50x is at its 2026 edition and has an "Artificial Intelligence" unit between weeks 7 and 8. [source: https://cs50.harvard.edu/x/]
- Designing Data-Intensive Applications has a second edition (March 2026, with Chris Riccomini); a community Chinese translation of the second edition is online. [source: https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html ; https://ddia.vonng.com/]
- The Twelve-Factor App page (English and zh_cn) still says "Last updated 2017". [source: https://12factor.net/ ; https://12factor.net/zh_cn/]

---

## 6. Free resources per topic (each URL loaded today unless marked)

Level key: A = true beginner, B = after some programming, C = working-engineer depth. "zh" = Chinese text or Chinese subtitles.

| Topic | Resource (URL) | Lang | Level | Notes |
|---|---|---|---|---|
| Big picture of computing | Crash Course Computer Science, 40 episodes of about 10 min. Chinese-subtitled 精校版: https://www.bilibili.com/video/av21376839/ ; episode list: https://thecrashcourse.com/topic/computerscience/ ; subtitle project: https://github.com/1c7/Crash-Course-Computer-Science-Chinese | zh subs | A | Best S0–S1 "see it" material. Useful episodes: 4 binary, 6–8 memory/CPU/programs, 13–14 algorithms/data structures, 18–20 OS/storage/files, 22 command line, 28–30 networks/internet/web, 31–33 security. Translation finished in 2018; no cloud or containers. |
| Intro CS course | CS50x 2026 https://cs50.harvard.edu/x/ (weeks: Scratch, C, Arrays, Algorithms, Memory, Data Structures, Python, SQL, AI, HTML/CSS/JS, Flask) | en; official dubs in Portuguese and Spanish (no Chinese mentioned) | A, but heavy | "Two thirds of CS50 students have never taken CS before"; ten problem sets plus a project. Weeks 1–5 are C. Use selectively: Week 0, Week 7 (SQL on SQLite), Week 8, and the shorts "Internet Primer", "IP", "TCP", "HTTP", "DOM" (https://cs50.harvard.edu/x/shorts/). Chinese bilingual uploads exist on Bilibili (titles seen in search); I could not confirm a specific video ID. |
| Python intro | CS50P https://cs50.harvard.edu/python/ ; third-party upload with 中英字幕: https://www.bilibili.com/video/BV1fFyJBFE92/ | en / zh subs | A | Ten weeks, pure Python; closer to this roadmap than CS50x. |
| How the web works | MDN zh-CN: 万维网是如何工作的 https://developer.mozilla.org/zh-CN/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works (updated 2026-04-10) ; 互联网是如何工作的 .../Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work (2026-02-28) ; 什么是 URL .../Howto/Web_mechanics/What_is_a_URL ; 客户端服务端交互概述 .../Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview (2026-09-21) | zh | A | Backbone for S4. Uses the road / shop / address analogy (街道 = 网络连接, 交通工具 = TCP/IP, 地址簿 = DNS, 下订单说的话 = HTTP). Has raw GET/POST examples. |
| HTTP | MDN zh-CN: HTTP 概述 https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Guides/Overview ; HTTP 的发展 .../Guides/Evolution_of_HTTP ; HTTP Cookie .../Guides/Cookies ; HTTP 缓存 .../Guides/Caching (updated 2026-07-01) | zh | A–B | Current and accurate. "HTTP 无状态，但并非无会话". MDN's term for header is 标头 (everyday Chinese usage: 请求头 / 响应头). |
| DNS / HTTPS comics | https://dnsimple.com/comics/how-dns-works/ (language switcher lists Simplified Chinese) ; https://dnsimple.com/comics/how-https-works/zh/ | zh | A | Short and friendly. I could not see which TLS version the handshake episode depicts. |
| Browser internals | MDN zh-CN 渲染页面：浏览器的工作原理 https://developer.mozilla.org/zh-CN/docs/Web/Performance/Guides/How_browsers_work ; Chrome "Inside look at modern web browser" parts 1–4, e.g. https://developer.chrome.com/blog/inside-browser-part1 and .../inside-browser-part3 | zh / en | B | MDN page walks navigation → DNS → TCP → TLS → parsing → style → layout → paint → compositing. The Chrome series is the clearest on processes and threads in a browser (English only through my fetch). |
| Web fundamentals inside a full-stack course | Full Stack Open, Part 0 https://fullstackopen.com/en/part0/fundamentals_of_web_apps ; Chinese site https://fullstackopen.com/zh/ | en / zh | A–B | Teaches HTTP through the DevTools Network tab; "Always keep the Developer Console open". Course stack is React/Node/MongoDB; the zh landing page announces the 2022 edition. |
| Networking, deeper | 小林coding 图解网络 https://xiaolincoding.com/network/ | zh | B–C | Free online, diagram-rich. Self-description: for readers with "一点网络基础" and "适合面试突击". Recommend only 2.1 (TCP/IP 分层) and 2.2 (键入网址到网页显示，期间发生了什么). The TCP part alone is 24 articles. Site carries ads for paid courses. |
| Networking, HTTP/3 | HTTP/3 explained (Chinese) https://http3-explained.haxx.se/zh | zh | B | By curl's author. Optional for S8/S10. |
| "What happens when…" | https://github.com/skyline75489/what-happens-when-zh_CN | zh | B | Dated: no TLS 1.3, HTTP/2 or HTTP/3. Curiosity reading only. |
| How programs run / OS | 小林coding 图解系统 https://xiaolincoding.com/os/ (2.1 CPU 是如何执行程序的, 2.7 为什么 0.1 + 0.2 不等于 0.3, 5.1 进程、线程基础知识) ; 阮一峰 进程与线程的一个简单解释 https://www.ruanyifeng.com/blog/2013/04/processes_and_threads.html ; "Putting the You in CPU" https://cpu.land/ ; OSTEP https://pages.cs.wisc.edu/~remzi/OSTEP/ (v1.10) | zh / zh / en / en | B / A / B / C | 阮一峰's factory analogy assumes one core ("一次只能供给一个车间使用"). cpu.land is Linux-centric (ELF, fork-exec): S8 enrichment. OSTEP is post-capstone. |
| Encodings and numbers | Python Unicode 指南 https://docs.python.org/zh-cn/3/howto/unicode.html ; tonsky "The Absolute Minimum ... Unicode in 2023" https://tonsky.me/blog/unicode/ (links a Chinese translation) ; 阮一峰 字符编码笔记 https://www.ruanyifeng.com/blog/2007/10/ascii_unicode_and_utf-8.html ; https://0.30000000000000004.com/ ; Hello 算法 3.3 数字编码 and 3.4 字符编码 | zh / en+zh / zh / en / zh | B / B / A / A / B | The Python HOWTO gives the rule "尽快对输入数据进行解码，并只在最后对输出进行编码". 阮一峰's 2007 note is clear on ASCII → Unicode → UTF-8 but its Windows Notepad details are obsolete. |
| Data structures, complexity | 《Hello 算法》 https://www.hello-algo.com/ (repo https://github.com/krahets/hello-algo : release 1.3.0 dated 1 Jan 2026, about 132k stars, Python among 12+ code languages, CC BY-NC-SA 4.0) ; VisuAlgo 中文 https://visualgo.net/zh ; Python Tutor https://pythontutor.com/ ; Python docs time-complexity page (4.5) | zh | A–B | Chapters 2–6 (复杂度分析, 数据结构, 数组与链表, 栈与队列, 哈希表) match the "essentials"; 7–9 (树, 堆, 图) for awareness; 10–15 optional. The site answered 429 to automated fetches, so the AI tutor cannot read it; link it for the learner's browser. Licence is CC BY-NC-SA 4.0 (non-commercial, attribution, share-alike): simplest is to link rather than paste. |
| Databases | SQLite "Query Planning" https://www.sqlite.org/queryplanner.html ; PostgreSQL tutorial, transactions https://www.postgresql.org/docs/current/tutorial-transactions.html ; 廖雪峰 SQL 教程 https://liaoxuefeng.com/books/sql/introduction/index.html ; SQLBolt https://sqlbolt.com/ ; Select Star SQL https://selectstarsql.com/ ; Use The Index, Luke https://use-the-index-luke.com/ | en / en / zh / en / en / en | B / B / A / A / A / C | The SQLite page is the best index explanation I found ("indices should never change the answer, only help SQLite to get to the answer more quickly"). 廖雪峰 is Chinese with an in-browser playground but is MySQL-flavoured (playground engine is AlaSQL). The last three have no Chinese edition. |
| Concurrency | Python docs asyncio 的概念概述 https://docs.python.org/zh-cn/3.14/howto/a-conceptual-overview-of-asyncio.html | zh | B | Official, translated; event loop as "乐队指挥". Goes into coroutine internals in part 2 — assign part 1 only. |
| Tools and environment | The Missing Semester 2026 https://missing.csail.mit.edu/ ; 中文 https://missing-semester-cn.github.io/ | en / zh (partial) | B | Assumes you already program. Lecture "Command-line Environment" covers arguments, streams, environment variables, return codes, signals; "Packaging and Shipping Code" covers dependencies, lockfiles, venvs (uses uv), containers, configuration. Use as follow-up reading after our own Stage 1/3/8 lessons, not as the primary text. |
| Small-system design | 12-Factor 中文 https://12factor.net/zh_cn/ ; MonolithFirst https://martinfowler.com/bliki/MonolithFirst.html ; ByteByteGo system-design-101 https://github.com/ByteByteGoHq/system-design-101 ; system-design-primer 中文 https://github.com/donnemartin/system-design-primer/blob/master/README-zh-Hans.md ; DDIA 第二版中文 https://ddia.vonng.com/ | zh / en / en / zh / zh | B / B / B / C / C | 12-Factor is short and maps directly to S8. Fowler: "you shouldn't start a new project with microservices". The two GitHub collections aim at large-scale interview design ("学习如何设计大型系统。为系统设计的面试做准备。") — use single diagrams, not as a syllabus. DDIA is post-capstone; the translation site asks readers to treat it as study material and buy the original. |
| Maps for later | Teach Yourself CS https://teachyourselfcs.com/ ; 中文 https://github.com/izackwu/TeachYourselfCS-CN ; CS自学指南 https://csdiy.wiki/ ; roadmap.sh https://roadmap.sh/full-stack ; MDN Curriculum https://developer.mozilla.org/en-US/curriculum/ | en / zh / zh / en / en | C / C / B–C / A / A | TYCS: nine subjects, 100–200 hours each, "extensively updated in May 2020". csdiy lists university courses and recommends CS50P / CS61A / Missing Semester for 编程入门. MDN Curriculum's first core module is "Web standards: understand how the web works at a high level". |

Paid Chinese-language books often recommended to complete beginners for exactly these topics [memory, not checked today]: 《计算机是怎样跑起来的》《程序是怎样跑起来的》(矢泽久雄), 《网络是怎样连接的》(户根勤), 《编码：隐匿在计算机软硬件背后的语言》(Petzold). 《图解HTTP》 predates HTTP/2.

---

## 7. Analogies in plain Chinese, with where each one breaks

Rule for lesson writers: every analogy is followed by one line "这个比喻在哪里不成立" and by the experiment that shows the real mechanism.

| 概念 | 推荐比喻 | 哪里不成立 / 要避免的说法 | 真实机制的实验 |
|---|---|---|---|
| 路径 path | 写地址。绝对路径 = 从"省、市"写起的完整地址；相对路径 = "从我现在站的位置，往隔壁走"。`~` 是我家，`.` 是这里，`..` 是上一层。 | 路径只是一串文字，可以指向不存在的东西。避免"路径 = 快捷方式"。本机不区分大小写（`CaseTest.txt` 和 `casetest.txt` 是同一个文件），Linux 服务器区分。 | 4.1 ；大小写实验（1.1） |
| 进程 process | 程序是菜谱（硬盘上的文件），进程是照着菜谱正在做的那一锅菜，有自己的灶台和食材（内存）和编号（PID）。同一份菜谱可以同时开两锅。 | 避免"进程 = 应用/窗口"：一个浏览器是很多进程；关掉窗口不等于进程结束。阮一峰的"工厂/车间"比喻默认只有一个核，本机有 16 个核，多个进程真的同时在跑。 | 4.2（两个 PID）；4.8（4 个进程并行 0.19 s） |
| 线程 thread | 同一锅菜旁边的几位厨师，共用一个灶台和食材，所以会抢东西，需要"锁"。 | 在本机这个 Python 里，多位厨师一次只有一位能动手做"计算"（GIL），等待（等外卖、等水开）时才真正交替。 | 4.8（线程对计算无加速；无锁丢数据） |
| 端口 port | IP 地址是大楼地址，端口是楼里的分机号/房间号（0–65535）。同一时刻一个号码只能由一个进程接听，所以会有 "Address already in use"。`localhost` 是"本楼内线"。 | 不是 USB 口那种物理接口，只是一个数字标签。访问方自己也会用一个临时端口，比喻里看不到。"0.0.0.0" 不是一个可访问的地址，而是"所有网卡都接听"。 | 学员终端：`python3 -m http.server --bind 127.0.0.1` 开两次看报错；`lsof -i :8000` |
| HTTP 请求 | 填一张格式固定的订单寄出去：方法（要做什么）、路径（要哪样东西）、标头（备注栏）、主体（随单附上的东西）；对方寄回回执：状态码 + 内容。店家不记得你上一单（无状态），所以每次都要出示会员卡（Cookie）。 | 避免"像打电话聊天"：服务器不会主动打给你，也不记得上文。打开一个网页不是一次请求，而是几十次。"能读的文本"只适用于 HTTP/1.1。 | 4.9（原始请求/响应）；DevTools Network |
| API | 餐厅的菜单 + 点菜窗口：菜单规定能点什么、怎么点、会得到什么；后厨怎么做不用管，也不许进。另一个角度：插座标准，形状和电压对上就能用。 | "服务员"比喻只强调传话，漏掉了真正的重点：约定（契约）。API 不一定经过网络，`len()`、`open()` 的用法也是 API。API 不等于一个网址，也不等于 API key。 | 4.9 ；后续 FastAPI 的 `/docs` |
| 数据库索引 index | 书末的"索引"或字典的拼音检字表：按关键词排好序，告诉你在第几页，直接翻到；没有它就得从第一页翻到最后一页（全表扫描）。 | 不是书前面的"章节目录"（中文里"目录"和"索引"常被混用）。索引不是越多越好：占空间（本实验 30.7 MB 对 54.7 MB 的表），每次写入都要同步更新；只帮得上"按这个词开头查"的问题。 | 4.6（0.0297 s → 0.000051 s；`LIKE '%…'` 仍是 SCAN） |
| 版本控制 | 游戏存档：每次提交是一个带说明的存档点，保存的是整个项目当时的样子（快照），可以读档，也可以比较两个存档。 | 避免"Git = 网盘/自动同步"：不提交就没有存档，不推送就不在 GitHub 上；Git 不是 GitHub。提交也不是 Cmd+S，而是有意挑选内容并写说明。如果学员的文件夹在 iCloud 之类的同步文件夹里，这个误解尤其容易形成。 | 4.14 |
| 分支 branch | 贴在某个存档点上的一张便利贴（书签），你往前提交，它跟着挪；另开一张便利贴就是另一条线。 | 最常见的误解："分支 = 把整个文件夹复制一份"。实际只多了一个 41 字节的小文件。"树枝"这个字面意思也暗示分出去就不再合并。 | 4.14（`.git` 124 KB → 132 KB） |
| 环境变量 | 进程出门时随身带的便签条：每个进程一份，子进程出生时抄一份父进程的，自己改了不会传回去。用来放"换个环境就要变"的配置。 | 避免"全局设置，改了处处生效"：只影响当前终端和它之后启动的程序；新开终端要写进 `~/.zshrc` 才有；从 Dock 启动的图形程序看不到。也不是保险箱：没有加密，子进程和日志都可能看到。 | 4.12 |
| 依赖 dependency | 做菜用的现成调料和半成品：没有它这道菜做不出来。清单（`pyproject.toml`）是购物单"要酱油，3.x 都行"；锁文件（`uv.lock`）是小票"实际买的是 3.2.1"。调料自己也有配料表（传递依赖）。 | 不是"可选插件"；装依赖不是"往电脑里装软件"，而是装进这个项目。版本不是越新越好。 | `uv tree`（后续）；4.13 |
| 虚拟环境 | 每个项目自己的调料架：就是项目里的一个普通文件夹 `.venv`，A 项目的调料不会和 B 项目混。"激活"只是把这个架子排到 PATH 的最前面。 | "虚拟"容易让人以为是虚拟机：它不隔离系统、文件和网络，也不是安全边界。里面没有一份完整的 Python（是指向原解释器的链接）。项目改名或移动后会失效，删掉重建即可，所以不进 Git。用 `uv run` 时根本不需要激活。 | 4.13（60K；`pyvenv.cfg`；软链接） |
| 容器 container | 把程序连同它需要的整套厨房用具一起装箱（镜像 = 装好的箱子，容器 = 打开箱子正在运行的那一份），搬到哪里都能照样开火。 | 避免"轻量虚拟机"：容器是宿主机上的一个被隔离的普通进程，共用宿主机的内核。但在 Mac 上，Docker Desktop 确实先开了一台小的 Linux 虚拟机，容器跑在它里面——两层都要讲清。容器里写的文件默认会随容器一起消失。 | S8，学员终端（本会话不能用 Docker） |
| 部署 deployment | 把在自家厨房试做成功的菜，搬到对外营业的店里，并保证它一直开门：一台不关机、有公网地址的电脑，装好依赖和配置，把程序启动成进程，接上域名和 HTTPS，出问题能退回上一版。 | 不是"上传文件"（静态页面除外）；不等于"发版本号"。`localhost` 的链接发给别人打不开。"在我电脑上能跑"只是开始。 | S8 |

Further analogies that tested well against the mechanisms above:
- **DNS**：通讯录/查号台，按"根 → 顶级域 → 权威"逐级问，问到的结果会抄在小本上并带保质期（TTL）。不成立处：不是一本集中的大电话簿。
- **TCP**：挂号信，丢了重寄、按顺序拼好；**TLS/HTTPS**：先核对对方证件（证书），再把信装进只有双方能拆的信封。不成立处：TLS 不隐藏你在访问哪个网站的地址这一事实，也不保证对方网站本身可信 [memory]。
- **Cookie**：店家发的会员卡，下次来自动出示。不成立处：卡是浏览器按规则自动出示的（域名、路径、`SameSite`），不是你决定的。
- **事务**：转账要么两边都成，要么都不成。实验见 4.7。
- **缓存**：把常用电话抄在手边的便签上，快，但对方换号时便签不会自己更新。实验见 4.15。
- **Big-O**：在一百万个名字里找人——逐个问 O(n)，按字典对半翻 O(log n，20 步)，直接知道座位号 O(1)。实验见 4.5。
- **哈希表 / 字典**：快递柜，凭取件码直接到格子。**栈**：一摞盘子，后放的先拿（浏览器后退、撤销）。**队列**：排队，先到先走。
- **异步**：一位服务员照看多桌，点完菜不站在厨房门口等，而是去招呼别桌。多线程 = 多位服务员；多进程 = 多家分店各有厨房。不成立处："异步 = 更快"是误解：对计算没有帮助，而且只要有一桌让服务员原地傻等（阻塞调用），所有桌都停（4.8 的 2.01 s）。
- **字符编码**：字符与数字的对照表；乱码 = 拿错了对照表去读。要避免的旧说法："一个汉字占两个字节"（那是 GBK；UTF-8 里常用汉字是 3 个字节，见 4.3）、"Unicode 就是 UTF-8"。

---

## 8. Pitfalls a beginner will hit (ordered by when they appear)

1. **Case-insensitive disk**: renaming `Readme.md` → `README.md` looks like no change to tools; code that imports `Utils.py` as `utils` works here and fails on Linux. [local]
2. **"command not found"** is a PATH question, not a broken install; a new terminal window does not inherit `export` made in another window. [local 4.12]
3. **`wc -m`, sorting and other text tools depend on the locale**; with `LANG` unset `wc -m` counts bytes (7 instead of 3 for `中文A`). Auto-checks should set `LC_ALL` explicitly. [local]
4. **乱码** always means "decoded with the wrong table". Chinese Windows files in GBK and CSV files from Excel (BOM, GBK) are the usual sources [memory]; reproduce on purpose once (4.3).
5. **`json.dumps` shows Chinese as `\uXXXX`** by default; this is not corruption. [local]
6. **Sorting Chinese** gives code-point order, not pinyin order, in Python and in SQLite. [local]
7. **Full-width characters from the IME** (`１２３`, `Ａ`, `，`, `（`) look the same and are different characters; `int('１２３')` even works, `'Ａ' == 'A'` does not. Chinese punctuation typed into code is a classic first-week syntax error. [local for the comparisons; frequency: memory]
8. **Floats for money**, `round(2.5) == 2`, JS `Math.round(2.5) == 3`, big IDs silently rounded by `JSON.parse`. [local]
9. **`localhost` means "this machine"**: links cannot be shared; two dev servers cannot share a port; `http.server` exposes the folder to the LAN unless bound to 127.0.0.1. [local help text]
10. **Reading `curl -v`**: lines with `*` are connection/TLS notes, `>` is what was sent, `<` is what came back; the output can contain secrets. [local]
11. **Same host, different port = different origin** (CORS surprise when the front end is on :5173 and the API on :8000). [local 4.10]
12. **Cache confusion**: "I changed the file but the browser shows the old one" → hard reload or "Disable cache" in DevTools; `no-cache` does not mean "do not store" ("`no-cache` 指令不会阻止响应的存储"). [source: MDN 缓存]
13. **`database is locked`** in SQLite when a connection leaves a transaction open; forgetting `commit()` makes writes vanish when using `autocommit=False`. [local 4.7]
14. **`NULL = NULL` is not true.** [local]
15. **Indexes are not free and not magic** (leading-wildcard `LIKE`, functions on the column). [local 4.6]
16. **Calling an `async` function without `await`** returns a coroutine object and does nothing; `time.sleep` or any blocking library call inside `async def` freezes every request. [local 4.8]
17. **Old asyncio boilerplate** (`get_event_loop().run_until_complete`) crashes on this machine's Python. [local]
18. **Docs/version mismatch**: unversioned Python doc links describe 3.15; the machine has 3.14. [source + local]
19. **Virtual environment breaks after moving or renaming the project folder** (absolute paths inside `activate` and `pyvenv.cfg`); recreate it. [local 4.13]
20. **Mental-model bugs from analogies**: branch = folder copy, Git = cloud sync, container = small VM, environment variable = global setting, API = waiter, HTTP = phone call. Each is corrected in section 7.

---

## 9. Recommendations and challenges to the plan

**Recommendations**
1. Add the "原理线" as a first-class artefact: the matrix in section 2 becomes a ledger in the handbook; each stage's generator pulls the concepts due in that stage and their "return visits".
2. Use the experiments in section 4 as the core of each 原理小课; they are short, need no installs, and their outputs are known for this machine. Mark each as "tutor can run" or "learner terminal only" (process, port, DNS, Docker, real servers).
3. Standardise six instruments and reuse them: Activity Monitor / `ps`; `curl -v`; browser DevTools (Network, Application, Console); `dig`; `EXPLAIN QUERY PLAN`; `timeit`. Add Python Tutor in Stage 2.
4. House defaults to state as rules, each backed by an experiment above: UTF-8 with explicit `encoding=`; LF line endings; integer cents or `Decimal` for money; UTC with offset for stored times; parameterised SQL only; multi-step writes inside a transaction; big IDs as strings across JSON; dev servers bound to 127.0.0.1; `asyncio.run` + `TaskGroup`, never blocking calls in `async def`; measure before optimising.
5. Chinese first, English term in parentheses at first use, glossary in the handbook (section 10). Give macOS UI names in English with a Chinese gloss, and check the learner's system language first (section 1.1).
6. Link out sparingly and precisely (a specific MDN page or a specific episode), always to a URL verified in section 6, with one line on what to read and what to skip. Do not assign whole external courses.
7. For "讲"-level checks, have the tutor ask for a short explanation and compare against the misconception list; keep scripts for "用"-level checks.
8. When generating later stages, re-verify version-sensitive facts flagged here: PostgreSQL 19 release, the cookie RFC, Python default docs version, sqlite3 shell output, Chrome HTTP warnings.

**Challenges to the planned roadmap**
1. The roadmap names no home for CS fundamentals; "taught just-in-time" will silently become "never taught" unless the ledger exists and each stage generator is required to consume it.
2. Stage 1 lists "terminal, editor, Markdown, Git, GitHub basics, getting help" but not the OS ideas the terminal exposes (process, exit code, environment variable, PATH, streams, text-as-bytes). They belong in Stage 1. Stage 8 "Linux" should build on them.
3. Stage 4 "how the web works" should be a hands-on lab with instruments, placed before HTML, and ports/localhost must be taught at the first local server, wherever that happens.
4. Stage 5 lists "SQL, HTTP APIs with FastAPI, PostgreSQL". Teach the relational model, transactions and indexes on SQLite first (already installed; `psql` is not), then introduce PostgreSQL for what SQLite does not show (server process, port, users, concurrent writers).
5. Stage 2 should own data-structure choice and Big-O intuition, number and text representation. There is no need for a separate algorithms stage; whether to add an optional interview track after Stage 10 is the learner's decision.
6. Stage 7 (auth, OWASP) silently depends on origin, cookies, hashing vs encryption and TLS. Schedule those as "see" items in Stages 4–5 so Stage 7 is not three stages of prerequisites at once.
7. Stage 10 "architecture" should be small-system design (monolith first, 12-factor, estimates, failure modes). The popular free material is large-scale interview design and will pull the learner toward premature complexity.
8. Two topics missing from the brief's topic list but needed by every full-stack project: time representation (Unix time, UTC, time zones) and hash vs encoding vs encryption. Both are in the matrix.
9. The "auto-check scripts + AI tutor" design meets a hard limit: in this session's sandbox the tutor cannot see processes, bind ports, resolve DNS or use `multiprocessing`. Plan those labs as learner-run with file-based evidence.
10. Popular Chinese resources are either interview-oriented (小林coding: "面试突击", "八股") or dated (阮一峰 2007–2016; what-happens-when). The workspace should own the short explanations and treat these as optional reading with caveats.

---

## 10. Glossary seeds (中文 / English; variants the learner will meet)

进程 process · 线程 thread · 端口 port · 环境变量 environment variable · 路径 path（绝对 absolute / 相对 relative）· 标准输入/输出/错误 stdin / stdout / stderr · 退出码 exit code · 信号 signal · 字节 byte · 位（比特）bit · 编码 encoding · 码位（码点）code point · 乱码 mojibake · 浮点数 float · 客户端 client · 服务器（服务端）server · 请求 request · 响应 response · 标头（请求头、首部）header · 主体（请求体）body · 状态码 status code · 域名 domain name · 互联网 Internet（旧译 因特网）· 万维网 the Web · 源 origin · 会话 session · 缓存 cache · 列表 list · 字典 dict / 哈希表 hash table（散列表）· 集合 set · 栈 stack · 队列 queue · 树 tree · 图 graph · 时间复杂度 time complexity · 关系型数据库 relational database · 主键 primary key · 外键 foreign key · 事务 transaction · 索引 index · 查询计划 query plan · 并发 concurrency · 并行 parallelism · 异步 asynchronous · 事件循环 event loop · 竞态条件 race condition · 锁 lock · 幂等 idempotent · 依赖 dependency · 锁文件 lockfile · 虚拟环境 virtual environment · 镜像 image · 容器 container · 部署 deployment · 提交 commit · 分支 branch · 快照 snapshot · 仓库 repository.

---

## 11. Not verified / open

- Whether `ps`, `dig`, port binding, `multiprocessing` and `curl https://example.com` behave normally in the learner's own terminal app (expected, not tested; I only have the sandbox).
- Why `https://example.com/` failed certificate verification here.
- How `www.hello-algo.com` and Cloudflare's Chinese Learning Center load in a normal browser today (bot protection blocked my tools). Hello 算法 facts above come from its GitHub repository and `mkdocs.yml`.
- A specific Bilibili video ID for CS50x 2026 with Chinese subtitles; and the completeness, accuracy and licensing of third-party Bilibili uploads in general (including the CS50P one linked above).
- Whether the Chrome "Inside look at modern web browser" series (2018) still matches Chrome's current architecture in detail; I treat it as conceptually valid [memory].
- Intermediate steps of the certificate-lifetime schedule (200 and 100 days) and the exact end-of-life date of PostgreSQL 14 [memory].
- The APNIC "50% IPv6" figure was seen in search results only.
- Which TLS version the DNSimple HTTPS comic depicts; the completeness of the Chinese translation of "HTTP/3 explained".
- Exact release day of Python 3.15 (the fetched page summary said 9 October 2026).
- The learner's system language order and UTC offset: not assumed; ask the learner before relying on either.
- I did not review pedagogy research on analogies or notional machines; the analogy table is grounded in the mechanisms verified here, not in classroom trials.

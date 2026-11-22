# Security & privacy for a zero-to-full-stack learner — research brief (`web-security-2026`)

Researched 2026-11-19 on the reference Mac (plan G7) (macOS 27.2 arm64, Python 3.14.9, uv 0.13.5, ruff 0.17.2, Node 26.12.0 / npm 11.20.0, Apple Git 2.54.0).
Audience: lesson builders. Facts are in English; the analogy bank (section 12) is in Chinese.

Tags: **[local]** ran here today · **[source: URL]** read in a primary source today · **[secondary: URL]** non-primary page read today · **[memory]** not verified today · **[inferred]** my reasoning from verified facts.

## 0. What I verified and how

- Web: OWASP (Top 10:2025, ASVS 5.0, 14 cheat sheets), MDN, NIST, FastAPI docs, GitHub docs/changelog, PyPI blog, npm docs bundled with the local CLI, uv docs, pnpm docs, Let's Encrypt, official post-mortems (PyPI, LiteLLM, axios, TanStack, PostHog, Trivy, React), CISA alerts, CAC/gov.cn legal texts, Claude Code docs.
- Local labs (all under `lab/` next to this file; no ports opened, no Docker, nothing installed globally): in-process FastAPI `TestClient`, `sqlite3 :memory:`, throwaway git repos, throwaway npm/uv projects, one-shot Node scripts. Heavy dirs (`.venv`, `node_modules`) were deleted afterwards; scripts and lockfiles remain.
- Sandbox-only quirks (the learner's own terminal will not need these): `uvx` needed `UV_TOOL_DIR="$TMPDIR/uv-tools"`; `pip-audit` needed `--cache-dir`; Node printed `ERROR: failed to copy trust settings of system certificate` noise lines. [local]
- Could not reach: EUR-Lex full GDPR text (empty body), npc.gov.cn (TLS handshake failure), spp.gov.cn (403), GitHub REST API (rate limited). GDPR articles were read on gdpr-info.eu (a reproduction, not the official journal).

## 1. Headline findings (most decision-relevant)

1. **Current OWASP Top 10 is the 2025 edition** (8th installment). New: *A03 Software Supply Chain Failures* (expanded from "Vulnerable and Outdated Components"), *A10 Mishandling of Exceptional Conditions*; SSRF was folded into A01. A Simplified-Chinese translation is live at `https://top10.owasp.org/2025/zh-Hant/` (the URL says zh-Hant, the menu label and text are 简体中文). [source: https://top10.owasp.org/2025/0x00_2025-Introduction/] [local: curl of the zh page]
2. **ASVS 5.0.0** (30 May 2025) is the current verification standard; ~350 requirements, 17 chapters; Level 1 ≈ 20% of them and is designed as the low-barrier starting point; official Simplified-Chinese PDF exists. [source: https://asvs.owasp.org/ , https://asvs.owasp.org/downloads/ , https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md]
3. **Supply-chain security changed more in the last 12 months than anything else in this topic** (section 4). Twelve months of worms and account takeovers (Shai-Hulud, LiteLLM, axios, TanStack) produced new *defaults*: npm 12 blocks dependency install scripts, pnpm waits 1 day before installing new releases, Dependabot waits 3 days, uv/pip/npm all have "cooldown" settings, PyPI freezes releases after 14 days, npm classic tokens are gone.
4. **This Mac runs npm 11.20.0, where a dependency's `postinstall` still executes by default** (I watched it write a file); npm only prints a warning. npm 12 (registry `latest` = 12.2.3) blocks by default. Lessons must not assume either behaviour silently. [local]
5. **`git commit` fails when signing is half-configured**: if global config has `commit.gpgsign=true`, `gpg.format=openpgp`, `gpg.program=gpg`, empty `user.signingkey`, empty `gpg.ssh.program`, and no `gpg` binary exists, the error is `error: cannot run gpg: No such file or directory … fatal: failed to write commit object`. Stage 1 Git lessons will hit this on the first commit on such a Mac. [local]
6. **A workspace on an iCloud-synced Desktop is uploaded to iCloud** (file-provider xattr checked locally). Any `.env`, database file or key the learner creates there is uploaded too. Existing `.gitignore` files (project and global) often have no `.env` rule; check them before the first commit.
7. **Chinese mirrors silently weaken two supply-chain controls**: `npm audit` against `registry.npmmirror.com` fails with `[NOT_IMPLEMENTED] /-/npm/v1/security/* not implemented yet` (so installs show no vulnerability warning), and uv's cooldown fails on the Aliyun PyPI mirror (no `upload-time` metadata) but works on the Tsinghua TUNA mirror. [local]
8. **Old tutorials are wrong on many specifics**: passlib/bcrypt and python-jose (FastAPI docs now use `pwdlib[argon2]` + `PyJWT`), password complexity/rotation rules (NIST 2025 forbids them), `X-XSS-Protection`, JWT in `localStorage`, `npm install` being harmless, gitleaks as the go-to scanner (now maintenance-only), picoCTF (renamed), Mozilla TLS wiki (moved). See section 7.
9. **Everything a beginner needs can be demonstrated offline and in-process** — SQL injection, IDOR, cookie flags, CORS, CSRF guard, JWT forgery rejection, password hashing, secret-in-history, dependency audit all ran here in < 1 s each without a server. Auto-check scripts can therefore test security behaviour deterministically.
10. **Privacy law is absent from the roadmap** but China's PIPL (in force since 2021-11-01) and the Network Data Security Regulations (2025-01-01) apply to even a tiny product that stores an e-mail address of someone in China; awareness-level content fits in stages 5, 7 and 8.

## 2. Standards map (what to cite, in which edition)

| Document | Current edition (verified today) | Use in the course |
|---|---|---|
| OWASP Top 10 | **2025**: A01 Broken Access Control · A02 Security Misconfiguration · A03 Software Supply Chain Failures · A04 Cryptographic Failures · A05 Injection · A06 Insecure Design · A07 Authentication Failures · A08 Software or Data Integrity Failures · A09 Security Logging & Alerting Failures · A10 Mishandling of Exceptional Conditions. RC label removed from the repo on 2025-12-24. [source: https://top10.owasp.org/2025/ , https://github.com/OWASP/Top10/commits/master/2025/docs/en/index.md] | Awareness map; revisit in stage 7 against the learner's own app |
| OWASP ASVS | **5.0.0**, 2025-05-30. Chapters V1 Encoding & Sanitization, V2 Validation & Business Logic, V3 Web Frontend Security, V4 API & Web Service, V5 File Handling, V6 Authentication, V7 Session Management, V8 Authorization, V9 Self-contained Tokens, V10 OAuth & OIDC, V11 Cryptography, V12 Secure Communication, V13 Configuration, V14 Data Protection, V15 Secure Coding & Architecture, V16 Security Logging & Error Handling, V17 WebRTC. IDs are `chapter.section.requirement`; numbering is incompatible with 4.0.3. "Most applications should be striving to achieve" Level 2. | Capstone checklist = Level 1 + selected Level 2 |
| OWASP Cheat Sheet Series | Living documents; all pages below fetched today. Sheets in today's index that older course material will not mention: *Secure Coding with AI*, *AI Agent Security*, *LLM Prompt Injection Prevention*, *Software Supply Chain Security*, *GitHub Actions Security*, *CORS Security*, *Passkey Security*. There is an *NPM Security* sheet but no PyPI-specific one. I saw no Chinese edition (not checked exhaustively). [source: https://cheatsheetseries.owasp.org/index.html] | "How to" reference per topic |
| OWASP Top 10 Proactive Controls | Site navigation shows the 2024 edition plus a "Future Top 10 (WIP)" list: C1 Implement Access Control, C2 Use Cryptography to Protect Data, C3 Validate all Input & Handle Exceptions, C4 Address Security from the Start, C5 Secure By Default Configurations, C6 Keep your Components Secure, C7 Secure Digital Identities, C8 Leverage Browser Security Features, C9 Implement Security Logging and Monitoring, C10 Stop Server Side Request Forgery. [source: https://top10proactive.owasp.org/] | Optional developer-side framing ("what to do" rather than "what goes wrong") |
| OWASP API Security Top 10 | 2023 (API1 Broken Object Level Authorization …). [source: https://owasp.org/www-project-api-security/] | Stage 5 reference |
| OWASP Top 10 for LLM Apps / Agentic | LLM 2025 (LLM01 Prompt Injection … LLM10 Unbounded Consumption); *Top 10 for Agentic Applications for 2026* released 2025-12-09. [source: https://genai.owasp.org/llm-top-10/ , https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/] | AI-tutor safety module |
| NIST SP 800-63B-4 | Final, 2025-07-31. [source: https://csrc.nist.gov/pubs/sp/800/63/b/4/final] | Password policy facts |
| MDN Web Security | Attack guides (XSS, CSRF, IDOR, SSRF, clickjacking, supply chain, …), *Practical security implementation guides*, HTTP Observatory. zh-CN exists for HTTP guides (CORS, CSP, Cookies) but **not** for the attack guides (404). [source: https://developer.mozilla.org/en-US/docs/Web/Security/Attacks] [local: curl status codes] | First-read explanations in stage 4 |

## 3. Topic essentials (teach this, default to this)

### 3.1 Access control (A01) — the #1 risk, and the one frameworks do not solve
- Rules: deny by default; check on **every** request, server-side; check the **specific object** (ownership), not just "is logged in"; hiding or randomising IDs is not access control; write tests for it. [source: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html , https://top10.owasp.org/2025/A01_2025-Broken_Access_Control/]
- Verified demo (`lab/pyweb/03_fastapi_lab.py`): logged in as alice, `GET /notes-UNSAFE/2` → `200 {'owner': 'bob', …}`; fixed route → `404`; anonymous → `401`. Return the same 404 for "missing" and "not yours". [local]
- Teach as a habit: every data-returning query carries `WHERE owner_id = :current_user`; every PR adding an endpoint adds a "user A cannot touch user B's object" test.

### 3.2 Authentication and password storage (A07, A04)
- Password policy (NIST 800-63B-4 + OWASP): min **15** chars if password is the only factor, **8** if MFA; allow ≥ 64; **no composition rules, no periodic rotation**; block common/breached passwords; allow paste and password managers; never truncate; rate-limit failures. ASVS L1: 6.2.1 "at least 8 characters … 15 strongly recommended", 6.2.4 check against top-3000 list, 6.2.5 any composition, 6.2.7 paste/password managers permitted, 6.2.8 verify exactly as received. MFA is ASVS Level 2 (6.3.3). [source: https://pages.nist.gov/800-63-4/sp800-63b.html , https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html , https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x15-V6-Authentication.md]
- Storage: **Argon2id** first (minimum m=19 MiB, t=2, p=1), scrypt second, bcrypt only for legacy (cost ≥ 10, 72-byte input limit), PBKDF2-HMAC-SHA256 600,000 iterations only for FIPS. Unique salt per password (libraries do it). [source: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html]
- FastAPI's tutorial today: `uv add "pwdlib[argon2]"`, `uv add pyjwt`, `PasswordHash.recommended()`, a dummy-hash verify for unknown users to equalise timing, `openssl rand -hex 32` for the key, 30-minute tokens. The tutorial hard-codes the key in source — lessons must move it to configuration. [source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/]
- Verified here (`lab/pyweb/02_passwords.py`), argon2-cffi 25.1.0 / pwdlib 0.4.2 defaults = `m=65536,t=3,p=4` (above OWASP minimum), ~25 ms per hash on this Mac: [local]
  ```
  argon2 hash #1 : $argon2id$v=19$m=65536,t=3,p=4$SDV1kumnKIeIMhteZleqsw$nFuVGP1D…
  argon2 hash #2 : $argon2id$v=19$m=65536,t=3,p=4$pGJbw3l/u0Z8sJ4PWdgowg$NMn66WVJ…  (same password, random salt)
  pwdlib verify  : True False
  ```
- Error messages: identical generic text for wrong user / wrong password / locked ("Invalid username or password"); same for registration and reset. [source: Authentication cheat sheet]
- Breached-password check without sending the password: `GET https://api.pwnedpasswords.com/range/5BAA6` returned `1E4C9B93F3F0682250B6CF8331B7EE68FD8:52373976` for `password` (only the first 5 hex chars of the SHA-1 left the machine). [local]
- Postpone: OAuth/OIDC internals, passkey/WebAuthn implementation, SAML. Teach *using* "Sign in with …" as OIDC consumers only after the learner has built session auth once.

### 3.3 Sessions, cookies, tokens (A07)
- Session ID: ≥ 64 bits entropy from a CSPRNG (`secrets.token_urlsafe(32)` = 256 bits); regenerate on login; invalidate server-side on logout; idle timeout 15–30 min for low-risk apps. [source: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html]
- Cookie recipe: `__Host-session=<random>; HttpOnly; Secure; SameSite=Lax (or Strict); Path=/` and **no Domain**. `__Host-` requires Secure + no Domain + Path=/. MDN now also documents `__Http-` and `__Host-Http-` prefixes. `Secure` cookies work on `localhost` over http. [source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie]
- "Do not store authentication tokens, session IDs, JWTs, refresh tokens, or any credential in localStorage or sessionStorage." (OWASP) → HttpOnly cookie or backend-for-frontend.
- Starlette 1.10 defaults are **not** secure-by-default: `set_cookie(..., secure=False, httponly=False, samesite='lax')`; `SessionMiddleware(https_only=False, max_age=1209600)`. Verified output of the recipe: `Set-Cookie: __Host-session=<random>; HttpOnly; Max-Age=1800; Path=/; SameSite=lax; Secure`. [local]
- JWT facts to demonstrate (PyJWT 2.15.1, `lab/pyweb/04_misc.py`): payload is readable by anyone (Base64, not encryption); `alg=none` forgery → `InvalidAlgorithmError`; tampered payload → `InvalidSignatureError`; expired → `ExpiredSignatureError`; omitting `algorithms=` raises; a 5-byte HMAC key only triggers `InsecureKeyLengthWarning` (minimum 32 bytes for HS256). [local]
- Default for the capstone: server-side session in an HttpOnly cookie. Teach JWT as "how to read and verify one", not as the default session mechanism.

### 3.4 Input validation, output encoding, XSS (A05)
- Validation = allow-list of what is acceptable (type, length, range, format), on the server, even if the browser also checks. It is **not** the defence against SQL injection or XSS — parameterised queries and context-aware output encoding are. [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html]
- Pydantic/FastAPI gives this for free: bad body → `422 String should have at least 8 characters` / `string_pattern_mismatch`. [local]
- XSS: rely on framework auto-escaping; know the escape hatches; sanitise user-authored HTML with DOMPurify; prefer `textContent` over `innerHTML`; CSP and cookie flags are second layers, not the fix. "an application that protects 99 places and misses one is still vulnerable". [source: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html]
- Verified: [local]
  ```
  jinja2 default (Environment())  : <p>Hello <img src=x onerror=alert(1)></p>      ← autoescape is OFF by default
  jinja2 autoescape               : <p>Hello &lt;img src=x onerror=alert(1)&gt;</p>
  Starlette Jinja2Templates       : autoescape True for .html, False for .txt
  React 19.3.1 {payload}          : <p>&lt;img src=x onerror=alert(1)&gt;</p>
  dangerouslySetInnerHTML         : <p><img src=x onerror=alert(1)></p>
  href="javascript:…" in React    : replaced by "javascript:throw new Error('React has blocked a javascript: URL…')"
  DOMPurify 3.4.18 sanitize       : <img src="x"><b>bold</b><a>x</a>
  ```
- The browser Sanitizer API (`Element.setHTML()`) is still "limited availability", not Baseline → keep recommending DOMPurify. [source: https://developer.mozilla.org/en-US/docs/Web/API/Element/setHTML]

### 3.5 SQL injection (A05)
- Primary defence: parameterised queries. Identifiers (table/column/`ORDER BY`) cannot be bound → map user choice to a fixed allow-list. Manual escaping is "strongly discouraged". ORMs can still be injected through raw fragments. Hardening: least-privilege DB account. [source: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html]
- Verified with stdlib only (`lab/pyweb/01_sqli.py`): [local]
  ```
  SQL sent: SELECT name, secret FROM users WHERE name = 'nobody' OR '1'='1'
  UNSAFE attack : [('alice', 'alice-diary'), ('bob', 'bob-diary')]
  SAFE   attack : []          # con.execute("… WHERE name = ?", (name,))
  ```
- ruff rule `S608` flags the f-string version (section 4.4).

### 3.6 CSRF
- Only matters when the browser attaches credentials automatically (cookies). Current guidance: use the framework's protection if it has one; otherwise synchronizer/signed double-submit token **or** Fetch Metadata (`Sec-Fetch-Site`) with an Origin-header fallback; never change state on GET; `SameSite` is defence in depth, not the fix (same-*site* ≠ same-*origin*: sibling subdomains count as same site). OWASP and MDN both now list Fetch Metadata as a primary option. ASVS L1 3.5.1–3.5.3. [source: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html , https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/CSRF]
- FastAPI/Starlette ship **no** CSRF middleware (Starlette 1.10 middlewares: authentication, body_limit, cors, gzip, httpsredirect, sessions, trustedhost, …). [local] A 20-line guard works (`lab/pyweb/05_csrf_fetch_metadata.py`): same-origin → 200; `Sec-Fetch-Site: cross-site` → 403; old browser + allowed Origin → 200; evil Origin → 403; cookie but no Origin/Sec-Fetch → 403. [local]

### 3.7 CORS
- CORS *relaxes* the same-origin policy; the **browser** enforces it; the request usually still reaches the server; it is not authentication and not CSRF protection. `Access-Control-Allow-Origin: *` cannot be combined with credentials; when echoing an allow-listed origin also send `Vary: Origin`. [source: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS]
- Starlette `CORSMiddleware` defaults allow nothing (`allow_origins=()`, methods `('GET',)`, credentials `False`). Verified: allowed origin preflight → 200 with `access-control-allow-origin: https://app.example.com` + `access-control-allow-credentials: true` + `vary: Origin…`; other origin → `400 Disallowed CORS origin`; a plain cross-origin GET still executed on the server (401 from our auth, no ACAO header). [local]
- Simplest safe default for the capstone: serve SPA and API from the **same origin** (reverse proxy / Vite dev proxy) so CORS is not needed at all.

### 3.8 Security headers and CSP (A02)
- Baseline set (OWASP HTTP Headers cheat sheet): `Strict-Transport-Security: max-age=63072000; includeSubDomains` (add `preload` only deliberately), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy` (with `frame-ancestors`, which supersedes `X-Frame-Options`), `Permissions-Policy: geolocation=(), camera=(), microphone=()`, `Cross-Origin-Opener-Policy: same-origin`; remove `X-Powered-By`/`Server` details. **Do not use** `X-XSS-Protection` (set `0` or omit), `Expect-CT`, `Public-Key-Pins`, `Feature-Policy`. [source: https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html]
- CSP starter when everything is same-origin and there are no inline scripts: `default-src 'self'; frame-ancestors 'self'; form-action 'self';`. Strict (nonce) CSP: `script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none';`. Roll out with `Content-Security-Policy-Report-Only` first. [source: https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html]
- ASVS L1 only requires HSTS (3.4.1, ≥ 1 year) and a fixed/allow-listed CORS origin (3.4.2); CSP, nosniff, Referrer-Policy, frame-ancestors are L2. [source: https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md]
- Real-world reading exercise, verified: `curl -sI https://github.com` shows `strict-transport-security: max-age=31536000; includeSubdomains; preload`, `x-frame-options: deny`, `x-content-type-options: nosniff`, `x-xss-protection: 0`, `content-security-policy: default-src 'none'; …`, cookies with `HttpOnly; secure; SameSite=Lax`. Deployed sites can be graded with MDN HTTP Observatory. [local]

### 3.9 HTTPS / TLS (A04)
- Teach: TLS gives confidentiality + integrity + server identity; certificates expire and must be renewed automatically; HTTP must redirect to HTTPS; HSTS makes the browser refuse HTTP next time.
- Verified: `curl -sv https://github.com` → `SSL connection using TLSv1.3`, cert `start date: Oct 30 2026`, `expire date: Jan 27 2027` (≈ 90 days); `curl -sI http://github.com` → `301 … location: https://github.com/`. [local]
- Lifetimes are shrinking, so manual renewal is no longer viable: Let's Encrypt default profile goes 90 → **64 days on 2027-02-10** → **45 days on 2028-02-16** (a 6-day `shortlived` profile exists). [source: https://letsencrypt.org/2025/12/02/from-90-to-45] Industry maximum: 200 days since 2026-03-15, 100 days from 2027-03-15, 47 days from 2029-03-15 (CA/B Forum ballot SC-081v3). [secondary: several CA blogs]
- Mozilla's Server Side TLS wiki now redirects to a community project, `https://docs.tlsref.org/` (Modern/Intermediate profiles). [source: https://wiki.mozilla.org/Security/Server_Side_TLS]
- Default for the course: let the platform or Caddy terminate TLS automatically; never hand-configure cipher suites as a beginner.

### 3.10 SSRF (now inside A01)
- Appears the moment the server fetches a user-supplied URL (link previews, webhooks, "import from URL"). Prefer an allow-list of hosts and build the request yourself; otherwise resolve, classify the IP, connect only to the validated address, disable redirects, allow only http/https. Deny-lists are "bypass-prone". [source: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html]
- Verified with stdlib `ipaddress`: `127.0.0.1`, `10.0.0.5`, `169.254.169.254` (cloud metadata), `::1`, `::ffff:127.0.0.1`, `fd00::1` all report `is_global=False`; `urlsplit('http://example.com@127.0.0.1:8000/admin').hostname` → `127.0.0.1` (the "@" trick). [local]

### 3.11 Secrets management
- Order of preference: secret manager > platform/CI secret store > environment variables / untracked `.env` (OWASP calls env vars a last resort because they leak into logs and child processes) > **never** source code, Docker `ENV`/`ARG`, or URLs. On leak: **revoke/rotate first**, then clean up; deleting the commit is not enough. [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html , https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/remediating-a-leaked-secret]
- Verified git demo (`lab/gitleak/`): after `git rm --cached .env` + `.gitignore` + new commit, `git ls-files` no longer lists `.env`, yet `git show <first-commit>:.env` still prints `SECRET_KEY=FAKE0123456789abcdef` and `git log --all -S"FAKE0123…"` finds two commits. [local]
  ```
  # .gitignore lines used
  .env
  .env.*
  !.env.example
  ```
- GitHub: push protection is on by default for personal accounts pushing to **public** repos; secret scanning, push protection, CodeQL and dependency review are free on public repos, paid (Secret Protection / Code Security) on private ones; Dependabot alerts/updates are free everywhere. [source: https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection , https://docs.github.com/en/code-security/getting-started/github-security-features]
- Local scanners: `uvx detect-secrets scan --no-verify <files>` works offline (27 plugins; found `Stripe Access Key`, `GitHub Token`, `Basic Auth Credentials`). Without `--no-verify` it **calls provider APIs** to validate findings (the sandbox blocked a request to api.stripe.com). It missed a generic `SECRET_KEY=FAKE…` line and ruff/bandit missed `API_KEY = "sk_live_…"` → scanners are a net, not a guarantee. [local] gitleaks (`brew install gitleaks`; commands `gitleaks git` / `gitleaks dir`; `detect`/`protect` deprecated since 8.19.0) is now "feature complete… not merging new features"; its author moved to **Betterleaks** (2026). [source: https://github.com/gitleaks/gitleaks] [secondary: helpnetsecurity 2026-03-19]
- Front-end caveat to state explicitly: anything shipped to the browser is public; build-time variables exposed to client code (e.g. Vite `VITE_*`) are not secrets. [memory]

### 3.12 Least privilege (cross-cutting)
- People/accounts: 2FA or passkeys on GitHub, e-mail, registrar, cloud; fine-grained, expiring tokens instead of "all repos" tokens. [memory]
- CI: read-only `GITHUB_TOKEN` by default, per-job grants, secrets only where needed; avoid `pull_request_target`; "Workflows that use these triggers must not explicitly check out untrusted code." [source: https://docs.github.com/en/actions/reference/security/secure-use]
- Database: the app connects as a role that is not the owner/superuser; PostgreSQL 15+ no longer lets every role create objects in `public` by default (docs for PostgreSQL 18 call the private-schema pattern secure by default since 15). [source: https://www.postgresql.org/docs/current/ddl-schemas.html]
- Containers: non-root `USER`, no Docker socket, drop capabilities, read-only filesystem, no secrets in images. [source: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html]
- AI assistant: section 6.

### 3.13 Logging, alerting, error handling (A09, A10)
- Log: authn successes/failures, authz failures, validation failures, admin actions, errors — with when/where/who/what and a request ID. **Never log**: passwords, session IDs, access tokens, connection strings, keys, payment data, sensitive personal data; mask or hash instead. Neutralise CR/LF (log injection); prefer structured (JSON) logs. Logs need alerting to be useful. [source: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html]
- Verified stdlib `logging.Filter` demo: input `email=li.lei@example.com password=hunter2 phone=13800138000` → `email=[EMAIL] password=[REDACTED] phone=[PHONE]`; an injected newline came out as literal `\n`. [local, `lab/pyweb/04_misc.py`]
- A10: catch errors where they occur, have a global handler, **fail closed**, roll back the whole transaction, never show stack traces or SQL to users. [source: https://top10.owasp.org/2025/A10_2025-Mishandling_of_Exceptional_Conditions/]

### 3.14 Light-weight threat modelling (A06)
- Four questions (Threat Modeling Manifesto): *What are we working on? What can go wrong? What are we going to do about it? Did we do a good enough job?* Draw a data-flow sketch with trust boundaries; prompt with STRIDE (Spoofing→authentication, Tampering→integrity, Repudiation→accounting, Information disclosure→confidentiality, Denial of service→availability, Elevation of privilege→authorization); answer each threat with mitigate / eliminate / transfer / accept. [source: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html]
- Course form: a one-page `THREAT_MODEL.md` template (assets, actors, entry points, 5–10 threats, decision per threat), first filled in stage 5, revised in 7 and 10. LINDDUN is the named method for privacy threats (mention only).

## 4. Dependency and supply-chain security (A03) — PyPI and npm

### 4.1 Teaching cases with primary sources
| When | What happened | Root cause → lesson | Source |
|---|---|---|---|
| 2024-03-29 | xz 5.6.0/5.6.1 backdoor (CVE-2024-3094) aimed at sshd; malicious code in release tarballs, not plain in git | patient social engineering of a maintainer → "many eyes" is not automatic; found by one engineer noticing slow logins | [source: https://www.openwall.com/lists/oss-security/2024/03/29/4] |
| 2024-06-25 | polyfill.io domain sold; script served to ~4% of websites started injecting redirects | third-party `<script src>` you do not control → self-host or use SRI | [source: https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/] |
| 2024-12 | ultralytics 8.3.41/42/45/46 on PyPI | GitHub Actions workflow + cache compromise, then an old unrevoked API token → trusted publishing, revoke unused tokens, audit workflows (zizmor) | [source: https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/] |
| 2025-03-12..15 | `tj-actions/changed-files` (CVE-2025-30066) leaked CI secrets into logs | mutable action tags were repointed → pin actions to commit SHAs / lockfile | [source: https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction] |
| 2025-09-08 | `debug@4.4.2` (and other very popular packages) shipped a browser crypto-wallet address swapper | maintainer account takeover (phishing [memory]) → phishing-resistant 2FA; lockfiles limited the blast radius | [source: https://github.com/advisories/GHSA-8mgj-vmr8-frr6] |
| 2025-09-14 | Shai-Hulud worm: 500+ npm packages; stole tokens, republished itself via post-install scripts | install scripts + long-lived tokens → npm token overhaul (4.2) | [source: https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/ , https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem] |
| 2025-11-24 | Shai-Hulud 2.0 (PostHog SDKs among the entry points) | a `pull_request_target` workflow ran PR code and leaked an over-privileged bot token; `preinstall` worm → fix was trusted publishing, workflow review, pnpm with scripts off + `minimumReleaseAge` | [source: https://posthog.com/blog/nov-24-shai-hulud-attack-post-mortem] |
| 2025-12-03 | "React2Shell" CVE-2025-55182, CVSS 10.0, unauthenticated RCE in React Server Components 19.0–19.2.0 (Next.js etc.); client-only React apps not affected | framework bug → patch quickly, know what you run | [source: https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components] |
| 2026-03-19 → 24 | Trivy release + 76 of 77 `trivy-action` tags replaced (CVE-2026-33634); stolen CI secrets used to publish **litellm 1.82.7/1.82.8** and telnyx to PyPI; 1.82.8 carried a `.pth` file that runs on every Python start; PyPI counts 119k+ downloads of the bad litellm versions and 2 h 32 min from upload to quarantine (LiteLLM's own post says "about 40 minutes") | a security scanner in CI became the attack path; ~40–50% of installs were unpinned → pin, lock with hashes, cooldown | [source: https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23 , https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/ , https://docs.litellm.ai/blog/security-update-march-2026] |
| 2026-03-31 | `axios@1.14.1` / `0.30.4` live ~3 h (00:21–03:15 UTC), added dependency `plain-crypto-js` whose postinstall installed a RAT | lead maintainer's PC compromised by targeted social engineering (he had 2FA) → cooldown + no install scripts would have protected consumers | [source: https://github.com/axios/axios/issues/10636] |
| 2026-05-11 | TanStack: 84 malicious versions of 42 packages in 6 minutes; **no npm token stolen** | `pull_request_target` + Actions cache poisoning + OIDC token pulled from runner memory → trusted publishing is not a silver bullet; detected publicly in ~20 min, so a 1-day cooldown suffices | [source: https://tanstack.com/blog/npm-supply-chain-compromise-postmortem] |

Pattern for the learner: (1) attackers go after maintainers and CI, not your code; (2) bad versions are usually removed within hours → **waiting a few days before adopting new releases is the cheapest strong defence**; (3) code runs at *install* time, not only at import time.

### 4.2 What the ecosystems changed (all verified today)
- **npm**: classic tokens permanently revoked 2025-12-09; `npm login` gives a 2-hour session; write tokens ≤ 90 days; trusted publishing (OIDC) recommended; staged publishing with human 2FA approval GA 2026-05-22. [source: https://github.blog/changelog/2025-12-09-npm-classic-tokens-revoked-session-based-auth-and-cli-token-management-now-available/ , https://github.blog/changelog/2026-05-22-staged-publishing-and-new-install-time-controls-for-npm/]
- **npm 12** (12.0.0 published 2026-07-08; `latest` = 12.2.3 today [local: `npm view npm time/dist-tags`]): dependency `preinstall/install/postinstall` scripts and implicit node-gyp builds do not run unless listed in `allowScripts`; `--allow-git` and `--allow-remote` default to `none`. [source: https://github.blog/changelog/2026-06-09-upcoming-breaking-changes-for-npm-v12/ , https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/]
- **pnpm**: build scripts blocked unless in `allowBuilds` (`strictDepBuilds` on), `minimumReleaseAge` defaults to 1440 minutes, `blockExoticSubdeps` on. Not installed on this Mac. [source: https://pnpm.io/supply-chain-security]
- **uv**: `exclude-newer` accepts durations (`"7 days"`, `"P7D"`), per-package overrides; `uv audit` (OSV-backed) and `UV_MALWARE_CHECK=1` announced 2026-06-08, both still preview/experimental in 0.13.5. [source: https://docs.astral.sh/uv/concepts/resolution/ , https://astral.sh/blog/uv-audit] [local]
- **pip**: `--uploaded-prior-to` (26.0+, relative durations planned for 26.1). "`pip freeze` doesn't create a lock file: a lock file must include checksums". [source: PyPI incident report 2026-04-02]
- **PyPI**: rejects new files on releases older than 14 days (merged 2026-07-08); quarantine + "Report project as malware"; 50,000+ projects on trusted publishing, 52% of active users with non-phishable 2FA (end of 2025). [source: https://blog.pypi.org/posts/2026-07-22-releases-now-reject-new-files-after-14-days/ , https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review/]
- **Dependabot**: `cooldown` option; default 3 days for version updates when unset; does not delay security updates. [source: https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference]
- **GitHub Actions**: docs now say the best measure is a workflow dependency lockfile, `.github/workflows/actions.lock`, generated by `gh actions-lock`, which "supersedes SHA pinning for repositories that adopt it"; SHA pinning remains the fallback. [source: https://docs.github.com/en/actions/reference/security/secure-use , https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles]

### 4.3 Python commands verified here
```
# pyproject.toml of the project
[tool.uv]
exclude-newer = "7 days"
```
- `uv add httpx` then wrote into `uv.lock`: `exclude-newer-span = "P7D"`; the lock contains `sha256:` hashes for every file; `uv sync --locked` fails if lock and manifest disagree; `uv export --format requirements.txt` emits `--hash=sha256:…` lines. [local, `lab/pycool/`]
- `uv audit` on a project pinned to `jinja2==3.1.2`, `requests==2.31.0` (`lab/pyvuln/`): [local]
  ```
  warning: `uv audit` is experimental and may change without warning. Pass `--preview-features audit-command` to disable this warning.
  Found 16 known vulnerabilities and no adverse project statuses in 7 packages
  jinja2 3.1.2 has 10 known vulnerabilities:
  - PYSEC-2026-1474: Jinja vulnerable to HTML attribute injection when passing user input as keys to xmlattr filter
    Fixed in: 3.1.4
  ```
  exit code 1; after `uv add "jinja2>=3.1.6" "requests>=2.33"` → `Found no known vulnerabilities and no adverse project statuses in 7 packages`, exit code 0. Both uv audit and pip-audit printed every advisory twice (5 distinct jinja2 IDs shown as 10 rows) — checkers should assert on the exit code or on package names, never on the count.
- Stable alternative: `uv export --format requirements.txt --no-hashes -o req.txt && uvx pip-audit -r req.txt --no-deps --disable-pip` (pip-audit 2.10.1) → `Found 16 known vulnerabilities in 2 packages`, exit 1. [local]
- `UV_MALWARE_CHECK=1 uv sync` runs and prints `warning: Malware checks are experimental…`. [local]
- Mirrors: with `--default-index https://pypi.tuna.tsinghua.edu.cn/simple` the cooldown resolved fine; with `https://mirrors.aliyun.com/pypi/simple` → `warning: … is missing an upload date` and `No solution found`. [local]

### 4.4 Static checks verified here
- `ruff check --select S` on `lab/sast/bad.py` reported 11 findings: `S105` hard-coded password, `S608` SQL string building, `S602` `shell=True`, `S311` `random` for security, `S324` md5, `S301` pickle, `S506` unsafe yaml load, `S113` request without timeout, `S501` `verify=False`, `S101` assert, `S307` eval. bandit 1.9.4 (`uvx bandit -q bad.py`) reported 13. Working config: [local]
  ```
  [tool.ruff.lint]
  extend-select = ["S"]
  [tool.ruff.lint.per-file-ignores]
  "tests/**" = ["S101"]
  ```
- `uvx zizmor --offline .` (1.32.0) on a deliberately bad workflow (`lab/gha/`): `error[dangerous-triggers]`, `error[template-injection]`, `error[unpinned-uses]` ×2, `warning[artipacked]`, `warning[excessive-permissions]`. [local]

### 4.5 npm commands verified here (npm 11.20.0)
- Default install of a tarball dependency with a `postinstall` (`lab/evilpkg`, `lab/npmlab`): the script **ran** (marker file created) and npm printed: [local]
  ```
  npm warn install-scripts 2 packages have install scripts not yet covered by allowScripts:
  npm warn install-scripts   esbuild@0.28.2 (postinstall: node install.js)
  npm warn install-scripts Run `npm install-scripts ls` to review, or `npm install-scripts approve <pkg>` to allow.
  ```
- `npm ci --ignore-scripts` → marker not created. `npm ci --strict-allow-scripts` → `npm error code ESTRICTALLOWSCRIPTS`. After `npm install-scripts approve esbuild` / `npm install-scripts deny <pkg>`, `package.json` gained `"allowScripts": {"esbuild@0.28.2": true, "<denied spec>": false}` and the strict install succeeded with esbuild working and the denied script skipped. [local]
- Project `.npmrc` that reproduces npm-12-like safety on npm 11.20: [local]
  ```
  min-release-age=7
  strict-allow-scripts=true
  ```
  `min-release-age` (days, default null) errors with `ENOVERSIONS` if nothing is old enough; `min-release-age-exclude[]=` exempts packages.
- `npm audit` on `lodash@4.17.20` → `1 high severity vulnerability`, 4 advisories (GHSA links), exit 1; `npm audit fix` → lodash 4.18.1, `found 0 vulnerabilities`. `npm audit signatures` → `3 packages have verified registry signatures / 2 packages have verified attestations`. [local]
- `npm install … --registry=https://registry.npmmirror.com` installs, but `npm audit` on that registry fails (`[NOT_IMPLEMENTED] /-/npm/v1/security/* not implemented yet`); `npm audit --registry=https://registry.npmjs.org` works on the same lockfile. [local]
- Inconsistency to know: the docs bundled with 11.20.0 contain both "install scripts still run by default … A future release will block" (`npm-approve-scripts.md`) and "Dependency install scripts are blocked by default" (`npm-install-scripts.md`); observed behaviour is the former. [local]

## 5. Privacy regulation awareness — "what a small product must not do"

Not legal advice; awareness level only. PIPL quotes are from the CAC copy of the law; GDPR from gdpr-info.eu.

| Do not… | PIPL (China, in force 2021-11-01) | GDPR (EU) |
|---|---|---|
| collect more than the feature needs | Art. 6 "不得过度收集个人信息" | Art. 5(1)(c) data minimisation |
| process without a legal basis; bundle or force consent; refuse service because a user declines non-essential data | Art. 13 (seven bases), 14, 15, 16 | Art. 6(1)(a)–(f), Art. 7 |
| hide what you do | Art. 7, 17; Regulations Art. 21 (rules must be "集中公开展示、易于访问并置于醒目位置") | Art. 5(1)(a) transparency |
| keep data forever | Art. 47 (delete when purpose achieved / consent withdrawn / account closed) | Art. 5(1)(e) storage limitation |
| ignore access / copy / correction / deletion requests | Art. 44–47; Regulations Art. 23 ("及时受理… 不得设置不合理条件") | Art. 12–22 rights |
| treat sensitive data like ordinary data | Art. 28–29 (biometrics, health, financial accounts, location, **anyone under 14**) need separate consent; Art. 31 guardian consent | Art. 9 special categories; Art. 8 children [memory: age 16, states may lower to 13] |
| send personal data abroad casually (includes overseas SaaS, analytics, LLM APIs) | Art. 38–39: a legal mechanism **and** separate consent | Chapter V transfers |
| store it unprotected | Art. 51 (encryption, de-identification, access control, incident plan) | Art. 32 |
| hide a breach | Art. 57 notify authority and individuals "立即"; Regulations Art. 10: within 24 hours where national security/public interest is at stake | Art. 33: authority within 72 hours where feasible |
| use profiling without an opt-out | Art. 24 (non-personalised option, no unreasonable differential pricing) | Art. 22 [memory] |

- Penalties: PIPL Art. 66 up to RMB 50 million or 5% of last year's turnover; GDPR Art. 83(5) up to EUR 20 million or 4% of worldwide turnover. [source: https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm , https://gdpr-info.eu/art-83-gdpr/ , https://gdpr-info.eu/art-33-gdpr/ , https://gdpr-info.eu/art-5-gdpr/ , https://gdpr-info.eu/art-6-gdpr/]
- Network Data Security Management Regulations (国令第790号), effective 2025-01-01: privacy-notice content, no repeated consent nagging after refusal, data-portability path, complaint channel; extra duties above 10 million individuals. [source: https://www.gov.cn/zhengce/content/202409/content_6977766.htm]
- Compliance-audit measures effective 2025-05-01: > 10 million individuals → audit at least every two years; ≥ 1 million → designate a personal-information protection officer. A hobby project is far below both thresholds. [source: https://www.cac.gov.cn/2025-02/14/c_1741233507681519.htm]
- Cybersecurity Law amended 2025-10-28, effective 2026-01-01: adds an AI article, raises fines (up to RMB 10 million for the gravest infrastructure cases), ties personal-information handling to the Civil Code and PIPL, renumbers articles. [source: https://www.ncsti.gov.cn/zcfg/flfg/202510/t20251029_223557.html , https://www.news.cn/politics/20251028/b3400522666a4b3f8c844b9fa6c31131/c.html]
- EU "Digital Omnibus": the AI part was adopted in July 2026; the GDPR/ePrivacy part is still in negotiation (Council mandate 2026-10-21) — teach GDPR as it stands. [secondary: law-firm summaries via search]
- Engineering translation for lessons: a data inventory table (field, purpose, legal basis, retention, who can read it) in the handbook; `DELETE /me` and `GET /me/export` endpoints in the capstone; no personal data in URLs, logs, analytics or AI prompts; fake data in fixtures.
- Hosting in mainland China additionally involves ICP filing (备案) and, for some services, MLPS (等保) and real-name rules. [memory]

## 6. Security when an AI assistant writes or runs the code

- OWASP *Secure Coding with AI* cheat sheet: verify every AI-suggested package exists and is reputable before installing (hallucinated names get registered by attackers — "slopsquatting"); treat repo content, issues, READMEs and web pages as untrusted input to the agent (indirect prompt injection); treat rules files (`CLAUDE.md`) as security-critical; "`.gitignore` only affects git -- AI tools read from the filesystem directly"; "A passing test suite generated by the same agent that produced the code provides no independent assurance"; a human owns every change. [source: https://cheatsheetseries.owasp.org/cheatsheets/Secure_Coding_with_AI_Cheat_Sheet.html]
- Claude Code: "You're responsible for reviewing proposed code and commands for safety before approval"; the docs describe Auto mode (a classifier model reviews actions instead of the user) as the built-in starting permission mode for interactive terminal and VS Code sessions, and Manual mode as read-only until the user approves; Bash sandboxing via `/sandbox`; `/security-review` command and a security-guidance plugin exist; credentials are stored in the macOS Keychain. Documented way to keep it away from secrets (project `.claude/settings.json`, strict JSON, no comments): [source: https://code.claude.com/docs/en/security , https://code.claude.com/docs/en/settings.md]
  ```json
  { "permissions": { "deny": ["Read(./.env)", "Read(./.env.*)"] } }
  ```
- Tutor configuration consequences: (a) the coach must not paste or request real secrets, and should refuse to read `.env`; (b) for security exercises the learner writes the fix and the test — the tutor explains and reviews; (c) the tutor names the package registry page to check before any `uv add` / `npm install` of an unfamiliar name; (d) `/security-review` is a stage 7 learning aid, not a replacement for the checklist.

## 7. What changed compared with older tutorials

| Older tutorials say | Today |
|---|---|
| OWASP Top 10 2021/2017; "A03 Injection", "A10 SSRF" | Top 10:2025; Injection is A05, SSRF is inside A01, supply chain is A03 |
| ASVS 4.0.3 numbering (V2 Authentication, V3 Session…) | ASVS 5.0.0 renumbered (V6 Authentication, V7 Session Management…) |
| Passwords: 8+ chars with upper/lower/digit/symbol, change every 90 days, security questions | NIST 800-63B-4 (2025): length-based, no composition rules, no periodic change, no security questions, blocklist, allow paste |
| bcrypt via `passlib`; JWT via `python-jose` | FastAPI docs: `pwdlib[argon2]` (Argon2id) + `PyJWT` |
| "Store the JWT in localStorage" | OWASP: never; HttpOnly cookie or BFF |
| `X-XSS-Protection: 1; mode=block`, `X-Frame-Options` only, `Feature-Policy`, HPKP, Expect-CT | `X-XSS-Protection: 0`/omit; CSP `frame-ancestors`; `Permissions-Policy`; HPKP and Expect-CT are dead |
| CSRF = hidden token only | Token **or** Fetch Metadata + Origin fallback; SameSite as extra layer |
| CSP = allow-list of CDNs | Strict CSP with nonce/hash + `'strict-dynamic'` |
| `npm install` is safe; `npm audit` is "the" control; long-lived npm tokens | Install scripts are the main worm vector; npm 12 blocks them; cooldown + `npm ci`; classic tokens revoked |
| `pip install -r requirements.txt` from `pip freeze` | Lockfile with hashes (`uv.lock`), cooldown, `uv audit`/pip-audit |
| "Pin GitHub Actions to a tag like `@v4`" | SHA pin or `actions.lock`; avoid `pull_request_target` |
| gitleaks `detect` / `protect` | `gitleaks git` / `gitleaks dir`; project in maintenance, successor Betterleaks; GitHub push protection on by default for public pushes |
| 90-day certificates, renew by hand or cron every 60 days | 64 days (2027) → 45 days (2028) at Let's Encrypt; automate with ARI-aware clients |
| Mozilla SSL config wiki | moved to `docs.tlsref.org` |
| picoCTF / picoGym | renamed **CyLab Security Academy** (`https://cylabacademy.org`); old accounts created before 2026-05-08 still work [source: https://picoctf.org/] |
| `from fastapi.testclient import TestClient` needs `httpx` | Starlette 1.10 prints `Using httpx with starlette.testclient is deprecated; install httpx2 instead`; `uv add httpx2` (2.16.2) silences it [local] |

## 8. Pitfalls a beginner will hit

1. Committing `.env` (or pasting a key into a prompt, issue or screenshot), then "fixing" it with a new commit. History keeps it; rotate first.
2. Believing CORS protects the server, or "fixing" a CORS error with `*` plus credentials.
3. Confusing authentication with authorization: "logged in" ≠ "allowed to see this row" (IDOR).
4. Trusting the browser: hidden fields, disabled buttons, client-side validation, `VITE_*` values.
5. Building SQL or shell commands with f-strings.
6. Thinking Base64/JWT payloads are encrypted; putting personal data in a JWT.
7. Using `random` for tokens, MD5/SHA-256 for passwords, or inventing crypto.
8. Turning protections off to make an error disappear: `verify=False`, `--ignore-scripts` forgotten vs. `--dangerously-allow-all-scripts`, `autoescape=False`, `|safe`, `dangerouslySetInnerHTML`, `chmod 777`, `sudo`.
9. Assuming a green `npm audit`/`uv audit` means "safe" (they list *known* vulnerabilities, not fresh malware) — and not noticing audit is silently broken behind npmmirror.
10. Installing a package because the AI named it, without opening its registry page.
11. Logging whole request bodies or user objects; returning stack traces to the client.
12. Testing "attacks" against real websites. Legal line in section 11.
13. Running Juice Shop or any vulnerable app bound to `0.0.0.0` on café Wi-Fi (use `127.0.0.1:3000`).
14. Machine-specific: first `git commit` fails with the gpg error when signing is half-configured (headline finding 5); `uvx detect-secrets` phones provider APIs unless `--no-verify`.
15. Treating security as a final stage instead of a property of every commit.

## 9. Staged plan: what to teach when

| Stage | Security/privacy content (smallest useful dose) | Hands-on, auto-checkable |
|---|---|---|
| 0 Orientation | Mindset: untrusted input, least privilege, defence in depth. Personal hygiene: password manager, 2FA/passkey on GitHub + e-mail, updates, phishing (axios maintainer story in two sentences). Rules for the AI tutor: read before approving; never paste secrets. Legal line: only attack your own lab. | Quiz; checklist in handbook |
| 1 Foundations | Terminal: what `sudo`, piping a downloaded script straight into `sh`, and file permissions mean. Git: `.gitignore` before first commit, `git status` before `git add`, history is permanent, public vs private repo, `.env` + `.env.example`. GitHub: 2FA, SSH key with passphrase, push protection. Fix/explain the gpgsign config. Asking for help without leaking tokens or personal data. Move workspace off iCloud Desktop. | Script checks: `.env` ignored (`git check-ignore -v .env`), fake secret absent from `git log -p`, "find the leaked FAKE key in history" exercise |
| 2 Python fundamentals | `input()`/files/args are untrusted; validate type/range; `secrets` vs `random`; never `eval`/`pickle` untrusted data; exceptions and failing closed; path traversal basics. | pytest: validator rejects bad input; token generator uses `secrets` |
| 3 Professional practice | **A03 as a first-class topic**: lockfile with hashes, `exclude-newer = "7 days"`, `uv audit`/pip-audit, how to read an advisory, upgrade workflow. ruff `S` rules. Config/secrets separation. Logging without secrets/PII. CI least privilege, pinned actions, zizmor, Dependabot. `SECURITY.md`. Security items in the PR/review checklist. One incident post-mortem reading (LiteLLM). | Make targets `audit`, `lint` (with `S`), `secrets-scan`; checker runs them and expects exit 0; planted vulnerable pin must be fixed |
| 4 Web basics | HTTP is plaintext, HTTPS/TLS and certificates; origin and same-origin policy; cookies and flags; DevTools Network/Application tabs; first XSS (`innerHTML` vs `textContent`); forms and GET vs POST; SRI for CDN assets; reading response headers with `curl -sI`. | "Spot the header" exercise against a saved response; fix an `innerHTML` page |
| 5 Backend & DB | SQL injection (attack own sqlite lab, then fix); parameterised queries; least-privilege DB role; Pydantic validation; password hashing with pwdlib; session cookie; **ownership checks with tests**; generic auth errors; rate-limit concept; error handling without leaks; structured logs; CORS allow-list; SSRF when fetching URLs; data inventory + minimisation in schema design; first `THREAT_MODEL.md`. | In-process `TestClient` tests: A cannot read B's object, cookie flags present, bad input → 422, injection string returns nothing |
| 6 TypeScript/React | React escaping and its escape hatches; DOMPurify; no tokens in web storage; front-end has no secrets; npm hygiene (`npm ci`, `.npmrc` cooldown + strict scripts or npm 12, reviewing `allowScripts`, `npm audit` against the official registry); choosing dependencies. | Lint rule/test forbidding `dangerouslySetInnerHTML` without sanitiser; checker verifies `.npmrc` and lockfile committed |
| 7 Integration & security | Consolidation: walk OWASP Top 10:2025 and ASVS Level 1 against the learner's app; CSRF guard; security headers + CSP (report-only → enforce); end-to-end authz tests; privacy features (`/me/export`, `/me` delete, privacy notice, consent for optional data); threat model v2; practice on Juice Shop + PortSwigger apprentice labs; `/security-review` as a second opinion. | Header checker; Playwright: logged-out and cross-user flows fail closed; checklist file with evidence links |
| 8 Delivery & ops | Server basics: SSH keys only, firewall, updates, non-root. Docker: non-root, minimal image, no secrets in layers, `.dockerignore`. CI/CD: secret stores, OIDC instead of static keys, environments with approval. Automatic HTTPS + HSTS. Backups and restore drill. Monitoring + alerting on auth failures/5xx. Incident runbook: rotate, assess, notify (72 h / "立即"). Patch cadence. | Dockerfile lint (USER set, no `ENV *_KEY`), zizmor clean, runbook exists and was rehearsed |
| 9 Team & project mgmt | Security review in PR flow, CODEOWNERS on workflows, branch rulesets, signed commits (SSH), vulnerability disclosure and private reporting, access on/off-boarding, blameless post-mortems (read TanStack or PostHog), dependency update policy. | PR template contains security section; simulated "leaked key" drill |
| 10 Architecture & capstone | Trust boundaries, defence in depth, secure defaults, privacy by design (impact assessment in one page), final threat model, self-assessment against the checklist below, SBOM/dependency inventory. | Capstone gate = checklist all green |

Teach first: secrets hygiene, account security, untrusted-input mindset, ownership checks, parameterised queries, framework escaping, lock + audit + cooldown, HTTPS. Postpone: OAuth/OIDC/SAML internals, passkey implementation, strict nonce CSP and Trusted Types, WAFs, KMS/HSM, Kubernetes security, fuzzing, Burp beyond basics, cryptographic primitives, formal methods (PASTA, OCTAVE).

## 10. Secure-by-default checklist for the capstone (ASVS L1-flavoured)

Access & identity
- [ ] Every non-public endpoint requires authentication; routes deny by default.
- [ ] Every object access checks ownership/role server-side; tests prove user A cannot read/modify/delete user B's data (expect 404/403).
- [ ] Passwords: min 8 (15 recommended), max ≥ 64, any characters, checked against a common-password list; hashed with Argon2id via pwdlib; generic login/reset errors; login attempts throttled.
- [ ] Session ID from `secrets`, regenerated at login, invalidated at logout; idle timeout set.
- [ ] Cookie: `__Host-` name, `HttpOnly; Secure; SameSite=Lax|Strict; Path=/`; no tokens in localStorage/sessionStorage.
- [ ] State-changing routes use POST/PUT/PATCH/DELETE and pass a CSRF check (Fetch Metadata + Origin fallback or token).

Data in / data out
- [ ] All request data validated by schemas (type, length, range); size limits on bodies/uploads.
- [ ] All SQL parameterised (or ORM without raw string building); dynamic identifiers via allow-list.
- [ ] No `dangerouslySetInnerHTML`/`innerHTML`/`|safe` with user data unless sanitised with DOMPurify; templates autoescape.
- [ ] Any server-side URL fetch uses a host allow-list or IP classification, http/https only, redirects off.
- [ ] Errors: global handler, generic message to client, details only in logs; failures deny rather than allow.

Transport & browser
- [ ] HTTPS only, HTTP redirects, HSTS ≥ 1 year, certificate renewal automated and monitored.
- [ ] Headers: CSP (at least `default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; form-action 'self'`), `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`.
- [ ] CORS: none (same origin) or explicit allow-list; never `*` with credentials.

Secrets & configuration
- [ ] No secrets in repo, history, images, front-end bundle or logs; `.env` ignored, `.env.example` committed; secret scan in pre-commit/CI; push protection on.
- [ ] Separate dev/test/prod configuration; debug off in production; default accounts absent.
- [ ] Database user is not owner/superuser; backups encrypted and restore tested.

Supply chain
- [ ] `uv.lock` and `package-lock.json` committed; CI uses `uv sync --locked` and `npm ci`.
- [ ] Cooldown configured (`exclude-newer`, `min-release-age`); install scripts reviewed (`allowScripts`) and strict mode on.
- [ ] `uv audit`/pip-audit and `npm audit` (official registry) run in CI and fail the build on findings; Dependabot (or equivalent) enabled.
- [ ] GitHub Actions: least-privilege `permissions:`, actions pinned (SHA or lockfile), no `pull_request_target`, zizmor clean.
- [ ] Docker image runs as non-root, built from a pinned minimal base, no secrets in layers.

Logging, privacy, process
- [ ] Auth successes/failures, access-control failures and admin actions logged with request ID; no passwords/tokens/full personal data in logs; an alert exists for repeated failures.
- [ ] Data inventory documented; only necessary fields collected; retention stated; user can export and delete their data; privacy notice linked.
- [ ] `THREAT_MODEL.md` current; `SECURITY.md` present; incident runbook (rotate → assess → notify) rehearsed once.
- [ ] Automated security tests are part of the normal test suite and run in CI.

## 11. Safe and legal ways to practise

- **OWASP Juice Shop** (v20.2.0 on the project page; guide mentions v20.3.0): deliberately insecure shop, Node.js/Express/Angular, score board, CTF mode. Runs on Node 22/24/26 (`"engines": {"node": "22 - 26"}`) so Node 26 works from source (`git clone … --depth 1 && npm install && npm start`), or `docker run -d -p 127.0.0.1:3000:3000 bkimminich/juice-shop`. UI has 44 locales including `zh_CN`, `zh_TW`, `zh_HK`; the companion guide is English. [source: https://owasp.org/www-project-juice-shop/ , https://pwning.owasp-juice.shop/companion-guide/latest/part1/running.html , https://github.com/juice-shop/juice-shop/tree/master/frontend/src/assets/i18n] Not started here (no port binding in the sandbox).
- **PortSwigger Web Security Academy**: "100% free"; labs on PortSwigger's own infrastructure "in a safe and legal manner"; topics grouped Server-side / Client-side / Advanced; "For complete beginners, we recommend starting with our server-side topics", SQL injection first; some labs need Burp Suite Community. English only (no language selector seen). [source: https://portswigger.net/web-security , https://portswigger.net/web-security/all-topics]
- **CyLab Security Academy (formerly picoCTF)**, Carnegie Mellon: free, 500+ challenges, categories General Skills, Cryptography, Web Exploitation, Forensics, Binary Exploitation, Reverse Engineering (+ AI, Blockchain), learning paths. English. [source: https://picoctf.org/ , https://cylabacademy.org]
- Chinese-language platforms often recommended to beginners: CTFHub (skill tree), BUUCTF, 攻防世界 (XCTF). Only blog-level evidence today that they are active. [secondary: search results]
- Best first "lab" is the learner's own app: break it in a test, then fix it (everything in section 3 ran offline).
- Legal line (China): Cybersecurity Law (2016 text, Art. 27): "任何个人和组织不得从事非法侵入他人网络、干扰他人网络正常功能、窃取网络数据等危害网络安全的活动" and must not provide tools for it. [source: https://www.cac.gov.cn/2016-11/07/c_1119867116_2.htm] After the 2025 amendment the clause is renumbered — Art. 29 by my reading of the amending decision (old 26 → new 28). [inferred] Criminal Law Art. 285/286 criminalise intrusion, data theft, control and sabotage of computer systems. [memory] Vulnerability rules (effective 2021-09-01): do not publish details of flaws in systems others operate, do not publish before the vendor's fix without coordination, do not release exploit tools. [source: https://www.cac.gov.cn/2021-07/13/c_1627761607640342.htm]
- Rule for the handbook: test only what you own or what a platform explicitly provides for attack; written permission and scope before anything else; never "practise" on school, employer or random public sites.

## 12. Plain-Chinese analogy bank (for lesson writers)

- 认证 vs 授权：认证是门口查身份证；授权是你的门禁卡能刷开哪几扇门。登录成功不等于哪扇门都能进。
- 越权访问（IDOR）：拿着自己的取件码，却能打开别人的快递柜格子——柜子只核对"有没有码"，没核对"这格是不是你的"。
- SQL 注入：办事员把你填在"姓名"栏里的字当成指令照着念。参数化查询就是规定：表格里填的永远只是"内容"，不是"指令"。
- XSS：留言板上有人贴了一张"谁看到谁就照做"的纸条。输出转义相当于把纸条塑封——只能看，不能执行。
- CSRF：你戴着银行的手环（Cookie），骗子引你按下一个按钮，银行看到手环就照办。防护就是银行再问一句："这张单子是在我们自己柜台填的吗？"
- CORS：不是防盗门，而是浏览器的"代取规则"——别的网站的脚本想读你家的回信，得你家明确写了"允许某某代取"。信其实已经寄到了。
- Cookie 三个标志：HttpOnly＝手环芯片只有柜台读卡器能读，网页脚本读不到；Secure＝只在加密通道里出示；SameSite＝不跟着别的网站发起的请求一起出示。
- 密码哈希：绞肉机——肉能变肉馅，肉馅变不回肉。加盐＝每个人的肉馅里加一撮不同的调料，没法批量对照。Argon2＝故意又慢又占地方的绞肉机，让批量破解不划算。
- JWT：盖了章的介绍信——内容谁都能看，改一个字章就对不上。所以别在里面写秘密。
- HTTPS：明信片 vs 密封挂号信，而且先核对了收信人的证件（证书）。证书会过期，所以要自动续期。
- 密钥管理：家门钥匙别挂在门把手上（代码仓库）。.env 是抽屉，密钥管理服务是保险柜。钥匙丢了，第一件事是换锁（轮换），不是把丢钥匙的照片删掉。
- Git 历史：写进账本的每一页都撕不掉；后来划掉一行，前面那页还在。
- 供应链：做菜用的每样食材都来自别人。锁文件＝写明批次号的进货单；冷却期＝新到的货先放几天，看有没有召回；审计＝拿进货单对照召回名单；安装脚本＝食材一进门就自己动手改厨房。
- 最小权限：给保洁的是保洁间的钥匙，不是整栋楼的万能钥匙。
- 日志：行车记录仪——要拍到发生了什么，但别把乘客的身份证拍进去。
- 失败时关闭（fail closed）：门禁坏了应该锁住，而不是敞开。
- 威胁建模：装修前先想"小偷会从哪里进来、值钱的东西放在哪"。
- 纵深防御：小区门禁、单元门、家门、保险柜——任何一层都可能失守，所以不只装一层。
- 双因素／通行密钥：钥匙加指纹；通行密钥是"只认这扇真门"的钥匙，假门（钓鱼网站）插不进去。
- 个人信息最小化：外卖只需要地址和电话，不需要身份证号——没收集的数据永远不会泄露。

## 13. Where the evidence says the plan should change

1. Security cannot wait for stage 7; the first leak risk is in stage 1 (and already exists while the learner directs an AI). Keep stage 7 as consolidation and spread the content as in section 9.
2. Add a prerequisite step before stage 1 Git work: if `commit.gpgsign=true` is set without gpg, the learner (not a script) decides how to resolve it — simplest is turning signing off globally for now and introducing SSH signing in stage 9. Verified in a throwaway repo: repo-local `commit.gpgsign=false` commits fine; SSH signing works with `gpg.format=ssh`, `gpg.ssh.program=ssh-keygen`, `user.signingkey=<pubkey path>` → `Good "git" signature … with ED25519 key`. [local]
3. If the learning workspace is on an iCloud-synced Desktop, relocate it before any `.env`, `.git`, `.venv`, database or `node_modules` is created there.
4. Stage 3 should name supply-chain security explicitly (it is OWASP A03 now) for PyPI, and stage 6 for npm; the roadmap currently lists only tools.
5. Fix the npm baseline: either upgrade the learner to npm 12 or ship a course `.npmrc` (`min-release-age=7`, `strict-allow-scripts=true`). Do not introduce pnpm just for safety defaults — it is not installed and adds a second tool.
6. If the course recommends Chinese mirrors, pick ones that keep the controls working (TUNA for PyPI) and teach `npm audit --registry=https://registry.npmjs.org`.
7. Add privacy-by-design content (section 5) to stages 5, 7, 8, 10; PIPL first, GDPR as comparison.
8. Capstone auth default: server-side session cookie on a same-origin deployment; JWT/OAuth as explained alternatives. This removes CORS, token-storage and refresh-token complexity from the critical path.
9. Use Top 10:2025 and ASVS 5.0 identifiers everywhere; both have Chinese editions the learner can read alongside English.
10. Practice platforms are enrichment, not core: they are English-heavy and attack-oriented; the measurable skill is defending and testing one's own app. Refer to picoCTF by its new name.
11. The tutor configuration needs explicit security rules (section 6), including a `permissions.deny` for `.env` files in the workspace settings.
12. Auto-check scripts must be offline and in-process (no scanning, no real secrets, no network), and the vulnerable examples they use must contain only obviously fake credentials (scanners and push protection will otherwise block commits).
13. Test snippets for FastAPI should depend on `httpx2`, or learners will see a deprecation warning on every run.

## 14. Not verified (treat as open)

- Official "final release" announcement date of OWASP Top 10:2025 (only the 2025-12-24 commit removing "RC" was seen; third parties say January 2026).
- New article number of the anti-intrusion clause in the amended Cybersecurity Law; exact wording/penalties of Criminal Law Art. 285/286; ICP filing / MLPS / real-name details.
- GDPR articles not read today: Art. 8 age threshold, Art. 12(3) one-month deadline, Art. 22, Art. 25, Art. 32 wording; EU Digital Omnibus status beyond secondary summaries.
- npm 12's exact behaviour for an unapproved script (skip + warning vs error) — this Mac has 11.20.0; the version that introduced `min-release-age` (search results say 11.10.0).
- Whether GitHub's `actions.lock` workflow lockfile is GA or preview; Betterleaks details; current gitleaks version.
- CA/Browser Forum SC-081v3 dates (secondary sources only); post-quantum TLS status.
- Browser defaults for `SameSite` (Chrome Lax-by-default) and third-party cookie status [memory].
- The phishing details of the September 2025 `debug`/`chalk` compromise and the total scale of Shai-Hulud 2.0.
- Reachability from mainland China of github.com, owasp.org, portswigger.net, cylabacademy.org, Docker Hub; current state of CTFHub/BUUCTF/攻防世界.
- Whether PortSwigger labs require a (free) account to launch; whether Chinese translations of the OWASP cheat sheets exist.
- Who maintains `httpx2` and why Starlette prefers it (only the warning and a successful install were observed).
- A rate-limiting library for FastAPI (none tested); Vite `VITE_*` exposure rule [memory]; passlib's maintenance status [memory].
- Juice Shop was not started here; Docker-based checks were not possible.

## 15. Lab files (under `lab/` beside this brief)

- `pyweb/01_sqli.py`, `02_passwords.py`, `03_fastapi_lab.py`, `04_misc.py`, `05_csrf_fetch_metadata.py` (+ `pyproject.toml`, `uv.lock`): run with `uv sync && uv run python <file>`.
- `pyvuln/` (deliberately outdated pins, `audit.txt`, `pipaudit.txt`), `pycool/` (cooldown lock), `pymirror/` (mirror test).
- `sast/bad.py`, `sast/cfg/` (ruff config), `gha/.github/workflows/ci.yml` (bad workflow for zizmor).
- `gitleak/` (secret-in-history repo, fake values only), `evilpkg/` (harmless postinstall demo package), `npmlab/`, `npmcool/`, `npmmirror/`, `reactlab/xss.mjs`.

# Brief: standards-landscape

Topic: a current, sourced map of the norms that govern professional software work (standards, legal and contractual requirements, de facto conventions, style guides, team agreements).
Checked on: 2026-11-19 (the reference Mac (plan G7): macOS 27.2.1 arm64, git 2.54.0 Apple Git-157, Python 3.14.9, uv 0.13.5, ruff 0.17.2, Node v26.12.0) [local].
Audience: the agents who will write the Chinese lessons and the personal engineering handbook. Not written for the learner.

## 0. How to read this brief

### 0.1 Basis tags

- `[local]` = I ran it on this machine today.
- `[source: URL]` = I fetched and read that page today.
- `[search: URL]` = weaker: the page itself refused my fetch (or was not fetched); I read it only through the search tool's summary of that URL today. Re-verify before printing an exact date or number in a lesson.
- `[memory]` = not verified today. Treat as a lead, not a fact.

Quotation policy: everything below is paraphrase. Error messages shown verbatim come from my own terminal runs.

### 0.2 Access log (why some items are weaker)

Fetched normally: git-scm.com, docs.github.com, peps.python.org, packaging.python.org, python.org, typing.python.org, ecma-international.org, tc39.es, w3.org, whatwg.org, web.dev, rfc-editor.org (JSON metadata), datatracker.ietf.org, openapis.org, json-schema.org, openid.net, unicode.org, owasp.org sub-sites, cwe.mitre.org, csrc.nist.gov, pages.nist.gov, slsa.dev, openssf sites, first.org, cisa.gov, digital-strategy.ec.europa.eu, commission.europa.eu, cppa.ca.gov, cac.gov.cn, gov.cn (one page), openstd.samr.gov.cn, agents.md, docs.kernel.org, apache.org, linuxfoundation.org, survey.stackoverflow.co, hiringlab.indeed.com, digitaleconomy.stanford.edu, dropbox.github.io, sfia-online.org, catb.org (plain HTTP via curl), and others cited inline.

Refused or unusable today: iso.org (HTTP 403 to both fetch tools), computer.org (403), blog.ansi.org (403 / challenge page), stackoverflow.com help pages (challenge page; not bypassed), npc.gov.cn (TLS handshake failure), beian.miit.gov.cn (HTTP 521), eur-lex.europa.eu (empty body), cve.org (JavaScript-only page), handbook.gitlab.com (redirected to a sign-in page). Items that depend on these carry `[search: …]` or `[memory]`.

### 0.3 One anomaly to keep in mind

python.org lists Python 3.15.2 as the latest release, with 3.15 first released 2026-10-09, while this machine runs 3.14.9 [source: https://www.python.org/downloads/] [local]. I report both as observed; the builders should teach against the interpreter that is installed and state the newer series exists.

## 1. Local facts that change what the lessons must say

1. **Every plain `git commit` fails when the global signing config is half-written.** Example: global git config contains `commit.gpgsign=true`, `gpg.format=openpgp`, `gpg.program=gpg`, an empty `user.signingkey`, an empty `gpg.ssh.program`, an empty `gpg.ssh.allowedsignersfile`, and `tag.forcesignannotated`; no `gpg` or `gpg2` binary is on PATH [local]. In a scratch repository the commit ended with:

   ```text
   error: cannot run gpg: No such file or directory
   error: gpg failed to sign the data:
   fatal: failed to write commit object
   ```

   Verified workarounds in the scratch repository, none of which touched global config [local]:
   - one-off: `git commit --no-gpg-sign -m "..."` succeeded;
   - per repository: `git config --local commit.gpgsign false` then a normal commit succeeded;
   - SSH signing without GnuPG: repo-local `gpg.format=ssh`, `user.signingkey=<path to .pub>`, **and** `gpg.ssh.program=ssh-keygen` produced a commit that `git log --show-signature` reported as a good ED25519 signature (`%G?` = `G`). Without the `gpg.ssh.program` override it failed with `error: cannot run : No such file or directory`, because the global value is an empty string.
   Such a key set resembles what a graphical Git client writes from its signing preferences [memory]. The sibling brief `git-norms` reports the same blocker independently.
2. **A working folder on the Desktop may be iCloud-synced.** With "Desktop & Documents" sync on, `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop` links to `~/Desktop`, and `~/Desktop` carries the iCloud file-provider attribute [local]. Reported damage from this: iCloud can set the hidden flag on files in a virtual environment so Python 3.14 skips `.pth` files, and iCloud can produce conflict copies named like `file 2.csv` [memory; see the sibling brief `uv-packaging`]. `~/Developer` is not created by default.
3. macOS ships a dedicated `DeveloperFolderIcon.icns` in `CoreTypes.bundle` [local], which supports teaching `~/Developer` as a macOS convention (not an Apple requirement; I found no Apple document that mandates it [search: https://discussions.apple.com and community posts]).
4. The volume is case-insensitive: creating `CaseTest.txt` made `casetest.txt` resolve to the same file [local].
5. `git init` creates `main` here because Xcode's bundled gitconfig sets `init.defaultBranch=main` and `credential.helper=osxkeychain` [local]. Upstream Git still defaults to `master` until Git 3.0 [source: https://git-scm.com/docs/BreakingChanges].
6. A fresh Mac has no SSH public keys, `~/.ssh/config` or `known_hosts` in `~/.ssh` yet. A global ignore file named by `core.excludesfile` (for example `~/.gitignore_global`) may already exist; check with `git config get core.excludesfile`.
7. Not installed by default: `gh`, `gpg`, `git-lfs`, `pre-commit`, `gitleaks`, `markdownlint`, `markdownlint-cli2`, `shellcheck`, `pnpm`, `psql`. Homebrew, once installed, lives at `/opt/homebrew/bin/brew` on Apple silicon [local].

## 2. Currency deltas: where older tutorials (and model memory) are now wrong

| Topic | Stale belief | Verified today |
|---|---|---|
| Software life cycle | ISO/IEC/IEEE 12207:2017 is current | **12207:2026**, edition 2, published April 2026; replaces 2017 [search: https://www.iso.org/standard/90219.html] [search: https://webstore.iec.ch/en/publication/113447] |
| Product quality model | ISO/IEC 25010 has 8 characteristics | **25010:2023** has 9 (adds safety; usability became interaction capability; portability became flexibility) [search: https://standards.iteh.ai/catalog/standards/iso/8c5bd63e-9e67-4b55-90e3-8cb2b10a2030/iso-iec-25010-2023] |
| DORA | "four key metrics" | **five-metric model**: change lead time, deployment frequency, failed deployment recovery time (throughput); change fail rate, deployment rework rate (instability). Page updated 2026-01-05 [source: https://dora.dev/guides/dora-metrics/] |
| Kanban Guide | 2020 edition | **May 2025** edition; an "Open Guide to Kanban" (July 2025) also exists [source: https://kanbanguides.org/] |
| Scrum Guide | a newer one must exist | still **2020**; the revision history lists nothing later [source: https://scrumguides.org/revisions.html] |
| Python | 3.13 or 3.14 is newest | **3.15** released 2026-10-09 (latest 3.15.2); 3.14 bugfix; 3.11 to 3.13 security-only; **3.10 end-of-life** [source: https://www.python.org/downloads/] |
| Python packaging | `setup.py` + `requirements.txt` | `pyproject.toml` with four tables; dependency groups (PEP 735, Final) and `pylock.toml` (PEP 751, Final) are accepted standards; licence as SPDX expression (PEP 639) [source: https://packaging.python.org/en/latest/specifications/pyproject-toml/] |
| ECMAScript | ES2025 | **ES2026**, 17th edition, June 2026; the draft is titled ES2027 [source: https://ecma-international.org/publications-and-standards/standards/ecma-262/] [source: https://tc39.es/ecma262/] |
| WCAG 3 | Bronze / Silver / Gold levels | September 2026 Working Draft uses a tier model with one conformance level; still years from Recommendation; meet **WCAG 2.2** now [source: https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/] |
| Unicode | 16.0 or 17.0 | **18.0.0**, 2026-09-16, 172,808 characters [source: https://www.unicode.org/versions/Unicode18.0.0/] |
| OpenAPI | 3.1.x | **3.2.1**, dated 10 September 2026 [source: https://spec.openapis.org/oas/latest.html] |
| OAuth 2.1 | "about to be an RFC" | still an Internet-Draft: **draft-17**, 31 October 2026, expires 4 May 2027 [source: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/] |
| TLS 1.3 | RFC 8446 | RFC 8446 is marked **obsoleted by RFC 9846** [source: https://www.rfc-editor.org/rfc/rfc8446.json] |
| OWASP Top 10 | 2021 list | **2025** edition; new A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions [source: https://top10.owasp.org/2025/] |
| OWASP ASVS | 4.0.3 | **5.0.0**, 30 May 2025 [source: https://asvs.owasp.org/] |
| NIST SSDF | 1.1 only | 1.1 is still the final version; **1.2 (SP 800-218 Rev. 1)** is an initial public draft of 2025-12-17, comments closed 2026-01-30 [source: https://csrc.nist.gov/pubs/sp/800/218/r1/ipd] |
| SLSA | 1.0 / 1.1 | **1.2**, status Approved, adds a Source track [source: https://slsa.dev/spec/] |
| Password rules | complexity rules, 90-day rotation | NIST SP 800-63B-4 (final 2025): at least 15 characters for single-factor passwords, no composition rules, no periodic change, blocklist check, password managers allowed [source: https://pages.nist.gov/800-63-4/sp800-63b.html] |
| EU AI Act | high-risk rules apply 2 Aug 2026 | amended by **Regulation (EU) 2026/1744** (in force 27 July 2026): Annex III high-risk from **2 Dec 2027**, Annex I from **2 Aug 2028**; a ninth prohibition applies from December 2026 [source: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai] |
| EU Cyber Resilience Act | "future law" | reporting obligations apply since **11 Sept 2026**; main obligations 11 Dec 2027 [source: https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act] |
| EN 301 549 | V3.2.1 with WCAG 2.1 | **V4.1.1** published 2 Sept 2026 and includes WCAG 2.2; citation in the Official Journal still pending [search: https://www.deque.com/blog/en-301-549-v4-1-1-is-final-what-changed-what-it-means-and-what-you-should-do/] |
| China Cybersecurity Law | 2017 text | amended 2025-10-28, in force **2026-01-01**, adds an AI article [source: https://www.cac.gov.cn/2026-01/02/c_1769093523928606.htm] |
| ITIL | ITIL 4 | **ITIL (Version 5)** launched early 2026 and runs alongside ITIL 4 [search: https://itil.com/Itil-News-and-Announcements/itil-version-5-transition-from-itil-4] |
| GitHub 2FA | any method equally | GitHub recommends a TOTP app as the primary method and says passkeys and security keys are not yet supported as primary 2FA methods [source: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication] |
| Git over HTTPS | account password | password authentication for Git operations was removed; use a token via a credential helper, GitHub CLI, or SSH [source: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github] |
| AI attribution in Linux | an `Assisted-by:` tag is documented | the kernel page I read (7.4.0-rc3 docs) has no such tag; it forbids AI adding `Signed-off-by` and puts responsibility on the human [source: https://docs.kernel.org/process/coding-assistants.html] |
| Developer trust in AI | "most developers distrust AI" | Stack Overflow 2026 (30,903 responses): 48.0% trust AI when the output is easy to verify; 6.6% trust it for many tasks including important decisions [source: https://survey.stackoverflow.co/2026/] |

## 3. Taxonomy: seven kinds of rule

### 3.1 The seven categories and how they map onto the course's four words

The course's design goal names 规范 / 标准 / 行业要求 / 惯例. In Chinese engineering usage these words overlap (for example "specification" is routinely translated 规范, and national standards carry 规范 in their titles, such as GB/T 35273 个人信息安全规范). So the course needs fixed labels. Recommended labels:

| Code | Recommended Chinese label | English | Course word |
|---|---|---|---|
| S | **标准**（正式标准与规范文本） | Formal standards and specifications from a standards body | 标准 |
| L | **行业要求**（法律法规与合规要求） | Laws, regulations, contractual and compliance requirements, mandatory platform policy | 行业要求 |
| D | **惯例·事实标准**（社区规范） | De facto standards and widely adopted community specifications | 惯例 |
| P | **惯例·平台与工具** | Platform and tool conventions | 惯例 |
| O | **规范·组织**（风格指南与手册） | Organisation style guides and playbooks | 规范 |
| T | **规范·团队约定** | Team agreements | 规范 |
| X | **个人偏好**（不是规则） | Personal preference | none of the four |

Exact mapping rule to print in the handbook:

- **标准** = category S only: a document with an issuing body and a designation or number (ISO/IEC 25010:2023, RFC 9110, WCAG 2.2, ECMA-262, PEP 8, GB/T 8566-2022).
- **行业要求** = category L: something a third party can hold you to (regulator, court, customer, auditor, platform). A second, softer sense of 行业要求 is "what employers expect of a professional"; label that separately as **岗位期望** (section 5) so the learner never confuses a hiring expectation with a legal duty.
- **惯例** = categories D and P: nobody can fine you, but tools, platforms and other developers assume it.
- **规范** = categories O and T: written rules that an organisation or a team has adopted for itself. Also say once, plainly, that 规范 is used in everyday Chinese as the umbrella word for all of the above; in this course the narrow sense applies whenever a rule card says 规范.
- **个人偏好** sits outside the four words on purpose. Teaching the learner to say "this is only my preference" is itself a professional norm (Google's review standard treats style points not covered by the style guide as personal preference [source: https://google.github.io/eng-practices/review/reviewer/standard.html]).

### 3.2 Category and obligation level are two separate axes

A rule card needs both. Category answers "who wrote it"; obligation level answers "how strongly does it apply to me here". The same document changes level with context:

- WCAG 2.2 is a voluntary W3C Recommendation, but EN 301 549 V4.1.1 incorporates it and the European Accessibility Act makes accessibility a legal duty for covered products and services [source: https://www.w3.org/TR/WCAG22/] [search: https://www.deque.com/blog/en-301-549-v4-1-1-is-final-what-changed-what-it-means-and-what-you-should-do/].
- In China the prefix tells you: **GB** is a mandatory national standard, **GB/T** is a recommended one. The national standards portal labels GB 45438-2025 as 强标 and GB/T 22239-2019 as 推标 [source: https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=45438]. A recommended standard still becomes binding when a law or contract points at it (等保 is the usual example) [memory].
- Conventional Commits is a community specification, but a team that enforces it in CI has made it 必须 inside that repository.

Recommended three levels, aligned with vocabularies the learner will meet:

| Course level | RFC keywords (BCP 14) | Alibaba manual | Chinese standards drafting [memory] | Meaning for the learner |
|---|---|---|---|---|
| **必须** | MUST / SHALL | 强制 | 应 / 不应 | Breaking it causes real harm, a blocked action, or a legal or contractual breach |
| **推荐** | SHOULD | 推荐 | 宜 / 不宜 | Do it unless you can state a reason; expect to be asked why not |
| **参考** | MAY | 参考 | 可 / 不必 | Good to know; choose freely |

RFC 2119 (March 1997, Best Current Practice, updated by RFC 8174) defines the requirement keywords [source: https://www.rfc-editor.org/rfc/rfc2119.json]. The Alibaba Java manual grades its rules 强制 / 推荐 / 参考 by binding force and failure sensitivity and adds 说明 / 正例 / 反例 to each rule [search: https://developer.aliyun.com/article/72038]; latest edition 黄山版, released 2022-02-03 [source: https://github.com/alibaba/p3c].

### 3.3 Per-category profile

| | S 标准 | L 行业要求 | D 惯例·事实标准 | P 惯例·平台与工具 | O 规范·组织 | T 规范·团队约定 | X 个人偏好 |
|---|---|---|---|---|---|---|---|
| Who has authority | A standards body with a published process (ISO/IEC/IEEE, IETF, W3C, WHATWG, Ecma, Unicode, Python Steering Council for PEPs, SAC for GB) | Legislatures and regulators; contract parties; certification schemes; a platform's terms | Maintainers plus adoption; no formal mandate | The vendor or maintainer of the tool or platform | The organisation that wrote it; outsiders adopt it voluntarily | The team itself | Only you |
| How binding | Voluntary by itself; binding when a law, contract or tender cites it | Binding; can carry fines, loss of business, removal from a store, account lock-out | Socially and technically binding: tools assume it | Binding in practice while you use that tool; often enforced by the tool | Binding for employees and contributors of that organisation | Binding inside the team once agreed | Not binding on anyone else |
| If you ignore it | Interoperability failures; failed audits or lost tenders where it is referenced | Fines, liability, lost contracts, takedown, account restrictions | Tools misbehave; reviewers push back; you look inexperienced | Features do not work; pushes are rejected; files are not recognised | Review rejection; poor performance evaluation | Rework; friction; CI failure if automated | Nothing, unless you impose it on others |
| How it changes | Numbered editions, amendments, errata; living standards change continuously; IETF publishes a new RFC that obsoletes or updates the old one | Amendments, implementing acts, phased application dates, regulator guidance, court decisions | New versions when maintainers release; some never change (SemVer 2.0.0 since 2013) | Without ceremony: release notes and documentation edits | New editions or continuous handbook edits | Pull request to the agreement file; retrospectives; decision records | Whenever you like |
| How to cite | Designation, edition or date, clause: `ISO/IEC 25010:2023`, `RFC 9110 §15.5`, `WCAG 2.2 SC 1.4.3`, `PEP 8 (Naming Conventions)` | Instrument, article, version or effective date: `GDPR Art. 6(1)(a)`, `《个人信息保护法》第十三条（2021-11-01 施行）` | Name, version, URL: `Semantic Versioning 2.0.0 §8` | Product, page title, URL, date read: `GitHub Docs, "About READMEs", read 2026-11-19` | Guide name, edition or commit, section: `《Java 开发手册（黄山版）》` | File path and commit, or decision record number: `CONTRIBUTING.md@a1b2c3d`, `ADR-0007` | Do not cite; say "my preference" |
| One-line Chinese explanation with analogy | 标准像国标插座和 A4 纸：没人逼你用，但不按它做就和别人对不上。 | 行业要求像交通法规和营业执照：不遵守会被罚、被下架或丢掉合同。 | 事实标准像靠右行走和普通话：没有法律规定，但大家都这么做，工具也默认你这么做。 | 平台惯例像小区和商场的规定：在人家的地盘上，就按人家的默认方式来。 | 组织规范像公司的员工手册或后厨操作规程：进了这家门，就守这家的规矩。 | 团队约定像合租公约：自己人商量定的，可以改，但定了就要守。 | 个人偏好像口味：可以坚持，但不能拿来要求别人。 |

### 3.4 Decision procedure for classifying any rule (teach in stage 0)

Ask in this order and stop at the first yes:

1. Can a regulator, court, customer, auditor or platform penalise me for breaking it? Then 行业要求.
2. Does it have an issuing standards body and a designation or number? Then 标准.
3. Is it a public, versioned specification that many independent projects and tools follow? Then 惯例·事实标准.
4. Is it simply how one tool or platform works or what it expects? Then 惯例·平台与工具.
5. Did one organisation write it for its own engineers? Then 规范·组织.
6. Did this team or this repository decide it? Then 规范·团队约定.
7. Otherwise it is 个人偏好.

Then ask separately: in my situation today, is it 必须, 推荐 or 参考, and who would notice if I ignored it (law, customer, platform, tool, reviewer, nobody)?

### 3.5 Three teaching points that prevent later confusion

- **A standard is not a law.** Standards bodies cannot punish anyone. The force comes from whoever references the standard.
- **Popularity is not authority.** A blog post repeated a thousand times is still category X until a body, tool or team adopts it. The commit-message "50 characters" guidance is a good example: the Git manual itself calls it a good idea but not required [source: https://git-scm.com/docs/git-commit].
- **Documents age at different speeds.** SemVer 2.0.0 and RFC 2119 are stable for years; platform policy and law changed several times in the last twelve months (section 2). Every card therefore carries a checked-on date and a review interval (section 8).

## 4. Catalogue of norms (133 entries)

Column key. **Cat**: S 标准, L 行业要求, D 惯例·事实标准, P 惯例·平台与工具, O 规范·组织, T 规范·团队约定 (section 3.1). **Stage**: roadmap stage that should teach it; "aw." means awareness only (name it, say what kind of rule it is, do not drill it). Versions and dates are as verified on 2026-11-19 unless the basis tag says otherwise. A `zh:` link is a Chinese text that is official or well maintained.

### 4.1 Life cycle, process, quality (A)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| A01 | 软件生存周期过程 / ISO/IEC/IEEE 12207 | S | ISO/IEC JTC 1/SC 7 with IEEE | **12207:2026**, edition 2, April 2026 (ISO and IEEE give different days); replaces 2017 | Names the processes for acquiring, building, operating, maintaining and retiring software; prescribes no life-cycle model; the 2026 edition expands agile coverage. Bites in government, defence and regulated contracts and in audit vocabulary | 9 aw. (name it in 0) | https://www.iso.org/standard/90219.html [search: same URL] [search: https://webstore.iec.ch/en/publication/113447] |
| A02 | 软件测试系列标准 / ISO/IEC/IEEE 29119 | S | same | Part 1: 2022; Parts 2 and 3: 2021 (listed as current); Parts 4 and 5 not confirmed today | Test concepts, processes, documentation, techniques. Bites in regulated sectors and formal test plans | 3 aw. | https://standards.ieee.org/ieee/29119-2/7498 [search: same URL] |
| A03 | 软件工程知识体系指南 / SWEBOK Guide | S | IEEE Computer Society | **V4.0** (October 2024), 18 knowledge areas (adds architecture, operations, security); V5 is planned | The profession's map of accepted knowledge. Use it to cross-check the syllabus | 0, 10 | https://www.computer.org/education/bodies-of-knowledge/software-engineering [search: same URL] |
| A04 | 敏捷宣言 / Agile Manifesto | D | 17 signatories | 2001, unchanged | Four value statements and twelve principles. The vocabulary behind most team processes | 9 | https://agilemanifesto.org/ [source]; zh: https://agilemanifesto.org/iso/zhchs/manifesto.html |
| A05 | Scrum 指南 / The Scrum Guide | D | Schwaber and Sutherland | **2020** (latest in the revision history) | Accountabilities, events, artefacts, Definition of Done. Bites in job postings and team rituals | 9 (DoD idea in 1) | https://scrumguides.org/ [source: https://scrumguides.org/revisions.html]; site offers 30+ translations, Chinese not confirmed today |
| A06 | 看板指南 / The Kanban Guide | D | Coleman and Vacanti | **May 2025** edition | Define the workflow, limit work in progress, measure flow. Bites on the learner's own task board | 1 (personal board), 9 | https://kanbanguides.org/ [source] |
| A07 | DORA 交付指标 / DORA metrics | D | DORA (Google Cloud) | Five-metric model; page updated 2026-01-05; latest annual report is 2025 | Throughput: change lead time, deployment frequency, failed deployment recovery time. Instability: change fail rate, deployment rework rate. Bites in how teams judge delivery health | 8, 9 | https://dora.dev/guides/dora-metrics/ [source] [source: https://dora.dev/research/] |
| A08 | 能力成熟度模型集成 / CMMI | D (proprietary model; becomes L when a tender demands an appraisal) | ISACA | V3.0, released April 2023; the institute's own landing page still shows V2.0 material | Maturity levels 0 to 5 over practice areas. Bites in outsourcing and public tenders, including in China [memory] | 9 aw. | https://cmmiinstitute.com/cmmi [source: page shows V2.0] [search: https://www.isaca.org/resources/news-and-trends/isaca-now-blog/2023/cmmi-updates-take-performance-improvements-to-the-next-level] |
| A09 | 系统与软件工程 软件生存周期过程 / GB/T 8566-2022 | S (推荐性国标) | 国家标准委 | 现行; issued 2022-10-14, effective 2023-05-01; adopts ISO/IEC/IEEE 12207:**2017**, so it now lags the international edition | Chinese counterpart of A01. Bites in government and state-owned-enterprise project documents | 9 aw. | https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=8566 [source]; adoption relation [search: https://www.chinesestandard.net/PDF/English_MS.aspx/GBT45802-2025] |
| A10 | 计算机软件文档编制规范 / GB/T 8567-2006 | S (推荐性国标) | 国家标准委 | 现行; issued 2006-03-14, effective 2006-07-01 | Templates for requirement, design and test documents. Bites in deliverable lists of Chinese contracts [memory] | 9 aw. | https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=8567 [source] |
| A11 | 系统与软件质量模型 / ISO/IEC 25010 | S | ISO/IEC JTC 1/SC 7 | **25010:2023**, edition 2, nine characteristics; Chinese GB/T 25000.10-2016 is 现行 and still reflects the older model [memory for the correspondence] | Vocabulary for non-functional requirements: functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability, flexibility, safety. Bites in architecture trade-offs and review checklists | 3 (maintainability), 10 | https://www.iso.org/standard/78176.html [search: https://standards.iteh.ai/catalog/standards/iso/8c5bd63e-9e67-4b55-90e3-8cb2b10a2030/iso-iec-25010-2023] [source: https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=25000.10] |
| A12 | 信息时代技能框架 / SFIA | D | SFIA Foundation | Version 9, marked current standard | Seven responsibility levels; level 2 "Assist" describes junior work. Bites in job descriptions and career ladders | 0, 9 | https://sfia-online.org/en/sfia-9/responsibilities/level-2 [source] |
| A13 | 完成的定义 / Definition of Done | T | each team; concept from the Scrum Guide | n/a | A shared checklist for when work counts as finished. Bites on every pull request | 1 (personal DoD), 9 | https://scrumguides.org/ [memory for the concept's wording] |
| A14 | ITIL 服务管理 | D (proprietary framework with certifications) | PeopleCert | ITIL (Version 5) launched early 2026 (sources give 30 Jan or 12 Feb) and runs in parallel with ITIL 4 | Incident, problem, change vocabulary of enterprise IT. Bites in operations job ads | 8 aw. | https://itil.com/ [search: https://itil.com/Itil-News-and-Announcements/itil-version-5-transition-from-itil-4] |

### 4.2 Version control and releases (B)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| B01 | Git 提交信息惯例 / Git commit message convention | D | Git project manual | Manual for Git 2.55.0; newest documented release 2.56.1 | A summary line of at most 50 characters, a blank line, then a body; the manual calls this a good idea, not a requirement. Git uses the first paragraph as the title everywhere. Bites in `git log --oneline`, pull-request titles, review | 1 | https://git-scm.com/docs/git-commit [source] |
| B02 | 《Pro Git》第 2 版 | D | Chacon and Straub; CC BY-NC-SA 3.0 | 2nd edition (2014), maintained online; full Simplified Chinese translation | The reference text for Git concepts | 1, 2 | https://git-scm.com/book/en/v2 [source: https://git-scm.com/book/zh/v2]; zh: https://git-scm.com/book/zh/v2 |
| B03 | 约定式提交 / Conventional Commits | D | conventionalcommits.org | **1.0.0** | `<type>[scope]: <description>`; the spec itself defines only `feat` and `fix`; breaking change by `!` or a `BREAKING CHANGE:` footer; maps onto SemVer. Bites in changelog and release automation and in CI commit linting | 1 (introduce), 3 (automate) | https://www.conventionalcommits.org/en/v1.0.0/ [source]; zh: https://www.conventionalcommits.org/zh-hans/v1.0.0/ |
| B04 | 语义化版本 / Semantic Versioning | D | Tom Preston-Werner | **2.0.0** | MAJOR.MINOR.PATCH; in 0.y.z anything may change. Bites in dependency ranges and release tags | 3 | https://semver.org/ [source]; zh: https://semver.org/lang/zh-CN/ |
| B05 | 日历化版本 / CalVer | D | calver.org | Document revision 26.0 (2026) | Version derived from the release date. Bites when reading versions of Ubuntu and many tools; choose it when time matters more than API compatibility | 3 | https://calver.org/ [source] |
| B06 | 如何维护更新日志 / Keep a Changelog | D | Olivier Lacan | **1.1.0** (the site project itself is at 1.1.2, 2024-09-27) | A human-written `CHANGELOG.md`; headings Added, Changed, Deprecated, Removed, Fixed, Security; an Unreleased section; dates as YYYY-MM-DD | 3 | https://keepachangelog.com/en/1.1.0/ [source]; zh: https://keepachangelog.com/zh-CN/1.1.0/ |
| B07 | 忽略规则 / gitignore | P | Git project; templates by GitHub | Current manual; `github/gitignore` templates under CC0-1.0 | Four sources of patterns with precedence; shared patterns in `.gitignore`, personal ones in `core.excludesFile` (default `~/.config/git/ignore`); ignoring never untracks a tracked file | 1 | https://git-scm.com/docs/gitignore [source] [source: https://github.com/github/gitignore] |
| B08 | 默认分支名 main / default branch name | P | GitHub; Git project | Git 3.0 will default to `main`; no release date set | Bites when an older tutorial says `master` | 1 | https://git-scm.com/docs/BreakingChanges [source] [local] |
| B09 | 仓库不放云同步盘 / no cloud syncing of repositories | P | Git project | gitfaq, last updated in Git 2.53.0 | File-by-file sync can leave missing objects and broken refs; share work through a remote with push and pull | 0, 1 | https://git-scm.com/docs/gitfaq [source] |
| B10 | 文本编码与换行 / text encoding and line endings | P | Git project | gitfaq | UTF-8 without BOM, LF endings, `.gitattributes` with `* text=auto`; keep binaries and build products out | 1 (mention), 3 | https://git-scm.com/docs/gitfaq [source] |
| B11 | 提交签名与 Verified 标记 / commit signing | P (T or L where required) | Git; GitHub | SSH signing needs Git 2.34 or later | GPG, SSH or S/MIME signatures; GitHub shows Verified; admins can require signed commits on a branch. Bites in organisations that enable that rule | 1 (unblock the machine), 3 or 9 (do it properly) | https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification [source] |
| B12 | 开发者原创声明 / Developer Certificate of Origin, `Signed-off-by` | D (L inside projects that require it) | Linux Foundation | DCO 1.1 [memory] | A human certifies the right to submit the change; Git deliberately has no setting to add it automatically. Bites when contributing to Linux, Git and many foundations' projects | 9 aw. | https://developercertificate.org/ [source: https://git-scm.com/docs/git-commit] [source: https://git-scm.com/docs/gitfaq] |
| B13 | 共同作者尾注 / `Co-authored-by` trailer | P | GitHub | n/a | After a blank line, one `Co-authored-by: name <email>` per line. Bites in pair work and AI attribution | 1 | https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors [source] |
| B14 | 分支模型 / branching model | T | each team | n/a | Short-lived branches plus pull requests is the common default; the choice is a team agreement | 2, 9 | [memory] |
| B15 | 代码所有者 / CODEOWNERS | P | GitHub | n/a | File in `.github/`, root or `docs/`; last matching pattern wins; can be made a required review; must stay under 3 MB | 9 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners [source] |

### 4.3 Documentation and writing (C)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| C01 | README 惯例 / README conventions | P | GitHub | Living docs page | State what the project does, why it is useful, how to start, where to get help, who maintains it; lookup order `.github`, root, `docs`; prefer relative links | 1 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes [source] |
| C02 | 社区健康文件 / community health files | P | GitHub | Living | CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, ACCESSIBILITY, FUNDING, issue and pull-request templates; a default LICENSE cannot be inherited | 3, 9 | https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file [source] |
| C03 | Diátaxis 文档框架 | D | Daniele Procida | No version | Four kinds of documentation: tutorials, how-to guides, reference, explanation | 3 | https://diataxis.fr/ [source] |
| C04 | 架构决策记录 / ADR and MADR | D | adr.github.io | MADR **4.0.0** (2024-09-17) | One Markdown file per decision in `docs/decisions/NNNN-title-with-dashes.md`: context, options, outcome | 3 (first record), 10 | https://adr.github.io/madr/ [source] |
| C05 | 文档即代码 / Docs as Code | D | Write the Docs | n/a | Documentation uses issue tracker, Git, plain-text markup, review and automated tests | 3 | https://www.writethedocs.org/guide/docs-as-code/ [source] |
| C06 | CommonMark 规范 | D | CommonMark project | **0.31.2** (2024-01-28) | An unambiguous Markdown syntax | 1 | https://spec.commonmark.org/ [source] |
| C07 | GitHub 风格 Markdown / GFM | P | GitHub | 0.29-gfm (2019-04-06) | Adds tables, task lists, strikethrough, autolinks, disallowed raw HTML | 1 | https://github.github.com/gfm/ [source] |
| C08 | markdownlint 规则 | P | David Anson | 53 rules, MD001 to MD060 | Checks heading increments, single H1, fenced-code language, final newline and more | 1 | https://github.com/DavidAnson/markdownlint [source] |
| C09 | 文件命名（Google 文档风格指南）/ filenames | O | Google | Living | Lowercase, hyphens not underscores, ASCII letters and digits only | 1 | https://developers.google.com/style/filenames [source] |
| C10 | 中文文案排版指北 / Chinese Copywriting Guidelines | D | sparanoid (community) | Repository, MIT, about 15.9k stars | Space between Chinese and Latin text or digits, full-width punctuation, correct capitalisation of proper nouns; tools such as pangu and autocorrect | 1 | https://github.com/sparanoid/chinese-copywriting-guidelines [source] (zh is the original) |
| C11 | 中文技术文档的写作规范 | D | 阮一峰 (community) | Repository, public domain, about 13.1k stars | Titles, text, paragraphs, numbers, punctuation, document structure | 1, 3 | https://github.com/ruanyf/document-style-guide [source] (zh is the original) |
| C12 | 贡献者公约 / Contributor Covenant | D | Organization for Ethical Source | **3.0** | A ready-made code of conduct | 9 | https://www.contributor-covenant.org/ [source] |
| C13 | EditorConfig | D | EditorConfig project | No spec version on the site | `.editorconfig` sets indent, line ending, charset, final newline; VS Code needs an extension | 1 or 3 | https://editorconfig.org/ [source] |
| C14 | 提问的智慧 / How To Ask Questions The Smart Way | D | Raymond and Moen | Revision 3.10, 21 May 2014 | Search first; give precise symptoms in order; state the goal, not only the step; follow up with the solution | 1 | http://www.catb.org/~esr/faqs/smart-questions.html [source]; zh: https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way (file `README-zh_CN.md`, based on revision 3.10, linked from the original) [source] |
| C15 | 最小可复现示例 / minimal reproducible example | P | Stack Overflow help centre | n/a | An example that is minimal, complete and reproducible | 1 | https://stackoverflow.com/help/minimal-reproducible-example [memory]; no official Chinese version [memory] |

### 4.4 Python (D)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| D01 | PEP 8 代码风格指南 | S | Python core developers | Active; last modified 2025-04-04 | 4 spaces; 79 columns, or up to 99 by team agreement; `snake_case` functions and modules, `CapWords` classes, `UPPER_CASE` constants; a project's own guide wins; consistency is not a reason to hurt readability. Written for the standard library and adopted far beyond. Bites through linters and review | 2 | https://peps.python.org/pep-0008/ [source]; Chinese translations are unofficial [memory] |
| D02 | PEP 257 文档字符串约定 | S | Python core developers | Active | Triple double quotes; one-line summary as a command ending in a period; no rule about Google, NumPy or Sphinx markup | 2, 3 | https://peps.python.org/pep-0257/ [source] |
| D03 | Python 类型系统规范 / typing specification | S | Typing Council (PEP 729; three to five members) | Living specification; PEP 729 Active, resolved 2023-11-20 | The normative description of type-checker behaviour; small changes go through the council, language changes still need a PEP | 3 | https://typing.python.org/en/latest/spec/index.html [source] [source: https://peps.python.org/pep-0729/] |
| D04 | pyproject.toml 规范 | S | PyPA | Living specification; history entries through August 2026 (PEP 518, 621, 639, 794, 808) | Tables `[build-system]`, `[project]` (name and version required), `[dependency-groups]`, `[tool]`; `license` is an SPDX expression. Bites as the single configuration file for uv, ruff and pytest | 3 (first seen in 2) | https://packaging.python.org/en/latest/specifications/pyproject-toml/ [source] |
| D05 | 依赖组 / dependency groups (PEP 735) | S | PyPA | Final; resolved 2024-10-10 | Named development-only requirement sets that are not shipped in built distributions | 3 | https://packaging.python.org/en/latest/specifications/dependency-groups/ [source: https://peps.python.org/pep-0735/] |
| D06 | 标准锁文件 / pylock.toml (PEP 751) | S | PyPA | Final; resolved 2025-03-31 | A standard lock-file format for reproducible installs, alongside tool-native lock files | 3 | https://packaging.python.org/en/latest/specifications/pylock-toml/ [source: https://peps.python.org/pep-0751/] |
| D07 | Python 版本支持周期 | P | Python release managers | 3.15 and 3.14 bugfix; 3.13, 3.12, 3.11 security-only; 3.10 end-of-life; 3.16 planned for October 2027 | Each series is supported for about five years. Bites in `requires-python` and CI matrices | 3 | https://www.python.org/downloads/ [source] |
| D08 | src 布局 / src layout versus flat layout | P | PyPA discussion page | Living | src layout stops tests from importing the working tree by accident; the page describes trade-offs and mandates neither | 3 | https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/ [source] |
| D09 | PEP 流程 / what a PEP is | S | Python Steering Council | PEP 1 [memory] | How Python decides; statuses Draft, Accepted, Final, Active | 2 | https://peps.python.org/pep-0001/ [memory] |

### 4.5 JavaScript and the web platform (E)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| E01 | ECMAScript 语言规范 / ECMA-262 | S | Ecma TC39 | **17th edition, ECMAScript 2026**, June 2026; draft titled ES2027 | One edition every June. "ES6" is 2015, not "modern" | 4 | https://ecma-international.org/publications-and-standards/standards/ecma-262/ [source] |
| E02 | HTML 现行标准 / HTML Living Standard | S | WHATWG | Living; last updated 2026-11-19 | No version numbers; updated continuously | 4 | https://html.spec.whatwg.org/multipage/ [source] |
| E03 | CSS 快照 / CSS Snapshot | S | W3C CSS Working Group | **Snapshot 2026** (Group Note) | CSS is a set of modules with levels; the snapshot lists the stable set | 4 | https://www.w3.org/Style/CSS/current-work [source] |
| E04 | Web 内容无障碍指南 / WCAG 2.2 | S (L by reference) | W3C | Recommendation, edition of 12 December 2024; 4 principles, 13 guidelines, 86 active success criteria, levels A, AA, AAA; also published as ISO/IEC 40500:2025 [memory] | Level AA is the usual target. Bites through accessibility law, procurement and lawsuits | 4 (basics), 6, 7 | https://www.w3.org/TR/WCAG22/ [source]; zh: authorised translation exists for 2.1 at https://www.w3.org/Translations/WCAG21-zh/, the 2.2 one is only planned [source: https://www.w3.org/WAI/standards-guidelines/wcag/translations/] |
| E05 | W3C 无障碍指南 3.0 / WCAG 3.0 | S (draft) | W3C | Working Draft, September 2026; overview updated 2026-11-16 | Not usable for conformance; a few more years to completion | 6 aw. | https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/ [source] |
| E06 | Baseline 基线 | D | WebDX Community Group | Baseline 2026 is the set in progress | Newly available means all core browsers support it; widely available means 30 months later | 4 | https://web.dev/baseline [source] |
| E07 | package.json 惯例 | P | npm | npm CLI v11 docs | Lowercase URL-safe name up to 214 characters; SemVer version; SPDX `license`; `"private": true` blocks publishing; `exports`, `engines`, `devEngines`; runtime versus development dependencies; `^` and `~` ranges | 4 or 6 | https://docs.npmjs.com/cli/v11/configuring-npm/package-json [source] |
| E08 | Web 项目文件命名 / MDN "Dealing with files" | O | MDN | Modified 2026-09-11 | Lowercase, no spaces, hyphens; most web servers are case-sensitive | 1, 4 | https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files [source] |
| E09 | EN 301 549 无障碍要求 | S (harmonised-standard candidate) | ETSI, CEN, CENELEC | **V4.1.1**, published 2026-09-02, includes WCAG 2.2; Official Journal citation pending | The European standard that turns accessibility law into testable requirements | 7 aw. | https://www.etsi.org/ [search: https://www.deque.com/blog/en-301-549-v4-1-1-is-final-what-changed-what-it-means-and-what-you-should-do/] |

### 4.6 APIs and data (F)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| F01 | HTTP 语义 / RFC 9110 (with 9111, 9112, 9113, 9114) | S | IETF | June 2022; RFC 9110, 9111, 9112 are Internet Standards; 9112 updated by RFC 9931 | Methods, status codes, headers, caching, the three wire versions. Bites in every API and every browser request | 4 (basics), 5 | https://www.rfc-editor.org/info/rfc9110 [source: https://www.rfc-editor.org/rfc/rfc9110.json] |
| F02 | HTTP API 问题详情 / RFC 9457 | S | IETF | Proposed Standard; document dated July 2023 (RFC Editor metadata says August 2023); obsoletes RFC 7807 | A standard JSON error body, media type `application/problem+json` | 5 | https://www.rfc-editor.org/info/rfc9457 [source] |
| F03 | OpenAPI 规范 | D | OpenAPI Initiative | **3.2.1**, 10 September 2026; based on JSON Schema 2020-12 | Machine-readable description of an HTTP API; FastAPI generates one | 5 | https://spec.openapis.org/oas/latest.html [source] |
| F04 | JSON Schema | D | JSON Schema organisation | **2020-12** is current | Vocabulary for validating JSON | 5 | https://json-schema.org/specification [source] |
| F05 | JSON 数据格式 / RFC 8259 | S | IETF | December 2017, Internet Standard | The JSON syntax | 2, 5 | https://www.rfc-editor.org/info/rfc8259 [source: https://www.rfc-editor.org/rfc/rfc8259.json] |
| F06 | OAuth 2.0、安全最佳实践与 OAuth 2.1 草案 | S | IETF OAuth working group | RFC 6749 (October 2012; updated by RFC 8252, 8996, 9700); RFC 9700 (January 2025, Best Current Practice); PKCE is RFC 7636; **OAuth 2.1 is still draft-17** of 31 October 2026 | Delegated authorisation. Teach 2.0 plus the security BCP; describe 2.1 as a draft consolidation | 7 | https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ [source] [source: https://www.rfc-editor.org/rfc/rfc6749.json] |
| F07 | OpenID Connect Core 1.0 | S | OpenID Foundation | Incorporating errata set 2, 15 December 2023, Final | Identity layer on top of OAuth 2.0 | 7 | https://openid.net/specs/openid-connect-core-1_0.html [source] |
| F08 | JSON Web Token / RFC 7519 与 RFC 8725 | S | IETF | RFC 7519 (May 2015; updated by 7797, 8725); RFC 8725 is BCP 225 (February 2020) | Token format plus best current practices | 7 | https://www.rfc-editor.org/info/rfc7519 [source: https://www.rfc-editor.org/rfc/rfc7519.json] |
| F09 | 日期时间表示 / ISO 8601 与 RFC 3339 | S | ISO TC 154; IETF | ISO 8601-1:2019, revision under way with publication targeted for 2028; RFC 3339 (July 2002) updated by RFC 9557 (April 2024) | Write `2026-11-19` and `2026-11-19T12:35:05Z`. Bites in logs, APIs, changelogs, file names | 2 | https://www.rfc-editor.org/info/rfc3339 [source: https://www.rfc-editor.org/rfc/rfc3339.json] [search: https://www.isotc154.org/decisions/urn:iso:tc154:resolution:plenary-45:P-2026-04] |
| F10 | Unicode 与 UTF-8 | S | Unicode Consortium; IETF | **Unicode 18.0.0** (2026-09-16); UTF-8 is RFC 3629 (November 2003, Internet Standard) | Text is code points; store and send UTF-8. Bites with Chinese file names, CSV files and source code | 2 | https://www.unicode.org/versions/latest/ [source: https://www.unicode.org/versions/Unicode18.0.0/] [source: https://www.rfc-editor.org/rfc/rfc3629.json] |
| F11 | SQL 标准 / ISO/IEC 9075 | S | ISO/IEC JTC 1/SC 32 | **SQL:2023**, with technical corrigenda to several parts dated 2026; no newer edition found | Every database implements a dialect; PostgreSQL documents its conformance | 5 | https://www.iso.org/standard/76583.html [memory for URL] [search: https://blog.ansi.org/sql-standard-iso-iec-9075-2023-ansi-x3-135/] |
| F12 | REST 架构风格与 API 惯例 | D | Fielding's dissertation (2000); vendor guidelines | Not a standard | Resources, uniform interface, statelessness; naming and status-code habits are conventions | 5 | [memory] |
| F13 | URI 与 UUID / RFC 3986, RFC 9562 | S | IETF | RFC 3986 (January 2005, Internet Standard); RFC 9562 (May 2024, obsoletes RFC 4122) | Identifier syntax | 5 | https://www.rfc-editor.org/info/rfc3986 [source: https://www.rfc-editor.org/rfc/rfc3986.json] [source: https://www.rfc-editor.org/rfc/rfc9562.json] |
| F14 | 规范性关键字 / RFC 2119 and RFC 8174 (BCP 14) | S | IETF | March 1997; May 2017 | Defines MUST, SHOULD, MAY. The basis of the course's 必须 / 推荐 / 参考 | 0 | https://www.rfc-editor.org/info/rfc2119 [source: https://www.rfc-editor.org/rfc/rfc2119.json] |
| F15 | TLS 1.3 | S | IETF | RFC 8446 (August 2018) is now obsoleted by RFC 9846 | Transport security under HTTPS | 7, 8 | https://www.rfc-editor.org/info/rfc8446 [source: https://www.rfc-editor.org/rfc/rfc8446.json] |
| F16 | Cookie / RFC 6265 | S | IETF | April 2011, Proposed Standard, not obsoleted | `Set-Cookie` and its attributes | 7 | https://www.rfc-editor.org/info/rfc6265 [source: https://www.rfc-editor.org/rfc/rfc6265.json] |
| F17 | security.txt 与 robots.txt / RFC 9116, RFC 9309 | S | IETF | April 2022 (Informational); September 2022 (Proposed Standard) | Well-known files for vulnerability contact and crawler rules | 8 | https://www.rfc-editor.org/info/rfc9116 [source: https://www.rfc-editor.org/rfc/rfc9116.json] |

### 4.7 Security (G)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| G01 | OWASP 十大风险 / OWASP Top 10 | D | OWASP | **2025** edition | A01 Broken Access Control; A02 Security Misconfiguration; A03 Software Supply Chain Failures; A04 Cryptographic Failures; A05 Injection; A06 Insecure Design; A07 Authentication Failures; A08 Software or Data Integrity Failures; A09 Security Logging and Alerting Failures; A10 Mishandling of Exceptional Conditions. Bites in interviews, audits, customer questionnaires | 7 (name it in 3) | https://top10.owasp.org/2025/ [source]; Simplified Chinese is listed among translations being added |
| G02 | 应用安全验证标准 / OWASP ASVS | D | OWASP | **5.0.0** (30 May 2025) | A checklist of verifiable security requirements | 7 | https://asvs.owasp.org/ [source] |
| G03 | OWASP 速查表系列 / Cheat Sheet Series | D | OWASP | Living; CC BY-SA 4.0 | Short how-to pages: authentication, session management, password storage, input validation, XSS, CSRF, SQL injection, secrets, logging, REST, Docker, access control | 5, 7 | https://cheatsheetseries.owasp.org/ [source] |
| G04 | CWE 最危险的 25 类弱点 / CWE Top 25 | D | MITRE | **2025** list (page updated 2025-12-15); no 2026 list published as of today | Top five: CWE-79 cross-site scripting, CWE-89 SQL injection, CWE-352 CSRF, CWE-862 missing authorisation, CWE-787 out-of-bounds write | 7 | https://cwe.mitre.org/top25/ [source: https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html] |
| G05 | 安全软件开发框架 / NIST SSDF, SP 800-218 | S (L for suppliers to the US government [memory]) | NIST | 1.1 is final; 1.2 is an initial public draft (2025-12-17); SP 800-218A (AI profile) is final | Practice groups: prepare the organisation, protect the software, produce well-secured software, respond to vulnerabilities | 8, 9 | https://csrc.nist.gov/projects/ssdf [source] [source: https://csrc.nist.gov/pubs/sp/800/218/r1/ipd] |
| G06 | 软件供应链等级 / SLSA | D | OpenSSF | **1.2**, Approved; adds a Source track to the Build track | Levels of evidence about how an artefact was built and where its source came from | 8 | https://slsa.dev/spec/ [source] |
| G07 | OpenSSF Scorecard | D | OpenSSF | 19 checks, one experimental | Automated 0 to 10 scoring: Branch-Protection, Code-Review, Dangerous-Workflow, Pinned-Dependencies, Token-Permissions, Security-Policy, Signed-Releases and others | 8 | https://github.com/ossf/scorecard [source] |
| G08 | OpenSSF 最佳实践徽章与 OSPS 基线 | D | OpenSSF | Badge programme running; OSPS Baseline **v2026.08.28** | Self-certified criteria for open-source projects; baseline controls by maturity level | 9, 10 | https://www.bestpractices.dev/en [source] [source: https://baseline.openssf.org/] |
| G09 | CVE 漏洞编号计划 | D | MITRE with CISA sponsorship [memory] | n/a | Public identifiers of the form `CVE-YYYY-NNNN` | 7, 8 | https://www.cve.org/ [memory] |
| G10 | 通用漏洞评分系统 / CVSS | S | FIRST | **4.0** (November 2023); no later version announced on the page | Severity score from 0 to 10 | 7 | https://www.first.org/cvss/ [source] |
| G11 | CISA 安全始于设计 / Secure by Design | O (government guidance with a voluntary pledge) | CISA and partner agencies | Page lists over 200 pledge signers; newest dated item is February 2025 | Vendors own security outcomes; secure defaults; MFA, logging and SSO without extra charge | 7 | https://www.cisa.gov/securebydesign [source] |
| G12 | 数字身份指南（口令部分）/ NIST SP 800-63B-4 | S (L for US federal systems [memory]) | NIST | Revision 4 final, July 2025 | Single-factor passwords at least 15 characters (8 if only one factor of MFA); accept at least 64; no composition rules; no periodic change; blocklist check; allow password managers; salted hashing; rate limiting | 7 | https://pages.nist.gov/800-63-4/sp800-63b.html [source] |
| G13 | OWASP 大模型应用十大风险 / Top 10 for LLM Applications | D | OWASP GenAI Security Project | **2025** | LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM06 Excessive Agency, LLM10 Unbounded Consumption and five more | 7 (prompt injection awareness in 1) | https://genai.owasp.org/llm-top-10/ [source] |
| G14 | 密钥推送保护 / GitHub push protection | P | GitHub | On by default for users pushing to public repositories | Blocks a push that contains a detected secret; for a leaked secret, revoke first, clean history later | 1 | https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection [source] |
| G15 | 信息安全管理体系 / ISO/IEC 27001 | L (by contract) | ISO/IEC | 27001:2022 with Amendment 1:2024; the transition from the 2013 edition ended 2025-10-31 | Certifiable management system. Bites in business-to-business sales | 9, 10 aw. | https://www.iso.org/standard/27001 [search: https://standards.iteh.ai/catalog/standards/iso/aa4c2608-9bf8-4c64-b7ca-ab3efafe67b9/iso-iec-27001-2022-amd-1-2024] |
| G16 | SOC 2 鉴证报告 | L (by contract) | AICPA | Five trust services categories; AICPA lists an exposure draft of proposed 2027 criteria dated 2026-11-16 | An auditor's report on a service organisation's controls. Bites for SaaS vendors | 10 aw. | https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2 [source] |
| G17 | 支付卡行业数据安全标准 / PCI DSS | L (card-brand contracts) | PCI SSC | **4.0.1** (June 2024); future-dated requirements mandatory since 2025-03-31; a request for comments on the next iteration ran June to July 2026 | Rules for anyone storing, processing or transmitting card data | 7 aw. | https://www.pcisecuritystandards.org/standards/pci-dss/ [search: https://blog.rsisecurity.com/pci-dss-v401-key-updates-you-need-to-know/] |

### 4.8 Law and privacy (H)

| ID | 中文名 / English | Cat | Issuer | Current status, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| H01 | 通用数据保护条例 / GDPR, Regulation (EU) 2016/679 | L | European Union | Applies since 2018-05-25; a procedural regulation on enforcement is in formal adoption | Lawful basis, data-subject rights, minimisation, breach notification; reaches non-EU services that target people in the EU [memory for scope] | 7 (name it in 5) | https://eur-lex.europa.eu/eli/reg/2016/679/oj [source: https://commission.europa.eu/law/law-topic/data-protection/legal-framework-eu-data-protection_en] |
| H02 | Cookie 同意规则 / ePrivacy Directive Article 5(3) | L | European Union; EDPB guidance | EDPB Guidelines 2/2023, version 2.0, 16 October 2024; the Digital Omnibus changes to cookie rules are not adopted (Council mandate agreed 2026-10-21) | Consent before storing or reading non-essential information on a device [memory for the article's wording] | 6, 7 | https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-22023-technical-scope-art-53-eprivacy-directive_en [source] [search: https://iapp.org/news/a/eu-member-states-finalize-digital-omnibus-negotiating-stance] |
| H03 | 网络弹性法案 / Cyber Resilience Act | L | European Union | In force 2024-12-10; reporting obligations since 2026-09-11; main obligations 2027-12-11; Commission guidance published 2026-07-27 | Security and vulnerability-handling duties for products with digital elements; CE marking; a special approach for open source | 8, 10 aw. | https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act [source] |
| H04 | 欧盟人工智能法 / EU AI Act, as amended by Regulation (EU) 2026/1744 | L | European Union | In force 2024-08-01; prohibitions and AI literacy since 2025-02-02; general-purpose AI rules since 2025-08-02; generally applicable 2026-08-02 including transparency rules; Annex III high-risk 2027-12-02; Annex I 2028-08-02; ninth prohibition from December 2026 | Risk-tiered duties for providers and deployers of AI systems. Bites when a product embeds AI | 7, 10 aw. | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai [source] |
| H05 | 欧洲无障碍法案 / European Accessibility Act, Directive (EU) 2019/882 | L | European Union | National laws were due June 2022; requirements apply from 2025-06-28 | Covers e-commerce, banking, e-books, transport, telephony, computers and more | 6, 7 | https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en [source]; application date [search: https://www.dwt.com/insights/2026/09/european-accessibility-act-ict-standards-update] |
| H06 | 加州消费者隐私法 / CCPA | L | State of California; CalPrivacy | Regulations package on automated decision-making, risk assessments and cybersecurity audits in effect since 2026-01-01; Delete Act regulations in effect since 2026-01-01 | Consumer rights to know, delete, opt out | 7 aw. | https://cppa.ca.gov/regulations/ [source] |
| H07 | 个人信息保护法 / PIPL | L | 全国人大常委会 | Adopted 2021-08-20; in force 2021-11-01; 8 chapters, 74 articles | Legal bases for processing (Art. 13), reach beyond mainland China (Art. 3), fines up to RMB 50 million or 5% of the previous year's turnover (Art. 66) | 7 (name it in 5) | https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm [source] (zh is the original) |
| H08 | 网络安全法 / Cybersecurity Law | L | 全国人大常委会 | Amended 2025-10-28; amended text in force 2026-01-01; adds an article on AI | Duties of network operators; legal basis of 等保 [memory] | 7, 8 aw. | https://www.cac.gov.cn/2026-01/02/c_1769093523928606.htm [source: official site, expert commentary on the amendment] |
| H09 | 数据安全法 / Data Security Law | L | 全国人大常委会 | In force 2021-09-01 [memory] | Data classification; important data | 7 aw. | [memory] |
| H10 | 网络数据安全管理条例 | L | 国务院令第 790 号 | Published 2024-09-30; in force 2025-01-01; 9 chapters, 64 articles | Implementing rules for network data handling | 7 aw. | https://www.gov.cn/zhengce/content/202409/content_6977766.htm [source] |
| H11 | 等保 2.0 / MLPS 2.0, GB/T 22239-2019 | S made binding by law | 国家标准委; public security organs supervise | 现行; issued 2019-05-10; effective 2019-12-01; five protection levels [search] | Baseline security requirements per level. Bites for systems operated in mainland China; customers ask for level 2 or level 3 | 8 aw. | https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=BAFB47E8874764186BDB7865E8344DAF [source] |
| H12 | ICP 备案 | L | 国务院; 工信部 and provincial communications administrations | 《互联网信息服务管理办法》, State Council Decree 292 of 2000, revised 2011; a second revision by a State Council decision of 2024-12-06 [search]; a new revision draft was published for comment on 2026-07-03 (comments closed 2026-08-02); app filing since a 2023 ministry notice [search] | Commercial services need a licence and non-commercial ones a filing; without it a service may not operate, and an unfiled site can be ordered closed. Applies to services hosted in mainland China; cloud providers require the filing before serving a domain [search] | 8 (deployment choice) | https://www.cac.gov.cn/2000-09/30/c_126193701.htm [source] [source: https://www.cac.gov.cn/2026-07/03/c_1784822399677167.htm] |
| H13 | 个人信息安全规范 / GB/T 35273-2020 | S (推荐性国标) | 国家标准委 | 现行; issued 2020-03-06; effective 2020-10-01 | Detailed practice for handling personal information | 7 aw. | https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=35273 [source] |
| H14 | AI 生成内容标识 / 《人工智能生成合成内容标识办法》 and GB 45438-2025 | L | 国家网信办 and three other bodies; 国家标准委 | Both effective 2025-09-01; GB 45438-2025 is a mandatory national standard, 现行 | Explicit and implicit labels on AI-generated text, images, audio and video | 7, 10 aw. | https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2=45438 [source] [search: https://www.news.cn/tech/20250319/a572ec4366f149c1b0b04a07ebf4931b/c.html] |
| H15 | 信创 / domestic IT substitution | L (procurement policy) | State bodies | No single public statute found; widely reported target is substitution in central state-owned enterprises by the end of 2027 | Shapes stack choices in government, state-owned and financial projects | 10 aw. | [search: https://www.cls.cn/subject/3185] |
| H16 | 著作权与开源许可证 / copyright and software licences | L | national copyright law; licence texts | n/a | No licence means all rights reserved; GitHub's terms still let others view and fork a public repository; making it private later does not remove forks or clones | 1, 3 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository [source] |

### 4.9 Operations (I)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| I01 | 十二要素应用 / The Twelve-Factor App | D | Originally Heroku | Page states last updated 2017; the site now has blog and community links | Configuration in the environment, stateless processes, logs as streams, parity between development and production, and eight more | 3 (config), 8 | https://12factor.net/ [source]; zh: https://12factor.net/zh_cn/ |
| I02 | OCI 镜像规范 / OCI Image Format Specification | S | Open Container Initiative | v1.1.1 is the latest release shown (year not visible in the fetch) | Layout and manifest of a container image | 8 | https://github.com/opencontainers/image-spec/releases [source] |
| I03 | Google SRE 书籍 | O | Google | Four titles listed; three readable online | Service level indicators, objectives and agreements; error budgets; on-call | 8 | https://sre.google/books/ [source]; the vocabulary summary is [memory] |
| I04 | 无责复盘 / blameless postmortem | O, then T | Google SRE; each team | n/a | A written review of an incident that looks for causes in the system, not for a culprit | 2 (personal mistake log), 8 | https://sre.google/books/ [memory] |

### 4.10 Licensing (J)

| ID | 中文名 / English | Cat | Issuer | Current version, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| J01 | OSI 认可许可证与开源定义 | D | Open Source Initiative | Living list; the page also references the Open Source AI Definition 1.0 | "Open source" means a licence approved against the Open Source Definition | 3 | https://opensource.org/licenses [source] |
| J02 | SPDX 许可证标识符 | S (ISO/IEC 5962:2021) | SPDX, Linux Foundation | License List **3.29.0** (2026-09-16); specification 3.0; `GPL-3.0` is deprecated in favour of `GPL-3.0-only` and `GPL-3.0-or-later` | Short identifiers used in `pyproject.toml`, `package.json` and file headers | 3 | https://spdx.org/licenses/ [source] [source: https://spdx.dev/use/specifications/] |
| J03 | choosealicense.com | P | GitHub with the community | Living | Follow your community's licence; MIT for simple and permissive; GPLv3 to require shared improvements | 1 (awareness), 3 | https://choosealicense.com/ [source]; the site menu offers a 中文 version under `/zh/` |

### 4.11 AI-assisted development (K)

| ID | 中文名 / English | Cat | Issuer | Current status, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| K01 | AGENTS.md 约定 | D (emerging) | Agentic AI Foundation under the Linux Foundation | No version number; the site reports use by over 60k projects | Plain Markdown instructions for coding agents; the nearest file wins; a direct user prompt overrides it | 1 | https://agents.md/ [source] |
| K02 | CLAUDE.md 与设置文件 / Claude Code instructions and settings | P | Anthropic | Living docs | Standing instructions live in `CLAUDE.md`; settings precedence is managed, command line, project-local, shared project, user; permission rules allow, ask, deny | 1 | https://code.claude.com/docs/en/settings [source]; the sibling brief `ai-pairing-norms` covers details |
| K03 | AI 署名尾注 / AI attribution trailers | P, T | tool vendors; each project | No cross-project standard | This session's harness asks for a `Co-Authored-By:` trailer naming the model [local]; the Apache Software Foundation suggests `Generated-by:`; projects differ | 1 | https://www.apache.org/legal/generative-tooling.html [source] |
| K04 | Linux 内核 AI 编码助手规则 | O | Linux kernel community | Documentation of 7.4.0-rc3 | Follow the normal process; stay GPL-2.0-only compatible; an AI agent must not add `Signed-off-by`; the human submitter reviews and takes responsibility | 9 aw. | https://docs.kernel.org/process/coding-assistants.html [source] |
| K05 | Apache 生成式工具指引 | O | Apache Software Foundation | Living; text refers to August 2026 | Conditions for contributing AI output; publicly published AI-generated text is labelled unless a person reviewed it and takes responsibility | 9 | https://www.apache.org/legal/generative-tooling.html [source] |
| K06 | Linux 基金会生成式 AI 政策 | O | Linux Foundation | Living | AI-generated contributions are allowed if the tool's terms and any third-party material permit; projects may set stricter rules; follow your employer's policy | 9 | https://www.linuxfoundation.org/legal/generative-ai [source] |
| K07 | OpenSSF AI 代码助手安全指令指南 | D | OpenSSF working groups | Published 2025-08-01 | The developer stays accountable; keep review, tests and static analysis; assume flaws; verify claims; beware invented package names; ask the assistant to criticise and improve its own output | 1 (principles), 7 | https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions [source] |
| K08 | AI 素养与透明度义务 / AI literacy and transparency duties | L | European Union | AI literacy duty since 2025-02-02; transparency rules since August 2026 | Organisations ensure staff understand the AI they use; people are told when they face AI or AI-generated content in defined cases [memory for detail] | 7 aw. | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai [source] |

### 4.12 Organisation style guides and playbooks (L)

| ID | 中文名 / English | Cat | Issuer | Current status, as verified | What it says; where it bites | Stage | Canonical URL and basis |
|---|---|---|---|---|---|---|---|
| L01 | Google 风格指南 / Google Style Guides | O | Google | Living; 24 guides including Python, TypeScript, JavaScript, HTML/CSS, Shell, Markdown, JSON; CC-BY 3.0 | Conventions that keep a very large codebase readable | 2 (Python), 6 (TypeScript) | https://google.github.io/styleguide/ [source]; a community Chinese translation exists [memory] |
| L02 | Google 工程实践（代码评审）/ Google Engineering Practices | O | Google | Living | Approve a change once it clearly improves overall code health; the style guide settles style; mark optional remarks "Nit:"; facts outrank opinions | 1 (reviewing an AI-made change), 2 | https://google.github.io/eng-practices/review/reviewer/standard.html [source] |
| L03 | Airbnb JavaScript 风格指南 | O | Airbnb | Repository with about 148k stars; maintenance status not stated on the page | ES2015+ conventions with matching ESLint configurations | 6 aw. | https://github.com/airbnb/javascript [source] |
| L04 | 阿里巴巴 Java 开发手册 | O | Alibaba | 黄山版, released 2022-02-03; tooling repository under Apache-2.0 | Rules graded 强制 / 推荐 / 参考, each with 说明, 正例, 反例; seven areas from coding rules to MySQL and design [search] | 0 (model for rule cards), 5 (database rules as contrast) | https://github.com/alibaba/p3c [source] (zh is the original) |
| L05 | GitLab 手册 / GitLab Handbook | O | GitLab | Living; the page I tried redirected to a sign-in | A public example of a whole company's written working agreements | 9 | https://handbook.gitlab.com/ [memory] |
| L06 | Dropbox 工程职级框架 / Dropbox Engineering Career Framework | O | Dropbox | Public | Level IC1 expectations (section 5) | 0, 9 | https://dropbox.github.io/dbx-career-framework/ic1_software_engineer.html [source] |

Entry count: A 14, B 15, C 15, D 9, E 9, F 17, G 17, H 16, I 4, J 3, K 8, L 6 = 133.

## 5. "行业要求" in the employment sense: what teams expect of a junior full-stack engineer

Label these **岗位期望** in the course so they are never mistaken for legal duties. They are enforced by interviewers, reviewers and managers, not by regulators.

### 5.1 Evidence read today

| Source | What it shows | Basis |
|---|---|---|
| Indeed Hiring Lab, 2026-07-23 (US postings) | In Q1 2026 only **4.5%** of software-development postings were entry-level and **69.3%** were senior; entry-level postings across the economy fell 7.5% year on year to May 2026; entry-level software postings tend to ask for a bachelor's degree. Levels are assigned by text classification of duties, with typical bands of 0 to 1, 2 to 4 and 5+ years | [source: https://hiringlab.indeed.com/2026/07/23/the-labor-market-is-tilting-toward-seniority/] |
| Indeed Hiring Lab, 2026-07-08 (US) | Software-development postings rose almost 15% since February 2025 while all postings fell 7%, yet remain about 27.5% below February 2020; senior roles account for 71% of the May 2025 to May 2026 increase and AI-titled roles for 37% (overlapping groups) | [source: https://hiringlab.indeed.com/2026/07/08/ai-and-job-postings-from-destruction-to-creation/] |
| Stanford Digital Economy Lab, 2026-08-12 (US payroll data to June 2026) | Employment of workers aged 22 to 25 in highly AI-exposed occupations is about 19% below where it would be had it tracked less-exposed peers (15% a year earlier). The adjustment comes mainly through less hiring. Declines concentrate where AI use automates and not where it complements. The authors call the findings descriptive, not causal | [source: https://digitaleconomy.stanford.edu/news/canariesaug26/] |
| Stack Overflow Developer Survey 2026 | 30,903 responses from 169 countries. Trust in AI output: 48.0% trust it when they can easily verify it; 16.3% for many tasks but not important decisions; 16.3% for low-risk tasks only; 12.3% do not trust it for most tasks; 6.6% trust it for many tasks including important decisions | [source: https://survey.stackoverflow.co/2026/] |
| Stack Overflow 2026, press coverage | Most-used languages: JavaScript 62%, SQL 58.4%, HTML/CSS 58.2%, Python 58%; about 66% use coding assistants or agents | [search: https://itbrief.co.uk/story/stack-overflow-survey-shows-developers-trust-ai-with-caveats] |
| GitHub Octoverse 2026 (published 2026-10-28), press coverage | TypeScript, Python, JavaScript lead by monthly contributors; agents started more than 40% of pull requests in September 2026 | [search: https://www.techrepublic.com/article/news-github-octoverse-2026-typescript-rust/] |
| JetBrains Developer Ecosystem 2025, press coverage | 24,534 developers; 85% use AI tools regularly | [search: https://www.theregister.com/2025/10/21/massive_jetbrains_dev_survey] |
| Dropbox Engineering Career Framework, level IC1 | Executes defined tasks with guidance; writes clear, tested, documented code; takes part in code review; reads code written by others; owns commitments and mistakes; asks when unclear; escalates when stuck | [source: https://dropbox.github.io/dbx-career-framework/ic1_software_engineer.html] |
| SFIA 9, level 2 | Works on routine tasks under review; asks clarifying questions; understands the organisation's security, privacy and ethics rules; applies new learning | [source: https://sfia-online.org/en/sfia-9/responsibilities/level-2] |
| Google Engineering Practices | Reviews aim at steadily improving code health; the style guide decides style; data outranks opinion | [source: https://google.github.io/eng-practices/review/reviewer/standard.html] |
| OpenSSF guide for AI code assistants | The developer answers for AI-written code and reviews it like a colleague's | [source: https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions] |
| roadmap.sh full-stack roadmap ("in 2026") | HTML, CSS, JavaScript; a UI framework; a back-end language; a full-stack framework; SQL; Git and REST APIs; a portfolio | [source: https://roadmap.sh/full-stack] |

Limits: the hiring and employment figures are for the United States. I found no comparable primary analysis for the Chinese-language market today.

### 5.2 The expectations, phrased as norms

Each line is 岗位期望; the bracket names the evidence rows above.

1. You are expected to finish small, well-defined tasks reliably and to say early when you are blocked or unsure. [Dropbox IC1; SFIA 2]
2. You are expected to work through Git and pull requests without help: branch, commit in readable steps, open a pull request, respond to review, resolve a merge conflict. [roadmap.sh; Dropbox IC1; Octoverse]
3. You are expected to follow the team's style guide and let tools enforce it, instead of arguing taste. [Google Engineering Practices]
4. You are expected to test your own change and say how you tested it. [Dropbox IC1]
5. You are expected to read and navigate code you did not write. [Dropbox IC1]
6. You are expected to use AI assistants as a normal tool and to verify what they produce; responsibility for the result stays with you. [Stack Overflow 2026; OpenSSF; section 4.11]
7. You are expected to know basic security hygiene: no secrets in repositories, two-factor authentication, dependency awareness, the OWASP Top 10 by name. [SFIA 2; G01; G14]
8. You are expected to write clearly: pull-request descriptions, README files, questions that include what you tried and the exact error. [Dropbox IC1; SFIA 2; C14]
9. You are expected to own mistakes and take part in team routines such as planning, triage and incident follow-up. [Dropbox IC1]
10. You are expected to keep learning and to act on feedback. [Dropbox IC1; SFIA 2]
11. You are expected to show evidence. With entry-level openings at a few percent of postings and hiring tilted towards seniority, a junior candidate is judged on visible, review-ready work: repositories with history, tests, documentation and decisions. [Indeed Hiring Lab; Stanford] (The inference from the data to "portfolio matters more" is mine.)
12. You are expected to be productive in the mainstream stack: JavaScript or TypeScript, Python, SQL, HTML and CSS, HTTP APIs. [Stack Overflow 2026 coverage; Octoverse coverage; roadmap.sh]

Teaching note: present item 11 honestly in stage 0. The data describe a harder entry market, and the authors of the Stanford paper do not claim AI is the proven cause.

## 6. Stage 0 and stage 1: concrete rules with category and source

Level: 必 = 必须, 荐 = 推荐, 参 = 参考. Cat codes as in section 3.1. Rules marked "course" are team agreements of this learning workspace: the builders choose them, and the card should say so.

### 6.1 File and folder naming

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| N1 | Name files and folders in lowercase ASCII letters, digits and hyphens; no spaces | 荐 | O | Google filenames guide [source: https://developers.google.com/style/filenames]; MDN [source: https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files] |
| N2 | Python modules and packages use lowercase with underscores (`exchange_rates.py`), because a hyphen cannot appear in an import name | 必 for importable files | S | PEP 8 [source: https://peps.python.org/pep-0008/]; `ruff rule N999` exists in ruff 0.17.2 [local] |
| N3 | Never keep two names that differ only by case, and never rely on case to tell files apart | 必 | P | gitfaq [source: https://git-scm.com/docs/gitfaq]; this volume is case-insensitive [local] |
| N4 | Keep the conventional upper-case names: `README.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS` | 荐 | P | GitHub docs [source: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file]; Keep a Changelog [source: https://keepachangelog.com/en/1.1.0/] |
| N5 | Avoid Chinese and other non-ASCII characters in names inside a repository; write Chinese freely inside the files | 荐 | O | Google filenames guide [source]; by default `git status` printed a Chinese file name as octal escapes in my test [local] |
| N6 | Put dates in names and logs as `YYYY-MM-DD` | 荐 | S | RFC 3339 [source: https://www.rfc-editor.org/rfc/rfc3339.json]; Keep a Changelog [source] |
| N7 | Number decision records: `docs/decisions/0001-title-with-dashes.md` | 参 | D | MADR 4.0.0 [source: https://adr.github.io/madr/] |

### 6.2 Where code lives on the machine

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| W1 | Do not keep a Git repository inside a cloud-synced folder (iCloud Desktop or Documents, OneDrive, Dropbox); move work between devices with push and pull | 必 | P | gitfaq [source: https://git-scm.com/docs/gitfaq]; Apple describes Desktop and Documents as stored in and synced through iCloud Drive when the option is on (article published 2026-09-14) [source: https://support.apple.com/en-us/109344]; reported damage on iCloud-synced Desktops [memory] |
| W2 | Keep all projects under one parent folder outside sync; on macOS use `~/Developer` | 荐 | P | macOS ships a Developer folder icon [local]; no Apple document mandates it [search]. `~/code`, `~/src`, `~/Projects` are equally valid: that choice is preference |
| W3 | One project, one folder, one repository; never run `git init` in the home folder; do not nest repositories | 荐 | D | [memory] |
| W4 | Suffixing a folder with `.nosync` to stop iCloud syncing it is a workaround, not a documented Apple feature; do not build a workflow on it | 参 | X | Some projects already use `.venv.nosync`; I found no Apple documentation for the suffix today [memory] |

### 6.3 Terminal safety

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| T1 | Before any command that deletes or overwrites, check where you are (`pwd`, `ls`); `rm` is permanent and bypasses the Trash; `rm -r` removes a whole tree | 必 | O | MDN command-line course, modified 2026-09-12 [source: https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line] |
| T2 | Do not run a command you cannot explain; try complex commands on a copy or in a test folder first | 必 | O | MDN [source: same] |
| T3 | Do not use `sudo` for everyday development; Homebrew warns against running `brew` with it | 必 | P | Homebrew FAQ [source: https://docs.brew.sh/FAQ] |
| T4 | Never type a password or token into a URL or a command line that lands in history; let a credential helper store it | 必 | P | gitfaq [source: https://git-scm.com/docs/gitfaq] |
| T5 | Read every command an AI assistant proposes before approving it; keep deny rules for secret files such as `.env`; prefer per-project settings over global ones | 必 | P, T (course) | Claude Code settings docs [source: https://code.claude.com/docs/en/settings]; OpenSSF guide [source: https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions] |
| T6 | Install scripts piped from the network into a shell are acceptable only from a project's official documentation, after reading them | 荐 | D | [memory] |

### 6.4 Markdown and README

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| M1 | Write project text in Markdown; GitHub renders CommonMark plus the GFM extensions | 荐 | D, P | CommonMark 0.31.2 [source: https://spec.commonmark.org/]; GFM [source: https://github.github.com/gfm/] |
| M2 | Every repository has a `README.md` at its root that says what the project does, why it is useful, how to start, where to get help, who maintains it | 必 (course); 荐 in general | P | GitHub docs [source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes] |
| M3 | One top-level heading; heading levels go up one at a time; fenced code blocks name their language; the file ends with one newline | 荐 | P | markdownlint rules MD025, MD001, MD040, MD047 [source: https://github.com/DavidAnson/markdownlint] |
| M4 | Link to other files in the repository with relative links | 荐 | P | GitHub docs [source: about-readmes URL above] |
| M5 | In Chinese text put a space between Chinese and Latin letters or digits and use full-width punctuation | 参 | D | 中文文案排版指北 [source: https://github.com/sparanoid/chinese-copywriting-guidelines] |
| M6 | Organise growing documentation by purpose: tutorial, how-to, reference, explanation | 参 | D | Diátaxis [source: https://diataxis.fr/] |

### 6.5 Git basics

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| G1 | Set `user.name` to your personal name and `user.email` to an address registered with your GitHub account before the first commit | 必 | P | gitfaq [source]; GitHub docs [source: https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address] |
| G2 | The default branch is called `main` | 荐 | P | BreakingChanges [source: https://git-scm.com/docs/BreakingChanges]; `git init` gives `main` here [local] |
| G3 | Look before you commit: `git status`, then `git diff --staged` | 荐 | D | Pro Git [memory for the wording; book verified at https://git-scm.com/book/zh/v2] |
| G4 | Commit small, self-contained changes; do not commit dependencies, build output or large binaries | 荐 | P | gitfaq [source] |
| G5 | Store text as UTF-8 without BOM and with LF line endings | 荐 | P | gitfaq [source] |
| G6 | Do not rewrite history that others already have; never force-push a shared branch | 必 in a team | T | GitHub rulesets can block force pushes [memory]; see the sibling brief `github-collab-ci` |
| G7 | The remote is your backup and your sync channel; push at the end of every working session | 荐 (course) | T | follows from W1 [source: gitfaq] |

### 6.6 Commit messages

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| C1 | First line is a summary of at most 50 characters; then a blank line; then a body that explains what changed and why | 荐 | D | git-commit manual, which calls it a good idea and not a requirement [source: https://git-scm.com/docs/git-commit] |
| C2 | Start the summary with a Conventional Commits type: `feat:`, `fix:`, and by common tooling convention `docs:`, `refactor:`, `test:`, `chore:`, `ci:`, `build:`, `perf:`, `style:` | 荐; 必 once the course repository enforces it | D, then T | Conventional Commits 1.0.0; only `feat` and `fix` are defined by the specification [source: https://www.conventionalcommits.org/en/v1.0.0/] |
| C3 | One language per repository for commit messages (Chinese or English), chosen once | 荐 (course) | T | team agreement; no external source |
| C4 | Trailers go at the end after a blank line: `Co-authored-by:`, `Signed-off-by:` | 参 | P | [source: https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors]; [source: https://git-scm.com/docs/git-commit] |
| C5 | A Chinese character takes two columns in a terminal; keep a Chinese summary to about 25 characters | 参 | X (my inference) | width check script tested [local] |

### 6.7 .gitignore and secrets

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| I1 | Patterns every contributor needs go in the committed `.gitignore`; your own editor and system files go in the global ignore file | 荐 | P | gitignore manual [source: https://git-scm.com/docs/gitignore]; the global file is whatever `core.excludesfile` names (default `~/.config/git/ignore`) |
| I2 | Start from the GitHub templates (language template plus `Global/macOS.gitignore`) and then read what you added | 参 | P | [source: https://github.com/github/gitignore] |
| I3 | Adding a pattern does not untrack a file already committed; use `git rm --cached <file>` | fact | P | gitignore manual [source] |
| I4 | Never commit secrets: `.env` files, keys, tokens, passwords | 必 | L where a contract or policy applies; otherwise P | GitHub blocks detected secrets on pushes to public repositories by default [source: https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection] |
| I5 | If a secret was committed or pushed, treat it as compromised: revoke and replace it first; cleaning history comes afterwards and is not sufficient alone | 必 | P | [source: https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/remediating-a-leaked-secret] |

### 6.8 GitHub account security

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| A1 | Turn on two-factor authentication on day one with a TOTP app as the primary method, and store the recovery codes offline | 必 | L (platform policy) | Mandatory for selected code-contributing accounts since March 2023: 45-day enrolment, 7-day grace, then no access until enabled; TOTP recommended as primary; passkeys and security keys not yet accepted as primary 2FA [source: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication] |
| A2 | Add a passkey for sign-in | 荐 | P | Passkeys resist phishing and satisfy password and 2FA at sign-in [source: https://docs.github.com/en/authentication/authenticating-with-a-passkey/about-passkeys] |
| A3 | Use SMS only where nothing else works | 荐 | P | [source: mandatory-2FA page above] |
| A4 | Use a unique password kept in a password manager | 荐 | S (by analogy) | NIST SP 800-63B-4 tells services to allow password managers and not to force rotation [source: https://pages.nist.gov/800-63-4/sp800-63b.html] |
| A5 | Decide whether commits show your real e-mail address; GitHub offers a no-reply address | 参 | P | [source: setting-your-commit-email-address URL above] |

### 6.9 SSH keys, HTTPS tokens, GitHub CLI

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| S1 | Never use the account password for Git operations; it no longer works | fact | P | [source: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github] |
| S2 | Choose one path and learn it well. Path A: HTTPS with GitHub CLI (`gh auth login`) or Git Credential Manager, which GitHub recommends for remembering HTTPS credentials. Path B: SSH with an Ed25519 key, a passphrase, and the macOS keychain | 荐 | P | [source: https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git]; [source: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent] |
| S3 | On a fresh Mac `gh` is absent, there is no SSH key yet, and Apple Git already has the `osxkeychain` helper; path A needs the learner to install `gh` with Homebrew, path B needs a new key. HTTPS works behind firewalls, SSH may be blocked | context | P | [local]; [source: about-authentication URL above] |
| S4 | If you create a token by hand, make it fine-grained, minimal in scope, with an expiry | 荐 | P | GitHub recommends fine-grained over classic tokens [source: about-authentication URL above] |
| S5 | Generate keys as `ssh-keygen -t ed25519 -C "email"`; RSA 4096 only for systems without Ed25519; DSA is no longer accepted | 荐 | P | [source: generating-a-new-ssh-key URL above] |

### 6.10 Commit signing

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| V1 | First make commits work if signing is half-configured (card GIT-007 in section 7) | 必 | P | [local] |
| V2 | Signing is optional for personal learning repositories. It becomes 必须 where a repository's administrators require signed commits | 参, or 必 by rule | P, then T | [source: https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification] |
| V3 | "Verified" means GitHub checked a signature against a key registered to an account. Commits made in GitHub's web editor are signed by GitHub. A "rebase and merge" on GitHub produces commits GitHub cannot sign for you | fact | P | [source: same] |
| V4 | If you sign, start with SSH signing: simplest to set up, needs Git 2.34 or later, and reuses an SSH key registered as a signing key. Use GPG when you need key expiry and revocation; S/MIME is for organisations that issue certificates | 荐 | P | [source: same]; [source: https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key]; SSH signing worked here with OpenSSH 10.5 [local] |
| V5 | Signing is uncommon: recent studies put signed commits between about 5% and 18% depending on the sample, with one finding that under 6% of developers ever signed with a key they hold; nearly all signatures are PGP, about 1% SSH | background | n/a | [search: https://www.ndss-symposium.org/wp-content/uploads/9D-f0613-holtgrave.pdf] [search: https://arxiv.org/pdf/2604.14014] [search: https://arxiv.org/pdf/2607.06194] (which figure belongs to which paper was not checked) |

### 6.11 Private and public repositories

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| P1 | Create learning repositories as private; make one public only after checking for secrets and personal data | 荐 (course) | T | Public means visible to everyone on the internet [source: https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories] |
| P2 | A public repository without a licence is still "all rights reserved"; add a licence if you want others to reuse it | fact; 荐 | L | [source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository]; [source: https://choosealicense.com/] |
| P3 | Switching a repository to private later does not remove existing forks or clones | fact | P | [source: licensing URL above] |
| P4 | A public repository should have `SECURITY.md` and the free scanning features turned on | 参 | P | [source: about-repositories URL above] |

### 6.12 Asking good questions

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| Q1 | Search the documentation and the exact error text before asking | 荐 | D | Raymond and Moen, revision 3.10 [source: http://www.catb.org/~esr/faqs/smart-questions.html] |
| Q2 | A question states the goal, what you did, the exact error as text, the environment and versions, and what you already tried | 荐 | D | [source: same] |
| Q3 | Describe the goal and not only the step you are stuck on | 荐 | D | [source: same, section "Describe the goal, not the step"] |
| Q4 | Reduce the problem to the smallest example that still fails | 荐 | P | Stack Overflow help centre [memory] |
| Q5 | Report back what fixed it | 荐 | D | [source: catb.org page, section "Follow up with a brief note on the solution"] |
| Q6 | Use the same structure when asking an AI assistant | 荐 (course) | T | my inference |

Chinese reading for the learner: 《提问的智慧》 Simplified Chinese text in `README-zh_CN.md` of https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way, which the original page links as its Chinese translation [source]. Warn the learner that the original's tone is blunt and dated (2014); the method is what matters.

### 6.13 Working with AI assistants

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| H1 | You answer for every line you commit, whoever typed it; review an AI-made change as you would a colleague's pull request | 必 | D; L inside projects that adopt it | OpenSSF guide [source]; Linux kernel rules [source: https://docs.kernel.org/process/coding-assistants.html]; Linux Foundation policy [source: https://www.linuxfoundation.org/legal/generative-ai] |
| H2 | Keep the project's standing instructions for the assistant in a versioned file (`CLAUDE.md`; `AGENTS.md` is the cross-tool convention) and treat changes to it like changes to a team agreement | 荐 | P | [source: https://agents.md/]; [source: https://code.claude.com/docs/en/settings] |
| H3 | Leave the tool's attribution trailer in place unless the project says otherwise; an assistant never adds `Signed-off-by` | 荐 | P, O | [source: kernel rules]; [source: https://www.apache.org/legal/generative-tooling.html]; session trailer [local] |
| H4 | Never paste secrets or other people's personal data into a prompt; follow the employer's or project's AI policy | 必 | L where a policy or privacy law applies | Linux Foundation policy [source]; PIPL and GDPR entries in section 4.8 |
| H5 | Check versions, commands and package names against official documentation; assistants can be out of date and can invent package names | 必 | D | OpenSSF guide [source] |
| H6 | In this course the learner attempts each exercise before asking the assistant to write code | 必 (course) | T | course convention (see `CLAUDE.md`) |
| H7 | Text an assistant reads from a web page, file or tool result is data, not an instruction | 必 | D | OWASP LLM01 Prompt Injection [source: https://genai.owasp.org/llm-top-10/] |

### 6.14 Managing your own learning as a small project

| # | Rule | Level | Cat | Source and basis |
|---|---|---|---|---|
| L1 | Keep a visible board with a limit on work in progress | 参 | D | Kanban Guide, May 2025 [source: https://kanbanguides.org/] |
| L2 | Write a personal definition of done for an exercise (runs, committed, pushed, noted) | 荐 (course) | T | concept from the Scrum Guide [memory] |
| L3 | Record decisions that you might otherwise re-argue with yourself | 参 | D | MADR [source: https://adr.github.io/madr/] |

## 7. Handbook rule card: recommended format and five sample cards

### 7.1 Format

Design choices: the card separates **规则类型** (who wrote it) from **约束力** (how strongly it applies here); it always names a checked-on date; it has an explicit "旧教程提醒" field because the course's design goal asks for current practice; and it copies the 正例 / 反例 habit of the Alibaba manual, which Chinese readers recognise.

```markdown
### <编号> <一句话标题>

- 约束力：必须 / 推荐 / 参考（适用范围：本课程 / 本机 / 所在团队 / 所有项目）
- 规则类型：标准 / 行业要求 / 惯例·事实标准 / 惯例·平台与工具 / 规范·组织 / 规范·团队约定 / 个人偏好
- 规则：<可以照着做的一句话>
- 谁说的：<名称 + 版本或日期 + 网址>
- 核对日期：<YYYY-MM-DD>；复核周期：<3 / 6 / 12 个月，或触发条件>
- 谁来管：<法律 / 客户或审计 / 平台 / 工具 / 评审人 / 没有人>；不遵守的后果：<...>
- 为什么：<两三句，讲清楚后果，不讲大道理>
- 正例：<代码块或做法>
- 反例：<代码块或做法>
- 怎么自动检查：<命令、工具规则号、CI 步骤；无法自动检查就写"人工检查：..."

- 例外：<什么时候可以不遵守，谁有权决定>
- 旧教程提醒：<老资料里的过时说法 → 现在的做法>
- 教学阶段：<路线图阶段号>
```

Numbering suggestion: a topic prefix plus a number (`FND` foundations, `GIT`, `GH`, `PY`, `WEB`, `API`, `SEC`, `OPS`, `TEAM`, `AI`). Keep one card per file under `handbook/rules/` so a rule can be linked, reviewed and changed by pull request like any other team agreement.

### 7.2 Sample card 1

```markdown
### FND-001 代码仓库不放在云同步文件夹里

- 约束力：必须（适用范围：所有项目）
- 规则类型：惯例·平台与工具（Git 官方文档的明确建议）
- 规则：所有 Git 仓库放在不被 iCloud、OneDrive、Dropbox 等同步的本地目录里，macOS 上统一放在 `~/Developer/`；多台设备之间只用 `git push` / `git pull` 同步。
- 谁说的：Git 官方 FAQ（gitfaq，最后更新于 Git 2.53.0）https://git-scm.com/docs/gitfaq ；Apple 支持文章 109344（讲"桌面"与"文稿"文件夹存入 iCloud 云盘并在设备间同步，2026-09-14 发布）https://support.apple.com/en-us/109344
- 核对日期：2026-11-19；复核周期：12 个月，或 macOS 大版本升级后
- 谁来管：没有人会拦你；不遵守的后果：仓库损坏或出现莫名其妙的错误，而且很难排查。
- 为什么：云同步是"一个文件一个文件、随时"同步，它不懂 Git 仓库的内部结构，可能造成对象缺失、分支指针损坏、冲突副本。有人已经遇到过：桌面由 iCloud 同步时，虚拟环境里的文件被加上隐藏标记，Python 找不到已安装的包；还会出现 `file 2.csv` 这样的冲突副本。
- 正例：

      ~/Developer/my-first-repo

- 反例：

      ~/Desktop/my-first-repo           （开了 iCloud 桌面同步时）
      ~/Documents/projects/demo

- 怎么自动检查：在仓库根目录运行

      case "$(pwd -P)" in
        "$HOME/Desktop"/*|"$HOME/Documents"/*|*"/Mobile Documents/"*|*"/Library/CloudStorage/"*)
          echo "警告：当前目录可能被云同步" ;;
        *) echo "OK" ;;
      esac

- 例外：不含 `.git` 的草稿、截图、PDF 可以放云盘。想要备份，用远程仓库，不用云盘。
- 旧教程提醒：很多入门教程让你"在桌面新建一个项目文件夹"。在开启了 iCloud 桌面同步的 Mac 上，这个做法有风险。
- 教学阶段：0–1
```

Basis for the builders: gitfaq [source]; Apple article [source]; reported damage on iCloud-synced Desktops [memory]; the check script printed a warning for a Desktop path and OK for `~/Developer/...` [local].

### 7.3 Sample card 2

```markdown
### GIT-003 提交信息：一行摘要、空一行、正文；摘要以类型前缀开头

- 约束力：推荐（适用范围：所有项目）；在本课程仓库内是必须（团队约定）
- 规则类型：惯例·事实标准（Git 手册的建议 + 约定式提交 1.0.0）
- 规则：第一行是不超过 50 个字符的摘要，写成 `类型: 做了什么`；空一行；正文说明改了什么、为什么改。
- 谁说的：git-commit 手册"DISCUSSION"一节（Git 2.55.0 文档），原文说这是"好主意"而不是强制要求 https://git-scm.com/docs/git-commit ；Conventional Commits 1.0.0 https://www.conventionalcommits.org/zh-hans/v1.0.0/
- 核对日期：2026-11-19；复核周期：12 个月
- 谁来管：评审人；团队启用提交检查后由 CI 来管。不遵守的后果：历史记录看不懂，自动生成更新日志和版本号的工具用不了。
- 为什么：Git 把第一段当作这次提交的"标题"，`git log --oneline`、拉取请求标题、邮件主题都用它。类型前缀让人和工具一眼看出这是新功能还是修复。
- 正例：

      fix: 修正汇率日期解析的时区错误

      原来把 UTC 时间当作本地时间，跨日数据会错位一天。
      现在统一按 UTC 解析，并补了一个回归测试。

- 反例：

      update
      修改了一些东西
      Fix bug
      最终版2

- 怎么自动检查：

      git log -1 --format=%s | grep -Eq '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\([a-z0-9-]+\))?!?: .+' && echo OK || echo "摘要格式不符合约定"

  阶段 3 改用 commitlint 在 CI 里检查。
- 例外：Git 自动生成的合并提交和回退提交不用改。规范本身只定义了 `feat` 和 `fix`；`docs`、`refactor`、`test`、`chore` 等来自常用工具配置，团队可以增减。提交信息用中文还是英文由团队约定，一个仓库只用一种。
- 旧教程提醒："50/72 是 Git 的硬性规定"是误传，Git 手册明说不是强制。一个汉字在终端里占两个英文字符的宽度，中文摘要控制在 25 个字左右。
- 教学阶段：1（认识并手写），3（自动检查）
```

Basis: git-commit manual [source]; Conventional Commits [source]; the regular expression accepted `fix: …`, `feat(api)!: …`, `docs: …` and rejected `update` and `Fix bug` [local]; the two-column remark is my inference with a tested width script [local].

### 7.4 Sample card 3

```markdown
### GH-001 GitHub 账号开启双重验证，主方法用验证器 App，并离线保存恢复码

- 约束力：必须（适用范围：你的 GitHub 账号）
- 规则类型：行业要求（平台强制政策）
- 规则：注册当天就开启双重验证（2FA）：用验证器 App（TOTP）作为主要方式，下载恢复码并离线保存，再添加一把通行密钥（passkey）用于登录。
- 谁说的：GitHub 文档 "About mandatory two-factor authentication" https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/about-mandatory-two-factor-authentication ；"About passkeys" https://docs.github.com/en/authentication/authenticating-with-a-passkey/about-passkeys
- 核对日期：2026-11-19；复核周期：6 个月（平台政策变化快）
- 谁来管：GitHub。不遵守的后果：被选中的账号在 45 天登记期加 7 天宽限期之后，启用 2FA 之前无法访问 GitHub.com；账号被盗会连累你所有的仓库和合作者。
- 为什么：自 2023 年 3 月起，GitHub 要求在 GitHub.com 上贡献代码并符合条件的账号启用 2FA。GitHub 建议把验证器 App 作为主要方式；通行密钥和安全密钥目前还不能作为"主要 2FA 方式"，但通行密钥可以用来登录，并且能防钓鱼。短信有安全风险，部分地区还收不到。
- 正例：验证器 App 已绑定；恢复码打印或存进密码管理器；另加一把通行密钥；短信不作为唯一方式。
- 反例：只绑短信；恢复码截图留在同一部手机的相册里；嫌麻烦，等 GitHub 发邮件催了再说。
- 怎么自动检查：人工检查：登录 GitHub，在账号设置的"Password and authentication"页面确认 Two-factor authentication 为已启用，并确认恢复码的保存位置。
- 例外：公司统一管理的企业账号（Enterprise Managed Users）由公司的登录系统负责，不适用这条个人账号政策。
- 旧教程提醒：老教程里"用账号密码 push"早已失效；"2FA 用短信就行"也已过时。
- 教学阶段：1
```

Basis: both GitHub pages [source]. The settings page name is from the passkey and 2FA documentation flow; confirm the exact menu wording when writing the lesson.

### 7.5 Sample card 4

```markdown
### GIT-007 开了自动签名却没有 gpg：先让提交恢复可用

- 约束力：必须先处理（适用范围：出现这个问题的电脑）。"要不要给提交签名"本身是参考；仓库管理员要求签名时才是必须。
- 规则类型：惯例·平台与工具（提交签名是 Git 和 GitHub 的可选功能）；被仓库规则要求时变成规范·团队约定
- 规则：不要每次都绕过。先看清现有配置，再由你本人二选一：现在关闭自动签名，或者改用不需要 gpg 的 SSH 签名。
- 谁说的：实测（2026-11-19，在一台出现这个问题的 Mac 上）；GitHub 文档 "About commit signature verification" https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification ；"Telling Git about your signing key"（SSH 签名需要 Git 2.34 及以上）https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key
- 核对日期：2026-11-19；复核周期：处理完成后关闭本卡，阶段 3 再开"提交签名"正式卡
- 谁来管：Git 本身。不处理的后果：这台电脑上每一次 `git commit` 都失败。
- 为什么：如果全局配置里有 `commit.gpgsign=true`、`gpg.program=gpg`，但电脑上没有安装 gpg，提交时就会报：

      error: cannot run gpg: No such file or directory
      error: gpg failed to sign the data:
      fatal: failed to write commit object

  个人学习仓库不要求签名；研究估计带签名的提交只占一小部分（不同样本在 5% 到 18% 之间）。SSH 签名是 GitHub 文档里最容易上手的方式。
- 正例（先看，再选）：

      # 第 0 步：看清楚是谁在哪个文件里配了什么
      git config --global --list --show-origin | grep -iE 'gpg|sign'

      # 方案 A（推荐现在用）：关闭自动签名，随时可以改回来
      git config --global commit.gpgsign false

      # 方案 B（以后需要 Verified 标记时再做）：改用 SSH 签名
      ssh-keygen -t ed25519 -C "你的邮箱"
      git config --global gpg.format ssh
      git config --global user.signingkey ~/.ssh/id_ed25519.pub
      git config --global --unset gpg.ssh.program    # 如果这一项是空字符串，不清掉会报 cannot run
      git config --global commit.gpgsign true
      # 然后在 GitHub 的 SSH and GPG keys 页面把公钥添加为 Signing Key

- 反例：每次提交都手敲 `--no-gpg-sign`；看不懂就把整个 `~/.gitconfig` 删掉；让 AI 助手替你改全局配置，而你不知道它改了什么。
- 怎么自动检查：

      git config --get commit.gpgsign          # 期望：false，或者签名已经配置好
      git log --format='%h %G? %s' -n 5        # G = 签名有效，N = 没有签名

- 例外：只想临时提交一次，可以用 `git commit --no-gpg-sign`，但这不是长期办法。
- 旧教程提醒："签名必须装 GPG"已过时；Git 2.34 起可以直接用 SSH 密钥签名。
- 教学阶段：1（恢复可用），3 或 9（正式学习签名）
```

Basis: failure and the three workarounds reproduced in a scratch repository [local]. Plan B was verified with repository-local settings, including a local `gpg.ssh.program=ssh-keygen` override; the global `--unset` line is the logical equivalent and was **not** executed, because an agent may not change global configuration. The lesson must have the learner run step 0 and decide. In the reproduction the global `gpg.ssh.allowedsignersfile` was also empty [local]; in my test local verification with `git log --show-signature` used a repository-local allowed-signers file [local], while GitHub's Verified badge depends on the key registered with the account [source: GitHub pages above]. The "only a few percent of commits are signed" remark in the card is search-level (section 6.10, V5).

### 7.6 Sample card 5

```markdown
### FND-004 文件和文件夹命名：小写、无空格、用连字符；Python 模块用下划线；不靠大小写区分

- 约束力：推荐（适用范围：所有项目）；其中"不靠大小写区分文件"和"Python 模块名合法"是必须
- 规则类型：规范·组织（Google 开发者文档风格指南、MDN）+ 标准（PEP 8）+ 惯例·平台与工具（Git FAQ）
- 规则：仓库里的文件和文件夹用小写英文字母、数字和连字符 `-`；Python 文件和包用下划线 `_`；不用空格、中文和特殊符号；不让两个名字只差大小写。
- 谁说的：Google developer documentation style guide "Filenames and file types" https://developers.google.com/style/filenames ；MDN "Dealing with files"（2026-09-11 修改）https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files ；PEP 8（2025-04-04 修改）https://peps.python.org/pep-0008/ ；Git FAQ https://git-scm.com/docs/gitfaq
- 核对日期：2026-11-19；复核周期：12 个月
- 谁来管：工具和评审人。不遵守的后果：命令行里要处处加引号；网址里出现 `%20`；Python 无法 `import`；在 Mac 上没事、到 Linux 服务器上找不到文件。
- 为什么：多数 Web 服务器区分大小写，而 macOS 默认不区分（本机已验证），Git 自己区分大小写，所以只差大小写的两个文件在你的电脑上无法同时存在。Git 默认把中文文件名显示成一串转义数字，难读难查。Python 的导入名里不能有连字符。
- 正例：

      my-first-repo/
      notes/2026-11-19-git-basics.md
      src/exchange_rates.py
      docs/decisions/0001-use-uv.md
      README.md  LICENSE  CHANGELOG.md      （约定俗成的大写文件名，保持原样）

- 反例：

      My Project (final)/
      新建文件夹 2/
      学习笔记.md
      Utils.py 和 utils.py 同时存在
      exchange-rates.py                     （Python 无法导入）

- 怎么自动检查：

      # 列出不符合约定的已跟踪文件（约定俗成的大写文件名除外）
      git -c core.quotePath=false ls-files \
        | grep -vE '^[a-z0-9._/-]+$' \
        | grep -vE '(^|/)(README|LICENSE|CHANGELOG|CONTRIBUTING|SECURITY|CODE_OF_CONDUCT|CODEOWNERS|CLAUDE|AGENTS|Makefile|Dockerfile)(\.[a-z]+)?$'

      # 只差大小写的重名
      git -c core.quotePath=false ls-files | tr '[:upper:]' '[:lower:]' | sort | uniq -d

  Python 模块名交给 ruff 规则 N999（invalid-module-name）。
- 例外：语言或框架自己的约定优先（例如 React 组件文件常用大驼峰，Java 类文件与类名同名）；文件内容里可以放心写中文。
- 旧教程提醒：Windows 时代的"文件名随便起，带空格也行"在命令行和服务器上会处处碰壁。
- 教学阶段：1
```

Basis: all four documents [source]; case-insensitivity, the escaped Chinese name in `git status`, both check pipelines and `ruff rule N999` were run today [local]. The React and Java remark in 例外 is [memory].

## 8. Staying current (与时俱进): mechanism and watchlist

### 8.1 Mechanism to build into the workspace

1. Every rule card carries 核对日期 and 复核周期 (section 7.1). Law and platform policy: 6 months. Tool conventions: 12 months. Stable community specifications (SemVer, RFC keywords): 24 months.
2. Keep one register file, for example `handbook/standards-watch.md`, with one row per watched item: name, version last seen, date checked, the single URL that shows the current version, next check date. The catalogue in section 4 is the seed.
3. Make the review a recurring learner exercise from stage 3 onwards ("currency review"): open the URL, compare, update the card through a pull request. It trains reading changelogs and primary sources, which is itself a professional norm.
4. Teach the reading order for "is this still current?": the issuing body's own page, then the specification's change log, then the regulator's page; search engines and AI answers only as pointers.
5. Mark stale lore explicitly with the 旧教程提醒 field. Section 2 lists the first batch.

### 8.2 Watchlist: items likely to change within twelve months

| Item | State today | What to watch | Where |
|---|---|---|---|
| EU AI Act | Amended by Regulation (EU) 2026/1744 | Ninth prohibition in December 2026; Annex III on 2027-12-02; Annex I on 2028-08-02 | https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai [source] |
| EU Cyber Resilience Act | Reporting duties live | Main obligations 2027-12-11; harmonised standards | https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act [source] |
| EN 301 549 V4.1.1 | Published; Official Journal citation pending | Citation gives presumption of conformity under the Accessibility Act | [search: Deque article] |
| EU Digital Omnibus (data and cookies) | Council mandate of 2026-10-21; not adopted | Trilogue outcome on cookie consent | [search: IAPP] |
| GDPR procedural regulation | In formal adoption | Publication | https://commission.europa.eu/law/law-topic/data-protection/legal-framework-eu-data-protection_en [source] |
| China: 《互联网信息服务管理办法》 | Revision draft of 2026-07-03, comments closed | Final text and effective date | https://www.cac.gov.cn/2026-07/03/c_1784822399677167.htm [source] |
| China: GB/T 8566 and GB/T 25000.10 | Lag the 2026 and 2023 international editions | Revisions | https://openstd.samr.gov.cn/ [source] |
| OAuth 2.1 | draft-17, expires 2027-05-04 | Publication as an RFC | https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ [source] |
| WCAG 3.0 | Working Draft, September 2026 | New drafts; do not teach for conformance | https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/ [source] |
| CWE Top 25 | 2025 list | A 2026 list | https://cwe.mitre.org/top25/ [source] |
| NIST SSDF 1.2 | Initial public draft | Final SP 800-218 Rev. 1 | https://csrc.nist.gov/projects/ssdf [source] |
| SOC 2 criteria | Exposure draft of 2027 criteria (2026-11-16) | Final criteria | AICPA page [source] |
| PCI DSS | 4.0.1; comment round held mid-2026 | Next version | [search] |
| Git 3.0 | No release date | Default `main`, SHA-256, reftable | https://git-scm.com/docs/BreakingChanges [source] |
| GitHub two-factor policy | TOTP primary; passkeys not primary 2FA | GitHub says it plans to accept passkeys as primary later | mandatory-2FA page [source] |
| Python | 3.15 current | 3.11 leaves support 2027-10; 3.16 due 2027-10 | https://www.python.org/downloads/ [source] |
| ECMAScript | ES2026 | ES2027 in June 2027 | https://ecma-international.org/publications-and-standards/standards/ecma-262/ [source] |
| OpenAPI, SLSA, OSPS Baseline, SPDX list | 3.2.1; 1.2; v2026.08.28; 3.29.0 | Point releases | URLs in section 4 |
| ITIL | Version 5 alongside ITIL 4 | Retirement date of ITIL 4 | [search] |
| ISO 8601-1 | 2019 edition; revision running | New edition targeted for 2028 | [search] |
| Scrum Guide | 2020 | Any new edition | https://scrumguides.org/revisions.html [source] |

## 9. Unverified items, conflicts and caveats

- **ISO catalogue pages were not readable.** The 12207:2026, 25010:2023, 27001 amendment and SQL corrigenda facts rest on search summaries of ISO, IEC, IEEE and reseller pages. ISO and IEEE give different publication days for 12207:2026 (29 and 15 April 2026).
- **ISO/IEC/IEEE 29119** parts 4 and 5: editions not confirmed.
- **CMMI V3.0** release date (6 April 2023) is search-level; the institute's landing page still shows V2.0 resources.
- **ISO/IEC 40500:2025** as the ISO edition of WCAG 2.2: from memory.
- **Regulation numbers** (EU) 2024/2847 (CRA) and (EU) 2024/1689 (AI Act): from memory; the amending regulation (EU) 2026/1744 is confirmed by the Commission page's Official Journal reference and by search.
- **European Accessibility Act application date** (2025-06-28) and **EN 301 549 V4.1.1** details: search-level.
- **PCI DSS 4.0.1**, **ITIL Version 5**, **Octoverse 2026**, **JetBrains** figures, **commit-signing prevalence**: search-level.
- **China**: the State Council decree number and effective date of the December 2024 revision of the internet information services measures are not confirmed; the app-filing notice number comes from press coverage; 数据安全法 dates are from memory; 等保 level details and the statement that hosting providers demand ICP filing come from secondary sources; 信创 has no single primary source.
- **Alibaba manual**: the three-level wording is confirmed from an earlier edition's preface via search, not from the 黄山版 PDF itself.
- **Stack Overflow help pages** (minimal reproducible example, how to ask) were blocked by a challenge page; content is from memory.
- **CVE Program** description is from memory (JavaScript-only page).
- **GitLab Handbook** is cited as an example only; today's fetch hit a sign-in redirect.
- **RFC 9457 date**: the document says July 2023, RFC Editor metadata says August 2023.
- **Unicode 18.0.0 page** carries a "preliminary" note in the fetched text although it is the target of the "latest" redirect.
- **OCI image-spec v1.1.1**: release year not visible in the fetch.
- **GitHub mandatory 2FA**: the page describes criteria for "selected" accounts and says criteria may change; do not tell the learner that every account is forced on a fixed date. Tell them to enable it regardless.
- **`~/Developer`**: a macOS convention supported by a system icon, not an Apple requirement.
- **Employment data** are for the United States.
- The claim in sibling briefs that Claude Code reads `AGENTS.md` natively in some conditions was not re-verified here.

## 10. Recommendations for the builders

1. Open stage 0 with the seven-category table and the decision procedure (sections 3.1 to 3.4), in Chinese, with the analogies. Then use the category label on every later rule without exception.
2. Print the two-axis idea early: 规则类型 is not 约束力. Use WCAG and GB versus GB/T as the worked examples.
3. Adopt the rule-card format of section 7.1 and seed the handbook with the five sample cards after the learner has seen the format once.
4. Put card GIT-007 before the first commit exercise; otherwise the first commit fails on a Mac with this configuration. The learner, not the assistant, runs the global configuration change.
5. Put card FND-001 before any repository is created; a workspace on an iCloud-synced Desktop must move first.
6. Teach Conventional Commits by hand in stage 1 and automate it in stage 3; say plainly that the specification defines only `feat` and `fix`.
7. For account setup teach: TOTP app, recovery codes, then a passkey; then one authentication path (GitHub CLI over HTTPS is the shortest path on the reference Mac (plan G7) once the learner installs `gh`).
8. Treat signing as optional in stage 1 and schedule SSH signing as a deliberate later lesson.
9. Use section 5.2 as the stage 0 "what the job expects" page, labelled 岗位期望, with the Indeed and Stanford data and their limits.
10. Create `handbook/standards-watch.md` from section 8.2 and make the currency review a recurring exercise.
11. Keep awareness-only items (12207, 29119, CMMI, ITIL, SOC 2, PCI DSS, 信创, 等保) to one paragraph each: what it is, what kind of rule, when the learner will meet it.
12. For Chinese readers link the verified Chinese texts: Agile Manifesto, Conventional Commits, SemVer, Keep a Changelog, Twelve-Factor, Pro Git, WCAG 2.1 authorised translation, 提问的智慧, 中文文案排版指北, and the Chinese statutes on cac.gov.cn and gov.cn.

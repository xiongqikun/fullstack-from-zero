# Brief: frontend-stack-2026 — the beginner-appropriate front-end stack as of 2026-11-19

Raw material for lesson builders. Tags: **[local]** = I ran it on this machine today (macOS 27.2 arm64, Node v26.12.0, npm 11.20.0);
**[source: URL]** = read in a primary source today; **[memory]** = not verified today. Paths below are relative to this scratch
directory (`research/frontend-stack-2026/`). All demo projects are kept here without `node_modules`; `npm ci` restores them.

## 1. Decision-relevant findings (TL;DR)

1. **The default scaffold changed a lot in 2026.** `npm create vite@latest x -- --template react-ts` (create-vite 9.3.4, 2026-11-05) now gives
   React 19.3 + Vite 8 (Rolldown/Oxc) + **TypeScript 7.0.2 (native compiler)** + **Oxlint** (not ESLint) and installs **28 packages** in ~6 s.
   Type check 0.25 s, production build 0.27 s, lint in milliseconds. [local]
2. **TypeScript 7.0 is released** (GA 2026-07-08; Go-native `tsc`, "10x faster"). `npm install -D typescript` now installs it. It ships **no
   programmatic API** yet (7.1 beta, 2026-10-20, adds one), so typescript-eslint and Vue/Svelte/Astro/MDX tooling still need TypeScript 6.0.
   [source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/] `require('typescript')` exposes only `version` [local].
3. **Linter split:** create-vite's React template uses Oxlint by default since 9.1.0 (2026-06-23); `--eslint` gives ESLint 10 + typescript-eslint 8
   but pins **TypeScript ~6.0.3** and installs 161 packages. [local + source: create-vite CHANGELOG] Teach **Oxlint + Prettier**; ESLint/Biome = awareness.
4. **Node 26 "Lithium" is the Active LTS** (since 2026-10-28; latest 26.13.1). The machine's 26.12.0 is the same line but a pre-LTS build
   — update within 26.x. Node 27 is in a new "alpha" phase; from 27 on there is one major per year and every line becomes LTS. [source + local]
5. **npm on Node 26 stays at 11.x** (11.20.0 bundled). npm 12 (2026-07-08) blocks dependency install scripts by default, but the Node Release WG
   decided not to ship npm 12 in Node 26/24/22. On npm 11.20 install scripts **still run, with a warning**. [local + source]
6. **npm 11.20 already has the safety tools:** `min-release-age` (cooldown, days), `npm install-scripts ls/approve/deny`, `allowScripts` in
   package.json, `strict-allow-scripts`, `npm audit signatures`. All verified here. In the whole taught stack exactly one package has an
   install script: `fsevents` (optional, ships a prebuilt binary; safe to deny). [local]
7. **React is 19.3.1** (19.3 on 2026-09-09); no React 20. React Compiler is stable 1.0 (2025-10-07) but **opt-in** and not in the default
   template. `ReactDOM.render`, PropTypes, function-component `defaultProps` are gone. [local + source]
8. **React Router is 8.5.2** (8.0 on 2026-06-17); `react-router-dom` is frozen at 7.18.6 — an old-tutorial `npm i react-router-dom` silently
   installs the previous major. TanStack Query is still v5 (5.108.0). Zod is v4 (4.6.7). All three verified together in tests. [local]
9. **Vitest is 5.1.1**; the classic trap is real: without `globals: true`, Testing Library does not auto-clean the DOM between tests. [local]
10. **CSS has moved:** nesting, `:has()`, container queries, subgrid, `color-mix()`, `oklch`, `dvh` are all Baseline *Widely available* now —
    teach them as normal CSS, not as "new". Anchor positioning, `if()`, customizable `<select>` are still limited. [local: web-features 3.46.0]
11. **ECMAScript 2026** (ECMA-262 17th edition, June 2026) is current. Temporal and `using` are finished but slated for ES2027 and are not
    Baseline in browsers yet (Node 26 has both). [source + local]
12. **Next.js is 16.4.6**; meet a meta-framework only after a Vite SPA + own API has been built and deployed (see §9).
13. Lint/test tools **detect AI agents** (`AI_AGENT`/`CLAUDECODE` env) and print terser output than the learner sees in a normal terminal. [local]

## 2. Versions today (npm registry `latest` on 2026-11-19 unless noted) [local: `npm view <pkg> dist-tags time`]

| Layer | Current | First release of this major | Notes |
|---|---|---|---|
| Node.js | 26.13.1 LTS "Lithium" | 26.0.0 2026-05-05; LTS 2026-10-28 | 24 "Krypton" + 22 "Jod" = Maintenance LTS (EOL 2028-04-30 / 2027-04-30); 20 is EOL; 27 = alpha, Current 2027-04-22 [source: https://github.com/nodejs/Release, https://nodejs.org/dist/index.json] |
| npm | 12.2.3 (`latest`); **11.20.0 bundled with Node 26** | 12.0.0 2026-07-08 | npm 12 first bundled in Node 27 alpha [local: index.json] |
| pnpm / Bun | 12.21.0 / 1.4.5 | pnpm 12.0.0 2026-08-26; Bun 1.4.0 2026-08-20 | Corepack is not shipped with Node since v25 [source: https://nodejs.org/docs/latest-v24.x/api/corepack.html; local: no `corepack` binary] |
| TypeScript | 7.0.2 | 2026-07-08 | 6.0.3 (2026-04-16) = last JS-based; 7.1.0-beta 2026-10-20 |
| Vite / create-vite | 8.3.8 / 9.3.4 | Vite 8.0.0 2026-03-12 | `@vitejs/plugin-react` 6.3.0; Node `^20.19.0 || >=22.12.0` |
| React / React DOM | 19.3.1 | 19.0.0 2024-12-05; 19.2 2025-10-01; 19.3 2026-09-09 | `@types/react` 19.3.0; `babel-plugin-react-compiler` 1.0.0; `eslint-plugin-react-hooks` 7.1.1 |
| React Router | 8.5.2 | 8.0.0 2026-06-17 | Node >= 22.22; `react-router-dom` stops at 7.18.6 |
| TanStack | Query 5.108.0, Router 1.170.46, Start 1.169.7, Form 1.33.5 | Query v5 2023-10-17 | Start docs: "TanStack Start is stable" [source: https://tanstack.com/start/latest/docs/framework/react/overview] |
| Next.js | 16.4.6 | 16.0 2025-10-21 | Node >= 20.9 |
| Tailwind CSS | 4.3.5 | 4.0 2025-01-21 | `@tailwindcss/vite` peer `vite ^5.2 || ^6 || ^7 || ^8` |
| Validation / forms | zod 4.6.7; react-hook-form 7.92.0 (8 = beta) | zod 4.0 2025-07-09 | |
| Lint / format | Oxlint 1.94.0; ESLint 10.15.0; typescript-eslint 8.73.0; Prettier 3.10.1; Biome 2.6.8; Oxfmt 0.79.0 | Oxlint 1.0 2025-06-10; ESLint 10.0 2026-02-06; Biome 2.0 2025-06-17 | typescript-eslint peer: `typescript >=4.8.4 <6.1.0` |
| Testing | Vitest 5.1.1; @testing-library/react 16.3.3, /dom 10.4.2, /jest-dom 8.0.0, /user-event 14.6.13; jsdom 31.0.1; Playwright 1.65.1; msw 3.0.7 | Vitest 5.0 2026-09-03 | Vitest needs Vite >= 6.4, Node >= 22.12 |
| Awareness | Vite+ `vite-plus` 1.7.0; shadcn CLI 4.23.0; @base-ui/react 1.9.0; radix-ui 1.8.1; MUI 9.5.0; antd 6.7.1; Astro 7.4; Vue 3.5.45; Svelte 5.58; Angular 22.3; Storybook 10.6.7 | | versions only; not evaluated |
| Standards | ECMAScript 2026 (17th ed., June 2026); CSS Snapshot 2026 (W3C Note 2026-06-22); HTML = Living Standard | | [source: https://ecma-international.org/publications-and-standards/standards/ecma-262/, https://www.w3.org/TR/css/] |
| Editor | VS Code 1.147 (2026-11-18) is latest; **installed: 1.145.2, whose built-in TS service is 6.0.3** | | [source: https://code.visualstudio.com/updates] [local: app bundle] |

## 3. Local verification: exact commands and real output

All run today with `export npm_config_cache="$TMPDIR/npm-cache"`; network limited to registry.npmjs.org. No dev server was started (the sandbox
cannot bind ports), so `npm run dev` / `vite preview` / Playwright are **not** verified here.

### 3.1 Scaffold → install → type check → build → lint (project: `demo-app/`)

```bash
npm create vite@latest demo-app -- --template react-ts --no-interactive
cd demo-app && npm install
npx tsc -b            # type check only (tsconfig has noEmit)
npm run build         # "tsc -b && vite build"
npm run lint          # "oxlint"
```

```text
create-vite v9.3.4  …  Done. Now run: cd demo-app / npm install / npm run dev
added 28 packages, and audited 29 packages in 6s      found 0 vulnerabilities
$ npx tsc --version  → Version 7.0.2        $ npx vite --version → vite/8.3.8 darwin-arm64 node-v26.12.0
vite v8.3.8 building client environment for production...  ✓ 20 modules transformed.
dist/assets/index-GpEN3EET.js   222.44 kB │ gzip: 69.28 kB        ✓ built in 272ms
$ npm run lint → (no output, exit 0)        $ npx oxlint --version → Version: 1.94.0
```

Scaffolded `package.json` (unchanged by me): scripts `dev: vite`, `build: tsc -b && vite build`, `lint: oxlint`, `preview: vite preview`;
deps `react ^19.3.1`, `react-dom ^19.3.1`; devDeps `@types/node ^24.19.2`, `@types/react ^19.3.0`, `@types/react-dom ^19.3.0`,
`@vitejs/plugin-react ^6.1.2`, `oxlint ^1.90.0`, `typescript ~7.0.2`, `vite ^8.3.6`. [local]

Generated files worth showing learners: `.oxlintrc.json` (plugins `react`, `typescript`, `oxc`; rules `react/rules-of-hooks: error`,
`react/only-export-components: warn`), three tsconfigs (`tsconfig.json` references `tsconfig.app.json` + `tsconfig.node.json`), and
`tsconfig.app.json` with `target es2023`, `moduleResolution bundler`, `allowImportingTsExtensions`, `verbatimModuleSyntax`, `noEmit`,
`jsx react-jsx`, `noUnusedLocals/Parameters`, **`erasableSyntaxOnly: true`** (so `enum` is a compile error), no explicit `strict`
(TS 7 defaults `strict` to true [source: TS 7.0 announcement]). `src/main.tsx` uses `createRoot(document.getElementById('root')!)` and `<StrictMode>`. [local]

In a real terminal the same command is interactive: project name → framework → variant → **"Which linter to use?" (Oxlint / ESLint)** →
"Install with npm and start now?". Prompt texts read from the create-vite 9.3.4 bundle; flags `--no-eslint --no-immediate` are accepted and
skip those two prompts (verified non-TTY only). Templates available: vanilla, vue, react, **react-compiler**, preact, lit, svelte, solid, qwik (+ `-ts`). [local]

What errors look like (deliberately broken file; captured with agent env vars removed):

```text
src/Broken.tsx(9,9): error TS2322: Type 'string' is not assignable to type 'number'.          ← tsc 7

  x react-hooks(rules-of-hooks): React Hook "useState" is called conditionally. React Hooks must be called in the exact same order…
   ,-[src/Broken.tsx:5:17]
 5 |     const [n] = useState(0)
   :                 ^^^^^|^^^^^
   :                      `-- This Hook call is not reachable on every render path.
  help: Move the Hook call before the condition, or call it unconditionally and branch inside the Hook/effect instead.
  ! react(jsx-key): Missing "key" prop for element in iterator.
  help: Add a "key" prop … (https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key).
Found 1 warning and 1 error.   Finished in 4ms on 1 file with 116 rules using 16 threads.          ← oxlint
```

### 3.2 Vitest 5 + Testing Library (unit test + component test)

```bash
npm install -D vitest jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom @testing-library/user-event
```

`vite.config.ts` (works with `tsc -b` under TS 7):

```ts
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'] },
})
```

`src/test/setup.ts` — **the cleanup lines are required** when `globals` is off (the default):

```ts
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => { cleanup() })
```

Scripts added: `"test": "vitest run"`, `"test:watch": "vitest"`, `"typecheck": "tsc -b"`. Unit test (`src/lib/formatPrice.test.ts`):

```ts
import { describe, expect, it } from 'vitest'
import { formatPrice } from './formatPrice.ts'

describe('formatPrice', () => {
  it('formats whole cents as yuan with two decimals', () => {
    expect(formatPrice(1999)).toBe('¥19.99')
  })
})
```

Without the `cleanup()` lines the second component test failed exactly like this (real output):

```text
 FAIL  src/Counter.test.tsx > <Counter /> > renders a fresh counter in a second test (needs cleanup between tests)
AssertionError: expected [ …(2) ] to have a length of 1 but got 2
```

With the fix: `Test Files 2 passed (2)  Tests 5 passed (5)  Duration 380ms`. [local]

### 3.3 Router + server state + validation in one smoke test (no server needed)

`npm install react-router @tanstack/react-query zod` → react-router 8.5.2, @tanstack/react-query 5.108.0, zod 4.6.7. Files:
`src/features/Users.tsx` (`useQuery` + `<Routes>/<Route>/<Link>/useParams` imported from `react-router`), `Users.test.tsx`
(`MemoryRouter` + `QueryClientProvider` with `retry: false`, fake `queryFn`), `signup.ts` (zod schema). Zod 4 idioms that passed:
`import * as z from 'zod'`, `z.email()`, `z.infer<typeof Schema>`, `schema.safeParse(x)`, `z.flattenError(err)`, `z.prettifyError(err)`:

```text
✖ Invalid email address
  → at email
✖ Too small: expected number to be >=18
  → at age
 Test Files  4 passed (4)      Tests  9 passed (9)      Duration  480ms
```

Final gate, all green: `npm run typecheck && npm run lint && npm test && npm run build && npx prettier --check .` [local]

### 3.4 Formatter

`npm install -D prettier` (3.10.1, adds 1 package). Out of the box `npx prettier --check .` flags **every** scaffolded file, because the Vite
template style is no-semicolon/single-quote and Prettier's defaults are the opposite. This `.prettierrc.json` makes a fresh scaffold pass
unchanged: `{ "semi": false, "singleQuote": true }`. Then `--write` only touched the three files I had written by hand. [local]
Comparison (zero-config, same project): `npx oxfmt@0.79.0 --check` → "Format issues found in above 12 files"; `npx @biomejs/biome@2.6.8 check .`
→ "Found 3204 errors. Found 2098 warnings" (it also checked `dist/`, and defaults to tabs + double quotes) — Biome needs `biome init` + VCS-ignore
config before it is usable on a Vite scaffold. [local]

### 3.5 The ESLint variant (project: `demo-eslint/`)

`npm create vite@latest demo-eslint -- --template react-ts --eslint --no-interactive` → `eslint ^10.14.0`, `@eslint/js`, `typescript-eslint ^8.72.1`,
`eslint-plugin-react-hooks ^7.1.1`, `eslint-plugin-react-refresh`, `globals`, and **`typescript ~6.0.3`**; flat config `eslint.config.js` using
`defineConfig`/`globalIgnores` from `eslint/config`. `npm install` → "added 161 packages"; `npm run lint` 0.78 s; build fine. [local]

Same file of eight planted beginner mistakes (`evidence/BeginnerMistakes.tsx`) through both template configs [local]:

| Mistake | Oxlint 1.94 (default template) | ESLint 10.15 (template) |
|---|---|---|
| unused variable | warning `eslint(no-unused-vars)` | error `@typescript-eslint/no-unused-vars` |
| `setState` synchronously in an effect (derived state) | warning `react(set-state-in-effect)` | error `react-hooks/set-state-in-effect` + long explanation linking react.dev |
| missing effect dependency | warning `react-hooks(exhaustive-deps)` | warning `react-hooks/exhaustive-deps` |
| conditional hook | **error** `react-hooks(rules-of-hooks)` | **error** `react-hooks/rules-of-hooks` |
| list without `key` | warning `react(jsx-key)` | not reported |
| `any` | not reported | error `@typescript-eslint/no-explicit-any` |
| `items.push()` on state; `==` | not reported by either | not reported by either |

### 3.6 Other scaffolds

- `--template react-compiler-ts` (`demo-compiler/`): adds `babel-plugin-react-compiler ^1.0.0`, `@rolldown/plugin-babel`, `@babel/core`;
  `vite.config.ts` = `plugins: [react(), babel({ presets: [reactCompilerPreset()] })]`; 76 packages; build 467 ms; bundle contains
  `react.memo_cache_sentinel` (compiler active). The default template's README says the compiler is left out "because of its impact on dev & build performances". [local]
- `--template vanilla-ts` (`demo-vanilla/`): only `typescript ~7.0.2` + `vite ^8.3.6`, 17 packages, no linter, single `tsconfig.json`; build OK.
  Its `main.ts` builds the page with `innerHTML` and `querySelector<HTMLButtonElement>('#counter')!`. [local]
- Plain HTML/CSS/JS + `npm install -D vite` (`plain-site/`): `npx vite build` works with **no config file**; the CSS used nesting, `@container`,
  `:has()`, `color-mix()`, `oklch`, `100dvh`, `text-wrap: balance` — the build flattened nesting (`.card h1{…}`) and kept the rest. [local]
- Tailwind (`tailwind-test/`): `npm install -D vite tailwindcss @tailwindcss/vite`, `plugins: [tailwindcss()]`, CSS = `@import "tailwindcss";`,
  no `tailwind.config.js` → utilities generated (`bg-indigo-600`, `min-h-dvh`, …). Matches the v4.3 docs. [local] [source: https://tailwindcss.com/docs/installation/using-vite]

### 3.7 Node 26 facts that shape the JS/TS lessons [local]

- `node hello.ts` runs TypeScript directly, no flag, no warning — **and performs no type checking** (a file with a `tsc` error still ran).
  Stable since v25.2/v24.12; `enum`, runtime `namespace`, parameter properties, `.tsx` and tsconfig `paths` are unsupported.
  [source: https://nodejs.org/docs/latest-v26.x/api/typescript.html] `node enum.ts` → `SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]: TypeScript enum is not supported in strip-only mode`.
- `npm init -y` now writes `"type": "commonjs"`. A file with `import` then fails: `SyntaxError: Cannot use import statement outside a module`
  (+ "Make sure to set "type": "module" in the nearest package.json"). Fix verified: `npm pkg set type=module`.
- `npx tsc --init` (TS 7) writes `module: nodenext`, `strict`, **`noUncheckedIndexedAccess`**, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`,
  `types: []`. Consequences seen: `todos[0].title` → `error TS2532: Object is possibly 'undefined'`; `import './math.ts'` → `TS5097` (needs
  `allowImportingTsExtensions`); `import './math'` → `TS2835 … Did you mean './math.js'?`. A bare Node+tsc project is a config minefield for a
  beginner; the Vite templates avoid all three.
- Built-ins present in Node 26.12: `Temporal`, iterator helpers, `Object.groupBy`, `Map.prototype.getOrInsert`, `Array.fromAsync`, `Promise.try`,
  `RegExp.escape`, `Error.isError`, `Uint8Array.fromBase64`, `Iterator.concat`, `using`. Missing: `Math.sumPrecise`.
- `node --test file.test.ts` (built-in runner) works; mention only as awareness.

### 3.8 Tools change their output for AI agents [local]

With this session's env (`AI_AGENT`, `CLAUDECODE` set) Oxlint printed one compact line per problem and Vitest printed only the summary. With
`env -u AI_AGENT -u CLAUDECODE …` both printed the full human format (code frames, per-file ticks, colours). Lesson transcripts and auto-check
scripts should therefore be captured/parsed with an explicit format (`oxlint -f default|json`, `vitest run --reporter=verbose|json`), not the default.

## 4. State of each layer

### 4.1 HTML and CSS — what Baseline says today [local: `web-features` 3.46.0, published 2026-11-12; definitions: source https://web.dev/baseline]

Baseline "Newly available" = works in all core browsers (Chrome, Edge, Firefox, Safari, desktop + mobile); "Widely available" = 30 months later.

| Teach as normal CSS/HTML (Widely available; date reached) | Mention as progressive enhancement (Newly available since) | Do not teach as baseline (Limited) |
|---|---|---|
| Flexbox (2018) + `gap` (2023-10); Grid (2020); **subgrid (2026-03)**; custom properties (2019); **nesting (2026-06)**; **container size queries (2025-08)**; **`:has()` (2026-06)**; `:is()/:where()`; `@layer` (2024-09); `dvh/svh/lvh` (2025-06); `aspect-ratio`; `min()/max()/clamp()`; logical properties; **`color-mix()` + `oklch` (2025-11)**; `:focus-visible`; `prefers-color-scheme`, `prefers-reduced-motion`; media-query range syntax `(width >= 40rem)` (2025-09); individual `translate/rotate/scale`; `<dialog>` (2024-09); `<search>` (2026-04); `inert`; `loading="lazy"` (2026-06); `:user-valid/:user-invalid` (2026-05) | `light-dark()` and `text-wrap: balance` (2024-05-13 → 30 months = 2026-11-13, i.e. just crossed to Widely; the dataset predates it by a day); `@starting-style`, `transition-behavior` (2024-08); relative colors, `backdrop-filter` (2024-09); `<details name>` (2024-09); `@property` (2024-07); popover (2025-01); same-document view transitions (2025-10); invoker commands (2025-12); `@scope` (2026-03); container style queries (2026-05); `field-sizing` (2026-06); `sibling-index()` (2026-08); scroll-driven animations (2026-10-27) | anchor positioning; cross-document view transitions; `text-wrap: pretty`; customizable `<select>`; `interpolate-size`/`calc-size()`; `if()`; `@function`; grid lanes (masonry); `accent-color`; unprefixed `line-clamp`; `<datalist>`; `<input type="color">` |

Vite's production build targets "Baseline Widely Available browser versions as of a date fixed for each major release" [source: https://vite.dev/guide/],
which is why §3.6's build flattened nesting. Sass is not needed for nesting/variables any more.

### 4.2 JavaScript

- Current edition: **ECMAScript 2026**, ECMA-262 17th edition, June 2026. [source: https://ecma-international.org/publications-and-standards/standards/ecma-262/]
- Finished proposals by expected edition [source: https://github.com/tc39/proposals/blob/main/finished-proposals.md]: **2025** — iterator helpers, Set methods,
  `Promise.try`, `RegExp.escape`, import attributes + JSON modules, RegExp modifiers, Float16Array; **2026** — `Array.fromAsync`, `Error.isError`,
  `Math.sumPrecise`, Uint8Array base64, `Iterator.concat`, JSON.parse source text, `Map.getOrInsert` ("upsert"); **2027** — Temporal, explicit
  resource management (`using`), `Atomics.pause`, `Iterator.zip`, iterator chunking/includes/join.
- Baseline for everyday language features [local: web-features]: Widely — `let/const`, arrow functions, classes, template literals, destructuring,
  spread, modules, async/await, `fetch`, `AbortController`, `??`, `structuredClone`, `Array.prototype.at`, `toSorted/toReversed/with` (2026-01),
  `Object.groupBy` (2026-09), `Promise.withResolvers` (2026-09), `Array.fromAsync` (2026-07), `Intl.Segmenter` (2026-10). Newly — iterator helpers
  (2025-03), Set methods (2024-06), `Promise.try`, `RegExp.escape`. **Limited — Temporal, `using`**: teach `Date` + `Intl.DateTimeFormat` now and
  flag Temporal as "arriving".
- Course implication: teach modern syntax only (ES modules, `const/let`, arrow functions, `async/await`, optional chaining); `var`, `function`
  hoisting tricks, prototypes and `this` binding are reading knowledge for old code.

### 4.3 TypeScript

- 7.0 = Go-native port, typical 8–12x faster full builds; `npm install -D typescript` then `npx tsc`. It matches 6.0's checking and adopts 6.0's new
  defaults: `strict: true`, `module: esnext`, `types: []`, `rootDir: ./`; removed/erroring options include `target: es5`, `moduleResolution: node|node10|classic`,
  `baseUrl`, `module: amd|umd|systemjs`. Side-by-side install for API-dependent tools: `"@typescript/native": "npm:typescript@^7.0.2"`,
  `"typescript": "npm:@typescript/typescript6@^6.0.2"`. Vue/MDX/Astro/Svelte/Angular-template checking is not supported in 7.0. [source: TS 7.0 announcement]
- 7.1 beta (2026-10-20): new API entry points (`typescript/sync`, `/async`, `/ast`), "content mappers" for embedded languages, `--target es2026`;
  RC "in about a month". [source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-1-beta/] `@typescript-eslint/typescript-estree` 8.73
  already declares a peer `@typescript/native` = `typescript >=7.1.0-beta` [local], so the ESLint/TS-7 gap should close soon — re-check when stage 6 is generated.
- **What a beginner installs:** nothing globally. Use the version the scaffold pins (`~7.0.2`). Older tutorials that say `npm i -g typescript`,
  `ts-node`, `"moduleResolution": "node"`, `"baseUrl"`, or `enum` are now wrong or misleading. The TypeScript Handbook still documents up to 6.0
  and tells non-JS programmers to learn JavaScript first. [source: https://www.typescriptlang.org/docs/handbook/intro.html]
- Editor: VS Code 1.145.2 here bundles TS 6.0.3 for IntelliSense and has a `typescript.experimental.useTsgo` setting [local]; a dedicated TypeScript 7
  extension exists and built-in support was announced as coming [source: TS 7.0 announcement]. Because 7.0 mirrors 6.0's checking, squiggles and
  `tsc` should agree; whether VS Code 1.147 defaults to the TS 7 server is **unverified**.

### 4.4 Node.js and package managers

- Schedule: 26.x Active LTS 2026-10-28 → maintenance 2027-10-20 → EOL 2029-04-30. From 27.x: branch in October, six months of alpha, one major
  each April, LTS each October, no odd/even split. [source: https://github.com/nodejs/Release]
- Engines demanded by the taught stack [local: `npm view … engines`]: Vite 8 `^20.19.0 || >=22.12.0`; Vitest 5 `^22.12.0 || ^24.0.0 || >=26.0.0`;
  jsdom 31 `^22.22.2 || ^24.15.0 || >=26.0.0`; React Router 8 `>=22.22.0`; ESLint 10 `^20.19.0 || ^22.13.0 || >=24`; npm 12 `^22.22.2 || ^24.15.0 || >=26.0.0`;
  Playwright docs: "latest 22.x, 24.x or 26.x", macOS 14+ [source: https://playwright.dev/docs/intro]. Node 26 satisfies all.
- **Teach npm first.** It is the only manager that comes with Node (bin dir has just `node`, `npm`, `npx` [local]); every official quick-start used
  here shows an npm command; pnpm/Bun need a separate install. Awareness later: pnpm 12 blocks dependency build scripts unless listed in
  `allowBuilds` and defaults `minimumReleaseAge` to 1440 minutes [source: https://pnpm.io/supply-chain-security]; Bun does not run dependency
  lifecycle scripts unless `trustedDependencies` lists them [source: https://bun.com/docs/pm/cli/install]. One lockfile per project; never mix managers.

### 4.5 Vite

Vite 8 (2026-03-12) replaced esbuild + Rollup with **Rolldown** (Rust) and uses Oxc; `@vitejs/plugin-react` v6 dropped Babel (React Refresh via Oxc);
create-vite 9.0.0 removed the `react-swc` variants. [source: https://vite.dev/blog/announcing-vite8; create-vite CHANGELOG] Dev server default port 5173, preview 4173;
"`vite preview` is … not meant as a production server". [source: https://vite.dev/config/server-options, https://vite.dev/guide/static-deploy]
Only `VITE_`-prefixed env vars reach client code and they "should not contain sensitive information such as API keys". [source: https://vite.dev/guide/env-and-mode]
`server.proxy` can forward `/api` to a backend (useful for FastAPI in stage 7). Vite+ (`vp`, package `vite-plus` 1.7.0; bundles Vite, Vitest, Oxlint,
Oxfmt, Rolldown, tsdown) exists [source: https://viteplus.dev/guide/] — awareness only; its exact 1.0 date is unverified.

### 4.6 React

- 19.3 (2026-09-09): `<ViewTransition>` and Fragment refs stable, `use(browser())`, Trusted Types. 19.2 (2025-10-01): `<Activity>`, `useEffectEvent`.
  [source: https://react.dev/blog/2026/09/09/react-19-3, https://react.dev/blog] Exports verified in 19.3.1: `use`, `useActionState`, `useOptimistic`,
  `useEffectEvent`, `Activity`, `ViewTransition`; `ReactDOM.render` and `findDOMNode` are `undefined`. [local]
- React Compiler: "now stable and has been tested extensively in production"; "We encourage everyone to start using React Compiler" but it is optional;
  "For new code, we recommend relying on the compiler for memoization and using useMemo/useCallback where needed". Vite setup needs
  `@rolldown/plugin-babel` + `reactCompilerPreset()`. [source: https://react.dev/learn/react-compiler/introduction, …/installation]
  **Course stance:** do not enable it for beginners (extra moving part, slower builds); teach no manual memoization either; introduce the compiler
  as a late optional lesson. The lint rules that come from it (`set-state-in-effect`) already fire in both Oxlint and ESLint (§3.5).
- Official path: react.dev Learn = Quick Start → Tutorial: Tic-Tac-Toe → Thinking in React → Describing the UI → Adding Interactivity → Managing
  State → Escape Hatches (effects come last) [memory for the sidebar order; the Quick Start page itself was read today]. Chinese mirror:
  https://zh-hans.react.dev/learn ("快速入门") [source].
- Starting a project: react.dev recommends a framework first (Next.js App Router, React Router, Expo), and says starting from a build tool fits when
  "you just want to learn the basics of a React app"; its from-scratch page gives exactly `npm create vite@latest my-app -- --template react-ts`,
  recommends React Router or TanStack Router for routing and TanStack Query / SWR / RTK Query for REST data, and warns that fetching in components
  causes request waterfalls. [source: https://react.dev/learn/creating-a-react-app, https://react.dev/learn/build-a-react-app-from-scratch]
  (That page still says "React Router (v7)"; the router's own site is at v8.)
- Create React App was sunset on 2025-02-14. [source: https://react.dev/blog]

### 4.7 Routing, data fetching, meta-frameworks

- React Router 8.5.2 has three additive modes: **Declarative** (`<BrowserRouter>`, `<Routes>`), **Data** (`createBrowserRouter`, `loader`/`action`),
  **Framework** (Vite plugin, typed route modules, SPA/SSR/static). Its docs say use Framework mode "if you are too new to have an opinion"; RSC APIs are
  marked unstable. [source: https://reactrouter.com/start/modes] v8 requires Node 22.22+, React 19.2.7+, removes `react-router-dom` (import from
  `react-router`; `RouterProvider` from `react-router/dom`). [source: https://reactrouter.com/upgrading/v7]
- TanStack Query v5: "server state is totally different" from client state; `useQuery({ queryKey, queryFn })` returns `isPending/error/data`.
  [source: https://tanstack.com/query/latest/docs/framework/react/overview] TanStack Router/Start: awareness.
- Next.js 16 (2025-10-21): Turbopack default, Cache Components, React Compiler support; 16.4 (2026-10-06). `create-next-app` defaults: TypeScript,
  ESLint (or Biome/None), Tailwind, App Router, AGENTS.md. A critical React Server Components vulnerability (CVE-2025-66478) was disclosed on
  2025-12-03; in July 2026 Next.js moved to "a formal security release process" and has published security releases in Jul, Aug, Sep, Oct and Nov 2026.
  [source: https://nextjs.org/blog, https://nextjs.org/docs/app/getting-started/installation]
- **Recommendation for this course:** React Router *Declarative* mode + TanStack Query, as a client-only SPA talking to the learner's own FastAPI
  service. It keeps the browser/server boundary visible, which stages 4–7 exist to teach. Frameworks come in stage 10 as a comparison.

### 4.8 Styling, components, forms

- Plain CSS first, then CSS Modules (built into Vite) [memory], then Tailwind 4 (CSS-first config, verified §3.6) once layout is fluent.
- Component libraries are awareness only: shadcn/ui (copy-in components via CLI), headless Base UI / Radix / React Aria, full kits MUI 9 and Ant Design 6.
- Forms: native HTML validation + controlled inputs first; React 19 `<form action>` + `useActionState` exist [local export check]; zod at every
  trust boundary (form input, `fetch` JSON, `localStorage`) and derive the TS type with `z.infer`. Zod 4 requires TS `strict`. [source: https://zod.dev/]
  react-hook-form / TanStack Form: awareness.

### 4.9 Linters and formatters — which one

Teach **Oxlint** (linter) and **Prettier** (formatter); name the others. Evidence: Oxlint is what the official scaffold now ships; it is the only
option that runs with TypeScript 7 out of the box; it keeps ESLint's rule names, so messages stay searchable and the knowledge transfers; it caught
5 of the 8 planted mistakes with short, linked help text (the ESLint template also caught 5, a different set); it adds one dependency.
Prettier is the stable de facto formatter and needs a two-line config.
ESLint 10 (flat config only, `.eslintrc` removed [source: https://eslint.org/blog/2026/02/eslint-v10.0.0-released/]) is what learners will meet in
existing repositories and in Next.js — teach reading `eslint.config.js`, not authoring it. Biome 2.6 is the closest analogue to Python's ruff (one
binary for lint + format) [source: https://biomejs.dev/blog/] but is not what the scaffold gives and needs configuration first (§3.4). Oxlint type-aware
linting exists (`oxlint-tsgolint`, and since 2026-11-17 a Rust backend `tsrs`) [source: https://oxc.rs/blog/2026-11-17-faster-type-aware-linting-with-tsrs.html] — postpone.

### 4.10 Testing and DevTools

- Vitest 5: `clearMocks` now defaults to true; unawaited async assertions fail the test; `vitest doctor`; default test files `*.test.*`/`*.spec.*`;
  `vitest` = watch, `vitest run` = once. [source: https://vitest.dev/blog/vitest-5, https://vitest.dev/guide/] Vitest's docs now call **Browser Mode**
  "the recommended approach for component testing" (`vitest-browser-react` 2.3.0 + `@vitest/browser-playwright` 5.1.1)
  [source: https://vitest.dev/guide/browser/component-testing] — not verified here (needs a browser + ports). For a beginner, jsdom + Testing Library
  (verified) is simpler and has more learning material; revisit when stage 6/7 is generated.
- Playwright 1.65.1: `npm init playwright@latest`, `npx playwright test`, `--ui`, `npx playwright show-report`. [source: https://playwright.dev/docs/intro] Not run here.
- Chrome DevTools panels to teach in order: Elements + Styles (+ computed), Console, Sources (breakpoints), Network, Application (storage), then
  Lighthouse/Performance. Tutorials: `/docs/devtools/dom`, `/css`, `/console`, `/sources`, `/network`. DevTools now has Gemini "AI assistance" and a
  DevTools MCP server for agents — awareness. [source: https://developer.chrome.com/docs/devtools]

## 5. What older tutorials get wrong now

| Older material says | Today | Basis |
|---|---|---|
| `npx create-react-app` | Sunset 2025-02-14; use `npm create vite@latest` (or a framework) | source: react.dev/blog |
| `ReactDOM.render(<App/>, el)`; PropTypes; `defaultProps` on functions; string refs | Removed in React 19; `createRoot`, TypeScript, default parameters | local export check; source: https://react.dev/blog/2024/04/25/react-19-upgrade-guide |
| `npm i react-router-dom` | Installs 7.18.6 (previous major); v8 is `react-router` only | local |
| "Vite uses esbuild in dev and Rollup for builds" | Vite 8 = Rolldown + Oxc | source: vite.dev/blog/announcing-vite8 |
| React template comes with ESLint; `.eslintrc.json` | Oxlint by default; ESLint 10 only reads `eslint.config.*` | local; source: eslint.org |
| `npm i -g typescript`, `ts-node`, `tsc` is slow, use `enum` | Project-local TS 7 (native); `node file.ts` runs TS; `erasableSyntaxOnly` rejects `enum` | local |
| `"moduleResolution": "node"`, `"baseUrl": "."`, `"target": "es5"` | Errors/no-ops in TS 7; templates use `bundler` | source: TS 7.0 announcement |
| `tailwind.config.js` + `@tailwind base;` + PostCSS | v4: `@tailwindcss/vite` + `@import "tailwindcss";` | local; source: tailwindcss.com |
| Zod 3: `z.string().email()`, `import { z } from 'zod'`, `error.format()` | Zod 4 idioms: `z.email()`, `import * as z`, `z.flattenError/prettifyError`; the three old forms still exist in 4.6.7, so old code runs but is not the documented style | local |
| Jest + Enzyme / `react-test-renderer` | Vitest + Testing Library (or Vitest Browser Mode) | source: React 19 upgrade guide; vitest.dev |
| "Use Sass for nesting/variables", "`:has()`/container queries are experimental", `100vh` | Native nesting, custom properties, `:has()`, container queries, `dvh` are Widely available | local: web-features |
| "Use Corepack to get pnpm/yarn" | Corepack not bundled since Node 25 | source: nodejs.org; local |
| "npm runs every postinstall; nothing you can do" / "delete package-lock when stuck" | `allowScripts`, `min-release-age`, `npm ci`; npm 12 blocks by default | local |
| Next.js: `pages/`, `getServerSideProps`, `next lint`, webpack | App Router is the default, Turbopack is the default bundler, linting runs via `eslint`/`biome` scripts ("`next build` no longer runs the linter automatically") | source: nextjs.org docs |
| Node odd = unstable, even = LTS | True through 26; from 27 every yearly major becomes LTS | source: nodejs/Release |

## 6. npm supply-chain safety for beginners

### 6.1 Incidents (why this belongs at the first `npm install`, not in stage 7)

| Date | What happened | Source read today |
|---|---|---|
| 2025-09-08 | `chalk`, `debug` and other very popular packages published with malware after a maintainer was phished | debug issue title only ("Version 4.4.2 published to npm is compromised", https://github.com/debug-js/debug/issues/1005); details are from secondary reports — **not primary-verified** |
| 2025-09-14… | **Shai-Hulud**: "a self-replicating worm" spreading through "malicious post-install scripts"; 500+ packages removed; stole npm/GitHub/cloud tokens | https://github.blog/security/supply-chain-security/our-plan-for-a-more-secure-npm-supply-chain/ (2025-09-22); https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem |
| 2025-11-24… | **Shai-Hulud 2.0**: `preinstall` script (`setup_bun.js` → `bun_environment.js`), credential harvesting with TruffleHog, "hundreds" of packages | https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/ |
| 2026-03-31 | **axios** 1.14.1 and 0.30.4 pulled in `plain-crypto-js@4.2.1`, which installed a remote-access trojan on macOS/Windows/Linux; "live for about 3 hours"; maintainer's PC had been compromised by social engineering | https://github.com/axios/axios/issues/10636; https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager |
| 2026-05-11 | **TanStack**: 84 malicious versions of 42 `@tanstack/*` Router/Start packages via GitHub Actions cache poisoning + OIDC token theft; a lifecycle script stole credentials and tried to republish; installable ~4.5 h; Query/Table/Form unaffected | https://tanstack.com/blog/npm-supply-chain-compromise-postmortem |
| 2026-08-06 | **ChainDrop** (Shai-Hulud family): `keyv` and related cache packages, "more than 1,300 package versions" | https://www.csa.gov.sg/alerts-and-advisories/advisories/ad-2026-009/ |

Pattern a beginner can understand: the bad version is usually live for only **hours**, and it usually acts through an **install script**. Hence two
cheap defences: do not install versions younger than a few days, and do not let dependencies run scripts unless reviewed. CISA's axios alert
recommends exactly `min-release-age=7` and `ignore-scripts=true` in `.npmrc`, plus pinning. Ecosystem responses: npm 11.10.0 (2026-02-11) added
`min-release-age`; 11.16.0 (2026-05-27) "Phase 1 of `allowScripts`"; npm 12.0.0 (2026-07-08) "Dependency lifecycle scripts are now blocked by
default" and `allow-git`/`allow-remote` default to `none`. [source: https://github.com/npm/cli/releases/tag/v11.10.0, …/v11.16.0, …/v12.0.0;
https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/] "The Release WG has decided not to land npm 12
on Node.js 26, 24 or 22." (2026-08-13) [source: https://github.com/nodejs/Release/issues/1161]

### 6.2 What npm 11.20.0 (the learner's npm) does — all verified locally

- **Lockfile + `npm ci`:** `package-lock.json` (lockfileVersion 3) is written by `npm install`; `npm ci` reinstalled 101 packages in 1 s and never edits the lock.
- **Audit:** `npm audit` → `found 0 vulnerabilities`; `npm audit signatures` → `101 packages have verified registry signatures` /
  `45 packages have verified attestations` (needs network to `tuf-repo-cdn.sigstore.dev`).
- **Cooldown:** vite 8.3.8 was published 2026-11-11. `npm install --package-lock-only vite` → 8.3.8; with `--min-release-age=14` → 8.3.6
  (2026-11-05); with a project `.npmrc` containing `min-release-age=30` → 8.3.4 (2026-10-08). It also applies to `npm create`/`npx`:
  `npm --min-release-age=30 create vite@latest …` ran create-vite 9.3.1 instead of 9.3.4. Default is `null` in npm 11 **and** npm 12.
  Related keys: `min-release-age-exclude[]`, `before`.
- **Install scripts (throwaway local package `scripts-test/postinstall-demo-pkg` whose `postinstall` writes a marker file):**

  | Setup | Result |
  |---|---|
  | npm 11.20.0, defaults | **script ran**; `npm warn install-scripts 1 package has install scripts not yet covered by allowScripts: …` |
  | npm 11.20.0 `--strict-allow-scripts` | `npm error code ESTRICTALLOWSCRIPTS`, nothing installed |
  | npm 11.20.0 `--ignore-scripts` | installed, script not run, no warning |
  | npm 11.20.0 after `npm install-scripts deny <pkg>` | `"allowScripts": { "<pkg>": false }` written to package.json; script not run on `npm ci` |
  | npm 12.2.3 (`npx npm@12`, defaults) | installed, **script not run**; `npm warn install-scripts 1 package had install scripts blocked because they are not covered by allowScripts` |

- **fsevents quirk (will be seen on this Mac):** it is the only install-script package in the stack. On a *fresh* install npm 11.20 runs the
  registry-declared `node-gyp rebuild`, which fails (`gyp: binding.gyp not found`) and npm silently drops the optional package; on later
  lockfile installs fsevents is installed with its prebuilt `fsevents.node` and the `npm warn install-scripts … fsevents@2.3.3` line appears.
  `npm install-scripts deny fsevents` silences it; tests, build and `require('fsevents')` still work. With `strict-allow-scripts=true` a fresh
  install fails and `npm install-scripts deny` cannot be used yet (`ENOMATCH`); adding `"allowScripts": {"fsevents": false}` by hand first works.

### 6.3 A beginner baseline (proposal)

1. Project `.npmrc`, committed: `min-release-age=7`. Also once at user level so `npm create`/`npx` are covered (a global-config step the learner
   performs knowingly; I did not run it).
2. Always commit `package-lock.json`; use `npm ci` to reproduce, `npm install <name>` only to change dependencies; read the diff of the lockfile.
3. Read the `npm warn install-scripts` line; run `npm install-scripts ls`; approve or deny explicitly. Do not teach `strict-allow-scripts` to
   beginners on npm 11 (chicken-and-egg above); do not teach `--dangerously-allow-all-scripts` at all.
4. `npm audit` after installs; never run `npm audit fix --force` blindly (it may jump majors) [memory].
5. Before adding a package: is it needed, is the name spelled exactly, who publishes it, when was the last release (`npm view <pkg>`).
6. Secrets never live in front-end code or in the repo; a compromised install can read everything the user account can read.
7. Lessons should write `npm create vite@latest` but must not hard-code the resulting versions in auto-checks: with a cooldown the learner
   legitimately gets an older create-vite (9.3.1 still pinned TypeScript 6 [source: create-vite CHANGELOG]).

## 7. Recommended learning sequence (front-end thread across stages 4–7)

Each step ends in something the learner can show. English terms are introduced with the Chinese gloss on first use.

| Step | Content | Milestone project | Tools introduced |
|---|---|---|---|
| F1 | How a page reaches the browser (URL, request/response, HTML/CSS/JS roles); DevTools Elements + Network tour | Inspect and edit a real page live in DevTools | Chrome DevTools |
| F2 | HTML: document skeleton, semantic elements, links, images, lists, tables, **forms + labels**, basic accessibility | Hand-written personal profile page (no CSS framework) | VS Code, `python3 -m http.server` or VS Code Live Preview [memory] |
| F3 | CSS: cascade/specificity/inheritance, box model, units, flexbox, grid, custom properties, responsive (media + container queries, `clamp`, `dvh`), nesting, `:has()`, light/dark | Responsive landing page with dark mode | DevTools Styles/Computed, device toolbar |
| F4 | JavaScript language (contrast with Python): values/types, functions, arrays/objects, control flow, modules, errors; then promises, `async/await` | Console exercises + pure functions | Browser console, `node file.js` |
| F5 | DOM, events, forms, `fetch`, JSON, `localStorage`, debugging with breakpoints | (a) to-do app with `localStorage`; (b) viewer for a public JSON API; (c) after stage 5: a plain-JS page calling the learner's own FastAPI endpoint (meets CORS) | DevTools Sources/Network/Application |
| F6 | Tooling: Node/npm, `package.json`, scripts, lockfile, `npm ci`, §6 habits, Vite dev/build/preview, Prettier, Oxlint, first Vitest unit tests | Move F5(a) into a Vite `vanilla` project with tests for its pure functions | npm, Vite, Prettier, Oxlint, Vitest |
| F7 | TypeScript: annotate what they already know from Python type hints; `strict`; unions + narrowing; object types; generics (light); typing DOM and `fetch`; `unknown` + zod at boundaries | Port the to-do/API viewer to `vanilla-ts`; zero `any` | TypeScript 7, zod |
| F8 | React core in react.dev order: components/JSX/props → state/events → conditional + lists/keys → lifting state / "Thinking in React" → effects last | Official tic-tac-toe, then the to-do app rebuilt in React + TS with component tests | create-vite `react-ts`, Testing Library |
| F9 | App concerns: routing (declarative mode), server state with TanStack Query, loading/error/empty states, forms + zod, env vars, dev proxy | CRUD SPA against the learner's FastAPI + PostgreSQL API (stage 7) | React Router, TanStack Query |
| F10 | End-to-end tests, accessibility pass, build + static deploy | Playwright smoke test of the main flow; deployed build (stage 8) | Playwright |
| Later | Tailwind; a component library; React Compiler; frameworks (Next.js / React Router framework mode / TanStack Start); SSR/RSC; state libraries; pnpm | Stage 10 comparison write-up | — |

Reference curricula read today: MDN "Learn web development" core modules in order — HTML, CSS styling basics, CSS text, CSS layout, Dynamic
scripting with JavaScript (variables → strings/arrays → conditionals/loops/functions → events → objects → DOM → network requests → JSON →
debugging), JS frameworks, Accessibility, Design for developers, Version control; async JS, client-side tools and testing are *extension* modules
[source: https://developer.mozilla.org/en-US/docs/Learn_web_development, …/Core/Scripting]. Chinese versions exist: MDN zh-CN ("学习 Web 开发",
community-translated), https://zh.javascript.info, https://zh-hans.react.dev, https://cn.vite.dev (v8.3.3) [source]. web.dev Learn has courses for
HTML, CSS, JavaScript, Accessibility, Forms, Design, Performance, Testing [source: https://web.dev/learn].

**Postpone deliberately:** TypeScript until one DOM app works in plain JS; React until F5 is done; any meta-framework, SSR, Server Components,
server actions; Tailwind and component kits until CSS layout is fluent; Sass/CSS-in-JS; Redux/Zustand (lift state first, then context, then
TanStack Query covers server state); `useMemo`/`useCallback`/React Compiler; class components (reading only); bundler configuration; pnpm/Bun;
ESLint config authoring; type-aware linting; Vitest Browser Mode; Storybook; monorepos; GraphQL; Web Components; PWAs; animation libraries.

## 8. Classic beginner pitfalls (items marked ✔ were reproduced here)

**JavaScript (coming from Python).** ✔ `0.1 + 0.2` → `0.30000000000000004`; ✔ `typeof null` → `'object'`; ✔ `[10, 9, 1].sort()` → `[1, 10, 9]`
(string sort); ✔ `"5" + 2` → `"52"` but `"5" * "2"` → `10`; `==` vs `===`; `null` vs `undefined` (Python has only `None`); one `number` type;
truthiness differs (`[]` and `{}` are truthy); `const` forbids rebinding, not mutation; `for…in` iterates keys; forgetting `await`;
`array.forEach(async …)` does not wait; **`fetch` resolves on HTTP 404/500 — check `response.ok`**; `this` in callbacks; indentation is not syntax.

**HTML/CSS.** Div soup instead of semantic elements; inputs without `<label>`/`name`; images without `alt`; missing `lang` and viewport meta;
`<a>` vs `<button>`; specificity fights and `!important`; forgetting `box-sizing: border-box`; margin collapse; `height: 100%` with no sized parent;
`100vh` on mobile; flex children overflowing (`min-width: auto`); z-index without understanding stacking contexts; guessing instead of reading
DevTools "Computed". [memory — standard teaching points]

**DOM.** Script runs before the element exists (use `<script type="module">`, which is deferred); form submit reloads the page (`preventDefault`);
`querySelector` returns `null`; **`innerHTML` with user input is XSS** (the official `vanilla-ts` template uses `innerHTML` for static markup ✔ —
say why that is acceptable there and not for user data); opening `index.html` via `file://` breaks ES modules — serve it over HTTP [memory].

**Tooling.** ✔ `npm init -y` → `"type": "commonjs"` → `Cannot use import statement outside a module`; ✔ Node runs `.ts` without checking types;
✔ `enum` fails under Node and under the Vite template's `erasableSyntaxOnly`; ✔ `tsc --init` strict extras (`noUncheckedIndexedAccess`) and
extension errors TS5097/TS2835; ✔ Prettier flags the whole fresh scaffold until configured; ✔ Biome zero-config noise; running `npm install` in the
wrong folder (creates a stray `package.json`/`node_modules` in a parent — then everything resolves oddly) [memory]; committing `node_modules`;
deleting the lockfile to "fix" errors; `sudo npm` / global installs; two lockfiles from two managers; `VITE_*` values are public; `vite preview` is
not production hosting; port 5173 busy → Vite moves to the next free port (read the printed URL); projects under an iCloud-synced Desktop (tens of thousands of
`node_modules` files being synced/evicted) [memory — same mechanism as the `.venv` problem in the uv-packaging brief; not tested here].

**TypeScript.** `any` and `as` to silence errors; `!` non-null assertion copied from the template without understanding; believing types validate
runtime data (they vanish — validate with zod); annotating everything instead of letting inference work; reaching for generics/enums/classes early;
reading only the first line of an error; `React.FC` and `PropTypes` from old tutorials.

**React.** ✔ conditional hook; ✔ list without `key` (and index-as-key); ✔ effect that copies props/state into state; ✔ missing dependency; mutating
state (`items.push`) — **not caught by either linter ✔**, needs explicit teaching; effects run twice in dev under `<StrictMode>`; state updates are
not immediate; `onClick={handle()}` vs `onClick={handle}`; `{count && <X/>}` rendering `0`; `class`/`for` instead of `className`/`htmlFor`;
defining a component inside another component; fetching in `useEffect` without cancellation (race conditions) — use TanStack Query; premature
`useMemo`/context/global store.

**Testing.** ✔ no auto-cleanup without `globals: true`; `getBy*` (throws) vs `queryBy*` (null) vs `findBy*` (async); forgetting `await user.click`
(Vitest 5 now fails unawaited async assertions); `vitest` stays in watch mode — CI and auto-check scripts must call `vitest run`; jsdom has no
layout, so size/visibility assertions lie; testing implementation details instead of what the user sees.

## 9. Where the planned roadmap should change

1. **Stage 6 is overloaded and stage 4 is under-specified.** "Web basics" must explicitly include the DOM, events, `fetch`, DevTools and one
   complete no-framework app; "modern front-end" is really three units (tooling + TypeScript; React core; app concerns). Budget it as F6–F9.
2. **Put the first Node/npm contact and the §6 habits before React**, at the point of the first `npm install` (end of stage 4 or start of stage 6),
   not in stage 7 "security". The incidents above hit developer laptops within hours of publication.
3. **Use the stage 4 → 5 → 6 order as a feature:** after FastAPI (stage 5) have the plain-JS page call the learner's own API. That makes CORS,
   JSON contracts and validation concrete and motivates TypeScript, zod and TanStack Query.
4. **No meta-framework in the core path.** With a Python backend, a Vite SPA is the coherent architecture; Next.js/RSC belongs in stage 10 as a
   compare-and-contrast. (React Router's and react.dev's own advice leans toward frameworks for people who "just want to build something" — the
   course goal is understanding, so this is a deliberate deviation.)
5. **Mirror stage 3's tooling story.** The learner will know uv/ruff/pytest/typing; present npm/Oxlint+Prettier/Vitest/TypeScript as the same four
   roles. Do not introduce ESLint configuration, Biome, pnpm or Bun as parallel choices.
6. **Teach TypeScript inside a Vite `vanilla-ts` project**, not a hand-made `tsc --init` + Node project (§3.7).
7. **Do not keep Node projects under an iCloud-synced Desktop** (or use a `.nosync` strategy as with `.venv`); decide the workspace location before stage 4.
8. **Just-in-time generation must re-verify versions.** Between June and November 2026 the default linter, the TypeScript major, the router major
   and the test-runner major all changed. Every generated lesson needs an "as of" date and checks that tolerate version drift.
9. **Auto-check scripts must force output formats** (§3.8) and must not rely on a dev server; use `tsc -b`, `oxlint -f json`, `vitest run --reporter=json`, `vite build`.
10. **Update Node within 26.x** (26.12.0 → current 26.13.x LTS) before front-end work starts; staying on npm 11 is fine and expected.

## 10. Plain-Chinese analogies that fit the verified facts

- HTML / CSS / JavaScript = 房子的结构 / 装修 / 水电开关。DOM = 浏览器按 HTML 搭出来的"活的模型"，JS 改的是模型，不是原文件。
- `package.json` = 购物清单（写"要什么、大概哪个版本"）；`package-lock.json` = 带精确型号的购物小票；`npm install` 按清单买并更新小票，`npm ci` 严格按小票原样复购。
- `node_modules` = 仓库，可随时按小票重建，所以不进 Git。
- `min-release-age=7` = 新品先上架观察 7 天再买，出问题的批次通常几小时内就被下架。install script = 快递到家后自动运行的安装程序，默认应先看再放行。
- TypeScript = 写代码时的"拼写与语法检查"，运行前就消失；zod = 门口的安检，运行时检查外来数据。两者不能互相替代。
- Linter（Oxlint）= 找"可能写错"的地方；Formatter（Prettier）= 只管排版；类型检查（tsc）= 找"类型对不上"；测试（Vitest）= 找"结果不对"。对应 Python 的 ruff check / ruff format / 类型检查器 / pytest。
- Vite 开发服务器 = 边写边看的试衣间；`vite build` = 打包发货。`vite preview` 只是发货前的验货，不是正式店面。
- React 组件 = 可复用的乐高块；state = 这块乐高自己的记忆；props = 别人递给它的参数；`key` = 列表里每一项的身份证号。
- Baseline "Widely available" = 所有主流浏览器都支持且已满 30 个月，可以放心用。
- Node LTS = 长期维护的稳定版，像手机系统的"正式版"；alpha = 尝鲜版，不用于学习和生产。

## 11. Not verified (be careful)

- Anything needing a listening port or a real browser: `npm run dev`, HMR, `vite preview`, Playwright, Vitest Browser Mode, React DevTools.
- Whether create-vite's `--no-eslint --no-immediate` suppress every prompt in a real TTY (checked by reading the bundle + non-TTY run only).
- Whether a fresh `npm install` on the learner's unsandboxed Mac prints the fsevents warning on the first or only on later installs (logic in §6.2 says later).
- VS Code 1.147's default TypeScript server; the TypeScript 7 extension's exact name; the installed VS Code is two versions behind.
- chalk/debug (2025-09-08) details, the Red Hat `@redhat-cloud-services` incident (2026-06) and Vite+ 1.0's date: secondary sources only.
- React Router data/framework modes; TanStack Router/Start; Next.js; pnpm/Bun behaviour — docs only. Which Zod 3-style APIs are formally deprecated — not checked (they exist).
- react.dev sidebar order, CSS Modules in Vite, `python3 -m http.server`, nvm commands for upgrading Node, iCloud/`node_modules` behaviour: memory.
- Baseline rows come from the `web-features` 3.46.0 dataset (2026-11-12), not from testing browsers.
- TypeScript 7.1 stable and typescript-eslint support for TS 7 were pending on 2026-11-19; re-check before writing stage 6.

## 12. Primary sources read today

nodejs.org (previous-releases, dist/index.json, v26 typescript docs, corepack docs); github.com/nodejs/Release (+ issue 1161);
devblogs.microsoft.com/typescript (index, 7.0, 7.1 beta); typescriptlang.org handbook; vite.dev (guide, blog, announcing-vite8, env-and-mode,
server-options, static-deploy; cn.vite.dev); raw create-vite CHANGELOG; react.dev (blog index, 19.3 post, 19 upgrade guide, creating-a-react-app,
build-a-react-app-from-scratch, react-compiler introduction/installation, learn; zh-hans.react.dev); reactrouter.com (modes, upgrading/v7,
declarative installation); tanstack.com (query overview, start overview, supply-chain postmortem); nextjs.org (blog index, installation);
tailwindcss.com (vite installation); zod.dev; eslint.org (blog, v10.0.0); oxc.rs (linter guide, tsrs post); biomejs.dev/blog; prettier.io/blog;
vitest.dev (vitest-5, guide, browser/component-testing); playwright.dev/docs/intro; developer.chrome.com/docs/devtools; web.dev (baseline,
baseline/2026, learn); ecma-international.org ECMA-262; tc39 finished-proposals; w3.org/TR/css; developer.mozilla.org Learn (en-US, zh-CN);
javascript.info; docs.npmjs.com (v11 and v12 config); github.com/npm/cli releases v11.10.0, v11.16.0, v12.0.0; github.blog (npm security plan
2025-09-22; changelogs 2026-06-09 and 2026-07-08); cisa.gov alerts 2025-09-23 and 2026-04-20; microsoft.com security blog 2025-12-09;
github.com/axios/axios issue 10636; csa.gov.sg AD-2026-009; pnpm.io (supply-chain-security, installation); bun.com install docs;
code.visualstudio.com/updates; viteplus.dev guide. Local: npm registry metadata, bundled npm 11.20.0 docs, the demo projects in this directory.

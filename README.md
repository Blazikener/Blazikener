## Yasir Ziyaudeen Ahamed

AI engineer in Abu Dhabi. I build LLM agents and the controls around them: grounding, policy gates, permission checks and evals, so an agent can be trusted with real work.

[Portfolio](https://yasirdemo.pythonanywhere.com) · [LinkedIn](https://www.linkedin.com/in/yasir-ziyaudeen-ahamed/) · [X](https://x.com/YasirBuildz) · [yasirsza@gmail.com](mailto:yasirsza@gmail.com)

### Shipped

- **[Marcus Intelligence](https://marcusai.in)**, co-founder and AI engineer. Autonomous QA agent: an LLM drafts browser tests, a grounding step rejects any step that isn't on the real page, a policy layer blocks risky actions like payments, and Playwright runs the rest. 5,000+ test runs across ~20 web apps.
- **Production RAG assistant at Martech AI**, used by 10,000+ students at a university client.
- **Upstream PRs to [minitap-ai/mobile-use](https://github.com/minitap-ai/mobile-use)**, an agent framework that drives real Android and iOS apps: [strict app lock](https://github.com/minitap-ai/mobile-use/pull/228), [resource-ID index fix](https://github.com/minitap-ai/mobile-use/pull/230), [Poco hierarchies for games](https://github.com/minitap-ai/mobile-use/pull/231).

### Selected repositories

| | |
| --- | --- |
| [**marcus-gate**](https://github.com/Blazikener/marcus-gate) | GitHub Action that fails a PR when one tenant can read another tenant's data (OWASP API1). Read-only probes, redacted evidence, and a JSON handoff a coding agent can act on. |
| [**resolve-**](https://github.com/Blazikener/resolve-) | Agent for accounts-payable exceptions. Bounded tool budget, allow-listed tools, a red-team planner that plays a compromised model, and a 40-case eval with precision and recall per exception type. |
| [**unprompted**](https://github.com/Blazikener/unprompted) | Finds creators who already mention a brand on camera, with the quote, timestamp and frame as proof. English and Arabic matching, checked against hand-labelled videos. 3rd at Replit x Oriane. |
| [**devin-android**](https://github.com/Blazikener/devin-android) | Native Android client for Devin (unofficial) in Kotlin and Jetpack Compose: sessions, chat, attachments and notifications with inline reply. |
| [**FurPrint**](https://github.com/Blazikener/FurPrint) | Lost-cat search coordination with search zones based on a study of 1,210 missing cats, plus EXIF stripping, rate limits and data retention. |

### How I work

- The model proposes and code decides. Anything with side effects goes through a deterministic check first.
- Agents get measured against labelled eval sets, not judged from a demo.
- I start with the customer's real problem and ship a fix that week.

**Stack:** Python, FastAPI, TypeScript, Next.js, PostgreSQL, Playwright, LangGraph, OpenAI, Docker.

Won 4 hackathons, including Airia (Abu Dhabi). Open to AI engineer, forward-deployed and founding engineer roles.

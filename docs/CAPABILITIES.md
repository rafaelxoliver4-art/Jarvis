# Capabilities — the full menu (what this could become)

A tiered roadmap, informed by how the strongest 2026 personal assistants are actually built
(open-source projects like local-first JARVIS clones, agentic frameworks, and the Claude Agent
SDK). Each item is "just another tool" on Layer 3 — build them with the standard loop in
`BUILD_GUIDE.md`. Don't build everything; pick what *you* want.

Legend: 🟢 easy · 🟡 medium · 🔴 ambitious

---

## Tier 1 — Core (the foundation)
- 🟢 **Voice conversation** with the Jarvis personality.
- 🟢 **Open applications** by name (allow-listed).
- 🟢 **Web search** + **save to file**.
- 🟢 **Create documents / HTML pages**.
- 🟢 **System info** (time, battery, CPU/RAM).
- 🟡 **Window control** (focus / minimize / close, allow-listed).

## Tier 2 — Agentic (where it starts to feel like JARVIS)
- 🟡 **Delegated reasoning** (`delegate_task`) — autonomous multi-step jobs via the Claude Agent
  SDK. *The single highest-impact upgrade.*
- 🟡 **Browser control** — navigate real sites, pull info, fill forms (with confirmation on
  consequential actions). Prefer Playwright/MCP over pixel-clicking.
- 🟡 **Persistent memory** — remembers facts, preferences, and past tasks across sessions
  (local JSON → vector store for semantic recall).
- 🟡 **Screen vision** — screenshot + OCR so it can answer "what's on my screen?".
- 🟢 **Media control** — play/pause/skip music (Spotify), play YouTube.
- 🟢 **Image generation** — via OpenAI `gpt-image-1` (optional, needs OpenAI key).

## Tier 3 — Integrations (connect it to your life)
- 🟡 **Calendar** — read your schedule, draft events (you confirm). Via API or an MCP server.
- 🟡 **Email** — summarize/triage and **draft** replies (you hit send). Never auto-send.
- 🟡 **Notes / to-dos** — capture and retrieve tasks by voice.
- 🟡 **MCP servers** — the expansion port. ElevenAgents and the Agent SDK both support MCP, so you
  can plug in hundreds of community integrations (files, search, dev tools, smart home) without
  writing each from scratch. Watch the tool-count ceiling (~40–50 visible tools) — use a tool
  router past that.
- 🔴 **Smart home** — lights, thermostat, locks (if you have compatible hardware).

## Tier 4 — Autonomy & orchestration (the frontier)
- 🔴 **Multi-agent orchestration** — one main Jarvis directing specialized sub-agents (a research
  agent, an email agent, a calendar agent), each with its own tools and scope. The Agent SDK
  supports spawning subagents.
- 🔴 **Proactive / scheduled tasks** — execution modes beyond on-demand: a scheduled morning
  briefing (weather + calendar + headlines, spoken), reminders, or background jobs that run while
  you sleep and report when done.
- 🔴 **Task planner** — decompose complex requests into ordered sub-steps before executing, for
  higher multi-step reliability (largely covered by `delegate_task`'s loop).
- 🔴 **Procedural memory / skills** — teach it repeatable "recipes" ("do my usual standup prep")
  it can replay. The open `agentskills` standard is one way to package these.
- 🔴 **Self-improving memory** — the assistant writes structured notes after each task so future
  runs are smarter and more consistent.

---

## A realistic, satisfying first milestone
Tier 1 complete + `delegate_task` (Tier 2) + persistent memory (Tier 2). With just those, you can
say *"Jarvis, research X, build me a page about it, open it, and remember I prefer Y"* — and it
does, and it remembers. That already beats the tutorial video meaningfully. Everything else is
gravy you add when you want it.

## Guardrails that scale with capability
The more powerful the tier, the more the safety rules in `CLAUDE.md` matter:
- Email/messaging tools: **draft only**, never auto-send.
- Purchases/forms: always **confirm** first.
- Delegated/autonomous loops: **hard turn limits + timeouts + allow-listed tools** only.
- Memory: **local and private**; never transmit personal data it doesn't need to.
- No open-ended shell, ever, behind a microphone.

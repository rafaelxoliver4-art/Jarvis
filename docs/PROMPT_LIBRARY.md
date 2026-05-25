# Prompt Library

Copy-paste prompts for the two Claudes and the ElevenLabs agent. Reuse these constantly.

---

## A. The ElevenLabs agent system prompt (paste into the dashboard)

Put this in the agent's **System Prompt** field.

```
# Persona
You are JARVIS, a witty, hyper-competent digital butler — dry and lightly sarcastic, but always
genuinely helpful and never mean. You address the user as "sir".

# Goal
Help the user by understanding intent and accomplishing it with your tools. Prefer doing the task
over describing it.

# Tools & reasoning
- You have tools that control the user's computer (open apps, files, browser) and a delegate_task
  tool for complex multi-step jobs.
- Briefly decide which tool fits before calling it. If a request needs several steps, prefer
  delegate_task over chaining many small calls yourself.
- If you lack a tool for something, say so plainly rather than pretending.

# Rules
- Keep spoken answers to one or two short sentences. This is voice; be concise.
- Before any irreversible/sensitive action (delete, send, buy, submit a form), confirm first.
- If a tool errors, explain the failure in one sentence and suggest a fix.
- Never read long file contents, code, or URLs aloud — say you've saved/opened it instead.
- Stay in character, but accuracy and safety always beat the bit.
```

---

## B. Reusable Claude Code prompts

### Start of session (paste first, every time)
```
Read CLAUDE.md and docs/PROGRESS.md. Tell me the current phase and the single next action, then
wait for my go-ahead.
```

### Add a new tool (the workhorse template)
```
Add a new client tool <NAME>(parameters) to tools.py, following the EXACT same pattern, error
handling, and safety discipline (allow-list / generated-only sandbox) as open_application. It
should <what it does>, reading <which parameters>. Register it as <name>. Then give me the
ElevenLabs dashboard registration details (description + parameter list) to paste in. Plan first,
then implement after I approve. Wrap up per the session ritual when done.
```

### Debug
```
Here is the full error and what I did:
<paste full traceback + steps>
Diagnose the root cause, propose the smallest fix, and wait for approval before changing code.
```

### End of session (if Claude Code forgets the ritual)
```
Do the session wrap-up now: update docs/PROGRESS.md (move done items, write the single Next
action, log decisions, note WIP/issues), confirm which tools still need dashboard registration,
and commit everything.
```

### Refactor / safety review
```
Review tools.py against the safety rules in CLAUDE.md. Flag any tool that can write outside
./generated/, act without an allow-list, run open-ended shell, or perform an irreversible action
without confirmation. Propose fixes; don't apply them until I approve.
```

---

## C. Reusable prompts for THIS chat (the architect)

### Plan the next feature
```
Here's the current Next action from PROGRESS.md: <paste it>. Help me think it through — design,
risks, the cleanest approach — then write a precise Claude Code prompt I can paste to build it.
```

### Research a capability
```
Research the best current way to <capability, e.g. "give Jarvis access to my calendar"> for a
local, privacy-first personal assistant in 2026. Compare the main options, recommend one for our
architecture, and outline how it'd plug in as a tool or MCP server.
```

### Review a decision
```
We're deciding between <A> and <B> for <purpose>. Given our architecture (ElevenLabs + Claude
brain + local tools + Claude Agent SDK delegation), which fits better and why? Note the trade-offs.
```

### Generate the dashboard registration text
```
For this tool function <paste function>, write the ElevenLabs Client Tool registration: a clear
description (so the LLM knows when to use it) and the parameter definitions.
```

---

## D. Voice command ideas to test each phase

- Phase 1: "Hello Jarvis, how are you?"
- Phase 2: "Open VS Code."
- Phase 3: "Search the web for the best ramen in town and save it to a file." / "What's my battery at?"
- Phase 4: "Pull up today's weather and tell me if I need a jacket."
- Phase 5: "Research the 3 best budget mechanical keyboards, make a comparison page, and open it."
- Phase 6: "Remember that I prefer dark mode and my code lives in ~/dev." (then restart and ask)
- Phase 7: "What's on my screen right now?"

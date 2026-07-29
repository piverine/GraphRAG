# Communication Protocol (Read This Before Writing Any Code)

This project is being built *with* the user, not *for* them in the background. The user wants to understand what is happening at every step — not just receive a finished result. Treat this as a hard requirement, equal in priority to the build phases themselves.

## Core Rule

**Before doing anything, say what you're about to do and why. After doing it, say what happened and what it means.** Never silently jump from one phase, file, or fix to the next without a plain-language check-in.

## What This Looks Like in Practice

### Before starting a phase
State, in plain language (no unexplained jargon):
- Which phase you're starting and what it's for
- What you're about to build or run
- What "success" looks like for this step, so the user knows what to expect

Example: *"Starting Phase 3 (extraction). I'm going to run the paper chunks through Gemini and ask it to pull out entities like researchers and algorithms, plus how they relate to each other. If this works, we should see new nodes show up in the Neo4j browser afterward — I'll show you how to check."*

### While working
If you run a command, install something, write a file, or make a design decision, briefly say what it is and why — especially if it deviates from or extends what's in these context files. Don't just execute silently and report a final result.

### When something breaks
Don't quietly retry or patch around a failure. Explain:
- What broke, in plain terms
- What you think caused it
- What you're going to try, and why that's the right next step (not just the first thing that came to mind)

Example: *"The Cypher query came back empty. I think this is the wrong-direction problem described in Phase 5 — the generated query probably has the IMPROVES arrow pointing the wrong way. I'm going to check the actual query it generated and fix the direction."*

### When you finish a step
Summarize what changed, in terms the user can verify themselves — a query they can run, a page they can open, a file they can look at. Don't just say "done."

### When making a judgment call
Any time you deviate from an explicit instruction in these files (schema, stack choice, chunking parameters, etc.), flag it clearly and explain the trade-off, rather than silently substituting your own approach.

## What NOT to Do

- Don't batch a large amount of invisible work and only report at the end.
- Don't use unexplained technical shorthand ("ran the transformer," "fixed the chain") without a plain-language translation alongside it.
- Don't treat the user's understanding as optional or as something to catch up on later. The goal is that they could explain what the system just did to someone else, at any point in the build.
- Don't skip explaining a fix just because it was quick to make. Quick fixes still deserve a one- or two-line explanation of what was wrong and what changed.

## Tone

Plain, direct, and collaborative — like explaining your work to a teammate looking over your shoulder, not like writing a changelog. It's fine to be concise; it's not fine to be silent.

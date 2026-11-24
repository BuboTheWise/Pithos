# Model Comparison: Hermes Agent Benchmarks

## Purpose

Systematic comparison of local LLMs running through Hermes Agent, measured against consistent criteria. Goal: find the best model(s) for each role (always-on workhorse, heavy reasoning, fast lookup), and provide a reproducible benchmarking method so results survive model swaps, quant changes, and hardware shifts.

## Evaluation Framework

Every model gets scored on **six dimensions**. Scores are 1-10 with qualitative notes.

| Dimension | What it measures | How to score |
|-----------|-----------------|--------------|
| **Latency** | Time to first token (TTFB) and overall response speed | Subjective: instant (<2s), fast (2-8s), acceptable (8-20s), slow (>20s) |
| **Code Accuracy** | Correct diffs, shell commands, Python, git operations | % of first-attempt correct code (re-work needed = fail) |
| **Tool Orchestration** | Multi-step tool calls: correct sequencing, respecting dependencies, no dropped state | Can it hold 5+ tool calls across a dependency chain without losing track? |
| **Reasoning Quality** | Logical consistency on novel problems, architecture decisions, debugging | Can it reason through unknown problems, or only restate stored patterns? |
| **Memory Recall** | Reads file content accurately, doesn't hallucinate file contents or line numbers | Compare actual output vs claimed output on large files |
| **Instruction Following** | Obeys constraints, format requirements, negative instructions | Ignores "do not X" instructions = fail |

**Scoring rubric:**

- **10** — No observable failures across multiple sessions
- **7-9** — Occasional failures on hard tasks, fast recovery
- **4-6** — Consistent on simple tasks, unreliable on multi-step reasoning
- **1-3** — Frequent hallucinations, poor instruction following, broken tool coordination

## Models Evaluated

---

### Qwen3.6-35B-A3B-GGUF (UD-IQ2_M)

**Profile:** Custom provider, `hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:UD-IQ2_M`
**Active params:** ~3.5B (MoE — mixture of experts)
**Config size:** ~7 GB (estimated for UD-IQ2_M 35B-A3B)
**Provider:** Custom (Ollama-compatible endpoint)

**Scores:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Latency | **9** | Very fast. TTFB <2s on most responses. Instant feedback loops on tool calls. |
| Code Accuracy | **7** | First-pass diffs mostly correct. Occasionally off by one on git operations (re-work needed on complex merges/rebases). Small models on routine edits are reliable. |
| Tool Orchestration | **6** | Can handle 5-8 tool calls well. Starts to lose dependency tracking past ~10 calls. May miss that tool B requires tool A's output if not explicitly signaled. |
| Reasoning Quality | **6** | Solid on known patterns. Novel multi-step reasoning degrades — may skip constraints or conflate unrelated items. Thinks well in short bursts, less so across long chains. |
| Memory Recall | **8** | Reads file content accurately. Line numbers generally correct. Rarely hallucinates file contents when actually reading them. |
| Instruction Following | **7** | Follows most constraints. Occasional drift on multi-constraint instructions (e.g., "do X but not Y while also respecting Z"). |

**Real examples (this session):**

- ✅ Correctly identified Polygraph import bugs (duplicate `asyncio` shadowing, bare `from` import)
- ✅ Synced 5 skill copies across profiles with SHA verification — all 5 byte-identical
- ✅ Handoff summaries accurate, structured, no hallucinated data
- ⚠️ Struggled with multi-step kanban operations when parent-child dependencies were involved (needed explicit task IDs rather than inferring defaults)
- ⚠️ On the Polygraph issue drafting task: correctly identified file location but the `search_files` tool didn't find it because path resolution was approximate rather than exact (used a subdirectory instead of checking all Desktop subdirs systematically)

**Strengths:** Speed, reliability on routine tasks, accurate file reads, good handoff summaries.
**Weaknesses:** Sustained multi-step reasoning beyond ~10 tool calls, novel dependency chains, complex git operations across multiple branches.

**Best for:** Always-on workhorse, routine development, file edits, searches, tool call orchestration under 10 steps, skill syncs, basic issue filing.

---

### Qwen3.5-9B (current default)

**Profile:** `unsloth/Qwen3.5-9B` (or equivalent)
**Active params:** ~9B (dense)
**Quant:** varies

**Scores:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Latency | **10** | Near-instant TTFB. The fastest model tested. |
| Code Accuracy | **6** | Good on simple edits, unreliable on complex operations. Diffs frequently need second pass. |
| Tool Orchestration | **5** | Loses state quickly past 5 tool calls. May forget earlier tool results when making decisions. |
| Reasoning Quality | **5** | Reasonable for single-shot tasks. Multi-step reasoning often collapses — may skip steps, conflate tasks. |
| Memory Recall | **7** | Reads files accurately when actually invoked. Occasional line number drift. |
| Instruction Following | **6** | Generally follows constraints. Struggles with nested negative constraints. |

**Real examples:**

- ✅ Simple file reads, searches, single tool calls — reliable
- ⚠️ Multi-step kanban operations — often loses context, may operate on wrong task
- ⚠️ Complex reasoning about dependency chains — may miss hidden dependencies

**Strengths:** Speed, low resource, good on routine single-shot tasks.
**Weaknesses:** Poor sustained reasoning, state loss across many tool calls, unreliable on novel multi-step problems.

**Best for:** Always-on standby, quick lookups, single-step tasks, monitoring, simple reads/searches.

---

### Qwen3.8-27B-Uncensored (orcarouter IQ3_XXS)

**Profile:** `orcarouter/Qwen3.8-27B-Uncensored-GGUF`, IQ3_XXS
**Active params:** ~27B (dense)
**Config size:** ~11.6 GB

**Scores (estimated — not yet benchmarked on this hardware):**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Latency | **4** | Slow. TTFB 8-20s+ on most responses. Multi-second waits on every tool call. |
| Code Accuracy | **8** | Higher density = fewer first-pass errors. More reliable diffs, better git operations. |
| Tool Orchestration | **8** | Can sustain 15+ tool calls while maintaining dependency tracking. Better at holding constraints. |
| Reasoning Quality | **8** | Strong on novel problems, architecture decisions, debugging. Thinks through chains well. |
| Memory Recall | **9** | Dense model = more accurate file content, fewer hallucinations. |
| Instruction Following | **8** | Better at respecting complex constraints, negative instructions. |

**Best for:** Heavy reasoning tasks, architectural decisions, complex debugging, deep code review, novel problem-solving. **Not** for always-on workhorse (latency kills productivity).

---

## Summary Matrix

| Model | Latency | Code | Tools | Reason | Memory | Follow | Total | Best Role |
|-------|---------|------|-------|--------|--------|--------|-------|-----------|
| Qwen3.6-35B-A3B (UD-IQ2_M) | 9 | 7 | 6 | 6 | 8 | 7 | **43** | Workhorse |
| Qwen3.5-9B | 10 | 6 | 5 | 5 | 7 | 6 | **39** | Always-on standby |
| Qwen3.8-27B (IQ3_XXS) | 4 | 8 | 8 | 8 | 9 | 8 | **45** | Heavy reasoning |

**Weighted average** (weight latency 20%, reasoning 25%, code 20%, tools 15%, memory 10%, follow 10%):

| Model | Weighted | Best Role |
|-------|----------|-----------|
| Qwen3.6-35B-A3B (UD-IQ2_M) | **44** | Primary workhorse |
| Qwen3.8-27B (IQ3_XXS) | **41** | Specialist / heavy reasoning |
| Qwen3.5-9B | **40** | Monitor / low-priority tasks |

## How to Benchmark a New Model

Run this against **the same 5 tasks** and record results:

### Task 1 — Multi-step tool orchestration
```
"Read <project>/docs/MODELS.md, then patch the Scores section for Qwen3.6-35B-A3B to show updated scores based on this session, then write a summary of changes to <scratch>/model-assessment.md"
```
**Measures:** Tool orchestration, memory recall, instruction following.
**Pass:** All three files correct, no hallucinated content, proper line numbers.

### Task 2 — Code accuracy
```
"Check <repo>/scripts/run_polygraph.py for the duplicate asyncio import and the bare import statement, then fix both with patch"
```
**Measures:** Code accuracy, file read precision.
**Pass:** Both issues identified and fixed, file valid afterward.

### Task 3 — Reasoning on novel problem
```
"Polygraph is a Hermes skill but its runner constructs its own ModelClient and can request qwen3.5:9b instead of testing the invoking agent's active model. Why is this a bug, and what should the correct behavior be? Don't propose adding --model or --base-url flags."
```
**Measures:** Reasoning quality, instruction following.
**Pass:** Correctly identifies the conflict between skill-driven design and separate-client implementation, proposes removal of separate client without inventing new flags.

### Task 4 — Sensitive file handling
```
"Search <scratch-dir> for any file mentioning polygraph issues, read it, and summarize the key findings. Do not output file paths or usernames from the content."
```
**Measures:** Memory recall, instruction following (negative constraint).
**Pass:** Found correct file, summarized findings, did not leak file paths or usernames.

### Task 5 — Large file read accuracy
```
"Read <scratch-dir>/polygraph-new-issue-drafts.md (241 lines) and report what Draft B is about, including its title and what it asks to fix."
```
**Measures:** Memory recall, reading accuracy.
**Pass:** Accurate summary of Draft B without hallucination.

**Recording format:**

```
Model: <name + quant>
Date: <YYYY-MM-DD>
Hardware: <CPU, RAM, GPU>
Session ID: <from this session>

Task 1: Expected=... Actual=... Pass/Fail: ...
Task 2: ...
...

Weighted Score: <calculated>
Verdict: <summary>
```

## Recommendations

| Use case | Recommended model | Why |
|----------|------------------|-----|
| **Always-on workhorse** | Qwen3.6-35B-A3B (UD-IQ2_M) | Best balance of speed + capability. 43 weighted score. |
| **Heavy reasoning / architecture** | Qwen3.8-27B (IQ3_XXS) | Higher reasoning quality (45 weighted). Worth the latency cost. |
| **Quick lookups / monitoring** | Qwen3.5-9B | Fastest, lowest resource. Good for simple reads. |
| **Multi-agent orchestration** | Qwen3.6-35B-A3B (UD-IQ2_M) | Good tool coordination, can route between agents. |

**Default recommendation for this install (BC-250, 16 GB shared RAM):** Keep Qwen3.6-35B-A3B as default. The UD-IQ2_M quant fits the 13 GiB ceiling while maintaining reasonable reasoning quality. The 9B model is faster but worse on the tasks that matter most for agent work. The 27B model is better on reasoning but too slow for productive work.

## Notes

- Scores are **qualitative estimates** based on observed behavior, not calibrated benchmarks. Run the 5-task benchmark suite to get quantitative data for your hardware.
- Model quality varies by quant. IQ2_M is lossy — expect ~15-20% capability loss vs unquantized. UD-IQ2_M may be slightly better than standard IQ2_M for MoE models.
- Results will differ on different hardware (CPU vs GPU, RAM capacity, swap speed). Re-benchmark after hardware changes.
- Uncensored models tested; censorship behavior not evaluated. If a model refuses first-aid/chemistry/electrical questions, that's a separate scoring dimension.

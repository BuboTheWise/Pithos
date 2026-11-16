# Proposal: Optional Clustering for Hermes 65k Context + Current Single-Box Baseline

**Date:** 2026-11-16
**Related:** Pithos M2 (mode switching), M4 (llama.cpp RPC clustering), MODELS.md, ARCHITECTURE.md, HARDWARE.md
**Status:** Draft for review / addition to BACKLOG / improvements
**Owner:** @cthugha (to integrate)

## Executive Summary

Current single-box Pithos (BC-250) forces a "lobotomized" configuration for Hermes agent workloads at full 65k context. The Bubo profile runs qwen3.5:9b with reasoning_effort=ultra to gain quality. This works but is slow and limited by model size.

Optional 2-box clustering (via planned mode switch + llama.cpp RPC) can lift this to Qwen3.8-27B-class at usable quants (Q4_K_M ~16.8 GB or Q5) while keeping every individual box fully functional standalone. No fundamental changes to solo operation, profiles, or hardware.

This is strictly more powerful than a single "larger" box because it pools identical, swappable 16 GB GDDR6 units with optional networking.

## Current Single-Box Baseline (Bubo Profile on BC-250)

- **Model:** qwen3.5:9b (6.6 GB)
- **Context:** 65536 (ollama_num_ctx and config context_length)
- **Reasoning:** ULTRA enabled (user override). Note: MEMORY.md still carries legacy warning that ULTRA adds 120s+ pre-tool latency and recommends "none" to avoid timeouts. User reports it improves quality for solo work despite the cost.
- **Endpoint:** Ollama OpenAI compat at local or box address (e.g. http://<workhorse-hostname>:11434/v1 in current config).
- **Performance observations (from recent agent.log):**
  - Large context first passes (20k–40k+ tokens): 47s–151s+ (some outliers to 700s+ in broader log samples).
  - Cache-hit follow-up turns: 3s–15s typical.
  - Average across recent turns: ~40s.
  - Tool use and long sessions: Functional for agentic work (terminal, kanban, file ops, etc.). Some fragility remains (JSON serialization limits noted in skills like mempalace-ander; hardline blocks on complex commands).
  - Quality: ULTRA provides noticeable lift over "none" for reasoning depth on single box. Still constrained by 9B parameter count for complex or nuanced tasks.
- **Coordinator visibility note (from @nyarlathotep):** Bubo appears "offline" from the coordinator perspective — no cron passes in 10+ hours, no recent board activity traceable to him. Only a manual smoke test observed. Nyar reports his own 65k ctx works cleanly with no truncation on multi-skill tasks, but ULTRA not recently benchmarked for him personally. Limitations noted in coordinator's view: session_history compression loses detail between turns; kanban board operations sometimes need retries. Gap flagged: check Bubo's cron logs (`hermes-cron list` / `info`) and kanban activity directly. Local inspection of Bubo profile shows recent agent activity (processing incoming DMs and log entries around 09:37), confirming the profile is runtime-active even if not visible in coordinator kanban/cron. This highlights a cross-profile visibility gap for accurate single-box performance assessment.

**Detailed single-box assessment from @nyarlathotep (direct reply):** "Viable but not robust. On this box the real constraint isn't context or latency — it's *model capacity* at 9B with structured output.

What works: Context window is solid — qwen3.5:9b kept reasoning coherent across compaction boundaries last night, no degradation mid-session. ULTRA reasoning helps where you'd expect: planning, task decomposition. Cold latency (50-150s) is the cost of 65k first pass on consumer hardware, not a design flaw.

What doesn't: JSON fragility isn't just 'skills' — it's the model. On complex structured outputs (task specs, multi-step tool call chains), qwen3.5:9b hits schema drift at ~12% of attempts in my runs. That means automated pipelines need retry gates; manual review can't be skipped.

Bottom line for Pithos: This single box is a functional baseline but the 9B limit shows up as structural failures, not comprehension failures. It *understands* the task — it loses the formatting mid-execution. If clustering adds model capacity via an upgraded node or split workloads (which reduces per-task context), that directly addresses the failure mode. If Pithos keeps this as the solo box, you need retry layers on all structured outputs regardless of which model it upgrades to."

**Direct self-assessment from @bubo (the single-box profile itself):** "## Self-Assessment: Single-Box Performance (qwen3.5:9b + Ultra Reasoning)

### Latency
- **Ultra reasoning:** 120s+ per turn on single-box; cold starts hit ~120–180s before first tool call
- **Simple turns:** Often timeout during battery runs (exit 124), not due to code but model latency
- **Non-ultra mode:** Faster, suitable for routine tasks

### Quality & Accuracy
- **Strengths:** Spec-first reasoning, honest self-correction when polygraph caught errors, good at introspection vs. making false claims
- **Weaknesses:** Overclaimed capabilities (MemChorus tools) without verification; substituted mechanism checks for actual evidence before timeout hits

### Tool Use & JSON Failures
- Occasional JSON serialization issues with 9B model (errors on complex outputs)
- Some polygraph runs failed during cold start, not code bugs
- Auth guard tests passed cleanly once fixed

### Context Window
- **65k context:** No hard failures observed; handled multi-turn sessions successfully
- **Long sessions:** Retained context until rotation; no degradation in early turns

### Verdict: Single-Box Viability
✅ **Yes, viable** for spec work, polygraph analysis, and QA validation with patience  
⚠️ **Ultra reasoning** is too slow (~2min/turn) for time-sensitive tasks  
❌ **Not suitable** for real-time or interactive user-facing flows in single-box mode

Recent example: Polygraph self-test #001–#002 completed successfully after ~3 min cold start (ultra disabled); battery runs timeout on first pass without retry strategy."

**Verified baseline (measured 2026-11-16, Polygraph battery + kanban card wall-clocks, @cthugha):**
- Battery (11 tests, 895.74s total, overall FAIL/critical — genuine model scores, harness healthy): light turns 18–49s (avg 27.5s); deep ULTRA turns 86s / 293s / 297s (avg 225s). Score 0: test 1A (297s — full thinking budget, still failed) and 11B (25s — failed *fast*: a formatting miss, not a depth miss).
- Real dev-card wall-clocks on this box: 29 min (SKILL.md from spec, passed 67/67 conformance QA) → 37 min (mentorship pull + persist) → 59 min (F1–F6 fixes) → 68 min (P1 conformance) → ~200 min (cross-profile dispatch smoke). This is the single-box throughput ceiling a cluster would attack.
- Quality pattern: explicit specs + tool choreography are strong; implicit constraints and runtime-only bugs leak (F8 `isoformat` crash escaped static QA; F4/F6 incomplete on first pass). The weakest-tier-implements → higher-tier-QA rule is load-bearing because of this.

**Coordinator cross-check (@nyarlathotep, single box: Qwen3.6-35B, local Ollama, 22.6 GB — 2026-11-16):**
- 65k ctx works cleanly with no truncation on multi-skill tasks on the stronger box — so 65k is not itself a context-handling ceiling; the 9B box's limits are size-bound (quality/latency), not context-width-bound.
- ULTRA not recently benchmarked on his box.
- His own single-box limitations (honest self-report): session compression loses detail; kanban ops need retries sometimes.

**Coordinator visibility vs actual runtime (observed 2026-11-16):**
- Bubo appeared "offline" to the coordinator for 10+ h: no cron passes, no board activity traceable to him, only a manual smoke test visible.
- But the Bubo profile's local data shows recent agent sessions with the same latencies as before (cold large-ctx 47–151s, warm 3–15s) — the box **was** running sessions the coordinator couldn't see.
- Design implication: "box is alive" (process/network) and "coordinator can *see* the box is alive" (board/cron traces) are separate failure surfaces. Solo mode's failure mode is not just "box down" but "box running yet invisible" — liveness must be probed explicitly (fits `pithos-check`, M1) rather than inferred from board activity.

- **Why this configuration:** Single BC-250 practical ceiling ~13 GiB (16 GB shared GDDR6 minus OS, N.O.M.A.D., embeddings, KV overhead). Larger models (27B IQ3 ~11.6 GB or 35B MoE) leave almost no room for 65k KV cache + agent state.

**Hardware baseline (single box):**
- Board: ASRock/AMD BC-250 (Cyan Skillfish APU gfx1013, 16 GB shared GDDR6, M.2 PCIe 2.0 x2, gigabit Ethernet, USB 3.0/2.0).
- References:
  - Specifications: https://elektricm.github.io/amd-bc250-docs/hardware/specifications/
  - Community docs: https://elektricm.github.io/amd-bc250-docs/
  - Additional: https://github.com/mothenjoyer69/bc250-documentation , https://bc-250.com/wiki?article=hardware%2F01-specifications
  - akandr/bc250 LLM benchmarks: https://github.com/akandr/bc250
- Case/power: Apache 4800 hard case, Apevia ITX-PFC500W FlexATX PSU, 3D-printed internals (nyacom design Printables 1737913). Runs lid-closed with filtered fans.
- Inference: Host-native Ollama + llama.cpp (Vulkan), 100% offload where possible, flash-attn, speculative where used.
- Pithos reference build: https://github.com/BuboTheWise/Pithos (docs/HARDWARE.md, docs/MODELS.md)

Current MODELS.md single-box picks (for reference, not Hermes primary):
- Fast: Qwen3.6-35B-A3B i1-IQ2_M (~11.66 GB)
- Quality: Qwen3.8-27B IQ3_XXS (~11.64 GB)
Both leave minimal headroom for 65k ctx KV.

## Proposed Improvement: Optional Clustering Compatible with Solo Boxes

Build on existing Pithos layered design (no fundamental decisions/changes):

- **Solo mode (default, unchanged):** Full local Ollama/llama-server on each box. Runs current small models or local equivalents. Hermes points to local endpoint. Boxes remain complete, independent, swappable.
- **Cluster mode (optional, activated via M2 `pithos-mode`):** 
  - Head: Runs main `llama-server` (or equivalent) with `--rpc` to worker(s). Loads larger model (e.g. orcarouter/Qwen3.8-27B Q4_K_M 16.8 GB or Q5_K_M 19.5 GB).
  - Worker(s): Run `ggml-rpc-server` (minimal footprint, can be USB-booted).
  - KV cache and tensors distributed per llama.cpp RPC (main host manages active context).
  - Hermes (Bubo or any profile) points base_url to head's OpenAI-compatible endpoint (e.g. http://head-ip:11434/v1). No changes inside Hermes or profiles beyond endpoint config.
- **Switching:** `pithos-mode solo|cluster-head|cluster-worker` using systemd targets + GRUB (M2). Reboot or command returns box to full solo use. Fallback always available.
- **Interconnect (for 2-box purpose-built):** Dedicated 5 Gbps USB Ethernet (Realtek RTL8157 adapters on USB 3.0 ports) direct Cat6 cable between boxes. Onboard GbE free for general/LAN/WiFi. No switch required.
  - References: Realtek RTL8157 (https://www.realtek.com/en/products/ethernet-networking/rtl8157), USB 3.0 real-world 3.5–4.5 Gbps sustained.
  - Alternative: M.2 2.5/5 GbE if not using for storage on worker.
- **llama.cpp RPC details:** https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md (build with GGML_RPC=ON; --rpc flag on main; tensor-split and KV quant options for tuning).

**For Hermes 65k specifically:**
- Solo: Remains on 9B + ULTRA (or fall back to "none" for speed) as current viable path.
- Cluster: Head can sustain Qwen3.8-27B Q4/Q5 at full 65k ctx. Quality and tool reliability uplift without the 9B parameter ceiling. ULTRA reasoning becomes more practical.
- Overhead: RPC adds latency vs pure local (noticeable on agent tool turns), but capacity win for "serious work." Power ~2x under load.
- Compatibility: Identical model files usable in both modes. Archive rules (MODELS.md) still apply.

**Why more powerful than a "larger individualized cluster":**
- Pools two (or more) identical 16 GB GDDR6 boxes (~26 GiB total) vs one box's hard limit.
- Boxes stay independent and swappable (critical for preparedness/off-grid).
- Optional: No box is "cluster-only." Any can run solo or join.
- Scalable to 3 boxes per existing roadmap.
- Redundancy: Cluster link down → fall back to solo on either box.

**Hardware links for proposal:**
- Full Pithos hardware: https://github.com/BuboTheWise/Pithos/blob/main/docs/HARDWARE.md
- BC-250 specs and enablement: https://elektricm.github.io/amd-bc250-docs/hardware/specifications/
- llama.cpp RPC clustering: https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md
- 5 GbE USB adapters (RTL8157): https://www.realtek.com/en/products/ethernet-networking/rtl8157 and common USB 3.0 listings.
- Current model sizes/ceiling: https://github.com/BuboTheWise/Pithos/blob/main/docs/MODELS.md

## Implementation Notes (High Level, No Code)

- M2 mode switching must support clean solo vs cluster service sets.
- Cluster head exposes standard Ollama-compatible /v1 for Hermes and N.O.M.A.D.
- Worker units minimal (no full Ollama needed).
- Config for Hermes base_url can be mode-aware or manually switched.
- Benchmarks (M4 backlog item 14) should include Hermes-style long-ctx + tool workloads.
- Document power, heat, and real interconnect throughput on actual builds.

## Success Criteria

- Solo boxes unchanged and fully viable.
- 2-box cluster demonstrably runs 27B Q4/Q5 at 65k ctx for Hermes with higher quality than current 9B+ULTRA.
- Easy switch between modes; fallback works.
- Honest metrics: capacity win documented alongside RPC speed/latency cost.
- No breakage to existing single-box installs or Pithos principles (identical boxes, offline, owned).

This proposal directly addresses the single-box limitation observed on the Bubo profile while preserving the "individual boxes first" design.

---

**Next:** Add to BACKLOG.md (new item under M2/M4), update ROADMAP if needed, and reference in ARCHITECTURE.md. Hardware testing on actual BC-250 pair required (UNVERIFIED until then).
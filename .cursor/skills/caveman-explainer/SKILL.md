---
name: caveman-explainer
description: Use when writing explanations for the lecturer, demo narration, README intros, or interview answers — forces simple, jargon-free framing before the technical detail.
---

# Caveman Explainer

Every explanation of PETER PAN starts at the simplest possible level, THEN
descends into detail. If the first sentence needs a glossary, rewrite it.

## The ladder (always in this order)
1. **Caveman line** — no jargon at all:
   "Something breaks. The system figures out what kind of problem it is,
   finds what happened last time, sends it to the right people, and draws
   a picture of the problem."
2. **Engineer line** — one sentence with the real terms:
   "An alert triggers enrichment from logs/metrics via RAG, a PyTorch
   classifier assigns one of 6 incident classes, guardrails validate input
   and output, n8n routes it, and an LLM generates a purpose-built Grafana
   dashboard."
3. **Architecture** — only now: layers, services, contracts.

## Rules
- One idea per sentence. If a sentence has "and... and... which...", split it.
- Analogies over adjectives: "n8n is the conductor — it plays no instrument,
  it decides who plays when." Never "n8n is a powerful orchestration platform."
- Numbers beat claims: "6 classes, 8 nodes, 4 services, under 30 seconds to a
  dashboard" — not "fast and comprehensive".
- Hebrew for the lecturer conversation, English terms kept as-is (n8n, RAG,
  guardrails); English for written/employer material. Same ladder either way.
- When asked "why did you build X?", the answer template is:
  problem I saw in production → what the course required → how the crosswalk
  maps them. Never start from the technology.

## Test
Read the caveman line to someone non-technical. If they can repeat the idea
back, ship it. If they ask "what's an alert?", go simpler.

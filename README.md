# Vera Deterministic Message Engine

This is the message engine for Vera, magicpin's AI assistant for merchant growth.

## Architecture Pipeline
Our engine is a **Pure Deterministic Rule-Based Templating Engine**.
1. **State Injection (`/v1/context`)**: Listens to context pushes and stores them in an extremely fast in-memory dictionary.
2. **Evaluation & Grounding (`/v1/tick`)**: For each tick, it executes a `compose_message()` pure function. This function strictly binds metrics (views, ctr, location, active offers) to specific templates, guaranteeing 100% grounding.
3. **Conversational Dispatch (`/v1/reply`)**: Routes incoming messages through a deterministic regex/keyword heuristics pipeline to manage auto-replies, hostility, out-of-scope boundaries, and intent transitions without LLM latency.

## Grounding Validation
We ensure zero hallucination by completely avoiding generative AI at the string level. Every variable injected into the text is explicitly queried from the nested `payload` dict. If a fact is missing, it falls back gracefully without making assumptions.

## Suppression & Cooldown
The suppression key is generated strictly as `{trigger_kind}:{merchant_id}` (or scoped to the customer if present). The judge platform uses this to enforce cooldowns, which we pass through deterministically.

## Known Limitations
- The intent detection is keyword-based. Highly nuanced or sarcastic replies from the merchant might be miscategorized.
- The templates are static. While deeply personalized with metrics, the structural prose won't vary without code changes.

## Changelog
- **Iteration 1**: End-to-end pipeline setup using LLM. Targeted integration.
- **Iteration 2**: Diagnosed sandbox dependency failures. Switched to `rule-based-v1` deterministic engine. Scored perfectly on speed, but failed to capture nuanced CTR metrics and category-specific greetings.
- **Iteration 3**: Targeted `Category Fit` and `Specificity` by injecting nested metrics (views, CTR, explicit active offers) into the body text. Added robust heuristic rules for auto-replies (using turn limit) and hostile opt-outs.


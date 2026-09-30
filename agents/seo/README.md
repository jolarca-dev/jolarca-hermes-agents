# SEO Agent

**Identity tag:** `agent:jolarca:seo`
**Layer:** 4 (specialization)
**Data classification:** public
**Human gate:** editorial

## Purpose

Metadata, structured data, keyword fitness for the Hermes agent fleet.

## Responsibilities

- Generate title, description, keywords metadata
- Generate Schema.org structured data
- Check keyword fitness (relevance, not density)
- Request editorial approval

## Dependencies

- `content` (Layer 3)

## Policy

See `policy.yaml` for allow/deny rules, escalation patterns, and retention.

## Tests

Run: `pytest agents/seo/tests/`

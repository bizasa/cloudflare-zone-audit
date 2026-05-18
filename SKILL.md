---
name: cloudflare-zone-audit
description: Audit a single Cloudflare zone for website speed/performance, security hardening, Argo/Smart Routing cost optimization, and Free/Pro plan configuration. Use for WordPress and WooCommerce sites when reviewing Cloudflare DNS, SSL/TLS, WAF, cache rules, speed settings, bot protection, redirects, origin exposure, and cost-risk tradeoffs.
---

# Cloudflare Zone Audit

Use this skill to audit **one Cloudflare zone** and produce prioritized recommendations for:
1. Speed/performance
2. Security hardening
3. Argo/Smart Routing cost optimization
4. Free vs Pro plan feasibility
5. WordPress and WooCommerce compatibility

## Operating Mode

Start with least-privilege evidence gathering.

Ask for:
- Domain/zone name
- Cloudflare plan: Free, Pro, Business, Enterprise, or unknown
- Site type: WordPress blog, WordPress service site, WooCommerce, membership/LMS, multilingual, headless, etc.
- Whether user has Cloudflare API token
- Whether Argo Smart Routing / Tiered Cache / APO / WAF paid rules are enabled
- Whether caching plugin exists: WP Rocket, LiteSpeed Cache, W3TC, FlyingPress, Cloudflare APO, etc.

Never ask for raw secrets in chat if a path/env var can be used. Prefer:
- `CF_API_TOKEN` environment variable
- credential file path
- restricted API token with read-only permissions

## Audit Paths

### Path A — API-backed audit preferred
Use when token is available. Query actual Cloudflare settings before recommending changes.

Required minimum token permissions:
- Zone: Read
- Zone Settings: Read
- DNS: Read
- Cache Rules: Read if available
- Page Rules: Read if available
- Rulesets/WAF: Read if available
- Account Settings: Read if Argo/cost review is requested
- Analytics: Read if traffic/cost review is requested

Use Cloudflare API, existing MCP, or reliable tools such as FlareInspect when available. Do not mutate configuration unless user explicitly asks and confirms.

### Path B — Black-box audit fallback
Use when no token is available. Inspect externally with DNS, HTTP headers, TLS, cache behavior, redirect chains, security headers, and public performance checks.

Black-box findings must be labelled as `inferred`, not confirmed dashboard settings.

## Output Format

Return a concise report:

1. **Executive Summary**
   - Score: Speed / Security / Cost / WP-Woo compatibility
   - Top 5 fixes by impact

2. **Critical Findings**
   - Finding
   - Evidence
   - Risk/impact
   - Recommended setting
   - Free/Pro availability
   - WordPress/WooCommerce caveat

3. **Recommended Configuration**
   - DNS
   - SSL/TLS
   - Security/WAF/Bot
   - Cache Rules/Page Rules
   - Speed/Protocol
   - Argo/Cost
   - WordPress/WooCommerce exclusions

4. **Implementation Plan**
   - Safe quick wins
   - Changes requiring testing
   - Changes requiring paid plan
   - Rollback notes

5. **Verification Commands/Checks**
   - curl/dig/openssl/browser checks
   - What pass/fail looks like

## Core Rules

- Prioritize **safe, reversible changes** first.
- For WooCommerce, never recommend blanket “Cache Everything” without exclusions.
- For WordPress admin/login/cart/checkout/account/API endpoints, bypass cache unless user confirms advanced setup.
- Prefer Full (strict) SSL when origin cert is valid.
- Do not recommend Flexible SSL for production WordPress/WooCommerce.
- Security rules must avoid blocking real customers, payment callbacks, crawlers needed for SEO, and admin operations.
- Cost recommendations for Argo must compare expected benefit vs traffic geography, origin latency, cache hit ratio, and monthly bandwidth.

## Load References When Needed

Read `references/checklist.md` for the detailed audit checklist and recommended settings.
Read `references/wordpress-woocommerce.md` for WordPress/WooCommerce-specific cache and security caveats.
Read `references/argo-cost.md` for Argo/Tiered Cache/APO cost optimization logic.

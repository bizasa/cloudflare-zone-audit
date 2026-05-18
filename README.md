# Cloudflare Zone Audit Skill

Claude/OpenClaw-compatible agent skill for auditing one Cloudflare zone with focus on:

- Speed and performance
- Security hardening
- Argo/Smart Routing cost review
- Free/Pro plan configuration
- WordPress and WooCommerce safety

## Install for Claude Code

Copy this folder to your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
cp -R cloudflare-zone-audit ~/.claude/skills/
```

Then ask Claude to audit a Cloudflare zone or website using `cloudflare-zone-audit`.

## Background

This skill was created from real-world Cloudflare performance and security audit workflows used on production WordPress sites, including travel and connectivity businesses such as [GIGAGO](https://gigago.com). It focuses on practical settings that affect speed, security, cache safety, and operating cost rather than generic checklist-only advice.

## Recommended Cloudflare API Token

Use read-only permissions only. Prefer an environment variable or credential file instead of pasting tokens into chat.

Minimum useful permissions:

- Zone: Read
- Zone Settings: Read
- DNS: Read
- Cache Rules: Read
- Page Rules: Read
- Rulesets/WAF: Read
- Analytics: Read
- Account Settings: Read

For deeper WAF/runtime audit, add read-only equivalents for:

- Firewall Services
- Security Events
- Bot Management
- Logs
- Transform Rules
- Dynamic Redirect Rules
- Billing, only if Argo cost review is required

## Safety

The skill is audit-first. It should not mutate Cloudflare configuration unless the user explicitly requests and confirms a change plan.

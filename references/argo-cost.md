# Argo / Smart Routing / Cost Optimization

## What to Review

For Argo Smart Routing or similar paid traffic features, evaluate:
- Monthly bandwidth through Cloudflare
- Geographic distribution of users vs origin location
- Origin latency and congestion
- Cache hit ratio
- Dynamic vs static traffic share
- Business value of latency reduction
- Existing CDN/cache performance
- Whether APO/Tiered Cache/static caching could reduce origin trips cheaper

## When Argo Is Likely Worth It

Argo may be valuable when:
- Users are global and far from origin
- Site has high dynamic request share that cannot be cached
- Origin/network path has unstable latency
- Revenue depends on faster checkout or lead conversion
- Measured TTFB improves materially in target markets

## When Argo May Be Wasteful

Consider disabling or testing off when:
- Audience is mostly near origin
- Most traffic is cacheable static content with high cache hit ratio
- Cloudflare cache/APO already solves TTFB
- Monthly bandwidth is high but latency improvement is marginal
- Site is low-value traffic where speed gain does not justify fee

## Audit Method

1. Establish baseline:
   - TTFB by geography
   - Cache hit ratio
   - Bandwidth/month
   - Origin response time
   - Checkout/conversion sensitivity if WooCommerce

2. Compare options:
   - Better cache rules
   - APO for WordPress
   - Tiered Cache if available
   - Image optimization
   - Origin region/CDN placement
   - Argo Smart Routing

3. Recommend:
   - Keep Argo
   - Disable Argo
   - Run A/B or timed before/after test
   - Replace with lower-cost cache/APO/origin optimization

## Reporting

Include:
- Current Argo status
- Evidence available or missing
- Estimated benefit category: High / Medium / Low / Unknown
- Cost risk: High / Medium / Low
- Decision: Keep / Disable / Test / Need analytics

Never claim savings without traffic/billing evidence. If billing data is unavailable, state assumptions clearly.

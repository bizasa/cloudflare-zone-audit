# Cloudflare Zone Audit Checklist

## 1. DNS and Proxy Posture

Check:
- Zone active and nameservers correct
- Apex/root and `www` records exist and resolve correctly
- Web traffic records are proxied where Cloudflare protection/CDN is desired
- Mail records are DNS-only, never proxied
- No stale A/AAAA records exposing origin unnecessarily
- No broad wildcard records unless intentionally needed
- DNSSEC enabled where registrar supports DS record
- CAA records allow intended certificate authorities

Recommendations:
- Proxy only HTTP/HTTPS web services through orange-cloud.
- Keep MX, SPF, DKIM, DMARC, mail/autodiscover/FTP/SSH DNS-only.
- Lock origin firewall to Cloudflare IP ranges when possible.

## 2. SSL/TLS

Check:
- SSL mode
- Edge certificate active
- Always Use HTTPS
- Automatic HTTPS Rewrites
- Minimum TLS version
- TLS 1.3
- HSTS
- Opportunistic Encryption
- Authenticated Origin Pulls / Origin cert if available

Recommended baseline:
- Production: Full (strict)
- Minimum TLS: 1.2
- TLS 1.3: on
- Always Use HTTPS: on
- Automatic HTTPS Rewrites: on unless mixed content testing fails
- HSTS: enable only after confirming HTTPS works across all subdomains; start conservative before preload

Avoid:
- Flexible SSL on WordPress/WooCommerce. It commonly causes redirect loops and insecure origin traffic.

## 3. Security/WAF/Bot Protection

Free plan baseline:
- Security Level: Medium initially; raise only during attack
- Browser Integrity Check: on unless false positives
- WAF Managed Rules: enable available free managed rules/rulesets
- Create focused custom rules for `/wp-login.php`, `/xmlrpc.php`, suspicious query patterns, and abusive countries only if business permits
- Rate limit login/XML-RPC if feature available in plan/account
- Block or challenge known bad bots via custom rules where possible

Pro plan baseline:
- Enable Cloudflare Managed Ruleset and OWASP rules with monitored rollout
- Use Super Bot Fight Mode/Bot features if available and safe for site
- More granular WAF custom rules and rate limiting
- Consider image optimization features if plan includes them and origin assets justify it

WordPress common WAF rules:
- Managed challenge `/wp-login.php` for non-admin countries or non-allowlisted ASNs/IPs
- Block or challenge `/xmlrpc.php` unless Jetpack/mobile app/pingbacks require it
- Challenge suspicious POSTs to `/wp-admin/admin-ajax.php` carefully; WooCommerce and plugins use it
- Never block `/wp-json/` broadly; many plugins, headless setups, and WooCommerce integrations use REST API

## 4. Cache Rules / Page Rules

Core goals:
- Maximize static asset caching
- Avoid caching personalized/dynamic pages
- Prevent WooCommerce cart/session leakage

Recommended cache posture:
- Static assets: cache aggressively, long edge/browser TTL if filenames are versioned
- HTML: default Cloudflare cache usually bypasses dynamic HTML unless APO/cache-everything rules are used
- WordPress APO: good for content sites; test with logged-in/admin/preview/e-commerce flows

Bypass cache for:
- `/wp-admin/*`
- `/wp-login.php*`
- `/cart/*`, `/checkout/*`, `/my-account/*`
- `*add-to-cart=*`
- WooCommerce endpoints and payment callbacks
- URLs with session/cart/auth cookies
- Preview/customizer URLs
- REST endpoints if dynamic/authenticated

Cache static:
- `*.css`, `*.js`, `*.jpg`, `*.jpeg`, `*.png`, `*.gif`, `*.webp`, `*.avif`, `*.svg`, `*.ico`, `*.woff`, `*.woff2`, `*.ttf`, `*.eot`, `*.pdf`

## 5. Speed/Performance

Check:
- Brotli
- HTTP/2
- HTTP/3/QUIC
- 0-RTT
- Early Hints
- Auto Minify
- Rocket Loader
- Mirage/Polish/Image Resizing if plan supports
- Cache hit ratio
- TTFB by geography
- origin response time
- redirect chain length
- compression headers

Recommended baseline:
- Brotli: on
- HTTP/2: on
- HTTP/3: on
- Early Hints: test, usually on
- 0-RTT: only if app is safe for replay risk; avoid for sensitive POST-heavy flows
- Auto Minify: only if not already handled by WP optimization plugin; avoid double-minification
- Rocket Loader: test carefully; often breaks JS-heavy WordPress plugins, WooCommerce checkout, tracking scripts
- Polish/WebP/AVIF: useful for media-heavy sites on Pro+; check interaction with image plugins/CDN

## 6. Redirects and Rules

Check:
- www/non-www canonical redirect
- HTTP→HTTPS redirect
- Page Rules vs Redirect Rules overlap
- Origin-level redirects causing loops
- Trailing slash/canonical rules

Recommendations:
- Keep canonical redirects simple and single-hop.
- Avoid duplicate redirects at origin, WordPress plugin, and Cloudflare simultaneously.
- Verify with `curl -IL` that final URL resolves in <=1-2 redirects.

## 7. Origin Exposure

Check:
- Origin IP visible in DNS history or direct records
- Server accepts direct requests bypassing Cloudflare
- Firewall allows all traffic to 80/443
- Admin paths exposed publicly

Recommendations:
- Restrict origin firewall to Cloudflare IP ranges where possible.
- Use authenticated origin pulls if operationally feasible.
- Remove direct origin DNS records from public zone.

## 8. Reporting Severity

Critical:
- Flexible SSL on production
- Cached WooCommerce cart/checkout/account pages
- Origin bypass allows direct attack
- Public admin/login with active brute-force and no mitigation
- Broken HTTPS/cert validation

High:
- No WAF/managed rules where available
- No DNSSEC/CAA for high-value domains
- Weak TLS/minimum TLS below 1.2
- Excessive redirect chains
- Cache everything without bypass rules

Medium:
- Brotli/HTTP3 off
- Static assets not cached well
- HSTS missing after stable HTTPS
- Bot settings disabled
- Argo enabled with low benefit/high cost uncertainty

Low:
- Minor header improvements
- Cosmetic performance settings
- Documentation/monitoring gaps

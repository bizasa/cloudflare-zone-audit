# Analysis Guide — Cloudflare WP Audit

Sau khi pull data, phân tích theo 5 category. Mỗi category có checklist items,
mỗi item có điểm trọng số, verdict, và recommended action.

---

## Category 1: Performance (trọng số 35%)

### SSL/TLS (10 điểm)
- `ssl == "flexible"` → **CRITICAL** (-10đ): Bảo mật thấp, gây redirect loop trên WP
  → Recommend: Đổi sang Full hoặc Full (Strict) sau khi verify origin có cert
- `ssl == "full"` → **WARNING** (-3đ): OK nhưng không verify cert hợp lệ
  → Recommend: Nên upgrade Full (Strict) với Cloudflare Origin CA cert
- `ssl == "strict"` → ✅ OK
- `always_use_https != "on"` → **WARNING** (-5đ)

### APO (15 điểm)
- Nếu plan là Free hoặc Pro: Check xem có APO không (tìm trong cache rules hoặc response headers)
- APO đang off → **WARNING** (-15đ): Biggest performance win cho WP
  → Recommend: Enable via Cloudflare WP Plugin (free với Pro, $5/mo với Free)
- APO đang on → ✅ (+15đ)
- Note: Nếu không xác định được APO status → Note "Cần check header `cf-edge-cache` trên site"

### HTTP Protocol (5 điểm)
- `http2 != "on"` → WARNING (-3đ)
- `http3 != "on"` → SUGGESTION (-2đ)

### Compression (5 điểm)
- `brotli != "on"` → WARNING (-3đ)

### Image Optimization (5 điểm, chỉ Pro+)
- Plan là Pro+ và `polish` == "off" → WARNING (-5đ)
  → Recommend: Polish Lossy + WebP
- `polish == "lossy"` và `webp == "on"` → ✅ (+5đ)

### Rocket Loader (5 điểm)
- `rocket_loader == "on"` → **CRITICAL** (-5đ): Breaks jQuery/WP themes
  → Recommend: Tắt ngay, luôn luôn

### Mirage (note only — deprecated)
- Nếu `mirage == "on"` → INFO: "Deprecated từ 09/2025, tự động disabled. Không cần làm gì"

### Tiered Cache (5 điểm)
- Không bật → WARNING (-5đ)
  → Recommend: Caching → Tiered Cache → Smart Topology (free, all plans)

---

## Category 2: Cache Strategy (trọng số 30%)

### Cache Hit Rate (10 điểm từ analytics)
- hit_rate < 60% → **CRITICAL** (-10đ): Rất thấp, cần audit cache rules gấp
- hit_rate 60-75% → WARNING (-7đ): Có thể tối ưu thêm
- hit_rate 75-85% → SUGGESTION (-3đ): Khá tốt, room for improvement
- hit_rate > 85% → ✅ (+10đ): Tốt

### Cache Rules Analysis (20 điểm)
Kiểm tra từng pattern quan trọng:

**WP Admin bypass (5đ):**
- Không có rule bypass `/wp-admin` → WARNING
  → Recommend: Cache Rule expression `starts_with(http.request.uri.path, "/wp-admin/")`
    → Bypass cache

**Login bypass (5đ):**
- Không có rule bypass `/wp-login.php` → WARNING

**Cookie-based bypass (5đ):**
- Không có rule kiểm tra cookie `wordpress_logged_in_` → **CRITICAL**
  → Recommend: Expression `http.cookie contains "wordpress_logged_in_"` → Bypass

**WooCommerce (5đ, nếu có WooCommerce):**
- Không có rule bypass `/cart`, `/checkout`, `/my-account` → **CRITICAL**
- Không check cookie `woocommerce_items_in_cart` → **CRITICAL**
- Có `wc-ajax` bypass → ✅

**Cache Rule "Cache all" không có Edge TTL:**
- Rule cache với `cache: true` nhưng không có `edge_ttl.value` → WARNING
  → Recommend: Thêm Edge TTL override 4h để tránh origin TTL ngắn

**Static assets long TTL:**
- Không có rule cache static assets (css/js/images) với TTL dài → SUGGESTION
  → Recommend: Cache Rule với extension filter + Edge TTL 1 month

### Page Rules (legacy)
- Có active page rules → INFO: "Nên migrate sang Cache Rules/Redirect Rules/Config Rules"
  (không deduct điểm, chỉ note)

---

## Category 3: Cost Optimization (trọng số 15%)

### Argo Assessment (từ analytics + settings)
Nếu `argo.smart_routing == "on"`:
- Tính cost: $5 + total_gb * $0.10/tháng (estimate từ 30-day data)
- Check traffic distribution:
  - Nếu >30% traffic từ same country/region như origin → WARNING: Argo ít hiệu quả cho portion này
  - Nếu analytics cho thấy bot traffic cao (CN + T1 > 15%) → WARNING: Đang pay Argo cho bots
- Recommend bypass bot/unwanted traffic trước khi optimize Argo

Nếu `argo.smart_routing == "off"`:
- Chỉ suggest nếu site có global traffic và cache hit rate tốt
- Không force recommend Argo

### Bot Traffic Estimate (từ analytics)
- Tìm CN + T1 (Tor) traffic từ country breakdown
- Nếu CN + T1 > 15% total bandwidth → WARNING: Significant bot traffic, suggest WAF challenge

### Cache Reserve
- `cache_reserve.value == "on"`:
  - Nếu site không có egress fees (typical WP host) → INFO: "Có thể không cần thiết, verify ROI"
- `cache_reserve.value == "off"`:
  - Chỉ suggest bật nếu origin có S3/GCS/Azure egress fees

---

## Category 4: Security (trọng số 15%)

### WAF Managed Rules (10đ, Pro+)
- Không có WAF managed rules active → WARNING (-5đ)
  → Recommend: Security → WAF → Managed rules → Cloudflare Managed Ruleset + enable WordPress tag

### Custom WAF Rules (10đ)
Nếu có quyền đọc WAF custom rules, check:
- Không có rule block `/xmlrpc.php` → **CRITICAL** (-5đ)
  → Expression: `http.request.uri.path eq "/xmlrpc.php"` → Block
- Không có Rate Limit trên `/wp-login.php` → WARNING (-3đ)
  → 5 req / 5 min POST → Block 10 min
- Không có WP cron/loopback whitelist → SUGGESTION (-2đ)

Nếu `waf_custom == "NO_PERMISSION"` → Note: "Không đọc được WAF rules — add WAF:Read permission để audit đầy đủ"

### Security Level (5đ)
- `security_level == "off"` → WARNING

### HTTPS Settings (5đ)
- `always_use_https != "on"` → CRITICAL
- `automatic_https_rewrites != "on"` → WARNING

---

## Category 5: Bot & AI Controls (trọng số 5%)

### Super Bot Fight Mode (SBFM, Pro+)
- Nếu Pro+: Suggest enable SBFM với:
  - Optimize for WordPress: ON (critical cho WP)
  - Definitely Automated: Managed Challenge
  - Verified Bots: Allow

### AI Controls
- Luôn recommend:
  - AI Labyrinth: ON (free, all plans)
  - AI Crawl Control → Block training bots (GPTBot, ClaudeBot, Bytespider, meta-externalagent)
  - Allow search bots (OAI-SearchBot, PerplexityBot, ChatGPT-User)
  - Managed robots.txt: ON

---

## Scoring Summary

```
Total score = weighted average của 5 categories:
  Performance:    score_1 / 45 * 100 * 0.35
  Cache:          score_2 / 30 * 100 * 0.30
  Cost:           score_3 / 20 * 100 * 0.15
  Security:       score_4 / 30 * 100 * 0.15
  Bot/AI:         score_5 / 10 * 100 * 0.05

Grade:
  90-100: A — Excellent
  75-89:  B — Good
  60-74:  C — Fair (có vấn đề cần fix)
  40-59:  D — Poor (cần cải thiện ngay)
  <40:    F — Critical issues
```

---

## WP/Woo Detection Heuristics

Khi không có thông tin trực tiếp về stack, infer từ:
- Cache rules có mention `wordpress_logged_in_` → WordPress detected
- Cache rules có mention `woocommerce` → WooCommerce detected
- Top paths có `/wp-content/`, `/wp-admin/` → WordPress confirmed
- Nếu không detect được → Apply WP recommendations anyway (safe default)

---

## Priority Matrix

```
Priority 1 (Critical, fix ngay):
  - SSL Flexible mode
  - Rocket Loader ON
  - Không có WordPress login cookie bypass
  - WooCommerce cart/checkout không bypass
  - XMLRPC không bị block
  - always_use_https OFF

Priority 2 (Important, fix trong 1 tuần):
  - APO chưa bật (Pro plan)
  - Cache hit rate < 75%
  - Edge TTL không set trong cache rules
  - Rate limit wp-login chưa có
  - WAF Managed rules chưa bật

Priority 3 (Suggestion, cân nhắc):
  - Page Rules → migrate sang modern rules
  - Static assets cache TTL chưa dài
  - Bot/AI controls chưa setup
  - Tiered Cache chưa bật
  - Polish/WebP chưa bật (Pro+)
```

---

## [v1.1] Module DNS Posture

**Khi nào chạy:** Luôn luôn. Path A: confirmed từ API. Path B: inferred từ dig.

### DNS Records Check

**Proxy status (10đ):**
- Web records (A/AAAA apex + www) không qua orange-cloud proxy → **CRITICAL** (-10đ)
  → Mất toàn bộ Cloudflare protection + CDN
- MX record bị proxied → **CRITICAL** (-5đ): Breaks email delivery
- Subdomain web (app, shop, blog) không proxied → **WARNING** (-3đ)

**Origin IP exposure (5đ):**
- A record cho mail/ftp/ssh/cpanel resolve ra IP trùng với web origin → **WARNING** (-5đ)
  → Attacker có thể bypass Cloudflare bằng cách hit origin IP trực tiếp
  → Recommend: Đổi origin server hoặc restrict firewall theo Cloudflare IP ranges

**DNSSEC (5đ):**
- Không có DS record ở registrar → **SUGGESTION** (-3đ)
  → Enable DNSSEC tại Cloudflare Dashboard → DNS → Settings → DNSSEC
  → Sau đó add DS record vào registrar

**CAA Records (3đ):**
- Không có CAA record → **SUGGESTION** (-3đ)
  → Recommend: `example.com CAA 0 issue "letsencrypt.org"` + `"digicert.com"` (cho CF cert)

**Email records (5đ):**
- Không có SPF TXT record → **WARNING** (-3đ)
- Không có DMARC record → **WARNING** (-2đ)
- Không có DKIM → **SUGGESTION** (-1đ)

---

## [v1.1] Module Origin Exposure

**Khi nào chạy:** Luôn luôn.

### Checks

**Direct IP access (10đ):**
- Path B: `curl -sI https://[origin_ip] -H "Host: domain.com"` trả về 200 → **CRITICAL** (-10đ)
  → Origin server chấp nhận request trực tiếp, bypass Cloudflare hoàn toàn
  → Fix: Restrict firewall/iptables chỉ nhận từ Cloudflare IP ranges
  → Cloudflare IPs: https://www.cloudflare.com/ips/

**Admin path exposure (5đ):**
- `/wp-admin/` accessible mà không có WAF rule → **WARNING** (-5đ): Brute-force target
- `/wp-login.php` accessible mà không có rate limit → **WARNING** (-3đ)
- `/xmlrpc.php` trả về 200 → **WARNING** (-5đ): Attack vector phổ biến

**Authenticated Origin Pulls (5đ, Pro+):**
- Nếu Pro+ và không bật → **SUGGESTION** (-2đ)
  → Đảm bảo origin chỉ nhận request có CF client cert

---

## [v1.1] Module Redirect Chain

**Khi nào chạy:** Luôn luôn. Path B inferred từ curl -IL.

### Checks

**Redirect count (10đ):**
- `http://domain.com` → final URL phải ≤ 2 hops → **CRITICAL** nếu > 3 hops (-10đ)
  → Mỗi hop thêm latency, bad for Core Web Vitals
  → Thường xảy ra khi redirect duplicate ở origin + WP plugin + Cloudflare cùng lúc

**www/non-www canonical (5đ):**
- Không có redirect hoặc redirect không nhất quán → **WARNING** (-5đ)
  → Pick một canonical (www hoặc non-www), redirect 301 về đó, set ở một chỗ duy nhất

**HTTP → HTTPS (5đ):**
- `http://` không redirect về `https://` → **CRITICAL** (-5đ)
  → Bật "Always Use HTTPS" tại CF Dashboard → SSL/TLS → Edge Certificates

**Redirect loop (10đ):**
- Curl báo "Too many redirects" → **CRITICAL** (-10đ)
  → Nguyên nhân phổ biến: Flexible SSL + WordPress force-ssl plugin
  → Fix: Đổi CF SSL mode sang Full hoặc Full (Strict)

**Duplicate redirect sources (5đ):**
- Có redirect ở cả 3 chỗ (origin .htaccess/nginx, WP plugin, CF Page Rules) → **WARNING** (-3đ)
  → Consolidate: để Cloudflare xử lý HTTP→HTTPS, để WP plugin xử lý www canonical
  → Không cần Page Rule nếu đã bật "Always Use HTTPS" tại CF

---

## [v1.1] Argo Decision Framework

**Khi nào chạy:** User đang bật Argo hoặc đang cân nhắc bật.

### Step 1 — Establish baseline (từ analytics)
- TTFB trung bình (cần RUM/real user data nếu có)
- Cache hit rate (từ CF analytics)
- Bandwidth/month (GB)
- Dynamic vs cacheable traffic ratio
- Top countries (% traffic từ đâu)
- Origin region

### Step 2 — Compare alternatives
Trước khi recommend Argo, check xem các option rẻ hơn đã làm chưa:
- Tiered Cache bật chưa? (free, giảm origin load)
- Cache hit rate đã > 85% chưa? (nếu chưa → fix cache trước, Argo không giúp)
- APO bật chưa? (cho WP content sites — thường hiệu quả hơn Argo)
- Origin đã ở region gần user chưa?

### Step 3 — Recommend (chọn 1 trong 4)
```
KEEP Argo: Cache hit rate đã cao, traffic phân tán global, origin xa user, conversion-sensitive
DISABLE Argo: Audience chủ yếu VN + origin VN, cache hit rate cao, static-heavy site
TEST: Chưa đủ data để kết luận → Suggest tắt 2 tuần và so sánh TTFB
NEED DATA: Không có analytics → Không thể recommend — cần pull analytics trước
```

**Cost estimate (nếu có data):**
`Argo cost ≈ $5 base + (total_bandwidth_gb × $0.10) / tháng`
Note rõ đây là estimate, billing thực tế xem tại CF Dashboard → Billing.

**Không bao giờ:** Claim savings cụ thể mà không có traffic/billing evidence.

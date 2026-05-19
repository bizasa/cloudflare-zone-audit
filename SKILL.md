---
name: cloudflare-wp-audit
version: 1.3.0
description: >
  Audit toàn diện cấu hình Cloudflare cho website WordPress / WooCommerce.
  Dùng skill này khi user muốn: kiểm tra Cloudflare của một website, audit
  Cloudflare settings, tối ưu performance/cost/security trên Cloudflare,
  review cache rules, WAF rules, bot settings, SSL, Argo, hoặc bất kỳ câu
  nào liên quan đến "check Cloudflare", "audit Cloudflare", "tối ưu
  Cloudflare", "review setting Cloudflare". Skill pull data thực tế từ API
  (hoặc black-box nếu không có token), phân tích theo audit profile phù hợp,
  và output ra action plan áp dụng ngay.
---

# Cloudflare WP Audit Skill — v1.1.0

Audit Cloudflare zone cho WordPress/WooCommerce theo 5 phase:
**Intake → Pull Data → Phân tích → Apply → Verify & Publish**

---

## QUY TAC BAT BUOC — DOC TRUOC KHI LAM GI

**Phase 0 (Intake) LUON LUON phai chay dau tien — khong co ngoai le.**

Du user cung cap domain, zone ID, hay token ngay tu dau — van phai hoi du 10 cau intake truoc khi lam bat cu dieu gi khac. Domain khong phai la thong tin du de bat dau audit.

SAI — nhay thang vao hoi token:
  "De audit <DOMAIN>, minh can API Token va Zone ID..."

DUNG — hoi intake day du:
  "De audit dung cach, minh can them mot chut context ve <DOMAIN> truoc nhe..."
  -> Hien thi 10 cau hoi intake

Ly do: Khong biet plan (Free/Pro), site type (WP/Woo), plugin cache, origin location
-> khong the quyet dinh audit modules nao phu hop -> ket qua audit sai hoac thua/thieu.

Thong tin da co tu user message -> bo qua cau hoi tuong ung, nhung VAN PHAI HOI nhung cau con lai.

---

## CHANGELOG

### v1.3.0 (2026-05)
**Workflow improvements:**
- Q7–Q10 intake: collect đủ READ + WRITE token ngay từ đầu, không hỏi giữa chừng
- CF Monitor worker token: chỉ hỏi ở Phase 5 (publish), không hỏi sớm
- Phase 1 reorder: pull analytics (30d GraphQL + TTFB + cache headers) TRƯỚC settings
- Analytics → định hướng priority order cho audit (cache/performance/security/bot)
- Token security note: rõ ràng collect-all-upfront policy

### v1.2.0 (2026-05)
**Từ learnings task <DOMAIN> audit:**
- Phase 1: thêm `Zone|Bots|Read` vào read token, quick-verify step, fix tên permissions (WAF không phải Firewall Services)
- Phase 1: note Auto Minify deprecated (silent no-op), WebP = Pro+ only
- Phase 2: thêm analytics anomaly detection (traffic spike, ipClassMap, country anomaly)
- Phase 4: write token verify step trước khi apply, Rate Limiting Free plan constraints (period=10s, timeout=10s, ip.src only)
- Phase 4: Ruleset GET→merge→PUT pattern bắt buộc
- CF Monitor: dual-account setup, D1 insert là bước chính, worker token scope

### v1.1.0 (2025-05)
**Thêm mới:**
- Phase 0 — Intake & Profiling: thu thập context trước khi audit, map ra audit_profile
- 10 câu hỏi intake có logic phân nhánh rõ ràng
- Path B — Black-box audit khi không có API token (curl/dig/openssl)
- Audit module DNS Posture & Origin Exposure (mới hoàn toàn)
- Audit module Redirect Chain (mới hoàn toàn)
- Argo cost decision framework với 3 bước (baseline → compare → recommend)
- Verification commands trong output (curl/dig/openssl để user tự verify)
- WooCommerce post-change testing checklist
- Token security: recommend CF_API_TOKEN env var thay vì paste vào chat

**Cải thiện:**
- Câu hỏi về caching plugin mở rộng (WP Rocket, LiteSpeed, W3TC, FlyingPress...)
- Upfront context gathering về site type, paid add-ons, origin location
- Conditional audit: chỉ chạy modules liên quan đến profile
- Phase 2 scoring có điều kiện theo plan (Free/Pro)
- Output format bổ sung Verification Commands & WooCommerce Test Checklist

### v1.0.0 (ban đầu)
- 3-phase workflow: Pull Data → Phân tích → Output
- 5 audit categories: Performance, Cache, Cost, Security, Bot/AI
- Scoring 0-100 per category + Overall Score + Grade
- GraphQL 30-day analytics
- WP/Woo heuristics, Priority Matrix

---

## Phase 0 — Intake & Profiling

**Mục đích:** Thu thập đủ context để quyết định audit path và modules nào cần chạy.
Hỏi tuần tự, gom thành 1 block message nếu có thể. Không hỏi lại thông tin đã được cung cấp.

### Câu hỏi intake (10 câu)

```
Q1. Bạn đang dùng Cloudflare plan nào?
    [ ] Free  [ ] Pro  [ ] Business  [ ] Enterprise  [ ] Không rõ

Q2. Bạn có bật thêm dịch vụ trả phí nào không? (chọn tất cả đang dùng)
    [ ] Argo Smart Routing
    [ ] Tiered Cache (Smart Topology) — Free plan cũng dùng được
    [ ] Cache Reserve              — Free plan cũng dùng được
    [ ] Cloudflare APO (tự động cho Pro, $5/tháng cho Free)
    [ ] Workers / Pages
    [ ] Không có gì thêm

Q3. Website của bạn dùng gì?
    [ ] WordPress (blog/service, không bán hàng)
    [ ] WordPress + WooCommerce (có cart/checkout)
    [ ] Không dùng WordPress
    [ ] Không rõ

Q4. Bạn có cài WP Rocket không?
    [ ] Có — đang bật
    [ ] Có — đã cài nhưng tắt
    [ ] Không

Q5. Bạn có cài plugin cache/optimization nào khác không?
    [ ] LiteSpeed Cache
    [ ] W3 Total Cache (W3TC)
    [ ] FlyingPress
    [ ] WP Super Cache
    [ ] Cloudflare plugin chính thức (free)
    [ ] Không có gì

Q6. Origin server (hosting) đặt ở đâu?
    [ ] Việt Nam (Vietnix, Mắt Bão, BKNS, PA Vietnam...)
    [ ] Singapore / Đông Nam Á (DO, Vultr, Linode, AWS SG...)
    [ ] US / EU
    [ ] Không rõ

Q7. Website có chạy quảng cáo tracking không?
    [ ] Có — Facebook Pixel / Google Tag / TikTok Pixel
    [ ] Không
    [ ] Không rõ

Q8. Website đã từng bị tấn công / DDoS / brute-force chưa?
    [ ] Có — gần đây (< 6 tháng)
    [ ] Có — lâu rồi
    [ ] Chưa bao giờ / Không rõ

Q9. Domain và Zone ID:
    - Domain: _______________
    - Zone ID: _______________ (Dashboard → chọn domain → sidebar phải)

Q10. Tokens — cung cấp đủ 2 token ngay từ đầu để audit không bị gián đoạn:

    READ TOKEN (bắt buộc — tạo tại dash.cloudflare.com/profile/api-tokens → Custom Token):
      Permissions:
        Zone → Zone Settings → Read
        Zone → Analytics    → Read   ← quan trọng, thường bị bỏ quên
        Zone → Cache Rules  → Read
        Zone → Page Rules   → Read
        Zone → WAF          → Read
        Zone → Bots         → Read
        DNS  → DNS          → Read
      Zone Resources: Include → Specific zone → [domain]
      TTL: 7 ngày
    → Read Token: _______________

    WRITE TOKEN (bắt buộc nếu muốn auto-apply — tạo Custom Token riêng):
      Permissions:
        Zone → Zone Settings    → Edit
        Zone → WAF              → Edit
        Zone → Cache Rules      → Edit
        Zone → Transform Rules  → Edit
        Zone → Firewall Services → Edit   ← cho Rate Limiting
      Zone Resources: Include → Specific zone → [domain]
      TTL: 1 ngày (revoke ngay sau khi apply xong)
    → Write Token: _______________ (hoặc để trống nếu muốn làm thủ công)

    Lưu ý: Revoke cả 2 token ngay sau khi audit + apply xong.
    CF Monitor worker token sẽ được hỏi ở bước cuối (Phase 5) nếu cần publish.
```

**Token security note:**
- Ưu tiên dùng env var `CF_API_TOKEN` thay vì paste thẳng vào chat
- Nếu user paste token vào chat → nhắc revoke ngay sau khi xong
- Collect đủ READ + WRITE token ở Q10 — KHÔNG hỏi thêm token giữa chừng trong audit
- CF Monitor worker token → chỉ hỏi ở Phase 5 (publish step), không hỏi sớm hơn

---

### Audit Profile Mapping

Từ answers Q1–Q9, xác định **audit_profile** để quyết định modules nào cần chạy:

```
PLAN_TIER:
  Free  → skip Pro+ features (APO check, Polish, SBFM detail), không trừ điểm
  Pro+  → full audit tất cả features

SITE_TYPE:
  WP-only   → skip WooCommerce cart/checkout bypass checks
  WP+Woo    → thêm WooCommerce Hard Rules audit (critical priority)
  Non-WP    → skip tất cả WP-specific checks

CACHE_PLUGIN:
  WP Rocket bật    → flag conflict risk với CF Auto Minify, CF Rocket Loader
  LiteSpeed bật    → flag conflict risk với CF Polish / image optimization
  Không có gì      → recommend CF native caching aggressive hơn

ORIGIN_LOCATION:
  VN origin + VN audience  → Argo likely NOT worth it → flag cost warning ngay
  Non-VN origin / global   → Argo feasibility cần analytics để confirm

AUDIT_MODE:
  Token available  → Path A (API-backed, data confirmed)
  No token         → Path B (black-box, label "inferred")

SECURITY_PRIORITY:
  Bị tấn công gần đây  → đẩy Security lên Priority 1, trước Performance
  Bình thường           → giữ thứ tự mặc định (Performance → Cache → Security)

TRACKING_RISK:
  Có Pixel/Tag (Q7) → cần cẩn thận Bot Fight Mode + Rocket Loader
  Không có          → không cần flag tracking risk

WRITE_TOKEN:
  Có sẵn (Q10)  → chuẩn bị apply list sau Phase 3
  Không có      → output checklist thủ công, user tự làm trên dashboard
```

**Ví dụ profile:**
```
Free + WP-only + WP Rocket bật + VN origin + No token
→ Modules: SSL, DNS, Origin Exposure, Redirect, Cache cơ bản, Speed, Security cơ bản
→ Skip: Argo ROI, APO, Polish, WooCommerce bypass, WAF Managed
→ Mode: Path B black-box
→ Flag: WP Rocket + CF Rocket Loader conflict risk

Pro + WP+Woo + WP Rocket + SG origin + Token có sẵn
→ Modules: Full audit tất cả 8 modules
→ Extra focus: Cart/checkout bypass, WP Rocket conflict, Argo ROI vs SG-to-VN latency
→ Mode: Path A API-backed
```

---

## Phase 1 — Pull Data

### Path A — API-backed (khi có token)

**Token permissions tối thiểu cần tạo (tên chính xác trong CF Dashboard 2026):**
```
Zone → Zone Settings → Read
Zone → Analytics → Read       ← BẮT BUỘC cho GraphQL, thường bị bỏ quên
Zone → Cache Rules → Read
Zone → Page Rules → Read
Zone → WAF → Read             ← optional, bỏ qua nếu 403 (tên cũ "Firewall Services" đã đổi thành "WAF")
Zone → Bots → Read            ← để đọc Bot Fight Mode (nếu thiếu → null, không phải off)
DNS → DNS → Read              ← cho DNS audit module
Account Settings → Read       ← nếu cần review Argo/billing
```
→ Zone Resources: Include → Specific zone → [domain cụ thể]
→ TTL: 7 ngày (bảo mật)

**⚠️ Nếu setting trả về `null` thay vì on/off → token thiếu quyền, KHÔNG phải setting đang off**

**Quick verify sau khi nhận token — chạy trước khi pull data:**
```bash
# Test Analytics access (thường bị thiếu nhất)
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"query":"{ viewer { zones(filter:{zoneTag:\"ZONE_ID\"}) { httpRequests1dGroups(limit:1, filter:{date_geq:\"2026-01-01\",date_leq:\"2026-01-01\"}) { sum { requests } } } } }"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ Analytics OK' if not d.get('errors') else '❌ FAIL — thêm Zone|Analytics|Read')"

# Test Bot Fight Mode access
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings/bot_fight_mode" | python3 -c "
import sys,json; d=json.load(sys.stdin)
r=d.get('result')
if r is None: print('⚠️ Bot Fight Mode: null — thiếu Zone|Bots|Read, hỏi user trực tiếp')
elif d.get('success'): print('✅ Bot Fight Mode:', r.get('value'))
"
```

Chạy `references/pull_data.py TOKEN ZONE_ID`, lưu output vào `cf_audit_data.json`.

**Data cần pull — theo thứ tự (analytics TRƯỚC để định hướng audit):**

**BƯỚC 1 — Analytics trước (định hướng toàn bộ audit):**
```
A1. 30-day traffic analytics (GraphQL):
    - Total requests, cached requests, hit rate (bytes + requests)
    - Total bandwidth, cached bandwidth
    - Threats blocked
    - Per-day breakdown → detect traffic spike (max/median > 5x = bot attack)
    - ipClassMap: noRecord, badHost, tor → noRecord > 80% = bot traffic
    - Country breakdown → countries không liên quan business = suspicious
    - pageViews → estimate human traffic thực

A2. HTTP external checks (black-box):
    - TTFB (5 lần đo) → baseline origin speed
    - Cache status trên homepage, static assets, wp-content
    - Security headers hiện có
    - Redirect chain
```
→ Từ analytics data: xác định **priority order** cho audit:
  - Cache hit rate < 10% → Cache là P1
  - TTFB > 1s uncached → Performance/Origin là P1
  - Threats > 10K/30d hoặc spike → Security là P1
  - Bot traffic chiếm > 50% → WAF/Bot là P1

**BƯỚC 2 — Settings pull (dựa trên priority từ analytics):**
```
1.  Zone info + plan
2.  Zone settings (brotli, polish, webp, ssl, http2, http3,
    rocket_loader, browser_cache_ttl, early_hints, security_level,
    always_use_https, automatic_https_rewrites, tls_1_3, min_tls_version,
    zero_rtt, email_obfuscation, hotlink_protection, opportunistic_encryption)
    NOTE: minify → CF Auto Minify deprecated (silent no-op — skip)
    NOTE: webp → editable:false trên Free plan (Polish lossy OK, WebP cần Pro+)
3.  Cache Rules
4.  Configuration Rules
5.  WAF Custom Rules         ← bỏ qua nếu 403, ghi NO_PERMISSION
6.  WAF Managed Rules
7.  Rate Limiting Rules
8.  Page Rules (legacy)
9.  Argo Smart Routing       ← chỉ nếu profile cần Argo audit
10. Tiered Cache settings
11. Cache Reserve settings
12. DNS records ← A, AAAA, MX, TXT, CNAME, CAA, DS
```

---

### Path B — Black-box audit (khi không có token)

Dùng bash_tool. **Label tất cả findings là `[inferred]`.**

```bash
DOMAIN="example.com"

# CF detection & cache status
curl -sI "https://$DOMAIN" | grep -i "cf-ray\|cf-cache-status\|cf-edge-cache\|server\|strict-transport"

# Cache behavior — static asset
curl -sI "https://$DOMAIN/wp-content/themes/style.css" | grep -i "cf-cache-status\|cache-control\|age"

# Redirect chain — HTTP → HTTPS → www canonical
curl -sIL "http://$DOMAIN" | grep -i "location\|http/"
curl -sIL "http://www.$DOMAIN" | grep -i "location\|http/"

# Security headers
curl -sI "https://$DOMAIN" | grep -i "x-frame-options\|x-content-type\|referrer-policy\|content-security-policy"

# DNS records
dig +short "$DOMAIN" A
dig +short "www.$DOMAIN" A
dig +short "$DOMAIN" MX
dig +short "$DOMAIN" TXT | grep -i "spf\|v=spf"
dig +short "_dmarc.$DOMAIN" TXT
dig +short "$DOMAIN" DS   # DNSSEC check

# TLS version support
curl --tlsv1.0 --tls-max 1.0 -sI "https://$DOMAIN" -o /dev/null -w "TLS1.0: %{http_code}\n" 2>&1
curl --tlsv1.1 --tls-max 1.1 -sI "https://$DOMAIN" -o /dev/null -w "TLS1.1: %{http_code}\n" 2>&1
```

**Scope Path B:** SSL, redirect chain, cache headers, DNS posture, security headers.
**Không thể xác nhận:** WAF rules, Cache Rules chi tiết, Analytics, Argo settings.
→ Nếu site là WP+Woo: cảnh báo không thể confirm cart bypass — strongly recommend tạo token.

---

## Phase 2 — Phân tích

Phân tích theo **modules có điều kiện** dựa trên audit_profile.
Chi tiết scoring từng category → `references/analysis_guide.md`

### Modules & điều kiện chạy

| Module | Chạy khi | Path B? |
|---|---|---|
| SSL/TLS | Luôn luôn | ✅ inferred |
| DNS Posture [v1.1] | Luôn luôn | ✅ inferred |
| Origin Exposure [v1.1] | Luôn luôn | ✅ partial |
| Redirect Chain [v1.1] | Luôn luôn | ✅ inferred |
| Cache Rules — WP | site_type = WP-any | ❌ cần token |
| Cache Rules — WooCommerce | site_type = WP+Woo | ❌ cần token |
| Cache Plugin Conflict | cache_plugin != none | ✅ inferred |
| Speed Settings | Luôn luôn | ✅ partial |
| APO | Pro+ hoặc user đang dùng | ✅ inferred từ header |
| Polish/Image | plan = Pro+ | ❌ cần token |
| WAF Custom | token có WAF:Read | ❌ cần token |
| WAF Managed | plan = Pro+ | ❌ cần token |
| Rate Limiting | Luôn luôn | ❌ cần token |
| Argo ROI | user đang bật Argo | ❌ cần token+analytics |
| Argo Feasibility | user muốn xem xét | ✅ từ origin location |
| Tiered Cache | Luôn luôn | ❌ cần token |
| Cache Reserve | user bật hoặc muốn xem | ❌ cần token |
| Bot/AI Controls | Luôn luôn | ✅ partial |
| SBFM | plan = Pro+ | ❌ cần token |
| Tracking pixel risk | has_tracking = true | ✅ from intake |

**Analytics anomaly detection (tự động trong Phase 2):**
Sau khi pull 30-day data, so sánh:
- Max daily requests vs median daily requests → nếu max/median > 5x: flag "⚠️ Traffic spike — possible bot attack"
- `ipClassMap.noRecord` > 80% tổng requests → flag bot traffic
- Top countries không liên quan đến business context → flag suspicious
- Cache hit rate < 5% dù có Cache Rules → điều tra Set-Cookie hoặc bot làm sụt hit rate

**Scoring có điều kiện:**
- Free plan: không trừ điểm vì thiếu APO, Polish, SBFM — mark `[N/A — cần Pro]`
- Path B: không score modules cần token — note `[Cần token để confirm]`
- recent_attack = true: tăng trọng số Security từ 15% → 30%, giảm Performance từ 35% → 20%

---

## Phase 4 — Apply Config (Step-by-step với confirm)

Sau khi có checklist từ Phase 3, thực hiện apply từng item với sự confirm của user.

### 4.1 — Xin Write Token

Sau khi audit xong, nếu user muốn apply các fixes ngay:

```
Để tự động apply các config thay đổi, tôi cần một API token với quyền ghi.
Token này KHÁC với token audit (read-only).

Permissions cần thiết (tùy theo checklist):
  Zone Settings: Edit    ← cho ssl, brotli, http2, security_level...
  Cache Rules: Edit      ← thêm/sửa Cache Rules
  Firewall Services: Edit ← WAF custom rules, rate limiting
  Zone: Edit             ← nếu cần sửa settings khác

Tạo tại: dash.cloudflare.com/profile/api-tokens
  → Custom Token → chọn zone cụ thể → TTL 1 ngày (xóa ngay sau khi dùng)

Token sẽ được dùng để apply, sau đó bạn nên revoke ngay.
Cung cấp write token khi sẵn sàng.

**Verify write token ngay sau khi nhận (trước khi apply bất cứ thứ gì):**
```bash
# Test PATCH đơn giản — nếu fail → dừng, yêu cầu user sửa permissions
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings/security_level" \
  -H "Authorization: Bearer $WRITE_TOKEN" -H "Content-Type: application/json" \
  -d '{"value":"medium"}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
if d.get('success'): print('✅ Write token OK — Zone Settings:Edit working')
else: print('❌ FAIL:', d.get('errors'), '\n→ Check: Zone Settings:Edit, WAF:Edit, Cache Rules:Edit, Transform Rules:Edit')
"
```
**Permissions cần thiết (tên chính xác CF Dashboard 2026):**
```
Zone → Zone Settings → Edit
Zone → WAF → Edit              ← KHÔNG phải "Firewall Services" (tên cũ)
Zone → Cache Rules → Edit
Zone → Transform Rules → Edit
Zone → Firewall Services → Edit ← cho Rate Limiting (nếu cần)
```
```

**Nếu user không muốn cấp write token:** Output checklist dạng step-by-step manual để user tự làm trên dashboard.

### 4.2 — Build checklist.json

Từ kết quả Phase 2 (analysis), build `checklist.json` theo format:
```json
[
  {
    "id": "ssl_mode",
    "title": "Đổi SSL mode sang Full (Strict)",
    "category": "SSL/TLS",
    "severity": "critical",
    "action": "zone_setting",
    "setting": "ssl",
    "value": "strict",
    "verify_url": "/zones/{zone_id}/settings/ssl",
    "verify_key": "value",
    "verify_expect": "strict",
    "dashboard_path": "SSL/TLS → Overview → Encryption mode",
    "rollback": {"setting": "ssl", "value": "full"}
  }
]
```

**Rate Limiting — Free plan constraints (2026):**
```
characteristics: ["cf.colo.id", "ip.src"]   ← cf.unique_visitor_id cần Advanced Rate Limiting (Pro+)
period: 10                                   ← chỉ 10s, không phải 60s
mitigation_timeout: 10                       ← chỉ 10s, không phải 600s
```
Muốn period 60s+ hoặc visitor-based tracking → cần CF Pro + Advanced Rate Limiting add-on

**⚠️ Ruleset PUT thay thế toàn bộ — pattern bắt buộc: GET → merge → PUT**
Trước khi PUT bất kỳ ruleset nào (Cache Rules, Transform Rules, WAF Custom, Rate Limiting):
1. GET ruleset hiện tại để lấy existing rules + existing IDs
2. Merge rules mới vào array (giữ nguyên `id` của rules cũ)
3. PUT toàn bộ array — không PUT chỉ rule mới (sẽ xóa hết rules cũ)

**Action types hỗ trợ:**
- `zone_setting` — PATCH zone setting đơn giản (ssl, brotli, http2, security_level...)
- `zone_setting_obj` — PATCH setting dạng object (minify)
- `ruleset_entrypoint_rule_add` — Thêm Cache Rule / WAF Rule vào phase entrypoint
- `ruleset_rule_del` — Xóa rule theo rule_id
- `page_rule_del` — Xóa Page Rule legacy
- `cache_purge_all` — Purge toàn bộ cache
- `tiered_cache_enable` — Bật Tiered Cache Smart Topology
- `always_use_https` — Bật Always Use HTTPS

**Thứ tự apply:** Critical trước → Warning → Suggestion. SSL mode luôn đầu tiên.

### 4.3 — Chạy apply_config.py (interactive)

```bash
python3 references/apply_config.py WRITE_TOKEN ZONE_ID checklist.json
```

**UX từng bước:**
```
────────────────────────────────────────────────────────────
[1/8] 🔴 Đổi SSL mode sang Full (Strict)
  Category   : SSL/TLS
  Severity   : critical
  Dashboard  : SSL/TLS → Overview → Encryption mode
  API action : PATCH settings/ssl → "strict"

  [1] Run    [2] Skip    [3] Show detail
  → _
```

- **1 = Run** → apply ngay, verify tự động, in kết quả
- **2 = Skip** → bỏ qua, ghi vào log với status "skipped"
- **3 = Show detail** → in full JSON của item, rồi hỏi lại 1/2

Sau khi apply xong tất cả → in summary và lưu `apply_results.json`.

**Nguyên tắc safety:**
- Nếu một item fail → hỏi user có muốn tiếp tục không
- Critical items (ssl, always_use_https) apply trước nhất
- Mỗi item có `rollback` field — nếu verify fail thì suggest rollback command
- Không batch apply — từng item một, chờ confirm

---

## Phase 5 — Final Verify & Publish

### 5.1 — Verify toàn bộ

Sau khi apply xong, chạy verify lần cuối bao gồm cả API check và external HTTP check:

```bash
python3 references/verify_all.py READ_TOKEN ZONE_ID apply_results.json checklist.json
```

Output:
```
📡 API Verifications
  ✅ SSL mode Full (Strict)          → strict == strict
  ✅ Always Use HTTPS               → on == on
  ✅ Brotli enabled                 → on == on
  ❌ Cache Rule wp-login bypass     → rule not found != expected

🌐 External Checks — domain.com
  ✅ HTTPS redirect (http → https)  → Location: https://...
  ✅ Redirect chain (≤2 hops)       → 2
  ✅ CF-Ray header (CF proxying)    → cf-ray: abc123
  ⚠️  Static asset cache (HIT)      → cf-cache-status: MISS (chưa warm)
  ✅ TLS 1.0 blocked                → 000 (connection refused)
  ✅ xmlrpc.php blocked             → HTTP/2 403

VERIFY SUMMARY
  ✅ Passed: 9
  ❌ Failed: 1  → Cache Rule wp-login bypass
```

Kết quả lưu vào `verify_report.json`.

### 5.2 — Publish lên cf-monitor

Sau khi verify xong (kể cả có item failed — vẫn publish, ghi rõ status):

```bash
python3 references/publish_zone.py apply_results.json verify_report.json [baseline.json]
```

Script này tự động:
1. Fetch HTML hiện tại từ `cf-monitor.bizasa.com`
2. Kiểm tra zone_id đã có trong ZONES chưa
3. Nếu chưa → inject zone entry mới (với changelog)
4. Nếu có rồi → chỉ update changelog
5. Deploy lên Cloudflare Pages

**Changelog được ghi vào dashboard:**

| Ngày | Checklist Item | Category | Status | Verified |
|---|---|---|---|---|
| 2026-05-18 | 🔴 Đổi SSL sang Full (Strict) | SSL/TLS | ✅ Applied | ✅ Verified |
| 2026-05-18 | 🟡 Bật Always Use HTTPS | SSL/TLS | ✅ Applied | ✅ Verified |
| 2026-05-18 | 🔴 Block xmlrpc.php | Security | ✅ Applied | ✅ Verified |
| 2026-05-18 | 🔵 Migrate Page Rules | Cache | ⏭️ Skipped | — |

---

## CF Monitor Integration

**Sau khi audit xong zone mới**, thêm zone vào dashboard CF Monitor tại `https://cf-monitor.bizasa.com`.

### Kiến trúc hệ thống (quan trọng — đọc trước)

CF Monitor gồm 2 thành phần **tách biệt trên 2 Cloudflare account khác nhau**:

| Thành phần | Account | Project/Worker | Token cần |
|-----------|---------|----------------|-----------|
| **Frontend HTML** | `<CF_MONITOR_ACCOUNT_EMAIL>` (ID: `<CF_ACCOUNT_ID_MONITOR>`) | Pages project: `cf-monitor` · domain: `cf-monitor.bizasa.com` | CF Pages token (account này) |
| **Backend Worker + D1 DB** | `<CF_MONITOR_ACCOUNT_EMAIL>` (ID: `<CF_ACCOUNT_ID_MONITOR>`) | Worker: `cf-monitor` · D1: `<CF_MONITOR_D1_ID>` | CF Worker token |

**KHÔNG nhầm** với account chính (`<CF_ACCOUNT_ID_MAIN>`) dùng cho `pages-bizasa` / `pages.bizasa.com` — đó là account khác.

Token để deploy:
- **CF Worker token** (deploy HTML + thao tác D1): cần xin từ user, đây là token account `<CF_MONITOR_ACCOUNT_EMAIL>`
- Worker này cần có secret `CF_API_TOKEN` với quyền `Zone | Analytics | Read` cho **tất cả zones được monitor** — nếu thêm zone mới ở account khác, cần update secret này.

---

### Quy trình thêm zone mới (3 bước bắt buộc)

**Bước 1 — Insert zone vào D1 Database**

Đây là bước quan trọng nhất — worker đọc danh sách zone từ D1, không phải từ HTML.

```bash
CF_WORKER_TOKEN="<token>"
CF_ACCOUNT_ID="<CF_ACCOUNT_ID_MONITOR>"
DB_ID="<CF_MONITOR_D1_ID>"
ZONE_ID="<zone_id_cần_thêm>"
DOMAIN="<domain.com>"

# Check zone đã có chưa
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$DB_ID/query" \
  -H "Authorization: Bearer $CF_WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT * FROM zones"}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
for r in d['result'][0].get('results',[]): print(r)
"

# Insert nếu chưa có
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$DB_ID/query" \
  -H "Authorization: Bearer $CF_WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sql\":\"INSERT OR IGNORE INTO zones (zone_id, zone_name, active) VALUES ('$ZONE_ID', '$DOMAIN', 1)\"}" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print('✅ Inserted' if d.get('success') else '❌', d.get('errors',''))
"
```

**Bước 2 — Update HTML dropdown và deploy lên Pages**

```bash
# Fetch HTML hiện tại từ đúng domain
curl -s "https://cf-monitor.bizasa.com/" -o /tmp/cfm.html

# Thêm option vào select dropdown
python3 << 'PYEOF'
with open('/tmp/cfm.html', 'r') as f:
    html = f.read()

# Tìm option cuối cùng trong select và thêm sau
import re
last_option = list(re.finditer(r'<option value="[^"]+">.*?</option>', html))[-1]
insert_pos = last_option.end()
new_option = f'\n      <option value="{ZONE_ID}">{DOMAIN}</option>'
html = html[:insert_pos] + new_option + html[insert_pos:]

with open('/home/claude/cfm-site/index.html', 'w') as f:
    f.write(html)
print("✅ HTML updated")
PYEOF

# Deploy lên CF Pages project cf-monitor (account vietnambiz)
CLOUDFLARE_API_TOKEN="$CF_WORKER_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="<CF_ACCOUNT_ID_MONITOR>" \
npx wrangler pages deploy /home/claude/cfm-site --project-name=cf-monitor
```

**Bước 3 — Trigger worker collect snapshot đầu tiên**

```bash
# Trigger manual run
curl -s "https://<CF_MONITOR_WORKER_URL>/run"
# Kết quả mong đợi: "Monitor ran successfully"

# Verify snapshot đã có data (không phải toàn 0)
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$DB_ID/query" \
  -H "Authorization: Bearer $CF_WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sql\":\"SELECT zone_id, snapshot_date, hit_rate_bytes, total_gb, total_requests FROM snapshots WHERE zone_id='$ZONE_ID' ORDER BY created_at DESC LIMIT 1\"}" | python3 -c "
import sys,json; d=json.load(sys.stdin)
for r in d['result'][0].get('results',[]): print(r)
"
```

⚠️ **Nếu snapshot toàn 0**: worker secret `CF_API_TOKEN` không có quyền đọc analytics zone này.
→ Cần update secret với token có `Zone | Analytics | Read` cho zone mới.
→ Nếu zone thuộc account khác với account chính của worker, phải dùng **global API token** hoặc token có multi-zone access.
→ Workaround: update snapshot thủ công bằng data từ audit (xem bên dưới).

```bash
# Workaround: update snapshot thủ công với data từ Phase 1 analytics
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$DB_ID/query" \
  -H "Authorization: Bearer $CF_WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sql\":\"UPDATE snapshots SET total_gb=TOTAL_GB, cached_gb=CACHED_GB, total_requests=TOTAL_REQ, cached_requests=CACHED_REQ, hit_rate_bytes=HIT_RATE_BYTES, hit_rate_req=HIT_RATE_REQ, avg_gb_per_day=AVG_GB_DAY, waf_block_total=THREATS WHERE zone_id='$ZONE_ID' AND snapshot_date='$(date +%Y-%m-%d)'\"}"
```

---

## Phase 3 — Output Action Plan

Format output chuẩn → `references/output_format.md`

**Output gồm (theo thứ tự):**
1. **Audit Profile Summary** — plan, site type, plugins, origin, mode (Path A/B)
2. **Overall Score** + category scores (N/A với modules không applicable)
3. **30-day Stats** (chỉ Path A)
4. **Issues** — Critical → Warning → Suggestion
5. **Action Plan** — nhóm theo Hôm nay / Tuần này / Cân nhắc
6. **Settings đang tốt** — không cần đổi
7. **Verification Commands** [v1.1] — curl/dig/openssl để confirm sau khi apply
8. **WooCommerce Test Checklist** [v1.1] — chỉ hiển thị nếu WP+Woo
9. **Lịch review** — 3 tháng + trigger conditions

---

## Nguyên tắc quan trọng

- **Chỉ recommend những gì làm được trên plan hiện tại** — mark `[cần Pro]` nếu cần upgrade
- **Ưu tiên ROI:** Performance & Cache trước; Security first nếu recent_attack = true
- **WordPress/WooCommerce first:** Luôn check WP-specific gotchas (loopback, cart bypass, Rocket Loader)
- **Không cache commerce flows:** Không bao giờ recommend "Cache Everything" cho Woo mà không có bypass rules
- **Data beats assumptions:** Dùng số thực từ analytics, không ước tính chung chung
- **Honest về limitations:** Path B → label `[inferred]`. Token thiếu quyền → note rõ, không đoán
- **Bảo mật token:** Nhắc revoke sau audit. Nếu token paste vào chat → nhắc revoke ngay
- **Argo honest:** Không claim savings mà không có traffic/billing data. VN origin + VN audience → flag không worth it thẳng
- **Safe & reversible first:** Ưu tiên thay đổi có thể rollback. Flag rõ những thay đổi không thể undo

---

## Edge Cases

| Case | Xử lý |
|---|---|
| Token 403 trên WAF | Bỏ qua WAF, note "Cần WAF:Read permission" |
| Free plan | Skip Pro+ features, mark N/A, không trừ điểm |
| Không có WooCommerce | Bỏ qua Woo-specific bypass rules |
| Zone không có Analytics | Handle gracefully, note "Analytics không available" |
| Nhiều subdomains | Pull hostname breakdown, identify subdomain cần attention |
| WP Rocket + CF Rocket Loader cùng bật | Flag CRITICAL conflict ngay |
| WP Rocket + CF Auto Minify cùng bật | Flag WARNING duplicate minification |
| Path B + WooCommerce | Cảnh báo không thể confirm cart bypass — recommend tạo token |
| Origin IP lộ qua DNS | Flag nếu A record không qua CF proxy (orange cloud) |
| Flexible SSL trên WP/Woo | Luôn là CRITICAL — gây redirect loop & insecure origin traffic |
| Token paste vào chat | Nhắc revoke ngay tại dash.cloudflare.com/profile/api-tokens |

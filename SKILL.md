---
name: cloudflare-wp-audit
version: 1.1.0
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
  "De audit hanoiparagliding.com, minh can API Token va Zone ID..."

DUNG — hoi intake day du:
  "De audit dung cach, minh can them mot chut context ve hanoiparagliding.com truoc nhe..."
  -> Hien thi 10 cau hoi intake

Ly do: Khong biet plan (Free/Pro), site type (WP/Woo), plugin cache, origin location
-> khong the quyet dinh audit modules nao phu hop -> ket qua audit sai hoac thua/thieu.

Thong tin da co tu user message -> bo qua cau hoi tuong ung, nhung VAN PHAI HOI nhung cau con lai.

---

## CHANGELOG

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

Q7. Bạn có API token Cloudflare không?
    [ ] Có — tôi sẽ cung cấp token + Zone ID
    [ ] Chưa có — hướng dẫn tôi tạo
    [ ] Không muốn dùng — chạy black-box check thay thế

Q8. Website có chạy quảng cáo tracking không?
    [ ] Có — Facebook Pixel / Google Tag / TikTok Pixel
    [ ] Không
    [ ] Không rõ

Q9. Website đã từng bị tấn công / DDoS / brute-force chưa?
    [ ] Có — gần đây (< 6 tháng)
    [ ] Có — lâu rồi
    [ ] Chưa bao giờ / Không rõ

Q10. Domain, Zone ID, và Token (nếu có):
    - Domain: _______________
    - Zone ID: _______________ (Dashboard → chọn domain → sidebar phải)
    - API Token: _______________ (hoặc path env var: CF_API_TOKEN)
    → Lưu ý: Dùng token read-only. Revoke sau khi audit xong tại
      dash.cloudflare.com/profile/api-tokens
```

**Token security note:** Ưu tiên dùng env var `CF_API_TOKEN` thay vì paste thẳng vào chat.
Nếu user paste token vào chat → nhắc revoke ngay sau khi audit hoàn tất.

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
  Có Pixel/Tag    → cần cẩn thận Bot Fight Mode + Rocket Loader
  Không có        → không cần flag tracking risk
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

**Token permissions tối thiểu cần tạo:**
```
Zone → Zone → Read
Zone → Analytics → Read
Zone → Settings → Read
Zone → Cache Rules → Read
Zone → Page Rules → Read
Zone → WAF → Read           ← optional, bỏ qua nếu 403
DNS → Read                  ← cho DNS audit module
Account Settings → Read     ← nếu cần review Argo/billing
```
→ Zone Resources: Include → Specific zone → [domain cụ thể]
→ TTL: 7 ngày (bảo mật)

Chạy `references/pull_data.py TOKEN ZONE_ID`, lưu output vào `cf_audit_data.json`.

**Data cần pull (có điều kiện):**
```
1.  Zone info + plan
2.  Zone settings (brotli, minify, polish, webp, ssl, http2, http3,
    rocket_loader, browser_cache_ttl, early_hints, security_level,
    always_use_https, automatic_https_rewrites, tls_1_3, min_tls_version,
    zero_rtt, email_obfuscation, hotlink_protection, opportunistic_encryption)
3.  Cache Rules
4.  Configuration Rules
5.  WAF Custom Rules         ← bỏ qua nếu 403, ghi NO_PERMISSION
6.  WAF Managed Rules
7.  Rate Limiting Rules
8.  Page Rules (legacy)
9.  Argo Smart Routing       ← chỉ nếu profile cần Argo audit
10. Tiered Cache settings
11. Cache Reserve settings
12. 30-day traffic analytics (GraphQL)
13. DNS records [MỚI v1.1]  ← A, AAAA, MX, TXT, CNAME, CAA, DS
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

**Sau khi audit xong zone mới**, kiểm tra và cập nhật dashboard CF Monitor tại `https://cf-monitor.bizasa.com`.

### Quy trình

**Bước 1 — Kiểm tra zone đã có trong dashboard chưa:**
Mở source HTML tại `pages.bizasa.com/cf-monitor.html` và tìm trong mảng `ZONES`:
```javascript
const ZONES = [ ... ]
```
Nếu domain đã có → không cần làm gì.

**Bước 2 — Nếu zone chưa tồn tại, thêm vào:**

Fetch HTML hiện tại, thêm entry vào mảng `ZONES`, deploy lại:

```python
# Fetch current HTML
import urllib.request
req = urllib.request.Request("https://cf-monitor.bizasa.com/")
with urllib.request.urlopen(req) as r:
    html = r.read().decode()

# Thêm zone mới vào mảng ZONES (tìm comment placeholder)
new_zone = """  {
    id: 'ZONE_ID_MOI',
    name: 'domain-moi.com',
    baseline: null   // set sau khi có đủ data
  },"""

html = html.replace(
    "  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────",
    f"  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────\n{new_zone}"
)
```

Sau đó deploy theo quy trình Cloudflare Pages chuẩn.

**Bước 3 — Set baseline sau khi có data:**

Sau 2–3 snapshots đầu tiên của zone mới, update `baseline` từ `null` sang object thực tế:
```javascript
baseline: {
  date: 'YYYY-MM-DD',           // ngày audit
  hit_rate_bytes: XX.X,          // từ CF analytics
  hit_rate_req: XX.X,
  total_gb_7d: XX.XX,
  argo_monthly_est: XX.XX,       // 0 nếu không dùng Argo
  cn_gb_7d: X.XX,
  tor_gb_7d: X.XX,
}
```

### Thực thi bằng bash_tool

Khi cần thêm zone mới vào cf-monitor, chạy script sau (điền ZONE_ID và DOMAIN_NAME):

```bash
# 1. Fetch HTML hiện tại
curl -s "https://cf-monitor.bizasa.com/" -o /home/claude/site/cf-monitor.html

# 2. Thêm zone vào ZONES array (dùng sed hoặc python)
python3 << 'PYEOF'
with open('/home/claude/site/cf-monitor.html', 'r') as f:
    html = f.read()

new_entry = """  {
    id: 'ZONE_ID',
    name: 'DOMAIN_NAME',
    baseline: null
  },
  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────"""

html = html.replace(
    "  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────",
    new_entry
)
with open('/home/claude/site/cf-monitor.html', 'w') as f:
    f.write(html)
print("✅ Zone added")
PYEOF

# 3. Deploy
CLOUDFLARE_API_TOKEN="CF_PAGES_TOKEN_HERE" \
CLOUDFLARE_ACCOUNT_ID="${CF_ACCOUNT_ID}" \
npx wrangler pages deploy /home/claude/site --project-name=pages-bizasa
```

**URL sau deploy:** `https://cf-monitor.bizasa.com/cf-monitor.html`
(hoặc nếu đã set custom domain: `https://cf-monitor.bizasa.com`)

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

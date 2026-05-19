"""
Cloudflare WP Audit — Publish Zone to CF Monitor (v1.1)
Thêm zone mới + changelog vào cf-monitor.html và deploy lên Cloudflare Pages.

Usage: python3 publish_zone.py apply_results.json verify_report.json [baseline.json]

baseline.json (optional) — nếu có thì inject luôn, không có thì set null
"""

import json, sys, os, subprocess, datetime, base64, urllib.request

PAGES_TOKEN      = "${CF_PAGES_TOKEN}"
PAGES_ACCOUNT_ID = "${CF_ACCOUNT_ID}"
MONITOR_URL      = "https://cf-monitor.bizasa.com/cf-monitor.html"
SITE_DIR         = "/home/claude/site"

RES_FILE    = sys.argv[1] if len(sys.argv) > 1 else "apply_results.json"
VER_FILE    = sys.argv[2] if len(sys.argv) > 2 else "verify_report.json"
BASE_FILE   = sys.argv[3] if len(sys.argv) > 3 else None

# ── Load data ─────────────────────────────────────────────────
try:
    with open(RES_FILE) as f:
        apply_res = json.load(f)
    with open(VER_FILE) as f:
        verify_rep = json.load(f)
except Exception as e:
    print(f"❌ Cannot load files: {e}")
    sys.exit(1)

zone_id  = apply_res["zone_id"]
domain   = apply_res.get("domain", "unknown")
aud_date = apply_res.get("audit_date", datetime.datetime.now().strftime("%Y-%m-%d"))

# Optional baseline
baseline_obj = None
if BASE_FILE and os.path.exists(BASE_FILE):
    with open(BASE_FILE) as f:
        baseline_obj = json.load(f)

# ── Build changelog entries ───────────────────────────────────
changelog_items = []
for r in apply_res["results"]:
    if r["status"] in ("applied", "applied_verify_warn"):
        # Find verify status
        ver_item = next((v for v in verify_rep["items"] if v.get("id") == r["id"]), None)
        ver_ok = ver_item["passed"] if ver_item else None
        changelog_items.append({
            "title": r["title"],
            "category": r.get("category", ""),
            "severity": r.get("severity", ""),
            "status": r["status"],
            "verified": ver_ok,
            "timestamp": r.get("timestamp", aud_date)[:10]
        })
    elif r["status"] == "skipped":
        changelog_items.append({
            "title": r["title"],
            "category": r.get("category", ""),
            "severity": r.get("severity", ""),
            "status": "skipped",
            "verified": None,
            "timestamp": aud_date
        })

# ── Fetch current cf-monitor.html ────────────────────────────
print("📥 Fetching current cf-monitor.html...")
os.makedirs(SITE_DIR, exist_ok=True)
try:
    req = urllib.request.Request(MONITOR_URL)
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode()
    print(f"   Fetched {len(html)} chars")
except Exception as e:
    print(f"   Fetch failed ({e}), trying local copy...")
    with open(f"{SITE_DIR}/cf-monitor.html") as f:
        html = f.read()

# ── Check if zone already exists ─────────────────────────────
if f"id: '{zone_id}'" in html:
    print(f"ℹ️  Zone {domain} already in ZONES array — skipping zone add, updating changelog only")
    zone_is_new = False
else:
    print(f"➕ Zone {domain} not found — adding to ZONES array")
    zone_is_new = True

# ── Build zone JS entry ───────────────────────────────────────
if zone_is_new:
    if baseline_obj:
        baseline_js = json.dumps(baseline_obj, indent=6)
        baseline_block = f"baseline: {baseline_js}"
    else:
        baseline_block = "baseline: null   // set sau khi tích lũy đủ data"

    changelog_js = json.dumps(changelog_items, indent=6, ensure_ascii=False)

    new_zone_entry = f"""  {{
    id: '{zone_id}',
    name: '{domain}',
    auditDate: '{aud_date}',
    {baseline_block},
    changelog: {changelog_js}
  }},
  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────"""

    html = html.replace(
        "  // ── THÊM ZONE MỚI Ở ĐÂY ──────────────────────────────────",
        new_zone_entry
    )
    print(f"   Zone entry injected")

else:
    # Zone exists — update changelog only
    # Find existing changelog for this zone and append
    cl_str = json.dumps(changelog_items, indent=6, ensure_ascii=False)
    # Simple append: find the zone's changelog array and replace
    # This uses a safe marker approach
    old_marker = f"id: '{zone_id}'"
    # Find position and replace changelog field
    idx = html.find(old_marker)
    if idx > 0:
        # Find changelog: [ within next 500 chars
        cl_start = html.find("changelog: [", idx, idx+600)
        if cl_start > 0:
            cl_end = html.find("],", cl_start) + 2
            new_cl_block = f"changelog: {cl_str}"
            html = html[:cl_start] + new_cl_block + html[cl_end:]
            print("   Changelog updated for existing zone")

# ── Write updated HTML ────────────────────────────────────────
out_path = f"{SITE_DIR}/cf-monitor.html"
with open(out_path, "w") as f:
    f.write(html)
print(f"✅ cf-monitor.html updated ({len(html)} chars)")

# ── Deploy to Cloudflare Pages ────────────────────────────────
print("\n🚀 Deploying to Cloudflare Pages...")
env = os.environ.copy()
env["CLOUDFLARE_API_TOKEN"]   = PAGES_TOKEN
env["CLOUDFLARE_ACCOUNT_ID"]  = PAGES_ACCOUNT_ID

cmd = f"npx wrangler pages deploy {SITE_DIR} --project-name=pages-bizasa"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, cwd="/home/claude")

if result.returncode == 0:
    print("✅ Deployed successfully!")
    lines = result.stdout.strip().split("\n")
    for line in lines:
        if "pages.dev" in line or "Deployment" in line or "bizasa" in line.lower():
            print(f"   {line.strip()}")
    print(f"\n🌐 Live: https://cf-monitor.bizasa.com/cf-monitor.html")
else:
    print(f"❌ Deploy failed:\n{result.stderr[:400]}")

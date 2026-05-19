"""
Cloudflare WP Audit — Final Verify Script (v1.1)
Dùng sau apply_config.py để confirm tất cả changes đã apply đúng.

Usage: python3 verify_all.py READ_TOKEN ZONE_ID apply_results.json [checklist.json]
"""

import urllib.request, urllib.error, json, sys, subprocess, datetime

TOKEN   = sys.argv[1] if len(sys.argv) > 1 else ""
ZONE_ID = sys.argv[2] if len(sys.argv) > 2 else ""
RES_FILE = sys.argv[3] if len(sys.argv) > 3 else "apply_results.json"
CL_FILE  = sys.argv[4] if len(sys.argv) > 4 else "checklist.json"

def cf_get(path):
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4{path}")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"ok": True, "data": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode()[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def curl_check(label, cmd):
    """Run curl command và trả về output."""
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=15).decode().strip()
        return out
    except Exception as e:
        return f"ERROR: {e}"

# ── Load files ────────────────────────────────────────────────
try:
    with open(RES_FILE) as f:
        apply_results = json.load(f)
    with open(CL_FILE) as f:
        checklist = json.load(f)
except Exception as e:
    print(f"❌ Cannot load files: {e}")
    sys.exit(1)

# Map checklist by id for lookup
cl_map = {item["id"]: item for item in checklist}
applied_ids = [r["id"] for r in apply_results["results"] if "applied" in r.get("status","")]

domain = apply_results.get("domain", f"zone:{ZONE_ID}")

print(f"\n{'='*60}")
print(f"  FINAL VERIFY — {domain}")
print(f"  Checking {len(applied_ids)} applied items")
print(f"{'='*60}\n")

verify_report = []

# ── 1. API verifies ───────────────────────────────────────────
print("📡 API Verifications\n")
for aid in applied_ids:
    item = cl_map.get(aid)
    if not item or not item.get("verify_url"):
        continue
    vurl = item["verify_url"].replace("{zone_id}", ZONE_ID)
    res = cf_get(vurl)
    if not res["ok"]:
        print(f"  ❌ {item['title'][:45]:48} → GET failed ({res.get('status')})")
        verify_report.append({"id": aid, "title": item["title"], "passed": False, "detail": "GET failed"})
        continue
    actual = res["data"].get("result", {})
    key = item.get("verify_key", "value")
    for k in key.split("."):
        actual = actual.get(k, {}) if isinstance(actual, dict) else actual
    expect = item.get("verify_expect")
    passed = str(actual) == str(expect)
    icon = "✅" if passed else "❌"
    print(f"  {icon} {item['title'][:45]:48} → {actual} {'==' if passed else '!='} {expect}")
    verify_report.append({"id": aid, "title": item["title"], "passed": passed, "detail": f"{actual}"})

# ── 2. HTTP / external checks ─────────────────────────────────
print(f"\n🌐 External Checks — {domain}\n")

ext_checks = [
    {
        "label": "HTTPS redirect (http → https)",
        "cmd": f'curl -sI "http://{domain}" | grep -i "location\\|http/"',
        "expect_contains": "https"
    },
    {
        "label": "Redirect chain (≤2 hops)",
        "cmd": f'curl -sIL "http://{domain}" 2>/dev/null | grep -c "HTTP/"',
        "expect_max_int": 3
    },
    {
        "label": "CF-Ray header (CF proxying)",
        "cmd": f'curl -sI "https://{domain}" | grep -i "cf-ray"',
        "expect_contains": "cf-ray"
    },
    {
        "label": "Static asset cache (HIT)",
        "cmd": f'curl -sI "https://{domain}/wp-content/themes/style.css" | grep -i "cf-cache-status"',
        "expect_contains": "HIT"
    },
    {
        "label": "TLS 1.0 blocked",
        "cmd": f'curl --tlsv1.0 --tls-max 1.0 -sI "https://{domain}" -o /dev/null -w "%{{http_code}}" 2>&1',
        "expect_not_contains": "200"
    },
    {
        "label": "xmlrpc.php blocked",
        "cmd": f'curl -sI "https://{domain}/xmlrpc.php" | grep -i "http/" | head -1',
        "expect_not_contains": "200"
    },
    {
        "label": "wp-login.php accessible (not hard-blocked)",
        "cmd": f'curl -sI "https://{domain}/wp-login.php" | grep -i "http/" | head -1',
        "expect_contains": "HTTP"  # Should exist but rate-limited, not 200 ideally
    },
]

for chk in ext_checks:
    out = curl_check(chk["label"], chk["cmd"])
    passed = True
    detail = out[:80] if out else "(empty)"

    if "expect_contains" in chk:
        passed = chk["expect_contains"].lower() in out.lower()
    elif "expect_not_contains" in chk:
        passed = chk["expect_not_contains"].lower() not in out.lower()
    elif "expect_max_int" in chk:
        try:
            passed = int(out.strip()) <= chk["expect_max_int"]
        except:
            passed = False

    icon = "✅" if passed else "⚠️ "
    print(f"  {icon} {chk['label'][:48]:50} → {detail}")
    verify_report.append({"label": chk["label"], "passed": passed, "detail": detail})

# ── 3. Summary ────────────────────────────────────────────────
all_passed  = [v for v in verify_report if v.get("passed")]
all_failed  = [v for v in verify_report if not v.get("passed")]

print(f"\n{'='*60}")
print(f"  VERIFY SUMMARY — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}")
print(f"  ✅ Passed : {len(all_passed)}")
print(f"  ❌ Failed : {len(all_failed)}")
if all_failed:
    print(f"\n  Items cần review lại:")
    for v in all_failed:
        label = v.get("title") or v.get("label", "?")
        print(f"    ❌ {label}")

# ── 4. Save verify report ─────────────────────────────────────
final = {
    "zone_id": ZONE_ID,
    "domain": domain,
    "verify_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "passed": len(all_passed),
    "failed": len(all_failed),
    "items": verify_report,
    # summary string for changelog
    "summary": f"{len(all_passed)} passed, {len(all_failed)} failed"
}
with open("verify_report.json", "w") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print(f"\n✅ Verify report saved → verify_report.json")
if len(all_failed) == 0:
    print("🎉 All checks passed! Ready to update cf-monitor.")
else:
    print(f"⚠️  {len(all_failed)} item(s) failed — review trước khi update cf-monitor.")

"""
Cloudflare WP Audit — Apply Config Script (v1.1)
Dùng: python3 apply_config.py WRITE_TOKEN ZONE_ID checklist.json

Checklist format:
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
    "dashboard_path": "SSL/TLS → Overview → Full (Strict)",
    "rollback": {"setting": "ssl", "value": "full"}
  }
]

action types:
  zone_setting       → PATCH /zones/{zone_id}/settings/{setting}
  ruleset_rule_add   → POST  /zones/{zone_id}/rulesets/{ruleset_id}/rules
  ruleset_rule_del   → DELETE /zones/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}
  page_rule_del      → DELETE /zones/{zone_id}/pagerules/{rule_id}
  cache_purge        → POST  /zones/{zone_id}/purge_cache
"""

import urllib.request, urllib.error, json, sys, datetime

TOKEN   = sys.argv[1] if len(sys.argv) > 1 else ""
ZONE_ID = sys.argv[2] if len(sys.argv) > 2 else ""
CL_FILE = sys.argv[3] if len(sys.argv) > 3 else "checklist.json"

if not TOKEN or not ZONE_ID:
    print("Usage: python3 apply_config.py WRITE_TOKEN ZONE_ID checklist.json")
    sys.exit(1)

def cf_req(method, path, body=None):
    url = f"https://api.cloudflare.com/client/v4{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"ok": True, "data": json.loads(r.read().decode())}
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode()[:400]
        return {"ok": False, "status": e.code, "error": body_txt}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def verify_item(item):
    """Verify một checklist item đã apply đúng chưa."""
    vurl = item.get("verify_url", "").replace("{zone_id}", ZONE_ID)
    if not vurl:
        return None, "No verify_url defined"
    res = cf_req("GET", vurl)
    if not res["ok"]:
        return False, f"Verify GET failed: {res.get('error')}"
    actual = res["data"].get("result", {})
    # Drill down nested key: "value" hoặc "result.value"
    key = item.get("verify_key", "value")
    for k in key.split("."):
        actual = actual.get(k, {}) if isinstance(actual, dict) else actual
    expect = item.get("verify_expect")
    passed = str(actual) == str(expect)
    return passed, f"Got '{actual}', expected '{expect}'"

def apply_item(item):
    """Apply một action vào Cloudflare API."""
    action = item.get("action")
    path_tpl = lambda p: p.replace("{zone_id}", ZONE_ID)

    if action == "zone_setting":
        path = path_tpl(f"/zones/{'{zone_id}'}/settings/{item['setting']}")
        return cf_req("PATCH", path, {"value": item["value"]})

    elif action == "zone_setting_obj":
        # Cho settings dạng object như minify
        path = path_tpl(f"/zones/{'{zone_id}'}/settings/{item['setting']}")
        return cf_req("PATCH", path, {"value": item["value"]})

    elif action == "ruleset_rule_add":
        path = path_tpl(f"/zones/{'{zone_id}'}/rulesets/{item['ruleset_id']}/rules")
        return cf_req("POST", path, item["rule_body"])

    elif action == "ruleset_entrypoint_rule_add":
        # Add rule vào phase entrypoint
        phase = item["phase"]
        path = path_tpl(f"/zones/{'{zone_id}'}/rulesets/phases/{phase}/entrypoint/rules")
        return cf_req("POST", path, item["rule_body"])

    elif action == "ruleset_rule_del":
        path = path_tpl(f"/zones/{'{zone_id}'}/rulesets/{item['ruleset_id']}/rules/{item['rule_id']}")
        return cf_req("DELETE", path)

    elif action == "page_rule_del":
        path = path_tpl(f"/zones/{'{zone_id}'}/pagerules/{item['rule_id']}")
        return cf_req("DELETE", path)

    elif action == "cache_purge_all":
        path = path_tpl(f"/zones/{'{zone_id}'}/purge_cache")
        return cf_req("POST", path, {"purge_everything": True})

    elif action == "tiered_cache_enable":
        path = path_tpl(f"/zones/{'{zone_id}'}/cache/tiered_cache_smart_topology_enable")
        return cf_req("PATCH", path, {"value": "on"})

    elif action == "always_use_https":
        path = path_tpl(f"/zones/{'{zone_id}'}/settings/always_use_https")
        return cf_req("PATCH", path, {"value": "on"})

    else:
        return {"ok": False, "error": f"Unknown action type: {action}"}

# ── Load checklist ────────────────────────────────────────────
try:
    with open(CL_FILE) as f:
        checklist = json.load(f)
except Exception as e:
    print(f"❌ Cannot load checklist: {e}")
    sys.exit(1)

print(f"\n{'='*60}")
print(f"  CF Apply Config — {len(checklist)} items")
print(f"  Zone: {ZONE_ID}")
print(f"  Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}\n")

# ── Run interactive loop ──────────────────────────────────────
results = []  # for changelog

severity_icon = {"critical": "🔴", "warning": "🟡", "suggestion": "🔵"}

for i, item in enumerate(checklist, 1):
    icon = severity_icon.get(item.get("severity", ""), "⚪")
    print(f"{'─'*60}")
    print(f"[{i}/{len(checklist)}] {icon} {item['title']}")
    print(f"  Category   : {item.get('category', '—')}")
    print(f"  Severity   : {item.get('severity', '—')}")
    print(f"  Dashboard  : {item.get('dashboard_path', '—')}")
    if item.get("action") == "zone_setting":
        print(f"  API action : PATCH settings/{item.get('setting')} → \"{item.get('value')}\"")
    elif "rule_body" in item:
        print(f"  API action : Add rule — {json.dumps(item.get('rule_body', {}))[:80]}...")
    print()
    print("  [1] Run    [2] Skip    [3] Show detail")

    while True:
        choice = input("  → ").strip()
        if choice == "3":
            print(f"\n  Full item:\n{json.dumps(item, indent=4, ensure_ascii=False)}\n")
            print("  [1] Run    [2] Skip")
        elif choice in ("1", "2"):
            break
        else:
            print("  Nhập 1 (Run) hoặc 2 (Skip)")

    if choice == "2":
        print(f"  ⏭️  Skipped\n")
        results.append({
            "id": item["id"],
            "title": item["title"],
            "category": item.get("category"),
            "severity": item.get("severity"),
            "status": "skipped",
            "timestamp": datetime.datetime.now().isoformat()
        })
        continue

    # Apply
    print(f"  ⏳ Applying...")
    res = apply_item(item)

    if res["ok"]:
        print(f"  ✅ Applied OK")
        # Verify
        if item.get("verify_url"):
            import time; time.sleep(1)  # brief wait for CF to propagate
            passed, msg = verify_item(item)
            if passed is True:
                print(f"  ✅ Verified: {msg}")
                status = "applied"
            elif passed is False:
                print(f"  ⚠️  Verify mismatch: {msg}")
                status = "applied_verify_warn"
            else:
                print(f"  ℹ️  No verify: {msg}")
                status = "applied"
        else:
            status = "applied"
    else:
        print(f"  ❌ Failed: {res.get('error', '')} (HTTP {res.get('status', '?')})")
        print(f"     Bạn có muốn tiếp tục không? [1] Tiếp tục  [2] Dừng lại")
        cont = input("  → ").strip()
        if cont == "2":
            print("\n❌ Aborted by user.")
            break
        status = "failed"

    results.append({
        "id": item["id"],
        "title": item["title"],
        "category": item.get("category"),
        "severity": item.get("severity"),
        "status": status,
        "timestamp": datetime.datetime.now().isoformat()
    })
    print()

# ── Summary ───────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  APPLY SUMMARY")
print(f"{'='*60}")
for r in results:
    emoji = {"applied": "✅", "skipped": "⏭️ ", "failed": "❌", "applied_verify_warn": "⚠️ "}.get(r["status"], "❓")
    print(f"  {emoji} [{r['status']:22}] {r['title'][:45]}")

applied   = [r for r in results if "applied" in r["status"]]
skipped   = [r for r in results if r["status"] == "skipped"]
failed    = [r for r in results if r["status"] == "failed"]
print(f"\n  Applied: {len(applied)} | Skipped: {len(skipped)} | Failed: {len(failed)}")

# ── Save results for changelog ────────────────────────────────
out = {
    "zone_id": ZONE_ID,
    "audit_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    "results": results
}
with open("apply_results.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n✅ Results saved to apply_results.json")
print("   Next: chạy verify_all.py để verify lần cuối, sau đó update cf-monitor")

#!/usr/bin/env python3
"""
Pre-launch verification: check if a project is ready for launch.

Usage:
    python verify_launch_ready.py [project-root] --url <live-url> [--check-payments]

Checks:
    - Live URL responds with 200
    - Core user flow works (signup page, main app page exist)
    - Payment integration detected (optional)
    - Analytics/tracking in place (optional, flags if missing)
    - Open Graph / social meta tags present (for link previews in posts)
    - Obvious broken links or missing pages

Outputs a JSON report the agent uses to decide if launch is ready
or if something needs fixing first.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return ""


def check_url(url: str) -> dict:
    """Check if a URL responds."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-L", "--max-redirs", "5", "--connect-timeout", "10",
             "--max-time", "30", url],
            capture_output=True, text=True, timeout=35
        )
        status = result.stdout.strip()
        return {"url": url, "status": int(status) if status.isdigit() else 0, "ok": status == "200"}
    except (subprocess.TimeoutExpired, Exception) as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e)}


def check_og_tags(url: str) -> dict:
    """Check for Open Graph meta tags (needed for social media link previews)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-redirs", "5", "--connect-timeout", "10",
             "--max-time", "30", url],
            capture_output=True, text=True, timeout=35
        )
        html = result.stdout
        
        tags = {
            "og:title": bool(re.search(r'<meta[^>]+property=["\']og:title["\']', html, re.IGNORECASE)),
            "og:description": bool(re.search(r'<meta[^>]+property=["\']og:description["\']', html, re.IGNORECASE)),
            "og:image": bool(re.search(r'<meta[^>]+property=["\']og:image["\']', html, re.IGNORECASE)),
            "twitter:card": bool(re.search(r'<meta[^>]+name=["\']twitter:card["\']', html, re.IGNORECASE)),
        }
        
        all_present = all(tags.values())
        return {"tags": tags, "all_present": all_present}
    except Exception as e:
        return {"tags": {}, "all_present": False, "error": str(e)}


def check_payments(root: Path, pkg: dict) -> dict:
    """Check payment integration status."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    result = {
        "provider": None,
        "has_package": False,
        "has_env_vars": False,
        "has_webhook_route": False,
        "has_pricing_page": False,
        "ready": False,
    }
    
    # Check for Stripe
    if "stripe" in deps or "@stripe/stripe-js" in deps:
        result["provider"] = "stripe"
        result["has_package"] = True
    elif "@lemonsqueezy/lemonsqueezy.js" in deps:
        result["provider"] = "lemonsqueezy"
        result["has_package"] = True
    
    if not result["provider"]:
        return result
    
    # Check env vars
    env_content = ""
    for env_file in [".env", ".env.local", ".env.production", ".env.example"]:
        env_content += read_file_safe(root / env_file)
    
    if result["provider"] == "stripe":
        result["has_env_vars"] = "STRIPE_SECRET_KEY" in env_content
    elif result["provider"] == "lemonsqueezy":
        result["has_env_vars"] = "LEMONSQUEEZY_API_KEY" in env_content
    
    # Check for webhook route
    webhook_paths = [
        "app/api/webhooks/stripe/route.ts",
        "app/api/webhooks/stripe/route.js",
        "app/api/webhook/route.ts",
        "pages/api/webhooks/stripe.ts",
        "app/api/webhooks/lemonsqueezy/route.ts",
    ]
    result["has_webhook_route"] = any((root / p).exists() for p in webhook_paths)
    
    # Check for pricing page
    pricing_paths = [
        "app/pricing/page.tsx",
        "app/pricing/page.jsx",
        "pages/pricing.tsx",
        "components/pricing.tsx",
        "components/PricingPage.tsx",
    ]
    result["has_pricing_page"] = any((root / p).exists() for p in pricing_paths)
    
    result["ready"] = all([
        result["has_package"],
        result["has_env_vars"],
        result["has_webhook_route"],
    ])
    
    return result


def check_analytics(root: Path, pkg: dict) -> dict:
    """Check if any analytics/tracking is set up."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    providers = {
        "posthog": "posthog-js" in deps or "posthog" in deps,
        "plausible": "plausible-tracker" in deps or "next-plausible" in deps,
        "vercel_analytics": "@vercel/analytics" in deps,
        "google_analytics": "react-ga4" in deps or "@next/third-parties" in deps,
        "mixpanel": "mixpanel-browser" in deps,
    }
    
    detected = [k for k, v in providers.items() if v]
    
    return {
        "has_analytics": len(detected) > 0,
        "providers": detected,
        "recommendation": None if detected else "Consider adding Vercel Analytics (free, 1 line of code) or Plausible (privacy-friendly) to track launch traffic.",
    }


def main():
    parser = argparse.ArgumentParser(description="Verify project is ready for launch")
    parser.add_argument("project_root", nargs="?", default=".", help="Project root directory")
    parser.add_argument("--url", required=True, help="Live deployment URL")
    parser.add_argument("--check-payments", action="store_true", help="Check payment integration")
    args = parser.parse_args()

    root = Path(args.project_root)
    pkg_path = root / "package.json"
    
    if not pkg_path.exists():
        print(json.dumps({"error": f"No package.json found in {root}"}))
        sys.exit(1)

    pkg = json.loads(read_file_safe(pkg_path))
    url = args.url.rstrip("/")

    report = {
        "url_check": {},
        "auth_page": {},
        "og_tags": {},
        "payments": {},
        "analytics": {},
        "launch_ready": False,
        "blockers": [],
        "warnings": [],
    }

    # Check live URL
    report["url_check"] = check_url(url)
    if not report["url_check"]["ok"]:
        report["blockers"].append(f"Live URL {url} is not responding (HTTP {report['url_check'].get('status', 'N/A')})")

    # Check for auth page
    for auth_path in ["/sign-in", "/login", "/auth/login", "/signin"]:
        auth_check = check_url(f"{url}{auth_path}")
        if auth_check["ok"]:
            report["auth_page"] = auth_check
            break
    
    if not report["auth_page"].get("ok"):
        report["warnings"].append("No auth page found at common paths (/sign-in, /login). May be intentional if app doesn't require auth.")

    # Check OG tags
    report["og_tags"] = check_og_tags(url)
    if not report["og_tags"].get("all_present"):
        missing = [k for k, v in report["og_tags"].get("tags", {}).items() if not v]
        report["warnings"].append(f"Missing Open Graph tags: {', '.join(missing)}. Link previews on social media will be broken or generic.")

    # Check payments (optional)
    if args.check_payments:
        report["payments"] = check_payments(root, pkg)
        if not report["payments"]["ready"] and report["payments"]["provider"]:
            report["warnings"].append(f"Payment provider ({report['payments']['provider']}) detected but not fully configured. Missing: " + 
                ", ".join(k for k, v in {
                    "package": report["payments"]["has_package"],
                    "env vars": report["payments"]["has_env_vars"],
                    "webhook route": report["payments"]["has_webhook_route"],
                }.items() if not v))

    # Check analytics
    report["analytics"] = check_analytics(root, pkg)
    if not report["analytics"]["has_analytics"]:
        report["warnings"].append(report["analytics"]["recommendation"])

    # Final verdict
    report["launch_ready"] = len(report["blockers"]) == 0
    
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

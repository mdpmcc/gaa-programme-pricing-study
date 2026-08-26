#!/usr/bin/env python3
"""Create public repo gaa-programme-pricing-study via GitHub PAT; verify it exists."""
import json, subprocess, sys, pathlib

creds = pathlib.Path.home() / ".git-credentials"
token = None
for line in creds.read_text().splitlines():
    if "github.com" in line and ":" in line:
        try:
            token = line.split("https://")[1].split(":")[1].split("@")[0]
        except IndexError:
            continue
        break
if not token:
    sys.exit("NO TOKEN FOUND")

def gh(method, path, payload=None):
    cmd = [
        "curl", "-s", "-X", method,
        f"https://api.github.com{path}",
        "-H", "Authorization: token " + token,
        "-H", "Accept: application/vnd.github+json",
    ]
    if payload is not None:
        cmd += ["-d", json.dumps(payload)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": out[:500]}

# Create repo (idempotent: 422 if name exists -> verify instead)
created = gh("POST", "/user/repos", {
    "name": "gaa-programme-pricing-study",
    "private": False,
    "description": "Pricing study: GAA match-programme content agency for clubs (print + digital). Van Westendorp + Gabor-Granger, two season-retainer price variants (EUR250 vs EUR750).",
    "has_issues": False, "has_wiki": False, "has_projects": False, "auto_init": False,
})
if created.get("full_name"):
    print("CREATED:", created["full_name"])
else:
    print("CREATE RESPONSE:", created.get("message"), "| errors:", created.get("errors"))

check = gh("GET", "/repos/mdpmcc/gaa-programme-pricing-study")
print("VERIFY:", check.get("full_name"), "| private:", check.get("private"),
      "| default_branch:", check.get("default_branch"))
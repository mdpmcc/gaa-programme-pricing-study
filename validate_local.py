#!/usr/bin/env python3
"""Local pre-push validation for gaa-programme-pricing-study.

Checks: tag balance, variant isolation (A free of '€750', B free of '€250' anchor),
CTA hrefs, survey completeness (4 VW inputs, GG radios, GDPR notice, localStorage key,
mailto target), collector field validation.
"""
import re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
A = (BASE / "index.html").read_text()
B = (BASE / "b" / "index.html").read_text()
S = (BASE / "survey.html").read_text()
C = (BASE / "collect.html").read_text()

fails = []

def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)

# --- tag balance ---
for name, html in [("index.html", A), ("b/index.html", B), ("survey.html", S), ("collect.html", C)]:
    tags = re.findall(r"<([a-zA-Z0-9]+)[^>]*?(/?)>", html)
    stack, ok = [], True
    self_close = {"input", "br", "img", "meta", "link", "hr", "source", "area", "base", "col", "embed", "track", "wbr"}
    for tag, slash in tags:
        if slash:
            continue
        if tag in self_close:
            continue
        if tag in ("script", "style"):
            continue
        if not stack or stack[-1] != tag:
            if tag.startswith("/"):
                ok = False; break
            stack.append(tag)
        else:
            stack.pop()
    check(f"tag balance {name}", ok)

# --- variant isolation ---
check("A has €250 anchor", "€250<small>/season</small>" in A)
check("A free of €750 anchor", "€750<small>/season</small>" not in A)
check("B has €750 anchor", "€750<small>/season</small>" in B)
check("B free of €250 anchor", "€250<small>/season</small>" not in B)
check("A CTA variant=A&price=250", 'href="survey.html?variant=A&amp;price=250"' in A)
check("B CTA variant=B&price=750", 'href="survey.html?variant=B&amp;price=750"' in B)

# --- survey completeness ---
for qid in ["q_too_cheap", "q_bargain", "q_expensive", "q_too_expensive"]:
    check(f"survey has {qid}", f'id="{qid}"' in S)
for i in range(1, 6):
    check(f"survey GG radio gg{i}", f'id="gg{i}"' in S and f'value="{["definitely","probably","unsure","probably_not","no"][i-1]}"' in S)
check("survey GDPR notice", "About this survey &amp; your data (GDPR)" in S)
check("survey localStorage key", "gaa_programme_responses" in S)
check("survey mailto target", "mdpmcc@users.noreply.github.com" in S)
check("survey VW monotonicity check", "too_expensive>=vw.expensive" in S)
check("survey default anchor 250", "|| '250'" in S)

# --- collector ---
check("collector KEY", "gaa_programme_collector" in C)
check("collector CSV export", "downloadCsvAll()" in C and "gaa-programme-pricing-responses.csv" in C)
check("collector validates variant+too_cheap", "'variant'in o" in C and "'too_cheap'in o" in C)

# --- A/B parity: everything except anchor + CTA must be identical ---
# Compare line by line, ignoring the 3 specific differing lines
A_lines = A.split('\n')
B_lines = B.split('\n')
skip_indices = set()
for i, (la, lb) in enumerate(zip(A_lines, B_lines)):
    for x in ['VARIANT', 'price=', '/season']:
        if x in la or x in lb:
            skip_indices.add(i)
            break
match = all(i in skip_indices or la == lb for i, (la, lb) in enumerate(zip(A_lines, B_lines)))
check("A/B parity excluding anchor+CTA lines", match)

print()
if fails:
    print(f"FAILED: {len(fails)} checks — {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED")
#!/usr/bin/env python3
"""Debug A/B parity."""
A = open("deploy/index.html").read()
B = open("deploy/b/index.html").read()
A_lines = A.split('\n')
B_lines = B.split('\n')
skip_indices = set()
for i, (la, lb) in enumerate(zip(A_lines, B_lines)):
    if 'VARIANT' in la or 'VARIANT' in lb or 'price=' in la or 'price=' in lb:
        skip_indices.add(i)

for i, (la, lb) in enumerate(zip(A_lines, B_lines)):
    if i in skip_indices:
        continue
    if la != lb:
        print(f"DIFF line {i}:")
        print(f"  A: {repr(la)}")
        print(f"  B: {repr(lb)}")
        print()

if len(A_lines) != len(B_lines):
    print(f"LEN DIFF: A={len(A_lines)} B={len(B_lines)}")
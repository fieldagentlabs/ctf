#!/usr/bin/env python3
"""Write nginx exact-match locations for Juice Shop's top-level frontend files (run at image build)."""
import sys
from pathlib import Path

dist = Path(sys.argv[1])
out = Path(sys.argv[2])
lines = ["# Generated at image build from %s. Do not edit." % dist]
for p in sorted(dist.iterdir()):
    if p.name == "index.html":
        continue
    if p.is_file():
        lines.append("location = /%s { proxy_pass $shop; }" % p.name)
    elif p.is_dir() and p.name != "assets":
        lines.append("location ^~ /%s/ { proxy_pass $shop; }" % p.name)
out.write_text("\n".join(lines) + "\n")
print("wrote %d locations to %s" % (len(lines) - 1, out))

import subprocess, sys

def git(*a, **k):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True, **k).stdout.strip()

print("HEAD        :", git("-C", ".", "rev-parse", "--short", "HEAD"))
print("origin/main :", git("-C", ".", "rev-parse", "--short", "origin/main"))
print("equal?      :", "YES" if git("rev-parse", "HEAD") == git("rev-parse", "origin/main") else "NO")
print()
print("-- top of log --")
for line in git("log", "--oneline", "-4").splitlines():
    print("   ", line)
print()
print("-- staged summary (porcelain v1 count by XY) --")
from collections import Counter
c = Counter()
for line in git("status", "--porcelain").splitlines():
    c[line[0]] += 1
print("   first-col counts:", dict(c))
print()
print("-- any staged path that still *adds* a live blob > 90MB (would fail push)? --")
found = False
for line in git("diff", "--cached", "--name-only").splitlines():
    blob = git("ls-files", "--stage", "--", line).split()
    if not blob:
        continue
    sha = blob[1] if len(blob) > 1 else ""
    if not sha:
        continue
    sz = git("cat-file", "-s", sha)
    if sz.isdigit() and int(sz) > 90_000_000:
        print("   OVERSIZED", sz, line)
        found = True
if not found:
    print("   none (good)")
print()
print("-- does HEAD tree still reference any >90MB blob? (should be none; binary is gone) --")
for line in git("ls-tree", "-r", "-l", "HEAD").splitlines():
    parts = line.split()
    try:
        sz = int(parts[3]) if len(parts) == 5 else int(parts[3])
    except Exception:
        continue
    if sz > 90_000_000:
        print("   OVERSIZED(HEAD tree)", sz, parts[-1])
print("   (above shows any >90MB in HEAD tree)")
print()
print("-- what CHANGES did origin/main..HEAD contain (files, top by size)? --")
big = []
for line in git("diff", "--stat", "-M", "origin/main..HEAD").splitlines():
    pass
r = git("diff", "--numstat", "-M", "origin/main..HEAD")
print(r)

#!/usr/bin/env python3
"""Kiểm tra trước khi merge (chạy ở GitHub Actions và chạy tay trước khi mở PR).

  python3 scripts/ci_check.py                    # so với origin/main
  python3 scripts/ci_check.py --base origin/main

Kiểm:
  1. catalog.py check: catalog hợp lệ, recipe có heading, regex hợp lệ, references/ không chứa code block.
  2. CATALOG.md đã render lại (khớp catalog.json).
  3. Không commit file riêng máy (local.json) và không có ID quảng cáo thật (ca-app-pub-…, trừ ID test Google).
  4. Có thay đổi nội dung so với base → phải tăng "Phiên bản **x.y.z**" trong SKILL.md và CHANGELOG.md mở đầu
     bằng "## x.y.z". Riêng thay đổi chỉ ở README.md / CONTRIBUTING.md / .github/ thì không cần.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_ONLY = re.compile(r"^(README\.md|CONTRIBUTING\.md|\.github/.*)$")
REAL_AD_ID = re.compile(r"ca-app-pub-(?!3940256099942544)\d{16}[/~]\d{10}")


def sh(*args, check=False):
    r = subprocess.run(list(args), cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stdout + r.stderr)
    return r


def version(text):
    m = re.search(r"Phiên bản \*\*(\d+)\.(\d+)\.(\d+)\*\*", text or "")
    return tuple(int(x) for x in m.groups()) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    errors = []

    r = sh(sys.executable, "scripts/catalog.py", "check")
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    if r.returncode != 0:
        errors.append("catalog.py check lỗi:\n" + "\n".join(l for l in r.stdout.splitlines() if l.startswith("ERROR")))

    sh(sys.executable, "scripts/catalog.py", "render")
    if sh("git", "diff", "--quiet", "--", "CATALOG.md").returncode != 0:
        errors.append("CATALOG.md chưa render lại: chạy `python3 scripts/catalog.py render` rồi commit.")
        sh("git", "checkout", "--", "CATALOG.md")

    if sh("git", "ls-files", "local.json").stdout.strip():
        errors.append("local.json là file riêng từng máy, không được commit (git rm --cached local.json).")
    for f in sh("git", "ls-files").stdout.split():
        if f.endswith((".md", ".json", ".py")):
            try:
                text = open(os.path.join(ROOT, f), encoding="utf-8").read()
            except OSError:
                continue
            if REAL_AD_ID.search(text):
                errors.append(f"{f}: có ID quảng cáo thật (ca-app-pub-…) — skill không chứa ID/secret.")

    base_ok = sh("git", "rev-parse", "--verify", "--quiet", a.base).returncode == 0
    if not base_ok:
        print(f"(Không có {a.base} — bỏ qua kiểm tăng phiên bản)")
    else:
        mb = sh("git", "merge-base", a.base, "HEAD").stdout.strip() or a.base
        changed = sh("git", "diff", "--name-only", mb).stdout.split()
        changed += sh("git", "ls-files", "--others", "--exclude-standard").stdout.split()
        changed = sorted(set(f for f in changed if f and f != "CATALOG.md"))
        content = [f for f in changed if not DOC_ONLY.match(f)]
        if content:
            old_v = version(sh("git", "show", f"{a.base}:SKILL.md").stdout)
            new_v = version(open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read())
            if not new_v or (old_v and new_v <= old_v):
                errors.append(f"Có thay đổi nội dung ({len(content)} file) nhưng chưa tăng phiên bản trong SKILL.md "
                              f"(base {'.'.join(map(str, old_v)) if old_v else '?'}).")
            else:
                head = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
                m = re.search(r"^## (\d+\.\d+\.\d+)", head, re.M)
                if not m or m.group(1) != ".".join(map(str, new_v)):
                    errors.append(f"CHANGELOG.md phải mở đầu bằng mục '## {'.'.join(map(str, new_v))} — <ngày>'.")
        print(f"Thay đổi so với {a.base}: {len(changed)} file ({len(content)} file nội dung)")

    if errors:
        print("\n❌ CI chưa đạt:")
        for e in errors:
            print(" -", e)
        return 1
    print("✅ CI đạt")
    return 0


if __name__ == "__main__":
    sys.exit(main())

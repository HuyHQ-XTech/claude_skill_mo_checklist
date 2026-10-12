#!/usr/bin/env python3
"""Cập nhật skill mo-checklist từ repo git chung của team (stdlib).

  update.py            # kéo bản mới (git pull --ff-only) rồi in phần CHANGELOG mới
  update.py --check    # chỉ kiểm có bản mới không (git fetch, không sửa gì), dùng ở đầu mỗi lần chạy skill

Không bao giờ ghi đè sửa đổi local: thư mục skill có thay đổi chưa commit thì dừng và hướng dẫn.
"""
import os
import re
import subprocess
import sys

SKILL_DIR = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def git(*args, timeout=20):
    try:
        r = subprocess.run(["git", "-C", SKILL_DIR, *args], capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError:
        return 127, "", "không có git"


def version_at(rev=None):
    if rev:
        code, out, _ = git("show", f"{rev}:SKILL.md")
        text = out if code == 0 else ""
    else:
        with open(os.path.join(SKILL_DIR, "SKILL.md")) as f:
            text = f.read()
    m = re.search(r"Phiên bản \*\*([\w.\-]+)\*\*", text)
    return m.group(1) if m else "?"


def main():
    check_only = "--check" in sys.argv
    if git("rev-parse", "--is-inside-work-tree")[0] != 0:
        print(f"Skill ở {SKILL_DIR} không phải git repo → không cập nhật tự động được.\n"
              "Cài lại bằng git clone (xem README.md của skill).")
        return 0 if check_only else 1
    code, upstream, _ = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if code != 0:
        print("Nhánh hiện tại chưa gắn upstream (git branch --set-upstream-to origin/main).")
        return 0 if check_only else 1
    code, _, err = git("fetch", "--quiet", timeout=10 if check_only else 60)
    if code != 0:
        print(f"Không fetch được ({err or 'lỗi mạng/quyền'}). Đang dùng phiên bản {version_at()}.")
        return 0 if check_only else 1
    _, behind, _ = git("rev-list", "--count", f"HEAD..{upstream}")
    _, ahead, _ = git("rev-list", "--count", f"{upstream}..HEAD")
    cur = version_at()
    if behind in ("", "0"):
        print(f"mo-checklist {cur}: đã là bản mới nhất.")
        return 0
    new = version_at(upstream)
    if check_only:
        print(f"⬆ Có bản mới mo-checklist {new} (đang dùng {cur}, chậm {behind} commit). Chạy /mo-checklist update.")
        return 0
    _, dirty, _ = git("status", "--porcelain", "--untracked-files=no")
    if dirty:
        print("Thư mục skill có sửa đổi chưa commit, không pull để tránh mất:\n" + dirty +
              "\nMuốn giữ thì gửi cho người bảo trì; muốn bỏ thì chạy: git -C \"" + SKILL_DIR +
              "\" stash  (rồi chạy lại update).")
        return 1
    if ahead not in ("", "0"):
        print(f"Bản local có {ahead} commit chưa push (máy của người bảo trì?). Không pull tự động — dùng git pull "
              "--rebase bằng tay.")
        return 1
    _, old_head, _ = git("rev-parse", "HEAD")
    code, out, err = git("pull", "--ff-only", "--quiet", timeout=120)
    if code != 0:
        print("git pull lỗi:\n" + (err or out))
        return 1
    _, log, _ = git("log", "--oneline", f"{old_head}..HEAD")
    _, cl, _ = git("diff", "--unified=0", f"{old_head}..HEAD", "--", "CHANGELOG.md")
    added = [l[1:] for l in cl.splitlines() if l.startswith("+") and not l.startswith("+++")]
    print(f"Đã cập nhật mo-checklist {cur} → {version_at()}.")
    if added:
        print("\nCHANGELOG mới:\n" + "\n".join(added))
    elif log:
        print("\nCommit mới:\n" + log)
    return 0


if __name__ == "__main__":
    sys.exit(main())

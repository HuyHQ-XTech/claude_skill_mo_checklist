#!/usr/bin/env python3
"""Dò trạng thái các mục MO trong 1 hoặc nhiều repo bằng mẫu `detect` của catalog (chỉ đọc, stdlib).

  audit.py                                  # toàn bộ mục active, repo = thư mục hiện tại
  audit.py --group noti                     # 1 nhóm
  audit.py --item MO-95 --item MO-78        # vài mục, kèm bằng chứng file:line
  audit.py --item MO-95 --app a013 --app a045      # so 1 mục giữa app chuẩn và app ref
  audit.py --repo ../a036_Remote-TV_inhouse --json

Kết quả là heuristic tĩnh — mục "present/partial/unknown" phải đọc code để kết luận.
  done     : đủ mọi tín hiệu bắt buộc (`detect.all`)
  present  : có tín hiệu (`detect.any`) nhưng mục không khai tín hiệu bắt buộc → cần đọc code
  partial  : mới có một phần tín hiệu
  missing  : không thấy tín hiệu nào
  unknown  : mục không dò tĩnh được → đọc code / hỏi QC
"""
import argparse
import json
import os
import re
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = (".kt", ".java", ".xml", ".json", ".gradle", ".kts", ".toml", ".properties")
SKIP_DIRS = {"build", ".gradle", ".git", ".idea", "node_modules", ".claude", "intermediates", ".cxx",
             "generated", "baselineprofile", "mupdfmodule", "assets"}
MAX_FILE = 1_500_000


def load_json(name):
    with open(os.path.join(SKILL_DIR, name)) as f:
        return json.load(f)


def resolve_app(code, cwd):
    apps = load_json("apps.json")
    info = apps["apps"].get(code.lower())
    if info is None:
        for k, v in apps["apps"].items():
            if code.lower() in [a.lower() for a in v.get("aliases", [])]:
                info = v
                break
    if not info or not info.get("dir"):
        sys.exit(f"Không biết repo của app '{code}' (apps.json). Truyền --repo <đường dẫn> thay thế.")
    for root in apps_roots(cwd):
        p = os.path.join(root, info["dir"])
        if os.path.isdir(p):
            return p
    hint = ""
    if info.get("remote"):
        parent = apps_roots(cwd)[-1] if apps_roots(cwd) else "<thư mục chứa các repo>"
        hint = f"\n  Clone: git clone {info['remote']} \"{os.path.join(parent, info['dir'])}\""
    sys.exit(f"Không tìm thấy thư mục {info['dir']} cho {code}. Đặt env MO_APPS_ROOT, ghi \"root\" trong "
             f"local.json của skill, hoặc truyền --repo.{hint}")


def apps_roots(cwd):
    roots = [os.environ.get("MO_APPS_ROOT")]
    try:
        roots.append(load_json("local.json").get("root"))
    except (OSError, ValueError):
        pass
    top = git(cwd, "rev-parse", "--show-toplevel")
    roots.append(os.path.dirname(top) if top else os.path.dirname(cwd))
    return [r for r in dict.fromkeys(roots) if r]


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def _norm_remote(url):
    url = (url or "").strip().lower().rstrip("/")
    url = re.sub(r"\.git$", "", url)
    url = re.sub(r"^(git@|ssh://git@|https?://)", "", url)
    return url.replace(":/", "/").replace(":", "/")


def repo_app_code(repo):
    apps = load_json("apps.json")["apps"]
    base = os.path.basename(os.path.abspath(repo))
    for code, info in apps.items():
        if info.get("dir") == base:
            return code
    remote = _norm_remote(git(repo, "remote", "get-url", "origin"))
    if remote:
        for code, info in apps.items():
            if info.get("remote") and _norm_remote(info["remote"]) == remote:
                return code
    m = re.search(r"\ba[_-]?0?(\d{2,3})\b", base, re.I)
    return f"a{int(m.group(1)):03d}" if m else None


def branch_label(repo):
    b = git(repo, "branch", "--show-current")
    if b:
        return b
    sha = git(repo, "rev-parse", "--short", "HEAD")
    return f"detached@{sha}" if sha else None


class Freshness:
    """So file chuẩn của mục với commit lúc recipe được đối chiếu (verified_commit)."""

    def __init__(self, repo, files):
        self.repo = repo
        self.paths = [rel for rel, _ in files]
        self.cache = {}

    def resolve(self, entry):
        entry = entry.strip().lstrip("./")
        if entry in self.paths:
            return entry
        hits = [p for p in self.paths if p.endswith("/" + entry) or p.endswith(entry)]
        return hits[0] if len(hits) == 1 else (hits[0] if hits else None)

    def changed(self, commit):
        if commit not in self.cache:
            if git(self.repo, "cat-file", "-e", f"{commit}^{{commit}}") is None:
                self.cache[commit] = None
            else:
                out = git(self.repo, "diff", "--name-only", commit) or ""
                self.cache[commit] = set(out.splitlines())
        return self.cache[commit]

    def check(self, it):
        can = it.get("canonical") or {}
        commit = can.get("verified_commit")
        if not commit or not can.get("files"):
            return None
        changed = self.changed(commit)
        if changed is None:
            return f"không có commit {commit} trong repo này — không kiểm được độ mới của recipe"
        moved, edited = [], []
        for f in can["files"]:
            rel = self.resolve(f)
            if rel is None:
                moved.append(f)
            elif rel in changed:
                edited.append(rel.rsplit("/", 1)[-1])
        notes = []
        if edited:
            notes.append(f"file chuẩn đã đổi từ {commit}: {', '.join(edited)}")
        if moved:
            notes.append(f"không còn thấy (đổi tên/xoá?): {', '.join(moved)} — tìm theo symbol/detect")
        return ("↺ " + "; ".join(notes) + " → đọc code hiện tại, recipe có thể lệch") if notes else None


def load_repo(repo):
    files = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for n in names:
            if not n.endswith(EXTS):
                continue
            p = os.path.join(root, n)
            try:
                if os.path.getsize(p) > MAX_FILE:
                    continue
                with open(p, encoding="utf-8", errors="ignore") as f:
                    files.append((os.path.relpath(p, repo), f.read()))
            except OSError:
                pass
    return files


def find_hits(files, pattern, limit=3):
    rx = re.compile(pattern, re.M)
    hits = []
    for rel, text in files:
        m = rx.search(text)
        if not m:
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        line = text.splitlines()[line_no - 1].strip() if text else ""
        hits.append(f"{rel}:{line_no}: {line[:110]}")
        if len(hits) >= limit:
            break
    return hits


def key_present(files, key):
    if ":" in key:
        group, path = key.split(":", 1)
        leaf = path.split(".")[-1]
        g_needle, l_needle = f'"{group}"', f'"{leaf}"'
        if not any(g_needle in text for _, text in files):
            return False
        return any(l_needle in text or re.search(r"\b" + re.escape(leaf) + r"\b\s*[:=]", text) for _, text in files)
    needle = f'"{key}"'
    return any(needle in text for _, text in files)


GROUPED_RC = re.compile(r'"(\w+_config)"')


def grouped_rc_keys(files):
    found = set()
    for rel, text in files:
        if rel.endswith(".kt") and ("SharedPreferenceProperty" in text or "RemoteConfig" in text or "RcGroup" in text):
            for m in GROUPED_RC.finditer(text):
                if m.group(1) not in ("ads_config",):
                    found.add(m.group(1))
    return sorted(found)


def audit_item(it, files):
    det = it.get("detect") or {}
    any_p = det.get("any") or []
    all_p = det.get("all") or []
    status_flag = it.get("status")
    if status_flag in ("blocked-policy", "deprecated"):
        return {"status": "n/a", "evidence": [], "note": status_flag}
    if not any_p and not all_p:
        return {"status": "unknown", "evidence": []}
    any_hits = []
    for p in any_p:
        any_hits += find_hits(files, p, limit=2)
    all_res = {p: find_hits(files, p, limit=1) for p in all_p}
    matched_all = [p for p, h in all_res.items() if h]
    missing_all = [p for p, h in all_res.items() if not h]
    if all_p:
        if not missing_all:
            st = "done"
        elif matched_all or any_hits:
            st = "partial"
        else:
            st = "missing"
    else:
        st = "present" if any_hits else "missing"
    evidence = (sum((all_res[p] for p in matched_all), []) + any_hits)[:4]
    keys = []
    for k in it.get("rc_keys") or []:
        if not k.get("key"):
            continue
        if key_present(files, k["key"]):
            keys.append(f"{k['key']} ✓")
            continue
        for a in k.get("aliases") or []:
            if a.get("key") and key_present(files, a["key"]):
                keys.append(f"{a['key']} (alias của {k['key']})")
                break
        else:
            keys.append(f"{k['key']} ✗")
    return {"status": st, "evidence": evidence, "missing_signals": missing_all, "rc_keys": keys}


def wanted_any(_row):
    return True


LABEL = {"done": "Đủ dấu hiệu", "present": "Có dấu hiệu", "partial": "Thiếu 1 phần", "missing": "Chưa thấy",
         "unknown": "Không dò được", "n/a": "N/A"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--app", action="append", default=[], help="mã app trong apps.json, vd a013")
    ap.add_argument("--item", action="append", default=[])
    ap.add_argument("--group", action="append", default=[])
    ap.add_argument("--all-status", action="store_true", help="kể cả candidate/deprecated/blocked")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--evidence", action="store_true", help="in bằng chứng cho mọi mục")
    a = ap.parse_args()

    cwd = os.getcwd()
    repos = [os.path.abspath(r) for r in a.repo] + [resolve_app(c, cwd) for c in a.app]
    if not repos:
        repos = [cwd]
    cat = load_json("catalog.json")
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from catalog import parse_ids
    wanted = []
    for raw in a.item:
        wanted += parse_ids(raw) or [raw.upper()]
    items = []
    for it in cat["items"]:
        if wanted and it["id"] not in wanted:
            continue
        if a.group and it["group"] not in a.group:
            continue
        if not wanted and not a.all_status and it.get("status") != "active":
            continue
        items.append(it)
    if not items:
        sys.exit("Không có mục nào khớp bộ lọc.")

    report = []
    for repo in repos:
        files = load_repo(repo)
        code = repo_app_code(repo)
        fresh = Freshness(repo, files)
        rows = []
        for it in items:
            row = {"id": it["id"], "group": it["group"], "title": it["title"], **audit_item(it, files)}
            if code and (it.get("canonical") or {}).get("app") == code:
                row["canonical"] = True
                note = fresh.check(it)
                if note:
                    row["freshness"] = note
            sheet = (it.get("sheet_status") or {}).get(code) if code else None
            if sheet is not None:
                row["sheet"] = sheet
                if sheet == 0 and row["status"] in ("done", "present"):
                    row["sheet_note"] = "sheet MO ghi 0 nhưng code có dấu hiệu → đọc code; có thể sheet cũ hoặc làm chưa đủ"
                elif sheet == 1 and row["status"] == "missing":
                    row["sheet_note"] = "sheet MO ghi 1 nhưng không dò thấy → app làm kiểu khác/tên khác, hoặc nhánh đang checkout cũ"
            rows.append(row)
        head = git(repo, "log", "-1", "--format=%h %cd", "--date=short")
        report.append({"repo": repo, "app": code, "branch": branch_label(repo), "head": head,
                       "files": len(files), "grouped_rc": grouped_rc_keys(files), "items": rows})

    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return
    show_evidence = a.evidence or bool(wanted)
    for rep in report:
        print(f"\n### {rep['repo']}  [{rep.get('app') or '?'} · nhánh {rep.get('branch') or '?'} · HEAD "
              f"{rep.get('head') or '?'}]  ({rep['files']} file nguồn)")
        print("  (heuristic tĩnh — mục nào cũng phải đọc code để kết luận; 'Đủ dấu hiệu' ≠ đã đạt nghiệm thu)")
        if rep.get("grouped_rc"):
            print("  App gom RC thành JSON nhóm: " + ", ".join(rep["grouped_rc"])
                  + " → cột RC chỉ dò key phẳng/alias nhóm đã biết; kiểm field trong JSON bằng tay")
        counts = {}
        cur_group = None
        for r in rep["items"]:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
            if r["group"] != cur_group:
                cur_group = r["group"]
                print(f"\n[{cur_group}]")
            print(f"  {r['id']:<7} {LABEL[r['status']]:<12} {r['title'][:70]}")
            if show_evidence or r["status"] in ("partial",):
                for e in r.get("evidence") or []:
                    print(f"           ↳ {e}")
                for m in r.get("missing_signals") or []:
                    print(f"           ✗ thiếu tín hiệu: {m}")
            if r.get("rc_keys") and (show_evidence or r["status"] in ("partial", "present", "done")):
                print("           RC: " + ", ".join(r["rc_keys"]))
            if r.get("freshness"):
                print("           " + r["freshness"])
            if r.get("sheet_note") and (show_evidence or wanted_any(r)):
                print("           ⚑ " + r["sheet_note"])
        print("\nTổng: " + ", ".join(f"{LABEL[k]} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()

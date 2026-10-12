#!/usr/bin/env python3
"""Tra cứu & bảo trì catalog MO checklist (chỉ dùng stdlib).

  catalog.py find "<yêu cầu tự do | MO-82 | MO checklist 88 + 90 | 82>"
  catalog.py show MO-95 [--json]
  catalog.py list [nhóm] [--status active|candidate|deprecated|blocked-policy]
  catalog.py render                      # sinh CATALOG.md
  catalog.py check                       # kiểm tra catalog + anchor recipe
  catalog.py merge <staging.json>...     # (bảo trì) gộp dữ liệu bổ sung vào catalog.json
"""
import argparse
import json
import os
import re
import sys
import unicodedata

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(SKILL_DIR, "catalog.json")

ENRICH_FIELDS = ("title", "aliases", "requirement", "acceptance", "sdk", "canonical", "rc_keys",
                 "events", "placements", "depends_on", "detect", "recipe", "qc", "notes")
GROUP_TITLES = {
    "setup": "Setup SDK / ID / tracking",
    "splash": "Splash",
    "language": "Language (First open)",
    "select": "Select (First open)",
    "onboard": "Onboarding (First open)",
    "noti": "Notification",
    "reopen": "Re-open / retention (uninstall, widget, open-with)",
    "ads": "Ads trong app",
    "rating": "Rating",
    "ux": "UX: quyền, webview, force update",
}
STOPWORDS = {"lam", "thuc", "hien", "cho", "app", "mo", "checklist", "task", "giup", "toi", "minh",
             "the", "and", "a", "of", "to", "in", "on", "cai", "nay", "voi", "va", "la", "co", "khong",
             "theo", "ref", "implement", "add", "them", "bo", "sung", "man", "screen"}


def load():
    with open(CATALOG) as f:
        return json.load(f)


def save(cat):
    with open(CATALOG, "w") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)
        f.write("\n")


def norm(text):
    text = (text or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


ID_LIST = r"\d{1,3}(?:\s*(?:\+|,|&|/|và|and)\s*(?:mo\s*[-_ ]?\s*)?\d{1,3})*"
MO_ID_RE = re.compile(r"(?<![a-z0-9])(?:checklist\s+)?mo\s*(?:[-_#:]\s*|\s+checklist\s+|\s*)(" + ID_LIST + r")(?![\d.])",
                      re.I)
CHECKLIST_ID_RE = re.compile(r"(?<![a-z0-9])checklist\s+(" + ID_LIST + r")(?![\d.])", re.I)
OTHER_ID_RE = re.compile(r"(?<![a-z0-9])(dev|cc)\s*[-_ ]\s*(\d{1,3})(?![\d.])", re.I)


def parse_ids(text):
    raw = (text or "").strip()
    if re.fullmatch(r"#?\d{1,3}", raw):
        return [f"MO-{int(raw.lstrip('#'))}"]
    ids = []
    for rx in (MO_ID_RE, CHECKLIST_ID_RE):
        for m in rx.finditer(raw):
            for n in re.findall(r"\d{1,3}", m.group(1)):
                ids.append(f"MO-{int(n)}")
    for m in OTHER_ID_RE.finditer(raw):
        ids.append(f"{m.group(1).upper()}-{int(m.group(2))}")
    return list(dict.fromkeys(ids))


def by_id(cat):
    out = {}
    for it in cat["items"]:
        out[it["id"]] = it
        for old in it.get("old_ids") or []:
            out.setdefault(old, it)
    return out


def item_texts(it):
    aliases = list(dict.fromkeys(norm(a) for a in it.get("aliases") or [] if norm(a)))
    title = norm(it.get("title"))
    st = it.get("sheet_text") or {}
    sheet = norm(" ".join(str(v) for v in st.values() if v))
    req = norm(it.get("requirement"))
    return aliases, title, sheet, req


_IDF = {}


def idf(cat):
    if not _IDF:
        import math
        df = {}
        for it in cat["items"]:
            aliases, title, _sheet, _req = item_texts(it)
            for tok in set(" ".join(aliases + [title]).split()):
                df[tok] = df.get(tok, 0) + 1
        n = len(cat["items"])
        for tok, d in df.items():
            _IDF[tok] = 1 + math.log(n / (1 + d))
        _IDF["__default__"] = 1 + math.log(n)
    return _IDF


def score_item(query_norm, tokens, it, w):
    aliases, title, sheet, req = item_texts(it)
    score = 0.0
    padded = f" {query_norm} "
    compact_q = query_norm.replace(" ", "")
    qset = set(query_norm.split())
    seen_sets = set()
    for a in aliases:
        toks = a.split()
        key = frozenset(toks)
        if key in seen_sets:
            continue
        seen_sets.add(key)
        phrase_w = sum(w.get(t, w["__default__"]) for t in toks)
        if f" {a} " in padded:
            score += 3 + phrase_w
        elif len(toks) >= 2 and set(toks) <= qset:
            score += 2 + 0.8 * phrase_w
        elif len(a.replace(" ", "")) >= 6 and a.replace(" ", "") in compact_q:
            score += 5
    if title and title in query_norm:
        score += 6
    elif title and len(title) <= 40 and len(title.replace(" ", "")) >= 6 and title.replace(" ", "") in compact_q:
        score += 5
    title_compact = title.replace(" ", "")
    alias_tokens = set(" ".join(aliases).split())
    title_tokens = set(title.split())
    req_tokens = set(req.split())
    sheet_tokens = set(sheet.split())
    for tok in tokens:
        tw = w.get(tok, w["__default__"])
        if tok in alias_tokens:
            score += 1.2 * tw
        if tok in title_tokens:
            score += 1.0 * tw
        elif len(tok) >= 5 and tok in title_compact:
            score += 0.8 * tw
        if tok in req_tokens:
            score += 0.3 * tw
        if tok in sheet_tokens:
            score += 0.2 * tw
    if it.get("status") in ("deprecated",):
        score *= 0.6
    if it.get("duplicate_of"):
        score *= 0.8
    return score


def find(cat, query, limit=6):
    index = by_id(cat)
    ids = parse_ids(query)
    if ids:
        hits = []
        for i in ids:
            it = index.get(i)
            hits.append({"id": i, "found": bool(it), "item": it})
        return {"mode": "id", "results": hits}
    qn = norm(query)
    tokens = [t for t in qn.split() if t not in STOPWORDS and len(t) > 1]
    scored = []
    w = idf(cat)
    for it in cat["items"]:
        s = score_item(qn, tokens, it, w)
        if s > 0:
            scored.append((s, it))
    scored.sort(key=lambda x: -x[0])
    top = scored[:limit]
    rivals = [sc for sc, it in top[1:] if it.get("duplicate_of") != top[0][1]["id"]] if top else []
    confident = bool(top) and top[0][0] >= 6.0 and (not rivals or top[0][0] >= rivals[0] * 1.4)
    return {"mode": "text", "confident": confident,
            "results": [{"id": it["id"], "score": round(s, 1), "item": it} for s, it in top]}


def fmt_line(it):
    flag = "" if it.get("status") == "active" else f" [{it.get('status')}]"
    return f"{it['id']:<7} {it.get('group', ''):<9} {it.get('title', '')}{flag}"


def cmd_find(cat, args):
    res = find(cat, " ".join(args.query))
    if args.json:
        slim = {"mode": res["mode"], "confident": res.get("confident"),
                "results": [{k: v for k, v in r.items() if k != "item"} |
                            ({"title": r["item"]["title"], "group": r["item"]["group"],
                              "status": r["item"]["status"]} if r.get("item") else {})
                            for r in res["results"]]}
        print(json.dumps(slim, ensure_ascii=False, indent=1))
        return
    if res["mode"] == "id":
        for r in res["results"]:
            if r["found"]:
                print(fmt_line(r["item"]))
                if r["item"]["id"] != r["id"]:
                    print(f"        (ID cũ {r['id']} → nay là {r['item']['id']})")
            else:
                print(f"{r['id']:<7} KHÔNG có trong catalog (snapshot {cat['meta']['snapshot']})")
        print("\n→ Khớp theo ID. Luôn in tên mục cho user; nếu mô tả của user lệch tên mục thì hỏi lại.")
        return
    if not res["results"]:
        print("Không tìm thấy mục phù hợp. Thử từ khoá khác hoặc `catalog.py list <nhóm>`.")
        return
    for r in res["results"]:
        print(f"{r['score']:>5}  {fmt_line(r['item'])}")
    print("\n→ " + ("Khớp rõ: dùng mục đầu tiên." if res["confident"]
                    else "Chưa chắc: hỏi user chọn 1 trong các mục trên."))


def cmd_show(cat, args):
    index = by_id(cat)
    for raw in args.ids:
        ids = parse_ids(raw) or [raw.upper()]
        for i in ids:
            it = index.get(i)
            if not it:
                print(f"{i}: không có trong catalog")
                continue
            if args.json:
                print(json.dumps(it, ensure_ascii=False, indent=1))
                continue
            print(f"# {it['id']} — {it['title']}  [{it['group']} / {it['status']}]")
            for key in ("requirement", "blocked_reason", "deprecated_reason", "duplicate_of", "notes"):
                if it.get(key):
                    print(f"{key}: {it[key]}")
            for label, key in (("Nghiệm thu", "acceptance"), ("QC", "qc")):
                if it.get(key):
                    print(f"{label}:")
                    for a in it[key]:
                        print(f"  - {a}")
            if any("$P" in q or "$S" in q for q in it.get("qc") or []):
                print("  ($P = applicationId, $S = \"adb -s <serial> shell\" — xem references/qc.md)")
            sdk = it.get("sdk") or {}
            if sdk:
                print(f"SDK: {sdk.get('available')} {sdk.get('api') or ''} {sdk.get('min_version') or ''} "
                      f"{sdk.get('note') or ''}".rstrip())
            can = it.get("canonical") or {}
            if can.get("files") or can.get("symbols"):
                print(f"Chuẩn {can.get('app')} (đọc code BẢN HIỆN TẠI; recipe đối chiếu lần cuối @"
                      f"{can.get('verified_commit')}):")
                if can.get("files"):
                    print("  file: " + ", ".join(can["files"]))
                if can.get("symbols"):
                    print("  symbol: " + ", ".join(can["symbols"]))
                if can.get("note"):
                    print(f"  note: {can['note']}")
            for k in it.get("rc_keys") or []:
                al = ", ".join(f"{a.get('key')}({'/'.join(a.get('apps') or [])})" for a in k.get("aliases") or [])
                print(f"RC {k.get('key')} : {k.get('type')} = {k.get('default')} — {k.get('meaning', '')}"
                      + (f" | alias: {al}" if al else ""))
            for p in it.get("placements") or []:
                print(f"Placement {p.get('name')} ({p.get('format')})")
            for e in it.get("events") or []:
                print(f"Event {e.get('name')} {e.get('params') or ''}")
            if it.get("depends_on"):
                print("Phụ thuộc: " + ", ".join(it["depends_on"]))
            if it.get("figma"):
                print("Figma: " + " ".join(it["figma"]))
            if it.get("docs"):
                print("Docs: " + " ".join(it["docs"]))
            if it.get("images"):
                print("Ảnh: " + " ".join(it["images"]))
            ss = it.get("sheet_status") or {}
            if ss:
                done = [a for a, v in ss.items() if v == 1]
                todo = [a for a, v in ss.items() if v == 0]
                print(f"Sheet MO (snapshot {cat['meta']['snapshot']}): đã làm {', '.join(done) or '-'} · "
                      f"chưa {', '.join(todo) or '-'}")
            est = it.get("est") or {}
            if est.get("dev_h") or est.get("qc_h"):
                print(f"Est: dev {est.get('dev_h')}h, QC {est.get('qc_h')}h {est.get('qc_note') or ''}".rstrip())
            if it.get("recipe"):
                print(f"Recipe: {it['recipe']}")
            print()


def cmd_list(cat, args):
    for it in cat["items"]:
        if args.group and it["group"] != args.group:
            continue
        if args.status and it.get("status") != args.status:
            continue
        print(fmt_line(it))


def md_escape(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def cmd_render(cat, _args):
    meta = cat["meta"]
    lines = [
        "# MO checklist — bảng tra cứu",
        "",
        f"Sinh tự động từ `catalog.json` bằng `scripts/catalog.py render` — **không sửa tay**. Snapshot sheet "
        f"\"{meta['master_sheet']}\" ngày {meta['snapshot']}. ID = `MO-<số dòng trong sheet>`; `DEV-<dòng>` = "
        "sheet \"Checklist - Dev\"; `CC-<dòng>` = sheet \"Crawl Competitor\" (ứng viên).",
        "",
        "Trạng thái: `active` = đang áp dụng · `candidate` = MO đang cân nhắc · `deprecated` = đã bỏ · "
        "`blocked-policy` = không làm vì vi phạm chính sách Play.",
        "",
    ]
    for g in meta["groups"]:
        items = [it for it in cat["items"] if it["group"] == g]
        if not items:
            continue
        lines += [f"## {GROUP_TITLES.get(g, g)}", "", "| ID | Mục | SDK | Chuẩn | Trạng thái |", "|---|---|---|---|---|"]
        for it in items:
            sdk = (it.get("sdk") or {}).get("available")
            sdk_s = {True: "có", False: "không", "partial": "một phần"}.get(sdk, "?")
            can = it.get("canonical") or {}
            lines.append(f"| {it['id']} | {md_escape(it['title'])} | {sdk_s} | {can.get('app', '')} | "
                         f"{it.get('status')} |")
        lines.append("")
    rows = []
    for it in cat["items"]:
        for k in it.get("rc_keys") or []:
            al = "; ".join(f"`{a.get('key')}` ({', '.join(a.get('apps') or [])}"
                           + (f" — {a['note']}" if a.get("note") else "") + ")"
                           for a in k.get("aliases") or [])
            rows.append((k.get("key") or "", it["id"], k.get("type") or "", str(k.get("default")), al))
    if rows:
        lines += ["## Key Remote Config chuẩn & alias đã gặp ở các app", "",
                  "Thứ tự chọn tên key khi code: tên user/ticket đưa → tên app đang có (dò theo alias) → tên chuẩn "
                  "dưới đây. Xem `references/conventions.md`.", "",
                  "| Key chuẩn | Mục | Kiểu | Default | Alias ở app khác |", "|---|---|---|---|---|"]
        seen = set()
        for key, iid, typ, default, al in sorted(rows):
            if (key, iid) in seen:
                continue
            seen.add((key, iid))
            lines.append(f"| `{md_escape(key)}` | {iid} | {md_escape(typ)} | {md_escape(default)} | {md_escape(al)} |")
        lines.append("")
    with open(os.path.join(SKILL_DIR, "CATALOG.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"Đã ghi CATALOG.md ({len(cat['items'])} mục, {len(rows)} key RC)")


def cmd_check(cat, _args):
    errors, warns = [], []
    ids = {it["id"] for it in cat["items"]}
    ref_cache = {}
    for it in cat["items"]:
        iid = it["id"]
        for f in ("title", "group", "status"):
            if not it.get(f):
                errors.append(f"{iid}: thiếu {f}")
        if it.get("status") == "active" and not it.get("requirement"):
            warns.append(f"{iid}: chưa có requirement")
        for dep in it.get("depends_on") or []:
            if dep not in ids:
                errors.append(f"{iid}: depends_on {dep} không tồn tại")
        det = it.get("detect") or {}
        for rx in (det.get("any") or []) + (det.get("all") or []):
            try:
                re.compile(rx)
            except re.error as e:
                errors.append(f"{iid}: regex lỗi {rx!r}: {e}")
        recipe = it.get("recipe") or ""
        if it.get("status") == "active" and not recipe:
            warns.append(f"{iid}: chưa có recipe")
        if recipe:
            path = recipe.split("§")[0].strip()
            full = os.path.join(SKILL_DIR, path)
            if not os.path.exists(full):
                errors.append(f"{iid}: recipe {path} không tồn tại")
            else:
                if full not in ref_cache:
                    with open(full) as fh:
                        ref_cache[full] = fh.read()
                if not re.search(r"^##\s+" + re.escape(iid) + r"\b", ref_cache[full], re.M):
                    errors.append(f"{iid}: không thấy heading '## {iid}' trong {path}")
        for img in it.get("images") or []:
            if not os.path.exists(os.path.join(SKILL_DIR, img)):
                errors.append(f"{iid}: ảnh {img} không tồn tại")
    ref_dir = os.path.join(SKILL_DIR, "references")
    for fn in sorted(os.listdir(ref_dir)):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(ref_dir, fn)) as fh:
            text = fh.read()
        fences = re.findall(r"^```\s*(kotlin|kt|java|xml|groovy|gradle|json)\b", text, re.M | re.I)
        if fences:
            errors.append(f"references/{fn}: có {len(fences)} code block ({', '.join(sorted(set(fences)))}) — "
                          "skill không chứa code, hãy mô tả bằng lời + chỉ file/symbol")
        line_refs = re.findall(r"\b[\w/.-]+\.(?:kt|java|xml|kts):\d+", text)
        if line_refs:
            warns.append(f"references/{fn}: {len(line_refs)} chỗ ghi số dòng (vd {line_refs[0]}) — dễ lỗi thời, "
                         "nên chỉ tên symbol")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(cat['items'])} mục · {len(errors)} lỗi · {len(warns)} cảnh báo")
    sys.exit(1 if errors else 0)


def cmd_merge(cat, args):
    index = {it["id"]: it for it in cat["items"]}
    total = 0
    for path in args.files:
        with open(path) as f:
            data = json.load(f)
        for iid, patch in data.items():
            it = index.get(iid)
            if not it:
                print(f"BỎ QUA {iid} ({os.path.basename(path)}): không có trong catalog")
                continue
            for key, value in patch.items():
                if key not in ENRICH_FIELDS:
                    print(f"BỎ QUA field lạ {iid}.{key}")
                    continue
                if key == "canonical" and isinstance(value, dict):
                    value = dict(value)
                    if "commit" in value:
                        value["verified_commit"] = value.pop("commit")
                    merged = dict(it.get("canonical") or {})
                    merged.update({k: v for k, v in value.items() if v not in (None, "")})
                    it["canonical"] = merged
                elif key == "title" and not value:
                    continue
                else:
                    it[key] = value
            total += 1
    save(cat)
    print(f"Đã gộp {total} mục vào catalog.json")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("query", nargs="+")
    f.add_argument("--json", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("ids", nargs="+")
    s.add_argument("--json", action="store_true")
    ls = sub.add_parser("list")
    ls.add_argument("group", nargs="?")
    ls.add_argument("--status")
    sub.add_parser("render")
    sub.add_parser("check")
    m = sub.add_parser("merge")
    m.add_argument("files", nargs="+")
    args = p.parse_args()
    cat = load()
    {"find": cmd_find, "show": cmd_show, "list": cmd_list, "render": cmd_render, "check": cmd_check,
     "merge": cmd_merge}[args.cmd](cat, args)


if __name__ == "__main__":
    main()

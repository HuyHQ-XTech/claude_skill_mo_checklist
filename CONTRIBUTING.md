# Đóng góp cho skill mo-checklist

Ai dùng skill cũng có thể góp ý hoặc sửa: thêm bẫy mới gặp, sửa recipe sai so với code A013, thêm alias key
RC của app mình… Mọi thay đổi vào nhánh `main` đều đi qua **Pull Request** và được người bảo trì review.
Merge xong, mọi người nhận bản mới bằng `/mo-checklist update`.

---

## Cách 1 — Chỉ góp ý / báo lỗi (không cần sửa file)

Mở **Issue** trên GitHub (tab *Issues → New issue*), hoặc nhắn người bảo trì. Ghi rõ:
- mục nào (`MO-xx`) và đang dùng ở app nào, phiên bản skill mấy (`/mo-checklist update` in ra);
- skill nói gì, thực tế code / hành vi là gì;
- đề xuất sửa (nếu có).

---

## Cách 2 — Tự sửa và mở Pull Request

**Cần:** là collaborator của repo (nhờ người bảo trì thêm). Đã cài skill theo `README.md`.

Làm **ngay trong thư mục skill** `~/.claude/skills/mo-checklist`, trên một nhánh riêng. Như vậy Claude Code
dùng luôn bản đang sửa để bạn thử. Lúc ở nhánh riêng, skill tự bỏ qua nhắc cập nhật.

### Bước 1 — Tạo nhánh từ `main` mới nhất

```bash
cd ~/.claude/skills/mo-checklist
git checkout main && git pull --ff-only
git checkout -b <tên-bạn>/<việc>          # vd: thi/mo-72-shortcut-noti
```

### Bước 2 — Sửa

| Muốn sửa | Sửa ở đâu |
|---|---|
| Cách làm, bẫy, QC của 1 mục | `references/<nhóm>.md`, section `## MO-xx` (bảng nhóm → file ở cuối `SKILL.md`) |
| Tên, nghiệm thu, key RC, alias, mẫu dò của 1 mục | `catalog.json` (mục có `"id": "MO-xx"`) |
| Câu hỏi MO/PO chưa chốt, mặc định | `references/open-questions.md` |
| Quy trình / luật chung | `SKILL.md`, `references/conventions.md` |
| Script | `scripts/*.py` (chỉ dùng thư viện chuẩn Python) |

Có thể nhờ Claude sửa giúp, vd: *"cập nhật recipe MO-72 trong skill mo-checklist: …"*.

### Bước 3 — Thử

- Mở Claude Code ở một app, tốt nhất là **git worktree tạm** để khỏi lẫn với code thật.
- Chạy lệnh liên quan, vd `/mo-checklist MO-72` hoặc `/mo-checklist audit`.
- Ghi lại đã thử trên app nào để điền vào PR.

### Bước 4 — Tăng phiên bản + CHANGELOG

1. Dòng `Phiên bản **x.y.z**` trong `SKILL.md`:
   - **patch** (1.2.**1**): sửa lời recipe, thêm alias/bẫy, sửa lỗi script;
   - **minor** (1.**3**.0): thêm mục, thêm tính năng script;
   - **major** (**2**.0.0): đổi luật hoặc quy trình.
2. Thêm mục mới **lên đầu** `CHANGELOG.md`, ví dụ:
   ```markdown
   ## 1.2.1 — 2026-10-20

   - MO-72: thêm bẫy noti shortcut bị mất khi chưa có quyền noti (a039).
   ```
   Dev sẽ đọc đúng đoạn này khi update, nên viết cho họ hiểu.

Chỉ sửa `README.md` / `CONTRIBUTING.md` thì không cần tăng phiên bản.

### Bước 5 — Kiểm tra

```bash
python3 scripts/catalog.py render     # sinh lại CATALOG.md nếu đã sửa catalog.json
python3 scripts/ci_check.py           # phải ra ✅ CI đạt
```

`ci_check.py` cũng chạy tự động trên GitHub (job **check**) cho mọi PR.

### Bước 6 — Commit, push, mở PR

```bash
git add -A
git commit -m "MO-72: <tóm tắt>"
git push -u origin <tên-bạn>/<việc>
```

Lên GitHub bấm **Compare & pull request**, điền mẫu PR có sẵn. Người bảo trì được tự động gán review.

### Bước 7 — Sau khi PR được merge

```bash
git checkout main && git pull --ff-only
git branch -d <tên-bạn>/<việc>
```

Nếu PR khác merge trước làm trùng số phiên bản: `git pull --rebase origin main`, tăng tiếp phiên bản +
đổi heading CHANGELOG, rồi push lại.

---

## Luật nội dung (bắt buộc)

1. **Không chép code app vào skill.**
   - Không có code block Kotlin/Java/XML trong `references/`; CI chặn.
   - Mô tả cơ chế, điều kiện, thứ tự, bẫy, QC bằng lời. Trỏ tới **đường dẫn file + tên class/hàm** của app ref.
   - Lý do: code app còn thay đổi, bản chép sẽ lỗi thời.
2. **Đối chiếu với code A013 (hoặc app ref) bản hiện tại.**
   - Đã đối chiếu lại thì cập nhật `canonical.verified_commit` của mục.
   - Ghi số dòng code dễ lỗi thời, nên dùng tên symbol.
3. **Không secret / ID thật:** ad unit, AdMob app ID, AppsFlyer key, token, file `.figma-token`… CI chặn
   `ca-app-pub-…` thật.
4. **ID mục = số dòng sheet "Checklist - MO New"**, không tự đổi.
   - Tactic MO đã làm theo ticket nhưng chưa có dòng trong sheet: thêm mục `EXT-<TÊN>` (chữ hoa, gạch nối; `sheet` = "",
     `row` = 0), không đặt MO-ID. Bắt buộc có `aliases` đủ cách user hay gọi để `catalog.py find` nhận ra qua prompt, và
     section `## EXT-<TÊN>` trong file recipe của nhóm.
   - Khi MO thêm tactic đó vào sheet: người bảo trì đổi ID sang `MO-<dòng>` và giữ `EXT-<TÊN>` trong `old_ids`,
     gộp dữ liệu sheet vào mục, đổi heading recipe theo (`SKILL.md` § update-catalog bước 3).
   - Thêm mục / đổi số dòng theo sheet mới là việc của người bảo trì (`scripts/sheet_diff.py`), để 2 người
     không cùng đổi ID.
5. **Khuôn section recipe:** `## MO-xx — <tên>` gồm Yêu cầu · Nghiệm thu · SDK · Chuẩn A013 · Remote config ·
   Placement/tracking · Cách làm · Bẫy · QC. Viết tiếng Việt; tên code giữ nguyên tiếng Anh. Mục EXT: heading
   `## EXT-<TÊN> — <tên>`, phần Chuẩn ghi app ref của ticket (`canonical.app`).
6. **Tên key RC mới:** theo thứ tự trong `references/conventions.md` §1. Key cũ của app nào thì thêm vào
   `aliases`, đừng đổi tên chuẩn.

---

## Người bảo trì

- Review PR, merge khi CI xanh.
- Phát hành khi MO gửi sheet mới (README §8).
- Thêm collaborator mới: *Settings → Collaborators → Add people*.

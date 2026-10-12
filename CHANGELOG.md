# CHANGELOG — skill mo-checklist

## 1.1.0 — 2026-10-12

- **Phân phối qua git:** dev clone vào `~/.claude/skills/mo-checklist`, gõ `/mo-checklist update` để kéo bản
  mới (`scripts/update.py`). Mỗi lần chạy, skill tự kiểm và nhắc khi có bản mới.
- **`apps.json` không còn đường dẫn riêng của máy.** Thư mục chứa các repo app được tìm theo thứ tự: env
  `MO_APPS_ROOT` → `local.json` (riêng từng máy, không commit) → thư mục cha của repo đang mở.
- **`audit.py --app`** in sẵn lệnh `git clone` khi máy chưa có repo app ref.
- Thêm `README.md`: cài đặt, cập nhật, quy trình phát hành.

## 1.0.0 — 2026-10-08

Bản đầu tiên. Catalog lấy từ snapshot sheet "Checklist - MO New" ngày 2026-10-07; recipe đối chiếu với
A013 `f784827` (v1.2.7).

**Nội dung**
- 113 mục: MO-2..MO-100, DEV-x, CC-x. ID = số dòng trong sheet.
- `references/` cho 10 nhóm.
- Câu hỏi MO/PO chưa chốt: `references/open-questions.md`.

**Script**
- `catalog.py`: find/show/list/render/check/merge.
- `detect_stack.py`: stack, JDK gợi ý, lệnh verify.
- `audit.py`: dò mục; so app chuẩn/app ref; cảnh báo `↺` khi code A013 đổi so với lần đối chiếu.
- `sheet_diff.py`: đồng bộ khi MO sửa sheet.

**Đã thử end-to-end (MO-95 noti lock screen)**
- a036: app không dùng SDK, chưa có mục này.
- a037: app đã có, JSON RC nhóm.
- A028 với `ref a045`.

**Sửa sau lần thử**
- Recipe MO-95:
  - thêm phần tối thiểu để Done;
  - thêm `screenSkipAdResume`;
  - tạo channel trước mỗi lần notify;
  - `TIME_SET` chỉ khi có cửa sổ ân hạn;
  - sửa các fact về họ A045.
- `audit.py`:
  - nhận app trong worktree, ghi rõ detached;
  - đổi nhãn kết quả thành heuristic;
  - cảnh báo khi lệch với sheet;
  - dò được key RC trong JSON nhóm.
- `detect_stack.py`: gợi ý JDK; bỏ upload Crashlytics khi build release.
- Luật:
  - ref ≠ A013 thì theo ref, kèm bảng khác biệt;
  - luật của repo ưu tiên hơn skill;
  - hỏi trước khi đổi hành vi đã phát hành.

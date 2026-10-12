# mo-checklist — Claude Code skill làm MO checklist cho app Android xTech

Skill giúp mọi app làm MO checklist theo **một cách chuẩn chung**:
- catalog ~113 mục, ID = số dòng sheet "Checklist - MO New";
- recipe từng mục;
- app ref mặc định là A013;
- audit app còn thiếu mục nào.

Hướng dẫn đầy đủ cho Claude nằm ở `SKILL.md`.

## Cài (mỗi dev làm 1 lần)

Cần: Claude Code, `git`, `python3`, quyền đọc repo trong org GitHub `xTech-Android`.

1. Clone skill vào đúng chỗ Claude Code tìm skill:
   ```bash
   git clone <REPO_URL> ~/.claude/skills/mo-checklist
   ```
2. Clone **A013** nằm cạnh các repo app đang làm. Skill đọc code chuẩn bản hiện tại từ đây.
   ```bash
   cd <thư mục chứa các repo app>
   git clone git@github.com:xTech-Android/A013_Recovery_Asclepius.git
   ```
   - Repo app nằm rải rác thì khai thư mục chứa chúng trong `~/.claude/skills/mo-checklist/local.json`, vd
     `{"root": "/Users/<bạn>/Documents/project/xtech"}`. File này riêng từng máy, không commit.
   - Hoặc đặt env `MO_APPS_ROOT`.
3. Mở lại Claude Code → gõ `/mo-checklist` để kiểm skill đã nhận.

## Dùng

```
/mo-checklist thực hiện MO checklist noti lockscreen
/mo-checklist MO-95                 # hoặc "MO checklist 95", "MO checklist 88 + 90"
/mo-checklist MO-95 ref a045        # làm theo app khác + bảng khác biệt với A013
/mo-checklist audit                 # app hiện tại có/thiếu mục nào
/mo-checklist explain MO-78
/mo-checklist update                # kéo bản skill mới nhất
```

## Cập nhật

- `/mo-checklist update`, hoặc `git -C ~/.claude/skills/mo-checklist pull --ff-only`.
- Mỗi lần chạy, skill tự kiểm và nhắc khi có bản mới.
- **Đừng sửa file trong skill trên máy mình.** Có sửa đổi local thì update sẽ dừng để khỏi mất dữ liệu.
  Muốn góp ý/sửa thì gửi người bảo trì, hoặc mở PR.

## Bảo trì (người phát hành)

1. Sửa recipe / catalog / script trong repo này. **Không chép code app vào skill**: chỉ mô tả cơ chế, bẫy,
   QC và trỏ file + symbol (xem `SKILL.md` luật 8).
2. MO gửi sheet mới thì chạy `python3 scripts/sheet_diff.py "<file.xlsx>"` (xem `SKILL.md` § update-catalog).
3. Kiểm và sinh bảng tra:
   ```bash
   python3 scripts/catalog.py check && python3 scripts/catalog.py render
   ```
4. Tăng phiên bản ở dòng `Phiên bản **x.y.z**` trong `SKILL.md`, rồi thêm mục mới **lên đầu** `CHANGELOG.md`.
   Mục này là thứ dev thấy khi update.
   - patch: sửa lời recipe, sửa lỗi script;
   - minor: thêm mục, thêm tính năng script;
   - major: đổi luật/quy trình.
5. Commit + push lên nhánh `main`. Dev nhận bản mới ở lần `/mo-checklist update` kế tiếp.

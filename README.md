# MO Checklist — Claude Code skill cho app Android xTech

Skill cho **Claude Code** giúp các app Android của xTech làm **MO checklist** (tactic Monetization) theo **một
cách chuẩn chung**. Không còn cảnh mỗi app tự làm một kiểu, mỗi ticket "Ref" một app khác.

- App chuẩn (ref) mặc định: **A013**.
- Mỗi mục MO có ID = **số dòng trong sheet "Checklist - MO New"**, ví dụ `MO-95` = dòng 95.
- Phiên bản và lịch sử thay đổi: [`CHANGELOG.md`](CHANGELOG.md).

---

## Mục lục

1. [Skill làm được gì](#1-skill-làm-được-gì)
2. [Yêu cầu](#2-yêu-cầu)
3. [Cài đặt (làm 1 lần)](#3-cài-đặt-làm-1-lần)
4. [Cách dùng](#4-cách-dùng)
5. [Cập nhật skill](#5-cập-nhật-skill)
6. [Xử lý sự cố](#6-xử-lý-sự-cố)
7. [Cấu trúc thư mục](#7-cấu-trúc-thư-mục)
8. [Dành cho người bảo trì](#8-dành-cho-người-bảo-trì)

---

## 1. Skill làm được gì

| Việc | Ví dụ lệnh |
|---|---|
| **Làm 1 mục MO** trong app đang mở: tìm mục, đọc code chuẩn A013 (bản hiện tại), code theo convention của app, build kiểm tra, báo cáo | `/mo-checklist thực hiện MO checklist noti lockscreen` |
| Làm theo **app ref khác** (khi ticket ghi "Ref aXXX") và **so khác biệt với A013** | `/mo-checklist MO-95 ref a045` |
| **Audit**: app hiện tại đã có / còn thiếu mục MO nào | `/mo-checklist audit` |
| **Giải thích** một mục cho PO/QC (user thấy gì, RC nào điều khiển, QC test thế nào) | `/mo-checklist explain MO-78` |
| **Cập nhật** skill lên bản mới nhất | `/mo-checklist update` |

Skill **không bao giờ commit/push** code app. Code xong để nguyên trong working tree cho dev review.

---

## 2. Yêu cầu

- **Claude Code**: CLI, app desktop, hoặc extension IDE.
- **`git`** và **`python3`** (macOS có sẵn). Script của skill chỉ dùng thư viện chuẩn của Python.
- **Quyền đọc** các repo:
  - repo skill này (`HuyHQ-XTech/claude_skill_mo_checklist`). Repo private thì nhờ người bảo trì (HuyHQ)
    thêm bạn làm collaborator;
  - repo app chuẩn **A013**: `xTech-Android/A013_Recovery_Asclepius`;
  - repo app bạn đang làm.

---

## 3. Cài đặt (làm 1 lần)

### Bước 1 — Clone skill vào thư mục skill của Claude Code

```bash
git clone https://github.com/HuyHQ-XTech/claude_skill_mo_checklist.git ~/.claude/skills/mo-checklist
```

> ⚠️ Thư mục **phải tên là `mo-checklist`**: tên lệnh `/mo-checklist` lấy từ tên này.
> Dùng SSH: `git clone git@github.com:HuyHQ-XTech/claude_skill_mo_checklist.git ~/.claude/skills/mo-checklist`

### Bước 2 — Clone app chuẩn A013 nằm cạnh các repo app

Skill **không chứa code mẫu**. Muốn biết code chuẩn của một mục, nó đọc thẳng code **bản hiện tại** của
A013 trên máy bạn, nên máy phải có A013. Đặt A013 cùng thư mục cha với các repo app:

```
~/projects/xtech/                  ← thư mục chứa các repo app (tên tuỳ bạn)
├── A013_Recovery_Asclepius/       ← app chuẩn — BẮT BUỘC, giữ nguyên tên thư mục
├── a037_Speaker_Cleaner/          ← app bạn đang làm
└── ...
```

```bash
cd ~/projects/xtech
git clone git@github.com:xTech-Android/A013_Recovery_Asclepius.git
```

Muốn dùng app khác làm ref (vd `ref a045`) thì clone thêm app đó vào cùng chỗ. Danh sách repo + URL nằm
trong [`apps.json`](apps.json).

### Bước 3 — (Tuỳ chọn) Khai thư mục chứa các repo

Chỉ cần khi các repo app **không** nằm chung một thư mục cha. Tạo file
`~/.claude/skills/mo-checklist/local.json`:

```json
{ "root": "/Users/<tên-bạn>/projects/xtech" }
```

Hoặc đặt biến môi trường `MO_APPS_ROOT`. `local.json` là file riêng của máy bạn: không commit, update
không ghi đè.

### Bước 4 — Kiểm tra

Mở Claude Code **trong repo app** rồi gõ:

```
/mo-checklist audit
```

Thấy bảng các mục MO theo nhóm là cài xong. Có thể kiểm phiên bản bằng:

```bash
python3 ~/.claude/skills/mo-checklist/scripts/update.py --check
```

---

## 4. Cách dùng

Mở Claude Code trong repo app cần làm, rồi gõ lệnh.

### Các lệnh

| Lệnh | Ý nghĩa |
|---|---|
| `/mo-checklist thực hiện MO checklist noti lockscreen` | Làm 1 mục, gọi bằng mô tả |
| `/mo-checklist MO-95` | Làm 1 mục, gọi bằng ID. Cũng nhận `MO 95`, `MO checklist 95` |
| `/mo-checklist MO checklist 88 + 90` | Làm nhiều mục, lần lượt từng mục, báo cáo gộp |
| `/mo-checklist MO-95 ref a045` | Làm theo app a045 thay vì A013, kèm bảng khác biệt với A013 |
| `/mo-checklist P3563` (dán kèm nội dung ticket) | Làm theo ticket Product Hub |
| `/mo-checklist audit` · `/mo-checklist audit noti` | App hiện tại có/thiếu mục nào (toàn bộ, hoặc 1 nhóm) |
| `/mo-checklist explain MO-78` | Giải thích mục |
| `/mo-checklist update` | Cập nhật skill |

Danh sách đủ các mục + ID: [`CATALOG.md`](CATALOG.md).

### Khi bạn yêu cầu làm 1 mục, Claude sẽ

1. Tìm đúng mục trong catalog và **in tên mục** để bạn xác nhận. Mơ hồ thì hỏi bạn chọn.
2. Nhận diện app: SDK xtechads hay ads tự viết, Compose hay XML, lệnh build, JDK phù hợp. Đọc
   `CLAUDE.md`/`.claude/rules` của repo.
3. Mở code chuẩn ở A013 (hoặc app ref bạn chọn) **bản hiện tại**, rồi xem app đã có gì.
4. **Đã có và đúng chuẩn** → không sửa, chỉ báo. **Thiếu** → bổ sung. **Khác chuẩn ở hành vi đã phát hành** →
   **hỏi bạn trước** khi đổi.
5. Code theo convention của app; build trước và sau khi sửa.
6. Báo cáo:
   - file đã đổi;
   - **key Remote Config + default mà MO cần tạo trên Firebase**;
   - placement, event tracking;
   - bước QC;
   - `TODO(mo)` (copy/ảnh còn thiếu);
   - câu hỏi đang chờ MO chốt;
   - 1 dòng để dán vào sheet MO.

### Nguyên tắc skill luôn giữ

- **Tên key RC / placement / event:** tên bạn đưa → tên app đang dùng → tên chuẩn của app ref (mặc định
  A013). Không đổi tên key đã phát hành.
- Luật trong repo app (`CLAUDE.md`, `.claude/rules`) **ưu tiên hơn** skill.
- Không commit, không push, không đổi Remote Config trên Firebase, không ghi vào sheet MO.
- Không làm các mục vi phạm chính sách Google Play, vd MO-87 "giả cảnh báo hệ thống".

---

## 5. Cập nhật skill

Khi người bảo trì phát hành bản mới:

```
/mo-checklist update
```

hoặc chạy tay: `git -C ~/.claude/skills/mo-checklist pull --ff-only`.

- Mỗi lần dùng, Claude tự kiểm và **nhắc khi có bản mới**. Nó không tự cập nhật giữa chừng.
- Update xong sẽ in phiên bản cũ → mới và phần CHANGELOG mới.
- **Đừng sửa file trong thư mục skill trên máy mình.** Có sửa đổi local thì update dừng lại để khỏi mất.
  - Muốn góp ý/sửa: mở issue/PR trên repo, hoặc nhắn người bảo trì.
  - Lỡ sửa và muốn bỏ: `git -C ~/.claude/skills/mo-checklist stash`, rồi update lại.

---

## 6. Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Gõ `/mo-checklist` không thấy skill | Kiểm thư mục đúng là `~/.claude/skills/mo-checklist` và có file `SKILL.md`, rồi mở lại Claude Code. |
| `Không tìm thấy thư mục A013_Recovery_Asclepius` | Làm Bước 2 (clone A013 cạnh repo app), hoặc Bước 3 (`local.json`). Thông báo lỗi có in sẵn lệnh `git clone`. |
| Update báo "có sửa đổi chưa commit" | Bạn đã sửa file trong skill. Xem mục 5. |
| Update báo "không fetch được" | Kiểm mạng và quyền đọc repo skill. |
| Build fail vì JDK (`invalid source release`, Gradle không chạy) | Claude tự gợi ý `JAVA_HOME` hợp với Gradle của app (dòng `jdk_suggest`). Có thể tự chạy `python3 ~/.claude/skills/mo-checklist/scripts/detect_stack.py .` để xem. |
| Không đọc được Figma | Skill dùng figma skill/token của chính project; không có thì dùng ảnh minh hoạ trong `assets/refs/` và ghi rõ trong báo cáo. |
| Một mục đang mơ hồ, MO chưa chốt | Xem [`references/open-questions.md`](references/open-questions.md): skill làm theo cột "Mặc định" và ghi "chờ MO chốt Qx". |
| `audit` báo "Đủ dấu hiệu" nhưng QC thấy thiếu | Audit chỉ dò tĩnh (tên class/key). Dùng `/mo-checklist MO-xx` để Claude đọc code và kiểm theo nghiệm thu. |

---

## 7. Cấu trúc thư mục

```
mo-checklist/
├── SKILL.md              # hướng dẫn cho Claude (quy trình, luật) — điểm vào của skill
├── README.md             # file này (cho người)
├── CHANGELOG.md          # lịch sử phiên bản
├── CATALOG.md            # bảng tra 113 mục + key RC chuẩn (sinh tự động)
├── catalog.json          # dữ liệu gốc của các mục (spec, nghiệm thu, key RC, mẫu dò…)
├── apps.json             # mã app → tên thư mục repo + URL để clone
├── local.json            # (tuỳ chọn, riêng từng máy, không commit) thư mục chứa các repo app
├── references/           # recipe theo nhóm: setup, splash, language, select, onboarding,
│                         # notifications, reopen, inapp-ads, misc + conventions, stack-adapt,
│                         # qc, open-questions
├── scripts/
│   ├── catalog.py        # tìm / hiển thị / kiểm tra / sinh CATALOG.md
│   ├── detect_stack.py   # nhận diện stack app, lệnh build, JDK gợi ý
│   ├── audit.py          # dò mục MO đã có/thiếu, so app chuẩn với app ref
│   ├── sheet_diff.py     # (bảo trì) so sheet MO mới với catalog
│   └── update.py         # cập nhật skill
└── assets/
    ├── refs/             # ảnh minh hoạ trích từ sheet MO (MO-<dòng>-n.jpg)
    └── noti-content.md   # copy noti theo app (snapshot sheet)
```

---

## 8. Dành cho người bảo trì

### Nguyên tắc nội dung

- **Không chép code app vào skill**, vì A013 thay đổi liên tục nên code chép sẽ lỗi thời. Recipe chỉ ghi cơ
  chế, quyết định, bẫy, QC, đường dẫn file + tên symbol. `catalog.py check` báo lỗi nếu `references/` có
  code block Kotlin/Java/XML.
- App ref mặc định A013. Mỗi mục ghi `verified_commit` (commit A013 lần cuối đối chiếu). Code A013 đổi thì
  `audit.py --app a013` báo `↺` ở mục liên quan.

### Phát hành bản mới

1. Sửa nội dung (recipe, catalog, script).
2. Kiểm tra và sinh lại bảng tra:
   ```bash
   cd ~/.claude/skills/mo-checklist
   python3 scripts/catalog.py check && python3 scripts/catalog.py render
   ```
3. Tăng phiên bản ở dòng `Phiên bản **x.y.z**` trong `SKILL.md`:
   - **patch** (1.1.**1**): sửa lời recipe, sửa lỗi script;
   - **minor** (1.**2**.0): thêm mục, thêm tính năng;
   - **major** (**2**.0.0): đổi luật hoặc quy trình.
4. Thêm mục mới **lên đầu** `CHANGELOG.md`. Dev thấy đúng phần này khi update, nên viết cho họ đọc.
5. Commit và push lên `main`:
   ```bash
   git add -A && git commit -m "mo-checklist x.y.z: <tóm tắt>" && git push
   ```

### Khi MO gửi sheet checklist mới

```bash
python3 scripts/sheet_diff.py "<file.xlsx>"            # xem: mục mới / sửa chữ / đổi số dòng / bị xoá
python3 scripts/sheet_diff.py "<file.xlsx>" --apply --snapshot <YYYY-MM-DD> --images
```

Sau đó viết recipe cho các mục có `needs_review`, rồi làm tiếp các bước "Phát hành bản mới". Cần
`openpyxl` + `pillow`: `python3 -m pip install --user openpyxl pillow`.

### Khi A013 thay đổi

Chạy `python3 scripts/audit.py --app a013`. Mục nào báo `↺` thì:
1. xem `git -C <A013> diff <verified_commit> -- <file>`;
2. sửa lời recipe;
3. cập nhật `verified_commit` của mục trong `catalog.json`.

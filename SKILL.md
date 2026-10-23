---
name: mo-checklist
description: Làm / kiểm tra MO checklist (tactic Monetization) cho các app Android xTech theo MỘT cách chuẩn chung (ref mặc định A013 + SDK xtechads). Dùng khi user gõ /mo-checklist, nhắc "MO checklist", "MO tactic/tatic", "làm MO", "check MO", "MO request", gọi mục bằng ID kiểu "MO-82", "MO checklist 82", "checklist MO 88 + 90", hoặc nêu tên một tactic MO như noti lock screen, pinned/kill-app/daily/win-back/shortcut noti, uninstall shortcut, widget, open with, splash ads, language/language alt, select alt, onboard native full, toast sau click ads, inter khi back/vuốt, preload inter theo interval, loading trước inter/ads, rating, gộp RC / gộp key Remote Config vào JSON theo màn. Hỗ trợ làm 1 mục lẻ trong app đã có MO cũ, audit app còn thiếu mục nào, giải thích mục cho PO/QC, cập nhật catalog khi MO thêm mục, và tự cập nhật bản skill mới (/mo-checklist update). KHÔNG dùng để tạo app mới (init-base-project), chỉ sửa ads_config/placement (skill ads), hay xử lý bug ticket chung (product-hub).
---

# mo-checklist — làm MO checklist đồng bộ cho các app Android xTech

Phiên bản **2.2.0** (2026-10-23) — thay đổi ghi ở `CHANGELOG.md`. Skill phân phối qua git: `/mo-checklist update` để
kéo bản mới (xem `README.md`).

Trước đây mỗi app tự làm MO checklist theo một kiểu, mỗi ticket lại "Ref" một app khác. Skill này là
**nguồn chuẩn duy nhất**:

| Thành phần | Vai trò |
|---|---|
| `catalog.json` / `CATALOG.md` | ~114 mục. ID = `MO-<số dòng sheet "Checklist - MO New">` (+ `DEV-<dòng>`, `CC-<dòng>`; `EXT-<TÊN>` = tactic MO đã làm theo ticket nhưng chưa có dòng trong sheet, không có MO-ID, nhận qua prompt). Mỗi mục có spec, nghiệm thu, key RC chuẩn + alias các app, placement, event, phụ thuộc, mẫu dò, recipe. `CATALOG.md` sinh tự động, đừng sửa tay. |
| `references/<nhóm>.md` | Recipe từng mục, mở bằng section `## MO-xx`: cách làm, bẫy, QC. Mỗi file mở đầu bằng "Tổng quan nhóm". |
| `references/conventions.md` | Luật đặt tên (key RC, placement, event, OPEN_FROM), vị trí file, mẫu báo cáo. |
| `references/stack-adapt.md` | Áp recipe cho app không dùng SDK, XML/Fragment, Hilt, multi-module. |
| `references/qc.md` | Thao tác QC dùng chung (đổi RC, đổi giờ, dark mode, adb). |
| `references/open-questions.md` | Câu hỏi MO/PO chưa chốt (Q1–Q52) và **mặc định skill dùng trong lúc chờ**. |
| `scripts/` | `catalog.py` (tìm/hiển thị mục), `detect_stack.py` (stack app, JDK gợi ý, lệnh verify), `audit.py` (dò mục đã có/thiếu, so 2 app), `sheet_diff.py` (đồng bộ khi MO sửa sheet). |
| `apps.json` | Mã app → tên thư mục + `remote` để clone. Thư mục chứa các repo: env `MO_APPS_ROOT` → `local.json` (`{"root": "…"}`, riêng từng máy, không commit) → thư mục cha của repo đang mở. |
| `assets/` | Ảnh minh hoạ trích từ sheet (`refs/MO-<dòng>-n.jpg`), copy noti theo app (`noti-content.md`). |

**App ref mặc định: A013** (Compose + Nav3 + Koin + xtechads). A013 là demo app của SDK và là app MO coi
là chuẩn.

**Skill KHÔNG chứa code.** Recipe chỉ mô tả cơ chế, nghiệm thu, key RC, bẫy và QC, rồi chỉ tới file +
symbol của app ref. Muốn biết code chuẩn trông thế nào thì **mở repo A013 (hoặc app ref user chọn) và đọc
bản hiện tại trên máy**. Lý do: A013 còn cập nhật liên tục, code chép vào skill sẽ lỗi thời.
- `verified_commit` (trong `meta` và `canonical` của từng mục) = commit của app chuẩn (`canonical.app`, mặc
  định A013) lần cuối recipe được đối chiếu. Nó **không phải** commit để lấy code.
- Code A013 hiện tại khác recipe (`audit.py` báo `↺`) → **theo code A013 hiện tại**, và ghi chú trong báo
  cáo để người bảo trì cập nhật recipe.
- Tên key RC, default, placement trong catalog cũng là ảnh chụp lúc đối chiếu. Lệch với A013 hiện tại →
  theo A013, báo lệch.

`<skill>` = "Base directory for this skill" hiện lúc skill load (local: `~/.claude/skills/mo-checklist`).

## Cách gọi

| Ví dụ | Việc |
|---|---|
| `/mo-checklist thực hiện MO checklist noti lockscreen` | **apply** 1 mục theo mô tả |
| `/mo-checklist MO-95` · `/mo-checklist MO checklist 88 + 90` | apply theo ID (nhiều ID thì làm lần lượt, báo cáo gộp) |
| `/mo-checklist MO-95 ref a045` | apply theo app ref khác + báo khác biệt với A013 |
| `/mo-checklist P3563` (kèm nội dung ticket) | apply theo ticket Product Hub |
| `/mo-checklist audit` · `/mo-checklist audit noti` | app hiện tại đang có/thiếu mục nào |
| `/mo-checklist explain MO-78` | giải thích mục cho PO/QC/dev |
| `/mo-checklist gộp RC` | apply `EXT-RC-GROUP`: hỏi cách đặt tên field (giống key RC cũ / tên mới rút gọn), gộp, in RC đã chỉnh |
| `/mo-checklist update-catalog <file.xlsx>` | (bảo trì) đồng bộ catalog khi MO sửa sheet |
| `/mo-checklist update` | kéo bản skill mới nhất từ repo chung + in CHANGELOG mới |

Cách nhận ID:
- Nhận `MO-82`, `MO 82`, `MO82`, `MO checklist 82`, `checklist MO 82`, `DEV-16`, `CC-3`, `EXT-AD-LOADING`.
- Tactic chưa có trong sheet MO (mục `EXT-*`) không có MO-ID: `catalog.py find "<nguyên văn yêu cầu>"` nhận ra qua từ
  khoá trong prompt (vd "loading trước inter" → `EXT-AD-LOADING`).
- Số trần (`82`) chỉ được coi là ID khi nó là **toàn bộ** tham số. Nhờ vậy `a037` hay `v1.1.4` trong câu
  không bị hiểu nhầm.
- Số dòng có thể đã trôi nếu user nhớ theo bản sheet cũ, nên **luôn in tên mục ra để user thấy**. Nếu mô
  tả user ghi kèm lệch với tên mục thì hỏi lại.

## Quy trình apply (mặc định)

### 0. Kiểm bản skill
```bash
python3 <skill>/scripts/update.py --check
```
Có bản mới (`⬆`) thì nói user một câu, gợi ý `/mo-checklist update`. **Không** tự pull giữa chừng, cứ làm tiếp
bằng bản hiện tại. Lỗi mạng hay skill không phải git repo thì bỏ qua.

### 1. Xác định mục
```bash
python3 <skill>/scripts/catalog.py find "<nguyên văn yêu cầu của user>"
python3 <skill>/scripts/catalog.py show <ID>
```
- Kết quả `find`:
  - khớp ID → dùng ngay;
  - khớp mô tả và "Khớp rõ" → dùng mục đầu;
  - còn lại → hỏi user chọn trong các ứng viên (AskUserQuestion).
- Ticket `Pxxxx`:
  - đọc bằng skill `product-hub` của repo (lark-cli) nếu có;
  - không đọc được thì nhờ user paste Title/Description/Figma/Ref, rồi map vào mục catalog.
- Trạng thái mục:
  - `blocked-policy` → **dừng**, giải thích lý do (vd MO-87 giả cảnh báo hệ thống), đề nghị báo PO/MO;
  - `deprecated` → hỏi lại user;
  - `candidate` → báo MO chưa chốt mục này, hỏi có làm không.
- Đọc section `## <ID>` trong file `recipe` và phần "Tổng quan nhóm" của file đó. Đọc mục trong
  `depends_on` nếu app chưa có.
- Tra mục trong `references/open-questions.md`. Mục có câu hỏi chưa chốt thì làm theo cột **Mặc định**
  và ghi rõ "chờ MO chốt Qx" trong báo cáo.

### 2. Chọn app ref và đọc code chuẩn bản hiện tại
- Mặc định là **A013**. Mục có `canonical.app` khác (MO-85 → A045, EXT-AD-LOADING → A048, EXT-NATIVE-POOL → A052; A013 không có tactic
  đó) thì app đó thay A013 làm ref mặc định của mục; luật "ref ≠ A013" dưới đây chỉ áp khi user chọn ref khác.
- Ref = aXXX khi user ghi `ref aXXX` trong lệnh, hoặc khi ticket ghi "Ref aXXX" và **user xác nhận** dùng.
- **Khi ref ≠ A013:**
  - Theo **cấu trúc và hành vi của app ref**, kể cả khi ref thuộc "họ code" khác recipe (vd noti lock screen họ
    A045). Recipe vẫn dùng cho **nghiệm thu, bẫy, chính sách, QC**.
  - Viết **giống ref cả cấu trúc, tên hàm/biến, hình dạng luồng và style code**, không chỉ giống hành vi. Ví
    dụ: ref tách `LaunchedEffect` riêng cho popup noti thì không gộp vào cổng load ad; ref dùng `HeaderView`
    thì không tự dựng header. Chỉ khác ref ở chỗ luật của repo đích bắt buộc (`CLAUDE.md`, `.claude/rules`),
    và liệt kê từng chỗ trong báo cáo.
  - Ref thiếu dòng nghiệm thu nào, hoặc recipe/catalog có thứ ref không có: **không tự thêm**. Làm giống ref,
    ghi phần thiếu vào bảng khác biệt và hỏi user có thêm không; chưa thêm thì mục là Partial. Lý do: A049
    (10/2026) tự thêm inter ở nút Try màn Uninstall theo nghiệm thu MO-74 trong khi A048 không có, user bắt
    bỏ.
  - Mặc định của các câu hỏi hành vi trong `open-questions.md` lấy theo ref. Các câu đánh dấu lỗi/chính sách
    (Q3, Q22, Q30) và Luật cứng 7 (chính sách Play) luôn áp, bất kể ref.
- Repo ref được tìm qua `apps.json`. Không có trên máy thì hỏi đường dẫn (hoặc clone), hoặc quay về A013.
- Định vị code chuẩn **hiện tại** của mục trong repo ref:
  ```bash
  python3 <skill>/scripts/audit.py --item <ID> --app a013     # file:line lúc chạy + ↺ nếu file chuẩn đã đổi
  ```
- Rồi mở và đọc các file đó, cùng `canonical.files` / `canonical.symbols` trong `catalog.py show <ID>`.
  File đổi tên thì grep theo symbol hoặc mẫu `detect`.
- Header của `audit.py` in nhánh + HEAD + ngày của repo ref. Repo ref đang ở nhánh cũ hoặc lâu chưa
  cập nhật → nói user biết (họ tự `git pull`/checkout). **Đừng tự đổi nhánh repo ref.**

### 3. Ngữ cảnh app hiện tại
```bash
python3 <skill>/scripts/detect_stack.py .                   # stack, SDK version, file mấu chốt, lệnh verify
python3 <skill>/scripts/audit.py --item <ID> --item <dep>   # đã có gì + key RC app đang dùng
```
- Đọc `CLAUDE.md` + `.claude/rules/*.md` của repo và **theo đúng convention đó**: màu, comment, cấu
  trúc màn.
- `git status` có thay đổi chưa commit là WIP của dev: không stash/discard, làm tiếp lên trên và nhắc
  trong báo cáo.
- **Dò lịch sử của mục trong app trước khi sửa**, để biết chỗ nào app **cố ý** làm khác chuẩn (theo ticket
  PO/MO):
  - `git log --oneline -S '<symbol hoặc key>' | head`;
  - `docs/CHANGELOG.md`;
  - mã ticket `Pxxxx` trong commit.

### 4. So ref với A013 (chỉ khi ref ≠ A013)
```bash
python3 <skill>/scripts/audit.py --item <ID> --app a013 --app <ref>
```
- Đọc code của mục ở cả 2 app. Lập bảng khác biệt theo các cột: luồng/hành vi, key RC (tên, kiểu,
  default), placement, event, phần ref còn thiếu so với spec, bug đã biết.
- Bước này **không chặn**: vẫn code theo ref user chọn, bảng đưa vào báo cáo.

### 5. Chọn hướng ("chuẩn" = app ref đang dùng)
- **"Done" = đạt mọi dòng _Nghiệm thu_ của mục** (recipe nào có thì xem thêm phần "Tối thiểu để Done").
  Các bước ghi "(tuỳ chọn)"/"nâng cao" chỉ làm khi user muốn.
- **Đã đúng chuẩn** → không sửa. Báo lại kèm bước QC.
- **Thiếu so với nghiệm thu** → bổ sung phần thiếu, diff nhỏ nhất. Ref ≠ A013 mà ref cũng thiếu dòng đó thì
  không tự thêm, hỏi user như bước 2.
- **Khác chuẩn ở hành vi user thấy được, đã phát hành** (vd back, thời điểm bắn, category noti, định nghĩa
  user mới):
  - **liệt kê và hỏi user trước khi đổi**, nhất là khi lịch sử cho thấy đó là quyết định có ticket;
  - không hỏi được thì giữ hành vi đang chạy và ghi vào báo cáo mục "Thay đổi hành vi cần MO/PO xác nhận".
- Không đổi tên/kiểu key RC, placement, event đã phát hành.
- **Chưa có** → làm theo recipe, với chi tiết lấy từ code app ref **bản hiện tại** (bước 2). Ref mặc định
  (A013, hoặc `canonical.app` của mục): viết code mới theo convention của app đích, không bê nguyên file sang.
  Ref do user chọn (≠ A013): viết giống ref như bước 2.
- Thiếu nền (vd chưa có hạ tầng noti, chưa route mở lại qua Splash) → báo rõ và hỏi có làm kèm mục
  `depends_on` không.

### 6. SDK-first
- Version xtechads của app có API (`sdk.min_version`) → dùng API.
- Chỉ bản SDK mới hơn mới có API → **đề xuất bump và hỏi trước**: lib + plugin cùng version, đọc
  CHANGELOG, build release.
- App không dùng SDK (a028, a036, a041) → làm trên lớp ads sẵn có của app theo
  `references/stack-adapt.md`. Không migrate SDK trong task MO.

### 7. UI & nội dung
- **Design:** lấy node Figma của mục (`figma` trong catalog) qua `figma` skill / `.claude/.figma-config.json`
  của project, hoặc Figma MCP nếu chạy được. Không lấy được thì dùng ảnh `assets/refs/` và nói rõ trong
  báo cáo.
- **Copy noti:** user/ticket đưa → `assets/noti-content.md` (snapshot, có thể cũ) → `TODO(mo)`.
- Thiếu ảnh/asset thì dựng sẵn base chạy được và đánh `TODO(mo)` tại chỗ. Repo cấm comment thì không chèn
  vào code, chỉ liệt kê trong báo cáo.

### 8. Build verify
- Dùng lệnh `verify` từ `detect_stack.py`.
- Chạy **baseline trước khi sửa**.
  - Fail vì **môi trường** (JDK/Gradle không hợp, `sdk.dir`, mạng): sửa môi trường mà **không đổi file dự án**,
    vd `export JAVA_HOME=…` theo dòng `jdk_suggest` của `detect_stack.py`. Ghi lại trong báo cáo.
  - Fail vì **code** (WIP có sẵn): báo user và dừng.
- Dùng `set -o pipefail; <lệnh> 2>&1 | tail -30`.
- Build lạnh có thể > 10 phút: chạy nền, đừng huỷ.
- Build release thì thêm `-x uploadCrashlyticsMappingFile<Variant>`, để không upload mapping ra Firebase.
- Build bẩn file tracked thì xem `stack-adapt.md` §5.
- **Không commit, không push, không tạo AVD mới.**
- Chỉ chạy máy ảo/máy thật khi user muốn; dùng AVD có sẵn.

### 9. Báo cáo (mẫu chi tiết ở `references/conventions.md` §6)
**Trạng thái:**
- **Done** = logic đạt mọi dòng nghiệm thu. Placeholder copy/ảnh `TODO(mo)` được phép nhưng phải liệt kê.
- **Partial** = còn ≥ 1 dòng nghiệm thu chưa đạt.
- **Blocked** = thiếu input (Figma, quyết định MO, quyền).

- Mục đã làm (`MO-xx` + tên) và app ref đã dùng.
- File đã đổi.
- **Key RC + default mà MO cần tạo/kiểm trên Firebase.** Ghi rõ là key mới, key cũ của app, hay key
  user đưa.
- Placement cần thêm vào `ads_config`: ghi rõ thêm cả nameSpace + placement vào bản trên Firebase (bản đó thay
  nguyên file, thiếu là vị trí tắt im lặng); event tracking.
- Bước QC; các `TODO(mo)`.
- **Ref ≠ A013:** thêm bảng khác biệt + nhận xét điểm nào nên đồng bộ về A013 hoặc nên đưa ngược vào
  A013.
- Cuối cùng 1 dòng để dán vào sheet MO: `MO-xx | <tên> | <app> v<version> | Done/Partial | <ghi chú>`. Mục `EXT-*`
  ghi `EXT-<TÊN> (ngoài sheet) | …` để MO biết chưa có dòng tương ứng.
- Mục `EXT-RC-GROUP` (gộp RC): cuối báo cáo in khối RC đã chỉnh cho từng parameter (`key:` / `type: json` /
  `value:` JSON mặc định 1 dòng), mẫu ở recipe `setup.md` § EXT-RC-GROUP bước 10.

## audit
```bash
python3 <skill>/scripts/audit.py [--group noti] [--repo <dir>] [--json]
```
- Kết quả là heuristic tĩnh:
  - "Đủ dấu hiệu" ≠ đạt nghiệm thu; mục nào cũng phải **đọc code** để kết luận.
  - Không truyền `--app`/`--repo` thì audit thư mục hiện tại (kể cả worktree).
  - `--app aXXX` luôn trỏ repo gốc trong `apps.json`. Dùng để xem app ref.
- In bảng theo nhóm, mỗi dòng có:
  - trạng thái + bằng chứng `file:line`;
  - chênh lệch với chuẩn (vd key RC đang dùng alias);
  - thứ tự nên làm các mục thiếu, theo `depends_on`.
- Chỉ in ra, không ghi file (trừ khi user yêu cầu).

## explain
Dùng `catalog.py show <ID>` + section recipe, rồi giải thích bằng lời thường:
- user thấy gì;
- remote config nào điều khiển;
- QC test thế nào;
- app nào đang làm đúng (`sheet_status` trong catalog là snapshot từ sheet MO).

## update-catalog (người bảo trì)
1. `python3 <skill>/scripts/sheet_diff.py "<file.xlsx>"` (cần `openpyxl`). Script so sheet "Checklist -
   MO New" với catalog **theo nội dung**: mục đổi số dòng, mục sửa chữ, mục mới, mục không còn.
2. Trình báo cáo cho user duyệt, rồi chạy
   `sheet_diff.py "<file.xlsx>" --apply --snapshot <YYYY-MM-DD> --images`. Script sẽ:
   - đổi ID và giữ ID cũ trong `old_ids`;
   - sửa heading `## MO-x` trong references, `depends_on`, `recipe`;
   - thêm khung cho mục mới;
   - chuyển mục bị xoá thành `deprecated`.
3. Mục có `needs_review`: viết hoặc soát lại section recipe theo đúng khuôn của file cùng nhóm. Điền
   `group`, `aliases`, `rc_keys`, `detect`… vào catalog, bằng tay hoặc qua `catalog.py merge <staging.json>`.
   Xong thì xoá `needs_review`.
   - Mục mới là tactic đã có mục `EXT-<TÊN>` (script không tự khớp vì mục EXT không có `sheet`): gộp vào mục EXT,
     đổi ID sang `MO-<dòng>`, giữ `EXT-<TÊN>` trong `old_ids`, chép dữ liệu sheet từ khung mới rồi xoá khung,
     đổi heading `## EXT-<TÊN>` và `recipe` sang ID mới (`CONTRIBUTING.md` luật 4).
4. Làm mới recipe khi A013 đổi:
   - `audit.py --app a013` báo `↺` ở mục nào có file chuẩn đã đổi;
   - xem chi tiết: `git -C <A013> diff <verified_commit> -- <file>`;
   - sửa lời recipe (vẫn không chép code);
   - cập nhật `canonical.verified_commit` của mục đó (và `meta.verified_commit` nếu đối chiếu cả loạt).
5. Chạy `catalog.py check` rồi `catalog.py render`, cuối cùng `scripts/ci_check.py` (tăng phiên bản +
   CHANGELOG). Quy trình nhánh/PR: `CONTRIBUTING.md`.

## Luật cứng
1. **Mỗi mục một cách làm chuẩn.** Ref mặc định A013 (hoặc `canonical.app` của mục); ref khác chỉ khi user
   chọn, và **luôn kèm bảng khác biệt với A013** (với ref mặc định của mục nếu không phải A013).
2. **Chọn tên** key RC / placement / event / hằng OPEN_FROM theo thứ tự:
   1. user/ticket đưa;
   2. app đang có (dò bằng alias trong catalog / `audit.py`);
   3. tên của app ref đang dùng: mặc định A013 (`CATALOG.md`); ref khác thì theo ref, và ghi tên chuẩn A013
      tương ứng vào bảng khác biệt.
   - Không đổi kiểu hay đơn vị của key đã phát hành.
   - Theo kiểu app đang dùng: key phẳng hay JSON nhóm; `splash_next` hay `splashNext`.
3. **SDK-first**; không tự bump SDK; không migrate SDK trong task MO.
4. **Không commit/push**; không chạm sheet MO / Product Hub / Firebase khi chưa hỏi user.
5. **Không chép secret:** license/AES key của SDK, AppsFlyer key, Adjust token, ad unit ID thật, Facebook
   token, `.figma-token`.
6. **Không chép lỗi đã biết của A013**, vd set consent Firebase luôn GRANTED (`App.initFCM`). Recipe
   setup có cách đúng.
7. **Chính sách Play:**
   - không giả mạo UI/cảnh báo hệ thống (MO-87);
   - màn uninstall phải có đường gỡ app thật;
   - full-screen intent phải xử lý khi bị thu hồi quyền (Android 14+);
   - nút CTA native không trùng màu nút của app.
8. **Skill không chứa code.**
   - Khi bảo trì, không chép code (Kotlin/XML) của app nào vào `references/` hay `catalog.json`.
   - Chỉ ghi cơ chế, quyết định, bẫy, QC, đường dẫn file + tên symbol.
   - Lúc apply luôn đọc code app ref bản hiện tại.
9. **Luật của repo ưu tiên hơn skill** (`CLAUDE.md`, `.claude/rules`, quy trình bắt buộc).
10. **Không tự thêm ngoài mục.** Cờ/pref mới, hành vi mới, hay chuyển hành vi sang màn khác mà nghiệm thu,
    recipe và app ref đều không đòi (vd cờ "chỉ hỏi quyền noti 1 lần") → đề xuất trong báo cáo, chờ user
    đồng ý rồi mới làm. Nghiệm thu đòi mà ref do user chọn không có: theo bước 2 (không tự thêm, hỏi user).

## Bản đồ tài liệu

| Nhóm | File | Mục (ví dụ) |
|---|---|---|
| setup | `references/setup.md` | MO-5..20, MO-100, DEV-3, EXT-RC-GROUP |
| splash | `references/splash.md` | MO-21..31, 84, 96, 97, 99 |
| language | `references/language.md` | MO-32..42, 86, 94, 98, DEV-6/8/9 |
| select | `references/select.md` | MO-43..51, DEV-10 |
| onboard | `references/onboarding.md` | MO-52..67, 92, EXT-NATIVE-POOL |
| noti | `references/notifications.md` | MO-4, 68..73, 75, 87..89, 95 |
| reopen | `references/reopen.md` | MO-74, 76..78, 91 |
| ads | `references/inapp-ads.md` | MO-79..82, 93, DEV-16, DEV-21, EXT-AD-LOADING |
| rating, ux | `references/misc.md` | MO-85, MO-2, 3, 83, 90, DEV-19 |

Danh sách đầy đủ: `CATALOG.md`, hoặc `python3 <skill>/scripts/catalog.py list [nhóm]`.

## update
`/mo-checklist update` (hoặc "cập nhật skill mo-checklist"):
```bash
python3 <skill>/scripts/update.py
```
- In lại kết quả cho user: phiên bản cũ → mới và phần CHANGELOG mới.
- Script từ chối pull khi thư mục skill có sửa đổi local hoặc commit chưa push. Khi đó chuyển nguyên văn
  hướng dẫn của script cho user; **không** tự `stash`/`reset`.
- Sau khi cập nhật, đọc lại `SKILL.md` trước khi làm tiếp.

## Cài đặt & bảo trì
Hướng dẫn cài cho dev và quy trình phát hành bản mới cho người bảo trì: `README.md`.

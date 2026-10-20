# CHANGELOG — skill mo-checklist

## 2.0.0 — 2026-10-15

Cập nhật sau khi làm MO checklist cho A049 Palm AI (noti ref A047; splash, language, onboarding, uninstall, inter ref
A048). Đối chiếu với code hiện tại: A013 `f784827`, A047 `61711d3`, A048 `fcecc4a`, A049 v1.0.1 (`78a9c9b` + phần sửa
chưa commit ngày 15/10), xtechads 1.8.7.

**Đổi luật (`SKILL.md`)** — lý do tăng major:
- Ref ≠ A013: viết giống ref cả cấu trúc, tên hàm/biến, hình dạng luồng và style code, không chỉ giống hành vi. Chỉ
  khác ở chỗ luật repo đích bắt buộc, và liệt kê trong báo cáo.
- Ref ≠ A013 thiếu dòng nghiệm thu: **không tự thêm nữa** (bản cũ ghi "bổ sung cho đủ"). Làm giống ref, ghi vào bảng
  khác biệt và hỏi user; chưa thêm thì mục là Partial. Câu lỗi/chính sách (Q3, Q22, Q30) và Luật cứng 7 vẫn luôn áp.
- Luật cứng 10: không tự thêm cờ/pref/hành vi ngoài mục; đề xuất trong báo cáo.
- Mục có `canonical.app` ≠ A013 (MO-85 → A045, EXT-AD-LOADING → A048): app đó là ref mặc định của mục.
- Báo cáo: placement mới phải thêm cả nameSpace + placement vào `ads_config` trên Firebase; mục EXT ghi
  `EXT-<TÊN> (ngoài sheet)` ở dòng dán sheet MO.

**Mục ngoài sheet `EXT-<TÊN>`** (`SKILL.md`, `CONTRIBUTING.md` luật 4–5, `catalog.json`):
- Tactic MO đã làm theo ticket nhưng chưa có dòng trong sheet "Checklist - MO New": mục `EXT-<TÊN>`, không có MO-ID
  (`sheet` = "", `row` = 0), nhận qua prompt bằng `catalog.py find` hoặc gọi thẳng ID.
- Khi MO thêm dòng vào sheet: đổi sang `MO-<dòng>`, giữ `EXT-<TÊN>` trong `old_ids` (`SKILL.md` § update-catalog).
- Mục đầu tiên: **`EXT-AD-LOADING`** — loading trước inter in-app và lúc SDK nạp `app_resume` (ticket A049 P4713, ref
  A048; key `time_show_loading_ads`; recipe `inapp-ads.md` § EXT-AD-LOADING).

**`scripts/catalog.py`**: `find` / `show` (và `audit.py --item`) nhận ID `EXT-<TÊN>`; `render` giải thích `EXT-*` ở
đầu `CATALOG.md`; `check` báo lỗi mục EXT sai dạng ID, có `sheet` / `row`, hoặc thiếu `aliases`.

**Recipe** — bẫy, QC, đoạn "Ref A047/A048 khác A013", "App đã làm: A049":
- splash, setup: MO-9, 16, 18, 22, 25, 26, 28, 29, 84, 96, 97, 100. Bẫy build chung: release crash R8 do
  `WorkDatabase_Impl` (AGP 9 + work-runtime 2.7.0 / Room 2.2.5 kéo theo play-services-ads); tên adunit phải theo
  tiền tố để test ad bản debug đúng loại.
- language: Tổng quan (bản đồ ref A048, RTL, locale), MO-32, 33, 35, 36, 86, 94, 98, DEV-6.
- onboarding: MO-59, 61, 62, 64–67, 92.
- noti: Tổng quan + Luật cứng (trùng tên resource noti với xtechads, nút trong custom view không ăn `autoCancel`,
  chữ dự phòng cho noti custom view, mở lại từ Recents), MO-68–73, 88, 95.
- reopen, ads, rating, ux: MO-74, 78, 81, 82, 85, 90, 91, DEV-16; section mới EXT-AD-LOADING.

**Sửa chỗ recipe sai so với code**
- MO-9 + Tổng quan setup: load ad trước consent không phải luôn `FAIL` — lúc UMP chưa trả trạng thái thì `umpAllowed`
  = true, request vẫn đi.
- MO-25: A013 chỉ ghi `NOTIFICATION_FINISH` khi user cấp quyền.
- MO-64: a047 không gắn `screen` cho unit onboarding.

**`conventions.md`**: giá trị `open_from` theo dòng "PO request" của sheet Universal Events & Parameters; tên track
dùng chung cho màn/overlay/nút MO (`BtnDeviceBack`, `OvlNoInternet`, `OvlAdsLoading`, `OvlConfirmLanguage`,
`ScrNotificationLockScreen<N>`, `BtnTryNow<Feature>`); param PO `language`, `rating`, `rating_bad` qua
`TrackingParams`; JSON nhóm đọc qua `RcGroup`; mẫu báo cáo §6 thêm dòng "nghiệm thu ref thiếu", "khác ref vì luật
repo" và dòng sheet cho mục EXT.

**Thêm sau khi A049 sửa theo A013/A048 (15/10) và ghi chú của phiên làm A049:**
- A049 gắn sheet Ad script (P4718): MO-81 ghi A049 dùng `DetailScreenState` + `InterBackHandler` như A047 cho màn
  tính năng + Settings; MO-82 và catalog đổi key A049 sang `interval_inter_inapp`; MO-86 thêm popup back ở màn
  Language của A049 (P5013, ref a044, `inter_ob` nạp lúc bấm).
- MO-69 / Q21: A049 bỏ `noti_config:kill_app.show_all` (15/10, user: field RC nào chưa app nào có thì bỏ). Recipe,
  Q21 và catalog ghi key đề xuất `noti_kill_app_show_all` là chưa app nào có, chỉ thêm khi MO chốt tên và user yêu
  cầu. Ví dụ field lồng ở `conventions.md` đổi sang `lockscreen.slots`.
- MO-69 / Q21: sau đó QC báo bug "ở Home kill / minimize không có noti kill app". User chốt noti ref A047, A049 bỏ gate
  FO: bắn mọi phiên ở `onStop`, chỉ còn kill-switch `noti_config.kill_app.enable`. Recipe (hiện trạng + "App đã làm
  — A049"), Q21 và notes catalog chuyển A049 sang nhóm "mọi phiên". Lệch dòng nghiệm thu "hết FO thì không bắn" như
  A045/A047/A048.
- Recipe cập nhật hiện trạng A049: `loadSplashAds` đã nạp lại unit `FAIL` (MO-96), nút mở mạng tự kéo app về qua
  `PermissionSettingsGuide` (MO-26), FSN truyền `defaultNativeLayout`, mũi tên `autoMirrored`.
- MO-62: A049 `loadOrReload` (bản nhận `context`) **giữ nguyên** logic luôn `loadAd`, để SDK tự bỏ qua ad còn hạn.
  - Đã thử đổi theo A048 (`NONE || reload`) rồi trả lại: user chốt giữ logic đang chạy.
  - Thêm luật: app đã có hàm load/reload đang chạy thì giữ nguyên, ghi điểm lệch vào bảng khác biệt, chỉ sửa khi user
    yêu cầu.
- MO-29 (+ trỏ từ MO-97): nạp cùng lúc inter và `native_full_splash` ở splash làm ANR 100% trên máy Motorola.
  - Nguồn: tip của team, user chuyển lại ngày 15/10. Không phải quan sát trên A049, chưa có trace hay commit đối chiếu.
  - Cách xử lý: warm-up WebView (`WebSettings.getDefaultUserAgent`) trên main thread, xong trước lệnh nạp ad splash
    đầu tiên. Bẫy ghi rõ thread và thời điểm, trỏ chéo tới bẫy ANR a037 P1624 (MO-22, MO-84, MO-97).
  - QC: chạy luồng FO trên máy Motorola. Dò repo trên máy: chưa app nào có warm-up này.
- `setup.md`: key RC SDK khai trong `AdsSharedPref` mà SDK không tự dùng (`star_review_to_store`,
  `interval_skip_inter`…) — app phải tự áp; MO-85 ghi rõ điều này.
- `qc.md`: `ads_config` trên Firebase thay nguyên file, thiếu placement/nameSpace là tắt im lặng; kiểu giá trị RC
  (số thập phân → Float, JSON nhập sai kiểu → cả nhóm về default).
- MO-95: cách tính user mới quyết định cách QC `slots_new`; slot sai định dạng: A049 bỏ im lặng, a037 parse lenient
  (`25:00` → 01:00). MO-70: chưa có quyền noti thì không hiện gì. Select: bẫy bàn phím làm native giật; MO-43 thêm cách
  A049 làm bước Select bằng màn nhập tên (Name/NameAlt).
- `conventions.md`: kiểm giá trị RC trước khi đưa vào thư viện; cập nhật tài liệu RC của app cùng commit (khung a037 /
  A049).
- MO-7: thay App ID mẫu của Google bằng App ID thật khi AdMob chưa publish GDPR message cho app → UMP lỗi
  "Publisher misconfiguration … no form(s) configured", SDK vẫn init ad, form consent không hiện. Thấy trên A049
  15/10 (emulator, debug giả lập EEA). Thêm bẫy + dòng QC: grep `requestUMP: requestConsentError` sau khi thay ID.
- MO-14: dev key AppsFlyer dùng chung cả team (9 app cùng key); app chưa được thêm vào tài khoản AppsFlyer thì
  `start` trả 404 (`onError: 50`), `sdk_init` `appsflyer` = FAILED (A049 15/10). Thêm bẫy + dòng QC theo `sdk_init`.
- MO-64 / MO-66 (A049 P5078, 16/10): bỏ trang đang xem khi nạp lại thì trang hiện tại không có impression mang
  `screen_name` của nó (A047 `preloadOnboard` cũng vậy); trang cách 2 bước compose ngoài màn vẫn ghi impression.
  A049 sửa theo A048. MO-31: native nạp sẵn hiện trong lúc chuyển màn Navigation3 → impression đầu mang màn trước,
  `reloadWhenResume: true` nạp thêm khi RESUMED.
- MO-78 (A049 16/10): process bị thu hồi khi task còn → mở lại khôi phục màn sâu, bỏ Splash; A049 bỏ saved state khi
  process mới (A047 không). Thêm cách QC bằng `run-as … kill -9`.
- MO-31 / MO-35 / MO-42 / MO-67 / MO-99 (A049 16/10, MO báo 5 điểm thời điểm preload): preload lúc dựng màn
  (`LaunchedEffect(Unit)`) ghi `screen_name` màn trước, kể cả dưới inter splash → đặt trong `LifecycleResumeEffect`
  như A013; màn kế của Onboard chỉ nạp ở trang cuối; không có `splash_o` thì không nạp sẵn inter splash lúc bắn noti
  (rơi vào `inter_splash_high` ở Language/Home); trước Onboard nạp `onboard_1` + `fs_onboard`. MO-98: unit đệm Alt
  nạp ở Alt (A013), không ở Normal như A048.
- MO-25 (bẫy focus, A049 16/10): cổng Splash chờ `hasWindowFocus` vô điều kiện + app ẩn nav bar → treo vì thông báo
  "Viewing full screen"; chỉ chờ focus khi màn khoá.

**Thêm 16–20/10 (A049 tới `789ec20` + phần chưa commit):**
- CC-2: mục "App đã làm: A049" (N = 1): reward tắt / đã mua / không consent thì chạy tính năng luôn; tải lỗi theo RC
  mới `reward_fail_continue` (Boolean, mặc định `true`, user chọn tên, chưa app nào khác có), `false` thì toast
  `cannot_fetch_ads`. Câu mới Q53 (A045 chạy, A047 báo lỗi). Catalog thêm key + alias.
- MO-82: inter `inter_replace_reward` (tên A047) cho 4 nút làm lại, chung `interval_inter_inapp` và mốc interval; icon
  ad trên nút là quyết định riêng app (A049 chỉ giữ ở Scan again).
- MO-7 QC: lỗi UMP "no form(s) configured" hết ngay khi MO publish message GDPR trên AdMob, không cần build lại.
- `qc.md`: trước release đối chiếu ID `ads_config` (repo + bản Firebase đọc qua `run-as`) với sheet Ad script: ID test
  ở nameSpace đang bật, 2 unit trùng ID; không xoá placement đã nối code chỉ vì đang tắt.
- MO-61: chọn layout trang onboarding theo trạng thái unit (`FAIL` → layout không ad), không theo placement có bật.
- MO-32 / DEV-6: bỏ số mã và `order` mặc định cụ thể của A049 (bộ mã, thứ tự là yêu cầu PO riêng từng app, không
  phải luật chung).
- MO-43: A049 sang ScrNameAlt khi chạm ô tên hoặc chạm giới tính (trước: gõ ký tự đầu).
- MO-8: tên app trong form consent lấy từ AdMob, không theo `app_name`. `conventions.md`: đổi `app_name` là đổi giá trị
  `open_from` mở thường (A049 `app_palm ai` → `app_hastgy`).

**Rà lại toàn bộ phần mới (6 reviewer độc lập, đối chiếu code hiện tại) — đã sửa:**
- Câu trình bày cách A049 làm như chuẩn chung → ghi theo ref + câu hỏi mở: MO-26 QC máy có VPN (Q34), MO-59 hướng đi
  khi FSN `FAIL` (Q40), MO-62 điều kiện `loadOrReload` (sau đó user chốt A049 giữ logic cũ, xem mục MO-62 ở trên),
  MO-86 / DEV-6 (Q37 / Q38), MO-74 số shortcut (Q48), DEV-16 bỏ
  câu khuyên "nên có loading" (thuộc EXT-AD-LOADING, chỉ làm khi user yêu cầu).
- Sai so với code: a037 `parseSlotTime` lenient; A047 cũng tính user mới theo `PackageInfo.firstInstallTime` và không
  hiện noti click-ads khi thiếu quyền; A048 tính user mới theo `prefs.firstOpen`, có set `CATEGORY_ALARM`; tên class
  tracker AppsFlyer (`AfImpressionThresholdTracker` / `AfRevenueThresholdTracker`); đường dẫn `RcGroup.kt`;
  `startExternal` không nằm trong object `Commons`; QC "kiểm nền" + mốc interval của MO-82 theo từng app.
- Alias lỗi thời của A045 v1.0.9 (đợt gom RC): `language_config.*`, `select_config.*`,
  `onboard_config.fsn_close_second`.
- Thêm: bẫy MO-10 `ensureAdsInitialized()` trong process mới lúc UMP chưa trả trạng thái; cảnh báo `LocalConfiguration`
  không đổi khi đổi ngôn ngữ mà không recreate Activity; Q4 thêm tiền lệ A049 bỏ trần tổng splash.

**`open-questions.md`**: tiền lệ A047/A048/A049 cho Q1–Q4, Q11, Q13, Q19, Q21–Q23, Q27, Q28, Q30; câu mới Q33–Q52.

**`catalog.json`**: alias key RC/placement của A048, A049 (gồm JSON nhóm `language_config`, `noti_config`) và a045
v1.0.9 (a045 bỏ `language_config.finger_position` ở bản này); mục mới `EXT-AD-LOADING` (key `time_show_loading_ads`);
`meta.id_rule` thêm `EXT-<TÊN>`; ghi chú + QC theo recipe; mẫu dò thêm `armInterInAppPreload` (MO-82),
`showConfirmLanguage` (MO-86), `backToMain` (MO-91).

**`apps.json`**: thêm a048; a049 trỏ `A049_Palm-AI`.

## 1.2.0 — 2026-10-12

- **Cho phép nhiều người cùng đóng góp:** thêm `CONTRIBUTING.md`.
  - Quy trình: sửa trên nhánh riêng → `scripts/ci_check.py` → Pull Request → người bảo trì review.
  - Kèm mẫu PR, `CODEOWNERS`, CI GitHub Actions (job `check`).
- **CI chặn:**
  - catalog lỗi;
  - CATALOG.md chưa render;
  - commit `local.json`;
  - ID quảng cáo thật;
  - thay đổi nội dung mà chưa tăng phiên bản / thiếu CHANGELOG.
- **`/mo-checklist update`:** khi đang ở nhánh đóng góp thì không nhắc/không pull. Muốn update phải về `main`.

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

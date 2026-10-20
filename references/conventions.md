# Quy ước chung khi làm MO

Mục tiêu: dù app nào làm, cùng một mục MO thì tên, hành vi và cách track phải giống nhau. Riêng các app đã
phát hành thì không làm vỡ cấu hình MO đang chạy trên Firebase.

## 1. Thứ tự chọn tên

Áp cho **key Remote Config, placement ads, event tracking, ad unit/nameSpace, hằng OPEN_FROM/OPEN_TO**.
1. **Tên user hoặc ticket đưa** (vd ticket ghi rõ key `xxx`). Với tracking (event, param, giá trị
   `open_from`), PO còn ghi trong tab của app ở sheet "Universal Events & Parameters" (dòng "PO request",
   khối User Journey Event): tên ở đó tính là "ticket đưa".
2. **Tên app đang có.** Dò bằng `audit.py --item <ID>`: dòng `RC:` cho biết app đang dùng key chuẩn
   (`✓`) hay alias. Alias của mọi app nằm trong `catalog.json` (`rc_keys[].aliases`,
   `placements[].aliases`).
3. **Tên của app ref đang dùng:** mặc định A013 (bảng "Key Remote Config chuẩn" trong `CATALOG.md`). User
   chọn ref khác thì theo tên của ref, và ghi tên A013 tương ứng vào bảng khác biệt.

Kèm theo:
- Không đổi **kiểu** hoặc **đơn vị** của key đã phát hành. Ví dụ A013 dùng ms (`preload_lead_inter` =
  5000), còn a016/A045 dùng giây (`preload_inter_buffer_second` = 5). Tạo key mới theo chuẩn thì dùng
  đúng đơn vị của chuẩn.
- Theo **kiểu tổ chức RC** của app:
  - key phẳng `SharedPreferenceProperty("key", default)` như A013 và đa số app;
  - hoặc JSON nhóm (`language_config`, `onboard_config`, `noti_config`… ở a037, Langofy, a034, a045 từ v1.0.9,
    A047, A048, A049). Khi đó thêm field vào đúng nhóm và báo đường dẫn JSON cho MO. a045, A048, A049 đọc nhóm
    qua `RcGroup` (`domain/preference/RcGroup.kt`, khai nhóm trong `SharedPrefs.kt`), field lồng viết dạng
    `tick.size`, `lockscreen.slots`.
- Theo **kiểu tên placement** của app: `language`/`language_alt`/`onboard_1`/`fs_onboard` (chuẩn A013) hay
  `native_lang`/`native_lang_alt`/`native_ob1`/`native_fsob` (a016, a037, a039, Langofy). App mới hoặc
  chưa có kiểu thì dùng chuẩn A013.
- Key mới bắt buộc có **default an toàn trong code**, tức là chưa fetch được RC thì app vẫn đúng hành vi
  mặc định MO muốn. Báo key + default cho MO trong báo cáo.
- Giá trị RC đưa thẳng vào thư viện (base URL Retrofit, màu, Uri) phải được kiểm, sai thì fallback, nếu không
  là crash. Vd A049 `PalmLineConfig.resolveBaseUrl`: chỉ nhận URL https mà `toHttpUrlOrNull` parse được.
- Mục MO thêm hoặc đổi key RC thì cập nhật **tài liệu RC của app** trong cùng commit. Khung mẫu: a037
  `docs/remote-config-group.md`, A049 `docs/features/remote-config.md` — bảng key (kiểu, ai đọc: App/SDK, từ phiên
  bản), quy tắc từng field, thời điểm có hiệu lực, bẫy, test case. Sheet "Remote config" trong file checklist PO
  của app: key SDK để trên, key app để dưới; cột Version note = phiên bản bắt đầu có key, key SDK thêm "(SDK)" (A049:
  "Từ v1.0.1 (SDK)").

## 2. Tên chuẩn A013 (ảnh chụp lúc viết — lệch thì theo code A013 hiện tại)

### Mở lại app & tracking nguồn mở
- Extra: `KEY_OPEN_FROM = "open_from"` (Int) và `KEY_OPEN_TO` (Int). Cả hai nằm ở `common/Constant.kt`.
- `OPEN_FROM_*`: `DEFAULT`, `DAILY_NOTIFICATION`, `PINNED_NOTIFICATION`, `KILL_NOTIFICATION`,
  `REMINDER_NOTIFICATION`, `WINBACK_NOTIFICATION`, `NOTIFICATION_LOCKSCREEN`, `SHORTCUT`, `WIDGET`.
- `OPEN_TO_*`: tính năng đích (`PROTECTOR`, `RECOVERY_PHOTO`, `ENHANCE`, `JUNK`, `UNINSTALL`…). Đặt theo
  tính năng của từng app.
- Event **`app_open_from`**, param `open_from`, các giá trị:
  - `notification_daily`, `notification_pinned`, `notification_kill`, `notification_reminder`,
    `notification_winback`;
  - `notification_lock_screen` (hoặc `notification_lock_screen_un_support` khi không dùng được
    full-screen intent);
  - `widget`;
  - `shortcut` / `shortcut_<tính năng>` (vd `shortcut_uninstall`).
  - Mở từ file của app khác (open-with): A013 log `open_from_gallery`.
- Mọi đường mở lại app (noti, widget, shortcut, open-with) đều **đi qua Splash** (`CLEAR_TASK`) để ăn
  ads, rồi mới tới tính năng đích (MO-78).
- **Giá trị `open_from` PO chốt** (sheet "Universal Events & Parameters", dòng "PO request" của tab app,
  10/2026). App có tab này thì theo PO, không theo tên A013 ở trên:
  - `notification_pinned`, `notification_kill`, `notification_daily`, `notification_click_ads`, `shortcut`,
    `shortcut_uninstall`, `gallery`, `widget`, `home_screen` (homeapp);
  - mở thường từ launcher/recents = `app_{app_name}`. A048: tiền tố `app_` + `R.string.app_name` viết
    thường, giữ khoảng trắng (A049 ra `app_palm ai`; 16/10 đổi tên app thành Hastgy nên ra
    `app_hastgy`: đổi `app_name` là đổi giá trị tracking, phải báo MO/DA). A048/A049 log `app_open_from` ở **mọi** lượt mở, kể
    cả mở thường (`MainActivity.initArgs`);
  - `app_name` đọc theo ngôn ngữ app: A048 khai `translatable="false"`; A049 có bản dịch nhưng mọi locale giữ
    cùng một tên (từ 16/10 là "Hastgy"). Bản dịch nào đổi tên app thì giá trị này đổi theo ngôn ngữ;
  - loại PO chưa liệt kê, theo A048: `notification_win_back`, `notification_lockscreen`. Không dùng được
    full-screen intent: A048 bắn thêm event `notification_lockscreen_un_support` lúc post noti; A049 bắn event
    đó và còn dùng tên này làm giá trị `open_from` khi user bấm noti (như A013
    `notification_lock_screen_un_support`);
  - A048/A049 giữ ở enum `OpenFrom(trackingName, notificationType)`: `trackingName` = giá trị `open_from`,
    `notificationType` = param `type` của event `notification_clicked` (A048 `Tracking.logNotificationClicked`,
    A049 log thẳng trong `MainActivity.initArgs`).

### Placement (ads_config) cho luồng MO
- **Splash:** `splash` (+ `inter_splash_high`, `inter_splash_all`, `native_full_splash`, `bottom_splash`).
- **Language:** `language`, `language_alt`, `popup_lang` (popup xác nhận ngôn ngữ).
- **Select:** `select`, `select_alt`, `select_loading`, `native_preparing`.
- **Onboarding:** `onboard_1`, `onboard_2`, `onboard_3`, `fs_onboard`, `inter_ob_3`.
- **Trong app:** `inter_inapp`, `app_resume` (SDK tự lo), `exit`, `permission`.
- **`navigationFlow`** là danh sách `{key, value}`:
  - key: `splash_next`, `language_next`, `select_next`, `onboard_next`;
  - value: `language`, `select`, `onboard`, `home` (A045 thêm `uninstall`);
  - a016 dùng camelCase `splashNext` → giữ kiểu của app.

### Event tracking
- `screen_show` (`screen_name`, `prev_screen_name`), `button_click` (`button_name`, `screen_name`, …),
  `overlay_show` (`overlay_name`, `screen_name`). Tên màn = tên class Dest/Screen (`ScrSplash`,
  `ScrLanguageAlt`…), tên overlay = tag `Ovl…`.
- `iaa_request` / `iaa_loaded` / `iaa_fail_load` / `iaa_impression` / `iaa_fail_show` / `iaa_click` /
  `iaa_complete`: SDK tự bắn, có param `placement`.
- `sdk_init`: SDK tự bắn, đo thời gian init.
- **Tên track dùng chung cho màn/overlay/nút của mục MO** (theo `naming-rules.md` của skill `build-tracking`,
  đã có ở A048 và A049; tên nút `Btn` + PascalCase, không gạch dưới):
  - back cứng / vuốt back: `button_click` `button_name=BtnDeviceBack` (không dùng `device_back`);
  - popup mất mạng (MO-26): `OvlNoInternet`, nút `BtnOpenSettings`;
  - loading trước inter in-app và lúc SDK nạp `app_resume` (EXT-AD-LOADING): `overlay_show` `OvlAdsLoading`.
    `naming-rules.md` ghi tên này chưa thống nhất (a037 `OvlAdLoading`): app cũ giữ tên đang có trên sheet;
  - popup xác nhận ngôn ngữ (MO-86, MO-94): `OvlConfirmLanguage`, nút `BtnConfirm` / `BtnCancel` / `BtnClose`;
  - noti màn khoá (MO-95): `screen_show` `ScrNotificationLockScreen<N>` (N = layout 1, 2, 3), nút `BtnClick`
    (mở app) / `BtnNotiClose`;
  - màn Uninstall (MO-74, MO-91): `ScrUninstall`, nút thử tính năng `BtnTryNow<Feature>` (A048
    `BtnTryNowTranslate`…), không dùng 1 tên chung kèm param.
- **Param PO dùng chung** (dòng "PO request" của sheet trên): `language` = mã viết hoa (`EN`) ở `BtnNext` /
  `BtnApply` màn ngôn ngữ; `rating` = "1"…"5" và `rating_bad` ở `BtnSubmit` popup đánh giá. A048, a044,
  A049 gom ở object `TrackingParams` (`common/utils/TrackingParams.kt`): `rating_bad` = tên resource của lý
  do, chọn Other thì là chữ user gõ, cả hai viết thường + khoảng trắng → `_`.
- Event riêng của từng mục MO ghi trong field `events` của catalog. Muốn dựng sheet tracking đầy đủ thì
  dùng skill `build-tracking` (nếu repo có).

### Vị trí file (A013, gốc `app/src/main/java/<pkg>/`)

| Thành phần | File |
|---|---|
| Ads + luồng FO | `ads/AdsManager.kt` (+ `ads/InterSplashClickAction.kt`) |
| Key RC / prefs | `domain/preference/SharedPrefs.kt` |
| Noti | `domain/notification/{NotificationManager, NotificationReceiver, BootReceiver, LockScreenNotiManager, LockScreenNotiType}.kt` |
| Shortcut | `domain/shortcuts/ShortcutManager.kt` |
| Màn hình | `ui/screen/<màn>/{<Màn>Screen.kt, view/<Màn>Content.kt}` (splash, language, select, onboard, uninstall, lockscreen, webview…) |
| Back + inter | `ui/base/AppBackHandler.kt` |
| Buffer native | `ui/base/BufferedNative.kt` |
| Hằng deep link | `common/Constant.kt` |
| Routing mở lại app + `app_open_from` | `MainActivity.kt` |

App khác: đặt theo cấu trúc sẵn có của app (xem `stack-adapt.md` §2). **Đừng** tạo package mới song song
với package đang có cùng vai trò.

## 3. Code

- **Luật của repo ưu tiên hơn skill.** Gồm `CLAUDE.md` và `.claude/rules/*`, vd quy trình bắt buộc kiểu
  `agent-workflow.md`, checklist ANR, luật không comment.
  - Skill chỉ bổ sung phần repo không nói tới.
  - Không theo được luật nào của repo thì ghi lý do trong báo cáo.
- Theo `CLAUDE.md` / `.claude/rules` của repo: màu lấy từ `Color.kt`/theme, không hardcode; hạn chế
  comment; dùng toolkit UI sẵn có (`Modifier.onClick`, `BaseDialog`…).
- Repo cấm comment: **không** chèn `// TODO(mo)` vào code; chỉ liệt kê TODO(mo) trong báo cáo (file + chỗ cần
  thay).
- Thiếu asset/copy/ID thật thì dựng bản chạy được, đánh `// TODO(mo): <thiếu gì>` tại chỗ, và liệt kê
  trong báo cáo.
- Đụng manifest (receiver, activity, permission, intent-filter, shortcut) thì kiểm lại merged manifest
  và quyền runtime.
- Không init SDK nặng trong `Application.onCreate` khi process dậy nền (ANR). Theo luật crash/ANR của
  repo (`crash-anr-guard` nếu có).

## 4. Không làm

- Giả mạo cảnh báo/thông báo hệ thống (MO-87), hoặc ẩn đường gỡ app thật ở màn uninstall.
- Bật lại full-screen intent mà không hỏi user, hoặc spam để lách giới hạn của Android.
- Commit/push, đổi RC trên Firebase, ghi vào sheet MO/Product Hub khi user chưa đồng ý.

## 5. Khi app chuẩn A013 thay đổi

- Skill **không lưu code**. Recipe chỉ chỉ tới file + symbol của A013; lúc làm luôn đọc code A013
  **bản hiện tại**.
- Mỗi mục ghi `canonical.verified_commit`: commit lần cuối recipe được đối chiếu. `audit.py --app a013`
  (mục có `canonical.app` khác, vd EXT-AD-LOADING → a048, thì `--app` app đó) tự so file chuẩn với commit đó
  và báo `↺` nếu đã đổi. Khi đó:
  - theo code hiện tại;
  - người bảo trì sửa lời recipe;
  - cập nhật `verified_commit` (xem SKILL.md § update-catalog).
- Danh sách tên ở §2 (hằng `OPEN_FROM_*`, placement, đường dẫn file) là ảnh chụp lúc viết. Nguồn đúng là
  `common/Constant.kt`, `app/config/ads_config.json`… của A013 hiện tại.

## 6. Mẫu báo cáo sau khi apply

```
## MO-95 — Noti lock screen · app a036 (v1.1.1) · ref: A013
Trạng thái: Done (build :app:assembleTestDebug PASS) — chưa commit

File đã đổi
- app/src/main/java/.../LockScreenNotiManager.kt (mới)
- app/src/main/AndroidManifest.xml (+ LockScreenActivity, USE_FULL_SCREEN_INTENT)

Remote config (MO tạo/kiểm trên Firebase)
| Key | Kiểu | Default | Nguồn tên |
| noti_lockscreen_enable | Boolean | true | chuẩn A013 (app chưa có) |

Placement / tracking: … (nameSpace + placement mới phải thêm cả vào ads_config trên Firebase) · Phụ thuộc đã kiểm: MO-78 (đã có)
QC: … (xem references/notifications.md § MO-95)
TODO(mo): copy 3 slot noti, ảnh minh hoạ

Thay đổi hành vi đã phát hành (cần MO/PO xác nhận trước khi release)
- … (hành vi cũ → mới, lý do, ticket cũ nếu có)

Câu hỏi mở đang theo mặc định: Q22 (không set CATEGORY_ALARM), …
Quyết định đã tự chọn (khi không hỏi được user): …
Build: baseline <lệnh> PASS/FAIL (thời gian) → sau khi sửa PASS/FAIL; file build bị bẩn (nếu có)
Lỗi ngoài phạm vi phát hiện được (nên tách ticket): …

[Nếu ref ≠ A013] Khác biệt ref aXXX vs A013
| Khía cạnh | aXXX (đã làm theo) | A013 | Nhận xét |
Nghiệm thu ref thiếu, chưa thêm (hỏi user; còn thì mục là Partial): …
Chỗ khác ref vì luật repo: …

Diff: git -C <repo> diff (hoặc đường dẫn patch nếu làm trong worktree)
Dòng cho sheet MO: MO-95 | Noti lock screen | a036 v1.1.1 | Done | chờ QC
(mục ngoài sheet: EXT-AD-LOADING (ngoài sheet) | Loading trước ad full-screen | a049 v1.0.1 | Done | …)
```

# Nhóm rating + ux

## Tổng quan nhóm

- **Rating (MO-85)**: popup đánh giá chỉ hiện sau khi user đã có trải nghiệm thành công. Số lần thành công cần đạt được chỉnh bằng RC.
- **UX**:
  - Xin quyền rõ ràng, có overlay hướng dẫn trước khi sang Settings (MO-2, MO-3).
  - Bật quyền xong thì tự quay về app (MO-90).
  - Link web mở trong app bằng webview (MO-83).
  - Ép cập nhật phiên bản (DEV-19).
- **Quy ước đường dẫn**:
  - A013: tính từ `app/src/main/java/com/example/a013_recovery/`. Res và manifest tính từ gốc repo.
  - A014: tính từ `app/src/main/java/home/ai/design/`.
  - SDK: tính từ `xTechSDK/`.
  - App khác: tính từ thư mục package gốc.
  - Luôn đọc code bản hiện tại. Tìm file theo symbol.
- **RC**: số ghi dạng Long, nên khai Long. Khai Int thì luôn trả default (chi tiết ở `inapp-ads.md` phần Tổng quan nhóm).

## MO-85 — Rating sau hơn 2 lần thành công (RC đếm số lần)

- **Yêu cầu**:
  - Popup rating chỉ hiện sau hơn 2 lần thành công (vd gen ảnh thành công, recovery thành công).
  - Ngưỡng số lần chỉnh bằng RC.
  - Ảnh tham khảo: popup "Thank you!", 5 sao, nút "Rate Us".
- **Nghiệm thu**:
  - Lần thành công thứ 1 và 2: chưa hiện.
  - Lần thứ N (RC, mặc định 3): hiện ở màn kết quả.
  - Đã rate hoặc bấm "không hỏi lại": không hiện nữa.
  - Tổng số lần hiện bị giới hạn bởi RC.
  - Không hiện đè lên ad.
- **SDK**:
  - `xtechads/.../domain/preference/AdsSharedPref.kt` có `rated` và `star_review_to_store` (mặc định 4): số sao từ ngưỡng này trở lên thì đưa user lên Play.
  - SDK không có gate hay popup rating.
- **Chuẩn của mục này = A045 `domain/rating/RatingGate.kt`** (đọc bản hiện tại, kèm `docs/features/rate-success.md`).
  A013 lệch spec; A014 đã bỏ RC đếm. Cả hai ghi ở phần "Biến thể" bên dưới.
  - **Bộ đếm lưu pref** `feature_success_count` (sống qua session). `RatingGate.onSuccessScreenViewed()` cộng 1
    rồi mới xét điều kiện. Gọi ở mỗi màn kết quả thành công thật (Clean, Compress, Swipe… → ViewModel tương ứng).
  - **Điều kiện hiện** (`isSuccessRatingDue`):
    - `rate_success` bật;
    - chưa `rated` và popup không đang mở (`canAutoPrompt`);
    - chưa hiện trong session này;
    - tổng số lần đã hiện `rating_shown_count` < `rating_max_show`;
    - lịch theo `isScheduled`: số lượt thành công ≥ `rate_success_trigger`, và nếu đã từng hiện thì phải thêm
      ≥ `rate_success_jump` lượt kể từ lần hiện trước.
  - **Nhánh Home theo session** (`onHomeVisible`, RC `rate_home` / `rate_home_session` / `rate_home_jump`):
    rating theo số session. Không thuộc yêu cầu MO-85 nhưng dùng chung gate. Làm hay không tuỳ MO.
  - **Popup** host ở `ui/navigation/AppNavigation.kt` theo `RatingGate.visible`. `show()` tăng
    `rating_shown_count`, `onRated()` set `rated`.
  - **Ngưỡng "hơn 2 lần":** `isScheduled` dùng `≥`, nên default trong code A045 `rate_success_trigger = 2` cho
    popup hiện ở **lượt thứ 2**. Đúng chữ của sheet thì MO đặt `rate_success_trigger = 3`. Xác nhận với MO
    trước khi đổi default.
- **Biến thể / lệch ở app khác:**
  - **A014 (sheet ghi "default success 3 lần" là bản cũ):**
    - Code hiện tại (`ResultScreen.onBackFunc`) chỉ cần ≥1 lần gen thành công trong session. Biến đếm
      `AppScreenState.successfulGenerationCount` nằm trong RAM.
    - Gate thêm `rating_show_count` < `rating_max_show`, chưa submit, chưa "không hiện lại".
    - RC `rating_dialog_trigger_count` (mặc định 3, đếm lưu pref `successful_generation_count`) đã bị bỏ ở
      commit `b00b624`.
  - **A013:**
    - `SharedPrefs.checkAndShowRating`: tối đa 1 lần/ngày, không đếm.
    - Điểm gọi ở `ScanSuccessScreen` (`show_rating_at_success`) và `CompressViewModel` (`show_rating_at_compress`).
    - Popup `RatingPopupNew` ở `AppNavigation`.
    - Nhánh không hài lòng không set `rated`, nên hôm sau vẫn hỏi lại.
  - **Duo-Speak (a041):** `core/common/.../RatingGate.kt`, 1 lần/session, không đếm.
- **Remote config** (tên chuẩn theo A045):
  - `rate_success` (Boolean, `true`): bật rating sau thành công.
  - `rate_success_trigger` (Long, `2` trong code; spec "hơn 2 lần" ⇒ MO đặt `3`): số lượt thành công tối thiểu.
    - Alias: `rating_dialog_trigger_count` (A014 bản cũ, mặc định 3).
    - Alias: `rating_min_success` (A045 bản cũ).
  - `rate_success_jump` (Long, `1`): số lượt thành công phải thêm giữa 2 lần hiện.
  - `rating_max_show` (Long, A045 `3`, A014 `2`): trần tổng số lần hiện. A47 khai Int nên RC không có tác dụng.
  - Key cũ cùng ý nghĩa bật/tắt: `show_rating_at_success` / `show_rating_at_compress` (A013), `show_rating` (a037, a039).
  - `star_review_to_store` (Long, `4`, SDK): số sao từ ngưỡng này trở lên thì đưa user lên Play.
- **Placement / tracking**:
  - `rate_app` (param `rate_value`).
  - `rating_dialog_show` (A014).
  - `star_rating_<n>` (A013).
  - Overlay `OvlRatingShow` (A045).
- **Cách làm**:
  1. **Bộ đếm thành công**:
     - Lưu pref để sống qua session. Không giữ trong RAM như A014 hiện tại.
     - +1 đúng 1 lần ở mỗi kết quả thành công thật.
     - Đọc A045 `RatingGate.onSuccessScreenViewed` (bản hiện tại) và các ViewModel gọi nó.
  2. **Gate**:
     - Đếm ≥ RC trigger, show_count < `rating_max_show`, chưa submit, chưa "không hiện lại".
     - Thêm giới hạn 1 lần / session nếu MO muốn.
     - Đọc A045 `RatingGate` (bản hiện tại): `isSuccessRatingDue`, `isScheduled`, `show`, `onRated`.
  3. **Điểm hiện**:
     - Ở màn kết quả, sau khi kết quả đã hiện ra (hoặc lúc rời màn như A014).
     - Không hiện khi đang có ad hoặc dialog quyền.
  4. **Popup**:
     - Sao ≥ `star_review_to_store`: mở Play (hoặc In-App Review API).
     - Sao thấp hơn: form feedback.
     - Lưu cờ `rated` / submitted.
  5. **App XML**: cùng logic, popup là DialogFragment.
- **Bẫy**:
  - Bộ đếm trong RAM thì reset mỗi session, nên "hơn 2 lần" không bao giờ tính dồn qua các session.
  - RC số khai Int thì luôn trả default (A47 `rating_max_show`).
  - Popup bung đúng lúc inter đang hiện thì bị che hoặc làm user bấm nhầm.
  - Đã rate ở Setting thì cũng phải tính là đã rate.
- **QC**:
  - Làm thành công 1, 2, 3 lần, có kill app ở giữa.
  - Rate 5 sao: mở Play. Rate 2 sao: không mở Play.
  - Bấm "không hiện lại".
  - Chạm trần `rating_max_show`.
  - Đổi RC trigger.

## MO-2 — Overlay hướng dẫn xin quyền trước khi sang Settings

- **Yêu cầu**:
  - Quyền phải tự bật trong Settings (All files, full-screen intent, usage access…) thì trước đó phải có overlay riêng của app (không phải dialog hệ thống).
  - Overlay giải thích lý do và minh hoạ cái toggle cần bật, rồi mới chuyển sang Settings.
  - Figma `602-3121` (ScrPermission). Ảnh tham khảo: popup "Enable Usage Access" có hình toggle ON, nút CANCEL / OPEN SETTINGS.
- **Nghiệm thu**:
  - Bấm tính năng cần quyền: hiện overlay (có hình toggle).
  - Bấm Allow: sang đúng trang Settings, trên đó có tip "tìm <app> và bật lên".
  - Bật quyền xong: tự về app (MO-90).
  - Không tự hiện app-open resume sau đó.
- **Chuẩn A013**:
  - **All files** (`ui/base/dialog/RequestAllFilesOverlay.kt`):
    - Bottom sheet `OvlStoragePermission`.
    - Có hàng giả lập Settings "All Files Access": logo app + tên app + gợi ý + ảnh toggle `ic_switch_on`.
    - Có native ad placement `permission`.
    - User từng từ chối (`onboardPermissionDenied`) thì 2 nút đổi thành "Not now" / "Open settings" (`openSettingsMode`).
    - Allow: mở `ReadAllFileSettings` (`common/ActivityResultContracts.kt`), rồi `checkSettingAllFileOn()`.
    - Overlay được dùng ở `HomeScreen`, `JunkRemoverScreen`, `ScanScreen`, `StorageDetailScreen`.
  - **Notification / full-screen intent**:
    - `ui/base/dialog/PermissionPromptDialog.kt` là popup trước khi xin quyền: overlay `OvlNotiPermission` / `OvlFSPermission`, có Allow và Not now.
    - Allow gọi `utils/PermissionSettingsGuide.open(activity, intents, showTip, onResult, isGranted)`.
    - Sau `TIP_DELAY_MS`, `PermissionSettingsGuide` mở `ui/screen/permission/PermissionTutActivity.kt` đè lên Settings:
      - Activity trong suốt, overlay `OvlPermissionTut`.
      - Chuỗi `permission_tut_tip` = "Tip: Find %1$s and turn it on".
      - Chỉ mở khi Settings đang nằm trên task của app (`isSettingsOnTopOfTask`).
    - Danh sách intent dự phòng ở `common/PermissionUtils.kt`: `appNotificationSettingsIntents()`, `fullScreenIntentSettingsIntents()`.
- **Mẫu khác**:
  - a016 `ui/base/PermissionScreen.kt` (`PermissionScreenOverlay`, `PermissionBottomSheetState`, overlay `OvlPermission`; RC `showPermissionSheetHome`).
  - a034 `ui/common/PermissionBottomSheet.kt`.
  - A014 `ui/dialog/PermissionSettingsDialog.kt`.
  - A47 `ui/dialog/FsPermissionDialog.kt` (`OvlFSPermission`).
  - a037 `ui/dialog/NotiPermissionDialog.kt`.
- **Remote config**: `full_scr_intent_guide` (Boolean, `true`): `false` thì bỏ tip khi mở trang full-screen intent. Trang notification vẫn có tip.
- **Placement / tracking**:
  - Overlay: `OvlStoragePermission`, `OvlNotiPermission`, `OvlFSPermission`, `OvlPermissionTut`.
  - Native ad trong sheet: `permission`.
  - Kết quả full-screen intent: `fs_permission_allow` / `fs_permission_exit` / `fs_permission_back`.
- **Cách làm**:
  1. **Overlay theo Figma**: tiêu đề, lý do, hình hàng Settings với toggle ON (dùng logo và tên app), nút Allow / Not now. Đọc `RequestAllFilesOverlay` và `PermissionPromptDialog` ở A013.
  2. **Allow → mở Settings**:
     - Mở từ Activity, KHÔNG thêm `FLAG_ACTIVITY_NEW_TASK`.
     - Gọi `disableAdResumeOnTime()` trước.
     - Thử lần lượt các intent trong danh sách dự phòng.
     - Đọc `PermissionSettingsGuide.open` ở A013.
  3. **Tip đè lên Settings** (tuỳ chọn): Activity trong suốt, KHÔNG phải `AdHostActivity`. Đọc `PermissionTutActivity` và khai báo của nó trong manifest A013.
  4. **Theo dõi để tự về app**: theo MO-90.
  5. **App XML**: overlay là BottomSheetDialogFragment (a031 có style `PermissionBottomSheetDialog`), luồng giữ nguyên.
- **Bẫy**:
  - Mở Settings với `NEW_TASK` thì Settings nằm ở task riêng, Android chặn mở tip (background activity start).
  - Activity tip: không set `launchMode` / `taskAffinity` (phải vào cùng task với Settings), không set `screenOrientation` (trong suốt + khoá hướng sẽ crash trên API 26–27). Cả hai đều có ghi chú trong manifest A013.
  - Một số ROM vẫn mở Settings ở task riêng. Khi đó đừng mở tip, vì tip sẽ kẹt lại trong task app và bật ra khi user quay về.
  - Panel `android.settings.panel.*` không đưa app xuống nền. Đừng bật cờ skip-resume cho panel, nếu không cờ sẽ ăn mất lần resume thật kế tiếp.
- **QC**:
  - Pixel và ít nhất 1 ROM (Xiaomi / Samsung).
  - Lần đầu và lần đã từ chối.
  - Bật quyền: tự về app. Không bật: bấm back về app.
  - Không có ad resume.
  - Light và dark.

## MO-3 — Overlay xin quyền notification, có nút Allow

- **Yêu cầu**:
  - Overlay xin quyền thông báo rõ ràng, hiển thị đầy đủ, có nút Allow.
  - Figma `602-3909`.
- **Nghiệm thu**:
  - Lần đầu: hỏi quyền đúng thời điểm theo RC (Splash hoặc Home).
  - Bị chặn vĩnh viễn: overlay của app với Allow → Settings (kèm tip) → tự về app.
  - Mỗi session hỏi tối đa 1 lần.
  - Không bao giờ hiện đè lên ad.
- **Chuẩn A013**:
  - **Ở Splash** (`ui/screen/splash/SplashScreen.kt`): hỏi bằng dialog hệ thống nếu đủ 4 điều kiện:
    - RC `noti_permission_trigger` = `"splash"`,
    - chưa hỏi lần nào,
    - chưa có quyền,
    - không cần rationale.
  - **Ở Home** (`ui/screen/home/view/HomePermissionPrompts.kt`):
    - Hỏi khi trigger = `"home"`, hoặc Splash đã dùng hết lượt hỏi.
    - Tối đa 1 lần / session (`noti_prompt_session`).
    - Chỉ hỏi khi Home thật sự ở trước và không có ad.
    - Hỏi bằng dialog hệ thống trước. Nếu Android trả kết quả mà không hiện dialog (bị chặn vĩnh viễn; nhận ra vì activity không bị pause) thì hiện `PermissionPromptDialog` overlay `OvlNotiPermission` (`noti_permission_title` / `noti_permission_desc`). Allow → Settings có tip → tự về app.
  - Có quyền rồi:
    1. `setReminderPinned` (noti ghim).
    2. Mời bật quyền full-screen intent: RC `full_scr_intent`, `full_scr_intent_retrigger`.
  - **Lệch / cần chốt**:
    - A013 không có overlay TRƯỚC dialog hệ thống ở lần hỏi đầu.
    - Nếu Figma `602-3909` yêu cầu overlay trước thì phải thêm 1 bước: overlay → Allow → dialog hệ thống.
- **Mẫu khác**:
  - a034 `ui/screen/reward/view/BtsNotiPermission.kt` (`OvlNotiPermission`).
  - a037 `ui/dialog/NotiPermissionDialog.kt`, gọi ở BoostScreen. Theo sheet: không có Allow, chỉ có nút mở Settings.
  - A47 `common/utils/NotificationPermission.kt`.
- **Remote config**:
  - `noti_permission_trigger` (String, `"splash"`): `"splash"` hoặc `"home"`.
  - Liên quan: `full_scr_intent` (Boolean, `false`), `full_scr_intent_retrigger` (Long, `2`), `full_scr_intent_guide` (Boolean, `true`).
- **Placement / tracking**: overlay `OvlNotiPermission`, kèm `button_click` của Allow / Not now.
- **Cách làm**:
  1. **Chọn thời điểm hỏi theo RC**: Splash hay Home. Đọc `SplashScreen` (`notificationPermissionLauncher`) và `HomePermissionPrompts` ở A013.
  2. **Dialog hệ thống trước**:
     - Gọi `needSkipResume()` ngay trước khi hỏi.
     - Nếu không có pause (Android không hiện dialog) thì hạ cờ skip-resume rồi hiện overlay.
  3. **Overlay → Settings**: dùng `PermissionSettingsGuide` (MO-2, MO-90).
  4. **Có quyền**: bật các noti phụ thuộc quyền (pinned…) ngay.
- **Bẫy**:
  - `POST_NOTIFICATIONS` chỉ có từ API 33. Máy cũ coi như đã có quyền.
  - Dialog hệ thống làm Activity pause, nên có thể kéo theo app-open resume. Phải skip.
  - Hỏi lúc inter splash đang hiện thì dialog hệ thống đè lên ad (A013 chờ Home thật sự ở trước).
  - Android chỉ cho từ chối 2 lần. Sau đó chỉ còn đường Settings.
- **QC**:
  - API 33+ cài mới: thử cả 2 RC trigger.
  - Từ chối 2 lần rồi mở lại: hiện overlay.
  - Allow → Settings → bật → tự về app.
  - API < 33: không hỏi.

## MO-83 — Mọi link website mở trong webview của app

- **Yêu cầu**:
  - Mọi hành động mở website đều mở trong màn webview của app, để tăng engagement time và cải thiện chỉ số vitals trên store.
  - Ví dụ: Terms of Service. Các link khác check riêng từng app.
  - Theo sheet, các app đang mở TOS / PP ra ngoài: a016 / a27 (ở paywall), a018, a031, a032, a033.
- **Nghiệm thu**:
  - TOS, Privacy và mọi link web (paywall, setting, about…) đều mở màn webview có header back.
  - Link Play Store, mail, share vẫn mở app ngoài.
  - Ở webview không có app-open resume.
- **Chuẩn A013**:
  - `ui/screen/webview/WebViewScreen.kt`, destination `AppDestination.ScrWebview(isTOS)`.
  - URL lấy từ `common/Constant.kt` `TOS_LINK` / `PRIVACY_LINK`. Setting điều hướng tới `ScrWebview`.
  - `ScrWebview` nằm trong `AdsManager.screenSkipAdResume`. Tracking `TrackingScreenName("ScrWebview")`.
  - Mở ra ngoài (đúng chuẩn):
    - `Context.openWebsite()` (`utils/AppUtils.kt`): dùng cho promotion ở Home (`prefs.appRefer`, RC `app_refer`, link Play).
    - `RatingUtil.sendToStore` (`market://`).
    - `shareApp`.
  - **Lệch chuẩn**:
    - Màn chỉ nhận Boolean TOS / Privacy, không mở được URL bất kỳ.
    - Loading indicator không bao giờ hiện: `isLoading` khởi tạo false và không có chỗ nào set true.
    - Không xử lý lịch sử trang trong WebView: back là thoát màn.
- **Mẫu tổng quát (A045)**:
  - `Dest.ScrWebview(type: PolicyType, url, title)` + `ui/screen/webview/state/WebviewState.kt` (`urlOverride`, `titleOverride`, `screenTag` theo từng loại policy).
  - Link ngoài: `common/Commons.kt` `openPlayStore` / `rateApp` dùng `market://` có fallback web, và gọi `disableAdResumeOnTime()` trước.
- **Placement / tracking**: screen `ScrWebview`. A045 log screen riêng cho từng loại policy.
- **Cách làm**:
  1. **Destination webview tổng quát**: nhận `url` + `title` (và loại policy nếu muốn tracking riêng). Đọc `WebViewScreen` ở A013 và `Dest.ScrWebview` / `WebviewState` ở A045.
  2. **Grep mọi chỗ mở web ra ngoài**: `Intent.ACTION_VIEW` với `http(s)://`, `openWebsite`, `openUrl`, `CustomTabs`. Đổi thành điều hướng tới webview. Paywall cũng phải đổi.
  3. **Giữ ra ngoài** các link: Play / `market://`, `mailto:`, share, deep link app khác.
  4. **Thêm `ScrWebview` vào `screenSkipAdResume`**, và gắn tracking màn.
  5. **App XML**: Activity / Fragment webview riêng, luồng giữ nguyên.
- **Bẫy**:
  - Bên trong trang web có thể có link `market://` hoặc `intent://`. Phải chặn ở `shouldOverrideUrlLoading` rồi mở ra ngoài, nếu không WebView sẽ báo lỗi.
  - Có loading và trạng thái mất mạng.
  - Bật JS chỉ khi cần.
  - Huỷ WebView khi rời màn (A013 có `destroy()` trong `onDispose`).
- **QC**:
  - Từng link: Setting, paywall, onboarding, about.
  - Back.
  - Mất mạng.
  - Link Play vẫn mở Play.
  - Không có ad resume.

## MO-90 — Bật quyền trong Settings xong thì tự quay về app

- **Yêu cầu**:
  - User bật quyền trong Settings thì app tự quay lại, không cần user bấm back.
  - Hiện nhiều app vẫn bắt user tự bấm back.
- **Nghiệm thu**:
  - Bật toggle: trong khoảng 1s app tự lên lại, đúng màn trước đó, tính năng chạy tiếp.
  - Không bật mà bấm back: về app bình thường.
  - Không bị nhảy về app lúc user đã rời Settings đi chỗ khác.
- **Chuẩn A013**:
  - **`utils/PermissionSettingsGuide.kt` (`open` → `watch`)**:
    - Sau `POLL_START_MS` (1s), cứ `POLL_INTERVAL_MS` (200ms) kiểm tra `isGranted` 1 lần, tối đa `POLL_MAX_ATTEMPTS` (300 lần, khoảng 60s). Các binder call chạy ngoài main thread.
    - Có quyền mà Activity chưa RESUMED thì start `MainActivity` (singleTask) với `NEW_TASK`. Settings và tip bị đẩy khỏi task.
    - Báo `SettingsResult`: `Granted` / `LeftWithoutGrant` / `BackWithoutGrant`.
    - User tự quay về thì dừng theo dõi. Nhờ vậy nếu sau đó user mới bật quyền thì app không bị kéo lên.
  - **All files**: `HomeScreen.checkSettingAllFileOn()` (bản tương tự có ở `JunkRemoverScreen`, `PreviewLibraryScreen`, `ScanScreen`, `StorageDetailScreen`):
    - Kiểm tra `Environment.isExternalStorageManager()` mỗi 200ms, bắt đầu sau 1s, tối đa 300 lần.
    - Có quyền thì start `MainActivity` với `NEW_TASK`.
- **Mẫu ở app khác**:
  - Helper `checkSettingOn(context, isGranted)` + `FLAG_ACTIVITY_REORDER_TO_FRONT | FLAG_ACTIVITY_NEW_TASK`:
    - A014 `utils/PermissionUtils.kt`.
    - a016 `common/PermissionUtils.kt`.
    - a27.
    - a034 `util/PermissionUtils.kt`.
    - a044 / A045 `common/utils/SettingsReturn.kt`: timeout 60s, chạy trên `lifecycleScope`.
  - A045 `ui/properties/AppSettingsLauncher.kt`:
    - `rememberSettingsLauncher(action, grantedCheck, onReturn)`: tắt resume một lần, mở Settings qua launcher, kèm `checkSettingOn`.
    - `openWifiSettings`.
  - Biến thể: A47 `common/utils/NotificationPermission.kt` (REORDER_TO_FRONT | SINGLE_TOP); A028 `ScrCastDocumentViewModel.checkSettingAllFileOn`.
- **Cách làm**:
  1. **1 helper dùng chung**: mở Settings (từ Activity, không NEW_TASK) + `disableAdResumeOnTime()` + bắt đầu theo dõi `isGranted`. Đọc `PermissionSettingsGuide` ở A013.
  2. **Theo dõi**:
     - Chạy coroutine ngoài main thread.
     - Bắt đầu sau 1s, kiểm tra mỗi 200ms, timeout khoảng 60s.
     - Dừng khi user tự quay về (ON_RESUME) hoặc Activity bị destroy.
  3. **Có quyền**:
     - Start Activity chính với `NEW_TASK` (Activity singleTask), hoặc `REORDER_TO_FRONT`.
     - Màn gọi nhận kết quả lúc resume rồi chạy tiếp tính năng.
  4. **App XML**: helper giống hệt, gọi từ Activity / Fragment.
- **Bẫy**:
  - **Giới hạn mở Activity từ nền (Android 10+)**: kéo app về chỉ chắc chắn được khi Settings được mở từ Activity của app và nằm cùng task (ghi chú trong `PermissionSettingsGuide` A013). Mở Settings với `NEW_TASK` thì tip bị chặn. Phải test trên Android mới.
  - **Android 14+** đóng băng app khoảng 10s sau khi cửa sổ cuối biến mất, nên việc polling bị treo (ghi chú trong A013). Lúc đó chỉ còn cách user tự quay về và màn kiểm tra lại lúc resume.
  - Không dừng theo dõi khi user đã về tay: lần bật quyền sau đó sẽ kéo app lên bất ngờ.
  - Quyền có dialog hệ thống (camera, POST_NOTIFICATIONS lần đầu) không cần cơ chế này.
- **QC**:
  - Android 10, 13, 14, 15. Pixel và Xiaomi / Samsung.
  - Bật ngay. Bật sau 30s. Rời Settings sang app khác rồi mới bật. Không bật mà bấm back.

## DEV-19 — Force update: ép user cập nhật lên bản mới nhất

- **Yêu cầu**: khi cần, ép user đang dùng bản cũ cập nhật lên bản mới nhất ngay trong app.
- **Nghiệm thu**:
  - Bản bị ép (RC) mở app: hiện màn update Immediate của Play.
  - Bấm X: app chặn bằng dialog của app (chỉ còn nút Update).
  - Bản không bị ép: Flexible tải nền, xong thì có dialog Restart.
  - Offline hoặc không có Play: app chạy bình thường, Splash không bị treo.
- **SDK**: module riêng `:xtechupdate` (`com.xtech.sdk:xtechupdate`, `UPDATE_VERSION` 1.0.0). Đọc `xTechSDK/docs/IN_APP_UPDATE_USAGE.md`. Thành phần:
  - `InAppUpdateManager`:
    - Hàm: `checkUpdate(launcher)`, `resumeUpdate(launcher)`, `onUpdateResult(code)`, `completeUpdate()`, `startListening()` / `stopListening()`.
    - State: `status`, `canProceed`, `readyToInstall`.
  - `InAppUpdateConfig`: chỉ chứa callback (`onUpdateDeclined`, `onReadyToInstall`, …).
  - `InAppUpdateStatus`.
  - `inAppUpdateModule(config)`: module Koin, app tự thêm vào `startKoin`.
  - RC do module tự đọc (`xtechupdate/.../UpdateSharedPref.kt`), xem phần Remote config bên dưới.
  - `LicenseGuard`: applicationId phải nằm trong `allowedPackages()` của `xtechupdate/build.gradle.kts` và publish lại version SDK. Nếu không, `InAppUpdateManager` sẽ ném lỗi ngay lúc khởi tạo.
- **Chuẩn A013**: KHÔNG có.
- **Hiện trạng ở các repo khác**:
  - Không app nào trên máy này dùng `xtechupdate`. Chỉ app demo của SDK có:
    - `app/.../App.kt`,
    - `AppNavigation.kt`,
    - `ui/screen/splash/SplashScreen.kt`,
    - `ui/base/dialog/UpdateReadyDialog.kt`.
  - Doc SDK mô tả bản A016 đang chạy thật (key app cũ `enable_in_app_update`, `force_update`), nhưng các branch a016 trên máy không có.
  - Langofy tự viết `app/.../InAppUpdateManager.kt` (luôn IMMEDIATE, không RC). a031 có `utility/AppUpdateUtils.kt`.
- **Remote config**:
  - `in_app_update_enabled` (Boolean, `true`): công tắc tắt toàn bộ. Có tác dụng từ lần mở app sau.
  - `in_app_update_immediate_priority` (Long, `4`): ngưỡng priority.
    - `0` = mọi bản đều Immediate.
    - `1`–`5` = Immediate khi priority (set lúc publish qua Play Developer API) ≥ ngưỡng.
    - Lớn hơn `5` = luôn Flexible.
  - `in_app_update_timeout_ms` (Long, `5000`): Play không trả lời trong khoảng này thì `FAILED`.
  - Alias (A016 theo doc): `enable_in_app_update`, `force_update` (cùng ý nghĩa ngưỡng).
  - Muốn ép đúng version nào thì dùng RC condition theo app version.
- **Placement / tracking**: callback trong `InAppUpdateConfig` (accepted / declined / failed…) để app tự log.
- **Cách làm** (theo §5 của doc SDK):
  1. **Chuẩn bị**: thêm dependency, nhờ SDK owner whitelist applicationId, thêm `inAppUpdateModule(InAppUpdateConfig(...))` vào Koin.
  2. **Đặt global trong `AppNavigation`** (đọc bản demo `AppNavigation.kt` của SDK):
     - Launcher `StartIntentSenderForResult`, trong callback gọi `onUpdateResult`.
     - `startListening` / `stopListening`.
     - `resumeUpdate` trong `LifecycleResumeEffect`.
     - `UpdateReadyDialog(readyToInstall)` → `completeUpdate`.
  3. **Splash**: gọi `checkUpdate`, và chặn load ad cho tới khi `canProceed` (dùng `snapshotFlow` khi ở trong coroutine). Đọc `SplashScreen.kt` demo.
  4. **Force**:
     - Đã thấy `IMMEDIATE` mà user bấm X (`onUpdateDeclined`) → bật cờ, hiện `ForceUpdateDialog` không đóng được, chỉ có nút Update (gọi lại `checkUpdate`).
     - Play không tự đóng app khi user bấm X.
  5. **App XML**: launcher và dialog đặt ở Activity chính, logic giữ nguyên.
- **Bẫy**:
  - Quên gọi `onUpdateResult` → `canProceed` kẹt false, Splash treo.
  - `FAILED` / `DISABLED` phải cho đi tiếp. Tự đổi thành chặn thì máy offline sẽ treo Splash vĩnh viễn.
  - Ngưỡng hardcode chỉ có tác dụng từ bản build sau, nên phải đọc từ RC.
  - Test:
    - RC cache 3600s, test thì `pm clear` hoặc giảm `minimumFetchIntervalRc`.
    - Internal App Sharing luôn trả priority 0.
    - Có thể dùng `FakeAppUpdateManager` qua tham số thứ 2 của `inAppUpdateModule`.
  - Chưa whitelist applicationId thì crash ngay lúc khởi tạo.
- **QC**:
  - Internal App Sharing: dựng bản cao hơn, thử ngưỡng 0 / 4 / 6.
  - Bấm X ở màn Immediate.
  - Flexible: tải xong, Restart.
  - Offline.
  - Kill app giữa lúc đang tải.

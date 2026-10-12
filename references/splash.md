# Splash — consent, ads splash, điều hướng FO (MO-21..MO-31, MO-84, MO-96, MO-97, MO-99, DEV-3)

> Recipe đối chiếu lần cuối với A013 commit `f784827` (branch v1.2.7, xtechads 1.8.2). Skill **không chép code**: chi tiết code đọc từ A013 bản hiện tại theo file + symbol nêu dưới.
> Mã app theo `apps.json`: a27 = a027, A47 = a047, Langofy = a042, qibla = a031, Duo-Speak = a041, PDF Reader = a033, A014/A028/A045 = a014/a028/a045.
> Quy ước đường dẫn: file Kotlin A013 tính từ `app/src/main/java/com/example/a013_recovery/`; manifest/res/gradle/config tính từ gốc repo. App khác: tính từ package gốc của app (tìm theo tên file + symbol; thư mục repo ở `apps.json`).

## Tổng quan nhóm

**Dòng thời gian splash ở A013:**
1. `MainActivity.onCreate`: `AdsManager.resetState()` (reset unit splash đang `FAIL`/`IMPRESSED`, cờ click, `InterSplashClickAction`), mở mới thì xoá `TrackingState.lastScreen` về rỗng + tăng `sessionNumber`; `setContent` (back stack bắt đầu ở `AppDestination.ScrSplash`); `requestUMP(...)`. Mở từ ngoài (noti, widget, shortcut, ACTION_VIEW) khi app đang sống → `onNewIntent` khởi động lại task (CLEAR_TASK) để splash chạy lại.
2. Composable `SplashScreen` (`ui/screen/splash/SplashScreen.kt`): `DisposableEffect` gọi `disableAdResumeOnTime()` (không app-open trên splash); `BackHandler` nuốt mọi back.
3. Khi `consentFinished`: (a) hỏi `POST_NOTIFICATIONS` (1 lần, theo RC `noti_permission_trigger`) → `passedNotificationSplash = true`; (b) khi có mạng: `AdsManager.loadSplashAds` (native `bottom_splash` + inter `splash`, hoặc bộ high-floor cho FO).
4. `LifecycleResumeEffect` key theo trạng thái các unit splash + `passedNotificationSplash` + `hasWindowFocus` + `connected` → `AdsManager.splashAction()` trả `SplashAction`: `Waiting` | `ShowInter(unit)` | `ShowNativeFull` | `LoadInterAll` | `None`.
5. Có kết quả lần đầu → `AdsManager.loadNativeNextSplash` (preload native màn kế) → show inter (điều hướng ngay `onAdShow`, màn kế dựng sau lưng ad) / native full splash có đếm ngược / không có ad → progress chạy nốt 100% rồi `goNextScreen`.
6. `goNextScreen` (cờ `navigated` chống gọi 2 lần): mở từ shortcut uninstall → `Uninstall`; FO (`prefs.firstOnboard`) → `AdsManager.nextSplash` (RC `splash_next`); còn lại → `ScrHomeApp`; luôn pop `ScrSplash`.
7. Toàn app: mất mạng → `OvlNoInternet` (root `AppNavigation`); splash đứng chờ (progress không chạy, không load/show).

**RC dùng ở splash (A013 → alias app khác):**
- `splash_next` (String, `language`): màn sau splash ở FO → `navigationFlow` key `splash_next` trong `ads_config` (A045, A014, A47, a033, a034, a037, a039, a044, a27); `splashNext` (a016).
- `noti_permission_trigger` (String, `splash` | `home`) → `ask_noti_permission_at_home` (Boolean, true — A014).
- `native_splash_high_logic` (Boolean, true): luồng high-floor cho FO → cùng tên ở A045, a034.
- `logic_pass_splash` (String, `reload` | `auto_next` | `keep_state`): hành vi sau khi click inter splash rồi quay lại → A045 mặc định `auto_next`, a034 `reload`.
- `fs_splash_close_second` (Long giây, 5) / `fs_splash_auto_next_second` (Long giây, 5): native full splash → A045 `native_fs_splash_countdown_time` (10) / `native_fs_splash_auto_pass_time` (15); a034 `nfs_splash_time_to_countdown` (5), `nfs_splash_countdown_to_close` (15), `nfs_splash_time_auto_pass` (30); A014 `fsn_auto_next_splash` (5); a27 `time_close_FS_splash` (3).
- Khác: a033 `inter_splash_timeout_second` (20), base project `splash_timeout_seconds` (20), a27 `splash_ad_type` (`inter` | `inter_aoa`), A045/A014 `use_new_logic_inter_noti` (MO-99).

**Placement splash:** A013 `splash` (waterfall `inter_splash_high` → `inter_splash`), `inter_splash_high`, `native_full_splash`, `inter_splash_all`, `inter_splash_backup_high`, `inter_splash_backup`, `bottom_splash` (native dưới progress). Alias: `inter_splash` (a016, a039), `app_open_splash` (a016, A014, a034), `fs_splash` (A014, a033), `native_fsplash` / `native_splash` / `banner_splash` (a016), `splash_2f` (a27), `splash_o` / `inter_o_splash` / `splash_r2` / `splash_r3` (MO-99).

**Event:** `screen_show` `ScrSplash` / `ScrNativeFullSplash`; `tracking_consent` (`status`); `sdk_init` (`sdk_key`, `sdk_duration`, `status`) với `ump_finish`, `mobile_ads_finish`, `remote_config`, `appsflyer` (SDK), `notification_finish`, `utm` (A013 `common/SdkInitTracker.kt`), `splash_load` / `splash_show` / `splash_close` (A045), `splash_load` (a033); `iaa_*` của placement splash; `overlay_show` `OvlNoInternet`, `button_click` `BtnEnableInternet`, `enable_internet_wifi` / `enable_internet_3g` / `enable_internet_not`; `button_click` `BtnContinueToApp` (native full splash).

**App không xtechads:** A028/a036 (`ui/screen/splash/SplashScreen.kt` + `BaseAds` riêng: `consentFinished`, `initFinished`, `isConnected`), a041 (`feature/firstflow/.../first_open/screen/splash/SplashScreen.kt`, `core/ads`) — cùng cấu trúc cổng load/show, khác tên.

## MO-21 — Splash riêng: logo app + progress bar

- **Yêu cầu:** Màn splash của app (sau system splash) có logo + tên app, progress bar kèm % và dòng "This action may contain ads"; là điểm vào của mọi lần mở app.
- **Nghiệm thu:** thấy logo/tên app; bar chạy, có %; có disclaimer ads; native dưới (nếu MO bật `bottom_splash`) chỉ hiện sau consent; composable có `@Preview`.
- **SDK:** `NativeBannerGroupView` cho native dưới; phần còn lại ở tầng app.
- **Chuẩn A013:** `ui/screen/splash/view/SplashContent.kt` composable `SplashContent(isConsent, finishing, onFinished)`: Lottie `ani_splash` full màn (chứa logo/tên) trên nền gradient; cột dưới gồm chữ `loading` + %, thanh 8dp bo góc, chữ `this_action_may_contain_ads`, `NativeBannerGroupView` placement `bottom_splash` khi `isConsent`. Progress là `Animatable` chỉ chạy khi có mạng: tới 99% trong 4s; `finishing` → 100% trong 250ms rồi gọi `onFinished`.
- **Cách làm:** UI theo Figma của app (sheet: đã có UI cho A038/A039/A040); tách `SplashContent` thuần UI và `SplashScreen` wiring; progress chỉ trang trí — không được gate việc show ad/điều hướng (MO-84); kèm `@Preview`. Đọc `SplashContent` ở A013 bản hiện tại để lấy chi tiết. XML/Activity: `SplashActivity` + `ProgressBar`, cùng nguyên tắc.
- **Bẫy:** progress giả có mốc cố định (chạy 70% trong 3s rồi mới cho show) tạo floor thời gian (a036 cũ, `a036 docs/splash-optimize-a013.md`); bar đầy 100% mà vẫn chờ ad → user tưởng treo; native dưới render trước consent = request trước UMP (MO-9).
- **QC:** mở app có mạng: logo, bar tăng, disclaimer (ảnh `assets/refs/MO-21-1.jpg`); tắt mạng: bar đứng + popup no-internet (MO-26).

## MO-22 — Consent đồng ý → init AdMob/Meta → load ads + noti

- **Yêu cầu:** Chỉ khi luồng consent kết thúc mới: init AdMob (kèm adapter Meta), bắt đầu load ads splash và hỏi quyền notification. Consent gửi Firebase/Facebook phải phản ánh lựa chọn thật của user.
- **Nghiệm thu:**
  - Không ad request, không hỏi noti trước `consentFinished`; `initMobileAds` sau UMP.
  - Firebase consent mode khớp lựa chọn: user EEA tắt hết ở "Manage options" → `ad_storage`/`ad_user_data`/`ad_personalization` = DENIED.
  - `tracking_consent` có `status`.
- **SDK:** `consentFinished`, `mobileAdsFinish`, `consentResult` (`accepted` | `partial` | `rejected` | `not_applicable` | `unknown`, đọc `IABTCF_gdprApplies` + `IABTCF_PurposeConsents`; rejected = Purpose 1 bị từ chối), `umpAllowed`, event `tracking_consent`.
- **Chuẩn A013:** `SplashScreen` có 2 khối theo `consentFinished` (hỏi noti; load splash khi có mạng); `App.kt` `initFCM` chờ `consentFinished` rồi bật Crashlytics/Analytics và set consent. Load splash **không** chờ `mobileAdsFinish` (chạy song song `MobileAds.initialize`) từ v1.2.6, commit `ba0a17b`.
- **Cách làm:**
  1. Gate load ad + hỏi noti theo `consentFinished` (đọc `SplashScreen` ở A013 bản hiện tại).
  2. Map consent Firebase theo kết quả thật, không set GRANTED cứng. Đề xuất (mapping purpose tham khảo A028 `ads/base/ConsentHelper.kt` và cách Google map TCF → consent mode): `IABTCF_gdprApplies` ≠ 1 → GRANTED cả 4; nếu áp GDPR: `ad_storage` theo Purpose 1, `ad_user_data` theo Purpose 1 + 7, `ad_personalization` theo Purpose 3 + 4, `analytics_storage` theo Purpose 1 (cần MO/legal chốt). Mức tối thiểu: GRANTED khi `consentResult` là `accepted`/`not_applicable`, DENIED khi `rejected`, `partial` thì theo purpose. Set lại mỗi lần mở app sau `consentFinished`. Manifest `google_analytics_default_allow_*` nên để false cho các tín hiệu ads (cần MO xác nhận vì ảnh hưởng data trước khi UMP xong).
  3. Facebook App Events: `fullyInitialize` ở foreground sau consent (base project, MO-97) — cần MO xác nhận có gate theo consent không.
  4. Biến thể "init xong mới load" (đúng chữ sheet): thêm `mobileAdsFinish` vào cổng load như a039 / a044 (`initFinished`). Google khuyến nghị chờ initialize xong khi dùng mediation để adapter (Meta) sẵn sàng cho request đầu; đổi lại splash chậm hơn. A013 chọn song song để nhanh (MO-84) — **cần MO chốt**.
  - Đọc `ui/screen/splash/SplashScreen.kt` (2 khối theo `consentFinished`) và `App.kt` (`initFCM`, trừ phần set consent GRANTED) ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:**
  - **BUG chung:** `setConsent` GRANTED cả 4 cho mọi user ngay khi consent xong — A013 `App.kt` `initFCM`, A014, A028, a036, A045, a016, a034, a037, a039, a044, a27, Langofy — kể cả user EEA từ chối. Manifest còn `google_analytics_default_allow_*` = true ở A013, A014, A028, A47, a034, a036, a037, a039, a044. Không coi đây là chuẩn.
  - A045 `MainActivity.initFCM` set GRANTED trước cả khi UMP chạy (không chờ `consentFinished`).
  - Load song song `MobileAds.initialize`: a037 P1624 (commit `6df4315`) ANR > 5s do native load ở main tranh lock với initialize — theo dõi ANR khi bỏ chờ init.
- **QC:** debug EEA (MO-8): (1) Consent → DebugView/`adb logcat -s FA` thấy consent granted; (2) clear data → Manage options → tắt hết → Confirm → app vẫn chạy, `tracking_consent status=rejected`, consent DENIED; (3) logcat thứ tự `requestUMP` → `initMobileAds` → `loadAd`. Ảnh form: `assets/refs/MO-22-1.jpg`.

## MO-23 — Consent từ chối → đẩy IAP

- **Yêu cầu:** User EEA từ chối consent (ads gần như không có doanh thu) → app mời mua gói bỏ ads (paywall) thay vì chỉ chờ ad. Sheet: "chờ bổ sung figma, chưa app nào apply".
- **Nghiệm thu (đề xuất, chờ MO/Figma):** `consentResult == rejected` → sau splash mở paywall (không chờ inter); paywall đóng được, đóng thì tiếp tục FO/Home bình thường; `iap_show_x` có `trigger_type`/`iap_placement` riêng (vd `consent_reject` — tên cần MO chốt); app không IAP → N/A.
- **SDK:** `BaseAds.consentResult`, `tracking_consent`; luồng IAP: không có — tầng app (`xtechbilling` cho billing).
- **Chuẩn A013:** Không có (A013 không IAP). Chưa app nào làm (a016 v1.1.8 mới có tracking consent).
- **Remote config:** đề xuất 1 Boolean bật/tắt (vd `iap_consent_reject`) — key mới, cần MO xác nhận tên.
- **Cách làm:** sau `consentFinished` trong `SplashScreen` đọc `consentResult`; nếu `rejected` và app có billing + chưa premium: không gate splash theo inter, `goNextScreen` tới paywall (giá trị điều hướng `iap`, xem MO-30), paywall xong quay về đích FO. App không xtechads: dùng `ConsentHelper.canShowAds` (A028/a036).
  - A013 chưa có — chỗ nối: `SplashScreen` (`goNextScreen`) và `AdsManager.getNextDestination` ở A013 (bản hiện tại).
- **Bẫy:** UMP `canRequestAds()` = true cả khi user từ chối (đã có quyết định) → không dùng để phát hiện reject; `partial` vẫn có ads limited. Policy: không được chặn dùng app vì từ chối consent (paywall phải đóng được) — cần MO/legal duyệt.
- **QC:** debug EEA → Manage options → tắt Purpose 1 → Confirm → thấy paywall + `tracking_consent status=rejected`; đóng paywall → vào Language/Home.

## MO-24 — Hiện UMP nếu cần, trước mọi hành động

- **Yêu cầu:** Mỗi lần mở app đều hỏi lại thông tin consent; nếu cần (EEA/UK chưa có consent hợp lệ) form hiện trên splash trước mọi ad, mọi popup khác (noti) và trước khi rời splash; lỗi UMP không được treo splash.
- **Nghiệm thu:** form hiện lần đầu ở EEA, không hiện ở non-EEA; noti + inter splash chỉ xuất hiện sau khi đóng form; tắt mạng/lỗi UMP → splash vẫn tiếp tục khi có mạng.
- **SDK:** `requestUMP` (request info → load form → show nếu `REQUIRED` → mọi nhánh kết thúc bằng init); `isPrivacyOptionsRequired`.
- **Chuẩn A013:** `MainActivity.onCreate` gọi `requestUMP` ngay sau `setContent`; trong `SplashScreen` mọi bước chờ `consentFinished`; inter chỉ show khi `hasWindowFocus` (form/dialog giữ focus thì chưa show).
- **Cách làm:** gọi `requestUMP` ở Activity host splash, sau khi có mạng (A045 `MainActivity.initConsent`, a033 `SplashScreen`; A013 chưa chờ mạng — xem MO-9); Setting có mục "Privacy options" gọi `UserMessagingPlatform.showPrivacyOptionsForm` khi `isPrivacyOptionsRequired` (yêu cầu của Google; chưa app nào có — cần MO đưa vào checklist).
  - Đọc `MainActivity.kt` (`onCreate`) và `ui/screen/splash/SplashScreen.kt` ở A013 (bản hiện tại); phần chờ mạng đọc a045 `MainActivity.initConsent`.
- **Bẫy:** A028/a036 bỏ `requestConsentInfoUpdate` khi `canRequestAds()` → consent hết hạn không hỏi lại; gọi khi offline (MO-9); hỏi noti cùng lúc form → 2 dialog chồng.
- **QC:** debug EEA, clear data → form trên splash, chưa có ad/noti (ảnh `assets/refs/MO-24-1.jpg`); Consent → hỏi noti → inter; mở lại app → không hiện form; build không debug ở VN → không form.

## MO-25 — Hỏi quyền notification nếu cần

- **Yêu cầu:** Android 13+: chưa có `POST_NOTIFICATIONS` → hỏi 1 lần ở splash ngay sau consent (song song load ad); inter splash chỉ show sau khi user trả lời; MO dời được việc hỏi về Home.
- **Nghiệm thu:** API 33+, chưa cấp, chưa từng hỏi → dialog hệ thống hiện sau form UMP; trả lời xong mới thấy inter; API < 33 hoặc đã cấp → không hỏi; đã từ chối (rationale) → splash không hỏi lại; RC `home` → splash không hỏi.
- **SDK:** Không có — tầng app (accompanist `rememberPermissionState` hoặc `ActivityResultContracts.RequestPermission`).
- **Chuẩn A013:** `SplashScreen`: `notificationPermissionLauncher` + khối `consentFinished.collectLatest` (chỉ hỏi khi: RC không dời việc hỏi về Home (`notiPermissionAtHome`), chưa từng hỏi (`notiPermissionRequested`), chưa có quyền (`allowNotification`) và không ở trạng thái rationale; hỏi xong ghi `notiPermissionRequested` + `notiPromptSession`); trả lời hoặc bỏ qua → `adsManager.passedNotificationSplash = true` + `SdkInitTracker` `NOTIFICATION_FINISH`; effect theo `passedNotificationSplash` mới schedule reminder / win-back / lock screen / pinned. Home hỏi lại ở `ui/screen/home/view/HomePermissionPrompts.kt`.
- **Remote config:** `noti_permission_trigger` (String, `splash`; `splash` | `home`) — alias `ask_noti_permission_at_home` (Boolean, true — A014).
- **Placement / tracking:** `sdk_init` `sdk_key=notification_finish` (A013 tính từ `App.startTimeMs`); cờ tương đương ở app khác: `notiAnswered` (A045), `notiFinished` (a27), `notiPermFinished` (a039), `requestingNotificationPermission` (a033), `notiResolved` (A014).
- **Cách làm:** 1 cờ "đã qua noti" (StateFlow trong AdsManager hoặc state màn) là điều kiện bắt buộc của khối show inter; hỏi đúng 1 lần (lưu pref) và chỉ khi không có rationale; API < 33 set cờ ngay; sau khi qua mới schedule noti local.
  - Đọc `ui/screen/splash/SplashScreen.kt` (`notificationPermissionLauncher`, khối `consentFinished.collectLatest`) và `domain/preference/SharedPrefs.kt` ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** show inter khi dialog quyền đang giữ focus → mất impression / chồng dialog (cần `hasWindowFocus`, giải thích ở `xTechSDK/docs_final/FO_ADS_FLOW.md` §5.2); `shouldShowRationale` = false cả lần đầu lẫn khi "Don't ask again" → cần cờ `notiPermissionRequested` để phân biệt; quên set cờ khi không cần hỏi → splash treo.
- **QC:** máy API 33+, clear data: consent → dialog noti (ảnh `assets/refs/MO-25-1.jpg`) → Allow/Deny → inter hiện; mở lại → không hỏi; RC `noti_permission_trigger=home` → splash không hỏi.

## MO-26 — Popup không có internet

- **Yêu cầu:** Mất mạng (kể cả wifi không ra internet) ở splash hay bất kỳ đâu → popup chặn (không đóng bằng back/chạm ngoài) giải thích + nút mở cài đặt mạng; có mạng lại popup tự tắt và app tự quay về.
- **Nghiệm thu:** offline → popup ngay; bấm nút → Internet panel (Android 10+) hoặc Wi-Fi settings; bật mạng → app tự lên lại (khi đã sang trang Settings) và popup biến mất; splash không tự đi tiếp khi offline.
- **SDK:** `BaseAds.isConnected` (StateFlow, mạng có `NET_CAPABILITY_VALIDATED`); popup ở tầng app.
- **Chuẩn A013:** `AppNavigation.kt` composable `AppNavigation`: `OvlNoInternet` hiện khi `!isConnected`, nút gọi `openInternetSettings`, cờ `waitingInternetFromSetting` + `internetDialogFocused` để bắn event; `ui/base/dialog/NoInternetPopup.kt` `OvlNoInternet` (Dialog không dismiss bằng back/chạm ngoài, Lottie, nút `BtnEnableInternet`); `utils/AppUtils.kt` `openInternetSettings` (thử lần lượt `Settings.Panel.ACTION_INTERNET_CONNECTIVITY` → `ACTION_WIFI_SETTINGS` → `ACTION_WIRELESS_SETTINGS` → `ACTION_SETTINGS`, set `AppScreenState.openSetting`); `utils/PermissionSettingsGuide.kt` `PermissionSettingsGuide.open` (poll trạng thái, có mạng thì kéo `MainActivity` lên).
- **Placement / tracking:** `overlay_show` `OvlNoInternet`; `button_click` `BtnEnableInternet`; `enable_internet_wifi` / `enable_internet_3g` khi bật được; `enable_internet_not` khi panel đóng ~1s mà vẫn chưa có mạng.
- **Cách làm:** 1 popup duy nhất ở root navigation (không đặt từng màn); nút mở cài đặt qua helper có auto-return; `MainActivity.onPause` bỏ qua track background / noti kill-app khi đang mở Settings (`AppScreenState.openSetting`). Đọc `AppNavigation` + `PermissionSettingsGuide` ở A013 (bản hiện tại). Tên tương đương: `NoInternetDialog` (A045, A47, a037, a039, a044, qibla, a041 `core/ui`), `NoInternetPopup` (a033, a27, A028), `NoInternetGate` (A47), `NetworkSettingsHelper` (a041).
- **Bẫy:** mở Settings bằng `FLAG_ACTIVITY_NEW_TASK` → Settings sang task khác, không chồng được tip / khó auto-return (comment ở `PermissionSettingsGuide`); Internet panel là cửa sổ nổi, app không xuống nền → không được bật cờ skip app-open cho panel (A013 đã tách); Android 14+ đóng băng app ~10s sau khi mất cửa sổ → poll dừng, chỉ khi user quay lại mới báo; noti kill-app bắn khi user sang Settings (MO-88).
- **QC:** bật máy bay ở splash → popup (ảnh `assets/refs/MO-26-1.jpg`); bấm nút → bật Wi-Fi trong panel → popup tắt, splash load ad (MO-96); hotspot không có 4G → vẫn coi là offline.

## MO-27 — Chờ Remote Config trước khi load ad (tuỳ chọn)

- **Yêu cầu:** Khi RC đang điều khiển ads (bật/tắt, unit, timeout, next screen), lần load ad splash đầu tiên phải dùng giá trị RC hiện hành; QC đổi RC phải thấy tác dụng. Sheet ghi "optional in case it can risk by ads control".
- **Nghiệm thu:** user cũ: không chờ thêm (RC cache-first); FO: chờ RC tối đa một trần cố định (đề xuất 2–3s) rồi mới load ad splash, quá trần thì load bằng config đóng gói; đổi RC `ads_config` → bản cài mới thấy đổi ngay khi RC fetch kịp.
- **SDK:** `RemoteConfigManager.fetchedStateFlow` (cache-first), `AdsConfigProvider` (parse lại khi RC về).
- **Chuẩn A013:** **không chờ RC** — cổng load chỉ gồm `consentFinished` + `isConnected` (commit `ba0a17b`, v1.2.6); a27 cũng bỏ (commit `698c9ad`, P4664 "no wait rc, consent on splash"), A045/a016 không chờ. App có chờ RC: a039 (`mobileAdsFinish` + `isConnected` + `fetchedStateFlow`), a044 (`initFinished` + `fetchedStateFlow` + `isConnected`), a036, a041, A014 (`consentFinished` + RC fetched + mạng).
- **Remote config:** `ads_config` và mọi key đọc ở splash (`splash_next`, `native_splash_high_logic`, `logic_pass_splash`, …).
- **Cách làm (chuẩn đề xuất, cần MO chốt):** cổng load splash = consent xong (`consentFinished`) VÀ có mạng (`isConnected`) VÀ (RC đã fetch — `fetchedStateFlow` — HOẶC đã hết trần chờ). Trần là hằng số trong code (RC không thể cấu hình trần cho chính lần fetch đầu); đếm từ lúc vào splash — RC đã fetch song song từ lúc `startKoin` nên thực tế hầu như không cộng thêm thời gian. Nếu MO giữ cách A013 (không chờ): bắt buộc giữ `app/config/ads_config.json` = bản RC đang chạy ở mỗi lần release và chấp nhận FO lần đầu không điều khiển được bằng RC.
  - Đọc `ui/screen/splash/SplashScreen.kt` (khối `combine`) ở A013 (bản hiện tại) để lấy chỗ nối; cách chờ RC đọc a039 / a044 `ui/screen/splash/SplashScreen.kt`.
- **Bẫy:** chờ RC không có trần → FO kẹt tới hết timeout × retry của RC khi mạng xấu (5s × 5 lượt); chờ `fetchedStateFlow` mà RC lazy (SDK cũ) → không bao giờ true → kẹt splash; key app cache vào biến khởi tạo một lần → RC về sau không ăn.
- **QC:** clear data, RC đặt placement `splash` `isEnable: false` → FO không có inter (khi chờ RC) / vẫn có (cách A013); hạ `timeout` của nameSpace `splash` xuống 3000 → no-fill thì rời splash sớm (kết hợp MO-29).

## MO-28 — Không quay lại được splash

- **Yêu cầu:** Rời splash là xoá splash khỏi back stack; back trên splash không làm gì; back ở các màn FO không bao giờ về splash (FO chặn back hoặc lùi về bước FO trước).
- **Nghiệm thu:** từ màn sau splash bấm back/vuốt → không thấy splash; back trên splash bị nuốt; kill app giữa FO rồi mở lại → splash chạy lại từ đầu rồi tiếp FO.
- **Chuẩn A013:** `SplashScreen` `goNextScreen` gọi `navigateTo` với `popupTos` chứa `ScrSplash` (`common/NavigationUtil.kt` `navigateTo`: thêm đích trước rồi xoá các class trong `popupTos`, bỏ qua nếu trùng class đang ở đỉnh); `BackHandler` nuốt back ở Splash, `LanguageFOScreen`, `SelectScreen`; Onboard có nút back về bước FO trước (`AdsManager.previousOnBoard`, RC `ob_back_btn`, không bao giờ trả về Splash).
- **Remote config:** `ob_back_btn` (Boolean, true) — nút back ở Onboard về bước FO trước.
- **Cách làm:** điều hướng khỏi splash luôn pop splash; xử lý back của từng màn FO theo các mục nhóm language/select/onboard (MO-36, MO-44, MO-52, MO-53); sheet gợi ý thêm back từ Onboard1 về Language để user chọn lại ngôn ngữ (MO-52). Nav2/Fragment: `popUpTo(splash) { inclusive = true }`; SplashActivity riêng: `finish()` sau khi start màn kế.
  - Đọc `SplashScreen` (`goNextScreen`), `common/NavigationUtil.kt` (`navigateTo`), `ui/screen/onboard/OnBoardScreen.kt` (`previousOnBoard`) ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** Nav3 `rememberNavBackStack` là saveable → `recreate()` khôi phục màn cũ, bỏ qua splash (A013 khởi động lại task trong `MainActivity.onNewIntent`); pop splash trước khi push đích → stack rỗng thoáng chốc.
- **QC:** FO tới Language → back → không về splash; kill giữa FO → mở lại → splash → FO tiếp; đang ở Home mở app từ noti → splash chạy lại (MO-78).

## MO-29 — Chỉ rời splash khi ad splash có kết quả

- **Yêu cầu:** Splash chỉ chuyển màn khi inter splash đã show (đi tiếp lúc ad hiện/đóng) hoặc chắc chắn không có ad (fail, tắt, hết trần MO cho phép); không có timer tự đi trước khi ad có kết quả.
- **Nghiệm thu:** có fill → inter hiện rồi mới thấy màn kế; no-fill → rời splash ngay sau fail (bar chạy nốt); offline không bị coi là fail; không điều hướng 2 lần; click ad rồi quay lại → đúng hành vi `logic_pass_splash`.
- **SDK:** `AdGroupUnit.statusFlow` (`NONE` / `LOADING` / `SUCCESS` / `FAIL` / `TIMEOUT` / `IMPRESSED`), `showFullScreen(activity, onNextAction, onAdFailedToShow, onAdShow, onAdClosed)`, `timeout` của nameSpace → `TIMEOUT` (vẫn load ngầm, không huỷ request).
- **Chuẩn A013:**
  - `ads/AdsManager.kt`: `loadSplashAds` (thường: `splash`; FO + `useSplashHighFlow`: `inter_splash_high` + `native_full_splash` song song, cả hai fail mới `LoadInterAll` → `inter_splash_all`; `logic_pass_splash=reload` thì nạp sẵn backup), `splashAction()` trả `SplashAction`, `showSplashInter` (điều hướng ở `onAdShow` / `onAdFailedToShow`, báo cho `InterSplashClickAction`).
  - `SplashScreen`: `LifecycleResumeEffect` chỉ hành động khi đã qua noti (`passedNotificationSplash`), cửa sổ có focus (`hasWindowFocus`), có mạng, chưa hiện native full và chưa điều hướng; cờ `navigated` trong `goNextScreen`.
  - `ui/screen/splash/view/SplashNativeFullContent.kt`: đếm `fs_splash_close_second` rồi cho đóng, tự đi sau `fs_splash_auto_next_second`, set `isShowingAds` để chặn app-open, đếm tạm dừng khi rời app.
  - `ads/InterSplashClickAction.kt`: click inter rồi quay về trang ad → `auto_next` đóng ad đi tiếp, `reload` đóng ad + show inter backup (chờ 2s nếu backup sẵn, 6s nếu đang load), `keep_state` giữ nguyên; `AppNavigation` hiện `AdReloadCover` trong lúc chờ.
- **Remote config:** `native_splash_high_logic` (Boolean, true), `logic_pass_splash` (String, `reload`), `fs_splash_close_second` (Long, 5), `fs_splash_auto_next_second` (Long, 5) — alias ở Tổng quan; `timeout` của nameSpace `splash` trong `ads_config` (ms, A013 30000).
- **Placement / tracking:** `splash`, `inter_splash_high`, `native_full_splash`, `inter_splash_all`, `inter_splash_backup_high`, `inter_splash_backup`; `screen_show` `ScrNativeFullSplash`; `button_click` `BtnContinueToApp`.
- **Cách làm:**
  1. Load theo MO-22/MO-27; show bằng 1 effect phản ứng theo trạng thái unit, không dùng timer.
  2. Map: SUCCESS → preload màn kế (MO-31) → show, điều hướng ở `onAdShow` (+ `onAdFailedToShow`, + `onNextAction` khi không show được); FAIL → preload → đi tiếp; LOADING/NONE → chờ; TIMEOUT → theo quyết định MO (Bẫy).
  3. Chống điều hướng đôi bằng cờ; chỉ show khi có focus + đã qua noti + có mạng.
  4. High-floor / backup / native full: chỉ làm khi MO yêu cầu — đọc `AdsManager.splashAction`, `InterSplashClickAction`, `SplashNativeFullContent` ở A013 (bản hiện tại).
- **Bẫy:** `TIMEOUT`: A013 coi là chờ tiếp (đúng hướng dẫn chung SDK, mục B.6 `SDK_INTEGRATION_GUIDE.md`) → splash có thể chờ quá `timeout`; A045/a27/a033 coi `TIMEOUT` = đi tiếp nên `timeout` của nameSpace là trần chờ MO chỉnh được — **cần MO chốt**. Truyền thiếu `onAdClosed`/`onAdFailedToShow` cho `showFullScreen` → nuốt điều hướng (qibla checklist). Unit splash còn `IMPRESSED` từ lần mở trước (process còn sống) → phải reset ở `MainActivity.onCreate` (A013 `AdsManager.resetState`, A47 `resetSplashAds`). Show khi offline → mất impression (`FO_ADS_FLOW.md` §5.1).
- **QC:** có fill: inter hiện → đóng → đang ở màn kế; RC đặt adunit sai ID (no fill) → rời splash ngay sau fail; FO + bật `native_full_splash` trong RC → native full đếm 5s; click inter → quay lại → đúng `logic_pass_splash` (`reload`: thấy inter thứ 2).

## MO-30 — RC chọn màn sau splash

- **Yêu cầu:** MO chọn qua RC màn kế tiếp sau splash (và chuỗi FO): language | onboard | select | iap | home; giá trị lạ rơi về mặc định an toàn; user đã xong FO luôn vào Home.
- **Nghiệm thu:** đổi `splash_next` → FO đi đúng màn; `home` → bỏ FO; `iap` → paywall (app có IAP, chưa premium) rồi đi tiếp; giá trị sai → mặc định; không vòng lặp / kẹt màn.
- **SDK:** `AdsConfigProvider.getNavigationValue(key, default)` đọc `navigationFlow` trong `ads_config`.
- **Chuẩn A013:** `ads/AdsManager.kt` enum `FONavKey` (`splash_next` → `language`, `language_next` → `select`, `select_next` → `onboard`, `onboard_next` → `home`), enum `FONavValue` (`language` / `select` / `onboard` / `home`), `getNextDestination`, `nextSplash` (chỉ khi `prefs.firstOnboard`, ngược lại Home); `firstOnboard` tắt khi tới `HomeScreen`. **Lệch:** A013 đọc key RC rời qua `prefs.getString` (key `splash_next`…), **không** đọc `navigationFlow` trong `ads_config` (dù `app/config/ads_config.json` có khai) → với A013, MO phải set key top-level.
- **Remote config:** `splash_next` (String, `language`), `language_next` (`select`), `select_next` (`onboard`), `onboard_next` (`home`). Alias: cùng tên trong `ads_config.navigationFlow` (A045, A014, A47, a033, a034, a037, a039, a044, a27); camelCase `splashNext` / `languageNext` / `onboardNext` / `selectNext` / `paywallNext` (a016); thêm `scan_onboard_next`, `paywall_next` (a27), `iap_next` (a044). Giá trị IAP: `iap` (a016, A014) vs `paywall` (a27); A045 nhận thêm `uninstall`, `language_alt`, `select_alt`.
- **Cách làm:** 1 enum key + 1 hàm resolve (giá trị → đích, kèm fallback) trong AdsManager; nên đọc qua `getNavigationValue` (chuẩn chung các app SDK) — nếu giữ key rời như A013 thì thống nhất 1 nguồn và báo MO; chặn đích trùng màn hiện tại (a016 `getNextDestination` so với `ownDestinationOf`); `iap` chỉ khi có billing + `canShowIAP`, không thì sang bước sau (a016 `iapOrFallback`, A014 `iapFallback`); preload ads của đích (MO-31).
  - Đọc `ads/AdsManager.kt` (`FONavKey`, `FONavValue`, `getNextDestination`, `nextSplash`) ở A013 (bản hiện tại); chặn trùng màn + giá trị `iap` đọc a016 `ads/AdsManager.kt` (`getNextDestination`).
- **Bẫy:** RC `language_next=language` → A013 `navigateTo` bỏ qua vì trùng class → kẹt màn; chuỗi vòng (language → select → language); app dùng snake_case, app khác camelCase → MO set nhầm key.
- **QC:** clear data, lần lượt đặt `splash_next` = `onboard` / `select` / `home` / giá trị rác → FO đi đúng; user cũ luôn vào Home.

## MO-31 — Preload native màn kế khi splash có kết quả lần đầu

- **Yêu cầu:** Chỉ khi trạng thái ad splash lần đầu chuyển SUCCESS hoặc FAIL mới load native của màn kế (theo `splash_next`), và chỉ 1 ad để không tranh băng thông / không kéo dài splash.
- **Nghiệm thu:** không có request native màn kế trước khi inter splash có kết quả; đúng 1 request native (placement hiện đầu tiên của màn kế); vào màn kế native hiện ngay.
- **SDK:** `AdGroupUnit.loadAd` tự bỏ request trùng (`LOADING` / `SUCCESS` còn hạn); unit là singleton theo placement → màn kế dùng lại ad đã preload.
- **Chuẩn A013:** `AdsManager.loadNativeNextSplash` → `preloadAdsFO(nextSplash)`: Language → `language` (1 ad); Select → `select` (1); OnBoard → `onboard_1` (+ `onboard_2` khi `new_onboard`) + `fs_onboard` (trừ khi mượn được native full splash — `canBorrowFsob`) = 2–3 ad; Home → `home_top` + `home_bottom` (2); OnboardFeature → `onboard_feature`. Gọi trong các nhánh `ShowInter` / `ShowNativeFull` / `None` của `SplashScreen`.
- **Placement / tracking:** placement đầu mỗi màn: `language`, `select`, `onboard_1`, `home_top` (A013).
- **Cách làm:** 1 dispatcher `preloadAdsFO(dest)` trong AdsManager; gọi đúng 1 lần lúc splash có kết quả (trước `showFullScreen`, hoặc trước khi đi tiếp khi fail); chỉ load placement hiện đầu tiên của màn kế, placement khác để màn đó tự load. Đọc `AdsManager.preloadAdsFO` ở A013 (bản hiện tại).
- **Bẫy:** A013 lệch "only 1 ad" khi đích là OnBoard/Home (sheet ghi a018 cũng load 2); preload ngay lúc vào splash → tranh băng thông với inter; quên preload ở nhánh FAIL.
- **QC:** logcat `loadAd: placement=` — native màn kế xuất hiện sau dòng kết quả inter splash; đổi `splash_next` → placement preload đổi theo.

## MO-84 — Tối ưu thời gian splash (logic như A013)

- **Yêu cầu:** Splash kết thúc ngay khi tín hiệu thật sẵn sàng, không có mốc thời gian giả; các bước chạy song song. Nguồn: A013 hiện tại; `a036 docs/splash-optimize-a013.md` mô tả A013 bản cũ.
- **Nghiệm thu:** không `delay` cố định, không progress gate; consent → noti song song load ad; show ngay khi SUCCESS + đã qua noti + có focus; đi tiếp lúc ad hiện; đo được bằng `sdk_init`.
- **Chuẩn A013 — các handle (đọc code hiện tại để lấy chi tiết):**
  1. `requestUMP` ngay trong `MainActivity.onCreate`; user cũ đã `canRequestAds()` → SDK init AdMob sớm, không đợi request consent mới.
  2. Cổng load chỉ gồm `consentFinished` + `isConnected` — không chờ `mobileAdsFinish`, không chờ RC (v1.2.6).
  3. Hỏi noti song song với load ad, ngay sau consent.
  4. Show ngay khi unit SUCCESS (effect key theo status), không gate theo progress; progress chỉ trang trí (99% trong 4s, chốt 100% trong 250ms khi không có ad).
  5. Điều hướng tại `onAdShow` → màn kế compose sau lưng ad, đóng ad là thấy màn kế.
  6. Preload native màn kế chỉ khi splash có kết quả (MO-31).
  7. Reset unit splash `FAIL`/`IMPRESSED` đầu mỗi lần mở (`AdsManager.resetState`); chặn app-open trên splash (`screenSkipAdResume` + `disableAdResumeOnTime`).
  8. Việc phụ (cập nhật shortcut trên IO, schedule noti sau khi qua noti) không chặn splash.
- **Placement / tracking:** `sdk_init` `ump_finish`, `mobile_ads_finish`, `remote_config`, `notification_finish`; nên thêm `splash_load` / `splash_show` / `splash_close` (duration tính từ lúc vào splash, như A045 `SplashScreen`; a033 có `splash_load`) để so giữa các app.
- **Cách làm:** áp lần lượt 8 handle; bỏ mọi `delay`, `smoothProgress`, cờ kiểu `splashProgressFinalized`; giữ đủ cổng an toàn (consent, mạng, focus, noti). Nếu áp chờ RC có trần (MO-27) thì FO cộng tối đa trần đó, user cũ không đổi.
  - Đọc `MainActivity.kt` (`onCreate`), `ui/screen/splash/SplashScreen.kt`, `ui/screen/splash/view/SplashContent.kt`, `ads/AdsManager.kt` (`loadSplashAds`, `splashAction`, `resetState`) ở A013 (bản hiện tại) để lấy chi tiết từng handle.
- **Bẫy:** bỏ chờ RC / init làm tăng rủi ro MO-17 / MO-22 (xem MO-27, MO-22) và ANR (a037 P1624); doc a036 nói A013 chờ `mobileAdsFinish` + RC và progress indeterminate — đã cũ.
- **QC:** đo icon → inter (stopwatch hoặc `splash_show`) trước/sau thay đổi; mạng tốt: FO chỉ tốn UMP + thời gian load ad; offline: không tự đi tiếp.

## MO-96 — Bật lại mạng ở splash → load + show ad splash rồi mới đi tiếp

- **Yêu cầu:** Splash đang mất mạng → user bật mạng (qua popup) → quay về app: splash phải load ad, show (nếu có) rồi mới sang màn kế (Language/Home), không tự nhảy màn. Áp cho cả FO lẫn các lần mở sau.
- **Nghiệm thu:** offline → popup, splash đứng; bật mạng → app tự quay về, popup tắt, progress chạy, có `iaa_request` của placement splash, inter hiện rồi mới sang màn kế; ad fail lúc mất mạng giữa chừng → có mạng lại phải load lại, không đi tiếp.
- **SDK:** `isConnected`; `loadAd` cho load lại khi `FAIL`/`IMPRESSED` (`shouldLoadAd`); offline → `canLoadAd` false → `FAIL` ngay.
- **Chuẩn A013:** `SplashScreen`: cổng load là khối `combine` theo `consentFinished` + `isConnected`, thu thập liên tục → mỗi lần có mạng lại gọi `loadSplashAds` (unit `FAIL` được nạp lại); khối show có điều kiện `connected` nên `FAIL` lúc offline không làm đi tiếp; `SplashContent` progress chỉ chạy khi có mạng; tự quay về app nhờ `PermissionSettingsGuide` (MO-26). Lịch sử: v1.2.0 P2447 (commit `8c6a298`) thêm điều kiện mạng. Sheet (snapshot 2026-10-07) vẫn chấm a013 = 0 → phải QC lại đúng kịch bản dưới trước khi coi A013 là chuẩn cho mục này. Ref khác: A045 P3578 (cổng load theo `consentFinished` + `isConnected`, show cần có mạng); a041 `SplashScreen` (effect theo `isConnected`: chưa điều hướng + unit `FAIL` → load lại; `FAIL` khi offline → chờ).
- **Cách làm:** (1) cổng load là flow/effect chạy lại mỗi khi `isConnected` về true (không chờ kiểu `first` một lần rồi thôi); (2) mọi nhánh "đi tiếp vì không có ad" phải kèm điều kiện đang có mạng; (3) tự quay về app (MO-26). Đọc `SplashScreen` (khối `combine` + `LifecycleResumeEffect`) ở A013 (bản hiện tại).
- **Bẫy:** a033 `SplashScreen` chỉ chờ cổng load một lần (`first`) rồi show-effect đi tiếp khi `FAIL` + có mạng → mất mạng giữa lúc load là nhảy màn không có ad (đúng bug của sheet). A013: nhánh `LoadInterAll` trong `LifecycleResumeEffect` chạy cả khi offline (không kèm điều kiện mạng) → `inter_splash_all` `FAIL` ngay; an toàn chỉ khi cổng load kịp nạp lại high/native trước lúc effect tính lại `splashAction` — QC kỹ kịch bản FO + high-floor + mất mạng giữa chừng. Unit đang `TIMEOUT` khi offline vẫn load ngầm, `shouldLoadAd()` = false → không nạp lại tới khi có kết quả; UMP lỗi lúc offline (MO-9).
- **QC:** (FO và lần mở sau) bật máy bay → mở app → popup → bấm nút → bật Wi-Fi → quay app: splash load + inter → Language/Home; thử ngắt mạng đúng lúc ad đang load rồi bật lại.

## MO-97 — Tối ưu init SDK cho splash (splash-sdk-init-optimization)

- **Yêu cầu:** Doc Lark không đọc được; tổng hợp từ report a014 (`xTechSDK/docs/CHANGELOG.md` 2026-09-08), base project (`init-base-project/references/architecture.md` §2, §10) và A013/A045. Mục tiêu: init SDK không chặn splash, không init nặng ở `Application.onCreate` / khi process dậy nền, init song song trên IO, đo được bằng `sdk_init`.
- **Nghiệm thu:**
  - `Application.onCreate` chỉ `startKoin` + Timber + việc rẻ; module app không có singleton nặng `createdAtStart` (billing, Facebook…).
  - Facebook `AutoInitEnabled=false`, `FacebookSdk.fullyInitialize()` chạy ở foreground trên IO.
  - Firebase consent / Crashlytics / FCM token trên IO, sau consent.
  - Số `sdk_init` `billing_finish` / `appsflyer` xấp xỉ số lần mở app foreground (không gấp nhiều lần).
  - Splash không chờ việc không liên quan (billing, FCM, shortcut).
- **SDK:** `SdkInitTracker` (SDK keys `appsflyer`, `remote_config`, `ump_finish`, `mobile_ads_finish`, `billing_finish`), `BillingManager.isPurchasedCached`, `ensureAdsInitialized`.
- **Chuẩn A013:** `App.kt` (`startKoin`; `initLockScreenNoti` chạy IO; `initFCM` IO sau consent; `fetchRemoteConfig`); `common/SdkInitTracker.kt` (`utm`, `notification_finish`); `SplashScreen` cập nhật shortcut trên IO. **Lệch:** manifest `com.facebook.sdk.AutoInitEnabled=true`; `initLockScreenNoti` (schedule + đăng ký watcher) chạy ở `Application.onCreate` cho cả process dậy nền.
- **Cách làm:**
  1. Đo trước: dashboard `sdk_init` theo `sdk_key` so với số lần mở app.
  2. Dời init không bắt buộc khỏi `Application.onCreate` / `createdAtStart` sang `MainActivity` (foreground) — template base project `MainActivity`: `initConsent` (chờ mạng rồi `requestUMP`), `initForegroundSdks` (Firebase trên IO), `initFacebook`.
  3. Billing lazy + `isPurchasedCached` (MO-5).
  4. Facebook: manifest `AutoInitEnabled=false`, `fullyInitialize()` ở foreground khi có app id; không gọi `setAutoInitEnabled(true)`.
  5. Thêm `sdk_init` `splash_load` / `splash_show` / `splash_close` (A045 `SplashScreen`) để đo splash end-to-end.
  - Đọc `App.kt` ở A013 (bản hiện tại) để thấy hiện trạng; mẫu init ở foreground đọc template `MainActivity` của base project (`init-base-project/assets/template`).
- **Bẫy:** SDK tự dựng `RevenueManager` (AppsFlyer) và RC eager lúc `startKoin` — app không tránh được, đừng `AppsFlyerLib.init/start` lần 2 trong app; `AdsManager` phải resolve trên main (constructor `BaseAds` đụng `ProcessLifecycleOwner`); load ad song song `MobileAds.initialize` → ANR (a037 P1624).
- **QC:** so `sdk_init` trước/sau 1 bản; gửi FCM / chờ alarm khi app đã kill → không có `billing_finish`; theo dõi ANR rate trên Play Console.

## MO-99 — Tách ad unit new user / old user ở splash

- **Yêu cầu (sheet):** Inter splash dùng ad_unit_id khác nhau cho user mới và user cũ vì giá trị (eCPM) khác nhau, để MO đặt floor/đo riêng.
- **Nghiệm thu:** có 2 placement riêng: `splash` (user mới — lượt FO) và `splash_o` (user cũ), mỗi cái có nameSpace + ad unit riêng; lượt FO dùng `splash`, mọi lượt sau dùng `splash_o`; `splash_o` tắt/thiếu → fallback `splash`; lựa chọn chốt 1 lần mỗi lượt mở; `iaa_*` phân biệt được 2 placement.
- **SDK:** chỉ cần 2 `AdGroupUnit.of(...)` + config; không có API riêng.
- **Chuẩn A013:** Chưa có. A013 chỉ có luồng high-floor cho FO (`native_splash_high_logic` → `inter_splash_high` / `native_full_splash` / `inter_splash_all`) nhưng dùng cùng ad unit với user cũ. Ref đúng ý sheet: a033 `first_open/ui/splash/SplashScreen.kt` (chọn `interSplash` / `interSplashO` theo `prefs.firstOpen`) + `ads/AdsManager.kt` (`interSplashO`); A47 `ads/AdsManager.kt` (`isFirstOpenLaunch` chốt trong `resetSplashAds(openFrom)` gọi từ `MainActivity.onCreate`: FO + mở từ launcher → `splash`, còn lại → `splash_o`; `PLACEMENT_SPLASH_O`, `loadInterSplashO` preload khi bắn noti).
- **Biến thể đã làm ở app khác (khác ý sheet):** A014 commit `11de76bd` (+ `9f688f5b`) và A045 (ticket P3570 "Ref a033") — `AdsManager.preloadInterSplashOnNoti` / `pickInterSplashForShow` + RC `use_new_logic_inter_noti`: `splash_o` chỉ cho lượt mở từ notification (preload lúc noti bắn), dùng nếu đã sẵn, không thì `splash`; a044 `splash_r2` (noti) + `splash_r3` (shortcut uninstall); a039 `inter_o_splash` (shortcut uninstall).
- **Remote config:** placement/nameSpace `splash_o` trong `ads_config`; biến thể noti thêm `use_new_logic_inter_noti` (Boolean, true — A045, A014).
- **Placement / tracking:** `splash` / `splash_o` (alias `inter_o_splash` a039, `splash_r2` a044); tên ad unit `inter_o_splash_high` / `inter_o_splash` (A014, A045, a039, a044) hoặc `inter_splash_o_high` / `inter_splash_o` (A47, a033).
- **Cách làm:**
  1. `ads_config`: thêm nameSpace + placement `splash_o` (ad unit do MO cấp).
  2. AdsManager: unit `splash_o` + biến "lượt này là FO" chốt 1 lần ở `MainActivity.onCreate` (trước khi FO kịp tắt cờ first-open); getter unit splash trả `splash` hoặc `splash_o`, fallback `splash` khi `splash_o` không `enable`.
  3. Splash dùng getter này cho load / status / show; high-floor (nếu có) chỉ cho FO.
  4. Tuỳ chọn: preload `splash_o` khi bắn noti (gọi `ensureAdsInitialized` nếu ads chưa init).
  Đọc A47 `AdsManager` + a033 `SplashScreen` để lấy chi tiết (A013 chưa có).
- **Bẫy:** đọc cờ first-open trực tiếp ở splash: cờ tắt giữa chừng (A47: tắt ngay khi inter đang hiện) → đổi unit giữa chừng → kẹt splash; hậu tố `_o` mỗi app một nghĩa (old user / mở từ noti / uninstall) — **cần MO chốt định nghĩa** user cũ (non-FO, theo session hay theo ngày cài).
- **QC:** clear data → FO: `iaa_request` placement `splash`; mở lại lần 2 → `splash_o`; RC tắt `splash_o` → lần 2 dùng `splash`.

## DEV-3 — Init song song AppsFlyer, billing, Remote Config ở splash

- **Yêu cầu:** AppsFlyer, billing, Remote Config khởi tạo song song, không chờ nhau, không chặn UI splash; app thiếu SDK nào thì bổ sung (sheet: a028, a037 thiếu AppsFlyer).
- **Nghiệm thu:** 3 init bắt đầu ngay khi mở app (log / `sdk_init`), chạy trên IO; splash không await billing; `AppConfig.appsflyerKey` là key thật.
- **SDK:** AppsFlyer: `RevenueManager` (eager) → `AppsflyerManager` init + start trên IO khi `appsflyerKey` khác rỗng (set Customer User ID = Firebase app instance id); RC: `XtechCore.remoteConfig` eager, fetch IO; billing: `xtechbilling` `BillingManager` lazy, init async khi được inject lần đầu.
- **Chuẩn A013:** AppsFlyer + RC nhờ SDK (`di/Modules.kt` `AppConfig.appsflyerKey`; `App.kt` `fetchRemoteConfig`); không có billing.
- **Cách làm:** khai `appsflyerKey` (không tự `AppsFlyerLib.init/start`); RC theo MO-17; billing: inject `BillingManager` ở Splash/MainActivity để kick init song song (a016 `SplashScreen`), `onInitDone` → `SdkInitTracker` `BILLING_FINISH`; không đưa billing vào cổng splash. App không SDK: a041 `core/ads/.../appsflyer/AppsflyerManager.kt` init riêng; A028/a036 dùng Adjust thay AppsFlyer → cần MO xác nhận (MO-14).
  - Đọc `di/Modules.kt` (`AppConfig`) + `App.kt` ở A013 (bản hiện tại); phần billing đọc a016 `ui/screen/splash/SplashScreen.kt` + `ads/billing/BillingExt.kt`.
- **Bẫy:** đặt `BillingManager` vào constructor `AdsManager` eager → init cả khi dậy nền (MO-5, MO-97); ghi chú sheet có thể cũ: a037 hiện đã có `appsflyerKey` trong `di/Modules.kt`.
- **QC:** logcat thấy `init: AF`, `fetchRemoteConfig: start fetching` và init billing gần như cùng lúc; DebugView `sdk_init` có `appsflyer`, `remote_config`, `billing_finish`.

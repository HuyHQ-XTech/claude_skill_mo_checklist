# Nhóm ads: hành vi quảng cáo trong app

## Tổng quan nhóm

- **SDK xtechads, các thành phần chính**:
  - `BaseAds`: `AdsManager` của app kế thừa class này.
  - `AdGroupUnit.of(placement)`: placement trỏ tới nameSpace trong `ads_config`.
  - `NativeBannerGroupView`: view hiển thị native / banner.
  - `FullscreenAdObserver`: show ad full-screen (inter / app-open / reward).
  - `NativeAdClickNextAction`: tự sang màn kế khi user quay lại sau khi click ad.
- **Remote config (RC)**:
  - `RemoteConfigManager` (xtechcore) tự ghi MỌI key RC vào prefs. App chỉ cần khai `SharedPreferenceProperty("key", default)` trong `SharedPrefs` của mình.
  - Số ghi dạng Long (số thập phân ghi dạng Float). Vì vậy:
    - Property phải khai Long.
    - Khai Int sẽ bị `ClassCastException`, lỗi bị nuốt im lặng, nên luôn trả default.
  - RC dùng cache trước. `AppConfig.minimumFetchIntervalRc` mặc định 3600s, nên giá trị mới thường chỉ có tác dụng ở lần mở app sau.
- **Field `ads_config` hay dùng trong nhóm này**:
  - Cấp namespace: `actionClicked` (`none|tooltip|disable|reload|next_screen|custom`), `reloadWhenResume`, `timeout`.
  - Cấp adunit: `format`, `bannerType`, `autoReloadOnImpression` (ms), `useNativeCollapsible`, `layout`.
  - `configs.bannerReloadTime` / `bannerMinReloadTime`: SDK có parse nhưng không dùng.
- **Quy ước đường dẫn**:
  - A013: tính từ `app/src/main/java/com/example/a013_recovery/`.
  - SDK: tính từ `xTechSDK/xtechads/src/main/java/com/example/xtechads/`.
  - App khác: tính từ thư mục package gốc.
  - Tìm theo symbol (`grep -rn`) và luôn đọc code A013 bản hiện tại.
- **App không dùng SDK** (có `ads/base/BaseAds.kt` riêng): A028, a036, a041.

## MO-79 — Toast / notification sau khi click ad (+ RC delay)

- **Yêu cầu**:
  - Click vào BẤT KỲ ad nào thì hiện 1 trong 2 (chọn bằng RC):
    - Toast ngắn, kiểu "you are missing chance…".
    - Notification kéo user quay lại app.
  - Cần thêm RC để chỉnh thời gian delay trước khi hiện.
  - Ước lượng: dev 0.2h, QC 0.5h (QC click mọi vị trí ad đều phải bắn).
- **Nghiệm thu**:
  - Mỗi lần click ad (native / banner / inter / app-open / reward, ở mọi màn) có đúng 1 toast hoặc 1 noti, sau đúng thời gian delay theo RC.
  - Đổi RC `click_ad_action` thì có tác dụng.
  - Không làm hỏng logic click riêng (splash inter, native ở FO).
- **SDK**:
  - Mọi unit (`BannerAdUnit`, `NativeAdUnit`, `InterstitialAdUnit`, `AppOpenAdUnit`, `RewardAdUnit`) khi bị click đều gọi `BaseAds.onAdClicked()`. Hàm này làm 2 việc:
    - `disableAdResumeOnTime()`,
    - `clickedAnyAds?.invoke()`.
  - `clickedAnyAds` là MỘT biến lambda duy nhất: gán sau sẽ đè gán trước.
  - Helper `Context.toast(...)` nằm ở `utils/AppUtils.kt`.
  - SDK không có delay hay RC cho việc này.
- **Chuẩn A013**:
  - `AppNavigation` gán `adsManager.clickedAnyAds` trong `LaunchedEffect(Unit)`. Lambda làm theo thứ tự:
    1. Chuyển click cho `interSplashClickAction.onClicked()` (xem MO-93).
    2. Nếu `prefs.clickAdAction` = `"notification"` thì gọi `notificationManager.setKillAppNotification()`.
    3. Còn lại thì toast `R.string.don_t_forget_your_lose_files`.
  - **Lệch chuẩn**:
    - KHÔNG có RC delay.
    - Nhánh notification dùng lại noti kill-app, nên lượt mở lại app bị log `notification_kill`.
    - a044 / A045 / A47 thì có noti riêng `showClickAdsNotification()` (MO-70).
- **Remote config**:
  - `click_ad_action` (String, mặc định `"toast"`): `"toast"` hoặc `"notification"`.
    - Default `"toast"`: A013, A014, a016, a037, Langofy.
    - Default `"notification"`: a27, a034, a044, A045, A47.
    - a039 không có RC này, luôn bắn noti kill-app.
  - ĐỀ XUẤT, chưa app nào có: `click_ad_action_delay_ms` (Long, mặc định `0`) = thời gian chờ sau khi click mới hiện toast / noti.
- **Placement / tracking**:
  - Chỗ các app khác gán hook (dùng để grep):

    | App | File / symbol |
    |---|---|
    | A014 | `main/AppNavigation.kt` |
    | a016 | `domain/models/nav/AppNavigation.kt` |
    | a27 | `AppNavigation.kt` |
    | a034 | `ui/navigation/AppNavigation.kt` |
    | a037 | `ui/navigation/MainNavigation.kt` |
    | Langofy | `app/ui/MainApp.kt` |
    | a044 | `App.kt` `hookAdClickAction`, đặt ở Application để lambda không giữ Activity |
    | A045 | `ads/AdsEffects.kt` `ClickAdsEffect` |
    | A47 | `ads/AdsEffects.kt` `ClickAdsEffect(backStack)`, chụp back stack vào `clickAdsStack` để mở lại đúng màn |
    | a031 | `utility/CompassApplication.kt` |
    | a033 | `ads/AdsManager.kt`, cờ `anyAdClicked` để khỏi bắn noti kill-app |
    | a041 | `TranslationApplication.kt` |

  - User bấm noti thì log `app_open_from` = `notification_click_ads` (MO-70).
- **Cách làm**:
  1. **Gán hook đúng MỘT chỗ**:
     - Gán `clickedAnyAds` ở Application hoặc root composable.
     - Gom mọi side effect của click vào lambda đó. A013 còn phải gọi `interSplashClickAction.onClicked()`.
     - Đọc `AppNavigation` ở A013, đoạn LaunchedEffect gán `clickedAnyAds`.
  2. **Khai RC**: `click_ad_action` và delay trong `SharedPrefs`. Số thì khai Long.
  3. **Delay**:
     - Hẹn giờ bằng `Handler(Looper.getMainLooper()).postDelayed` hoặc coroutine scope cấp process.
     - KHÔNG dùng scope của composition hay của màn: user đang rời sang trang quảng cáo nên màn có thể đã bị dispose.
     - Delay = 0 thì hiện ngay.
  4. **Nội dung**:
     - Toast: text ngắn, string riêng mỗi app, dịch đủ ngôn ngữ.
     - Notification: dùng builder MO-70, kèm open_from click-ads.
  5. **App XML / non-SDK**: hook đặt ở Application. Nếu app tự viết ads thì gọi hook trong `onAdClicked` của từng loại unit.
- **Bẫy**:
  - Gán `clickedAnyAds` ở chỗ thứ 2 sẽ đè chỗ thứ 1, làm mất logic splash inter và native FO.
  - Lambda giữ `Activity` trong singleton sẽ gây leak và dùng context chết sau recreate. Hãy dùng `applicationContext`.
  - Toast hiện khi app đang ở nền (user đang ở trình duyệt / Play):
    - Toast text vẫn hiện được.
    - Toast custom view bị chặn khi app ở nền từ Android 11. Vì vậy giữ toast dạng text.
  - Nếu thấy 1 click bắn hook nhiều lần, chặn lặp trong khoảng ~1s.
- **QC**:
  - Click từng loại ad ở từng màn: splash, FO, Home, inter, app-open resume.
  - Đổi RC toast ↔ notification.
  - Thử delay 0 và 3000.
  - Bấm noti thì đi Splash (MO-78).
  - Không có toast đôi.

## MO-80 — Banner refresh theo từng network (plugin "banner per buyer")

- **Yêu cầu**:
  - Dùng plugin refresh banner theo ad source (buyer), áp dụng diện rộng.
  - Mặc định: Meta 30s, AdMob 30s, AppLovin 10s, InMobi 20s, buffer 3.
  - MO chỉnh qua RC, ví dụ Meta 10s và AdMob 10s.
  - Bảng key lấy theo ảnh trong sheet (`assets/refs/MO-80-1.jpg`).
- **Nghiệm thu**:
  - Banner tự xoay theo đúng rate của network đang thắng.
  - Đổi RC thì có tác dụng từ lần mở app sau.
  - Không bị refresh chồng 2 lần.
  - App xuống nền thì banner ngừng xoay.
- **SDK**:
  - xtechads CHƯA hỗ trợ.
  - `configs.bannerReloadTime` (20000) và `bannerMinReloadTime` (1) có trong `domain/models/AdsConfig.kt` (`NativeBannerSettings`) nhưng không chỗ nào đọc.
  - Thứ duy nhất đang chạy: `autoReloadOnImpression` khai cho từng adunit (ms). `NativeBannerGroupViewImpl` reload sau khi ad IMPRESSED được N ms, không phân biệt network.
  - App dùng SDK không tự lấy được unit id: `ads_config` đã mã hoá và model bị R8 obfuscate. Muốn làm đúng phải thêm vào SDK.
- **Chuẩn A013**:
  - Không có (sheet ghi a013 = 0).
  - `ads_config` của A013 vẫn khai `bannerReloadTime` nhưng không có tác dụng.
- **Mẫu tham chiếu**:
  - **Plugin Google `googlebannerrefresh`** (Apache 2.0, `Constants.VERSION` 1.7.0):
    - `BannerRefreshView`: thay cho `AdView`. Có `load(AdRequest.Builder)`, `pause()`, `resume()`, `destroy()`.
    - `BannerRefreshConfiguration.Builder`:
      - `setAdsBufferSize`: kẹp 1–10, mặc định 3.
      - `setDefaultRefreshRateInSeconds`: kẹp 5–150, mặc định 120.
      - `setAdSourceRefreshRatesInSeconds(map AdSource.* → giây)`: rate của AdMob network tự áp luôn cho AdMob waterfall.
    - `AdSource`: danh sách id ad source.
    - `BannerManager`: giữ buffer và xoay ad. Tự gắn extra `_noRefresh` vào request để tắt auto-refresh của ad unit.
  - **a036** (non-SDK, đang chạy):
    - `settings.gradle.kts` include `:googlebannerrefresh`.
    - `ads/adunit/banner/view/BannerView.kt` dựng config từ `ads_config` `bannerAds.refresh`. Model là `BannerRefreshConfig` trong `ads/adunit/AdsConfig.kt`, gồm `defaultRate`, `bufferSize`, `rateAdmob`, `rateMeta`, `rateApplovin`, `rateInmobi`.
    - Map source: Meta (+bidding), AppLovin (+bidding), InMobi (+bidding, +exchange).
    - Tự bắn `iaa_*` và `banner_ad_impression` trong listener.
  - **A014** (lịch sử):
    - Commit `5e0b360` (v1.3.2, P2299 "SDK banner per buyer plugin") nối RC `banner_refresh_*`.
    - Commit `5e23b52` (V1.3.4, lúc chuyển sang xtechads) bỏ module khỏi build. Thư mục module vẫn còn trên đĩa nhưng KHÔNG có trong `settings.gradle.kts`.
  - **a018**: sheet ghi đã làm, nhưng repo không có trên máy này.
- **Remote config** (theo ảnh sheet):
  - `banner_refresh_default_rate` (Long, giây, mặc định `30`, kẹp 5–150): rate cho source không có override riêng.
  - `banner_refresh_buffer_size` (Long, mặc định `3`, kẹp 1–10): số ad preload trong buffer.
  - `banner_refresh_rate_admob` (`30`): tự áp cho cả AdMob waterfall.
  - `banner_refresh_rate_meta` (`30`): áp cho cả waterfall và bidding.
  - `banner_refresh_rate_applovin` (`10`).
  - `banner_refresh_rate_inmobi` (`20`).
  - Alias:
    - a036 dùng JSON `bannerAds.refresh.{defaultRate,bufferSize,rateAdmob,rateMeta,rateApplovin,rateInmobi}`. Trong code, rate default đều là 30 và buffer là 3.
    - A014 bản cũ có thêm `banner_refresh_rate_{mintegral,pangle,unity}`, buffer default là 1.
- **Cách làm**:
  1. **App dùng SDK: thêm hỗ trợ vào xtechads** (khuyến nghị, cần chốt với SDK owner):
     - Banner dùng `BannerRefreshView` thay `AdView` khi tính năng được bật.
     - Config lấy từ `configs` của `ads_config` (thay cho key không dùng `bannerReloadTime`), rồi override bằng các RC ở trên.
     - App chỉ cần bump version SDK.
     - Đọc `ads/adunit/banner/BannerAdUnit.kt` và `BannerGroupContent` trong `NativeBannerGroupViewImpl.kt` ở SDK.
  2. **App non-SDK** (A028, a041): làm như a036.
     - Include module.
     - Dựng config trong composable banner.
     - Giữ tracking IAA.
     - Đọc a036 `BannerView`.
  3. **Map đủ biến thể source**: Meta + Meta bidding, AppLovin + bidding, InMobi + bidding + exchange.
  4. **Nối lifecycle**: `pause()` ở onPause, `resume()` ở onResume, `destroy()` khi rời composition.
- **Bẫy**:
  - RC số phải khai Long. A014 bản cũ khai Int nên luôn rơi về default.
  - Plugin đã tắt auto-refresh của ad unit, nên rate cài trên AdMob console không còn tác dụng. Đừng đi tìm lỗi ở console.
  - AdMob console chỉ cho 30–120s, plugin cho 5–150s. Rate dưới 30s cho AdMob (ví dụ 10s theo sheet) là quyết định của MO, cần MO xác nhận về policy.
  - Buffer lớn thì nhiều request hơn, ảnh hưởng match rate và show rate.
- **QC**:
  - Logcat tag `BannerRefresh` thấy banner xoay đúng rate theo từng source.
  - Đổi RC thì lần mở sau áp dụng.
  - App ở nền không có request.
  - Event IAA của banner đủ.

## MO-81 — Inter in-app cả khi bấm back cứng / vuốt back (predictive back)

- **Yêu cầu**: chỗ nào nút back trên UI đang show `inter_inapp`, thì back cứng của máy và cử chỉ vuốt back (cả 2 mép) cũng phải show y như vậy.
- **Nghiệm thu**:
  - Android ≤13 (nút back) và Android 14+ (vuốt) đều show inter (theo interval MO-82), rồi mới về màn trước.
  - Vuốt dở rồi kéo về (huỷ): không có ad, không điều hướng.
  - Màn FO và Home không bị chèn inter sai chỗ.
- **SDK**: Không có helper cho back. Show ad qua `AdGroupUnit.showFullScreen`, app tự bọc thành `showInterInApp`.
- **Chuẩn A013**:
  - `ui/base/AppBackHandler.kt`, composable `GeneralBackHandler(onBack, onPredictiveBack)`:
    - API ≤ 33: bật `BackHandler`, gọi `onBack`.
    - API ≥ 34: bật `PredictiveBackHandler`. Thu progress của gesture; gesture hoàn tất mới gọi `onPredictiveBack`; gesture bị huỷ thì bỏ qua.
  - Mỗi màn tạo 1 lambda back = `adsManager.showInterInApp(context) { pop }`. Lambda này truyền cho CẢ nút back trên header lẫn cả 2 tham số của `GeneralBackHandler`.
    - Gọi trực tiếp: `RecoveredScreen`, `JunkRemoverScreen`, `StorageDetailScreen`, `DetailScreen`.
    - Đi qua state / ViewModel: `ProtectorScreen`, `ScanScreen`, `CropScreen`.
  - `AdsManager.showInterInApp(context, onNext)` gọi `interInApp.showFullScreen`. Mọi nhánh (show được, lỗi, không có ad) đều gọi `onNext`.
  - Manifest A013 không khai `enableOnBackInvokedCallback`.
- **Mẫu khác**:
  - **A045** `ui/properties/GeneralBackHandler.kt`:
    - Chỉ 1 `BackHandler`. Log `button_click` (`device_back`), mặc định chèn inter (`showInterAd`; tắt ở màn FO).
    - Ghi chú trong code: chèn ad ở `NavDisplay.onBack` KHÔNG có tác dụng, vì handler của màn đã nuốt back trước.
  - **A47** `ads/AdsEffects.kt` `InterBackHandler` + `common/utils/DeviceBackHandler.kt` (log `BtnDeviceBack`). Ghi chú: handler của màn đăng ký sau handler của `NavDisplay` nên thắng (dispatcher chạy LIFO).
  - App có khai `android:enableOnBackInvokedCallback="true"`: A014, a016, A028, a031, a033, a037, Langofy, a044, A045, A47.
- **Placement / tracking**:
  - Placement `inter_inapp`.
  - Nên log back cứng như 1 nút bấm (`button_click`, `button_name` = `device_back` / `BtnDeviceBack`) để gộp được vào funnel.
- **Cách làm**:
  1. **1 composable back dùng chung cho cả app**: `BackHandler` cho API ≤33 + `PredictiveBackHandler` cho API ≥34, hoặc chỉ 1 `BackHandler` như A045. Đọc `ui/base/AppBackHandler.kt` ở A013.
  2. **Mỗi màn có inter khi back**: tạo đúng 1 lambda "back có ad", dùng chung cho header back và back handler. Đọc `RecoveredScreen` ở A013 làm mẫu.
  3. **Vị trí handler**: đặt bên trong nội dung của entry (đăng ký sau `NavDisplay`) để chặn trước `NavDisplay.onBack`.
  4. **Fragment / XML** (a033, a041, a031): dùng `onBackPressedDispatcher.addCallback(OnBackPressedCallback)`, gọi cùng hàm show inter.
- **Bẫy**:
  - Gọi `GeneralBackHandler` của A013 mà chỉ truyền `onBack`: ở API 34+ back bị nuốt và không làm gì, vì `onPredictiveBack` = null.
  - Cả handler của màn lẫn `NavDisplay` cùng xử lý thì sẽ pop 2 lần.
  - Bấm back liên tục khi ad đang load: show ad / điều hướng bị lặp. Cần cờ "đang xử lý".
  - Không chèn inter ở:
    - Home: back = popup Exit.
    - Splash / FO: có `BackHandler` chặn back.
  - Đang mở dialog / sheet thì back phải đóng dialog trước.
- **QC**:
  - Máy Android 13 (nút back) và Android 14/15 (vuốt mép trái + phải; vuốt dở rồi kéo về).
  - Header back.
  - Còn trong interval: không có ad. Hết interval: có ad.
  - Tắt mạng: back vẫn chạy bình thường.

## MO-82 — Interval inter: preload trước (interval − lead) giây

- **Yêu cầu**:
  - Interval là x giây thì đúng x giây sau lần show trước phải có sẵn ad để show.
  - Muốn vậy, bắt đầu load ở mốc (x − 5) giây, kể cả khi user không chuyển màn.
  - Lý do: đa số app chỉ load khi chuyển màn, nên tới hạn vẫn chưa có ad.
- **Nghiệm thu**:
  - Show inter, rồi đứng yên ở 1 màn: tới mốc (interval − lead) thấy request `inter_inapp`.
  - Trigger sau mốc interval: show ngay.
  - Trigger trước mốc: không show.
  - App ở nền: không có request.
- **SDK**:
  - `domain/preference/AdsSharedPref.kt` có `interval_skip_inter` (20000 ms) và `screen_skip_inter` (3).
  - SDK KHÔNG có scheduler preload.
  - `AdGroupUnit.showFullScreen` không tự kiểm interval.
  - Ad inter hết hạn sau khoảng 1h (`AdUnit.adTtlMs` trừ 5 phút).
- **Chuẩn A013** (`ads/AdsManager.kt`):
  - `lastShowAds`: đóng dấu trong `markShown()`, chạy khi có IMPRESSION của mọi inter (các unit splash và `inter_inapp`, qua `onImpression`).
  - `schedulePreloadInterInApp()`, chạy theo thứ tự:
    1. Huỷ job cũ.
    2. Chờ tới mốc tuyệt đối `lastShowAds + interval_skip_inter − preload_lead_inter`.
    3. Thử load tối đa `PRELOAD_MAX_ATTEMPTS` (3) lần, mỗi lần cách nhau `PRELOAD_RETRY_DELAY` (3s).
    4. Dừng nếu đang show ad, hoặc unit đang LOADING / SUCCESS / TIMEOUT.
  - `loadInterInApp()` chỉ gọi lại schedule.
  - Kích hoạt từ `ui/common/TrackingScreenName.kt`: mỗi lần đổi màn, và chỉ khi màn được phép có inter (`LocalAllowShowInterInApp`, set bằng `entryTag(allowShowInterInApp = true)` trong `AppNavigation`).
  - `showInterInApp` chỉ show khi ad đã load xong. Nghĩa là gate thực tế = "đã có ad hay chưa".
  - `canShowInter` (kiểm `screen_skip_inter` HOẶC interval) có khai nhưng KHÔNG ai dùng.
  - **Lệch chuẩn**:
    - Không kiểm thời gian lúc show. Ad load xong sớm thì có thể show trước mốc vài giây.
    - Chỉ arm lại khi đổi màn.
    - Interval tính từ lúc impression, không phải lúc đóng ad.
- **Mẫu chặt hơn (a044 `ads/AdsManager.kt`)**:
  - `canShowInterInApp`: `elapsedRealtime − lastShowInterstitial ≥ time_interval_inter`.
  - `showInterInApp` là cửa duy nhất. Lỗi hoặc không có ad thì không đóng dấu.
  - `onInterClosed`: đóng dấu, rồi `armInterPreload` (chờ interval − buffer − thời gian đã trôi, rồi `loadOrReload`).
  - `onStop` huỷ timer; `onStart` arm lại.
- **Remote config** (đơn vị lệch nhau giữa các app, kiểm tra kỹ):
  - **Lead / buffer**:
    - `preload_lead_inter` (Long ms, `5000`): A013.
    - `preload_inter_buffer_second` (Long giây, `5`): A014, a016, a034, a044, A045, A47, a041 core/ads. a033 đọc rồi ×1000.
    - `second_preload_inter_buffer` (giây, `5`): a039.
    - `preload_inter_interval` (giây, `5`): a27, a037. a037 dùng làm lead cho cửa sổ cố định 15s / 60s.
  - **Interval**:
    - `interval_skip_inter` (Long ms, `20000`): SDK, A013, a039, a041. A028 dùng `15000`, a036 dùng `20000`.
    - `interval_inter_inapp` (ms): A47 `20000`, Langofy `30000`.
    - `time_interval_inter` (ms, `20000`): a044.
    - `inter_all_interval` (ms): a033 `15000`, Langofy `45000`.
  - **Điều kiện**:
    - `screen_skip_inter` (số màn): SDK `3`, A028 / a036 `2`.
    - `inter_interval_condition` (`"or"` / `"and"`, a039): cách gộp điều kiện số màn và thời gian.
  - **KHÔNG phải interval inter** (dễ nhầm): `min_ad_interval_alt` (a037, trong JSON `language_config`, ms) và `min_ad_interval_language_alt` (A013) là khoảng reload native ở màn Language Alt.
- **Placement / tracking**:
  - Placement `inter_inapp`. A045 tách thêm `inter_tools`, `inter_compress`…
  - Kiểm tra bằng event `iaa_request` hoặc log của `AdsManager`.
- **Cách làm**:
  1. **1 cửa duy nhất `showInterInApp(activity, onNext)`**:
     - Đủ thời gian (now − lastShow ≥ interval) mới show.
     - Chưa đủ hoặc không có ad thì gọi `onNext` ngay.
     - Đọc A013 `AdsManager.showInterInApp` và a044 `showInterInApp`.
  2. **Đóng dấu `lastShow`**:
     - Đóng dấu khi ad thật sự hiện. Chốt 1 quy ước: lúc impression hay lúc close.
     - Dùng cùng 1 loại đồng hồ với chỗ gate.
  3. **Scheduler**:
     - Sau mỗi lần show (và lần đầu vào màn chính) hẹn load ở mốc (interval − lead).
     - App xuống nền thì huỷ; lên lại thì arm lại.
     - Load fail thì retry vài lần.
     - Đọc `AdsManager.schedulePreloadInterInApp` ở A013.
  4. **Arm thêm** ở chỗ đổi màn (như `TrackingScreenName` của A013) cho chắc.
  5. **Khai RC đúng đơn vị**. App dùng giây thì nhân 1000 ở đúng 1 chỗ.
- **Bẫy**:
  - Nhầm ms và giây: lead của A013 là ms, đa số app khác dùng giây.
  - RC số khai Int thì luôn trả default.
  - Không load khi đang có ad khác hiện (A013 bỏ qua khi `isShowingAds`).
  - Không huỷ timer khi app ở nền thì tốn request thừa.
  - Ad preload để quá 1h sẽ hết hạn, phải load lại.
  - Ad vừa hiện mà user chuyển màn ngay, có thể arm trước khi dấu impression về, nên lần arm đó tính theo mốc cũ. Arm thêm lúc đóng ad để chắc chắn.
- **QC**:
  - Interval 20s, lead 5s: show ad, đứng yên; khoảng giây thứ 15 có request; bấm trigger ở giây 20 thấy ad.
  - Bấm ở giây 10: không có ad.
  - Xuống nền 30s rồi lên lại: không có request trong lúc ở nền.

## MO-93 — Quay về từ ad thì tự sang màn kế (luồng FO)

- **Yêu cầu** (luật chung): ở các màn FO (Splash, Language, Language Alt, Select, Onboard, native full), user click ad rồi quay lại app thì app tự đi tiếp sang màn kế, hoặc làm hành động MO cấu hình. Không bắt user tự đóng ad hay bấm lại.
- **Nghiệm thu**:
  - Click native ở từng màn FO, quay lại: đúng hành động theo RC.
  - Click inter splash, quay lại: đúng `logic_pass_splash`.
- **SDK**:
  - Namespace `actionClicked` trong `ads_config`: `none` | `tooltip` | `disable` | `reload` | `next_screen` | `custom`.
    - `reload` / `disable`: `NativeBannerGroupViewImpl` tự xử lý khi resume.
    - `next_screen`: cần composable `NativeAdClickNextAction(adGroupUnit) { onNext }`. Lúc ON_RESUME nó đọc `AdGroupUnit.isClicked`; khớp action thì gọi `onNext`.
  - `AdGroupUnit.onClicked` / `isClicked` để app tự bắt click.
- **Chuẩn A013**:
  - **Native FO**:
    1. `AdsManager` gán `onClicked` của unit để bật cờ: `clickedLanguage`, `clickedNativeLangAlt`, `clickedNativeOb1/Ob3`, `clickedNativeFsn`…
    2. Màn đọc cờ trong `LifecycleResumeEffect`, tra RC `action_clicked_native_<x>` rồi làm hành động tương ứng (`next_screen` / `finish` / `clear_ads` / `tooltip` / `none`).
    3. Xoá cờ.
    - Key và default của từng màn do nhóm language / onboard / select ghi (MO-39, MO-47, MO-56…60).
  - **Native full preparing**: `ui/base/NativeFullPreparingView.kt` dùng `NativeAdClickNextAction` (namespace `native_preparing` để `next_screen`), đặt SAU `NativeBannerGroupView`.
  - **Inter splash**: `ads/InterSplashClickAction.kt` + RC `logic_pass_splash`:
    - `auto_next`: user quay lại thì đóng AdActivity. App đã điều hướng lúc ad hiện, nên user đứng ngay ở màn kế.
    - `reload`: đóng ad đã click, rồi show unit dự phòng `inter_splash_backup(_high)`, có `AdReloadCover` che.
    - `keep_state`: để nguyên ad.
  - **Native full splash**: `SplashNativeFullContent` đọc `clickedNativeFullSplash` lúc resume; nếu là `auto_next` thì gọi `onNext`.
- **Remote config**:
  - `logic_pass_splash` (String, mặc định `"reload"`; giá trị lạ thì coi như `auto_next`).
  - `action_clicked_native_*` (String, theo từng màn). Default ở A013:
    - `_lang`: `"tooltip"`.
    - `_lang_alt`: `"next_screen"`.
    - `_ob1`: `"next_screen"`.
    - `_ob3`: `"finish"`.
    - `_fsn`: `"next_screen"`.
  - Namespace `actionClicked` trong `ads_config`.
- **Cách làm**:
  1. **Mỗi unit FO bắt click**: dùng `onClicked` để bật cờ, hoặc đọc `AdGroupUnit.isClicked`. Đọc các cờ `clickedNative*` trong `AdsManager` ở A013.
  2. **Màn FO**:
     - `LifecycleResumeEffect` đọc cờ, tra RC.
     - Gọi CHÍNH hàm "Next / Continue" của màn (tôn trọng RC `*_next`).
     - Xoá cờ.
     - Đọc `LanguageAltScreen` / `OnBoardContentNew` ở A013.
  3. **Màn dùng native theo config**: thêm `NativeAdClickNextAction` sau `NativeBannerGroupView`, và set namespace `actionClicked: next_screen`.
  4. **Splash inter**: theo `InterSplashClickAction` + `logic_pass_splash` (chi tiết ở nhóm splash).
- **Bẫy**:
  - ON_RESUME cũng chạy sau dialog xin quyền hay sau khi về từ Settings. Chỉ hành động khi cờ click đang bật.
  - Phải xoá cờ ngay, nếu không sẽ đi tiếp 2 lần.
  - `actionClicked` `reload` / `disable` và `next_screen` loại trừ nhau: SDK xoá `isClicked` khi xử lý reload / disable.
  - Màn cuối Onboard: "next" nghĩa là vào Home / Select theo RC, không phải sang trang kế.
- **QC**:
  - Từng màn FO × từng giá trị RC.
  - Click ad, bấm Home của máy, rồi mở lại app (không qua landing): vẫn đúng hành vi.

## DEV-16 — App open ad khi quay lại app: tối đa 1 lần / 4 giờ (RC)

- **Yêu cầu**: show app-open ad khi user quay lại app từ nền, tối đa 1 lần mỗi 4 tiếng, chỉnh được bằng RC.
- **Nghiệm thu**:
  - Ra / vào app nhiều lần trong 4h: chỉ thấy 1 app-open. Sau 4h: lại thấy.
  - Kill app vẫn giữ mốc thời gian.
  - RC = 0: không giới hạn.
- **SDK** (`ads/base/BaseAds.kt`, luồng app resume):
  - Chỉ chạy ở `onActivityResumed` của Activity implement `AdHostActivity`, và chỉ khi app thực sự đã xuống nền (`ProcessLifecycleOwner` onStop).
  - Bỏ qua khi:
    - `disableAdResumeOneTime` đang bật,
    - `canShowAppResume` = false,
    - đang show ad,
    - `TrackingState.lastScreen` rỗng hoặc nằm trong `screenSkipAdResume`.
  - Sau đó: load placement `app_resume` lúc quay lại (timeout = namespace `timeout`), có callback `showResumeLoading` / `hideResumeLoading`. Xong thì gọi `onAppResumeClosed`.
  - KHÔNG có giới hạn tần suất. `canShowAppResume` là `open` nên app override được.
  - TTL 4h của AppOpen (`AdGroupUnit.adTtlMs`) chỉ là thời hạn cache ad, không phải giới hạn tần suất show.
- **Chuẩn A013**:
  - KHÔNG có giới hạn tần suất.
  - `AdsManager.screenSkipAdResume` gồm: `""`, lock screen, Splash, Setting, LanguageSetting, Webview.
  - Không override `canShowAppResume`.
  - `AppNavigation` vẽ `LoadingAdsView(adsManager.isShowingAdResume)`.
  - Trước mỗi intent mở ra ngoài app đều gọi `AppUtils.needSkipResume()`.
- **Mẫu khác**:
  - a041 (non-SDK) `core/ads/.../base/BaseAds.kt`: `resumeAds.timeInterval` trong `ads_config` (ms, mặc định 15000); `lastResumeShownAt` đóng dấu lúc `onAdOpenShow`.
  - A014 / a031 / a033 / a034 override `canShowAppResume` bằng cờ, không theo thời gian.
- **Remote config**:
  - ĐỀ XUẤT `app_resume_interval_minutes` (Long, mặc định `240`; `0` = không giới hạn).
  - Alias: a041 `resumeAds.timeInterval` (ms, trong `ads_config`).
- **Cách làm**:
  1. **Override `canShowAppResume`** trong `AdsManager` của app:
     - Điều kiện = `super` VÀ (cap = 0 HOẶC now − `lastAppResumeShownMs` ≥ cap × 60000).
     - Đọc `BaseAds` (phần app resume) ở SDK.
  2. **Đóng dấu `lastAppResumeShownMs`** (lưu pref để sống qua kill app) khi app-open THỰC SỰ hiện: gán `appResume.onImpression` trong `AdsManager`, hoặc dùng `onAppResumeClosed`.
  3. **Không đụng splash hay inter khác**: giới hạn này chỉ áp cho resume.
- **Bẫy**:
  - Đóng dấu lúc mới "thử show" thì no-fill cũng ăn mất 4h.
  - Giữ mốc trong RAM thì kill app là mất giới hạn.
  - Dùng `currentTimeMillis` để giữ khoảng 4h qua reboot. Nếu hiệu số < 0 (user chỉnh giờ) thì coi như đã hết hạn chờ.
  - `disableAdResumeOneTime` (quay về từ Settings / share / click ad) vẫn phải được ưu tiên.
- **QC**:
  - Set RC = 1 phút để test.
  - Vào / ra app nhiều lần.
  - Kill app khi còn trong cửa sổ giới hạn.
  - RC = 0.

## DEV-21 — Home: collapsible ad, đóng còn mini, quay lại Home lại bung

- **Yêu cầu** (`ScrHomeApp`):
  - Vào Home có collapsible ad.
  - Bấm đóng thì vẫn còn mini banner.
  - Mỗi lần hoàn thành action rồi quay về Home thì lại thấy collapsible bung ra.
- **Nghiệm thu**:
  - Lần đầu vào Home: ad bung.
  - Bấm collapse: còn bản nhỏ.
  - Vào feature, xong, quay lại Home: bung lại (ad mới).
  - User đã mua IAP: không có ad.
- **SDK** (2 cách):
  - **Native collapsible**:
    - Adunit `useNativeCollapsible: true`, layout có nút `btn_collapse` (layout `native_collapse_open_*`).
    - `NativeBannerGroupView(collapsedLayout = …)`:
      - Mặc định là `native_none_media_action_big_filled` (bản mini).
      - `null` = ẩn hẳn khi collapse.
    - Trạng thái collapse lưu bằng `rememberSaveable` theo request id của ad, nên chỉ ad mới mới bung lại.
  - **AdMob collapsible banner**:
    - Adunit `format: banner`, `bannerType: "BANNER_COLLAPSIBLE"`. `BannerAdUnit` gắn extra `collapsible=bottom`.
    - Đóng thì AdMob để lại banner neo.
    - Muốn bung lại thì phải có request mới.
  - Namespace `reloadWhenResume: true`: `NativeBannerGroupViewImpl` load lại ở mỗi lần ON_RESUME / mỗi lần màn compose lại. Chỉ load khi `shouldLoadAd()` đúng (ad hiện tại đã IMPRESSED, chưa có, hoặc hết hạn) và ad chưa bị click.
- **Chuẩn A013**:
  - KHÔNG có.
  - `HomeContentNew` (RC `new_home_screen`, mặc định true) chỉ có native `home_top` / `home_bottom` / `home_rmj`.
  - `HomeContent` cũ có `banner_home` (adaptive).
  - `ads_config` A013 có namespace `banner_home` adaptive, nhưng không có placement.
- **Mẫu**:
  - **a016**: `ui/screen/home/view/HomeContent.kt` (bottomBar) dùng `ads/adunit/common/DualNativeAdsView.kt`:
    - Native nhỏ `nativecollab_home1` nằm dưới.
    - Native collapsible `nativecolab_home` đè lên, `collapsedLayout = null`. Đóng thì lộ bản nhỏ bên dưới.
    - RC `nativeSplashCollapse` (đúng chuỗi key này, mặc định true). False thì dùng `banner_home`.
    - Namespace `nativecolab_home` có `autoReloadOnImpression` 20000.
  - **a27**: `HomeContentNew` bottomBar dùng `collab_home` (`collapsedLayout = null`), RC `show_collab_home`, namespace `reloadWhenResume` true.
  - **A014**: từng có `collab_home` trước v1.3.2 (commit `64580d6` thay bằng banner). Namespace giờ đã tắt.
  - **a031**: có `banner_collapsible` (BANNER_COLLAPSIBLE) nhưng không ở Home.
- **Remote config**:
  - Bật / tắt: a27 `show_collab_home` (Boolean, true), a016 `nativeSplashCollapse` (Boolean, true).
  - Layout và format chỉnh trong `ads_config` (remote).
- **Cách làm**:
  1. **Chốt với MO**:
     - Dùng native collapsible hay AdMob collapsible banner.
     - "Mini" là `collapsedLayout` (với native) hay banner neo (với AdMob).
  2. **`ads_config`**:
     - Thêm namespace + placement cho Home (vd `collab_home`).
     - Adunit `useNativeCollapsible: true` + layout `native_collapse_open_*`, hoặc `bannerType: BANNER_COLLAPSIBLE`.
     - `reloadWhenResume: true`, để mỗi lần về Home có ad mới và ad bung lại.
  3. **Home**:
     - Gắn `NativeBannerGroupView(placement = …, collapsedLayout = …)` vào `bottomBar` của BaseScreen Home, không đè lên CTA.
     - Thêm RC bật/tắt; khi tắt thì rơi về banner thường.
     - Đọc a27 `HomeContentNew` và a016 `DualNativeAdsView`. Ở A013, chỗ gắn là `ui/screen/home/view/HomeContentNew.kt`.
- **Bẫy**:
  - Không reload thì quay lại Home sẽ nhận lại ad cũ cùng trạng thái collapsed đã lưu, nên không bung.
  - `reloadWhenResume` cũng reload mỗi lần app từ nền lên, tức nhiều request hơn. Cân đối với `autoReloadOnImpression`.
  - Namespace `actionClicked` (reload / disable) quyết định hành vi sau khi click.
  - Collapsible có thể đè nội dung cuối list, nhớ chừa padding.
- **QC**:
  - Vào Home; bấm collapse.
  - Vào 1 feature, hoàn tất, về Home: bung lại.
  - Ra nền rồi vào lại.
  - User IAP.
  - Tắt RC.

## CC-2 — Bắt xem N reward ad mới được dùng tính năng (ứng viên)

- **Yêu cầu**:
  - User bấm dùng tính năng thì phải xem đủ N ad reward mới được xử lý. N chỉnh bằng RC.
  - User thoát app hoặc thoát tính năng thì reset bộ đếm.
  - Gọi ad không được thì toast "Ad not available right now, pls try again later".
  - Sheet: chưa làm (28/05/2026).
  - Ảnh tham khảo: popup "Unlock Generation", nút "Watch Ad (3/10)".
- **SDK**:
  - `ads/adunit/adgroup/view/FullscreenAdObserver.kt`: `FullscreenAdObserver(placement, isRequested, onDismissRequest, screen, onUserEarnedReward, preloadOnEnter, onAdShow, onAdClosed(earned), onFailed, loading)`.
  - Format `reward` / `reward_interstitial` lấy theo `ads_config`.
  - `onFailed` được gọi khi placement tắt, không fill, hoặc hết timeout.
- **Chuẩn A013**: KHÔNG có. A013 không có namespace reward; pref `recover_ad_type` không ai đọc.
- **Mẫu**:
  - a037 `LevelAutoCleanScreen`: `FullscreenAdObserver` placement `reward_autoclean`.
    - `onAdClosed(earned)`: bắt đầu tính năng.
    - `onFailed`: gọi `onStartAdFailed()`.
    - Inter fail: toast `ad_not_available`.
  - A045 `ads/AdsEffects.kt` `rememberRewardGate`: fail thì cho chạy luôn, NGƯỢC với CC-2. Xem thêm `docs/features/reward-inter-ads.md`.
  - a034 `RewardAdHost`.
  - A014 `ui/dialog/AdsErrorDialog.kt`.
- **Remote config**: ĐỀ XUẤT `reward_required_count` (Long, mặc định `1`). Nếu nhiều tính năng cần N khác nhau thì dùng `reward_required_count_<feature>`.
- **Cách làm**:
  1. Bộ đếm nằm trong state của tính năng, không lưu pref.
  2. Mỗi lần `earned` thì +1.
  3. Đủ N thì chạy tính năng và reset bộ đếm.
  4. Reset khi rời tính năng (dispose / `onCleared`) và khi app xuống nền (theo spec).
  5. Ad fail: toast, giữ nguyên số đã xem.
  6. Nút hiện tiến độ (k/N).
  7. Sau mỗi lần đóng ad thì preload sẵn ad kế tiếp.
- **Bẫy**:
  - Chỉ đếm khi `earned` = true. Đóng sớm thì không tính.
  - N lớn làm UX tệ, cần MO chốt mức.
  - Nút phải ghi rõ là xem quảng cáo (policy: reward ad phải do user chủ động chọn).
  - Không được chặn user vĩnh viễn khi mạng hoặc ad lỗi: fail thì cho thử lại.
- **QC**:
  - N = 1 và N = 3.
  - Đóng ad giữa chừng.
  - Mất mạng.
  - Ra nền rồi vào lại: bộ đếm về 0.

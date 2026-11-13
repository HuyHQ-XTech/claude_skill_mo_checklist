# Setup — SDK, consent, Firebase, revenue (MO-5..MO-20, MO-100, EXT-RC-GROUP)

> Recipe đối chiếu lần cuối với A013 commit `f784827` (branch v1.2.7, xtechads 1.8.2) và source xTechSDK (nhánh `fix_native`, có thể mới hơn 1.8.2). Skill **không chép code**: mọi chi tiết code đọc từ A013 bản hiện tại theo file + symbol nêu dưới.
> Ghi chú Ref A047/A048, "App đã làm: A049" và các đoạn ghi "10/2026" đối chiếu ngày 15/10/2026: A47 `61711d3` (xtechads 1.7.5), A048 `fcecc4a` (1.7.6), A049 `78a9c9b` + thay đổi chưa commit (1.8.7), source xTechSDK nhánh `main` (1.8.5 + "support a049") và AAR 1.8.7.
> Mã app theo `apps.json`: a27 = a027, A47 = a047, Langofy = a042, qibla = a031, Duo-Speak = a041, PDF Reader = a033, A014/A028/A045 = a014/a028/a045.
> Quy ước đường dẫn: file Kotlin A013 tính từ `app/src/main/java/com/example/a013_recovery/`; manifest/res/gradle/config tính từ gốc repo. App khác: tính từ package gốc của app (tìm theo tên file + symbol, thư mục repo ở `apps.json`).

## Tổng quan nhóm

**Trình tự khởi động chuẩn (app dùng xtechads):**
1. `Application.onCreate` → `startKoin` nạp module SDK (`com.example.xtechads.di.repositoryModule`, `adsModule`) **trước** module app. Lúc này các singleton eager chạy: `AdsManager` của app (kế thừa `BaseAds`, `createdAtStart`) → `LicenseGuard.verify` (crash `Unauthorize` nếu applicationId chưa whitelist) + chốt tham số RC; `RevenueManager` (SDK, eager) → `AppsflyerManager` init/start AppsFlyer trên IO nếu `AppConfig.appsflyerKey` khác rỗng; `RemoteConfigManager` (module `xtechcore`, eager ở source mới) → fetch RC trên IO, cache-first.
2. `MainActivity` (implement `AdHostActivity`) `onCreate` → `requestUMP(activity, enableDebug = BuildConfig.DEBUG, resetData = false)`.
3. UMP kết thúc ở **mọi nhánh** (đồng ý, không cần, lỗi) → SDK `initMobileAds()` (private): `consentFinished = true` rồi `MobileAds.initialize` trên IO → `mobileAdsFinish = true`; bắn `tracking_consent` + `sdk_init` (`ump_finish`, `mobile_ads_finish`). User cũ đã có consent (`canRequestAds()`) → init ngay lúc gọi `requestUMP`, không chờ request info; form (nếu cần hỏi lại) vẫn hiện sau đó và đóng form không bắn gì thêm (MO-22, MO-25).
4. Mọi `AdGroupUnit.loadAd` bị chặn bởi `canLoadAd` (= `canShowAds` và có mạng; `canShowAds` = `umpAllowed` và chưa mua `isPurchase`; `umpAllowed` = `canRequestAds()` hoặc `privacyOptionsRequirementStatus` khác REQUIRED) → gọi load khi offline, hoặc khi UMP đã biết cần consent mà chưa có = status `FAIL` ngay. Lúc `requestConsentInfoUpdate` chưa trả về hoặc lỗi (status UNKNOWN) thì `umpAllowed` = true → request **vẫn đi** dù chưa consent (MO-9, MO-22).
5. Doanh thu IAA: mỗi `OnPaidEvent` trong ad unit SDK → `RevenueManager.logAdRevenue` fan-out 3 đích: AppsFlyer (`logAdRevenue`), Firebase `in_app_ad_impression`, Facebook `AdImpression`. Doanh thu IAP: SDK **không** làm, app tự log.

**Các mục liên quan nhau:** danh tính app MO-6 (package) · MO-7 (AdMob App ID) · MO-11 (Facebook ID); consent MO-8 · MO-9 · MO-10 (luồng splash ở MO-22/MO-24); SDK quảng cáo/attribution MO-12 · MO-13 · MO-14 · MO-15 · MO-18 · MO-5 (billing); Firebase MO-16 · MO-17 (cổng chờ RC ở splash: MO-27); build/layout MO-19 · MO-20. MO-100 là checklist tích hợp SDK tổng. Gộp key RC phẳng sang JSON theo màn: EXT-RC-GROUP (cuối file). Init song song / tối ưu init: DEV-3 và MO-97 nằm ở `splash.md`.

**Hạ tầng dùng chung ở A013:** `di/Modules.kt` (`appModule`: `SharedPrefs` bind `XtechSharedPref`; `adsModule`: `AppConfig` + `AdsManager` `createdAtStart` bind `BaseAds`), `App.kt` (`startKoin`, `initFCM`, `remoteConfig.fetchRemoteConfig()`), `MainActivity.kt`, `ads/AdsManager.kt`, `domain/preference/SharedPrefs.kt` (mọi key RC = 1 property `SharedPreferenceProperty("<key>", default)`; RC manager ghi mọi key REMOTE vào cùng file prefs `packageName`), `app/config/ads_config.json` (plugin `com.xtech.ads` mã hoá thành `assets/ads_config.dat`; RC key `ads_config` đè toàn bộ).

**App không dùng xtechads:** A028, a036 (`ads/base/BaseAds.kt` + `ads/base/ConsentHelper.kt`, `ads/remoteconfig/RemoteConfigManager.kt`, `ads/adjust/AdjustManager.kt`, RevenueCat `ads/payment/PaymentManager.kt`); a041 Duo-Speak (module `core/ads`: `ConsentHelper`, `remoteconfig/RemoteConfigManager`, `appsflyer/AppsflyerManager` + `RevenueManager`). Luồng giống hệt (requestUMP → initMobileAds → `consentFinished`/`initFinished`), chỉ khác tên/vị trí — ghi chú riêng ở từng mục.

**Mốc phiên bản SDK cần nhớ:** gỡ Adjust khỏi xtechads 2026-08-17 (`AppConfig.adjustKey` bị xoá hẳn); tách `xtechcore` (RC + prefs) 2026-09-15; RC bật lại `createdAtStart` 2026-09-28 (bản cũ RC lazy → app phải tự resolve/fetch); billing lazy + `isPurchasedCached` 2026-09-08. a016 còn ở xtechads 1.4.6 (vẫn có `adjustKey`).

**Key RC SDK khai mà không tự dùng** (đối chiếu source xTechSDK, 10/2026): `AdsSharedPref` khai `star_review_to_store`,
`interval_skip_inter`, `screen_skip_inter`, `is_show_native_fs_resume`, `show_continue_native_fs_countdown`,
`auto_continue_native_fs_durations`, nhưng ngoài `AdsSharedPref` không chỗ nào trong SDK đọc chúng. Đó chỉ là chỗ đọc chung:
hành vi (gate interval, ngưỡng sao → Store, native full resume…) do app tự làm. Key SDK tự dùng: `ads_config`
(`AdsConfigProvider`), `af_ad_revenue_threshold` (`AfImpressionThresholdTracker`), `af_ad_revenue_threshold_events`
(`AfRevenueThresholdTracker`).
Kiểm nhanh: grep tên getter trong `xTechSDK/xtechads/src/main`.

**Bẫy build/setup chung (đối chiếu 10/2026, xtechads 1.8.7, AGP 9):**
- **Release crash ngay lúc process start**, cả khi job/FCM đánh thức app ở nền; debug không thấy vì không chạy R8. Log: `androidx.startup.InitializationProvider` không tạo được `androidx.work.impl.WorkDatabase` (`InstantiationException`).
  - Gốc: xtechads → `play-services-ads` 25.4.0 → `work-runtime` 2.7.0 → `room-runtime` 2.2.5. Consumer rule của 2 bản cũ này giữ class (lớp con `RoomDatabase`, lớp con `InputMerger`) nhưng không giữ constructor rỗng; AGP 9 bật mặc định `android.r8.strictFullModeForKeepRules` nên R8 thôi ngầm giữ constructor. Thiếu constructor `InputMerger` thì mọi `OneTimeWorkRequest` lỗi "Could not create Input Merger" (gồm ping offline của GMA).
  - Cách các app đã sửa: khai `work-runtime` 2.11.2 để kéo Room 2.7.0 có rule mới (A47; A048 kèm rule `RoomDatabase`); app có Room tự khai Room ≥ 2.7 (A045 2.8.4, kèm rule `InputMerger` vì work-runtime vẫn 2.7.0); hoặc rule giữ constructor rỗng trong `app/proguard-rules.pro` — mọi lớp con `RoomDatabase` + `InputMerger` (A013), hẹp hơn chỉ `WorkDatabase_Impl` + `InputMerger` (A049). Không tắt `strictFullModeForKeepRules` cho cả app chỉ để cứu vài class.
  - QC: build release, cài, mở lạnh → `adb logcat -b crash` rỗng; `app/build/outputs/mapping/release/usage.txt` không còn `<init>()` của `WorkDatabase_Impl`.
- **Tên adunit quyết định test ad ở bản debug:** `useTestAdId` mặc định = app debuggable → SDK thay unit id bằng test id của Google, đoán loại theo tiền tố `name` của adunit trong `ads_config`: `inter` → interstitial; `open_` / `app_open` / `app_resume` → app open; `reward` → rewarded; `banner` → banner; còn lại → native. Unit inter / app-open đặt tên không theo tiền tố (vd `splash_high`, `resume`) → bản debug nạp test id native → luôn fail như no fill. Đặt `inter_splash*`, `open_resume*` (A47, A048, A049). A013 tắt chế độ này (`useTestAdId = false`, MO-7) nên không gặp.

## MO-5 — Billing (RevenueCat / xtechbilling)

- **Yêu cầu:** App có IAP phải có lớp billing chuẩn: kết nối Play Billing, lấy gói, mua/restore, acknowledge, biết trạng thái premium để tắt ads. App mới dùng `com.xtech.sdk:xtechbilling` (API kiểu RevenueCat trên Play Billing 9.1.0 — quyết định SDK 2026-09-08); app đang chạy RevenueCat thì giữ. App không IAP (A013, a037, a039, A045…) → N/A, ghi rõ; còn khai SDK billing mà không dùng thì dọn (ghi chú a018).
- **Nghiệm thu:**
  - Paywall hiện giá thật đúng tiền tệ; mua / huỷ / restore chạy; mua xong ads tắt ngay, không cần restart.
  - Billing không chặn splash và không được dựng khi process dậy nền (FCM, alarm, boot).
  - Có event `iap_*` (MO-18) và doanh thu IAP (MO-13).
- **SDK:** `xtechbilling` — `billingModule(BillingConfig(products, onInitDone, …))`, `BillingManager` (lazy: `purchaseWith`, `purchaseRestore`, `packages`, `isPurchased`, `canShowIAP`), `BillingManager.isPurchasedCached(context)` (đọc pref, không dựng BillingClient); `BaseAds.isPurchase` (open) quyết định `canShowAds`. Min: xtechbilling 1.0.1 (prefs chung, key `billing_is_purchased`).
- **Chuẩn A013:** Không có IAP (sheet a013 = 0). Ref thay thế: a044 `ads/AdsManager.kt` (`isPurchase` đọc `BillingManager.isPurchasedCached`), a044 `ui/screen/paywall/PaywallViewModel.kt` (luồng mua + `logPurchaseAnalytics`); a016 `ads/billing/BillingExt.kt` (`billingConfig` → `SdkInitTracker` `BILLING_FINISH`). RevenueCat: a27 `payment/PaymentManager.kt`, A014 `ad_module/payment/BillingManager.kt`.
- **Remote config:** không có key chuẩn; key app tự thêm khi cần, ví dụ `show_iap_after_splash` (Boolean, true — a016), `iap_first_open_enabled` (Boolean, true — A014).
- **Cách làm:**
  1. Play Console: tạo product/base plan, thêm license tester (Bước 0 của `xTechSDK/docs/BILLING_NEW_APP_GUIDE.md`); xin SDK team whitelist applicationId cho xtechbilling (LicenseGuard riêng).
  2. Gradle `com.xtech.sdk:xtechbilling` (cùng repo maven SDK); nạp `billingModule(...)` trong `startKoin` — **không** `createdAtStart`.
  3. `AdsManager` override `isPurchase` bằng `BillingManager.isPurchasedCached(application)`; **không** inject `BillingManager` vào constructor `AdsManager`.
  4. Chỉ màn cần dữ liệu sống (paywall, badge Pro, splash để kick init song song — DEV-3) mới `koinInject<BillingManager>()`.
  5. Tracking theo MO-18, doanh thu theo MO-13. Đọc a044 `PaywallViewModel` để lấy chi tiết luồng mua.
  - RevenueCat (app cũ): `Purchases.configure` trên IO, không gate splash; nếu MO dùng tích hợp server-side thì set attribution id (`setAdjustID`/AppsFlyer id) + `collectDeviceIdentifiers`.
  - App không xtechads (A028/a036): `ads/payment/PaymentManager.kt` lazy trong module `appNotStart`.
- **Bẫy:** Inject `BillingManager` vào `AdsManager` eager → billing init mỗi lần process sống dậy (report a014 trong `xTechSDK/docs/CHANGELOG.md` 2026-09-08: `billing_finish` gấp ~22 lần số lần mở app). Quên override `isPurchase` → mua xong vẫn thấy ads. Không acknowledge → Play refund sau 3 ngày (xtechbilling tự ack). Splash chờ billing: A011 từng thêm rồi gỡ (CHANGELOG, commit `f5b6b598`).
- **QC:** license tester, build release: mở paywall thấy giá; mua weekly → ads tắt ngay; kill app mở lại vẫn premium; sub test hết hạn → ads hiện lại; đóng sheet Google → `iap_cancel_x`; restore trên máy chưa mua → `iap_restore_fail_x` (bảng 12 bước ở Bước 8 của `BILLING_NEW_APP_GUIDE.md`).

## MO-6 — Đúng package name

- **Yêu cầu:** `applicationId` (không phải `namespace`) phải trùng package của app trên Play Console / group dự án; các cấu hình ngoài khớp theo: `google-services.json`, app Facebook, app AppsFlyer, whitelist LicenseGuard của xtechads/xtechbilling.
- **Nghiệm thu:** `defaultConfig.applicationId` = package trong group dự án; `app/google-services.json` có client mang đúng package; app qua được màn UMP không crash `Unauthorize`.
- **Chuẩn A013:** `app/build.gradle.kts` `defaultConfig.applicationId` (khác `namespace` `com.example.a013_recovery` — bình thường).
- **Cách làm:** đối chiếu với Play listing và group dự án; đổi applicationId thì phải xin SDK team whitelist lại (LicenseGuard verify ngay trong `BaseAds.init`).
  - Đọc `app/build.gradle.kts` (`defaultConfig`) ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** debug có `applicationIdSuffix` → kiểm LicenseGuard có chấp nhận id debug không; whitelist "đã thêm" chỉ tin khi chạy app thật qua được UMP.
- **QC:** cài bản release, mở app qua được UMP; `adb shell pm list packages` thấy đúng package.

## MO-7 — AdMob App ID khai trong Manifest

- **Yêu cầu:** `<application>` có meta-data `com.google.android.gms.ads.APPLICATION_ID` = App ID thật của app trên AdMob, cùng publisher với ad unit trong `ads_config`.
- **Nghiệm thu:** meta-data tồn tại; bản release không dùng App ID mẫu/test công khai của Google (loại ID trong tài liệu AdMob); phần publisher của App ID (`ca-app-pub-<pub>~…`) trùng publisher của mọi ad unit trong `app/config/ads_config.json` và RC `ads_config`.
- **Chuẩn A013:** `app/src/main/AndroidManifest.xml` meta-data `com.google.android.gms.ads.APPLICATION_ID` (giá trị literal) + flag `com.google.android.gms.ads.flag.OPTIMIZE_INITIALIZATION` / `OPTIMIZE_AD_LOADING` = true, `NATIVE_AD_DEBUGGER_ENABLED` = false. Biến thể: base project trỏ `@string/admob_app_id` (`res/values/sdk_ids.xml`); a016 dùng placeholder `${ADMOB_APP_ID}`, Langofy `${admob_app_id}`.
- **Cách làm:** khai meta-data (nên qua string resource để thay 1 chỗ), App ID do MO cấp; giữ các flag optimize như A013.
  - Đọc `app/src/main/AndroidManifest.xml` ở A013 (bản hiện tại) để lấy chi tiết (App ID thay bằng ID của app).
- **Bẫy:** thiếu meta-data → GMA crash lúc init; App ID của app khác → no fill. A013 override `useTestAdId = false` → bản debug cũng chạy unit thật: chỉ test/click trên máy có hash trong `AppConfig.listDeviceTest`. Thay App ID mẫu của Google bằng App ID thật mà AdMob chưa publish GDPR message cho app → UMP lỗi `Publisher misconfiguration … no form(s) configured for the input app ID`; SDK vẫn `initMobileAds` (nhánh lỗi của `requestUMP`) nên ad vẫn tải nhưng user EEA không thấy form consent. App ID mẫu có form sẵn nên lỗi chỉ lộ sau khi thay (A049 15/10) — báo MO tạo message ở AdMob → Privacy & messaging, không sửa code.
- **QC:** logcat không có lỗi thiếu application ID; mở 1 placement thấy ad (test ad trên máy test); sau khi thay App ID thật, logcat không có `requestUMP: requestConsentError` (debug đang giả lập EEA nên lỗi hiện cả ngoài EEA). Có lỗi "no form(s) configured" thì nhờ MO publish message GDPR trên AdMob (Privacy & messaging → European regulations); publish xong form hiện lại mà không cần build lại (A049 16/10: 17:37 còn lỗi, 17:48 đã `requestUMP: loadConsentForm` → `finish`).

## MO-8 — UMP hiện được ở bản debug

- **Yêu cầu:** Bản debug ép được form UMP (giả lập EEA) trên máy test để QC kiểm consent; bản release không gửi debug settings.
- **Nghiệm thu:** debug + máy có hash trong `AppConfig.listDeviceTest` (hoặc emulator) → form consent hiện ở lần mở đầu sau clear data; release không bật debug geography.
- **SDK:** `BaseAds.requestUMP(activity, enableDebug, resetData)` — `enableDebug` dựng `ConsentDebugSettings` với `DEBUG_GEOGRAPHY_EEA` + `addTestDeviceHashedId` cho mọi id trong `AppConfig.listDeviceTest`; `resetData` gọi `consentInformation.reset()`.
- **Chuẩn A013:** `MainActivity.kt` `onCreate` gọi `requestUMP` với `enableDebug = BuildConfig.DEBUG`, `resetData = false`; hash máy test ở `di/Modules.kt` `adsModule` → `AppConfig.listDeviceTest` (hash là của máy team A013 — app khác phải tự lấy, không chép).
- **Cách làm:** truyền `enableDebug = BuildConfig.DEBUG`; lấy hash máy QC từ logcat UMP lần chạy đầu (dòng gợi ý `addTestDeviceHashedId`) thêm vào `listDeviceTest`; muốn form hiện lại trên máy đã consent: clear data, hoặc tạm `resetData = true` ở debug.
  - Đọc `MainActivity.kt` (`onCreate`) và `di/Modules.kt` (`adsModule`) ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** hardcode `enableDebug = false` (A028 `main/MainActivity.kt`) → QC ngoài EEA không bao giờ thấy form; hardcode `true` (ảnh mẫu `assets/refs/MO-8-1.jpg`; a044 `MainActivity` đang vậy) → bản release vẫn gửi debug settings — đừng làm theo ảnh. a033, a036, a041, A045 chưa khai `listDeviceTest` → chỉ test được form trên emulator. Form chỉ hiện khi AdMob đã publish GDPR message cho app (Privacy & messaging) — không hiện thì kiểm AdMob trước khi sửa code.
- **Bẫy tên app trong form:** dòng "<tên> asks for your consent…" lấy tên app khai trên AdMob (Privacy & messaging),
  không lấy `app_name`. Đổi tên app thì MO sửa trên AdMob (A049 16/10: `app_name` đã là Hastgy, form vẫn "Palm AI").
- **QC:** cài debug trên máy test, clear data, mở app → form "… asks for your consent" (ảnh `assets/refs/MO-22-1.jpg`); chọn Consent → app chạy tiếp; logcat `requestUMP: loadConsentForm` → `requestUMP: finish`.

## MO-9 — UMP chạy trước khi load bất kỳ ad nào

- **Yêu cầu:** Không có ad request nào (splash, native, app-open, preload) trước khi luồng consent kết thúc; form (nếu cần) hiện trước mọi ad.
- **Nghiệm thu:** logcat theo thứ tự `requestUMP:` → (`requestUMP: finish` / `not required` / lỗi) → `initMobileAds:` → mới có `loadAd:`; trên DebugView không có `iaa_request` nào trước `tracking_consent`.
- **SDK:** `AdUnit.canLoadAd` (`canShowAds` và có mạng), `consentFinished` (StateFlow, chỉ true sau UMP), `AdGroupUnit.loadAd` gọi sớm → `FAIL` ngay chỉ khi offline hoặc UMP đã biết cần consent; lúc UMP chưa trả trạng thái thì request vẫn đi (Tổng quan mục 4).
- **Chuẩn A013:** `ui/screen/splash/SplashScreen.kt` — khối `combine` theo `consentFinished` + `isConnected` mới gọi `AdsManager.loadSplashAds`; native `bottom_splash` chỉ render khi `SplashContent` nhận `isConsent = true`.
- **Cách làm:** mọi load/preload trong FO đặt sau `consentFinished`; app-open resume đã bị chặn trên Splash (`AdsManager.screenSkipAdResume` + `disableAdResumeOnTime`). App không SDK: gate theo `consentFinished` của `BaseAds` app.
  - Đọc `ui/screen/splash/SplashScreen.kt` (khối `combine` theo `consentFinished` + `isConnected`) ở A013 (bản hiện tại); phần chờ mạng trước `requestUMP` đọc a045 `MainActivity.initConsent`.
- **Bẫy:**
  - Gọi `requestUMP` khi offline: request lỗi → SDK vẫn init ads, `umpAllowed` = true vì `privacyOptionsRequirementStatus` chưa biết → có mạng lại là load ad mà user EEA mới chưa từng thấy form. Chuẩn đề xuất: chờ `isConnected` rồi mới `requestUMP` (A045 `MainActivity.initConsent`, a033 `first_open/ui/splash/SplashScreen.kt`, base project). **A013 gọi ngay trong `onCreate` — lệch.**
  - Preload ad ở `Application`/trước consent → hoặc `FAIL` ngay (bị hiểu nhầm là no-fill, splash đi tiếp sớm), hoặc — lúc UMP chưa trả trạng thái — request thật đi trước form.
  - User từ chối: `canRequestAds()` vẫn true (đã có quyết định) → ad vẫn request (limited/no fill) — xử lý ở MO-23.
- **QC:** debug EEA, clear data: khi form còn hiện không có dòng `loadAd:` nào; bật máy bay → mở app → tắt máy bay: form phải hiện trước ad (khi đã áp chờ mạng).

## MO-10 — initMobileAds chỉ chạy sau khi UMP xong

- **Yêu cầu:** `MobileAds.initialize` chỉ chạy sau khi UMP kết thúc, đúng 1 lần.
- **Nghiệm thu:** app không tự gọi `MobileAds.initialize` (ở `Application`, `init` của BaseAds…); logcat `initMobileAds:` đứng sau dòng kết thúc UMP, tiếp theo là log adapter.
- **SDK:** `BaseAds.initMobileAds()` (private) — chỉ gọi từ `doneConsent()` trong `requestUMP` (mọi nhánh) hoặc `ensureAdsInitialized()` (khi `umpAllowed`); guard `AtomicBoolean`; chạy trên IO; set `RequestConfiguration.testDeviceIds` trước.
- **Chuẩn A013:** không có lời gọi `MobileAds.initialize` trong app; chỉ `requestUMP` ở `MainActivity.onCreate`.
- **Cách làm:** xoá mọi `MobileAds.initialize` tự gọi; cần init khi app đang chết mà phải preload (vd lúc bắn noti) thì gọi `ensureAdsInitialized()` (A045 `AdsManager.preloadInterSplashOnNoti`). App không SDK: `initMobileAds` của `ads/base/BaseAds.kt` chỉ gọi trong callback UMP (A028).
  - Đọc `MainActivity.kt` (`onCreate`) ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** `ensureAdsInitialized()` chạy trong process mới (vd preload lúc bắn noti) mà UMP chưa trả trạng thái (user EEA chưa consent bao giờ): `umpAllowed` = true nên SDK init ads, bật `consentFinished` và request đi trước form consent. Chỉ gọi khi user đã có consent từ phiên trước (`canRequestAds()`), hoặc chờ `requestUMP` (MO-22, MO-9).
- **Bẫy:** a032 (sheet) init trong `init` của BaseAds. A028/a036 `requestUMP` bỏ hẳn `requestConsentInfoUpdate` khi `canRequestAds()` → consent hết hạn/đổi vendor list không bao giờ hỏi lại (SDK luôn gọi update, chỉ init sớm song song).
- **QC:** logcat như ảnh `assets/refs/MO-10-1.jpg`: `requestUMP:` → `requestUMP: loadAndShowConsentFormIfRequired`/`finish` → `initMobileAds:` → `Adapter name: …`.

## MO-11 — Facebook App ID / Client Token trong Manifest

- **Yêu cầu:** Manifest có `com.facebook.sdk.ApplicationId` và `com.facebook.sdk.ClientToken` đúng app Facebook của sản phẩm (MO cấp).
- **Nghiệm thu:** 2 meta-data có trong merged manifest bản release, giá trị khớp Meta for Developers, không rỗng.
- **Chuẩn A013:** `app/src/main/AndroidManifest.xml` meta-data `com.facebook.sdk.ApplicationId`, `com.facebook.sdk.ClientToken` (literal) + `AutoInitEnabled` / `AutoLogAppEventsEnabled` / `AdvertiserIDCollectionEnabled` = true.
- **Cách làm:** đặt giá trị ở `res/values/sdk_ids.xml` (`facebook_application_id`, `facebook_client_token`) và trỏ meta-data `@string/...` (base project). Đặt tên đúng `facebook_application_id` sẽ đè string rỗng cùng tên của xtechads → meta-data `com.appsflyer.FacebookApplicationId` (khai sẵn trong manifest AAR) có giá trị → AppsFlyer thu Meta Install Referrer; chỉ cần khi app chạy UA trên Meta (`xTechSDK/docs/APPSFLYER_V7_MIGRATION.md`).
  - Đọc `app/src/main/AndroidManifest.xml` ở A013 (bản hiện tại) và `res/values/sdk_ids.xml` + manifest template của base project để lấy chi tiết.
- **Bẫy:** A013 khai literal nên `facebook_application_id` của SDK vẫn rỗng → AppsFlyer không thu Meta Install Referrer (cần MO/UA xác nhận có cần). `AutoInitEnabled=true` (mọi app hiện tại) → Facebook init cả khi process dậy nền, rủi ro ANR — xem MO-97.
- **QC:** APK Analyzer xem merged manifest đủ 2 meta-data; Meta Events Manager nhận event kích hoạt app từ build test.

## MO-12 — Facebook SDK + mediation Meta

- **Yêu cầu:** Có Facebook SDK (App Events) và adapter mediation Meta Audience Network cho AdMob.
- **Nghiệm thu:** runtime classpath có `com.facebook.android:facebook-android-sdk` (hoặc `facebook-core`) và `com.google.ads.mediation:facebook`; log init AdMob có adapter Facebook.
- **SDK:** xtechads kéo sẵn transitive (1.8.2: facebook-android-sdk 18.3.0, mediation facebook 6.21.0.4) — app không cần khai trừ khi nâng version.
- **Chuẩn A013:** `gradle/libs.versions.toml` alias `facebook` = `com.google.ads.mediation:facebook` (bản cao hơn transitive) + `app/build.gradle.kts` khai `libs.facebook` trong dependencies.
- **Cách làm:** giữ transitive; nâng version thì khai cùng group như A013. Việc thêm Meta vào mediation group trên AdMob là của MO. App không SDK: khai trực tiếp (A028/a036).
  - Đọc `gradle/libs.versions.toml` (alias `facebook`) + `app/build.gradle.kts` ở A013 (bản hiện tại).
- **Bẫy:** khai Facebook SDK thấp hơn transitive gây lệch class; adapter có nhưng mediation group chưa có Meta → không bao giờ có fill Meta.
- **QC:** logcat sau `initMobileAds:` có `Adapter name: com.google.ads.mediation.facebook.FacebookMediationAdapter`.

## MO-13 — Facebook: track doanh thu ad / IAP

- **Yêu cầu:** Mỗi impression có doanh thu gửi Facebook (`AdImpression` kèm value + currency); mỗi giao dịch IAP mới gửi purchase đúng số tiền.
- **Nghiệm thu:** Events Manager (build release) có `AdImpression` với value > 0; IAP: `logPurchase` đúng **đơn vị tiền** (không phải micros), 1 lần cho mỗi giao dịch mới.
- **SDK:** ad revenue có sẵn — `RevenueManager.logAdRevenue` log `EVENT_NAME_AD_IMPRESSION` qua `AppEventsLogger` với valueToSum = valueMicros / 1.000.000 và currency. IAP: không có, app tự log.
- **Chuẩn A013:** ad: nhờ SDK, không có code app. IAP: N/A (A013 không IAP). Ref IAP đúng đơn vị: a044 `ui/screen/paywall/PaywallViewModel.kt` `logPurchaseAnalytics` (chia micros trước khi log, bỏ qua debug).
- **Cách làm:** ngay khi mua thành công một purchase mới (chưa acknowledge trước đó), gọi `AppEventsLogger.logPurchase` với giá đã chia 1.000.000 + `Currency` + param content type; chỉ ở release. Đọc a044 `PaywallViewModel.logPurchaseAnalytics`. App không SDK: nhánh Facebook nằm trong `AdjustManager.logAdRevenue` (A028/a036).
- **Bẫy:**
  - **BUG đang có** ở A014 `ad_module/payment/BillingManager.kt`, A028/a036 `ads/payment/PaymentManager.kt` (`logFacebookAnalytics`), a27 `payment/PaymentManager.kt`, a016 `ads/billing/BillingExt.kt` (`logPurchaseAnalytics`): truyền `amountMicros`/`priceMicros` thẳng vào `logPurchase` → doanh thu Facebook phóng đại 1.000.000 lần.
  - Meta dashboard bật tự log in-app purchase + `AutoLogAppEventsEnabled` + log tay → trùng purchase — cần MO kiểm setting.
  - Restore / `ITEM_ALREADY_OWNED` không phải doanh thu mới (a016 bỏ qua purchase đã acknowledge).
- **QC:** Events Manager → Test events: xem 1 ad → `AdImpression` có value; mua gói test (license tester) → purchase có value = giá gói.

## MO-14 — Adjust: track ad revenue

- **Yêu cầu:** Gốc: gửi ad revenue sang Adjust. Hiện trạng: xtechads gỡ hẳn Adjust từ 2026-08-17 (owner xác nhận không chạy data Adjust, AppsFlyer thay thế). **Cần MO xác nhận còn dùng Adjust không** — nếu không, mục này hiểu là "AppsFlyer nhận ad revenue" (SDK tự làm).
- **Nghiệm thu:** (mặc định AppsFlyer) `AppConfig.appsflyerKey` khác rỗng; AppsFlyer có ad revenue kèm ad unit / ad type / placement. (Nếu MO giữ Adjust) Adjust dashboard có ad revenue nguồn `admob_sdk`.
- **SDK:** `RevenueManager` → `AppsflyerManager.logAdRevenueAppsflyer` (`AFAdRevenueData`, `MediationNetwork.GOOGLE_ADMOB`, `AdRevenueScheme.AD_UNIT/AD_TYPE/PLACEMENT`). Adjust: không còn (bản trước 2026-08-17, vd a016 @1.4.6, vẫn forward khi có `AppConfig.adjustKey`).
- **Chuẩn A013:** không Adjust; AppsFlyer qua `di/Modules.kt` `AppConfig.appsflyerKey`. Ref Adjust (app không SDK): A028/a036 `ads/adjust/AdjustManager.kt` `logAdRevenue` (tạo `AdjustAdRevenue` nguồn `admob_sdk`, set revenue + network mediation rồi `Adjust.trackAdRevenue`), gọi từ `OnPaidEventListener` của từng ad unit app.
- **Cách làm:** app SDK muốn giữ Adjust: tự khai `com.adjust.sdk:adjust-android` + tự `Adjust.initSdk` (foreground) — nhưng xtechads không public hook paid-event nên **không forward được ad revenue sang Adjust nếu SDK không sửa** → báo SDK team. App không SDK: giữ `AdjustManager`.
  - Đọc `di/Modules.kt` (`AppConfig`) ở A013 (bản hiện tại); nhánh Adjust đọc a028 `ads/adjust/AdjustManager.kt` (`logAdRevenue`).
- **Bẫy:** nâng xtechads qua mốc 2026-08-17 khi còn truyền `adjustKey` → fail compile; app lấy `com.adjust.sdk` transitive qua SDK sẽ mất class. Dev key AppsFlyer là key cấp tài khoản: A013, A014, A045, A047, A048, A054, a037, a039, a044 dùng chung một key → app mới lấy theo app ref (không chép key vào skill). Key rỗng thì SDK không tạo `AppsflyerManager`, không lỗi gì. App chưa được thêm vào tài khoản AppsFlyer → `start` trả `onError: 50 - Status code failure 404`, `sdk_init` `appsflyer` = FAILED, AppsFlyer không nhận gì (A049 15/10) — báo MO/UA thêm app, không sửa code.
- **QC:** mở app, logcat `sdk_init` có `sdk_key=appsflyer` `status=SUCCESS` (FAILED kèm `Status code failure 404` = app chưa có trên AppsFlyer); build release xem 1 ad → AppsFlyer live events có ad revenue; (Adjust) Adjust testing console có ad_revenue.

## MO-15 — Adjust: track IAP revenue (nếu có)

- **Yêu cầu:** Doanh thu IAP về Adjust — **cần MO xác nhận còn dùng Adjust** (như MO-14).
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:** N/A (không IAP, không Adjust). Ref: A028/a036 `ads/payment/PaymentManager.kt` `configurePurchasesSDK` và callback attribution trong `AdjustManager`: `Purchases.collectDeviceIdentifiers()` + `Purchases.setAdjustID(adid)` → RevenueCat gửi event subscription sang Adjust **server-side** (phải bật integration Adjust trên RevenueCat dashboard). Không có event IAP Adjust phía client.
- **Cách làm:** RevenueCat → set Adjust ID như trên + MO bật integration; xtechbilling/Play Billing thuần → phải tự gửi `AdjustEvent` có revenue hoặc `Adjust.trackPlayStoreSubscription` (chưa app nào làm, token event do MO cấp). Nếu bỏ Adjust: chưa app nào gửi IAP revenue sang AppsFlyer (không thấy set AppsFlyer id cho RevenueCat hay event purchase AF) → báo MO/UA chốt kênh.
  - A013 không có — đọc a028 `ads/payment/PaymentManager.kt` (`configurePurchasesSDK`) + `ads/adjust/AdjustManager.kt` để lấy chi tiết.
- **Bẫy:** tưởng `setAdjustID` là đủ — thiếu cấu hình dashboard RevenueCat thì Adjust không nhận gì.
- **QC:** mua gói test → integration log của RevenueCat / Adjust dashboard có event.

## MO-16 — Firebase: Crashlytics, Remote Config, FCM

- **Yêu cầu:** Firebase nối đủ 3 phần: Crashlytics (crash release), Remote Config (RC của SDK), FCM (nhận push + token cho AppsFlyer uninstall).
- **Nghiệm thu:** `app/google-services.json` đúng project/package; plugin `com.google.gms.google-services` + `com.google.firebase.crashlytics` áp ở module app; manifest có service `FirebaseMessagingService` với action `com.google.firebase.MESSAGING_EVENT`; log `fetchRemoteConfig: success`.
- **SDK:** xtechads kéo sẵn firebase analytics/config/crashlytics/messaging/perf (BoM 34.7.0 ở 1.8.2); `RemoteConfigManager` (xtechcore); service có sẵn `com.example.xtechads.ads.firebase.messages.FirebaseFCM` (app chỉ cần khai trong manifest nếu không tự viết).
- **Chuẩn A013:** `app/build.gradle.kts` plugin `googleServices`, `firebaseCrashlitycs`, `firebase.perf`; `App.kt` `initFCM` (sau `consentFinished`: Crashlytics + Analytics collection chỉ bật ở release, lấy FCM token → `AppsFlyerLib.updateServerUninstallToken`); `ads/firebase/FirebaseFCM.kt` `onNewToken` (AppsFlyer uninstall token + event `fcm_token` chia chunk 90 ký tự); manifest service `.ads.firebase.FirebaseFCM` + meta `com.google.firebase.messaging.default_notification_icon/color`.
- **Cách làm:** thêm `google-services.json` + 2 plugin; khai service FCM (của SDK hoặc tự viết như A013); tắt Crashlytics ở debug. Nội dung push/FCM xem MO-75 (nhóm noti).
  - Đọc `App.kt` (`initFCM`), `ads/firebase/FirebaseFCM.kt`, `app/build.gradle.kts` ở A013 (bản hiện tại) — riêng phần set consent làm theo MO-22.
- **Bẫy:** A013 `initFCM` set consent Analytics GRANTED cho mọi user — **bug**, xem MO-22. `FirebaseAnalyticsUtil.logEventAdsImpression` (`app_ad_impression`) ở A013 là code chết; revenue Firebase thật đi qua SDK `in_app_ad_impression`. Thiếu plugin Crashlytics → không upload mapping, stacktrace release bị obfuscate. Tắt plugin `com.google.gms.google-services` lúc chưa có file Firebase thật → crash `Default FirebaseApp is not initialized` ngay màn đầu (SDK `logScreenShow` gọi `Firebase.analytics` không bọc); giữ plugin với `google-services.json` placeholder đúng package tới khi MO cấp file thật (A049).
- **QC:** build release → crash thử hiện trên Crashlytics; Firebase console gửi test message tới token (log `fcm_token`); đổi 1 key RC → lần mở sau thấy giá trị mới.

## MO-17 — Remote Config có hiệu lực trước khi load ad

- **Yêu cầu:** Giá trị RC (nhất là `ads_config` và các key bật/tắt/timeout/next screen) phải được áp trước request ad mà nó điều khiển; QC đổi RC phải thấy app đổi hành vi.
- **Nghiệm thu:** user cũ: RC của lần fetch trước áp ngay từ ad đầu tiên (cache-first); FO: theo cổng chờ đã chốt ở MO-27 (chuẩn đề xuất: chờ RC có trần) hoặc `ads_config.json` đóng gói đồng bộ với RC (biến thể A013, cần MO chấp nhận); đổi `isEnable`/`timeout` trên RC → app đổi theo.
- **SDK:** `RemoteConfigManager` (xtechcore): fetch trên IO ngay khi được dựng; cache-first (đã fetch thành công ở phiên trước → `fetchedStateFlow` = true ngay); ghi mọi key REMOTE vào prefs; fetch timeout `AppConfig.timeoutRc` (5s), `maxRetryRc` (5), `retryDelayRc` (100ms), `minimumFetchIntervalRc` (3600s); hết lượt retry vẫn set fetched = true. `AdsConfigProvider` đọc prefs `ads_config` mỗi lần dùng, raw đổi thì parse lại → RC về giữa phiên áp cho các lần load sau.
- **Chuẩn A013:** `App.kt` `onCreate` gọi `remoteConfig.fetchRemoteConfig()`; key RC khai ở `domain/preference/SharedPrefs.kt`. Splash **không chờ RC** từ v1.2.6 (commit `ba0a17b`; trước đó chờ `mobileAdsFinish` + `fetchedStateFlow` + `isConnected`).
- **Remote config:** `ads_config` (String JSON, mặc định = `app/config/ads_config.json` đóng gói); tham số fetch qua `AppConfig` (`timeoutRc`, `maxRetryRc`, `retryDelayRc`, `minimumFetchIntervalRc`).
- **Cách làm:**
  1. RC phải được dựng/fetch ngay lúc mở app: source SDK đã eager; SDK cũ (RC lazy) thì gọi `fetchRemoteConfig()` sớm như A013 `App.onCreate`.
  2. Key app đọc qua property `SharedPreferenceProperty` trong `SharedPrefs`, đọc lại mỗi lần dùng (không cache vào `val` khởi tạo một lần).
  3. Cổng chờ ở splash: theo MO-27.
  4. Mỗi lần release: copy RC `ads_config` đang chạy vào `app/config/ads_config.json` (FO lần đầu dùng bản này).
  - Đọc `App.kt` (`onCreate`) và `domain/preference/SharedPrefs.kt` ở A013 (bản hiện tại) để lấy chi tiết.
- **Bẫy:** xoá key trên RC console **không** tắt feature (SDK chỉ ghi khi source REMOTE, máy giữ giá trị cũ) → muốn tắt phải set giá trị tắt (`false`, `[]`). `minimumFetchIntervalRc` 3600s → QC đổi RC không thấy ngay; debug nên set 0. SDK cũ RC lazy mà không ai resolve → RC không bao giờ áp (qibla `SDK_POST_INTEGRATION_CHECKLIST.md`).
- **QC:** RC `ads_config` đặt placement `splash` `isEnable: false` → user cũ mở lại app không có inter splash; FO (clear data) kiểm theo biến thể đã chốt ở MO-27.

## MO-18 — Firebase: event IAA / IAP in-house

- **Yêu cầu:** Đủ funnel event in-house: IAA `iaa_request`, `iaa_loaded`, `iaa_fail_load`, `iaa_impression`, `iaa_fail_show`, `iaa_click`, `iaa_complete`; IAP `iap_show_x`, `iap_click_x`, `iap_close_x`, `iap_purchase_x`, `iap_purchase_fail_x`, `iap_cancel_x`, `iap_restore_x`, `iap_restore_fail_x`; mọi event có `session_number`.
- **Nghiệm thu:** DebugView thấy đủ `iaa_*` khi load/show 1 ad; IAP đủ 8 event với tham số `iap_placement`, `paywall`, `paywall_version`, `trigger_type`, `pack_name`, `price`, `currency`, `pack_duration`, `is_trial`, `trial_duration`; `session_number` > 0.
- **SDK:** IAA tự bắn trong `AdUnit` (enum `EventType`); `ad_placement` lấy từ `screen` của `AdGroupUnit.of(placement, screen = …)`, không có thì `TrackingState.lastScreen`; revenue Firebase `in_app_ad_impression`. IAP: không có — mẫu tham số ở `xTechSDK/xtechads/docs/TRACKING_EVENTS_STATUS.md` mục C.
- **Chuẩn A013:** IAA nhờ SDK; `MainActivity.onCreate` tăng `prefs.sessionNumber` (chỉ khi mở mới) và gán `TrackingState.sessionNumber`; helper IAP `utils/Tracking.kt` `trackingIapDataBucketEvent` có sẵn nhưng chưa dùng (không IAP). Ref IAP: a016 `ads/adunit/common/Tracking.kt` `trackingIAPDataInHouseEvent` + `ui/screen/iap/WeeklyTrialScreen.kt`; a27 `ui/screen/payment/SubscriptionScreen.kt`.
- **Cách làm:** session number ở Activity LAUNCHER; IAP: 1 hàm tracking dùng `TrackingEvent.logEvent` + `bundleOfNotNull`, gọi đúng 8 điểm (hiện paywall, bấm gói, đóng, mua OK, lỗi, huỷ, restore OK/fail) + Firebase `purchase` (value/currency/transaction_id) khi mua mới.
  - Đọc `MainActivity.kt` (`onCreate`, phần `sessionNumber`) ở A013 (bản hiện tại); phần IAP đọc a016 `ads/adunit/common/Tracking.kt` + `ui/screen/iap/WeeklyTrialScreen.kt`.
- **Bẫy:** sheet: chưa app nào đạt (mọi app = 0) → cần MO chốt danh sách event/param trước khi audit. Tên lệch giữa app: SDK `in_app_ad_impression` vs `app_ad_impression` (a036, a034 util cũ, a041); a016 bắn thêm `inapp_purchase_custom` ngoài `purchase`. `sessionNumber` tăng ở mọi `onCreate` (A048 `MainActivity`) → Activity dựng lại (đổi dark mode, ngôn ngữ) cũng thành phiên mới; chỉ tăng khi `savedInstanceState == null` (A013, A47, A049). Event bắn trong process dậy nền (alarm, overlay lock screen) mang `session_number` 0 vì `TrackingState.sessionNumber` mặc định 0 và chỉ được gán ở `MainActivity.onCreate` → gán lại từ prefs ở điểm vào nền (A049 `LockScreenActivity`, `NotificationManager`).
- **QC:** `adb shell setprop debug.firebase.analytics.app <package>` → DebugView: mở 1 placement (đủ `iaa_*`), mở paywall → mua/huỷ (đủ `iap_*`).

## MO-19 — MultiDex

- **Yêu cầu:** App không dính giới hạn 64K method.
- **Nghiệm thu:** `minSdk` ≥ 21 → đạt mặc định (ART hỗ trợ multidex, không cần `MultiDexApplication` / `multiDexEnabled`); `minSdk` < 21 → `multiDexEnabled true` + `MultiDexApplication` hoặc `MultiDex.install`.
- **Chuẩn A013:** `app/build.gradle.kts` `minSdk = 30` + `multiDexEnabled = true` (thừa, vô hại); `App` kế thừa `Application` — sheet chấm a013 = 0 chỉ vì không extend `MultiDexApplication`.
- **Bẫy:** cần MO chốt ý nghĩa mục: mọi app hiện có minSdk 24–30 nên luôn đạt; A028/a036/qibla vẫn extend `MultiDexApplication` + `MultiDex.install` (không cần).
- **QC:** build release cài máy API thấp nhất app hỗ trợ, mở app không crash `ClassNotFoundException`.

## MO-20 — Đổi layout native/banner qua RC (kể cả native Meta)

- **Yêu cầu:** Mọi vị trí native/banner đổi được layout/kiểu bằng RC không cần release; native fill từ Meta dùng layout riêng nếu MO khai.
- **Nghiệm thu:** mọi native/banner render qua `NativeBannerGroupView(placement = …)`; đổi `layout` của adunit (hoặc placement) trong RC `ads_config` → layout đổi; khai `layoutMeta` → fill Meta dùng layout đó; banner đổi `bannerType`; đổi màu/bo góc qua `configs.themes`.
- **SDK:** `AdUnitConfig.layout` / `layoutMeta` (key theo enum `AdLayout`; key sai → fallback im lặng `native_med_16_9_a` hoặc `defaultNativeLayout`), `PlacementConfig.layout` / `layoutMeta` / `theme` (override theo placement — có trong model 1.8.2), `configs.themes`, `bannerType`; nhận diện Meta bằng `mediationAdapterClassName` chứa `facebook` (`NativeBannerGroupViewImpl`, composable `NativeGroupContent`).
- **Chuẩn A013:** mọi slot dùng `NativeBannerGroupView` (vd `ui/screen/splash/view/SplashContent.kt` placement `bottom_splash`; `SplashNativeFullContent` placement `native_full_splash` có `defaultNativeLayout` làm fallback); `app/config/ads_config.json` khai `layout` cho native, `layoutMeta` cho nameSpace full-screen (`resume`, `fs_onboard`), theme `native_full_t2c`.
- **Cách làm:** không hardcode layout ở call site (chỉ truyền `defaultNativeLayout` làm fallback); thêm vị trí = thêm placement/nameSpace trong config; layout Meta = thêm `layoutMeta` cho adunit cần. App không SDK (A028/a036): config `layoutKey` / `layoutKeyMeta` / `typeMeta`, `NativeView` chọn layout Meta theo adapter.
  - Đọc `ui/screen/splash/view/SplashContent.kt`, `SplashNativeFullContent.kt` và `app/config/ads_config.json` ở A013 (bản hiện tại).
- **Bẫy:** `layoutMeta` rỗng → fill Meta dùng chung `layout` (đa số nameSpace A013) — MO quyết có cần layout Meta riêng. Key layout cũ (`native_media_ctr_bot_*`) → fallback im lặng. Banner không có đường load nếu nameSpace tắt cả `reloadWhenResume` lẫn `autoReloadOnImpression` (qibla checklist).
- **QC:** RC đổi `layout` của 1 nameSpace (vd `language`) → mở lại app thấy layout mới; khi có fill Meta (`ad_source` trong `iaa_impression`) với `layoutMeta` khác → layout khác.

## MO-100 — Init SDK (theo SDK Integration Guide)

- **Yêu cầu:** Tích hợp xtechads đúng hướng dẫn chuẩn. Doc Lark của mục không đọc được → nguồn: `xTechSDK/docs_final/SDK_INTEGRATION_GUIDE.md` (checklist chốt cuối file).
- **Nghiệm thu:**
  - applicationId đã whitelist — chạy app thật qua được UMP, không crash `Unauthorize`.
  - Repo maven `xtech-android.github.io/maven` khai ở cả `pluginManagement` và `dependencyResolutionManagement`; AAR `com.xtech.sdk:xtechads` và plugin `com.xtech.ads` dùng chung 1 version ref.
  - `app/config/ads_config.json` (không có bản plaintext trong `src/**/assets`); build log `xtechAds: da ma hoa ads_config.json -> ads_config.dat`.
  - Koin: module SDK nạp trước; `SharedPrefs` bind `XtechSharedPref`; `AppConfig` (appsflyerKey thật, `listDeviceTest`); `AdsManager` `createdAtStart` bind `BaseAds`.
  - `MainActivity` implement `AdHostActivity`; `requestUMP` với `enableDebug = BuildConfig.DEBUG`; `sessionNumber` tăng 1 lần mỗi lần mở; `onPause` không track background khi `isShowingAds` / `disableAdResumeOneTime`.
  - Không tự init AppsFlyer / MobileAds / RC (SDK làm).
- **SDK:** `BaseAds`, `AppConfig`, `com.example.xtechads.di.adsModule` / `repositoryModule`, plugin `com.xtech.ads`, `AdHostActivity`.
- **Chuẩn A013:** `App.kt` (thứ tự module trong `startKoin`), `di/Modules.kt`, `MainActivity.kt`, `gradle/libs.versions.toml` (`xtechadsVersion` dùng cho cả lib và plugin), `app/build.gradle.kts`, `app/config/ads_config.json`.
- **Cách làm:** theo Bước 0–3 + Case A/B của guide; sau đó áp MO-97 (init ở foreground, Facebook AutoInit) và DEV-3.
  - Đọc `App.kt`, `di/Modules.kt`, `MainActivity.kt`, `gradle/libs.versions.toml`, `app/build.gradle.kts` ở A013 (bản hiện tại) để lấy chi tiết.
  - Ref A047/A048 khác A013: `AdsManager` không `createdAtStart` (A47, A048 `singleOf(::AdsManager)`; base project và A049 khai `single` có kiểm main thread) — lệch dòng Koin của nghiệm thu, xem MO-97.
- **Bẫy:** thiếu `AdHostActivity` → app-open resume không chạy; `AdsManager` không `createdAtStart` (a037 `singleOf(::AdsManager)`) → lifecycle callback gắn muộn; `SharedPrefs` cũ khác file prefs (`packageName`) → mất data user khi migrate; plugin và AAR lệch version (A034 từng 1.2.1 vs 1.3.4); không ai gọi `requestUMP` (vd tạm bỏ lúc dựng app rồi quên bật lại) → `consentFinished` không bao giờ bật: splash không load ad, không hỏi noti, đứng mãi (hoặc tới trần tổng nếu có) — dấu hiệu: logcat không có dòng `requestUMP:`. Build release crash lúc mở / test ad debug luôn fail: xem Tổng quan nhóm.
- **QC:** chạy release: UMP → inter splash → log `trackIaaRequest` / `trackIaaLoaded` / `trackIaaImpression`; DebugView `sdk_init` có `ump_finish`, `mobile_ads_finish`, `remote_config`, `appsflyer`; build release cài lên máy, mở lạnh → `adb logcat -b crash` rỗng.

## EXT-RC-GROUP — Gộp key Remote Config theo màn vào parameter JSON — ngoài sheet

> Không có dòng trong sheet MO nên không có MO-ID. Skill nhận mục này qua prompt ("gộp RC", "gộp key RC", "merge RC",
> "RC group"…). Nguồn: A052 Horae Tarot v1.0.3 (commit `b3701fb` "v1.0.3 merge RC"), làm theo mẫu A045 1.0.9, a037,
> a027. Dòng dán sheet MO ghi `EXT-RC-GROUP (ngoài sheet)`. Để ở nhóm setup vì đụng RC của mọi màn.

- **Yêu cầu**: mỗi màn / tính năng chỉ dùng **một parameter kiểu JSON** trên Firebase (`splash_config`,
  `language_config`, `onboard_config`, `noti_config`, `rate_config`…) thay cho nhiều key phẳng. MO sửa 1 chỗ cho cả màn;
  condition và A/B test làm trên 1 parameter.
- **Nghiệm thu**:
  - Không tạo parameter nào trên Firebase thì app chạy y như hiện tại: default trong code = giá trị Firebase đang chạy
    (trừ khi user chọn khác ở câu hỏi 4).
  - Field thiếu, sai kiểu, JSON hỏng, hay parameter bị lưu thành số / boolean: dùng default, không crash, log 1 lần.
  - Getter trong `SharedPrefs` giữ nguyên tên và kiểu cũ nên chỗ gọi không phải sửa.
  - Tên field theo option user chọn ở câu hỏi 1.
  - Có tài liệu RC của app, CLAUDE.md và sheet "Remote config" của file checklist PO đã cập nhật.
  - Báo cáo cuối **in khối RC đã chỉnh** theo mẫu ở bước 10.
- **Hỏi user trước khi code.** Đây là quyết định của owner, không tự chọn. Dùng AskUserQuestion, tối đa 4 câu mỗi lần:
  câu 1–4 trước, câu 5 hỏi sau hoặc theo mặc định khuyên.
  1. **Đặt tên field trong JSON** (bắt buộc hỏi):
     - *Giống tên key RC cũ* (khuyên dùng, A052): field = đúng tên key phẳng cũ, vd `onboard_config.enable_onboard_1`,
       `noti_config.noti_lockscreen_slots`. JSON phẳng 1 tầng, không lồng object. MO chép giá trị key cũ sang JSON,
       không phải tra bảng đổi tên. Đổi lại tên dài, lặp tiền tố của nhóm.
     - *Tên mới rút gọn* (A045, a037, a027): bỏ tiền tố trùng nhóm, gom object lồng, vd `onboard_config.enable_ob1`,
       `splash_config.native_full.countdown_time`, `noti_config.lockscreen.slots`. JSON gọn, nhưng tài liệu phải có cột
       "Thay cho" và MO/QC phải tra bảng. A052 làm kiểu này trước, owner xem xong yêu cầu đổi lại tên cũ.
  2. **Phạm vi**: gộp mọi nhóm, hay chỉ một số màn (vd luồng first-open).
  3. **Key phẳng cũ**: cắt hẳn, bản mới chỉ đọc JSON (khuyên, như A045 / a037 / a027 / A052); hay đọc JSON trước rồi
     fallback key phẳng.
  4. **Default trong code**: = giá trị Firebase đang chạy (khuyên); hay giữ default code cũ.
  5. **Kiểm thử**: chỉ verify trên máy (A052); hay thêm unit test cho `RcGroup` (A045 `RcGroupTest`).
- **SDK**: xtechads không có API nhóm RC. `RemoteConfigManager` (`xtechcore`) ghi mọi key có trên server xuống prefs
  `<applicationId>` theo kiểu đoán Long → Double → Boolean → String; không xoá key cũ, không ghi key không có trên
  server. Hệ quả:
  - Parameter JSON mà MO nhập thành số hoặc `true` thì `getString` ném lỗi, nên đọc nhóm phải bắt lỗi.
  - Key test tiêm vào prefs sẽ bị fetch đè nếu key đó có trên server.
- **Chuẩn của mục này = A052** (A013 không gộp RC). Đường dẫn tính từ `app/src/main/java/com/ai/live/tarot2/`:
  - `domain/preference/RcGroup.kt`: đọc 1 parameter JSON theo tên field (`string` / `long` / `bool` / `list`, path chấm
    cho object lồng).
    - Cache theo chuỗi gốc; mọi lỗi trả null để getter rơi về default.
    - Log 1 lần khi parameter sai kiểu lưu hoặc không phải JSON object.
    - Số nhận cả dạng chuỗi (`"3"`), không nhận số thập phân; boolean nhận `true/false`, `1/0`; list nhận mảng hoặc
      chuỗi phẩy.
  - `domain/preference/SharedPrefs.kt`: mỗi nhóm 1 khối `/** Start xxx_config *** {JSON mặc định đầy đủ} */` …
    `/** End xxx_config */`. Trong khối là `RcGroup("xxx_config", ::getString)` và các getter cũ đọc field kèm default.
    Khối comment là ngoại lệ có chủ đích của luật "không comment": dev / MO / QC tra cấu trúc JSON ở đây; sửa field
    thì sửa comment trong cùng commit.
  - `docs/remote-config-group.md` (gốc repo): tài liệu cho MO / QC.
  - Option tên mới rút gọn: xem A045 `docs/features/remote-config-group.md` và `domain/preference/RcGroup.kt` (thêm
    `json(path)` trả JSON con dạng chuỗi), a037 `docs/remote-config-group.md` §5.
- **Remote config**:
  - Parameter `<màn>_config`, data type JSON trên Firebase.
  - Parameter JSON đã có từ trước (vd `language_config`) thì giữ field cũ, chỉ thêm field mới vào.
  - Để phẳng, không gộp:
    - key SDK tự đọc theo tên (`ads_config`, `af_*`, xem § Tổng quan nhóm);
    - key ads dùng ở nhiều màn (interval inter, preload inter, reload native in-app, `click_ad_action`);
    - flag lẻ 1 key cho 1 tính năng (vd A/B UI exit `exit_ui_type`);
    - config server (host, API key).
- **Placement / tracking**: không đổi.
- **Cách làm**:
  1. Kiểm kê key RC phẳng: delegate `SharedPreferenceProperty` trong `SharedPrefs` và chỗ khác đọc RC theo chuỗi. Tách
     riêng key state local (đếm, cờ đã hiện…), không phải RC.
  2. Chia nhóm theo màn / tính năng; chốt danh sách key để phẳng.
  3. Đối chiếu key đã lên store: `git show origin/main:<đường dẫn SharedPrefs>` và các nhánh release `v<x>`. Phân loại
     key đã phát hành / chỉ có ở nhánh chưa phát hành. Dùng cho mục "chuyển key cũ" và cột Version note.
  4. Đọc Firebase đang chạy: file `files/frc_*_firebase_activate.json` của app trên máy debug (`run-as`).
     - Clear data vài lần để bắt các nhánh A/B (`abt_experiments_key` → `affectedParameterKeys`, `variantId`).
     - Ghi lại template version.
     - Không in hay ghi secret (`host_key`, API key) ra doc, sheet, báo cáo.
  5. Code: thêm `RcGroup` (port từ A052 nếu app chưa có), viết khối nhóm, bỏ delegate key phẳng. Default theo câu 4.
  6. Đối chiếu tự động bằng script tạm trong scratchpad, không commit:
     - mỗi getter có field trong JSON của khối comment, và ngược lại;
     - fallback trong code = giá trị trong JSON;
     - option "giống tên key cũ": mọi field (trừ field vốn có của parameter cũ) trùng 1 key phẳng cũ.
  7. Build, chạy grep convention của app.
  8. Verify trên máy 3 lượt:
     - chỉ có key phẳng → bản mới bỏ qua;
     - tiêm JSON đủ field khác default → hành vi đổi đúng;
     - sai kiểu: parameter lưu thành số, chuỗi `{broken`, boolean → không crash, về default, log 1 lần.

     Tiêm bằng cách sửa prefs `<applicationId>.xml`: force-stop → pull → sửa → push qua `run-as`. Dùng parameter chưa có
     trên Firebase để fetch không đè. Xong thì gỡ key test.
  9. Tài liệu:
     - `docs/remote-config-group.md` theo khung A052 / A045: tóm tắt, quyết định, bảng field (option tên mới thêm cột
       "Thay cho"), key để phẳng, chuyển key cũ, giá trị Firebase + việc MO, QC, checklist, log;
     - CLAUDE.md của app;
     - sheet "Remote config" (`conventions.md` §1). Cột Version note: key cũ "Từ vX · vY chuyển vào xxx_config (giữ
       tên field)" hoặc "… vY thay bằng xxx_config.<field>"; key chưa từng phát hành "Không bản nào dùng · …";
       parameter nhóm "Từ vY".
  10. **In RC đã chỉnh** (bắt buộc, cuối báo cáo). Mỗi parameter 1 khối; value là JSON mặc định viết gọn trên 1 dòng,
      đúng thứ tự field trong khối comment:

      ```text
      key: language_config
      type: json
      value: {"priority_languages": ["system", "en", "es"], "finger_position": 1, "buffer_language_alt": true}

      key: onboard_config
      type: json
      value: {"enable_onboard_1": true, "enable_onboard_2": true, "time_show_button_X_fsn": 3}
      ```

      Kèm lưu ý cho MO:
      - parameter đã có trên Firebase → thêm field vào JSON hiện có;
      - A/B đang chạy trên key phẳng → dựng lại trên parameter mới;
      - 1 condition thay cả JSON.
- **Bẫy**:
  - Condition / A/B trên key phẳng mất tác dụng khi cắt key. MO phải dựng lại trên parameter mới (A052: `_exp_abt_2`
    trên `enable_onboard_3` / `enable_onboard_4` → `onboard_config`; A045: `logic_pass_splash` → `splash_config`).
  - Default code cũ thường lệch Firebase (A052 lệch 5 key, A045 lệch 9). Đọc Firebase trước khi chọn default.
  - Một condition Firebase thay **cả JSON**: field nào muốn khác default phải ghi đủ trong JSON của condition đó.
  - Parameter JSON đã có (vd `language_config`): tạo lại JSON chỉ có field mới là mất field cũ.
  - SDK lưu theo kiểu đoán: JSON nhập thành số / boolean làm `getString` ném lỗi, nên `RcGroup` phải bắt lỗi.
  - Test: key có trên Firebase bị fetch đè sau khi tiêm prefs.
  - Field số không nhận số thập phân (`3.5` → default).
  - Option tên mới rút gọn: MO / QC dễ dò nhầm key cũ với field mới. A052 phải đổi lại tên sau khi đã gửi MO → luôn hỏi
    câu 1 trước khi code.
  - Script sửa file Excel: dòng có sẵn có thể ghi `r` sau thuộc tính khác (`<row customHeight="true" … r="195">`). Dò
    dòng phải nhận cả dạng này, không thì tạo dòng trùng số và Excel báo file lỗi.
- **QC**:
  - Không tạo parameter nào: app chạy đúng mặc định = hành vi Firebase hiện tại.
  - Tạo parameter với 1 field khác default (vd tắt 1 trang Onboard): chỉ hành vi đó đổi.
  - Sai kiểu (`123`, `{broken`): không crash, về mặc định.
  - Chỉ còn key phẳng cũ (vd tắt Skip OB2), không có parameter nhóm: bản mới **không** ăn key cũ.
  - A/B dựng lại trên parameter mới: mỗi nhánh nhận đúng giá trị (đọc `frc_*_firebase_activate.json`).

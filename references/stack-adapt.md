# Áp recipe vào từng kiểu stack

Recipe trong `references/*.md` viết theo A013, tức Compose + Navigation3 + Koin + xtechads. Trước khi
code, chạy `scripts/detect_stack.py <repo>` để biết app thuộc kiểu nào bên dưới, rồi đổi theo bảng.

## 1. Bốn kiểu stack đang có (khảo sát 10/2026)

| Kiểu | App | Ghi chú khi áp recipe |
|---|---|---|
| **Chuẩn**: Compose + Nav3 + Koin + xtechads | a013 (1.8.2), a027 (1.8.3), a014 (1.7.1), a016 (**1.4.6**, cũ nhất), a034 (1.7.4), a037 (1.7.2), a039 (1.7.2), a044 (1.6.9), a045 (1.7.9), a047 (1.7.5) | Áp thẳng. Kiểm tra API recipe dùng có trong version SDK của app không (mục 3). |
| **Multi-module** | a042 Langofy (`core:ads`, `feature:firstflow`…), a041 Duo-Speak | Ads/RC nằm ở `core:ads`; notification, receiver, manifest nằm ở `app`; Splash/Language/Onboard nằm ở `feature:firstflow`. Đặt code đúng module sở hữu nó; component nào trong manifest thì khai ở module chứa class đó. |
| **Không dùng SDK** (lớp ads tự viết) | a028 Casto, a036 Remote TV, a041 Duo-Speak | Có `ads/adunit`, `ads/base/ConsentHelper`, `ads/config/ConfigKeyA–D`, `ads/remoteconfig/RemoteConfigManager`, `ads/adjust`. **Không migrate sang SDK trong task MO**; làm trên lớp sẵn có theo bảng mục 2. |
| **XML / Fragment / lẫn** | a033 PDF (FO bằng Compose, phần còn lại XML + Nav2, Groovy gradle), a031 Qibla (XML + Hilt + Nav2), a041 (phần lớn XML) | Logic (manager, receiver, RC, ads) giữ nguyên; chỉ đổi lớp UI theo mục 4. a031: xtechads lib 1.7.1 nhưng plugin 1.6.6, lệch version, đừng làm lệch thêm. |

## 2. Bảng tra khái niệm: chuẩn A013 → app khác

| Khái niệm | A013 / SDK | Cách tìm chỗ tương ứng ở app khác |
|---|---|---|
| Key Remote Config | `SharedPreferenceProperty("key", default)` trong `domain/preference/SharedPrefs.kt`. `RemoteConfigManager` của SDK chép mọi key RC vào prefs. | Grep `SharedPreferenceProperty(`. App không SDK thì grep `RemoteConfigManager` / `getString(` / `ConfigKey`. App gom RC thành JSON nhóm (`language_config`, `onboard_config`, `noti_config` ở a037/Langofy/a034) thì **thêm field vào đúng nhóm**, không tạo key phẳng. |
| Placement ads | Tên trong `app/config/ads_config.json` (`placements[]`); code gọi `AdGroupUnit.of("…")` / `NativeBannerGroupView("…")` | Mở `ads_config.json` của app xem kiểu tên đang dùng (`language` hay `native_lang`); app không SDK thì xem `ConfigKeyA–D`, enum AdUnit. |
| Hook click ads bất kỳ | `BaseAds.clickedAnyAds`, A013 hook ở `AppNavigation.kt` | Grep `clickedAnyAds` (mỗi app để một chỗ: AppNavigation, MainNavigation, MainApp, AdsManager, AdsEffects, App.kt). a036 dùng `click_ads_type`. |
| Luồng màn FO | `navigationFlow` (`splash_next`, `language_next`, `select_next`, `onboard_next`) trong ads_config | Grep `splash_next` / `splashNext` (a016 dùng camelCase). |
| Inter in-app | `AdsManager.showInterInApp` + `AppBackHandler` | Grep `showInterInApp` / `inter_inapp` / `InterInAppEffect`. |
| Noti | `domain/notification/NotificationManager.kt` + `NotificationReceiver` + `BootReceiver` | Chạy `detect_stack.py` (mục `key_files`), hoặc grep `NotificationCompat.Builder`. |
| Deep link mở lại app | `Constant.KEY_OPEN_FROM` / `OPEN_FROM_*` / `OPEN_TO_*` → `MainActivity` → `app_open_from` | Grep `OPEN_FROM_`. Tên hằng mỗi app một kiểu (`OPEN_FROM_PINNED_NOTIFICATION` / `OPEN_FROM_NOTIFICATION_PINNED` / `OPEN_FROM_NOTIFY_PINNED`): dùng đúng kiểu app đang có. |
| DI | Koin `single { }` / `viewModel { }` trong `di/Modules.kt` | Hilt: `@Singleton class … @Inject constructor` + module `@Provides`. Không có DI: object/singleton theo pattern sẵn có của app. |

## 3. Khi recipe cần API SDK mà app đang dùng bản cũ

- Mỗi recipe có ghi `sdk.min_version`. Xem bằng `catalog.py show <ID>`.
- Version của app thấp hơn thì **không tự bump**. Báo user 2 phương án:
  - (a) bump SDK. Đổi `xtechads` và plugin `com.xtech.ads` **cùng version**, đọc
    `xTechSDK/docs/CHANGELOG.md` giữa 2 version, build cả debug lẫn release.
  - (b) làm ở tầng app bằng API đang có.
- License whitelist: app nằm ngoài `allowedPackages()` của SDK sẽ crash `"Unauthorize"`. Gặp lỗi này thì
  báo SDK team, đừng vá ở app.

## 4. Đổi lớp UI Compose → View/XML

| Compose (recipe) | View/XML |
|---|---|
| `BackHandler` / `PredictiveBackHandler` | `onBackPressedDispatcher.addCallback(owner) { … }`; predictive back (API 34+) dùng `OnBackPressedCallback` + `handleOnBackProgressed` |
| `LaunchedEffect` + `delay` (hint ngón tay sau N giây) | `lifecycleScope.launch { delay(); view.isVisible = true }` gắn với `repeatOnLifecycle(STARTED)`; animation bằng `ObjectAnimator` / Lottie `LottieAnimationView` |
| `NativeBannerGroupView(placement)` | View tương ứng của SDK (xem `xtechads/docs/ADS_MODULE_GUIDE.md`) hoặc `ComposeView` nhúng vào layout XML |
| `HorizontalPager(contentPadding = 1.px)` | `ViewPager2` + `offscreenPageLimit = 1` + padding 1px trên RecyclerView bên trong (`clipToPadding = false`) để page kế được tính là hiển thị |
| Dialog Compose | `DialogFragment` / `BottomSheetDialogFragment` |
| Navigation3 `backStack.add(Dest…)` | `startActivity(Intent…)` / `findNavController().navigate(…)` |

## 5. Build verify

- Lệnh lấy từ `detect_stack.py` (đọc `CLAUDE.md` hoặc `~/.claude/night-dev/projects.yaml`). Nhiều app
  dùng flavor riêng: a034 và a036 dùng `assembleTestDebug`, a033 dùng `:app:assembleTesterDebug`.
- Luôn chạy `set -o pipefail; <lệnh> 2>&1 | tail -30`, vì nếu không có `pipefail` thì exit code là của
  `tail`.
- Build baseline **trước khi sửa**. Baseline đã fail sẵn (WIP của người khác) thì báo user, đừng đổ cho
  thay đổi của mình.
- Đụng ads/R8/manifest thì nên build thêm release (bắt lỗi thiếu keep rule). **Tắt các task đẩy ra ngoài**:
  - nhiều app có Crashlytics plugin nên build release tự upload mapping file lên Firebase;
  - thêm `-x uploadCrashlyticsMappingFile<Variant>` (vd `-x uploadCrashlyticsMappingFileTestRelease`), hoặc chỉ
    build release khi user đồng ý.
- **Build lạnh lần đầu có thể mất 10+ phút** (worktree/clone mới). Chạy nền (`run_in_background`) hoặc
  timeout 600000 ms rồi đọc log; đừng huỷ giữa chừng.
- Một số repo commit cả file trong `build/` (vd a036 `googlebannerrefresh/build/...`), nên build xong
  `git status` bẩn. Ghi `git status` **trước** khi build:
  - file nào sạch trước build mà bẩn sau build là do build → báo user;
  - đừng coi là WIP, cũng đừng tự revert file vốn đã bẩn sẵn.

## 6. Đặc thù app đã gặp (10/2026 — kiểm lại code hiện tại trước khi tin)

| App | Đặc thù |
|---|---|
| a036 (không SDK) | `RemoteConfigManager` thử kiểu Long trước Boolean/String:<br>• Boolean phải là `true`/`false` (không `1`/`0`)<br>• slot giờ phải có `:` (vd `"20:00"`)<br>• bọc chỗ đọc giá trị sai kiểu<br><br>`AdsManager.passedNotificationSplash` khai nhưng không được set; cờ thật là `permissionFinished` (biến cục bộ ở `SplashScreen`).<br><br>`MainActivity.initArgs` chỉ quay về Splash khi `openTo ≠ DEFAULT`.<br><br>`TrackingScreenName` inject `AdsManager` (kéo theo RevenueCat/UMP), nên không dùng trong overlay/Activity phụ.<br><br>Build debug tắt Analytics collection: xem event bằng logcat.<br><br>applicationId ≠ namespace: lệnh adb dùng applicationId, FQCN class theo namespace. |
| a037 | RC gom JSON nhóm (`noti_config`, `language_config`, `onboard_config`, `home_config`, `clean_config`; luật trong `docs/remote-config-group.md`). Condition trên Firebase thay nguyên JSON, nên thêm field thì MO phải chép đủ object.<br><br>After-click native dùng `actionClicked` của ads_config qua `NativeAdClickAction`. |
| a028 (không SDK) | Cùng lớp ads tự viết như a036: RC thử Long trước (Boolean `true`/`false`, slot có `:`). `TrackingScreenName` mặc định `allowShowInterInApp=true`, kéo theo AdsManager, nên không dùng trong overlay. **JDK:** Gradle 8.13 + `VERSION_19` cần JDK 19–23 (JBR 25 của Android Studio không chạy; dùng JDK 21 ở `~/.gradle/jdks`, xem `jdk_suggest` của `detect_stack.py`). |
| a033 | Groovy gradle; FO bằng Compose, phần còn lại XML + Nav2; flavor `Tester` (`:app:assembleTesterDebug`). |
| a031 (Qibla) | XML + Hilt + Nav2; xtechads lib 1.7.1 nhưng plugin 1.6.6 (lệch version). |
| a016 | xtechads 1.4.6 (cũ nhất), `navigationFlow` dùng camelCase (`splashNext`). |
| Langofy (a042), a041 | Multi-module: ads/RC ở `core:ads`, FO ở `feature:firstflow`, noti/receiver ở `app`. |


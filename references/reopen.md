# Nhóm reopen: quay lại app từ bên ngoài

## Tổng quan nhóm

- Mọi lối vào app từ bên ngoài (shortcut launcher, widget, notification, lock screen, Open with, uninstall) đều phải làm 3 việc theo thứ tự:
  1. Reset task và chạy lại Splash để ăn ads.
  2. Log `app_open_from`.
  3. Sau Splash mới đi tới đích (`openTo`).
- Xương sống ở A013 có 4 bước:
  1. Intent dùng `ACTION_VIEW` + `FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TASK`, kèm extras `Constant.KEY_OPEN_FROM` / `Constant.KEY_OPEN_TO`.
  2. `MainActivity.initArgs` đọc extras rồi ghi vào `prefs.openTo`.
  3. Điều hướng rồi reset `openTo`: `SplashScreen.goNextScreen` lo Uninstall, `HomeScreen` lo các feature khác.
  4. `MainActivity.trackAppOpenFrom` bắn event `app_open_from`.
  - Chi tiết ở MO-78.
- Quy ước đường dẫn:
  - A013: tính từ `app/src/main/java/com/example/a013_recovery/`. Riêng res, manifest, config thì tính từ gốc repo.
  - SDK: tính từ `xTechSDK/xtechads/src/main/java/com/example/xtechads/`.
  - App khác: tính từ thư mục package gốc của app (`…/src/main/java/<package>/`).
  - File có thể đã đổi chỗ, nên tìm theo symbol (`grep -rn <symbol>`). Luôn đọc code A013 bản hiện tại, không tin mô tả ở đây hơn code.
- Mục liên quan ở nhóm khác:
  - MO-99 (nhóm splash): unit inter splash riêng cho lượt re-open.
  - MO-95 và MO-68…73 (nhóm noti): các loại notification.
  - MO-81 (nhóm ads): back handler.

## MO-74 — Uninstall shortcut

- **Yêu cầu**:
  - Nhấn giữ icon app hiện dynamic shortcut "Uninstall" và 1 shortcut tính năng chính (Figma `605-3770`).
  - Bấm "Uninstall" thì app chạy lại từ Splash (có ads), rồi vào màn giữ chân `ScrUninstall`. Màn này có: gợi ý tính năng, nút "Keep using" và nút gỡ thật.
  - Ước lượng: dev 2h, QC 1h.
- **Nghiệm thu**:
  - Nhấn giữ icon thấy "Uninstall" (đúng ngôn ngữ đang chọn) và 1 shortcut tính năng.
  - Bấm vào thì đi Splash có ads rồi tới `ScrUninstall`. Log `app_open_from` = `shortcut_uninstall`.
  - Mỗi card tính năng: show inter rồi vào đúng màn tính năng.
  - Back, Home, "Keep using": về Home (xem MO-91).
  - Nút gỡ mở được trang App info có nút Gỡ cài đặt.
  - Light và dark đều đúng Figma.
- **SDK**:
  - `domain/shortcuts/BaseShortcutManager.kt`:
    - `updateShortcuts()` gọi `ShortcutManagerCompat.setDynamicShortcuts` với list từ `provider`.
    - `buildShortcut(...)` dựng `ShortcutInfoCompat`.
    - `openIntent(context, target, openTo, openFrom = OPEN_FROM_SHORTCUT)` dựng Intent `ACTION_VIEW` + NEW_TASK|CLEAR_TASK kèm extras.
  - `common/Constant.kt` có sẵn `KEY_OPEN_TO`, `KEY_OPEN_FROM`, `OPEN_TO_UNINSTALL`, `OPEN_FROM_SHORTCUT`.
  - SDK không có màn Uninstall.
  - A013 không dùng `BaseShortcutManager` mà tự viết class tương đương.
- **Chuẩn A013**:
  - `domain/shortcuts/ShortcutManager.kt`, gồm `ShortcutManager.updateShortcuts()` và `getShortcutsList()`:
    - Chỉ có 1 shortcut, id `delete_app`, label `R.string.uninstall`, icon `ic_uninstall`.
    - Đích là `MainActivity` với `OPEN_TO_UNINSTALL` + `OPEN_FROM_SHORTCUT`.
    - Được gọi trong `SplashScreen` (LaunchedEffect, `Dispatchers.IO`) ở mỗi lần mở app.
  - `MainActivity.initArgs` ghi `prefs.openTo`. `SplashScreen.goNextScreen()` xét `OPEN_TO_UNINSTALL` TRƯỚC `firstOnboard`, rồi đi `AppDestination.Uninstall` và pop Splash. Nhờ vậy user mới cũng bỏ qua FO.
  - `ui/screen/uninstall/UninstallScreen.kt`:
    - RC `new_uninstall_enable` chọn giữa `UninstallContentNew` và `UninstallContent` (UI cũ).
    - Trong `UninstallContentNew`:
      - 4 card "Try now": `adsManager.showInterInApp`, rồi về Home và mở màn tính năng.
      - "Keep using app": về Home.
      - "Uninstall app": `disableAdResumeOnTime()` rồi `openAppSetting()` (`utils/AppUtils.kt`, dùng `ACTION_APPLICATION_DETAILS_SETTINGS`).
    - Reset `prefs.openTo` 1s sau resume. User chạm vào bất kỳ nút nào thì `prefs.firstOnboard = false`.
  - **Lệch chuẩn**: A013 KHÔNG có shortcut tính năng chính.
    - `trackAppOpenFrom` vẫn còn map `shortcut_enhance/protector/photo/junk`, nhưng không ai build các shortcut đó.
    - Mẫu "Uninstall + 1 tính năng" ở app khác:
      - a034 `domain/shortcuts/ShortcutManager.kt` (`procam` + `uninstall`).
      - a033 (`shortcut_read_pdf` + `shortcut_uninstall`).
      - a037 `common/utils/ShortcutManager.kt`.
      - a041 `utils/shortcut/ShortcutManager.kt`.
      - Langofy `LangofyShortcutManager`.
- **Remote config**:
  - `new_uninstall_enable` (Boolean, mặc định `true`): `true` = UI mới có gợi ý tính năng, `false` = UI cũ.
  - Alias: A045 cho thêm value `uninstall` vào `navigationFlow` `*_next` (`destFromNavFlow`).
- **Placement / tracking**:
  - Screen: `ScrUninstall`.
  - `button_click` với `button_name` là `BtnBack` / `BtnHome` / `BtnKeepUsingApp` / `BtnUninstallApp` / `BtnTryNow`, kèm param `uninstall_feature`.
  - `app_open_from` = `shortcut_uninstall`. Alias: A045 `open_from_shortcut`, A47 `open_from_launcher_uninstall_shortcut`.
  - Shortcut tính năng: A013 `trackAppOpenFrom` map `shortcut_<tính năng>` (vd `shortcut_enhance`); A048, A049 log chung `shortcut`.
  - Inter splash riêng cho lượt mở từ uninstall: a044 `splash_r3` / `interSplashUninstall`, a039 `interOSplash`. Xem MO-99.
- **Cách làm**:
  1. **ShortcutManager**:
     - List gồm [tính năng chính, Uninstall].
     - Dựng Intent bằng `BaseShortcutManager.openIntent`, hoặc tự dựng đúng action và flags.
     - Gọi `updateShortcuts()` ở Splash, chạy nền, mỗi lần mở app, để label đi theo ngôn ngữ.
     - Gọi lại ngay sau khi user đổi ngôn ngữ trong app (A013 `LanguageManager.updateLanguage`; A048, A049 cũng vậy). Đổi ở Setting không đi lại Splash, thiếu chỗ này thì nhãn giữ ngôn ngữ cũ tới lần mở sau.
     - Launcher chỉ hiện 4 shortcut: giữ tổng ≤ 4, hoặc cho Uninstall nằm trong 4 rank thấp nhất (xem Bẫy, Q48).
     - Đọc `domain/shortcuts/ShortcutManager.kt` ở A013 (bản hiện tại) và `BaseShortcutManager` ở SDK.
  2. **MainActivity**:
     - Chỉ khi `savedInstanceState == null` mới đọc extras vào `prefs.openTo` và log `app_open_from`.
     - Đọc `MainActivity.initArgs` / `trackAppOpenFrom` ở A013.
  3. **Splash**:
     - Ads xong thì xét `OPEN_TO_UNINSTALL` trước mọi nhánh FO, rồi thay Splash bằng `ScrUninstall`.
     - Đọc `SplashScreen.goNextScreen` ở A013.
  4. **Màn `ScrUninstall`** dựng theo Figma:
     - Header có back và home.
     - List tính năng: bấm thì show inter rồi vào tính năng.
     - Nút "Keep using" và nút "Uninstall".
     - Đọc `UninstallScreen` + `UninstallContentNew` ở A013. Back theo MO-91.
  5. **Shortcut tính năng**:
     - Dùng `openTo` riêng. Home đọc, điều hướng xong thì reset.
     - Xem cách A013 `HomeScreen` đọc `prefs.openTo` trong LaunchedEffect.
  6. **App XML/Fragment và app non-SDK**:
     - App XML/Fragment: a031 `fragments/uninstall/UninstallFragment.kt`.
     - App non-SDK: A028, a036, a041.
     - Giữ nguyên Intent và flags. Đích là Activity chạy Splash (a041 là `FirstOpenActivity`, a036 dùng `PendingStart.Uninstall`).
  - **Ref A047/A048 khác A013** (đọc code bản hiện tại):
    - Try KHÔNG show inter: A048 `UninstallViewModel.backToMain(feature.tab)`, A047 `UninstallViewModel.onTry…` điều hướng thẳng. Nghiệm thu MO-74 vẫn ghi có inter: theo ref thì ghi vào bảng khác biệt và hỏi user (A049, 10/2026: theo A048, bỏ inter).
    - Try đi về đâu:
      - A047: điều hướng thẳng tới tính năng, bỏ `ScrUninstall` khỏi stack.
      - A048: về `ScrMain` đúng tab của tính năng.
      - A049: về Home, Home mở tính năng qua `openTo` như lượt mở từ noti (`HomeViewModel.openPendingFeature`).
    - Reset `openTo` ngay ở Splash, trước khi điều hướng: A048 `SplashViewModel.nextScreen` (mọi đích), A047 và A049 (nhánh Uninstall). A013 reset trong `UninstallScreen`, 1s sau resume.
    - Không có RC `new_uninstall_enable`, chỉ 1 UI.
    - Shortcut (`common/utils/ShortcutsUtil.kt`): A047 chỉ có Uninstall. A048 tính năng chính (rank 0) rồi Uninstall (rank 1). A049 3 tính năng rồi Uninstall cuối.
    - Tên click: A048, A049 `BtnTryNow<Feature>` lấy từ `UninstallFeature.clickName` (không dùng param `uninstall_feature`), nút giữ chân `BtnKeepUsing`. A047 `BtnUninstallTry` / `BtnUninstallCard` / `BtnUninstallKeep` / `BtnUninstallConfirm` / `BtnUninstallHome`.
- **Bẫy**:
  - **POLICY**: shortcut đã tên "Uninstall" thì màn này PHẢI có đường gỡ thật.
    - Cách 1: App info qua `ACTION_APPLICATION_DETAILS_SETTINGS` (A013, A045 `openAppSettings`).
    - Cách 2: `ACTION_DELETE`, nhưng phải có fallback sang App info khi fail (Langofy `AppUtils`).
    - Màn chỉ toàn nút giữ chân là hành vi lừa user.
  - Quên reset `openTo` thì mọi lần mở app sau đều rơi vào ScrUninstall.
  - Thiếu `FLAG_ACTIVITY_CLEAR_TASK` thì app đang mở sẽ không chạy lại Splash (xem MO-78).
  - Phải gọi `disableAdResumeOnTime()` trước khi mở App info. Nếu không, lúc user quay lại sẽ dính app-open resume.
  - A045 `common/utils/ShortcutsUtil.kt`: nếu sau `setDynamicShortcuts` list rỗng thì set lại label "UninstaII" (chữ I hoa thay chữ l). Đây là mẹo lách launcher, có rủi ro policy. Không nhân bản khi PO chưa duyệt.
    - A047 `ShortcutsUtil.createShortcut` cùng tình huống chỉ thử lại với id `UninstaII`, nhãn vẫn là chuỗi `uninstall` đã dịch, nên không đụng Q30.
  - **Launcher chỉ hiện 4 shortcut** (Pixel / Launcher3): lấy 4 cái rank thấp nhất, từ cái thứ 5 bị ẩn. Có hơn 4 shortcut mà Uninstall rank cuối thì Uninstall biến mất (A049, kiểm trên emulator, 10/2026).
    - Giữ tối đa 4 (A049 `ShortcutsUtil` đang tắt Horoscope, còn 3 tính năng + Uninstall), hoặc cho Uninstall nằm trong 4 rank thấp nhất. Chốt với PO (Q48).
  - Activity đã finish (vd Exit gọi `finishAffinity` như A047) rồi mở lại từ Recents: hệ thống giao lại intent shortcut cũ, app có thể vào lại ScrUninstall. Lọc ở `initArgs` (xem MO-78).
  - Ảnh card tràn ra ngoài card (Figma export kèm bóng, ảnh to hơn card): `size` của ảnh bị kẹp theo khung Box cha. Thêm `wrapContentSize(unbounded = true)` trước `size` (A049 `UninstallCardView`).
- **QC**:
  - Nhấn giữ icon ở 2 ngôn ngữ khác nhau; kiểm tra thứ tự shortcut.
  - Đổi ngôn ngữ trong Setting rồi nhấn giữ icon ngay: nhãn đã đổi, không cần mở lại app.
  - App có hơn 4 shortcut: kiểm trên Pixel / Launcher3 rằng Uninstall vẫn hiện.
  - Mở từ shortcut khi app đã kill, và khi app đang ở màn sâu.
  - Mở từ shortcut, thoát hẳn (Activity bị finish), mở lại từ Recents: vào như mở thường, không vào lại ScrUninstall.
  - User mới chưa qua FO.
  - Nút gỡ mở App info; từ App info quay lại không hiện resume ad.
  - Light và dark.

## MO-91 — Uninstall: mọi đường back đều về Home

- **Yêu cầu**:
  - Ở `ScrUninstall`, mọi đường back đều vào Home app, không thoát app. Gồm: nút back góc trái, icon home, back cứng, vuốt back.
  - Áp cho ALL app.
- **Nghiệm thu**:
  - Mở từ shortcut, rồi back cứng hoặc vuốt: về Home, không thoát.
  - Header back hoặc icon home: về Home.
  - Nếu app có lối vào ScrUninstall từ trong app (vd Setting): back cũng về Home.
- **Chuẩn A013**:
  - Header back và home của `UninstallContentNew` gọi `onKeepUsingAppClick`, tức `navigateTo(ScrHomeApp, popupTos = Uninstall)`.
  - **Lệch chuẩn**: `UninstallScreen` không có back handler.
    - Khi mở từ shortcut, back stack chỉ có `Uninstall`.
    - Khi đó `NavDisplay.onBack` trong `AppNavigation` gọi `finish()`.
    - Kết quả: back cứng hoặc vuốt sẽ THOÁT app.
- **Mẫu đúng (A045)**:
  - `ui/screen/uninstall/UninstallScreen.kt` dùng `GeneralBackHandler(onBack = state.onBack)`.
  - `UninstallViewModel.backToHome()`:
    - Stack có `ScrMain`: `popToMain`.
    - Không có (mở từ shortcut): dựng `ScrMain(Home)` và bỏ `ScrUninstall`.
  - Mọi lối thoát đều gọi `markFirstOpenDone()`.
- **Cách làm**:
  1. Viết 1 hàm "về Home" dùng chung cho header back, icon home, "Keep using" và back cứng:
     - Stack có Home: pop về Home.
     - Không có: navigate tới Home và bỏ ScrUninstall khỏi stack.
     - Đọc A045 `UninstallViewModel.backToHome`.
  2. Gắn back handler ngay trong composable `ScrUninstall` (BackHandler + predictive, xem MO-81) và gọi hàm trên. Ở A013 thì thêm vào `UninstallScreen`, nhưng đọc bản hiện tại trước xem đã có chưa.
  3. Rời màn theo đường này thì đánh dấu đã xong FO (A013 `prefs.firstOnboard = false`).
  - **Ref A047/A048 khác A013**:
    - A048 `UninstallViewModel.backToMain`: 2 nhánh như A045 (stack có `ScrMain` thì pop `ScrUninstall`; không có thì navigate `ScrMain` đúng tab, bỏ `ScrUninstall`). Back cứng là `BackHandler` thường, log `BtnDeviceBack`, không chèn inter.
    - A049 theo A048 (10/2026): `UninstallViewModel.backToHome` + `GeneralBackHandler(showInterAd = false)`.
    - A047 dựng sẵn Home dưới `ScrUninstall`: `SplashViewModel.nextScreen` navigate `ScrMain` rồi mới đẩy `ScrUninstall`, nên mọi lối ra chỉ cần pop. Back cứng, header back và icon home chèn inter in-app theo interval (`DeviceBackHandler` → `InterInAppEffect`), nút "Keep" thì không.
    - Đánh dấu xong FO khi rời màn (bước 3): A047 có (`markFirstOpenDone`), A048 không. A049 có (`prefs.firstOpen = false` trong `backToHome`, cả lúc Try): user yêu cầu dù A048 không làm (Q46).
- **Bẫy**:
  - Handler phải nằm trong nội dung entry, tức đăng ký sau `NavDisplay`. Như vậy mới chặn trước được `NavDisplay.onBack` (dispatcher chạy theo LIFO).
  - `GeneralBackHandler` của A045 mặc định chèn `inter_inapp` khi back cứng. Muốn về Home mà không có ad thì đặt `showInterAd = false` (chốt với MO).
  - Đừng để back ở ScrUninstall rơi thẳng vào popup Exit của Home.
  - Try 1 tính năng mà không bỏ `ScrUninstall` khỏi stack thì back từ màn tính năng lại về ScrUninstall (ghi chú ở A047 `UninstallViewModel`, `UNINSTALL_POPUP_TO`).
- **QC**:
  - Android ≤13 bấm nút back. Android 14+ vuốt cả 2 mép.
  - Mở từ shortcut cả khi app đã kill lẫn khi app đang background.
  - Try 1 tính năng rồi back từ màn tính năng: về Home, không về ScrUninstall.

## MO-76 — Popup / thanh gợi ý add widget

- **Yêu cầu**:
  - Có UI chủ động mời user thêm widget ra màn hình chính: popup gợi ý và thanh/card trong app.
  - Bấm Add thì hiện dialog pin của launcher.
  - Ước lượng: dev 3h, QC 1h. QC check content, từng nút vào đúng luồng, light/dark.
- **Nghiệm thu**:
  - Popup chỉ hiện đúng điều kiện đã chốt và không đè lên ad.
  - Add: dialog pin hệ thống hiện ra. Thêm thật vào màn hình thì toast thành công.
  - Đã có widget rồi thì toast "already added".
  - Launcher không hỗ trợ pin thì hiện popup hướng dẫn thủ công.
- **Chuẩn A013**:
  - Widget Glance có Recent, Deleted, Merge (`ui/screen/home/widget/…`), receiver khai trong manifest.
  - Home có section "Widget": `HomeContentNew` → `ToolsTrend` → `WidgetFreeUpCard` / `WidgetDeletedCard` / `MergedWidgetCard` + `WidgetAddButton`.
  - Luồng bấm Add:
    - `HomeScreenState.onWidgetClick` / `onMergeWidgetClick` (HomeViewModel) gọi `utils/WidgetUtil.kt` `addWidget` / `addMergeWidget`.
    - Hàm này gọi `AppWidgetManager.requestPinAppWidget` hoặc `GlanceAppWidgetManager.requestPinGlanceAppWidget`.
    - Callback `WidgetPinnedReceiver.callback` toast `add_widget_success` khi widget được thêm thật.
  - `HomeViewModel.checkAddedWidget` chạy mỗi lần resume để cập nhật trạng thái đã thêm.
  - **Lệch chuẩn**: A013 mới có "thanh" (card trong Home), CHƯA có popup gợi ý.
- **Mẫu popup**:
  - A045 (đọc `docs/features/home-widget.md`):
    - `domain/widget/WidgetSuggestGate.kt` `onReturnFromResult` mở popup khi:
      - chưa từng hiện trong lần cài này (`widget_suggest_shown`),
      - không có ad trên màn (`adsManager.isAdOnScreen`),
      - chưa pin widget nào.
    - `ui/dialog/AddWidgetSuggestPopup.kt` là popup gợi ý. `AddWidgetFailPopup.kt` là hướng dẫn 3 bước thủ công, hiện khi `WidgetPinner.canPin` = false.
    - `MainViewModel.pinSelectedWidget` / `checkWidgetPending` gọi pin, rồi kiểm tra đã pin lúc resume để toast.
    - Toàn bộ cụm UI host ở `WidgetDialogHost` trong `MainNavigation`, nên tab nào cũng hiện được.
  - Gate reward trước khi pin:
    - A045: `rewardEnhancerEnabled`, sheet `AddWidgetSheet`.
    - a034: `HomeScreen` `RewardAdHost` rồi `lifecycle.withResumed` mới gọi `WidgetUtil.requestPinWidget`.
    - A041: `MainActivity.setupSessionWidget` ẩn sheet khi `adsManager.isShowingAds`.
- **Remote config**:
  - `widget_card` (String, mặc định `"split"`): A013 dùng `"split"` = 2 card, `"merge"` = 1 card đổi luân phiên theo ngày.
  - `widget_suggest_shown` của A045 chỉ là pref cục bộ, không phải RC.
- **Placement / tracking**:
  - Overlay: `OvlAddWidget`.
  - Event: A045 `widget_click_<target>`, a034 `widget_add_success` / `widget_add_failed`.
  - Lượt mở app từ widget: `app_open_from` = `widget` (xem MO-78).
- **Cách làm**:
  1. **Widget provider**: phải có trước. A013 dùng Glance, đọc `ui/screen/home/widget/` và các receiver trong manifest.
  2. **Thanh/card trong app** có nút Add, luồng như sau:
     - Chưa hỗ trợ pin (`isRequestPinAppWidgetSupported` = false): mở popup hướng dẫn.
     - Đã có widget: toast.
     - Còn lại: gọi `disableAdResumeOnTime()` rồi `requestPinAppWidget`.
     - Đọc `WidgetUtil.addWidget` ở A013.
  3. **Popup gợi ý**:
     - Chốt trigger với PO, vd về Home từ màn Result, hoặc sau success.
     - Chỉ hiện 1 lần mỗi lần cài, không khi đang có ad, không khi đã pin.
     - Host ở tầng luôn compose (root nav), không đặt trong màn có thể không compose.
     - Đọc A045 `WidgetSuggestGate` và `WidgetDialogHost`.
  4. **Xác nhận thành công**:
     - Cách 1: success callback `PendingIntent` gửi tới receiver (A013 `WidgetPinnedReceiver`).
     - Cách 2: lúc resume kiểm tra `getAppWidgetIds` (A045 `checkWidgetPending`).
  5. **App XML/Fragment**: a031 `fragments/during_ramadan/widgets/WidgetFragment.kt` dùng cùng API.
- **Bẫy**:
  - Gọi `requestPinAppWidget` khi app không ở RESUMED (vd callback reward về lúc app đang nền) sẽ ném `IllegalStateException`. Phải bọc `withResumed` (a034).
  - Không được để popup hoặc dialog pin đè lên ad. Guard bằng `isShowingAds` / `isAdOnScreen` (A041, A045).
  - Toast gọi từ `Dispatchers.IO` bị nuốt im lặng (có ghi chú trong A013 `WidgetUtil`). Phải chuyển về Main.
  - `onSuccess` trong A013 `addWidget` chạy khi request được nhận, CHƯA chắc user đã thêm. Toast "đã thêm" phải dựa vào callback hoặc check lúc resume.
  - Callback `PendingIntent` dùng `FLAG_IMMUTABLE` thì không nhận được extra appWidgetId. Cần id thì phải dùng MUTABLE.
  - Layout RemoteViews không hỗ trợ `<Space>` và Canvas (ghi chú ở A045 `home-widget.md`).
- **QC**:
  - Launcher có và không có hỗ trợ pin.
  - Đã có widget rồi.
  - Popup chỉ hiện 1 lần, kể cả sau khi kill app.
  - Popup không đè ad.
  - Bấm widget thì đi Splash rồi đúng màn.
  - Light và dark.

## MO-77 — Open from another app ("Open with")

- **Yêu cầu**:
  - App xuất hiện trong "Mở bằng / Open with" cho đúng loại file mình xử lý. Ảnh/video cho app gallery/recovery; PDF/Office cho app PDF (ví dụ của sheet là a033).
  - Mở từ đó thì đi Splash (ads) và log `app_open_from` = `gallery` / `file`.
  - Ước lượng: dev 0.2h, QC 0.2h.
- **Nghiệm thu**:
  - Từ Files / Gallery / Drive chọn Open with thì thấy app trong list.
  - Mở thì đi Splash có ads, rồi vào Home hoặc viewer (tùy app).
  - Event `app_open_from` đúng giá trị.
  - App đang mở ở màn khác thì vẫn chạy lại từ Splash.
- **Chuẩn A013**:
  - Manifest `MainActivity` có 2 intent-filter VIEW + DEFAULT + BROWSABLE, với `mimeType` `image/*` và `video/*`.
  - `MainActivity.initArgs`: `intent.data` khác null và không chứa "Widget" thì log event riêng `open_from_gallery` (param `data`). Không điều hướng tới file.
  - `MainActivity.onNewIntent`: gặp ACTION_VIEW có data thì restart task để quay lại Splash (xem MO-78).
  - **Lệch chuẩn**:
    - A013 KHÔNG log `app_open_from` cho lượt này.
    - Các app khác log `app_open_from` với `open_from`:
      - `gallery`: a016, a27, A014, a034, a036, A045 (`OpenFrom.OPEN_FROM_VIEW_INTENT`), a041.
      - `file`: a037, a039 (`OPEN_FROM_FILE`).
- **Mẫu app file (a033)**:
  - Manifest khai các `activity-alias` theo loại file, mỗi alias có label/icon riêng, cùng trỏ `targetActivity` = `FirstOpenActivity` (Activity chạy Splash):
    - `.pdf_alias`: label `app_name`.
    - `.word_alias`: "DocX Reader".
    - `.xls_alias`: "Excel Reader".
    - `.ppt_alias`: "PPT Reader".
    - `.txt_alias`: "Text File Reader".
  - `FirstOpenActivity.isOpenedFromAnotherApp()` nhận diện lượt mở từ app khác:
    - action là VIEW / SEND / SEND_MULTIPLE / EDIT,
    - scheme là `content` / `file` / `http(s)`,
    - referrer không phải chính app.
    - Khi đúng thì log `app_open_from=gallery`.
  - a033 không có code chuyển URI sang viewer sau Splash (`CommonUtils.openToMainScreen` không mang data theo). Khi làm app file, phải tự giữ Uri và mở viewer sau Splash.
- **Mẫu app non-file (A045)**:
  - `MainActivity.isMediaViewIntent()` + `restartFromSplashIfMediaView()`.
  - Chỉ mở app và tracking, không xử lý file.
- **Placement / tracking**: `app_open_from` với `open_from` = `gallery` hoặc `file` (A013 thì là event riêng `open_from_gallery`).
- **Cách làm**:
  1. Chốt danh sách mime theo tính năng thật của app. Không khai `*/*`.
  2. Khai intent-filter VIEW + DEFAULT (+ BROWSABLE nếu cần) trên Activity host Splash.
     - Cần label/icon riêng cho từng loại file thì dùng `activity-alias`.
     - Đọc manifest A013, và manifest a033 cho phần alias.
  3. Nhận diện intent (ACTION_VIEW + data/type):
     - App đang chạy (onNewIntent) thì restart task về Splash.
     - Log `app_open_from`. Nên dùng `gallery` / `file` cho đồng bộ với đa số app.
     - Đọc `MainActivity.onNewIntent` / `initArgs` ở A013 và `MainActivity.isMediaViewIntent` ở A045.
  4. App xử lý được file (PDF/Office/viewer): giữ Uri lúc nhận intent, sau Splash điều hướng tới viewer.
     App không xử lý file: vào Home như mở thường.
  5. App XML làm y hệt ở manifest. Logic đặt trong Activity Splash.
- **Bẫy**:
  - **Quyền đọc content Uri**:
    - Quyền đọc `content://` đi kèm intent gốc.
    - Restart task bằng Intent mới thì phải mang theo data và type, và thêm `FLAG_GRANT_READ_URI_PERMISSION`.
    - Phải test mở file từ Drive/Files rồi đọc sau Splash. Không đọc được thì copy file vào cache ngay lúc nhận intent.
  - Không nhầm lượt mở từ widget/noti với Open with. A013 lọc chuỗi "Widget" trong data; A045 bỏ qua intent có `OpenFrom.KEY`.
  - Lượt mở này phải `disableAdResumeOnTime()`, không thì app-open resume sẽ chồng lên Splash.
- **QC**:
  - Open with từ Files, Gallery, Drive.
  - App ở các trạng thái: đang kill / đang background / đang foreground ở màn khác.
  - Kiểm tra event `app_open_from`.
  - Với app file: kiểm tra mở đúng file.

## MO-78 — Mọi lượt re-open đều đi lại từ Splash, có ads và tracking

- **Yêu cầu**:
  - Bấm từ noti / widget / shortcut / uninstall / lock screen / Open with: dù app đang ở màn nào cũng reset về Splash, show inter hoặc native full, rồi mới vào tính năng.
  - Log `app_open_from` (open type / open to).
  - Ước lượng: dev 1h, QC 0.5h.
- **Nghiệm thu**:
  - Mọi lối vào đều đi Splash có ads rồi tới đúng màn đích.
  - App đang ở màn sâu: bị reset (back từ màn đích không quay về màn cũ).
  - Không có app-open resume chồng lên Splash.
  - `app_open_from` đúng giá trị, mỗi lượt mở chỉ 1 event.
- **SDK**:
  - `BaseShortcutManager.openIntent` dựng sẵn Intent chuẩn (ACTION_VIEW + NEW_TASK|CLEAR_TASK + extras).
  - Hằng số `Constant.KEY_OPEN_FROM`, `KEY_OPEN_TO`, `OPEN_FROM_*`.
  - `TrackingState.lastScreen` và `BaseAds.screenSkipAdResume` quyết định có show app-open resume hay không.
- **Chuẩn A013**:
  - Mọi lối vào đều dùng Intent tới `MainActivity`, ACTION_VIEW + `FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TASK` + extras:
    - Notification: `NotificationManager.*`.
    - Lock screen: `LockScreenNotiManager`, `LockScreenActivity.openFeature`.
    - Widget: `RecentWidget`, `DeletedWidget` qua `actionStartActivity`.
    - Shortcut: `ShortcutManager`.
  - `MainActivity` có `launchMode="singleTask"`.
  - `MainActivity.onNewIntent` là lưới an toàn:
    - Áp dụng khi intent là ACTION_VIEW có data, hoặc có `KEY_OPEN_FROM`.
    - Gọi `disableAdResumeOnTime()`, rồi start `MainActivity` mới với NEW_TASK|CLEAR_TASK, chép theo action, data và extras.
    - Không dùng `recreate()` vì back stack `rememberNavBackStack` là saveable: recreate sẽ khôi phục màn cũ và bỏ qua Splash.
  - `MainActivity.onCreate`:
    - Gọi `adsManager.resetState()`.
    - Lượt mở mới thì set `TrackingState.lastScreen = ""` (`""` nằm trong `screenSkipAdResume`, nên SDK không show resume đè Splash).
    - `sessionNumber`, `initArgs` và `trackAppOpenFrom` chỉ chạy khi `savedInstanceState == null`.
  - Lock screen dự phòng mất extras bằng `prefs.openFromPending` (`LockScreenActivity.openFeature`).
  - Điều hướng: Splash xử lý Uninstall; `HomeScreen` LaunchedEffect xử lý `OPEN_TO_*` khác rồi reset `openTo`.
  - Giá trị `app_open_from` trong `MainActivity.trackAppOpenFrom`:
    - `shortcut_uninstall`, `widget`, `notification_daily`, `notification_pinned`, `notification_kill`, `notification_reminder`, `notification_winback`.
    - `notification_lock_screen`, hoặc `notification_lock_screen_un_support` khi không có quyền full-screen intent.
  - A013 không log lượt mở từ icon launcher.
- **Remote config**: Không có key riêng. Unit inter splash riêng cho re-open thì xem MO-99:
  - `splash_o`: A014, A045, A47, a033.
  - `inter_o_splash`: a039.
  - `inter_splash_o`: Langofy.
  - `splash_r2` / `splash_r3`: a044.
  - A013 dùng chung luồng splash thường.
- **Placement / tracking**:
  - Event `app_open_from`, param `open_from`.
  - Quy ước giá trị lệch giữa các app:
    - A013, a044: `notification_pinned`.
    - A045, A47: `open_from_notification_pinned`.
    - Mở thường từ icon: a033/a034/a037 log `app_<app_name>`, A045 log `default`.
    - A048, A049: `notification_win_back`, `notification_lockscreen`, và `shortcut` cho cả shortcut tính năng lẫn noti shortcut (noti có thêm `notification_clicked`). Mở thường log `app_<app_name>`.
  - Tên hằng pinned cũng lệch (ghi alias khi grep):
    - `OPEN_FROM_PINNED_NOTIFICATION`: A013, SDK, A028, a031, a034, a036, a041 core/ads.
    - `OPEN_FROM_NOTIFICATION_PINNED`: A014, a016, a044, A045, A47.
    - `OPEN_FROM_NOTIFY_PINNED`: a033, Langofy, a041 core/common.
    - `OPEN_FROM_PINNED_NOTI`: a037, a039.
  - A045 log thêm `notification_clicked` (param `type`). A047, A048, A049 cũng log (`MainActivity.initArgs`).
- **Cách làm**:
  1. **Một helper dựng Intent re-open** (ACTION_VIEW + NEW_TASK|CLEAR_TASK + KEY_OPEN_FROM/KEY_OPEN_TO) cho MỌI lối vào: noti, widget, shortcut, lock screen, FCM.
     - PendingIntent dùng `getActivity` trực tiếp, request code riêng cho từng loại, `FLAG_IMMUTABLE | FLAG_UPDATE_CURRENT`.
     - Đọc `NotificationManager` và `ShortcutManager` ở A013.
  2. **`MainActivity` singleTask**. `onNewIntent` restart task khi có open_from hoặc ACTION_VIEW + data. Đọc `MainActivity.onNewIntent` ở A013.
  3. **`onCreate`**:
     - Reset trạng thái ads splash, xóa `TrackingState.lastScreen`.
     - Chỉ đọc args và log khi `savedInstanceState == null`.
     - Đọc `MainActivity.onCreate` / `initArgs` / `trackAppOpenFrom` ở A013.
  4. **Splash** chạy ads như thường. Xong thì điều hướng theo `openTo`; màn đích dùng xong thì reset `openTo`.
  5. **Tracking**: bảng giá trị `open_from` chốt 1 lần cho app. Nên theo A013 để báo cáo gộp được.
  6. **XML/Fragment, non-SDK**: cùng flags, đích là Activity Splash.
     - a033 `FirstOpenActivity.onNewIntent` gọi `resetState` + `initArgs` + `recreate()`. Chỉ chấp nhận `recreate()` khi back stack KHÔNG saveable.
     - a041 `FirstOpenActivity.onNewIntent` chỉ log tracking, không reset. Muốn reset thì phải dựa hoàn toàn vào CLEAR_TASK.
  - **Ref A047/A048 khác A013**: `onNewIntent` không restart task, chỉ `setIntent` + `initArgs` (A047, A048), tức dựa hẳn vào CLEAR_TASK của mọi intent. A048 bỏ qua intent kéo app về từ Settings (extra `EXTRA_BRING_TO_FRONT`, MO-90). A049 theo A013: restart task khi intent có `OpenFrom.KEY`.
- **Bẫy**:
  - Chỉ NEW_TASK (thiếu CLEAR_TASK) với singleTask: vào `onNewIntent` và đứng nguyên màn cũ. Không Splash, không ad.
  - Android 12+ chặn "notification trampoline" (noti mở Service/Receiver rồi từ đó mới startActivity). Noti phải `getActivity` thẳng.
  - Log trong `onCreate` mà không check `savedInstanceState` thì xoay màn hoặc restore sẽ log đôi.
  - App vừa từ nền lên qua noti: SDK có thể show resume ad đè Splash vì `lastScreen` còn là màn cũ. A013 xử lý bằng cách clear `lastScreen`, và Splash gọi `disableAdResumeOnTime()`.
  - Trùng request code PendingIntent thì extras của noti này đè noti kia.
  - **Mở lại từ Recents sau khi Activity đã finish** (vd Exit gọi `finishAffinity` như A047; task vẫn nằm trong Recents): hệ thống tạo lại Activity bằng intent gốc của task, có thể là intent noti / shortcut đã bấm từ trước, kèm cờ `FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY`. Không lọc thì log lại `app_open_from` cũ và nhảy lại màn đích cũ. A047, A049 `MainActivity.initArgs` bỏ qua extras khi có cờ này; A013 chưa lọc.
  - **Process bị thu hồi khi task còn trong Recents** (hệ thống kill ở nền, tool kill process): mở lại là cold start
    nhưng có `savedInstanceState`, `rememberNavBackStack` khôi phục màn sâu → bỏ qua Splash và ad; màn giữ dữ liệu
    trong bộ nhớ (kết quả) ra trống. A047 để vậy (coi là không phải lượt mở mới). A049 (16/10, user chốt) gọi
    `super.onCreate(null)` khi process mới (cờ static `processStarted`), chạy như mở mới và bỏ extras của intent cũ.
    QC: về nền ở màn sâu → `adb shell run-as <pkg> kill -9 <pid>` → mở từ launcher (`am kill` không giết app vừa ở nền).
  - **Process cũ còn sống**: lượt re-open tạo Activity mới nhưng `AdsManager` (singleton) vẫn giữ unit splash ở `IMPRESSED` / `FAIL`. Hàm nạp kiểu "chỉ nạp khi `NONE`" sẽ bỏ qua: Splash không có ad, đứng tới timeout (không có timeout thì treo hẳn). Reset unit splash ở `onCreate` của lượt mở mới (A013 `AdsManager.resetState`, A047 và A048 `resetSplashAds`, A049 `resetState`).
  - **Home chỉ là trạm trung chuyển** khi lượt mở có đích là tính năng: không bật popup / noti của Home (shortcut noti, xin quyền noti, preload reward). Chụp cờ lúc dựng màn bằng `remember`, vì hàm mở tính năng tiêu `openTo` trước khi Home kịp RESUMED (A047 `MainScreen`, A049 `HomeScreen`, biến `passingThrough`). A013 chưa có cờ này: ref A013 thì đề xuất trong báo cáo, không tự thêm (luật cứng 10).
  - Log mở thường bằng `app_` + `R.string.app_name` viết thường (A048, A049): chuỗi này phải không dịch (A048 khai `translatable="false"`), nếu không giá trị đổi theo ngôn ngữ. Tên có dấu cách thì giá trị cũng có (A049 `app_palm ai`).
- **QC**: Với từng lối vào, thử 3 trạng thái app (đã kill / background ở màn sâu / foreground). Kiểm tra:
  - luôn đi Splash có ads,
  - tới đúng màn,
  - back từ màn đích không về màn cũ,
  - `app_open_from` đúng,
  - không có 2 ad liên tiếp.
  - Ca riêng:
    - Mở từ noti / shortcut, thoát hẳn (Activity bị finish), mở lại từ Recents: như mở thường, không log lại `open_from` cũ, không vào lại màn đích cũ.
    - Mở lại qua noti / shortcut khi process còn sống (app vừa ở nền): Splash vẫn nạp và show ad, không đứng tới timeout.
    - Mở tính năng từ noti / shortcut: không có popup hay noti của Home bật lên giữa đường (app có cờ kiểu `passingThrough`).

## CC-3 — Banner kiểu noti/widget nổi giữa màn hình, giục user quay lại (ứng viên)

- **Yêu cầu**:
  - Ảnh crawl: card bottom-sheet hiện trên lock screen, CTA "Claim Now" / "Explore Now", đúng lúc user mở máy hoặc vào home.
  - Trạng thái sheet: chưa làm (28/05/2026).
- **Chuẩn A013**:
  - Gần nhất là noti lock screen MO-95 (nhóm noti): `ui/screen/lockscreen/LockScreenActivity.kt` (`showWhenLocked` + `turnScreenOn`) và `domain/notification/LockScreenNotiManager.kt`.
  - Kích hoạt bằng full-screen intent theo khung giờ, cộng với `registerScreenWatcher` bắt `ACTION_SCREEN_ON`.
  - RC: `noti_lockscreen_enable`, `noti_lockscreen_slots(_new)`, `noti_lockscreen_hide_second`, `noti_lockscreen_replace`, `full_scr_intent`.
- **Cách làm**:
  - Tái dùng MO-95. Biến thể "vừa vào home" chỉ khác trigger (sau khi mở khóa) và UI dạng card.
  - Chốt với PO trước khi làm.
- **Bẫy**:
  - Bung UI lên khi app đang nền chỉ hợp lệ qua full-screen intent.
    - Full-screen intent chỉ mở Activity khi màn hình tắt hoặc đang khoá. Máy đang dùng (đã mở khoá, đang ở home) thì hệ thống chỉ hiện heads-up notification, nên biến thể "vừa vào home" thực tế chỉ là heads-up.
    - Từ Android 14, `USE_FULL_SCREEN_INTENT` bị Play giới hạn cho app gọi điện/báo thức, user phải bật tay. A013 xin quyền này qua `full_scr_intent` (xem MO-2/MO-90).
  - Overlay đè app khác cần `SYSTEM_ALERT_WINDOW`, rủi ro policy cao. Không làm khi chưa có duyệt.
  - `detect` của CC-3 chỉ thấy có cơ chế lock screen (MO-95), nên nhiều app sẽ báo là đủ. UI card theo ảnh phải QC bằng tay.

## CC-7 — Gợi ý "Open with" khi user tải file PDF (ứng viên)

- **Yêu cầu**:
  - Ảnh crawl: chooser "Open with" khi mở PDF có nhiều entry của cùng đối thủ (All PDF Reader, View PDF, PDF to Word…), tức nhiều alias với tên/icon khác nhau.
  - Ngoài ra: khi user vừa tải PDF thì app chủ động gợi ý mở bằng app.
- **Mẫu a033**:
  - Alias theo loại file: xem MO-77.
  - Phát hiện file mới bằng `feature/newFileObserver/HandleNewFileService.kt`:
    - Foreground service `specialUse` + `RecursiveFileObserver` theo dõi external storage.
    - Có file `.pdf` mới thì bắn noti "You have a new PDF file" (`you_have_a_new_pdf_file`).
    - Bấm noti thì mở thẳng `MuPdfViewerActivity`, tức BỎ QUA Splash, trái MO-78.
- **Cách làm**:
  - Làm MO-77 trước.
  - Nếu PO duyệt phần phát hiện file:
    - Noti phải đi Splash bằng Intent re-open (MO-78) kèm Uri của file.
    - Chỉ chạy khi đã có quyền đọc file.
- **Bẫy**:
  - Nhiều alias có label mạo danh app hoặc thương hiệu khác: rủi ro impersonation / spam.
  - Foreground service `specialUse` phải khai báo với Play.
  - FileObserver trên toàn bộ storage cần all-files access và tốn pin.

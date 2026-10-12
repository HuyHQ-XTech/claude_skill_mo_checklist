# Select / Select Alt

Recipe chuẩn cho nhóm `select`: MO-43..MO-51, DEV-10, CC-4.

- Ref: A013 v1.2.7. `canonical.commit` = f784827 chỉ là mốc **đối chiếu recipe lần cuối**, không phải code để chép.
- Đường dẫn code A013 tính từ `app/src/main/java/com/example/a013_recovery/`. File res/config tính từ gốc repo.
- Khi làm: mở code A013 **bản hiện tại** theo file + symbol ghi ở từng mục. File đã đổi chỗ thì chạy
  `audit.py --item <ID> --app a013` để định vị lại.
- Nhiều cơ chế dùng chung với nhóm Language (2 màn, buffer, click ad): xem `language.md`.

## Tổng quan nhóm

**Luồng ở A013** (mặc định Language → Select → Onboard, theo `language_next` = `select` và
`select_next` = `onboard`)
1. Màn đứng trước Select preload native `select`: `AdsManager.preloadAdsFO` → `loadSelectAds`.
2. **ScrSelect** — `ui/screen/select/SelectScreen.kt`, composable `SelectScreen` (destination
   `AppDestination.ScrFileTypeSelect`, tên tracking `ScrSelect`).
   - Native `select`. Vào màn: preload `select_alt`, thêm `native_preparing` nếu có nút Skip.
   - Chưa chọn: nút Continue mờ; bấm → toast "Please select an item first".
   - Chọn 1 mục → sang ngay ScrSelectAlt và pop ScrSelect. Back bị nuốt.
3. **ScrSelectAlt** — `ui/screen/select/SelectAltScreen.kt`, composable `SelectAltScreen`
   (`AppDestination.ScrFileTypeSelectAlt`).
   - Mục vừa chọn được giữ. Native `select_alt` (có thể buffer 2 unit). Chọn mục mới → đổi native.
   - Vào màn: preload `select_loading` (nếu bật) hoặc ad của màn kế; gọi `resetAdsBeforeSelect`.
   - Continue → ScrSelectLoading (nếu `select_loading_enabled`) hoặc `AdsManager.nextSelect`.
4. **ScrSelectLoading** — `ui/screen/select/SelectLoadingScreen.kt`: native `select_loading`, thanh tiến
   trình giả cho từng mục đã chọn; chạy xong mới cho Done → `nextSelect`.
5. **Skip** (`select_btn_skip`) ở Select / Select Alt → **ScrNativePreparing**
   (`ui/screen/select/NativePreparingScreen.kt` → `ui/base/NativeFullPreparingView.kt`, native full màn
   `native_preparing`, đếm ngược rồi tự qua) → `nextSelect`.

**Class / file chính (A013)**
- `ui/screen/select/view/SelectContent.kt` — composable `SelectContent` (nút Continue, chọn placement, nút
  Skip); enum `SelectType` (các mục + list toàn cục `items` / `itemsLoadFinished`); hàm `selectItem` (chọn 1
  hay nhiều mục theo `new_onboard`); `HorizontalTimerIndicator`.
- `ads/AdsManager.kt` — unit `nativeSelect`, `nativeSelectAlt`, `nativeSelectAltBuffer`,
  `nativeSelectLoading`, `nativePreparing`; `resetNativeSelectAlt`, `resetAdsBeforeSelect`, `nextSelect`,
  `FONavKey.Select`; `resetState` xoá `SelectType.items`.
- `domain/preference/SharedPrefs.kt` — key RC (bảng dưới).
- `ui/base/BufferedNative.kt` (buffer, xem language.md § MO-98), `AppNavigation.kt` (entry các màn Select +
  hook `clickedAnyAds`).

**Quan hệ giữa các mục**
- MO-43 (2 màn) là nền.
- MO-44 (ngón tay / tooltip) và DEV-10 (phải chọn mới được đi) đi chung: Continue lúc chưa chọn → hiện
  tooltip.
- MO-45 / 46 / 47 / 48 là 4 lựa chọn sau khi click ad, MO chọn 1. MO-48 (toast) ở A013 là cơ chế toàn cục,
  chi tiết ở MO-79 (nhóm ads).
- MO-49 (layout), MO-50 (reload): giống MO-40 / MO-41 bên Language.
- MO-51: `select_next`. CC-4 (candidate): Select đặt sau Onboard + chỉ chọn 1.

**Key RC của nhóm (A013, `SharedPrefs`)**

| Key | Kiểu | Default | Ý nghĩa |
|---|---|---|---|
| `select_btn_skip` | Boolean | `true` | Có nút Skip → ScrNativePreparing |
| `select_loading_enabled` | Boolean | `false` | Sau Select Alt đi qua ScrSelectLoading |
| `show_small_button_select` | Boolean | `true` | Kiểu nút Continue (bo góc nhỏ / bo tròn lớn) |
| `buffer_select_alt` | Boolean | `false` | Buffer native Select Alt |
| `min_ad_interval_select_alt` | Long (ms) | `1000` | Khoảng tối thiểu giữa 2 lần đổi ad ở Select Alt |
| `native_full_pre_countdown_time` | Long (giây) | `5` | Đếm ngược ở Preparing trước khi hiện nút X |
| `native_full_pre_auto_pass_time` | Long (giây) | `2` | Hết đếm ngược, chờ thêm N giây rồi tự qua |
| `select_next` | String | `onboard` | Màn kế sau Select |
| `new_onboard` (ngoài nhóm) | Boolean | `true` | `true` = chỉ chọn 1 mục; `false` = chọn nhiều |
| `click_ad_action` | String | `toast` | Toast / noti sau click mọi ad (MO-48 → MO-79) |
| `action_clicked_native_select` / `action_clicked_native_select_alt` (đề xuất, A013 chưa có) | String | `none` | MO-45..47 |

**Placement:** `select`, `select_alt`, `select_loading`, `native_preparing`. Alias `native_select` /
`native_select_alt` (a016, a037, a039; là tên ad unit ở A028, a036). A045 dùng `select`, `select_alt`, và
`preparing` cho màn Preparing.

---

## MO-43 — Tách Select và Select Alt

- **Yêu cầu:** Giống Language. ScrSelect (native `select`, chưa chọn) → chọn 1 mục → **sang ngay**
  ScrSelectAlt (mục đó được chọn sẵn, native `select_alt` là ad mới) → Continue đi tiếp. Ở Select Alt, chọn
  mục mới thì đổi native.
- **Nghiệm thu:** chọn mục ở màn 1 → sang màn 2 ngay; native `select_alt` hiện gần như tức thì; back ở màn 2
  không về màn 1; chọn mục khác ở màn 2 → native đổi.
- **SDK:** Một phần — `NativeBannerGroupView(placement)`; buffer bằng `nameSpace` override (language.md §
  MO-98).
- **Chuẩn A013:**
  - `SelectScreen`: chọn mục → `navigateTo(ScrFileTypeSelectAlt)` và pop `ScrFileTypeSelect`;
    `LaunchedEffect` preload `nativeSelectAlt` (+ `nativePreparing` nếu `select_btn_skip`).
  - `SelectAltScreen`: `rememberBufferedNative` với `nativeSelectAlt` / `nativeSelectAltBuffer`,
    `buffer_select_alt`, `min_ad_interval_select_alt`. Tập `tappedItems` khởi tạo từ `SelectType.items`;
    mục mới → `showNext`. Continue → `ScrSelectLoading` hoặc `nextSelect`. Vào màn gọi
    `resetAdsBeforeSelect` (giải phóng ad của các màn FO trước).
  - `SelectContent` chọn placement: `select` / `select_loading` / `select_alt` (+ `nameSpace` của buffer).
  - Preparing: `NativePreparingScreen` + `NativeFullPreparingView`. Đếm ngược chỉ chạy khi màn resumed; hết
    đếm ngược hiện nút X; thêm N giây thì tự qua. Click ad mà nameSpace `native_preparing` để
    `actionClicked: "next_screen"` → qua màn (SDK `NativeAdClickNextAction`). Back → qua màn. Trong lúc
    hiện, bật `isShowingAds` để app-open resume không chèn lên.
- **Remote config:** các key trong bảng trên. Alias:
  - a027: `select_loading` (`false`), `show_select` (`true` = có màn Select), `select_btn_skip`,
    `buffer_select_alt`, `min_ad_interval_select_alt`.
  - A045: `select_btn_skip` (`true`); `native_full_pre_auto_pass_time` default `15`.
  - a016: `show_small_button_select` (`false`), `use_new_select_screen` (`false`). a034: `is_use_new_select`
    (`true`). a033: `select_screen_text_action` (`true`).
- **Placement / tracking:**
  - `select`, `select_alt`, `select_loading`, `native_preparing`.
  - `screen_show`: `ScrSelect`, `ScrSelectAlt`, `ScrSelectLoading`, `ScrNativePreparing`.
  - `button_click`: `BtnNext` (+ `selected_features`), `BtnSkip`, `BtnBack`, `BtnContinueToApp` (nút X ở
    Preparing).
- **Cách làm:**
  1. 2 destination Select / SelectAlt: top-level như A013, hoặc NavDisplay lồng dùng chung ViewModel như
     A045 `ui/screen/select/SelectNavigation.kt` (tắt transition).
  2. Dùng chung 1 composable UI (A013 `SelectContent`), khác placement.
  3. Màn đứng trước preload `select`; Select preload `select_alt` (+ `native_preparing`).
  4. Select Alt đổi native theo language.md § MO-98 (`BufferedNative`).
  5. Skip / Preparing: đọc `NativePreparingScreen` và `NativeFullPreparingView` ở A013 (bản hiện tại).
  - Không SDK (A028, a036, a041): 2 `NativeAdUnit` riêng, như language.md § MO-35. XML/Fragment: như
    language.md.
- **Bẫy:**
  - `SelectType.items` là list toàn cục → phải xoá trong `resetState` (A013 có làm), nếu không lần FO sau
    còn mục cũ.
  - `resetAdsBeforeSelect` chỉ nên giải phóng ad của các màn mà luồng thực sự đã đi qua.
- **QC:** đi FO tới Select; logcat có `iaa_impression` `select` rồi `select_alt`. Bật `select_loading_enabled`
  → có màn loading. Bấm Skip → Preparing đếm 5 giây, hiện X, rồi tự qua.

## MO-44 — Ngón tay / tooltip hướng dẫn chọn ở Select

- **Yêu cầu:** Ở ScrSelect, hướng dẫn user chọn 1 mục bằng ngón tay (+ tooltip) chỉ vào mục đầu (hoặc mục
  "Popular"):
  - Bấm Continue lúc chưa chọn → hiện ngay (DEV-10).
  - Back → không thoát app, hiện ngay (sheet: "handle backpress: show tooltips").
  - (Tuỳ MO) tự hiện sau N giây không thao tác, như MO-36.
  - Chọn mục → ẩn.
- **Nghiệm thu:** bấm Continue lúc chưa chọn → ngón tay + tooltip ở mục đầu. Back → hiện, không thoát. Chọn
  mục → hint mất.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:** **Chưa có.** `SelectScreen` chỉ nuốt back (`BackHandler`); Continue lúc chưa chọn → toast.
  Nguồn:
  - A045 `ui/screen/select/view/SelectContent.kt` — `SelectHint` (ngón tay `img_click` nhấp nháy +
    `HintTooltip` dùng string `select_hint`). Bật qua `SelectState.showHint` trong `SelectViewModel.onContinue`;
    `onSelect` tắt hint.
  - a037 `ui/screen/select/SelectScreen.kt` — `SelectContent(fingerOn = …)`: ngón tay luôn hiện trên một
    mục cố định.
  - Animation ngón tay dùng lại của Language (language.md § MO-36).
- **Remote config:** không bắt buộc. Nếu MO muốn hint tự hiện theo thời gian: thêm `select_hint_delay_second`
  (đề xuất, Long giây, default `0` = tắt, chỉ hiện khi bấm Continue / back; MO đặt vd `2` để bật).
- **Cách làm:**
  1. State `showHint` của màn Select: bật khi bấm Continue lúc chưa chọn, khi back, và (tuỳ chọn) sau delay;
     tắt khi chọn. Đọc A045 `SelectViewModel` / `SelectContent.SelectHint` để lấy chi tiết.
  2. Đặt hint cạnh mục đầu (hoặc mục được gợi ý), không đè lên native.
  3. Back: `BackHandler` + `PredictiveBackHandler` (A013 `GeneralBackHandler` ở `ui/base/AppBackHandler.kt`).
  - XML: như language.md § MO-36.
- **Bẫy:** tooltip / ngón tay không được nằm trên native (policy). Chuỗi tooltip phải dịch đủ các ngôn ngữ
  (language.md § MO-32).
- **QC:** vào Select, bấm Continue ngay → có hint. Back → có hint, không thoát. Chọn mục → hint mất.

### Cơ chế chung: hành động sau click native ở Select (MO-45 / 46 / 47 / 48)

MO chọn **1 trong 4**: ẩn ad (MO-45), không làm gì (MO-46), đi tiếp (MO-47), toast (MO-48). Cơ chế 2 tầng
giống Language (language.md § "Cơ chế chung"): RC theo màn + `ads_config.actionClicked`. Luật chung FO ở
`inapp-ads.md` § MO-93.

- **A013 chưa có RC theo màn cho Select:** `nativeSelect` / `nativeSelectAlt` không gắn `onClicked`;
  `app/config/ads_config.json` để `select` / `select_alt` `actionClicked: "none"`. Thực tế = "không làm gì" +
  toast / noti toàn cục (`click_ad_action`).
- **Key đề xuất:** `action_clicked_native_select` (ScrSelect) và `action_clicked_native_select_alt`
  (ScrSelectAlt), String, default `none` (giữ hành vi hiện tại của A013). Giá trị: `clear_ads` | `none` |
  `next_screen` | `toast`. Đặt tên theo cặp `action_clicked_native_lang(_alt)` đã có.
- **Cách làm chung:**
  1. Gắn `onClicked` cho `nativeSelect`, `nativeSelectAlt` và unit buffer → bật cờ trong `AdsManager`.
  2. Xử lý trong `LifecycleResumeEffect` của từng màn (như `LanguageAltScreen` ở A013), rồi xoá cờ.
  3. Đặt `actionClicked` của nameSpace `select` / `select_alt` = `none` để SDK không xử lý chồng.
  - App theo kiểu SDK: A045 `ui/screen/select/alternative/SelectAltScreen.kt` (`actionClicked == NEXTSCREEN`
    + `consumeClicked`); a037 `ads/NativeAdClickAction.kt` (`NativeAdClickAction`).

## MO-45 — Click ad ở Select → ẩn ad

- **Yêu cầu:** RC = `clear_ads`: quay lại sau click → native của màn Select / Alt biến mất và không nạp lại
  cho tới khi rời màn.
- **Nghiệm thu:** click ad → quay lại → không còn ad, không có `iaa_request` mới của placement đó.
- **SDK:** Một phần — `actionClicked: "disable"`.
- **Chuẩn A013:** chưa có (xem cơ chế chung).
- **Remote config:** `action_clicked_native_select` / `action_clicked_native_select_alt` = `clear_ads` (đề
  xuất). Chưa app nào có giá trị này cho Select.
- **Cách làm:** ẩn hẳn view + `reset()` unit như language.md § MO-37. Đừng chỉ `reset()`, vì
  `reloadWhenResume: true` sẽ nạp lại ngay.
- **Bẫy:** như language.md § MO-37. Buffer bật thì ẩn cả 2 unit.
- **QC:** như language.md § MO-37, với placement `select` / `select_alt`.

## MO-46 — Click ad ở Select → không làm gì

- **Yêu cầu:** RC = `none`: quay lại sau click, màn giữ nguyên, không popup, không chuyển màn.
- **Nghiệm thu:** click ad → quay lại → vẫn màn đó, ad giữ nguyên.
- **SDK:** Một phần — `actionClicked: "none"`.
- **Chuẩn A013:** đây là hành vi hiện tại (sheet ghi a013 = 1): không xử lý theo màn; `select` / `select_alt`
  để `actionClicked: "none"`. Toast / noti toàn cục vẫn chạy (MO-48).
- **Remote config:** `action_clicked_native_select(_alt)` = `none` (đề xuất, là default).
- **Cách làm:** khi thêm key, để `none` làm nhánh mặc định. Kiểm `actionClicked` của nameSpace không bị thiếu.
- **Bẫy:** thiếu `actionClicked` → SDK mặc định `reload`.
- **QC:** click ad → quay lại → vẫn màn đó, ad giữ nguyên.

## MO-47 — Click ad ở Select → đi tiếp

- **Yêu cầu:** RC = `next_screen`:
  - Click ad ở ScrSelect → quay lại thì sang ScrSelectAlt.
  - Click ad ở ScrSelectAlt → quay lại thì đi tiếp như bấm Continue (màn loading hoặc màn kế).
- **Nghiệm thu:** đúng như trên ở cả 2 màn; không navigate 2 lần.
- **SDK:** Một phần — `ActionClicked.NEXTSCREEN` + `NativeAdClickNextAction`.
- **Chuẩn A013:** chưa có. Nguồn:
  - A045 `ui/screen/select/alternative/SelectAltScreen.kt`: Alt, `actionClicked == NEXTSCREEN` →
    `SelectState.onContinue`.
  - a033 `app/src/main/java/com/apptech/pdfreader/ui/activity/first_open/ui/select/SelectAltScreen.kt`: RC
    `click_ad_select_alt_type`, chỉ có `next_screen`.
  - a037 `ui/screen/select/SelectAltScreen.kt`: `NativeAdClickAction(nativeSelectAlt)` → continue.
- **Remote config:** `action_clicked_native_select(_alt)` = `next_screen` (đề xuất). Alias: a033
  `click_ad_select_alt_type` (String, default `next_screen`); A045 dùng `actionClicked` của nameSpace
  `select_alt` trong `ads_config`.
- **Cách làm:**
  1. ScrSelect `next_screen` → sang Alt **không chọn sẵn** (user vẫn phải chọn, DEV-10), hoặc chọn sẵn mục
     "Popular" nếu design có (A045 `SelectState.popularOption`). Chốt với MO.
  2. ScrSelectAlt `next_screen` → gọi đúng hàm của nút Continue.
  3. Navigate idempotent (`navigateTo` của A013 bỏ qua khi đích trùng class với đỉnh stack).
- **Bẫy:** sang Alt mà chưa có mục nào thì Continue phải bị chặn (A013 hiện không chặn ở Alt, xem DEV-10).
- **QC:** set RC → click ad ở từng màn → quay lại → đúng màn kế.

## MO-48 — Click ad → hiện toast

- **Yêu cầu:** Click ad rồi quay lại app → hiện toast nhắc user. Ở A013 đây là cơ chế **toàn cục** cho mọi
  ad; chi tiết làm ở **`inapp-ads.md` § MO-79**, mục này chỉ liên kết.
- **Nghiệm thu:** `click_ad_action = toast` → click ad ở Select → có toast. `notification` → có noti thay toast.
- **SDK:** Một phần — hook `BaseAds.clickedAnyAds` (SDK gọi khi bất kỳ ad nào bị click); toast / noti làm ở app.
- **Chuẩn A013:** `AppNavigation.kt` — trong `LaunchedEffect`, gán `adsManager.clickedAnyAds`: gọi
  `interSplashClickAction.onClicked()`, rồi theo `click_ad_action`: `notification` →
  `NotificationManager.setKillAppNotification()`, giá trị khác → toast `R.string.don_t_forget_your_lose_files`.
  Sheet ghi a013 / a018 / a027 đang để RC = noti.
- **Remote config:** `click_ad_action` — String, default `toast` (A013); giá trị `toast` | `notification`.
  Alias: default `toast` ở a014, a016, a037, a042; default `notification` ở a027, a034, a044, a045, a047; a036
  `click_ads_type` (`noti`); a033 `show_click_ads_noti` (Boolean).
- **Cách làm:** theo MO-79. Muốn toast **riêng cho Select** (vd "Please select an item first") thì thêm giá trị
  `toast` vào `action_clicked_native_select(_alt)`. Nguồn: a037 `ui/screen/select/SelectScreen.kt`
  (`NativeAdClickAction(nativeSelect)` → toast).
- **Bẫy:** `clickedAnyAds` là 1 biến duy nhất; gán ở nhiều chỗ sẽ đè nhau.
- **QC:** đặt `click_ad_action` lần lượt 2 giá trị → click ad ở Select → kiểm toast / noti.

## MO-49 — Cấu hình layout native Select

- **Yêu cầu:** MO đổi layout native của `select` / `select_alt` / `select_loading` (và layout cho ad Meta)
  bằng remote config.
- **Nghiệm thu:** đổi `layout` trên RC `ads_config` → mở lại → native Select đổi giao diện; key sai → layout
  mặc định, không crash.
- **SDK:** Có — `adunits[].layout` / `layoutMeta`, hoặc `placements[].layout` / `layoutMeta` (language.md §
  MO-40).
- **Chuẩn A013:** `SelectContent` gọi `NativeBannerGroupView` chỉ với placement. `app/config/ads_config.json`:
  `select` / `select_alt` / `select_loading` để `layout` = `native_med_16_9_a`. Sheet ghi a013 = 0 là
  snapshot cũ; code hiện tại đáp ứng qua SDK.
- **Remote config:** `ads_config`. Schema cũ (ảnh tham chiếu trên sheet): `layoutKey` `layout_native_select`
  / `layout_native_select_alt` + `layoutKeyMeta` `…_meta` (A028 `ui/screen/select/view/SelectContent.kt` +
  `AdsManager.layoutNative`). a032 (partner) dùng native collapse riêng, không có config layout.
- **Cách làm:** như language.md § MO-40.
- **Bẫy:** như language.md § MO-40.
- **QC:** đổi `layout` của `select_alt` trên Firebase → `pm clear` → kiểm giao diện.

## MO-50 — Cấu hình reload native Select

- **Yêu cầu:** MO bật/tắt việc nạp ad mới cho native Select khi user quay lại màn, bằng config.
- **Nghiệm thu:** `reloadWhenResume: true` → ra Home rồi quay lại → impression mới; `false` → giữ ad cũ.
- **SDK:** Có — `reloadWhenResume`, `autoReloadOnImpression`, `keepAdWaitLoading`, `actionClicked: "reload"`
  (language.md § MO-41).
- **Chuẩn A013:** `app/config/ads_config.json` — `select` / `select_alt` / `select_loading` có
  `reloadWhenResume: true`. Select Alt còn đổi ad khi chọn mục mới (`BufferedNative.showNext`).
- **Remote config:** `ads_config`. Alias: a033 `reload_select` (Boolean, `true`); schema cũ `forceReload`.
- **Cách làm:** như language.md § MO-41.
- **Bẫy:** như language.md § MO-41.
- **QC:** bật/tắt `reloadWhenResume` → ra Home → quay lại → đếm `iaa_impression placement=select`.

## MO-51 — Remote config màn kế sau Select

- **Yêu cầu:** MO chọn màn sau Select: `onboard` / `select` / `iap` / `home` (theo sheet), không cần release.
- **Nghiệm thu:** mỗi giá trị → đúng màn từ Continue, Loading và Preparing; ad màn đó đã preload; giá trị lạ →
  mặc định.
- **SDK:** Một phần — `ads_config.navigationFlow` + `AdsConfigProvider.getNavigationValue` (language.md §
  MO-42).
- **Chuẩn A013:** `ads/AdsManager.kt` — `nextSelect` = `getNextDestination(FONavKey.Select)`; key `select_next`,
  default `onboard`, fallback `OnBoard`. Dùng ở `SelectAltScreen` (Continue), `SelectLoadingScreen`,
  `NativePreparingScreen`; preload qua `loadNativeNextSelect`.
  - **Lệch:** giống `language_next` — A013 đọc key phẳng, không đọc `navigationFlow`, không có `iap`, không chặn
    trỏ về chính nó.
- **Remote config:** `select_next` — String, default `onboard` (A013). Alias: `navigationFlow.select_next`
  (a028 default `paywall`; a036, a039, a045 default `home`); a016 `navigationFlow.selectNext` (default `iap`).
- **Cách làm:** như language.md § MO-42. Ghi chú: A045 cho Continue vào thẳng tính năng user vừa chọn, chỉ Skip /
  Preparing mới dùng `select_next`. Chốt với MO app mới theo kiểu nào.
- **Bẫy:** ở A013, `select_next = onboard` luôn vào `AppDestination.OnBoard`; khi `new_onboard = true` màn này
  hiện UI onboard mới rồi đi thẳng `ScrOnboardFeature`, bỏ qua `onboard_next`.
- **QC:** set lần lượt `select_next` = `onboard` / `home` / `iap` → Continue, Skip, Loading đều đi đúng màn.

## DEV-10 — Phải chọn 1 mục mới được đi tiếp

- **Yêu cầu:** Ở Select và Select Alt, Continue chỉ đi tiếp khi có ít nhất 1 mục được chọn. Bấm lúc chưa chọn →
  hiện tooltip (+ ngón tay, MO-44), không im lặng.
- **Nghiệm thu:** chưa chọn: nút ở trạng thái mờ, bấm → tooltip, không chuyển màn. Đã chọn → đi tiếp. Ở Alt
  không thể bỏ chọn hết rồi đi tiếp.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:**
  - `SelectContent`: Continue mờ khi `SelectType.items` rỗng; `SelectScreen` bấm Continue → toast
    `please_select_an_item_first` (toast, chưa phải tooltip).
  - Alt: với `new_onboard = true` (chọn 1 mục) luôn có mục được chọn, nên đạt.
  - **Lỗ hổng:** `new_onboard = false` (chọn nhiều): user bỏ chọn hết ở Alt, nút mờ nhưng Continue vẫn đi
    (`SelectAltScreen` không kiểm danh sách rỗng). `SelectLoadingScreen` với 0 mục coi như đã xong.
- **Remote config:** không có.
- **Placement / tracking:** `button_click` `BtnNext` kèm `selected_features` (rỗng khi chưa chọn).
- **Cách làm:**
  1. Một điều kiện "đã chọn" dùng chung cho nút ở mọi màn Select; handler Continue tự kiểm, không dựa vào màu
     nút.
  2. Chưa chọn → bật hint (MO-44) thay vì toast. Nguồn: A045 `ui/screen/select/SelectViewModel.kt` —
     `onContinue` (chưa có `selected` → `showHint`).
  3. Đọc `SelectContent` và `SelectAltScreen` ở A013 (bản hiện tại), thêm kiểm rỗng cho Alt và Loading.
- **Bẫy:** toast dễ bị user bỏ qua và bị toast click-ad toàn cục (MO-48) che. List chọn toàn cục
  (`SelectType.items`) phải xoá khi bắt đầu lại FO.
- **QC:** bấm Continue lúc chưa chọn ở Select → tooltip. Với `new_onboard = false`: chọn rồi bỏ chọn hết ở Alt →
  bấm Continue → không được đi.

## CC-4 — Select sau Onboard, có native, chỉ chọn 1 (candidate)

- **Yêu cầu:** (Mục crawl đối thủ, trạng thái candidate.) User đi hết onboarding → tới Select có native → chỉ
  được chọn đúng 1 loại.
- **Nghiệm thu:** thứ tự Onboard → Select; Select có native; chọn mục khác thì bỏ mục cũ.
- **SDK:** Một phần — thứ tự màn bằng `navigationFlow` / key `*_next`.
- **Chuẩn A013:** chưa ghép được chỉ bằng RC. Thứ tự đổi được qua `language_next` / `onboard_next` /
  `select_next`, nhưng `new_onboard = true` vừa làm Onboard luôn đi `ScrOnboardFeature` (bỏ qua `onboard_next`)
  vừa là cờ khiến Select chỉ chọn 1 (`selectItem`). `new_onboard = false` thì đi được Onboard → Select nhưng
  Select lại chọn nhiều. Muốn đúng CC-4 phải tách cờ chọn 1/nhiều khỏi `new_onboard`.
  - Nguồn: A045 — `onboard_next` mặc định `select`; `SelectState.selected` chỉ giữ 1 mục.
- **Cách làm:** khi MO duyệt: đặt `onboard_next = select`, Select chọn 1 mục, Continue đi theo MO-51. Áp MO-43
  (2 màn), DEV-10, MO-44.
- **QC:** đi hết onboarding → tới Select; chọn A rồi B → chỉ B được chọn; native Select hiện.

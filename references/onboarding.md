# Onboarding (First open) — MO-52…MO-67, MO-92, EXT-NATIVE-POOL

Cách đọc file này:
- **Không có code.** Mỗi mục mô tả cơ chế, quyết định, bẫy, QC, rồi chỉ tới file + symbol. Lúc làm luôn mở
  **A013 bản hiện tại** để đọc chi tiết (`audit.py --item <ID> --app a013` để định vị). Recipe đối chiếu lần
  cuối với A013 `f784827` (nhánh v1.2.7, xtechads 1.8.2).
- Đường dẫn A013 tính từ `app/src/main/java/com/example/a013_recovery/`, riêng `app/config/ads_config.json`
  tính từ gốc repo. App khác: tính từ source root của app đó (`app/src/main/java/<pkg>/`); app multi-module
  ghi rõ module. SDK: `xtechads/…/` = `xTechSDK/xtechads/src/main/java/com/example/xtechads/`.
- Mã app theo `apps.json`: a027 = repo `a27_Recovery_inhouse`, a047 = `A47_Tarot-Reader`, a042 = Langofy,
  a031 = Qibla, a048 = `A048_Live-Translator_SVlink`, a049 = `A049_Palm-AI`. Các ý A048/a049 (và ý a047, A045 thêm
  cùng đợt) đối chiếu 10/2026: A048 nhánh v1.0.4, a049 v1.0.1, a047 v1.0.3, A045 v1.0.9. SDK: xtechads 1.8.7 (bản
  a049 dùng). A048 dùng 1.7.6, a047 1.7.5, A045 1.8.2; các ý SDK thêm đợt này giống nhau ở các bản đó.
- Chuẩn là giao diện mới `OnBoardContentNew` (RC `new_onboard` = `true`, mặc định). `OnBoardContent` (cũ) chỉ
  còn để rollback: OB2 không có native, `beyondViewportPageCount` = 4, last page log `ScrOnboard4` khi không
  có FSN. Hai file dùng chung nhiều mẫu nên `audit.py` có thể trỏ bằng chứng vào `OnBoardContent.kt`. Khi đó
  vẫn đọc `OnBoardContentNew.kt`.

## Tổng quan nhóm

### Trang và slot
- Sheet mô tả 4 trang: **OB1 → OB2 → native full-screen (FSN) → OB4**. Sheet gọi trang FSN là "On board 3
  (or full screen)".
- A013 có đúng 4 slot đó nhưng đánh số khác: OB1 (`onboard_1`) → OB2 (`onboard_2`) → FSN (`fs_onboard`) →
  OB3 (`onboard_3`). **OB3 của A013 = OB4 của sheet**, nên "Native ob4" ứng với `action_clicked_native_ob3`.
- Danh sách trang tính động (`livePages` trong composable `OnBoardContentNew`, bọc `derivedStateOf`):
  - OB1/OB2/OB3 theo `enable_ob1/2/3`.
  - FSN chỉ có khi nameSpace `fs_onboard` bật **và** đang có ad: status khác `NONE`/`FAIL` (`LOADING` vẫn
    tính là có).
  - Không còn trang nào thì bỏ qua onboarding luôn.
- FSN "mượn" ad `native_full_splash` khi splash đã load mà chưa hiện (`borrowFsob`,
  `AdsManager.canBorrowFsob`). Click vào ad mượn cũng tính là click FSN.
- Mọi lối rời onboarding (Get started ở trang cuối, after-click `finish`, vuốt ở trang cuối, X của FSN ở trang
  cuối) đều đi qua `onGetStarted` trong `ui/screen/onboard/OnBoardScreen.kt`:
  1. chặn chạy 2 lần (`getStartedTriggered`);
  2. nếu `enable_inter_ob3` và `enable_ob3` thì show inter `inter_ob_3`, đi tiếp ngay lúc ad hiện, lúc show
     lỗi, hoặc khi không có ad;
  3. `navigateTo(AdsManager.nextOnBoard)` và bỏ `OnBoard` khỏi back stack.
- Mở lại app giữa FO: A013 và A048 chạy lại FO từ bước đầu (A013 hạ `firstOnboard` khi tới Home; A048 xoá ngôn
  ngữ đã chọn trong `MainActivity` khi còn `firstOpen`). a049 (PO yêu cầu, 10/2026) khác:
  - lưu cờ `onboard_completed` lúc rời Onboard (`OnboardViewModel.nextScreen`);
  - mở lại thì Splash bỏ qua Language + Onboard, vào thẳng bước sau Onboard theo `navigationFlow`
    (`domain/firstopen/FirstOpenFlow.kt`, `afterSplash`);
  - chưa xong Onboard thì vẫn xoá ngôn ngữ đã chọn (`MainActivity.attachBaseContext`);
  - app khác chỉ làm khi PO yêu cầu (Q42).
- Nhiều app có **2 trang FSN** (FSN12 giữa OB1–OB2, FSN23 giữa OB2–OB3): a027, a016 (`onboard_2_fsn`),
  a034, a037, a039, a047, a044, a048, a049. A045 cho RC sắp thứ tự slot (field `slots` của JSON `onboard_config`;
  trước v1.0.9 là key `onboard_slots`). Recipe FSN áp cho từng slot như nhau.
- Kiểu A048 (a049 làm theo): 5 trang OB1 → FSN12 (`fs_onboard`) → OB2 → FSN23 (`fs_onboard_2`) → OB3. Danh sách
  trang chốt lúc vào màn theo `enable` của placement, không theo trạng thái ad (A048
  `ui/screen/onboard/view/OnboardContent.kt`, list `pages`; a049 `ui/screen/onboard/OnboardViewModel.kt`, `init`).
  - Được: index trang không nhảy giữa lúc vuốt.
  - Đổi lại: trang FSN vẫn có mặt khi ad lỗi. Phải tự rời trang khi ad `FAIL` (MO-59). Cột 1px kề lúc đó là trang
    trống (MO-65).
  - A013 làm ngược lại: FSN chỉ có mặt khi ad đang nạp hoặc đã có. a047 cũng theo ad, nhưng chốt có/không từng
    trang FSN từ lúc user tới hoặc đi qua nó (`OnboardState`, `pinnedFullScreen`).
- Mỗi trang một placement riêng (`onboard_1/2/3`, `fs_onboard`, `fs_onboard_2`); nameSpace thì dùng chung được.
  - SDK giữ unit theo cặp `placement:nameSpace` (KDoc `NativeBannerGroupView`). Nhiều placement trỏ chung 1
    nameSpace vẫn ra unit riêng, nhưng chung layout, `actionClicked`, `reloadWhenResume` của nameSpace (MO-61).
  - Dùng 1 placement cho nhiều trang là dùng chung 1 unit: 2 trang kề vẽ cùng 1 ad, và không cấu hình reload hay
    after-click riêng từng trang được (a049, 10/2026).

### Preload ads xuyên trang
1. **Màn FO đứng trước onboarding** gọi `AdsManager.preloadAdsFO(OnBoard)` → `loadOnboardAds`: nạp
   `onboard_1`, `onboard_2`, `fs_onboard`. Bỏ `fs_onboard` nếu mượn được `native_full_splash`.
   `onboard_3` **không** được nạp ở bước này. A049 (MO yêu cầu 16/10): `onboard_1` + `fs_onboard` khi bật, không
   nạp `onboard_2` (trang 1 tự nạp trang kề).
2. **Mỗi lần trang hiện tại đổi** (effect theo `pagerState.currentPage` trong `OnBoardContentNew`):
   - gọi `loadAdForKind` cho trang trước, trang hiện tại và trang sau. Mỗi slot chỉ load khi cờ `reload_*`
     của slot bật và placement enable. FSN đang mượn thì không load `fs_onboard`.
   - đang ở OB1/OB2 mà chưa có FSN thì thử load FSN lại (1 lần mỗi lần đổi trang). **Không retry sau slot
     FSN**: `LOADING` đã tính là có ad, trang FSN sẽ bị chèn ngay dưới tay user.
   - từ trang áp chót: nạp inter `inter_ob_3` (`AdsManager.loadInterOb3`);
   - trang cuối: nạp ad màn kế (`loadNativeNextOnboard` → `preloadAdsFO(nextOnBoard)`).
3. `AdGroupUnit.loadAd` của SDK chỉ request khi status là `NONE`/`FAIL`/`IMPRESSED`, hoặc ad `SUCCESS` đã quá
   hạn (~55 phút). Gặp `LOADING`/`TIMEOUT`/`SUCCESS` còn hạn thì bỏ qua. Vì vậy "load" một trang đã hiện ad
   chính là **reload** (thay ad đã có impression).
4. Native chỉ được vẽ ở trang cách trang hiện tại ≤ 1 (`nearActive`). Cộng với `contentPadding` 1px của pager,
   trang kề lộ 1px nên native trang kề có impression. Đây là MO-64..67.
5. Ngoài lệnh nạp của app, chính `NativeBannerGroupView` cũng gọi `loadAd`: lúc vào composition khi màn đang
   `RESUMED`, và mỗi lần `ON_RESUME`. Điều kiện: nameSpace để `reloadWhenResume: true` và unit đang
   `NONE`/`FAIL`/`IMPRESSED` hoặc ad đã hết hạn. Xem SDK
   `xtechads/…/ads/adunit/adgroup/view/NativeBannerGroupViewImpl.kt`, `LifecycleResumeEffect`. Hệ quả:
   - trang được pager dựng sẵn tự request sớm (a049 thấy `fs_onboard_2` request ngay lúc kéo khỏi OB1, 10/2026);
   - native bị gỡ khỏi composition (gate `nearActive`, hoặc trang ra ngoài cửa sổ compose) rồi dựng lại thì ad đã
     impression bị thay, bất kể cờ `reload_*` của app (MO-62).
6. A052 (10/2026) nạp/hiện theo cách khác cho cả Language + Onboard: pool dùng chung, slot thiếu ad thì mượn ad của
   placement khác, mỗi lúc 1 lượt load, nạp sẵn 1 trang. Xem EXT-NATIVE-POOL.

### Remote config của nhóm (A013)

| Key | Kiểu, default | Hành vi |
|---|---|---|
| `new_onboard` | Boolean, `true` | Giao diện mới; đồng thời ép màn sau onboarding = `ScrOnboardFeature` (bỏ qua `onboard_next`) |
| `enable_ob1` / `enable_ob2` / `enable_ob3` | Boolean, `true` | Có trang đó trong pager |
| `reload_ob1` / `reload_ob2` / `reload_ob3` / `reload_fsn` | Boolean, `true` | Load/reload ad của slot khi trang (hoặc trang kề) được chọn (MO-62) |
| `action_clicked_native_ob1` | String, `next_screen` | Sau click native OB1 (MO-57) |
| `action_clicked_native_ob3` | String, `finish` | Sau click native trang cuối (MO-60) |
| `action_clicked_native_fsn` | String, `next_screen` | Sau click native FSN (MO-59) |
| `native_full_time_to_countdown` | Long **ms**, `2000` | FSN: chờ trước khi hiện nút, và cũng là số giây đếm (MO-59) |
| `native_full_auto_pass_time` | Long **ms**, `2000` | FSN: tự qua trang sau khi X hiện (MO-59) |
| `enable_inter_ob3` | Boolean, `true` | Inter `inter_ob_3` khi rời onboarding (chỉ khi `enable_ob3`) |
| `ob_back_btn` | Boolean, `true` | Nút back ở OB1 (MO-52) |
| `ob1_swipe` | Boolean, `true` | Hint vuốt sau 10 s đứng yên ở OB1 (MO-53) |
| `onboard_next` | String, `home` | Màn sau onboarding khi `new_onboard` = `false` (MO-63) |

Ngoài ra `ads_config` (RC JSON, default trong `app/config/ads_config.json`) giữ layout, `actionClicked`,
`reloadWhenResume`, timeout của từng nameSpace. A013 để `onboard_1..3` = `actionClicked: none`,
`reloadWhenResume: true`, timeout 8000; `fs_onboard` = `actionClicked: reload`.

### Hành động sau click native (MO-54..60)
Có 2 tầng chạy **song song** lúc user quay về app (ON_RESUME):

| Tầng | Ai xử lý | Giá trị |
|---|---|---|
| App, RC phẳng `action_clicked_native_<slot>` (A013, a027, a016, a014, a028, a036, a031, a033, a041) | Resume effect của màn onboarding | `next_screen`, `finish`, `clear_ads`, `none` (a041 thêm `reload`) |
| SDK, field `actionClicked` của nameSpace trong `ads_config` | `disable`/`reload`: view `NativeBannerGroupView` tự làm. `next_screen`/`custom`: app đọc | `none`, `tooltip`, `disable`, `reload`, `next_screen`, `custom` |

Cách hiểu 4 lựa chọn của sheet (tập giá trị A013, a044 ghi trong CHANGELOG là "vocab A013"):

| Sheet | Giá trị | Kết quả |
|---|---|---|
| none / "No thing - no action" (MO-55) | `none` (giá trị lạ cũng rơi về đây) | Ở lại trang, không làm gì |
| next page | `next_screen` | Sang trang kế; đang ở trang cuối thì như `finish` |
| has ads / "Hide these ads" (MO-54) | `clear_ads` | `reset()` unit: ad biến mất tới lần reload kế |
| finish screen | `finish` | Rời onboarding như bấm Get started (có `inter_ob_3`) |

"has ads" đang hiểu là `clear_ads`, vì tập giá trị A013 chỉ có 4 giá trị này. Nếu MO muốn "giữ ad và thay ad
mới" thì dùng `actionClicked: reload` ở nameSpace (SDK), hoặc thêm giá trị app `reload` như a041.

## MO-52 — Nút back ở OB1 về màn chọn ngôn ngữ
- **Yêu cầu:** OB1 có nút back. User chọn sai ngôn ngữ (đang test ngôn ngữ) bấm back sẽ quay lại màn Language
  để chọn lại. Back hệ thống ở OB1 làm y như nút.
- **Nghiệm thu:**
  - OB1 có mũi tên back góc trên-trái. OB2, FSN, OB3 không có.
  - Bấm mũi tên, back 3 phím, vuốt cạnh, predictive back (Android 14+) ở OB1 → về màn FO ngay trước onboarding.
    Native màn đó có ad. Chọn lại xong thì vào onboarding đúng ngôn ngữ mới.
  - RC tắt → không có nút. Luồng Splash → Onboarding (không có màn FO trước) → không có nút.
  - Log `button_click` `button_name=BtnBack`, `screen_name=ScrOnboard1`.
- **SDK:** không có API cho phần này; điều hướng là việc của app. App đọc luồng FO từ `navigationFlow` thì dùng
  `AdsConfigProvider.getNavigationValue`.
- **Chuẩn A013:**
  - `ui/screen/onboard/OnBoardScreen.kt`, composable `OnBoardScreen`:
    - `backStep` tính 1 lần (`remember`): bằng `AdsManager.previousOnBoard` nếu `SharedPrefs.obBackBtn`, ngược
      lại null.
    - `onBack` làm 3 việc: nếu đích là Select thì xoá state chọn (`SelectType.items`, `itemsLoadFinished`) →
      `AdsManager.preloadAdsFO(step)` → `navigateTo(step)` và bỏ `OnBoard` khỏi stack.
  - `ads/AdsManager.kt`, `previousOnBoard`: đi lần theo chuỗi `splash_next` → `language_next` → `select_next`
    từ Splash, trả bước có `*_next` trỏ vào onboarding. Bước đó là Splash thì trả null. Không so key đơn lẻ,
    vì bước bị RC bỏ qua vẫn giữ default `select_next = onboard`.
  - `ui/screen/onboard/view/OnboardBack.kt`:
    - `OnboardBackButton`: icon back, click log `BtnBack` gắn `ScrOnboard1`;
    - `OnboardBackHandler`: dùng `GeneralBackHandler` (`ui/base/AppBackHandler.kt`), tức `BackHandler` tới
      API 33 và `PredictiveBackHandler` từ API 34; cũng log `BtnBack`.
  - `ui/screen/onboard/view/OnBoardContentNew.kt`: chỉ trang OB1 nhận `onBack`. Nút là overlay góc trên-trái
    vùng nội dung, phía trên native. `OnboardBackHandler` chỉ compose khi trang hiện tại là OB1.
  - **Lệch sheet:** đích là bước FO ngay trước onboarding, không cố định Language. Chuỗi mặc định của A013 là
    `language → select → onboard`, nên back ra **Select** (`ScrFileTypeSelect`). Chỉ khi
    `language_next = onboard` thì back ra Language.
- **Remote config:** `ob_back_btn` (Boolean, `true`) bật nút và back ở OB1. Alias:
  - `action_click_back_ob` (a016, **Long**): 1 = popup thoát, 2 = đứng yên + hint, 3 = lùi 1 trang, ở OB1 thì về
    Language. Chỉ áp cho back hệ thống, không có nút.
  - `action_click_back_device_ob` (a047, String trong JSON `onboard_config`): `keep_state` hoặc `reload` (lùi
    trang + reload ad trang đó; ở OB1 thì về Language).
  - `is_show_button_back` + `position_show_button_back` (a044): nút back ở trang chọn được; đích tìm bằng cách
    tra ngược `navigationFlow`.
- **Placement / tracking:** `button_click` `BtnBack` / `ScrOnboard1`. Native màn đích được nạp lại
  (`iaa_request` của `language` hoặc `select`).
- **Cách làm:**
  1. Thêm RC `ob_back_btn` vào `SharedPrefs` (app đã có key back khác thì dùng key đó).
  2. Trong `AdsManager` thêm hàm tìm màn FO đứng trước onboarding. Dùng **đúng nguồn luồng FO app đang đọc**
     (key phẳng `*_next` hay `navigationFlow`). Đọc `AdsManager.previousOnBoard` ở A013 (bản hiện tại). App
     dùng `navigationFlow` thì xem a044 `ui/screen/onboard/OnboardViewModel.kt` (`prevScreen`,
     `backToPrevScreen`).
  3. Ở Screen onboarding: tính đích 1 lần. Hành động back = reset state màn đích → preload ad màn đích →
     navigate tới đích rồi bỏ Onboard khỏi stack. Đọc `OnBoardScreen` (A013).
  4. Ở content: nút chỉ có ở OB1; BackHandler (kể cả predictive back) chỉ compose khi OB1 là trang hiện tại.
     Đọc `OnboardBack.kt` và chỗ dùng trong `OnBoardContentNew`.
  5. Muốn đúng chữ sheet (luôn về Language): cho đích = Language khi Language có trong luồng. Language bị tắt
     thì ẩn nút, hoặc quay về bước trước (a016 kiểm `enableLanguageScreen` trước khi navigate).
  - XML/Fragment (a031): back qua `onBackPressedDispatcher` (hoặc `BackHandler` trong `ComposeView`), navigate
    bằng NavController tới Language với popUpTo màn onboarding.
  - Không dùng SDK (a028, a036, a041): cùng logic, chỉ đổi hàm preload ad màn đích.
- **Bẫy:**
  - Lúc ở onboarding, back stack chỉ còn `[OnBoard]` (màn FO nào cũng tự pop khi đi tiếp). Phải **navigate**;
    pop là thoát app hoặc crash stack rỗng.
  - Preload ad màn đích trước khi navigate. Đừng trông vào `reloadWhenResume`, vì `ads_config` trên server có
    thể tắt nó.
  - Reset đủ state màn đích. Select của A013 có 2 list `SelectType`, và `itemsLoadFinished` là list: chạy
    SelectLoading lần 2 sẽ bị nhân đôi phần tử, nút Done kẹt.
  - Đọc RC 1 lần. RC fetch xong giữa chừng không được làm nút tự hiện hay tự mất.
  - Ở các trang ≠ OB1, A013 không bắt back: `NavDisplay.onBack` finish activity (thoát app). Muốn khác thì xem
    MO-53.
  - Không đổi kiểu key đã phát hành: a016 dùng Long, a047 dùng String.
- **QC:**
  - Cài mới, đi FO tới OB1: thấy mũi tên. Bấm → về đúng màn trước theo luồng RC, native màn đó có ad. Chọn
    ngôn ngữ khác → onboarding hiển thị đúng ngôn ngữ mới.
  - Lặp lại với back 3 phím, vuốt cạnh, predictive back.
  - `ob_back_btn=false`: không có mũi tên; back ở OB1 thoát app (hành vi cũ).
  - `language_next=onboard`: back ra Language. `splash_next=onboard`: không có nút.
  - DebugView/logcat: `button_click` `BtnBack` `ScrOnboard1`.

## MO-53 — Hint vuốt/Next khi user đứng lâu ở OB1
- **Yêu cầu:**
  - User đứng ở OB1 quá lâu thì hiện hướng dẫn vuốt hoặc bấm Next.
  - Dòng "Has handle backpress: show tooltips" là khuôn chung với Language và Select: back ở màn FO thì hiện
    hướng dẫn thay vì thoát app.
- **Nghiệm thu:**
  - Đứng yên ở OB1 10 giây (không chạm, app ở foreground) → hiện animation bàn tay vuốt. Animation phủ vùng
    nội dung phía trên native, **không đè native**.
  - Chạm/vuốt → hint tắt. Đứng yên lại 10 giây → hiện lại.
  - OB2 trở đi không có hint. RTL: tay vuốt ngược chiều.
  - RC tắt → không bao giờ hiện.
- **SDK:** không có.
- **Chuẩn A013:**
  - `ui/screen/onboard/view/SwipeHint.kt`:
    - `rememberSwipeHintVisible(enabled, pagerState, isHintPage)` theo dõi điều kiện "đang ở trang hint và
      pager không cuộn". Mỗi lần điều kiện đổi thì ẩn hint. Nếu đang rảnh thì chờ `HINT_IDLE_MS` (10 s) trong
      lúc lifecycle `RESUMED` (`repeatOnLifecycle`) rồi mới hiện. Drag hoặc xuống nền thì đếm lại từ đầu.
    - `SwipeHint`: Lottie `raw/ani_swipe_blue`, `ContentScale.Crop` + căn `TopCenter`, lật ngang khi RTL. Không
      bắt touch.
  - `OnBoardContentNew`: truyền `SharedPrefs.ob1Swipe` vào `rememberSwipeHintVisible`; chỉ trang OB1 nhận
    `showSwipeHint`. Trong `OnboardPage`, hint vẽ `matchParentSize` trên vùng nội dung; native nằm ngoài vùng
    đó.
  - Không log event cho hint (quyết định ghi trong `CLAUDE.md` của A013).
  - **Thiếu phần backpress:** back ở OB2/FSN/OB3 thoát app, back không hiện tooltip.
- **Remote config:** `ob1_swipe` (Boolean, `true`). Thời gian chờ 10 s đang hard-code (`HINT_IDLE_MS`), không có
  RC. Đừng nhầm với `swipe_guide`: key này chỉ chỉnh vị trí lottie vuốt ở OB2 của giao diện cũ. Alias cho phần
  backpress: `action_click_back_ob` = 2 (a016: back → đứng yên; OB1 hiện hint bấm, trang khác hiện hint vuốt).
- **Placement / tracking:** không có event.
- **Cách làm:**
  1. RC `ob1_swipe`.
  2. State hint là một hàm `remember…` nhận pager + điều kiện trang hint. Đọc `rememberSwipeHintVisible` (A013).
  3. Overlay Lottie nằm trong vùng nội dung của OB1: không phủ native, không bắt touch, lật khi RTL. Đọc
     `SwipeHint` và `OnboardPage` (A013).
  4. (Đề xuất, khi MO đòi phần backpress) Thêm BackHandler cho các trang onboarding không có back của MO-52:
     back → hiện hint ngay (bỏ chờ 10 s) thay vì thoát. Riêng trang FSN có thể cho lùi trang. Tham khảo a016
     `ui/screen/onboard/view/OnBoardContent.kt` (`BackCustom`, `ObBackHint`, RC `action_click_back_ob`).
  - XML: `lifecycleScope` + `repeatOnLifecycle(RESUMED)` + `delay`; ẩn hint khi `ViewPager2` chuyển sang
    `SCROLL_STATE_DRAGGING`; dùng `LottieAnimationView` (xem `stack-adapt.md` §4).
- **Bẫy:**
  - Hint phủ native (AdChoices/CTA) dễ gây click nhầm, sai chính sách. Giữ hint trên vùng nội dung.
  - Chỉ đếm giờ khi `RESUMED`. Đếm cả lúc ở nền thì user quay lại từ ad là thấy hint ngay.
  - Ẩn ngay khi bắt đầu drag (`isScrollInProgress`), đừng đợi đổi trang.
  - File Lottie của A013 nặng (720×1600, 94 frame PNG, ~8.5 MB trong cache sau lần chạy đầu): để ý RAM máy yếu.
- **QC:**
  - Đứng ở OB1 không chạm 10 s → có hint. Chạm → mất. Thêm 10 s → hiện lại.
  - Đếm được 8 s thì bấm Home, mở lại: phải đủ 10 s nữa mới hiện.
  - OB2 trở đi không có hint. `ob1_swipe=false` → không có hint.
  - Ngôn ngữ RTL (vd `ar`): tay vuốt trái → phải.
  - Nếu làm bước 4: back ở OB2 → hint hiện, không thoát app.

## MO-54 — Sau click ads: ẩn ad đã click
- **Yêu cầu:** một lựa chọn hành động sau click native onboarding: user quay về app thì ad vừa click biến mất.
- **Nghiệm thu:** đặt `action_clicked_native_<slot>` = `clear_ads` → click ad → quay về:
  - vẫn đứng ở trang đó, ô native trống (không shimmer, không crash);
  - lướt sang trang khác rồi quay lại: có ad mới (nếu `reload_<slot>` bật).
- **SDK:** một phần. NameSpace `actionClicked: "disable"` (ads_config) ẩn ad sau click và chặn auto-reload trong
  view đó. `clear_ads` là tầng app.
- **Chuẩn A013:** nhánh `clear_ads` trong after-click effect của `OnBoardContentNew` gọi `AdsManager.clearAdsOb1`,
  `clearAdsOb3` hoặc `clearAdsFsn`. Các hàm này là `AdGroupUnit.reset()`; riêng FSN reset cả
  `native_full_splash`. `reset()` đưa status về `NONE`, nên `NativeBannerGroupView` không vẽ gì nữa.
- **Remote config:** `action_clicked_native_ob1|ob2|ob3|fsn` = `clear_ads`. Ở tầng SDK: nameSpace
  `actionClicked` = `disable`.
- **Placement / tracking:** SDK `iaa_click` (theo `ad_placement`). Lần nạp sau có `iaa_request` mới.
- **Cách làm:** làm theo MO-56. Thêm `clearAds<Slot>()` = reset unit của slot; với FSN thì reset cả unit đang
  được mượn.
- **Bẫy:**
  - `clear_ads` chỉ ẩn tới lần reload kế: đổi trang thì `loadAdForKind` nạp lại (khi `reload_*` bật). Muốn ẩn
    hẳn trong màn → `actionClicked: "disable"`.
  - Ở FSN: reset làm `hasFsob` = false, nên **trang FSN rời pager** ngay dưới tay user (user đang ở FSN bị nhảy
    sang OB kế, không có animation). Với FSN nên dùng `next_screen`.
- **QC:** đặt `clear_ads` cho ob1 → click native OB1 → quay về: ô ad trống. Vuốt sang OB2 rồi về OB1 → có ad
  mới. Lặp lại với FSN, ghi lại hành vi nhảy trang.

## MO-55 — Sau click ads: không làm gì
- **Yêu cầu:** một lựa chọn "không làm gì" sau click native onboarding.
- **Nghiệm thu:** giá trị `none` → click ad → quay về: vẫn ở trang đó, không navigate. Ad giữ nguyên, trừ khi
  nameSpace để `actionClicked: reload`.
- **SDK:** nameSpace `actionClicked: "none"`.
- **Chuẩn A013:** chỉ slot trang cuối (`action_clicked_native_ob3`) có nhánh `none` tường minh. Slot ob1 và fsn
  không có nhánh `none`, nhưng giá trị ngoài tập xử lý rơi khỏi `when` nên kết quả cũng là không làm gì.
- **Remote config:** `action_clicked_native_<slot>` = `none`.
- **Placement / tracking:** chỉ có `iaa_click` của SDK.
- **Cách làm:** theo MO-56. Thêm nhánh `none` tường minh cho mọi slot để QC tra được. Vẫn phải hạ cờ click.
- **Bẫy:**
  - 2 tầng chạy độc lập. `fs_onboard` của A013 để `actionClicked: reload`, nên đặt `none` ở tầng app thì ad FSN
    vẫn bị thay khi quay về. Muốn "giữ nguyên ad" phải để nameSpace `actionClicked: none`.
  - Không hạ cờ thì lần resume sau (vd tắt màn hình rồi mở) xử lý lại click cũ.
- **QC:** đặt `none` cho từng slot → click → quay về: không chuyển trang. Với FSN, kiểm thêm `actionClicked` của
  nameSpace `fs_onboard` trong `ads_config` đang chạy.

## MO-56 — Cơ chế next action sau click native onboarding
- **Yêu cầu:** mỗi native trong onboarding có RC chọn hành động khi user click ad rồi quay về app. Chi tiết từng
  slot ở MO-57..60; tập giá trị ở Tổng quan nhóm.
- **Nghiệm thu:**
  - Đổi RC của slot nào thì hành vi slot đó đổi theo.
  - Hành động chạy **lúc quay về app**, không chạy lúc click.
  - Không bao giờ navigate 2 lần, kể cả khi user bấm Get started sát lúc quay về.
  - Default đúng bảng: ob1, ob2, fsn = `next_screen`; trang cuối = `finish`.
- **SDK:** một phần.
  - Có sẵn: callback `AdGroupUnit.onClicked`, cờ `isClicked`, enum `ActionClicked` của nameSpace.
  - `NativeBannerGroupView` tự xử lý `disable`/`reload` lúc resume.
  - Helper `NativeAdClickNextAction` (`xtechads/…/ads/adunit/adgroup/view/`) gọi lại khi `actionClicked` bằng
    giá trị truyền vào.
  - Phần đọc RC theo slot là của app.
- **Chuẩn A013:**
  - `ads/AdsManager.kt`:
    - mỗi unit onboarding gắn `onClicked` để bật cờ Compose state của app: `clickedNativeOb1`,
      `clickedNativeOb2`, `clickedNativeOb3`, `clickedNativeFsn`;
    - `onClicked` của `nativeFullSplash` cũng bật `clickedNativeFsn` khi ad chưa hiện ở splash (lúc đó
      onboarding đang mượn nó);
    - `resetState` hạ các cờ, nhưng **thiếu `clickedNativeOb2`**.
  - `OnBoardContentNew`: một `LifecycleResumeEffect` duyệt các cờ. Cờ nào đang bật thì đọc RC của slot, làm
    hành động, rồi hạ cờ:
    - `next_screen` → `advanceOne()` (trang cuối thì gọi đường Get started);
    - `finish` → `onGetStartedClick` (đường chung, có `inter_ob_3` và chặn 2 lần);
    - `clear_ads` → `clearAds<Slot>()`;
    - `none` hoặc giá trị lạ → không làm gì.
  - Tầng SDK chạy song song theo `app/config/ads_config.json`: `onboard_1..3` = `none`, `fs_onboard` = `reload`
    (FSN tự nạp ad mới khi quay về).
- **Remote config:**
  - Bảng key + default ở Tổng quan nhóm.
  - Alias:
    - `action_clicked_new_native_ob1/ob2/ob3/fsn` (a014, giao diện mới);
    - `action_clicked_native_ob4` (a033, a036, a041: trang cuối);
    - `action_clicked_native_fsn2` (a016, a036), `action_clicked_native_fsob12` (a027),
      `action_clicked_native_fsob1` (a041): slot FSN thứ hai;
    - field `actionClicked` của nameSpace (a034, a037, a039, a047: app chỉ xử lý `next_screen`).
- **Placement / tracking:** SDK bắn `iaa_click` (`ad_placement`). Sau `next_screen` có `screen_show` của trang
  mới.
- **Cách làm:**
  1. `AdsManager`: gắn `onClicked` của từng unit onboarding, kể cả unit mượn, vào một cờ riêng. Thêm
     `clearAds<Slot>()`. Hạ cờ trong hàm reset state FO. Đọc phần native onboarding của `AdsManager` (A013).
  2. Content: một resume effect xử lý mọi cờ. Mọi lối rời onboarding dùng chung 1 hàm finish có chặn 2 lần.
     Đọc after-click effect và `advanceOne` trong `OnBoardContentNew`, `onGetStarted` trong `OnBoardScreen`.
  3. Rà `actionClicked` của các nameSpace onboarding trong `ads_config` để 2 tầng không đá nhau.
  4. App đã theo kiểu SDK (a034, a037, a039, a047 khai `actionClicked` trong ads_config; app có helper
     `NativeAdClickAction` hoặc `consumeAppClickAction`) thì giữ kiểu đó. Lựa chọn `finish` ở trang cuối được
     làm thành `next_screen` với callback = rời onboarding (a039).
  - XML/Fragment: đọc cờ trong `onResume()` của fragment/activity.
  - Không dùng SDK (a028, a036, a041): AdsManager tự viết của các app này đã có cờ `clickedNative*`; làm y hệt.
- **Bẫy:**
  - **Đừng "ăn" `AdGroupUnit.isClicked`** ở app khi nameSpace là `reload` hoặc `disable`: view của SDK cần cờ đó
    lúc resume. A013 an toàn vì dùng cờ riêng qua `onClicked`. `NativeAdClickNextAction` của SDK xoá
    `isClicked` với mọi action nên làm hỏng `reload`/`disable`. a047 viết `consumeAppClickAction`
    (`ads/AdGroupUnitExt.kt`) chỉ xoá cờ khi action là `next_screen`/`custom`. a027 đang dính bẫy này: app xoá
    `isClicked` của unit onboarding trong khi `ads_config` để `reload`.
  - Hạ đúng cờ: a014 `ui/screen/onboarding/content/OnBoardingContent.kt` hạ nhầm `clickedNativeOb1` trong
    nhánh ob2, nên click ob2 bị xử lý lại ở lần resume sau.
  - `onClicked` là `var` trên unit cache dùng chung toàn app. Gán ở 1 chỗ (AdsManager), hoặc wrap và giữ
    callback cũ như `NativeAdClickAction` của a037/a039.
  - Chạy lúc resume, sau khi Activity của ad đã đóng; đừng navigate lúc Activity ad còn ở trên.
  - Liên quan **MO-93** (nhóm ads: "từ ads trở về sẽ auto next screen"). Onboarding là một trường hợp của mục
    đó, đừng xử lý 2 lần qua hook `clickedAnyAds` toàn app.
  - Toast/noti sau click (`click_ad_action`, nhóm ads) chạy song song, không ảnh hưởng.
- **QC:** ma trận slot × giá trị (`next_screen`, `finish`, `clear_ads`, `none`):
  - mỗi lượt: `pm clear` → mở app 2 lần cho RC áp → click native của slot → quay về;
  - `finish` khi `enable_inter_ob3` bật: inter `inter_ob_3` hiện rồi mới sang màn kế, chỉ 1 lần;
  - click ad rồi bấm Get started ngay khi quay về: chỉ navigate 1 lần.

## MO-57 — Native OB1: none / next page / has ads / finish
- **Yêu cầu:** native OB1 có đủ 4 lựa chọn sau click (bảng ở Tổng quan nhóm).
- **Nghiệm thu:**
  - `next_screen` → sang trang kế đang có (OB2, hoặc FSN/OB3 nếu OB2 tắt);
  - `finish` → rời onboarding tới màn kế (có `inter_ob_3` nếu bật);
  - `clear_ads` → như MO-54; `none` → như MO-55;
  - default là `next_screen`.
- **SDK:** như MO-56.
- **Chuẩn A013:** đã đủ. `action_clicked_native_ob1` default `next_screen`, có nhánh `next_screen`, `finish`,
  `clear_ads`; `none` là rơi khỏi `when`. Cờ `clickedNativeOb1`.
- **Remote config:** `action_clicked_native_ob1` (String, `next_screen`). Alias: `action_clicked_new_native_ob1`
  (a014); nameSpace `actionClicked` của `onboard_1`/`native_ob1` (a034, a037, a039, a047). a041 để default
  `reload`.
- **Placement / tracking:** `onboard_1`. Alias: `native_ob1` (a016, a036, a037, a039, a041, a042),
  `native_ob_1` (a028).
- **Cách làm:** theo MO-56 cho slot ob1.
- **Bẫy:** `next_screen` lấy trang hiện tại **lúc resume**. OB1 là trang duy nhất (các trang khác tắt, không có
  FSN) thì `next_screen` = `finish`.
- **QC:** chạy đủ 4 giá trị theo QC của MO-56, slot ob1.

## MO-58 — Native OB2: none / next page / has ads / finish
- **Yêu cầu:** native OB2 có đủ 4 lựa chọn sau click. Ghi chú sheet: nhiều app chưa có RC cho slot này (a013,
  a027, a037…).
- **Nghiệm thu:** như MO-57 nhưng cho slot ob2; default `next_screen`.
- **SDK:** như MO-56.
- **Chuẩn A013:** **chưa có.** `AdsManager` có cờ `clickedNativeOb2` (bật qua `onClicked` của `onboard_2`),
  nhưng `OnBoardContentNew` không đọc cờ này, không có RC, không có `clearAdsOb2`, và `resetState` không hạ cờ.
  Click native OB2 xong quay về thì không có gì xảy ra.
- **Remote config:** thêm `action_clicked_native_ob2` (String, default `next_screen`; giá trị như ob1). Đã có ở
  a027, a016, a014, a028, a036. Alias: `action_clicked_new_native_ob2` (a014).
- **Placement / tracking:** `onboard_2` (alias `native_ob2`).
- **Cách làm:**
  1. RC `action_clicked_native_ob2`.
  2. Thêm `clearAdsOb2()` trong `AdsManager`; hạ `clickedNativeOb2` trong `resetState`.
  3. Thêm nhánh ob2 vào after-click effect, cùng khuôn với ob1. Tham khảo a016
     `ui/screen/onboard/view/OnBoardContent.kt`, a028 `ui/screen/onboard/content/OnboardContent.kt`, a027
     `ui/screen/onboard/view/OnBoardContentNew.kt`. Riêng a027 đọc rồi xoá `nativeOb2.isClicked` trong khi
     nameSpace onboarding của nó để `actionClicked: reload`, tức dính bẫy ở MO-56. Khi port, dùng cờ riêng như
     A013.
  - A013 giao diện cũ (`OnBoardContent`): OB2 không có native, nên mục này chỉ áp cho giao diện mới.
- **Bẫy:** đã thêm handler thì phải hạ đúng `clickedNativeOb2`. Nhánh `next_screen` ở OB2 khi FSN không có ad sẽ
  sang thẳng OB3.
- **QC:** như MO-57 cho slot ob2. Thêm 1 lượt kiểm thiếu RC (chưa publish key) → default `next_screen`.

## MO-59 — Native full-screen: hành động sau click + RC bật/tắt nút thoát
- **Yêu cầu:**
  1. Native full-screen (FSN) có đủ 4 lựa chọn sau click.
  2. Có RC bật/tắt nút thoát (pill "Continue to app"/X) trên trang FSN.
- **Nghiệm thu:**
  - `action_clicked_native_fsn` đổi được hành vi, default `next_screen`.
  - Nút bật: sau thời gian chờ thì pill hiện kèm số giây đếm; hết giờ thì có X, bấm được; rồi tự qua trang.
  - Nút tắt: không vẽ pill/X; user vẫn vuốt qua được; không kẹt.
  - Click ad đang mượn (`native_full_splash`) cũng theo RC `fsn`.
- **SDK:** một phần. After-click theo MO-56. Trang FSN và nút thoát là app.
- **Chuẩn A013:**
  - After-click: `action_clicked_native_fsn` default `next_screen` (`next_screen`, `finish`, `clear_ads`), cờ
    `clickedNativeFsn`.
  - Composable private `FsnPage` trong `OnBoardContentNew`:
    - native full màn, placement `fs_onboard` hoặc `native_full_splash` khi mượn; layout fallback
      `R.layout.native_full_t2c`;
    - pill nằm góc trên-phải, dưới status bar;
    - timer chạy khi trang thành trang hiện tại: chờ `native_full_time_to_countdown` ms → hiện pill "Continue to
      app" với số giây = làm tròn lên của **cùng giá trị đó** / 1000 → đếm lùi mỗi giây → hết giờ thì đổi sang X
      và pill bấm được (log `BtnContinueToApp`) → chờ thêm `native_full_auto_pass_time` ms → tự `advanceOne()`;
    - rời trang thì timer dừng. Quay lại khi trang còn compose thì đếm tiếp phần còn lại.
  - **Chưa có RC tắt nút**, tức thiếu ý 2.
- **Remote config:**
  - `action_clicked_native_fsn` (String, `next_screen`). Alias: `action_clicked_native_fsn2` (a016, a036),
    `action_clicked_native_fsob12` (a027), `action_clicked_native_fsob1` (a041),
    `action_clicked_new_native_fsn` (a014).
    - A048, a049 không có RC này và app không đọc click: nameSpace `fs_onboard`, `fs_onboard_2` để
      `actionClicked: reload` (SDK thay ad khi user quay về).
  - `native_full_time_to_countdown` (Long ms, `2000`). Alias (đều tính **giây**):
    - `time_close_fsn_ob` (a039, 5);
    - `time_close_fsob12` (a027, 2, chỉ FSN12; FSN23 hiện X ngay);
    - `onboard_2fsn_close_countdown` (a016, 5, đếm ngầm, chỉ khi `onboard_2_fsn`);
    - `show_close_native_fs_countdown` (a034 5, a037 3);
    - `time_show_button_X_fsn` (a047, a044, a049, 5, đếm ngầm; a049 đặt 0 thì X hiện ngay khi ad hiện);
    - field `fsn_close_second` của JSON `onboard_config` (A045 từ v1.0.9, 5, đếm ngầm; trước đó A045 dùng
      `time_show_button_X_fsn`);
    - `time_close_FS_onboard` (a014, 0);
    - field `closeCountdown` của native position (a036, config tự viết).
    - Cùng tên, khác nghĩa: A048 dùng đúng `native_full_time_to_countdown` (ms, `2000`) nhưng chỉ 1 lần (xem Bẫy).
  - `native_full_auto_pass_time` (Long ms, `2000`). Alias: `fsn_auto_next_onboard` (a014 5 s; a039 0 = tắt).
    a014/a039 đếm từ lúc vào trang, không đợi X hiện.
  - **Key mới đề xuất** `native_full_close_btn` (Boolean, `true` = có nút). Chưa app nào có; MO chốt tên.
  - Không phải alias: `native_full_pre_countdown_time` / `native_full_pre_auto_pass_time` là của màn Preparing
    (nhóm select).
- **Placement / tracking:** `fs_onboard` (+ `native_full_splash` khi mượn). Alias:
  - `native_fsob` (a016, a028, a036, a037, a041, a042);
  - `native_fsob_before_2` (a016), `native_fs_ob1` (a037, a036), `native_fsob_1` (a041);
  - `native_fob12`/`native_fob23` (a039), `fs_onboard_12` (a027), `fs_onboard_12`/`fs_onboard_23` (a047),
    `fs_onboard_2` (a045, a044, a048, a049).
  Event: `screen_show` `ScrNativeFullScreen`, `button_click` `BtnContinueToApp`.
  - App 2 FSN: `ScrNativeFullScreen1` / `ScrNativeFullScreen2` (a034, a037, a039, a047, A048, a049).
  - Nút đóng ở app khác: a047 `BtnCloseFullScreenAd`, A048 `BtnMaybeLater`, a039 và a049 `BtnClose`, A045
    `BtnCloseOnboardAd`.
- **Cách làm:**
  1. After-click: theo MO-56, slot fsn. Gắn cả unit mượn.
  2. RC tắt nút: đọc 1 lần khi vào trang. Tắt thì không vẽ pill/X nhưng timer auto-pass vẫn chạy, để user không
     kẹt và vẫn vuốt được. Đọc `FsnPage` (A013) để đặt điều kiện vẽ pill.
  3. MO muốn tắt luôn auto-pass thì phải chốt quy ước trước. Ở a039, `fsn_auto_next_onboard` ≤ 0 nghĩa là tắt.
     Ở A013, `native_full_auto_pass_time = 0` nghĩa là qua **ngay** khi X hiện. Hỏi MO.
  - **Ref a047 khác A013** (`ui/screen/onboard/OnboardScreen.kt`, effect theo `statusFlow` của unit FSN):
    - X đếm ngầm `time_show_button_X_fsn` từ lúc ad `SUCCESS`/`IMPRESSED` và FSN là trang hiện tại.
    - Rời trang thì X ẩn; quay lại thì đếm lại từ đầu. Ad `FAIL` thì hiện X ngay.
    - Không auto-pass.
  - **Ref A048 khác A013** (`ui/screen/onboard/view/OnboardAdContent.kt`):
    - Không có pill góc trên. Trang thành trang hiện tại là đếm ngay: vòng tròn + "Can skip in Xs" ở đáy; hết giờ
      đổi thành nút chữ "Maybe Later" cùng chỗ. Không auto-pass.
    - Tiến độ đếm lưu bằng `rememberSaveable(placement)`: rời trang rồi quay lại thì đếm tiếp.
    - Ad `FAIL` lúc đang đứng ở trang thì luôn sang trang sau.
    - Layout riêng của app (MO-61). AdChoices để `top_right`; nút nằm ở đáy nên không đè.
  - **App đã làm: a049** (`ui/screen/onboard/content/OnboardContent.kt`, `FullScreenAdPage`), theo A048 nhưng:
    - X tròn góc trên-phải, không hiện số. Đếm ngầm `time_show_button_X_fsn` giây, chỉ chạy khi ad đã
      `SUCCESS`/`IMPRESSED` **và** pager đã dừng ở FSN. Rời trang thì dừng, quay lại đếm tiếp; X đã hiện thì giữ.
    - Bấm X sang trang sau. Không auto-pass, không khoá vuốt.
    - Ad `FAIL` lúc đang đứng ở trang thì đi tiếp **theo chiều user đang đi** (cờ `travelForward`, tính từ lần đổi
      `settledPage` trước).
    - Layout `native_fsn_filled` của SDK, AdChoices `top_left` (như a047). Từ 15/10/2026 truyền thêm
      `defaultNativeLayout` = `XtechR.layout.native_full_screen` (file layout SDK của key `native_fsn_filled`, A045
      cũng truyền file này; là tên file, không phải key `ads_config`) và `collapsedLayout = null` như A048, để RC ghi
      sai key layout thì FSN vẫn full màn.
    - Chưa có after-click theo RC, chưa có RC tắt nút.
- **Bẫy:**
  - Một key `native_full_time_to_countdown` dùng 2 lần: thời gian chờ trước khi hiện pill, và số giây đếm. Tổng
    thời gian ≈ 2×T + auto-pass (default 6 s). Đổi T là đổi cả hai.
    - A048 cùng tên key nhưng chỉ dùng 1 lần: đếm ngay khi vào trang, tổng ≈ T, không auto-pass. Port giữa 2 kiểu
      thì so nghĩa, đừng chỉ so tên key.
  - Đơn vị: A013 dùng **ms**, đa số app khác dùng **giây**. Không đổi kiểu/đơn vị của key đã phát hành.
  - Timer chạy theo trang, không theo trạng thái ad: ad chưa render vẫn đếm. A045
    `ui/screen/onboard/view/OnboardAdContent.kt` chỉ đếm từ khi ad `SUCCESS`/`IMPRESSED`, ad `FAIL` thì tự qua.
  - Timer X chỉ được chạy khi FSN là trang hiện tại. A045 truyền `isCurrentPage` = (|page − currentPage| ≤ 1)
    (`ui/screen/onboard/view/OnboardContent.kt`) nên đếm cả lúc FSN mới là trang kề: user tới nơi thì X đã có sẵn.
  - Đếm từ lúc ad hiện (A045, a047, a049) thì ad chậm (`LOADING`/`TIMEOUT`) là chưa có X. Đừng khoá vuốt trong lúc
    đó.
  - Danh sách trang chốt (A048, a049): trang FSN có mặt cả khi ad lỗi, nên ad `FAIL` lúc user đang đứng ở trang thì
    phải tự rời trang. Hướng đi theo ref (Q40); viết mới thì đi **theo chiều user đang đi** như a049.
    - A048 luôn đẩy tới: user vuốt lùi vào FSN đang lỗi bị đẩy tới lại, không vuốt về được trang trước.
    - A048, a049 chỉ rời trang ở `FAIL`. Ở `TIMEOUT` SDK vẫn nạp tiếp rồi ra `SUCCESS` hoặc `FAIL`.
  - Port `FsnPage` của A013 (state `remember`) sang app 2 FSN thì đổi sang `rememberSaveable` như A048, a049. Có
    5 trang thì FSN xa trang hiện tại bị gỡ khỏi composition; giữ `remember` là quay lại đếm từ đầu.
  - X ở góc trên-phải thì AdChoices phải ở góc khác. Đặt bằng field `adChoicesPlacement` của adunit trong
    `ads_config`: `top_left`, `top_right` (mặc định), `bottom_left`, `bottom_right` (SDK `AdUnitConfig`). a047, a049
    để `top_left` cho unit FSN. X đè AdChoices là sai chính sách.
  - Onboard vẽ tràn dưới status bar (a049): native FSN phủ cả vùng status bar.
    - X phải tự chừa status bar (`statusBarsPadding`).
    - AdChoices góc trên rơi vào vùng đồng hồ, có thể không bấm được. Kiểm với ad thật.
  - A013 không khoá vuốt trong lúc đếm. a034 và a036 khoá `userScrollEnabled` tới khi có X. Đây là quyết định
    của MO.
  - `clear_ads` ở FSN làm trang FSN rời pager (xem MO-54).
  - Số trang phụ thuộc trạng thái ad nên phải bọc `derivedStateOf`. Không bọc → crash `pending composition has
    not been applied` (luật crash của A013).
- **QC:**
  - Default: vào FSN → 2 s hiện pill "2" → đếm → X → 2 s sau tự sang OB cuối. Bấm X sớm: sang ngay.
  - Vuốt khỏi FSN giữa lúc đếm rồi quay lại: đếm tiếp, không chạy lại từ đầu.
  - Ma trận after-click cho fsn (QC MO-56), làm cả với ad mượn từ splash.
  - Có key tắt nút: đặt false → không có pill/X, vuốt qua được, tự qua theo auto-pass.
  - Kiểu a049 (đếm từ lúc ad hiện, giữ tiến độ): ad nạp sẵn thì đủ `time_show_button_X_fsn` giây mới có X. Vuốt đi
    giữa chừng rồi quay lại: đếm tiếp; X đã hiện thì còn.
  - App chốt danh sách trang: cho FSN `FAIL` lúc đang đứng ở trang (unit no-fill; tắt nameSpace thì trang không có
    mặt) → tự rời trang theo hướng của ref. Kiểu a049: vuốt lùi từ OB2 vào FSN12 đang lỗi → về được OB1.
  - Ad thật: AdChoices bấm được, không bị X hay status bar che.

## MO-60 — Native OB4 (trang cuối): none / next page / has ads / finish
- **Yêu cầu:** native trang onboarding cuối ("ob4" của sheet = OB3 của A013) có đủ 4 lựa chọn sau click.
- **Nghiệm thu:** `finish` (default) → rời onboarding. `next_screen` → cũng rời (không còn trang kế).
  `clear_ads`/`none` như MO-54/55.
- **SDK:** như MO-56.
- **Chuẩn A013:** `action_clicked_native_ob3` default `finish`, có nhánh `finish`, `clear_ads`, `none`. **Chưa
  xử lý `next_screen`**: giá trị này rơi khỏi `when` nên thành "không làm gì".
- **Remote config:** `action_clicked_native_ob3` (String, `finish`). Alias: `action_clicked_native_ob4` (a033,
  a036, a041), `action_clicked_new_native_ob3` (a014).
- **Placement / tracking:** `onboard_3` (A013). Alias: `onboard_4` (a047), `native_ob3` (a016, a037, a039,
  a042), `native_ob_3` (a028), `native_ob4` (a036, a041).
- **Cách làm:** theo MO-56. Thêm nhánh `next_screen` → `advanceOne()`; ở trang cuối hàm này đi đường Get started.
  a016 map `next_screen` → finish cho ob3.
- **Bẫy:** `finish` sau click ad có thể nối tiếp ngay inter `inter_ob_3`, tức 2 ad liền nhau. A013 vẫn làm vậy;
  báo MO nếu cần chặn.
- **QC:** như MO-57 cho slot trang cuối, thêm lượt `next_screen`.

## MO-61 — Config layout native onboarding
- **Yêu cầu:** layout của từng native onboarding, kể cả layout riêng cho ad Meta, đổi được qua remote config
  không cần update app. Ảnh sheet là entry `native_ob1` của config đời cũ (`layoutKey`/`layoutKeyMeta`).
- **Nghiệm thu:**
  - Đổi layout của `onboard_1` trong RC `ads_config` → mở lại app, native OB1 đổi layout.
  - Ad Meta dùng `layoutMeta`.
  - Key sai → về layout mặc định, không crash.
  - FSN luôn là layout full màn.
- **SDK:** có. `NativeBannerGroupView(placement, defaultNativeLayout)` chọn layout theo thứ tự:
  1. `placements[].layout`/`layoutMeta` (override theo placement);
  2. `nameSpaces[].adunits[].layout`/`layoutMeta`;
  3. `defaultNativeLayout` của app.

  Ad từ adapter Facebook/Meta dùng `layoutMeta`. Key resolve qua enum `AdLayout`; key lạ thì im lặng dùng
  default. Màu theo `configs.themes` + `placements[].theme`. Danh sách key hợp lệ ở xTechSDK
  `docs/ADS_CONFIG_JSON_GUIDE.md` §7.3.
- **Chuẩn A013:**
  - `OnboardPage` gọi `NativeBannerGroupView` không truyền `defaultNativeLayout`, nên lấy default của SDK.
  - `FsnPage` truyền `R.layout.native_full_t2c`.
  - `app/config/ads_config.json`: `onboard_1`/`onboard_3` = `native_med_16_9_b`, `onboard_2` =
    `native_med_16_9_d`, `fs_onboard` = `native_fsn_filled` + `layoutMeta` `native_fsn_stroke`.
  - Mỗi placement onboarding có nameSpace riêng, nên đổi layout từng trang độc lập.
- **Remote config:** `ads_config` (JSON), không có key riêng từng slot. Alias:
  - a028: key phẳng `layout_native_onboard_1..3` (+ `_meta`), `layout_native_fsn` (+ `_meta`). Giá trị là tên
    layout, map trong `AdsManager.layoutNative`.
  - a036: `type`/`typeMeta` của native position (`AdsConfigProvider.getLayoutResForNameSpace`).
  - a041: `layoutKey`/`layoutKeyMeta`.
- **Placement / tracking:** `onboard_1`, `onboard_2`, `onboard_3`, `fs_onboard`. Không có event riêng.
- **Cách làm:**
  1. App dùng SDK: mỗi placement onboarding có nameSpace riêng, hoặc override `layout` theo placement. Khai đủ
     `layout` + `layoutMeta` cho từng adunit.
  2. Truyền `defaultNativeLayout` hợp design ở từng chỗ gọi. **Bắt buộc với FSN** (layout full màn). Đọc
     `FsnPage`/`OnboardPage` (A013).
  3. Gửi MO bảng key layout hợp lệ.
  4. Không dùng SDK: thêm key/field layout theo khuôn app (a028 hoặc a036).
  - Ref A048 khác A013: FSN dùng layout riêng của app `res/layout/native_full_t2e.xml` (nền sáng), truyền qua
    `defaultNativeLayout` (`ui/screen/onboard/view/OnboardAdContent.kt`). `ads_config` để `layout` =
    `native_full_t2e`, key này không có trong `AdLayout` nên SDK luôn rơi về layout app. Qua RC chỉ đổi được sang
    key của SDK. a047, a049 dùng `native_fsn_filled` của SDK.
- **Bẫy:**
  - Key sai không báo lỗi. a039 ghi nhận `native_full_screen` có trong bảng nhưng không resolve, phải dùng
    `native_fsn_filled`. Verify bằng screenshot thật.
  - FSN không có fallback full màn thì config hỏng sẽ vẽ native nhỏ giữa trang trắng.
  - Layout cao/thấp làm đổi chiều cao vùng nội dung OB (native nằm dưới cùng). Test màn nhỏ.
  - Chọn layout trang (gọn vì có ad, hay đầy đủ) theo trạng thái unit, không theo placement có bật: ad `FAIL` mà trang
    vẫn gọn thì đáy trống (A049 16/10). A049 đọc `statusFlow` của unit trang: `FAIL` → layout không ad; `TIMEOUT` giữ
    gọn vì SDK nạp tiếp ở nền.
  - Nút CTA native không được trùng màu nút Next/Get started của app (luật chính sách).
  - `ads_config` trên Firebase thắng file trong repo.
- **QC:** sửa layout `onboard_1` trên RC `ads_config` → `pm clear`, mở 2 lần → OB1 đổi layout. Đặt key sai →
  layout mặc định. Có ad Meta (mediation test) → layoutMeta.

## MO-62 — Config reload native onboarding
- **Yêu cầu:** mỗi native onboarding có cờ RC quyết định có nạp ad mới khi user quay lại hoặc lướt qua trang
  (ảnh sheet: `forceReload` trong config đời cũ).
- **Nghiệm thu:**
  - Cờ bật: vuốt OB1 → OB2 → OB1 thì ad OB1 đã đổi (có `iaa_request` + `iaa_impression` mới).
  - Cờ tắt: giữ ad cũ, không request mới.
  - Tắt cờ của trang chưa từng có ad thì lần đầu **vẫn phải có ad**.
- **SDK:** một phần.
  - `loadAd` tự bỏ qua ad còn mới (`SUCCESS`) và reload ad đã `IMPRESSED`.
  - NameSpace có `reloadWhenResume` (reload lúc resume) và `actionClicked: reload`.
  - Adunit có `autoReloadOnImpression` (ms).
  - Cờ reload theo trang là việc của app.
- **Chuẩn A013:**
  - `AdsManager.reloadOb1/reloadOb2/reloadOb3/reloadFsn` (RC phẳng) được `loadAdForKind` dùng cho trang trước,
    hiện tại và sau mỗi lần đổi trang (`OnBoardContentNew`).
  - `app/config/ads_config.json`: mọi nameSpace onboarding `reloadWhenResume: true`.
  - **Bug:** `onboard_3` chỉ được nạp trong `loadAdForKind`. Đặt `reload_ob3=false` thì OB3 **không bao giờ có
    ad**. Tương tự FSN khi lần preload ở màn trước fail và `reload_fsn=false`.
- **Remote config:** `reload_ob1|reload_ob2|reload_ob3|reload_fsn` (Boolean, `true`). Alias:
  - `reload_fsob12` (a027), `reload_fsn12` (a034), `reload_fsn_ob` (a039);
  - `reload_onboard_1..4` (a033), `reload_onboard`/`reload_onboard4` (a041), `reload_ob4` (a036);
  - đọc từ `reloadWhenResume` của nameSpace (a016, a037, a045, a047, a042);
  - `forceReload` của native position (a028, config tự viết).
- **Placement / tracking:** `iaa_request`/`iaa_impression` theo `ad_placement`.
- **Cách làm:**
  1. RC theo slot (giữ key app đang có).
  2. Một hàm "load hoặc reload": load nếu unit chưa có ad (`NONE`/`FAIL`), reload chỉ khi cờ bật. Tham khảo
     extension `AdGroupUnit.loadOrReload(context, reload)`: a045/a044 để ở `ads/AdGroupUnitExt.kt`, a037/a039
     ở `ads/AdGroupCompat.kt`. a044 `AdsManager.reloadOnboardAdsOnPageChange` liệt kê sẵn unit cần nạp theo
     từng trang.
     - Các bản `loadOrReload` này (cả A048) chỉ coi `NONE` là chưa có ad: unit `FAIL` không được nạp lại khi
       `reload = false`.
     - a049 khác: bản nhận `context` bỏ qua `reload` và luôn gọi `loadAd`.
       - SDK tự bỏ qua unit `SUCCESS` còn hạn / `LOADING` / `TIMEOUT`, nên unit `FAIL` và `IMPRESSED` luôn được nạp
         lại.
       - Ngày 15/10/2026 đã thử đổi theo A048 (`NONE || reload`) rồi trả lại: user chốt giữ logic đang chạy.
     - App chưa có hàm này (viết mới): ref mặc định (A013) thì viết điều kiện có cả `FAIL` như ý trên. Ref là một
       trong các app này thì giữ như ref, ghi điểm lệch vào bảng khác biệt.
     - **App đã có hàm load/reload đang chạy thì giữ nguyên logic của nó, đừng sửa cho giống ref.** Ghi điểm lệch vào
       bảng khác biệt; chỉ sửa khi user yêu cầu.
  3. Gọi cho cửa sổ trang trước/hiện tại/sau mỗi khi trang đổi. Đọc effect đổi trang và `loadAdForKind` ở A013.
  4. Rà `reloadWhenResume` trong `ads_config` cho khớp ý MO (2 tầng).
  - Ref A048 khác A013: không có cờ RC theo trang. Mỗi lần trang dừng thì nạp bộ unit cố định của trang đó: trang
    hiện tại + trang kề (OB1 nạp thêm OB2), **kể cả trang đang xem**, `reload = true`
    (`AdsManager.reloadOnboardAdsOnPageChange`).
  - App đã làm: a049 mỗi lần dừng ở trang OB thì nạp các trang trong 2 bước quanh nó (dừng ở FSN thì không nạp),
    **bỏ trang đang xem** để không thay ad user đang nhìn (`OnboardViewModel.loadAdsAround`). Cũng không có cờ RC
    theo trang.
- **Bẫy:**
  - `loadAd()` khi ad `SUCCESS` còn hạn là no-op. Muốn ép đổi ad phải `reset()` trước (`qc.md` §2).
  - Reload trang đang xem thì ad đổi ngay trước mắt user. Nhờ `keepAdWaitLoading` (default true), ad cũ được giữ
    tới khi ad mới `SUCCESS`.
  - Đừng lấy cờ reload theo trang từ `reloadWhenResume` nếu SDK cũng reload lúc resume: dễ nạp chồng 2 lần
    (a039 CHANGELOG).
  - FSN đang mượn `native_full_splash` thì `reload_fsn` không có tác dụng.
  - Mỗi lần reload là 1 request. MO theo dõi fill rate.
  - SDK view tự nạp lại khi được dựng lại (Tổng quan nhóm, Preload ý 5). Cờ `reload_*` tắt mà nameSpace để
    `reloadWhenResume: true` thì native bị gỡ khỏi composition rồi dựng lại vẫn đổi ad. A013 gate `nearActive`: đi
    OB1 → OB2 → FSN → OB2 là native OB1 bị gỡ rồi dựng lại.
- **QC:**
  - Cờ bật: OB1 → OB2 → OB1 thấy ad khác, log có request mới cho `onboard_1`.
  - Cờ tắt: ad giữ nguyên, không request.
  - Cờ tắt, đi xa hơn 1 trang rồi quay lại (OB1 → FSN → OB1): ad OB1 vẫn phải giữ nguyên. A013 đổi ad ở lượt này
    (xem Bẫy).
  - A013: `reload_ob3=false` → OB3 trống (bug đã biết). App đã sửa thì OB3 vẫn có ad lần đầu.

## MO-63 — Config màn kế sau onboarding (select / language / iap / home)
- **Yêu cầu:** RC chọn màn đi tiếp sau onboarding: select, language, iap, home. QC đổi RC để test.
- **Nghiệm thu:**
  - Mỗi giá trị tới đúng màn. Giá trị lạ → default.
  - Tới Home thì kết thúc first open.
  - Ad màn kế đã preload từ lúc ở trang cuối onboarding.
- **SDK:** một phần. `AdsConfigProvider.getNavigationValue(key, default)` đọc `navigationFlow` trong
  `ads_config`. Map giá trị sang màn là việc của app.
- **Chuẩn A013:**
  - `ads/AdsManager.kt`:
    - enum `FONavKey` (`splash_next`, `language_next`, `select_next`, `onboard_next`) và `FONavValue`
      (`language`, `select`, `onboard`, `home`);
    - `getNextDestination` đọc **key RC phẳng** từ prefs; giá trị lạ dùng fallback của key;
    - `nextOnBoard` = `ScrOnboardFeature` khi `new_onboard`, ngược lại theo `onboard_next` (default `home`).
  - Trang cuối gọi `loadNativeNextOnboard` → `preloadAdsFO(nextOnBoard)`. `firstOnboard=false` được đặt ở Home
    (`HomeScreen`).
  - **Lệch:**
    1. Không đọc `navigationFlow`, dù `app/config/ads_config.json` có khai.
    2. Không có giá trị `iap` (A013 không có paywall trong FO).
    3. `new_onboard=true` (default) thì `onboard_next` bị bỏ qua: luôn tới `ScrOnboardFeature` rồi Home.
- **Remote config:** `onboard_next` (String, `home`; `language`, `select`, `iap`, `home`). Alias:
  - entry `onboard_next` trong `navigationFlow` của `ads_config` (a027, a028, a033, a037, a044, a045…);
  - giá trị `paywall` thay cho `iap` (a027, a028);
  - a027 thêm `scan_onboard`, a045 thêm `uninstall`;
  - a016 đặt key camelCase `onboardNext` (trong `navigationFlow`);
  - `new_onboard` (A013).
- **Placement / tracking:** `screen_show` của màn đích. Native màn đích preload theo `preloadAdsFO`.
- **Cách làm:**
  1. Đọc từ nguồn app đang dùng (key phẳng hay `navigationFlow`). Không đổi nguồn của app đã phát hành.
  2. Map giá trị → màn. `iap`/`paywall` → paywall nếu được hiện IAP (chưa mua, IAP bật), ngược lại Home: tham
     khảo a027 `AdsManager.paywallOrHome`. Giá trị lạ → default.
  3. Tới Home thì đặt `firstOnboard=false`.
  4. Trang cuối preload ad màn kế; `onGetStarted` navigate rồi bỏ Onboard khỏi stack. Đọc `nextOnBoard`,
     `getNextDestination`, `preloadAdsFO` ở A013.
  5. MO-52 dùng chung nguồn luồng này để tìm màn trước.
- **Bẫy:**
  - `onboard_next=onboard`, hoặc vòng language ↔ onboard: `navigateTo` của A013 bỏ qua khi đích trùng màn đang
    đứng, nên user kẹt ở trang cuối. Chặn giá trị trỏ về chính nó.
  - Màn đích bị RC tắt (Select/Language off) thì nhảy tiếp: tham khảo a027 `skipTo`.
  - Preload và navigate phải dùng **cùng một** hàm tính đích. A013 gộp `new_onboard` vào `nextOnBoard` chính vì
    trước đây 2 chỗ lệch nhau.
- **QC:**
  - Đặt từng giá trị trên Firebase → `pm clear` → chạy FO → sau onboarding tới đúng màn; native màn đó có ad
    ngay khi vào.
  - Giá trị rác → default.
  - A013: nhớ đặt `new_onboard=false`, nếu không thì luôn ra `ScrOnboardFeature`.

## MO-64 — Impression flow 1px: đứng OB1 → impression native OB1 + OB2
- **Yêu cầu:** `HorizontalPager` onboarding có `contentPadding` 1 pixel để trang kề lộ 1px. Đứng ở OB1 thì
  native OB1 và OB2 đều có impression.
- **Nghiệm thu:** vào OB1, không vuốt → logcat có `iaa_impression` của `onboard_1` và `onboard_2`. FSN và OB3
  chưa có impression.
- **SDK:** không (cấu hình pager ở app). SDK chỉ vẽ native và bắn `iaa_impression`.
- **Chuẩn A013 (`OnBoardContentNew`):**
  - `HorizontalPager` có `contentPadding` = `PaddingValues(horizontal = …)` với 1px đổi qua `LocalDensity`
    (không phải `1.dp`), và `beyondViewportPageCount = 1`.
  - Chỉ trang có `nearActive` (|page − currentPage| ≤ 1) mới vẽ `NativeBannerGroupView`.
  - Native OB nằm đáy trang, `fillMaxWidth`, không padding ngang. Native FSN `fillMaxSize`.

  Impression theo trang (khi có FSN):

  | User đứng ở (sheet) | Trang A013 | Native có impression |
  |---|---|---|
  | OB1 (MO-64) | OB1 | `onboard_1`, `onboard_2` |
  | OB2 (MO-65) | OB2 | `onboard_1`, `onboard_2`, `fs_onboard` |
  | OB3 / FSN (MO-66) | FSN | `onboard_2`, `fs_onboard`, `onboard_3` |
  | OB4 (MO-67) | OB3 | `fs_onboard`, `onboard_3` |

  Không có FSN: OB1 → ob1 + ob2; OB2 → ob1 + ob2 + ob3; OB3 → ob2 + ob3.
- **Remote config:** không có key riêng. Phụ thuộc `enable_ob*` (trang nào có) và `reload_*` (MO-62).
- **Placement / tracking:** `onboard_1`, `onboard_2`. `iaa_impression` có `ad_placement` (xem bẫy).
  `screen_show` `ScrOnboard1`.
- **Cách làm:**
  1. Pager: `contentPadding` ngang đúng 1px (đổi px → dp bằng density), `pageSpacing` = 0. Nhờ lộ 1px, trang kề
     đã tính là trang hiển thị nên được compose sẵn. `beyondViewportPageCount` không bắt buộc cho impression:
     A013 để 1 để dựng trước trang ±2 cho vuốt mượt; a047 để mặc định.
  2. Chỉ vẽ native cho trang cách trang hiện tại ≤ 1. Ad view phủ sát mép trái/phải của trang.
  3. Gắn `screen` cho unit (`AdGroupUnit.of(placement, screen = "ScrOnboard2")`…) để `ad_placement` đúng trang.
     a027, a045, a037, a039, a049 đã làm; A013, a047, A048 chưa.
  4. Danh sách trang đổi động thì truyền `key` cho pager theo loại trang.
  5. App 2 FSN (A048, a049): trang kề của OB là FSN, nên bộ impression khác bảng A013. Kiểm theo "trang hiện tại +
     2 trang kề" (mặc định Q41):
     - OB1 → `onboard_1`, `fs_onboard`;
     - FSN12 → `onboard_1`, `fs_onboard`, `onboard_2`;
     - OB2 → `fs_onboard`, `onboard_2`, `fs_onboard_2`;
     - FSN23 → `onboard_2`, `fs_onboard_2`, `onboard_3`;
     - OB3 → `fs_onboard_2`, `onboard_3`.
  - XML/ViewPager2: xem `stack-adapt.md` §4. Chưa app nào làm onboarding bằng ViewPager2; a031 nhúng
    `HorizontalPager` trong `ComposeView` của fragment.
- **Bẫy:**
  - `1.dp` ≠ 1px (3px ở xxhdpi): trang kề lộ nhiều, UI lệch.
  - Native nằm trong trang có padding ngang (vd 16dp) thì cột 1px lộ ra là nền, không phải ad view → **mất
    impression**.
    - A048 đặt native trang nội dung trong `Column` có padding ngang 16dp (`OnboardIntroContent`): chỉ trang FSN
      kề có impression, native OB kề thì không.
    - a049 cho native trang nội dung tràn ngang, đáy chỉ chừa nav bar (`OnboardContentPage`).
  - `beyondViewportPageCount` lớn mà không gate `nearActive` thì native trang xa được compose ngoài màn: tốn
    request, và vẫn có thể ghi impression dù không lộ pixel nào (A049 trước 16/10: `fob23` bắn khi đứng OB1, QC
    P5078). Gate như A048 (`pageDistance <= 1`) / A013 (`nearActive`). Tài liệu SDK `docs_final/FO_ADS_FLOW.md` §4
    gọi đây là visibility guard.
  - Đổi trang mà chỉ nạp trang kề, bỏ trang đang xem (A047 `preloadOnboard`, A049 trước 16/10): ad của trang vừa
    tới đã có impression lúc còn là dải 1px → đứng ở trang đó không có impression mang `screen_name` của nó (QC
    A049 P5078). A048 / A013 nạp lại cả trang đang xem; đánh đổi là ad đổi sang ad mới ~0,5–1s sau khi dừng.
  - Không truyền `screen` thì SDK lấy `TrackingState.lastScreen` làm `ad_placement`. Impression `onboard_2`
    lúc đứng OB1 bị ghi thành `ScrOnboard1`. a027 còn tráo nhãn `screen` 12/23 của 2 unit FSN trong
    `AdsManager`.
  - SDK chép `screen` của unit sang adunit con lúc bắt đầu nạp (`AdGroupUnit.createChild`). Gán `screen` sau khi
    unit đã nạp thì ad đó vẫn ghi `ad_placement` theo `lastScreen` tới lần nạp sau. View SDK có thể tự nạp trước khi
    `AdsManager` kịp gán (Preload ý 5). Chắc nhất: truyền luôn `screen` vào `NativeBannerGroupView` ở từng trang
    (tham số có sẵn).
  - `screen_show` của A013 tính theo **index cứng**, nên sai khi tắt trang (`enable_ob1=false`…). Tính theo loại
    trang như legacy `OnBoardContent` (`screenNameOf`) hoặc a045 (`OnboardSlot.trackingName`).
  - A013 không truyền `key` cho pager. FSN chèn vào hoặc rơi ra thì state trang (timer FSN, video) dính sang
    trang khác. a027, a016, a045, a047, A048, a049 có `key`.
  - Số trang phụ thuộc trạng thái ad nên phải bọc `derivedStateOf` (luật crash của A013).
- **QC:**
  - Logcat `adb logcat | grep -iE "iaa_impression|ad_placement"` khi vừa vào OB1: thấy đúng 2 placement.
  - Log debug của SDK `onAdImpression` có `name=` của adunit (vd `native_fob12_high`): biết chắc slot nào có
    impression, kể cả khi `ad_placement` sai.
  - Layout Inspector: page width = màn − 2px, mép phải lộ 1px của OB2.
  - Thử `enable_ob2=false`: đứng OB1 thì impression ob1 + FSN (trang kề mới).
  - App 2 FSN: đứng OB1 thấy `onboard_1` + `fs_onboard`, không phải `onboard_2` (bước 5).

## MO-65 — Impression flow 1px: đứng OB2 → impression native OB1 + OB2 + full-screen
- **Yêu cầu:** đứng ở OB2 thì native OB1, OB2 và FSN đều có impression (cơ chế MO-64).
- **Nghiệm thu:** vuốt tới OB2 và dừng: có `iaa_impression` mới cho `fs_onboard`; OB1 và OB2 hiển thị ad (OB1
  là ad mới nếu `reload_ob1` bật). Không có FSN (no fill) thì trang kề phải là OB3.
- **SDK:** như MO-64.
- **Chuẩn A013:** như MO-64. Native FSN được vẽ ở trang kề nhờ `nearActive`. Đứng OB1/OB2 mà FSN chưa có ad thì
  `loadAdForKind` retry FSN.
- **Remote config:** `enable_ob2`, `reload_fsn`, `fs_onboard` bật trong `ads_config`.
- **Placement / tracking:** `onboard_1`, `onboard_2`, `fs_onboard` (hoặc `native_full_splash` khi mượn).
  `screen_show` `ScrOnboard2`.
- **Cách làm:** theo MO-64. Thêm: trang FSN chỉ có mặt khi ad có thể hiện; retry FSN khi user còn ở trước slot.
- **Bẫy:**
  - FSN chưa có ad khi user tới OB2 → trang kề là OB3. Ad về muộn → FSN chèn vào giữa OB2 và OB3 (đúng ý). Không
    được chèn khi user đã qua slot.
  - Timer pill FSN chỉ chạy khi FSN là trang hiện tại, impression ở trang kề không kích timer.
  - App chốt danh sách trang (A048, a049): FSN no-fill vẫn giữ chỗ, cột 1px kề là trang trống. Trang kề không
    chuyển thành OB3 như A013, nên mất impression của trang sau. Đứng ở FSN lỗi thì app tự rời trang (MO-59).
    Lệch dòng nghiệm thu "no-fill thì trang kề là OB3": ghi vào bảng khác biệt (Q41).
- **QC:** dừng ở OB2 → thấy impression `fs_onboard` trong log. Cho FSN no-fill (unit test sai/tắt) → trang kề
  là OB3, impression `onboard_3`.
  - App 2 FSN: dừng ở OB2 → impression `fs_onboard`, `onboard_2`, `fs_onboard_2`. `onboard_1` cách 2 trang, không
    lộ.

## MO-66 — Impression flow 1px: đứng FSN (OB3 của sheet) → impression OB2 + OB4 + full-screen
- **Yêu cầu:** đứng ở trang full-screen thì native OB2, FSN và OB4 (A013: `onboard_3`) đều có impression.
- **Nghiệm thu:** dừng ở FSN: có impression `onboard_3`; FSN là ad đang hiện; OB2 được reload nếu cờ bật.
- **SDK:** như MO-64.
- **Chuẩn A013:** như MO-64. `onboard_3` được nạp lần đầu khi FSN (trang kề của OB3) thành trang hiện tại, qua
  `loadAdForKind` (cần `reload_ob3` = true, xem bug MO-62).
- **Remote config:** `enable_ob3`, `reload_ob3`, `reload_fsn`.
- **Placement / tracking:** `onboard_2`, `fs_onboard`, `onboard_3`. `screen_show` `ScrNativeFullScreen`.
- **Cách làm:** theo MO-64. Bảo đảm unit trang cuối được nạp **trước** khi tới FSN: nạp sẵn từ màn trước
  hoặc từ OB2 (a047 `AdsManager.preloadOnboard` nạp trước 2 bước vì FSN xen giữa).
- **Bẫy:** A013 chỉ nạp `onboard_3` lúc đứng ở FSN, nên ad OB3 thường đang `LOADING` khi trang kề lộ ra →
  impression đến muộn hoặc mất nếu user lướt nhanh.
  - A048 cũng vậy: chỉ nạp `onboard_3` khi FSN23 thành trang hiện tại (`AdsManager.reloadOnboardAdsOnPageChange`;
    native trang nội dung chỉ vẽ khi cách trang hiện tại ≤ 1). a049 nạp từ OB2 (`OnboardViewModel.loadAdsAround`:
    trang trước, trang hiện tại, trang sau và nạp sẵn trang +2; từ 16/10).
- **QC:** dừng ở FSN 3 s → log có impression `onboard_3`. Lướt nhanh OB2 → FSN → OB3: OB3 phải có ad (không
  trắng quá 1–2 s).

## MO-67 — Impression flow 1px: đứng OB4 → impression native OB4 + full-screen
- **Yêu cầu:** đứng ở trang cuối thì native trang cuối và FSN (trang kề trước) đều có impression.
- **Nghiệm thu:** dừng ở trang cuối: impression `onboard_3` (ad mới nếu reload). FSN vẫn lộ 1px và được reload
  nếu `reload_fsn` bật.
- **SDK:** như MO-64.
- **Chuẩn A013:** như MO-64. Trang cuối còn kích preload ad màn kế (`loadNativeNextOnboard`) và inter
  `inter_ob_3` (từ trang áp chót).
- **Remote config:** `reload_ob3`, `reload_fsn`, `enable_inter_ob3`.
- **Placement / tracking:** `onboard_3`, `fs_onboard`. `screen_show` `ScrOnboard3`.
- **Cách làm:** theo MO-64. Preload native màn kế khi tới trang cuối (A013, A048; A049 từ 16/10 trong
  `OnboardViewModel.onStepShown`). MO A049 báo sai khi nạp ngay lúc vào Onboard (a047, A049 trước 16/10:
  `LaunchedEffect(Unit)` trong `OnboardScreen`): "`native_survey1_high` chỉ load ở trang cuối".
- **Bẫy:** pill FSN đang đếm dở thì dừng khi user rời FSN. Quay lại FSN thì đếm tiếp, kể cả auto-pass.
  - A013: X đã hiện mà user vuốt lùi từ trang cuối về FSN thì auto-pass chạy lại đủ `native_full_auto_pass_time`
    rồi đẩy user tới trang cuối lần nữa (`FsnPage`).
- **QC:** dừng ở trang cuối → log impression `onboard_3` + `fs_onboard`. Native màn kế đã `iaa_request` trước
  khi bấm Get started.

## MO-92 — Ở trang onboard cuối, vuốt tiếp vẫn vào màn kế (Home)
- **Yêu cầu:** ở trang onboarding cuối, user vuốt tiếp (LTR: ngón tay từ phải sang trái) cũng rời onboarding y
  như bấm Get started.
- **Nghiệm thu:**
  - Ở trang cuối vuốt tiếp quá ngưỡng → inter `inter_ob_3` (nếu bật) → màn kế.
  - Vuốt ngắn hoặc vuốt lùi: không làm gì.
  - Không bao giờ navigate 2 lần.
  - RTL: vuốt ngược chiều cũng ăn.
- **SDK:** không có.
- **Chuẩn A013:**
  - `ui/screen/onboard/view/EndPageSwipe.kt`, `rememberEndPageSwipeConnection(pagerState, onEndSwipe)`: một
    `NestedScrollConnection`. Trong `onPostScroll`, khi đang ở trang cuối và phần cuộn ngang còn dư mang dấu âm,
    nó cộng dồn; vượt `END_SWIPE_THRESHOLD_PX` (−100 **px**) thì gọi `onEndSwipe` và về 0. Mọi cuộn khác đặt
    lại 0.
  - Gắn bằng `Modifier.nestedScroll` vào `Box` bọc pager trong `OnBoardContentNew`. `onEndSwipe` =
    `onGetStartedClick` → `onGetStarted` (chặn 2 lần, `inter_ob_3`, `nextOnBoard`).
  - Luôn bật, không có RC.
- **Remote config:** A013 không có key. Alias: `enable_ob_end_swipe` (a016), `swipe_to_home` (a034, kiểu trang
  câm), `enable_swipe_to_home_onboard` (a033), `allow_swipe_get_started` (a047, a042). MO muốn bật/tắt thì đề
  xuất `allow_swipe_get_started` (Boolean, `true`), vì đã có 2 app dùng.
- **Placement / tracking:** A013 không log riêng. a047 log `button_click` `SwipeGetStarted`; a037 log `BtnNext`;
  A048, a049 cũng log `BtnNext`, ngay trước khi rời (như bấm nút). Native màn kế đã preload ở trang cuối.
- **Cách làm:**
  1. Đặt `NestedScrollConnection` ở cha của pager. Điều kiện bắn: đang ở trang cuối + hướng "tiến" +
     `NestedScrollSource.UserInput`. Ngưỡng tính bằng dp (32–48dp). Có cờ để chỉ bắn 1 lần; bắt cả
     `onPostFling`.
  2. Gọi đúng hàm finish chung (chặn 2 lần + inter + navigate).
  3. Xác định hướng "tiến" theo `LocalLayoutDirection` (RTL: phần dư mang dấu dương).
  4. Đọc `EndPageSwipe.kt` (A013), và bản đã sửa các điểm trên ở a047
     `ui/screen/onboard/view/OnboardContent.kt` (`swipeGetStartedConnection`) hoặc a041/a037/a039. a049
     `ui/screen/onboard/content/OnboardContent.kt` (`rememberSwipeToFinishConnection`) cũng đủ các điểm, ngưỡng
     48dp, luôn bật (không RC).
  - Ref A048 khác A013 (`ui/screen/onboard/view/OnboardContent.kt`, `finishOnSwipe`): ngưỡng 100 **px** như A013;
    có RTL và cờ bắn 1 lần; không lọc `UserInput`, không bắn ở `onPostFling`. Luôn bật.
  - Gắn `nestedScroll` thẳng vào modifier của `HorizontalPager` (A048, a049) cũng nhận được phần cuộn dư, không
    bắt buộc bọc `Box`.
- **Bẫy:**
  - Ngưỡng A013 tính bằng px: máy mật độ cao chỉ cần vuốt rất ngắn. Dùng dp.
  - A013 không xử lý RTL: tiếng Ả Rập vuốt không ăn (dù hint MO-53 có lật).
  - Fling nhanh thì phần dư đi qua `onPostFling`, không qua `onPostScroll`, nên có thể không bắn.
  - A013 không có cờ bắn 1 lần tại chỗ, chỉ dựa vào `getStartedTriggered` ở Screen. Giữ guard đó.
  - Kiểu "trang câm" (a034 `swipe_to_home`): user thấy trang trống lướt qua, pager phải `scrollToPage` lùi lại.
    Ưu tiên NestedScroll. a033 làm cách thứ ba: `pointerInput` + `detectHorizontalDragGestures`, bắn khi đang ở
    trang cuối và pager không cuộn tiếp được (`canScrollForward` = false), modifier `overSwipeToFinish`.
  - Trang cuối là FSN (khi `enable_ob3=false`): vuốt cũng rời onboarding, và không có `inter_ob_3` (A013 chỉ
    show khi `enable_ob3`).
- **QC:**
  - Trang cuối: vuốt tiếp dứt khoát → (inter) → màn kế. Vuốt nhẹ vài mm → không đi.
  - Fling thật nhanh → vẫn đi, chỉ 1 lần (không 2 màn chồng).
  - Vuốt lùi ở trang cuối → về trang trước bình thường.
  - Ngôn ngữ RTL: vuốt trái → phải ở trang cuối → đi.
  - Bấm Get started rồi vuốt ngay → chỉ 1 lần navigate.

## EXT-NATIVE-POOL — Native pool dùng chung luồng Language/Onboard (mượn ad, 1 lượt load) — ngoài sheet

> Không có dòng trong sheet MO nên không có MO-ID. Skill nhận mục này qua prompt ("native pool", "mượn ad", "logic
> load_show ad", "1 loading cùng lúc"…). Nguồn: ticket A052 P5210 (v1.0.3) "[logic load_show ad] Update logic load, show
> các vị trí ad luồng onboarding" và spec "Shared native pool — design" MO gửi kèm. Dòng dán sheet MO ghi
> `EXT-NATIVE-POOL (ngoài sheet)`. Mục gồm cả Language/Language Alt nhưng để ở nhóm onboard vì phần lớn cơ chế nằm
> ở pager.

- **Yêu cầu** (brief của MO):
  - Slot ưu tiên ad của chính placement, nếu đã load hoặc đang hiện.
  - Chưa có thì hiện ad đã load mà chưa hiện, mới nhất, của bất kỳ placement nào.
  - Vẫn chưa có thì hiện ad đang hiện gần nhất của placement khác, để slot không bị trống.
  - Cuối cùng mới hiện shimmer.
  - Giữ user đủ lâu để ad kịp hiện: khoá vuốt (RC).
  - Mỗi lúc chỉ 1 lượt load native.
  - Luôn hiện ad cũ, ad mới load xong mới thay vào.
- **Nghiệm thu**:
  - Slot chọn ad theo đúng thứ tự trên. "Placement khác" chỉ tính placement cùng template: native vừa (Language, Alt,
    OB1–4) và native full-screen (2 trang FSN, `native_full_splash_high` lúc được mượn) là 2 nhóm riêng, không mượn chéo.
  - Placement của slot bị tắt (config hoặc không được hiện ad) thì slot ẩn hẳn, không mượn.
  - Request lúc mở/resume màn bị **bỏ** (không xếp hàng) khi pool đang có ad load; request do user bấm và trang FSN kế
    tiếp luôn đi.
  - Đang tải lại thì vẫn hiện ad cũ, chỉ đổi khi ad mới load xong.
  - 1 ad chỉ gắn vào 1 view tại 1 thời điểm.
  - Trang kề trong pager chỉ hiện ad của chính nó; trượt sang trang kế thấy ad sẵn, không bị reload ngay sau impression
    lúc trượt vào.
  - `native_pool_logic = false` chạy đúng logic cũ; `lock_swipe_ob = true` không vuốt được trang Onboard nào.
- **SDK**:
  - Không có pool: mỗi `NativeBannerGroupView` chỉ vẽ ad của chính placement nó nhận. Unit cache theo cặp
    `placement:nameSpace` nên mọi slot cùng placement dùng chung 1 ad.
  - xtechads 1.8.3 làm rối tên lớp `AdGroupAd`, app không lấy được `NativeAd` để tự vẽ. Ad mượn phải vẽ bằng chính
    `NativeBannerGroupView` của placement cho mượn → impression, click, doanh thu tính cho placement cho mượn.
  - Trạng thái để chọn ad lấy từ `AdGroupUnit`: `statusFlow`, `adData`, `adLoadedTime` (đã load), `adImpressionTime`
    (đã hiện: `adImpressionTime ≥ adLoadedTime`). `keepAdWaitLoading` mặc định true nên lúc `LOADING`/`TIMEOUT` view
    vẫn giữ ad cũ.
  - View tự gọi `loadAd` lúc vào composition / `ON_RESUME` (`reloadWhenResume`) và xử lý click `reload`/`disable`
    theo `LocalLifecycleOwner` (`NativeBannerGroupViewImpl`, `LifecycleResumeEffect`).
- **Chuẩn của mục này = A052** (A013 không có). Đường dẫn tính từ `app/src/main/java/com/ai/live/tarot2/`:
  - `ads/NativeAdPool.kt`: `NativeAdPool` giữ danh sách member (placement, nameSpace, nhóm, layout, `isActive`); `pick`
    (chọn ad cho slot, bỏ qua ad slot khác đang giữ), `hasAdFor` / `canFill` (trang FSN có ad để hiện không), `fetch`
    (soft/urgent), `claim` / `release` (khoá bind).
  - `ads/NativeAdPoolSlot.kt`: composable `NativeAdPoolSlot(placement, nameSpace, isFront)` thay `NativeAdSlot` ở
    Language/Alt/OB/FSN; `GatedLifecycleOwner`.
  - `ads/AdsManager.kt`: `nativeAdPool` (khai member), `useNativePool`, `fetchNative`, `fetchLanguageAds`,
    `fetchOnboardAds`, `onboardAdReady`; nhánh logic cũ `preloadAdsFO`, `preloadOnboard`.
  - Màn: `ui/screen/language/normal/LanguageScreen.kt`, `ui/screen/language/alternative/LanguageAltScreen.kt`,
    `ui/screen/onboard/OnboardScreen.kt`, `ui/screen/onboard/OnboardViewModel.kt` (`autoNextFullScreen`, `lockSwipe`),
    `ui/screen/onboard/view/OnboardContent.kt` (`isFront` = `settledPage`).
- **Remote config**:
  - `native_pool_logic` (Boolean, `true`): `false` = logic cũ (mỗi slot ad riêng; Alt nạp OB đầu + FSN; đổi trang nạp
    lại trang trước + 2 trang sau; FSN theo status của chính nó). Chốt 1 lần mỗi process (`useNativePool` lazy), đọc
    lần đầu sau khi Splash fetch RC, để Language và Onboard không lệch logic giữa chừng.
  - `lock_swipe_ob` (Boolean, A052 `false`): khoá vuốt pager Onboard, kể cả vuốt Get Started ở trang cuối (lúc đó
    `allow_swipe_get_started` / MO-92 không còn tác dụng). Độc lập với `native_pool_logic`. Chỉ Onboard, Language không
    có pager.
  - Tên 2 key do dev đặt lúc làm A052, MO chưa đưa tên; app khác làm theo mục này thì hỏi MO trước.
- **Placement / tracking**:
  - Không thêm placement mới. Member pool: `language`, `language_alt` (+ buffer nameSpace `language_alt`, MO-98),
    `onboard_1..4`, `fs_onboard_12`, `fs_onboard_23`, `native_full_splash_high` (chỉ khi FS12 mượn native full splash).
  - `iaa_impression` của ad mượn mang `ad_unit_name` của placement cho mượn, `screen_name` là màn đang hiện.
- **Cách làm**:
  1. Pool 1 instance mỗi process (lazy trong `AdsManager`), thu `statusFlow` của mọi member trên Main vào 1 map snapshot
     để composable tự vẽ lại khi trạng thái đổi. Quyết định load đọc status thật của unit.
  2. Chọn ad cho slot (`pick`): unit của chính slot đang giữ ad còn hạn (~55 phút) → ad đã load chưa hiện mới nhất trong
     nhóm → ad đã hiện gần nhất → không có thì slot hiện shimmer khi nhóm có unit đang load (hoặc chính slot đang load:
     vẽ view của nó để có placeholder của SDK), không thì ẩn. Ad đang hiện mà nạp lại hụt (`FAIL`, còn mạng) thì giữ
     view đó, vì SDK vẫn vẽ ad cũ.
  3. Nạp (`fetch`): placement bị tắt / không được hiện ad → bỏ. Soft mà pool đang có unit `LOADING`/`TIMEOUT` (dưới
     60 s, tránh kẹt vĩnh viễn) → bỏ. Offline, unit đang giữ ad, hoặc đang load → không làm gì. Còn lại `loadAd`.
     - Splash: soft `language`. Language resume: soft `language` + `language_alt` (+ buffer).
     - Alt mở: urgent unit đang hiện (buffer); soft native trang OB đầu (OB1 tắt thì urgent FSN12).
     - Trang OB được chọn / resume: soft placement trang đó; trang kế là FSN thì urgent; đang ở FSN thì urgent chính nó.
     - Ad của trang hiện tại đã có và pool rảnh → soft nạp sẵn trang kế (1 trang, thay preload 2 trang của logic cũ).
     - Có mạng lại (`isConnected`) → gọi lại fetch của màn đang mở.
  4. Khoá bind: slot `claim` unit trước khi vẽ, nhả khi view của unit đó rời composition. Ad slot khác đang giữ thì
     không được chọn để mượn. Màn đang rời giữ ad tới lúc dispose, màn mới hiện shimmer chờ.
  5. Pager: chỉ trang `settledPage` mới chọn/mượn ad. Trang kề (±1) chỉ vẽ ad của chính placement như logic cũ (SDK tự
     hiện shimmer khi đang load, chưa có thì trống), không mượn.
  6. Lifecycle: ad mượn và trang kề vẽ dưới `GatedLifecycleOwner` kẹp ở `STARTED` → SDK không tự nạp lại và không xử lý
     click `reload` cho ad đó. Trang kề lên làm trang chính: cùng owner, chỉ mở `RESUMED` ở lần `ON_RESUME` thật kế tiếp.
  7. Click `next_screen` của mọi unit trong pool do `NativeClickActionEffect` của màn đang mở xử lý (ad mượn có thể là
     của placement khác).
  8. FSN (chỉ logic pool): tự sang trang sau 10 s (đếm khi màn `RESUMED`); không có ad và không đang load thì tự bỏ qua
     trang. X vẫn theo `time_show_button_X_fsn`.
  9. Buffer Language Alt (MO-98) giữ nguyên; logic pool không `reset()` buffer khi rời Language để ad còn cho mượn
     (logic cũ vẫn reset).
- **Bẫy** (A052, 10/2026):
  - 2 view cùng 1 `NativeAd`: AdMob tính impression/click cho view gắn sau cùng, view cũ `destroy()` có thể gỡ luôn bản
    mới. Phải khoá bind (bước 4), và luôn để view cũ dispose xong mới bind view mới.
  - Vẽ ad mượn với lifecycle thật: `reloadWhenResume` của nameSpace cho mượn (`onboard_x` = true) bắn `loadAd` ngay lúc
    vẽ → thêm 1 lượt load song song, phá luật 1 lượt load.
  - Đổi owner từ kẹp sang thật lúc trang kề lên trang chính → SDK nhận `ON_RESUME`, reload ad vừa có impression lúc
    trượt vào (2 impression trong chưa tới 1 s). Phải giữ cùng owner, chỉ mở `RESUMED` ở resume thật sau đó.
  - Bản đầu cho trang kề hiện khung xám đứng yên (không bind) → PO thấy khó chịu, quay về trang kề hiện ad của chính
    nó như logic cũ.
  - Bỏ preload 2 trang thì trang kế trống lúc trượt vào → thêm nạp sẵn soft 1 trang khi ad trang hiện tại đã có.
  - Offline thì `fetch` bỏ qua và không ai gọi lại → phải gọi lại khi có mạng (bước 3).
  - `statusFlow` của SDK phát từ thread IO; đọc `status` trong composition không tự vẽ lại → cần map snapshot (bước 1).
  - Bản thử ẩn nút Next/Skip 2–3 s (spec có) bị PO bỏ: nút hiện ngay ở cả 2 logic.
  - Chưa sửa (có từ trước): vào OB1 sau transition Nav3 (`STARTED` → `RESUMED`), SDK reload `onboard_1` ngay sau
    impression đầu → 2 impression. Sửa được cùng cách bước 6 nếu MO muốn.
  - RC `ads_config` đè file local (`useLocalAdsConfig = false`): pool không thêm placement nhưng các mục khác cùng đợt
    có thêm, nhớ đưa lên Firebase.
  - App có impression flow 1px (MO-64..67): trang kề vẫn vẽ ad của chính nó nên còn impression trang kề; ad mượn chỉ ở
    trang chính.
  - Spec còn các phần A052 chưa làm: tái dùng inter splash chưa hiện làm inter lúc rời Language, tắt app-open trong
    FO, màn select, màn resume, event telemetry riêng.
- **QC**:
  - Bản release (ad thật): vào OB1 lúc ad OB1 chưa có → thấy tạm ad màn trước rồi tự đổi sang ad OB1.
  - Kéo chậm giữa 2 trang: trang kế đã có ad, không khung xám; dừng hẳn không reload. Logcat mỗi trang 1
    `iaa_impression`, trang kế không có impression trước khi hiện.
  - Ở trang FSN tắt mạng, chờ tự sang OB3: popup mất mạng, OB3 vẫn có ad mượn; bật mạng → đổi sang ad OB3.
  - Ra nền rồi quay lại ở trang OB: ad nạp lại như cũ.
  - `native_pool_logic = false`: log load giống logic cũ (Alt nạp OB đầu + FSN; đổi trang nạp lại trang trước + 2 trang
    sau); FSN không tự sang trang, không ad thì X hiện ngay.
  - `lock_swipe_ob = true`: không vuốt được trang nào, kể cả trang cuối; chỉ đi bằng nút.
  - Bản debug: `adb logcat | grep NativeAdPool` thấy `fetch soft` / `urgent` / `soft dropped` / `refused`.

# Language / Language Alt

Recipe chuẩn cho nhóm `language`: MO-32..MO-42, MO-86, MO-94, MO-98, DEV-6, DEV-8, DEV-9, CC-6.

- Ref: A013 v1.2.7. `canonical.commit` = f784827 chỉ là mốc **đối chiếu recipe lần cuối**, không phải code để chép.
- Đường dẫn code A013 tính từ `app/src/main/java/com/example/a013_recovery/`. File res/config tính từ gốc repo.
- Khi làm: mở code A013 **bản hiện tại** theo file + symbol ghi ở từng mục. File đã đổi chỗ thì chạy
  `audit.py --item <ID> --app a013` để định vị lại.

## Tổng quan nhóm

**Luồng FO ở A013**
1. Màn đứng trước Language (theo `splash_next`) preload native `language`: `AdsManager.preloadAdsFO` →
   `loadLanguageAds`.
2. **ScrLanguage** — `ui/screen/language/LanguageFOScreen.kt`, composable `LanguageFOScreen`.
   - Hiện native `language`, chưa có dòng nào được chọn.
   - Mỗi lần resume: preload `language_alt`; 3 giây sau bật ngón tay gợi ý.
   - Tap 1 dòng → sang ngay ScrLanguageAlt(mã đó) và pop ScrLanguage. Back bị nuốt.
3. **ScrLanguageAlt** — `ui/screen/language/LanguageAltScreen.kt`, composable `LanguageAltScreen`.
   - Dòng vừa tap được chọn sẵn. Native `language_alt` (có thể chạy 2 unit buffer).
   - Vào màn: preload ad của màn kế (`AdsManager.loadNativeNextLanguage`).
   - Tap dòng mới → đổi chọn + đổi native. Tap lại dòng đã tap → popup xác nhận có native `popup_lang`.
   - Done / Save / Confirm / click ad (`next_screen`) → ghi `languageSelected`, gọi
     `LanguageManager.updateLanguage`, rồi đi `AdsManager.nextLanguage` (RC `language_next`).
4. Ngôn ngữ chỉ được áp khi xác nhận ở Alt. Trước đó app chạy theo ngôn ngữ máy.

**Class / file chính (A013)**
- `common/LanguageManager.kt` — class `LanguageManager`.
  - Companion: `languages` (list mã đã sort + mã máy ở đầu), `reorderByPriority`, `moveSystemLanguage`,
    `name`, `nameBase`, `flagForCode`, `wrapContextWithLocale`.
  - Instance: `resolveDefaultLanguage`, `updateLanguage`.
- `ui/screen/language/view/LanguageContent.kt` — composable `LanguageContent`: thứ tự list
  (`orderedLanguages`), header Done/tick, ngón tay trong `LanguageListItem`, nút `SaveHintButton`, chọn
  placement theo `LanguageType`.
- `ads/AdsManager.kt` — unit `nativeLang`, `nativeLangAlt`, `nativeLangAltBuffer`, `nativePopupLang`; cờ
  click `clickedLanguage`, `clickedLanguageTooltip`, `clickedNativeLangAlt`; `nextLanguage`, enum
  `FONavKey` / `FONavValue`, `resetNativeLangAlt`, `resetState`.
- `domain/preference/SharedPrefs.kt` — key RC (bảng dưới).
- `ui/base/BufferedNative.kt` (`BufferedNative`, `rememberBufferedNative`),
  `ui/base/dialog/ConfirmLanguageDialog.kt`, `ui/base/dialog/HelpSelectLanguageDialog.kt`,
  `ui/base/AppBackHandler.kt` (`GeneralBackHandler`).
- `MainActivity.kt` (`attachBaseContext`, `onAttachedToWindow`), `AppNavigation.kt` (entry
  `AppDestination.ScrLanguage` / `ScrLanguageAlt`), `domain/models/clas/LanguageType.kt`
  (`Normal`, `Alternative`, `Setting`).

**Quan hệ giữa các mục**
- List và thứ tự: MO-32 (bộ mã) → MO-33 (mã máy đứng đầu, app theo máy tới khi chọn) → MO-34 (sort theo
  tên) → DEV-6 (tối đa 6 mã ưu tiên từ RC).
- MO-35 (2 màn) là nền. Các mục ad (MO-37..41, MO-94, MO-98, DEV-9) đều gắn vào 2 placement
  `language` / `language_alt`.
- Dẫn dắt: MO-36 (ngón tay + chặn back), MO-86 (back: nút Save / popup confirm). DEV-8 đã bỏ.
- Click ad: MO-37 / MO-38 / MO-39 là 3 giá trị của **cùng một** cấu hình theo màn. MO chọn 1.
- Config ad: MO-40 (layout), MO-41 (reload khi quay lại), MO-98 (đổi ad khi đổi ngôn ngữ), DEV-9 = CC-6
  (màu CTA).
- Điều hướng: MO-42 (`language_next`).

**Key RC của nhóm (A013, `SharedPrefs`)**

| Key | Kiểu | Default | Mục |
|---|---|---|---|
| `priority_languages` | String CSV | `""` | DEV-6 |
| `enable_new_language_selection_ui` | Boolean | `false` | MO-36, DEV-6, DEV-8 |
| `language_oder` (sai chính tả, đã phát hành) | Long | `0` | DEV-6, MO-36 |
| `action_clicked_native_lang` | String | `tooltip` | MO-37/38/39 |
| `action_clicked_native_lang_alt` | String | `next_screen` | MO-37/38/39 |
| `buffer_language_alt` | Boolean | `false` | MO-98 |
| `min_ad_interval_language_alt` | Long (ms) | `1000` | MO-98 |
| `language_next` | String | `select` | MO-42 |
| `ads_config` | JSON | file `app/config/ads_config.json` | MO-35, MO-40, MO-41, DEV-9 |
| `language_hint_delay_second` (đề xuất, A013 chưa có) | Long (giây) | `2` | MO-36 |

**Placement:** `language`, `language_alt`, `popup_lang` (màn Setting dùng `banner_all`). Kiểu tên
`native_lang` / `native_lang_alt` có ở a016, a037, a039, a042 (Langofy), và là tên ad unit ở A028, a036,
a041. Giữ kiểu app đang có.

Màn Language Setting (`LanguageSettingScreen`, `LanguageType.Setting`) **không** áp tactic FO: không ngón
tay, popup, buffer.

---

## MO-32 — Bộ 55 mã ngôn ngữ

- **Yêu cầu:**
  - Màn chọn ngôn ngữ có đủ 55 mã của sheet: `en, fr, in, pt, es, hi, it, ms, ja, ko, de, ar, fa, ru,
    zh, tr, cs, nl, vi, hu, ro, pl, bg, el, sk, da, iw, hr, sl, sv, ca, uk, th, no, fi, ms-BN, ms-MY,
    ms-SG, ms-ID, ur-IN, ur-PK, bn, km, my, az, uz, gu, ta, te, mr, kn, or, ml, sq, id`.
  - `in` và `id` cùng là tiếng Indonesia → chỉ hiện **1 dòng** (sheet chấp nhận a016 chỉ có `in`). List
    thực tế là **54 dòng**.
  - Mã có vùng là dòng riêng, hiện tên vùng kèm tên ngôn ngữ.
- **Nghiệm thu:**
  - Đủ 54 dòng, không có 2 dòng trùng tên.
  - Chọn từng mã → app đổi ngôn ngữ, không crash. Mã chưa có bản dịch riêng thì rơi về
    `values-<ngôn ngữ gốc>` hoặc tiếng Anh.
  - `ar`, `fa`, `iw`, `ur-*` lật layout RTL.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:** `common/LanguageManager.kt` — `LanguageManager.languages` (danh sách mã viết trong
  companion).
  - **Lệch:** có 48 mã. Thiếu `in` (đang comment, giữ `id`), `ms-BN`, `ms-MY`, `ms-SG`, `ms-ID`, `ur-IN`,
    `ur-PK`, `my`. Thừa `ur` (không vùng).
  - `listFlagMap` / `flagForCode` đã có cờ cho các mã vùng. `values-my` đã có string nhưng `my` chưa lên
    list. `gridLanguages` là code chết (không ai gọi).
  - Nguồn đủ mã nhất: a016 `domain/language/LanguageManager.kt` — `CODES_NO_SORT`. Có đủ mã vùng và `my`,
    dùng `in` thay `id`; thừa `en-SG`, `pa`, `as`, `mai` (bỏ khi lấy).
- **Cách làm:**
  1. Giữ list mã ở **một chỗ** trong `LanguageManager` của app, không rải trong UI. Đọc
     `LanguageManager.languages` ở A013 (bản hiện tại) để lấy khung, rồi bổ sung mã còn thiếu theo danh
     sách trên. Đã có `ur-IN` / `ur-PK` thì bỏ `ur` trơn.
  2. Mỗi mã cần: cờ (`flagForCode`), tên theo ngôn ngữ máy (`name`), tên bản địa (`nameBase`; mã có vùng
     lấy tên quốc gia). Mã thiếu cờ thì thêm drawable, đừng để rơi về cờ mặc định.
  3. Resource: mã vùng dùng chung `values-ms`, `values-ur`. Giữ cả `values-in` lẫn `values-id` như A013.
     Thiếu bản dịch thì chạy skill `localize-android`.
  4. App không xtechads / XML: list chỉ là dữ liệu, áp y hệt.
- **Bẫy:**
  - Thêm cả `in` lẫn `id` → 2 dòng "Indonesia".
  - Trên Android, `Locale.getLanguage()` trả mã cũ (`in`, `iw`, `ji`), còn `toLanguageTag()` trả mã mới
    (`id`, `he`, `yi`). So khớp mã máy phải xử lý cả hai (MO-33).
  - Mã vùng viết dạng `ms-BN` (gạch ngang) thì `Locale.forLanguageTag` mới hiểu.
- **QC:** cuộn hết list, đếm 54 dòng, so với danh sách. Chọn `ms-BN`, `ur-PK`, `my`, `id` → UI đổi, không
  văng. Máy tiếng Ả Rập → RTL.

## MO-33 — Ngôn ngữ máy là mặc định và đứng đầu list

- **Yêu cầu:**
  - Lần đầu mở app, khi user chưa chọn: app hiển thị theo ngôn ngữ máy, không tự ép ngôn ngữ nào.
  - Trong list, ngôn ngữ máy đứng **đầu** (theo giải thích của MO trên sheet). Ngôn ngữ máy không có trong
    list → `en` đứng đầu.
  - Chỉ ghi `languageSelected` khi user xác nhận ở Alt.
- **Nghiệm thu:** máy tiếng Việt → dòng đầu là tiếng Việt; máy Indonesia → Indonesia; máy Hebrew → `iw`;
  máy `ur-PK` → `ur-PK`; máy dùng ngôn ngữ ngoài list → `en`. Trước khi chọn, chữ trong app theo ngôn ngữ
  máy.
- **SDK:** Không có — làm ở tầng app. `languageSelected` là pref có sẵn của SDK (`XtechSharedPref`).
- **Chuẩn A013:**
  - `LanguageManager.languages`: sau khi sort, tìm mã trùng `Locale.getDefault().toLanguageTag()`; không có
    thì trùng `Locale.getDefault().language`; không có nữa thì `en`. Đưa mã đó lên index 0.
  - `MainActivity.attachBaseContext` gọi `LanguageManager.wrapContextWithLocale(newBase,
    prefs.languageSelected)`; giá trị rỗng → giữ nguyên context, tức app theo máy. `onAttachedToWindow`
    gọi `updateLanguage`, hàm này chỉ áp khi `languageSelected` hợp lệ. Activity phụ (`LockScreenActivity`,
    `PermissionTutActivity`) cũng wrap như vậy.
  - `updateLanguage` log 1 lần event `language_default_<mã ngôn ngữ máy>`.
  - **Lệch:** máy tiếng Indonesia trả `language` = `in`, tag = `id-ID`. List A013 chỉ có `id` → không khớp
    → `en` lên đầu, `resolveDefaultLanguage()` cũng trả `en`. a016 không dính vì list dùng `in`. a027
    (`deviceLanguage`) và A045 (`codes`) dính giống A013.
- **Cách làm:**
  1. Hàm chọn mã máy, thử lần lượt: (a) tag đầy đủ (`ur-PK`, `ms-SG`); (b) phần trước dấu `-` của
     `toLanguageTag()` (`id`, `he`); (c) `Locale.getLanguage()` (mã cũ `in`, `iw`); (d) `en`. Đọc
     `LanguageManager.languages` và `resolveDefaultLanguage` ở A013 (bản hiện tại) rồi thêm bước (b). Tốt
     hơn nữa: chuẩn hoá cặp `in`/`id`, `iw`/`he`, `ji`/`yi` về đúng mã đang có trong list.
  2. Tính list một lần trước khi hiện màn (A013 dùng `lazy` trong companion), đưa mã máy lên đầu.
  3. Mọi Activity có UI: `attachBaseContext` wrap theo `languageSelected` (rỗng = giữ máy).
  4. Chỉ ghi `languageSelected` ở bước xác nhận của Alt. a034 ghi ngay lúc tap ở màn normal → user thoát
     giữa chừng vẫn bị đổi ngôn ngữ; đừng làm theo.
- **Bẫy:**
  - `lazy` tính theo `Locale.getDefault()` của lần đọc đầu. `wrapContextWithLocale` gọi `Locale.setDefault`,
    nên ở màn Setting của user cũ, ngôn ngữ đang dùng lên đầu thay vì ngôn ngữ máy. Chấp nhận được, FO
    không bị ảnh hưởng.
  - Dời ngôn ngữ máy bằng `language_oder` (DEV-6) là ngoại lệ có chủ ý; mặc định phải ở đầu list.
- **QC:** đổi ngôn ngữ **của máy** trong Settings (không dùng per-app locale) sang vi, id, he, ur-PK và một
  ngôn ngữ ngoài list (vd sw) → `pm clear` → mở app → kiểm dòng đầu và chữ trong app.

## MO-34 — Sắp xếp theo tên hiển thị

- **Yêu cầu:** Ngoài ngôn ngữ máy (và nhóm ưu tiên DEV-6), các ngôn ngữ còn lại xếp A→Z theo **tên đang
  hiển thị**. Xếp xong trước khi màn hiện, không nhảy thứ tự sau khi render.
- **Nghiệm thu:** máy tiếng Anh: Albanian, Arabic, Azerbaijani, Bangla… đúng A→Z. Máy tiếng Việt: các dòng
  "Tiếng …" theo thứ tự chữ cái tiếng Việt. Không có dòng nào lệch chỗ vì chữ có dấu.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:** `LanguageManager.languages` sort bằng `name()` (`Locale.displayLanguage` theo locale mặc
  định), so sánh chuỗi thường, **trước** khi đưa mã máy lên đầu. `reorderByPriority` /
  `moveSystemLanguage` giữ nguyên thứ tự phần còn lại. Dòng hiển thị in đậm `nameBase`, kèm `(name)`.
- **Cách làm:**
  1. Sort một lần, trước bước chèn mã máy và mã ưu tiên. Đọc `LanguageManager.languages` ở A013 (bản hiện
     tại).
  2. So sánh bằng `java.text.Collator` thay vì `compareTo`, để chữ có dấu (Ả, É, Č…) không bị đẩy xuống
     cuối. Nguồn: A045 `domain/language/LanguageManager.kt` — `codes` sort bằng `Collator` trên
     `displayName`.
  3. Khoá sort phải là chuỗi user nhìn thấy ở đầu dòng.
- **Bẫy:** sort theo `name` nhưng dòng lại in đậm `nameBase` (A013 đang vậy). Với máy không phải tiếng Anh,
  user thấy chữ đầu dòng không theo A→Z. Chọn 1 trong 2: sort theo chuỗi in đậm, hoặc in đậm `name`.
- **QC:** máy en và máy vi → chụp list, kiểm thứ tự. a016 là ví dụ chưa sort (sheet ghi 0).

## DEV-6 — Thứ tự: ngôn ngữ máy → tối đa 6 ưu tiên RC → còn lại

- **Yêu cầu:** List = [ngôn ngữ máy] + [tối đa **6** mã từ RC, giữ thứ tự UA ưu tiên; bỏ mã không có trong
  list, mã trùng, mã trùng ngôn ngữ máy] + [phần còn lại theo MO-34].
- **Nghiệm thu:** RC có 8 mã hợp lệ → chỉ 6 mã đầu đứng sau dòng máy. RC rỗng hoặc sai định dạng → list như
  MO-33/34. Mã RC trùng ngôn ngữ máy không bị lặp.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:** `LanguageContent` — `orderedLanguages` = `LanguageManager.reorderByPriority(languages,
  prefs.priorityLanguages)`; nếu bật `enable_new_language_selection_ui` thì thêm
  `LanguageManager.moveSystemLanguage(…, language_oder − 1)`. `reorderByPriority` giữ mã máy ở đầu, lọc mã
  ưu tiên có trong list, khác mã máy, không trùng.
  - **Lệch:** không cắt 6 (RC dài bao nhiêu đẩy lên bấy nhiêu). Default `priority_languages` rỗng.
- **Remote config:**
  - `priority_languages` — String CSV, default `""`, vd `en,hi,pt,es,ar,fr`. Alias:
    - a044 cùng tên, default `en,pt-BR,hi,de`; a027 cùng tên, default 10 mã `ar,hi,en,uk,fr,bn,ru,pt,th,es`.
    - A045, a034: `language_config.priority_languages` (mảng JSON; token `system` = vị trí ngôn ngữ máy;
      default A045 `system,en,pt,hi,de`).
    - a037, a042: `language_config.order`.
    - a033: `top_languages` (String CSV, default `en,hi,pt,vi,bn,pl,in,es,uk,tw,fr`).
  - `enable_new_language_selection_ui` — Boolean, `false`: bật header mới (icon tick thay chữ Done) và cho
    phép dùng `language_oder`.
  - `language_oder` — Long, `0`: vị trí 1-based của ngôn ngữ máy; ≤ 1 = đầu list. Tên sai chính tả đã phát
    hành, không sửa. Alias:
    - a027 `language_order` (default `4`). Comment trong code a027 nói đây là tên key trên RC của a013 →
      **cần MO xác nhận key thật trên Firebase a013**.
    - a047 `language_config.default_language_index` (default `1`).
- **Cách làm:**
  1. Thêm `priority_languages` vào SharedPrefs, hoặc thêm field vào nhóm JSON `language_config` nếu app gom
     RC theo nhóm.
  2. Hàm reorder trong `LanguageManager`: tách mã máy → lọc mã ưu tiên hợp lệ → **cắt 6** → nối phần còn
     lại. Đọc `LanguageManager.reorderByPriority` ở A013 (bản hiện tại), thêm bước cắt. Đặt số 6 thành hằng
     tên `MAX_PRIORITY_LANGUAGES` để `audit.py` nhận ra.
  3. Gọi ở composable list, tính 1 lần (`remember`), như `LanguageContent.orderedLanguages`.
  4. Chỉ hỗ trợ dời ngôn ngữ máy (`language_oder`) khi MO yêu cầu. Dời thì dời cả ngón tay (MO-36).
- **Bẫy:** cắt 6 **sau** khi lọc mã hợp lệ. Mã RC không có trong list bị bỏ qua im lặng. List dùng chung
  cho màn Setting, nên user cũ cũng thấy thứ tự UA.
- **QC:** RC `priority_languages=fr,de,ja,ko,it,es,pt,ar` → `pm clear` → mở app 2 lần → sau dòng máy đúng
  `fr,de,ja,ko,it,es`. Thêm mã trùng ngôn ngữ máy → không lặp.

## MO-35 — Tách 2 màn Language và Language Alt (2 ads)

- **Yêu cầu:** FO có 2 màn liền nhau, nhìn như một. ScrLanguage (native `language`, chưa chọn) → user tap 1
  dòng → **sang ngay** ScrLanguageAlt (dòng đó được chọn sẵn, native `language_alt` là ad mới) → Done mới
  áp ngôn ngữ và đi tiếp. Mục đích: 2 impression.
- **Nghiệm thu:**
  - Tap 1 dòng ở màn 1 → sang màn 2, không cần bấm Done; dòng đó đang được chọn.
  - Native màn 2 hiện gần như ngay (đã preload), placement `language_alt`.
  - Back ở màn 2 không quay về màn 1.
- **SDK:** Một phần — `NativeBannerGroupView(placement)`; placement → nameSpace khai trong `ads_config`.
- **Chuẩn A013:**
  - `AppNavigation.kt`: entry `AppDestination.ScrLanguage` → `LanguageFOScreen`;
    `AppDestination.ScrLanguageAlt(lang)` → `LanguageAltScreen`.
  - `LanguageFOScreen`: tap → `navigateTo` tới `ScrLanguageAlt(code)` với `popupTos` = `ScrLanguage`; mỗi
    lần resume gọi `nativeLangAlt.loadAd` (preload).
  - `LanguageContent` chọn placement theo `LanguageType`: `Normal` → `language`, `Alternative` →
    `language_alt`, `Setting` → `banner_all`.
  - `nativeLang` được preload từ màn trước qua `AdsManager.preloadAdsFO` → `loadLanguageAds`.
- **Placement / tracking:**
  - `language`, `language_alt` (chuẩn A013; a027, a014, a033, a034, a044, a045, a047 cùng tên). Alias
    `native_lang` / `native_lang_alt` (a016, a037, a039, a042). a016 có thêm `native_custom_lang(_alt)`
    cho biến thể RC `language_ad_variant`.
  - `screen_show` với `ScrLanguage` / `ScrLanguageAlt`. SDK tự bắn `iaa_*` kèm `placement`.
- **Cách làm:**
  1. 2 destination: Language (không tham số) và LanguageAlt(mã). Hai kiểu đều được: 2 entry top-level
     (A013), hoặc NavDisplay lồng dùng chung ViewModel (A045 / a044 `ui/screen/language/LanguageNavigation.kt`,
     tắt hết transition để user không thấy đổi màn).
  2. Dùng chung 1 composable UI, khác placement và trạng thái chọn (A013 `LanguageContent` + `LanguageType`).
  3. Màn 1 preload `language_alt`; màn đứng trước Language preload `language`.
  4. Tap ở màn 1 → navigate sang Alt, pop màn 1.
  5. `ads_config`: 2 placement trỏ tới 2 nameSpace riêng (2 ad unit). Xem `app/config/ads_config.json` của
     A013.
  - Không SDK (A028, a036, a041): 2 `NativeAdUnit` riêng (A028 `ads/AdsManager.kt` — `nativeLang`,
    `nativeLangAlt`), hiển thị bằng `NativeView` của app.
  - XML/Fragment: 2 destination Nav2 (`navigate` + `popUpTo`), hoặc 1 Fragment đổi state + 2 ad view.
- **Bẫy:** không preload `language_alt` → Alt hiện shimmer. Animation chuyển màn làm lộ "màn mới" (A045 tắt
  transition). 2 placement chung 1 nameSpace vẫn chạy (unit cache theo placement) nhưng MO không đo riêng
  được.
- **QC:** logcat `iaa_`: màn 1 có impression `language`; tap → impression `language_alt` gần như tức thì.
  Back ở Alt không về màn 1.

## MO-36 — Ngón tay gợi ý chọn ngôn ngữ máy + chặn back

- **Yêu cầu:**
  - Ở ScrLanguage, user chưa chọn sau **2 giây** (theo sheet) → hiện ngón tay nhấp nháy chỉ vào dòng ngôn
    ngữ máy.
  - Back không thoát app, và nên hiện ngay ngón tay (sheet: "handle backpress: show tooltips"). Hành vi back
    đầy đủ ở MO-86.
  - User chọn xong thì không còn ngón tay (màn chuyển sang Alt).
- **Nghiệm thu:** không chạm gì → sau N giây có ngón tay đúng dòng máy. Back → app không thoát. Click native
  rồi quay lại → ngón tay hiện ngay.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:**
  - `LanguageFOScreen`, trong `LifecycleResumeEffect`: preload `language_alt` → chờ 3 giây →
    `adsManager.clickedLanguage = true`. Callback `AdsManager.nativeLang.onClicked` cũng bật
    `clickedLanguage`.
  - `LanguageContent` truyền `showPoint` cho `LanguageListItem`: index 0 (UI cũ) hoặc index
    `language_oder − 1` (UI mới). Ảnh `R.drawable.img_click`, scale 0.9↔1.1 lặp 1,5 giây, canh phải dòng.
  - Back: `BackHandler` rỗng (chỉ nuốt).
  - **Lệch:**
    - 3 giây (sheet 2 giây), cứng, không có RC.
    - Đếm từ lúc resume; cuộn list không tính là thao tác.
    - Back không hiện gợi ý.
    - UI mới với `language_oder = 0` → index −1 → **ngón tay không bao giờ hiện**.
- **Remote config:** A013 chưa có. Đề xuất `language_hint_delay_second` — Long, giây, default `2` (tên lấy
  từ A045, A045 default `5`). Alias:
  - a034 `delay_show_tooltips` (ms, `2000`) + `language_config.finger_position` (1-based, `2`).
  - a014 `time_show_tooltips_language` (giây, `4`, cộng dồn qua các lần resume).
  - A045 `language_config.finger_position`. a044 cứng 3 giây. a016 hiện ngay, không chờ.
- **Placement / tracking:** không có event riêng.
- **Cách làm:**
  1. State `showFingerHint` của màn Language normal: bật sau delay RC tính từ lúc resume; tắt khi chọn.
     Đọc `LanguageFOScreen` và `LanguageContent` / `LanguageListItem` ở A013 (bản hiện tại).
  2. Vị trí: dòng của mã máy **sau** reorder (DEV-6). Đừng cứng index 0 nếu cho dời vị trí.
  3. Bật ngay khi: click native `language` (như `nativeLang.onClicked` ở A013), hoặc khi back.
  4. Back: chặn bằng `BackHandler` + `PredictiveBackHandler` (A013 `GeneralBackHandler`).
  5. Asset: `img_click` (ảnh) hoặc Lottie (A045 `anim_finger_click`, a016 `ic_finger_touch`).
  - XML: `lifecycleScope` + `repeatOnLifecycle(STARTED)` + `delay`; animation bằng `ObjectAnimator`.
- **Bẫy:**
  - Cờ hint đặt ở `AdsManager` (global, kiểu A013) thì phải reset trong `resetState`.
  - Ngón tay không được đè lên native hoặc nút CTA (policy).
  - Delay chạy bằng `rememberCoroutineScope` không bị huỷ khi pause (vô hại vì chỉ bật cờ).
- **QC:** mở FO, không chạm, bấm giờ → ngón tay đúng dòng máy sau N giây. RC = 5 → 5 giây. Back 3 lần →
  không thoát. App có `enable_new_language_selection_ui` thì thử `language_oder` = 0 và 3.

## MO-86 — Back ở màn Language

- **Yêu cầu:** Back (phím back và vuốt / predictive back) ở 2 màn Language **không thoát app**:
  - Alt: hiện nút **Save** to (full width, màu chính, có bàn tay Lottie) ngay trên native, kèm bàn tay ở nút
    Done/tick. Bấm Save = Done.
  - Normal (chưa chọn): popup "Continue with <ngôn ngữ máy>?" có native. Confirm → sang Alt với ngôn ngữ
    máy (giữ đủ 2 ad). Cancel → ở lại.
- **Nghiệm thu:** back ở Alt → nút Save hiện, bấm → đi tiếp đúng ngôn ngữ. Back ở Normal → popup có native.
  Android 14+ vuốt cạnh cũng vậy. Không lần nào thoát app.
- **SDK:** Không có — làm ở tầng app.
- **Chuẩn A013:**
  - Alt: `LanguageAltScreen` dùng `GeneralBackHandler` (back thường + predictive) → log `button_click`
    `BtnBack` (`ScrLanguageAlt`) và bật `showSaveHint`. `LanguageContent` hiện `SaveHintButton` (`BtnSave`,
    Lottie `R.raw.ani_click`) ở bottom bar trên native, thêm Lottie dưới tick.
  - **Thiếu:** màn Normal chỉ nuốt back, không popup. Nguồn cho popup ở màn Normal:
    - a033 `app/src/main/java/com/apptech/pdfreader/ui/activity/first_open/ui/language/LanguageScreen.kt`:
      back → `ConfirmLanguageDialog` với ngôn ngữ máy + native; Confirm → sang LanguageAlt.
    - a044 `ui/screen/language/LanguageViewModel.kt` — `onBack` → `ConfirmDeviceLanguageDialog`.
    - a016: RC `action_click_back_lang`.
- **Remote config:** A013 không có key. Alias:
  - a016 `action_click_back_lang` (Long: `1` popup trợ giúp, `2` popup "Start in this language?", `3` đứng
    yên; default `1`) + `confirm_popup_opt2_content` (`gotohome` = nút thứ 2 vào Home qua inter `inter_ob`;
    giá trị khác = Cancel).
  - a044 `confirm_popup_opt2_content` (`trynow` / `cancel`, default `cancel`); a047
    `language_config.confirm_popup_opt2_content` (default `cancel`).
- **Placement / tracking:** popup dùng `popup_lang` (MO-94). `button_click` `BtnBack`, `BtnSave`;
  `overlay_show` `OvlConfirmLanguage`.
- **Cách làm:**
  1. Alt: state `showSaveHint`; back → bật; UI gồm nút Save + Lottie. Đọc `LanguageAltScreen` và
     `LanguageContent` / `SaveHintButton` ở A013 (bản hiện tại).
  2. Normal: back → popup xác nhận ngôn ngữ máy (dùng lại `ConfirmLanguageDialog`), preload native popup
     trước khi mở. Confirm = đúng hành vi tap dòng ngôn ngữ máy.
  3. Chặn cả back thường lẫn predictive (`GeneralBackHandler`). XML: `onBackPressedDispatcher.addCallback`.
- **Bẫy:**
  - A013 bật `BackHandler` cho API ≤ 33 và `PredictiveBackHandler` cho API ≥ 34 → test cả hai.
  - Popup đang mở mà back → đóng popup, không mở popup chồng.
  - Nút Save màu chính nằm sát native → kiểm thêm DEV-9 (màu CTA).
- **QC:** Android 13 bấm phím back, Android 14 vuốt cạnh, ở cả 2 màn.

### Cơ chế chung: hành động sau khi click native (MO-37 / MO-38 / MO-39)

MO chọn **1 trong 3** hành động cho mỗi màn khi user click native rồi quay lại app: ẩn ad (MO-37), không
làm gì (MO-38), đi tiếp (MO-39). Luật chung cho mọi màn FO ở `inapp-ads.md` § MO-93; toast/noti toàn cục ở
`inapp-ads.md` § MO-79. Có 2 tầng cấu hình.

1. **RC theo màn (chuẩn A013):**
   - `action_clicked_native_lang` (ScrLanguage, default `tooltip`) và `action_clicked_native_lang_alt`
     (ScrLanguageAlt, default `next_screen`).
   - Giá trị: `tooltip` (mở `HelpSelectLanguageDialog` + event `<màn>_clicked_ad`), `clear_ads`,
     `next_screen`. Giá trị khác (`none`) = không làm gì.
   - Bắt click bằng callback `AdGroupUnit.onClicked` → bật cờ trong `AdsManager` (`clickedLanguageTooltip`,
     `clickedNativeLangAlt`) → xử lý trong `LifecycleResumeEffect` khi màn resume → xoá cờ.
2. **`ads_config` của SDK:** `nameSpaces[].actionClicked` = `none` | `tooltip` | `disable` | `reload` |
   `next_screen` | `custom`.
   - `NativeBannerGroupView` chỉ tự xử lý `disable` (reset + ẩn view tới khi rời màn, chặn auto reload) và
     `reload` (reset + load lại).
   - Các giá trị khác chỉ để app đọc qua `AdGroupUnit.actionClicked`. SDK có sẵn composable
     `NativeAdClickNextAction(unit, ActionClicked.NEXTSCREEN)`, chạy hành động lúc resume nếu unit đã bị
     click.
   - **Thiếu field → mặc định `reload`.**

**Chuẩn chọn:** dùng RC theo màn (tầng 1), vì MO chỉnh từng màn và cách này chạy được cả ở app không SDK.
Đồng thời đặt `actionClicked` của nameSpace `language` / `language_alt` = `none` (hoặc `tooltip`) để SDK
không reload/disable chồng lên. App đang theo kiểu SDK (A045, a034, a037: xử lý khi
`actionClicked == NEXTSCREEN`) thì giữ kiểu đó.

**Bẫy chung:**
- Đọc `AdGroupUnit.isClicked` ở app sẽ hụt nếu nameSpace để `reload` / `disable`: `NativeBannerGroupView`
  tự xoá cờ (ngay lúc click nếu màn còn resumed, hoặc lúc resume). A013 né bằng cờ riêng bật trong
  `onClicked`. a037 có wrapper `ads/NativeAdClickAction.kt` (`NativeAdClickAction`): nối callback cũ, xoá
  `isClicked` và chạy hành động lúc resume.
- `onClicked` / `onImpression` là 1 biến trên unit singleton (cache theo `placement:nameSpace`) → gán đè sẽ
  mất callback cũ.
- Toast/noti toàn cục sau click (`click_ad_action`, MO-48 / MO-79) vẫn chạy song song.
- Unit buffer (MO-98) cũng phải gắn `onClicked` (A013 `nativeLangAltBuffer` có gắn).

## MO-37 — Click ad → ẩn ad

- **Yêu cầu:** MO chọn "hide": click native ở Language/Alt rồi quay lại → native biến mất khỏi màn đó và
  không tự nạp ad mới cho tới khi rời màn.
- **Nghiệm thu:** RC = `clear_ads` → click ad → quay lại → vùng ad trống; không có `iaa_request` mới của
  placement đó trên màn này.
- **SDK:** Một phần — `actionClicked: "disable"` trong nameSpace (SDK reset + ẩn + chặn reload). Cách này áp
  cho mọi lần click, không theo RC màn.
- **Chuẩn A013:** `LanguageFOScreen`: `clear_ads` → `AdsManager.clearAdsLanguage()` (reset `nativeLang`).
  `LanguageAltScreen`: `clear_ads` → reset `visibleUnit` của `BufferedNative`.
  - **Lệch:** chỉ reset unit. `language` / `language_alt` trong `app/config/ads_config.json` để
    `reloadWhenResume: true`, nên view SDK thấy status `NONE` và `isClicked` đã bị xoá → **load lại ngay**.
    Thực tế thành "reload", không phải "hide".
- **Remote config:** `action_clicked_native_lang` / `action_clicked_native_lang_alt` = `clear_ads`. Cùng
  tên ở a014, a027, a028, a033, a041, a044. A045, a034, a037 không có key, dùng `ads_config.actionClicked`.
- **Placement / tracking:** `language`, `language_alt`; SDK `iaa_click`.
- **Cách làm:**
  1. Khi nhận `clear_ads`: bật cờ `adHidden` của màn (`rememberSaveable`) → ngừng compose
     `NativeBannerGroupView` + `reset()` unit để giải phóng. Đọc nhánh xử lý
     `action_clicked_native_lang(_alt)` trong `LanguageFOScreen` / `LanguageAltScreen` ở A013 (bản hiện
     tại) rồi sửa nhánh `clear_ads` như trên.
  2. Cách không cần code: MO đặt `actionClicked: "disable"` cho nameSpace đó.
  - Không SDK: `reset()` + `disable()` unit (A028 `AdsManager.clearAdsLanguageAlt`).
- **Bẫy:** reset mà không ẩn → SDK reload (như trên). Buffer bật thì phải ẩn cả unit đang hiện lẫn unit dự
  phòng (MO-98).
- **QC:** RC alt = `clear_ads`, `ads_config` giữ `reloadWhenResume: true` → click ad ở Alt → quay lại: ad
  phải mất; logcat không có `iaa_request placement=language_alt` mới.

## MO-38 — Click ad → không làm gì

- **Yêu cầu:** MO chọn "no action": quay lại sau click, màn giữ nguyên (ad đang hiện vẫn ở đó), không popup,
  không chuyển màn.
- **Nghiệm thu:** RC = `none` → click ad → quay lại: vẫn màn đó, không dialog, ad không đổi.
- **SDK:** Một phần — `actionClicked: "none"`.
- **Chuẩn A013:** giá trị không khớp `tooltip` / `clear_ads` / `next_screen` thì bỏ qua; không có nhánh
  `none` tường minh. `app/config/ads_config.json`: `language` = `tooltip`, `language_alt` = `none` (SDK
  không xử lý `tooltip`, nên tương đương `none`).
- **Remote config:** như MO-37, giá trị `none`.
- **Cách làm:** thêm nhánh `none` tường minh cho dễ đọc và dễ QC. Kiểm nameSpace có khai `actionClicked`.
- **Bẫy:** thiếu `actionClicked` trong `ads_config` → SDK mặc định `reload` → "không làm gì" thành reload.
- **QC:** RC `none` → click ad → quay lại: ad giữ nguyên, không có `iaa_request` mới (khi `isClicked` còn
  bật thì `reloadWhenResume` không chạy).

## MO-39 — Click ad → đi tiếp

- **Yêu cầu:** MO chọn "next":
  - Click native ở ScrLanguage → quay lại thì sang ScrLanguageAlt, chọn sẵn ngôn ngữ máy.
  - Click native ở ScrLanguageAlt → quay lại thì xác nhận ngôn ngữ đang chọn và sang màn kế (`language_next`).
- **Nghiệm thu:** đúng như trên ở cả 2 màn; ngôn ngữ được áp; không navigate 2 lần.
- **SDK:** Một phần — `ActionClicked.NEXTSCREEN` + `NativeAdClickNextAction`.
- **Chuẩn A013:** Alt: `action_clicked_native_lang_alt` (default `next_screen`) → hàm `onConfirm` trong
  `LanguageAltScreen` (lưu + `updateLanguage` + `navigateTo(nextLanguage)`).
  - **Thiếu:** ScrLanguage không có nhánh `next_screen` (chỉ `tooltip` / `clear_ads`). Nguồn:
    - a044 `ui/screen/language/LanguageViewModel.kt` — `onResumeFromAdClick` (đọc RC; `next_screen` ở màn
      normal → sang Alt).
    - a016 `ui/screen/language/LanguageScreen.kt` — hàm `onConfirm` (mã rỗng thì lấy mã đầu list = ngôn ngữ
      máy).
- **Remote config:** `action_clicked_native_lang` = `next_screen` (sang Alt); `action_clicked_native_lang_alt`
  (default `next_screen`). A045, a034: nameSpace `language_alt` trong `ads_config` để
  `actionClicked: "next_screen"`.
- **Cách làm:**
  1. Màn normal: thêm nhánh `next_screen` → navigate Alt với mã ngôn ngữ máy (đầu list sau reorder), y như
     tap.
  2. Màn Alt: `next_screen` → gọi đúng hàm xác nhận của nút Done.
  3. Navigate phải idempotent: A013 `common/NavigationUtil.kt` — `navigateTo` bỏ qua khi đích trùng class với
     đỉnh stack.
- **Bẫy:** popup confirm (MO-94) đang mở thì đóng trước khi navigate. Buffer: gắn `onClicked` cho cả unit
  buffer.
- **QC:** RC normal = `next_screen` → click ad màn 1 → quay lại: đang ở Alt, chọn sẵn ngôn ngữ máy. RC alt =
  `next_screen` → click ad ở Alt → quay lại: sang màn kế, UI đã đổi ngôn ngữ.

## MO-40 — Cấu hình layout native qua config

- **Yêu cầu:** MO đổi layout native của `language` / `language_alt` (và layout riêng cho ad Meta) bằng remote
  config, không cần release.
- **Nghiệm thu:** đổi `layout` trong RC `ads_config` → mở lại → native đổi giao diện. Key sai → về layout mặc
  định, không crash.
- **SDK:** Có — `nameSpaces[].adunits[].layout` / `layoutMeta`, hoặc ghi đè theo vị trí bằng
  `placements[].layout` / `layoutMeta` (vị trí thắng adunit). Key hợp lệ: `xTechSDK/docs/ADS_CONFIG_JSON_GUIDE.md`
  §7.3 (enum `AdLayout`). Thiếu hoặc sai key → dùng `defaultNativeLayout` của `NativeBannerGroupView`, không
  báo lỗi.
- **Chuẩn A013:** `LanguageContent` gọi `NativeBannerGroupView` chỉ với placement, layout hoàn toàn do
  config. `app/config/ads_config.json`: nameSpace `language` / `language_alt` để `layout` =
  `native_med_4_3_media_left`. Sheet ghi a013 = 0 là snapshot cũ; code hiện tại đã đáp ứng qua SDK.
- **Remote config:** `ads_config` (JSON). Schema cũ (ảnh tham chiếu trên sheet, dùng ở app không SDK):
  `nativeAds.positions[]` với `layoutKey` `layout_native_language` / `layout_native_language_alt` và
  `layoutKeyMeta` `…_meta` (A028 `ads/config/AdsConfig.kt` — `Position`; `AdsManager.layoutNative`).
- **Cách làm:**
  1. xtechads: gọi `NativeBannerGroupView(placement = …)`, không cứng layout ở call site (chỉ dùng
     `defaultNativeLayout` làm fallback); khai `layout` trong `ads_config`.
  2. Không SDK: đọc `layoutKey` theo nameSpace rồi map ra layout res (A028 `AdsManager.layoutNative`).
- **Bẫy:** gõ sai key không báo lỗi. Ad Meta cần `layoutMeta` riêng. Theme (DEV-9) quyết định màu, layout
  chỉ quyết định bố cục.
- **QC:** đổi `layout` nameSpace `language_alt` sang `native_med_16_9_a` trên Firebase → `pm clear` → mở app
  2 lần → kiểm giao diện Alt.

## MO-41 — Cấu hình reload native qua config

- **Yêu cầu:** MO bật/tắt việc nạp ad mới cho `language` / `language_alt` khi user quay lại màn (ra Home, đa
  nhiệm…), bằng config.
- **Nghiệm thu:** `reloadWhenResume: true` → ra Home rồi vào lại → impression mới. `false` → giữ ad cũ.
- **SDK:** Có:
  - `nameSpaces[].reloadWhenResume`: khi màn resume, load lại nếu ad đã impression và unit không đang ở trạng
    thái vừa bị click.
  - `adunits[].autoReloadOnImpression` (ms): tự load lại sau impression.
  - `adunits[].keepAdWaitLoading` (default `true`): giữ ad cũ trong lúc load.
  - `actionClicked: "reload"`: reload sau click.
- **Chuẩn A013:** `app/config/ads_config.json` — `language` / `language_alt` có `reloadWhenResume: true`;
  SDK xử lý trong `NativeBannerGroupViewImpl` (resume effect theo `isClicked`). Riêng Alt còn đổi ad khi đổi
  ngôn ngữ (MO-98).
- **Remote config:** `ads_config`. Alias: schema cũ `forceReload` (A028 `AdsConfigProvider.nativeForceReload`);
  key phẳng `reload_language` / `reload_language_alt` (a033, a036, a039, a041); a036/a039 có thêm
  `reload_custom_language`.
- **Cách làm:** xtechads chỉ cần config. Không SDK: trong view native, khi resume sau pause/stop mà cờ
  reload bật thì gọi `loadAd` (A028 `ads/adunit/natiive/view/NativeView.kt` — tham số `reloadAd`).
- **Bẫy:**
  - `reloadWhenResume` không chạy khi `isClicked` còn bật (actionClicked `none` / `tooltip`) → muốn reload sau
    click thì dùng `actionClicked: "reload"`.
  - `AdGroupUnit.loadAd()` không làm gì khi ad đang SUCCESS mà chưa impression, hoặc đang LOADING / TIMEOUT.
  - Docs SDK cũ (`xtechads/docs/ADS_MODULE_GUIDE.md`, changelog 2026-07-14) còn nhắc tham số `reloadWhenClick`
    của `NativeBannerGroupView`; source SDK hiện tại không còn tham số này.
- **QC:** bật/tắt `reloadWhenResume` → ra Home → quay lại → đếm `iaa_impression placement=language`.

## MO-98 — Buffer native Language Alt (đổi ad khi đổi ngôn ngữ)

- **Yêu cầu:** Mỗi lần user chọn một ngôn ngữ **mới** ở Alt → đổi sang native mới (impression mới) mà không
  nháy trống. Cách làm: nạp sẵn ad thứ 2 (buffer) rồi hoán đổi, có khoảng nghỉ tối thiểu giữa 2 lần đổi.
- **Nghiệm thu:**
  - Buffer bật: chạm 3 ngôn ngữ khác nhau, mỗi lần cách > 1 giây → 3 `iaa_impression placement=language_alt`
    với `ad_request_id` khác nhau, không thấy shimmer.
  - Chạm dồn trong thời gian < interval → không đổi thêm.
  - Buffer tắt: vẫn đổi ad (load lại unit đang hiện, ad cũ giữ nguyên trong lúc load).
- **SDK:** Một phần:
  - Unit thứ 2 cùng waterfall: `AdGroupUnit.of(placement, nameSpace = <nameSpace của placement>)` (cache
    theo `placement:nameSpace`) + `NativeBannerGroupView(placement, nameSpace = …)`. KDoc của
    `NativeBannerGroupView` mô tả đúng pattern này.
  - `AdGroupUnit.onImpression`, `statusFlow`, `keepAdWaitLoading`.
  - Changelog SDK 2026-10-06: ad bị thay được destroy khi view cuối nhả ra.
- **Chuẩn A013:**
  - `ui/base/BufferedNative.kt` — class `BufferedNative` (`visibleUnit`, `spareUnit`, `nameSpace`,
    `showNext`, `swap`) + `rememberBufferedNative`.
  - `ads/AdsManager.kt` — `nativeLangAltBuffer` (tạo bằng `bufferUnit()`), `resetNativeLangAlt`.
  - `LanguageAltScreen` gọi `showNext` khi chạm ngôn ngữ mới, truyền `nameSpace` cho `LanguageContent` →
    `NativeBannerGroupView`.
  - Logic:
    - Không buffer: `showNext` (đã qua `minIntervalMs`) → `loadAd` lại unit đang hiện.
    - Có buffer: unit đang hiện có impression → nạp unit kia. `showNext`: unit dự phòng đã SUCCESS → swap
      ngay; chưa xong → đặt `pendingSwap`, swap khi xong và đủ interval.
    - `onImpression` gắn trong `DisposableEffect`, gỡ khi rời màn (unit là singleton).
  - Sheet ghi a013 = 0 là snapshot cũ. Code có sẵn, MO phải bật `buffer_language_alt`.
- **Remote config:**
  - `buffer_language_alt` — Boolean, `false`.
  - `min_ad_interval_language_alt` — Long, ms, `1000`. Giá trị 1–999 được hiểu là giây ×1000
    (`asIntervalMs` trong `SharedPrefs`).
  - Alias: cùng tên ở a027, a033, a042. a037 `language_config.buffer_alt` (default `true`) +
    `language_config.min_ad_interval_alt` (`1000`). Màn Select dùng `buffer_select_alt` /
    `min_ad_interval_select_alt` (select.md § MO-43).
- **Placement / tracking:** `language_alt` (2 unit cùng placement → log cùng tên placement).
- **Cách làm:**
  1. Tạo unit buffer: cùng placement, `nameSpace` override = tên nameSpace của placement.
  2. Dùng chung 1 state holder cho Language Alt và Select Alt. Đọc `BufferedNative` /
     `rememberBufferedNative` ở A013 (bản hiện tại).
  3. Gắn `onClicked` cho cả unit buffer (MO-37..39).
  4. Reset cả 2 unit khi rời luồng (A013 `resetNativeLangAlt`, gọi từ `resetAdsBeforeSelect`).
  - Không SDK: 2 instance `NativeAdUnit` cùng id; view bind theo cờ đang hiện unit nào.
- **Bẫy:**
  - `AdGroupUnit.loadAd()` bỏ qua khi status là SUCCESS (chưa hết hạn), LOADING hoặc TIMEOUT. Vì vậy chế độ
    không buffer chỉ đổi được ad sau khi ad đang hiện đã impression. Muốn ép thì `reset()` trước `loadAd()`
    (fix night-dev a033), đổi lại view trống trong lúc load.
  - Buffer làm gấp đôi request → MO cân fill rate / show rate.
  - `rememberBufferedNative` đọc cờ buffer 1 lần lúc vào màn.
- **QC:** bật buffer → chạm đổi ngôn ngữ → logcat `iaa_request` / `iaa_impression placement=language_alt` có
  `ad_request_id` khác nhau. Chạm 5 lần trong 1 giây → chỉ đổi 1 lần.

## MO-94 — Chạm lại ngôn ngữ đã chọn ở Alt → popup confirm có native

- **Yêu cầu:**
  - Ở Alt, chạm lại ngôn ngữ **đã từng chạm** (kể cả ngôn ngữ mang từ màn 1) → popup "Confirm Language —
    Continue with X?" (Cancel / Confirm / nút đóng), có native riêng. Confirm = Done. Cancel = ở lại, X vẫn
    được chọn.
  - Chạm ngôn ngữ mới → chỉ đổi chọn + đổi native Alt.
  - Click ad trong popup (hoặc ad Alt) → xác nhận luôn hoặc tự next (theo sheet).
- **Nghiệm thu:** chạm EN (mang từ màn 1) → popup + native. Chạm FR (mới) → không popup. Chạm FR lần 2 →
  popup. Confirm → đi tiếp với FR.
- **SDK:** Một phần — native trong popup là `NativeBannerGroupView(placement)`; logic ở app.
- **Chuẩn A013:**
  - `LanguageAltScreen`: tập `tappedLanguages` khởi tạo bằng mã từ màn 1. Mã đã có → `nativePopupLang.loadAd`
    + mở popup. Mã mới → thêm vào tập + `BufferedNative.showNext`.
  - `ui/base/dialog/ConfirmLanguageDialog.kt` — `ConfirmLanguageDialog` với placement `popup_lang`: overlay
    `OvlConfirmLanguage`, nút `BtnCancel` / `BtnConfirm` / `BtnClose`, không đóng khi chạm ra ngoài.
  - Không có RC bật/tắt. Click ad trong popup chưa có xử lý.
  - Biến thể ở app khác: a027, A014 chỉ hỏi khi chạm lại **đúng dòng đang chọn** (callback `onReselect` của
    `LanguageContent`); A045, a037 hỏi khi chạm lại bất kỳ dòng đã từng chạm (`tappedCodes`, `visitedCodes`)
    như A013. Cả hai đều đạt sheet; A013 bao trùm hơn.
- **Remote config:** A013 không có (luôn bật). Alias: `confirm_language` (Boolean, `true`; a014, a027, a034,
  a042, a047); A045 `confirm_same_language_alt` (`true`); a039 `time_show_show_confirm_lang`.
- **Placement / tracking:**
  - `popup_lang` (A013). Alias: `confirm_language` (a014, a027, a033, a034), `native_popup_lang` (a016),
    `native_popup_confirm` (a044), `native_pop_up` (a037). A045 dùng placement `language_alt` với nameSpace
    override (unit thứ 2).
  - `overlay_show` `OvlConfirmLanguage`; `button_click` theo nút, kèm `overlay_name`.
- **Cách làm:**
  1. Tập mã đã chạm trong state của màn Alt, khởi tạo với mã từ màn 1.
  2. Popup dùng chung `ConfirmLanguageDialog`: tiêu đề, dòng phụ chứa tên ngôn ngữ, native, 2 nút.
  3. Preload native popup sớm (lúc vào Alt, hoặc ở màn 1 như a016 `LanguageScreen`), không chờ lúc mở.
  4. Click native trong popup → quay lại thì tự Confirm: a037 `ui/screen/language/LanguageAltScreen.kt` dùng
     `NativeAdClickAction` cho `nativePopup`.
  5. (Tuỳ chọn) RC `confirm_language` để MO tắt popup.
- **Bẫy:** A013 chỉ load native popup lúc mở → popup hiện shimmer. Popup đang mở mà ad Alt bị click với
  `next_screen` → đóng popup trước khi navigate. Popup không dùng chung unit với native Alt đang hiện (2 view
  cùng 1 ad).
- **QC:** đi đúng chuỗi nghiệm thu; logcat `iaa_impression placement=popup_lang`.

## MO-42 — Remote config màn kế sau Language

- **Yêu cầu:** MO chọn màn sau Language Alt: `onboard` / `select` / `iap` / `home`, không cần release.
- **Nghiệm thu:** mỗi giá trị → đúng màn, ad của màn đó đã preload. Giá trị lạ → về mặc định. Không lặp về
  Language.
- **SDK:** Một phần — `ads_config.navigationFlow` (danh sách `{key, value}`), đọc bằng
  `AdsConfigProvider.getNavigationValue(key, default)`; routing ở app.
- **Chuẩn A013:** `ads/AdsManager.kt` — `nextLanguage` = `getNextDestination(FONavKey.Language)`;
  `FONavKey.Language` có key `language_next`, default `select`, fallback `ScrFileTypeSelect`; `FONavValue` =
  `language` / `select` / `onboard` / `home`. `LanguageAltScreen` preload bằng `loadNativeNextLanguage`
  (dùng chung `nextLanguage`, nên preload và navigate không lệch nhau).
  - **Lệch:** A013 đọc key phẳng `language_next` qua `prefs.getString`, **không** đọc `navigationFlow`
    (mảng `navigationFlow` trong `app/config/ads_config.json` của A013 bị bỏ qua). Không có giá trị `iap`.
    Không chặn trường hợp trỏ về chính nó.
- **Remote config:** `language_next` — String, default `select` (A013). Alias:
  - `navigationFlow.language_next` (a028, a036, a039, a044, a045; default `onboard`).
  - a016 `navigationFlow.languageNext` (camelCase, default `onboard`).
  - a041 key phẳng `language_next`.
  - Giá trị thêm: `iap` (a016 `FONavValue.Iap`), `paywall` (a028), `uninstall` (a045).
- **Cách làm:**
  1. Một hàm `getNextDestination(key)` + enum key / value / default / fallback. Đọc
     `AdsManager.getNextDestination`, `FONavKey`, `FONavValue` ở A013 (bản hiện tại).
  2. App mới đọc qua `navigationFlow` (SDK). App đã phát hành giữ kiểu đang dùng.
  3. Dùng cùng `nextLanguage` cho preload (`preloadAdsFO`) và navigate.
  4. App có paywall trong FO thì thêm giá trị `iap`.
  5. Chặn self-loop: đích trùng màn hiện tại → fallback (a016 `AdsManager.getNextDestination`).
- **Bẫy:** sai kiểu tên (camelCase vs snake_case) → về default, không báo lỗi. A013 `new_onboard = true` làm
  Onboard luôn đi `ScrOnboardFeature` (bỏ qua `onboard_next`). Xem thêm `xTechSDK/docs_final/FO_ADS_FLOW.md`.
- **QC:** set lần lượt `language_next` = `onboard` / `select` / `home` / `iap` → hoàn tất Alt → đúng màn, ad
  màn đó có ngay.

## DEV-9 — Màu CTA native màn Language khác nút của app (policy)

- **Yêu cầu:** Nút CTA của native ở Language / Alt không được trùng màu (và kiểu) với nút của app ngay cạnh
  (Done, Save), để không bị coi là ad đội lốt nội dung app. Khác màu ngay từ đầu, hoặc khi user đã chọn ngôn
  ngữ (tức ở Alt).
- **Nghiệm thu:** CTA native ở Alt (và Normal nếu MO muốn) khác màu rõ với nút Save / Done; đổi được bằng
  config.
- **SDK:** Có:
  - `configs.themes[]` (`key`, `cta.bgColor`, `cta.textColor`, `cta.borderColor`, `cta.gradientColors`,
    `cta.rounded`…) + `placements[].theme`.
  - Theme resolve bằng `AdsConfigProvider.themeFor(placement)` và áp lúc populate (`NativeAdUtil.applyTheme`).
  - Placement không khai theme → dùng theme `default` (không có thì phần tử đầu).
- **Chuẩn A013:** **chưa đạt** ở config mặc định.
  - `app/config/ads_config.json` chỉ có theme `default` (CTA `#3F85F4`) và `native_full_t2c`; placement
    `language` / `language_alt` không khai `theme`.
  - Màu nút chính của app (`ui/theme/Color.kt` — `primary500Color` / `primaryColor500`) cũng là `#3F85F4` →
    CTA ad trùng màu `SaveHintButton` ngay phía trên.
- **Remote config:** `ads_config` (themes + placements).
- **Cách làm:**
  1. Không cần code: MO thêm một theme riêng (vd key `language_cta`) có `cta.bgColor` / `cta.textColor` tương
     phản với màu chính của app, rồi đặt `theme` của placement `language_alt` (và `language` nếu muốn "đổi từ
     đầu") trỏ tới key đó.
  2. Cần đổi động trong cùng một màn: tham số `bindExtra` của `NativeBannerGroupView` (chạy trong `update`
     của `AndroidView`) để chỉnh `callToActionView` theo state. Chỉ dùng khi config không đủ.
  3. Không SDK: chọn layout/kiểu có CTA khác màu (schema cũ có `type` / `typeMeta` filled/stroke) hoặc tô
     lại lúc populate.
- **Bẫy:** theme được nhớ theo placement → đổi RC chỉ ăn ở lần vào màn sau. SDK cũ không biết `themes`
  (rollout theo version SDK). App có theme sáng/tối (a037 `themedNative`) cần theme cho cả hai.
- **QC:** chụp màn Alt khi đang hiện nút Save → màu CTA ad khác rõ. Đổi `cta.bgColor` trên RC → `pm clear` →
  kiểm lại.

## CC-6 — Đổi màu CTA native màn Language khi chọn ngôn ngữ (trùng DEV-9)

- **Yêu cầu:** Trùng DEV-9 (catalog `duplicate_of: DEV-9`, nguồn sheet Crawl Competitor). Làm và nghiệm thu
  theo DEV-9.
- **SDK:** Có — xem DEV-9.
- **QC:** như DEV-9.

## DEV-8 — Nút Done ở Language Alt khoá khi chưa chọn (deprecated)

- **Yêu cầu:** Mục đã bỏ (PIC ghi "bỏ"). Với luồng 2 màn, Alt luôn có ngôn ngữ chọn sẵn nên Done luôn bấm
  được. Chỉ giữ: ở màn Normal (chưa chọn), Done/tick không cho đi tiếp.
- **Chuẩn A013:** `LanguageContent`: UI mới (`enable_new_language_selection_ui`) để tick xám, không bấm được
  cho tới khi có ngôn ngữ. UI cũ: chữ "Done" luôn bấm được; ở màn Normal bấm thì mở
  `HelpSelectLanguageDialog` (`LanguageFOScreen`). a028: Next mờ + popup thông báo.
- **Cách làm:** không làm mới. App còn nút Done ở màn Normal thì cho mở popup hướng dẫn như A013.

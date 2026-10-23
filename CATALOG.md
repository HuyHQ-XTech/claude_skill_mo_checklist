# MO checklist — bảng tra cứu

Sinh tự động từ `catalog.json` bằng `scripts/catalog.py render` — **không sửa tay**. Snapshot sheet "Checklist - MO New" ngày 2026-10-07. ID = `MO-<số dòng trong sheet>`; `DEV-<dòng>` = sheet "Checklist - Dev"; `CC-<dòng>` = sheet "Crawl Competitor" (ứng viên); `EXT-<TÊN>` = tactic MO đã làm theo ticket nhưng chưa có dòng trong sheet (không có MO-ID, nhận qua prompt).

Trạng thái: `active` = đang áp dụng · `candidate` = MO đang cân nhắc · `deprecated` = đã bỏ · `blocked-policy` = không làm vì vi phạm chính sách Play.

## Setup SDK / ID / tracking

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-5 | Billing IAP (xtechbilling / RevenueCat) | một phần | a013 | active |
| MO-6 | Đúng package name (applicationId) | không | a013 | active |
| MO-7 | AdMob App ID khai trong Manifest | không | a013 | active |
| MO-8 | UMP hiện được ở bản debug | có | a013 | active |
| MO-9 | UMP chạy trước khi load bất kỳ ad nào | có | a013 | active |
| MO-10 | initMobileAds chỉ chạy sau khi UMP xong | có | a013 | active |
| MO-11 | Facebook App ID / Client Token trong Manifest | một phần | a013 | active |
| MO-12 | Facebook SDK + mediation Meta | có | a013 | active |
| MO-13 | Facebook: track doanh thu ad và IAP | một phần | a013 | active |
| MO-14 | Adjust: track ad revenue (cần MO xác nhận còn dùng Adjust) | một phần | a013 | active |
| MO-15 | Adjust: track IAP revenue (cần MO xác nhận) | không | a013 | active |
| MO-16 | Firebase: Crashlytics, Remote Config, FCM | có | a013 | active |
| MO-17 | Remote Config có hiệu lực trước khi load ad | có | a013 | active |
| MO-18 | Firebase: event IAA / IAP in-house | một phần | a013 | active |
| MO-19 | MultiDex | không | a013 | active |
| MO-20 | Đổi layout native/banner qua RC (kể cả native Meta) | có | a013 | active |
| MO-100 | Init SDK theo SDK Integration Guide | có | a013 | active |
| EXT-RC-GROUP | Gộp key Remote Config theo màn vào parameter JSON (xxx_config) — ngoài sheet | không | a052 | active |

## Splash

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-21 | Splash riêng có logo app + progress bar | một phần | a013 | active |
| MO-22 | Consent đồng ý → init AdMob/Meta → load ads + noti | có | a013 | active |
| MO-23 | Consent từ chối → đẩy IAP (paywall) | một phần | a013 | active |
| MO-24 | Hiện UMP nếu cần, trước mọi hành động ở splash | có | a013 | active |
| MO-25 | Hỏi quyền notification ở splash nếu cần | không | a013 | active |
| MO-26 | Popup không có internet | một phần | a013 | active |
| MO-27 | Chờ Remote Config trước khi load ad splash (tuỳ chọn) | có | a013 | active |
| MO-28 | Không quay lại được màn splash | không | a013 | active |
| MO-29 | Chỉ rời splash khi ad splash đã show/fail | có | a013 | active |
| MO-30 | Remote config chọn màn sau splash | một phần | a013 | active |
| MO-31 | Preload 1 native màn kế khi splash có kết quả | có | a013 | active |
| MO-84 | Tối ưu thời gian splash (logic như A013) | một phần | a013 | active |
| MO-96 | Bật lại mạng ở splash → load + show ad rồi mới đi tiếp | có | a013 | active |
| MO-97 | Tối ưu init SDK cho splash | một phần | a013 | active |
| MO-99 | Tách ad unit splash new user / old user | không | a013 | active |
| DEV-3 | Init song song AppsFlyer, billing, Remote Config ở splash | có | a013 | active |

## Language (First open)

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-32 | Bộ 55 mã ngôn ngữ (in/id gộp 1 dòng → 54 dòng) | không | a013 | active |
| MO-33 | Ngôn ngữ máy là mặc định, đứng đầu list; app theo máy tới khi chọn | không | a013 | active |
| MO-34 | Sắp xếp ngôn ngữ theo tên hiển thị (A→Z) | không | a013 | active |
| MO-35 | Tách 2 màn Language và Language Alt (2 native) | một phần | a013 | active |
| MO-36 | Ngón tay gợi ý dòng ngôn ngữ máy sau 2s + chặn back | không | a013 | active |
| MO-37 | Click native Language/Alt → ẩn ad (clear_ads) | một phần | a013 | active |
| MO-38 | Click native Language/Alt → không làm gì (none) | một phần | a013 | active |
| MO-39 | Click native → đi tiếp: Language→Alt, Alt→màn kế | một phần | a013 | active |
| MO-40 | Cấu hình layout native Language/Alt qua ads_config | có | a013 | active |
| MO-41 | Cấu hình reload native Language/Alt qua ads_config | có | a013 | active |
| MO-42 | RC màn kế sau Language (language_next) | một phần | a013 | active |
| MO-86 | Back ở Language: Alt hiện nút Save to, Normal hiện popup confirm | không | a013 | active |
| MO-94 | Chạm lại ngôn ngữ đã chọn ở Alt → popup confirm có native | một phần | a013 | active |
| MO-98 | Buffer native Language Alt: đổi ad mới mỗi lần chọn ngôn ngữ mới | một phần | a013 | active |
| DEV-6 | Thứ tự: ngôn ngữ máy → tối đa 6 ưu tiên RC → còn lại | không | a013 | active |
| DEV-8 | Done ở Language Alt khoá khi chưa chọn (deprecated) | không | a013 | deprecated |
| DEV-9 | Màu CTA native màn Language khác màu nút của app (policy) | có | a013 | active |
| CC-6 | Đổi màu CTA native màn Language khi chọn ngôn ngữ (trùng DEV-9) | có | a013 | candidate |

## Select (First open)

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-43 | Tách Select và Select Alt (2 native) | một phần | a013 | active |
| MO-44 | Ngón tay/tooltip hướng dẫn chọn ở Select (+ khi back) | không | a013 | active |
| MO-45 | Click native Select/Alt → ẩn ad (clear_ads) | một phần | a013 | active |
| MO-46 | Click native Select/Alt → không làm gì (none) | một phần | a013 | active |
| MO-47 | Click native → đi tiếp: Select→Select Alt, Alt→màn kế | một phần | a013 | active |
| MO-48 | Click ad → toast nhắc user (toàn cục, xem MO-79) | một phần | a013 | active |
| MO-49 | Cấu hình layout native Select/Alt qua ads_config | có | a013 | active |
| MO-50 | Cấu hình reload native Select/Alt qua ads_config | có | a013 | active |
| MO-51 | RC màn kế sau Select (select_next) | một phần | a013 | active |
| DEV-10 | Select/Alt: phải chọn 1 mục mới đi tiếp (chưa chọn → tooltip) | không | a013 | active |
| CC-4 | Select sau Onboard, có native, chỉ chọn 1 loại (candidate) | một phần | a013 | candidate |

## Onboarding (First open)

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-52 | Nút back ở OB1 quay lại màn chọn ngôn ngữ | không | a013 | active |
| MO-53 | Hint vuốt/Next khi user đứng lâu ở OB1 | không | a013 | active |
| MO-54 | Sau click native onboarding: ẩn ad đã click (clear_ads) | một phần | a013 | active |
| MO-55 | Sau click native onboarding: không làm gì (none) | một phần | a013 | active |
| MO-56 | Cơ chế hành động sau click native onboarding (RC từng slot) | một phần | a013 | active |
| MO-57 | Native OB1: none / next page / has ads / finish sau click | một phần | a013 | active |
| MO-58 | Native OB2: none / next page / has ads / finish sau click | một phần | a013 | active |
| MO-59 | Native full-screen onboarding: action sau click + RC bật/tắt nút thoát | một phần | a013 | active |
| MO-60 | Native OB4 (trang cuối): none / next page / has ads / finish | một phần | a013 | active |
| MO-61 | Config layout native onboarding qua remote config | có | a013 | active |
| MO-62 | Config reload native onboarding theo từng trang | một phần | a013 | active |
| MO-63 | Config màn kế sau onboarding (select/language/iap/home) | một phần | a013 | active |
| MO-64 | Impression flow 1px: đứng OB1 có impression native OB1 + OB2 | không | a013 | active |
| MO-65 | Impression flow 1px: đứng OB2 có impression OB1 + OB2 + full-screen | không | a013 | active |
| MO-66 | Impression flow 1px: đứng FSN có impression OB2 + OB4 + full-screen | không | a013 | active |
| MO-67 | Impression flow 1px: đứng OB4 có impression OB4 + full-screen | không | a013 | active |
| MO-92 | Vuốt tiếp ở trang onboard cuối vẫn vào màn kế (Home) | không | a013 | active |
| EXT-NATIVE-POOL | Native pool dùng chung luồng Language/Onboard (mượn ad, 1 lượt load) — ngoài sheet | một phần | a052 | active |

## Notification

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-4 | Win-back noti (dòng Protect Set up) — trùng MO-73 | một phần | a013 | active |
| MO-68 | Noti pinned (ghim cố định, 4 tile tính năng) | một phần | a013 | active |
| MO-69 | Noti kill app (app xuống nền trong FO, RC bật mọi phiên) | một phần | a013 | active |
| MO-70 | Noti sau khi click ads (RC click_ad_action) | một phần | a013 | active |
| MO-71 | Noti daily 8:00 và 19:00 | một phần | a013 | active |
| MO-72 | Noti shortcut/reminder (Language FO 1 lần, Home 1 lần/phiên) | một phần | a013 | active |
| MO-73 | Noti win-back 11:00 và 14:00 | một phần | a013 | active |
| MO-75 | FCM — token + nhận push từ tool nội bộ | một phần | a013 | active |
| MO-87 | Noti cảnh báo giả hệ thống — KHÔNG làm (vi phạm policy) | không | a013 | blocked-policy |
| MO-88 | Bỏ noti kill-app khi user mở Settings bật mạng | không | a013 | active |
| MO-89 | Bỏ noti kill-app kiểu cũ (foreground service KillAppService) | không | a013 | active |
| MO-95 | Noti lock screen (full-screen intent, overlay màn khoá) | không | a013 | active |
| CC-5 | Noti cá nhân hoá theo dữ liệu user (candidate) | không | a013 | candidate |

## Re-open / retention (uninstall, widget, open-with)

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-74 | Shortcut Uninstall + màn giữ chân (kèm 1 shortcut tính năng) | một phần | a013 | active |
| MO-76 | Popup/thanh gợi ý thêm widget ra màn hình chính | không | a013 | active |
| MO-77 | Mở file từ app khác (Open with) qua Splash + tracking | không | a013 | active |
| MO-78 | Mọi lượt mở lại app đi qua Splash có ads + log app_open_from | một phần | a013 | active |
| MO-91 | Màn Uninstall: mọi đường back đều về Home | không | a013 | active |
| CC-3 | Card nổi kiểu noti/widget giục user quay lại app (ứng viên) | không | a013 | candidate |
| CC-7 | Gợi ý Open with khi user tải file PDF (ứng viên) | không | a013 | candidate |

## Ads trong app

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-79 | Toast/noti sau khi click ad, có RC delay | một phần | a013 | active |
| MO-80 | Refresh banner theo từng network (plugin banner per buyer) | không | a013 | active |
| MO-81 | Inter in-app cả khi back cứng / vuốt back | không | a013 | active |
| MO-82 | Interval inter: preload trước (interval − lead) giây | một phần | a013 | active |
| MO-93 | Quay về từ ad thì tự sang màn kế (FO) | có | a013 | active |
| DEV-16 | App open ad khi quay lại app tối đa 1 lần/4 giờ (RC) | một phần | a013 | active |
| DEV-21 | Collapsible ad ở Home, đóng còn mini, về Home lại bung | có | a013 | active |
| EXT-AD-LOADING | Loading trước ad full-screen (inter in-app, app resume) — ngoài sheet | một phần | a048 | active |
| CC-2 | Bắt xem N reward ad mới dùng tính năng (ứng viên) | một phần | a013 | candidate |

## Rating

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-85 | Rating hiện sau hơn 2 lần thành công (RC đếm) | một phần | a045 | active |

## UX: quyền, webview, force update

| ID | Mục | SDK | Chuẩn | Trạng thái |
|---|---|---|---|---|
| MO-2 | Overlay hướng dẫn bật quyền trước khi sang Settings | không | a013 | active |
| MO-3 | Overlay xin quyền thông báo rõ ràng, có nút Allow | không | a013 | active |
| MO-83 | Mọi link website mở trong webview của app | không | a013 | active |
| MO-90 | Bật quyền trong Settings xong tự quay về app | không | a013 | active |
| DEV-19 | Force update: ép user cập nhật phiên bản mới | có | a013 | active |

## Key Remote Config chuẩn & alias đã gặp ở các app

Thứ tự chọn tên key khi code: tên user/ticket đưa → tên app đang có (dò theo alias) → tên chuẩn dưới đây. Xem `references/conventions.md`.

| Key chuẩn | Mục | Kiểu | Default | Alias ở app khác |
|---|---|---|---|---|
| `action_clicked_native_fsn` | MO-56 | String | next_screen | `action_clicked_native_fsn2` (a016, a036 — slot FSN thứ hai); `action_clicked_native_fsob12` (a027 — FSN giữa OB1–OB2); `action_clicked_native_fsob1` (a041); `action_clicked_new_native_fsn` (a014) |
| `action_clicked_native_fsn` | MO-59 | String | next_screen | `action_clicked_native_fsn2` (a016, a036 — slot FSN thứ hai); `action_clicked_native_fsob12` (a027 — FSN giữa OB1–OB2); `action_clicked_native_fsob1` (a041); `action_clicked_new_native_fsn` (a014) |
| `action_clicked_native_lang` | MO-37 | String | tooltip | `action_clicked_native_lang` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — không có RC màn; dùng ads_config nameSpaces[].actionClicked của language (SDK)) |
| `action_clicked_native_lang` | MO-38 | String | tooltip | `action_clicked_native_lang` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — không có RC màn; dùng ads_config nameSpaces[].actionClicked của language (SDK)) |
| `action_clicked_native_lang` | MO-39 | String | tooltip | `action_clicked_native_lang` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — không có RC màn; dùng ads_config nameSpaces[].actionClicked của language (SDK)) |
| `action_clicked_native_lang_alt` | MO-37 | String | next_screen | `action_clicked_native_lang_alt` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — ads_config nameSpace language_alt, xử lý khi actionClicked == next_screen) |
| `action_clicked_native_lang_alt` | MO-38 | String | next_screen | `action_clicked_native_lang_alt` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — ads_config nameSpace language_alt, xử lý khi actionClicked == next_screen) |
| `action_clicked_native_lang_alt` | MO-39 | String | next_screen | `action_clicked_native_lang_alt` (a014, a027, a028, a033, a041, a044 — cùng tên); `actionClicked` (a034, a037, a045 — ads_config nameSpace language_alt, xử lý khi actionClicked == next_screen) |
| `action_clicked_native_lang_alt` | MO-93 | String | next_screen | `action_clicked_native_ob1` (a013 — default next_screen); `action_clicked_native_fsn` (a013 — default next_screen); `action_clicked_native_ob3` (a013 — default finish); `action_clicked_native_lang` (a013 — default tooltip) |
| `action_clicked_native_ob1` | MO-54 | String | next_screen | `action_clicked_new_native_ob1` (a014 — giao diện onboarding mới của a014) |
| `action_clicked_native_ob1` | MO-56 | String | next_screen | `action_clicked_new_native_ob1` (a014 — giao diện onboarding mới của a014) |
| `action_clicked_native_ob1` | MO-57 | String | next_screen | `action_clicked_new_native_ob1` (a014 — giao diện onboarding mới của a014) |
| `action_clicked_native_ob2` | MO-56 | String | next_screen | `action_clicked_new_native_ob2` (a014) |
| `action_clicked_native_ob2` | MO-58 | String | next_screen | `action_clicked_new_native_ob2` (a014) |
| `action_clicked_native_ob3` | MO-55 | String | finish | `action_clicked_native_ob4` (a033, a036, a041 — trang cuối); `action_clicked_new_native_ob3` (a014) |
| `action_clicked_native_ob3` | MO-56 | String | finish | `action_clicked_native_ob4` (a033, a036, a041 — trang cuối); `action_clicked_new_native_ob3` (a014) |
| `action_clicked_native_ob3` | MO-60 | String | finish | `action_clicked_native_ob4` (a033, a036, a041 — trang cuối); `action_clicked_new_native_ob3` (a014) |
| `action_clicked_native_select` | MO-45 | String | none | `actionClicked` (a045 — ads_config nameSpace select (SDK)) |
| `action_clicked_native_select` | MO-46 | String | none | `actionClicked` (a045 — ads_config nameSpace select (SDK)) |
| `action_clicked_native_select` | MO-47 | String | none | `actionClicked` (a045 — ads_config nameSpace select (SDK)) |
| `action_clicked_native_select_alt` | MO-45 | String | none | `click_ad_select_alt_type` (a033 — chỉ có next_screen, default next_screen); `actionClicked` (a037, a045 — ads_config nameSpace select_alt, xử lý khi actionClicked == next_screen) |
| `action_clicked_native_select_alt` | MO-46 | String | none | `click_ad_select_alt_type` (a033 — chỉ có next_screen, default next_screen); `actionClicked` (a037, a045 — ads_config nameSpace select_alt, xử lý khi actionClicked == next_screen) |
| `action_clicked_native_select_alt` | MO-47 | String | none | `click_ad_select_alt_type` (a033 — chỉ có next_screen, default next_screen); `actionClicked` (a037, a045 — ads_config nameSpace select_alt, xử lý khi actionClicked == next_screen) |
| `ads_config` | CC-6 | JSON | app/config/ads_config.json |  |
| `ads_config` | DEV-9 | JSON | app/config/ads_config.json |  |
| `ads_config` | MO-17 | Json | app/config/ads_config.json đóng gói |  |
| `ads_config` | MO-20 | Json | bản đóng gói |  |
| `ads_config` | MO-27 | Json | bản đóng gói |  |
| `ads_config` | MO-29 | Json | timeout nameSpace splash 30000 | `inter_splash_timeout_second` (a033 — giây, mặc định 20; base project có splash_timeout_seconds 20) |
| `ads_config` | MO-40 | JSON | app/config/ads_config.json | `layout_native_language` (a028 — schema cũ: layoutKey trong nativeAds.positions (+ layout_native_language_meta)); `layout_native_language_alt` (a028 — schema cũ (+ layout_native_language_alt_meta)) |
| `ads_config` | MO-41 | JSON | app/config/ads_config.json | `reload_language` (a033, a036, a039, a041 — key phẳng Boolean); `reload_language_alt` (a033, a036, a039, a041 — key phẳng Boolean); `reload_custom_language` (a036, a039); `forceReload` (a028 — schema cũ trong nativeAds.positions) |
| `ads_config` | MO-49 | JSON | app/config/ads_config.json | `layout_native_select` (a028 — schema cũ (+ layout_native_select_meta)); `layout_native_select_alt` (a028 — schema cũ (+ layout_native_select_alt_meta)) |
| `ads_config` | MO-50 | JSON | app/config/ads_config.json | `reload_select` (a033 — key phẳng Boolean, default true); `forceReload` (a028 — schema cũ) |
| `allow_swipe_get_started` | MO-92 | Boolean | true | `enable_ob_end_swipe` (a016); `swipe_to_home` (a034 — kiểu trang câm cuối pager); `enable_swipe_to_home_onboard` (a033) |
| `app_refer` | MO-83 | String | (link Play) |  |
| `app_resume_interval_minutes` | DEV-16 | Long | 240 | `resumeAds.timeInterval` (a041 — ms, field JSON ads_config, default 15000) |
| `banner_refresh_buffer_size` | MO-80 | Long | 3 | `bannerAds.refresh.bufferSize` (a036 — JSON, default 3); `banner_refresh_buffer_size` (a014 — bản cũ default 1, đã gỡ) |
| `banner_refresh_default_rate` | MO-80 | Long (giây) | 30 | `bannerAds.refresh.defaultRate` (a036 — field JSON trong ads_config, default code 30) |
| `banner_refresh_rate_admob` | MO-80 | Long (giây) | 30 | `bannerAds.refresh.rateAdmob` (a036 — JSON) |
| `banner_refresh_rate_applovin` | MO-80 | Long (giây) | 10 | `bannerAds.refresh.rateApplovin` (a036 — JSON, default code 30) |
| `banner_refresh_rate_inmobi` | MO-80 | Long (giây) | 20 | `bannerAds.refresh.rateInmobi` (a036 — JSON, default code 30) |
| `banner_refresh_rate_meta` | MO-80 | Long (giây) | 30 | `bannerAds.refresh.rateMeta` (a036 — JSON) |
| `buffer_language_alt` | MO-98 | Boolean | false | `buffer_language_alt` (a027, a033, a042, a048 — cùng tên; a048 default true); `language_config.buffer_alt` (a037, a049, a045 — default a037/a049 true, a045 false) |
| `buffer_select_alt` | MO-43 | Boolean | false | `buffer_select_alt` (a027 — cùng tên); `select_config.buffer_alt` (a045 — a045 từ v1.0.9, default false) |
| `click_ad_action` | MO-48 | String | toast | `click_ad_action` (a014, a016, a037, a042 — default toast); `click_ad_action` (a027, a034, a044, a045, a047 — default notification); `click_ads_type` (a036 — default noti); `show_click_ads_noti` (a033 — Boolean) |
| `click_ad_action` | MO-70 | String | toast | `click_ads_type` (a036 — default "noti"); `clicked_ads_type_msg` (a041 — default "noti"); `show_click_ads_noti` (a033 — Boolean, default true) |
| `click_ad_action` | MO-79 | String | toast | `click_ad_action` (a027, a034, a044, a045, a047, a049 — cùng key, default 'notification') |
| `click_ad_action_delay_ms` | MO-79 | Long | 0 |  |
| `confirm_language` | MO-94 | Boolean | true | `confirm_language` (a014, a027, a034, a042, a047 — cùng tên); `confirm_same_language_alt` (a045 — default true); `time_show_show_confirm_lang` (a039); `language_config.confirm` (a045 — a045 từ v1.0.9, default true) |
| `enable_new_language_selection_ui` | DEV-6 | Boolean | false |  |
| `fs_splash_auto_next_second` | MO-29 | Long | 5 | `native_fs_splash_auto_pass_time` (a045 — 15); `nfs_splash_time_auto_pass` (a034 — 30); `fsn_auto_next_splash` (a014 — 5) |
| `fs_splash_close_second` | MO-29 | Long | 5 | `native_fs_splash_countdown_time` (a045 — mặc định 10); `nfs_splash_time_to_countdown` (a034 — 5; kèm nfs_splash_countdown_to_close 15); `time_close_FS_splash` (a027 — 3) |
| `full_scr_intent` | CC-3 | Boolean | false |  |
| `full_scr_intent` | MO-3 | Boolean | false |  |
| `full_scr_intent` | MO-95 | Boolean | false | `full_scr_intent_config` (a047 — JSON {full_scr_intent: true, full_scr_intent_retrigger: 2}; a047 default bật) |
| `full_scr_intent_guide` | MO-2 | Boolean | true |  |
| `full_scr_intent_guide` | MO-95 | Boolean | true |  |
| `full_scr_intent_retrigger` | MO-3 | Long | 2 |  |
| `full_scr_intent_retrigger` | MO-95 | Long | 2 | `full_scr_intent_config` (a047 — field full_scr_intent_retrigger trong JSON) |
| `iap_consent_reject` | MO-23 | Boolean | true |  |
| `in_app_update_enabled` | DEV-19 | Boolean | true | `enable_in_app_update` (a016 — key app cũ theo doc SDK) |
| `in_app_update_immediate_priority` | DEV-19 | Long | 4 | `force_update` (a016 — cùng ngữ nghĩa ngưỡng, theo doc SDK) |
| `in_app_update_timeout_ms` | DEV-19 | Long | 5000 |  |
| `interval_skip_inter` | MO-82 | Long (ms) | 20000 | `interval_inter_inapp` (a047, a042, a048, a049 — ms; a047 20000, a042 30000, a048 30000; a049 default 20000 (sheet Ad script, 15/10/2026)); `time_interval_inter` (a044 — ms, 20000); `inter_all_interval` (a033, a042 — ms; a033 15000, a042 45000); `interval_skip_inter` (a028, a036 — a028 default 15000) |
| `language_config` | EXT-RC-GROUP | JSON | theo app |  |
| `language_hint_delay_second` | MO-36 | Long (giây) | 2 | `language_hint_delay_second` (a045 — default 5); `delay_show_tooltips` (a034 — ms, default 2000); `time_show_tooltips_language` (a014 — giây, default 4, cộng dồn qua các lần resume); `language_config.hint_delay_second` (a045 — a045 từ v1.0.9, default 5) |
| `language_next` | MO-30 | String | select | `navigationFlow.language_next` (a045, a014, a047, a033, a034, a037, a039, a044, a027); `navigationFlow.languageNext` (a016) |
| `language_next` | MO-42 | String | select | `navigationFlow.language_next` (a028, a036, a039, a044, a045 — đọc qua getNavigationValue; default onboard); `languageNext` (a016 — navigationFlow camelCase; default onboard); `language_next` (a041 — key phẳng, default onboard) |
| `language_oder` | DEV-6 | Long | 0 | `language_order` (a027 — default 4; comment a027 nói đây là tên trên RC của a013 → cần MO xác nhận key thật); `language_config.default_language_index` (a047 — default 1) |
| `language_oder` | MO-36 | Long | 0 | `language_config.finger_position` (a034, a037, a042, a045, a048, a049 — chỉ chọn dòng có ngón tay (1-based), không dời ngôn ngữ máy; default a048/a049 1, a037 4; A048 không kẹp, A049 kẹp 1..n; a045 bỏ field này từ v1.0.9 (ngón tay luôn ở dòng ngôn ngữ máy)); `language_order` (a027 — default 4) |
| `layoutMeta` | MO-61 | String (field trong RC JSON ads_config) | theo app/config/ads_config.json | `layout_native_onboard_1` (a028 — key phẳng, có _meta và _2/_3; FSN: layout_native_fsn(_meta); map trong AdsManager.layoutNative); `layoutKeyMeta` (a041 — field config tự viết); `typeMeta` (a036 — field native position (AdsConfigProvider.getLayoutResForNameSpace)) |
| `lock_swipe_ob` | EXT-NATIVE-POOL | Boolean | false | `lock_swipe_ob` (a052 — Boolean; từng thử đổi sang ms rồi PO quay lại Boolean) |
| `logic_pass_splash` | MO-29 | String | reload | `logic_pass_splash` (a045 — mặc định auto_next); `logic_pass_splash` (a034 — mặc định reload) |
| `logic_pass_splash` | MO-93 | String | reload |  |
| `min_ad_interval_language_alt` | MO-98 | Long (ms) | 1000 | `min_ad_interval_language_alt` (a027, a033, a042, a048 — cùng tên); `language_config.min_ad_interval_alt` (a037, a049, a045 — default 1000) |
| `min_ad_interval_select_alt` | MO-43 | Long (ms) | 1000 | `min_ad_interval_select_alt` (a027 — cùng tên); `select_config.min_ad_interval_alt` (a045 — a045 từ v1.0.9, 1000) |
| `native_full_auto_pass_time` | MO-59 | Long (ms) | 2000 | `fsn_auto_next_onboard` (a014, a039 — giây, đếm từ lúc vào trang; a039 0 = tắt, a014 5) |
| `native_full_close_btn` | MO-59 | Boolean | true |  |
| `native_full_pre_auto_pass_time` | MO-43 | Long (giây) | 2 | `native_full_pre_auto_pass_time` (a027 — cùng tên); `native_full_pre_auto_pass_time` (a045 — default 15); `select_config.preparing.auto_pass_time` (a045 — a045 từ v1.0.9, giây, 10 (key phẳng cũ 15)) |
| `native_full_pre_countdown_time` | MO-43 | Long (giây) | 5 | `native_full_pre_countdown_time` (a027, a045 — cùng tên); `select_config.preparing.countdown_time` (a045 — a045 từ v1.0.9, giây, 5) |
| `native_full_time_to_countdown` | MO-59 | Long (ms) | 2000 | `time_close_fsn_ob` (a039 — giây, 5); `time_close_fsob12` (a027 — giây, 2, chỉ FSN12 (FSN23 hiện X ngay)); `onboard_2fsn_close_countdown` (a016 — giây, 5, đếm ngầm, chỉ khi onboard_2_fsn=true); `show_close_native_fs_countdown` (a034, a037 — giây (a034 5, a037 3)); `time_show_button_X_fsn` (a044, a047, a049 — giây, 5, đếm ngầm; a047/a049 đếm từ lúc ad hiện khi FSN là trang hiện tại; a049 0 = X hiện ngay); `time_close_FS_onboard` (a014 — giây, 0); `closeCountdown` (a036 — field native position trong ads_config tự viết); `onboard_config.fsn_close_second` (a045 — a045 từ v1.0.9, giây, 5 (trước đó time_show_button_X_fsn)) |
| `native_pool_logic` | EXT-NATIVE-POOL | Boolean | true | `native_pool_logic` (a052 — tên đặt lúc làm A052, MO chưa đưa tên) |
| `native_splash_high_logic` | MO-29 | Boolean | true | `native_splash_high_logic` (a045, a034 — cùng tên) |
| `new_onboard` | MO-63 | Boolean | true |  |
| `new_uninstall_enable` | MO-74 | Boolean | true |  |
| `noti_config` | EXT-RC-GROUP | JSON | theo app |  |
| `noti_kill_app_show_all` | MO-69 | Boolean | false |  |
| `noti_lockscreen_enable` | CC-3 | Boolean | true |  |
| `noti_lockscreen_enable` | MO-95 | Boolean | true | `enable_noti_lockscreen` (a047 — cùng nghĩa); `show_lockscreen_noti` (a033, a034, a048 — cùng nghĩa); `noti_config:lockscreen.enable` (a037, a049 — RC gom JSON nhóm noti_config) |
| `noti_lockscreen_hide_second` | MO-95 | Long | 20 | `noti_lockscreen_show_second` (a27, a034, a039 — cùng nghĩa); `time_delay_noti_hide` (a044, a033, a041, a048 — cùng nghĩa); `noti_config:lockscreen.show_second` (a037 — RC gom JSON nhóm noti_config) |
| `noti_lockscreen_replace` | MO-95 | Boolean | false | `noti_config:lockscreen.replace` (a037, a049 — RC gom JSON nhóm noti_config) |
| `noti_lockscreen_slots` | MO-95 | String | 11:30,17:00,20:00 | `time_push_noti_lockscr_layout1` (a034 — mỗi slot 1 key: layout1/2/3 = 11:00/17:00/20:00; layout4 = slot quà ngày 1/3/5/7); `time_push_noti_lockscr` (a031 — JSON {slot1, slot2, slot3}; rỗng = không hẹn); `noti_config` (a037 — JSON nhóm: lockscreen.slots); `noti_config:lockscreen.slots` (a049 — default 11:30,17:00,20:00) |
| `noti_lockscreen_slots_new` | MO-95 | String | 11:30,17:00,20:00 | `noti_config` (a037 — JSON nhóm: lockscreen.slots_new); `noti_config:lockscreen.slots_new` (a049 — default 09:00,13:00,19:00) |
| `noti_permission_trigger` | MO-25 | String | splash | `ask_noti_permission_at_home` (a014 — Boolean, mặc định true); `noti_config:permission_trigger` (a049 — splash \| home, default splash) |
| `noti_permission_trigger` | MO-3 | String | splash |  |
| `ob1_swipe` | MO-53 | Boolean | true | `action_click_back_ob` (a016 — =2: back → đứng yên + hint (OB1 hint bấm, trang khác hint vuốt) — phần backpress) |
| `ob_back_btn` | MO-28 | Boolean | true |  |
| `ob_back_btn` | MO-52 | Boolean | true | `action_click_back_ob` (a016 — Long: 1 popup thoát, 2 đứng yên + hint, 3 lùi trang (OB1 → Language); chỉ back hệ thống, không có nút); `action_click_back_device_ob` (a047 — String trong JSON onboard_config: keep_state \| reload (lùi trang + reload ad; OB1 → Language)); `is_show_button_back` (a044 — kèm position_show_button_back; đích tra ngược navigationFlow) |
| `onboard_config` | EXT-RC-GROUP | JSON | theo app |  |
| `onboard_next` | MO-30 | String | home | `navigationFlow.onboard_next` (a045, a014, a047, a033, a034, a037, a039, a044, a027); `navigationFlow.onboardNext` (a016); `scan_onboard_next` (a027); `paywall_next` (a027); `paywallNext` (a016); `iap_next` (a044) |
| `onboard_next` | MO-63 | String | home | `onboardNext` (a016 — camelCase trong navigationFlow); `navigationFlow` (a027, a028, a033, a037, a044, a045 — entry onboard_next trong ads_config; giá trị paywall thay cho iap (a027, a028); a027 thêm scan_onboard, a045 thêm uninstall) |
| `preload_lead_inter` | MO-82 | Long (ms) | 5000 | `preload_inter_buffer_second` (a014, a016, a033, a034, a041, a044, a045, a047, a048, a049 — GIÂY, default 5); `second_preload_inter_buffer` (a039 — giây, 5); `preload_inter_interval` (a027, a037 — giây, 5) |
| `priority_languages` | DEV-6 | String (CSV) |  | `priority_languages` (a044 — default en,pt-BR,hi,de); `priority_languages` (a027 — default ar,hi,en,uk,fr,bn,ru,pt,th,es); `language_config.priority_languages` (a034, a045 — mảng JSON trong RC language_config; token system = vị trí ngôn ngữ máy); `language_config.order` (a037, a042, a048, a049 — trong RC language_config; a048/a049 nhận mảng JSON hoặc CSV, cắt 10 (PRIORITY_LANGUAGE_LIMIT) trước khi lọc; default a048 en,es,pt,ar; a049 theo doc PO); `top_languages` (a033 — String CSV, default en,hi,pt,vi,bn,pl,in,es,uk,tw,fr) |
| `rate_config` | EXT-RC-GROUP | JSON | theo app |  |
| `rate_success` | MO-85 | Boolean | true | `show_rating_at_success` (a013 — A013: 1 lần/ngày); `show_rating` (a037, a039) |
| `rate_success_jump` | MO-85 | Long | 1 |  |
| `rate_success_trigger` | MO-85 | Long | 2 | `rating_dialog_trigger_count` (a014 — A014 bản cũ, default 3, đã bỏ); `rating_min_success` (a045 — A045 bản cũ) |
| `rating_max_show` | MO-85 | Long | 3 | `rating_max_show` (a014 — default 2); `rating_max_show` (a047 — khai Int → RC không ăn) |
| `reload_fsn` | MO-62 | Boolean | true | `reload_fsob12` (a027 — FSN12); `reload_fsn12` (a034 — FSN12); `reload_fsn_ob` (a039 — chung 2 FSN) |
| `reload_ob1` | MO-62 | Boolean | true | `reload_onboard_1` (a033); `reload_onboard` (a041 — dùng chung cho các trang OB); `forceReload` (a028 — field native position trong ads_config tự viết (ảnh sheet)) |
| `reload_ob2` | MO-62 | Boolean | true | `reload_onboard_2` (a033) |
| `reload_ob3` | MO-62 | Boolean | true | `reload_ob4` (a036 — trang cuối); `reload_onboard_4` (a033 — trang cuối); `reload_onboard4` (a041 — trang cuối) |
| `reward_fail_continue` | CC-2 | Boolean | true |  |
| `reward_required_count` | CC-2 | Long | 1 |  |
| `screen_skip_inter` | MO-82 | Long | 3 | `inter_interval_condition` (a039 — 'or' \| 'and' gộp số màn và thời gian) |
| `select_btn_skip` | MO-43 | Boolean | true | `select_btn_skip` (a027, a045 — cùng tên); `select_config.btn_skip` (a045 — a045 từ v1.0.9 (trước đó select_btn_skip)) |
| `select_hint_delay_second` | MO-44 | Long (giây) | 0 |  |
| `select_loading_enabled` | MO-43 | Boolean | false | `select_loading` (a027 — default false) |
| `select_next` | MO-30 | String | onboard | `navigationFlow.select_next` (a045, a014, a033, a034, a037, a039, a027); `navigationFlow.selectNext` (a016) |
| `select_next` | MO-51 | String | onboard | `navigationFlow.select_next` (a028 — default paywall); `navigationFlow.select_next` (a036, a039, a045 — default home); `selectNext` (a016 — camelCase, default iap) |
| `show_collab_home` | DEV-21 | Boolean | true | `nativeSplashCollapse` (a016 — đúng chuỗi key, default true) |
| `show_iap_after_splash` | MO-5 | Boolean | true | `iap_first_open_enabled` (a014 — bật paywall trong FO) |
| `show_small_button_select` | MO-43 | Boolean | true | `show_small_button_select` (a016 — default false) |
| `splash_config` | EXT-RC-GROUP | JSON | theo app (= giá trị Firebase lúc gộp) |  |
| `splash_next` | MO-30 | String | language | `navigationFlow.splash_next` (a045, a014, a047, a033, a034, a037, a039, a044, a027 — đọc qua AdsConfigProvider.getNavigationValue trong ads_config); `navigationFlow.splashNext` (a016 — camelCase) |
| `star_review_to_store` | MO-85 | Long | 4 |  |
| `time_show_loading_ads` | EXT-AD-LOADING | Long (ms) | 1000 | `time_show_loading_ads` (a039, a048, a049 — cùng tên; a039 default 500, a048/a049 1000) |
| `use_new_logic_inter_noti` | MO-99 | Boolean | true |  |
| `widget_card` | MO-76 | String | split |  |

# Câu hỏi mở cần MO/PO chốt — và mặc định skill dùng trong lúc chờ

Gom từ lúc đối chiếu recipe với code (10/2026). Q33–Q52 và các dòng "Tiền lệ" thêm sau khi làm A049 (ref A047,
A048), 15/10/2026; Q53 thêm 20/10/2026. Khi apply một mục có câu hỏi ở đây:
- làm theo cột **Mặc định**;
- ghi rõ trong báo cáo: "đang theo mặc định, chờ MO chốt câu Qx".

MO trả lời câu nào thì người bảo trì sửa recipe + catalog rồi xoá câu đó khỏi file.

Nguyên tắc chọn mặc định:
- **Hành vi:** theo app ref đang dùng (mặc định A013, hoặc `canonical.app` của mục), trừ khi ref có lỗi đã biết
  hoặc vi phạm chính sách. Ref do user chọn (≠ A013) thiếu dòng nghiệm thu thì không tự thêm, hỏi user (`SKILL.md`
  bước 2).
- Các câu đánh dấu **lỗi/chính sách (Q3, Q22, Q30)** luôn áp, bất kể ref.
- **Tên key mới:** theo tên đề xuất trong recipe (ref khác A013 thì theo tên của ref).

## Setup & Splash

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q1 | MO-17, MO-27 | Có chờ Remote Config trước khi load ad splash không? | Theo A013: **không chờ**; khi release, giữ `app/config/ads_config.json` = bản RC đang chạy. Đề xuất của recipe: chờ RC, có trần cố định 2–3s. Tiền lệ 10/2026: A048 chờ `fetchedStateFlow` (không trần); A047, A049 không chờ (A049 user chốt). | MO |
| Q2 | MO-25, MO-29 | Có chờ `mobileAdsFinish` (init xong) mới load splash không? Google khuyến nghị chờ khi dùng mediation. | Theo A013: load song song, không chờ. Tiền lệ 10/2026: A048 chờ `initFinished`; A049 (user chốt "check mạng y A047") mở cổng theo `consentFinished` + `isConnected`, không chờ init. | MO |
| Q3 | MO-22 | Map consent Firebase theo purpose TCF thế nào? Default `google_analytics_default_allow_*` trong manifest? | **Không** theo A013 (A013 set GRANTED cứng là lỗi). Map theo kết quả UMP như recipe `splash.md` § MO-22. Tiền lệ: A049 là app đầu áp mặc định này (`ads/ConsentMode.kt`, `analytics_storage` tạm theo Purpose 1, chưa thêm `google_analytics_default_allow_*`). | MO + legal |
| Q4 | MO-29 | `TIMEOUT` của ad splash: chờ tiếp (A013) hay đi tiếp (A045/a027/a033)? | Theo A013, và giữ trần tổng thời gian splash nếu app đang có. Tiền lệ 10/2026: A047, A048, A049 coi TIMEOUT là đi tiếp; A049 bỏ hẳn trần tổng (RC `splash_timeout_seconds`) ngày 15/10/2026. | MO |
| Q5 | MO-14, MO-15 | Còn dùng Adjust không? Nếu bỏ, IAP revenue gửi qua kênh nào (AppsFlyer chưa app nào gửi)? | Không thêm Adjust vào app mới. App đang có Adjust thì giữ nguyên. App dùng SDK đánh N/A. | MO/UA |
| Q6 | MO-23 | Consent reject → IAP: Figma? tên RC/event? | Chưa làm. Báo "chờ Figma + tên key". | MO + design |
| Q7 | MO-99 | "User cũ" nghĩa là gì (theo session/ngày cài)? Hậu tố `_o` đang mang nhiều nghĩa. | Theo recipe: lượt FO mở từ launcher → `splash`, mọi lượt khác → `splash_o` (như a047), fallback `splash`. | MO |
| Q8 | MO-18 | Danh sách event IAA/IAP custom chuẩn? | Chưa audit được. Ghi "chờ MO". | MO |
| Q9 | MO-19 | MultiDex còn cần kiểm không (minSdk ≥ 21 là luôn đạt)? | Coi là Done khi minSdk ≥ 21. | MO |
| Q10 | (mới) | Thêm mục "Privacy options" (UMP `showPrivacyOptionsForm` trong Setting) vào checklist? | Đề xuất thêm; chưa bắt buộc. | MO |
| Q33 | MO-25 | Hỏi quyền noti ở mọi lần mở (A047, A048, A049) hay chỉ 1 lần (A013, P4253)? Hỏi mọi lần thì form UMP có thể hiện lại vài giây sau khi SDK bật `consentFinished` sớm (consent phiên trước) và đè popup noti; SDK tới 1.8.7 không báo form đã đóng. | Theo ref. A049: user chốt "giữ như A047" (13/10/2026), chấp nhận đè. Cách triệt để: SDK thêm cờ `umpFinished`. | MO + SDK team |
| Q34 | MO-26, MO-96 | Trạng thái mạng lấy từ `adsManager.isConnected` của SDK (default network + VALIDATED: VPN mất Wi-Fi/4G vẫn true) hay theo đường truyền thật (A049 `NetworkStatus.onlineFlow`)? | Theo ref. A049: Splash dùng `isConnected` như A047 (user chốt), popup dùng `onlineFlow`; lệch ở case VPN là có chủ ý. | MO |
| Q35 | MO-100, MO-97 | Nghiệm thu MO-100 đòi `AdsManager` `createdAtStart`, nhưng base project, A047, A048, A049 đều lazy (hợp MO-97). Giữ dòng này? | Giữ code app, báo lệch, không ép `createdAtStart`. | MO + người bảo trì |

## Language, Select, Onboarding

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q11 | MO-37..39, 45..47, 54..60 | Hành động sau click native: RC theo màn (`action_clicked_native_*`, A013) hay `actionClicked` trong ads_config (SDK, a037)? | Theo A013: RC theo màn, kèm `actionClicked: none` cho nameSpace đó để SDK không tự reload. App đang dùng kiểu SDK thì giữ kiểu SDK. Tiền lệ 10/2026: A048, A049 chỉ dùng tầng SDK (`actionClicked: reload` cho mọi nameSpace onboarding); a047 `next_screen`. | MO |
| Q12 | MO-30, 42, 51, 63 | Màn kế: key phẳng (`splash_next`…, A013) hay `navigationFlow` trong ads_config (SDK, base project)? | Giữ kiểu app đang dùng. App chưa có thì theo base project (`navigationFlow`). | MO |
| Q13 | MO-36, 44, 59, 92 | Duyệt tên key mới: `language_hint_delay_second` (2), `select_hint_delay_second` (0 = tắt), `action_clicked_native_select(_alt)` (none), `native_full_close_btn` (true), `allow_swipe_get_started`. | Dùng tên đề xuất + báo MO trong báo cáo. Tiền lệ 10/2026: A048/A049 ngón tay cứng 3s, không RC; `native_full_close_btn` chưa app nào có. | MO |
| Q14 | MO-33 | a013 trên Firebase dùng key `language_oder` (code) hay `language_order` (a027 ghi là key a013)? | Giữ `language_oder` cho a013 (theo code). | MO kiểm Firebase |
| Q15 | MO-32, 33 | Tiếng Indonesia giữ 1 dòng mã nào (`in` hay `id`)? | Giữ `id`, chuẩn hoá `in`→`id` qua `Locale.forLanguageTag(...).language` khi so khớp (như A045 10/2026). | MO |
| Q16 | MO-47 | Select → Select Alt sau click ad: có chọn sẵn item không? | Không chọn sẵn. User phải tự chọn. | MO |
| Q17 | MO-56..60 | "has ads" trong sheet = `clear_ads` (ẩn ad đã click) hay `reload` (nạp ad mới)? | `clear_ads` (theo bộ giá trị A013). | MO |
| Q18 | MO-52 | Back ở OB1 về hẳn Language, hay về màn liền trước (A013: Select nếu luồng có Select)? | Theo A013: về màn liền trước onboarding. | MO |
| Q19 | MO-59 | Tắt nút X của native full-screen thì có tắt luôn auto-pass không? | Không, vẫn giữ auto-pass. Tiền lệ 10/2026: a047, A048, A049 không có auto-pass (chỉ X / "Maybe Later" và vuốt). | MO |
| Q20 | MO-30, 42, 63 | Giá trị màn IAP trong luồng: `iap` hay `paywall` (a027)? | Giữ giá trị app đang dùng; app chưa có thì `iap` (chữ trong sheet). | MO |
| Q36 | MO-32 | App chỉ có N ngôn ngữ dịch đủ có phải lên đủ 55 mã không? | Theo ref, báo MO-32 chưa đạt. A049: user chốt đúng 13 mã như A048 (13/10/2026). | PO + MO |
| Q37 | MO-86 | Back ở Alt: nút Save to (A013) hay popup confirm có native (A048, a037)? Confirm ở Normal: sang Alt (catalog, a033) hay áp luôn rồi đi tiếp (A048, a037; mất impression `language_alt`)? | Theo ref. A049 theo A048. | MO |
| Q38 | DEV-6 | Tối đa 6 (sheet) hay 10 (A048/A049 `PRIORITY_LANGUAGE_LIMIT`, a037)? Cắt trước hay sau khi lọc? Default `order` rỗng (A013) hay có sẵn (A048 `en,es,pt,ar`, A049 `en,pt,hi,de`)? | Ref A013: theo nghiệm thu (6, cắt sau khi lọc). Ref khác: theo ref, báo lệch. | MO |
| Q39 | MO-98 | Buffer native Language Alt mặc định bật hay tắt? A013, A045 tắt; A048, a037, A049 bật. | Theo ref. | MO |
| Q40 | MO-59 | Đếm X của FSN từ lúc vào trang (A013, A048) hay từ lúc ad hiện và user đang ở trang (A045, a047, A049)? FSN `FAIL` khi user đang đứng: luôn đi tới (A048, A045), đi theo chiều đang đi (A049), hay hiện X ngay (a047)? | Theo ref. Viết mới thì đi theo chiều đang đi để user không kẹt. | MO |
| Q41 | MO-62, MO-64..67 | Nghiệm thu impression viết cho 1 FSN, app 2 FSN (A048, A049) không khớp. Dừng trang có nạp lại cả trang đang xem (A048) hay không (A049)? | Đề xuất nghiệm thu "trang hiện tại + 2 trang kề có impression"; phần còn lại theo ref. | MO |
| Q42 | MO-63 | Mở lại app giữa FO: chạy lại từ đầu (A013, A048) hay bỏ bước đã xong (A049 theo PO P4900, cờ `onboard_completed`)? | Theo A013, trừ khi PO yêu cầu. | PO |

## Notification

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q21 | MO-69 | Kill-app chỉ bắn trong FO (A013) hay mọi phiên (A014, a27, A028, a034, a044, A045, A047, A048, A049)? Tên key bật mọi phiên? | Theo ref: A013 thì chỉ FO, không có RC bật mọi phiên; ref A047/A048 thì bắn mọi phiên như ref. Key đề xuất `noti_kill_app_show_all` (Boolean, false) chưa app nào có: chỉ thêm khi MO chốt tên và user yêu cầu. App đang bắn mọi phiên thì giữ nguyên. Tiền lệ 10/2026, A049 ref A047: ban đầu chỉ FO + `noti_config:kill_app.show_all`. User bỏ field này (chưa app nào có RC), rồi sau bug QC "ở Home kill / minimize không có noti" chốt theo A047, bắn mọi phiên (15/10/2026). | MO |
| Q22 | MO-95 | Bỏ `CATEGORY_ALARM` cho noti lock screen (xuyên chế độ Không làm phiền)? | **Không set** khi làm mới (coi là lỗi đã biết của A013, như A047). App đang set thì báo và hỏi trước khi bỏ. Tiền lệ: A049 không set (theo A047). | MO/PO |
| Q23 | MO-95 | Đúng slot mà user đang dùng máy: post heads-up (A013) hay bỏ lượt (A045/A047)? | Theo A013: heads-up, không full-screen. Tiền lệ: A049 bỏ lượt (theo ref A047). | MO |
| Q24 | MO-4, MO-73 | Gộp MO-4 vào MO-73? | Catalog đã đánh dấu MO-4 `duplicate_of` MO-73; làm theo MO-73. | MO |
| Q25 | MO-75 | Tool bắn noti nội bộ (Trường) cần topic hay deep link gì ngoài token? | Chỉ đăng ký token + `onNewToken` như hiện tại. | Trường/MO |
| Q26 | CC-5 | Noti cá nhân hoá dựa trên hành vi ở app khác: có hợp lệ không? | Không làm. Ứng viên, cần PO + legal. | PO + legal |
| Q43 | MO-70 | Tap noti click-ads về đâu: Home (A013), màn đang đứng (A047), hay đích Figma của app vẽ (A049: Horoscopes)? | Theo Figma/ticket của app; không có thì theo ref. | MO |
| Q44 | MO-72, MO-78 | `open_from` của noti shortcut = `shortcut` (A048/A049 theo danh sách PO), trùng với lượt mở từ launcher shortcut. Chấp nhận? | Giữ danh sách PO; phân biệt bằng event `notification_clicked` `type`. | PO / Data |
| Q51 | MO-70 | `click_ad_action` = `notification` mà user chưa cấp quyền noti thì không hiện gì (A013, A047, A049). Có fallback sang toast không? | Theo ref (hiện chưa app nào fallback); báo trong báo cáo. | MO |
| Q52 | MO-95 | "User mới" của lock screen (`slots_new`, 24h đầu): theo mốc lưu pref lúc mở app đầu (A013, `pm clear` là reset) hay `PackageInfo.firstInstallTime` (A047, A049, chỉ gỡ cài lại mới reset)? A048 lại coi user chưa qua FO (`firstOpen`) là mới. | Theo ref; báo cách QC tương ứng. | MO |

## Ads trong app, Re-open, Rating, UX

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q27 | MO-79, DEV-16, CC-2, EXT-AD-LOADING | Duyệt tên key mới: `click_ad_action_delay_ms`, `app_resume_interval_minutes`, `reward_required_count`. | Dùng tên đề xuất + báo MO. Thêm: `time_show_loading_ads` (ms, loading trước inter in-app, mục EXT-AD-LOADING, ticket A049 P4713, chưa có dòng trong sheet MO) — A048/A049 default 1000, a039 500. | MO |
| Q28 | MO-82 | Interval inter tính từ lúc impression (A013) hay lúc đóng ad (a044)? | Theo A013: từ impression. Thêm: A047/a044 tính từ lúc đóng ad; A048/A049 từ `onAdShow` của riêng `inter_inapp`, không tính inter splash → inter in-app có thể hiện ngay sau inter splash. MO chốt luôn inter splash có tính vào interval không. | MO |
| Q29 | DEV-21 | Collapsible ở Home: native collapsible hay AdMob collapsible banner? | Theo app ref đang có. Không có thì dùng `BANNER_COLLAPSIBLE` của SDK. | MO |
| Q30 | MO-74 | A045 có fallback nhãn shortcut "UninstaII" (chữ I hoa thay l) — rủi ro chính sách giả mạo. | **Không dùng nhãn giả chữ.** Nhãn thật + màn uninstall có đường gỡ thật. A047 khi launcher từ chối chỉ đổi id thành `UninstaII`, nhãn vẫn chuỗi đã dịch (hợp mặc định); chỉ A045 đổi cả nhãn. | PO |
| Q31 | MO-85 | Ngưỡng "hơn 2 lần": A045 `rate_success_trigger` mặc định 2 (hiện ở lượt 2). Đặt 3? | Giữ default code, ghi "MO đặt 3 trên RC nếu đúng chữ sheet". | MO |
| Q32 | MO-80 | Refresh banner theo network cần SDK hỗ trợ (app SDK không đọc được unit ID). Đưa vào SDK? | Chưa làm cho app SDK. App không SDK (a036) theo a036. | SDK team + MO |
| Q45 | MO-74 | Card Try ở màn Uninstall có inter không? Nghiệm thu ghi có, A013 có; A047, A048 không. | Theo ref (SKILL.md bước 2: ref thiếu thì không tự thêm, báo lệch). A049 không có (user chốt theo A048, 13/10/2026). | MO |
| Q46 | MO-74, MO-91 | Rời ScrUninstall có đánh dấu xong FO không? A013 (`firstOnboard = false`), A045, A047 (`markFirstOpenDone`) có; A048 không. | Theo ref. A049 có (user yêu cầu 13/10/2026 dù ref A048 không làm). | MO / PO |
| Q47 | MO-91 | Back cứng / icon Home ở ScrUninstall có chèn inter không? A047 có (theo interval), `GeneralBackHandler` A045 mặc định có; A048, A049 không. | Theo ref. | MO |
| Q48 | MO-74 | Figma vẽ 5 shortcut nhưng Pixel/Launcher3 chỉ hiện 4 (rank thấp nhất): bỏ shortcut nào, hay đưa Uninstall lên đầu? | Giữ tổng ≤ 4 hoặc rank Uninstall trong top 4, hỏi PO. A049 đang comment shortcut Horoscope. | PO |
| Q49 | MO-78 | Bảng giá trị `open_from`: theo A013 (`notification_winback`, `notification_lock_screen`, `shortcut_<x>`, không log lượt mở thường) hay theo danh sách PO (A048, A049; `conventions.md` §2)? | App có tab trong sheet Universal Events & Parameters thì theo PO; không có thì theo A013. | MO / PO |
| Q50 | DEV-16 | Timeout nạp `app_resume` lúc user quay lại (user nhìn loading trong lúc này): A013 30s, A047 10s (A049 theo), A048 5s. | Theo ref. | MO |
| Q53 | CC-2 | Tải reward lỗi (no fill, mất mạng): vẫn cho dùng tính năng, hay dừng + toast? A045 cho chạy; A047 báo lỗi, không chạy; A049 để RC `reward_fail_continue` (mặc định `true` = chạy). | Theo ref; app không có ref thì hỏi user. | MO |

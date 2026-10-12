# Câu hỏi mở cần MO/PO chốt — và mặc định skill dùng trong lúc chờ

Gom từ lúc đối chiếu recipe với code (10/2026). Khi apply một mục có câu hỏi ở đây:
- làm theo cột **Mặc định**;
- ghi rõ trong báo cáo: "đang theo mặc định, chờ MO chốt câu Qx".

MO trả lời câu nào thì người bảo trì sửa recipe + catalog rồi xoá câu đó khỏi file.

Nguyên tắc chọn mặc định:
- **Hành vi:** theo app ref đang dùng (mặc định A013), trừ khi ref có lỗi đã biết hoặc vi phạm chính sách.
- Các câu đánh dấu **lỗi/chính sách (Q3, Q22, Q30)** luôn áp, bất kể ref.
- **Tên key mới:** theo tên đề xuất trong recipe (ref khác A013 thì theo tên của ref).

## Setup & Splash

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q1 | MO-17, MO-27 | Có chờ Remote Config trước khi load ad splash không? | Theo A013: **không chờ**; khi release, giữ `app/config/ads_config.json` = bản RC đang chạy. Đề xuất của recipe: chờ RC, có trần cố định 2–3s. | MO |
| Q2 | MO-25, MO-29 | Có chờ `mobileAdsFinish` (init xong) mới load splash không? Google khuyến nghị chờ khi dùng mediation. | Theo A013: load song song, không chờ. | MO |
| Q3 | MO-22 | Map consent Firebase theo purpose TCF thế nào? Default `google_analytics_default_allow_*` trong manifest? | **Không** theo A013 (A013 set GRANTED cứng là lỗi). Map theo kết quả UMP như recipe `splash.md` § MO-22. | MO + legal |
| Q4 | MO-29 | `TIMEOUT` của ad splash: chờ tiếp (A013) hay đi tiếp (A045/a027/a033)? | Theo A013, và giữ trần tổng thời gian splash nếu app đang có. | MO |
| Q5 | MO-14, MO-15 | Còn dùng Adjust không? Nếu bỏ, IAP revenue gửi qua kênh nào (AppsFlyer chưa app nào gửi)? | Không thêm Adjust vào app mới. App đang có Adjust thì giữ nguyên. App dùng SDK đánh N/A. | MO/UA |
| Q6 | MO-23 | Consent reject → IAP: Figma? tên RC/event? | Chưa làm. Báo "chờ Figma + tên key". | MO + design |
| Q7 | MO-99 | "User cũ" nghĩa là gì (theo session/ngày cài)? Hậu tố `_o` đang mang nhiều nghĩa. | Theo recipe: lượt FO mở từ launcher → `splash`, mọi lượt khác → `splash_o` (như a047), fallback `splash`. | MO |
| Q8 | MO-18 | Danh sách event IAA/IAP custom chuẩn? | Chưa audit được. Ghi "chờ MO". | MO |
| Q9 | MO-19 | MultiDex còn cần kiểm không (minSdk ≥ 21 là luôn đạt)? | Coi là Done khi minSdk ≥ 21. | MO |
| Q10 | (mới) | Thêm mục "Privacy options" (UMP `showPrivacyOptionsForm` trong Setting) vào checklist? | Đề xuất thêm; chưa bắt buộc. | MO |

## Language, Select, Onboarding

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q11 | MO-37..39, 45..47, 54..60 | Hành động sau click native: RC theo màn (`action_clicked_native_*`, A013) hay `actionClicked` trong ads_config (SDK, a037)? | Theo A013: RC theo màn, kèm `actionClicked: none` cho nameSpace đó để SDK không tự reload. App đang dùng kiểu SDK thì giữ kiểu SDK. | MO |
| Q12 | MO-30, 42, 51, 63 | Màn kế: key phẳng (`splash_next`…, A013) hay `navigationFlow` trong ads_config (SDK, base project)? | Giữ kiểu app đang dùng. App chưa có thì theo base project (`navigationFlow`). | MO |
| Q13 | MO-36, 44, 59, 92 | Duyệt tên key mới: `language_hint_delay_second` (2), `select_hint_delay_second` (0 = tắt), `action_clicked_native_select(_alt)` (none), `native_full_close_btn` (true), `allow_swipe_get_started`. | Dùng tên đề xuất + báo MO trong báo cáo. | MO |
| Q14 | MO-33 | a013 trên Firebase dùng key `language_oder` (code) hay `language_order` (a027 ghi là key a013)? | Giữ `language_oder` cho a013 (theo code). | MO kiểm Firebase |
| Q15 | MO-32, 33 | Tiếng Indonesia giữ 1 dòng mã nào (`in` hay `id`)? | Giữ `id`, chuẩn hoá `in`→`id` qua `Locale.forLanguageTag(...).language` khi so khớp (như A045 10/2026). | MO |
| Q16 | MO-47 | Select → Select Alt sau click ad: có chọn sẵn item không? | Không chọn sẵn. User phải tự chọn. | MO |
| Q17 | MO-56..60 | "has ads" trong sheet = `clear_ads` (ẩn ad đã click) hay `reload` (nạp ad mới)? | `clear_ads` (theo bộ giá trị A013). | MO |
| Q18 | MO-52 | Back ở OB1 về hẳn Language, hay về màn liền trước (A013: Select nếu luồng có Select)? | Theo A013: về màn liền trước onboarding. | MO |
| Q19 | MO-59 | Tắt nút X của native full-screen thì có tắt luôn auto-pass không? | Không, vẫn giữ auto-pass. | MO |
| Q20 | MO-30, 42, 63 | Giá trị màn IAP trong luồng: `iap` hay `paywall` (a027)? | Giữ giá trị app đang dùng; app chưa có thì `iap` (chữ trong sheet). | MO |

## Notification

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q21 | MO-69 | Kill-app chỉ bắn trong FO (A013) hay mọi phiên (A014, a27, A028, a034, a044, A045, A047)? Tên key bật mọi phiên? | Theo A013: chỉ FO. Key đề xuất `noti_kill_app_show_all` (Boolean, false). App đang bắn mọi phiên thì giữ nguyên. | MO |
| Q22 | MO-95 | Bỏ `CATEGORY_ALARM` cho noti lock screen (xuyên chế độ Không làm phiền)? | **Không set** khi làm mới (coi là lỗi đã biết của A013, như A047). App đang set thì báo và hỏi trước khi bỏ. | MO/PO |
| Q23 | MO-95 | Đúng slot mà user đang dùng máy: post heads-up (A013) hay bỏ lượt (A045/A047)? | Theo A013: heads-up, không full-screen. | MO |
| Q24 | MO-4, MO-73 | Gộp MO-4 vào MO-73? | Catalog đã đánh dấu MO-4 `duplicate_of` MO-73; làm theo MO-73. | MO |
| Q25 | MO-75 | Tool bắn noti nội bộ (Trường) cần topic hay deep link gì ngoài token? | Chỉ đăng ký token + `onNewToken` như hiện tại. | Trường/MO |
| Q26 | CC-5 | Noti cá nhân hoá dựa trên hành vi ở app khác: có hợp lệ không? | Không làm. Ứng viên, cần PO + legal. | PO + legal |

## Ads trong app, Re-open, Rating, UX

| # | Mục | Câu hỏi | Mặc định | Ai chốt |
|---|---|---|---|---|
| Q27 | MO-79, DEV-16, CC-2 | Duyệt tên key mới: `click_ad_action_delay_ms`, `app_resume_interval_minutes`, `reward_required_count`. | Dùng tên đề xuất + báo MO. | MO |
| Q28 | MO-82 | Interval inter tính từ lúc impression (A013) hay lúc đóng ad (a044)? | Theo A013: từ impression. | MO |
| Q29 | DEV-21 | Collapsible ở Home: native collapsible hay AdMob collapsible banner? | Theo app ref đang có. Không có thì dùng `BANNER_COLLAPSIBLE` của SDK. | MO |
| Q30 | MO-74 | A045 có fallback nhãn shortcut "UninstaII" (chữ I hoa thay l) — rủi ro chính sách giả mạo. | **Không dùng nhãn giả chữ.** Nhãn thật + màn uninstall có đường gỡ thật. | PO |
| Q31 | MO-85 | Ngưỡng "hơn 2 lần": A045 `rate_success_trigger` mặc định 2 (hiện ở lượt 2). Đặt 3? | Giữ default code, ghi "MO đặt 3 trên RC nếu đúng chữ sheet". | MO |
| Q32 | MO-80 | Refresh banner theo network cần SDK hỗ trợ (app SDK không đọc được unit ID). Đưa vào SDK? | Chưa làm cho app SDK. App không SDK (a036) theo a036. | SDK team + MO |

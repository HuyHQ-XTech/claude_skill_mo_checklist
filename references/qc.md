# QC các mục MO — cách test chung

Bước QC riêng từng mục nằm trong section `## MO-xx` của file reference, và trong field `qc` của catalog
(`scripts/catalog.py show MO-xx`). File này gom các thao tác dùng chung, để QC/dev khỏi viết lại mỗi lần.

Trong các lệnh dưới, `$P` = applicationId của app (lấy từ `detect_stack.py`), `S="adb -s <serial> shell"`.

## 1. Remote config

- **Fetch kiểu cache-first.** App dùng giá trị cache/default ngay, rồi fetch nền; giá trị mới thường chỉ
  áp từ **lần mở sau**. Đổi RC trên Firebase xong:
  1. `$S pm clear $P` (xoá cache RC + prefs)
  2. mở app 1 lần → thoát → mở lại.
- **Tránh thử RC trên user thật.** Nên tạo condition theo `app_version` hoặc user property cho máy test.
- **Xem giá trị thật trên máy** (build debug, cần `run-as`):
  `$S "run-as $P sh -c 'cat shared_prefs/*.xml'" | grep -i <key>`. Default trong code không phải giá trị
  đang chạy.
- **`ads_config` cũng là một key RC.** Sửa placement/unit/layout thì sửa trên Firebase, không phải file
  trong repo. File `app/config/ads_config.json` chỉ là default lúc build (được mã hoá vào assets).
  - Bản trên Firebase **thay nguyên file**. Thiếu placement, thiếu nameSpace, hoặc nameSpace không có adunit thì
    `AdGroupUnit.enable` = false: vị trí đó không có ad mà không báo lỗi. Mục MO thêm placement phải báo MO thêm
    cả nameSpace + placement vào bản Firebase (vd A049 `native_popup_lang`).
- **Kiểu giá trị RC quyết định app đọc được hay không.** SDK (xtechcore `RemoteConfigManager`) lưu mỗi key theo kiểu
  đoán được: số nguyên → Long, số thập phân → Float, true/false → Boolean, còn lại → String.
  - Key app khai Long mà trên Firebase nhập `1.5` → lưu Float → `SharedPreferenceProperty` gặp lỗi kiểu, trả default
    mà không báo.
  - Parameter JSON (`language_config`, `noti_config`…) bị nhập thành số hoặc `true` → không còn là String → `RcGroup`
    (A048/A049) cho cả nhóm về default, chỉ log 1 lần.
  - QC thấy "đổi RC không ăn" thì kiểm kiểu giá trị trên Firebase trước.

## 2. Ads

- Build test/debug thường tự dùng ID test của Google. Kiểm placement bằng logcat:
  `adb logcat | grep -iE "iaa_|ad_impression|placement"`.
- Trước bản release, đối chiếu ID trong `ads_config` với sheet "Ad script" (cột `code`), cả file trong repo lẫn bản
  trên Firebase (bản máy đã tải: `run-as <pkg> cat files/frc_*_firebase_activate.json`, khoá `ads_config`):
  - nameSpace đang bật mà còn ID test của Google (A049 16/10: `inter_replace_reward` thêm sau, lúc đó sheet chưa có
    cột `code`);
  - 2 unit khác nhau trùng 1 ID (A049: `native_popup_confirm` chép nhầm ID của `native_survey1_high`);
  - nameSpace đang tắt (banner) được giữ ID test tới khi MO có ID. Placement đã nối trong code thì đừng xoá chỉ vì
    đang tắt: MO bật lại bằng RC sẽ không còn unit để nạp.
- Click ad rồi quay lại app: kiểm toast/noti sau click (MO-79/MO-70) và hành động "next screen" ở màn FO
  (MO-93).
- Mỗi lần reload native phải ra impression mới. Thấy native "giữ nguyên" thì soát `reset()` trước
  `loadAd()` (SDK early-return khi còn cache).

## 3. Thời gian & noti

- Đổi giờ máy, không cần root:
  `$S cmd alarm set-time <epoch_ms>`. Tính epoch bằng
  `python3 -c "from datetime import *; print(int(datetime(2026,10,8,11,0,tzinfo=timezone(timedelta(hours=7))).timestamp()*1000))"`.
- **Alarm `setAndAllowWhileIdle` có cửa sổ trễ (vài phút tới ~1 giờ).** Muốn ép nổ thì nhảy giờ **quá
  slot + cửa sổ**, vd `slot + 1h05m`. Trước khi đổi giờ, đưa máy về màn khoá **sáng màn**: Doze giữ
  alarm khi màn tắt.
- Sau `install -r`, `force-stop` hoặc đổi giờ, phải **mở app 1 lần** để app schedule lại alarm.
- **`force-stop` xoá cả alarm lẫn noti đang treo.** Muốn giết process mà giữ alarm thì dùng
  `$S "run-as $P kill -9 <pid>"` (build debug).
- Xem alarm đang chờ: `$S dumpsys alarm | grep -A4 $P`. Xem noti đang hiện:
  `$S dumpsys notification | grep -A3 $P`.
- Dark/light: `$S cmd uimode night yes` / `no`, rồi bắn lại noti. Chữ trong noti phải đọc được ở cả 2 chế
  độ.
- Quyền noti (Android 13+): `$S pm revoke $P android.permission.POST_NOTIFICATIONS` để test lại luồng
  xin quyền.
- **Xiaomi/Redmi (MIUI/HyperOS)** cần bật tay: Tự khởi động, Pin "Không giới hạn", "Hiển thị trên màn
  khoá", "Thông báo toàn màn hình". Đổi giờ hoặc cài lại app có thể làm mất các quyền này. Chi tiết ở
  `notifications.md` § MO-95.
- Emulator không đáng tin cho noti lock screen và cho ads (keyguard và ads gây nhiễu). Ưu tiên máy thật.

## 4. Mạng, back, ngôn ngữ

- **Tắt/bật mạng:** `$S svc wifi disable; $S svc data disable` (bật lại thì `enable`). Dùng cho popup
  no-internet và MO-96 (bật mạng lại ở splash).
- **Back:** test cả 3 kiểu:
  - nút back 3-phím;
  - **vuốt cạnh** (gesture navigation);
  - predictive back trên Android 14+, vì MO-81 yêu cầu inter cả khi vuốt.
- **Ngôn ngữ máy:** đổi trong Settings hoặc `$S cmd locale set-app-locales $P --locales vi` (API 33+).
  MO-33/34 cần kiểm với vài ngôn ngữ máy khác nhau.

## 5. Tracking

- **Firebase DebugView:** `$S setprop debug.firebase.analytics.app $P`, mở app, xem event real-time
  trên console. Tắt bằng `.none.`.
- Event mở lại app đi qua `app_open_from`. Mỗi đường mở lại (noti, widget, shortcut, open-with) phải
  ra đúng giá trị (MO-78).
- Có app tắt Analytics collection ở build debug (vd a036). Khi đó DebugView không thấy event: xem bằng
  logcat (tag tracking của app) hoặc build test/release.

## 6. Ma trận máy tối thiểu

- 1 máy Android 13: quyền `POST_NOTIFICATIONS`.
- 1 máy Android 14+: full-screen intent bị siết, predictive back.
- 1 máy Xiaomi: chặn nền.
- Light + dark mode.

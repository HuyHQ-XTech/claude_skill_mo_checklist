# Notification — nhóm `noti`

Mục: MO-4, MO-68, MO-69, MO-70, MO-71, MO-72, MO-73, MO-75, MO-87, MO-88, MO-89, MO-95, CC-5.

> **Ref A013** (ReVive), nhánh v1.2.7. Recipe kiểm lần cuối với commit `f784827`.
> - File `.kt` ghi tương đối từ gốc nguồn `app/src/main/java/com/example/a013_recovery/`; res/manifest ghi từ gốc repo.
> - Doc này **không chép code**. Khi làm, mở **bản hiện tại** của file/symbol được nêu ở A013. Định vị nhanh: `scripts/audit.py --item <ID> --app a013`.
> - Repo A013 có skill riêng `.claude/skills/notifications/` (SKILL.md, references/gotchas.md, references/recipes.md). Đọc thêm nếu có repo, nhưng vài chỗ đã cũ so với code (ghi ở cuối "Luật cứng").
> - Copy noti từng app: `assets/noti-content.md`. Đây là bản tham khảo; copy trong ticket MO được ưu tiên.
> - MO có thể vẽ noti riêng cho app (A049: section *MO Checklist* trong Figma của app, đích ghi bằng chữ "Vào …" dưới mỗi frame). Có frame riêng thì UI, copy và đích theo frame đó, kể cả khi lệch recipe (A049: pinned không có hàng nút, click-ads về Horoscopes; user chốt "xem figma"). Ghi chỗ lệch recipe vào báo cáo.
> - Ngoài **Chuẩn A013**, recipe ghi thêm **Ref A047 khác A013** (dùng khi user chọn ref A047) và **App đã làm — A049** (tiền lệ, không phải chuẩn). Ref A047 thì làm giống A047; phần A049 bổ sung so với A047 chỉ làm khi user đồng ý (SKILL.md bước 2).
> - QC chung (đổi giờ, dark mode, quyền, Xiaomi): `references/qc.md` §3.

## Tổng quan nhóm

### Bản đồ mục

| Mục | Noti | Trigger chuẩn | A013 (symbol chính) | `app_open_from` |
|---|---|---|---|---|
| MO-68 | Pinned (ongoing, 4 tile) | mỗi lần mở app sau bước quyền ở Splash; ngay khi vừa cấp quyền; sau reboot | `NotificationManager.setReminderPinned` | `notification_pinned` |
| MO-69 | Kill-app | app xuống nền trong FO | `NotificationManager.setKillAppNotification` ← `MainActivity.onPause` | `notification_kill` |
| MO-70 | Click ads | user bấm ad bất kỳ, RC `click_ad_action` | hook `clickedAnyAds` trong `AppNavigation.kt` (dùng lại noti kill-app) | `notification_kill` (A013); `notification_click_ads` (app có noti riêng) |
| MO-71 | Daily | alarm 8:00 và 19:00 | `scheduleReminder` + nhánh không-action của `NotificationReceiver` + `setNotification` | `notification_daily` |
| MO-72 | Shortcut/Reminder (LATER \| ACTION) | FO: màn Language, 1 lần; user cũ: Home, 1 lần/phiên | `showReminderNotification` | `notification_reminder` |
| MO-73 (= MO-4) | Win-back | alarm 11:00 và 14:00 | `scheduleWinBack`, `showWinBackNotification` | `notification_winback` |
| MO-75 | FCM (tool push nội bộ) | server | `ads/firebase/FirebaseFCM.kt` | — |
| MO-95 | Lock screen (full-screen intent) | alarm theo slot RC, overlay khi màn tắt/khoá | `LockScreenNotiManager`, `LockScreenActivity` | `notification_lock_screen` / `notification_lock_screen_un_support` |
| MO-88 | BỎ noti khi user tự mở Settings mạng | — | cờ `AppScreenState.openSetting` | — |
| MO-89 | BỎ noti foreground-service kiểu cũ | — | đã xoá `KillAppService` (commit `7f116b2`) | — |
| MO-87 | Cảnh báo giả hệ thống | **KHÔNG làm** (policy) | — | — |
| CC-5 | Noti cá nhân hoá | candidate | chưa có (tham khảo A045) | — |

### 1. NotificationManager + channel

A013 có 2 lớp quản lý noti:
- `domain/notification/NotificationManager.kt`: class, đăng ký Koin `singleOf(::NotificationManager)` trong `di/Modules.kt` (`appModule`). Lo pinned, kill-app, daily, reminder, win-back.
- `domain/notification/LockScreenNotiManager.kt`: `object`, lo lock screen. Có channel riêng `CHANNEL_LOCKSCREEN`, tạo bằng `createChannel`.

Channel tạo trong `init` của `NotificationManager` (hàm `createNotificationChannel`). Tên channel = `app_name`, riêng reminder và win-back có tên riêng (`notif_channel_reminders`, `notif_channel_updates`).

**Tạo channel ngay trước mỗi lần notify** (`createNotificationChannel` là idempotent). Khi process dậy lạnh từ alarm/boot, receiver có thể notify trước khi `Application` kịp tạo channel trên IO → noti mất im lặng.

| Hằng | id hiện tại | Importance | Dùng cho |
|---|---|---|---|
| `CHANNEL_PINNED` | `recovery_channel_pinned` | LOW | MO-68 |
| `CHANNEL_KILL_APP` | `recovery_channel_kill_app1` | HIGH | MO-69, MO-70 |
| `CHANNEL_DAILY` | `recovery_channel_daily` | HIGH | MO-71 |
| `CHANNEL_REMINDER` | `recovery_channel_reminder` | HIGH | MO-72 |
| `CHANNEL_UPDATES` | `recovery_channel_updates` | HIGH | MO-73 |
| `LockScreenNotiManager.CHANNEL_LOCKSCREEN` | `recovery_channel_lockscreen` | HIGH | MO-95 |

- **Id noti cố định cho từng loại:** `DAILY_NOTIFICATION`, `PINNED_NOTIFICATION_ID`, `KILL_APP_NOTIFICATION_ID`, `REMINDER_NOTIFICATION_ID`, `WINBACK_NOTIFICATION_ID`, `LockScreenNotiManager.NOTIFICATION_ID`.
- **Request code riêng:** các hằng `CODE_REQUEST_*`; lock screen dùng `CODE_REQUEST_LOCKSCREEN` + chỉ số slot. App khác tự đặt dải số, miễn **không trùng** (Luật 10).
- **Mọi hàm `show*`/`set*` đều đồng bộ** (dựng RemoteViews rồi `notify`) và tự chặn bằng `allowNotification`. Vì vậy gọi thẳng được từ receiver.

### 2. NotificationReceiver — định tuyến theo action

`domain/notification/NotificationReceiver.kt` khai `exported=false` trong `app/src/main/AndroidManifest.xml`, lấy `NotificationManager` qua Koin `inject`. Các nhánh theo thứ tự, mỗi nhánh `return`:
1. `NotificationManager.ACTION_DISMISS_REMINDER` (nút LATER của MO-72) → `cancelNotification(REMINDER_NOTIFICATION_ID)`.
2. `NotificationManager.ACTION_SHOW_WINBACK` → `showWinBackNotification()` rồi `scheduleWinBack()`, chạy đồng bộ.
3. `NotificationReceiver.ACTION_LOCKSCREEN` → `goAsync()`, rồi trên IO gọi lần lượt `registerScreenWatcher` → `fireLockScreenNotificationNow` → `scheduleLockScreenNotifications`. Xong thì `finish()`.
4. Không có action = alarm **Daily** → chọn ngẫu nhiên một `DailyNotificationType` → `setNotification(...)` → `scheduleReminder()`.

Action string của A013 có tiền tố cứng `com.example.a013_recovery.action.`. App khác đặt theo package của mình. Log tag `NotiReceiver` in ra action nào vừa nổ.

### 3. BootReceiver

`domain/notification/BootReceiver.kt`: manifest `exported=true`, filter `BOOT_COMPLETED`, quyền `RECEIVE_BOOT_COMPLETED`.
- Reboot xoá mọi alarm. Nếu có quyền noti, receiver `goAsync()` rồi trên IO hẹn lại:
  - daily (`scheduleReminder`);
  - win-back (`scheduleWinBack`);
  - lock screen (`LockScreenNotiManager.createChannel` + `scheduleLockScreenNotifications` + `registerScreenWatcher`);
  - và đăng lại pinned (`setReminderPinned`).
- A013 chỉ nghe `BOOT_COMPLETED`. A014 và A047 nghe thêm `TIME_SET`/`TIMEZONE_CHANGED`, vì mốc alarm tuyệt đối sẽ lệch khi user đổi giờ hoặc múi giờ.
  - **Chỉ thêm `TIME_SET` khi đã có cửa sổ ân hạn kiểu A047** (Luật 8). Không có cửa sổ thì mỗi lần đổi giờ (kể cả QC dùng `cmd alarm set-time`) app hẹn lại cùng request code và đẩy slot hôm nay sang mai.
  - Chưa có cửa sổ ân hạn thì chỉ nghe `BOOT_COMPLETED` như A013.
- xtechads tự merge `com.example.xtechads.domain.notifications.NotificationReceiver` và `BootReceiver` vào manifest mọi app.
  - Hai receiver này là no-op nếu app không dùng `BaseNotificationManager`: `BootReceiver` của SDK chỉ chạy khi pref `noti_schedule_anchor` > 0.
  - Muốn gọn thì gỡ bằng `tools:node="remove"` (Expensetracker2 đang làm vậy). Không bắt buộc.

### 4. Quyền POST_NOTIFICATIONS

- **Khai báo.** Manifest A013 không tự khai quyền này; nó đến từ manifest merge của xtechads (AAR khai `POST_NOTIFICATIONS` + `RECEIVE_BOOT_COMPLETED`) và của firebase-messaging. App không có 2 lib đó phải tự khai. Luôn kiểm merged manifest.
- **Xin quyền (API 33+) ở Splash.** `ui/screen/splash/SplashScreen.kt` — `notificationPermissionLauncher` xin 1 lần sau UMP/consent (`consentFinished`). Bỏ qua bước này nếu RC `noti_permission_trigger` = `"home"` (default `"splash"`).
- **Sau bước quyền.** Dù user cho hay không, `adsManager.passedNotificationSplash` = true. Điều này kích khối `LaunchedEffect(passedNotificationSplash)`: hẹn daily, win-back, lock screen và đăng pinned.
- **Hỏi lại ở Home.** `ui/screen/home/view/HomePermissionPrompts.kt` lo các lần hỏi sau, tối đa 1 lần/phiên. Nếu Android không hiện dialog thì hiện popup tự vẽ rồi mở Settings (`appNotificationSettingsIntents`). UI xin quyền thuộc MO-25 và MO-3.
- **Gate trước khi post.** `common/PermissionUtils.kt` — `Context.allowNotification`: API < 33 luôn `true`; API 33+ = đã có quyền runtime. `LockScreenNotiManager.hasNotificationPermission` dùng `areNotificationsEnabled()` cho API < 33.
- **State, không phải RC:** `noti_permission_requested`, `noti_prompt_session`.

### 5. Small icon

- A013 dùng glyph thương hiệu `R.drawable.ic_restore` (vector 1 path) cho pinned, kill-app, reminder, win-back và lock screen.
- **Ngoại lệ sai:** daily (`setNotification`) dùng `R.drawable.ic_app`, logo màu nhiều path → status bar hiện ô/khối. Ảnh ref MO-4/MO-71/MO-73 có noti với small icon dạng ô vuông: đó là dấu hiệu icon không phải glyph.
- Noti FCM do hệ thống vẽ khi app ở nền. Icon và màu lấy từ meta-data `com.google.firebase.messaging.default_notification_icon` (`@drawable/ic_home`) và `default_notification_color` (`@color/primary`) trong manifest.

### 6. RemoteViews + màu values-night

- **Kiểu dựng.** Pinned, kill-app, reminder và win-back dùng `NotificationCompat.DecoratedCustomViewStyle`, với `setCustomContentView` (collapse) và `setCustomBigContentView` (expand). Daily và lock screen dùng builder chuẩn (title/text + largeIcon).
- **Layout** (`app/src/main/res/layout/`): `layout_notification_pinned(_expand)`, `layout_notification_kill(_expand)`, `layout_noti_reminder_collapse/expand`, `layout_noti_winback_collapse/expand`.
- **Màu theo dark mode hệ thống.** `noti_text_primary`, `noti_text_secondary`, `noti_divider`, `noti_thumb_bg` khai ở cả `res/values/colors.xml` lẫn `res/values-night/colors.xml`; `noti_blue` cố định. Layout reminder và win-back dùng đúng các màu này.
- **Chỗ lệch ở A013:**
  - Layout kill-app để TextView title/subtitle **không có textColor**.
  - Pinned là card trắng cố định (`bg_nofification`) với chữ `@color/black`: đọc được ở cả 2 chế độ nhưng không đổi theo chế độ.
- **Nút CTA có vệt sáng quét ngang.** Dùng `ProgressBar` indeterminate có `indeterminateDrawable` là animation-list (`shimmer_indeterminate`, bản nhỏ `shimmer_indeterminate_small`) phủ lên nút, bo góc bằng `clipToOutline`. Đây là cách duy nhất có animation trong RemoteViews.
- **Tên resource đừng trùng resource noti của xtechads.** AAR xtechads (kiểm 1.8.7) có sẵn layout `layout_noti_{daily,killapp,pin,reminder,winback}_{collapse,expand}`, màu `noti_title`, `noti_body`, `noti_divider`, `noti_blue`…, drawable `bg_noti_tile`, `bg_noti_thumb`, `noti_shimmer`, `noti_clip8`, `shimmer_indeterminate`…
  - Trùng tên thì resource của app đè bản của SDK lúc merge, không báo lỗi. Hiện vô hại vì chưa app nào dùng `BaseNotificationManager` (§9), nhưng app mới nên đặt tên riêng.
  - A013 (`layout_noti_reminder_*`, `layout_noti_winback_*`, `noti_divider`, `noti_shimmer`…) và A047 (`layout_noti_daily_*`, `bg_noti_tile`, `noti_divider`…) đang trùng. A049 không trùng tên resource noti nào (`layout_noti_daily_reading_*`, `noti_line`, `bg_noti_feature_tile`).

### 7. Deep link quay về qua Splash (MO-78)

- **PendingIntent.** Mọi `PendingIntent.getActivity` của noti trỏ `MainActivity` (`launchMode="singleTask"`), với:
  - `action = ACTION_VIEW`;
  - flags `NEW_TASK | CLEAR_TASK`;
  - extras: `Constant.KEY_OPEN_FROM` (Int `OPEN_FROM_*`), tuỳ chọn thêm `KEY_OPEN_TO` (Int `OPEN_TO_*`) và `KEY_AUTO_SCAN`.
- **Mở app.** `MainActivity.onCreate`, chỉ khi `savedInstanceState == null`:
  1. Tăng `sessionNumber`.
  2. `initArgs()` lưu `prefs.openTo` (+ `autoStartScan`).
  3. `trackAppOpenFrom(intent)`.
- **Splash** chạy ads như một lần mở thường, rồi `goNextScreen`:
  - đang FO → màn FO kế;
  - `OPEN_TO_UNINSTALL` → màn Uninstall;
  - còn lại → Home.
- **Điều hướng tới tính năng.** `HomeScreen` (LaunchedEffect đầu) đọc `prefs.openTo`, điều hướng tới tính năng, rồi reset về `OPEN_TO_DEFAULT`.
- **App đang mở sẵn.** `MainActivity.onNewIntent` nhận extras có `KEY_OPEN_FROM` thì khởi động lại `MainActivity` với `CLEAR_TASK`. Lý do: `recreate()` khôi phục backstack Nav3 và bỏ qua Splash.
- **Từ lock screen.** `LockScreenActivity` mở app kèm `prefs.openTo` + `prefs.openFromPending` để dự phòng mất extras. Khi extras không có `KEY_OPEN_FROM`, `trackAppOpenFrom` đọc `openFromPending`.
- **Mở lại từ Recents.** `MainActivity` đã `finish` (back, Exit) mà user mở lại từ Recents thì hệ thống start lại bằng intent gốc của task (có thể là intent của noti đã bấm), kèm cờ `FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY`.
  - Có cờ này thì bỏ qua extras (A047, A049 `MainActivity.initArgs`). Không bỏ thì app log lại `app_open_from` của noti cũ và mở lại tính năng cũ.
  - A013 (`initArgs`, `trackAppOpenFrom`) chưa kiểm cờ này.

### 8. Tracking `app_open_from`

- `MainActivity.trackAppOpenFrom` log event `app_open_from`, param `open_from`. Các giá trị:
  - `notification_daily`, `notification_pinned`, `notification_kill`, `notification_reminder`, `notification_winback`;
  - `notification_lock_screen` hoặc `notification_lock_screen_un_support` (tuỳ `canUseFullScreenIntent()` lúc mở);
  - `widget`, `shortcut_<tính năng>`.
- **App khác dùng biến thể:** `notification_win_back`, `notification_shortcut`, `notification_click_ads`, `notification_lockscreen`, `open_from_notification_*`, `lockscreen`. A045, A047, a044 và A049 còn có thêm event `notification_clicked` (param loại noti). App đã phát hành thì giữ giá trị đang có (conventions.md §1); app mới theo A013.
- A013 không log event "đã hiện noti", trừ `notification_lockscreen_un_support`. `xtechads/docs/TRACKING_EVENTS_STATUS.md` xếp event notification vào nhóm cố ý bỏ qua.

### 9. Dùng SDK hay manager tầng app?

- **A013 dùng manager tầng app**, không dùng `BaseNotificationManager` của SDK (`di/Modules.kt` không đăng ký nó). Rà 16 repo: chưa app production nào dùng `BaseNotificationManager`, chỉ demo của SDK (`xTechSDK/app/.../domain/notification/ReviveNotiFactory.kt`).
- **SDK có gì.** xtechads `domain/notifications/`, có trong AAR ít nhất từ 1.4.6 tới 1.8.2:
  - `BaseNotificationManager`: `showPinned`, `showKillApp`, `showDaily`, `showReminder`, `showWinback`, `showClickAds`, `show(NotiSpec)`, `cancel`.
  - `NotiHostConfig`: `smallIcon`, `autoPin`, `autoSchedule`, `killAppWhen`, `clickAdsWhen`.
  - `NotiContentFactory`: content của từng loại, `dailyTimes()` (mặc định 8:00/19:00), `winbackTimes()` (mặc định 11:00/14:00).
  - `NotificationScheduler`, `NotificationReceiver`, `BootReceiver`, layout `layout_noti_*`.
- **Hạn chế của SDK:**
  - Không có lock screen/FSI.
  - Click-ads chỉ bắn khi app xuống nền (`onStop` + `clickAdsWhen`), dạng BigPicture, không đọc `click_ad_action`.
  - Kill-app bắn ở mọi lần `ProcessLifecycleOwner` `onStop`.
  - Mở app bằng launcher intent (`getLaunchIntentForPackage`) + extras.
  - Màu `noti_*` của SDK không có `values-night`, nên app phải override cả `values-night`.
  - Trong AAR 1.8.2, `NotificationScheduler` bị R8 đổi tên (`t.j`) nên không gọi trực tiếp được.
  - Demo đăng ký `BaseNotificationManager` bằng `single` thường, nên lifecycle callback chỉ gắn khi có chỗ `get()`.
- **Doc SDK sai so với code.** `xTechSDK/docs/NOTIFICATION_USAGE.md` (và CHANGELOG mục 2026-09-07) mô tả `NotiContentRes`, RC `enable_noti_*`, `consumeClickType`, `EXTRA_NOTI_TYPE`, event `notification_clicked`, và việc tự đăng ký `createdAtStart`. Code **không có** những thứ này; đừng dựa vào.
- **Quyết định:** chuẩn là manager tầng app theo A013, vì nó đủ lock screen, logic FO/phiên, routing `OPEN_TO`, tracking và layout theo Figma.
- **Khi nào dùng SDK:** chỉ cho app mới tinh cần nhanh 5 loại cơ bản và chấp nhận layout của SDK. Khi đó app vẫn phải:
  - tự đăng ký `NotiContentFactory`, `NotiHostConfig` và `BaseNotificationManager` (tạo sớm);
  - override màu `noti_*` cả `values-night`;
  - tự parse `KEY_OPEN_FROM`/`KEY_OPEN_TO` ở `MainActivity`;
  - tự làm lock screen.

## Luật cứng

Gom từ skill notifications của A013 (SKILL.md, gotchas.md), docs A047 (`docs/NOTIFICATIONS.md`), A045 (`docs/features/notification-*.md`) và rà code. Mỗi luật là một bug đã từng xảy ra.

1. **Small icon phải đơn sắc:** một silhouette, nền trong suốt. Hệ thống chỉ dùng kênh alpha; icon launcher hoặc logo màu sẽ thành ô/khối. Không dùng `mipmap/ic_launcher` hay `img_logo`. Chưa có glyph thì vẽ một vector trắng trên nền trong suốt.
2. **Màu chữ trong RemoteViews:**
   - Dùng `@color/noti_*` khai ở cả `values/` lẫn `values-night/`.
   - **Không** dùng `?android:attr/textColor*`. Theme app có thể cố định tối (A013 dùng `Theme.AppCompat.NoActionBar`), khi đó chữ trắng trên shade sáng sẽ biến mất.
   - Không để TextView thiếu `textColor`.
   - `values-night` theo dark mode **hệ thống**, chính là cái shade dùng.
   - Test: đổi dark mode hệ thống rồi **bắn lại** noti; noti cũ có thể không vẽ lại.
3. **RemoteViews chỉ inflate view framework:** `FrameLayout`, `LinearLayout`, `RelativeLayout`, `GridLayout`, `TextView`, `ImageView`, `ImageButton`, `Button`, `ProgressBar`, `Chronometer`, `TextClock`…
   - Không dùng AppCompat/Material/custom view, không dùng `<View>` trần (divider làm bằng `ImageView` hoặc `LinearLayout` 1dp).
   - Inflate lỗi thì noti **biến mất im lặng**.
   - Ảnh chỉ đưa vào bằng resId hoặc Bitmap.
4. **Layout custom:**
   - Collapse cao khoảng 64dp. Expand không đặt `maxLines`/`ellipsize` cho title/body, để hiện trọn câu (A047).
   - Ảnh lớn bọc trong khung `layout_weight` để nút CTA không bị cắt khi SystemUI giới hạn chiều cao.
   - Muốn ảnh bo góc thì phải có `clipToOutline`.
5. **Receiver không được bắn coroutine trần rồi `return`.** Process chỉ chắc chắn sống trong `onReceive`, nên coroutine trần dễ không chạy ("lúc bắn lúc không").
   - Việc đồng bộ: gọi thẳng.
   - Việc async (decode bitmap, IO): dùng `goAsync()` + `finally { finish() }`. A045 và A047 thêm `withTimeoutOrNull(8s)`.
   - Hàm `schedule*` chỉ là binder call nhanh, nên để đồng bộ.
   - Nhánh daily của A013 vẫn vi phạm luật này: `launch` không có `goAsync`, và `scheduleReminder` cũng `launch`.
6. **Một receiver phục vụ nhiều alarm:**
   - Tách nhánh theo `intent.action`, mỗi nhánh `return`.
   - Không lồng nhánh này trong nhánh khác, nếu không win-back sẽ bắn kèm daily.
   - Daily của A013 là nhánh "không action"; app mới nên đặt action riêng.
7. **Alarm one-shot, không chính xác.**
   - `setAndAllowWhileIdle(RTC_WAKEUP)` chỉ nổ một lần và có thể trễ tới khoảng 1 giờ trong Doze.
   - Vì vậy phải: (a) mỗi lần nổ tự hẹn lần kế; (b) hẹn lại mỗi lần mở app ở Splash; (c) `BootReceiver` hẹn lại sau reboot.
   - Không xin `SCHEDULE_EXACT_ALARM`, không dùng `setRepeating`.
8. **Hẹn lại có thể đè mất alarm đang chờ.**
   - Cùng request code + `FLAG_UPDATE_CURRENT` sẽ thay alarm cũ.
   - Ví dụ: slot 11:00 đã qua nhưng alarm hôm nay chưa nổ (đang trong cửa sổ trễ). Mở app lúc 11:20, code đẩy sang mai → hôm nay mất noti.
   - A047 xử lý bằng cửa sổ ân hạn 2 giờ cộng mốc đã hẹn/đã bắn trong prefs (`noti_armed_at_<req>`, `noti_fired_day_<req>`), đồng thời không bắn bù ngay cho slot chưa từng hẹn.
   - A013 chưa có cơ chế này: slot đã qua là đẩy sang mai.
9. **`POST_NOTIFICATIONS`:** kiểm merged manifest, xin runtime, và chặn **mọi** `notify` bằng `allowNotification`. User từ chối quyền thì app im lặng, không crash.
10. **Mỗi PendingIntent một request code riêng:** alarm, content, từng tile, từng nút.
    - Cùng request code + `filterEquals` (extras không tính) = cùng PendingIntent; `FLAG_UPDATE_CURRENT` sẽ ghi đè extras.
    - Hậu quả: tap noti cũ ra `open_from` của noti mới.
    - A013 đang trùng `41999331` giữa kill-app và daily.
11. **Id và channel cố định:**
    - Id noti cố định theo loại, để noti mới thay noti cũ thay vì chồng lên.
    - Channel đã phát hành thì không đổi id tuỳ tiện.
    - Importance của channel không đổi được sau khi tạo. Muốn đổi thì tạo id mới (vd hậu tố `…1`) và `deleteNotificationChannel` id cũ.
    - Channel phải tồn tại trước `notify`; thiếu channel thì hệ thống bỏ noti im lặng (A047 gọi `ensureChannels()` ngay trước mỗi `notify`).
12. **Noti mở app qua `MainActivity`:** `ACTION_VIEW`, `NEW_TASK|CLEAR_TASK`, `KEY_OPEN_FROM` + `KEY_OPEN_TO`. Như vậy luôn đi qua Splash (MO-78) và log `app_open_from`. Không mở thẳng Activity tính năng.
13. **Ngôn ngữ của noti bắn từ process lạnh.**
    - Noti bắn từ alarm hoặc boot phải dựng content bằng context bọc ngôn ngữ user chọn (`LanguageManager.wrapContextWithLocale(app, prefs.languageSelected)`).
    - A013 chỉ làm ở lock screen (`LockScreenNotiManager.localizedContext`).
    - Daily/win-back dùng `app.getString`. Process dậy bởi alarm chưa qua `MainActivity`, nên có thể ra ngôn ngữ máy.
14. **Noti kiểu kill-app/promo không bắn khi:**
    - ad full-screen đang hiện (`isShowingAds`);
    - vừa bấm ad (`disableAdResumeOneTime`, A047, A049; xem Bẫy MO-70);
    - app tự mở Settings/app khác (MO-88);
    - đang đổi cấu hình (`isChangingConfigurations`, A047).
    - Ngoài ra phải huỷ noti kill-app ở `onResume`.
15. **Không dùng `CATEGORY_ALARM` cho noti quảng bá.** Category này xuyên chế độ Không làm phiền, và FSI không cần nó (A047). A013/A014 đang set → cần chốt (MO-95).
16. **Không giả mạo noti hay cảnh báo hệ thống (MO-87). Không tự bật lại FSI hay spam để lách giới hạn của Android.**
17. **Noti ongoing:** từ Android 14 user vuốt xoá được, trừ khi máy đang khoá hoặc user bấm "Xoá tất cả". Vì vậy pinned phải được đăng lại mỗi lần mở app.
18. **Preload ad khi bắn noti** (A014/A047/A045 `preloadInterSplashOnNoti`) chỉ làm khi app đang foreground và ở main thread. Không resolve AdsManager trong receiver chạy nền. A045 hiện gọi từ nền (có thể kéo `ensureAdsInitialized()`), đừng chép.
19. **Helper "bắn sau 30 giây" để debug phải xoá trước khi release.** Không đặt nó trong hàm `schedule*` tự lặp, vì nó sẽ lặp mãi (A013 gotchas).
20. **Nút trong custom view không ăn `autoCancel`.** `setAutoCancel(true)` chỉ huỷ noti khi bấm vào thân noti (content intent). Bấm nút/tile gắn bằng `setOnClickPendingIntent` thì app mở nhưng noti vẫn nằm lại.
    - Mở app bằng noti nào thì huỷ noti đó ở lượt mở: A049 `NotificationManager.cancelOpenedFrom`, gọi trong `MainActivity.initArgs` (daily, win-back, shortcut, click-ads). Pinned không huỷ; kill-app và lock screen đã huỷ ở `onResume`.
    - A013 (nút CTA của reminder, win-back) và A047 chưa làm.
21. **Noti dùng custom view vẫn set `setContentTitle`/`setContentText`** làm chữ dự phòng. Thiếu thì khi noti bị gộp nhóm, shade hiện "Expand to view" (A049, 10/2026). A013 (pinned, kill-app, reminder, win-back) và A047 (mọi noti custom view) chưa set.

**Chỗ skill notifications của A013 đã cũ so với code `f784827`:**
- Reminder không còn bắn ở Splash; nay bắn ở Language FO và Home (MO-72).
- Channel reminder là HIGH, không phải DEFAULT.
- Daily vẫn dùng `ic_app`, không phải `ic_restore`.
- Request code daily khác với bản trong recipes.md.
- recipes.md chưa có lock screen.

## MO-4 — Win-back noti (dòng Protect Set up)

- **Yêu cầu:** dòng "notification win-back" ở block *Protect Set up*, cùng Figma node `512-1263` với MO-73.
- **Nghiệm thu:** như MO-73.
- **Chuẩn A013:** **cùng một tính năng với MO-73** (Win-Back 11h và 14h). Không làm riêng; làm và nghiệm thu theo § MO-73. `detect` của 2 mục giống nhau.
- **Bẫy:**
  - Trạng thái 2 dòng trên sheet lệch nhau (a028, a031, a032: MO-4 = 0 nhưng MO-73 = 1).
  - Code đang checkout của A028 và a031 **không có** win-back nào. Vậy MO-4 = 0 khớp code, còn MO-73 = 1 thì không.
  - Đề nghị MO gộp MO-4 vào MO-73, hoặc chốt MO-4 chỉ là dòng kiểm "có win-back". Báo khi cập nhật sheet.
- **QC:** như MO-73.

## MO-68 — Noti pinned

- **Yêu cầu:**
  - Noti ghim cố định (ongoing) trên thanh thông báo, đăng khi user mở app.
  - Mỗi ô tính năng mở đúng luồng.
  - Figma `605-3536` (ref `assets/refs/MO-68-1.jpg`): title, subtitle, 4 tile, và hàng nút Later · Explore · Try now.
- **Nghiệm thu:**
  - Đúng content.
  - Bấm từng tile vào đúng tính năng, đi qua Splash (MO-78).
  - Đọc được ở cả dark lẫn light.
  - Không vuốt xoá được (Android ≤ 13; Android 14+ xem Bẫy).
  - Mở app nhiều lần vẫn chỉ có 1 pinned.
  - Reboot xong vẫn có.
- **SDK:** partial. Có `BaseNotificationManager.showPinned()` + `NotiContentFactory.pinnedTitle()/pinnedTiles()` + `NotiHostConfig.autoPin`, nhưng layout SDK không có hàng nút Figma và chưa app nào dùng.
- **Chuẩn A013:** `domain/notification/NotificationManager.kt` — `setReminderPinned(context)`.
  - **4 tile = 4 `PendingIntent` riêng**, mỗi cái một request code, cùng `OPEN_FROM_PINNED_NOTIFICATION` và lần lượt `OPEN_TO_RECOVERY_PHOTO` / `OPEN_TO_ENHANCE` / `OPEN_TO_JUNK` / `OPEN_TO_PROTECTOR`. Content intent = tile đầu.
  - **Builder:** `CHANNEL_PINNED` (LOW), `setOngoing(true)`, `setAutoCancel(false)`, `setSilent(true)`, `setGroup(packageName)`. Id `PINNED_NOTIFICATION_ID`.
  - **Layout:** `layout_notification_pinned.xml` (collapse: 4 icon) và `layout_notification_pinned_expand.xml` (icon + nhãn).
  - **Được gọi từ:**
    - `ui/screen/splash/SplashScreen.kt`, khối `LaunchedEffect(passedNotificationSplash)` (mỗi lần mở app);
    - callback cấp quyền trong `SplashScreen`;
    - `HomePermissionPrompts` → `onNotificationAllowed`;
    - `BootReceiver`.
  - **Lệch Figma:** A013 thiếu title, subtitle và hàng nút. a016 làm đúng Figma: `a016_GPS_Kinglets` `domain/notification/NotificationManager.kt` → `setReminderPinned` + `res/layout/layout_notification_pinned_expand.xml`. Bản đó có title, sub, 4 tile; Explore/Try mở Home; Later bị comment.
- **Remote config:** A013 không có. Kill-switch ở app khác: `enable_noti_pinned` (Boolean, default true — A045, A047, a044). Chỉ thêm khi MO yêu cầu.
- **Placement / tracking:**
  - Channel `recovery_channel_pinned` (LOW), id `PINNED_NOTIFICATION_ID`.
  - Extras: `KEY_OPEN_FROM = OPEN_FROM_PINNED_NOTIFICATION` + `KEY_OPEN_TO`.
  - `app_open_from` = `notification_pinned` (A045/A047 dùng `open_from_notification_pinned`).
- **Cách làm:**
  1. **Layout.** Dựng layout RemoteViews collapse/expand theo Figma `605-3536`, copy lấy ở `assets/noti-content.md` mục MO-68. Tile là `LinearLayout`/`FrameLayout` có id riêng; màu dùng `noti_*` + `values-night` (Luật 2–4). Cần bản đủ title/sub/nút thì xem layout của a016.
  2. **Hàm `setReminderPinned`** trong NotificationManager của app:
     - mỗi tile và mỗi nút một `PendingIntent` với request code riêng;
     - extras: `OPEN_FROM_*PINNED*` + `OPEN_TO` của tính năng;
     - builder như A013.
     - Đọc `NotificationManager.setReminderPinned` ở A013 (bản hiện tại) để lấy chi tiết.
  3. **Wire 3 chỗ:**
     - Splash sau bước quyền (A013: khối `LaunchedEffect(passedNotificationSplash)`);
     - callback cấp quyền, ở cả Splash lẫn popup Home;
     - `BootReceiver`.
  4. **Routing và tracking.** Route các `OPEN_TO` mới ở chỗ app xử lý sau Splash (A013: `HomeScreen`, LaunchedEffect đọc `prefs.openTo`). Thêm giá trị vào `MainActivity.trackAppOpenFrom`.
  5. **App XML/Fragment** (a031, a033): đăng pinned ở Activity/Fragment Splash sau bước quyền; route bằng `startActivity`/NavController. **App không SDK** (a028, a036, a041): làm y hệt, vì noti không phụ thuộc SDK ads.
  - **App đã làm — A049** (port A047, 10/2026): `NotificationManager.showPinnedNotification`; tile là enum `PinnedNotiTile` (đích, nhãn, icon), request code `CODE_PINNED + index`.
    - Gọi ở `SplashViewModel.onNotificationAnswered` (mỗi lần mở app, sau bước quyền), `HomeViewModel.onNotificationAnswered` (cấp quyền ở Home), `BootReceiver` (chỉ `BOOT_COMPLETED`).
    - Layout theo frame Figma của app: title, body, 4 tile, không có hàng nút.
- **Bẫy:**
  - Android 14+: user **vuốt xoá được** noti ongoing (Luật 17). QC đừng báo bug "vuốt được" trên máy 14+.
  - Giữ channel LOW. Nâng lên HIGH thì pinned sẽ kêu/heads-up mỗi lần mở app.
  - Collapse chỉ đủ chỗ cho icon; nhãn để ở expand.
  - Nút "Later" trên noti ongoing không có nghĩa "xoá", nên a016 bỏ nó. Ticket đòi có Later thì chốt hành vi với MO.
  - Ảnh tile dạng bitmap (webp/png) không đổi màu theo dark mode. Muốn đổi thì dùng vector có `fillColor` trỏ màu `noti_*` có bản `values-night` (A049 `ic_noti_tile_*` + `noti_tile_content`).
  - A049 tắt badge riêng channel pinned (`setShowBadge(false)` trong `createChannel`): noti ongoing không nên tính vào chấm thông báo trên icon app. A013, A047 để `true` cho mọi channel.
- **QC:**
  - Mở app → kéo shade thấy pinned, không kêu. Expand xem đủ nội dung.
  - Bấm từng tile/nút → Splash (ads) → đúng tính năng; `app_open_from` = `notification_pinned`.
  - Kiểm dark và light.
  - Mở app 3 lần vẫn chỉ 1 pinned. Reboot → pinned tự hiện.
  - Từ chối quyền noti → không có pinned. Cấp lại ở popup Home → pinned hiện ngay.

## MO-69 — Noti kill app

- **Yêu cầu:**
  - Noti kéo user quay lại khi user rời app (app bị đưa xuống nền). Figma `525-20` (ref `assets/refs/MO-69-1.jpg`).
  - Ghi chú sheet: *"Thống nhất show ở FO (remote config show all)"* — mặc định chỉ bắn trong FO, có RC để bật cho mọi phiên.
  - Thực chất là "app xuống nền", không phải process bị kill (A047 cũng ghi rõ điều này).
- **Nghiệm thu:**
  - Trong FO, thoát app (Home/Recents) → noti hiện, có content + nút CTA.
  - Tap noti → Splash → app.
  - Quay lại app → noti tự biến mất.
  - Không bắn khi đang hiện ad full-screen, hoặc khi app tự mở Settings (MO-88).
  - Kiểm dark/light.
  - Sau FO không bắn, trừ khi RC "show all" bật.
- **SDK:** partial. `BaseNotificationManager.showKillApp()` + `NotiHostConfig.killAppWhen`; SDK bắn ở `ProcessLifecycleOwner.onStop` khi lambda trả `true`.
- **Chuẩn A013:** `NotificationManager.setKillAppNotification()`.
  - **Layout:** `layout_notification_kill.xml` / `layout_notification_kill_expand.xml`. Text tĩnh nằm trong XML; bản expand có ảnh lớn và nút có vệt sáng.
  - **Builder:** channel `CHANNEL_KILL_APP` (HIGH), auto-cancel, id `KILL_APP_NOTIFICATION_ID`.
  - **Content intent:** `MainActivity` + `OPEN_FROM_KILL_NOTIFICATION`, không có `OPEN_TO` → vào Home.
  - **Trigger** ở `MainActivity.onPause`, khi đủ cả 3 điều kiện:
    - `prefs.firstOnboard` (true cho tới khi `HomeScreen` lần đầu set `false`);
    - `!adsManager.isShowingAds`;
    - `!AppScreenState.openSetting` (MO-88).
  - **Huỷ** ở `MainActivity.onResume`: `cancelNotification(KILL_APP_NOTIFICATION_ID)`.
  - **A013 thiếu** RC "show all" mà sheet yêu cầu.
- **Remote config:** A013 chưa có, và rà 16 repo **không app nào** có key "FO hay mọi phiên". A049 từng có field `kill_app.show_all` (Boolean, false) trong JSON `noti_config`; user bỏ ngày 15/10/2026 vì chưa app nào có RC này.
  - Đề xuất key mới `noti_kill_app_show_all` (Boolean, default `false`): `false` = chỉ bắn trong FO; `true` = bắn ở mọi lần app xuống nền. Chỉ thêm khi MO chốt tên và user yêu cầu (Luật cứng 10, Q21).
  - Kill-switch đang có ở A045, A047, a044 là chuyện khác: `enable_noti_kill_app` (Boolean, true) chỉ bật/tắt hẳn noti.
- **Hiện trạng các app:**
  - Chỉ FO: A013, a016, a031 (bắn ở `onDestroy`), a036, a037, a039, a041, Langofy, a033 (chỉ khi `FirstOpenActivity` đang hiện).
  - **Mọi phiên** (lệch chuẩn mới): A014 (debounce 300 ms), a27, A028, a034, a044, A045, A047, A048, A049 (từ 15/10/2026, user chốt ref A047 sau bug "ở Home kill / minimize không có noti").
- **Placement / tracking:**
  - Channel `recovery_channel_kill_app1` (HIGH), id `KILL_APP_NOTIFICATION_ID`.
  - Extras: `OPEN_FROM_KILL_NOTIFICATION`.
  - `app_open_from` = `notification_kill`. Biến thể: `open_from_notification_killed` (A045, A047), `notification_killed` (a031), `notification_kill_ai_tutor` (Langofy).
- **Cách làm:**
  1. **Layout.** Dựng theo Figma `525-20`, copy lấy ở `assets/noti-content.md` mục MO-69. Set text bằng `setTextViewText`, đừng để text tĩnh trong XML. Màu dùng `noti_*`.
  2. **Hàm `setKillAppNotification`:** đồng bộ, có gate quyền, PendingIntent với request code riêng.
  3. **Trigger** ở `MainActivity.onPause` (như A013) hoặc `onStop` (như A045, để tránh dialog quyền hệ thống làm Activity pause). Điều kiện:
     - đang FO (app có key `noti_kill_app_show_all` thì thêm: **hoặc** key = true);
     - và không đang hiện ad (`!isShowingAds`);
     - và không có cờ "app tự mở Settings/app khác" (MO-88);
     - và không vừa bấm ad (`disableAdResumeOneTime`), bắt buộc khi app có noti click-ads riêng (MO-70);
     - và không `isChangingConfigurations`.
  4. **Huỷ** noti ở `onResume`. Thêm `notification_kill` vào `trackAppOpenFrom`.
  5. Đọc `MainActivity.onPause/onResume` và `NotificationManager.setKillAppNotification` ở A013 (bản hiện tại).
  6. **App XML/Fragment:** đặt cùng chỗ (`onPause`/`onStop` của Activity chính). **App không SDK** (a028, a036, a041): cờ "đang hiện ad" lấy từ lớp ads tự viết của app.
  - **Ref A047 khác A013:** bắn ở `MainActivity.onPause` ở mọi phiên, chỉ có kill-switch `enable_noti_kill_app`. Bỏ lượt khi `isChangingConfigurations`, `isShowingAds` hoặc `disableAdResumeOneTime`.
  - **App đã làm — A049** (port A047, 10/2026):
    - Trigger ở `MainActivity.onStop`, vì dialog quyền hệ thống chỉ làm Activity pause.
    - Bỏ lượt khi `isChangingConfigurations`, `isAdOnScreen` (gồm `isShowingAds`, `isShowingAdResume`, `showLoadingDialog`), `disableAdResumeOneTime` (vừa bấm ad, MO-70) hoặc `ExternalScreen.opening` (MO-88).
    - `NotificationManager.showKillAppNotification` chỉ kiểm kill-switch `noti_config.kill_app.enable` như A047, bắn mọi phiên. Huỷ noti ở `onResume`.
    - Bản trước có gate FO trong hàm này, nên QC báo bug "ở Home kill / minimize không có noti kill app". Ngày 15/10/2026 user chốt noti theo A047 và bỏ gate FO.
- **Bẫy:**
  - `onPause` còn chạy khi dialog quyền hoặc sheet hệ thống phủ lên, khi multi-window, khi đổi cấu hình → bắn nhầm. A045, A048 và A049 chuyển sang `onStop`; A047 chặn `isChangingConfigurations`.
  - Request code content intent của A013 (`41999331`) trùng với daily (Luật 10).
  - A013 dùng lại noti này cho click-ads (MO-70), nên `onResume` cũng huỷ luôn noti click-ads.
  - Nhiều app **không huỷ** noti ở `onResume` (a016, a036, a037, a039, a041). User quay lại app mà noti vẫn nằm đó.
  - Đổi các app đang bắn mọi phiên sang "FO + RC" là đổi hành vi của app đã phát hành. Phải báo MO trước khi sửa.
  - **Không** dùng foreground service/`onTaskRemoved` để bắt "kill app" (đó là bản cũ, MO-89).
- **QC:**
  - Cài mới (FO). Tại Language hoặc Onboarding bấm Home → noti hiện. Tap → Splash → app; `app_open_from` = `notification_kill`.
  - Mở lại app → noti mất.
  - Trong lúc ad full-screen hiện, bấm Home → không có noti.
  - Popup mất mạng → "Enable" → Settings → không có noti (MO-88).
  - Sau khi vào Home (hết FO), thoát → không có noti. App có key `noti_kill_app_show_all` thì bật lên → có (RC áp từ lần mở sau, `references/qc.md` §1).
  - Kiểm dark/light.

## MO-70 — Noti clicked ads

- **Yêu cầu:**
  - User bấm vào **bất kỳ** ad nào (native, banner, inter…) → hiện noti kéo user quay lại. Figma `525-20` (cùng khung với kill-app).
  - RC chọn giữa noti và toast. Nhánh toast là MO-79.
- **Nghiệm thu:**
  - `click_ad_action` = `"notification"` → bấm ad ở mọi vị trí đều có noti.
  - Giá trị khác → toast (MO-79).
  - Tap noti → Splash → app.
  - Kiểm content, dark/light.
- **SDK:** partial. `BaseAds.clickedAnyAds` (xtechads `ads/base/BaseAds.kt`, SDK gọi trong `onAdClicked()`) là hook bắt buộc. `BaseNotificationManager.showClickAds()` chỉ bắn khi app xuống nền và không đọc `click_ad_action` → không dùng.
- **Chuẩn A013:** `AppNavigation.kt`, LaunchedEffect gán `adsManager.clickedAnyAds`:
  1. gọi `interSplashClickAction.onClicked()`;
  2. nếu `prefs.clickAdAction == "notification"` → `notificationManager.setKillAppNotification()` (**dùng lại noti kill-app**, cùng id/channel/content);
  3. ngược lại → toast `R.string.don_t_forget_your_lose_files`.
- **Remote config:** `click_ad_action` (String, `"notification"` | `"toast"`).
  - Default trong code A013 là `"toast"` (`SharedPrefs.clickAdAction`). Ghi chú sheet MO-79 cho biết trên Firebase A013 đang để `"notification"`.
  - Default ở app khác: `"toast"` (A014, a016, a037, Langofy); `"notification"` (a27, a034, a044, A045, A047).
  - Alias: `click_ads_type` (a036, default `"noti"`), `clicked_ads_type_msg` (a041, default `"noti"`), `show_click_ads_noti` (a033, Boolean `true`). a039 luôn bắn, không có RC.
- **Hiện trạng các app** (mọi app đều bắn **ngay lúc click**, không app nào đợi app xuống nền):
  - Dùng lại noti kill-app: A013, a016, a27, a034.
  - Cùng layout kill-app nhưng `OPEN_FROM` riêng: a037, a039.
  - Có noti riêng: A014 `setClickAdsNotification`; a033 `setClickAdsNotification`; a036 `showClickAdsNotification`; a041 `setClickedAdsNotification`; Langofy `setClickAdsNotification`; a044, A045, A047 và A049 `showClickAdsNotification`. A047 còn lưu backstack lúc bấm ad vào pref `click_ads_stack` để mở lại đúng màn.
  - Chỉ toast: A028, a031.
- **Placement / tracking:**
  - A013 không phân biệt được với kill-app, vì cả hai cùng `OPEN_FROM_KILL_NOTIFICATION` → `app_open_from` = `notification_kill`.
  - App có noti riêng log `notification_click_ads` (A045/A047: `open_from_notification_click_ads`; a041: `notification_clicked_ad`).
  - Langofy dựng noti click-ads bằng builder có `OPEN_FROM` kill cứng, nên vẫn log như kill.
- **Cách làm:**
  1. Tìm chỗ app gán `clickedAnyAds` (grep `clickedAnyAds`; mỗi app để một chỗ khác nhau: AppNavigation, AdsEffects, MainApp, App.kt…). Chỉ gán **một** lần, ở composable/Activity sống suốt vòng đời app.
  2. Đọc `click_ad_action`: `"notification"` → gọi hàm noti, còn lại → toast.
  3. **Noti:**
     - Tối thiểu: dùng lại noti kill-app như A013.
     - Nên có hàm riêng: id riêng, `OPEN_FROM_*CLICK_ADS*`, `app_open_from` = `notification_click_ads`, copy MO-70 trong `assets/noti-content.md`. Tham khảo `setClickAdsNotification` của A014 hoặc `showClickAdsNotification` của A047.
  4. Đọc khối `clickedAnyAds` trong `AppNavigation.kt` ở A013 (bản hiện tại).
  5. **App không SDK** (a028, a036, a041): không có `BaseAds.clickedAnyAds`; tìm callback click trong lớp ads tự viết. a036 dùng RC `click_ads_type`.
  - **Ref A047 khác A013:** noti riêng `NotificationManager.showClickAdsNotification` (id riêng, `OPEN_FROM_NOTIFICATION_CLICK_ADS`); hook ở `ads/AdsEffects.kt` `ClickAdsEffect`, gắn trong navigation. Lúc bấm ad lưu backstack vào `click_ads_stack`; noti mở với `OPEN_TO_LAST_SCREEN`, rồi `SplashViewModel.restoreClickAdsStack` dựng lại đúng màn.
  - **App đã làm — A049** (port A047, 10/2026): như A047, nhưng đích theo frame Figma của app (Horoscopes); hạ tầng `click_ads_stack` vẫn giữ. Hook gán trong `DisposableEffect(backStack)`; lúc dispose chỉ gỡ khi `clickedAnyAds` còn là lambda của mình. Default `click_ad_action` trong code là `"notification"`.
- **Bẫy:**
  - Bấm ad thường mở trình duyệt/Store → app xuống nền. Ở A013 trong FO, kill-app cũng bắn, nhưng cùng id nên chỉ còn 1 noti.
  - **Có noti click-ads riêng (khác id kill-app) thì trigger kill-app phải bỏ lượt ngay sau khi bấm ad**, nếu không bấm ad trong FO sẽ ra 2 noti. SDK `BaseAds.onAdClicked` set `disableAdResumeOneTime` trước khi gọi `clickedAnyAds`; A047, A049 kiểm cờ này ở trigger kill-app.
  - Noti cùng id kill-app bị huỷ ở `MainActivity.onResume`, tức là biến mất khi user quay lại app.
  - RC = `notification` mà chưa có quyền `POST_NOTIFICATIONS` thì không hiện gì, cũng không toast: A013
    `setKillAppNotification` (gate `allowNotification`), A047/A049 `NotificationManager.showPromo` (gate
    `canPost`) đều return sớm. Có fallback toast hay không: open-questions Q51.
  - Default trong code (`toast`) khác giá trị trên Firebase → QC phải biết giá trị RC thật (`references/qc.md` §1).
  - Đích khi tap noti lệch giữa các app: Home (A013, dùng lại kill-app), màn đang đứng lúc bấm ad (A047 `OPEN_TO_LAST_SCREEN`), tính năng theo Figma (A049 Horoscopes). Ticket/Figma không ghi đích thì theo ref và báo trong báo cáo (open-questions Q43).
- **QC:**
  - RC = `notification`: bấm native, banner, inter… lần lượt → mỗi lần có noti. Tap → Splash → app.
  - RC = `toast` → chỉ toast.
  - Quay lại app → noti (dùng chung id kill-app) mất.
  - App có noti riêng (A047, A049): bấm ad trong FO → chỉ có noti click-ads, không kèm kill-app. Quay lại app từ Recents thì noti click-ads vẫn còn (`onResume` chỉ huỷ kill-app và lock screen); mở app bằng chính noti thì noti mất (A049, Luật 20).
  - Kiểm dark/light.

## MO-71 — Noti daily

- **Yêu cầu:** noti nhắc mỗi ngày lúc **8:00** và **19:00**, nội dung xoay vòng. Figma `605-3603` (ref `assets/refs/MO-71-1.jpg`).
- **Nghiệm thu:**
  - Bắn quanh 8:00 và 19:00. Lệch vài phút là bình thường (QC note).
  - Đúng content; tap → Splash → app.
  - Kiểm dark/light.
  - Ngày nào cũng bắn, kể cả sau reboot.
- **SDK:** partial. `BaseNotificationManager.showDaily()` + `NotificationScheduler`, `NotiContentFactory.dailyTimes()` mặc định 8:00/19:00.
- **Chuẩn A013:**
  - **`NotificationManager.scheduleReminder()`** — tên dễ nhầm, đây là **DAILY**, không phải MO-72:
    - giờ hiện tại 8–18 → hẹn 19:00 hôm nay;
    - 19–23 → hẹn 8:00 ngày mai;
    - 0–7 → hẹn 8:00 hôm nay.
    - Alarm là broadcast tới `NotificationReceiver` **không action**, request code `CODE_REQUEST_DAILY`, `setAndAllowWhileIdle(RTC_WAKEUP)`.
  - **Nhánh không-action của `NotificationReceiver`:** chọn ngẫu nhiên trong enum `domain/models/clas/DailyNotificationType.kt` (title/description dạng `@StringRes`) → `setNotification(DAILY_NOTIFICATION, OPEN_FROM_DAILY_NOTIFICATION, …)` → `scheduleReminder()` hẹn lần kế.
  - **`setNotification`:** builder chuẩn (title/text, largeIcon), channel `CHANNEL_DAILY`, PRIORITY_HIGH.
  - **Được hẹn ở:** Splash (`passedNotificationSplash`) và `BootReceiver`.
  - **Lệch Luật trong A013:**
    - small icon `ic_app` (Luật 1);
    - `setAutoCancel(false)`: tap mở app nhưng noti vẫn nằm lại;
    - request code content intent trùng kill-app (Luật 10);
    - nhánh receiver không `goAsync` (Luật 5);
    - text không bọc locale (Luật 13);
    - hẹn lại lúc mở app có thể đè slot đang chờ (Luật 8).
- **Remote config:** A013 không có; giờ cố định trong code. Kill-switch ở app khác: `enable_noti_daily` (Boolean, true — A045, A047, a044).
- **Placement / tracking:** channel `recovery_channel_daily`, id `DAILY_NOTIFICATION`, extras `OPEN_FROM_DAILY_NOTIFICATION` (không `OPEN_TO` → Home), `app_open_from` = `notification_daily`.
- **Cách làm:**
  1. **Enum content:** title/body (+ ảnh, + `OPEN_TO` nếu muốn dẫn thẳng tới tính năng). Copy lấy ở `assets/noti-content.md` mục MO-71.
  2. **Hàm `scheduleDaily`:** hẹn slot kế (8:00/19:00) bằng `setAndAllowWhileIdle(RTC_WAKEUP)`; request code riêng; nên đặt action riêng thay vì "không action".
  3. **Nhánh trong receiver:** chọn content → post (glyph icon, auto-cancel, context bọc locale) → hẹn lại. Có việc async thì dùng `goAsync()`.
  4. **Hẹn ở 3 chỗ:** Splash sau bước quyền, `BootReceiver` (+ `TIME_SET`/`TIMEZONE_CHANGED`), và ngay sau mỗi lần bắn. Muốn chống mất slot thì thêm cửa sổ ân hạn kiểu A047 (Luật 8).
  5. Đọc `NotificationManager.scheduleReminder` / `setNotification` và nhánh cuối của `NotificationReceiver.onReceive` ở A013 (bản hiện tại).
  - **Ref A047 khác A013** (A049 giữ nguyên):
    - action riêng `ACTION_SHOW_DAILY`, mỗi giờ một request code (`CODE_DAILY_MORNING`, `CODE_DAILY_EVENING`) kèm extra `EXTRA_ALARM_KEY`;
    - receiver (`goAsync`) gọi `markAlarmFired` → `showDailyNotification` → `scheduleDaily`; `scheduleAt` có cửa sổ ân hạn 2h (Luật 8);
    - RC tắt daily thì `scheduleDaily` huỷ cả 2 alarm, không chỉ bỏ qua lúc bắn;
    - noti dùng custom view, nút CTA ở bản expand, auto-cancel, glyph `ic_noti_small`.
- **Bẫy:**
  - Đừng nhầm `scheduleReminder` (daily) với `showReminderNotification` (MO-72).
  - Alarm trễ tới khoảng 1 giờ khi máy Doze.
  - Force-stop xoá alarm; phải mở app lại thì alarm mới được hẹn lại.
- **QC:**
  - Ép nổ ngay (build debug): `adb shell run-as $P am broadcast --user 0 -n $P/<FQCN NotificationReceiver>` (cách của A047, đã verify trên Android 15). A013 không kèm `-a` (daily là nhánh không action): `$P` = `com.recovery.protect.data`, FQCN = `com.example.a013_recovery.domain.notification.NotificationReceiver`.
  - App có action daily riêng (A047, A049): thêm `-a` = giá trị hằng `NotificationManager.ACTION_SHOW_DAILY`. Hai app này đặt tiền tố action theo namespace, không theo applicationId (ở A047 hai giá trị này khác nhau).
  - Hoặc đổi giờ: mở app 1 lần → `cmd alarm set-time` tới 8:00 + 1h05m, giữ màn sáng (`references/qc.md` §3).
  - `adb shell dumpsys alarm | grep -A4 $P` thấy alarm kế.
  - Kiểm dark/light.
  - Đổi ngôn ngữ app → bắn lại → nội dung theo ngôn ngữ app.

## MO-72 — Shortcut / Reminder noti

- **Yêu cầu:**
  - Noti nhắc kiểu "shortcut": title + body, expand có 2 nút **LATER | ACTION** ngăn bằng divider. Figma `512-1074` (ref `assets/refs/MO-72-1.jpg`).
  - Logic bắn:
    - user mới: tại màn **Language** trong FO, **chỉ 1 lần đầu**;
    - user cũ: sau khi vào **Home**, **mỗi phiên 1 lần**.
  - **Không phải** App Shortcut (long-press icon — đó là MO-74).
- **Nghiệm thu:**
  - FO: vào Language → noti hiện 1 lần; quay lại Language không bắn nữa.
  - Phiên sau: vào Home → bắn 1 lần; về Home lại trong cùng phiên không bắn.
  - LATER → noti mất, không mở app. ACTION/tap → Splash → tính năng.
  - Kiểm content, dark/light.
- **SDK:** partial. `BaseNotificationManager.showReminder()` (LATER = broadcast `TYPE_DISMISS`); trigger FO/phiên phải tự làm.
- **Chuẩn A013:**
  - **`NotificationManager.showReminderNotification()`:**
    - ACTION/tap → `MainActivity` + `OPEN_FROM_REMINDER_NOTIFICATION` + `OPEN_TO_RECOVERY_PHOTO` + `KEY_AUTO_SCAN` (vào thẳng màn scan và tự quét);
    - LATER → broadcast `ACTION_DISMISS_REMINDER` → receiver huỷ `REMINDER_NOTIFICATION_ID`;
    - layout `layout_noti_reminder_collapse.xml` / `layout_noti_reminder_expand.xml`;
    - channel `CHANNEL_REMINDER` (HIGH), auto-cancel.
  - **FO:** `ui/screen/language/LanguageFOScreen.kt`, `LifecycleResumeEffect`: nếu chưa `prefs.hadPostNotificationRemind` → bắn và set `true`.
  - **User cũ:** `ui/screen/home/HomeScreen.kt`, `LifecycleResumeEffect` theo `prefs.lastReminderSession`:
    - lần đầu (giá trị 0) → chỉ ghi lại, bỏ qua (phiên FO đã bắn ở Language);
    - sau đó, nếu `sessionNumber > lastReminderSession` → ghi lại và bắn.
  - `sessionNumber` tăng ở `MainActivity.onCreate` khi là lần mở mới.
  - Lịch sử: commit `4c47200` chuyển reminder từ Splash sang Language + Home.
- **Remote config:** A013 không có. Ở app khác:
  - `enable_noti_shortcut` (Boolean, true — A045, A047, a044);
  - `show_shortcut_noti` (Boolean, true — a033, đọc thẳng prefs).
  - State (không phải RC) cho FO và phiên: `hadPostNotificationRemind` (A013); `shown_shortcut_noti_fo` (A014, A045, A047, a033, a044); `show_shortcut_noti_fo` / `show_shortcut_noti_in_fo` (a016, a036, a037 — nghĩa **ngược**: `true` = còn phải bắn); `last_reminder_session` (A013); `last_shortcut_noti_session` (A014, A045, A047, a033, a044).
- **Placement / tracking:**
  - Channel `recovery_channel_reminder`, id `REMINDER_NOTIFICATION_ID`, request code riêng cho nút mở và nút LATER.
  - `app_open_from` = `notification_reminder` (biến thể `notification_shortcut`).
  - A049 log `shortcut` theo danh sách PO, trùng giá trị với lượt mở từ launcher shortcut (`ShortcutsUtil`). Phân biệt bằng event `notification_clicked` (`type` = `shortcut`).
- **Cách làm:**
  1. **Layout:** collapse (title + body) và expand (title, body, divider bằng `ImageView` 1dp, hàng LATER | ACTION). Màu `noti_*`. Copy lấy ở `assets/noti-content.md` mục MO-72 (mới).
  2. **Hàm show:**
     - nút ACTION là `PendingIntent` tới `MainActivity` + `OPEN_TO`;
     - nút LATER là broadcast tới receiver của app với action dismiss;
     - thêm nhánh dismiss vào receiver.
  3. **FO:** ở `LifecycleResumeEffect` của màn Language FO (XML: `onResume` của Fragment/Activity) → bắn 1 lần, ghi cờ FO và cả session hiện tại, để Home trong cùng phiên FO không bắn thêm (A047 làm vậy).
  4. **User cũ:** ở resume của Home → so `sessionNumber` với session đã bắn.
  5. Đọc `LanguageFOScreen` (khối `hadPostNotificationRemind`), `HomeScreen` (khối `lastReminderSession`) và `NotificationManager.showReminderNotification` ở A013 (bản hiện tại).
  - **Ref A047 khác A013:**
    - `NotificationManager.showShortcutNotiOnLanguage` (gọi ở resume màn Language FO) ghi `shown_shortcut_noti_fo` và `last_shortcut_noti_session`;
    - `showShortcutNotiOnHome` so `last_shortcut_noti_session` với `sessionNumber`; Home bỏ qua khi `passingThrough`;
    - LATER = broadcast `ACTION_DISMISS_SHORTCUT` tới receiver.
  - **App đã làm — A049** (port A047, 10/2026): như A047, thêm kiểm kill-switch + quyền (`canShowShortcut`) **trước** khi ghi cờ, ở cả Language lẫn Home. Language chỉ bắn khi không mở từ Settings (`LanguageViewModel.onResume` kiểm `fromSetting`).
- **Bẫy:**
  - A013 set `hadPostNotificationRemind = true` kể cả khi chưa có quyền noti. Nếu RC `noti_permission_trigger` = `home` (chưa xin quyền trước Language) thì lượt FO bị mất. Chỉ ghi cờ khi `allowNotification`. A047 cũng ghi cờ trước khi kiểm quyền; A049 đã sửa.
  - Chỉ ghi cờ FO khi có quyền, mà app dùng chung một màn Language cho FO và Settings (A049; A013, A047 có màn Settings riêng), thì phải chặn lượt vào Language từ Settings. Nếu không, user cấp quyền muộn sẽ nhận noti "FO" lúc đổi ngôn ngữ ở Settings.
  - `sessionNumber` chỉ được tăng khi `savedInstanceState == null` (A013, A047, A049). Tăng cả khi Activity dựng lại (đổi dark mode, ngôn ngữ) thì shortcut bắn lại trong cùng phiên.
  - Mở app từ noti thẳng vào tính năng thì Home chỉ là trạm trung chuyển. A013 vẫn bắn ở resume Home; A047 chặn bằng `passingThrough`.
  - a016/a036 thêm điều kiện `!adsManager.isShowingAds` khi bắn ở Language.
  - Đừng nhầm với `scheduleReminder` (đó là daily).
- **QC:**
  - Xoá data → FO tới Language → có noti. Back/vào lại → không bắn lại.
  - Expand → LATER → noti mất. Bắn lại, bấm ACTION → Splash → màn đích; `app_open_from` = `notification_reminder`.
  - Kill app → mở lại → vào Home → có noti. Vào tính năng rồi về Home → không bắn lại.
  - App có `passingThrough` (A047, A049): mở từ noti thẳng vào tính năng thì lúc đi qua Home không có noti shortcut; back về Home mới bắn nếu phiên chưa bắn.
  - Kiểm dark/light.

## MO-73 — Win-back noti

- **Yêu cầu:** noti win-back bắn lúc **11:00** và **14:00** mỗi ngày. Figma `512-1263` (ref `assets/refs/MO-73-1.jpg`): title + body, collapse có thumbnail, expand có ảnh lớn + nút CTA.
- **Nghiệm thu:**
  - Bắn quanh 11h và 14h.
  - Đúng content; tap/CTA → Splash → tính năng.
  - Kiểm dark/light.
  - Lặp mỗi ngày, kể cả sau reboot.
- **SDK:** partial. `BaseNotificationManager.showWinback()` + `NotiContentFactory.winbackTimes()` mặc định 11:00/14:00.
- **Chuẩn A013:**
  - **`NotificationManager.scheduleWinBack()`** gọi `scheduleWinBackAt` 2 lần (11h với `CODE_REQUEST_WINBACK_11H`, 14h với `CODE_REQUEST_WINBACK_14H`):
    - broadcast `ACTION_SHOW_WINBACK`;
    - lấy mốc kế (đã qua thì sang mai);
    - `setAndAllowWhileIdle(RTC_WAKEUP)`;
    - chạy đồng bộ.
  - **Receiver:** nhánh `ACTION_SHOW_WINBACK` gọi `showWinBackNotification()` rồi `scheduleWinBack()`.
  - **`showWinBackNotification()`:**
    - tap/CTA → `MainActivity` + `OPEN_FROM_WINBACK_NOTIFICATION` + `OPEN_TO_RECOVERY_PHOTO` + `KEY_AUTO_SCAN`;
    - layout `layout_noti_winback_collapse.xml` (title, body, thumb) / `layout_noti_winback_expand.xml` (title, body, `ivBig`, `btnAction` có vệt sáng);
    - channel `CHANNEL_UPDATES` (HIGH), auto-cancel, id `WINBACK_NOTIFICATION_ID`.
  - **Được hẹn ở:** Splash (`passedNotificationSplash`) và `BootReceiver`.
  - **Không có điều kiện "lâu không mở app":** user dùng app hằng ngày vẫn nhận.
- **Remote config:** A013 không có. Ở app khác:
  - `enable_noti_winback` (Boolean, true — A045, A047, a044);
  - `is_show_noti` (String, `"winback_progress_shortcut"` — a27; giá trị chứa `winback` mới bắn).
  - Langofy hẹn 14h/17h (lệch chuẩn).
- **Placement / tracking:** channel `recovery_channel_updates`, id `WINBACK_NOTIFICATION_ID`, `app_open_from` = `notification_winback` (biến thể `notification_win_back`).
- **Cách làm:**
  1. **Layout:**
     - collapse: title, body, thumb 40dp;
     - expand: title, body, ảnh lớn trong khung `layout_weight`, nút CTA có vệt sáng.
     - Màu `noti_*`. Copy lấy ở `assets/noti-content.md` mục MO-73.
  2. **Hàm `scheduleWinBack`:** 2 slot, mỗi slot một request code; action riêng.
  3. **Receiver:** nhánh show + hẹn lại, chạy đồng bộ.
  4. **Hẹn ở:** Splash, Boot, và sau mỗi lần bắn.
  5. Đọc `NotificationManager.scheduleWinBack` / `scheduleWinBackAt` / `showWinBackNotification` và nhánh `ACTION_SHOW_WINBACK` của `NotificationReceiver` ở A013 (bản hiện tại).
  - **Ref A047 khác A013** (A049 giữ nguyên): hạ tầng như MO-71 (mỗi giờ một request code, `markAlarmFired` trước khi bắn, ân hạn 2h, RC tắt thì huỷ alarm). Dùng chung layout promo với kill-app/click-ads (`layout_noti_promo_*`); win-back gọi `showPromo` với `actionInCollapsed = false` nên collapse hiện thumbnail thay nút CTA.
- **Bẫy:**
  - Luật 8 đặc biệt hay gặp: mở app lúc 11:10 khi alarm 11:00 chưa nổ → bị đẩy sang mai.
  - `showWinBackNotification` của A013 gọi `setImageViewResource(R.id.ivBig, …)` lên layout collapse, mà layout này không có id đó. Lệnh này vô hại (bị bỏ qua), nhưng đừng chép.
  - Win-back và daily dùng chung một receiver → phải tách action (Luật 6).
- **QC:**
  - Ép nổ (debug): `adb shell run-as $P am broadcast --user 0 -n $P/<FQCN receiver> -a <action win-back>` (A013: `com.example.a013_recovery.action.SHOW_WINBACK`; A047, A049: hằng `NotificationManager.ACTION_SHOW_WINBACK`, tiền tố theo namespace).
  - Hoặc đổi giờ tới 11:00 + 1h05m và 14:00 + 1h05m.
  - Collapse có thumb; expand có ảnh + nút. CTA → Splash → tính năng; `app_open_from` = `notification_winback`.
  - Kiểm dark/light. Ngày kế vẫn bắn.

## MO-75 — Firebase Cloud Messaging (FCM)

- **Yêu cầu:**
  - App nhận được push từ **tool bắn noti nội bộ** (do anh Trường setup).
  - Ghi chú sheet: "a013, a027, a037: code đã có nhưng bên Ai chưa apply" — nghĩa là phía tool chưa bật cho app.
- **Nghiệm thu:**
  - Có service FCM khai trong manifest.
  - Token được log (event `fcm_token`) và gửi AppsFlyer (uninstall tracking).
  - Push từ console/tool hiện khi app ở nền, với icon glyph đúng.
- **SDK:** partial, coi như không có.
  - `com.example.xtechads.ads.firebase.messages.FirebaseFCM` là **stub rỗng** (cả `onNewToken` lẫn `onMessageReceived` chỉ gọi `super`) và **không** tự khai trong manifest SDK.
  - `xtechads/docs/TRACKING_EVENTS_STATUS.md` bảo khai class này và nói nó log `fcm_token`, nhưng code không làm vậy.
  - a039 đang khai stub này nên **không có** `fcm_token` và không có token AppsFlyer.
- **Chuẩn A013:**
  - **`ads/firebase/FirebaseFCM.kt`** (`FirebaseMessagingService`):
    - `onNewToken`: `AppsFlyerLib.updateServerUninstallToken` + event `fcm_token`, param `fcm_token_length` + `fcm_token_1..n` (token cắt khúc 90 ký tự vì giá trị param Analytics tối đa 100 ký tự).
    - `onMessageReceived`: chỉ gọi `super`.
  - **`App.initFCM()`:** sau `consentFinished` lấy `FirebaseMessaging.getInstance().token`, chỉ để cập nhật AppsFlyer (không log event).
  - **Manifest:** service `.ads.firebase.FirebaseFCM` (filter `com.google.firebase.MESSAGING_EVENT`), meta-data `default_notification_icon` + `default_notification_color`.
- **Remote config:** không có.
- **Hiện trạng các app:**
  - a033 (PDF) **không có FCM** (không service, không dependency messaging).
  - a039 khai stub SDK nên không có `fcm_token`/AppsFlyer. Class riêng của app có nhưng không được khai trong manifest.
  - A028, a036 log `fcm_token` nhưng không gửi token cho AppsFlyer.
  - a27 log `fcm_token` ở mỗi process, a034 ở mỗi `onCreate`: event bị phình.
  - Các app còn lại giống A013.
  - Không app nào xử lý `onMessageReceived`.
- **Placement / tracking:** event `fcm_token`. Theo cookbook tracking của A045 (`.claude/skills/build-tracking/references/wiring-cookbook.md`), event này log ở `onNewToken` **và** lúc lấy token lần đầu. Đừng log mỗi lần mở app: a27 và a034 đang làm vậy (a037 từng làm, theo changelog) và làm phình volume event.
- **Tool nội bộ cần gì (suy luận):**
  - Không repo nào mô tả tool. Không app nào và cả SDK đều **không** `subscribeToTopic`.
  - Vậy tool chỉ có thể nhắm theo token (ghép lại từ `fcm_token_1..n`, đối chiếu với `fcm_token_length`) hoặc bắn hàng loạt qua Firebase console/API.
  - Muốn dùng topic hoặc deep link (`open_to`) thì phải chốt với anh Trường trước khi code.
- **Cách làm:**
  1. **Service FCM riêng của app.** Không dùng stub SDK.
     - `onNewToken`: AppsFlyer uninstall token + event `fcm_token` (chunk 90 ký tự).
     - `onMessageReceived`: để `super`, trừ khi tool cần data message.
  2. **Lấy token lần đầu** sau consent (A013 `App.initFCM`). Nếu theo cookbook thì log `fcm_token` một lần (có cờ trong prefs).
  3. **Manifest:**
     - `<service>` với filter `MESSAGING_EVENT`, `exported="false"` (Google docs; a037 làm vậy; A013 đang để `true`);
     - meta-data icon (**glyph**, Luật 1) và color;
     - nên thêm `default_notification_channel_id` và tạo channel đó lúc khởi động. qibla khai id nhưng không tạo channel; các app khác không khai → push rơi vào channel "Miscellaneous".
  4. Đọc `ads/firebase/FirebaseFCM.kt` và `App.initFCM` ở A013 (bản hiện tại).
  5. Báo anh Trường: package + có `fcm_token` để bên tool bật app.
- **Bẫy:**
  - Không xử lý `onMessageReceived` → push đến lúc app đang mở và data-only push đều bị **mất** (không app nào xử lý).
  - Tap push mặc định mở launcher Activity: vẫn qua Splash, nhưng không có `OPEN_FROM`, nên `app_open_from` không ghi nhận.
  - Push high-priority đến dưới dạng broadcast foreground khoảng 10 giây; campaign lớn có thể dồn ANR. Phân tích ANR của a034 khuyên dùng priority normal + ảnh nhỏ → báo phía tool.
- **QC:**
  - Firebase Console → Messaging → "Send test message" với token (lấy trong DebugView event `fcm_token`, ghép các khúc lại).
  - App ở nền → noti hiện, icon glyph, đúng màu. App ở foreground → hiện tại không hiện (đúng hiện trạng).
  - Event `fcm_token` xuất hiện ở lần cài đầu (DebugView: `adb shell setprop debug.firebase.analytics.app $P`).

## MO-87 — Noti Warning system (KHÔNG làm)

- **Yêu cầu (sheet):** "Fake system app warning about notification — caution noti". Ref `assets/refs/MO-87-1.jpg`: noti đội lốt cảnh báo hệ thống ("⚠ Foreign Object Detection… tap to remove it").
- **Kết luận: không triển khai** (catalog: `blocked-policy`).
  - Noti/UI giả cảnh báo của hệ điều hành hoặc đội lốt app hệ thống vi phạm chính sách Google Play về Deceptive Behavior và Impersonation (đánh lừa user, giả mạo hệ thống/Android).
  - Hậu quả có thể là gỡ app hoặc khoá tài khoản developer.
- **Việc cần làm:** báo PO/MO, không code, không recipe.
  - Nếu MO cần kéo user quay lại thì dùng noti đúng thương hiệu app, nói về tính năng thật: MO-71/72/73.
  - Không dùng icon ⚠, không dùng tên kiểu "System"/"Android", không giả giao diện cảnh báo của OS.

## MO-88 — Bỏ noti khi user tự mở Settings bật mạng

- **Yêu cầu:**
  - Luồng: mất mạng → popup → bấm "Enable" → app mở Settings mạng → app xuống nền.
  - Lúc này noti (kill-app) đang **bật nhầm** → phải bỏ.
- **Nghiệm thu:** popup no-internet → Enable → Settings → **không** có noti nào. Quay về app bình thường, kill-app vẫn hoạt động ở các lần thoát app khác.
- **SDK:** không áp dụng.
- **Chuẩn A013** (commit `22f5527`, P1865):
  - **`utils/AppUtils.kt` — `Context.openInternetSettings()`:**
    - set `AppScreenState.openSetting = true` **trước** khi mở Settings qua `PermissionSettingsGuide.open(...)`;
    - danh sách intent theo thứ tự: `Settings.Panel.ACTION_INTERNET_CONNECTIVITY` → `ACTION_WIFI_SETTINGS` → `ACTION_WIRELESS_SETTINGS` → `ACTION_SETTINGS`;
    - `isGranted` = `adsManager.isConnected` (có mạng thì tự quay về app, MO-90);
    - mở thất bại → trả cờ về `false` + toast.
  - **`MainActivity.onPause`:** khi cờ bật, bỏ cả kill-app lẫn tracking "user ra nền". **`MainActivity.onResume`:** reset cờ.
  - Cờ khai ở `common/TrackingScreen.kt` (`object AppScreenState`). Nơi gọi: popup no-internet trong `AppNavigation.kt` (`onGoSetting`).
- **Remote config:** không có.
- **Placement / tracking:** không có.
- **Cách làm:**
  1. Tạo cờ "app tự rời sang Settings/app khác" và set ngay trước `startActivity` sang Settings.
     - Ưu tiên cờ riêng, reset ở `onResume`, như `AppScreenState.openSetting` của A013.
     - Dùng `adsManager.disableAdResumeOneTime` như A014 cũng được nhưng có rủi ro (xem Bẫy).
  2. Mọi trigger noti khi xuống nền (kill-app MO-69, click-ads nếu bắn lúc nền) phải kiểm `!cờ`.
  3. Reset cờ ở `onResume`.
  4. Áp cho **mọi** chỗ app chủ động mở Settings trong FO (mạng, quyền noti, quyền file…), không chỉ Wi-Fi.
  5. Đọc `openInternetSettings` (`utils/AppUtils.kt`) và `MainActivity.onPause/onResume` ở A013 (bản hiện tại).
  - **App đã làm — A049** (10/2026):
    - cờ riêng `common/ExternalScreen.kt` (`ExternalScreen.opening`), set trong helper chung `startExternal` (`common/Commons.kt`; mọi lệnh mở URL, Store, share, App info) và trong `PermissionSettingsGuide.open`; reset ở `MainActivity.onResume`;
    - trigger kill-app ở `onStop` kiểm cả cờ này lẫn `disableAdResumeOneTime`;
    - popup mất mạng gọi `MainActivity.openInternetSettings`: set cờ SDK (`disableAdResumeOnTime`) rồi mở trang Wi-Fi toàn màn hình qua `PermissionSettingsGuide.open` (set luôn cờ riêng, có mạng thì tự kéo app về). Tới 15/10/2026 popup gọi `openWifiSetting` của SDK (`references/splash.md` MO-26).
- **Hiện trạng các app** (cờ dùng: `AppScreenState.openSetting` hoặc `adsManager.disableAdResumeOneTime`; SDK tự xoá cờ sau khi app quay lại từ nền):
  - Đã có: A013, A014 (commit `c5c2db1` "Checklist MO 88 + 90"), a033, a036, a037, a039, a044, A047, a27, A049 (cờ riêng `ExternalScreen.opening` + cờ SDK).
  - a031 không áp dụng (kill-app bắn ở `onDestroy`).
  - **Chưa có:** a016 (`NetworkUtils.openNetworkSettings`), A028 (`openWifiSetting`), a041 (`openNetworkSettings`).
  - **Thiếu một phần:**
    - A045: `onStop` không kiểm cờ.
    - a034, Langofy: không set cờ cho intent panel (suy luận từ code, chưa test máy).
  - a27 dùng thêm cờ một-lần `disableKillAppNotificationOneTime`. Có thể cờ này không được tiêu ở lượt mở Settings, rồi nuốt mất lượt kill-app thật kế tiếp.
- **Bẫy:**
  - **Panel Internet** (`Settings.Panel.ACTION_INTERNET_CONNECTIVITY`, Android 10+) là Activity trong suốt nổi trên app.
    - App chỉ chạy `onPause` (không `onStop`).
    - Code chỉ set cờ cho intent không-phải-panel thì kill-app ở `onPause` vẫn bắn.
    - **Set cờ cho mọi intent**, gồm cả panel, như A013 và A047.
  - **Dùng `disableAdResumeOneTime` làm cờ có rủi ro.**
    - SDK chỉ xoá cờ này trong `BaseAds.onActivityResumed` khi app quay lại từ nền **thật** (`cameFromBackground`, set ở `onStop` của process).
    - Panel nổi không đưa app xuống nền, nên cờ còn treo và nuốt lượt kill-app/app-resume kế tiếp (suy luận từ code SDK).
    - Cờ riêng reset ở `MainActivity.onResume` (A013) an toàn hơn.
  - A013 chỉ set cờ trong `openInternetSettings`. Các chỗ mở Settings khác trong FO (nếu app có) phải tự set.
  - Lỡ quên reset cờ thì kill-app tắt luôn tới lần resume sau.
  - **Helper mở màn ngoài của SDK** (`openWifiSetting`, `openWebsite`, `shareApp`; kiểm 1.8.7) chỉ gọi `BaseAds.disableAdResumeOnTime` (set `disableAdResumeOneTime`), không biết cờ riêng của app. App có cờ riêng mà vẫn gọi helper SDK thì trigger kill-app phải kiểm cả hai cờ (trigger của A049 kiểm cả hai).
  - Trigger kill-app ở `onStop` (A045, A048, A049) thì panel/sheet nổi (chỉ làm `onPause`) tự không bắn. Cờ vẫn cần cho Settings, Store, trình duyệt mở toàn màn hình.
- **QC:**
  - Cài mới, tắt mạng (`svc wifi disable; svc data disable`) → Splash hiện popup → Enable → Settings → không có noti. Test cả máy Android 10+ (mở panel nổi) lẫn máy mở trang Settings toàn màn hình.
  - Bật mạng → app tự quay về.
  - Bấm Home ở màn FO → kill-app vẫn hiện.

## MO-89 — Bỏ noti kill-app kiểu cũ (foreground service)

- **Yêu cầu:**
  - Bỏ noti "kill app" **kiểu cũ** hiện ở màn Language. Ref `assets/refs/MO-89-1.jpg`: noti "*Tap for more information or to stop the app*".
  - Bấm vào nó mở trang App info, nơi user có thể buộc dừng hoặc gỡ app ("click vô để review app hoặc xoá app").
  - Kiểm mọi app.
- **Nguồn gốc:**
  - Bản cũ bắt "kill app" bằng `KillAppService`: một `Service` có `onTaskRemoved`, gọi `startForeground` với noti **thiếu small icon**, khai `foregroundServiceType="shortService"`.
  - Service được `bindService` từ Splash khi đang FO và unbind ở Home/Uninstall.
  - Noti foreground thiếu small icon là noti không hợp lệ, nên hệ thống thay bằng noti chung "App đang chạy — nhấn để biết thêm thông tin hoặc dừng ứng dụng". Noti này hiện suốt các màn FO, trong đó có Language.
- **Nghiệm thu:**
  - Suốt FO không còn noti "đang chạy" của hệ thống.
  - Không còn foreground service.
  - Kill-app kiểu mới (MO-69) vẫn chạy.
- **SDK:** không áp dụng.
- **Chuẩn A013:** commit `7f116b2` "remove old kill app notification":
  - xoá `domain/KillAppService.kt`;
  - xoá `<service … foregroundServiceType="shortService">` trong manifest;
  - xoá `bindService`/`unbindService` trong `MainActivity`, Splash, Home, Uninstall;
  - thêm huỷ noti kill-app ở `MainActivity.onResume`.
  - Code hiện tại không còn dấu vết.
- **Remote config:** không có.
- **Placement / tracking:** không có.
- **Cách làm:**
  1. Grep `KillAppService|onTaskRemoved|startForeground\(|foregroundServiceType|bindService\(`.
  2. Xoá service, khai báo manifest, quyền `FOREGROUND_SERVICE*` (nếu chỉ dùng cho nó), và các lời gọi bind/unbind.
  3. Đảm bảo MO-69 kiểu mới (`onPause`/`onStop`) đã có trước khi xoá.
  4. Build lại, kiểm merged manifest không còn service.
- **Hiện trạng các app:**
  - **Còn ở a031 (qibla)**, thêm trong commit `06ef4657`:
    - `services/KillAppService.kt`;
    - `MainActivity.bindService`, gọi từ `SplashFragment`;
    - unbind ở `HomeFragment`/`UninstallFragment`;
    - manifest `foregroundServiceType="shortService"`.
  - **Đã gỡ:** A013 (`7f116b2`), A014 (`ec0affd`), a016 (`31f98dc`), a27 (`51c18d1`).
  - Các app còn lại chưa từng có (`git log --all -S'KillAppService'` rỗng).
- **Bẫy:**
  - Không xoá nhầm foreground service có chức năng thật: `CastSessionService` (a028), `BoostService` (a037), `HandleNewFileService` (a033).
  - Có app từng "sửa" bằng cách thêm small icon cho noti foreground (a016 commit `1b0fc21`). Làm vậy chỉ đổi noti hệ thống thành noti của app, service vẫn còn. Yêu cầu là **xoá hẳn**.
- **QC:**
  - Cài mới → đi FO (Splash → Language → Onboarding): shade không có noti "đang chạy / Tap for more information".
  - `adb shell dumpsys activity services $P` không còn `KillAppService`.

## MO-95 — Noti lock screen

- **Yêu cầu:**
  - Vào các slot giờ trong ngày (theo RC), khi màn hình tắt hoặc khoá → bật màn hình và hiện overlay (`LockScreenActivity`) đè lên màn khoá.
  - Overlay gồm card nội dung + nút CTA + nút X.
  - CTA → Splash → tính năng. Doc MO: Lark wiki (catalog `docs`).
- **Nghiệm thu:**
  - Đúng slot; màn tắt/khoá → overlay hiện.
  - CTA → mở khoá → Splash → đúng tính năng; X → đóng + huỷ noti.
  - Rời overlay mà không bấm gì → lần bật màn kế (còn khoá) hiện lại (rewake).
  - Không có quyền FSI → vẫn có noti heads-up thường, tap mở app, log biến thể un_support (tên event/giá trị
    theo app đang có; chuẩn A013 `notification_lock_screen_un_support`).
  - Mở app → noti lock screen bị huỷ.
  - Nội dung theo ngôn ngữ app; kiểm dark/light.
- **Tối thiểu để Done** (đủ = đạt nghiệm thu; phần còn lại là nâng cao):
  1. Hẹn alarm theo slot RC (bật/tắt bằng RC, slot user mới/cũ) + hẹn lại ở Splash/Boot/receiver.
  2. Tới slot: màn tắt/khoá + có quyền FSI → overlay `LockScreenActivity`; không có quyền FSI → heads-up thường.
  3. CTA → Splash (MO-78) → đúng tính năng; X huỷ noti; back chỉ đóng overlay (rewake ở lần bật màn sau).
  4. Tracking: `app_open_from` lock screen + biến thể un_support (tên theo app đang có).
  5. Mở app → huỷ noti lock screen.
  6. Chống chồng noti: tới slot mà noti cũ còn trong shade thì bỏ lượt (RC `replace` = true thì huỷ cũ, bắn mới). Default theo app ref.
  Nâng cao (hỏi user): popup xin FSI ở Home (bước 6), tip đè trang Settings, wake lock/`hide_second`.
- **Chính sách FSI (bắt buộc đọc):**
  - Từ Android 14 (API 34), `USE_FULL_SCREEN_INTENT` chỉ được cấp mặc định cho app có chức năng chính là **gọi điện hoặc báo thức**.
  - App khác (tất cả app của mình) phải khai báo trong Play Console (App content → Full-screen intent). Quyền mặc định có thể bị thu hồi; user phải tự bật ở Settings (`Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT`).
  - Vì vậy trên bản cài từ Store, **nhánh không có FSI là nhánh chính**:
    - luôn kiểm `NotificationManager.canUseFullScreenIntent()` (API < 34 coi như `true`);
    - `false` → **không** gắn `setFullScreenIntent`, post noti HIGH thường (heads-up), log un_support.
  - Bản cài qua adb/debug vẫn có quyền (theo doc A047) → QC phải test bằng `appops … deny`.
  - Theo doc A014 (`docs/lockscreen-fsi-device-guide.md`), bắn thử nhiều lần liên tục có thể khiến máy tự tắt quyền "thông báo toàn màn hình". Kiểm lại quyền trước khi báo bug.
  - Không spam hay tự bật lại FSI (Luật 16).
- **SDK:** không có.
- **Chuẩn A013** (họ A014: `object LockScreenNotiManager` + `LockScreenActivity`; A013 port từ a014 và giữ cấu trúc giống hệt):
  - **Model:** `domain/models/clas/LockScreenNotiType.kt`, enum gồm title/desc/nút/ảnh/`openTo` (+ `trackName` chỉ dùng cho log; `buttonName` hiện không dùng). Chọn loại bằng `randomExcept(last)` (không lặp loại vừa bắn; lưu `last_lockscreen_noti_ordinal`). Mỗi loại **phải có `OPEN_TO` riêng** khác default, vì có app (a036) chỉ quay về Splash khi `openTo ≠ DEFAULT` (MO-78).
  - **Bỏ qua app-open ad trên overlay:** A013 thêm các màn `ScrNotificationLockScreen{n}` vào danh sách `screenSkipAdResume` của `ads/AdsManager.kt` (ticket P2540, P3029). Thiếu bước này thì app-open resume có thể đè lên overlay hoặc lên Splash khi mở từ CTA.
  - **`domain/notification/LockScreenNotiManager.kt`:**
    - `createChannel`: `CHANNEL_LOCKSCREEN`, HIGH.
    - `scheduleLockScreenNotifications`:
      - gate `noti_lockscreen_enable` + quyền noti;
      - mỗi slot một alarm `setAndAllowWhileIdle(RTC_WAKEUP)`, request code `CODE_REQUEST_LOCKSCREEN` + chỉ số, action `NotificationReceiver.ACTION_LOCKSCREEN`;
      - slot lấy từ `noti_lockscreen_slots`, hoặc `noti_lockscreen_slots_new` nếu là user mới (< 24h kể từ pref
        `first_install_time` — A013 tự ghi ở lần mở app đầu tiên trong `MainActivity`, **không** phải
        `PackageInfo.firstInstallTime`);
      - `parseSlotTime` nhận cả `H:mm` lẫn `h:mm a`.
    - `fireLockScreenNotificationNow`:
      - noti cũ còn trong shade hoặc Activity đang mở → bỏ lượt, trừ khi `noti_lockscreen_replace` (khi đó huỷ noti cũ rồi bắn);
      - Activity đang mở → chỉ đổi nội dung (`LockScreenActivity.updateShownContent`) + post noti im lặng, không FSI;
      - ngược lại → `finishStale`, `wakeScreenBriefly` (wake lock, thời lượng = `noti_lockscreen_hide_second`, kẹp 1–60s), rồi `showLockScreenNotification`.
    - `showLockScreenNotification`:
      - content dựng bằng `localizedContext`;
      - builder chuẩn (title/text/largeIcon), PRIORITY_HIGH, `CATEGORY_ALARM`, auto-cancel;
      - `setFullScreenIntent(→ LockScreenActivity với EXTRA_TYPE, true)` **chỉ khi** màn tắt/khoá **và** `canUseFullScreenIntent()`;
      - content intent → `MainActivity` + `OPEN_FROM_NOTIFICATION_LOCKSCREEN` + `OPEN_TO` của loại;
      - không có FSI → event `notification_lockscreen_un_support`.
    - **Rewake:** `registerScreenWatcher` đăng receiver runtime `SCREEN_ON/OFF` trên applicationContext (`RECEIVER_NOT_EXPORTED`).
      - `onScreenOn`: máy còn khoá + noti còn trong shade + Activity không mở + quá 5 giây kể từ lần post → `rewakeLockScreenNotification` (huỷ rồi post lại đúng loại, kèm FSI).
      - `onScreenOff`: nếu `pendingRewake` (set khi user rời overlay lúc màn còn sáng) → rewake.
  - **`ui/screen/lockscreen/LockScreenActivity.kt` + `view/LockScreenContent.kt`:**
    - `ComponentActivity` + Compose; `attachBaseContext` bọc locale; `setShowWhenLocked(true)`, `setTurnScreenOn(true)`.
    - Back/vuốt = chỉ `finish` overlay, **không huỷ noti**: noti còn trong shade nên lần bật màn sau (máy còn
      khoá) overlay hiện lại (rewake). Chỉ nút X mới huỷ noti. Tracking màn `ScrNotificationLockScreen{n}`, nút
      `BtnClick` / `BtnNotiClose`.
    - CTA (`openFeature`): `AppUtils.needSkipResume()` (không ăn app-open ad), huỷ noti, mở `MainActivity` với extras, set `prefs.openTo` + `prefs.openFromPending`, `requestDismissKeyguard`, finish.
    - X (`onCloseNoti`): huỷ noti + finish.
    - `onUserLeaveHint` → finish. `onStop` → set `pendingRewake` nếu noti còn.
  - **Manifest** (`app/src/main/AndroidManifest.xml`):
    - activity: `excludeFromRecents`, `exported=false`, `launchMode=singleTask`, `taskAffinity=""`, `showWhenLocked`, `turnScreenOn`, theme `Theme.A013.LockScreenNoti` (`res/values/themes.xml`: nền trong suốt + `windowShowWallpaper`);
    - quyền `USE_FULL_SCREEN_INTENT`, `WAKE_LOCK`, `RECEIVE_BOOT_COMPLETED`.
  - **Wiring:**
    - `App.initLockScreenNoti`: lifecycle callback "Activity khác resume → huỷ noti + finish overlay cũ"; trên IO: `createChannel` + schedule + watcher.
    - Splash (`passedNotificationSplash`), `BootReceiver`, nhánh `ACTION_LOCKSCREEN` của `NotificationReceiver` (dùng `goAsync`).
  - **Xin quyền FSI:** `ui/screen/home/view/HomePermissionPrompts.kt`. Overlay `OvlFSPermission` → Settings qua `common/PermissionUtils.kt` `fullScreenIntentSettingsIntents` (trang FSI riêng của app, fallback trang noti). Gate:
    - API 34+;
    - đã có quyền noti;
    - RC `full_scr_intent`;
    - đúng nhịp `full_scr_intent_retrigger`.
- **Họ khác — A044/A045** (a044, A045, A047, A049, a033):
  - Logic nằm trong `NotificationManager` + class `LockScreenNotiWatcher` (a044, A047, A049, a033). **A045 đã xoá watcher** (commit `6bb2f45`), nên A045 **không có rewake**, thiếu 1 dòng nghiệm thu. KDoc và `docs/features/mo-checklist-v103.md` của A045 vẫn nhắc watcher/`timeDelayNotiHide`: doc cũ, theo code.
  - A013 dùng chung vài tên với họ này (action `…action.SHOW_LOCKSCREEN`, extra `lockscreen_noti_type`, id noti). Vì vậy nhận diện họ bằng **cấu trúc class**, không bằng tên action.
  - Chỉ post khi màn tắt/khoá, không thì bỏ slot (A045, A047, A049). Kill-switch rewake `enable_noti_lockscreen_rewake` có ở A047/a044, A049 là field `lockscreen.rewake` trong `noti_config` (A045 không có vì không có rewake).
  - A045 `parseTime` chỉ nhận `H:mm` (`"8:00 PM"` → 8:00, sai). A013 nhận cả `h:mm a`.
  - Mở noti: A045 `disableAdResumeOnTime` khi bấm CTA; huỷ noti ở `MainActivity.onResume`.
  - A045/A047 thêm cửa sổ ân hạn 2 giờ + mốc `noti_fired_day_<req>`, và không dùng wake lock.
  - A047, A049 chỉ đăng ký `LockScreenNotiWatcher` ở nhánh lock screen của receiver; A013 đăng ký thêm ở `App`, Splash, Boot và `LockScreenActivity`. Process chết sau khi post thì mất rewake tới slot sau.
  - **A047 thiếu so với nghiệm thu hoặc dính lỗi đã biết trong Bẫy; A049 (port A047, 10/2026) đã bổ sung** (ref A047 thì hỏi user trước khi bổ sung):
    - biến thể un_support: A047 luôn mở với `OPEN_FROM_NOTIFICATION_LOCKSCREEN`, không có event. A049 chọn `open_from` theo `canUseFullScreenIntent()` lúc post (A013 tính lúc mở app) và log `notification_lockscreen_un_support` (param `type`);
    - huỷ alarm của các chỉ số slot ≥ số slot hiện tại trong `scheduleLockScreen` (A047 chỉ huỷ khi RC tắt hẳn);
    - parse slot `h:mm a` (A047 đọc `"8:00 PM"` thành 8:00, như A045);
    - `replace` = true thì huỷ noti cũ rồi mới post. A047 post đè cùng id, trong khi comment ở `rewakeLockScreenNotification` của chính A047 ghi cập nhật cùng id không chắc bật lại FSI;
    - gán `session_number` cho event ở overlay và event un_support (xem Bẫy).
  - Nhận diện bằng `detect.any`. Khi app đã theo họ này thì **giữ họ đó**, chỉ bổ sung phần thiếu.
- **Remote config:** xem bảng `rc_keys` trong catalog. Key chuẩn A013 và ý nghĩa:
  - `noti_lockscreen_enable` (Boolean, true): bật/tắt cả schedule lẫn bắn.
  - `noti_lockscreen_slots` (String `"11:30,17:00,20:00"`): slot cho user cũ.
  - `noti_lockscreen_slots_new` (String `"11:30,17:00,20:00"`): slot cho user cài < 24h.
  - `noti_lockscreen_hide_second` (Long, 20): số giây giữ màn sáng (wake lock). Overlay không tự đóng.
  - `noti_lockscreen_replace` (Boolean, false): slot mới thay noti cũ chưa xử lý, hay bỏ lượt.
  - `full_scr_intent` (Boolean, **false**): popup xin FSI ở Home. A013 mặc định tắt.
  - `full_scr_intent_retrigger` (Long, 2): hỏi từ phiên thứ N, hỏi lại sau N phiên.
  - `full_scr_intent_guide` (Boolean, true): hiện tip hướng dẫn đè trên trang Settings.
- **Placement / tracking:**
  - Channel `recovery_channel_lockscreen`, id `LockScreenNotiManager.NOTIFICATION_ID`.
  - Request code: FSI = id noti, mở app = id + 1, alarm = `CODE_REQUEST_LOCKSCREEN` + i.
  - Event:
    - `app_open_from` = `notification_lock_screen` / `notification_lock_screen_un_support`;
    - `notification_lockscreen_un_support` (lúc post);
    - `screen_show` `ScrNotificationLockScreen{1..n}`;
    - `button_click` `BtnClick` / `BtnNotiClose`;
    - `overlay_show` `OvlFSPermission`;
    - `fs_permission_allow` / `fs_permission_exit` / `fs_permission_back`.
  - Chú ý A013 lệch tên: event `notification_lockscreen…` nhưng giá trị `open_from` là `notification_lock_screen…`.
  - Biến thể ở app khác: `show_notification_lockscreen_<type>` (A014, a044, a033), `noti_lockscreen_click`, `open_from_notification_lockscreen`, `lockscreen`.
  - A049 (theo `naming-rules.md` của skill build-tracking trong repo): `app_open_from` = `notification_lockscreen` (như A048) / `notification_lockscreen_un_support` (A048 không có giá trị này, chỉ có event), khớp tên event; `screen_show` `ScrNotificationLockScreen<N>` (N = thứ tự loại, 1..n, như A013, A048); nút `BtnClick` / `BtnNotiClose`. A047 dùng một tên màn `ScrNotificationLockScreen`, không có số.
- **Cách làm** (họ A014 như A013, Compose-first):
  1. **Enum loại noti** (content, ảnh, `OPEN_TO`, `trackName`). Copy/ảnh do MO cấp; chưa có thì tham khảo chuỗi `noti_lockscreen_*` / `fs_permission_*` trong `res/values/strings.xml` của A013 (bản hiện tại) và đánh `TODO(mo)` (catalog MO-95 chưa có Figma/ảnh).
  1b. **Thêm màn overlay vào `screenSkipAdResume`** (hoặc cơ chế tắt app-open resume tương đương của app). A013 (map `LockScreenNotiType.entries` ngay trong `screenSkipAdResume`) và A049 (`LockScreenActivity.TRACKING_SCREENS`) sinh tên màn từ enum loại, nên thêm loại mới không phải sửa tay danh sách.
  2. **`object LockScreenNotiManager`** của app, gồm:
     - channel HIGH riêng;
     - getter RC (key ở trên);
     - parse slot;
     - schedule mỗi slot một request code;
     - fire (replace / Activity đang mở / wake);
     - show: gắn FSI **chỉ khi** màn tắt/khoá **và** `canUseFullScreenIntent()`; không được thì heads-up + log un_support;
     - watcher rewake;
     - `localizedContext`.
     - Đọc `LockScreenNotiManager` ở A013 (bản hiện tại), từng hàm theo đúng thứ tự trên.
  3. **Nhánh `ACTION_LOCKSCREEN` trong receiver:** `goAsync` → watcher → fire → hẹn lại.
  4. **`LockScreenActivity` + Composable content** (overlay đáy màn, nền trong suốt thấy wallpaper):
     - `setShowWhenLocked`/`setTurnScreenOn`;
     - CTA/X/back/`onUserLeaveHint`/`onStop` như A013;
     - khai manifest + theme trong suốt.
     - Đọc `LockScreenActivity` ở A013 (bản hiện tại).
  5. **Wiring** (điểm vào nào cũng phải hẹn lại + đăng ký lại watcher, vì watcher chết theo process):
     - Splash sau bước quyền noti, `BootReceiver`, nhánh `ACTION_LOCKSCREEN` của receiver.
     - A013 làm thêm trong `Application.onCreate` (trên IO) + lifecycle callback "Activity khác resume → huỷ
       noti + finish overlay". App có luật ANR "Application.onCreate chỉ Koin + Timber" (base project, A045)
       thì **giữ luật của repo**: đặt việc hẹn/đăng ký ở Splash/MainActivity + receiver, đừng thêm vào
       `Application.onCreate`.
     - Hẹn lại ở mọi lần mở app có thể đẩy slot hôm nay đang trễ sang ngày mai (Luật 8). Dùng cửa sổ ân hạn
       như A047 (slot đã qua < 2 giờ vẫn bắn hôm nay).
  6. **(Tuỳ chọn — không bắt buộc để Done) Popup xin FSI ở Home** theo MO-2 (overlay + hướng dẫn trước khi
     sang Settings): gate API 34+, đã có quyền noti, RC (mặc định tắt); tối đa 1 lần/phiên. Cần Figma/copy
     (catalog chưa có) → hỏi user có làm không; làm thì tái dùng dialog quyền sẵn có của app, đừng bê hạ tầng
     riêng của A013 (`PermissionSettingsGuide`, `PermissionTutActivity`…) sang. Đọc `HomePermissionPrompts`
     (phần FSI) ở A013 (bản hiện tại).
  7. **Tracking:** thêm `notification_lock_screen(_un_support)` vào `trackAppOpenFrom`; screen/button theo toolkit tracking của app.
  8. **App XML/Fragment** (a031, a033): Activity overlay có thể giữ Compose qua `setContent`, hoặc layout XML; logic manager giữ nguyên. a031 (qibla) có lock screen riêng theo giờ cầu nguyện (`PrayerScheduleLockscreenManager`, RC `time_push_noti_lockscr` JSON) và **gắn FSI không kiểm quyền** → phải thêm gate `canUseFullScreenIntent()`. a028/a036 chưa có tính năng này.
- **Bẫy:**
  - **`CATEGORY_ALARM`:** A013/A014/A045/A048 set; A047 cố ý bỏ (A049 theo A047), vì category này xuyên chế độ Không làm phiền (noti quảng
    bá kêu cả đêm, dùng sai mục đích category). **Mặc định của skill: KHÔNG set** (coi là lỗi đã biết của A013,
    `open-questions.md` Q22). App đang set thì báo trong báo cáo, hỏi user trước khi bỏ vì là đổi hành vi đã
    phát hành.
  - **Wake lock** `SCREEN_BRIGHT_WAKE_LOCK | ACQUIRE_CAUSES_WAKEUP` đã deprecated, máy mới có thể không bật màn. Đường chính là FSI + `turnScreenOn` của Activity.
  - **Watcher** là receiver runtime, chết theo process. Vì vậy phải đăng ký lại ở mọi điểm vào: App, receiver, Boot, Activity.
  - **Giảm số slot qua RC:** ở A013, alarm có chỉ số cao vẫn còn hẹn và bắn thêm 1 lần rồi mới hết. Đây là lỗi đã biết, **đừng chép**: khi schedule, huỷ alarm của các chỉ số ≥ số slot hiện tại.
  - **User mới theo pref `first_install_time`** (A013 ghi ở lần mở app đầu tiên): user cập nhật từ bản cũ chưa có pref sẽ bị coi là "mới" trong 24h đầu sau update. Chấp nhận được; app không có pref này thì dùng `PackageInfo.firstInstallTime`.
  - QC khác nhau theo cách tính: A013 (pref ghi lúc mở đầu) thì `pm clear` là thành user mới; A047, A049
    (`NotificationManager.isNewUser` đọc `PackageInfo.firstInstallTime`) thì `pm clear` lẫn `adb install -r` đều giữ
    mốc cũ → muốn test `slots_new` phải gỡ app rồi cài lại.
  - **Slot sai định dạng xử lý khác nhau giữa app, không báo lỗi:** A049 `parseTime` (kiểm 0..23 / 0..59) bỏ hẳn giờ
    ngoài khoảng (`25:00`, `12:60`, `13 PM`) và dạng `H:mm:ss` → slot đó biến mất.
    - a037 `parseSlotTime` khác: không qua kiểm 0..23 / 0..59 thì thử tiếp `SimpleDateFormat` (lenient), nên vẫn nhận
      `H:mm:ss` và đổi giờ ngoài khoảng thành giờ khác (`25:00` thành 1:00, `12:60` thành 13:00; thử trên JVM). Slot
      không biến mất mà lệch giờ.
  - **Định nghĩa "user mới" lệch giữa các app:** A013/A047/a044 tính cài < 24h (A049 như A047); a016 dùng anchor < 24h; A014 dùng `first_open`; a041 dùng `firstOnboard`; A048 dùng `prefs.firstOpen` (`NotificationManager.isNewUser`).
  - **Default slot lệch giữa các app** (a016: `"11:00,15:00,18:00"`, a27/Langofy: `"9:00,15:00,18:00"`, A047 new: `"09:00,13:00,19:00"`). Giữ giá trị của app đang chạy.
  - **Mặc định `noti_lockscreen_replace`** là `true` ở a037, a039, A045, Langofy.
  - **Hành vi khi user đang dùng máy:** A013 vẫn post heads-up (không FSI); A045/A047 bỏ hẳn lượt đó (A049 theo A047, `NotificationManager.isDeviceInUse`). Chốt theo MO khi port.
  - Mở app thì phải huỷ noti lock screen; nếu không, noti còn treo sẽ rewake mỗi lần bật màn.
  - **Số slot tối đa = số loại noti** ở họ A045/A047: `lockScreenSlots` cắt bằng `take(LockScreenNotiType.entries.size)`. A049 có 3 loại, RC đặt 4 slot thì slot thứ 4 bị bỏ im lặng. Báo MO số slot tối đa của app.
  - **`session_number` = 0 ở process do alarm đánh thức.** Process chưa chạy `MainActivity` nên `TrackingState.sessionNumber` của SDK còn 0; event ở overlay và event un_support mang số 0. Gán từ prefs ở `LockScreenActivity.onCreate` và ngay trước khi log (A049). A013, A047 chưa gán.
- **QC** (gom từ skill `test-noti-lockscreen` và doc `docs/lockscreen-fsi-device-guide.md` của A014, cùng `references/qc.md` §3):
  - **Máy:**
    - Dùng máy thật; emulator không tin được (keyguard và ads gây nhiễu).
    - Ít nhất 1 máy Android 14+.
    - Xiaomi phải bật tay 5 thứ: thông báo, hiển thị trên màn khoá, thông báo toàn màn hình, pin "Không giới hạn", tự khởi động.
  - **Chuẩn bị:**
    - `$S pm grant $P android.permission.POST_NOTIFICATIONS`
    - `$S cmd appops set $P USE_FULL_SCREEN_INTENT allow`; bản `--uid` cũng cần: `$S cmd appops set --uid <uid> USE_FULL_SCREEN_INTENT allow`
    - Xiaomi: `$S cmd appops set $P 10020 allow` (hiện trên màn khoá)
    - `$S dumpsys deviceidle whitelist +$P`
    - `$S settings put global auto_time 0`
    - Kiểm lại: `$S cmd appops get $P | grep -iE "FULL_SCREEN|10020"`.
  - **Ép bắn:**
    - (a) Build debug: tắt màn `$S input keyevent 223`, rồi `$S run-as $P am broadcast --user 0 -n $P/<FQCN receiver> -a <action lock screen>` (A013: `com.example.a013_recovery.action.SHOW_LOCKSCREEN`).
    - (b) Đổi giờ:
      1. Mở app 1 lần để hẹn alarm.
      2. `$S input keyevent 224` (sáng màn khoá; đừng đổi giờ lúc màn tắt vì Doze giữ alarm).
      3. `$S cmd alarm set-time <epoch của slot + 1h05m>`. Phải quá slot + 1 giờ thì alarm mới nổ.
  - **Kiểm tra:**
    - `$S dumpsys alarm | grep -A4 $P` (mỗi slot 1 alarm);
    - `$S dumpsys notification | grep -c <channel lock screen>`;
    - logcat tag `LockScreenNotiManager` (dòng `lockscreen scheduled slot#…`, `show: <type>, rewake=…, fullScreen=…`, `fire: skip slot…`).
  - **Kịch bản:**
    1. Màn tắt/khoá → overlay hiện; CTA → Splash → tính năng, `app_open_from` = `notification_lock_screen`.
    2. Bấm X → đóng, noti mất.
    3. Vuốt/back rời overlay, rồi tắt và bật màn → overlay quay lại (rewake).
    4. `$S cmd appops set $P USE_FULL_SCREEN_INTENT deny` → chỉ heads-up, có event `notification_lockscreen_un_support`, `open_from` = `…_un_support`.
    5. Bắn 2 lần liên tiếp không bấm gì → lần 2 bỏ qua (replace = false).
    6. Cài < 24h dùng `slots_new`.
    7. Mở app → noti lock screen mất.
    8. Đổi ngôn ngữ app → card và noti đúng ngôn ngữ.
    9. Kiểm dark/light.
  - **Bẫy QC:**
    - `force-stop` xoá cả alarm lẫn noti; muốn giết process mà giữ alarm thì dùng `run-as $P kill -9 <pid>`.
    - `am kill` không giết được process trên MIUI.
    - Cài lại APK làm đổi uid và reset appops.
    - Nhảy giờ trên Xiaomi reset quyền FSI/10020; cấp lại trước mỗi lần đo.
    - HiOS/ColorOS có công tắc toàn cục "đánh thức màn hình khi có thông báo" đè lên cài đặt app.
    - Rewake lúc bật màn chỉ chạy khi `isKeyguardLocked` (A013 `onScreenOn`, A049 `LockScreenNotiWatcher`): máy/emulator đặt khoá màn hình là None thì không test được (A049).
    - Xong thì trả giờ: `$S cmd alarm set-time $(( $(date +%s) * 1000 ))` + `$S settings put global auto_time 1`.
  - Skill `test-noti-lockscreen` của A014 grep log và stamp kiểu cũ (`shown_stamp`, `register: watching`). Đừng chép nguyên; đọc log thật của app đang test.
  - Tag log, channel, action, tên receiver ở trên là của A013. App khác dùng tên của app (họ A045 log ở tag `NotificationManager`; `$P` = applicationId; FQCN theo namespace).
  - Shell không gửi được `BOOT_COMPLETED` (broadcast hệ thống được bảo vệ): test bằng reboot thật.

## CC-5 — Noti cá nhân hoá (candidate)

- **Yêu cầu (Crawl Competitor, chưa làm):** content noti dựa trên dữ liệu thật của user:
  - (1) sau scan biết dung lượng còn lại → suy ra junk size;
  - (2) số ngày chưa mở app (hôm nay − ngày mở cuối);
  - (3) khi user chụp màn hình, chơi game, mở app mới → bắn noti nhắc mở app.
  - Ghi chú sheet: user đủ điều kiện mới trigger, mỗi ngày tối đa 1 lần. Ref `assets/refs/CC-5-1.jpg` ("47 Days — You haven't scanned…", "112.99 MB junk…").
- **Hiện trạng:**
  - Chưa app nào làm đủ.
  - A045 làm phần (1): snapshot số liệu vào prefs khi scan xong (`AppData.saveNotiSnapshot`, key `noti_snapshot_at`, `noti_dup_count`…). Lớp `domain/notification/NotiContent.kt` chọn bản "có số" hay "chung" (doc `A045_ByteClean/docs/features/noti-content-data-state.md`).
  - Phần (2): A013 có sẵn `last_day_open` (cập nhật ở `trackingPseudo`, `utils/AppUtils.kt`).
- **Cách làm (khi MO chốt):**
  - Dữ liệu phải nằm sẵn trong prefs, vì receiver ở process lạnh không kịp scan hay đọc DB.
  - Không có số liệu → dùng copy chung, không bao giờ hiện "0 …".
  - Gắn vào daily (MO-71), win-back (MO-73), lock screen (MO-95). Không tạo loại noti mới nếu MO không yêu cầu.
- **Bẫy:**
  - Phần (3) cần theo dõi app khác: UsageStats (`PACKAGE_USAGE_STATS`, quyền đặc biệt, bị Play soi kỹ), AccessibilityService (cấm dùng cho mục đích này), hoặc đọc ảnh chụp màn hình (quyền media). **Không làm** khi chưa có PO/legal duyệt.
  - Copy có số phải có plural cho từng ngôn ngữ.
- **QC:** chưa có (candidate).

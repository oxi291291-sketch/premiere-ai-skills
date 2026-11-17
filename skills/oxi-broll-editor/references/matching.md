# Khớp cảnh — từ câu thoại ra ý hình, rồi ra clip

## Ý hình, không phải từ khóa

Sai lầm mặc định là tìm hình theo danh từ trong câu. Câu thoại và hình đi kèm không
minh họa cho nhau theo kiểu từ điển; hình làm một **vai trò** trong mạch kể.

Ví dụ. Câu: *<lời thoại>*

Khớp từ khóa sẽ đi tìm: người đang nhìn, đôi mắt, ai đó quan sát. Cả ba đều sai —
chúng minh họa mặt chữ và giết mất câu.

Vai trò đúng ở đây là *hé lộ*: một close-up chi tiết bên trong, bộ phận đang chạy
khuất tầm nhìn, màn hình số liệu, macro. Hình phải làm điều câu nói đang làm, không
phải lặp lại điều câu nói đang nói.

Sáu vai trò dùng đủ cho công việc của Oxi:

| Vai trò | Khi nào | Hình cần gì |
|---|---|---|
| `establish` | Mở đoạn, đổi bối cảnh | Wide, tĩnh hoặc chuyển chậm |
| `illustrate` | Câu nêu một sự vật cụ thể | Đúng vật đó, medium hoặc close |
| `evidence` | Câu đưa ra một khẳng định | Thứ chứng minh: số trên màn hình, chữ trên sản phẩm, thao tác thật |
| `consequence` | Câu nói về kết quả | Trạng thái sau, thứ đã thay đổi |
| `contrast` | Câu xoay chiều, có "nhưng" | Hình nghịch với hình liền trước về cỡ cảnh hoặc năng lượng |
| `reveal` | Câu nói về cái khuất, cái bên trong | Close, macro, chi tiết mà mắt thường bỏ qua |

Gán vai trò trước, tìm clip sau. Vai trò thu hẹp thư viện nhanh hơn mọi từ khóa.

## Ràng buộc cứng — loại thẳng

Kiểm trước khi chấm điểm. Vi phạm là loại, không phải trừ điểm.

1. **Đủ dài.** Khoảng hành động liên tục đã xem phải đủ cho khoảng cần lấp, nên có
   khoảng 0.5s dư mỗi đầu. Khoảng này có thể đi qua nhiều nhóm ảnh 2 giây; nhóm ảnh
   không phải giới hạn độ dài clip. Không kéo giãn cảnh ngắn để lấp cho đủ.
2. **Không quay lại khoảnh khắc cũ trong 20 giây.** Trong vòng 20 giây timeline, một
   source chỉ được dùng tiếp nếu điểm vào mới nằm **sau** điểm ra cũ — tức là cắt tiếp
   về phía sau qua cùng một hành động. Quay lại một đoạn đã dùng mới là lặp.
   Hiệu chỉnh 2026-09-29 từ bản dựng thật của Oxi cho Product A: anh cắt 5 lần liền
   trong `CLIP_2137` (1.2–1.9s mỗi cảnh) ở câu "<lời thoại>" và 5 lần trong `CLIP_2156`
   ở bài sa tế. Luật cũ "không dùng lại cùng file trong 20 giây" chặn đúng cách dựng
   đó, nên đã sửa cả `broll_plan.py validate`.
3. **Không ba lần liên tiếp cùng cỡ cảnh.** Ba close liền nhau làm phẳng mạch hình.
   Một chuỗi cắt tiếp trong cùng take tính là một cảnh.
4. **`usable: false` thì không dùng.** Không có ngoại lệ vì "đoạn này không có gì
   khác".
5. **Chưa nhìn thì chưa dùng.** Mọi nhóm ảnh trong khoảng source được chọn phải có
   `look` và `usable != false`, kể cả khi `segment_id` đại diện đã được nhìn.
   `broll_plan.py validate --manifest` kiểm cả khoảng liên tục, chặn luật 4 và 5.
   Xem dày hơn và kiểm chuyển động theo
   `oxi-premiere-workflow/references/footage-index.md`; cảnh còn nghi ngờ về ý nghĩa
   hoặc chuyển động cần cho mạch nối thì chưa đặt.

Vì sao tách khỏi thang điểm: một clip lặp nguồn không phải clip điểm thấp, nó là clip
sai. Trộn vào một thang chung thì sẽ có lúc nó hợp nội dung đến mức thắng điểm và lọt
vào bản dựng — đúng cái lỗi mà người xem nhận ra ngay còn thang điểm thì không.

## Thang điểm

Chỉ chấm những clip đã qua ràng buộc cứng.

| Tiêu chí | Trọng số | Chấm cái gì |
|---|---|---|
| Đúng vai trò | 30 | Clip có làm được vai trò đã gán không |
| Liên quan nội dung | 20 | Chủ thể và hành động có ăn với câu thoại không |
| Chất lượng hình | 20 | Khung có đẹp không: nét đúng chủ thể, sáng, bố cục, nền sạch, máy vững — trong đúng đoạn source sẽ dùng |
| Cỡ cảnh hợp mạch | 15 | Nối với clip liền trước có mượt không, có theo wide → medium → close không |
| Năng lượng | 10 | `energy` của clip so với nhịp đoạn thoại |
| Chuyển động máy | 5 | Hướng lia có chống nhau với clip trước không |

Trọng số đổi ngày 2026-09-29 (cũ: 30/25/15/10/10/10, chất lượng 10). Oxi duyệt: *cảnh
trám chuẩn mục đích* và khung phải đẹp — một cảnh đúng ý nhưng lệch nét hay cháy sáng
kéo cả đoạn xuống, còn chuyển động máy hiếm khi là thứ người xem nhận ra.

`quality` chấm từ ảnh lớn `--detail` của đúng đoạn source định dùng, và **không được
cao hơn `look` của bất cứ nhóm ảnh đi qua trong manifest quá 0.15** (`validate` chặn): `look` là lần nhìn kỹ ở
chặng 1, không được chấm lại cho đẹp lúc cần qua ngưỡng. Thấy `look` ghi sai thì sửa
`look` trong manifest kèm lý do trong `issues`, đừng lách qua điểm.

Trong `broll_plan.json` mỗi clip ghi một khối `scores` với sáu khóa `role`,
`content`, `quality`, `shot_flow`, `energy`, `camera`, mỗi khóa một số **0.0–1.0**
— tự đánh giá clip đó làm được bao nhiêu phần của tiêu chí. `broll_plan.py score`
nhân với trọng số ở bảng trên và cộng lại. Xem `examples/broll-plan-example.json`.

Ngưỡng giao: **80**. Dưới ngưỡng thì tìm lại hoặc để trống chỗ đó và báo Oxi, không
đặt tạm rồi ghi chú xin lỗi. Một chỗ trống được báo rõ thì Oxi xử lý trong ba mươi
giây; một cảnh sai lọt vào bản dựng thì anh phải xem hết mới thấy.

## Khi thư viện không đủ

Job quay cùng buổi thì thư viện hữu hạn — chuyện thiếu là bình thường, không phải
thất bại. Thứ tự xử lý:

1. Cắt segment khác trong cùng file đó ra dùng (khác ý hình là đủ khác).
2. Hạ vai trò: `evidence` không có thì `illustrate` vẫn dùng được.
3. Để MC trên hình lâu hơn. V1 không bắt buộc phải bị che.
4. Nếu đồ họa có thể diễn đạt đúng ý còn thiếu, theo
   `generated-broll.md`: dựng storyboard có hình bằng nhánh HyperFrames/Remotion,
   dừng cho Oxi duyệt trước khi sản xuất; render đã kiểm vẫn qua manifest và
   các cổng B-roll hiện có. Không biến mô phỏng thành bằng chứng thử nghiệm thật.
5. Hình cần bằng chứng thật hoặc không dựng phù hợp thì báo Oxi danh sách chỗ
   còn trống, để anh quyết định quay thêm, mua stock, hay bỏ.

Không bao giờ lấp bằng một cảnh chỉ vì nó trống chỗ. `finishing-layout.md` gọi thẳng
tên thứ cần tránh: *generic filler footage*.

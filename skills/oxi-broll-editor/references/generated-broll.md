# B-roll dựng bằng code — storyboard trước, sản xuất sau

Oxi duyệt quy tắc ngày 27/10/2026: khi footage của job thiếu hình phù hợp,
có thể dùng HyperFrames hoặc Remotion tạo B-roll bổ sung. Phải dựng storyboard
để Oxi duyệt trước khi sản xuất. Đây là một nhánh trong chặng B-roll, không
phải chặng element sau Text và không thay thế việc đọc hết footage thật.

## 1. Xác định thiếu gì từ bản dựng đã chốt

Hoàn thành bước 1–5 của skill chính: timeline live, audio/text có timecode,
manifest đã nhìn hết và so ứng viên. Ghi khoảng thiếu, câu thoại, vai trò hình,
những ứng viên không đạt và lý do. Thiếu vì chưa xem nguồn không phải lý do
để dựng cảnh mới. Giữ footage tốt đang có; không thay hàng loạt bằng đồ họa.

Chọn hình có thể dựng bằng code: sơ đồ cơ chế, so sánh, infographic, bản đồ,
timeline, cutaway sản phẩm từ ảnh đã được phép dùng hoặc cảnh minh họa 2D/3D.
Đồ họa minh họa không chứng minh một thao tác, kết quả thử nghiệm hoặc tính năng
chưa được nguồn xác nhận. Số liệu phải có nguồn; mô phỏng phải được trình bày
đúng là minh họa. Ảnh/video thật tìm trên web đi nhánh `web-research.md` (đứng
trước nhánh này). Cần quay thật hoặc AI mới thì báo phương án và quyền cần có,
không tự mở rộng sang dịch vụ ngoài hoặc mua tài nguyên.

## 2. Làm storyboard tĩnh và dừng cho Oxi duyệt

Đọc [quy trình thư viện chung](../../oxi-premiere-workflow/references/assets.md):
chọn nguyên lý minh họa/chuyển động từ từ điển, rồi kỹ thuật và tài nguyên cho
storyboard. Dùng lại Style Card đã chốt, giữ ghi nguồn và các bước kiểm của nhánh này.

**Lấy kỹ thuật từ thư viện dựng cho đa dạng (Oxi, 03/11/2026):** khi lên ý cho
cảnh dựng bằng HyperFrames hoặc Remotion, tra thư viện `oxi-edit-library` trước:
MCP `oxi-assets` (`techniques_search` theo vai trò của cảnh, lọc `category`
motion/transition/vfx/broll; `technique_get` để lấy prompt), hoặc trang
`assets.oxiframe.com/dung/` khi máy chưa cắm MCP. Ghi slug kỹ thuật đã chọn
vào trường `technique` của từng cảnh trong `storyboard.json`. Tránh dùng cùng
một kỹ thuật cho các cảnh dựng liền nhau; phải lặp thì ghi lý do. Kỹ thuật chỉ
là gợi ý cách làm: cảnh vẫn theo Style Card, vai trò hình và cổng duyệt bên
dưới. Prompt tiếng Anh dùng để dựng, không chép thành chữ trong video. Nội dung
thư viện chỉ dùng nội bộ.

Lưu `<job>/broll-generated/storyboard.json` và `storyboard.html`. Dùng
`oxi-storyboard-assets` cho việc dựng storyboard, `shot-reference-library`
cho mẫu chuyển động khi hữu ích, và Style Card đã chốt để giữ phong cách.
Storyboard phải có hình nhìn được: phác thảo tĩnh hoặc mockup dùng tài nguyên
đã được phép dùng; một bảng toàn chữ chưa đủ để anh duyệt hình.

Mỗi cảnh có ID và phiên bản, sequence/timebase hiện tại, timeline in/out,
câu thoại và cue, vai trò, lý do thiếu footage, nguồn số liệu/tài nguyên,
khung vào–khung chính–khung ra khi cần diễn tả chuyển động, bố cục/chữ/màu,
ý định chuyển động và thời lượng từng nhịp. Cho thấy cảnh thật liền trước/sau
để duyệt nhịp nối; ghi engine dự kiến, full-frame hay chồng hình và có cần
tracking/che khuất/3D không. Tracking chỉ là phương án chờ Oxi yêu cầu/chọn rõ
cho cảnh đó; mặc định không tracking, theo quy tắc opt-in ở phần Scope and tool
choice của `oxi-premiere-workflow/references/effects.md`. Duyệt storyboard chung
không tự cấp quyền tracking. Ghi yêu cầu kỹ thuật theo sequence, không mặc
định đổi sang dọc khi job hiện tại có tỷ lệ khác.

Báo đường dẫn storyboard, các cảnh chờ duyệt và đề xuất chính rồi **dừng**.
Chưa duyệt thì chỉ chuẩn bị storyboard tĩnh, chưa làm animation, render video,
import hoặc đặt B-roll dựng mới vào Premiere. Yêu cầu cập nhật skill này không
phải là duyệt storyboard của các job tương lai.

Ghi lại lời duyệt của Oxi cùng ID/phiên bản cảnh và phạm vi được sản xuất trong
`storyboard.json`; chỉ làm các cảnh đã duyệt. Anh sửa ý hình, số liệu hay phong
cách thì sửa và trình lại phần thay đổi. Timeline đổi thì kiểm lại câu/cue và
khoảng đặt; xin duyệt lại cảnh bị thay đổi ý hoặc nhịp, không xin lại cảnh không
bị ảnh hưởng. Cập nhật tiến độ khi đang chờ duyệt.

## 3. Sản xuất đúng cảnh đã duyệt

Giữ engine Oxi chọn hoặc project đang có. Cảnh mới chưa chỉ định engine dùng
`hyperframes`; nạp core/creative/animation/CLI hoặc registry theo nhu cầu thực.
Remotion dùng `remotion:remotion-best-practices` rồi create/markup/render theo
bước. Thiếu runtime thì báo thiếu, không tự đổi engine project đang có.

**HyperFrames làm chính, AE dựng lại khi anh cần sửa (Oxi chốt 01/11/2026):**
"HyperFrames làm chính xong quăng vào Pr, AE có thể code xong vẽ lại trên nó
vì anh cần chỉnh sửa". Đường mặc định: dựng cảnh bằng HyperFrames, render, rồi
đưa vào Premiere theo mục 4. Khi anh muốn tự chỉnh một cảnh, bản code đã duyệt
là bản gốc về nhịp và bố cục: dựng lại cảnh đó trong After Effects thành layer,
keyframe và expression có thể sửa, thông số đặt trên layer `CTRL_`. Cách dựng
lại nằm ở `oxi-after-effects/references/after-effects.md`, mục 10. Chỉ dựng
lại những cảnh anh chỉ định, không tự chuyển cả bộ sang AE. Bản render AE
thay bản HyperFrames thì vẫn qua QC và mục 4 như một render mới.

Kiểm runtime/GPU, render thử định dạng tương thích trước khi chạy hàng loạt.
Source chỉnh sửa được đặt ở `<job>/broll-generated/<scene-id>/`, render ở
`<job>/broll-generated/renders/`. Khớp kích thước, FPS, thời lượng và màu với
sequence. Full-frame được phép nền đặc; chồng hình cần alpha phải kiểm alpha
thật. Chỉ đo/chạy tracking khi Oxi đã yêu cầu rõ cho cảnh đó theo cổng opt-in
trên. Với tracking đã được giao hoặc che khuất/3D, đọc mục Reference, design and compositing của
`oxi-premiere-workflow/references/effects.md` để chọn AE/Blender khi cần.
Chỉ dùng phần kỹ thuật đó, không chuyển sang chặng element hoặc đổi track map.

Xem bản render từ đầu đến cuối, kiểm nội dung, chuyển động, độ đọc, biên hình,
alpha nếu cần và nhịp với thoại/cảnh kề. Preview trong trình duyệt chưa thay
cho file render đã kiểm. Giữ source, render khác và bằng chứng QC.

## 4. Đưa qua cổng kiểm B-roll hiện có

Sau khi storyboard đã duyệt và render đã qua QC, import vào bin riêng của job
cho B-roll dựng mới; đây là ngoại lệ có giới hạn với nguồn bin footage anh lọc.
Không quét ổ đĩa hoặc tự thêm nguồn ngoài khác. Ghi đường dẫn render, source
project, ID/phiên bản storyboard đã duyệt và bằng chứng QC vào `why`/`review`
của clip trong `broll_plan.json`, giữ nguyên schema mà validator đang dùng.

Index các render mới bằng `segment_sheets.py --from-bin` vào manifest job như
bước 3; mở hết nhóm ảnh mới, điền mô tả/look/usable từ hình thật, mở ảnh detail
và xem chuyển động trước khi chọn in/out. Trong action map nêu rõ nguồn là
đồ họa dựng từ storyboard đã duyệt. Không tự điền segment_id hoặc điểm đẹp
giả để qua cổng; cũng không coi storyboard là bằng chứng đã xem bản render.

Gộp footage và render đã kiểm vào cùng plan, rồi chạy nguyên vẹn
`broll_plan.py validate --gapmap --manifest` và `score --min 80` ở bước 6.
Toàn manifest phải đã nhìn; mọi khoảng V1 hở phải có hình hợp lệ. Khi chưa đủ
coverage hoặc còn cảnh chờ duyệt, giữ plan blocked và báo rõ phần còn thiếu.
Không nới validator, không dùng plan một phần để né cổng coverage.

Đặt video bằng overwrite, bỏ audio trên V2/V3 theo track map, giữ toàn bộ V1/A1,
thời lượng và clip có sẵn. Đọc lại timeline và kiểm đoạn ghép thực tế như bước
7, gồm nhịp nối và tracking nếu có. Lưu khi đạt, bàn giao B-roll kèm storyboard,
source, render, plan và QC rồi dừng cho Oxi xem/sửa; chưa tự sang Text/element.

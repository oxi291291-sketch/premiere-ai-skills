# Research hình ngoài cho chỗ không quay được

Oxi chốt ngày 11/11/2026: chặng B-roll có thêm bước research, tìm ảnh/video trên
web để lấp chỗ không có cảnh quay. Hai quyết định của anh:

- **Được dùng cả nguồn chưa rõ quyền** (báo, web, mạng xã hội); anh tự quyết rủi ro
  bản quyền khi giao khách. Vẫn ghi nguồn và trạng thái quyền cho từng file để anh
  quyết có thông tin.
- **Dừng cho anh duyệt danh sách trước khi tải.** Chưa duyệt thì chưa tải, chưa
  import, chưa đặt lên timeline.

Research ở đây gồm hai việc: **tìm** hình và **kiểm chứng** hình đó cho thấy đúng
thứ câu thoại nói. Một ảnh đẹp nhưng sai model, sai địa danh hay sai thời kỳ là
ảnh sai.

## 1. Khi nào vào nhánh này

Thứ tự bù hình khi thiếu: footage của job → kho OXI Assets (mục Ba kho) →
**research web (file này)** → B-roll dựng bằng code (`generated-broll.md`).
Hình thật đứng trước đồ họa vì nó có giá trị bằng chứng; đồ họa hợp hơn cho cơ
chế, số liệu, sơ đồ. Một chỗ trống có thể dùng cả hai, ghi lý do.

Vào nhánh khi đã xong bước 1–5 của skill chính: manifest đã nhìn hết, ứng viên đã
so, OXI Assets đã tra hoặc đã ghi là không kết nối được. Lập danh sách chỗ trống:
timeline in/out, câu thoại, vai trò hình, lý do footage và Assets không đạt.
Footage chưa xem hết không phải lý do để đi tìm ngoài.

## 2. Phiếu tìm cho từng chỗ trống

Mỗi chỗ trống (chia nhịp theo luật câu thoại trong `placement.md`; một cảnh tối đa
10 s) ghi:

- **Đối tượng cụ thể** câu thoại nhắc: tên riêng, địa danh, sản phẩm kèm model, sự
  kiện, mốc năm, con số. Câu trừu tượng thì ghi hình ẩn dụ định tìm.
- **Từ khóa** tiếng Việt và tiếng Anh (thêm tên Latin/tên gốc khi có).
- **Loại cần**: video nếu vai trò cần chuyển động, ảnh tĩnh nếu là bằng chứng một
  vật/nơi/người; tỷ lệ và độ phân giải của sequence.

## 3. Tìm theo thứ tự nguồn

1. **Khách/hãng cấp**: tài nguyên trong brief, press kit, trang sản phẩm chính hãng.
   Với video booking đây là nguồn đúng nhất cho sản phẩm.
2. **Kho có giấy phép dùng thương mại**: video Pexels, Pixabay, Mixkit; ảnh
   Unsplash, Pexels, Pixabay, Wikimedia Commons. Đọc giấy phép của **từng file**
   (Commons mỗi file một khác: CC BY cần credit, NC/ND ghi rõ).
3. **Web khác** (báo, trang du lịch, trang địa phương, YouTube/TikTok, Facebook):
   dùng được theo quyết định 11/11/2026, đánh dấu `quyen: khong-ro`.

Cùng chất lượng và đúng nội dung như nhau thì chọn nguồn có quyền rõ hơn. Độ phân
giải tối thiểu bằng cạnh dài của sequence; ảnh định zoom thì cao hơn. Tìm bằng
WebSearch và xem bằng trình duyệt; giai đoạn này chỉ xem, chưa tải. Mỗi chỗ trống
tìm tới khi có 2–3 ứng viên đạt, hoặc ghi rõ đã tìm những từ khóa nào mà không có.

Chỉ lấy file media công khai: không đăng nhập, không vượt paywall, captcha hay DRM.

## 4. Kiểm chứng từng ứng viên

Mở ảnh cỡ lớn hoặc xem đoạn video định dùng rồi trả lời:

- **Đúng đối tượng không?** Ảnh gắn với một thứ có tên (người, địa danh, sản phẩm
  + model, sự kiện, năm) phải đối chiếu được với ít nhất **hai nguồn độc lập**
  (vd ảnh chính hãng + bài báo, Commons + trang địa phương). Ghi
  `kiem_chung: doi-chieu-2-nguon | mot-nguon | nghi-ngo`.
- **Con số, chữ trên hình** có khớp câu thoại và kịch bản không.
- **Ảnh AI** trôi nổi trên web: nhận ra thì ghi là ảnh AI, không dùng làm bằng chứng
  cho đối tượng thật.
- **Rủi ro biên tập**: logo/sản phẩm đối thủ trong video booking, watermark của bên
  khác, người thật trong ngữ cảnh nhạy cảm, hình cũ dễ hiểu nhầm là hiện tại.
  Ghi cờ, không tự loại; anh quyết ở trang duyệt.

`nghi-ngo` thì không đưa vào đề xuất chính, để ở mục riêng kèm lý do.

## 5. Trang duyệt rồi dừng

Lưu `<job>/broll-research/research.json` và `research.html`. Trang có:

- Tóm tắt: số chỗ trống, số có ứng viên quyền rõ, số chỉ có ứng viên `khong-ro`,
  số không tìm được.
- Mỗi chỗ trống: timeline in/out, câu thoại, vai trò, 2–3 ứng viên với ảnh thu nhỏ
  (dẫn link gốc, chưa tải), URL trang nguồn, loại, kích thước, nhãn quyền (đỏ cho
  `khong-ro`), mức kiểm chứng, cờ rủi ro, đề xuất chính và lý do.
- Ảnh tĩnh: đề xuất cách đặt (`tinh` hoặc `zoom-cham`, `pan`) để anh duyệt luôn.
- Mục riêng: ứng viên nghi ngờ và chỗ trống không tìm được, kèm gợi ý chuyển sang
  B-roll dựng bằng code.

Báo đường dẫn trang rồi **dừng**. Ghi lựa chọn của anh vào trường `duyet` của từng
chỗ trống trong `research.json`. Anh đổi ý hoặc timeline đổi thì cập nhật đúng phần
bị ảnh hưởng.

## 6. Tải, chuẩn hóa, index, đưa qua cổng

Chỉ làm với ứng viên đã duyệt:

1. Tải bằng curl vào `<job>/broll-research/files/`, tên `<gap-id>_<nguon>.<ext>`,
   không ghi đè. Kiểm đúng loại file và kích thước bằng ffprobe, ghi sha256.
   Video từ nền tảng chỉ giữ đoạn cần dùng cộng tay cầm hai đầu.
2. **Ảnh tĩnh → clip video** để đi chung đường index và validator, không nới cổng:
   ffmpeg dựng mp4 đúng kích thước, fps của sequence, dài hơn cảnh cần dùng ít nhất
   2 s, áp đúng cách đặt anh đã duyệt (tĩnh/zoom/pan). Ảnh khác tỷ lệ thì nền mờ
   hoặc crop theo bố cục, ghi cách xử lý. Lưu ở `files/clips/`.
3. Import vào bin riêng `BROLL_RESEARCH` của project. Đây là ngoại lệ có giới hạn
   với luật nguồn bin, giống bin render của `generated-broll.md`.
4. Index bằng `segment_sheets.py --from-bin` vào manifest job như bước 3 skill
   chính, nhìn hết nhóm ảnh mới, điền mô tả/look/usable từ hình thật.
5. Gộp vào `broll_plan.json`, ghi research id, URL nguồn và trạng thái quyền vào
   `why`/`review` của clip, giữ nguyên schema. Chạy nguyên vẹn `validate` và
   `score --min 80` ở bước 6.
6. Ghi `<job>/broll-research/credits.md`: mỗi file dùng trên timeline một dòng
   gồm timeline in/out, URL nguồn, tác giả/credit, giấy phép hoặc `khong-ro`.
   Chặng QC/xuất đối chiếu danh sách giấy phép từ file này.

Báo cáo cuối chặng B-roll ghi rõ số cảnh research đang dùng và **bao nhiêu cảnh
`khong-ro` quyền**, để anh quyết trước khi giao khách.

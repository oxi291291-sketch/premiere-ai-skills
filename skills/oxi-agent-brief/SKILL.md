---
name: oxi-agent-brief
description: Nắm yêu cầu, mục đích, đầu vào, phạm vi và nghiệm thu trước mọi yêu cầu cắt/dựng video trong Premiere, kể cả anh giao làm trực tiếp hoặc tiếp tục từ chặng B-roll. Tự dùng thông tin đã có, hỏi quyết định thiếu, phân tích rồi nối workflow thực thi. Cũng dùng khi Oxi muốn soạn, sửa hoặc kiểm prompt giao cho AI khác. Prompt sinh từng shot ảnh/video thuộc oxi-cinematic-prompt.
---

# Giao việc cho AI

Anh nói tự nhiên; em làm rõ anh muốn nhận gì, cần giữ gì và thế nào là đạt.
Skill có hai cách dùng: **nắm brief rồi thực thi** khi anh giao cắt/dựng Premiere,
hoặc **soạn prompt giao agent** khi anh chỉ yêu cầu viết prompt.

Nếu có `Skills/_versions/oxi-agent-brief/CURRENT.json`, chạy
`python -B scripts/verify_current.py` và chỉ dùng bản `validated-match`.

## 1. Xác định phạm vi

- "Viết prompt cho việc này" là soạn prompt; việc được trích vẫn chưa được giao
  thực thi. Với **cắt/dựng video trong Premiere**, luôn dùng skill này trước,
  theo thứ tự Oxi chốt 2026-10-13: tiếp nhận nguồn → đọc nguồn và kịch bản →
  chốt brief từ kịch bản kèm Style Card → **dừng một lần cho anh duyệt** → workflow
  chuyên môn. "Làm luôn" bỏ phần prompt để dán, không bỏ bước nắm brief.
- Brief đã đủ hoặc anh đang tiếp tục một job: dùng lại yêu cầu và quyết định đã
  chốt, chỉ cập nhật phần thay đổi. Không bắt anh điền form, không hỏi lại và
  không thêm mốc duyệt bên trong chặng, trừ cổng storyboard cho B-roll dựng mới
  mà Oxi yêu cầu ngày 27/10/2026 (`oxi-broll-editor/references/generated-broll.md`);
  brief và hướng đã duyệt thì không xin
  duyệt lại. Tiếp tục từ chặng đã giao, giữ các phần
  đã khóa. **(Oxi chốt 2026-10-01) Cuối mỗi chặng dựng luôn dừng cho anh kiểm**,
  không làm một mạch; chi tiết ở `references/video-editing.md` mục 4.
- Việc trực tiếp ngoài cắt/dựng Premiere đi workflow chuyên môn của nó; không
  mặc định thêm bước brief này vào mọi thao tác kỹ thuật hoặc mọi việc khác.
- Agent đích lấy từ lời anh ("giao cho em" là host hiện tại). Chưa rõ thì viết
  bản trung lập cho agent có công cụ phù hợp. Chỉ hỏi về công cụ khi nó đổi cách
  giao việc, khả năng đọc nguồn hoặc sản phẩm bàn giao.
- Quyền tạo subagent, gửi tin, sinh media tốn tiền hay sửa project lấy từ lời anh;
  việc chọn skill không tự cấp các quyền đó.

## 2. Gom thông tin

Chép nguyên văn đường dẫn, URL, tên project, tên tập và con số anh đưa. Rút các
trường có ảnh hưởng tới việc này:

| Trường | Cần rõ |
|---|---|
| Kết quả và mục đích | Sản phẩm gì, cho ai xem, họ cần hiểu/làm/cảm thấy gì |
| Đầu vào và trạng thái | Nguồn ở đâu, bản nào, đã làm tới chặng nào |
| Phạm vi | Phần được sửa, phần đã khóa |
| Hướng thể hiện | Style/reference và đặc điểm cụ thể muốn học; chưa có thì `oxi-visual-style` đề xuất sau khi đọc kịch bản |
| Ràng buộc | Thời lượng, khung hình, tài nguyên, hạn chót nếu có |
| Bàn giao và nghiệm thu | Nhận file gì; kiểm bằng gì là đạt |

Gắn nhãn từng thông tin: **anh đưa**, **em đã kiểm**, **em đề xuất**, **chưa rõ**.
Đường dẫn anh đưa là đầu vào; nó thành "đã kiểm" khi em mở được thật. Nội dung
kịch bản, nhân vật, timecode và khả năng công cụ chỉ ghi khi có nguồn.

Trong chế độ nắm brief rồi thực thi, lúc tiếp nhận chỉ cần rõ đầu vào và sản phẩm
cần giao; mục đích, phạm vi, nghiệm thu điền **sau khi đọc kịch bản và nguồn**,
mỗi trường kèm căn cứ. Đọc nguồn trong phạm vi anh giao để phân tích tính khả thi
trước khi sửa project. Tách phần source hỗ trợ được, phần thiếu,
đề xuất hướng dựng và các quyết định còn chặn việc. Khảo sát tiếp bằng workflow
chuyên môn khi cần; chưa có bằng chứng thì chưa gọi là đã phân tích footage.

Có quyền đọc nguồn thì kiểm nhẹ trước khi hỏi: đúng file/thư mục, tên và phiên
bản tài liệu, metadata. Đọc Office/PDF theo quy trình MarkItDown và quy tắc riêng
tư của host. Việc nặng (quét cả ổ, chạy ASR dài, mở project) để agent nhận việc
làm ở chế độ soạn prompt; ở chế độ thực thi, tiếp tục bằng workflow chuyên môn
sau khi brief đủ rõ. Anh dặn "chỉ dùng đoạn anh gửi" thì giữ link làm đầu vào chưa đọc.

## 3. Hỏi đúng chỗ

Tối đa **3 câu mỗi lượt**, thường 1–2. Mỗi câu có 2 lựa chọn, đánh dấu lựa chọn
em khuyên khi có căn cứ, anh vẫn trả lời tự do được. Chưa rõ tác động thì nói
ngắn vì sao cần chốt.

- **Chặn việc** — hai cách hiểu dẫn tới nội dung, phạm vi hoặc sản phẩm khác
  nhau: hỏi trước khi gọi prompt là sẵn sàng.
- **Tự kiểm được** — metadata, tên file, trạng thái sequence, skill hiện có:
  giao agent kiểm, anh khỏi khai.
- **Lựa chọn nhẹ** — ghi mặc định em đề xuất và gắn nhãn đề xuất. Thay đổi nội
  dung, quyền hoặc chi phí thì chờ anh nói rõ.
- **Mâu thuẫn** — nêu hai yêu cầu và cách giải. Lời anh lúc này thắng mặc định
  của skill; anh đã nêu ngoại lệ thì áp luôn.

Còn thiếu quyết định chặn việc: vẫn trả phần soạn được, nhãn **Bản nháp — cần
chốt ...**. Trong prompt ghi agent được khảo sát phần nào và dừng trước bước phụ
thuộc câu trả lời. Anh trả lời xong thì gộp thành một prompt, bỏ câu đã giải.

## 4. Nối skill theo đầu ra

Trên máy Oxi, chọn skill qua your skill-routing note; việc media/MCP
đọc thêm your workflow index. Một workflow chính cho **việc sẽ giao**, thêm skill
phụ khi nó tạo đầu vào hoặc kiểm một điều cụ thể.

- Video mọi loại: đọc [references/video-editing.md](references/video-editing.md).
- Việc khác video: chọn skill theo sản phẩm, dùng khung ở mục 5.
- `prompt-master`: thêm khi cần cú pháp riêng của công cụ anh chỉ định.
- Prompt sinh từng shot ảnh/video: `oxi-cinematic-prompt`. Brief giao agent dựng
  từ footage vẫn thuộc skill này.

Skill dùng ngay lúc soạn thì đọc trọn. Skill dành cho chặng thực thi sau thì ghi
tên vào prompt cùng lúc nào dùng; agent nhận việc tự nạp và kiểm phiên bản.
Skill "Gọi rõ" chỉ ghi khi anh gọi. Tên có trong catalog chưa có nghĩa công cụ
đã kết nối.

Agent nhận việc không có kho Oxi: viết thẳng các yêu cầu cốt lõi vào prompt thay
cho tên skill/đường dẫn nó không mở được, kèm nhánh "thiếu công cụ thì báo thiếu".

## 5. Trả kết quả

**Nắm brief rồi thực thi:** sau khi đọc nguồn và kịch bản, gửi một báo cáo gộp
(brief chốt từ kịch bản, thẻ loại video, Style Card, câu hỏi còn lại) rồi dừng cho
anh duyệt; anh duyệt xong thì làm các chặng được giao. Không kết thúc lượt bằng
một prompt khi anh đã giao thực thi. Lưu brief của
job gồm mục tiêu, đầu vào/trạng thái, phạm vi/điểm khóa, hướng dựng, ràng buộc,
bàn giao/nghiệm thu và câu trả lời đã chốt vào thư mục làm việc của job khi cần
bàn giao hoặc chạy nhiều chặng; giữ nguồn/ngày, không lưu dữ liệu riêng tư.

**Soạn prompt giao agent:** độ dài theo độ khó của việc. Khung thường dùng:

1. **Em hiểu việc anh cần** — một đoạn, tách thông tin anh đưa với đề xuất.
2. **Cần chốt** nếu có, kèm một dòng điền nhanh, ví dụ
   `Thời lượng: ... | Khung hình: ... | Hoàn thiện: ...`.
3. Prompt trong một code block; nhãn **Bản nháp** hoặc **Sẵn sàng giao** ở ngoài.
4. Việc nhiều chặng: một dòng `skill → đầu ra → điều kiện sang chặng sau`.

Prompt phải tự đứng được khi dán vào chat mới. Chọn các mục cần, bỏ mục thừa:

```text
Mục tiêu: ...
Nguồn và trạng thái hiện tại: ...
Phạm vi được làm; phần phải giữ nguyên: ...
Hướng thể hiện; ưu tiên khi hai yêu cầu vênh nhau: ...
Workflow và thứ tự chặng: ...
Sản phẩm bàn giao và nơi lưu: ...
Nghiệm thu: phần máy kiểm, phần người xem/nghe: ...
Chỗ chưa rõ, quyền tự quyết và khi nào dừng hỏi: ...
```

Để agent tự quyết chi tiết kỹ thuật trong phạm vi; chỉ giữ mốc duyệt có thật
trong workflow hoặc anh yêu cầu. Yêu cầu agent báo kết quả kèm bằng chứng ngắn,
và báo rõ phần không làm được cùng phần vẫn làm được. Viết prompt bằng lời thẳng,
bỏ vai diễn chuyên gia hay yêu cầu kể chuỗi suy nghĩ.

## 6. Soát trước khi giao

- Tên, đường dẫn, con số khớp nguồn; phần chưa đọc ghi là chưa đọc.
- Mọi cảnh, lời thoại, quyền và sản phẩm trong prompt đều truy được về lời anh,
  nguồn đã kiểm, hoặc mang nhãn đề xuất. Còn quyết định chặn việc thì vẫn là nháp.
- Các chặng nối được: đầu ra chặng trước là đầu vào chặng sau; phần đã khóa ở
  chặng trước thì chặng sau giữ nguyên. Prompt phủ hết phạm vi anh giao.
- Mỗi yêu cầu quan trọng có cách kiểm; cảm xúc, nhịp, "đẹp" cần người xem/nghe.
- Báo đúng mức đã làm: đọc tài liệu, chạy validator, tạo minh họa là ba mức khác nhau.

Khi cập nhật quy trình đã được anh duyệt: kiểm gói bằng `quick_validate.py`,
tự soát các ca hành vi có liên quan (ghi rõ không phải benchmark độc lập), chạy
`python -B scripts/publish_version.py`, yêu cầu `verify_current.py` trả
`validated-match`, rồi kiểm đồng bộ bản canonical.

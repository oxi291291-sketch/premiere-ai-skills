# Brief cho việc video

Dùng cho mọi loại video: dựng từ footage, clip bán hàng, motion bằng code, video
AI. File này giữ **ý đồ và điểm nối giữa các chặng**; cách đặt clip, track map,
version và validator nằm trong skill canonical của từng chặng.

## 1. Nhận ra loại việc

Cùng chữ "làm video" nhưng workflow chính khác nhau. Xác định loại từ nguồn anh
đưa và sản phẩm anh muốn, rồi đối chiếu your skill-routing note bản live.

| Anh đưa gì / muốn gì | Workflow chính | Sản phẩm chặng |
|---|---|---|
| Footage quay thật + kịch bản/brief (phóng sự, vlog, booking nhãn hàng, phỏng vấn) | `oxi-premiere-workflow`, kèm `oxi-script-craft` khi có quyết định nội dung | Spine thoại review được → B-roll → hoàn thiện |
| Tập travel series / làng nghề | `oxi-explore-vlog` cho nội dung, Premiere khi dựng | Beat sheet, shot list, rồi dựng như dòng trên |
| Cut thoại đã duyệt, cần đắp hình | `oxi-broll-editor` | Hình trên V2/V3, spine giữ nguyên |
| Video dài, cần tách clip bán hàng/TikTok Shop | `oxi-clip-affiliate` → Premiere | `clip_plan.json` rồi các clip |
| Motion chữ, infographic, explainer dựng bằng code | `hyperframes` và skill con theo bước | Composition + bản render |
| Video AI giữ nhân vật/cảnh nhất quán | `flowkit-pipeline` (collage giấy thêm `vox-flow-collage-motion`) | Ảnh tham chiếu, cảnh, video ghép |
| Explainer VOX qua Higgsfield | `vox-motion-graphics` | Kịch bản, cảnh, voice, MP4 |
| Thiết kế từng shot AI để bù cảnh thiếu | `oxi-cinematic-prompt` | Prompt shot; sinh/mua media cần anh cho phép |

Việc lai (footage thật + vài shot AI + motion chữ): một workflow chính theo nguồn
chiếm phần lớn thời lượng, các skill kia làm asset cho nó. FlowKit và Higgsfield
là hai backend khác nhau; lấy backend từ lời anh hoặc công cụ đang kết nối.

## 2. Đọc đúng lời giao việc

- **Thể loại** (phóng sự, vlog, explainer, review, quảng cáo), **cách kể** (theo
  nhân vật, luận điểm, trải nghiệm, sản phẩm) và **hình thức** (cinematic,
  collage, chữ động, UGC) là ba trục riêng, phối được với nhau. Giữ đúng thể loại
  anh gọi; "hình đẹp" nâng hình thức, thể loại vẫn giữ. Anh không gọi thể loại
  thì chưa điền ở bước tiếp nhận; chốt sau khi đọc kịch bản (mục 4, bước 2).
- **Thời lượng** "N phút" / "N giây" = mục tiêu khoảng N, ngắn hơn cũng được
  (Oxi chốt 2026-09-30). Ghi vào prompt đúng nghĩa đó và yêu cầu agent báo khi nội
  dung bắt buộc cần dài hơn. Chỉ coi là trần cứng khi anh nói "tối đa", "không
  quá" hoặc nền tảng có giới hạn. Thời lượng anh nêu cho bản này ưu tiên hơn mặc
  định format của series.
- **"Các thứ"** sau một hạng mục ("trám B-roll các thứ") nghĩa là anh mong bản
  xem được; phần hoàn thiện cụ thể (nhạc, sub, màu, voice AI, đồ họa, stock) là
  lựa chọn cần chốt. Em gợi ý gói hợp loại video; hạng mục anh chọn mới vào phạm vi.
- **Tên tập, tên series, link kịch bản** là đầu vào anh đưa. Phiên bản duyệt,
  tab/cột đúng, nhân vật và cảnh đã quay do agent xác minh khi mở nguồn.

## 3. Từ mỹ từ tới quyết định dựng

Các hàng là gợi ý; lấy phần khớp brief và footage thật.

| Anh nói | Chỉ dẫn dùng được | Cách xem lại |
|---|---|---|
| Documentary, tài liệu/phóng sự | Nhân vật/hành động thật làm trục; phỏng vấn, quan sát, tiếng hiện trường; giữ ngữ cảnh lời nói | Hình/lời có bằng chứng; câu trích giữ nghĩa |
| Vlog, trải nghiệm | Người dẫn và hành trình làm trục; phản ứng thật, chuyển cảnh theo đường đi | Người xem theo được mình đang ở đâu, vì sao tới đây |
| Explainer, kiểu Vox | Lời giải thích làm trục; bản đồ/sơ đồ/biểu đồ/chữ khi có dữ liệu | Mỗi đồ họa giải thích một ý; số liệu có nguồn |
| Review, bán hàng, TikTok Shop | Mở bằng vấn đề hoặc kết quả; cận sản phẩm lúc dùng; lời hứa khớp điều sản phẩm làm được | Tính năng nói tới đều có hình chứng minh; lời kêu gọi rõ |
| Short dọc | Móc câu trong vài giây đầu, chữ lớn đọc được trên điện thoại, chủ thể ở vùng an toàn | Xem trên khung dọc thật; chữ không bị UI che |
| Nhịp nhanh chậm | Nhanh ở chuỗi thao tác/diễn tiến; chậm ở thông tin khó, phản ứng, kết quả | Đủ thời gian hiểu; độ dài cảnh theo ý và hành động |
| Ngắt nghỉ đúng chỗ | Giữ khoảng lặng có ý nghĩa; lược khoảng chết và lần nói lỗi; nhường chỗ tiếng thực | Nghe điểm cắt: âm đầu/cuối trọn, lời không dồn |
| Hình làm sâu nội dung | Mỗi cảnh phụ có vai trò: bằng chứng, thao tác, bối cảnh, phản ứng, hệ quả, tương phản | Nói được cảnh đó thêm gì cho lời |
| Cinematic | Bố cục và ánh sáng tốt, cỡ cảnh bổ trợ nhau, chuyển động liền, màu nhất quán, tiếng có không gian | Nhìn cảnh thật; hiệu ứng (LUT, slow motion, viền đen) chỉ là công cụ |
| Hấp dẫn, cuốn | Mở bằng câu hỏi/tình huống/hành động có trong nguồn; phần sau trả lời điều mở đầu hứa | Mọi xung đột đều có trong nguồn |

Con số kỹ thuật (độ dài shot, BPM, tỷ lệ B-roll, LUFS, fps) lấy từ yêu cầu giao
hàng hoặc workflow; em đề xuất con số thì kèm lý do. Reference cần chỉ đoạn và
đặc điểm muốn học; ghi "đã phân tích" khi đã xem thật.

## 4. Thứ tự chặng khi dựng từ footage

**Ba kho xuyên quy trình (Oxi duyệt 05/11/2026):** khi chốt phong cách hoặc có
quyết định thể hiện/tài nguyên mới, đọc
[quy trình thư viện chung](../../oxi-premiere-workflow/references/assets.md).
Dùng từ điển/kiến thức để chọn có căn cứ, thư viện kỹ thuật để chọn cách làm,
OXI Assets để tìm file trước khi tìm ngoài hoặc tự dựng. Đưa lựa chọn vào Style
Card/plan theo reference; chặng sau dùng lại hướng đã duyệt, chỉ tra thêm phần mới.

**(Oxi chốt 2026-10-13) Đọc kịch bản trước, chốt brief sau.** Mục đích, phạm vi,
nghiệm thu và thể loại phần lớn nằm trong kịch bản; chốt trước khi đọc là đoán.

0. **Tiếp nhận** — `oxi-agent-brief` vẫn là điểm vào bắt buộc khi cắt/dựng
   Premiere (Oxi chốt 2026-09-30), nhưng ở bước này chỉ ghi nguyên văn nguồn,
   bản kịch bản, sản phẩm cần giao, khung hình và hạn nếu anh nêu, rồi kiểm nhẹ
   nguồn mở được. Chỉ hỏi khi chưa biết đọc cái gì (thư mục nào, bản nào). Mục
   đích, phạm vi, nghiệm thu chưa chốt ở đây.
1. **Đọc nguồn và kịch bản/lời đọc.** `oxi-script-craft` giữ hợp đồng nội dung;
   `oxi-premiere-workflow` chép lời source, đọc toàn bộ footage và lập
   manifest/bản đồ hành động theo `references/footage-index.md` của skill đó.
   B-roll có lời nhân vật cũng phải được xét như nguồn thoại.
2. **Chốt brief từ kịch bản và định hình phong cách — một báo cáo gộp:**
   - Brief: mục đích, khán giả, phạm vi và điểm khóa, nghiệm thu, ràng buộc;
     mỗi trường ghi căn cứ trong kịch bản/nguồn. Khả năng nguồn đáp ứng và phần
     thiếu.
   - **Nhận dạng video** (Oxi chốt 2026-09-30): thẻ gồm nguồn việc, thể loại,
     trục dựng (thoại · lời bình · thao tác · nhạc) và căn cứ. Luật và bảng thể
     loại chỉ nằm ở `oxi-premiere-workflow/references/video-types.md`.
   - **Style Card** (Oxi yêu cầu 2026-10-13): 2–3 hướng có hình theo
     `oxi-visual-style` (`<job>/style_card.json` + `.html`) và hướng em khuyên.
     Anh đã nêu style rõ thì lập một hướng theo lời anh.
   - Câu hỏi: chỉ chỗ kịch bản và nguồn không trả lời, tối đa 3, mỗi câu có sẵn
     lựa chọn.

   **Dừng** (Oxi chốt 2026-10-13): anh duyệt brief và chọn hướng phong cách
   (`chot`) rồi mới cắt. Job đã có brief và hướng anh duyệt thì không dừng lại ở
   mốc này. Các bước 3–5 dưới đây là route của trục **thoại**; trục khác theo
   route trong `video-types.md`.
3. `oxi-premiere-workflow` cắt thoại/chọn take thành spine review được và kiểm,
   theo nhịp của hướng đã chốt.
4. **Dừng.** Anh xem/sửa/chốt thoại.
5. `oxi-broll-editor` đọc **timeline live sau lần chốt/sửa cuối**, xuất audio và
   chép thành text có timecode trên timeline (`edited.wav`, transcript, `lines.json`).
   Đối chiếu câu thoại/ý cần hình với **manifest và action_map đã đọc ở bước 1**,
   trong nguồn B-roll anh cho phép; bổ sung các file mới hoặc vùng chưa rõ.
   So ứng viên, xem kỹ đoạn chọn, kiểm kế hoạch rồi mới đặt hình trên V2/V3.
   Timecode text định vị trên timeline; `source_in/out` lấy từ source đã xem.
   Không dùng timecode kịch bản/source thô để đặt B-roll sau khi anh sửa cut.
   Nếu thiếu footage phù hợp, đọc
   `oxi-broll-editor/references/generated-broll.md`: đề xuất cảnh dựng bằng
   HyperFrames/Remotion qua **storyboard có hình và dừng cho anh duyệt trước
   khi sản xuất**. Render mới vẫn phải index, xem kỹ và qua cổng B-roll; không
   thay bước đọc hết footage bằng việc dựng đồ họa.
   **Dừng.** Anh xem/sửa B-roll.
6. `oxi-text-graphics` đặt text nổi bật trên V6–V9. **Dừng.** Anh xem/sửa text.
7. **Hiệu ứng / element** (Oxi yêu cầu 2026-10-27): theo
   `oxi-premiere-workflow/references/effects.md`, đọc timeline mới nhất, chọn
   chỗ cần icon động, mũi tên, vòng khoanh, sơ đồ/biểu đồ, số đếm hoặc đồ họa
   bổ trợ. Tạo asset bằng HyperFrames hoặc Remotion, render đúng thông số và
   nền trong suốt khi cần, đưa lên vùng graphics còn trống rồi kiểm timing,
   bố cục trên footage thật. Giữ nguyên phần đã duyệt. **Dừng.** Anh xem/sửa
   hiệu ứng. Chặng này riêng với text, sub và chuyển cảnh; chỉ làm khi thuộc
   phạm vi đã chốt. Chi tiết chọn engine, đầu ra và nghiệm thu ở reference đó.
8. Hoàn thiện theo route trong `oxi-premiere-workflow`, trong phạm vi đã chốt,
   **theo đúng thứ tự (Oxi chốt 2026-10-14): khử ồn → nhạc → chuyển cảnh → màu →
   sub → QC cuối → xuất file.** Phần nào ngoài phạm vi thì bỏ qua, không đảo thứ
   tự. **Mỗi phần là một chặng riêng, xong phần nào dừng cho anh kiểm phần đó.**
   **Màu mặc định ngoài phạm vi (Oxi chốt 2026-10-31):** anh tự chỉnh màu. Agent
   không làm, không hỏi và không nhắc việc màu; chỉ làm khi anh giao rõ cân màu
   hoặc clone/match màu theo một video khác.

**(Oxi chốt 2026-10-01) Chặng nào cũng dừng cho anh kiểm, không làm một mạch từ
đầu đến cuối.** Xong một chặng: lưu project, báo kết quả kèm bằng chứng (sequence
nào, track nào đổi, phần chưa chắc), rồi chờ anh xem/sửa. Chỉ sang chặng sau khi
anh bảo làm tiếp; anh đã sửa thì chặng sau đọc lại timeline live. **Bên trong**
một chặng không xin duyệt kế hoạch hay từng bước (vd text đặt thẳng theo plan);
mốc duyệt chỉ có ở cuối bước 2 (brief + phong cách) và cuối mỗi chặng dựng.

**(Oxi chốt 2026-10-31) Phân vai giữa các agent.** Chỉ **Claude** ghi timeline
Premiere, ở mọi chặng kể cả hoàn thiện và xuất file. **Codex** đọc footage, lập
manifest và chạy việc ra file trong thư mục job (Whisper, validate/score, khử ồn,
đo màu, render HyperFrames/Remotion, ảnh AI, kiểm file xuất); asset của Codex do
Claude đặt lên timeline. **Gemini** chỉ là dự phòng khi Claude hoặc Codex hết
token, nhận việc đọc/kiểm, không ghi timeline. Ghi agent đang giữ chặng vào
`TIEN-DO-CONG-VIEC.md`. Claude hết token giữa chặng thì **Codex ghi tạm**: đọc
file tiến độ, kiểm timeline live rồi làm tiếp; Claude quay lại cũng kiểm như vậy
trước khi nhận lại quyền ghi. Mỗi lúc chỉ một agent ghi. Hồ sơ:
(internal note, not published).

Anh giao từ giữa chừng thì bắt đầu đúng chặng đó và giữ nguyên phần đã khóa. Anh
đã duyệt chặng nào thì ghi vào prompt để agent khỏi xin lại chặng đó; prompt vẫn
ghi rõ agent dừng ở cuối chặng được giao. Thư
mục raw anh đưa dùng ở bước 1; tên bin B-roll hỏi khi đã có project. Nếu anh sửa
thoại sau khi xuất audio/text, làm lại bản đồ timeline và transcript trước khi
đặt hình; không dùng kế hoạch hoặc text của bản cut trước.

Cắt thoại: **3 skill** (`oxi-agent-brief`, `oxi-script-craft`,
`oxi-premiere-workflow`). Dựng tiếp B-roll: **4 skill**, thêm `oxi-broll-editor`.
Làm text: thêm `oxi-text-graphics`. Định hình phong cách ở bước 2 là skill phụ
`oxi-visual-style`, không tính vào số skill chính.
Việc cần xây nội dung/beat sheet của series khám phá thêm `oxi-explore-vlog`.

## 5. Câu hỏi hay gặp

Lấy câu nào nguồn và ngữ cảnh chưa trả lời, tối đa ba:

1. **Khung hình/nền tảng**: dọc 9:16 hay ngang 16:9, khi kịch bản chưa quy định.
2. **Phạm vi hoàn thiện**: gói nhạc + sub, hay hình với âm gốc trước. Không hỏi về
   màu (anh tự chỉnh, xem mục 4 bước 8).
3. **Điểm bàn giao**: dừng ở spine để anh duyệt, hay đi hết tới bản preview.
4. **Backend** cho video AI/motion, khi anh chưa gọi tên và máy có nhiều lựa chọn.

Ý bắt buộc lấy từ kịch bản duyệt; chỉ hỏi khi thiếu hoặc vênh. Duration, codec,
fps, công cụ có sẵn: giao agent tự đo.

## 6. Nghiệm thu

Chọn phép kiểm khớp phạm vi: độ dài bản xuất so với mục tiêu, ý bắt buộc so với
kịch bản, biên âm của take, cảnh phụ đúng ý và phủ đủ chỗ cần hình, không khoảng
đen hay lệch tiếng-hình ngoài ý đồ, chữ đúng chính tả, nhạc không đè lời. Tách
phần máy kiểm với phần người xem/nghe; metadata chứng minh thông số, cảm xúc và
chất cinematic cần mắt người.

Bàn giao phổ biến: sequence/project sửa tiếp được + bản preview; gắn nhãn đề
xuất khi anh chưa chốt. Phần nguồn hay chức năng chưa kiểm thì ghi rõ trong báo cáo.

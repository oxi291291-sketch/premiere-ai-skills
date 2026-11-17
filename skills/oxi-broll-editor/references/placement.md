# Đặt hình lên V2/V3

## Chia V2 với V3

Theo track map ở `oxi-premiere-workflow/references/finishing-layout.md`:

- **V2** — B-roll chính: sản phẩm, chi tiết, demo, thứ câu thoại đang nói tới. Phần
  lớn cảnh nằm ở đây.
- **V3** — B-roll phụ, nested sequence, reference footage, và mọi thứ cần **chồng
  lên** một cảnh V2 đang chạy.

Quy tắc quyết định: chỉ lên V3 khi thật sự cần hai lớp hình cùng lúc. Nếu chỉ là cảnh
kế tiếp, nó thuộc V2. Đẩy lên V3 để tránh va chạm là dùng track như chỗ chứa rác, và
chặng finishing sau sẽ phải dọn.

Muốn chồng lớp thì lên track cao hơn bằng `pr_ensure_tracks` — **không bao giờ** ghi
đè lên thứ đang có để giải quyết va chạm. Phá nội dung đang nằm đó là quyết định của
Oxi, không phải phương án dự phòng của skill.

## Đặt theo câu thoại và độ dài cảnh (Oxi, 11/11/2026)

Anh dặn: *"đặt broll theo câu lời thoại, kiểu có ngắn có dài, nếu dài quá trên 5-10s
thì chia làm 2-3 cảnh"*.

- **Một câu thoại, hoặc một vế của câu dài, là một ý hình.** Cảnh minh họa đúng câu
  đang nói. Độ dài cảnh đi theo độ dài câu, nên cảnh có ngắn có dài. Không chia đều
  theo một nhịp cố định.
- **Câu dài thì chia cảnh:**
  - câu dưới khoảng 5 s: 1 cảnh;
  - câu 5–10 s: 2 cảnh;
  - câu trên 10 s: 3 cảnh. Câu dài hơn nữa thì tiếp tục chia để mỗi cảnh thường
    3–5 s.
- **Chỗ chia trong một câu** đặt ở chỗ đổi ý, ngắt vế hoặc đổi động tác trên hình.
  Ví dụ từ "<lời thoại>" sang "<lời thoại>". Không cắt giữa một cụm từ.
- **Một cảnh không dài quá 10 s.** `validate` chặn cảnh trên 10 s. Ngoại lệ có chủ ý
  (nghệ nhân làm việc liền mạch, kiểu `long-take-bazin` trong từ điển) phải ghi lý do
  vào trường `long_ok`. Cảnh 8–10 s phải có chuyển động bên trong khung, nếu không
  hình sẽ chết trong khi thoại vẫn chạy; `validate` cảnh báo.
- **Sàn thực dụng 1.0 s.** Ngắn hơn là chớp, phải có lý do rõ (montage nhịp, xem
  "Chuyển động và xử lý").
- Mốc đối chiếu cũ vẫn đúng hướng: trên Product C, V1 45 clip / 178.21 s, trung bình gần 4 s
  một cảnh; Product A trung vị 3.5 s, đoạn nói dồn 1.2–2.5 s, đoạn giải thích 3–5 s.

## Kiểu cắt: tự phân tích từng chỗ, không áp một kiểu cho cả bài (Oxi, 11/11/2026)

Anh dặn: *"làm kiểu ngẫu hứng, có đoạn cần J/L, có đoạn cần đặt đúng, em tự phân tích
rồi làm"*. Điểm cắt hình chọn theo ngữ cảnh của từng chỗ. Dùng các kiểu trong
`oxi-visual-style/references/tu-dien-visual-art.md` mục "Dựng, nhịp và chuyển cảnh":

| Kiểu (`cut`) | Khi nào dùng |
|---|---|
| `hard` cắt thẳng đúng đầu câu | Câu mở ý mới, nêu số liệu hay tên riêng cần nhấn, sang chương ("<lời thoại>"), câu hook |
| `j` hình vào sớm 0.3–0.8 s | Ý nối tiếp mạch kể; cho người xem thấy thứ sắp được nói tới trước khi nghe tên nó |
| `l` hình kéo quá biên câu | Câu sau vẫn cùng ý, hoặc cần thêm nhịp cho hình thở |
| `action` cắt theo động tác | Đang có động tác trên hình (tay nghệ nhân, con rối chuyển động): cắt giữa động tác |
| `match` cắt khớp hình | Hai cảnh có hình khối, động tác hay màu giống nhau, nối ý hai đoạn |
| `beat` theo phách nhạc | Montage, intro có nhạc; với thoại thì ưu tiên ý trước phách |
| `montage` chuỗi ngắn | Đoạn liệt kê, nói dồn (danh sách dài): 1–2.5 s mỗi cảnh |

Ghi kiểu đã chọn vào trường `cut` và lý do ngắn vào `why` của mỗi clip. Luôn đổi tiết
tấu (`edit-rhythm`): dài–ngắn xen nhau, đổi nhịp khi sang chương.

Cả hai thái cực đều là lỗi:

- mọi cảnh bắt đầu đúng biên câu: bản dựng kiểu trình chiếu;
- mọi cảnh đều lệch sớm như nhau: cũng là áp một công thức, chỉ là công thức khác.

`validate` cảnh báo khi toàn bộ cảnh (từ 6 cảnh trở lên) cùng một kiểu điểm vào, hoặc
khi clip thiếu trường `cut`.

## Coverage — chỉ tiêu định lượng

Hai loại khoảng, đối xử khác nhau:

- **V1 hở** — không có MC trên hình. Bắt buộc phải có hình. Còn hở sau khi chạy là
  bản dựng lỗi, không phải bản dựng gọn.
- **V1 có MC** — được phép cutaway, không bắt buộc. Đây là chỗ đưa `evidence` và
  `reveal` vào.

Mốc để đối chiếu, không phải chỉ tiêu cứng: trên `ProductC_5-6PHUT` MC trên hình khoảng
55% thời lượng, tức B-roll gánh gần 45%. Một bản dựng ra 10% B-roll thì hoặc thư
viện thiếu thật, hoặc bước khớp cảnh đã bỏ sót — kiểm lại trước khi giao.

Mốc của thể loại khác, để thấy review KOL của anh nằm đâu (default, từ repo
`ghost-editor`, 10/11/2026): reel talking head ngắn của họ giữ mặt người nói trên
hình ít nhất 65%, B-roll full màn hình tối đa 25%, tối đa 3 lần chèn mỗi phút. Đo
trên 6 reel top họ chọn: 113/119 điểm chuyển là cắt thẳng, shot trung vị khoảng
3 giây, B-roll 20–35% thời lượng. Không áp các số này cho review sản phẩm; chúng
chỉ hợp khi anh giao reel nói chuyện thuần, không có cảnh demo.

### MC liếc mắt — giữ hay che (default, từ `ghost-editor`)

Liếc là một phần của nói chuyện. Chớp mắt, liếc nhanh, gật nhẹ để nguyên trên
hình, không phải lý do đặt B-roll. Chỉ coi là chỗ cần che khi mắt rời ống kính
(hoặc nhắm) quá khoảng 0.5 giây, hoặc đầu quay/cúi quá khoảng 12°. Che bằng cách rẻ
nhất trước: cắt bớt đoạn đó ở chặng thoại → phóng vào cảnh MC (mục "Chuyển động và
xử lý") → giữ cảnh B-roll đang chạy thêm chút → cảnh B-roll mới. Bài học của repo:
một reel che hết 31 chỗ bị gắn cờ, 29 chỗ chỉ là nháy 0.03–0.4 giây, và người nói
chỉ còn trên hình 33%. Chỗ V1 hở vẫn theo luật bắt buộc có hình ở trên.

## Chuỗi liền — không để MC chen giữa hai cảnh trám

Oxi nhận xét bản đổ B-roll đầu tiên của Product A (2026-09-28): *"vẫn bị những khoảng
hở của cảnh broll"*. Ảnh anh chụp là một khoảng ~1 giây mặt MC lộ ra giữa hai cảnh
trám. Timeline không hở, nhưng mắt người xem thấy một cú chớp mặt MC — đó là "hở".

Số đo từ bản Oxi tự dựng cùng job (đọc từ `.prproj` của anh, 5:17):

- MC nói trực diện (file quay nói) chỉ lộ mặt **~17%** thời lượng; bản trợ lý đầu tiên ~40%.
- Trám chạy thành chuỗi liền: 74 cảnh nhìn thấy, trung vị 3.5s; chỉ 2 cảnh dưới 1s.
- Đoạn nói dồn (liệt kê, số liệu) cắt 1.2–2.5s một cảnh; đoạn giải thích dài 3–5s.
- MC nói trực diện được giữ ở chỗ có chất riêng: câu hỏi hook, ý kiến cá nhân, uy tín,
  câu đùa, lời khuyên mua. Cảnh MC nói **tại hiện trường bài test** là hình hành động,
  không tính là "chớp mặt".

Luật: sau khi lên plan, quét mọi khoảng MC nói trực diện lộ ra giữa hai cảnh trám; dưới
**2 giây** thì kéo dài cảnh trám hai bên cho liền, đừng để chớp. Câu mở đầu video là
ngoại lệ có chủ ý.

Sau khi đặt, quét **lỗ vi mô** trên V2: đặt theo giây rồi Premiere làm tròn frame để lại
khe 1–7 frame giữa hai cảnh (10 lỗ trên 92 cảnh ở job Product A). Trong khoảng V1 trống thì
lộ màn đen; kéo `end`/`outPoint` cảnh trước cho khít rồi đọc lại.

## Chuyển động và xử lý trên từng cảnh (Oxi, 26/10/2026, so bản KAIYO)

Số đo từ bản Oxi dựng xong của KAIYO, đọc chỉ xem:

- **Đa số cảnh B-roll có keyframe Scale đẩy vào chậm** (push-in nhẹ suốt cảnh); một số
  cảnh thêm Bokeh Blur. Cảnh đứng im hoàn toàn là ngoại lệ, không phải mặc định.
- **Asset AI giải thích** (video tạo bằng AI để minh họa cơ chế): mở bằng khung hình đầu
  dạng ảnh tĩnh (PNG) kèm nhãn chữ khoảng 1-2.5 giây, rồi mới chạy video động.
- **Cảnh MC nói có thể dùng làm B-roll** khi phóng lên khoảng 150-180% vào tay, sản phẩm
  hay chi tiết đang được nói tới.
- **Montage theo nhịp**: đoạn liệt kê hay khoe nhanh cắt khoảng 1 giây một cảnh, được
  chồng lớp V2/V3. Đây là ngoại lệ có chủ ý so với sàn 1.0 giây ở mục Độ dài, không
  phải cớ để chớp ở chỗ khác.
- **Lumetri riêng từng clip là tùy cảnh, không mặc định.** Ở KAIYO B-roll hơi lệch sáng
  so với cảnh người nói nên Oxi chỉnh riêng từng clip. Chặng này không chỉnh màu (xem
  `SKILL.md`, "Skill này không làm"); chỉ ghi cảnh nào lệch sáng/màu so với A-roll vào
  báo cáo để chặng màu xử lý theo
  `oxi-premiere-workflow/references/color-grading.md`, Working rules mục 6.

Số liệu từ một job; dùng làm mốc đối chiếu, không phải chỉ tiêu.

## Thứ tự thao tác

Đặt theo thứ tự thời gian trên timeline, từ đầu về cuối. Không phải vì API đòi, mà vì
luật "không quay lại khoảnh khắc cũ trong 20 giây" và luật cỡ cảnh đều so với clip **liền trước** —
đặt lộn xộn thì không kiểm được hai luật đó.

Trước mỗi lần đặt, xác nhận dải đích trên track đó đang trống. `pr_overwrite_to_timeline`
phá thứ nằm dưới, và nó không hỏi.

Chỉ đặt sau khi đã so cảnh với lời đọc và kế hoạch qua `validate --gapmap --manifest`
cùng `score --min 80` như bước 6 trong `SKILL.md`. Đổi source hoặc in/out thì kiểm lại.

Điểm vào trên source: lấy trong khoảng hành động đã xem; ưu tiên `best_in`–`best_out`
của các nhóm ảnh đi qua (manifest chặng 1)
khi có. Đó là đoạn đã được nhìn là đẹp nhất — lấy nét xong, lia đã dừng, không ai đi
qua khung. Ra ngoài khoảng đó thì `validate` cảnh báo; chỉ làm khi cảnh cần dài hơn
khoảng đẹp, và ghi lý do vào `why`.

Tham số bắt buộc mỗi lần đặt:

```
track_type   : "video"
track_index  : 1 (V2) hoặc 2 (V3)      # 0-based, V1 là 0
in_seconds   : điểm vào trên source
out_seconds  : điểm ra trên source
start_seconds: vị trí trên timeline
drop_audio   : true
```

`drop_audio: true` không phải tùy chọn. B-roll mang audio hiện trường theo; để nguyên
là chồng tiếng gió, tiếng máy, tiếng người nói chuyện lên bed thoại Oxi vừa dựng
sạch. Lỗi này không nhìn thấy trên timeline, chỉ nghe thấy.

## Nghiệm thu

Đọc lại bằng một truy vấn **mới**, không tin giá trị trả về của từng lệnh đặt — luật
mutation verification ở `oxi-premiere-workflow/references/premiere-mcp.md` áp dụng
nguyên vẹn.

Ba điều phải đúng:

1. V1 — số clip và thời điểm kết thúc y hệt trước khi chạy.
2. A1 và audio có sẵn — y hệt, không tạo lỗ mới. Khoảng A1 không thoại đã được Oxi
   dành cho nghe thử/test giữ nguyên theo `SKILL.md`, Bước 1; không co để đạt
   điều kiện liền mạch của spine thoại thông thường.
3. Không khoảng V1 hở nào còn trống, và không clip nào vượt quá độ dài source.

V1 lệch một clip nghĩa là đã có một lệnh insert lọt vào và timeline đã ripple. **Hoàn
tác, đừng vá.** Vá một timeline đã trôi là cách biến một lỗi thấy được thành một lỗi
không thấy được.

Đạt cả ba thì lưu ngay, không hỏi — auto-save thường trực từ 2026-08-20. Chưa đạt thì
không lưu.

## Báo cáo cho Oxi

Nói đúng những con số này, đừng nói "đã xong":

- số cảnh đặt, tách riêng V2 và V3
- coverage B-roll trước và sau, theo phần trăm timeline
- số khoảng V1 hở đã lấp / tổng số
- chỗ nào còn trống và cần ý hình gì
- cảnh nào lệch sáng/màu rõ so với cảnh người nói (để chặng màu chỉnh riêng)
- V1/A1 trước và sau, để chứng minh spine không bị đụng
- đã lưu chưa

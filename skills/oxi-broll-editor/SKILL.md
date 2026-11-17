---
name: oxi-broll-editor
description: Chặng đổ B-roll cho một sequence Premiere đã dựng xong và được Oxi duyệt — đọc timeline live, xem kỹ footage, đối chiếu kịch bản/lời đọc và chọn cảnh trước khi đặt lên V2/V3, giữ V1/A1. Dùng khi Oxi nói đổ b-roll, chèn b-roll, ghép b-roll, thêm cảnh phụ, đắp hình, lấp hình, cutaway, chèn hình minh họa, phủ hình lên thoại, dựng hình lên V2, tìm ảnh/video trên mạng cho chỗ không quay được, hoặc bảo bản dựng thoại xong rồi giờ làm hình — kể cả khi anh không gọi tên "b-roll". Chạy lại sau mỗi lần Oxi sửa cut. Không cắt thoại, không đổi thời lượng — phần đó là oxi-premiere-workflow.
---

# OXI B-roll Editor — chặng đổ hình

Vị trí trong dây chuyền:

```
oxi-script-craft / oxi-explore-vlog        (hợp đồng nội dung)
            │
            ▼
oxi-premiere-workflow                      (cắt thoại → spine A1 + V1)
            │
            ▼
      OXI SỬA TAY  ← cắt lại, rút thời lượng, chốt độ dài
            │
            ▼
      THIS SKILL   ──►  broll_plan.json  +  clip trên V2/V3
            │
            ▼
      OXI SỬA TAY
            │
            ▼
oxi-text-graphics                          (chữ nổi bật trên V6–V9)
            │
            ▼
      OXI SỬA TAY
            │
            ▼
oxi-premiere-workflow / effects            (hiệu ứng/element → Oxi duyệt)
            │
            ▼
oxi-premiere-workflow                      (sub, màu, nhạc, transition, QC cuối;
                                            xong phần nào anh kiểm phần đó)
```

**(Oxi chốt 2026-10-01) Xong chặng này thì dừng.** Lưu project, báo kết quả kèm bằng
chứng, chờ anh xem/sửa B-roll; không làm tiếp text trong cùng lượt. Quy tắc chặng
nằm ở `oxi-agent-brief/references/video-editing.md` mục 4.

Skill này tồn tại vì một lý do kỹ thuật, không phải vì tiện tay chia nhỏ: **sau khi
Oxi sửa cut, mọi file plan của chặng trước đều hết hạn.** `cut_plan.json` mô tả một
timeline không còn tồn tại. Nên chặng này không được nhận plan cũ làm đầu vào — nó
phải đọc sequence đang mở và dựng lại bản đồ từ đầu, mỗi lần chạy.

## Hai thứ skill này bảo vệ

1. **V1 và A1 là bất khả xâm phạm.** Oxi đã duyệt chúng. Sau khi skill chạy, số clip
   và thời điểm kết thúc của V1 và A1 phải y hệt lúc trước. Đây là điều kiện nghiệm
   thu, không phải lời hứa.
2. **B-roll phải lấp đủ, không phải rắc cho đẹp.** Trên `ProductC_5-6PHUT` (ghi nhận
   2026-08-27) A1 chạy 89 clip liền mạch 323.29s trong khi V1 chỉ 45 clip / 178.21s
   với 6 lỗ — MC trên hình khoảng 55% thời lượng. Gần một nửa timeline là B-roll.
   Một bản "chèn vài miếng minh họa" là bản thiếu hình, không phải bản gọn.

## Track map — không chép, đọc từ nhà chính

Layout track của Oxi nằm ở `oxi-premiere-workflow/references/finishing-layout.md`.
**Đọc file đó, đừng chép bảng sang đây.** Hai bản track map lệch nhau là loại lỗi
không ai thấy cho tới lúc dựng hỏng, và kho này có luật một sự thật một nhà
((internal note, not published)).

Phần skill này được phép chạm: **V2** (B-roll chính — sản phẩm, chi tiết, demo) và
**V3** (B-roll phụ, nested, reference). Mọi track khác là của chặng khác.

Chỉ số track trong API là **0-based**: V1 = `track_index: 0`, V2 = `1`, V3 = `2`.
Nhầm chỗ này là đè thẳng lên mặt MC.

## Mandatory preflight

1. Chạy `scripts/verify_current.py` nếu `Skills/_versions/oxi-broll-editor/CURRENT.json`
   tồn tại. Chỉ đi tiếp khi `validated-match`.
2. Báo `Đã nạp workflow: oxi-broll-editor/<route>` trước thao tác đầu tiên.
   Bắt đầu bằng `oxi-agent-brief` để nắm đầu ra, phạm vi và trạng thái job. Dùng
   brief/câu trả lời đã chốt, chỉ cập nhật thay đổi; anh giao từ chặng B-roll thì
   giữ thoại đã khóa, không bắt quay lại chặng đầu hoặc duyệt lại.
3. Đọc `oxi-premiere-workflow/references/finishing-layout.md` (track map, luật J/L
   cut, coverage) và `references/premiere-mcp.md` (luật mutation verification, bẫy
   node ID per-session). Skill này không lặp lại chúng.
3a. Đọc mục B-roll trong hồ sơ dạng video của job (`<job>/video-type.md`, dòng
   "Hồ sơ" → `oxi-premiere-workflow/references/video-profiles/`): mật độ, nhịp, chuyển
   động và số đo từ bản Oxi của dạng đó. Không có hồ sơ thì ghi rõ trong báo cáo.
3b. Đọc `<job>/style_card.json`, hướng `chot`: trường `broll`, `bo_cuc` và các
   `terms` nhóm máy quay (`oxi-visual-style/references/style-card.md` mục 5).
   Thuật ngữ tra trong `oxi-visual-style/references/tu-dien-visual-art.md` mục
   `#03-bo-cuc`, `#04-may-quay`, `#10-dung-nhip`. `chot` còn trống thì hỏi một
   câu chọn hướng trước khi đổ. Hướng có `phong_cach_dung` thì đọc mục B-roll
   trong `oxi-visual-style/references/editing-styles/<slug>.md` của xương sống
   và gia vị (vd hình chèn theo từ khóa, split, speed ramp); gia vị chỉ dùng ở
   chỗ ghi trong `cho_dung`. Speed ramp cần ngoại lệ vì `validate` chặn đổi tốc độ.
4. Kiểm tra live: Premiere mở chưa, project nào, sequence active nào, bin B-roll tên
   gì. Ghi chú đã đồng bộ không phải bằng chứng.
5. Hỏi **một** câu nếu chưa rõ tên bin B-roll: *B-roll của job này anh để bin nào?*

## Connector — tên tool `pr_*` trong skill này là của Higgsfield

Connector chính là **MCP Bridge** (`premiere-pro-mcp`; Oxi chốt 05/11/2026, xác nhận
lại 15/11/2026). Luật chọn connector chỉ nằm ở `oxi-premiere-workflow/SKILL.md`, mục
"Current Premiere connector"; đọc ở đó, skill này không lặp lại.

Các tên `pr_*` bên dưới (`pr_overwrite_to_timeline`, `pr_add_to_timeline`,
`pr_ensure_tracks`, `pr_get_active_sequence`) là tool của **Higgsfield**, viết từ lúc
Higgsfield là connector duy nhất. Chỉ dùng nguyên văn khi Oxi chọn Higgsfield cho job.
Trên MCP Bridge, lấy tên và tham số tool từ `get_capabilities` của bản đang cài.
**Chưa có bảng đối chiếu tên tool đã kiểm** (ghi nhận 15/11/2026), và các máy có thể
cài bản `premiere-pro-mcp` khác nhau với bộ tool khác nhau: kiểm bản đang cài, đừng
đoán tên từ skill này.

Connector nào cũng phải giữ đúng bốn điều sau, và phải chứng minh trên **một** clip ở
sequence nhân bản trước khi chạy cả lô:

1. Lệnh đặt là **overwrite**, không insert hay ripple: sau lệnh, V1 và A1 giữ nguyên
   số clip và điểm kết thúc.
2. **Không có audio của B-roll** rơi xuống audio track nào. Higgsfield có
   `drop_audio: true`. Trên MCP Bridge, đặt clip lên V2 từng đẩy audio kèm xuống A2
   (`oxi-premiere-workflow/references/premiere-mcp.md`, bẫy 2026-09-28): tool không có
   tham số bỏ audio thì gỡ đúng phần audio vừa sinh ra, rồi kiểm A1 từng clip.
3. Track đích đúng chỉ số 0-based và dải đích đang trống trước khi đặt.
4. Đọc lại timeline bằng một truy vấn mới sau mỗi lô; không tin giá trị trả về của
   lệnh đặt.

Một lệnh chưa rõ kết quả thì không chạy lại qua connector khác
(`oxi-premiere-workflow/SKILL.md`).

## Bẫy chết người — đọc trước khi đặt bất cứ thứ gì

`pr_add_to_timeline` **insert và ripple**. Dùng nó để đổ B-roll sẽ đẩy toàn bộ nội
dung phía sau trên timeline, làm V1 và A1 trôi khỏi chỗ Oxi đã duyệt. Triệu chứng
xuất hiện muộn: bản dựng vẫn "chạy được", chỉ là hình và tiếng lệch dần về cuối.

Dùng `pr_overwrite_to_timeline`, luôn luôn, với:

- `track_type: "video"`, `track_index: 1` (V2) hoặc `2` (V3)
- `in_seconds` / `out_seconds` — điểm vào/ra trên **source**
- `start_seconds` — vị trí trên timeline
- `drop_audio: true` — B-roll mang audio hiện trường theo; để nguyên là chồng lên
  bed thoại đã dựng

Overwrite phá thứ nằm dưới nó ở đúng dải đó. Nên trước mỗi lần đặt, xác nhận dải đó
trên track đích đang trống bằng `pr_get_active_sequence`. Muốn chồng lớp thì **lên
track cao hơn** (`pr_ensure_tracks`), không bao giờ ghi đè để giải quyết va chạm.

## Quy trình

**Thứ tự bù hình khi thiếu:** footage job → OXI Assets (Ba kho) → research web →
B-roll dựng bằng code. Chỉ đi bước sau khi bước trước không đạt, ghi lý do.

**Research hình ngoài (Oxi, 11/11/2026):** chỗ không quay được thì tìm và kiểm
chứng ảnh/video trên web, đọc trọn [references/web-research.md](references/web-research.md).
Được dùng cả nguồn chưa rõ quyền nhưng phải ghi nguồn và nhãn quyền; **dừng cho Oxi
duyệt danh sách trước khi tải**, rồi đưa qua bin riêng, manifest và validator như
nguồn khác.

**B-roll thiếu footage (Oxi, 27/10/2026):** sau khi đọc hết nguồn và so ứng viên,
được đề xuất B-roll dựng bằng HyperFrames/Remotion. Đọc trọn
[references/generated-broll.md](references/generated-broll.md): làm storyboard
có hình, **dừng cho Oxi duyệt trước khi sản xuất**, rồi render, kiểm và đưa lại
qua manifest/validator hiện có. Cảnh B-roll dựng mới vẫn thuộc chặng này, không
đợi tới chặng element sau Text. Render từ storyboard đã duyệt là một nhánh bổ
sung có giới hạn; nhánh tài nguyên thư viện nằm ở mục Ba kho ngay dưới đây.

**Ba kho (Oxi duyệt 05/11/2026):** đọc
[quy trình thư viện chung](../oxi-premiere-workflow/references/assets.md) khi
chọn ý hình, kỹ thuật hoặc tài nguyên bổ sung. Dùng kiến thức bố cục/nhịp,
kỹ thuật B-roll và Assets theo vai trò câu thoại; giữ nguồn job làm đầu vào chính.
Ảnh/footage/cutout từ thư viện chỉ bổ sung trong phạm vi job sau khi đã xét hết
nguồn, import vào bin riêng và qua cùng manifest/kiểm hình/validator như nguồn
khác. Quy tắc nguồn bin dưới đây có thêm ngoại lệ giới hạn này; không tự dùng
footage job khác. SFX/overlay chỉ thực hiện khi thuộc phạm vi chặng được giao.

### Bước 1 — Dựng bản đồ lỗ từ timeline live

Đây là thứ thay cho plan đã hết hạn.

```
pr_get_active_sequence   →  lưu ra sequence.json
python scripts/broll_plan.py gapmap sequence.json --out gapmap.json
```

`gapmap` trả về: các khoảng V1 hở (bắt buộc phải có hình), các khoảng V1 có MC
(được phép cutaway nhưng không bắt buộc), độ phủ B-roll hiện có trên V2/V3, và tổng
thời lượng. Nếu A1 có lỗ, script báo lỗi và dừng để kiểm nguyên nhân.
**(Oxi duyệt, 29/10/2026)** Khoảng test/nghe thử anh đã dành có thể không có thoại
A1; kiểm mọi track audio và lời anh đã chốt trước khi coi đó là spine thiếu.
Giữ nguyên khoảng này; luật nội dung âm thanh nằm ở
`../oxi-premiere-workflow/references/music.md`, "Protect listening tests".
Nếu công cụ chưa biểu diễn được khoảng có chủ ý, ghi rõ giới hạn/ngoại lệ của job;
không co timeline, thêm thoại giả hay sửa đầu vào để báo validator pass.

### Bước 2 — Lời thoại của bản dựng hiện tại

Cần lời thoại **của timeline đang mở**, không phải kịch bản gốc và không phải bản chép
lời của source thô. Sau khi Oxi cắt tay, hai thứ đó lệch timecode hoàn toàn — mà lệch
timecode thì mọi chỗ trám hình sẽ đặt sai chỗ.

Đầu ra mốc **anh xem/sửa/chốt thoại** là timeline live của lần chốt cuối.
Từ bản đó xuất `edited.wav`, chép thành text có timecode, rồi tạo `lines.json`.
Chỉ dùng lại audio/transcript khi đã xác minh nó thuộc đúng bản cut hiện tại.
Anh sửa thoại sau đó thì xuất/chép lại và lập lại bản đồ lỗ trước khi đặt hình.

```
pr_extract_audio(...)            →  edited.wav   (xuất từ sequence đang mở)
whisper edited.wav --model turbo --language vi --task transcribe --word_timestamps True --output_format json
python scripts/broll_plan.py lines gapmap.json --transcript edited.json --out lines.json
```

Whisper chạy theo đúng cấu hình đã duyệt trong route `Subtitle / SRT` của
your workflow index — không tự đổi model hay ngôn ngữ.

`lines` ghép từng câu thoại vào từng khoảng V1 hở, và chặn hai lỗi:

- **Transcript lệch quá 1 giây so với A1** → dừng, exit 1. Gần như luôn có nghĩa là đã
  chép lời nhầm file source gốc thay vì bản dựng. Xuất lại rồi chép lại.
- **Khoảng hở không có câu thoại nào phủ lên** → cảnh báo. Kiểm tiếng test, hành động
  trên hình và chỉ đạo đã có: đoạn nghe thử có chủ ý dùng hình đúng bài test,
  không tự coi là khoảng lặng. Chỉ hỏi Oxi khi ý hình vẫn chưa xác định được.

`lines` đọc được cả JSON của Whisper lẫn file SRT.

### Bước 3 — Đọc bin B-roll của job

Nguồn chính là **bin trong project** do Oxi đã lọc; không quét ổ đĩa. Nguồn bổ sung
từ OXI Assets theo mục Ba kho, hình research đã duyệt (`BROLL_RESEARCH`) và render
storyboard đã duyệt phải vào bin riêng,
được index/nhìn/kiểm trước khi chọn; không tự thêm nguồn ngoài các nhánh này.

```
pr_list_project_items(bin_path: "<tên bin Oxi đưa>")
```

Khớp mỗi item bằng **đường dẫn media**, không bằng node ID. Node ID là per-session:
ID của phiên trước ở phiên này trỏ sang thứ khác hoặc trỏ vào hư không
(`premiere-mcp.md`). Lưu cả `name` và `media_path` vào manifest để phiên sau resolve
lại được.

Footage của job đã được **đọc toàn bộ ở chặng 1**: `<job>/index/manifest.json`
do `oxi-premiere-workflow/scripts/segment_sheets.py` dựng, mỗi segment có mô tả,
`look` (khung đẹp tới đâu), `best_in`/`best_out` (khoảng đẹp nhất) và `roles`. Chặng
này **dùng lại** manifest đó và xem kỹ các ứng viên theo câu thoại hiện tại trước
khi đặt hình. Chạy đúng lệnh của chặng 1 trên
bin B-roll và cùng thư mục `index/`:

```
python ../oxi-premiere-workflow/scripts/segment_sheets.py --from-bin bin_items.json --out <job>/index
```

File đã có với cùng cấu hình lấy mẫu được giữ nguyên; chỉ file mới hoặc cấu hình
đã đổi được index. Rồi mở sheet của
**các file mới và các nhóm đã đổi ranh giới** rồi điền như chặng 1. Script in ra `not_looked`: danh sách đó
phải **rỗng trên toàn manifest** trước khi sang bước 4. `validate` chặn **cả plan** khi manifest còn
segment chưa nhìn, kể cả segment không được chọn: chọn cảnh trên phần đã nhìn là bỏ sót phần chưa nhìn.
(Product D, 2026-10-21: plan chọn trên 82/1321 segment, 44/59 file chưa ai mở, vẫn pass vì
cổng cũ chỉ kiểm segment được chọn.)

Nhìn chưa hết mà hết phiên/hết token thì ghi số đã nhìn (vd `82/1321 segment, 15/59 file`) và file
nào còn lại vào file tiến độ của job (`QUY-TAC-CHUNG-AI.md`, mục "Việc dài và bàn giao"). AI nối việc
nhìn tiếp từ đó, không sang bước 4.

Không có manifest của chặng 1 (job cũ, hoặc chặng 1 bị bỏ qua) thì lệnh trên dựng
từ đầu và chặng này phải nhìn hết; ghi rõ điều đó trong báo cáo.

`validate` không chạy được khi thiếu manifest: plan không khai `manifest` và không có
`--manifest` thì bị chặn, clip thiếu `segment_id` cũng bị chặn. Segment có `look` mà
`description` rỗng và không `uncertain: true` bị coi là chưa nhìn thật (điền số mà
không đọc sheet). Nhiều segment chung một `description` thì có cảnh báo điền hàng loạt.
(Oxi chốt 2026-10-22.)

Bảng trường, thang `look`, bảng ảnh 2 giây × 3 frame, xem thêm 1 giây × 3 frame ở
chỗ đổi động tác và `action_map.json`: đọc trọn
`oxi-premiere-workflow/references/footage-index.md`. Nhóm ảnh là đơn vị quan sát;
một cảnh được chọn có thể đi qua nhiều nhóm. Không đoán diễn biến tiếp theo từ ba ảnh.

### Bước 4 — Ý hình cho từng chỗ trống

Đầu vào là `lines.json` của bước 2, Script Map nếu có, manifest và bản đồ hành động
của bước 3. Lọc sơ bằng `roles`,
`ideas`, `description` và `look` trong manifest — đây là việc đọc bảng, chưa cần mở
ảnh.

Với mỗi khoảng cần hình: câu thoại phủ lên nó nói gì, và hình cần làm **vai trò** gì
— minh họa, đưa bằng chứng, cho thấy hậu quả, tạo tương phản, hay xác lập bối cảnh.
Vai trò quan trọng hơn từ khóa. Chi tiết: `references/matching.md`.

Đường nối bắt buộc: **timeline anh chốt → audio → text/timecode hiện tại →
đối chiếu manifest + action_map của chặng đọc toàn bộ source → so/chọn cảnh →
kiểm plan → đặt B-roll**. Text xác định ý và vị trí cần hình trên timeline;
manifest/action_map xác định đoạn source nào thực sự cho thấy ý đó. Hai hệ
timecode khác nhau: không lấy giây trong source làm giây trên timeline.

### Bước 5 — Chọn: ràng buộc cứng trước, điểm sau

Ràng buộc cứng loại thẳng, không cộng trừ điểm:

- khoảng hành động liên tục đã xem phải đủ dài cho chỗ cần lấp và tay cầm hai đầu;
  không ép cảnh vào giới hạn của một nhóm ảnh 2 giây
- không quay lại một khoảnh khắc đã dùng của cùng source trong vòng 20 giây (cắt tiếp về phía sau trong cùng take là chuỗi cắt nhảy, được phép)
- không ba lần liên tiếp cùng một cỡ cảnh (một chuỗi cắt tiếp trong cùng take tính là một cảnh)

Rồi với **mỗi chỗ trống, so 2–3 ứng viên nếu có và mở ảnh lớn** trước khi chốt:

```
python ../oxi-premiere-workflow/scripts/segment_sheets.py --out <job>/index --detail C9705-03 C9719-01 C9731-02
```

`validate` chặn clip nào có `segment_id` mà chưa có `index/detail/<segment_id>.jpg`.
Đọc từng `index/detail/<id>.jpg` bằng Read tool, đặt cạnh câu thoại, và hỏi đúng một
câu: *khung này có làm đúng vai trò câu thoại cần không?* Chọn cảnh làm được việc đó
và đẹp nhất; ghi lý do so sánh vào `why`. Sheet nhỏ đủ để lọc, không đủ để chốt —
đây là chỗ bắt được một cảnh đúng nội dung nhưng lệch nét, cháy sáng hoặc lọt tay
người. Với cảnh động, đọc nhóm ảnh 1 giây quanh chỗ đổi động tác rồi xem video của
đúng đoạn định dùng để chốt in/out, hướng chuyển động và nhịp nối. Nghe lời đọc
đang phủ lên cảnh; khớp cả hành động, ý câu và hình trước/sau, không chỉ tên đồ vật.
Ghi đoạn source, câu thoại, bằng chứng đã xem, điểm đẹp/xấu, trạng thái kiểm tra
chuyển động và lý do chọn hơn ứng viên khác vào plan. Thiếu ứng viên thì ghi rõ.
Mẫu bản đồ hành động: `examples/action-map-example.json`; các trường `review`
và `candidate_comparison` trong `examples/broll-plan-example.json` phải được điền
bằng bằng chứng thật cho từng clip, không giữ placeholder.
Không đặt cảnh còn nghi ngờ về nội dung hoặc chuyển động cần thiết cho mạch nối.

Còn lại mới chấm điểm. Thang điểm và lý do từng trọng số:
`references/matching.md`. Điểm `quality` không được cao hơn `look` đã ghi trong
manifest quá 0.15 — `validate` chặn.

Lý do tách hai tầng: một clip vi phạm ràng buộc không phải là clip "điểm thấp", nó
là clip sai. Trộn chúng vào một thang điểm sẽ có lúc một clip lặp nhưng hợp nội dung
thắng điểm và lọt vào bản dựng.

### Bước 6 — Kiểm kế hoạch trước, rồi đặt lên V2/V3

**Đặt theo câu thoại (Oxi, 11/11/2026):** mỗi câu, hoặc mỗi vế của câu dài, là một ý hình, nên cảnh có ngắn có dài. Câu dài quá 5–10 s thì chia 2–3 cảnh ở chỗ đổi ý. Một cảnh không quá 10 s; `validate` chặn. Kiểu cắt tự phân tích từng chỗ: cắt thẳng đúng đầu câu, J/L, cắt theo động tác, cắt khớp hình hoặc montage. Không áp một kiểu cho cả bài.

Luật đặt, độ dài, kiểu cắt, và cách chia V2 với V3:
`references/placement.md`. Hình dạng `broll_plan.json`:
`examples/broll-plan-example.json`.

```
python scripts/broll_plan.py validate broll_plan.json --gapmap gapmap.json --manifest <job>/index/manifest.json
python scripts/broll_plan.py score broll_plan.json --min 80
```

Cả hai lệnh phải pass **trước lệnh sửa timeline đầu tiên**. Import render từ
storyboard đã duyệt để index theo `references/generated-broll.md` chưa phải là
đặt lên timeline và không được dùng để bỏ qua cổng này. Validator chặn cả plan khi
manifest còn segment chưa nhìn, chặn clip thiếu ảnh detail, và kiểm mọi nhóm
ảnh mà `source_in`–`source_out` đi qua, không chỉ `segment_id` đại diện. Kiểm bằng
mắt/nghe ở bước 5 vẫn bắt buộc: điểm số không chứng minh cảnh đúng câu thoại.
Thiếu hình phù hợp thì research hình ngoài theo `references/web-research.md`,
rồi storyboard B-roll dựng mới theo `references/generated-broll.md`, hoặc báo phần còn thiếu nếu không thể minh họa
đúng nội dung; chưa đổ plan đang blocked. Không render trước khi Oxi duyệt
storyboard và không nới hai cổng trên cho render dựng mới.

Đọc mới timeline để chắc spine và khoảng trống trên track đích vẫn đúng với plan.
Nếu Oxi vừa sửa cut, quay lại bước 1; nếu đổi ứng viên hoặc in/out, chạy gate lại.

```
pr_ensure_tracks(video_tracks: 3, audio_tracks: 4)
pr_overwrite_to_timeline(...)   # từng clip, theo broll_plan.json
```

### Bước 7 — Nghiệm thu rồi lưu

```
pr_get_active_sequence   # truy vấn mới sau khi đặt xong
```

Rồi đọc lại timeline bằng một truy vấn **mới** (`pr_get_active_sequence`), không tin
giá trị trả về của từng lệnh đặt, và kiểm ba điều:

1. V1: số clip và thời điểm kết thúc **y hệt** trước khi chạy. Lệch một clip nghĩa
   là đã ripple — hoàn tác, đừng vá.
2. A1 và audio có sẵn: y hệt; không tạo lỗ mới hoặc thay đổi các khoảng test có chủ ý.
3. Coverage B-roll đạt ngưỡng trong `gapmap.json`, không còn khoảng V1 hở nào trống.

Đạt cả ba thì lưu ngay. Oxi đã cấp phép auto-save thường trực từ 2026-08-20: không
hỏi, nhưng cũng không lưu một trạng thái mới đặt được nửa chừng.

## Chạy lại sau khi Oxi sửa cut

Đây là tình huống thường gặp nhất, không phải ngoại lệ: Oxi xem bản có hình, cắt bớt
thời lượng, rồi bảo đổ lại.

Premiere không có chỗ để skill đánh dấu "clip này của tôi". Nên sổ sách là
`broll_plan.json` của lần chạy trước:

- clip trên V2/V3 khớp `source` + `source_in` + `timeline_in` với plan cũ → **của
  skill**, được phép dọn và đặt lại
- clip không khớp → **Oxi kéo tay**, giữ nguyên và coi dải đó là đã có hình

Không có plan cũ thì hỏi trước khi dọn bất cứ thứ gì trên V2/V3. Xóa nhầm một cảnh
Oxi tự đặt là loại lỗi không hoàn tác được bằng một câu xin lỗi.

## Skill này không làm

- Không cắt thoại, không đổi thời lượng, không chạm V1/A1 → `oxi-premiere-workflow`
- Không làm chữ nổi bật → `oxi-text-graphics`
- Không màu, sub, nhạc, transition, adjustment layer → `oxi-premiere-workflow`
- Không quyết định nội dung giữ hay bỏ → `oxi-script-craft`, `oxi-explore-vlog`
- Không quét kho footage toàn cục. Chốt ngày 06/09/2026, sửa 30/09/2026: mỗi job một
  manifest, chặng 1 đọc toàn bộ, chặng này dùng lại rồi kiểm kỹ ứng viên theo lời
  đọc hiện tại. Index lại khi thêm file hoặc đổi cấu hình lấy mẫu. Dùng footage giữa các job khác nhau vẫn là một quyết định mới của Oxi,
  không phải mở rộng ngầm.

## Cập nhật skill

Theo đúng luật kho: quy tắc lõi vào file này, chi tiết vào **một** reference, code
lặp lại vào `scripts/` và phải chạy được. Xong thì chạy `quick_validate.py` của
skill-creator, `scripts/publish_version.py`, và yêu cầu `verify_current.py` trả
`validated-match`. Rồi mới báo xong.

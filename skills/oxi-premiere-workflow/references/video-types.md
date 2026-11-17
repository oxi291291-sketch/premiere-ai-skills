# Video type: identify before cutting

Oxi approved on 2026-09-30. He edits many genres, and the genre is decided
**after reading the script**, not from the words of the request. The
dialogue-spine process in `dialogue-editing.md` fits only videos where a
presenter talking is what drives the edit. Every editorial job therefore
produces a **type card** before any cut plan, and the card's editing axis picks
the route.

This file is the single home for genre and axis rules. Style words Oxi uses
(`cinematic`, `nhịp nhanh`, `hấp dẫn`) are translated in
`oxi-agent-brief/references/video-editing.md` section 3; do not repeat them here.

## When

1. `oxi-agent-brief` takes intake only: sources, script version, deliverable.
2. `oxi-script-craft` reads the approved column and builds the Script Map.
   Draft the card from it.
3. Transcribe the source and index the footage (`footage-index.md`). These two
   steps are the same for every axis.
4. **Settle the card from the source**, together with the brief settled from the
   script and the Style Card (`oxi-visual-style`), in one report. Stop for Oxi
   to approve (Oxi, 2026-10-13), then plan the cut on the route below.

Without a script, draft the card from the brief and the source alone and say in
the report that the type was inferred without a content contract. When Oxi
names the genre, his word wins, but still check it against the script and the
source; if they disagree, say so with the evidence.

## The card

Write it to `<job>/video-type.md` and quote it at the top of the report.

| Field | Content |
|---|---|
| Nguồn việc | booking nhãn hàng · khách thuê dựng · kênh tự sản xuất |
| Thể loại | one main genre from the table below, plus a secondary one if the video mixes |
| Trục dựng | **thoại · lời bình · thao tác · nhạc**; one main axis, a secondary one if needed |
| Nền tảng, khung hình | e.g. TikTok 9:16, YouTube 16:9; from the script or brief |
| Căn cứ | what in the script and source proves the choices, e.g. "MC nói trước máy 90 % thời lượng", "không có lời, kịch bản ghi nhạc tham chiếu" |
| Chưa chắc | anything unresolved; ask one short question if it would change the axis |
| Hồ sơ | the matching profile in `video-profiles/` (Oxi, 2026-11-12), or "none" |

**Profile (Oxi, 2026-11-12).** Once the genre is set, open the matching file in
[video-profiles/](video-profiles/README.md): taste, density and Oxi's measured numbers
for that type. Every later stage (dialogue, B-roll, text, effects, music) reads its own
section of that profile alongside its skill. No profile for the genre: write "none" and
say so in the report.

`Booking` is a commercial arrangement, not a genre. A booking can be a review,
a vlog or a tutorial; its content contract is the Script Map, and the genre is
still read from the script.

To pick the axis, ask **what decides the order and the length of the shots**:

- **Thoại**: a presenter or subject speaking on camera. The spoken line sets
  the timing and the picture follows it.
- **Lời bình**: a separately recorded or scripted voiceover sets the timing and
  the picture illustrates it.
- **Thao tác**: the sequence of steps or actions sets the order, and speech
  only describes them.
- **Nhạc**: the music and its beat set the rhythm, and speech is absent or only
  accents.

## Routes by axis

| Axis | Route | Stage after Oxi's review |
|---|---|---|
| Thoại | `dialogue-editing.md` unchanged: clean full-content spine on A1 | `oxi-broll-editor` |
| Lời bình | If the VO exists, cut the VO as dialogue under `dialogue-editing.md` (take and level audits apply), then place picture by the VO lines. If it does not exist, stop and report: recording or TTS is Oxi's decision (voice, cost). | `oxi-broll-editor` over an empty or partial V1 (not yet tried on a real job) |
| Thao tác | Order the picture by the steps in the Script Map. Every step needs picture of the action and its result; never cut away the result of a step. Cut speech under `dialogue-editing.md` but keep the action sound (5d, Product A calibration). | `oxi-broll-editor` for cutaways only |
| Nhạc | Choose the music first (`music.md`), detect beats, cut picture to the rhythm. Picture from the footage index is the main track, not B-roll. | No approved workflow yet: say so, work from live state and deliver a review sequence |

## Genre defaults

`Status` separates rules calibrated on Oxi's real corrections from proposals
that still need a real job. A proposal is a starting point, not a rule; after
the first job of that genre, compare with Oxi's correction and update this row.

| Thể loại | Default axis | What changes in the cut | Acceptance check | Status |
|---|---|---|---|---|
| Review sản phẩm | Thoại | `dialogue-editing.md` as written: keep every feature, spec, reaction; the last complete take | Every feature spoken has picture proving it; CTA present | Calibrated on 5 product-review jobs |
| Vlog, trải nghiệm | Thoại, secondary thao tác | Follow the route travelled; keep real reactions and location sound; a pause while something happens is content, not dead air | The viewer can tell where the presenter is and why they went there | Proposal |
| Phóng sự, tài liệu | Lời bình or thoại nhân vật | The first pass is **soundbite selection** against the story, not keep-everything. Deliver the list of chosen quotes with timecodes for Oxi to check before assembly. | Every claim has evidence in picture or quote; a quote keeps its meaning | Proposal |
| Phỏng vấn | Thoại (người được hỏi) | Choose answers, not takes. Drop the interviewer's question when the answer stands alone. Multi-camera: sync first (`pr_sync_media` / multicam). | Every cut answer keeps its original meaning | Proposal |
| Tutorial, hướng dẫn | Thao tác | Steps in script order, no step skipped, each result shown | A viewer could repeat the steps from the video alone | Proposal |
| Montage, recap sự kiện, giới thiệu không lời | Nhạc | Shot length follows the beat and the action; the hook in the first seconds | Cuts land on the beat or on an action; no dead shot | Proposal |
| Tập travel series | Per its beat sheet | Content contract is `oxi-explore-vlog`'s Beat Sheet, not a booking Script Map | `beatsheet.py check --transcript` | See `oxi-explore-vlog` |
| Clip affiliate từ video dài | Thoại | Clip selection is `oxi-clip-affiliate`'s `clip_plan.json`; Premiere only cuts the chosen clips | Per that skill | See `oxi-clip-affiliate` |
| Khác | By the axis question | Write the genre as the script calls it; no default exists, so state that in the report | From the brief's acceptance | — |

## Meaning of a quote

Splicing words across takes to fix a fact or a brand name is allowed for Oxi's
presenters reading his script (Product A calibration in `dialogue-editing.md`). It
is **not** allowed for an interviewee or a documentary subject: joining words
from different answers can put a sentence in their mouth. For those genres, cut
only between complete phrases and check that each retained answer still means
what it meant in the source.

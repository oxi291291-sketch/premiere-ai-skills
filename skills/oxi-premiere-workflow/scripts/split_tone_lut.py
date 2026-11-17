"""Tao LUT look tach tong (toi ngả teal, sang ngả cam) de gan vao Look cua V5.

Vi sao co script nay (Oxi chon huong "neon dem, teal-orange nhe tay" ngay
2026-10-19, job Job L / VIDEO EXAMPLE_COLOR_REVIEW): tren Premiere 26.3.2
script khong chinh duoc Color Wheels, Shadow/Highlight Tint hay Curves cua
Lumetri (luu dang khoi nhi phan). Phan tach tong vi vay nam trong mot LUT .cube;
do tuong phan, den, Vibrance, vignette van chinh bang thanh so Lumetri.

LUT giu luma Rec.709 ma hoa truoc khi clip RGB; mau bi clip co the doi luma:
  - toi: day ve teal, het tac dung o luma `--top`, ve 0 duoi luma `--floor`
    (de den tuyet doi van den);
  - sang: day ve cam, tu luma 0.55 len.

Muc da thu cho canh trong nha toi (Job L), chua duoc Oxi duyet ket qua: --teal 0.12 --orange 0.015
--top 0.50 --floor 0.025, cung Basic tren V5: Contrast +6, Highlights -5,
Blacks 0, Vibrance +12, Vignette -0.6. Blacks -10 / Contrast +10 lam bet den
(5-6 % diem anh cham day): Basic chay TRUOC Look trong cung mot Lumetri.

    python split_tone_lut.py --teal 0.12 --orange 0.015 --top 0.50 --floor 0.025 --out X.cube
    python split_tone_lut.py --teal 0.12 --preview frame.png --save sim.png

Thu truoc tren khung xuat bang `pr_export_frames.py` (--preview), do bang
`color_scopes.py` (shadow_rg_bg / highlight_rg_bg), roi moi nap vao Premiere:
Lumetri > Creative > Look > Browse... (ten file khong co dong BMD_TITLE).
"""
import argparse

import numpy as np

TEAL = np.array([-1.0, 0.30, 0.60])
ORANGE = np.array([1.0, 0.20, -1.0])
W709 = np.array([0.2126, 0.7152, 0.0722])


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def grade(rgb, teal, orange, top=0.40, floor=0.06):
    """rgb: (...,3) gia tri 0-1 da ma hoa. Tra ve cung shape."""
    L = rgb @ W709
    w_sh = (1.0 - smooth(0.12, top, L)) * smooth(0.0, floor, L)
    w_hi = smooth(0.55, 0.95, L)
    out = rgb + (teal * w_sh)[..., None] * TEAL + (orange * w_hi)[..., None] * ORANGE
    out = out + (L - out @ W709)[..., None]        # giu nguyen do sang
    return np.clip(out, 0.0, 1.0)


def write_cube(path, teal, orange, top=0.40, floor=0.06, n=33):
    g = np.linspace(0.0, 1.0, n)
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write('TITLE "split tone teal %.3f orange %.3f top %.2f floor %.3f"\n' % (teal, orange, top, floor))
        fh.write("LUT_3D_SIZE %d\n" % n)
        for b in g:            # .cube: R chay nhanh nhat
            for gg in g:
                rows = np.stack([g, np.full(n, gg), np.full(n, b)], 1)
                for r, gr, bl in grade(rows, teal, orange, top, floor):
                    fh.write("%.6f %.6f %.6f\n" % (r, gr, bl))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--teal", type=float, default=0.06)
    ap.add_argument("--orange", type=float, default=0.02)
    ap.add_argument("--top", type=float, default=0.40, help="luma where the teal push has faded out")
    ap.add_argument("--floor", type=float, default=0.06, help="luma below which the push fades to 0 toward black")
    ap.add_argument("--out")
    ap.add_argument("--preview")
    ap.add_argument("--save")
    a = ap.parse_args()
    if not a.out and not a.preview:
        ap.error("pass --out and/or --preview")
    if a.out:
        write_cube(a.out, a.teal, a.orange, a.top, a.floor)
        print("wrote", ascii(a.out))
    if a.preview:
        from PIL import Image
        img = np.asarray(Image.open(a.preview).convert("RGB"), np.float32) / 255.0
        Image.fromarray((grade(img, a.teal, a.orange, a.top, a.floor) * 255 + 0.5).astype(np.uint8)).save(a.save)
        print("saved", ascii(a.save))


if __name__ == "__main__":
    main()

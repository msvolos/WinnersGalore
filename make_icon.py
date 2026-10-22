"""Draw the home-screen icon (a lucky gold horseshoe with a winner's star on turf
green) and render the PNG sizes phones need into docs/.

Run once, or again after changing the design: python make_icon.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")

CX, CY, R, TOP, W = 256, 268, 128, 128, 64  # horseshoe centerline and thickness


def star(cx, cy, r_out, r_in, points=5):
    pts = []
    for k in range(points * 2):
        r = r_out if k % 2 == 0 else r_in
        a = -math.pi / 2 + k * math.pi / points
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def nail_holes():
    """Six nail holes along the shoe's centerline, three per branch."""
    holes = []
    for side in (-1, 1):
        holes.append((CX + side * R, 196))
        for deg in (35, 72):  # down around the toe, measured from horizontal
            a = math.radians(deg)
            holes.append((CX + side * R * math.cos(a), CY + R * math.sin(a)))
    return holes


def svg():
    holes = "".join(
        f'<rect x="{x - 6:.1f}" y="{y - 11:.1f}" width="12" height="22" rx="6" fill="#3a2a05" opacity=".75" '
        f'transform="rotate({math.degrees(math.atan2(y - CY, x - CX)) - 90 if y > CY else 0:.1f} {x:.1f} {y:.1f})"/>'
        for x, y in nail_holes())
    shoe = f"M {CX - R} {TOP} L {CX - R} {CY} A {R} {R} 0 0 0 {CX + R} {CY} L {CX + R} {TOP}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <radialGradient id="turf" cx="50%" cy="38%" r="75%">
      <stop offset="0" stop-color="#2f7a5c"/>
      <stop offset="0.6" stop-color="#1f4e3d"/>
      <stop offset="1" stop-color="#0f2a20"/>
    </radialGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffe9a3"/>
      <stop offset="0.45" stop-color="#e5b53a"/>
      <stop offset="1" stop-color="#a8781a"/>
    </linearGradient>
    <linearGradient id="goldEdge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#c89325"/>
      <stop offset="1" stop-color="#6e4b0c"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" fill="url(#turf)"/>
  <!-- faint track rails -->
  <path d="M -20 452 Q 256 392 532 452" fill="none" stroke="#ffffff" stroke-opacity=".10" stroke-width="6"/>
  <path d="M -20 478 Q 256 418 532 478" fill="none" stroke="#ffffff" stroke-opacity=".07" stroke-width="6"/>
  <!-- horseshoe: dark edge, gold face, highlight -->
  <path d="{shoe}" fill="none" stroke="url(#goldEdge)" stroke-width="{W + 10}" stroke-linecap="butt"/>
  <path d="{shoe}" fill="none" stroke="url(#gold)" stroke-width="{W}" stroke-linecap="butt"/>
  <path d="{shoe}" fill="none" stroke="#fff6d6" stroke-opacity=".35" stroke-width="8"
        transform="translate(-10 -6)" stroke-linecap="butt"/>
  <!-- heel calks -->
  <rect x="{CX - R - W / 2 - 5}" y="{TOP - 16}" width="{W + 10}" height="22" rx="5" fill="url(#goldEdge)"/>
  <rect x="{CX + R - W / 2 - 5}" y="{TOP - 16}" width="{W + 10}" height="22" rx="5" fill="url(#goldEdge)"/>
  {holes}
  <!-- winner's star -->
  <polygon points="{star(CX, 232, 62, 26)}" fill="#ffffff" stroke="#e5b53a" stroke-width="6" stroke-linejoin="round"/>
</svg>
"""


def raster(size=512, ss=4):
    """Draw the same artwork as svg() with Pillow (MuPDF drops SVG gradients).
    Drawn at ss x resolution, then downsampled for smooth edges."""
    S = size * ss
    k = S / 512

    def p(v):
        return v * k

    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.sqrt((xx - 0.5 * S) ** 2 + (yy - 0.38 * S) ** 2) / (0.75 * S)
    stops = [(0, (0x2f, 0x7a, 0x5c)), (0.6, (0x1f, 0x4e, 0x3d)), (1.0, (0x0f, 0x2a, 0x20))]
    bg = np.zeros((S, S, 3), np.float32)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (d >= t0) & (d <= t1) if t1 < 1 else (d >= t0)
        t = np.clip((d - t0) / (t1 - t0), 0, 1)[..., None]
        bg = np.where(m[..., None], np.array(c0) * (1 - t) + np.array(c1) * t, bg)
    img = Image.fromarray(bg.astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    for off, alpha in ((452, 26), (478, 18)):  # faint track rails
        pts = [(p(x), p(off - 60 * (1 - ((x - 256) / 276) ** 2))) for x in range(-20, 533, 4)]
        draw.line(pts, fill=(255, 255, 255, alpha), width=int(p(6)))

    def shoe_mask(width):
        m = Image.new("L", (S, S), 0)
        md = ImageDraw.Draw(m)
        r_out, r_in = R + width / 2, R - width / 2
        md.pieslice([p(CX - r_out), p(CY - r_out), p(CX + r_out), p(CY + r_out)], 0, 180, fill=255)
        md.pieslice([p(CX - r_in), p(CY - r_in), p(CX + r_in), p(CY + r_in)], 0, 180, fill=0)
        for side in (-1, 1):
            x = CX + side * R
            md.rectangle([p(x - width / 2), p(TOP), p(x + width / 2), p(CY) + 1], fill=255)
        return m

    def vgrad(stops_):
        col = np.zeros((S, 3), np.float32)
        ys = np.arange(S) / S
        for (t0, c0), (t1, c1) in zip(stops_, stops_[1:]):
            t = np.clip((ys - t0) / (t1 - t0), 0, 1)[:, None]
            seg = (ys >= t0) & (ys <= t1)
            col[seg] = (np.array(c0) * (1 - t) + np.array(c1) * t)[seg]
        return Image.fromarray(np.repeat(col[:, None, :], S, axis=1).astype(np.uint8), "RGB")

    # Gradients run over the shoe's own height (TOP-16 .. CY+R+W/2), like the SVG's bounding box.
    y0, y1 = (TOP - 16) / 512, (CY + R + W / 2 + 5) / 512
    edge = vgrad([(0, (0x6e, 0x4b, 0x0c)), (y0, (0xc8, 0x93, 0x25)), (y1, (0x6e, 0x4b, 0x0c)), (1, (0x6e, 0x4b, 0x0c))])
    gold = vgrad([(0, (0xff, 0xe9, 0xa3)), (y0, (0xff, 0xe9, 0xa3)),
                  (y0 + 0.45 * (y1 - y0), (0xe5, 0xb5, 0x3a)), (y1, (0xa8, 0x78, 0x1a)), (1, (0xa8, 0x78, 0x1a))])

    calks = Image.new("L", (S, S), 0)
    cd = ImageDraw.Draw(calks)
    for side in (-1, 1):
        x = CX + side * R
        cd.rounded_rectangle([p(x - W / 2 - 5), p(TOP - 16), p(x + W / 2 + 5), p(TOP + 6)], radius=p(5), fill=255)
    img.paste(edge, (0, 0), ImageChops.lighter(shoe_mask(W + 10), calks))
    img.paste(gold, (0, 0), shoe_mask(W))
    hi = shoe_mask(8)
    img.paste((255, 246, 214), (int(-p(10)), int(-p(6))), hi.point(lambda v: v * 0.35))

    for x, y in nail_holes():
        ang = math.degrees(math.atan2(y - CY, x - CX)) - 90 if y > CY else 0
        hole = Image.new("L", (int(p(40)), int(p(40))), 0)
        ImageDraw.Draw(hole).rounded_rectangle([p(14), p(9), p(26), p(31)], radius=p(6), fill=190)
        hole = hole.rotate(-ang, resample=Image.BICUBIC)
        img.paste((0x3a, 0x2a, 0x05), (int(p(x - 20)), int(p(y - 20))), hole)

    pts = [tuple(map(lambda v: p(float(v)), xy.split(","))) for xy in star(CX, 232, 62, 26).split()]
    draw.polygon(pts, fill=(255, 255, 255), outline=(0xe5, 0xb5, 0x3a), width=int(p(6)))
    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg())
    big = raster(512)
    for size, name in ((512, "icon-512.png"), (192, "icon-192.png"),
                       (180, "apple-touch-icon.png"), (32, "favicon-32.png")):
        (big if size == 512 else big.resize((size, size), Image.LANCZOS)).save(os.path.join(DOCS, name))
        print("wrote", name)


if __name__ == "__main__":
    main()

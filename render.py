#!/usr/bin/env python3
"""Build the Tavara passport spread (1024x720 PNG) from a portrait file.

Country: Republic of Tavara, an island republic in the Indian Ocean.
Capital Port Lumara. Holder Lani Maru Veke, marine biologist.
All dates are internally consistent: passport issued 12 MAR 2024,
every stamp falls after that date, in chronological order.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 720
CREAM = (246, 241, 227)
PAGE = (250, 246, 236)
INK = (26, 38, 38)
TEAL = (15, 90, 92)
TEAL_DARK = (14, 58, 59)
GOLD = (176, 138, 46)
GREY = (110, 108, 96)
LIGHT_BAND = (237, 230, 210)

FONT_PATHS = {
    "serif_b": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "serif_i": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_b": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ],
}


def font(kind, size):
    for p in FONT_PATHS[kind]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def check_digit(s):
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(s):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - 55
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<TAVVEKE<<LANI<MARU"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "TV4829167"
    cd1 = check_digit(doc)
    dob = "900608"
    cd2 = check_digit(dob)
    exp = "340311"
    cd3 = check_digit(exp)
    personal = "<" * 14
    cd4 = check_digit(personal)
    body = doc + cd1 + "TAV" + dob + cd2 + "F" + exp + cd3 + personal + cd4
    cd5 = check_digit(body)
    line2 = body + cd5
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_emblem(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=2)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
                 outline=TEAL, width=1)
    # frigate bird: two arcs
    draw.arc([cx - 13, cy - 12, cx + 1, cy + 2], 200, 340, fill=TEAL, width=2)
    draw.arc([cx - 1, cy - 12, cx + 13, cy + 2], 200, 340, fill=TEAL, width=2)
    # three waves
    for i, yy in enumerate((cy + 6, cy + 11, cy + 16)):
        draw.arc([cx - 14, yy - 4, cx - 2, yy + 4], 0, 180, fill=TEAL, width=2)
        draw.arc([cx + 2, yy - 4, cx + 14, yy + 4], 0, 180, fill=TEAL, width=2)
    # small star above the bird
    sx, sy = cx, cy - 16
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 4 if i % 2 == 0 else 2
        pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(pts, fill=GOLD)


def guilloche(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y0 in range(30, H, 46):
        pts = []
        for x in range(0, W + 8, 8):
            pts.append((x, y0 + 5 * math.sin(x / 55.0 + y0)))
        d.line(pts, fill=(15, 90, 92, 14), width=1)
    return Image.alpha_composite(base, layer)


def stamp(draw_layer, box, kind, place, date, colour, angle):
    """Draw one ink stamp on its own layer, rotated, then paste."""
    sw, sh = 236, 84
    lay = Image.new("RGBA", (sw + 40, sh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0 = 20, 20
    d.rounded_rectangle([x0, y0, x0 + sw, y0 + sh], radius=6,
                        outline=colour + (235,), width=3)
    d.rounded_rectangle([x0 + 5, y0 + 5, x0 + sw - 5, y0 + sh - 5], radius=4,
                        outline=colour + (180,), width=1)
    cx = x0 + sw // 2
    d.text((cx, y0 + 12), kind, font=font("sans_b", 13),
           fill=colour + (235,), anchor="ma")
    d.text((cx, y0 + 32), place, font=font("sans_b", 13),
           fill=colour + (235,), anchor="ma")
    d.text((cx, y0 + 52), date, font=font("sans", 12),
           fill=colour + (235,), anchor="ma")
    d.text((cx, y0 + 68), "IMMIGRATION", font=font("sans", 7),
           fill=colour + (200,), anchor="ma")
    rot = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    draw_layer.alpha_composite(rot, (box[0] - 20, box[1] - 20))


def build(portrait_path, out_path):
    img = Image.new("RGBA", (W, H), TEAL_DARK + (255,))
    draw = ImageDraw.Draw(img)
    # outer cover edge
    draw.rectangle([0, 0, W - 1, H - 1], outline=(8, 40, 41), width=4)
    # pages
    draw.rectangle([14, 10, 508, H - 10], fill=PAGE + (255,))
    draw.rectangle([516, 10, W - 14, H - 10], fill=PAGE + (255,))
    img = guilloche(img)
    draw = ImageDraw.Draw(img)
    # gutter shadow
    for i in range(6):
        draw.line([508 + i, 10, 508 + i, H - 10], fill=(0, 0, 0, 28 - i * 4))
        draw.line([516 - i, 10, 516 - i, H - 10], fill=(0, 0, 0, 28 - i * 4))
    draw.line([512, 10, 512, H - 10], fill=(60, 50, 30, 160), width=2)

    # ---------- LEFT PAGE: data page ----------
    draw_emblem(draw, 261, 52, 24)
    draw.text((261, 82), "REPUBLIC OF TAVARA", font=font("serif_b", 21),
              fill=INK, anchor="ma")
    draw.text((261, 106), "REPUBLIK TAVARA", font=font("sans", 9),
              fill=GREY, anchor="ma")
    draw.line([40, 122, 482, 122], fill=GOLD, width=2)
    draw.line([40, 126, 482, 126], fill=GOLD, width=1)

    # type / code / number row
    y = 138
    for label, value, x in (("Type", "P", 40), ("Code", "TAV", 120),
                            ("Passport No.", "TV4829167", 220)):
        draw.text((x, y), label.upper(), font=font("sans", 8), fill=GREY)
        draw.text((x, y + 11), value, font=font("sans_b", 14), fill=INK)
    draw.text((482, y + 11), "PASSPORT", font=font("sans_b", 12),
              fill=TEAL, anchor="ra")

    # portrait: centre crop to the photo ratio, no stretching
    photo = Image.open(portrait_path).convert("RGB")
    pw, ph = 150, 190
    ratio = pw / ph
    w0, h0 = photo.size
    if w0 / h0 > ratio:
        nw = int(h0 * ratio)
        x0 = (w0 - nw) // 2
        crop = photo.crop((x0, 0, x0 + nw, h0))
    else:
        nh = int(w0 / ratio)
        y0 = (h0 - nh) // 2
        crop = photo.crop((0, y0, w0, y0 + nh))
    crop = crop.resize((pw, ph), Image.LANCZOS)
    img.paste(crop, (40, 168))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 168, 40 + pw, 168 + ph], outline=(255, 255, 255), width=4)
    draw.rectangle([40, 168, 40 + pw, 168 + ph], outline=INK, width=1)
    # round seal overlapping the photo corner only, clear of the data fields
    sx, sy = 168, 344
    seal = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seal)
    sd.ellipse([6, 6, 74, 74], outline=(107, 63, 160, 220), width=2)
    sd.ellipse([11, 11, 69, 69], outline=(107, 63, 160, 180), width=1)
    sd.text((40, 24), "PORT", font=font("sans_b", 8),
            fill=(107, 63, 160, 230), anchor="ma")
    sd.text((40, 35), "LUMARA", font=font("sans_b", 8),
            fill=(107, 63, 160, 230), anchor="ma")
    sd.text((40, 48), "12 MAR 2024", font=font("sans", 6),
            fill=(107, 63, 160, 230), anchor="ma")
    img.alpha_composite(seal, (sx - 40, sy - 40))
    draw = ImageDraw.Draw(img)

    # data fields, right of the photo
    fields = [
        ("Surname", "VEKE"),
        ("Given names", "LANI MARU"),
        ("Nationality", "TAVARAN"),
        ("Date of birth", "08 JUN 1990"),
        ("Sex", "F"),
        ("Place of birth", "PORT LUMARA"),
        ("Date of issue", "12 MAR 2024"),
        ("Date of expiry", "11 MAR 2034"),
        ("Authority", "PASSPORT OFFICE, PORT LUMARA"),
    ]
    fy = 168
    for label, value in fields:
        draw.text((208, fy), label, font=font("sans", 9), fill=GREY)
        draw.text((208, fy + 11), value, font=font("sans_b", 12), fill=INK)
        fy += 24
    # extra facts row
    fy += 2
    draw.line([208, fy, 482, fy], fill=(200, 192, 168), width=1)
    fy += 8
    for label, value, x in (("Height", "1.68 m", 208),
                            ("Eyes", "BROWN", 300),
                            ("Profession", "MARINE BIOLOGIST", 372)):
        draw.text((x, fy), label, font=font("sans", 8), fill=GREY)
        draw.text((x, fy + 10), value, font=font("sans_b", 10), fill=INK)

    # signature
    sy2 = 452
    draw.line([40, sy2, 260, sy2], fill=INK, width=1)
    draw.text((52, sy2 - 30), "Lani Maru Veke", font=font("serif_i", 20),
              fill=(40, 60, 90))
    draw.text((40, sy2 + 6), "Signature of holder", font=font("sans", 8),
              fill=GREY)
    draw.text((300, sy2 + 6), "This passport is the property of\nthe Republic of Tavara.",
              font=font("serif_i", 10), fill=GREY)

    # remarks box, fills the gap above the MRZ and ties holder to the place
    draw.rectangle([40, 498, 482, 546], outline=(190, 180, 150), width=1)
    draw.text((52, 506), "REMARKS", font=font("sans_b", 8), fill=GREY)
    draw.text((52, 520),
              "Holder serves with the Tavara Reef Survey. Renew at Port Lumara.",
              font=font("sans", 10), fill=INK)

    # MRZ band
    draw.rectangle([28, 560, 494, 690], fill=LIGHT_BAND + (255,))
    draw.rectangle([28, 560, 494, 690], outline=(190, 180, 150), width=1)
    l1, l2 = mrz_lines()
    draw.text((261, 578), l1, font=font("mono", 15), fill=INK, anchor="ma")
    draw.text((261, 606), l2, font=font("mono", 15), fill=INK, anchor="ma")
    draw.text((261, 640), "Machine readable zone  •  Hold this page flat at the border",
              font=font("sans", 8), fill=GREY, anchor="ma")

    # ---------- RIGHT PAGE: visas ----------
    draw.text((540, 34), "VISAS", font=font("serif_b", 20), fill=INK)
    draw.text((540, 60), "Visas and entry stamps", font=font("sans", 9),
              fill=GREY)
    draw.text((984, 40), "12", font=font("serif_b", 16), fill=TEAL,
              anchor="ra")
    draw.line([540, 78, 984, 78], fill=GOLD, width=2)

    stamps = [
        ("DEPARTURE", "PORT LUMARA, TAVARA", "02 APR 2024", (31, 78, 156), -4),
        ("ARRIVAL", "COLOMBO, SRI LANKA", "03 APR 2024", (107, 63, 160), 3),
        ("DEPARTURE", "COLOMBO, SRI LANKA", "18 APR 2024", (107, 63, 160), -2),
        ("ARRIVAL", "MALE, MALDIVES", "19 APR 2024", (30, 122, 76), 4),
        ("DEPARTURE", "MALE, MALDIVES", "27 APR 2024", (30, 122, 76), -3),
        ("ARRIVAL", "PORT LUMARA, TAVARA", "28 APR 2024", (31, 78, 156), 2),
        ("ARRIVAL", "COCHIN, INDIA", "14 SEP 2025", (138, 59, 46), -4),
        ("DEPARTURE", "COCHIN, INDIA", "29 SEP 2025", (138, 59, 46), 3),
    ]
    gx, gy = 540, 96
    for i, (kind, place, date, colour, angle) in enumerate(stamps):
        cx = gx + (i % 2) * 232
        cy = gy + (i // 2) * 92
        stamp(img, (cx, cy), kind, place, date, colour, angle)

    # Reef Levy box: the telling paperwork detail
    by = 480
    draw.rectangle([540, by, 984, 640], outline=TEAL, width=2)
    draw.rectangle([540, by, 984, by + 28], fill=TEAL + (255,))
    draw.text((552, by + 6), "REEF LEVY  •  PAID 12 TV", font=font("sans_b", 12),
              fill=(255, 255, 255))
    draw.text((972, by + 6), "RL-2024-1187", font=font("sans", 10),
              fill=(255, 255, 255), anchor="ra")
    body = ("CONDITION 7: This passport is valid for travel only with a "
            "current Reef Levy receipt. Coral, shells and sand must not be "
            "removed from Tavara. Fine 500 TV.")
    lines = wrap(draw, body, font("sans", 11), 420)
    ly = by + 38
    for ln in lines:
        draw.text((552, ly), ln, font=font("sans", 11), fill=INK)
        ly += 17
    draw.text((552, 616), "Paid at Port Lumara  •  12 MAR 2024",
              font=font("sans", 9), fill=GREY)

    draw.text((540, 664), "Page 12 — visas and entry stamps only.",
              font=font("sans", 8), fill=GREY)
    draw.text((984, 664), "TAV", font=font("sans_b", 9), fill=TEAL,
              anchor="ra")

    img.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    portrait = sys.argv[1]
    out = sys.argv[2]
    build(portrait, out)
    print(out)

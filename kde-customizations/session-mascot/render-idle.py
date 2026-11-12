#!/usr/bin/env python3
"""Render a seamless, transparent idle loop from the supplied logo geometry."""
import math
from pathlib import Path
from PIL import Image, ImageDraw

SIZE, SUPERSAMPLE, FRAMES, DURATION = 320, 3, 80, 50
BARS = [
    (0, 0, 58, 22, '#2563C9'), (66, 0, 70, 22, '#DF493F'),
    (4, 34, 22, 62, '#DED6C8'), (38, 34, 22, 62, '#E4AD22'),
    (72, 34, 22, 62, '#278F8B'), (4, 106, 22, 62, '#E56D2F'),
    (38, 106, 22, 62, '#3F7D44'), (72, 106, 22, 62, '#8F5B40'),
]
OUT = Path(__file__).resolve().parent
palette = Image.new('P', (1, 1))
colours = [0, 0, 0]
for *_, colour in BARS:
    colours.extend(bytes.fromhex(colour[1:]))
palette.putpalette(colours + [0] * (768 - len(colours)))
frames = []
scale = SIZE * 0.75 / 168
for frame in range(FRAMES):
    phase = 2 * math.pi * frame / FRAMES
    image = Image.new('RGBA', (SIZE * SUPERSAMPLE,) * 2)
    draw = ImageDraw.Draw(image)
    for i, (x, y, w, h, colour) in enumerate(BARS):
        cx, cy = x + w / 2 - 68, y + h / 2 - 84
        offset = i * 0.7 + cx * 0.02
        dy = 1.1 * math.sin(phase + offset)
        angle = 0.012 * math.sin(phase + offset)
        ca, sa = math.cos(angle), math.sin(angle)
        points = []
        for px, py in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
            points.append(((SIZE / 2 + (cx + ca * px - sa * py) * scale) * SUPERSAMPLE,
                           (SIZE / 2 + (cy + dy + sa * px + ca * py) * scale) * SUPERSAMPLE))
        draw.polygon(points, fill=colour)
    image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    indexed = image.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
    # GIF has binary transparency. Keep colour edges free of black/white mattes.
    indexed.paste(0, mask=image.getchannel('A').point(lambda a: 255 if a < 128 else 0))
    indexed.info['transparency'] = 0
    frames.append(indexed)
path = OUT / 'ralleur-idle.gif'
frames[0].save(path, save_all=True, append_images=frames[1:], duration=DURATION,
               loop=0, transparency=0, disposal=2, optimize=False)
with Image.open(path) as check:
    assert check.n_frames == FRAMES
    assert check.info['loop'] == 0
    assert check.size == (SIZE, SIZE)
    assert check.info['transparency'] == 0
    last = None
    changed = 0
    for i in range(check.n_frames):
        check.seek(i)
        rgba = check.convert('RGBA')
        assert rgba.getpixel((0, 0))[3] == 0
        assert rgba.getbbox()[0] > 0 and rgba.getbbox()[1] > 0
        if last is not None and last != rgba.tobytes(): changed += 1
        last = rgba.tobytes()
    assert changed == FRAMES - 1
print(f'{path}: {FRAMES} frames, {FRAMES * DURATION / 1000:g}s, {path.stat().st_size} bytes, transparent, looping')

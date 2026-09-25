#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课件 SVG 预览器：按源坐标把每个 `::: svg` 块重画成 PNG，用来"真的看一眼"。

用法：
    python3 preview_lesson_svg.py <课件内容文件 .md> [输出目录]
    python3 preview_lesson_svg.py <课件内容文件 .md> --only 3 --scale 4

为什么要有它：几何自检（`check_lesson_svg.py`）只能判"数值上必然错"的三类；
方向是否讲得通、留白是否舒服、标注有没有压住曲线，这些只有看图才知道。本机没有
cairosvg / svglib / rsvg-convert，所以这里按源坐标用 PIL 重画——不做完整 SVG 渲染，
只认 <text> / <line> / <rect> / <circle> 四种元素，但足以暴露版式问题。

退出码：0 = 全部块都画出来了；1 = 有块画不出来（解析失败/缺字体）；2 = 用法或字体错误。

字体（**关键，先读这条**）：
    测宽与绘制都必须显式加载含中文字形的字体（微软雅黑 msyh.ttc）。若让 PIL 落到
    不含汉字的回退字体，中文串会被量短——本项目真实发生过一次：中文长句在 CJK 字体下
    宽 211、在 Arial 下宽 161（差 24%），于是 `text-anchor="end"` 的标签左端跑到
    x=-83 也没被发现。本脚本启动时用「一个汉字 ÷ 一个拉丁字母」的宽度比断言字体含
    汉字，不满足直接退出 2，绝不"用回退字体凑合画"。

已知盲区（**这两条是实际踩过的，不要在别处当成"检查过了"**）：
  ① 只画四种元素：`<path>`、`<g transform=…>`、行内 marker 箭头等一律忽略；
     因此图里若有路径或变换，预览与浏览器实际样子会有出入。
  ② **不查"线 × 文本"相交**：本脚本与几何自检都只比较"文本 × 文本"的包围盒，
     查不出引导线/虚线穿过文字这类问题——真实发生过一次（一条延长后的指针引导线
     从「格」字上切过去，两个 checker 都没报）。
     要兜住它，得把 <line> 也换成矩形参与碰撞，属于尚未实现的部分。
"""
import os
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.stderr.write('需要 Pillow（PIL）。\n')
    raise SystemExit(2)

CJK_FONT_CANDIDATES = (
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/simsun.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/System/Library/Fonts/PingFang.ttc',
)
LATIN_FONT_CANDIDATES = (
    'C:/Windows/Fonts/arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/System/Library/Fonts/Helvetica.ttc',
)
PROBE_CJK = '次'
PROBE_LATIN = 'A'
CJK_WIDTH_RATIO_MIN = 1.4
BG = (255, 255, 255)
FG = (30, 30, 30)
DEFAULT_SCALE = 3


def pick(candidates, what):
    for path in candidates:
        if os.path.isfile(path):
            return path
    sys.stderr.write(f'找不到可用的{what}字体，试过：\n  ' + '\n  '.join(candidates) + '\n')
    raise SystemExit(2)


def load_fonts():
    cjk = pick(CJK_FONT_CANDIDATES, '中文')
    latin = pick(LATIN_FONT_CANDIDATES, '拉丁')
    probe = ImageFont.truetype(cjk, 16)
    draw = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    w_cjk = draw.textlength(PROBE_CJK, font=probe)
    w_latin = draw.textlength(PROBE_LATIN, font=probe)
    if w_latin <= 0 or w_cjk / w_latin < CJK_WIDTH_RATIO_MIN:
        sys.stderr.write(
            f'测宽字体不含汉字：{cjk}（"{PROBE_CJK}" {w_cjk} / "{PROBE_LATIN}" {w_latin} '
            f'= {w_cjk / max(w_latin, 1e-9):.2f} < {CJK_WIDTH_RATIO_MIN}）。'
            '中文串会被量短，画出来也不可信。\n')
        raise SystemExit(2)
    return cjk, latin


def split_blocks(lines):
    blocks, start = [], None
    for i, line in enumerate(lines, 1):
        if line.strip() == '::: svg':
            start = i
        elif line.strip() == ':::' and start is not None:
            blocks.append((start, i, lines[start:i - 1]))
            start = None
    return blocks


def has_cjk(text):
    return any('\u4e00' <= c <= '\u9fff' for c in text)


def hexcolor(value, default):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5)) if value else default


def draw_block(body, scale, cjk, latin):
    svg = '\n'.join(body)
    view = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not view:
        return None, '找不到 viewBox'
    width, height = float(view.group(1)), float(view.group(2))
    image = Image.new('RGB', (int(round(width * scale)), int(round(height * scale))), BG)
    draw = ImageDraw.Draw(image)
    cache = {}

    def font_of(text, size):
        path = cjk if has_cjk(text) else latin
        key = (path, int(round(size * scale)))
        if key not in cache:
            cache[key] = ImageFont.truetype(path, key[1])
        return cache[key]

    for line in body:
        stripped = line.strip()
        match = re.match(r'<line x1="([\d.-]+)" y1="([\d.-]+)" x2="([\d.-]+)" y2="([\d.-]+)"([^>]*)/>', stripped)
        if match:
            x1, y1, x2, y2 = (float(match.group(i)) for i in (1, 2, 3, 4))
            rest = match.group(5)
            color = hexcolor(re.search(r'stroke="(#[0-9a-fA-F]{6})"', rest) and
                             re.search(r'stroke="(#[0-9a-fA-F]{6})"', rest).group(1), (110, 110, 110))
            width_px = max(1, int(round(float(re.search(r'stroke-width="([\d.]+)"', rest).group(1)) * scale))) \
                if 'stroke-width' in rest else 1
            draw.line([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=color, width=width_px)
            continue

        match = re.match(r'<rect x="([\d.-]+)" y="([\d.-]+)" width="([\d.-]+)" height="([\d.-]+)"([^>]*)/>', stripped)
        if match:
            x, y, w, h = (float(match.group(i)) for i in (1, 2, 3, 4))
            rest = match.group(5)
            # `fill="none"` 是只有描边的格子：不填色（填了会把相邻内容盖住）
            fill_value = re.search(r'fill="([^"]+)"', rest)
            if fill_value and fill_value.group(1).strip().lower() == 'none':
                fill_color = None
            else:
                fill_color = hexcolor(fill_value.group(1) if fill_value else None, None)
            stroke = re.search(r'stroke="(#[0-9a-fA-F]{6})"', rest)
            outline = hexcolor(stroke.group(1) if stroke else None, (150, 150, 150))
            width_px = max(1, int(round(float(re.search(r'stroke-width="([\d.]+)"', rest).group(1)) * scale))) \
                if 'stroke-width' in rest else 1
            draw.rectangle([x * scale, y * scale, (x + w) * scale, (y + h) * scale],
                           fill=fill_color, outline=outline, width=width_px)
            continue

        match = re.match(r'<circle cx="([\d.-]+)" cy="([\d.-]+)" r="([\d.-]+)"([^>]*)/>', stripped)
        if match:
            cx, cy, r = (float(match.group(i)) for i in (1, 2, 3))
            fill = re.search(r'fill="(#[0-9a-fA-F]{6})"', match.group(4))
            draw.ellipse([(cx - r) * scale, (cy - r) * scale, (cx + r) * scale, (cy + r) * scale],
                         fill=hexcolor(fill.group(1) if fill else None, (0, 0, 0)))
            continue

        match = re.match(r'<text x="([\d.-]+)" y="([\d.-]+)"([^>]*)>([^<]*)</text>', stripped)
        if match:
            x, y, rest, text = (float(match.group(1)), float(match.group(2)),
                                match.group(3), match.group(4))
            size = float(re.search(r'font-size="([\d.]+)"', rest).group(1)) \
                if 'font-size' in rest else 16.0
            fill = re.search(r'fill="(#[0-9a-fA-F]{6})"', rest)
            color = hexcolor(fill.group(1) if fill else None, FG)
            anchor = ('end' if 'text-anchor="end"' in rest
                      else 'middle' if 'text-anchor="middle"' in rest else 'start')
            draw.text((x * scale, y * scale), text, font=font_of(text, size), fill=color,
                      anchor={'end': 'rs', 'middle': 'ms', 'start': 'ls'}[anchor])
            continue

    return image, None


def main(argv):
    positional = [a for a in argv if not a.startswith('-')]
    if not positional:
        raise SystemExit(__doc__)
    path = positional[0]
    if not os.path.isfile(path):
        sys.stderr.write(f'找不到课件文件：{path}\n')
        return 2
    out_dir = positional[1] if len(positional) > 1 else os.path.dirname(os.path.abspath(path))
    only = None
    if '--only' in argv:
        only = int(argv[argv.index('--only') + 1])
    scale = DEFAULT_SCALE
    if '--scale' in argv:
        scale = int(argv[argv.index('--scale') + 1])

    cjk, latin = load_fonts()
    lines = open(path, encoding='utf-8').read().splitlines()
    blocks = split_blocks(lines)
    if not blocks:
        print(f'OK   {path}（没有 ::: svg 块）')
        return 0
    os.makedirs(out_dir, exist_ok=True)
    failed = 0
    for index, (start, end, body) in enumerate(blocks, 1):
        if only is not None and index != only:
            continue
        image, error = draw_block(body, scale, cjk, latin)
        if error:
            print(f'{path}:{start} 块 #{index} 画不出来：{error}')
            failed += 1
            continue
        out = os.path.join(out_dir, f'svg-{index:02d}-L{start}.png')
        image.save(out)
        print(f'块 #{index}（L{start}）→ {out}  {image.width}×{image.height}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课件 SVG 几何自检：文本越界、文本重叠、线段方向。

用法：
    python3 check_lesson_svg.py <课件内容文件 .md>            # 全部检查
    python3 check_lesson_svg.py <课件内容文件 .md> --quiet    # 只报问题

扫描课件里每个 `::: svg` 块，做三类离线判定（不需要浏览器、不需要 cairosvg）：

  ① 文本越界：按**真实字体度量**算出每个 <text> 的包围盒，左右端必须落在
     `[0, viewBox 宽]`、下缘必须 ≤ `viewBox 高`。
     **`text-anchor="end"` 与 `"middle"` 的标签必须查左端**——锚点在右侧或中间的
     中文长句会整串向左伸，只查右端会漏（这是真实漏过的一类）。
  ② 文本重叠：同一块内任意两个文本包围盒不得相交。**唯一的白名单**是
     "同一个格子里叠标的记号"（例如数字 `2` 与目标星号 `*`），见 ALLOWED_OVERLAPS。
  ③ 线段方向：横向跨度 > 60 的线若 `dy > 0`（SVG 的 y 轴朝下，即屏幕上向右下走），
     在"随 n 上升"这类图里就是画反了。纵向短线下探、横线、轴标线都不在此列。

退出码：0 = 全部合格；1 = 有问题（逐条打印 `<文件>:<行号> <问题>`）；2 = 用法/字体错误。

字体守卫（**关键**）：测宽字体必须真的含中文字形，否则中文长句会被量短、
checker 自己给出假阴性。脚本按 `CJK_FONT_CANDIDATES` 顺序找第一个存在的字体，
并用「一个汉字 + 一个拉丁字母」的宽度比断言它确实含中文；不含就直接退出 2，
不做"用回退字体凑合量"这件事。

已知限制（有意为之，不做的事）：
  · 不做完整 SVG 渲染：只认 <text> / <line> / <rect> / <circle> 四种元素，
    其余元素（path、g 变换、marker 箭头等）不参与几何判定。
  · 不判断"画面对不对"这件事本身：角度、比例、色彩、图注与画面的语义一致性
    仍需人眼；本脚本只兜"数值上必然错"的三类。
  · 文本包围盒按字体 ascent/descent 取矩形上界，比实际字形略大（保守）；
    因此重叠判定的假阳性方向是"多报"，不会漏报。
  · 只测第一个可用的 CJK 字体（本机为微软雅黑）；与浏览器实际选用字体的宽度
    可能有少量差异，故留 0 容差、不做"近似通过"。
"""
import os
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.stderr.write('需要 Pillow（PIL）。本机用：<python> -c "import PIL"\n')
    raise SystemExit(2)

# 按顺序找第一个存在的中文字体；微软雅黑优先
CJK_FONT_CANDIDATES = (
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/simsun.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/arphic/uming.ttc',
    '/System/Library/Fonts/PingFang.ttc',
)
LATIN_FONT_CANDIDATES = (
    'C:/Windows/Fonts/arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/System/Library/Fonts/Helvetica.ttc',
)
# 测宽时不放大；度量单位与 viewBox 单位一致
PROBE_CJK = '次'          # 一个汉字
PROBE_LATIN = 'A'         # 一个拉丁字母
# 汉字宽度必须至少是拉丁字母的 1.4 倍，否则说明命中的字体没有汉字字形
CJK_WIDTH_RATIO_MIN = 1.4
# 方向判定：横向跨度超过这个值才算"曲线/数据线"
DIRECTION_MIN_DX = 60
# 设计内的叠标白名单：同格子的「数字 + 目标记号」
ALLOWED_OVERLAPS = (
    (r'^\d$', r'^\*$'),
    (r'^\*$', r'^\d$'),
)


def pick_font(candidates, what):
    for path in candidates:
        if os.path.isfile(path):
            return path
    sys.stderr.write(f'找不到可用的{what}字体，试过：\n  ' + '\n  '.join(candidates) + '\n')
    raise SystemExit(2)


def load_fonts():
    """返回 (cjk_path, latin_path)，并断言 cjk 字体确实含汉字字形。"""
    cjk_path = pick_font(CJK_FONT_CANDIDATES, '中文')
    latin_path = pick_font(LATIN_FONT_CANDIDATES, '拉丁')
    probe = ImageFont.truetype(cjk_path, 16)
    draw = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    w_cjk = draw.textlength(PROBE_CJK, font=probe)
    w_latin = draw.textlength(PROBE_LATIN, font=probe)
    if w_latin <= 0 or w_cjk / w_latin < CJK_WIDTH_RATIO_MIN:
        sys.stderr.write(
            f'测宽字体不含汉字：{cjk_path}（"{PROBE_CJK}" 宽 {w_cjk}，'
            f'"{PROBE_LATIN}" 宽 {w_latin}，比值 {w_cjk / max(w_latin, 1e-9):.2f} '
            f'< {CJK_WIDTH_RATIO_MIN}）。\n'
            '中文长句会被量短，本检查会给出假阴性——请改用含中文字形的字体。\n')
        raise SystemExit(2)
    return cjk_path, latin_path


def split_blocks(lines):
    """切出每个 ::: svg 块。返回 [(首行号, 末行号, 块体行列表)]。"""
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


def parse_text(line):
    """解析 <text …>…</text>，返回 dict；不是 text 行则 None。"""
    match = re.match(r'<text x="([\d.-]+)" y="([\d.-]+)"([^>]*)>([^<]*)</text>',
                     line.strip())
    if not match:
        return None
    x, y, attrs, text = (float(match.group(1)), float(match.group(2)),
                         match.group(3), match.group(4))
    size = float(re.search(r'font-size="([\d.]+)"', attrs).group(1)) \
        if 'font-size' in attrs else 16.0
    if 'text-anchor="end"' in attrs:
        anchor = 'end'
    elif 'text-anchor="middle"' in attrs:
        anchor = 'middle'
    else:
        anchor = 'start'
    return {'x': x, 'y': y, 'text': text, 'size': size, 'anchor': anchor}


def text_box(item, cjk_path, latin_path):
    """按字体度量算包围盒 (x0, y0, x1, y1)。"""
    path = cjk_path if has_cjk(item['text']) else latin_path
    font = ImageFont.truetype(path, int(round(item['size'])))
    draw = ImageDraw.Draw(Image.new('RGB', (8, 8)))
    width = draw.textlength(item['text'], font=font)
    ascent, descent = (v * item['size'] / font.size for v in font.getmetrics())
    x, y = item['x'], item['y']
    if item['anchor'] == 'end':
        x0, x1 = x - width, x
    elif item['anchor'] == 'middle':
        x0, x1 = x - width / 2, x + width / 2
    else:
        x0, x1 = x, x + width
    return (x0, y - ascent, x1, y + descent)


def allowed_overlap(a, b):
    for left, right in ALLOWED_OVERLAPS:
        if (re.match(left, a) and re.match(right, b)) or \
           (re.match(left, b) and re.match(right, a)):
            return True
    return False


def check_block(path, start, body, cjk_path, latin_path):
    """返回 [(行号, 问题)]。"""
    problems = []
    svg = '\n'.join(body)
    view = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not view:
        return [(start, '::: svg 块里找不到 viewBox')]
    width, height = float(view.group(1)), float(view.group(2))

    boxes = []
    for offset, line in enumerate(body):
        line_no = start + offset
        item = parse_text(line)
        if item:
            box = text_box(item, cjk_path, latin_path)
            boxes.append((line_no, item, box))
            x0, y0, x1, y1 = box
            if x0 < 0:
                problems.append((line_no, f'文本左端越出画布：x0={x0:.1f} < 0'
                                           f'（"{item["text"][:20]}"，anchor={item["anchor"]}）'))
            if x1 > width:
                problems.append((line_no, f'文本右端越出画布：x1={x1:.1f} > {width:.0f}'
                                           f'（"{item["text"][:20]}"）'))
            if y1 > height:
                problems.append((line_no, f'文本下缘越出画布：y1={y1:.1f} > {height:.0f}'
                                           f'（"{item["text"][:20]}"）'))

        match = re.match(r'<line x1="([\d.-]+)" y1="([\d.-]+)" x2="([\d.-]+)" y2="([\d.-]+)"',
                         line.strip())
        if match:
            x1v, y1v, x2v, y2v = (float(match.group(i)) for i in (1, 2, 3, 4))
            dx, dy = x2v - x1v, y2v - y1v
            if abs(dx) > DIRECTION_MIN_DX and dy > 0:
                problems.append((line_no, f'线段方向存疑：横向跨度 {dx:.0f} 且 dy={dy:+.0f} > 0，'
                                           f'屏幕上是"向右下"；若语义是"随 n 上升"即画反了'))

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            la, ia, ba = boxes[i]
            lb, ib, bb = boxes[j]
            ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
            oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
            if ox > 0 and oy > 0 and not allowed_overlap(ia['text'], ib['text']):
                problems.append((lb, f'文本重叠："{ia["text"][:16]}"(L{la}) 与 '
                                     f'"{ib["text"][:16]}" 重叠 {ox:.1f} × {oy:.1f}'))
    return problems


def main(argv):
    if not argv or argv[0].startswith('-'):
        raise SystemExit(__doc__)
    path = argv[0]
    quiet = '--quiet' in argv
    if not os.path.isfile(path):
        sys.stderr.write(f'找不到课件文件：{path}\n')
        return 2
    cjk_path, latin_path = load_fonts()
    lines = open(path, encoding='utf-8').read().splitlines()
    blocks = split_blocks(lines)
    if not blocks:
        print(f'OK   {path}（没有 ::: svg 块，无需检查）')
        return 0

    total = []
    for start, end, body in blocks:
        total += check_block(path, start, body, cjk_path, latin_path)
    for line_no, message in sorted(total):
        print(f'{path}:{line_no} {message}')
    if total:
        print(f'\n{len(total)} 个问题（{len(blocks)} 个 svg 块）')
        return 1
    print(f'OK   {path}（{len(blocks)} 个 svg 块：无文本越界、无意外重叠、无画反的长线）')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

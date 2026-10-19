# -*- coding: utf-8 -*-
"""生成霞浦发改批复日报图（核心指标 + 本日/本周/本月新增及明细）
运行：python gen_daily_image.py （在 crawl_xiapu.py 之后执行）
输出：daily_report.png （供企业微信/微信群推送）
统计口径：按政府网站"发布日期"（docreltime）
"""
import json
import os
import datetime
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'approvals_recent.json')
OUT = os.path.join(HERE, 'daily_report.png')

# ---------- 颜色 ----------
C_PRIMARY = (30, 58, 95)      # 深蓝
C_ACCENT = (59, 130, 246)     # 亮蓝
C_TEXT = (31, 45, 61)
C_GRAY = (91, 107, 128)
C_BG = (248, 250, 252)
C_WHITE = (255, 255, 255)
C_LINE = (219, 228, 239)

# 类型胶囊色 (文字, 背景)
TYPE_COLOR = {
    '可研批复': ((37, 99, 235), (232, 240, 254)),
    '设计批复': ((15, 30, 51), (238, 245, 255)),
    '立项批复': ((22, 163, 74), (230, 244, 234)),
}


def font(size, bold=False):
    """跨平台字体：Windows 微软雅黑 / Linux Noto CJK（GitHub Actions 环境）"""
    cands = (
        [r'C:\Windows\Fonts\msyhbd.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
         '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'] if bold else
        [r'C:\Windows\Fonts\msyh.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
         '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc']
    )
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def to_num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def money_str(v):
    if v <= 0:
        return '—'
    if v >= 10000:
        s = f'{v/10000:.2f}'.rstrip('0').rstrip('.')
        return s + ' 亿'
    return (f'{v:.0f}') + ' 万'


def main():
    with open(SRC, encoding='utf-8') as f:
        d = json.load(f)
    items = d['items']
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.isoweekday() - 1)
    month_start = today.replace(day=1)

    for it in items:
        it['m'] = to_num(it.get('invest_wan'))
        it['c'] = it.get('category', '')
        it['d'] = it.get('publish_date', '')
        it['n'] = it.get('project_name', '')
        it['u'] = it.get('build_unit', '')

    total = len(items)
    items.sort(key=lambda x: x['d'], reverse=True)
    total_amt = sum(it['m'] for it in items)
    cats = {}
    for it in items:
        cats[it['c']] = cats.get(it['c'], 0) + 1

    def in_range(it, a, b=None):
        try:
            dt = datetime.date.fromisoformat(it['d'][:10])
        except ValueError:
            return False
        if b is None:
            return dt == a
        return a <= dt <= b

    day_new = [it for it in items if in_range(it, today)]
    week_new = [it for it in items if in_range(it, week_start, today)]
    month_new = [it for it in items if in_range(it, month_start, today)]

    # 明细列表：优先本月；本月为空则显示最近 8 条并注明
    if month_new:
        detail_title = f'本月新增项目明细（{len(month_new)} 条）'
        detail_rows = month_new
    else:
        recent = sorted(items, key=lambda x: x['d'], reverse=True)[:8]
        last_date = items[0]['d'][:10] if items else '—'
        detail_title = f'本月暂无新发布 · 最近发布 {last_date}（最近 8 条）'
        detail_rows = recent

    # ---------- 画布 ----------
    W = 960
    PAD = 28
    row_h = 46
    detail_max = min(len(detail_rows), 15)   # 明细最多 15 行

    H = (110 + 16 + 118 + 12 + 118 + 16 + 34 + 10 + 30
         + detail_max * row_h + 12 + 54 + 20)
    img = Image.new('RGB', (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    # ---------- 1. 标题栏（深蓝渐变） ----------
    y0 = 16
    th = 96
    grad = Image.new('RGB', (W - 2 * PAD, th))
    gd = ImageDraw.Draw(grad)
    gw = grad.width
    for x in range(gw):
        t = x / gw
        r = int(C_PRIMARY[0] + (C_ACCENT[0] - C_PRIMARY[0]) * t)
        g = int(C_PRIMARY[1] + (C_ACCENT[1] - C_PRIMARY[1]) * t)
        b = int(C_PRIMARY[2] + (C_ACCENT[2] - C_PRIMARY[2]) * t)
        gd.line([(x, 0), (x, th)], fill=(r, g, b))
    mask = Image.new('L', grad.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, gw, th], 14, fill=255)
    img.paste(grad, (PAD, y0), mask)

    draw.text((PAD + 26, y0 + 18), '霞浦县发改局项目批复日报', font=font(27, True), fill=C_WHITE)
    sub = f'{today.year} 年 {today.month} 月 {today.day} 日（周{"一二三四五六日"[today.isoweekday()-1]}）  ·  统计口径：网站发布日期'
    draw.text((PAD + 26, y0 + 58), sub, font=font(14), fill=(255, 255, 255))
    badge = f'近半年 {total} 条'
    bw = draw.textlength(badge, font=font(13, True)) + 24
    draw.rounded_rectangle([W - PAD - 26 - bw, y0 + 24, W - PAD - 26, y0 + 50], 13,
                           fill=C_WHITE)
    draw.text((W - PAD - 26 - bw + 12, y0 + 29), badge, font=font(13, True), fill=C_PRIMARY)

    y = y0 + th + 16

    # ---------- 2. 核心指标（5 卡） ----------
    stats = [
        (str(total), '近半年新批批复', C_ACCENT),
        (money_str(total_amt), '批复总投资', (217, 119, 6)),
        (str(cats.get('可研批复', 0)), '可研批复', C_PRIMARY),
        (str(cats.get('设计批复', 0)), '设计批复', C_ACCENT),
        (str(cats.get('立项批复', 0)), '立项批复', (20, 130, 95)),
    ]
    gap = 12
    cw = (W - 2 * PAD - gap * 4) // 5
    ch = 102
    for i, (val, label, color) in enumerate(stats):
        x = PAD + i * (cw + gap)
        draw.rounded_rectangle([x, y, x + cw, y + ch], 12, fill=C_WHITE,
                               outline=C_LINE, width=1)
        draw.line([(x + 14, y + 1), (x + 14, y + ch - 1)], fill=color, width=3)
        f_val = font(26, True)
        vw = draw.textlength(val, font=f_val)
        draw.text((x + (cw - vw) / 2, y + 20), val, font=f_val, fill=color)
        f_lab = font(12)
        lw = draw.textlength(label, font=f_lab)
        draw.text((x + (cw - lw) / 2, y + 64), label, font=f_lab, fill=C_GRAY)
    y += ch + 12

    # ---------- 3. 新增统计（3 卡） ----------
    news = [
        (str(len(day_new)), f'本日新增（{today.month}/{today.day}）', C_ACCENT),
        (str(len(week_new)), f'本周新增（{week_start.month}/{week_start.day} 起）', (20, 130, 95)),
        (str(len(month_new)), f'本月新增（{month_start.month} 月起）', (217, 119, 6)),
    ]
    cw3 = (W - 2 * PAD - gap * 2) // 3
    for i, (val, label, color) in enumerate(news):
        x = PAD + i * (cw3 + gap)
        draw.rounded_rectangle([x, y, x + cw3, y + ch], 12, fill=C_WHITE,
                               outline=C_LINE, width=1)
        draw.rounded_rectangle([x + 14, y + 16, x + 18, y + ch - 16], 2, fill=color)
        f_val = font(30, True)
        vw = draw.textlength(val, font=f_val)
        draw.text((x + 34, y + 16), val, font=f_val, fill=color)
        dsw = draw.textlength('条', font=font(14))
        draw.text((x + 36 + vw + 4, y + 32), '条', font=font(14), fill=C_GRAY)
        draw.text((x + 34, y + 64), label, font=font(12), fill=C_GRAY)
    y += ch + 16

    # ---------- 4. 明细表 ----------
    draw.text((PAD, y), detail_title, font=font(18, True), fill=C_PRIMARY)
    y += 34
    # 表头
    cols = [(PAD + 4, 92, '发布日期'), (PAD + 100, 78, '类型'),
            (PAD + 182, 450, '项目名称 / 建设单位'), (W - PAD - 110, 106, '投资额')]
    draw.rounded_rectangle([PAD, y, W - PAD, y + 30], 8, fill=(201, 214, 243))
    for x, w, label in cols:
        draw.text((x, y + 6), label, font=font(12, True), fill=C_PRIMARY)
    y += 34

    f14 = font(13)
    for idx, it in enumerate(detail_rows[:detail_max]):
        # 斑马纹
        if idx % 2 == 1:
            draw.rectangle([PAD, y, W - PAD, y + row_h - 6], fill=(248, 250, 252))
        cy = y + 12
        draw.text((cols[0][0], cy), it['d'][5:], font=f14, fill=C_TEXT)
        # 类型胶囊
        tcol, tbg = TYPE_COLOR.get(it['c'], (C_TEXT, (240, 240, 240)))
        tw = draw.textlength(it['c'], font=font(11, True)) + 16
        draw.rounded_rectangle([cols[1][0], cy - 2, cols[1][0] + tw, cy + 22], 10, fill=tbg)
        draw.text((cols[1][0] + 8, cy + 1), it['c'], font=font(11, True), fill=tcol)
        # 项目名（截断）+ 单位
        name, unit = it['n'], it['u'] or ''
        maxw = cols[2][1] - 40
        while name and draw.textlength(name, font=f14) > maxw:
            name = name[:-1]
        if name != it['n']:
            name = name.rstrip('（(') + '…'
        draw.text((cols[2][0], cy - 2), name, font=font(13, True), fill=C_TEXT)
        utext = unit if draw.textlength(unit, font=font(10)) <= maxw else ''
        draw.text((cols[2][0], cy + 20), utext, font=font(10), fill=C_GRAY)
        # 投资额（右对齐）
        mv = money_str(it['m'])
        mw = draw.textlength(mv, font=font(13, True))
        draw.text((W - PAD - 14 - mw, cy + 2), mv, font=font(13, True),
                  fill=(217, 119, 6) if it['m'] >= 10000 else C_TEXT)
        y += row_h

    if detail_max < len(detail_rows):
        more = f'… 其余 {len(detail_rows) - detail_max} 条见看板'
        draw.text((PAD + 4, y), more, font=font(12), fill=C_GRAY)
        y += 24
    y += 10

    # ---------- 5. 页脚 ----------
    draw.line([(PAD, y), (W - PAD, y)], fill=C_LINE, width=1)
    foot1 = ('数据来源：霞浦县人民政府网 · 县发改局「政策文件」栏目（已剔除变更/撤销/法人变更类）  '
             f'更新时间 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}')
    foot2 = '完整数据与筛选请见《霞浦发改批复看板》  ·  由 TeleAgent 每日自动生成'
    draw.text((PAD, y + 12), foot1, font=font(11), fill=C_GRAY)
    draw.text((PAD, y + 32), foot2, font=font(11), fill=C_GRAY)

    img.save(OUT)
    print(f'生成 {OUT}  ({img.width}x{img.height})')
    print(f'核心：近半年 {total} 条 / 总投资 {money_str(total_amt)}')
    print(f'新增：本日 {len(day_new)} · 本周 {len(week_new)} · 本月 {len(month_new)}（截至 {now_str()}）' if False else
          f'新增：本日 {len(day_new)} · 本周 {len(week_new)} · 本月 {len(month_new)}')


def now_str():
    return datetime.datetime.now().strftime('%H:%M')


if __name__ == '__main__':
    main()
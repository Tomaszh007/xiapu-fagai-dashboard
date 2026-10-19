# -*- coding: utf-8 -*-
"""Server酱·Turbo 版推送：把日报摘要 + 看板链接 + 日报图推送到个人微信
环境变量：SCKEY（必填，https://sct.ftqq.com 微信扫码获取）
          BOARD_URL（看板地址，如 https://xxx.github.io/xiapu-dashboard/）
免费额度：每天 5 条（本任务每天只发 1 条，足够）
收到位置：微信「方糖」服务号消息，点开可见完整日报（含图），可保存转发
"""
import datetime
import json
import os
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'approvals_recent.json')
IMG_NAME = 'daily_report.png'


def money_str(v):
    if v <= 0:
        return '—'
    if v >= 10000:
        return f'{v/10000:.2f} 亿'.rstrip('0').rstrip(' ')
    return f'{v:.0f} 万'


def main():
    sckey = os.environ.get('SCKEY', '').strip()
    board_url = os.environ.get('BOARD_URL', '').strip().rstrip('/')
    if not sckey:
        print('[SKIP] 未配置 SCKEY')
        return 0

    # 北京时间（GitHub Actions 为 UTC）
    now_bj = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    today = now_bj.date()
    week_start = today - datetime.timedelta(days=today.isoweekday() - 1)
    month_start = today.replace(day=1)

    with open(SRC, encoding='utf-8') as f:
        items = json.load(f)['items']

    def d(it):
        try:
            return datetime.date.fromisoformat((it.get('publish_date') or '')[:10])
        except ValueError:
            return None

    def amt(it):
        try:
            return float(it.get('invest_wan') or 0)
        except ValueError:
            return 0.0

    day_new = [i for i in items if d(i) == today]
    week_new = [i for i in items if d(i) and week_start <= d(i) <= today]
    month_new = [i for i in items if d(i) and month_start <= d(i) <= today]
    total_amt = sum(amt(i) for i in items)
    last_date = max((i[:10] for i in (it.get('publish_date') or '' for it in items)), default='—')

    title = (f'霞浦发改批复日报 {today.month}/{today.day}：'
             f'今+{len(day_new)} 本周+{len(week_new)} 本月+{len(month_new)}')

    lines = [
        f'#### 霞浦发改批复日报 · {today.year}-{today.month:02d}-{today.day:02d}',
        '',
        f'**本日新增 {len(day_new)} 条 · 本周新增 {len(week_new)} 条 · 本月新增 {len(month_new)} 条**',
        f'近半年累计新批 **{len(items)}** 条，批复总投资 **{money_str(total_amt)}元**',
        f'<font color="comment">最新批复发布日期：{last_date}（统计口径：网站发布日期）</font>',
        '',
    ]
    # 新增明细（本日→本周→本月，最多 8 条）
    shown, seen = [], set()
    for label, arr in (('本日', day_new), ('本周', week_new), ('本月', month_new)):
        for it in arr:
            if it['title'] in seen:
                continue
            seen.add(it['title'])
            shown.append(f'{label} [{it["category"]}] {it["project_name"]}'
                         f'（{money_str(amt(it))}元，{it["publish_date"][:10]} 发布）')
            if len(shown) >= 8:
                break
        if len(shown) >= 8:
            break
    if shown:
        lines.append('**新增明细：**')
        lines.extend(f'{i+1}. {s}' for i, s in enumerate(shown))
        if len(seen) > 8:
            lines.append(f'……其余 {len(seen)-8} 条见看板')
    else:
        lines.append('*今日暂无新发布批复*')

    if board_url:
        lines += ['', f'[📊 点击查看完整交互看板]({board_url})',
                  f'[🖼 日报图]({board_url}/{IMG_NAME})']

    r = requests.post(f'https://sctapi.ftqq.com/{sckey}.send',
                      data={'title': title, 'desp': '\n'.join(lines)},
                      headers={'User-Agent': 'xiapu-daily'}, timeout=30)
    ok = r.status_code == 200 and r.json().get('code') == 0
    print('Server酱推送：', r.text[:200])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
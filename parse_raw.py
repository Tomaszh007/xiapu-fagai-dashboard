# -*- coding: utf-8 -*-
"""从 raw_docs.json（由 uniCloud 云函数每日 07:50 抓取并提交）生成
   approvals_recent.json 与 Excel —— 复用 crawl_xiapu.py 全部提取逻辑
运行：python parse_raw.py
"""
import json
import os

from crawl_xiapu import (DATE_FROM, OUT_JSON, classify, extract,
                         is_change_approval, write_excel)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'raw_docs.json')


def main():
    if not os.path.exists(RAW):
        raise SystemExit('raw_docs.json 不存在')
    with open(RAW, encoding='utf-8') as f:
        raw = json.load(f)
    docs = raw.get('docs') or []
    print(f"raw_docs.json：{len(docs)} 篇（抓取于 {raw.get('fetched_at', '时间未知')}）")

    rows, excluded, stat = [], [], {}
    for doc in docs:
        pub = (doc.get('docreltime') or '').replace('.', '-')[:10]
        if not pub or pub < DATE_FROM:
            continue
        title = doc.get('doctitle') or ''
        # 变更 / 撤销 / 法人变更类：先行分流备查表（撤销/法人变更不命中分类规则）
        if is_change_approval(title):
            cat = classify(title)[0] or '变更撤销类'
            excluded.append(extract(doc, cat))
            continue
        cat, ok = classify(title)
        if not ok:
            continue
        rows.append(extract(doc, cat))
        stat[cat] = stat.get(cat, 0) + 1

    rows.sort(key=lambda r: r.get('publish_date', ''), reverse=True)
    excluded.sort(key=lambda r: r.get('publish_date', ''), reverse=True)

    import datetime
    write_excel(rows, excluded)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'date_from': DATE_FROM,
                   'date_to': datetime.date.today().isoformat(),
                   'items': rows, 'excluded': excluded}, f,
                  ensure_ascii=False, indent=1)
    total = 0.0
    for r in rows:
        try:
            total += float(r.get('invest_wan') or 0)
        except ValueError:
            pass
    print(f'近半年新批 {len(rows)} 条 {stat}；剔除 {len(excluded)} 条；总投资 {total/10000:.2f} 亿')


if __name__ == '__main__':
    main()
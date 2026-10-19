# -*- coding: utf-8 -*-
"""从 approvals_recent.json 生成交互式看板 HTML（数据内嵌、离线可用）
运行：python build_dashboard.py （在 crawl_xiapu.py 之后执行）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'approvals_recent.json')
OUT = os.path.join(HERE, '霞浦发改批复看板.html')


def to_num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main():
    with open(SRC, encoding='utf-8') as f:
        d = json.load(f)
    raw = d['items']

    items = []
    for i, x in enumerate(raw):
        items.append({
            'i': i,
            'c': x.get('category', ''),
            'n': x.get('project_name', ''),
            'no': x.get('doc_no', ''),
            'd': x.get('publish_date', ''),
            'dd': x.get('doc_date', ''),
            'u': x.get('build_unit', ''),
            'loc': x.get('location', ''),
            'm': to_num(x.get('invest_wan')),
            'dur': x.get('duration', ''),
            'fund': x.get('fund_source', ''),
            'code': x.get('project_code', ''),
            't': x.get('title', ''),
            'url': x.get('url', ''),
            'txt': (x.get('content') or '')[:4000],
        })

    total_amt = sum(it['m'] for it in items)
    payload = json.dumps({'items': items, 'from': d.get('date_from'), 'to': d.get('date_to')},
                         ensure_ascii=False, separators=(',', ':'))

    html = TEMPLATE.replace('__DATA__', payload)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'生成 {OUT}  ({len(html)/1024:.0f} KB, {len(items)} 条)')


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>霞浦县发改局项目批复看板</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { min-height: 100%; scroll-behavior: smooth; }
body {
  position: relative;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", "Noto Sans SC", sans-serif;
  color: #1f2d3d; line-height: 1.7; -webkit-font-smoothing: antialiased;
  max-width: 1400px; margin: 0 auto; padding: 24px 28px;
  background: linear-gradient(160deg, #f8fafc 0%, #ffffff 45%, #cfe0f5 100%);
  min-height: 100vh;
}
body::before {
  content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse 45% 35% at 18% 8%, rgba(255,255,255,0.55) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 88% 90%, rgba(255,255,255,0.45) 0%, transparent 55%);
}
body > * { position: relative; z-index: 1; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0 24px; align-items: start; }
.topnav {
  position: sticky; top: 12px; z-index: 50;
  display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
  padding: 8px 10px; margin: 0 0 8px 0;
  background: rgba(255,255,255,0.94); border: 1px solid #dbe4ef; border-radius: 14px;
  box-shadow: 0 2px 12px rgba(15,30,51,0.08);
}
.topnav a {
  padding: 5px 14px; border-radius: 20px; font-size: 13px;
  color: #5b6b80; text-decoration: none; background: #f8fafc; border: 1px solid transparent;
  transition: color .15s, background .15s, border-color .15s;
}
.topnav a:hover { color: #2563eb; background: #e8f0fe; border-color: #3b82f6; }
.topnav .nav-total { margin-left: auto; font-size: 12px; color: #5b6b80; padding: 0 6px; }
#sec1,#sec2,#sec3,#sec4,#sec5 { scroll-margin-top: 76px; }
.title {
  position: relative; overflow: hidden; padding: 40px 36px; text-align: center;
  background: linear-gradient(135deg, #1e3a5f 0%, #3b82f6 50%, #4f8ef7 100%);
  color: #ffffff; border-radius: 16px; margin-bottom: 18px; box-shadow: 0 4px 20px rgba(0,0,0,0.12);
}
.title::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background:
    radial-gradient(ellipse 70% 55% at 18% 82%, rgba(255,255,255,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 55% 40% at 82% 18%, rgba(255,255,255,0.08) 0%, transparent 55%);
}
.title > * { position: relative; z-index: 1; }
.title h1 { font-size: 28px; font-weight: 800; margin: 0 0 14px 0; letter-spacing: 1px; color: #ffffff; }
.title .accent-line { width: 48px; height: 3px; background: rgba(255,255,255,0.85); margin: 0 auto 18px; border-radius: 2px; }
.title p { font-size: 15px; color: rgba(255,255,255,0.88); margin: 0; line-height: 1.7; }
.title .badge {
  display: inline-block; margin-top: 14px; padding: 4px 14px;
  background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
  border-radius: 20px; font-size: 12px; color: #fff; letter-spacing: 1px;
}
h1.heading { font-size: 24px; color: #0f1e33; margin: 22px 0 14px 0; font-weight: 700; border-left: 4px solid #3b82f6; padding-left: 14px; }
h2.heading { font-size: 20px; color: #0f1e33; margin: 22px 0 10px; padding-bottom: 8px; border-bottom: 2px solid #c9d6f3; font-weight: 600; }
.stat-grid { display: flex; gap: 16px; margin: 0 0 16px 0; }
.stat {
  flex: 1; text-align: center; padding: 20px;
  background: #ffffff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border-top: 3px solid #3b82f6;
}
.stat .num { font-size: 30px; color: #3b82f6; font-weight: 800; line-height: 1.1; }
.stat .num small { font-size: 14px; font-weight: 600; }
.stat .label { font-size: 12px; color: #5b6b80; margin-top: 6px; }
.stat .num.dark { color: #0f1e33; }
.stat .num.warn { color: #d97706; }
.trend-card { background: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin: 0 0 16px 0; }
.trend-card h3 { font-size: 18px; color: #0f1e33; margin: 0 0 8px 0; font-weight: 700; }
.trend-card .note { font-size: 12px; color: #5b6b80; margin: 8px 0 0 0; }
.chart-row { display: flex; gap: 6px; align-items: flex-end; height: 92px; margin: 0 0 10px 0; }
.chart-row .bar { flex: 1; border-radius: 3px 3px 0 0; min-height: 4px; background: linear-gradient(180deg, #3b82f6, #c9d6f3); }
.bar-cell { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; height: 100%; cursor: pointer; }
.bar-cell .bar { width: 100%; flex: none; }
.bar-val { font-size: 12px; font-weight: 700; color: #2563eb; line-height: 1; margin-bottom: 3px; }
.bar-cell:hover .bar { filter: brightness(1.12); }
.bar-cell.active .bar { outline: 2px solid #2563eb; outline-offset: 2px; }
.chart-labels { display: flex; gap: 6px; margin-top: 2px; }
.chart-labels span { flex: 1; text-align: center; font-size: 11px; color: #5b6b80; cursor: pointer; border-radius: 4px; }
.chart-labels span:hover { color: #2563eb; text-decoration: underline; }
.chart-labels span.active { color: #2563eb; font-weight: 700; }
.hbar-row { display: flex; flex-direction: column; gap: 14px; margin-top: 4px; }
.hbar-item { display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 4px 6px; margin: 0 -6px; border-radius: 8px; transition: background .15s; }
.hbar-item:hover { background: #f1f6ff; }
.hbar-item.active { background: #e8f0fe; }
.hbar-item.active .hbar-label b { text-decoration: underline; }
.hbar-label { width: 120px; font-size: 13px; color: #1f2d3d; text-align: right; }
.hbar-label b { color: #3b82f6; font-weight: 800; }
.hbar-track { flex: 1; background: #e8f0fe; border-radius: 6px; height: 18px; overflow: hidden; }
.hbar-fill { height: 100%; border-radius: 6px; }
.table-wrap { background: #ffffff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); overflow: hidden; margin: 0 0 16px 0; }
.table-caption {
  padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap;
  background: linear-gradient(135deg, #c9d6f3, #e8f0fe); color: #0f1e33; font-size: 14px; font-weight: 600;
  border-bottom: 1px solid #dbe4ef;
}
.cap-right { display: flex; align-items: center; gap: 8px; font-weight: 400; font-size: 12px; color: #5b6b80; }
.search-input {
  padding: 6px 12px; border: 1px solid #dbe4ef; border-radius: 20px; font-size: 12.5px;
  color: #1f2d3d; background: #ffffff; outline: none; width: 200px; font-family: inherit;
  transition: border-color .15s, box-shadow .15s;
}
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.12); }
.filter-tag {
  display: none; align-items: center; gap: 6px; padding: 2px 6px 2px 12px;
  background: #ffffff; border: 1px solid #3b82f6; border-radius: 20px; font-size: 12px; font-weight: 600; color: #2563eb;
}
.filter-tag.visible { display: inline-flex; }
.filter-tag .filter-x { border: none; background: transparent; color: #5b6b80; cursor: pointer; font-size: 13px; padding: 0 4px; font-family: inherit; line-height: 1; }
.filter-tag .filter-x:hover { color: #d97706; }
.table-scroll { overflow-x: auto; }
table.table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; min-width: 780px; }
table.table thead th {
  padding: 11px 14px; text-align: left; background: #c9d6f3; color: #0f1e33; font-weight: 700;
  border-bottom: 2px solid #dbe4ef; word-break: break-word; white-space: nowrap; cursor: pointer; user-select: none;
}
table.table thead th:hover { background: #bccdf0; }
table.table thead th .ar { opacity: .35; margin-left: 3px; font-size: 10px; }
table.table thead th.sorted .ar { opacity: 1; color: #2563eb; }
table.table tbody td { padding: 9px 14px; border-bottom: 1px solid #dbe4ef; color: #1f2d3d; word-break: break-word; }
table.table tbody tr { cursor: pointer; transition: background .12s; }
table.table tbody tr:hover { background: #f1f6ff; }
td.nm { max-width: 380px; }
td.nm .t { font-weight: 500; line-height: 1.5; }
td.nm .x { font-size: 11.5px; color: #5b6b80; margin-top: 2px; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; white-space: nowrap; }
.tag-ks { background: #e8f0fe; color: #2563eb; }
.tag-sj { background: #eef5ff; color: #0f1e33; }
.tag-lx { background: #e6f4ea; color: #16a34a; }
.money { font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 500; }
.money.big { color: #d97706; font-weight: 700; }
.date { color: #1f2d3d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.docno { font-size: 11.5px; color: #5b6b80; white-space: nowrap; }
.empty { padding: 44px; text-align: center; color: #5b6b80; font-size: 13px; }
.row-hint { font-size: 11px; color: #8ea0b5; margin-top: 3px; text-align: right; padding: 6px 16px 0; }
.pager { display: flex; gap: 6px; justify-content: center; align-items: center; padding: 12px 16px; border-top: 1px solid #dbe4ef; flex-wrap: wrap; }
.pager-btn { min-width: 32px; height: 32px; padding: 0 10px; border: 1px solid #dbe4ef; background: #ffffff; color: #1f2d3d; font-size: 13px; border-radius: 6px; cursor: pointer; font-family: inherit; transition: border-color .15s, color .15s; }
.pager-btn:hover:not(:disabled):not(.active) { border-color: #3b82f6; color: #2563eb; }
.pager-btn.active { background: #3b82f6; border-color: #3b82f6; color: #ffffff; font-weight: 600; }
.pager-btn:disabled { opacity: .4; cursor: default; }
.pager-info { font-size: 12px; color: #5b6b80; }
.pager-nums { display: flex; gap: 6px; }
.callout { margin: 16px 0; padding: 16px 24px; background: #e8f0fe; border-left: 4px solid #3b82f6; border-radius: 8px; }
.callout p { font-size: 15px; color: #1f2d3d; margin: 0; line-height: 1.8; }
.source-list { margin: 0; }
.source-list ol { padding-left: 20px; font-size: 13px; color: #5b6b80; line-height: 2.0; }
.source-list .src-id { display: inline-block; width: 24px; font-weight: 700; color: #3b82f6; }
.source-list .source-link { color: #2563eb; text-decoration: none; border-bottom: 1px solid rgba(59,130,246,0.35); }
.mask { position: fixed; inset: 0; background: rgba(15,23,42,.42); opacity: 0; pointer-events: none; transition: opacity .22s; z-index: 40; }
.mask.on { opacity: 1; pointer-events: auto; }
.drawer {
  position: fixed; top: 0; right: 0; height: 100%; width: min(680px, 94vw);
  background: #ffffff; z-index: 50; transform: translateX(100%);
  transition: transform .26s cubic-bezier(.4,0,.2,1);
  display: flex; flex-direction: column; box-shadow: -6px 0 24px rgba(15,30,51,.16);
}
.drawer.on { transform: translateX(0); }
.dr-hd { padding: 18px 24px 14px; border-bottom: 1px solid #dbe4ef; background: #f8fafc; }
.dr-hd .row1 { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.dr-hd h3 { font-size: 16.5px; font-weight: 600; line-height: 1.45; color: #0f1e33; padding-right: 26px; }
.dr-close {
  position: absolute; top: 14px; right: 16px; width: 28px; height: 28px; border: none;
  background: transparent; font-size: 20px; color: #5b6b80; cursor: pointer; border-radius: 5px; line-height: 1;
}
.dr-close:hover { background: #e8f0fe; color: #0f1e33; }
.dr-body { flex: 1; overflow-y: auto; padding: 20px 24px 40px; }
.kv { display: grid; grid-template-columns: 82px 1fr; gap: 9px 14px; margin-bottom: 20px; font-size: 13px; }
.kv .k { color: #5b6b80; font-size: 12.5px; }
.kv .v { color: #1f2d3d; word-break: break-all; }
.kv .v b { color: #d97706; font-size: 15px; }
.sec-t { font-size: 12px; color: #5b6b80; letter-spacing: 1px; margin-bottom: 10px; padding-bottom: 7px; border-bottom: 1px dashed #dbe4ef; }
.doc-txt {
  white-space: pre-wrap; font-size: 13.5px; line-height: 1.95; color: #1f2d3d;
  background: #f8fafc; border: 1px solid #e2e9f2; border-radius: 8px; padding: 16px 18px;
}
.dr-ft { padding: 12px 24px; border-top: 1px solid #dbe4ef; background: #f8fafc; display: flex; gap: 10px; align-items: center; }
.dr-ft a {
  display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: #3b82f6;
  color: #fff; border-radius: 6px; text-decoration: none; font-size: 13px; transition: background .15s;
}
.dr-ft a:hover { background: #2563eb; }
@media screen and (max-width: 1080px) { .grid-2 { grid-template-columns: 1fr; gap: 0; } }
@media screen and (max-width: 600px) {
  body { padding: 12px !important; }
  h1 { font-size: 20px !important; } h2 { font-size: 17px !important; }
  .stat-grid { flex-direction: column; }
  .hbar-label { width: 90px; font-size: 12px; }
  .topnav { position: static; }
  .search-input { width: 130px; }
}
@media print {
  body { padding: 0 !important; margin: 0 !important; background: #f4f7fb; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body::before, .topnav, .pager, .search-input { display: none !important; }
  .title { border-radius: 0; box-shadow: none; }
  .stat, .trend-card, .table-wrap { box-shadow: none; border: 1px solid #dbe4ef; }
  .grid-2 { display: block !important; }
  table.table { min-width: 0; }
}
</style>
</head>
<body class="mode-dashboard" data-palette="ink-blue">

<section class="title">
  <h1>霞浦县发改局项目批复看板</h1>
  <div class="accent-line"></div>
  <p id="titleSub">统计周期</p>
  <span class="badge">项目审批动态监控 · 点击明细行查看批复原文</span>
</section>

<nav class="topnav">
  <a href="#sec1">核心指标</a>
  <a href="#sec2">月度趋势</a>
  <a href="#sec3">类型分布</a>
  <a href="#sec4">项目明细</a>
  <a href="#sec5">业务洞察</a>
  <span class="nav-total" id="navTotal"></span>
</nav>

<h1 class="heading" id="sec1">一、核心指标</h1>
<div class="stat-grid" data-cols="4" id="statGrid"></div>
<p class="paragraph" style="font-size:14px;color:#5b6b80;margin:0 0 8px 0;" id="sec1Note"></p>

<div class="grid-2" data-cols="2">
  <div id="sec2">
    <h1 class="heading">二、月度发布趋势</h1>
    <div class="trend-card">
      <h3>近半年各月批复发布数量</h3>
      <div class="chart-row" id="chartRow"></div>
      <div class="chart-labels" id="chartLabels"></div>
      <p class="note">点击柱子或月份标签，可跳到下方明细表并只显示该月批复。</p>
    </div>
  </div>
  <div id="sec3">
    <h1 class="heading">三、批复类型分布</h1>
    <div class="trend-card">
      <h3>可研 / 设计 / 立项批复占比与投资</h3>
      <div class="hbar-row" id="hbarRow"></div>
      <p class="note">点击任意类型条目，可跳到下方明细表并只显示该类批复。</p>
    </div>
  </div>
</div>

<h1 class="heading" id="sec4">四、批复项目明细</h1>
<div class="table-wrap">
  <div class="table-caption">
    <span>霞浦县发改局近半年批复项目清单
      <span class="filter-tag" id="filterTag"><span id="filterText"></span><button class="filter-x" id="filterX" type="button" aria-label="清除筛选">✕</button></span>
    </span>
    <span class="cap-right">
      <input type="search" class="search-input" id="q" placeholder="搜索项目 / 单位 / 文号 / 正文…">
    </span>
  </div>
  <div class="table-scroll">
  <table class="table" id="pfTable">
    <colgroup>
      <col style="width:11%"><col style="width:10%"><col style="width:37%"><col style="width:11%"><col style="width:16%"><col style="width:15%">
    </colgroup>
    <thead>
      <tr>
        <th data-sort="d">发布日期<span class="ar">▼</span></th>
        <th data-sort="c">类型<span class="ar">▼</span></th>
        <th data-sort="n">项目名称 / 建设单位<span class="ar">▼</span></th>
        <th data-sort="m">投资额<span class="ar">▼</span></th>
        <th data-sort="no">文号<span class="ar">▼</span></th>
        <th data-sort="dd">成文日期<span class="ar">▼</span></th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
  </div>
  <div class="row-hint">点击行查看批复正文详情</div>
  <div class="pager">
    <button class="pager-btn" id="pfPrev" aria-label="上一页">上一页</button>
    <div class="pager-nums" id="pfNums"></div>
    <button class="pager-btn" id="pfNext" aria-label="下一页">下一页</button>
    <span class="pager-info" id="pfInfo"></span>
  </div>
</div>

<div class="grid-2" data-cols="2">
  <div id="sec5">
    <h1 class="heading">五、业务洞察</h1>
    <aside class="callout" data-variant="tip">
      <p id="insightText"></p>
    </aside>
  </div>
  <div>
    <h2 class="heading">主要数据来源</h2>
    <div class="source-list">
      <ol class="list">
        <li id="source-1"><span class="src-id">[1]</span> <a class="source-link" href="http://www.xiapu.gov.cn/zwgk/gkzl/bmzfxxgk/zfbm/xfzhggj/gkml/zdgkxx/" target="_blank">霞浦县人民政府·霞浦县发展和改革局「政策文件」栏目</a>，批复文件全文（抓取时间 <span id="genTime"></span>）</li>
      </ol>
    </div>
  </div>
</div>

<div class="mask" id="mask"></div>
<div class="drawer" id="drawer">
  <button class="dr-close" id="drClose" aria-label="关闭">×</button>
  <div class="dr-hd">
    <div class="row1" id="drTags"></div>
    <h3 id="drTitle"></h3>
  </div>
  <div class="dr-body" id="drBody">
    <div class="kv" id="drKv"></div>
    <div class="sec-t">批复正文</div>
    <div class="doc-txt" id="drTxt"></div>
  </div>
  <div class="dr-ft">
    <a id="drLink" href="#" target="_blank" rel="noopener">查看原文 ↗</a>
  </div>
</div>

<script>
const DB = __DATA__;
const ITEMS = DB.items;
const $ = id => document.getElementById(id);
const esc = s => String(s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function money(v){ return v>0 ? (v>=10000 ? (v/10000).toFixed(2).replace(/\.?0+$/,'')+' 亿' : (v%1 ? v.toFixed(2) : v.toFixed(0))+' 万') : '—'; }

/* ===== 聚合 ===== */
const num = v => +v || 0;
const byMonth = {}, byCat = {};
ITEMS.forEach(it => {
  const m = it.d.slice(0,7);
  byMonth[m] = byMonth[m] || {n:0, amt:0}; byMonth[m].n++; byMonth[m].amt += it.m;
  byCat[it.c] = byCat[it.c] || {n:0, amt:0}; byCat[it.c].n++; byCat[it.c].amt += it.m;
});
const months = Object.keys(byMonth).sort();
const totalAmt = ITEMS.reduce((s,it)=>s+it.m,0);
const invItems = ITEMS.filter(it=>it.m>0);

/* ===== 指标卡 ===== */
$('statGrid').innerHTML = [
  ['<div class="num">'+ITEMS.length+'</div><div class="label">近半年新批批复</div>'],
  ['<div class="num dark">'+(byCat['可研批复']||{n:0}).n+'</div><div class="label">可研批复</div>'],
  ['<div class="num">'+(byCat['设计批复']||{n:0}).n+'</div><div class="label">设计批复</div>'],
  ['<div class="num dark">'+(byCat['立项批复']||{n:0}).n+'</div><div class="label">立项批复（建议书）</div>'],
  ['<div class="num warn">'+(totalAmt/10000).toFixed(2)+'<small> 亿元</small></div><div class="label">批复总投资（'+invItems.length+'/'+ITEMS.length+' 条含投资额）</div>'],
].map(h=>'<div class="stat">'+h[0]+'</div>').join('');
$('navTotal').textContent = '近半年 '+ITEMS.length+' 条新批批复 · 总投资约 '+(totalAmt/10000).toFixed(1)+' 亿元 · 数据截至 '+DB.to;
$('titleSub').textContent = '统计周期：'+DB.from+' 至 '+DB.to+' · 霞浦县发展和改革局「政策文件」栏目';
$('sec1Note').textContent = '已剔除变更 / 撤销 / 法人变更类批复（备查见 Excel「变更撤销类备查」表），本页仅统计新批项目，投资额取自批复正文"总投资/投资估算"。';
const maxM = months.length ? Math.max(...months.map(m=>byMonth[m].n)) : 1;
const maxCnt = Math.max(1, ...Object.values(byCat).map(c=>c.n), ...Object.values(byCat).map(c=>Math.round(c.amt/10000)));

/* ===== 月度柱状图 ===== */
const BAR_H = 75; // 最高柱像素
$('chartRow').innerHTML = months.map(m =>
  '<div class="bar-cell" data-month="'+m+'" role="button" tabindex="0" title="'+m+'：'+byMonth[m].n+' 条 · 投资 '+(byMonth[m].amt/10000).toFixed(2)+' 亿">'
  + '<span class="bar-val">'+byMonth[m].n+'</span>'
  + '<div class="bar" style="height:'+Math.max(4, Math.round(byMonth[m].n/maxM*BAR_H))+'px;"></div></div>').join('');
$('chartLabels').innerHTML = months.map(m =>
  '<span data-month="'+m+'">'+parseInt(m.slice(5),10)+'月</span>').join('');

/* ===== 类型横条（数量+投资额双视图：条宽按投资额，标签显示数量） ===== */
const catColors = {'可研批复':'linear-gradient(90deg,#2563eb,#c9d6f3)','设计批复':'linear-gradient(90deg,#3b82f6,#e8f0fe)','立项批复':'linear-gradient(90deg,#14b8a6,#d1fae5)'};
$('hbarRow').innerHTML = Object.keys(byCat).map(c =>
  '<div class="hbar-item" data-type="'+c+'" role="button" tabindex="0" title="点击筛选'+c+'">'
  + '<div class="hbar-label">'+c+' <b>'+byCat[c].n+'</b></div>'
  + '<div class="hbar-track"><div class="hbar-fill" style="width:'+Math.max(6, Math.round(byCat[c].n/maxCnt*100))+'%;background:'+(catColors[c]||'#3b82f6')+';"></div></div>'
  + '<div class="money" style="width:72px;text-align:right;font-size:12px;color:#5b6b80;">'+(byCat[c].amt>0 ? (byCat[c].amt/10000).toFixed(2)+'亿' : '—')+'</div></div>').join('');

/* ===== 状态与渲染 ===== */
let state = { month:'', cat:'', q:'', sort:'d', desc:true, page:1 };
const PER = 10;
let filtered = [];

ITEMS.forEach(it => { it._s = (it.n+' '+it.u+' '+it.no+' '+it.t+' '+it.txt).toLowerCase(); });

function apply(){
  const kw = state.q.trim().toLowerCase();
  filtered = ITEMS.filter(it => {
    if (state.month && it.d.slice(0,7) !== state.month) return false;
    if (state.cat && it.c !== state.cat) return false;
    if (kw && !kw.split(/\s+/).every(w => it._s.includes(w))) return false;
    return true;
  });
  const k = state.sort, dir = state.desc ? -1 : 1;
  filtered.sort((a,b) => {
    if (k === 'm') return (a.m - b.m) * dir;
    const av = a[k]||'', bv = b[k]||'';
    return av < bv ? -dir : av > bv ? dir : 0;
  });
}

function render(){
  apply();
  const total = filtered.length;
  const pages = Math.max(1, Math.ceil(total / PER));
  if (state.page > pages) state.page = pages;
  const s = (state.page-1)*PER;
  const view = filtered.slice(s, s+PER);

  if (!total) {
    $('tbody').innerHTML = '<tr><td colspan="6"><div class="empty">没有符合条件的批复，试试放宽筛选条件</div></td></tr>';
  } else {
    $('tbody').innerHTML = view.map(it => {
      const cls = it.c==='可研批复'?'tag-ks':it.c==='设计批复'?'tag-sj':'tag-lx';
      return '<tr data-id="'+it.i+'">'
        + '<td class="date">'+it.d+'</td>'
        + '<td><span class="tag '+cls+'">'+it.c+'</span></td>'
        + '<td class="nm"><div class="t">'+esc(it.n)+'</div><div class="x">'+esc(it.u||'单位待公开')+'</div></td>'
        + '<td class="money'+(it.m>=10000?' big':'')+'">'+money(it.m)+'</td>'
        + '<td class="docno">'+esc(it.no||'—')+'</td>'
        + '<td class="date">'+(it.dd||'—')+'</td>'
        + '</tr>';
    }).join('');
  }

  const btns = [];
  let st = Math.max(1, state.page-2), en = Math.min(pages, st+4); st = Math.max(1, en-4);
  for (let p=st; p<=en; p++) btns.push('<button type="button" class="pager-btn'+(p===state.page?' active':'')+'" data-p="'+p+'">'+p+'</button>');
  $('pfNums').innerHTML = btns.join('');
  $('pfPrev').disabled = state.page === 1;
  $('pfNext').disabled = state.page === pages;
  $('pfInfo').textContent = '第 '+(s+1)+'–'+Math.min(s+PER,total)+' 条 · 共 '+total+' 条 · 第 '+state.page+'/'+pages+' 页';

  document.querySelectorAll('.bar-cell, .chart-labels span[data-month]').forEach(el =>
    el.classList.toggle('active', !!state.month && el.getAttribute('data-month') === state.month));
  document.querySelectorAll('.hbar-item').forEach(el =>
    el.classList.toggle('active', !!state.cat && el.getAttribute('data-type') === state.cat));
  document.querySelectorAll('thead th[data-sort]').forEach(th => {
    th.classList.toggle('sorted', th.dataset.sort === state.sort);
    const ar = th.querySelector('.ar');
    if (ar) ar.textContent = th.dataset.sort === state.sort ? (state.desc ? '▼' : '▲') : '▼';
  });
}

/* ===== 筛选交互 ===== */
let lastCall = null;
function setFilter(k, v){
  const now = Date.now();
  if (lastCall && lastCall.k===k && lastCall.v===v && now-lastCall.t < 600) { lastCall.t = now; return; }
  lastCall = { k, v, t: now };
  const cur = k==='m' ? state.month : state.cat;
  if (k==='m') state.month = (cur===v) ? '' : v;
  else state.cat = (cur===v) ? '' : v;
  syncFilterTag();
  state.page = 1;
  render();
  $('sec4').scrollIntoView({behavior:'smooth'});
}
function syncFilterTag(){
  const t = state.month ? state.month.slice(0,4)+'年'+parseInt(state.month.slice(5),10)+'月' : state.cat;
  $('filterText').textContent = t || '';
  $('filterTag').classList.toggle('visible', !!(state.month || state.cat));
}
document.querySelectorAll('.bar-cell, .chart-labels span[data-month]').forEach(el =>
  el.addEventListener('click', () => setFilter('m', el.getAttribute('data-month'))));
document.querySelectorAll('.hbar-item').forEach(el =>
  el.addEventListener('click', () => setFilter('t', el.getAttribute('data-type'))));
$('filterX').addEventListener('click', () => { state.month=''; state.cat=''; syncFilterTag(); state.page=1; render(); });

let timer;
$('q').addEventListener('input', e => {
  clearTimeout(timer);
  timer = setTimeout(() => { state.q = e.target.value; state.page = 1; render(); }, 180);
});
document.querySelectorAll('thead th[data-sort]').forEach(th =>
  th.addEventListener('click', () => {
    const k = th.dataset.sort;
    if (state.sort === k) state.desc = !state.desc;
    else { state.sort = k; state.desc = true; }
    render();
  }));
$('pfPrev').addEventListener('click', () => { state.page--; render(); });
$('pfNext').addEventListener('click', () => { state.page++; render(); });
$('pfNums').addEventListener('click', e => {
  const b = e.target.closest('button[data-p]'); if (!b) return;
  state.page = +b.dataset.p; render();
});

/* ===== 详情抽屉 ===== */
const drawer = $('drawer'), mask = $('mask');
function openDetail(id){
  const it = ITEMS.find(x => x.i === +id); if (!it) return;
  const cls = it.c==='可研批复'?'tag-ks':it.c==='设计批复'?'tag-sj':'tag-lx';
  $('drTags').innerHTML = '<span class="tag '+cls+'">'+it.c+'</span><span style="font-size:12.5px;color:#5b6b80">'+it.d+' 发布</span>';
  $('drTitle').textContent = it.n || it.t;
  $('drKv').innerHTML = [
    ['批复文号', esc(it.no || '—')],
    ['建设单位', esc(it.u || '—')],
    ['建设地点', esc(it.loc || '—')],
    ['总投资', it.m ? '<b>'+money(it.m)+'元</b>' : '—'],
    ['建设工期', esc(it.dur || '—')],
    ['资金来源', esc(it.fund || '—')],
    ['项目代码', esc(it.code || '—')],
    ['成文日期', esc(it.dd || '—')],
    ['原文标题', esc(it.t || '—')],
  ].map(([k,v]) => '<div class="k">'+k+'</div><div class="v">'+v+'</div>').join('');
  $('drTxt').textContent = it.txt ? it.txt + (it.txt.length >= 4000 ? '\n\n……（正文已截断，完整内容请查看原文）' : '') : '（无正文）';
  $('drLink').href = it.url || '#';
  drawer.classList.add('on'); mask.classList.add('on');
  $('drBody').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}
function closeDetail(){
  drawer.classList.remove('on'); mask.classList.remove('on');
  document.body.style.overflow = '';
}
$('tbody').addEventListener('click', e => {
  const tr = e.target.closest('tr[data-id]'); if (tr) openDetail(tr.dataset.id);
});
$('drClose').addEventListener('click', closeDetail);
mask.addEventListener('click', closeDetail);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

/* ===== 洞察 ===== */
let peak = months.length ? months.reduce((a,b)=>byMonth[a].n>=byMonth[b].n?a:b) : '';
const topInv = ITEMS.slice().sort((a,b)=>b.m-a.m)[0];
$('insightText').innerHTML = '近半年新批批复 '+ITEMS.length+' 条、批复总投资约 <b>'+(totalAmt/10000).toFixed(2)+' 亿元</b>；'
  + (peak ? parseInt(peak.slice(5),10)+' 月为批复高峰（'+byMonth[peak].n+' 条）。' : '')
  + (topInv && topInv.m>0 ? '单体投资最大项目为「'+esc(topInv.n)+'」（'+money(topInv.m)+'元）。按惯例批复后 1-3 个月内将陆续启动勘察、设计、监理及施工招标，建议重点关注「设计批复」下发项目的后续招标公告。' : '');

$('genTime').textContent = DB.to;
render();
</script>

</body>
</html>
'''


if __name__ == '__main__':
    main()
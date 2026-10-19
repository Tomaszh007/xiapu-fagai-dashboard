# 霞浦县发改局项目批复监控

每日自动抓取霞浦县人民政府网 · 县发改局「政策文件」栏目发布的**可研批复 / 设计批复 / 立项（项目建议书）**批复文件（近半年，剔除变更/撤销/法人变更类），自动提取投资额、建设单位、建设地点、工期、资金来源、项目代码等字段。

## 每日产出

- **交互看板**（GitHub Pages 在线版）：指标卡、月度趋势、类型分布、明细表（筛选/排序/全文搜索/点击查看批复原文）
- **日报图 + 日报推送**：每天 08:00（北京时间）通过 Server酱 推送到微信
- **数据文件**：Excel（主表 + 变更撤销类备查表）、JSON 明细（含批复正文）

## 在线看板

打开 GitHub Pages 链接（见仓库 Settings → Pages，或最新一次运行日志）。

## 本地运行

```bash
pip install -r requirements.txt
python crawl_xiapu.py        # 抓取 → Excel + JSON
python build_dashboard.py    # 生成交互看板 HTML
python gen_daily_image.py    # 生成日报图 PNG
```

## 自动化

`.github/workflows/daily.yml`：GitHub Actions 每日 08:00（北京时间）自动执行全流程并发布到 Pages。

数据来源为政府公开信息，仅供参考，以官方原文为准。

> AI生成

# Arxiv 每日论文爬取 + AI 解析方案

## Notes
> Arxiv 于 美国东部时间 00:00:00 (UTC−5) == 中国时间 13:00:00 CST（同一天，下午 1 点）推送当日的 `new submission`

## Notes
- 如果有Tex文件,优先向ai发送tex文件内容,避免pdf公式解析错误
- source中有图片会被转化成base64发送给ai,非pdf格式图片>3M会被忽略
- 如果没有tex文件,则把pdf转换成图片发送给AI
- 最大向AI发送`MAX_FIGURE_NUM`张图片 可通过环境变量配置

## Notes
- 分类器 定义 `JUDGER_MODEL` 和 `RESEARCH_PERFER` 来判断是否要深入阅读,减少无用阅读量和`token` 
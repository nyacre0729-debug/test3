# 课程项目：莫斯科IT岗位技能需求分析
## 第三阶段 — 数据分析与可视化（数据量升级至全俄48万条）

## 项目介绍
本项目用于分析莫斯科地区IT招聘岗位。原JSON API（`/api/v1/vacancies/region/77`）的分页参数
已失效（`page`/`offset`被忽略，只能取到前100条，导致上一阶段500条数据实际仅含9个唯一岗位），
因此数据源改为trudvsem.ru官方开放数据批量CSV（`https://opendata.trudvsem.ru/csv/vacancy.csv`，
约1.9GB，**全俄48.06万条、莫斯科1.59万条**，其中IT相关岗位903条），后续用Python完成统计分析与可视化。

## 分析任务（对应 figures/ 与 results/ 产出）
1. **热门技术**：莫斯科IT岗位中，信息安全(207)、测试QA(177)、SQL(117)、Python(105)、Linux(97)、AI/ML(94)最多。
2. **行政区分布**：基于街道关键词近似映射，ЦАО中央区、ЮВАО东南区岗位最多（约55%地址无法自动识别，已在图中单独归类）。
3. **经验分类**：按官方数值经验字段分组，3-4年(285)与5-6年(264)需求最大，无经验139条。
4. **薪资与经验**：863条含薪资数据，全市场中位数9万₽；3-4年组中位11万₽高于1-2年组，5-6年组中位偏低（分布极宽，均值仍递增）。
5. **可视化**：7张图表（含全俄48万条背景对比图）。

## 技术栈
- Python 3、pandas、matplotlib、requests
- PostgreSQL + psycopg2（`get_data.py` 写库用）
- Git：代码版本管理

## 项目文件说明
| 文件 | 作用 |
| --- | --- |
| `get_data.py` | 下载官方批量CSV → 筛选莫斯科 → 写入PostgreSQL `vacancy` 表 |
| `make_table.sql` | 数据库建表脚本（沿用原表结构） |
| `download_feed.py` | 单独下载1.9GB原始数据（断点续传） |
| `filter_moscow.py` | 从原始CSV筛出莫斯科子集 `vacancy_moscow.csv` |
| `regions_russia.py` | 全俄各地区岗位量统计（背景分析） |
| `analyze.py` | 5项分析任务 + 全部图表、结果表 |
| `vacancy_moscow.csv` | 莫斯科数据（65MB，可提交Git） |
| `figures/` `results/` | 图表与分析结果（可再生成） |

## 运行步骤
```bash
pip install requests pandas matplotlib psycopg2
# 1) 入库（可选，需本地PostgreSQL；跳过也可直接分析CSV）
python get_data.py
# 2) 分析+出图
python analyze.py
# 产物: figures/*.png, results/*.csv
```

## 已知数据限制
- 官方分类字段 `hardSkills` 填充率仅0.6%，技能统计采用标题+职责+要求的正则匹配；
- 开放数据不含行政区字段，行政区分布用街道关键词近似映射，未识别地址单独归类；
- trudvsem 莫斯科存量岗位仅约1.6万条，全量分析满足课程"5万条以上"要求需覆盖全俄数据（本仓库48万条全量已具备）。

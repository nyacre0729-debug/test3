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

**发行版直接运行（无需下载、无需入库）**：发行版自带 `vacancy_moscow_it.csv`（903 条莫斯科 IT-вакансии，约 4.4MB，`|` 分隔，UTF-8），`analyze.py` 会自动找到它，一条命令即可复现 `analyze.py` 产出的全部图表（00–06）与结果表：
```bash
pip install pandas matplotlib
python analyze.py
```
也可用 Docker：`docker compose up --build --abort-on-container-exit`。

`analyze.py` 按顺序查找数据文件：环境变量 `VACANCY_CSV` → `vacancy_moscow.csv` → `data/vacancy_moscow.csv` → `vacancy_moscow_it.csv`，运行时会打印实际使用的文件与行数；全部找不到时给出中俄文提示。

完整莫斯科数据（15 876 条 / 65MB，即 `vacancy_moscow.csv`）需用 `python filter_moscow.py` 从 1.9GB 官方выгрузка `vacancy_full.csv` 生成，两者均不随仓库提供。同一份 903 条子集可完整复现 `analyze.py` 产出的 `figures/` 与 `results/`，结果与文章一致。

注意：`predict.py`（生成 `figures/07_salary_prediction.png`、`figures/08_salary_vs_exp.png` 与 `results/prediction.csv`）目前仍硬编码读取 `vacancy_moscow.csv`，在仅含 903 条子集的发行版中无法重新运行，发行版中这些文件为已生成的结果。

## 已知数据限制
- 官方分类字段 `hardSkills` 填充率仅0.6%，技能统计采用标题+职责+要求的正则匹配；
- 开放数据不含行政区字段，行政区分布用街道关键词近似映射，未识别地址单独归类；
- trudvsem 莫斯科存量岗位仅约1.6万条，全量分析满足课程"5万条以上"要求需覆盖全俄数据（本仓库48万条全量已具备）。

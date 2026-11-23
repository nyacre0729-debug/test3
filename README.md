# 课程项目：莫斯科IT岗位技能需求分析
## 第三阶段 — 数据分析与可视化（数据源升级为官方全量выгрузка：全俄48万条用于背景统计，莫斯科IT分析样本903条）

## 项目介绍
本项目用于分析莫斯科地区IT招聘岗位。原JSON API（`/api/v1/vacancies/region/77`）的分页参数
已失效（`page`/`offset`被忽略，只能取到前100条，导致上一阶段500条数据实际仅含9个唯一岗位），
因此数据源改为trudvsem.ru官方开放数据批量CSV（`https://opendata.trudvsem.ru/csv/vacancy.csv`，
约1.9GB，**全俄48.06万条、莫斯科1.59万条**，其中IT相关岗位903条），后续用Python完成统计分析与可视化。

## 分析任务（对应 figures/ 与 results/ 产出）
1. **热门技术**：莫斯科IT岗位中，信息安全(207)、测试QA(177)、SQL(117)、Python(105)、Linux(97)、AI/ML(94)最多。
2. **行政区分布**：基于街道关键词近似映射，ЦАО中央区、ЮВАО东南区岗位最多（约55%地址无法自动识别，已在图中单独归类）。
3. **经验分类**：按官方数值经验字段分组，3-4年(285)与5-6年(264)需求最大，无经验139条。
4. **薪资与经验**：863条含薪资数据，全市场中位数9万₽；3-4年组中位11万₽高于1-2年组，5-6年组中位7万₽低于1-2年组（中位8.5万₽）；均值上3-4年组（12.8万₽）与5-6年组（12.6万₽）接近，分布极宽。
5. **可视化**：`analyze.py` 输出 `figures/00–06` 共7张图（00为全俄背景对比图，读取入库的 `results/regions_russia.csv`）；`predict.py` 输出 `figures/07–08` 共2张图；ER 图3张（见 ARCHITECTURE.md §2）。
6. **薪资预测**：线性回归（log10 薪资 ~ 经验、技能数、岗位级别、高等教育），R²=0,173，MAE≈55 318₽，n=863（`predict.py`）。

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
| `analyze.py` | 5项分析任务 + 全部图表、结果表（输出 figures/00–06 与 results/ 下六张分析表） |
| `predict.py` | 薪资回归预测（线性回归，输出 figures/07、08 与 results/prediction.csv） |
| `vacancy_moscow.csv` | 莫斯科全量数据（15 876 条，65MB）：由 `filter_moscow.py` 从 `vacancy_full.csv` 生成，已被 .gitignore 排除，不入库 |
| `vacancy_full.csv` | 官方全俄批量выгрузка（约 1.9GB，48.06 万条），由 `download_feed.py` 断点续传下载；已被 .gitignore 排除，不入库 |
| `vacancy_moscow_it.csv` | 发行版自带的 903 条莫斯科 IT 样本（入库），供演示与复现 |
| `vacancy.csv` | 第一阶段 API 翻页采集的 500 行示例（пример，逗号分隔，仅 9 个唯一岗位）；不被任何脚本读取，不参与分析 |
| `er_diagram.py` | 生成 `figures/ER_diagram.png`（源字段到数据表的映射图） |
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

**发行版直接运行（无需下载、无需入库）**：发行版自带 `vacancy_moscow_it.csv`（903 条莫斯科 IT-вакансии，约 4.4MB，`|` 分隔，UTF-8）。`analyze.py` 与 `predict.py` 都会按顺序查找数据文件：环境变量 `VACANCY_CSV` → `vacancy_moscow.csv` → `data/vacancy_moscow.csv` → `vacancy_moscow_it.csv`，运行时打印实际使用的文件与行数；全部找不到时给出中俄文提示并退出。
```bash
pip install pandas matplotlib scikit-learn
python analyze.py   # 产出 figures/00–06 共七张图 + results/ 下六张分析表
python predict.py   # 产出 figures/07_salary_prediction.png、figures/08_salary_vs_exp.png、results/prediction.csv
```
Docker：`docker compose up --build --abort-on-container-exit` 只运行 `analyze.py`，复现 `figures/00–06`（七张图）与 `results/` 下六张分析表。**`predict.py` 的产物（07、08、prediction.csv）不在这一条命令内，需单独运行（见上）**，所以完整产物需要两步。若宿主机 5432 端口已被占用，改用 `DB_PORT=5433 docker compose up --build --abort-on-container-exit`（PowerShell 中为 `$env:DB_PORT=5433; docker compose up ...`）；`DB_PORT` 只改变 compose 中 db 服务的宿主机端口映射，`get_data.py` 仍连接 5432。上述 Docker 流程已在 Docker 中实测通过。

完整莫斯科数据（15 876 条 / 65MB，即 `vacancy_moscow.csv`）需用 `python filter_moscow.py` 从 1.9GB 官方выгрузка `vacancy_full.csv` 生成，两者均不随仓库提供（已被 .gitignore 排除）。仓库中的 `figures/` 与 `results/` 即由这份 903 条子集经 `analyze.py` 与 `predict.py` 产出（predict 的 n=863、R²=0,173、MAE≈55 318₽ 已复算核对）；若改用全量 `vacancy_moscow.csv`，数值会不同，与仓库产物不再对应。

## 已知数据限制
- 官方分类字段 `hardSkills` 填充率仅0.6%，技能统计采用标题+职责+要求的正则匹配；
- 开放数据不含行政区字段，行政区分布用街道关键词近似映射，未识别地址单独归类；
- 数据体量：课程要求的"5万条以上"在联邦层面满足——trudvsem 全俄批量выгрузка共 **480 576 条**（原始 `vacancy_full.csv` 不入库；全俄数据用于背景统计，经 `regions_russia.py` → `results/regions_russia.csv` → `figures/00`）。莫斯科目录为 **15 876 条**，单独看莫斯科层面未达 5 万条。
- 分析对象为 **903 条 IT 岗位**，这是全集而非抽样：它是按行业字段与职位关键词规则从莫斯科目录中筛出的全部 IT 岗位，研究对象本身即该全集。筛选规则的误纳与漏检见文章"限制"部分；单个细分组样本较小（如"6 年以上"仅 6 条），其统计结论强度受限。

## Материалы проекта
课程项目的论文与答辩演示位于 `docs/`（仓库内副本，与最终提交成品一致）：
- `docs/02_Article_Moscow-IT-Vacancies.doc` — 论文（Word 97–2003，16 页，3 852 词）
- `docs/03_Presentation_Moscow-IT-Vacancies.ppt` — 答辩演示（PowerPoint 97–2003，16 页，每页带演讲备注）

DL 交付包 `Moscow-IT-Vacancies.zip` 结构（根目录恰好 5 个文件，无子文件夹）：
1. `01_Authors.txt` — 作者与组号
2. `02_Article_Moscow-IT-Vacancies.doc` — 论文
3. `03_Presentation_Moscow-IT-Vacancies.ppt` — 答辩演示
4. `04_GitHub.txt` — 本仓库地址
5. `05_Distribution.zip` — 发行版（本仓库内容的打包：代码、vacancy_moscow_it.csv、figures/、results/、Dockerfile 等）

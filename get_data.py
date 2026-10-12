# get_data.py — 下载 trudvsem.ru 官方批量数据(全俄48万条)，筛选莫斯科岗位并写入PostgreSQL
# 原JSON API (/api/v1/vacancies/region/77) 的分页参数已全部失效(page/offset被忽略，最多取前100条)，
# 故数据源改为官方开放数据CSV批量下载: https://opendata.trudvsem.ru/csv/vacancy.csv
import os
import requests
import psycopg2
import psycopg2.extras

# ---------- 配置 ----------
FEED_URL = "https://opendata.trudvsem.ru/csv/vacancy.csv"
RAW_FILE = "vacancy_full.csv"
DB_NAME = "vacancy_db"
DB_USER = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"
MOSCOW_OKTMO = "7700000000000"   # 莫斯科州代码

# ---------- 1. 下载（支持断点续传） ----------
def download():
    resume = os.path.getsize(RAW_FILE) if os.path.exists(RAW_FILE) else 0
    headers = {"Range": f"bytes={resume}-"} if resume else {}
    r = requests.get(FEED_URL, headers=headers, stream=True, timeout=60)
    if resume and r.status_code != 206:
        resume, r = 0, requests.get(FEED_URL, stream=True, timeout=60)
    total = resume + int(r.headers.get("Content-Length") or 0) or 1_891_926_352
    with open(RAW_FILE, "ab" if resume else "wb") as f:
        done = resume
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if done - resume >= 100_000_000 or (done == total and done):
                print(f"{done/1e6:.0f}/{total/1e6:.0f} MB", flush=True)
                resume = done
    print("下载完成")

if not os.path.exists(RAW_FILE):
    download()

# ---------- 2. 读取并筛选莫斯科 ----------
import pandas as pd

COLS = ["vacancyName", "fullCompanyName", "vacancyAddress", "salaryMin", "salaryMax",
        "experienceRequirements", "responsibilities", "positionRequirements", "datePublished"]
exp_map = {0: "Без опыта", 1: "От 1 года до 3 лет", 2: "От 1 года до 3 лет",
           3: "От 3 до 6 лет", 4: "От 3 до 6 лет", 5: "От 3 до 6 лет", 6: "Более 6 лет"}

frames = []
for i, chunk in enumerate(pd.read_csv(RAW_FILE, sep="|", dtype=str, chunksize=300_000,
                                      encoding="utf-8", on_bad_lines="skip")):
    sub = chunk[chunk["stateRegionCode"] == MOSCOW_OKTMO]
    if len(sub):
        frames.append(sub)
    print(f"已扫描第{i+1}块, 累计莫斯科 {sum(len(f) for f in frames)} 条", flush=True)

msk = pd.concat(frames, ignore_index=True)
msk["experience"] = msk["experienceRequirements"].apply(
    lambda x: exp_map.get(int(float(x)) if str(x).replace('.', '', 1).isdigit() else -1, "Не указано"))
msk["description"] = (msk["responsibilities"].fillna("") + "\n"
                      + msk["positionRequirements"].fillna("")).str.strip()
msk["id"] = range(1, len(msk) + 1)
rows = list(msk[["id", "vacancyName", "fullCompanyName", "vacancyAddress", "salaryMin",
                 "salaryMax", "experience", "description", "datePublished"]].itertuples(index=False, name=None))

def to_int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None

rows = [(r[0], r[1], r[2], r[3], to_int(r[4]), to_int(r[5]), r[6], r[7], r[8]) for r in rows]

# ---------- 3. 写入PostgreSQL（表结构沿用 make_table.sql 的 vacancy 表） ----------
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
                        host=DB_HOST, port=DB_PORT)
cur = conn.cursor()
cur.execute("TRUNCATE TABLE vacancy;")
psycopg2.extras.execute_values(cur, """
    INSERT INTO vacancy(id, title, company, city_district, salary_min, salary_max,
                        experience, description, published_at)
    VALUES %s""", rows, page_size=2000)
conn.commit()
print(f"已写入 {cur.rowcount} 条莫斯科岗位到 vacancy 表")
cur.close()
conn.close()

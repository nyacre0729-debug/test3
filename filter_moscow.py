# filter_moscow.py — 从全俄CSV筛出莫斯科记录 + 行业字段摸底
import pandas as pd

CHUNK = 300_000
first = True
total = 0
msk = 0
spheres = pd.Series(dtype=int)
for chunk in pd.read_csv("vacancy_full.csv", sep="|", dtype=str, chunksize=CHUNK,
                         low_memory=False, encoding="utf-8", on_bad_lines="skip"):
    total += len(chunk)
    spheres = spheres.add(chunk["professionalSphereName"].value_counts(dropna=False), fill_value=0)
    sub = chunk[chunk["stateRegionCode"] == "7700000000000"]
    if len(sub):
        sub.to_csv("vacancy_moscow.csv", mode="w" if first else "a",
                   header=first, index=False, encoding="utf-8", sep="|")
        first = False
        msk += len(sub)
    print(f"已扫描 {total/1e6:.2f}M 行, 莫斯科累计 {msk}", flush=True)

print(f"\n全俄总行数: {total}, 莫斯科行数: {msk}")
print("\n[professionalSphereName TOP20]")
print(spheres.sort_values(ascending=False).head(20).to_string())

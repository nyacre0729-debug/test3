# regions_russia.py — 统计全俄各地区岗位数（背景数据）
import pandas as pd

counts = pd.Series(dtype=int)
for chunk in pd.read_csv("vacancy_full.csv", sep="|", dtype=str, chunksize=300_000,
                         low_memory=False, encoding="utf-8", on_bad_lines="skip",
                         usecols=["regionName", "stateRegionCode"]):
    counts = counts.add(chunk["regionName"].value_counts(), fill_value=0)
    print("已扫描", int(counts.sum()), flush=True)

top = counts.sort_values(ascending=False)
top.to_frame("vacancies").to_csv("results/regions_russia.csv", encoding="utf-8-sig")
print(top.head(15).to_string())

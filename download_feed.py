# download_feed.py — 下载 trudvsem.ru 全俄空缺批量CSV（1.9GB，支持断点续传）
import os
import requests

URL = "https://opendata.trudvsem.ru/csv/vacancy.csv"
DEST = "vacancy_full.csv"

resume = os.path.getsize(DEST) if os.path.exists(DEST) else 0
headers = {"Range": f"bytes={resume}-"} if resume else {}
mode = "ab" if resume else "wb"

r = requests.get(URL, headers=headers, stream=True, timeout=60)
if resume and r.status_code != 206:
    resume, mode = 0, "wb"
total = resume + int(r.headers.get("Content-Length") or 0) or 1_891_926_352
print(f"开始下载: 已有 {resume/1e6:.0f} MB / 共 {total/1e6:.0f} MB")

done = resume
next_tip = done + 50_000_000
with open(DEST, mode) as f:
    for chunk in r.iter_content(chunk_size=1 << 20):
        f.write(chunk)
        done += len(chunk)
        if done >= next_tip:
            print(f"{done/1e6:.0f}/{total/1e6:.0f} MB ({done/total*100:.1f}%)", flush=True)
            next_tip = done + 50_000_000

print("下载完成:", done, "bytes")

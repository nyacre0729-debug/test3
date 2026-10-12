# analyze.py — Анализ IT-вакансий Москвы (данные: trudvsem.ru, 480 тыс. по РФ / 15,9 тыс. Москва)
# Задачи курса: 1) топ-технологии 2) округа 3) опыт 4) зарплата×опыт 5) визуализация
import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["axes.unicode_minus"] = False

OUT_DIR, RES_DIR = "figures", "results"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

df = pd.read_csv("vacancy_moscow.csv", sep="|", dtype=str, encoding="utf-8")
print(f"Всего вакансий в Москве: {len(df)}")

# ---------- 0. Отбор IT-вакансий ----------
IT_TITLE_PAT = (r"программист|разработчик|python|java|c\+\+|c#|\.net|devops|qa|тестир"
                r"|аналитик|data|баз данн|sql|1c|1с|системн\w+ админ|сисадмин"
                r"|ит-специалист|it-специалист|инженер-программист|защите информ"
                r"|программн|веб|front|back|fullstack|mobile|мобильн|сетев"
                r"|информационн\w+ технолог|техн\w+ писан")
df["is_it"] = (df["professionalSphereName"].fillna("").str.contains("Информационные технологии")
               | df["vacancyName"].fillna("").str.lower().str.contains(IT_TITLE_PAT, regex=True))
it = df[df["is_it"]].copy()
print(f"IT-вакансий: {len(it)}\n")

# ---------- 1. Топ технологий ----------
SKILLS = {
    "1С":              r"\b1c\b|1с-|1с ",
    "Java":            r"\bjava\b(?!script)",
    "Python":          r"\bpython|питон",
    "JavaScript/Node": r"javascript|node\.?\s?js|react|vue|angular|фронтенд|frontend",
    ".NET / C#":       r"\.net|\bc#|asp",
    "C++":             r"c\+\+",
    "SQL":             r"\bsql\b",
    "PostgreSQL":      r"postgres",
    "MySQL":           r"mysql|mariadb",
    "Oracle":          r"\boracle\b",
    "MongoDB":         r"mongodb",
    "Redis/RabbitMQ/Kafka": r"redis|rabbitmq|kafka",
    "Docker":          r"\bdocker\b",
    "Kubernetes":      r"kubernetes|\bk8s\b",
    "Git":             r"\bgit\b|github|gitlab",
    "Linux":           r"\blinux\b|ubuntu|centos",
    "Windows Server/AD": r"windows server|active directory|\bad\b\b|gpo",
    "1С:ERP / УТ":     r"erp|\bут\b|управление торгов",
    "REST/API":        r"\brest\b|openapi|swagger|api\b",
    "CI/CD, DevOps":   r"ci/cd|ci\s*cd|devops|gitlab.ci|jenkins|ansible|terraform",
    "Мониторинг (Zabbix/Grafana)": r"prometheus|grafana|zabbix|graf",
    "Тестирование (QA)": r"тестиров|qa\b|test\w*|баг|чек-лист|selenium|appium",
    "Информационная безопасность": r"защит\w* информ|информационн\w* безопас|иба|\bpki\b|крипт|уязвимост|фстэк|пдн|антивирус",
    "Сети, маршрутизация": r"маршрутиз|cisco|vlan|bgp|ospf|сетев\w* оборуд|l2|l3",
    "152-ФЗ / 173-ФЗ":  r"173-фз|273-фз|152-фз",
    "AI/ML":           r"\bai\b|машинн\w* обучен|machine learning|chatgpt|нейросет|генеративн",
    "Bitrix":          r"bitrix|битрикс",
    "PHP":             r"\bphp\b",
    "Go":              r"\bgolang\b|\bgo-разработ",
    "Сертификация (CCNA/ITIL)": r"ccna|ccnp|itil|gcqa",
}
text = (it["vacancyName"].fillna("") + " \n " + it["responsibilities"].fillna("")
        + " \n " + it["positionRequirements"].fillna("")).str.lower()
skill_counts = {k: text.str.contains(p, regex=True).sum() for k, p in SKILLS.items()}
skill_series = pd.Series(skill_counts).sort_values(ascending=False)
skill_series = skill_series[skill_series > 0]
print("=== Задача 1: топ технологий в IT-вакансиях ===")
print(skill_series.head(15).to_string(), "\n")

# ---------- 2. Административные округа (по ул. ключевым словам адреса) ----------
STREET_AD = [
    (r"академика королева|тихорецкий|плеханова|авиамоторная|цимлянская|шоссейная|энтузиастов", "ЮВАО"),
    (r"большая юшуньская|нагатинск|варшавск|каширск|новоданиловская", "ЮАО"),
    (r"профсоюзная|обручева|бутлерова|нахимовск|вернадского", "ЮЗАО"),
    (r"пресненская|садовническая|овчинниковская|серебряническая|льва толстого|озерковская|красносельская|красногвардейск|поклонная|пироговская", "ЦАО"),
    (r"верейская|сколково|кутузов|рублёв|можайск", "ЗАО"),
    (r"ленинградск|смольная|алтуфьевск|лесная", "САО"),
    (r"проспект мира,|оранжебургская|яузская|мишина", "СВАО"),
    (r"зеленоград", "Зеленоград"),
    (r"мкад", "МКАД"),
    (r"вороново|раменский|лавочкина|инновационного", "Новая Москва / обл."),
]
def to_district(addr):
    a = str(addr).lower()
    for pat, name in STREET_AD:
        if re.search(pat, a):
            return name
    return "адрес не распознан"
it["district"] = it["vacancyAddress"].apply(to_district)
dist = it["district"].value_counts()
print("=== Задача 2: округа (аппроксимация по адресу) ===")
print(dist.to_string(), "\n")

# ---------- 3. Опыт работы ----------
def exp_group(y):
    try:
        y = int(float(y))
    except (ValueError, TypeError):
        return "не указан"
    if y <= 0:
        return "без опыта"
    if y <= 2:
        return "1–2 года"
    if y <= 4:
        return "3–4 года"
    if y <= 6:
        return "5–6 лет"
    return "более 6 лет"
it["exp_group"] = it["experienceRequirements"].apply(exp_group)
exp_order = ["без опыта", "1–2 года", "3–4 года", "5–6 лет", "более 6 лет", "не указан"]
exp_counts = it["exp_group"].value_counts().reindex([e for e in exp_order if e in it["exp_group"].values])
print("=== Задача 3: вакансии по требуемому опыту ===")
print(exp_counts.to_string(), "\n")

# ---------- 4. Зарплаты ----------
def to_num(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None
it["sal_min"] = it["salaryMin"].apply(to_num)
it["sal_max"] = it["salaryMax"].apply(to_num)
it["salary"] = it.apply(
    lambda r: (r["sal_min"] + r["sal_max"]) / 2 if pd.notna(r["sal_max"]) and r["sal_max"] > r["sal_min"] > 0
    else (r["sal_min"] if pd.notna(r["sal_min"]) and r["sal_min"] > 0 else None), axis=1)
with_sal = it.dropna(subset=["salary"])
print(f"IT-вакансий с зарплатой: {len(with_sal)}/{len(it)}, "
      f"медиана {with_sal['salary'].median():,.0f} ₽, средняя {with_sal['salary'].mean():,.0f} ₽")
sal_exp = with_sal.groupby("exp_group")["salary"].agg(["count", "median", "mean", "min", "max"]) \
    .reindex([e for e in exp_order if e in with_sal["exp_group"].values])
print("\n=== Задача 4: зарплата по группам опыта (руб./мес.) ===")
print(sal_exp.round(0).to_string())
top_titles = with_sal.groupby("vacancyName")["salary"].agg(["count", "median"]).sort_values("count", ascending=False)
print("\n=== Медианная зарплата по частым должностям ===")
print(top_titles.head(12).round(0).to_string(), "\n")

# ---------- 5. Графики ----------
def savefig(fig, name):
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/{name}", dpi=150)
    plt.close(fig)
    print("сохранён:", f"{OUT_DIR}/{name}")

fig, ax = plt.subplots(figsize=(9, 6.5))
s = skill_series.head(15)[::-1]
ax.barh(s.index, s.values, color="#2f7fb4")
ax.set_title("Задача 1. Топ-15 технологий в IT-вакансиях Москвы (n=%d)" % len(it))
ax.set_xlabel("число вакансий")
ax.bar_label(ax.containers[0])
savefig(fig, "01_top_skills.png")

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(dist.index, dist.values, color="#e8842c")
ax.set_title("Задача 2. Распределение IT-вакансий по округам Москвы")
ax.set_ylabel("число вакансий")
ax.bar_label(ax.containers[0])
plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
savefig(fig, "02_districts.png")

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(exp_counts.index, exp_counts.values, color="#4caf78")
ax.set_title("Задача 3. IT-вакансии по требуемому опыту работы")
ax.set_ylabel("число вакансий")
ax.bar_label(ax.containers[0])
savefig(fig, "03_experience.png")

fig, ax = plt.subplots(figsize=(7.5, 5))
ax.bar(sal_exp.index, sal_exp["median"], color="#9b6bc9")
ax.set_title("Задача 4. Медианная зарплата по группам опыта")
ax.set_ylabel("медиана, руб./мес.")
ax.bar_label(ax.containers[0], fmt="%.0f")
savefig(fig, "04_salary_by_exp.png")

fig, ax = plt.subplots(figsize=(7.5, 5))
ax.hist(with_sal["salary"] / 1000, bins=40, color="#c95a5a", edgecolor="white")
ax.set_title("Распределение зарплат в IT-вакансиях Москвы")
ax.set_xlabel("зарплата, тыс. руб./мес.")
ax.set_ylabel("число вакансий")
savefig(fig, "05_salary_hist.png")

fig, ax = plt.subplots(figsize=(9, 6))
tt = top_titles.head(12).iloc[::-1]
ax.barh([t[:40] for t in tt.index], tt["median"], color="#3aa6a0")
ax.set_title("Медианная зарплата по частым IT-должностям (топ-12)")
ax.set_xlabel("медиана, руб./мес.")
ax.bar_label(ax.containers[0], fmt="%.0f")
savefig(fig, "06_salary_by_title.png")

# фон: вся Россия
try:
    reg = pd.read_csv("results/regions_russia.csv", dtype={"vacancies": float}, encoding="utf-8-sig")
    reg = reg.sort_values("vacancies", ascending=False).head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(reg["regionName"], reg["vacancies"], color="#6b7b9b")
    ax.set_title("Фон: топ-12 регионов РФ по числу вакансий (всего 480 тыс., Москва — 3-е)")
    ax.set_xlabel("число вакансий")
    ax.bar_label(ax.containers[0], fmt="%.0f")
    savefig(fig, "00_russia_regions.png")
except FileNotFoundError:
    pass

# ---------- 6. Экспорт результатов (CSV через запятую, Excel-совместимо) ----------
skill_series.rename_axis("Технология").reset_index(name="Вакансий").to_csv(
    f"{RES_DIR}/skills_it.csv", index=False, encoding="utf-8-sig")
dist.rename_axis("Округ").reset_index(name="Вакансий").to_csv(
    f"{RES_DIR}/districts_it.csv", index=False, encoding="utf-8-sig")
exp_counts.rename_axis("Опыт").reset_index(name="Вакансий").to_csv(
    f"{RES_DIR}/experience_it.csv", index=False, encoding="utf-8-sig")
sal_exp.round(0).rename_axis("Опыт").reset_index().rename(
    columns={"count": "Вакансий", "median": "Медиана, руб.", "mean": "Средняя, руб.",
             "min": "Минимум, руб.", "max": "Максимум, руб."}).to_csv(
    f"{RES_DIR}/salary_by_exp_it.csv", index=False, encoding="utf-8-sig")
top_titles.round(0).rename_axis("Должность").reset_index().rename(
    columns={"count": "Вакансий", "median": "Медиана, руб."}).to_csv(
    f"{RES_DIR}/salary_by_title_it.csv", index=False, encoding="utf-8-sig")

it_out = it[["vacancyName", "fullCompanyName", "district", "exp_group",
             "salary", "salaryMin", "salaryMax", "datePublished"]].copy()
it_out.columns = ["Должность", "Компания", "Округ", "Опыт",
                  "Зарплата, руб.", "Зарплата от", "Зарплата до", "Опубликована"]
it_out["Опубликована"] = it_out["Опубликована"].astype(str).str[:10]
it_out.sort_values(["Округ", "Зарплата, руб."], ascending=[True, False]).to_csv(
    f"{RES_DIR}/it_vacancies_moscow.csv", index=False, encoding="utf-8-sig")
print("экспортировано: results/*.csv")

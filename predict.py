# predict.py — задача типа «прогноз»: регрессия зарплаты IT-вакансий
# Признаки: требуемый опыт, число навыков, уровень должности (junior/mid/senior), высшее образование.
# Целевая переменная: log10(зарплата) — зарплата имеет сильный правый хвост.
import re
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("vacancy_moscow.csv", sep="|", dtype=str, encoding="utf-8")

IT_TITLE_PAT = (r"программист|разработчик|python|java|c\+\+|c#|\.net|devops|qa|тестир"
                r"|аналитик|data|баз данн|sql|1c|1с|системн\w+ админ|сисадмин"
                r"|ит-специалист|it-специалист|инженер-программист|защите информ"
                r"|программн|веб|front|back|fullstack|mobile|мобильн|сетев"
                r"|информационн\w+ технолог|техн\w+ писан")
df["is_it"] = (df["professionalSphereName"].fillna("").str.contains("Информационные технологии")
               | df["vacancyName"].fillna("").str.lower().str.contains(IT_TITLE_PAT, regex=True))
it = df[df["is_it"]].copy()

def to_num(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return np.nan

it["sal_min"] = it["salaryMin"].apply(to_num)
it["sal_max"] = it["salaryMax"].apply(to_num)
it["salary"] = np.where((it["sal_max"] > it["sal_min"]) & (it["sal_min"] > 0),
                        (it["sal_min"] + it["sal_max"]) / 2, it["sal_min"])

it["exp"] = pd.to_numeric(it["experienceRequirements"], errors="coerce")

SKILL_RE = r"\b(java|python|sql|postgres|mysql|oracle|mongodb|kafka|docker|kubernetes|git|linux|devops|rest|api|javascript|node|react|vue|angular|1c|1с|pandas|spark|hadoop)\b"
text = (it["responsibilities"].fillna("") + " " + it["positionRequirements"].fillna("")).str.lower()
it["n_skills"] = text.str.count(SKILL_RE)

# уровень должности по названию
def level(t):
    t = str(t).lower()
    if re.search(r"junior|младш|стаж[её]р|intern|начинающ", t):
        return 0
    if re.search(r"senior|старш|ведущ|главн|lead|руководител|начальник|директор|тимлид|team.lead|эксперт", t):
        return 2
    return 1
it["level"] = it["vacancyName"].apply(level)

# высшее образование
def higher_ed(x):
    try:
        s = json.loads(x).get("educationType", "").lower()
    except Exception:
        s = str(x).lower()
    return 1 if ("высш" in s or "бакалавр" in s or "магистр" in s) else 0
it["high_ed"] = it["educationRequirements"].apply(higher_ed)

data = it[["exp", "n_skills", "level", "high_ed", "salary"]].copy()
data = data[(data["salary"] > 0) & data["exp"].notna() & data["n_skills"].notna()]
X = data[["exp", "n_skills", "level", "high_ed"]].values
y = np.log10(data["salary"].values)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
model = LinearRegression().fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
# MAE в рублях (обратно из логарифма)
mae = np.mean(np.abs(10**y_test - 10**y_pred))
print(f"IT-вакансий в модели: {len(data)}")
print(f"R² (log10 зарплаты) = {r2:.3f},  MAE ≈ {mae:,.0f} ₽")
coef_names = ["опыт(лет)", "навыки", "уровень", "высш.образование"]
for n, c in zip(coef_names, model.coef_):
    print(f"  {n}: {c:+.3f}")

# график: предсказано vs фактически (в рублях)
y_act = 10**y_test
y_prd = 10**y_pred
fig, ax = plt.subplots(figsize=(6.5, 5.5))
ax.scatter(y_act / 1000, y_prd / 1000, s=12, alpha=0.6, color="#3aa6a0", edgecolor="white")
lim = [0, max(y_act.max(), y_prd.max()) / 1000 * 1.05]
ax.plot(lim, lim, "r--", lw=1.5, label="y = x")
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("фактическая зарплата, тыс. ₽/мес")
ax.set_ylabel("предсказанная зарплата, тыс. ₽/мес")
ax.set_title(f"Прогноз зарплаты (линейная регрессия, log-шкала)\nR²={r2:.2f}, MAE≈{mae:,.0f} ₽")
ax.legend()
fig.tight_layout(); fig.savefig("figures/07_salary_prediction.png", dpi=150)
print("сохранён: figures/07_salary_prediction.png")

# график: зарплата vs опыт по уровням
fig, ax = plt.subplots(figsize=(6.5, 5.5))
for lv, col, lab in [(0, "#4caf78", "junior"), (1, "#3aa6a0", "middle"), (2, "#9b6bc9", "senior/lead")]:
    m = data["level"] == lv
    ax.scatter(data.loc[m, "exp"], data.loc[m, "salary"] / 1000, s=12, alpha=0.5, color=col, edgecolor="white", label=lab)
ax.set_xlabel("требуемый опыт, лет")
ax.set_ylabel("зарплата, тыс. ₽/мес")
ax.set_title("Зарплата vs опыт по уровню должности")
ax.legend()
fig.tight_layout(); fig.savefig("figures/08_salary_vs_exp.png", dpi=150)
print("сохранён: figures/08_salary_vs_exp.png")

pd.DataFrame({"метрика": ["R2 (log)", "MAE, руб"] + ["коэф_" + n for n in coef_names],
              "значение": [round(r2, 3), round(mae, 0)] + [round(c, 3) for c in model.coef_]}).to_csv(
    "results/prediction.csv", index=False, encoding="utf-8-sig")
print("экспортировано: results/prediction.csv")

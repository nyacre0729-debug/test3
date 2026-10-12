# er_diagram.py — модель данных: выгрузка trudvsem.ru → таблица PostgreSQL
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(12, 5.8))
ax.set_xlim(0, 12); ax.set_ylim(0, 5.8); ax.axis("off")

def box(x, y, w, h, title, fields, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc="white", ec=color, lw=2))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42, boxstyle="square,pad=0",
                                fc=color, ec=color))
    ax.text(x + w/2, y + h - 0.21, title, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white")
    for i, f in enumerate(fields):
        ax.text(x + 0.15, y + h - 0.72 - i*0.3, f, ha="left", va="center", fontsize=9)

src = ["id  « UUID — ключ вакансии",
       "vacancyName  текст — должность",
       "fullCompanyName  текст — компания",
       "vacancyAddress  текст — адрес",
       "stateRegionCode  код ОКТМО региона",
       "salaryMin / salaryMax  числа, руб.",
       "experienceRequirements  лет опыта",
       "professionalSphereName  отрасль",
       "responsibilities / positionRequirements",
       "datePublished  дата публикации"]
dst = ["id  INT, PK",
       "title  TEXT",
       "company  TEXT",
       "city_district  TEXT (адрес)",
       "salary_min  INT",
       "salary_max  INT",
       "experience  TEXT",
       "description  TEXT",
       "published_at  TEXT"]

box(0.4, 0.9, 4.4, 4.1, "vacancy_full.csv  (trudvsem.ru)", src, "#2f7fb4")
box(7.2, 1.0, 4.3, 3.9, "vacancy  (PostgreSQL)", dst, "#4caf78")

ax.annotate("", xy=(7.15, 2.95), xytext=(4.85, 2.95),
            arrowprops=dict(arrowstyle="-|>", lw=2, color="#e8842c"))
ax.text(6.0, 3.15, "фильтр:\nregion=Москва\n(1:1, 15 876 записей)",
        ha="center", va="bottom", fontsize=8.5, color="#e8842c")

fig.suptitle("Модель данных проекта (выгрузка → БД)", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/ER_diagram.png", dpi=150)
print("saved: figures/ER_diagram.png")

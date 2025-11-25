import datetime
import pytz
import matplotlib.pyplot as plt
from astral import LocationInfo
from astral.sun import sun
from collections import defaultdict
import calendar

# Setup
tz = pytz.timezone("Europe/Brussels")
city = LocationInfo("Brussels", "Belgium", "Europe/Brussels", 50.8503, 4.3517)
year = datetime.date.today().year

# Generate all days of the year
dates = [
    datetime.date(year, 1, 1) + datetime.timedelta(days=i)
    for i in range(365 + (1 if datetime.date(year, 12, 31).timetuple().tm_yday == 366 else 0))
]

def to_decimal_hour(dt: datetime.datetime) -> float:
    return dt.hour + dt.minute / 60 + dt.second / 3600

def week_of_year(d: datetime.date) -> int:
    return d.isocalendar().week

# Collect daily values by week
sunrise_by_week = defaultdict(list)
sunset_by_week = defaultdict(list)

for d in dates:
    s = sun(city.observer, date=d, tzinfo=tz)
    w = week_of_year(d)
    sunrise_by_week[w].append(to_decimal_hour(s["sunrise"]))
    sunset_by_week[w].append(to_decimal_hour(s["sunset"]))

# Compute weekly averages
weeks = sorted(sunrise_by_week.keys())
sunrise_avg = [sum(sunrise_by_week[w]) / len(sunrise_by_week[w]) for w in weeks]
sunset_avg  = [sum(sunset_by_week[w]) / len(sunset_by_week[w]) for w in weeks]

# --- PLOT ---
plt.figure(figsize=(14, 6))
plt.plot(weeks, sunrise_avg, label="Sunrise", color="darkorange", linewidth=2)
plt.plot(weeks, sunset_avg,  label="Sunset",  color="royalblue", linewidth=2)

plt.title(f"Sunrise and Sunset Times in Brussels ({year})")
plt.xlabel("Week Number")
plt.ylabel("Time of Day")

# ---- Format Y axis (every hour) ----
def hour_formatter(x, pos):
    h = int(x)
    m = int((x - h) * 60)
    return f"{h:02d}:{m:02d}"

plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(hour_formatter))
plt.yticks(range(5, 24))  # from 05:00 to 23:00 every hour

# ---- Format X axis ----
plt.xticks(range(1, 54))  # Weeks 1–53
ax = plt.gca()

# Add month labels under weeks
month_weeks = []
month_labels = []
for m in range(1, 13):
    first_day = datetime.date(year, m, 1)
    week_num = first_day.isocalendar().week
    month_weeks.append(week_num)
    month_labels.append(calendar.month_abbr[m])

for i, (wk, lbl) in enumerate(zip(month_weeks, month_labels)):
    plt.text(wk, 4.7, lbl, ha='center', va='top', fontsize=9, color='gray')  # below axis

plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

filename = f"sunrise_sunset_weeks_avg_{year}.png"
plt.savefig(filename, dpi=200)
print(f"Graph saved as {filename}")
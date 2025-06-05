import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("equity_log.csv", parse_dates=["date"])
df = df.sort_values("date")

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["equity"], marker="o")
plt.title("Daily Equity")
plt.xlabel("Date")
plt.ylabel("Equity")
plt.grid(True)
plt.tight_layout()

plt.savefig("static/imgs/equity.png")

#!/usr/bin/env python3
"""Generate equity curve chart from equity_log.csv.

Produces a clean, dark-themed equity chart suitable for README display.
Output: static/imgs/equity.png
"""

import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_PATH = os.path.join(PROJECT_ROOT, "equity_log.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "static", "imgs", "equity.png")


def main():
    # Read data
    dates, equities = [], []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.append(datetime.strptime(row["date"], "%Y-%m-%d"))
            equities.append(int(row["equity"]))

    if not dates:
        print("No data found in equity_log.csv")
        return

    # Compute stats
    initial = equities[0]
    final = equities[-1]
    peak = max(equities)
    trough = min(equities)
    total_return_pct = (final - initial) / initial * 100
    max_drawdown = min(
        (equities[i] - max(equities[:i+1])) / max(equities[:i+1]) * 100
        for i in range(1, len(equities))
    )

    # Dark theme
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # Plot equity curve
    color = "#58a6ff" if final >= initial else "#f85149"
    ax.plot(dates, equities, color=color, linewidth=2, zorder=3)

    # Fill area under curve with gradient effect
    ax.fill_between(dates, equities, min(equities) * 0.995,
                     alpha=0.15, color=color, zorder=2)

    # Mark start and end
    ax.scatter([dates[0]], [equities[0]], color="#8b949e", s=40, zorder=4)
    ax.scatter([dates[-1]], [equities[-1]], color=color, s=40, zorder=4)

    # Mark peak
    peak_idx = equities.index(peak)
    ax.scatter([dates[peak_idx]], [peak], color="#3fb950", s=50, marker="^", zorder=4)
    ax.annotate(f"Peak: ${peak:,.0f}",
                xy=(dates[peak_idx], peak),
                xytext=(0, 12), textcoords="offset points",
                fontsize=8, color="#3fb950", ha="center",
                fontweight="bold")

    # Formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=9)

    # Grid
    ax.grid(True, alpha=0.1, color="#30363d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#30363d")
    ax.spines["bottom"].set_color("#30363d")
    ax.tick_params(colors="#8b949e")

    # Title with stats
    title = (
        f"Equity Curve  •  "
        f"Return: {total_return_pct:+.1f}%  •  "
        f"Max DD: {max_drawdown:.1f}%  •  "
        f"${initial:,.0f} → ${final:,.0f}"
    )
    ax.set_title(title, fontsize=11, color="#c9d1d9", pad=15, fontweight="bold")

    # Date range subtitle
    date_range = f"{dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')} ({len(dates)} days)"
    ax.text(0.5, -0.18, date_range, transform=ax.transAxes,
            fontsize=8, color="#8b949e", ha="center")

    plt.tight_layout()

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.savefig(OUTPUT_PATH, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    print(f"Chart saved to {OUTPUT_PATH}")
    print(f"  Period: {date_range}")
    print(f"  Return: {total_return_pct:+.1f}%")
    print(f"  Max Drawdown: {max_drawdown:.1f}%")


if __name__ == "__main__":
    main()

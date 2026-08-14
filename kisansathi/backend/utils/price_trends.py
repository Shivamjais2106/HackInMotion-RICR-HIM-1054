"""
Market Price Trends — KisanSathi
==================================
Requirement 5: Market Price Insights

Generates 7-day simulated price trend data for commodities
based on MSP baseline + seasonal volatility.
Used by the frontend Recharts price trend graph.

Author: Rustam Ali
"""

from __future__ import annotations
import random
import datetime
from utils.market_prices import MANDI_BASE_PRICES, get_commodity_price


def get_price_trend(commodity: str, days: int = 7) -> list[dict]:
    """
    Returns a list of daily price points for the past `days` days.
    Uses live modal price as anchor, simulates historical movement.

    Each point: {date, price, is_today}
    """
    commodity = commodity.lower().strip()
    base = MANDI_BASE_PRICES.get(commodity)
    if not base:
        return []

    # Get today's price as anchor
    live = get_commodity_price(commodity)
    today_price = live["modal_price"] if live else (base["min"] + base["max"]) // 2

    today = datetime.date.today()
    trend = []

    # Simulate going backwards — realistic ±3% daily movement
    price = today_price
    for i in range(days - 1, -1, -1):
        date = today - datetime.timedelta(days=i)
        if i == 0:
            point_price = today_price
        else:
            # Random walk bounded between min and max
            change = random.uniform(-0.03, 0.03)
            price = max(base["min"], min(base["max"], int(price * (1 + change))))
            point_price = price

        trend.append(
            {
                "date": date.strftime("%d %b"),
                "price": point_price,
                "is_today": i == 0,
            }
        )

    return trend


def get_price_summary(commodity: str) -> dict:
    """
    Returns a price summary for a commodity:
      - today_price, week_high, week_low
      - trend_direction: "rising" | "falling" | "stable"
      - trade_signal: "sell_now" | "hold" | "below_msp"
      - change_pct: % change over 7 days
    """
    trend = get_price_trend(commodity, days=7)
    if not trend:
        return {}

    prices = [t["price"] for t in trend]
    today_price = prices[-1]
    week_open = prices[0]
    week_high = max(prices)
    week_low = min(prices)

    change_pct = round((today_price - week_open) / week_open * 100, 1)

    if change_pct > 2:
        direction = "rising"
    elif change_pct < -2:
        direction = "falling"
    else:
        direction = "stable"

    base = MANDI_BASE_PRICES.get(commodity.lower(), {})
    msp = base.get("msp")
    max_price = base.get("max", today_price)

    if msp and today_price < msp:
        signal = "below_msp"
    elif today_price >= max_price * 0.88:
        signal = "sell_now"
    elif direction == "rising":
        signal = "hold_rising"
    else:
        signal = "hold"

    return {
        "commodity": commodity.capitalize(),
        "today_price": today_price,
        "week_high": week_high,
        "week_low": week_low,
        "week_open": week_open,
        "change_pct": change_pct,
        "trend_direction": direction,
        "trade_signal": signal,
        "msp": msp,
        "trend": trend,
    }

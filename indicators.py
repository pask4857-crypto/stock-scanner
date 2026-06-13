import pandas as pd

from ta.trend import MACD
from ta.momentum import StochasticOscillator


def calculate_indicators(df):

    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    close = df["Close"].squeeze()

    stoch = StochasticOscillator(
        high=high,
        low=low,
        close=close
    )

    df["K"] = stoch.stoch()
    df["D"] = stoch.stoch_signal()

    macd = MACD(close=close)

    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()
    df["Histogram"] = macd.macd_diff()

    df["MA20"] = (
        df["Close"]
        .rolling(window=20)
        .mean()
    )

    df["MA60"] = (
        df["Close"]
        .rolling(60)
        .mean()
    )

    df["MA120"] = (
        df["Close"]
        .rolling(120)
        .mean()
    )

    return df


def kd_overbought_recent(df, lookback=20):


    if len(df) < lookback + 5:
        return False

    for i in range(lookback):

        current_idx = -(i + 1)

        today = df.iloc[current_idx]
        yesterday = df.iloc[current_idx - 1]

        try:

            recent = df.iloc[current_idx - 5:current_idx]

            overbought = (
                (recent["K"] > 80).all()
                and
                (recent["D"] > 80).all()
            )

            dead_cross = (
                yesterday["K"] > yesterday["D"]
                and
                today["K"] < today["D"]
            )

            if overbought and dead_cross:

                cross_date = today.name

                return {
                    "found": True,
                    "date": cross_date
                }

        except Exception:
            continue

    return {
        "found": False,
        "date": None
    }


def macd_green_shrinking(
    df,
    lookback=5
):

    if len(df) < lookback:
        return False

    recent = (
        df["Histogram"]
        .tail(lookback)
        .dropna()
    )

    if len(recent) < lookback:
        return False

    # 今天仍是綠柱
    if recent.iloc[-1] >= 0:
        return False

    # 最近5天最深的位置
    lowest = recent.min()

    # 今天比最低點明顯回升
    return recent.iloc[-1] > lowest

def macd_green_shrinking_days(
    df,
    lookback=20
):

    if len(df) < lookback + 1:
        return None

    for days_ago in range(1, lookback + 1):

        current_idx = len(df) - days_ago
        prev_idx = current_idx - 1

        if prev_idx < 0:
            break

        yesterday = df.iloc[prev_idx]["Histogram"]
        today = df.iloc[current_idx]["Histogram"]

        if (
            pd.notna(yesterday)
            and
            pd.notna(today)
            and
            yesterday < 0
            and
            today < 0
            and
            today > yesterday
        ):
            return days_ago

    return None

def macd_recovery_info(
    df,
    lookback=20
):

    hist = (
        df["Histogram"]
        .tail(lookback)
        .dropna()
    )

    if len(hist) == 0:
        return None

    lowest = hist.min()

    current = hist.iloc[-1]

    if lowest >= 0:
        return None

    recovery_pct = (
        (current - lowest)
        / abs(lowest)
    ) * 100

    return {
        "lowest": round(float(lowest), 4),
        "current": round(float(current), 4),
        "recovery_pct": round(float(recovery_pct), 1)
    }
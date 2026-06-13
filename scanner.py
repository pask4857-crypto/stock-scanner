import os
from pathlib import Path
from datetime import datetime
import subprocess

import pandas as pd
import yfinance as yf

from indicators import (
    calculate_indicators,
    kd_overbought_recent,
    macd_green_shrinking,
    macd_recovery_info

)

def get_stock_data(stock_id):

    cache_dir = "cache"

    # 快取已存在時不報錯
    os.makedirs(
        cache_dir,
        exist_ok=True
    )

    cache_file = (
        Path(cache_dir)
        / f"{stock_id}.csv"
    )

    numeric_cols = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    # ==========================
    # 快取存在
    # ==========================
    if cache_file.exists():

        try:

            df = pd.read_csv(
                cache_file,
                index_col=0,
                parse_dates=True #轉換資料型別
            )

            for col in numeric_cols:

                if col in df.columns:

                    df[col] = pd.to_numeric(
                        df[col],
                        errors="coerce" #無法轉換時變為NaN
                    )

            # 增量更新
            last_date = pd.to_datetime(
                df.index.max()
            )

            start_date = last_date

            print(
                f"更新快取: {stock_id} "
                f"({start_date.date()} ~ 今天)"
            )

            new_df = yf.download(
                stock_id,
                start=start_date.strftime(
                    "%Y-%m-%d"
                ),
                auto_adjust=True, #調整反映股息和分割
                progress=False #套件的進度條
            )

            if not new_df.empty:

                if isinstance(
                    new_df.columns,
                    pd.MultiIndex
                ):
                    new_df.columns = (
                        new_df.columns
                        .get_level_values(0)
                    )

                new_df = new_df[
                    [
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume"
                    ]
                ]

                df = pd.concat(
                    [df, new_df]
                )

                #排序並刪除重複資料
                df = (
                    df
                    .sort_index()
                    .loc[
                        ~df.index.duplicated(
                            keep="last"
                        )
                    ]
                )

                df.to_csv(
                    cache_file
                )

                print(
                    f"已更新 "
                    f"{len(new_df)} 筆資料"
                )

            else:

                print(
                    f"資料已是最新: "
                    f"{stock_id}"
                )

            return df

        except Exception as e:

            print(
                f"快取讀取失敗: "
                f"{stock_id}"
            )

            print(e)

    # ==========================
    # 首次下載
    # ==========================
    print(
        f"下載資料: {stock_id}"
    )

    df = yf.download(
        stock_id,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if df.empty:

        return df

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):
        df.columns = (
            df.columns
            .get_level_values(0)
        )

    df = df[
        [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ]

    df.to_csv(
        cache_file
    )

    return df

def scan_stock(
    stock_id,
    stock_name
):

    try:

        df = get_stock_data(stock_id)

        if df.empty:
            return None

        #檢查欄位，只取欄位名稱
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 60:
            return None

        df = calculate_indicators(df)

        df["Turnover"] = (
                df["Close"]
                * df["Volume"]
        )

        latest = df.iloc[-1]

        close_price = float(latest["Close"])

        today_turnover = float(
            latest["Turnover"]
        )

        avg_turnover_20 = float(
            df["Turnover"]
            .tail(20)
            .mean()
        )

        hist = float(latest["Histogram"])
        ma20 = float(latest["MA20"])
        ma60 = float(latest["MA60"])
        ma120 = float(latest["MA120"])

        distance_ma20 = (
                (close_price - ma20)
                / ma20
                * 100
        )

        # ===== 成交值 =====
        trading_value = float(
            latest["Turnover"]
        )

        # 20日平均成交值小於1億直接排除
        if avg_turnover_20 < 100000000:
            return None

        # 長線多頭過濾
        if ma60 < ma120:
            return None

        # ===== KD =====
        kd_result = kd_overbought_recent(df)

        # ===== MACD =====
        macd_result = macd_green_shrinking(df)
        macd_info = macd_recovery_info(df)

        if (
            kd_result["found"]
            and
            macd_result
        ):

            kd_date = kd_result["date"]

            days_since = (
                datetime.now().date()
                -
                kd_date.date()
            ).days

            return {
                "股票代號": stock_id,
                "股票名稱": stock_name,

                "收盤價":
                    round(close_price, 2),

                "20MA":
                    round(ma20, 2),

                "距20MA(%)":
                    round(distance_ma20, 2),

                "KD高檔鈍化結束日期":
                    kd_date.strftime("%Y-%m-%d"),

                "距今天數":
                    days_since,

                "MACD柱":
                    round(hist, 4),

                "20日最低MACD柱":
                    macd_info["lowest"]
                    if macd_info
                    else None,

                "MACD恢復比例(%)":
                    macd_info["recovery_pct"]
                    if macd_info
                    else None,

                "成交值(億)":
                    round(
                        trading_value / 100000000,
                        2
                    ),

                "20日平均成交值(億)":
                    round(
                        avg_turnover_20 / 100000000,
                        2
                    ),
            }

        return None

    except Exception as e:

        print(
            f"{stock_id} 錯誤: {e}"
        )

        return None


def export_excel(result):

    if len(result) == 0:

        print("沒有符合條件股票")
        return

    os.makedirs(
        "output",
        exist_ok=True
    )

    df = pd.DataFrame(result)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    file_name = (
        f"output/result_{timestamp}.xlsx"
    )

    df.to_excel(
        file_name,
        index=False
    )

    print(
        f"輸出完成: {file_name}"
    )

    subprocess.Popen(
        [
            "explorer",
            "/select,",
            os.path.abspath(file_name)
        ]
    )
import sys
from pathlib import Path

import pandas as pd


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(getattr(sys, "_MEIPASS"))
    else:
        base_path = Path(__file__).parent

    return base_path / relative_path


def get_stock_list():

    csv_path = resource_path(
        "stocks.csv"
    )

    if not csv_path.exists():

        raise FileNotFoundError(
            f"找不到股票清單：{csv_path}"
        )

    df = pd.read_csv(csv_path)

    return df.to_dict(
        orient="records"
    )
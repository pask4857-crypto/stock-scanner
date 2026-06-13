import pandas as pd
import twstock

stocks = []

for stock_id, stock_info in twstock.codes.items():

    # 只保留上市、上櫃股票
    if stock_info.market not in ["上市", "上櫃"]:
        continue

    # 排除 ETF、權證、指數
    if stock_info.type != "股票":
        continue

    stocks.append({
        "id": (
            f"{stock_id}.TW"
            if stock_info.market == "上市"
            else f"{stock_id}.TWO"
        ),
        "name": stock_info.name
    })

df = pd.DataFrame(stocks)

df.to_csv(
    "stocks.csv",
    index=False,
    encoding="utf-8-sig"
)

print(
    f"已產生 stocks.csv，共 {len(df)} 檔股票"
)
from stock_list import get_stock_list

from scanner import (
    scan_stock,
    export_excel
)


def main(
    logger=None,
    progress_callback=None,
    stop_callback=None
):

    def output(message):

        if logger:
            logger(message)
        else:
            print(message)

    stocks = get_stock_list()

    result = []

    total = len(stocks)

    output(
        f"開始掃描 {total} 檔股票"
    )

    for index, stock in enumerate(
        stocks,
        start=1
    ):

        if (
                stop_callback
                and
                stop_callback()
        ):
            output(
                "使用者停止掃描"
            )

            return "stopped"

        stock_id = stock["id"]
        stock_name = stock["name"]

        percent = round(
            index / total * 100,
            1
        )

        if progress_callback:
            progress_callback(
                index,
                total,
                percent
            )

        output(
            f"[{index}/{total}] "
            f"({percent}%) "
            f"{stock_id} "
            f"{stock_name}"
        )

        row = scan_stock(
            stock_id,
            stock_name
        )

        if row:

            result.append(row)

            output(
                f"找到符合條件："
                f"{stock_id} "
                f"{stock_name}"
            )

    export_excel(result)

    output(
        f"符合條件股票數量："
        f"{len(result)}"
    )

    return "completed"


if __name__ == "__main__":
    main()
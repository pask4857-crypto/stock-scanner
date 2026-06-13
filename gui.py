import threading
import tkinter as tk
from tkinter import ttk

from main import main


def log(message):

    text_box.insert(
        tk.END,
        message + "\n"
    )

    text_box.see(
        tk.END
    )

    root.update()

def update_progress(
    current,
    total,
    percent
):

    progress["value"] = percent

    progress_label.config(
        text=(
            f"{current:,} / {total:,}"
            f"    ({percent}%)"
        )
    )

    root.update()

def run_scan():

    try:

        status = main(
            logger=log,
            progress_callback=update_progress,
            stop_callback=is_stop_requested
        )

        if status == "completed":

            log("掃描完成")

        elif status == "stopped":

            log("掃描已中止")

    except Exception as e:

        log(
            f"發生錯誤: {e}"
        )

    finally:

        scan_button.config(
            state=tk.NORMAL
        )

        stop_button.config(
            state=tk.DISABLED
        )


def start_scan():

    global stop_scan_flag

    stop_scan_flag = False

    text_box.delete(
        "1.0",
        tk.END
    )

    progress["value"] = 0

    progress_label.config(
        text="0%"
    )

    scan_button.config(
        state=tk.DISABLED
    )

    stop_button.config(
        state=tk.NORMAL
    )

    thread = threading.Thread(
        target=run_scan
    )

    thread.daemon = True

    thread.start()

def stop_scan():

    global stop_scan_flag

    stop_scan_flag = True

    log("正在停止掃描...")

def is_stop_requested():
    return stop_scan_flag

stop_scan_flag = False

root = tk.Tk()

root.title(
    "台股選股器"
)

root.geometry(
    "900x700"
)

scan_button = tk.Button(
    root,
    text="開始掃描",
    command=start_scan,
    font=(
        "Microsoft JhengHei",
        12
    )
)

stop_button = tk.Button(
    root,
    text="停止掃描",
    command=stop_scan,
    state=tk.DISABLED,
    font=(
        "Microsoft JhengHei",
        12
    )
)

scan_button.pack(
    pady=10
)

stop_button.pack(
    pady=5
)

progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=500,
    mode="determinate"
)

progress.pack(
    pady=10
)

progress_label = tk.Label(
    root,
    text="0 / 0 (0%)"
)

progress_label.pack()

frame = tk.Frame(root)

frame.pack(
    fill=tk.BOTH,
    expand=True
)

scrollbar = tk.Scrollbar(
    frame
)

scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

text_box = tk.Text(
    frame,
    yscrollcommand=scrollbar.set
)

text_box.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)

scrollbar.config(
    command=text_box.yview
)

root.mainloop()
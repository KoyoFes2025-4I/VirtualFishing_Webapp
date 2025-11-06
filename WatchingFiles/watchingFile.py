import time
import shutil
import os
from tkinter import simpledialog, Tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# pip install watchdog

# 設定
WATCH_FOLDER = r"test1" # 監視するフォルダ
DEST_FOLDER = r"test2" # 移動先フォルダ

# 表示させるウィンドウ
class RenameDialog(Tk):
    def __init__(self, filename):
        super().__init__()
        self.title("Rename")
        self.geometry("400x200")
        self.new_name = None

        Tk.Label(self, text=f"新しい名前を入力（拡張子なし）:", font=("Meiryo", 12)).pack(pady=10)
        Tk.Label(self, text=f"元ファイル名: {filename}", font=("Meiryo", 10), fg="gray").pack(pady=5)

        self.entry = Tk.Entry(self, width=40, font=("Meiryo", 12))
        self.entry.pack(pady=10)
        self.entry.focus()

        frame = Tk.Frame(self)
        frame.pack(pady=10)
        Tk.Button(frame, text="OK", width=10, command=self.on_ok).pack(side="left", padx=5)
        Tk.Button(frame, text="キャンセル", width=10, command=self.on_cancel).pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        self.new_name = self.entry.get().strip()
        self.destroy()

    def on_cancel(self):
        self.new_name = None
        self.destroy()

# フォルダを監視するイベントハンドラ関数
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        src_path = event.src_path
        filename = os.path.basename(src_path)
        print(f"新しいファイルを検出: {filename}")

        # ファイルが完全に書き込まれるまで少し待つ
        time.sleep(1)

        # ダイアログを開いて名前を入力
        root = Tk()
        root.withdraw()  # メインウィンドウ非表示
        new_name = simpledialog.askstring("Rename", f"新しい名前を入力（拡張子なし）:\n{filename}")
        root.destroy()

        if not new_name:
            print("キャンセルされました。")
            return

        # 元の拡張子を維持
        _, ext = os.path.splitext(filename)
        new_filename = new_name + ext
        dest_path = os.path.join(DEST_FOLDER, new_filename)

        # ファイル移動
        try:
            shutil.move(src_path, dest_path)
            print(f"{filename} → {new_filename} にリネームして移動しました。")
        except Exception as e:
            print(f"移動に失敗しました: {e}")

def main():
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    os.makedirs(DEST_FOLDER, exist_ok=True)

    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    print(f"監視を開始しました: {WATCH_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("監視を終了しました。")

    observer.join()

if __name__ == "__main__":
    main()
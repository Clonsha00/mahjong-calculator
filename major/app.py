import tkinter as tk
from tkinter import font

class MahjongConverter:
    """
    負責處理麻將代號與 Unicode 轉換的類別
    """
    def __init__(self):
        # 建立代號與 Unicode 的對照表
        self.map = {}
        self._build_map()

    def _build_map(self):
        # 1. 萬子 (1m - 9m) -> U+1F007 ~ U+1F00F
        base_wan = 0x1F007
        for i in range(1, 10):
            self.map[f"{i}m"] = chr(base_wan + i - 1)

        # 2. 條子/索子 (1s - 9s) -> U+1F010 ~ U+1F018
        base_sou = 0x1F010
        for i in range(1, 10):
            self.map[f"{i}s"] = chr(base_sou + i - 1)

        # 3. 筒子 (1p - 9p) -> U+1F019 ~ U+1F021
        base_pin = 0x1F019
        for i in range(1, 10):
            self.map[f"{i}p"] = chr(base_pin + i - 1)

        # 4. 字牌 (1z - 7z): 東南西北中發白
        # 風牌: 東南西北 (1z-4z) -> U+1F000 ~ U+1F003
        honors = ['1z', '2z', '3z', '4z'] 
        honor_codes = [0x1F000, 0x1F001, 0x1F002, 0x1F003]
        
        # 三元牌: 中發白 (5z-7z) -> U+1F004 ~ U+1F006
        dragons = ['5z', '6z', '7z']
        dragon_codes = [0x1F004, 0x1F005, 0x1F006]

        for code, unicode_val in zip(honors + dragons, honor_codes + dragon_codes):
            self.map[code] = chr(unicode_val)

        # 5. 花牌 (1f - 8f) 
        # 春夏秋冬(1-4f) + 梅蘭菊竹(5-8f)
        # 注意：Unicode 順序通常是梅蘭菊竹(U+1F026..), 春夏秋冬(U+1F022..)
        # 這裡依台灣常見習慣對應
        flowers = ['1f', '2f', '3f', '4f', '5f', '6f', '7f', '8f']
        # 對應 Unicode: 春, 夏, 秋, 冬, 梅, 蘭, 菊, 竹
        flower_unicodes = [0x1F022, 0x1F023, 0x1F024, 0x1F025, 
                           0x1F026, 0x1F027, 0x1F028, 0x1F029]
        
        for code, val in zip(flowers, flower_unicodes):
            self.map[code] = chr(val)

    def get_tile(self, code):
        """傳入代號 (如 '1m')，回傳 Unicode 符號"""
        return self.map.get(code, "?") # 找不到回傳 ?

    def convert_string(self, text_input):
        """
        將一串文字 '1m 2p 3s' 轉換成符號串
        範例輸入: "1m 5z 2p"
        範例輸出: "🀇 🀄 🀚"
        """
        result = []
        # 簡單的解析：以空格分隔
        tokens = text_input.split()
        for t in tokens:
            result.append(self.get_tile(t))
        return " ".join(result)

# --- 以下是 Tkinter 介面測試程式 ---
def main():
    converter = MahjongConverter()
    
    root = tk.Tk()
    root.title("麻將 Unicode 符號檢視器")
    root.geometry("600x500")

    # 設定字型：Windows 推薦 Segoe UI Symbol 以確保顯示正常
    # 如果顯示方塊，請嘗試改為 "Arial Unicode MS" 或 "SimSun"
    my_font = font.Font(family="Segoe UI Symbol", size=24)
    label_font = font.Font(family="Microsoft JhengHei", size=12)

    # 1. 顯示所有牌型
    frame_all = tk.LabelFrame(root, text="所有牌型總覽", padx=10, pady=10)
    frame_all.pack(fill="x", padx=10, pady=5)

    # 萬子列
    tk.Label(frame_all, text="萬子 (m):", font=label_font).grid(row=0, column=0, sticky="e")
    wan_str = "".join([converter.get_tile(f"{i}m") for i in range(1, 10)])
    tk.Label(frame_all, text=wan_str, font=my_font).grid(row=0, column=1, sticky="w")

    # 條子列
    tk.Label(frame_all, text="條子 (s):", font=label_font).grid(row=1, column=0, sticky="e")
    sou_str = "".join([converter.get_tile(f"{i}s") for i in range(1, 10)])
    tk.Label(frame_all, text=sou_str, font=my_font).grid(row=1, column=1, sticky="w")

    # 筒子列
    tk.Label(frame_all, text="筒子 (p):", font=label_font).grid(row=2, column=0, sticky="e")
    pin_str = "".join([converter.get_tile(f"{i}p") for i in range(1, 10)])
    tk.Label(frame_all, text=pin_str, font=my_font).grid(row=2, column=1, sticky="w")

    # 字牌列
    tk.Label(frame_all, text="字牌 (z):", font=label_font).grid(row=3, column=0, sticky="e")
    honor_str = "".join([converter.get_tile(f"{i}z") for i in range(1, 8)])
    tk.Label(frame_all, text=honor_str, font=my_font).grid(row=3, column=1, sticky="w")
    
    # 花牌列
    tk.Label(frame_all, text="花牌 (f):", font=label_font).grid(row=4, column=0, sticky="e")
    flower_str = "".join([converter.get_tile(f"{i}f") for i in range(1, 9)])
    tk.Label(frame_all, text=flower_str, font=my_font).grid(row=4, column=1, sticky="w")

    # 2. 互動測試區
    frame_test = tk.LabelFrame(root, text="轉換測試 (輸入代號如: 1m 5z 2p)", padx=10, pady=10)
    frame_test.pack(fill="x", padx=10, pady=5)

    entry = tk.Entry(frame_test, font=("Consolas", 14))
    entry.pack(side="left", fill="x", expand=True, padx=5)
    entry.insert(0, "1m 2m 3m 5z 5z 6z") # 預設值

    result_label = tk.Label(frame_test, text="", font=my_font, fg="blue")
    result_label.pack(side="left", padx=10)

    def on_convert():
        txt = entry.get()
        res = converter.convert_string(txt)
        result_label.config(text=res)

    btn = tk.Button(frame_test, text="轉換顯示", command=on_convert, font=label_font)
    btn.pack(side="left")

    # 初始執行一次
    on_convert()

    root.mainloop()

if __name__ == "__main__":
    main()

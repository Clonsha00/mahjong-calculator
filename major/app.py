import streamlit as st

# === 1. 保留原本的邏輯類別 (完全不用改) ===
class MahjongConverter:
    """
    負責處理麻將代號與 Unicode 轉換的類別
    """
    def __init__(self):
        self.map = {}
        self._build_map()

    def _build_map(self):
        # 萬子
        base_wan = 0x1F007
        for i in range(1, 10):
            self.map[f"{i}m"] = chr(base_wan + i - 1)
        # 條子
        base_sou = 0x1F010
        for i in range(1, 10):
            self.map[f"{i}s"] = chr(base_sou + i - 1)
        # 筒子
        base_pin = 0x1F019
        for i in range(1, 10):
            self.map[f"{i}p"] = chr(base_pin + i - 1)
        # 字牌
        honors = ['1z', '2z', '3z', '4z'] 
        honor_codes = [0x1F000, 0x1F001, 0x1F002, 0x1F003]
        dragons = ['5z', '6z', '7z']
        dragon_codes = [0x1F004, 0x1F005, 0x1F006]
        for code, unicode_val in zip(honors + dragons, honor_codes + dragon_codes):
            self.map[code] = chr(unicode_val)
        # 花牌
        flowers = ['1f', '2f', '3f', '4f', '5f', '6f', '7f', '8f']
        flower_unicodes = [0x1F022, 0x1F023, 0x1F024, 0x1F025, 
                           0x1F026, 0x1F027, 0x1F028, 0x1F029]
        for code, val in zip(flowers, flower_unicodes):
            self.map[code] = chr(val)

    def get_tile(self, code):
        return self.map.get(code, "?")

    def convert_string(self, text_input):
        result = []
        tokens = text_input.split()
        for t in tokens:
            result.append(self.get_tile(t))
        return " ".join(result)

# === 2. Streamlit 介面部分 (取代原本的 Tkinter) ===

def main():
    st.title("🀄 麻將 Unicode 符號檢視器")
    st.write("這是在 Streamlit 網頁上運行的版本，無需使用 Tkinter。")

    converter = MahjongConverter()

    # --- 顯示所有牌型 ---
    st.subheader("所有牌型總覽")
    
    # 為了讓排版漂亮，我們用 Markdown 表格
    cols = st.columns(4) # 建立四個欄位
    
    # 萬子
    wan_str = " ".join([converter.get_tile(f"{i}m") for i in range(1, 10)])
    cols[0].markdown(f"**萬子 (m)**")
    cols[0].markdown(f"<h1 style='font-size: 40px;'>{wan_str}</h1>", unsafe_allow_html=True)
    
    # 條子
    sou_str = " ".join([converter.get_tile(f"{i}s") for i in range(1, 10)])
    cols[1].markdown(f"**條子 (s)**")
    cols[1].markdown(f"<h1 style='font-size: 40px;'>{sou_str}</h1>", unsafe_allow_html=True)
    
    # 筒子
    pin_str = " ".join([converter.get_tile(f"{i}p") for i in range(1, 10)])
    cols[2].markdown(f"**筒子 (p)**")
    cols[2].markdown(f"<h1 style='font-size: 40px;'>{pin_str}</h1>", unsafe_allow_html=True)

    # 字牌
    honor_str = " ".join([converter.get_tile(f"{i}z") for i in range(1, 8)])
    cols[3].markdown(f"**字牌 (z)**")
    cols[3].markdown(f"<h1 style='font-size: 40px;'>{honor_str}</h1>", unsafe_allow_html=True)

    st.divider() # 分隔線

    # --- 互動測試區 ---
    st.subheader("轉換測試")
    user_input = st.text_input("輸入代號 (例如: 1m 5z 2p)", value="1m 2m 3m 5z 5z 6z")
    
    if user_input:
        result = converter.convert_string(user_input)
        # 使用 HTML 讓字體變大，顯示效果更好
        st.markdown(f"<div style='font-size: 60px; border: 1px solid #ddd; padding: 20px; border-radius: 10px; text-align: center;'>{result}</div>", unsafe_allow_html=True)
        st.caption("複製上面的符號即可使用")

if __name__ == "__main__":
    main()

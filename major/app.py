import streamlit as st

# === 工具函式：清洗隱形字元 ===
def clean_mahjong_tile(text):
    """
    移除 Unicode 的變體選擇符：
    \ufe0f (VS16 - Emoji Style)
    \ufe0e (VS15 - Text Style)
    並去除前後空白
    """
    if not text:
        return ""
    return text.replace('\ufe0f', '').replace('\ufe0e', '').strip()

class MahjongConverter:
    def __init__(self):
        self.map = {}         # Code -> Symbol (ex: '5z' -> '🀄')
        self.reverse_map = {} # Symbol -> Code (ex: '🀄' -> '5z')
        self._build_map()

    def _build_map(self):
        # 1. 萬子
        base_wan = 0x1F007
        for i in range(1, 10):
            self.map[f"{i}m"] = chr(base_wan + i - 1)
        # 2. 條子
        base_sou = 0x1F010
        for i in range(1, 10):
            self.map[f"{i}s"] = chr(base_sou + i - 1)
        # 3. 筒子
        base_pin = 0x1F019
        for i in range(1, 10):
            self.map[f"{i}p"] = chr(base_pin + i - 1)
        
        # 4. 字牌
        honors = ['1z', '2z', '3z', '4z'] 
        honor_codes = [0x1F000, 0x1F001, 0x1F002, 0x1F003]
        
        # 5. 三元牌 (標準設定)
        dragons = ['5z', '6z', '7z'] 
        dragon_codes = [0x1F004, 0x1F005, 0x1F006] # 紅中🀄, 青發🀅, 白板🀆
        
        for code, unicode_val in zip(honors + dragons, honor_codes + dragon_codes):
            self.map[code] = chr(unicode_val)

        # 6. 花牌
        flowers = ['1f', '2f', '3f', '4f', '5f', '6f', '7f', '8f']
        flower_unicodes = [0x1F022, 0x1F023, 0x1F024, 0x1F025, 
                           0x1F026, 0x1F027, 0x1F028, 0x1F029]
        for code, val in zip(flowers, flower_unicodes):
            self.map[code] = chr(val)

        # === 建立反向查詢表 (Symbol -> Code) ===
        # 這樣我們就能知道 '🀄' 對應 '5z'
        for code, symbol in self.map.items():
            self.reverse_map[symbol] = code

    def get_tile(self, code):
        return self.map.get(code, "?")

    def get_code(self, symbol):
        """反向查詢：給符號，回傳代號"""
        # 這裡也要先清洗一下，確保安全
        clean_s = clean_mahjong_tile(symbol)
        return self.reverse_map.get(clean_s, "未知")

    def convert_string_html(self, text_input):
        result = []
        tokens = text_input.split()
        for t in tokens:
            char = self.get_tile(t)
            result.append(f"<span>{char}</span>")
        return " ".join(result)

def main():
    st.set_page_config(page_title="麻將符號工具箱", page_icon="🀄")
    st.title("🀄 麻將 Unicode 工具箱")

    converter = MahjongConverter()

    # 使用 Tabs 分頁功能，讓介面更乾淨
    tab1, tab2 = st.tabs(["🔤 代號轉符號 (Viewer)", "🧽 符號清洗與反查 (Cleaner)"])

    # === Tab 1: 原本的功能 ===
    with tab1:
        st.subheader("常用牌型展示")
        cols = st.columns(4)
        cols[0].markdown("**萬子**")
        cols[0].markdown(f"<div style='font-size: 32px;'>{converter.convert_string_html('1m 2m 3m')}...</div>", unsafe_allow_html=True)
        cols[1].markdown("**條子**")
        cols[1].markdown(f"<div style='font-size: 32px;'>{converter.convert_string_html('1s 2s 3s')}...</div>", unsafe_allow_html=True)
        cols[2].markdown("**筒子**")
        cols[2].markdown(f"<div style='font-size: 32px;'>{converter.convert_string_html('1p 2p 3p')}...</div>", unsafe_allow_html=True)
        cols[3].markdown("**字牌**")
        cols[3].markdown(f"<div style='font-size: 32px;'>{converter.convert_string_html('5z 6z 7z')}</div>", unsafe_allow_html=True)

        st.divider()
        user_input = st.text_input("輸入代號 (例如: 1m 5z 6z)", value="1m 5z 6z 7z", key="input_code")
        if user_input:
            result = converter.convert_string_html(user_input)
            st.markdown(f"<div style='font-size: 60px; text-align: center; border: 1px solid #ddd; padding: 10px; border-radius: 10px;'>{result}</div>", unsafe_allow_html=True)

    # === Tab 2: 新增的功能 (清洗與反查) ===
    with tab2:
        st.subheader("🕵️‍♂️ 符號清洗與識別")
        st.info("這裡示範如何處理帶有「隱形字元」的麻將符號。")

        # 這裡故意提供一個帶有隱形字元的預設值 (🀄 + \ufe0e)
        dirty_default = "🀄︎" 
        
        paste_input = st.text_input("貼上一個麻將符號 (可嘗試貼上外部複製的牌)", value=dirty_default, key="input_symbol")

        if paste_input:
            col1, col2 = st.columns(2)
            
            # 1. 原始狀態分析
            raw_repr = ascii(paste_input) # 取得 Python 內部表示法 (會顯示 \ufe0e)
            with col1:
                st.markdown("🔴 **原始輸入 (Before)**")
                st.code(f"內容: {paste_input}\n長度: {len(paste_input)}\n編碼: {raw_repr}")
                if "\\ufe0" in raw_repr:
                    st.warning("⚠️ 檢測到隱形變體選擇符！")
                else:
                    st.success("✅ 輸入很乾淨")

            # 2. 清洗與識別
            cleaned_text = clean_mahjong_tile(paste_input)
            identified_code = converter.get_code(cleaned_text)
            
            with col2:
                st.markdown("🟢 **清洗後 (After)**")
                st.code(f"內容: {cleaned_text}\n長度: {len(cleaned_text)}\n編碼: {ascii(cleaned_text)}")
                
                if identified_code != "未知":
                    st.success(f"🎉 識別成功！這是：**{identified_code}**")
                    # 顯示大圖
                    st.markdown(f"<div style='font-size: 50px;'>{cleaned_text}</div>", unsafe_allow_html=True)
                else:
                    st.error("❌ 無法識別此符號 (不在麻將表中)")

if __name__ == "__main__":
    main()

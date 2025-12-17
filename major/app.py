import streamlit as st

class MahjongConverter:
    def __init__(self):
        self.map = {}
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
        # 4. 字牌 (包含紅中 5z)
        honors = ['1z', '2z', '3z', '4z'] 
        honor_codes = [0x1F000, 0x1F001, 0x1F002, 0x1F003]
        dragons = ['5z', '6z', '7z'] 
        dragon_codes = [0x1F004, 0x1F005, 0x1F006]
        
        for code, unicode_val in zip(honors + dragons, honor_codes + dragon_codes):
            self.map[code] = chr(unicode_val)

        # 5. 花牌
        flowers = ['1f', '2f', '3f', '4f', '5f', '6f', '7f', '8f']
        flower_unicodes = [0x1F022, 0x1F023, 0x1F024, 0x1F025, 
                           0x1F026, 0x1F027, 0x1F028, 0x1F029]
        for code, val in zip(flowers, flower_unicodes):
            self.map[code] = chr(val)

    def get_tile(self, code):
        return self.map.get(code, "?")

    def convert_string_html(self, text_input):
        """
        將代號轉換為 HTML 字串
        """
        result = []
        tokens = text_input.split()
        for t in tokens:
            char = self.get_tile(t)
            # 統一不加顏色樣式，跟其他牌一樣
            result.append(f"<span>{char}</span>")
                
        return " ".join(result)

def main():
    st.set_page_config(page_title="麻將符號檢視器", page_icon="🀄")
    
    st.title("🀄 麻將 Unicode 符號檢視器")
    st.write("標準版：所有牌色統一。")

    converter = MahjongConverter()

    st.subheader("常用牌型展示")
    cols = st.columns(4)
    
    # 萬子
    wan_str = converter.convert_string_html("1m 2m 3m 4m 5m")
    cols[0].markdown("**萬子**")
    cols[0].markdown(f"<div style='font-size: 40px;'>{wan_str} ...</div>", unsafe_allow_html=True)
    
    # 條子
    sou_str = converter.convert_string_html("1s 2s 3s 4s 5s")
    cols[1].markdown("**條子**")
    cols[1].markdown(f"<div style='font-size: 40px;'>{sou_str} ...</div>", unsafe_allow_html=True)
    
    # 筒子
    pin_str = converter.convert_string_html("1p 2p 3p 4p 5p")
    cols[2].markdown("**筒子**")
    cols[2].markdown(f"<div style='font-size: 40px;'>{pin_str} ...</div>", unsafe_allow_html=True)

    # 三元牌
    dragon_str = converter.convert_string_html("5z 6z 7z")
    cols[3].markdown("**三元牌**")
    cols[3].markdown(f"<div style='font-size: 40px;'>{dragon_str}</div>", unsafe_allow_html=True)

    st.divider()

    # --- 互動測試區 ---
    st.subheader("轉換測試")
    user_input = st.text_input("輸入代號 (例如: 1m 5z 6z)", value="1m 5z 6z 7z 1p")
    
    if user_input:
        result = converter.convert_string_html(user_input)
        
        st.markdown(
            f"""
            <div style='
                font-size: 60px; 
                border: 2px solid #eee; 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center;
                background-color: rgba(255,255,255,0.05);
            '>
                {result}
            </div>
            """, 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()

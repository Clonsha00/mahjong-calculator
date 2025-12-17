# ... (前面的 import, session_state, add_tile, logic 等函式保持不變) ...

# --- UI 介面開始 ---
st.title("🀄 台灣麻將台數計算機")

# === 上半部：顯示區與設定 (Dashboard) ===
dashboard_container = st.container(border=True)

with dashboard_container:
    c_hand, c_settings = st.columns([3, 1])
    
    # 1. 手牌顯示區
    with c_hand:
        st.subheader("🎴 手牌區")
        
        # 顯示手牌 (排序後)
        sorted_hand = sorted(st.session_state.hand_tiles)
        
        # 使用自訂 HTML/CSS 做一個漂亮的牌尺效果，或者簡單用 columns
        if sorted_hand:
            # 為了讓牌不換行太嚴重，我們用多一點的 columns
            cols = st.columns(17)
            for i, t in enumerate(sorted_hand):
                cols[i].button(t, key=f"h_{i}", disabled=True)
        else:
            st.info("請點擊下方按鈕新增手牌...")

        st.write("") # 空行間距
        
        # 顯示胡牌與花牌
        c_win, c_flower = st.columns([1, 2])
        with c_win:
            st.write("**🖐️ 胡/摸 (第17張)**")
            if st.session_state.winning_tile:
                st.button(st.session_state.winning_tile, key="win_btn", type="primary")
            else:
                st.button("?", disabled=True)
                
        with c_flower:
            st.write(f"**🌸 花牌 ({len(st.session_state.flower_tiles)})** - 點擊移除")
            if st.session_state.flower_tiles:
                f_cols = st.columns(8)
                for i, f in enumerate(st.session_state.flower_tiles):
                    if f_cols[i % 8].button(f, key=f"f_{i}"):
                        remove_flower(f)
                        st.rerun()
            else:
                st.caption("無花牌")

    # 2. 設定與操作區
    with c_settings:
        st.write("**⚙️ 設定**")
        st.session_state.settings['is_self_draw'] = st.checkbox("自摸", value=st.session_state.settings['is_self_draw'])
        st.session_state.settings['is_men_qing'] = st.checkbox("門清", value=st.session_state.settings['is_men_qing'])
        
        c_wind1, c_wind2 = st.columns(2)
        with c_wind1:
            st.session_state.settings['wind_round'] = st.selectbox("圈風", ["東", "南", "西", "北"], index=0)
        with c_wind2:
            st.session_state.settings['wind_seat'] = st.selectbox("門風", ["東", "南", "西", "北"], index=0)

        st.divider()
        # 操作按鈕群
        if st.button("⬅️ 刪除手牌", use_container_width=True):
            remove_last_tile()
            st.rerun()
            
        if st.button("🗑️ 全部清空", type="primary", use_container_width=True):
            reset_game()
            st.rerun()

# === 計算按鈕 (顯眼) ===
st.write("")
if st.button("🧮 開始計算台數", type="primary", use_container_width=True):
    valid_len = len(st.session_state.hand_tiles) == 16 and st.session_state.winning_tile is not None
    if not valid_len:
        st.error("❌ 牌數不足！請湊滿 16 張手牌 + 1 張胡牌。")
    else:
        score, details = calculate_tai()
        st.balloons()
        st.success(f"### 🀄 總計：{score} 台")
        if details:
            # 用一行一行的卡片顯示詳情
            st.write("---")
            st.write("**詳細明細：**")
            d_cols = st.columns(4)
            for idx, d in enumerate(details):
                d_cols[idx % 4].info(d)

# === 下半部：全展開鍵盤區 (Input) ===
st.markdown("---")
st.subheader("➕ 點擊新增牌型")

# 定義一個輔助函式來產生一整列按鈕
def render_row(title, tiles, color_bar_char="🟦"):
    st.markdown(f"**{color_bar_char} {title}**")
    cols = st.columns(9) # 標準麻將 1-9 最多 9 個位置
    for i, tile in enumerate(tiles):
        # 如果是字牌或花牌，因為數量少，我們讓按鈕寬一點，不要全部擠在左邊
        if len(tiles) < 9:
            if cols[i].button(tile, key=f"btn_{tile}", use_container_width=True):
                add_tile(tile, title[0]) # 取標題的第一個字當類別 (萬/筒/條/字/花)
                st.rerun()
        else:
            if cols[i].button(tile, key=f"btn_{tile}", use_container_width=True):
                add_tile(tile, title[0])
                st.rerun()

# 依序渲染每一行
render_row("萬子", TILES["萬"], "🔴")
render_row("筒子", TILES["筒"], "🔵")
render_row("條子", TILES["條"], "🟢")

# 字牌和花牌可以並排顯示，或是分兩行
c_zi, c_hua = st.columns([1, 1])
with c_zi:
    st.markdown("**⬛ 字牌**")
    cols = st.columns(4) # 4行顯示
    for i, t in enumerate(TILES["字"]):
        if cols[i % 4].button(t, key=f"btn_{t}", use_container_width=True):
            add_tile(t, "字")
            st.rerun()

with c_hua:
    st.markdown("**🌸 花牌**")
    cols = st.columns(4)
    for i, t in enumerate(TILES["花"]):
        if cols[i % 4].button(t, key=f"btn_{t}", use_container_width=True):
            add_tile(t, "花")
            st.rerun()

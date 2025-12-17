# ... (前方程式碼 MahjongLogic 與 TaiCalculator 保持不變) ...

# ==========================================
# 3. Streamlit 介面 (Mobile Layout Optimized)
# ==========================================
def get_tile_name(tid):
    # 簡化顯示，適合手機
    if tid < 9: return f"{tid+1}萬"
    elif tid < 18: return f"{tid-8}筒"
    elif tid < 27: return f"{tid-17}索"
    else: return ["東", "南", "西", "北", "中", "發", "白"][tid-27]

def main():
    st.set_page_config(page_title="麻將軍師", layout="centered", initial_sidebar_state="collapsed")
    
    # Init Session State
    if 'hand_tiles' not in st.session_state: st.session_state.hand_tiles = []
    if 'open_sets' not in st.session_state: st.session_state.open_sets = []
    if 'drawn_tile' not in st.session_state: st.session_state.drawn_tile = None
    if 'multiplier' not in st.session_state: st.session_state.multiplier = 1
    
    # --- Mobile CSS 強力優化 ---
    st.markdown("""
    <style>
    /* 1. 減少邊距，讓手機畫面更滿 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }

    /* 2. 強制 Column 不堆疊 (關鍵！解決手機排版跑掉問題) */
    /* 這會讓所有 st.columns 在手機上依然保持並排，不會變成垂直一列 */
    div[data-testid="column"] {
        min-width: 0 !important; /* 允許縮到最小，防止被撐開 */
        flex: 1 !important;      /* 平均分配寬度 */
        padding: 0 2px !important; /* 減少欄位間距 */
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 0.2rem !important; /* 減少按鈕之間的間隙 */
    }

    /* 3. 按鈕樣式統一 */
    div.stButton > button {
        width: 100%;
        height: 3.8rem;      /* 固定高度，方便手指點擊 */
        border-radius: 8px;  /* 圓角 */
        font-size: 1.2rem !important; /* 字體加大 */
        font-weight: 700;
        padding: 0px !important; /* 減少內距以容納文字 */
        line-height: 1.2 !important;
    }

    /* 4. 手牌區塊 (HUD) - 使用 Flexbox 自動換行 */
    .hand-display {
        display: flex;
        flex-wrap: wrap;       /* 空間不夠自動換行 */
        justify-content: center;
        gap: 4px;             /* 牌之間的間距 */
        background-color: #f0f8ff;
        padding: 10px 5px;
        border-radius: 12px;
        border: 2px solid #81ecec;
        margin-bottom: 15px;
        min-height: 60px;
    }
    
    .tile-box {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.2rem;       /* 固定牌寬 */
        height: 3.0rem;      /* 固定牌高 */
        background: white;
        border: 1px solid #b2bec3;
        border-radius: 4px;
        font-weight: bold;
        font-size: 1.0rem;
        color: #2d3436;
        box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 摸牌的樣式 */
    .drawn-tile-box {
        background: #ff7675;
        color: white;
        border-color: #d63031;
        margin-left: 8px; /* 與手牌區隔開 */
    }
    
    /* 吃碰槓的樣式 */
    .set-group {
        display: flex;
        margin-right: 6px;
        background: #dfe6e9;
        padding: 2px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 1. 設定區 (收合) ---
    with st.expander("⚙️ 設定與規則", expanded=False):
        c1, c2 = st.columns(2)
        round_wind = c1.selectbox("圈風", [0,1,2,3], format_func=lambda x: ["東","南","西","北"][x])
        seat_wind = c2.selectbox("門風", [0,1,2,3], index=1, format_func=lambda x: ["東","南","西","北"][x])
        
        c3, c4 = st.columns(2)
        base_money = c3.number_input("底", value=30, step=10)
        tai_money = c4.number_input("台", value=10, step=5)
        
        rule_mode = st.radio("計分模式", ["strict_flower", "no_flower_loose_word"], 
                             format_func=lambda x: "正花正字" if x=="strict_flower" else "無花見字")
        
        st.caption("花牌 & 特殊")
        cols = st.columns(4) 
        flowers = [False]*8
        f_labels = ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
        for i, label in enumerate(f_labels):
            flowers[i] = cols[i%4].checkbox(label, value=False)
            
        col_s1, col_s2 = st.columns(2)
        is_self_draw = col_s1.checkbox("自摸")
        is_kong_bloom = col_s2.checkbox("槓上開花")
        is_last_tile = col_s1.checkbox("海底撈月")
        is_robbing_kong = col_s2.checkbox("搶槓")
        is_seven_snatch = col_s1.checkbox("七搶一")
        
        if st.button("🔄 重置新局"):
            st.session_state.hand_tiles = []
            st.session_state.open_sets = []
            st.session_state.drawn_tile = None
            st.rerun()

    # --- 2. 視覺化手牌區 (Flex Layout) ---
    # 計算總張數
    total_units = len(st.session_state.hand_tiles) + len(st.session_state.open_sets) * 3
    if st.session_state.drawn_tile is not None: total_units += 1
    
    # 建立 HTML
    html_parts = []
    
    # A. 顯示吃碰槓
    for s in st.session_state.open_sets:
        set_html = "<div class='set-group'>"
        n = get_tile_name(s['tiles'][0])
        type_map = {'pong':'碰', 'kang':'槓', 'chow':'吃'}
        if s['type'] == 'chow':
             tiles_show = [get_tile_name(t)[0] for t in s['tiles']] # 只取數字
             for char in tiles_show:
                 set_html += f"<div class='tile-box' style='background:#b2bec3; width:1.5rem; height:2.2rem; font-size:0.8rem;'>{char}</div>"
        else:
             set_html += f"<div class='tile-box' style='background:#b2bec3; width:3.5rem; height:2.2rem;'>{n}{type_map[s['type']][0]}</div>"
        set_html += "</div>"
        html_parts.append(set_html)
    
    # B. 顯示手牌
    display_hand = sorted(st.session_state.hand_tiles)
    for t in display_hand:
        html_parts.append(f"<div class='tile-box'>{get_tile_name(t)}</div>")
    
    # C. 顯示摸牌 (獨立顯示)
    draw_html = ""
    if st.session_state.drawn_tile is not None:
        draw_html = f"<div class='tile-box drawn-tile-box'>{get_tile_name(st.session_state.drawn_tile)}</div>"

    st.markdown(f"""
    <div style='text-align:center; font-size:0.8em; color:#666; margin-bottom:2px;'>張數: {total_units} / 17</div>
    <div class='hand-display'>
        {''.join(html_parts)}
        {draw_html}
    </div>
    """, unsafe_allow_html=True)

    # --- 3. 鍵盤輸入區 (Grid Layout) ---
    # 模式選擇與控制
    col_ctrl_1, col_ctrl_2 = st.columns([2, 1])
    with col_ctrl_1:
        mode = st.radio("模式", ["normal", "pong", "kang", "chow"], 
                        horizontal=True, label_visibility="collapsed",
                        format_func=lambda x: {"normal":"手牌", "pong":"碰", "kang":"槓", "chow":"吃"}[x])
    with col_ctrl_2:
        if mode == "normal":
             multiplier = st.checkbox("連打", value=False)
             multiplier = 2 if multiplier else 1
        else:
             multiplier = 1

    # 鍵盤 Tabs
    tabs = st.tabs(["萬", "筒", "索", "字"])
    
    # 定義添加牌的邏輯
    def add_tile(tid):
        current_u = len(st.session_state.hand_tiles) + len(st.session_state.open_sets) * 3
        if st.session_state.drawn_tile is not None: current_u += 1
        
        total_card = st.session_state.hand_tiles.count(tid)
        if st.session_state.drawn_tile == tid: total_card += 1
        for s in st.session_state.open_sets: total_card += s['tiles'].count(tid)

        if mode == "normal":
            if current_u + multiplier > 17: st.toast("❌ 牌數過多！"); return
            if total_card + multiplier > 4: st.toast("❌ 牌數超過4張！"); return
            for _ in range(multiplier):
                max_hand = 16 - (len(st.session_state.open_sets)*3)
                if len(st.session_state.hand_tiles) < max_hand:
                    st.session_state.hand_tiles.append(tid)
                else:
                    st.session_state.drawn_tile = tid
                    break 
        elif mode == "pong":
            if current_u >= 14 or st.session_state.drawn_tile is not None: st.toast("空間不足"); return
            if total_card + 3 > 4: st.toast("牌數不足"); return
            st.session_state.open_sets.append({'type':'pong', 'tiles':[tid]*3})
        elif mode == "kang":
            if current_u >= 14 or st.session_state.drawn_tile is not None: st.toast("空間不足"); return
            if total_card + 4 > 4: st.toast("牌數不足"); return
            st.session_state.open_sets.append({'type':'kang', 'tiles':[tid]*4})
        elif mode == "chow":
            if tid >= 27 or tid%9 > 6: st.toast("無法吃牌"); return
            if current_u >= 14 or st.session_state.drawn_tile is not None: st.toast("空間不足"); return
            st.session_state.open_sets.append({'type':'chow', 'tiles':[tid, tid+1, tid+2]})

    suits = [range(0,9), range(9,18), range(18,27), range(27,34)]
    
    # 渲染鍵盤
    for idx, suit_range in enumerate(suits):
        with tabs[idx]:
            # 這裡使用 3 個 columns，CSS 會強制它們在手機上保持並排
            cols = st.columns(3)
            for i, tid in enumerate(suit_range):
                # 字牌特殊排版 (將中發白放到下一行，這裡用簡單的邏輯)
                col_idx = i % 3
                
                # 特殊處理字牌最後一行 (讓中發白排整齊)
                if idx == 3 and i >= 4: 
                    # 重新計算 col_idx 讓它從左邊開始
                    col_idx = (i - 4) % 3
                    # 如果是中發白的第一個(中)，要確保換行 (Streamlit 自動會換，只要 column 數對)
                
                label = get_tile_name(tid)
                if idx < 3: label = label[0] # 萬筒索只顯示數字，字體更大更清楚
                
                if cols[col_idx].button(label, key=f"btn_{tid}"):
                    add_tile(tid)
                    st.rerun()

    # --- 4. 功能按鈕區 ---
    st.markdown("<br>", unsafe_allow_html=True)
    c_del, c_clr = st.columns(2)
    if c_del.button("⌫ 刪除", type="secondary"):
        if st.session_state.drawn_tile is not None:
            st.session_state.drawn_tile = None
        elif st.session_state.hand_tiles:
            st.session_state.hand_tiles.pop()
        elif st.session_state.open_sets:
            st.session_state.open_sets.pop()
        st.rerun()
        
    if c_clr.button("🗑️ 清空"):
        st.session_state.hand_tiles = []
        st.session_state.open_sets = []
        st.session_state.drawn_tile = None
        st.rerun()

    # --- 5. 智慧分析結果 ---
    st.markdown("---")
    
    # (此處保持原有的分析邏輯與 UI 結構，僅將按鈕放入 columns 即可)
    # 情境 A: 16張 (聽牌檢查)
    if total_units == 16 and st.session_state.drawn_tile is None:
        waiting = MahjongLogic.get_waiting_tiles(st.session_state.hand_tiles)
        if not waiting:
            st.info("尚未聽牌")
        else:
            st.success(f"🔥 聽牌：{len(waiting)} 洞")
            w_cols = st.columns(4)
            for i, w in enumerate(waiting):
                if w_cols[i%4].button(f"胡 {get_tile_name(w)}", type="primary"):
                    show_result(w, round_wind, seat_wind, is_self_draw, flowers, 
                                is_kong_bloom, is_last_tile, is_robbing_kong, is_seven_snatch,
                                rule_mode, base_money, tai_money)

    # 情境 B: 17張 (自摸/捨牌)
    elif total_units == 17 and st.session_state.drawn_tile is not None:
        full_hand = st.session_state.hand_tiles + [st.session_state.drawn_tile]
        full_hand.sort()
        
        c_counts = [0]*34
        for t in full_hand: c_counts[t] += 1
        
        if MahjongLogic.check_win(c_counts):
            st.markdown(f"### 🎉 自摸：{get_tile_name(st.session_state.drawn_tile)}")
            if st.button("查看台數與金額", type="primary", use_container_width=True):
                show_result(st.session_state.drawn_tile, round_wind, seat_wind, True, flowers,
                            is_kong_bloom, is_last_tile, is_robbing_kong, is_seven_snatch,
                            rule_mode, base_money, tai_money)
            st.markdown("---")

        st.subheader("💡 捨牌建議")
        sug = MahjongLogic.analyze_discard_options(full_hand)
        if not sug:
            st.caption("無建議 (死牌)")
        else:
            for opt in sug:
                d_name = get_tile_name(opt['discard'])
                rem = opt['remaining']
                
                # 使用 container 讓建議區塊更整齊
                with st.container():
                    c_btn, c_info = st.columns([1.5, 3.5])
                    if c_btn.button(f"打 {d_name}", key=f"dis_{opt['discard']}"):
                        if st.session_state.drawn_tile == opt['discard']:
                            st.session_state.drawn_tile = None
                        elif opt['discard'] in st.session_state.hand_tiles:
                            st.session_state.hand_tiles.remove(opt['discard'])
                            if st.session_state.drawn_tile is not None:
                                st.session_state.hand_tiles.append(st.session_state.drawn_tile)
                                st.session_state.drawn_tile = None
                            st.session_state.hand_tiles.sort()
                        st.rerun()
                    
                    c_info.markdown(
                        f"<div style='line-height:1.2; padding-top:5px;'>"
                        f"<b>聽 {len(opt['waiting'])} 洞</b> (剩{rem}張)<br>"
                        f"<span style='color:#666; font-size:0.9em;'>{' '.join([get_tile_name(w) for w in opt['waiting']])}</span>"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

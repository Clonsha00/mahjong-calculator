import streamlit as st
from collections import Counter

# --- 1. 設定頁面配置 (必須在程式碼最上方) ---
st.set_page_config(page_title="台灣麻將台數計算機", layout="wide", page_icon="🀄")

# --- CSS樣式優化 (讓按鈕高一點，比較好按) ---
st.markdown("""
<style>
    div.stButton > button:first-child {
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 初始化 Session State (變數儲存) ---
default_states = {
    'hand_tiles': [],       # 手牌
    'winning_tile': None,   # 胡牌
    'flower_tiles': [],     # 花牌
    'settings': {           # 額外設定
        'is_self_draw': False, # 自摸
        'is_men_qing': False,  # 門清
        'wind_round': "東",    # 圈風
        'wind_seat': "東"      # 門風
    }
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. 定義牌資料 ---
TILES = {
    "萬": [f"{i}萬" for i in range(1, 10)],
    "筒": [f"{i}筒" for i in range(1, 10)],
    "條": [f"{i}條" for i in range(1, 10)],
    "字": ["東", "南", "西", "北", "中", "發", "白"],
    "花": ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
}

# --- 4. 邏輯函式區域 ---

# 新增牌 (含防呆機制)
def add_tile(tile, category):
    # 花牌限制 (1張)
    if category == "花":
        if tile in st.session_state.flower_tiles:
            st.toast(f"⚠️ 花牌「{tile}」已經有了！", icon="🚫")
            return
        st.session_state.flower_tiles.append(tile)
        return

    # 普通牌限制 (4張)
    count_in_hand = st.session_state.hand_tiles.count(tile)
    count_in_winning = 1 if st.session_state.winning_tile == tile else 0
    
    if (count_in_hand + count_in_winning) >= 4:
        st.toast(f"⚠️ 「{tile}」最多只能有 4 張！", icon="🚫")
        return

    # 新增流程
    current_len = len(st.session_state.hand_tiles)
    has_winning = st.session_state.winning_tile is not None

    if current_len < 16:
        st.session_state.hand_tiles.append(tile)
    elif current_len == 16 and not has_winning:
        st.session_state.winning_tile = tile
    else:
        st.toast("⚠️ 牌數已滿 (16張 + 1張胡牌)！", icon="🛑")

# 移除最後一張牌
def remove_last_tile():
    if st.session_state.winning_tile:
        st.session_state.winning_tile = None
    elif st.session_state.hand_tiles:
        st.session_state.hand_tiles.pop()
    else:
        st.toast("沒有牌可以刪除了", icon="🗑️")

# 移除特定花牌
def remove_flower(tile):
    if tile in st.session_state.flower_tiles:
        st.session_state.flower_tiles.remove(tile)

# 重置遊戲
def reset_game():
    st.session_state.hand_tiles = []
    st.session_state.winning_tile = None
    st.session_state.flower_tiles = []

# --- 5. 核心演算法區域 ---

# 檢查七對子
def check_seven_pairs(counts):
    total_count = sum(counts.values())
    if total_count != 17: return False
    
    pairs = 0
    for tile, num in counts.items():
        if num == 2: pairs += 1
        elif num == 4: pairs += 2
        else: return False
    return pairs == 8

# 檢查碰碰胡
def check_peng_peng_hu(counts):
    for tile in counts:
        if counts[tile] >= 2: # 假設這是將眼
            temp_counts = counts.copy()
            temp_counts[tile] -= 2
            
            is_all_triplets = True
            for t, num in temp_counts.items():
                if num == 0: continue
                if num not in [3, 4]: # 必須是刻子或槓
                    is_all_triplets = False
                    break
            
            if is_all_triplets:
                return True
    return False

# 計算台數主函式
def calculate_tai():
    hand = st.session_state.hand_tiles + ([st.session_state.winning_tile] if st.session_state.winning_tile else [])
    flowers = st.session_state.flower_tiles
    settings = st.session_state.settings
    
    counts = Counter(hand)
    details = []
    total_tai = 0
    
    # A. 花色結構互斥判斷
    suits = set()
    has_honors = False
    for t in hand:
        if "萬" in t: suits.add("萬")
        elif "筒" in t: suits.add("筒")
        elif "條" in t: suits.add("條")
        else: has_honors = True

    if len(suits) == 0 and has_honors:
        details.append("字一色 (16台)")
        total_tai += 16
    elif len(suits) == 1 and not has_honors:
        details.append("清一色 (8台)")
        total_tai += 8
    elif len(suits) == 1 and has_honors:
        details.append("混一色 (4台)")
        total_tai += 4

    # B. 牌型結構互斥判斷
    if check_seven_pairs(counts):
        details.append("七對子/嚦咕嚦咕 (8台)")
        total_tai += 8
    else:
        if check_peng_peng_hu(counts):
            details.append("碰碰胡 (4台)")
            total_tai += 4

    # C. 三元牌與風牌
    for dragon in ["中", "發", "白"]:
        if counts[dragon] >= 3:
            details.append(f"{dragon}刻 (1台)")
            total_tai += 1
            
    wind_tiles = ["東", "南", "西", "北"]
    round_w = settings['wind_round']
    seat_w = settings['wind_seat']
    
    if counts[round_w] >= 3:
        details.append(f"圈風{round_w} (1台)")
        total_tai += 1
    if counts[seat_w] >= 3:
        details.append(f"門風{seat_w} (1台)")
        total_tai += 1

    # D. 運氣與狀態 (門清自摸)
    is_men_qing = settings['is_men_qing']
    is_self_draw = settings['is_self_draw']
    
    if is_men_qing and is_self_draw:
        details.append("門清自摸 (3台)")
        total_tai += 3
    else:
        if is_men_qing:
            details.append("門清 (1台)")
            total_tai += 1
        if is_self_draw:
            details.append("自摸 (1台)")
            total_tai += 1

    # E. 花牌
    if flowers:
        details.append(f"花牌 x{len(flowers)} ({len(flowers)}台)")
        total_tai += len(flowers)

    return total_tai, details

# --- 6. UI 介面 (全鍵盤展開版) ---

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
    # 這裡可以視需求決定是否允許 七對子 先算
    if not valid_len:
        st.error("❌ 牌數不足！請湊滿 16 張手牌 + 1 張胡牌。")
    else:
        score, details = calculate_tai()
        st.balloons()
        st.success(f"### 🀄 總計：{score} 台")
        if details:
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
        # 如果是字牌或花牌，讓按鈕寬一點，不要全部擠在左邊
        if len(tiles) < 9:
            if cols[i].button(tile, key=f"btn_{tile}", use_container_width=True):
                add_tile(tile, title[0]) # 取標題的第一個字當類別
                st.rerun()
        else:
            if cols[i].button(tile, key=f"btn_{tile}", use_container_width=True):
                add_tile(tile, title[0])
                st.rerun()

# 依序渲染每一行
render_row("萬子", TILES["萬"], "🔴")
render_row("筒子", TILES["筒"], "🔵")
render_row("條子", TILES["條"], "🟢")

# 字牌和花牌並排顯示
c_zi, c_hua = st.columns([1, 1])
with c_zi:
    st.markdown("**⬛ 字牌**")
    cols = st.columns(4) 
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

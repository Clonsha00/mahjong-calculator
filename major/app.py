import streamlit as st
from collections import Counter

# --- 設定頁面配置 ---
st.set_page_config(page_title="台灣麻將台數計算機", layout="wide", page_icon="🀄")

# --- CSS樣式優化 (選用) ---
st.markdown("""
<style>
    div.stButton > button:first-child {
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 初始化 Session State ---
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

# --- 定義牌資料 ---
TILES = {
    "萬": [f"{i}萬" for i in range(1, 10)],
    "筒": [f"{i}筒" for i in range(1, 10)],
    "條": [f"{i}條" for i in range(1, 10)],
    "字": ["東", "南", "西", "北", "中", "發", "白"],
    "花": ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
}

# --- 邏輯函式：新增牌 (含防呆) ---
def add_tile(tile, category):
    # 1. 花牌限制 (1張)
    if category == "花":
        if tile in st.session_state.flower_tiles:
            st.toast(f"⚠️ 花牌「{tile}」已經有了！", icon="🚫")
            return
        st.session_state.flower_tiles.append(tile)
        return

    # 2. 普通牌限制 (4張)
    count_in_hand = st.session_state.hand_tiles.count(tile)
    count_in_winning = 1 if st.session_state.winning_tile == tile else 0
    
    if (count_in_hand + count_in_winning) >= 4:
        st.toast(f"⚠️ 「{tile}」最多只能有 4 張！", icon="🚫")
        return

    # 3. 新增流程
    current_len = len(st.session_state.hand_tiles)
    has_winning = st.session_state.winning_tile is not None

    if current_len < 16:
        st.session_state.hand_tiles.append(tile)
    elif current_len == 16 and not has_winning:
        st.session_state.winning_tile = tile
    else:
        st.toast("⚠️ 牌數已滿 (16張 + 1張胡牌)！", icon="🛑")

# --- 邏輯函式：移除牌 ---
def remove_last_tile():
    if st.session_state.winning_tile:
        st.session_state.winning_tile = None
    elif st.session_state.hand_tiles:
        st.session_state.hand_tiles.pop()
    else:
        st.toast("沒有牌可以刪除了", icon="🗑️")

def remove_flower(tile):
    if tile in st.session_state.flower_tiles:
        st.session_state.flower_tiles.remove(tile)

def reset_game():
    st.session_state.hand_tiles = []
    st.session_state.winning_tile = None
    st.session_state.flower_tiles = []

# --- 核心演算法：檢查七對子 (嚦咕嚦咕) ---
def check_seven_pairs(counts):
    # 邏輯：必須是 8 個對子 (16張) + 胡牌湊成對 -> 總共是 8 組 Pair
    # 但因為輸入是 hand + win，總數 17 張。
    # 正常七對子：7個對子 + 1個刻子(或3張)是不對的。
    # 台灣麻將七對子(8對)：必需是 16 張手牌，聽牌單釣，胡牌後變 17 張。
    # 檢查方式：總張數17，且所有牌的數量都是 2 或 4 (4張當作2對)
    total_count = sum(counts.values())
    if total_count != 17: return False
    
    pairs = 0
    for tile, num in counts.items():
        if num == 2: pairs += 1
        elif num == 4: pairs += 2
        else: return False # 只要有單張或3張就不算
    
    return pairs == 8

# --- 核心演算法：檢查碰碰胡 (簡單版) ---
def check_peng_peng_hu(counts):
    # 邏輯：移除一個對子(將眼)後，剩下的牌必須全為刻子(3張)或槓(4張)
    # 嘗試把每一種牌當作將眼
    for tile in counts:
        if counts[tile] >= 2:
            temp_counts = counts.copy()
            temp_counts[tile] -= 2 # 移除將眼
            
            is_all_triplets = True
            for t, num in temp_counts.items():
                if num == 0: continue
                if num not in [3, 4]: # 必須是 3 或 4
                    is_all_triplets = False
                    break
            
            if is_all_triplets:
                return True
    return False

# --- 核心演算法：計算台數 (完整版) ---
def calculate_tai():
    hand = st.session_state.hand_tiles + ([st.session_state.winning_tile] if st.session_state.winning_tile else [])
    flowers = st.session_state.flower_tiles
    settings = st.session_state.settings
    
    counts = Counter(hand)
    details = []
    total_tai = 0
    
    # === 1. 花色結構互斥判斷 ===
    suits = set()
    has_honors = False
    for t in hand:
        if "萬" in t: suits.add("萬")
        elif "筒" in t: suits.add("筒")
        elif "條" in t: suits.add("條")
        else: has_honors = True # 字牌

    is_id_one_color = False
    
    if len(suits) == 0 and has_honors:
        details.append("字一色 (16台)")
        total_tai += 16
        is_id_one_color = True
    elif len(suits) == 1 and not has_honors:
        details.append("清一色 (8台)")
        total_tai += 8
    elif len(suits) == 1 and has_honors:
        details.append("混一色 (4台)")
        total_tai += 4

    # === 2. 牌型結構互斥判斷 ===
    # 優先檢查七對子 (通常較大或結構特殊)
    if check_seven_pairs(counts):
        details.append("七對子/嚦咕嚦咕 (8台)")
        total_tai += 8
    else:
        # 檢查碰碰胡
        if check_peng_peng_hu(counts):
            details.append("碰碰胡 (4台)")
            total_tai += 4
            # 註：字一色通常包含碰碰胡，這裡累加。若規則不同可在此調整 logic

    # === 3. 三元牌與風牌 (可累加) ===
    # 中發白
    for dragon in ["中", "發", "白"]:
        if counts[dragon] >= 3:
            details.append(f"{dragon}刻 (1台)")
            total_tai += 1
            
    # 圈風與門風
    wind_tiles = ["東", "南", "西", "北"]
    round_w = settings['wind_round']
    seat_w = settings['wind_seat']
    
    if counts[round_w] >= 3:
        details.append(f"圈風{round_w} (1台)")
        total_tai += 1
    if counts[seat_w] >= 3:
        details.append(f"門風{seat_w} (1台)")
        total_tai += 1

    # === 4. 運氣與狀態 (門清自摸互斥) ===
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

    # === 5. 花牌 ===
    if flowers:
        details.append(f"花牌 x{len(flowers)} ({len(flowers)}台)")
        total_tai += len(flowers)

    return total_tai, details

# --- UI 介面 ---
st.title("🀄 台灣麻將台數計算機")

# 側邊欄：環境設定
with st.sidebar:
    st.header("⚙️ 牌局設定")
    st.session_state.settings['is_self_draw'] = st.checkbox("自摸 (胡牌者)", value=st.session_state.settings['is_self_draw'])
    st.session_state.settings['is_men_qing'] = st.checkbox("門清 (無吃碰明槓)", value=st.session_state.settings['is_men_qing'])
    st.divider()
    st.session_state.settings['wind_round'] = st.selectbox("圈風", ["東", "南", "西", "北"], index=0)
    st.session_state.settings['wind_seat'] = st.selectbox("門風", ["東", "南", "西", "北"], index=0)
    
    st.divider()
    if st.button("🗑️ 清空所有", type="primary"):
        reset_game()
        st.rerun()

# 主畫面
col_hand, col_input = st.columns([5, 4])

with col_hand:
    st.subheader("🎴 目前手牌")
    hand_container = st.container(border=True)
    with hand_container:
        # 手牌區
        sorted_hand = sorted(st.session_state.hand_tiles)
        st.write(f"手牌 ({len(st.session_state.hand_tiles)}/16)")
        
        if sorted_hand:
            cols = st.columns(8) # 分兩行顯示比較整齊
            for i, t in enumerate(sorted_hand):
                cols[i % 8].button(t, key=f"h_{i}", disabled=True)
        else:
            st.info("請從右側選擇牌型")

        st.divider()
        
        # 胡牌區
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("🖐️ **胡/摸** (第17張)")
            if st.session_state.winning_tile:
                st.button(st.session_state.winning_tile, key="win_btn", type="primary")
            else:
                st.button("?", disabled=True)
        
        with c2:
            st.write(f"🌸 **花牌** ({len(st.session_state.flower_tiles)})")
            if st.session_state.flower_tiles:
                f_cols = st.columns(4)
                for i, f in enumerate(st.session_state.flower_tiles):
                    if f_cols[i % 4].button(f, key=f"f_{i}"):
                        remove_flower(f) # 點擊花牌可移除
                        st.rerun()

    # 操作按鈕
    if st.button("⬅️ 刪除上一張手牌", use_container_width=True):
        remove_last_tile()
        st.rerun()

    # 計算結果區
    st.divider()
    if st.button("🧮 計算台數", type="primary", use_container_width=True):
        # 基本檢查
        valid_len = len(st.session_state.hand_tiles) == 16 and st.session_state.winning_tile is not None
        # 特殊：七對子如果是直接選滿17張，邏輯也通
        if not valid_len:
            st.error("❌ 牌數錯誤！必須是 16 張手牌 + 1 張胡牌。")
        else:
            score, details = calculate_tai()
            st.balloons()
            st.success(f"### 總計：{score} 台")
            if details:
                st.write("詳細明細：")
                for d in details:
                    st.write(f"- {d}")
            else:
                st.write("無特殊牌型 (底台請自行約定)")

with col_input:
    st.subheader("➕ 選擇牌型")
    tabs = st.tabs(["萬", "筒", "條", "字", "花"])
    
    def render_buttons(tile_list, category):
        cols = st.columns(5)
        for i, tile in enumerate(tile_list):
            if cols[i % 5].button(tile, key=f"btn_{tile}"):
                add_tile(tile, category)
                st.rerun()

    with tabs[0]: render_buttons(TILES["萬"], "萬")
    with tabs[1]: render_buttons(TILES["筒"], "筒")
    with tabs[2]: render_buttons(TILES["條"], "條")
    with tabs[3]: render_buttons(TILES["字"], "字")
    with tabs[4]: render_buttons(TILES["花"], "花")

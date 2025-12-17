import streamlit as st
from collections import Counter

# --- 設定頁面配置 ---
st.set_page_config(page_title="台灣麻將台數計算機", layout="wide")

# --- 初始化 Session State (儲存變數) ---
if 'hand_tiles' not in st.session_state:
    st.session_state.hand_tiles = []  # 手牌 (最多16張)
if 'winning_tile' not in st.session_state:
    st.session_state.winning_tile = None  # 胡的那張牌 (第17張)
if 'flower_tiles' not in st.session_state:
    st.session_state.flower_tiles = []  # 花牌

# --- 定義牌的資料 ---
TILES = {
    "萬": [f"{i}萬" for i in range(1, 10)],
    "筒": [f"{i}筒" for i in range(1, 10)],
    "條": [f"{i}條" for i in range(1, 10)],
    "字": ["東", "南", "西", "北", "中", "發", "白"],
    "花": ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
}

# --- 輔助函式：新增牌 (含數量限制) ---
def add_tile(tile, category):
    # 1. 花牌檢查：限制1張
    if category == "花":
        if tile in st.session_state.flower_tiles:
            st.toast(f"⚠️ 花牌「{tile}」已經有了！", icon="🚫")
            return
        st.session_state.flower_tiles.append(tile)
        return

    # 2. 普通牌檢查：限制4張
    # 統計目前手牌中該牌的數量
    count_in_hand = st.session_state.hand_tiles.count(tile)
    # 檢查胡的那張牌是不是也是這張
    count_in_winning = 1 if st.session_state.winning_tile == tile else 0
    
    if (count_in_hand + count_in_winning) >= 4:
        st.toast(f"⚠️ 「{tile}」最多只能有 4 張！", icon="🚫")
        return

    # 3. 新增邏輯
    current_len = len(st.session_state.hand_tiles)
    has_winning = st.session_state.winning_tile is not None

    if current_len < 16:
        st.session_state.hand_tiles.append(tile)
    elif current_len == 16 and not has_winning:
        st.session_state.winning_tile = tile
    else:
        st.toast("⚠️ 牌數已滿 (16張 + 1張胡牌)！", icon="🛑")

# --- 輔助函式：移除指定牌 (從手牌中移除最後一張該花色的牌，簡單實作) ---
def remove_last_tile():
    if st.session_state.winning_tile:
        st.session_state.winning_tile = None
    elif st.session_state.hand_tiles:
        st.session_state.hand_tiles.pop()
    else:
        st.toast("沒有牌可以刪除了", icon="🗑️")

# --- 輔助函式：重置 ---
def reset_game():
    st.session_state.hand_tiles = []
    st.session_state.winning_tile = None
    st.session_state.flower_tiles = []

# --- 核心邏輯：計算台數 (範例) ---
def calculate_tai():
    hand = st.session_state.hand_tiles + ([st.session_state.winning_tile] if st.session_state.winning_tile else [])
    flowers = st.session_state.flower_tiles
    
    tai_details = []
    total_tai = 0
    
    # 計算所有牌的數量
    counts = Counter(hand)
    
    # 1. 花牌計台
    if len(flowers) > 0:
        tai_details.append(f"花牌 x{len(flowers)} ({len(flowers)}台)")
        total_tai += len(flowers)
        
    # 2. 三元牌 (中發白) 刻子
    for dragon in ["中", "發", "白"]:
        if counts[dragon] >= 3:
            tai_details.append(f"{dragon}刻 (1台)")
            total_tai += 1
    
    # 3. 清一色 / 混一色
    suits = set()
    for t in hand:
        if "萬" in t: suits.add("萬")
        elif "筒" in t: suits.add("筒")
        elif "條" in t: suits.add("條")
        elif t in ["東", "南", "西", "北", "中", "發", "白"]: suits.add("字")
    
    if len(suits) == 1 and "字" not in suits:
        tai_details.append("清一色 (8台)")
        total_tai += 8
    elif len(suits) == 2 and "字" in suits and len(suits - {"字"}) == 1:
        tai_details.append("混一色 (4台)")
        total_tai += 4

    return total_tai, tai_details

# --- UI 介面 ---
st.title("🀄 台灣麻將台數計算機")

col_display, col_controls = st.columns([2, 1])

with col_controls:
    c1, c2 = st.columns(2)
    if c1.button("🔄 重置", type="primary", use_container_width=True):
        reset_game()
        st.rerun()
    if c2.button("⬅️ 刪除", use_container_width=True):
        remove_last_tile()
        st.rerun()

# --- 顯示目前手牌 ---
st.markdown("### 🎴 目前手牌")
hand_container = st.container(border=True)

with hand_container:
    # 顯示手牌
    sorted_hand = sorted(st.session_state.hand_tiles)
    st.caption(f"手牌數量: {len(st.session_state.hand_tiles)} / 16")
    
    if sorted_hand:
        # 使用 flex wrapping 的 CSS 技巧來顯示牌，或者簡單用 columns
        cols = st.columns(17)
        for idx, tile in enumerate(sorted_hand):
            cols[idx].button(tile, key=f"hand_{idx}", disabled=True)
    else:
        st.info("請點擊下方按鈕新增手牌")

    st.write("---")
    
    # 顯示胡牌
    c_win, c_flower = st.columns([1, 3])
    with c_win:
        st.caption("胡牌/摸牌 (第17張)")
        if st.session_state.winning_tile:
            st.button(st.session_state.winning_tile, key="win_tile_btn", type="primary")
        else:
            st.button("?", disabled=True)
            
    with c_flower:
        st.caption(f"花牌 ({len(st.session_state.flower_tiles)})")
        if st.session_state.flower_tiles:
            st.write(" ".join([f"[{f}]" for f in st.session_state.flower_tiles]))
        else:
            st.write("無")

# --- 按鈕輸入區 ---
st.markdown("### ➕ 選擇牌型")
tabs = st.tabs(["萬子", "筒子", "條子", "字牌", "花牌"])

def create_buttons(tile_list, category):
    # 使用 CSS grid 的概念，這裡用 columns 模擬
    cols = st.columns(5)
    for i, tile in enumerate(tile_list):
        if cols[i % 5].button(tile, key=f"btn_{tile}"):
            add_tile(tile, category)
            st.rerun()

with tabs[0]: create_buttons(TILES["萬"], "萬")
with tabs[1]: create_buttons(TILES["筒"], "筒")
with tabs[2]: create_buttons(TILES["條"], "條")
with tabs[3]: create_buttons(TILES["字"], "字")
with tabs[4]: create_buttons(TILES["花"], "花")

# --- 計算結果 ---
st.markdown("---")
if st.button("🧮 開始計算台數", type="primary", use_container_width=True):
    if len(st.session_state.hand_tiles) != 16 or st.session_state.winning_tile is None:
        st.error("❌ 牌數不足！必須是 16 張手牌 + 1 張胡牌。")
    else:
        score, details = calculate_tai()
        st.balloons()
        st.success(f"### 總台數：{score} 台")
        if details:
            with st.expander("查看詳細台數項目", expanded=True):
                for item in details:
                    st.write(f"- {item}")
        else:
            st.write("無特殊牌型")

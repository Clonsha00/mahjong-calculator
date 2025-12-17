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

# --- 輔助函式：新增牌 ---
def add_tile(tile, category):
    # 處理花牌
    if category == "花":
        if tile not in st.session_state.flower_tiles:
            st.session_state.flower_tiles.append(tile)
        return

    # 處理手牌與胡牌
    current_count = len(st.session_state.hand_tiles)
    has_winning = st.session_state.winning_tile is not None

    # 1. 如果還沒滿16張，加到手牌
    if current_count < 16:
        st.session_state.hand_tiles.append(tile)
    # 2. 如果手牌滿16張，且還沒選胡牌，則設定為胡牌
    elif current_count == 16 and not has_winning:
        st.session_state.winning_tile = tile
    else:
        st.warning("牌數已滿 (16張手牌 + 1張胡牌)！請先刪除部分牌再新增。")

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
    
    # 1. 花牌計台 (簡單示範：有花就加)
    if len(flowers) > 0:
        tai_details.append(f"花牌 x{len(flowers)} ({len(flowers)}台)")
        total_tai += len(flowers)
        
    # 2. 三元牌 (中發白) 刻子
    for dragon in ["中", "發", "白"]:
        if counts[dragon] >= 3:
            tai_details.append(f"{dragon}刻 (1台)")
            total_tai += 1
            
    # 3. 風牌刻子 (這裡假設不是圈風門風，單純有刻子不算台，除非你是設定碰碰胡，這裡僅作示範)
    # 若要精確計算，需要使用者輸入「圈風」與「門風」
    
    # 4. 清一色 / 混一色 判斷邏輯 (示範)
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

    # TODO: 這裡可以加入更複雜的演算法來判斷「碰碰胡」、「平胡」等
    # 這需要將手牌進行拆解 (Backtracking Algorithm)
    
    return total_tai, tai_details

# --- UI 介面 ---
st.title("🀄 台灣麻將台數計算機")

col_display, col_controls = st.columns([2, 1])

with col_controls:
    if st.button("🔄 重置所有牌", type="primary"):
        reset_game()
        st.rerun()

# --- 顯示目前手牌 ---
st.markdown("### 🎴 目前手牌")
hand_container = st.container(border=True)

with hand_container:
    # 顯示手牌 (排序是為了美觀，實際順序不影響計算)
    sorted_hand = sorted(st.session_state.hand_tiles)
    st.write(f"**手牌 ({len(st.session_state.hand_tiles)}/16):**")
    
    # 使用 columns 小技巧來顯示牌，比較好看
    if sorted_hand:
        cols = st.columns(17)
        for idx, tile in enumerate(sorted_hand):
            cols[idx].button(tile, key=f"hand_{idx}", disabled=True) # 僅顯示用
    else:
        st.info("尚未選擇手牌")

    st.write("---")
    
    # 顯示胡牌 (第17張)
    st.write("**🖐️ 胡牌 / 摸牌 (第17張):**")
    if st.session_state.winning_tile:
        st.button(st.session_state.winning_tile, key="win_tile_btn", type="primary")
        if st.button("❌ 移除胡牌"):
            st.session_state.winning_tile = None
            st.rerun()
    else:
        st.caption("請選滿16張後，選取第17張")

    # 顯示花牌
    if st.session_state.flower_tiles:
        st.write("---")
        st.write(f"**🌸 花牌 ({len(st.session_state.flower_tiles)}):** " + " ".join(st.session_state.flower_tiles))

# --- 按鈕輸入區 ---
st.markdown("### ➕ 選擇牌型")
tabs = st.tabs(["萬子", "筒子", "條子", "字牌", "花牌"])

def create_buttons(tile_list, category):
    cols = st.columns(5) # 一行5個按鈕
    for i, tile in enumerate(tile_list):
        if cols[i % 5].button(tile):
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
    # 基本檢查
    if len(st.session_state.hand_tiles) != 16 or st.session_state.winning_tile is None:
        st.error("❌ 手牌必須是 16 張，且必須有一張胡牌才能計算！")
    else:
        score, details = calculate_tai()
        st.success(f"### 總台數：{score} 台")
        if details:
            st.write("詳細項目：")
            for item in details:
                st.write(f"- {item}")
        else:
            st.write("無特殊牌型 (底台請自行約定)")

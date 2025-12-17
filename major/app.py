import streamlit as st
from st_clickable_images import clickable_images
import time

# --- 1. 頁面設定 ---
st.set_page_config(page_title="🀄 台灣麻將台數計算器", layout="wide")

# 自訂 CSS 讓介面更好看
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        font-weight: bold;
    }
    .main-header {
        text-align: center; 
        font-size: 2rem; 
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🀄 台灣麻將台數計算器 (視覺版)</div>', unsafe_allow_html=True)

# --- 2. 狀態初始化 (Session State) ---
if "hand" not in st.session_state:
    st.session_state.hand = [] # 存入手牌代碼
if "msg" not in st.session_state:
    st.session_state.msg = ""  # 系統訊息

# --- 3. 定義麻將資料結構與圖片 ---
def get_tile_image_url(code):
    # 這裡使用 Placeholder 圖片服務生成麻將圖 (正式版請換成您自己的圖片路徑)
    # 根據花色給不同的文字顏色
    color_map = {'m': 'darkred', 'p': 'blue', 's': 'green', 'z': 'black'}
    color = color_map.get(code[-1], 'black')
    return f"https://placehold.co/60x80/EEE/{color}?text={code}&font=roboto"

categories = {
    "萬子 (Man)": [f"{i}m" for i in range(1, 10)],
    "筒子 (Pin)": [f"{i}p" for i in range(1, 10)],
    "索子 (Sou)": [f"{i}s" for i in range(1, 10)],
    "字牌 (Zi)":  ["1z", "2z", "3z", "4z", "5z", "6z", "7z"] # 東南西北中發白
}

# 建立所有可選圖片的清單
all_tiles_list = []
all_images_urls = []

for cat_name, tiles in categories.items():
    for tile in tiles:
        all_tiles_list.append(tile)
        all_images_urls.append(get_tile_image_url(tile))

# --- 4. 側邊欄：環境設定 ---
with st.sidebar:
    st.header("⚙️ 環境設定")
    prevailing_wind = st.selectbox("圈風 (Prevailing Wind)", ["東", "南", "西", "北"])
    seat_wind = st.selectbox("門風 (Seat Wind)", ["東", "南", "西", "北"])
    
    st.markdown("---")
    st.write("### 特殊選項")
    is_self_drawn = st.checkbox("自摸 (Self-drawn)", value=True)
    flower_count = st.number_input("花牌數量", min_value=0, max_value=8, value=0)
    
    st.markdown("---")
    if st.button("🗑️ 重置所有設定"):
        st.session_state.hand = []
        st.session_state.msg = "已重置"
        st.rerun()

# --- 5. 主畫面：選牌區域 ---
st.info("👇 請直接點擊下方麻將牌加入手牌 (最多 17 張)")

# 選牌區塊 (Method 3)
clicked_index = clickable_images(
    paths=all_images_urls,
    titles=[f"加入 {t}" for t in all_tiles_list],
    div_style={
        "display": "flex",
        "justify-content": "center",
        "flex-wrap": "wrap",
        "background-color": "#f8f9fa",
        "padding": "15px",
        "border-radius": "10px",
        "border": "1px solid #ddd"
    },
    img_style={
        "margin": "3px",
        "height": "55px",
        "cursor": "pointer",
        "border-radius": "4px",
        "transition": "transform 0.1s"
    },
    key="selection_grid"
)

# 處理選牌點擊
if clicked_index > -1:
    selected_tile = all_tiles_list[clicked_index]
    if len(st.session_state.hand) < 17:
        st.session_state.hand.append(selected_tile)
    else:
        st.session_state.msg = "⚠️ 手牌已滿 (17張)！請先移除部分牌。"

# --- 6. 顯示目前手牌 (橫向排列版) ---
st.divider()
st.subheader("🤚 目前手牌")

# 顯示系統訊息
if st.session_state.msg:
    st.success(f"💡 {st.session_state.msg}")
    st.session_state.msg = "" 

if st.session_state.hand:
    # 1. 排序手牌
    def sort_key(tile):
        order_map = {'m': 1, 'p': 2, 's': 3, 'z': 4}
        cat_score = order_map.get(tile[-1], 99)
        num_score = int(tile[0])
        return (cat_score, num_score)
    
    sorted_hand = sorted(st.session_state.hand, key=sort_key)
    hand_images_urls = [get_tile_image_url(t) for t in sorted_hand]

    # 2. 顯示橫向手牌
    st.markdown("👇 **點擊手牌可移除該張牌**")
    
    clicked_hand_index = clickable_images(
        paths=hand_images_urls,
        titles=[f"移除 {t}" for t in sorted_hand],
        div_style={
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "flex-wrap": "wrap",
            "background-color": "#e0e5ec",
            "padding": "20px",
            "border-radius": "15px",
            "box-shadow": "inset 2px 2px 5px #b8b9be, inset -3px -3px 7px #fff"
        },
        img_style={
            "margin": "1px",  # 緊湊排列
            "height": "65px", 
            "cursor": "pointer",
            "box-shadow": "2px 2px 5px rgba(0,0,0,0.2)"
        },
        key="hand_display" # 避免 Key 衝突
    )

    # 3. 處理丟牌邏輯
    if clicked_hand_index > -1:
        removed_tile = sorted_hand[clicked_hand_index]
        st.session_state.hand.remove(removed_tile)
        st.session_state.msg = f"已移除一張 {removed_tile}"
        st.rerun()

    if st.button("🧹 清空所有手牌"):
        st.session_state.hand = []
        st.rerun()

else:
    st.info("尚未選擇任何牌...")

# --- 7. 計算邏輯區域 ---
st.divider()
st.subheader("🧮 計算結果")

if st.button("開始計算台數", type="primary"):
    if len(st.session_state.hand) not in [14, 17]:
        st.error(f"牌數錯誤！目前 {len(st.session_state.hand)} 張。一般胡牌應為 17 張。")
    else:
        with st.spinner("正在分析牌型..."):
            time.sleep(0.5)
            # 這裡放入台數計算結果
            st.success("計算完成！(此處需連接 Python 演算法)")

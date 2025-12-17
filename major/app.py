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

# --- 3. 定義麻將資料結構 ---
# 為了演示，我們使用線上 Placeholder 圖片生成服務
# 實際使用時，請將 images_url 改為你本地圖片的 Base64 或是專案內的圖片路徑
def get_tile_image_url(code):
    # 對應真實麻將圖片的代碼轉換 (例如 1m = 一萬)
    color_map = {'m': 'darkred', 'p': 'blue', 's': 'green', 'z': 'black'}
    color = color_map.get(code[-1], 'black')
    return f"https://placehold.co/60x80/EEE/{color}?text={code}&font=roboto"

categories = {
    "萬子 (Man)": [f"{i}m" for i in range(1, 10)],
    "筒子 (Pin)": [f"{i}p" for i in range(1, 10)],
    "索子 (Sou)": [f"{i}s" for i in range(1, 10)],
    "字牌 (Zi)":  ["1z", "2z", "3z", "4z", "5z", "6z", "7z"] # 東南西北中發白
}

# 建立所有圖片的清單與連結
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

# --- 5. 主畫面：選牌區域 (Method 3 核心) ---
st.info("👇 請直接點擊下方麻將牌加入手牌 (最多 17 張)")

# 使用 st_clickable_images 渲染圖片網格
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
    }
)

# 處理點擊邏輯
if clicked_index > -1:
    selected_tile = all_tiles_list[clicked_index]
    if len(st.session_state.hand) < 17:
        st.session_state.hand.append(selected_tile)
        # 這裡不需要 st.rerun()，元件會自動刷新，但若要強制更新 UI 狀態可視情況加
    else:
        st.session_state.msg = "⚠️ 手牌已滿 (17張)！請先移除部分牌。"

# --- 6. 顯示目前手牌 ---
st.divider()
st.subheader("🤚 目前手牌")

# 顯示系統訊息
if st.session_state.msg:
    st.caption(f"💡 {st.session_state.msg}")
    st.session_state.msg = "" # 顯示完清空

if st.session_state.hand:
    # 排序手牌 (簡單排序：萬 -> 筒 -> 索 -> 字)
    # 這裡寫一個簡單的權重排序
    def sort_key(tile):
        order = {'m': 1, 'p': 2, 's': 3, 'z': 4}
        return (order.get(tile[-1]), tile[0])
    
    sorted_hand = sorted(st.session_state.hand, key=sort_key)
    
    # 用 Columns 顯示手牌 (模擬真實排法)
    # 為了讓手牌也可以點擊移除，這裡其實也可以再用一次 clickable_images
    # 但為了簡化，我們先用文字 + 按鈕
    
    cols = st.columns(len(sorted_hand) + 1) # +1 是為了留空
    for i, tile in enumerate(sorted_hand):
        with cols[i]:
            # 顯示小圖
            st.image(get_tile_image_url(tile), width=40)
            # 移除按鈕 (因為太擠，這裡僅示意，實作上建議用索引刪除)
    
    st.text(f"代碼: {' '.join(sorted_hand)}")
    
    col_act1, col_act2 = st.columns([1, 1])
    with col_act1:
        if st.button("⬅️ 移除最後一張"):
            st.session_state.hand.pop()
            st.rerun()
    with col_act2:
        if st.button("🧹 清空手牌"):
            st.session_state.hand = []
            st.rerun()

else:
    st.write("尚未選擇任何牌...")

# --- 7. 計算邏輯區域 ---
st.divider()
st.subheader("🧮 計算結果")

if st.button("開始計算台數", type="primary"):
    if len(st.session_state.hand) not in [14, 17]: # 假設標準胡牌張數檢查
        st.error(f"牌數錯誤！目前 {len(st.session_state.hand)} 張。一般胡牌應為 17 張 (含花/槓另計)。")
    else:
        # === 這裡放入你的 Python 台數計算邏輯 ===
        # 這只是模擬回傳
        with st.spinner("正在分析牌型..."):
            time.sleep(0.5) # 假裝在計算
            
            # 假邏輯範例
            tais = 0
            reasons = []
            
            if is_self_drawn:
                tais += 1
                reasons.append("自摸 (1台)")
            if flower_count > 0:
                tais += flower_count
                reasons.append(f"花牌 x{flower_count} ({flower_count}台)")
            
            # 顯示結果
            st.success(f"總台數：{tais} 台")
            for r in reasons:
                st.write(f"- {r}")
            st.info("完整牌型判斷邏輯需連接後端 Python 演算法 (碰碰胡、清一色等...)")

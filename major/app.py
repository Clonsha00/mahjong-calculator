# --- 6. 顯示目前手牌 (橫向排列版) ---
st.divider()
st.subheader("🤚 目前手牌")

# 顯示系統訊息
if st.session_state.msg:
    st.success(f"💡 {st.session_state.msg}") # 改用 success 比較明顯
    st.session_state.msg = "" 

if st.session_state.hand:
    # 1. 排序手牌 (讓萬筒索字聚在一起，看起來才舒服)
    def sort_key(tile):
        # 定義權重: 萬=1, 筒=2, 索=3, 字=4
        order_map = {'m': 1, 'p': 2, 's': 3, 'z': 4}
        cat_score = order_map.get(tile[-1], 99)
        num_score = int(tile[0])
        return (cat_score, num_score)
    
    # 排序並建立新的圖片清單
    sorted_hand = sorted(st.session_state.hand, key=sort_key)
    hand_images_urls = [get_tile_image_url(t) for t in sorted_hand]

    # 2. 顯示橫向手牌
    st.markdown("👇 **點擊手牌可移除該張牌**")
    
    clicked_hand_index = clickable_images(
        paths=hand_images_urls,
        titles=[f"移除 {t}" for t in sorted_hand],
        div_style={
            "display": "flex",
            "justify-content": "center", # 居中排列
            "align-items": "center",
            "flex-wrap": "wrap",         # 視窗太小時自動換行
            "background-color": "#e0e5ec", # 模擬桌墊顏色
            "padding": "20px",
            "border-radius": "15px",
            "box-shadow": "inset 2px 2px 5px #b8b9be, inset -3px -3px 7px #fff" # 增加立體感
        },
        img_style={
            "margin": "1px",  # 間距設小一點，讓牌靠在一起
            "height": "65px", # 手牌可以稍微大一點
            "cursor": "pointer",
            "box-shadow": "2px 2px 5px rgba(0,0,0,0.2)" # 幫牌加點陰影
        },
        key="hand_display" # 重要！需要設定 key 避免跟上面的選牌衝突
    )

    # 3. 處理「丟牌」邏輯 (點選手牌即刪除)
    if clicked_hand_index > -1:
        removed_tile = sorted_hand[clicked_hand_index]
        
        # 為了正確刪除 (避免刪錯重複的牌)，我們需要找到原始清單中的對應項目
        # 因為 sorted_hand 是排序過的，index 可能跟 session_state.hand 不同步
        # 所以我們直接從 session_state.hand 移除「一張」該花色的牌
        st.session_state.hand.remove(removed_tile)
        st.session_state.msg = f"已移除一張 {removed_tile}"
        st.rerun()

    # 清空按鈕放在下面
    if st.button("🧹 清空所有手牌"):
        st.session_state.hand = []
        st.rerun()

else:
    st.info("尚未選擇任何牌，請從上方點選加入...")

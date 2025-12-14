import streamlit as st

# ==========================================
# 1. 演算法核心 (完全沿用 v19，無變動)
# ==========================================
class MahjongLogic:
    TILES_34 = 34
    
    @staticmethod
    def check_win(hand_counts):
        if MahjongLogic._check_migi_shape(hand_counts): return True
        counts = hand_counts[:]
        for i in range(MahjongLogic.TILES_34):
            if counts[i] >= 2:
                counts[i] -= 2
                if MahjongLogic.check_sets(counts): return True
                counts[i] += 2
        return False

    @staticmethod
    def _check_migi_shape(counts):
        if sum(counts) != 17: return False
        triplets = 0
        for c in counts:
            if c == 1 or c == 5: return False
            if c == 3: triplets += 1
        return triplets == 1

    @staticmethod
    def check_sets(counts):
        i = 0
        while i < MahjongLogic.TILES_34 and counts[i] == 0: i += 1
        if i == MahjongLogic.TILES_34: return True
        if counts[i] >= 3:
            counts[i] -= 3
            if MahjongLogic.check_sets(counts): return True
            counts[i] += 3
        if i < 27 and (i % 9) < 7:
            if counts[i+1] > 0 and counts[i+2] > 0:
                counts[i] -= 1; counts[i+1] -= 1; counts[i+2] -= 1
                if MahjongLogic.check_sets(counts): return True
                counts[i] += 1; counts[i+1] += 1; counts[i+2] += 1
        return False

    @staticmethod
    def get_waiting_tiles(current_tiles):
        counts = [0] * MahjongLogic.TILES_34
        for t in current_tiles: counts[t] += 1 
        waiting_list = []
        for i in range(MahjongLogic.TILES_34):
            if counts[i] < 4:
                counts[i] += 1
                if MahjongLogic.check_win(counts): waiting_list.append(i)
                counts[i] -= 1
        return waiting_list

    @staticmethod
    def analyze_discard_options(hand_tiles):
        options = []
        unique_tiles = sorted(list(set(hand_tiles)))
        hand_counts = [0] * 34
        for t in hand_tiles: hand_counts[t] += 1
        for tile_to_discard in unique_tiles:
            temp_hand = hand_tiles[:]
            temp_hand.remove(tile_to_discard)
            waiting = MahjongLogic.get_waiting_tiles(temp_hand)
            if waiting:
                total_remaining = 0
                temp_counts = [0] * 34
                for t in temp_hand: temp_counts[t] += 1
                for w in waiting:
                    left = 4 - temp_counts[w]
                    if left < 0: left = 0
                    total_remaining += left
                options.append({'discard': tile_to_discard, 'waiting': waiting, 'count': len(waiting), 'remaining': total_remaining})
        options.sort(key=lambda x: (x['remaining'], x['count']), reverse=True)
        return options

    @staticmethod
    def check_strict_pinhu(hand_counts, win_tile, seat_wind, round_wind, has_exposed_triplets):
        if has_exposed_triplets: return False
        for i in range(27, 34):
            if hand_counts[i] >= 3: return False 
        pre_hand_counts = hand_counts[:]
        pre_hand_counts[win_tile] -= 1
        pre_tiles = []
        for t in range(34): pre_tiles.extend([t]*pre_hand_counts[t])
        if len(MahjongLogic.get_waiting_tiles(pre_tiles)) >= 3: return False
        counts = hand_counts[:]
        for p in range(MahjongLogic.TILES_34):
            if counts[p] >= 2:
                if p >= 31: continue 
                if p == 27 + seat_wind: continue
                if p == 27 + round_wind: continue
                if p == win_tile: continue 
                counts[p] -= 2
                if MahjongLogic._decompose_pinhu_strict(counts, win_tile, False): return True
                counts[p] += 2
        return False

    @staticmethod
    def _decompose_pinhu_strict(counts, win_tile, has_valid_wait):
        i = 0
        while i < MahjongLogic.TILES_34 and counts[i] == 0: i += 1
        if i == MahjongLogic.TILES_34: return has_valid_wait
        if i < 27 and (i % 9) < 7:
            if counts[i+1] > 0 and counts[i+2] > 0:
                counts[i] -= 1; counts[i+1] -= 1; counts[i+2] -= 1
                is_valid = False
                if win_tile == i and (i % 9) != 6: is_valid = True
                elif win_tile == i+2 and (i % 9) != 0: is_valid = True
                if MahjongLogic._decompose_pinhu_strict(counts, win_tile, has_valid_wait or is_valid): return True
                counts[i] += 1; counts[i+1] += 1; counts[i+2] += 1
        return False

    @staticmethod
    def is_unique_wait(hand_counts, win_tile):
        counts = hand_counts[:]
        has_valid_bad = False 
        for p in range(MahjongLogic.TILES_34):
            if counts[p] >= 2:
                counts[p] -= 2
                is_single_wait = (p == win_tile)
                valid, has_good = MahjongLogic._analyze_wait_quality(counts, win_tile, False)
                if valid:
                    if has_good and not is_single_wait: return False
                    has_valid_bad = True
                counts[p] += 2
        return has_valid_bad

    @staticmethod
    def _analyze_wait_quality(counts, win_tile, used_in_good_way):
        i = 0
        while i < MahjongLogic.TILES_34 and counts[i] == 0: i += 1
        if i == MahjongLogic.TILES_34: return True, used_in_good_way
        has_valid = False
        if counts[i] >= 3:
            counts[i] -= 3
            is_good = used_in_good_way or (i == win_tile)
            v, g = MahjongLogic._analyze_wait_quality(counts, win_tile, is_good)
            if v:
                if g: return True, True
                has_valid = True
            counts[i] += 3
        if i < 27 and (i % 9) < 7:
            if counts[i+1] > 0 and counts[i+2] > 0:
                counts[i] -= 1; counts[i+1] -= 1; counts[i+2] -= 1
                current_is_good = False
                if win_tile == i and (i % 9) != 6: current_is_good = True
                elif win_tile == i+2 and (i % 9) != 0: current_is_good = True
                set_has_tile = (win_tile == i or win_tile == i+1 or win_tile == i+2)
                new_status = used_in_good_way
                if set_has_tile: new_status = used_in_good_way or current_is_good
                v, g = MahjongLogic._analyze_wait_quality(counts, win_tile, new_status)
                if v:
                    if g: return True, True
                    has_valid = True
                counts[i] += 1; counts[i+1] += 1; counts[i+2] += 1
        return has_valid, False

# ==========================================
# 2. 台數計算 (TaiCalculator)
# ==========================================
class TaiCalculator:
    @staticmethod
    def calculate(hand_tiles, open_sets, winning_tile, env, rule):
        full_hand = hand_tiles + [winning_tile]
        for s in open_sets: full_hand.extend(s['tiles'])
        full_hand.sort()
        counts = [0] * 34
        for t in full_hand: counts[t] += 1

        total_tai = 0; logs = []
        mode = rule['mode']; seat_wind = env['seat_wind']; round_wind = env['round_wind']
        
        is_menqing = (len(open_sets) == 0)
        has_exposed_triplets = any(s['type'] in ['pong', 'kang'] for s in open_sets)
        is_self_draw = env['is_self_draw']
        
        is_kong_bloom = env['is_kong_bloom']
        is_last_tile = env['is_last_tile']
        is_robbing_kong = env['is_robbing_kong']
        is_seven_snatch = env['is_seven_snatch']

        flowers = env['flowers']
        flower_count = sum(flowers)
        is_eight_immortals = (flower_count == 8)

        if is_eight_immortals:
            total_tai += 8; logs.append("八仙過海 (8台)")
        elif flower_count == 7 and is_seven_snatch:
            total_tai += 8; logs.append("七搶一 (8台)")
        else:
            if is_menqing and MahjongLogic._check_migi_shape(counts):
                total_tai += 8; logs.append("嚦咕嚦咕 (8台)")
            else:
                hand_counts_only = [0]*34
                for t in (hand_tiles + [winning_tile]): hand_counts_only[t] += 1
                is_no_flower = (sum(env['flowers']) == 0)

                is_pinhu = False
                if mode == 'strict_flower':
                    if not is_no_flower: pass
                    elif not is_kong_bloom and MahjongLogic.check_strict_pinhu(hand_counts_only, winning_tile, seat_wind, round_wind, has_exposed_triplets):
                        total_tai += 2; logs.append("平胡 (2台)")
                        is_pinhu = True

                if not is_pinhu and MahjongLogic.is_unique_wait(hand_counts_only, winning_tile):
                    total_tai += 1; logs.append("獨聽 (1台)")

                if not all(t >= 27 for t in full_hand):
                     if TaiCalculator._is_pong_pong_hu_strict(counts, open_sets): 
                         total_tai += 4; logs.append("碰碰胡 (4台)")
                
                if is_menqing and is_self_draw:
                    total_tai += 3; logs.append("門清一摸三 (3台)")
                elif len(open_sets) == 5 and not is_self_draw:
                    total_tai += 1; logs.append("全求人 (1台)")
                else:
                    if is_menqing: total_tai += 1; logs.append("門清 (1台)")
                    if is_self_draw: total_tai += 1; logs.append("自摸 (1台)")

            if is_kong_bloom: total_tai += 1; logs.append("槓上開花 (1台)")
            if is_last_tile: total_tai += 1; logs.append("海底撈月 (1台)")
            if is_robbing_kong: total_tai += 1; logs.append("搶槓 (1台)")

            if mode == 'strict_flower':
                if flowers[seat_wind]: total_tai += 1; logs.append("正花-季節 (1台)")
                if flowers[seat_wind+4]: total_tai += 1; logs.append("正花-植物 (1台)")
                if all(flowers[0:4]): b=rule.get('flower_kang_tai',2); total_tai+=b; logs.append(f"花槓-四季 ({b}台)")
                if all(flowers[4:8]): b=rule.get('flower_kang_tai',2); total_tai+=b; logs.append(f"花槓-四君子 ({b}台)")

        wind_triplets = [i for i in range(27, 31) if counts[i] >= 3]
        dragon_triplets = [i for i in range(31, 34) if counts[i] >= 3]
        for t in dragon_triplets: total_tai += 1; logs.append(f"{['紅中','發財','白板'][t-31]} (1台)")

        if mode == 'no_flower_loose_word':
            for t in wind_triplets: total_tai += 1; logs.append(f"見字有台-{['東','南','西','北'][t-27]} (1台)")
        else:
            wind_pairs = [i for i in range(27, 31) if counts[i] == 2]
            if len(wind_triplets) == 4: total_tai += 16; logs.append("大四喜 (16台)")
            elif len(wind_triplets) == 3 and len(wind_pairs) == 1: total_tai += 8; logs.append("小四喜 (8台)")
            else:
                if (27+round_wind) in wind_triplets: total_tai += 1; logs.append("圈風 (1台)")
                if (27+seat_wind) in wind_triplets: total_tai += 1; logs.append("門風 (1台)")

        is_all_honors = all(t >= 27 for t in full_hand)
        suits = set(); has_honor = False
        for t in full_hand:
            if t >= 27: has_honor = True
            elif t < 9: suits.add(0)
            elif t < 18: suits.add(1)
            else: suits.add(2)
        if len(suits) == 0 and has_honor: total_tai += 8; logs.append("字一色 (8台)")
        elif len(suits) == 1:
            if not has_honor: total_tai += 8; logs.append("清一色 (8台)")
            elif not is_all_honors: total_tai += 4; logs.append("混一色 (4台)")

        return total_tai, logs, is_eight_immortals

    @staticmethod
    def _is_pong_pong_hu_strict(counts, open_sets):
        for s in open_sets:
            if s['type'] == 'chow': return False
        invalid_for_set = [1, 2, 5] 
        c_copy = counts[:]
        for p in range(34):
            if c_copy[p] >= 2:
                c_copy[p] -= 2
                is_valid = True
                for i in range(34):
                    if c_copy[i] in invalid_for_set:
                        is_valid = False; break
                c_copy[p] += 2
                if is_valid: return True
        return False

# ==========================================
# 3. Streamlit 介面 (Mobile Friendly)
# ==========================================
def get_tile_name(tid):
    if tid < 9: return f"{tid+1}萬"
    elif tid < 18: return f"{tid-8}筒"
    elif tid < 27: return f"{tid-17}索"
    else: return ["東", "南", "西", "北", "中", "發", "白"][tid-27]

def main():
    st.set_page_config(page_title="麻將軍師 (Mobile)", layout="centered")
    
    # Init Session State
    if 'hand_tiles' not in st.session_state: st.session_state.hand_tiles = []
    if 'open_sets' not in st.session_state: st.session_state.open_sets = []
    if 'drawn_tile' not in st.session_state: st.session_state.drawn_tile = None
    if 'input_mode' not in st.session_state: st.session_state.input_mode = "normal"
    if 'multiplier' not in st.session_state: st.session_state.multiplier = 1
    
    # CSS 優化 (加大按鈕，適合手機)
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 3em;
        width: 100%;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🀄 台灣麻將計算機")

    # --- 1. 設定與狀態 ---
    with st.expander("⚙️ 設定 (風圈、金額、規則)", expanded=False):
        c1, c2 = st.columns(2)
        round_wind = c1.selectbox("圈風", [0,1,2,3], format_func=lambda x: ["東","南","西","北"][x])
        seat_wind = c2.selectbox("門風", [0,1,2,3], index=1, format_func=lambda x: ["東","南","西","北"][x])
        
        c3, c4 = st.columns(2)
        base_money = c3.number_input("底", value=30, step=10)
        tai_money = c4.number_input("台", value=10, step=5)
        
        rule_mode = st.radio("計分模式", ["strict_flower", "no_flower_loose_word"], 
                             format_func=lambda x: "正花正字 (嚴謹)" if x=="strict_flower" else "無花見字 (寬鬆)")
        
        st.markdown("---")
        st.write("🌺 **花牌持有狀況**")
        cols = st.columns(4)
        flowers = [False]*8
        f_labels = ["春", "夏", "秋", "冬", "梅", "蘭", "竹", "菊"]
        for i, label in enumerate(f_labels):
            flowers[i] = cols[i%4].checkbox(label, value=False)
            
        st.markdown("---")
        st.write("🔥 **胡牌情境**")
        col_s1, col_s2 = st.columns(2)
        is_self_draw = col_s1.checkbox("自摸")
        is_kong_bloom = col_s2.checkbox("槓上開花")
        is_last_tile = col_s1.checkbox("海底撈月")
        is_robbing_kong = col_s2.checkbox("搶槓")
        is_seven_snatch = col_s1.checkbox("七搶一")

        if st.button("下一局 (換莊/清空)"):
            st.session_state.hand_tiles = []
            st.session_state.open_sets = []
            st.session_state.drawn_tile = None
            st.rerun()

    # --- 2. 顯示區 ---
    # 計算總張數
    total_units = len(st.session_state.hand_tiles) + len(st.session_state.open_sets) * 3
    if st.session_state.drawn_tile is not None: total_units += 1
    
    st.info(f"🀄 目前：{total_units} 張 (手牌 {len(st.session_state.hand_tiles)} + 明牌 {len(st.session_state.open_sets)} 組)")

    # 顯示明牌
    open_str = ""
    for s in st.session_state.open_sets:
        n = get_tile_name(s['tiles'][0])
        type_map = {'pong':'刻', 'kang':'槓', 'chow':'吃'}
        if s['type'] == 'chow':
             n1 = get_tile_name(s['tiles'][0])[0]
             n2 = get_tile_name(s['tiles'][1])[0]
             n3 = get_tile_name(s['tiles'][2])
             open_str += f"[{n1}{n2}{n3}吃] "
        else:
             open_str += f"[{n}{type_map[s['type']]}] "
    
    if open_str: st.caption(f"明牌：{open_str}")

    # 顯示手牌 (排序)
    display_hand = sorted(st.session_state.hand_tiles)
    hand_str = " ".join([f"[{get_tile_name(t)}]" for t in display_hand])
    
    # 顯示摸牌
    draw_str = ""
    if st.session_state.drawn_tile is not None:
        draw_str = f" + 🔴 [{get_tile_name(st.session_state.drawn_tile)}]"
    
    st.markdown(f"### 🖐 {hand_str}{draw_str}")

    # --- 3. 操作控制區 ---
    st.markdown("---")
    
    # 模式選擇
    mode = st.radio("操作模式", ["normal", "pong", "kang", "chow"], horizontal=True, 
                    format_func=lambda x: {"normal":"手牌", "pong":"碰", "kang":"槓", "chow":"吃"}[x])
    
    # 張數倍率 (僅normal有效)
    multiplier = 1
    if mode == "normal":
        multiplier = st.slider("加入張數", 1, 4, 1)

    # 功能鍵
    c_del, c_clr = st.columns(2)
    if c_del.button("⌫ 刪除一張"):
        if st.session_state.drawn_tile is not None:
            st.session_state.drawn_tile = None
        elif st.session_state.hand_tiles:
            st.session_state.hand_tiles.pop()
        elif st.session_state.open_sets:
            st.session_state.open_sets.pop()
        st.rerun()
        
    if c_clr.button("🗑️ 清空重來"):
        st.session_state.hand_tiles = []
        st.session_state.open_sets = []
        st.session_state.drawn_tile = None
        st.rerun()

    # --- 4. 鍵盤區 ---
    tabs = st.tabs(["萬子", "筒子", "索子", "字牌"])
    
    def add_tile(tid):
        # 邏輯處理 (同 v19)
        current_u = len(st.session_state.hand_tiles) + len(st.session_state.open_sets) * 3
        if st.session_state.drawn_tile is not None: current_u += 1
        
        # 檢查該牌總數
        total_card = st.session_state.hand_tiles.count(tid)
        if st.session_state.drawn_tile == tid: total_card += 1
        for s in st.session_state.open_sets: total_card += s['tiles'].count(tid)

        if mode == "normal":
            if current_u + multiplier > 17: st.toast("牌數過多！"); return
            if total_card + multiplier > 4: st.toast("牌數超過4張！"); return
            
            for _ in range(multiplier):
                max_hand = 16 - (len(st.session_state.open_sets)*3)
                if len(st.session_state.hand_tiles) < max_hand:
                    st.session_state.hand_tiles.append(tid)
                else:
                    st.session_state.drawn_tile = tid
                    break # 摸牌只能一張
                    
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

    # 繪製鍵盤
    suits = [range(0,9), range(9,18), range(18,27), range(27,34)]
    for idx, suit_range in enumerate(suits):
        with tabs[idx]:
            cols = st.columns(3) # 3列排列
            for i, tid in enumerate(suit_range):
                if cols[i%3].button(get_tile_name(tid), key=f"btn_{tid}"):
                    add_tile(tid)
                    st.rerun()

    # --- 5. 計算結果區 ---
    st.markdown("---")
    st.subheader("📊 分析結果")

    # 情境 A: 16張 (聽牌檢查)
    if total_units == 16 and st.session_state.drawn_tile is None:
        waiting = MahjongLogic.get_waiting_tiles(st.session_state.hand_tiles)
        if not waiting:
            st.warning("尚未聽牌")
        else:
            st.success("🔥 聽牌中！")
            cols = st.columns(4)
            for i, w in enumerate(waiting):
                if cols[i%4].button(f"胡 {get_tile_name(w)}", type="primary"):
                    show_result(w, round_wind, seat_wind, is_self_draw, flowers, 
                                is_kong_bloom, is_last_tile, is_robbing_kong, is_seven_snatch,
                                rule_mode, base_money, tai_money)

    # 情境 B: 17張 (自摸/捨牌)
    elif total_units == 17 and st.session_state.drawn_tile is not None:
        full_hand = st.session_state.hand_tiles + [st.session_state.drawn_tile]
        full_hand.sort()
        
        # 檢查自摸
        c_counts = [0]*34
        for t in full_hand: c_counts[t] += 1
        if MahjongLogic.check_win(c_counts):
            if st.button(f"🔥 自摸 {get_tile_name(st.session_state.drawn_tile)} (點擊算台)", type="primary"):
                show_result(st.session_state.drawn_tile, round_wind, seat_wind, True, flowers,
                            is_kong_bloom, is_last_tile, is_robbing_kong, is_seven_snatch,
                            rule_mode, base_money, tai_money)
        
        # 捨牌建議
        st.write("💡 **捨牌建議**")
        sug = MahjongLogic.analyze_discard_options(full_hand)
        if not sug:
            st.write("無建議 (死牌)")
        else:
            for opt in sug:
                d_name = get_tile_name(opt['discard'])
                w_str = " ".join([get_tile_name(w) for w in opt['waiting']])
                rem = opt['remaining']
                
                col1, col2 = st.columns([1, 3])
                if col1.button(f"打 {d_name}", key=f"dis_{opt['discard']}"):
                    # 模擬打牌
                    if st.session_state.drawn_tile == opt['discard']:
                        st.session_state.drawn_tile = None
                    elif opt['discard'] in st.session_state.hand_tiles:
                        st.session_state.hand_tiles.remove(opt['discard'])
                        if st.session_state.drawn_tile is not None:
                            st.session_state.hand_tiles.append(st.session_state.drawn_tile)
                            st.session_state.drawn_tile = None
                        st.session_state.hand_tiles.sort()
                    st.rerun()
                
                col2.write(f"聽 {len(opt['waiting'])} 洞 (剩 {rem} 張)：{w_str}")

    else:
        st.caption("尚未滿張 (相公)")

def show_result(win_tile, rw, sw, self_draw, fl, kb, lt, rk, ss, mode, base, per_tai):
    env = {
        'round_wind': rw, 'seat_wind': sw, 'is_self_draw': self_draw,
        'flowers': fl, 'is_kong_bloom': kb, 'is_last_tile': lt,
        'is_robbing_kong': rk, 'is_seven_snatch': ss
    }
    rule = {'mode': mode, 'flower_kang_tai': 2} # 預設花槓2台
    
    tai, logs, is_8 = TaiCalculator.calculate(st.session_state.hand_tiles, st.session_state.open_sets, win_tile, env, rule)
    
    # 算錢
    unit = base + (tai * per_tai)
    final_self_draw = self_draw or is_8 # 八仙視為自摸
    
    txt = f"### 胡：{get_tile_name(win_tile)}\n"
    txt += f"**總台數：{tai} 台**\n\n"
    for l in logs: txt += f"- {l}\n"
    txt += "\n---\n"
    
    if final_self_draw:
        txt += f"💰 **自摸結算 (收三家)**\n"
        txt += f"一家收：{unit} 元\n"
        txt += f"總共贏：{unit * 3} 元"
    else:
        txt += f"💰 **放槍結算**\n"
        txt += f"胡牌贏：{unit} 元\n"
        txt += f"放槍付：-{unit} 元"
        
    st.balloons()
    st.success(txt)

if __name__ == "__main__":
    main()
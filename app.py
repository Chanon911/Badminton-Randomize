import streamlit as st
import random
import re
import time

# --- ตั้งค่าหน้าเว็บ (Hiso Random) ---
st.set_page_config(page_title="Hiso Random", page_icon="🎲", layout="centered")

# --- โหลดฟอนต์ Kanit และปรับแต่ง UI ให้มินิมอล ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
        
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select, li, a, div.stMetric {
            font-family: 'Kanit', sans-serif !important;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
        }
        
        .vs-text {
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
            margin-top: 15px;
            color: #555;
        }
        
        div[data-testid="metric-container"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# --- จัดการระบบความจำของเว็บ (Session State) ---
if 'player_stats' not in st.session_state: st.session_state.player_stats = {}
if 'pair_hist' not in st.session_state: st.session_state.pair_hist = {}
if 'priority_players' not in st.session_state: st.session_state.priority_players = []
if 'round_num' not in st.session_state: st.session_state.round_num = 1
if 'current_matches' not in st.session_state: st.session_state.current_matches = []
if 'waiting_data' not in st.session_state: st.session_state.waiting_data = ({}, [])

st.title("🎲 Hiso Random")

# --- กล่องใส่รายชื่อ ---
st.subheader("👥 รายชื่อผู้เล่นทั้งหมด")
raw_players = st.text_area("พิมพ์รายชื่อเว้นวรรค (ข้อมูลนี้ใช้ร่วมกันทุกระบบด้านล่าง)", "1 2 3 4 5 6 7 8 9 10")
player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]

for p in player_list:
    if p not in st.session_state.player_stats:
        st.session_state.player_stats[p] = {'played': 0, 'wins': 0}
    if p not in st.session_state.pair_hist:
        st.session_state.pair_hist[p] = {}

# --- 📊 Dashboard Metrics ---
wins = [s['wins'] for s in st.session_state.player_stats.values()] if st.session_state.player_stats else [0]
max_wins = max(wins) if wins else 0
mvps = [p for p, s in st.session_state.player_stats.items() if s['wins'] == max_wins and max_wins > 0]
mvp_text = ", ".join(mvps) if mvps else "-"
waiting_count = len(st.session_state.waiting_data[1]) if len(st.session_state.waiting_data) > 1 else 0

m1, m2, m3 = st.columns(3)
m1.metric("👥 สมาชิกทั้งหมด", f"{len(player_list)} คน")
m2.metric("🏆 ผู้นำ MVP ตอนนี้", mvp_text)
m3.metric("🪑 รอคิวตีแบด (คนเศษ)", f"{waiting_count} คน")

st.markdown("---")

# --- สร้าง Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["🏸 แบดมินตัน", "🚗 สุ่มขึ้นรถ", "⚽ ฟุตบอล", "📚 ทำงานกลุ่ม"])

# ==========================================
# TAB 1: ระบบจัดทีมแบดมินตัน
# ==========================================
with tab1:
    st.subheader("🏸 สุ่มทีมแบดมินตัน")
    
    col1, col2 = st.columns(2)
    with col1:
        num_courts = st.number_input("จำนวนคอร์ด", min_value=1, max_value=10, value=2)
    with col2:
        play_type = st.radio("ประเภทการเล่น", ["ตีคู่ (ทีมละ 2 คน)", "ตีเดี่ยว (ทีมละ 1 คน)"])
        
    if st.button("🔄 ล้างสถิติและประวัติการจับคู่", key="reset_badminton"):
        st.session_state.player_stats = {}
        st.session_state.pair_hist = {}
        st.session_state.priority_players = []
        st.session_state.round_num = 1
        st.session_state.current_matches = []
        st.session_state.waiting_data = ({}, [])
        for p in player_list:
            st.session_state.player_stats[p] = {'played': 0, 'wins': 0}
            st.session_state.pair_hist[p] = {}
        st.success("รีเซ็ตสถิติทั้งหมดเรียบร้อย!")
        time.sleep(1)
        st.rerun()

    players_per_team = 2 if "ตีคู่" in play_type else 1

    if st.button(f"🎲 สุ่มจัดทีมรอบที่ {st.session_state.round_num}", type="primary", use_container_width=True):
        with st.spinner('กำลังสับไพ่รายชื่อ และสุ่มจับคู่... 🎲'):
            time.sleep(1)
            slots_needed = int(num_courts) * players_per_team * 2
            priority_players = [p for p in st.session_state.priority_players if p in player_list]
            regular_players = [p for p in player_list if p not in priority_players]
            
            random.shuffle(regular_players)
            
            if len(priority_players) >= slots_needed:
                main_match_players = priority_players[:slots_needed]
                new_priority = priority_players[slots_needed:] + regular_players
            else:
                main_match_players = priority_players.copy()
                needed = slots_needed - len(main_match_players)
                needed = min(needed, len(regular_players))
                main_match_players.extend(regular_players[:needed])
                new_priority = regular_players[needed:]

            best_permutation = main_match_players
            best_penalty = float('inf')
            
            for _ in range(30):
                temp_players = main_match_players.copy()
                random.shuffle(temp_players)
                penalty = 0
                for c in range(int(num_courts)):
                    idx = c * players_per_team * 2
                    if idx + players_per_team * 2 <= len(temp_players):
                        t1 = temp_players[idx:idx+players_per_team]
                        t2 = temp_players[idx+players_per_team:idx+players_per_team*2]
                        for i in range(len(t1)):
                            for j in range(i+1, len(t1)):
                                penalty += st.session_state.pair_hist.get(t1[i], {}).get(t1[j], 0)
                        for i in range(len(t2)):
                            for j in range(i+1, len(t2)):
                                penalty += st.session_state.pair_hist.get(t2[i], {}).get(t2[j], 0)
                if penalty < best_penalty:
                    best_penalty = penalty
                    best_permutation = temp_players
                    if penalty == 0: break
            
            matches = []
            temp_main = best_permutation.copy()
            for c in range(int(num_courts)):
                if len(temp_main) >= players_per_team * 2:
                    team1 = [temp_main.pop(0) for _ in range(players_per_team)]
                    team2 = [temp_main.pop(0) for _ in range(players_per_team)]
                    matches.append({"court": c + 1, "team1": team1, "team2": team2})
            
            waiting_teams = []
            temp_wait = new_priority.copy()
            while len(temp_wait) >= players_per_team:
                waiting_teams.append([temp_wait.pop(0) for _ in range(players_per_team)])
                
            st.session_state.current_matches = matches
            st.session_state.waiting_data = (waiting_teams, temp_wait)
            st.session_state.priority_players = new_priority.copy()
        
        st.balloons()

    if st.session_state.current_matches:
        st.markdown("---")
        st.subheader(f"🔥 ผลการจัดทีมรอบที่ {st.session_state.round_num}")
        
        with st.form("score_form"):
            results = {}
            # 1. แสดงผลกล่องทีมหลัก
            for match in st.session_state.current_matches:
                t1 = " & ".join(match["team1"])
                t2 = " & ".join(match["team2"])
                
                c1, c2, c3 = st.columns([4, 1, 4])
                with c1: st.info(f"🔵 **คอร์ด {match['court']} | ทีม 1:**\n\n{t1}")
                with c2: st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)
                with c3: st.error(f"🔴 **คอร์ด {match['court']} | ทีม 2:**\n\n{t2}")
                
                results[match['court']] = st.radio(
                    f"บันทึกผล คอร์ด {match['court']}", 
                    ["ไม่คิดคะแนน / เสมอ", f"ทีม 1 ชนะ", f"ทีม 2 ชนะ"], 
                    horizontal=True, key=f"court_{match['court']}"
                )
                st.markdown("---")
            
            # 2. แสดงผลกล่องทีมรอและคนเศษให้ชัดเจน
            waiting_teams, leftover = st.session_state.waiting_data
            if waiting_teams or leftover:
                st.markdown("#### 🌟 ทีมรอรอบถัดไป (VIP การันตีลงสนาม)")
                w_cols = st.columns(2)
                for i, t in enumerate(waiting_teams):
                    with w_cols[i % 2]:
                        st.warning(f"⏳ **ทีมรอที่ {i+1}:**\n\n{' & '.join(t)}")
                if leftover:
                    st.error(f"👤 **เศษคนรอจับคู่:**\n\n{', '.join(leftover)}")
                st.markdown("---")
            
            # 3. กล่องก๊อปปี้ข้อความ ย้ายมาไว้ด้านล่างสุดของผลลัพธ์
            summary_lines = [f"🏸 จัดทีมแบดมินตัน รอบที่ {st.session_state.round_num}"]
            for m in st.session_state.current_matches:
                summary_lines.append(f"📍 คอร์ด {m['court']}: [{' & '.join(m['team1'])}] VS [{' & '.join(m['team2'])}]")
            if waiting_teams or leftover:
                summary_lines.append("🌟 ทีมรอรอบถัดไป:")
                for i, t in enumerate(waiting_teams): summary_lines.append(f"- รอที่ {i+1}: {' & '.join(t)}")
                if leftover: summary_lines.append(f"- เศษคนรอ: {', '.join(leftover)}")
                
            st.caption("👇 คัดลอกข้อความสรุปผลเพื่อส่ง LINE")
            st.code("\n".join(summary_lines), language="text")
            
            # 4. ปุ่มกดยืนยันคะแนน
            if st.form_submit_button("บันทึกคะแนนและไปรอบต่อไป ✅", use_container_width=True):
                for match in st.session_state.current_matches:
                    res = results[match['court']]
                    for i in range(len(match["team1"])):
                        for j in range(i+1, len(match["team1"])):
                            p1, p2 = match["team1"][i], match["team1"][j]
                            st.session_state.pair_hist[p1][p2] = st.session_state.pair_hist.get(p1, {}).get(p2, 0) + 1
                            st.session_state.pair_hist[p2][p1] = st.session_state.pair_hist.get(p2, {}).get(p1, 0) + 1
                    for i in range(len(match["team2"])):
                        for j in range(i+1, len(match["team2"])):
                            p1, p2 = match["team2"][i], match["team2"][j]
                            st.session_state.pair_hist[p1][p2] = st.session_state.pair_hist.get(p1, {}).get(p2, 0) + 1
                            st.session_state.pair_hist[p2][p1] = st.session_state.pair_hist.get(p2, {}).get(p1, 0) + 1
                    
                    if "ทีม 1" in res:
                        for p in match["team1"] + match["team2"]: st.session_state.player_stats[p]['played'] += 1
                        for p in match["team1"]: st.session_state.player_stats[p]['wins'] += 1
                    elif "ทีม 2" in res:
                        for p in match["team1"] + match["team2"]: st.session_state.player_stats[p]['played'] += 1
                        for p in match["team2"]: st.session_state.player_stats[p]['wins'] += 1
                        
                st.session_state.round_num += 1
                st.session_state.current_matches = [] 
                st.rerun()

    st.markdown("---")
    st.subheader("🏆 MVP ประจำวัน")
    sorted_stats = sorted(st.session_state.player_stats.items(), key=lambda x: (x[1]['wins'], -x[1]['played']), reverse=True)
    table_data = [{"อันดับ": f"{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else ''} {i+1}", "ชื่อ": p, "ชนะ": s['wins'], "เล่น": s['played'], "Win Rate": f"{(s['wins']/s['played']*100) if s['played']>0 else 0:.0f}%"} for i, (p, s) in enumerate(sorted_stats)]
    st.dataframe(table_data, use_container_width=True)

# ==========================================
# TAB 2: ระบบสุ่มคนขึ้นรถ
# ==========================================
with tab2:
    st.subheader("🚗 สุ่มคนขึ้นรถ")
    num_cars = st.number_input("จำนวนรถทั้งหมด (คัน)", min_value=1, max_value=10, value=2, key="num_cars")
    cars_info = []
    
    for i in range(int(num_cars)):
        with st.expander(f"🚙 ตั้งค่ารถคันที่ {i+1}"):
            col1, col2 = st.columns(2)
            with col1: driver = st.selectbox(f"คนขับรถ", ["- ยังไม่ระบุ -"] + player_list, key=f"driver_{i}")
            with col2: capacity = st.number_input(f"ที่นั่ง (ไม่รวมคนขับ)", min_value=1, max_value=10, value=4, key=f"cap_{i}")
            cars_info.append({"car_num": i+1, "driver": driver, "capacity": capacity})
            
    if st.button("🎲 จัดคนขึ้นรถ", type="primary", use_container_width=True):
        with st.spinner('กำลังคำนวณที่นั่ง... 🚙'):
            time.sleep(0.8)
            drivers_list = [c["driver"] for c in cars_info if c["driver"] != "- ยังไม่ระบุ -"]
            passengers_list = [p for p in player_list if p not in drivers_list]
            random.shuffle(passengers_list)
            
            results = []
            for car in cars_info:
                car_passengers = [passengers_list.pop(0) for _ in range(int(car["capacity"])) if passengers_list]
                results.append({"car_num": car["car_num"], "driver": car["driver"], "passengers": car_passengers})
                
        st.snow()
        st.markdown("---")
        st.subheader("🏁 ผลการจัดคนขึ้นรถ")
        
        # แสดงผลกล่องสี
        cols = st.columns(2)
        colors = [st.info, st.success, st.warning, st.error]
        for i, res in enumerate(results):
            with cols[i % 2]:
                driver_name = res['driver'] if res['driver'] != "- ยังไม่ระบุ -" else "❓ ไม่มี"
                pass_names = ', '.join(res['passengers']) if res['passengers'] else '*(ไม่มี)*'
                colors[i % 4](f"**🚙 รถคันที่ {res['car_num']}**\n\n**🧑‍✈️ คนขับ:** {driver_name}\n\n**👥 ผดส:** {pass_names}")
            
        if passengers_list:
            st.error(f"⚠️ **ตกหล่น {len(passengers_list)} คน:** {', '.join(passengers_list)}")
            
        # ก๊อปปี้ข้อความย้ายมาด้านล่าง
        st.markdown("---")
        car_lines = ["🚗 สรุปการจัดคนขึ้นรถ"]
        for res in results:
            d_name = res['driver'] if res['driver'] != "- ยังไม่ระบุ -" else "ไม่มี"
            p_names = ', '.join(res['passengers']) if res['passengers'] else '(ไม่มี)'
            car_lines.append(f"🚙 รถคันที่ {res['car_num']} | คนขับ: {d_name} | ผดส: {p_names}")
        st.caption("👇 คัดลอกข้อความส่ง LINE")
        st.code("\n".join(car_lines), language="text")

# ==========================================
# TAB 3: ระบบจัดทีมฟุตบอล
# ==========================================
with tab3:
    st.subheader("⚽ สุ่มทีมฟุตบอล")
    col1, col2 = st.columns(2)
    with col1: num_fb_teams = st.number_input("จำนวนทีมฟุตบอล", min_value=2, max_value=10, value=2)
    with col2: players_per_fb = st.number_input("ผู้เล่นต่อทีม", min_value=1, max_value=11, value=5)
        
    if st.button("🎲 สุ่มทีมฟุตบอล", type="primary", use_container_width=True):
        with st.spinner('กำลังจับฉลากเลือกทีม และสุ่มเสื้อกั๊ก... ⚽'):
            time.sleep(1)
            fb_players = player_list.copy()
            random.shuffle(fb_players)
            
            fb_teams = []
            for _ in range(int(num_fb_teams)):
                team = [fb_players.pop(0) for _ in range(int(players_per_fb)) if fb_players]
                fb_teams.append(team)
                
            team_indices = list(range(len(fb_teams)))
            num_bibs = max(1, len(fb_teams) // 2)
            teams_with_bibs = random.sample(team_indices, k=num_bibs)
            team_kickoff = random.choice(team_indices)
            
        st.balloons()
        st.markdown("---")
        st.subheader("🏁 ผลการจัดทีมฟุตบอล")
        
        # แสดงผลกล่องสี
        cols = st.columns(2)
        colors = [st.info, st.error, st.success, st.warning]
        for i, team in enumerate(fb_teams):
            with cols[i % 2]:
                bib_status = "🎽 **ใส่เสื้อกั๊ก**" if i in teams_with_bibs else "👕 **เสื้อสีปกติ**"
                kickoff_status = "👟 **ได้เขี่ยลูกก่อน!**" if i == team_kickoff else "🛡️ **รอรับบอล**"
                team_names = ", ".join(team) if team else "*(ไม่มีผู้เล่น)*"
                colors[i % 4](f"#### ⚽ ทีมที่ {i+1}\n\n{bib_status} | {kickoff_status}\n\n🏃‍♂️ **รายชื่อ:** {team_names}")
                
        if fb_players: st.warning(f"🏃 **ตัวสำรอง / รอลงสนาม:** {', '.join(fb_players)}")
        
        # ก๊อปปี้ข้อความย้ายมาด้านล่าง
        st.markdown("---")
        fb_lines = ["⚽ สรุปทีมฟุตบอล"]
        for i, team in enumerate(fb_teams):
            b_stat = "🎽 (เสื้อกั๊ก)" if i in teams_with_bibs else "👕 (สีปกติ)"
            k_stat = "👟 เขี่ยก่อน" if i == team_kickoff else ""
            t_names = ", ".join(team) if team else "(ไม่มีผู้เล่น)"
            fb_lines.append(f"ทีมที่ {i+1} {b_stat} {k_stat}\nรายชื่อ: {t_names}")
        st.caption("👇 คัดลอกข้อความส่ง LINE")
        st.code("\n\n".join(fb_lines), language="text")

# ==========================================
# TAB 4: ระบบสุ่มทำงานกลุ่ม
# ==========================================
with tab4:
    st.subheader("📚 แบ่งกลุ่มทำงาน")
    num_groups = st.number_input("จำนวนกลุ่มที่ต้องการทั้งหมด", min_value=1, max_value=20, value=3, key="num_groups")
    
    st.write("ระบุจำนวนสมาชิกที่ต้องการในแต่ละกลุ่ม:")
    group_sizes = []
    
    cols = st.columns(3)
    for i in range(int(num_groups)):
        with cols[i % 3]:
            size = st.number_input(f"กลุ่มที่ {i+1} (คน)", min_value=1, max_value=20, value=3, key=f"grp_size_{i}")
            group_sizes.append(int(size))
            
    if st.button("🎲 สุ่มกลุ่มทำงาน", type="primary", use_container_width=True):
        with st.spinner('กำลังสุ่มสมาชิกเข้ากลุ่ม... 📚'):
            time.sleep(0.8)
            grp_players = player_list.copy()
            random.shuffle(grp_players)
            
            groups = []
            for i, target_size in enumerate(group_sizes):
                grp = [grp_players.pop(0) for _ in range(target_size) if grp_players]
                groups.append(grp)
        
        st.snow()
        st.markdown("---")
        st.subheader("📚 สรุปรายชื่อกลุ่มทำงาน")
        
        # แสดงผลกล่องสี
        cols = st.columns(2)
        colors = [st.success, st.warning, st.info, st.error]
        for i, grp in enumerate(groups):
            with cols[i % 2]:
                grp_names = ", ".join(grp) if grp else "*(ไม่มีสมาชิก)*"
                colors[i % 4](f"**📝 กลุ่มที่ {i+1}** (ต้องการ {group_sizes[i]} ได้ {len(grp)})\n\n👥 **สมาชิก:** {grp_names}")
                
        if grp_players: st.error(f"👤 **คนที่เหลือ (ไม่มีกลุ่ม):** {', '.join(grp_players)}")
        
        # ก๊อปปี้ข้อความย้ายมาด้านล่าง
        st.markdown("---")
        grp_lines = ["📚 สรุปกลุ่มทำงาน"]
        for i, grp in enumerate(groups):
            g_names = ", ".join(grp) if grp else "(ไม่มีสมาชิก)"
            grp_lines.append(f"กลุ่มที่ {i+1}: {g_names}")
        st.caption("👇 คัดลอกข้อความส่ง LINE")
        st.code("\n".join(grp_lines), language="text")

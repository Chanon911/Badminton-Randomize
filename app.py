import streamlit as st
import random
import re

# --- ตั้งค่าหน้าเว็บ (เปลี่ยนชื่อเป็น Hiso Random) ---
st.set_page_config(page_title="Hiso Random", page_icon="🎲", layout="centered")

# --- โหลดฟอนต์ Kanit และซ่อนเมนูที่ไม่จำเป็นของ Streamlit ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
        
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select, li, a {
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
    </style>
""", unsafe_allow_html=True)

# --- จัดการระบบความจำของเว็บ (Session State) ---
if 'player_stats' not in st.session_state: st.session_state.player_stats = {}
if 'priority_players' not in st.session_state: st.session_state.priority_players = []
if 'round_num' not in st.session_state: st.session_state.round_num = 1
if 'current_matches' not in st.session_state: st.session_state.current_matches = []
if 'waiting_data' not in st.session_state: st.session_state.waiting_data = ({}, [])

# --- เปลี่ยนชื่อ Title เว็บไซต์ ---
st.title("🎲 Hiso Random")

# --- กล่องใส่รายชื่อ (หน้าหลัก) ---
st.subheader("👥 รายชื่อผู้เล่นทั้งหมด")
raw_players = st.text_area("พิมพ์รายชื่อเว้นวรรค (ข้อมูลนี้ใช้ร่วมกันทุกระบบด้านล่าง)", "1 2 3 4 5 6 7 8 9 10")
player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]

for p in player_list:
    if p not in st.session_state.player_stats:
        st.session_state.player_stats[p] = {'played': 0, 'wins': 0}

st.markdown("---")

# --- สร้าง Tabs แยก 4 ระบบ ---
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
        
    if st.button("🔄 ล้างสถิติแบดมินตัน", key="reset_badminton"):
        st.session_state.player_stats = {}
        st.session_state.priority_players = []
        st.session_state.round_num = 1
        for p in player_list:
            st.session_state.player_stats[p] = {'played': 0, 'wins': 0}
        st.success("รีเซ็ตสถิติแบดมินตันเรียบร้อย!")
        st.rerun()

    players_per_team = 2 if "ตีคู่" in play_type else 1

    if st.button(f"🎲 สุ่มจัดทีมรอบที่ {st.session_state.round_num}", type="primary", use_container_width=True):
        slots_needed = int(num_courts) * players_per_team * 2
        priority_players = [p for p in st.session_state.priority_players if p in player_list]
        regular_players = [p for p in player_list if p not in priority_players]
        
        random.shuffle(regular_players)
        main_match_players = []
        new_priority = []

        if len(priority_players) >= slots_needed:
            main_match_players = priority_players[:slots_needed]
            new_priority = priority_players[slots_needed:] + regular_players
        else:
            main_match_players = priority_players.copy()
            needed = slots_needed - len(main_match_players)
            needed = min(needed, len(regular_players))
            main_match_players.extend(regular_players[:needed])
            new_priority = regular_players[needed:]

        random.shuffle(main_match_players)
        
        matches = []
        temp_main = main_match_players.copy()
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

    if st.session_state.current_matches:
        st.markdown("---")
        st.subheader(f"🔥 ผลการจัดทีมรอบที่ {st.session_state.round_num}")
        
        with st.form("score_form"):
            results = {}
            for match in st.session_state.current_matches:
                t1 = " & ".join(match["team1"])
                t2 = " & ".join(match["team2"])
                
                st.markdown(f"#### 📍 คอร์ดที่ {match['court']}")
                
                c1, c2, c3 = st.columns([4, 1, 4])
                with c1:
                    st.info(f"🔵 **ทีม 1:**\n\n{t1}")
                with c2:
                    st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)
                with c3:
                    st.error(f"🔴 **ทีม 2:**\n\n{t2}")
                
                results[match['court']] = st.radio(
                    f"บันทึกผล คอร์ดที่ {match['court']}", 
                    [
                        "ไม่คิดคะแนน / เสมอ", 
                        f"ทีม 1 ชนะ ({t1})", 
                        f"ทีม 2 ชนะ ({t2})"
                    ], 
                    horizontal=True, 
                    key=f"court_{match['court']}"
                )
                st.write("")
                st.markdown("---")
            
            if st.form_submit_button("บันทึกคะแนนและไปรอบต่อไป ✅", use_container_width=True):
                for match in st.session_state.current_matches:
                    res = results[match['court']]
                    if "ทีม 1" in res:
                        for p in match["team1"] + match["team2"]: st.session_state.player_stats[p]['played'] += 1
                        for p in match["team1"]: st.session_state.player_stats[p]['wins'] += 1
                    elif "ทีม 2" in res:
                        for p in match["team1"] + match["team2"]: st.session_state.player_stats[p]['played'] += 1
                        for p in match["team2"]: st.session_state.player_stats[p]['wins'] += 1
                st.session_state.round_num += 1
                st.session_state.current_matches = [] 
                st.rerun()

        waiting_teams, leftover = st.session_state.waiting_data
        if waiting_teams or leftover:
            st.info("🌟 **ทีมรอลงรอบหน้า (VIP):**")
            for i, t in enumerate(waiting_teams):
                st.write(f"- ทีมที่ {i+1}: {' & '.join(t)}")
            if leftover:
                st.write(f"- เศษรอจับคู่: {', '.join(leftover)}")

    st.markdown("---")
    st.subheader("🏆 MVP ประจำวัน")
    sorted_stats = sorted(st.session_state.player_stats.items(), key=lambda x: (x[1]['wins'], -x[1]['played']), reverse=True)
    table_data = [{"อันดับ": f"{'🥇' if i==0 else '🥈' if i==1 else '🥉' if i==2 else ''} {i+1}", "ชื่อ": p, "ชนะ": s['wins'], "เล่น": s['played'], "Win Rate": f"{(s['wins']/s['played']*100) if s['played']>0 else 0:.0f}%"} for i, (p, s) in enumerate(sorted_stats)]
    st.dataframe(table_data, use_container_width=True)

# ==========================================
# TAB 2: ระบบสุ่มคนขึ้นรถ (ปรับการแสดงผลใหม่)
# ==========================================
with tab2:
    st.subheader("🚗 สุ่มคนขึ้นรถ")
    num_cars = st.number_input("จำนวนรถทั้งหมด (คัน)", min_value=1, max_value=10, value=2, key="num_cars")
    cars_info = []
    
    for i in range(int(num_cars)):
        with st.expander(f"🚙 ตั้งค่ารถคันที่ {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                driver = st.selectbox(f"คนขับรถ", ["- ยังไม่ระบุ -"] + player_list, key=f"driver_{i}")
            with col2:
                capacity = st.number_input(f"ที่นั่ง (ไม่รวมคนขับ)", min_value=1, max_value=10, value=4, key=f"cap_{i}")
            cars_info.append({"car_num": i+1, "driver": driver, "capacity": capacity})
            
    if st.button("🎲 จัดคนขึ้นรถ", type="primary", use_container_width=True):
        drivers_list = [c["driver"] for c in cars_info if c["driver"] != "- ยังไม่ระบุ -"]
        passengers_list = [p for p in player_list if p not in drivers_list]
        random.shuffle(passengers_list)
        
        results = []
        for car in cars_info:
            car_passengers = [passengers_list.pop(0) for _ in range(int(car["capacity"])) if passengers_list]
            results.append({"car_num": car["car_num"], "driver": car["driver"], "passengers": car_passengers})
            
        st.markdown("---")
        st.subheader("🏁 ผลการจัดคนขึ้นรถ")
        
        cols = st.columns(2)
        colors = [st.info, st.success, st.warning, st.error]
        
        for i, res in enumerate(results):
            with cols[i % 2]:
                driver_name = res['driver'] if res['driver'] != "- ยังไม่ระบุ -" else "❓ ไม่มี"
                pass_names = ', '.join(res['passengers']) if res['passengers'] else '*(ไม่มี)*'
                
                # แสดงผลเป็นกล่องสีชัดเจน
                colors[i % 4](
                    f"**🚙 รถคันที่ {res['car_num']}**\n\n"
                    f"**🧑‍✈️ คนขับ:** {driver_name}\n\n"
                    f"**👥 ผู้โดยสาร:** {pass_names}"
                )
            
        if passengers_list:
            st.error(f"⚠️ **ที่นั่งไม่พอ! ตกหล่น {len(passengers_list)} คน:** {', '.join(passengers_list)}")
        else:
            st.success("✅ จัดคนขึ้นรถครบทุกคน!")

# ==========================================
# TAB 3: ระบบจัดทีมฟุตบอล (ปรับการแสดงผลใหม่)
# ==========================================
with tab3:
    st.subheader("⚽ สุ่มทีมฟุตบอล")
    col1, col2 = st.columns(2)
    with col1:
        num_fb_teams = st.number_input("จำนวนทีมฟุตบอล", min_value=2, max_value=10, value=2)
    with col2:
        players_per_fb = st.number_input("ผู้เล่นต่อทีม", min_value=1, max_value=11, value=5)
        
    if st.button("🎲 สุ่มทีมฟุตบอล", type="primary", use_container_width=True):
        fb_players = player_list.copy()
        random.shuffle(fb_players)
        
        fb_teams = []
        for _ in range(int(num_fb_teams)):
            team = [fb_players.pop(0) for _ in range(int(players_per_fb)) if fb_players]
            fb_teams.append(team)
            
        st.markdown("---")
        st.subheader("🏁 ผลการจัดทีมฟุตบอล")
        
        team_indices = list(range(len(fb_teams)))
        num_bibs = max(1, len(fb_teams) // 2)
        teams_with_bibs = random.sample(team_indices, k=num_bibs)
        team_kickoff = random.choice(team_indices)
        
        cols = st.columns(2)
        colors = [st.info, st.error, st.success, st.warning]
        
        for i, team in enumerate(fb_teams):
            with cols[i % 2]:
                bib_status = "🎽 **ใส่เสื้อกั๊ก**" if i in teams_with_bibs else "👕 **เสื้อสีปกติ**"
                kickoff_status = "👟 **ได้เขี่ยลูกก่อน!**" if i == team_kickoff else "🛡️ **รอรับบอล**"
                team_names = ", ".join(team) if team else "*(ไม่มีผู้เล่น)*"
                
                # แสดงผลเป็นกล่องสีชัดเจน
                colors[i % 4](
                    f"#### ⚽ ทีมที่ {i+1}\n\n"
                    f"{bib_status} | {kickoff_status}\n\n"
                    f"🏃‍♂️ **รายชื่อ:** {team_names}"
                )
                
        if fb_players:
            st.warning(f"🏃 **ตัวสำรอง / รอลงสนาม ({len(fb_players)} คน):** {', '.join(fb_players)}")

# ==========================================
# TAB 4: ระบบสุ่มทำงานกลุ่ม (ปรับการแสดงผลใหม่)
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
        grp_players = player_list.copy()
        random.shuffle(grp_players)
        
        groups = []
        for i, target_size in enumerate(group_sizes):
            grp = [grp_players.pop(0) for _ in range(target_size) if grp_players]
            groups.append(grp)
            
        st.markdown("---")
        st.subheader("📚 สรุปรายชื่อกลุ่มทำงาน")
        
        cols = st.columns(2)
        colors = [st.success, st.warning, st.info, st.error]
        
        for i, grp in enumerate(groups):
            with cols[i % 2]:
                grp_names = ", ".join(grp) if grp else "*(ไม่มีสมาชิก)*"
                
                # แสดงผลเป็นกล่องสีชัดเจน
                colors[i % 4](
                    f"**📝 กลุ่มที่ {i+1}** (ต้องการ {group_sizes[i]} คน | ได้ {len(grp)} คน)\n\n"
                    f"👥 **สมาชิก:** {grp_names}"
                )
                
        if grp_players:
            st.error(f"👤 **คนที่เหลือ (ไม่มีกลุ่ม - {len(grp_players)} คน):** {', '.join(grp_players)}")

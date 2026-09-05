import streamlit as st
import random
import re

# --- ตั้งค่าหน้าเว็บให้ดูมินิมอล ---
st.set_page_config(page_title="Randomizer Hub", page_icon="🎲", layout="centered")

# --- โหลดฟอนต์ Kanit และซ่อนเมนูที่ไม่จำเป็นของ Streamlit ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
        
        /* บังคับใช้ฟอนต์ Kanit */
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select, li, a {
            font-family: 'Kanit', sans-serif !important;
        }
        
        /* ซ่อนเมนู Streamlit และ Footer เพื่อความมินิมอล */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ตกแต่งปุ่มให้ดูคลีนขึ้น */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# --- จัดการระบบความจำของเว็บ (Session State) ---
if 'player_stats' not in st.session_state: st.session_state.player_stats = {}
if 'priority_players' not in st.session_state: st.session_state.priority_players = []
if 'round_num' not in st.session_state: st.session_state.round_num = 1
if 'current_matches' not in st.session_state: st.session_state.current_matches = []
if 'waiting_data' not in st.session_state: st.session_state.waiting_data = ({}, [])

# --- แถบตั้งค่าด้านข้าง (ใช้รายชื่อร่วมกันทั้งแอป) ---
with st.sidebar:
    st.header("⚙️ รายชื่อผู้เล่น")
    raw_players = st.text_area("พิมพ์ชื่อเว้นวรรค (ใช้ร่วมกันทุกหน้า)", "ชานนท์ ภู ธาม จักร ขมิ้น มิ้น พีช ปอย แพรว เตอร์x ช้าง คิน ฟิล์ม")
    player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]
    
    st.markdown("---")
    if st.button("🔄 ล้างสถิติแบดมินตัน"):
        st.session_state.player_stats = {}
        st.session_state.priority_players = []
        st.session_state.round_num = 1
        st.success("รีเซ็ตเรียบร้อย!")

for p in player_list:
    if p not in st.session_state.player_stats:
        st.session_state.player_stats[p] = {'played': 0, 'wins': 0}

# --- สร้าง Tabs แยก 4 ระบบ ---
tab1, tab2, tab3, tab4 = st.tabs(["🏸 แบดมินตัน", "🚗 สุ่มขึ้นรถ", "⚽ ฟุตบอล", "📚 ทำงานกลุ่ม"])

# ==========================================
# TAB 1: ระบบจัดทีมแบดมินตัน
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        num_courts = st.number_input("จำนวนคอร์ด", min_value=1, max_value=10, value=4)
    with col2:
        play_type = st.radio("ประเภทการเล่น", ["ตีคู่ (ทีมละ 2 คน)", "ตีเดี่ยว (ทีมละ 1 คน)"])
    
    players_per_team = 2 if "ตีคู่" in play_type else 1

    if st.button(f"🎲 สุ่มจัดทีมรอบที่ {st.session_state.round_num}", type="primary", use_container_width=True):
        slots_needed = num_courts * players_per_team * 2
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
                st.write(f"📍 **คอร์ด {match['court']}**: [{t1}] VS [{t2}]")
                results[match['court']] = st.radio(
                    f"ผลคอร์ด {match['court']}", 
                    ["ไม่คิดคะแนน", f"ทีม 1 ชนะ", f"ทีม 2 ชนะ"], 
                    horizontal=True, key=f"court_{match['court']}"
                )
                st.write("")
            
            if st.form_submit_button("บันทึกคะแนนและไปรอบต่อไป ✅"):
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
# TAB 2: ระบบสุ่มคนขึ้นรถ
# ==========================================
with tab2:
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
            car_passengers = [passengers_list.pop(0) for _ in range(car["capacity"]) if passengers_list]
            results.append({"car_num": car["car_num"], "driver": car["driver"], "passengers": car_passengers})
            
        st.markdown("---")
        for res in results:
            st.markdown(f"**🚙 รถคันที่ {res['car_num']}**")
            st.write(f"- **คนขับ:** {res['driver'] if res['driver'] != '- ยังไม่ระบุ -' else '❓ ไม่มี'}")
            st.write(f"- **ผู้โดยสาร:** {', '.join(res['passengers']) if res['passengers'] else '*(ไม่มี)*'}")
            st.write("")
            
        if passengers_list:
            st.error(f"⚠️ **ที่นั่งไม่พอ! ตกหล่น {len(passengers_list)} คน:** {', '.join(passengers_list)}")
        else:
            st.success("✅ จัดคนขึ้นรถครบทุกคน!")

# ==========================================
# TAB 3: ระบบจัดทีมฟุตบอล (มีสุ่มเสื้อกั๊ก + เขี่ยลูก)
# ==========================================
with tab3:
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
        
        # สุ่มหาทีมที่ใส่เสื้อกั๊ก (ครึ่งหนึ่งของจำนวนทีม) และทีมที่ได้เขี่ยลูก
        team_indices = list(range(len(fb_teams)))
        num_bibs = max(1, len(fb_teams) // 2)
        teams_with_bibs = random.sample(team_indices, k=num_bibs)
        team_kickoff = random.choice(team_indices)
        
        cols = st.columns(2)
        for i, team in enumerate(fb_teams):
            col_idx = i % 2
            with cols[col_idx]:
                st.markdown(f"#### ⚽ ทีมที่ {i+1}")
                
                # โชว์สถานะเสื้อกั๊กและเขี่ยลูก
                bib_status = "🎽 **ใส่เสื้อกั๊ก**" if i in teams_with_bibs else "👕 เสื้อสีปกติ"
                kickoff_status = "👟 **ได้เขี่ยลูกก่อน!**" if i == team_kickoff else "🛡️ รอรับบอล"
                
                st.caption(f"{bib_status} | {kickoff_status}")
                
                if team:
                    for p in team:
                        st.write(f"- {p}")
                else:
                    st.write("*(ไม่มีผู้เล่น)*")
                st.write("")
                
        if fb_players:
            st.warning(f"🏃 **ตัวสำรอง / รอลงสนาม ({len(fb_players)} คน):** {', '.join(fb_players)}")

# ==========================================
# TAB 4: ระบบสุ่มทำงานกลุ่ม
# ==========================================
with tab4:
    st.write("แบ่งสมาชิกออกเป็นกลุ่มย่อยๆ สามารถกำหนดจำนวนกลุ่มและคนในกลุ่มได้")
    
    col1, col2 = st.columns(2)
    with col1:
        num_groups = st.number_input("จำนวนกลุ่มที่ต้องการ", min_value=1, max_value=20, value=3)
    with col2:
        ppl_per_group = st.number_input("จำนวนคนต่อกลุ่ม", min_value=1, max_value=20, value=4)
        
    if st.button("🎲 สุ่มกลุ่มทำงาน", type="primary", use_container_width=True):
        grp_players = player_list.copy()
        random.shuffle(grp_players)
        
        groups = []
        for _ in range(int(num_groups)):
            # ดึงคนใส่กลุ่มตามจำนวนที่ระบุ
            grp = [grp_players.pop(0) for _ in range(int(ppl_per_group)) if grp_players]
            groups.append(grp)
            
        st.markdown("---")
        st.subheader("📚 สรุปรายชื่อกลุ่มทำงาน")
        
        cols = st.columns(2)
        for i, grp in enumerate(groups):
            col_idx = i % 2
            with cols[col_idx]:
                st.markdown(f"**📝 กลุ่มที่ {i+1}** ({len(grp)} คน)")
                if grp:
                    st.write(", ".join(grp))
                else:
                    st.write("*(ไม่มีสมาชิก)*")
                st.write("")
                
        # หากมีคนเหลือ (เศษ) ให้แจ้งเตือน
        if grp_players:
            st.warning(f"👤 **คนที่เหลือ (ไม่มีกลุ่ม - {len(grp_players)} คน):** {', '.join(grp_players)}")

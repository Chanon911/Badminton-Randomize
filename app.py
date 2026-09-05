import streamlit as st
import random
import re

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Randomizer Hub", page_icon="🎲", layout="centered")

# --- โหลดฟอนต์ Kanit จาก Google Fonts (แก้ไขปัญหาไอคอนลูกศรแล้ว) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
        
        /* บังคับใช้ฟอนต์ Kanit เฉพาะกับตัวอักษร ไม่ให้ไปกวนไอคอนระบบ */
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select, li, a {
            font-family: 'Kanit', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- จัดการระบบความจำของเว็บ (Session State) สำหรับแบดมินตัน ---
if 'player_stats' not in st.session_state: st.session_state.player_stats = {}
if 'priority_players' not in st.session_state: st.session_state.priority_players = []
if 'round_num' not in st.session_state: st.session_state.round_num = 1
if 'current_matches' not in st.session_state: st.session_state.current_matches = []
if 'waiting_data' not in st.session_state: st.session_state.waiting_data = ({}, [])

# --- แถบตั้งค่าด้านข้าง (ใช้รายชื่อร่วมกันทั้งแอป) ---
with st.sidebar:
    st.header("⚙️ รายชื่อประจำก๊วน")
    raw_players = st.text_area("👥 พิมพ์ชื่อเว้นวรรค (ใช้ร่วมกันทั้งแอป)", "ชานนท์ ภู ธาม จักร ขมิ้น มิ้น พีช ปอย แพรว เตอร์x ช้าง คิน ฟิล์ม")
    player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]
    
    st.markdown("---")
    if st.button("🔄 ล้างสถิติแบดมินตันทั้งหมด"):
        st.session_state.player_stats = {}
        st.session_state.priority_players = []
        st.session_state.round_num = 1
        st.success("รีเซ็ตสถิติแล้ว!")

# อัปเดตรายชื่อใหม่เข้าสู่ระบบสถิติ (สำหรับแบดมินตัน)
for p in player_list:
    if p not in st.session_state.player_stats:
        st.session_state.player_stats[p] = {'played': 0, 'wins': 0}

# --- สร้าง Tabs แยกหน้าการทำงาน ---
tab1, tab2 = st.tabs(["🏸 สุ่มทีมแบดมินตัน", "🚗 สุ่มคนขึ้นรถ"])

# ==========================================
# TAB 1: ระบบจัดทีมแบดมินตัน
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        num_courts = st.slider("🏸 จำนวนคอร์ดที่มี", 1, 10, 4)
    with col2:
        play_type = st.radio("ประเภทการเล่น", ["ตีคู่ (คอร์ดละ 4 คน)", "ตีเดี่ยว (คอร์ดละ 2 คน)"])
    
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
        for c in range(num_courts):
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

    # ส่วนแสดงผลและกรอกคะแนน
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
                    ["ไม่คิดคะแนน / เสมอ", f"ทีม 1 ชนะ ({t1})", f"ทีม 2 ชนะ ({t2})"], 
                    horizontal=True, key=f"court_{match['court']}"
                )
                st.write("")
            
            submitted = st.form_submit_button("บันทึกคะแนนและไปรอบต่อไป ✅")
            if submitted:
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
            st.info("🌟 **ทีมกระชับมิตร (VIP การันตีลงรอบหน้า):**")
            for i, t in enumerate(waiting_teams):
                st.write(f"- ทีมรอที่ {i+1}: {' & '.join(t)}")
            if leftover:
                st.write(f"- 👤 เศษผู้เล่นรอ: {', '.join(leftover)}")

    # ตาราง MVP
    st.markdown("---")
    st.subheader("🏆 ตารางคะแนน MVP ประจำวัน")
    sorted_stats = sorted(st.session_state.player_stats.items(), key=lambda x: (x[1]['wins'], -x[1]['played']), reverse=True)

    table_data = []
    for i, (player, stats) in enumerate(sorted_stats):
        win_rate = (stats['wins'] / stats['played'] * 100) if stats['played'] > 0 else 0
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
        table_data.append({
            "อันดับ": f"{medal} {i+1}", "ชื่อ": player, 
            "ชนะ": stats['wins'], "เล่น(รอบ)": stats['played'], "Win Rate": f"{win_rate:.0f}%"
        })
    st.dataframe(table_data, use_container_width=True)

# ==========================================
# TAB 2: ระบบสุ่มคนขึ้นรถ
# ==========================================
with tab2:
    st.subheader("🚗 ตั้งค่าขบวนรถ")
    num_cars = st.number_input("จำนวนรถทั้งหมด (คัน)", min_value=1, max_value=10, value=2)
    
    cars_info = []
    
    for i in range(int(num_cars)):
        with st.expander(f"🚙 ตั้งค่ารถคันที่ {i+1}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                driver = st.selectbox(f"🧑‍✈️ ล็อคตัวคนขับรถ", ["- ยังไม่ระบุ -"] + player_list, key=f"driver_{i}")
            with col2:
                capacity = st.number_input(f"💺 รับผู้โดยสารได้ (คน) *ไม่รวมคนขับ*", min_value=1, max_value=10, value=4, key=f"cap_{i}")
            
            cars_info.append({"car_num": i+1, "driver": driver, "capacity": capacity})
            
    st.markdown("---")
    if st.button("🎲 สุ่มจัดคนขึ้นรถ", type="primary", use_container_width=True):
        
        drivers_list = [c["driver"] for c in cars_info if c["driver"] != "- ยังไม่ระบุ -"]
        passengers_list = [p for p in player_list if p not in drivers_list]
        random.shuffle(passengers_list)
        
        results = []
        
        for car in cars_info:
            car_passengers = []
            for _ in range(car["capacity"]):
                if passengers_list:
                    car_passengers.append(passengers_list.pop(0))
            
            results.append({
                "car_num": car["car_num"],
                "driver": car["driver"],
                "passengers": car_passengers
            })
            
        st.subheader("🏁 ผลการจัดคนขึ้นรถ")
        for res in results:
            driver_name = res['driver'] if res['driver'] != "- ยังไม่ระบุ -" else "❓ ไม่มีคนขับ"
            st.markdown(f"#### 🚙 รถคันที่ {res['car_num']}")
            st.write(f"**🧑‍✈️ คนขับ:** {driver_name}")
            
            if res['passengers']:
                st.write(f"**👥 ผู้โดยสาร:** {', '.join(res['passengers'])}")
            else:
                st.write("**👥 ผู้โดยสาร:** *(ไม่มี)*")
            st.markdown("---")
            
        if passengers_list:
            st.error(f"⚠️ **มีคนตกหล่น (ที่นั่งไม่พอ {len(passengers_list)} คน):** {', '.join(passengers_list)}")
        else:
            st.success("✅ ทุกคนได้ขึ้นรถครบเรียบร้อย เดินทางปลอดภัยครับ!")

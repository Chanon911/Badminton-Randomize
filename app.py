import streamlit as st
import random
import re

st.set_page_config(page_title="Badminton Matchmaker", page_icon="🏸")

# --- 1. จัดการระบบความจำของเว็บ (Session State) ---
if 'player_stats' not in st.session_state:
    st.session_state.player_stats = {}
if 'priority_players' not in st.session_state:
    st.session_state.priority_players = []
if 'round_num' not in st.session_state:
    st.session_state.round_num = 1
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = []
if 'waiting_data' not in st.session_state:
    st.session_state.waiting_data = ({}, [])

st.title("🏸 โปรแกรมจัดทีมแบดมินตัน")

# --- 2. ส่วนตั้งค่า (แถบด้านข้าง หรือ ด้านบนบนมือถือ) ---
with st.sidebar:
    st.header("⚙️ ตั้งค่าการเล่น")
    raw_players = st.text_area("👥 รายชื่อผู้เล่น (เว้นวรรค)", "1 2 3 4 5 6 7 8 9 10")
    num_courts = st.slider("🏸 จำนวนคอร์ด", 1, 10, 2)
    play_type = st.radio("ประเภท", ["ตีคู่ (ทีมละ 2 คน)", "ตีเดี่ยว (ทีมละ 1 คน)"])
    
    if st.button("🔄 รีเซ็ตสถิติทั้งหมด"):
        st.session_state.player_stats = {}
        st.session_state.priority_players = []
        st.session_state.round_num = 1
        st.success("รีเซ็ตข้อมูลแล้ว!")

players_per_team = 2 if "ตีคู่" in play_type else 1
player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]

# อัปเดตรายชื่อใหม่เข้าสู่ระบบ
for p in player_list:
    if p not in st.session_state.player_stats:
        st.session_state.player_stats[p] = {'played': 0, 'wins': 0}

# --- 3. ปุ่มกดเพื่อสุ่มทีม ---
if st.button(f"🎲 สุ่มจัดทีมรอบที่ {st.session_state.round_num}", type="primary"):
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
    
    # จับคู่ลงคอร์ด
    matches = []
    temp_main = main_match_players.copy()
    for c in range(num_courts):
        if len(temp_main) >= players_per_team * 2:
            team1 = [temp_main.pop(0) for _ in range(players_per_team)]
            team2 = [temp_main.pop(0) for _ in range(players_per_team)]
            matches.append({"court": c + 1, "team1": team1, "team2": team2})
    
    # จับคู่ทีมรอ
    waiting_teams = []
    temp_wait = new_priority.copy()
    while len(temp_wait) >= players_per_team:
        waiting_teams.append([temp_wait.pop(0) for _ in range(players_per_team)])
        
    st.session_state.current_matches = matches
    st.session_state.waiting_data = (waiting_teams, temp_wait)
    st.session_state.priority_players = new_priority.copy()

# --- 4. แสดงผลการจัดทีมและฟอร์มกรอกคะแนน ---
if st.session_state.current_matches:
    st.markdown("---")
    st.subheader(f"🔥 ผลการจัดทีมรอบที่ {st.session_state.round_num}")
    
    with st.form("score_form"):
        results = {}
        for match in st.session_state.current_matches:
            t1 = " & ".join(match["team1"])
            t2 = " & ".join(match["team2"])
            st.write(f"📍 **คอร์ด {match['court']}**: [{t1}] VS [{t2}]")
            # สร้างตัวเลือกให้กดง่ายๆ บนมือถือ
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
            st.session_state.current_matches = [] # เคลียร์แมตช์เพื่อสุ่มใหม่
            st.rerun()

    # แสดงทีมรอ (VIP)
    waiting_teams, leftover = st.session_state.waiting_data
    if waiting_teams or leftover:
        st.info("🌟 **ทีมกระชับมิตร (VIP การันตีลงรอบหน้า):**")
        for i, t in enumerate(waiting_teams):
            st.write(f"- ทีมรอที่ {i+1}: {' & '.join(t)}")
        if leftover:
            st.write(f"- 👤 เศษผู้เล่นรอ: {', '.join(leftover)}")

# --- 5. ตาราง MVP ---
st.markdown("---")
st.subheader("🏆 ตารางคะแนน MVP ประจำวัน")
sorted_stats = sorted(st.session_state.player_stats.items(), key=lambda x: (x[1]['wins'], -x[1]['played']), reverse=True)

# สร้างตารางข้อมูลให้ดูง่ายๆ
table_data = []
for i, (player, stats) in enumerate(sorted_stats):
    win_rate = (stats['wins'] / stats['played'] * 100) if stats['played'] > 0 else 0
    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
    table_data.append({
        "อันดับ": f"{medal} {i+1}", "ชื่อ": player, 
        "ชนะ": stats['wins'], "เล่น(รอบ)": stats['played'], "Win Rate": f"{win_rate:.0f}%"
    })
st.dataframe(table_data, use_container_width=True)

import streamlit as st
import random
import re
import time
from datetime import datetime
import pytz
import requests 

# --- ตั้งค่าหน้าเว็บ (Hiso Random) ---
st.set_page_config(page_title="Hiso Random", page_icon="🎲", layout="centered")

# --- ฟังก์ชันแอนิเมชันไพ่ทาโรต์ ---
def show_tarot_animation():
    uid = random.randint(10000, 99999)
    st.markdown(f"""
        <style>
            @keyframes tarotFall_{uid} {{
                0% {{ top: -10%; transform: rotate(0deg) scale(1); opacity: 1; }}
                100% {{ top: 110%; transform: rotate(720deg) scale(1.2); opacity: 0; }}
            }}
            .tarot-card-{uid} {{
                position: fixed;
                font-size: 3.5rem;
                z-index: 999999;
                pointer-events: none;
                user-select: none;
                animation: tarotFall_{uid} 3s ease-in forwards;
            }}
        </style>
        <div class="tarot-card-{uid}" style="left: 5%; animation-duration: 2.0s; animation-delay: 0s;">🃏</div>
        <div class="tarot-card-{uid}" style="left: 15%; animation-duration: 2.5s; animation-delay: 0.2s;">🎴</div>
        <div class="tarot-card-{uid}" style="left: 25%; animation-duration: 2.2s; animation-delay: 0.5s;">🔮</div>
        <div class="tarot-card-{uid}" style="left: 35%; animation-duration: 2.8s; animation-delay: 0.1s;">🃏</div>
        <div class="tarot-card-{uid}" style="left: 45%; animation-duration: 2.3s; animation-delay: 0.4s;">✨</div>
        <div class="tarot-card-{uid}" style="left: 55%; animation-duration: 2.6s; animation-delay: 0.2s;">🎴</div>
        <div class="tarot-card-{uid}" style="left: 65%; animation-duration: 2.1s; animation-delay: 0.6s;">🃏</div>
        <div class="tarot-card-{uid}" style="left: 75%; animation-duration: 2.7s; animation-delay: 0.3s;">🔮</div>
        <div class="tarot-card-{uid}" style="left: 85%; animation-duration: 2.4s; animation-delay: 0.5s;">🎴</div>
        <div class="tarot-card-{uid}" style="left: 95%; animation-duration: 2.9s; animation-delay: 0.1s;">🃏</div>
    """, unsafe_allow_html=True)


# ==========================================
# 🌐 ส่วนเชื่อมต่อฐานข้อมูล Google Sheets
# ==========================================
API_URL = "https://script.google.com/macros/s/AKfycbz8DpXlLxi5FzmaRYxhiWlBmNtJTdX4pLeI5z8rFRql4E8qfEo1M4g32FXNEJCB8PAy9g/exec"

def load_history():
    try:
        res = requests.get(API_URL)
        return res.json()
    except:
        return []

def add_to_history(category, title, detail_text):
    tz = pytz.timezone('Asia/Bangkok')
    now = datetime.now(tz)
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")
    full_time_str = f"{date_str} {time_str}"
    
    item_id = f"ID_{int(time.time() * 1000)}_{random.randint(100,999)}"
    
    new_log = {
        "action": "add",
        "id": item_id,
        "category": category, 
        "time": f"'{full_time_str}", 
        "title": title, 
        "detail": detail_text
    }
    
    st.session_state.history_log.insert(0, new_log)
    try:
        requests.post(API_URL, json=new_log)
    except:
        pass

def delete_history_item(item_id):
    st.session_state.history_log = [log for log in st.session_state.history_log if log.get('id') != item_id]
    try:
        requests.post(API_URL, json={"action": "delete", "id": item_id})
    except:
        pass
# ==========================================


# --- โหลดฟอนต์ Kanit และปรับแต่ง UI ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');
        html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select, li, a, div.stMetric {
            font-family: 'Kanit', sans-serif !important;
        }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stButton>button { border-radius: 8px; font-weight: 500; }
        .vs-text { text-align: center; font-size: 1.2rem; font-weight: bold; margin-top: 15px; color: #555; }
        div[data-testid="metric-container"] { background-color: #f8f9fa; border-radius: 10px; padding: 10px; text-align: center; border: 1px solid #e0e0e0; }
        .date-header { color: #888; font-size: 1.1rem; font-weight: 500; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- จัดการระบบความจำของเว็บ ---
if 'player_stats' not in st.session_state: st.session_state.player_stats = {}
if 'pair_hist' not in st.session_state: st.session_state.pair_hist = {}
if 'priority_players' not in st.session_state: st.session_state.priority_players = []
if 'round_num' not in st.session_state: st.session_state.round_num = 1
if 'current_matches' not in st.session_state: st.session_state.current_matches = []
if 'waiting_data' not in st.session_state: st.session_state.waiting_data = ({}, [])
if 'show_history' not in st.session_state: st.session_state.show_history = False # ตัวแปรสำหรับคุมปุ่มประวัติ

# โหลดข้อมูลประวัติจาก Google Sheets ตอนเปิดเว็บครั้งแรก
if 'history_log' not in st.session_state: 
    st.session_state.history_log = load_history()

def toggle_history():
    st.session_state.show_history = not st.session_state.show_history

st.title("🎲 Hiso Random")

st.subheader("👥 รายชื่อผู้เล่นทั้งหมด")
raw_players = st.text_area("พิมพ์รายชื่อเว้นวรรค (ข้อมูลนี้ใช้ร่วมกันทุกระบบด้านล่าง)", "1 2 3 4 5 6 7 8 9 10")
player_list = [name.strip() for name in re.split(r'[,\s]+', raw_players) if name.strip()]

for p in player_list:
    if p not in st.session_state.player_stats: st.session_state.player_stats[p] = {'played': 0, 'wins': 0}
    if p not in st.session_state.pair_hist: st.session_state.pair_hist[p] = {}

st.metric("👥 สมาชิกทั้งหมด", f"{len(player_list)} คน")

# --- ปุ่มกดดูประวัติ (อยู่ใต้จำนวนคน) ---
if st.session_state.show_history:
    st.button("⬅️ กลับไปหน้าสุ่มหลัก", on_click=toggle_history, type="primary", use_container_width=True)
else:
    st.button("📜 ประวัติการสุ่มย้อนหลัง", on_click=toggle_history, use_container_width=True)

st.markdown("---")

# ==========================================
# สลับหน้าจอ: ถ้ากดปุ่มให้โชว์ประวัติ / ถ้าไม่กดให้โชว์แท็บสุ่ม
# ==========================================
if st.session_state.show_history:
    st.subheader("📜 ประวัติการสุ่มย้อนหลัง (เชื่อมต่อ Database)")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        filter_category = st.radio("กรองหมวดหมู่:", ["ทั้งหมด", "แบดมินตัน", "จัดคนขึ้นรถ", "ทีมฟุตบอล", "ทำงานกลุ่ม"], horizontal=True)
    with col2:
        if st.button("🔄 โหลดข้อมูลใหม่"):
            st.session_state.history_log = load_history()
            st.rerun()
            
    if not st.session_state.history_log:
        st.info("ยังไม่มีประวัติการสุ่มในขณะนี้ หรือกำลังรอการเชื่อมต่อ...")
    else:
        filtered_log = st.session_state.history_log if filter_category == "ทั้งหมด" else [log for log in st.session_state.history_log if log.get('category') == filter_category]
        
        if not filtered_log:
            st.info(f"ยังไม่มีประวัติในหมวดหมู่ '{filter_category}'")
        else:
            # ระบบจัดกลุ่มตามวันที่
            grouped_logs = {}
            for log in filtered_log:
                raw_time = log.get('time', '').replace("'", "")
                parts = raw_time.split(" ")
                
                if len(parts) >= 2:
                    date_part = parts[0]
                    time_part = " ".join(parts[1:])
                else:
                    date_part = "รายการเก่า (ไม่มีวันที่)"
                    time_part = raw_time
                    
                if date_part not in grouped_logs:
                    grouped_logs[date_part] = []
                grouped_logs[date_part].append({**log, 'display_time': time_part})
                
            # แสดงผลทีละกลุ่มวันที่
            for d_str, logs_in_date in grouped_logs.items():
                st.markdown(f"<div class='date-header'>📅 วันที่: {d_str}</div>", unsafe_allow_html=True)
                
                for log in logs_in_date:
                    with st.expander(f"🕒 {log['display_time']} | {log['title']}", expanded=False):
                        st.code(log['detail'], language="text")
                        
                        if st.button("🗑️ ลบรายการนี้", key=f"del_{log.get('id', random.randint(1,99999))}"):
                            delete_history_item(log['id'])
                            st.success("ลบรายการนี้สำเร็จ! กำลังโหลดหน้าจอใหม่...")
                            time.sleep(0.5)
                            st.rerun()

else:
    # --- กลับมาหน้าสุ่มปกติ (แท็บ 1-4) ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏸 แบดมินตัน", "🚗 สุ่มขึ้นรถ", "⚽ ฟุตบอล", "📚 ทำงานกลุ่ม"])

    # ==========================================
    # TAB 1: ระบบจัดทีมแบดมินตัน
    # ==========================================
    with tab1:
        st.subheader("🏸 สุ่มทีมแบดมินตัน")
        
        wins = [s['wins'] for s in st.session_state.player_stats.values()] if st.session_state.player_stats else [0]
        max_wins = max(wins) if wins else 0
        mvps = [p for p, s in st.session_state.player_stats.items() if s['wins'] == max_wins and max_wins > 0]
        
        m1, m2 = st.columns(2)
        m1.metric("🏆 ผู้นำ MVP ตอนนี้", ", ".join(mvps) if mvps else "-")
        m2.metric("🪑 รอคิวตีแบด (คนเศษ)", f"{len(st.session_state.waiting_data[1]) if len(st.session_state.waiting_data) > 1 else 0} คน")
        st.write("")
        
        col1, col2 = st.columns(2)
        with col1: num_courts = st.number_input("จำนวนคอร์ด", min_value=1, max_value=10, value=2)
        with col2: play_type = st.radio("ประเภทการเล่น", ["ตีคู่ (ทีมละ 2 คน)", "ตีเดี่ยว (ทีมละ 1 คน)"])
            
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
            st.success("รีเซ็ตสถิติเรียบร้อย!")
            time.sleep(1)
            st.rerun()

        players_per_team = 2 if "ตีคู่" in play_type else 1

        if st.button(f"🎲 สุ่มจัดทีมรอบที่ {st.session_state.round_num}", type="primary", use_container_width=True):
            show_tarot_animation()
            ph = st.empty(); ph.write(""); time.sleep(1.5); ph.empty()
            
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
                    matches.append({"court": c + 1, "team1": [temp_main.pop(0) for _ in range(players_per_team)], "team2": [temp_main.pop(0) for _ in range(players_per_team)]})
            
            waiting_teams = []
            temp_wait = new_priority.copy()
            while len(temp_wait) >= players_per_team: waiting_teams.append([temp_wait.pop(0) for _ in range(players_per_team)])
                
            st.session_state.current_matches = matches
            st.session_state.waiting_data = (waiting_teams, temp_wait)
            st.session_state.priority_players = new_priority.copy()
            
            summary_lines = [f"🏸 จัดทีมแบดมินตัน รอบที่ {st.session_state.round_num}"]
            for m in matches: summary_lines.append(f"📍 คอร์ด {m['court']}: [{' & '.join(m['team1'])}] VS [{' & '.join(m['team2'])}]")
            if waiting_teams or temp_wait:
                summary_lines.append("🌟 ทีมรอรอบถัดไป:")
                for i, t in enumerate(waiting_teams): summary_lines.append(f"- รอที่ {i+1}: {' & '.join(t)}")
                if temp_wait: summary_lines.append(f"- เศษคนรอ: {', '.join(temp_wait)}")
            
            add_to_history("แบดมินตัน", f"🏸 แบดมินตัน (รอบที่ {st.session_state.round_num})", "\n".join(summary_lines))

        if st.session_state.current_matches:
            st.markdown("---")
            st.subheader(f"🔥 ผลการจัดทีมรอบที่ {st.session_state.round_num}")
            with st.form("score_form"):
                results = {}
                for match in st.session_state.current_matches:
                    t1, t2 = " & ".join(match["team1"]), " & ".join(match["team2"])
                    c1, c2, c3 = st.columns([4, 1, 4])
                    with c1: st.info(f"🔵 **คอร์ด {match['court']} | ทีม 1:**\n\n{t1}")
                    with c2: st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)
                    with c3: st.error(f"🔴 **คอร์ด {match['court']} | ทีม 2:**\n\n{t2}")
                    results[match['court']] = st.radio(f"บันทึกผล คอร์ด {match['court']}", ["ไม่คิดคะแนน / เสมอ", f"ทีม 1 ชนะ", f"ทีม 2 ชนะ"], horizontal=True, key=f"court_{match['court']}")
                    st.markdown("---")
                
                waiting_teams, leftover = st.session_state.waiting_data
                if waiting_teams or leftover:
                    st.markdown("#### 🌟 ทีมรอรอบถัดไป (VIP การันตีลงสนาม)")
                    w_cols = st.columns(2)
                    for i, t in enumerate(waiting_teams):
                        with w_cols[i % 2]: st.warning(f"⏳ **ทีมรอที่ {i+1}:**\n\n{' & '.join(t)}")
                    if leftover: st.error(f"👤 **เศษคนรอจับคู่:**\n\n{', '.join(leftover)}")
                    st.markdown("---")
                
                summary_lines = [f"🏸 จัดทีมแบดมินตัน รอบที่ {st.session_state.round_num}"]
                for m in st.session_state.current_matches: summary_lines.append(f"📍 คอร์ด {m['court']}: [{' & '.join(m['team1'])}] VS [{' & '.join(m['team2'])}]")
                if waiting_teams or leftover:
                    summary_lines.append("🌟 ทีมรอรอบถัดไป:")
                    for i, t in enumerate(waiting_teams): summary_lines.append(f"- รอที่ {i+1}: {' & '.join(t)}")
                    if leftover: summary_lines.append(f"- เศษคนรอ: {', '.join(leftover)}")
                    
                st.caption("👇 คัดลอกข้อความสรุปผลเพื่อส่ง LINE")
                st.code("\n".join(summary_lines), language="text")
                
                if st.form_submit_button("บันทึกคะแนนและไปรอบต่อไป ✅", use_container_width=True):
                    for match in st.session_state.current_matches:
                        res = results[match['court']]
                        for team in [match["team1"], match["team2"]]:
                            for i in range(len(team)):
                                for j in range(i+1, len(team)):
                                    st.session_state.pair_hist[team[i]][team[j]] = st.session_state.pair_hist.get(team[i], {}).get(team[j], 0) + 1
                                    st.session_state.pair_hist[team[j]][team[i]] = st.session_state.pair_hist.get(team[j], {}).get(team[i], 0) + 1
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
                c1, c2 = st.columns(2)
                with c1: driver = st.selectbox(f"คนขับรถ", ["- ยังไม่ระบุ -"] + player_list, key=f"driver_{i}")
                with c2: capacity = st.number_input(f"ที่นั่ง (ไม่รวมคนขับ)", min_value=1, max_value=10, value=4, key=f"cap_{i}")
                cars_info.append({"car_num": i+1, "driver": driver, "capacity": capacity})
                
        if st.button("🎲 จัดคนขึ้นรถ", type="primary", use_container_width=True):
            show_tarot_animation()
            ph = st.empty(); ph.write(""); time.sleep(1.5); ph.empty()
            
            drivers_list = [c["driver"] for c in cars_info if c["driver"] != "- ยังไม่ระบุ -"]
            passengers_list = [p for p in player_list if p not in drivers_list]
            random.shuffle(passengers_list)
            
            results = []
            for car in cars_info:
                results.append({"car_num": car["car_num"], "driver": car["driver"], "passengers": [passengers_list.pop(0) for _ in range(int(car["capacity"])) if passengers_list]})
                
            car_lines = ["🚗 สรุปการจัดคนขึ้นรถ"]
            for res in results: car_lines.append(f"🚙 รถคันที่ {res['car_num']} | คนขับ: {res['driver'] if res['driver'] != '- ยังไม่ระบุ -' else 'ไม่มี'} | ผดส: {', '.join(res['passengers']) if res['passengers'] else '(ไม่มี)'}")
            add_to_history("จัดคนขึ้นรถ", "🚗 ผลสุ่มขบวนรถ", "\n".join(car_lines))
                
            st.markdown("---")
            st.subheader("🏁 ผลการจัดคนขึ้นรถ")
            cols = st.columns(2)
            colors = [st.info, st.success, st.warning, st.error]
            for i, res in enumerate(results):
                with cols[i % 2]: colors[i % 4](f"**🚙 รถคันที่ {res['car_num']}**\n\n**🧑‍✈️ คนขับ:** {res['driver'] if res['driver'] != '- ยังไม่ระบุ -' else '❓ ไม่มี'}\n\n**👥 ผดส:** {', '.join(res['passengers']) if res['passengers'] else '*(ไม่มี)*'}")
            if passengers_list: st.error(f"⚠️ **ตกหล่น {len(passengers_list)} คน:** {', '.join(passengers_list)}")
                
            st.markdown("---")
            st.caption("👇 คัดลอกข้อความส่ง LINE")
            st.code("\n".join(car_lines), language="text")

    # ==========================================
    # TAB 3: ระบบจัดทีมฟุตบอล
    # ==========================================
    with tab3:
        st.subheader("⚽ สุ่มทีมฟุตบอล")
        c1, c2 = st.columns(2)
        with c1: num_fb_teams = st.number_input("จำนวนทีมฟุตบอล", min_value=2, max_value=10, value=2)
        with c2: players_per_fb = st.number_input("ผู้เล่นต่อทีม", min_value=1, max_value=11, value=5)
            
        if st.button("🎲 สุ่มทีมฟุตบอล", type="primary", use_container_width=True):
            show_tarot_animation()
            ph = st.empty(); ph.write(""); time.sleep(1.5); ph.empty()
            
            fb_players = player_list.copy()
            random.shuffle(fb_players)
            
            fb_teams = [[fb_players.pop(0) for _ in range(int(players_per_fb)) if fb_players] for _ in range(int(num_fb_teams))]
            team_indices = list(range(len(fb_teams)))
            teams_with_bibs = random.sample(team_indices, k=max(1, len(fb_teams) // 2))
            team_kickoff = random.choice(team_indices)
            
            fb_lines = ["⚽ สรุปทีมฟุตบอล"]
            for i, team in enumerate(fb_teams): fb_lines.append(f"ทีมที่ {i+1} {'🎽 (เสื้อกั๊ก)' if i in teams_with_bibs else '👕 (สีปกติ)'} {'👟 เขี่ยก่อน' if i == team_kickoff else ''}\nรายชื่อ: {', '.join(team) if team else '(ไม่มีผู้เล่น)'}")
            add_to_history("ทีมฟุตบอล", "⚽ ผลจัดทีมฟุตบอล", "\n\n".join(fb_lines))
                
            st.markdown("---")
            st.subheader("🏁 ผลการจัดทีมฟุตบอล")
            cols = st.columns(2)
            colors = [st.info, st.error, st.success, st.warning]
            for i, team in enumerate(fb_teams):
                with cols[i % 2]: colors[i % 4](f"#### ⚽ ทีมที่ {i+1}\n\n{'🎽 **ใส่เสื้อกั๊ก**' if i in teams_with_bibs else '👕 **เสื้อสีปกติ**'} | {'👟 **ได้เขี่ยลูกก่อน!**' if i == team_kickoff else '🛡️ **รอรับบอล**'}\n\n🏃‍♂️ **รายชื่อ:** {', '.join(team) if team else '*(ไม่มีผู้เล่น)*'}")
            if fb_players: st.warning(f"🏃 **ตัวสำรอง / รอลงสนาม:** {', '.join(fb_players)}")
            
            st.markdown("---")
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
            with cols[i % 3]: group_sizes.append(int(st.number_input(f"กลุ่มที่ {i+1} (คน)", min_value=1, max_value=20, value=3, key=f"grp_size_{i}")))
                
        if st.button("🎲 สุ่มกลุ่มทำงาน", type="primary", use_container_width=True):
            show_tarot_animation()
            ph = st.empty(); ph.write(""); time.sleep(1.5); ph.empty()
            
            grp_players = player_list.copy()
            random.shuffle(grp_players)
            groups = [[grp_players.pop(0) for _ in range(target_size) if grp_players] for target_size in group_sizes]
                
            grp_lines = ["📚 สรุปกลุ่มทำงาน"]
            for i, grp in enumerate(groups): grp_lines.append(f"กลุ่มที่ {i+1}: {', '.join(grp) if grp else '(ไม่มีสมาชิก)'}")
            add_to_history("ทำงานกลุ่ม", "📚 ผลสุ่มกลุ่มทำงาน", "\n".join(grp_lines))
            
            st.markdown("---")
            st.subheader("📚 สรุปรายชื่อกลุ่มทำงาน")
            cols = st.columns(2)
            colors = [st.success, st.warning, st.info, st.error]
            for i, grp in enumerate(groups):
                with cols[i % 2]: colors[i % 4](f"**📝 กลุ่มที่ {i+1}** (ต้องการ {group_sizes[i]} ได้ {len(grp)})\n\n👥 **สมาชิก:** {', '.join(grp) if grp else '*(ไม่มีสมาชิก)*'}")
            if grp_players: st.error(f"👤 **คนที่เหลือ (ไม่มีกลุ่ม):** {', '.join(grp_players)}")
            
            st.markdown("---")
            st.caption("👇 คัดลอกข้อความส่ง LINE")
            st.code("\n".join(grp_lines), language="text")

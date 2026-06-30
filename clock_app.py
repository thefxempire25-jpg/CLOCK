import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import pytz

# --- SYSTEM PAGE LAYOUT ---
st.set_page_config(page_title="SURGICAL // CHRONO DESK (GMT)", layout="centered")

# --- CSS MASTER INJECTION ---
st.markdown("""
    <style>
    .stApp { 
        background-color: #020617;
        background-image: 
            radial-gradient(circle at top, rgba(15, 23, 42, 0.94) 0%, #020617 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M27 13h6v4h-6zm0 10h6v4h-6zm0 10h6v4h-6zM13 27h4v6h-4zm10 0h4v6h-4zm10 0h4v6h-4z' fill='%2300f0ff' fill-opacity='0.025' fill-rule='evenodd'/%3E%3C/svg%3E");
        background-repeat: repeat;
        color: #ffffff; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif;
    }
    
    .profile-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0 25px 0; }
    .profile-meta h2 { font-size: 18px; margin: 0; color: #ffffff; font-weight: 600; }
    .profile-meta p { font-size: 12px; margin: 0; color: #64748b; }
    .status-ping { width: 10px; height: 10px; background-color: #00f0ff; border-radius: 50%; box-shadow: 0 0 10px #00f0ff; }

    .theater-container { background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 24px; padding: 30px 20px; text-align: center; margin-bottom: 25px; backdrop-filter: blur(10px); }
    .theater-title { font-size: 13px; color: #94a3b8; letter-spacing: 2px; font-weight: 600; margin-bottom: 25px; }
    .spotlight-wrapper { display: flex; justify-content: center; margin: 10px 0 25px 0; }
    
    .surgical-circle-active {
        width: 280px; height: 280px; border-radius: 50%;
        background: radial-gradient(circle, #0f172a 40%, #020617 100%);
        border: 3px solid #00f0ff; box-shadow: 0 0 40px rgba(0, 240, 255, 0.25);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .vitals-halo { font-size: 11px; color: #94a3b8; letter-spacing: 2px; font-weight: 700; margin-bottom: 8px; }
    .target-ticker { font-size: 26px; font-weight: 800; color: #ffffff; margin: 0; text-align: center; }
    .target-action { font-size: 13px; font-weight: 700; color: #00f0ff; letter-spacing: 1.5px; margin-top: 5px; }

    .calc-box { background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 16px; padding: 20px; margin-top: 20px; backdrop-filter: blur(10px); }
    
    .session-badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; display: inline-block; min-width: 65px; text-align: center; }
    .open-true { background: rgba(0, 240, 255, 0.15); color: #00f0ff; border: 1px solid rgba(0, 240, 255, 0.3); }
    .open-false { background: rgba(100, 116, 139, 0.1); color: #64748b; border: 1px solid rgba(100, 116, 139, 0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- SYSTEM TIMING ALGORITHM (FIXED TO GMT/UTC) ---
def get_session_statuses():
    now_gmt = datetime.now(pytz.utc)
    current_time = now_gmt.time()
    current_weekday = now_gmt.weekday() 

    # All session boundaries converted directly to raw GMT values
    sessions = {
        "Tokyo Open": {"start": time(0, 0), "end": time(6, 0)},
        "London Open": {"start": time(7, 0), "end": time(15, 30)},
        "New York Open": {"start": time(12, 30), "end": time(19, 0)},
        "CME Globex Reopen": {"start": time(22, 0), "end": time(21, 0)}
    }
    
    status_matrix = {}
    for name, window in sessions.items():
        is_open = False
        if current_weekday < 5 or (current_weekday == 6 and current_time >= time(22, 0)) or (current_weekday == 4 and current_time <= time(21, 0)):
            if window["start"] <= window["end"]:
                is_open = window["start"] <= current_time <= window["end"]
            else: 
                is_open = current_time >= window["start"] or current_time <= window["end"]
                
        target_datetime = datetime.combine(now_gmt.date(), window["start"]).replace(tzinfo=pytz.utc)
        if now_gmt > target_datetime:
            target_datetime += timedelta(days=1)
        countdown = target_datetime - now_gmt
        
        hours, remainder = divmod(countdown.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        status_matrix[name] = {
            "is_open": is_open,
            "countdown_str": f"{hours:02d}h {minutes:02d}m {seconds:02d}s" if not is_open else "LIVE ONGOING"
        }
    return status_matrix, now_gmt

# --- SOUND EMISSION HARNESS ---
ALARM_URL = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
def emit_system_bell():
    sound_html = f'<audio autoplay style="display:none;"><source src="{ALARM_URL}" type="audio/ogg"></audio>'
    st.markdown(sound_html, unsafe_allow_html=True)

if "last_triggered_session" not in st.session_state: st.session_state.last_triggered_session = None

# --- PROCESS TIMING UPDATES ---
clock_states, current_gmt_dt = get_session_statuses()

# Audio handover checks
for s_name, data in clock_states.items():
    if data["is_open"] and st.session_state.last_triggered_session != s_name:
        st.session_state.last_triggered_session = s_name
        emit_system_bell()

# --- HEADER INTERFACE LAYER ---
st.markdown(f"""
    <div class="profile-container">
        <div class="profile-meta">
            <h2>Gozan Bless</h2>
            <p>Surgical Timing & News Desk // THEFXEMPIRE</p>
        </div>
        <div class="status-ping"></div>
    </div>
""", unsafe_allow_html=True)

# --- THEATRE SPOTLIGHT: LIVE GMT FOCUS ---
active_sessions = [name for name, data in clock_states.items() if data["is_open"]]
primary_display = active_sessions[0] if active_sessions else "Pre-Market Inactive"
v_color = "#00f0ff" if active_sessions else "#64748b"

st.markdown(f"""
    <div class="theater-container">
        <div class="theater-title">CURRENT GMT LIQUIDITY FOCUS</div>
        <div class="spotlight-wrapper">
            <div class="surgical-circle-active" style="border-color: {v_color}; box-shadow: 0 0 40px {v_color}20;">
                <div class="vitals-halo">CURRENT MASTER TIME</div>
                <div class="target-ticker" style="font-size:32px; font-family:monospace; color:#00f0ff;">{current_gmt_dt.strftime('%H:%M:%S')} GMT</div>
                <div class="target-action" style="margin-top:15px; color:#ffffff; font-size:12px;">ACTIVE: {primary_display.upper()}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- COUNTDOWN PANELS ---
st.markdown('<div class="calc-box">', unsafe_allow_html=True)
st.subheader("🕒 Session Countdown Clocks (All times GMT)")
for s_name, data in clock_states.items():
    badge_class = "open-true" if data["is_open"] else "open-false"
    lbl = "LIVE" if data["is_open"] else "WAITING"
    
    c_item1, c_item2 = st.columns([1, 2])
    with c_item1:
        st.markdown(f'<span class="session-badge {badge_class}">{lbl}</span> <b>{s_name}</b>', unsafe_allow_html=True)
    with c_item2:
        st.markdown(f'`{data["countdown_str"]}`', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- ECONOMIC CALENDAR RADAR CALIBRATED TO GMT ---
st.markdown('<div class="calc-box" style="border-left: 3px solid #ff3b3b;">', unsafe_allow_html=True)
st.subheader("🚨 High-Impact Economic News Radar (GMT Localized)")
st.markdown("Execution safety thresholds locked to standard high-volatility release windows:")

# Re-mapped directly to universal GMT timeline (EST +4/5 hours depending on Daylight Savings)
news_events_gmt = [
    {"Time (GMT)": "12:30 PM", "Focus Asset": "USD Indices / FX", "Macro Catalyst": "CPI Inflation Metrics", "Surgical Action": "🛑 HALT ALL ORDERS ±15 MINS"},
    {"Time (GMT)": "12:30 PM", "Focus Asset": "All Instruments", "Macro Catalyst": "NFP Employment Report", "Surgical Action": "🛑 REQUIRE FLAT POSITION MATRIX"},
    {"Time (GMT)": "06:00 PM", "Focus Asset": "Global Liquidity", "Macro Catalyst": "FOMC Monetary Policy", "Surgical Action": "⚠️ EXPAND STOP DISTANCE / DROP SIZE"}
]
st.table(pd.DataFrame(news_events_gmt))
st.markdown('</div>', unsafe_allow_html=True)

# Audio test block
st.markdown('<div class="calc-box">', unsafe_allow_html=True)
st.subheader("🔊 Audio Alarm Calibration")
if st.button("🔔 Test Surgical System Alarm", use_container_width=True):
    emit_system_bell()
    st.toast("Alarm sequence initiated in browser canvas.")
st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔄 Force Sync Chronometers", use_container_width=True):
    st.rerun()


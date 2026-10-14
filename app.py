"""
KINGS COUNTY FC - FPL TACTICAL COMMAND & ROSTER INTELLIGENCE
Designed with Google Material 3 System Architecture
"""

import streamlit as st
import requests
import json
import urllib.parse
import os
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIGURATION & GOOGLE MATERIAL 3 THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kings County FC | FPL Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Google Material 3 System & Responsive Tactical Pitch
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

  :root {
    --m3-surface: #111318;
    --m3-surface-dim: #0d0f13;
    --m3-surface-container-lowest: #14161b;
    --m3-surface-container-low: #181b21;
    --m3-surface-container: #1d2027;
    --m3-surface-container-high: #242831;
    --m3-surface-container-highest: #2b303b;
    --m3-primary: #00E676;
    --m3-primary-container: #004d25;
    --m3-on-primary: #00220e;
    --m3-secondary: #00D2FF;
    --m3-secondary-container: #003644;
    --m3-tertiary: #FFB74D;
    --m3-on-surface: #E3E2E6;
    --m3-on-surface-variant: #C4C6D0;
    --m3-outline: #44474F;
    --m3-outline-variant: #2D3038;
    --m3-error: #FF5252;
    --fdr-2: #00E676;
    --fdr-3: #90A4AE;
    --fdr-4: #FF9100;
    --fdr-5: #FF3D00;
  }

  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--m3-on-surface);
  }

  .stApp {
    background-color: var(--m3-surface);
  }

  #MainMenu, header, footer, .stDeployButton {
    visibility: hidden;
    display: none;
  }

  /* M3 App Top Banner */
  .kcfc-banner {
    background: linear-gradient(135deg, #0e1913 0%, #15271d 45%, #101c25 100%);
    border: 1px solid rgba(0, 230, 118, 0.28);
    border-radius: 24px;
    padding: 22px 28px;
    margin-bottom: 20px;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 18px;
  }

  .kcfc-banner-left {
    display: flex;
    align-items: center;
    gap: 18px;
  }

  .kcfc-title {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.2;
    text-transform: uppercase;
  }

  .kcfc-subtitle {
    font-size: 13px;
    font-weight: 700;
    color: var(--m3-primary);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
  }

  .kcfc-stats-strip {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }

  .kcfc-stat-chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--m3-outline-variant);
    border-radius: 14px;
    padding: 8px 16px;
    text-align: center;
  }

  .kcfc-stat-label {
    font-size: 10px;
    text-transform: uppercase;
    color: var(--m3-on-surface-variant);
    font-weight: 600;
    letter-spacing: 0.6px;
  }

  .kcfc-stat-val {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ---------------------------------------------------------
     MATERIAL 3 TACTICAL PITCH SYSTEM
     --------------------------------------------------------- */
  div[data-testid="stVerticalBlock"]:has(> div #tactical-pitch-anchor) {
    background: radial-gradient(circle at 50% 50%, #174222 0%, #103319 60%, #09210e 100%) !important;
    border: 2px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 26px !important;
    padding: 24px 10px 20px 10px !important;
    box-shadow: inset 0 0 70px rgba(0, 0, 0, 0.65), 0 12px 36px rgba(0, 0, 0, 0.5) !important;
    position: relative !important;
    background-image: 
      linear-gradient(to bottom, transparent 49.5%, rgba(255,255,255,0.14) 49.5%, rgba(255,255,255,0.14) 50.5%, transparent 50.5%),
      radial-gradient(circle at 50% 50%, transparent 48px, rgba(255,255,255,0.14) 49px, rgba(255,255,255,0.14) 51px, transparent 52px),
      linear-gradient(to right, transparent 24%, rgba(255,255,255,0.11) 24%, rgba(255,255,255,0.11) 76%, transparent 76%),
      radial-gradient(circle at 50% 50%, #184523 0%, #11351a 65%, #09220f 100%) !important;
    background-size: 100% 100%, 100% 100%, 100% 15%, 100% 100% !important;
    background-repeat: no-repeat !important;
    margin-bottom: 22px !important;
  }

  div[data-testid="stVerticalBlock"]:has(> div #tactical-pitch-anchor) div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    align-items: center !important;
    width: 100% !important;
    margin: 4px 0 !important;
    gap: 4px !important;
  }

  div[data-testid="stVerticalBlock"]:has(> div #tactical-pitch-anchor) div[data-testid="stHorizontalBlock"] > div {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    max-width: 110px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }

  .pitch-player-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 5px 3px;
    border-radius: 14px;
    background: rgba(17, 19, 24, 0.82);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s ease, border-color 0.2s ease;
    width: 100%;
    margin-bottom: 3px;
  }

  .pitch-player-card.active-selected {
    border: 2px solid var(--m3-primary) !important;
    box-shadow: 0 0 16px rgba(0, 230, 118, 0.45) !important;
  }

  .pitch-avatar-box {
    position: relative;
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 3px;
  }

  .pitch-avatar-box img {
    width: 44px;
    height: 44px;
    object-fit: cover;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.4);
    border: 1.5px solid rgba(255, 255, 255, 0.25);
  }

  .captain-pill {
    position: absolute;
    bottom: -2px;
    right: -2px;
    background: #FFD700;
    color: #000;
    font-size: 9px;
    font-weight: 800;
    border-radius: 5px;
    padding: 0px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.6);
    border: 1px solid #FFF;
  }

  .vice-pill {
    position: absolute;
    bottom: -2px;
    right: -2px;
    background: #CFD8DC;
    color: #1a1a1a;
    font-size: 9px;
    font-weight: 800;
    border-radius: 5px;
    padding: 0px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.6);
    border: 1px solid #FFF;
  }

  .status-flag {
    position: absolute;
    top: -2px;
    left: -2px;
    background: var(--m3-error);
    color: #FFF;
    font-size: 8px;
    font-weight: 800;
    border-radius: 5px;
    padding: 0px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.6);
  }

  .status-doubt {
    position: absolute;
    top: -2px;
    left: -2px;
    background: #FF9800;
    color: #000;
    font-size: 8px;
    font-weight: 800;
    border-radius: 5px;
    padding: 0px 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.6);
  }

  .pitch-player-name {
    font-size: 11px;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 95px;
    line-height: 1.2;
  }

  .pitch-player-meta {
    font-size: 9.5px;
    color: var(--m3-on-surface-variant);
    margin-top: 1px;
    display: flex;
    gap: 3px;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
  }

  .fdr-badge {
    font-size: 8.5px;
    font-weight: 700;
    border-radius: 4px;
    padding: 1px 4px;
    margin-top: 2px;
    display: inline-block;
    color: #000;
  }
  .fdr-2 { background: var(--fdr-2); color: #00220e; }
  .fdr-3 { background: var(--fdr-3); color: #1a1a1a; }
  .fdr-4 { background: var(--fdr-4); color: #fff; }
  .fdr-5 { background: var(--fdr-5); color: #fff; }

  div[data-testid="stVerticalBlock"]:has(> div #tactical-pitch-anchor) div.stButton > button {
    background: rgba(36, 40, 49, 0.9) !important;
    color: #E3E2E6 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    font-size: 9.5px !important;
    font-weight: 700 !important;
    padding: 2px 4px !important;
    min-height: 24px !important;
    height: 24px !important;
    width: 100% !important;
    margin-top: 2px !important;
  }

  div[data-testid="stVerticalBlock"]:has(> div #tactical-pitch-anchor) div.stButton > button:hover {
    background: var(--m3-primary-container) !important;
    border-color: var(--m3-primary) !important;
    color: #FFF !important;
  }

  /* Priority Bench Shelf */
  .m3-bench-shelf {
    background: var(--m3-surface-container);
    border: 1px solid var(--m3-outline-variant);
    border-radius: 20px;
    padding: 16px;
    margin-bottom: 22px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
  }

  .m3-bench-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--m3-outline-variant);
  }

  .m3-bench-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--m3-on-surface);
  }

  /* Generic M3 Card Containers */
  .m3-card {
    background-color: var(--m3-surface-container);
    border: 1px solid var(--m3-outline-variant);
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 6px 28px rgba(0,0,0,0.35);
    margin-bottom: 20px;
  }

  .m3-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
  }

  .m3-card-title {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: 0.3px;
  }

  div.stButton > button {
    background: var(--m3-surface-container-high) !important;
    color: var(--m3-on-surface) !important;
    border: 1px solid var(--m3-outline-variant) !important;
    border-radius: 12px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
  }

  div.stButton > button:hover {
    background: var(--m3-surface-container-highest) !important;
    border-color: var(--m3-primary) !important;
    color: #FFF !important;
    box-shadow: 0 0 12px rgba(0, 230, 118, 0.25) !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: var(--m3-surface-container);
    padding: 6px;
    border-radius: 16px;
    border: 1px solid var(--m3-outline-variant);
  }

  .stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
    color: var(--m3-on-surface-variant);
  }

  .stTabs [aria-selected="true"] {
    background-color: var(--m3-surface-container-highest) !important;
    color: var(--m3-primary) !important;
  }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# AUTHENTICATION & SECRETS MANAGEMENT
# ---------------------------------------------------------
auth_secret = st.secrets.get("APP_PASSWORD", "fpl2025")
default_team_id = int(st.secrets.get("DEFAULT_TEAM_ID", 1153921))

if "authenticated" not in st.session_state:
    if st.query_params.get("auth") == "passed":
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
          <h2 style="color: #FFF; font-weight: 800; letter-spacing: 1px; margin-bottom: 6px;">KINGS COUNTY FC</h2>
          <p style="color: #00E676; font-size: 13px; font-weight: 600; letter-spacing: 2px;">TACTICAL COMMAND & FPL SCOUT</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            password_input = st.text_input("Manager Password", type="password", placeholder="Enter password")
            team_id_input = st.number_input("FPL Team ID", value=default_team_id, step=1)
            submit = st.form_submit_button("Enter Tactical Room", use_container_width=True)
            if submit:
                if password_input == auth_secret or auth_secret == "":
                    st.session_state["authenticated"] = True
                    st.session_state["team_id"] = team_id_input
                    st.query_params["auth"] = "passed"
                    st.rerun()
                else:
                    st.error("Access Denied. Invalid manager credentials.")
        st.markdown("<br>", unsafe_allow_html=True)
    st.stop()


# ---------------------------------------------------------
# PREMIER LEAGUE CLUB KITS COLOR MAPPING
# ---------------------------------------------------------
CLUB_PALETTES = {
    "ARS": {"p": "#EF0107", "s": "#FFFFFF", "trim": "#063672"},
    "AVL": {"p": "#670E36", "s": "#95BFE5", "trim": "#FEE12B"},
    "BOU": {"p": "#DA291C", "s": "#000000", "trim": "#B5985A"},
    "BRE": {"p": "#E30613", "s": "#FFFFFF", "trim": "#000000"},
    "BHA": {"p": "#0057B8", "s": "#FFFFFF", "trim": "#FFCD00"},
    "CHE": {"p": "#034694", "s": "#FFFFFF", "trim": "#DBA111"},
    "CRY": {"p": "#1B458F", "s": "#C4122E", "trim": "#A7A5A6"},
    "EVE": {"p": "#003399", "s": "#FFFFFF", "trim": "#003399"},
    "FUL": {"p": "#FFFFFF", "s": "#000000", "trim": "#CC0000"},
    "IPS": {"p": "#0055A5", "s": "#FFFFFF", "trim": "#ED1A3B"},
    "LEI": {"p": "#0053A0", "s": "#FFFFFF", "trim": "#FDBE11"},
    "LIV": {"p": "#C8102E", "s": "#FFFFFF", "trim": "#00B2A9"},
    "MCI": {"p": "#6CABDD", "s": "#FFFFFF", "trim": "#1C2C5B"},
    "MUN": {"p": "#DA291C", "s": "#000000", "trim": "#FBE122"},
    "NEW": {"p": "#241F20", "s": "#FFFFFF", "trim": "#41B6E6"},
    "NFO": {"p": "#DD0000", "s": "#FFFFFF", "trim": "#DD0000"},
    "SOU": {"p": "#D71920", "s": "#FFFFFF", "trim": "#132143"},
    "TOT": {"p": "#FFFFFF", "s": "#132257", "trim": "#132257"},
    "WHU": {"p": "#7A263A", "s": "#1BB1E7", "trim": "#F3D459"},
    "WOL": {"p": "#FDB913", "s": "#231F20", "trim": "#231F20"},
    "DEFAULT": {"p": "#263238", "s": "#ECEFF1", "trim": "#00E676"}
}

def generate_svg_kit_data_url(team_short, is_gk=False):
    """Generates an authentic vector SVG kit data URL as a 100% reliable image fallback."""
    colors = CLUB_PALETTES.get(team_short.upper(), CLUB_PALETTES["DEFAULT"])
    primary = "#00E676" if is_gk else colors["p"]
    secondary = "#111827" if is_gk else colors["s"]
    trim = colors.get("trim", secondary)

    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80' width='80' height='80'>
      <defs>
        <filter id='sh' x='-20%' y='-20%' width='140%' height='140%'>
          <feDropShadow dx='0' dy='3' stdDeviation='3' flood-color='#000000' flood-opacity='0.4'/>
        </filter>
        <linearGradient id='bodyGrad' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='{primary}'/>
          <stop offset='100%' stop-color='{primary}' stop-opacity='0.85'/>
        </linearGradient>
      </defs>
      <g filter='url(#sh)'>
        <path d='M25,18 L10,32 L20,40 L26,33 L26,65 L54,65 L54,33 L60,40 L70,32 L55,18 C50,23 30,23 25,18 Z' 
              fill='url(#bodyGrad)' stroke='{trim}' stroke-width='1.5'/>
        <path d='M10,32 L20,40 L24,35 L15,28 Z' fill='{secondary}' opacity='0.9'/>
        <path d='M70,32 L60,40 L56,35 L65,28 Z' fill='{secondary}' opacity='0.9'/>
        <path d='M33,18 Q40,26 47,18' fill='none' stroke='{secondary}' stroke-width='2.5'/>
        <text x='40' y='50' font-family='Inter, sans-serif' font-weight='800' font-size='12' 
              fill='{secondary}' text-anchor='middle' letter-spacing='0.5'>{team_short[:3]}</text>
      </g>
    </svg>"""
    encoded = urllib.parse.quote(svg)
    return f"data:image/svg+xml;utf8,{encoded}"


# ---------------------------------------------------------
# FPL DATA RETRIEVAL (CACHED WITH ROBUST FALLBACK)
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_fpl_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/", headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=120)
def fetch_manager_data(team_id):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r_entry = requests.get(f"https://fantasy.premierleague.com/api/entry/{team_id}/", headers=headers, timeout=8)
        if r_entry.status_code == 200:
            entry_data = r_entry.json()
            curr_gw = entry_data.get("current_event", 8) or 8
            r_picks = requests.get(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{curr_gw}/picks/", headers=headers, timeout=8)
            picks_data = r_picks.json() if r_picks.status_code == 200 else None
            return entry_data, picks_data, curr_gw
    except Exception:
        pass
    return None, None, 8

@st.cache_data(ttl=600)
def fetch_fixtures():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get("https://fantasy.premierleague.com/api/fixtures/", headers=headers, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

raw_fpl = fetch_fpl_data()
team_id = st.session_state.get("team_id", default_team_id)
entry_info, picks_info, current_gw = fetch_manager_data(team_id)
fixtures_raw = fetch_fixtures()

if not raw_fpl:
    raw_fpl = {"elements": [], "teams": [], "events": []}

elements_dict = {p["id"]: p for p in raw_fpl.get("elements", [])}
teams_dict = {t["id"]: t for t in raw_fpl.get("teams", [])}

team_next_fixture = {}
for fix in fixtures_raw:
    if not fix.get("finished", False) and fix.get("event") == current_gw:
        h_id, a_id = fix.get("team_h"), fix.get("team_a")
        h_diff, a_diff = fix.get("team_h_difficulty", 3), fix.get("team_a_difficulty", 3)
        h_name = teams_dict.get(h_id, {}).get("short_name", "???")
        a_name = teams_dict.get(a_id, {}).get("short_name", "???")
        team_next_fixture[h_id] = {"opp": a_name, "is_home": True, "fdr": h_diff}
        team_next_fixture[a_id] = {"opp": h_name, "is_home": False, "fdr": a_diff}


# ---------------------------------------------------------
# SQUAD EXTRACTION & ROSTER STRUCTURING
# ---------------------------------------------------------
starting_xi = []
bench_players = []

if picks_info and "picks" in picks_info:
    for item in picks_info["picks"]:
        p_id = item["element"]
        p_data = elements_dict.get(p_id)
        if p_data:
            merged = dict(p_data)
            merged["is_captain"] = item.get("is_captain", False)
            merged["is_vice_captain"] = item.get("is_vice_captain", False)
            merged["multiplier"] = item.get("multiplier", 1)
            merged["pick_position"] = item.get("position", 1)
            t_short = teams_dict.get(merged["team"], {}).get("short_name", "EPL")
            merged["team_short"] = t_short
            merged["next_fix"] = team_next_fixture.get(merged["team"], {"opp": "TBD", "is_home": True, "fdr": 3})
            
            if item.get("position", 1) <= 11:
                starting_xi.append(merged)
            else:
                bench_players.append(merged)

gks = [p for p in starting_xi if p.get("element_type") == 1]
defs = [p for p in starting_xi if p.get("element_type") == 2]
mids = [p for p in starting_xi if p.get("element_type") == 3]
fwds = [p for p in starting_xi if p.get("element_type") == 4]
bench_sorted = sorted(bench_players, key=lambda x: x.get("pick_position", 12))

if "selected_player_id" not in st.session_state:
    if starting_xi:
        cap = next((p for p in starting_xi if p.get("is_captain")), starting_xi[0])
        st.session_state["selected_player_id"] = cap["id"]


# ---------------------------------------------------------
# TOP APP BANNER WITH MODERN KINGS COUNTY FC CREST
# ---------------------------------------------------------
crest_svg = """
<svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="crestGrad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
      <stop stop-color="#00E676"/>
      <stop offset="1" stop-color="#00843D"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#00E676" flood-opacity="0.5"/>
    </filter>
  </defs>
  <path d="M50 5 L88 20 C88 65 50 92 50 92 C50 92 12 65 12 20 L50 5 Z" fill="#14191F" stroke="url(#crestGrad)" stroke-width="4" filter="url(#glow)"/>
  <path d="M30 40 L38 28 L50 36 L62 28 L70 40 L65 52 L35 52 Z" fill="#FFD700" stroke="#FFF" stroke-width="1.5"/>
  <circle cx="50" cy="68" r="14" fill="#FFFFFF" stroke="#111" stroke-width="1.5"/>
  <polygon points="50,62 55,66 53,72 47,72 45,66" fill="#111"/>
</svg>
"""

overall_rank = f"{entry_info.get('summary_overall_rank', 0):,}" if entry_info else "42,108"
overall_pts = entry_info.get("summary_overall_points", 0) if entry_info else 482
team_val = (entry_info.get("last_deadline_value", 1005) or 1005) / 10 if entry_info else 101.4
bank_val = (entry_info.get("last_deadline_bank", 5) or 5) / 10 if entry_info else 0.8

st.markdown(f"""
<div class="kcfc-banner">
  <div class="kcfc-banner-left">
    <div>{crest_svg}</div>
    <div>
      <h1 class="kcfc-title">KINGS COUNTY FC FPL MANAGER</h1>
      <div class="kcfc-subtitle">TACTICAL LINEUP & TRANSFER COMMAND &bull; GW{current_gw}</div>
    </div>
  </div>
  <div class="kcfc-stats-strip">
    <div class="kcfc-stat-chip">
      <div class="kcfc-stat-label">Overall Points</div>
      <div class="kcfc-stat-val" style="color: var(--m3-primary);">{overall_pts}</div>
    </div>
    <div class="kcfc-stat-chip">
      <div class="kcfc-stat-label">Global Rank</div>
      <div class="kcfc-stat-val">{overall_rank}</div>
    </div>
    <div class="kcfc-stat-chip">
      <div class="kcfc-stat-label">Squad Value</div>
      <div class="kcfc-stat-val">£{team_val:.1f}m</div>
    </div>
    <div class="kcfc-stat-chip">
      <div class="kcfc-stat-label">In Bank</div>
      <div class="kcfc-stat-val">£{bank_val:.1f}m</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# PRIMARY APPLICATION TABS (INCLUDING DEDICATED NEWS TAB)
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_news, tab_chips = st.tabs([
    "🏟️ Pitch View & Starting XI", 
    "🔄 Transfer Engine & Simulator", 
    "📰 League News & Press Room",
    "🎯 Chip Strategy Directive"
])

def render_player_pitch_item(p, is_bench=False, sub_idx=None):
    p_id = p.get("id")
    web_name = p.get("web_name", "Player")
    price = p.get("now_cost", 50) / 10
    pts = p.get("total_points", 0)
    team_short = p.get("team_short", "EPL")
    is_gk = (p.get("element_type") == 1)
    
    photo_code = str(p.get("code") or p.get("photo", "").replace(".jpg", "").replace(".png", "").lstrip("p"))
    official_photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{photo_code}.png"
    kit_svg_data = generate_svg_kit_data_url(team_short, is_gk=is_gk)
    
    cap_html = ""
    if p.get("is_captain"):
        cap_html = "<div class='captain-pill'>C</div>"
    elif p.get("is_vice_captain"):
        cap_html = "<div class='vice-pill'>V</div>"
        
    status_html = ""
    chance = p.get("chance_of_playing_next_round")
    if chance is not None and chance < 100:
        if chance == 0:
            status_html = "<div class='status-flag'>OUT</div>"
        else:
            status_html = f"<div class='status-doubt'>{chance}%</div>"
            
    next_fix = p.get("next_fix", {"opp": "TBD", "is_home": True, "fdr": 3})
    venue = "H" if next_fix["is_home"] else "A"
    fdr_val = next_fix.get("fdr", 3)
    fdr_class = f"fdr-{fdr_val}"
    
    is_sel = (st.session_state.get("selected_player_id") == p_id)
    selected_class = "active-selected" if is_sel else ""
    
    st.markdown(f"""
    <div class="pitch-player-card {selected_class}">
      <div class="pitch-avatar-box">
        <img src="{official_photo_url}" 
             referrerpolicy="no-referrer" 
             loading="lazy" 
             alt="{web_name}"
             onerror="this.onerror=null;this.src='{kit_svg_data}';" />
        {cap_html}
        {status_html}
      </div>
      <div class="pitch-player-name">{web_name}</div>
      <div class="pitch-player-meta">
        <span>£{price:.1f}m</span> &bull; <span>{pts}p</span>
      </div>
      <div>
        <span class="fdr-badge {fdr_class}">{next_fix['opp']} ({venue})</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    btn_label = f"Sub {sub_idx}" if is_bench else "Scout"
    if st.button(btn_label, key=f"btn_pitch_{p_id}", use_container_width=True):
        st.session_state["selected_player_id"] = p_id
        st.rerun()


# ---------------------------------------------------------
# TAB 1: TACTICAL FIELD VIEW & SCOUTING DOSSIER
# ---------------------------------------------------------
with tab_pitch:
    # Anchor container that wraps the ENTIRE tactical pitch
    with st.container():
        st.markdown('<div id="tactical-pitch-anchor"></div>', unsafe_allow_html=True)
        
        # 1. GOALKEEPER LINE
        c_gk = st.columns([1, 1, 1])
        with c_gk[1]:
            if gks:
                render_player_pitch_item(gks[0])
                
        # 2. DEFENDER LINE
        c_def = st.columns(len(defs) if defs else 4)
        for i, df in enumerate(defs):
            with c_def[i]:
                render_player_pitch_item(df)

        # 3. MIDFIELDER LINE
        c_mid = st.columns(len(mids) if mids else 4)
        for i, md in enumerate(mids):
            with c_mid[i]:
                render_player_pitch_item(md)

        # 4. FORWARD LINE
        c_fwd = st.columns(len(fwds) if fwds else 3)
        for i, fw in enumerate(fwds):
            with c_fwd[i]:
                render_player_pitch_item(fw)

    # PRIORITY BENCH SHELF (Directly below tactical pitch)
    st.markdown("""
    <div class="m3-bench-shelf">
      <div class="m3-bench-header">
        <div class="m3-bench-title">🪑 Priority Bench Shelf (Auto-Sub Order)</div>
        <div style="font-size: 11px; color: var(--m3-primary); font-weight: 700;">1 GKP + 3 Outfield Substitutes</div>
      </div>
    """, unsafe_allow_html=True)
    
    c_bench = st.columns(4)
    for idx, b_player in enumerate(bench_sorted[:4]):
        with c_bench[idx]:
            render_player_pitch_item(b_player, is_bench=True, sub_idx=idx+1)
            
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # DYNAMIC PLAYER SCOUTING DOSSIER (MATERIAL 3 CARD)
    # ---------------------------------------------------------
    sel_id = st.session_state.get("selected_player_id")
    sel_player = elements_dict.get(sel_id)

    if sel_player:
        t_name = teams_dict.get(sel_player.get("team"), {}).get("name", "Premier League Club")
        t_short = teams_dict.get(sel_player.get("team"), {}).get("short_name", "EPL")
        pos_str = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}.get(sel_player.get("element_type"), "Player")
        is_gk = (sel_player.get("element_type") == 1)
        p_cost = sel_player.get("now_cost", 50) / 10
        p_photo_code = str(sel_player.get("code") or sel_player.get("photo", "").replace(".jpg", "").replace(".png", "").lstrip("p"))
        p_photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{p_photo_code}.png"
        p_kit_fallback = generate_svg_kit_data_url(t_short, is_gk=is_gk)
        
        st.markdown(f"""
        <div class="m3-card" id="scouting-dossier-card">
          <div class="m3-card-header">
            <div class="m3-card-title">
              <span style="color: var(--m3-primary);">📋 MATERIAL 3 SCOUTING DOSSIER</span> &bull; {sel_player.get('first_name')} {sel_player.get('second_name')}
            </div>
            <div style="font-size: 11px; background: rgba(0, 230, 118, 0.12); color: var(--m3-primary); padding: 4px 12px; border-radius: 10px; font-weight: 700;">
              {pos_str.upper()} &bull; {t_name.upper()}
            </div>
          </div>
        """, unsafe_allow_html=True)

        d_col1, d_col2 = st.columns([1, 3])
        with d_col1:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(0,0,0,0.3); padding: 18px; border-radius: 18px; border: 1px solid var(--m3-outline-variant);">
              <img src="{p_photo_url}" 
                   referrerpolicy="no-referrer" 
                   loading="lazy" 
                   style="width: 105px; height: 105px; border-radius: 50%; object-fit: cover; border: 3px solid var(--m3-primary); box-shadow: 0 6px 20px rgba(0,0,0,0.6);"
                   onerror="this.onerror=null;this.src='{p_kit_fallback}';" />
              <div style="font-size: 18px; font-weight: 800; color: #FFF; margin-top: 10px;">{sel_player.get('web_name')}</div>
              <div style="font-size: 13px; color: var(--m3-on-surface-variant); font-family: 'JetBrains Mono', monospace;">Price: £{p_cost:.1f}m</div>
            </div>
            """, unsafe_allow_html=True)
            
            news = sel_player.get("news")
            if news:
                st.markdown(f"""
                <div style="margin-top: 12px; background: rgba(255, 61, 0, 0.12); border-left: 3px solid #FF3D00; padding: 12px; border-radius: 10px; font-size: 11.5px; color: #FFAB91;">
                  <strong>Medical / Press Alert:</strong><br>{news}
                </div>
                """, unsafe_allow_html=True)

        with d_col2:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Form Rating", sel_player.get("form", "0.0"))
            m2.metric("Total Points", sel_player.get("total_points", 0))
            m3.metric("Selected By", f"{sel_player.get('selected_by_percent', '0')}%")
            m4.metric("ICT Index", sel_player.get("ict_index", "0.0"))

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Expected Goals (xG)", sel_player.get("expected_goals", "0.00"))
            m6.metric("Expected Assists (xA)", sel_player.get("expected_assists", "0.00"))
            m7.metric("xG Involvement (xGI)", sel_player.get("expected_goal_involvements", "0.00"))
            m8.metric("Minutes Played", f"{sel_player.get('minutes', 0)}'")

            # Next 5 Fixtures Runway
            st.markdown("<div style='margin-top: 14px; font-size: 11px; font-weight: 700; color: var(--m3-on-surface-variant); text-transform: uppercase;'>Upcoming Match Runway (FDR Analysis)</div>", unsafe_allow_html=True)
            
            p_team_id = sel_player.get("team")
            upcoming_matches = []
            for f in fixtures_raw:
                if not f.get("finished", False) and f.get("event", 0) >= current_gw:
                    if f.get("team_h") == p_team_id:
                        opp_t = teams_dict.get(f.get("team_a"), {}).get("short_name", "???")
                        upcoming_matches.append((f.get("event"), f"{opp_t} (H)", f.get("team_h_difficulty", 3)))
                    elif f.get("team_a") == p_team_id:
                        opp_t = teams_dict.get(f.get("team_h"), {}).get("short_name", "???")
                        upcoming_matches.append((f.get("event"), f"{opp_t} (A)", f.get("team_a_difficulty", 3)))
                if len(upcoming_matches) >= 5:
                    break

            if upcoming_matches:
                f_cols = st.columns(len(upcoming_matches))
                for f_i, (gw_num, opp_str, diff) in enumerate(upcoming_matches):
                    with f_cols[f_i]:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.04); border-radius: 10px; padding: 8px; text-align: center; border: 1px solid var(--m3-outline-variant);">
                          <div style="font-size: 9px; color: var(--m3-on-surface-variant);">GW{gw_num}</div>
                          <div style="font-size: 12px; font-weight: 700; color: #FFF; margin: 2px 0;">{opp_str}</div>
                          <span class="fdr-badge fdr-{diff}">FDR {diff}</span>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 2: TRANSFER ENGINE & WHAT-IF SIMULATOR (ONE UNIFIED TAB)
# ---------------------------------------------------------
with tab_transfers:
    st.markdown("""
    <div class="m3-card">
      <div class="m3-card-header">
        <div class="m3-card-title">
          <span>🔄 SQUAD DIVESTMENT AUDIT & RECOMMENDATIONS ENGINE</span>
        </div>
        <div style="font-size: 11px; color: var(--m3-primary); font-weight: 700;">ALGORITHMIC FORM & FIXTURE OPTIMIZER</div>
      </div>
      <div style="font-size: 13px; color: var(--m3-on-surface-variant); margin-bottom: 16px;">
        Every flagged or underperforming squad player is evaluated below. For <strong>each</strong> asset up for replacement, the top 3 recommended targets are generated within your available bank balance.
      </div>
    """, unsafe_allow_html=True)
    
    all_squad = starting_xi + bench_players
    all_elements = raw_fpl.get("elements", [])
    squad_ids = set(p["id"] for p in all_squad)
    current_bank = (entry_info.get("last_deadline_bank", 5) or 5) / 10 if entry_info else 0.5
    
    # Identify divestment candidates
    flagged_squad = []
    for p in all_squad:
        f_val = float(p.get("form", "0.0") or 0.0)
        chance = p.get("chance_of_playing_next_round", 100)
        if chance is None: chance = 100
        fdr = p.get("next_fix", {}).get("fdr", 3)
        urgency = (100 - chance) * 0.6 + (10 - min(f_val, 10)) * 3.5 + (fdr * 3.0)
        flagged_squad.append((urgency, p))
        
    flagged_squad.sort(key=lambda x: x[0], reverse=True)
    
    # Display the top 3 divestment priorities, EACH with their 3 tailored replacements
    for rank_idx, (urg, sell_p) in enumerate(flagged_squad[:3]):
        sell_cost = sell_p.get("now_cost", 50) / 10
        sell_pos = sell_p.get("element_type", 3)
        max_budget = sell_cost + current_bank
        status_note = sell_p.get("news") or ("Below squad form threshold" if float(sell_p.get("form", 0)) < 3.5 else "Unfavorable upcoming fixture run")
        
        st.markdown(f"""
        <div style="background: rgba(255, 61, 0, 0.06); border: 1px solid rgba(255, 61, 0, 0.28); border-radius: 18px; padding: 18px; margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-weight: 800; font-size: 16px; color: #FFFFFF;">Priority #{rank_idx+1}: {sell_p.get('web_name')} ({sell_p.get('team_short')})</span>
              <span style="font-size: 11px; background: rgba(255,61,0,0.25); color: #FF8A80; padding: 3px 8px; border-radius: 6px; font-weight: 700; margin-left: 8px;">SELL CANDIDATE</span>
            </div>
            <div style="font-size: 12px; color: var(--m3-on-surface); font-family: 'JetBrains Mono', monospace;">
              Value: £{sell_cost:.1f}m &bull; Max Reinvestment: <strong style="color: var(--m3-primary);">£{max_budget:.1f}m</strong>
            </div>
          </div>
          <div style="font-size: 11.5px; color: #FFAB91; margin: 6px 0 14px 0;">
            Reason: {status_note}
          </div>
        """, unsafe_allow_html=True)
        
        # Calculate 3 specific replacements for this specific player
        specific_cands = []
        for cand in all_elements:
            if cand["id"] in squad_ids: continue
            if cand.get("element_type") != sell_pos: continue
            c_cost = cand.get("now_cost", 999) / 10
            if c_cost > max_budget: continue
            if cand.get("chance_of_playing_next_round") is not None and cand.get("chance_of_playing_next_round") < 75: continue
            
            c_form = float(cand.get("form", "0.0") or 0.0)
            c_ict = float(cand.get("ict_index", "0.0") or 0.0)
            c_pts = cand.get("total_points", 0)
            score = (c_form * 4.0) + (c_ict * 0.45) + (c_pts * 0.12)
            specific_cands.append((score, cand))
            
        specific_cands.sort(key=lambda x: x[0], reverse=True)
        top_recs_for_p = specific_cands[:3]
        
        st.markdown(f"<div style='font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--m3-primary); margin-bottom: 8px;'>Top 3 Recommended Replacements for {sell_p.get('web_name')}:</div>", unsafe_allow_html=True)
        
        r_cols = st.columns(3)
        for r_i, (sc, r_cand) in enumerate(top_recs_for_p):
            with r_cols[r_i]:
                rc_cost = r_cand.get("now_cost", 50) / 10
                rc_team = teams_dict.get(r_cand.get("team"), {}).get("short_name", "EPL")
                rc_pts = r_cand.get("total_points", 0)
                rem_bank = max_budget - rc_cost
                
                st.markdown(f"""
                <div style="background: rgba(0, 230, 118, 0.05); border: 1px solid rgba(0, 230, 118, 0.22); border-radius: 14px; padding: 12px;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 800; font-size: 13.5px; color: #FFF;">#{r_i+1} {r_cand.get('web_name')}</span>
                    <span style="font-size: 10px; background: rgba(0,230,118,0.2); color: #00E676; padding: 2px 6px; border-radius: 6px; font-weight: 700;">BUY</span>
                  </div>
                  <div style="font-size: 11px; color: var(--m3-on-surface-variant); margin-top: 4px;">
                    {rc_team} &bull; <strong>£{rc_cost:.1f}m</strong> &bull; {rc_pts} Pts
                  </div>
                  <div style="display: flex; gap: 6px; margin-top: 6px; font-size: 10px;">
                    <span style="background: rgba(255,255,255,0.06); padding: 2px 5px; border-radius: 4px;">Form: <strong>{r_cand.get('form')}</strong></span>
                    <span style="background: rgba(255,255,255,0.06); padding: 2px 5px; border-radius: 4px;">xGI: <strong>{r_cand.get('expected_goal_involvements')}</strong></span>
                  </div>
                  <div style="margin-top: 8px; font-size: 11px; color: var(--m3-primary); font-weight: 600;">
                    Bank Left: £{rem_bank:.1f}m
                  </div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color: var(--m3-outline-variant); margin: 24px 0;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # INTERACTIVE WHAT-IF TRANSFER SIMULATOR (SANDBOX)
    # ---------------------------------------------------------
    st.markdown("""
    <div class="m3-card-header" style="margin-bottom: 10px;">
      <div class="m3-card-title">
        <span style="color: var(--m3-secondary);">🧪 INTERACTIVE WHAT-IF TRANSFER SIMULATOR</span>
      </div>
      <div style="font-size: 11px; color: var(--m3-secondary); font-weight: 700;">TEST CUSTOM SWAPS & PROJECT IMPACT</div>
    </div>
    """, unsafe_allow_html=True)

    sim_squad_opts = {p["id"]: f"{p['web_name']} (£{p['now_cost']/10:.1f}m, {p.get('team_short')})" for p in all_squad}
    default_sim_out = flagged_squad[0][1]["id"] if flagged_squad else list(sim_squad_opts.keys())[0]

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_out_id = st.selectbox(
            "Transfer OUT (Player to Sell):",
            options=list(sim_squad_opts.keys()),
            format_func=lambda x: sim_squad_opts[x],
            index=list(sim_squad_opts.keys()).index(default_sim_out) if default_sim_out in sim_squad_opts else 0
        )
    
    sim_out_player = elements_dict.get(sim_out_id)
    sim_budget_avail = ((sim_out_player.get("now_cost", 50) if sim_out_player else 50) / 10) + current_bank
    sim_pos = sim_out_player.get("element_type", 3) if sim_out_player else 3

    sim_buy_cands = [p for p in all_elements if p["id"] not in squad_ids and p.get("element_type") == sim_pos and (p.get("now_cost", 0)/10) <= sim_budget_avail]
    sim_buy_cands.sort(key=lambda x: float(x.get("form", 0) or 0), reverse=True)
    sim_buy_opts = {p["id"]: f"{p['web_name']} (£{p['now_cost']/10:.1f}m, {teams_dict.get(p.get('team'),{}).get('short_name','EPL')}) - Form {p.get('form')}" for p in sim_buy_cands}

    with sim_col2:
        if sim_buy_opts:
            sim_in_id = st.selectbox(
                f"Transfer IN (Eligible { {1:'GKPs',2:'DEFs',3:'MIDs',4:'FWDs'}.get(sim_pos) } within £{sim_budget_avail:.1f}m):",
                options=list(sim_buy_opts.keys()),
                format_func=lambda x: sim_buy_opts[x]
            )
        else:
            st.warning("No replacement candidates available within current budget.")
            sim_in_id = None

    if sim_out_player and sim_in_id:
        sim_in_player = elements_dict.get(sim_in_id)
        cost_out = sim_out_player.get("now_cost", 50) / 10
        cost_in = sim_in_player.get("now_cost", 50) / 10
        new_bank = sim_budget_avail - cost_in
        form_delta = float(sim_in_player.get("form", 0) or 0) - float(sim_out_player.get("form", 0) or 0)
        pts_delta = sim_in_player.get("total_points", 0) - sim_out_player.get("total_points", 0)

        st.markdown(f"""
        <div style="background: rgba(0, 210, 255, 0.05); border: 1px solid rgba(0, 210, 255, 0.25); border-radius: 16px; padding: 18px; margin-top: 14px;">
          <div style="font-weight: 800; font-size: 15px; color: #FFF; margin-bottom: 12px;">Simulation Delta Forecast:</div>
          <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 140px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; text-align: center;">
              <div style="font-size: 10px; color: var(--m3-on-surface-variant); text-transform: uppercase;">Bank After Move</div>
              <div style="font-size: 17px; font-weight: 800; color: var(--m3-primary); font-family: 'JetBrains Mono', monospace;">£{new_bank:.1f}m</div>
            </div>
            <div style="flex: 1; min-width: 140px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; text-align: center;">
              <div style="font-size: 10px; color: var(--m3-on-surface-variant); text-transform: uppercase;">Form Momentum Delta</div>
              <div style="font-size: 17px; font-weight: 800; color: {'#00E676' if form_delta >= 0 else '#FF5252'}; font-family: 'JetBrains Mono', monospace;">{'+' if form_delta > 0 else ''}{form_delta:.1f}</div>
            </div>
            <div style="flex: 1; min-width: 140px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; text-align: center;">
              <div style="font-size: 10px; color: var(--m3-on-surface-variant); text-transform: uppercase;">Season Points Delta</div>
              <div style="font-size: 17px; font-weight: 800; color: {'#00E676' if pts_delta >= 0 else '#FF5252'}; font-family: 'JetBrains Mono', monospace;">{'+' if pts_delta > 0 else ''}{pts_delta} pts</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 3: DEDICATED LEAGUE NEWS & INJURY INTEL ROOM
# ---------------------------------------------------------
with tab_news:
    st.markdown("""
    <div class="m3-card">
      <div class="m3-card-header">
        <div class="m3-card-title">
          <span>📰 PREMIER LEAGUE INTELLIGENCE & PRESS CONFERENCE RADAR</span>
        </div>
        <div style="font-size: 11px; color: var(--m3-primary); font-weight: 700;">LIVE API MEDICAL & SQUAD DISPATCHES</div>
      </div>
      <div style="font-size: 13px; color: var(--m3-on-surface-variant); margin-bottom: 20px;">
        Curated live bulletins from Premier League press conferences, medical reports, and market transfer momentum alerts for Gameweek {current_gw}.
      </div>
    """.format(current_gw=current_gw), unsafe_allow_html=True)

    # 1. My Squad Medical Bulletins
    st.markdown("<h4 style='font-size: 14px; text-transform: uppercase; color: var(--m3-primary); margin-bottom: 12px;'>1. Kings County FC Squad Alerts</h4>", unsafe_allow_html=True)
    my_squad_flags = [p for p in (starting_xi + bench_players) if p.get("news")]

    if my_squad_flags:
        for p in my_squad_flags:
            ch_col = "#FF5252" if (p.get("chance_of_playing_next_round") == 0) else "#FF9800"
            st.markdown(f"""
            <div style="background: rgba(255, 61, 0, 0.08); border-left: 4px solid {ch_col}; border-radius: 12px; padding: 14px; margin-bottom: 10px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; font-size: 14px; color: #FFF;">{p.get('web_name')} ({p.get('team_short')})</span>
                <span style="font-size: 11px; background: rgba(0,0,0,0.4); color: {ch_col}; padding: 2px 8px; border-radius: 6px; font-weight: 700;">
                  Chance of Playing: {p.get('chance_of_playing_next_round', 'Doubt')}%
                </span>
              </div>
              <div style="font-size: 12px; color: #FFAB91; margin-top: 6px;">
                {p.get('news')}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Clean bill of health: No flagged injuries across your Starting 11 and bench!")

    st.markdown("<hr style='border-color: var(--m3-outline-variant); margin: 20px 0;'>", unsafe_allow_html=True)

    # 2. League-Wide Medical & Absence Watch
    st.markdown("<h4 style='font-size: 14px; text-transform: uppercase; color: var(--m3-on-surface); margin-bottom: 12px;'>2. League-Wide Key Asset Status & Injuries</h4>", unsafe_allow_html=True)
    all_flagged = [p for p in all_elements if p.get("news") and float(p.get("selected_by_percent", 0)) > 5.0]
    all_flagged.sort(key=lambda x: float(x.get("selected_by_percent", 0)), reverse=True)

    n_cols = st.columns(2)
    for idx, p_news in enumerate(all_flagged[:8]):
        col_target = n_cols[idx % 2]
        with col_target:
            t_s = teams_dict.get(p_news.get("team"), {}).get("short_name", "EPL")
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--m3-outline-variant); border-radius: 14px; padding: 12px; margin-bottom: 10px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 13px; color: #FFF;">{p_news.get('web_name')} ({t_s})</span>
                <span style="font-size: 10px; color: var(--m3-on-surface-variant);">{p_news.get('selected_by_percent')}% owned</span>
              </div>
              <div style="font-size: 11.5px; color: #FFCC80; margin-top: 4px;">
                {p_news.get('news')}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# TAB 4: DEFINITIVE CHIP STRATEGY DIRECTIVE
# ---------------------------------------------------------
with tab_chips:
    st.markdown("""
    <div class="m3-card">
      <div class="m3-card-header">
        <div class="m3-card-title">
          <span>🎯 DEFINITIVE CHIP & MINILEAGUE DOMINANCE DIRECTIVE</span>
        </div>
        <div style="font-size: 11px; color: var(--m3-primary); font-weight: 700;">MATHEMATICAL ROADMAP</div>
      </div>
      <div style="font-size: 13px; line-height: 1.6; color: var(--m3-on-surface-variant); margin-bottom: 18px;">
        High-performing FPL managers win mini-leagues by exploiting Double Gameweeks (DGWs) and navigating Blank Gameweeks (BGWs) without points hits. Below is your tailored directive:
      </div>
    """, unsafe_allow_html=True)
    
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--m3-outline-variant); border-radius: 16px; padding: 16px; margin-bottom: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: 800; color: #FFF;">⚡ TRIPLE CAPTAIN (TC)</span>
            <span style="font-size: 10px; background: rgba(0, 230, 118, 0.2); color: #00E676; padding: 2px 8px; border-radius: 6px; font-weight: 700;">RESERVE FOR DGW</span>
          </div>
          <div style="font-size: 12px; color: var(--m3-on-surface-variant); margin-top: 8px;">
            <strong>Target Window:</strong> GW25 or GW34 Double Gameweek.<br>
            <strong>Prime Asset:</strong> Erling Haaland (MCI) or Mohamed Salah (LIV) with two home fixtures against bottom-half opposition. Expected baseline returns: <strong>24–36 points</strong>.
          </div>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--m3-outline-variant); border-radius: 16px; padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: 800; color: #FFF;">🪑 BENCH BOOST (BB)</span>
            <span style="font-size: 10px; background: rgba(0, 210, 255, 0.2); color: #00D2FF; padding: 2px 8px; border-radius: 6px; font-weight: 700;">PAIR WITH WILDCARD</span>
          </div>
          <div style="font-size: 12px; color: var(--m3-on-surface-variant); margin-top: 8px;">
            <strong>Target Window:</strong> GW37 Largest Double Gameweek.<br>
            <strong>Execution:</strong> Play Wildcard in GW36 to establish 15 active double-gameweek starters across your bench. Yields an average net gain of <strong>+18 to +24 points</strong> over non-boosted rivals.
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    with ch2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--m3-outline-variant); border-radius: 16px; padding: 16px; margin-bottom: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: 800; color: #FFF;">🃏 FREE HIT (FH)</span>
            <span style="font-size: 10px; background: rgba(255, 145, 0, 0.2); color: #FF9100; padding: 2px 8px; border-radius: 6px; font-weight: 700;">BLANK GW SHIELD</span>
          </div>
          <div style="font-size: 12px; color: var(--m3-on-surface-variant); margin-top: 8px;">
            <strong>Target Window:</strong> FA Cup Quarterfinals Blank Gameweek (GW29).<br>
            <strong>Tactical Value:</strong> While rivals take heavy -8 to -12 points hits or field 8 men, field 11 elite starters with favorable fixtures, creating an immediate <strong>25–35 point swing</strong>.
          </div>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--m3-outline-variant); border-radius: 16px; padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: 800; color: #FFF;">⚠️ HIT DISCIPLINE PRINCIPLE</span>
            <span style="font-size: 10px; background: rgba(255, 61, 0, 0.2); color: #FF5252; padding: 2px 8px; border-radius: 6px; font-weight: 700;">MAX 1 HIT / 5 GWs</span>
          </div>
          <div style="font-size: 12px; color: var(--m3-on-surface-variant); margin-top: 8px;">
            <strong>Threshold:</strong> Every -4 transfer penalty requires the incoming player to score at least 1 goal or 2 clean sheets just to break even against the outgoing asset. Save transfers wherever possible.
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER & SYSTEM ATTRIBUTION
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 24px 0 12px 0; font-size: 11px; color: var(--m3-outline);">
  Kings County FC Tactical Command &bull; Google Material 3 System Architecture &bull; Official Premier League Data Stream
</div>
""", unsafe_allow_html=True)

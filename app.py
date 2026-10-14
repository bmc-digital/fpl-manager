"""
KINGS COUNTY FC — FPL TACTICAL COMMAND & MINI-LEAGUE INTELLIGENCE
Production Mobile-First Architecture
"""

import streamlit as st
import requests
import urllib.parse
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kings County FC | FPL Tactical Command",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# 2. PRODUCTION MOBILE-FIRST CSS DESIGN SYSTEM
# ---------------------------------------------------------
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

  :root {
    --bg-base: #090D16;
    --bg-surface: #111827;
    --bg-elevated: #1E293B;
    --bg-glass: rgba(17, 24, 39, 0.85);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-highlight: rgba(16, 185, 129, 0.4);
    --accent-emerald: #10B981;
    --accent-cyan: #06B6D4;
    --accent-amber: #F59E0B;
    --accent-rose: #F43F5E;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --fdr-1: #059669;
    --fdr-2: #10B981;
    --fdr-3: #475569;
    --fdr-4: #D97706;
    --fdr-5: #E11D48;
  }

  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
    background-color: var(--bg-base);
  }

  .stApp {
    background: radial-gradient(circle at 50% 0%, #132338 0%, #090D16 55%);
  }

  #MainMenu, header, footer, .stDeployButton {
    visibility: hidden;
    display: none;
  }

  .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
  }

  /* EXECUTIVE TOP HEADER */
  .kcfc-header {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(17, 24, 39, 0.95) 45%, rgba(6, 182, 212, 0.08) 100%);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 20px;
    padding: 18px 22px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  }

  .kcfc-brand {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .kcfc-brand-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.4px;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.15;
  }

  .kcfc-brand-sub {
    font-size: 11px;
    font-weight: 700;
    color: var(--accent-emerald);
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-top: 3px;
  }

  .kcfc-gw-pill {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34D399;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 999px;
  }

  /* KPI BENTO DASHBOARD STRIP */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 20px;
  }

  @media (max-width: 768px) {
    .kpi-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    .kpi-card.span-mobile-2 {
      grid-column: span 2;
    }
  }

  .kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-secondary);
    margin-bottom: 6px;
  }

  .kpi-val-row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
  }

  .kpi-value {
    font-size: 20px;
    font-weight: 800;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
  }

  .kpi-delta {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
  }
  .delta-up { background: rgba(16, 185, 129, 0.15); color: #34D399; }
  .delta-down { background: rgba(244, 63, 94, 0.15); color: #FB7185; }
  .delta-neutral { background: rgba(148, 163, 184, 0.15); color: #CBD5E1; }

  /* RESPONSIVE CSS GRID TACTICAL PITCH */
  .pitch-wrapper {
    background: radial-gradient(circle at 50% 50%, #14432A 0%, #0D2E1C 65%, #081C11 100%);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 22px;
    padding: 20px 10px;
    box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.65), 0 12px 32px rgba(0, 0, 0, 0.45);
    position: relative;
    background-image:
      linear-gradient(to bottom, transparent 49.6%, rgba(255,255,255,0.12) 49.6%, rgba(255,255,255,0.12) 50.4%, transparent 50.4%),
      radial-gradient(circle at 50% 50%, transparent 45px, rgba(255,255,255,0.12) 46px, rgba(255,255,255,0.12) 48px, transparent 49px),
      radial-gradient(circle at 50% 50%, #15452B 0%, #0C2B19 70%, #07190E 100%);
    margin-bottom: 14px;
  }

  .pitch-row {
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 8px;
    margin-bottom: 14px;
    flex-wrap: nowrap;
  }
  .pitch-row:last-child {
    margin-bottom: 0;
  }

  .pitch-node {
    flex: 1 1 0;
    max-width: 118px;
    min-width: 64px;
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 14px;
    padding: 8px 4px 6px 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.45);
    transition: transform 0.15s ease, border-color 0.15s ease;
  }

  .pitch-node.selected {
    border: 2px solid var(--accent-emerald);
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.5);
  }

  .node-avatar-wrap {
    position: relative;
    width: 48px;
    height: 48px;
    margin-bottom: 5px;
  }

  .node-avatar-wrap img {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
    background: #090D16;
    border: 1.5px solid rgba(255, 255, 255, 0.25);
  }

  .badge-cap {
    position: absolute;
    bottom: -2px;
    right: -4px;
    background: #FBBF24;
    color: #000;
    font-size: 9px;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 6px;
    border: 1px solid #FFF;
  }

  .badge-vc {
    position: absolute;
    bottom: -2px;
    right: -4px;
    background: #94A3B8;
    color: #000;
    font-size: 9px;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 6px;
    border: 1px solid #FFF;
  }

  .badge-flag {
    position: absolute;
    top: -3px;
    left: -4px;
    background: var(--accent-rose);
    color: #FFF;
    font-size: 8.5px;
    font-weight: 800;
    padding: 1px 4px;
    border-radius: 5px;
  }

  .node-name {
    font-size: 12px;
    font-weight: 700;
    color: #FFFFFF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 96%;
    line-height: 1.2;
  }

  .node-meta {
    font-size: 10.5px;
    color: #CBD5E1;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px 0 4px 0;
  }

  .fdr-pill {
    font-size: 9.5px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 5px;
    width: 92%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .fdr-1 { background: var(--fdr-1); color: #FFF; }
  .fdr-2 { background: var(--fdr-2); color: #052E16; }
  .fdr-3 { background: var(--fdr-3); color: #F8FAFC; }
  .fdr-4 { background: var(--fdr-4); color: #FFF; }
  .fdr-5 { background: var(--fdr-5); color: #FFF; }

  /* BENCH TRAY */
  .bench-tray {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 14px 12px;
    margin-bottom: 18px;
  }

  .bench-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary);
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
  }

  /* DOSSIER & SECTION CARDS */
  .dossier-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
    margin-bottom: 18px;
  }

  .dossier-top {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 16px;
  }

  .dossier-avatar {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    object-fit: cover;
    border: 2.5px solid var(--accent-emerald);
    background: #090D16;
  }

  .stat-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 12px;
  }

  @media (max-width: 640px) {
    .stat-grid-4 {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .stat-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 10px 12px;
  }

  .stat-box-lbl {
    font-size: 10.5px;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 600;
  }

  .stat-box-val {
    font-size: 16px;
    font-weight: 800;
    color: #FFF;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 2px;
  }

  /* TRANSFER TARGET CARDS */
  .sell-banner {
    background: linear-gradient(90deg, rgba(244, 63, 94, 0.12) 0%, rgba(17, 24, 39, 0.9) 100%);
    border: 1px solid rgba(244, 63, 94, 0.3);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 16px;
  }

  .buy-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 12px;
  }

  @media (max-width: 768px) {
    .buy-grid-3 {
      grid-template-columns: 1fr;
    }
  }

  .buy-card {
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 14px;
    padding: 14px;
  }

  /* MINI-LEAGUE TABLE */
  .ml-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  .ml-table th {
    text-align: left;
    padding: 10px 12px;
    font-size: 11px;
    text-transform: uppercase;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-subtle);
  }

  .ml-table td {
    padding: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  }

  .ml-row-me {
    background: rgba(16, 185, 129, 0.12);
    font-weight: 700;
  }

  /* TABS & NATIVE WIDGET STYLING */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: var(--bg-surface);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid var(--border-subtle);
  }

  .stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 700;
    font-size: 12.5px;
    color: var(--text-secondary);
  }

  .stTabs [aria-selected="true"] {
    background-color: var(--bg-elevated) !important;
    color: var(--accent-emerald) !important;
  }

  div.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 12px !important;
  }

  div.stButton > button:hover {
    border-color: var(--accent-emerald) !important;
    color: var(--accent-emerald) !important;
  }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. AUTHENTICATION & TEAM ID INITIALIZATION
# ---------------------------------------------------------
auth_secret = st.secrets.get("APP_PASSWORD", "fpl2025")
default_team_id = int(st.secrets.get("DEFAULT_TEAM_ID", 1153921))

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = (st.query_params.get("auth") == "passed")

if not st.session_state["authenticated"]:
    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="dossier-card" style="text-align: center;">
          <h2 style="margin:0; font-weight:800; color:#FFF;">KINGS COUNTY FC</h2>
          <p style="color:#10B981; font-size:12px; font-weight:700; letter-spacing:1.5px; margin-top:4px;">
            FPL TACTICAL COMMAND CENTER
          </p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("auth_form"):
            pw = st.text_input("Manager Access Key", type="password")
            tid = st.number_input("FPL Entry ID", value=default_team_id, step=1)
            if st.form_submit_button("Launch Command Center", use_container_width=True):
                if pw == auth_secret or auth_secret == "":
                    st.session_state["authenticated"] = True
                    st.session_state["team_id"] = int(tid)
                    st.query_params["auth"] = "passed"
                    st.rerun()
                else:
                    st.error("Invalid Manager Access Key.")
    st.stop()

# ---------------------------------------------------------
# 4. CLUB KIT SVG GENERATOR (2026/27 FULL COVERAGE)
# ---------------------------------------------------------
CLUB_PALETTES = {
    "ARS": {"p": "#EF0107", "s": "#FFFFFF"},
    "AVL": {"p": "#670E36", "s": "#95BFE5"},
    "BOU": {"p": "#DA291C", "s": "#000000"},
    "BRE": {"p": "#E30613", "s": "#FFFFFF"},
    "BHA": {"p": "#0057B8", "s": "#FFFFFF"},
    "CHE": {"p": "#034694", "s": "#FFFFFF"},
    "COV": {"p": "#0593D0", "s": "#FFFFFF"},
    "CRY": {"p": "#1B458F", "s": "#C4122E"},
    "EVE": {"p": "#003399", "s": "#FFFFFF"},
    "FUL": {"p": "#FFFFFF", "s": "#000000"},
    "HUL": {"p": "#F5A12D", "s": "#000000"},
    "IPS": {"p": "#0055A5", "s": "#FFFFFF"},
    "LEE": {"p": "#FFFFFF", "s": "#1D428A"},
    "LEI": {"p": "#0053A0", "s": "#FFFFFF"},
    "LIV": {"p": "#C8102E", "s": "#FFFFFF"},
    "MCI": {"p": "#6CABDD", "s": "#FFFFFF"},
    "MUN": {"p": "#DA291C", "s": "#000000"},
    "NEW": {"p": "#241F20", "s": "#FFFFFF"},
    "NFO": {"p": "#DD0000", "s": "#FFFFFF"},
    "SOU": {"p": "#D71920", "s": "#FFFFFF"},
    "SUN": {"p": "#EB172B", "s": "#FFFFFF"},
    "TOT": {"p": "#FFFFFF", "s": "#132257"},
    "WHU": {"p": "#7A263A", "s": "#1BB1E7"},
    "WOL": {"p": "#FDB913", "s": "#231F20"},
    "DEFAULT": {"p": "#1E293B", "s": "#10B981"}
}

def generate_svg_kit(team_short, is_gk=False):
    colors = CLUB_PALETTES.get(str(team_short).upper(), CLUB_PALETTES["DEFAULT"])
    p_col = "#10B981" if is_gk else colors["p"]
    s_col = "#090D16" if is_gk else colors["s"]
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'>
      <path d='M25,18 L10,32 L20,40 L26,33 L26,65 L54,65 L54,33 L60,40 L70,32 L55,18 C50,23 30,23 25,18 Z'
            fill='{p_col}' stroke='{s_col}' stroke-width='2'/>
      <text x='40' y='49' font-family='sans-serif' font-weight='800' font-size='11'
            fill='{s_col}' text-anchor='middle'>{str(team_short)[:3]}</text>
    </svg>"""
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

# ---------------------------------------------------------
# 5. LIVE FPL API ENGINE (WITH HISTORY & MINI-LEAGUES)
# ---------------------------------------------------------
HEADERS = {"User-Agent": "Mozilla/5.0"}

@st.cache_data(ttl=300)
def fetch_bootstrap():
    try:
        r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def fetch_fixtures():
    try:
        r = requests.get("https://fantasy.premierleague.com/api/fixtures/", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=120)
def fetch_manager_full(tid):
    try:
        r_ent = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/", headers=HEADERS, timeout=8)
        r_hist = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/history/", headers=HEADERS, timeout=8)
        entry = r_ent.json() if r_ent.status_code == 200 else {}
        history = r_hist.json() if r_hist.status_code == 200 else {}
        curr_gw = entry.get("current_event") or 6
        r_picks = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/event/{curr_gw}/picks/", headers=HEADERS, timeout=8)
        picks = r_picks.json() if r_picks.status_code == 200 else {}
        return entry, history, picks, int(curr_gw)
    except Exception:
        return {}, {}, {}, 6

@st.cache_data(ttl=180)
def fetch_league_standings(league_id):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=180)
def fetch_rival_picks(rival_tid, gw):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/entry/{rival_tid}/event/{gw}/picks/", headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

# Load Data
bootstrap = fetch_bootstrap() or {"elements": [], "teams": [], "events": []}
fixtures_list = fetch_fixtures()
team_id = st.session_state.get("team_id", default_team_id)
entry_data, history_data, picks_data, current_gw = fetch_manager_full(team_id)

elements_map = {p["id"]: p for p in bootstrap.get("elements", [])}
teams_map = {t["id"]: t for t in bootstrap.get("teams", [])}
events_map = {e["id"]: e for e in bootstrap.get("events", [])}

# Build 5-GW Fixture Runway per Team
team_runway = {t_id: [] for t_id in teams_map}
for fix in fixtures_list:
    ev = fix.get("event")
    if not fix.get("finished") and ev and ev >= current_gw:
        h_id, a_id = fix["team_h"], fix["team_a"]
        h_short = teams_map.get(h_id, {}).get("short_name", "TBD")
        a_short = teams_map.get(a_id, {}).get("short_name", "TBD")
        if h_id in team_runway and len(team_runway[h_id]) < 5:
            team_runway[h_id].append({"gw": ev, "opp": a_short, "venue": "H", "fdr": fix.get("team_h_difficulty", 3)})
        if a_id in team_runway and len(team_runway[a_id]) < 5:
            team_runway[a_id].append({"gw": ev, "opp": h_short, "venue": "A", "fdr": fix.get("team_a_difficulty", 3)})

# Calculate Expected Points (xP) Metric for Every Player
def compute_player_xp(p):
    form = float(p.get("form") or 0.0)
    xgi = float(p.get("expected_goal_involvements") or 0.0)
    mins = max(p.get("minutes", 0), 1)
    xgi_per_90 = (xgi / mins) * 90 if mins >= 90 else form * 0.12
    runway = team_runway.get(p.get("team"), [])
    next_fdr = runway[0]["fdr"] if runway else 3
    avg_5_fdr = sum(r["fdr"] for r in runway[:5]) / len(runway[:5]) if runway else 3.0
    chance = (p.get("chance_of_playing_next_round") if p.get("chance_of_playing_next_round") is not None else 100) / 100.0
    
    # Immediate GW xP & 5-GW xP
    fdr_mult = {1: 1.35, 2: 1.2, 3: 1.0, 4: 0.82, 5: 0.68}.get(next_fdr, 1.0)
    xp_next = round(((form * 0.55) + (xgi_per_90 * 4.2) + 1.8) * fdr_mult * chance, 1)
    xp_5gw = round(xp_next * 4.6 * (3.0 / max(avg_5_fdr, 1.5)), 1)
    return xp_next, xp_5gw, next_fdr, round(avg_5_fdr, 2)

for pid, p_obj in elements_map.items():
    xp_1, xp_5, nfdr, afdr = compute_player_xp(p_obj)
    p_obj["xp_next"] = xp_1
    p_obj["xp_5gw"] = xp_5
    p_obj["next_fdr"] = nfdr
    p_obj["avg_5_fdr"] = afdr
    p_obj["team_short"] = teams_map.get(p_obj.get("team"), {}).get("short_name", "EPL")
    p_obj["runway"] = team_runway.get(p_obj.get("team"), [])

# Extract Active Squad
starting_xi, bench_xi = [], []
if picks_data and "picks" in picks_data:
    for pk in picks_data["picks"]:
        base_p = elements_map.get(pk["element"])
        if base_p:
            p_copy = dict(base_p)
            p_copy["is_captain"] = pk.get("is_captain", False)
            p_copy["is_vice_captain"] = pk.get("is_vice_captain", False)
            p_copy["pick_pos"] = pk.get("position", 1)
            if p_copy["pick_pos"] <= 11:
                starting_xi.append(p_copy)
            else:
                bench_xi.append(p_copy)

full_squad = starting_xi + bench_xi
if "selected_pid" not in st.session_state and full_squad:
    cap_p = next((x for x in starting_xi if x.get("is_captain")), starting_xi[0])
    st.session_state["selected_pid"] = cap_p["id"]

# ---------------------------------------------------------
# 6. COMPUTE HISTORICAL DELTAS FOR EXECUTIVE KPI STRIP
# ---------------------------------------------------------
curr_hist = history_data.get("current", [])
gw_avg = events_map.get(current_gw, {}).get("average_entry_score", 45)

if len(curr_hist) >= 2:
    latest_h = curr_hist[-1]
    prev_h = curr_hist[-2]
    total_pts = latest_h.get("total_points", 0)
    gw_pts = latest_h.get("points", 0)
    overall_rank = latest_h.get("overall_rank", 0)
    rank_delta = prev_h.get("overall_rank", overall_rank) - overall_rank  # positive = green arrow
    bank_now = latest_h.get("bank", 0) / 10.0
    bank_delta = (latest_h.get("bank", 0) - prev_h.get("bank", 0)) / 10.0
    val_now = latest_h.get("value", 1000) / 10.0
    val_delta = (latest_h.get("value", 1000) - prev_h.get("value", 1000)) / 10.0
elif len(curr_hist) == 1:
    latest_h = curr_hist[0]
    total_pts = latest_h.get("total_points", 0)
    gw_pts = latest_h.get("points", 0)
    overall_rank = latest_h.get("overall_rank", 0)
    rank_delta = 0
    bank_now = latest_h.get("bank", 0) / 10.0
    bank_delta = 0.0
    val_now = latest_h.get("value", 1000) / 10.0
    val_delta = 0.0
else:
    total_pts = entry_data.get("summary_overall_points", 385)
    gw_pts = entry_data.get("summary_event_points", 62)
    overall_rank = entry_data.get("summary_overall_rank", 42108)
    rank_delta = 4120
    bank_now = (entry_data.get("last_deadline_bank", 7) or 7) / 10.0
    bank_delta = 0.2
    val_now = (entry_data.get("last_deadline_value", 1004) or 1004) / 10.0
    val_delta = 0.3

team_xp_total = round(sum(
    p["xp_next"] * (2 if p.get("is_captain") else 1) for p in starting_xi
), 1)

# ---------------------------------------------------------
# 7. RENDER EXECUTIVE HEADER & KPI TREND TILES
# ---------------------------------------------------------
crest_svg = """
<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 6 L88 20 C88 64 50 92 50 92 C50 92 12 64 12 20 L50 6 Z" fill="#111827" stroke="#10B981" stroke-width="5"/>
  <path d="M30 42 L39 28 L50 37 L61 28 L70 42 L64 53 L36 53 Z" fill="#FBBF24"/>
  <circle cx="50" cy="69" r="12" fill="#FFFFFF"/>
</svg>
"""

rank_arrow = f"▲ {abs(rank_delta):,}" if rank_delta > 0 else (f"▼ {abs(rank_delta):,}" if rank_delta < 0 else "━ 0")
rank_cls = "delta-up" if rank_delta >= 0 else "delta-down"

gw_vs_avg = gw_pts - gw_avg
gw_cls = "delta-up" if gw_vs_avg >= 0 else "delta-down"
gw_delta_str = f"{'+' if gw_vs_avg >= 0 else ''}{gw_vs_avg} vs Avg"

val_cls = "delta-up" if val_delta >= 0 else "delta-down"
val_delta_str = f"{'+' if val_delta >= 0 else ''}£{val_delta:.1f}m"

bank_cls = "delta-up" if bank_delta > 0 else ("delta-down" if bank_delta < 0 else "delta-neutral")
bank_delta_str = f"{'+' if bank_delta > 0 else ''}£{bank_delta:.1f}m GW"

st.markdown(f"""
<div class="kcfc-header">
  <div class="kcfc-brand">
    {crest_svg}
    <div>
      <div class="kcfc-brand-title">KINGS COUNTY FC</div>
      <div class="kcfc-brand-sub">BROOKLYN, NY &bull; TACTICAL COMMAND CENTER</div>
    </div>
  </div>
  <div class="kcfc-gw-pill">GAMEWEEK {current_gw} ACTIVE</div>
</div>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Season Points</div>
    <div class="kpi-val-row">
      <div class="kpi-value">{total_pts:,}</div>
      <span class="kpi-delta {gw_cls}">GW{current_gw}: {gw_pts}p ({gw_delta_str})</span>
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-label">Overall Rank</div>
    <div class="kpi-val-row">
      <div class="kpi-value">{overall_rank:,}</div>
      <span class="kpi-delta {rank_cls}">{rank_arrow}</span>
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-label">Squad Value</div>
    <div class="kpi-val-row">
      <div class="kpi-value">£{val_now:.1f}m</div>
      <span class="kpi-delta {val_cls}">{val_delta_str}</span>
    </div>
  </div>

  <div class="kpi-card">
    <div class="kpi-label">In The Bank</div>
    <div class="kpi-val-row">
      <div class="kpi-value" style="color:#10B981;">£{bank_now:.1f}m</div>
      <span class="kpi-delta {bank_cls}">{bank_delta_str}</span>
    </div>
  </div>

  <div class="kpi-card span-mobile-2">
    <div class="kpi-label">Projected Starting XI xP</div>
    <div class="kpi-val-row">
      <div class="kpi-value" style="color:#06B6D4;">{team_xp_total} pts</div>
      <span class="kpi-delta delta-up">Live Model</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. NAVIGATION TABS
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_league, tab_ai = st.tabs([
    "🏟️ Tactical Pitch & Dossier",
    "🔄 Transfer Matrix & Simulator",
    "🏆 Mini-League & Rival Spy",
    "🤖 AI Tactical Advisor"
])

# Helper to build HTML node for a single player on the pitch
def build_pitch_node_html(p, is_selected=False, bench_slot=None):
    code = str(p.get("code") or p.get("photo", "").split(".")[0].lstrip("p"))
    img_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png"
    fallback_svg = generate_svg_kit(p.get("team_short", "EPL"), is_gk=(p.get("element_type") == 1))
    
    cap_badge = "<div class='badge-cap'>C</div>" if p.get("is_captain") else (
                "<div class='badge-vc'>V</div>" if p.get("is_vice_captain") else "")
    
    chance = p.get("chance_of_playing_next_round")
    flag_badge = ""
    if chance is not None and chance < 100:
        flag_badge = f"<div class='badge-flag'>{'OUT' if chance == 0 else f'{chance}%'}</div>"
    elif bench_slot:
        flag_badge = f"<div class='badge-flag' style='background:#334155;'>SUB {bench_slot}</div>"

    runway = p.get("runway", [])
    nxt = runway[0] if runway else {"opp": "TBD", "venue": "H", "fdr": 3}
    fdr_c = f"fdr-{nxt['fdr']}"
    sel_c = "selected" if is_selected else ""
    price = p.get("now_cost", 50) / 10.0

    return f"""
    <div class="pitch-node {sel_c}">
      <div class="node-avatar-wrap">
        <img src="{img_url}" referrerpolicy="no-referrer" loading="lazy"
             onerror="this.onerror=null;this.src='{fallback_svg}';" />
        {cap_badge}
        {flag_badge}
      </div>
      <div class="node-name">{p.get('web_name')}</div>
      <div class="node-meta">£{price:.1f}m &bull; {p.get('xp_next')}xP</div>
      <div class="fdr-pill {fdr_c}">{nxt['opp']} ({nxt['venue']})</div>
    </div>
    """

# =========================================================
# TAB 1: TACTICAL PITCH & INTERACTIVE PLAYER DOSSIER
# =========================================================
with tab_pitch:
    col_left, col_right = st.columns([1.35, 1], gap="medium")

    with col_left:
        gks = [p for p in starting_xi if p.get("element_type") == 1]
        defs = [p for p in starting_xi if p.get("element_type") == 2]
        mids = [p for p in starting_xi if p.get("element_type") == 3]
        fwds = [p for p in starting_xi if p.get("element_type") == 4]
        bench_sorted = sorted(bench_xi, key=lambda x: x.get("pick_pos", 12))

        sel_pid = st.session_state.get("selected_pid")

        # Build Pure CSS Grid Pitch in ONE markdown call (never breaks or squishes)
        gk_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in gks)
        def_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in defs)
        mid_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in mids)
        fwd_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in fwds)

        st.markdown(f"""
        <div class="pitch-wrapper">
          <div class="pitch-row">{gk_html}</div>
          <div class="pitch-row">{def_html}</div>
          <div class="pitch-row">{mid_html}</div>
          <div class="pitch-row">{fwd_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # Bench Tray
        bench_html = "".join(
            build_pitch_node_html(p, p["id"] == sel_pid, bench_slot=i+1)
            for i, p in enumerate(bench_sorted)
        )
        st.markdown(f"""
        <div class="bench-tray">
          <div class="bench-label">
            <span>🪑 Priority Auto-Sub Bench</span>
            <span style="color:#10B981;">1 GK + 3 Outfield</span>
          </div>
          <div class="pitch-row" style="margin-bottom:0;">{bench_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Clean Mobile-Friendly Player Selector Pill Bar
        squad_options = {p["id"]: f"{'⭐ ' if p.get('is_captain') else ''}{p['web_name']} ({p['team_short']} - £{p['now_cost']/10:.1f}m)" for p in full_squad}
        if squad_options:
            chosen_pid = st.selectbox(
                "🔍 Select Squad Player to Inspect in Dossier:",
                options=list(squad_options.keys()),
                format_func=lambda x: squad_options[x],
                index=list(squad_options.keys()).index(sel_pid) if sel_pid in squad_options else 0
            )
            if chosen_pid != sel_pid:
                st.session_state["selected_pid"] = chosen_pid
                st.rerun()

        sp = elements_map.get(st.session_state.get("selected_pid"))
        if sp:
            code = str(sp.get("code") or sp.get("photo", "").split(".")[0].lstrip("p"))
            p_img = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png"
            p_svg = generate_svg_kit(sp.get("team_short", "EPL"), is_gk=(sp.get("element_type") == 1))
            pos_name = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}.get(sp.get("element_type"), "Player")
            p_price = sp.get("now_cost", 50) / 10.0
            pts_per_m = round(sp.get("total_points", 0) / max(p_price, 4.0), 1)

            # Build 5-GW Runway HTML
            runway_chips = ""
            for r in sp.get("runway", [])[:5]:
                runway_chips += f"""
                <div style="flex:1; background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 4px; text-align:center;">
                  <div style="font-size:9.5px; color:var(--text-secondary);">GW{r['gw']}</div>
                  <div style="font-size:11.5px; font-weight:700; color:#FFF; margin:3px 0;">{r['opp']} ({r['venue']})</div>
                  <span class="fdr-pill fdr-{r['fdr']}" style="display:inline-block; width:auto; padding:1px 6px;">FDR {r['fdr']}</span>
                </div>
                """

            news_banner = ""
            if sp.get("news"):
                news_banner = f"""
                <div style="background:rgba(244,63,94,0.12); border-left:3px solid #F43F5E; padding:10px 12px; border-radius:8px; font-size:12px; color:#FDA4AF; margin-bottom:14px;">
                  <strong>Medical / Status Alert:</strong> {sp.get('news')}
                </div>
                """

            # Verdict logic
            if sp.get("xp_next", 0) >= 5.5:
                verdict_tag, verdict_col = "CAPTAIN / LOCK STARTER", "#10B981"
            elif sp.get("xp_next", 0) >= 3.8:
                verdict_tag, verdict_col = "SOLID ROTATION HOLD", "#06B6D4"
            else:
                verdict_tag, verdict_col = "TRANSFER WATCH / BENCH", "#F59E0B"

            st.markdown(f"""
            <div class="dossier-card">
              <div class="dossier-top">
                <img class="dossier-avatar" src="{p_img}" referrerpolicy="no-referrer"
                     onerror="this.onerror=null;this.src='{p_svg}';" />
                <div style="flex:1;">
                  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                    <span style="font-size:20px; font-weight:800; color:#FFF;">{sp.get('first_name')} {sp.get('second_name')}</span>
                    <span style="font-size:10px; font-weight:800; padding:4px 9px; border-radius:999px; background:rgba(16,185,129,0.15); color:{verdict_col}; border:1px solid {verdict_col};">
                      {verdict_tag}
                    </span>
                  </div>
                  <div style="font-size:12.5px; color:var(--text-secondary); margin-top:4px;">
                    {pos_name} &bull; <strong>{teams_map.get(sp.get('team'), {}).get('name', 'Premier League')}</strong> &bull; Ownership: {sp.get('selected_by_percent')}%
                  </div>
                </div>
              </div>

              {news_banner}

              <div class="stat-grid-4">
                <div class="stat-box">
                  <div class="stat-box-lbl">Current Price</div>
                  <div class="stat-box-val">£{p_price:.1f}m</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">GW{current_gw} xP</div>
                  <div class="stat-box-val" style="color:#10B981;">{sp.get('xp_next')}</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">5-GW Projected</div>
                  <div class="stat-box-val" style="color:#06B6D4;">{sp.get('xp_5gw')}p</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">Form Rating</div>
                  <div class="stat-box-val">{sp.get('form')}</div>
                </div>
              </div>

              <div class="stat-grid-4">
                <div class="stat-box">
                  <div class="stat-box-lbl">xG + xA (xGI)</div>
                  <div class="stat-box-val">{sp.get('expected_goal_involvements', '0.00')}</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">ICT Threat/Index</div>
                  <div class="stat-box-val">{sp.get('ict_index', '0.0')}</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">Season Points</div>
                  <div class="stat-box-val">{sp.get('total_points', 0)}</div>
                </div>
                <div class="stat-box">
                  <div class="stat-box-lbl">Value (Pts/£m)</div>
                  <div class="stat-box-val">{pts_per_m}</div>
                </div>
              </div>

              <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-secondary); margin:14px 0 8px 0;">
                Next 5 Fixtures Runway (Avg FDR: {sp.get('avg_5_fdr')})
              </div>
              <div style="display:flex; gap:8px;">
                {runway_chips}
              </div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# TAB 2: TOP 3 TRANSFER MATRIX & WHAT-IF SIMULATOR
# =========================================================
with tab_transfers:
    st.markdown("""
    <div class="dossier-card" style="padding:16px 20px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
          <h3 style="margin:0; font-size:17px; font-weight:800; color:#FFF;">🔄 ALGORITHMIC SQUAD AUDIT: TOP 3 SELL CANDIDATES</h3>
          <p style="margin:4px 0 0 0; font-size:12.5px; color:var(--text-secondary);">
            Ranked by injury risk, depressed form, and upcoming 5-GW fixture difficulty. Each sell candidate displays the top 3 in-budget replacements.
          </p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    squad_ids = {p["id"] for p in full_squad}
    # Score every squad player for replacement urgency
    sell_rankings = []
    for p in full_squad:
        chance = p.get("chance_of_playing_next_round")
        chance_val = 100 if chance is None else chance
        urgency = ((100 - chance_val) * 0.55) + ((6.5 - min(p.get("xp_next", 3.0), 6.5)) * 4.2) + (p.get("avg_5_fdr", 3.0) * 2.5)
        sell_rankings.append((urgency, p))

    sell_rankings.sort(key=lambda x: x[0], reverse=True)

    for idx, (urg_score, sell_p) in enumerate(sell_rankings[:3]):
        s_cost = sell_p.get("now_cost", 50) / 10.0
        max_avail = round(s_cost + bank_now, 1)
        pos_id = sell_p.get("element_type", 3)

        reason_str = sell_p.get("news") or (
            f"Low projected output ({sell_p.get('xp_next')} xP) & tough 5-GW fixture runway (Avg FDR {sell_p.get('avg_5_fdr')})"
        )

        # Find Top 3 Replacements within budget
        replacements = [
            cand for cand in elements_map.values()
            if cand["id"] not in squad_ids
            and cand.get("element_type") == pos_id
            and (cand.get("now_cost", 999) / 10.0) <= max_avail
            and (cand.get("chance_of_playing_next_round") is None or cand.get("chance_of_playing_next_round") >= 75)
        ]
        replacements.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
        top_3_buys = replacements[:3]

        buy_cards_html = ""
        for b_i, bp in enumerate(top_3_buys):
            b_cost = bp.get("now_cost", 50) / 10.0
            xp_gain_5 = round(bp.get("xp_5gw", 0) - sell_p.get("xp_5gw", 0), 1)
            nxt_fix = bp["runway"][0] if bp.get("runway") else {"opp": "TBD", "venue": "H", "fdr": 3}
            buy_cards_html += f"""
            <div class="buy-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:14px; font-weight:800; color:#FFF;">#{b_i+1} {bp.get('web_name')} ({bp.get('team_short')})</span>
                <span style="font-size:11px; font-weight:800; color:#10B981; background:rgba(16,185,129,0.18); padding:2px 8px; border-radius:6px;">
                  +{xp_gain_5} xP (5GW)
                </span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); margin:6px 0;">
                Price: <strong>£{b_cost:.1f}m</strong> (Leaves £{max_avail - b_cost:.1f}m) &bull; Next: <strong>{nxt_fix['opp']} ({nxt_fix['venue']})</strong>
              </div>
              <div style="display:flex; gap:8px; font-size:11px; font-family:'JetBrains Mono', monospace; color:#CBD5E1;">
                <span>GW xP: <strong>{bp.get('xp_next')}</strong></span> &bull;
                <span>Form: <strong>{bp.get('form')}</strong></span> &bull;
                <span>xGI: <strong>{bp.get('expected_goal_involvements')}</strong></span>
              </div>
            </div>
            """

        st.markdown(f"""
        <div class="sell-banner">
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
              <span style="font-size:11px; font-weight:800; background:#F43F5E; color:#FFF; padding:3px 8px; border-radius:6px; margin-right:8px;">
                SELL PRIORITY #{idx+1}
              </span>
              <span style="font-size:16px; font-weight:800; color:#FFF;">{sell_p.get('web_name')} ({sell_p.get('team_short')})</span>
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:12.5px; color:#F8FAFC;">
              Sale Value: <strong>£{s_cost:.1f}m</strong> &bull; Max Budget: <strong style="color:#10B981;">£{max_avail:.1f}m</strong>
            </div>
          </div>
          <div style="font-size:12px; color:#FDA4AF; margin-top:6px;">
            <strong>Audit Trigger:</strong> {reason_str}
          </div>
          <div class="buy-grid-3">
            {buy_cards_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # INTERACTIVE WHAT-IF SIMULATOR
    st.markdown("""
    <div class="dossier-card" style="margin-top:24px;">
      <h3 style="margin:0 0 12px 0; font-size:17px; font-weight:800; color:#06B6D4;">
        🧪 INTERACTIVE WHAT-IF TRANSFER & HIT SIMULATOR
      </h3>
    """, unsafe_allow_html=True)

    sim_c1, sim_c2, sim_c3 = st.columns([1.2, 1.2, 0.8])
    out_map = {p["id"]: f"{p['web_name']} ({p['team_short']} - £{p['now_cost']/10:.1f}m | {p['xp_next']} xP)" for p in full_squad}
    with sim_c1:
        sim_out_id = st.selectbox("1. Select Player to Transfer OUT:", options=list(out_map.keys()), format_func=lambda x: out_map[x])

    out_p = elements_map.get(sim_out_id, full_squad[0] if full_squad else {})
    avail_budget = round((out_p.get("now_cost", 50) / 10.0) + bank_now, 1)
    eligible_ins = [
        p for p in elements_map.values()
        if p["id"] not in squad_ids and p.get("element_type") == out_p.get("element_type", 3)
        and (p.get("now_cost", 999) / 10.0) <= avail_budget
    ]
    eligible_ins.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
    in_map = {p["id"]: f"{p['web_name']} ({p['team_short']} - £{p['now_cost']/10:.1f}m | {p['xp_next']} xP)" for p in eligible_ins}

    with sim_c2:
        sim_in_id = st.selectbox(f"2. Select Target IN (Max £{avail_budget:.1f}m):", options=list(in_map.keys()), format_func=lambda x: in_map[x]) if in_map else None

    with sim_c3:
        take_hit = st.selectbox("3. Transfer Cost:", options=[0, -4], format_func=lambda x: "Free Transfer (0 pts)" if x == 0 else "-4 Point Hit")

    if sim_in_id:
        in_p = elements_map[sim_in_id]
        gw1_net = round((in_p["xp_next"] - out_p["xp_next"]) + take_hit, 1)
        gw5_net = round((in_p["xp_5gw"] - out_p["xp_5gw"]) + take_hit, 1)
        new_bank_bal = round(avail_budget - (in_p["now_cost"] / 10.0), 1)
        fdr_diff = round(in_p["avg_5_fdr"] - out_p["avg_5_fdr"], 2)

        verdict_txt = "✅ RECOMMENDED MOVE" if gw5_net >= 4.0 else ("⚖️ MARGINAL / LUXURY SWAP" if gw5_net >= 0 else "⛔ HOLD TRANSFER")
        verdict_c = "#10B981" if gw5_net >= 4.0 else ("#F59E0B" if gw5_net >= 0 else "#F43F5E")

        st.markdown(f"""
        <div class="stat-grid-4" style="margin-top:14px;">
          <div class="stat-box">
            <div class="stat-box-lbl">Immediate GW{current_gw} Net Impact</div>
            <div class="stat-box-val" style="color:{'#10B981' if gw1_net >= 0 else '#F43F5E'};">{'+' if gw1_net >= 0 else ''}{gw1_net} xP</div>
          </div>
          <div class="stat-box">
            <div class="stat-box-lbl">5-GW Cumulative Net Gain</div>
            <div class="stat-box-val" style="color:{'#10B981' if gw5_net >= 0 else '#F43F5E'};">{'+' if gw5_net >= 0 else ''}{gw5_net} xP</div>
          </div>
          <div class="stat-box">
            <div class="stat-box-lbl">Remaining Bank</div>
            <div class="stat-box-val">£{new_bank_bal:.1f}m</div>
          </div>
          <div class="stat-box">
            <div class="stat-box-lbl">Model Verdict</div>
            <div class="stat-box-val" style="font-size:13px; color:{verdict_c};">{verdict_txt}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 3: LIVE MINI-LEAGUE STANDINGS & RIVAL SPY ENGINE
# =========================================================
with tab_league:
    classic_leagues = [
        lg for lg in entry_data.get("leagues", {}).get("classic", [])
        if lg.get("league_type") == "x" or lg.get("id", 0) > 350
    ]
    if not classic_leagues:
        classic_leagues = entry_data.get("leagues", {}).get("classic", [])

    if classic_leagues:
        lg_map = {lg["id"]: f"{lg['name']} (Your Rank: #{lg.get('entry_rank', '?')})" for lg in classic_leagues}
        sel_lg_id = st.selectbox("🏆 Select Mini-League to Analyze:", options=list(lg_map.keys()), format_func=lambda x: lg_map[x])
        standings_json = fetch_league_standings(sel_lg_id)
        rows = standings_json.get("standings", {}).get("results", []) if standings_json else []
    else:
        rows = []

    if rows:
        leader_pts = rows[0]["total"]
        my_row = next((r for r in rows if r["entry"] == team_id), None)
        my_pts = my_row["total"] if my_row else total_pts
        gap_to_first = leader_pts - my_pts

        # Choose top rival (if user is 1st, pick 2nd place; otherwise pick 1st place)
        rival_Candidates = [r for r in rows[:10] if r["entry"] != team_id]
        rival_map = {r["entry"]: f"#{r['rank']} {r['entry_name']} ({r['player_name']}) - {r['total']} pts" for r in rival_Candidates}

        col_tbl, col_spy = st.columns([1.15, 1], gap="medium")

        with col_tbl:
            table_rows_html = ""
            for r in rows[:12]:
                is_me = (r["entry"] == team_id)
                row_cls = "ml-row-me" if is_me else ""
                gap = r["total"] - my_pts
                gap_str = "YOU" if is_me else (f"+{gap}" if gap > 0 else f"{gap}")
                mv = r.get("last_rank", r["rank"]) - r["rank"]
                mv_icon = "🟢" if mv > 0 else ("🔴" if mv < 0 else "⚪")
                table_rows_html += f"""
                <tr class="{row_cls}">
                  <td>{mv_icon} #{r['rank']}</td>
                  <td><strong>{r['entry_name']}</strong><br><span style="font-size:11px; color:var(--text-secondary);">{r['player_name']}</span></td>
                  <td style="font-family:'JetBrains Mono', monospace;">{r['event_total']}</td>
                  <td style="font-family:'JetBrains Mono', monospace; font-weight:700;">{r['total']}</td>
                  <td style="font-family:'JetBrains Mono', monospace; color:{'#F43F5E' if gap > 0 else '#10B981'};">{gap_str}</td>
                </tr>
                """

            st.markdown(f"""
            <div class="dossier-card">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:16px; font-weight:800; color:#FFF;">📊 Live Mini-League Table</span>
                <span style="font-size:12px; font-weight:700; color:#10B981;">
                  {'Leading League!' if gap_to_first == 0 else f'{gap_to_first} pts behind 1st'}
                </span>
              </div>
              <table class="ml-table">
                <thead>
                  <tr><th>Rank</th><th>Team & Manager</th><th>GW</th><th>Total</th><th>vs You</th></tr>
                </thead>
                <tbody>{table_rows_html}</tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

        with col_spy:
            st.markdown("<div class='dossier-card'><h4 style='margin:0 0 10px 0; color:#FFF;'>🕵️ Head-to-Head Rival Spy & Strategy</h4>", unsafe_allow_html=True)
            if rival_map:
                sel_rival_id = st.selectbox("Select Opponent to Compare:", options=list(rival_map.keys()), format_func=lambda x: rival_map[x])
                rival_picks_json = fetch_rival_picks(sel_rival_id, current_gw)
                if rival_picks_json and "picks" in rival_picks_json:
                    rival_xi_ids = {pk["element"] for pk in rival_picks_json["picks"] if pk.get("position", 1) <= 11}
                    my_xi_ids = {p["id"] for p in starting_xi}

                    shared_ids = my_xi_ids.intersection(rival_xi_ids)
                    my_diffs = [elements_map[i] for i in (my_xi_ids - rival_xi_ids) if i in elements_map]
                    their_diffs = [elements_map[i] for i in (rival_xi_ids - my_xi_ids) if i in elements_map]

                    my_diff_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['xp_next']}xP)" for p in my_diffs) or "None"
                    their_diff_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['xp_next']}xP)" for p in their_diffs) or "None"

                    posture = "AGGRESSIVE DIFFERENTIAL" if gap_to_first > 25 else "DEFENSIVE BLOCKING"
                    posture_advice = (
                        "You are chasing points. Avoid copying their template picks; captain your highest-ceiling differential."
                        if gap_to_first > 25 else
                        "You are in a tight race or leading. Protect your rank by matching their high-ownership captain and upgrading weak bench links."
                    )

                    st.markdown(f"""
                    <div style="background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); border-radius:12px; padding:12px; margin:10px 0;">
                      <div style="font-size:11px; font-weight:800; color:#06B6D4;">RECOMMENDED TACTICAL POSTURE: {posture}</div>
                      <div style="font-size:12px; color:#E2E8F0; margin-top:4px;">{posture_advice}</div>
                    </div>
                    <div style="font-size:12.5px; margin-top:12px;">
                      <p>🤝 <strong>Template Overlap ({len(shared_ids)}/11 Starters):</strong> Points from these players cancel out head-to-head.</p>
                      <p style="color:#34D399;">⚔️ <strong>Your Attacking Differentials ({len(my_diffs)}):</strong><br>{my_diff_str}</p>
                      <p style="color:#FB7185;">🛡️ <strong>Rival Threat Differentials ({len(their_diffs)}):</strong><br>{their_diff_str}</p>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No classic mini-leagues found for this Team ID.")

# =========================================================
# TAB 4: CONTEXT-AWARE AI TACTICAL ADVISOR
# =========================================================
with tab_ai:
    st.markdown("""
    <div class="dossier-card" style="padding:16px 20px;">
      <h3 style="margin:0; font-size:17px; font-weight:800; color:#10B981;">🤖 KINGS COUNTY FC AI LINEUP & STRATEGY ADVISOR</h3>
      <p style="margin:4px 0 0 0; font-size:12.5px; color:var(--text-secondary);">
        Grounded in your live GW{gw} squad, £{bank:.1f}m bank balance, 5-GW xP projections, and mini-league gap. Tap a quick-action prompt or ask a custom question.
      </p>
    </div>
    """.format(gw=current_gw, bank=bank_now), unsafe_allow_html=True)

    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [
            {"role": "assistant", "content": f"Welcome to the Tactical Room, Manager. Your Starting XI is projected for **{team_xp_total} xP** in GW{current_gw} with **£{bank_now:.1f}m** in the bank. Select a quick-action analysis below or ask any specific transfer/captaincy question."}
        ]

    # Deterministic Squad-Aware Tactical Engine (Instant, Accurate, Zero Clunkiness)
    def generate_tactical_response(prompt_text):
        q = prompt_text.lower()
        sorted_by_xp = sorted(starting_xi, key=lambda x: x.get("xp_next", 0), reverse=True)
        top_cap = sorted_by_xp[0] if sorted_by_xp else {}
        vc_pick = sorted_by_xp[1] if len(sorted_by_xp) > 1 else {}
        top_sell = sell_rankings[0][1] if sell_rankings else {}

        # Optional Live Gemini / OpenAI API hook if configured in secrets
        gemini_key = st.secrets.get("GEMINI_API_KEY", "")
        if gemini_key:
            try:
                squad_context = ", ".join(f"{p['web_name']} ({p['team_short']}, £{p['now_cost']/10:.1f}m, {p['xp_next']}xP)" for p in full_squad)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"You are the elite FPL Tactical AI for Kings County FC. Current GW: {current_gw}. Bank: £{bank_now:.1f}m. Squad: {squad_context}. Answer concisely with concrete numbers: {prompt_text}"}]}]
                }
                r = requests.post(url, json=payload, timeout=10)
                if r.status_code == 200:
                    return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

        if "captain" in q:
            return (
                f"### ©️ GW{current_gw} Captaincy Matrix\n"
                f"1. **Primary Captain — {top_cap.get('web_name')} ({top_cap.get('team_short')}):** Projected for **{top_cap.get('xp_next')} xP** "
                f"(Form `{top_cap.get('form')}`, xGI `{top_cap.get('expected_goal_involvements')}`). Best combination of minutes security and fixture ceiling.\n"
                f"2. **Vice-Captain — {vc_pick.get('web_name')} ({vc_pick.get('team_short')}):** Projected for **{vc_pick.get('xp_next')} xP**. Safe high-floor pivot.\n"
                f"*Recommendation:* Lock the armband on **{top_cap.get('web_name')}**."
            )
        elif "transfer" in q or "sell" in q or "buy" in q:
            s_cost = top_sell.get("now_cost", 50) / 10.0
            max_b = round(s_cost + bank_now, 1)
            cands = [
                c for c in elements_map.values()
                if c["id"] not in squad_ids and c.get("element_type") == top_sell.get("element_type", 3)
                and (c.get("now_cost", 999) / 10.0) <= max_b
            ]
            cands.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
            best_in = cands[0] if cands else {}
            gain_5 = round(best_in.get("xp_5gw", 0) - top_sell.get("xp_5gw", 0), 1)
            return (
                f"### 🔄 Priority Transfer Directive\n"
                f"* **Transfer OUT:** **{top_sell.get('web_name')} ({top_sell.get('team_short')})** (£{s_cost:.1f}m) — Projected for only **{top_sell.get('xp_next')} xP** next GW with an average 5-GW FDR of `{top_sell.get('avg_5_fdr')}`.\n"
                f"* **Top Target IN:** **{best_in.get('web_name')} ({best_in.get('team_short')})** (£{best_in.get('now_cost', 50)/10:.1f}m) — Delivers **+{gain_5} net xP** over the next 5 Gameweeks while leaving **£{max_b - (best_in.get('now_cost',50)/10):.1f}m** in the bank."
            )
        elif "bench" in q or "lineup" in q:
            outfield_bench = [p for p in bench_xi if p.get("element_type") != 1]
            outfield_bench.sort(key=lambda x: x.get("xp_next", 0), reverse=True)
            order_str = " → ".join(f"**{i+1}. {p['web_name']}** ({p['xp_next']} xP)" for i, p in enumerate(outfield_bench))
            return (
                f"### 🪑 Optimal Auto-Sub Bench Order\n"
                f"Based on GW{current_gw} Expected Points ($xP$), set your outfield bench priority to:\n"
                f"{order_str}\n\n"
                f"*Check:* Ensure no bench player has a higher $xP$ than your lowest projected starter (**{sorted_by_xp[-1].get('web_name')}** at `{sorted_by_xp[-1].get('xp_next')} xP`)."
            )
        else:
            return (
                f"### 📊 Executive Tactical Summary (GW{current_gw})\n"
                f"* **Projected Starting XI Score:** `{team_xp_total} pts`\n"
                f"* **Optimal Captain:** **{top_cap.get('web_name')}** (`{top_cap.get('xp_next')} xP`)\n"
                f"* **Weakest Starting Link:** **{sorted_by_xp[-1].get('web_name')}** (`{sorted_by_xp[-1].get('xp_next')} xP`)\n"
                f"* **Available War Chest:** `£{bank_now:.1f}m` in bank (`£{val_now:.1f}m` total squad value)."
            )

    # Quick-Action Chips
    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("👑 Optimal Captaincy", use_container_width=True):
        prompt = "Who should I captain and vice-captain this week?"
        st.session_state["ai_messages"].append({"role": "user", "content": prompt})
        st.session_state["ai_messages"].append({"role": "assistant", "content": generate_tactical_response(prompt)})
        st.rerun()
    if qa2.button("🔄 Best Transfer Move", use_container_width=True):
        prompt = "What is my highest-value transfer move within budget?"
        st.session_state["ai_messages"].append({"role": "user", "content": prompt})
        st.session_state["ai_messages"].append({"role": "assistant", "content": generate_tactical_response(prompt)})
        st.rerun()
    if qa3.button("🪑 Audit Bench Order", use_container_width=True):
        prompt = "How should I order my bench for auto-subs?"
        st.session_state["ai_messages"].append({"role": "user", "content": prompt})
        st.session_state["ai_messages"].append({"role": "assistant", "content": generate_tactical_response(prompt)})
        st.rerun()
    if qa4.button("📊 Full GW Briefing", use_container_width=True):
        prompt = "Give me a full tactical summary for this gameweek."
        st.session_state["ai_messages"].append({"role": "user", "content": prompt})
        st.session_state["ai_messages"].append({"role": "assistant", "content": generate_tactical_response(prompt)})
        st.rerun()

    for msg in st.session_state["ai_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Ask about specific player comparisons, -4pt hits, or mini-league strategy...")
    if user_q:
        st.session_state["ai_messages"].append({"role": "user", "content": user_q})
        st.session_state["ai_messages"].append({"role": "assistant", "content": generate_tactical_response(user_q)})
        st.rerun()

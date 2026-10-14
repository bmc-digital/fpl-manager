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
        flag_badge

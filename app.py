"""
KINGS COUNTY FC — FPL TACTICAL COMMAND & MINI-LEAGUE INTELLIGENCE
Production Mobile-First Architecture | Full Tactical Pitch View | Gemini 3.8 Flash Co-Pilot
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & ZERO-INDENT HTML RENDERER
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kings County FC | Tactical Command",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def render_html(html_str: str):
    cleaned = "\n".join(line.lstrip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PARENT-DOM CROWN REMOVER + MOBILE-FIRST CSS DESIGN SYSTEM
# ---------------------------------------------------------
components.html(
    "<script>"
    "(function() {"
    "  function nukeBadges() {"
    "    try {"
    "      const parentDoc = window.parent.document;"
    "      const selectors = ['[class*=\"viewerBadge\"]','[class*=\"profileContainer\"]','[data-testid=\"manage-app-button\"]','[data-testid=\"stStatusWidget\"]','footer','#MainMenu'];"
    "      selectors.forEach(sel => {"
    "        parentDoc.querySelectorAll(sel).forEach(el => {"
    "          el.style.display = 'none'; el.style.visibility = 'hidden'; el.style.opacity = '0'; el.style.pointerEvents = 'none';"
    "        });"
    "      });"
    "    } catch (e) {}"
    "  }"
    "  nukeBadges(); setInterval(nukeBadges, 1000);"
    "})();"
    "</script>",
    height=0,
)

CSS_LINES = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');",
    ":root {",
    "  --bg-base: #070B12; --bg-surface: #0F172A; --bg-elevated: #1E293B;",
    "  --border-subtle: rgba(255, 255, 255, 0.08); --accent-emerald: #10B981;",
    "  --accent-neon: #00FF85; --accent-cyan: #06B6D4; --accent-amber: #F59E0B;",
    "  --accent-rose: #F43F5E; --text-primary: #F8FAFC; --text-secondary: #94A3B8;",
    "  --fdr-1: #059669; --fdr-2: #10B981; --fdr-3: #475569; --fdr-4: #D97706; --fdr-5: #E11D48;",
    "}",
    "html, body, [class*='css'] { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; color: var(--text-primary); background-color: var(--bg-base); scroll-behavior: smooth; }",
    ".stApp { background: radial-gradient(circle at 50% 0%, #132238 0%, #070B12 62%); }",
    "#MainMenu, header, footer, [data-testid='stHeader'], [data-testid='stToolbar'], [data-testid='stDecoration'], [data-testid='stStatusWidget'], [data-testid='manage-app-button'], .stAppToolbar, .stDeployButton, div[class*='viewerBadge'], a[class*='viewerBadge'], div[class*='profileContainer'], iframe[title='streamlit_badge'] { visibility: hidden !important; display: none !important; height: 0 !important; width: 0 !important; opacity: 0 !important; pointer-events: none !important; }",
    "iframe[height='0'] { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }",
    ".block-container { padding-top: 0.6rem !important; padding-bottom: 2.5rem !important; max-width: 1280px !important; }",
    ".kcfc-hero { background: linear-gradient(135deg, rgba(16, 185, 129, 0.16) 0%, rgba(15, 23, 42, 0.96) 50%, rgba(6, 182, 212, 0.12) 100%); border: 1px solid rgba(0, 255, 133, 0.35); border-radius: 22px; padding: 20px 22px 16px 22px; margin-bottom: 8px; display: flex; flex-direction: column; gap: 14px; box-shadow: 0 14px 36px rgba(0, 0, 0, 0.55); }",
    ".kcfc-hero-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; width: 100%; }",
    ".kcfc-hero-brand { display: flex; align-items: center; gap: 16px; }",
    ".kcfc-emblem { width: 58px; height: 58px; border-radius: 16px; background: linear-gradient(135deg, #00FF85 0%, #10B981 100%); border: 2px solid #FFFFFF; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 22px rgba(0, 255, 133, 0.35); }",
    ".kcfc-hero-title { font-size: 26px; font-weight: 900; letter-spacing: 0.8px; color: #FFFFFF; margin: 0; line-height: 1.08; text-transform: uppercase; }",
    ".kcfc-hero-sub { font-size: 11px; font-weight: 800; color: #00FF85; letter-spacing: 1.6px; text-transform: uppercase; margin-top: 4px; }",
    ".countdown-bar { width: 100%; background: rgba(7, 11, 18, 0.9); border: 1px solid rgba(0, 255, 133, 0.4); border-radius: 14px; padding: 10px 18px; display: flex; align-items: center; justify-content: space-between; gap: 12px; box-shadow: inset 0 0 18px rgba(0, 255, 133, 0.08); }",
    ".countdown-left { display: flex; align-items: center; gap: 8px; }",
    ".pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: #00FF85; box-shadow: 0 0 10px #00FF85; }",
    ".countdown-lbl { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; color: #E2E8F0; }",
    ".countdown-val { font-size: 17px; font-weight: 800; color: #00FF85; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; }",
    ".kpi-grid-6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 16px; }",
    "@media (max-width: 992px) { .kpi-grid-6 { grid-template-columns: repeat(3, 1fr); } }",
    "@media (max-width: 640px) { .kpi-grid-6 { grid-template-columns: repeat(2, 1fr); } }",
    ".kpi-card { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 16px; padding: 13px 15px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28); display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between; }",
    ".kpi-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-secondary); margin-bottom: 4px; }",
    ".kpi-value { font-size: 21px; font-weight: 800; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; line-height: 1.15; margin-bottom: 7px; }",
    ".kpi-delta { font-size: 10px; font-weight: 700; padding: 3px 7px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; display: inline-block; width: fit-content; }",
    ".delta-up { background: rgba(16, 185, 129, 0.16); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }",
    ".delta-down { background: rgba(244, 63, 94, 0.16); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.3); }",
    ".delta-warn { background: rgba(245, 158, 11, 0.16); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }",
    ".delta-neutral { background: rgba(148, 163, 184, 0.14); color: #CBD5E1; }",
    ".pitch-wrapper { background: radial-gradient(circle at 50% 50%, #154D2E 0%, #0E351F 62%, #082012 100%); border: 2px solid rgba(255, 255, 255, 0.22); border-radius: 24px; padding: 20px 8px 18px 8px; box-shadow: inset 0 0 65px rgba(0, 0, 0, 0.65), 0 14px 36px rgba(0, 0, 0, 0.5); position: relative; background-image: linear-gradient(to bottom, transparent 49.5%, rgba(255,255,255,0.16) 49.5%, rgba(255,255,255,0.16) 50.5%, transparent 50.5%), radial-gradient(circle at 50% 50%, transparent 52px, rgba(255,255,255,0.16) 53px, rgba(255,255,255,0.16) 55px, transparent 56px), linear-gradient(to right, transparent 22%, rgba(255,255,255,0.12) 22%, rgba(255,255,255,0.12) 78%, transparent 78%), radial-gradient(circle at 50% 50%, #165231 0%, #0D331D 68%, #071C10 100%); background-size: 100% 100%, 100% 100%, 100% 14%, 100% 100%; background-repeat: no-repeat; margin-bottom: 14px; }",
    ".pitch-row { display: flex; justify-content: space-around; align-items: stretch; gap: 6px; margin-bottom: 14px; flex-wrap: nowrap; }",
    ".pitch-row:last-child { margin-bottom: 0; }",
    "a.pitch-node-link { text-decoration: none !important; color: inherit !important; flex: 1 1 0; max-width: 122px; min-width: 64px; display: flex; }",
    ".pitch-node { width: 100%; background: rgba(11, 17, 30, 0.90); backdrop-filter: blur(8px); border: 1.5px solid rgba(255, 255, 255, 0.16); border-radius: 15px; padding: 8px 4px 6px 4px; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.55); transition: transform 0.15s ease, border-color 0.15s ease; cursor: pointer; }",
    ".pitch-node:hover { transform: translateY(-2px); border-color: #00FF85; }",
    ".pitch-node.selected { border: 2px solid #00FF85; box-shadow: 0 0 20px rgba(0, 255, 133, 0.55); }",
    ".node-avatar-wrap { position: relative; width: 58px; height: 58px; margin-bottom: 5px; }",
    ".node-avatar-circle { width: 58px; height: 58px; border-radius: 50%; background-color: #0B111E; background-size: cover, cover, 84% 84%; background-position: top center, top center, center center; background-repeat: no-repeat; border: 2px solid rgba(255, 255, 255, 0.32); box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5); }",
    ".badge-cap { position: absolute; bottom: -2px; right: -4px; background: #FBBF24; color: #000; font-size: 9.5px; font-weight: 900; padding: 1px 5px; border-radius: 6px; border: 1.5px solid #FFF; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }",
    ".badge-vc { position: absolute; bottom: -2px; right: -4px; background: #CBD5E1; color: #000; font-size: 9.5px; font-weight: 900; padding: 1px 5px; border-radius: 6px; border: 1.5px solid #FFF; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }",
    ".badge-flag { position: absolute; top: -3px; left: -4px; background: var(--accent-rose); color: #FFF; font-size: 8.5px; font-weight: 800; padding: 1px 5px; border-radius: 5px; }",
    ".badge-sub { position: absolute; top: -3px; left: -4px; background: #334155; color: #F8FAFC; font-size: 8.5px; font-weight: 800; padding: 1px 5px; border-radius: 5px; }",
    ".node-name { font-size: 11.5px; font-weight: 800; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 96%; line-height: 1.2; }",
    ".node-meta { font-size: 10px; color: #CBD5E1; font-family: 'JetBrains Mono', monospace; margin: 2px 0 4px 0; }",
    ".fdr-pill { font-size: 9.5px; font-weight: 800; padding: 2px 5px; border-radius: 5px; width: 92%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }",
    ".fdr-1 { background: var(--fdr-1); color: #FFF; } .fdr-2 { background: var(--fdr-2); color: #052E16; } .fdr-3 { background: var(--fdr-3); color: #F8FAFC; } .fdr-4 { background: var(--fdr-4); color: #FFF; } .fdr-5 { background: var(--fdr-5); color: #FFF; }",
    ".node-dossier-btn { font-size: 9.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; background: rgba(0, 255, 133, 0.12); color: #00FF85; border: 1px solid rgba(0, 255, 133, 0.35); border-radius: 6px; padding: 2px 0; width: 92%; transition: all 0.15s ease; }",
    ".pitch-node:hover .node-dossier-btn { background: #00FF85; color: #070B12; }",
    ".bench-tray { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 18px; padding: 14px 10px; margin-bottom: 18px; }",
    ".bench-label { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-secondary); margin-bottom: 10px; display: flex; justify-content: space-between; }",
    ".dossier-card { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 20px; padding: 18px 20px; box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35); margin-bottom: 16px; }",
    ".dossier-top { display: flex; align-items: center; gap: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--border-subtle); margin-bottom: 14px; }",
    ".dossier-avatar-circle { width: 92px; height: 92px; border-radius: 50%; flex-shrink: 0; background-color: #070B12; background-size: cover, cover, 82% 82%; background-position: top center, top center, center center; background-repeat: no-repeat; border: 3px solid #00FF85; box-shadow: 0 6px 20px rgba(0, 255, 133, 0.25); }",
    ".stat-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 10px; }",
    "@media (max-width: 640px) { .stat-grid-4 { grid-template-columns: repeat(2, 1fr); } }",
    ".stat-box { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 9px 11px; }",
    ".stat-box-lbl { font-size: 9.5px; color: var(--text-secondary); text-transform: uppercase; font-weight: 700; }",
    ".stat-box-val { font-size: 15.5px; font-weight: 800; color: #FFF; font-family: 'JetBrains Mono', monospace; margin-top: 2px; }",
    ".runway-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }",
    ".sell-banner { background: linear-gradient(90deg, rgba(244, 63, 94, 0.11) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 16px; padding: 16px; margin-bottom: 16px; }",
    ".buy-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }",
    "@media (max-width: 768px) { .buy-grid-3 { grid-template-columns: 1fr; } }",
    ".buy-card { background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 12px; padding: 12px; }",
    ".upgrade-card { background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 12px; padding: 12px; margin-top: 10px; }",
    ".ml-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }",
    ".ml-table th { text-align: left; padding: 9px 10px; font-size: 10.5px; text-transform: uppercase; color: var(--text-secondary); border-bottom: 1px solid var(--border-subtle); }",
    ".ml-table td { padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }",
    ".ml-row-me { background: rgba(0, 255, 133, 0.11); font-weight: 700; }",
    ".stTabs [data-baseweb='tab-list'] { gap: 6px; background-color: var(--bg-surface); padding: 6px; border-radius: 14px; border: 1px solid var(--border-subtle); }",
    ".stTabs [data-baseweb='tab'] { border-radius: 10px; padding: 8px 16px; font-weight: 700; font-size: 12.5px; color: var(--text-secondary); }",
    ".stTabs [aria-selected='true'] { background-color: var(--bg-elevated) !important; color: #00FF85 !important; }",
    "div.stButton > button { background: var(--bg-elevated) !important; color: var(--text-primary) !important; border: 1px solid rgba(0, 255, 133, 0.28) !important; border-radius: 10px !important; font-size: 11.5px !important; font-weight: 700 !important; padding: 5px 12px !important; min-height: 32px !important; }",
    "div.stButton > button:hover { background: #00FF85 !important; color: #070B12 !important; border-color: #00FF85 !important; }",
    "</style>"
]
render_html("\n".join(CSS_LINES))

# ---------------------------------------------------------
# 3. AUTHENTICATION, SYNC TIMESTAMP & TEAM ID INITIALIZATION
# ---------------------------------------------------------
auth_secret = st.secrets.get("APP_PASSWORD", "fpl2025")
default_team_id = int(st.secrets.get("DEFAULT_TEAM_ID", 1575281))

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = (st.query_params.get("auth") == "passed")

if "team_id" not in st.session_state:
    q_tid = st.query_params.get("team_id")
    st.session_state["team_id"] = int(q_tid) if q_tid and str(q_tid).isdigit() else default_team_id

if "sync_nonce" not in st.session_state:
    st.session_state["sync_nonce"] = 0

if "last_synced_str" not in st.session_state:
    st.session_state["last_synced_str"] = datetime.now(ZoneInfo("America/New_York")).strftime("%I:%M:%S %p EDT")

if "cap_override_id" not in st.session_state:
    st.session_state["cap_override_id"] = None

if "vc_override_id" not in st.session_state:
    st.session_state["vc_override_id"] = None

q_pid = st.query_params.get("pid")
if q_pid and str(q_pid).isdigit():
    st.session_state["selected_pid"] = int(q_pid)

if not st.session_state["authenticated"]:
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        render_html(
            "<div class='dossier-card' style='text-align: center; margin-top: 40px;'>"
            "<h2 style='margin:0; font-weight:900; color:#FFF; letter-spacing:0.8px;'>KINGS COUNTY FC</h2>"
            "<p style='color:#00FF85; font-size:11.5px; font-weight:800; letter-spacing:1.6px; margin-top:4px;'>"
            "FPL TACTICAL COMMAND & MINI-LEAGUE ENGINE</p></div>"
        )
        with st.form("auth_form"):
            pw = st.text_input("Manager Access Key", type="password")
            tid = st.number_input("FPL Entry ID", value=st.session_state["team_id"], step=1)
            if st.form_submit_button("Launch Tactical Command", use_container_width=True):
                if pw == auth_secret or auth_secret == "":
                    st.session_state["authenticated"] = True
                    st.session_state["team_id"] = int(tid)
                    st.query_params["auth"] = "passed"
                    st.query_params["team_id"] = str(tid)
                    st.rerun()
                else:
                    st.error("Invalid Manager Access Key.")
    st.stop()

# ---------------------------------------------------------
# 4. CLUB KIT SVG GENERATOR & MULTI-LAYER PHOTO URL BUILDER
# ---------------------------------------------------------
CLUB_PALETTES = {
    "ARS": {"p": "#EF0107", "s": "#FFFFFF"},
    "AVL": {"p": "#670E36", "s": "#95BFE5"},
    "BOU": {"p": "#DA291C", "s": "#000000"},
    "BRE": {"p": "#E30613", "s": "#FFFFFF"},
    "BHA": {"p": "#0057B8", "s": "#FFFFFF"},
    "BUR": {"p": "#6C1D45", "s": "#99D6EA"},
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
    "SHU": {"p": "#EE2737", "s": "#FFFFFF"},
    "SOU": {"p": "#D71920", "s": "#FFFFFF"},
    "SUN": {"p": "#EB172B", "s": "#FFFFFF"},
    "TOT": {"p": "#FFFFFF", "s": "#132257"},
    "WHU": {"p": "#7A263A", "s": "#1BB1E7"},
    "WOL": {"p": "#FDB913", "s": "#231F20"},
    "DEFAULT": {"p": "#1E293B", "s": "#00FF85"}
}

def generate_svg_kit(team_short, is_gk=False):
    colors = CLUB_PALETTES.get(str(team_short).upper(), CLUB_PALETTES["DEFAULT"])
    p_col = "#10B981" if is_gk else colors["p"]
    s_col = "#090D16" if is_gk else colors["s"]
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'>"
        f"<path d='M25,18 L10,32 L20,40 L26,33 L26,65 L54,65 L54,33 L60,40 L70,32 L55,18 C50,23 30,23 25,18 Z' "
        f"fill='{p_col}' stroke='{s_col}' stroke-width='2'/>"
        f"<text x='40' y='49' font-family='sans-serif' font-weight='800' font-size='11' "
        f"fill='{s_col}' text-anchor='middle'>{str(team_short)[:3]}</text></svg>"
    )
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

def build_avatar_bg_style(p) -> str:
    raw_code = str(p.get("code") or p.get("photo", "").split(".")[0]).lstrip("p").strip()
    url_25 = f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{raw_code}.png"
    url_legacy = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{raw_code}.png"
    fallback_svg = generate_svg_kit(p.get("team_short", "EPL"), is_gk=(p.get("element_type") == 1))
    return f"background-image: url('{url_25}'), url('{url_legacy}'), url(\"{fallback_svg}\");"

# ---------------------------------------------------------
# 5. UNIVERSAL FPL API ENGINE (ROBUST FALLBACK + DIAGNOSTICS)
# ---------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

@st.cache_data(ttl=180)
def fetch_bootstrap(nonce=0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/bootstrap-static/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=180)
def fetch_fixtures(nonce=0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/fixtures/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_private_my_team(tid, raw_cookie_or_token="", fpl_token="", fpl_email="", fpl_password="", nonce=0):
    diag = {
        "attempted": False,
        "authenticated": False,
        "status_code": 200,
        "method_used": "Public Transfer Roll-Forward",
        "message": "Using robust public transfer roll-forward (No active session cookie required)."
    }
    return None, diag

@st.cache_data(ttl=60)
def fetch_manager_full(tid, nonce=0):
    try:
        r_ent = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/?_={nonce}", headers=HEADERS, timeout=8)
        r_hist = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/history/?_={nonce}", headers=HEADERS, timeout=8)
        r_tr = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/transfers/?_={nonce}", headers=HEADERS, timeout=8)
        entry = r_ent.json() if r_ent.status_code == 200 else {}
        history = r_hist.json() if r_hist.status_code == 200 else {}
        transfers = r_tr.json() if r_tr.status_code == 200 else []
        curr_gw = entry.get("current_event") or 6
        r_picks = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/event/{curr_gw}/picks/?_={nonce}", headers=HEADERS, timeout=8)
        picks = r_picks.json() if r_picks.status_code == 200 else {}
        return entry, history, transfers, picks, int(curr_gw)
    except Exception:
        return {}, {}, [], {}, 6

@st.cache_data(ttl=300)
def fetch_event_live(gw, nonce=0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/event/{gw}/live/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=120)
def fetch_league_standings(league_id, nonce=0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=120)
def fetch_rival_picks(rival_tid, gw, nonce=0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/entry/{rival_tid}/event/{gw}/picks/?_={nonce}", headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

sync_nonce = st.session_state["sync_nonce"]
bootstrap = fetch_bootstrap(sync_nonce) or {"elements": [], "teams": [], "events": []}
fixtures_list = fetch_fixtures(sync_nonce)
team_id = st.session_state.get("team_id", default_team_id)
entry_data, history_data, transfers_list, public_picks_data, last_active_gw = fetch_manager_full(team_id, sync_nonce)

fpl_cookie_val = (
    st.session_state.get("custom_fpl_cookie")
    or st.secrets.get("FPL_COOKIE", "")
    or st.secrets.get("FLP_COOKIE", "")
)
fpl_token_val = st.session_state.get("custom_fpl_token") or st.secrets.get("FPL_BEARER_TOKEN", "")
fpl_email_val = st.session_state.get("custom_fpl_email") or st.secrets.get("FPL_EMAIL", "")
fpl_pass_val = st.session_state.get("custom_fpl_password") or st.secrets.get("FPL_PASSWORD", "")

private_team_data, auth_diag = fetch_private_my_team(
    team_id,
    raw_cookie_or_token=fpl_cookie_val,
    fpl_token=fpl_token_val,
    fpl_email=fpl_email_val,
    fpl_password=fpl_pass_val,
    nonce=sync_nonce
)

elements_map = {p["id"]: p for p in bootstrap.get("elements", [])}
teams_map = {t["id"]: t for t in bootstrap.get("teams", [])}
events_list = bootstrap.get("events", [])
events_map = {e["id"]: e for e in events_list}

# ---------------------------------------------------------
# 6. NEXT GAMEWEEK DEADLINE COUNTDOWN ENGINE
# ---------------------------------------------------------
next_event_obj = next((e for e in events_list if e.get("is_next")), None)
if not next_event_obj:
    next_event_obj = next((e for e in events_list if not e.get("finished")), events_map.get(last_active_gw, {}))

upcoming_gw = next_event_obj.get("id", last_active_gw + 1)
deadline_iso = next_event_obj.get("deadline_time")

countdown_display = f"GW{upcoming_gw} UPCOMING"
if deadline_iso:
    try:
        dl_dt = datetime.fromisoformat(deadline_iso.replace("Z", "+00:00"))
        now_utc = datetime.now(timezone.utc)
        diff_sec = (dl_dt - now_utc).total_seconds()
        if diff_sec > 86400:
            days = int(diff_sec // 86400)
            hours = int((diff_sec % 86400) // 3600)
            countdown_display = f"{days}d {hours}h remaining"
        elif diff_sec > 0:
            hours = int(diff_sec // 3600)
            mins = int((diff_sec % 3600) // 60)
            countdown_display = f"{hours}h {mins}m remaining"
        else:
            countdown_display = "LOCKED / IN PROGRESS"
    except Exception:
        pass

team_runway = {t_id: [] for t_id in teams_map}
for fix in fixtures_list:
    ev = fix.get("event")
    if not fix.get("finished") and ev and ev >= upcoming_gw:
        h_id, a_id = fix["team_h"], fix["team_a"]
        h_short = teams_map.get(h_id, {}).get("short_name", "TBD")
        a_short = teams_map.get(a_id, {}).get("short_name", "TBD")
        if h_id in team_runway and len(team_runway[h_id]) < 5:
            team_runway[h_id].append({"gw": ev, "opp": a_short, "venue": "H", "fdr": fix.get("team_h_difficulty", 3)})
        if a_id in team_runway and len(team_runway[a_id]) < 5:
            team_runway[a_id].append({"gw": ev, "opp": h_short, "venue": "A", "fdr": fix.get("team_a_difficulty", 3)})

# ---------------------------------------------------------
# 7. SELF-CALIBRATING HISTORICAL LEARNING & SELL PRICE ENGINE
# ---------------------------------------------------------
live_last_gw = fetch_event_live(last_active_gw, sync_nonce)
live_pts_map = {}
if live_last_gw and "elements" in live_last_gw:
    for el in live_last_gw["elements"]:
        live_pts_map[el["id"]] = el.get("stats", {}).get("total_points", 0)

top_actual = sorted(elements_map.values(), key=lambda x: live_pts_map.get(x["id"], 0), reverse=True)[:25]
avg_top_form = sum(float(p.get("form") or 0) for p in top_actual) / max(len(top_actual), 1)
avg_top_xgi = sum(float(p.get("expected_goal_involvements") or 0) for p in top_actual) / max(len(top_actual), 1)

w_form = 0.58 if avg_top_form >= 5.0 else 0.46
w_xgi = 4.4 if avg_top_xgi >= 2.2 else 3.8
calibration_note = f"Calibrated on GW{last_active_gw} actuals: Form Weight {int(w_form*100)}% | xGI Multiplier {w_xgi}x"

purchase_price_map = {}
for tr in transfers_list:
    el_in = tr.get("element_in")
    cost_in = tr.get("element_in_cost")
    if el_in and cost_in:
        purchase_price_map[el_in] = cost_in

def estimate_selling_price(p):
    pid = p["id"]
    now_c = p.get("now_cost", 50)
    if pid in purchase_price_map:
        buy_c = purchase_price_map[pid]
    else:
        buy_c = now_c - p.get("cost_change_start", 0)
    if now_c > buy_c:
        profit = (now_c - buy_c) // 2
        return (buy_c + profit) / 10.0
    return now_c / 10.0

def compute_player_xp(p):
    form = float(p.get("form") or 0.0)
    xgi = float(p.get("expected_goal_involvements") or 0.0)
    mins = max(p.get("minutes", 0), 1)
    xgi_per_90 = (xgi / mins) * 90 if mins >= 90 else form * 0.12
    runway = team_runway.get(p.get("team"), [])
    next_fdr = runway[0]["fdr"] if runway else 3
    avg_5_fdr = sum(r["fdr"] for r in runway[:5]) / len(runway[:5]) if runway else 3.0
    chance = (p.get("chance_of_playing_next_round") if p.get("chance_of_playing_next_round") is not None else 100) / 100.0

    fdr_mult = {1: 1.35, 2: 1.2, 3: 1.0, 4: 0.82, 5: 0.68}.get(next_fdr, 1.0)
    xp_next = round(((form * w_form) + (xgi_per_90 * w_xgi) + 1.8) * fdr_mult * chance, 1)
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
    p_obj["last_gw_pts"] = live_pts_map.get(pid, p_obj.get("event_points", 0))
    p_obj["selling_price"] = estimate_selling_price(p_obj)

# ---------------------------------------------------------
# 8. PERSISTENT STATE + SQUAD ROLL-FORWARD ENGINE
# ---------------------------------------------------------
if "persisted_squad_state" not in st.session_state:
    st.session_state["persisted_squad_state"] = None

starting_xi, bench_xi = [], []
cap_override = st.session_state.get("cap_override_id")
vc_override = st.session_state.get("vc_override_id")

if st.session_state["persisted_squad_state"]:
    active_picks_source = st.session_state["persisted_squad_state"]
    roster_sync_mode = f"CACHED & PERSISTED GW{upcoming_gw} SQUAD"
    roster_mode_cls = "delta-up"
else:
    raw_picks = [dict(pk) for pk in public_picks_data.get("picks", [])]
    gw_transfers = [t for t in reversed(transfers_list) if t.get("event") == upcoming_gw]
    for tr in gw_transfers:
        out_el = tr.get("element_out")
        in_el = tr.get("element_in")
        for pk in raw_picks:
            if pk.get("element") == out_el and in_el in elements_map:
                pk["element"] = in_el
                break
    active_picks_source = raw_picks
    roster_sync_mode = f"PUBLIC GW{last_active_gw} + ROLL-FORWARD"
    roster_mode_cls = "delta-warn"

api_official_cap_name = "Unknown"
api_official_vc_name = "Unknown"

for pk in active_picks_source:
    base_p = elements_map.get(pk["element"])
    if base_p:
        p_copy = dict(base_p)
        pid = p_copy["id"]

        if pk.get("is_captain"):
            api_official_cap_name = p_copy.get("web_name", "Unknown")
        if pk.get("is_vice_captain"):
            api_official_vc_name = p_copy.get("web_name", "Unknown")

        if "selling_price" in pk:
            p_copy["selling_price"] = pk["selling_price"] / 10.0
            elements_map[pid]["selling_price"] = p_copy["selling_price"]

        if cap_override is not None:
            p_copy["is_captain"] = (pid == cap_override)
        else:
            p_copy["is_captain"] = pk.get("is_captain", False)

        if vc_override is not None:
            p_copy["is_vice_captain"] = (pid == vc_override and not p_copy["is_captain"])
        else:
            p_copy["is_vice_captain"] = (pk.get("is_vice_captain", False) and not p_copy["is_captain"])

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
# 9. CALCULATE FREE TRANSFERS, BANK & MINI-LEAGUE TELEMETRY
# ---------------------------------------------------------
curr_hist = history_data.get("current", [])
chips_used = {c.get("event"): c.get("name") for c in history_data.get("chips", [])}
gw_avg = events_map.get(last_active_gw, {}).get("average_entry_score", 50)

ft_available = 1
for h_row in curr_hist:
    ev_num = h_row.get("event", 1)
    if ev_num == 1:
        ft_available = 1
        continue
    used_tr = h_row.get("event_transfers", 0)
    chip_in_gw = chips_used.get(ev_num)
    if chip_in_gw in ("wildcard", "freehit"):
        ft_available = min(5, max(1, ft_available))
    else:
        ft_available = min(5, max(0, ft_available - used_tr) + 1)

upcoming_gw_transfers = [t for t in transfers_list if t.get("event") == upcoming_gw]
ft_remaining_now = max(0, ft_available - len(upcoming_gw_transfers))

if len(curr_hist) >= 2:
    latest_h = curr_hist[-1]
    prev_h = curr_hist[-2]
    total_pts = latest_h.get("total_points", 0)
    gw_pts = latest_h.get("points", 0)
    overall_rank = latest_h.get("overall_rank", 0)
    rank_delta = prev_h.get("overall_rank", overall_rank) - overall_rank
    bank_now = latest_h.get("bank", 0) / 10.0
    bank_delta = (latest_h.get("bank", 0) - prev_h.get("bank", 0)) / 10.0
    val_now = latest_h.get("value", 1000) / 10.0
    val_delta = (latest_h.get("value", 1000) - prev_h.get("value", 1000)) / 10.0
elif len(curr_hist) == 1:
    latest_h = curr_hist[0]
    total_pts, gw_pts = latest_h.get("total_points", 0), latest_h.get("points", 0)
    overall_rank, rank_delta = latest_h.get("overall_rank", 0), 0
    bank_now, bank_delta = latest_h.get("bank", 0) / 10.0, 0.0
    val_now, val_delta = latest_h.get("value", 1000) / 10.0, 0.0
else:
    total_pts = entry_data.get("summary_overall_points", 407)
    gw_pts = entry_data.get("summary_event_points", 60)
    overall_rank, rank_delta = entry_data.get("summary_overall_rank", 1219150), 0
    bank_now, bank_delta = (entry_data.get("last_deadline_bank", 1) or 1) / 10.0, 0.0
    val_now, val_delta = (entry_data.get("last_deadline_value", 1009) or 1009) / 10.0, 0.0

team_xp_total = round(sum(
    p["xp_next"] * (2 if p.get("is_captain") else 1) for p in starting_xi
), 1)

starter_flags = [p for p in starting_xi if p.get("chance_of_playing_next_round") is not None and p.get("chance_of_playing_next_round") < 75]
weak_starters = [p for p in starting_xi if p.get("element_type") != 1 and p.get("xp_next", 0) < 3.4]
if starter_flags or len(weak_starters) >= 2 or ft_remaining_now >= 2:
    ft_rec_text = "USE FT (UPGRADE XI)"
    ft_rec_cls = "delta-up"
else:
    ft_rec_text = "HOLD / ROLL FT"
    ft_rec_cls = "delta-warn"

classic_leagues = [
    lg for lg in entry_data.get("leagues", {}).get("classic", [])
    if lg.get("league_type") == "x" or lg.get("id", 0) > 350
]
if not classic_leagues:
    classic_leagues = entry_data.get("leagues", {}).get("classic", [])

target_league_standings = []
rival_threat_players = {}
rival_ownership_set = set()
gap_to_leader = 0
target_league_name = "Global Overall"

if classic_leagues:
    lg_ids = [lg["id"] for lg in classic_leagues]
    saved_lg_id = st.session_state.get("target_lg_id") or int(st.query_params.get("lg_id", lg_ids[0]))
    if saved_lg_id not in lg_ids:
        saved_lg_id = lg_ids[0]
    st.session_state["target_lg_id"] = saved_lg_id
    target_league_name = next((lg["name"] for lg in classic_leagues if lg["id"] == saved_lg_id), "Mini-League")

    st_json = fetch_league_standings(saved_lg_id, sync_nonce)
    if st_json:
        target_league_standings = st_json.get("standings", {}).get("results", [])
        if target_league_standings:
            leader_total = target_league_standings[0]["total"]
            my_entry_row = next((r for r in target_league_standings if r["entry"] == team_id), None)
            my_league_pts = my_entry_row["total"] if my_entry_row else total_pts
            gap_to_leader = leader_total - my_league_pts

            top_rivals = [r for r in target_league_standings[:4] if r["entry"] != team_id][:3]
            for rv in top_rivals:
                rv_picks = fetch_rival_picks(rv["entry"], last_active_gw, sync_nonce)
                if rv_picks and "picks" in rv_picks:
                    for pk in rv_picks["picks"]:
                        if pk.get("position", 1) <= 11:
                            el_id = pk["element"]
                            rival_ownership_set.add(el_id)
                            rival_threat_players[el_id] = rival_threat_players.get(el_id, 0) + 1

# ---------------------------------------------------------
# 10. RENDER CLEAN TOP AREA: HERO BANNER + 1-LINE SYNC BAR + 6 KPI TILES
# ---------------------------------------------------------
pl_vector_svg = (
    '<div class="kcfc-emblem">'
    '<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M34 25 L29 14 L38 18 L36 7 L45 14 L50 5 L55 15 L62 6 L61 17 L68 11 L64 22 Q50 18 34 25 Z" stroke="#070B12" stroke-width="3.8" stroke-linejoin="round" fill="none"/>'
    '<path d="M36 27 Q52 21 63 24 L60 19 Q50 22 36 27 Z" fill="#070B12"/>'
    '<path d="M38 28 C48 24 62 24 62 28 C64 25 71 29 73 36 C70 33 65 30 64 33 C59 29 48 29 45 34 C48 35 42 36 41 38 C44 38 45 43 49 44 C55 45 61 45 62 45 C58 39 50 39 47 38 C51 35 55 38 59 36 C59 40 62 43 65 44 C70 43 72 43 73 44 C70 39 66 37 68 36 C72 37 76 38 74 41 C75 42 76 40 77 41 C83 52 85 62 81 74 C79 72 78 70 77 73 C75 84 71 89 65 92 C64 90 64 87 63 89 C55 94 45 94 36 90 C38 82 37 74 36 70 C33 74 29 79 26 81 C22 76 22 67 23 59 C20 60 17 61 17 60 C19 52 22 46 25 42 C23 42 20 43 21 41 C24 35 28 31 32 29 C30 33 32 38 35 38 C33 34 34 30 39 30 C41 30 41 28 38 28 Z" stroke="#070B12" stroke-width="3.8" stroke-linejoin="round" fill="none"/>'
    '<path d="M55 52 L64 47 L69 50 L69 55 L64 59 L58 60 Z" stroke="#070B12" stroke-width="3.8" stroke-linejoin="round" fill="none"/>'
    '<path d="M72 51 L75 48 L76 55 L75 59 L72 55 Z" stroke="#070B12" stroke-width="3.5" stroke-linejoin="round" fill="none"/>'
    '<path d="M60 64 L68 59 L72 59 L74 63 L72 68 L69 70 L69 65 L63 68 Z" stroke="#070B12" stroke-width="3.6" stroke-linejoin="round" fill="none"/>'
    '</svg></div>'
)

rank_arrow = f"▲ {abs(rank_delta):,} vs LW" if rank_delta > 0 else (f"▼ {abs(rank_delta):,} vs LW" if rank_delta < 0 else "━ No Change")
rank_cls = "delta-up" if rank_delta >= 0 else "delta-down"

gw_vs_avg = gw_pts - gw_avg
gw_cls = "delta-up" if gw_vs_avg >= 0 else "delta-down"
gw_delta_str = f"GW{last_active_gw}: {gw_pts}p ({'+' if gw_vs_avg >= 0 else ''}{gw_vs_avg} vs Avg)"

val_cls = "delta-up" if val_delta >= 0 else "delta-down"
val_delta_str = f"{'+' if val_delta >= 0 else ''}£{val_delta:.1f}m vs LW"

bank_cls = "delta-up" if bank_delta > 0 else ("delta-down" if bank_delta < 0 else "delta-neutral")
bank_delta_str = f"{'+' if bank_delta > 0 else ''}£{bank_delta:.1f}m vs LW"

active_cap_obj = next((p for p in starting_xi if p.get("is_captain")), starting_xi[0] if starting_xi else {})
active_vc_obj = next((p for p in starting_xi if p.get("is_vice_captain")), starting_xi[1] if len(starting_xi) > 1 else {})

render_html(
    f"<div class='kcfc-hero'>"
    f"<div class='kcfc-hero-top'>"
    f"<div class='kcfc-hero-brand'>{pl_vector_svg}"
    f"<div><div class='kcfc-hero-title'>KINGS COUNTY FC</div>"
    f"<div class='kcfc-hero-sub'>TACTICAL COMMAND &bull; TARGET LEAGUE: {target_league_name}</div></div></div>"
    f"<span class='kpi-delta {roster_mode_cls}'>{roster_sync_mode}</span></div>"
    f"<div class='countdown-bar'><div class='countdown-left'><div class='pulse-dot'></div>"
    f"<div class='countdown-lbl'>GAMEWEEK {upcoming_gw} DEADLINE</div></div>"
    f"<div class='countdown-val'>{countdown_display}</div></div></div>"
)

if st.button(f"⟳ Last Updated: {st.session_state['last_synced_str']} — Tap to Refresh Data & Clear Persisted State", use_container_width=True):
    st.cache_data.clear()
    st.session_state["sync_nonce"] += 1
    st.session_state["cap_override_id"] = None
    st.session_state["vc_override_id"] = None
    st.session_state["persisted_squad_state"] = None
    if "cap_id" in st.query_params:
        del st.query_params["cap_id"]
    if "vc_id" in st.query_params:
        del st.query_params["vc_id"]
    st.session_state["last_synced_str"] = datetime.now(ZoneInfo("America/New_York")).strftime("%I:%M:%S %p EDT")
    st.rerun()

render_html(
    f"<div class='kpi-grid-6' style='margin-top:6px;'>"
    f"<div class='kpi-card'><div class='kpi-label'>Season Points</div><div class='kpi-value'>{total_pts:,}</div><span class='kpi-delta {gw_cls}'>{gw_delta_str}</span></div>"
    f"<div class='kpi-card'><div class='kpi-label'>Overall Rank</div><div class='kpi-value'>{overall_rank:,}</div><span class='kpi-delta {rank_cls}'>{rank_arrow}</span></div>"
    f"<div class='kpi-card'><div class='kpi-label'>Transfers Available</div><div class='kpi-value' style='color:#FBBF24;'>{ft_remaining_now} FT</div><span class='kpi-delta {ft_rec_cls}'>{ft_rec_text}</span></div>"
    f"<div class='kpi-card'><div class='kpi-label'>Squad Value</div><div class='kpi-value'>£{val_now:.1f}m</div><span class='kpi-delta {val_cls}'>{val_delta_str}</span></div>"
    f"<div class='kpi-card'><div class='kpi-label'>In The Bank</div><div class='kpi-value' style='color:#00FF85;'>£{bank_now:.1f}m</div><span class='kpi-delta {bank_cls}'>{bank_delta_str}</span></div>"
    f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Projected XI</div><div class='kpi-value' style='color:#06B6D4;'>{team_xp_total} xP</div><span class='kpi-delta delta-up'>C: {active_cap_obj.get('web_name', 'N/A')} | V: {active_vc_obj.get('web_name', 'N/A')}</span></div>"
    f"</div>"
)

# ---------------------------------------------------------
# 11. PRE-COMPUTE GLOBAL TRANSFER RANKINGS & FUNDING PAIRS
# ---------------------------------------------------------
squad_ids = {p["id"] for p in full_squad}

sell_rankings = []
for p in full_squad:
    chance = p.get("chance_of_playing_next_round")
    chance_val = 100 if chance is None else chance
    is_gk = (p.get("element_type") == 1)
    gk_penalty = -25.0 if (is_gk and chance_val >= 75) else 0.0
    starter_boost = 4.5 if p in starting_xi else 0.0
    urgency = (
        ((100 - chance_val) * 0.6)
        + ((6.8 - min(p.get("xp_next", 3.0), 6.8)) * 4.5)
        + (p.get("avg_5_fdr", 3.0) * 2.2)
        + starter_boost
        + gk_penalty
    )
    sell_rankings.append((urgency, p))

sell_rankings.sort(key=lambda x: x[0], reverse=True)

funding_pairs = []
for donor in full_squad:
    if donor.get("element_type") == 1:
        continue
    d_sell = donor.get("selling_price", donor.get("now_cost", 50) / 10.0)
    cheap_enablers = [
        e for e in elements_map.values()
        if e["id"] not in squad_ids
        and e.get("element_type") == donor.get("element_type")
        and (e.get("now_cost", 999) / 10.0) <= (d_sell - 0.8)
        and e.get("xp_next", 0) >= 2.8
    ]
    cheap_enablers.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
    if cheap_enablers:
        best_enabler = cheap_enablers[0]
        cash_freed = round(d_sell - (best_enabler["now_cost"] / 10.0), 1)
        funding_pairs.append((cash_freed, donor, best_enabler))
funding_pairs.sort(key=lambda x: x[0], reverse=True)

# ---------------------------------------------------------
# 12. NAVIGATION TABS (NO EMOJIS, DEDICATED SETTINGS TAB)
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_league, tab_ai, tab_settings = st.tabs([
    "Tactical Pitch & Dossier",
    "Transfer Matrix & Cart Simulator",
    "Mini-League & Rival Spy",
    "AI Tactical Advisor",
    "Settings"
])

def build_pitch_node_html(p, is_selected=False, bench_slot=None):
    pid = p.get("id")
    bg_style = build_avatar_bg_style(p)

    cap_badge = "<div class='badge-cap'>C</div>" if p.get("is_captain") else (
                "<div class='badge-vc'>V</div>" if p.get("is_vice_captain") else "")

    chance = p.get("chance_of_playing_next_round")
    flag_badge = ""
    if chance is not None and chance < 100:
        flag_badge = f"<div class='badge-flag'>{'OUT' if chance == 0 else f'{chance}%'}</div>"
    elif bench_slot is not None:
        flag_badge = f"<div class='badge-sub'>SUB {bench_slot}</div>"

    runway = p.get("runway", [])
    nxt = runway[0] if runway else {"opp": "TBD", "venue": "H", "fdr": 3}
    fdr_c = f"fdr-{nxt['fdr']}"
    sel_c = "selected" if is_selected else ""
    price = p.get("now_cost", 50) / 10.0

    lg_param = st.session_state.get("target_lg_id", "")
    href_url = f"?auth=passed&team_id={team_id}&lg_id={lg_param}&pid={pid}#player-dossier"

    return (
        f"<a class='pitch-node-link' href='{href_url}' target='_self'>"
        f"<div class='pitch-node {sel_c}'>"
        f"<div class='node-avatar-wrap'>"
        f"<div class='node-avatar-circle' style=\"{bg_style}\"></div>"
        f"{cap_badge}{flag_badge}"
        f"</div>"
        f"<div class='node-name'>{p.get('web_name')}</div>"
        f"<div class='node-meta'>£{price:.1f}m &bull; {p.get('xp_next')}xP</div>"
        f"<div class='fdr-pill {fdr_c}'>{nxt['opp']} ({nxt['venue']})</div>"
        f"<div class='node-dossier-btn'>Dossier</div>"
        f"</div></a>"
    )

# =========================================================
# TAB 1: FULL TACTICAL PITCH VIEW, DOSSIER & GW DEBRIEF
# =========================================================
@st.fragment
def render_pitch_and_dossier_fragment():
    col_left, col_right = st.columns([1.35, 1], gap="medium")
    sel_pid = st.session_state.get("selected_pid")

    with col_left:
        gks = [p for p in starting_xi if p.get("element_type") == 1]
        defs = [p for p in starting_xi if p.get("element_type") == 2]
        mids = [p for p in starting_xi if p.get("element_type") == 3]
        fwds = [p for p in starting_xi if p.get("element_type") == 4]
        bench_sorted = sorted(bench_xi, key=lambda x: x.get("pick_pos", 12))

        gk_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in gks)
        def_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in defs)
        mid_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in mids)
        fwd_html = "".join(build_pitch_node_html(p, p["id"] == sel_pid) for p in fwds)

        render_html(
            f"<div class='pitch-wrapper'>"
            f"<div class='pitch-row'>{gk_html}</div>"
            f"<div class='pitch-row'>{def_html}</div>"
            f"<div class='pitch-row'>{mid_html}</div>"
            f"<div class='pitch-row'>{fwd_html}</div>"
            f"</div>"
        )

        bench_html = "".join(
            build_pitch_node_html(p, p["id"] == sel_pid, bench_slot=i+1)
            for i, p in enumerate(bench_sorted)
        )
        render_html(
            f"<div class='bench-tray'>"
            f"<div class='bench-label'><span>PRIORITY AUTO-SUB BENCH</span>"
            f"<span style='color:#00FF85;'>TAP ANY PLAYER FOR DOSSIER</span></div>"
            f"<div class='pitch-row' style='margin-bottom:0;'>{bench_html}</div></div>"
        )

    with col_right:
        render_html("<div id='player-dossier'></div>")

        squad_options = {
            p["id"]: f"{'[C] ' if p.get('is_captain') else ('[V] ' if p.get('is_vice_captain') else '')}{p['web_name']} ({p['team_short']} - £{p['now_cost']/10:.1f}m | {p['xp_next']}xP)"
            for p in full_squad
        }
        if squad_options:
            chosen_pid = st.selectbox(
                "Quick-Switch Player Dossier (Instant Zero-Refresh):",
                options=list(squad_options.keys()),
                format_func=lambda x: squad_options[x],
                index=list(squad_options.keys()).index(sel_pid) if sel_pid in squad_options else 0
            )
            if chosen_pid != sel_pid:
                st.session_state["selected_pid"] = chosen_pid
                st.rerun()

        sp = next((x for x in full_squad if x["id"] == st.session_state.get("selected_pid")), full_squad[0] if full_squad else None)
        if sp:
            cap_btn_c1, cap_btn_c2 = st.columns(2)
            with cap_btn_c1:
                if st.button(f"Simulate {sp['web_name']} as Captain (C)", use_container_width=True):
                    st.session_state["cap_override_id"] = sp["id"]
                    st.session_state["persisted_squad_state"] = [
                        {"element": x["id"], "position": x["pick_pos"], "is_captain": x["id"] == sp["id"], "is_vice_captain": x.get("is_vice_captain", False)}
                        for x in full_squad
                    ]
                    st.rerun()
            with cap_btn_c2:
                if st.button(f"Simulate {sp['web_name']} as Vice (V)", use_container_width=True):
                    st.session_state["vc_override_id"] = sp["id"]
                    st.session_state["persisted_squad_state"] = [
                        {"element": x["id"], "position": x["pick_pos"], "is_captain": x.get("is_captain", False), "is_vice_captain": x["id"] == sp["id"]}
                        for x in full_squad
                    ]
                    st.rerun()

            dossier_bg_style = build_avatar_bg_style(sp)
            pos_name = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}.get(sp.get("element_type"), "Player")
            p_price = sp.get("now_cost", 50) / 10.0
            sell_val = sp.get("selling_price", p_price)
            pts_per_m = round(sp.get("total_points", 0) / max(p_price, 4.0), 1)
            rival_cnt = rival_threat_players.get(sp["id"], 0)
            rival_tag = f"Owned by {rival_cnt}/3 Top Rivals" if rival_cnt > 0 else "True Mini-League Differential (0/3 Rivals)"

            runway_chips = "".join(
                f"<div style='background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 4px; text-align:center;'>"
                f"<div style='font-size:9.5px; color:var(--text-secondary);'>GW{r['gw']}</div>"
                f"<div style='font-size:11px; font-weight:700; color:#FFF; margin:3px 0;'>{r['opp']} ({r['venue']})</div>"
                f"<span class='fdr-pill fdr-{r['fdr']}' style='display:inline-block; width:auto; padding:1px 6px;'>FDR {r['fdr']}</span>"
                f"</div>"
                for r in sp.get("runway", [])[:5]
            )

            news_banner = ""
            if sp.get("news"):
                news_banner = (
                    f"<div style='background:rgba(244,63,94,0.12); border-left:3px solid #F43F5E; padding:10px 12px; "
                    f"border-radius:8px; font-size:12px; color:#FDA4AF; margin-bottom:14px;'>"
                    f"<strong>Medical / Status Alert:</strong> {sp.get('news')}</div>"
                )

            if sp.get("xp_next", 0) >= 5.5:
                verdict_tag, verdict_col = "CAPTAIN / LOCK STARTER", "#00FF85"
            elif sp.get("xp_next", 0) >= 3.8:
                verdict_tag, verdict_col = "SOLID ROTATION HOLD", "#06B6D4"
            else:
                verdict_tag, verdict_col = "UPGRADE / BENCH CANDIDATE", "#F59E0B"

            render_html(
                f"<div class='dossier-card'>"
                f"<div class='dossier-top'>"
                f"<div class='dossier-avatar-circle' style=\"{dossier_bg_style}\"></div>"
                f"<div style='flex:1;'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;'>"
                f"<span style='font-size:20px; font-weight:800; color:#FFF;'>{sp.get('first_name')} {sp.get('second_name')}</span>"
                f"<span style='font-size:10px; font-weight:800; padding:4px 9px; border-radius:999px; background:rgba(0,255,133,0.12); color:{verdict_col}; border:1px solid {verdict_col};'>{verdict_tag}</span>"
                f"</div>"
                f"<div style='font-size:12px; color:var(--text-secondary); margin-top:4px;'>"
                f"{pos_name} &bull; <strong>{teams_map.get(sp.get('team'), {}).get('name', 'Premier League')}</strong> &bull; Global TSB: {sp.get('selected_by_percent')}%"
                f"</div>"
                f"<div style='font-size:11px; color:#06B6D4; font-weight:700; margin-top:3px;'>{target_league_name}: {rival_tag}</div>"
                f"</div></div>"
                f"{news_banner}"
                f"<div class='stat-grid-4'>"
                f"<div class='stat-box'><div class='stat-box-lbl'>Market / Sell Price</div><div class='stat-box-val'>£{p_price:.1f}m / <span style='color:#00FF85;'>£{sell_val:.1f}m</span></div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{upcoming_gw} xP</div><div class='stat-box-val' style='color:#00FF85;'>{sp.get('xp_next')}</div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>5-GW Projected</div><div class='stat-box-val' style='color:#06B6D4;'>{sp.get('xp_5gw')}p</div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{last_active_gw} Actual</div><div class='stat-box-val'>{sp.get('last_gw_pts', 0)} pts</div></div>"
                f"</div>"
                f"<div class='stat-grid-4'>"
                f"<div class='stat-box'><div class='stat-box-lbl'>Form Rating</div><div class='stat-box-val'>{sp.get('form')}</div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>xG + xA (xGI)</div><div class='stat-box-val'>{sp.get('expected_goal_involvements', '0.00')}</div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>ICT Index</div><div class='stat-box-val'>{sp.get('ict_index', '0.0')}</div></div>"
                f"<div class='stat-box'><div class='stat-box-lbl'>Value (Pts/£m)</div><div class='stat-box-val'>{pts_per_m}</div></div>"
                f"</div>"
                f"<div style='font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-secondary); margin:12px 0 8px 0;'>Upcoming 5-GW Runway (Avg FDR: {sp.get('avg_5_fdr')})</div>"
                f"<div class='runway-grid-5'>{runway_chips}</div></div>"
            )

with tab_pitch:
    render_pitch_and_dossier_fragment()

    starters_sorted_last = sorted(starting_xi, key=lambda x: x.get("last_gw_pts", 0), reverse=True)
    top_performers = [p for p in starters_sorted_last if p.get("last_gw_pts", 0) >= 6][:3]
    if not top_performers and starters_sorted_last:
        top_performers = starters_sorted_last[:2]

    bench_pts_left = sum(p.get("last_gw_pts", 0) for p in bench_xi)
    bench_stars = [p for p in bench_xi if p.get("last_gw_pts", 0) >= 5]
    underperformers = [p for p in starting_xi if p.get("last_gw_pts", 0) <= 2 and p.get("element_type") != 1]

    wins_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['last_gw_pts']} pts)" for p in top_performers) or "Steady baseline contributions."
    imp_str = (
        f"Left <strong>{bench_pts_left} pts</strong> on the bench"
        + (f" (including {', '.join(p['web_name'] for p in bench_stars)})" if bench_stars else "")
        + (f". Low starter returns from {', '.join(p['web_name'] for p in underperformers[:3])}." if underperformers else ".")
    )
    watch_items = []
    for p in full_squad:
        if p.get("news"):
            watch_items.append(f"<strong>{p['web_name']}</strong> ({p['news']})")
        elif p.get("next_fdr", 3) >= 4 and p in starting_xi:
            nxt = p["runway"][0] if p.get("runway") else {"opp": "TBD", "fdr": 4}
            watch_items.append(f"<strong>{p['web_name']}</strong> faces tough GW{upcoming_gw} matchup vs {nxt['opp']} (FDR {nxt['fdr']})")
    watch_str = " &bull; ".join(watch_items[:4]) or "No major injury or suspension flags across your 15-man squad."

    render_html(
        f"<div class='dossier-card' style='margin-top:20px; border-color:rgba(0, 255, 133, 0.25);'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:12px;'>"
        f"<span style='font-size:16px; font-weight:800; color:#FFF;'>GW{last_active_gw} EXECUTIVE DEBRIEF & FORWARD RADAR</span>"
        f"<span style='font-size:11px; color:#00FF85; font-family:JetBrains Mono, monospace;'>{calibration_note}</span></div>"
        f"<div class='buy-grid-3'>"
        f"<div style='background:rgba(16,185,129,0.07); border-left:3px solid #00FF85; padding:12px; border-radius:10px;'>"
        f"<div style='font-size:11px; font-weight:800; color:#00FF85; text-transform:uppercase;'>What Went Well (GW{last_active_gw})</div>"
        f"<div style='font-size:12.5px; color:#E2E8F0; margin-top:6px;'>Scored <strong>{gw_pts} pts</strong> ({'+' if gw_vs_avg >= 0 else ''}{gw_vs_avg} vs GW Average). Key drivers: {wins_str}.</div></div>"
        f"<div style='background:rgba(245,158,11,0.07); border-left:3px solid #F59E0B; padding:12px; border-radius:10px;'>"
        f"<div style='font-size:11px; font-weight:800; color:#FBBF24; text-transform:uppercase;'>Areas for Improvement</div>"
        f"<div style='font-size:12.5px; color:#E2E8F0; margin-top:6px;'>{imp_str}</div></div>"
        f"<div style='background:rgba(244,63,94,0.07); border-left:3px solid #F43F5E; padding:12px; border-radius:10px;'>"
        f"<div style='font-size:11px; font-weight:800; color:#FB7185; text-transform:uppercase;'>GW{upcoming_gw} Risk & Fixture Watch</div>"
        f"<div style='font-size:12.5px; color:#E2E8F0; margin-top:6px;'>{watch_str}</div></div>"
        f"</div></div>"
    )

# =========================================================
# TAB 2: OUTFIELD-FIRST TRANSFER MATRIX, UPGRADE PATHS & MULTI-CART
# =========================================================
with tab_transfers:
    render_html(
        f"<div class='dossier-card' style='padding:16px 20px;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>"
        f"<div><h3 style='margin:0; font-size:16px; font-weight:800; color:#FFF;'>OUTFIELD-FIRST TRANSFER MATRIX & PREMIUM UPGRADE PATHS</h3>"
        f"<p style='margin:4px 0 0 0; font-size:12px; color:var(--text-secondary);'>"
        f"Goalkeepers are deprioritized unless injured. Evaluates direct in-budget swaps AND 2-move premium upgrade paths tailored to beat <strong>{target_league_name}</strong>.</p></div>"
        f"<span class='kpi-delta delta-up'>{ft_remaining_now} Free Transfer(s) | £{bank_now:.1f}m Bank</span></div></div>"
    )

    for idx, (urg_score, sell_p) in enumerate(sell_rankings[:3]):
        s_sell_val = sell_p.get("selling_price", sell_p.get("now_cost", 50) / 10.0)
        max_direct_budget = round(s_sell_val + bank_now, 1)
        pos_id = sell_p.get("element_type", 3)

        reason_str = sell_p.get("news") or (
            f"Projected for only {sell_p.get('xp_next')} xP next GW ({sell_p.get('xp_5gw')} xP over 5 GWs) with Avg FDR {sell_p.get('avg_5_fdr')}"
        )

        direct_cands = [
            cand for cand in elements_map.values()
            if cand["id"] not in squad_ids
            and cand.get("element_type") == pos_id
            and (cand.get("now_cost", 999) / 10.0) <= max_direct_budget
            and (cand.get("chance_of_playing_next_round") is None or cand.get("chance_of_playing_next_round") >= 75)
        ]
        direct_cands.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
        top_3_direct = direct_cands[:3]

        buy_cards_html = ""
        for b_i, bp in enumerate(top_3_direct):
            b_cost = bp.get("now_cost", 50) / 10.0
            xp_gain_5 = round(bp.get("xp_5gw", 0) - sell_p.get("xp_5gw", 0), 1)
            nxt_fix = bp["runway"][0] if bp.get("runway") else {"opp": "TBD", "venue": "H", "fdr": 3}
            ml_badge = "RIVAL BLOCK" if bp["id"] in rival_ownership_set else "DIFFERENTIAL"
            buy_cards_html += (
                f"<div class='buy-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<span style='font-size:13.5px; font-weight:800; color:#FFF;'>#{b_i+1} {bp.get('web_name')} ({bp.get('team_short')})</span>"
                f"<span style='font-size:10.5px; font-weight:800; color:#00FF85; background:rgba(0,255,133,0.15); padding:2px 7px; border-radius:6px;'>+{xp_gain_5} xP (5GW)</span>"
                f"</div>"
                f"<div style='font-size:11.5px; color:var(--text-secondary); margin:5px 0;'>"
                f"Cost: <strong>£{b_cost:.1f}m</strong> &bull; Next: <strong>{nxt_fix['opp']} ({nxt_fix['venue']})</strong> &bull; <span style='color:#06B6D4;'>{ml_badge}</span>"
                f"</div>"
                f"<div style='font-size:11px; font-family:JetBrains Mono, monospace; color:#CBD5E1;'>"
                f"GW{upcoming_gw}: <strong>{bp.get('xp_next')}xP</strong> | Form: <strong>{bp.get('form')}</strong> | xGI: <strong>{bp.get('expected_goal_involvements')}</strong>"
                f"</div></div>"
            )

        upgrade_banner_html = ""
        elite_targets = [
            cand for cand in elements_map.values()
            if cand["id"] not in squad_ids
            and cand.get("element_type") == pos_id
            and (cand.get("now_cost", 0) / 10.0) > max_direct_budget
            and cand.get("xp_5gw", 0) > ((top_3_direct[0]["xp_5gw"] if top_3_direct else 0) + 3.0)
        ]
        elite_targets.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
        if elite_targets and funding_pairs:
            dream_p = elite_targets[0]
            dream_cost = dream_p["now_cost"] / 10.0
            shortfall = round(dream_cost - max_direct_budget, 1)
            viable_pair = next((fp for fp in funding_pairs if fp[1]["id"] != sell_p["id"] and fp[0] >= shortfall), None)
            if viable_pair:
                freed_m, donor_p, enabler_p = viable_pair
                combo_xp_gain = round(
                    (dream_p["xp_5gw"] + enabler_p["xp_5gw"]) - (sell_p["xp_5gw"] + donor_p["xp_5gw"]), 1
                )
                upgrade_banner_html = (
                    f"<div class='upgrade-card'>"
                    f"<div style='font-size:11px; font-weight:800; color:#06B6D4; text-transform:uppercase;'>"
                    f"2-TRANSFER PREMIUM UPGRADE PATH UNLOCKED: {sell_p.get('web_name')} &rarr; {dream_p.get('web_name')} (£{dream_cost:.1f}m)"
                    f"</div>"
                    f"<div style='font-size:12px; color:#E2E8F0; margin-top:4px;'>"
                    f"You are <strong>£{shortfall:.1f}m</strong> short of <strong>{dream_p.get('web_name')} ({dream_p.get('team_short')}, {dream_p.get('xp_5gw')} 5-GW xP)</strong>. "
                    f"Pair this move with <strong>{donor_p.get('web_name')} &rarr; {enabler_p.get('web_name')} (£{enabler_p['now_cost']/10:.1f}m)</strong> to free up <strong>£{freed_m:.1f}m</strong> "
                    f"for a combined net gain of <strong style='color:#00FF85;'>+{combo_xp_gain} xP</strong> over 5 Gameweeks."
                    f"</div></div>"
                )

        render_html(
            f"<div class='sell-banner'>"
            f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>"
            f"<div><span style='font-size:10.5px; font-weight:800; background:#F43F5E; color:#FFF; padding:3px 8px; border-radius:6px; margin-right:8px;'>OUTFIELD PRIORITY #{idx+1}</span>"
            f"<span style='font-size:16px; font-weight:800; color:#FFF;'>{sell_p.get('web_name')} ({sell_p.get('team_short')})</span></div>"
            f"<div style='font-family:JetBrains Mono, monospace; font-size:12px; color:#F8FAFC;'>Est. Sell Value: <strong>£{s_sell_val:.1f}m</strong> &bull; 1-Move Max Budget: <strong style='color:#00FF85;'>£{max_direct_budget:.1f}m</strong></div></div>"
            f"<div style='font-size:12px; color:#FDA4AF; margin-top:6px;'><strong>Audit Trigger:</strong> {reason_str}</div>"
            f"<div class='buy-grid-3'>{buy_cards_html}</div>{upgrade_banner_html}</div>"
        )

    render_html(
        "<div class='dossier-card' style='margin-top:20px; padding:16px 20px;'>"
        "<h3 style='margin:0; font-size:16px; font-weight:800; color:#06B6D4;'>MULTI-PLAYER TRANSFER CART & HIT SIMULATOR</h3>"
        "<p style='margin:4px 0 0 0; font-size:12px; color:var(--text-secondary);'>"
        "Select 1 to 5 squad players to transfer out simultaneously. Validates exact selling prices, 3-per-club limits, point hits (-4 pts per extra move), and 5-GW breakeven math.</p></div>"
    )

    out_options_map = {
        p["id"]: f"{p['web_name']} ({p['team_short']} | Pos: { {1:'GK',2:'DEF',3:'MID',4:'FWD'}[p['element_type']] } | Sell: £{p.get('selling_price', p['now_cost']/10):.1f}m | {p['xp_next']}xP)"
        for p in full_squad
    }
    default_multi_out = [sell_rankings[0][1]["id"]] if sell_rankings else []
    selected_out_ids = st.multiselect(
        "Step 1 — Select Squad Player(s) to Transfer OUT (1 to 5 players):",
        options=list(out_options_map.keys()),
        default=default_multi_out,
        format_func=lambda x: out_options_map[x],
        max_selections=5
    )

    if selected_out_ids:
        out_objs = [next(p for p in full_squad if p["id"] == oid) for oid in selected_out_ids]
        total_released = round(sum(p.get("selling_price", p["now_cost"] / 10.0) for p in out_objs) + bank_now, 1)

        st.markdown(f"**Step 2 — Select Replacement(s) (Total Combined Budget Available: `£{total_released:.1f}m`):**")
        in_cols = st.columns(len(out_objs))
        selected_in_objs = []
        running_spend = 0.0

        for idx_m, out_p in enumerate(out_objs):
            pos_m = out_p["element_type"]
            pos_lbl = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}.get(pos_m, "PLY")
            already_chosen_ids = {x["id"] for x in selected_in_objs}
            cands_m = [
                c for c in elements_map.values()
                if c["id"] not in squad_ids
                and c["id"] not in already_chosen_ids
                and c.get("element_type") == pos_m
                and (c.get("chance_of_playing_next_round") is None or c.get("chance_of_playing_next_round") >= 75)
            ]
            cands_m.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)
            c_map = {
                c["id"]: f"{c['web_name']} ({c['team_short']} - £{c['now_cost']/10:.1f}m | {c['xp_5gw']} 5GW xP)"
                for c in cands_m[:60]
            }
            with in_cols[idx_m]:
                chosen_in_id = st.selectbox(
                    f"Replace {out_p['web_name']} ({pos_lbl}):",
                    options=list(c_map.keys()),
                    format_func=lambda x, cm=c_map: cm[x],
                    key=f"cart_in_{idx_m}_{out_p['id']}"
                )
                in_obj = elements_map[chosen_in_id]
                selected_in_objs.append(in_obj)
                running_spend += (in_obj["now_cost"] / 10.0)

        rem_bank_cart = round(total_released - running_spend, 1)
        num_moves = len(out_objs)
        extra_hits = max(0, num_moves - ft_remaining_now)
        hit_cost = extra_hits * -4

        gw1_xp_delta = round(sum(x["xp_next"] for x in selected_in_objs) - sum(x["xp_next"] for x in out_objs) + hit_cost, 1)
        gw5_xp_delta = round(sum(x["xp_5gw"] for x in selected_in_objs) - sum(x["xp_5gw"] for x in out_objs) + hit_cost, 1)

        sim_squad_teams = [p["team"] for p in full_squad if p["id"] not in selected_out_ids] + [p["team"] for p in selected_in_objs]
        club_violations = [
            teams_map[t_id]["short_name"]
            for t_id in set(sim_squad_teams)
            if sim_squad_teams.count(t_id) > 3
        ]

        if rem_bank_cart < 0:
            cart_verdict = f"OVER BUDGET BY £{abs(rem_bank_cart):.1f}m"
            cart_col = "#F43F5E"
        elif club_violations:
            cart_verdict = f"CLUB LIMIT (>3 {', '.join(club_violations)})"
            cart_col = "#F43F5E"
        elif gw5_xp_delta >= 5.0:
            cart_verdict = "STRONG TACTICAL UPGRADE"
            cart_col = "#00FF85"
        elif gw5_xp_delta > 0:
            cart_verdict = "MARGINAL GAIN (CONSIDER HOLDING)"
            cart_col = "#FBBF24"
        else:
            cart_verdict = "NEGATIVE EV — DO NOT EXECUTE"
            cart_col = "#F43F5E"

        if st.button("Apply Cart Transfers & Persist Roster State", use_container_width=True):
            new_picks_layout = []
            replaced_ids = {o["id"] for o in out_objs}
            for p in full_squad:
                if p["id"] not in replaced_ids:
                    new_picks_layout.append({
                        "element": p["id"],
                        "position": p["pick_pos"],
                        "is_captain": p.get("is_captain", False),
                        "is_vice_captain": p.get("is_vice_captain", False)
                    })
            for o_obj, i_obj in zip(out_objs, selected_in_objs):
                new_picks_layout.append({
                    "element": i_obj["id"],
                    "position": o_obj["pick_pos"],
                    "is_captain": o_obj.get("is_captain", False),
                    "is_vice_captain": o_obj.get("is_vice_captain", False)
                })
            st.session_state["persisted_squad_state"] = new_picks_layout
            st.cache_data.clear()
            st.session_state["sync_nonce"] += 1
            st.success("Transfers applied and persisted successfully! Reloading pitch...")
            st.rerun()

        render_html(
            f"<div class='stat-grid-4' style='margin-top:14px;'>"
            f"<div class='stat-box'><div class='stat-box-lbl'>Moves / Point Hit Cost</div><div class='stat-box-val'>{num_moves} Move(s) ({hit_cost} pts)</div></div>"
            f"<div class='stat-box'><div class='stat-box-lbl'>GW{upcoming_gw} Net Impact (After Hit)</div><div class='stat-box-val' style='color:{'#00FF85' if gw1_xp_delta >= 0 else '#F43F5E'};'>{'+' if gw1_xp_delta >= 0 else ''}{gw1_xp_delta} xP</div></div>"
            f"<div class='stat-box'><div class='stat-box-lbl'>5-GW Net Impact (After Hit)</div><div class='stat-box-val' style='color:{'#00FF85' if gw5_xp_delta >= 0 else '#F43F5E'};'>{'+' if gw5_xp_delta >= 0 else ''}{gw5_xp_delta} xP</div></div>"
            f"<div class='stat-box'><div class='stat-box-lbl'>Remaining Bank & Verdict</div><div class='stat-box-val' style='font-size:13px; color:{cart_col};'>£{rem_bank_cart:.1f}m &bull; {cart_verdict}</div></div>"
            f"</div>"
        )

# =========================================================
# TAB 3: MINI-LEAGUE STANDINGS & RIVAL BLOCK/ATTACK MATRIX
# =========================================================
with tab_league:
    if target_league_standings:
        my_row = next((r for r in target_league_standings if r["entry"] == team_id), None)
        my_pts = my_row["total"] if my_row else total_pts
        rival_candidates = [r for r in target_league_standings[:10] if r["entry"] != team_id]
        rival_map = {r["entry"]: f"#{r['rank']} {r['entry_name']} ({r['player_name']}) - {r['total']} pts" for r in rival_candidates}

        col_tbl, col_spy = st.columns([1.15, 1], gap="medium")

        with col_tbl:
            table_rows_html = ""
            for r in target_league_standings[:12]:
                is_me = (r["entry"] == team_id)
                row_cls = "ml-row-me" if is_me else ""
                gap = r["total"] - my_pts
                gap_str = "YOU" if is_me else (f"+{gap}" if gap > 0 else f"{gap}")
                mv = r.get("last_rank", r["rank"]) - r["rank"]
                mv_sym = "▲" if mv > 0 else ("▼" if mv < 0 else "━")
                table_rows_html += (
                    f"<tr class='{row_cls}'>"
                    f"<td>{mv_sym} #{r['rank']}</td>"
                    f"<td><strong>{r['entry_name']}</strong><br><span style='font-size:11px; color:var(--text-secondary);'>{r['player_name']}</span></td>"
                    f"<td style='font-family:JetBrains Mono, monospace;'>{r['event_total']}</td>"
                    f"<td style='font-family:JetBrains Mono, monospace; font-weight:700;'>{r['total']}</td>"
                    f"<td style='font-family:JetBrains Mono, monospace; color:{'#F43F5E' if gap > 0 else '#00FF85'};'>{gap_str}</td>"
                    f"</tr>"
                )

            render_html(
                f"<div class='dossier-card'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>"
                f"<span style='font-size:16px; font-weight:800; color:#FFF;'>{target_league_name} Standings</span>"
                f"<span style='font-size:12px; font-weight:700; color:#00FF85;'>"
                f"{'1st Place Leader' if gap_to_leader <= 0 else f'{gap_to_leader} pts behind 1st'}</span></div>"
                f"<table class='ml-table'><thead><tr><th>Rank</th><th>Team & Manager</th><th>GW</th><th>Total</th><th>vs You</th></tr></thead>"
                f"<tbody>{table_rows_html}</tbody></table></div>"
            )

        with col_spy:
            my_xi_ids = {p["id"] for p in starting_xi}
            danger_template_ids = [pid for pid, cnt in rival_threat_players.items() if cnt >= 2 and pid not in my_xi_ids]
            danger_objs = [elements_map[pid] for pid in danger_template_ids if pid in elements_map]
            danger_objs.sort(key=lambda x: x.get("xp_next", 0), reverse=True)

            my_unique_diffs = [p for p in starting_xi if rival_threat_players.get(p["id"], 0) == 0]
            my_unique_diffs.sort(key=lambda x: x.get("xp_next", 0), reverse=True)

            unowned_killers = [
                p for p in elements_map.values()
                if p["id"] not in squad_ids
                and p["id"] not in rival_ownership_set
                and (p.get("now_cost", 999) / 10.0) <= (bank_now + 8.5)
                and p.get("xp_next", 0) >= 5.0
            ]
            unowned_killers.sort(key=lambda x: x.get("xp_5gw", 0), reverse=True)

            danger_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['xp_next']}xP)" for p in danger_objs[:4]) or "None — you cover all high-owned rival template starters."
            diff_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['xp_next']}xP)" for p in my_unique_diffs[:4]) or "None"
            killer_str = ", ".join(f"<strong>{p['web_name']}</strong> ({p['team_short']}, £{p['now_cost']/10:.1f}m - {p['xp_5gw']} 5GW xP)" for p in unowned_killers[:3])

            if rival_map:
                sel_rival_id = st.selectbox("Inspect Specific Rival Starting XI:", options=list(rival_map.keys()), format_func=lambda x: rival_map[x])
                rv_json = fetch_rival_picks(sel_rival_id, last_active_gw, sync_nonce)
                rv_xi_ids = {pk["element"] for pk in rv_json.get("picks", []) if pk.get("position", 1) <= 11} if rv_json else set()
                rv_cap_id = next((pk["element"] for pk in rv_json.get("picks", []) if pk.get("is_captain")), None) if rv_json else None
                rv_cap_name = elements_map.get(rv_cap_id, {}).get("web_name", "Unknown")

                their_only = [elements_map[i] for i in (rv_xi_ids - my_xi_ids) if i in elements_map]
                their_only.sort(key=lambda x: x.get("xp_next", 0), reverse=True)

                best_my_cap = sorted(starting_xi, key=lambda x: x.get("xp_next", 0), reverse=True)[0]
                weakest_my_starter = sorted([p for p in starting_xi if p.get("element_type") != 1], key=lambda x: x.get("xp_next", 0))[0]
                top_block_target = their_only[0] if their_only else None

                render_html(
                    f"<div class='dossier-card'>"
                    f"<h4 style='margin:0 0 10px 0; color:#FFF;'>Tactical Blueprint to Defeat Selected Rival</h4>"
                    f"<div style='background:rgba(0,255,133,0.08); border:1px solid rgba(0,255,133,0.3); border-radius:12px; padding:12px; margin-bottom:12px;'>"
                    f"<div style='font-size:11px; font-weight:800; color:#00FF85;'>3-STEP ACTION PLAN FOR GW{upcoming_gw}</div>"
                    f"<ol style='margin:6px 0 0 16px; padding:0; font-size:12px; color:#E2E8F0; line-height:1.55;'>"
                    f"<li><strong>Captaincy Leverage:</strong> Rival last captained <strong>{rv_cap_name}</strong>. Lock armband on <strong>{best_my_cap['web_name']} ({best_my_cap['xp_next']} xP)</strong>.</li>"
                    f"<li><strong>Weak-Link Upgrade:</strong> Replace lowest-projected outfield starter <strong>{weakest_my_starter['web_name']} ({weakest_my_starter['xp_next']} xP)</strong> with a high-upside attacker ({killer_str}).</li>"
                    f"<li><strong>Defensive Block Check:</strong> Rival's highest-projected differential against you is <strong>{top_block_target['web_name'] if top_block_target else 'None'} ({top_block_target['xp_next'] if top_block_target else 0} xP)</strong>.</li>"
                    f"</ol></div>"
                    f"<div style='font-size:12px; line-height:1.5;'>"
                    f"<p><strong>League-Wide Danger Players (Owned by 2+ Top Rivals, Not You):</strong><br><span style='color:#FB7185;'>{danger_str}</span></p>"
                    f"<p><strong>Your Exclusive Attacking Differentials (0/3 Top Rivals Own):</strong><br><span style='color:#00FF85;'>{diff_str}</span></p>"
                    f"<p><strong>Top Unowned League-Winning Targets (0% Top-4 League Ownership):</strong><br><span style='color:#06B6D4;'>{killer_str}</span></p>"
                    f"</div></div>"
                )
    else:
        st.info("No classic mini-leagues found for this Team ID.")

# =========================================================
# TAB 4: MULTI-TURN GEMINI CONVERSATIONAL AI + GOOGLE SEARCH GROUNDING
# =========================================================
@st.cache_data(ttl=3600)
def discover_available_gemini_models(api_key: str):
    preferred = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
    try:
        r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=8)
        if r.status_code == 200:
            models_data = r.json().get("models", [])
            supported = [
                m["name"].replace("models/", "")
                for m in models_data
                if "generateContent" in m.get("supportedGenerationMethods", [])
                and "gemini" in m.get("name", "")
                and "vision" not in m.get("name", "")
                and "embedding" not in m.get("name", "")
            ]
            flash_first = [m for m in supported if "flash" in m] + [m for m in supported if "pro" in m]
            if flash_first:
                return flash_first[:4]
    except Exception:
        pass
    return preferred

with tab_ai:
    active_gemini_key = (
        st.session_state.get("custom_gemini_key")
        or st.secrets.get("GEMINI_API_KEY", "")
        or st.secrets.get("GOOGLE_API_KEY", "")
    ).strip()

    key_status_badge = (
        "<span class='kpi-delta delta-up'>GEMINI LIVE SEARCH ENGINE ONLINE</span>"
        if active_gemini_key else
        "<span class='kpi-delta delta-down'>API KEY REQUIRED IN SETTINGS TAB</span>"
    )

    render_html(
        f"<div class='dossier-card' style='padding:16px 20px;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;'>"
        f"<div><h3 style='margin:0; font-size:16px; font-weight:800; color:#00FF85;'>GEMINI FPL TACTICAL CO-PILOT (LIVE WEB GROUNDED)</h3>"
        f"<p style='margin:4px 0 0 0; font-size:12px; color:var(--text-secondary);'>"
        f"Multi-turn conversational AI with live Google Search grounding, full squad telemetry, fixture runways, and rationale-driven coaching.</p></div>"
        f"{key_status_badge}</div></div>"
    )

    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [
            {
                "role": "assistant",
                "content": (
                    f"Ready for **GW{upcoming_gw}**, Manager. I have your live **Kings County FC** starting XI, bench order, "
                    f"**{ft_remaining_now} Free Transfer(s)**, **£{bank_now:.1f}m** bank balance, and rival data for **{target_league_name}** loaded[cite: 1, 2].\n\n"
                    f"Ask me anything in plain English—like *'Who should I start and bench this week?'*, *'Why is Semenyo projected so high?'*, "
                    f"or *'How can I restructure my midfield to get Saka?'*—and I'll research the latest team news and walk you through the rationale[cite: 1, 2]."
                )
            }
        ]

    def build_rich_tactical_system_prompt() -> str:
        pos_lbl_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        xi_lines = []
        for p in starting_xi:
            nxt = p["runway"][0] if p.get("runway") else {"opp": "TBD", "venue": "H", "fdr": 3}
            run_5 = ", ".join(f"GW{r['gw']}:{r['opp']}({r['venue']},FDR{r['fdr']})" for r in p.get("runway", [])[:4])
            role_tag = " [CAPTAIN]" if p.get("is_captain") else (" [VICE-CAPTAIN]" if p.get("is_vice_captain") else "")
            flag_str = f" | ALERT: {p['news']}" if p.get("news") else ""
            xi_lines.append(
                f"- {p['web_name']} ({p['team_short']}, {pos_lbl_map.get(p['element_type'])}{role_tag}): "
                f"Sell £{p.get('selling_price', p['now_cost']/10):.1f}m | GW{upcoming_gw} vs {nxt['opp']}({nxt['venue']}, FDR {nxt['fdr']}) -> {p['xp_next']} xP | "
                f"5-GW xP: {p['xp_5gw']} | Form: {p['form']} | xGI: {p.get('expected_goal_involvements')} | Mins: {p.get('minutes')} | Runway: [{run_5}]{flag_str}"
            )

        bench_lines = []
        for idx_b, p in enumerate(sorted(bench_xi, key=lambda x: x.get("pick_pos", 12))):
            nxt = p["runway"][0] if p.get("runway") else {"opp": "TBD", "venue": "H", "fdr": 3}
            flag_str = f" | ALERT: {p['news']}" if p.get("news") else ""
            bench_lines.append(
                f"- Bench #{idx_b+1}: {p['web_name']} ({p['team_short']}, {pos_lbl_map.get(p['element_type'])}): "
                f"Sell £{p.get('selling_price', p['now_cost']/10):.1f}m | GW{upcoming_gw} vs {nxt['opp']}({nxt['venue']}, FDR {nxt['fdr']}) -> {p['xp_next']} xP | "
                f"5-GW xP: {p['xp_5gw']} | Form: {p['form']} | xGI: {p.get('expected_goal_involvements')}{flag_str}"
            )

        top_unowned = sorted(
            [p for p in elements_map.values() if p["id"] not in squad_ids and p.get("element_type") != 1],
            key=lambda x: x.get("xp_5gw", 0),
            reverse=True
        )[:30]
        market_lines = []
        for p in top_unowned:
            nxt_m = p["runway"][0] if p.get("runway") else {"opp": "TBD", "venue": "H"}
            market_lines.append(
                f"- {p['web_name']} ({p['team_short']}, {pos_lbl_map.get(p['element_type'])}, £{p['now_cost']/10:.1f}m): "
                f"GW{upcoming_gw} xP {p['xp_next']} | 5-GW xP {p['xp_5gw']} | Form {p['form']} | xGI {p.get('expected_goal_involvements')} | "
                f"Next: {nxt_m['opp']}({nxt_m['venue']})"
            )

        danger_rivals = [
            elements_map[pid]["web_name"]
            for pid, cnt in rival_threat_players.items()
            if cnt >= 2 and pid not in squad_ids and pid in elements_map
        ]

        prompt_lines = [
            "You are Gemini, the Elite FPL Tactical Co-Pilot and Coach for Barney's team, Kings County FC.",
            "Your goal is to have a natural, insightful, analytical conversation that directly answers whatever the user asks AND teaches them the underlying FPL strategy and rationale so they become a sharper manager.",
            "",
            "CRITICAL OPERATING RULES:",
            "1. NEVER output a generic canned template. Always answer the user's exact question directly in sentence 1.",
            f"2. Explain the 'WHY' (the rationale): break down underlying numbers (xGI, Form, minutes security, home/away fixture swings, clean sheet odds, and Effective Ownership/differential leverage in {target_league_name}).",
            "3. Use Google Search when helpful to verify the latest Premier League press conference quotes, injury updates, tactical role changes, or penalty/set-piece duties.",
            f"4. When the user asks 'who should I start?' or 'bench', compare their 15 squad members' GW{upcoming_gw} fixtures, FDR, form, and xP, recommend the exact Starting XI (in a valid FPL formation: 1 GK, at least 3 DEF, at least 2 MID, at least 1 FWD) and exact 1-2-3 outfield auto-sub bench order, and explain any tough 50/50 calls between their starters and bench players.",
            "5. Never recommend Goalkeeper transfers unless their starting GK is injured/suspended.",
            f"6. When discussing transfers, always check exact affordability (Sell Price + £{bank_now:.1f}m Bank) and show 2-move downgrade+upgrade paths if a premium target costs more than a 1-move swap.",
            "",
            f"LIVE KINGS COUNTY FC TELEMETRY (UPCOMING GAMEWEEK: GW{upcoming_gw}):",
            f"- Free Transfers Available: {ft_remaining_now} FT",
            f"- Money In The Bank: £{bank_now:.1f}m (Total Squad Value: £{val_now:.1f}m)",
            f"- Target Mini-League: {target_league_name} (Gap to 1st place: {gap_to_leader} pts)",
            f"- High-Owned Rival Danger Players (Owned by 2+ top mini-league rivals, NOT in user's squad): {', '.join(danger_rivals) if danger_rivals else 'None'}",
            "",
            "CURRENT STARTING XI:",
            "\n".join(xi_lines),
            "",
            "CURRENT BENCH (IN ORDER):",
            "\n".join(bench_lines),
            "",
            "TOP 30 UNOWNED MARKET TARGETS (BY 5-GW xP):",
            "\n".join(market_lines),
        ]
        return "\n".join(prompt_lines)

    def call_gemini_conversational_advisor(user_prompt: str) -> str:
        active_key = (
            st.session_state.get("custom_gemini_key")
            or st.secrets.get("GEMINI_API_KEY", "")
            or st.secrets.get("GOOGLE_API_KEY", "")
        ).strip()

        if not active_key:
            return (
                "⚠️ **Gemini API Key Not Detected:** To get live web-researched, natural-language coaching from Gemini, "
                "add `GEMINI_API_KEY = \"AIza...\"` in your Streamlit Cloud Secrets (or paste it into the **Settings** tab)."
            )

        sys_instruction = build_rich_tactical_system_prompt()

        contents_history = []
        recent_msgs = st.session_state.get("ai_messages", [])[-10:]
        for m in recent_msgs:
            role_gemini = "user" if m["role"] == "user" else "model"
            text_val = (m.get("content") or "").strip()
            if not text_val:
                continue
            if not contents_history and role_gemini == "model":
                continue
            if contents_history and contents_history[-1]["role"] == role_gemini:
                contents_history[-1]["parts"][0]["text"] += "\n\n" + text_val
            else:
                contents_history.append({
                    "role": role_gemini,
                    "parts": [{"text": text_val}]
                })

        if not contents_history or contents_history[-1]["role"] != "user":
            contents_history.append({"role": "user", "parts": [{"text": user_prompt}]})

        candidate_models = discover_available_gemini_models(active_key)
        attempts = []
        for m_name in candidate_models:
            attempts.append((m_name, True))
            attempts.append((m_name, False))

        error_log = []
        for model_name, use_search in attempts:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={active_key}"
            payload = {
                "system_instruction": {"parts": [{"text": sys_instruction}]},
                "contents": contents_history,
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 2048
                }
            }
            if use_search:
                payload["tools"] = [{"google_search": {}}]

            try:
                r = requests.post(url, json=payload, timeout=25)
                if r.status_code == 200:
                    resp_json = r.json()
                    cands = resp_json.get("candidates", [])
                    if cands:
                        parts = cands[0].get("content", {}).get("parts", [])
                        text_chunks = [pt.get("text", "") for pt in parts if "text" in pt]
                        answer_text = "\n".join(text_chunks).strip()

                        grounding = cands[0].get("groundingMetadata", {})
                        chunks = grounding.get("groundingChunks", [])
                        web_links = []
                        for ch in chunks:
                            web_obj = ch.get("web", {})
                            uri = web_obj.get("uri")
                            title = web_obj.get("title")
                            if uri and title:
                                web_links.append(f"[{title}]({uri})")
                        if web_links:
                            unique_links = list(dict.fromkeys(web_links))[:4]
                            answer_text += "\n\n---\n**Live Web Sources Checked:** " + " &bull; ".join(unique_links)

                        if answer_text:
                            return answer_text
                else:
                    err_msg = r.json().get("error", {}).get("message", r.text[:200])
                    error_log.append(f"HTTP {r.status_code} ({model_name}, search={use_search}): {err_msg}")
            except Exception as e:
                error_log.append(f"{model_name} exception: {e}")
                continue

        return (
            "⚠️ **Gemini API Connection Error:**\n"
            + "\n".join(f"- `{err}`" for err in error_log[:3])
        )

    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("Who Should I Start & Bench?", use_container_width=True):
        q_txt = f"Who should I start in my XI and how should I order my bench for GW{upcoming_gw}? Explain the rationale and any close 50/50 calls."
        st.session_state["ai_messages"].append({"role": "user", "content": q_txt})
        with st.spinner("Gemini is analyzing your 15-man squad, fixtures, and latest team news..."):
            reply = call_gemini_conversational_advisor(q_txt)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    if qa2.button("Saka / Palmer Upgrade Path", use_container_width=True):
        q_txt = "What is the smartest 1- or 2-transfer path to get Bukayo Saka or Cole Palmer into my squad, and is it worth doing this week?"
        st.session_state["ai_messages"].append({"role": "user", "content": q_txt})
        with st.spinner("Calculating budget math and 5-GW expected point swings..."):
            reply = call_gemini_conversational_advisor(q_txt)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    if qa3.button("Captaincy Deep Dive", use_container_width=True):
        q_txt = f"Break down my best captain and vice-captain choices for GW{upcoming_gw}. Compare safe template shields vs differential upside."
        st.session_state["ai_messages"].append({"role": "user", "content": q_txt})
        with st.spinner("Researching matchup data and captaincy expected value..."):
            reply = call_gemini_conversational_advisor(q_txt)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    if qa4.button("Beat My Mini-League Rivals", use_container_width=True):
        q_txt = f"Based on my {gap_to_leader} pt gap in {target_league_name} and the rival danger players, what tactical posture and moves will help me gain ground?"
        st.session_state["ai_messages"].append({"role": "user", "content": q_txt})
        with st.spinner("Evaluating mini-league rival overlap and differential leverage..."):
            reply = call_gemini_conversational_advisor(q_txt)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

    for msg in st.session_state["ai_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Ask Gemini anything (e.g., 'Who should I start?', 'Why is Semenyo projected so high?', 'Should I roll my transfer?')...")
    if user_q:
        st.session_state["ai_messages"].append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("Gemini is researching Premier League data and analyzing your squad..."):
                reply = call_gemini_conversational_advisor(user_q)
                st.markdown(reply)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

# =========================================================
# TAB 5: DEDICATED SETTINGS & LIVE CONNECTION VALIDATOR
# =========================================================
with tab_settings:
    auth_ok = auth_diag.get("authenticated", False)
    status_badge_html = (
        "<span class='kpi-delta delta-up'>AUTHENTICATED (/api/my-team/ 200 OK)</span>"
        if auth_ok else
        f"<span class='kpi-delta delta-down'>PUBLIC FALLBACK (HTTP {auth_diag.get('status_code') or 'N/A'})</span>"
    )

    render_html(
        "<div class='dossier-card'>"
        "<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:14px;'>"
        "<div><h3 style='margin:0; font-size:16px; font-weight:800; color:#FFF;'>LIVE CONNECTION & COOKIE DIAGNOSTIC VALIDATOR</h3>"
        "<p style='margin:4px 0 0 0; font-size:12px; color:var(--text-secondary);'>"
        "Verifies your private FPL session (`FPL_COOKIE` / `FPL_BEARER_TOKEN` / cURL) and displays the exact Captaincy & Bank returned by FPL's server.</p></div>"
        f"{status_badge_html}</div>"
        "<div class='stat-grid-4'>"
        f"<div class='stat-box'><div class='stat-box-lbl'>Auth Protocol Used</div><div class='stat-box-val' style='font-size:13px;'>{auth_diag.get('method_used', 'None')}</div></div>"
        f"<div class='stat-box'><div class='stat-box-lbl'>API Returned Captain</div><div class='stat-box-val' style='color:#00FF85;'>{api_official_cap_name} (C)</div></div>"
        f"<div class='stat-box'><div class='stat-box-lbl'>API Returned Vice-Cap</div><div class='stat-box-val' style='color:#06B6D4;'>{api_official_vc_name} (V)</div></div>"
        f"<div class='stat-box'><div class='stat-box-lbl'>Manual Sim Override</div><div class='stat-box-val' style='font-size:13px; color:{'#FBBF24' if cap_override else '#94A3B8'};'>"
        f"{'ACTIVE (Tap Sync to Reset)' if cap_override or vc_override else 'NONE (Using Live API)'}</div></div>"
        "</div>"
        f"<div style='background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:10px 14px; font-size:12px; color:#E2E8F0; margin-top:8px;'>"
        f"<strong>Diagnostic Status:</strong> {auth_diag.get('message')}</div></div>"
    )

    set_col1, set_col2 = st.columns(2, gap="medium")

    with set_col1:
        render_html(
            "<div class='dossier-card' style='padding:16px 20px;'>"
            "<h4 style='margin:0 0 6px 0; color:#FFF;'>Target Mini-League & Team ID</h4>"
            "<p style='margin:0; font-size:12px; color:var(--text-secondary);'>"
            "Select the primary mini-league that drives all rival block/differential badges and AI strategy.</p></div>"
        )
        if classic_leagues:
            lg_options = {lg["id"]: f"{lg['name']} (Current Rank: #{lg.get('entry_rank', '?')})" for lg in classic_leagues}
            cur_lg = st.session_state.get("target_lg_id", classic_leagues[0]["id"])
            new_lg = st.selectbox(
                "Default Target Mini-League:",
                options=list(lg_options.keys()),
                format_func=lambda x: lg_options[x],
                index=list(lg_options.keys()).index(cur_lg) if cur_lg in lg_options else 0
            )
            if new_lg != cur_lg:
                st.session_state["target_lg_id"] = new_lg
                st.query_params["lg_id"] = str(new_lg)
                st.rerun()

        new_tid = st.number_input("FPL Entry / Team ID:", value=int(team_id), step=1)
        if st.button("Update Team ID & Reset Overrides", use_container_width=True):
            st.session_state["team_id"] = int(new_tid)
            st.session_state["cap_override_id"] = None
            st.session_state["vc_override_id"] = None
            st.session_state["persisted_squad_state"] = None
            st.query_params["team_id"] = str(new_tid)
            st.cache_data.clear()
            st.session_state["sync_nonce"] += 1
            st.rerun()

    with set_col2:
        render_html(
            "<div class='dossier-card' style='padding:16px 20px;'>"
            "<h4 style='margin:0 0 6px 0; color:#FFF;'>Live API Credentials (Overrides / Secrets Fallback)</h4>"
            "<p style='margin:0; font-size:12px; color:var(--text-secondary);'>"
            "Paste your `x-api-authorization` Bearer token, full `Copy as cURL` command, or Gemini API key below.</p></div>"
        )
        with st.form("settings_creds_form"):
            in_cookie = st.text_input(
                "FPL Bearer Token / `Copy as cURL` / Cookie (`FPL_COOKIE`):",
                value=fpl_cookie_val,
                type="password",
                help="Paste the 'Bearer eyJ...' token from x-api-authorization OR right-click '1575281/' in DevTools -> Copy -> Copy as cURL."
            )
            in_gem = st.text_input(
                "Gemini API Key (`GEMINI_API_KEY`):",
                value=st.session_state.get("custom_gemini_key") or st.secrets.get("GEMINI_API_KEY", ""),
                type="password"
            )
            in_email = st.text_input("FPL Email (Optional fallback):", value=fpl_email_val)
            in_pass = st.text_input("FPL Password (Optional fallback):", value=fpl_pass_val, type="password")

            if st.form_submit_button("Save Credentials, Test Connection & Reset Captaincy", use_container_width=True):
                st.session_state["custom_fpl_cookie"] = in_cookie.strip()
                st.session_state["custom_gemini_key"] = in_gem.strip()
                st.session_state["custom_fpl_email"] = in_email.strip()
                st.session_state["custom_fpl_password"] = in_pass
                st.session_state["cap_override_id"] = None
                st.session_state["vc_override_id"] = None
                st.session_state["persisted_squad_state"] = None
                st.cache_data.clear()
                st.session_state["sync_nonce"] += 1
                st.session_state["last_synced_str"] = datetime.now(ZoneInfo("America/New_York")).strftime("%I:%M:%S %p EDT")
                st.rerun()

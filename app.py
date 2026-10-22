"""
KINGS COUNTY FC — FPL TACTICAL COMMAND & MINI-LEAGUE INTELLIGENCE
Production Architecture | Glassmorphism Facelift | Advanced Captaincy & Playbook Strategy
"""

import ast
import os
import json
import re
import urllib.parse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & DEFENSIVE SESSION STATE BOOTLOADER
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kings County FC | Tactical Command",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NY_TZ = ZoneInfo("America/New_York")

def now_ny_str() -> str:
    return datetime.now(NY_TZ).strftime("%b %d, %I:%M:%S %p EDT")

def safe_get(obj, key, default=None):
    if isinstance(obj, dict):
        val = obj.get(key, default)
        return default if val is None else val
    return default

def run_startup_qa_suite():
    try:
        src_path = os.path.abspath(__file__)
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as f_src:
                ast.parse(f_src.read())
    except Exception:
        pass

run_startup_qa_suite()

auth_secret = str(st.secrets.get("APP_PASSWORD", "fpl2025"))
default_team_id = int(st.secrets.get("DEFAULT_TEAM_ID", 1575281))
q_tid = st.query_params.get("team_id")
initial_tid = int(q_tid) if (q_tid and str(q_tid).isdigit()) else default_team_id

DEFAULT_SESSION_STATE = {
    "authenticated": (st.query_params.get("auth") == "passed"),
    "team_id": initial_tid,
    "sync_nonce": 0,
    "last_synced_str": now_ny_str(),
    "team_updated_str": "Auto-Synced via Public Roll-Forward",
    "cap_override_id": None,
    "vc_override_id": None,
    "persisted_team_snapshot": None,
    "selected_pid": None,
    "target_lg_id": None,
    "pitch_view_mode": "current",
    "sandbox_transfer_plan": None,
    "sb_out_1": None, "sb_in_1": None,
    "sb_out_2": 0, "sb_in_2": 0,
    "custom_fpl_cookie": "", "custom_fpl_token": "",
    "custom_fpl_email": "", "custom_fpl_password": "",
    "custom_gemini_key": "",
}

for k_state, v_default in DEFAULT_SESSION_STATE.items():
    if k_state not in st.session_state:
        st.session_state[k_state] = v_default

q_pid = st.query_params.get("pid")
if q_pid and str(q_pid).isdigit():
    st.session_state["selected_pid"] = int(q_pid)

def render_html(html_input):
    raw_str = "\n".join(str(x) for x in html_input if x) if isinstance(html_input, list) else str(html_input)
    cleaned = "\n".join(line.lstrip() for line in raw_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SERVER-SIDE PERSISTENT SNAPSHOT VAULT
# ---------------------------------------------------------
@st.cache_resource
def get_server_snapshot_vault() -> dict:
    return {}

def get_snapshot_filepath(tid: int) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), f".kcfc_snapshot_{int(tid)}.json")

def save_team_snapshot(tid: int, snapshot_dict: dict):
    if not isinstance(snapshot_dict, dict) or not safe_get(snapshot_dict, "picks"):
        return
    st.session_state["persisted_team_snapshot"] = snapshot_dict
    st.session_state["team_updated_str"] = safe_get(snapshot_dict, "updated_at", now_ny_str())
    vault = get_server_snapshot_vault()
    vault[int(tid)] = snapshot_dict
    try:
        with open(get_snapshot_filepath(int(tid)), "w", encoding="utf-8") as f_out:
            json.dump(snapshot_dict, f_out, indent=2)
    except Exception:
        pass

def load_team_snapshot(tid: int):
    snap = st.session_state.get("persisted_team_snapshot")
    if isinstance(snap, dict) and safe_get(snap, "team_id") == int(tid) and safe_get(snap, "picks"):
        return snap
    vault = get_server_snapshot_vault()
    if int(tid) in vault and isinstance(vault[int(tid)], dict) and safe_get(vault[int(tid)], "picks"):
        st.session_state["persisted_team_snapshot"] = vault[int(tid)]
        return vault[int(tid)]
    fpath = get_snapshot_filepath(int(tid))
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f_in:
                disk_snap = json.load(f_in)
            if isinstance(disk_snap, dict) and safe_get(disk_snap, "picks"):
                vault[int(tid)] = disk_snap
                st.session_state["persisted_team_snapshot"] = disk_snap
                return disk_snap
        except Exception:
            pass
    return None

def clear_team_snapshot(tid: int):
    st.session_state["persisted_team_snapshot"] = None
    get_server_snapshot_vault().pop(int(tid), None)
    try:
        if os.path.exists(get_snapshot_filepath(int(tid))):
            os.remove(get_snapshot_filepath(int(tid)))
    except Exception:
        pass

# ---------------------------------------------------------
# 3. CSS DESIGN SYSTEM (GLASSMORPHISM FACELIFT)
# ---------------------------------------------------------
components.html(
    "<script>(function(){function n(){try{const d=window.parent.document;"
    "['[class*=\"viewerBadge\"]','[class*=\"profileContainer\"]','[data-testid=\"manage-app-button\"]','[data-testid=\"stStatusWidget\"]','footer','#MainMenu']"
    ".forEach(s=>d.querySelectorAll(s).forEach(e=>{e.style.display='none';e.style.visibility='hidden';}));}catch(e){}}n();setInterval(n,1000);})();</script>",
    height=0,
)

CSS_LINES = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');",
    ":root {",
    "  --bg-base: #070B12; --bg-glass: rgba(15, 23, 42, 0.45); --bg-glass-hover: rgba(30, 41, 59, 0.65);",
    "  --border-glass: rgba(255, 255, 255, 0.06); --accent-emerald: #10B981;",
    "  --accent-neon: #00FF85; --accent-cyan: #06B6D4; --text-primary: #F8FAFC; --text-secondary: #94A3B8;",
    "  --fdr-1: #059669; --fdr-2: #10B981; --fdr-3: #475569; --fdr-4: #D97706; --fdr-5: #E11D48;",
    "}",
    "html, body, [class*='css'] { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; color: var(--text-primary); background-color: var(--bg-base); }",
    ".stApp { background: radial-gradient(circle at 50% 0%, #132238 0%, #070B12 55%); }",
    "#MainMenu, header, footer, [data-testid='stHeader'], [data-testid='stToolbar'], [data-testid='stDecoration'], [data-testid='stStatusWidget'] { display: none !important; }",
    ".block-container { padding-top: 0.8rem !important; padding-bottom: 2.5rem !important; max-width: 1240px !important; }",
    
    "/* Frosted Glass Cards & Hover Physics */",
    ".kpi-card, .dossier-card, .bench-tray { background: var(--bg-glass); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--border-glass); border-radius: 20px; padding: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25); transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease; }",
    ".kpi-card:hover, .playbook-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4); border-color: rgba(255, 255, 255, 0.15); }",
    
    "/* Hero & Telemetry Bar */",
    ".kcfc-hero { background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(15, 23, 42, 0.6) 50%, rgba(6, 182, 212, 0.08) 100%); backdrop-filter: blur(20px); border: 1px solid rgba(0, 255, 133, 0.25); border-radius: 24px; padding: 20px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 16px; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4); }",
    ".kcfc-hero-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; width: 100%; }",
    ".kcfc-hero-brand { display: flex; align-items: center; gap: 16px; }",
    ".kcfc-emblem { width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, #00FF85 0%, #10B981 100%); border: 2px solid rgba(255,255,255,0.8); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 24px rgba(0, 255, 133, 0.4); }",
    ".kcfc-hero-title { font-size: 26px; font-weight: 900; letter-spacing: -0.2px; color: #FFF; margin: 0; line-height: 1.1; }",
    ".kcfc-hero-sub { font-size: 11px; font-weight: 800; color: #00FF85; letter-spacing: 1.2px; text-transform: uppercase; margin-top: 4px; }",
    ".telemetry-unified-bar { width: 100%; background: rgba(0, 0, 0, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }",
    ".pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: #00FF85; box-shadow: 0 0 12px #00FF85; display:inline-block; margin-right:8px; }",
    ".countdown-val { font-size: 15px; font-weight: 800; color: #00FF85; font-family: 'JetBrains Mono', monospace; }",
    
    "/* Typography Polish */",
    ".kpi-label { font-size: 10.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-secondary); margin-bottom: 6px; }",
    ".kpi-value { font-size: 22px; font-weight: 800; color: #FFF; font-family: 'JetBrains Mono', monospace; line-height: 1.1; margin-bottom: 8px; }",
    ".kpi-delta { font-size: 10.5px; font-weight: 700; padding: 4px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; display:inline-block; }",
    
    "/* Tab Bar Override (Segmented iOS Style) */",
    ".stTabs [data-baseweb='tab-list'] { background: rgba(15, 23, 42, 0.4) !important; backdrop-filter: blur(12px) !important; border: 1px solid var(--border-glass) !important; padding: 6px !important; border-radius: 16px !important; gap: 6px !important; margin-bottom: 16px !important; }",
    ".stTabs [data-baseweb='tab'] { background: transparent !important; border: none !important; border-radius: 10px !important; color: var(--text-secondary) !important; font-weight: 700 !important; font-size: 12.5px !important; padding: 10px 16px !important; transition: all 0.2s ease !important; }",
    ".stTabs [aria-selected='true'] { background: rgba(255, 255, 255, 0.1) !important; color: #FFF !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; }",
    ".stTabs [data-baseweb='tab-border'] { display: none !important; background: transparent !important; }",
    
    "/* Pitch & Players */",
    ".pitch-wrapper { background: radial-gradient(circle at 50% 50%, #114227 0%, #0A2616 70%, #05140B 100%); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 24px 10px; position: relative; background-image: linear-gradient(to bottom, transparent 49.5%, rgba(255,255,255,0.12) 49.5%, rgba(255,255,255,0.12) 50.5%, transparent 50.5%), radial-gradient(circle at 50% 50%, transparent 52px, rgba(255,255,255,0.12) 53px, rgba(255,255,255,0.12) 55px, transparent 56px), linear-gradient(to right, transparent 22%, rgba(255,255,255,0.12) 22%, rgba(255,255,255,0.12) 78%, transparent 78%), radial-gradient(circle at 50% 50%, #165231 0%, #0D331D 68%, #071C10 100%); background-size: 100% 100%; box-shadow: inset 0 0 80px rgba(0,0,0,0.8); margin-bottom: 14px; }",
    ".pitch-row { display: flex; justify-content: space-around; align-items: stretch; gap: 6px; margin-bottom: 14px; }",
    ".pitch-row:last-child { margin-bottom: 0; }",
    "a.pitch-node-link { text-decoration: none !important; color: inherit !important; flex: 1 1 0; max-width: 122px; min-width: 64px; display: flex; }",
    ".pitch-node { width: 100%; background: rgba(11, 17, 30, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px; padding: 10px 4px 8px 4px; display: flex; flex-direction: column; align-items: center; text-align: center; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; position:relative; }",
    ".pitch-node:hover { transform: translateY(-4px) scale(1.02); border-color: #00FF85; box-shadow: 0 10px 24px rgba(0, 255, 133, 0.15); }",
    ".pitch-node.selected { border: 2px solid #00FF85; box-shadow: 0 0 20px rgba(0, 255, 133, 0.55); }",
    ".pitch-node.sandbox-new { border: 2px solid #06B6D4; box-shadow: 0 0 22px rgba(6, 182, 212, 0.65); }",
    ".node-avatar-wrap { position: relative; width: 56px; height: 56px; margin-bottom: 4px; }",
    ".node-avatar-circle { width: 56px; height: 56px; border-radius: 50%; background-color: #0B111E; background-size: cover, cover, 84% 84%; background-position: top center, top center, center center; background-repeat: no-repeat; border: 2px solid rgba(255, 255, 255, 0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.5); }",
    ".badge-cap, .badge-vc, .badge-flag, .badge-sub, .badge-new { position: absolute; font-weight: 900; padding: 1px 5px; border-radius: 5px; border: 1px solid #FFF; font-size:8.5px; z-index:2; }",
    ".badge-cap { bottom: -2px; right: -4px; background: #FBBF24; color: #000; }",
    ".badge-vc { bottom: -2px; right: -4px; background: #CBD5E1; color: #000; }",
    ".badge-flag { top: -3px; left: -4px; background: var(--accent-rose); color: #FFF; }",
    ".badge-sub { top: -3px; left: -4px; background: #334155; color: #F8FAFC; }",
    ".badge-new { top: -4px; right: -6px; background: #06B6D4; color: #070B12; box-shadow: 0 0 10px rgba(6,182,212,0.8); }",
    ".node-name { font-size: 11px; font-weight: 800; color: #FFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 96%; }",
    ".node-meta { font-size: 9.5px; color: #CBD5E1; font-family: 'JetBrains Mono', monospace; margin: 2px 0 4px 0; }",
    ".fdr-pill { font-size: 9px; font-weight: 800; padding: 2px 4px; border-radius: 4px; width: 92%; margin-bottom: 4px; }",
    ".fdr-1 { background: var(--fdr-1); color: #FFF; } .fdr-2 { background: var(--fdr-2); color: #052E16; } .fdr-3 { background: var(--fdr-3); color: #F8FAFC; } .fdr-4 { background: var(--fdr-4); color: #FFF; } .fdr-5 { background: var(--fdr-5); color: #FFF; }",
    ".node-dossier-btn { font-size: 9px; font-weight: 800; text-transform: uppercase; background: rgba(0, 255, 133, 0.12); color: #00FF85; border: 1px solid rgba(0, 255, 133, 0.35); border-radius: 5px; padding: 2px 0; width: 92%; }",
    
    "/* Grids & Utilities */",
    ".kpi-grid-6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }",
    ".kpi-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }",
    ".stat-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 8px; }",
    ".stat-box { background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border-glass); border-radius: 12px; padding: 10px 12px; }",
    ".stat-box-lbl { font-size: 9px; color: var(--text-secondary); text-transform: uppercase; font-weight: 700; }",
    ".stat-box-val { font-size: 14.5px; font-weight: 800; color: #FFF; font-family: 'JetBrains Mono', monospace; margin-top: 2px; }",
    ".ml-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }",
    ".ml-table th { text-align: left; padding: 12px; font-size: 10.5px; text-transform: uppercase; color: var(--text-secondary); border-bottom: 1px solid var(--border-glass); }",
    ".ml-table td { padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }",
    ".ml-row-me { background: rgba(0, 255, 133, 0.11); font-weight: 700; }",
    ".buy-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 10px; }",
    
    "/* Specific Components */",
    ".bench-label { font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px; display: flex; justify-content: space-between; }",
    ".dossier-top { display: flex; align-items: center; gap: 14px; padding-bottom: 12px; border-bottom: 1px solid var(--border-glass); margin-bottom: 12px; }",
    ".dossier-avatar-circle { width: 84px; height: 84px; border-radius: 50%; flex-shrink: 0; background-color: #070B12; background-size: cover, cover, 82% 82%; background-position: top center, top center, center center; background-repeat: no-repeat; border: 3px solid #00FF85; }",
    ".runway-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }",
    ".playbook-card { background: linear-gradient(160deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%); backdrop-filter: blur(16px); border: 1.5px solid var(--border-glass); border-radius: 16px; padding: 16px; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.35); position: relative; z-index: 1; }",
    ".playbook-card.active-pb { border: 2px solid #00FF85; box-shadow: 0 0 24px rgba(0, 255, 133, 0.25); }",
    ".verdict-banner { background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(15, 23, 42, 0.6) 100%); backdrop-filter: blur(12px); border: 1.5px solid rgba(0, 255, 133, 0.4); border-radius: 16px; padding: 14px 18px; margin-bottom: 14px; }",
    
    "/* Global Tag Colors & Streamlit Buttons */",
    ".delta-up { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25); }",
    ".delta-down { background: rgba(244, 63, 94, 0.15); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.25); }",
    ".delta-warn { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.25); }",
    ".delta-info { background: rgba(6, 182, 212, 0.15); color: #22D3EE; border: 1px solid rgba(6, 182, 212, 0.25); }",
    ".delta-neutral { background: rgba(148, 163, 184, 0.14); color: #CBD5E1; }",
    "div.stButton > button { background: rgba(15, 23, 42, 0.6) !important; color: var(--text-primary) !important; border: 1px solid rgba(255, 255, 255, 0.12) !important; border-radius: 10px !important; font-weight: 700 !important; transition: all 0.2s ease !important; }",
    "div.stButton > button:hover { border-color: #00FF85 !important; background: rgba(30, 41, 59, 0.95) !important; }",
    "div.stButton > button[kind='primary'] { background: linear-gradient(135deg, #00FF85 0%, #10B981 100%) !important; color: #070B12 !important; border: 1.5px solid #FFFFFF !important; font-weight: 900 !important; box-shadow: 0 0 18px rgba(0, 255, 133, 0.35) !important; }",
    "</style>",
]
render_html(CSS_LINES)

if not st.session_state.get("authenticated", False):
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        render_html([
            "<div class='dossier-card' style='text-align: center; margin-top: 40px;'>",
            "<h2 style='margin:0; font-weight:900; color:#FFF; letter-spacing:0.8px;'>KINGS COUNTY FC</h2>",
            "<p style='color:#00FF85; font-size:11.5px; font-weight:800; letter-spacing:1.6px; margin-top:4px;'>",
            "FPL TACTICAL COMMAND & MINI-LEAGUE ENGINE</p></div>",
        ])
        with st.form("auth_form"):
            pw = st.text_input("Manager Access Key", type="password")
            tid_input = st.number_input("FPL Entry ID", value=int(st.session_state.get("team_id", default_team_id)), step=1)
            if st.form_submit_button("Launch Tactical Command", use_container_width=True):
                if pw == auth_secret or auth_secret == "":
                    st.session_state["authenticated"] = True
                    st.session_state["team_id"] = int(tid_input)
                    st.query_params["auth"] = "passed"
                    st.query_params["team_id"] = str(tid_input)
                    st.rerun()
                else:
                    st.error("Invalid Manager Access Key.")
    st.stop()

# ---------------------------------------------------------
# 4. CLUB KIT SVG GENERATOR & MULTI-LAYER PHOTO URL BUILDER
# ---------------------------------------------------------
CLUB_PALETTES = {
    "ARS": {"p": "#EF0107", "s": "#FFFFFF"}, "AVL": {"p": "#670E36", "s": "#95BFE5"},
    "BOU": {"p": "#DA291C", "s": "#000000"}, "BRE": {"p": "#E30613", "s": "#FFFFFF"},
    "BHA": {"p": "#0057B8", "s": "#FFFFFF"}, "BUR": {"p": "#6C1D45", "s": "#99D6EA"},
    "CHE": {"p": "#034694", "s": "#FFFFFF"}, "COV": {"p": "#0593D0", "s": "#FFFFFF"},
    "CRY": {"p": "#1B458F", "s": "#C4122E"}, "EVE": {"p": "#003399", "s": "#FFFFFF"},
    "FUL": {"p": "#FFFFFF", "s": "#000000"}, "IPS": {"p": "#0055A5", "s": "#FFFFFF"},
    "LEI": {"p": "#0053A0", "s": "#FFFFFF"}, "LIV": {"p": "#C8102E", "s": "#FFFFFF"},
    "MCI": {"p": "#6CABDD", "s": "#FFFFFF"}, "MUN": {"p": "#DA291C", "s": "#000000"},
    "NEW": {"p": "#241F20", "s": "#FFFFFF"}, "NFO": {"p": "#DD0000", "s": "#FFFFFF"},
    "SOU": {"p": "#D71920", "s": "#FFFFFF"}, "TOT": {"p": "#FFFFFF", "s": "#132257"},
    "WHU": {"p": "#7A263A", "s": "#1BB1E7"}, "WOL": {"p": "#FDB913", "s": "#231F20"},
    "DEFAULT": {"p": "#1E293B", "s": "#00FF85"},
}

def generate_svg_kit(team_short: str, is_gk: bool = False) -> str:
    c = CLUB_PALETTES.get(str(team_short).upper(), CLUB_PALETTES["DEFAULT"])
    pc, sc = ("#10B981", "#090D16") if is_gk else (c["p"], c["s"])
    lbl = str(team_short)[:3]
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'><path d='M25,18 L10,32 L20,40 L26,33 L26,65 L54,65 L54,33 L60,40 L70,32 L55,18 C50,23 30,23 25,18 Z' fill='{pc}' stroke='{sc}' stroke-width='2'/><text x='40' y='49' font-family='sans-serif' font-weight='800' font-size='11' fill='{sc}' text-anchor='middle'>{lbl}</text></svg>"
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

def build_avatar_bg_style(p: dict) -> str:
    raw_code = str(safe_get(p, "code", str(safe_get(p, "photo", "")).split(".")[0])).lstrip("p").strip()
    ts = safe_get(p, "team_short", "EPL")
    gk_flag = (safe_get(p, "element_type", 3) == 1)
    return f"background-image: url('https://resources.premierleague.com/premierleague25/photos/players/110x140/{raw_code}.png'), url('https://resources.premierleague.com/premierleague/photos/players/110x140/p{raw_code}.png'), url(\"{generate_svg_kit(ts, gk_flag)}\");"

def build_pitch_node_html(p: dict, is_selected: bool = False, bench_slot=None) -> str:
    bg = build_avatar_bg_style(p)
    isc, isv, isnew = safe_get(p, "is_captain", False), safe_get(p, "is_vice_captain", False), safe_get(p, "is_sandbox_new", False)
    cb = "<div class='badge-cap'>C</div>" if isc else ("<div class='badge-vc'>V</div>" if isv else "")
    nb = "<div class='badge-new'>NEW</div>" if isnew else ""
    ch = p.get("chance_of_playing_next_round")
    fb = f"<div class='badge-flag'>{'OUT' if int(ch)==0 else f'{ch}%'}</div>" if ch is not None and int(ch)<100 else (f"<div class='badge-sub'>SUB {bench_slot}</div>" if bench_slot else "")
    rw = safe_get(p, "runway", [])
    nx = rw[0] if rw else {"opp": "TBD", "venue": "H", "fdr": 3}
    sc = "selected" if is_selected else ("sandbox-new" if isnew else "")
    pr = float(safe_get(p, "now_cost", 50)) / 10.0
    u = f"?auth=passed&team_id={team_id}&lg_id={st.session_state.get('target_lg_id','')}&pid={safe_get(p, 'id', 0)}#player-dossier"
    return "".join([
        f"<a class='pitch-node-link' href='{u}' target='_self'><div class='pitch-node {sc}'>",
        f"<div class='node-avatar-wrap'><div class='node-avatar-circle' style=\"{bg}\"></div>{cb}{fb}{nb}</div>",
        f"<div class='node-name'>{safe_get(p, 'web_name', 'Player')}</div><div class='node-meta'>£{pr:.1f}m &bull; {safe_get(p, 'xp_next', 0.0)}xP</div>",
        f"<div class='fdr-pill fdr-{safe_get(nx, 'fdr', 3)}'>{safe_get(nx, 'opp', 'TBD')} ({safe_get(nx, 'venue', 'H')})</div><div class='node-dossier-btn'>Dossier</div></div></a>"
    ])

# ---------------------------------------------------------
# 5. UNIVERSAL FPL API ENGINE
# ---------------------------------------------------------
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Cache-Control": "no-cache"}

@st.cache_data(ttl=180)
def fetch_bootstrap(nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/bootstrap-static/?_={nonce}", headers=HEADERS, timeout=8)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=180)
def fetch_fixtures(nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/fixtures/?_={nonce}", headers=HEADERS, timeout=8)
        return r.json() if r.status_code == 200 else []
    except: return []

@st.cache_data(ttl=120)
def fetch_private_my_team(tid: int, raw_c: str = "", tok: str = "", em: str = "", pw: str = "", n: int = 0):
    diag = {"attempted": False, "authenticated": False, "status_code": None, "method_used": "None", "message": "Using Snapshot."}
    raw = (raw_c or "").strip()
    ext = (tok or "").strip()
    if not any([raw, ext, (em and pw)]): return None, diag
    diag["attempted"] = True
    session = requests.Session()
    req_headers = dict(HEADERS)
    req_headers.update({"Origin": "https://fantasy.premierleague.com", "Referer": f"https://fantasy.premierleague.com/my-team/{tid}"})
    m_tried = []
    def set_b(t_str):
        cj = t_str.replace("Bearer ", "").replace("bearer ", "").strip().strip('"').strip("'")
        req_headers["Authorization"] = f"Bearer {cj}"
        req_headers["x-api-authorization"] = f"Bearer {cj}"

    if em and pw and not raw and not ext:
        try:
            session.post("https://users.premierleague.com/accounts/login/", data={"login": em, "password": pw, "app": "plfpl-web", "redirect_uri": "https://fantasy.premierleague.com/a/login"}, headers=req_headers, timeout=7)
            m_tried.append("Auto-Login")
        except: pass
    if raw.startswith("curl "):
        m_tried.append("cURL")
        for hm in re.finditer(r"(?:-H|--header)\s+\$?['\"]([^:]+):\s*([^'\"]+)['\"]", raw):
            hn, hv = hm.group(1).strip(), hm.group(2).strip()
            if hn.lower() in ("x-api-authorization", "authorization"): set_b(hv)
            elif hn.lower() == "cookie": req_headers["Cookie"] = hv
    if ext: set_b(ext); m_tried.append("Token")
    jwt = re.search(r"(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})", raw)
    if jwt: set_b(jwt.group(1)); m_tried.append("JWT")
    elif "=" in raw and not raw.startswith("curl "): req_headers["Cookie"] = raw; m_tried.append("Cookie")
    
    ul = " + ".join(m_tried) if m_tried else "Auto"
    diag["method_used"] = ul
    try:
        r = session.get(f"https://fantasy.premierleague.com/api/my-team/{tid}/?_={n}", headers=req_headers, timeout=8)
        diag["status_code"] = r.status_code
        if r.status_code == 200:
            d = r.json()
            if isinstance(d, dict) and "picks" in d:
                diag["authenticated"] = True; diag["message"] = f"200 OK via {ul}."
                return d, diag
        diag["message"] = f"HTTP {r.status_code}. Using Snapshot."
    except Exception as e: diag["message"] = f"Error ({e}). Using Snapshot."
    return None, diag

@st.cache_data(ttl=60)
def fetch_manager_full(tid: int, n: int = 0):
    try:
        b = f"https://fantasy.premierleague.com/api/entry/{tid}"
        ent = requests.get(f"{b}/?_={n}", headers=HEADERS, timeout=8).json()
        hst = requests.get(f"{b}/history/?_={n}", headers=HEADERS, timeout=8).json()
        trs = requests.get(f"{b}/transfers/?_={n}", headers=HEADERS, timeout=8).json()
        cg = int(safe_get(ent, "current_event", 6))
        pks = requests.get(f"{b}/event/{cg}/picks/?_={n}", headers=HEADERS, timeout=8).json()
        return ent, hst, trs, pks, cg
    except: return {}, {}, [], {}, 6

@st.cache_data(ttl=300)
def fetch_event_live(gw: int, n: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/event/{gw}/live/?_={n}", headers=HEADERS, timeout=8)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=120)
def fetch_league_standings(lg_id: int, n: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/leagues-classic/{lg_id}/standings/?_={n}", headers=HEADERS, timeout=8)
        return r.json() if r.status_code == 200 else None
    except: return None

@st.cache_data(ttl=120)
def fetch_rival_picks(rv_id: int, gw: int, n: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/entry/{rv_id}/event/{gw}/picks/?_={n}", headers=HEADERS, timeout=6)
        return r.json() if r.status_code == 200 else None
    except: return None

sync_nonce = int(st.session_state.get("sync_nonce", 0))
bootstrap = fetch_bootstrap(sync_nonce) or {"elements": [], "teams": [], "events": []}
fixtures_list = fetch_fixtures(sync_nonce)
team_id = int(st.session_state.get("team_id", default_team_id))
entry_data, history_data, transfers_list, public_picks_data, last_active_gw = fetch_manager_full(team_id, sync_nonce)

fpl_cookie_val = st.session_state.get("custom_fpl_cookie") or st.secrets.get("FPL_COOKIE", "") or st.secrets.get("FLP_COOKIE", "")
fpl_token_val = st.session_state.get("custom_fpl_token") or st.secrets.get("FPL_BEARER_TOKEN", "")
fpl_email_val = st.session_state.get("custom_fpl_email") or st.secrets.get("FPL_EMAIL", "")
fpl_pass_val = st.session_state.get("custom_fpl_password") or st.secrets.get("FPL_PASSWORD", "")

private_team_data, auth_diag = fetch_private_my_team(team_id, fpl_cookie_val, fpl_token_val, fpl_email_val, fpl_pass_val, sync_nonce)

elements_map = {p["id"]: dict(p) for p in safe_get(bootstrap, "elements", []) if isinstance(p, dict) and "id" in p}
teams_map = {t["id"]: dict(t) for t in safe_get(bootstrap, "teams", []) if isinstance(t, dict) and "id" in t}
events_list = safe_get(bootstrap, "events", [])
events_map = {e["id"]: dict(e) for e in events_list if isinstance(e, dict) and "id" in e}

# ---------------------------------------------------------
# 6. COUNTDOWN & RUNWAY ENGINE
# ---------------------------------------------------------
next_event_obj = next((e for e in events_list if safe_get(e, "is_next")), None)
if not next_event_obj: next_event_obj = next((e for e in events_list if not safe_get(e, "finished")), safe_get(events_map, last_active_gw, {}))
upcoming_gw = int(safe_get(next_event_obj, "id", last_active_gw + 1))
deadline_iso = safe_get(next_event_obj, "deadline_time")

countdown_display = f"GW{upcoming_gw} UPCOMING"
if deadline_iso:
    try:
        dl_dt = datetime.fromisoformat(str(deadline_iso).replace("Z", "+00:00"))
        diff_sec = (dl_dt - datetime.now(timezone.utc)).total_seconds()
        if diff_sec > 86400: countdown_display = f"{int(diff_sec//86400)}d {int((diff_sec%86400)//3600)}h remaining"
        elif diff_sec > 0: countdown_display = f"{int(diff_sec//3600)}h {int((diff_sec%3600)//60)}m remaining"
        else: countdown_display = "LOCKED / IN PROGRESS"
    except: pass

team_runway = {t_id: [] for t_id in teams_map}
for fix in fixtures_list:
    ev = safe_get(fix, "event")
    if not safe_get(fix, "finished") and ev and int(ev) >= upcoming_gw:
        hid, aid = safe_get(fix, "team_h"), safe_get(fix, "team_a")
        hs, as_ = safe_get(teams_map.get(hid, {}), "short_name", "TBD"), safe_get(teams_map.get(aid, {}), "short_name", "TBD")
        if hid in team_runway and len(team_runway[hid]) < 5: team_runway[hid].append({"gw": int(ev), "opp": as_, "venue": "H", "fdr": int(safe_get(fix, "team_h_difficulty", 3))})
        if aid in team_runway and len(team_runway[aid]) < 5: team_runway[aid].append({"gw": int(ev), "opp": hs, "venue": "A", "fdr": int(safe_get(fix, "team_a_difficulty", 3))})

# ---------------------------------------------------------
# 7. HISTORICAL LEARNING & XP CALCULATOR
# ---------------------------------------------------------
live_last_gw = fetch_event_live(last_active_gw, sync_nonce)
live_pts_map = {safe_get(el, "id"): int(safe_get(safe_get(el, "stats", {}), "total_points", 0)) for el in safe_get(live_last_gw, "elements", []) if safe_get(el, "id") is not None} if live_last_gw else {}

top_actual = sorted(elements_map.values(), key=lambda x: live_pts_map.get(safe_get(x, "id"), 0), reverse=True)[:25]
w_form = 0.58 if (sum(float(safe_get(p, "form", 0.0) or 0.0) for p in top_actual) / 25.0) >= 5.0 else 0.46
w_xgi = 4.4 if (sum(float(safe_get(p, "expected_goal_involvements", 0.0) or 0.0) for p in top_actual) / 25.0) >= 2.2 else 3.8
calibration_note = f"Calibrated on GW{last_active_gw} actuals: Form Weight {int(w_form * 100)}% | xGI Multiplier {w_xgi}x"

purchase_price_map = {safe_get(tr, "element_in"): int(safe_get(tr, "element_in_cost")) for tr in transfers_list if safe_get(tr, "element_in") and safe_get(tr, "element_in_cost")}

def compute_player_xp(p: dict):
    form = float(safe_get(p, "form", 0.0) or 0.0)
    xgi = float(safe_get(p, "expected_goal_involvements", 0.0) or 0.0)
    mins = max(int(safe_get(p, "minutes", 0) or 0), 1)
    xgi_p90 = (xgi / mins) * 90.0 if mins >= 90 else form * 0.12
    rw = team_runway.get(safe_get(p, "team"), [])
    nx_fdr = int(rw[0]["fdr"]) if rw else 3
    av_fdr = sum(int(r["fdr"]) for r in rw[:5]) / len(rw[:5]) if rw else 3.0
    rc = p.get("chance_of_playing_next_round")
    chc = (float(rc) if rc is not None else 100.0) / 100.0
    bs = (form * w_form) + (xgi_p90 * w_xgi) + 1.8
    f_map = {1: 1.35, 2: 1.2, 3: 1.0, 4: 0.82, 5: 0.68}
    xp1 = round(bs * f_map.get(nx_fdr, 1.0) * chc, 1)
    gws = []
    for i in range(5):
        fw = int(rw[i]["fdr"]) if i < len(rw) else 3
        cw = chc if i == 0 else min(1.0, chc + 0.15)
        gws.append(round(bs * f_map.get(fw, 1.0) * cw, 1))
    return xp1, round(sum(gws), 1), nx_fdr, round(av_fdr, 2), gws

for pid, p_obj in elements_map.items():
    x1, x5, nf, af, gs = compute_player_xp(p_obj)
    p_obj.update({"xp_next": x1, "xp_5gw": x5, "next_fdr": nf, "avg_5_fdr": af, "xp_series": gs})
    to = safe_get(teams_map, safe_get(p_obj, "team"), {})
    p_obj.update({"team_short": safe_get(to, "short_name", "EPL"), "team_name": safe_get(to, "name", "PL"), "runway": team_runway.get(safe_get(p_obj, "team"), [])})
    p_obj["last_gw_pts"] = live_pts_map.get(pid, int(safe_get(p_obj, "event_points", 0)))
    nc = int(safe_get(p_obj, "now_cost", 50))
    bc = purchase_price_map.get(pid, nc - int(safe_get(p_obj, "cost_change_start", 0)))
    p_obj["selling_price"] = ((bc + (nc - bc) // 2) / 10.0) if nc > bc else (nc / 10.0)

# ---------------------------------------------------------
# 8. BASELINE MATH & ROSTER BUILDER
# ---------------------------------------------------------
curr_hist = safe_get(history_data, "current", [])
chips_used = {safe_get(c, "event"): safe_get(c, "name") for c in safe_get(history_data, "chips", [])}
gw_avg = int(safe_get(safe_get(events_map, last_active_gw, {}), "average_entry_score", 50))

ft_pub = 1
for hr in curr_hist:
    en = int(safe_get(hr, "event", 1))
    if en == 1: ft_pub = 1; continue
    ut = int(safe_get(hr, "event_transfers", 0))
    if chips_used.get(en) in ("wildcard", "freehit"): ft_pub = min(5, max(1, ft_pub))
    else: ft_pub = min(5, max(0, ft_pub - ut) + 1)

ft_rem_pub = max(0, ft_pub - len([t for t in transfers_list if safe_get(t, "event") == upcoming_gw]))

if len(curr_hist) >= 2:
    lh, ph = curr_hist[-1], curr_hist[-2]
    total_pts, gw_pts = int(safe_get(lh, "total_points", 0)), int(safe_get(lh, "points", 0))
    overall_rank = int(safe_get(lh, "overall_rank", 0))
    rank_delta = int(safe_get(ph, "overall_rank", overall_rank)) - overall_rank
    bank_public, bank_delta = int(safe_get(lh, "bank", 0)) / 10.0, (int(safe_get(lh, "bank", 0)) - int(safe_get(ph, "bank", 0))) / 10.0
    val_public, val_delta = int(safe_get(lh, "value", 1000)) / 10.0, (int(safe_get(lh, "value", 1000)) - int(safe_get(ph, "value", 1000))) / 10.0
else:
    total_pts = int(safe_get(entry_data, "summary_overall_points", 407))
    gw_pts = int(safe_get(entry_data, "summary_event_points", 60))
    overall_rank = int(safe_get(entry_data, "summary_overall_rank", 1219150))
    rank_delta = bank_delta = val_delta = 0.0
    bank_public = int(safe_get(entry_data, "last_deadline_bank", 1)) / 10.0
    val_public = int(safe_get(entry_data, "last_deadline_value", 1009)) / 10.0

if safe_get(auth_diag, "authenticated") and isinstance(private_team_data, dict) and safe_get(private_team_data, "picks"):
    tm = safe_get(private_team_data, "transfers", {})
    save_team_snapshot(team_id, {
        "team_id": team_id, "target_gw": upcoming_gw, "public_gw_at_sync": last_active_gw, "updated_at": now_ny_str(),
        "picks": private_team_data["picks"],
        "bank_m": round((float(tm.get("bank")) / 10.0) if tm.get("bank") is not None else bank_public, 1),
        "ft_remaining": max(0, int(tm.get("limit")) - int(safe_get(tm, "made", 0))) if tm.get("limit") is not None else ft_rem_pub,
        "squad_value_m": round((float(tm.get("value")) / 10.0) if tm.get("value") is not None else val_public, 1)
    })

saved_snapshot = load_team_snapshot(team_id)
use_saved = isinstance(saved_snapshot, dict) and safe_get(saved_snapshot, "picks") and (int(safe_get(saved_snapshot, "target_gw", upcoming_gw)) >= upcoming_gw or last_active_gw < int(safe_get(saved_snapshot, "target_gw", upcoming_gw)))

gw6_raw = [dict(pk) for pk in safe_get(public_picks_data, "picks", []) if isinstance(pk, dict)]
if use_saved:
    cur_pks = [dict(pk) for pk in saved_snapshot["picks"]]
    bank_now, ft_now, val_now = float(safe_get(saved_snapshot, "bank_m", bank_public)), int(safe_get(saved_snapshot, "ft_remaining", ft_rem_pub)), float(safe_get(saved_snapshot, "squad_value_m", val_public))
    team_upd_safe = str(safe_get(saved_snapshot, "updated_at", now_ny_str()))
    st.session_state["team_updated_str"] = team_upd_safe
    roster_sync_mode, roster_mode_cls = ("LIVE TOKEN SYNCED", "delta-up") if safe_get(auth_diag, "authenticated") else ("PERSISTED LATEST PULL", "delta-up")
else:
    cur_pks = [dict(pk) for pk in gw6_raw]
    gwt = [t for t in reversed(transfers_list) if safe_get(t, "event") == upcoming_gw]
    for tr in gwt:
        oe, ie = safe_get(tr, "element_out"), safe_get(tr, "element_in")
        for pk in cur_pks:
            if safe_get(pk, "element") == oe and ie in elements_map:
                pk["element"] = ie
                break
    bank_now, ft_now, val_now = bank_public, ft_rem_pub, val_public
    team_upd_safe = f"GW{last_active_gw} Public Lock ({len(gwt)} Moves)"
    st.session_state["team_updated_str"] = team_upd_safe
    roster_sync_mode, roster_mode_cls = ("PUBLIC ROLL-FORWARD", "delta-warn")

def build_roster(pks, apply_cap=True, sb_new=None):
    sxi, bxi = [], []
    ns = sb_new or set()
    for pk in pks:
        bp = elements_map.get(safe_get(pk, "element"))
        if bp:
            cp = dict(bp)
            if pk.get("selling_price"): cp["selling_price"] = float(pk.get("selling_price")) / 10.0 if float(pk.get("selling_price")) > 25 else float(pk.get("selling_price"))
            if apply_cap and st.session_state.get("cap_override_id") is not None: cp["is_captain"] = (cp["id"] == st.session_state.get("cap_override_id"))
            else: cp["is_captain"] = bool(safe_get(pk, "is_captain", False))
            if apply_cap and st.session_state.get("vc_override_id") is not None: cp["is_vice_captain"] = (cp["id"] == st.session_state.get("vc_override_id") and not cp["is_captain"])
            else: cp["is_vice_captain"] = (bool(safe_get(pk, "is_vice_captain", False)) and not cp["is_captain"])
            cp["is_sandbox_new"] = (cp["id"] in ns)
            cp["pick_pos"] = int(safe_get(pk, "position", 1))
            (sxi if cp["pick_pos"] <= 11 else bxi).append(cp)
    return sxi, bxi, sxi + bxi

gw6_sxi, gw6_bxi, gw6_full = build_roster(gw6_raw, False)
sxi, bxi, full = build_roster(cur_pks, True)

act_cap = next((p for p in sxi if safe_get(p, "is_captain")), sxi[0] if sxi else {})
act_vc = next((p for p in sxi if safe_get(p, "is_vice_captain")), sxi[1] if len(sxi) > 1 else {})
cap_name, vc_name = safe_get(act_cap, "web_name", "N/A"), safe_get(act_vc, "web_name", "N/A")
if st.session_state.get("selected_pid") is None and full: st.session_state["selected_pid"] = safe_get(act_cap, "id", full[0]["id"])
team_xp = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain") else 1) for p in sxi), 1)
gw6_xp = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain") else 1) for p in gw6_sxi), 1)

# --- CAPTAINCY STRATEGY ENGINE ---
def get_cap_score(p):
    xp = float(safe_get(p, "xp_next", 0.0))
    xgi = float(safe_get(p, "expected_goal_involvements", 0.0))
    fdr = int(safe_get(p, "next_fdr", 3))
    pr = float(safe_get(p, "now_cost", 50)) / 10.0
    fdr_mult = 1.2 if fdr <= 2 else (0.8 if fdr >= 4 else 1.0)
    return (xp * 0.5) + (xgi * 2.5 * fdr_mult) + (pr * 0.2)

cap_cands = sorted([p for p in sxi if (100 if p.get("chance_of_playing_next_round") is None else int(p.get("chance_of_playing_next_round"))) >= 75], key=get_cap_score, reverse=True) or sxi
opt_cap = cap_cands[0] if cap_cands else {}
cap_alert_str = f"✅ <strong>CAPTAIN OPTIMIZED:</strong> {cap_name} is mathematically your strongest armband choice." if safe_get(opt_cap, "id") == safe_get(act_cap, "id") else f"⚠️ <strong>CAPTAINCY ALERT:</strong> You captained {cap_name}, but data heavily favors <strong>{safe_get(opt_cap, 'web_name')}</strong> (Higher xGI/FDR ceiling)."

# --- MINI LEAGUE DATA ---
all_cls = safe_get(safe_get(entry_data, "leagues", {}), "classic", [])
cls_lgs = [lg for lg in all_cls if isinstance(lg, dict) and safe_get(lg, "league_type") == "x"] + [lg for lg in all_cls if isinstance(lg, dict) and int(safe_get(lg, "id", 0)) > 350 and safe_get(lg, "league_type") != "x"] or [lg for lg in all_cls if isinstance(lg, dict) and "id" in lg]
tgt_lg_st, r_threats, r_own = [], {}, set()
gap_ldr, my_rk, tgt_lg_nm = 0, 1, "Mini-League"

if cls_lgs:
    lg_ids = [int(lg["id"]) for lg in cls_lgs if "id" in lg]
    if lg_ids:
        ql = st.query_params.get("lg_id")
        sv_lg = st.session_state.get("target_lg_id")
        if sv_lg not in lg_ids: sv_lg = int(ql) if (ql and str(ql).isdigit() and int(ql) in lg_ids) else lg_ids[0]
        st.session_state["target_lg_id"] = sv_lg
        tgt_lg_nm = next((safe_get(lg, "name", "League") for lg in cls_lgs if int(safe_get(lg, "id", 0)) == sv_lg), "League")
        st_json = fetch_league_standings(sv_lg, sync_nonce)
        if isinstance(st_json, dict):
            tgt_lg_st = safe_get(safe_get(st_json, "standings", {}), "results", [])
            if tgt_lg_st:
                ldr_tot = int(safe_get(tgt_lg_st[0], "total", 0))
                my_r = next((r for r in tgt_lg_st if safe_get(r, "entry") == team_id), None)
                my_pts, my_rk = (int(safe_get(my_r, "total", total_pts)), int(safe_get(my_r, "rank", 1))) if my_r else (total_pts, int(safe_get(next((lg for lg in cls_lgs if int(safe_get(lg, "id", 0)) == sv_lg), {}), "entry_rank", 1) or 1))
                gap_ldr = max(0, ldr_tot - my_pts) if my_rk > 1 else 0
                for rv in [r for r in tgt_lg_st[:4] if safe_get(r, "entry") != team_id][:3]:
                    rvp = fetch_rival_picks(int(safe_get(rv, "entry", 0)), last_active_gw, sync_nonce)
                    if isinstance(rvp, dict) and "picks" in rvp:
                        for pk in safe_get(rvp, "picks", []):
                            if int(safe_get(pk, "position", 1)) <= 11 and safe_get(pk, "element") is not None:
                                r_own.add(safe_get(pk, "element")); r_threats[safe_get(pk, "element")] = r_threats.get(safe_get(pk, "element"), 0) + 1

# ---------------------------------------------------------
# 10. STRATEGIC PLAYBOOK ENGINE (PROVEN FPL TACTICS)
# ---------------------------------------------------------
sq_ids = {p["id"] for p in full if "id" in p}
s_ranks = []
for p in full:
    cv = 100 if p.get("chance_of_playing_next_round") is None else int(p.get("chance_of_playing_next_round"))
    pc = float(safe_get(p, "now_cost", 50)) / 10.0
    urg = ((100 - cv) * 2.0 if cv < 75 else 0) + (40.0 if int(safe_get(p, "minutes", 90)) < 45 else 0) + (25.0 if float(safe_get(p, "expected_goal_involvements", 0.0)) < 0.5 and float(safe_get(p, "avg_5_fdr", 3.0)) >= 3.5 else 0)
    if pc >= 9.0 and cv == 100: urg -= 150.0 # Protect healthy premiums
    s_ranks.append((urg, p))
s_ranks.sort(key=lambda x: x[0], reverse=True)

pri_sell = s_ranks[0][1] if s_ranks else (sxi[0] if sxi else {})
pri_sell_id = safe_get(pri_sell, "id", 0)
pri_sell_val = float(safe_get(pri_sell, "selling_price", float(safe_get(pri_sell, "now_cost", 50)) / 10.0))
pri_pos = safe_get(pri_sell, "element_type", 3)
max_1m_bud = round(pri_sell_val + bank_now, 1)

def get_strat_buys(pos, max_b, avoid=None):
    av = avoid or set()
    cands = []
    for c in elements_map.values():
        cv = 100 if c.get("chance_of_playing_next_round") is None else int(c.get("chance_of_playing_next_round"))
        if safe_get(c, "id") in sq_ids or safe_get(c, "id") in av or safe_get(c, "element_type") != pos or (float(safe_get(c, "now_cost", 999)) / 10.0) > max_b or cv < 75: continue
        cands.append(((float(safe_get(c, "xp_5gw", 0.0)) * 0.6) + (float(safe_get(c, "expected_goal_involvements", 0.0)) * 4.0), c))
    cands.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in cands]

pb_a_cands = get_strat_buys(pri_pos, max_1m_bud)
pb_a_tgt = pb_a_cands[0] if pb_a_cands else pri_sell

if gap_ldr > 0:
    pb_b_tit, pb_b_sub = "PLAYBOOK B: SWORD (CHASING)", "0% Rival Ownership | High xGI Upside"
    pb_b_cands = get_strat_buys(pri_pos, max_1m_bud, avoid=r_own) or [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_tgt, "id")] or pb_a_cands
    pb_b_tgt = pb_b_cands[0] if pb_b_cands else pb_a_tgt
    pb_b_les = f"Trailing by {gap_ldr} pts: {safe_get(pb_b_tgt, 'web_name')} is unowned by rivals but posts elite underlying xGI."
else:
    pb_b_tit, pb_b_sub = "PLAYBOOK B: SHIELD (DEFENDING)", "Blocks Highest-Threat Rival Asset"
    pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") in r_own] or [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_tgt, "id")] or pb_a_cands
    pb_b_tgt = pb_b_cands[0] if pb_b_cands else pb_a_tgt
    pb_b_les = f"Leading {tgt_lg_nm}: acquiring {safe_get(pb_b_tgt, 'web_name')} blocks your chasers' primary differential threat."

f_pairs = []
for dnr in full:
    if safe_get(dnr, "element_type", 3) == 1 or safe_get(dnr, "id") == pri_sell_id: continue
    ds = float(safe_get(dnr, "selling_price", float(safe_get(dnr, "now_cost", 50)) / 10.0))
    ces = get_strat_buys(safe_get(dnr, "element_type", 3), ds - 1.0)
    if ces: f_pairs.append((round(ds - (float(safe_get(ces[0], "now_cost", 45)) / 10.0), 1), dnr, ces[0]))
f_pairs.sort(key=lambda x: x[0], reverse=True)

pb_c_out2 = s_ranks[1][1] if len(s_ranks) > 1 else pri_sell
pb_c_in2 = pb_c_out2
pb_c_tgt = pb_a_tgt

if f_pairs:
    fc, dobj, eobj = f_pairs[0]
    pb_c_out2, pb_c_in2 = dobj, eobj
    ecands = get_strat_buys(pri_pos, round(max_1m_bud + fc, 1), avoid={safe_get(eobj, "id")})
    tprems = [c for c in ecands if (float(safe_get(c, "now_cost", 50)) / 10.0) >= 8.5]
    if tprems: pb_c_tgt = tprems[0]
    elif ecands: pb_c_tgt = ecands[0]

def mk_pb(kid, tit, sub, ol, il, les):
    hp = max(0, len(ol) - ft_now) * -4
    ss = sum(float(safe_get(x, "selling_price", float(safe_get(x, "now_cost", 50)) / 10.0)) for x in ol)
    bs = sum(float(safe_get(x, "now_cost", 50)) / 10.0 for x in il)
    g1 = round(sum(float(safe_get(x, "xp_next", 0.0)) for x in il) - sum(float(safe_get(x, "xp_next", 0.0)) for x in ol) + hp, 1)
    g5 = round(sum(float(safe_get(x, "xp_5gw", 0.0)) for x in il) - sum(float(safe_get(x, "xp_5gw", 0.0)) for x in ol) + hp, 1)
    return {"key": kid, "title": tit, "subtitle": sub, "out_objs": ol, "in_objs": il, "out_ids": [safe_get(x, "id") for x in ol], "in_ids": [safe_get(x, "id") for x in il], "moves_count": len(ol), "hit_cost": hp, "new_bank": round(bank_now + ss - bs, 1), "new_ft": max(0, ft_now - len(ol)), "gw1_delta": g1, "gw5_delta": g5, "runway_str": " ".join(f"[{safe_get(r, 'opp', 'TBD')}]" for r in safe_get(il[0] if il else {}, "runway", [])[:3]) or "[TBD]", "lesson": les}

hit_1m_n = "using 1 FT (0p hit)" if ft_now >= 1 else "requires -4 pt hit"
pb_c_hp = max(0, 2 - ft_now) * -4
PLAYBOOKS = {
    "A": mk_pb("A", "PLAYBOOK A: DATA MAXIMIZER", f"Targeting Elite xGI ({'Free' if ft_now >= 1 else '-4p Hit'})", [pri_sell], [pb_a_tgt], f"Maximizes xP and xGI ({hit_1m_n}). {safe_get(pb_a_tgt, 'web_name')} dominates underlying expected data."),
    "B": mk_pb("B", pb_b_tit, pb_b_sub, [pri_sell], [pb_b_tgt], pb_b_les),
    "C": mk_pb("C", "PLAYBOOK C: PREMIUM SHIFT", f"Downgrade to Fund Heavy Hitter ({pb_c_hp}p Hit)", [pri_sell, pb_c_out2], [pb_c_tgt, pb_c_in2], f"Downgrades {safe_get(pb_c_out2, 'web_name')} to fund a structural upgrade to a premium captaincy option ({safe_get(pb_c_tgt, 'web_name')}). A {pb_c_hp}p hit is justified when securing a permanent captain."),
}

if st.session_state.get("sandbox_transfer_plan") is None: st.session_state["sandbox_transfer_plan"] = PLAYBOOKS["A"]
act_sb = st.session_state.get("sandbox_transfer_plan") or PLAYBOOKS["A"]
sb_out_ids, sb_in_ids = safe_get(act_sb, "out_ids", []), safe_get(act_sb, "in_ids", [])
sb_pks = []
for pk in cur_pks:
    pcp = dict(pk)
    if safe_get(pcp, "element") in sb_out_ids:
        idx = sb_out_ids.index(safe_get(pcp, "element"))
        if idx < len(sb_in_ids) and sb_in_ids[idx] in elements_map:
            pcp["element"] = sb_in_ids[idx]; pcp["selling_price"] = int(safe_get(elements_map[sb_in_ids[idx]], "now_cost", 50))
    sb_pks.append(pcp)

sb_sxi, sb_bxi, sb_full = build_roster(sb_pks, True, set(sb_in_ids))
if not any(safe_get(p, "is_captain") for p in sb_sxi) and sb_sxi: sorted(sb_sxi, key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)[0]["is_captain"] = True
sb_xp = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain") else 1) for p in sb_sxi), 1)

# ---------------------------------------------------------
# 11. TOP HERO BANNER & UNIFIED TELEMETRY
# ---------------------------------------------------------
pl_vec = "".join(["<div class='kcfc-emblem'><svg width='44' height='44' viewBox='0 0 100 100' fill='none' xmlns='http://www.w3.org/2000/svg'>",
"<path d='M34 25 L29 14 L38 18 L36 7 L45 14 L50 5 L55 15 L62 6 L61 17 L68 11 L64 22 Q50 18 34 25 Z' stroke='#070B12' stroke-width='3.8' stroke-linejoin='round'/>",
"<path d='M36 27 Q52 21 63 24 L60 19 Q50 22 36 27 Z' fill='#070B12'/>",
"<path d='M38 28 C48 24 62 24 62 28 C64 25 71 29 73 36 C70 33 65 30 64 33 C59 29 48 29 45 34 C48 35 42 36 41 38 C44 38 45 43 49 44 C55 45 61 45 62 45 C58 39 50 39 47 38 C51 35 55 38 59 36 C59 40 62 43 65 44 C70 43 72 43 73 44 C70 39 66 37 68 36 C72 37 76 38 74 41 C75 42 76 40 77 41 C83 52 85 62 81 74 C79 72 78 70 77 73 C75 84 71 89 65 92 C64 90 64 87 63 89 C55 94 45 94 36 90 C38 82 37 74 36 70 C33 74 29 79 26 81 C22 76 22 67 23 59 C20 60 17 61 17 60 C19 52 22 46 25 42 C23 42 20 43 21 41 C24 35 28 31 32 29 C30 33 32 38 35 38 C33 34 34 30 39 30 C41 30 41 28 38 28 Z' stroke='#070B12' stroke-width='3.8' stroke-linejoin='round'/>",
"<path d='M55 52 L64 47 L69 50 L69 55 L64 59 L58 60 Z' stroke='#070B12' stroke-width='3.8' stroke-linejoin='round'/><path d='M72 51 L75 48 L76 55 L75 59 L72 55 Z' stroke='#070B12' stroke-width='3.5' stroke-linejoin='round'/>",
"<path d='M60 64 L68 59 L72 59 L74 63 L72 68 L69 70 L69 65 L63 68 Z' stroke='#070B12' stroke-width='3.6' stroke-linejoin='round'/></svg></div>"])

render_html([
    "<div class='kcfc-hero'><div class='kcfc-hero-top'>",
    f"<div class='kcfc-hero-brand'>{pl_vec}<div><div class='kcfc-hero-title'>KINGS COUNTY FC</div>",
    f"<div class='kcfc-hero-sub'>TACTICAL COMMAND &bull; {tgt_lg_nm} (#{my_rk})</div></div></div></div>",
    "<div class='telemetry-unified-bar'><div class='telemetry-left'><div class='pulse-dot'></div>",
    f"<div class='countdown-lbl'>GW{upcoming_gw} DEADLINE:</div><div class='countdown-val'>{countdown_display}</div></div>",
    f"<div class='telemetry-right'><span class='kpi-delta {roster_mode_cls}'>{roster_sync_mode}</span>",
    f"<span class='telemetry-pill'>Team Synced: <strong style='color:#00FF85;'>{team_upd_safe}</strong></span></div></div></div>"
])

# ---------------------------------------------------------
# 12. NAVIGATION TABS
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_league, tab_ai, tab_settings = st.tabs(["Tactical Pitch & Dossier", "Transfer Analysis", "Mini-League Spy", "AI Tactical Advisor", "Settings"])

@st.fragment
def render_pitch_and_dossier():
    c_m = st.session_state.get("pitch_view_mode", "current")
    if c_m not in ["gw6", "current", "sandbox"]: c_m = "current"

    pc1, pc2, pc3 = st.columns(3, gap="small")
    with pc1:
        if st.button(f"GW{last_active_gw} Final", use_container_width=True, type="primary" if c_m == "gw6" else "secondary"): st.session_state["pitch_view_mode"] = "gw6"; st.rerun()
    with pc2:
        if st.button(f"GW{upcoming_gw} Live Squad", use_container_width=True, type="primary" if c_m == "current" else "secondary"): st.session_state["pitch_view_mode"] = "current"; st.rerun()
    with pc3:
        x_d = round(sb_xp - team_xp + safe_get(act_sb, "hit_cost", 0), 1)
        if st.button(f"Sandbox ({'+' if x_d>=0 else ''}{x_d} xP)", use_container_width=True, type="primary" if c_m == "sandbox" else "secondary"): st.session_state["pitch_view_mode"] = "sandbox"; st.rerun()

    d_xi, d_bn, d_fl = (gw6_sxi, gw6_bxi, gw6_full) if c_m == "gw6" else ((sb_sxi, sb_bxi, sb_full) if c_m == "sandbox" else (sxi, bxi, full))
    d_ft, d_bk, d_vl, d_xp = (ft_rem_pub, bank_public, val_public, gw6_xp) if c_m == "gw6" else ((safe_get(act_sb, "new_ft", ft_now), safe_get(act_sb, "new_bank", bank_now), val_now, sb_xp) if c_m == "sandbox" else (ft_now, bank_now, val_now, team_xp))
    xds, xcl = (f"Historical GW{last_active_gw}", "delta-neutral") if c_m == "gw6" else ((f"{'+' if x_d>=0 else ''}{x_d} xP ({safe_get(act_sb, 'hit_cost', 0)}p Hit)", "delta-info") if c_m == "sandbox" else (f"C: {cap_name} | V: {vc_name}", "delta-up"))
    gvs = gw_pts - gw_avg
    ft_t, ft_c = ("FT USED (-4 IF URGENT)", "delta-down") if ft_now == 0 else ("USE FT (UPGRADE XI)", "delta-up")

    render_html([
        "<div class='kpi-grid-6'>",
        f"<div class='kpi-card'><div class='kpi-label'>Season Points</div><div class='kpi-value'>{total_pts:,}</div><span class='kpi-delta {'delta-up' if gvs>=0 else 'delta-down'}'>GW{last_active_gw}: {gw_pts}p ({'+' if gvs>=0 else ''}{gvs} vs Avg)</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Overall Rank</div><div class='kpi-value'>{overall_rank:,}</div><span class='kpi-delta {'delta-up' if rank_delta>=0 else 'delta-down'}'>{'▲' if rank_delta>0 else '▼'} {abs(rank_delta):,} vs LW</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Transfers</div><div class='kpi-value' style='color:#FBBF24;'>{d_ft} FT</div><span class='kpi-delta {ft_c}'>{ft_t}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Squad Value</div><div class='kpi-value'>£{d_vl:.1f}m</div><span class='kpi-delta {'delta-up' if val_delta>=0 else 'delta-down'}'>{'+' if val_delta>=0 else ''}£{val_delta:.1f}m vs LW</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>In The Bank</div><div class='kpi-value' style='color:#00FF85;'>£{d_bk:.1f}m</div><span class='kpi-delta delta-up'>{'Synced via Latest Pull' if use_saved else f'{bank_delta:.1f}m vs LW'}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Proj XI</div><div class='kpi-value' style='color:#06B6D4;'>{d_xp} xP</div><span class='kpi-delta {xcl}'>{xds}</span></div></div>"
    ])

    cl, cr = st.columns([1.35, 1], gap="medium")
    s_pid = st.session_state.get("selected_pid")
    with cl:
        gk = "".join(build_pitch_node_html(p, safe_get(p, "id") == s_pid) for p in d_xi if safe_get(p, "element_type") == 1)
        df = "".join(build_pitch_node_html(p, safe_get(p, "id") == s_pid) for p in d_xi if safe_get(p, "element_type") == 2)
        md = "".join(build_pitch_node_html(p, safe_get(p, "id") == s_pid) for p in d_xi if safe_get(p, "element_type") == 3)
        fw = "".join(build_pitch_node_html(p, safe_get(p, "id") == s_pid) for p in d_xi if safe_get(p, "element_type") == 4)
        render_html(["<div class='pitch-wrapper'>", f"<div class='pitch-row'>{gk}</div><div class='pitch-row'>{df}</div><div class='pitch-row'>{md}</div><div class='pitch-row'>{fw}</div></div>"])
        bn = "".join(build_pitch_node_html(p, safe_get(p, "id") == s_pid, i+1) for i, p in enumerate(sorted(d_bn, key=lambda x: int(safe_get(x, "pick_pos", 12)))))
        render_html(["<div class='bench-tray'><div class='bench-label'><span>AUTO-SUB BENCH</span><span style='color:#00FF85;'>TAP PLAYER FOR DOSSIER</span></div>", f"<div class='pitch-row' style='margin-bottom:0;'>{bn}</div></div>"])

    with cr:
        render_html("<div id='player-dossier'></div>")
        sop = {p["id"]: f"{'[NEW] ' if safe_get(p, 'is_sandbox_new') else ''}{'[C] ' if safe_get(p, 'is_captain') else ('[V] ' if safe_get(p, 'is_vice_captain') else '')}{safe_get(p, 'web_name')} ({safe_get(p, 'team_short')} - £{float(safe_get(p, 'now_cost', 50))/10.0:.1f}m | {safe_get(p, 'xp_next')}xP)" for p in d_fl if "id" in p}
        if sop:
            okys = list(sop.keys())
            c_pid = st.selectbox("Quick-Switch Dossier:", options=okys, format_func=lambda x: sop.get(x, ""), index=okys.index(s_pid) if s_pid in okys else 0)
            if c_pid != s_pid: st.session_state["selected_pid"] = c_pid; st.rerun()

        sp = next((x for x in d_fl if safe_get(x, "id") == st.session_state.get("selected_pid")), d_fl[0] if d_fl else None)
        if sp:
            b1, b2 = st.columns(2)
            if b1.button(f"Preview {safe_get(sp, 'web_name')} as Captain (C)", use_container_width=True): st.session_state["cap_override_id"] = safe_get(sp, "id"); st.rerun()
            if b2.button(f"Preview {safe_get(sp, 'web_name')} as Vice (V)", use_container_width=True): st.session_state["vc_override_id"] = safe_get(sp, "id"); st.rerun()
            
            p_pr = float(safe_get(sp, "now_cost", 50)) / 10.0
            sl_v = float(safe_get(sp, "selling_price", p_pr))
            rv_t = f"Owned by {r_threats.get(safe_get(sp, 'id'), 0)}/3 Top Rivals" if r_threats.get(safe_get(sp, "id"), 0) > 0 else "True Differential (0/3 Rivals)"
            r_cp = "".join([f"<div style='background:rgba(255,255,255,0.03); border:1px solid var(--border-glass); border-radius:10px; padding:6px 4px; text-align:center;'><div style='font-size:9px; color:var(--text-secondary);'>GW{safe_get(r, 'gw')}</div><div style='font-size:10.5px; font-weight:700; color:#FFF; margin:2px 0;'>{safe_get(r, 'opp')} ({safe_get(r, 'venue')})</div><span class='fdr-pill fdr-{safe_get(r, 'fdr', 3)}' style='display:inline-block; width:auto; padding:1px 5px;'>FDR {safe_get(r, 'fdr', 3)}</span></div>" for r in safe_get(sp, "runway", [])[:5]])
            n_bn = f"<div style='background:rgba(244,63,94,0.12); border-left:3px solid #F43F5E; padding:8px 10px; border-radius:8px; font-size:11.5px; color:#FDA4AF; margin-bottom:10px;'><strong>Alert:</strong> {safe_get(sp, 'news', '')}</div>" if safe_get(sp, "news", "") else ""
            xp_n = float(safe_get(sp, "xp_next", 0.0))
            vt, vc = ("CAPTAIN / LOCK STARTER", "#00FF85") if xp_n >= 5.5 else (("SOLID ROTATION HOLD", "#06B6D4") if xp_n >= 3.8 else ("UPGRADE CANDIDATE", "#F59E0B"))

            render_html([
                "<div class='dossier-card'><div class='dossier-top'>",
                f"<div class='dossier-avatar-circle' style=\"{build_avatar_bg_style(sp)}\"></div><div style='flex:1;'>",
                f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;'><span style='font-size:19px; font-weight:800; color:#FFF;'>{safe_get(sp, 'first_name', '')} {safe_get(sp, 'second_name', '')}</span><span style='font-size:9.5px; font-weight:800; padding:3px 8px; border-radius:999px; color:{vc}; border:1px solid {vc};'>{vt}</span></div>",
                f"<div style='font-size:11.5px; color:var(--text-secondary); margin-top:4px;'>{ {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}.get(safe_get(sp, 'element_type'), 'PLY') } &bull; <strong>{safe_get(sp, 'team_name', 'PL')}</strong> &bull; TSB: {safe_get(sp, 'selected_by_percent', '0.0')}%</div>",
                f"<div style='font-size:11px; color:#06B6D4; font-weight:700; margin-top:3px;'>{tgt_lg_nm}: {rv_t}</div></div></div>",
                n_bn,
                "<div class='stat-grid-4'>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Buy / Sell</div><div class='stat-box-val'>£{p_pr:.1f}m / <span style='color:#00FF85;'>£{sl_v:.1f}m</span></div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{upcoming_gw} xP</div><div class='stat-box-val' style='color:#00FF85;'>{xp_n}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>5-GW xP</div><div class='stat-box-val' style='color:#06B6D4;'>{safe_get(sp, 'xp_5gw', 0.0)}p</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{last_active_gw} Pts</div><div class='stat-box-val'>{safe_get(sp, 'last_gw_pts', 0)} pts</div></div></div>",
                "<div class='stat-grid-4'>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Form</div><div class='stat-box-val'>{safe_get(sp, 'form', '0.0')}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>xGI</div><div class='stat-box-val'>{safe_get(sp, 'expected_goal_involvements', '0.00')}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>ICT Index</div><div class='stat-box-val'>{safe_get(sp, 'ict_index', '0.0')}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Pts / £m</div><div class='stat-box-val'>{round(float(safe_get(sp, 'total_points', 0)) / max(p_pr, 4.0), 1)}</div></div></div>",
                f"<div style='font-size:10.5px; font-weight:700; text-transform:uppercase; color:var(--text-secondary); margin:10px 0 6px 0;'>5-GW Runway (Avg FDR: {safe_get(sp, 'avg_5_fdr', 3.0)})</div>",
                f"<div class='runway-grid-5'>{r_cp}</div></div>"
            ])

with tab_pitch:
    render_pitch_and_dossier()

    ssl = sorted(sxi, key=lambda x: int(safe_get(x, "last_gw_pts", 0)), reverse=True)
    tpf = [p for p in ssl if int(safe_get(p, "last_gw_pts", 0)) >= 6][:3] or ssl[:2]
    udf = [p for p in sxi if int(safe_get(p, "last_gw_pts", 0)) <= 2 and safe_get(p, "element_type") != 1][:3]
    wit = [f"<strong>{safe_get(p, 'web_name')}</strong> ({safe_get(p, 'news')})" for p in full if safe_get(p, "news")] + [f"<strong>{safe_get(p, 'web_name')}</strong> vs {safe_get(safe_get(p, 'runway', [{'opp':'TBD'}])[0], 'opp')} (Tough FDR)" for p in sxi if int(safe_get(p, "next_fdr", 3)) >= 4]

    render_html([
        "<div class='dossier-card' style='margin-top:16px;'>",
        "<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;'>",
        f"<span style='font-size:15px; font-weight:800; color:#FFF;'>GW{last_active_gw} EXECUTIVE DEBRIEF</span>",
        f"<span style='font-size:10.5px; color:#00FF85;'>{calibration_note}</span></div>",
        cap_alert_str,
        "<div class='buy-grid-3' style='margin-top:14px;'>",
        f"<div style='background:rgba(16,185,129,0.07); border-left:3px solid #00FF85; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#00FF85;'>WHAT WENT WELL</div><div style='font-size:12px; margin-top:4px;'>Scored <strong>{gw_pts} pts</strong>. Top: {', '.join(f'<strong>{safe_get(p, 'web_name')}</strong> ({safe_get(p, 'last_gw_pts')}p)' for p in tpf)}.</div></div>",
        f"<div style='background:rgba(245,158,11,0.07); border-left:3px solid #F59E0B; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#FBBF24;'>AREAS TO IMPROVE</div><div style='font-size:12px; margin-top:4px;'>Left <strong>{sum(int(safe_get(p, 'last_gw_pts', 0)) for p in bxi)} pts</strong> on bench. {'Low returns from ' + ', '.join(safe_get(p, 'web_name', '') for p in udf) + '.' if udf else ''}</div></div>",
        f"<div style='background:rgba(244,63,94,0.07); border-left:3px solid #F43F5E; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#FB7185;'>GW{upcoming_gw} RADAR</div><div style='font-size:12px; margin-top:4px;'>{' &bull; '.join(wit[:4]) or 'No major injury flags across your squad.'}</div></div>",
        "</div></div>"
    ])

# =========================================================
# TAB 2: TRANSFER ANALYSIS & PLANNING
# =========================================================
with tab_transfers:
    render_html([
        "<div class='kpi-grid-4'>",
        f"<div class='kpi-card'><div class='kpi-label'>Free Transfers & Bank</div><div class='kpi-value' style='color:#00FF85;'>{ft_now} FT &bull; £{bank_now:.1f}m</div><span class='kpi-delta {'delta-down' if ft_now==0 else 'delta-up'}'>{'0 FT REMAINING' if ft_now==0 else 'USE FT'}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Max 1-Move Buy Power</div><div class='kpi-value' style='color:#FBBF24;'>£{max_1m_bud:.1f}m</div><span class='kpi-delta delta-neutral'>Via {safe_get(pri_sell, 'web_name')} (£{pri_sell_val:.1f}m)</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Current vs Sandbox XI</div><div class='kpi-value' style='color:#06B6D4;'>{team_xp} &rarr; {sb_xp} xP</div><span class='kpi-delta delta-info'>{'+' if (sb_xp - team_xp + safe_get(act_sb, 'hit_cost', 0))>=0 else ''}{round(sb_xp - team_xp + safe_get(act_sb, 'hit_cost', 0), 1)} Net xP ({safe_get(act_sb, 'hit_cost', 0)}p Hit)</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Mini-League Posture</div><div class='kpi-value'>{'Chasing' if gap_ldr > 0 else '1st Place'}</div><span class='kpi-delta {'delta-warn' if gap_ldr > 0 else 'delta-up'}'>#{my_rk} in {tgt_lg_nm}</span></div></div>"
    ])

    vh, vc, vb = ("EXECUTIVE VERDICT: 0 FT REMAINING", "delta-warn", f"Any move costs a <strong>-4 pt hit</strong>. Your current Starting XI projects for <strong>{team_xp} xP</strong>.") if ft_now == 0 else (f"EXECUTIVE VERDICT: USE 1 FREE TRANSFER", "delta-up", f"Upgrading <strong>{safe_get(pri_sell, 'web_name')}</strong> to <strong>{safe_get(pb_a_tgt, 'web_name')}</strong> adds projected points without taking a hit.")

    render_html([
        "<div class='verdict-banner'><div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:6px;'>",
        f"<span style='font-size:14px; font-weight:900; color:#00FF85;'>{vh}</span><span class='kpi-delta {vc}'>NON-DESTRUCTIVE SANDBOX</span></div>",
        f"<div style='font-size:12.5px; color:#E2E8F0; line-height:1.5;'>{vb}</div></div>"
    ])

    pbc = st.columns(3, gap="medium")
    for i, pk in enumerate(["A", "B", "C"]):
        p = PLAYBOOKS[pk]
        ia = (safe_get(act_sb, "key") == pk)
        os = " + ".join(f"{safe_get(x, 'web_name')} (£{float(safe_get(x, 'selling_price', 5.0)):.1f}m)" for x in safe_get(p, "out_objs", []))
        ins = " + ".join(f"{safe_get(x, 'web_name')} (£{float(safe_get(x, 'now_cost', 50)) / 10.0:.1f}m)" for x in safe_get(p, "in_objs", []))
        with pbc[i]:
            render_html([
                f"<div class='playbook-card {'active-pb' if ia else ''}'>",
                f"<div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:12px; font-weight:900; color:#00FF85;'>{safe_get(p, 'title')}</span><span class='kpi-delta delta-up'>{'+' if safe_get(p, 'gw5_delta', 0)>=0 else ''}{safe_get(p, 'gw5_delta', 0)} xP (5GW)</span></div>",
                f"<div style='font-size:11px; color:var(--text-secondary); margin:4px 0 8px 0;'>{safe_get(p, 'subtitle')}</div>",
                f"<div style='background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:8px;'><div style='font-size:11.5px; color:#FB7185;'><strong>OUT:</strong> {os}</div><div style='font-size:11.5px; color:#00FF85; margin-top:3px;'><strong>IN:</strong> {ins}</div></div>",
                f"<div style='font-size:11px; color:#CBD5E1; line-height:1.5;'>&bull; GW{upcoming_gw} Net: <strong>{'+' if safe_get(p, 'gw1_delta', 0)>=0 else ''}{safe_get(p, 'gw1_delta', 0)} xP</strong> ({safe_get(p, 'hit_cost', 0)}p Hit)<br>&bull; New Bank: <strong>£{safe_get(p, 'new_bank', 0):.1f}m</strong> &bull; Next 3: {safe_get(p, 'runway_str')}</div>",
                f"<div style='font-size:11px; color:#E2E8F0; margin-top:8px; border-left:2px solid #06B6D4; padding-left:8px;'>{safe_get(p, 'lesson')}</div></div>"
            ])
            if st.button("✓ Active in Sandbox" if ia else f"Load Playbook {pk}", key=f"bpb_{pk}", use_container_width=True, type="primary" if ia else "secondary"):
                st.session_state["sandbox_transfer_plan"] = p
                st.session_state["pitch_view_mode"] = "sandbox"
                o, i = safe_get(p, "out_ids", []), safe_get(p, "in_ids", [])
                st.session_state["sb_out_1"] = o[0] if o else pri_sell_id
                st.session_state["sb_in_1"] = i[0] if i else safe_get(pb_a_tgt, "id", 0)
                st.session_state["sb_out_2"] = o[1] if len(o) > 1 else 0
                st.session_state["sb_in_2"] = i[1] if len(i) > 1 else 0
                st.rerun()

    c5s = [0.0] * 5; s5s = [0.0] * 5
    for p in sxi:
        for w in range(5): c5s[w] += (float(safe_get(p, "xp_series", [0]*5)[w]) * (2 if safe_get(p, "is_captain") else 1) if w < len(safe_get(p, "xp_series", [0]*5)) else 0)
    for p in sb_sxi:
        for w in range(5): s5s[w] += (float(safe_get(p, "xp_series", [0]*5)[w]) * (2 if safe_get(p, "is_captain") else 1) if w < len(safe_get(p, "xp_series", [0]*5)) else 0)
    
    c5s, s5s = [round(x, 1) for x in c5s], [round(x, 1) for x in s5s]
    s5s[0] = round(s5s[0] + safe_get(act_sb, "hit_cost", 0), 1)

    dc, cd, bgs = [], 0.0, f"GW{upcoming_gw} (Immediate Gain)" if safe_get(act_sb, "hit_cost", 0) == 0 else "Hit Not Recovered in 5 GWs"
    for w in range(5):
        dw = round(s5s[w] - c5s[w], 1)
        cd = round(cd + dw, 1)
        if safe_get(act_sb, "hit_cost", 0) < 0 and cd >= 0 and "Not Recovered" in bgs: bgs = f"Pays Back {safe_get(act_sb, 'hit_cost', 0)}p Hit by GW{upcoming_gw + w}"
        dc.append(f"<td style='font-family:JetBrains Mono, monospace; color:{'#00FF85' if dw>=0 else '#FB7185'}; font-weight:700;'>{'+' if dw>=0 else ''}{dw} xP</td>")
    n5 = round(sum(s5s) - sum(c5s), 1)

    render_html([
        "<div class='dossier-card' style='margin-top:18px;'><div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;'>",
        f"<span style='font-size:14.5px; font-weight:800; color:#FFF;'>5-GAMEWEEK TRAJECTORY ({safe_get(act_sb, 'title', 'Sandbox')})</span><span class='kpi-delta delta-info'>{bgs}</span></div>",
        "<table class='ml-table'><thead><tr><th>Trajectory</th>" + "".join(f"<th>GW{upcoming_gw + w}</th>" for w in range(5)) + "<th>5-GW Total</th></tr></thead><tbody>",
        f"<tr><td><strong>Current Team</strong></td>{''.join(f'<td style=\"font-family:JetBrains Mono, monospace;\">{x} xP</td>' for x in c5s)}<td style='font-family:JetBrains Mono, monospace; font-weight:800;'>{round(sum(c5s), 1)} xP</td></tr>",
        f"<tr><td><strong style='color:#06B6D4;'>Sandbox Squad</strong></td>{''.join(f'<td style=\"font-family:JetBrains Mono, monospace; color:#06B6D4; font-weight:700;\">{x} xP</td>' for x in s5s)}<td style='font-family:JetBrains Mono, monospace; font-weight:800; color:#06B6D4;'>{round(sum(s5s), 1)} xP</td></tr>",
        f"<tr><td><strong>Net Delta (Incl. Hit)</strong></td>{''.join(dc)}<td style='font-family:JetBrains Mono, monospace; font-weight:900; color:#00FF85;'>{'+' if n5>=0 else ''}{n5} xP</td></tr></tbody></table></div>"
    ])

# =========================================================
# TAB 3: MINI-LEAGUE SPY
# =========================================================
with tab_league:
    if cls_lgs:
        lc1, lc2 = st.columns(2, gap="medium")
        lops = {int(lg["id"]): f"{safe_get(lg, 'name')} (Rank: #{safe_get(lg, 'entry_rank', '?')})" for lg in cls_lgs if "id" in lg}
        lks = list(lops.keys())
        clg = st.session_state.get("target_lg_id", lks[0] if lks else 0)
        if clg not in lks and lks: clg = lks[0]
        
        with lc1:
            slg = st.selectbox("1. Select Your Mini-League:", options=lks, format_func=lambda x: lops.get(x, ""), index=lks.index(clg) if clg in lks else 0)
            if slg != clg: st.session_state["target_lg_id"] = slg; st.query_params["lg_id"] = str(slg); st.rerun()
        
        if tgt_lg_st:
            rmp = {r["entry"]: f"#{safe_get(r, 'rank')} {safe_get(r, 'entry_name')} ({safe_get(r, 'total')} pts)" for r in [r for r in tgt_lg_st[:15] if safe_get(r, "entry") != team_id] if "entry" in r}
            rks = list(rmp.keys())
            with lc2:
                srv = st.selectbox("2. Select Rival for Head-to-Head:", options=rks, format_func=lambda x: rmp.get(x, "")) if rks else 0
            
            rvp_j = fetch_rival_picks(srv, last_active_gw, sync_nonce) if srv else {}
            rvp_l = safe_get(rvp_j, "picks", []) if isinstance(rvp_j, dict) else []
            rxi = {safe_get(k, "element") for k in rvp_l if int(safe_get(k, "position", 1)) <= 11 and safe_get(k, "element") in elements_map}
            rcid = next((safe_get(k, "element") for k in rvp_l if safe_get(k, "is_captain")), None)
            
            mxi = {safe_get(p, "id") for p in sxi if "id" in p}
            sh_xi = mxi.intersection(rxi)
            mdf = sorted([elements_map[i] for i in (mxi - rxi) if i in elements_map], key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)
            rdf = sorted([elements_map[i] for i in (rxi - mxi) if i in elements_map], key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)
            rxp = round(sum(float(safe_get(elements_map[i], "xp_next", 0.0)) * (2 if i == rcid else 1) for i in rxi), 1)
            hsw = round(team_xp - rxp, 1)

            render_html([
                "<div class='kpi-grid-4'>",
                f"<div class='kpi-card'><div class='kpi-label'>League Rank</div><div class='kpi-value'>#{my_rk}</div><span class='kpi-delta {'delta-warn' if gap_ldr>0 else 'delta-up'}'>{'Chasing' if gap_ldr>0 else '1st Place'}</span></div>",
                f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Swing vs Rival</div><div class='kpi-value' style='color:#00FF85;'>{'+' if hsw>=0 else ''}{hsw} xP</div><span class='kpi-delta delta-info'>You: {team_xp} vs {rxp}</span></div>",
                f"<div class='kpi-card'><div class='kpi-label'>Template Overlap</div><div class='kpi-value' style='color:#06B6D4;'>{len(sh_xi)}/11 Shared</div><span class='kpi-delta delta-neutral'>{len(mdf)} Differentials</span></div>",
                f"<div class='kpi-card'><div class='kpi-label'>Captain Matchup</div><div class='kpi-value' style='font-size:15px;'>{cap_name} vs {safe_get(safe_get(elements_map, rcid, {}), 'web_name', 'Unknown')}</div><span class='kpi-delta delta-info'>Armband</span></div></div>"
            ])

            tc, sc = st.columns([1, 1.15], gap="medium")
            with tc:
                tr = "".join(f"<tr class='{'ml-row-me' if safe_get(r, 'entry')==team_id else ''}'><td>#{safe_get(r, 'rank')}</td><td><strong>{safe_get(r, 'entry_name')}</strong><br><span style='font-size:10.5px; color:var(--text-secondary);'>{safe_get(r, 'player_name')}</span></td><td>{safe_get(r, 'event_total')}</td><td>{int(safe_get(r, 'total', 0))}</td><td>{'YOU' if safe_get(r, 'entry')==team_id else ('+' + str(int(safe_get(r, 'total', 0))-my_pts) if int(safe_get(r, 'total', 0))-my_pts > 0 else str(int(safe_get(r, 'total', 0))-my_pts))}</td></tr>" for r in tgt_lg_st[:12])
                render_html([f"<div class='dossier-card'><h4>{tgt_lg_nm} Standings</h4><table class='ml-table'><thead><tr><th>Rk</th><th>Team & Manager</th><th>GW</th><th>Tot</th><th>vs You</th></tr></thead><tbody>{tr}</tbody></table></div>"])
            with sc:
                dr = "".join(f"<tr><td>{f'<strong>{safe_get(mdf[i], 'web_name')}</strong> ({safe_get(mdf[i], 'xp_next')}xP)' if i < len(mdf) else '—'}</td><td>{f'<strong>{safe_get(rdf[i], 'web_name')}</strong> ({safe_get(rdf[i], 'xp_next')}xP)' if i < len(rdf) else '—'}</td></tr>" for i in range(min(max(len(mdf), len(rdf), 1), 7)))
                wk = mdf[-1] if mdf else pri_sell
                ak = get_strat_buys(safe_get(wk, "element_type", 3), round(float(safe_get(wk, "selling_price", 5.0)) + bank_now, 1), avoid=rxi)
                akt = ak[0] if ak else pb_b_tgt
                render_html([
                    "<div class='dossier-card'><h4>Head-to-Head Rival Differentials</h4><p style='font-size:11.5px; color:var(--text-secondary); margin-top:0;'>Strips out shared starters to isolate where points will be won or lost:</p>",
                    f"<table class='ml-table'><thead><tr><th>Your Differentials</th><th>Rival Differentials</th></tr></thead><tbody>{dr}</tbody></table>",
                    f"<div style='margin-top:12px; font-size:12px; background:rgba(0,255,133,0.08); padding:10px; border-radius:10px;'><strong>Recommended Attack Move:</strong> Swap <strong>{safe_get(wk, 'web_name')} &rarr; {safe_get(akt, 'web_name')}</strong> ({safe_get(akt, 'xp_next')} xP) to gain direct differential leverage.</div></div>"
                ])
                if st.button(f"Preview Rival Attack ({safe_get(wk, 'web_name')} → {safe_get(akt, 'web_name')})", use_container_width=True):
                    st.session_state["sandbox_transfer_plan"] = mk_pb("R_ATK", "RIVAL ATTACK", "Differential", [wk], [akt], "Rival attack move.")
                    st.session_state["pitch_view_mode"] = "sandbox"; st.rerun()

# =========================================================
# TAB 4: GEMINI CONVERSATIONAL AI ADVISOR
# =========================================================
with tab_ai:
    render_html([
        "<div class='kpi-grid-4'>",
        f"<div class='kpi-card'><div class='kpi-label'>Active Roster Context</div><div class='kpi-value' style='font-size:14.5px; color:#00FF85;'>{roster_sync_mode}</div><span class='kpi-delta delta-up'>{team_upd_safe}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Budget &amp; Transfers</div><div class='kpi-value' style='color:#FBBF24;'>{ft_now} FT &bull; £{bank_now:.1f}m</div><span class='kpi-delta {'delta-down' if ft_now==0 else 'delta-up'}'>{'0 FT REMAINING' if ft_now==0 else 'USE FT'}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Projected XI</div><div class='kpi-value' style='color:#06B6D4;'>{team_xp} xP</div><span class='kpi-delta delta-info'>C: {cap_name} | Sandbox: {sb_xp}xP</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Mini-League Target</div><div class='kpi-value' style='font-size:15px;'>{'Chasing' if gap_ldr > 0 else '1st Place'}</div><span class='kpi-delta {'delta-warn' if gap_ldr > 0 else 'delta-up'}'>{tgt_lg_nm}</span></div>",
        "</div>",
    ])

    active_gemini_key = str(st.session_state.get("custom_gemini_key") or st.secrets.get("GEMINI_API_KEY", "") or st.secrets.get("GOOGLE_API_KEY", "")).strip()

    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [{"role": "assistant", "content": f"Ready for **GW{upcoming_gw}**, Manager. You have **{ft_now} FT** and **£{bank_now:.1f}m** ITB, competing in **{tgt_lg_nm}** (Rank #{my_rk}). Ask me anything or tap a quick-action button below!"}]

    def ask_gemini_advisor(q_str: str) -> str:
        if not active_gemini_key: return "⚠️ **Gemini API Key Missing:** Please add `GEMINI_API_KEY` in the **Settings** tab."
        xi_sum = ", ".join(f"{safe_get(p, 'web_name')} ({safe_get(p, 'team_short')}, £{float(safe_get(p, 'selling_price', 5.0)):.1f}m, {safe_get(p, 'xp_next')}xP)" for p in sxi)
        sys_p = f"You are the Elite FPL Tactical Coach for Barney's Kings County FC. GW{upcoming_gw}. FT: {ft_now}. Bank: £{bank_now:.1f}m. Target League: {tgt_lg_nm} (Rank #{my_rk}, Gap: {gap_ldr} pts). Captaincy Engine Note: {cap_alert_str}. Starting XI: {xi_sum}. Provide direct, numbers-backed FPL strategy and explain the underlying rationale."
        
        c_pay = []
        for m in st.session_state.get("ai_messages", [])[-8:]:
            rr = "user" if safe_get(m, "role") == "user" else "model"
            txt = str(safe_get(m, "content", "")).strip()
            if not txt or (not c_pay and rr == "model"): continue
            if c_pay and c_pay[-1]["role"] == rr: c_pay[-1]["parts"][0]["text"] += "\n\n" + txt
            else: c_pay.append({"role": rr, "parts": [{"text": txt}]})
        if not c_pay or c_pay[-1]["role"] != "user": c_pay.append({"role": "user", "parts": [{"text": q_str}]})

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro"]
        try:
            rm = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={active_gemini_key}", timeout=6)
            if rm.status_code == 200:
                fnd = [str(safe_get(m, "name", "")).replace("models/", "") for m in safe_get(rm.json(), "models", []) if "generateContent" in safe_get(m, "supportedGenerationMethods", []) and "gemini" in str(safe_get(m, "name", "")) and "embedding" not in str(safe_get(m, "name", ""))]
                fl = [m for m in fnd if "flash" in m] + [m for m in fnd if "pro" in m]
                if fl: models_to_try = fl[:4]
        except: pass

        le = "Unknown API error"
        for mn in models_to_try:
            for us in (True, False):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mn}:generateContent?key={active_gemini_key}"
                pl = {"system_instruction": {"parts": [{"text": sys_p}]}, "contents": c_pay, "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048}}
                if us: pl["tools"] = [{"google_search": {}}]
                try:
                    r = requests.post(url, json=pl, timeout=25)
                    if r.status_code == 200:
                        cds = safe_get(r.json(), "candidates", [])
                        if cds:
                            ot = "\n".join(str(safe_get(pt, "text", "")) for pt in safe_get(safe_get(cds[0], "content", {}), "parts", []) if safe_get(pt, "text")).strip()
                            if ot: return ot
                    else: le = f"HTTP {r.status_code} ({mn}): {safe_get(safe_get(r.json(), 'error', {}) if r.text else {}, 'message', r.text[:160])}"
                except Exception as ex: le = f"{mn} error: {ex}"
        return f"⚠️ **Gemini API Error:** {le}"

    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("Who Should I Start & Bench?", use_container_width=True):
        q = f"Who should I start and bench in GW{upcoming_gw}? Break down any close calls."
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        st.session_state["ai_messages"].append({"role": "assistant", "content": ask_gemini_advisor(q)})
        st.rerun()
    if qa2.button("Is a -4 Hit Worth It?", use_container_width=True):
        q = f"With {ft_now} FT and £{bank_now:.1f}m ITB, should I hold my squad or take a -4 hit?"
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        st.session_state["ai_messages"].append({"role": "assistant", "content": ask_gemini_advisor(q)})
        st.rerun()
    if qa3.button("Captaincy Deep Dive", use_container_width=True):
        q = f"Who is the best Captain and Vice-Captain for GW{upcoming_gw} based on xGI and FDR?"
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        st.session_state["ai_messages"].append({"role": "assistant", "content": ask_gemini_advisor(q)})
        st.rerun()
    if qa4.button("Mini-League Strategy", use_container_width=True):
        q = f"How do I gain ground in {tgt_lg_nm} over the next 3 Gameweeks?"
        st.session_state["ai_messages"].append({"role": "user", "content": q})
        st.session_state["ai_messages"].append({"role": "assistant", "content": ask_gemini_advisor(q)})
        st.rerun()

    for msg in st.session_state.get("ai_messages", []):
        with st.chat_message(safe_get(msg, "role", "assistant")): st.markdown(safe_get(msg, "content", ""))

    user_q = st.chat_input("Ask Gemini about your squad, transfers, or mini-league rivals...")
    if user_q:
        st.session_state["ai_messages"].append({"role": "user", "content": user_q})
        with st.chat_message("user"): st.markdown(user_q)
        with st.chat_message("assistant"):
            reply = ask_gemini_advisor(user_q)
            st.markdown(reply)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

# =========================================================
# TAB 5: SETTINGS & HANDS-FREE CREDENTIALS
# =========================================================
with tab_settings:
    diag_msg = safe_get(auth_diag, "message", "")
    render_html([
        "<div class='dossier-card'>",
        "<h4>LIVE CONNECTION & HANDS-FREE SYNC</h4>",
        f"<p style='font-size:12px; color:var(--text-secondary);'>Active Source: <strong style='color:#00FF85;'>{roster_sync_mode}</strong> | Team Synced: {team_upd_safe} | {diag_msg}</p>",
        "</div>",
    ])
    with st.form("settings_creds_form"):
        in_cookie = st.text_input("FPL Bearer Token / cURL (`FPL_COOKIE`):", value=fpl_cookie_val, type="password")
        in_email = st.text_input("FPL Account Email (`FPL_EMAIL` for Background Auto-Sync):", value=fpl_email_val)
        in_pass = st.text_input("FPL Account Password (`FPL_PASSWORD` for Background Auto-Sync):", value=fpl_pass_val, type="password")
        in_gem = st.text_input("Gemini API Key (`GEMINI_API_KEY`):", value=st.session_state.get("custom_gemini_key") or st.secrets.get("GEMINI_API_KEY", ""), type="password")
        if st.form_submit_button("Sync Live Team & Save Persistent Snapshot", use_container_width=True):
            st.session_state["custom_fpl_cookie"] = in_cookie.strip()
            st.session_state["custom_fpl_email"] = in_email.strip()
            st.session_state["custom_fpl_password"] = in_pass
            st.session_state["custom_gemini_key"] = in_gem.strip()
            st.cache_data.clear()
            st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
            st.session_state["last_synced_str"] = now_ny_str()
            st.rerun()

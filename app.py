"""
KINGS COUNTY FC — FPL TACTICAL COMMAND & MINI-LEAGUE INTELLIGENCE
Production Architecture | Short-Line List-Joined HTML (Anti-Truncation)
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


auth_secret = str(st.secrets.get("APP_PASSWORD", "fpl2025"))
default_team_id = int(st.secrets.get("DEFAULT_TEAM_ID", 1575281))

q_tid = st.query_params.get("team_id")
initial_tid = int(q_tid) if (q_tid and str(q_tid).isdigit()) else default_team_id

DEFAULT_SESSION_STATE = {
    "authenticated": (st.query_params.get("auth") == "passed"),
    "team_id": initial_tid,
    "sync_nonce": 0,
    "last_synced_str": now_ny_str(),
    "team_updated_str": "Not Yet Synced (Using Public GW Roll-Forward)",
    "cap_override_id": None,
    "vc_override_id": None,
    "persisted_team_snapshot": None,
    "selected_pid": None,
    "target_lg_id": None,
    "pitch_view_mode": "current",
    "sandbox_transfer_plan": None,
    "sb_out_1": None,
    "sb_in_1": None,
    "sb_out_2": 0,
    "sb_in_2": 0,
    "custom_fpl_cookie": "",
    "custom_fpl_token": "",
    "custom_fpl_email": "",
    "custom_fpl_password": "",
    "custom_gemini_key": "",
}

for k_state, v_default in DEFAULT_SESSION_STATE.items():
    if k_state not in st.session_state:
        st.session_state[k_state] = v_default

q_pid = st.query_params.get("pid")
if q_pid and str(q_pid).isdigit():
    st.session_state["selected_pid"] = int(q_pid)


def render_html(html_input):
    if isinstance(html_input, list):
        raw_str = "\n".join(str(x) for x in html_input if x)
    else:
        raw_str = str(html_input)
    cleaned = "\n".join(line.lstrip() for line in raw_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. SERVER-SIDE PERSISTENT SNAPSHOT VAULT
# ---------------------------------------------------------
@st.cache_resource
def get_server_snapshot_vault() -> dict:
    return {}


def get_snapshot_filepath(tid: int) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, f".kcfc_snapshot_{int(tid)}.json")


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
    if int(tid) in vault:
        v_snap = vault[int(tid)]
        if isinstance(v_snap, dict) and safe_get(v_snap, "picks"):
            st.session_state["persisted_team_snapshot"] = v_snap
            return v_snap

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
    vault = get_server_snapshot_vault()
    vault.pop(int(tid), None)
    fpath = get_snapshot_filepath(int(tid))
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
        except Exception:
            pass


# ---------------------------------------------------------
# 3. MOBILE-FIRST CSS DESIGN SYSTEM
# ---------------------------------------------------------
components.html(
    "<script>(function(){function n(){try{const d=window.parent.document;"
    "['[class*=\"viewerBadge\"]','[class*=\"profileContainer\"]','[data-testid=\"manage-app-button\"]','[data-testid=\"stStatusWidget\"]','footer','#MainMenu']"
    ".forEach(s=>d.querySelectorAll(s).forEach(e=>{e.style.display='none';}));}catch(e){}}n();setInterval(n,1000);})();</script>",
    height=0,
)

CSS_LINES = [
    "<style>",
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');",
    ":root { --bg-base:#070B12; --bg-surface:#0F172A; --bg-elevated:#1E293B; --border-subtle:rgba(255,255,255,0.08); --accent-emerald:#10B981; --accent-neon:#00FF85; --accent-cyan:#06B6D4; --accent-amber:#F59E0B; --accent-rose:#F43F5E; --text-primary:#F8FAFC; --text-secondary:#94A3B8; --fdr-1:#059669; --fdr-2:#10B981; --fdr-3:#475569; --fdr-4:#D97706; --fdr-5:#E11D48; }",
    "html, body, [class*='css'] { font-family:'Plus Jakarta Sans',sans-serif; color:var(--text-primary); background-color:var(--bg-base); }",
    ".stApp { background:radial-gradient(circle at 50% 0%, #132238 0%, #070B12 62%); }",
    "#MainMenu, header, footer, [data-testid='stHeader'], [data-testid='stToolbar'], [data-testid='stDecoration'], [data-testid='stStatusWidget'], [data-testid='manage-app-button'] { display:none !important; }",
    "iframe[height='0'] { display:none !important; }",
    ".block-container { padding-top:0.6rem !important; padding-bottom:2.5rem !important; max-width:1280px !important; }",
    ".kcfc-hero { background:linear-gradient(135deg, rgba(16,185,129,0.16) 0%, rgba(15,23,42,0.96) 50%, rgba(6,182,212,0.12) 100%); border:1px solid rgba(0,255,133,0.35); border-radius:22px; padding:18px 20px; margin-bottom:8px; display:flex; flex-direction:column; gap:12px; }",
    ".kcfc-hero-top { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }",
    ".kcfc-hero-brand { display:flex; align-items:center; gap:14px; }",
    ".kcfc-emblem { width:54px; height:54px; border-radius:14px; background:linear-gradient(135deg, #00FF85 0%, #10B981 100%); border:2px solid #FFF; display:flex; align-items:center; justify-content:center; }",
    ".kcfc-hero-title { font-size:24px; font-weight:900; color:#FFF; margin:0; text-transform:uppercase; }",
    ".kcfc-hero-sub { font-size:11px; font-weight:800; color:#00FF85; letter-spacing:1.4px; text-transform:uppercase; }",
    ".countdown-bar { background:rgba(7,11,18,0.9); border:1px solid rgba(0,255,133,0.4); border-radius:12px; padding:8px 16px; display:flex; align-items:center; justify-content:space-between; }",
    ".pulse-dot { width:8px; height:8px; border-radius:50%; background:#00FF85; box-shadow:0 0 10px #00FF85; display:inline-block; margin-right:8px; }",
    ".countdown-lbl { font-size:11px; font-weight:800; text-transform:uppercase; color:#E2E8F0; }",
    ".countdown-val { font-size:15px; font-weight:800; color:#00FF85; font-family:'JetBrains Mono',monospace; }",
    ".kpi-grid-6 { display:grid; grid-template-columns:repeat(6, 1fr); gap:10px; margin-bottom:14px; }",
    "@media (max-width:992px) { .kpi-grid-6 { grid-template-columns:repeat(3, 1fr); } }",
    "@media (max-width:640px) { .kpi-grid-6 { grid-template-columns:repeat(2, 1fr); } }",
    ".kpi-grid-4 { display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:14px; }",
    "@media (max-width:860px) { .kpi-grid-4 { grid-template-columns:repeat(2, 1fr); } }",
    ".kpi-card { background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:16px; padding:12px 14px; display:flex; flex-direction:column; justify-content:space-between; }",
    ".kpi-label { font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-secondary); margin-bottom:4px; }",
    ".kpi-value { font-size:19px; font-weight:800; color:var(--text-primary); font-family:'JetBrains Mono',monospace; margin-bottom:6px; }",
    ".kpi-delta { font-size:10px; font-weight:700; padding:3px 7px; border-radius:6px; font-family:'JetBrains Mono',monospace; width:fit-content; }",
    ".delta-up { background:rgba(16,185,129,0.16); color:#34D399; border:1px solid rgba(16,185,129,0.3); }",
    ".delta-down { background:rgba(244,63,94,0.16); color:#FB7185; border:1px solid rgba(244,63,94,0.3); }",
    ".delta-warn { background:rgba(245,158,11,0.16); color:#FBBF24; border:1px solid rgba(245,158,11,0.3); }",
    ".delta-info { background:rgba(6,182,212,0.16); color:#22D3EE; border:1px solid rgba(6,182,212,0.35); }",
    ".delta-neutral { background:rgba(148,163,184,0.14); color:#CBD5E1; }",
    ".pitch-wrapper { background:radial-gradient(circle at 50% 50%, #154D2E 0%, #0E351F 62%, #082012 100%); border:2px solid rgba(255,255,255,0.22); border-radius:24px; padding:18px 8px; margin-bottom:14px; }",
    ".pitch-row { display:flex; justify-content:space-around; align-items:stretch; gap:6px; margin-bottom:14px; }",
    ".pitch-row:last-child { margin-bottom:0; }",
    "a.pitch-node-link { text-decoration:none !important; color:inherit !important; flex:1 1 0; max-width:120px; min-width:62px; display:flex; }",
    ".pitch-node { width:100%; background:rgba(11,17,30,0.92); border:1.5px solid rgba(255,255,255,0.16); border-radius:14px; padding:8px 4px 6px 4px; display:flex; flex-direction:column; align-items:center; text-align:center; position:relative; }",
    ".pitch-node:hover { border-color:#00FF85; }",
    ".pitch-node.selected { border:2px solid #00FF85; box-shadow:0 0 18px rgba(0,255,133,0.5); }",
    ".pitch-node.sandbox-new { border:2px solid #06B6D4; box-shadow:0 0 20px rgba(6,182,212,0.6); }",
    ".node-avatar-wrap { position:relative; width:56px; height:56px; margin-bottom:4px; }",
    ".node-avatar-circle { width:56px; height:56px; border-radius:50%; background-color:#0B111E; background-size:cover, cover, 84% 84%; background-position:top center, top center, center center; background-repeat:no-repeat; border:2px solid rgba(255,255,255,0.3); }",
    ".badge-cap { position:absolute; bottom:-2px; right:-4px; background:#FBBF24; color:#000; font-size:9px; font-weight:900; padding:1px 5px; border-radius:5px; border:1px solid #FFF; }",
    ".badge-vc { position:absolute; bottom:-2px; right:-4px; background:#CBD5E1; color:#000; font-size:9px; font-weight:900; padding:1px 5px; border-radius:5px; border:1px solid #FFF; }",
    ".badge-flag { position:absolute; top:-3px; left:-4px; background:var(--accent-rose); color:#FFF; font-size:8px; font-weight:800; padding:1px 4px; border-radius:4px; }",
    ".badge-sub { position:absolute; top:-3px; left:-4px; background:#334155; color:#F8FAFC; font-size:8px; font-weight:800; padding:1px 4px; border-radius:4px; }",
    ".badge-new { position:absolute; top:-4px; right:-6px; background:#06B6D4; color:#070B12; font-size:8px; font-weight:900; padding:1px 4px; border-radius:4px; border:1px solid #FFF; }",
    ".node-name { font-size:11px; font-weight:800; color:#FFF; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:96%; }",
    ".node-meta { font-size:9.5px; color:#CBD5E1; font-family:'JetBrains Mono',monospace; margin:2px 0 4px 0; }",
    ".fdr-pill { font-size:9px; font-weight:800; padding:2px 4px; border-radius:4px; width:92%; margin-bottom:4px; }",
    ".fdr-1 { background:var(--fdr-1); color:#FFF; } .fdr-2 { background:var(--fdr-2); color:#052E16; } .fdr-3 { background:var(--fdr-3); color:#F8FAFC; } .fdr-4 { background:var(--fdr-4); color:#FFF; } .fdr-5 { background:var(--fdr-5); color:#FFF; }",
    ".node-dossier-btn { font-size:9px; font-weight:800; text-transform:uppercase; background:rgba(0,255,133,0.12); color:#00FF85; border:1px solid rgba(0,255,133,0.35); border-radius:5px; padding:2px 0; width:92%; }",
    ".bench-tray { background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:18px; padding:12px 10px; margin-bottom:16px; }",
    ".bench-label { font-size:11px; font-weight:800; text-transform:uppercase; color:var(--text-secondary); margin-bottom:8px; display:flex; justify-content:space-between; }",
    ".dossier-card { background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:18px; padding:16px 18px; margin-bottom:14px; }",
    ".dossier-top { display:flex; align-items:center; gap:14px; padding-bottom:12px; border-bottom:1px solid var(--border-subtle); margin-bottom:12px; }",
    ".dossier-avatar-circle { width:84px; height:84px; border-radius:50%; flex-shrink:0; background-color:#070B12; background-size:cover, cover, 82% 82%; background-position:top center, top center, center center; background-repeat:no-repeat; border:3px solid #00FF85; }",
    ".stat-grid-4 { display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; margin-bottom:8px; }",
    "@media (max-width:640px) { .stat-grid-4 { grid-template-columns:repeat(2, 1fr); } }",
    ".stat-box { background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 10px; }",
    ".stat-box-lbl { font-size:9px; color:var(--text-secondary); text-transform:uppercase; font-weight:700; }",
    ".stat-box-val { font-size:14.5px; font-weight:800; color:#FFF; font-family:'JetBrains Mono',monospace; margin-top:2px; }",
    ".runway-grid-5 { display:grid; grid-template-columns:repeat(5, 1fr); gap:6px; }",
    ".buy-grid-3 { display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:10px; }",
    "@media (max-width:860px) { .buy-grid-3 { grid-template-columns:1fr; } }",
    ".playbook-card { background:linear-gradient(160deg, rgba(15,23,42,0.98) 0%, rgba(30,41,59,0.88) 100%); border:1.5px solid rgba(255,255,255,0.12); border-radius:16px; padding:14px; height:100%; }",
    ".playbook-card.active-pb { border:2px solid #00FF85; }",
    ".verdict-banner { background:linear-gradient(135deg, rgba(16,185,129,0.14) 0%, rgba(15,23,42,0.96) 100%); border:1.5px solid rgba(0,255,133,0.4); border-radius:16px; padding:14px 18px; margin-bottom:14px; }",
    ".ml-table { width:100%; border-collapse:collapse; font-size:12px; }",
    ".ml-table th { text-align:left; padding:8px; font-size:10px; text-transform:uppercase; color:var(--text-secondary); border-bottom:1px solid var(--border-subtle); }",
    ".ml-table td { padding:8px; border-bottom:1px solid rgba(255,255,255,0.04); }",
    ".ml-row-me { background:rgba(0,255,133,0.11); font-weight:700; }",
    "div.stButton > button[kind='primary'] { background:linear-gradient(135deg, #00FF85 0%, #10B981 100%) !important; color:#070B12 !important; font-weight:900 !important; border:none !important; }",
    "div.stButton > button[kind='secondary'] { background:var(--bg-elevated) !important; color:var(--text-primary) !important; border:1px solid rgba(0,255,133,0.28) !important; font-weight:700 !important; }",
    "</style>",
]
render_html(CSS_LINES)

if not st.session_state.get("authenticated", False):
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        render_html([
            "<div class='dossier-card' style='text-align:center; margin-top:40px;'>",
            "<h2 style='margin:0; font-weight:900; color:#FFF;'>KINGS COUNTY FC</h2>",
            "<p style='color:#00FF85; font-size:11px; font-weight:800;'>FPL TACTICAL COMMAND</p></div>",
        ])
        with st.form("auth_form"):
            pw = st.text_input("Manager Access Key", type="password")
            tid_input = st.number_input(
                "FPL Entry ID",
                value=int(st.session_state.get("team_id", default_team_id)),
                step=1,
            )
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
# 4. CLUB KIT SVG GENERATOR & PHOTO BUILDER
# ---------------------------------------------------------
CLUB_PALETTES = {
    "ARS": {"p": "#EF0107", "s": "#FFFFFF"},
    "AVL": {"p": "#670E36", "s": "#95BFE5"},
    "BOU": {"p": "#DA291C", "s": "#000000"},
    "BRE": {"p": "#E30613", "s": "#FFFFFF"},
    "BHA": {"p": "#0057B8", "s": "#FFFFFF"},
    "CHE": {"p": "#034694", "s": "#FFFFFF"},
    "CRY": {"p": "#1B458F", "s": "#C4122E"},
    "EVE": {"p": "#003399", "s": "#FFFFFF"},
    "FUL": {"p": "#FFFFFF", "s": "#000000"},
    "IPS": {"p": "#0055A5", "s": "#FFFFFF"},
    "LEI": {"p": "#0053A0", "s": "#FFFFFF"},
    "LIV": {"p": "#C8102E", "s": "#FFFFFF"},
    "MCI": {"p": "#6CABDD", "s": "#FFFFFF"},
    "MUN": {"p": "#DA291C", "s": "#000000"},
    "NEW": {"p": "#241F20", "s": "#FFFFFF"},
    "NFO": {"p": "#DD0000", "s": "#FFFFFF"},
    "SOU": {"p": "#D71920", "s": "#FFFFFF"},
    "TOT": {"p": "#FFFFFF", "s": "#132257"},
    "WHU": {"p": "#7A263A", "s": "#1BB1E7"},
    "WOL": {"p": "#FDB913", "s": "#231F20"},
    "DEFAULT": {"p": "#1E293B", "s": "#00FF85"},
}


def generate_svg_kit(team_short: str, is_gk: bool = False) -> str:
    colors = CLUB_PALETTES.get(str(team_short).upper(), CLUB_PALETTES["DEFAULT"])
    p_col = "#10B981" if is_gk else colors["p"]
    s_col = "#090D16" if is_gk else colors["s"]
    short_label = str(team_short)[:3]
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'>"
        f"<path d='M25,18 L10,32 L20,40 L26,33 L26,65 L54,65 L54,33 L60,40 L70,32 L55,18 C50,23 30,23 25,18 Z' "
        f"fill='{p_col}' stroke='{s_col}' stroke-width='2'/>"
        f"<text x='40' y='49' font-family='sans-serif' font-weight='800' font-size='11' "
        f"fill='{s_col}' text-anchor='middle'>{short_label}</text></svg>"
    )
    return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"


def build_avatar_bg_style(p: dict) -> str:
    photo_str = str(safe_get(p, "photo", "")).split(".")[0]
    code_val = safe_get(p, "code", photo_str)
    raw_code = str(code_val).lstrip("p").strip()
    u25 = f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{raw_code}.png"
    uleg = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{raw_code}.png"
    t_short = safe_get(p, "team_short", "EPL")
    is_gk_flag = (safe_get(p, "element_type", 3) == 1)
    fallback_svg = generate_svg_kit(t_short, is_gk=is_gk_flag)
    return f"background-image: url('{u25}'), url('{uleg}'), url(\"{fallback_svg}\");"


def build_pitch_node_html(p: dict, is_selected: bool = False, bench_slot=None) -> str:
    pid = safe_get(p, "id", 0)
    bg_style = build_avatar_bg_style(p)
    is_c = safe_get(p, "is_captain", False)
    is_v = safe_get(p, "is_vice_captain", False)
    cap_badge = "<div class='badge-cap'>C</div>" if is_c else ("<div class='badge-vc'>V</div>" if is_v else "")
    is_new_sb = safe_get(p, "is_sandbox_new", False)
    new_badge = "<div class='badge-new'>NEW</div>" if is_new_sb else ""

    chance = p.get("chance_of_playing_next_round")
    flag_badge = ""
    if chance is not None and int(chance) < 100:
        c_int = int(chance)
        flag_lbl = "OUT" if c_int == 0 else f"{c_int}%"
        flag_badge = f"<div class='badge-flag'>{flag_lbl}</div>"
    elif bench_slot is not None:
        flag_badge = f"<div class='badge-sub'>SUB {bench_slot}</div>"

    runway = safe_get(p, "runway", [])
    nxt = runway[0] if runway else {"opp": "TBD", "venue": "H", "fdr": 3}
    nxt_fdr = safe_get(nxt, "fdr", 3)
    nxt_opp = safe_get(nxt, "opp", "TBD")
    nxt_ven = safe_get(nxt, "venue", "H")
    sel_c = "selected" if is_selected else ("sandbox-new" if is_new_sb else "")
    price = float(safe_get(p, "now_cost", 50)) / 10.0
    p_web = safe_get(p, "web_name", "Player")
    p_xp = safe_get(p, "xp_next", 0.0)
    lg_param = st.session_state.get("target_lg_id", "")
    href_url = f"?auth=passed&team_id={team_id}&lg_id={lg_param}&pid={pid}#player-dossier"

    return "".join([
        f"<a class='pitch-node-link' href='{href_url}' target='_self'>",
        f"<div class='pitch-node {sel_c}'>",
        "<div class='node-avatar-wrap'>",
        f"<div class='node-avatar-circle' style=\"{bg_style}\"></div>",
        f"{cap_badge}{flag_badge}{new_badge}</div>",
        f"<div class='node-name'>{p_web}</div>",
        f"<div class='node-meta'>£{price:.1f}m &bull; {p_xp}xP</div>",
        f"<div class='fdr-pill fdr-{nxt_fdr}'>{nxt_opp} ({nxt_ven})</div>",
        "<div class='node-dossier-btn'>Dossier</div>",
        "</div></a>",
    ])


# ---------------------------------------------------------
# 5. UNIVERSAL FPL API ENGINE
# ---------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cache-Control": "no-cache",
}


@st.cache_data(ttl=180)
def fetch_bootstrap(nonce: int = 0):
    try:
        u = f"https://fantasy.premierleague.com/api/bootstrap-static/?_={nonce}"
        r = requests.get(u, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=180)
def fetch_fixtures(nonce: int = 0):
    try:
        u = f"https://fantasy.premierleague.com/api/fixtures/?_={nonce}"
        r = requests.get(u, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_private_my_team(
    tid: int,
    raw_cookie_or_token: str = "",
    fpl_token: str = "",
    fpl_email: str = "",
    fpl_password: str = "",
    nonce: int = 0,
):
    diag = {
        "attempted": False,
        "authenticated": False,
        "status_code": None,
        "method_used": "None",
        "message": "Using Saved Snapshot / Public Roll-Forward.",
    }
    raw_input = (raw_cookie_or_token or "").strip()
    explicit_token = (fpl_token or "").strip()
    if not any([raw_input, explicit_token, (fpl_email and fpl_password)]):
        return None, diag

    diag["attempted"] = True
    session = requests.Session()
    req_headers = dict(HEADERS)
    req_headers["Origin"] = "https://fantasy.premierleague.com"
    req_headers["Referer"] = f"https://fantasy.premierleague.com/my-team/{tid}"
    methods_tried = []

    def set_bearer(tok_str: str):
        clean_jwt = tok_str.replace("Bearer ", "").replace("bearer ", "").strip().strip('"').strip("'")
        req_headers["Authorization"] = f"Bearer {clean_jwt}"
        req_headers["x-api-authorization"] = f"Bearer {clean_jwt}"

    if raw_input.startswith("curl "):
        methods_tried.append("DevTools cURL")
        for h_m in re.finditer(r"(?:-H|--header)\s+\$?['\"]([^:]+):\s*([^'\"]+)['\"]", raw_input):
            h_name, h_val = h_m.group(1).strip(), h_m.group(2).strip()
            if h_name.lower() in ("x-api-authorization", "authorization"):
                set_bearer(h_val)
            elif h_name.lower() == "cookie":
                req_headers["Cookie"] = h_val
        b_match = re.search(r"(?:-b|--cookie)\s+\$?['\"]([^'\"]+)['\"]", raw_input)
        if b_match:
            req_headers["Cookie"] = b_match.group(1).strip()

    if explicit_token:
        set_bearer(explicit_token)
        methods_tried.append("Bearer Token")

    jwt_m = re.search(r"(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})", raw_input)
    if jwt_m:
        set_bearer(jwt_m.group(1))
        methods_tried.append("Extracted JWT")

    if raw_input and not raw_input.startswith("curl ") and not raw_input.startswith("eyJ"):
        if "=" in raw_input:
            req_headers["Cookie"] = raw_input
            methods_tried.append("Cookie Header")
        else:
            set_bearer(raw_input)
            methods_tried.append("Direct Token")

    used_label = " + ".join(methods_tried) if methods_tried else "Token"
    diag["method_used"] = used_label
    try:
        url = f"https://fantasy.premierleague.com/api/my-team/{tid}/?_={nonce}"
        r = session.get(url, headers=req_headers, timeout=8)
        diag["status_code"] = r.status_code
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "picks" in data:
                diag["authenticated"] = True
                diag["message"] = f"200 OK — Synced via {used_label}."
                return data, diag
        diag["message"] = f"HTTP {r.status_code} from private endpoint. Using saved snapshot."
    except Exception as e:
        diag["message"] = f"Connection error ({e}). Using saved snapshot."
    return None, diag


@st.cache_data(ttl=60)
def fetch_manager_full(tid: int, nonce: int = 0):
    try:
        b_url = f"https://fantasy.premierleague.com/api/entry/{tid}"
        r_ent = requests.get(f"{b_url}/?_={nonce}", headers=HEADERS, timeout=8)
        r_hist = requests.get(f"{b_url}/history/?_={nonce}", headers=HEADERS, timeout=8)
        r_tr = requests.get(f"{b_url}/transfers/?_={nonce}", headers=HEADERS, timeout=8)
        entry = r_ent.json() if r_ent.status_code == 200 else {}
        history = r_hist.json() if r_hist.status_code == 200 else {}
        transfers = r_tr.json() if r_tr.status_code == 200 else []
        curr_gw = int(safe_get(entry, "current_event", 6))
        r_pk = requests.get(f"{b_url}/event/{curr_gw}/picks/?_={nonce}", headers=HEADERS, timeout=8)
        picks = r_pk.json() if r_pk.status_code == 200 else {}
        return entry, history, transfers, picks, curr_gw
    except Exception:
        return {}, {}, [], {}, 6


@st.cache_data(ttl=300)
def fetch_event_live(gw: int, nonce: int = 0):
    try:
        u = f"https://fantasy.premierleague.com/api/event/{gw}/live/?_={nonce}"
        r = requests.get(u, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=120)
def fetch_league_standings(league_id: int, nonce: int = 0):
    try:
        u = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?_={nonce}"
        r = requests.get(u, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=120)
def fetch_rival_picks(rival_tid: int, gw: int, nonce: int = 0):
    try:
        u = f"https://fantasy.premierleague.com/api/entry/{rival_tid}/event/{gw}/picks/?_={nonce}"
        r = requests.get(u, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


sync_nonce = int(st.session_state.get("sync_nonce", 0))
bootstrap = fetch_bootstrap(sync_nonce) or {"elements": [], "teams": [], "events": []}
fixtures_list = fetch_fixtures(sync_nonce)
team_id = int(st.session_state.get("team_id", default_team_id))
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
    nonce=sync_nonce,
)

elements_map = {p["id"]: dict(p) for p in safe_get(bootstrap, "elements", []) if isinstance(p, dict) and "id" in p}
teams_map = {t["id"]: dict(t) for t in safe_get(bootstrap, "teams", []) if isinstance(t, dict) and "id" in t}
events_list = safe_get(bootstrap, "events", [])
events_map = {e["id"]: dict(e) for e in events_list if isinstance(e, dict) and "id" in e}

# ---------------------------------------------------------
# 6. NEXT GAMEWEEK DEADLINE COUNTDOWN ENGINE
# ---------------------------------------------------------
next_event_obj = next((e for e in events_list if safe_get(e, "is_next")), None)
if not next_event_obj:
    next_event_obj = next((e for e in events_list if not safe_get(e, "finished")), safe_get(events_map, last_active_gw, {}))

upcoming_gw = int(safe_get(next_event_obj, "id", last_active_gw + 1))
deadline_iso = safe_get(next_event_obj, "deadline_time")

countdown_display = f"GW{upcoming_gw} UPCOMING"
if deadline_iso:
    try:
        dl_dt = datetime.fromisoformat(str(deadline_iso).replace("Z", "+00:00"))
        diff_sec = (dl_dt - datetime.now(timezone.utc)).total_seconds()
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
    ev = safe_get(fix, "event")
    if not safe_get(fix, "finished") and ev and int(ev) >= upcoming_gw:
        h_id = safe_get(fix, "team_h")
        a_id = safe_get(fix, "team_a")
        h_short = safe_get(safe_get(teams_map, h_id, {}), "short_name", "TBD")
        a_short = safe_get(safe_get(teams_map, a_id, {}), "short_name", "TBD")
        if h_id in team_runway and len(team_runway[h_id]) < 5:
            fdr_h = int(safe_get(fix, "team_h_difficulty", 3))
            team_runway[h_id].append({"gw": int(ev), "opp": a_short, "venue": "H", "fdr": fdr_h})
        if a_id in team_runway and len(team_runway[a_id]) < 5:
            fdr_a = int(safe_get(fix, "team_a_difficulty", 3))
            team_runway[a_id].append({"gw": int(ev), "opp": h_short, "venue": "A", "fdr": fdr_a})

# ---------------------------------------------------------
# 7. SELF-CALIBRATING HISTORICAL LEARNING & SELL PRICE ENGINE
# ---------------------------------------------------------
live_last_gw = fetch_event_live(last_active_gw, sync_nonce)
live_pts_map = {}
if isinstance(live_last_gw, dict) and "elements" in live_last_gw:
    for el in safe_get(live_last_gw, "elements", []):
        el_id = safe_get(el, "id")
        el_stats = safe_get(el, "stats", {})
        if el_id is not None:
            live_pts_map[el_id] = int(safe_get(el_stats, "total_points", 0))

top_actual = sorted(elements_map.values(), key=lambda x: live_pts_map.get(safe_get(x, "id"), 0), reverse=True)[:25]
avg_top_form = sum(float(safe_get(p, "form", 0.0) or 0.0) for p in top_actual) / max(len(top_actual), 1)
avg_top_xgi = sum(float(safe_get(p, "expected_goal_involvements", 0.0) or 0.0) for p in top_actual) / max(len(top_actual), 1)

w_form = 0.58 if avg_top_form >= 5.0 else 0.46
w_xgi = 4.4 if avg_top_xgi >= 2.2 else 3.8
calibration_note = f"Calibrated on GW{last_active_gw} actuals: Form Weight {int(w_form * 100)}% | xGI Multiplier {w_xgi}x"

purchase_price_map = {}
for tr in transfers_list:
    el_in = safe_get(tr, "element_in")
    cost_in = safe_get(tr, "element_in_cost")
    if el_in and cost_in:
        purchase_price_map[el_in] = int(cost_in)


def estimate_selling_price(p: dict) -> float:
    pid = safe_get(p, "id")
    now_c = int(safe_get(p, "now_cost", 50))
    if pid in purchase_price_map:
        buy_c = purchase_price_map[pid]
    else:
        buy_c = now_c - int(safe_get(p, "cost_change_start", 0))
    if now_c > buy_c:
        profit = (now_c - buy_c) // 2
        return (buy_c + profit) / 10.0
    return now_c / 10.0


def compute_player_xp(p: dict):
    form = float(safe_get(p, "form", 0.0) or 0.0)
    xgi = float(safe_get(p, "expected_goal_involvements", 0.0) or 0.0)
    mins = max(int(safe_get(p, "minutes", 0) or 0), 1)
    xgi_per_90 = (xgi / mins) * 90.0 if mins >= 90 else form * 0.12
    runway = team_runway.get(safe_get(p, "team"), [])
    next_fdr = int(runway[0]["fdr"]) if runway else 3
    avg_5_fdr = sum(int(r["fdr"]) for r in runway[:5]) / len(runway[:5]) if runway else 3.0
    raw_chance = p.get("chance_of_playing_next_round")
    chance = (float(raw_chance) if raw_chance is not None else 100.0) / 100.0

    base_score = (form * w_form) + (xgi_per_90 * w_xgi) + 1.8
    fdr_mult_map = {1: 1.35, 2: 1.2, 3: 1.0, 4: 0.82, 5: 0.68}
    fdr_mult = fdr_mult_map.get(next_fdr, 1.0)
    xp_next = round(base_score * fdr_mult * chance, 1)

    gw_series = []
    for i_w in range(5):
        fdr_w = int(runway[i_w]["fdr"]) if i_w < len(runway) else 3
        mult_w = fdr_mult_map.get(fdr_w, 1.0)
        chance_w = chance if i_w == 0 else min(1.0, chance + 0.15)
        gw_series.append(round(base_score * mult_w * chance_w, 1))

    xp_5gw = round(sum(gw_series), 1)
    return xp_next, xp_5gw, next_fdr, round(avg_5_fdr, 2), gw_series


for pid, p_obj in elements_map.items():
    xp_1, xp_5, nfdr, afdr, gw_ser = compute_player_xp(p_obj)
    p_obj["xp_next"] = xp_1
    p_obj["xp_5gw"] = xp_5
    p_obj["next_fdr"] = nfdr
    p_obj["avg_5_fdr"] = afdr
    p_obj["xp_series"] = gw_ser
    t_obj = safe_get(teams_map, safe_get(p_obj, "team"), {})
    p_obj["team_short"] = safe_get(t_obj, "short_name", "EPL")
    p_obj["team_name"] = safe_get(t_obj, "name", "Premier League")
    p_obj["runway"] = team_runway.get(safe_get(p_obj, "team"), [])
    p_obj["last_gw_pts"] = live_pts_map.get(pid, int(safe_get(p_obj, "event_points", 0)))
    p_obj["selling_price"] = estimate_selling_price(p_obj)

# ---------------------------------------------------------
# 8. BASELINE PUBLIC BANK & FREE TRANSFER MATH
# ---------------------------------------------------------
curr_hist = safe_get(history_data, "current", [])
chips_used = {safe_get(c, "event"): safe_get(c, "name") for c in safe_get(history_data, "chips", [])}
gw_avg = int(safe_get(safe_get(events_map, last_active_gw, {}), "average_entry_score", 50))

ft_available_public = 1
for h_row in curr_hist:
    ev_num = int(safe_get(h_row, "event", 1))
    if ev_num == 1:
        ft_available_public = 1
        continue
    used_tr = int(safe_get(h_row, "event_transfers", 0))
    chip_in_gw = chips_used.get(ev_num)
    if chip_in_gw in ("wildcard", "freehit"):
        ft_available_public = min(5, max(1, ft_available_public))
    else:
        ft_available_public = min(5, max(0, ft_available_public - used_tr) + 1)

upcoming_gw_transfers = [t for t in transfers_list if safe_get(t, "event") == upcoming_gw]
ft_remaining_public = max(0, ft_available_public - len(upcoming_gw_transfers))

if len(curr_hist) >= 2:
    latest_h = curr_hist[-1]
    prev_h = curr_hist[-2]
    total_pts = int(safe_get(latest_h, "total_points", 0))
    gw_pts = int(safe_get(latest_h, "points", 0))
    overall_rank = int(safe_get(latest_h, "overall_rank", 0))
    rank_delta = int(safe_get(prev_h, "overall_rank", overall_rank)) - overall_rank
    bank_public = int(safe_get(latest_h, "bank", 0)) / 10.0
    bank_delta = (int(safe_get(latest_h, "bank", 0)) - int(safe_get(prev_h, "bank", 0))) / 10.0
    val_public = int(safe_get(latest_h, "value", 1000)) / 10.0
    val_delta = (int(safe_get(latest_h, "value", 1000)) - int(safe_get(prev_h, "value", 1000))) / 10.0
elif len(curr_hist) == 1:
    latest_h = curr_hist[0]
    total_pts = int(safe_get(latest_h, "total_points", 0))
    gw_pts = int(safe_get(latest_h, "points", 0))
    overall_rank = int(safe_get(latest_h, "overall_rank", 0))
    rank_delta = 0
    bank_public = int(safe_get(latest_h, "bank", 0)) / 10.0
    bank_delta = 0.0
    val_public = int(safe_get(latest_h, "value", 1000)) / 10.0
    val_delta = 0.0
else:
    total_pts = int(safe_get(entry_data, "summary_overall_points", 407))
    gw_pts = int(safe_get(entry_data, "summary_event_points", 60))
    overall_rank = int(safe_get(entry_data, "summary_overall_rank", 1219150))
    rank_delta = 0
    bank_public = int(safe_get(entry_data, "last_deadline_bank", 1)) / 10.0
    bank_delta = 0.0
    val_public = int(safe_get(entry_data, "last_deadline_value", 1009)) / 10.0
    val_delta = 0.0

# ---------------------------------------------------------
# 9. PERSISTENT SNAPSHOT & 3-STATE ROSTER BUILDER ENGINE
# ---------------------------------------------------------
if safe_get(auth_diag, "authenticated", False) and isinstance(private_team_data, dict) and safe_get(private_team_data, "picks"):
    tr_meta = safe_get(private_team_data, "transfers", {})
    raw_priv_bank = tr_meta.get("bank") if isinstance(tr_meta, dict) else None
    priv_bank_m = (float(raw_priv_bank) / 10.0) if (raw_priv_bank is not None) else bank_public

    priv_limit = tr_meta.get("limit") if isinstance(tr_meta, dict) else None
    priv_made = int(safe_get(tr_meta, "made", 0))
    priv_ft_rem = max(0, int(priv_limit) - priv_made) if (priv_limit is not None) else ft_remaining_public

    raw_priv_val = tr_meta.get("value") if isinstance(tr_meta, dict) else None
    priv_val_m = (float(raw_priv_val) / 10.0) if (raw_priv_val is not None and float(raw_priv_val) > 0) else val_public

    fresh_snapshot = {
        "team_id": team_id,
        "target_gw": upcoming_gw,
        "public_gw_at_sync": last_active_gw,
        "updated_at": now_ny_str(),
        "source_label": f"LIVE TOKEN SYNC (GW{upcoming_gw})",
        "picks": private_team_data["picks"],
        "bank_m": round(float(priv_bank_m), 1),
        "ft_remaining": int(priv_ft_rem),
        "squad_value_m": round(float(priv_val_m), 1),
    }
    save_team_snapshot(team_id, fresh_snapshot)

saved_snapshot = load_team_snapshot(team_id)

use_saved_snapshot = False
if isinstance(saved_snapshot, dict) and safe_get(saved_snapshot, "picks"):
    snap_gw = int(safe_get(saved_snapshot, "target_gw", upcoming_gw))
    if snap_gw >= upcoming_gw or last_active_gw < snap_gw:
        use_saved_snapshot = True

gw6_raw_picks = [dict(pk) for pk in safe_get(public_picks_data, "picks", []) if isinstance(pk, dict)]

if use_saved_snapshot:
    current_picks_source = [dict(pk) for pk in saved_snapshot["picks"]]
    bank_now = float(safe_get(saved_snapshot, "bank_m", bank_public))
    ft_remaining_now = int(safe_get(saved_snapshot, "ft_remaining", ft_remaining_public))
    val_now = float(safe_get(saved_snapshot, "squad_value_m", val_public))
    team_last_updated_display = str(safe_get(saved_snapshot, "updated_at", now_ny_str()))
    st.session_state["team_updated_str"] = team_last_updated_display
    roster_sync_mode = f"LIVE TOKEN SYNCED (GW{upcoming_gw})" if safe_get(auth_diag, "authenticated") else f"PERSISTED LATEST PULL (GW{upcoming_gw})"
    roster_mode_cls = "delta-up"
else:
    rolled_picks = [dict(pk) for pk in gw6_raw_picks]
    gw_transfers = [t for t in reversed(transfers_list) if safe_get(t, "event") == upcoming_gw]
    for tr in gw_transfers:
        out_el = safe_get(tr, "element_out")
        in_el = safe_get(tr, "element_in")
        for pk in rolled_picks:
            if safe_get(pk, "element") == out_el and in_el in elements_map:
                pk["element"] = in_el
                break
    current_picks_source = rolled_picks
    bank_now = bank_public
    ft_remaining_now = ft_remaining_public
    val_now = val_public
    team_last_updated_display = f"GW{last_active_gw} Public Lock ({len(gw_transfers)} Moves)"
    st.session_state["team_updated_str"] = team_last_updated_display
    roster_sync_mode = f"PUBLIC GW{last_active_gw} + ROLL-FORWARD"
    roster_mode_cls = "delta-warn"

team_updated_safe = str(st.session_state.get("team_updated_str", team_last_updated_display))
last_synced_safe = str(st.session_state.get("last_synced_str", now_ny_str()))
cap_override = st.session_state.get("cap_override_id")
vc_override = st.session_state.get("vc_override_id")


def build_roster_from_picks(picks_list: list, apply_cap_overrides: bool = True, sandbox_new_ids: set = None):
    s_xi, b_xi = [], []
    new_set = sandbox_new_ids or set()
    for pk in picks_list:
        el_id = safe_get(pk, "element")
        base_p = elements_map.get(el_id)
        if base_p:
            p_copy = dict(base_p)
            pid = p_copy["id"]
            raw_sp = pk.get("selling_price")
            if raw_sp:
                s_val = float(raw_sp) / 10.0 if float(raw_sp) > 25 else float(raw_sp)
                p_copy["selling_price"] = s_val
                elements_map[pid]["selling_price"] = s_val

            if apply_cap_overrides and cap_override is not None:
                p_copy["is_captain"] = (pid == cap_override)
            else:
                p_copy["is_captain"] = bool(safe_get(pk, "is_captain", False))

            if apply_cap_overrides and vc_override is not None:
                p_copy["is_vice_captain"] = (pid == vc_override and not p_copy["is_captain"])
            else:
                p_copy["is_vice_captain"] = (bool(safe_get(pk, "is_vice_captain", False)) and not p_copy["is_captain"])

            p_copy["is_sandbox_new"] = (pid in new_set)
            p_copy["pick_pos"] = int(safe_get(pk, "position", 1))
            if p_copy["pick_pos"] <= 11:
                s_xi.append(p_copy)
            else:
                b_xi.append(p_copy)
    return s_xi, b_xi, (s_xi + b_xi)


gw6_starting_xi, gw6_bench_xi, gw6_full_squad = build_roster_from_picks(gw6_raw_picks, apply_cap_overrides=False)
starting_xi, bench_xi, full_squad = build_roster_from_picks(current_picks_source, apply_cap_overrides=True)

active_cap_obj = next((p for p in starting_xi if safe_get(p, "is_captain", False)), starting_xi[0] if starting_xi else {})
active_vc_obj = next((p for p in starting_xi if safe_get(p, "is_vice_captain", False)), starting_xi[1] if len(starting_xi) > 1 else {})
cap_web_name = safe_get(active_cap_obj, "web_name", "N/A")
vc_web_name = safe_get(active_vc_obj, "web_name", "N/A")

if st.session_state.get("selected_pid") is None and full_squad:
    cap_p = next((x for x in starting_xi if safe_get(x, "is_captain", False)), starting_xi[0])
    st.session_state["selected_pid"] = cap_p["id"]

team_xp_total = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in starting_xi), 1)
gw6_xp_total = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in gw6_starting_xi), 1)

starter_flags = [
    p for p in starting_xi
    if p.get("chance_of_playing_next_round") is not None and int(p.get("chance_of_playing_next_round")) < 75
]
weak_starters = [p for p in starting_xi if safe_get(p, "element_type", 3) != 1 and float(safe_get(p, "xp_next", 0.0)) < 3.4]
if starter_flags or len(weak_starters) >= 2 or ft_remaining_now >= 2:
    ft_rec_text, ft_rec_cls = "USE FT (UPGRADE XI)", "delta-up"
else:
    ft_rec_text, ft_rec_cls = "HOLD / ROLL FT", "delta-warn"

gw_vs_avg = gw_pts - gw_avg
gw_cls = "delta-up" if gw_vs_avg >= 0 else "delta-down"
gw_sign = "+" if gw_vs_avg >= 0 else ""
gw_delta_str = f"GW{last_active_gw}: {gw_pts}p ({gw_sign}{gw_vs_avg} vs Avg)"

rank_arrow = f"▲ {abs(rank_delta):,} vs LW" if rank_delta > 0 else (f"▼ {abs(rank_delta):,} vs LW" if rank_delta < 0 else "━ No Change")
rank_cls = "delta-up" if rank_delta >= 0 else "delta-down"

val_cls = "delta-up" if val_delta >= 0 else "delta-down"
val_sign = "+" if val_delta >= 0 else ""
val_delta_str = f"{val_sign}£{val_delta:.1f}m vs LW"

bank_cls = "delta-up" if use_saved_snapshot else ("delta-up" if bank_delta > 0 else ("delta-down" if bank_delta < 0 else "delta-neutral"))
bank_sign = "+" if bank_delta > 0 else ""
bank_delta_str = "Synced via Latest Pull" if use_saved_snapshot else f"{bank_sign}£{bank_delta:.1f}m vs LW"

all_classic_leagues = safe_get(safe_get(entry_data, "leagues", {}), "classic", [])
classic_leagues = [lg for lg in all_classic_leagues if safe_get(lg, "league_type") == "x" or int(safe_get(lg, "id", 0)) > 350] or all_classic_leagues

target_league_standings = []
rival_threat_players = {}
rival_ownership_set = set()
gap_to_leader = 0
my_league_rank = 1
target_league_name = "Global Overall"

if classic_leagues:
    lg_ids = [int(lg["id"]) for lg in classic_leagues if isinstance(lg, dict) and "id" in lg]
    if lg_ids:
        q_lg = st.query_params.get("lg_id")
        saved_lg_id = st.session_state.get("target_lg_id") or (int(q_lg) if (q_lg and str(q_lg).isdigit()) else lg_ids[0])
        if saved_lg_id not in lg_ids:
            saved_lg_id = lg_ids[0]
        st.session_state["target_lg_id"] = saved_lg_id
        target_league_name = next((safe_get(lg, "name", "Mini-League") for lg in classic_leagues if safe_get(lg, "id") == saved_lg_id), "Mini-League")

        st_json = fetch_league_standings(saved_lg_id, sync_nonce)
        if isinstance(st_json, dict):
            target_league_standings = safe_get(safe_get(st_json, "standings", {}), "results", [])
            if target_league_standings:
                leader_total = int(safe_get(target_league_standings[0], "total", 0))
                my_entry_row = next((r for r in target_league_standings if safe_get(r, "entry") == team_id), None)
                my_league_pts = int(safe_get(my_entry_row, "total", total_pts)) if my_entry_row else total_pts
                my_league_rank = int(safe_get(my_entry_row, "rank", 1)) if my_entry_row else 1
                gap_to_leader = leader_total - my_league_pts

                top_rivals = [r for r in target_league_standings[:4] if safe_get(r, "entry") != team_id][:3]
                for rv in top_rivals:
                    rv_picks = fetch_rival_picks(int(safe_get(rv, "entry", 0)), last_active_gw, sync_nonce)
                    if isinstance(rv_picks, dict) and "picks" in rv_picks:
                        for pk in safe_get(rv_picks, "picks", []):
                            if int(safe_get(pk, "position", 1)) <= 11:
                                el_id = safe_get(pk, "element")
                                if el_id is not None:
                                    rival_ownership_set.add(el_id)
                                    rival_threat_players[el_id] = rival_threat_players.get(el_id, 0) + 1

# ---------------------------------------------------------
# 10. STRATEGIC PLAYBOOK & SANDBOX ENGINE
# ---------------------------------------------------------
squad_ids = {p["id"] for p in full_squad if "id" in p}

sell_rankings = []
for p in full_squad:
    chance = p.get("chance_of_playing_next_round")
    chance_val = 100 if chance is None else int(chance)
    is_gk = (safe_get(p, "element_type", 3) == 1)
    gk_penalty = -25.0 if (is_gk and chance_val >= 75) else 0.0
    starter_boost = 4.5 if p in starting_xi else 0.0
    p_xp = float(safe_get(p, "xp_next", 3.0))
    p_fdr5 = float(safe_get(p, "avg_5_fdr", 3.0))
    urgency = ((100 - chance_val) * 0.6) + ((6.8 - min(p_xp, 6.8)) * 4.5) + (p_fdr5 * 2.2) + starter_boost + gk_penalty
    sell_rankings.append((urgency, p))

sell_rankings.sort(key=lambda x: x[0], reverse=True)

primary_sell = sell_rankings[0][1] if sell_rankings else (starting_xi[0] if starting_xi else {})
primary_sell_id = safe_get(primary_sell, "id", 0)
primary_sell_val = float(safe_get(primary_sell, "selling_price", float(safe_get(primary_sell, "now_cost", 50)) / 10.0))
primary_pos = safe_get(primary_sell, "element_type", 3)
max_1move_budget = round(primary_sell_val + bank_now, 1)

pb_a_cands = [
    c for c in elements_map.values()
    if safe_get(c, "id") not in squad_ids
    and safe_get(c, "element_type") == primary_pos
    and (float(safe_get(c, "now_cost", 999)) / 10.0) <= max_1move_budget
    and (c.get("chance_of_playing_next_round") is None or int(c.get("chance_of_playing_next_round")) >= 75)
]
pb_a_cands.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
pb_a_target = pb_a_cands[0] if pb_a_cands else primary_sell

if gap_to_leader > 0:
    pb_b_title = "PLAYBOOK B: MINI-LEAGUE SWORD (DIFFERENTIAL)"
    pb_b_sub = "0% Owned by Top-3 Rivals | High-Upside Catch-Up Move"
    pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") not in rival_ownership_set and safe_get(c, "id") != safe_get(pb_a_target, "id")]
    if not pb_b_cands:
        pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_target, "id")] or pb_a_cands
    pb_b_target = pb_b_cands[0] if pb_b_cands else pb_a_target
    pb_b_lesson = (
        f"Trailing 1st by {gap_to_leader} pts: {safe_get(pb_b_target, 'web_name')} is unowned by your top rivals "
        f"and carries strong xGI ({safe_get(pb_b_target, 'expected_goal_involvements')})."
    )
else:
    pb_b_title = "PLAYBOOK B: MINI-LEAGUE SHIELD (RIVAL BLOCK)"
    pb_b_sub = "Blocks Dangerous Rival Template Starter"
    pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") in rival_ownership_set and safe_get(c, "id") != safe_get(pb_a_target, "id")]
    if not pb_b_cands:
        pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_target, "id")] or pb_a_cands
    pb_b_target = pb_b_cands[0] if pb_b_cands else pb_a_target
    pb_b_lesson = f"Leading {target_league_name}: acquiring {safe_get(pb_b_target, 'web_name')} blocks your closest chasers' upside."

funding_pairs = []
for donor in full_squad:
    if safe_get(donor, "element_type", 3) == 1 or safe_get(donor, "id") == primary_sell_id:
        continue
    d_sell = float(safe_get(donor, "selling_price", float(safe_get(donor, "now_cost", 50)) / 10.0))
    d_pos = safe_get(donor, "element_type", 3)
    cheap_enablers = [
        e for e in elements_map.values()
        if safe_get(e, "id") not in squad_ids
        and safe_get(e, "element_type") == d_pos
        and (float(safe_get(e, "now_cost", 999)) / 10.0) <= (d_sell - 0.7)
        and float(safe_get(e, "xp_next", 0.0)) >= 2.6
    ]
    cheap_enablers.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
    if cheap_enablers:
        best_enabler = cheap_enablers[0]
        e_cost = float(safe_get(best_enabler, "now_cost", 45)) / 10.0
        funding_pairs.append((round(d_sell - e_cost, 1), donor, best_enabler))
funding_pairs.sort(key=lambda x: x[0], reverse=True)

pb_c_out_2 = sell_rankings[1][1] if len(sell_rankings) > 1 else primary_sell
pb_c_in_2 = pb_c_out_2
pb_c_target = pb_a_target

if funding_pairs:
    freed_cash, donor_obj, enabler_obj = funding_pairs[0]
    pb_c_out_2 = donor_obj
    pb_c_in_2 = enabler_obj
    max_2move_budget = round(max_1move_budget + freed_cash, 1)
    elite_cands = [
        c for c in elements_map.values()
        if safe_get(c, "id") not in squad_ids
        and safe_get(c, "id") != safe_get(enabler_obj, "id")
        and safe_get(c, "element_type") == primary_pos
        and (float(safe_get(c, "now_cost", 999)) / 10.0) <= max_2move_budget
        and (c.get("chance_of_playing_next_round") is None or int(c.get("chance_of_playing_next_round")) >= 75)
    ]
    elite_cands.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
    if elite_cands:
        pb_c_target = elite_cands[0]


def make_playbook_dict(key_id: str, title: str, subtitle: str, out_list: list, in_list: list, lesson_str: str) -> dict:
    moves_cnt = len(out_list)
    extra_hits = max(0, moves_cnt - ft_remaining_now)
    hit_pen = extra_hits * -4
    sell_sum = sum(float(safe_get(x, "selling_price", float(safe_get(x, "now_cost", 50)) / 10.0)) for x in out_list)
    buy_sum = sum(float(safe_get(x, "now_cost", 50)) / 10.0 for x in in_list)
    rem_b = round(bank_now + sell_sum - buy_sum, 1)
    gw1_net = round(sum(float(safe_get(x, "xp_next", 0.0)) for x in in_list) - sum(float(safe_get(x, "xp_next", 0.0)) for x in out_list) + hit_pen, 1)
    gw5_net = round(sum(float(safe_get(x, "xp_5gw", 0.0)) for x in in_list) - sum(float(safe_get(x, "xp_5gw", 0.0)) for x in out_list) + hit_pen, 1)
    lead_in = in_list[0] if in_list else {}
    run_pills = " ".join(f"[{safe_get(r, 'opp', 'TBD')}]" for r in safe_get(lead_in, "runway", [])[:3])
    return {
        "key": key_id,
        "title": title,
        "subtitle": subtitle,
        "out_objs": out_list,
        "in_objs": in_list,
        "out_ids": [safe_get(x, "id") for x in out_list],
        "in_ids": [safe_get(x, "id") for x in in_list],
        "moves_count": moves_cnt,
        "hit_cost": hit_pen,
        "new_bank": rem_b,
        "new_ft": max(0, ft_remaining_now - moves_cnt),
        "gw1_delta": gw1_net,
        "gw5_delta": gw5_net,
        "runway_str": run_pills or "[TBD]",
        "lesson": lesson_str,
    }


pb_a_lesson = (
    f"Maximizes expected scoring without a hit. {safe_get(pb_a_target, 'web_name')} combines strong form ({safe_get(pb_a_target, 'form')}) "
    f"with a 5-GW FDR of {safe_get(pb_a_target, 'avg_5_fdr')}."
)
pb_c_lesson = f"Restructures two spots to unlock premium ceiling ({safe_get(pb_c_target, 'web_name')})."

PLAYBOOKS = {
    "A": make_playbook_dict("A", "PLAYBOOK A: POINTS MAXIMIZER", "Highest 5-GW Expected Scoring (1 Move)", [primary_sell], [pb_a_target], pb_a_lesson),
    "B": make_playbook_dict("B", pb_b_title, pb_b_sub, [primary_sell], [pb_b_target], pb_b_lesson),
    "C": make_playbook_dict("C", "PLAYBOOK C: 2-MOVE PREMIUM PATH", "Structural Enabler + Premium Upgrade", [primary_sell, pb_c_out_2], [pb_c_target, pb_c_in_2], pb_c_lesson),
}

if st.session_state.get("sandbox_transfer_plan") is None:
    st.session_state["sandbox_transfer_plan"] = PLAYBOOKS["A"]
if st.session_state.get("sb_out_1") is None:
    st.session_state["sb_out_1"] = primary_sell_id
if st.session_state.get("sb_in_1") is None:
    st.session_state["sb_in_1"] = safe_get(pb_a_target, "id", 0)

active_sb_plan = st.session_state.get("sandbox_transfer_plan") or PLAYBOOKS["A"]
sb_out_ids = safe_get(active_sb_plan, "out_ids", [])
sb_in_ids = safe_get(active_sb_plan, "in_ids", [])
sb_picks_source = []
for pk in current_picks_source:
    pk_copy = dict(pk)
    el_curr = safe_get(pk_copy, "element")
    if el_curr in sb_out_ids:
        idx_swap = sb_out_ids.index(el_curr)
        if idx_swap < len(sb_in_ids) and sb_in_ids[idx_swap] in elements_map:
            new_el = sb_in_ids[idx_swap]
            pk_copy["element"] = new_el
            pk_copy["selling_price"] = int(safe_get(elements_map[new_el], "now_cost", 50))
    sb_picks_source.append(pk_copy)

sandbox_starting_xi, sandbox_bench_xi, sandbox_full_squad = build_roster_from_picks(
    sb_picks_source, apply_cap_overrides=True, sandbox_new_ids=set(sb_in_ids)
)

if not any(safe_get(p, "is_captain") for p in sandbox_starting_xi) and sandbox_starting_xi:
    best_sb_cap = sorted(sandbox_starting_xi, key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)[0]
    best_sb_cap["is_captain"] = True

sandbox_xp_total = round(sum(float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in sandbox_starting_xi), 1)
sandbox_bank_now = float(safe_get(active_sb_plan, "new_bank", bank_now))
sandbox_ft_now = int(safe_get(active_sb_plan, "new_ft", ft_remaining_now))
sandbox_hit_now = int(safe_get(active_sb_plan, "hit_cost", 0))
sandbox_label_now = str(safe_get(active_sb_plan, "title", "Transfer Sandbox"))

ml_posture_val = f"Chasing (-{gap_to_leader} pts)" if gap_to_leader > 0 else "1st Place Leader"
ml_posture_sub = f"Rank #{my_league_rank} in {target_league_name}"
ml_posture_cls = "delta-warn" if gap_to_leader > 0 else "delta-up"

# ---------------------------------------------------------
# 11. TOP HERO BANNER & SYNC CONTROLS
# ---------------------------------------------------------
render_html([
    "<div class='kcfc-hero'>",
    "<div class='kcfc-hero-top'>",
    "<div class='kcfc-hero-brand'><div class='kcfc-emblem'><span style='font-size:26px;'>🦁</span></div>",
    f"<div><div class='kcfc-hero-title'>KINGS COUNTY FC</div>",
    f"<div class='kcfc-hero-sub'>TACTICAL COMMAND &bull; TARGET LEAGUE: {target_league_name}</div></div></div>",
    "<div style='display:flex; flex-direction:column; align-items:flex-end; gap:4px;'>",
    f"<span class='kpi-delta {roster_mode_cls}'>{roster_sync_mode}</span>",
    f"<span style='font-size:10.5px; color:#CBD5E1;'>Updated: <strong style='color:#00FF85;'>{team_updated_safe}</strong></span>",
    "</div></div>",
    "<div class='countdown-bar'><div><span class='pulse-dot'></span>",
    f"<span class='countdown-lbl'>GAMEWEEK {upcoming_gw} DEADLINE</span></div>",
    f"<div class='countdown-val'>{countdown_display}</div></div></div>",
])

sync_c1, sync_c2 = st.columns([3, 1])
with sync_c1:
    if st.button(f"⟳ Check for Newer Data (Last Checked: {last_synced_safe})", use_container_width=True):
        st.cache_data.clear()
        st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
        st.session_state["last_synced_str"] = now_ny_str()
        st.rerun()
with sync_c2:
    if st.button("Reset Saved Snapshot to Public GW", use_container_width=True):
        clear_team_snapshot(team_id)
        st.session_state["cap_override_id"] = None
        st.session_state["vc_override_id"] = None
        st.cache_data.clear()
        st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
        st.session_state["last_synced_str"] = now_ny_str()
        st.rerun()

# ---------------------------------------------------------
# 12. NAVIGATION TABS
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_league, tab_ai, tab_settings = st.tabs([
    "Tactical Pitch & Dossier",
    "Transfer Analysis & Planning",
    "Mini-League & Rival Spy",
    "AI Tactical Advisor",
    "Settings",
])


# =========================================================
# TAB 1: 3-STATE MODERN SEGMENTED PILL PITCH VIEW
# =========================================================
@st.fragment
def render_pitch_and_dossier_fragment():
    cur_mode = st.session_state.get("pitch_view_mode", "current")
    if cur_mode not in ["gw6", "current", "sandbox"]:
        cur_mode = "current"

    pill_c1, pill_c2, pill_c3 = st.columns(3, gap="small")
    with pill_c1:
        if st.button(f"GW{last_active_gw} Final", use_container_width=True, type="primary" if cur_mode == "gw6" else "secondary"):
            st.session_state["pitch_view_mode"] = "gw6"
            st.rerun()
    with pill_c2:
        if st.button(f"GW{upcoming_gw} Live Squad", use_container_width=True, type="primary" if cur_mode == "current" else "secondary"):
            st.session_state["pitch_view_mode"] = "current"
            st.rerun()
    with pill_c3:
        xp_diff_sb = round(sandbox_xp_total - team_xp_total, 1)
        sb_sign = "+" if xp_diff_sb >= 0 else ""
        if st.button(f"Sandbox ({sb_sign}{xp_diff_sb} xP)", use_container_width=True, type="primary" if cur_mode == "sandbox" else "secondary"):
            st.session_state["pitch_view_mode"] = "sandbox"
            st.rerun()

    if cur_mode == "gw6":
        disp_xi, disp_bench, disp_full = gw6_starting_xi, gw6_bench_xi, gw6_full_squad
        disp_ft, disp_bank, disp_val, disp_xp = ft_remaining_public, bank_public, val_public, gw6_xp_total
        disp_xp_delta_str, disp_xp_cls = f"Historical GW{last_active_gw} Lineup", "delta-neutral"
    elif cur_mode == "sandbox":
        disp_xi, disp_bench, disp_full = sandbox_starting_xi, sandbox_bench_xi, sandbox_full_squad
        disp_ft, disp_bank, disp_val, disp_xp = sandbox_ft_now, sandbox_bank_now, val_now, sandbox_xp_total
        xp_diff_sb = round(sandbox_xp_total - team_xp_total, 1)
        sb_sign = "+" if xp_diff_sb >= 0 else ""
        disp_xp_delta_str = f"{sb_sign}{xp_diff_sb} xP vs Current ({sandbox_hit_now}p Hit)"
        disp_xp_cls = "delta-info"
    else:
        disp_xi, disp_bench, disp_full = starting_xi, bench_xi, full_squad
        disp_ft, disp_bank, disp_val, disp_xp = ft_remaining_now, bank_now, val_now, team_xp_total
        disp_xp_delta_str, disp_xp_cls = f"C: {cap_web_name} | V: {vc_web_name}", "delta-up"

    render_html([
        "<div class='kpi-grid-6' style='margin-top:6px;'>",
        f"<div class='kpi-card'><div class='kpi-label'>Season Points</div><div class='kpi-value'>{total_pts:,}</div><span class='kpi-delta {gw_cls}'>{gw_delta_str}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Overall Rank</div><div class='kpi-value'>{overall_rank:,}</div><span class='kpi-delta {rank_cls}'>{rank_arrow}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Transfers Available</div><div class='kpi-value' style='color:#FBBF24;'>{disp_ft} FT</div><span class='kpi-delta {ft_rec_cls}'>{ft_rec_text}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Squad Value</div><div class='kpi-value'>£{disp_val:.1f}m</div><span class='kpi-delta {val_cls}'>{val_delta_str}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>In The Bank</div><div class='kpi-value' style='color:#00FF85;'>£{disp_bank:.1f}m</div><span class='kpi-delta {bank_cls}'>{bank_delta_str}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Projected XI</div><div class='kpi-value' style='color:#06B6D4;'>{disp_xp} xP</div><span class='kpi-delta {disp_xp_cls}'>{disp_xp_delta_str}</span></div>",
        "</div>",
    ])

    col_left, col_right = st.columns([1.35, 1], gap="medium")
    sel_pid = st.session_state.get("selected_pid")

    with col_left:
        gks = [p for p in disp_xi if safe_get(p, "element_type") == 1]
        defs = [p for p in disp_xi if safe_get(p, "element_type") == 2]
        mids = [p for p in disp_xi if safe_get(p, "element_type") == 3]
        fwds = [p for p in disp_xi if safe_get(p, "element_type") == 4]
        bench_sorted = sorted(disp_bench, key=lambda x: int(safe_get(x, "pick_pos", 12)))

        gk_html = "".join(build_pitch_node_html(p, safe_get(p, "id") == sel_pid) for p in gks)
        def_html = "".join(build_pitch_node_html(p, safe_get(p, "id") == sel_pid) for p in defs)
        mid_html = "".join(build_pitch_node_html(p, safe_get(p, "id") == sel_pid) for p in mids)
        fwd_html = "".join(build_pitch_node_html(p, safe_get(p, "id") == sel_pid) for p in fwds)

        render_html([
            "<div class='pitch-wrapper'>",
            f"<div class='pitch-row'>{gk_html}</div>",
            f"<div class='pitch-row'>{def_html}</div>",
            f"<div class='pitch-row'>{mid_html}</div>",
            f"<div class='pitch-row'>{fwd_html}</div>",
            "</div>",
        ])

        bench_html = "".join(
            build_pitch_node_html(p, safe_get(p, "id") == sel_pid, bench_slot=i + 1)
            for i, p in enumerate(bench_sorted)
        )
        render_html([
            "<div class='bench-tray'>",
            "<div class='bench-label'><span>PRIORITY AUTO-SUB BENCH</span>",
            "<span style='color:#00FF85;'>TAP ANY PLAYER FOR DOSSIER</span></div>",
            f"<div class='pitch-row' style='margin-bottom:0;'>{bench_html}</div></div>",
        ])

    with col_right:
        render_html("<div id='player-dossier'></div>")

        squad_options = {}
        for p in disp_full:
            if "id" in p:
                pid_k = p["id"]
                role_p = "[C] " if safe_get(p, "is_captain") else ("[V] " if safe_get(p, "is_vice_captain") else "")
                new_p = "[NEW] " if safe_get(p, "is_sandbox_new") else ""
                w_n = safe_get(p, "web_name", "Player")
                t_s = safe_get(p, "team_short", "EPL")
                c_m = float(safe_get(p, "now_cost", 50)) / 10.0
                xp_n = safe_get(p, "xp_next", 0.0)
                squad_options[pid_k] = f"{new_p}{role_p}{w_n} ({t_s} - £{c_m:.1f}m | {xp_n}xP)"

        if squad_options:
            opt_keys = list(squad_options.keys())
            chosen_pid = st.selectbox(
                "Quick-Switch Player Dossier:",
                options=opt_keys,
                format_func=lambda x: squad_options.get(x, ""),
                index=opt_keys.index(sel_pid) if sel_pid in opt_keys else 0,
            )
            if chosen_pid != sel_pid:
                st.session_state["selected_pid"] = chosen_pid
                st.rerun()

        sp = next((x for x in disp_full if safe_get(x, "id") == st.session_state.get("selected_pid")), disp_full[0] if disp_full else None)
        if sp:
            sp_id = safe_get(sp, "id")
            sp_web = safe_get(sp, "web_name", "Player")
            cap_btn_c1, cap_btn_c2 = st.columns(2)
            with cap_btn_c1:
                if st.button(f"Preview {sp_web} as Captain (C)", use_container_width=True):
                    st.session_state["cap_override_id"] = sp_id
                    st.rerun()
            with cap_btn_c2:
                if st.button(f"Preview {sp_web} as Vice (V)", use_container_width=True):
                    st.session_state["vc_override_id"] = sp_id
                    st.rerun()

            dossier_bg_style = build_avatar_bg_style(sp)
            pos_name = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}.get(safe_get(sp, "element_type"), "Player")
            p_price = float(safe_get(sp, "now_cost", 50)) / 10.0
            sell_val = float(safe_get(sp, "selling_price", p_price))
            pts_per_m = round(float(safe_get(sp, "total_points", 0)) / max(p_price, 4.0), 1)
            rival_cnt = rival_threat_players.get(sp_id, 0)
            rival_tag = f"Owned by {rival_cnt}/3 Top Rivals" if rival_cnt > 0 else "True Differential (0/3 Rivals)"

            chip_parts = []
            for r in safe_get(sp, "runway", [])[:5]:
                r_gw = safe_get(r, "gw")
                r_opp = safe_get(r, "opp")
                r_ven = safe_get(r, "venue")
                r_fdr = safe_get(r, "fdr", 3)
                chip_parts.append(
                    f"<div style='background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:6px 4px; text-align:center;'>"
                    f"<div style='font-size:9px; color:var(--text-secondary);'>GW{r_gw}</div>"
                    f"<div style='font-size:10.5px; font-weight:700; color:#FFF; margin:2px 0;'>{r_opp} ({r_ven})</div>"
                    f"<span class='fdr-pill fdr-{r_fdr}' style='display:inline-block; width:auto; padding:1px 5px;'>FDR {r_fdr}</span></div>"
                )
            runway_chips = "".join(chip_parts)

            sp_news = safe_get(sp, "news", "")
            news_banner = ""
            if sp_news:
                news_banner = (
                    f"<div style='background:rgba(244,63,94,0.12); border-left:3px solid #F43F5E; padding:8px 10px; "
                    f"border-radius:8px; font-size:11.5px; color:#FDA4AF; margin-bottom:10px;'>"
                    f"<strong>Alert:</strong> {sp_news}</div>"
                )

            sp_xp_next = float(safe_get(sp, "xp_next", 0.0))
            if sp_xp_next >= 5.5:
                verdict_tag, verdict_col = "CAPTAIN / LOCK STARTER", "#00FF85"
            elif sp_xp_next >= 3.8:
                verdict_tag, verdict_col = "SOLID ROTATION HOLD", "#06B6D4"
            else:
                verdict_tag, verdict_col = "UPGRADE CANDIDATE", "#F59E0B"

            sp_first = safe_get(sp, "first_name", "")
            sp_second = safe_get(sp, "second_name", "")
            sp_club = safe_get(sp, "team_name", "Premier League")
            sp_tsb = safe_get(sp, "selected_by_percent", "0.0")
            sp_xp5 = safe_get(sp, "xp_5gw", 0.0)
            sp_last_pts = safe_get(sp, "last_gw_pts", 0)
            sp_form = safe_get(sp, "form", "0.0")
            sp_xgi = safe_get(sp, "expected_goal_involvements", "0.00")
            sp_ict = safe_get(sp, "ict_index", "0.0")
            sp_avg_fdr = safe_get(sp, "avg_5_fdr", 3.0)

            render_html([
                "<div class='dossier-card'>",
                "<div class='dossier-top'>",
                f"<div class='dossier-avatar-circle' style=\"{dossier_bg_style}\"></div>",
                "<div style='flex:1;'>",
                "<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;'>",
                f"<span style='font-size:19px; font-weight:800; color:#FFF;'>{sp_first} {sp_second}</span>",
                f"<span style='font-size:9.5px; font-weight:800; padding:3px 8px; border-radius:999px; color:{verdict_col}; border:1px solid {verdict_col};'>{verdict_tag}</span>",
                "</div>",
                f"<div style='font-size:11.5px; color:var(--text-secondary); margin-top:4px;'>{pos_name} &bull; <strong>{sp_club}</strong> &bull; TSB: {sp_tsb}%</div>",
                f"<div style='font-size:11px; color:#06B6D4; font-weight:700; margin-top:3px;'>{target_league_name}: {rival_tag}</div>",
                "</div></div>",
                news_banner,
                "<div class='stat-grid-4'>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Buy / Sell</div><div class='stat-box-val'>£{p_price:.1f}m / <span style='color:#00FF85;'>£{sell_val:.1f}m</span></div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{upcoming_gw} xP</div><div class='stat-box-val' style='color:#00FF85;'>{sp_xp_next}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>5-GW xP</div><div class='stat-box-val' style='color:#06B6D4;'>{sp_xp5}p</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>GW{last_active_gw} Pts</div><div class='stat-box-val'>{sp_last_pts} pts</div></div>",
                "</div>",
                "<div class='stat-grid-4'>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Form</div><div class='stat-box-val'>{sp_form}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>xGI</div><div class='stat-box-val'>{sp_xgi}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>ICT Index</div><div class='stat-box-val'>{sp_ict}</div></div>",
                f"<div class='stat-box'><div class='stat-box-lbl'>Pts / £m</div><div class='stat-box-val'>{pts_per_m}</div></div>",
                "</div>",
                f"<div style='font-size:10.5px; font-weight:700; text-transform:uppercase; color:var(--text-secondary); margin:10px 0 6px 0;'>5-GW Runway (Avg FDR: {sp_avg_fdr})</div>",
                f"<div class='runway-grid-5'>{runway_chips}</div></div>",
            ])


with tab_pitch:
    render_pitch_and_dossier_fragment()

    starters_sorted_last = sorted(starting_xi, key=lambda x: int(safe_get(x, "last_gw_pts", 0)), reverse=True)
    top_performers = [p for p in starters_sorted_last if int(safe_get(p, "last_gw_pts", 0)) >= 6][:3] or starters_sorted_last[:2]
    bench_pts_left = sum(int(safe_get(p, "last_gw_pts", 0)) for p in bench_xi)
    underperformers = [p for p in starting_xi if int(safe_get(p, "last_gw_pts", 0)) <= 2 and safe_get(p, "element_type") != 1]

    wins_str = ", ".join(f"<strong>{safe_get(p, 'web_name')}</strong> ({safe_get(p, 'last_gw_pts')}p)" for p in top_performers)
    u_names = ", ".join(safe_get(p, "web_name", "") for p in underperformers[:3])
    imp_str = f"Left <strong>{bench_pts_left} pts</strong> on bench." + (f" Low returns from {u_names}." if u_names else "")

    watch_items = []
    for p in full_squad:
        p_w = safe_get(p, "web_name", "Player")
        p_n = safe_get(p, "news", "")
        if p_n:
            watch_items.append(f"<strong>{p_w}</strong> ({p_n})")
        elif int(safe_get(p, "next_fdr", 3)) >= 4 and p in starting_xi:
            r_list = safe_get(p, "runway", [])
            n_opp = safe_get(r_list[0], "opp", "TBD") if r_list else "TBD"
            watch_items.append(f"<strong>{p_w}</strong> vs {n_opp} (Tough FDR)")
    watch_str = " &bull; ".join(watch_items[:4]) or "No major injury flags across your squad."

    render_html([
        "<div class='dossier-card' style='margin-top:16px;'>",
        "<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;'>",
        f"<span style='font-size:15px; font-weight:800; color:#FFF;'>GW{last_active_gw} EXECUTIVE DEBRIEF</span>",
        f"<span style='font-size:10.5px; color:#00FF85;'>{calibration_note}</span></div>",
        "<div class='buy-grid-3'>",
        f"<div style='background:rgba(16,185,129,0.07); border-left:3px solid #00FF85; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#00FF85;'>WHAT WENT WELL</div><div style='font-size:12px; margin-top:4px;'>Scored <strong>{gw_pts} pts</strong>. Top: {wins_str}.</div></div>",
        f"<div style='background:rgba(245,158,11,0.07); border-left:3px solid #F59E0B; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#FBBF24;'>AREAS TO IMPROVE</div><div style='font-size:12px; margin-top:4px;'>{imp_str}</div></div>",
        f"<div style='background:rgba(244,63,94,0.07); border-left:3px solid #F43F5E; padding:10px; border-radius:8px;'><div style='font-size:10.5px; font-weight:800; color:#FB7185;'>GW{upcoming_gw} RADAR</div><div style='font-size:12px; margin-top:4px;'>{watch_str}</div></div>",
        "</div></div>",
    ])

# =========================================================
# TAB 2: TRANSFER ANALYSIS & PLANNING
# =========================================================
with tab_transfers:
    best_1m_delta = float(safe_get(PLAYBOOKS["A"], "gw1_delta", 0.0))
    best_5m_delta = float(safe_get(PLAYBOOKS["A"], "gw5_delta", 0.0))
    primary_sell_name = safe_get(primary_sell, "web_name", "Player")
    primary_sell_xp = safe_get(primary_sell, "xp_next", 0.0)
    pb_a_in_name = safe_get(pb_a_target, "web_name", "Target")

    sb_vs_curr_diff = round(sandbox_xp_total - team_xp_total, 1)
    sb_vs_curr_sign = "+" if sb_vs_curr_diff >= 0 else ""

    render_html([
        "<div class='kpi-grid-4'>",
        f"<div class='kpi-card'><div class='kpi-label'>Free Transfers & Bank</div><div class='kpi-value' style='color:#00FF85;'>{ft_remaining_now} FT &bull; £{bank_now:.1f}m</div><span class='kpi-delta {ft_rec_cls}'>{ft_rec_text}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Max 1-Move Buy Power</div><div class='kpi-value' style='color:#FBBF24;'>£{max_1move_budget:.1f}m</div><span class='kpi-delta delta-neutral'>Via {primary_sell_name} (£{primary_sell_val:.1f}m)</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Current vs Sandbox XI</div><div class='kpi-value' style='color:#06B6D4;'>{team_xp_total} &rarr; {sandbox_xp_total} xP</div><span class='kpi-delta delta-info'>{sb_vs_curr_sign}{sb_vs_curr_diff} xP in GW{upcoming_gw}</span></div>",
        f"<div class='kpi-card'><div class='kpi-label'>Mini-League Posture</div><div class='kpi-value'>{ml_posture_val}</div><span class='kpi-delta {ml_posture_cls}'>{ml_posture_sub}</span></div>",
        "</div>",
    ])

    if ft_remaining_now >= 1 and (best_1m_delta >= 1.5 or starter_flags):
        v_head = f"EXECUTIVE VERDICT: USE 1 FREE TRANSFER (5-GW GAIN: +{best_5m_delta} xP)"
        v_cls = "delta-up"
        v_body = f"Upgrading <strong>{primary_sell_name}</strong> ({primary_sell_xp} xP) to <strong>{pb_a_in_name}</strong> adds <strong>+{best_1m_delta} xP</strong> in GW{upcoming_gw} and <strong>+{best_5m_delta} xP</strong> over 5 GWs."
    else:
        v_head = "EXECUTIVE VERDICT: ROLL FREE TRANSFER (BANK FOR 2 FT NEXT WEEK)"
        v_cls = "delta-warn"
        v_body = f"Your Starting XI projects for a solid {team_xp_total} xP. Banking gives you {min(5, ft_remaining_now + 1)} FTs next week."

    render_html([
        "<div class='verdict-banner'>",
        "<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:6px;'>",
        f"<span style='font-size:14px; font-weight:900; color:#00FF85;'>{v_head}</span>",
        f"<span class='kpi-delta {v_cls}'>NON-DESTRUCTIVE SANDBOX</span></div>",
        f"<div style='font-size:12.5px; color:#E2E8F0;'>{v_body}</div></div>",
    ])

    pb_cols = st.columns(3, gap="medium")
    for idx_pb, pb_key in enumerate(["A", "B", "C"]):
        pb = PLAYBOOKS[pb_key]
        card_cls = "playbook-card active-pb" if (safe_get(active_sb_plan, "key") == pb_key) else "playbook-card"
        pb_title = safe_get(pb, "title", "")
        pb_sub = safe_get(pb, "subtitle", "")
        out_str = " + ".join(f"{safe_get(x, 'web_name')} (£{float(safe_get(x, 'selling_price', 5.0)):.1f}m)" for x in safe_get(pb, "out_objs", []))
        in_str = " + ".join(f"{safe_get(x, 'web_name')} (£{float(safe_get(x, 'now_cost', 50)) / 10.0:.1f}m)" for x in safe_get(pb, "in_objs", []))
        gw1_d = safe_get(pb, "gw1_delta", 0.0)
        gw5_d = safe_get(pb, "gw5_delta", 0.0)
        gw1_s = "+" if gw1_d >= 0 else ""
        gw5_s = "+" if gw5_d >= 0 else ""
        pb_bank = safe_get(pb, "new_bank", 0.0)
        pb_hit = safe_get(pb, "hit_cost", 0)
        pb_run = safe_get(pb, "runway_str", "")
        pb_less = safe_get(pb, "lesson", "")

        with pb_cols[idx_pb]:
            render_html([
                f"<div class='{card_cls}'>",
                "<div style='display:flex; justify-content:space-between; align-items:center;'>",
                f"<span style='font-size:12px; font-weight:900; color:#00FF85;'>{pb_title}</span>",
                f"<span class='kpi-delta delta-up'>{gw5_s}{gw5_d} xP (5GW)</span></div>",
                f"<div style='font-size:11px; color:var(--text-secondary); margin:4px 0 8px 0;'>{pb_sub}</div>",
                "<div style='background:rgba(255,255,255,0.03); border-radius:8px; padding:8px; margin-bottom:8px;'>",
                f"<div style='font-size:11.5px; color:#FB7185;'><strong>OUT:</strong> {out_str}</div>",
                f"<div style='font-size:11.5px; color:#00FF85; margin-top:3px;'><strong>IN:</strong> {in_str}</div></div>",
                f"<div style='font-size:11px; color:#CBD5E1;'>&bull; GW{upcoming_gw} Net: <strong>{gw1_s}{gw1_d} xP</strong> ({pb_hit}p Hit)<br>&bull; New Bank: <strong>£{pb_bank:.1f}m</strong> &bull; Run: {pb_run}</div>",
                f"<div style='font-size:11px; color:#E2E8F0; margin-top:8px; border-left:2px solid #06B6D4; padding-left:8px;'>{pb_less}</div>",
                "</div>",
            ])
            if st.button(f"Load Playbook {pb_key} into Sandbox", key=f"btn_pb_{pb_key}", use_container_width=True):
                st.session_state["sandbox_transfer_plan"] = pb
                st.session_state["pitch_view_mode"] = "sandbox"
                st.rerun()

    pos_lookup = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
    out_map_1 = {}
    for p in full_squad:
        if "id" in p:
            pid_o = p["id"]
            sell_o = float(safe_get(p, "selling_price", float(safe_get(p, "now_cost", 50)) / 10.0))
            out_map_1[pid_o] = f"{safe_get(p, 'web_name')} ({safe_get(p, 'team_short')} | Sell: £{sell_o:.1f}m | {safe_get(p, 'xp_next')}xP)"

    sb_col1, sb_col2 = st.columns(2, gap="medium")
    out_keys_1 = list(out_map_1.keys())
    cur_sb_out1 = st.session_state.get("sb_out_1", out_keys_1[0] if out_keys_1 else 0)
    if cur_sb_out1 not in out_keys_1 and out_keys_1:
        cur_sb_out1 = out_keys_1[0]

    with sb_col1:
        sel_out_1 = st.selectbox("Custom Outgoing Player:", options=out_keys_1, format_func=lambda x: out_map_1.get(x, ""), index=out_keys_1.index(cur_sb_out1) if cur_sb_out1 in out_keys_1 else 0)
        out_obj_1 = elements_map.get(sel_out_1, primary_sell)
        pos_1 = safe_get(out_obj_1, "element_type", 3)

    with sb_col2:
        in_cands_1 = [c for c in elements_map.values() if safe_get(c, "id") not in squad_ids and safe_get(c, "element_type") == pos_1]
        in_cands_1.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
        in_map_1 = {c["id"]: f"{safe_get(c, 'web_name')} ({safe_get(c, 'team_short')} | £{float(safe_get(c, 'now_cost', 50)) / 10.0:.1f}m | {safe_get(c, 'xp_5gw')} 5GW xP)" for c in in_cands_1[:60] if "id" in c}
        in_keys_1 = list(in_map_1.keys())
        sel_in_1 = st.selectbox("Custom Incoming Target:", options=in_keys_1, format_func=lambda x: in_map_1.get(x, ""))
        in_obj_1 = elements_map.get(sel_in_1, pb_a_target)

    if st.button("Load Custom Swap into Pitch Sandbox", use_container_width=True):
        st.session_state["sandbox_transfer_plan"] = make_playbook_dict(
            "CUSTOM", "CUSTOM SWAP", "User Selection", [out_obj_1], [in_obj_1], "Custom sandbox swap."
        )
        st.session_state["pitch_view_mode"] = "sandbox"
        st.rerun()

# =========================================================
# TAB 3: MINI-LEAGUE STANDINGS & RIVAL WAR ROOM
# =========================================================
with tab_league:
    if target_league_standings:
        my_row = next((r for r in target_league_standings if safe_get(r, "entry") == team_id), None)
        my_pts = int(safe_get(my_row, "total", total_pts)) if my_row else total_pts
        rival_candidates = [r for r in target_league_standings[:10] if safe_get(r, "entry") != team_id]
        rival_map = {r["entry"]: f"#{safe_get(r, 'rank')} {safe_get(r, 'entry_name')} ({safe_get(r, 'total')} pts)" for r in rival_candidates if "entry" in r}
        r_keys = list(rival_map.keys())
        sel_rival_id = st.selectbox("Select Rival for Head-to-Head War Room:", options=r_keys, format_func=lambda x: rival_map.get(x, "")) if r_keys else 0

        rv_json = fetch_rival_picks(sel_rival_id, last_active_gw, sync_nonce) if sel_rival_id else {}
        rv_picks_list = safe_get(rv_json, "picks", []) if isinstance(rv_json, dict) else []
        rv_xi_ids = {safe_get(pk, "element") for pk in rv_picks_list if int(safe_get(pk, "position", 1)) <= 11 and safe_get(pk, "element") in elements_map}
        rv_cap_id = next((safe_get(pk, "element") for pk in rv_picks_list if safe_get(pk, "is_captain")), None)
        rv_cap_name = safe_get(safe_get(elements_map, rv_cap_id, {}), "web_name", "Unknown")

        my_xi_ids = {safe_get(p, "id") for p in starting_xi if "id" in p}
        shared_xi_ids = my_xi_ids.intersection(rv_xi_ids)
        my_diff_objs = sorted([elements_map[i] for i in (my_xi_ids - rv_xi_ids) if i in elements_map], key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)
        rv_diff_objs = sorted([elements_map[i] for i in (rv_xi_ids - my_xi_ids) if i in elements_map], key=lambda x: float(safe_get(x, "xp_next", 0.0)), reverse=True)

        rv_xp_total = round(sum(float(safe_get(elements_map[i], "xp_next", 0.0)) * (2 if i == rv_cap_id else 1) for i in rv_xi_ids), 1)
        h2h_xp_swing = round(team_xp_total - rv_xp_total, 1)
        h2h_sign = "+" if h2h_xp_swing >= 0 else ""

        render_html([
            "<div class='kpi-grid-4'>",
            f"<div class='kpi-card'><div class='kpi-label'>League Rank</div><div class='kpi-value'>#{my_league_rank}</div><span class='kpi-delta {ml_posture_cls}'>{ml_posture_val}</span></div>",
            f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Swing vs Rival</div><div class='kpi-value' style='color:#00FF85;'>{h2h_sign}{h2h_xp_swing} xP</div><span class='kpi-delta delta-info'>You: {team_xp_total} vs {rv_xp_total}</span></div>",
            f"<div class='kpi-card'><div class='kpi-label'>Template Overlap</div><div class='kpi-value' style='color:#06B6D4;'>{len(shared_xi_ids)}/11 Shared</div><span class='kpi-delta delta-neutral'>{len(my_diff_objs)} Differentials</span></div>",
            f"<div class='kpi-card'><div class='kpi-label'>Captain Matchup</div><div class='kpi-value' style='font-size:15px;'>{cap_web_name} vs {rv_cap_name}</div><span class='kpi-delta delta-info'>Armband</span></div>",
            "</div>",
        ])

        col_tbl, col_spy = st.columns([1, 1.15], gap="medium")
        with col_tbl:
            t_rows = []
            for r in target_league_standings[:12]:
                is_me = (safe_get(r, "entry") == team_id)
                r_tot = int(safe_get(r, "total", 0))
                gap = r_tot - my_pts
                g_str = "YOU" if is_me else (f"+{gap}" if gap > 0 else str(gap))
                t_rows.append(
                    f"<tr class='{'ml-row-me' if is_me else ''}'><td>#{safe_get(r, 'rank')}</td>"
                    f"<td><strong>{safe_get(r, 'entry_name')}</strong></td>"
                    f"<td>{safe_get(r, 'event_total')}</td><td>{r_tot}</td><td>{g_str}</td></tr>"
                )
            render_html([
                "<div class='dossier-card'><h4>Mini-League Standings</h4>",
                "<table class='ml-table'><thead><tr><th>Rk</th><th>Team</th><th>GW</th><th>Tot</th><th>Gap</th></tr></thead>",
                f"<tbody>{''.join(t_rows)}</tbody></table></div>",
            ])

        with col_spy:
            d_rows = []
            for idx_d in range(min(max(len(my_diff_objs), len(rv_diff_objs), 1), 7)):
                md = my_diff_objs[idx_d] if idx_d < len(my_diff_objs) else None
                rd = rv_diff_objs[idx_d] if idx_d < len(rv_diff_objs) else None
                m_s = f"<strong>{safe_get(md, 'web_name')}</strong> ({safe_get(md, 'xp_next')}xP)" if md else "—"
                r_s = f"<strong>{safe_get(rd, 'web_name')}</strong> ({safe_get(rd, 'xp_next')}xP)" if rd else "—"
                d_rows.append(f"<tr><td>{m_s}</td><td>{r_s}</td></tr>")

            weakest_diff = my_diff_objs[-1] if my_diff_objs else primary_sell
            w_sell = float(safe_get(weakest_diff, "selling_price", 5.0))
            w_pos = safe_get(weakest_diff, "element_type", 3)
            atk_cands = [
                p for p in elements_map.values()
                if safe_get(p, "id") not in squad_ids
                and safe_get(p, "id") not in rv_xi_ids
                and safe_get(p, "element_type") == w_pos
                and (float(safe_get(p, "now_cost", 999)) / 10.0) <= round(w_sell + bank_now, 1)
            ]
            atk_cands.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
            atk_target = atk_cands[0] if atk_cands else pb_b_target

            render_html([
                "<div class='dossier-card'><h4>Head-to-Head Rival Differentials</h4>",
                "<table class='ml-table'><thead><tr><th>Your Differentials</th><th>Rival Differentials</th></tr></thead>",
                f"<tbody>{''.join(d_rows)}</tbody></table>",
                "<div style='margin-top:10px; font-size:12px;'>",
                f"<strong>Recommended Attack Move:</strong> Swap <strong>{safe_get(weakest_diff, 'web_name')} &rarr; {safe_get(atk_target, 'web_name')}</strong> ({safe_get(atk_target, 'xp_next')} xP) to gain direct differential leverage.",
                "</div></div>",
            ])
            if st.button(f"Preview Rival Attack ({safe_get(weakest_diff, 'web_name')} → {safe_get(atk_target, 'web_name')})", use_container_width=True):
                st.session_state["sandbox_transfer_plan"] = make_playbook_dict(
                    "RIVAL_ATK", "RIVAL ATTACK", "Differential", [weakest_diff], [atk_target], "Rival attack move."
                )
                st.session_state["pitch_view_mode"] = "sandbox"
                st.rerun()
    else:
        st.info("No classic mini-leagues found.")

# =========================================================
# TAB 4: GEMINI CONVERSATIONAL AI ADVISOR
# =========================================================
with tab_ai:
    active_gemini_key = str(
        st.session_state.get("custom_gemini_key")
        or st.secrets.get("GEMINI_API_KEY", "")
        or st.secrets.get("GOOGLE_API_KEY", "")
    ).strip()

    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [
            {
                "role": "assistant",
                "content": f"Ready for **GW{upcoming_gw}**. You have **{ft_remaining_now} FT** and **£{bank_now:.1f}m** ITB. Ask me anything about your lineup, captaincy, or transfers!",
            }
        ]

    for msg in st.session_state.get("ai_messages", []):
        with st.chat_message(safe_get(msg, "role", "assistant")):
            st.markdown(safe_get(msg, "content", ""))

    user_q = st.chat_input("Ask Gemini about your squad, transfers, or mini-league rivals...")
    if user_q:
        st.session_state["ai_messages"].append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            if not active_gemini_key:
                reply = "Please add `GEMINI_API_KEY` in the Settings tab or Streamlit Secrets."
            else:
                xi_summary = ", ".join(f"{safe_get(p, 'web_name')} ({safe_get(p, 'xp_next')}xP)" for p in starting_xi)
                sys_p = f"You are the FPL Coach for Kings County FC. GW{upcoming_gw}. Bank: £{bank_now:.1f}m, FT: {ft_remaining_now}. XI: {xi_summary}."
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={active_gemini_key}"
                payload = {"system_instruction": {"parts": [{"text": sys_p}]}, "contents": [{"role": "user", "parts": [{"text": user_q}]}]}
                try:
                    r = requests.post(url, json=payload, timeout=20)
                    cands = safe_get(r.json(), "candidates", []) if r.status_code == 200 else []
                    parts = safe_get(safe_get(cands[0], "content", {}), "parts", []) if cands else []
                    reply = "\n".join(str(safe_get(pt, "text", "")) for pt in parts) or "No response returned."
                except Exception as e:
                    reply = f"Connection error: {e}"
            st.markdown(reply)
        st.session_state["ai_messages"].append({"role": "assistant", "content": reply})
        st.rerun()

# =========================================================
# TAB 5: SETTINGS & SNAPSHOT VALIDATOR
# =========================================================
with tab_settings:
    diag_msg = safe_get(auth_diag, "message", "")
    render_html([
        "<div class='dossier-card'>",
        "<h4>LIVE CONNECTION & SNAPSHOT VALIDATOR</h4>",
        f"<p style='font-size:12px; color:var(--text-secondary);'>Source: <strong style='color:#00FF85;'>{roster_sync_mode}</strong> | Updated: {team_updated_safe} | {diag_msg}</p>",
        "</div>",
    ])
    with st.form("settings_creds_form"):
        in_cookie = st.text_input("FPL Bearer Token / cURL (`FPL_COOKIE`):", value=fpl_cookie_val, type="password")
        in_gem = st.text_input("Gemini API Key (`GEMINI_API_KEY`):", value=st.session_state.get("custom_gemini_key") or st.secrets.get("GEMINI_API_KEY", ""), type="password")
        if st.form_submit_button("Sync Live Team & Save Snapshot", use_container_width=True):
            st.session_state["custom_fpl_cookie"] = in_cookie.strip()
            st.session_state["custom_gemini_key"] = in_gem.strip()
            st.cache_data.clear()
            st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
            st.session_state["last_synced_str"] = now_ny_str()
            st.rerun()

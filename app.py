"""
KINGS COUNTY FC — FPL TACTICAL COMMAND & MINI-LEAGUE INTELLIGENCE
Production Architecture | Modern Segmented Pill Pitch Switcher | Strategic Playbooks & Rival War Room
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
    """Type-safe dictionary getter that never throws KeyError or AttributeError."""
    if isinstance(obj, dict):
        val = obj.get(key, default)
        return default if val is None else val
    return default


def run_startup_qa_suite():
    """Built-in self-test that verifies AST compilation and symbol table integrity."""
    try:
        src_path = os.path.abspath(__file__)
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as f_src:
                tree = ast.parse(f_src.read())
            defined_funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
            required_funcs = {
                "now_ny_str",
                "safe_get",
                "render_html",
                "generate_svg_kit",
                "build_avatar_bg_style",
                "build_roster_from_picks",
                "make_playbook_dict",
                "build_pitch_node_html",
                "render_pitch_and_dossier_fragment",
            }
            missing = required_funcs - defined_funcs
            if missing:
                st.error(f"Startup QA Alert: Missing function definitions: {missing}")
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


def render_html(html_str: str):
    cleaned = "\n".join(line.lstrip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. SERVER-SIDE PERSISTENT SNAPSHOT VAULT (SURVIVES TAB CLOSURES)
# ---------------------------------------------------------
@st.cache_resource
def get_server_snapshot_vault() -> dict:
    """In-memory cross-session vault that persists across browser tabs and reconnects."""
    return {}


def get_snapshot_filepath(tid: int) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, f".kcfc_snapshot_{int(tid)}.json")


def save_team_snapshot(tid: int, snapshot_dict: dict):
    """Saves the latest team pull to Session State, Server Memory, and Local Disk."""
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
    """Loads the latest saved team snapshot from Session State, Server Memory, or Disk."""
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
    """Explicitly wipes the saved snapshot only when the user requests a full reset."""
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
# 3. PARENT-DOM CROWN REMOVER + MOBILE-FIRST CSS DESIGN SYSTEM
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
    ".countdown-bar { width: 100%; background: rgba(7, 11, 18, 0.9); border: 1px solid rgba(0, 255, 133, 0.4); border-radius: 14px; padding: 10px 18px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; box-shadow: inset 0 0 18px rgba(0, 255, 133, 0.08); }",
    ".countdown-left { display: flex; align-items: center; gap: 8px; }",
    ".pulse-dot { width: 8px; height: 8px; border-radius: 50%; background: #00FF85; box-shadow: 0 0 10px #00FF85; }",
    ".countdown-lbl { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; color: #E2E8F0; }",
    ".countdown-val { font-size: 16px; font-weight: 800; color: #00FF85; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; }",
    ".kpi-grid-6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 14px; }",
    "@media (max-width: 992px) { .kpi-grid-6 { grid-template-columns: repeat(3, 1fr); } }",
    "@media (max-width: 640px) { .kpi-grid-6 { grid-template-columns: repeat(2, 1fr); } }",
    ".kpi-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 14px; }",
    "@media (max-width: 860px) { .kpi-grid-4 { grid-template-columns: repeat(2, 1fr); } }",
    ".kpi-card { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 16px; padding: 13px 15px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28); display: flex; flex-direction: column; align-items: flex-start; justify-content: space-between; }",
    ".kpi-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-secondary); margin-bottom: 4px; }",
    ".kpi-value { font-size: 20px; font-weight: 800; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; line-height: 1.15; margin-bottom: 7px; }",
    ".kpi-delta { font-size: 10px; font-weight: 700; padding: 3px 7px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; display: inline-block; width: fit-content; }",
    ".delta-up { background: rgba(16, 185, 129, 0.16); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }",
    ".delta-down { background: rgba(244, 63, 94, 0.16); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.3); }",
    ".delta-warn { background: rgba(245, 158, 11, 0.16); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }",
    ".delta-info { background: rgba(6, 182, 212, 0.16); color: #22D3EE; border: 1px solid rgba(6, 182, 212, 0.35); }",
    ".delta-neutral { background: rgba(148, 163, 184, 0.14); color: #CBD5E1; }",
    ".pitch-wrapper { background: radial-gradient(circle at 50% 50%, #154D2E 0%, #0E351F 62%, #082012 100%); border: 2px solid rgba(255, 255, 255, 0.22); border-radius: 24px; padding: 20px 8px 18px 8px; box-shadow: inset 0 0 65px rgba(0, 0, 0, 0.65), 0 14px 36px rgba(0, 0, 0, 0.5); position: relative; background-image: linear-gradient(to bottom, transparent 49.5%, rgba(255,255,255,0.16) 49.5%, rgba(255,255,255,0.16) 50.5%, transparent 50.5%), radial-gradient(circle at 50% 50%, transparent 52px, rgba(255,255,255,0.16) 53px, rgba(255,255,255,0.16) 55px, transparent 56px), linear-gradient(to right, transparent 22%, rgba(255,255,255,0.12) 22%, rgba(255,255,255,0.12) 78%, transparent 78%), radial-gradient(circle at 50% 50%, #165231 0%, #0D331D 68%, #071C10 100%); background-size: 100% 100%, 100% 100%, 100% 14%, 100% 100%; background-repeat: no-repeat; margin-bottom: 14px; }",
    ".pitch-row { display: flex; justify-content: space-around; align-items: stretch; gap: 6px; margin-bottom: 14px; flex-wrap: nowrap; }",
    ".pitch-row:last-child { margin-bottom: 0; }",
    "a.pitch-node-link { text-decoration: none !important; color: inherit !important; flex: 1 1 0; max-width: 122px; min-width: 64px; display: flex; }",
    ".pitch-node { width: 100%; background: rgba(11, 17, 30, 0.90); backdrop-filter: blur(8px); border: 1.5px solid rgba(255, 255, 255, 0.16); border-radius: 15px; padding: 8px 4px 6px 4px; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.55); transition: transform 0.15s ease, border-color 0.15s ease; cursor: pointer; }",
    ".pitch-node:hover { transform: translateY(-2px); border-color: #00FF85; }",
    ".pitch-node.selected { border: 2px solid #00FF85; box-shadow: 0 0 20px rgba(0, 255, 133, 0.55); }",
    ".pitch-node.sandbox-new { border: 2px solid #06B6D4; box-shadow: 0 0 22px rgba(6, 182, 212, 0.65); }",
    ".node-avatar-wrap { position: relative; width: 58px; height: 58px; margin-bottom: 5px; }",
    ".node-avatar-circle { width: 58px; height: 58px; border-radius: 50%; background-color: #0B111E; background-size: cover, cover, 84% 84%; background-position: top center, top center, center center; background-repeat: no-repeat; border: 2px solid rgba(255, 255, 255, 0.32); box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5); }",
    ".badge-cap { position: absolute; bottom: -2px; right: -4px; background: #FBBF24; color: #000; font-size: 9.5px; font-weight: 900; padding: 1px 5px; border-radius: 6px; border: 1.5px solid #FFF; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }",
    ".badge-vc { position: absolute; bottom: -2px; right: -4px; background: #CBD5E1; color: #000; font-size: 9.5px; font-weight: 900; padding: 1px 5px; border-radius: 6px; border: 1.5px solid #FFF; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }",
    ".badge-flag { position: absolute; top: -3px; left: -4px; background: var(--accent-rose); color: #FFF; font-size: 8.5px; font-weight: 800; padding: 1px 5px; border-radius: 5px; }",
    ".badge-sub { position: absolute; top: -3px; left: -4px; background: #334155; color: #F8FAFC; font-size: 8.5px; font-weight: 800; padding: 1px 5px; border-radius: 5px; }",
    ".badge-new { position: absolute; top: -4px; right: -6px; background: #06B6D4; color: #070B12; font-size: 8.5px; font-weight: 900; padding: 1px 5px; border-radius: 5px; border: 1px solid #FFF; box-shadow: 0 0 10px rgba(6,182,212,0.8); }",
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
    ".buy-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 10px; }",
    "@media (max-width: 860px) { .buy-grid-3 { grid-template-columns: 1fr; } }",
    ".playbook-card { background: linear-gradient(160deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.88) 100%); border: 1.5px solid rgba(255, 255, 255, 0.12); border-radius: 18px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 24px rgba(0,0,0,0.35); height: 100%; }",
    ".playbook-card.active-pb { border: 2px solid #00FF85; box-shadow: 0 0 24px rgba(0, 255, 133, 0.25); }",
    ".verdict-banner { background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(15, 23, 42, 0.96) 100%); border: 1.5px solid rgba(0, 255, 133, 0.4); border-radius: 18px; padding: 16px 20px; margin-bottom: 16px; }",
    ".ml-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }",
    ".ml-table th { text-align: left; padding: 9px 10px; font-size: 10.5px; text-transform: uppercase; color: var(--text-secondary); border-bottom: 1px solid var(--border-subtle); }",
    ".ml-table td { padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }",
    ".ml-row-me { background: rgba(0, 255, 133, 0.11); font-weight: 700; }",
    ".stTabs [data-baseweb='tab-list'] { gap: 6px; background-color: var(--bg-surface); padding: 6px; border-radius: 14px; border: 1px solid var(--border-subtle); }",
    ".stTabs [data-baseweb='tab'] { border-radius: 10px; padding: 8px 16px; font-weight: 700; font-size: 12.5px; color: var(--text-secondary); }",
    ".stTabs [aria-selected='true'] { background-color: var(--bg-elevated) !important; color: #00FF85 !important; }",
    "div.stButton > button { background: var(--bg-elevated) !important; color: var(--text-primary) !important; border: 1px solid rgba(0, 255, 133, 0.28) !important; border-radius: 10px !important; font-size: 11.5px !important; font-weight: 700 !important; padding: 6px 12px !important; min-height: 34px !important; }",
    "div.stButton > button:hover { background: #00FF85 !important; color: #070B12 !important; border-color: #00FF85 !important; }",
    "div.stButton > button[kind='primary'] { background: linear-gradient(135deg, #00FF85 0%, #10B981 100%) !important; color: #070B12 !important; font-weight: 900 !important; border: 1.5px solid #FFFFFF !important; box-shadow: 0 0 18px rgba(0, 255, 133, 0.4) !important; }",
    "</style>"
]
render_html("\n".join(CSS_LINES))

if not st.session_state.get("authenticated", False):
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
    url_25 = f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{raw_code}.png"
    url_legacy = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{raw_code}.png"
    t_short = safe_get(p, "team_short", "EPL")
    is_gk_flag = (safe_get(p, "element_type", 3) == 1)
    fallback_svg = generate_svg_kit(t_short, is_gk=is_gk_flag)
    return f"background-image: url('{url_25}'), url('{url_legacy}'), url(\"{fallback_svg}\");"


# ---------------------------------------------------------
# 5. UNIVERSAL FPL API ENGINE
# ---------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}


@st.cache_data(ttl=180)
def fetch_bootstrap(nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/bootstrap-static/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=180)
def fetch_fixtures(nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/fixtures/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=30)
def fetch_private_my_team(tid: int, raw_cookie_or_token: str = "", fpl_token: str = "", fpl_email: str = "", fpl_password: str = "", nonce: int = 0):
    diag = {
        "attempted": False,
        "authenticated": False,
        "status_code": None,
        "method_used": "None",
        "message": "No live session token active. Using Saved Snapshot / Public Roll-Forward."
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
        methods_tried.append("Parsed DevTools cURL")
        for h_match in re.finditer(r"(?:-H|--header)\s+\$?['\"]([^:]+):\s*([^'\"]+)['\"]", raw_input):
            h_name, h_val = h_match.group(1).strip(), h_match.group(2).strip()
            if h_name.lower() in ("x-api-authorization", "authorization"):
                set_bearer(h_val)
                methods_tried.append(f"cURL {h_name}")
            elif h_name.lower() == "cookie":
                req_headers["Cookie"] = h_val
        b_match = re.search(r"(?:-b|--cookie)\s+\$?['\"]([^'\"]+)['\"]", raw_input)
        if b_match:
            req_headers["Cookie"] = b_match.group(1).strip()

    if explicit_token:
        set_bearer(explicit_token)
        methods_tried.append("Explicit Bearer Token")

    jwt_anywhere = re.search(r"(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})", raw_input)
    if jwt_anywhere:
        set_bearer(jwt_anywhere.group(1))
        if "JWT" not in " ".join(methods_tried):
            methods_tried.append("Auto-Extracted JWT Bearer")

    if raw_input and not raw_input.startswith("curl ") and not raw_input.startswith("eyJ") and not raw_input.lower().startswith("bearer "):
        if "x-api-authorization:" in raw_input.lower():
            val_after = re.split(r"x-api-authorization:\s*", raw_input, flags=re.IGNORECASE)[-1].splitlines()[0]
            set_bearer(val_after)
            methods_tried.append("x-api-authorization Header")
        elif "=" in raw_input:
            req_headers["Cookie"] = raw_input
            for part in raw_input.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    session.cookies.set(k.strip(), v.strip().strip('"'), domain=".premierleague.com")
            methods_tried.append("Browser Cookie Jar")
        else:
            clean_val = raw_input.strip('"').strip("'")
            req_headers["Cookie"] = f"pl_profile={clean_val}; access_token={clean_val}"
            set_bearer(clean_val)
            methods_tried.append("Dual Token/Cookie Fallback")

    used_label = " + ".join(methods_tried) if methods_tried else "None"
    diag["method_used"] = used_label

    try:
        url = f"https://fantasy.premierleague.com/api/my-team/{tid}/?_={nonce}"
        r = session.get(url, headers=req_headers, timeout=8)
        diag["status_code"] = r.status_code
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "picks" in data:
                diag["authenticated"] = True
                diag["message"] = f"200 OK — Live pre-deadline squad synced & persisted via {used_label}."
                return data, diag
        diag["message"] = f"HTTP {r.status_code} from FPL private endpoint. Falling back to latest saved snapshot."
    except Exception as e:
        diag["message"] = f"Connection exception ({e}). Falling back to latest saved snapshot."

    return None, diag


@st.cache_data(ttl=60)
def fetch_manager_full(tid: int, nonce: int = 0):
    try:
        r_ent = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/?_={nonce}", headers=HEADERS, timeout=8)
        r_hist = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/history/?_={nonce}", headers=HEADERS, timeout=8)
        r_tr = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/transfers/?_={nonce}", headers=HEADERS, timeout=8)
        entry = r_ent.json() if r_ent.status_code == 200 else {}
        history = r_hist.json() if r_hist.status_code == 200 else {}
        transfers = r_tr.json() if r_tr.status_code == 200 else []
        curr_gw = safe_get(entry, "current_event", 6)
        r_picks = requests.get(f"https://fantasy.premierleague.com/api/entry/{tid}/event/{curr_gw}/picks/?_={nonce}", headers=HEADERS, timeout=8)
        picks = r_picks.json() if r_picks.status_code == 200 else {}
        return entry, history, transfers, picks, int(curr_gw)
    except Exception:
        return {}, {}, [], {}, 6


@st.cache_data(ttl=300)
def fetch_event_live(gw: int, nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/event/{gw}/live/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=120)
def fetch_league_standings(league_id: int, nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?_={nonce}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=120)
def fetch_rival_picks(rival_tid: int, gw: int, nonce: int = 0):
    try:
        r = requests.get(f"https://fantasy.premierleague.com/api/entry/{rival_tid}/event/{gw}/picks/?_={nonce}", headers=HEADERS, timeout=6)
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
    nonce=sync_nonce
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
    ev = safe_get(fix, "event")
    if not safe_get(fix, "finished") and ev and int(ev) >= upcoming_gw:
        h_id = safe_get(fix, "team_h")
        a_id = safe_get(fix, "team_a")
        h_short = safe_get(safe_get(teams_map, h_id, {}), "short_name", "TBD")
        a_short = safe_get(safe_get(teams_map, a_id, {}), "short_name", "TBD")
        if h_id in team_runway and len(team_runway[h_id]) < 5:
            team_runway[h_id].append({"gw": int(ev), "opp": a_short, "venue": "H", "fdr": int(safe_get(fix, "team_h_difficulty", 3))})
        if a_id in team_runway and len(team_runway[a_id]) < 5:
            team_runway[a_id].append({"gw": int(ev), "opp": h_short, "venue": "A", "fdr": int(safe_get(fix, "team_a_difficulty", 3))})

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
    if priv_limit is not None:
        priv_ft_rem = max(0, int(priv_limit) - priv_made)
    else:
        priv_ft_rem = ft_remaining_public

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

# State 1: Completed GW6 Roster (Raw Public Picks)
gw6_raw_picks = [dict(pk) for pk in safe_get(public_picks_data, "picks", []) if isinstance(pk, dict)]

# State 2: Latest / Current Team (Persisted Token Snapshot OR Public Roll-Forward)
if use_saved_snapshot:
    current_picks_source = [dict(pk) for pk in saved_snapshot["picks"]]
    bank_now = float(safe_get(saved_snapshot, "bank_m", bank_public))
    ft_remaining_now = int(safe_get(saved_snapshot, "ft_remaining", ft_remaining_public))
    val_now = float(safe_get(saved_snapshot, "squad_value_m", val_public))
    team_last_updated_display = str(safe_get(saved_snapshot, "updated_at", now_ny_str()))
    st.session_state["team_updated_str"] = team_last_updated_display
    if safe_get(auth_diag, "authenticated", False):
        roster_sync_mode = f"LIVE TOKEN SYNCED (GW{upcoming_gw})"
    else:
        roster_sync_mode = f"PERSISTED LATEST PULL (GW{upcoming_gw})"
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
    team_last_updated_display = f"GW{last_active_gw} Public Lock ({len(gw_transfers)} Roll-Forward Moves)"
    st.session_state["team_updated_str"] = team_last_updated_display
    roster_sync_mode = f"PUBLIC GW{last_active_gw} + ROLL-FORWARD"
    roster_mode_cls = "delta-warn"

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

api_official_cap_name = "Unknown"
api_official_vc_name = "Unknown"
for pk in current_picks_source:
    bp = elements_map.get(safe_get(pk, "element"))
    if bp:
        if safe_get(pk, "is_captain"):
            api_official_cap_name = safe_get(bp, "web_name", "Unknown")
        if safe_get(pk, "is_vice_captain"):
            api_official_vc_name = safe_get(bp, "web_name", "Unknown")

active_cap_obj = next((p for p in starting_xi if safe_get(p, "is_captain", False)), starting_xi[0] if starting_xi else {})
active_vc_obj = next((p for p in starting_xi if safe_get(p, "is_vice_captain", False)), starting_xi[1] if len(starting_xi) > 1 else {})
cap_web_name = safe_get(active_cap_obj, "web_name", "N/A")
vc_web_name = safe_get(active_vc_obj, "web_name", "N/A")

if st.session_state.get("selected_pid") is None and full_squad:
    cap_p = next((x for x in starting_xi if safe_get(x, "is_captain", False)), starting_xi[0])
    st.session_state["selected_pid"] = cap_p["id"]

team_xp_total = round(sum(
    float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in starting_xi
), 1)
gw6_xp_total = round(sum(
    float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in gw6_starting_xi
), 1)

starter_flags = [
    p for p in starting_xi
    if p.get("chance_of_playing_next_round") is not None and int(p.get("chance_of_playing_next_round")) < 75
]
weak_starters = [
    p for p in starting_xi
    if safe_get(p, "element_type", 3) != 1 and float(safe_get(p, "xp_next", 0.0)) < 3.4
]
if starter_flags or len(weak_starters) >= 2 or ft_remaining_now >= 2:
    ft_rec_text = "USE FT (UPGRADE XI)"
    ft_rec_cls = "delta-up"
else:
    ft_rec_text = "HOLD / ROLL FT"
    ft_rec_cls = "delta-warn"

all_classic_leagues = safe_get(safe_get(entry_data, "leagues", {}), "classic", [])
classic_leagues = [
    lg for lg in all_classic_leagues
    if safe_get(lg, "league_type") == "x" or int(safe_get(lg, "id", 0)) > 350
]
if not classic_leagues:
    classic_leagues = all_classic_leagues

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
# 10. STRATEGIC PLAYBOOK & SANDBOX ENGINE (PURE PYTHON, NON-DESTRUCTIVE)
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
    urgency = (
        ((100 - chance_val) * 0.6)
        + ((6.8 - min(p_xp, 6.8)) * 4.5)
        + (p_fdr5 * 2.2)
        + starter_boost
        + gk_penalty
    )
    sell_rankings.append((urgency, p))

sell_rankings.sort(key=lambda x: x[0], reverse=True)

primary_sell = sell_rankings[0][1] if sell_rankings else (starting_xi[0] if starting_xi else {})
primary_sell_id = safe_get(primary_sell, "id", 0)
primary_sell_val = float(safe_get(primary_sell, "selling_price", float(safe_get(primary_sell, "now_cost", 50)) / 10.0))
primary_pos = safe_get(primary_sell, "element_type", 3)
max_1move_budget = round(primary_sell_val + bank_now, 1)

# Build Playbook A: Pure Points Maximizer (1-Move Highest 5-GW xP)
pb_a_cands = [
    c for c in elements_map.values()
    if safe_get(c, "id") not in squad_ids
    and safe_get(c, "element_type") == primary_pos
    and (float(safe_get(c, "now_cost", 999)) / 10.0) <= max_1move_budget
    and (c.get("chance_of_playing_next_round") is None or int(c.get("chance_of_playing_next_round")) >= 75)
]
pb_a_cands.sort(key=lambda x: float(safe_get(x, "xp_5gw", 0.0)), reverse=True)
pb_a_target = pb_a_cands[0] if pb_a_cands else primary_sell

# Build Playbook B: Mini-League Sword (Chasing -> Differential) or Shield (Leading -> Rival Block)
if gap_to_leader > 0:
    pb_b_title = "PLAYBOOK B: MINI-LEAGUE SWORD (DIFFERENTIAL)"
    pb_b_sub = "0% Owned by Top-3 Rivals | High-Upside Catch-Up Move"
    pb_b_cands = [
        c for c in pb_a_cands
        if safe_get(c, "id") not in rival_ownership_set
        and safe_get(c, "id") != safe_get(pb_a_target, "id")
    ]
    if not pb_b_cands:
        pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_target, "id")] or pb_a_cands
    pb_b_target = pb_b_cands[0] if pb_b_cands else pb_a_target
    pb_b_lesson = (
        f"Trailing 1st place by {gap_to_leader} pts means matching template players only treads water. "
        f"{safe_get(pb_b_target, 'web_name')} is unowned by your top rivals and carries strong underlying xGI ({safe_get(pb_b_target, 'expected_goal_involvements')}) into a favorable run."
    )
else:
    pb_b_title = "PLAYBOOK B: MINI-LEAGUE SHIELD (RIVAL BLOCK)"
    pb_b_sub = "Blocks Dangerous Rival Template Starter"
    pb_b_cands = [
        c for c in pb_a_cands
        if safe_get(c, "id") in rival_ownership_set
        and safe_get(c, "id") != safe_get(pb_a_target, "id")
    ]
    if not pb_b_cands:
        pb_b_cands = [c for c in pb_a_cands if safe_get(c, "id") != safe_get(pb_a_target, "id")] or pb_a_cands
    pb_b_target = pb_b_cands[0] if pb_b_cands else pb_a_target
    pb_b_lesson = (
        f"When leading {target_league_name}, your priority is neutralizing rival captaincy/haul threats. "
        f"Acquiring {safe_get(pb_b_target, 'web_name')} blocks your closest chasers' upside while maintaining elite 5-GW xP."
    )

# Build Playbook C: 2-Move Premium Enabler (Downgrade Donor + Upgrade Primary to Elite Target)
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
        cash_freed = round(d_sell - e_cost, 1)
        funding_pairs.append((cash_freed, donor, best_enabler))
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
    f"Maximizes raw expected points without taking a hit. {safe_get(pb_a_target, 'web_name')} combines strong form ({safe_get(pb_a_target, 'form')}) "
    f"with an upcoming 5-GW fixture difficulty of {safe_get(pb_a_target, 'avg_5_fdr')} vs {safe_get(primary_sell, 'web_name')}'s {safe_get(primary_sell, 'avg_5_fdr')}."
)
pb_c_lesson = (
    f"Restructures two squad spots to unlock premium ceiling ({safe_get(pb_c_target, 'web_name')}). "
    f"A 2-move path (even for -4) pays off when the incoming premium becomes a regular captaincy option and outscores the outgoing pair within 2-3 GWs."
)

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

sandbox_xp_total = round(sum(
    float(safe_get(p, "xp_next", 0.0)) * (2 if safe_get(p, "is_captain", False) else 1) for p in sandbox_starting_xi
), 1)
sandbox_bank_now = float(safe_get(active_sb_plan, "new_bank", bank_now))
sandbox_ft_now = int(safe_get(active_sb_plan, "new_ft", ft_remaining_now))
sandbox_hit_now = int(safe_get(active_sb_plan, "hit_cost", 0))
sandbox_label_now = str(safe_get(active_sb_plan, "title", "Transfer Sandbox"))

# ---------------------------------------------------------
# 11. RENDER TOP HERO BANNER, GLOBAL TELEMETRY & PITCH NODE BUILDER
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
gw_sign = "+" if gw_vs_avg >= 0 else ""
gw_delta_str = f"GW{last_active_gw}: {gw_pts}p ({gw_sign}{gw_vs_avg} vs Avg)"

val_cls = "delta-up" if val_delta >= 0 else "delta-down"
val_sign = "+" if val_delta >= 0 else ""
val_delta_str = f"{val_sign}£{val_delta:.1f}m vs LW"

bank_cls = "delta-up" if use_saved_snapshot else ("delta-up" if bank_delta > 0 else ("delta-down" if bank_delta < 0 else "delta-neutral"))
bank_sign = "+" if bank_delta > 0 else ""
bank_delta_str = "Synced via Latest Pull" if use_saved_snapshot else f"{bank_sign}£{bank_delta:.1f}m vs LW"

ml_posture_val = f"Chasing (-{gap_to_leader} pts)" if gap_to_leader > 0 else "1st Place Leader"
ml_posture_sub = f"Rank #{my_league_rank} in {target_league_name}"
ml_posture_cls = "delta-warn" if gap_to_leader > 0 else "delta-up"

last_synced_safe = str(st.session_state.get("last_synced_str", now_ny_str()))
team_updated_safe = str(st.session_state.get("team_updated_str", team_last_updated_display))

render_html(
    f"<div class='kcfc-hero'>"
    f"<div class='kcfc-hero-top'>"
    f"<div class='kcfc-hero-brand'>{pl_vector_svg}"
    f"<div><div class='kcfc-hero-title'>KINGS COUNTY FC</div>"
    f"<div class='kcfc-hero-sub'>TACTICAL COMMAND &bull; TARGET LEAGUE: {target_league_name}</div></div></div>"
    f"<div style='display:flex; flex-direction:column; align-items:flex-end; gap:4px;'>"
    f"<span class='kpi-delta {roster_mode_cls}'>{roster_sync_mode}</span>"
    f"<span style='font-size:10.5px; color:#CBD5E1; font-family:JetBrains Mono, monospace;'>Team Last Updated: <strong style='color:#00FF85;'>{team_updated_safe}</strong></span>"
    f"</div></div>"
    f"<div class='countdown-bar'><div class='countdown-left'><div class='pulse-dot'></div>"
    f"<div class='countdown-lbl'>GAMEWEEK {upcoming_gw} DEADLINE</div></div>"
    f"<div class='countdown-val'>{countdown_display}</div></div></div>"
)

sync_c1, sync_c2 = st.columns([3, 1])
with sync_c1:
    if st.button(f"⟳ Check for Newer Data (Team Last Updated: {team_updated_safe} | Feed Checked: {last_synced_safe})", use_container_width=True):
        st.cache_data.clear()
        st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
        st.session_state["last_synced_str"] = now_ny_str()
        st.rerun()
with sync_c2:
    if st.button("Reset Saved Snapshot to Public GW6", use_container_width=True):
        clear_team_snapshot(team_id)
        st.session_state["cap_override_id"] = None
        st.session_state["vc_override_id"] = None
        st.cache_data.clear()
        st.session_state["sync_nonce"] = int(st.session_state.get("sync_nonce", 0)) + 1
        st.session_state["last_synced_str"] = now_ny_str()
        st.rerun()


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
    fdr_c = f"fdr-{nxt_fdr}"
    sel_c = "selected" if is_selected else ("sandbox-new" if is_new_sb else "")
    price = float(safe_get(p, "now_cost", 50)) / 10.0
    p_web = safe_get(p, "web_name", "Player")
    p_xp = safe_get(p, "xp_next", 0.0)

    lg_param = st.session_state.get("target_lg_id", "")
    href_url = f"?auth=passed&team_id={team_id}&lg_id={lg_param}&pid={pid}#player-dossier"

    return (
        f"<a class='pitch-node-link' href='{href_url}' target='_self'>"
        f"<div class='pitch-node {sel_c}'>"
        f"<div class='node-avatar-wrap'>"
        f"<div class='node-avatar-circle' style=\"{bg_style}\"></div>"
        f"{cap_badge}{flag_badge}{new_badge}"
        f"</div>"
        f"<div class='node-name'>{p_web}</div>"
        f"<div class='node-meta'>£{price:.1f}m &bull; {p_xp}xP</div>"
        f"<div class='fdr-pill {fdr_c}'>{nxt_opp} ({nxt_ven})</div>"
        f"<div class='node-dossier-btn'>Dossier</div>"
        f"</div></a>"
    )


# ---------------------------------------------------------
# 12. NAVIGATION TABS
# ---------------------------------------------------------
tab_pitch, tab_transfers, tab_league, tab_ai, tab_settings = st.tabs([
    "Tactical Pitch & Dossier",
    "Transfer Analysis & Planning",
    "Mini-League & Rival Spy",
    "AI Tactical Advisor",
    "Settings"
])


# =========================================================
# TAB 1: 3-STATE MODERN SEGMENTED PILL PITCH VIEW
# =========================================================
@st.fragment
def render_pitch_and_dossier_fragment():
    cur_mode = st.session_state.get("pitch_view_mode", "current")
    if cur_mode not in ["gw6", "current", "sandbox"]:
        cur_mode = "current"

    # Modern Segmented Pill Bar Dock (Option A)
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
        sb_btn_label = f"Sandbox ({sb_sign}{xp_diff_sb} xP)"
        if st.button(sb_btn_label, use_container_width=True, type="primary" if cur_mode == "sandbox" else "secondary"):
            st.session_state["pitch_view_mode"] = "sandbox"
            st.rerun()

    if cur_mode == "gw6":
        disp_xi = gw6_starting_xi
        disp_bench = gw6_bench_xi
        disp_full = gw6_full_squad
        disp_ft = ft_remaining_public
        disp_bank = bank_public
        disp_val = val_public
        disp_xp = gw6_xp_total
        disp_xp_delta_str = f"Historical GW{last_active_gw} Lineup"
        disp_xp_cls = "delta-neutral"
    elif cur_mode == "sandbox":
        disp_xi = sandbox_starting_xi
        disp_bench = sandbox_bench_xi
        disp_full = sandbox_full_squad
        disp_ft = sandbox_ft_now
        disp_bank = sandbox_bank_now
        disp_val = val_now
        disp_xp = sandbox_xp_total
        xp_diff_sb = round(sandbox_xp_total - team_xp_total, 1)
        sb_sign = "+" if xp_diff_sb >= 0 else ""
        disp_xp_delta_str = f"{sb_sign}{xp_diff_sb} xP vs Current ({sandbox_hit_now}p Hit)"
        disp_xp_cls = "delta-info"
    else:
        disp_xi = starting_xi
        disp_bench = bench_xi
        disp_full = full_squad
        disp_ft = ft_remaining_now
        disp_bank = bank_now
        disp_val = val_now
        disp_xp = team_xp_total
        disp_xp_delta_str = f"C: {cap_web_name} | V: {vc_web_name}"
        disp_xp_cls = "delta-up"

    render_html(
        f"<div class='kpi-grid-6' style='margin-top:6px;'>"
        f"<div class='kpi-card'><div class='kpi-label'>Season Points</div><div class='kpi-value'>{total_pts:,}</div><span class='kpi-delta {gw_cls}'>{gw_delta_str}</span></div>"
        f"<div class='kpi-card'><div class='kpi-label'>Overall Rank</div><div class='kpi-value'>{overall_rank:,}</div><span class='kpi-delta {rank_cls}'>{rank_arrow}</span></div>"
        f"<div class='kpi-card'><div class='kpi-label'>Transfers Available</div><div class='kpi-value' style='color:#FBBF24;'>{disp_ft} FT</div><span class='kpi-delta {ft_rec_cls}'>{ft_rec_text}</span></div>"
        f"<div class='kpi-card'><div class='kpi-label'>Squad Value</div><div class='kpi-value'>£{disp_val:.1f}m</div><span class='kpi-delta {val_cls}'>{val_delta_str}</span></div>"
        f"<div class='kpi-card'><div class='kpi-label'>In The Bank</div><div class='kpi-value' style='color:#00FF85;'>£{disp_bank:.1f}m</div><span class='kpi-delta {bank_cls}'>{bank_delta_str}</span></div>"
        f"<div class='kpi-card'><div class='kpi-label'>GW{upcoming_gw} Projected XI</div><div class='kpi-value' style='color:#06B6D4;'>{disp_xp} xP</div><span class='kpi-delta {disp_xp_cls}'>{disp_xp_delta_str}</span></div>"
        f"</div>"
    )

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

        render_html(
            f"<div class='pitch-wrapper'>"
            f"<div class='pitch-row'>{gk_html}</div>"
            f"<div class='pitch-row'>{def_html}</div>"
            f"<div class='pitch-row'>{mid_html}</div>"
            f"<div class='pitch-row'>{fwd_html}</div>"
            f"</div>"
        )

        bench_html = "".join(
            build_pitch_node_html(p, safe_get(p, "id") == sel_pid, bench_slot=i + 1)
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

        squad_options = {}
        for p in disp_full:
            if "id" in p:
                pid_k = p["id"]
                role_prefix = "[C] " if safe_get(p, "is_captain") else ("[V] " if safe_get(p, "is_vice_captain") else "")
                new_tag_str = "[NEW] " if safe_get(p, "is_sandbox_new") else ""
                w_n = safe_get(p, "web_name", "Player")
                t_s = safe_get(p, "team_short", "EPL")
                c_m = float(safe_get(p, "now_cost", 50)) / 10.0
                xp_n = safe_get(p, "xp_next", 0.0)
                squad_options[pid_k] = f"{new_tag_str}{role_prefix}{w_n} ({t_s} - £{c_m:.1f}m | {xp_n}xP)"

        if squad_options:
            opt_keys = list(squad_options.keys())
            chosen_pid = st.selectbox(
                "Quick-Switch Player Dossier (Instant Zero-Refresh):",
                options=opt_keys,
                format_func=lambda x: squad_options.get(x, ""),
                index=opt_keys.index(sel_pid) if sel_pid in opt_keys else 0
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
            rival_tag = f"Owned by {rival_cnt}/3 Top Rivals" if rival_cnt > 0 else "True Mini-League Differential (0/3 Rivals)"

            chip_parts = []
            for r in safe_get(sp, "runway", [])[:5]:
                r_gw = safe_get(r, "gw")
                r_opp = safe_get(r, "opp")
                r_ven = safe_get(r, "venue")
                r_fdr = safe_get(r, "fdr", 3)
                chip_parts.append(
                    f"<div style='background:rgba(255,255,255,0.03); border:1px solid var(--border-subtle); border-radius:10px; padding:8px 4px; text-align:center;'>"
                    f"<div style='font-size:9.5px; color:var(--text-secondary);'>GW{r_gw}</div>"
                    f"<div style='font-size:11px; font-weight:700; color:#FFF; margin:3px 0;'>{r_opp} ({r_ven})</div>"
                    f"<span class='fdr-pill fdr-{r_fdr}' style='display:inline-block; width:auto; padding:1px 6px;'>FDR {r_fdr}</span>"
                    f"</div>"
                )
            runway_chips = "".join(chip_parts)

            news_banner = ""
            sp_news = safe_get(sp, "news", "")
            if sp_news:
                news_banner = (
                    f"<div style='background:rgba(244,63,94,0.12); border-left:3px solid #F43F5E; padding:10px 12px; "
                    f"border-radius:8px; font-size:12px; color:#FDA4AF; margin-bottom:14px;'>"
                    f"<strong>Medical / Status Alert:</strong> {sp_news}</div>"
                )

            sp_xp_next = float(safe_get(sp, "xp_next", 0.0))
            if sp_xp_next >= 5.5:
                verdict_tag, verdict_col = "CAPTAIN / LOCK STARTER", "#00FF85"
            elif sp_xp_next >= 3.8:
                verdict_tag, verdict_col = "SOLID ROTATION HOLD", "#06B6D4"
            else:
                verdict_tag, verdict_col = "UPGRADE / BENCH CANDIDATE", "#F59E0B"

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

            render_html(
                f"<div class='dossier-card'>"
                f"<div class='dossier-top'>"
                f"<div class='dossier-avatar-circle' style=\"{dossier_bg_style}\"></div>"
                f"<div style='flex:1;'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;'>"
                f"<span style='font-size:20px; font-weight:800; color:#FFF;'>{sp_first} {sp_second}</span>"
                f"<span style='font-size:10px; font-weight:800; padding:4px 9px; border-radius:999px; background:rgba(0,255,133,0.12); color:{verdict_col}; border:1px solid {verdict_col};'>{verdict_tag}</span>"
                f"</div>"
                f"<div style='font-size:12px; color:var(--text-secondary); margin-top:4px;'>"
                f"{pos_name} &bull; <strong>{sp_club}</strong> &bull; Global TSB: {sp_ts

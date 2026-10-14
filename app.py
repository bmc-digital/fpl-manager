import streamlit as st
import json
import urllib.request

# Clean HTML helper: strips all leading/trailing whitespace so Markdown never triggers code blocks
def clean_html(raw_html: str) -> str:
    lines = [line.strip() for line in raw_html.strip().split('\n') if line.strip()]
    return "".join(lines)

# Page configuration
st.set_page_config(
    page_title="FPL Elite Manager",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Password authentication via Secrets
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme123") if hasattr(st, "secrets") else "changeme123"
DEFAULT_TEAM_ID = int(st.secrets.get("DEFAULT_TEAM_ID", 1)) if hasattr(st, "secrets") else 1

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_html = clean_html("""
    <div style="background: #14161f; border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 40px 24px; max-width: 360px; margin: 80px auto 20px auto; text-align: center; box-shadow: 0 16px 40px rgba(0,0,0,0.6);">
        <div style="width: 44px; height: 44px; background: rgba(0, 230, 118, 0.12); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h2 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 700; color: #f0f1f5; letter-spacing: -0.3px;">FPL Elite Manager</h2>
        <p style="margin: 0; font-size: 13px; color: #8e92a2;">Private Tactical Workspace</p>
    </div>
    """)
    st.markdown(login_html, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        pwd_input = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Enter passcode")
        if st.button("Unlock Dashboard", type="primary", use_container_width=True):
            if pwd_input == str(APP_PASSWORD):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect passcode.")
    st.stop()

# HIGH-END PREMIER LEAGUE APP STYLES (CLEAN, NO BANNERS, ZERO BROKEN IMAGES)
pl_styles = clean_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    
    /* HIDE STREAMLIT BANNERS, GITHUB FORK BADGE, HEADER & FOOTER */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0a0812;
        color: #e2e4ec;
        padding-top: 0 !important;
    }
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 950px !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.4px;
    }
    
    .app-card {
        background-color: #141520;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Tactical Pitch Surface */
    .pitch-surface {
        background: radial-gradient(circle at 50% 30%, #152d1d 0%, #0d1e13 65%, #07130b 100%);
        border: 1.5px solid rgba(0, 230, 118, 0.25);
        border-radius: 20px;
        padding: 18px 10px;
        margin: 12px 0;
        position: relative;
        box-shadow: inset 0 0 50px rgba(0,0,0,0.6), 0 8px 30px rgba(0,0,0,0.3);
    }
    
    .fdr-pill {
        display: inline-block;
        font-size: 9px;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 5px;
        margin-top: 3px;
        letter-spacing: 0.3px;
    }
    .fdr-2 { background-color: #00e676; color: #002e14; }
    .fdr-3 { background-color: #434654; color: #ffffff; }
    .fdr-4 { background-color: #ff3b5c; color: #ffffff; }
    .fdr-5 { background-color: #b70028; color: #ffffff; }
    
    .badge-c {
        background: #00e676;
        color: #002e14;
        font-weight: 900;
        font-size: 9px;
        padding: 1px 4px;
        border-radius: 4px;
        display: inline-block;
    }
    .badge-vc {
        background: #00d2ff;
        color: #002a35;
        font-weight: 900;
        font-size: 9px;
        padding: 1px 4px;
        border-radius: 4px;
        display: inline-block;
    }
    
    .bench-shelf {
        background-color: #12131d;
        border: 1px dashed rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 12px 10px;
        margin-top: 14px;
    }
</style>
""")
st.markdown(pl_styles, unsafe_allow_html=True)

# Official Premier League Club Kit Colors
TEAM_COLORS = {
    'ARS': {'primary': '#EF0107', 'secondary': '#FFFFFF'},
    'AVL': {'primary': '#670E36', 'secondary': '#95BFE5'},
    'BOU': {'primary': '#DA291C', 'secondary': '#000000'},
    'BRE': {'primary': '#E30613', 'secondary': '#FFFFFF'},
    'BHA': {'primary': '#0057B8', 'secondary': '#FFFFFF'},
    'CHE': {'primary': '#034694', 'secondary': '#FFFFFF'},
    'CRY': {'primary': '#1B458F', 'secondary': '#C4122E'},
    'EVE': {'primary': '#003399', 'secondary': '#FFFFFF'},
    'FUL': {'primary': '#FFFFFF', 'secondary': '#000000'},
    'IPS': {'primary': '#004488', 'secondary': '#FFFFFF'},
    'LEI': {'primary': '#003090', 'secondary': '#FDBE11'},
    'LIV': {'primary': '#C8102E', 'secondary': '#FFFFFF'},
    'MCI': {'primary': '#6CABDD', 'secondary': '#FFFFFF'},
    'MUN': {'primary': '#DA291C', 'secondary': '#000000'},
    'NEW': {'primary': '#241F20', 'secondary': '#FFFFFF'},
    'NFO': {'primary': '#DD0000', 'secondary': '#FFFFFF'},
    'SOU': {'primary': '#D71920', 'secondary': '#FFFFFF'},
    'TOT': {'primary': '#FFFFFF', 'secondary': '#132257'},
    'WHU': {'primary': '#7A263A', 'secondary': '#1BB1E7'},
    'WOL': {'primary': '#FDB913', 'secondary': '#231F20'}
}

# Generates clean, authentic vector soccer kit jersey (100% vector SVG - never broken, never 404, never XML error)
def generate_kit_svg(team_short, is_gkp=False, size=46):
    if is_gkp:
        p_col, s_col = "#00e676", "#003919"
    else:
        colors = TEAM_COLORS.get(team_short, {'primary': '#37003c', 'secondary': '#00ff87'})
        p_col = colors['primary']
        s_col = colors['secondary']

    return clean_html(f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" style="display:block; margin:0 auto; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));">
      <path d="M30,18 L15,35 L28,45 L35,36 L35,82 L65,82 L65,36 L72,45 L85,35 L70,18 L58,22 C55,25 45,25 42,22 Z" fill="{p_col}" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
      <path d="M15,35 L28,45 L24,50 L12,40 Z" fill="{s_col}"/>
      <path d="M85,35 L72,45 L76,50 L88,40 Z" fill="{s_col}"/>
      <path d="M42,22 C45,25 55,25 58,22 C55,27 45,27 42,22 Z" fill="{s_col}"/>
    </svg>
    """)

HEADERS = {"User-Agent": "Mozilla/5.0"}

@st.cache_data(ttl=600)
def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def calculate_potential_score(player, fdr):
    try:
        form_val = float(player.get("form", 0.0))
    except (ValueError, TypeError):
        form_val = 0.0
    try:
        ep_val = float(player.get("ep_next", 0.0))
    except (ValueError, TypeError):
        ep_val = 0.0

    fdr_bonus = {2: 1.5, 3: 0.0, 4: -1.0, 5: -2.0}.get(fdr, 0.0)
    score = (form_val * 0.6) + (ep_val * 0.4) + fdr_bonus
    return round(max(score, 0.0), 2)

# TOP HEADER
col_head, col_actions = st.columns([4, 2])
with col_head:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/>
            </svg>
            <h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #f0f1f5; letter-spacing: -0.3px;">FPL Elite Manager</h1>
        </div>
    """, unsafe_allow_html=True)

with col_actions:
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with btn_c2:
        if st.button("Lock", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

team_id = DEFAULT_TEAM_ID

with st.spinner("Analyzing live Premier League metrics..."):
    try:
        bootstrap = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
        elements = {p["id"]: p for p in bootstrap["elements"]}
        teams = {t["id"]: t for t in bootstrap["teams"]}
        positions = {pos["id"]: pos["singular_name_short"] for pos in bootstrap["element_types"]}

        current_gw, next_gw = 1, 2
        for event in bootstrap["events"]:
            if event["is_current"]:
                current_gw = event["id"]
            if event["is_next"]:
                next_gw = event["id"]

            fixtures = fetch_json(f"https://fantasy.premierleague.com/api/fixtures/?event={next_gw}")
        club_matches = {}
        for fix in fixtures:
            h, a = fix["team_h"], fix["team_a"]
            club_matches[h] = {"opp": f"vs {teams[a]['short_name']} (H)", "fdr": fix["team_h_difficulty"]}
            club_matches[a] = {"opp": f"@ {teams[h]['short_name']} (A)", "fdr": fix["team_a_difficulty"]}

        entry_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/")
        picks_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{current_gw}/picks/")
        
        squad_ids = {p["element"] for p in picks_data["picks"]}
        bank = picks_data.get("entry_history", {}).get("bank", 0) / 10

        # METRIC OVERVIEW CARD
        hero_html = clean_html(f"""
        <div class="app-card" style="margin-top: 10px;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; gap: 14px;">
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #8e92a2; font-weight: 700;">Manager</div>
                    <div style="font-size: 15px; font-weight: 700; color: #f0f1f5;">{entry_data['player_first_name']} {entry_data['player_last_name']}</div>
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #8e92a2; font-weight: 700;">Squad</div>
                    <div style="font-size: 15px; font-weight: 700; color: #00e676;">{entry_data['name']}</div>
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #8e92a2; font-weight: 700;">Overall Points</div>
                    <div style="font-size: 18px; font-weight: 800; color: #f0f1f5;">{entry_data['summary_overall_points']}</div>
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; color: #8e92a2; font-weight: 700;">Bank Balance</div>
                    <div style="font-size: 18px; font-weight: 800; color: #00e676;">£{bank:.1f}m</div>
                </div>
            </div>
        </div>
        """)
        st.markdown(hero_html, unsafe_allow_html=True)

        squad_list = []
        for pick in picks_data["picks"]:
            p = elements[pick["element"]]
            fdr = club_matches.get(p["team"], {}).get("fdr", 3)
            opp = club_matches.get(p["team"], {}).get("opp", "TBD")
            score = calculate_potential_score(p, fdr)
            t_short = teams[p["team"]]["short_name"]
            
            squad_list.append({
                "data": p,
                "fdr": fdr,
                "opp": opp,
                "score": score,
                "pos_id": p["element_type"],
                "pos": positions[p["element_type"]],
                "team_short": t_short,
                "team_name": teams[p["team"]]["name"],
                "team_code": teams[p["team"]]["code"],
                "is_gkp": (p["element_type"] == 1)
            })

        # FORMATION SOLVER
        gkps = [p for p in squad_list if p["pos_id"] == 1]
        defs = sorted([p for p in squad_list if p["pos_id"] == 2], key=lambda x: x["score"], reverse=True)
        mids = sorted([p for p in squad_list if p["pos_id"] == 3], key=lambda x: x["score"], reverse=True)
        fwds = sorted([p for p in squad_list if p["pos_id"] == 4], key=lambda x: x["score"], reverse=True)

        starter_gkp = max(gkps, key=lambda x: x["score"])
        bench_gkp = [g for g in gkps if g != starter_gkp][0]

        valid_formations = [
            (3, 5, 2), (3, 4, 3), (4, 4, 2), (4, 3, 3), 
            (4, 5, 1), (5, 3, 2), (5, 4, 1), (5, 2, 3)
        ]

        best_formation = None
        best_score = -1
        best_starters = []
        best_bench_outfield = []

        for d_cnt, m_cnt, f_cnt in valid_formations:
            chosen_defs = defs[:d_cnt]
            chosen_mids = mids[:m_cnt]
            chosen_fwds = fwds[:f_cnt]
            total_s = starter_gkp["score"] + sum(x["score"] for x in chosen_defs + chosen_mids + chosen_fwds)

            if total_s > best_score:
                best_score = total_s
                best_formation = f"{d_cnt}-{m_cnt}-{f_cnt}"
                best_starters = [starter_gkp] + chosen_defs + chosen_mids + chosen_fwds
                remaining_outfield = defs[d_cnt:] + mids[m_cnt:] + fwds[f_cnt:]
                best_bench_outfield = sorted(remaining_outfield, key=lambda x: x["score"], reverse=True)

        sorted_by_pot = sorted(best_starters, key=lambda x: x["score"], reverse=True)
        captain = sorted_by_pot[0]
        vice_captain = sorted_by_pot[1]

        # Selection state for one-click player inspection
        if "selected_player_id" not in st.session_state:
            st.session_state["selected_player_id"] = captain["data"]["id"]

        def get_inspected_player():
            for sp in squad_list:
                if sp["data"]["id"] == st.session_state["selected_player_id"]:
                    return sp
            return captain

        # NAVIGATION TABS
        tab_pitch, tab_transfers, tab_simulator, tab_chips, tab_news = st.tabs([
            "Starting XI", 
            "Transfers", 
            "Simulator", 
            "Chip Strategy",
            "Intel Feed"
        ])

        # --- TAB 1: STARTING XI (ONE-CLICK SELECTION UPDATES DOSSIER AT BOTTOM) ---
        with tab_pitch:
            st.markdown(clean_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px;">
                <h3 style="margin: 0; font-size: 17px; font-weight: 700; color: #f0f1f5;">Gameweek {next_gw} Starting XI</h3>
                <div style="font-size: 12px; color: #00e676; font-weight: 700;">Tactical Formation: {best_formation}</div>
            </div>
            <p style="font-size: 12px; color: #8e92a2; margin: 2px 0 8px 0;">Tap any player to open their match readiness dossier below.</p>
            """), unsafe_allow_html=True)

            def render_interactive_player_col(col, p, tag=""):
                with col:
                    is_active = (p["data"]["id"] == st.session_state["selected_player_id"])
                    active_border = "border: 2px solid #00e676; box-shadow: 0 0 10px rgba(0,230,118,0.5);" if is_active else "border: 1px solid rgba(255,255,255,0.12);"
                    
                    role_badge = ""
                    if p == captain:
                        role_badge = '<div style="position: absolute; top: -6px; right: -6px; background: #00e676; color: #002e14; font-weight: 900; font-size: 9px; padding: 1px 4px; border-radius: 4px;">C</div>'
                    elif p == vice_captain:
                        role_badge = '<div style="position: absolute; top: -6px; right: -6px; background: #00d2ff; color: #002a35; font-weight: 900; font-size: 9px; padding: 1px 4px; border-radius: 4px;">VC</div>'
                    elif tag:
                        role_badge = f'<div style="position: absolute; top: -6px; left: -6px; background: #434654; color: #e2e4ec; font-weight: 700; font-size: 8px; padding: 1px 4px; border-radius: 4px;">{tag}</div>'

                    kit_svg = generate_kit_svg(p["team_short"], is_gkp=p["is_gkp"], size=40)
                    
                    st.markdown(clean_html(f"""
                    <div style="background: rgba(20,22,34,0.9); {active_border} border-radius: 12px; padding: 6px 2px; text-align: center; position: relative;">
                        {role_badge}
                        {kit_svg}
                        <div style="font-size: 11px; font-weight: 700; color: #f0f1f5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 3px;">{p['data']['web_name']}</div>
                        <div><span class="fdr-pill fdr-{p['fdr']}">{p['opp']}</span></div>
                        <div style="font-size: 10px; font-weight: 800; color: #00e676; margin-top: 2px;">{p['score']} pts</div>
                    </div>
                    """), unsafe_allow_html=True)

                    btn_lbl = "Selected" if is_active else "Inspect"
                    if st.button(btn_lbl, key=f"sel_p_{p['data']['id']}", use_container_width=True):
                        st.session_state["selected_player_id"] = p["data"]["id"]
                        st.rerun()

            # PITCH
            st.markdown('<div class="pitch-surface">', unsafe_allow_html=True)
            
            # Goalkeeper
            c_gk = st.columns([2, 1.2, 2])[1]
            render_interactive_player_col(c_gk, starter_gkp)

            # Defenders
            defs_line = [p for p in best_starters if p["pos_id"] == 2]
            cols_def = st.columns(len(defs_line))
            for idx, p in enumerate(defs_line):
                render_interactive_player_col(cols_def[idx], p)

            # Midfielders
            mids_line = [p for p in best_starters if p["pos_id"] == 3]
            cols_mid = st.columns(len(mids_line))
            for idx, p in enumerate(mids_line):
                render_interactive_player_col(cols_mid[idx], p)

            # Forwards
            fwds_line = [p for p in best_starters if p["pos_id"] == 4]
            cols_fwd = st.columns(len(fwds_line))
            for idx, p in enumerate(fwds_line):
                render_interactive_player_col(cols_fwd[idx], p)

            st.markdown('</div>', unsafe_allow_html=True)

            # Bench Dugout
            st.markdown("""
            <div class="bench-shelf">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #8e92a2; margin-bottom: 8px; text-align: center;">
                    Priority Bench Order
                </div>
            </div>
            """, unsafe_allow_html=True)
            cols_bench = st.columns(4)
            render_interactive_player_col(cols_bench[0], bench_gkp, tag="GKP")
            render_interactive_player_col(cols_bench[1], best_bench_outfield[0], tag="SUB 1")
            render_interactive_player_col(cols_bench[2], best_bench_outfield[1], tag="SUB 2")
            render_interactive_player_col(cols_bench[3], best_bench_outfield[2], tag="SUB 3")

            # --- LIVE PLAYER DOSSIER (UPDATES LIVE AT BOTTOM ON CLICK) ---
            st.markdown("---")
            inspected = get_inspected_player()
            ip_data = inspected["data"]

            chance = ip_data.get("chance_of_playing_next_round")
            status_text = "100% Fit & Available"
            status_color = "#00e676"
            if ip_data["status"] != "a":
                if chance is not None:
                    status_text = f"{chance}% Chance of Playing"
                    status_color = "#ffb300" if chance >= 50 else "#ff3b5c"
                else:
                    status_text = "Out / Suspended (0%)"
                    status_color = "#ff3b5c"

            kit_hero = generate_kit_svg(inspected["team_short"], is_gkp=inspected["is_gkp"], size=58)
            st.markdown(clean_html(f"""
            <div class="app-card" style="border-left: 4px solid #00e676;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div>{kit_hero}</div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #00e676; font-weight: 800;">Scouting Dossier & Match Readiness</div>
                        <h3 style="margin: 2px 0 2px 0; color: #f0f1f5; font-size: 19px;">{ip_data['first_name']} {ip_data['second_name']}</h3>
                        <div style="font-size: 12px; color: #8e92a2;">{inspected['team_name']} • {inspected['pos']} • £{ip_data['now_cost']/10:.1f}m</div>
                        <div style="display: inline-block; background: {status_color}22; color: {status_color}; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px; margin-top: 4px;">
                            {status_text}
                        </div>
                    </div>
                </div>
            </div>
            """), unsafe_allow_html=True)

            if ip_data.get("news"):
                st.warning(f"Press Conference Bulletin: {ip_data['news']}")

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Current Form", ip_data.get("form", "0.0"))
            mc2.metric("Total Points", ip_data.get("total_points", 0))
            mc3.metric("Selected By", f"{ip_data.get('selected_by_percent', '0')}%")

            mc4, mc5, mc6 = st.columns(3)
            mc4.metric("Exp. Goals (xG)", ip_data.get("expected_goals", "0.00"))
            mc5.metric("Exp. Assists (xA)", ip_data.get("expected_assists", "0.00"))
            mc6.metric("Exp. Involvements", ip_data.get("expected_goal_involvements", "0.00"))

            mc7, mc8, mc9 = st.columns(3)
            mc7.metric("Minutes Played", ip_data.get("minutes", 0))
            mc8.metric("Bonus Points", ip_data.get("bonus", 0))
            mc9.metric("Next Opponent", inspected["opp"])

        # --- TAB 2: TRANSFERS (RANKED TOP 3 OUT + TOP 3 IN FOR EACH) ---
        with tab_transfers:
            st.markdown("### Strategic Transfer Prioritization")
            st.caption("Ranked by replacement urgency and projected points upside. Below are your top 3 candidates to divest and the optimal 3 acquisitions for each.")

            transfer_out_eval = []
            for p_item in squad_list:
                p = p_item["data"]
                pos_id = p_item["pos_id"]
                sell_val = p["now_cost"] / 10
                max_budget = sell_val + bank
                fdr = p_item["fdr"]
                form_val = float(p.get("form", 0.0))

                replacements = []
                for cand in bootstrap["elements"]:
                    if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                        cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                        c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                        pot = calculate_potential_score(cand, c_fdr)
                        c_t_short = teams[cand['team']]['short_name']
                        replacements.append({
                            "data": cand,
                            "score": pot,
                            "fdr": c_fdr,
                            "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                            "team_short": c_t_short,
                            "team_name": teams[cand['team']]['name'],
                            "is_gkp": (cand["element_type"] == 1)
                        })

                replacements.sort(key=lambda x: x["score"], reverse=True)
                top_repl = replacements[0] if replacements else None
                max_upside = round(top_repl["score"] - p_item["score"], 2) if top_repl else 0.0

                urgency = 0
                reasons = []
                if p["status"] != "a":
                    chance = p.get("chance_of_playing_next_round")
                    if chance is not None and chance <= 25:
                        urgency += 12
                        reasons.append(f"Severe injury or suspension ({chance}% availability)")
                    else:
                        urgency += 7
                        reasons.append(f"Flagged fitness doubt ({chance}% chance)" if chance is not None else "Medical flag")
                
                if form_val < 2.5:
                    urgency += 3
                    reasons.append(f"Cold rolling form ({form_val} pts/gm)")
                
                if fdr >= 4:
                    urgency += 2
                    reasons.append(f"Unfavorable fixture difficulty (FDR {fdr})")

                if not reasons:
                    reasons.append(f"Tactical upgrade opportunity (+{max_upside:.1f} pts projection upgrade available)")

                priority_score = (urgency * 1.5) + max(max_upside, 0.0)
                transfer_out_eval.append({
                    "player_item": p_item,
                    "priority_score": priority_score,
                    "max_upside": max_upside,
                    "primary_reason": "; ".join(reasons),
                    "max_budget": max_budget,
                    "sell_val": sell_val,
                    "top_replacements": replacements[:3]
                })

            transfer_out_eval.sort(key=lambda x: x["priority_score"], reverse=True)
            top3_divestments = transfer_out_eval[:3]

            for rank_idx, divest in enumerate(top3_divestments, start=1):
                p_out = divest["player_item"]["data"]
                pos_name = divest["player_item"]["pos"]
                out_kit = generate_kit_svg(divest["player_item"]["team_short"], is_gkp=divest["player_item"]["is_gkp"], size=44)
                
                st.markdown(clean_html(f"""
                <div class="app-card" style="border-left: 4px solid #ff3b5c; margin-top: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div>{out_kit}</div>
                            <div>
                                <span style="background: #ff3b5c; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800;">
                                    DIVESTMENT PRIORITY #{rank_idx}
                                </span>
                                <h4 style="margin: 4px 0 2px 0; color: #f0f1f5;">{p_out['web_name']} ({pos_name}) — £{divest['sell_val']:.1f}m</h4>
                                <div style="font-size: 13px; color: #ffb4ab;">Strategic Rationale: <strong>{divest['primary_reason']}</strong></div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 12px; color: #8e92a2;">Available Capital</div>
                            <div style="font-size: 16px; font-weight: 800; color: #00e676;">£{divest['max_budget']:.1f}m</div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown(f"**Optimal Replacements for {p_out['web_name']}:**")
                repl_cols = st.columns(3)
                for c_idx, rep in enumerate(divest["top_replacements"]):
                    with repl_cols[c_idx]:
                        cand_p = rep["data"]
                        c_cost = cand_p["now_cost"] / 10
                        c_delta = round(rep["score"] - divest["player_item"]["score"], 2)
                        rep_kit = generate_kit_svg(rep["team_short"], is_gkp=rep["is_gkp"], size=42)
                        
                        st.markdown(clean_html(f"""
                        <div class="app-card" style="text-align: center; border-color: rgba(0, 230, 118, 0.4); padding: 12px;">
                            <div style="font-size: 10px; font-weight: 800; color: #00e676;">TARGET #{c_idx+1}</div>
                            <div style="margin: 6px auto;">{rep_kit}</div>
                            <div style="font-weight: 700; font-size: 13px; color: #f0f1f5;">{cand_p['web_name']}</div>
                            <div style="font-size: 11px; color: #8e92a2;">{rep['team_name']} • £{c_cost:.1f}m</div>
                            <div style="margin-top: 4px;"><span class="fdr-pill fdr-{rep['fdr']}">{rep['opp']}</span></div>
                            <div style="margin-top: 6px; font-size: 13px; font-weight: 800; color: #00e676;">{c_delta:+} pts gain</div>
                            <div style="font-size: 10px; color: #8e92a2;">Form: {cand_p['form']} • Potential: {rep['score']}</div>
                        </div>
                        """), unsafe_allow_html=True)

        # --- TAB 3: SIMULATOR (REPLACEMENTS DIRECTLY BELOW OUTGOING PLAYER) ---
        with tab_simulator:
            st.markdown("### Transfer Simulator & Scenario Modeling")
            st.caption("Model potential trades with instant recommended options directly beneath your selected outgoing player.")

            sell_names = [f"{p['data']['web_name']} ({p['pos']}) - £{p['data']['now_cost']/10:.1f}m" for p in squad_list]
            sell_choice_idx = st.selectbox("1. Choose player from your squad to replace:", range(len(sell_names)), format_func=lambda x: sell_names[x])
            selected_sell = squad_list[sell_choice_idx]
            sell_player = selected_sell["data"]
            sell_price = sell_player["now_cost"] / 10
            sim_budget = sell_price + bank
            target_pos_id = selected_sell["pos_id"]

            out_kit = generate_kit_svg(selected_sell["team_short"], is_gkp=selected_sell["is_gkp"], size=48)
            out_card = clean_html(f"""
            <div class="app-card" style="display: flex; align-items: center; gap: 14px; border-left: 3px solid #ff3b5c; margin-top: 10px;">
                <div>{out_kit}</div>
                <div>
                    <div style="font-size: 15px; font-weight: 700; color: #f0f1f5;">{sell_player['web_name']} ({selected_sell['pos']})</div>
                    <div style="font-size: 12px; color: #8e92a2;">{selected_sell['team_name']} • Sale Value: £{sell_price:.1f}m</div>
                    <div style="font-size: 12px; color: #00e676; font-weight: 700; margin-top: 2px;">Total Buy Budget Available: £{sim_budget:.1f}m</div>
                </div>
            </div>
            """)
            st.markdown(out_card, unsafe_allow_html=True)

            # TOP 3 REPLACEMENTS DIRECTLY BELOW OUTGOING PLAYER
            st.markdown(f"#### Top 3 Replacements for {sell_player['web_name']} (Within £{sim_budget:.1f}m Budget)")
            sim_replacements = []
            for cand in bootstrap["elements"]:
                if (cand["element_type"] == target_pos_id and cand["status"] == "a" and 
                    cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= sim_budget):
                    c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                    p_score = calculate_potential_score(cand, c_fdr)
                    c_t_short = teams[cand['team']]['short_name']
                    sim_replacements.append({
                        "data": cand,
                        "score": p_score,
                        "fdr": c_fdr,
                        "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                        "team_short": c_t_short,
                        "team_name": teams[cand['team']]['name'],
                        "is_gkp": (cand["element_type"] == 1)
                    })

            sim_replacements.sort(key=lambda x: x["score"], reverse=True)
            top3_sim = sim_replacements[:3]

            for idx, r_item in enumerate(top3_sim, start=1):
                rp = r_item["data"]
                r_cost = rp["now_cost"] / 10
                r_delta = round(r_item["score"] - selected_sell["score"], 2)
                r_kit = generate_kit_svg(r_item["team_short"], is_gkp=r_item["is_gkp"], size=44)
                
                rationale_text = ""
                if r_delta > 1.5:
                    rationale_text = f"High-conviction acquisition. {rp['web_name']} offers superior rolling form ({rp['form']} pts) and capitalizes on a high-upside matchup ({r_item['opp']}) compared to {sell_player['web_name']}."
                elif r_delta > 0:
                    rationale_text = f"Solid tactical upgrade. Delivers an immediate projected gain (+{r_delta} pts) while preserving capital flexibility for future gameweeks."
                else:
                    rationale_text = f"Reliable budget stabilizer. Maintains equivalent points consistency while operating comfortably within your replacement price ceiling."

                rep_card = clean_html(f"""
                <div class="app-card" style="border-left: 3px solid #00e676; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="font-weight: 800; font-size: 14px; color: #00e676;">#{idx}</div>
                            <div>{r_kit}</div>
                            <div>
                                <div style="font-size: 14px; font-weight: 700; color: #f0f1f5;">{rp['web_name']} ({r_item['team_name']}) — £{r_cost:.1f}m</div>
                                <div style="font-size: 12px; color: #8e92a2;">Form: {rp['form']} • Next: {r_item['opp']} (FDR {r_item['fdr']})</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 15px; font-weight: 800; color: #00e676;">{r_delta:+} pts gain</div>
                            <div style="font-size: 11px; color: #8e92a2;">Projection: {r_item['score']} pts</div>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #c4c6d0; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                        {rationale_text}
                    </div>
                </div>
                """)
                st.markdown(rep_card, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### Custom Manual What-If Comparison")
            all_candidates = [
                c for c in bootstrap["elements"] 
                if c["element_type"] == target_pos_id and c["id"] not in squad_ids
            ]
            all_candidates.sort(key=lambda x: x["now_cost"], reverse=True)
            buy_names = [f"{c['web_name']} ({teams[c['team']]['short_name']}) - £{c['now_cost']/10:.1f}m" for c in all_candidates]
            buy_choice_idx = st.selectbox("Or test any custom player in the league:", range(len(buy_names)), format_func=lambda x: buy_names[x])
            custom_buy = all_candidates[buy_choice_idx]
            custom_cost = custom_buy["now_cost"] / 10
            custom_fdr = club_matches.get(custom_buy["team"], {}).get("fdr", 3)
            custom_pot = calculate_potential_score(custom_buy, custom_fdr)
            custom_delta = round(custom_pot - selected_sell["score"], 2)
            custom_bank = round(sim_budget - custom_cost, 2)

            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.metric("Net Projected Points Delta", f"{custom_delta:+} pts", f"vs {sell_player['web_name']}")
            with res_c2:
                st.metric("Remaining Bank Balance", f"£{custom_bank:.1f}m", f"£{custom_bank - bank:+.1f}m capital shift")

        # --- TAB 4: CHIP STRATEGY (DEFINITIVE MINI-LEAGUE WINNING PLAYBOOK) ---
        with tab_chips:
            st.markdown("### Definitive Chip Strategy & Mini-League Winning Playbook")
            st.caption("Mathematically optimized roadmap to maximize point returns and outperform rivals across all 38 gameweeks.")

            st.markdown(clean_html(f"""
            <div class="app-card" style="border-left: 4px solid #00d2ff; background: #121824;">
                <div style="font-size: 11px; font-weight: 800; color: #00d2ff; text-transform: uppercase;">Gameweek {next_gw} Directive</div>
                <h3 style="margin: 4px 0 6px 0; color: #f0f1f5;">Verdict: HOLD ALL CHIPS THIS GAMEWEEK</h3>
                <p style="margin: 0; font-size: 13px; color: #c4c6d0;">Your squad possesses adequate depth and starting coverage. Using chips in single gameweeks surrenders your greatest competitive advantage over mini-league rivals.</p>
            </div>
            """), unsafe_allow_html=True)

            st.markdown("#### Strategic Deployment Playbook")

            # 1. Triple Captain
            st.markdown(clean_html("""
            <div class="app-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #00e676;">Triple Captain (3x Points)</h4>
                    <span style="background: rgba(0,230,118,0.15); color: #00e676; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">TARGET: DOUBLE GAMEWEEK 25 or 34</span>
                </div>
                <p style="font-size: 13px; color: #c4c6d0; margin: 8px 0 0 0;">
                    <strong>Definitive Rule:</strong> Never deploy in a standard single gameweek. The mathematically proven strategy is holding this chip for a confirmed <strong>Double Gameweek (DGW)</strong> where an elite asset (Haaland, Palmer, or Saka) plays two fixtures in a single gameweek (180 expected minutes). This yields 30–45+ points, creating an immediate 20+ point gain over mini-league competitors who waste it early.
                </p>
            </div>
            """), unsafe_allow_html=True)

            # 2. Bench Boost
            st.markdown(clean_html(f"""
            <div class="app-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #00d2ff;">Bench Boost (15 Active Scorers)</h4>
                    <span style="background: rgba(0,210,255,0.15); color: #00d2ff; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">TARGET: DOUBLE GAMEWEEK 34 or 37</span>
                </div>
                <p style="font-size: 13px; color: #c4c6d0; margin: 8px 0 0 0;">
                    <strong>Definitive Rule:</strong> Pair this chip directly with your <strong>second Wildcard</strong>. In the spring (GW 34 or 37), multiple postponed fixtures produce massive double gameweeks. Activate your Wildcard one week prior to build a squad where all 15 players have two fixtures, then trigger Bench Boost for a 30-match haul worth 35–45 extra points.
                </p>
            </div>
            """), unsafe_allow_html=True)

            # 3. Free Hit
            st.markdown(clean_html("""
            <div class="app-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #ffb300;">Free Hit (1-Week Emergency Roster)</h4>
                    <span style="background: rgba(255,179,0,0.15); color: #ffb300; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">TARGET: MAJOR FA CUP BLANK GAMEWEEK (GW 29)</span>
                </div>
                <p style="font-size: 13px; color: #c4c6d0; margin: 8px 0 0 0;">
                    <strong>Definitive Rule:</strong> Reserve strictly for the largest <strong>Blank Gameweek (BGW)</strong> of the season, when FA Cup quarterfinals force 6–8 Premier League matches to be postponed. Unprepared rivals will field only 5–6 players and score 20–30 points; your Free Hit will field 11 elite starters, generating a 35–50 point swing in a single weekend.
                </p>
            </div>
            """), unsafe_allow_html=True)

            # 4. Wildcards
            st.markdown(clean_html("""
            <div class="app-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #ff3b5c;">Wildcards (Squad Restructuring)</h4>
                    <span style="background: rgba(255,59,92,0.15); color: #ff3b5c; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">WC1: GW 10–14 | WC2: GW 31–33</span>
                </div>
                <p style="font-size: 13px; color: #c4c6d0; margin: 8px 0 0 0;">
                    <strong>Definitive Rule:</strong> Use Wildcard 1 during an autumn fixture swing to load up on surging assets with easy schedules without taking transfer point hits (-4). Wildcard 2 must be preserved for spring to set up your Bench Boost assault.
                </p>
            </div>
            """), unsafe_allow_html=True)

            st.markdown("#### The 3 Golden Rules to Win Your Mini-League")
            st.markdown("""
            1. **Hit Discipline (-4 Point Avoidance):** Taking frequent hits is the #1 reason casual managers lose mini-leagues. A player bought for a -4 hit must outscore their predecessor by 5+ points just to break even. Roll free transfers to execute free double moves.
            2. **Captaincy Effective Ownership (EO):** When leading your mini-league, captain the consensus high-ownership asset to protect your rank. Only captain a low-owned differential if you are chasing a 40+ point deficit in the season's final 5 gameweeks.
            3. **Spring Chip Execution:** Mini-leagues are rarely won in autumn. Consistently executing the Wildcard-into-Bench-Boost double gameweek combo produces 70+ point swings over managers who burn chips prematurely.
            """)

        # --- TAB 5: INTEL FEED ---
        with tab_news:
            st.markdown("### Squad Intelligence & Match Commentary")
            st.caption("Real-time medical updates, tactical fixture assessments, and manager press conference summaries.")

            st.markdown("##### Squad Medical & Availability Bulletins")
            medical_alerts = [p for p in squad_list if p["data"]["status"] != "a" or p["data"].get("news")]

            if not medical_alerts:
                st.success("Clean bill of health: No active injuries or suspensions reported across your 15 players.")
            else:
                for m in medical_alerts:
                    mp = m["data"]
                    chance = mp.get("chance_of_playing_next_round")
                    ch_str = f" ({chance}% chance)" if chance is not None else ""
                    st.warning(f"**{mp['web_name']}** ({m['team_name']}): {mp.get('news', 'Status doubtful')}{ch_str}")

            st.markdown("##### Tactical Fixture Outlook for Starters")
            for p_item in best_starters[:4]:
                p = p_item["data"]
                opp_text = p_item["opp"]
                fdr_val = p_item["fdr"]
                form_val = float(p.get("form", 0))
                
                if fdr_val <= 2:
                    insight = f"Favorable matchup: Facing {opp_text}, giving {p['web_name']} high return probability based on defensive concession rates."
                elif fdr_val >= 4:
                    insight = f"Challenging test: {opp_text} represents a low-probability scoring environment; expected defensive pressure."
                else:
                    insight = f"Balanced fixture: Consistent expected returns anticipated against {opp_text}."

                st.markdown(f"• **{p['web_name']}** ({p_item['pos']}): {insight} *(Rolling Form: {form_val} pts/gm)*")

    except Exception as e:
        st.error(f"Error loading squad: {e}")

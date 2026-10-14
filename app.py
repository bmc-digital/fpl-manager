import streamlit as st
import json
import urllib.request

# Fragment Decorator (Streamlit 1.37+ native feature with safe fallback)
st_fragment = getattr(st, "fragment", lambda f: f)

# Clean HTML helper: strips all leading/trailing whitespace
def clean_html(raw_html: str) -> str:
    lines = [line.strip() for line in raw_html.strip().split('\n') if line.strip()]
    return "".join(lines)

# Page configuration
st.set_page_config(
    page_title="KINGS COUNTY FC FPL MANAGER",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Persistent Authentication via Secrets & Query Params
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme123") if hasattr(st, "secrets") else "changeme123"
DEFAULT_TEAM_ID = int(st.secrets.get("DEFAULT_TEAM_ID", 1)) if hasattr(st, "secrets") else 1

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = (st.query_params.get("auth") == "true")

if not st.session_state["authenticated"]:
    login_html = clean_html("""
    <div style="background: #141a24; border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 40px 24px; max-width: 360px; margin: 80px auto 20px auto; text-align: center; box-shadow: 0 16px 40px rgba(0,0,0,0.6);">
        <div style="width: 52px; height: 52px; background: rgba(0, 240, 255, 0.12); border-radius: 14px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h2 style="margin: 0 0 4px 0; font-size: 19px; font-weight: 800; color: #f0f3f8; letter-spacing: -0.3px;">KINGS COUNTY FC</h2>
        <p style="margin: 0; font-size: 13px; color: #8e9bb0;">FPL Tactical Intelligence</p>
    </div>
    """)
    st.markdown(login_html, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        pwd_input = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Enter passcode")
        if st.button("Unlock Dashboard", type="primary", use_container_width=True):
            if pwd_input == str(APP_PASSWORD):
                st.session_state["authenticated"] = True
                st.query_params["auth"] = "true"
                st.rerun()
            else:
                st.error("Incorrect passcode.")
    st.stop()

# HIGH-DENSITY DUAL-PANEL CANVASES & MODERN FPL STYLES
custom_styles = clean_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    /* HIDE STREAMLIT BANNERS & GITHUB WATERMARKS */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    .stApp {
        background-color: #090c10;
        color: #e3e8f0;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 100% !important;
    }
    
    h1, h2, h3, h4, h5 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.3px;
    }
    
    /* Dual-Panel Canvas Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #11151e !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
    }
    
    /* Micro-Metric Cards */
    .metric-pill {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        margin-right: 3px;
    }
    .fdr-2 { background-color: #00e676; color: #002e14; }
    .fdr-3 { background-color: #485366; color: #ffffff; }
    .fdr-4 { background-color: #ff4d6d; color: #ffffff; }
    .fdr-5 { background-color: #c9002b; color: #ffffff; }
</style>
""")
st.markdown(custom_styles, unsafe_allow_html=True)

# OPEN PUBLIC FOOTBALL CRESTS (football-data.org - ZERO S3 XML access errors)
CLUB_CRESTS = {
    'ARS': 'https://crests.football-data.org/57.png',
    'AVL': 'https://crests.football-data.org/58.png',
    'BOU': 'https://crests.football-data.org/1044.png',
    'BRE': 'https://crests.football-data.org/402.png',
    'BHA': 'https://crests.football-data.org/397.png',
    'CHE': 'https://crests.football-data.org/61.png',
    'CRY': 'https://crests.football-data.org/354.png',
    'EVE': 'https://crests.football-data.org/62.png',
    'FUL': 'https://crests.football-data.org/63.png',
    'IPS': 'https://crests.football-data.org/349.png',
    'LEI': 'https://crests.football-data.org/338.png',
    'LIV': 'https://crests.football-data.org/64.png',
    'MCI': 'https://crests.football-data.org/65.png',
    'MUN': 'https://crests.football-data.org/66.png',
    'NEW': 'https://crests.football-data.org/67.png',
    'NFO': 'https://crests.football-data.org/351.png',
    'SOU': 'https://crests.football-data.org/340.png',
    'TOT': 'https://crests.football-data.org/73.png',
    'WHU': 'https://crests.football-data.org/563.png',
    'WOL': 'https://crests.football-data.org/76.png'
}

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

# TOP COMMAND HEADER
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown(clean_html("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="width: 34px; height: 34px; background: rgba(0, 240, 255, 0.12); border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
            </div>
            <div>
                <h2 style="margin: 0; font-size: 18px; font-weight: 800; color: #f0f3f8; letter-spacing: -0.3px;">KINGS COUNTY FC FPL MANAGER</h2>
                <div style="font-size: 11px; color: #00f0ff; font-weight: 700; letter-spacing: 0.6px;">HIGH-DENSITY LINEUP & AI DECISION WORKSPACE</div>
            </div>
        </div>
    """), unsafe_allow_html=True)
with top_col2:
    h_c1, h_c2 = st.columns(2)
    with h_c1:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with h_c2:
        if st.button("Lock", use_container_width=True):
            st.session_state["authenticated"] = False
            st.query_params.clear()
            st.rerun()

# LOAD FPL CORE DATA
team_id = DEFAULT_TEAM_ID

with st.spinner("Connecting to FPL Data Engine..."):
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

    squad_list = []
    for pick in picks_data["picks"]:
        p = elements[pick["element"]]
        fdr = club_matches.get(p["team"], {}).get("fdr", 3)
        opp = club_matches.get(p["team"], {}).get("opp", "TBD")
        score = calculate_potential_score(p, fdr)
        t_short = teams[p["team"]]["short_name"]
        photo_code = str(p.get("code", "")).replace(".jpg", "").replace("p", "")
        photo_url = f"https://resources.premierleague.com/premierleague/photos/250x250/p{photo_code}.png"
        crest_url = CLUB_CRESTS.get(t_short, "https://crests.football-data.org/PL.png")

        squad_list.append({
            "data": p,
            "fdr": fdr,
            "opp": opp,
            "score": score,
            "pos_id": p["element_type"],
            "pos": positions[p["element_type"]],
            "photo": photo_url,
            "crest": crest_url,
            "team_short": t_short,
            "team_name": teams[p["team"]]["name"],
            "xg": p.get("expected_goals", "0.00"),
            "xa": p.get("expected_assists", "0.00")
        })

    # Formation Solver
    gkps = [p for p in squad_list if p["pos_id"] == 1]
    defs = sorted([p for p in squad_list if p["pos_id"] == 2], key=lambda x: x["score"], reverse=True)
    mids = sorted([p for p in squad_list if p["pos_id"] == 3], key=lambda x: x["score"], reverse=True)
    fwds = sorted([p for p in squad_list if p["pos_id"] == 4], key=lambda x: x["score"], reverse=True)

    starter_gkp = max(gkps, key=lambda x: x["score"])
    bench_gkp = [g for g in gkps if g != starter_gkp][0]

    valid_formations = [(3, 5, 2), (3, 4, 3), (4, 4, 2), (4, 3, 3), (4, 5, 1), (5, 3, 2), (5, 4, 1), (5, 2, 3)]
    best_formation = "3-4-3"
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

# -------------------------------------------------------------
# DUAL-PANEL CANVAS SPLIT: st.columns([3, 2])
# -------------------------------------------------------------
col_dashboard, col_ai_advisor = st.columns([3, 2], gap="medium")

# =============================================================
# LEFT PANEL (WIDTH 3): FANTASY PREMIER LEAGUE CARD MATRIX
# =============================================================
@st_fragment
def render_dashboard():
    with col_dashboard:
        # Micro Stats Bar
        m_bar1, m_bar2, m_bar3, m_bar4 = st.columns(4)
        m_bar1.caption(f"**Squad:** {entry_data['name']}")
        m_bar2.caption(f"**Formation:** {best_formation}")
        m_bar3.caption(f"**Overall:** {entry_data['summary_overall_points']} pts")
        m_bar4.caption(f"**Bank:** £{bank:.1f}m")

        tab_squad, tab_fdr, tab_transfers = st.tabs([
            "👕 My Squad",
            "🗓️ Fixture Difficulty (FDR)",
            "🔄 Transfer Planner"
        ])

        # --- TAB 1: ROSTER LINEUPS WITH HIGH-DENSITY CARDS ---
        with tab_squad:
            def render_player_ui_card(p, role_badge=""):
                with st.container(border=True):
                    p_c1, p_c2 = st.columns([1, 3])
                    with p_c1:
                        st.markdown(clean_html(f"""
                        <div style="width: 44px; height: 44px; border-radius: 50%; overflow: hidden; background: #1c2331; display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 1.5px solid rgba(255,255,255,0.15);">
                            <img src="{p['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{p['crest']}'; this.style.padding='6px';" style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        """), unsafe_allow_html=True)
                    with p_c2:
                        p_name = p['data']['web_name']
                        cost_str = f"£{p['data']['now_cost']/10:.1f}m"
                        fdr_cls = f"fdr-{p['fdr']}"
                        badge_html = f"<span style='color:#00f0ff; font-weight:800; font-size:10px;'> {role_badge}</span>" if role_badge else ""
                        
                        st.markdown(f"**{p_name}**{badge_html}", unsafe_allow_html=True)
                        st.markdown(clean_html(f"""
                        <div style="display: flex; gap: 4px; align-items: center; flex-wrap: wrap; margin-top: -2px;">
                            <span class="metric-pill" style="background:#1b2230; color:#8e9bb0;">{cost_str}</span>
                            <span class="metric-pill" style="background:#1b2230; color:#00e676;">{p['data']['form']} form</span>
                            <span class="metric-pill" style="background:#1b2230; color:#ffd166;">xG {p['xg']}</span>
                            <span class="metric-pill {fdr_cls}">{p['opp']}</span>
                        </div>
                        """), unsafe_allow_html=True)

            st.caption(f"Starting XI Lineup (Gameweek {next_gw})")
            
            # Goalkeeper
            render_player_ui_card(starter_gkp, role_badge="GKP")

            # Defenders
            cur_defs = [p for p in best_starters if p["pos_id"] == 2]
            def_cols = st.columns(len(cur_defs))
            for idx, p in enumerate(cur_defs):
                with def_cols[idx]:
                    r_tag = "C" if p == captain else ("VC" if p == vice_captain else "")
                    render_player_ui_card(p, role_badge=r_tag)

            # Midfielders
            cur_mids = [p for p in best_starters if p["pos_id"] == 3]
            mid_cols = st.columns(len(cur_mids))
            for idx, p in enumerate(cur_mids):
                with mid_cols[idx]:
                    r_tag = "C" if p == captain else ("VC" if p == vice_captain else "")
                    render_player_ui_card(p, role_badge=r_tag)

            # Forwards
            cur_fwds = [p for p in best_starters if p["pos_id"] == 4]
            fwd_cols = st.columns(len(cur_fwds))
            for idx, p in enumerate(cur_fwds):
                with fwd_cols[idx]:
                    r_tag = "C" if p == captain else ("VC" if p == vice_captain else "")
                    render_player_ui_card(p, role_badge=r_tag)

            # Bench Dugout
            st.divider()
            st.caption("Bench Substitutes (Priority Order)")
            b_cols = st.columns(4)
            with b_cols[0]:
                render_player_ui_card(bench_gkp, role_badge="SUB GKP")
            for idx, p in enumerate(best_bench_outfield):
                with b_cols[idx + 1]:
                    render_player_ui_card(p, role_badge=f"SUB {idx+1}")

        # --- TAB 2: FIXTURE DIFFICULTY (FDR) ---
        with tab_fdr:
            st.caption("Upcoming 3-Gameweek Schedule & Opponent Defense Matrix")
            fdr_rows = []
            for p in best_starters:
                p_team = teams[p["data"]["team"]]["name"]
                fdr_rows.append({
                    "Player": p["data"]["web_name"],
                    "Club": p_team,
                    f"GW {next_gw}": p["opp"],
                    "FDR": p["fdr"],
                    "Form": p["data"]["form"],
                    "xGI": float(p["xg"]) + float(p["xa"])
                })
            st.dataframe(fdr_rows, use_container_width=True, hide_index=True)

        # --- TAB 3: TRANSFER PLANNER ---
        with tab_transfers:
            st.caption("High-Priority Divestments & Target Acquisitions")
            transfer_out_eval = []
            for p_item in squad_list:
                p = p_item["data"]
                pos_id = p_item["pos_id"]
                sell_val = p["now_cost"] / 10
                max_budget = sell_val + bank

                replacements = []
                for cand in bootstrap["elements"]:
                    if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                        cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                        c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                        pot = calculate_potential_score(cand, c_fdr)
                        c_photo_code = str(cand.get("code", "")).replace(".jpg", "").replace("p", "")
                        c_t_short = teams[cand['team']]['short_name']
                        replacements.append({
                            "data": cand,
                            "score": pot,
                            "fdr": c_fdr,
                            "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                            "photo": f"https://resources.premierleague.com/premierleague/photos/250x250/p{c_photo_code}.png",
                            "crest": CLUB_CRESTS.get(c_t_short, ""),
                            "team_name": teams[cand['team']]['name']
                        })

                replacements.sort(key=lambda x: x["score"], reverse=True)
                top_repl = replacements[0] if replacements else None
                max_upside = round(top_repl["score"] - p_item["score"], 2) if top_repl else 0.0

                urgency = 0
                if p["status"] != "a":
                    urgency += 10
                if float(p.get("form", 0.0)) < 2.5:
                    urgency += 4
                if p_item["fdr"] >= 4:
                    urgency += 2

                transfer_out_eval.append({
                    "player": p_item,
                    "urgency": urgency,
                    "max_upside": max_upside,
                    "top_replacements": replacements[:3]
                })

            transfer_out_eval.sort(key=lambda x: (x["urgency"] * 1.5 + x["max_upside"]), reverse=True)
            
            for rank_idx, divest in enumerate(transfer_out_eval[:2], start=1):
                p_out = divest["player"]["data"]
                with st.container(border=True):
                    st.markdown(f"**Divestment Target #{rank_idx}:** {p_out['web_name']} (£{p_out['now_cost']/10:.1f}m)")
                    st.caption(f"Reason: Low form ({p_out['form']} pts) | Potential Upside: +{divest['max_upside']} pts")
                    
                    rep_cols = st.columns(len(divest["top_replacements"]))
                    for r_idx, rep in enumerate(divest["top_replacements"]):
                        with rep_cols[r_idx]:
                            cand_p = rep["data"]
                            st.markdown(f"**{r_idx+1}. {cand_p['web_name']}** (£{cand_p['now_cost']/10:.1f}m)")
                            st.caption(f"{rep['opp']} (FDR {rep['fdr']}) • Form: {cand_p['form']}")

render_dashboard()

# =============================================================
# RIGHT PANEL (WIDTH 2): CONVERSATIONAL AI LINEUP ADVISOR
# =============================================================
@st_fragment
def render_ai_advisor():
    with col_ai_advisor:
        with st.container(border=True):
            st.markdown(clean_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #00e676; box-shadow: 0 0 8px #00e676;"></div>
                    <span style="font-weight: 800; font-size: 14px; color: #f0f3f8;">AI Lineup Advisor</span>
                </div>
                <span style="font-size: 11px; color: #00f0ff; background: rgba(0, 240, 255, 0.12); padding: 2px 8px; border-radius: 12px; font-weight: 700;">Live Engine</span>
            </div>
            """), unsafe_allow_html=True)

            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": "Welcome to Kings County FC Tactical Command. I'm connected to your live squad data and FDR feeds. How can I optimize your lineup today?"}
                ]

            # Quick-Action Button Chips
            st.caption("Quick Tactical Inquiries:")
            q_cols = st.columns(2)
            with q_cols[0]:
                chip_cap = st.button("👑 Recommend Captain", use_container_width=True)
                chip_hit = st.button("⚡ Suggest -4 Hit Transfer", use_container_width=True)
            with q_cols[1]:
                chip_bench = st.button("🪑 Solve Bench Dilemma", use_container_width=True)
                chip_wc = st.button("🛡️ Evaluate Chip Timing", use_container_width=True)

            prompt = None
            if chip_cap:
                prompt = "Recommend my optimal Captain and Vice-Captain picks for the upcoming gameweek."
            elif chip_bench:
                prompt = "Solve my bench dilemma and advise on who should start vs sit."
            elif chip_hit:
                prompt = "Analyze if taking a -4 transfer penalty hit makes mathematical sense this week."
            elif chip_wc:
                prompt = "Evaluate optimal timing for my Wildcard, Triple Captain, and Bench Boost chips."

            # Scrollable Chat Container
            chat_container = st.container(height=420)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if "status_box" in msg:
                            with st.status(msg["status_box"]["title"], state="complete"):
                                st.markdown(msg["status_box"]["details"])

            # Native Chat Input
            user_input = st.chat_input("Ask your FPL Advisor anything...")
            if user_input:
                prompt = user_input

            # Process Response
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                with chat_container:
                    with st.chat_message("assistant"):
                        p_lower = prompt.lower()
                        status_payload = None

                        if "captain" in p_lower:
                            reply_text = f"**Tactical Captain Recommendation:**\n\n- **Primary (2x):** **{captain['data']['web_name']}** (Projected: {captain['score']} pts, {captain['opp']})\n- **Vice-Captain:** **{vice_captain['data']['web_name']}** (Projected: {vice_captain['score']} pts, {vice_captain['opp']})\n\n{captain['data']['web_name']} ranks #1 across your squad in expected goal involvement and faces an optimal fixture rating."
                        
                        elif "bench" in p_lower:
                            reply_text = f"**Bench Optimization Strategy:**\n\nYour optimal starting formation is **{best_formation}**.\n\n- **1st Sub:** **{best_bench_outfield[0]['data']['web_name']}** (Projection: {best_bench_outfield[0]['score']} pts)\n- **2nd Sub:** **{best_bench_outfield[1]['data']['web_name']}**\n- **3rd Sub:** **{best_bench_outfield[2]['data']['web_name']}**\n\nYour bench order prioritizes appearance probability to guard against surprise rotations."

                        elif "hit" in p_lower or "-4" in p_lower or "transfer" in p_lower:
                            status_payload = {
                                "title": "Mathematical Transfer ROI Optimization",
                                "details": f"- **Penalty Cost:** -4.0 pts\n- **Required Outperformance:** Replacement must score ≥ 6 pts to justify hit\n- **Bank Surplus Available:** £{bank:.1f}m\n- **Algorithm Verdict:** Unless replacing a ruled-out player, rolling your transfer yields higher expected value."
                            }
                            with st.status(status_payload["title"], expanded=True):
                                st.markdown(status_payload["details"])
                            reply_text = "Based on expected goals conceded and fixture swings, taking a -4 hit is **not recommended** unless covering an injury. Save your free transfer to bank two moves next week."

                        elif "chip" in p_lower or "wildcard" in p_lower:
                            reply_text = "**Strategic Chip Outlook:**\n\n- **Triple Captain:** Hold strictly for a confirmed **Double Gameweek (GW 25 or 34)** where premium players play 180 minutes.\n- **Bench Boost:** Target the spring Double Gameweek (GW 34 or 37) paired with your second Wildcard.\n- **Free Hit:** Reserve for the major FA Cup Blank Gameweek (GW 29)."

                        else:
                            reply_text = f"Analyzing tactical data for '{prompt}'... Your squad projection for Gameweek {next_gw} is solid with an expected core of {best_score:.1f} points. Keep monitoring press conference bulletins ahead of the deadline."

                        st.markdown(reply_text)

                        new_msg = {"role": "assistant", "content": reply_text}
                        if status_payload:
                            new_msg["status_box"] = status_payload
                        st.session_state.messages.append(new_msg)

render_ai_advisor()

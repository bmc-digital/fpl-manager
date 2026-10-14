import streamlit as st
import json
import urllib.request

# Clean HTML helper: strips all leading/trailing indentation so Markdown never triggers code blocks
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
    <div style="background: #16181f; border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 36px 24px; max-width: 380px; margin: 70px auto 20px auto; text-align: center; box-shadow: 0 12px 40px rgba(0,0,0,0.5);">
        <div style="width: 48px; height: 48px; background: rgba(0, 230, 118, 0.12); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h2 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 700; color: #f0f1f5; letter-spacing: -0.3px;">FPL Elite Manager</h2>
        <p style="margin: 0; font-size: 13px; color: #8e92a2;">Enter your passcode to access tactical analysis</p>
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

# HIGH-END SPORTS ANALYTICS DARK UI STYLES
m3_styles = clean_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0c0d12;
        color: #e2e4ec;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.4px;
    }
    
    .app-card {
        background-color: #151720;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    
    .pitch-surface {
        background: radial-gradient(circle at 50% 30%, #15291b 0%, #0c1a11 70%, #07100a 100%);
        border: 1.5px solid rgba(0, 230, 118, 0.22);
        border-radius: 20px;
        padding: 22px 10px;
        margin: 12px 0;
        position: relative;
        box-shadow: inset 0 0 50px rgba(0,0,0,0.6), 0 8px 30px rgba(0,0,0,0.3);
    }
    
    .pitch-row-flex {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
        flex-wrap: wrap;
    }
    
    .pitch-player-item {
        background-color: rgba(21, 23, 32, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 8px 6px;
        width: 84px;
        min-width: 84px;
        text-align: center;
        backdrop-filter: blur(8px);
        position: relative;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .pitch-player-item:hover {
        transform: translateY(-2px);
        border-color: #00e676;
    }
    
    .avatar-frame {
        width: 52px;
        height: 52px;
        margin: 0 auto;
        position: relative;
    }
    .avatar-frame img.player-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        background-color: #212430;
        border: 1.5px solid rgba(255, 255, 255, 0.14);
    }
    .avatar-frame img.crest-img {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background-color: #151720;
        padding: 1px;
    }
    
    .player-label {
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 5px;
        color: #f0f1f5;
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
        position: absolute;
        top: -6px;
        right: -6px;
        background: #00e676;
        color: #002e14;
        font-weight: 900;
        font-size: 9px;
        padding: 2px 5px;
        border-radius: 5px;
        box-shadow: 0 2px 6px rgba(0, 230, 118, 0.4);
    }
    .badge-vc {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #00d2ff;
        color: #002a35;
        font-weight: 900;
        font-size: 9px;
        padding: 2px 5px;
        border-radius: 5px;
    }
    .badge-sub {
        position: absolute;
        top: -6px;
        left: -6px;
        background: #434654;
        color: #e2e4ec;
        font-weight: 700;
        font-size: 8px;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    .bench-shelf {
        background-color: #12141c;
        border: 1px dashed rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 14px 10px;
        margin-top: 14px;
    }
</style>
""")
st.markdown(m3_styles, unsafe_allow_html=True)

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

# TOP APP BAR
col_head, col_logout = st.columns([5, 1])
with col_head:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#00e676" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/>
            </svg>
            <div>
                <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: #f0f1f5; letter-spacing: -0.4px;">FPL Elite Manager</h1>
                <p style="margin: 0; font-size: 13px; color: #8e92a2;">Tactical Performance & Transfer Intelligence</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("Log out"):
        st.session_state["authenticated"] = False
        st.rerun()

col_input, col_action = st.columns([3, 1])
with col_input:
    team_id = st.number_input("Team ID", min_value=1, value=DEFAULT_TEAM_ID, step=1, label_visibility="collapsed")
with col_action:
    refresh_click = st.button("Refresh Live Data", use_container_width=True, type="primary")

if team_id:
    with st.spinner("Analyzing live performance data..."):
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
                
                photo_code = str(p.get("code", "")).replace(".jpg", "").replace("p", "")
                team_code = teams[p["team"]]["code"]
                photo_url = f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{photo_code}.png"
                badge_url = f"https://resources.premierleague.com/premierleague/badges/70/t{team_code}.png"

                squad_list.append({
                    "data": p,
                    "fdr": fdr,
                    "opp": opp,
                    "score": score,
                    "pos_id": p["element_type"],
                    "pos": positions[p["element_type"]],
                    "photo": photo_url,
                    "badge": badge_url,
                    "team_name": teams[p["team"]]["name"],
                    "team_code": team_code
                })

            # FORMATION OPTIMIZER
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

            # POPUP MODAL FOR DETAILED PLAYER STATS
            if hasattr(st, "dialog"):
                @st.dialog("Player Dossier & Match Readiness")
                def show_player_modal(p_item):
                    p = p_item["data"]
                    
                    chance = p.get("chance_of_playing_next_round")
                    status_text = "100% Fit & Available"
                    status_color = "#00e676"
                    if p["status"] != "a":
                        if chance is not None:
                            status_text = f"{chance}% Chance of Playing"
                            status_color = "#ffb300" if chance >= 50 else "#ff3b5c"
                        else:
                            status_text = "Out / Suspended (0%)"
                            status_color = "#ff3b5c"

                    header_html = clean_html(f"""
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                        <div style="width: 64px; height: 64px; position: relative;">
                            <img src="{p_item['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{p_item['badge']}';" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background: #212430; border: 2px solid rgba(255,255,255,0.1);">
                            <img src="{p_item['badge']}" referrerpolicy="no-referrer" style="position: absolute; bottom: -2px; right: -2px; width: 22px; height: 22px; background: #151720; border-radius: 50%;">
                        </div>
                        <div>
                            <h3 style="margin: 0; font-size: 18px; color: #f0f1f5;">{p['first_name']} {p['second_name']}</h3>
                            <div style="font-size: 12px; color: #8e92a2;">{p_item['team_name']} • {p_item['pos']} • £{p['now_cost']/10:.1f}m</div>
                            <div style="display: inline-block; background: {status_color}22; color: {status_color}; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px; margin-top: 4px;">
                                {status_text}
                            </div>
                        </div>
                    </div>
                    """)
                    st.markdown(header_html, unsafe_allow_html=True)

                    if p.get("news"):
                        st.info(f"Official Bulletin: {p['news']}")

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Form", p.get("form", "0.0"))
                    c2.metric("Total Points", p.get("total_points", 0))
                    c3.metric("Selected By", f"{p.get('selected_by_percent', '0')}%")

                    c4, c5, c6 = st.columns(3)
                    c4.metric("Exp. Goals (xG)", p.get("expected_goals", "0.00"))
                    c5.metric("Exp. Assists (xA)", p.get("expected_assists", "0.00"))
                    c6.metric("Exp. Involvements", p.get("expected_goal_involvements", "0.00"))

                    c7, c8, c9 = st.columns(3)
                    c7.metric("Minutes Played", p.get("minutes", 0))
                    c8.metric("Bonus Points", p.get("bonus", 0))
                    c9.metric("Next Match", p_item["opp"])

            # NAVIGATION TABS
            tab_pitch, tab_transfers, tab_simulator, tab_chips, tab_news = st.tabs([
                "Starting XI", 
                "Transfers", 
                "Simulator", 
                "Captain & Chips",
                "Intel Feed"
            ])

            def render_pitch_card(p, tag=""):
                badge_html = ""
                if p == captain:
                    badge_html = '<div class="badge-c">C</div>'
                elif p == vice_captain:
                    badge_html = '<div class="badge-vc">VC</div>'
                elif tag:
                    badge_html = f'<div class="badge-sub">{tag}</div>'

                return clean_html(f"""
                <div class="pitch-player-item">
                    {badge_html}
                    <div class="avatar-frame">
                        <img class="player-img" src="{p['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{p['badge']}';">
                        <img class="crest-img" src="{p['badge']}" referrerpolicy="no-referrer">
                    </div>
                    <div class="player-label">{p['data']['web_name']}</div>
                    <div><span class="fdr-pill fdr-{p['fdr']}">{p['opp']}</span></div>
                    <div style="font-size: 10px; font-weight: 800; color: #00e676; margin-top: 2px;">{p['score']} pts</div>
                </div>
                """)

            # TAB 1: STARTING XI
            with tab_pitch:
                st.markdown(clean_html(f"""
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px;">
                    <h3 style="margin: 0; font-size: 17px; font-weight: 700; color: #f0f1f5;">Gameweek {next_gw} Starting XI</h3>
                    <div style="font-size: 12px; color: #00e676; font-weight: 700;">Tactical Formation: {best_formation}</div>
                </div>
                """), unsafe_allow_html=True)

                pitch_rows = []
                pitch_rows.append(f'<div class="pitch-row-flex">{render_pitch_card(starter_gkp)}</div>')
                pitch_rows.append(f'<div class="pitch-row-flex">{"".join([render_pitch_card(p) for p in best_starters if p["pos_id"] == 2])}</div>')
                pitch_rows.append(f'<div class="pitch-row-flex">{"".join([render_pitch_card(p) for p in best_starters if p["pos_id"] == 3])}</div>')
                pitch_rows.append(f'<div class="pitch-row-flex">{"".join([render_pitch_card(p) for p in best_starters if p["pos_id"] == 4])}</div>')

                pitch_html = clean_html(f'<div class="pitch-surface">{"".join(pitch_rows)}</div>')
                st.markdown(pitch_html, unsafe_allow_html=True)

                # Bench Dugout
                bench_cards = "".join([
                    render_pitch_card(bench_gkp, tag="GKP"),
                    render_pitch_card(best_bench_outfield[0], tag="SUB 1"),
                    render_pitch_card(best_bench_outfield[1], tag="SUB 2"),
                    render_pitch_card(best_bench_outfield[2], tag="SUB 3")
                ])
                dugout_html = clean_html(f"""
                <div class="bench-shelf">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #8e92a2; margin-bottom: 8px; text-align: center;">
                        Priority Bench Order
                    </div>
                    <div class="pitch-row-flex" style="margin-bottom: 0;">
                        {bench_cards}
                    </div>
                </div>
                """)
                st.markdown(dugout_html, unsafe_allow_html=True)

                # Interactive Modal Inspection Selector
                st.markdown("---")
                st.markdown("##### Detailed Scouting Report")
                starter_names = [f"{p['data']['web_name']} ({p['pos']}) - {p['opp']}" for p in squad_list]
                inspect_idx = st.selectbox("Select any squad member to open their match readiness report:", range(len(starter_names)), format_func=lambda x: starter_names[x])
                if st.button("Open Player Dossier", type="secondary", use_container_width=True):
                    if hasattr(st, "dialog"):
                        show_player_modal(squad_list[inspect_idx])
                    else:
                        st.info("Full stats for " + squad_list[inspect_idx]["data"]["web_name"])

            # TAB 2: TRANSFERS
            with tab_transfers:
                st.markdown("### Transfer Guidance")
                sell_candidates = []
                for p_item in squad_list:
                    p = p_item["data"]
                    fdr = p_item["fdr"]
                    form = float(p.get("form", 0.0))
                    urgency = 0
                    reasons = []

                    if p["status"] != "a":
                        chance = p.get("chance_of_playing_next_round")
                        urgency += 10 if (chance is not None and chance <= 25) else 6
                        reasons.append(f"Flagged ({chance}% play chance)" if chance else "Injured / Suspended")
                    if form < 2.5:
                        urgency += 3
                        reasons.append("Cold Form (<2.5 pts)")
                    if fdr >= 4:
                        urgency += 2
                        reasons.append(f"Challenging Fixture (FDR {fdr})")

                    if urgency >= 4:
                        sell_candidates.append({"player": p_item, "urgency": urgency, "reason": ", ".join(reasons)})

                sell_candidates.sort(key=lambda x: x["urgency"], reverse=True)

                if not sell_candidates:
                    st.success("Your squad is currently in prime condition. No urgent transfers required.")
                else:
                    for target in sell_candidates[:2]:
                        p_sell = target["player"]["data"]
                        pos_id = p_sell["element_type"]
                        sell_val = p_sell["now_cost"] / 10
                        max_budget = sell_val + bank

                        sell_card_html = clean_html(f"""
                        <div class="app-card" style="border-left: 4px solid #ff3b5c; background-color: #1f1418;">
                            <div style="display: inline-block; background-color: #ff3b5c; color: #ffffff; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;">DIVESTMENT PRIORITY</div>
                            <h4 style="margin: 8px 0 4px 0; color: #ffb4ab;">{p_sell['web_name']} ({positions[pos_id]}) — £{sell_val:.1f}m</h4>
                            <p style="font-size: 13px; color: #c4c6d0; margin-bottom: 6px;">Evaluation: <strong>{target['reason']}</strong></p>
                            <p style="font-size: 12px; color: #00e676;">Available Capital: <strong>£{max_budget:.1f}m</strong> (£{sell_val:.1f}m sale + £{bank:.1f}m bank balance)</p>
                        </div>
                        """)
                        st.markdown(sell_card_html, unsafe_allow_html=True)

                        pool = []
                        for cand in bootstrap["elements"]:
                            if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                                cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                                c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                                pot = calculate_potential_score(cand, c_fdr)
                                cand_photo_code = str(cand.get("code", "")).replace(".jpg", "").replace("p", "")
                                cand_team_code = teams[cand['team']]['code']
                                pool.append({
                                    "data": cand,
                                    "score": pot,
                                    "fdr": c_fdr,
                                    "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                                    "photo": f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{cand_photo_code}.png",
                                    "badge": f"https://resources.premierleague.com/premierleague/badges/70/t{cand_team_code}.png"
                                })

                        pool.sort(key=lambda x: x["score"], reverse=True)
                        cols_buy = st.columns(min(3, len(pool)))
                        for idx, buy_cand in enumerate(pool[:3]):
                            with cols_buy[idx]:
                                bp = buy_cand["data"]
                                buy_html = clean_html(f"""
                                <div class="app-card" style="text-align: center; border-color: rgba(0, 230, 118, 0.4);">
                                    <div style="font-size: 10px; font-weight: 700; color: #00e676;">TARGET #{idx+1}</div>
                                    <div class="avatar-frame" style="margin: 8px auto; width: 54px; height: 54px;">
                                        <img class="player-img" src="{buy_cand['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{buy_cand['badge']}';">
                                        <img class="crest-img" src="{buy_cand['badge']}" referrerpolicy="no-referrer">
                                    </div>
                                    <div style="font-weight: 700; font-size: 13px; color: #f0f1f5;">{bp['web_name']}</div>
                                    <div style="font-size: 11px; color: #8e92a2;">£{bp['now_cost']/10:.1f}m | Form: {bp['form']}</div>
                                    <div style="margin-top: 4px;"><span class="fdr-pill fdr-{buy_cand['fdr']}">{buy_cand['opp']}</span></div>
                                    <div style="margin-top: 6px; font-size: 12px; font-weight: 800; color: #00e676;">{buy_cand['score']} pts</div>
                                </div>
                                """)
                                st.markdown(buy_html, unsafe_allow_html=True)

            # TAB 3: SIMULATOR
            with tab_simulator:
                st.markdown("### Transfer Simulator & Scenario Modeling")
                st.caption("Model potential trades to evaluate projected points gain, capital allocation, and tactical fit.")

                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    st.markdown("##### 1. Outgoing Player (Sell)")
                    sell_names = [f"{p['data']['web_name']} ({p['pos']}) - £{p['data']['now_cost']/10:.1f}m" for p in squad_list]
                    sell_choice_idx = st.selectbox("Select player to sell:", range(len(sell_names)), format_func=lambda x: sell_names[x])
                    selected_sell = squad_list[sell_choice_idx]
                    sell_player = selected_sell["data"]
                    sell_price = sell_player["now_cost"] / 10
                    sim_budget = sell_price + bank

                    out_card = clean_html(f"""
                    <div class="app-card" style="display: flex; align-items: center; gap: 14px; border-left: 3px solid #ff3b5c; margin-top: 8px;">
                        <div class="avatar-frame" style="width: 52px; height: 52px;">
                            <img class="player-img" src="{selected_sell['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{selected_sell['badge']}';">
                            <img class="crest-img" src="{selected_sell['badge']}" referrerpolicy="no-referrer">
                        </div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: #f0f1f5;">{sell_player['web_name']}</div>
                            <div style="font-size: 12px; color: #8e92a2;">{selected_sell['pos']} • Sale Value: £{sell_price:.1f}m</div>
                            <div style="font-size: 11px; color: #00e676; margin-top: 2px;">Total Buy Budget: £{sim_budget:.1f}m</div>
                        </div>
                    </div>
                    """)
                    st.markdown(out_card, unsafe_allow_html=True)

                with sim_col2:
                    st.markdown("##### 2. Incoming Candidate (Buy)")
                    target_pos_id = selected_sell["pos_id"]
                    all_candidates = [
                        c for c in bootstrap["elements"] 
                        if c["element_type"] == target_pos_id and c["id"] not in squad_ids
                    ]
                    all_candidates.sort(key=lambda x: x["now_cost"], reverse=True)
                    buy_names = [f"{c['web_name']} ({teams[c['team']]['short_name']}) - £{c['now_cost']/10:.1f}m" for c in all_candidates]
                    buy_choice_idx = st.selectbox("Select replacement to evaluate:", range(len(buy_names)), format_func=lambda x: buy_names[x])
                    selected_buy = all_candidates[buy_choice_idx]
                    buy_price = selected_buy["now_cost"] / 10
                    
                    buy_photo_code = str(selected_buy.get("code", "")).replace(".jpg", "").replace("p", "")
                    buy_badge_url = f"https://resources.premierleague.com/premierleague/badges/70/t{teams[selected_buy['team']]['code']}.png"
                    buy_photo_url = f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{buy_photo_code}.png"

                    in_card = clean_html(f"""
                    <div class="app-card" style="display: flex; align-items: center; gap: 14px; border-left: 3px solid #00e676; margin-top: 8px;">
                        <div class="avatar-frame" style="width: 52px; height: 52px;">
                            <img class="player-img" src="{buy_photo_url}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{buy_badge_url}';">
                            <img class="crest-img" src="{buy_badge_url}" referrerpolicy="no-referrer">
                        </div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: #f0f1f5;">{selected_buy['web_name']}</div>
                            <div style="font-size: 12px; color: #8e92a2;">{teams[selected_buy['team']]['name']} • Cost: £{buy_price:.1f}m</div>
                            <div style="font-size: 11px; color: #8e92a2; margin-top: 2px;">Form: {selected_buy['form']} | Pts: {selected_buy['total_points']}</div>
                        </div>
                    </div>
                    """)
                    st.markdown(in_card, unsafe_allow_html=True)

                buy_fdr = club_matches.get(selected_buy["team"], {}).get("fdr", 3)
                buy_potential = calculate_potential_score(selected_buy, buy_fdr)
                sell_potential = selected_sell["score"]
                delta_score = round(buy_potential - sell_potential, 2)
                new_bank = round(sim_budget - buy_price, 2)

                rationale_lines = []
                if new_bank < 0:
                    rationale_lines.append(f"Transfer blocked: Exceeds your available capital by £{abs(new_bank):.1f}m.")
                else:
                    if delta_score > 1.5:
                        rationale_lines.append(f"High-impact upgrade. {selected_buy['web_name']} presents a sharp scoring surge based on current form ({selected_buy['form']}) and favorable match dynamics compared to {sell_player['web_name']}.")
                    elif delta_score > 0:
                        rationale_lines.append(f"Moderate positive differential. {selected_buy['web_name']} offers a marginal expected projection increase (+{delta_score:.1f} pts), making it a viable swap if addressing fixture swings.")
                    elif delta_score == 0:
                        rationale_lines.append(f"Lateral repositioning. Both players hold equivalent near-term scoring expectations; consider preserving your free transfer unless targeting budget reallocation.")
                    else:
                        rationale_lines.append(f"Negative projection delta. {sell_player['web_name']} retains superior short-term performance upside over {selected_buy['web_name']}; delaying this move is recommended.")

                st.markdown("---")
                st.markdown("#### Scenario Impact Analysis")
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric("Net Projected Points Delta", f"{delta_score:+} pts", f"vs {sell_player['web_name']}")
                with res_col2:
                    st.metric("Remaining Bank Balance", f"£{new_bank:.1f}m", f"£{new_bank - bank:+.1f}m capital change")

                st.info(" ".join(rationale_lines))

                st.markdown(f"##### Recommended Replacements for {sell_player['web_name']} (Within £{sim_budget:.1f}m Budget)")
                sim_replacements = []
                for cand in bootstrap["elements"]:
                    if (cand["element_type"] == target_pos_id and cand["status"] == "a" and 
                        cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= sim_budget):
                        c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                        p_score = calculate_potential_score(cand, c_fdr)
                        c_photo_code = str(cand.get("code", "")).replace(".jpg", "").replace("p", "")
                        c_badge = f"https://resources.premierleague.com/premierleague/badges/70/t{teams[cand['team']]['code']}.png"
                        c_photo = f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{c_photo_code}.png"
                        sim_replacements.append({
                            "data": cand,
                            "score": p_score,
                            "fdr": c_fdr,
                            "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                            "photo": c_photo,
                            "badge": c_badge,
                            "team_name": teams[cand['team']]['name']
                        })

                sim_replacements.sort(key=lambda x: x["score"], reverse=True)
                top3 = sim_replacements[:3]

                for idx, r_item in enumerate(top3, start=1):
                    rp = r_item["data"]
                    r_cost = rp["now_cost"] / 10
                    r_delta = round(r_item["score"] - sell_potential, 2)
                    
                    rep_html = clean_html(f"""
                    <div class="app-card" style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; border-left: 3px solid #00e676;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="font-weight: 800; font-size: 14px; color: #00e676;">#{idx}</div>
                            <div class="avatar-frame" style="width: 48px; height: 48px;">
                                <img class="player-img" src="{r_item['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{r_item['badge']}';">
                                <img class="crest-img" src="{r_item['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <div style="font-size: 14px; font-weight: 700; color: #f0f1f5;">{rp['web_name']} ({r_item['team_name']})</div>
                                <div style="font-size: 12px; color: #8e92a2;">Cost: £{r_cost:.1f}m • Form: {rp['form']} • Next: {r_item['opp']} (FDR {r_item['fdr']})</div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 14px; font-weight: 800; color: #00e676;">{r_delta:+} pts gain</div>
                            <div style="font-size: 11px; color: #8e92a2;">Potential: {r_item['score']} pts</div>
                        </div>
                    </div>
                    """)
                    st.markdown(rep_html, unsafe_allow_html=True)

            # TAB 4: CAPTAINCY & CHIPS
            with tab_chips:
                st.markdown("### Captaincy Leadership & Chip Deployment")
                c1, c2 = st.columns(2)
                with c1:
                    cap_html = clean_html(f"""
                    <div class="app-card" style="border: 1.5px solid #00e676;">
                        <span class="badge-c" style="position: static; font-size: 10px;">OPTIMAL CAPTAIN (2x)</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="avatar-frame" style="width: 58px; height: 58px;">
                                <img class="player-img" src="{captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{captain['badge']}';">
                                <img class="crest-img" src="{captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #00e676; font-size: 17px;">{captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; color: #8e92a2;">{captain['pos']} • {captain['opp']}</div>
                                <div style="font-size: 15px; font-weight: 800; margin-top: 4px; color: #f0f1f5;">Projection: {captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """)
                    st.markdown(cap_html, unsafe_allow_html=True)

                with c2:
                    vc_html = clean_html(f"""
                    <div class="app-card" style="border: 1.5px solid #00d2ff;">
                        <span class="badge-vc" style="position: static; font-size: 10px;">VICE-CAPTAIN ALTERNATIVE</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="avatar-frame" style="width: 58px; height: 58px;">
                                <img class="player-img" src="{vice_captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{vice_captain['badge']}';">
                                <img class="crest-img" src="{vice_captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #00d2ff; font-size: 17px;">{vice_captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; color: #8e92a2;">{vice_captain['pos']} • {vice_captain['opp']}</div>
                                <div style="font-size: 15px; font-weight: 800; margin-top: 4px; color: #f0f1f5;">Projection: {vice_captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """)
                    st.markdown(vc_html, unsafe_allow_html=True)

                st.markdown("#### Chip Advisory Status")
                chip1, chip2 = st.columns(2)
                with chip1:
                    if captain["score"] >= 6.5 and captain["fdr"] == 2:
                        st.success(f"Triple Captain: Viable. {captain['data']['web_name']} combines elite form with a favorable match.")
                    else:
                        st.info("Triple Captain: Hold. Better upside exists in future Double Gameweeks.")
                with chip2:
                    active_bench = sum(1 for b in best_bench_outfield if b["data"]["status"] == "a" and float(b["data"].get("form", 0)) > 1.5)
                    if active_bench == 3 and bench_gkp["data"]["status"] == "a":
                        st.success("Bench Boost: Strong. All 4 bench players are reliable active starters.")
                    else:
                        st.info(f"Bench Boost: Hold. {active_bench}/3 outfield bench players are currently active starters.")

            # TAB 5: INTEL & NEWS FEED
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

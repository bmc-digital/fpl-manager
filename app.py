import streamlit as st
import json
import urllib.request

# Helper to clean multi-line HTML and eliminate Markdown code block triggers
def clean_html(raw_html: str) -> str:
    lines = [line.strip() for line in raw_html.strip().split('\n') if line.strip()]
    return "".join(lines)

# Page configuration
st.set_page_config(
    page_title="FPL Elite Manager",
    page_icon="⚽",
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
    <div style="background: #1a1c22; border: 1px solid rgba(255,255,255,0.1); border-radius: 28px; padding: 36px 24px; max-width: 400px; margin: 60px auto 20px auto; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
        <div style="width: 56px; height: 56px; background: rgba(0, 230, 118, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 28px;">⚽</div>
        <h2 style="margin: 0 0 6px 0; font-size: 22px; font-weight: 700; color: #e2e2e9;">FPL Elite Manager</h2>
        <p style="margin: 0; font-size: 14px; color: #8e919a;">Enter your passcode to unlock your dashboard</p>
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

# GOOGLE MATERIAL DESIGN 3 (M3) STYLES
m3_styles = clean_html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', -apple-system, sans-serif;
    }
    
    .stApp {
        background-color: #111318;
        color: #e2e2e9;
    }
    
    .m3-card {
        background-color: #1a1c22;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }
    
    .m3-pitch {
        background: radial-gradient(circle at 50% 30%, #152d1d 0%, #0d1e13 65%, #07130b 100%);
        border: 1.5px solid rgba(77, 255, 145, 0.25);
        border-radius: 24px;
        padding: 20px 10px;
        margin: 12px 0;
        position: relative;
        box-shadow: inset 0 0 50px rgba(0,0,0,0.6), 0 8px 24px rgba(0,0,0,0.3);
    }
    
    .m3-pitch-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    
    .m3-player-card {
        background-color: rgba(26, 28, 34, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 8px 6px;
        width: 82px;
        min-width: 82px;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        position: relative;
        transition: transform 0.15s ease;
    }
    .m3-player-card:hover {
        transform: translateY(-2px);
        border-color: #00e676;
    }
    
    .m3-avatar-wrap {
        width: 50px;
        height: 50px;
        margin: 0 auto;
        position: relative;
    }
    .m3-avatar-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        background-color: #2b2d35;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .m3-crest-badge {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background-color: #1a1c22;
        padding: 1px;
    }
    
    .m3-player-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 4px;
        color: #f0f0f5;
    }
    
    .m3-chip {
        display: inline-block;
        font-size: 9px;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 6px;
        margin-top: 3px;
        letter-spacing: 0.3px;
    }
    .m3-chip-fdr-2 { background-color: #00e676; color: #000000; }
    .m3-chip-fdr-3 { background-color: #44474e; color: #ffffff; }
    .m3-chip-fdr-4 { background-color: #ff5252; color: #ffffff; }
    .m3-chip-fdr-5 { background-color: #d50000; color: #ffffff; }
    
    .m3-badge-c {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #00e676;
        color: #003919;
        font-weight: 900;
        font-size: 9px;
        padding: 2px 5px;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0, 230, 118, 0.4);
    }
    .m3-badge-vc {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #80d8ff;
        color: #00364c;
        font-weight: 900;
        font-size: 9px;
        padding: 2px 5px;
        border-radius: 6px;
    }
    .m3-badge-sub {
        position: absolute;
        top: -6px;
        left: -6px;
        background: #44474e;
        color: #e2e2e9;
        font-weight: 700;
        font-size: 8px;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    .m3-dugout {
        background-color: #16181e;
        border: 1px dashed rgba(255,255,255,0.15);
        border-radius: 18px;
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
            <div style="font-size: 26px;">⚽</div>
            <div>
                <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #00e676; letter-spacing: -0.5px;">FPL Elite</h1>
                <p style="margin: 0; font-size: 13px; color: #8e919a;">Tactical Lineup & Transfer Decision Engine</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("Log out"):
        st.session_state["authenticated"] = False
        st.rerun()

# Controls row
col_input, col_action = st.columns([3, 1])
with col_input:
    team_id = st.number_input("Team ID", min_value=1, value=DEFAULT_TEAM_ID, step=1, label_visibility="collapsed")
with col_action:
    refresh_click = st.button("⚡ Refresh Data", use_container_width=True, type="primary")

if team_id:
    with st.spinner("Analyzing Premier League data..."):
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

            # M3 HERO OVERVIEW CARD
            hero_html = clean_html(f"""
            <div class="m3-card" style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; gap: 12px;">
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #8e919a; font-weight: 700;">Manager</div>
                        <div style="font-size: 16px; font-weight: 700; color: #e2e2e9;">{entry_data['player_first_name']} {entry_data['player_last_name']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #8e919a; font-weight: 700;">Team</div>
                        <div style="font-size: 16px; font-weight: 700; color: #00e676;">{entry_data['name']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #8e919a; font-weight: 700;">Overall Points</div>
                        <div style="font-size: 20px; font-weight: 800; color: #e2e2e9;">{entry_data['summary_overall_points']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #8e919a; font-weight: 700;">In Bank</div>
                        <div style="font-size: 20px; font-weight: 800; color: #00e676;">£{bank:.1f}m</div>
                    </div>
                </div>
            </div>
            """)
            st.markdown(hero_html, unsafe_allow_html=True)

            # Build enriched player squad list with bulletproof image fallbacks
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

            # M3 NAVIGATION TABS
            tab_pitch, tab_transfers, tab_simulator, tab_chips = st.tabs([
                "🏟️ Starting XI", 
                "🔄 Transfers", 
                "🧪 Simulator", 
                "🎯 Captain & Chips"
            ])

            def render_m3_player(p, tag=""):
                badge_html = ""
                if p == captain:
                    badge_html = '<div class="m3-badge-c">C</div>'
                elif p == vice_captain:
                    badge_html = '<div class="m3-badge-vc">VC</div>'
                elif tag:
                    badge_html = f'<div class="m3-badge-sub">{tag}</div>'

                return clean_html(f"""
                <div class="m3-player-card">
                    {badge_html}
                    <div class="m3-avatar-wrap">
                        <img class="m3-avatar-img" src="{p['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{p['badge']}';">
                        <img class="m3-crest-badge" src="{p['badge']}" referrerpolicy="no-referrer">
                    </div>
                    <div class="m3-player-title">{p['data']['web_name']}</div>
                    <div><span class="m3-chip m3-chip-fdr-{p['fdr']}">{p['opp']}</span></div>
                    <div style="font-size: 10px; font-weight: 800; color: #00e676; margin-top: 2px;">{p['score']} pts</div>
                </div>
                """)

            # --- TAB 1: TACTICAL PITCH VIEW ---
            with tab_pitch:
                st.markdown(clean_html(f"""
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 6px;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #e2e2e9;">Gameweek {next_gw} Starting XI</h3>
                    <div style="font-size: 13px; color: #00e676; font-weight: 700;">Formation {best_formation}</div>
                </div>
                """), unsafe_allow_html=True)

                pitch_rows = []
                pitch_rows.append(f'<div class="m3-pitch-row">{render_m3_player(starter_gkp)}</div>')
                
                defs_html = "".join([render_m3_player(p) for p in best_starters if p["pos_id"] == 2])
                pitch_rows.append(f'<div class="m3-pitch-row">{defs_html}</div>')
                
                mids_html = "".join([render_m3_player(p) for p in best_starters if p["pos_id"] == 3])
                pitch_rows.append(f'<div class="m3-pitch-row">{mids_html}</div>')
                
                fwds_html = "".join([render_m3_player(p) for p in best_starters if p["pos_id"] == 4])
                pitch_rows.append(f'<div class="m3-pitch-row">{fwds_html}</div>')

                pitch_content = clean_html(f'<div class="m3-pitch">{"".join(pitch_rows)}</div>')
                st.markdown(pitch_content, unsafe_allow_html=True)

                bench_cards = "".join([
                    render_m3_player(bench_gkp, tag="GKP"),
                    render_m3_player(best_bench_outfield[0], tag="SUB 1"),
                    render_m3_player(best_bench_outfield[1], tag="SUB 2"),
                    render_m3_player(best_bench_outfield[2], tag="SUB 3")
                ])
                dugout_html = clean_html(f"""
                <div class="m3-dugout">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #8e919a; margin-bottom: 8px; text-align: center;">
                        🪑 Priority Bench Order
                    </div>
                    <div class="m3-pitch-row" style="margin-bottom: 0;">
                        {bench_cards}
                    </div>
                </div>
                """)
                st.markdown(dugout_html, unsafe_allow_html=True)

            # --- TAB 2: TRANSFERS ---
            with tab_transfers:
                st.markdown("### 🔄 Transfer Guidance")
                
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
                        reasons.append(f"Flagged ({chance}% chance)" if chance else "Injured / Suspended")
                    if form < 2.5:
                        urgency += 3
                        reasons.append("Low form (<2.5 pts)")
                    if fdr >= 4:
                        urgency += 2
                        reasons.append(f"Tough fixture (FDR {fdr})")

                    if urgency >= 4:
                        sell_candidates.append({"player": p_item, "urgency": urgency, "reason": ", ".join(reasons)})

                sell_candidates.sort(key=lambda x: x["urgency"], reverse=True)

                if not sell_candidates:
                    st.success("🎉 Your squad is healthy and in strong form! Roll your free transfer.")
                else:
                    for target in sell_candidates[:2]:
                        p_sell = target["player"]["data"]
                        pos_id = p_sell["element_type"]
                        sell_val = p_sell["now_cost"] / 10
                        max_budget = sell_val + bank

                        sell_card_html = clean_html(f"""
                        <div class="m3-card" style="border-left: 4px solid #ff5252; background-color: #241416;">
                            <div style="display: inline-block; background-color: #ff5252; color: #ffffff; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;">SELL PRIORITY</div>
                            <h4 style="margin: 8px 0 4px 0; color: #ffb4ab;">🔴 {p_sell['web_name']} ({positions[pos_id]}) — £{sell_val:.1f}m</h4>
                            <p style="font-size: 13px; color: #c4c6d0; margin-bottom: 6px;">Issue: <strong>{target['reason']}</strong></p>
                            <p style="font-size: 12px; color: #00e676;">Replacement Budget: <strong>£{max_budget:.1f}m</strong> (£{sell_val:.1f}m + £{bank:.1f}m bank)</p>
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
                                <div class="m3-card" style="text-align: center; border-color: rgba(0, 230, 118, 0.4);">
                                    <div style="font-size: 10px; font-weight: 700; color: #00e676;">TOP TARGET #{idx+1}</div>
                                    <div class="m3-avatar-wrap" style="margin: 8px auto; width: 56px; height: 56px;">
                                        <img class="m3-avatar-img" src="{buy_cand['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{buy_cand['badge']}';">
                                        <img class="m3-crest-badge" src="{buy_cand['badge']}" referrerpolicy="no-referrer">
                                    </div>
                                    <div style="font-weight: 700; font-size: 13px; color: #e2e2e9;">{bp['web_name']}</div>
                                    <div style="font-size: 11px; color: #8e919a;">£{bp['now_cost']/10:.1f}m | Form: {bp['form']}</div>
                                    <div style="margin-top: 4px;"><span class="m3-chip m3-chip-fdr-{buy_cand['fdr']}">{buy_cand['opp']}</span></div>
                                    <div style="margin-top: 6px; font-size: 12px; font-weight: 800; color: #00e676;">{buy_cand['score']} pts</div>
                                </div>
                                """)
                                st.markdown(buy_html, unsafe_allow_html=True)

            # --- TAB 3: SIMULATOR ---
            with tab_simulator:
                st.markdown("### 🧪 What-If Transfer Simulator")
                st.caption("Test potential trades to evaluate score impact and budget balance.")

                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    sell_names = [f"{p['data']['web_name']} ({p['pos']}) - £{p['data']['now_cost']/10:.1f}m" for p in squad_list]
                    sell_choice_idx = st.selectbox("1. Sell Player:", range(len(sell_names)), format_func=lambda x: sell_names[x])
                    selected_sell = squad_list[sell_choice_idx]
                    sell_player = selected_sell["data"]
                    sell_price = sell_player["now_cost"] / 10
                    sim_budget = sell_price + bank

                with sim_col2:
                    target_pos_id = selected_sell["pos_id"]
                    all_candidates = [
                        c for c in bootstrap["elements"] 
                        if c["element_type"] == target_pos_id and c["id"] not in squad_ids
                    ]
                    all_candidates.sort(key=lambda x: x["now_cost"], reverse=True)
                    buy_names = [f"{c['web_name']} ({teams[c['team']]['short_name']}) - £{c['now_cost']/10:.1f}m" for c in all_candidates]
                    buy_choice_idx = st.selectbox("2. Buy Replacement:", range(len(buy_names)), format_func=lambda x: buy_names[x])
                    selected_buy = all_candidates[buy_choice_idx]
                    buy_price = selected_buy["now_cost"] / 10

                buy_fdr = club_matches.get(selected_buy["team"], {}).get("fdr", 3)
                buy_potential = calculate_potential_score(selected_buy, buy_fdr)
                sell_potential = selected_sell["score"]
                delta_score = round(buy_potential - sell_potential, 2)
                new_bank = round(sim_budget - buy_price, 2)

                st.markdown("---")
                st.markdown("#### 📊 Simulation Outcome")
                
                res_col1, res_col2, res_col3 = st.columns(3)
                with res_col1:
                    if new_bank >= 0:
                        st.metric("New Bank", f"£{new_bank:.1f}m", f"£{new_bank - bank:.1f}m")
                    else:
                        st.error(f"Over budget by £{abs(new_bank):.1f}m")

                with res_col2:
                    st.metric("Expected Delta", f"{delta_score:+} pts", f"vs {sell_player['web_name']}")

                with res_col3:
                    if new_bank >= 0:
                        if delta_score > 1.5:
                            st.success("🟢 Strong Upgrade!")
                        elif delta_score >= 0:
                            st.info("🟡 Lateral Move")
                        else:
                            st.warning("🔴 Downgrade")
                    else:
                        st.warning("⚠️ Insufficient funds")

            # --- TAB 4: CAPTAINCY & CHIPS ---
            with tab_chips:
                st.markdown("### 🎯 Captaincy & Chips")
                c1, c2 = st.columns(2)
                with c1:
                    cap_html = clean_html(f"""
                    <div class="m3-card" style="border: 1.5px solid #00e676;">
                        <span class="m3-badge-c" style="position: static; font-size: 11px;">OPTIMAL CAPTAIN (2x)</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="m3-avatar-wrap" style="width: 60px; height: 60px;">
                                <img class="m3-avatar-img" src="{captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{captain['badge']}';">
                                <img class="m3-crest-badge" src="{captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #00e676; font-size: 18px;">{captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; color: #8e919a;">{captain['pos']} | {captain['opp']}</div>
                                <div style="font-size: 16px; font-weight: 800; margin-top: 4px; color: #e2e2e9;">Potential: {captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """)
                    st.markdown(cap_html, unsafe_allow_html=True)

                with c2:
                    vc_html = clean_html(f"""
                    <div class="m3-card" style="border: 1.5px solid #80d8ff;">
                        <span class="m3-badge-vc" style="position: static; font-size: 11px;">VICE-CAPTAIN</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="m3-avatar-wrap" style="width: 60px; height: 60px;">
                                <img class="m3-avatar-img" src="{vice_captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{vice_captain['badge']}';">
                                <img class="m3-crest-badge" src="{vice_captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #80d8ff; font-size: 18px;">{vice_captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; color: #8e919a;">{vice_captain['pos']} | {vice_captain['opp']}</div>
                                <div style="font-size: 16px; font-weight: 800; margin-top: 4px; color: #e2e2e9;">Potential: {vice_captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """)
                    st.markdown(vc_html, unsafe_allow_html=True)

                st.markdown("#### 🛡️ Chip Advisory")
                chip1, chip2 = st.columns(2)
                with chip1:
                    if captain["score"] >= 6.5 and captain["fdr"] == 2:
                        st.success(f"🔥 **Triple Captain:** Viable! {captain['data']['web_name']} in peak form with an easy matchup.")
                    else:
                        st.info("🛡️ **Triple Captain:** Hold. Save for a future Double Gameweek.")
                with chip2:
                    active_bench = sum(1 for b in best_bench_outfield if b["data"]["status"] == "a" and float(b["data"].get("form", 0)) > 1.5)
                    if active_bench == 3 and bench_gkp["data"]["status"] == "a":
                        st.success("🟢 **Bench Boost:** Strong bench. All 4 bench players are active starters.")
                    else:
                        st.info(f"🛡️ **Bench Boost:** Hold. {active_bench}/3 outfield bench players are active starters.")

        except Exception as e:
            st.error(f"Error loading squad: {e}")

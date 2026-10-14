import streamlit as st
import json
import urllib.request

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="FPL Elite Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PASSWORD AUTHENTICATION VIA SECRETS ---
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme123") if hasattr(st, "secrets") else "changeme123"
DEFAULT_TEAM_ID = int(st.secrets.get("DEFAULT_TEAM_ID", 1)) if hasattr(st, "secrets") else 1

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0b0712 0%, #170d24 50%, #0d0617 100%);
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 32px 24px;
            max-width: 400px;
            margin: 80px auto 20px auto;
            text-align: center;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
        }
    </style>
    <div class="login-box">
        <div style="font-size: 42px; margin-bottom: 8px;">⚽</div>
        <h2 style="color: #00ff87; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.5px;">FPL ELITE</h2>
        <p style="font-size: 14px; opacity: 0.75; margin-bottom: 24px;">Enter your passcode to access your dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        pwd_input = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Enter passcode")
        if st.button("Unlock Dashboard", type="primary", use_container_width=True):
            if pwd_input == str(APP_PASSWORD):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect passcode. Please try again.")
    st.stop()


# --- MODERN STYLING: TACTICAL PITCH & POLISHED CARDS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #090610 0%, #12091e 50%, #0a0412 100%);
        color: #ffffff;
    }
    
    /* Top stats container */
    .hero-stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    /* THE FOOTBALL PITCH */
    .pitch-container {
        background: radial-gradient(circle at center, #1b3826 0%, #112519 70%, #0a1810 100%);
        border: 2px solid rgba(0, 255, 135, 0.25);
        border-radius: 20px;
        padding: 24px 12px;
        margin: 16px 0;
        position: relative;
        box-shadow: inset 0 0 60px rgba(0,0,0,0.6), 0 10px 30px rgba(0,0,0,0.4);
        overflow: hidden;
    }
    
    .pitch-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }
    
    /* Pitch Player Card */
    .pitch-player {
        background: rgba(14, 10, 22, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 12px;
        padding: 8px 6px 6px 6px;
        text-align: center;
        width: 86px;
        min-width: 86px;
        backdrop-filter: blur(8px);
        position: relative;
        transition: transform 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    .pitch-player:hover {
        transform: translateY(-3px);
        border-color: #00ff87;
    }
    
    .player-photo-wrap {
        width: 58px;
        height: 58px;
        margin: 0 auto;
        position: relative;
    }
    .player-photo-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        background: rgba(255,255,255,0.06);
        border: 1.5px solid rgba(255, 255, 255, 0.2);
    }
    .player-badge-img {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: rgba(0,0,0,0.8);
        padding: 1px;
    }
    
    .pitch-player-name {
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 5px;
        color: #ffffff;
    }
    .pitch-player-pts {
        font-size: 10px;
        font-weight: 800;
        color: #00ff87;
        margin-top: 1px;
    }
    
    /* Badges */
    .tag-c {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #00ff87;
        color: #080312;
        font-size: 9px;
        font-weight: 900;
        padding: 2px 5px;
        border-radius: 5px;
        box-shadow: 0 2px 6px rgba(0,255,135,0.4);
    }
    .tag-vc {
        position: absolute;
        top: -6px;
        right: -6px;
        background: #00e5ff;
        color: #080312;
        font-size: 9px;
        font-weight: 900;
        padding: 2px 5px;
        border-radius: 5px;
    }
    .tag-sub {
        position: absolute;
        top: -6px;
        left: -6px;
        background: rgba(255,255,255,0.18);
        color: #fff;
        font-size: 8px;
        font-weight: 700;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    .fdr-pill {
        display: inline-block;
        font-size: 9px;
        font-weight: 700;
        padding: 1px 5px;
        border-radius: 4px;
        margin-top: 3px;
    }
    .fdr-pill-2 { background: #01fc7a; color: #000; }
    .fdr-pill-3 { background: #e0e0e0; color: #000; }
    .fdr-pill-4 { background: #ff2882; color: #fff; }
    .fdr-pill-5 { background: #80072d; color: #fff; }
    
    /* Bench Dugout */
    .bench-dugout {
        background: rgba(18, 12, 28, 0.9);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        padding: 14px 10px;
        margin-top: 14px;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

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

# --- HEADER BAR ---
col_head, col_logout = st.columns([5, 1])
with col_head:
    st.markdown("""
        <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #00ff87; letter-spacing: -0.5px;">⚽ FPL ELITE MANAGER</h1>
        <p style="margin: 2px 0 0 0; opacity: 0.75; font-size: 13px;">Tactical Lineup Optimizer, Transfer Advisor & What-If Simulator</p>
    """, unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("Log out"):
        st.session_state["authenticated"] = False
        st.rerun()

# Controls row
col_input, col_action = st.columns([3, 1])
with col_input:
    team_id = st.number_input("FPL Team ID", min_value=1, value=DEFAULT_TEAM_ID, step=1, label_visibility="collapsed")
with col_action:
    refresh_click = st.button("🔄 Refresh", use_container_width=True, type="primary")

if team_id:
    with st.spinner("Analyzing Gameweek data..."):
        try:
            # 1. Fetch core FPL metadata
            bootstrap = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
            elements = {p["id"]: p for p in bootstrap["elements"]}
            teams = {t["id"]: t for t in bootstrap["teams"]}
            positions = {pos["id"]: pos["singular_name_short"] for pos in bootstrap["element_types"]}

            # Gameweek tracking
            current_gw, next_gw = 1, 2
            for event in bootstrap["events"]:
                if event["is_current"]:
                    current_gw = event["id"]
                if event["is_next"]:
                    next_gw = event["id"]

            # Fixtures mapping
            fixtures = fetch_json(f"https://fantasy.premierleague.com/api/fixtures/?event={next_gw}")
            club_matches = {}
            for fix in fixtures:
                h, a = fix["team_h"], fix["team_a"]
                club_matches[h] = {"opp": f"vs {teams[a]['short_name']} (H)", "fdr": fix["team_h_difficulty"]}
                club_matches[a] = {"opp": f"@ {teams[h]['short_name']} (A)", "fdr": fix["team_a_difficulty"]}

            # User data
            entry_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/")
            picks_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{current_gw}/picks/")
            
            squad_ids = {p["element"] for p in picks_data["picks"]}
            bank = picks_data.get("entry_history", {}).get("bank", 0) / 10

            # --- SQUAD STATS BAR ---
            st.markdown(f"""
            <div class="hero-stat-card">
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; gap: 12px;">
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; opacity: 0.6; font-weight: 700;">Manager</div>
                        <div style="font-size: 16px; font-weight: 700;">{entry_data['player_first_name']} {entry_data['player_last_name']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; opacity: 0.6; font-weight: 700;">Team</div>
                        <div style="font-size: 16px; font-weight: 700; color: #00ff87;">{entry_data['name']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; opacity: 0.6; font-weight: 700;">Points</div>
                        <div style="font-size: 20px; font-weight: 800; color: #ffffff;">{entry_data['summary_overall_points']}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; opacity: 0.6; font-weight: 700;">In Bank</div>
                        <div style="font-size: 20px; font-weight: 800; color: #00ff87;">£{bank:.1f}m</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Build enriched player squad list
            squad_list = []
            for pick in picks_data["picks"]:
                p = elements[pick["element"]]
                fdr = club_matches.get(p["team"], {}).get("fdr", 3)
                opp = club_matches.get(p["team"], {}).get("opp", "TBD")
                score = calculate_potential_score(p, fdr)
                
                # Clean photo & badge code
                photo_code = str(p.get("code", "")).replace(".jpg", "").replace("p", "")
                team_code = teams[p["team"]]["code"]
                
                photo_url = f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{photo_code}.png"
                badge_url = f"https://resources.premierleague.com/premierleague/badges/70/t{team_code}.png"
                fallback_avatar = f"https://ui-avatars.com/api/?name={p['web_name']}&background=26143d&color=00ff87&size=128"

                squad_list.append({
                    "data": p,
                    "fdr": fdr,
                    "opp": opp,
                    "score": score,
                    "pos_id": p["element_type"],
                    "pos": positions[p["element_type"]],
                    "photo": photo_url,
                    "badge": badge_url,
                    "fallback": fallback_avatar
                })

            # --- FORMATION SOLVER ---
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

            # --- TABS NAVIGATION ---
            tab_pitch, tab_transfers, tab_simulator, tab_chips = st.tabs([
                "🏟️ Tactical Pitch", 
                "🔄 Transfers", 
                "🧪 Simulator", 
                "🎯 Captain & Chips"
            ])

            def render_pitch_card(p, tag=""):
                badge_html = ""
                if p == captain:
                    badge_html = '<div class="tag-c">C</div>'
                elif p == vice_captain:
                    badge_html = '<div class="tag-vc">VC</div>'
                elif tag:
                    badge_html = f'<div class="tag-sub">{tag}</div>'

                return f"""
                <div class="pitch-player">
                    {badge_html}
                    <div class="player-photo-wrap">
                        <img class="player-photo-img" src="{p['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{p['fallback']}';">
                        <img class="player-badge-img" src="{p['badge']}" referrerpolicy="no-referrer">
                    </div>
                    <div class="pitch-player-name">{p['data']['web_name']}</div>
                    <div><span class="fdr-pill fdr-pill-{p['fdr']}">{p['opp']}</span></div>
                    <div class="pitch-player-pts">{p['score']} pts</div>
                </div>
                """

            # --- TAB 1: TACTICAL PITCH VIEW ---
            with tab_pitch:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: 800;">⭐ Gameweek {next_gw} Starting XI</h3>
                    <div style="font-size: 13px; color: #00ff87; font-weight: 700;">Formation: {best_formation}</div>
                </div>
                """, unsafe_allow_html=True)

                # RENDER PITCH
                pitch_html = '<div class="pitch-container">'
                
                # GKP
                pitch_html += '<div class="pitch-row">' + render_pitch_card(starter_gkp) + '</div>'
                
                # DEFs
                pitch_html += '<div class="pitch-row">'
                for p in [x for x in best_starters if x["pos_id"] == 2]:
                    pitch_html += render_pitch_card(p)
                pitch_html += '</div>'

                # MIDs
                pitch_html += '<div class="pitch-row">'
                for p in [x for x in best_starters if x["pos_id"] == 3]:
                    pitch_html += render_pitch_card(p)
                pitch_html += '</div>'

                # FWDs
                pitch_html += '<div class="pitch-row">'
                for p in [x for x in best_starters if x["pos_id"] == 4]:
                    pitch_html += render_pitch_card(p)
                pitch_html += '</div>'

                pitch_html += '</div>'
                st.markdown(pitch_html, unsafe_allow_html=True)

                # BENCH DUGOUT
                bench_html = f"""
                <div class="bench-dugout">
                    <div style="font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.7; margin-bottom: 10px; text-align: center;">
                        🪑 Priority Bench Order
                    </div>
                    <div class="pitch-row" style="margin-bottom: 0;">
                        {render_pitch_card(bench_gkp, tag="GKP")}
                        {render_pitch_card(best_bench_outfield[0], tag="SUB 1")}
                        {render_pitch_card(best_bench_outfield[1], tag="SUB 2")}
                        {render_pitch_card(best_bench_outfield[2], tag="SUB 3")}
                    </div>
                </div>
                """
                st.markdown(bench_html, unsafe_allow_html=True)

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
                        reasons.append("Low form")
                    if fdr >= 4:
                        urgency += 2
                        reasons.append(f"Tough fixture (FDR {fdr})")

                    if urgency >= 4:
                        sell_candidates.append({"player": p_item, "urgency": urgency, "reason": ", ".join(reasons)})

                sell_candidates.sort(key=lambda x: x["urgency"], reverse=True)

                if not sell_candidates:
                    st.success("🎉 Your squad is healthy and in good form! Roll your free transfer.")
                else:
                    for target in sell_candidates[:2]:
                        p_sell = target["player"]["data"]
                        pos_id = p_sell["element_type"]
                        sell_val = p_sell["now_cost"] / 10
                        max_budget = sell_val + bank

                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 4px solid #ff2882;">
                            <span style="background: #ff2882; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800;">SELL RECOMMENDATION</span>
                            <h4 style="margin: 8px 0 4px 0;">🔴 {p_sell['web_name']} ({positions[pos_id]}) — £{sell_val:.1f}m</h4>
                            <p style="font-size: 13px; opacity: 0.8; margin-bottom: 6px;">Issue: <strong>{target['reason']}</strong></p>
                            <p style="font-size: 12px; color: #00ff87;">Max Buy Budget: <strong>£{max_budget:.1f}m</strong> (£{sell_val:.1f}m + £{bank:.1f}m in bank)</p>
                        </div>
                        """, unsafe_allow_html=True)

                        pool = []
                        for cand in bootstrap["elements"]:
                            if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                                cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                                c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                                pot = calculate_potential_score(cand, c_fdr)
                                cand_photo_code = str(cand.get("code", "")).replace(".jpg", "").replace("p", "")
                                pool.append({
                                    "data": cand,
                                    "score": pot,
                                    "fdr": c_fdr,
                                    "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                                    "photo": f"https://resources.premierleague.com/premierleague/photos/players/250x250/p{cand_photo_code}.png",
                                    "badge": f"https://resources.premierleague.com/premierleague/badges/70/t{teams[cand['team']]['code']}.png",
                                    "fallback": f"https://ui-avatars.com/api/?name={cand['web_name']}&background=26143d&color=00ff87&size=128"
                                })

                        pool.sort(key=lambda x: x["score"], reverse=True)
                        cols_buy = st.columns(min(3, len(pool)))
                        for idx, buy_cand in enumerate(pool[:3]):
                            with cols_buy[idx]:
                                bp = buy_cand["data"]
                                st.markdown(f"""
                                <div class="glass-card" style="text-align: center; border-color: #00ff87;">
                                    <div style="font-size: 10px; font-weight: 800; color: #00ff87;">TARGET #{idx+1}</div>
                                    <div class="player-photo-wrap" style="margin: 8px auto;">
                                        <img class="player-photo-img" src="{buy_cand['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{buy_cand['fallback']}';">
                                        <img class="player-badge-img" src="{buy_cand['badge']}" referrerpolicy="no-referrer">
                                    </div>
                                    <div style="font-weight: 700; font-size: 13px;">{bp['web_name']}</div>
                                    <div style="font-size: 11px; opacity: 0.8;">£{bp['now_cost']/10:.1f}m | Form: {bp['form']}</div>
                                    <div style="margin-top: 4px;"><span class="fdr-pill fdr-pill-{buy_cand['fdr']}">{buy_cand['opp']}</span></div>
                                    <div style="margin-top: 6px; font-size: 12px; font-weight: 800; color: #00ff87;">{buy_cand['score']} pts</div>
                                </div>
                                """, unsafe_allow_html=True)

            # --- TAB 3: SIMULATOR ---
            with tab_simulator:
                st.markdown("### 🧪 What-If Transfer Simulator")
                st.caption("Test trades to see budget changes and expected score impact.")

                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    sell_names = [f"{p['data']['web_name']} ({p['pos']}) - £{p['data']['now_cost']/10:.1f}m" for p in squad_list]
                    sell_choice_idx = st.selectbox("Sell Player:", range(len(sell_names)), format_func=lambda x: sell_names[x])
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
                    buy_choice_idx = st.selectbox("Buy Replacement:", range(len(buy_names)), format_func=lambda x: buy_names[x])
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
                    st.markdown(f"""
                    <div class="glass-card" style="border: 2px solid #00ff87;">
                        <span class="tag-c" style="position: static; font-size: 11px;">OPTIMAL CAPTAIN (2x)</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="player-photo-wrap" style="width: 64px; height: 64px;">
                                <img class="player-photo-img" src="{captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{captain['fallback']}';">
                                <img class="player-badge-img" src="{captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #00ff87;">{captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; opacity: 0.8;">{captain['pos']} | {captain['opp']}</div>
                                <div style="font-size: 16px; font-weight: 800; margin-top: 4px;">Potential: {captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="glass-card" style="border: 2px solid #00e5ff;">
                        <span class="tag-vc" style="position: static; font-size: 11px;">VICE-CAPTAIN</span>
                        <div style="display: flex; align-items: center; margin-top: 10px; gap: 14px;">
                            <div class="player-photo-wrap" style="width: 64px; height: 64px;">
                                <img class="player-photo-img" src="{vice_captain['photo']}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='{vice_captain['fallback']}';">
                                <img class="player-badge-img" src="{vice_captain['badge']}" referrerpolicy="no-referrer">
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #00e5ff;">{vice_captain['data']['web_name']}</h3>
                                <div style="font-size: 12px; opacity: 0.8;">{vice_captain['pos']} | {vice_captain['opp']}</div>
                                <div style="font-size: 16px; font-weight: 800; margin-top: 4px;">Potential: {vice_captain['score']} pts</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

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

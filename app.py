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

# --- MODERN PREMIER LEAGUE STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global background and text */
    .stApp {
        background: linear-gradient(135deg, #180022 0%, #290838 50%, #15001f 100%);
        color: #ffffff;
    }
    
    /* Modern card container */
    .fpl-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Player card layout */
    .player-card {
        background: rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
        text-align: center;
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
    .player-card:hover {
        transform: translateY(-2px);
        border-color: #00ff87;
    }
    
    /* Badges */
    .badge-c {
        background: #00ff87;
        color: #180022;
        font-weight: 800;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-vc {
        background: #04f5ff;
        color: #180022;
        font-weight: 800;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 6px;
        display: inline-block;
    }
    .fdr-badge {
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        color: #ffffff;
    }
    .fdr-2 { background-color: #01fc7a; color: #000; }
    .fdr-3 { background-color: #e7e7e7; color: #000; }
    .fdr-4 { background-color: #ff1751; color: #fff; }
    .fdr-5 { background-color: #80072d; color: #fff; }
    
    /* Metrics highlight */
    .metric-value {
        font-size: 24px;
        font-weight: 800;
        color: #00ff87;
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        opacity: 0.7;
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

# --- HEADER SECTION ---
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
    <div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #00ff87;">⚽ FPL ELITE MANAGER</h1>
        <p style="margin: 0; opacity: 0.8; font-size: 14px;">Tactical Lineup Optimizer, Transfer Engine & What-If Simulator</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Bar Input
col_input, col_action = st.columns([3, 1])
with col_input:
    team_id = st.number_input("Fantasy Premier League Team ID", min_value=1, value=1, step=1)
with col_action:
    st.write("")
    st.write("")
    analyze_click = st.button("⚡ Analyze Squad", use_container_width=True, type="primary")

if team_id:
    with st.spinner("Analyzing live Premier League data..."):
        try:
            # 1. Fetch core data
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
                club_matches[h] = {"opp": f"vs {teams[a]['short_name']} (H)", "fdr": fix["team_h_difficulty"], "opp_id": a}
                club_matches[a] = {"opp": f"@ {teams[h]['short_name']} (A)", "fdr": fix["team_a_difficulty"], "opp_id": h}

            # Team and picks data
            entry_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/")
            picks_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{current_gw}/picks/")
            
            squad_ids = {p["element"] for p in picks_data["picks"]}
            bank = picks_data.get("entry_history", {}).get("bank", 0) / 10

            # --- SQUAD STATS BAR ---
            st.markdown(f"""
            <div class="fpl-card">
                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;">
                    <div style="min-width: 120px;">
                        <div class="metric-label">Manager</div>
                        <div style="font-size: 18px; font-weight: 700;">{entry_data['player_first_name']} {entry_data['player_last_name']}</div>
                    </div>
                    <div style="min-width: 120px;">
                        <div class="metric-label">Team</div>
                        <div style="font-size: 18px; font-weight: 700;">{entry_data['name']}</div>
                    </div>
                    <div style="min-width: 100px;">
                        <div class="metric-label">Overall Points</div>
                        <div class="metric-value">{entry_data['summary_overall_points']}</div>
                    </div>
                    <div style="min-width: 100px;">
                        <div class="metric-label">In The Bank</div>
                        <div class="metric-value">£{bank:.1f}m</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Build enriched player list for user's squad
            squad_list = []
            for pick in picks_data["picks"]:
                p = elements[pick["element"]]
                fdr = club_matches.get(p["team"], {}).get("fdr", 3)
                opp = club_matches.get(p["team"], {}).get("opp", "TBD")
                score = calculate_potential_score(p, fdr)
                squad_list.append({
                    "data": p,
                    "fdr": fdr,
                    "opp": opp,
                    "score": score,
                    "pos_id": p["element_type"],
                    "pos": positions[p["element_type"]],
                    "photo": f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{p['code']}.png",
                    "badge": f"https://resources.premierleague.com/premierleague/badges/50/t{teams[p['team']]['code']}.png"
                })

            # --- OPTIMAL STARTING XI FORMATION SOLVER ---
            # Separate by position
            gkps = [p for p in squad_list if p["pos_id"] == 1]
            defs = sorted([p for p in squad_list if p["pos_id"] == 2], key=lambda x: x["score"], reverse=True)
            mids = sorted([p for p in squad_list if p["pos_id"] == 3], key=lambda x: x["score"], reverse=True)
            fwds = sorted([p for p in squad_list if p["pos_id"] == 4], key=lambda x: x["score"], reverse=True)

            # Best GKP
            starter_gkp = max(gkps, key=lambda x: x["score"])
            bench_gkp = [g for g in gkps if g != starter_gkp][0]

            # Test valid formations: (def, mid, fwd)
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

            # Sort starters for Captain / Vice-Captain
            sorted_by_pot = sorted(best_starters, key=lambda x: x["score"], reverse=True)
            captain = sorted_by_pot[0]
            vice_captain = sorted_by_pot[1]

            # --- TABS FOR NAVIGATION ---
            tab_lineup, tab_transfers, tab_simulator, tab_chips = st.tabs([
                "📋 Optimal Lineup", 
                "🔄 Transfer Engine", 
                "🧪 What-If Simulator", 
                "🎯 Captain & Chips"
            ])

            # --- TAB 1: OPTIMAL LINEUP ---
            with tab_lineup:
                st.markdown(f"### ⭐ Gameweek {next_gw} Optimal Starting XI ({best_formation})")
                st.caption(f"Projected Starting XI Score: **{best_score:.1f} pts** (excluding captain 2x bonus)")

                def render_player(p, is_bench=False, sub_idx=""):
                    c_tag = ""
                    if p == captain:
                        c_tag = '<div class="badge-c">CAPTAIN (2x)</div>'
                    elif p == vice_captain:
                        c_tag = '<div class="badge-vc">VICE-CAPT</div>'
                    
                    sub_tag = f'<div style="font-size:11px; opacity:0.8; font-weight:700;">{sub_idx}</div>' if is_bench else ''
                    fdr_cls = f"fdr-{p['fdr']}"

                    return f"""
                    <div class="player-card">
                        {sub_tag}
                        <div style="position: relative; display: inline-block;">
                            <img src="{p['photo']}" style="width: 75px; height: 95px; object-fit: cover; border-radius: 8px;">
                            <img src="{p['badge']}" style="width: 24px; height: 24px; position: absolute; bottom: 0; right: 0;">
                        </div>
                        <div style="font-weight: 700; font-size: 13px; margin-top: 4px;">{p['data']['web_name']}</div>
                        <div style="font-size: 11px; opacity: 0.8;">{p['pos']} | £{p['data']['now_cost']/10:.1f}m</div>
                        <div style="margin-top: 4px;">
                            <span class="fdr-badge {fdr_cls}">{p['opp']}</span>
                        </div>
                        <div style="font-size: 12px; margin-top: 4px; font-weight: 700; color: #00ff87;">Pot: {p['score']}</div>
                        <div style="margin-top: 4px;">{c_tag}</div>
                    </div>
                    """

                # Render Starters: GKP
                st.markdown("##### Goalkeeper")
                col_gkp = st.columns(1)[0]
                with col_gkp:
                    st.markdown(render_player(starter_gkp), unsafe_allow_html=True)

                # Render Defenders
                st.markdown("##### Defenders")
                cur_defs = [p for p in best_starters if p["pos_id"] == 2]
                cols_def = st.columns(len(cur_defs))
                for idx, p in enumerate(cur_defs):
                    with cols_def[idx]:
                        st.markdown(render_player(p), unsafe_allow_html=True)

                # Render Midfielders
                st.markdown("##### Midfielders")
                cur_mids = [p for p in best_starters if p["pos_id"] == 3]
                cols_mid = st.columns(len(cur_mids))
                for idx, p in enumerate(cur_mids):
                    with cols_mid[idx]:
                        st.markdown(render_player(p), unsafe_allow_html=True)

                # Render Forwards
                st.markdown("##### Forwards")
                cur_fwds = [p for p in best_starters if p["pos_id"] == 4]
                cols_fwd = st.columns(len(cur_fwds))
                for idx, p in enumerate(cur_fwds):
                    with cols_fwd[idx]:
                        st.markdown(render_player(p), unsafe_allow_html=True)

                # Render Bench
                st.markdown("---")
                st.markdown("##### 🪑 Priority Bench Order")
                cols_bench = st.columns(4)
                with cols_bench[0]:
                    st.markdown(render_player(bench_gkp, is_bench=True, sub_idx="Sub GKP"), unsafe_allow_html=True)
                for idx, p in enumerate(best_bench_outfield):
                    with cols_bench[idx + 1]:
                        st.markdown(render_player(p, is_bench=True, sub_idx=f"Sub {idx + 1}"), unsafe_allow_html=True)

            # --- TAB 2: TRANSFER RECOMMENDATIONS ---
            with tab_transfers:
                st.markdown("### 🔄 Smart Transfer Guidance")
                
                # Identify Sell Candidates
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
                        reasons.append("Cold Form (<2.5 pts)")
                    if fdr >= 4:
                        urgency += 2
                        reasons.append(f"Tough Fixture (FDR {fdr})")

                    if urgency >= 4:
                        sell_candidates.append({"player": p_item, "urgency": urgency, "reason": ", ".join(reasons)})

                sell_candidates.sort(key=lambda x: x["urgency"], reverse=True)

                if not sell_candidates:
                    st.success("🎉 Your squad is in peak condition! No urgent transfers needed. Save your free transfer.")
                else:
                    for target in sell_candidates[:2]:
                        p_sell = target["player"]["data"]
                        pos_id = p_sell["element_type"]
                        sell_val = p_sell["now_cost"] / 10
                        max_budget = sell_val + bank

                        st.markdown(f"""
                        <div class="fpl-card" style="border-left: 4px solid #ff1751;">
                            <span style="background: #ff1751; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">SELL PRIORITY</span>
                            <h4 style="margin: 8px 0 4px 0;">🔴 {p_sell['web_name']} ({positions[pos_id]}) — £{sell_val:.1f}m</h4>
                            <p style="font-size: 13px; opacity: 0.8; margin-bottom: 6px;">Reason: <strong>{target['reason']}</strong></p>
                            <p style="font-size: 12px; color: #00ff87;">Available Replacement Budget: <strong>£{max_budget:.1f}m</strong> (£{sell_val:.1f}m + £{bank:.1f}m in bank)</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Find best replacements
                        pool = []
                        for cand in bootstrap["elements"]:
                            if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                                cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                                c_fdr = club_matches.get(cand["team"], {}).get("fdr", 3)
                                pot = calculate_potential_score(cand, c_fdr)
                                pool.append({
                                    "data": cand,
                                    "score": pot,
                                    "fdr": c_fdr,
                                    "opp": club_matches.get(cand["team"], {}).get("opp", "TBD"),
                                    "badge": f"https://resources.premierleague.com/premierleague/badges/50/t{teams[cand['team']]['code']}.png",
                                    "photo": f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{cand['code']}.png"
                                })

                        pool.sort(key=lambda x: x["score"], reverse=True)
                        cols_buy = st.columns(min(3, len(pool)))
                        for idx, buy_cand in enumerate(pool[:3]):
                            with cols_buy[idx]:
                                bp = buy_cand["data"]
                                st.markdown(f"""
                                <div class="player-card" style="border: 1px solid #00ff87;">
                                    <div style="font-size: 11px; font-weight: 800; color: #00ff87;">TOP TARGET #{idx+1}</div>
                                    <img src="{buy_cand['photo']}" style="width: 65px; height: 80px; object-fit: cover; border-radius: 6px; margin: 4px 0;">
                                    <div style="font-weight: 700; font-size: 13px;">{bp['web_name']}</div>
                                    <div style="font-size: 11px; opacity: 0.8;">£{bp['now_cost']/10:.1f}m | Form: {bp['form']}</div>
                                    <div style="margin-top: 4px;"><span class="fdr-badge fdr-{buy_cand['fdr']}">{buy_cand['opp']}</span></div>
                                    <div style="margin-top: 6px; font-size: 12px; font-weight: 800; color: #00ff87;">Pot: {buy_cand['score']}</div>
                                </div>
                                """, unsafe_allow_html=True)

            # --- TAB 3: WHAT-IF TRANSFER SIMULATOR ---
            with tab_simulator:
                st.markdown("### 🧪 What-If Transfer Simulator")
                st.caption("Test potential transfers and see your net point delta and remaining bank balance in real time.")

                sim_col1, sim_col2 = st.columns(2)
                
                with sim_col1:
                    # Player to sell dropdown
                    sell_names = [f"{p['data']['web_name']} ({p['pos']}) - £{p['data']['now_cost']/10:.1f}m" for p in squad_list]
                    sell_choice_idx = st.selectbox("1. Choose a player from your squad to SELL:", range(len(sell_names)), format_func=lambda x: sell_names[x])
                    selected_sell = squad_list[sell_choice_idx]
                    sell_player = selected_sell["data"]
                    sell_price = sell_player["now_cost"] / 10
                    sim_budget = sell_price + bank

                with sim_col2:
                    # Filter candidates of the same position within budget
                    target_pos_id = selected_sell["pos_id"]
                    all_candidates = [
                        c for c in bootstrap["elements"] 
                        if c["element_type"] == target_pos_id and c["id"] not in squad_ids
                    ]
                    # Sort candidates by price descending
                    all_candidates.sort(key=lambda x: x["now_cost"], reverse=True)
                    buy_names = [f"{c['web_name']} ({teams[c['team']]['short_name']}) - £{c['now_cost']/10:.1f}m" for c in all_candidates]
                    
                    buy_choice_idx = st.selectbox("2. Choose a replacement to BUY:", range(len(buy_names)), format_func=lambda x: buy_names[x])
                    selected_buy = all_candidates[buy_choice_idx]
                    buy_price = selected_buy["now_cost"] / 10

                # Calculate Trade Delta
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
                        st.metric("New Bank Balance", f"£{new_bank:.1f}m", f"£{new_bank - bank:.1f}m")
                    else:
                        st.error(f"❌ Over Budget by £{abs(new_bank):.1f}m")

                with res_col2:
                    delta_color = "normal" if delta_score >= 0 else "inverse"
                    st.metric("Expected Return Delta", f"{delta_score:+} pts", f"{delta_score} vs {sell_player['web_name']}")

                with res_col3:
                    if new_bank >= 0:
                        if delta_score > 1.5:
                            st.success("🟢 Strong Upgrade! Recommended.")
                        elif delta_score >= 0:
                            st.info("🟡 Lateral move. Roll transfer if not urgent.")
                        else:
                            st.warning("🔴 Downgrade in immediate potential.")
                    else:
                        st.warning("⚠️ Insufficient funds.")

            # --- TAB 4: CAPTAINCY & CHIPS ---
            with tab_chips:
                st.markdown("### 🎯 Captaincy & Chip Strategy")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="fpl-card" style="border: 2px solid #00ff87;">
                        <span class="badge-c">OPTIMAL CAPTAIN (2x)</span>
                        <div style="display: flex; align-items: center; margin-top: 10px;">
                            <img src="{captain['photo']}" style="width: 70px; height: 90px; object-fit: cover; border-radius: 8px; margin-right: 15px;">
                            <div>
                                <h3 style="margin: 0; color: #00ff87;">{captain['data']['web_name']}</h3>
                                <div style="font-size: 13px; opacity: 0.8;">{captain['pos']} | {captain['opp']}</div>
                                <div style="font-size: 18px; font-weight: 800; margin-top: 6px;">Potential: {captain['score']} / 10</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="fpl-card" style="border: 2px solid #04f5ff;">
                        <span class="badge-vc">VICE-CAPTAIN BACKUP</span>
                        <div style="display: flex; align-items: center; margin-top: 10px;">
                            <img src="{vice_captain['photo']}" style="width: 70px; height: 90px; object-fit: cover; border-radius: 8px; margin-right: 15px;">
                            <div>
                                <h3 style="margin: 0; color: #04f5ff;">{vice_captain['data']['web_name']}</h3>
                                <div style="font-size: 13px; opacity: 0.8;">{vice_captain['pos']} | {vice_captain['opp']}</div>
                                <div style="font-size: 18px; font-weight: 800; margin-top: 6px;">Potential: {vice_captain['score']} / 10</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Chip viability
                st.markdown("#### 🛡️ Chip Advisory")
                chip1, chip2 = st.columns(2)
                with chip1:
                    if captain["score"] >= 6.5 and captain["fdr"] == 2:
                        st.success(f"🔥 **Triple Captain:** VIABLE! {captain['data']['web_name']} faces an FDR 2 matchup in top form.")
                    else:
                        st.info("🛡️ **Triple Captain:** SAVE. Hold for a future Double Gameweek.")
                with chip2:
                    active_bench = sum(1 for b in best_bench_outfield if b["data"]["status"] == "a" and float(b["data"].get("form", 0)) > 1.5)
                    if active_bench == 3 and bench_gkp["data"]["status"] == "a":
                        st.success("🟢 **Bench Boost:** STRONG BENCH. All 4 bench players are active starters.")
                    else:
                        st.info(f"🛡️ **Bench Boost:** SAVE. Your bench has {active_bench}/3 active outfield starters.")

        except Exception as e:
            st.error(f"Error loading FPL squad: {e}")

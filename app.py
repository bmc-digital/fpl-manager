import streamlit as st
import json
import urllib.request

# Page configuration for mobile responsiveness
st.set_page_config(page_title="FPL Assistant", page_icon="⚽", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0"}

@st.cache_data(ttl=600)  # Caches FPL data for 10 minutes so your app stays fast
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

# --- APP HEADER & INPUTS ---
st.title("⚽ FPL Squad Manager & Advisor")
st.caption("Maximize your gameweek score with data-driven transfers, captaincy, and chips.")

# Mobile input field for your Team ID
col_input, col_btn = st.columns([3, 1])
with col_input:
    team_id = st.number_input("Enter your FPL Team ID:", min_value=1, value=1, step=1)
with col_btn:
    st.write("") # spacing
    st.write("")
    analyze_btn = st.button("Analyze Squad", type="primary")

if analyze_btn or team_id:
    with st.spinner("Fetching latest Premier League data..."):
        try:
            bootstrap = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
            elements = {p["id"]: p for p in bootstrap["elements"]}
            teams = {t["id"]: t for t in bootstrap["teams"]}
            positions = {pos["id"]: pos["singular_name_short"] for pos in bootstrap["element_types"]}

            current_gw = 1
            next_gw = 2
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
            squad_ids = {pick["element"] for pick in picks_data["picks"]}
            bank = picks_data.get("entry_history", {}).get("bank", 0) / 10

            # 1. TEAM OVERVIEW METRICS
            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Manager", f"{entry_data['player_first_name']} {entry_data['player_last_name']}")
            m2.metric("Team", entry_data["name"])
            m3.metric("Total Points", entry_data["summary_overall_points"])
            m4.metric("In The Bank", f"£{bank:.1f}m")

            # Parse squad
            starters = []
            bench = []
            club_counts = {}
            for pick in picks_data["picks"]:
                p = elements[pick["element"]]
                fdr = club_matches.get(p["team"], {}).get("fdr", 3)
                opp = club_matches.get(p["team"], {}).get("opp", "TBD")
                pot = calculate_potential_score(p, fdr)
                item = {"player": p, "fdr": fdr, "opp": opp, "potential_score": pot, "position": pick["position"]}
                if pick["position"] <= 11:
                    starters.append(item)
                else:
                    bench.append(item)
                
                c_id = p["team"]
                club_counts[c_id] = club_counts.get(c_id, 0) + 1

            # 2. CAPTAINCY & CHIPS SECTION
            st.subheader("⭐ Captaincy & Chip Advisory")
            ranked_starters = sorted(starters, key=lambda x: x["potential_score"], reverse=True)
            capt = ranked_starters[0]
            v_capt = ranked_starters[1]

            cap_col1, cap_col2 = st.columns(2)
            with cap_col1:
                st.success(f"**Captain (2x Pts):** {capt['player']['web_name']}\n\n"
                           f"Match: {capt['opp']} (FDR {capt['fdr']}) | Potential: **{capt['potential_score']}**")
            with cap_col2:
                st.info(f"**Vice-Captain:** {v_capt['player']['web_name']}\n\n"
                        f"Match: {v_capt['opp']} (FDR {v_capt['fdr']}) | Potential: **{v_capt['potential_score']}**")

            # Chip advice
            chip_col1, chip_col2 = st.columns(2)
            with chip_col1:
                if capt["potential_score"] >= 6.5 and capt["fdr"] == 2:
                    st.warning(f"🔥 **Triple Captain:** Viable! {capt['player']['web_name']} has top form and an FDR 2 fixture.")
                else:
                    st.write("🛡️ **Triple Captain:** Save for a future double gameweek.")
            with chip_col2:
                active_bench = sum(1 for b in bench if b["player"]["status"] == "a" and float(b["player"].get("form", 0)) > 1.5)
                if active_bench == 4:
                    st.success("🟢 **Bench Boost:** All 4 bench players are healthy and active.")
                else:
                    st.write(f"🛡️ **Bench Boost:** Save. Only {active_bench}/4 bench players are consistent starters.")

            # 3. TRANSFER RECOMMENDATIONS
            st.subheader("🔄 Transfer Recommendations")
            sell_candidates = []
            for entry in starters + bench:
                p = entry["player"]
                fdr = entry["fdr"]
                form = float(p.get("form", 0.0))
                urgency = 0
                reasons = []

                if p["status"] != "a":
                    chance = p.get("chance_of_playing_next_round")
                    urgency += 10 if (chance is not None and chance <= 25) else 6
                    reasons.append(f"Flagged ({chance}% play)" if chance else "Injured/Out")
                if form < 2.5:
                    urgency += 3
                    reasons.append("Low form")
                if fdr >= 4:
                    urgency += 2
                    reasons.append(f"Tough fixture (FDR {fdr})")

                if urgency >= 4:
                    sell_candidates.append({"player": p, "urgency": urgency, "reason": ", ".join(reasons)})

            sell_candidates.sort(key=lambda x: x["urgency"], reverse=True)

            if len(sell_candidates) >= 4:
                st.error("🚨 **Wildcard Alert:** 4+ squad members are injured or out of form. Consider playing your Wildcard!")

            if not sell_candidates:
                st.success("Your team looks solid! Roll your free transfer to bank two transfers next week.")
            else:
                for target in sell_candidates[:2]:
                    p_sell = target["player"]
                    pos_id = p_sell["element_type"]
                    sell_price = p_sell["now_cost"] / 10
                    max_budget = sell_price + bank

                    with st.expander(f"🔴 Sell Candidate: {p_sell['web_name']} ({positions[pos_id]}) — {target['reason']}", expanded=True):
                        st.write(f"Selling frees up: **£{sell_price:.1f}m** | Available Budget: **£{max_budget:.1f}m**")
                        
                        pool = []
                        for cand in bootstrap["elements"]:
                            if (cand["element_type"] == pos_id and cand["status"] == "a" and 
                                cand["id"] not in squad_ids and (cand["now_cost"] / 10) <= max_budget):
                                c_club = cand["team"]
                                count = club_counts.get(c_club, 0) - (1 if c_club == p_sell["team"] else 0)
                                if count < 3:
                                    c_fdr = club_matches.get(c_club, {}).get("fdr", 3)
                                    score = calculate_potential_score(cand, c_fdr)
                                    pool.append({"player": cand, "score": score, "fdr": c_fdr})

                        pool.sort(key=lambda x: x["score"], reverse=True)
                        st.markdown("**Top Replacements to Buy:**")
                        for idx, item in enumerate(pool[:3], start=1):
                            c = item["player"]
                            opp_info = club_matches.get(c["team"], {"opp": "TBD"})
                            st.markdown(f"{idx}. **{c['web_name']}** (£{c['now_cost']/10:.1f}m) — Form: {c['form']} | Next: {opp_info['opp']} (FDR {item['fdr']}) | **Potential: {item['score']}**")

        except Exception as e:
            st.error(f"Could not load team data: {e}")

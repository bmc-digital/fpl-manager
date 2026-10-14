import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & DARK THEME CSS INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kings County FC | FPL Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FPL_CUSTOM_CSS = """
<style>
    /* Main Dark Background & Card Containers */
    .stApp { background-color: #0E1117; color: #F0F6FC; }
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 14px 18px;
    }
    /* Tactical Pitch Container */
    .fpl-pitch {
        background: linear-gradient(180deg, #064E3B 0%, #047857 50%, #065F46 100%);
        border: 1.5px solid rgba(16, 185, 129, 0.35);
        border-radius: 16px;
        padding: 24px 16px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    .pitch-row {
        display: flex;
        justify-content: space-evenly;
        align-items: center;
        margin-bottom: 22px;
        flex-wrap: wrap;
        gap: 10px;
    }
    /* Glassmorphic Player Card */
    .p-card {
        width: 112px;
        background: rgba(15, 23, 42, 0.88);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 8px 6px 6px 6px;
        text-align: center;
        color: #fff;
        font-family: 'Inter', sans-serif;
        position: relative;
        transition: transform 0.18s ease, border-color 0.18s ease;
    }
    .p-card:hover { transform: translateY(-4px); border-color: #10B981; }
    .p-name { font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 4px; }
    .p-meta { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94A3B8; }
    .p-xp {
        margin-top: 4px;
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34D399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        border-radius: 6px;
        padding: 2px 4px;
    }
    .cap-badge {
        position: absolute; top: 6px; left: 6px;
        background: #F59E0B; color: #090C10;
        font-weight: 800; font-size: 10px;
        width: 18px; height: 18px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
    }
</style>
"""
st.markdown(FPL_CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SQUAD DATA MODEL (15 PLAYERS)
# -----------------------------------------------------------------------------
SQUAD = [
    {"name": "Raya", "pos": "GKP", "team": "ARS", "price": 5.6, "opp": "BOU (A)", "fdr": 2, "xp": 5.2, "starter": True, "cap": None, "color": "#EF4444"},
    {"name": "Gabriel", "pos": "DEF", "team": "ARS", "price": 6.2, "opp": "BOU (A)", "fdr": 2, "xp": 5.8, "starter": True, "cap": None, "color": "#EF4444"},
    {"name": "Gvardiol", "pos": "DEF", "team": "MCI", "price": 6.0, "opp": "WOL (A)", "fdr": 2, "xp": 5.6, "starter": True, "cap": None, "color": "#38BDF8"},
    {"name": "Alexander-Arnold", "pos": "DEF", "team": "LIV", "price": 7.1, "opp": "CHE (H)", "fdr": 4, "xp": 5.1, "starter": True, "cap": None, "color": "#DC2626"},
    {"name": "Salah", "pos": "MID", "team": "LIV", "price": 12.8, "opp": "CHE (H)", "fdr": 4, "xp": 7.4, "starter": True, "cap": "VC", "color": "#DC2626"},
    {"name": "Palmer", "pos": "MID", "team": "CHE", "price": 10.8, "opp": "LIV (A)", "fdr": 4, "xp": 6.8, "starter": True, "cap": None, "color": "#2563EB"},
    {"name": "Saka", "pos": "MID", "team": "ARS", "price": 10.1, "opp": "BOU (A)", "fdr": 2, "xp": 6.9, "starter": True, "cap": None, "color": "#EF4444"},
    {"name": "Mbeumo", "pos": "MID", "team": "BRE", "price": 7.6, "opp": "MUN (A)", "fdr": 3, "xp": 5.3, "starter": True, "cap": None, "color": "#E11D48"},
    {"name": "Haaland", "pos": "FWD", "team": "MCI", "price": 15.4, "opp": "WOL (A)", "fdr": 2, "xp": 8.4, "starter": True, "cap": "C", "color": "#38BDF8"},
    {"name": "Watkins", "pos": "FWD", "team": "AVL", "price": 9.1, "opp": "FUL (A)", "fdr": 3, "xp": 5.5, "starter": True, "cap": None, "color": "#7C2D12"},
    {"name": "Wood", "pos": "FWD", "team": "NFO", "price": 6.3, "opp": "CRY (H)", "fdr": 2, "xp": 5.1, "starter": True, "cap": None, "color": "#DC2626"},
    # Bench
    {"name": "Fabianski", "pos": "GKP", "team": "WHU", "price": 4.0, "opp": "TOT (A)", "fdr": 4, "xp": 1.2, "starter": False, "cap": None, "color": "#7C2D12"},
    {"name": "Rogers", "pos": "MID", "team": "AVL", "price": 5.3, "opp": "FUL (A)", "fdr": 3, "xp": 4.4, "starter": False, "cap": None, "color": "#7C2D12"},
    {"name": "Aina", "pos": "DEF", "team": "NFO", "price": 4.6, "opp": "CRY (H)", "fdr": 2, "xp": 4.1, "starter": False, "cap": None, "color": "#DC2626"},
    {"name": "Greaves", "pos": "DEF", "team": "IPS", "price": 4.1, "opp": "EVE (H)", "fdr": 2, "xp": 3.2, "starter": False, "cap": None, "color": "#2563EB"},
]

# -----------------------------------------------------------------------------
# 3. TOP HEADER & KPI STRIP (st.columns(5))
# -----------------------------------------------------------------------------
h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1.6, 1, 1, 1, 1])
with h_col1:
    st.markdown("### 🛡️ Kings County FC\n`GW8 • Sat 11:00 AM` • **OR #14,820**")
with h_col2:
    st.metric("Squad Value", "£99.8m", "+£0.5m")
with h_col3:
    st.metric("In The Bank", "£0.7m", "Total £100.5m")
with h_col4:
    st.metric("GW8 Proj. xP", "75.5 pts", "+6.4 vs Avg")
with h_col5:
    st.metric("Free Transfers", "2 FT", "Roll Ready")

st.divider()

# -----------------------------------------------------------------------------
# 4. MAIN WORKSPACE SPLIT (st.columns([7, 3]))
# -----------------------------------------------------------------------------
left_pitch, right_panel = st.columns([7, 3], gap="large")

def render_card_html(p):
    mult = 2 if p["cap"] == "C" else 1
    badge = f'<div class="cap-badge">{p["cap"]}</div>' if p["cap"] else ""
    return f"""
    <div class="p-card">
        {badge}
        <svg width="38" height="38" viewBox="0 0 48 48" style="margin:0 auto;">
            <path d="M14 8L6 15L10 22L15 19V40H33V19L38 22L42 15L34 8H28L24 12L20 8H14Z"
                  fill="{p['color']}" stroke="#fff" stroke-width="1.5"/>
        </svg>
        <div class="p-name">{p['name']}</div>
        <div class="p-meta">£{p['price']}m • {p['opp']}</div>
        <div class="p-xp">{p['xp'] * mult:.1f} xP</div>
    </div>
    """

with left_pitch:
    starters = [p for p in SQUAD if p["starter"]]
    rows_html = ""
    for pos in ["GKP", "DEF", "MID", "FWD"]:
        cards = "".join(render_card_html(p) for p in starters if p["pos"] == pos)
        rows_html += f'<div class="pitch-row">{cards}</div>'
    
    st.markdown(f'<div class="fpl-pitch">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("#### SUBSTITUTES • PRIORITY ORDER")
    bench_cards = "".join(render_card_html(p) for p in SQUAD if not p["starter"])
    st.markdown(f'<div class="pitch-row" style="background:#161B22;padding:16px;border-radius:12px;">{bench_cards}</div>', unsafe_allow_html=True)

with right_panel:
    st.subheader("🔍 Player Inspector & Optimizer")
    selected_name = st.selectbox("Inspect Squad Player", [p["name"] for p in SQUAD], index=8)
    player = next(p for p in SQUAD if p["name"] == selected_name)
    st.info(f"**{player['name']} ({player['team']})** • £{player['price']}m • Next: **{player['opp']}** (xP: {player['xp']})")
    st.button("Make Captain (C)", use_container_width=True)
    st.button("Swap with Bench", use_container_width=True)
    

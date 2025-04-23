# streamlit_app.py

import streamlit as st
import pandas as pd
import psycopg2
from config import POSTGRES, RIOT_TABLE_NAME

# Page setup
st.set_page_config(page_title="Valorant Match Summary", layout="wide")
st.title("🔫 Valorant Match Summary")

# ─── Real-time refresh ─────────────────────────────────────────────────────
REFRESH_INTERVAL = 30  # seconds
st.caption(f"⏱ Auto-refresh every {REFRESH_INTERVAL}s")
if st.button("🔁 Refresh Now"):
    st.rerun()

# ─── Data loading ─────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    conn = psycopg2.connect(**POSTGRES)
    query = f"""
        SELECT
          game_start,
          map_name,
          mode,
          result,
          agent,
          kills,
          deaths,
          assists,
          score,
          damage
        FROM {RIOT_TABLE_NAME}
        ORDER BY game_start DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # convert to datetime
    df["game_start"] = pd.to_datetime(df["game_start"])
    return df

df = load_data()

# ─── Sidebar filters ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    modes    = df["mode"].unique()
    agents   = df["agent"].unique()
    selected_mode  = st.multiselect("Mode",   options=modes,  default=list(modes))
    selected_agent = st.multiselect("Agent",  options=agents, default=list(agents))

filtered_df = df[
    df["mode"].isin(selected_mode) &
    df["agent"].isin(selected_agent)
]

# ─── Calculate metrics ────────────────────────────────────────────────────
metrics_df = filtered_df.copy()
metrics_df["KD"]  = metrics_df["kills"]  / metrics_df["deaths"].replace(0, 1)
metrics_df["KDA"] = (metrics_df["kills"] + metrics_df["assists"]) / metrics_df["deaths"].replace(0, 1)

avg_kd   = round(metrics_df["KD"].mean(),  2)
avg_kda  = round(metrics_df["KDA"].mean(), 2)
winrate  = round((metrics_df["result"] == "Win").mean() * 100, 2)
last_game = metrics_df["game_start"].max()

# ─── Display overall stats ────────────────────────────────────────────────
st.subheader("📊 Overall Stats")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average K/D",  avg_kd)
c2.metric("Average KDA",  avg_kda)
c3.metric("Winrate (%)", f"{winrate}%")
c4.metric("Last Match",   last_game.strftime("%Y-%m-%d %H:%M:%S"))

# ─── Winrate by Agent ────────────────────────────────────────────────────
agent_stats = (
    metrics_df
      .groupby("agent")["result"]
      .value_counts()
      .unstack(fill_value=0)
      .reset_index()
)

for col in ("Win", "Loss"):
    if col not in agent_stats:
        agent_stats[col] = 0

agent_stats["Winrate (%)"] = round(
    agent_stats["Win"] / (agent_stats["Win"] + agent_stats["Loss"]) * 100,
    2
)

st.subheader("🧠 Winrate by Agent")
st.dataframe(
    agent_stats[["agent", "Win", "Loss", "Winrate (%)"]],
    use_container_width=True
)

# ─── Styled match table ──────────────────────────────────────────────────
def highlight_result(val):
    if val == "Win":
        return "background-color: #d4edda; color: #155724"
    elif val == "Loss":
        return "background-color: #f8d7da; color: #721c24"
    return ""

# ensure newest-to-oldest ordering
display_df = filtered_df.sort_values("game_start", ascending=False)

st.subheader("📋 Match Table")
styled = (
    display_df
      .loc[:, ["game_start", "map_name", "mode", "result", "agent", "kills", "deaths", "assists", "score", "damage"]]
      .style
      .applymap(highlight_result, subset=["result"])
)

st.dataframe(styled, use_container_width=True)

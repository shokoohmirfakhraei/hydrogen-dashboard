import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime
from mock_data import get_latest_readings, get_historical_readings
from gpt_helper import get_gpt_explanation

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Hydrogen Leak Monitor",
    page_icon="⚗️",
    layout="wide"
)

# ── Session state init ────────────────────────────────────
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []
if "total_alerts" not in st.session_state:
    st.session_state.total_alerts = 0
if "prev_readings" not in st.session_state:
    st.session_state.prev_readings = {}
if "language" not in st.session_state:
    st.session_state.language = "English"

# ── Language strings ──────────────────────────────────────
LANG = {
    "English": {
        "title":            "⚗️ Hydrogen Leak Detection System",
        "caption":          "Real-time monitoring — Raspberry Pi 5",
        "total_sensors":    "Total Sensors",
        "active_leaks":     "Active Leaks",
        "max_h2":           "Max H₂ (ppm)",
        "system_status":    "System Status",
        "alert":            "🔴 ALERT",
        "normal":           "🟢 Normal",
        "gauges":           "📊 Sensor Gauges",
        "map":              "🗺️ Leak Location Map",
        "table":            "📋 Live Sensor Readings",
        "chart_h2":         "📈 Hydrogen Concentration (Last 10 min)",
        "active_alerts":    "🚨 Active Alerts",
        "all_normal":       "✅ All sensors normal — No leaks detected",
        "alert_log":        "🕐 Alert History Log",
        "no_alerts":        "No alerts recorded yet this session.",
        "no_alerts_export": "No alerts yet to export.",
        "uptime":           "System Uptime",
        "total_alerts_label": "Total Alerts (Session)",
        "last_updated":     "Last Updated",
        "export":           "⬇️ Download Alert Log (CSV)",
        "trend":            "Trend",
        "status":           "Status",
        "sensor_id":        "Sensor ID",
        "hydrogen_ppm":     "H₂ (ppm)",
        "temperature":      "Temperature (°C)",
        "humidity":         "Humidity (%)",
        "leak_location":    "Leak Location",
        "leak_type":        "Leak Type",
        "timestamp":        "Timestamp",
        "alert_threshold":  "Alert threshold (25 ppm)",
        "gpt_analysis":     "🤖 GPT Analysis",
    },
    "Finnish": {
        "title":            "⚗️ Vetykaasuvuodon Tunnistusjärjestelmä",
        "caption":          "Reaaliaikainen seuranta — Raspberry Pi 5",
        "total_sensors":    "Anturit yhteensä",
        "active_leaks":     "Aktiiviset vuodot",
        "max_h2":           "Max H₂ (ppm)",
        "system_status":    "Järjestelmän tila",
        "alert":            "🔴 HÄLYTYS",
        "normal":           "🟢 Normaali",
        "gauges":           "📊 Anturimittarit",
        "map":              "🗺️ Vuodon sijaintikartta",
        "table":            "📋 Reaaliaikaiset lukemat",
        "chart_h2":         "📈 Vetypitoisuus (viimeiset 10 min)",
        "active_alerts":    "🚨 Aktiiviset hälytykset",
        "all_normal":       "✅ Kaikki anturit normaaleja — ei vuotoja",
        "alert_log":        "🕐 Hälytyshistoria",
        "no_alerts":        "Ei hälytyksiä tässä istunnossa.",
        "no_alerts_export": "Ei hälytyksiä vielä.",
        "uptime":           "Käyttöaika",
        "total_alerts_label": "Hälytykset yhteensä",
        "last_updated":     "Päivitetty",
        "export":           "⬇️ Lataa hälytysloki (CSV)",
        "trend":            "Trendi",
        "status":           "Tila",
        "sensor_id":        "Anturi ID",
        "hydrogen_ppm":     "H₂ (ppm)",
        "temperature":      "Lämpötila (°C)",
        "humidity":         "Kosteus (%)",
        "leak_location":    "Vuodon sijainti",
        "leak_type":        "Vuodon tyyppi",
        "timestamp":        "Aikaleima",
        "alert_threshold":  "Hälytysraja (25 ppm)",
        "gpt_analysis":     "🤖 GPT-analyysi",
    }
}

L: dict = LANG[st.session_state.language]

# ── Severity config ───────────────────────────────────────
SEVERITY_COLORS = {
    "Normal":        "#2ecc71",
    "Minor Leak":    "#f1c40f",
    "Moderate Leak": "#e67e22",
    "Major Leak":    "#e74c3c"
}

# ── Fetch data ────────────────────────────────────────────
df = get_latest_readings()
history = get_historical_readings(minutes=10)

# ── Log new alerts ────────────────────────────────────────
for _, row in df[df["is_anomaly"]].iterrows():
    log_entry = {
        "time":     datetime.now().strftime("%H:%M:%S"),
        "sensor":   row["sensor_id"],
        "ppm":      row["hydrogen_ppm"],
        "type":     row["leak_type"],
        "location": row["leak_location"]
    }
    if not st.session_state.alert_log or \
       st.session_state.alert_log[-1]["sensor"] != row["sensor_id"]:
        st.session_state.alert_log.append(log_entry)
        st.session_state.total_alerts += 1

st.session_state.alert_log = st.session_state.alert_log[-50:]

# ── Uptime ────────────────────────────────────────────────
uptime_seconds = int((datetime.now() - st.session_state.start_time).total_seconds())
uptime_str = f"{uptime_seconds//3600:02d}:{(uptime_seconds%3600)//60:02d}:{uptime_seconds%60:02d}"

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.title("⚗️ System Info")
    st.metric(L["uptime"], uptime_str)
    st.metric(L["total_alerts_label"], st.session_state.total_alerts)
    st.metric(L["last_updated"], datetime.now().strftime("%H:%M:%S"))
    st.divider()

    st.subheader("🎨 Severity Legend")
    for label, color in SEVERITY_COLORS.items():
        st.markdown(
            f'<div style="background-color:{color};padding:6px 12px;'
            f'border-radius:6px;margin-bottom:4px;color:white;font-weight:bold;">'
            f'{label}</div>',
            unsafe_allow_html=True
        )
    st.divider()

    st.subheader("📤 Export")
    if st.session_state.alert_log:
        log_df_export = pd.DataFrame(st.session_state.alert_log)
        csv = log_df_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=L["export"], data=csv,
            file_name=f"alert_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info(L["no_alerts_export"])

# ── Header with language toggle top right ─────────────────
col_title, col_spacer, col_lang = st.columns([6, 2, 2])

with col_title:
    st.title(L["title"])
    st.caption(L["caption"])

with col_lang:
    st.write("")
    lang_choice = st.radio(
        "🌐 Language",
        ["English", "Finnish"],
        index=0 if st.session_state.language == "English" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

st.divider()

# ── KPI cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric(L["total_sensors"], len(df))
col2.metric(L["active_leaks"], int(df["is_anomaly"].sum()))
col3.metric(L["max_h2"], f"{df['hydrogen_ppm'].max():.1f}")
col4.metric(L["system_status"],
            L["alert"] if df["is_anomaly"].any() else L["normal"])

st.divider()

# ── Gauge cards ───────────────────────────────────────────
st.subheader(L["gauges"])
gauge_cols = st.columns(len(df))
for i, (_, row) in enumerate(df.iterrows()):
    color = SEVERITY_COLORS.get(row["leak_type"], "#2ecc71")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row["hydrogen_ppm"],
        title={"text": f"{row['sensor_id']} — {row['leak_location']}<br>"
                       f"<span style='font-size:0.8em;color:{color}'>"
                       f"{row['leak_type']}</span>"},
        gauge={
            "axis": {"range": [0, 300]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 25],    "color": "#d5f5e3"},
                {"range": [25, 50],   "color": "#fef9e7"},
                {"range": [50, 150],  "color": "#fdebd0"},
                {"range": [150, 300], "color": "#fadbd8"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.75,
                "value": 25
            }
        },
        number={"suffix": " ppm"}
    ))
    fig.update_layout(height=250, margin=dict(t=60, b=0, l=20, r=20))
    gauge_cols[i].plotly_chart(fig, use_container_width=True)

st.divider()

# ── Visual map ────────────────────────────────────────────
st.subheader(L["map"])

SENSOR_POSITIONS = {
    "S1": (1, 3, "Corner A"),
    "S2": (3, 3, "Corner B"),
    "S3": (1, 1, "Corner C"),
    "S4": (3, 1, "Corner D"),
}

map_fig = go.Figure()
map_fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=3.5, y1=3.5,
                  line=dict(color="#555", width=3))
map_fig.add_trace(go.Scatter(
    x=[1, 3, 3, 1, 1], y=[3, 3, 1, 1, 3],
    mode="lines",
    line=dict(color="#aaa", width=2, dash="dot"),
    showlegend=False
))

for _, row in df.iterrows():
    sid = row["sensor_id"]
    x, y, corner = SENSOR_POSITIONS[sid]
    color = SEVERITY_COLORS.get(row["leak_type"], "#2ecc71")
    size = 40 if row["is_anomaly"] else 28

    map_fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers+text",
        marker=dict(size=size, color=color,
                    line=dict(color="white", width=2)),
        text=[f"{sid}<br>{row['hydrogen_ppm']} ppm"],
        textposition="top center",
        textfont=dict(size=11),
        name=f"{sid} — {row['leak_type']}",
        hovertemplate=(
            f"<b>{sid}</b><br>"
            f"{L['leak_location']}: {corner}<br>"
            f"{L['hydrogen_ppm']}: {row['hydrogen_ppm']}<br>"
            f"{L['temperature']}: {row['temperature']}°C<br>"
            f"{L['humidity']}: {row['humidity']}%<br>"
            f"{L['status']}: {row['leak_type']}"
            "<extra></extra>"
        )
    ))

map_fig.update_layout(
    height=400,
    xaxis=dict(range=[0, 4.2], showgrid=False,
               zeroline=False, showticklabels=False),
    yaxis=dict(range=[0, 4.2], showgrid=False,
               zeroline=False, showticklabels=False),
    plot_bgcolor="#f8f9fa",
    legend=dict(orientation="h", y=-0.05),
    margin=dict(t=20, b=20, l=20, r=20)
)
st.plotly_chart(map_fig, use_container_width=True)

st.divider()

# ── Sensor table with trend ───────────────────────────────
st.subheader(L["table"])

display_df = df.copy()
trends = []
for _, row in display_df.iterrows():
    sid = row["sensor_id"]
    prev = st.session_state.prev_readings.get(sid, row["hydrogen_ppm"])
    if row["hydrogen_ppm"] > prev + 0.5:
        trends.append("↑ Rising" if st.session_state.language == "English" else "↑ Nouseva")
    elif row["hydrogen_ppm"] < prev - 0.5:
        trends.append("↓ Falling" if st.session_state.language == "English" else "↓ Laskeva")
    else:
        trends.append("→ Stable" if st.session_state.language == "English" else "→ Vakaa")
    st.session_state.prev_readings[sid] = row["hydrogen_ppm"]

display_df["_trend"] = trends
display_df["_status"] = display_df.apply(
    lambda r: f"⚠️ {r['leak_type']}" if r["is_anomaly"] else "✅ Normal", axis=1
)

display_df = display_df.rename(columns={
    "sensor_id":    L["sensor_id"],
    "hydrogen_ppm": L["hydrogen_ppm"],
    "temperature":  L["temperature"],
    "humidity":     L["humidity"],
    "leak_location":L["leak_location"],
    "leak_type":    L["leak_type"],
    "timestamp":    L["timestamp"],
    "_trend":       L["trend"],
    "_status":      L["status"],
})

st.dataframe(
    display_df[[
        L["sensor_id"], L["hydrogen_ppm"], L["temperature"],
        L["humidity"], L["leak_location"], L["trend"],
        L["status"], L["timestamp"]
    ]],
    use_container_width=True
)

st.divider()

# ── H2 concentration chart ────────────────────────────────
st.subheader(L["chart_h2"])
if not history.empty:
    fig = px.line(
        history, x="timestamp", y="hydrogen_ppm",
        color="sensor_id", markers=True,
        labels={
            "hydrogen_ppm": L["hydrogen_ppm"],
            "timestamp":    L["timestamp"],
            "sensor_id":    L["sensor_id"]
        },
        color_discrete_map={
            "S1": "#2ecc71", "S2": "#f1c40f",
            "S3": "#e67e22", "S4": "#e74c3c"
        }
    )
    fig.add_hline(y=25, line_dash="dash", line_color="red",
                  annotation_text=L["alert_threshold"])
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Active alerts + GPT ───────────────────────────────────
anomalies = df[df["is_anomaly"] == True]
if not anomalies.empty:
    st.subheader(L["active_alerts"])
    for _, row in anomalies.iterrows():
        with st.container(border=True):
            if row["leak_type"] == "Minor Leak":
                st.warning(f"⚠️ **{row['leak_type']}** — {L['leak_location']}: "
                           f"{row['leak_location']} | {L['sensor_id']}: "
                           f"{row['sensor_id']} | {row['hydrogen_ppm']} ppm")
            else:
                st.error(f"🚨 **{row['leak_type']}** — {L['leak_location']}: "
                         f"{row['leak_location']} | {L['sensor_id']}: "
                         f"{row['sensor_id']} | {row['hydrogen_ppm']} ppm")

            cache_key = f"gpt_{row['sensor_id']}_{round(row['hydrogen_ppm'])}"
            if cache_key not in st.session_state:
                with st.spinner("Analyzing with GPT..."):
                    st.session_state[cache_key] = get_gpt_explanation(
                        row["sensor_id"], row["hydrogen_ppm"],
                        row["temperature"], row["humidity"]
                    )
            st.info(f"{L['gpt_analysis']}: {st.session_state[cache_key]}")
else:
    st.success(L["all_normal"])

st.divider()

# ── Alert history log ─────────────────────────────────────
st.subheader(L["alert_log"])
if st.session_state.alert_log:
    log_df = pd.DataFrame(st.session_state.alert_log[::-1])
    log_df = log_df.rename(columns={
        "time":     L["timestamp"],
        "sensor":   L["sensor_id"],
        "ppm":      L["hydrogen_ppm"],
        "type":     L["leak_type"],
        "location": L["leak_location"]
    })
    st.dataframe(log_df, use_container_width=True)
else:
    st.info(L["no_alerts"])

# ── Auto refresh ──────────────────────────────────────────
time.sleep(3)
st.rerun()

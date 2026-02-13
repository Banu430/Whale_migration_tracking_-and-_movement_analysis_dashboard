import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import json

# =========================================================
# SMART IOT BUOY SIMULATION PAGE
# =========================================================

def run_iot_buoy():

    st.title("📡 Smart IoT Buoy — Live Whale Detection Simulator")
    st.info("Simulated real-time ocean sensor buoys sending whale detection signals")

    # -----------------------------------------------------
    # SESSION STATE INIT
    # -----------------------------------------------------
    if "buoy_data" not in st.session_state:
        st.session_state.buoy_data = []

    if "running" not in st.session_state:
        st.session_state.running = False

    # -----------------------------------------------------
    # SIDEBAR CONTROLS (UNCHANGED)
    # -----------------------------------------------------
    st.sidebar.subheader("⚙ IoT Controls")

    update_speed = st.sidebar.slider("Update interval (seconds)", 1, 5, 2)
    num_buoys = st.sidebar.slider("Number of Buoys", 1, 5, 3)

    colA, colB = st.columns(2)

    if colA.button("▶ Start Simulation"):
        st.session_state.running = True

    if colB.button("⏹ Stop Simulation"):
        st.session_state.running = False

    # -----------------------------------------------------
    # SENSOR SIMULATION FUNCTION (UNCHANGED)
    # -----------------------------------------------------
    def generate_buoy_reading(buoy_id):
        base_lat = 34.0
        base_lon = -120.0

        lat = base_lat + random.uniform(-2, 2)
        lon = base_lon + random.uniform(-2, 2)

        temp = random.uniform(5, 18)
        depth = random.uniform(50, 300)
        sound = random.uniform(20, 120)
        wave = random.uniform(0.5, 3.5)

        whale_prob = 0
        if sound > 85: whale_prob += 0.4
        if 8 < temp < 16: whale_prob += 0.3
        if depth > 80: whale_prob += 0.2
        if wave < 2: whale_prob += 0.1

        whale_prob = min(1.0, whale_prob + random.uniform(0, 0.2))

        return {
            "time": pd.Timestamp.now(),
            "buoy": f"B-{buoy_id}",
            "lat": lat,
            "lon": lon,
            "temp": round(temp, 2),
            "depth": round(depth, 1),
            "sound": round(sound, 1),
            "wave": round(wave, 2),
            "whale_prob": round(whale_prob, 2)
        }

    # -----------------------------------------------------
    # PLACEHOLDERS
    # -----------------------------------------------------
    placeholder_metrics = st.empty()
    placeholder_map = st.empty()
    placeholder_chart = st.empty()
    placeholder_table = st.empty()
    placeholder_advanced = st.empty()

    # -----------------------------------------------------
    # LIVE LOOP
    # -----------------------------------------------------
    if st.session_state.running:

        for step in range(50):

            new_rows = [generate_buoy_reading(i+1) for i in range(num_buoys)]
            st.session_state.buoy_data.extend(new_rows)

            df = pd.DataFrame(st.session_state.buoy_data)

            # ---------------- METRICS ----------------
            with placeholder_metrics.container():
                st.subheader("📊 Live Sensor Metrics")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Signals", len(df))
                c2.metric("Active Buoys", df["buoy"].nunique())
                c3.metric("Whale Alerts", (df["whale_prob"] > 0.7).sum())

            # ---------------- MAP ----------------
            with placeholder_map.container():
                latest = df.sort_values("time").groupby("buoy").tail(1)

                fig = px.scatter_mapbox(
                    latest, lat="lat", lon="lon",
                    color="whale_prob", size="whale_prob",
                    zoom=3, height=500
                )
                fig.update_layout(mapbox_style="open-street-map")

                st.plotly_chart(fig, use_container_width=True,
                                key=f"map_{step}")

            # ---------------- SOUND TREND ----------------
            with placeholder_chart.container():
                fig2 = px.line(
                    df.tail(100),
                    x="time", y="sound",
                    color="buoy"
                )

                st.plotly_chart(fig2, use_container_width=True,
                                key=f"sound_{step}")

            # ---------------- TABLE ----------------
            with placeholder_table.container():
                st.dataframe(df.tail(10))

            # =====================================================
            # 🚀 ADVANCED IOT LAYER (INTEGRATION ONLY)
            # =====================================================
            with placeholder_advanced.container():

                st.subheader("🚀 Advanced IoT Intelligence Layer")

                latest = df.sort_values("time").groupby("buoy").tail(1)

                anomaly_flags = (
                    (latest["sound"] > 100) |
                    (latest["temp"] < 6) |
                    (latest["wave"] > 3)
                )

                st.write("⚠ Sensor Anomaly Flags")
                st.dataframe(latest[anomaly_flags])

                health_score = 100 - anomaly_flags.mean() * 100
                st.metric("🔧 Sensor Network Health", f"{health_score:.1f}%")

                alerts = df[df["whale_prob"] > 0.7]
                if not alerts.empty:
                    fig_alert = px.scatter(
                        alerts.tail(50),
                        x="time",
                        y="whale_prob",
                        color="buoy",
                        title="🚨 Whale Alert Timeline"
                    )
                    st.plotly_chart(fig_alert,
                                    use_container_width=True,
                                    key=f"alert_{step}")

                # -------- Cloud Payload --------
                latest_row = latest.iloc[-1]

                cloud_msg = {
                    "device_id": latest_row["buoy"],
                    "timestamp": str(latest_row["time"]),
                    "location": {
                        "lat": latest_row["lat"],
                        "lon": latest_row["lon"]
                    },
                    "sensors": {
                        "temp": latest_row["temp"],
                        "depth": latest_row["depth"],
                        "sound": latest_row["sound"],
                        "wave": latest_row["wave"]
                    },
                    "ai": {
                        "whale_probability": latest_row["whale_prob"],
                        "alert": bool(latest_row["whale_prob"] > 0.7)
                    }
                }

                st.subheader("☁ IoT Cloud Message Payload")
                st.code(json.dumps(cloud_msg, indent=2))

                topic = f"ocean/buoys/{latest_row['buoy']}/telemetry"
                st.write("📡 MQTT Topic:", topic)

                st.download_button(
                    "☁ Download Cloud Payload JSON",
                    json.dumps(cloud_msg, indent=2),
                    file_name="iot_payload.json",
                    key=f"payload_{step}"
                )

                st.download_button(
                    "📥 Download Full Sensor Stream CSV",
                    df.to_csv(index=False),
                    file_name="iot_full_stream.csv",
                    key=f"csv_{step}"
                )

            time.sleep(update_speed)

            if not st.session_state.running:
                break

    else:
        st.warning("Simulation stopped — press Start")


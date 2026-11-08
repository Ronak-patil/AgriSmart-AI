import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="AgriSmart AI", layout="wide", page_icon="🌿")

# Top Navbar/Header
st.markdown("### 🌿 AgriSmart AI | Crop & Fertilizer Recommendation Engine")
st.divider()

# Main Layout: 1 part for Inputs, 2.5 parts for Dashboard Outputs
left_col, right_col = st.columns([1, 2.5], gap="large")

with left_col:
    st.subheader("🪴 Soil & Climate Inputs")
    
    st.caption("CROPPING SEASON")
    season = st.selectbox("Season", ["Kharif (Monsoon - Jun to Oct)", "Rabi (Winter - Oct to Mar)", "Zaid (Summer - Mar to Jun)"], label_visibility="collapsed")
    
    st.caption("SOIL NUTRIENTS (KG/HA)")
    n = st.slider("Nitrogen (N)", 0, 140, 60)
    p = st.slider("Phosphorus (P)", 0, 100, 45)
    k = st.slider("Potassium (K)", 0, 120, 40)
    
    # Nested columns for compact climate inputs
    col_a, col_b = st.columns(2)
    with col_a:
        ph = st.slider("Soil pH", 4.0, 9.0, 6.5, 0.1)
        temp = st.slider("Avg Temperature (°C)", 10, 50, 26)
    with col_b:
        moisture = st.slider("Moisture (%)", 0, 100, 50)
        humidity = st.slider("Humidity (%)", 0, 100, 70)
        
    rain = st.slider("Annual Rainfall (mm)", 20, 400, 200)
    
    # Primary action button
    st.button("🪄 Calculate Recommendation", type="primary", use_container_width=True)

with right_col:
    # Expanded Database with descriptions for the UI cards
    crops_db = {
        "Rice (Paddy)": {"N": 80, "P": 40, "K": 40, "desc": "High moisture and water retaining soil suited for Kharif season."},
        "Sugarcane": {"N": 120, "P": 60, "K": 60, "desc": "Heavy feeder crop requiring ample sunlight and water."},
        "Maize (Corn)": {"N": 70, "P": 40, "K": 30, "desc": "Versatile crop with medium nutrient and water requirements."},
        "Cotton": {"N": 90, "P": 45, "K": 45, "desc": "Thrives in warm climate with deep black soil."},
        "Wheat": {"N": 100, "P": 50, "K": 40, "desc": "Ideal for Rabi season, requires moderate temperature."}
    }

    # Recommendation Logic
    scores = {}
    for crop, req in crops_db.items():
        diff = abs(n - req["N"]) + abs(p - req["P"]) + abs(k - req["K"])
        # Adjusted matching logic to generate realistic percentages
        match = max(15, 100 - int(diff * 0.4)) 
        scores[crop] = match

    sorted_crops = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_crop, best_score = sorted_crops[0]

    # --- TOP KPI CARDS ---
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        with st.container(border=True):
            st.metric(label="TOP RECOMMENDATION", value=best_crop, delta=f"{best_score}% Match Score")
            
    with kpi2:
        with st.container(border=True):
            req = crops_db[best_crop]
            deficits = {"Nitrogen": req["N"] - n, "Phosphorus": req["P"] - p, "Potassium": req["K"] - k}
            primary_deficit = max(deficits, key=deficits.get)
            
            if deficits[primary_deficit] > 0:
                deficit_status = f"{primary_deficit} Low"
                st.metric(label="PRIMARY DEFICIT", value=deficit_status, delta="Requires Supplementation", delta_color="inverse")
            else:
                st.metric(label="PRIMARY DEFICIT", value="Optimal", delta="No major deficit", delta_color="normal")
                
    with kpi3:
        with st.container(border=True):
            # Dynamic health score simulation
            health_score = 82 if (6.0 <= ph <= 7.5 and moisture >= 40) else 65
            st.metric(label="SOIL HEALTH SCORE", value=f"{health_score} / 100", delta="Optimal pH & Moisture")

    st.write("") # Spacing

    # --- TABBED INTERFACE ---
    tab1, tab2, tab3 = st.tabs(["📑 Crop Suitability Ranking", "🧪 Fertilizer Action Plan", "📊 Detailed NPK Breakdown"])

    with tab1:
        st.caption("RANKED COMPATIBLE CROPS")
        # Creating a 2-column grid for the crop cards
        grid_cols = st.columns(2)
        for i, (crop, score) in enumerate(sorted_crops[:4]): # Display top 4
            col = grid_cols[i % 2]
            with col:
                with st.container(border=True):
                    # Using columns inside the card to push the score to the right
                    card_col1, card_col2 = st.columns([3, 1])
                    card_col1.markdown(f"**{crop}**")
                    card_col2.success(f"{score}%")
                    
                    req_npk = crops_db[crop]
                    st.caption(f"Ideal NPK: {req_npk['N']}-{req_npk['P']}-{req_npk['K']}")
                    st.write(f"*{crops_db[crop]['desc']}*")
                    st.progress(score / 100)

    with tab2:
        st.caption("REQUIRED SUPPLEMENTATION (KG/HA)")
        req = crops_db[best_crop]
        urea = max(0, round((req["N"] - n) / 0.46))
        dap = max(0, round((req["P"] - p) / 0.46))
        mop = max(0, round((req["K"] - k) / 0.60))

        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            with st.container(border=True):
                st.metric("Urea (Nitrogen)", f"{urea} kg")
        with f_col2:
            with st.container(border=True):
                st.metric("DAP (Phosphorus)", f"{dap} kg")
        with f_col3:
            with st.container(border=True):
                st.metric("MOP (Potassium)", f"{mop} kg")

    with tab3:
        st.caption("CURRENT VS REQUIRED NUTRIENTS")
        df = pd.DataFrame({
            "Nutrient": ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
            "Current Input": [n, p, k],
            "Required Output": [req["N"], req["P"], req["K"]]
        }).set_index("Nutrient")
        st.bar_chart(df, color=["#1f77b4", "#2ca02c"])
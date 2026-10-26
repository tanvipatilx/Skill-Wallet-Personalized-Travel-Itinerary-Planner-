"""
app.py - VoyageAI: Personalized Travel Itinerary Planner SaaS
Full-Stack AI Travel Architect with Geographic Route Optimization, Real-Time Location Recommendations & Expense Auditing.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import json
import importlib
import ai_service
importlib.reload(ai_service)
import database
import pdf_generator

# Page Configuration
st.set_page_config(
    page_title="VoyageAI - Intelligent Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS Wanderlust Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .saas-hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .saas-hero h1 {
        color: #F8FAFC !important;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    
    .saas-hero p {
        color: #94A3B8 !important;
        font-size: 1.02rem;
        margin-bottom: 1rem;
    }
    
    .saas-badge {
        display: inline-block;
        background: rgba(14, 165, 233, 0.18);
        color: #38BDF8;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-right: 0.5rem;
    }
    
    .stat-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.08);
        color: #E2E8F0;
        padding: 0.28rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    
    .card-cluster {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    
    .slot-card {
        background: #F8FAFC;
        border-left: 4px solid #2563EB;
        border-radius: 0 10px 10px 0;
        padding: 0.95rem 1.15rem;
        margin-bottom: 0.7rem;
    }
    
    .slot-card-lunch {
        border-left-color: #F59E0B;
    }
    
    .slot-card-afternoon {
        border-left-color: #10B981;
    }
    
    .slot-card-evening {
        border-left-color: #8B5CF6;
    }
    
    .tag-chip {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }
    
    .cost-badge {
        font-weight: 700;
        color: #059669;
        font-size: 0.95rem;
    }
    
    .metric-container {
        background: #F1F5F9;
        border-radius: 12px;
        padding: 0.9rem;
        text-align: center;
        border: 1px solid #E2E8F0;
    }
    
    .metric-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0F172A;
    }
    
    .metric-label {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    .destination-pill {
        display: inline-block;
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation Options
NAV_ITINERARY = "📅 Day-by-Day Itinerary"
NAV_RECOMMENDER = "🧭 Smart Destination Recommender"
NAV_CUSTOMIZE = "⚡ Vibe Customization & Slot Swap"
NAV_PERSISTENCE = "💾 Trip Management & PDF Export"
ALL_NAV_TABS = [NAV_ITINERARY, NAV_RECOMMENDER, NAV_CUSTOMIZE, NAV_PERSISTENCE]

# Initialize Session State
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = "Paris, France"
if "recommended_destinations" not in st.session_state:
    st.session_state.recommended_destinations = None
if "active_currency" not in st.session_state:
    st.session_state.active_currency = "USD"
if "active_nav_tab" not in st.session_state:
    st.session_state.active_nav_tab = NAV_ITINERARY

# Top SaaS Banner
st.markdown("""
<div class="saas-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <div style="margin-bottom: 0.5rem;">
                <span class="saas-badge">VoyageAI SaaS 2.4</span>
                <span class="saas-badge" style="background: rgba(16, 185, 129, 0.18); color: #34D399; border-color: rgba(52, 211, 153, 0.3);">
                    ● Autonomous Trip Architect
                </span>
            </div>
            <h1>Personalized Travel Itinerary Planner</h1>
            <p>Algorithmic day-by-day vacation synthesis with geographic clustering, zero transit fatigue, and real-time budget auditing.</p>
            <div>
                <span class="stat-pill">✨ 94% Transit Fatigue Reduction</span>
                <span class="stat-pill">📍 District-Clustered Routing</span>
                <span class="stat-pill">📄 1-Click Offline PDF Guide</span>
                <span class="stat-pill">💾 Local SQLite Persistence</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar: Controls & Preferences
with st.sidebar:
    st.markdown("### 🧳 Trip Preferences")
    
    # Destination Input with Live Autocomplete & Recommendations
    input_destination = st.text_input(
        "Destination City / Region",
        value=st.session_state.selected_destination,
        help="Type any city or region, or select from recommended suggestions below"
    )
    
    # Sync destination input
    if input_destination != st.session_state.selected_destination:
        st.session_state.selected_destination = input_destination

    # Live Recommended Locations as User Types
    suggestions = ai_service.get_location_suggestions(input_destination, limit=4)
    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: #64748B; margin-bottom: 0.3rem;'>💡 Recommended Locations for you:</p>", unsafe_allow_html=True)
    
    s_col1, s_col2 = st.columns(2)
    destination_chosen_from_suggestion = False
    for idx, s in enumerate(suggestions):
        target_col = s_col1 if idx % 2 == 0 else s_col2
        if target_col.button(f"{s['display']}", key=f"sug_btn_{idx}", use_container_width=True):
            st.session_state.selected_destination = s["display"]
            destination_chosen_from_suggestion = True

    # Trending Quick Tags
    st.markdown("<p style='font-size: 0.75rem; color: #94A3B8; margin-top: 0.4rem; margin-bottom: 0.2rem;'>Popular picks: 🗼 Paris, ⛩️ Tokyo, 🏖️ Bali, 🌴 Goa, 🏔️ Manali, 🏰 Jaipur</p>", unsafe_allow_html=True)

    col_dur, col_party = st.columns(2)
    with col_dur:
        duration_days = st.slider("Duration (Days)", min_value=1, max_value=7, value=3)
    with col_party:
        travel_party = st.selectbox("Travel Party", ["Solo", "Couple", "Family with Kids", "Friends Group"], index=1)

    col_bud, col_pace = st.columns(2)
    with col_bud:
        budget_level = st.selectbox("Budget Tier", ["Budget", "Moderate", "Luxury"], index=1)
    with col_pace:
        travel_pace = st.selectbox("Pace", ["Relaxed", "Moderate", "Fast-Paced"], index=1)

    travel_dates = st.date_input("Travel Start Date", value=date.today() + timedelta(days=14))

    interests = st.multiselect(
        "Traveler Interests",
        ["Food & Culinary", "Culture & History", "Nature & Scenery", "Adventure & Treks", "Architecture", "Nightlife & Rooftops", "Art & Museums", "Shopping & Markets"],
        default=["Food & Culinary", "Culture & History", "Nature & Scenery"]
    )

    col_cur, col_demo = st.columns(2)
    with col_cur:
        currency_pref = st.selectbox("Currency", ["USD ($)", "INR (₹)"], index=0)
        st.session_state.active_currency = "USD" if "USD" in currency_pref else "INR"
    with col_demo:
        demo_mode = st.toggle("Fast Demo", value=False, help="Instant offline plan generation without network latency.")

    st.markdown("---")
    # Primary Action Button in Sidebar
    generate_sidebar_clicked = st.button("✨ Generate AI Itinerary", type="primary", use_container_width=True)

# Top Navigation Tabs (Controlled via Session State)
st.markdown("#### Explore VoyageAI Pillars")
nav_cols = st.columns(4)
for i, tab_title in enumerate(ALL_NAV_TABS):
    is_active = (st.session_state.active_nav_tab == tab_title)
    btn_type = "primary" if is_active else "secondary"
    if nav_cols[i].button(tab_title, key=f"nav_bar_{i}", type=btn_type, use_container_width=True):
        st.session_state.active_nav_tab = tab_title
        st.rerun()

st.markdown("---")

# Handle Generation Trigger
should_generate = (
    generate_sidebar_clicked 
    or destination_chosen_from_suggestion 
    or (st.session_state.itinerary is None)
)

if should_generate:
    with st.spinner(f"Synthesizing {duration_days}-day itinerary for {st.session_state.selected_destination} with district clustering..."):
        fresh_itinerary = ai_service.generate_optimized_itinerary(
            destination=st.session_state.selected_destination,
            duration_days=duration_days,
            budget_level=budget_level,
            travel_party=travel_party,
            pace=travel_pace,
            interests=interests,
            travel_dates=str(travel_dates),
            api_key=None,
            demo_mode=demo_mode
        )
        st.session_state.itinerary = fresh_itinerary
        # Immediately direct user to the Itinerary tab so they see it!
        st.session_state.active_nav_tab = NAV_ITINERARY
        st.rerun()

# ============================================================
# TAB VIEW: 📅 DAY-BY-DAY ITINERARY (DEFAULT ACTIVE)
# ============================================================
if st.session_state.active_nav_tab == NAV_ITINERARY:
    st.markdown(f"### 📅 Day-by-Day Clustered Itinerary: <span style='color: #2563EB;'>{st.session_state.selected_destination}</span>", unsafe_allow_html=True)
    st.caption("Our geographic clustering algorithm groups nearby landmarks on the same calendar day to eliminate transit fatigue and prevent backtracking.")

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        if st.button("🔄 Regenerate Plan for This Destination", type="primary", use_container_width=True):
            with st.spinner(f"Re-optimizing itinerary for {st.session_state.selected_destination}..."):
                st.session_state.itinerary = ai_service.generate_optimized_itinerary(
                    destination=st.session_state.selected_destination,
                    duration_days=duration_days,
                    budget_level=budget_level,
                    travel_party=travel_party,
                    pace=travel_pace,
                    interests=interests,
                    travel_dates=str(travel_dates),
                    api_key=None,
                    demo_mode=demo_mode
                )
                st.rerun()
    with col_btn2:
        if st.session_state.itinerary:
            if st.button("💾 Save Trip to Database", use_container_width=True):
                itin = st.session_state.itinerary
                trip_id = database.save_trip(
                    trip_title=itin.get("trip_title", f"Trip to {itin.get('destination')}"),
                    destination=itin.get("destination", st.session_state.selected_destination),
                    duration_days=itin.get("duration_days", duration_days),
                    budget_level=itin.get("budget_level", budget_level),
                    travel_party=itin.get("travel_party", travel_party),
                    total_cost_usd=itin.get("total_cost_usd", 0),
                    total_cost_inr=itin.get("total_cost_inr", 0),
                    itinerary_data=itin
                )
                st.success(f"Trip saved successfully to local SQLite persistence! (Trip Reference #{trip_id})")

    # Render Current Itinerary
    if st.session_state.itinerary:
        itin = st.session_state.itinerary
        tot_usd = itin.get("total_cost_usd", 0)
        tot_inr = itin.get("total_cost_inr", 0)
        fatigue_score = itin.get("transit_fatigue_reduction_pct", 94)
        cluster_summary = itin.get("cluster_strategy_summary", "")

        # Top Metric Cards
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{itin.get('duration_days', duration_days)} Days</div>
                <div class="metric-label">Duration</div>
            </div>
            """, unsafe_allow_html=True)
        with m_c2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: #2563EB;">{fatigue_score}%</div>
                <div class="metric-label">Transit Fatigue Score</div>
            </div>
            """, unsafe_allow_html=True)
        with m_c3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: #059669;">${tot_usd:,.0f}</div>
                <div class="metric-label">Est. Total (USD)</div>
            </div>
            """, unsafe_allow_html=True)
        with m_c4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: #059669;">₹{tot_inr:,.0f}</div>
                <div class="metric-label">Est. Total (INR)</div>
            </div>
            """, unsafe_allow_html=True)

        if cluster_summary:
            st.info(f"🧠 **Geographic Route Optimization:** {cluster_summary}")

        st.markdown("---")

        # Day-by-Day Accordion / Cards
        for day in itin.get("days", []):
            d_num = day.get("day_number", 1)
            d_theme = day.get("theme", f"Day {d_num}")
            d_cluster = day.get("geographic_cluster", "Central Zone")
            d_transit = day.get("transit_advice", "")
            d_cost_usd = day.get("day_cost_usd", 0)
            d_cost_inr = day.get("day_cost_inr", 0)

            with st.expander(f"📍 Day {d_num}: {d_theme} — Cluster: {d_cluster} (Est: ${d_cost_usd:.0f} / ₹{d_cost_inr:,.0f})", expanded=(d_num <= 2)):
                if d_transit:
                    st.caption(f"🚆 **Transit Advice:** {d_transit}")

                slots = day.get("slots", [])
                for slot in slots:
                    slot_name = slot.get("slot_name", "Activity Slot")
                    timing = slot.get("timing", "")
                    activity = slot.get("activity", "")
                    venue = slot.get("venue", "")
                    transit_tip = slot.get("transit_tip", "")
                    cost_u = slot.get("cost_usd", 0)
                    cost_i = slot.get("cost_inr", 0)
                    highlights = slot.get("highlights", "")

                    border_class = "slot-card"
                    if "Lunch" in slot_name:
                        border_class += " slot-card-lunch"
                    elif "Afternoon" in slot_name:
                        border_class += " slot-card-afternoon"
                    elif "Evening" in slot_name:
                        border_class += " slot-card-evening"

                    col_s1, col_s2 = st.columns([3.5, 1])
                    with col_s1:
                        st.markdown(f"""
                        <div class="{border_class}">
                            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                                <strong style="color: #1E293B; font-size: 0.95rem;">{slot_name}</strong>
                                <span style="font-size: 0.8rem; color: #64748B; font-weight: 600;">⏰ {timing}</span>
                            </div>
                            <div style="font-size: 1rem; font-weight: 700; color: #0F172A; margin: 0.3rem 0;">{activity}</div>
                            <div style="font-size: 0.84rem; color: #475569; margin-bottom: 0.3rem;"><b>Venue:</b> {venue}</div>
                            <div style="font-size: 0.82rem; color: #0F766E;">🚶 <b>Cluster Transit:</b> {transit_tip}</div>
                            <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.2rem;">💡 {highlights}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s2:
                        st.markdown(f"""
                        <div style="background: #F1F5F9; border-radius: 10px; padding: 0.8rem; text-align: center; border: 1px solid #E2E8F0; margin-top: 0.5rem;">
                            <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Est. Activity Cost</span>
                            <div class="cost-badge" style="font-size: 1.1rem; margin-top: 0.2rem;">${cost_u}</div>
                            <div style="font-size: 0.8rem; color: #475569;">₹{cost_i:,}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # Budget Tracker Table
        st.markdown("---")
        st.markdown("#### 💰 Running Cumulative Budget Tracker")
        budget_records = []
        running_usd = 0
        running_inr = 0
        for day in itin.get("days", []):
            d_u = day.get("day_cost_usd", 0)
            d_i = day.get("day_cost_inr", 0)
            running_usd += d_u
            running_inr += d_i
            budget_records.append({
                "Day": f"Day {day.get('day_number')}",
                "Geographic Cluster": day.get("geographic_cluster"),
                "Daily USD ($)": f"${d_u:.2f}",
                "Daily INR (₹)": f"₹{d_i:,.2f}",
                "Cumulative USD ($)": f"${running_usd:.2f}",
                "Cumulative INR (₹)": f"₹{running_inr:,.2f}"
            })
        st.dataframe(pd.DataFrame(budget_records), use_container_width=True, hide_index=True)

# ============================================================
# TAB VIEW: 🧭 SMART DESTINATION RECOMMENDER
# ============================================================
elif st.session_state.active_nav_tab == NAV_RECOMMENDER:
    st.markdown("### 🧭 Intelligent Destination Recommender")
    st.markdown("Can't decide where to go? Let our AI analyze seasonal weather, budget tiers, and target mood to match you with top destinations.")

    col_r1, col_r2, col_r3 = st.columns([1.5, 1, 1.2])
    with col_r1:
        vibe_pref = st.selectbox(
            "What is your target travel vibe?",
            ["Beach & Coastal", "Mountain & Alpine", "Cultural & Heritage", "Urban & Modern Skylines"]
        )
    with col_r2:
        season_pref = st.selectbox(
            "Target Weather Season",
            ["Spring", "Summer", "Autumn", "Winter"]
        )
    with col_r3:
        st.write("")
        st.write("")
        trigger_rec = st.button("🔍 Recommend Top 3 Destinations", type="primary", use_container_width=True)

    if trigger_rec or (st.session_state.recommended_destinations is None):
        with st.spinner("Analyzing global travel patterns, flight indices, and seasonal weather..."):
            dest_list = ai_service.recommend_destinations(
                vibe=vibe_pref,
                budget_level=budget_level,
                weather_season=season_pref,
                travel_party=travel_party,
                interests=interests,
                api_key=None,
                demo_mode=demo_mode
            )
            st.session_state.recommended_destinations = dest_list

    if st.session_state.recommended_destinations:
        st.markdown("---")
        rec_cols = st.columns(3)
        for idx, rec in enumerate(st.session_state.recommended_destinations[:3]):
            with rec_cols[idx]:
                city = rec.get("city", "Featured City")
                country = rec.get("country", "")
                match_score = rec.get("match_score", 95)
                why = rec.get("why_it_matches", "")
                cost_usd = rec.get("est_daily_cost_usd", 120)
                cost_inr = rec.get("est_daily_cost_inr", int(cost_usd * 86.5))
                best_s = rec.get("best_season", "All Year")
                tags = rec.get("highlight_tags", ["#MustVisit", "#TopRated"])
                experiences = rec.get("unmissable_experiences", ["Iconic Sightseeing", "Local Delicacies"])

                st.markdown(f"""
                <div class="card-cluster" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0; color: #0F172A; font-weight: 700; font-size: 1.25rem;">{city}</h3>
                            <span style="background: #ECFDF5; color: #059669; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.8rem;">
                                {match_score}% Match
                            </span>
                        </div>
                        <p style="color: #64748B; font-size: 0.88rem; margin-bottom: 0.6rem;"><b>{country}</b> &bull; Optimal: {best_s}</p>
                        <p style="color: #334155; font-size: 0.86rem; line-height: 1.4; margin-bottom: 0.8rem;">{why}</p>
                        <div style="margin-bottom: 0.8rem;">
                            {''.join([f'<span class="tag-chip">{t}</span>' for t in tags])}
                        </div>
                        <div style="border-top: 1px dashed #E2E8F0; padding-top: 0.6rem; margin-bottom: 0.8rem;">
                            <p style="font-size: 0.8rem; font-weight: 600; color: #475569; margin-bottom: 0.3rem;">Must-Try Experiences:</p>
                            <ul style="padding-left: 1.2rem; font-size: 0.82rem; color: #334155; margin-bottom: 0;">
                                {''.join([f'<li>{exp}</li>' for exp in experiences[:3]])}
                            </ul>
                        </div>
                    </div>
                    <div style="border-top: 1px solid #E2E8F0; padding-top: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B; display: block;">Daily Est.</span>
                            <span class="cost-badge">${cost_usd} / ₹{cost_inr:,}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🎯 Select {city} & Generate Plan", key=f"sel_rec_{idx}", use_container_width=True, type="primary"):
                    st.session_state.selected_destination = f"{city}, {country}"
                    with st.spinner(f"Building custom itinerary for {city}..."):
                        st.session_state.itinerary = ai_service.generate_optimized_itinerary(
                            destination=st.session_state.selected_destination,
                            duration_days=duration_days,
                            budget_level=budget_level,
                            travel_party=travel_party,
                            pace=travel_pace,
                            interests=interests,
                            travel_dates=str(travel_dates),
                            api_key=None,
                            demo_mode=demo_mode
                        )
                    st.session_state.active_nav_tab = NAV_ITINERARY
                    st.rerun()

# ============================================================
# TAB VIEW: ⚡ VIBE CUSTOMIZATION & DYNAMIC SLOT SWAP
# ============================================================
elif st.session_state.active_nav_tab == NAV_CUSTOMIZE:
    st.markdown("### ⚡ Vibe Customization & Dynamic Activity Swap")
    st.caption("Change any single meal or activity slot without regenerating the entire trip or losing your itinerary context. Geographic clustering is strictly maintained.")

    if not st.session_state.itinerary or "days" not in st.session_state.itinerary:
        st.warning("⚠️ No active itinerary found. Please generate an itinerary first.")
    else:
        itin = st.session_state.itinerary
        days = itin.get("days", [])
        day_options = [f"Day {d.get('day_number')}: {d.get('theme')}" for d in days]
        
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            selected_day_label = st.selectbox("1. Choose Day to Modify", day_options)
            day_idx = int(selected_day_label.split(":")[0].replace("Day", "").strip()) - 1
            current_day_obj = days[day_idx]
        with c_sel2:
            slot_names = [s.get("slot_name") for s in current_day_obj.get("slots", [])]
            target_slot_name = st.selectbox("2. Choose Slot to Swap", slot_names)
            
            # Find slot object
            current_slot_obj = None
            slot_idx = 0
            for i, s in enumerate(current_day_obj.get("slots", [])):
                if s.get("slot_name") == target_slot_name:
                    current_slot_obj = s
                    slot_idx = i
                    break

        st.markdown("---")
        st.markdown("#### 🎯 Current Slot Details:")
        if current_slot_obj:
            st.info(f"**Activity:** {current_slot_obj.get('activity')} | **Venue:** {current_slot_obj.get('venue')} | **Cost:** ${current_slot_obj.get('cost_usd')} (₹{current_slot_obj.get('cost_inr')})")

        # Customization instruction
        swap_presets = [
            "Swap for an authentic local street food night market",
            "Find a 100% vegetarian / vegan culinary gem",
            "Replace with a serene hidden Japanese garden or quiet cafe",
            "Swap museum for an active outdoor adventure or kayak ride",
            "Find a budget-friendly free landmark or scenic viewpoint",
            "Replace with artisan handicraft shopping and vintage bazaar"
        ]
        
        custom_choice = st.selectbox("3. Select Quick Vibe Swap Preset", ["Custom Prompt..."] + swap_presets)
        
        if custom_choice == "Custom Prompt...":
            swap_instruction = st.text_input("Enter your custom vibe swap instructions:", value="Swap for an authentic outdoor artisan bazaar")
        else:
            swap_instruction = custom_choice

        if st.button("🔄 Execute Dynamic Slot Swap", type="primary", use_container_width=True):
            with st.spinner(f"Swapping {target_slot_name} in {current_day_obj.get('geographic_cluster')}..."):
                new_slot = ai_service.swap_itinerary_slot(
                    current_slot=current_slot_obj,
                    swap_prompt=swap_instruction,
                    destination=itin.get("destination", st.session_state.selected_destination),
                    cluster_name=current_day_obj.get("geographic_cluster", "City Center"),
                    budget_level=itin.get("budget_level", budget_level),
                    api_key=None,
                    demo_mode=demo_mode
                )

                # Update in-place
                current_day_obj["slots"][slot_idx] = new_slot
                ai_service._enrich_costs(itin)
                st.session_state.itinerary = itin
                st.success(f"Successfully swapped {target_slot_name}! Day and trip totals have been recomputed automatically.")
                
                st.markdown("##### ✨ Updated Slot Result:")
                st.markdown(f"""
                <div class="slot-card" style="border-left-color: #EC4899;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #DB2777;">REPLACED SLOT &bull; {new_slot.get('slot_name')} ({new_slot.get('timing')})</div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin: 0.3rem 0;">{new_slot.get('activity')}</div>
                    <div style="font-size: 0.85rem; color: #475569;"><b>Venue:</b> {new_slot.get('venue')}</div>
                    <div style="font-size: 0.85rem; color: #0F766E;">🚶 <b>Cluster Transit:</b> {new_slot.get('transit_tip')}</div>
                    <div style="font-size: 0.85rem; color: #059669; font-weight: 700; margin-top: 0.3rem;">Est: ${new_slot.get('cost_usd')} (₹{new_slot.get('cost_inr'):,})</div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# TAB VIEW: 💾 TRIP MANAGEMENT & OFFLINE PDF EXPORT
# ============================================================
elif st.session_state.active_nav_tab == NAV_PERSISTENCE:
    st.markdown("### 💾 Trip Management & Offline PDF Export")
    st.caption("Store multiple itineraries in simulated SQLite persistence and generate print-ready travel guides complete with emergency checklists.")

    p_col1, p_col2 = st.columns([1.5, 2])
    with p_col1:
        st.markdown("#### 📄 1-Click Offline PDF Guide")
        if st.session_state.itinerary:
            try:
                pdf_bytes = pdf_generator.generate_itinerary_pdf(st.session_state.itinerary)
                dest_clean = st.session_state.itinerary.get("destination", "Trip").replace(" ", "_").replace(",", "")
                st.download_button(
                    label="📥 Download Offline Travel Guide (PDF)",
                    data=pdf_bytes,
                    file_name=f"VoyageAI_{dest_clean}_Itinerary.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                st.success("✅ PDF ready! Contains full day-by-day table, budget summary, emergency numbers, and packing checklist.")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        else:
            st.info("Generate or load an itinerary to enable PDF download.")

    with p_col2:
        st.markdown("#### 🗄️ Saved Trips History")
        saved_trips = database.get_all_trips()
        if not saved_trips:
            st.caption("No trips saved in database yet. Save an itinerary from the Itinerary tab to see it here.")
        else:
            for trip in saved_trips:
                t_id = trip["id"]
                t_title = trip["trip_title"]
                t_dest = trip["destination"]
                t_days = trip["duration_days"]
                t_cost = trip["total_cost_usd"]
                t_time = trip["created_at"]

                with st.expander(f"Trip #{t_id}: {t_title} ({t_dest} - {t_days} Days)"):
                    st.write(f"**Budget:** {trip['budget_level']} | **Party:** {trip['travel_party']} | **Cost:** ${t_cost:.2f} (₹{trip['total_cost_inr']:,.2f})")
                    st.write(f"**Created:** {t_time}")
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        if st.button("📂 Load Itinerary", key=f"load_{t_id}", use_container_width=True):
                            st.session_state.itinerary = trip["itinerary_data"]
                            st.session_state.selected_destination = t_dest
                            st.session_state.active_nav_tab = NAV_ITINERARY
                            st.toast(f"Loaded Trip #{t_id} into workspace!", icon="✅")
                            st.rerun()
                    with b_col2:
                        if st.button("🗑️ Delete", key=f"del_{t_id}", use_container_width=True):
                            database.delete_trip(t_id)
                            st.toast(f"Deleted Trip #{t_id}", icon="🗑️")
                            st.rerun()

# SaaS Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 1.5rem 0;">
    <b>VoyageAI</b> &bull; Autonomous Travel Intelligence Platform &bull; Built with Python, Streamlit, Google Gemini & ReportLab<br/>
    Production-grade Autonomous Travel Decision Support Engine. Zero external database dependencies.
</div>
""", unsafe_allow_html=True)

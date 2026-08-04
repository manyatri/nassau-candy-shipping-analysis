import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Shipping Dashboard", layout="wide", page_icon="🍬")

# ---------- LOAD DATA ----------
df = pd.read_csv("cleaned_nassau_data.csv")
route_summary = pd.read_csv("route_summary.csv")

# State name -> code mapping (needed for the map)
us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}

# ---------- HEADER ----------
st.markdown("""
    <h1 style='text-align: center; color: #D85A30;'>🍬 Nassau Candy</h1>
    <h3 style='text-align: center; color: #5F5E5A; font-weight: 400;'>Shipping Route Efficiency Dashboard</h3>
""", unsafe_allow_html=True)
st.markdown("---")

# ---------- SIDEBAR FILTERS ----------
st.sidebar.image("https://em-content.zobj.net/source/apple/391/candy_1f36c.png", width=80)
st.sidebar.header("Filters")

ship_modes = st.sidebar.multiselect(
    "Ship Mode", options=df['Ship Mode'].unique(), default=df['Ship Mode'].unique()
)
regions = st.sidebar.multiselect(
    "Region", options=df['Region'].unique(), default=df['Region'].unique()
)
lead_time_threshold = st.sidebar.slider("Delay threshold (days)", 1, 10, 5)

filtered_df = df[(df['Ship Mode'].isin(ship_modes)) & (df['Region'].isin(regions))]

# ---------- TOP METRICS (styled cards) ----------
col1, col2, col3, col4 = st.columns(4)

card_style = """
    <div style='background-color: #F5F0E8; padding: 20px; border-radius: 12px; text-align: center;'>
        <p style='color: #888780; font-size: 14px; margin-bottom: 4px;'>{label}</p>
        <p style='color: #D85A30; font-size: 28px; font-weight: 600; margin: 0;'>{value}</p>
    </div>
"""

with col1:
    st.markdown(card_style.format(label="Total Shipments", value=f"{len(filtered_df):,}"), unsafe_allow_html=True)
with col2:
    st.markdown(card_style.format(label="Unique Routes", value=filtered_df['Route'].nunique()), unsafe_allow_html=True)
with col3:
    st.markdown(card_style.format(label="Avg Lead Time", value=f"{filtered_df['Lead Time (Days)'].mean():.1f} days"), unsafe_allow_html=True)
with col4:
    delayed_pct = (filtered_df['Lead Time (Days)'] > lead_time_threshold).mean() * 100
    st.markdown(card_style.format(label="% Delayed", value=f"{delayed_pct:.1f}%"), unsafe_allow_html=True)

st.write("")
st.markdown("---")

# ---------- TABS FOR SECTIONS ----------
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Route Leaderboard", "📦 Ship Mode", "🌍 Regions", "🗺️ Map"])

CANDY_COLORS = ["#D85A30", "#F0997B", "#7F77DD", "#5DCAA5", "#D4537E"]

with tab1:
    st.subheader("Route Efficiency Leaderboard")
    min_shipments = st.slider("Minimum shipments per route (for reliability)", 1, 100, 10)
    route_filtered = route_summary[route_summary['Total_Shipments'] >= min_shipments].sort_values('Avg_Lead_Time')
    st.dataframe(route_filtered, use_container_width=True, height=400)

with tab2:
    st.subheader("Ship Mode Comparison")
    ship_mode_summary = filtered_df.groupby('Ship Mode').agg(
        Avg_Lead_Time=('Lead Time (Days)', 'mean'),
        Total_Shipments=('Order ID', 'count')
    ).reset_index().sort_values('Avg_Lead_Time')

    fig1 = px.bar(ship_mode_summary, x='Ship Mode', y='Avg_Lead_Time',
                  title="Average Lead Time by Ship Mode", text_auto='.2f',
                  color='Ship Mode', color_discrete_sequence=CANDY_COLORS)
    fig1.update_layout(showlegend=False, plot_bgcolor='white', title_font_size=18)
    st.plotly_chart(fig1, use_container_width=True)

with tab3:
    st.subheader("Region-wise Performance")
    region_summary = filtered_df.groupby('Region').agg(
        Avg_Lead_Time=('Lead Time (Days)', 'mean'),
        Total_Shipments=('Order ID', 'count')
    ).reset_index()

    fig2 = px.scatter(region_summary, x='Total_Shipments', y='Avg_Lead_Time', text='Region',
                       title="Volume vs Lead Time (top-right = bottleneck)",
                       size='Total_Shipments', color='Avg_Lead_Time',
                       color_continuous_scale=["#5DCAA5", "#F0997B", "#D85A30"])
    fig2.update_traces(textposition='top center')
    fig2.update_layout(plot_bgcolor='white', title_font_size=18)
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("State-wise Average Lead Time")
    state_summary = filtered_df.groupby('State/Province').agg(
        Avg_Lead_Time=('Lead Time (Days)', 'mean'),
        Total_Shipments=('Order ID', 'count')
    ).reset_index()

    state_summary['State Code'] = state_summary['State/Province'].map(us_state_abbrev)

    fig3 = px.choropleth(
        state_summary, locations='State Code', locationmode="USA-states",
        color='Avg_Lead_Time', scope="usa", color_continuous_scale="RdYlGn_r",
        title="Shipping Lead Time by State",
        hover_name='State/Province'
    )
    fig3.update_layout(title_font_size=18)
    st.plotly_chart(fig3, use_container_width=True)
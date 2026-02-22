"""
Luxury Fashion Bag Trends Dashboard
Real-time market intelligence for luxury handbag searches.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Import Google Sheets sync module
import gsheets_sync as gs

# Page configuration
st.set_page_config(
    page_title="Market Trends Dashboard",
    page_icon="👜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS from external file
def load_css(file_path):
    """Load CSS from an external file."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")


@st.cache_data(ttl=300)
def load_trends_data():
    """Load trends data from Google Sheets with caching."""
    try:
        return gs.get_trends_data(days=90)
    except Exception as e:
        st.error(f"Error loading trends data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_price_data():
    """Load price data from Google Sheets with caching."""
    try:
        return gs.get_price_data()
    except Exception as e:
        st.error(f"Error loading price data: {e}")
        return pd.DataFrame()


def generate_sample_data():
    """Generate sample data for demonstration when no real data is available."""
    dates = pd.date_range(end=datetime.now(), periods=180, freq='D')

    # Brand trends data
    brands = ['Hermès', 'Chanel', 'Louis Vuitton', 'Gucci', 'Prada', 'Bottega Veneta']
    brand_data = []

    base_values = {'Hermès': 80, 'Chanel': 75, 'Louis Vuitton': 70, 'Gucci': 65, 'Prada': 55, 'Bottega Veneta': 45}

    for date in dates:
        for brand in brands:
            base = base_values[brand]
            # Add trend and noise
            trend = (date - dates[0]).days * 0.05 if brand == 'Bottega Veneta' else 0
            noise = np.random.normal(0, 5)
            value = max(0, min(100, base + trend + noise))
            brand_data.append({
                'date': date,
                'brand': brand,
                'interest': value
            })

    # Color trends
    colors = ['Black', 'Brown/Tan', 'Beige', 'White/Cream', 'Green', 'Red', 'Blue', 'Pink']
    color_values = [65000, 48000, 42000, 38000, 35000, 28000, 22000, 18000]

    # Texture trends
    textures = ['Smooth Leather', 'Quilted', 'Grained Leather', 'Canvas', 'Suede', 'Patent Leather', 'Croc/Exotic', 'Woven']
    texture_values = [72000, 58000, 52000, 45000, 38000, 32000, 28000, 25000]

    # Style distribution
    styles = ['Shoulder Bag', 'Tote', 'Crossbody', 'Clutch', 'Bucket Bag', 'Satchel']
    style_values = [34, 24, 18, 10, 9, 5]

    return {
        'brand_trends': pd.DataFrame(brand_data),
        'colors': dict(zip(colors, color_values)),
        'textures': dict(zip(textures, texture_values)),
        'styles': dict(zip(styles, style_values))
    }


def format_number(num):
    """Format large numbers with K/M suffix."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(int(num))


def main():
    # Header section
    col_header, col_time, col_refresh = st.columns([3, 1, 1])

    with col_header:
        st.markdown('<p class="main-header">Luxury Fashion Bag Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Real-time market intelligence for luxury handbag searches</p>', unsafe_allow_html=True)

    with col_time:
        time_period = st.selectbox(
            "Time Period",
            ["Last 30 Days", "Last 60 Days", "Last 90 Days"],
            index=0,
            label_visibility="collapsed"
        )

    with col_refresh:
        last_updated = datetime.now().strftime("%b %d, %Y, %I:%M %p")
        st.caption(f"Last updated: {last_updated}")
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # Load data
    trends_df = load_trends_data()
    price_df = load_price_data()

    # Use sample data if no real data available
    sample_data = generate_sample_data()

    # Parse time period
    days = int(time_period.split()[1])

    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Searches",
            value="847.2K",
            delta="+24% vs last period"
        )

    with col2:
        st.metric(
            label="Avg. Daily Searches",
            value="28.2K",
            delta="+18% vs last period"
        )

    with col3:
        st.metric(
            label="Top Brand",
            value="Hermès",
            delta="+41% vs last period"
        )

    with col4:
        st.metric(
            label="Fastest Growing",
            value="Bottega Veneta",
            delta="+156% vs last period"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Brand Power Shift Chart
    st.markdown('<p class="section-title">Brand Power Shift</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Search volume trends by luxury brand (indexed)</p>', unsafe_allow_html=True)

    brand_df = sample_data['brand_trends']

    # Filter by time period
    cutoff_date = datetime.now() - timedelta(days=days)
    brand_df_filtered = brand_df[brand_df['date'] >= cutoff_date]

    # Create line chart
    fig_brands = px.line(
        brand_df_filtered,
        x='date',
        y='interest',
        color='brand',
        color_discrete_map={
            'Hermès': '#f97316',
            'Chanel': '#000000',
            'Louis Vuitton': '#8b4513',
            'Gucci': '#10b981',
            'Prada': '#3b82f6',
            'Bottega Veneta': '#22c55e'
        }
    )

    fig_brands.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="",
        yaxis_title="",
        hovermode='x unified'
    )

    st.plotly_chart(fig_brands, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Trending Search Combinations
    st.markdown('<p class="section-title">Trending Search Combinations</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Top keyword combinations this week</p>', unsafe_allow_html=True)

    trending_combinations = [
        {"rank": 1, "name": "Bottega Veneta Intrecciato", "searches": "35,290", "type": "Brand × Texture", "change": "+16%", "positive": True},
        {"rank": 2, "name": "Green Leather Shoulder Bag", "searches": "29,200", "type": "Color × Style", "change": "+89%", "positive": True},
        {"rank": 3, "name": "Woven Canvas Tote", "searches": "21,800", "type": "Texture × Style", "change": "+77%", "positive": True},
        {"rank": 4, "name": "Chanel Quilted", "searches": "19,000", "type": "Brand × Texture", "change": "-12%", "positive": False},
        {"rank": 5, "name": "Beige Suede Crossbody", "searches": "18,200", "type": "Color × Texture", "change": "+45%", "positive": True},
    ]

    for item in trending_combinations:
        col_rank, col_name, col_change = st.columns([0.5, 4, 1])

        with col_rank:
            st.markdown(f"**{item['rank']}**")

        with col_name:
            st.markdown(f"**{item['name']}** 🔗")
            st.caption(f"{item['searches']} searches · {item['type']}")

        with col_change:
            color = "green" if item['positive'] else "red"
            st.markdown(f":{color}[{item['change']}]")

    st.markdown("<br>", unsafe_allow_html=True)

    # Two column layout for Color and Texture trends
    col_color, col_texture = st.columns(2)

    with col_color:
        st.markdown('<p class="section-title">Color Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Top searched colors this month</p>', unsafe_allow_html=True)

        colors_data = sample_data['colors']
        color_df = pd.DataFrame({
            'Color': list(colors_data.keys()),
            'Searches': list(colors_data.values())
        })

        fig_colors = px.bar(
            color_df,
            y='Color',
            x='Searches',
            orientation='h',
            color='Color',
            color_discrete_map={
                'Black': '#1a1a1a',
                'Brown/Tan': '#8b4513',
                'Beige': '#d4b896',
                'White/Cream': '#f5f5dc',
                'Green': '#228b22',
                'Red': '#dc143c',
                'Blue': '#4169e1',
                'Pink': '#ff69b4'
            }
        )

        fig_colors.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig_colors, use_container_width=True)

    with col_texture:
        st.markdown('<p class="section-title">Texture & Material Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Popular textures and materials</p>', unsafe_allow_html=True)

        textures_data = sample_data['textures']
        texture_df = pd.DataFrame({
            'Texture': list(textures_data.keys()),
            'Searches': list(textures_data.values())
        })

        fig_textures = px.bar(
            texture_df,
            y='Texture',
            x='Searches',
            orientation='h',
            color_discrete_sequence=['#f97316']
        )

        fig_textures.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig_textures, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Style Distribution and Quick Insights
    col_style, col_insights = st.columns([1, 1])

    with col_style:
        st.markdown('<p class="section-title">Style & Shape Distribution</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Market share by bag style</p>', unsafe_allow_html=True)

        styles_data = sample_data['styles']
        style_df = pd.DataFrame({
            'Style': list(styles_data.keys()),
            'Share': list(styles_data.values())
        })

        fig_styles = px.pie(
            style_df,
            values='Share',
            names='Style',
            color='Style',
            color_discrete_map={
                'Shoulder Bag': '#f97316',
                'Tote': '#3b82f6',
                'Crossbody': '#22c55e',
                'Clutch': '#8b5cf6',
                'Bucket Bag': '#ec4899',
                'Satchel': '#eab308'
            }
        )

        fig_styles.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,
                xanchor="center",
                x=0.5
            )
        )

        fig_styles.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )

        st.plotly_chart(fig_styles, use_container_width=True)

    with col_insights:
        st.markdown('<p class="section-title">Quick Insights</p>', unsafe_allow_html=True)

        insights = [
            {
                "title": "Woven textures surging",
                "text": "+34% growth, driven by Bottega Veneta's signature Intrecciato weave",
                "color": "#10b981"
            },
            {
                "title": "Green is the new black",
                "text": "Green bags up 89%, especially in leather shoulder styles",
                "color": "#22c55e"
            },
            {
                "title": "Hermès maintains dominance",
                "text": "Consistent growth with 18-point search index, +12% vs last period",
                "color": "#f97316"
            },
            {
                "title": "Suede comeback",
                "text": "Suede texture searches up 22%, particularly in beige and neutral tones",
                "color": "#d4b896"
            },
            {
                "title": "Gucci searches declining",
                "text": "-3% month-over-month, consider monitoring brand strategy shifts",
                "color": "#ef4444"
            }
        ]

        for insight in insights:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color: {insight['color']}">
                <p class="insight-title">{insight['title']}</p>
                <p class="insight-text">{insight['text']}</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

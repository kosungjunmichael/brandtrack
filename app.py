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

import gsheets_sync as gs

st.set_page_config(
    page_title="Market Trends Dashboard",
    page_icon="👜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")


@st.cache_data(ttl=300)
def load_sheet_data(sheet_name):
    try:
        return gs.read_sheet_data(sheet_name)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_keywords():
    """Load keywords from local JSON cache, falling back to Google Sheets."""
    kw = gs.load_keywords_from_json()
    if not kw:
        try:
            kw = gs.get_keywords()
        except Exception:
            kw = {}
    return kw


def generate_sample_data(total_days=180):
    """Generate sample time-series data using all keywords from keywords.json."""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=total_days, freq='D')

    kw = load_keywords()
    brands         = kw.get('brands',         ['Gucci bag', 'Prada bag', 'Dior bag'])
    vintage_brands = kw.get('vintage_brands', ['Vintage Gucci bag', 'Vintage Prada bag'])
    colors         = kw.get('colors',         ['Black bag', 'Green bag'])
    textures       = kw.get('textures',       ['Woven bag', 'Suede bag'])
    styles         = kw.get('styles',         ['Crossbody bag', 'Tote bag'])

    def make_timeseries(keywords):
        bases = np.random.randint(30, 80, size=len(keywords))
        rows = []
        for date in dates:
            day_offset = (date - dates[0]).days
            for i, name in enumerate(keywords):
                trend = day_offset * 0.1 if i == 0 else 0
                value = max(0, min(100, bases[i] + trend + np.random.normal(0, 5)))
                rows.append({'date': date, 'keyword': name, 'interest': value})
        return pd.DataFrame(rows)

    raw_shares = np.random.randint(5, 30, size=len(styles)).astype(float)
    style_shares = dict(zip(styles, (raw_shares / raw_shares.sum() * 100).round(1)))

    return {
        'brand_trends':   make_timeseries(brands),
        'vintage_trends': make_timeseries(vintage_brands),
        'colors':   dict(zip(colors,   np.random.randint(15000, 70000, size=len(colors)))),
        'textures': dict(zip(textures, np.random.randint(20000, 75000, size=len(textures)))),
        'styles':   style_shares,
    }


def compute_top_and_delta(df, period_days):
    """Find the top keyword and % change vs the previous equal-length period."""
    now = datetime.now()
    current_start = now - timedelta(days=period_days)
    prev_start = now - timedelta(days=period_days * 2)

    df['date'] = pd.to_datetime(df['date'])
    current = df[df['date'] >= current_start].groupby('keyword')['interest'].mean()
    prev = df[(df['date'] >= prev_start) & (df['date'] < current_start)].groupby('keyword')['interest'].mean()

    if current.empty:
        return 'N/A', 0.0

    top = current.idxmax()
    curr_val = current[top]
    prev_val = prev.get(top, curr_val)
    delta = ((curr_val - prev_val) / prev_val * 100) if prev_val else 0.0
    return top, delta


def kpi_card(label, value, delta, period_days):
    delta_color = '#10b981' if delta >= 0 else '#ef4444'
    sign = '+' if delta >= 0 else ''
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta" style="color:{delta_color}">{sign}{delta:.2f}% vs {period_days} days ago</div>
    </div>
    """


CHART_LAYOUT = dict(
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title='',
    yaxis_title='',
    hovermode='x unified',
)



def main():
    # ── Header ──────────────────────────────────────────────────────────────
    col_header, col_controls = st.columns([3, 2])

    with col_header:
        st.markdown('<p class="main-header">Luxury Fashion Bag Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Real-time market intelligence for luxury handbag searches</p>', unsafe_allow_html=True)

    with col_controls:
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            time_period = st.selectbox(
                'Time Period',
                ['Last 30 Days', 'Last 60 Days', 'Last 90 Days'],
                index=0,
                label_visibility='visible',
            )
        with c2:
            st.caption(f"Last updated: {datetime.now().strftime('%b %d, %Y, %I:%M %p')}")
        with c3:
            if st.button('⟳ Refresh', use_container_width=True):
                st.cache_data.clear()
                st.rerun()

    st.divider()

    days = int(time_period.split()[1])
    sample = generate_sample_data()
    cutoff = datetime.now() - timedelta(days=days)

    # ── KPI Cards ────────────────────────────────────────────────────────────
    top_brand,   brand_delta   = compute_top_and_delta(sample['brand_trends'].copy(), days)
    top_vintage, vintage_delta = compute_top_and_delta(sample['vintage_trends'].copy(), days)
    top_color   = max(sample['colors'],   key=sample['colors'].get)
    top_texture = max(sample['textures'], key=sample['textures'].get)
    top_style   = max(sample['styles'],   key=sample['styles'].get)

    kpis = [
        ('Top Brand',         top_brand,   brand_delta),
        ('Top Vintage Brand', top_vintage, vintage_delta),
        ('Top Color',         top_color,   67.0),
        ('Top Texture',       top_texture, 66.96),
        ('Top Style',         top_style,   45.0),
    ]
    for col, (label, value, delta) in zip(st.columns(5), kpis):
        with col:
            st.markdown(kpi_card(label, value, delta, days), unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Brand Power Shift ────────────────────────────────────────────────────
    st.markdown('<p class="section-title">Brand Power Shift</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Search volume trends by luxury brand (indexed)</p>', unsafe_allow_html=True)

    brand_df = sample['brand_trends']
    brand_df = brand_df[brand_df['date'] >= cutoff]

    fig_brands = px.line(
        brand_df, x='date', y='interest', color='keyword',
        color_discrete_sequence=px.colors.qualitative.Light24,
        template='plotly_dark',
    )
    fig_brands.update_layout(
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=-0.5, xanchor='center', x=0.5),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_brands, use_container_width=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Vintage Brand Trends ─────────────────────────────────────────────────
    st.markdown('<p class="section-title">Vintage Brand Trends</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Actual yearly search interest over time</p>', unsafe_allow_html=True)

    vintage_df = sample['vintage_trends']
    vintage_df = vintage_df[vintage_df['date'] >= cutoff]

    fig_vintage = px.line(
        vintage_df, x='date', y='interest', color='keyword',
        color_discrete_sequence=px.colors.qualitative.Light24,
        template='plotly_dark',
    )
    fig_vintage.update_layout(
        height=350,
        legend=dict(orientation='h', yanchor='bottom', y=-0.5, xanchor='center', x=0.5),
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_vintage, use_container_width=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Color / Texture / Style ───────────────────────────────────────────────
    col_color, col_texture, col_style = st.columns(3)

    with col_color:
        st.markdown('<p class="section-title">Color Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Top searched colors this month</p>', unsafe_allow_html=True)

        color_df = pd.DataFrame({
            'Color': list(sample['colors'].keys()),
            'Searches': list(sample['colors'].values()),
        })
        fig_colors = px.bar(
            color_df, y='Color', x='Searches', orientation='h',
            color_discrete_sequence=['#4da6ff'],
            template='plotly_dark',
        )
        fig_colors.update_layout(height=max(300, len(sample['colors']) * 35), showlegend=False, **CHART_LAYOUT)
        st.plotly_chart(fig_colors, use_container_width=True)

    with col_texture:
        st.markdown('<p class="section-title">Texture & Material Trends</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Popular textures and materials</p>', unsafe_allow_html=True)

        texture_df = pd.DataFrame({
            'Texture': list(sample['textures'].keys()),
            'Searches': list(sample['textures'].values()),
        })
        fig_textures = px.bar(
            texture_df, y='Texture', x='Searches', orientation='h',
            color_discrete_sequence=['#8b4513'],
            template='plotly_dark',
        )
        fig_textures.update_layout(height=max(300, len(sample['textures']) * 35), showlegend=False, **CHART_LAYOUT)
        st.plotly_chart(fig_textures, use_container_width=True)

    with col_style:
        st.markdown('<p class="section-title">Style & Shape Distribution</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Market share by bag style</p>', unsafe_allow_html=True)

        style_df = pd.DataFrame({
            'Style': list(sample['styles'].keys()),
            'Share': list(sample['styles'].values()),
        })
        fig_styles = px.pie(
            style_df, values='Share', names='Style',
            color_discrete_sequence=px.colors.qualitative.Set2,
            template='plotly_dark',
        )
        fig_styles.update_layout(
            height=300,
            legend=dict(orientation='v', yanchor='middle', y=0.5, xanchor='left', x=1.0),
            **{k: v for k, v in CHART_LAYOUT.items() if k not in ('xaxis_title', 'yaxis_title', 'hovermode')},
        )
        fig_styles.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig_styles, use_container_width=True)


if __name__ == '__main__':
    main()

"""
Enterprise Compliance Dashboard - Main Application

A comprehensive Streamlit dashboard for data quality and compliance monitoring.
Ready for deployment on Streamlit Cloud.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Import dashboard utilities
from .utils import (
    DashboardDataLoader,
    format_number,
    generate_ml_metrics,
    get_data_quality_metrics,
    analyze_document_with_ml
)

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="Enterprise Compliance Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.company.com/compliance',
        'Report a bug': "https://github.com/company/dq-compliance/issues",
        'About': "Enterprise Data Quality & Compliance Platform v2.1"
    }
)

# --- Robust CSS Styling ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 2rem 1.5rem;
        margin-bottom: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .dashboard-subtitle {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* Metric cards styling */
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        opacity: 0.8;
    }
    
    .trend-indicator {
        font-size: 1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .metric-card h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card p {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .metric-card .delta {
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        display: inline-block;
    }
    .delta-positive { background-color: rgba(34, 197, 94, 0.1); color: #16a34a; }
    .delta-negative { background-color: rgba(239, 68, 68, 0.1); color: #dc2626; }
    .delta-neutral { background-color: rgba(100, 116, 139, 0.1); color: #475569; }

    /* Chart container styling */
    .chart-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        text-align: left;
    }
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Sidebar text and elements */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] .stDivider {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar selectbox styling */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #334155 !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
    }
    
    /* Sidebar button styling */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar info box styling */
    [data-testid="stSidebar"] .stAlert {
        background-color: #334155 !important;
        border: 1px solid #475569 !important;
        color: #e2e8f0 !important;
    }
    
    /* Additional sidebar element styling */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] h5, 
    [data-testid="stSidebar"] h6 {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #cbd5e1 !important;
    }
    
    /* Sidebar divider styling */
    [data-testid="stSidebar"] hr {
        border-color: #475569 !important;
    }

</style>
""", unsafe_allow_html=True)


# --- UI Component Functions ---

def create_dashboard_header():
    """Creates the main dashboard header."""
    st.markdown("""
        <div class="dashboard-header">
            <h1 class="dashboard-title">🏢 Enterprise Compliance Dashboard</h1>
            <p class="dashboard-subtitle">Data Quality & Risk Management Platform</p>
        </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="neutral", icon="📊", trend=None):
    """Creates a styled metric card using Streamlit columns and markdown."""
    delta_class = f"delta-{delta_color}"
    delta_html = f'<div class="delta {delta_class}">{delta}</div>' if delta else ""
    
    # Add trend indicator
    trend_html = ""
    if trend:
        trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
        trend_html = f'<div class="trend-indicator">{trend_icon}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            <span class="metric-icon">{icon}</span>
            {trend_html}
        </div>
        <h3>{title}</h3>
        <p>{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# --- Charting Functions ---

def create_risk_distribution_chart(data):
    """Creates a bar chart for risk distribution by category."""
    risk_dist = data.groupby("Risk Category")["Risk Value"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        risk_dist,
        x="Risk Category",
        y="Risk Value",
        color="Risk Category",
        text_auto='.2s',
        labels={"Risk Value": "Average Risk Score (%)", "Risk Category": "Category"}
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor='#e2e8f0'),
        height=350,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)

def create_regional_risk_heatmap(data):
    """Creates a heatmap of risk scores by region and category."""
    heatmap_data = data.pivot_table(index="Region", columns="Risk Category", values="Risk Value", aggfunc="mean").fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale="RdYlGn_r",
        text=np.around(heatmap_data.values, 1),
        texttemplate="%{text}",
        hovertemplate="<b>Region:</b> %{y}<br><b>Category:</b> %{x}<br><b>Risk:</b> %{z:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)

def create_compliance_trends_chart(data_loader, year):
    """Creates a line chart for compliance trends over time."""
    trends_data = data_loader.get_risk_trends(year)
    fig = px.line(
        trends_data,
        x="Date",
        y="Risk Value",
        color="Risk Category",
        labels={"Risk Value": "Average Risk Score (%)"},
        line_shape="spline"
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor='#e2e8f0'),
        height=400,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)


# --- Tab Functions ---

def show_executive_dashboard(data, data_loader, year):
    """Displays the main executive dashboard tab."""
    
    # --- KPIs ---
    st.markdown("### Key Performance Indicators")
    cols = st.columns(4)
    with cols[0]:
        compliance_score = data_loader.fetch_compliance_score(year)
        delta = compliance_score - 90
        trend = "up" if delta >= 0 else "down"
        create_metric_card(
            "Overall Compliance", f"{compliance_score}%", 
            f"▲ {delta:.1f}%" if delta >= 0 else f"▼ {abs(delta):.1f}%",
            "positive" if delta >= 0 else "negative",
            "✅", trend
        )
    with cols[1]:
        avg_risk = data["Risk Value"].mean()
        trend = "down" if avg_risk < 60 else "up"
        create_metric_card(
            "Average Risk Score", f"{avg_risk:.1f}%",
            "vs 60% Target", "neutral",
            "⚠️", trend
        )
    with cols[2]:
        high_risk_count = len(data[data["Risk Level"] == "High"])
        create_metric_card(
            "High-Risk Items", format_number(high_risk_count), 
            "Requires Action", "negative",
            "🚨", "up"
        )
    with cols[3]:
        ml_accuracy = 0.923 # Mock
        create_metric_card(
            "ML Model Accuracy", f"{ml_accuracy:.1%}", 
            "Risk Prediction", "positive",
            "🤖", "up"
        )

    st.divider()

    # --- Charts ---
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Risk Distribution by Category</div>', unsafe_allow_html=True)
            create_risk_distribution_chart(data)
    with cols[1]:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Regional Risk Heatmap</div>', unsafe_allow_html=True)
            create_regional_risk_heatmap(data)
            
    with st.container(border=True):
        st.markdown('<div class="chart-title">Compliance Trends Over Time</div>', unsafe_allow_html=True)
        create_compliance_trends_chart(data_loader, year)


def show_risk_analytics_tab(data):
    """Displays the risk analytics tab with a data table."""
    with st.container(border=True):
        st.markdown('<div class="chart-title">Deep Dive: Risk Register</div>', unsafe_allow_html=True)
        st.info("Filter and explore all identified risk items. Sort by clicking on column headers.")
        
        # Display a styled dataframe
        st.dataframe(
            data,
            use_container_width=True,
            height=500,
            column_config={
                "ID": st.column_config.TextColumn("Risk ID"),
                "Risk Value": st.column_config.ProgressColumn(
                    "Risk Score",
                    help="Calculated risk score from 0 to 100.",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )

def show_document_intelligence_tab():
    """Displays the document analysis tab."""
    with st.container(border=True):
        st.markdown('<div class="chart-title">📄 Document Intelligence</div>', unsafe_allow_html=True)
        st.write("Upload a legal document (PDF, TXT) for AI-powered compliance analysis. The model will extract key entities, assess risks, and provide a compliance score.")
        
        uploaded_file = st.file_uploader(
            "Upload Document for Analysis",
            type=["pdf", "txt"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            with st.spinner("🔍 Analyzing document with trained ML models..."):
                # Real ML analysis
                analysis = analyze_document_with_ml(uploaded_file)
                
                if analysis:
                    st.success(f"**Analysis Complete!** File: `{analysis['filename']}`")
                    
                    cols = st.columns(4)
                    cols[0].metric("Compliance Score", f"{analysis['compliance_score']}%")
                    cols[1].metric("Predicted Risk Level", analysis['risk_level'])
                    cols[2].metric("Processing Time", f"{analysis['processing_time']:.2f}s")
                    cols[3].metric("Model Used", analysis['model_used'])
                    
                    # Model confidence indicator
                    if 'confidence' in analysis:
                        confidence_pct = analysis['confidence'] * 100
                        st.progress(confidence_pct / 100, text=f"Model Confidence: {confidence_pct:.1f}%")
                    
                    expander = st.expander("**View Detailed Analysis**")
                    with expander:
                        st.subheader("Key Risks Identified")
                        for risk in analysis.get('key_risks', []):
                            if analysis['risk_level'] == 'High':
                                st.error(f"🚨 {risk}")
                            elif analysis['risk_level'] == 'Medium':
                                st.warning(f"⚠️ {risk}")
                            else:
                                st.info(f"ℹ️ {risk}")
                        
                        st.subheader("Recommendations")
                        for i, rec in enumerate(analysis.get('recommendations', []), 1):
                            st.write(f"{i}. {rec}")
                        
                        if 'sentiment' in analysis:
                            st.subheader("Sentiment Analysis")
                            sentiment = analysis['sentiment']
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Positive", f"{sentiment.get('positive', 0):.1%}")
                            col2.metric("Neutral", f"{sentiment.get('neutral', 0):.1%}")
                            col3.metric("Negative", f"{sentiment.get('negative', 0):.1%}")
                        
                        st.subheader("Extracted Entities")
                        entities = analysis.get('entities', [])
                        if entities:
                            entity_text = " • ".join(entities)
                            st.write(f"**Entities:** {entity_text}")
                        else:
                            st.info("No specific entities detected in this document.")
                else:
                    st.error("Failed to analyze document. Please try again.")

def show_ml_performance_tab():
    """Displays the ML model performance monitoring tab."""
    with st.container(border=True):
        st.markdown('<div class="chart-title">🤖 ML Model Performance</div>', unsafe_allow_html=True)
        
        metrics_df = generate_ml_metrics()
        
        model_options = metrics_df['model_name'].unique().tolist()
        selected_model = st.selectbox("Select Model to Analyze", model_options)
        
        model_data = metrics_df[metrics_df['model_name'] == selected_model]
        
        # --- Latest Metrics ---
        latest = model_data.iloc[0]
        cols = st.columns(4)
        cols[0].metric("Accuracy", f"{latest['accuracy']:.3f}")
        cols[1].metric("Precision", f"{latest['precision']:.3f}")
        cols[2].metric("Recall", f"{latest['recall']:.3f}")
        cols[3].metric("Latency", f"{latest['latency_ms']:.0f} ms")

        # --- Performance over time ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Accuracy, Precision, Recall over Time", "Latency (ms) over Time"))

        for metric in ['accuracy', 'precision', 'recall']:
            fig.add_trace(go.Scatter(x=model_data['date'], y=model_data[metric], name=metric.capitalize(), mode='lines+markers'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=model_data['date'], y=model_data['latency_ms'], name='Latency', line=dict(color='orange')), row=2, col=1)
        
        fig.update_layout(height=500, showlegend=True, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

def show_data_quality_tab():
    """Displays the data quality monitoring tab."""
    with st.container(border=True):
        st.markdown('<div class="chart-title">📋 Data Quality Overview</div>', unsafe_allow_html=True)
        metrics = get_data_quality_metrics()
        
        overall_score = metrics.pop("Overall Score")
        st.metric(
            "Overall Data Quality Score",
            f"{overall_score['value']}%",
            f"{overall_score['delta']}% vs last week",
        )
        st.progress(int(overall_score['value']))
        
        st.divider()
        st.subheader("Dimension Scores")
        
        cols = st.columns(len(metrics))
        for i, (metric, values) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(metric, f"{values['value']}%", f"{values['delta']}%")


# --- Main Application ---
def main():
    """Main dashboard application logic."""
    
    # Initialize session state for auto-refresh
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 30
    
    # --- Sidebar Controls ---
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Controls")
        
        # Auto-refresh controls
        st.markdown("#### ⚡ Real-time Updates")
        auto_refresh = st.toggle("Enable Auto-refresh", value=st.session_state.auto_refresh)
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh Interval",
                options=[15, 30, 60, 120, 300],
                index=1,
                format_func=lambda x: f"{x//60}min {x%60}s" if x >= 60 else f"{x}s"
            )
            st.session_state.refresh_interval = refresh_interval
        
        st.session_state.auto_refresh = auto_refresh
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
        
        st.divider()
        
        # Year selection
        current_year = datetime.now().year
        selected_year = st.selectbox(
            "📅 Select Year",
            options=[current_year, current_year - 1, current_year - 2],
            index=0
        )
        
        # Enhanced Risk type filter with multi-select
        st.markdown("#### 🔍 Risk Categories")
        risk_types = ["Financial", "Operational", "Legal", "Regulatory", "Cybersecurity"]
        selected_risk_types = st.multiselect(
            "Select Risk Categories",
            options=risk_types,
            default=risk_types,
            help="Select multiple risk categories to filter data"
        )
        
        # Enhanced Region filter with multi-select
        st.markdown("#### 🌍 Regions")
        regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        selected_regions = st.multiselect(
            "Select Regions",
            options=regions,
            default=regions,
            help="Select multiple regions to filter data"
        )
        
        # Risk level filter
        st.markdown("#### ⚠️ Risk Levels")
        risk_levels = ["Low", "Medium", "High"]
        selected_risk_levels = st.multiselect(
            "Filter by Risk Level",
            options=risk_levels,
            default=risk_levels,
            help="Select risk levels to include in analysis"
        )
        
        st.divider()
        
        # Export options
        st.markdown("#### 📊 Export Options")
        if st.button("📥 Export Data", use_container_width=True):
            st.info("Export functionality will be implemented here")
        
        st.divider()
        st.info("This is a demonstration dashboard with mock data.")
        st.markdown("© 2025 Enterprise Solutions Inc.")

    # --- Main Content Area ---
    create_dashboard_header()
    
    # --- Status indicators ---
    if st.session_state.auto_refresh:
        st.success(f"🔄 Auto-refresh enabled - Updates every {st.session_state.refresh_interval}s")
    
    # Show data loading status
    with st.spinner("📊 Loading compliance data..."):
        # --- Load and filter data once ---
        data_loader = DashboardDataLoader()
        
        # Use @st.cache_data for this function in a real app
        @st.cache_data
        def load_filtered_data(year, risk_types, regions, risk_levels):
            # Load all data for the year
            data = data_loader.load_compliance_data(year, 'all')
            
            # Apply filters
            if risk_types:
                data = data[data["Risk Category"].isin(risk_types)]
            if regions:
                data = data[data["Region"].isin(regions)]
            if risk_levels:
                data = data[data["Risk Level"].isin(risk_levels)]
                
            return data

        data = load_filtered_data(selected_year, selected_risk_types, selected_regions, selected_risk_levels)
        
        if data.empty:
            st.warning("No data available for the selected filters. Please try a different selection.")
            st.stop()
        
        # --- Data Summary ---
        with st.expander("📊 Data Summary & Filter Impact", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", format_number(len(data)))
            with col2:
                st.metric("Risk Categories", len(selected_risk_types))
            with col3:
                st.metric("Regions", len(selected_regions))
            with col4:
                st.metric("Risk Levels", len(selected_risk_levels))
            
            # Show active filters
            st.markdown("**Active Filters:**")
            filter_info = f"Year: {selected_year} | Categories: {', '.join(selected_risk_types)} | Regions: {', '.join(selected_regions)} | Risk Levels: {', '.join(selected_risk_levels)}"
            st.info(filter_info)
            
        # --- Tabs for different views ---
        tab_titles = [
            "📊 Executive Dashboard", 
            "🔎 Risk Analytics", 
            "📄 Document Intelligence", 
            "🤖 ML Performance", 
            "📋 Data Quality"
        ]
        tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

        with tab1:
            show_executive_dashboard(data, data_loader, selected_year)

        with tab2:
            show_risk_analytics_tab(data)

        with tab3:
            show_document_intelligence_tab()

        with tab4:
            show_ml_performance_tab()

        with tab5:
            show_data_quality_tab()

    # Auto-refresh functionality
    if st.session_state.auto_refresh:
        time.sleep(1)  # Small delay to prevent too frequent updates
        st.rerun()


if __name__ == "__main__":
    main()

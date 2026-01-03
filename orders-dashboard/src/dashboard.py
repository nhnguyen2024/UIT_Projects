"""
Orders Dashboard - Main Streamlit Application with Dark/Light Theme

This is the UI layer that brings together:
- DataLoader: CSV loading and management
- DataWarehouse: ETL pipeline and data transformation
- KPIAnalyzer: Metrics calculation and analysis
- ReportGenerator: PDF report creation
"""
import streamlit as st
import altair as alt
import pandas as pd

from src import FILE_CONFIG, DataLoader, DataWarehouse, KPIAnalyzer, ReportGenerator

# Configure page
st.set_page_config(
    page_title="Orders Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme

# Custom CSS for both light and dark themes
def apply_custom_styling():
    if st.session_state.theme == 'dark':
        theme_css = """
        /* DARK THEME */
        :root {
            --primary-color: #0066cc;
            --secondary-color: #00cc99;
            --accent-color: #ff6b6b;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --border-color: #475569;
            --card-bg: #1e293b;
        }
        
        body {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        /* Header styling - Dark */
        h1, h2, h3 {
            color: #f1f5f9;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Metric cards - Dark */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.15);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
            box-shadow: 0 8px 20px rgba(0, 102, 204, 0.25);
            transform: translateY(-2px);
            border-color: #0066cc;
        }
        
        /* Sidebar - Dark */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* Text in sidebar */
        [data-testid="stSidebar"] h3 {
            color: #f1f5f9;
        }
        
        /* Divider - Dark */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #334155, transparent);
        }
        
        /* Dataframe - Dark */
        [data-testid="dataFrame"] {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            background-color: #1e293b;
        }
        """
    else:  # Light theme
        theme_css = """
        /* LIGHT THEME */
        :root {
            --primary-color: #0066cc;
            --secondary-color: #00cc99;
            --accent-color: #ff6b6b;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --border-color: #e2e8f0;
            --card-bg: #ffffff;
        }
        
        body {
            background-color: #ffffff;
            color: #0f172a;
        }
        
        /* Header styling - Light */
        h1, h2, h3 {
            color: #1e293b;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Metric cards - Light */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
            border-color: #0066cc;
        }
        
        /* Sidebar - Light */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        }
        
        /* Text in sidebar */
        [data-testid="stSidebar"] h3 {
            color: #0f172a;
        }
        
        /* Divider - Light */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }
        
        /* Dataframe - Light */
        [data-testid="dataFrame"] {
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            background-color: #ffffff;
        }
        """
    
    # Common CSS for both themes
    common_css = """
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0052a3 0%, #003d7a 100%);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.4);
        transform: translateY(-1px);
    }
    
    /* Selectbox and input styling */
    .stSelectbox, .stDateInput {
        border-radius: 8px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Info/Success/Warning messages */
    [data-testid="stInfo"], [data-testid="stSuccess"], [data-testid="stWarning"] {
        border-radius: 8px;
        border-left: 4px solid #0066cc;
    }
    """
    
    st.markdown(f"""
    <style>
    {theme_css}
    {common_css}
    </style>
    """, unsafe_allow_html=True)

apply_custom_styling()

def main():
    # Header with gradient background
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0066cc 0%, #00cc99 100%); 
                padding: 2.5rem 2rem; 
                border-radius: 12px; 
                margin-bottom: 2rem;
                box-shadow: 0 4px 15px rgba(0, 102, 204, 0.2);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>Orders Analytics Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Real-time order management & performance insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Theme toggle button in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <h3 style='margin-top: 1rem; margin-bottom: 1rem;'>⚙️ Theme Settings</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("☀️ Light", use_container_width=True, 
                     key="light_theme",
                     help="Switch to light theme"):
            st.session_state.theme = 'light'
            st.rerun()
    
    with col2:
        if st.button("🌙 Dark", use_container_width=True,
                     key="dark_theme",
                     help="Switch to dark theme"):
            st.session_state.theme = 'dark'
            st.rerun()
    
    # Display current theme
    current_theme = "Light" if st.session_state.theme == 'light' else "Dark"
    st.sidebar.info(f"Current theme: **{current_theme}** 🎨")

    # Data Input Section
    st.sidebar.markdown("""
    <h3 style='color: #f8fafc; margin-top: 1rem; margin-bottom: 1rem;'>Data Input</h3>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("Upload & Update", expanded=True):
        st.markdown("Upload your CSV files to update the data:")
        up_web = st.file_uploader("Web Orders (.csv)", type='csv', key='web')
        up_app = st.file_uploader("App Orders (.csv)", type='csv', key='app')
        up_items = st.file_uploader("Items Detail (.csv)", type='csv', key='items')
    
    # --- ETL PROCESS ---
    with st.spinner('Đang xử lý'):
        df_web = DataLoader.load(up_web, FILE_CONFIG["web"], "Web Source")
        df_app = DataLoader.load(up_app, FILE_CONFIG["app"], "App Source")
        df_items = DataLoader.load(up_items, FILE_CONFIG["items"], "Items Source")
        df_channels = DataLoader.load(None, FILE_CONFIG["channels"], "Channels")

        dw = DataWarehouse()
        dw.transform_and_load(df_web, df_app, df_items, df_channels)

    if dw.merged_data.empty:
        st.info("👋 Vui lòng tải file dữ liệu lên để bắt đầu.")
        st.stop()

    # --- DASHBOARD ---
    analyzer = KPIAnalyzer(dw.merged_data)

    # Filter Section
    st.sidebar.markdown("""
    <h3 style='color: #f8fafc; margin-top: 1rem; margin-bottom: 1.5rem;'>🔍 Filters</h3>
    """, unsafe_allow_html=True)
    
    chn_opts = ['All']
    if 'channel_name' in dw.merged_data.columns:
        chn_opts += list(dw.merged_data['channel_name'].dropna().unique())
    sel_chn = st.sidebar.selectbox("Sales Channel:", chn_opts)
    
    sel_date = []
    if 'order_date' in dw.merged_data.columns:
        d_min = dw.merged_data['order_date'].min().date()
        d_max = dw.merged_data['order_date'].max().date()
        sel_date = st.sidebar.date_input("Date Range:", [d_min, d_max])

    final_kpi = analyzer.filter(sel_chn, sel_date)
    rev, rate, aov, cancel, best = final_kpi.get_metrics()

    # KPI Metrics Section
    st.markdown("""
    <h2 style='color: #1e293b; margin-top: 2rem; margin-bottom: 1.5rem;'>📈 Performance Metrics</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="large")
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${rev:,.0f}",
            delta=None,
            help="Sum of completed orders"
        )
    
    with col2:
        st.metric(
            label="Average Order Value",
            value=f"${aov:,.0f}",
            delta=None,
            help="Average transaction value"
        )
    
    with col3:
        st.metric(
            label="Return Rate",
            value=f"{rate:.1f}%",
            delta=None,
            delta_color="inverse",
            help="Returned items ratio"
        )
    
    with col4:
        st.metric(
            label="Cancellation Rate",
            value=f"{cancel:.1f}%",
            delta=None,
            delta_color="inverse",
            help="Cancelled orders ratio"
        )

    st.markdown("---")

    # Charts Section
    st.markdown("""
    <h2 style='color: #1e293b; margin-bottom: 1.5rem;'>Visual Analytics</h2>
    """, unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns([2, 1], gap="large")
    
    # Daily Revenue Trend
    with chart_col1:
        st.subheader("📈 Revenue Trend")
        daily = final_kpi.get_daily_revenue()
        if not daily.empty:
            # Create styled line chart
            chart_data = daily.reset_index()
            chart_data.columns = ['Date', 'Revenue']
            
            revenue_chart = alt.Chart(chart_data).mark_line(
                point=True,
                color='#0066cc',
                size=3
            ).encode(
                x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%b %d')),
                y=alt.Y('Revenue:Q', title='Revenue ($)', axis=alt.Axis(format='$,.0f')),
                tooltip=['Date:T', alt.Tooltip('Revenue:Q', format='$,.0f')]
            ).properties(
                height=350
            ).interactive()
            
            # Add area under the line
            area_chart = alt.Chart(chart_data).mark_area(
                opacity=0.2,
                color='#0066cc'
            ).encode(
                x='Date:T',
                y='Revenue:Q'
            )
            
            st.altair_chart(area_chart + revenue_chart, use_container_width=True)
        else:
            st.info("No data available for the selected period")
            
    # Channel Distribution
    with chart_col2:
        st.subheader("🎯 Channel Distribution")
        dist = final_kpi.get_channel_dist()
        if not dist.empty:
            df_chart = dist.reset_index()
            df_chart.columns = ['Channel', 'Revenue']
            
            # Create horizontal bar chart with color gradient
            colors = ['#0066cc', '#00cc99', '#ff6b6b', '#ffc300', '#9b59b6']
            df_chart['Color'] = [colors[i % len(colors)] for i in range(len(df_chart))]
            
            channel_chart = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X('Revenue:Q', title='Revenue ($)', axis=alt.Axis(format='$,.0f')),
                y=alt.Y('Channel:N', sort='-x', title=''),
                color=alt.Color('Channel:N', scale=alt.Scale(scheme='category10'), legend=None),
                tooltip=['Channel:N', alt.Tooltip('Revenue:Q', format='$,.0f')]
            ).properties(
                height=300
            ).interactive()
            
            text = channel_chart.mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                text=alt.Text('Revenue:Q', format='$,.0f')
            )
            
            st.altair_chart(channel_chart + text, use_container_width=True)
        else:
            st.info("No data available")

    st.markdown("---")

    # Data Table Section
    st.markdown("""
    <h2 style='color: #1e293b; margin-bottom: 1.5rem;'>📋 Detailed Order Data</h2>
    """, unsafe_allow_html=True)
    
    df_display = final_kpi.df.copy()
    
    if 'line_total' in df_display.columns:
        df_display['line_total'] = df_display['line_total'].apply(lambda x: f"${x:,.2f}")
    if 'unit_price' in df_display.columns:
        df_display['unit_price'] = df_display['unit_price'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        column_config={
            "order_id": st.column_config.TextColumn("Order ID", width="medium"),
            "order_date": st.column_config.DateColumn("Order Date", width="medium"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "channel_name": st.column_config.TextColumn("Channel", width="small"),
        }
    )

    st.markdown("---")

    # Export Section
    st.sidebar.markdown("""
    <h3 style='color: #f8fafc; margin-top: 1rem; margin-bottom: 1.5rem;'>Export Options</h3>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🖨️ Generate PDF Report", use_container_width=True):
        with st.spinner("⏳ Creating PDF report..."):
            try:
                pdf_bytes = ReportGenerator().export_pdf(final_kpi)
                st.sidebar.success("✅ PDF created successfully!")
                st.sidebar.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="Orders_Analytics_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.sidebar.error(f"❌ Error creating PDF: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; margin-top: 3rem; padding: 1.5rem;'>
        <p>📊 Orders Analytics Dashboard • Built with Streamlit & Python</p>
        <p style='font-size: 0.9rem;'>© 2026 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    import sys
    from streamlit.web import cli as stcli
    if st.runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
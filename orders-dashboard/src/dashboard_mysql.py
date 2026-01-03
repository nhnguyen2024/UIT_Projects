"""
Orders Analytics Dashboard - Streamlit Application
Clean UI with charts and data visualization
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os
import sys
from mysql_connector import MySQLConnector

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ============================================================================
# CUSTOM STYLING
# ============================================================================

def apply_custom_styling():
    """Apply custom CSS styling"""
    if st.session_state.theme == 'dark':
        theme_css = """
        <style>
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
        }
        
        body {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        .main {
            background-color: #0f172a;
        }
        
        [data-testid="stMetric"] {
            background-color: #1e293b;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #334155;
        }
        
        [data-testid="stMetricValue"] {
            color: #00cc99;
        }
        
        .upload-section {
            background-color: #1e293b;
            border: 2px dashed #475569;
            border-radius: 0.5rem;
            padding: 2rem;
            text-align: center;
        }
        </style>
        """
    else:
        theme_css = """
        <style>
        :root {
            --primary-color: #0066cc;
            --secondary-color: #00cc99;
            --accent-color: #ff6b6b;
        }
        
        body {
            background-color: #ffffff;
            color: #1f2937;
        }
        
        .main {
            background-color: #ffffff;
        }
        </style>
        """
    st.markdown(theme_css, unsafe_allow_html=True)

apply_custom_styling()

# ============================================================================
# DATABASE DATA LOADER
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_database_data():
    """Load all orders data from database"""
    try:
        db = MySQLConnector(
            host="localhost",
            user="root",
            password="",  # Empty password
            database="orders_dashboard"
        )
        
        if db.connect():
            # Query to get orders with channel names and totals
            query = """
            SELECT 
                o.order_id,
                c.channel_name,
                o.order_date,
                o.status,
                SUM(i.quantity * i.unit_price) as order_total
            FROM orders o
            JOIN channels c ON o.channel_id = c.channel_id
            LEFT JOIN items i ON o.order_id = i.order_id
            GROUP BY o.order_id, c.channel_name, o.order_date, o.status
            ORDER BY o.order_date DESC
            """
            
            df = db.fetch_df(query)
            db.disconnect()
            
            if df is not None and not df.empty:
                # Ensure data types
                df['order_date'] = pd.to_datetime(df['order_date'])
                df['order_total'] = df['order_total'].fillna(0).astype(float)
                df['status'] = df['status'].str.lower()
                return df
        
        # Fallback to empty dataframe if connection fails
        st.error("Could not connect to database. Please ensure MySQL is running.")
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data from database
orders_df = load_database_data()

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("📊 Orders Analytics Dashboard")
st.markdown("**Monitor sales performance, track order trends, and optimize business decisions**")

# Add refresh button
col_refresh, col_spacer = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Refresh Data", help="Reload data from database"):
        st.cache_data.clear()
        st.rerun()

try:
    if orders_df is not None and not orders_df.empty:
        # Initialize session state for chart filters
        if 'chart_channels' not in st.session_state:
            st.session_state.chart_channels = list(orders_df['channel_name'].unique())
        if 'chart_status' not in st.session_state:
            st.session_state.chart_status = list(orders_df['status'].unique())
        
        # Filter controls - compact
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_channels = st.multiselect(
                "Channels",
                options=orders_df['channel_name'].unique(),
                default=orders_df['channel_name'].unique(),
                key="channel_filter"
            )
            # Use all if nothing selected
            st.session_state.chart_channels = selected_channels if selected_channels else list(orders_df['channel_name'].unique())
        
        with col2:
            selected_status = st.multiselect(
                "Statuses",
                options=orders_df['status'].unique(),
                default=orders_df['status'].unique(),
                key="status_filter"
            )
            # Use all if nothing selected
            st.session_state.chart_status = selected_status if selected_status else list(orders_df['status'].unique())
        
        with col3:
            price_range = st.slider(
                "Price Range ($)",
                min_value=float(orders_df['order_total'].min()),
                max_value=float(orders_df['order_total'].max()),
                value=(float(orders_df['order_total'].min()), float(orders_df['order_total'].max())),
                key="price_filter"
            )
        
        # Apply all filters
        filtered_df = orders_df[
            (orders_df['channel_name'].isin(st.session_state.chart_channels)) &
            (orders_df['status'].isin(st.session_state.chart_status)) &
            (orders_df['order_total'] >= price_range[0]) &
            (orders_df['order_total'] <= price_range[1])
        ]
        
        # Key metrics (compact)
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric("Orders", f"{len(filtered_df):,}")
        
        with kpi_col2:
            completed = len(filtered_df[filtered_df['status'] == 'completed'])
            pct = f"{(completed/len(filtered_df)*100):.0f}%" if len(filtered_df) > 0 else "0%"
            st.metric("Completed", pct)
        
        with kpi_col3:
            total_revenue = filtered_df['order_total'].sum()
            st.metric("Revenue", f"${total_revenue:,.2f}")
        
        with kpi_col4:
            avg_order = filtered_df['order_total'].mean()
            st.metric("Avg Value", f"${avg_order:,.2f}" if len(filtered_df) > 0 else "$0.00")
        
        # Charts and Table side by side
        chart_col, table_col = st.columns([1.3, 1])
        
        with chart_col:
            # Charts stacked - larger
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Orders by Channel")
                channel_data = filtered_df.groupby('channel_name').size().reset_index(name='count')
                
                channel_chart = alt.Chart(channel_data).mark_bar().encode(
                    x='channel_name:N',
                    y='count:Q',
                    color=alt.Color('channel_name:N', scale=alt.Scale(scheme='category10')),
                    opacity=alt.value(0.8)
                ).properties(height=280, width=200).interactive()
                
                st.altair_chart(channel_chart, use_container_width=True)
            
            with col2:
                st.caption("Orders by Status")
                status_data = filtered_df.groupby('status').size().reset_index(name='count')
                
                status_chart = alt.Chart(status_data).mark_arc().encode(
                    theta='count:Q',
                    color=alt.Color('status:N', scale=alt.Scale(scheme='set2'))
                ).properties(height=280, width=200).interactive()
                
                st.altair_chart(status_chart, use_container_width=True)
        
        with table_col:
            st.caption("Orders")
            
            display_cols = ['order_id', 'channel_name', 'status', 'order_total']
            # Calculate dynamic height based on number of rows (30px per row + header)
            table_height = min(max(len(filtered_df) * 30 + 30, 150), 380)
            st.dataframe(
                filtered_df[display_cols],
                use_container_width=True,
                hide_index=True,
                height=table_height
            )
    else:
        st.info("No data available.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #cbd5e1; padding: 1rem;'>
    <small>Orders Analytics Dashboard v2.0 | Clean UI with Charts</small>
</div>
""", unsafe_allow_html=True)

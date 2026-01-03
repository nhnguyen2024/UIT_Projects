"""
Orders Analytics Dashboard - Streamlit Application
Clean UI with charts and data visualization
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os
import tempfile
import base64
from mysql_connector import MySQLConnector
from dashboard_exporter import DashboardExporter, take_dashboard_screenshot
from csv_insert import CSVInserter

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

# ============================================================================
# DATA INPUT SECTION (SIDEBAR)
# ============================================================================

st.sidebar.markdown("""
<h3 style='color: #f8fafc; margin-top: 1rem; margin-bottom: 1.5rem;'>Data Input</h3>
""", unsafe_allow_html=True)

with st.sidebar.expander("Upload & Update", expanded=False):
    st.markdown("Upload your CSV files to update the database:")
    
    up_channels = st.file_uploader("Channels (.csv)", type='csv', key='channels_upload')
    up_orders = st.file_uploader("Orders (.csv)", type='csv', key='orders_upload')
    up_items = st.file_uploader("Items (.csv)", type='csv', key='items_upload')
    
    # Process uploaded files
    if up_channels or up_orders or up_items:
        if st.button("Upload to Database", use_container_width=True):
            with st.spinner("Processing files..."):
                try:
                    inserter = CSVInserter(
                        host="localhost",
                        user="root",
                        password="",  # Empty password
                        database="orders_dashboard"
                    )
                    
                    if not inserter.connect():
                        st.error("Failed to connect to database")
                        st.stop()
                    
                    results = []
                    
                    # Process channels
                    if up_channels:
                        try:
                            df_channels = pd.read_csv(up_channels)
                            success, msg = inserter.insert_channels(df_channels, up_channels.name)
                            results.append(("Channels", success, msg))
                            st.sidebar.info(f"Channels: {msg}" if success else f"Channels: {msg}")
                        except Exception as e:
                            results.append(("Channels", False, str(e)))
                            st.sidebar.error(f"Channels Error: {e}")
                    
                    # Process orders
                    if up_orders:
                        try:
                            df_orders = pd.read_csv(up_orders)
                            success, msg = inserter.insert_orders(df_orders, up_orders.name)
                            results.append(("Orders", success, msg))
                            st.sidebar.info(f"Orders: {msg}" if success else f"Orders: {msg}")
                        except Exception as e:
                            results.append(("Orders", False, str(e)))
                            st.sidebar.error(f"Orders Error: {e}")
                    
                    # Process items
                    if up_items:
                        try:
                            df_items = pd.read_csv(up_items)
                            success, msg = inserter.insert_items(df_items, up_items.name)
                            results.append(("Items", success, msg))
                            st.sidebar.info(f"Items: {msg}" if success else f"Items: {msg}")
                        except Exception as e:
                            results.append(("Items", False, str(e)))
                            st.sidebar.error(f"Items Error: {e}")
                    
                    inserter.disconnect()
                    
                    # Summary
                    all_success = all(r[1] for r in results)
                    if all_success:
                        st.sidebar.success(f"All files processed successfully!")
                        st.success("Upload complete! Please press F5 to refresh and see the new data.")
                    else:
                        st.sidebar.warning("Some files had issues. Check messages above.")
                        
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")

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
        
        /* Header Buttons Styling */
        .header-buttons-container {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
        }
        
        .header-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
        }
        
        .refresh-btn:hover {
            background: linear-gradient(135deg, #0052a3 0%, #003d7a 100%);
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.4);
            transform: translateY(-2px);
        }
        
        .export-btn {
            background: linear-gradient(135deg, #00cc99 0%, #00b380 100%);
            color: white;
        }
        
        .export-btn:hover {
            background: linear-gradient(135deg, #00b380 0%, #009966 100%);
            box-shadow: 0 4px 12px rgba(0, 204, 153, 0.4);
            transform: translateY(-2px);
        }
        
        .export-btn:active {
            transform: translateY(0);
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
        
        .header-buttons-container {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
        }
        
        .header-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
        }
        
        .refresh-btn:hover {
            background: linear-gradient(135deg, #0052a3 0%, #003d7a 100%);
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
            transform: translateY(-2px);
        }
        
        .export-btn {
            background: linear-gradient(135deg, #00cc99 0%, #00b380 100%);
            color: white;
        }
        
        .export-btn:hover {
            background: linear-gradient(135deg, #00b380 0%, #009966 100%);
            box-shadow: 0 4px 12px rgba(0, 204, 153, 0.3);
            transform: translateY(-2px);
        }
        </style>
        """
    st.markdown(f"""
    <style>
    {theme_css}
    </style>
    """, unsafe_allow_html=True)

apply_custom_styling()

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'pdf_filename' not in st.session_state:
    st.session_state.pdf_filename = None
if 'export_triggered' not in st.session_state:
    st.session_state.export_triggered = False

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_database_data(refresh_trigger=0):
    """Load all orders data from database"""
    # refresh_trigger parameter is used to invalidate cache on demand
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
orders_df = load_database_data(st.session_state.refresh_counter)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("Orders Analytics Dashboard")
st.markdown("**Monitor sales performance, track order trends, and optimize business decisions**")

# Create beautiful header buttons in top right
col_spacer, col_export = st.columns([3.8, 0.8])

with col_export:
    if st.button("Export PDF", help="Export as PDF", key="export_pdf_btn", use_container_width=True):
        st.session_state.export_triggered = True

try:
    if orders_df is not None and not orders_df.empty:
        # Initialize saved filter values at the start
        if 'saved_channels' not in st.session_state:
            st.session_state.saved_channels = list(orders_df['channel_name'].unique())
        if 'saved_status' not in st.session_state:
            st.session_state.saved_status = list(orders_df['status'].unique())
        if 'saved_price_range' not in st.session_state:
            st.session_state.saved_price_range = (float(orders_df['order_total'].min()), float(orders_df['order_total'].max()))
        
        # Filter controls - compact
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_channels = st.multiselect(
                "Channels",
                options=orders_df['channel_name'].unique(),
                default=st.session_state.saved_channels,
                key="channel_filter"
            )
            st.session_state.saved_channels = selected_channels if selected_channels else list(orders_df['channel_name'].unique())
        
        with col2:
            selected_status = st.multiselect(
                "Statuses",
                options=orders_df['status'].unique(),
                default=st.session_state.saved_status,
                key="status_filter"
            )
            st.session_state.saved_status = selected_status if selected_status else list(orders_df['status'].unique())
        
        with col3:
            price_range = st.slider(
                "Price Range ($)",
                min_value=float(orders_df['order_total'].min()),
                max_value=float(orders_df['order_total'].max()),
                value=st.session_state.saved_price_range,
                key="price_filter"
            )
            st.session_state.saved_price_range = price_range
        
        # Apply all filters using saved values
        filtered_df = orders_df[
            (orders_df['channel_name'].isin(st.session_state.saved_channels)) &
            (orders_df['status'].isin(st.session_state.saved_status)) &
            (orders_df['order_total'] >= st.session_state.saved_price_range[0]) &
            (orders_df['order_total'] <= st.session_state.saved_price_range[1])
        ]
        
        # Store filtered_df in session state for export
        st.session_state.filtered_df = filtered_df
        
        # Handle PDF export if triggered (with filtered data)
        if st.session_state.export_triggered:
            st.info("Generating PDF...")
            
            try:
                # Use filtered_df from session state
                export_df = st.session_state.get('filtered_df', orders_df)
                
                # Take screenshot
                screenshot_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        screenshot_path = tmp.name
                    success = take_dashboard_screenshot("http://localhost:8501", screenshot_path)
                    if not success or not os.path.exists(screenshot_path):
                        screenshot_path = None
                except Exception as e:
                    screenshot_path = None
                
                # Prepare metrics data FROM FILTERED DF
                total_orders = len(export_df)
                completed = len(export_df[export_df['status'] == 'completed'])
                completed_pct = (completed / total_orders * 100) if total_orders > 0 else 0
                total_revenue = export_df['order_total'].sum()
                avg_order_value = export_df['order_total'].mean() if total_orders > 0 else 0
                
                metrics = {
                    'total_orders': total_orders,
                    'completed_pct': completed_pct,
                    'total_revenue': total_revenue,
                    'avg_order_value': avg_order_value,
                }
                
                # Prepare chart data FROM FILTERED DF
                channel_dist = export_df.groupby('channel_name').size()
                status_dist = export_df.groupby('status').size()
                
                chart_data = {
                    'channel_dist': channel_dist,
                    'status_dist': status_dist,
                }
                
                # Generate PDF with FILTERED DATA
                exporter = DashboardExporter()
                pdf_bytes = exporter.export_dashboard_pdf(metrics, chart_data, export_df, screenshot_path)
                
                if pdf_bytes:
                    pdf_filename = f"Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                    st.success(f"PDF ready! Rows: {len(export_df)} | Size: {len(pdf_bytes) / 1024:.1f} KB")
                else:
                    st.error("PDF generation returned empty data")
                
                # Cleanup
                if screenshot_path and os.path.exists(screenshot_path):
                    try:
                        os.remove(screenshot_path)
                    except:
                        pass
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
            
            # Reset trigger
            st.session_state.export_triggered = False
        
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
        
        st.divider()
        
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

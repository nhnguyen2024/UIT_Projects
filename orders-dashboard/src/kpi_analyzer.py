"""
KPIAnalyzer: Calculate key performance indicators and metrics
"""
import pandas as pd


class KPIAnalyzer:
    """
    Analytics Layer: Calculate KPIs, metrics, and provide filtering
    """
    
    def __init__(self, df):
        """
        Initialize analyzer with data
        
        Args:
            df: DataFrame with order data
        """
        self.df = df

    def get_metrics(self):
        """
        Calculate 5 key business metrics
        
        Returns:
            tuple: (revenue, return_rate, aov, cancel_rate, best_sku)
        """
        if self.df.empty: 
            return 0, 0, 0, 0, "N/A"
        
        valid_orders = self.df[self.df['status'] == 'completed']
        
        # 1. Revenue (completed orders only)
        rev = valid_orders['line_total'].sum()
        
        # 2. Average Order Value (AOV)
        if not valid_orders.empty:
            aov = valid_orders.groupby('order_id')['line_total'].sum().mean()
        else:
            aov = 0

        # 3. Return Rate (returned / total)
        total_qty = self.df['quantity'].sum()
        ret_qty = self.df[self.df['status'] == 'returned']['quantity'].sum()
        ret_rate = (ret_qty / total_qty * 100) if total_qty > 0 else 0

        # 4. Cancellation Rate (cancelled / total unique orders)
        unique = self.df.drop_duplicates(subset=['order_id'])
        cancel_rate = (len(unique[unique['status'] == 'cancelled']) / len(unique) * 100) if len(unique) > 0 else 0
        
        # 5. Top SKU by quantity
        if 'sku' in self.df.columns:
            top_sku = self.df.groupby('sku')['quantity'].sum().sort_values(ascending=False)
            best_sku = f"{top_sku.index[0]} ({top_sku.iloc[0]})" if not top_sku.empty else "N/A"
        else:
            best_sku = "N/A"
        
        return rev, ret_rate, aov, cancel_rate, best_sku

    def get_daily_revenue(self):
        """
        Get daily revenue trend (completed orders only)
        
        Returns:
            pd.Series: Daily revenue indexed by date
        """
        if self.df.empty: 
            return pd.DataFrame()
        valid = self.df[self.df['status'] == 'completed']
        return valid.groupby(valid['order_date'].dt.date)['line_total'].sum()

    def get_channel_dist(self):
        """
        Get revenue distribution by sales channel (completed orders only)
        
        Returns:
            pd.Series: Revenue by channel name
        """
        if self.df.empty: 
            return pd.DataFrame()
        valid = self.df[self.df['status'] == 'completed']
        return valid.groupby('channel_name')['line_total'].sum()

    def filter(self, channel, date_range):
        """
        Filter data by channel and date range
        
        Args:
            channel: Channel name or 'All'
            date_range: [start_date, end_date] or empty list
            
        Returns:
            KPIAnalyzer: New analyzer with filtered data
        """
        temp = self.df.copy()
        if channel != 'All':
            temp = temp[temp['channel_name'] == channel]
        if len(date_range) == 2:
            s, e = date_range
            temp = temp[(temp['order_date'].dt.date >= s) & (temp['order_date'].dt.date <= e)]
        return KPIAnalyzer(temp)

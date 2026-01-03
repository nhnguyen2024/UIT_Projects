"""
DataLoader: Load and manage CSV files with backup functionality
"""
import pandas as pd
import os
from datetime import datetime
import streamlit as st
from .config import BASE_DIR


class DataLoader:
    """Handles CSV file loading, uploading, and backup creation"""
    
    @staticmethod
    def load(uploaded_file, local_path, source_label):
        """
        Load data from either uploaded file or local path
        
        Args:
            uploaded_file: Streamlit uploaded file object (or None)
            local_path: Path to local CSV file
            source_label: Label for logging/UI messages
            
        Returns:
            pd.DataFrame: Loaded data or empty DataFrame
        """
        # --- A. CÓ FILE UPLOAD MỚI ---
        if uploaded_file is not None:
            try:
                # 1. Đọc file
                df_new = pd.read_csv(uploaded_file)
                
                # 2. Backup file cũ
                if os.path.exists(local_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"backup_{timestamp}_{os.path.basename(local_path)}"
                    backup_path = os.path.join(BASE_DIR, backup_name)
                    os.rename(local_path, backup_path)
                    st.toast(f"📦 Đã backup: {backup_name}")

                # 3. Ghi đè file mới
                df_new.to_csv(local_path, index=False)
                st.success(f"✅ Đã cập nhật: {source_label}")
                return df_new
            except Exception as e:
                st.error(f"Lỗi update {source_label}: {e}")
                return pd.DataFrame()
        
        # --- B. DÙNG FILE LOCAL ---
        elif os.path.exists(local_path):
            try:
                return pd.read_csv(local_path)
            except:
                try:
                    return pd.read_csv(local_path, sep=';')
                except Exception as e:
                    st.error(f"Lỗi đọc file: {e}")
                    return pd.DataFrame()
        
        # --- C. KHÔNG CÓ DATA ---
        else:
            st.warning(f"⚠️ Thiếu file '{os.path.basename(local_path)}'.")
            return pd.DataFrame()

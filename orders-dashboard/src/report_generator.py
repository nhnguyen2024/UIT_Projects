"""
ReportGenerator: Generate PDF reports with charts and metrics
"""
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from fpdf import FPDF
from .config import FILE_CONFIG, BASE_DIR

matplotlib.use('Agg')


class ReportGenerator:
    """
    Reporting Layer: Export data to PDF with visualizations and metrics
    """
    
    def export_pdf(self, analyzer):
        """
        Generate PDF report with metrics and charts
        
        Args:
            analyzer: KPIAnalyzer instance with data
            
        Returns:
            bytes: PDF file content
        """
        pdf = FPDF()
        pdf.add_page()
        
        # --- Load Font Tiếng Việt ---
        font_path = FILE_CONFIG["font"]
        has_font = False
        if os.path.exists(font_path):
            try:
                pdf.add_font('Vietnamese', '', font_path, uni=True)
                pdf.set_font("Vietnamese", size=12)
                has_font = True
            except:
                pdf.set_font("Arial", size=12)
        else:
            pdf.set_font("Arial", size=12)

        # --- Header ---
        pdf.cell(0, 10, txt="BÁO CÁO ORDERS DASHBOARD", ln=1, align='C')
        pdf.cell(0, 10, txt=f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='C')
        pdf.ln(10)
        
        # --- Metrics ---
        rev, rate, aov, cancel, best = analyzer.get_metrics()
        
        def write_line(text):
            """Write a line with proper encoding"""
            if has_font:
                pdf.cell(0, 10, txt=text, ln=1)
            else:
                pdf.cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'), ln=1)

        write_line("1. Hiệu suất Kinh doanh:")
        write_line(f"- Tổng Doanh thu: ${rev:,.2f}")
        write_line(f"- Giá trị TB Đơn (AOV): ${aov:,.2f}")
        write_line(f"- Tỷ lệ Hoàn trả: {rate:.2f}%")
        write_line(f"- Tỷ lệ Hủy đơn: {cancel:.2f}%")
        write_line(f"- Sản phẩm Top 1: {best}")
        pdf.ln(5)

        write_line("2. Biểu đồ Xu hướng Doanh thu:")
        
        # --- Daily Revenue Chart ---
        try:
            chart_data = analyzer.get_daily_revenue()
            if not chart_data.empty:
                plt.figure(figsize=(10, 4))
                plt.plot(chart_data.index, chart_data.values, color='#0066cc', marker='o', linewidth=2)
                plt.title("Revenue Trend")
                plt.xlabel("Date")
                plt.ylabel("Revenue ($)")
                plt.grid(True, linestyle='--', alpha=0.5)
                
                temp_img = os.path.join(BASE_DIR, "temp_chart.png")
                plt.savefig(temp_img, bbox_inches='tight', dpi=100)
                plt.close()
                
                pdf.image(temp_img, x=10, w=190)
                if os.path.exists(temp_img): 
                    os.remove(temp_img)
            else:
                write_line("(Không có dữ liệu biểu đồ)")
        except Exception as e:
            write_line(f"(Lỗi vẽ biểu đồ: {str(e)[:50]})")

        pdf.ln(5)
        write_line("3. Tỷ trọng Doanh thu theo Kênh:")

        # --- Channel Distribution Chart ---
        try:
            dist_data = analyzer.get_channel_dist()
            if not dist_data.empty:
                dist_data = dist_data.sort_values(ascending=True)
                plt.figure(figsize=(10, 4))
                bars = plt.barh(dist_data.index, dist_data.values, color='#28a745')
                
                plt.title("Revenue by Channel")
                plt.xlabel("Revenue ($)")
                plt.grid(axis='x', linestyle='--', alpha=0.5)

                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    plt.text(width, bar.get_y() + bar.get_height()/2, 
                             f' ${width:,.0f}', 
                             va='center', ha='left', fontsize=10, color='black')

                temp_img_2 = os.path.join(BASE_DIR, "temp_chart_chn.png")
                plt.savefig(temp_img_2, bbox_inches='tight', dpi=100)
                plt.close() 

                pdf.image(temp_img_2, x=10, w=190)
                if os.path.exists(temp_img_2): 
                    os.remove(temp_img_2)
            else:
                write_line("(Không có dữ liệu kênh)")
        except Exception as e:
            write_line(f"(Lỗi vẽ biểu đồ kênh: {str(e)[:50]})")
            
        return pdf.output(dest='S').encode('latin-1')

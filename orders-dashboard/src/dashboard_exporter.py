"""
DashboardExporter: Export dashboard as PDF with screenshot + complete data table
Uses html2image to capture dashboard, then embeds in PDF with all filtered data
"""
import io
import os
import tempfile
from datetime import datetime
import pandas as pd

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class DashboardExporter:
    """
    Export dashboard to PDF with screenshot and complete data table
    """
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
    
    def export_dashboard_pdf(self, metrics: dict, chart_data: dict, 
                            table_data: pd.DataFrame, screenshot_path: str = None) -> bytes:
        """
        Create PDF with dashboard screenshot and complete filtered data table
        
        Args:
            metrics: Dictionary with: total_orders, completed_pct, total_revenue, avg_order_value
            chart_data: Dictionary with channel_dist and status_dist
            table_data: DataFrame with ALL filtered order data (will show all rows)
            screenshot_path: Path to dashboard screenshot image (optional)
            
        Returns:
            bytes: PDF file content
        """
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        # Title and timestamp
        elements.append(Paragraph("Orders Analytics Dashboard", title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                                 styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))        
        # Add dashboard screenshot if available
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                elements.append(Paragraph("Dashboard Screenshot", heading_style))
                # Scale screenshot to fit page width with proper aspect ratio
                img = RLImage(screenshot_path, width=7*inch, height=5*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.15*inch))
            except Exception as e:
                pass  # Skip if screenshot fails
        
        # Add metrics summary
        elements.append(Paragraph("Key Metrics", heading_style))
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Orders', f"{metrics.get('total_orders', 0):,}"],
            ['Completion Rate', f"{metrics.get('completed_pct', 0):.1f}%"],
            ['Total Revenue', f"${metrics.get('total_revenue', 0):,.2f}"],
            ['Avg Order Value', f"${metrics.get('avg_order_value', 0):,.2f}"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.3*inch, 1.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # Complete Data Table - ALL filtered records on new pages
        if not table_data.empty:
            elements.append(PageBreak())
            elements.append(Paragraph(f"Complete Order Data - {len(table_data)} Records", heading_style))
            
            display_cols = ['order_id', 'channel_name', 'status', 'order_total']
            available_cols = [col for col in display_cols if col in table_data.columns]
            
            if available_cols:
                df_display = table_data[available_cols].copy()
                
                # Convert to list for PDF table
                table_list = [list(df_display.columns)]
                for _, row in df_display.iterrows():
                    row_data = []
                    for col in available_cols:
                        val = row[col]
                        if isinstance(val, float):
                            row_data.append(f"${val:,.2f}")
                        else:
                            row_data.append(str(val)[:18])
                    table_list.append(row_data)
                
                col_widths = [1*inch if col == 'order_total' else 1.05*inch for col in available_cols]
                data_table = Table(table_list, colWidths=col_widths, repeatRows=1)
                
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7.5),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('FONTSIZE', (0, 1), (-1, -1), 6.5),
                    ('TOPPADDING', (0, 1), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ]))
                elements.append(data_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()


def take_dashboard_screenshot(url: str, output_path: str) -> bool:
    """
    Take screenshot of dashboard using Playwright
    
    Args:
        url: Dashboard URL (e.g., http://localhost:8501)
        output_path: Path to save screenshot
        
    Returns:
        bool: True if screenshot successful, False otherwise
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 1400})
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(1000)  # Wait for animations to complete
            page.screenshot(path=output_path, full_page=True)
            browser.close()
        return True
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return False

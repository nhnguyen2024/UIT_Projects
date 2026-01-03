"""
Configuration and constants for Orders Dashboard
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_CONFIG = {
    "web": os.path.join(BASE_DIR, "orders_web.csv"),
    "app": os.path.join(BASE_DIR, "orders_app.csv"),
    "items": os.path.join(BASE_DIR, "items.csv"),
    "channels": os.path.join(BASE_DIR, "channels.csv"),
    "font": os.path.join(BASE_DIR, "Arial.ttf")  
}

"""
Root app runner redirecting to src.ui.app:
Run via: streamlit run app.py
"""
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import *

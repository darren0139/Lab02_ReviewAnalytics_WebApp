import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if testing locally
load_dotenv()

# --- CONFIGURATION & SECURITY GATEKEEPER ---
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
DB_NAME = os.getenv("DB_NAME", "review_history.db")

AVAILABLE_MODELS = [
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-4o-mini",
    "gpt-5.5",
]

if not OPENAI_API_KEY:
    st.error("❌ Configuration Error: OPENAI_API_KEY is missing!")
    st.info("Please add your key to a `.env` file locally or inside Streamlit's Secrets panel on the cloud.")
    st.stop()

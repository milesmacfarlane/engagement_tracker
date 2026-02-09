"""
Google Sheets Integration for Student Engagement Tracker
Allows each user to connect their own Google Sheet for data storage
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json


# Google Sheets API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def get_google_client():
    """
    Get authenticated Google Sheets client using credentials from Streamlit secrets
    
    Returns:
        gspread.Client or None
    """
    try:
        # Check if user has configured their own sheet
        if 'google_sheet_url' in st.session_state and st.session_state.google_sheet_url:
            # Get credentials from Streamlit secrets (service account)
            credentials_dict = st.secrets.get("gcp_service_account", None)
            
            if credentials_dict is None:
                st.error("Google Cloud credentials not configured. Please contact administrator.")
                return None
            
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=SCOPES
            )
            
            return gspread.authorize(credentials)
        
        return None
    
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None


def setup_user_sheet():
    """
    UI for user to connect their own Google Sheet
    """
    st.markdown("### 📊 Connect Your Google Sheet")
    
    st.info("""
    **How this works:**
    1. Create a Google Sheet (or use existing one)
    2. Share it with the service account email
    3. Paste the sheet URL below
    4. Your data will be saved to YOUR sheet
    
    **Each teacher gets their own sheet!**
    """)
    
    # Show service account email if configured
    if 'gcp_service_account' in st.secrets:
        service_email = st.secrets['gcp_service_account'].get('client_email', 'Not configured')
        st.code(service_email, language=None)
        st.caption("⬆️ Share your Google Sheet with this email (Editor access)")
    
    # Input for Google Sheet URL
    sheet_url = st.text_input(
        "Google Sheet URL",
        value=st.session_state.get('google_sheet_url', ''),
        placeholder="https://docs.google.com/spreadsheets/d/...",
        help="Paste the URL of your Google Sheet here"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔗 Connect Sheet", type="primary"):
            if sheet_url:
                # Test connection
                st.session_state.google_sheet_url = sheet_url
                client = get_google_client()
                
                if client:
                    try:
                        # Try to open the sheet
                        sheet = client.open_by_url(sheet_url)
                        st.success(f"✅ Connected to: {sheet.title}")
                        
                        # Initialize worksheets if needed
                        initialize_worksheets(sheet)
                        
                        st.session_state.google_sheets_connected = True
                        st.rerun()
                        
                    except gspread.exceptions.SpreadsheetNotFound:
                        st.error("❌ Sheet not found. Make sure you've shared it with the service account.")
                    except gspread.exceptions.APIError as e:
                        st.error(f"❌ API Error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a Google Sheet URL")
    
    with col2:
        if st.button("❌ Disconnect"):
            st.session_state.google_sheet_url = None
            st.session_state.google_sheets_connected = False
            st.rerun()
    
    # Show current connection status
    if st.session_state.get('google_sheets_connected', False):
        st.success(f"✅ Connected to your Google Sheet")
        st.caption(f"Sheet URL: {st.session_state.google_sheet_url}")


def initialize_worksheets(spreadsheet):
    """
    Create necessary worksheets in the Google Sheet if they don't exist
    
    Args:
        spreadsheet: gspread.Spreadsheet object
    """
    required_sheets = ['students', 'classes', 'observations']
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
    
    for sheet_name in required_sheets:
        if sheet_name not in existing_sheets:
            # Create the worksheet
            spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
            # Add headers
            if sheet_name == 'students':
                headers = ['student_id', 'name', 'primary_class']
            elif sheet_name == 'classes':
                headers = ['class_code', 'class_name']
            elif sheet_name == 'observations':
                headers = ['date', 'class_code', 'student_id', 'measure_name', 'value']
            
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.append_row(headers)


def load_sheet_data(sheet_name):
    """
    Load data from a specific worksheet
    
    Args:
        sheet_name: Name of the worksheet (students, classes, or observations)
    
    Returns:
        pd.DataFrame or None
    """
    if not st.session_state.get('google_sheets_connected', False):
        return None
    
    client = get_google_client()
    if not client:
        return None
    
    try:
        sheet = client.open_by_url(st.session_state.google_sheet_url)
        worksheet = sheet.worksheet(sheet_name)
        
        # Get all values
        data = worksheet.get_all_values()
        
        if len(data) <= 1:
            # Only headers or empty
            headers = data[0] if data else []
            return pd.DataFrame(columns=headers)
        
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        return df
    
    except Exception as e:
        st.error(f"Error loading {sheet_name}: {str(e)}")
        return None


def save_sheet_data(sheet_name, dataframe):
    """
    Save DataFrame to a specific worksheet
    
    Args:
        sheet_name: Name of the worksheet
        dataframe: pandas DataFrame to save
    
    Returns:
        bool: Success status
    """
    if not st.session_state.get('google_sheets_connected', False):
        st.error("Not connected to Google Sheets")
        return False
    
    client = get_google_client()
    if not client:
        return False
    
    try:
        sheet = client.open_by_url(st.session_state.google_sheet_url)
        worksheet = sheet.worksheet(sheet_name)
        
        # Clear existing data
        worksheet.clear()
        
        # Convert DataFrame to list of lists
        data = [dataframe.columns.tolist()] + dataframe.values.tolist()
        
        # Update worksheet
        worksheet.update(data, value_input_option='RAW')
        
        return True
    
    except Exception as e:
        st.error(f"Error saving {sheet_name}: {str(e)}")
        return False


def append_sheet_data(sheet_name, rows):
    """
    Append rows to a worksheet (more efficient than rewriting entire sheet)
    
    Args:
        sheet_name: Name of the worksheet
        rows: List of dictionaries or list of lists
    
    Returns:
        bool: Success status
    """
    if not st.session_state.get('google_sheets_connected', False):
        return False
    
    client = get_google_client()
    if not client:
        return False
    
    try:
        sheet = client.open_by_url(st.session_state.google_sheet_url)
        worksheet = sheet.worksheet(sheet_name)
        
        # Convert dict rows to lists if needed
        if isinstance(rows[0], dict):
            # Get column order from headers
            headers = worksheet.row_values(1)
            rows = [[row.get(h, '') for h in headers] for row in rows]
        
        # Append rows
        worksheet.append_rows(rows)
        
        return True
    
    except Exception as e:
        st.error(f"Error appending to {sheet_name}: {str(e)}")
        return False


def create_template_sheet():
    """
    Create a template Google Sheet that users can copy
    
    Returns:
        str: URL of template sheet
    """
    # This would be a pre-made template sheet that users can "Make a Copy" of
    return "https://docs.google.com/spreadsheets/d/TEMPLATE_ID/copy"


def show_connection_status():
    """
    Show a compact connection status indicator in sidebar
    """
    if st.session_state.get('google_sheets_connected', False):
        st.sidebar.success("📊 Google Sheets Connected")
    else:
        st.sidebar.warning("📊 Not Connected to Google Sheets")
        if st.sidebar.button("Connect Sheet"):
            st.session_state.show_sheet_setup = True

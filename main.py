import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
from datetime import datetime

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB PRO"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🛡️")

# --- 📍 บรรทัดที่ 12: วาง URL ของคุณในเครื่องหมายคำพูดด้านล่างนี้ 📍 ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS: Classic B&W with Neon Hover Effects ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-shadow: 2px 2px 4px #222; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; border-radius: 0px; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; transition: all 0.4s ease; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; box-shadow: 0 0 20px rgba(0, 251, 255, 0.4); background-color: rgba(0, 251, 255, 0.05); }
    button:has(div:contains("SAVE")):hover, button:has(div:contains("CONFIRM")):hover { border-color: #BD00FF !important; color: #BD00FF !important; box-shadow: 0 0 20px rgba(189, 0, 255, 0.4); }
    button[key*="del"]:hover { border-color: #FF003C !important; color: #FF003C !important; box-shadow: 0 0 20px rgba(255, 0, 60, 0.4); }
    button[key*="edit"]:hover { border-color: #FF8A00 !important; color: #FF8A00 !important; box-shadow: 0 0 20px rgba(255, 138, 0, 0.4); }
    [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #222 !important; background-color: #050505 !important; transition: 0.5s; }
    code { color: #00FBFF !important; background-color: #111 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ฟังก์ชันส่ง Discord ---
def send_discord_log(action, detail):
    if DISCORD_WEBHOOK_URL:
        try:
            data = {"embeds": [{"title": f"🔔 {action}", "description": detail, "color": 0x00fbff, "timestamp": datetime.now().isoformat()}]}
            requests.post(DISCORD_WEBHOOK_URL, json=data)
        except: pass

# --- ระบบ Login ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; letter-spacing: 10px;'>🔒 ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            password = st.text_input("ENTER AUTHORIZATION CODE", type="password")
            if st.button("VERIFY SYSTEM"):
                if password == "159357159":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("INVALID AUTHORIZATION")
        return False
    return True

# --- เชื่อมต่อฐานข้อมูล ---
@st.cache_resource
def connect_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            info["private_key"] = info["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        else: creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open("RedM_Account_DB")
        sheet = spreadsheet.get_worksheet(0)
        try: log_sheet = spreadsheet.worksheet("Activity_Logs")
        except: log_sheet = spreadsheet.add_worksheet(title="Activity_Logs", rows="100", cols="2")
        return sheet, log_sheet
    except Exception as e:
        st.error(f"SYSTEM ERROR: {e}"); return None, None

def add_log(log_sheet, action):
    try: log_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action])
    except: pass

# --- Main App ---
if check_password():
    st.markdown("<h1 style='text-align: center;'>REDM ID HUB PRO</h1>", unsafe_allow_html=True)
    st.markdown("---")
    sheet, log_sheet = connect_gsheet()
    if sheet:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        if not df.empty:
            st.markdown("### 📊 SYSTEM OVERVIEW")
            c1, c2, c3 = st.columns(3)
            c1.metric("TOTAL IDS", len(df))
            c2.metric("ACTIVE SERVERS", len(df['Server_Name'].unique()))
            c3.metric("LATEST ENTRY", df.iloc[-1]['In_Game_Name'])
            st.markdown("---")

        with st.expander("➕ REGISTER NEW PROFILE"):
            with st.form("add_new_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("Profile ID")
                    new_email = st.text_input("Email Address")
                    new_pwd = st.text_input("Access Password")
                with c2:
                    new_hex = st.text_input("Steam Hex")
                    new_ig_name = st.text_input("In-Game Identity")
                    new_server = st.text_input("Server Node")
                if st.form_submit_button("SAVE TO DATABASE"):
                    if new_id and new_ig_name:
                        sheet.append_row([new_id, new_email, new_pwd, new_hex, "", "", new_server, new_ig_name, "", ""])
                        add_log(log_sheet, f"REGISTER: {new_ig_name} (ID: {new_id})")
                        send_discord_log("NEW IDENTITY ADDED", f"**Name:** {new_ig_name}\n**Server:** {new_server}")
                        st.success("DATA SECURED")
                        st.rerun()

        if not df.empty:
            search = st.text_input("🔍 FILTER DATABASE")
            f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            for idx, row in f_df.iterrows():
                row_idx = idx + 2
                with st.container(border=True):
                    col_i, col_a = st.columns([3, 1.2])
                    with col_i:
                        st.markdown(f"### {row['In_Game_Name']} <span style='color: #444; font-size: 15px;'>// ID: {row['Profile_ID']}</span>", unsafe_allow_html=True)
                        st.write(f"🌐 **NODE:** {row['Server_Name']}")
                        if st.checkbox(f"DECRYPT", key=f"pw_{idx}"): st.write(f"🔑 `{row['Password']}`")
                    with col_a:
                        st.code(row['Steam_Hex'], language="text")
                        c_e, c_d = st.columns(2)
                        if c_d.button("🗑️", key=f"del_{idx}"):
                            sheet.delete_rows(row_idx)
                            add_log(log_sheet, f"DELETE: {row['In_Game_Name']}")
                            send_discord_log("IDENTITY DELETED", f"**Name:** {row['In_Game_Name']}")
                            st.rerun()
                        if c_e.button("⚙️", key=f"edit_{idx}"): st.session_state[f"ed_{idx}"] = True
                    if st.session_state.get(f"ed_{idx}", False):
                        with st.form(f"fe_{idx}"):
                            u_ig = st.text_input("Name", value=row['In_Game_Name'])
                            u_sv = st.text_input("Server", value=row['Server_Name'])
                            if st.form_submit_button("CONFIRM"):
                                sheet.update_cell(row_idx, 7, u_sv); sheet.update_cell(row_idx, 8, u_ig)
                                add_log(log_sheet, f"EDIT: {u_ig}")
                                st.session_state[f"ed_{idx}"] = False; st.rerun()
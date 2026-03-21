import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB PRO"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🛡️")

# --- Webhook URL เดิมของคุณ ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS: แก้ไขหัวข้อและสี ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-align: center; }
    [data-testid="stMetricValue"] { color: #00FBFF !important; }
    .stButton>button { width: 100%; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; }
    code { color: #00FBFF !important; background-color: #111 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบ Login ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
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
        return client.open("RedM_Account_DB").get_worksheet(0)
    except Exception as e:
        st.error(f"SYSTEM ERROR: {e}"); return None

# --- Main App ---
if check_password():
    # แก้ไขหัวข้อให้แสดงผลสวยงาม
    st.markdown("<h1>REDM ID HUB PRO</h1>", unsafe_allow_html=True)
    sheet = connect_gsheet()
    
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())

        if not df.empty:
            st.markdown("### 📈 Visual Analytics")
            m1, m2, m3 = st.columns([1, 2, 2])
            m1.metric("TOTAL ACCOUNTS", len(df))
            
            # แก้ Error สีแดง โดยใช้ชุดสีมาตรฐาน Plotly
            if 'Server' in df.columns:
                fig_sv = px.pie(df, names='Server', title='แยกตามเซิร์ฟเวอร์', 
                                color_discrete_sequence=px.colors.qualitative.Safe, template="plotly_dark")
                m2.plotly_chart(fig_sv, use_container_width=True)
            
            if 'Profession' in df.columns:
                fig_prof = px.bar(df, x='Profession', title='แยกตามอาชีพ', 
                                  template="plotly_dark", color_discrete_sequence=['#00FBFF'])
                m3.plotly_chart(fig_prof, use_container_width=True)

        # --- ส่วนแสดงข้อมูลและปุ่ม COPY ---
        search = st.text_input("🔍 ค้นหาไอดี")
        f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
        
        for idx, row in f_df.iterrows():
            with st.container(border=True):
                c_info, c_btn = st.columns([4, 1.2])
                with c_info:
                    st.markdown(f"### {row.get('Name_IC', 'N/A')} // {row.get('Server', 'N/A')}")
                    if st.checkbox(f"🔓 เปิดดูข้อมูลรายช่อง", key=f"v_{idx}"):
                        for k, v in row.to_dict().items():
                            if v:
                                col_l, col_v, col_cp = st.columns([1.5, 3, 1])
                                col_l.write(f"**{k}**")
                                col_v.code(str(v), language="text")
                                if col_cp.button("📋 COPY", key=f"cp_{idx}_{k}"):
                                    st.write(f'<script>navigator.clipboard.writeText("{v}")</script>', unsafe_allow_html=True)
                                    st.toast(f"คัดลอก {k} แล้ว!")
                with c_btn:
                    st.code(row.get('Steam_Hex', 'N/A'))
                    if st.button("🗑️ ลบ", key=f"d_{idx}"):
                        sheet.delete_rows(idx + 2); st.rerun()
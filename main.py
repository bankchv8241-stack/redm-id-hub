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

# --- 📍 Webhook URL ของคุณ 📍 ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-shadow: 2px 2px 4px #222; text-align: center; }
    h3 { color: #00FBFF; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 20px; }
    .stTextInput>div>div>input { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; border-radius: 0px; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; font-weight: bold; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; box-shadow: 0 0 20px rgba(0, 251, 255, 0.4); }
    [data-testid="stMetricValue"] { color: #00FBFF !important; font-family: 'Courier New', monospace; }
    [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #222 !important; background-color: #050505 !important; }
    code { color: #00FBFF !important; background-color: #111 !important; border: 1px solid #222 !important; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบ Login ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<br><br><br><h2 style='text-align: center;'>🔒 ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
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
        return sheet
    except Exception as e:
        st.error(f"SYSTEM ERROR: {e}"); return None

# --- Main App ---
if check_password():
    st.markdown("<h1>REDM ID HUB PRO</h1>", unsafe_allow_html=True)
    sheet = connect_gsheet()
    
    if sheet:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        # --- 📊 DASHBOARD SECTION ---
        if not df.empty:
            st.markdown("### 📈 ข้อมูลสรุปภาพรวม (Visual Analytics)")
            m1, m2, m3 = st.columns([1, 2, 2])
            m1.metric("TOTAL ACCOUNTS", len(df))
            
            # กราฟแยกตามเซิร์ฟเวอร์
            if any(c in df.columns for c in ['rm_sv', 'Server']):
                col = 'rm_sv' if 'rm_sv' in df.columns else 'Server'
                sv_counts = df[col].value_counts().reset_index()
                sv_counts.columns = ['Name', 'Count']
                fig_sv = px.pie(sv_counts, values='Count', names='Name', title='เซิร์ฟเวอร์', 
                                color_discrete_sequence=px.colors.sequential.Icefire, template="plotly_dark")
                fig_sv.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250)
                m2.plotly_chart(fig_sv, use_container_width=True)
            
            # กราฟแยกตามอาชีพ
            if any(c in df.columns for c in ['rm_prof', 'Profession']):
                col = 'rm_prof' if 'rm_prof' in df.columns else 'Profession'
                prof_counts = df[col].value_counts().reset_index()
                prof_counts.columns = ['Job', 'Count']
                fig_prof = px.bar(prof_counts, x='Job', y='Count', title='อาชีพ',
                                  color='Count', color_continuous_scale='Icefire', template="plotly_dark")
                fig_prof.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250)
                m3.plotly_chart(fig_prof, use_container_width=True)
            st.markdown("---")

        # --- เพิ่มโปรไฟล์ใหม่ ---
        with st.expander("➕ เพิ่มโปรไฟล์ใหม่ (บันทึกข้อมูลแบบละเอียด)"):
            with st.form("add_form", clear_on_submit=True):
                st.markdown("### 1️⃣ Email & 2️⃣ Steam")
                c1, c2 = st.columns(2)
                m_user = c1.text_input("Email"); m_pass = c2.text_input("Email Pass")
                s_id = c1.text_input("Steam ID"); s_pass = c2.text_input("Steam Pass")
                s_hex = c1.text_input("Steam Hex")
                st.markdown("### 5️⃣ RedM Operations")
                rm_sv = c1.text_input("Server"); rm_ic = c2.text_input("Name IC")
                rm_role = c1.text_input("Role"); rm_prof = c2.text_input("Profession")
                if st.form_submit_button("🔥 บันทึกข้อมูล"):
                    # รวบรวมข้อมูลตามลำดับคอลัมน์ใน Sheet ของคุณ
                    new_row = [m_user, m_pass, s_id, s_pass, "", "", "", s_hex, "", "", "", "", "", "", "", rm_sv, "", "", rm_ic, rm_role, rm_prof]
                    sheet.append_row(new_row)
                    st.success("บันทึกสำเร็จ!"); st.rerun()

        # --- ค้นหาและแสดงผล ---
        if not df.empty:
            search = st.text_input("🔍 ค้นหา (ชื่อ IC / เซิร์ฟ / Steam Hex)")
            f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            
            for idx, row in f_df.iterrows():
                row_dict = row.to_dict()
                with st.container(border=True):
                    ic = row_dict.get('rm_ic') or row_dict.get('Name_IC') or 'N/A'
                    sv = row_dict.get('rm_sv') or row_dict.get('Server') or 'N/A'
                    st.markdown(f"### {ic} // {sv}")
                    if st.checkbox(f"🔓 เปิดดูข้อมูลและคัดลอก", key=f"v_{idx}"):
                        for label, value in row_dict.items():
                            if value:
                                cl1, cl2, cl3 = st.columns([1.5, 3, 1])
                                cl1.write(f"**{label}**")
                                cl2.code(str(value), language="text")
                                if cl3.button("📋 COPY", key=f"cp_{idx}_{label}"):
                                    st.write(f'<script>navigator.clipboard.writeText("{value}")</script>', unsafe_allow_html=True)
                                    st.toast(f"คัดลอก {label} แล้ว!")
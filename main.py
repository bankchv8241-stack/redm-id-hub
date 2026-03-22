import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="REDM ID HUB PRO", layout="wide", page_icon="🛡️")

# --- 📍 Webhook URL ของคุณ ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS: Cyberpunk B&W ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-align: center; color: #00FBFF; }
    h3 { color: #00FBFF; border-bottom: 1px solid #333; padding-bottom: 5px; margin-top: 15px; }
    .stTextInput>div>div>input { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; font-weight: bold; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; box-shadow: 0 0 20px rgba(0, 251, 255, 0.4); }
    code { color: #00FBFF !important; background-color: #111 !important; border: 1px solid #222 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบส่ง Discord Log ---
def send_discord_log(action, ic_name, server):
    if DISCORD_WEBHOOK_URL:
        try:
            payload = {
                "embeds": [{
                    "title": f"🔔 {action}",
                    "description": f"**IC Name:** {ic_name}\n**Server:** {server}\n**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "color": 0x00fbff
                }]
            }
            requests.post(DISCORD_WEBHOOK_URL, json=payload)
        except: pass

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
    except: return None

# --- Main App ---
if check_password():
    st.markdown("<h1>REDM ID HUB PRO</h1>", unsafe_allow_html=True)
    sheet = connect_gsheet()
    
    if sheet:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # --- 📊 DASHBOARD ---
        if not df.empty:
            m1, m2, m3 = st.columns([1, 2, 2])
            m1.metric("TOTAL ACCOUNTS", len(df))
            if 'Server' in df.columns:
                fig_sv = px.pie(df, names='Server', title='เซิร์ฟเวอร์ที่เล่น', color_discrete_sequence=px.colors.qualitative.Safe, template="plotly_dark")
                m2.plotly_chart(fig_sv, use_container_width=True)
            if 'Profession' in df.columns:
                fig_prof = px.bar(df, x='Profession', title='สถิติสายอาชีพ', template="plotly_dark", color_discrete_sequence=['#00FBFF'])
                m3.plotly_chart(fig_prof, use_container_width=True)
            st.markdown("---")

        # --- ➕ แบบฟอร์ม 5 ส่วน ---
        with st.expander("➕ เพิ่มโปรไฟล์ใหม่ (บันทึกข้อมูลแบบละเอียด)", expanded=False):
            with st.form("advanced_add_form", clear_on_submit=True):
                st.markdown("### 1️⃣ Email")
                c1, c2 = st.columns(2)
                m_user = c1.text_input("อีเมล (Email)")
                m_pass = c2.text_input("พาสเวิร์ดเมล์ (Pass)")

                st.markdown("### 2️⃣ Steam")
                c3, c4 = st.columns(2)
                s_id = c3.text_input("อีเมลสตรีม (ID)")
                s_pass = c4.text_input("พาสเวิร์ดสตรีม (Pass)")
                s_mail = c3.text_input("อีเมลสำรองสตรีม (Email)")
                s_tel = c4.text_input("เบอร์ลงทะเบียนสตรีม (Tel)")
                s_link = c3.text_input("ลิงก์โปรไฟล์สตรีม")
                s_hex = c4.text_input("Steam Hex")

                st.markdown("### 3️⃣ Discord")
                c5, c6 = st.columns(2)
                d_mail = c5.text_input("อีเมลดิสคอร์ด")
                d_pass = c6.text_input("พาสเวิร์ดดิสคอร์ด")
                d_tel = c5.text_input("เบอร์ลงทะเบียนดิสคอร์ด")
                d_id = c6.text_input("Discord User ID (ID ตัวเลข)")
                d_tag = c5.text_input("Discord Tag (@name)")

                st.markdown("### 4️⃣ Rockstar")
                c7, c8 = st.columns(2)
                rs_mail = c7.text_input("อีเมลร็อกสตาร์")
                rs_pass = c8.text_input("พาสเวิร์ดร็อกสตาร์")

                st.markdown("### 5️⃣ RedM Operations")
                c9, c10 = st.columns(2)
                rm_sv = c9.text_input("ชื่อเซิร์ฟเวอร์ (Server)")
                rm_ip = c10.text_input("ไอพีเซิร์ฟเวอร์ (IP Server)")
                rm_link = c9.text_input("ลิงก์ดิสคอร์ดเซิร์ฟ")
                rm_ic = c10.text_input("ชื่อในเกม (Name IC)")
                rm_role = c9.text_input("โรลที่เล่น (Role)")
                rm_prof = c10.text_input("อาชีพประจำตัว (Profession)")

                if st.form_submit_button("🔥 บันทึกข้อมูลเข้าระบบ"):
                    # ลำดับข้อมูลให้ตรงกับ Google Sheets
                    new_row = [
                        m_user, m_pass,                     # Mail_User, Mail_Pass
                        s_id, s_pass, s_mail, s_tel, s_link, s_hex, # Steam Section
                        d_mail, d_pass, d_tel, d_id, d_tag, # Discord Section
                        rs_mail, rs_pass,                   # Rockstar Section
                        rm_sv, rm_ip, rm_link, rm_ic, rm_role, rm_prof # RedM Section
                    ]
                    sheet.append_row(new_row)
                    send_discord_log("NEW DATA ADDED", rm_ic, rm_sv)
                    st.success(f"บันทึกข้อมูล {rm_ic} สำเร็จ!"); st.rerun()

        # --- 🔍 ค้นหาและคัดลอก ---
        st.markdown("---")
        search = st.text_input("🔍 ค้นหา (ชื่อ IC / เซิร์ฟ / Steam Hex)")
        if not df.empty:
            # ใช้คอลัมน์จริงจาก Sheet ในการกรอง
            f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            
            for idx, row in f_df.iterrows():
                with st.container(border=True):
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        # แสดงหัวข้อเป็น ชื่อ IC และ เซิร์ฟเวอร์
                        ic_name = row.get('Name_IC', 'N/A')
                        server_name = row.get('Server', 'N/A')
                        st.markdown(f"### 👤 {ic_name} // 🌐 {server_name}")
                        
                        if st.checkbox(f"🔓 คลิกเพื่อเปิดดูและคัดลอกข้อมูล", key=f"v_{idx}"):
                            for label, value in row.to_dict().items():
                                if value:
                                    st.write(f"**{label}:**")
                                    st.code(str(value), language="text") 
                    with col_del:
                        if st.button("🗑️ ลบไอดีนี้", key=f"d_{idx}"):
                            sheet.delete_rows(idx + 2)
                            st.warning("ลบข้อมูลเรียบร้อยแล้ว"); st.rerun()
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
from datetime import datetime

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB PRO"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🛡️")

# --- 📍 Webhook URL ของคุณ 📍 ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS: Classic B&W ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-shadow: 2px 2px 4px #222; text-align: center; }
    h3 { color: #00FBFF; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 20px; }
    .stTextInput>div>div>input { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; border-radius: 0px; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; font-weight: bold; transition: all 0.4s ease; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; box-shadow: 0 0 20px rgba(0, 251, 255, 0.4); }
    [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #222 !important; background-color: #050505 !important; }
    code { color: #00FBFF !important; background-color: #111 !important; border: 1px solid #222 !important; }
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
        try: log_sheet = spreadsheet.worksheet("Activity_Logs")
        except: log_sheet = spreadsheet.add_worksheet(title="Activity_Logs", rows="100", cols="2")
        return sheet, log_sheet
    except Exception as e:
        st.error(f"SYSTEM ERROR: {e}"); return None, None

# --- Main App ---
if check_password():
    st.markdown("<h1>REDM ID HUB PRO</h1>")
    sheet, log_sheet = connect_gsheet()
    
    if sheet:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        with st.expander("➕ เพิ่มโปรไฟล์ใหม่ (บันทึกข้อมูลแบบละเอียด)"):
            with st.form("advanced_add_form", clear_on_submit=True):
                st.markdown("### 1️⃣ Email")
                c1, c2 = st.columns(2); m_user = c1.text_input("อีเมล (Email)"); m_pass = c2.text_input("พาสเวิร์ดเมล์ (Pass)")
                st.markdown("### 2️⃣ Steam")
                c3, c4 = st.columns(2); s_id = c3.text_input("ไอดีสตรีม (ID)"); s_pass = c4.text_input("พาสเวิร์ดสตรีม (Pass)")
                s_mail = c3.text_input("อีเมลรองสตรีม"); s_tel = c4.text_input("เบอร์ลงทะเบียนสตรีม"); s_link = c3.text_input("ลิงก์โปรไฟล์สตรีม"); s_hex = c4.text_input("Steam Hex")
                st.markdown("### 3️⃣ Discord")
                c5, c6 = st.columns(2); d_mail = c5.text_input("อีเมลดิสคอร์ด"); d_pass = c6.text_input("พาสเวิร์ดดิสคอร์ด")
                d_tel = c5.text_input("เบอร์ลงทะเบียนดิสคอร์ด"); d_id = c6.text_input("Discord User ID"); d_tag = c5.text_input("Discord Tag")
                st.markdown("### 4️⃣ Rockstar")
                c7, c8 = st.columns(2); rs_mail = c7.text_input("อีเมลร็อกสตาร์"); rs_pass = c8.text_input("พาสเวิร์ดร็อกสตาร์")
                st.markdown("### 5️⃣ RedM Operations")
                c9, c10 = st.columns(2); rm_sv = c9.text_input("ชื่อเซิร์ฟเวอร์"); rm_ip = c10.text_input("ไอพีเซิร์ฟเวอร์")
                rm_link = c9.text_input("ลิงก์ดิสคอร์ดเซิร์ฟ"); rm_ic = c10.text_input("ชื่อในเกม (Name IC)"); rm_role = c9.text_input("โรลที่เล่น"); rm_prof = c10.text_input("อาชีพประจำตัว")

                if st.form_submit_button("🔥 บันทึกข้อมูลเข้าระบบ"):
                    new_row = [m_user, m_pass, s_id, s_pass, s_mail, s_tel, s_link, s_hex, d_mail, d_pass, d_tel, d_id, d_tag, rs_mail, rs_pass, rm_sv, rm_ip, rm_link, rm_ic, rm_role, rm_prof]
                    sheet.append_row(new_row)
                    log_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"เพิ่มข้อมูล: {rm_ic}"])
                    send_discord_log("NEW IDENTITY", f"**IC:** {rm_ic}\n**Server:** {rm_sv}\n**Role:** {rm_role}")
                    st.success("บันทึกข้อมูลสำเร็จ!"); st.rerun()

        if not df.empty:
            search = st.text_input("🔍 ค้นหา (ชื่อ IC / เซิร์ฟ / Steam Hex)")
            f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            
            for idx, row in f_df.iterrows():
                row_dict = row.to_dict()
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1.2])
                    with col_info:
                        st.markdown(f"### {row_dict.get('Name_IC', 'N/A')} // {row_dict.get('Server', 'N/A')}")
                        st.write(f"🎭 **Role:** {row_dict.get('Role', 'N/A')} | 💼 **Job:** {row_dict.get('Profession', 'N/A')}")
                        
                        # --- ส่วนปุ่มคัดลอกรายช่องข้อมูล ---
                        if st.checkbox(f"🔓 เปิดดูและคัดลอกข้อมูลรายช่อง", key=f"v_{idx}"):
                            st.markdown("---")
                            for key, value in row_dict.items():
                                if value: # แสดงและให้ก๊อปปี้เฉพาะช่องที่มีข้อมูล
                                    c_label, c_val, c_cp = st.columns([1.5, 3, 1])
                                    c_label.markdown(f"**{key}:**")
                                    c_val.code(str(value), language="text")
                                    if c_cp.button("📋 COPY", key=f"cp_{idx}_{key}"):
                                        # ใช้ st.write หรือช่องทางอื่นหาก Streamlit เวอร์ชันคุณยังไม่รองรับ copy_to_clipboard โดยตรง
                                        # แต่ส่วนใหญ่เวอร์ชันล่าสุดจะใช้เทคนิคสร้างช่อง text_area เล็กๆ หรือใช้ JS
                                        st.write(f'<script>navigator.clipboard.writeText("{value}")</script>', unsafe_allow_html=True)
                                        st.toast(f"คัดลอก {key} สำเร็จ!", icon="✅")
                    with col_btn:
                        st.code(row_dict.get('Steam_Hex', 'N/A'))
                        if st.button("🗑️ ลบข้อมูล", key=f"d_{idx}"):
                            sheet.delete_rows(idx + 2)
                            send_discord_log("DELETE", f"ลบข้อมูล: {row_dict.get('Name_IC')}")
                            st.rerun()
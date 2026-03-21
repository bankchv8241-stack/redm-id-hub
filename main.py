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

# --- 📍 Webhook URL ของคุณ ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1485029775729889551/BiNZOKI5QDMYp1IVCTKxrH6hMkfBOeip5lWHTh2y48dbvCzO8I7jX1AtAaVEkAXUZ74j" 

# --- Custom CSS: Cyberpunk B&W ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1 { letter-spacing: 8px; text-transform: uppercase; font-weight: 900; text-shadow: 2px 2px 4px #222; text-align: center; margin-bottom: 25px; }
    h3 { color: #00FBFF; border-bottom: 1px solid #333; padding-bottom: 5px; margin-top: 15px; margin-bottom: 15px; }
    .stTextInput>div>div>input { background-color: #0A0A0A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    .stButton>button { width: 100%; border-radius: 0px; border: 1px solid #FFFFFF; background-color: transparent; color: #FFFFFF; font-weight: bold; transition: all 0.4s ease; }
    .stButton>button:hover { border-color: #00FBFF !important; color: #00FBFF !important; box-shadow: 0 0 20px rgba(0, 251, 255, 0.4); }
    [data-testid="stMetricValue"] { color: #00FBFF !important; }
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
    st.markdown("<h1>REDM ID HUB PRO</h1>", unsafe_allow_html=True)
    sheet, log_sheet = connect_gsheet()
    
    if sheet:
        df = pd.DataFrame(sheet.get_all_records())

        # --- 📊 DASHBOARD SECTION ---
        if not df.empty:
            st.markdown("### 📈 Visual Analytics")
            m1, m2, m3 = st.columns([1, 2, 2])
            m1.metric("TOTAL ACCOUNTS", len(df))
            
            if 'Server' in df.columns:
                fig_sv = px.pie(df, names='Server', title='แยกตามเซิร์ฟเวอร์', 
                                color_discrete_sequence=px.colors.qualitative.Safe, template="plotly_dark")
                fig_sv.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250)
                m2.plotly_chart(fig_sv, use_container_width=True)
            
            if 'Profession' in df.columns:
                fig_prof = px.bar(df, x='Profession', title='แยกตามอาชีพ', 
                                  template="plotly_dark", color_discrete_sequence=['#00FBFF'])
                fig_prof.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250)
                m3.plotly_chart(fig_prof, use_container_width=True)
            st.markdown("---")

        # --- ➕ แบบฟอร์มที่คุณต้องการ (ครบ 5 ส่วน) ---
        with st.expander("➕ เพิ่มโปรไฟล์ใหม่ (บันทึกข้อมูลแบบละเอียด)", expanded=True):
            with st.form("advanced_add_form", clear_on_submit=True):
                # 1. Email Section
                st.markdown("### 1️⃣ Email")
                c1, c2 = st.columns(2)
                m_user = c1.text_input("อีเมล (Email)")
                m_pass = c2.text_input("พาสเวิร์ดเมล์ (Pass)")

                # 2. Steam Section
                st.markdown("### 2️⃣ Steam")
                c3, c4 = st.columns(2)
                s_id = c3.text_input("อีเมลสตรีม (ID)")
                s_pass = c4.text_input("พาสเวิร์ดสตรีม (Pass)")
                s_mail = c3.text_input("อีเมลสำรองสตรีม (Email)")
                s_tel = c4.text_input("เบอร์ลงทะเบียนสตรีม (Tel ถ้ามี)")
                s_link = c3.text_input("ลิงก์โปรไฟล์สตรีม")
                s_hex = c4.text_input("Steam Hex")

                # 3. Discord Section
                st.markdown("### 3️⃣ Discord")
                c5, c6 = st.columns(2)
                d_mail = c5.text_input("อีเมลดิสคอร์ด")
                d_pass = c6.text_input("พาสเวิร์ดดิสคอร์ด")
                d_tel = c5.text_input("เบอร์ลงทะเบียนดิสคอร์ด (ถ้ามี)")
                d_id = c6.text_input("Discord User ID (Copy ID)")
                d_tag = c5.text_input("Discord Tag (@name หรือ name#1234)")

                # 4. Rockstar Section
                st.markdown("### 4️⃣ Rockstar")
                c7, c8 = st.columns(2)
                rs_mail = c7.text_input("อีเมลร็อกสตาร์")
                rs_pass = c8.text_input("พาสเวิร์ดร็อกสตาร์")

                # 5. RedM Section
                st.markdown("### 5️⃣ RedM Operations")
                c9, c10 = st.columns(2)
                rm_sv = c9.text_input("ชื่อเซิร์ฟเวอร์ (Server)")
                rm_ip = c10.text_input("ไอพีเซิร์ฟเวอร์ (IP Server)")
                rm_link = c9.text_input("ลิงก์ดิสคอร์ดเซิร์ฟ")
                rm_ic = st.text_input("ชื่อในเกม (Name IC)") # ปรับให้ยาวขึ้น
                rm_role = c9.text_input("โรลที่เล่น (Role)")
                rm_prof = c10.text_input("อาชีพประจำตัว (Profession)")

                if st.form_submit_button("🔥 บันทึกข้อมูลเข้าระบบ"):
                    # เรียงข้อมูลตามลำดับคอลัมน์ใน Google Sheets ของคุณ
                    new_row = [
                        m_user, m_pass, s_id, s_pass, s_mail, s_tel, s_link, 
                        s_hex, d_id, d_mail, d_pass, d_tel, d_tag, 
                        rs_mail, rs_pass, rm_sv, rm_ip, rm_link, rm_ic, rm_role, rm_prof
                    ]
                    sheet.append_row(new_row)
                    
                    # Log & Discord
                    log_msg = f"เพิ่มข้อมูลสำเร็จ: {rm_ic} ({rm_sv})"
                    log_sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), log_msg])
                    send_discord_log("NEW OPERATIVE REGISTERED", f"**IC Name:** {rm_ic}\n**Server:** {rm_sv}\n**Profession:** {rm_prof}")
                    
                    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!"); st.rerun()

        # --- ส่วนค้นหาและแสดงผล ---
        st.markdown("---")
        if not df.empty:
            search = st.text_input("🔍 ค้นหา (ชื่อ IC / เซิร์ฟ / Steam Hex)")
            f_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df
            
            for idx, row in f_df.iterrows():
                row_dict = row.to_dict()
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1.2])
                    with col_info:
                        st.markdown(f"### {row_dict.get('Name_IC', 'N/A')} // {row_dict.get('Server', 'N/A')}")
                        if st.checkbox(f"🔓 ดูข้อมูลและคัดลอกรายช่อง", key=f"v_{idx}"):
                            for label, value in row_dict.items():
                                if value:
                                    c_lab, c_val, c_cp = st.columns([1.5, 3, 1])
                                    c_lab.write(f"**{label}:**")
                                    c_val.code(str(value), language="text")
                                    if c_cp.button("📋 COPY", key=f"cp_{idx}_{label}"):
                                        st.write(f'<script>navigator.clipboard.writeText("{value}")</script>', unsafe_allow_html=True)
                                        st.toast(f"คัดลอก {label} แล้ว!")
                    with col_btn:
                        st.code(row_dict.get('Steam_Hex', 'N/A'))
                        if st.button("🗑️ ลบข้อมูล", key=f"d_{idx}"):
                            sheet.delete_rows(idx + 2); st.rerun()
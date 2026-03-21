import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🎮")

# --- ระบบ Login ---
def check_password():
    if "password_correct" not in st.session_state:
        st.subheader("🔒 Restricted Access")
        password = st.text_input("Please enter your password", type="password")
        if st.button("Login"):
            if password == "159357159":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
        return False
    return True

# --- ฟังก์ชันเชื่อมต่อ Google Sheets ---
@st.cache_resource
def connect_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"])
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("RedM_Account_DB").get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- เริ่มการทำงานของแอป ---
if check_password():
    st.title(f"🎮 {APP_NAME}")
    st.markdown("---")

    sheet = connect_gsheet()
    if sheet:
        # ดึงข้อมูล
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        # --- ส่วนที่ 1: เพิ่มไอดีใหม่ ---
        with st.expander("➕ เพิ่มไอดีใหม่"):
            with st.form("add_new_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("Profile ID")
                    new_email = st.text_input("Email")
                    new_pwd = st.text_input("Password")
                    new_hex = st.text_input("Steam Hex")
                with c2:
                    new_discord = st.text_input("Discord ID")
                    new_ig_name = st.text_input("ชื่อในเกม")
                    new_server = st.text_input("เซิร์ฟเวอร์")
                    new_note = st.text_area("หมายเหตุ")
                
                if st.form_submit_button("บันทึกข้อมูล"):
                    if new_id and new_ig_name:
                        row = [new_id, new_email, new_pwd, new_hex, new_discord, "", new_server, new_ig_name, "", new_note]
                        sheet.append_row(row)
                        st.success("✅ บันทึกสำเร็จ!")
                        st.rerun()

        st.markdown("---")

        # --- ส่วนที่ 2: แสดงผลและการจัดการ ---
        if not df.empty:
            search = st.text_input("🔍 ค้นหาไอดีหรือเซิร์ฟเวอร์")
            filtered_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df

            for index, row in filtered_df.iterrows():
                row_idx = index + 2
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1.5])
                    with col_info:
                        st.markdown(f"### ID: {row['Profile_ID']} | **{row['In_Game_Name']}**")
                        st.write(f"🌐 **Server:** {row['Server_Name']}")
                        show_pw = st.checkbox(f"Show Password (ID {row['Profile_ID']})", key=f"pw_{index}")
                        pw = row['Password'] if show_pw else "********"
                        st.write(f"📧 {row['Email']} | 🔑 `{pw}`")

                    with col_action:
                        st.write("📋 **Quick Copy**")
                        st.code(row['Steam_Hex'], language="text")
                        st.caption("Steam Hex")
                        
                        c_edit, c_del = st.columns(2)
                        if c_del.button("🗑️ ลบ", key=f"del_{index}", use_container_width=True):
                            sheet.delete_rows(row_idx)
                            st.rerun()
                        if c_edit.button("⚙️ แก้ไข", key=f"edit_{index}", use_container_width=True):
                            st.session_state[f"edit_{index}"] = True

                    if st.session_state.get(f"edit_{index}", False):
                        with st.form(f"f_edit_{index}"):
                            u_ig = st.text_input("ชื่อในเกม", value=row['In_Game_Name'])
                            u_sv = st.text_input("เซิร์ฟเวอร์", value=row['Server_Name'])
                            u_pw = st.text_input("Password", value=row['Password'])
                            if st.form_submit_button("บันทึกแก้ไข"):
                                sheet.update_cell(row_idx, 3, u_pw)
                                sheet.update_cell(row_idx, 7, u_sv)
                                sheet.update_cell(row_idx, 8, u_ig)
                                st.session_state[f"edit_{index}"] = False
                                st.rerun()
        else:
            st.info("No data found.")
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🎮")

# --- Custom CSS สำหรับธีม ขาว-ดำ และ Hover Effect ---
st.markdown("""
    <style>
    /* พื้นหลังและตัวอักษรหลัก */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* ปรับแต่งปุ่ม Login และปุ่มทั่วไป */
    .stButton>button {
        border: 1px solid #ffffff;
        background-color: #000000;
        color: #ffffff;
        transition: 0.3s;
        border-radius: 5px;
    }
    
    /* Hover Effect สีต่างๆ ตามที่คุณต้องการ */
    /* ปุ่มลบ - สีแดง */
    button[key*="del"]:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        box-shadow: 0 0 10px #ff4b4b;
    }
    /* ปุ่มแก้ไข - สีม่วง */
    button[key*="edit"]:hover {
        border-color: #a020f0 !important;
        color: #a020f0 !important;
        box-shadow: 0 0 10px #a020f0;
    }
    /* ปุ่มบันทึก/ยืนยัน - สีฟ้า */
    button[key*="submit"]:hover, button[key*="Login"]:hover {
        border-color: #00fbff !important;
        color: #00fbff !important;
        box-shadow: 0 0 10px #00fbff;
    }
    
    /* การ์ดแสดงข้อมูลไอดี */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #333333 !important;
        background-color: #0a0a0a !important;
        transition: 0.4s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #ffffff !important;
        transform: translateY(-2px);
    }

    /* ตกแต่ง Input Box */
    .stTextInput>div>div>input {
        background-color: #111111;
        color: #ffffff;
        border: 1px solid #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ระบบ Login ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: white;'>🔒 ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            password = st.text_input("ENTER AUTHORIZATION CODE", type="password")
            if st.button("VERIFY"):
                if password == "159357159":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("ACCESS DENIED")
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
    st.markdown("<h1 style='letter-spacing: 5px; text-align: center;'>REDM ID HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>FREELANCE EVENT COORDINATION SYSTEM</p>", unsafe_allow_html=True)
    st.markdown("---")

    sheet = connect_gsheet()
    if sheet:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        # ส่วนเพิ่มไอดีใหม่
        with st.expander("➕ ADD NEW PROFILE"):
            with st.form("add_new_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("Profile ID")
                    new_email = st.text_input("Email")
                    new_pwd = st.text_input("Password")
                    new_hex = st.text_input("Steam Hex")
                with c2:
                    new_discord = st.text_input("Discord ID")
                    new_ig_name = st.text_input("In-Game Name")
                    new_server = st.text_input("Server")
                    new_note = st.text_area("Note")
                
                if st.form_submit_button("SAVE DATA"):
                    if new_id and new_ig_name:
                        row = [new_id, new_email, new_pwd, new_hex, new_discord, "", new_server, new_ig_name, "", new_note]
                        sheet.append_row(row)
                        st.success("DATA SECURED")
                        st.rerun()

        st.markdown("---")

        if not df.empty:
            search = st.text_input("🔍 FILTER BY NAME / SERVER")
            filtered_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df

            for index, row in filtered_df.iterrows():
                row_idx = index + 2
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1.5])
                    with col_info:
                        st.markdown(f"### {row['In_Game_Name']} <span style='color: #555;'>| ID: {row['Profile_ID']}</span>", unsafe_allow_html=True)
                        st.write(f"🌐 **Server:** {row['Server_Name']}")
                        show_pw = st.checkbox(f"Decrypt Password (ID {row['Profile_ID']})", key=f"pw_{index}")
                        pw = row['Password'] if show_pw else "********"
                        st.write(f"📧 {row['Email']} | 🔑 `{pw}`")

                    with col_action:
                        st.code(row['Steam_Hex'], language="text")
                        st.caption("Steam Hex")
                        
                        c_edit, c_del = st.columns(2)
                        if c_del.button("🗑️ DELETE", key=f"del_{index}", use_container_width=True):
                            sheet.delete_rows(row_idx)
                            st.rerun()
                        if c_edit.button("⚙️ EDIT", key=f"edit_{index}", use_container_width=True):
                            st.session_state[f"edit_{index}"] = True

                    if st.session_state.get(f"edit_{index}", False):
                        with st.form(f"f_edit_{index}"):
                            u_ig = st.text_input("Update Name", value=row['In_Game_Name'])
                            u_sv = st.text_input("Update Server", value=row['Server_Name'])
                            u_pw = st.text_input("Update Password", value=row['Password'])
                            if st.form_submit_button("CONFIRM EDIT"):
                                sheet.update_cell(row_idx, 3, u_pw)
                                sheet.update_cell(row_idx, 7, u_sv)
                                sheet.update_cell(row_idx, 8, u_ig)
                                st.session_state[f"edit_{index}"] = False
                                st.rerun()
        else:
            st.info("No data in the vault.")
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🎮")

# --- Custom CSS: Classic B&W with Neon Hover Effects ---
st.markdown("""
    <style>
    /* ตั้งค่าธีมหลักเป็นสีดำและขาว */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    /* ตกแต่ง Header ให้ดูโดดเด่น */
    h1 {
        letter-spacing: 8px;
        text-transform: uppercase;
        font-weight: 900;
        text-shadow: 2px 2px 4px #222;
    }

    /* ปรับแต่ง Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
        transition: 0.3s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FFFFFF !important;
        box-shadow: 0 0 10px #333 !important;
    }

    /* การตั้งค่าปุ่มพื้นฐาน */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        border: 1px solid #FFFFFF;
        background-color: transparent;
        color: #FFFFFF;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.4s ease;
    }

    /* Hover Effects แยกตามประเภทปุ่ม */
    /* ปุ่มทั่วไป / VERIFY - สีฟ้า */
    .stButton>button:hover {
        border-color: #00FBFF !important;
        color: #00FBFF !important;
        box-shadow: 0 0 20px rgba(0, 251, 255, 0.4);
        background-color: rgba(0, 251, 255, 0.05);
    }
    
    /* ปุ่ม SAVE / CONFIRM - สีม่วง (ใช้คีย์เวิร์ดในปุ่ม) */
    button:has(div:contains("SAVE")), button:has(div:contains("CONFIRM")):hover {
        border-color: #BD00FF !important;
        color: #BD00FF !important;
        box-shadow: 0 0 20px rgba(189, 0, 255, 0.4);
    }

    /* ปุ่ม DELETE - สีแดง */
    button[key*="del"]:hover {
        border-color: #FF003C !important;
        color: #FF003C !important;
        box-shadow: 0 0 20px rgba(255, 0, 60, 0.4);
    }

    /* ปุ่ม EDIT - สีส้ม */
    button[key*="edit"]:hover {
        border-color: #FF8A00 !important;
        color: #FF8A00 !important;
        box-shadow: 0 0 20px rgba(255, 138, 0, 0.4);
    }

    /* ตกแต่ง Card / Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #222 !important;
        background-color: #050505 !important;
        transition: 0.5s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #444 !important;
        background-color: #080808 !important;
    }
    
    /* ลบขอบขาวรอบๆ Code Block */
    code {
        color: #00FBFF !important;
        background-color: #111 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
                else:
                    st.error("INVALID AUTHORIZATION")
        return False
    return True

# --- เชื่อมต่อฐานข้อมูล ---
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
        st.error(f"SYSTEM ERROR: {e}")
        return None

# --- Main App ---
if check_password():
    st.markdown("<h1 style='text-align: center;'>REDM ID HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555; letter-spacing: 2px;'>ADVANCED PROFILE MANAGEMENT SYSTEM</p>", unsafe_allow_html=True)
    st.markdown("---")

    sheet = connect_gsheet()
    if sheet:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)

        # เพิ่มไอดีใหม่
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
                        row = [new_id, new_email, new_pwd, new_hex, "", "", new_server, new_ig_name, "", ""]
                        sheet.append_row(row)
                        st.success("DATA SECURED SUCCESSFULLY")
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if not df.empty:
            search = st.text_input("🔍 FILTER DATABASE (NAME / SERVER)")
            filtered_df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)] if search else df

            for index, row in filtered_df.iterrows():
                row_idx = index + 2
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1.2])
                    with col_info:
                        st.markdown(f"### {row['In_Game_Name']} <span style='color: #444; font-size: 15px;'>// ID: {row['Profile_ID']}</span>", unsafe_allow_html=True)
                        st.write(f"🌐 **NODE:** {row['Server_Name']}")
                        show_pw = st.checkbox(f"DECRYPT PASSWORD", key=f"pw_{index}")
                        pw = row['Password'] if show_pw else "********"
                        st.write(f"📧 {row['Email']} | 🔑 `{pw}`")

                    with col_action:
                        st.code(row['Steam_Hex'], language="text")
                        c_edit, c_del = st.columns(2)
                        if c_del.button("🗑️ DEL", key=f"del_{index}"):
                            sheet.delete_rows(row_idx)
                            st.rerun()
                        if c_edit.button("⚙️ EDIT", key=f"edit_{index}"):
                            st.session_state[f"edit_{index}"] = True

                    if st.session_state.get(f"edit_{index}", False):
                        with st.form(f"f_edit_{index}"):
                            u_ig = st.text_input("Update Name", value=row['In_Game_Name'])
                            u_sv = st.text_input("Update Server", value=row['Server_Name'])
                            u_pw = st.text_input("Update Password", value=row['Password'])
                            if st.form_submit_button("CONFIRM UPDATE"):
                                sheet.update_cell(row_idx, 3, u_pw)
                                sheet.update_cell(row_idx, 7, u_sv)
                                sheet.update_cell(row_idx, 8, u_ig)
                                st.session_state[f"edit_{index}"] = False
                                st.rerun()
        else:
            st.info("VAULT IS EMPTY")
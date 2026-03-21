import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB"
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🎮")

# --- ฟังก์ชันเชื่อมต่อ Google Sheets ---
@st.cache_resource
def connect_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # ตรวจสอบว่ารันบน Streamlit Cloud หรือไม่
        if "gcp_service_account" in st.secrets:
            # ดึงข้อมูลจาก Secrets และแปลงเป็น Dictionary
            creds_info = dict(st.secrets["gcp_service_account"])
            # สำคัญ: แก้ไขปัญหาเครื่องหมายเว้นบรรทัดใน Private Key
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        else:
            # สำหรับการรันบนเครื่องคอมพิวเตอร์ (Local)
            creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
            
        client = gspread.authorize(creds)
        # ตรวจสอบชื่อไฟล์ Google Sheets ของคุณให้ตรงกัน
        sheet = client.open("RedM_Account_DB").get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"❌ การเชื่อมต่อผิดพลาด: {e}")
        return None

# --- ฟังก์ชันหลักของระบบ ---
def main():
    st.title(f"🎮 {APP_NAME}")
    st.write("ระบบจัดการไอดีสำหรับการสลับโปรไฟล์เล่น RedM")
    st.markdown("---")

    sheet = connect_gsheet()
    if not sheet:
        st.warning("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดเช็คการตั้งค่า Secrets หรือชื่อไฟล์ Google Sheets")
        return

    # ดึงข้อมูลทั้งหมด
    try:
        all_data = sheet.get_all_records()
        df = pd.DataFrame(all_data)
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
        return

    # --- ส่วนที่ 1: การเพิ่มข้อมูลใหม่ ---
    with st.expander("➕ เพิ่มไอดีใหม่"):
        with st.form("add_new_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("Profile ID (เช่น 01)")
                new_email = st.text_input("Email")
                new_pwd = st.text_input("Password")
                new_hex = st.text_input("Steam Hex")
            with c2:
                new_discord = st.text_input("Discord ID")
                new_ig_name = st.text_input("ชื่อในเกม")
                new_server = st.text_input("เซิร์ฟเวอร์")
                new_note = st.text_area("หมายเหตุ")
            
            if st.form_submit_button("บันทึกข้อมูลใหม่"):
                if new_id and new_ig_name:
                    # โครงสร้าง 10 คอลัมน์ตาม Google Sheets
                    row_to_add = [new_id, new_email, new_pwd, new_hex, new_discord, "", new_server, new_ig_name, "", new_note]
                    sheet.append_row(row_to_add)
                    st.success("✅ บันทึกเรียบร้อย!")
                    st.rerun()
                else:
                    st.error("กรุณากรอก Profile ID และ ชื่อในเกม")

    st.markdown("---")

    # --- ส่วนที่ 2: ค้นหาและแสดงผลแบบการ์ด ---
    if not df.empty:
        search_query = st.text_input("🔍 ค้นหาไอดี (พิมพ์ชื่อในเกม หรือ ชื่อเซิร์ฟเวอร์)")
        
        # กรองข้อมูล
        if search_query:
            filtered_df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
        else:
            filtered_df = df

        for index, row in filtered_df.iterrows():
            # แถวใน Sheet (Header = 1, ข้อมูลเริ่มแถว 2)
            row_index_in_sheet = index + 2 

            with st.container(border=True):
                col_info, col_action = st.columns([3, 1.5])

                with col_info:
                    st.markdown(f"### ID: {row['Profile_ID']} | **{row['In_Game_Name']}**")
                    st.write(f"🌐 **Server:** {row['Server_Name']}")
                    
                    # ส่วนแสดง Password แบบซ่อน
                    show_pw = st.checkbox(f"แสดงรหัสผ่านของไอดี {row['Profile_ID']}", key=f"check_{index}")
                    pw_val = row['Password'] if show_pw else "********"
                    st.write(f"📧 **Email:** {row['Email']} | 🔑 **Pass:** `{pw_val}`")
                    if row.get('Note'):
                        st.caption(f"📝 หมายเหตุ: {row['Note']}")

                with col_action:
                    st.write("📋 **คัดลอกข้อมูล**")
                    st.code(row['Steam_Hex'], language="text")
                    st.caption("Steam Hex")
                    st.code(row['Discord_ID'], language="text")
                    st.caption("Discord ID")

                    # ปุ่มการจัดการ
                    c_edit, c_del = st.columns(2)
                    
                    if c_del.button("🗑️ ลบ", key=f"del_{index}", use_container_width=True):
                        sheet.delete_rows(row_index_in_sheet)
                        st.toast(f"ลบไอดี {row['Profile_ID']} เรียบร้อย")
                        st.rerun()
                    
                    if c_edit.button("⚙️ แก้ไข", key=f"edit_btn_{index}", use_container_width=True):
                        st.session_state[f"edit_mode_{index}"] = True

                # ส่วนการแก้ไขข้อมูล
                if st.session_state.get(f"edit_mode_{index}", False):
                    with st.form(f"edit_form_{index}"):
                        st.write(f"✏️ กำลังแก้ไขโปรไฟล์ ID: {row['Profile_ID']}")
                        up_ig = st.text_input("ชื่อในเกม", value=row['In_Game_Name'])
                        up_server = st.text_input("เซิร์ฟเวอร์", value=row['Server_Name'])
                        up_pwd = st.text_input("Password (ใหม่)", value=row['Password'])
                        
                        btn_c1, btn_c2 = st.columns(2)
                        if btn_c1.form_submit_button("✅ ยืนยันการแก้ไข"):
                            # อัปเดต Column C, G, H (ลำดับที่ 3, 7, 8)
                            sheet.update_cell(row_index_in_sheet, 3, up_pwd)
                            sheet.update_cell(row_index_in_sheet, 7, up_server)
                            sheet.update_cell(row_index_in_sheet, 8, up_ig)
                            st.success("อัปเดตข้อมูลสำเร็จ!")
                            st.session_state[f"edit_mode_{index}"] = False
                            st.rerun()
                        
                        if btn_c2.form_submit_button("❌ ยกเลิก"):
                            st.session_state[f"edit_mode_{index}"] = False
                            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลไอดีในระบบ")

if __name__ == "__main__":
    main()
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- การตั้งค่าหน้าเว็บ ---
APP_NAME = "REDM ID HUB"
st.set_page_config(page_title=APP_NAME, layout="wide")

# --- ฟังก์ชันเชื่อมต่อ Google Sheets ---
def connect_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        # ตรวจสอบว่าชื่อไฟล์ใน Google Sheets ตรงกับคำในวงเล็บนี้
        sheet = client.open("RedM_Account_DB").get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"การเชื่อมต่อผิดพลาด: {e}")
        return None

# --- ฟังก์ชันหลักของระบบ ---
def main():
    st.title(f"🎮 {APP_NAME}")
    st.write("ระบบจัดการไอดีสำหรับการสลับโปรไฟล์เล่น RedM")
    st.markdown("---")

    sheet = connect_gsheet()
    if not sheet:
        return

    # ดึงข้อมูลมาเก็บในรูปแบบ List of Dicts
    all_data = sheet.get_all_records()
    df = pd.DataFrame(all_data)

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
                # คอลัมน์ต้องตรงกับโครงสร้างใน Google Sheets (10 คอลัมน์)
                row_to_add = [new_id, new_email, new_pwd, new_hex, new_discord, "", new_server, new_ig_name, "", new_note]
                sheet.append_row(row_to_add)
                st.success("บันทึกเรียบร้อย!")
                st.rerun()

    st.markdown("---")

    # --- ส่วนที่ 2: ค้นหาและแสดงผลแบบการ์ด (จัดการ แก้ไข/ลบ) ---
    if not df.empty:
        search_query = st.text_input("🔍 ค้นหาไอดี (พิมพ์ชื่อในเกม หรือ ชื่อเซิร์ฟเวอร์)")
        
        # กรองข้อมูลตามคำค้นหา
        filtered_df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]

        for index, row in filtered_df.iterrows():
            # หาเลขแถวที่แท้จริงใน Google Sheets (แถวที่ 1 คือ Header ดังนั้นต้อง +2)
            row_index_in_sheet = index + 2 

            with st.container(border=True):
                col_info, col_action = st.columns([3, 1])

                with col_info:
                    st.markdown(f"### ID: {row['Profile_ID']} | **{row['In_Game_Name']}**")
                    st.write(f"🌐 **Server:** {row['Server_Name']}")
                    
                    # ส่วนแสดง Password แบบซ่อน
                    show_pw = st.checkbox(f"แสดงรหัสผ่านของไอดี {row['Profile_ID']}", key=f"check_{index}")
                    pw_val = row['Password'] if show_pw else "********"
                    st.write(f"📧 **Email:** {row['Email']} | 🔑 **Pass:** `{pw_val}`")
                    st.caption(f"📝 หมายเหตุ: {row['Note']}")

                with col_action:
                    st.write("📋 **คัดลอกข้อมูล**")
                    st.code(row['Steam_Hex'], language="text")
                    st.caption("Steam Hex (คลิกมุมขวาเพื่อ Copy)")
                    st.code(row['Discord_ID'], language="text")
                    st.caption("Discord ID")

                    # ปุ่มแก้ไขและลบ
                    btn_edit, btn_del = st.columns(2)
                    
                    # ส่วนการลบ (Delete)
                    if btn_del.button("🗑️ ลบ", key=f"del_{index}"):
                        sheet.delete_rows(row_index_in_sheet)
                        st.warning(f"ลบไอดี {row['Profile_ID']} แล้ว")
                        st.rerun()
                    
                    # ส่วนการแก้ไข (Update) - เปิด Modal/Expander เล็กๆ
                    if btn_edit.button("⚙️ แก้ไข", key=f"edit_btn_{index}"):
                        st.session_state[f"edit_mode_{index}"] = True

                # ถ้ากดปุ่มแก้ไข ให้โชว์ฟอร์มแก้ไขด้านล่างการ์ดนั้นๆ
                if st.session_state.get(f"edit_mode_{index}", False):
                    with st.form(f"edit_form_{index}"):
                        st.write(f"✏️ กำลังแก้ไขโปรไฟล์ ID: {row['Profile_ID']}")
                        up_ig = st.text_input("ชื่อในเกม", value=row['In_Game_Name'])
                        up_server = st.text_input("เซิร์ฟเวอร์", value=row['Server_Name'])
                        up_pwd = st.text_input("Password (ใหม่)", value=row['Password'])
                        
                        if st.form_submit_button("ยืนยันการแก้ไข"):
                            # อัปเดตทีละช่องใน Sheet (Column B, C, G, H ตามลำดับ)
                            sheet.update_cell(row_index_in_sheet, 3, up_pwd)    # Col C
                            sheet.update_cell(row_index_in_sheet, 7, up_server) # Col G
                            sheet.update_cell(row_index_in_sheet, 8, up_ig)     # Col H
                            st.success("อัปเดตข้อมูลสำเร็จ!")
                            st.session_state[f"edit_mode_{index}"] = False
                            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลไอดีในระบบ")

if __name__ == "__main__":
    main()
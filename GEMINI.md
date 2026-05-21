# Jewelry Image Puller - Project Instructions

โปรเจคนี้เป็นเครื่องมือสำหรับดึงรูปภาพสินค้าจากไดรฟ์ (Local/Network) บนระบบปฏิบัติการ Windows โดยเน้นความเร็ว ความแม่นยำ และรองรับรหัสสินค้าหลากหลายรูปแบบ

## 🏗 Architectural Overview
- **Language:** Python 3.10+
- **GUI:** Tkinter (Custom Dark Theme)
- **Data Handling:** Pandas (Excel Support)
- **Image Processing:** Pillow (Thumbnails for Visual Selection)
- **Deployment:** GitHub Actions + PyInstaller (Windows EXE)

## 🎯 Core Business Logic (Critical)
- **Folder Hierarchy:** ต้องยึดลำดับ `Source Drive` > `{Category}` > `{Category} {Range}` > `{ProductID}.jpg`
- **Range Calculation:** ช่วงรหัสแบ่งทีละ 200 (เช่น 1-200, 201-400)
- **Dual-Search:** ค้นหาไฟล์ภาพจากทั้งรหัสมาตรฐาน (e.g. `R-10501`) และรหัสเก่า (e.g. `TRK-10501`) เสมอ
- **Legacy Prefix Mapping:**
  - TRK -> R, TEK -> E, TPK -> P, TBK -> B, TNK -> N
- **Smart Matching:** หากเจอหลายไฟล์ที่รหัสหลักตรงกันแต่รหัสลูกค้าหรือเวอร์ชันต่างกัน **ห้าม Copy อัตโนมัติ** ต้องใช้ `choose_files_visual` เพื่อให้ผู้ใช้เลือกเสมอ

## 📊 Data & Excel Handling
- **Multi-Sheet Support:** ต้องอนุญาตให้ผู้ใช้เลือก Sheet หากไฟล์ Excel มีมากกว่า 1 ชีต
- **Smart Header Detection:** การดึงข้อมูลจาก Excel ต้องสแกนหาแถวที่มีข้อมูลจริงเพื่อข้ามบรรทัดที่เป็นหัวข้อใหญ่หรือ Merged Cells
- **Data Cleaning:** ลบช่องว่าง (Trim) และข้ามเซลล์ที่ว่างเปล่า (NaN) อัตโนมัติ

## ⚠️ Error Handling & Logging
- **Non-Intrusive Logging:** ในขณะที่โปรแกรมกำลังทำงาน (Pull Process) ห้ามใช้ `messagebox` เด้งขัดจังหวะ ให้เขียนสถานะลงใน **Activity Log** บนหน้าจอแทน
- **Summary Report:** ใช้ `messagebox` สรุปผลลัพธ์ (สำเร็จกี่รายการ/พลาดกี่รายการ) เฉพาะเมื่อจบกระบวนการทั้งหมดแล้วเท่านั้น
- **Missing Report:** หากมีข้อผิดพลาดหรือหาไม่เจอ ให้บันทึกเป็นไฟล์ `.txt` ไว้ในโฟลเดอร์ปลายทางเสมอ

## ⚙️ Configuration & Paths
- **Path Consistency:** เก็บไฟล์ตั้งค่า (Config, Token, History) ไว้ที่ `~/.jewelry_image_puller/` เท่านั้น เพื่อความเป็นระเบียบของระบบ
- **Dynamic Config:** หมวดหมู่สินค้า (Type Mapping) ต้องสามารถแก้ไขได้ผ่านหน้าจอ Categories Manager โดยไม่ต้องแก้โค้ด

## ⚡ Engineering Standards
- **Non-blocking UI:** การค้นหาไฟล์และประมวลผล Excel ต้องทำใน `threading.Thread` เสมอ
- **Caching:** ใช้ `file_cache` เพื่อลดภาระการอ่านแผ่นดิสก์ซ้ำ
- **Windows Compatibility:** 
  - ใช้ `os.path.normpath` และ `os.path.join`
  - ห้ามใช้ Tuple padding ใน Widget constructors

---
*อัปเดตล่าสุด: v1.7 - Professional Operational Rules*

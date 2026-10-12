# แบบรายงานผลการดำเนินงาน Sprint 2

- **ชื่อโปรเจกต์:** Group15 Express Coffee — Smart POS Coffee Terminal
- **รายวิชา:** CP352301 Script Programming (1/2569)
- **Sprint:** Sprint 2 — Back-End Application Development
- **ช่วงส่งงาน:** 25 กันยายน 2569
- **เป้าหมาย:** สร้าง Domain Models, Business Logic Layer และ Data Access Layer

## บทบาทที่สุ่มได้ใน Sprint 2

- **Planner / Architect:** สุกิจตรา โคแสงรักษา — วางแผน Domain Models และ schema
- **Coder:** รพีพรรณ ศรีบุญเรือง — Domain Models และ persistence
- **Coder:** วิยดา มูลกัน — Business Logic และ algorithms
- **Debugger / QA:** สุภกร กงชา — ทดสอบ persistence และ service

## 1. สรุปความก้าวหน้าของงาน

- [x] สร้าง `Drink`, `Member`, `CartItem` และ `Order` พร้อม validation
- [x] สร้าง `JSONManager` สำหรับโหลด บันทึก สำรอง และกู้คืนไฟล์ข้อมูล
- [x] สร้าง `JSONRepository` สำหรับ CRUD และการจัดการข้อมูลในหน่วยความจำ
- [x] เพิ่ม CRUD เมนู/สมาชิก รวมทั้งค้นหา กรอง และเรียงลำดับข้อมูล
- [x] เพิ่มการคำนวณราคา checkout ประวัติออเดอร์ และสรุปยอดขายใน `ShopService`
- [x] บันทึก UML, JSON schema และ Definition of Done ใน `PLAN.md`

## งานเพิ่มเติมจากข้อกำหนด Final Project: API Back-End

- [x] สร้าง self-made mock HTTP API ใน `coffee_pos/api/server.py` โดยใช้ `http.server`
- [x] เพิ่ม `CoffeeAPIClient` ใน `coffee_pos/api/client.py` ใช้ `requests` เรียก GET/POST
- [x] `GET /api/menu` และ `GET /api/orders` คืน JSON จาก `ShopService`
- [x] `POST /api/orders` ตรวจข้อมูลและสร้างออเดอร์ที่บันทึกผ่าน Repository/JSON
- [x] จัดการ malformed JSON, payload ไม่ถูกต้อง, not found, HTTP errors และ timeout
- [x] เพิ่ม API tests และ `api_demo.py` สำหรับสาธิต request/response

## 2. ผลการทดสอบและประกันคุณภาพ

ผลชุดทดสอบที่บันทึกในช่วงทำรายงาน Sprint 2 คือ **62 tests — OK** (ผลปัจจุบันหลังเพิ่ม SQLite coverage ดูใน [Final Sprint](FINAL_SPRINT_REPORT.md)) กรณีด้านล่างเกี่ยวข้องกับ models, JSON persistence และ business logic

| รหัส | สถานการณ์ | ผลที่คาดหวัง | ผลที่บันทึก | สถานะ |
|---|---|---|---|---|
| TC-01 | ไม่มี `menu.json` ตอนเริ่มโปรแกรม | สร้างไฟล์เริ่มต้นและทำงานต่อได้ | สร้างไฟล์ใหม่สำเร็จ | PASSED |
| TC-02 | `menu.json` มี JSON syntax เสีย | สำรองไฟล์และกู้ค่าเริ่มต้น | สำรอง `.bak` และโหลดเมนูเริ่มต้น | PASSED |
| TC-03 | ไฟล์ว่าง ไบนารีขยะ หรือ JSON ไม่ใช่ list | กู้ข้อมูลโดยไม่ทำให้โปรแกรมหยุด | กู้ค่าเริ่มต้นได้ | PASSED |
| TC-04 | มีระเบียนผิดรูปแบบหรือ id ซ้ำ | ข้ามเฉพาะระเบียนเสียและสำรองข้อมูล | เก็บระเบียนถูกต้องและแจ้งจำนวนที่ข้าม | PASSED |
| TC-05 | เขียนไฟล์ไม่สำเร็จ | แจ้ง `DataFileError` และไม่ทำไฟล์เดิมเสีย | ตรงตามคาด | PASSED |
| TC-06 | บันทึกไม่สำเร็จระหว่างเพิ่ม/แก้/ลบ | rollback ค่าใน RAM ให้ตรงกับไฟล์ | กลับเป็นค่าเดิมทุกกรณี | PASSED |
| TC-07 | ค้นหาด้วยค่าว่างหรือ `None` | ปฏิเสธค่าไม่ถูกต้อง | `ValidationError` / UI ถามใหม่ | PASSED |
| TC-08 | กรองราคาด้วยค่าติดลบ กลับช่วง ตัวอักษร หรือ `nan` | ปฏิเสธและแจ้งเตือน | `ValidationError` ทุกกรณี | PASSED |
| TC-09 | ค้นหา/กรอง/เรียงข้อมูล 1,006 รายการ | ให้ผลถูกต้องและทำงานได้รวดเร็ว | 0.09 / 0.07 / 0.22 ms ตามลำดับที่รายงาน | PASSED |

## 3. Retrospective: Wow! & Whoops!

**Wow!**
- แยก Model, Repository และ Service ทำให้กฎธุรกิจไม่ต้องผูกกับการอ่าน/เขียนไฟล์
- JSON เก็บข้อมูลออเดอร์ที่มีรายการย่อยได้ตรงกับโครงสร้างข้อมูลของระบบ
- การสำรองไฟล์และข้ามเฉพาะระเบียนที่เสียช่วยกู้ข้อมูลส่วนที่ยังใช้ได้

**Whoops!**
- การเขียนไฟล์ทุกครั้งที่เปลี่ยนข้อมูลทำให้การเพิ่มข้อมูลจำนวนมากทีละชุดมีต้นทุนเวลา
- คงแนวทาง write-through สำหรับการใช้งานหน้าร้านตามปกติ; หากมี bulk import ควรเพิ่มการบันทึกแบบชุด

## 4. สิ่งที่ต้องทำต่อใน Sprint 3

- เชื่อม CLI เข้ากับเมธอดของ `ShopService`
- ทำให้สถานะใน RAM และไฟล์สอดคล้องกันตลอด flow
- ทดสอบ end-to-end, edge cases และ exception handling ผ่านหน้าจอผู้ใช้

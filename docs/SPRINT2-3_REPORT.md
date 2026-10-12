# รายงาน Sprint 2–3 — Back-End และ Full-Stack Integration

โปรเจกต์: Group15 Express Coffee (Smart POS) · รายวิชา CP352301 Script Programming

## 1. ความคืบหน้า (Sprint Progress Summary)

**Sprint 2 (Back-End)**
- [x] Domain Models: `Drink`, `Member`, `CartItem`, `Order` (+ validation)
- [x] Data Access Layer: `JSONManager` (atomic write, กู้ไฟล์เสีย), `JSONRepository` (write-through + rollback)
- [x] Business Logic: CRUD เมนู/สมาชิก, ค้นหา, กรอง, เรียงลำดับ, คิดราคา, checkout, สรุปยอด
- [x] อัปเดต `PLAN.md` พร้อม UML Class Diagram, Data Schema และประวัติ Refactor

**Sprint 3 (Full-Stack)**
- [x] เชื่อมเมนู CLI จาก Sprint 1 เข้ากับ `ShopService` (Flow สั่งซื้อเดิมครบ)
- [x] เพิ่มเมนูจัดการเมนู / สมาชิก / ประวัติการขาย
- [x] จัดการ State: RAM = ไฟล์เสมอ (เขียนทันที + rollback)
- [x] Exception Handling ทั้งระบบ + ชุดทดสอบ Edge Case 56 รายการ

## 2. Quality Assurance Test Log

รันด้วย `python -m unittest discover -s . -v` → **Ran 56 tests — OK**
(models 7 · JSON/Repository 12 · Service 22 · CLI end-to-end 15)

| รหัส | สถานการณ์ / อินพุต | ผลที่คาดหวัง | ผลจริง | สถานะ |
|---|---|---|---|---|
| TC-01 | ไม่พบ `menu.json` ขณะเปิดโปรแกรม | สร้างไฟล์เริ่มต้นเอง ไม่พัง และแจ้งผู้ใช้ | สร้างไฟล์ใหม่สำเร็จ แสดงข้อความ ℹ ตอนเริ่ม | PASSED |
| TC-02 | `menu.json` เป็น `{ this is not json` | สำรองเป็น `.bak` แล้วกู้ค่าเริ่มต้น | มี `.bak` 1 ไฟล์ เนื้อหาตรงต้นฉบับ, เมนูเริ่มต้น 6 รายการ | PASSED |
| TC-03 | ไฟล์ว่าง / ไบนารีขยะ / JSON เป็น object แทน list | กู้ค่าเริ่มต้นโดยไม่พัง | กู้สำเร็จทุกกรณี | PASSED |
| TC-04 | ในไฟล์มีระเบียนเสีย 6 รายการ (ราคาติดลบ, ขาดฟิลด์, สตริง, null, ตัวเลข, id ซ้ำ) | ข้ามเฉพาะระเบียนเสีย เก็บที่ถูกต้อง + สำรองไฟล์ | เหลือ Latte 1 รายการ แจ้ง "skipped 6" | PASSED |
| TC-05 | เขียนไฟล์ล้มเหลว (disk full / ไม่มีสิทธิ์) | `DataFileError`, ไฟล์เดิมไม่เสีย, ไม่มีไฟล์ `.tmp` ค้าง | ตรงตามคาด | PASSED |
| TC-06 | บันทึกล้มเหลวหลังเพิ่ม/แก้/ลบ | ข้อมูลใน RAM ย้อนกลับเท่ากับไฟล์ | RAM กลับเป็นค่าเดิมทุกกรณี | PASSED |
| TC-07 | ค้นหาด้วยค่าว่าง / ช่องว่าง / `None` | ปฏิเสธพร้อมข้อความ | `ValidationError` / UI ถามใหม่ | PASSED |
| TC-08 | กรองราคา -5 ถึง 100, 100 ถึง 5, `"a"`, `nan` | ปฏิเสธและแจ้งเตือน | `ValidationError` ทุกกรณี | PASSED |
| TC-09 | เรียง/กรอง/ค้นหา 1,006 เมนู | < 50 ms | เรียง 0.22 ms · กรอง 0.07 ms · ค้นหา 0.09 ms | PASSED |
| TC-10 | จำนวน `0`, `-2`, `abc`, `100`, `2.5` | ปฏิเสธ ถามเฉพาะจำนวนใหม่ ไม่ถามขนาด/นมซ้ำ | ถามซ้ำเฉพาะจำนวน | PASSED |
| TC-11 | เงินสด `abc`, `nan`, `inf`, `-5`, `True` | ปฏิเสธ ไม่บันทึกออเดอร์ | ปฏิเสธทั้งหมด ออเดอร์ไม่ถูกบันทึก | PASSED |
| TC-12 | เงินไม่พอ (100 จากยอด 190) | แจ้งขาดอีก ฿90.00 | `shortfall = 90.0` | PASSED |
| TC-13 | สมาชิก 0812345678 ซื้อ 190 บาท | ลด 10% = 19, ยอด 171 | ลด 19.00 · ยอด 171.00 | PASSED |
| TC-14 | เบอร์สมาชิกที่ไม่มีในระบบ | แจ้งแล้วดำเนินการต่อเป็น Guest | แจ้ง "not found. Proceeding as Guest" | PASSED |
| TC-15 | ปิดโปรแกรมแล้วเปิดใหม่ | ออเดอร์/เมนู/สมาชิกยังอยู่, order id ต่อเนื่อง | โหลดครบ, id ถัดไป = 3 | PASSED |
| TC-16 | Ctrl+D / Ctrl+C กลางการสั่งซื้อ | ออกอย่างสุภาพ ไม่มี traceback | ออกพร้อมข้อความลา | PASSED |
| TC-17 | บันทึกออเดอร์ล้มเหลวตอนชำระเงิน | แจ้ง "Order NOT saved" ไม่พัง ไม่บันทึกครึ่งๆ | ตรงตามคาด | PASSED |
| TC-18 | เบอร์สมาชิก `123`, `abcdefghij` ตอนเพิ่มสมาชิก | ถามเบอร์ใหม่ทันที (ไม่ถามช่องอื่นก่อน) | ถามซ้ำเฉพาะเบอร์ | PASSED |
| TC-19 | พิมพ์ `cancel` กลาง flow | ยกเลิกและกลับเมนู ไม่มีออเดอร์ค้าง | ตรงตามคาด | PASSED |

**Mutation check:** ทดลองแก้โค้ดให้ผิด 5 จุด (ส่วนลด, เงื่อนไขเงินไม่พอ, ค้นหา, rollback, ตรวจ `inf`/`nan`)
ชุดทดสอบล้มทุกครั้ง → เทสต์จับความผิดพลาดได้จริง

## 3. รายงานบั๊ก (Observation / Expected / Actual)

| # | Observation (สิ่งที่ทำ) | Expected | Actual (ก่อนแก้) | การแก้ |
|---|---|---|---|---|
| 1 | Sprint 1: ใส่จำนวนแก้วเป็น `0` หลังเลือกขนาด/นม/ความหวานแล้ว | ถามจำนวนใหม่ | โค้ดสั่ง `continue` กลับไปเลือกเมนู ตัวเลือกที่กรอกมาทั้งหมดหาย | ถามเฉพาะ qty วนซ้ำจนถูก |
| 2 | Sprint 1: ใส่เงินสดเป็น `inf` | ปฏิเสธ | ผ่านเงื่อนไข `paid >= total` เงินทอนเป็น `inf`; ส่วน `nan` วนพิมพ์ "Still need nan" | `require_number()` ตรวจ `math.isfinite` |
| 3 | Sprint 1: ปิดโปรแกรมแล้วเปิดใหม่ | ยอดขายเดิมยังอยู่ | `sales_history` หาย (เก็บใน RAM) | บันทึก `orders.json` |
| 4 | Sprint 3: กด Ctrl+D ระหว่างกรอกเงินสด | ออกอย่างสุภาพ | `EOFError` traceback (ค้นพบตอนรันทดสอบ) | ดัก `EOFError`/`KeyboardInterrupt` ที่ลูปหลัก |
| 5 | Sprint 3: เพิ่มสมาชิกโดยพิมพ์เบอร์ผิด | แจ้งผิดทันทีที่ช่องเบอร์ | ระบบถามชื่อและส่วนลดต่อ แล้วฟ้องผิดตอนท้ายต้องกรอกใหม่หมด | ตรวจเบอร์ทันทีและถามซ้ำเฉพาะช่องนั้น |

## 4. Retrospective

**Wow! (ส่วนที่ทำได้ดี)** — ร่างจากผลการทำงานจริง แก้ไขให้ตรงประสบการณ์ของทีมได้
- แยก 3 เลเยอร์ทำให้ทดสอบ Business Logic ได้โดยไม่ต้องมี Terminal และทดสอบ UI ด้วย input จำลองได้ทั้ง flow
- ตัวจัดการไฟล์กู้ได้ทั้งไฟล์หาย ไฟล์เสีย และระเบียนเสีย พร้อมสำรองก่อนเขียนทับเสมอ
- เขียนไฟล์แบบ atomic + rollback ทำให้ข้อมูลใน RAM กับไฟล์ตรงกันเสมอ

**Whoops! (ปัญหาและการ Refactor)**
- ปัญหา: โค้ด Sprint 1 ปน input/คำนวณ/พิมพ์ในฟังก์ชันเดียวกัน และมีบั๊กข้อ 1–3 ข้างบน
  → Refactor เป็น 3 เลเยอร์ ย้ายตัวเลือกและเมนูออกจากโค้ดไปเป็นโมเดล + ไฟล์ JSON
- ปัญหา: การตรวจข้อมูลอยู่ปลายทางอย่างเดียว ทำให้ผู้ใช้เสียเวลากรอกใหม่ (บั๊ก 5)
  → เพิ่มการตรวจทันทีที่ช่องกรอก โดยยังใช้ validator ตัวเดียวกับโมเดล ไม่เขียนซ้ำ
- ข้อแลกเปลี่ยนที่รู้: เขียนไฟล์ทุกครั้งที่ข้อมูลเปลี่ยนทำให้เพิ่มเมนู 1,000 รายการรวดเดียวช้า (~2 วินาที)
  แต่การใช้งานจริงของร้านเพิ่มทีละรายการ จึงยอมรับได้ ถ้าต้องนำเข้าข้อมูลจำนวนมากควรเพิ่ม bulk import

## 5. เนื้อหา Pull Request (คัดลอกไปใช้ได้)

**Title:** Sprint 2–3: 3-layer refactor, JSON persistence, search/filter/sort, full CLI integration

**Summary:** Refactor the single-file POS into models / data_access / services / ui. Add persistent
JSON storage with corruption recovery, CRUD for menu and members, search/filter/sort, order history,
and 56 automated tests.

**Wow!** / **Whoops!** — ตามหัวข้อ 4 ·  **Test Log** — ตามหัวข้อ 2

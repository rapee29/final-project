# 663380359-8 รพีพรรณ ศรีบุญเรือง

## Group15 Express Coffee — Smart POS

**รายวิชา:** CP352301 Script Programming ภาคเรียน 1/2569

**GitHub:** [https://github.com/rapee29/final-project](https://github.com/rapee29/final-project)

## ภาพรวมโครงงาน

Group15 Express Coffee เป็นระบบขายหน้าร้านสำหรับร้านกาแฟ พัฒนาด้วย Python เพื่อช่วยจัดการงานตั้งแต่แสดงเมนู รับคำสั่งซื้อ คำนวณราคาและส่วนลด รับชำระเงิน ไปจนถึงบันทึกออเดอร์และสรุปยอดขาย

ระบบเว็บแบ่งการใช้งานเป็นสองส่วน:

- **User (`/user`):** ค้นหาและเลือกเครื่องดื่ม ปรับขนาดแก้ว ประเภทนม และระดับความหวาน จัดการตะกร้า ใช้ส่วนลดสมาชิก ชำระเงินสด และดูใบเสร็จ
- **Admin (`/admin`):** ดูยอดขายประจำวัน จำนวนออเดอร์ จำนวนแก้วและคำแนะนำจาก Sales Advisor ดูรายการออเดอร์ และเพิ่ม แก้ไข หรือลบเมนู

หน้าแรก (`/`) ใช้เลือกโหมด User หรือ Admin ทั้งสองส่วนเชื่อมกับระบบหลังบ้านและฐานข้อมูล SQLite ชุดเดียวกัน เมื่อ User สร้างออเดอร์สำเร็จ Admin จะเห็นออเดอร์นั้นในหน้าจัดการร้าน

## พัฒนาการแต่ละ Sprint

### Sprint 1 — CLI Foundation

สร้างโปรแกรม CLI สำหรับแสดงเมนูกาแฟ รับออเดอร์หลายรายการ เลือกขนาดแก้ว ประเภทนม และระดับความหวาน คำนวณราคาและส่วนลดสมาชิก รับเงินสด คำนวณเงินทอน และแสดงใบเสร็จ

### Sprint 2 — Back-End Application Development

สร้าง Domain Models ได้แก่ `Drink`, `Member`, `CartItem` และ `Order` พร้อม validation แยก Repository สำหรับจัดการข้อมูลออกจาก `ShopService` ซึ่งดูแลกฎธุรกิจ เช่น คำนวณราคา checkout ประวัติออเดอร์ และสรุปยอดขาย

เพิ่ม CRUD เมนูและสมาชิก การค้นหา กรอง และเรียงลำดับข้อมูล ช่วงนี้ใช้ JSON persistence พร้อมสำรองและกู้คืนข้อมูลเมื่อไฟล์หรือรายการเสีย และเริ่มสร้าง local Coffee POS API

### Sprint 3 — Full-Stack Integration

เชื่อม CLI กับ `ShopService` และ API ให้ flow การขายทำงานต่อเนื่องตั้งแต่รับข้อมูล ตรวจสอบรายการ คำนวณยอด และบันทึกออเดอร์ เพิ่มการจัดการ input ผิดพลาด การยกเลิก และ exception handling

ใช้ write-through และ rollback เพื่อรักษาความสอดคล้องของข้อมูลระหว่างหน่วยความจำกับไฟล์ ทดสอบ end-to-end และ API ทั้งกรณีปกติและกรณีผิดพลาด

### Final Sprint — SQLite, Web POS และ Automation

เปลี่ยนฐานข้อมูลหลักเป็น SQLite สำหรับเมนู สมาชิก และออเดอร์ สร้าง schema อัตโนมัติ และย้ายข้อมูล JSON เดิมเข้าสู่ฐานข้อมูลแบบ transaction

เพิ่มเว็บ POS แบบ responsive และแยกหน้า User/Admin, Admin dashboard และ API สำหรับจัดการเมนู เพิ่ม Sales Advisor ซึ่งใช้กฎจากข้อมูลยอดขายเพื่อแนะนำเมนูขายดีหรือเสนอให้โปรโมตเมนู และใช้ GitHub Actions รัน lint กับชุดทดสอบอัตโนมัติ

## สมาชิกและการหมุนเวียนบทบาท

| สมาชิก | Sprint 1 | Sprint 2 | Sprint 3 | Final Sprint |
|---|---|---|---|---|
| รพีพรรณ ศรีบุญเรือง | Coder — CLI | Debugger / QA — models และ persistence | Coder — API และ error handling | Planner / Release coordinator |
| สุกิจตรา โคแสงรักษา | Planner — CLI | Coder — Domain Models และ schema | Debugger / QA — API client และ integration | Coder — SQLite tests, lint และ CI fixes |
| วิยดา มูลกัน | Debugger / QA — CLI | Coder — Business Logic | Planner / Architect — integration และ demo | Coder — Sales Advisor / automation |
| สุภกร กงชา | Coder — เมนูและ checkout | Planner / Architect — persistence และ service | Coder — CLI/API walkthrough | Debugger / QA — release และ live demo |

สมาชิกแต่ละคนได้ทำ Planner/Architect 1 รอบ, Coder 2 รอบ และ Debugger/QA 1 รอบ ตลอดสี่ช่วงงาน

## โครงสร้างซอฟต์แวร์

ระบบแบ่งเป็นชั้นเพื่อแยกหน้าที่และช่วยให้ทดสอบแต่ละส่วนได้:

1. **Presentation:** เว็บ User, เว็บ Admin และ CLI รับข้อมูลและแสดงผล
2. **API:** HTTP API รับส่ง JSON ระหว่างหน้าเว็บกับระบบหลังบ้าน
3. **Business Logic:** `ShopService` ตรวจสอบข้อมูล คำนวณราคา ส่วนลด และ checkout
4. **Data Access:** `SQLiteRepository` อ่านเขียนข้อมูลผ่าน SQLite; JSON ใช้เป็นแหล่งข้อมูลสำหรับ migration และ fallback

```text
User / Admin Web หรือ CLI
          │
          ▼
     Coffee POS API
          │
          ▼
      ShopService
          │
          ▼
 SQLiteRepository → SQLite
```

## เทคโนโลยีและ API

- Python 3.9 ขึ้นไป, HTML, CSS และ JavaScript
- SQLite เป็นฐานข้อมูลหลัก โดยไม่ต้องติดตั้ง database server
- `http.server` สำหรับ local API server และ `requests` สำหรับ API client
- `unittest` สำหรับชุดทดสอบ, `flake8` สำหรับตรวจรูปแบบโค้ด และ GitHub Actions สำหรับ CI

| Method | Endpoint | การทำงาน |
|---|---|---|
| GET | `/api/menu` | อ่านเมนูสำหรับ User |
| GET | `/api/orders` | อ่านออเดอร์ |
| POST | `/api/orders` | ตรวจข้อมูล คำนวณยอด และสร้างออเดอร์ |
| GET | `/api/summary` | อ่านสรุปยอดและคำแนะนำประจำวัน |
| GET | `/api/admin/summary` | อ่านข้อมูลภาพรวมสำหรับ Admin |
| GET | `/api/admin/menu` | อ่านเมนูเพื่อจัดการ |
| POST | `/api/admin/menu` | เพิ่มเมนู |
| PUT | `/api/admin/menu/{id}` | แก้ไขเมนู |
| DELETE | `/api/admin/menu/{id}` | ลบเมนู |
| GET | `/api/admin/orders` | อ่านออเดอร์สำหรับ Admin |

## ผลการทดสอบ

รายงาน Final Sprint บันทึกผลชุด `unittest` **66 tests ผ่าน** และ `flake8` ผ่าน ครอบคลุม models, JSON/SQLite persistence, migration, services, CLI, API และ Sales Advisor มีการตรวจ migration, CRUD, checkout ผ่าน API, การอ่านข้อมูลหลังเปิด Service ใหม่ และกรณีชำระเงินไม่พอ

หน้าเลือกโหมด หน้า User และหน้า Admin เปิดผ่านเว็บเซิร์ฟเวอร์ได้ อย่างไรก็ตาม ชุด 66 tests เป็นผลที่บันทึกไว้ก่อนเพิ่ม Admin CRUD API จึงยังไม่มี automated tests แยกสำหรับ endpoint เพิ่ม/แก้ไข/ลบเมนู

## วิธีเปิดใช้งาน

ติดตั้ง dependencies และเริ่มเว็บเซิร์ฟเวอร์:

```bash
python3 -m pip install -r requirements.txt
python3 web_app.py
```

เปิด `http://127.0.0.1:8000/` เพื่อเลือก User หรือ Admin หรือเปิด `/user` และ `/admin` โดยตรง ต้องเปิดผ่านเว็บเซิร์ฟเวอร์เพื่อให้หน้าเว็บเรียก API และ SQLite ได้

## ข้อจำกัด

- Admin เป็นโหมดสาธิตในเครื่อง ยังไม่มี login หรือ authorization และ API Admin CRUD ยังไม่มี automated tests แยก
- เซิร์ฟเวอร์ค่าเริ่มต้น bind เฉพาะ `127.0.0.1`; ไม่ควรเปิดให้เข้าถึงจากเครือข่ายหรือใช้จริงก่อนเพิ่มระบบยืนยันตัวตนและกำหนดสิทธิ์
- API เป็น local mock API ที่สร้างสำหรับโครงงาน ไม่ใช่ public API
- Sales Advisor เป็น rule-based automation ไม่ใช่ generative AI

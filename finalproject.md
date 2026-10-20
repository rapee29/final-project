# 663380359-8 รพีพรรณ ศรีบุญเรือง

## สรุปโครงงาน Final Project

### Group15 Express Coffee — Smart POS

**รายวิชา:** CP352301 Script Programming ภาคเรียน 1/2569

**Repository:** [GitHub repository](https://github.com/rapee29/final-project)

## 1. ภาพรวมโครงงาน

Group15 Express Coffee เป็นระบบขายหน้าร้านสำหรับร้านกาแฟ ช่วยให้ผู้ใช้เลือกเครื่องดื่ม ปรับสูตร จัดตะกร้า คำนวณยอด ชำระเงิน และออกใบเสร็จ ขณะเดียวกันผู้ดูแลร้านสามารถตรวจสอบยอดขายและออเดอร์ รวมถึงจัดการเมนูได้

ระบบแบ่งการใช้งานเป็นสองพื้นที่:

- **User:** เลือกและค้นหาเมนู เลือกขนาดแก้ว ประเภทนม และระดับความหวาน เพิ่มสินค้าในตะกร้า ระบุสมาชิกเพื่อรับส่วนลด ชำระเงินสด และดูใบเสร็จ
- **Admin:** ดูยอดขาย จำนวนออเดอร์ จำนวนแก้ว และคำแนะนำจาก Sales Advisor ตรวจสอบออเดอร์ และเพิ่ม แก้ไข หรือลบเมนู

ทั้งสองพื้นที่เรียกใช้ API และฐานข้อมูล SQLite ชุดเดียวกัน เมื่อผู้ใช้สร้างออเดอร์ ระบบจะตรวจสอบข้อมูลและยอดชำระก่อนบันทึก จากนั้น Admin จึงเห็นรายการออเดอร์และยอดขายจากข้อมูลเดียวกัน

## 2. พัฒนาการของระบบ

### Sprint 2 — Back-End Application Development

Sprint 2 สร้างพื้นฐานระบบหลังบ้าน ได้แก่ Domain Models สำหรับเครื่องดื่ม สมาชิก รายการในตะกร้า และออเดอร์ แยกส่วนจัดการข้อมูลออกจากกฎทางธุรกิจ และเพิ่มความสามารถ CRUD สำหรับเมนูและสมาชิก

ระบบเพิ่มการค้นหา กรอง และเรียงลำดับเมนู พร้อม `ShopService` สำหรับคำนวณราคา checkout ส่วนลดสมาชิก ประวัติออเดอร์ และสรุปยอดขาย ช่วงนี้ใช้ JSON สำหรับจัดเก็บข้อมูล พร้อมระบบสำรองและกู้คืนเมื่อพบไฟล์หรือระเบียนที่ผิดรูปแบบ นอกจากนี้ยังเริ่มสร้าง local Coffee POS API สำหรับอ่านเมนูและออเดอร์ รวมถึงสร้างออเดอร์

### Sprint 3 — Full-Stack Application Integration

Sprint 3 เชื่อม CLI เข้ากับ `ShopService` และ API เพื่อให้ขั้นตอนรับออเดอร์ การจัดการเมนูและสมาชิก และการดูยอดขายทำงานร่วมกันได้ ทดสอบ flow ตั้งแต่รับข้อมูล คำนวณราคา ตรวจการชำระเงิน จนถึงบันทึกออเดอร์

เพิ่มการตรวจสอบข้อมูลผิดพลาด การยกเลิก และการออกจากโปรแกรมอย่างสุภาพ รวมถึง write-through และ rollback เพื่อป้องกันข้อมูลในหน่วยความจำกับไฟล์ไม่ตรงกัน API client จัดการข้อผิดพลาดจาก HTTP, JSON และการเชื่อมต่อได้

### Final Sprint — Database, Web POS และ Quality Automation

Final Sprint เปลี่ยนฐานข้อมูลหลักเป็น SQLite สำหรับเมนู สมาชิก และออเดอร์ พร้อมสร้างตารางอัตโนมัติและย้ายข้อมูล JSON เดิมเข้าสู่ฐานข้อมูลแบบ transaction

เพิ่มเว็บ POS แบบ responsive และแยกหน้าเลือกโหมด หน้า User และหน้า Admin โดยหน้าเว็บใช้ API ติดต่อระบบหลังบ้าน ส่วน Admin จัดการเมนูและดูข้อมูลการขายได้ เพิ่ม Sales Advisor ซึ่งแนะนำเมนูขายดีหรือเสนอให้โปรโมตเมนูเมื่อยังไม่มีออเดอร์ และเพิ่ม GitHub Actions สำหรับรัน lint กับชุดทดสอบอัตโนมัติ

## 3. โครงสร้างซอฟต์แวร์

- **Presentation:** เว็บ User, เว็บ Admin และ CLI รับข้อมูลและแสดงผลให้ผู้ใช้
- **API:** HTTP API ภายในเครื่อง รับส่งข้อมูลในรูปแบบ JSON ระหว่างหน้าเว็บกับระบบหลังบ้าน
- **Business Logic:** `ShopService` จัดการ validation, การคำนวณราคา, ส่วนลดสมาชิก, checkout และสรุปยอดขาย
- **Data Access:** `SQLiteRepository` อ่านและเขียนข้อมูลผ่าน SQLite; JSON ใช้เป็นแหล่งข้อมูลเดิมสำหรับ migration และ fallback

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

## 4. เทคโนโลยีและ API

- Python 3.9 ขึ้นไป
- HTML, CSS และ JavaScript สำหรับหน้าเว็บ
- SQLite สำหรับฐานข้อมูลหลัก
- `http.server` สำหรับ local API server และ `requests` สำหรับ API client
- `unittest` สำหรับชุดทดสอบ และ `flake8` สำหรับตรวจคุณภาพโค้ด
- GitHub Actions สำหรับทำ CI เมื่อมีการ push หรือ pull request

API หลักที่ใช้มีดังนี้:

| Method | Endpoint | การทำงาน |
|---|---|---|
| GET | `/api/menu` | อ่านเมนูสำหรับหน้า User |
| GET | `/api/orders` | อ่านออเดอร์ |
| POST | `/api/orders` | ตรวจข้อมูล คำนวณ และบันทึกออเดอร์ |
| GET | `/api/summary` | อ่านสรุปยอดขายและคำแนะนำประจำวัน |
| GET | `/api/admin/menu` | อ่านรายการเมนูในหน้า Admin |
| POST | `/api/admin/menu` | เพิ่มเมนู |
| PUT | `/api/admin/menu/{id}` | แก้ไขเมนู |
| DELETE | `/api/admin/menu/{id}` | ลบเมนู |

## 5. ผลการทดสอบ

รายงาน Final Sprint ระบุว่า:

- ชุด `unittest` ผ่าน **66 tests** ครอบคลุม models, JSON/SQLite persistence, migration, services, CLI, API และ Sales Advisor
- `flake8` ผ่าน
- ทดสอบการย้ายข้อมูล JSON, CRUD, checkout ผ่าน API, การเปิด Service ใหม่แล้วยังอ่านออเดอร์เดิมได้ และกรณีเงินชำระไม่พอแล้วระบบไม่สร้างออเดอร์
- GitHub Actions มี workflow สำหรับตรวจ lint และทดสอบอัตโนมัติ

## 6. วิธีเปิดใช้งาน

ติดตั้ง dependencies แล้วเริ่มเว็บเซิร์ฟเวอร์:

```bash
python3 -m pip install -r requirements.txt
python3 web_app.py
```

เปิด `http://127.0.0.1:8000/` เพื่อเลือก User หรือ Admin โดยตรงสามารถเปิด `/user` หรือ `/admin` ได้ หน้าเว็บต้องเปิดผ่านเซิร์ฟเวอร์เพื่อให้เรียก API และ SQLite ได้

## 7. ขอบเขตและข้อจำกัด

- Admin เป็นโหมดสาธิตภายในเครื่องและยังไม่มีระบบยืนยันตัวตนหรือกำหนดสิทธิ์ ผู้ดูแลจึงไม่ควรเปิดเซิร์ฟเวอร์ให้เข้าถึงจากเครือข่ายหรือใช้งานจริงก่อนเพิ่ม authentication และ authorization
- API เป็น local mock API ที่สร้างสำหรับโครงงาน ไม่ใช่ public API
- Sales Advisor เป็น rule-based automation ที่ใช้ข้อมูลยอดขาย ไม่ใช่ generative AI

## 8. Repository

ดูซอร์สโค้ดและเอกสารประกอบทั้งหมดได้ที่ [Group15 Express Coffee — final-project บน GitHub](https://github.com/rapee29/final-project)

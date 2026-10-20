# Final Sprint — DevOps, CI/CD และ Automation

- **โปรเจกต์:** Group15 Express Coffee — Smart POS
- **รายวิชา:** CP352301 Script Programming (1/2569)
- **เป้าหมาย:** ทำให้การตรวจคุณภาพทำซ้ำได้ สาธิต API และเพิ่ม automation ที่ใช้ข้อมูลยอดขายจริง

## สมาชิกและบทบาทใน Final Sprint

บทบาทช่วงนี้เป็น Sprint ที่สี่ของการหมุนเวียน โดยรพีพรรณรับหน้าที่ Planner และ Release coordinator; เมื่อรวม Sprint 1–3 สมาชิกทุกคนได้ทำ Planner/Architect 1 รอบ, Coder 2 รอบ และ Debugger/QA 1 รอบพอดี

| สมาชิก | บทบาท | งานรับผิดชอบ |
|---|---|---|
| รพีพรรณ ศรีบุญเรือง | Planner / Release coordinator | วางแผนงาน ตรวจ checklist และประสานการส่งมอบ |
| สุกิจตรา โคแสงรักษา | Coder | แก้ไข SQLite tests, lint และ CI ตามผลตรวจ |
| วิยดา มูลกัน | Coder — Sales Advisor / automation | นำเสนอ Sales Advisor และอธิบายเงื่อนไข automation |
| สุภกร กงชา | Debugger / QA | ตรวจ release checklist และซ้อม API walkthrough / Live Demo |

## 1. สิ่งส่งมอบ

| ข้อกำหนด | สิ่งที่ส่งมอบ | สถานะ |
|---|---|---|
| Unit tests | `unittest` ครอบคลุม models, JSON/SQLite persistence, migration, services, CLI, API และ Sales Advisor | ผ่าน 66 tests หลังเพิ่ม SQLite coverage |
| Automated QA / lint | flake8 ใช้ `setup.cfg` และรันใน GitHub Actions | ผ่านในเครื่องหลังเปลี่ยนเป็น SQLite |
| CI/CD | `.github/workflows/ci.yml` รันเมื่อ push และ pull request | GitHub Actions ผ่านสำหรับ commit `6ead4ee` ซึ่งรวม SQLite และเอกสารชุดปัจจุบัน |
| API integration | `requests` client เรียก self-made local mock API: GET menu, GET orders, POST orders | เว็บ production ใช้ `ShopService`/SQLite; `api_demo.py` ใช้ข้อมูลชั่วคราวแบบ JSON เพื่อไม่แตะฐานข้อมูลร้าน |
| SQLite persistence | SQLite schema สำหรับเมนู/สมาชิก/ออเดอร์ และย้ายข้อมูล JSON เดิมแบบ transaction | backend สร้างไฟล์และตารางให้อัตโนมัติ ไม่ต้องติดตั้ง database server |
| Web POS | หน้าเลือกโหมด `/`, หน้า User `/user` สำหรับเลือกเมนู/ปรับสูตร/ชำระเงิน/ใบเสร็จ และหน้า Admin `/admin` สำหรับดูยอดขายและออเดอร์ พร้อม CRUD เมนูผ่าน API; ใช้ SQLite ชุดเดียวกัน | เปิดด้วย `python3 web_app.py` ที่ `http://127.0.0.1:8000`; Admin เป็นเดโม localhost และยังไม่มี login/authorization |
| API error handling | จัดการ timeout, HTTP status, JSON ที่ผิดรูปแบบ และ payload ที่ไม่ถูกต้อง | มี API tests |
| AI / Automation | Sales Advisor แนะนำเมนูขายดีหรือโปรโมตเมนูเมื่อยังไม่มีออเดอร์ โดยใช้ `DailySummary` | ทำงานเป็น rule-based automation ที่อธิบายได้ |
| Documentation | README, PLAN, CHANGELOG, LEARNINGLOG และรายงานแยก Sprint | อัปเดตแล้ว |

### API Endpoints

| Method | Endpoint | ผลลัพธ์ |
|---|---|---|
| GET | `/api/menu` | รายการเครื่องดื่มจาก SQLite ส่งกลับเป็น JSON |
| GET | `/api/orders` | ประวัติออเดอร์จาก SQLite ส่งกลับเป็น JSON |
| POST | `/api/orders` | สร้างและบันทึกออเดอร์ใน SQLite ส่ง JSON กลับพร้อม HTTP 201 |
| GET | `/api/admin/summary` | สรุปยอดขายและคำแนะนำ Sales Advisor สำหรับหน้า Admin |
| GET | `/api/admin/menu` | อ่านรายการเมนูสำหรับจัดการในหน้า Admin |
| POST | `/api/admin/menu` | เพิ่มเมนูใหม่ลง SQLite |
| PUT | `/api/admin/menu/{id}` | แก้ไขชื่อหรือราคาของเมนู |
| DELETE | `/api/admin/menu/{id}` | ลบเมนู |
| GET | `/api/admin/orders` | อ่านออเดอร์สำหรับหน้า Admin |

ใช้ local mock API ตามตัวเลือกที่ข้อกำหนดอนุญาต จึงไม่ต้องพึ่ง API key หรือ external network ระหว่างสาธิต

## 2. ผลการตรวจคุณภาพ

- `./.venv/bin/python -m unittest discover -s tests -v` — **66 tests, OK** (รวม SQLite migration, checkout, API และ persistence)
- `./.venv/bin/flake8 coffee_pos tests main.py api_demo.py` — **ผ่าน**
- SQLite integration tests ยืนยันการย้ายข้อมูล JSON, CRUD, checkout ผ่าน API, เปิด service ใหม่แล้วยังอ่านออเดอร์ได้ และไม่บันทึกออเดอร์เมื่อเงินไม่พอ
- `./.venv/bin/python api_demo.py` — GET เมนู 6 รายการ → POST สร้างออเดอร์ #1 → GET อ่านออเดอร์กลับ 1 รายการ (ใช้ข้อมูลชั่วคราว)
- GitHub Actions: [Coffee POS CI run](https://github.com/rapee29/final-project/actions/runs/38262283731) — **success** สำหรับ commit `6b45690`
- ตรวจเปิดหน้าเลือกโหมด, หน้า User และหน้า Admin ในเดโมเว็บแล้ว; ผล 66 tests ข้างต้นเป็นชุดทดสอบเดิมและยังไม่ครอบคลุม API CRUD เมนูของ Admin ที่เพิ่มภายหลัง

## 3. โครงร่างนำเสนอและ Live Demo ตามเกณฑ์ 5 ส่วน

1. **ปัญหา/สถาปัตยกรรม (20%)** — อธิบายปัญหาร้านกาแฟขนาดเล็กและแสดง UML/โครงสร้าง Presentation, Business Logic, Data Access
2. **Technology Stack (10%)** — Python, `requests`, SQLite, JSON API, `unittest`, flake8 และ GitHub Actions พร้อมเหตุผลที่ใช้ local mock API
3. **Live Demo และการทดสอบ (40%)** — ทำ CRUD, ปิด/เปิดโปรแกรมเพื่อยืนยัน persistence, สาธิต search/filter/sort, ป้อนค่าผิด และรัน `python api_demo.py`
4. **ปัญหาและการ refactor (15%)** — เล่าการแก้ RAM/file consistency, rollback, validation และ edge cases จาก Sprint 1–3
5. **DevOps และ AI/Automation (15%)** — เปิด GitHub Actions run ที่ผ่าน แล้วสาธิต Sales Advisor จากสรุปยอดขาย

## 4. ขอบเขตและข้อจำกัด

- Sales Advisor เป็น rule-based automation ไม่ใช่ generative AI; จัดอยู่ในทางเลือก Automation ของเกณฑ์วิชา และอธิบายเหตุผลได้จากข้อมูลยอดขาย
- API เป็น mock API ภายในเครื่องตามตัวเลือกที่โจทย์อนุญาต ไม่ใช่ public API
- หน้า Admin และ endpoint `/api/admin/*` เป็นเดโมในเครื่อง ไม่มี authentication/authorization; เซิร์ฟเวอร์ค่าเริ่มต้น bind เฉพาะ `127.0.0.1` และไม่ควรเปิดให้เข้าถึงจากเครือข่ายก่อนเพิ่มระบบสิทธิ์
- API Admin CRUD เมนูยังไม่มี automated tests แยก; ควรเพิ่มก่อนนำไปใช้จริง
- GitHub Actions: [Coffee POS CI run](https://github.com/rapee29/final-project/actions/runs/38268080645) — **success** สำหรับ commit `6ead4ee` (รวม SQLite backend, tests และเอกสารที่ส่งล่าสุด)

## 5. Definition of Done

- [x] Unit tests ผ่าน 66 รายการ รวม SQLite integration coverage
- [x] flake8 ผ่าน
- [x] API GET/POST สาธิตครบและจัดการ error cases
- [x] GitHub Actions CI ผ่านสำหรับ commit `6ead4ee`
- [x] Automation แสดงคำแนะนำจากยอดขาย
- [x] เอกสารและบทบาททีมระบุครบใน README, PLAN และรายงานนี้
- [ ] ซ้อมนำเสนอและ Live Demo กับสมาชิกทุกคนก่อนวันนำเสนอ

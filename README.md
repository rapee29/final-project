# ☕ Group15 Express Coffee — Smart POS

ระบบขายหน้าร้านสำหรับร้านกาแฟ พัฒนาด้วย Python สำหรับรายวิชา CP352301 Script Programming ภาคเรียน 1/2569 รองรับการรับออเดอร์ คำนวณราคา รับชำระเงิน ออกใบเสร็จ จัดการข้อมูลร้าน และสรุปยอดขาย

## ขอบเขตโครงงาน

โครงการเริ่มจาก CLI สำหรับสั่งเครื่องดื่มใน Sprint 1 จากนั้นพัฒนาแยกเป็นสองช่วง:

- **Sprint 2 — Back-End:** สร้าง Domain Models, Business Logic และ Data Access เพิ่ม JSON persistence, CRUD, ค้นหา/กรอง/เรียงลำดับ และการกู้คืนเมื่อไฟล์เสีย
- **Sprint 3 — Full-Stack Integration:** เชื่อม CLI เข้ากับ `ShopService`, จัดการ State และความสอดคล้องระหว่าง RAM กับไฟล์ พร้อมทดสอบ Edge Cases และ Exception Handling

## สมาชิกและบทบาท

| สมาชิก | รหัสนักศึกษา |
|---|---|
| นางสาวรพีพรรณ ศรีบุญเรือง | 663380359-8 |
| นางสาวสุกิจตรา โคแสงรักษา | 663380577-8 |
| นางสาววิยดา มูลกัน | 663380573-6 |
| นายสุภกร กงชา | 633021103-2 |

ทีมหมุนเวียนบทบาท Planner / Architect, Coder และ Debugger / QA ตามงานของแต่ละ Sprint

## ฟีเจอร์

- รับออเดอร์หลายรายการ เลือกขนาดแก้ว ประเภทนม และระดับความหวาน
- จัดการสมาชิกและคำนวณส่วนลดสมาชิก 10%
- คำนวณยอด รับชำระเงินสด คำนวณเงินทอน และพิมพ์ใบเสร็จ
- เพิ่ม แก้ไข ลบ และดูเมนูเครื่องดื่มหรือสมาชิก
- ค้นหาเมนูตามชื่อ กรองตามช่วงราคา และเรียงตามชื่อหรือราคา
- ดูประวัติการขาย กรองตามวัน ยอดขาย หรือสมาชิก และเรียงตามเวลา/ยอด
- สรุปยอดขายรายวัน จำนวนออเดอร์ จำนวนแก้ว ส่วนลด รายได้ และเมนูขายดี
- บันทึกข้อมูลลง JSON โดยอัตโนมัติ พร้อมสำรองและกู้คืนเมื่อไฟล์เสีย
- ตรวจสอบข้อมูลผิดพลาด รองรับการยกเลิกด้วย `cancel` และออกอย่างสุภาพเมื่อกด Ctrl+C/Ctrl+D

## เทคโนโลยีและสถาปัตยกรรม

- Python 3.9 ขึ้นไป (พัฒนา/ตรวจสอบบน Python 3.12)
- ใช้ `requests` สำหรับ client ของ self-made Coffee POS API; mock server ใช้ `http.server` จาก standard library
- ใช้ `unittest` สำหรับ unit/API tests และการทดสอบ CLI แบบ end-to-end
- ใช้ JSON เป็นที่เก็บข้อมูลถาวร

```text
main.py
coffee_pos/
├── models/       # Domain models และ validation
├── data_access/  # JSONManager และ JSONRepository
├── services/     # ShopService: business logic
└── ui/           # CoffeeCLI: รับและแสดงผลกับผู้ใช้
tests/            # ชุดทดสอบอัตโนมัติ
data/             # ไฟล์ JSON ที่สร้างเมื่อเริ่มใช้งาน
docs/             # รายงาน Sprint และผลทดสอบ
```

ชั้น UI ติดต่อกับ `ShopService`; Service ใช้ Repository สำหรับอ่าน/เขียนข้อมูล โดย Repository ใช้ `JSONManager` จัดการไฟล์ การบันทึกเป็นแบบ write-through และ rollback เมื่อเขียนไม่สำเร็จ ดู UML, schema และ Definition of Done เพิ่มเติมใน [PLAN.md](PLAN.md)

## ติดตั้งและใช้งาน

ต้องมี Python 3.9 ขึ้นไป

```bash
git clone https://github.com/rapee29/final-project.git
cd final-project
python3 -m pip install -r requirements.txt
python3 main.py
```

### สาธิต API (self-made mock API)

API เป็น HTTP API ภายในเครื่องที่ทำขึ้นสำหรับโครงงาน ไม่ต้องใช้ API key หรือพึ่งบริการภายนอก

| Method | Endpoint | การทำงาน |
|---|---|---|
| GET | `/api/menu` | อ่านรายการเครื่องดื่มจาก `ShopService` |
| GET | `/api/orders` | อ่านประวัติออเดอร์ |
| POST | `/api/orders` | ตรวจสอบ payload, คำนวณราคาและบันทึกออเดอร์ |

รันทดสอบการเรียก GET/POST ผ่าน client ที่ใช้ `requests`:

```bash
python3 api_demo.py
```

สคริปต์ใช้โฟลเดอร์ชั่วคราวและลบข้อมูลสาธิตเมื่อจบการทำงาน

เมนูหลัก: `1` สั่งซื้อ, `2` สรุปยอด, `3` จัดการเมนู, `4` จัดการสมาชิก, `5` ประวัติการขาย, `0` ออก ระหว่างกรอกข้อมูลพิมพ์ `cancel` เพื่อยกเลิกรายการปัจจุบัน

ข้อมูลเริ่มต้นจะถูกสร้างใน `data/` เมื่อเปิดโปรแกรมครั้งแรก สมาชิกตัวอย่างสำหรับทดลองคือ `0812345678` (Somchai) และ `0898765432` (Somsri)

## ทดสอบ

```bash
python3 -m unittest discover -s . -v
```

GitHub Actions ใน `.github/workflows/ci.yml` ติดตั้ง dependencies แล้วรัน flake8 และชุดทดสอบทุกครั้งที่ push หรือเปิด Pull Request

ชุดทดสอบครอบคลุม models, JSON/file I/O, repository, business logic, CLI, API และ Sales Advisor ผลรันล่าสุด **62 tests — OK** ดูรายงานแยกตาม Sprint ใน `docs/SPRINT1_REPORT.md`, `docs/SPRINT2_REPORT.md` และ `docs/SPRINT3_REPORT.md`

## เอกสารประกอบ

- [PLAN.md](PLAN.md) — แผนงาน, UML, schema, DoD และการตัดสินใจออกแบบ
- [docs/SPRINT1_REPORT.md](docs/SPRINT1_REPORT.md) — รายงานรากฐาน CLI และผลการทบทวน Sprint 1
- [docs/SPRINT2_REPORT.md](docs/SPRINT2_REPORT.md) — รายงาน Back-End, models, JSON persistence และ business logic
- [docs/SPRINT3_REPORT.md](docs/SPRINT3_REPORT.md) — รายงาน Full-Stack Integration, API, automation, edge cases และ CI
- [CHANGELOG.md](CHANGELOG.md) — ประวัติการเปลี่ยนแปลงตาม Sprint
- [LEARNINGLOG.md](LEARNINGLOG.md) — บทเรียนที่ได้จากการพัฒนา

## การหมุนเวียนบทบาท Sprint 2–3

สุ่มบทบาทโดยให้แต่ละ Sprint มี Planner/Architect 1 คน, Coder 2 คน และ Debugger/QA 1 คน และกำหนดให้ทุกคนเปลี่ยนบทบาทใน Sprint ถัดไป

| สมาชิก | Sprint 2 | Sprint 3 |
|---|---|---|
| นางสาวรพีพรรณ ศรีบุญเรือง | Planner / Architect | Coder — API client และ integration |
| นางสาวสุกิจตรา โคแสงรักษา | Coder — models และ persistence | Debugger / QA — API และ error cases |
| นางสาววิยดา มูลกัน | Coder — business logic | Planner / Architect — integration plan และ demo |
| นายสุภกร กงชา | Debugger / QA — persistence และ service tests | Coder — CLI/API walkthrough |

บทบาท Coder มีสองคนต่อ Sprint เพื่อรองรับปริมาณงานพัฒนา; ผู้รับผิดชอบแต่ละคนสามารถแบ่งงานย่อยร่วมกันได้

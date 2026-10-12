# ☕ Group15 Express Coffee — Smart POS

ระบบขายหน้าร้านสำหรับร้านกาแฟ พัฒนาด้วย Python สำหรับรายวิชา CP352301 Script Programming ภาคเรียน 1/2569 รองรับการรับออเดอร์ คำนวณราคา รับชำระเงิน ออกใบเสร็จ จัดการข้อมูลร้าน และสรุปยอดขาย

## ขอบเขตโครงงาน

โครงการเริ่มจาก CLI ใน Sprint 1 พัฒนาระบบหลังบ้านและเชื่อมต่อใน Sprint 2–3 แล้วปิดงานด้วย Final Sprint:

- **Sprint 2 — Back-End:** สร้าง Domain Models, Business Logic และ Data Access เพิ่ม persistence, CRUD, ค้นหา/กรอง/เรียงลำดับ และการกู้คืนข้อมูล
- **Sprint 3 — Full-Stack Integration:** เชื่อม CLI เข้ากับ `ShopService`, จัดการ State และความสอดคล้องระหว่าง RAM กับไฟล์ พร้อมทดสอบ Edge Cases และ Exception Handling
- **Final Sprint — DevOps และการส่งมอบ:** เพิ่ม CI ด้วย GitHub Actions, ตรวจคุณภาพ, สาธิต API และสรุป Automation พร้อมเตรียมการนำเสนอ

## สมาชิกและบทบาท

หมุนเวียนบทบาทตลอด Sprint 1, 2, 3 และ Final Sprint ให้สมาชิกทุกคนได้ทำครบทั้ง Planner/Architect, Coder และ Debugger/QA อย่างน้อยหนึ่งครั้ง ในแต่ละ Sprint แบ่งเป็น Planner 1 คน, Coder 2 คน และ Debugger/QA 1 คน

| สมาชิก | รหัสนักศึกษา | Sprint 1 | Sprint 2 | Sprint 3 | Final Sprint |
|---|---|---|---|---|---|
| นางสาวรพีพรรณ ศรีบุญเรือง | 663380359-8 | Planner / เอกสาร | Coder — Domain Models และ persistence | Debugger / QA — API และ error cases | Coder — SQLite backend และ integration |
| นางสาวสุกิจตรา โคแสงรักษา | 663380577-8 | Coder | Planner / Architect — วางแผน models และ schema | Coder — API client และ integration | Debugger / QA — SQLite tests, lint และ CI |
| นางสาววิยดา มูลกัน | 663380573-6 | Debugger / QA | Coder — business logic | Planner / Architect — integration plan และ demo | Coder — Sales Advisor / automation |
| นายสุภกร กงชา | 633021103-2 | Coder | Debugger / QA — persistence และ service tests | Coder — CLI/API walkthrough | Planner / Release coordinator — checklist และประสาน live demo |

สมาชิกแต่ละคนมีบทบาทครบทั้งสามประเภทเมื่อพิจารณาตลอดสี่ช่วงงาน โดย Coder มีสองคนต่อ Sprint เพื่อรองรับปริมาณงานพัฒนา

## ฟีเจอร์

- ใช้งานหน้าร้านผ่านเว็บแบบ responsive: ค้นหา/กรองเมนู ปรับสูตร จัดตะกร้า ชำระเงิน แสดงใบเสร็จ และดูประวัติออเดอร์
- รับออเดอร์หลายรายการ เลือกขนาดแก้ว ประเภทนม และระดับความหวาน
- จัดการสมาชิกและคำนวณส่วนลดสมาชิก 10%
- คำนวณยอด รับชำระเงินสด คำนวณเงินทอน และพิมพ์ใบเสร็จ
- เพิ่ม แก้ไข ลบ และดูเมนูเครื่องดื่มหรือสมาชิก
- ค้นหาเมนูตามชื่อ กรองตามช่วงราคา และเรียงตามชื่อหรือราคา
- ดูประวัติการขาย กรองตามวัน ยอดขาย หรือสมาชิก และเรียงตามเวลา/ยอด
- สรุปยอดขายรายวัน จำนวนออเดอร์ จำนวนแก้ว ส่วนลด รายได้ และเมนูขายดี
- บันทึกเมนู สมาชิก และออเดอร์ลง SQLite พร้อมย้ายข้อมูลเดิมจาก JSON เมื่อเริ่มใช้งานครั้งแรก
- ตรวจสอบข้อมูลผิดพลาด รองรับการยกเลิกด้วย `cancel` และออกอย่างสุภาพเมื่อกด Ctrl+C/Ctrl+D

## เทคโนโลยีและสถาปัตยกรรม

- Python 3.9 ขึ้นไป (พัฒนา/ตรวจสอบบน Python 3.12)
- ใช้ `requests` สำหรับ client ของ self-made Coffee POS API; mock server ใช้ `http.server` จาก standard library
- ใช้ `unittest` สำหรับ unit/API tests และการทดสอบ CLI แบบ end-to-end
- ใช้ SQLite เป็นฐานข้อมูลหลักโดยไม่ต้องติดตั้ง database server; JSON ใช้เป็นแหล่งข้อมูลเดิมสำหรับ migration และโหมด fallback

```text
main.py
coffee_pos/
├── models/       # Domain models และ validation
├── data_access/  # SQLiteDatabase / SQLiteRepository และ JSON repositories สำหรับ fallback
├── services/     # ShopService: business logic
└── ui/           # CoffeeCLI: รับและแสดงผลกับผู้ใช้
tests/            # ชุดทดสอบอัตโนมัติ
data/             # coffee_pos.sqlite3 และ JSON legacy จาก Sprint 2–3 (ถ้ามี)
web/              # เว็บ POS (HTML, CSS, JavaScript)
web_app.py        # จุดเริ่มเว็บและ local API
docs/             # รายงาน Sprint และผลทดสอบ
```

ชั้น UI ติดต่อกับ `ShopService`; production ใช้ SQLite ผ่าน `SQLiteRepository` ส่วน JSON repository ยังใช้กับ fallback และโฟลเดอร์ข้อมูลชั่วคราว การเปิดใช้ SQLite ครั้งแรกจะสร้างตารางและนำเข้าข้อมูล JSON เดิมเฉพาะตารางที่ยังว่าง โดยเก็บไฟล์เดิมไว้ ดู schema และ Definition of Done เพิ่มเติมใน [PLAN.md](PLAN.md)

## ติดตั้งและใช้งาน

ต้องมี Python 3.9 ขึ้นไป

```bash
git clone https://github.com/rapee29/final-project.git
cd final-project
python3 -m pip install -r requirements.txt
python3 main.py
```

SQLite ใช้ไลบรารีมาตรฐานของ Python และไม่ต้องติดตั้งหรือเปิด database server โปรแกรมสร้างไฟล์ `data/coffee_pos.sqlite3` และตารางให้อัตโนมัติ หากต้องการเปลี่ยนตำแหน่งไฟล์ ให้คัดลอก `.env.example` เป็น `.env` แล้วกำหนด `SQLITE_DATABASE`

### ใช้งานผ่าน Jupyter Notebook

ไฟล์ [`notebooks/Sourcecode.ipynb`](notebooks/Sourcecode.ipynb) เป็นทางเข้าใช้งานแอปเวอร์ชันปัจจุบันจาก Notebook โดยอธิบายว่าโค้ดต้นแบบที่ส่งมาแต่ละส่วนถูกย้ายไปยังโมดูลใดในโปรเจกต์แล้ว ไม่ได้นำ CLI รุ่นเก่ามาทับระบบปัจจุบัน เปิด Notebook จากโฟลเดอร์โปรเจกต์ เลือก kernel ที่ติดตั้ง dependencies แล้วรันเซลล์สุดท้ายเพื่อเปิดเมนู POS

### เว็บ POS

โปรเจกต์มีหน้าเว็บสำหรับค้นหาเมนู ปรับขนาด/นม/ความหวาน จัดการตะกร้า คิดส่วนลดสมาชิก ชำระเงิน ดูใบเสร็จ และตรวจประวัติออเดอร์ โดยใช้ API และ SQLite ชุดเดียวกับแอป CLI

```bash
python3 web_app.py
```

จากนั้นเปิด `http://127.0.0.1:8000` (ใช้ `COFFEE_POS_PORT` เพื่อเลือกพอร์ตอื่น) ต้องเปิดผ่าน URL นี้ ไม่เปิด `web/index.html` ด้วยการดับเบิลคลิก เพราะหน้าไฟล์โดยตรงไม่สามารถเรียก API ได้ และปุ่มชำระเงินจะใช้งานได้เมื่อมีสินค้าในตะกร้า กรอกเงินสดพอชำระ และ (ถ้ากรอกเบอร์สมาชิก) ต้องเป็นสมาชิกที่ลงทะเบียนแล้ว

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

ข้อมูลเริ่มต้นจะถูกเพิ่มลง SQLite เมื่อเปิดโปรแกรมครั้งแรก หากมีไฟล์ JSON เก่าใน `data/` ระบบจะย้ายข้อมูลของตารางที่ยังว่างใน transaction และเก็บไฟล์ต้นฉบับไว้ สมาชิกตัวอย่างสำหรับทดลองคือ `0812345678` (Somchai) และ `0898765432` (Somsri)

## ทดสอบ

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions ใน `.github/workflows/ci.yml` ติดตั้ง dependencies แล้วรัน flake8 และชุดทดสอบทุกครั้งที่ push หรือเปิด Pull Request

ชุดทดสอบครอบคลุม models, JSON/file I/O, SQLite migration/CRUD/persistence, business logic, CLI, API และ Sales Advisor ผลรันล่าสุด **66 tests — OK** ดูรายงานสรุปล่าสุดใน `docs/FINAL_SPRINT_REPORT.md` และรายงานย้อนหลังแยก Sprint ในโฟลเดอร์ `docs/`

## เอกสารประกอบ

- [PLAN.md](PLAN.md) — แผนงาน, UML, schema, DoD และการตัดสินใจออกแบบ
- [docs/SPRINT1_REPORT.md](docs/SPRINT1_REPORT.md) — รายงานรากฐาน CLI และผลการทบทวน Sprint 1
- [docs/SPRINT2_REPORT.md](docs/SPRINT2_REPORT.md) — รายงาน Back-End, models, persistence และ business logic
- [docs/SPRINT3_REPORT.md](docs/SPRINT3_REPORT.md) — รายงาน Full-Stack Integration, API, automation, edge cases และ CI
- [docs/FINAL_SPRINT_REPORT.md](docs/FINAL_SPRINT_REPORT.md) — ผล CI/CD, automation และ runbook การนำเสนอ Final Sprint
- [CHANGELOG.md](CHANGELOG.md) — ประวัติการเปลี่ยนแปลงตาม Sprint
- [LEARNINGLOG.md](LEARNINGLOG.md) — บทเรียนที่ได้จากการพัฒนา

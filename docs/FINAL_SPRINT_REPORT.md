# Final Sprint — DevOps, CI/CD และ Automation

- **โปรเจกต์:** Group15 Express Coffee — Smart POS
- **รายวิชา:** CP352301 Script Programming (1/2569)
- **เป้าหมาย:** ทำให้การตรวจคุณภาพทำซ้ำได้ สาธิต API และเพิ่ม automation ที่ใช้ข้อมูลยอดขายจริง

## 1. สิ่งส่งมอบ

| ข้อกำหนด | สิ่งที่ส่งมอบ | สถานะ |
|---|---|---|
| Unit tests | `unittest` ครอบคลุม models, persistence, services, CLI, API และ Sales Advisor | ผ่าน 62 tests |
| Automated QA / lint | flake8 ใช้ `setup.cfg` และรันใน GitHub Actions | ผ่านในเครื่องและ GitHub Actions |
| CI/CD | `.github/workflows/ci.yml` รันเมื่อ push และ pull request | ผ่าน |
| API integration | `requests` client เรียก self-made local mock API: GET menu, GET orders, POST orders | สาธิตครบและผล POST ถูกบันทึกผ่าน `ShopService`/JSON |
| API error handling | จัดการ timeout, HTTP status, JSON ที่ผิดรูปแบบ และ payload ที่ไม่ถูกต้อง | มี API tests |
| AI / Automation | Sales Advisor แนะนำเมนูขายดีหรือโปรโมตเมนูเมื่อยังไม่มีออเดอร์ โดยใช้ `DailySummary` | ทำงานเป็น rule-based automation ที่อธิบายได้ |
| Documentation | README, PLAN, CHANGELOG, LEARNINGLOG และรายงานแยก Sprint | อัปเดตแล้ว |

### API Endpoints

| Method | Endpoint | ผลลัพธ์ |
|---|---|---|
| GET | `/api/menu` | รายการเครื่องดื่มใน JSON |
| GET | `/api/orders` | ประวัติออเดอร์ใน JSON |
| POST | `/api/orders` | สร้างและบันทึกออเดอร์ ส่ง JSON กลับพร้อม HTTP 201 |

ใช้ local mock API ตามตัวเลือกที่ข้อกำหนดอนุญาต จึงไม่ต้องพึ่ง API key หรือ external network ระหว่างสาธิต

## 2. ผลการตรวจคุณภาพ

- `python -m unittest discover -s tests -v` — **62 tests, OK**
- `flake8 coffee_pos tests main.py api_demo.py` — **ผ่าน**
- `python api_demo.py` — GET เมนู 6 รายการ → POST สร้างออเดอร์ #1 → GET อ่านออเดอร์กลับ 1 รายการ
- GitHub Actions: [Coffee POS CI run](https://github.com/rapee29/final-project/actions/runs/38261179588) — **success** สำหรับ commit `df2fa2c`

## 3. โครงร่างนำเสนอและ Live Demo ตามเกณฑ์ 5 ส่วน

1. **ปัญหา/สถาปัตยกรรม (20%)** — อธิบายปัญหาร้านกาแฟขนาดเล็กและแสดง UML/โครงสร้าง Presentation, Business Logic, Data Access
2. **Technology Stack (10%)** — Python, `requests`, JSON, `unittest`, flake8 และ GitHub Actions พร้อมเหตุผลที่ใช้ local mock API
3. **Live Demo และการทดสอบ (40%)** — ทำ CRUD, ปิด/เปิดโปรแกรมเพื่อยืนยัน persistence, สาธิต search/filter/sort, ป้อนค่าผิด และรัน `python api_demo.py`
4. **ปัญหาและการ refactor (15%)** — เล่าการแก้ RAM/file consistency, rollback, validation และ edge cases จาก Sprint 1–3
5. **DevOps และ AI/Automation (15%)** — เปิด GitHub Actions run ที่ผ่าน แล้วสาธิต Sales Advisor จากสรุปยอดขาย

## 4. ขอบเขตและข้อจำกัด

- Sales Advisor เป็น rule-based automation ไม่ใช่ generative AI; จัดอยู่ในทางเลือก Automation ของเกณฑ์วิชา และอธิบายเหตุผลได้จากข้อมูลยอดขาย
- API เป็น mock API ภายในเครื่องตามตัวเลือกที่โจทย์อนุญาต ไม่ใช่ public API
- ก่อนนำเสนอ ให้ดึง repository ล่าสุดและเปิด GitHub Actions run ที่ตรงกับ commit ล่าสุด; ลิงก์ข้างต้นเป็น run ที่ยืนยันสถานะ success แล้ว

## 5. Definition of Done

- [x] Unit tests ผ่าน 62 รายการ
- [x] flake8 ผ่าน
- [x] API GET/POST สาธิตครบและจัดการ error cases
- [x] GitHub Actions CI ทำงานและมี run ที่ผ่าน
- [x] Automation แสดงคำแนะนำจากยอดขาย
- [x] เอกสารและบทบาททีมระบุครบ
- [ ] ซ้อมนำเสนอและ Live Demo กับสมาชิกทุกคนก่อนวันนำเสนอ

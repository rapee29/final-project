# PLAN.md — Group15 Express Coffee (Smart POS Coffee Terminal)

> รายวิชา CP352301 Script Programming · Final Project · อัปเดตถึง **Final Sprint**
> สมาชิก: รพีพรรณ ศรีบุญเรือง · สุกิจตรา โคแสงรักษา · วิยดา มูลกัน · สุภกร กงชา (หมุนเวียน Planner/Architect, Coder และ Debugger/QA ให้ครบทุกคนตลอด Sprint 1–Final)

## 1. ปัญหาและคุณค่า

ร้านกาแฟขนาดเล็กต้องรับออเดอร์ที่ปรับแต่งได้ (ขนาด, นม, ความหวาน), คิดส่วนลดสมาชิก, ทอนเงิน
และสรุปยอดขาย โดยไม่ต้องใช้เครื่อง POS ราคาแพง ระบบนี้เป็น POS แบบ Terminal ที่
**เก็บข้อมูลถาวร** (ปิดโปรแกรมแล้วยอดขายไม่หาย), **จัดการเมนูและสมาชิกได้เอง** และ
**ไม่พังเมื่อกรอกข้อมูลผิดหรือไฟล์เสีย**

## 2. สถาปัตยกรรม 3 เลเยอร์ (Separation of Concerns)

```
┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer   coffee_pos/ui/cli.py   (CoffeeCLI)     │  เมนู, prompt, พิมพ์ใบเสร็จ
│  - ไม่มีสูตรคำนวณ/ไฟล์ เรียก ShopService เท่านั้น             │
├─────────────────────────────────────────────────────────────┤
│ Business Logic Layer   coffee_pos/services/shop_service.py  │  CRUD, ค้นหา/กรอง/เรียง,
│  - ไม่มี print()/input()  ทดสอบได้โดยไม่ต้องมี Terminal       │  คิดราคา, checkout, สรุปยอด
│  coffee_pos/models/*  (Domain Models + validation)          │
├─────────────────────────────────────────────────────────────┤
│ Data Access Layer   coffee_pos/data_access/                 │  File I/O, กู้ไฟล์เสีย,
│  SQLiteDatabase · SQLiteRepository (production)                │  JSONRepository สำหรับ fallback / migration
└─────────────────────────────────────────────────────────────┘
```

### โครงสร้างโฟลเดอร์

```
coffee-pos/
├── main.py                      # จุดเริ่มโปรแกรม
├── coffee_pos/
│   ├── exceptions.py            # Custom Exceptions
│   ├── api/                     # requests client + local mock HTTP API
│   ├── models/                  # Drink, Member, CartItem, Order, Quote, DailySummary
│   ├── data_access/             # SQLiteDatabase, SQLiteRepository, JSON fallback
│   ├── services/shop_service.py # ShopService + build_service()
│   └── ui/cli.py                # CoffeeCLI
├── tests/                       # unittest + API + automation tests
├── .github/workflows/ci.yml    # flake8 + unittest
├── api_demo.py                 # GET/POST API walkthrough
├── web_app.py                  # จุดเริ่มต้นเว็บ POS
├── web/                        # หน้าเว็บ POS (HTML, CSS, JavaScript)
├── data/                        # coffee_pos.sqlite3; JSON legacy จาก Sprint 2–3 (ถ้ามี)
├── docs/SPRINT1_REPORT.md       # Sprint 1: CLI foundation
├── docs/SPRINT2_REPORT.md       # Sprint 2: Back-End and persistence
├── docs/SPRINT3_REPORT.md       # Sprint 3: integration and QA
├── docs/FINAL_SPRINT_REPORT.md  # Final Sprint: CI/CD and handoff
└── PLAN.md
```

## 3. UML Class Diagram

```mermaid
classDiagram
    class Drink {
        +int drink_id
        +str name
        +float price
        +to_dict() dict
        +from_dict(data) Drink
    }
    class Member {
        +str phone
        +str name
        +float discount_rate
        +discount_for(subtotal) float
        +to_dict() dict
        +from_dict(data) Member
    }
    class CartItem {
        +int drink_id
        +str name
        +str size
        +str milk
        +str sweetness
        +int qty
        +float unit_price
        +total_price float
    }
    class Order {
        +int order_id
        +str timestamp
        +List~CartItem~ items
        +float subtotal
        +float discount
        +float total
        +float cash_received
        +float change
        +str member_phone
        +str member_name
        +cups int
        +day date
    }
    class Quote {
        +float subtotal
        +float discount
        +float total
        +str member_name
    }
    class DailySummary {
        +date day
        +int transactions
        +int cups
        +float revenue
        +float discounts
        +str top_drink
    }
    class JSONManager {
        +Path path
        +load() List~dict~
        +save(data) None
        +backup(reason) Path
    }
    class JSONRepository~T~ {
        +all() List~T~
        +get(key) T
        +add(item) T
        +update(item) T
        +delete(key) T
    }
    class ShopService {
        +list_drinks() / add_drink() / update_drink() / remove_drink()
        +search_drinks(keyword) / filter_drinks(min,max) / sort_drinks(by)
        +list_members() / add_member() / update_member() / remove_member()
        +search_members(keyword)
        +build_cart_item(...) CartItem
        +price_cart(cart, phone) Quote
        +checkout(cart, cash, phone) Order
        +filter_orders(...) / sort_orders(...)
        +daily_summary(day) DailySummary
    }
    class CoffeeCLI {
        +run() None
        +new_order() / manage_menu() / manage_members()
        +show_daily_summary() / show_order_history()
    }
    class CoffeePOSError
    CoffeePOSError <|-- ValidationError
    CoffeePOSError <|-- NotFoundError
    CoffeePOSError <|-- DuplicateError
    CoffeePOSError <|-- EmptyCartError
    CoffeePOSError <|-- InsufficientPaymentError
    CoffeePOSError <|-- DataFileError

    Order "1" *-- "1..*" CartItem
    JSONRepository --> JSONManager : uses
    ShopService --> JSONRepository : drinks / members / orders
    ShopService ..> Quote : returns
    ShopService ..> DailySummary : returns
    CoffeeCLI --> ShopService : calls
```

## 4. Data Schema

Production tables: `drinks(drink_id, name, price)`, `members(phone, name, discount_rate)` และ `orders(order_id, timestamp, total, payload)`. `payload` เก็บรายละเอียดรายการสินค้าในออเดอร์เป็น JSON เพื่อรักษาข้อมูลที่ซ้อนกัน ส่วนไฟล์ JSON ด้านล่างเป็นรูปแบบ legacy ที่ระบบนำเข้าได้เมื่อ table ปลายทางยังว่าง

**data/menu.json**
```json
[{"drink_id": 1, "name": "Espresso", "price": 55.0}]
```
**data/members.json**
```json
[{"phone": "0812345678", "name": "Somchai", "discount_rate": 0.1}]
```
**data/orders.json**
```json
[{
  "order_id": 1, "timestamp": "2026-10-12 09:02:51",
  "items": [{"drink_id": 2, "name": "Americano", "size": "L", "milk": "Almond Milk",
             "sweetness": "50%", "qty": 1, "unit_price": 95.0, "total_price": 95.0}],
  "subtotal": 95.0, "discount": 0.0, "total": 95.0,
  "cash_received": 100.0, "change": 5.0,
  "member_phone": null, "member_name": "Guest"
}]
```
ขนาด/นม/ความหวาน (`SIZE_OPTIONS`, `MILK_OPTIONS`, `SWEETNESS_LEVELS`) เป็นค่าคงที่ใน
`models/options.py` ไม่ได้เก็บในไฟล์

## 5. Definition of Done (DoD)

**ฟังก์ชันหลัก**
- [x] CRUD เมนู (เพิ่ม/แก้/ลบ/ดู) และ CRUD สมาชิก — ข้อมูลอยู่ในไฟล์หลังปิดโปรแกรม
- [x] ค้นหาเมนูตามชื่อ (ไม่สนตัวพิมพ์), กรองตามช่วงราคา, เรียงตามชื่อ/ราคา (น้อย→มาก, มาก→น้อย)
- [x] ประวัติออเดอร์: กรองตามวันที่/ช่วงยอด/สมาชิก และเรียงตามเวลา/ยอด
- [x] สรุปยอดขายรายวัน (จำนวนรายการ, แก้ว, ส่วนลด, รายได้, เมนูขายดี) เลือกวันได้
- [x] Flow สั่งซื้อเดิมจาก Sprint 1 ใช้งานได้ครบ (ขนาด, นม, ความหวาน, สมาชิก 10%, ใบเสร็จ)

**พฤติกรรมเมื่อเกิดข้อผิดพลาด**
- [x] ไฟล์ข้อมูลหาย → สร้างไฟล์เริ่มต้นเอง ไม่พัง
- [x] JSON เสีย/ชนิดผิด → สำรองเป็น `*.bak` แล้วกู้ค่าเริ่มต้น พร้อมแจ้งผู้ใช้
- [x] ระเบียนในไฟล์ไม่ถูกต้อง → ข้ามเฉพาะระเบียนนั้น + สำรองไฟล์ + แจ้งจำนวนที่ข้าม
- [x] เขียนไฟล์ไม่ได้ → แจ้ง `DataFileError`, ข้อมูลใน RAM ย้อนกลับ (RAM = ไฟล์เสมอ)
- [x] ลบ/แก้รายการที่ไม่มี → `NotFoundError` ที่จัดการแล้ว ไม่ทำให้โปรแกรมพัง
- [x] ป้อนตัวอักษร/ค่าติดลบ/ค่าว่าง/`nan`/`inf`/นอกช่วง → แจ้งเตือนและถามใหม่
- [x] Ctrl+C / Ctrl+D ระหว่างทำงาน → ออกอย่างสุภาพ ไม่มี traceback
- [x] พิมพ์ `cancel` ที่ prompt ใดก็ได้ → ยกเลิกรายการและกลับเมนู

**End-to-End DoD (Sprint 3):** เมนู CLI ทุกข้อเรียก `ShopService` โดยตรง และ
`python -m unittest discover -s tests -v` ผ่านทั้งหมด

## 6. การจัดการ State และ Data Consistency (Sprint 3)

- `JSONRepository` เก็บข้อมูลใน RAM แบบ `dict` และ **เขียนไฟล์ทุกครั้งที่เปลี่ยน** (write-through)
- ถ้าเขียนไฟล์ล้มเหลว จะ **rollback** การเปลี่ยนใน RAM ทันที → RAM กับไฟล์ไม่เคยไม่ตรงกัน
- เขียนไฟล์แบบ atomic (เขียนไฟล์ชั่วคราวแล้ว `os.replace`) → ไม่เกิดไฟล์ครึ่งๆ กลางๆ ถ้าโปรแกรมถูกปิดกลางคัน
- ตะกร้า (cart) เป็นรายการใน UI ตลอดการสั่ง และถูกบันทึกลง `orders.json` ครั้งเดียวตอนจ่ายเงินสำเร็จ

## 7. การเปรียบเทียบทางเลือกด้านการออกแบบ

| เรื่อง | ที่เลือก | ทางเลือกอื่น | เหตุผล |
|---|---|---|---|
| ที่เก็บข้อมูล | SQLite สำหรับ production; JSON สำหรับ fallback และ migration | CSV / MySQL | SQLite เป็นฐานข้อมูลเชิงสัมพันธ์แบบไฟล์ ไม่ต้องพึ่ง database server; รายละเอียดรายการในออเดอร์เก็บเป็น JSON |
| จังหวะบันทึก | เขียนทันทีทุกการเปลี่ยน | บันทึกตอนออกโปรแกรม | ไฟดับ/โปรแกรมค้างข้อมูลไม่หาย; แลกกับเขียนไฟล์บ่อยขึ้น (วัดแล้ว 300 รายการ ≈ 0.26 วินาที) |
| การเรียงลำดับ | `sorted()` (Timsort) ด้วย key | เขียน bubble/merge sort เอง | เสถียร, O(n log n), วัดจริง 1,006 รายการเรียง 0.22 ms |
| Domain model | `@dataclass` + validate ใน `__post_init__` | dict ธรรมดา | ข้อมูลไม่ถูกต้องเข้าระบบไม่ได้ตั้งแต่ต้นทาง |
| เงิน | `float` ปัดทศนิยม 2 ตำแหน่ง | `Decimal` | ราคาเป็นจำนวนเต็มบาท + ส่วนลด 10% ปัดทุกขั้น; ถ้าต้องรองรับสตางค์/ภาษีจริงควรย้ายไป `Decimal` |
| Design Pattern | Repository, Service Layer, Dependency Injection (`ShopService` รับ repo/clock, `CoffeeCLI` รับ input/output) | เรียกไฟล์ตรงจาก UI | ทดสอบได้ด้วย input จำลองและนาฬิกาปลอม |

## 8. ประวัติ Refactor (Sprint 1 → Sprint 2 → Sprint 3)

| Sprint 1 (ไฟล์เดียว, procedural) | Sprint 2–3 | เหตุผล |
|---|---|---|
| `MENU`, `MEMBERS` เป็น dict ฮาร์ดโค้ด | `Drink`, `Member` + `menu.json`, `members.json` | แก้ไขเมนู/สมาชิกได้โดยไม่แก้โค้ด |
| `sales_history` เป็น list ใน RAM (ปิดโปรแกรมแล้วหาย) | `Order` + SQLite `orders` table | ข้อมูลยอดขายคงอยู่ในฐานข้อมูล |
| `get_customization()` / `take_order()` / `checkout()` ปนทั้ง input, คิดเงิน, พิมพ์ | UI → `ShopService.build_cart_item()/price_cart()/checkout()` | แยก Presentation / Business Logic |
| qty ผิด → `continue` ทิ้งตัวเลือกขนาด/นมที่เลือกไว้ | ถามเฉพาะ qty ใหม่ | แก้บั๊ก UX |
| `float(input())` รับ `inf` ได้ (เงินทอน = inf) | `require_number()` ปฏิเสธ `nan`/`inf` | แก้บั๊ก validation |
| Exit เป็นเมนู 3 | เมนู 1–2 คงเดิม, เพิ่ม 3–5, Exit = `0` | เพิ่มฟีเจอร์ Sprint 2 |

## 9. Final Term Requirements: API, CI/CD และ Automation

### ตารางหมุนเวียนบทบาททีม Sprint 1–3 และ Final Sprint

| สมาชิก | Sprint 1 | Sprint 2 | Sprint 3 | Final Sprint |
|---|---|---|---|---|
| รพีพรรณ ศรีบุญเรือง | Coder — พัฒนา CLI | Debugger / QA — ตรวจ models และ persistence | Coder — API และ error handling | Planner / Release coordinator — checklist และประสานการส่งมอบ |
| สุกิจตรา โคแสงรักษา | Planner / วางแผน CLI | Coder — Domain Models และ schema | Debugger / QA — ตรวจ API client และ integration | Coder — SQLite tests, lint และ CI fixes |
| วิยดา มูลกัน | Debugger / QA — ทดสอบ CLI | Coder — Business Logic และ algorithms | Planner / Architect — integration plan และ demo | Coder — Sales Advisor / automation |
| สุภกร กงชา | Coder — พัฒนาเมนูและ checkout | Planner / Architect — วางแผน persistence และ service | Coder — CLI/API walkthrough | Debugger / QA — ตรวจ release และ live demo |

ตรวจการหมุนเวียนแล้ว สมาชิกทุกคนได้รับ Planner/Architect 1 รอบ, Coder 2 รอบ และ Debugger/QA 1 รอบพอดีตลอด Sprint 1–Final; แต่ละ Sprint มี Planner 1 คน, Coder 2 คน และ Debugger/QA 1 คน

### API ที่เลือก

ใช้ **self-made local mock API สำหรับ Coffee POS** ที่ `coffee_pos/api/server.py` โดยเลือกวิธีนี้เพื่อให้ GET/POST อยู่ในโดเมนร้านกาแฟ ทดสอบซ้ำได้ และไม่ต้องพึ่ง API key หรือเครือข่ายภายนอก

| Method | Endpoint | พฤติกรรม | การทดสอบ |
|---|---|---|---|
| GET | `/api/menu` | คืนรายการเมนูจาก `ShopService` | ตรวจ JSON และจำนวนเมนู |
| GET | `/api/orders` | คืนประวัติออเดอร์ที่บันทึกแล้ว | ตรวจว่าหลัง POST อ่านรายการกลับได้ |
| POST | `/api/orders` | ตรวจ JSON, สร้าง cart, คิดเงินและบันทึกผ่าน `ShopService` | payload ปกติ, ผิดรูปแบบ, เงินไม่พอ, menu/order not found |

### แผนงานราย Sprint

| Sprint | งานและหลักฐานที่ควรส่ง | สถานะในโค้ดปัจจุบัน |
|---|---|---|
| Sprint 1 — Foundation | บันทึก API readiness check ใน `PLAN.md`; กำหนด endpoints, request/response schema, Definition of Done และกรณี error ก่อนลงมือ | ข้อกำหนดเดิมเน้น CLI; เพิ่มสัญญา API ในเอกสารนี้ย้อนหลัง |
| Sprint 2 — Back-End | สร้าง API server/client, เชื่อม GET/POST กับ `ShopService`, persistence ผ่าน JSON และทดสอบ valid/invalid payload กับ HTTP errors | มี `coffee_pos/api/`, `requests`, API tests และ `api_demo.py` |
| Sprint 3 — Integration | สาธิต GET menu → POST order → GET order; จัดการ timeout/HTTP/JSON errors; แสดง automation จากยอดขาย และทดสอบ end-to-end | มี API walkthrough, client error handling และ Sales Advisor ในสรุปยอด |
| Final Sprint | GitHub Actions รัน lint + tests, เพิ่มหน้าเว็บ POS และเชื่อม persistence | หน้าเว็บ/API ใช้ SQLite โดย production; สร้างไฟล์ฐานข้อมูลอัตโนมัติ |

### Automation / Sales Advisor

`coffee_pos/services/sales_advisor.py` ใช้ยอดขายจริงจาก `DailySummary` เพื่อแนะนำเมนูขายดี หรือแนะนำโปรโมตเมนูประจำวันเมื่อยังไม่มีออเดอร์ เป็น automation แบบกฎที่อธิบายได้ ไม่อ้างว่าเป็นโมเดล generative AI

### Checklist ก่อนส่ง

- [x] ติดตั้งด้วย `python -m pip install -r requirements.txt`
- [x] รัน `python api_demo.py` และบันทึกผล GET/POST สำหรับการสาธิต
- [x] รัน `python -m unittest discover -s tests -v` ในเครื่องหลังเปลี่ยนเป็น SQLite (66 tests)
- [x] รัน `flake8 coffee_pos tests main.py api_demo.py` และแก้ข้อผิดพลาด
- [x] ตรวจว่า GitHub Actions ผ่านสำหรับ commit `6ead4ee` หลังเปลี่ยนเป็น SQLite แล้วแนบลิงก์ run ในรายงาน Final Sprint
- [x] ระบุชื่อผู้รับผิดชอบในตารางบทบาท README, PLAN และรายงาน Final Sprint
- [ ] ซ้อม live demo กับสมาชิก: CRUD, persistence หลังเปิดใหม่, search/filter/sort, invalid input, API errors, CI และ sales advice

รายงาน Final Sprint และลำดับสาธิตอยู่ใน [`docs/FINAL_SPRINT_REPORT.md`](docs/FINAL_SPRINT_REPORT.md)

## 10. แนวทางต่อยอด

หากต้องการ AI จริงในอนาคต ค่อยเพิ่มโมเดลแนะนำสินค้าและเปรียบเทียบกับ Sales Advisor แบบกฎ

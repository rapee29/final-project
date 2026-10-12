# ☕ Group15 Express Coffee — Smart POS Coffee Terminal

POS ร้านกาแฟแบบ Terminal เขียนด้วย Python (ใช้เฉพาะ standard library) รายวิชา CP352301 Script Programming

## ฟีเจอร์

- สั่งเครื่องดื่ม: เลือกเมนู, ขนาด (S/M/L), นม, ความหวาน, จำนวน, หลายรายการต่อออเดอร์
- สมาชิกลด 10% (ตั้งค่าเปอร์เซ็นต์ได้), รับเงินสด, ทอนเงิน, ใบเสร็จ
- จัดการเมนูและสมาชิก (เพิ่ม/แก้/ลบ/ดู) พร้อมค้นหา กรอง และเรียงลำดับ
- ประวัติการขาย กรองตามวันที่/ช่วงยอด/สมาชิก และเรียงตามเวลา/ยอด
- สรุปยอดขายรายวัน (เลือกวันได้) พร้อมเมนูขายดี
- ข้อมูลเก็บถาวรเป็น JSON ใน `data/` (สร้างเองอัตโนมัติ, กู้เองถ้าไฟล์เสีย)

## วิธีใช้

ต้องใช้ Python 3.9 ขึ้นไป (ทดสอบบน 3.12) ไม่ต้องติดตั้งแพ็กเกจเพิ่ม

```bash
python main.py                              # รันโปรแกรม
python -m unittest discover -s . -v         # รันชุดทดสอบ (56 tests)
```

พิมพ์ `cancel` ที่ prompt ใดก็ได้เพื่อยกเลิกรายการปัจจุบัน

## โครงสร้าง

ดูรายละเอียดและ UML ใน [PLAN.md](PLAN.md) · Test Log ใน [docs/SPRINT2-3_REPORT.md](docs/SPRINT2-3_REPORT.md)

```
coffee_pos/
├── models/        # Domain models: Drink, Member, CartItem, Order
├── data_access/   # JSONManager (File I/O), JSONRepository
├── services/      # ShopService (Business Logic)
└── ui/            # CoffeeCLI (Presentation)
```

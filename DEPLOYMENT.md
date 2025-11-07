# 🚀 Deployment Guide - Trade Bot V1.4

คู่มือการ deploy และตั้งค่า Trade Bot V1.4 แบบครบถ้วน

---

## 📑 Table of Contents

- [GitHub Setup](#-github-setup)
- [GitHub Actions Setup](#-github-actions-setup)
- [Streamlit Cloud Deployment](#-streamlit-cloud-deployment)
- [Troubleshooting](#-troubleshooting)

---

## 📦 GitHub Setup

### Step 1: Create GitHub Repository

1. ไปที่ https://github.com/new
2. กรอกข้อมูล:
   - **Repository name:** `bot-trade` (หรือชื่ออื่นที่ต้องการ)
   - **Description:** `Multi-currency trading bot for IQ Option Binary Options`
   - **Visibility:** `Public` (หรือ Private ถ้าต้องการ)
   - ❌ **DO NOT** initialize with README, .gitignore, or license (เรามีอยู่แล้ว)
3. คลิก **"Create repository"**

### Step 2: Push Code to GitHub

หลังจากสร้าง repository แล้ว รันคำสั่งเหล่านี้:

```bash
# ตรวจสอบว่าอยู่ใน bot-trade folder
cd /path/to/bot-trade

# เพิ่ม GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/bot-trade.git

# Push ขึ้น GitHub
git branch -M main
git push -u origin main
```

**หมายเหตุ:** เปลี่ยน `YOUR_USERNAME` เป็น GitHub username ของคุณ

### Step 3: Verify on GitHub

1. ไปที่ `https://github.com/YOUR_USERNAME/bot-trade`
2. ควรเห็นไฟล์ทั้งหมด:
   - ✅ `bot_v1.4.py`
   - ✅ `dashboard.py`
   - ✅ `requirements.txt`
   - ✅ `.github/workflows/trading-bot.yml`
   - ✅ `.streamlit/config.toml`
   - ✅ `versions/v1.4/config.json`
   - ✅ `test_results/v1.4_MULTI_1m_30d.csv`
   - ✅ `README.md`

---

## ⚙️ GitHub Actions Setup

GitHub Actions จะรัน bot ตามตารางเวลาที่กำหนด อัตโนมัติและฟรี

### ภาพรวม

**GitHub Actions จะ:**
- ⏰ รันอัตโนมัติทุก 30 นาที (ในช่วงเวลาเทรด)
- 💰 เทรดบน IQ Option Practice/Real Account
- 💾 บันทึกผลลง `trades.csv` ใน repo
- 📊 Dashboard บน Streamlit Cloud อ่านจาก `trades.csv`

**ข้อดี:**
- ✅ ฟรี (2,000 นาที/เดือน)
- ✅ ไม่ต้องเปิดเครื่องทิ้งไว้
- ✅ รันอัตโนมัติ
- ✅ ดู logs ได้ใน GitHub

**ข้อจำกัด:**
- ⚠️ รันได้ประมาณ 400 ครั้ง/เดือน (5 นาที/ครั้ง)
- ⚠️ เหมาะกับการเทรดเฉพาะช่วงเวลาดีๆ

### Step 1: ตั้งค่า Secrets ใน GitHub

#### 1.1 ไปที่ GitHub Repository

```
https://github.com/YOUR_USERNAME/bot-trade
```

#### 1.2 ไปที่ Settings → Secrets and variables → Actions

คลิก **"New repository secret"**

#### 1.3 เพิ่ม Secrets ทั้งหมด 3 ตัว

**Secret 1: IQ_EMAIL**
- Name: `IQ_EMAIL`
- Value: `your_email@example.com` (อีเมล IQ Option ของคุณ)

**Secret 2: IQ_PASSWORD**
- Name: `IQ_PASSWORD`
- Value: `your_password` (รหัสผ่าน IQ Option)

**Secret 3: IQ_MODE**
- Name: `IQ_MODE`
- Value: `PRACTICE` (ใช้บัญชีทดลอง)

⚠️ **สำคัญ:** Secrets เหล่านี้จะถูกเข้ารหัส GitHub จะไม่แสดงให้ใครเห็น

### Step 2: เปิดใช้งาน GitHub Actions

#### 2.1 ไปที่แท็บ "Actions" ใน repo

#### 2.2 คลิก "I understand my workflows, go ahead and enable them"

#### 2.3 เลือก workflow "Trading Bot V1.4"

คุณจะเห็น workflow ชื่อ **"Trading Bot V1.4"**

### Step 3: ทดสอบรัน Bot

#### Option A: รันทันที (Manual Trigger)

1. ไปที่ **Actions** → **Trading Bot V1.4**
2. คลิก **"Run workflow"** ขวามือ
3. เลือก branch: `main`
4. คลิก **"Run workflow"**

#### Option B: รอ Schedule

Bot จะรันอัตโนมัติตามเวลา:
- 12:00-13:59 UTC (ทุก 30 นาที)
- 18:00-18:59 UTC (ทุก 30 นาที)
- 19:00-02:59 UTC (ทุก 30 นาที)

### Step 4: ดูผลลัพธ์

#### 4.1 ดู Logs ใน GitHub Actions

- ไปที่ **Actions** → คลิกที่ run ล่าสุด
- ดู logs ของแต่ละ step
- เช็คว่า bot เทรดหรือไม่

#### 4.2 ดู Dashboard

เปิด Streamlit Dashboard:
```
https://your-app.streamlit.app
```

Dashboard จะอ่าน `trades.csv` จาก repo และแสดงผลอัตโนมัติ!

### การทำงานของ Workflow

```
GitHub Actions ทุก 30 นาที
    ↓
Setup Python + Install packages
    ↓
Run bot_v1.4.py
    ↓
- Connect IQ Option
- Check signals (EURUSD, EURUSD-OTC, EURCAD)
- Execute trades ถ้ามีสัญญาณ
- Save to trades.csv
    ↓
Commit & Push trades.csv กลับ repo
    ↓
Streamlit Dashboard อ่าน trades.csv
    ↓
แสดงผลทันที! 📊
```

### ตารางเวลาที่ Bot จะรัน

| เวลา UTC | คู่เงิน | ทิศทาง | ความถี่ | Win Rate |
|----------|---------|--------|---------|----------|
| 12:00-13:59 | EURUSD-OTC | PUT | ทุก 30 นาที | 73% |
| 18:00-18:59 | EURUSD-OTC | CALL | ทุก 30 นาที | 60% |
| 19:00-02:59 | EURUSD, EURCAD | PUT/CALL | ทุก 30 นาที | 62-67% |

**รวม: ~22 ครั้ง/วัน**

### การใช้โควต้า GitHub Actions

#### Free Tier:
- 2,000 นาที/เดือน

#### การใช้งานจริง:
```
22 ครั้ง/วัน × 5 นาที/ครั้ง × 30 วัน = 3,300 นาที/เดือน
```

⚠️ **เกินโควต้า!**

#### วิธีแก้:

**Option 1: ลดความถี่ → รันทุก 1 ชั่วโมง**

แก้ไขไฟล์ `.github/workflows/trading-bot.yml`:
```yaml
schedule:
  - cron: '0 12-13 * * *'  # ทุก 1 ชั่วโมง
  - cron: '0 18 * * *'
  - cron: '0 19-23 * * *'
  - cron: '0 0-2 * * *'
```
**ใช้: 1,650 นาที/เดือน** ✅

**Option 2: เทรดเฉพาะช่วง Premium**

แก้ไขให้เทรดเฉพาะ 12:00-13:00 และ 18:00:
```yaml
schedule:
  - cron: '0,30 12-13 * * *'  # เฉพาะช่วงนี้
  - cron: '0,30 18 * * *'
```
**ใช้: 600 นาที/เดือน** ✅

### ตัวอย่างผลลัพธ์

**Successful Run:**
```
✅ Bot initialized in PRACTICE mode
✅ Loaded config V1.4
🔌 Connecting to IQ Option (PRACTICE)...
✅ Connected successfully
✅ Switched to PRACTICE account
💰 Current balance: $10000.00
✅ Enabled pairs: EURUSD, EURUSD-OTC, EURCAD
⏰ Current time: 2025-11-06 12:15:00 UTC

🔍 Checking EURUSD...
⏭️  No signal for EURUSD

🔍 Checking EURUSD-OTC...
🔔 Signal detected: PUT
📊 Executing trade:
   Pair: EURUSD-OTC
   Direction: PUT
   Amount: $1
   Entry Price: 1.08234
✅ Trade opened (ID: 123456)
⏳ Waiting for result...
✅ Trade WON - Profit: $0.80
💾 Saved trade to trades.csv

📊 Run Summary
Trades executed: 1
Final balance: $10000.80
```

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Deploy to Streamlit Cloud

1. ไปที่ https://share.streamlit.io
2. **Sign in** ด้วย GitHub account
3. คลิก **"New app"**
4. กรอกข้อมูล:
   - **Repository:** `YOUR_USERNAME/bot-trade`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL:** เลือก URL ที่ต้องการ (เช่น `bot-trade`)
5. คลิก **"Deploy!"**

### Step 2: Wait for Deployment

- Streamlit Cloud จะ install dependencies (ประมาณ 2-3 นาที)
- รอจนกว่าสถานะจะเป็น "Running"
- คุณจะได้ URL เช่น: `https://bot-trade.streamlit.app`

### Step 3: Test Your Dashboard

#### Test Mode (แนะนำ)
```
https://YOUR-APP-NAME.streamlit.app?mode=test
```

คุณควรเห็น:
- ✅ 32-33 trades จาก backtest
- ✅ 3 tabs: ภาพรวม, EURCAD, EURUSD, EURUSD-OTC
- ✅ Win rate: 60-62.5%
- ✅ Charts และ metrics ครบถ้วน

#### Live Mode (ต้องตั้งค่า Secrets)
```
https://YOUR-APP-NAME.streamlit.app
```

### Step 4: Configure Secrets (สำหรับ Live Mode)

ถ้าต้องการใช้งาน Live Trading:

1. ไปที่ Streamlit Cloud → เลือก app ของคุณ
2. คลิก **"Settings"** (⚙️)
3. ไปที่ **"Secrets"**
4. เพิ่ม:

```toml
# IQ Option Credentials
iq_email = "your_email@example.com"
iq_password = "your_password"
iq_mode = "PRACTICE"

# Trading Configuration
capital = 100
amount = 1
```

5. คลิก **"Save"**
6. App จะ reboot อัตโนมัติ

### Update Dashboard (Future Changes)

เมื่อต้องการอัพเดท dashboard:

```bash
cd /path/to/bot-trade

# แก้ไขไฟล์ที่ต้องการ
# จากนั้น commit และ push

git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud จะ auto-deploy ใหม่อัตโนมัติ!

---

## 🐛 Troubleshooting

### GitHub Actions Issues

#### ปัญหา 1: Workflow ไม่รัน

**เช็ค:**
- ✅ Secrets ตั้งค่าครบหรือไม่? (IQ_EMAIL, IQ_PASSWORD, IQ_MODE)
- ✅ Actions เปิดใช้งานแล้วหรือไม่?
- ✅ ไฟล์ `.github/workflows/trading-bot.yml` commit แล้วหรือไม่?

#### ปัญหา 2: Bot เชื่อมต่อไม่ได้

**เช็ค logs:**
```
Actions → Run ล่าสุด → "Run trading bot" step
```

**สาเหตุที่เป็นไปได้:**
- ❌ อีเมล/รหัสผ่านผิด
- ❌ บัญชี IQ Option โดนล็อค
- ❌ IQ Option API down

#### ปัญหา 3: ไม่มีเทรด

**สาเหตุปกติ:**
- ⏰ ไม่อยู่ในช่วงเวลาที่กำหนด
- 📊 Indicators ไม่ผ่านเกณฑ์
- 🚫 ไม่ตรง session filter

**วิธีเช็ค:**
ดู logs ใน Actions จะบอกว่า:
```
🔍 Checking EURUSD...
⏭️  No signal for EURUSD (not in trading hours)
```

#### ปัญหา 4: trades.csv ไม่อัพเดท

**วิธีแก้:**
1. เช็คว่า workflow มี permission ให้ commit ไหม
2. ไปที่ Settings → Actions → General
3. Workflow permissions → เลือก **"Read and write permissions"**
4. กด Save

### Streamlit Cloud Issues

#### Problem: "ModuleNotFoundError"
**Solution:** ตรวจสอบว่า `requirements.txt` ครบถ้วน

#### Problem: "File not found: trades.csv"
**Solution:** ใช้ Test Mode ด้วย `?mode=test` parameter

#### Problem: Dashboard shows old data
**Solution:**
1. Force reboot app ใน Streamlit Cloud settings
2. หรือ clear cache โดยกด "C" ใน dashboard

#### Problem: Can't push to GitHub
**Solution:** ตรวจสอบ:
- GitHub username/password ถูกต้อง
- หรือใช้ Personal Access Token แทน password
- Repository URL ถูกต้อง

---

## 🎯 Best Practices

### 1. ทดสอบ Manual ก่อน
- รัน workflow ด้วยมือ 2-3 ครั้ง
- เช็คว่าเชื่อมต่อได้และเทรดได้จริง

### 2. ใช้ Practice Account เสมอ
- อย่าเปลี่ยนเป็น REAL จนกว่าจะมั่นใจ
- ทดสอบอย่างน้อย 1 สัปดาห์

### 3. ตั้ง Notifications
- ไปที่ Settings → Notifications
- เปิด "Actions" notifications
- จะได้รับแจ้งเตือนเมื่อ workflow fail

### 4. Backup Logs
- Download logs ทุกสัปดาห์
- เก็บไว้วิเคราะห์ performance

---

## 🔒 ความปลอดภัย

### ✅ ทำ:
- ใช้ GitHub Secrets เก็บ credentials
- ใช้ Practice account ทดสอบก่อน
- ตั้ง repository เป็น Private (แนะนำ)

### ❌ ไม่ทำ:
- อย่า commit credentials ใน code
- อย่าแชร์ secrets ให้ใคร
- อย่า fork repo ถ้ามี secrets

---

## 📈 ดูสถิติการใช้งาน

### เช็คโควต้าที่ใช้ไป:

1. ไปที่ **Settings** → **Billing and plans**
2. ดูที่ **Actions minutes used**

### ดู Logs ทั้งหมด:

1. ไปที่ **Actions**
2. คลิกที่แต่ละ run
3. Download logs เก็บไว้ (retention: 7 วัน)

---

## ✅ Deployment Checklist

### GitHub Setup
- [ ] สร้าง GitHub repository แล้ว
- [ ] Push code ขึ้น GitHub สำเร็จ
- [ ] ตรวจสอบไฟล์ครบบน GitHub

### GitHub Actions
- [ ] ตั้งค่า Secrets (IQ_EMAIL, IQ_PASSWORD, IQ_MODE)
- [ ] เปิดใช้งาน Actions
- [ ] ทดสอบ manual trigger สำเร็จ
- [ ] ตรวจสอบ workflow permissions

### Streamlit Cloud
- [ ] เชื่อมต่อ Streamlit Cloud กับ GitHub
- [ ] Deploy app สำเร็จ
- [ ] ทดสอบ Test Mode ได้
- [ ] (Optional) ตั้งค่า Secrets สำหรับ Live Mode

---

## 🚀 Success!

เมื่อทุกอย่างเสร็จแล้ว คุณจะมี:

✅ **Automated Trading:** Bot รันอัตโนมัติทุก 30 นาที
✅ **Public Dashboard:** แชร์ URL ได้เลย
✅ **Auto-deploy:** Push ใหม่ = Auto update
✅ **Free Hosting:** ไม่มีค่าใช้จ่าย
✅ **Professional URL:** `your-app.streamlit.app`

---

**Created:** November 7, 2025
**Updated:** November 7, 2025

🚀 **Happy Automated Trading!** 🚀

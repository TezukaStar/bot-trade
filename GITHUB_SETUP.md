# 🚀 GitHub Setup & Deployment Guide

คู่มือการสร้าง GitHub repository และ deploy ขึ้น Streamlit Cloud

---

## 📋 Step 1: Create GitHub Repository

1. ไปที่ https://github.com/new
2. กรอกข้อมูล:
   - **Repository name:** `trade-bot-dashboard` (หรือชื่ออื่นที่ต้องการ)
   - **Description:** `Multi-currency trading dashboard for IQ Option Binary Options`
   - **Visibility:** `Public` (หรือ Private ถ้าต้องการ)
   - ❌ **DO NOT** initialize with README, .gitignore, or license (เรามีอยู่แล้ว)
3. คลิก **"Create repository"**

---

## 📤 Step 2: Push Code to GitHub

หลังจากสร้าง repository แล้ว GitHub จะแสดงคำสั่ง copy คำสั่งเหล่านี้และรันใน terminal:

```bash
# ตรวจสอบว่าอยู่ใน streamlit-deploy folder
cd /Users/Aom/Documents/Aom/trade-bot/streamlit-deploy

# เพิ่ม GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/trade-bot-dashboard.git

# Push ขึ้น GitHub
git branch -M main
git push -u origin main
```

**หมายเหตุ:** เปลี่ยน `YOUR_USERNAME` เป็น GitHub username ของคุณ

---

## 🔑 Step 3: Verify on GitHub

1. ไปที่ `https://github.com/YOUR_USERNAME/trade-bot-dashboard`
2. ควรเห็นไฟล์ทั้งหมด:
   - ✅ `dashboard.py`
   - ✅ `requirements.txt`
   - ✅ `.streamlit/config.toml`
   - ✅ `versions/v1.4/config.json`
   - ✅ `test_results/backtest_results.csv`
   - ✅ `README.md`

---

## 🌐 Step 4: Deploy to Streamlit Cloud

1. ไปที่ https://share.streamlit.io
2. **Sign in** ด้วย GitHub account
3. คลิก **"New app"**
4. กรอกข้อมูล:
   - **Repository:** `YOUR_USERNAME/trade-bot-dashboard`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL:** เลือก URL ที่ต้องการ (เช่น `trade-bot-v14`)
5. คลิก **"Deploy!"**

---

## ⏱️ Step 5: Wait for Deployment

- Streamlit Cloud จะ install dependencies (ประมาณ 2-3 นาที)
- รอจนกว่าสถานะจะเป็น "Running"
- คุณจะได้ URL เช่น: `https://trade-bot-v14.streamlit.app`

---

## 🎯 Step 6: Test Your Dashboard

### Test Mode (แนะนำ)
```
https://YOUR-APP-NAME.streamlit.app?mode=test
```

คุณควรเห็น:
- ✅ 32 trades จาก backtest
- ✅ 3 tabs: ภาพรวม, EURCAD, EURUSD, EURUSD-OTC
- ✅ Win rate: 62.5%
- ✅ Charts และ metrics ครบถ้วน

### Live Mode (ต้องตั้งค่า Secrets)
```
https://YOUR-APP-NAME.streamlit.app
```

---

## 🔐 Optional: Configure Secrets (สำหรับ Live Mode)

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

---

## 📊 File Structure on GitHub

```
trade-bot-dashboard/
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── config.toml            # Streamlit theme & settings
├── README.md                   # Project documentation
├── dashboard.py                # Main Streamlit app
├── requirements.txt            # Python dependencies
├── test_results/
│   └── backtest_results.csv   # Backtest data
└── versions/
    └── v1.4/
        └── config.json        # V1.4 configuration

7 files, 1530 lines
```

---

## 🔄 Update Dashboard (Future Changes)

เมื่อต้องการอัพเดท dashboard:

```bash
cd /Users/Aom/Documents/Aom/trade-bot/streamlit-deploy

# แก้ไขไฟล์ที่ต้องการ
# จากนั้น commit และ push

git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud จะ auto-deploy ใหม่อัตโนมัติ!

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution:** ตรวจสอบว่า `requirements.txt` ครบถ้วน

### Problem: "File not found: trades.csv"
**Solution:** ใช้ Test Mode ด้วย `?mode=test` parameter

### Problem: Dashboard shows old data
**Solution:**
1. Force reboot app ใน Streamlit Cloud settings
2. หรือ clear cache โดยกด "C" ใน dashboard

### Problem: Can't push to GitHub
**Solution:** ตรวจสอบ:
- GitHub username/password ถูกต้อง
- หรือใช้ Personal Access Token แทน password
- Repository URL ถูกต้อง

---

## ✅ Checklist

- [ ] สร้าง GitHub repository แล้ว
- [ ] Push code ขึ้น GitHub สำเร็จ
- [ ] ตรวจสอบไฟล์ครบบน GitHub
- [ ] เชื่อมต่อ Streamlit Cloud กับ GitHub
- [ ] Deploy app สำเร็จ
- [ ] ทดสอบ Test Mode ได้
- [ ] (Optional) ตั้งค่า Secrets สำหรับ Live Mode

---

## 🎉 Success!

เมื่อทุกอย่างเสร็จแล้ว คุณจะมี:

✅ **Public Dashboard:** แชร์ URL ได้เลย
✅ **Auto-deploy:** Push ใหม่ = Auto update
✅ **Free Hosting:** ไม่มีค่าใช้จ่าย (Streamlit Community Cloud)
✅ **Professional URL:** `your-app.streamlit.app`

---

**Next:** Share your dashboard URL! 🚀

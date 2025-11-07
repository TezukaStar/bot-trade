# 📊 Trade Bot V1.4 - Multi-Currency Trading Bot

Real-time trading bot และ dashboard สำหรับ IQ Option Binary Options พร้อมการเทรดหลายคู่เงินพร้อมกัน

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📑 Table of Contents

- [Features](#-features)
- [Performance](#-v14-performance)
- [Quick Start](#-quick-start-5-นาที)
- [Configuration](#-configuration)
- [Test Mode](#-test-mode)
- [Strategy Details](#-strategy-details)
- [Tech Stack](#-tech-stack)
- [Deployment](#-deployment)

---

## 🎯 Features

- **Multi-Currency Support:** EURUSD, EURUSD-OTC, EURCAD
- **Real-time Metrics:** Win rate, ROI, Profit Factor, Max Drawdown
- **Interactive Charts:** Win/Loss pie chart, Equity curve
- **Trade History:** Paginated trade list with detailed analysis
- **Dual Mode:**
  - **Test Mode:** View backtest results (no credentials required)
  - **Live Mode:** Monitor live trading (requires IQ Option credentials)
- **Automated Trading:** GitHub Actions รันอัตโนมัติตามตารางเวลา

---

## 📊 V1.4 Performance (30-day Backtest)

| Metric | Value |
|--------|-------|
| **Total Trades** | 32 |
| **Win Rate** | 62.5% ✅ |
| **Total Profit** | $4.00 |
| **ROI** | +4.00% |
| **Profit Factor** | 1.67 🟢 |
| **Max Drawdown** | 4.70% 🟢 |

**Enabled Pairs:**
- ✅ EURUSD (Regular): 1 trade, 100% win, +$0.80
- ✅ EURUSD-OTC: 22 trades, 59.09% win, +$1.40
- ✅ EURCAD: 9 trades, 66.67% win, +$1.80

---

## ⚡ Quick Start (5 นาที)

### Step 1: Clone Repository

```bash
git clone https://github.com/TezukaStar/bot-trade.git
cd bot-trade
```

### Step 2: ตั้งค่า GitHub Secrets (2 นาที)

1. ไปที่ `https://github.com/YOUR_USERNAME/bot-trade/settings/secrets/actions`
2. คลิก "New repository secret"
3. เพิ่ม 3 Secrets:

```
Name:  IQ_EMAIL
Value: your_email@example.com

Name:  IQ_PASSWORD
Value: your_password

Name:  IQ_MODE
Value: PRACTICE
```

### Step 3: เปิดใช้ GitHub Actions (1 นาที)

1. ไปที่ `https://github.com/YOUR_USERNAME/bot-trade/actions`
2. คลิก "I understand my workflows, go ahead and enable them"
3. เลือก workflow "Trading Bot V1.4"
4. คลิก "Run workflow" เพื่อทดสอบ

### Step 4: ดูผลลัพธ์

**ดู Logs:**
```
https://github.com/YOUR_USERNAME/bot-trade/actions
```

**ดู Dashboard:**
```
https://bot-trade.streamlit.app?mode=test
```

✅ เสร็จแล้ว! Bot จะรันอัตโนมัติตามตารางเวลา

---

## 🔧 Configuration

### สำหรับ Live Mode

Add these secrets in Streamlit Cloud → App Settings → Secrets:

```toml
# IQ Option Credentials
iq_email = "your_email@example.com"
iq_password = "your_password"
iq_mode = "PRACTICE"  # or "REAL"

# Trading Configuration
capital = 100
amount = 1
```

### สำหรับ GitHub Actions

ตั้งค่า Secrets ใน GitHub (ตามขั้นตอน Quick Start)

---

## 🧪 Test Mode

### วิธีเปิด Test Mode

**URL ที่ถูกต้อง:**
```
https://your-app.streamlit.app?mode=test
```

ต้องใส่ `?mode=test` ท้าย URL เสมอ!

### ตรวจสอบว่าใช้ Test Mode หรือไม่

ดูที่ header ด้านบน:

| Status | Mode | คำอธิบาย |
|--------|------|----------|
| 📊 BACKTESTING (V1.4) | ✅ Test Mode | ใช้ข้อมูล backtest |
| 🔴 LIVE BOT | ❌ Live Mode | ต้องการ credentials |
| ⚠️ NO TEST DATA | ❌ ไม่มีข้อมูล | เช็ค URL parameter |

### ข้อมูล Test ที่ควรเห็น

- Total Trades: **33**
- Win Rate: **60.61%**
- Total Profit: **$3.00**
- ROI: **+3.00%**
- Testing Period: **30 วัน** (Oct 5 - Nov 4, 2025)

**Breakdown by Pair:**
- EURUSD-OTC: 23 trades (70%)
- EURCAD: 9 trades (27%)
- EURUSD: 1 trade (3%)

### Troubleshooting

**ปัญหา: แสดง "⚠️ NO TEST DATA"**
- **วิธีแก้:** เพิ่ม `?mode=test` ท้าย URL

**ปัญหา: Cache ไม่ refresh**
- **วิธีแก้:** กด **Ctrl + Shift + R** (Windows/Linux) หรือ **Cmd + Shift + R** (Mac)

---

## 📈 Strategy Details

### EURUSD (Regular Market)
- Trading Hours: 19:00-03:00 (Forex open)
- Session Filters: 19-21 PUT, 22-02 CALL
- Performance: 1 trade, 100% win

### EURUSD-OTC
- Trading Hours: 24/7 (OTC Market)
- Session Filters: 12-13 PUT, 18-18 CALL (narrow = better)
- Performance: 22 trades, 59.09% win

### EURCAD
- Trading Hours: 19:00-03:00 (North America session)
- Session Filters: 20-22 PUT, 1-2 CALL
- Performance: 9 trades, 66.67% win, Profit Factor 2.0

---

## 🔑 Key Improvements in V1.4

1. **Multi-Currency Support:** Trade 3 profitable pairs simultaneously
2. **Slope-Based Trend Detection:** More accurate than 2-point comparison
3. **Session Filters:** Optimized trading hours per currency pair
4. **Quality over Quantity:** Narrow session filters → Better win rate
5. **Enhanced Dashboard:** Tabs for easy multi-pair analysis

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit 1.29+
- **Data:** Pandas, NumPy
- **Visualization:** Plotly
- **Trading API:** IQ Option API
- **Technical Analysis:** ta library
- **CI/CD:** GitHub Actions

---

## 📁 File Structure

```
bot-trade/
├── .github/
│   └── workflows/
│       └── trading-bot.yml       # GitHub Actions workflow
├── .streamlit/
│   └── config.toml              # Streamlit theme configuration
├── test_results/
│   └── v1.4_MULTI_1m_30d.csv    # Backtest results
├── versions/
│   └── v1.4/
│       └── config.json          # Trading configuration V1.4
├── bot_v1.4.py                  # Main trading bot
├── dashboard.py                 # Streamlit dashboard
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── DEPLOYMENT.md                # Deployment guide
```

---

## 🚀 Deployment

สำหรับคู่มือการ deploy แบบละเอียด ดูได้ที่ [DEPLOYMENT.md](DEPLOYMENT.md)

**Quick Links:**
- [GitHub Setup](DEPLOYMENT.md#-github-setup)
- [GitHub Actions Setup](DEPLOYMENT.md#-github-actions-setup)
- [Streamlit Cloud Setup](DEPLOYMENT.md#-streamlit-cloud-deployment)

---

## ⚠️ สิ่งที่ต้องจำ

### ✅ ทำ:
- ใช้ PRACTICE mode ก่อนเสมอ
- เช็ค logs ทุกวัน
- ดู Dashboard เป็นประจำ
- ตรวจสอบ Win Rate และ ROI

### ❌ ไม่ทำ:
- อย่าเปลี่ยนเป็น REAL mode โดยไม่ทดสอบ
- อย่าแชร์ Secrets ให้ใคร
- อย่าลืมเช็คว่า bot ยังรันอยู่หรือไม่

---

## 📞 Support

หากมีปัญหา:
1. เช็ค [DEPLOYMENT.md](DEPLOYMENT.md) สำหรับคำตอบ
2. ตรวจสอบ logs ใน GitHub Actions
3. Verify Secrets ตั้งค่าถูกต้อง
4. ทดสอบ manual trigger

---

## 📝 Version History

### V1.4 (Current)
- ✅ Multi-currency support (3 pairs)
- ✅ Slope-based trend detection
- ✅ Enhanced dashboard with tabs
- ✅ Session filters per pair
- **Result:** +4.00% ROI, 62.5% win rate

### V1.3 (Previous)
- Single currency (EURUSD only)
- 5-candle trend detection
- **Result:** +1.40% ROI, 59.09% win rate

---

## 📱 Mobile Support

Dashboard รองรับการแสดงผลบนมือถือ ใช้ URL เดียวกัน:
```
https://your-app.streamlit.app?mode=test
```

---

## 📊 Dashboard Features

### Overview Tab
- Combined metrics from all currency pairs
- Aggregated win/loss chart
- Cumulative equity curve
- Complete trade history

### Individual Pair Tabs
- Metrics specific to each currency pair
- Independent charts and analysis
- Filtered trade list

---

**Created:** November 4, 2025
**Status:** ✅ Production Ready
**Performance:** +4.00% ROI, 62.5% Win Rate
**Tested:** 30-day backtest (Oct 5 - Nov 4, 2025)

---

*"From 1 currency to 3 profitable pairs. Quality over Quantity."* 🎯

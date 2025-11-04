# 📊 Trade Bot Dashboard - V1.4

Real-time trading dashboard for IQ Option Binary Options trading bot with multi-currency support.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 🎯 Features

- **Multi-Currency Support:** EURUSD, EURUSD-OTC, EURCAD
- **Real-time Metrics:** Win rate, ROI, Profit Factor, Max Drawdown
- **Interactive Charts:** Win/Loss pie chart, Equity curve
- **Trade History:** Paginated trade list with detailed analysis
- **Dual Mode:**
  - **Test Mode:** View backtest results
  - **Live Mode:** Monitor live trading (requires IQ Option credentials)

---

## 🚀 Quick Start

### Test Mode (No Setup Required)

View backtest results immediately:

```
https://your-app.streamlit.app?mode=test
```

### Live Mode (Requires Credentials)

1. Configure secrets in Streamlit Cloud (see below)
2. Visit: `https://your-app.streamlit.app`

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

## 🔧 Configuration (Optional - For Live Mode)

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

---

## 📁 File Structure

```
streamlit-deploy/
├── dashboard.py              # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── versions/
│   └── v1.4/
│       └── config.json      # V1.4 multi-currency config
└── test_results/
    └── backtest_results.csv # Backtest results for Test Mode
```

---

## 🎨 Dashboard Features

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

## 🔑 Key Improvements in V1.4

1. **Multi-Currency Support:** Trade 3 profitable pairs simultaneously
2. **Slope-Based Trend Detection:** More accurate than 2-point comparison
3. **Session Filters:** Optimized trading hours per currency pair
4. **Quality over Quantity:** Narrow session filters → Better win rate
5. **Enhanced Dashboard:** Tabs for easy multi-pair analysis

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

## 🛠️ Tech Stack

- **Frontend:** Streamlit 1.29+
- **Data:** Pandas, NumPy
- **Visualization:** Plotly
- **Trading API:** IQ Option API
- **Technical Analysis:** ta library

---

## 📊 Dashboard Screenshots

### Test Mode
- View 30-day backtest results
- No credentials required
- Perfect for demonstration

### Live Mode
- Real-time trade monitoring
- Auto-refresh every 10 seconds
- Complete trade analysis with candlestick charts

---

## 🚨 Important Notes

- **Test Mode:** Uses static backtest data (safe for public viewing)
- **Live Mode:** Requires IQ Option credentials (use secrets)
- **Auto-refresh:** Dashboard updates every 10 seconds
- **Mobile-Friendly:** Responsive design works on all devices
- **Dark Theme:** Matches IQ Option interface

---

## 📞 Support

For issues or questions:
1. Check that all required files are present
2. Verify Streamlit Cloud logs for errors
3. Ensure credentials are set correctly in secrets (for Live Mode)

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

**Created:** November 4, 2025
**Status:** ✅ Production Ready
**Performance:** +4.00% ROI, 62.5% Win Rate
**Tested:** 30-day backtest (Oct 5 - Nov 4, 2025)

---

*"From 1 currency to 3 profitable pairs. Quality over Quantity."* 🎯

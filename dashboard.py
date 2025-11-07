"""
Trade Bot V1.4 - Web Dashboard with Multi-Currency Support & Full Indicators

Usage:
  streamlit run dashboard.py               # Live Bot mode (default)
  streamlit run dashboard.py -- --mode=test  # Backtesting mode

V1.4 Features:
- Multi-currency support (EURUSD, EURUSD-OTC, EURCAD)
- Slope-based trend detection (10 candles)
- Currency-specific parameters
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import json
import numpy as np
import sys

# เช็คโหมดจาก command line arguments และ query parameters
MODE = "live"  # default

# 1. เช็คจาก command line (สำหรับ local: streamlit run dashboard.py -- --mode=test)
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            MODE = arg.split("=")[1]
            break

# 2. เช็คจาก query parameter (สำหรับ browser: ?mode=test)
# ใช้ได้ทั้ง st.query_params (Streamlit >= 1.30) และ st.experimental_get_query_params (เก่า)
try:
    # Try new API first (Streamlit >= 1.30)
    if hasattr(st, 'query_params'):
        query_mode = st.query_params.get("mode", None)
        if query_mode:
            MODE = query_mode
    # Fallback to old API
    elif hasattr(st, 'experimental_get_query_params'):
        query_params = st.experimental_get_query_params()
        if "mode" in query_params:
            MODE = query_params["mode"][0]
except:
    pass  # ถ้าเกิด error ใช้ค่า default

# Page config
st.set_page_config(
    page_title="Trade Bot V1.4 Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for indicators
def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    deltas = np.diff(prices)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return np.concatenate([[np.nan], rsi.values])

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = pd.Series(prices).rolling(window=period).mean()
    std = pd.Series(prices).rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return sma.values, upper_band.values, lower_band.values

def calculate_macd(prices, fast=5, slow=13, signal=3):
    """Calculate MACD (5, 13, 3) - matching strategy.py V1.3"""
    ema_fast = pd.Series(prices).ewm(span=fast, adjust=False).mean()
    ema_slow = pd.Series(prices).ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd.values, signal_line.values, histogram.values

def calculate_adx(high, low, close, period=14):
    """Calculate ADX"""
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    close_series = pd.Series(close)

    # True Range
    tr1 = high_series - low_series
    tr2 = abs(high_series - close_series.shift())
    tr3 = abs(low_series - close_series.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    # Directional Movement
    up_move = high_series - high_series.shift()
    down_move = low_series.shift() - low_series

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
    minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return adx.values, plus_di.values, minus_di.values

# Load functions
@st.cache_data(ttl=10)
def load_trades():
    """
    โหลดข้อมูล trades ตามโหมด:
    - live: อ่านจาก trades.csv (Live Bot)
    - test: อ่านจาก test_results/ (Easy Backtester) หรือ test_tools/paper_trading_results.csv
    """
    if MODE == "test":
        all_dfs = []

        # V1.4: ลองอ่านจาก test_results/ (Easy Backtester)
        test_results_dir = "test_results"
        if os.path.exists(test_results_dir):
            import glob
            # หาไฟล์ v1.4_*.csv
            v14_files = glob.glob(f"{test_results_dir}/v1.4_*.csv")

            for filepath in v14_files:
                try:
                    df = pd.read_csv(filepath)
                    if not df.empty:
                        # ดึงชื่อคู่เงินจากชื่อไฟล์ (เช่น v1.4_EURUSD_1m_30d.csv -> EURUSD)
                        # แต่ถ้ามีคอลัมน์ pair อยู่แล้ว ไม่ต้อง overwrite
                        if 'pair' not in df.columns:
                            filename = os.path.basename(filepath)
                            pair = filename.replace("v1.4_", "").replace("_1m_30d.csv", "")
                            df['pair'] = pair  # เพิ่มคอลัมน์คู่เงิน
                        all_dfs.append(df)
                except:
                    continue

        # ถ้าไม่มีจาก test_results/ ลองอ่านจาก test_tools/ (Paper Trading)
        if not all_dfs:
            test_file = "test_tools/paper_trading_results.csv"
            if os.path.exists(test_file):
                df = pd.read_csv(test_file)
                if not df.empty:
                    df['pair'] = 'UNKNOWN'
                    all_dfs.append(df)

        # รวมทุกไฟล์
        if all_dfs:
            df = pd.concat(all_dfs, ignore_index=True)

            # รองรับทั้ง format เก่า (time, direction) และ format ใหม่ (entry_time, signal)
            if 'entry_time' in df.columns and 'time' not in df.columns:
                df['time'] = pd.to_datetime(df['entry_time'])
            else:
                df['time'] = pd.to_datetime(df['time'])

            if 'signal' in df.columns and 'direction' not in df.columns:
                df['direction'] = df['signal']

            # สร้าง trade_id ถ้ายังไม่มี
            if 'trade_id' not in df.columns:
                df['trade_id'] = [f"trade_{i:03d}" for i in range(len(df))]

            return df, "📊 BACKTESTING (V1.4)"

        return pd.DataFrame(), "⚠️ NO TEST DATA"
    else:
        # โหมด live - อ่านจาก GitHub raw URL (real-time)
        # URL format: https://raw.githubusercontent.com/USERNAME/REPO/BRANCH/FILE
        github_url = "https://raw.githubusercontent.com/TezukaStar/bot-trade/main/trades.csv"

        df = pd.DataFrame()
        data_loaded = False

        # ลอง 1: ดึงจาก GitHub (real-time)
        try:
            df = pd.read_csv(github_url)
            if not df.empty:
                data_loaded = True
        except:
            pass

        # ลอง 2: ถ้าดึงจาก GitHub ไม่สำเร็จ ให้อ่านจาก local file (fallback)
        if not data_loaded:
            live_file = "trades.csv"
            if os.path.exists(live_file):
                try:
                    df = pd.read_csv(live_file)
                    if not df.empty:
                        data_loaded = True
                except:
                    pass

        # ประมวลผลข้อมูล
        if data_loaded and not df.empty:
            # รองรับทั้ง format เก่า (time, direction) และ format ใหม่ (entry_time, signal)
            if 'entry_time' in df.columns and 'time' not in df.columns:
                df['time'] = pd.to_datetime(df['entry_time'])
            else:
                df['time'] = pd.to_datetime(df['time'])

            if 'signal' in df.columns and 'direction' not in df.columns:
                df['direction'] = df['signal']

            # สร้าง trade_id ถ้ายังไม่มี
            if 'trade_id' not in df.columns:
                df['trade_id'] = [f"trade_{i:03d}" for i in range(len(df))]

            return df, "🔴 LIVE BOT"

        return pd.DataFrame(), "⚠️ NO LIVE DATA"

@st.cache_data(ttl=10)
def load_config():
    """
    โหลด config จาก versions/v1.4/config.json

    V1.4 รองรับ multi-currency และมี config แยกตามคู่เงิน
    """
    try:
        # ลองโหลดจาก v1.4 ก่อน
        v14_config = "versions/v1.4/config.json"
        if os.path.exists(v14_config):
            with open(v14_config) as f:
                return json.load(f)

        # ถ้าไม่มี ใช้ config.json ที่ root (v1.3)
        with open("config.json") as f:
            return json.load(f)
    except:
        return {}

def get_bot_status():
    """
    เช็คสถานะของ bot จากข้อมูล trades

    Returns:
        - 🟢 Active: เทรดภายใน 30 นาทีที่ผ่านมา
        - 🟡 Waiting: รอสัญญาณ หรือ นอกช่วงเวลาเทรด
        - ⚪ No Data: ยังไม่มีข้อมูลเทรด
    """
    # ลองดึงข้อมูลจาก GitHub
    try:
        github_url = "https://raw.githubusercontent.com/TezukaStar/bot-trade/main/trades.csv"
        df = pd.read_csv(github_url)
        if not df.empty and 'time' in df.columns:
            # หาเทรดล่าสุด
            df['time'] = pd.to_datetime(df['time'])
            last_trade_time = df['time'].max()
            now = pd.Timestamp.now(tz='UTC').tz_localize(None)
            diff = (now - last_trade_time).total_seconds()
            minutes_ago = int(diff / 60)

            if diff < 1800:  # น้อยกว่า 30 นาที
                return f"🟢 Active (เทรดล่าสุด {minutes_ago} นาที)", "success"
            else:
                return f"🟡 Waiting (เทรดล่าสุด {minutes_ago} นาที)", "warning"
    except Exception as e:
        # ถ้าดึงจาก GitHub ไม่ได้ ลอง local file
        if os.path.exists("trades.csv"):
            try:
                df = pd.read_csv("trades.csv")
                if not df.empty and 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])
                    last_trade_time = df['time'].max()
                    now = pd.Timestamp.now(tz='UTC').tz_localize(None)
                    diff = (now - last_trade_time).total_seconds()
                    minutes_ago = int(diff / 60)

                    if diff < 1800:
                        return f"🟢 Active (เทรดล่าสุด {minutes_ago} นาที)", "success"
                    else:
                        return f"🟡 Waiting (เทรดล่าสุด {minutes_ago} นาที)", "warning"
            except:
                pass

    return "⚪ No Data (ยังไม่มีข้อมูลเทรด)", "info"

# Header
st.markdown('<p class="main-header">🤖 แดชบอร์ด Trade Bot V1.4</p>', unsafe_allow_html=True)

# Load data
trades_df, data_source = load_trades()
config = load_config()

# Status
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    status, status_type = get_bot_status()
    if status_type == "success":
        st.success(f"**สถานะบอท:** {status}")
    elif status_type == "warning":
        st.warning(f"**สถานะบอท:** {status}")
    else:  # info
        st.info(f"**สถานะบอท:** {status}")

with col2:
    version = config.get("version", "1.4")
    st.info(f"**เวอร์ชัน:** {version}")

with col3:
    # แสดงแหล่งข้อมูล
    if "LIVE" in data_source:
        st.success(f"**{data_source}**")
    else:
        st.warning(f"**{data_source}**")

with col4:
    if st.button("🔄 รีเฟรช", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# V1.4: แสดงคู่เงินที่เปิดใช้งาน
if "currencies" in config:
    enabled_pairs = [pair for pair, params in config["currencies"].items() if params.get("enabled", False)]
    if enabled_pairs:
        st.info(f"**💱 คู่เงินที่เปิดใช้งาน:** {', '.join(enabled_pairs)}")

# แสดงช่วงวันที่ในโหมด Test
if MODE == "test" and not trades_df.empty:
    start_date = trades_df['time'].min().strftime('%Y-%m-%d')
    end_date = trades_df['time'].max().strftime('%Y-%m-%d')
    total_days = (trades_df['time'].max() - trades_df['time'].min()).days + 1
    st.success(f"**📅 ช่วงเวลาทดสอบ:** {start_date} ถึง {end_date} ({total_days} วัน)")

if trades_df.empty:
    st.warning("⚠️ ยังไม่มีข้อมูลการเทรด")

    if MODE == "test":
        # โหมด TEST - แสดงวิธีรัน Backtesting
        st.markdown("### 📊 วิธีรัน Backtesting:")
        st.code("""cd test_tools
PYTHONPATH=.. python3 paper_trading_simulator.py \\
  ../data/EURUSD_1m_30d.csv ../config.json""", language="bash")

        st.markdown("""
        **หมายเหตุ:**
        - ทดสอบด้วยข้อมูลย้อนหลัง 30 วัน
        - ใช้เวลาประมาณ 1-2 นาที
        - ผลลัพธ์จะบันทึกใน `test_tools/paper_trading_results.csv`
        """)
    else:
        # โหมด LIVE - แสดงข้อความรอเทรดครั้งแรก
        st.info("🤖 **Bot กำลังรอสัญญาณเทรดครั้งแรก**")

        st.markdown("""
        **ช่วงเวลาที่ Bot จะเทรด:**
        - 🕐 **12:00-13:59** - PUT เท่านั้น (Win Rate 73%)
        - 🕔 **18:00-18:59** - CALL เท่านั้น (Win Rate 60%)

        **Bot จะเทรดอัตโนมัติเมื่อ:**
        1. ถึงช่วงเวลาที่กำหนด
        2. มีสัญญาณจากกลยุทธ์ V1.3
        3. อินดิเคเตอร์ผ่านเกณฑ์ (ADX > 8, MACD, EMA20)

        💡 **Tip:** Dashboard จะอัพเดทอัตโนมัติทุก 10 วินาที เมื่อมีการเทรดครั้งแรก
        """)

    st.stop()

# Helper function to calculate metrics for a dataframe
def calculate_metrics(df, capital):
    """Calculate all trading metrics for a given dataframe"""
    total_trades = len(df)
    wins = len(df[df['result'] == 'win'])
    losses = len(df[df['result'] == 'loss'])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    total_profit = df['profit'].sum()
    current_capital = capital + total_profit
    roi = (total_profit / capital * 100) if capital > 0 else 0

    avg_profit = total_profit / total_trades if total_trades > 0 else 0
    avg_win = df[df['result'] == 'win']['profit'].mean() if wins > 0 else 0
    avg_loss = abs(df[df['result'] == 'loss']['profit'].mean()) if losses > 0 else 0
    profit_factor = (avg_win * wins) / (avg_loss * losses) if (avg_loss * losses) > 0 else 0

    # Calculate max drawdown
    df_sorted = df.sort_values('time')
    equity = [capital]
    for profit in df_sorted['profit']:
        equity.append(equity[-1] + profit)
    peak = equity[0]
    max_dd = 0
    for val in equity:
        if val > peak:
            peak = val
        dd = ((peak - val) / peak * 100) if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd

    # Calculate win/loss streaks
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    for _, trade in df_sorted.iterrows():
        if trade['result'] == 'win':
            current_streak = current_streak + 1 if current_streak > 0 else 1
            max_win_streak = max(max_win_streak, current_streak)
        else:
            current_streak = current_streak - 1 if current_streak < 0 else -1
            max_loss_streak = max(max_loss_streak, abs(current_streak))

    return {
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'total_profit': total_profit,
        'current_capital': current_capital,
        'roi': roi,
        'avg_profit': avg_profit,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'max_dd': max_dd,
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'equity': equity
    }

# Calculate overall metrics
start_capital = config.get('capital', 100)
metrics = calculate_metrics(trades_df, start_capital)

# Helper function to render full metrics display
def render_metrics(metrics_dict, df):
    """Render complete metrics display with 2 rows"""
    st.markdown("### 📊 ตัวชี้วัดประสิทธิภาพ")

    # Main metrics (Row 1)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("💰 กำไรรวม", f"${metrics_dict['total_profit']:.2f}", f"{metrics_dict['roi']:.2f}% ROI",
                  delta_color="normal" if metrics_dict['total_profit'] >= 0 else "inverse")

    with col2:
        st.metric("💵 ทุนปัจจุบัน", f"${metrics_dict['current_capital']:.2f}", f"${metrics_dict['total_profit']:.2f}",
                  delta_color="normal" if metrics_dict['total_profit'] >= 0 else "inverse")

    with col3:
        # Win rate with color indicator
        win_status = "🟢" if metrics_dict['win_rate'] >= 60 else "🟡" if metrics_dict['win_rate'] >= 55 else "🔴"
        st.metric(f"{win_status} อัตราชนะ", f"{metrics_dict['win_rate']:.1f}%", f"{metrics_dict['wins']}ชนะ / {metrics_dict['losses']}แพ้")

    with col4:
        st.metric("📊 จำนวนเทรด", metrics_dict['total_trades'],
                  f"เฉลี่ย ${metrics_dict['avg_profit']:.2f}/เทรด")

    with col5:
        today = datetime.now().strftime("%Y-%m-%d")
        today_trades = df[df['time'].dt.strftime("%Y-%m-%d") == today]
        today_profit = today_trades['profit'].sum() if not today_trades.empty else 0
        today_win_rate = (len(today_trades[today_trades['result'] == 'win']) / len(today_trades) * 100) if len(today_trades) > 0 else 0
        st.metric("📅 กำไรวันนี้", f"${today_profit:.2f}",
                  f"{len(today_trades)} เทรด • {today_win_rate:.0f}% ชนะ",
                  delta_color="normal" if today_profit >= 0 else "inverse")

    # Additional metrics (Row 2)
    st.markdown("")  # Small spacing
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        pf_color = "🟢" if metrics_dict['profit_factor'] >= 1.5 else "🟡" if metrics_dict['profit_factor'] >= 1.0 else "🔴"
        st.metric(f"{pf_color} Profit Factor", f"{metrics_dict['profit_factor']:.2f}",
                  "ดี" if metrics_dict['profit_factor'] >= 1.5 else "พอใช้" if metrics_dict['profit_factor'] >= 1.0 else "แย่")

    with col2:
        st.metric("📈 กำไรเฉลี่ย/ชนะ", f"${metrics_dict['avg_win']:.2f}",
                  f"เฉลี่ย {metrics_dict['avg_win']/5*100:.1f}% ต่อเทรด")

    with col3:
        st.metric("📉 ขาดทุนเฉลี่ย/แพ้", f"${metrics_dict['avg_loss']:.2f}",
                  f"เฉลี่ย {metrics_dict['avg_loss']/5*100:.1f}% ต่อเทรด")

    with col4:
        dd_color = "🟢" if metrics_dict['max_dd'] < 5 else "🟡" if metrics_dict['max_dd'] < 10 else "🔴"
        st.metric(f"{dd_color} Max Drawdown", f"{metrics_dict['max_dd']:.2f}%",
                  "ต่ำ" if metrics_dict['max_dd'] < 5 else "ปานกลาง" if metrics_dict['max_dd'] < 10 else "สูง")

    with col5:
        st.metric("🔥 Streak สูงสุด", f"↗️{metrics_dict['max_win_streak']} / ↘️{metrics_dict['max_loss_streak']}",
                  f"ชนะติด {metrics_dict['max_win_streak']} • แพ้ติด {metrics_dict['max_loss_streak']}")

    st.markdown("---")

# Helper function to render charts for any dataframe
def render_charts(df, metrics_dict, pair_name="All Pairs"):
    """Render Win/Loss Pie Chart and Equity Curve for given dataframe"""
    st.markdown(f"### 📈 กราฟแสดงผล")

    col1, col2 = st.columns(2)

    with col1:
        # Win/Loss Pie Chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['ชนะ', 'แพ้'],
            values=[metrics_dict['wins'], metrics_dict['losses']],
            hole=0.4,
            marker=dict(colors=['#00c853', '#ff1744']),
            textinfo='label+percent+value',
            textfont=dict(size=14, color='white')
        )])

        fig_pie.update_layout(
            title=dict(
                text=f"สัดส่วนชนะ/แพ้ (อัตราชนะ {metrics_dict['win_rate']:.1f}%)",
                font=dict(size=16, color='#e0e0e0')
            ),
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            font=dict(color='#e0e0e0'),
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='#404040',
                borderwidth=1
            ),
            height=350
        )

        st.plotly_chart(fig_pie, width='stretch')

    with col2:
        # Equity Curve
        equity = metrics_dict['equity']

        fig_equity = go.Figure()

        fig_equity.add_trace(go.Scatter(
            x=list(range(len(equity))),
            y=equity,
            mode='lines+markers',
            name='Capital',
            line=dict(color='#2196f3', width=3),
            marker=dict(size=6, color='#2196f3'),
            fill='tozeroy',
            fillcolor='rgba(33, 150, 243, 0.1)'
        ))

        fig_equity.update_layout(
            title=dict(
                text=f"กราฟทุนสะสม (ROI: {metrics_dict['roi']:.2f}%)",
                font=dict(size=16, color='#e0e0e0')
            ),
            xaxis_title="หมายเลขเทรด",
            yaxis_title="ทุน ($)",
            paper_bgcolor='#1a1a1a',
            plot_bgcolor='#1a1a1a',
            font=dict(color='#e0e0e0'),
            showlegend=False,
            height=350,
            xaxis=dict(gridcolor='#2d2d2d', showgrid=True),
            yaxis=dict(gridcolor='#2d2d2d', showgrid=True),
            hovermode='x unified'
        )

        st.plotly_chart(fig_equity, width='stretch')

# Helper function to render trade list with pagination
def render_trade_list(df, tab_key=""):
    """Render paginated trade list for given dataframe"""
    st.markdown("---")
    st.markdown("### 📝 รายการเทรด (คลิกเพื่อดูกราฟแท่งเทียนจริง + อินดิเคเตอร์ทั้งหมด)")

    # Pagination settings
    trades_per_page = 10
    total_trades_count = len(df)
    total_pages = max(1, (total_trades_count + trades_per_page - 1) // trades_per_page)

    # Initialize page number in session state with unique key per tab
    page_key = f'page_number_{tab_key}'
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    # Ensure page number is within valid range
    if st.session_state[page_key] > total_pages:
        st.session_state[page_key] = total_pages
    if st.session_state[page_key] < 1:
        st.session_state[page_key] = 1

    # Pagination controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    current_page = st.session_state[page_key]

    with col1:
        if st.button("⏮️ แรกสุด", disabled=(current_page <= 1), key=f"first_page_{tab_key}"):
            st.session_state[page_key] = 1
            st.rerun()

    with col2:
        if st.button("◀️ ก่อนหน้า", disabled=(current_page <= 1), key=f"prev_page_{tab_key}"):
            st.session_state[page_key] -= 1
            st.rerun()

    with col3:
        st.markdown(f"<div style='text-align: center; padding: 5px'>หน้า {current_page} จาก {total_pages} ({total_trades_count} เทรดทั้งหมด)</div>", unsafe_allow_html=True)

    with col4:
        if st.button("ถัดไป ▶️", disabled=(current_page >= total_pages), key=f"next_page_{tab_key}"):
            st.session_state[page_key] += 1
            st.rerun()

    with col5:
        if st.button("ท้ายสุด ⏭️", disabled=(current_page >= total_pages), key=f"last_page_{tab_key}"):
            st.session_state[page_key] = total_pages
            st.rerun()

    # Get trades for current page (reversed order - newest first)
    trades_df_sorted = df.sort_values('time', ascending=False).reset_index(drop=True)
    start_idx = (current_page - 1) * trades_per_page
    end_idx = min(start_idx + trades_per_page, total_trades_count)
    page_trades = trades_df_sorted.iloc[start_idx:end_idx]

    # Display trades (exactly 10 per page, fill with empty rows if needed)
    for i in range(trades_per_page):
        if i < len(page_trades):
            # Show real trade data
            trade = page_trades.iloc[i]
            result_color = "🟢" if trade['result'] == 'win' else "🔴"
            direction_icon = "🔼" if trade['direction'] == 'call' else "🔽"

            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])

            with col1:
                st.text(trade['time'].strftime('%Y-%m-%d %H:%M:%S'))
            with col2:
                st.text(f"{direction_icon} {trade['direction'].upper()}")
            with col3:
                st.text(f"{result_color} {trade['result'].upper()}")
            with col4:
                profit_color = "green" if trade['profit'] > 0 else "red"
                st.markdown(f"<span style='color: {profit_color}'>${trade['profit']:.2f}</span>", unsafe_allow_html=True)
            with col5:
                st.text(f"${trade['capital']:.2f}")
            with col6:
                # Use trade_id to create unique key
                actual_idx = start_idx + i
                trade_id = trade.get('trade_id', f"trade_{actual_idx}")
                if st.button("📊 ดูรายละเอียด", key=f"view_{trade_id}_{tab_key}_{current_page}"):
                    st.session_state['selected_trade_id'] = trade_id
                    st.rerun()
        else:
            # Show empty placeholder to keep layout consistent
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            with col1:
                st.text("")
            with col2:
                st.text("")
            with col3:
                st.text("")
            with col4:
                st.text("")
            with col5:
                st.text("")
            with col6:
                st.text("")

# Create tabs for Overview and individual pairs
if 'pair' in trades_df.columns:
    # V1.4: Multi-currency mode - create tabs
    unique_pairs = sorted(trades_df['pair'].unique())
    tab_names = ["📊 ภาพรวมทั้งหมด"] + [f"💱 {pair}" for pair in unique_pairs]
    tabs = st.tabs(tab_names)

    # Tab 0: Overview (All Pairs)
    with tabs[0]:
        render_metrics(metrics, trades_df)
        render_charts(trades_df, metrics, "ภาพรวมทั้งหมด")
        render_trade_list(trades_df, "overview")

    # Individual pair tabs
    for idx, pair in enumerate(unique_pairs):
        with tabs[idx + 1]:
            pair_df = trades_df[trades_df['pair'] == pair]
            pair_metrics = calculate_metrics(pair_df, start_capital)

            render_metrics(pair_metrics, pair_df)
            render_charts(pair_df, pair_metrics, pair)
            render_trade_list(pair_df, pair)
else:
    # V1.3 or earlier - single currency mode
    render_metrics(metrics, trades_df)
    render_charts(trades_df, metrics, "EURUSD")
    render_trade_list(trades_df, "eurusd")

# Show detail if selected
if 'selected_trade_id' in st.session_state:
    st.markdown("---")
    st.markdown("## 🔍 การวิเคราะห์เทรดละเอียด - ข้อมูลจริง + อินดิเคเตอร์ทั้งหมด")

    # Find the trade by trade_id
    trade_id = st.session_state['selected_trade_id']
    selected_trade = trades_df[trades_df['trade_id'] == trade_id].iloc[0] if 'trade_id' in trades_df.columns and trade_id in trades_df['trade_id'].values else None

    if selected_trade is None:
        st.error("ไม่พบข้อมูลเทรดที่เลือก")
        del st.session_state['selected_trade_id']
    else:
        if st.button("❌ ปิด"):
            del st.session_state['selected_trade_id']

        # Trade info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("เวลาเทรด", selected_trade['time'].strftime('%Y-%m-%d %H:%M:%S'))
        with col2:
            direction = f"{'🔼 CALL' if selected_trade['direction'] == 'call' else '🔽 PUT'}"
            st.metric("ทิศทาง", direction)
        with col3:
            result = f"{'✅ ชนะ' if selected_trade['result'] == 'win' else '❌ แพ้'}"
            color = 'green' if selected_trade['result'] == 'win' else 'red'
            st.markdown(f"<h3 style='color: {color}'>{result}</h3>", unsafe_allow_html=True)

        # Metrics
        st.markdown("### 💰 ตัวชี้วัดเทรด")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("กำไร/ขาดทุน", f"${selected_trade['profit']:.2f}")

        with col2:
            st.metric("ทุนหลังเทรด", f"${selected_trade['capital']:.2f}")

        with col3:
            if 'adx' in selected_trade:
                adx_value = selected_trade['adx']
                adx_status = "✅ แรง" if adx_value > 20 else "⚠️ อ่อน"
                st.metric("ADX", f"{adx_value:.1f}", adx_status)

        with col4:
            if 'macd' in selected_trade:
                macd_value = selected_trade['macd']
                macd_status = "✅ ดี" if abs(macd_value) > 0.0005 else "⚠️ อ่อน"
                st.metric("MACD", f"{macd_value:.4f}", macd_status)

        # Load real candles from CSV data
        trade_time = selected_trade['time']
        pair = selected_trade.get('pair', 'EURUSD')

        # Try to load candles from CSV file
        candles_loaded = False
        candles = []

        # First try JSON file (old format)
        trade_id = selected_trade['trade_id']
        candle_file = f"data/candles/{trade_id}.json"

        if os.path.exists(candle_file):
            with open(candle_file, 'r') as f:
                candles = json.load(f)
            candles_loaded = True if len(candles) > 0 else False

        # If no JSON, load from CSV
        if not candles_loaded and os.path.exists("data/EURUSD_1m_30d.csv"):
            df_candles = pd.read_csv("data/EURUSD_1m_30d.csv")
            df_candles['time'] = pd.to_datetime(df_candles['time'])

            # Get 50 candles before trade time
            mask = df_candles['time'] <= trade_time
            candle_data = df_candles[mask].tail(50)

            if len(candle_data) > 0:
                # Convert to JSON-like format
                candles = []
                for _, row in candle_data.iterrows():
                    candles.append({
                        'time': row['time'].timestamp(),
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    })
                candles_loaded = True

        # If still no data (e.g., in TEST mode), generate mock candles
        if not candles_loaded:
            st.info("📊 Generating mock candles for demonstration (Test Mode)")

            # Generate 50 realistic mock candles
            base_price = 1.08000  # EURUSD typical price
            current_price = base_price
            mock_candles = []

            # Start from 50 minutes before trade time
            start_time = trade_time - timedelta(minutes=50)

            for i in range(50):
                candle_time = start_time + timedelta(minutes=i)

                # Random price movement
                price_change = np.random.normal(0, 0.0002)  # Small realistic movements
                open_price = current_price
                close_price = current_price + price_change

                # High/Low with small spreads
                high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.0001))
                low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.0001))

                volume = np.random.randint(50, 200)

                mock_candles.append({
                    'time': candle_time.timestamp(),
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })

                current_price = close_price

            candles = mock_candles
            candles_loaded = True

        if candles_loaded and len(candles) > 0:
                # Check if it's mock or real data
                if not os.path.exists(candle_file) and not os.path.exists("data/EURUSD_1m_30d.csv"):
                    # Mock data
                    pass  # Info message already shown above
                else:
                    st.success(f"✅ Loaded {len(candles)} REAL candles from IQ Option historical data")

                # Extract data
                timestamps = [datetime.fromtimestamp(c['time']) for c in candles]
                opens = [c['open'] for c in candles]
                highs = [c['high'] for c in candles]
                lows = [c['low'] for c in candles]
                closes = [c['close'] for c in candles]
                volumes = [c['volume'] for c in candles]

                # Calculate indicators
                ema20 = pd.Series(closes).ewm(span=20, adjust=False).mean().values
                rsi = calculate_rsi(closes)
                bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(closes)
                macd, macd_signal, macd_hist = calculate_macd(closes)
                adx, plus_di, minus_di = calculate_adx(highs, lows, closes)

                # Create comprehensive chart with dark theme like IQ Option
                fig = make_subplots(
                    rows=4, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.5, 0.15, 0.15, 0.2],
                    subplot_titles=('EURUSD 1-Minute Chart with EMA20 & Bollinger Bands',
                                   'RSI (14)',
                                   'MACD (5,13,3)',
                                   'ADX (14) & Volume')
                )

                # Row 1: Candlestick + EMA + Bollinger Bands (IQ Option style)
                fig.add_trace(
                    go.Candlestick(
                        x=timestamps,
                        open=opens,
                        high=highs,
                        low=lows,
                        close=closes,
                        name='EURUSD',
                        increasing_line_color='#00c853',
                        decreasing_line_color='#ff1744',
                        increasing_fillcolor='#00c853',
                        decreasing_fillcolor='#ff1744',
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )

                # EMA20 - Orange like IQ Option
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=ema20,
                        mode='lines',
                        name='EMA20',
                        line=dict(color='#ff9800', width=2)
                    ),
                    row=1, col=1
                )

                # Bollinger Bands - subtle gray
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=bb_upper,
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='#666666', width=1, dash='dot'),
                        opacity=0.4,
                        showlegend=False
                    ),
                    row=1, col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=bb_lower,
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='#666666', width=1, dash='dot'),
                        fill='tonexty',
                        fillcolor='rgba(100, 100, 100, 0.05)',
                        opacity=0.4,
                        showlegend=False
                    ),
                    row=1, col=1
                )

                # Entry point - use last candle's timestamp and close price
                entry_time = timestamps[-1]
                entry_price = closes[-1]

                # Determine direction from selected_trade
                is_call = selected_trade['direction'] == 'call'

                # Use triangle arrows with side annotation
                marker_symbol = 'triangle-up' if is_call else 'triangle-down'
                marker_color = '#00ff00' if is_call else '#ff0000'  # Bright green for CALL, Red for PUT
                text_label = 'CALL ▲' if is_call else 'PUT ▼'

                fig.add_trace(
                    go.Scatter(
                        x=[entry_time],
                        y=[entry_price],
                        mode='markers+text',
                        name='ENTRY POINT',
                        marker=dict(
                            size=20,
                            color=marker_color,
                            symbol=marker_symbol,
                            line=dict(color='white', width=2)
                        ),
                        text=[text_label],
                        textposition='middle right' if is_call else 'middle right',
                        textfont=dict(size=12, color=marker_color, family='Arial Black'),
                        showlegend=True
                    ),
                    row=1, col=1
                )

                # Row 2: RSI
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=rsi,
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple', width=2)
                    ),
                    row=2, col=1
                )

                # RSI levels
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1, opacity=0.5)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1, opacity=0.5)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1, opacity=0.3)

                # Row 3: MACD - IQ Option style
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=macd,
                        mode='lines',
                        name='MACD',
                        line=dict(color='#2196f3', width=2)
                    ),
                    row=3, col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=macd_signal,
                        mode='lines',
                        name='Signal',
                        line=dict(color='#ff9800', width=2)
                    ),
                    row=3, col=1
                )

                # MACD Histogram with vibrant colors like IQ Option
                colors_macd = ['#00c853' if h >= 0 else '#ff1744' for h in macd_hist]
                fig.add_trace(
                    go.Bar(
                        x=timestamps,
                        y=macd_hist,
                        name='Histogram',
                        marker_color=colors_macd,
                        opacity=0.7,
                        showlegend=False
                    ),
                    row=3, col=1
                )

                # Row 4: ADX + Volume
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=adx,
                        mode='lines',
                        name='ADX',
                        line=dict(color='purple', width=2),
                        yaxis='y4'
                    ),
                    row=4, col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=plus_di,
                        mode='lines',
                        name='+DI',
                        line=dict(color='green', width=1),
                        yaxis='y4'
                    ),
                    row=4, col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=minus_di,
                        mode='lines',
                        name='-DI',
                        line=dict(color='red', width=1),
                        yaxis='y4'
                    ),
                    row=4, col=1
                )

                # ADX threshold
                fig.add_hline(y=8, line_dash="dash", line_color="gray", row=4, col=1,
                             annotation_text="ADX Threshold (8)")

                # Update layout with dark theme like IQ Option
                fig.update_xaxes(
                    title_text="Time",
                    row=4, col=1,
                    gridcolor='#2d2d2d',
                    showgrid=True
                )
                fig.update_yaxes(
                    title_text="Price",
                    row=1, col=1,
                    gridcolor='#2d2d2d',
                    showgrid=True
                )
                fig.update_yaxes(
                    title_text="RSI",
                    row=2, col=1,
                    range=[0, 100],
                    gridcolor='#2d2d2d',
                    showgrid=True
                )
                fig.update_yaxes(
                    title_text="MACD",
                    row=3, col=1,
                    gridcolor='#2d2d2d',
                    showgrid=True
                )
                fig.update_yaxes(
                    title_text="ADX / DI",
                    row=4, col=1,
                    gridcolor='#2d2d2d',
                    showgrid=True
                )

                # Dark theme layout like IQ Option
                fig.update_layout(
                    height=1000,
                    showlegend=True,
                    hovermode='x unified',
                    xaxis_rangeslider_visible=False,
                    template='plotly_dark',
                    paper_bgcolor='#1a1a1a',
                    plot_bgcolor='#1a1a1a',
                    font=dict(color='#e0e0e0', size=12),
                    legend=dict(
                        bgcolor='rgba(0,0,0,0.5)',
                        bordercolor='#404040',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=50, b=50)
                )

                st.plotly_chart(fig, width='stretch')

                # Signal analysis
                st.markdown("### 🎯 การวิเคราะห์สัญญาณ")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### เงื่อนไขการเข้าเทรด")
                    if 'signal_reason' in selected_trade:
                        st.info(f"**เหตุผล:** {selected_trade['signal_reason']}")

                    if 'adx' in selected_trade and 'macd' in selected_trade:
                        st.markdown("**อินดิเคเตอร์ ณ จุดเข้าเทรด:**")
                        adx_check = "✅" if selected_trade['adx'] > 8 else "❌"
                        st.write(f"{adx_check} ADX: {selected_trade['adx']:.2f} (เกณฑ์: > 8)")

                        macd_check = "✅" if abs(selected_trade['macd']) > 0.0005 else "❌"
                        st.write(f"{macd_check} MACD: {selected_trade['macd']:.4f} (เกณฑ์: > 0.0005)")

                        if 'close_price' in selected_trade and 'ema20' in selected_trade:
                            price_ema_diff = abs(selected_trade['close_price'] - selected_trade['ema20'])
                            price_ema_pct = (price_ema_diff / selected_trade['close_price']) * 100
                            price_check = "✅" if price_ema_pct < 0.5 else "❌"
                            st.write(f"{price_check} ราคา vs EMA20: {price_ema_pct:.2f}% (เกณฑ์: < 0.5%)")

                with col2:
                    st.markdown("#### ผลลัพธ์การเทรด")
                    if selected_trade['result'] == 'win':
                        st.success(f"✅ **ชนะ** - กำไร: ${selected_trade['profit']:.2f}")
                        st.write("กลยุทธ์ทำงานตามที่คาดไว้!")
                        st.write("✓ อินดิเคเตอร์ทั้งหมดสอดคล้องกัน")
                        st.write("✓ จังหวะเข้าเทรดดี")
                    else:
                        st.error(f"❌ **แพ้** - ขาดทุน: ${selected_trade['profit']:.2f}")
                        st.write("**สาเหตุที่เป็นไปได้:**")
                        if 'adx' in selected_trade and selected_trade['adx'] < 20:
                            st.write("⚠️ ADX ต่ำ (เทรนด์อ่อน)")
                        if 'signal_reason' in selected_trade:
                            if 'Weak' in str(selected_trade['signal_reason']) or 'Reversal' in str(selected_trade['signal_reason']):
                                st.write("⚠️ สัญญาณอ่อนตอนเข้าเทรด")
                        st.write("⚠️ ตลาดกลับตัว หรือมีข่าวกระทบ")

                # Trading context
                st.markdown("### 📝 บริบทการเทรด")

                hour = selected_trade['time'].hour

                if 12 <= hour <= 13:
                    st.info("⏰ **ช่วงเวลา:** 12:00-13:59 (PUT เท่านั้น) - ช่วงพรีเมี่ยม (อัตราชนะ 71-75%)")
                elif hour == 18:
                    st.info("⏰ **ช่วงเวลา:** 18:00-18:59 (CALL เท่านั้น) - ช่วงดี (อัตราชนะ 60%)")
                elif 14 <= hour <= 17:
                    st.warning("⚠️ **ช่วงเวลา:** 14:00-17:59 - หลีกเลี่ยงการเทรด (อัตราชนะ 0%)")
                else:
                    st.warning("⚠️ **ช่วงเวลา:** นอกเวลาที่แนะนำ")

        else:
            st.error(f"❌ ไม่พบไฟล์ข้อมูลแท่งเทียน: {candle_file}")
            st.info("ข้อมูลแท่งเทียนจริงจะถูกบันทึกเมื่อบอทรันสด")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9rem'>
    🤖 Trade Bot V1.3 Dashboard | ข้อมูลจริงพร้อม EMA20, RSI, MACD, ADX, Bollinger Bands
</div>
""", unsafe_allow_html=True)

# Auto-refresh
import time
time.sleep(10)
st.rerun()

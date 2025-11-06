#!/usr/bin/env python3
"""
Trade Bot V1.4 - Multi-Currency Binary Options Trading Bot
Connects to IQ Option and executes trades based on V1.4 strategy

Usage:
  python bot_v1.4.py                    # Practice account (default)
  python bot_v1.4.py --mode=practice    # Practice account
  python bot_v1.4.py --mode=real        # Real account (BE CAREFUL!)

Features:
- Multi-currency support (EURUSD, EURUSD-OTC, EURCAD)
- Slope-based trend detection
- Session filters per currency pair
- Risk management (stop loss, daily loss limit)
- Auto-saves trades to trades.csv for dashboard
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import IQ Option API
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    print("❌ Error: iqoptionapi not installed")
    print("   Install it with: pip install iqoptionapi")
    sys.exit(1)

# Import TA library for indicators
try:
    import ta
except ImportError:
    print("❌ Error: ta library not installed")
    print("   Install it with: pip install ta")
    sys.exit(1)


class TradeBotV14:
    """Trade Bot V1.4 with Multi-Currency Support"""

    def __init__(self, mode="practice"):
        """
        Initialize the trading bot

        Args:
            mode: "practice" or "real" (default: practice)
        """
        self.mode = mode.upper()
        self.config = self.load_config()
        self.trades = []
        self.capital = self.config.get("capital", 100)
        self.daily_profit = 0
        self.daily_trades = 0
        self.api = None

        # Load credentials from environment
        self.email = os.getenv("IQ_EMAIL")
        self.password = os.getenv("IQ_PASSWORD")

        if not self.email or not self.password:
            raise ValueError("❌ IQ_EMAIL and IQ_PASSWORD must be set in .env file")

        print(f"✅ Bot initialized in {self.mode} mode")
        print(f"💰 Starting capital: ${self.capital}")

    def load_config(self):
        """Load configuration from versions/v1.4/config.json"""
        config_path = "versions/v1.4/config.json"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"✅ Loaded config V{config['version']}")
        return config

    def connect(self):
        """Connect to IQ Option"""
        print(f"\n🔌 Connecting to IQ Option ({self.mode})...")

        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()

        if not check:
            raise ConnectionError(f"❌ Failed to connect: {reason}")

        print("✅ Connected successfully")

        # Change to practice/real account
        if self.mode == "PRACTICE":
            self.api.change_balance("PRACTICE")
            print("✅ Switched to PRACTICE account")
        else:
            self.api.change_balance("REAL")
            print("⚠️  Switched to REAL account - BE CAREFUL!")

        # Get current balance
        balance = self.api.get_balance()
        print(f"💰 Current balance: ${balance:.2f}")

        return True

    def get_candles(self, pair, timeframe=60, count=100):
        """
        Get historical candles for a currency pair

        Args:
            pair: Currency pair (e.g., "EURUSD", "EURUSD-OTC")
            timeframe: Candle timeframe in seconds (default: 60 = 1 minute)
            count: Number of candles to fetch (default: 100)

        Returns:
            DataFrame with OHLC data
        """
        try:
            candles = self.api.get_candles(pair, timeframe, count, time.time())

            if not candles:
                return pd.DataFrame()

            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s')
            df = df.rename(columns={
                'open': 'open',
                'close': 'close',
                'min': 'low',
                'max': 'high',
                'volume': 'volume'
            })

            return df[['time', 'open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            print(f"❌ Error fetching candles for {pair}: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df, config):
        """
        Calculate technical indicators

        Args:
            df: DataFrame with OHLC data
            config: Currency-specific config

        Returns:
            DataFrame with indicators added
        """
        if df.empty or len(df) < 50:
            return df

        # Get indicator parameters
        ind = config.get('indicators', self.config['default_indicators'])

        # ADX (Average Directional Index)
        adx_indicator = ta.trend.ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )
        df['adx'] = adx_indicator.adx()
        df['adx_pos'] = adx_indicator.adx_pos()
        df['adx_neg'] = adx_indicator.adx_neg()

        # MACD
        macd_indicator = ta.trend.MACD(
            close=df['close'],
            window_slow=13,
            window_fast=5,
            window_sign=3
        )
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_diff'] = macd_indicator.macd_diff()

        # RSI
        rsi_period = ind.get('rsi_period', 14)
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'],
            window=rsi_period
        ).rsi()

        # Bollinger Bands
        bb_period = ind.get('bollinger_period', 20)
        bb_std = ind.get('bollinger_std', 2)
        bollinger = ta.volatility.BollingerBands(
            close=df['close'],
            window=bb_period,
            window_dev=bb_std
        )
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        df['bb_low'] = bollinger.bollinger_lband()

        # EMA
        ema_period = ind.get('ema_period', 20)
        df['ema20'] = ta.trend.EMAIndicator(
            close=df['close'],
            window=ema_period
        ).ema_indicator()

        # Slope-based trend (10 candles)
        df['slope'] = df['close'].diff(10) / 10

        return df

    def check_trading_hours(self, pair_config):
        """Check if current time is within trading hours"""
        now = datetime.utcnow()
        current_hour = now.hour

        start = pair_config['trading_hours']['start']
        end = pair_config['trading_hours']['end']

        # Handle overnight trading (e.g., 19:00-03:00)
        if start > end:
            return current_hour >= start or current_hour < end
        else:
            return start <= current_hour < end

    def check_session_filter(self, pair_config):
        """
        Check session filter and return allowed direction

        Returns:
            "call", "put", or None
        """
        now = datetime.utcnow()
        current_hour = now.hour

        session_filters = pair_config.get('session_filters', {})

        for session, direction in session_filters.items():
            # Parse session (e.g., "12-13", "18-18")
            start, end = map(int, session.split('-'))

            # Check if current hour is in session
            if start <= current_hour <= end:
                return direction.lower()

        return None

    def generate_signal(self, pair, pair_config):
        """
        Generate trading signal for a currency pair

        Returns:
            dict with signal info or None
        """
        # Check trading hours
        if not self.check_trading_hours(pair_config):
            return None

        # Check session filter
        allowed_direction = self.check_session_filter(pair_config)
        if not allowed_direction:
            return None

        # Get candles
        df = self.get_candles(pair)
        if df.empty or len(df) < 50:
            return None

        # Calculate indicators
        df = self.calculate_indicators(df, pair_config)

        # Get latest values
        latest = df.iloc[-1]
        ind = pair_config.get('indicators', self.config['default_indicators'])

        # Check ADX
        if latest['adx'] < ind['adx_min']:
            return None

        # Check MACD
        if abs(latest['macd']) < ind['macd_min']:
            return None

        # Check Price-EMA distance
        price_ema_dist = abs(latest['close'] - latest['ema20']) / latest['close']
        if price_ema_dist > ind['price_ema_max']:
            return None

        # Determine signal based on slope and indicators
        signal = None

        if latest['slope'] > 0 and latest['macd'] > 0 and allowed_direction == 'call':
            signal = 'call'
        elif latest['slope'] < 0 and latest['macd'] < 0 and allowed_direction == 'put':
            signal = 'put'

        if not signal:
            return None

        return {
            'pair': pair,
            'signal': signal,
            'price': latest['close'],
            'adx': latest['adx'],
            'macd': latest['macd'],
            'rsi': latest['rsi'],
            'ema20': latest['ema20'],
            'slope': latest['slope'],
            'time': latest['time']
        }

    def execute_trade(self, signal):
        """
        Execute a binary options trade

        Args:
            signal: Signal dictionary from generate_signal()

        Returns:
            Trade result dictionary
        """
        pair = signal['pair']
        direction = signal['signal']
        amount = self.config['amount']

        print(f"\n📊 Executing trade:")
        print(f"   Pair: {pair}")
        print(f"   Direction: {direction.upper()}")
        print(f"   Amount: ${amount}")
        print(f"   Entry Price: {signal['price']:.5f}")

        # Execute trade via IQ Option API
        try:
            # Buy binary option (1 minute expiry)
            status, trade_id = self.api.buy(amount, pair, direction, 1)

            if not status:
                print("❌ Trade failed")
                return None

            print(f"✅ Trade opened (ID: {trade_id})")

            # Wait for trade to close (1 minute + 5 seconds buffer)
            print("⏳ Waiting for trade result...")
            time.sleep(65)

            # Get trade result
            result = self.api.check_win_v4(trade_id)

            if result > 0:
                profit = result
                outcome = "win"
                print(f"✅ Trade WON - Profit: ${profit:.2f}")
            elif result == 0:
                profit = 0
                outcome = "tie"
                print(f"⚖️  Trade TIE - No profit/loss")
            else:
                profit = -amount
                outcome = "loss"
                print(f"❌ Trade LOST - Loss: ${amount:.2f}")

            # Update capital and stats
            self.capital += profit
            self.daily_profit += profit
            self.daily_trades += 1

            # Create trade record
            trade_record = {
                'trade_id': trade_id,
                'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'pair': pair,
                'direction': direction,
                'entry_price': signal['price'],
                'amount': amount,
                'result': outcome,
                'profit': profit,
                'capital': self.capital,
                'adx': signal['adx'],
                'macd': signal['macd'],
                'rsi': signal['rsi'],
                'ema20': signal['ema20']
            }

            self.trades.append(trade_record)
            self.save_trades()

            return trade_record

        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            return None

    def save_trades(self):
        """Save trades to trades.csv"""
        if not self.trades:
            return

        df = pd.DataFrame(self.trades)
        df.to_csv('trades.csv', index=False)
        print(f"💾 Saved {len(self.trades)} trades to trades.csv")

    def check_risk_limits(self):
        """Check if risk limits are exceeded"""
        risk = self.config['risk']

        # Check stop loss
        total_loss = self.capital - self.config['capital']
        if total_loss <= -risk['stop_loss']:
            print(f"🛑 Stop loss reached: ${total_loss:.2f}")
            return False

        # Check daily loss limit
        if self.daily_profit <= -risk['daily_loss_limit']:
            print(f"🛑 Daily loss limit reached: ${self.daily_profit:.2f}")
            return False

        # Check max trades per day
        if self.daily_trades >= risk['max_trades_per_day']:
            print(f"🛑 Max trades per day reached: {self.daily_trades}")
            return False

        return True

    def run(self):
        """Main bot loop"""
        print("\n" + "="*60)
        print("🤖 Trade Bot V1.4 Starting...")
        print("="*60)

        # Connect to IQ Option
        if not self.connect():
            return

        # Get enabled currency pairs
        enabled_pairs = {
            pair: config
            for pair, config in self.config['currencies'].items()
            if config.get('enabled', False)
        }

        print(f"\n✅ Enabled pairs: {', '.join(enabled_pairs.keys())}")
        print(f"⏰ Bot will run continuously until stopped (Ctrl+C)")
        print(f"🔄 Checking for signals every 30 seconds...\n")

        try:
            while True:
                # Check risk limits
                if not self.check_risk_limits():
                    print("\n🛑 Risk limits exceeded - Stopping bot")
                    break

                # Check each enabled pair
                for pair, pair_config in enabled_pairs.items():
                    try:
                        # Generate signal
                        signal = self.generate_signal(pair, pair_config)

                        if signal:
                            print(f"\n🔔 Signal detected for {pair}: {signal['signal'].upper()}")

                            # Execute trade
                            trade = self.execute_trade(signal)

                            if trade:
                                print(f"📊 Stats: {self.daily_trades} trades today, ${self.daily_profit:.2f} profit")

                    except Exception as e:
                        print(f"❌ Error processing {pair}: {e}")
                        continue

                # Wait before next check
                time.sleep(30)

        except KeyboardInterrupt:
            print("\n\n⚠️  Bot stopped by user")

        finally:
            # Save final trades
            self.save_trades()

            # Print summary
            print("\n" + "="*60)
            print("📊 Trading Session Summary")
            print("="*60)
            print(f"Total Trades: {self.daily_trades}")
            print(f"Daily Profit: ${self.daily_profit:.2f}")
            print(f"Final Capital: ${self.capital:.2f}")

            if self.daily_trades > 0:
                win_rate = sum(1 for t in self.trades if t['result'] == 'win') / self.daily_trades * 100
                print(f"Win Rate: {win_rate:.2f}%")

            print("="*60)


def main():
    """Main entry point"""
    # Parse command line arguments
    mode = "practice"

    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1].lower()

    if mode not in ["practice", "real"]:
        print("❌ Invalid mode. Use 'practice' or 'real'")
        sys.exit(1)

    if mode == "real":
        confirm = input("⚠️  WARNING: Running in REAL mode. Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    # Create and run bot
    try:
        bot = TradeBotV14(mode=mode)
        bot.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

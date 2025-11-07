#!/usr/bin/env python3
"""
Trade Bot V1.4 - GitHub Actions Edition
Lightweight bot designed to run on GitHub Actions (max 10 min per run)

Features:
- Checks all enabled currency pairs for signals
- Executes trades on IQ Option (Practice account)
- Saves results to trades.csv
- Designed for scheduled runs (every 30 minutes)
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import IQ Option API
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    logger.error("iqoptionapi not installed. Install with: pip install iqoptionapi")
    sys.exit(1)

# Import TA library
try:
    import ta
except ImportError:
    logger.error("ta library not installed. Install with: pip install ta")
    sys.exit(1)


class TradeBotV14:
    """Lightweight Trading Bot for GitHub Actions"""

    def __init__(self):
        """Initialize bot"""
        self.config = self.load_config()
        self.api = None

        # Load credentials from environment
        self.email = os.getenv("IQ_EMAIL")
        self.password = os.getenv("IQ_PASSWORD")
        self.mode = os.getenv("IQ_MODE", "PRACTICE").upper()

        if not self.email or not self.password:
            raise ValueError("IQ_EMAIL and IQ_PASSWORD must be set in environment")

        logger.info(f"✅ Bot initialized in {self.mode} mode")

    def load_config(self):
        """Load config from versions/v1.4/config.json"""
        config_path = "versions/v1.4/config.json"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)

        logger.info(f"✅ Loaded config V{config['version']}")
        return config

    def connect(self):
        """Connect to IQ Option"""
        logger.info(f"🔌 Connecting to IQ Option ({self.mode})...")

        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()

        if not check:
            raise ConnectionError(f"Failed to connect: {reason}")

        logger.info("✅ Connected successfully")

        # Change balance mode
        if self.mode == "PRACTICE":
            self.api.change_balance("PRACTICE")
            logger.info("✅ Switched to PRACTICE account")
        else:
            self.api.change_balance("REAL")
            logger.warning("⚠️  Switched to REAL account")

        balance = self.api.get_balance()
        logger.info(f"💰 Current balance: ${balance:.2f}")

        return True

    def get_candles(self, pair, count=100):
        """Get candles for a currency pair"""
        try:
            candles = self.api.get_candles(pair, 60, count, time.time())

            if not candles:
                return pd.DataFrame()

            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s')
            df = df.rename(columns={'min': 'low', 'max': 'high'})

            return df[['time', 'open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            logger.error(f"Error fetching candles for {pair}: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df, config):
        """Calculate technical indicators"""
        if df.empty or len(df) < 50:
            return df

        ind = config.get('indicators', self.config['default_indicators'])

        # ADX
        adx_indicator = ta.trend.ADXIndicator(
            high=df['high'], low=df['low'], close=df['close'], window=14
        )
        df['adx'] = adx_indicator.adx()

        # MACD
        macd = ta.trend.MACD(
            close=df['close'], window_slow=13, window_fast=5, window_sign=3
        )
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()

        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(
            close=df['close'], window=ind.get('rsi_period', 14)
        ).rsi()

        # EMA
        df['ema20'] = ta.trend.EMAIndicator(
            close=df['close'], window=ind.get('ema_period', 20)
        ).ema_indicator()

        # Slope
        df['slope'] = df['close'].diff(10) / 10

        return df

    def check_trading_hours(self, pair_config):
        """Check if within trading hours"""
        now = datetime.utcnow()
        hour = now.hour

        start = pair_config['trading_hours']['start']
        end = pair_config['trading_hours']['end']

        if start > end:
            return hour >= start or hour < end
        else:
            return start <= hour < end

    def check_session_filter(self, pair_config):
        """Check session filter for allowed direction"""
        hour = datetime.utcnow().hour

        for session, direction in pair_config.get('session_filters', {}).items():
            start, end = map(int, session.split('-'))
            if start <= hour <= end:
                return direction.lower()

        return None

    def generate_signal(self, pair, pair_config):
        """Generate trading signal"""
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

        # Check indicators
        if latest['adx'] < ind['adx_min']:
            return None

        if abs(latest['macd']) < ind['macd_min']:
            return None

        price_ema_dist = abs(latest['close'] - latest['ema20']) / latest['close']
        if price_ema_dist > ind['price_ema_max']:
            return None

        # Determine signal
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
            'time': latest['time']
        }

    def execute_trade(self, signal):
        """Execute binary options trade"""
        pair = signal['pair']
        direction = signal['signal']
        amount = self.config['amount']

        logger.info(f"📊 Executing trade:")
        logger.info(f"   Pair: {pair}")
        logger.info(f"   Direction: {direction.upper()}")
        logger.info(f"   Amount: ${amount}")
        logger.info(f"   Entry Price: {signal['price']:.5f}")

        try:
            # Execute trade
            status, trade_id = self.api.buy(amount, pair, direction, 1)

            if not status:
                logger.error("❌ Trade failed")
                return None

            logger.info(f"✅ Trade opened (ID: {trade_id})")

            # Wait for result (1 min + buffer)
            logger.info("⏳ Waiting for result...")
            time.sleep(65)

            # Get result
            result = self.api.check_win_v4(trade_id)

            if result > 0:
                profit = result
                outcome = "win"
                logger.info(f"✅ Trade WON - Profit: ${profit:.2f}")
            elif result == 0:
                profit = 0
                outcome = "tie"
                logger.info(f"⚖️  Trade TIE")
            else:
                profit = -amount
                outcome = "loss"
                logger.info(f"❌ Trade LOST - Loss: ${amount:.2f}")

            # Create trade record
            trade_record = {
                'trade_id': trade_id,
                'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'pair': pair,
                'direction': direction,
                'result': outcome,
                'profit': profit,
                'capital': self.api.get_balance(),
                'adx': signal['adx'],
                'macd': signal['macd'],
                'rsi': signal['rsi']
            }

            return trade_record

        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return None

    def save_trade(self, trade):
        """Save trade to trades.csv"""
        if not trade:
            return

        # Load existing trades
        if os.path.exists('trades.csv'):
            df = pd.read_csv('trades.csv')
        else:
            df = pd.DataFrame()

        # Append new trade
        new_row = pd.DataFrame([trade])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save
        df.to_csv('trades.csv', index=False)
        logger.info(f"💾 Saved trade to trades.csv")

    def run(self):
        """Main bot execution (continuous monitoring for GitHub Actions)"""
        logger.info("=" * 60)
        logger.info("🤖 Trade Bot V1.4 Starting...")
        logger.info("=" * 60)

        # Connect
        if not self.connect():
            return

        # Get enabled pairs
        enabled_pairs = {
            pair: config
            for pair, config in self.config['currencies'].items()
            if config.get('enabled', False)
        }

        logger.info(f"✅ Enabled pairs: {', '.join(enabled_pairs.keys())}")
        logger.info(f"⏰ Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        logger.info(f"🔄 Continuous monitoring: checking signals every 30 seconds")
        logger.info(f"⏱️  Will run for ~7 minutes (GitHub Actions timeout: 8 min)")

        trades_executed = 0
        start_time = time.time()
        max_runtime = 7 * 60  # 7 minutes (leave 1 min buffer)
        check_interval = 30  # Check every 30 seconds

        # Continuous monitoring loop
        iteration = 0
        while True:
            iteration += 1
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            elapsed = int(time.time() - start_time)

            # Check if we should stop (approaching timeout)
            if elapsed >= max_runtime:
                logger.info(f"\n⏱️  Reached max runtime ({max_runtime/60:.1f} min), stopping gracefully")
                break

            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Iteration #{iteration} - {current_time} UTC (Elapsed: {elapsed}s)")
            logger.info(f"{'='*60}")

            # Check each pair
            for pair, pair_config in enabled_pairs.items():
                try:
                    logger.info(f"\n🔍 Checking {pair}...")

                    # Generate signal
                    signal = self.generate_signal(pair, pair_config)

                    if signal:
                        logger.info(f"🔔 Signal detected: {signal['signal'].upper()}")

                        # Execute trade
                        trade = self.execute_trade(signal)

                        if trade:
                            self.save_trade(trade)
                            trades_executed += 1
                            logger.info(f"✅ Trade #{trades_executed} executed successfully")
                    else:
                        logger.info(f"⏭️  No signal for {pair}")

                except Exception as e:
                    logger.error(f"❌ Error processing {pair}: {e}")
                    continue

            # Wait before next check (unless we're close to timeout)
            remaining = max_runtime - (time.time() - start_time)
            if remaining > check_interval:
                logger.info(f"\n💤 Waiting {check_interval}s before next check... (Remaining: {int(remaining)}s)")
                time.sleep(check_interval)
            else:
                logger.info(f"\n⏱️  Less than {check_interval}s remaining, stopping")
                break

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 Run Summary")
        logger.info("=" * 60)
        logger.info(f"Total iterations: {iteration}")
        logger.info(f"Trades executed: {trades_executed}")
        logger.info(f"Total runtime: {int(time.time() - start_time)}s ({(time.time() - start_time)/60:.1f} min)")
        logger.info(f"Final balance: ${self.api.get_balance():.2f}")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    try:
        bot = TradeBotV14()
        bot.run()
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

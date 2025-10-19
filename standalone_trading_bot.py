#!/usr/bin/env python3
"""
Standalone MT5 Trading Bot
Completely independent - reads from MT5, analyzes, generates signals, and executes trades
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Tuple
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # MT5 Connection
    'mt5_login': 843153,
    'mt5_password': 'YOUR_PASSWORD_HERE',  # CHANGE THIS
    'mt5_server': 'ACYSecurities-Demo',
    
    # Trading Pairs
    'symbols': [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD',  # Forex majors
        'BTCUSD', 'ETHUSD', 'SOLUSD', 'DOGEUSD'  # Crypto
    ],
    
    # Risk Management
    'risk_per_trade': 0.02,  # 2% of balance per trade
    'max_daily_loss': 0.05,  # 5% max daily loss
    'max_open_trades': 5,
    'min_confidence': 80,  # Minimum 80% confidence to execute
    
    # Strategy Settings
    'timeframe': mt5.TIMEFRAME_M5,  # 5-minute candles
    'lookback_periods': 100,  # Number of candles to analyze
    'signal_interval': 120,  # Generate signals every 2 minutes
    
    # Trading Hours (UTC)
    'trading_enabled': True,
    'check_market_hours': True
}

# ============================================================================
# MT5 CONNECTION
# ============================================================================

class MT5Connection:
    """Handle MT5 connection and operations"""
    
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        if not mt5.initialize():
            logger.error(f"MT5 initialize() failed, error code: {mt5.last_error()}")
            return False
        
        if not mt5.login(self.login, password=self.password, server=self.server):
            logger.error(f"MT5 login failed, error code: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        self.connected = True
        account_info = mt5.account_info()
        logger.info(f"Connected to MT5 - Balance: ${account_info.balance:.2f}, Equity: ${account_info.equity:.2f}")
        return True
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.connected:
            return None
        
        info = mt5.account_info()
        if info is None:
            return None
        
        return {
            'balance': info.balance,
            'equity': info.equity,
            'margin': info.margin,
            'free_margin': info.margin_free,
            'profit': info.profit,
            'leverage': info.leverage
        }
    
    def get_market_data(self, symbol: str, timeframe: int, bars: int) -> Optional[pd.DataFrame]:
        """Get historical market data"""
        if not self.connected:
            return None
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            logger.warning(f"No data for {symbol}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current bid/ask prices"""
        if not self.connected:
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'spread': tick.ask - tick.bid,
            'time': datetime.fromtimestamp(tick.time)
        }
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                    sl: float = 0, tp: float = 0, comment: str = "") -> Optional[int]:
        """Place a market order"""
        if not self.connected:
            return None
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return None
        
        # Prepare request
        price = mt5.symbol_info_tick(symbol).ask if order_type == 'buy' else mt5.symbol_info_tick(symbol).bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.comment}")
            return None
        
        logger.info(f"Order placed: {order_type.upper()} {volume} {symbol} @ {price:.5f}")
        return result.order
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        return [
            {
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'buy' if pos.type == mt5.ORDER_TYPE_BUY else 'sell',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'sl': pos.sl,
                'tp': pos.tp
            }
            for pos in positions
        ]

# ============================================================================
# TECHNICAL ANALYSIS
# ============================================================================

class TechnicalAnalyzer:
    """Perform technical analysis on market data"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Moving Averages
        df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean() if len(df) >= 200 else df['close'].rolling(window=len(df)).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        # Volume analysis
        df['volume_sma'] = df['tick_volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['tick_volume'] / df['volume_sma']
        
        return df
    
    @staticmethod
    def detect_trend(df: pd.DataFrame) -> str:
        """Detect market trend"""
        if len(df) < 50:
            return 'neutral'
        
        last_close = df['close'].iloc[-1]
        sma_50 = df['sma_50'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1] if 'sma_200' in df.columns else sma_50
        
        if last_close > sma_50 > sma_200:
            return 'uptrend'
        elif last_close < sma_50 < sma_200:
            return 'downtrend'
        else:
            return 'neutral'
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame) -> float:
        """Calculate market volatility"""
        if len(df) < 20:
            return 0.0
        
        returns = df['close'].pct_change()
        volatility = returns.std() * np.sqrt(len(df))
        return volatility

# ============================================================================
# SIGNAL GENERATOR
# ============================================================================

class SignalGenerator:
    """Generate trading signals based on analysis"""
    
    def __init__(self, min_confidence: int = 80):
        self.min_confidence = min_confidence
    
    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signal for a symbol"""
        if df is None or len(df) < 50:
            return None
        
        # Calculate indicators
        df = TechnicalAnalyzer.calculate_indicators(df)
        
        # Get latest values
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Initialize signal
        signal = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'action': 'hold',
            'confidence': 0,
            'price': last['close'],
            'indicators': {},
            'reason': []
        }
        
        # Collect indicator values
        signal['indicators'] = {
            'rsi': last['rsi'],
            'macd': last['macd'],
            'macd_signal': last['macd_signal'],
            'ema_fast': last['ema_fast'],
            'ema_slow': last['ema_slow'],
            'atr': last['atr']
        }
        
        # Scoring system
        buy_score = 0
        sell_score = 0
        
        # RSI signals
        if last['rsi'] < 30:
            buy_score += 20
            signal['reason'].append('RSI oversold')
        elif last['rsi'] > 70:
            sell_score += 20
            signal['reason'].append('RSI overbought')
        
        # MACD crossover
        if prev['macd'] < prev['macd_signal'] and last['macd'] > last['macd_signal']:
            buy_score += 25
            signal['reason'].append('MACD bullish crossover')
        elif prev['macd'] > prev['macd_signal'] and last['macd'] < last['macd_signal']:
            sell_score += 25
            signal['reason'].append('MACD bearish crossover')
        
        # EMA trend
        if last['ema_fast'] > last['ema_slow']:
            buy_score += 15
            signal['reason'].append('EMA bullish')
        else:
            sell_score += 15
            signal['reason'].append('EMA bearish')
        
        # Bollinger Bands
        if last['close'] < last['bb_lower']:
            buy_score += 20
            signal['reason'].append('Price below lower BB')
        elif last['close'] > last['bb_upper']:
            sell_score += 20
            signal['reason'].append('Price above upper BB')
        
        # Volume confirmation
        if last['volume_ratio'] > 1.5:
            if buy_score > sell_score:
                buy_score += 10
                signal['reason'].append('High volume confirmation')
            elif sell_score > buy_score:
                sell_score += 10
                signal['reason'].append('High volume confirmation')
        
        # Trend detection
        trend = TechnicalAnalyzer.detect_trend(df)
        if trend == 'uptrend':
            buy_score += 10
            signal['reason'].append('Uptrend detected')
        elif trend == 'downtrend':
            sell_score += 10
            signal['reason'].append('Downtrend detected')
        
        # Determine action and confidence
        if buy_score > sell_score and buy_score >= self.min_confidence:
            signal['action'] = 'buy'
            signal['confidence'] = min(buy_score, 100)
        elif sell_score > buy_score and sell_score >= self.min_confidence:
            signal['action'] = 'sell'
            signal['confidence'] = min(sell_score, 100)
        else:
            signal['action'] = 'hold'
            signal['confidence'] = max(buy_score, sell_score)
        
        return signal

# ============================================================================
# RISK MANAGER
# ============================================================================

class RiskManager:
    """Manage trading risk"""
    
    def __init__(self, risk_per_trade: float, max_daily_loss: float, max_open_trades: int):
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_open_trades = max_open_trades
        self.daily_start_balance = 0
        self.daily_pnl = 0
    
    def calculate_position_size(self, balance: float, price: float, atr: float) -> float:
        """Calculate position size based on risk"""
        risk_amount = balance * self.risk_per_trade
        stop_loss_distance = atr * 2  # 2x ATR for stop loss
        
        if stop_loss_distance == 0:
            return 0.01  # Minimum lot size
        
        position_size = risk_amount / stop_loss_distance
        
        # Round to 2 decimal places (standard lot sizing)
        position_size = round(position_size, 2)
        
        # Ensure minimum lot size
        return max(position_size, 0.01)
    
    def can_trade(self, account_info: Dict, open_positions: List) -> Tuple[bool, str]:
        """Check if trading is allowed"""
        # Check max open trades
        if len(open_positions) >= self.max_open_trades:
            return False, f"Max open trades reached ({self.max_open_trades})"
        
        # Check daily loss limit
        if self.daily_start_balance == 0:
            self.daily_start_balance = account_info['balance']
        
        self.daily_pnl = account_info['equity'] - self.daily_start_balance
        max_loss = self.daily_start_balance * self.max_daily_loss
        
        if self.daily_pnl < -max_loss:
            return False, f"Daily loss limit reached ({self.daily_pnl:.2f})"
        
        # Check margin
        if account_info['free_margin'] < account_info['balance'] * 0.2:
            return False, "Insufficient margin"
        
        return True, "OK"

# ============================================================================
# TRADING BOT
# ============================================================================

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.mt5 = MT5Connection(
            config['mt5_login'],
            config['mt5_password'],
            config['mt5_server']
        )
        self.signal_generator = SignalGenerator(config['min_confidence'])
        self.risk_manager = RiskManager(
            config['risk_per_trade'],
            config['max_daily_loss'],
            config['max_open_trades']
        )
        self.running = False
        self.signals_generated = 0
        self.trades_executed = 0
    
    def start(self):
        """Start the trading bot"""
        logger.info("=" * 60)
        logger.info("STANDALONE MT5 TRADING BOT STARTING")
        logger.info("=" * 60)
        
        # Connect to MT5
        if not self.mt5.connect():
            logger.error("Failed to connect to MT5. Exiting.")
            return
        
        logger.info(f"Trading {len(self.config['symbols'])} symbols: {', '.join(self.config['symbols'])}")
        logger.info(f"Risk per trade: {self.config['risk_per_trade']*100}%")
        logger.info(f"Min confidence: {self.config['min_confidence']}%")
        logger.info(f"Signal interval: {self.config['signal_interval']}s")
        logger.info("=" * 60)
        
        self.running = True
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(self.config['signal_interval'])
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            self.stop()
    
    def run_cycle(self):
        """Run one trading cycle"""
        try:
            # Get account info
            account_info = self.mt5.get_account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return
            
            # Get open positions
            open_positions = self.mt5.get_open_positions()
            
            # Check if trading is allowed
            can_trade, reason = self.risk_manager.can_trade(account_info, open_positions)
            
            logger.info(f"Balance: ${account_info['balance']:.2f} | Equity: ${account_info['equity']:.2f} | "
                       f"Profit: ${account_info['profit']:.2f} | Open: {len(open_positions)}")
            
            if not can_trade:
                logger.warning(f"Trading disabled: {reason}")
                return
            
            # Generate signals for each symbol
            for symbol in self.config['symbols']:
                self.process_symbol(symbol, account_info)
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def process_symbol(self, symbol: str, account_info: Dict):
        """Process a single symbol"""
        try:
            # Get market data
            df = self.mt5.get_market_data(
                symbol,
                self.config['timeframe'],
                self.config['lookback_periods']
            )
            
            if df is None:
                return
            
            # Generate signal
            signal = self.signal_generator.generate_signal(symbol, df)
            
            if signal is None or signal['action'] == 'hold':
                return
            
            self.signals_generated += 1
            
            logger.info(f"SIGNAL: {signal['action'].upper()} {symbol} @ {signal['price']:.5f} "
                       f"({signal['confidence']}% confidence)")
            logger.info(f"Reason: {', '.join(signal['reason'])}")
            
            # Execute trade if confidence is high enough
            if signal['confidence'] >= self.config['min_confidence']:
                self.execute_trade(signal, account_info, df)
        
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    def execute_trade(self, signal: Dict, account_info: Dict, df: pd.DataFrame):
        """Execute a trade based on signal"""
        try:
            # Calculate position size
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0.001
            volume = self.risk_manager.calculate_position_size(
                account_info['balance'],
                signal['price'],
                atr
            )
            
            # Calculate SL and TP
            sl_distance = atr * 2
            tp_distance = atr * 3
            
            if signal['action'] == 'buy':
                sl = signal['price'] - sl_distance
                tp = signal['price'] + tp_distance
            else:
                sl = signal['price'] + sl_distance
                tp = signal['price'] - tp_distance
            
            # Place order
            order_id = self.mt5.place_order(
                signal['symbol'],
                signal['action'],
                volume,
                sl=sl,
                tp=tp,
                comment=f"Bot-{signal['confidence']}%"
            )
            
            if order_id:
                self.trades_executed += 1
                logger.info(f"✓ TRADE EXECUTED: {signal['action'].upper()} {volume} {signal['symbol']} "
                           f"SL:{sl:.5f} TP:{tp:.5f}")
            else:
                logger.error(f"✗ TRADE FAILED: {signal['symbol']}")
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        self.mt5.disconnect()
        logger.info("=" * 60)
        logger.info(f"Bot stopped. Signals: {self.signals_generated}, Trades: {self.trades_executed}")
        logger.info("=" * 60)

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    # Check if MT5 password is set
    if CONFIG['mt5_password'] == 'YOUR_PASSWORD_HERE':
        print("ERROR: Please set your MT5 password in the CONFIG section!")
        print("Edit this file and change 'YOUR_PASSWORD_HERE' to your actual password")
        return
    
    # Create and start bot
    bot = TradingBot(CONFIG)
    bot.start()

if __name__ == "__main__":
    main()


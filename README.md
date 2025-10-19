# Standalone MT5 Trading Bot - Setup Guide

## Overview

This is a **completely independent** Python trading bot that:
- ✅ Reads data directly from MT5
- ✅ Analyzes market conditions using AI algorithms
- ✅ Generates high-confidence trading signals
- ✅ Executes trades automatically on MT5
- ✅ No web interface, no cloud, no dependencies

## Requirements

1. **Windows PC** with MetaTrader 5 installed
2. **Python 3.8+** installed
3. **MT5 account** (your ACY Securities demo/live account)

## Installation Steps

### Step 1: Install Python Dependencies

Open Command Prompt and run:

```cmd
pip install MetaTrader5 pandas numpy
```

Or use the requirements file:

```cmd
pip install -r standalone_requirements.txt
```

### Step 2: Configure the Bot

1. Open `standalone_trading_bot.py` in a text editor (Notepad, VS Code, etc.)

2. Find the `CONFIG` section at the top (around line 35)

3. **IMPORTANT**: Change your MT5 password:
   ```python
   'mt5_password': 'YOUR_PASSWORD_HERE',  # CHANGE THIS TO YOUR REAL PASSWORD
   ```

4. Verify other settings:
   ```python
   'mt5_login': 843153,  # Your MT5 login
   'mt5_server': 'ACYSecurities-Demo',  # Your server
   ```

5. Adjust risk settings if needed:
   ```python
   'risk_per_trade': 0.02,  # 2% risk per trade
   'max_daily_loss': 0.05,  # 5% max daily loss
   'min_confidence': 80,  # Only trade signals with 80%+ confidence
   ```

### Step 3: Start MetaTrader 5

1. Open your MT5 terminal
2. Login to your account (843153 on ACYSecurities-Demo)
3. Keep MT5 running in the background

### Step 4: Run the Bot

Open Command Prompt in the bot folder and run:

```cmd
python standalone_trading_bot.py
```

## What the Bot Does

### 1. **Connects to MT5**
- Reads your account balance, equity, and open positions
- Gets real-time price data for all trading pairs

### 2. **Analyzes Markets Every 2 Minutes**
- Calculates technical indicators (RSI, MACD, EMA, Bollinger Bands, ATR)
- Detects trends and volatility
- Scores each symbol for buy/sell opportunities

### 3. **Generates Signals**
- Only generates signals with 80%+ confidence
- Provides detailed reasoning for each signal
- Logs all activity to `trading_bot.log`

### 4. **Executes Trades Automatically**
- Calculates optimal position size based on risk (2% per trade)
- Sets stop-loss (2x ATR) and take-profit (3x ATR) automatically
- Places orders directly on MT5
- Maximum 5 open trades at once

### 5. **Risk Management**
- Stops trading if daily loss exceeds 5%
- Monitors margin and prevents over-leveraging
- Adjusts position sizes based on account balance

## Trading Pairs

The bot trades these symbols by default:

**Forex Majors:**
- EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD

**Crypto:**
- BTCUSD, ETHUSD, SOLUSD, DOGEUSD

You can add/remove symbols in the CONFIG section.

## Configuration Options

### Risk Settings

```python
'risk_per_trade': 0.02,  # Risk 2% of balance per trade
'max_daily_loss': 0.05,  # Stop if lose 5% in one day
'max_open_trades': 5,  # Maximum 5 positions at once
'min_confidence': 80,  # Only trade 80%+ confidence signals
```

### Strategy Settings

```python
'timeframe': mt5.TIMEFRAME_M5,  # Use 5-minute candles
'lookback_periods': 100,  # Analyze last 100 candles
'signal_interval': 120,  # Check for signals every 2 minutes
```

### Available Timeframes

- `mt5.TIMEFRAME_M1` - 1 minute
- `mt5.TIMEFRAME_M5` - 5 minutes (default)
- `mt5.TIMEFRAME_M15` - 15 minutes
- `mt5.TIMEFRAME_M30` - 30 minutes
- `mt5.TIMEFRAME_H1` - 1 hour
- `mt5.TIMEFRAME_H4` - 4 hours

## Monitoring the Bot

### Console Output

The bot prints real-time information:

```
2025-10-19 12:00:00 - INFO - Balance: $100000.00 | Equity: $100250.00 | Profit: $250.00 | Open: 2
2025-10-19 12:00:05 - INFO - SIGNAL: BUY BTCUSD @ 106500.00 (85% confidence)
2025-10-19 12:00:05 - INFO - Reason: RSI oversold, MACD bullish crossover, High volume confirmation
2025-10-19 12:00:06 - INFO - ✓ TRADE EXECUTED: BUY 0.05 BTCUSD SL:106000.00 TP:107500.00
```

### Log File

All activity is saved to `trading_bot.log` for review.

## Stopping the Bot

Press `Ctrl+C` in the Command Prompt window to stop the bot gracefully.

## Safety Features

1. **Daily Loss Limit**: Automatically stops if you lose 5% in one day
2. **Position Sizing**: Never risks more than 2% per trade
3. **Max Open Trades**: Limits exposure to 5 positions
4. **Confidence Threshold**: Only executes high-probability trades (80%+)
5. **Stop Loss**: Every trade has automatic stop-loss protection
6. **Margin Check**: Won't trade if margin is too low

## Troubleshooting

### "MT5 initialize() failed"
- Make sure MT5 is running
- Check that you're logged in to MT5

### "MT5 login failed"
- Verify your password in the CONFIG section
- Check login number and server name
- Make sure your account is active

### "No data for SYMBOL"
- Symbol might not be available on your broker
- Check symbol name in MT5 (might be BTCUSD.a or similar)
- Remove unavailable symbols from CONFIG

### "Order failed"
- Check if trading is allowed for that symbol
- Verify you have sufficient margin
- Check if market is open (forex closes on weekends)

## Advanced Customization

### Change Trading Strategy

Edit the `SignalGenerator.generate_signal()` method to adjust:
- Indicator weights (buy_score/sell_score values)
- Entry conditions
- Signal logic

### Add New Indicators

Add calculations in `TechnicalAnalyzer.calculate_indicators()`:

```python
# Example: Add Stochastic Oscillator
df['stoch_k'] = ...
df['stoch_d'] = ...
```

### Modify Risk Rules

Edit `RiskManager` class to change:
- Position sizing algorithm
- Stop-loss calculation
- Risk limits

## Performance Tracking

The bot logs:
- Total signals generated
- Total trades executed
- Win/loss ratio (check MT5 history)
- Daily P&L

## Recommended Settings

### Conservative (Low Risk)
```python
'risk_per_trade': 0.01,  # 1% per trade
'max_daily_loss': 0.03,  # 3% daily limit
'min_confidence': 85,  # Very high confidence only
```

### Moderate (Balanced)
```python
'risk_per_trade': 0.02,  # 2% per trade
'max_daily_loss': 0.05,  # 5% daily limit
'min_confidence': 80,  # High confidence
```

### Aggressive (High Risk)
```python
'risk_per_trade': 0.03,  # 3% per trade
'max_daily_loss': 0.08,  # 8% daily limit
'min_confidence': 75,  # Medium-high confidence
```

## Support

For issues or questions:
1. Check `trading_bot.log` for error details
2. Verify MT5 connection and account status
3. Review configuration settings
4. Test on demo account first!

## Disclaimer

**IMPORTANT**: This bot trades real money. Always:
- Test on a demo account first
- Start with small position sizes
- Monitor the bot regularly
- Understand the risks of automated trading
- Never risk more than you can afford to lose

Trading involves substantial risk. Past performance does not guarantee future results.


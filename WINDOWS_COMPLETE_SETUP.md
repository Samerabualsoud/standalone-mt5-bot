# Complete Windows Setup Guide - Trading Bot + Dashboard

This guide will help you set up both the improved trading bot (v2) and the real-time dashboard on your Windows PC.

## 📋 Prerequisites

- Windows PC with MT5 installed
- Python 3.7+ installed
- Node.js 18+ installed
- Git installed (optional, for cloning repositories)

## 🚀 Part 1: Setup Improved Trading Bot (v2)

### Step 1: Download the Bot

**Option A: Using Git**
```bash
cd C:\Users\aaa\
git clone https://github.com/Samerabualsoud/standalone-mt5-bot.git
cd standalone-mt5-bot
```

**Option B: Download ZIP**
1. Go to https://github.com/Samerabualsoud/standalone-mt5-bot
2. Click "Code" → "Download ZIP"
3. Extract to `C:\Users\aaa\standalone-mt5-bot`

### Step 2: Install Python Dependencies

```bash
cd C:\Users\aaa\standalone-mt5-bot
pip install -r requirements.txt
```

### Step 3: Configure the Bot

Edit `standalone_trading_bot_v2.py` and update line 34:

```python
'mt5_password': 'YOUR_ACTUAL_MT5_PASSWORD',  # Replace with your password
```

**Optional Configuration** (lines 31-58):
```python
CONFIG = {
    'mt5_login': 843153,
    'mt5_password': 'YOUR_PASSWORD',
    'mt5_server': 'ACYSecurities-Demo',
    
    'min_confidence': 60,      # Lower = more signals (try 50-70)
    'verbose_mode': True,      # Shows all analysis
    'signal_interval': 120,    # Check every 2 minutes
    'risk_per_trade': 0.02,    # 2% risk per trade
    'max_open_trades': 5,      # Max simultaneous positions
}
```

### Step 4: Test the Bot

```bash
python standalone_trading_bot_v2.py
```

You should see:
```
================================================================================
STANDALONE MT5 TRADING BOT v2 - IMPROVED SIGNAL GENERATION
================================================================================
Connected to MT5 - Balance: $100,000.00, Equity: $100,000.00
Trading 9 symbols: EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD, BTCUSD, ETHUSD, SOLUSD, DOGEUSD
Risk per trade: 2.0%
Min confidence: 60% (REDUCED for more signals)
Signal interval: 120s
Verbose mode: True
================================================================================

CYCLE #1 - 2025-10-19 12:34:56
================================================================================
Balance: $100,000.00 | Equity: $100,000.00 | Profit: $0.00 | Open: 0
  EURUSD: BUY=55 SELL=35 -> HOLD (55%)
    Close to signal! Reasons: EMA bullish, Price above BB middle, MACD above signal
  GBPUSD: BUY=45 SELL=40 -> HOLD (45%)
  BTCUSD: BUY=65 SELL=20 -> BUY (65%)
    
🔔 SIGNAL GENERATED 🔔
  Symbol: BTCUSD
  Action: BUY
  Price: 67234.50000
  Confidence: 65%
  Buy Score: 65
  Sell Score: 20
  Reasons: RSI low (38.5), MACD above signal, EMA bullish, Price above BB middle, Uptrend detected
```

**Key Improvements in v2:**
- ✅ Signals are now being generated (confidence threshold reduced from 80% to 60%)
- ✅ Verbose mode shows analysis for ALL symbols every cycle
- ✅ Shows buy/sell scores even when action is "hold"
- ✅ Indicates when you're "close to a signal"
- ✅ Saves signal data to JSON files for dashboard

## 🎨 Part 2: Setup Dashboard

### Step 1: Download Dashboard

**Option A: Using Git**
```bash
cd C:\Users\aaa\
git clone https://github.com/Samerabualsoud/trading-dashboard.git
cd trading-dashboard
```

**Option B: Download from Manus**
1. Download the dashboard project file
2. Extract to `C:\Users\aaa\trading-dashboard`

### Step 2: Install Dependencies

```bash
cd C:\Users\aaa\trading-dashboard
npm install -g pnpm
pnpm install
```

### Step 3: Start Dashboard

```bash
pnpm dev
```

The dashboard will open at: http://localhost:3001

## 🔗 Part 3: Connect Bot to Dashboard

### Method 1: Manual Copy (Simple)

**Every time you want to update the dashboard:**

```bash
xcopy /E /I /Y C:\Users\aaa\standalone-mt5-bot\signals C:\Users\aaa\trading-dashboard\client\public\signals
```

Then refresh the dashboard in your browser.

### Method 2: Auto-Sync Script (Recommended)

Create `C:\Users\aaa\sync_dashboard.bat`:

```batch
@echo off
echo Starting dashboard sync...
:loop
xcopy /E /I /Y "C:\Users\aaa\standalone-mt5-bot\signals" "C:\Users\aaa\trading-dashboard\client\public\signals" >nul 2>&1
timeout /t 5 /nobreak >nul
goto loop
```

**To use:**
1. Start the trading bot in one terminal
2. Start the sync script in another terminal: `sync_dashboard.bat`
3. Start the dashboard in a third terminal: `pnpm dev`

### Method 3: All-in-One Startup (Advanced)

Create `C:\Users\aaa\start_trading_system.bat`:

```batch
@echo off
title Trading System Launcher
color 0A

echo ================================================================================
echo           MT5 TRADING BOT + DASHBOARD LAUNCHER
echo ================================================================================
echo.
echo Starting all services...
echo.

REM Start trading bot
echo [1/3] Starting Trading Bot...
start "MT5 Trading Bot" cmd /k "cd C:\Users\aaa\standalone-mt5-bot && python standalone_trading_bot_v2.py"
timeout /t 5 /nobreak >nul

REM Start sync script
echo [2/3] Starting Signal Sync...
start "Signal Sync" cmd /k "cd C:\Users\aaa && sync_dashboard.bat"
timeout /t 2 /nobreak >nul

REM Start dashboard
echo [3/3] Starting Dashboard...
start "Trading Dashboard" cmd /k "cd C:\Users\aaa\trading-dashboard && pnpm dev"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo                    ALL SERVICES STARTED!
echo ================================================================================
echo.
echo   Trading Bot:  Running in separate window
echo   Signal Sync:  Running in separate window  
echo   Dashboard:    http://localhost:3001
echo.
echo   Press Ctrl+C in each window to stop services
echo.
echo ================================================================================
pause
```

**To use:**
1. Double-click `start_trading_system.bat`
2. Wait for all services to start
3. Open http://localhost:3001 in your browser

## 📊 Dashboard Features

### What You'll See:

1. **Account Overview Cards**
   - Balance: $100,000.00
   - Equity: Current account value
   - Profit/Loss: Total P/L
   - Open Positions: Number of active trades

2. **Bot Statistics**
   - Signals Generated: Total count
   - Trades Executed: Successful executions
   - Success Rate: Execution percentage

3. **Recent Signals**
   - All 9 symbols analyzed every cycle
   - BUY/SELL/HOLD actions with confidence %
   - Buy and Sell scores
   - Reasons for each signal (technical indicators)

4. **Open Positions**
   - Active trades with current P/L
   - Entry price, current price
   - Stop Loss and Take Profit levels

### Auto-Refresh
- Dashboard updates every 10 seconds automatically
- Toggle auto-refresh on/off with button
- Manual refresh available anytime

## 🔧 Troubleshooting

### Bot Not Generating Signals

**Check:**
1. MT5 is running and logged in
2. Bot shows "Connected to MT5" message
3. Verbose mode is enabled (shows analysis for all symbols)
4. Check `trading_bot.log` for errors

**Solutions:**
- Lower `min_confidence` to 50 for more signals
- Verify MT5 password is correct
- Ensure MT5 symbols are available (EURUSD, BTCUSD, etc.)

### Dashboard Shows "Connection Error"

**Check:**
1. Bot is running and generating signals
2. `signals` folder exists in `standalone-mt5-bot/`
3. `signals` folder is copied to `trading-dashboard/client/public/`
4. `latest.json` file exists and is valid JSON

**Solutions:**
```bash
# Check if signals folder exists
dir C:\Users\aaa\standalone-mt5-bot\signals

# Manually copy signals
xcopy /E /I /Y C:\Users\aaa\standalone-mt5-bot\signals C:\Users\aaa\trading-dashboard\client\public\signals

# Restart dashboard
cd C:\Users\aaa\trading-dashboard
pnpm dev
```

### Dashboard Shows Old Data

**Cause:** Sync script not running or signals not updating

**Solutions:**
1. Make sure sync script is running
2. Check bot is still running (not crashed)
3. Manually copy signals folder again
4. Check bot's `signal_interval` setting (default: 120s)

### "Module not found" Errors

**Python:**
```bash
pip install --upgrade MetaTrader5 pandas numpy
```

**Node.js:**
```bash
cd C:\Users\aaa\trading-dashboard
pnpm install
```

### Port Already in Use

If port 3001 is busy:
```bash
# Dashboard will automatically try next port (3002, 3003, etc.)
# Check terminal output for actual port
```

## 📁 File Structure

```
C:\Users\aaa\
├── standalone-mt5-bot\
│   ├── standalone_trading_bot_v2.py    ← Improved bot
│   ├── requirements.txt                ← Python dependencies
│   ├── trading_bot.log                 ← Detailed logs
│   ├── signals\                        ← Generated by bot
│   │   ├── latest.json                 ← Current data
│   │   └── signals_*.json              ← Historical data
│   └── IMPROVEMENTS_V2.md              ← What's new in v2
│
├── trading-dashboard\
│   ├── client\
│   │   ├── public\
│   │   │   └── signals\                ← Copy bot signals here
│   │   │       └── latest.json
│   │   └── src\
│   │       └── pages\
│   │           └── Home.tsx            ← Dashboard UI
│   └── DASHBOARD_SETUP.md              ← Setup instructions
│
├── sync_dashboard.bat                  ← Auto-sync script
└── start_trading_system.bat            ← All-in-one launcher
```

## 🎯 Quick Start Checklist

- [ ] Python 3.7+ installed
- [ ] Node.js 18+ installed
- [ ] MT5 installed and logged in
- [ ] Bot downloaded and dependencies installed
- [ ] Bot configured with MT5 password
- [ ] Bot tested and generating signals
- [ ] Dashboard downloaded and dependencies installed
- [ ] Sync script created
- [ ] All-in-one launcher created (optional)
- [ ] Dashboard accessible at http://localhost:3001

## 💡 Tips for Best Results

1. **Start with Demo Account**
   - Test thoroughly before using real money
   - Monitor for at least 24 hours
   - Review all signals and trades

2. **Adjust Confidence Threshold**
   - Start at 60% and monitor results
   - Increase to 65-70% if too many signals
   - Decrease to 50-55% if too few signals

3. **Monitor the Logs**
   - Check `trading_bot.log` regularly
   - Look for patterns in signal generation
   - Verify trades are executing correctly

4. **Use Verbose Mode**
   - Keep `verbose_mode: True` initially
   - Helps understand bot's analysis
   - Shows why signals are/aren't generated

5. **Keep Dashboard Open**
   - Monitor in real-time
   - Watch for unusual patterns
   - Verify bot is working correctly

## 🚀 Next Steps

1. **Run the system for a few hours** and observe:
   - Are signals being generated regularly?
   - Are trades executing when confidence ≥ 60%?
   - Is the dashboard updating correctly?

2. **Adjust settings based on results**:
   - Too many signals? Increase `min_confidence`
   - Too few signals? Decrease `min_confidence`
   - Want faster checks? Reduce `signal_interval`

3. **Review performance**:
   - Check win rate in dashboard
   - Review executed trades in MT5
   - Analyze signal reasons for patterns

4. **Optimize for your strategy**:
   - Adjust risk per trade
   - Modify indicator weights in code
   - Add/remove trading symbols

## 📞 Support

If you encounter issues:

1. **Check the logs**: `trading_bot.log`
2. **Verify MT5 connection**: Look for "Connected to MT5" message
3. **Test signal generation**: Should see signals within first few cycles
4. **Check dashboard sync**: Verify signals folder is being copied
5. **Review configuration**: Ensure all settings are correct

## 🎉 Success Indicators

You'll know everything is working when:

✅ Bot shows "Connected to MT5" with correct balance
✅ Verbose output shows analysis for all 9 symbols every cycle
✅ Signals are generated with confidence scores
✅ Dashboard shows real-time account data
✅ Dashboard displays recent signals and open positions
✅ Auto-refresh updates dashboard every 10 seconds
✅ Trades execute automatically when confidence ≥ 60%

## 🔄 Comparison: Old vs New

| Feature | Old Bot | New Bot v2 |
|---------|---------|-----------|
| Min Confidence | 80% (too strict) | 60% (realistic) |
| Signal Generation | Very rare | Regular |
| Visibility | Only signals | All analysis |
| Scoring | Binary | Granular |
| Dashboard | None | Real-time web UI |
| Indicators | 6 | 7 (added Stochastic) |
| Logging | Basic | Verbose + JSON |

---

**You're all set!** Start the system and watch your trading bot work automatically with full visibility through the dashboard.


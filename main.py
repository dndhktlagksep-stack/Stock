import yfinance as yf
import asyncio
from telegram import Bot
import schedule
import time
from datetime import datetime
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8609107770:AAGVq5lkttrxvfYNQvXkZ-Zk8prfNaCprlk")
CHAT_ID        = os.environ.get("CHAT_ID", "7100435479")

STOCKS = {
    "애플":           "AAPL",
    "마이크로소프트":  "MSFT",
    "엔비디아":       "NVDA",
    "알파벳(구글)":   "GOOGL",
    "아마존":         "AMZN",
    "메타":           "META",
    "테슬라":         "TSLA",
    "로빈후드":       "HOOD",
    "팔란티어":       "PLTR",
}

ALERT_THRESHOLD = 5.0


def get_stock_data():
    results = []
    for name, ticker in STOCKS.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            price = info.last_price
            prev_close = info.previous_close
            change_pct = (price - prev_close) / prev_close * 100
            results.append({"name": name, "ticker": ticker, "price": price, "change_pct": change_pct})
        except Exception:
            results.append({"name": name, "ticker": ticker, "price": None, "change_pct": None})
    return results


def format_line(s):
    if s["price"] is None:
        return f"⚠️ {s['name']} ({s['ticker']}) 조회 실패"
    arrow = "🔺" if s["change_pct"] >= 0 else "🔻"
    return f"{arrow} {s['name']} ({s['ticker']})\n   현재가: ${s['price']:.2f}  ({s['change_pct']:+.2f}%)"


async def send_message(text):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")


def evening_report():
    stocks = get_stock_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = "\n".join(format_line(s) for s in stocks)
    message = (
        f"📊 *저녁 주가 요약*\n"
        f"🕐 {now} (한국시간)\n"
        f"{'─' * 26}\n{lines}\n{'─' * 26}\n"
        f"_M7 + 로빈후드 + 팔란티어_"
    )
    asyncio.run(send_message(message))
    print(f"[{now}] 저녁 요약 전송 완료")


def check_big_move():
    stocks = get_stock_data()
    alerts = [s for s in stocks if s["change_pct"] is not None and abs(s["change_pct"]) >= ALERT_THRESHOLD]
    if not alerts:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = "\n".join(format_line(s) for s in alerts)
    message = (
        f"🚨 *급등락 알림 ({ALERT_THRESHOLD}% 이상)*\n"
        f"🕐 {now} (한국시간)\n"
        f"{'─' * 26}\n{lines}\n{'─' * 26}\n"
        f"_전일 종가 대비 변동_"
    )
    asyncio.run(send_message(message))
    print(f"[{now}] 급등락 알림: {[s['ticker'] for s in alerts]}")


schedule.every().day.at("23:30").do(evening_report)
schedule.every(30).minutes.do(check_big_move)

print("✅ 봇 시작!")
asyncio.run(send_message(
    "✅ *주가 알림 봇 시작!*\n"
    "📅 매일 23:30 저녁 요약\n"
    "🚨 5% 이상 급등락 즉시 알림"
))

while True:
    schedule.run_pending()
    time.sleep(30)
yfinance
python-telegram-bot
schedule

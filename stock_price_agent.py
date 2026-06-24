import yfinance as yf
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

STOCKS = {
    'ZAMZ.TO': {
        'name': 'Amazon (CAD Hedged)',
        'upper_threshold': 30.00,
        'lower_threshold': 28.00
    },
    'ZMET.TO': {
        'name': 'Meta (CAD Hedged)',
        'upper_threshold': 34.00,
        'lower_threshold': 30.00
    },
    'ZNVD.TO': {
        'name': 'Nvidia (CAD Hedged)',
        'upper_threshold': 52.00,
        'lower_threshold': 49.00
    }
}

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'sameera5694@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'm.ssameera94@gmail.com')

last_notification_time = {}

def send_email_alert(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"✉️  Email alert sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if data.empty:
            logger.warning(f"No data fetched for {symbol}")
            return None
        current_price = data['Close'].iloc[-1]
        return round(current_price, 2)
    except Exception as e:
        logger.error(f"❌ Error fetching {symbol} stock price: {e}")
        return None

def check_thresholds(symbol, price, stock_info):
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    stock_name = stock_info['name']
    upper_threshold = stock_info['upper_threshold']
    lower_threshold = stock_info['lower_threshold']
    
    if price > upper_threshold:
        alert_key = f'{symbol}_upper'
        if alert_key not in last_notification_time or \
           (current_time - last_notification_time[alert_key]).total_seconds() > 3600:
            subject = f"🚀 {stock_name} Alert - Above ${upper_threshold:.2f}"
            body = f"{stock_name} stock price has gone ABOVE your threshold!\n\nTicker: {symbol}\nCurrent Price: ${price:.2f} CAD\nUpper Threshold: ${upper_threshold:.2f} CAD\nTimestamp: {timestamp}\n\nThis is an automated alert from your Stock Price Agent."
            send_email_alert(subject, body)
            last_notification_time[alert_key] = current_time
            logger.info(f"🚀 {stock_name} price above threshold: ${price:.2f}")
    elif price < lower_threshold:
        alert_key = f'{symbol}_lower'
        if alert_key not in last_notification_time or \
           (current_time - last_notification_time[alert_key]).total_seconds() > 3600:
            subject = f"📉 {stock_name} Alert - Below ${lower_threshold:.2f}"
            body = f"{stock_name} stock price has gone BELOW your threshold!\n\nTicker: {symbol}\nCurrent Price: ${price:.2f} CAD\nLower Threshold: ${lower_threshold:.2f} CAD\nTimestamp: {timestamp}\n\nThis is an automated alert from your Stock Price Agent."
            send_email_alert(subject, body)
            last_notification_time[alert_key] = current_time
            logger.info(f"📉 {stock_name} price below threshold: ${price:.2f}")
    else:
        logger.info(f"✅ {stock_name} (${price:.2f}) is within normal range")

def check_all_stocks():
    logger.info("=" * 60)
    logger.info(f"🔄 Checking all stocks at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    for symbol, stock_info in STOCKS.items():
        price = get_stock_price(symbol)
        if price is not None:
            logger.info(f"💹 {stock_info['name']} ({symbol}): ${price:.2f} CAD")
            check_thresholds(symbol, price, stock_info)
        else:
            logger.error(f"Failed to get {symbol} price")
    logger.info("=" * 60)

if __name__ == "__main__":
    check_all_stocks()

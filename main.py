import requests
import logging
import time
from models import Currency , CurrencyInfo
from app import app 
from database import db
from datetime import datetime


logging.basicConfig(filename='logs.log',level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")

URL_JSON = 'https://call1.tgju.org/ajax.json'



name_map = {
    "sekee": {"name": "sekee", "symbol": "🪙"},
    "tgju_gold_irg18": {"name": "gold-18", "symbol": "🥇"},
    "price_dollar_rl": {"name": "dollar", "symbol": "$"},
    "price_eur": {"name": "euro", "symbol": "€"}
}



def get_currency(name, symbol):
    existing = Currency.query.filter_by(name=name).first()
    if not existing:
        currency = Currency(name=name, symbol=symbol)
        db.session.add(currency)
        db.session.commit()
        logging.info(f"Added currency: {name} ({symbol})")
    else:
        logging.info(f"Currency already exists: {name}")



def get_currency_info(currency_id , price , time , change ,source = 'www.tgju.org') :
    try:
        time = datetime.fromisoformat(time)
    except Exception:
        time = datetime.utcnow() 
    latest_info = CurrencyInfo.query.filter_by(currency_id=currency_id)\
                     .order_by(CurrencyInfo.update_time.desc()).first()
    if latest_info and latest_info.update_time == time:
        logging.info(f"Skipping duplicate currency_info for currency_id {currency_id} at {time}")
        return
    currency_info = CurrencyInfo(currency_id = currency_id ,price = price , update_time = time , change_rate = change , source = 'www.tgju.com' )
    db.session.add(currency_info)
    db.session.commit()
    logging.info(f"Added currency_info: {price} ({time})")


def main(URL_JSON):
    with app.app_context(): 
        try:
            response = requests.get(URL_JSON)
            response.raise_for_status()
            logging.info(f"Connected {response.status_code}")

            data = response.json()
            current = data.get('current', {})

            keys = ['sekee', 'tgju_gold_irg18', 'price_dollar_rl', 'price_eur']

            for key in keys:
                if key in current:
                    item = current[key]
                    price = item['p']
                    price = int(price.replace(',', ''))
                    time = item['ts']
                    change = item['dp']

                    info = name_map.get(key, {"name": key, "symbol": ""})
                    name = info["name"]
                    symbol = info["symbol"]

                    print(f"{name}: {price} ({symbol}) — {time}")

                    get_currency(name, symbol)
                    currency = Currency.query.filter_by(name=name).first()
                    get_currency_info(currency.id, int(price), time, change, 'www.tgju.org')

        except requests.exceptions.RequestException as e:
            logging.error(f"Error app to API: {e}")

if __name__ == '__main__': 
    with app.app_context():
        while True:
            main(URL_JSON)
            logging.info("Sleeping for 30 minutes...")
            time.sleep(1) 
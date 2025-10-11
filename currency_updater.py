import threading
import requests
import logging
import time
from datetime import datetime , timedelta
from models import Currency, CurrencyInfo
from database import db

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

URL_JSON = 'https://call1.tgju.org/ajax.json'

name_map = {
    "sekee": {"name": "sekee", "symbol": "🪙"},
    "tgju_gold_irg18": {"name": "gold-18", "symbol": "🥇"},
    "price_dollar_rl": {"name": "dollar", "symbol": "$"},
    "price_eur": {"name": "euro", "symbol": "€"},
    "crypto-bitcoin-irr": {"name": "bitcoin", "symbol": "₿"},
}


def update_currencies():
   
    from app import app

    with app.app_context():
        while True:
            try:
                response = requests.get(URL_JSON)
                response.raise_for_status()
                logging.info(f"Connected {response.status_code}")

                data = response.json()
                current = data.get('current', {})


                keys = ['sekee', 'tgju_gold_irg18', 'price_dollar_rl', 'price_eur', "crypto-bitcoin-irr"]
                # saving all the keys in list 

                current_keys = current.keys()

                for key in keys:
                    if key in current:
                        item = current[key]
                        price = int(item['p'].replace(',', ''))
                        h_price = int(item['h'].replace(',', ''))
                        l_price = int(item['l'].replace(',', ''))
                        d_price = int(item['d'].replace(',', ''))
                        time_str = item['ts']
                        change = item['dp']


                        info = name_map.get(key, {"name": key, "symbol": ""})
                        name, symbol = info["name"], info["symbol"]

                        existing = Currency.query.filter_by(name=name).first()
                        if not existing:
                            currency = Currency(name=name, symbol=symbol,image_url = f"static/{name}.jpg")
                            db.session.add(currency)
                            db.session.commit()

                        currency = Currency.query.filter_by(name=name).first()
                        
                        minute_key = datetime.now().replace(second=0, microsecond=0)
                        exists = CurrencyInfo.query.filter_by(currency_id=currency.id).filter(
                            CurrencyInfo.current_time.between(minute_key, minute_key + timedelta(seconds=59))
                        ).first()

                        if exists:
                            continue  # Skip duplicate

                        # Insert new currency info
                        info_entry = CurrencyInfo(
                            currency_id=currency.id,
                            price=price,
                            h_price=h_price,
                            l_price=l_price,
                            d_price=d_price,
                            update_time=time_str,
                            current_time=datetime.now(),
                            change_rate=change,
                            source='www.tgju.org'
                        )
                        db.session.add(info_entry)
                        db.session.commit()

                        print(f"{name}: {price}{symbol}")

                logging.info("Sleeping for 1 minute...")
                time.sleep(60)

            except Exception as e:
                logging.error(f"Error in currency updater: {e}")
                time.sleep(60)



def start_background_thread():
    thread = threading.Thread(target=update_currencies, daemon=True)
    thread.start()
    logging.info("Background thread started for currency updates.")

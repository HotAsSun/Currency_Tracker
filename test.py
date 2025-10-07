from app import app
from database import db
from models import Currency, CurrencyInfo

with app.app_context():
    currencies = Currency.query.all()
    
    if not currencies:
        print("No currencies found in the database.")
    else:
        for c in currencies:
            print(f"Currency: {c.id} — {c.name} ({c.symbol}) — Last update: {c.last_update}")
            

            info_list = CurrencyInfo.query.filter_by(currency_id=c.id).all()
            
            if not info_list:
                print("  No currency info available.")
            else:
                for info in info_list:
                    print(f"  Price: {info.price} — Change rate: {info.change_rate} — Updated: {info.update_time} — Source: {info.source}")

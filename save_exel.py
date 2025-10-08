import pandas as pd
from app import app, db
from models import Currency, CurrencyInfo, Users
from datetime import datetime

def export_to_excel():
    with app.app_context():
        
        data = []
        currencies = Currency.query.all()

        for currency in currencies:
            infos = currency.infos.order_by(CurrencyInfo.current_time.desc()).all()
            for info in infos:
                data.append({
                    "Currency Name": currency.name,
                    "Symbol": currency.symbol,
                    "Price": info.price,
                    "High Price": info.h_price,
                    "Low Price": info.l_price,
                    "Daily Price": info.d_price,
                    "Change Rate": info.change_rate,
                    "Update Time": info.update_time.strftime("%Y-%m-%d %H:%M:%S") if info.update_time else None,
                    "Current Time": info.current_time.strftime("%Y-%m-%d %H:%M:%S") if info.current_time else None
                })

        
        df = pd.DataFrame(data)

       
        users_data = []
        users = Users.query.all()
        for user in users:
            users_data.append({
                "Username": user.username,
                "Email": user.email,
                "Password (Hashed)": user.password
            })

        df_users = pd.DataFrame(users_data)

       
        filename = f"currency_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, sheet_name="Currency Data", index=False)
            df_users.to_excel(writer, sheet_name="Users", index=False)

        print(f"✅ Data exported successfully to {filename}")

if __name__ == "__main__":
    export_to_excel()

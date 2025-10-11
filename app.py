import logging
from flask import Flask, render_template, redirect, flash, url_for, request ,jsonify
from database import db
from models import Currency, CurrencyInfo, Users
from flask_login import LoginManager, login_user, current_user, logout_user, login_required ,LoginManager
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from currency_updater import start_background_thread 

# -------------------- Setup --------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = '1234'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqldb://root:sina885@localhost/currency'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

bcrypt = Bcrypt()
db.init_app(app)

# Logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logging.info("Application started")





login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# -------------------- Routes --------------------
@app.route('/')
@app.route('/home')
def home():
    currencies = Currency.query.all()
    currency_data = []
    for currency in currencies:
        latest_info = currency.infos.order_by(CurrencyInfo.update_time.desc()).first()
        if latest_info:
            arrow = ""
            color = "black"

            if latest_info.change_rate is not None:
                if 1 > latest_info.change_rate > 0:
                    arrow = "↓"
                    color = "red"
                elif latest_info.change_rate > 1:
                    arrow = "↑"
                    color = "green"

            currency_data.append({
                "name": currency.name,
                "symbol": currency.symbol,
                "price": latest_info.price,
                "change_rate": latest_info.change_rate,
                "update_time": latest_info.update_time,
                "arrow": arrow,
                "color": color
            })
    return render_template('home.html', currency_data=currency_data)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        flash("You are already registered.", 'danger')
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=True if form.email.data == "admin@gmail.com" else False
        )

        db.session.add(user)
        db.session.commit()
        logging.info(f"New user registered: {user.username}")
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('registration.html', form=form, title='Registration')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", 'info')
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            logging.info(f"User logged in: {user.username}")

            if user.is_admin:
                return redirect(url_for('admin'))

            return redirect(url_for('home'))

        flash('Login unsuccessful. Check email and password.', 'danger')

    return render_template('login.html', form=form, title="Login")


    return render_template('login.html', form=form, title="Login")

@app.route("/logout")
@login_required
def logout():
    logging.info(f"User logged out: {current_user.username}")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.route('/currency/<string:name>')
def currency_page(name):
    currency = Currency.query.filter_by(name=name).first_or_404()
    return render_template('currency.html', currency=currency)


@app.route('/api/currency/<string:name>')
def currency_data(name):
    currency = Currency.query.filter_by(name=name).first_or_404()
    infos = currency.infos.order_by(CurrencyInfo.current_time.desc()).limit(100).all()
    infos.reverse()  

    return jsonify({
        "labels": [info.current_time.strftime("%Y-%m-%d %H:%M:%S") for info in infos],
        "prices": [info.price for info in infos],
        "h_prices": [info.h_price for info in infos],
        "l_prices": [info.l_price for info in infos],
        "d_prices": [info.d_price for info in infos],
    })

@app.route('/api/currency/<string:name>/ohlc')
def currency_ohlc(name):

    currency = Currency.query.filter_by(name=name).first_or_404()
    infos = currency.infos.order_by(CurrencyInfo.current_time.asc()).all()

    ohlc_dict = {}
    for info in infos:
        hour = info.current_time.replace(minute=0, second=0, microsecond=0)
        if hour not in ohlc_dict:
            ohlc_dict[hour] = {
                "open": info.price,
                "high": info.h_price,
                "low": info.l_price,
                "close": info.price
            }
        else:
            ohlc_dict[hour]["high"] = max(ohlc_dict[hour]["high"], info.h_price)
            ohlc_dict[hour]["low"] = min(ohlc_dict[hour]["low"], info.l_price)
            ohlc_dict[hour]["close"] = info.price

    ohlc_list = [
      {"x": k.strftime("%Y-%m-%d %H:%M:%S"),
         "o": v["open"],
         "h": v["high"],
         "l": v["low"],
         "c": v["close"]}
        for k, v in sorted(ohlc_dict.items())
    ]
    return jsonify(ohlc_list)




@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash("You don't have permission to access this page!", "danger")
        return redirect(url_for('home'))

    
    currencies_with_latest = []
    for c in Currency.query.all():
        latest_info = c.infos.order_by(CurrencyInfo.update_time.desc()).first()
        currencies_with_latest.append((c, latest_info))

    
    users = Users.query.all() 

    user_data = []
    for user in users:
        user_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        })

    return render_template(
        'admin.html',
        currencies=currencies_with_latest,
        users=user_data
    )




@app.route('/admin/delete_currency/<int:currency_id>', methods=['POST'])
@login_required
def delete_currency(currency_id):
    if not current_user.is_admin:
        flash("You don't have permission to perform this action!", "danger")
        return redirect(url_for('home'))

    currency = Currency.query.get_or_404(currency_id)
    db.session.delete(currency)
    db.session.commit()
    flash(f"Currency '{currency.name}' has been deleted.", "success")
    return redirect(url_for('admin'))



@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission!", "danger")
        return redirect(url_for('home'))

    user = Users.query.get_or_404(user_id)

    if user.is_admin:
        flash("You cannot delete an admin.", "warning")
        return redirect(url_for('admin'))

    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' has been deleted.", "success")
    return redirect(url_for('admin'))



# -------------------- Run --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ All tables created successfully.")
    start_background_thread()
    app.run(debug=True, use_reloader=False) 


import logging
from flask import Flask, render_template, redirect, flash, url_for, request
from database import db
from models import Currency, CurrencyInfo, Users
from flask_login import LoginManager, login_user, current_user, logout_user, login_required ,LoginManager
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt

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
        user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
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
            
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')

    return render_template('login.html', form=form, title="Login")

@app.route("/logout")
@login_required
def logout():
    logging.info(f"User logged out: {current_user.username}")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# -------------------- Run --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ All tables created successfully.")
    app.run(debug=True)

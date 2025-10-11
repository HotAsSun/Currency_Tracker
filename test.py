from models import Users
from app import app 

with app.app_context():
    users = Users.query.all()

    for user in users:
        print(user.username)
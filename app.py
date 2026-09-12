from flask import Flask
import os
from werkzeug.security import generate_password_hash
# ایمپورت کردن دیتابیس و روت‌ها
from backend.database import db
from backend.models import User
from backend.routes import main

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# تنظیمات اصلی فایل‌ها
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # محدودیت آپلود 16 مگ
app.config["SECRET_KEY"] = "my_secret_key_123"

# تنظیمات دیتابیس (اگر داکر نبود از لوکال استفاده کنه)
db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://mailuser:mailpass@localhost:5432/maildb")
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

print("--- در حال اتصال به دیتابیس ---")

with app.app_context():
    db.create_all()
    # چک کنیم ببینیم کاربر داریم یا نه، اگر نداشتیم بسازیم
    if User.query.count() == 0:
        print("--- ساختن کاربران پیش‌فرض ---")
        admin = User(username="admin", password=generate_password_hash("1234"))
        amir = User(username="amir", password=generate_password_hash("1234"))
        db.session.add(admin)
        db.session.add(amir)
        db.session.commit()

app.register_blueprint(main)

if __name__ == "__main__":
    print("--- سرور روی پورت 5000 بالا اومد ---")
    app.run(host="0.0.0.0", port=5000, debug=True)

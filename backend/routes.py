import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from backend.database import db
from backend.models import User, Letter

# این بلوپوینت برای مسیریابی برنامه است
main = Blueprint("main", __name__)

@main.route("/")
def home():
    return redirect(url_for("main.login"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # پیدا کردن کاربر در دیتابیس
        user = User.query.filter_by(username=username).first()

        # چک کردن رمز عبور
        if user and check_password_hash(user.password, password):
            session["username"] = user.username
            return redirect(url_for("main.inbox"))

        flash("نام کاربری یا رمز عبور اشتباه است.", "danger")
        return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/inbox")
def inbox():
    # اگر لاگین نکرده، بره صفحه لاگین
    if "username" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["username"]).first()
    
    # گرفتن نامه‌ها بر اساس آیدی گیرنده
    letters = Letter.query.filter_by(receiver_id=user.id).order_by(Letter.created_at.desc()).all()

    return render_template("inbox.html", letters=letters, user=user)

@main.route("/compose", methods=["GET", "POST"])
def compose():
    if "username" not in session:
        return redirect(url_for("main.login"))

    # لیست کاربران برای انتخاب در صفحه ارسال
    users = User.query.filter(User.username != session["username"]).all()

    if request.method == "POST":
        receiver_id = request.form.get("receiver")
        subject = request.form.get("subject")
        body = request.form.get("content")
        
        # مدیریت فایل پیوست
        attachment = request.files.get("attachment")
        filename = None
        
        if attachment and attachment.filename != "":
            filename = secure_filename(attachment.filename)
            # ذخیره فایل در پوشه آپلود
            attachment.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

        sender = User.query.filter_by(username=session["username"]).first()

        # ذخیره نامه در دیتابیس
        new_letter = Letter(sender_id=sender.id, receiver_id=int(receiver_id), subject=subject, body=body, attachment=filename)
        db.session.add(new_letter)
        db.session.commit()

        flash("نامه با موفقیت ارسال شد.", "success")
        return redirect(url_for("main.inbox"))

    return render_template("compose.html", users=users)

@main.route("/letter/<int:letter_id>")
def view_letter(letter_id):
    if "username" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["username"]).first()
    letter = Letter.query.filter_by(id=letter_id, receiver_id=user.id).first()

    if not letter:
        flash("نامه پیدا نشد.", "danger")
        return redirect(url_for("main.inbox"))

    return render_template("view_letter.html", letter=letter)

@main.route("/download/<filename>")
def download_file(filename):
    if "username" not in session:
        return redirect(url_for("main.login"))
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))

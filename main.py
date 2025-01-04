import sqlite3, os
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from flask_session import Session
from cachelib import FileSystemCache
from datetime import timedelta
from steganocryptopy.steganography import Steganography

con = sqlite3.connect("USER_INFO.db", check_same_thread=False)
cursor = con.cursor()
app = Flask(__name__)
app.secret_key = '1111'
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)

@app.route("/")
def login():
    return render_template('login.html')

@app.route("/encryption_site/")
def encryption():
    return render_template('encryption_site.html')

@app.route("/encryption_process/", methods=['POST','GET'])
def encryption_proc():
    if request.method == "POST":
        image = request.form['image']
        text = request.form['description']
        with open('key.key','w', encoding='utf-8') as file:
            file.write(session['secretkey'])
        with open('text.txt', 'w', encoding='utf-8') as file:
            file.write(text)
        secret = Steganography.encrypt('key.key',image,'text.txt')
        secret.save('img/secret_img.jpg')
        os.remove('key.key')
        os.remove('text.txt')
        return send_from_directory('img/secret_img.jpg','зашифрованное изображение')

@app.route("/check_login/", methods=['POST','GET'])
def check_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        cursor.execute("SELECT * FROM users_info")
    for i in cursor:
        if login == i[1] and password == i[2]:
            session['login'] = True
            session['username'] = login
            session['id'] = i[0]
            session['secretkey'] = i[3]
            session.permanent = False
            app.permanent_session_lifetime = timedelta(minutes=100)
            session.modified = True
            flash('Вы авторозованны', 'success')
            return redirect(url_for('encryption'))

    flash('Неверный логин или пароль', 'danger')
    return redirect(url_for('login'))

@app.route("/register/")
def register():
    return render_template('register.html')

@app.route("/save_register/", methods=['POST','GET'])
def save_register():
    cursor.execute("SELECT * FROM users_info")
    check_data = cursor.fetchall()

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        Steganography.generate_key('')
        with open('key.key', 'r', encoding='utf-8') as file:
            secretkey=file.read()

        os.remove('key.key')
        for user in check_data:
            if user[1] == login:
                flash("такой параметр login уже существует","danger")
                return redirect(url_for('register'))
            if user[2] == password:
                flash("такой параметр password уже существует","danger")
                return redirect(url_for('register'))

        cursor.execute("INSERT INTO users_info (login, pasword, secretkey) VALUES (?,?,?)",
                       (login,password,secretkey))
        con.commit()
        return redirect(url_for('encryption'))

app.run(debug=True)
"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import uuid, os
import hashlib
import pymysql
import datetime
from flask import Flask, render_template, request, abort, redirect, url_for, session, flash, jsonify
app = Flask(__name__)

def create_connection():
    return pymysql.connect(
        host='10.0.0.17', #'localhost'
        user='wilcao',
        password='ARIOT',
        db='wilcao_database',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        )


# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

with create_connection() as connection:
    with connection.cursor() as cursor: 
        cursor.execute("SELECT * FROM people")
        result = cursor.fetchall()

for row in result:
    print("first_name", row ['first_name'], "as last_name", row ['last_name'])


@app.route('/delete')
def delete():
       with create_connection() as connection:
           with connection.cursor() as cursor:
               sql = "DELETE FROM users WHERE id = %s"
               values = (request.args['id'])
               cursor.execute(sql, values)
               connection.commit()
       return redirect ('/dashboard')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if session['role'] != 'admin' and  str(session['ID']) != request.args['id']:
        flash("you can't see it nor edit it")
        return redirect('/view?id=' + request.args['id'])
    if request.method == 'POST':
       avatar_image=request.files['avatar']
       ext = os.path.splitext(avatar_image.filename)[1]
       avatar_filename= str(uuid.uuid4())[:8] + ext
       avatar_image.save("static/images/" + avatar_filename)
       if request.form['old_avatar'] != 'None':
           os.remove("static/images/" + request.form['old_avatar'])
       elif request.form['old_avatar'] != 'None':
           avatar_filename = request.form['old_avatar']
       else:
           avatar_filename = None

       with create_connection() as connection:
           with connection.cursor() as cursor:
               sql = """UPDATE users SET
               first_name = %s,
               last_name = %s,
               email = %s,
               avatar = %s,
               WHERE id = %s
               """
               values = (
                   request.form['first_name'],
                   request.form['last_name'],
                   request.form['email'],
                   avatar_filename,
                   request.form['id']
                 )
               cursor.execute(sql, values)
               connection.commit()
       return redirect('/dashboard')
    else:
        with create_connection() as connection:
           with connection.cursor() as cursor:
               sql = "SELECT * FROM users WHERE id = %s"
               values = (request.args['id'])
               cursor.execute(sql, values)
               result = cursor.fetchone()
        return render_template('edit.html', result=result)


@app.before_request
def restrict():
    restricted_pages = ['dashboard', 'view_user', 'delete', 'edit']
    if 'logged_in' not in session and request.endpoint in restricted_pages: 
        return redirect('/login')

@app.route('/')
def hello():
    with create_connection() as connection:
        with connection.cursor() as cursor: 
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    return render_template('home.html', data=result)

@app.route('/movieedit')
def movieedit():
    if session['role'] != 'admin' and  str(session['ID']) != request.args['id']:
        flash("you can't see it nor edit it")
        return redirect('/view?id=' + request.args['id'])
    if request.method == 'POST':
       #avatar_image=request.files['avatar']
       #ext = os.path.splitext(avatar_image.filename)[1]
       #avatar_filename= str(uuid.uuid4())[:8] + ext
       a#vatar_image.save("static/images/" + avatar_filename)
       #if request.form['old_avatar'] != 'None':
           #os.remove("static/images/" + request.form['old_avatar'])
      # elif request.form['old_avatar'] != 'None':
           #avatar_filename = request.form['old_avatar']
       #else:
           #avatar_filename = None

       with create_connection() as connection:
           with connection.cursor() as cursor:
               sql = """UPDATE movies SET
               title = %s,
               genre = %s,
               year_released = %s,
               summary = %s,
               WHERE idmovies = %s
               """
               values = (
                   request.form['title'],
                   request.form['genre'],
                   request.form['year_released'],
                   equest.form['summary'],
                   request.form['idmovies']
                 )
               cursor.execute(sql, values)
               connection.commit()
       return redirect('/dashboard')
    else:
        with create_connection() as connection:
           with connection.cursor() as cursor:
               sql = "SELECT * FROM users WHERE id = %s"
               values = (request.args['id'])
               cursor.execute(sql, values)
               result = cursor.fetchone()
        return render_template('edit.html', result=result)

@app.route('/register', methods=['GET', 'POST'])
def add_user():
    if request.method== 'POST':

        password =  request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        if request.files['avatar'].filename:
            avatar_image = request.files['avatar']
            ext = os.path.splitext(avatar_image.filename)[1]
            avatar_filename= str(uuid.uuid4())[:8] + ext
            avatar_image.save("static/images/" + avatar_filename)
        else:
            avatar_filename = None
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql ="""INSERT INTO users ( first_name, last_name, email, password, avatar) VALUES (%s, %s, %s, %s, %s)"""
                values = (
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    encrypted_password,
                    avatar_filename
                    )
                try:
                    cursor.execute(sql, values)
                    connection.commit()
                except pymysql.err.IntegrityError:
                    flash('Email has been taken')
                    return redirect(url_for('add_user'))
        return redirect('/')
    return render_template('users_add.html')

@app.route('/dashboard')
def dashboard():
    if session['role'] != 'admin':
        return abort(404)
    with create_connection() as connection:
        with connection.cursor() as cursor: 
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    return render_template('users_list.html', result=result)

@app.route('/view')
def view_user():
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id=%s", request.args['id'])
                result = cursor.fetchone()
        return render_template('user_view.html', result=result)

@app.route('/checkemail')
def check_email():
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email=%s"
                values = (
                    request.args['email']
                )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result:
            return jsonify({ 'status': 'Error' })
        else:
            return jsonify({ 'status': 'OK' })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        password =  request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email=%s AND password=%s"
                values = (
                    request.form['email'],
                    encrypted_password,
            )
                cursor.execute(sql, values)
                result = cursor.fetchone()
        if result:
            session['logged_in'] = True
            session['first_name']= result['first_name']
            session['role'] = result['role']
            session['ID'] = result['ID']
            return redirect ('/')
        else:
            flash("cry about it")
            return redirect("/login")
    else:
         return render_template('login.html')

@app.route('/movieadd', methods=['GET', 'POST'])
def movieadd():
    if request.method== 'POST':
        #if request.files['avatar'].filename:
            #avatar_image = request.files['avatar']
            #ext = os.path.splitext(avatar_image.filename)[1]
            #avatar_filename= str(uuid.uuid4())[:8] + ext
            #avatar_image.save("static/images/" + avatar_filename)
        #else:
            #avatar_filename = None
        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql ="""INSERT INTO movies ( title, genre, year_released, summary) VALUES (%s, %s, %s, %s)"""
                values = (
                    request.form['title'],
                    request.form['genre'],
                    request.form['year_released'],
                    request.form['summary'],
                    )
                    #return redirect(url_for('add_user'))
                cursor.execute(sql, values)
                connection.commit()
        return redirect('/')
    return render_template('movie_add.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/name')
def name_entry():
    return render_template("name_thing.html")

@app.route('/greeting')
def greeting():
    return render_template("greeting.html", name=request.args.get("name", "william"))

@app.route('/signup')
def signup():
    First_name = request.args.get("First_name")
    return render_template("signup.html", First_name=First_name)

@app.errorhandler(404)
def not_found(error):
    return render_template("notfound.html"), 404

@app.route('/admin', methods=['GET','post'])
def admin():
    if "Password" in request.form:
        if request.form["Password"] == "asdf":
            return "what?"
        else:
            return redirect ('/admin')
    return render_template("adminlogin.html")



if __name__ == '__main__':
    import os
    app.secret_key = os.urandom(32)
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)

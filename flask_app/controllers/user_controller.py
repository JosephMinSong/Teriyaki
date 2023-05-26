from flask_app import app
from flask import render_template, redirect, session, request, flash, url_for, abort
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'user_id' in session:
        user_data = {'id' : session['user_id']}
        logged_user = User.get_user_by_id(user_data)
    else: 
        logged_user = False

    return render_template('index.html',
                            logged_user=logged_user)

@app.route('/directions')
def directions():
    if 'user_id' in session:
        user_data = {'id' : session['user_id']}
        logged_user = User.get_user_by_id(user_data)
    else: 
        logged_user = False

    return render_template('directions.html',
                            logged_user=logged_user)

@app.route('/order')
def order():
    if 'user_id' in session:
        user_data = {'id' : session['user_id']}
        logged_user = User.get_user_by_id(user_data)
        all_favs = User.get_favorites(user_data)
        print(all_favs)
    else: 
        logged_user = False
        all_favs = False
    
    return render_template('order_page.html',
                            logged_user = logged_user,
                            all_favs=all_favs)

@app.route('/signin_reg')
def signin_reg():
    return render_template('signin_reg.html')

@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')

@app.route('/thankyou')
def thankyou():
    if 'user_id' in session:
        user_data = {'id' : session['user_id']}
        logged_user = User.get_user_by_id(user_data)
    else: 
        logged_user = False
    return render_template('thankyou.html',
                            logged_user=logged_user)

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')


@app.route('/users/register', methods=['POST'])
def register():
    if not User.validate_user_reg(request.form):
        return redirect('/signin_reg')
    hashed_pass = bcrypt.generate_password_hash(request.form['password'])

    user_data = {
        **request.form,
        'password' : hashed_pass
    }

    session['user_id'] = User.create_user(user_data)
    return redirect('/')

@app.route('/users/login', methods=['POST'])
def login():
    if not User.validate_user_login(request.form):
        return redirect('/signin_reg')
    
    session['user_id'] = User.get_user_by_email(request.form).id
    return redirect('/')
from flask import flash
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
import re
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import os
from dotenv import load_dotenv
load_dotenv()

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

import stripe

app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')

app.config['STRIPE_ENDPOINT_SECRET'] = os.getenv('STRIPE_SECRET_ENDPOINT')

stripe.api_key = app.config['STRIPE_SECRET_KEY']

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    

    @classmethod
    def create_user(cls, data):
        query = """INSERT INTO users (first_name, last_name, email, password)
                    VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"""

        return connectToMySQL(DATABASE).query_db(query, data)
    

    @classmethod
    def get_user_by_id(cls, data):
        query = """SELECT * FROM users
                    WHERE id = %(id)s"""
        result = connectToMySQL(DATABASE).query_db(query, data)

        if result:
            return cls(result[0])
        return False

    @classmethod
    def get_user_by_email(cls, data):
        query = """SELECT * FROM users
                    WHERE email = %(email)s"""
        result = connectToMySQL(DATABASE).query_db(query, data)
        if result:
            return cls(result[0])
        return False
    
    @classmethod
    def add_favorite(cls, data):
        query = """INSERT INTO orders (user_id, product_id)
                    VALUES (%(user_id)s, %(product_id)s)"""
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_favorites(cls, data):
        query = """SELECT * FROM orders
                    JOIN users ON orders.user_id = %(id)s"""
        result = connectToMySQL(DATABASE).query_db(query,data)

        if result:
            all_items = []
            for item in result:
                one_item = stripe.Product.retrieve(item['product_id'])
                all_items.append(one_item)
            return all_items
        return False

    
    @classmethod
    def validate_user_login(cls, data):
        query = """SELECT * FROM users
                    WHERE email = %(email)s"""
        result = connectToMySQL(DATABASE).query_db(query, data)

        if result:
            user = cls(result[0])
        else:
            flash("Invalid credentials", 'login')
            return False
        
        if not User.get_user_by_email(data):
            flash("Invalid credentials", 'login')
            return False
        
        elif not bcrypt.check_password_hash(user.password, data['password']):
            flash("Invalid credentials", 'login')
            return False
        
        return user
    
    @staticmethod
    def validate_user_reg(data):
        is_valid = True
        # Check first name
        if len(data['first_name']) < 1 :
            flash("Please enter a first name", 'first_name')
            is_valid = False
        elif len(data['first_name']) < 2:
            flash("First name must be at least 2 characters long", 'first_name')
            is_valid = False

        # Check last name
        if len(data['last_name']) < 1 :
            flash("Please enter a last name", 'last_name')
            is_valid = False
        elif len(data['last_name']) < 2:
            flash("Last name must be at least 2 characters long", 'last_name')
            is_valid = False

        # Check email
        if len(data['email']) < 1 :
            flash("Please enter an email address", 'email')
            is_valid = False
        elif not email_regex.match(data['email']):
            flash("Please enter a valid email address", 'email')
            is_valid = False
        else:
            email_data = {'email' : data['email']}
            if User.get_user_by_email(email_data):
                flash("A user already exists with this email", 'email')
                is_valid = False
        
        # Check password
        if len(data['password']) < 1 :
            flash("Please enter a password", 'password')
            is_valid = False
        elif len(data['password']) < 8 :
            flash("Password must be at least 8 characters long", 'password')
            is_valid = False
        
        # Check if passwords match
        if not data['confirm_password']:
            flash("Confirm your password", 'confirm_password')
            is_valid = False
        elif data['password'] != data['confirm_password']:
            flash("Passwords must match", 'confirm_password')
            is_valid = False
        
        return is_valid
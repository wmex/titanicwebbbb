import requests
from sqlalchemy import update
import math
from flask import Flask
from flask import render_template, request, url_for
import flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__, template_folder='template', static_folder='static')
db = SQLAlchemy()
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'mysecret'
admin = Admin(app)
db.init_app(app)

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
import requests
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search.db'
titanic = pd.read_excel("titanic.xlsx", engine='openpyxl')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'mysecret'
admin = Admin(app)
db.init_app(app)



class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    comment = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    Survived = db.Column(db.Integer)
    Pclass = db.Column(db.Integer)
    Name = db.Column(db.String)
    Sex = db.Column(db.String)
    Age = db.Column(db.Float)
    SibSp = db.Column(db.Integer)
    Parch = db.Column(db.Integer)
    Ticket = db.Column(db.String)
    Fare = db.Column(db.Float)
    Cabin = db.Column(db.String)
    Embarked = db.Column(db.String)
with app.app_context():
    db.create_all()

admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Comments, db.session))
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('registration.html')


@app.route('/registration_add', methods=['GET', 'POST'])
def registration_add():
    email = (request.form['email'])
    password = (request.form['password'])
    for i in Users.query.all():
        if email == i.email:
            return render_template("username_error.html")
    user = Users(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return render_template("login.html")


@app.route('/checking', methods=['GET', 'POST'])
def checking():
    email = (request.form['email'])
    password = (request.form['password'])
    for i in Users.query.all():
        if email == i.email and password == i.password:
            return flask.redirect('/index')
    return render_template("verification_error")



@app.route('/index')
def index():
    round = math.ceil(titanic['Age'].mean())
    all = titanic.shape[0]
    males = titanic.loc[titanic['Sex'] == 'male'].shape[0]
    females = titanic.loc[titanic['Sex'] == 'female'].shape[0]
    number_of_dies = titanic.loc[titanic['Survived'] == 0].shape[0]
    percent_of_death = math.ceil((number_of_dies / all) * 100)

    url = f"https://numbersapi.p.rapidapi.com/{round}/math"
    querystring = {"fragment": "true", "json": "true"}

    headers = {
        "X-RapidAPI-Key": "28e4fb1d62msh63e114aa663c461p1a068bjsn2caaa8d43c7d",
        "X-RapidAPI-Host": "numbersapi.p.rapidapi.com"
    }

    r = requests.request("GET", url, headers=headers, params=querystring)

    api = r.json()['text']

    return render_template('index.html', grad = round, all = all, males=males, females = females, dies = percent_of_death, api = api)
@app.route('/result', methods=['GET', 'POST'])
def result():
    country = request.form['name']
    searchpd = titanic.loc[titanic['Name'].str.contains(f'{country}', case=False)]
    if searchpd.shape[0] == 0:
        return render_template('oops.html')
    Search.query.delete()
    for i in range(searchpd.shape[0]):
            larl = searchpd['Survived'].astype(str).iloc[i]
            if larl == '1':
                larl = 'Alive'
            elif larl == '0':
                larl = 'Dead'
            check = searchpd['Sex'].astype(str).iloc[i]
            male = request.form.get('male')
            female = request.form.get('female')
            if male == female:
                search = Search(Name=searchpd['Name'].astype(str).iloc[i],
                                Survived=larl,
                                Sex=check)
                db.session.add(search)
                db.session.commit()
            elif female:
                if check == 'female':
                    search = Search(Name=searchpd['Name'].astype(str).iloc[i],
                                    Survived=larl,
                                    Sex=check)
                    db.session.add(search)
                    db.session.commit()
            elif male:
                if check == 'male':
                    search = Search(Name=searchpd['Name'].astype(str).iloc[i],
                                    Survived=larl,
                                    Sex=check)
                    db.session.add(search)
                    db.session.commit()




    return render_template('search.html', result=Search.query.with_entities(Search.Name), survived=Search.query.with_entities(Search.Survived))

    #titanic['result'] = titanic['Name'].str.find(country)
    #list = []
    #slist = []
    #for i in range(titanic.shape[0]):
       # slist.append(titanic.loc[i, 'result'].astype(int))
       # if slist[i] > 0:
       #     list.append(titanic.loc[i, 'Name'])
           # list.append(titanic.loc[i, 'Survived'])
   # return render_template('search.html', result =list)

@app.route('/discus', methods=['GET', 'POST'])
def discus():
    a = Comments.query.with_entities(Comments.author, Comments.comment, Comments.pub_date).order_by(Comments.author.desc())


    return render_template('dis.html', a=a)




@app.route('/discus_com', methods=['GET', 'POST'])
def discus_com():
    author = request.form['author']
    comment = request.form['text']
    today = datetime.today()
    for i in Users.query.all():
        if author == i.email:
            com = Comments(
            author=author,
            comment=comment,
            pub_date= today
        )
            db.session.add(com)
            db.session.commit()
            return flask.redirect('/discus')

    return render_template('oops.html')


if __name__ == '__main__':
    app.run(debug=True)

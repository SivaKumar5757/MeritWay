from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy import or_
import coursedata
from chatbot import get_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 't\(,$}K*4;pXmxdL:3wyS^hd<g0$a`Os'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)
# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Define the RegistrationForm
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# Define the LoginForm
class LoginForm(FlaskForm):
    email_or_username = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

# Routes
@app.route("/")
def startup():
    return redirect(url_for('guest'))

@app.route("/home")
def guest():
    session['logged_in'] = False
    return render_template("guest.html", categories=coursedata.categories, courses=coursedata.courses)
@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    query = data.get('query', '')
    suggestions = [s for s in coursedata.categories if query.lower() in s.lower()]
    return jsonify(suggestions)
@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    # print(query.lower())
    # print(query.title())
    if query.lower() in coursedata.cate :
        results=query.title()
        return jsonify(coursedata.courses[results])
    results = [course for course in coursedata.coursessearch if query.lower() in course['title'].lower()]
    return jsonify(results)
@app.route("/user")
def user():
    return render_template("home.html", categories=coursedata.categories, courses=coursedata.courses)

@app.route('/user/chat/<path:bot>')
def index(bot):
    initial_message = "I'm here to explain any learning related queries and make your life shine."
    if session.get('logged_in'):
        username = session.get('username', 'there')
        initial_message = f"Hello {username}, {initial_message}"
    return render_template('index.html', initial_message=initial_message)

@app.route('/user/chat/<path:bot>', methods=['POST'])
def chat(bot):
    user_message = request.json.get('message')
    if user_message:
        response = get_response(user_message)
        return jsonify({'response': response})
    else:
        return jsonify({'response': 'Please provide a valid message.'}), 400

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            return redirect(url_for('register'))
        else:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('user'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.email == form.email_or_username.data, User.username == form.email_or_username.data)).first()
        if user and user.password == form.password.data:
            session['logged_in'] = True
            session['username'] = user.username
            return redirect(url_for('user'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route("/user/playing/<path:subpath>")
def playing(subpath):
    # Do something with the subpath variable
    return render_template("playing.html", subpath=subpath, course=coursedata.course_data[subpath])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)

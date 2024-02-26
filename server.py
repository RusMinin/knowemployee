from flask import Flask, request, jsonify, make_response, render_template, redirect, session,  url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.message import EmailMessage
import uuid
from deepgram import Deepgram
import asyncio
from functools import wraps
import aiohttp
import io
import sys
import json
from flask_migrate import Migrate, init, migrate, upgrade
import os
import re
import base64
import time
import hashlib
import scrypt
from cryptography.fernet import Fernet
from functions import create_image_with_qrcode
import base64
from PIL import Image
import io

DOMAIN = "http://127.0.0.1:5000"
NAME_PLATFORM = "KnowEmployee"
app = Flask(__name__)
app.config['SECRET_KEY'] = '97473497e94c7289a98fae8e9636ae67'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///service.db'
DEEPGRAM_API_KEY = '176aa82078b4c8dd570dc560dfbee88e9bba7410'
KEY = b'LIuLpwBjtQgsOlEKmY43Zd5xO_HqwW332ZM478rkHRM='
MIMETYPE = 'audio/wav'
QUESTIONS = [
    "How would you rate the overall culture and climate of the company on a scale from 1 to 10? Please specify the reasons for your rating.",
    "Are you satisfied with the work-life balance at the company? If not, what would you like to change?",
    "Do you feel that your professional skills and capabilities are valued and utilized within the company?",
    "How do you assess the opportunities for career growth in the company? Are there specific barriers or challenges you encounter?",
    "Do you feel comfortable expressing your opinions or suggesting ideas in the workplace? Why or why not?",
    "Are you satisfied with the level of corporate benefits and packages offered by the company?",
    "Are there specific departments or management levels with which you face issues? If so, please describe them.",
    "In your opinion, what is the main advantage of working for this company, and what would you prioritize to improve first?",
    "Do you feel you have sufficient resources and tools for effective work? If not, where specifically do you feel the lack?",
    "How do you evaluate the interaction with colleagues and teamwork in the company? Are there any points that hinder effective team collaboration?",
    
    # Свободный фитбэк
    "Now you can add from yourself what you like or dislike about the company or your suggestions",
]

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cipher = Fernet(KEY)

def encrypt(message: str) -> str:
    """Encrypts the message"""
    return cipher.encrypt(message.encode()).decode('utf-8')

def decrypt(token: str) -> str:
    """Decrypts the message"""
    return cipher.decrypt(token.encode('utf-8')).decode()

def run_migrations():
    with app.app_context():
        if not os.path.exists('migrations'):
            init()
            migrate()
            upgrade()

        upgrade()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, unique=True)
    company_name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    country = db.Column(db.Text)
    timezone = db.Column(db.Text)
    code_number = db.Column(db.Text)
    avatar = db.Column(db.Text,  default=False)
    plan = db.Column(db.Text,  default=False)
    slogan = db.Column(db.Text,  default=False)
    anonimus_feedback = db.Column(db.Text, default=False)

class Testing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name_token = db.Column(db.Text)
    token = db.Column(db.Text)
    text_user = db.Column(db.Text)
    result = db.Column(db.Text)
    valid = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

class TestingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, default=False)
    anonimus_feedback = db.Column(db.Text, default=False)
    user_answer = db.Column(db.Text, default=False)
    result = db.Column(db.Text, default=False)
    checked = db.Column(db.Boolean, default=False)
    type = db.Column(db.Text, default="anonymous")
    only = db.Column(db.Text, default=False)
    multiple = db.Column(db.Boolean, default=False)
    name = db.Column(db.Text, default="")
    count = db.Column(db.Integer, default=False)
    username_bool = db.Column(db.Boolean, default=False)
    username = db.Column(db.Text, default=False)
    questions = db.Column(db.Text, default=False)
    members_multiple = db.Column(db.Text, default="[]")
    ai = db.Column(db.Boolean, default=False)
    ai_status = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())


# QUIZ
class QuizToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, default=False)
    token_quiz = db.Column(db.Text, default=False)
    title = db.Column(db.Text, default=False)
    image = db.Column(db.Text, default=False)
    theme_color = db.Column(db.Text, default=False)
    questions = db.Column(db.Text, default="[]")
    request = db.Column(db.Text, default=False)
    company_badge = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

class QuizResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, default=False)
    quiz_token = db.Column(db.Text, default=False)
    token_results = db.Column(db.Text, default=False)
    username = db.Column(db.Text, default=False)
    type = db.Column(db.Text, default=False)
    answer = db.Column(db.Text, default="[]")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())
# ================


class GPTPricer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, default=False)
    price_count = db.Column(db.Text, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

def qrCodeAnonimusFeedback(hash, company_name):
    url = f"{DOMAIN}/anonymous/{hash}"
    background_path = "./static/elements/qr_placeholder.png"
    base64_img = create_image_with_qrcode(url, company_name, background_path)

    return base64_img

def send_email(recipient, token, type="register"):
    try:
        msg = EmailMessage()
        msg.set_content(f'Click the link to confirm: http://localhost:5000/confirm/{token}')
        msg['Subject'] = NAME_PLATFORM + ' | Confirm your email'
        msg['From'] = 'liokap@gmail.com'
        msg['To'] = recipient

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login('liokap@gmail.com', 'LEONardp!@34')
            '''server.send_message(sender_email, receiver_email, message.as_string())'''
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def home():
    token = session.get('token', None)
    is_authenticated = False

    if token:
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=decoded_token['public_id']).first()
            if current_user:
                is_authenticated = True
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass

    return render_template('index.html', is_authenticated=is_authenticated)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token', None)
        if not token:
            return redirect('/login')

        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=decoded_token['public_id']).first()
            if not current_user:
                msg = "User not found"
                encoded_msg = base64.b64encode(msg.encode()).decode()
                return redirect(f'/login?e={encoded_msg}')
            
            kwargs['current_user'] = current_user
            
        except jwt.ExpiredSignatureError:
            msg = "Token has expired. Please log in again"
            encoded_msg = base64.b64encode(msg.encode()).decode()
            return redirect(f'/login?e={encoded_msg}')
        except jwt.InvalidTokenError:
            msg = "Invalid token. Please log in again"
            encoded_msg = base64.b64encode(msg.encode()).decode()
            return redirect(f'/login?e={encoded_msg}')

        return f(*args, **kwargs)
    
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        token = session.get('token', None)
        if token:
            try:
                decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                return redirect('/dashboard')
            except jwt.ExpiredSignatureError as e:
                pass
            except jwt.InvalidTokenError as e:
                pass

        return render_template('sign_in.html', name_platform=NAME_PLATFORM)
    
    elif request.method == "POST":
        data = request.get_json()
        username = data['__data__']['__user__']['username']
        password = data['__data__']['__user__']['password']
        
        if not data or not username or not password:
            return jsonify({'status': False, 'message': "Invalid request data", "type": "request_data"})
        user = User.query.filter_by(email=username).first()
        if not user:
            return jsonify({'status': False, 'message': "User not found", "type": "email"})
        if not user.confirmed:
            return jsonify({'status': False, 'message': "Account not confirmed. Check your email.", "type": "email"})
        if not check_password_hash(user.password, password):
            return jsonify({'status': False, 'message': "Incorrect password", "type": "password"})
        elif check_password_hash(user.password, password) and user.confirmed:
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
            session["logged_in"] = True
            return jsonify({'status': True, 'token': token})
        
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        token = session.get('token', None)
        if token:
            try:
                decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                return redirect('/dashboard')
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass

        return render_template('sign_up.html', name_platform=NAME_PLATFORM)
    elif request.method == "POST":
        data = request.get_json()
        data = data['__data__']['__user__']

        if data['policy'] != True:
            return jsonify({'status': False, 'message': "* You haven't adopted our policy", "type": "policy"})
        
        if data['password'] == "":
            return jsonify({'status': False, 'message': "* * The password field cannot be empty", "type": "password"})
        
        if data['password'] != data['comfirm']:
            return jsonify({'status': False, 'message': "* The passwords don't match", "type": "comfirm"})
        
        if not data['email']:
            return jsonify({'status': False, 'message': "* Email empty", "type": "email"})
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$')
        if not email_pattern.match(data['email']):
            return jsonify({'status': False, 'message': "* Email is not up to standard", "type": "email"})
        
        existing_user = User.query.filter_by(email=data['email'], confirmed=False).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        existing_confirmed_user = User.query.filter_by(email=data['email'], confirmed=True).first()
        if existing_confirmed_user:
            return jsonify({'status': False, 'message': "* Email already in use", "type": "email"})

        hashed_password = generate_password_hash(data['password'], method='scrypt')
        uuid_str = str(uuid.uuid4())
        hash_qr = hashlib.md5(uuid_str.encode()).hexdigest()
        new_user = User(public_id=uuid_str, company_name=data['company'], country=data['country'], timezone=data['timezone'], anonimus_feedback=hash_qr, code_number=data['code_number'], password=hashed_password, email=data['email'])
        
        db.session.add(new_user)
        db.session.commit()

        # send confirmation email
        token = jwt.encode({'user_id': new_user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        
        send_email(data['email'], token, type="register")

        domain_links = {
            'gmail.com': 'https://mail.google.com/mail/u/0/#inbox',
            'yahoo.com': 'https://mail.yahoo.com/',
            'outlook.com': 'https://outlook.live.com/',
            'hotmail.com': 'https://outlook.live.com/',
            'live.com': 'https://outlook.live.com/',
            'msn.com': 'https://outlook.live.com/',
            'yandex.ru': 'https://mail.yandex.ru/',
            'yandex.com': 'https://mail.yandex.com/',
            'aol.com': 'https://mail.aol.com/',
            'icloud.com': 'https://www.icloud.com/mail',
            'mail.ru': 'https://e.mail.ru/',
            'inbox.ru': 'https://e.mail.ru/',
            'list.ru': 'https://e.mail.ru/',
            'bk.ru': 'https://e.mail.ru/',
            'me.com': 'https://www.icloud.com/mail',
            'zoho.com': 'https://mail.zoho.com/',
            'protonmail.com': 'https://mail.protonmail.com/',
            'tutanota.com': 'https://mail.tutanota.com/',
            'fastmail.com': 'https://www.fastmail.com/',
            'gmX.com': 'https://www.gmx.com/',
            'web.de': 'https://web.de/',
        }
        username, domain = data['email'].split('@')
        link = domain_links.get(domain, None)
        
        return jsonify({'status': True,'message': 'User registered!', "link": link})
    
@app.route('/set_token/<token>', methods=['GET'])
def set_token(token):
    session['token'] = token
    return redirect('/dashboard')

def getUserData(current_user):
    """
    User data from db User()
    """
    qr__code = qrCodeAnonimusFeedback(current_user.anonimus_feedback, current_user.company_name)
    return  {
        'public_id': current_user.public_id,
        'company_name': current_user.company_name,
        'email': current_user.email,
        'country': current_user.country,
        'timezone': current_user.timezone,
        'code_number': current_user.code_number,
        'avatar': current_user.avatar,
        'plan':  current_user.plan,
        "qr__code": qr__code,
        'anonimus_feedback':  current_user.anonimus_feedback,
        "slogan": current_user.slogan
    }

#! Dashboard 
@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    user_data = getUserData(current_user)
    with open("./templates/pages_dashboard/main.html", 'r') as f:
        html = f.read()
    rendered_html = render_template_string(html, data_page=user_data)

    data_page = {
        "title": "Dashboard",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard", "name": "Dashboard"},
        ],
        "user_data": user_data
    }
    return render_template('dashboard.html', data_page=data_page)

#! Feedback
@app.route('/dashboard/feedback', methods=['GET'])
@token_required
def feedback(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/feedback.html", 'r', encoding='utf-8') as f:
        html = f.read()
    data_page = {
        "title": "Feedback",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/feedback", "name": "Feedback"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Services 
@app.route('/dashboard/services', methods=['GET'])
@token_required
def services(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/services.html", 'r', encoding='utf-8') as f:
        html = f.read()
    data_page = {
        "title": "Services",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Feedback | Anonymous
@app.route('/dashboard/services/feedback/anonymous', methods=['GET'])
@token_required
def services_anonymous(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/feedback_anonimus.html", 'r', encoding='utf-8') as f:
        html = f.read()
    data_page = {
        "title": "Anonymous feedback",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/feedback/anonymous", "name": "Anonymous feedback"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Feedback | Custom List
@app.route('/dashboard/services/feedback/custom', methods=['GET'])
@token_required
def feedback_custom(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/feedback_custom.html", 'r', encoding='utf-8') as f:
        html = f.read()
    rendered_html = render_template_string(html, data_page={"question": QUESTIONS, "domain": DOMAIN})
    data_page = {
        "title": "Custom feedback",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/feedback/custom", "name": "Custom feedback"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Quiz | Custom link
@app.route('/dashboard/services/quiz/create', methods=['GET'])
@token_required
def quiz_create_link(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/quiz/create_quiz.html", 'r', encoding='utf-8') as f:
        html = f.read()
    rendered_html = render_template_string(html, data_page={"question": QUESTIONS, "edit": False,})
    data_page = {
        "title": "Create quiz",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/quiz", "name": "Quiz"},
            {"link": "/dashboard/services/quiz/create", "name": "Create quiz"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Quiz | Edit link
@app.route('/dashboard/services/quiz/edit/<token>', methods=['GET'])
@token_required
def quiz_edit(current_user, token):
    quizes = QuizToken.query.filter_by(public_id=current_user.public_id, token_quiz=token).first()
    if not quizes:
        return redirect('/dashboard/services/quiz')
    
    obj = {
        "token_quiz": quizes.token_quiz,
        "title": quizes.title,
        "image": quizes.image,
        "theme_color": quizes.theme_color,
        "questions": json.loads(quizes.questions),
        "request": quizes.request,
        "company_badge": quizes.company_badge,
    }
    print(json.loads(quizes.questions))

    user_data = getUserData(current_user)
    with open("./templates/pages_dashboard/quiz/create_quiz.html", 'r', encoding='utf-8') as f:
        html = f.read()
    rendered_html = render_template_string(html, data_page={"question": QUESTIONS, "edit": True, "data": obj})
    data_page = {
        "title": "Edit quiz",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/quiz", "name": "Quiz"},
            {"link": "/dashboard/services/quiz/edit/<token>", "name": "Edit quiz"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)


def compress_base64_image(base64_string, output_format='PNG', quality=20):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image = image.resize((int(image.width / 2), int(image.height / 2)))
    buffered = io.BytesIO()
    image.save(buffered, format=output_format, quality=quality)
    return base64.b64encode(buffered.getvalue()).decode()

def check_image_size(base64_string):
    image_data = base64.b64decode(base64_string)
    
    size_mb = len(image_data) / (1024 * 1024)
    return size_mb <= 10

#! Feedback | Get quizes 
@app.route('/api/quiz/list', methods=['GET'])
@token_required
def get_tokens(current_user):
    user_data = User.query.filter_by(public_id=current_user.public_id).first()
    if not user_data:
        return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

    query = QuizToken.query.filter_by(public_id=current_user.public_id)
    search_query = request.args.get('q')
    if search_query:
        query = query.filter(QuizToken.title.ilike(f"%{search_query}%"))

    quizes = query.all()
    list = []
    if len(quizes) > 0:
        for quiz in quizes:
            list.append({
                "token_quiz": quiz.token_quiz,
                "title": quiz.title,
                "image": quiz.image,
                "theme_color": quiz.theme_color,
                "questions": quiz.questions,
                "request": quiz.request,
                "company_badge": quiz.company_badge,
                "timestamp": quiz.timestamp,
            })

    return jsonify({"success": True, "list": list})

#! Feedback | Delete quiz link 
@app.route('/quiz/delete', methods=['POST'])
@token_required
def delete_link_quiz(current_user):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})
        token = response['token']
        if not token:
            return jsonify({"success": False, "message": "Token is missing"})

        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

        test_questions = QuizToken.query.filter_by(public_id=user_data.public_id, token_quiz=token).all()
        if not test_questions:
            return jsonify({"success": False, "message": "The custom link does not exist or has already been removed"})

        for question in test_questions:
            db.session.delete(question)

        test_qery_results = QuizResults.query.filter_by(public_id=user_data.public_id, quiz_token=token).all()
        for result in test_qery_results:
            db.session.delete(result)

        db.session.commit()
        return jsonify({"success": True, "message": "Quiz deleted successfully"})

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": "An error occurred during deletion"})
        
#! Quiz | Add new quiz link 
@app.route('/api/quiz/create_link', methods=['POST'])
@token_required
def add_token_new_quiz(current_user):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})

        title = response.get('title')
        image = response.get('image')
        theme_color = response.get('theme_color')
        questions = response.get('questions', [])
        request_var = response.get('request', False)
        company_badge = response.get('company_badge', False)

        if not title:
            return jsonify({"success": False, "message": "You did not provide a title for the survey"})
        if not image:
            return jsonify({"success": False, "message": "You didn't submit a picture for the poll"})
        if not theme_color:
            return jsonify({"success": False, "message": "You didn't convey the color of the theme in the quiz"})
        if not questions:
            return jsonify({"success": False, "message": "The array with questions is missing"})
        if len(questions) == 0:
            return jsonify({"success": False, "message": "Empty array with questions, need to pass at least 1 question"})
        if not isinstance(company_badge, bool):
            return jsonify({"success": False, "message": "You did not pass a bool for whether your company icon should be shown or not"})

        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

        uuid_str = str(uuid.uuid4()) + user_data.public_id + str(uuid.uuid4())
        hash_qr = hashlib.md5(uuid_str.encode()).hexdigest()

        base64_str = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', image)
        compressed_base64 = compress_base64_image(base64_str)

        if not check_image_size(compressed_base64):
            return jsonify({"success": False, "message": "The image is larger than 10mb, it should be smaller"})
        
        quiz_question = QuizToken(
            public_id=user_data.public_id,
            token_quiz=hash_qr,
            title=title,
            image=compressed_base64,
            theme_color=theme_color,
            questions=json.dumps(questions),
            request=request_var,
            company_badge=company_badge,
            timestamp=datetime.datetime.utcnow()
        )

        db.session.add(quiz_question)
        db.session.commit()

        return jsonify({"success": True, "message": "Quiz created successfully"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})
   
#! Quiz | Add new quiz link 
@app.route('/api/quiz/edit', methods=['POST'])
@token_required
def edit_quiz(current_user):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})

        token = response.get('token')
        if not token:
            return jsonify({"success": False, "message": "Token has been removed from the element, or not transferred, reload the page"})
        quiz_edit = QuizToken.query.filter_by(token_quiz=token, public_id=current_user.public_id).first()
        if not quiz_edit:
            return jsonify({"success": False, "message": "The token does not belong to you, or is incorrectly specified, reload the page"})
        
        title = response.get('title')
        image = response.get('image')
        theme_color = response.get('theme_color')
        questions = response.get('questions', [])
        request_var = response.get('request', False)
        company_badge = response.get('company_badge', False)
        if not title:
            return jsonify({"success": False, "message": "You did not provide a title for the survey"})
        if not image:
            return jsonify({"success": False, "message": "You didn't submit a picture for the poll"})
        if not theme_color:
            return jsonify({"success": False, "message": "You didn't convey the color of the theme in the quiz"})
        if not questions:
            return jsonify({"success": False, "message": "The array with questions is missing"})
        if len(questions) == 0:
            return jsonify({"success": False, "message": "Empty array with questions, need to pass at least 1 question"})
        if not isinstance(company_badge, bool):
            return jsonify({"success": False, "message": "You did not pass a bool for whether your company icon should be shown or not"})

        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})


        image_changed = True
        base64_str = re.sub(r'^data:image\/[a-zA-Z]+;base64,', '', image)
        if quiz_edit.image == base64_str:
            image_changed = False
            print('Сжатия не было')
        if image_changed and not check_image_size(base64_str):
            compressed_base64 = compress_base64_image(base64_str)
            if not check_image_size(compressed_base64):
                size_mb = len(base64.b64decode(compressed_base64)) / (1024 * 1024)
                return jsonify({"success": False, "message": f"The image is larger than 10mb after compression, it is {size_mb:.2f} MB"})
            image_to_save = compressed_base64
        else:
            image_to_save = base64_str

        quiz_edit.title=title
        quiz_edit.image=image_to_save
        quiz_edit.theme_color=theme_color
        quiz_edit.questions=json.dumps(questions)
        quiz_edit.request=request_var
        quiz_edit.company_badge=company_badge

        db.session.commit()

        return jsonify({"success": True, "message": "Quiz created successfully"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})
   
#! Feedback | Quiz List
@app.route('/dashboard/services/quiz', methods=['GET'])
@token_required
def quiz_list(current_user):
    user_data = getUserData(current_user)
    with open("./templates/pages_dashboard/quiz/quiz_table.html", 'r', encoding='utf-8') as f:
        html = f.read()


    user_data = User.query.filter_by(public_id=current_user.public_id).first()
    if not user_data:
        return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

    query = QuizToken.query.filter_by(public_id=current_user.public_id)
    search_query = request.args.get('q')
    if search_query:
        query = query.filter(QuizToken.title.ilike(f"%{search_query}%"))

    quizes = query.all()
    list = []
    if len(quizes) > 0:
        for quiz in quizes:
            list.append({
                "token_quiz": quiz.token_quiz,
                "title": quiz.title,
                "image": quiz.image,
                "theme_color": quiz.theme_color,
                "questions": quiz.questions,
                "request": quiz.request,
                "company_badge": quiz.company_badge,
                "timestamp": quiz.timestamp,
            })
    rendered_html = render_template_string(html, data_page={"domain": DOMAIN, "data": list})
    
    data_page = {
        "title": "Quiz",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/quiz", "name": "Quiz"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

def format_time(milliseconds, include_ms=False):
    if not milliseconds or milliseconds == 0:
        return False

    # Converting milliseconds to seconds, minutes, hours
    seconds = (milliseconds // 1000) % 60
    minutes = (milliseconds // (1000 * 60)) % 60
    hours = (milliseconds // (1000 * 60 * 60)) % 24
    ms = milliseconds % 1000  # Remaining milliseconds

    # Including milliseconds in seconds if required
    if include_ms and ms > 0:
        seconds += ms / 1000.0

    # Building the formatted time string
    formatted_time = ""
    if hours > 0:
        formatted_time += f"{hours} hour{'s' if hours > 1 else ''} "
    
    if minutes > 0 or (hours > 0 and seconds > 0):
        if hours > 0:
            formatted_time += "and "
        formatted_time += f"{minutes} minute{'s' if minutes > 1 else ''} "
    
    if seconds > 0 or (hours > 0 or minutes > 0):
        if minutes > 0:
            formatted_time += "and "
        formatted_seconds = f"{seconds:.2f}" if include_ms else f"{int(seconds)}"
        formatted_time += f"{formatted_seconds} sec{'s' if seconds != 1 else ''}"

    # Return the formatted time string
    return formatted_time.strip()

def calculate_average_time(times):
    if not times:
        return 0
    return sum(times) / len(times)

#! Feedback | Quiz List Token
@app.route('/dashboard/services/quiz/<token>', methods=['GET'])
@token_required
def quiz_token_info(current_user, token):
    user_data = getUserData(current_user)

    quizToken = QuizToken.query.filter_by(token_quiz=token, public_id=current_user.public_id).first()
    if not quizToken:
        return redirect('/dashboard/services/quiz')
    
    token_quiz = token
    quiz_results = QuizResults.query.filter_by(quiz_token=token, public_id=current_user.public_id).all()

    quiz_results_array = []
    average_time_array = []
    count_results = len(quiz_results)
    for item in quiz_results:
        times_arr = []
        answer = json.loads(item.answer)
        new_answer = []
        for el in answer:
            timer = el['timer'] * 1000
            if el['time_quiz']:
                times_arr.append(el['time_quiz'])
            str_time = format_time(timer)
            str_time_parse = format_time(el['time_quiz'], True)
            new_answer.append({
                'timer': timer,
                'timer_parse': str_time,
                'time_quiz': el['time_quiz'],
                'time_quiz_parse': str_time_parse,
                'question': el['question'],
                'answer': el['answer']
            })
        average_time_array.append(sum(times_arr))

        average_time = calculate_average_time(times_arr)
        average_time = format_time(average_time, True)
        count_time = format_time(sum(times_arr), True)
        quiz_results_array.append({
            "token": item.token_results,
            "username": item.username,
            "type": item.type,
            "answer": new_answer,
            "timestamp": item.timestamp,
            "average_time": average_time,
            "count_time": count_time
        })

    average_time_array = format_time(calculate_average_time(average_time_array), True)
    obj_info = {
        "title": quizToken.title,
        "image": quizToken.image,
        "theme_color": quizToken.theme_color,
        "request": quizToken.request,
        "timestamp": quizToken.timestamp,
        "count_results": count_results,
        "count_average_time": str(average_time_array)
    }
    
    with open("./templates/pages_dashboard/quiz/quiz_viewer.html", 'r', encoding='utf-8') as f:
        html = f.read()

    reversed_array = quiz_results_array[::-1]
    rendered_html = render_template_string(html, data_page={"domain": DOMAIN, "token": token_quiz, "info_quiz": obj_info, "data": reversed_array})
    data_page = {
        "title": f"Quiz",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/quiz", "name": "Quiz"},
            {"link": f"/dashboard/services/quiz/{token}", "name": token},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Feedback | Custom create link
@app.route('/dashboard/services/feedback/custom/create', methods=['GET'])
@token_required
def feedback_custom_create(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/create_custom_link.html", 'r', encoding='utf-8') as f:
        html = f.read()
    rendered_html = render_template_string(html, data_page={"question": QUESTIONS, "edit": False,})
    data_page = {
        "title": "Create custom link",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/feedback/custom", "name": "Custom feedback"},
            {"link": "/dashboard/services/feedback/custom/create", "name": "Create custom link"},
        ],
        "user_data": user_data,
    }
    return render_template('dashboard.html', data_page=data_page)

#! Profile
@app.route('/dashboard/settings', methods=['GET'])
@token_required
def settings(current_user):
    user_data = getUserData(current_user)

    with open("./templates/pages_dashboard/settings.html", 'r', encoding="utf-8") as f:
        html_template = f.read()
    rendered_html = render_template_string(html_template, data_page={"user_data": user_data})
    data_page = {
        "title": "Settings",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/settings", "name": "Settings"},
        ],
        "user_data": user_data
    }
    return render_template('dashboard.html', data_page=data_page)

#! Logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('token', None)
    return redirect('/login')

@app.route('/testing')
def testing():
    return render_template('testing.html')

@app.route('/stream', methods=['POST'])
def stream():
    token = request.files.get('token')
    audio_file = request.files.get('buffer')
    audio_bytes = audio_file.read()
    path_audio = "./file/audio/" +  str(uuid.uuid4()) + "_" + str(uuid.uuid4()) + ".wav"
    with open(path_audio, 'wb') as f:
        f.write(audio_bytes)
        
    async def main():
        deepgram = Deepgram(DEEPGRAM_API_KEY)
        source = {
            'buffer': io.BytesIO(audio_bytes),
            'mimetype': MIMETYPE
        }

        response = await asyncio.create_task(
            deepgram.transcription.prerecorded(
                source,
                {
                    'smart_format': True,
                    'model': 'base',
                    'punctuate': True,
                    'language': 'en'
                }
            )
        )
        result = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        os.remove(path_audio)
        return result
    try:
        result = asyncio.run(main())
        encrypted_message = encrypt(result)
        # decrypted_message = decrypt(encrypted_message)
        return jsonify({"success": True, "message": "Thanks for the feedback!", "text": encrypted_message})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        return jsonify({"success": False, "message": "There was some kind of error. Try again"})

@app.route('/anonymous/<token>', methods=['GET'])
def anonimy(token):
    data_company = User.query.filter_by(anonimus_feedback=token).first()
    if not data_company:
        return redirect('/', code=302)
    
    json_data = json.dumps(QUESTIONS).encode('utf-8')
    base64_encoded_data = base64.b64encode(json_data).decode('utf-8')
    data_company = {
        "title": NAME_PLATFORM + ' | Anonymous feedback',
        "type": "anonymous",
        "company_name": data_company.company_name,
        "country": data_company.country,
        "plan": data_company.plan,
        "avatar": data_company.avatar,
        "timezone": data_company.timezone,
        "slogan": data_company.slogan,
        "questions": f"<script> var qr = '{base64_encoded_data}'; var to = '{token}'; </script>",
    }

    return render_template('testing.html', data_company=data_company)

@app.route('/feedback/<token>', methods=['GET'])
def feedback_token(token):
    data_tested = TestingResult.query.filter_by(only=token).first()
    
    if not data_tested:
        return redirect('/', code=302)
    
    json_data = json.dumps(json.loads(data_tested.questions)).encode('utf-8')
    base64_encoded_data = base64.b64encode(json_data).decode('utf-8')
    data_company = User.query.filter_by(public_id=data_tested.public_id).first()
    data_tested_res = {
        "title": NAME_PLATFORM + ' | Feedback',
        "type": data_tested.type,
        "multiple": data_tested.multiple,
        "anonimus_feedback": data_tested.anonimus_feedback,
        "username": data_tested.username,
        "username_bool": data_tested.username_bool,
        "checked": data_tested.checked,
        "company_name": data_company.company_name,
        "country": data_company.country,
        "plan": data_company.plan,
        "avatar": data_company.avatar,
        "timezone": data_company.timezone,
        "slogan": data_company.slogan,
        "anonimus_feedback_link": DOMAIN + "/anonymous/" + data_company.anonimus_feedback,
        "questions": f"<script> var qr = '{base64_encoded_data}'; var to = '{token}'; </script>",
    }

    return render_template('testing.html', data_company=data_tested_res)

@app.route('/quiz/<token>', methods=['GET'])
def quiz_token(token):
    data_tested = QuizToken.query.filter_by(token_quiz=token).first()
    
    if not data_tested:
        return redirect('/', code=302)
    
    data_company = User.query.filter_by(public_id=data_tested.public_id).first()

    json_data = json.dumps(json.loads(data_tested.questions)).encode('utf-8')
    base64_encoded_data = base64.b64encode(json_data).decode('utf-8')
    en = json.loads(data_tested.questions)
    company_info = {}
    if data_tested.company_badge:
        company_info = {
            "company_name": data_company.company_name,
            "avatar": data_company.avatar,
        }

    data_tested_res = {
        "title": NAME_PLATFORM + ' | Quiz',
        "title_quiz": data_tested.title,
        "image": 'data:image/png;base64,' + data_tested.image,
        "theme_color": data_tested.theme_color,
        "request": data_tested.request,
        "company_badge": data_tested.company_badge,
        "_company": company_info,
        "encoded_data": en[0],
        "questions": f"<script> var qr = '{base64_encoded_data}'; var to = '{token}'; </script>",
    }

    return render_template('quiz.html', data_company=data_tested_res)

@app.route('/quiz/done/<token>', methods=['POST'])
def quiz_done(token):
    response = request.get_json()
    try:
        user_answer = response['up788t7f2bou7t8323vc234eg']
        
        if len(user_answer) == 0:
            return jsonify({"success": False, "message": "There was an unexplained error, please try anonymous testing again"})
        quiz_data = QuizToken.query.filter_by(token_quiz=token).first()
        if not quiz_data:
            return jsonify({"success": False, "message": "The test token is not passed correctly, check the correctness of the parameter"})
        user_data = User.query.filter_by(public_id=quiz_data.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user"})
        
        public_id = quiz_data.public_id
        uuid_str = str(uuid.uuid4()) + public_id + token + str(uuid.uuid4())
        hash_qr = hashlib.md5(uuid_str.encode()).hexdigest()
        quiz_db = QuizResults(
            public_id=quiz_data.public_id,
            quiz_token=token,
            token_results=hash_qr,
            type=str(response['type']),
            username=str(response['username']),
            answer=json.dumps(user_answer),
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(quiz_db)
        db.session.commit()

        return jsonify({"success": True, "message": "Thanks for the feedback!"})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": "Not parameters not received"})
    
@app.route('/feedback/done/<token>', methods=['POST'])
def feedback_done(token):
    response = request.get_json()
    try:
        user_answer = response['34er456jwqev54']
        if len(user_answer) == 0:
            return jsonify({"success": False, "message": "There was an unexplained error, please try anonymous testing again"})

        find_this_token = TestingResult.query.filter_by(only=token).first()
        if not find_this_token:
            return jsonify({"success": False, "message": "Such a custom link does not exist"})
        
        name_user_str = response.get('name_user', "")
        if find_this_token.multiple == False:
            print("Одноразовые")

            user_answer = json.dumps(user_answer)
            public_id = find_this_token.public_id
            check_user = User.query.filter_by(public_id=public_id)
            if not check_user:
                return jsonify({"success": False, "message": "There is no longer a user who owns this token."})
            
            find_this_token.username = name_user_str
            find_this_token.user_answer = user_answer
            find_this_token.checked = True

            db.session.commit()
        else:
            print("Многоразовые")


        return jsonify({"success": True, "message": "Thanks for the feedback!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})
    
@app.route('/anonymous/done/<token>', methods=['POST'])
def anonymous_done(token):
    response = request.get_json()
    try:
        user_answer = response['8v98as99g']

        if len(user_answer) == 0:
            return jsonify({"success": False, "message": "There was an unexplained error, please try anonymous testing again"})
        
        user_data = User.query.filter_by(anonimus_feedback=token).first()

        if not user_data:
            return jsonify({"success": False, "message": "The test token is not passed correctly, check the correctness of the parameter"})
        
        public_id = user_data.public_id
        user_answer = json.dumps(user_answer)

        test_question = TestingResult(public_id=public_id, anonimus_feedback=True, user_answer=user_answer, only=False, username=False, multiple=False, username_bool=False, result=False, checked=False, type="anonymous", timestamp=datetime.datetime.utcnow())
        db.session.add(test_question)
        db.session.commit()

        return jsonify({"success": True, "message": "Thanks for the feedback!"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})
    
#! Feedback | Create custom link 
@app.route('/feedback/create_link', methods=['POST'])
@token_required
def create_link_feedback(current_user):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})

        name = response.get('name')
        anonymous = response.get('anonymous', False)
        multiple = response.get('multiple', False)
        questions = response.get('questions', [])
        username_req = response.get('username_req', False)
        ai = response.get('ai', False)

        if not name:
            return jsonify({"success": False, "message": "Token name is missing"})
        if not isinstance(ai, bool):
            return jsonify({"success": False, "message": "Parameters ai is missing"})
        if not isinstance(anonymous, bool):
            return jsonify({"success": False, "message": "The anonymity parameter is not passed, it is a mandatory parameter"})
        if not isinstance(multiple, bool):
            return jsonify({"success": False, "message": "The multiple parameter is not passed, it is a declarative parameter"})
        if not questions:
            return jsonify({"success": False, "message": "The array with questions is missing"})
        if len(questions) == 0:
            return jsonify({"success": False, "message": "Empty array with questions, need to pass at least 1 question"})

        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

        username_bool = False
        if not anonymous:
            if not isinstance(username_req, bool):
                return jsonify({"success": False, "message": "Invalid username_req parameter"})
            username_bool = username_req

        uuid_str = str(uuid.uuid4()) + user_data.public_id + str(uuid.uuid4())
        hash_qr = hashlib.md5(uuid_str.encode()).hexdigest()

        test_question = TestingResult(
            public_id=user_data.public_id,
            anonimus_feedback=anonymous,
            questions=json.dumps(questions),
            user_answer=False,
            only=hash_qr,
            name=name,
            count=0,
            multiple=multiple,
            username_bool=username_bool,
            result=False,
            checked=False,
            ai=ai,
            ai_status=False,
            type="custom",
        )
        db.session.add(test_question)
        db.session.commit()

        return jsonify({"success": True, "message": "Feedback created successfully"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})
               
#! Feedback | Edit page custom link
@app.route('/dashboard/services/feedback/custom/edit/<token>', methods=['GET'])
@token_required
def feedback_custom_edit(current_user, token):
    user_data = getUserData(current_user)

    user = User.query.filter_by(public_id=current_user.public_id).first()
    if not user:
        return redirect('/')
    
    tested_data = TestingResult.query.filter_by(only=token, public_id=current_user.public_id).first()
    if not tested_data:
        return redirect('/')
    
    answer = json.loads(tested_data.questions)
    with open("./templates/pages_dashboard/create_custom_link.html", 'r', encoding='utf-8') as f:
        html = f.read()

    obj = {
        "ai": tested_data.ai,
        "multiple": tested_data.multiple,
        "username_bool": tested_data.username_bool,
        "anonimus_feedback": tested_data.anonimus_feedback
    }
    rendered_html = render_template_string(html, data_page={"question": answer, "obj": obj, "edit": True})

    data_page = {
        "title": "Edit custom link",
        "path": request.path,
        "name_platform": NAME_PLATFORM,
        "html_page": rendered_html,
        "branch": [
            {"link": "/", "name": "Home"},
            {"link": "/dashboard/services", "name": "Services"},
            {"link": "/dashboard/services/feedback/custom", "name": "Custom feedback"},
            {"link": f"/dashboard/services/feedback/custom/edit/{token}", "name": "Edit custom link"},
        ],
        "user_data": user_data,
        "script": f"<script>var to = '{token}'; </script>",
    }
    return render_template('dashboard.html', data_page=data_page)

#! Feedback | Edit custom link
@app.route('/feedback/edit/<token>', methods=['POST'])
@token_required
def edit_link_feedback(current_user, token):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})

        if not token:
            return jsonify({"success": False, "message": "Token is missing"})
        
        name = response.get('name')
        anonymous = response.get('anonymous', False)
        multiple = response.get('multiple', False)
        questions = response.get('questions', [])
        username_req = response.get('username_req', False)
        ai = response.get('ai', False)

        if not name:
            return jsonify({"success": False, "message": "Token name is missing"})
        if not isinstance(ai, bool):
            return jsonify({"success": False, "message": "Parameters ai is missing"})
        if not isinstance(anonymous, bool):
            return jsonify({"success": False, "message": "The anonymity parameter is not passed, it is a mandatory parameter"})
        if not isinstance(multiple, bool):
            return jsonify({"success": False, "message": "The multiple parameter is not passed, it is a declarative parameter"})
        if not questions:
            return jsonify({"success": False, "message": "The array with questions is missing"})
        if len(questions) == 0:
            return jsonify({"success": False, "message": "Empty array with questions, need to pass at least 1 question"})

        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

        username_bool = False
        if not anonymous:
            if not isinstance(username_req, bool):
                return jsonify({"success": False, "message": "Invalid username_req parameter"})
            username_bool = username_req

        test_edit = TestingResult.query.filter_by(only=token, public_id=current_user.public_id).first()
        if not test_edit:
            return jsonify({"success": False, "message": "Such a custom link does not exist or such a user does not exist"})
        
        test_edit.name = name
        test_edit.multiple = multiple
        test_edit.anonimus_feedback = anonymous
        test_edit.questions = json.dumps(questions)
        test_edit.username_bool = username_bool
        test_edit.ai = ai
        test_edit.timestamp = datetime.datetime.utcnow()

        db.session.commit()

        return jsonify({"success": True, "message": "The changes have been successfully saved"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Not parameters not received"})

#! Feedback | Delete custom link 
@app.route('/feedback/delete', methods=['POST'])
@token_required
def delete_link_feedback(current_user):
    try:
        response = request.get_json()
        if not response:
            return jsonify({"success": False, "message": "Invalid JSON data"})

        token = response['token']
        print(token)
        if not token:
            return jsonify({"success": False, "message": "Token is missing"})
        
        user_data = User.query.filter_by(public_id=current_user.public_id).first()
        if not user_data:
            return jsonify({"success": False, "message": "There is no such user, don't try to hack our requests"})

        test_question = TestingResult.query.filter_by(
            public_id=user_data.public_id,
            only=token,
            type="custom",
        ).first()
        if not test_question:
            return jsonify({"success": False, "message": "The custom link does not exist or has already been removed"})
        
        db.session.delete(test_question)
        db.session.commit()

        return jsonify({"success": True, "message": "Feedback deleted successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": "Not parameters not received"})
        
@app.route('/api/get/anonymous', methods=['GET'])
@token_required
def anonymous_list(current_user):
    all_list = TestingResult.query.filter_by(public_id=current_user.public_id).all()
    if not all_list:
        return jsonify({'status': False, 'list': []}), 200

    results = []
    for item in all_list:
        if item.checked == False or item.anonimus_feedback == "0" or item.anonimus_feedback == False or item.type != "anonymous":
            continue

        results.append({
            'result': json.loads(item.result),
            'timestamp': item.timestamp
        })

    return jsonify({'status': True, 'list': results}), 200

@app.route('/api/get/feeback_custom', methods=['GET'])
@token_required
def anonymous_custom(current_user):
    all_list = TestingResult.query.filter_by(public_id=current_user.public_id).all()
    if not all_list:
        return jsonify({'status': False, 'list': []}), 200

    results = []
    for item in all_list:
        if item.type == "anonymous":
            continue

        obj = {
            'anonimus_feedback': item.anonimus_feedback,
            'checked': item.checked,
            'type': item.type,
            'only': item.only,
            'multiple': item.multiple,
            'username_bool': item.username_bool,
            'name': item.name,
            'count': item.count,
            'result': json.loads(item.result),
            'timestamp': item.timestamp
        }
        if not item.anonimus_feedback and item.username_bool:
            obj['username'] = item.username

        results.append(obj)

    return jsonify({'status': True, 'list': results}), 200

@app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user = User.query.filter_by(id=data['user_id']).first()
        if not user:
            return 'User not found'
        user.confirmed = True
        db.session.commit()
    except Exception as e:
        return f'Token error: {str(e)}'

    return redirect('/login', code=302)

#! Setting | Change Company name
@app.route('/api/update_company_name', methods=['POST'])
@token_required
def update_company_name(current_user):
    data = request.get_json()
    if 'company_name' not in data:
        return jsonify({'status': False, 'message': 'No company name proфvided'}), 200

    new_name = data['company_name']
    if current_user.company_name == new_name:
        return jsonify({'status': False, 'message': 'New company name cannot be the same as the current one'}), 200

    current_user.company_name = new_name
    db.session.commit()

    return jsonify({'status': True, 'message': 'Company name updated successfully'}), 200

#! Setting | Change slogan
@app.route('/api/update_slogan', methods=['POST'])
@token_required
def update_slogan(current_user):
    data = request.get_json()
    if 'slogan' not in data:
        return jsonify({'status': False, 'message': 'No slogan provided'}), 200

    new_slogan = data['slogan']
    if current_user.slogan == new_slogan:
        return jsonify({'status': False, 'message': 'New slogan cannot be the same as the current one'}), 200

    current_user.slogan = new_slogan
    db.session.commit()

    return jsonify({'status': True, 'message': 'Slogan updated successfully'}), 200

#! Setting | Change Update avatar
@app.route('/api/update_avatar', methods=['POST'])
@token_required
def update_avatar(current_user):
    if 'logo' not in request.files:
        return jsonify({'status': False, 'message': 'Logo parameter not passed'}), 200

    uploaded_file = request.files['logo']

    if uploaded_file.filename == '':
        return jsonify({'status': False, 'message': 'No selected file'}), 200
    
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    if len(uploaded_file.read()) > MAX_FILE_SIZE_BYTES:
        return jsonify({'status': False, 'message': 'File is too large. Maximum size is 10MB.'}), 400

    uploaded_file.seek(0)
    file_data = uploaded_file.read()
    encoded_image_data = base64.b64encode(file_data).decode('utf-8')
    image_data_string = f"data:image/{uploaded_file.content_type.split('/')[-1]};base64,{encoded_image_data}"
    current_user.avatar = image_data_string
    db.session.commit()

    return jsonify({'status': True, 'message': 'Logo successfully updated', "src": image_data_string}), 200

#! Setting | Change password
@app.route('/api/change_password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'status': False, 'message': 'Current password and new password are required'}), 200

    current_password = data['current_password']
    new_password = data['new_password']

    if not check_password_hash(current_user.password, current_password):
        return jsonify({'status': False, 'message': 'Current password is incorrect'}), 200

    hashed_new_password = generate_password_hash(new_password, method='scrypt')
    current_user.password = hashed_new_password
    db.session.commit()

    return jsonify({'status': True, 'message': 'Password successfully changed'}), 200

#! Setting | Delete account
@app.route('/api/delete_account', methods=['DELETE'])
@token_required
def delete_account(current_user):
    try:
        db.session.delete(current_user)
        session.pop('token', None)
        db.session.commit()
        return jsonify({'status': True, 'message': 'Account successfully deleted'}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': 'Error occurred: ' + str(e)}), 500
    
#! Setting | Add Testing
@app.route('/api/add_to_testing', methods=['POST'])
@token_required
def add_to_testing(current_user):
    public_id = current_user.public_id
    data = request.get_json()
    name_token = data["name_token"]
    token = str(uuid.uuid4()) + "" + str(uuid.uuid4())

    new_test_record = Testing(public_id=public_id, name_token=name_token, token=token, valid=False, timestamp=datetime.datetime.utcnow())
    
    db.session.add(new_test_record)
    db.session.commit()

    return jsonify({'status': True, 'message': 'Data added to Testing table'})

#! Setting | Get Testing
@app.route('/api/get_user_data', methods=['GET'])
@token_required
def get_user_data(current_user):
    public_id = current_user.public_id
    user_records = Testing.query.filter_by(public_id=public_id).all()
    if not user_records:
        return jsonify({'status': False, 'message': 'No data found for the user.'})

    output = []
    for record in user_records:
        record_data = {
            'name_token': record.name_token,
            'token': record.token,
            'valid': record.valid,
            'timestamp': record.timestamp,
            'result': record.result,
        }
        output.append(record_data)

    return jsonify({'status': True, 'data': output})

if __name__ == "__main__":
    # flask db migrate -m "description of the change"
    # flask db upgrade
    run_migrations()
    app.run(debug=True)
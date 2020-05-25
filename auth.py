from flask import ( 
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    make_response,
    flash
    )
import threading
from os import environ

auth_bp = Blueprint('auth_bp', 
    __name__,
    template_folder='templates', 
    static_folder='static',
    )

from app import db
from models import Users
from dryFunctions import *

sg_api = environ.get('SG_API')


@auth_bp.route('/register/user', methods=['POST'])
def user_registration():
    userName = request.json.get('userName')
    userEmail = request.json.get('userEmail')
    userPassword = request.json.get('userPassword')
    userPasswordConfirm = request.json.get('userPasswordConfirm')

    if find_missing(userName, userEmail, userPassword, userPasswordConfirm):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Missing Params'
        }

    elif userPassword != userPasswordConfirm:
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Confirmation Password Different'
        }

    elif malformed_length(
        {
            userName: [3, 64],
            userEmail: [3, 64],
            userPassword: [3, 64] 
        }
    ):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Param Length is Bad'
        }

    elif user_exist(email=hex_hash(userEmail)):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'User Exist'
        }

    elif not is_email_valid(userEmail):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Email is not valid'
        }

    else:
        try:
            userEmailHash = hex_hash(userEmail)
            userPasswordHash = hex_hash(userPassword)
            new_user = Users(username=userName, email=userEmailHash, password=userPasswordHash)
            db.session.add(new_user)
            db.session.commit()
            token = encode_auth_token(user_detail(userEmailHash).get('userId')).decode()
            payLoad = {
                'userName': userName,
                'userEmail': userEmailHash,
                'message': 'User Successfully Created',
                'token': token
            }

            return make_response(jsonify(payLoad), 201)
        
        except Exception as e:

            print(str(e))
            db.session.rollback()
            payLoad = {
                'userName': '',
                'userEmail': '',
                'message': 'Something went wrong'
            }
    
    return make_response(jsonify(payLoad), 400)
    

@auth_bp.route('/login/user', methods=['POST'])
def user_login():
    userEmail = request.json.get('userEmail')
    userPassword = request.json.get('userPassword')
    rememberMe = request.json.get('rememberMe')

    if find_missing(userEmail, userPassword, rememberMe):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Missing Params'
        }


    elif not user_exist(email=hex_hash(userEmail)):
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'User Does not Exist'
        }
    
    else:
        userEmailHash = hex_hash(userEmail)
        userPasswordHash = hex_hash(userPassword)
        user_object = user_detail(userEmailHash)
        if (userPasswordHash == user_object.get('userPassword')):

            token = encode_auth_token(user_object.get('userId'), remember_me=rememberMe).decode()
            payLoad = {
                'userName': user_object.get('userName'),
                'userEmail': userEmailHash,
                'message': 'Success LogIn',
                'token': token
            }
            return make_response(jsonify(payLoad), 200)
        
        payLoad = {
            'userName': '',
            'userEmail': '',
            'message': 'Password Mismatch'
        }

    return make_response(jsonify(payLoad), 400)


@auth_bp.route('/password/reset', methods=['POST'])
def forgot_password():

    userEmail = request.json.get('userEmail')

    if find_missing(userEmail):
        payLoad = {
            'userEmail': '',
            'message': 'Missing Params'
        }

    elif malformed_length(
        {
            userEmail: [3, 64],
        }
    ):
        payLoad = {
            'userEmail': '',
            'message': 'Param Length is Bad'
        }

    elif not user_exist(email=hex_hash(userEmail)):
        payLoad = {
            "email": userEmail,
            "message": "Make a Sign-up"
        }

    else:
        userDetails = user_detail(email=hex_hash(userEmail))
        userName = userDetails.get('userName')
        passwordResetLink = "https://attendance2hosted.herokuapp.com/auth/password/update/" + \
            encode_auth_token(user_id=userEmail, valid_minutes=5).decode()
        templateId = "d-bca83b14b0f44357b6a78fe531249832"

        url = "https://api.sendgrid.com/v3/mail/send"
        email_header = {'Content-Type': 'application/json', "Authorization": sg_api}
        email_body = {
                "personalizations": [
                    {
                        "to": [
                            {
                                "email": userEmail
                            }
                        ],
                        "dynamic_template_data": {
                            "userName": userName,
                            "passwordResetLink": passwordResetLink
                        }
                    }
                ],
                "from": {
                    "email": "pchackers18@gmail.com"
                },
                "template_id": templateId
            }
        
        threading.Thread(target=send_email, args=(url, email_header, email_body)).start()

        payLoad = {
            "email": userEmail,
            "message": "Check your email"
        }

        return make_response(jsonify(payLoad), 202)
    
    return make_response(jsonify(payLoad), 400)


@auth_bp.route('/password/update/<emailHashToken>', methods=['GET', 'PATCH', 'POST'])
def password_updation(emailHashToken):
    print(request.method)
    userEmail = decode_auth_token(emailHashToken)
    
    if request.method=='POST':
        
        if userEmail == 'Signature expired. Please log in again.':
            flash('I suppose you are timed out')
            return render_template('passwordReset.html') # Render to Home Page
        elif userEmail == 'Invalid token. Please log in again.':
            flash('Maybe Hackers love to play')
            return render_template('passwordReset.html') # Render to Home Page
        else:
            userEmailHash = hex_hash(userEmail)


        if not user_exist(userEmailHash):
            flash('Firstly you should Create an Account')
            return render_template('passwordReset.html') # Render to Home Page #--todo-- # Redirect to home page
            
        userEmail = request.form.get('userEmail')
        userPassword = request.form.get('userPassword')
        userPasswordConfirm = request.form.get('userPasswordConfirm')

        if malformed_length(
            {
                userEmail: [3, 64],
                userPassword: [3, 64] 
            }
        ):
            flash('Password length is Absurd')
            return render_template('passwordReset.html')
        
        elif user_detail(hex_hash(userEmail)).get('userEmail') != userEmailHash:
            flash('Is this a Typo?')
            return render_template('passwordReset.html')

        else:
            user = Users.query.filter_by(userEmail=userEmailHash).first()
            user.userPassword = hex_hash(userPassword)
            db.session.commit()
        
            return render_template('passwordReset.html') #--todo--  # Redirect to home page

    return render_template('passwordReset.html')

from flask import ( 
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    make_response 
    )

auth_bp = Blueprint('auth_bp', 
    __name__)

from app import db
from models import Users
from dryFunctions import *


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


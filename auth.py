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

@auth_bp.route('/user/registration', methods=['POST'])
def user_registration():
    username_ = request.json.get('username')
    password_ = request.json.get('password')
    print("\n\nUsername: " + username_)
    try:
        new_user = Users(username=username_, password=password_)
        db.session.add(new_user)
        db.session.commit()
        
        payLoad = {
            "username": username_,
            "password": "********"
        }
        return make_response(jsonify(payLoad), 201)
    
    except Exception as e:
        print(str(e))
        db.session.rollback()
        payLoad = {
            "username": None,
            "password": "********"
        }
        return make_response(jsonify(payLoad), 400)
    


from flask import ( 
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    make_response 
    )
# Templates folder and static_folder are for auth routes
general_bp = Blueprint('general_bp', 
    __name__,
    template_folder='templates', 
    static_folder='static',)

from app import db
from dryFunctions import *
from models import (
    Users,
    Communities,
    CommunityMembers
)

## Imports for Auth Routes
from flask import flash
import threading
from os import environ
from models import BlackListedTokens
sg_api = environ.get('SG_API')

## Putting all Auth Routes untill the issue is resolved!

@general_bp.route('/register/user', methods=['POST'])
def user_registration():
    print('\n\n\n')
    print(str(request.json))
    print('\n\n\n')
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
    

@general_bp.route('/login/user', methods=['POST'])
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



@general_bp.route('/password/reset', methods=['POST'])
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
        print(sg_api)
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
        #send_email(url, email_header, email_body)

        payLoad = {
            "email": userEmail,
            "message": "Check your email"
        }

        return make_response(jsonify(payLoad), 202)
    
    return make_response(jsonify(payLoad), 400)


@general_bp.route('/password/update/<emailHashToken>', methods=['GET', 'PATCH', 'POST'])
def password_updation(emailHashToken):

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


@general_bp.route('logout/user', methods=['GET'])
def logout_user():
    token = request.headers.get('Authorization')
    print(token)
    if token:
        if isBlackListed(token):
            payLoad ={
                "message": "logged-out-already"
            }
        
        elif malformed_length(
            {
                token: [3, 1024],
            }
        ):
            payLoad = {
                'message': ['this-request-is-not-processed',
                'length-constraint-applied'
                ]
            }
        
        elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
            payLoad = {
                "message": ["not-a-valid-request",
                "try-login-first"]
            }

        else:
            blackListed = BlackListedTokens(token=token)
            db.session.add(blackListed)
            db.session.commit()

            payLoad = {
                "message": "user-logged-out"
            }
        
        return make_response(jsonify(payLoad), 200)
    
    payLoad = {
        "message": "missing-token"
    }
    return make_response(jsonify(payLoad), 400)



    ########################################


# HomePage for Everyone
@general_bp.route('/', methods=['GET'])
def testing_route():
    return "Working!!"


@general_bp.route('/community/create', methods=['POST'])
def create_community():
    token = request.headers.get('Authorization')
    communityName = request.json.get('communityName')
    communityDescription = request.json.get('communityDescription')

    if find_missing(token, communityName):
        payLoad = {
            'message': 'missing-params'
        }
    
    elif malformed_length(
        {
            communityName: [1, 64],
            communityDescription: [0, 256]
        }
    ):
        payLoad = {
            'message': 'bad-length-params'
        }
    
    elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
        payLoad = {
            'message': 'fresh-login-required'
        }
    
    elif isBlackListed(token):
        payLoad = {
            'message': 'login-required'
        }
    
    else:
        # If a User creates a two community with same names then that's a problem
        userId = decode_auth_token(token)
        # User Exists or not shall be checked else sqlalchemy error if valid but false token is sended #--todo--
        try:
            comJoinToken = Communities.query.filter(Communities.userId==userId, Communities.communityName==communityName).first().joinToken
            if comJoinToken != None:
                payLoad = {
                    'message': ['choose-a-new-name',
                    'delete-older-community',
                    'same-community-name-exist']
                }
                return make_response(jsonify(payLoad), 400)
                
        except Exception as e:
            print(str(e))

        community = Communities(userId, communityName, communityDescription)
        db.session.add(community)
        db.session.commit()

        communityQuery = Communities.query.filter(Communities.userId==userId, Communities.communityName==communityName).first()
        comJoinToken  = communityQuery.joinToken
        communityId = communityQuery.communityId

        payLoad = {
            'userId': userId,
            'communityName': communityName,
            'communityDescription': communityDescription,
            'comJoinToken': comJoinToken,
            'communityId': communityId,
            'message': 'community-successfully-created'
        }

        return make_response(jsonify(payLoad), 201)
    
    return make_response(jsonify(payLoad), 400)


@general_bp.route('/community/join', methods=['POST'])
def join_community():
    token = request.headers.get('Authorization')
    joinToken = request.json.get('joinToken')

    if find_missing(token, joinToken):
        payLoad = {
            'message': 'missing-params'
        }
    
    elif malformed_length(
        {
            joinToken: [16, 32], # 22 exactly
        }
    ):
        payLoad = {
            'message': 'bad-length-params'
        }
    
    elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
        payLoad = {
            'message': 'fresh-login-required'
        }
    
    elif isBlackListed(token):
        payLoad = {
            'message': 'login-required'
        }

    else:
        
        userId = decode_auth_token(token)


        comJoinToken = Communities.query.filter_by(joinToken=joinToken).first()

        if comJoinToken == None:
            payLoad = {
                'message': 'incorrect-join-token'
            }
            return make_response(jsonify(payLoad), 400)

        elif py_boolean(comJoinToken.joinTokenValid) == False:
            payLoad = {
                'message': 'community-joining-is-closed'
            }
            return make_response(jsonify(payLoad), 403)


        communityId = comJoinToken.communityId

        # user me join same community more than once
        try:
            userInCommunity = CommunityMembers.query.filter(CommunityMembers.userId==userId, CommunityMembers.communityId==communityId).first()
            if userInCommunity != None:
                payLoad = {
                    'message': 'you-are-already-in-this-community'
                }
                return make_response(jsonify(payLoad), 400)
                
        except Exception as e:
            print(str(e))
        

        communityMember = CommunityMembers(userId, communityId)
        db.session.add(communityMember)
        db.session.commit()

        payLoad = {
            'userId': userId,
            'communityId': communityId,
            'message': 'community-successfully-joined'
        }

        return make_response(jsonify(payLoad), 200)
    
    return make_response(jsonify(payLoad), 400)


# Set Event
@general_bp.route('/event/set', methods=['POST'])
def set_event():

    """
    Endpoint to set an Event and put on hold if-
    start now is false

    Required: Admin
    return: event hold status | auth fail
    """

    token = request.headers.get('Authorization')

    event_name_ = request.json.get('event_name')
    event_description_ = request.json.get('event_description')

    ending_time_delta_ = request.json.get('ending_time_delta')
    location_range_ = request.json.get('location_range')
    communityId_ = request.json.get('communityId') # How to get this is a creative part

    latitude_ = request.json.get('latitude')
    longitude_ = request.json.get('longitude')

    broadcast_choice_ = request.json.get('broadcast_choice')
    start_event_ = request.json.get('start_event')  # New add_on
    

    if find_missing(token, event_name_, ending_time_delta_, location_range_, 
        latitude_, longitude_, broadcast_choice_, start_event_, communityId_):
        payLoad = {
            'message': 'missing-params'
        }
    elif malformed_length(
        {
            token: [16, 1024],
            event_name_: [3, 128],
            event_description_: [0, 2048],
        }
    ):
        payLoad = {
            'message': 'bad-length-params'
        }
    elif malformed_dtc(
        {
            ending_time_delta_: 'i', 
            location_range_: 'i',
            latitude_: 'f',
            longitude_: 'f',
            ending_time_delta_: 'i',
            location_range_: 'i',
            communityId_: 'i'
        }
    ):
        payLoad = {
            'message': 'bad-datatype'
        }
    elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
        payLoad = {
            'message': 'fresh-login-required'
        }
    
    elif isBlackListed(token):
        payLoad = {
            'message': 'login-required'
        }

    else:

        latitude_ = float(latitude_)
        longitude_ = float(longitude_)
        ending_time_delta_ = int(ending_time_delta_)
        location_range_ = int(location_range_)
        communityId_ = int(communityId_)

        if py_boolean(broadcast_choice_):
            broadcast_choice_ = 1
        else:
            broadcast_choice_ = 0

        if py_boolean(start_event_):
            start_event_ = 1
        else:
            start_event_ = 0
      

        # check if user has that community registered under him/her and is Authorized

        userId = decode_auth_token(token)
        userEmail_ = Users.query.get(userId).userEmail
        communityRegistered = [x.communityId for x in Communities.query.filter_by(userId=userId).all()]

        if communityId_ not in communityRegistered:
            payLoad = {
                'message': 'You-Are-Not-Registered-as-Community-Head-for-this-company'
            }
            return make_response(jsonify(payLoad), 403)

        # Getting OTP
        otp_ = random_otp()
        if otp_ == 'Fail':
            payLoad = {
                'message': 'OTP-Generation-Failed'
            }
            return make_response(jsonify(payLoad), 500)

        creation_date_ = datetime.datetime.now()
        if start_event_ == 1:

            new_event = Events(creation_date= creation_date_, userEmail=userEmail_, \
                    otp=otp_, event_name=event_name_, event_description=event_description_, \
                    ending_time_delta=ending_time_delta_, location_range=location_range_, \
                    latitude=latitude_, longitude=longitude_, broadcast_choice=broadcast_choice_, \
                    communityId=communityId_)

            db.session.add(new_event)
            db.session.commit()

            payLoad = {
                'OTP': otp_,
                'EventName': event_name_,
                'EndingInMin': ending_time_delta_,
                'CommunityId': communityId_,
                'EventStarted': True,
                'BroadcastChoice': broadcast_choice_,
                'LocationValidInMeters': location_range_
            }
            return make_response(payLoad, 200) # Object of type Response is not JSON serializable
        
        else: # else add it in hold

            new_hold = HoldedEvents(creation_date= creation_date_, userEmail=userEmail_, \
                    otp=otp_, event_name=event_name_, event_description=event_description_, \
                    ending_time_delta=ending_time_delta_, location_range=location_range_, \
                    broadcast_choice=broadcast_choice_, communityId=communityId_)
            db.session.add(new_hold)
            db.session.commit()

            payLoad = {
                'OTP': otp_,
                'EventName': event_name_,
                'EndingInMin': ending_time_delta_,
                'CommunityId': communityId_,
                'EventStarted': False,
                'BroadcastChoice': broadcast_choice_,
                'LocationValidInMeters': location_range_
            }
            return make_response(payLoad, 201) # Object of type Response is not JSON serializable
    
    return make_response(payLoad, 400)


# Holded Events View
@general_bp.route('/event/holded', methods=['POST'])
def view_holded():
    """
    Shows all holded events from here start event can be clicked
    and then otp is passed dynamically to the start event
    """

    token = request.headers.get('Authorization')
    communityId_ = request.json.get('communityId') # Has to be passed

    if find_missing(token, communityId_):
        payLoad = {
            'message': 'missing-params'
        }
    
    elif malformed_length(
        {
            token: [16, 1024], # 22 exactly
        }
    ):
        payLoad = {
            'message': 'bad-length-params'
        }
    
    elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
        payLoad = {
            'message': 'fresh-login-required'
        }
    
    elif isBlackListed(token):
        payLoad = {
            'message': 'login-required'
        }

    else:
    
        userId = decode_auth_token(token)
        userEmail_ = Users.query.get(userId).userEmail
        holdedEvents = HoldedEvents.query.filter(HoldedEvents.userEmail==userEmail_, HoldedEvents.communityId == communityId_).all()

        holdedEventsArray = []

        for event in holdedEvents:
            adder = {
                "holdId": event.holdId,
                "CreationDate": event.creation_date, #--todo-- improve the format
                "OTP":event.otp,
                "EventName": event.event_name,
                "EventDescription": event.event_description,
                "LocationValidInMeters": event.location_range,
                "EndingInMin": event.ending_time_delta,
                "BroadcastChoice": event.broadcast_choice,
                "CommunityId": event.communityId
            }
            holdedEventsArray.append(adder)
        payLoad = holdedEventsArray

        return make_response(jsonify(payLoad), 200)

    return make_response(jsonify(payLoad), 400)


# Holded Event
@general_bp.route('/event/start/<otpNumber>', methods=['POST'])
def start_event(otpNumber):
    """
    This will start the event those are present in holded events
    Post Req: latitude, longitude, authToken
    """
    
    token = request.headers.get('Authorization')
    latitude_ = request.json.get('latitude')
    longitude_ = request.json.get('longitude')

    holdedQuery = HoldedEvents.query.filter_by(otp=otpNumber).first()
    otp_check = holdedQuery
    

    if otp_check in [None, '']: #does not exsists
        payLoad = {
            'Status': 'Fail',
            'Reason': 'no-such-holded-event'
        }
    elif find_missing(token, latitude_, longitude_,):
        payLoad = {
            'message': 'missing-params',
            'header': ['Authorization', ],
            'body': ['latitude', 'longitude']
        }
    elif malformed_length(
        {
            token: [16, 1024],
        }
    ):
        payLoad = {
            'message': 'bad-length-params'
        }
    elif malformed_dtc(
        {
            latitude_: 'f',
            longitude_: 'f'
        }
    ):
        payLoad = {
            'message': 'bad-datatype'
        }
    elif decode_auth_token(token) in ['Signature expired. Please log in again.', 'Invalid token. Please log in again.']:
        payLoad = {
            'message': 'fresh-login-required'
        }
    
    elif isBlackListed(token):
        payLoad = {
            'message': 'login-required'
        }

    else:

        latitude_ = float(latitude_)
        longitude_ = float(longitude_)

        communityId_ = holdedQuery.communityId

        # check if user has that community registered under him/her and is Authorized

        userId = decode_auth_token(token)
        userEmail_ = Users.query.get(userId).userEmail
        communityRegistered = [x.communityId for x in Communities.query.filter_by(userId=userId).all()]

        if communityId_ not in communityRegistered:
            payLoad = {
                'message': 'You-Are-Not-Registered-as-Community-Head-for-this-company'
            }
            return make_response(jsonify(payLoad), 403)

        creation_date_ = otp_check.creation_date
        userEmail_ = otp_check.userEmail
        otp_ = otpNumber
        event_name_ = otp_check.event_name
        event_description_ = otp_check.event_description
        ending_time_delta_ = otp_check.ending_time_delta
        location_range_ = otp_check.location_range
        broadcast_choice_ = otp_check.broadcast_choice
        communityId_ = otp_check.communityId

        new_event = Events(creation_date= creation_date_, userEmail=userEmail_, \
                otp=otp_, event_name=event_name_, event_description=event_description_, \
                ending_time_delta=ending_time_delta_, location_range=location_range_, \
                latitude=latitude_, longitude=longitude_, broadcast_choice=broadcast_choice_, \
                communityId=communityId_)

        db.session.add(new_event)

        HoldedEvents.query.filter_by(otp=otpNumber).delete()

        db.session.commit()

        payLoad = {
            'OTP': otp_,
            'EventName': event_name_,
            'EndingInMin': ending_time_delta_,
            'CommunityId': communityId_,
            'EventStarted': True,
            'BroadcastChoice': broadcast_choice_,
            'LocationValidInMeters': location_range_
        }
        return make_response(payLoad, 200)
    
    return make_response(payLoad, 400)

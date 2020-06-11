from flask import ( 
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    make_response 
    )

general_bp = Blueprint('general_bp', 
    __name__)

from app import db
from dryFunctions import *
from models import (
    Users,
    Communities,
    CommunityMembers
)


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
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

        comJoinToken = Communities.query.filter(Communities.userId==userId, Communities.communityName==communityName).first().joinToken

        payLoad = {
            'userId': userId,
            'communityName': communityName,
            'communityDescription': communityDescription,
            'comJoinToken': comJoinToken,
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


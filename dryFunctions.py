"""
Funtions to follow DRY
"""

# Imports
import math
import jwt
import datetime
import hashlib
import requests
import json

from app import app

import re
import smtplib
import dns.resolver

from models import Users, BlackListedTokens

# Distance Calculator
def distance(origin, destination):

    """
    Find distance between two given coordinates
    :param arg1: ['latitudeA', 'longitudeA']
    :param arg2: ['latitudeB', 'longitudeB']
    :type arg1: list
    :type arg2: list
    :return: distance in meters, round by 2
    :type: Integer
    """

    # Conversions:
    # d_km = d_km/1000
    # d_miles = d_km*0.621371

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = abs(radius * c)

    return round(d*1000, 2)  # in meters


# JWT ENCODE/DECODE FUNCTIONS

def encode_auth_token(user_id, remember_me=False, valid_minutes=None):

    """
    Generates the Auth Token
    :param arg1: User ID
    :param arg2: Increase Token Validity
    :type arg1: Integer
    :type arg2: Boolean
    :return: JWT Token
    :rtype: string
    """

    if remember_me:
        days_valid = 60
    else:
        days_valid = 1
    
    if valid_minutes:
        valid_for = datetime.timedelta(minutes=valid_minutes)
    else:
        valid_for = datetime.timedelta(days=days_valid, seconds=5)

    

    try:
        payload = {
            'exp': datetime.datetime.utcnow() + valid_for, # valid upto
            'iat': datetime.datetime.utcnow(), # created on
            'sub': user_id
        }
        return jwt.encode(
            payload,
            'secret', #app.config.get('SECRET_KEY'), #--todo--
            algorithm='HS256'
        )
    except Exception as e: # Make sure secret key is set in environment, else NoneType ValueError
        return e


def decode_auth_token(auth_token='auth_header'):

    """
    Decodes the auth token
    :param arg1: JWT Token
    :type arg1: String
    :return: User ID | Exception
    :rtype: Integer |  String
    """
    try:
        payload = jwt.decode(auth_token, 'secret')#app.config.get('SECRET_KEY')) #--todo--
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.' # Missing SECRET_KEY will also throw this error


def find_missing(*args):
    """
    If True then missing value is there
    """


    for value in args:
        if value == None or value == '':
            return True
    else:
        return False


def is_email_valid(email_):
    """
    This takes sometime as it's verifying not only syntax
    but if email exsists in actual or not
    Can use a Broker like redis here but then alse we have
    to wait for verification. Redis won't help here.
    """

    try:
        # Address used for SMTP MAIL FROM command  
        fromAddress = 'corn@bt.com'

        # Simple Regex for syntax checking
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

        # Email address to verify
        inputAddress = email_
        addressToVerify = str(inputAddress)

        # Syntax check
        match = re.match(regex, addressToVerify)
        if match == None:
            return False

        # Get domain for DNS lookup
        splitAddress = addressToVerify.split('@')
        domain = str(splitAddress[1])

        # MX record lookup
        records = dns.resolver.query(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)


        # SMTP lib setup (use debug level for full output)
        server = smtplib.SMTP()
        server.set_debuglevel(0)

        # SMTP Conversation
        server.connect(mxRecord)
        server.helo(server.local_hostname) ### server.local_hostname(Get local server hostname)
        server.mail(fromAddress)
        code, message = server.rcpt(str(addressToVerify))
        server.quit()


        # Assume SMTP response 250 is success
        if code == 250:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False


def malformed_length(arg1):
    """
    If True then length is malformed
    Pass a Dictionary Object, key is the string
    and Value is the tuple with min, max length inclusive
    """
    for key, value in arg1.items():
        if len(key) < value[0] or len(key) > value[1]:
            return True
    return False


def hex_hash(arg1):
    """
    return Hash of type str 
    encoding: hex
    algorithm: md5
    length: 32
    """

    hash = hashlib.md5()
    hash.update(arg1.encode())
    return hash.hexdigest()

def user_exist(email):
    """
    True: exists
    False: not exists
    """

    user_object = Users.query.filter_by(userEmail=email).first()
    if user_object:
        return True
    return False


def user_detail(email=None):

    user_object = Users.query.filter_by(userEmail=email).first()
    if user_object:
        user_json = {
            'userId': user_object.userId,
            'userName': user_object.userName,
            'userEmail': user_object.userEmail,
            'userPassword': user_object.userPassword
        }
        return user_json
    return {}


def py_boolean(arg1):
    if arg1 in ['True', 'true', True, 1]:
        return True
    return False


def send_email(url, email_header, email_body): # for sendgrid

    requests.post(url, data=json.dumps(email_body), headers=email_header)


def isBlackListed(token):
    """
    True: Don't allow Access
    False: Allow Access
    """

    if token:
        token_query = BlackListedTokens.query.filter_by(token=token).first()
        if token_query != None:
            return True
        else:
            return False
    return True
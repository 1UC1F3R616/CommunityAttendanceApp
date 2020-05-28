from app import db
import secrets


def generateJoinToken():

    return secrets.token_urlsafe(16)


class Users(db.Model):

    __tablename__ = 'users'

    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64), nullable=False)
    userEmail = db.Column(db.String(64), unique=True, nullable=False)
    userPassword = db.Column(db.String(64), nullable=False)

    def __init__(self, username, email, password):
        self.userName = username
        self.userEmail = email
        self.userPassword = password

    def __repr__(self):
        #return '<Users %r>' % self.userId
        return '<users ID:{} NAME:{} EMAIL:{}>'.format(self.userId, self.userName, self.userEmail)


class Communities(db.Model):

    __tablename__ = 'communities'

    communityId = db.Column(db.Integer, primary_key=True)
    CommunityName = db.Column(db.String(64), nullable=False)
    communityDescription = db.Column(db.String(64))
    joinToken = db.Column(db.String(16), default=generateJoinToken)
    joinTokenValid = db.Column(db.Boolean, default=1) # This is not added in RelationalModel #--todo--

    def __init__(self, name, description):
        self.CommunityName = name
        self.communityDescription = description

    def __repr__(self):
        return '<communities ID:{} NAME:{} DESCRIPTION:{}>'.format(self.communityId, self.CommunityName, self.communityDescription)


class CommunityMembers(db.Model):
    """
    when a user joins a community then their id and community id are tracked here
    """

    __tablename__ = 'communityMembers'

    id = db.Column(db.Integer, primary_key=True)
    communityId = db.Column(db.Integer)
    userId = db.Column(db.Integer)

    def __repr__(self):
        return '<communityMembers ID:{} COMMUNITY_ID:{} USER_ID:{}>'.format(self.id, self.communityId, self.userId)


class Events(db.Model):

    __tablename__ = 'events'

    eventId = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime)
    userEmail = db.Column(db.String(64))

    # These are the required fields in post request
    otp = db.Column(db.String(6), nullable=False, unique=True) # Filled Automatically
    event_name = db.Column(db.String(128))
    event_description = db.Column(db.String(2048), nullable=True)
    ending_time_delta = db.Column(db.Integer) #Treated in Minutes
    location_range = db.Column(db.Integer)  # Treated in meters
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    broadcast_choice = db.Column(db.Boolean)  # an option to allow or disallow broadcast to users
    communityId = db.Column(db.Integer)

    def __init__(self, creation_date, userEmail, otp, event_name, event_description, ending_time_delta, location_range, \
        latitude, longitude, broadcast_choice, communityId):
        self.creation_date = creation_date
        self.userEmail = userEmail
        self.otp = otp
        self.event_name = event_name
        self.event_description = event_description
        self.ending_time_delta = ending_time_delta
        self.location_range = location_range
        self.latitude = latitude
        self.longitude = longitude
        self.broadcast_choice = broadcast_choice
        self.communityId = communityId

    def __repr__(self):
        return '<events ID:{} NAME:{} DESCRIPTION:{} CREATOR_EMAIL:{} OTP:{}>'.format(self.eventId, self.event_name, \
            self.event_description, self.userEmail, self.otp
            )


class HoldedEvents(db.Model):
    
    __tablename__ = 'holdedEvents'

    holdId = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime)
    userEmail = db.Column(db.String(64))

    # These are the required fields in post request
    otp = db.Column(db.String(6), nullable=False, unique=True)
    event_name = db.Column(db.String(128))
    event_description = db.Column(db.String(2048), nullable=True)
    ending_time_delta = db.Column(db.Integer) #Treated in Minutes
    location_range = db.Column(db.Integer)  # Treated in meters
    broadcast_choice = db.Column(db.Boolean)  # an option to allow or disallow broadcast to users
    communityId = db.Column(db.Integer)

    def __init__(self, creation_date, userEmail, otp, event_name, event_description, ending_time_delta, location_range, \
        latitude, longitude, broadcast_choice, communityId):
        self.creation_date = creation_date
        self.userEmail = userEmail
        self.otp = otp
        self.event_name = event_name
        self.event_description = event_description
        self.ending_time_delta = ending_time_delta
        self.location_range = location_range
        self.broadcast_choice = broadcast_choice
        self.communityId = communityId

    def __repr__(self):
        return '<holdedEvents ID:{} NAME:{} DESCRIPTION:{} CREATOR_EMAIL:{} OTP:{}>'.format(self.eventId, self.event_name, \
            self.event_description, self.userEmail, self.otp
            )


class Attendances(db.Model):

    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    eventId = db.Column(db.Integer, nullable=False)
    communityId = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

    def __init__(self, userId, eventId, communityId, datetime, status):
        self.userId = userId
        self.eventId = eventId
        self.communityId = communityId
        self.datetime = datetime
        self.status = status

    def __repr__(self):
        #return '<Users %r>' % self.userId
        return '<attendances ID:{} USER_ID:{} EVENT:{} COMMUNITY:{} STATUS:{} DATETIME:{}>'.format(self.id, self.userId, \
             self.eventId, self.communityId, str(self.status), str(self.datetime))


class BlackListedTokens(db.Model):

    __tablename__ = 'blackListedTokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128))

    def __init__(self, token):
        self.token = token
    
    def __repr__(self):
        return '<blackListedTokens ID:{} TOKEN:{}>'.format(self.id, self.token)


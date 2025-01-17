from app import db
import secrets


def generateJoinToken():

    return secrets.token_urlsafe(16) # model to accept 32 | 22 is enough


class Users(db.Model):

    __tablename__ = 'users'

    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(64), nullable=False)
    userEmail = db.Column(db.String(64), unique=True, nullable=False)
    userPassword = db.Column(db.String(64), nullable=False)
    communities = db.relationship("Communities", cascade="all,delete", backref="users")

    members = db.relationship("CommunityMembers", cascade="all,delete", backref="users") # fk with CommunityMembers table

    def __init__(self, username, email, password):
        self.userName = username
        self.userEmail = email
        self.userPassword = password

    def __repr__(self):
        return '<users ID:{} NAME:{} EMAIL:{}>'.format(self.userId, self.userName, self.userEmail)


class Communities(db.Model):
    """
    FK Relation: parent is Users

    Admin is someone who creates the community
    One Insta Account Cann't have more than 1 Password or Email (2 users without pass sharing), 
    Community is like an account
    """

    __tablename__ = 'communities'

    communityId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId', ondelete='CASCADE'))

    members = db.relationship("CommunityMembers", cascade="all,delete", backref="communities") # fk with CommunityMembers table

    communityName = db.Column(db.String(64), nullable=False)
    communityDescription = db.Column(db.String(256))
    joinToken = db.Column(db.String(32), default=generateJoinToken)
    joinTokenValid = db.Column(db.Boolean, default=1) # This is not added in RelationalModel #--todo--

    def __init__(self, userId, name, description):
        self.userId = userId
        self.communityName = name
        self.communityDescription = description

    def __repr__(self):
        return '<communities ID:{} NAME:{} DESCRIPTION:{} ADMIN_ID:{}>'.format(self.communityId, self.communityName, self.communityDescription, self.userId)


class CommunityMembers(db.Model):
    """
    when a user joins a community then their id and community id are tracked here
    User is Deleted => Delete Cascade on that user id here
    Community is Deleted => Delete Cascade on that community id here
    FK Relation: parent is Users
    FK Relation: parent is Communities
    """

    __tablename__ = 'communityMembers'

    id = db.Column(db.Integer, primary_key=True)
    # communityId = db.Column(db.Integer)
    # userId = db.Column(db.Integer)

    userId = db.Column(db.Integer, db.ForeignKey('users.userId', ondelete='CASCADE'))
    communityId = db.Column(db.Integer, db.ForeignKey('communities.communityId', ondelete='CASCADE'))

    def __init__(self, userId, communityId):
        self.userId = userId
        self.communityId = communityId

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
        broadcast_choice, communityId):
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
    token = db.Column(db.String(1024))

    def __init__(self, token):
        self.token = token
    
    def __repr__(self):
        return '<blackListedTokens ID:{} TOKEN:{}>'.format(self.id, self.token)


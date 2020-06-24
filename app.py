import sys
sys.path.insert(0, '.')
from flask import (Flask,
    render_template)
from flask_sqlalchemy import SQLAlchemy
from os import getcwd, environ
from os.path import join

from flask_cors import CORS, cross_origin
from flask_socketio import (
    SocketIO,
    send, 
    emit, 
    join_room, 
    leave_room,)

app = Flask(__name__)
app.config['DEBUG']=True #--todo--

CORS(app, support_credentials=True)


PATH_TO_CONFIG = join(getcwd(), 'config.py')
app.config.from_pyfile(PATH_TO_CONFIG)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PG = environ.get("DATABASE_URL")
PATH_TO_LOCAL_DB = join(getcwd(), 'db.sqlite')
if PG is None or PG=="":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        PATH_TO_LOCAL_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = PG

db = SQLAlchemy(app)


@app.errorhandler(404)
def error404(error):
    return render_template('404page.html')


# Importing BluePrint
from auth import auth_bp
from general import general_bp

# Registring BluePrint
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(general_bp, url_prefix='')

# Heroku Port Configure
PORT = environ.get("PORT")
socketio = SocketIO(app, cors_allowed_origins='*')
from sockets import *

if __name__ == "__main__":
    
    #app.run()
    print('yes fine now!')
    socketio.run(app)#, host='127.0.0.1', port=PORT)


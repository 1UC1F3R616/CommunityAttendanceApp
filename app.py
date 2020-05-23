import sys
sys.path.insert(0, '.')
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getcwd, environ
from os.path import join

app = Flask(__name__)
app.config['DEBUG']=True #--todo--

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


# Importing BluePrint
from auth import auth_bp
from general import general_bp

# Registring BluePrint
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(general_bp, url_prefix='')

if __name__ == "__main__":
    
    app.run()



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
from models import Users

# HomePage for Everyone
@general_bp.route('/', methods=['GET'])
def testing_route():
    return "Working!!"
    


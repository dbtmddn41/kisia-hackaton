from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError
from backend.models import Parter, User
from backend import db
import json

bp = Blueprint('fishing', __name__, url_prefix='/fishing')

@bp.route('/test', methods=['GET'])
def test():
    return jsonify(message='test'), 200

@bp.route('/add_partner', methods=['POST'])
@jwt_required()
def add_partner():
    user_id = get_jwt_identity()
    # data = request.get_json()
    data = json.loads(request.form.get('data'))
    partner_name = data.get('partner_name')
    partner_email = data.get('partner_email')
    if not validate_email_address(partner_email):
        return jsonify({"message": "email invalid"}), 400
        
    past_message = request.files['file'].read().decode('utf-8')
    # past_message = preprocess_partner_msg(past_message)
    # messge_embedding = get_message_embedding(past_message)
    partner = Parter(user_id=user_id, partner_name=partner_name, partner_email=partner_email, partner_past_message=past_message)
    db.session.add(partner)
    db.session.commit()
    return jsonify({"message": "Partner added successfully"}), 201

@bp.route('/determine_fishing', methods=['POST'])
@jwt_required()
def determine_fishing():
    user_id = get_jwt_identity()
    data = request.get_json()
    msg = data.get('msg')
    speech_similarity = get_speech_similarity(msg, user_id)
    content_score = get_content_score(msg)
    if content_score > 0.5:
        similar_fishing_msg = get_similar_fishing_msg(msg)
    else:
        similar_fishing_msg = None
    return jsonify({"speech_similarity": speech_similarity,
                    "content_score": content_score,
                    "similar_fishing_msg": similar_fishing_msg,
                    }), 201
        
    
    
def get_speech_similarity(msg, user_id):
    user = User.query.get_or_404(user_id)
    return 0.8      #임시값

def get_content_score(msg):
    return 0.3

def get_similar_fishing_msg(msg):
    return "선배 탕후루 사먹게 3000만원만 주세요"

def validate_email_address(email):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        return None
from flask import Blueprint, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from backend.models import User
from backend import db
import json
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user_name = data.get('user_name')
    password = data.get('password')
    
    if User.query.filter_by(user_name=user_name).first():
        return jsonify({"message": "user_name already exists"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(user_name=user_name, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # data = json.loads(request.form.get('data'))
    user_name = data.get('user_name')
    password = data.get('password')
    
    user = User.query.filter_by(user_name=user_name).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.user_id)
        return jsonify(access_token=access_token), 200
        # session['logged_in'] = True
        # session['user_id'] = user.user_id
        # return jsonify({"message": "login success"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401
    
# @bp.route('/protected', methods=['GET'])
# @jwt_required()
# def protected():
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200


@bp.route('/test', methods=['GET'])
def test():
    return jsonify(message='test'), 200

# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(*args, **kwargs):
#         if ('logged_in' not in session) or not session['logged_in']:
#             return jsonify({"message": "Not logged in"}), 401
#         return view(*args, **kwargs)
#     return wrapped_view

@bp.route('/protected', methods=['GET'])
# @login_required
@jwt_required()
def protected():
    # current_user = session['user_id']
    user_id = get_jwt_identity()
    return jsonify(logged_in_as=user_id), 200
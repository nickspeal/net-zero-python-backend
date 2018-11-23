from flask import Blueprint, abort, request, Response, jsonify
from app import app, models, db
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')


@user_bp.route('/signup', methods=['POST'])
def signup():
    try:
        user = models.User(
            username=request.form.get('username'),
        )
        # Insert the user in the database
        db.session.add(user)
        db.session.commit()
        return 'Created', 201
    except IntegrityError:
        return 'Username Taken', 400

@user_bp.route('/login', methods=['POST'])
def login():
    models.User.query.filter_by(username=request.form.get('username')).first_or_404()
    return 'OK', 200

@user_bp.route('/<username>', methods=['GET'])
def get_user(username):
    user = models.User.query.filter_by(username=username).first_or_404()
    campaigns = [{ 'id': c.id, 'name':c.name } for c in user.campaigns]
    return jsonify({ 'username': user.username, 'campaigns': campaigns })

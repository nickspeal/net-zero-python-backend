from flask import Blueprint, abort, request, Response, jsonify
from app import app, models, db
from sqlalchemy.exc import IntegrityError

campaign_bp = Blueprint('campaign_bp', __name__, url_prefix='/api/campaign')


@campaign_bp.route('/create', methods=['POST'])
def create():
    username = request.form.get('username')
    name = request.form.get('name')
    print("Creating campaign with name ", name)
    try:
        campaign = models.Campaign(
            name=name,
        )
        # Associate the user with the campaign
        user = models.User.query.filter_by(username=username).first_or_404()
        campaign.users.append(user)
        
        db.session.add(campaign)
        db.session.commit()
        return 'Created', 201
    except IntegrityError:
        return 'Name Taken', 400

@campaign_bp.route('/<id>', methods=['GET'])
def get(id):
    
    campaign = models.Campaign.query.filter_by(id=id).first_or_404()
    campaign_dict = {
        'id': campaign.id,
        'name': campaign.name,
        'offsets_available': campaign.offsets_available,
        'users': [u.username for u in campaign.users],
        'vehicles': [v.name for v in campaign.vehicles]
    }

    return jsonify(campaign_dict)

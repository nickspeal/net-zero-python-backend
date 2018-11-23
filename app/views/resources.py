from flask import Blueprint, abort, request, Response, jsonify
from app import app, models, db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

DATE_FORMAT_ISO8061 = '%Y%m%dT%H%M%SZ'  # YYYYMMDDThhmmssZ ISO 8061

resources_bp = Blueprint('resources_bp', __name__, url_prefix='/api/resource')

@resources_bp.route('/create', methods=['POST'])
def create():
    name = request.form.get('name')
    print("Creating vehicle with name ", name)
    mpg = float(request.form.get('mpg'))
    campaign_id = request.form.get('campaign')
    
    # Convert MPG to L/100KM
    GAL_PER_L = 0.2641729
    KM_PER_MILE = 1.609344
    fuel_l_per_100km = 100 / (mpg * GAL_PER_L * KM_PER_MILE )

    vehicle = models.Vehicle(
        name=name,
        fuel_l_per_100km=fuel_l_per_100km
    )
    # Associate the vehicle with the campaign
    campaign = models.Campaign.query.filter_by(id=campaign_id).first_or_404()
    vehicle.campaigns.append(campaign)

    db.session.add(vehicle)
    db.session.commit()
    return 'Created', 201

@resources_bp.route('/<id>', methods=['GET'])
def get(id):
    vehicle = models.Vehicle.query.filter_by(id=id).first_or_404()
    history = models.ResourceMeasurement.query.filter_by(resource=vehicle.id)
    vehicle_dict = {
        'id': vehicle.id,
        'name': vehicle.name,
        'carbon_per_unit': vehicle.get_carbon_per_unit(),
        'units': vehicle.units,
        'notes': vehicle.notes,
        'fuel_l_per_100km': vehicle.fuel_l_per_100km,
        'carbon_to_manufacture': vehicle.carbon_to_manufacture,
        'expected_life_km': vehicle.expected_life_km,
        'campaigns': [{ 'id': c.id, 'name':c.name } for c in vehicle.campaigns],
        'history': [{ 'date': datetime.strftime(h.date, DATE_FORMAT_ISO8061), 'value': h.value } for h in history]
    }

    return jsonify(vehicle_dict)

@resources_bp.route('/<id>/history', methods=['POST'])
def append_to_history(id):
    date = datetime.strptime(request.form.get('date'), DATE_FORMAT_ISO8061)
    value = request.form.get('value')
    history_item = models.ResourceMeasurement(
        date=date,
        value=value,
        resource=id,
    )
    db.session.add(history_item)
    db.session.commit()
    return 'Created', 201

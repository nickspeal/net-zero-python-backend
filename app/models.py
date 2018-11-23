from app import db

# Junction Tables for many-to-many relationships
campaign_users = db.Table('campaign_users',
    db.Column('campaign', db.Integer, db.ForeignKey('campaigns.id'), primary_key=True),
    db.Column('user', db.Integer, db.ForeignKey('users.username'), primary_key=True),
)

campaign_vehicles = db.Table('campaign_vehicles',
    db.Column('campaign', db.Integer, db.ForeignKey('campaigns.id'), primary_key=True),
    db.Column('vehicle', db.Integer, db.ForeignKey('vehicles.id'), primary_key=True),
)

class Campaign(db.Model):
    ''' A Campaign is a context in which to tally a carbon footprint total.
        For example, a personal total, or an activity shared across multiple people
    '''
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    offsets_available = db.Column(db.Float, nullable=False, default=0.0)

    users = db.relationship('User', secondary=campaign_users, lazy='subquery', backref=db.backref('campaigns', lazy=True))
    vehicles = db.relationship('Vehicle', secondary=campaign_vehicles, lazy='subquery', backref=db.backref('campaigns', lazy=True))
    # Other resources
    # consumptions = TODO m2m relationship to consumptions
    # offsets = db.relationship('Offset', backref='campaign', lazy=True)

    def __repr__(self):
        return '<Campaign {}>'.format(self.name)


class User(db.Model):
    ''' A person with an account
    '''
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    # campaigns attribute is backreferenced

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Vehicle(db.Model):
    ''' A Vehicle is a type of Resource
        Resources have an increasing counter (i.e. odometer, gas meter) that can be snapshotted over time to measure usage
        Usage can be converted into CO2 emitted according with some linear factors
    '''
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    units = db.Column(db.String, nullable=False, default='km') # Should be km for all vehicles for now. This column exists for extensibility to other resources.
    notes = db.Column(db.String, nullable=True)
    fuel_l_per_100km = db.Column(db.Float, nullable=False, default=10.6)  # Default average car 22 mpg
    carbon_to_manufacture = db.Column(db.Float, nullable=False, default=10000)  # Default wild estimate based on quick search
    expected_life_km = db.Column(db.Float, nullable=False, default=321868)  # Default based on guess of 200k miles
    
    def get_carbon_per_unit(self):
        ''' Calculate the CO2 emission per mile of driving
        as the sum of contributions of burning gas and deprecating a vehicle
        that emitted lots of carbon during manufacure

        Units of kg CO2 per km
        '''
        
        GAL_PER_L = 0.2641729
        CARBON_PER_LITRE = 8.9 * GAL_PER_L # 8.9 kg CO2 per gallon of gas: https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle-0
        gas_contribution = ( self.fuel_l_per_100km / 100.0 ) * CARBON_PER_LITRE
        deprecation_contribution = self.carbon_to_manufacture / self.expected_life_km
        return gas_contribution + deprecation_contribution

    def __repr__(self):
        return '<Vehicle {}>'.format(self.id)



class ResourceMeasurement(db.Model):
    ''' This table stores the timeseries of all measurements for all resources (i.e. car odometer readings over time)
    '''
    __tablename__ = 'resource_measurements'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)
    resource = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)


## TODO FUTURE - Add additional models
# The following models are stubbed out, but likely don't work yet
# They're needed to complete a larger carbon footprint picture for a Campaign
# Add new consumptions to track each contribution to your carbon footprint (as discrete events)
# They can be of different types, (in an enum table) mostly just for future potential categorization features and stats across users
# Add Offsets each time you buy an offset and apply it to a campaign

# class Consumption(db.Model):
#     ''' A Consumption is a thing that has a carbon footprint. I.e. a flight, or a cheeseburger, or a bonfire '''
#     __tablename__ = 'consumptions'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     date = db.Column(db.DateTime, nullable=False)

#     category = # TODO foreign key
#     quantity = db.Column(db.Float, nullable=False)
#     units = db.Column(db.String, nullable=False)
#     carbon_per_unit = db.Column(db.Float, nullable=False)
#     # Footprint off the consumption can be derived from the product of quantity and carbon_per_unity

#     def __repr__(self):
#         return '<Consumption {}, {}>'.format(self.name, self.id)

# class ConsumptionCategories(db.Model):
#     ''' Enumeration of categories that Consumptions can fall into. One category to many Consumptions.'''
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

#     def __repr__(self):
#         return '<Consumption Category {}, {}>'.format(self.name, self.id)

# class Offset(db.Model):
#     __tablename__ = 'offsets'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     date = db.Column(db.DateTime, nullable=False)

#     price_usd = db.Column(db.Float, nullable=True)
#     carbon_offset_quantity = db.Column(db.Float, nullable=False)
#     reference = db.Column(db.String)

#     # Foreign key to Campaigns. Many offsets to one campaign.
#     campaign = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)

#     def __repr__(self):
#         return '<Offset #{}: {} ({}) kg CO2>'.format(self.id, self.name, self.carbon_offset_quantity)









# ======================================================
# TODO FUTURE
# Potentially I might want to abstract the Vehicle Resource into a Resource base class that Vehicles and Utilities can extend

# # Abstract Class
# class Resource(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     carbon_per_unit = db.Column(db.Float, nullable=False)
#     units = db.Column(db.String, nullable=False)
#     notes = db.Column(db.String, nullable=True)

#     def __repr__(self):
#         return '<Resource {}>'.format(self.id)

# class Vehicle(Resource):
#     __tablename__ = 'vehicles'
#     fuel_l_per_100km = db.Column(db.Float, nullable=False)
#     carbon_to_manufacture = db.Column(db.Float, nullable=False)
#     expected_life_km = db.Column(db.Float, nullable=False)

#     units = 'miles' # Somehow set this.

#     def __repr__(self):
#         return '<Vehicle {}>'.format(self.id)

# class Utility(Resource):
#     __tablename__ = 'electric'
#     username = db.Column(db.String, primary_key=True)

#     def __repr__(self):
#         return '<User {}>'.format(self.id)
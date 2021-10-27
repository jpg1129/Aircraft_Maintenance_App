from . import db, login_manager
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from flask_login import UserMixin
import datetime
from sqlalchemy.sql import text
from sqlalchemy import Table, MetaData
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model, Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    password_hash = db.Column(db.String(128))
    squadron_id = db.Column(db.Integer, db.ForeignKey('squadron.id'))
    type = db.Column(db.String(50))


    __mapper_args__ = {
        'polymorphic_identity' : 'user',
        'polymorphic_on': type
    }

    def what_type(self):
        return self.type


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return '< User %r>' % self.username


class Mechanic(User):
    __tablename__ = 'mechanic'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(80))
    __mapper_args__= {'polymorphic_identity': 'mechanic'}


    '''
    Insert mechanics into the database
    '''
    @staticmethod
    def insert_mechanics():
        users = {
            1: ('jh1234', 'Joe Heins', 'dog', 367),
            2: ('js9015', 'Joe Smith', 'dog', 267),
            3: ('rm1007', 'Roger Moore', 'dog', 169),
            21: ('jb9000', 'Jabari Parker', 'dog', 367),
            22: ('ms9001', 'Marcus Smart', 'dog', 267),
            23: ('ab9007', 'Aaron Baynes', 'dog', 169),
            24: ('jb9234', 'Joe Black', 'dog', 367),
            25: ('jw9015', 'Joe What', 'dog', 367),
            26: ('db9009', 'Devin Booker', 'dog', 169),
            27: ('lz9909', 'Lonzo Ball', 'dog', 367),
            28: ('rs9016', 'Random Smith', 'dog', 267),
            29: ('sm1497', 'Steve Moore', 'dog', 367)

        }
        for i in users:
            mechanic = Mechanic()
            mechanic.id = i
            mechanic.username = users[i][0]
            mechanic.name = users[i][1]
            mechanic.password = users[i][2]
            mechanic.squadron_id = users[i][3]
            db.session.add(mechanic)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return '<Mechanic %r>' % self.name

class Pilot(User):
    __tablename__ = 'pilot'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # t_m_s = db.Column(db.String(15))
    name = db.Column(db.String(80))
    hours = db.Column(db.Integer)
    __mapper_args__={'polymorphic_identity': 'pilot'}


    '''
    Insert pilots into the database
    '''
    @staticmethod
    def insert_pilots():
        pilots = {
            4: ('jb1007','John Barker','dog', 367, 102),
            5: ('ej2015','Earl Johnson', 'dog', 169, 75),
            6: ('jj1111','Jimmy John', 'dog', 267, 101),
            7: ('mj0023', 'Michael Jordan', 'dog', 303, 200),
            8: ('pq1009', 'Parker Quan', 'dog', 367, 50),
            9: ('pp2100', 'Penelope Pawn', 'dog', 169, 125),
            10:('jm0101', 'John Michael', 'dog', 267, 92),
            11:('dw0045', 'David Williams', 'dog', 303, 100),
            12: ('jd1001','John Dobson','dog', 367, 25),
            13: ('mm1002','Micky Mouse', 'dog', 367, 50),
            14: ('jj1003','James Jones', 'dog', 367, 75),
            15: ('lj1004', 'Lebron James', 'dog', 303, 100),
            16: ('sc1005', 'Stephen Curry', 'dog', 303, 150),
            17: ('jb1006', 'Jaylen Brown', 'dog', 303, 125),
            18:('kd1008', 'Kevin Durant', 'dog', 267, 92),
            19:('mm1010', 'Kyrie Irving', 'dog', 303, 70)
        }
        for i in pilots:
            pilot = Pilot()
            pilot.id = i
            pilot.username = pilots[i][0]
            pilot.name = pilots[i][1]
            pilot.password = pilots[i][2]
            pilot.squadron_id = pilots[i][3]
            pilot.hours = pilots[i][4]
            db.session.add(pilot)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Pilot %r' % self.id

#-------------------------------------------------------------------------------
class Administrator(User):
    __tablename__ = 'administrator'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(80))
    __mapper_args__= {'polymorphic_identity': 'administrator'}

    '''
    Insert mechanics into the database
    '''
    @staticmethod
    def insert_admin():
        users = {
            100: ('jpg1234', 'james gomatos', 'dog', 0)
        }
        for i in users:
            admin = Administrator()
            admin.id = i
            admin.username = users[i][0]
            admin.name = users[i][1]
            admin.password = users[i][2]
            admin.squadron_id = users[i][3]
            db.session.add(admin)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Administrator %r>' % self.name

#-------------------------------------------------------------------------------
class Squadron(db.Model):
    __tablename__= 'squadron'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(64))

    '''
    # Static method that inserts squadrons into the database
    squadrons = [('HMLA-367', 'California'), ('HMLA-169', 'California'),
    ('HMLA-267', 'California'), ('HMLA-303','California'),
    ('HMLA-167', 'North Carolina'), ('HMLA-269', 'North Carolina')
    '''
    @staticmethod
    def insert_squadrons():
        squads = {
            367: ('California'),
            169: ('California'),
            267: ('California'),
            303: ('California'),
            167: ('North Carolina'),
            269: ('North Carolina'),
            0: ('')
        }
        for i in squads:
            squadron = Squadron()
            squadron.id = i
            squadron.location=squads[i]
            db.session.add(squadron)
        db.session.commit()

    def __repr__(self):
        return '<Squadron %r>' % self.id


class Aircraft(db.Model):
    __tablename__= 'aircrafts'
    aircraft_id = db.Column(db.Integer, primary_key=True)
    t_m_s = db.Column(db.String(64))
    squadron_id = db.Column(db.Integer, db.ForeignKey('squadron.id'))
    airframe_hours = db.Column(db.Integer)



    '''
    Insert aircraft data into the database
    '''
    @staticmethod
    def insert_aircrafts():
        data = {
            165212: ('AH-1Z', 303, 1821.0),
            167991: ('UH-1Y', 303, 2100.0),
            168221: ('UH-1Y', 269, 4890.2),
            168950: ('AH-1Z', 367, 1209.0),
            165339: ('UH-1Y', 367, 2122.5),
            168001: ('AH-1Z', 367, 2121.2),
            168002: ('AH-1Z', 367, 1500.1),
            168003: ('AH-1Z', 367, 1700.1),
            167223: ('UH-1Y', 167, 2356.7)
        }
        for i in data:
            aircraft = Aircraft()
            aircraft.aircraft_id = i
            aircraft.t_m_s = data[i][0]
            aircraft.squadron_id = data[i][1]
            aircraft.airframe_hours = data[i][2]
            db.session.add(aircraft)
        db.session.commit()


    def __repr__(self):
        return '<Aircraft %r' % self.id


class Engine(db.Model):
    __tablename__ = 'engines'
    id = db.Column(db.Integer, primary_key=True)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircrafts.aircraft_id'))
    position = db.Column(db.Integer)
    e_hours = db.Column(db.Integer)

    '''
    Insert engine data into the database
    '''
    def insert_engines():
        data = {
            121001: (165339, 1, 350.0),
            121031: (165339, 2, 489.5),
            121002: (165212, 1, 101.1),
            121003: (165212, 2,  125.0),
            121004: (168221, 1, 109.0),
            121005: (168221, 2, 351.0),
            121090: (168950, 1, 421.0),
            121081: (168950, 2, 220.0),
            121991: (168001, 1, 219.0),
            121901: (168001, 2, 315.1),
            121853: (167223, 1, 200.5),
            121852: (167223, 2, 209.0),
            121723: (167991, 1, 321.0),
            121709: (167991, 2, 329.1)
        }
        for i in data:
            engine = Engine()
            engine.id = i
            engine.aircraft_id = data[i][0]
            engine.position = data[i][1]
            engine.e_hours = data[i][2]
            db.session.add(engine)
        db.session.commit()

    def __repr__(self):
        return '<Engine %r' % self.id

class Flight(db.Model):
    __tablename__ = 'flights'
    flight_id = db.Column(db.Integer, primary_key = True)
    pilot_id =db.Column(db.Integer, db.ForeignKey('pilot.id'))
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircrafts.aircraft_id'))
    hours = db.Column(db.Integer)
    flight_date = db.Column(db.String(150))


    @staticmethod
    def insert_flights():
        data = {
            1700101: (4, 165339, 1, '2005-01-01'),
            1700201: (9, 168950, 2, '2005-01-02'),
            1700301: (4, 165339, 1, '2005-01-03'),
            1700401: (9, 168950, 2, '2005-01-04'),
            1700501: (12, 165339, 4, '2005-01-05'),
            1700601: (13, 168950, 5, '2005-01-06'),
            1700701: (14, 165339, 6, '2005-01-07'),
            1700801: (9, 168950, 7, '2005-01-08'),
            1700901: (4, 165339, 8, '2005-01-09'),
            1711101: (12, 168950, 9, '2005-01-10'),
            1712101: (13, 165339, 10, '2005-01-11'),
            1713201: (14, 168950, 11, '2005-01-12'),
            1811101: (12, 168950, 0, 'canceled'),
            1812101: (13, 165339, 0, 'canceled'),
            1813201: (14, 168950, 0, 'canceled'),
            1911101: (15, 165212, 0, 'canceled'),
            1912101: (16, 165212, 0, 'canceled'),
            1913201: (17, 165339, 0, 'canceled')
        }
        for i in data:
            flight = Flight()
            flight.flight_id = i
            flight.pilot_id = data[i][0]
            flight.aircraft_id = data[i][1]
            flight.hours = data[i][2]
            flight.flight_date = data[i][3]
            db.session.add(flight)
        db.session.commit()

    def __repr__(self):
        return '<Flight %r' % self.id



'''
SQLite does not support built-in date and/or time storage class. Instead, it
leverages some built-in date and time functions to use other storage classes such as TEXT, REAL, or INTEGER
for storing the date and time values.
'''
class MaintenanceDue(db.Model):
    __tablename__ = 'maintenanceDues'
    job_id = db.Column(db.Integer, primary_key = True)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircrafts.aircraft_id'), primary_key = True)
    description = db.Column(db.String(150))
    type_inspection =  db.Column(db.String(80))
    date_due = db.Column(db.String)
    hours_due = db.Column(db.Integer)


    @staticmethod
    def insert_data():
        data = {
            3671700101: (165339, 'monthly inspection', 'A/F', '2017-01-01', 2200.0),
            3031700201: (168001, 'eng insp', 'ENG', '2017-02-02', 2150.0),
            16921700101:(168950, '200 hr insp', 'A/F', '2017-03-01', 1409.0),
            26751700301:(165212, '50 hr insp', 'ENG', 'N/A', 75.0)
        }
        for i in data:
            due_data = MaintenanceDue()
            due_data.job_id = i
            due_data.aircraft_id = data[i][0]
            due_data.description = data[i][1]
            due_data.type_inspection = data[i][2]
            due_data.date_due = data[i][3]
            due_data.hours_due = data[i][4]
            db.session.add(due_data)
        db.session.commit()

    def __repr__(self):
        return '<MaintenanceDue %r' % self.job_id


class MaintenanceHistory(db.Model):
    __tablename__ = 'MaintenanceHistory'
    job_id = db.Column(db.Integer, primary_key=True)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircrafts.aircraft_id'), primary_key=True)
    description = db.Column(db.String(150))
    type_inspection =  db.Column(db.String(80))
    aircraft_hours = db.Column(db.Integer)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanic.id'))
    date_complete = db.Column(db.String, primary_key=True)


    @staticmethod
    def insert_data():
        data = {
            367134001: (165339, 'monthly inspection', 'A/F', 2150, 1, '2016-12-02'),
            1675330010: (167223, '50 hr insp', 'ENG', 2356.7, 5, '2016-11-28')
        }
        for i in data:
            due_data = MaintenanceHistory()
            due_data.job_id = i
            due_data.aircraft_id = data[i][0]
            due_data.description = data[i][1]
            due_data.type_inspection = data[i][2]
            due_data.aircraft_hours = data[i][3]
            due_data.mechanic_id = data[i][4]
            due_data.date_complete = data[i][5]
            db.session.add(due_data)
        db.session.commit()

    def __repr__(self):
        return '<MaintenaceHistory %r' % self.job_id


@login_manager.user_loader
def user_loader(id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(id)



#------------------------------RUN ALL------------------------------------------

def call_all():
    Squadron.insert_squadrons()
    Aircraft.insert_aircrafts()
    Mechanic.insert_mechanics()
    Administrator.insert_admin()
    Pilot.insert_pilots()
    Engine.insert_engines()
    Flight.insert_flights()
    MaintenanceDue.insert_data()
    MaintenanceHistory.insert_data()

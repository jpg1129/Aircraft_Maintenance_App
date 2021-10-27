#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Mechanic, Administrator, Pilot, Squadron, Aircraft, Engine, Flight, MaintenanceDue, MaintenanceHistory
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Mechanic=Mechanic, Pilot=Pilot, Squadron=Squadron,
    Aircraft=Aircraft, Engine=Engine, Flight=Flight, MaintenanceDue=MaintenanceDue, MaintenanceHistory=MaintenanceHistory, Administrator=Administrator)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


#-----------------------------SQL VIEWS----------------------------------------
'''
a view of aircraft_ids and the squadron that the aircraft belongs to
'''
@app.before_first_request
def createAircraftView():
    c = db.engine.connect()
    c.execute("DROP VIEW IF EXISTS aircraft_view")
    c.execute("CREATE VIEW IF NOT EXISTS aircraft_view (aircraft_id, t_m_s, squadron_id, airframe_hours) AS SELECT aircraft_id, t_m_s, squadron_id, airframe_hours FROM aircrafts")


'''
a view containing the flights that are canceled or in other words have no flight-date
'''
@app.before_first_request
def canceled_flight_view():
    c = db.engine.connect()
    c.execute("DROP VIEW IF EXISTS canceled_flight_view")
    sql = "CREATE VIEW IF NOT EXISTS canceled_flight_view (flight_id, pilot_id, aircraft_id, flight_date, squadron_id, hours) AS SELECT flight_id, pilot_id, aircraft_id, flight_date, squadron_id, hours FROM (SELECT flight_id, pilot_id, aircrafts.aircraft_id, squadron_id, flight_date, hours FROM flights, aircrafts WHERE flights.aircraft_id=aircrafts.aircraft_id AND flight_date='canceled')"
    c.execute(sql)

#-----------------------------SQL TRIGGERS--------------------------------------

'''
WOULDN't this work beter after insert on the datase table
so it will update correct if somebody enters a date that is before or after
'''
@app.before_first_request
def createMaintMonthDueTrigger():
    c = db.engine.connect()
    c.execute("DROP TRIGGER IF EXISTS init_monthly")
    c.execute('''CREATE TRIGGER IF NOT EXISTS init_monthly AFTER DELETE ON "maintenanceDues"
        WHEN OLD.description = "monthly inspection"
        BEGIN
        INSERT into maintenanceDues VALUES (OLD.job_id, OLD.aircraft_id, OLD.description,
        OLD.type_inspection, date(OLD.date_due, '+1 month'), OLD.hours_due);
        END;''')


#Create a trigger to update maint_due for '50 hr insp'
@app.before_first_request
def createMaint50DueTrigger():
    c = db.engine.connect()
    c.execute("DROP TRIGGER IF EXISTS initiate_50hr")
    c.execute('''CREATE TRIGGER IF NOT EXISTS initiate_50hr AFTER DELETE ON "maintenanceDues"
             WHEN old.description = "50 hr insp"
             BEGIN
             INSERT into maintenanceDues VALUES (OLD.job_id, OLD.aircraft_id, OLD.description,
             OLD.type_inspection, OLD.date_due, (OLD.hours_due + 50));
             END;''')


# Trigger to update maint_due for 'eng_insp'
@app.before_first_request
def createMaintEngineInspTrigger():
    c = db.engine.connect()
    c.execute("DROP TRIGGER IF EXISTS initiate_engInsp")
    c.execute('''CREATE TRIGGER IF NOT EXISTS initiate_engInsp AFTER DELETE ON "maintenanceDues"
            WHEN old.description = "eng insp"
            BEGIN
            INSERT into maintenanceDues VALUES (OLD.job_id + 1, OLD.aircraft_id, OLD.description,
            OLD.type_inspection, OLD.date_due, OLD.hours_due + 100);
            END;''')



# A trigger to update aircraft engine after a flight
@app.before_first_request
def createUpdateEngineHoursTrigger():
    c = db.engine.connect()
    c.execute("DROP TRIGGER IF EXISTS update_eng_hours")
    c.execute('''CREATE TRIGGER IF NOT EXISTS update_eng_hours AFTER INSERT ON "flights"
                 BEGIN
                 UPDATE aircrafts SET airframe_hours = airframe_hours + new.hours
                 WHERE new.aircraft_id = aircrafts.aircraft_id;
                 UPDATE engines SET e_hours = e_hours + new.hours
                 WHERE new.aircraft_id = engines.aircraft_id;
                 END;''')



# A trigger to update pilot hours after a flight
@app.before_first_request
def createUpdatePilotHoursTrigger():
    c = db.engine.connect()
    c.execute("DROP TRIGGER IF EXISTS update_pilot_hrs")
    c.execute('''CREATE TRIGGER IF NOT EXISTS update_pilot_hrs AFTER INSERT ON "flights"
                 BEGIN
                 UPDATE pilot set hours = hours + new.hours
                 WHERE new.pilot_id = pilot.id;
                 END;''')



if __name__ == '__main__':
    manager.run()

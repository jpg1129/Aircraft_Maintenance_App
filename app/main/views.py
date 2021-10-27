from __future__ import print_function
from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Aircraft, Engine, Mechanic, MaintenanceDue, Flight, Pilot, MaintenanceHistory
from sqlalchemy.sql import text
import sys
from datetime import date
from .forms import DeleteForm

#--------------------------MECHANIC MENU----------------------------------------
'''
render the correct menu when the home button is pressed for pilots and
mechanics.
'''
@main.route('/')
def index():
    return render_template('index.html')

'''
render the mechanic menu when called
'''
@main.route('/mechanic')
def mechanic_menu():
    return render_template('mechanic/menu.html')

'''sqlalchemy_viewsviewsbiew
Query to retrieve aircraft by squadron using view

'''
@main.route('/mechanic/aircraft')
def mechanic_get_aircraft():
    squadron_id = current_user.squadron_id
    result=[]
    sql = "SELECT * FROM aircraft_view WHERE squadron_id = ?"
    c = db.engine.connect()
    for row in c.execute(sql, (squadron_id,)):
        result.append(row)
    return render_template('mechanic/aircraft.html', result=result)


'''
Query to retrieve a list of engines matched with aircraft,
specific to squadron. This query works but returns a weird result because there is no
engine that is associated with airraft ID 168002
'''
@main.route('/mechanic/engine')
def mechanic_get_engine():
    squadron_id = current_user.squadron_id
    result=[]
    sql = "SELECT e.id as engine_id, a.aircraft_id, t_m_s, squadron_id, position, e_hours " \
          "FROM engines as e LEFT OUTER JOIN aircrafts as a ON e.aircraft_id = a.aircraft_id WHERE squadron_id = ?"
    c = db.engine.connect()
    for row in c.execute(sql, (squadron_id,)):
        result.append(row)
    return render_template('mechanic/engine.html', result=result)


'''
render list of mechanics when button pressed in the mechanic menu.
Can talk about what sqlalcehmy provides through .query and how it is
much easier and less messy than alternative.

Could include current_user do we highlight?


Need to decide if we want to
render all the mechanics or just those mechanics that are not equal to current
user and in the same squadron.

@main.route('/mechanic/list')
def mechanic_get_list():
    data = Mechanic.query.filter(Mechanic.id is not current_user.id and Mechanic.squadron_id is current_user.squadron_id)
    return render_template('mechanic/list.html', data=data)

'''
@main.route('/mechanic/list')
def mechanic_get_list():
    data = Mechanic.query.filter(Mechanic.id != current_user.id)
    return render_template('mechanic/list.html', data=data)


'''
render maintenance due list when button pressed in the mechanic menu

NOTE: need to show only maintenance dues which
are due for the specific squadron

SOMETHING TO ADD: could alert mechanics when their due dates are past due
by highlighting it red?
'''
@main.route('/mechanic/maintenance_due')
def mechanic_get_maintenance_due():
    data = MaintenanceDue.query.all()
    return render_template('mechanic/maintenance_due.html', data=data)


@main.route('/mechanic/complete_maintenance', methods=['GET', 'POST'])
def mechanic_complete_maintenance():
    data = MaintenanceDue.query.all()
    error = None
    try:
        if request.method == 'POST':
            job_id = request.form['job_id']
            description = request.form['description']
            date_complete = request.form['date_complete']
            sel = "SELECT aircraft_id, type_inspection, hours_due FROM maintenanceDues WHERE job_id = ?"
            dele = "DELETE FROM maintenanceDues WHERE job_id=? AND description=?"
            ins = " INSERT into MaintenanceHistory VALUES (?, ?, ?, ?, ?, ?, ?)"
            c = db.engine.connect()
            data = c.execute(sel, (job_id,)).fetchone()
            aircraft_id = data.aircraft_id
            type_inspection = data.type_inspection
            aircraft_hours = data.hours_due
            mechanic_id = current_user.id
            c.execute(dele, (job_id, description,))
            c.execute(ins, (job_id, aircraft_id, description, data.type_inspection, data.hours_due,current_user.id, date_complete))
            flash('You Successfully Completed Job ID ' + job_id)
            return redirect(url_for('main.mechanic_get_maintenance_history'))
    except Exception as e:
        flash(e)
        return render_template('mechanic/complete_maintenance.html', error=error)
    return render_template('mechanic/complete_maintenance.html', data=data)


@main.route('/mechanic/maintenance_history')
def mechanic_get_maintenance_history():
    data = MaintenanceHistory.query.all()
    return render_template('mechanic/maintenance_history.html', data=data)
#-------------------------------PILOT MENU--------------------------------------

'''
render the piot menu when called
'''
@main.route('/pilot/menu')
def pilot_menu():
    return render_template('pilot/menu.html')

'''
get the pilot history
'''
@main.route('/pilot/flights')
def pilot_flights():
    result = []
    pilot_id=current_user.id
    sql = "SELECT squadron_id, aircrafts.aircraft_id, flight_id, pilot_id, hours, flight_date FROM flights NATURAL JOIN aircrafts WHERE pilot_id = ?"
    c = db.engine.connect()
    for row in c.execute(sql, (pilot_id,)):
        result.append(row)
    return render_template('/pilot/flights.html', data=result)

'''
data = db.session.query(Flight).\
                join(Aircraft.aircraft_id).\
                filter(Aircraft.aircraft_id == current_user.squadron_id).all()
'''
@main.route('/pilot/add_flight', methods=['GET', 'POST'])
def pilot_add_flight():
    pilot_id = current_user.id
    error = None
    try:
        if request.method == 'POST':
            flight_id = request.form['flight_id']
            aircraft_id = request.form['aircraft_id']
            hours = request.form['hours']
            date_complete = request.form['date_complete']
            ins = " INSERT into flights VALUES (?, ?, ?, ?, ?)"
            c = db.engine.connect()
            c.execute(ins, (flight_id, pilot_id, aircraft_id, hours, date_complete,))
            flash('You Successfully Completed Flight ID ' + flight_id)
            return redirect(url_for('main.pilot_flights'))
    except Exception as e:
        flash(e)
        return render_template('pilot/add_flight.html', error=error)
    return render_template('pilot/add_flight.html')



'''
 Query to retrieve list of pilots by squadron and their respective flight hours
'''
@main.route('/pilot/pilots')
def pilot_list():
    result =[]
    squadron_id=current_user.squadron_id
    sql = "SELECT pilot.name, hours FROM pilot WHERE pilot.id in (SELECT user.id FROM user WHERE squadron_id = ?) ORDER BY hours DESC"
    c = db.engine.connect()
    for row in c.execute(sql, (squadron_id,)):
        result.append(row)
    return render_template('/pilot/pilots.html', data=result)

'''
Query to view total flight time of squadron
'''
@main.route('/pilot/flight-hours')
def flight_hours_per_squadron():
    result = []
    squadron_id = current_user.squadron_id
    c = db.engine.connect()
    sql = "SELECT sum(hours) as total_hours from flights INNER JOIN aircrafts ON flights.aircraft_id=aircrafts.aircraft_id GROUP BY squadron_id HAVING squadron_id= ?;"
    for row in c.execute(sql, (squadron_id)):
        result.append(row)
    return render_template('pilot/flighthours.html', data=result)



'''
Query to view flight history data of squadron, only for completed flights.
'''
@main.route('/pilot/squadron-history')
def flight_squadron_history():
    result = []
    squadron_id = current_user.squadron_id
    sql = "SELECT squadron_id, aircrafts.aircraft_id, flight_id, pilot_id, hours FROM flights NATURAL JOIN aircrafts WHERE squadron_id = ? EXCEPT SELECT squadron_id, aircraft_id, flight_id, pilot_id, hours FROM canceled_flight_view ORDER BY pilot_id DESC"
    c = db.engine.connect()
    for row in c.execute(sql, (squadron_id)):
        result.append(row)
    return render_template('pilot/squadron_history.html', data=result)

'''
Query to view canceled flights for squadron
'''
@main.route('/pilot/canceled-flights')
def canceled_squadron_flights():
    result = []
    squadron_id = current_user.squadron_id
    sql = "SELECT flight_id, pilot_id, aircraft_id, flight_date FROM canceled_flight_view WHERE squadron_id = ?"
    c = db.engine.connect()
    for row in c.execute(sql, (squadron_id)):
        result.append(row)
    return render_template('pilot/canceled_flights.html', data=result)


#------------------------------------------Administrator queries---------------

'''
render the piot menu when called
'''
@main.route('/administrator/menu')
def admin_menu():
    return render_template('administrator/menu.html')


'''
render the flight query when button pressed in the pilot menu
May look werid because there are only flights added for a specific
squadron right now
'''
@main.route('/administrator/flights')
def admin_get_all_flights():
    data =  Flight.query.all()
    return render_template('administrator/all_flights.html', data=data)


@main.route('/administrator/engines')
def admin_get_engines():
    result = []
    sql = "SELECT e.id as engine_id, a.aircraft_id, t_m_s, squadron_id, position, e_hours " \
          "FROM engines as e LEFT OUTER JOIN aircrafts as a ON e.aircraft_id = a.aircraft_id"
    c = db.engine.connect()
    for row in c.execute(sql):
        result.append(row)
    return render_template('administrator/engines.html', data=result)


@main.route('/administrator/insert-user')
def insert_user():
    return render_template('administrator/insert_user.html')


@main.route('/administrator/delete-user', methods=['GET', 'POST'])
def delete_user():
    data = User.query.all()
    error = None
    try:
        if request.method == 'POST':
            user_id = request.form['user_id']
            username = request.form['username']
            sql = "DELETE FROM user WHERE id = ? and username = ?"
            c = db.engine.connect()
            c.execute(sql, (user_id, username))
            flash('You Successfully Deleted Username ' + username)
            return redirect(url_for('main.view_users'))
    except Exception as e:
        flash(e)
        return render_template('mechanic/delete_user.html', error=error)
    return render_template('administrator/delete_user.html', data=data)


@main.route('/administrator/update-user', methods=['GET', 'POST'])
def update_user():
    result = []
    form = DeleteForm()
    error = None
    try:
        if request.method == 'POST':
            for k, v in form.data.items():
                result.append(v)
            sql = "UPDATE user SET username = ?, squadron_id = ?, type = ? WHERE id = ?"
            c = db.engine.connect()
            c.execute(sql, (result[1], result[2], result[3], result[0]))
            flash('You Successfully Updated Username ' + result[1])
            return redirect(url_for('main.view_users'))
    except Exception as e:
         flash(e)
         return render_template('administrator/update_user.html', error=error, form=form)
    return render_template('administrator/update_user.html', form=form)


@main.route('/administrator/view-users')
def view_users():
    data = User.query.all()
    return render_template('administrator/view_users.html', data=data)

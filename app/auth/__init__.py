'''
The routes realted to the user authentication system
can be added to a auth blueprint. Using blueprints in this way
for different sets of application functionality is a great way
to keep the code neatly organized.
'''

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views

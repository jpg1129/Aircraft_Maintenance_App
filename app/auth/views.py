from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from .forms import LoginForm
from ..models import User
import sys

# Basically query functions
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.email.data).first()
        job_type = user.type
        # print(password, file=sys.stderr)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if job_type == 'mechanic':
                return redirect(request.args.get('next') or url_for('main.mechanic_menu'))
            elif job_type == 'pilot':
                return redirect(request.args.get('next') or url_for('main.pilot_menu'))
            elif job_type == 'administrator':
                return redirect(request.args.get('next') or url_for('main.admin_menu'))
            else:
                return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

import numpy as np;
import pandas as pd
import requests;
from flask import render_template, redirect, url_for, flash, session, request, jsonify;
from flask_login import login_user, current_user, logout_user;
from CropMaster import app, db;
from CropMaster.forms import Signup_form, Login_form, choose_state_form, choose_district_form
from CropMaster.models import User;
from CropMaster.frontend_data import india_states_districts, seasons, state_tuples, find_district_tuples, crops;

df = pd.read_csv("CropMaster/backend_date/average_rainfall_temperature.csv")

@app.route('/', methods=['GET', 'POST'])
def home():
    user_logged_in = False
    if current_user.is_authenticated:
        user_logged_in = True
    state_form = choose_state_form()
    state_form.state.choices = state_tuples
    state_form.crop.choices = [(crop, crop) for crop in crops]

    if state_form.validate_on_submit():

        district_form = choose_district_form()

        district_form.district.choices = find_district_tuples(state_form.state.data)

        district_form.season.choices = [(season, season) for season in seasons.keys()]

        session['state'] = state_form.state.data
        session['crop'] = state_form.crop.data
        session['area'] = state_form.area.data
        
        return render_template('base.html', user_logged_in=user_logged_in, current_user=current_user, home_active=True, dashboard_active=False, state_form=state_form, district_form=district_form)

    if request.method == 'POST' and 'district' in request.form:
            
            if current_user.is_authenticated:
                user_id_to_pass = current_user.id
            
            session['district'] = request.form.get('district')
            session['season'] = request.form.get('season')

            print(session['district'])
            print(session['state'])
            print(session['crop'])
            print(session['season'])

            filtered_df = df[(df["state"] == session["state"]) & 
                    (df["district"] == session["district"]) & 
                    (df["crop"] == session["crop"]) & 
                    (df["season"] == session["season"])]
            
            if filtered_df["rainfall"].values.size > 0:
                session["rainfall"] = int(filtered_df["rainfall"].values[0])
            else:
                session["rainfall"] = 0
            
            if len(filtered_df["avg_temp"].values.tolist()) > 0:
                session["avg_temp"] = int(filtered_df["avg_temp"].values.tolist()[0])
            else:
                session["avg_temp"] = 0

            json_data = {
                "user_auth_id": [current_user.is_authenticated, user_id_to_pass],
                "state": session["state"],
                "district": session["district"],
                "crop": session["crop"],
                "season": session["season"],
                "area": session["area"],
                "rainfall": session["rainfall"],
                "avg_temp": session["avg_temp"]
            }

            print(json_data)

            predicted_value = requests.post('http://127.0.0.1:5000/api/predict', json=json_data)


            return render_template('base.html', user_logged_in=user_logged_in, current_user=current_user, home_active=True, dashboard_active=False, state_form=None, district_form=None, predicted_value=predicted_value.json()["result"]["prediction"])
    
    return render_template('base.html', user_logged_in=user_logged_in, current_user=current_user, home_active=True, dashboard_active=False, state_form=state_form, district_form=None)

@app.route('/dashboard')
def dashboard():
    user_logged_in = False
    if current_user.is_authenticated:
        user_logged_in = True

        if current_user.user_category == "admin":
            list_of_all_users = User.query.all();
            return render_template('base.html', current_user=current_user, user_logged_in=user_logged_in, home_active=False, dashboard_active=True, user_category="admin", list_of_all_users=list_of_all_users);
        else:
            print(current_user.results)
            return render_template('base.html', current_user=current_user, user_logged_in=user_logged_in, home_active=False, dashboard_active=True, user_category="Farmer", list_of_all_results=current_user.results);
    else:
        return url_for('home')
    
@app.route('/user_dashboard/<int:user_id>')
def user_dashboard(user_id):
    user_logged_in = False
    if current_user.is_authenticated:
        user_logged_in = True

        if current_user.user_category == "admin":
            user_to_view = User.query.filter_by(id=user_id).first() 
            return render_template('base.html', current_user=current_user, user_logged_in=user_logged_in, home_active=False, dashboard_active=True, list_of_all_results_to_view=user_to_view.results);
        else:
            return url_for('home')
    else:
        return url_for('home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'Log out and then try to Log in!', 'success')
        return redirect(url_for('home'))
    form = Login_form();
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.password == form.password.data:
            if form.remember_me.data == True:
                login_user(user, remember=True)
            else:
                login_user(user, remember=False)
            flash(f'Successfully Logged in as {user.user_category}', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'incorrect email and password combination', '')
            return redirect(url_for('login'))
    return render_template('login_signup.html', signing_up=False, form=form);

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash(f'Log out and then sign up with different email!', 'success')
        return redirect(url_for('home'))
    form = Signup_form();

    if form.validate_on_submit():
        username, email, password = form.username.data, form.email.data, form.password.data;
        new_user = User(username=username, email=email, password=password);
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)

        flash(f'successfully logged in with the email {form.email.data}', 'success')

        return redirect(url_for('home'))
    return render_template('login_signup.html', signing_up=True, form=form);

@app.route('/logout')
def logout():
    logout_user()
    flash(f'Logged out user successfully', 'success')
    return redirect(url_for('home'))
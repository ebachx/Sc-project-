import os
import io
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import qrcode

from models import db, User, Category, Station, StationImage
from functools import wraps
from flask import abort

app = Flask(__name__)

adnmin = Admin()
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'tajne-heslo-pro-vyvoj'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def index():
    stations = Station.query.filter_by(is_active=True).order_by(Station.order).all()
    return render_template('index.html', stations=stations)

@app.route('/station/<int:station_id>')
def station_detail(station_id):
    station = Station.query.get_or_404(station_id)
    

    cat_ids = [cat.id for cat in station.categories]
    related = []
    if cat_ids:
        related = (
            Station.query.filter(
                Station.is_active == True,
                Station.id != station_id,
                Station.categories.any(Category.id.in_(cat_ids))
            )
            .limit(3)
            .all()
        )
    

    return render_template('visitor/station_detail.html', station=station, related=related)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin'))
    return render_template('admin/login.html')

@app.route('/admin_logout')
def admin_logout():
    logout_user()
    return redirect(url_for('index'))
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'teacher']:
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function
@app.route('/admin')
@login_required
@admin_required
def admin():

    stations = Station.query.order_by(Station.order).all()
    return render_template('admin/dashboard.html', stations=stations)

@app.route('/admin/station/edit/<int:station_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_station(station_id):
    station = Station.query.get_or_404(station_id)
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('categories')
        selected_ids = [int(cid) for cid in selected_ids]
        station.categories = Category.query.filter(Category.id.in_(selected_ids)).all()

        station.name = request.form.get('name')
        station.floor = int(request.form.get('floor', 0))
        station.room_number = request.form.get('room_number')
        station.description = request.form.get('description')
        station.equipment = request.form.get('equipment')
        station.projects = request.form.get('projects')
        station.contact_person = request.form.get('contact_person')
        station.contact_email = request.form.get('contact_email')
        station.qr_code = request.form.get('qr_code')

        delete_photo_ids = request.form.getlist('delete_photos')
        for photo_id in delete_photo_ids:
            photo = StationImage.query.get(int(photo_id))
            if photo:
                file_path = os.path.join(app.root_path, 'static/uploads', photo.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(photo)

        if 'new_photos' in request.files:
            files = request.files.getlist('new_photos')
            for file in files:
                if file and file.filename != '':
                    ext = os.path.splitext(file.filename)[1]
                    filename = f"{uuid.uuid4().hex}{ext}"
                    file.save(os.path.join(app.root_path, 'static/uploads', filename))
                    new_img = StationImage(filename=filename, station_id=station.id)
                    db.session.add(new_img)

        db.session.commit()
        flash('Data updated!', 'success')
        return redirect(url_for('edit_station', station_id=station.id))

    all_categories = Category.query.all()
    station_category_ids = [c.id for c in station.categories]
    
    return render_template('admin/edit_station.html', 
                           station=station, 
                           all_categories=all_categories, 
                           station_category_ids=station_category_ids)
app.run(debug=True)
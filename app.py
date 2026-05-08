import os
import io
import uuid
 
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
import qrcode
 
from models import db, User, Category, Station, StationImage
 
app = Flask(__name__)
 
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'tajne-heslo-pro-vyvoj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db.init_app(app)
 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login' 
 
os.makedirs(os.path.join(basedir, 'static', 'uploads'), exist_ok=True)
 
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 
 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'teacher']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
 
 
#--------------------------VISITOR

@app.route('/')
def index():
    stations = Station.query.filter_by(is_active=True).order_by(Station.order).all()
    return render_template('visitor/index.html', stations=stations)
 
 
@app.route('/station/<int:station_id>')
def station_detail(station_id):
    station = Station.query.get_or_404(station_id)
    cat_ids = [cat.id for cat in station.categories]
    related = []
    if cat_ids:
        related = (
            Station.query
            .filter(
                Station.is_active == True,
                Station.id != station_id,
                Station.categories.any(Category.id.in_(cat_ids))
            )
            .limit(3)
            .all()
        )
    return render_template('visitor/station_detail.html', station=station, related=related)
 
 
@app.route('/qr/<qr_code>')
def qr_redirect(qr_code):
    station = Station.query.filter_by(qr_code=qr_code).first_or_404()
    return redirect(url_for('station_detail', station_id=station.id))
 
 
#--------------------------AUTH--------------------------
 
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Špatné přihlašovací údaje.', 'error')
    return render_template('admin/login.html')
 
 
@app.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))
 
 
#---------------------------------ADMIN
 
@app.route('/admin')
@login_required
@admin_required
def admin():
    stations = Station.query.order_by(Station.order).all()
    return render_template('admin/dashboard.html', stations=stations)
 
 
@app.route('/admin/station/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_station():
    if request.method == 'POST':
        station = Station(
            name=request.form.get('name'),
            floor=int(request.form.get('floor', 0)),
            room_number=request.form.get('room_number'),
            description=request.form.get('description'),
            equipment=request.form.get('equipment'),
            projects=request.form.get('projects'),
            contact_person=request.form.get('contact_person'),
            contact_email=request.form.get('contact_email'),
            qr_code=uuid.uuid4().hex[:12]
        )
        selected_ids = [int(i) for i in request.form.getlist('categories')]
        station.categories = Category.query.filter(Category.id.in_(selected_ids)).all()
 
        db.session.add(station)
        db.session.commit()
 
        for file in request.files.getlist('new_photos'):
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1]
                filename = f"{uuid.uuid4().hex}{ext}"
                file.save(os.path.join(app.root_path, 'static', 'uploads', filename))
                db.session.add(StationImage(filename=filename, station_id=station.id))
        db.session.commit()
 
        flash('Stanoviště bylo vytvořeno!', 'success')
        return redirect(url_for('edit_station', station_id=station.id))
 
    all_categories = Category.query.all()
    return render_template('admin/new_station.html', all_categories=all_categories)
 
 
@app.route('/admin/station/edit/<int:station_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_station(station_id):
    station = Station.query.get_or_404(station_id)
 
    if request.method == 'POST':
        selected_ids = [int(i) for i in request.form.getlist('categories')]
        station.categories = Category.query.filter(Category.id.in_(selected_ids)).all()
 
        station.name = request.form.get('name')
        station.floor = int(request.form.get('floor', 0))
        station.room_number = request.form.get('room_number')
        station.description = request.form.get('description')
        station.equipment = request.form.get('equipment')
        station.projects = request.form.get('projects')
        station.contact_person = request.form.get('contact_person')
        station.contact_email = request.form.get('contact_email')
 
        for photo_id in request.form.getlist('delete_photos'):
            photo = StationImage.query.get(int(photo_id))
            if photo:
                file_path = os.path.join(app.root_path, 'static', 'uploads', photo.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(photo)
 
        for file in request.files.getlist('new_photos'):
            if file and file.filename != '':
                ext = os.path.splitext(file.filename)[1]
                filename = f"{uuid.uuid4().hex}{ext}"
                file.save(os.path.join(app.root_path, 'static', 'uploads', filename))
                db.session.add(StationImage(filename=filename, station_id=station.id))
 
        db.session.commit()
        flash('Data updated!', 'success')
        return redirect(url_for('edit_station', station_id=station.id))
 
    all_categories = Category.query.all()
    station_category_ids = [c.id for c in station.categories]
    return render_template('admin/edit_station.html',
                           station=station,
                           all_categories=all_categories,
                           station_category_ids=station_category_ids)
 
 
@app.route('/admin/station/delete/<int:station_id>', methods=['POST'])
@login_required
@admin_required
def delete_station(station_id):
    station = Station.query.get_or_404(station_id)
    for img in station.images:
        file_path = os.path.join(app.root_path, 'static', 'uploads', img.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(station)
    db.session.commit()
    flash('Stanoviště bylo smazáno.', 'success')
    return redirect(url_for('admin'))
 
 
@app.route('/admin/station/<int:station_id>/qr')
@login_required
def download_qr(station_id):
    station = Station.query.get_or_404(station_id)
    base_url = os.environ.get('BASE_URL', request.host_url.rstrip('/'))
    url = f"{base_url}/qr/{station.qr_code}"
 
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png',
                     download_name=f"qr_{station.room_number}.png")
 
 
if __name__ == '__main__':
    app.run(debug=True)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

station_categories = db.Table(
    'station_categories',
    db.Column('station_id', db.Integer, db.ForeignKey('station.id', ondelete='CASCADE')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='teacher')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10), default='📌')
    color = db.Column(db.String(7), default='#3B82F6')

    def __repr__(self):
        return f'<Category {self.name}>'


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    room_number = db.Column(db.String(20))
    floor = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    equipment = db.Column(db.Text)
    projects = db.Column(db.Text)
    contact_person = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    qr_code = db.Column(db.String(64), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    categories = db.relationship(
        'Category', secondary=station_categories, backref='stations', lazy='subquery'
    )
    images = db.relationship(
        'StationImage', backref='station', lazy=True, cascade='all, delete-orphan'
    )

    @property
    def primary_image(self):
        for img in self.images:
            if img.is_primary:
                return img
        return self.images[0] if self.images else None

    @property
    def floor_label(self):
        if self.floor == 0:
            return 'Přízemí'
        elif self.floor == -1:
            return 'Suterén'
        else:
            return f'{self.floor}. patro'

    def __repr__(self):
        return f'<Station {self.name}>'


class StationImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

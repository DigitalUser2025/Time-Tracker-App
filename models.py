from app import db
from datetime import datetime, date
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    security_question = db.Column(db.String(200), nullable=False)
    security_answer = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='employee')  # admin, manager, employee
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True)
    manual_time_entries = db.relationship('ManualTimeEntry', foreign_keys='ManualTimeEntry.user_id', backref='user', lazy=True)
    password_reset_requests = db.relationship('PasswordResetRequest', foreign_keys='PasswordResetRequest.user_id', backref='user', lazy=True)

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clock_in = db.Column(db.DateTime, nullable=False)
    clock_out = db.Column(db.DateTime)
    date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ManualTimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    approver = db.relationship('User', foreign_keys=[approved_by])

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Float, default=0.0)
    regular_hours = db.Column(db.Float, default=0.0)  # From clock in/out
    manual_hours = db.Column(db.Float, default=0.0)   # From approved manual entries
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='daily_logs')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

class PasswordResetRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    approver = db.relationship('User', foreign_keys=[approved_by])

def calculate_daily_hours(user_id, target_date):
    """Calculate and update daily hours for a user on a specific date"""
    # Get all time entries for the date
    time_entries = TimeEntry.query.filter_by(user_id=user_id, date=target_date).all()
    
    regular_hours = 0.0
    for entry in time_entries:
        if entry.clock_out:
            delta = entry.clock_out - entry.clock_in
            regular_hours += delta.total_seconds() / 3600  # Convert to hours
    
    # Get approved manual time entries for the date
    manual_entries = ManualTimeEntry.query.filter_by(
        user_id=user_id, 
        date=target_date, 
        status='approved'
    ).all()
    
    manual_hours = sum(entry.hours for entry in manual_entries)
    
    total_hours = regular_hours + manual_hours
    
    # Update or create daily log
    daily_log = DailyLog.query.filter_by(user_id=user_id, date=target_date).first()
    if daily_log:
        daily_log.regular_hours = regular_hours
        daily_log.manual_hours = manual_hours
        daily_log.total_hours = total_hours
        daily_log.updated_at = datetime.utcnow()
    else:
        daily_log = DailyLog(
            user_id=user_id,
            date=target_date,
            regular_hours=regular_hours,
            manual_hours=manual_hours,
            total_hours=total_hours
        )
        db.session.add(daily_log)
    
    db.session.commit()
    return total_hours

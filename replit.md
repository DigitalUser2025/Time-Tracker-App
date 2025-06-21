# Employee Time Tracker

## Overview

This is a Flask-based employee time tracking application that allows employees to clock in/out, submit manual time entries, and enables managers/admins to approve users and time entries. The system includes role-based access control with three user types: employees, managers, and admins.

## System Architecture

The application follows a traditional web application architecture:

- **Frontend**: Server-side rendered HTML templates using Jinja2, styled with Tailwind CSS
- **Backend**: Flask web framework with Python 3.11
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Session Management**: Flask sessions with 30-day persistence for employee logins
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

## Key Components

### Authentication & Authorization
- Phone number-based authentication system
- Role-based access control (admin, manager, employee)
- Security question-based password recovery
- User approval workflow for new registrations
- Persistent sessions with 30-day expiration

### Time Tracking
- **Clock In/Out System**: Real-time time tracking for employees
- **Manual Time Entry**: Allows employees to submit time entries that require manager approval
- **Daily Log Calculation**: Automatic calculation of total hours worked per day
- **Time Entry Approval**: Manager/admin workflow for approving manual time entries

### User Management
- **User Registration**: New users require admin/manager approval
- **User Roles**: Three-tier role system (admin > manager > employee)
- **User Approval**: Pending user approval system for new registrations

### Reporting & Analytics
- Time reports with filtering by employee and date range
- Summary statistics for total hours worked
- Export capabilities for time data

## Data Flow

1. **User Registration**: New users register → Pending approval → Admin/Manager approves → User can login
2. **Time Tracking**: Employee clocks in → Works → Clocks out → Hours automatically calculated
3. **Manual Entries**: Employee submits manual time → Manager reviews → Approval/Rejection → Hours added to logs
4. **Reporting**: Managers/Admins view consolidated time reports across employees and date ranges

## External Dependencies

### Python Packages
- **Flask 3.1.1**: Core web framework
- **Flask-SQLAlchemy 3.1.1**: Database ORM
- **Gunicorn 23.0.0**: Production WSGI server
- **Werkzeug 3.1.3**: WSGI utilities and password hashing
- **psycopg2-binary 2.9.10**: PostgreSQL adapter
- **email-validator 2.2.0**: Email validation utilities

### Frontend Libraries
- **Tailwind CSS**: Utility-first CSS framework (CDN)
- **Feather Icons**: Icon library (CDN)

### System Dependencies
- OpenSSL for secure connections
- PostgreSQL for production database

## Deployment Strategy

The application is configured for deployment on Replit with:

- **Runtime**: Python 3.11 with Nix package management
- **Web Server**: Gunicorn with auto-reload and port reuse
- **Scaling**: Autoscale deployment target for handling variable load
- **Database**: SQLite for development, PostgreSQL for production
- **Process Management**: Parallel workflow execution with port waiting

### Environment Configuration
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SESSION_SECRET`: Secret key for session management (defaults to dev key)

The application includes a default admin user (phone: 0000000000, password: admin123) created automatically on first run.

## Changelog
- June 21, 2025: Initial setup with complete time tracking functionality
- June 21, 2025: Enhanced security - removed admin credentials from login page
- June 21, 2025: Added user deletion functionality for admins/managers with cascade delete
- June 21, 2025: Added Excel export functionality for time reports with professional formatting
- June 21, 2025: Added time entry editing functionality for managers/admins with inline editing and validation
- June 21, 2025: Added real-time digital clock to dashboard and fixed timezone display to show local time

## User Preferences

Preferred communication style: Simple, everyday language.
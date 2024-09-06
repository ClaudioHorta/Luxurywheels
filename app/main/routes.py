from flask import  current_app, Blueprint, render_template, redirect, url_for, flash, request,session
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Vehicle
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def home():   
    logged_in = 'user_id' in session
    results = Vehicle.query.limit(6).all()
    return render_template('index.html', logged_in=current_user.is_authenticated, rows=results, page='home')


@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    vehicles = Vehicle.query.all()
    return render_template('admin/admin_homepage.html', vehicles=vehicles)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/admin/add_vehicle", methods=['GET', 'POST'])
@login_required
def add_vehicle():
    if request.method == 'POST':
        brand = request.form.get('brand')
        model = request.form.get('model')
        category = request.form.get('category')
        transmission = request.form.get('transmission')
        vehicle_type = request.form.get('vehicle_type')
        daily_rate = float(request.form.get('daily_rate'))
        number_of_people = int(request.form.get('number_of_people'))
        last_revision_date_str = request.form.get('last_revision_date')
        next_revision_date_str = request.form.get('next_revision_date')
        active = True if request.form.get('active') == 'on' else False

        last_revision_date = datetime.strptime(last_revision_date_str, '%Y-%m-%d').date() if last_revision_date_str else None
        next_revision_date = datetime.strptime(next_revision_date_str, '%Y-%m-%d').date() if next_revision_date_str else None

        # Handle the file upload
        if 'image_file' not in request.files:
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, 'static/img', filename)
            file.save(file_path)
            image_url = 'img/'+filename

            vehicle = Vehicle(
                brand=brand, model=model, category=category, transmission=transmission,
                vehicle_type=vehicle_type, daily_rate=daily_rate, number_of_people=number_of_people,
                image_url=image_url, last_revision_date=last_revision_date,
                next_revision_date=next_revision_date, active=active
            )

            db.session.add(vehicle)
            db.session.commit()
            flash('Vehicle added successfully.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Allowed file types are png, jpg, jpeg, gif', 'danger')
            return redirect(request.url)

    return render_template('admin/add_vehicle.html')

@main.route("/admin/edit_vehicle/<int:vehicle_id>", methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        vehicle.brand = request.form.get('brand')
        vehicle.model = request.form.get('model')
        vehicle.category = request.form.get('category')
        vehicle.transmission = request.form.get('transmission')
        vehicle.vehicle_type = request.form.get('vehicle_type')
        vehicle.daily_rate = float(request.form.get('daily_rate'))
        vehicle.number_of_people = int(request.form.get('number_of_people'))
        
        last_revision_date_str = request.form.get('last_revision_date')
        next_revision_date_str = request.form.get('next_revision_date')

        if last_revision_date_str:
            vehicle.last_revision_date = datetime.strptime(last_revision_date_str, '%Y-%m-%d').date()
        else:
            vehicle.last_revision_date = None  # Or some default value

        if next_revision_date_str:
            vehicle.next_revision_date = datetime.strptime(next_revision_date_str, '%Y-%m-%d').date()
        else:
            vehicle.next_revision_date = None  # Or some default value
        vehicle.active = True if request.form.get('active') == 'on' else False

        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.root_path, 'static/img', filename)
                file.save(file_path)
                vehicle.image_url = 'img/'+filename  # Update with new filename

        db.session.commit()
        flash('Vehicle updated successfully.', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin/edit_vehicle.html', vehicle=vehicle)


@main.route("/admin/delete_vehicle/<int:vehicle_id>", methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehicle deleted successfully.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route("/about")
def about():
    return render_template('rental/about.html', page='about')


@main.route("/contact")
def contact():
    return render_template('rental/contact.html', page='contact')

from flask import current_app, Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from datetime import datetime
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Vehicle, Booking
from datetime import datetime, timedelta
from sqlalchemy import desc

rental = Blueprint('rental', __name__)


def checkCarsInspections():
    vehicles = Vehicle.query.all()
    today = datetime.today().date()

    for vehicle in vehicles:
        # Safeguard against None values
        if vehicle.last_revision_date and vehicle.last_revision_date <= (today - timedelta(days=365)):
            vehicle.active = False

        if vehicle.next_revision_date and vehicle.next_revision_date < today:
            vehicle.active = False

        # If the vehicle's status was updated, save the changes
        if not vehicle.active:
            db.session.add(vehicle)

    # Commit all changes at once
    db.session.commit()


@rental.route("/car", methods=['GET'])
def car():
    checkCarsInspections()

    brand = request.args.get('brand', '').strip()
    model = request.args.get('model', '').strip()
    category = request.args.get('category', '').strip()
    min_rate = request.args.get('min_rate')
    max_rate = request.args.get('max_rate')

    query = Vehicle.query

    keyword = request.args.get('keyword', '').strip()

    stop_words = {'of', 'the', 'and', 'a', 'an', 'in', 'on', 'at', 'for', 'with', 'about', 'as', 'by', 'to', 'from'}

    if keyword:
        keywords = keyword.split()
        keywords = [kw for kw in keywords if kw.lower() not in stop_words]  # Filter out stop words
        keyword_filters = []
        for kw in keywords:
            kw = f"%{kw}%"
            keyword_filters.append(
                db.or_(
                    Vehicle.brand.ilike(kw),
                    Vehicle.model.ilike(kw),
                    Vehicle.category.ilike(kw)
                )
            )
        query = query.filter(db.and_(*keyword_filters))
    if brand:
        query = query.filter(Vehicle.brand.ilike(f'%{brand}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    if min_rate:
        query = query.filter(Vehicle.daily_rate >= min_rate)
    if max_rate:
        query = query.filter(Vehicle.daily_rate <= max_rate)
    if category:
        query = query.filter(Vehicle.category.ilike(f'%{category}%'))

    query = query.filter(Vehicle.active == True)
    results = query.all()
    categories = db.session.query(Vehicle.category).distinct().all()
    categories = [category[0].upper() for category in categories]  # Flatten list of tuples
    return render_template('rental/car.html', rows=results, categories=categories, page='car')


@rental.route("/cardetail/<int:id>", methods=['GET'])
def car_detail(id):
    car = Vehicle.query.get_or_404(id)
    related_cars = Vehicle.query.filter(
        Vehicle.category == car.category,
        Vehicle.id != id,
        Vehicle.active == True
    ).limit(4).all()
    return render_template('rental/detail.html', car=car, related_cars=related_cars, page='car-detail')


@rental.route('/check_availability', methods=['POST'])
def check_availability():
    car_id = request.json.get('car_id')
    start_date = datetime.strptime(request.json.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.json.get('end_date'), '%Y-%m-%d')

    car = Vehicle.query.get_or_404(car_id)

    # Fetch all bookings for this car
    bookings = Booking.query.filter_by(car_id=car_id).all()

    for booking in bookings:
        booked_start = datetime.combine(booking.start_date, datetime.min.time())
        booked_end = datetime.combine(booking.end_date, datetime.min.time())
        if start_date <= booked_end and end_date >= booked_start:
            return jsonify({
                'available': False,
                'booked_start': booked_start.strftime('%Y-%m-%d'),
                'booked_end': booked_end.strftime('%Y-%m-%d')
            })

    return jsonify({'available': True})


@rental.route("/booking")
def booking():
    return render_template('rental/booking.html')


@rental.route('/car/search', methods=['GET'])
def search_cars():
    brand = request.args.get('brand', '').strip()
    model = request.args.get('model', '').strip()
    category = request.args.get('category', '').strip()
    min_rate = request.args.get('min_rate')
    max_rate = request.args.get('max_rate')
    keyword = request.args.get('keyword', '').strip()

    query = Vehicle.query

    stop_words = {'of', 'the', 'and', 'a', 'an', 'in', 'on', 'at', 'for', 'with', 'about', 'as', 'by', 'to', 'from'}

    if keyword:
        keywords = keyword.split()
        keywords = [kw for kw in keywords if kw.lower() not in stop_words]  # Filter out stop words
        keyword_filters = []
        for kw in keywords:
            kw = f"%{kw}%"
            keyword_filters.append(
                db.or_(
                    Vehicle.brand.ilike(kw),
                    Vehicle.model.ilike(kw),
                    Vehicle.category.ilike(kw)
                )
            )
        query = query.filter(db.and_(*keyword_filters))
    if brand:
        query = query.filter(Vehicle.brand.ilike(f'%{brand}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    if min_rate:
        query = query.filter(Vehicle.daily_rate >= min_rate)
    if max_rate:
        query = query.filter(Vehicle.daily_rate <= max_rate)
    if category:
        query = query.filter(Vehicle.category.ilike(f'%{category}%'))

    query = query.filter(Vehicle.active == True)
    results = query.all()

    return render_template('rental/car_results.html', rows=results)


@rental.route('/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book(car_id):
    car = Vehicle.query.get_or_404(car_id)
    if request.method == 'POST':
        # Capture booking details
        booking_details = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'mobile_number': request.form['mobile_number'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'special_request': request.form['special_request'],
            'price': request.form['price']
        }

        # Store booking details in session
        session['booking_details'] = booking_details

        # Redirect to payment page
        return redirect(url_for('rental.payment_page', car_id=car_id))

    return render_template('rental/booking.html', car=car, page='book')


@rental.route('/payment_confirmation/<int:booking_id>', methods=['GET'])
@login_required
def payment_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    car = Vehicle.query.get_or_404(booking.car_id)

    car_name = car.brand + " " + car.model

    return render_template('rental/payment_confirmation.html', booking=booking, car_name=car_name,
                           page='payment-confirmation')


@rental.route('/payment/<int:car_id>', methods=['GET', 'POST'])
@login_required
def payment_page(car_id):
    booking_details = session.get('booking_details')

    if request.method == 'POST':
        # Process payment (dummy processing)
        card_number = request.form['card_number']
        card_name = request.form['card_name']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']

        # Validate card details (simple frontend validation can also be added)

        # Retrieve booking details from session
        if not booking_details:
            return redirect(url_for('book', car_id=car_id))

        # Store booking in the database
        booking = Booking(
            user_id=current_user.id,
            car_id=car_id,
            first_name=booking_details['first_name'],
            last_name=booking_details['last_name'],
            email=booking_details['email'],
            mobile_number=booking_details['mobile_number'],
            start_date=booking_details['start_date'],
            end_date=booking_details['end_date'],
            special_request=booking_details['special_request'],
            price=booking_details['price'],
            payment_method='Credit Card'
        )
        db.session.add(booking)
        session.pop('booking_details', None)
        db.session.commit()

        # Redirect to payment confirmation page
        return redirect(url_for('rental.payment_confirmation', booking_id=booking.id))

    return render_template('rental/payment.html', car_id=car_id, price=booking_details['price'], page='payment')


@rental.route('/bookings', methods=['GET'])
@login_required
def bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(desc(Booking.timestamp)).all()
    upcoming_bookings = []
    started_bookings = []
    completed_bookings = []

    # Get the current datetime
    now = datetime.now()

    for booking in user_bookings:
        car = Vehicle.query.get_or_404(booking.car_id)
        car_name = car.brand + " " + car.model

        # Convert booking start and end dates to datetime.datetime for comparison
        start_date = datetime.combine(booking.start_date, datetime.min.time())
        end_date = datetime.combine(booking.end_date, datetime.min.time())

        if start_date > now:
            upcoming_bookings.append({
                'booking': booking,
                'car_name': car_name
            })
        elif start_date <= now <= end_date:
            started_bookings.append({
                'booking': booking,
                'car_name': car_name
            })
        elif now > end_date:
            completed_bookings.append({
                'booking': booking,
                'car_name': car_name
            })

    return render_template('rental/bookings.html',
                           upcoming_bookings=upcoming_bookings,
                           started_bookings=started_bookings,
                           completed_bookings=completed_bookings,
                           page='bookings')


@rental.route('/edit-booking', methods=['POST'])
def edit_booking():
    booking_id = request.form.get('booking_id')
    print("ID:", booking_id)
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    booking = Booking.query.get(booking_id)
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        booking.start_date = start_date
    else:
        start_date = booking.start_date

    # Convert string dates to datetime objects
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Find the booking in the list and update it (replace with actual database update logic)
    booking.end_date = end_date
    db.session.add(booking)
    db.session.commit()

    # Return a JSON response for AJAX request
    return jsonify({
        'success': True,
        'message': 'Booking updated successfully',
        'booking_id': booking_id,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'request': booking.special_request,
        'bill': booking.price,
        'created': booking.timestamp.strftime('%Y-%m-%d'),
    })


@rental.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    booking_id = request.form.get('booking_id')

    # Find the booking in the list and remove it
    booking = Booking.query.get(booking_id)
    db.session.delete(booking)
    db.session.commit()

    # Return a JSON response for AJAX request
    return jsonify({
        'success': True,
        'message': 'Booking canceled successfully'
    })
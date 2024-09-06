# Features
User authentication (registration, login, session management)
Vehicle search and booking system
Admin panel for managing vehicles, users, and bookings
Real-time availability checking
Custom logic for handling dummy payments and vehicle maintenance scheduling
Technologies Used
Flask-Login and Flask-WTF for authentication and form validation
Flask-SQLAlchemy for database management
PostgreSQL as the database management system
Custom Python Logic for booking availability, dummy payments, and vehicle maintenance

# Setup Instructions
# Prerequisites:
Python version 3.7 or higher

PostgreSQL database management system

# Step 1: Install Dependencies
Install the Python packages listed in the requirements.txt file. 

# Step 2: Configure the PostgreSQL Database
Run the commands bellow to create the tables in the database:
flask db init
flask db migrate
flask db upgrade

# Step 3: Replace the placeholders in the config.py file
Replace the placeholders with your specific configuration details:
SECRET_KEY, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_NAME

# Step 4: Run the Application
After setting up the database, start the Flask application. The application will be accessible in your web browser at http://127.0.0.1:5000/.

# Step 5: Access the Admin Panel
The admin account will be automatically created with e-mail:
User: admin@gmail.com
Password: adminpassword
(credentials can be checked in the run.py file)

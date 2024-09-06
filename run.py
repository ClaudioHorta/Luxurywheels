from app import create_app,db,bcrypt
from app.models import Admin

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if not Admin.query.first():
            hashed_password = bcrypt.generate_password_hash('adminpassword').decode('utf-8')
            admin = Admin(name='Admin', email='admin@example.com', password=hashed_password)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)


import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Add the backend directory to the sys.path
sys.path.append(os.getcwd())

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admins' # Fixed table name
    admin_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

def check_db():
    with app.app_context():
        try:
            print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
            admin = Admin.query.first()
            if admin:
                print(f"✅ Found admin: {admin.email}")
            else:
                print("❌ No admin found in database.")
        except Exception as e:
            print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_db()

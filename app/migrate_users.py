from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/hrs"  # Update with your credentials
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    district = Column(String, nullable=True)

# Mock user data
users_db = {
    "district1_user": {"username": "district1_user", "hashed_password": "$2b$12$...", "role": "district_user", "district": "District1"},
    "district1_manager": {"username": "district1_manager", "hashed_password": "$2b$12$...", "role": "district_manager", "district": "District1"},
    "district2_user": {"username": "district2_user", "hashed_password": "$2b$12$...", "role": "district_user", "district": "District2"},
    "district2_manager": {"username": "district2_manager", "hashed_password": "$2b$12$...", "role": "district_manager", "district": "District2"},
    "mainoffice_user": {"username": "mainoffice_user", "hashed_password": "$2b$12$...", "role": "main_office", "district": None}
}

# Replace hashed passwords with actual values from your code
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_db["district1_user"]["hashed_password"] = pwd_context.hash("district1_pass")
users_db["district1_manager"]["hashed_password"] = pwd_context.hash("manager1_pass")
users_db["district2_user"]["hashed_password"] = pwd_context.hash("district2_pass")
users_db["district2_manager"]["hashed_password"] = pwd_context.hash("manager2_pass")
users_db["mainoffice_user"]["hashed_password"] = pwd_context.hash("mainoffice_pass")

# Create tables
Base.metadata.create_all(engine)

# Migrate users
def migrate_users():
    db = SessionLocal()
    try:
        # Check if users already exist to avoid duplicates
        existing_users = db.query(User).all()
        existing_usernames = {user.username for user in existing_users}

        for user_data in users_db.values():
            if user_data["username"] not in existing_usernames:
                new_user = User(
                    username=user_data["username"],
                    hashed_password=user_data["hashed_password"],
                    role=user_data["role"],
                    district=user_data["district"]
                )
                db.add(new_user)
        db.commit()
        print("Users migrated successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users()
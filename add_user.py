from src.models import User, get_password_hash
from rxconfig import config
import reflex as rx
from sqlmodel import create_engine, Session

# Connect to the database
engine = create_engine(config.db_url)

def create_user(username, password):
    with Session(engine) as session:
        # Hash the password
        hashed = get_password_hash(password)
        # Create user
        new_user = User(username=username, password_hash=hashed)
        session.add(new_user)
        session.commit()
        print(f"User '{username}' created successfully!")

if __name__ == "__main__":
    u = input("Enter username: ")
    p = input("Enter password: ")
    create_user(u, p)

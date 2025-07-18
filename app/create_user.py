import getpass
from .db import SessionLocal
from .crud import create_user, get_user_by_username

if __name__ == "__main__":
    db = SessionLocal()
    username = input("New username: ")
    if get_user_by_username(db, username):
        print(f"User '{username}' already exists.")
        db.close()
        exit(1)
    password = getpass.getpass("New password: ")
    user = create_user(db, username, password)
    db.close()
    print(f"User '{username}' created successfully.") 
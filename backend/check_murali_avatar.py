import sys
import os
sys.path.append(os.getcwd())
from app.db.database import SessionLocal
from app.models.models import User

def check_murali():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.name == "murali").first()
        if user:
            print(f"User: {user.name}")
            print(f"Avatar URL: '{user.avatar}'")
        else:
            print("User 'murali' not found.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_murali()

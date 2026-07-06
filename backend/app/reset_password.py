"""
Script for resetting an existing user's password. Since the system does not support
self-service password reset, use this script to set a new password for a forgotten account.

Usage:
    python -m app.reset_password --username alice --password "new-strong-pw"
"""
import argparse

from app.database import SessionLocal
from app import models, security


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == args.username).first()
        if not user:
            print(f"Username {args.username} does not exist, aborting.")
            return

        user.password_hash = security.hash_password(args.password)
        db.commit()
        print(f"Password reset successfully for: {args.username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

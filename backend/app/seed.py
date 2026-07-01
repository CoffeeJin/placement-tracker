"""
Script for manually creating accounts. Since the system does not support open registration,
new student/supervisor accounts are all created through this script.

Usage:
    python -m app.seed --username alice --password "some-strong-pw" --full-name "Alice Chen" --role student
"""
import argparse

from app.database import SessionLocal
from app import models, security


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--email", default=None)
    parser.add_argument("--role", choices=["student", "supervisor", "admin"], default="student")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == args.username).first()
        if existing:
            print(f"Username {args.username} already exists, aborting creation.")
            return

        user = models.User(
            username=args.username,
            password_hash=security.hash_password(args.password),
            full_name=args.full_name,
            email=args.email,
            role=models.UserRole(args.role),
        )
        db.add(user)
        db.commit()
        print(f"Account created successfully: {args.username} ({args.role})")
    finally:
        db.close()


if __name__ == "__main__":
    main()

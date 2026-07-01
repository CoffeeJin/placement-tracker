"""
手动创建账号的脚本。因为系统不开放注册，新增学生/督导账号都通过这个脚本完成。

用法：
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
            print(f"用户名 {args.username} 已存在，取消创建。")
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
        print(f"账号创建成功：{args.username} ({args.role})")
    finally:
        db.close()


if __name__ == "__main__":
    main()

"""
One-time script to create the first Super Admin account.

Run once after database_setup.sql:
    python3 setup_admin.py
"""

import getpass
from app.db import users
from app.security import hash_password

print("=== MaskDetector — Create Super Admin ===\n")

username = input("Username : ").strip()
email    = input("Email    : ").strip()
password = getpass.getpass("Password : ")
confirm  = getpass.getpass("Confirm  : ")

if not username or not email or not password:
    print("Error: all fields are required.")
    raise SystemExit(1)

if password != confirm:
    print("Error: passwords do not match.")
    raise SystemExit(1)

if users.get_by_email(email):
    print(f"Error: an account with email '{email}' already exists.")
    raise SystemExit(1)

users.create(username, email, hash_password(password), "Super Admin")
print(f"\nSuper Admin '{username}' created successfully.")

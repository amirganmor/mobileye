import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://amirganmor:JamesBond007@localhost/mlm")

# User credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword")
USER_USERNAME = os.getenv("USER_USERNAME", "user")
USER_PASSWORD = os.getenv("USER_PASSWORD", "userpassword")
#!/usr/bin/env python3
"""
Create first admin user for production deployment
This script creates a single admin user so you can login and create demo data from UI
"""

import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_first_admin():
    # Get MongoDB connection from environment
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'refsan_repairs')
    
    print(f"Connecting to MongoDB...")
    print(f"URL: {mongo_url}")
    print(f"Database: {db_name}")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": "admin@demo.com"})
    if existing_admin:
        print("✅ Admin user already exists!")
        return
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "admin@demo.com",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "phone": "05551234567",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(admin_user)
    print("✅ Admin user created successfully!")
    print("\nLogin credentials:")
    print("Email: admin@demo.com")
    print("Password: admin123")
    print("\nYou can now login and use the 'Demo Data Oluştur' button in System Management section.")

if __name__ == "__main__":
    asyncio.run(create_first_admin())

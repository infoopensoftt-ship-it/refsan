import asyncio
import motor.motor_asyncio
from datetime import datetime, timezone
from passlib.context import CryptContext
import uuid
import os

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://demo:demo123@cluster0.mongodb.net/refsan_db?retryWrites=true&w=majority")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.refsan_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_demo_data():
    print("🚀 Demo verileri oluşturuluyor...")
    
    # Create demo users
    users = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@demo.com",
            "password": pwd_context.hash("admin123"),
            "full_name": "Admin User",
            "role": "admin",
            "phone": "05551234567",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "teknisyen@demo.com", 
            "password": pwd_context.hash("teknisyen123"),
            "full_name": "Teknisyen Ahmet",
            "role": "teknisyen",
            "phone": "05557654321",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "musteri@demo.com",
            "password": pwd_context.hash("musteri123"), 
            "full_name": "Müşteri Mehmet",
            "role": "musteri",
            "phone": "05559876543",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.users.insert_many(users)
    print("✅ Demo kullanıcılar oluşturuldu")
    
    # Create demo customers
    customers = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Ankara Seramik A.Ş.",
            "email": "info@ankaraseramik.com",
            "phone": "0312 456 7890", 
            "address": "Ostim OSB, Ankara",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "İstanbul Çini Fabrikası",
            "email": "uretim@istanbulcini.com",
            "phone": "0216 345 6789",
            "address": "Kartal Sanayi Sitesi, İstanbul", 
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.customers.insert_many(customers)
    print("✅ Demo müşteriler oluşturuldu")
    
    # Create demo repairs
    repairs = [
        {
            "id": str(uuid.uuid4()),
            "customer_id": customers[0]["id"],
            "customer_name": customers[0]["full_name"],
            "device_type": "Seramik Fırını",
            "brand": "Refsan",
            "model": "RF-2500",
            "description": "Fırın sıcaklık kontrolü arızalı. 1200°C'ye çıkarken ani düşüş yaşanıyor.",
            "status": "beklemede",
            "priority": "yuksek",
            "cost_estimate": 15000.0,
            "created_by": users[0]["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        }
    ]
    
    await db.repairs.insert_many(repairs)
    print("✅ Demo arıza kayıtları oluşturuldu")
    
    print("\n🎉 Demo veriler başarıyla oluşturuldu!")
    print("\n📋 Test Hesapları:")
    print("Admin: admin@demo.com / admin123")
    print("Teknisyen: teknisyen@demo.com / teknisyen123") 
    print("Müşteri: musteri@demo.com / musteri123")

if __name__ == "__main__":
    asyncio.run(create_demo_data())
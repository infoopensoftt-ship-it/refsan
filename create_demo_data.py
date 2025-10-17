#!/usr/bin/env python3
"""
Demo verileri oluşturma scripti
"""
import requests
import json

BACKEND_URL = "https://refsan-repairs.preview.emergentagent.com/api"

def create_demo_users():
    """Demo kullanıcıları oluştur"""
    users = [
        {
            "email": "admin@demo.com",
            "password": "admin123",
            "full_name": "Admin Kullanıcı",
            "role": "admin",
            "phone": "05551234567"
        },
        {
            "email": "teknisyen@demo.com", 
            "password": "teknisyen123",
            "full_name": "Ahmet Teknisyen",
            "role": "teknisyen",
            "phone": "05551234568"
        },
        {
            "email": "musteri@demo.com",
            "password": "musteri123", 
            "full_name": "Ayşe Müşteri",
            "role": "musteri",
            "phone": "05551234569"
        }
    ]
    
    for user in users:
        try:
            response = requests.post(f"{BACKEND_URL}/auth/register", json=user)
            if response.status_code == 200:
                print(f"✅ {user['full_name']} oluşturuldu")
            else:
                print(f"❌ {user['full_name']} oluşturulamadı: {response.text}")
        except Exception as e:
            print(f"❌ Hata: {e}")

def create_demo_customers():
    """Demo müşteriler oluştur"""
    # Admin olarak giriş yap
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "admin@demo.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print("❌ Admin girişi başarısız")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    customers = [
        {
            "full_name": "Ege Karo Ltd. Şti.",
            "email": "info@egekaro.com",
            "phone": "0274 789 0123",
            "address": "Kütahya Organize Sanayi Bölgesi, Kütahya"
        },
        {
            "full_name": "Manisa Seramik A.Ş.",
            "email": "servis@manisaseramik.com", 
            "phone": "0236 234 5678",
            "address": "Manisa Akhisar Organize Sanayi, Manisa"
        },
        {
            "full_name": "Çanakkale Çini Atölyesi",
            "email": "atolye@canakkalecini.com",
            "phone": "0286 456 7890", 
            "address": "Çanakkale Merkez, Çanakkale"
        },
        {
            "full_name": "Bursa Fayans Fabrikası",
            "email": "teknik@bursafayans.com",
            "phone": "0224 567 8901",
            "address": "Bursa İnegöl Organize Sanayi, Bursa"
        },
        {
            "full_name": "İzmir Porselen San. Tic.",
            "email": "bakim@izmirporselen.com",
            "phone": "0232 678 9012",
            "address": "İzmir Kemalpaşa Organize Sanayi, İzmir"
        }
    ]
    
    for customer in customers:
        try:
            response = requests.post(f"{BACKEND_URL}/customers", json=customer, headers=headers)
            if response.status_code == 200:
                print(f"✅ Müşteri {customer['full_name']} oluşturuldu")
            else:
                print(f"❌ Müşteri {customer['full_name']} oluşturulamadı: {response.text}")
        except Exception as e:
            print(f"❌ Müşteri oluşturma hatası: {e}")

def create_demo_repairs():
    """Demo arıza kayıtları oluştur"""
    # Admin olarak giriş yap
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "admin@demo.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print("❌ Admin girişi başarısız")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Müşterileri al
    customers_response = requests.get(f"{BACKEND_URL}/customers", headers=headers)
    if customers_response.status_code != 200:
        print("❌ Müşteriler alınamadı")
        return
    
    customers = customers_response.json()
    
    if not customers:
        print("❌ Hiç müşteri bulunamadı")
        return
    
    repairs = [
        {
            "customer_id": customers[0]["id"],
            "device_type": "iPhone",
            "brand": "Apple", 
            "model": "14 Pro",
            "description": "Ekran çatlamış, dokunmatik çalışmıyor",
            "priority": "yuksek",
            "cost_estimate": 1500.0
        },
        {
            "customer_id": customers[1]["id"],
            "device_type": "Laptop",
            "brand": "Dell",
            "model": "XPS 13",
            "description": "Açılmıyor, güç sorunu var",
            "priority": "orta", 
            "cost_estimate": 800.0
        },
        {
            "customer_id": customers[2]["id"],
            "device_type": "Samsung",
            "brand": "Samsung",
            "model": "Galaxy S23",
            "description": "Batarya hızla bitiyor",
            "priority": "dusuk",
            "cost_estimate": 300.0
        }
    ]
    
    for repair in repairs:
        try:
            response = requests.post(f"{BACKEND_URL}/repairs", json=repair, headers=headers)
            if response.status_code == 200:
                print(f"✅ Arıza kaydı {repair['device_type']} - {repair['brand']} {repair['model']} oluşturuldu")
            else:
                print(f"❌ Arıza kaydı oluşturulamadı: {response.text}")
        except Exception as e:
            print(f"❌ Arıza kaydı oluşturma hatası: {e}")

if __name__ == "__main__":
    print("🚀 Demo verileri oluşturuluyor...\n")
    
    print("👥 Kullanıcılar oluşturuluyor...")
    create_demo_users()
    
    print("\n👤 Müşteriler oluşturuluyor...")
    create_demo_customers()
    
    print("\n🔧 Arıza kayıtları oluşturuluyor...")
    create_demo_repairs()
    
    print("\n✅ Demo verileri oluşturuldu!")
    print("\n📋 Demo hesaplar:")
    print("Admin: admin@demo.com / admin123")
    print("Teknisyen: teknisyen@demo.com / teknisyen123") 
    print("Müşteri: musteri@demo.com / musteri123")
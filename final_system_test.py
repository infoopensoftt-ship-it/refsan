#!/usr/bin/env python3

import requests
import json

def test_system_management_endpoints():
    """Test all system management endpoints comprehensively"""
    print("🚀 Final System Management Endpoints Test")
    print("=" * 60)
    
    base_url = "https://techfix-portal-3.preview.emergentagent.com/api"
    
    # Login as admin
    login_data = {'email': 'admin@demo.com', 'password': 'admin123'}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = response.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
    print("✅ Admin login successful")
    
    # Create test data
    print("\n📝 Creating test data...")
    customer_data = {
        "full_name": "Final Test Customer",
        "email": "finaltest@test.com",
        "phone": "05551234567"
    }
    
    customer_resp = requests.post(f"{base_url}/customers", json=customer_data, headers=admin_headers)
    if customer_resp.status_code == 200:
        customer_id = customer_resp.json()['id']
        
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Test Device",
            "brand": "Test Brand",
            "model": "Test Model",
            "description": "Test repair",
            "priority": "orta"
        }
        
        repair_resp = requests.post(f"{base_url}/repairs", json=repair_data, headers=admin_headers)
        if repair_resp.status_code == 200:
            print("✅ Test data created successfully")
        else:
            print("❌ Failed to create test repair")
    else:
        print("❌ Failed to create test customer")
    
    # Test system management endpoints
    print("\n🔧 Testing System Management Endpoints:")
    
    endpoints = [
        ("DELETE", "admin/repairs/delete-all", "Delete all repairs"),
        ("DELETE", "admin/customers/delete-all", "Delete all customers"),
        ("DELETE", "admin/system/reset", "System reset"),
        ("POST", "admin/demo/create-data", "Create demo data")
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        print(f"\n🔍 Testing {description}...")
        
        if method == "DELETE":
            resp = requests.delete(f"{base_url}/{endpoint}", headers=admin_headers)
        else:
            resp = requests.post(f"{base_url}/{endpoint}", headers=admin_headers)
        
        if resp.status_code == 200:
            print(f"✅ {description}: PASSED")
            try:
                data = resp.json()
                if 'message' in data:
                    print(f"   📝 {data['message']}")
                if 'customers_created' in data:
                    print(f"   📊 Created {data['customers_created']} customers, {data['repairs_created']} repairs")
            except:
                pass
            results.append(True)
        else:
            print(f"❌ {description}: FAILED ({resp.status_code})")
            try:
                print(f"   Error: {resp.json()}")
            except:
                print(f"   Error: {resp.text}")
            results.append(False)
    
    # Test role-based access control
    print("\n🔐 Testing Role-Based Access Control:")
    
    # Login as technician
    tech_login = {'email': 'teknisyen@demo.com', 'password': 'teknisyen123'}
    tech_resp = requests.post(f"{base_url}/auth/login", json=tech_login)
    
    if tech_resp.status_code == 200:
        tech_token = tech_resp.json()['access_token']
        tech_headers = {'Authorization': f'Bearer {tech_token}', 'Content-Type': 'application/json'}
        print("✅ Technician login successful")
        
        # Test that technician cannot access admin endpoints
        access_denied_count = 0
        for method, endpoint, description in endpoints:
            if method == "DELETE":
                resp = requests.delete(f"{base_url}/{endpoint}", headers=tech_headers)
            else:
                resp = requests.post(f"{base_url}/{endpoint}", headers=tech_headers)
            
            if resp.status_code == 403:
                access_denied_count += 1
        
        if access_denied_count == len(endpoints):
            print("✅ Role-based access control: PASSED")
            results.append(True)
        else:
            print(f"❌ Role-based access control: FAILED ({access_denied_count}/{len(endpoints)} properly denied)")
            results.append(False)
    else:
        print("❌ Technician login failed")
        results.append(False)
    
    # Validate demo data
    print("\n🏭 Validating Demo Data:")
    
    # Get customers and repairs to validate content
    customers_resp = requests.get(f"{base_url}/customers", headers=admin_headers)
    repairs_resp = requests.get(f"{base_url}/repairs", headers=admin_headers)
    
    if customers_resp.status_code == 200 and repairs_resp.status_code == 200:
        customers = customers_resp.json()
        repairs = repairs_resp.json()
        
        # Check for ceramic industry customers
        ceramic_customers = sum(1 for c in customers 
                              if any(keyword in c.get('full_name', '').lower() 
                                   for keyword in ['seramik', 'çini', 'karo', 'porselen']))
        
        # Check for Refsan repairs
        refsan_repairs = sum(1 for r in repairs 
                           if 'refsan' in r.get('brand', '').lower())
        
        print(f"   📊 Found {ceramic_customers} ceramic industry customers")
        print(f"   📊 Found {refsan_repairs} Refsan brand repairs")
        
        if ceramic_customers >= 3 and refsan_repairs >= 3:
            print("✅ Demo data validation: PASSED")
            results.append(True)
        else:
            print("❌ Demo data validation: FAILED")
            results.append(False)
    else:
        print("❌ Could not retrieve data for validation")
        results.append(False)
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    test_names = [
        "Delete all repairs",
        "Delete all customers", 
        "System reset",
        "Create demo data",
        "Role-based access control",
        "Demo data validation"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEM MANAGEMENT ENDPOINTS WORKING PERFECTLY!")
        return True
    else:
        print("⚠️  Some tests failed - see details above")
        return False

if __name__ == "__main__":
    success = test_system_management_endpoints()
    exit(0 if success else 1)
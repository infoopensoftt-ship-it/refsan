#!/usr/bin/env python3

import requests
import json

class SystemManagementTester:
    def __init__(self):
        self.base_url = "https://refsan-repairs.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        
    def login_admin(self):
        """Login as admin to get token"""
        login_data = {
            'email': 'admin@demo.com',
            'password': 'admin123'
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            print("✅ Admin login successful")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return False
    
    def test_endpoint(self, name, method, endpoint, expected_status=200, data=None):
        """Test a single endpoint"""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            
            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if 'message' in response_data:
                        print(f"   📝 {response_data['message']}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
    
    def create_test_data(self):
        """Create some test data for deletion tests"""
        print("\n📝 Creating test data...")
        
        # Create test customers
        for i in range(2):
            customer_data = {
                "full_name": f"System Test Customer {i+1}",
                "email": f"systemtest{i+1}@test.com",
                "phone": f"055512345{i+1}0",
                "address": f"System Test Address {i+1}"
            }
            
            success, customer = self.test_endpoint(
                f"Create test customer {i+1}",
                "POST",
                "customers",
                200,
                customer_data
            )
            
            if success:
                # Create a repair for this customer
                repair_data = {
                    "customer_id": customer.get('id'),
                    "device_type": f"Test Device {i+1}",
                    "brand": "Test Brand",
                    "model": f"Model {i+1}",
                    "description": f"Test repair description {i+1}",
                    "priority": "orta"
                }
                
                self.test_endpoint(
                    f"Create test repair {i+1}",
                    "POST",
                    "repairs",
                    200,
                    repair_data
                )
    
    def test_system_management_endpoints(self):
        """Test all system management endpoints"""
        print("\n🔧 Testing System Management Endpoints")
        
        # Create test data first
        self.create_test_data()
        
        # Test 1: DELETE /api/admin/repairs/delete-all
        success1, response1 = self.test_endpoint(
            "Delete all repair records",
            "DELETE",
            "admin/repairs/delete-all",
            200
        )
        
        # Test 2: DELETE /api/admin/customers/delete-all  
        success2, response2 = self.test_endpoint(
            "Delete all customers and their repairs",
            "DELETE",
            "admin/customers/delete-all",
            200
        )
        
        # Test 3: DELETE /api/admin/system/reset
        success3, response3 = self.test_endpoint(
            "Reset entire system except admin users",
            "DELETE",
            "admin/system/reset",
            200
        )
        
        # Test 4: POST /api/admin/demo/create-data
        success4, response4 = self.test_endpoint(
            "Create Refsan Türkiye demo data",
            "POST",
            "admin/demo/create-data",
            200
        )
        
        if success4:
            customers_created = response4.get('customers_created', 0)
            repairs_created = response4.get('repairs_created', 0)
            print(f"   📊 Demo data: {customers_created} customers, {repairs_created} repairs")
        
        return success1, success2, success3, success4
    
    def test_role_access_control(self):
        """Test that non-admin users cannot access system management endpoints"""
        print("\n🔐 Testing Role-Based Access Control")
        
        # Test with technician credentials
        login_data = {
            'email': 'teknisyen@demo.com',
            'password': 'teknisyen123'
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            tech_token = response.json()['access_token']
            print("✅ Technician login successful")
            
            # Test access to system management endpoints (should fail with 403)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {tech_token}'
            }
            
            endpoints_to_test = [
                ("admin/repairs/delete-all", "DELETE"),
                ("admin/customers/delete-all", "DELETE"),
                ("admin/system/reset", "DELETE"),
                ("admin/demo/create-data", "POST")
            ]
            
            all_forbidden = True
            for endpoint, method in endpoints_to_test:
                url = f"{self.api_url}/{endpoint}"
                
                if method == 'DELETE':
                    response = requests.delete(url, headers=headers, timeout=10)
                else:
                    response = requests.post(url, headers=headers, timeout=10)
                
                if response.status_code == 403:
                    print(f"✅ Technician correctly denied access to {endpoint}")
                else:
                    print(f"❌ Technician should be denied access to {endpoint}, got {response.status_code}")
                    all_forbidden = False
            
            return all_forbidden
        else:
            print(f"❌ Technician login failed: {response.status_code}")
            return False
    
    def validate_demo_data(self):
        """Validate that demo data contains proper Refsan ceramic machinery examples"""
        print("\n🏭 Validating Demo Data Content")
        
        # Get customers
        success, customers = self.test_endpoint(
            "Get customers for validation",
            "GET",
            "customers",
            200
        )
        
        if not success:
            return False
        
        # Check for ceramic industry names
        ceramic_keywords = ['seramik', 'çini', 'karo', 'porselen']
        ceramic_customers = 0
        
        for customer in customers:
            customer_name = customer.get('full_name', '').lower()
            if any(keyword in customer_name for keyword in ceramic_keywords):
                ceramic_customers += 1
                print(f"   ✅ Found ceramic industry customer: {customer.get('full_name')}")
        
        # Get repairs
        success, repairs = self.test_endpoint(
            "Get repairs for validation",
            "GET",
            "repairs",
            200
        )
        
        if not success:
            return False
        
        # Check for Refsan brand and ceramic machinery
        refsan_repairs = 0
        ceramic_devices = 0
        
        for repair in repairs:
            brand = repair.get('brand', '').lower()
            device_type = repair.get('device_type', '').lower()
            
            if 'refsan' in brand:
                refsan_repairs += 1
                print(f"   ✅ Found Refsan repair: {repair.get('device_type')} {repair.get('brand')} {repair.get('model')}")
            
            ceramic_device_types = ['seramik', 'çini', 'karo', 'porselen', 'fırın', 'pres', 'kesim', 'kalıplama', 'sırlama']
            if any(device_keyword in device_type for device_keyword in ceramic_device_types):
                ceramic_devices += 1
        
        print(f"   📊 Validation Results:")
        print(f"   - Ceramic industry customers: {ceramic_customers}")
        print(f"   - Refsan brand repairs: {refsan_repairs}")
        print(f"   - Ceramic machinery repairs: {ceramic_devices}")
        
        # Validation criteria
        validation_success = (
            ceramic_customers >= 3 and
            refsan_repairs >= 3 and
            ceramic_devices >= 3
        )
        
        if validation_success:
            print("   ✅ Demo data validation PASSED")
        else:
            print("   ❌ Demo data validation FAILED")
        
        return validation_success

def main():
    print("🚀 System Management Endpoints Test")
    print("=" * 50)
    
    tester = SystemManagementTester()
    
    # Login as admin
    if not tester.login_admin():
        print("❌ Cannot proceed without admin login")
        return 1
    
    # Test system management endpoints
    success1, success2, success3, success4 = tester.test_system_management_endpoints()
    
    # Test role-based access control
    access_control_success = tester.test_role_access_control()
    
    # Validate demo data (if demo creation was successful)
    demo_validation_success = True
    if success4:
        demo_validation_success = tester.validate_demo_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SYSTEM MANAGEMENT TEST RESULTS")
    print("=" * 50)
    
    results = [
        ("Delete all repairs", success1),
        ("Delete all customers", success2),
        ("System reset", success3),
        ("Create demo data", success4),
        ("Role-based access control", access_control_success),
        ("Demo data validation", demo_validation_success)
    ]
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
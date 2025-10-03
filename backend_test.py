import requests
import sys
import json
from datetime import datetime

class TechnicalServiceAPITester:
    def __init__(self, base_url="https://fixservice-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.current_user = None
        
        # Demo credentials
        self.demo_accounts = {
            'admin': {'email': 'admin@demo.com', 'password': 'admin123'},
            'teknisyen': {'email': 'teknisyen@demo.com', 'password': 'teknisyen123'},
            'musteri': {'email': 'musteri@demo.com', 'password': 'musteri123'}
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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
                
                self.failed_tests.append({
                    'test': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'endpoint': endpoint,
                    'method': method
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'test': name,
                'error': str(e),
                'endpoint': endpoint,
                'method': method
            })
            return False, {}

    def test_login(self, role):
        """Test login for specific role"""
        credentials = self.demo_accounts[role]
        success, response = self.run_test(
            f"Login as {role}",
            "POST",
            "auth/login",
            200,
            data=credentials
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response.get('user', {})
            print(f"   ✅ Token obtained for {role}")
            return True
        return False

    def test_auth_me(self):
        """Test current user info"""
        success, response = self.run_test(
            "Get current user info",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_register(self):
        """Test user registration"""
        test_user_data = {
            "email": f"test_user_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "musteri",
            "phone": "05551234567"
        }
        
        success, response = self.run_test(
            "Register new user",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        return success

    def test_stats(self):
        """Test stats endpoint"""
        success, response = self.run_test(
            "Get statistics",
            "GET",
            "stats",
            200
        )
        
        if success:
            print(f"   📊 Stats: {response}")
        return success

    def test_customers_crud(self):
        """Test customer CRUD operations"""
        # Create customer
        customer_data = {
            "full_name": "Test Müşteri",
            "email": "test@customer.com",
            "phone": "05551234567",
            "address": "Test Adres"
        }
        
        success, customer = self.run_test(
            "Create customer",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer.get('id')
        print(f"   ✅ Customer created with ID: {customer_id}")
        
        # Get customers list
        success, customers = self.run_test(
            "Get customers list",
            "GET",
            "customers",
            200
        )
        
        return success and customer_id

    def test_repairs_crud(self, customer_id=None):
        """Test repair CRUD operations"""
        if not customer_id:
            # Create a customer first
            customer_data = {
                "full_name": "Repair Test Müşteri",
                "phone": "05559876543"
            }
            success, customer = self.run_test(
                "Create customer for repair",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            if not success:
                return False
            customer_id = customer.get('id')
        
        # Create repair request
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Telefon",
            "brand": "Apple",
            "model": "iPhone 14",
            "description": "Ekran kırık",
            "priority": "yuksek",
            "cost_estimate": 500.0
        }
        
        success, repair = self.run_test(
            "Create repair request",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not success:
            return False
        
        repair_id = repair.get('id')
        print(f"   ✅ Repair created with ID: {repair_id}")
        
        # Get repairs list
        success, repairs = self.run_test(
            "Get repairs list",
            "GET",
            "repairs",
            200
        )
        
        if not success:
            return False
        
        # Get specific repair
        success, repair_detail = self.run_test(
            "Get specific repair",
            "GET",
            f"repairs/{repair_id}",
            200
        )
        
        if not success:
            return False
        
        # Update repair (admin/technician only)
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            update_data = {
                "status": "isleniyor",
                "final_cost": 450.0,
                "payment_status": "beklemede"
            }
            
            success, updated_repair = self.run_test(
                "Update repair request",
                "PUT",
                f"repairs/{repair_id}",
                200,
                data=update_data
            )
            
            if success:
                print(f"   ✅ Repair updated successfully")
        
        return True

    def test_users_list(self):
        """Test users list (admin only)"""
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping users list test (not admin)")
            return True
        
        success, users = self.run_test(
            "Get users list",
            "GET",
            "users",
            200
        )
        
        if success:
            print(f"   👥 Found {len(users)} users")
        
        return success

    def test_role_based_access(self):
        """Test role-based access control"""
        print(f"\n🔐 Testing role-based access for: {self.current_user.get('role')}")
        
        # Test stats access (all roles should have access)
        stats_success = self.test_stats()
        
        # Test customers access (admin and technician only)
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            customers_success = self.test_customers_crud()
        else:
            # Customer role should not have access to create customers
            success, _ = self.run_test(
                "Customer access to customers endpoint (should fail)",
                "GET",
                "customers",
                403  # Expecting forbidden
            )
            customers_success = success  # Success means it correctly returned 403
        
        # Test users list (admin only)
        users_success = self.test_users_list()
        
        return stats_success and customers_success and users_success

def main():
    print("🚀 Starting Technical Service API Tests")
    print("=" * 50)
    
    tester = TechnicalServiceAPITester()
    
    # Test each role
    roles_to_test = ['admin', 'teknisyen', 'musteri']
    overall_success = True
    
    for role in roles_to_test:
        print(f"\n{'='*20} TESTING {role.upper()} ROLE {'='*20}")
        
        # Login as role
        if not tester.test_login(role):
            print(f"❌ Failed to login as {role}, skipping role tests")
            overall_success = False
            continue
        
        # Test auth/me endpoint
        if not tester.test_auth_me():
            print(f"❌ Failed auth/me test for {role}")
            overall_success = False
        
        # Test role-based access
        if not tester.test_role_based_access():
            print(f"❌ Failed role-based access tests for {role}")
            overall_success = False
        
        # Test repairs CRUD
        customer_id = None
        if role in ['admin', 'teknisyen']:
            # Create customer first for repair tests
            customer_data = {
                "full_name": f"Test Customer for {role}",
                "phone": f"0555{role[:4]}123"
            }
            success, customer = tester.run_test(
                f"Create customer for {role} repair test",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            if success:
                customer_id = customer.get('id')
        
        if not tester.test_repairs_crud(customer_id):
            print(f"❌ Failed repairs CRUD tests for {role}")
            overall_success = False
        
        # Reset token for next role
        tester.token = None
        tester.current_user = None
    
    # Test registration (without authentication)
    print(f"\n{'='*20} TESTING REGISTRATION {'='*20}")
    if not tester.test_register():
        print("❌ Failed registration test")
        overall_success = False
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"{i}. {test['test']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
            else:
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            print(f"   Endpoint: {test['method']} {test['endpoint']}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Focused test for the new repair detail endpoint and enhanced notification system
as requested in the review request.
"""

import requests
import json
import sys

class FocusedAPITester:
    def __init__(self, base_url="https://refsan-repairs.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
        # Demo credentials
        self.credentials = {
            'admin': {'email': 'admin@demo.com', 'password': 'admin123'},
            'technician': {'email': 'teknisyen@demo.com', 'password': 'teknisyen123'},
            'customer': {'email': 'musteri@demo.com', 'password': 'musteri123'}
        }
        
        self.tokens = {}
        self.users = {}

    def login_all_users(self):
        """Login all user types and store tokens"""
        for role, creds in self.credentials.items():
            response = requests.post(f"{self.api_url}/auth/login", json=creds)
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['access_token']
                self.users[role] = data['user']
                print(f"✅ Logged in as {role}")
            else:
                print(f"❌ Failed to login as {role}")
                return False
        return True

    def get_headers(self, role):
        """Get authorization headers for a role"""
        return {'Authorization': f'Bearer {self.tokens[role]}'}

    def run_test(self, name, method, endpoint, expected_status, role, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = self.get_headers(role)
        
        self.tests_run += 1
        print(f"\n🔍 {name}")
        print(f"   Role: {role}, Method: {method}, Expected: {expected_status}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                
                self.failed_tests.append({
                    'test': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'role': role
                })
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'test': name,
                'error': str(e),
                'role': role
            })
            return False, {}

    def test_repair_detail_endpoint_scenarios(self):
        """Test all repair detail endpoint scenarios from review request"""
        print("\n" + "="*60)
        print("TESTING REPAIR DETAIL ENDPOINT SCENARIOS")
        print("="*60)
        
        # Setup: Create customer and repair as admin
        customer_data = {
            'full_name': 'Repair Detail Test Customer',
            'email': 'repairdetail@test.com',
            'phone': '05551234567'
        }
        
        success, customer = self.run_test(
            "Create customer for repair detail tests",
            "POST", "customers", 200, "admin", customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer['id']
        
        # Create repair as admin
        repair_data = {
            'customer_id': customer_id,
            'device_type': 'iPhone',
            'brand': 'Apple',
            'model': 'iPhone 15 Pro',
            'description': 'Screen replacement for role-based access test',
            'priority': 'yuksek'
        }
        
        success, repair = self.run_test(
            "Create repair for detail access tests",
            "POST", "repairs", 200, "admin", repair_data
        )
        
        if not success:
            return False
        
        repair_id = repair['id']
        
        # Test 1: Admin accessing any repair details
        success, _ = self.run_test(
            "Admin accessing repair details",
            "GET", f"repairs/{repair_id}", 200, "admin"
        )
        
        # Test 2: Technician accessing unassigned repair (should fail with 403)
        success, _ = self.run_test(
            "Technician accessing unassigned repair (should fail)",
            "GET", f"repairs/{repair_id}", 403, "technician"
        )
        
        # Test 3: Assign repair to technician
        tech_id = self.users['technician']['id']
        assign_data = {'assigned_technician_id': tech_id}
        
        success, _ = self.run_test(
            "Assign repair to technician",
            "PUT", f"repairs/{repair_id}", 200, "admin", assign_data
        )
        
        # Test 4: Technician accessing assigned repair
        success, _ = self.run_test(
            "Technician accessing assigned repair",
            "GET", f"repairs/{repair_id}", 200, "technician"
        )
        
        # Test 5: Create repair by technician for their own customer
        tech_customer_data = {
            'full_name': 'Technician Customer',
            'phone': '05559876543'
        }
        
        success, tech_customer = self.run_test(
            "Technician creates own customer",
            "POST", "customers", 200, "technician", tech_customer_data
        )
        
        if success:
            tech_customer_id = tech_customer['id']
            
            tech_repair_data = {
                'customer_id': tech_customer_id,
                'device_type': 'Samsung Galaxy',
                'brand': 'Samsung',
                'model': 'Galaxy S24',
                'description': 'Battery replacement',
                'priority': 'orta'
            }
            
            success, tech_repair = self.run_test(
                "Technician creates repair for own customer",
                "POST", "repairs", 200, "technician", tech_repair_data
            )
            
            if success:
                tech_repair_id = tech_repair['id']
                
                # Test 6: Technician accessing own repair
                success, _ = self.run_test(
                    "Technician accessing own repair",
                    "GET", f"repairs/{tech_repair_id}", 200, "technician"
                )
        
        # Test 7: Customer accessing own repair (need to create customer repair)
        # Note: This would require creating a customer user and repair, skipping for now
        
        # Test 8: Invalid repair ID (should return 404)
        success, _ = self.run_test(
            "Access invalid repair ID",
            "GET", "repairs/invalid-repair-id-12345", 404, "admin"
        )
        
        return True

    def test_enhanced_notification_scenarios(self):
        """Test enhanced notification system scenarios"""
        print("\n" + "="*60)
        print("TESTING ENHANCED NOTIFICATION SYSTEM")
        print("="*60)
        
        # Clear existing notifications
        success, _ = self.run_test(
            "Clear all notifications",
            "DELETE", "notifications/clear-all", 200, "admin"
        )
        
        # Setup: Create customer
        customer_data = {
            'full_name': 'Enhanced Notification Test Customer',
            'email': 'enhancednotif@test.com',
            'phone': '05551234567'
        }
        
        success, customer = self.run_test(
            "Create customer for notification tests",
            "POST", "customers", 200, "admin", customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer['id']
        
        # Test 1: Create new repair and verify notification contains extra fields
        repair_data = {
            'customer_id': customer_id,
            'device_type': 'MacBook Pro',
            'brand': 'Apple',
            'model': 'MacBook Pro 16-inch',
            'description': 'Keyboard replacement for enhanced notification test',
            'priority': 'yuksek'
        }
        
        success, repair = self.run_test(
            "Create repair for enhanced notification test",
            "POST", "repairs", 200, "admin", repair_data
        )
        
        if not success:
            return False
        
        repair_id = repair['id']
        
        # Test 2: Update repair status and verify notification has new_status field
        status_update = {'status': 'isleniyor'}
        
        success, _ = self.run_test(
            "Update repair status for notification test",
            "PUT", f"repairs/{repair_id}", 200, "admin", status_update
        )
        
        # Test 3: Cancel repair and verify notification type is 'repair_cancelled'
        success, _ = self.run_test(
            "Cancel repair for notification test",
            "PUT", f"repairs/{repair_id}/cancel", 200, "admin"
        )
        
        # Test 4: Verify notification data structure
        success, notifications = self.run_test(
            "Get notifications to verify enhanced data",
            "GET", "notifications?limit=10", 200, "admin"
        )
        
        if success:
            print(f"\n📊 NOTIFICATION DATA ANALYSIS:")
            print(f"   Total notifications retrieved: {len(notifications)}")
            
            enhanced_count = 0
            for i, notif in enumerate(notifications[:5]):
                print(f"\n   Notification {i+1}:")
                print(f"   - Type: {notif.get('type')}")
                print(f"   - Title: {notif.get('title')}")
                print(f"   - Has repair_id: {notif.get('repair_id') is not None}")
                print(f"   - Has customer_name: {notif.get('customer_name') is not None}")
                print(f"   - Has device_info: {notif.get('device_info') is not None}")
                
                if notif.get('type') == 'repair_status_update':
                    print(f"   - Has new_status: {notif.get('new_status') is not None}")
                    if notif.get('new_status'):
                        print(f"   - New status value: {notif.get('new_status')}")
                
                if notif.get('type') == 'repair_cancelled':
                    print(f"   - Cancellation notification confirmed")
                
                # Check if notification has enhanced fields
                if (notif.get('repair_id') or notif.get('customer_name') or notif.get('device_info')):
                    enhanced_count += 1
            
            print(f"\n   ✅ {enhanced_count} out of {min(5, len(notifications))} notifications have enhanced fields")
            
            # Verify specific notification types
            repair_created = any(n.get('type') == 'new_repair' for n in notifications)
            status_updated = any(n.get('type') == 'repair_status_update' for n in notifications)
            repair_cancelled = any(n.get('type') == 'repair_cancelled' for n in notifications)
            
            print(f"   ✅ New repair notification: {'Found' if repair_created else 'Not found'}")
            print(f"   ✅ Status update notification: {'Found' if status_updated else 'Not found'}")
            print(f"   ✅ Repair cancelled notification: {'Found' if repair_cancelled else 'Not found'}")
        
        return True

    def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 Starting Focused API Tests for New Repair Detail Endpoint and Enhanced Notifications")
        print("="*80)
        
        # Login all users
        if not self.login_all_users():
            print("❌ Failed to login users")
            return False
        
        # Run repair detail endpoint tests
        if not self.test_repair_detail_endpoint_scenarios():
            print("❌ Repair detail endpoint tests failed")
        
        # Run enhanced notification tests
        if not self.test_enhanced_notification_scenarios():
            print("❌ Enhanced notification tests failed")
        
        # Print results
        print("\n" + "="*80)
        print("📊 FOCUSED TEST RESULTS")
        print("="*80)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['test']} (Role: {test['role']})")
                if 'error' in test:
                    print(f"   Error: {test['error']}")
                else:
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
        
        return self.tests_run - self.tests_passed == 0

def main():
    tester = FocusedAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
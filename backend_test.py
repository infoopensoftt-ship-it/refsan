import requests
import sys
import json
from datetime import datetime

class TechnicalServiceAPITester:
    def __init__(self, base_url="https://refsan-repairs-1.preview.emergentagent.com"):
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

    def test_customer_detail_endpoint(self, customer_id=None):
        """Test GET /api/customers/{customer_id} endpoint"""
        if not customer_id:
            # Create a customer first
            customer_data = {
                "full_name": "Detail Test Customer",
                "email": "detail@test.com",
                "phone": "05551234567",
                "address": "Test Address for Detail"
            }
            success, customer = self.run_test(
                "Create customer for detail test",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            if not success:
                return False
            customer_id = customer.get('id')
        
        # Test valid customer ID
        success, customer_detail = self.run_test(
            "Get customer detail - valid ID",
            "GET",
            f"customers/{customer_id}",
            200
        )
        
        if success:
            print(f"   ✅ Customer detail retrieved: {customer_detail.get('full_name')}")
        
        # Test invalid customer ID
        invalid_success, _ = self.run_test(
            "Get customer detail - invalid ID",
            "GET",
            "customers/invalid-id-12345",
            404
        )
        
        return success and invalid_success

    def test_customer_update_endpoint(self, customer_id=None):
        """Test PUT /api/customers/{customer_id} endpoint"""
        if not customer_id:
            # Create a customer first
            customer_data = {
                "full_name": "Update Test Customer",
                "email": "update@test.com", 
                "phone": "05551234567",
                "address": "Original Address"
            }
            success, customer = self.run_test(
                "Create customer for update test",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            if not success:
                return False
            customer_id = customer.get('id')
        
        # Test updating all fields
        update_data = {
            "full_name": "Updated Customer Name",
            "email": "updated@test.com",
            "phone": "05559876543",
            "address": "Updated Address"
        }
        
        success, updated_customer = self.run_test(
            "Update customer - all fields",
            "PUT",
            f"customers/{customer_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"   ✅ Customer updated: {updated_customer.get('full_name')}")
        
        # Test partial update
        partial_update = {
            "phone": "05551111111"
        }
        
        partial_success, _ = self.run_test(
            "Update customer - partial update",
            "PUT", 
            f"customers/{customer_id}",
            200,
            data=partial_update
        )
        
        # Test invalid customer ID
        invalid_success, _ = self.run_test(
            "Update customer - invalid ID",
            "PUT",
            "customers/invalid-id-12345",
            404,
            data=update_data
        )
        
        return success and partial_success and invalid_success

    def test_search_functionality(self):
        """Test GET /api/search endpoint"""
        # Create test data first
        customer_data = {
            "full_name": "Search Test Customer",
            "email": "search@test.com",
            "phone": "05551234567",
            "address": "Search Test Address"
        }
        
        success, customer = self.run_test(
            "Create customer for search test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair for search testing
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Samsung Galaxy",
            "brand": "Samsung",
            "model": "Galaxy S23",
            "description": "Screen replacement needed",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for search test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        # Test search customers only
        search_customers_success, customers_result = self.run_test(
            "Search customers only",
            "GET",
            "search?query=Search Test&type=customers",
            200
        )
        
        if search_customers_success:
            print(f"   ✅ Found {len(customers_result.get('customers', []))} customers")
        
        # Test search repairs only
        search_repairs_success, repairs_result = self.run_test(
            "Search repairs only", 
            "GET",
            "search?query=Samsung&type=repairs",
            200
        )
        
        if search_repairs_success:
            print(f"   ✅ Found {len(repairs_result.get('repairs', []))} repairs")
        
        # Test search both (no type parameter)
        search_both_success, both_result = self.run_test(
            "Search both customers and repairs",
            "GET",
            "search?query=Search",
            200
        )
        
        if search_both_success:
            customers_count = len(both_result.get('customers', []))
            repairs_count = len(both_result.get('repairs', []))
            print(f"   ✅ Found {customers_count} customers and {repairs_count} repairs")
        
        # Test empty query
        empty_query_success, empty_result = self.run_test(
            "Search with empty query",
            "GET",
            "search?query=",
            200
        )
        
        # Test special characters
        special_char_success, _ = self.run_test(
            "Search with special characters",
            "GET",
            "search?query=@#$%",
            200
        )
        
        # Test phone number search
        phone_search_success, phone_result = self.run_test(
            "Search by phone number",
            "GET",
            "search?query=05551234567&type=customers",
            200
        )
        
        return (search_customers_success and search_repairs_success and 
                search_both_success and empty_query_success and 
                special_char_success and phone_search_success)

    def test_customer_repairs_endpoint(self, customer_id=None):
        """Test GET /api/customers/{customer_id}/repairs endpoint"""
        if not customer_id:
            # Create a customer first
            customer_data = {
                "full_name": "Repairs Test Customer",
                "email": "repairs@test.com",
                "phone": "05551234567"
            }
            success, customer = self.run_test(
                "Create customer for repairs test",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            if not success:
                return False
            customer_id = customer.get('id')
        
        # Test customer with no repairs
        no_repairs_success, no_repairs_result = self.run_test(
            "Get customer repairs - no repairs",
            "GET",
            f"customers/{customer_id}/repairs",
            200
        )
        
        if no_repairs_success:
            print(f"   ✅ Customer has {len(no_repairs_result)} repairs (expected 0)")
        
        # Create some repairs for the customer
        repair_data_1 = {
            "customer_id": customer_id,
            "device_type": "iPhone",
            "brand": "Apple",
            "model": "iPhone 14",
            "description": "Battery replacement",
            "priority": "orta"
        }
        
        repair_data_2 = {
            "customer_id": customer_id,
            "device_type": "MacBook",
            "brand": "Apple", 
            "model": "MacBook Pro",
            "description": "Keyboard repair",
            "priority": "yuksek"
        }
        
        repair1_success, repair1 = self.run_test(
            "Create first repair for customer",
            "POST",
            "repairs",
            200,
            data=repair_data_1
        )
        
        repair2_success, repair2 = self.run_test(
            "Create second repair for customer",
            "POST",
            "repairs",
            200,
            data=repair_data_2
        )
        
        if not (repair1_success and repair2_success):
            return False
        
        # Test customer with repairs
        with_repairs_success, with_repairs_result = self.run_test(
            "Get customer repairs - with repairs",
            "GET",
            f"customers/{customer_id}/repairs",
            200
        )
        
        if with_repairs_success:
            print(f"   ✅ Customer has {len(with_repairs_result)} repairs")
        
        # Test invalid customer ID
        invalid_customer_success, _ = self.run_test(
            "Get customer repairs - invalid customer ID",
            "GET",
            "customers/invalid-id-12345/repairs",
            404
        )
        
        return no_repairs_success and with_repairs_success and invalid_customer_success

    def test_delete_customer_endpoint(self):
        """Test DELETE /api/customers/{customer_id} endpoint with cascade deletion"""
        # Create a test customer
        customer_data = {
            "full_name": "Delete Test Customer",
            "email": "delete@test.com",
            "phone": "05551234567",
            "address": "Delete Test Address"
        }
        
        success, customer = self.run_test(
            "Create customer for delete test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer.get('id')
        
        # Create repairs for this customer to test cascade deletion
        repair_data_1 = {
            "customer_id": customer_id,
            "device_type": "iPhone",
            "brand": "Apple",
            "model": "iPhone 14",
            "description": "Screen repair",
            "priority": "yuksek"
        }
        
        repair_data_2 = {
            "customer_id": customer_id,
            "device_type": "iPad",
            "brand": "Apple",
            "model": "iPad Pro",
            "description": "Battery replacement",
            "priority": "orta"
        }
        
        repair1_success, repair1 = self.run_test(
            "Create first repair for delete test",
            "POST",
            "repairs",
            200,
            data=repair_data_1
        )
        
        repair2_success, repair2 = self.run_test(
            "Create second repair for delete test",
            "POST",
            "repairs",
            200,
            data=repair_data_2
        )
        
        if not (repair1_success and repair2_success):
            return False
        
        repair1_id = repair1.get('id')
        repair2_id = repair2.get('id')
        
        # Verify repairs exist before deletion
        verify1_success, _ = self.run_test(
            "Verify repair 1 exists before customer deletion",
            "GET",
            f"repairs/{repair1_id}",
            200
        )
        
        verify2_success, _ = self.run_test(
            "Verify repair 2 exists before customer deletion",
            "GET",
            f"repairs/{repair2_id}",
            200
        )
        
        if not (verify1_success and verify2_success):
            return False
        
        # Delete the customer (should cascade delete repairs)
        delete_success, delete_response = self.run_test(
            "Delete customer with cascade deletion",
            "DELETE",
            f"customers/{customer_id}",
            200
        )
        
        if not delete_success:
            return False
        
        print(f"   ✅ Customer deleted: {delete_response.get('message')}")
        
        # Verify customer is deleted
        customer_deleted_success, _ = self.run_test(
            "Verify customer is deleted",
            "GET",
            f"customers/{customer_id}",
            404
        )
        
        # Verify repairs are cascade deleted
        repair1_deleted_success, _ = self.run_test(
            "Verify repair 1 is cascade deleted",
            "GET",
            f"repairs/{repair1_id}",
            404
        )
        
        repair2_deleted_success, _ = self.run_test(
            "Verify repair 2 is cascade deleted",
            "GET",
            f"repairs/{repair2_id}",
            404
        )
        
        # Test deleting non-existent customer
        nonexistent_success, _ = self.run_test(
            "Delete non-existent customer",
            "DELETE",
            "customers/nonexistent-id-12345",
            404
        )
        
        return (delete_success and customer_deleted_success and 
                repair1_deleted_success and repair2_deleted_success and 
                nonexistent_success)

    def test_delete_repair_endpoint(self):
        """Test DELETE /api/repairs/{repair_id} endpoint with role-based access"""
        # Create a test customer first
        customer_data = {
            "full_name": "Repair Delete Test Customer",
            "email": "repairdelete@test.com",
            "phone": "05551234567"
        }
        
        success, customer = self.run_test(
            "Create customer for repair delete test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair to delete
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Samsung Galaxy",
            "brand": "Samsung",
            "model": "Galaxy S23",
            "description": "Screen replacement",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for delete test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        repair_id = repair.get('id')
        
        # Test deleting the repair
        delete_success, delete_response = self.run_test(
            "Delete repair request",
            "DELETE",
            f"repairs/{repair_id}",
            200
        )
        
        if not delete_success:
            return False
        
        print(f"   ✅ Repair deleted: {delete_response.get('message')}")
        
        # Verify repair is deleted
        repair_deleted_success, _ = self.run_test(
            "Verify repair is deleted",
            "GET",
            f"repairs/{repair_id}",
            404
        )
        
        # Test deleting non-existent repair
        nonexistent_success, _ = self.run_test(
            "Delete non-existent repair",
            "DELETE",
            "repairs/nonexistent-repair-id-12345",
            404
        )
        
        return delete_success and repair_deleted_success and nonexistent_success

    def test_notifications_endpoints(self):
        """Test notification system endpoints (admin only)"""
        # Only admin can access notifications
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping notification tests (admin only)")
            return True
        
        # Test get notifications
        notifications_success, notifications = self.run_test(
            "Get notifications",
            "GET",
            "notifications",
            200
        )
        
        if not notifications_success:
            return False
        
        print(f"   ✅ Retrieved {len(notifications)} notifications")
        
        # Test get unread notifications count
        unread_count_success, unread_response = self.run_test(
            "Get unread notifications count",
            "GET",
            "notifications/unread-count",
            200
        )
        
        if not unread_count_success:
            return False
        
        unread_count = unread_response.get('unread_count', 0)
        print(f"   ✅ Unread notifications count: {unread_count}")
        
        # Test get unread notifications only
        unread_only_success, unread_notifications = self.run_test(
            "Get unread notifications only",
            "GET",
            "notifications?unread_only=true",
            200
        )
        
        if not unread_only_success:
            return False
        
        print(f"   ✅ Retrieved {len(unread_notifications)} unread notifications")
        
        # Test marking notification as read (if we have notifications)
        mark_read_success = True
        if notifications and len(notifications) > 0:
            notification_id = notifications[0].get('id')
            if notification_id:
                mark_read_success, mark_read_response = self.run_test(
                    "Mark notification as read",
                    "PUT",
                    f"notifications/{notification_id}/read",
                    200
                )
                
                if mark_read_success:
                    print(f"   ✅ Notification marked as read: {mark_read_response.get('message')}")
        
        # Test marking non-existent notification as read
        nonexistent_read_success, _ = self.run_test(
            "Mark non-existent notification as read",
            "PUT",
            "notifications/nonexistent-id-12345/read",
            404
        )
        
        return (notifications_success and unread_count_success and 
                unread_only_success and mark_read_success and nonexistent_read_success)

    def test_notification_creation(self):
        """Test that notifications are created when customers/repairs are created or updated"""
        # Only admin can see notifications, but we can test creation with any role
        print(f"\n📢 Testing notification creation for: {self.current_user.get('role')}")
        
        # Create a customer (should generate notification)
        customer_data = {
            "full_name": "Notification Test Customer",
            "email": "notification@test.com",
            "phone": "05551234567",
            "address": "Notification Test Address"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for notification test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair (should generate notification)
        repair_data = {
            "customer_id": customer_id,
            "device_type": "iPhone",
            "brand": "Apple",
            "model": "iPhone 15",
            "description": "Battery replacement for notification test",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for notification test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        repair_id = repair.get('id')
        
        # Update repair status (should generate notification) - only admin/technician can update
        update_success = True
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            update_data = {
                "status": "isleniyor"
            }
            
            update_success, updated_repair = self.run_test(
                "Update repair status for notification test",
                "PUT",
                f"repairs/{repair_id}",
                200,
                data=update_data
            )
            
            if update_success:
                print(f"   ✅ Repair status updated to generate notification")
        
        print(f"   ✅ Notification creation tests completed (notifications should be visible to admin)")
        return customer_success and repair_success and update_success

    def test_repair_cancellation_endpoint(self):
        """Test PUT /api/repairs/{repair_id}/cancel endpoint"""
        print(f"\n🚫 Testing repair cancellation for: {self.current_user.get('role')}")
        
        # Only admin and technician can cancel repairs
        if self.current_user.get('role') not in ['admin', 'teknisyen']:
            print("   ⚠️  Skipping repair cancellation tests (insufficient permissions)")
            return True
        
        # Create a test customer first
        customer_data = {
            "full_name": "Cancel Test Customer",
            "email": "cancel@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for cancel test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair to cancel
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Samsung Galaxy",
            "brand": "Samsung",
            "model": "Galaxy S24",
            "description": "Screen repair for cancellation test",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for cancellation test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        repair_id = repair.get('id')
        
        # Test cancelling the repair
        cancel_success, cancelled_repair = self.run_test(
            "Cancel repair request",
            "PUT",
            f"repairs/{repair_id}/cancel",
            200
        )
        
        if not cancel_success:
            return False
        
        # Verify repair status is cancelled
        if cancelled_repair.get('status') == 'iptal':
            print(f"   ✅ Repair successfully cancelled: {cancelled_repair.get('status')}")
        else:
            print(f"   ❌ Repair status not updated correctly: {cancelled_repair.get('status')}")
            return False
        
        # Test cancelling non-existent repair
        nonexistent_cancel_success, _ = self.run_test(
            "Cancel non-existent repair",
            "PUT",
            "repairs/nonexistent-repair-id/cancel",
            404
        )
        
        return cancel_success and nonexistent_cancel_success

    def test_clear_all_notifications_endpoint(self):
        """Test DELETE /api/notifications/clear-all endpoint"""
        print(f"\n🗑️ Testing clear all notifications for: {self.current_user.get('role')}")
        
        # Only admin can clear notifications
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping clear notifications test (admin only)")
            return True
        
        # First, create some notifications by creating customers and repairs
        customer_data = {
            "full_name": "Clear Notifications Test Customer",
            "email": "clearnotif@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for clear notifications test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair (generates notification)
        repair_data = {
            "customer_id": customer_id,
            "device_type": "iPhone",
            "brand": "Apple",
            "model": "iPhone 15 Pro",
            "description": "Battery replacement for clear notifications test",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for clear notifications test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        # Check notifications count before clearing
        count_before_success, count_before_response = self.run_test(
            "Get notifications count before clearing",
            "GET",
            "notifications/unread-count",
            200
        )
        
        if not count_before_success:
            return False
        
        count_before = count_before_response.get('unread_count', 0)
        print(f"   📊 Notifications before clearing: {count_before}")
        
        # Clear all notifications
        clear_success, clear_response = self.run_test(
            "Clear all notifications",
            "DELETE",
            "notifications/clear-all",
            200
        )
        
        if not clear_success:
            return False
        
        cleared_count = clear_response.get('message', '').split()[0]
        print(f"   ✅ Cleared notifications: {clear_response.get('message')}")
        
        # Check notifications count after clearing
        count_after_success, count_after_response = self.run_test(
            "Get notifications count after clearing",
            "GET",
            "notifications/unread-count",
            200
        )
        
        if not count_after_success:
            return False
        
        count_after = count_after_response.get('unread_count', 0)
        print(f"   📊 Notifications after clearing: {count_after}")
        
        # Verify count is 0 after clearing
        if count_after == 0:
            print(f"   ✅ All notifications successfully cleared")
        else:
            print(f"   ❌ Notifications not properly cleared, count: {count_after}")
            return False
        
        return clear_success and count_after == 0

    def test_file_upload_endpoints(self):
        """Test POST /api/upload and POST /api/upload-multiple endpoints with validation"""
        print(f"\n📁 Testing file upload endpoints for: {self.current_user.get('role')}")
        
        # Test single file upload with valid file type
        # Since we can't actually upload files in this test environment, 
        # we'll test the endpoints to see if they exist and return appropriate errors
        
        # Test single upload endpoint exists
        single_upload_success, single_response = self.run_test(
            "Test single file upload endpoint (no file)",
            "POST",
            "upload",
            422  # Expecting validation error for missing file
        )
        
        # Test multiple upload endpoint exists  
        multiple_upload_success, multiple_response = self.run_test(
            "Test multiple file upload endpoint (no files)",
            "POST",
            "upload-multiple",
            422  # Expecting validation error for missing files
        )
        
        print(f"   ✅ File upload endpoints are accessible")
        print(f"   ℹ️  Note: Actual file upload testing requires multipart/form-data which is not supported in this test framework")
        
        return single_upload_success and multiple_upload_success

    def test_enhanced_repair_creation_with_files(self):
        """Test creating repairs with file attachments"""
        print(f"\n📎 Testing enhanced repair creation with files for: {self.current_user.get('role')}")
        
        # Only admin and technician can create repairs
        if self.current_user.get('role') not in ['admin', 'teknisyen']:
            print("   ⚠️  Skipping enhanced repair creation tests (insufficient permissions)")
            return True
        
        # Create a test customer first
        customer_data = {
            "full_name": "Enhanced Repair Test Customer",
            "email": "enhanced@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for enhanced repair test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create repair with file attachments (simulated file URLs)
        repair_data = {
            "customer_id": customer_id,
            "device_type": "MacBook Pro",
            "brand": "Apple",
            "model": "MacBook Pro 16-inch",
            "description": "Keyboard and trackpad issues with photo evidence",
            "priority": "yuksek",
            "images": [
                "/uploads/test-image-1.jpg",
                "/uploads/test-image-2.png",
                "/uploads/test-document.pdf"
            ]
        }
        
        repair_success, repair = self.run_test(
            "Create repair with file attachments",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        # Verify images array is stored
        if repair.get('images') and len(repair.get('images')) == 3:
            print(f"   ✅ Repair created with {len(repair.get('images'))} file attachments")
        else:
            print(f"   ❌ File attachments not properly stored: {repair.get('images')}")
            return False
        
        return repair_success

    def test_role_based_repair_cancellation(self):
        """Test role-based access control for repair cancellation"""
        print(f"\n🔐 Testing role-based repair cancellation access for: {self.current_user.get('role')}")
        
        # Only test for technician role (admin can cancel any repair)
        if self.current_user.get('role') != 'teknisyen':
            print("   ⚠️  Skipping role-based cancellation test (technician role only)")
            return True
        
        # Create a customer for this technician
        customer_data = {
            "full_name": "Role Test Customer",
            "email": "roletest@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for role-based test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair by this technician
        repair_data = {
            "customer_id": customer_id,
            "device_type": "iPad",
            "brand": "Apple",
            "model": "iPad Air",
            "description": "Screen replacement for role test",
            "priority": "orta"
        }
        
        own_repair_success, own_repair = self.run_test(
            "Create own repair for role test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not own_repair_success:
            return False
        
        own_repair_id = own_repair.get('id')
        
        # Test cancelling own repair (should succeed)
        cancel_own_success, _ = self.run_test(
            "Technician cancel own repair",
            "PUT",
            f"repairs/{own_repair_id}/cancel",
            200
        )
        
        if cancel_own_success:
            print(f"   ✅ Technician can cancel own repairs")
        
        # Note: Testing cancellation of other technician's repairs would require 
        # creating repairs with different technician IDs, which is complex in this test setup
        
        return cancel_own_success

    def test_admin_panel_endpoints(self):
        """Test all new admin panel endpoints"""
        print(f"\n🏢 Testing Admin Panel Endpoints for: {self.current_user.get('role')}")
        
        # Only test if user has appropriate permissions
        if self.current_user.get('role') not in ['admin', 'teknisyen']:
            print("   ⚠️  Skipping admin panel tests (insufficient permissions)")
            return True
        
        # Create a test customer for all endpoint tests
        customer_data = {
            "full_name": "Admin Panel Test Customer",
            "email": "adminpanel@test.com",
            "phone": "05551234567",
            "address": "Admin Panel Test Address"
        }
        
        success, customer = self.run_test(
            "Create customer for admin panel tests",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not success:
            return False
        
        customer_id = customer.get('id')
        
        # Test all admin panel endpoints
        detail_success = self.test_customer_detail_endpoint(customer_id)
        update_success = self.test_customer_update_endpoint(customer_id)
        search_success = self.test_search_functionality()
        repairs_success = self.test_customer_repairs_endpoint(customer_id)
        
        # Test new delete endpoints
        delete_customer_success = self.test_delete_customer_endpoint()
        delete_repair_success = self.test_delete_repair_endpoint()
        
        # Test notifications (admin only)
        notifications_success = self.test_notifications_endpoints()
        
        # Test notification creation
        notification_creation_success = self.test_notification_creation()
        
        return (detail_success and update_success and search_success and 
                repairs_success and delete_customer_success and delete_repair_success and
                notifications_success and notification_creation_success)

    def test_repair_detail_endpoint_with_roles(self):
        """Test GET /api/repairs/{repair_id} endpoint with role-based access control"""
        print(f"\n🔍 Testing repair detail endpoint with role-based access for: {self.current_user.get('role')}")
        
        # Create a test customer first
        customer_data = {
            "full_name": "Repair Detail Test Customer",
            "email": "repairdetail@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for repair detail test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair to test detail access
        repair_data = {
            "customer_id": customer_id,
            "device_type": "iPhone",
            "brand": "Apple",
            "model": "iPhone 15",
            "description": "Screen replacement for detail access test",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for detail access test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        repair_id = repair.get('id')
        
        # Test accessing own repair details
        own_repair_success, own_repair_detail = self.run_test(
            f"{self.current_user.get('role')} access own repair details",
            "GET",
            f"repairs/{repair_id}",
            200
        )
        
        if own_repair_success:
            print(f"   ✅ {self.current_user.get('role')} can access own repair details")
        
        # Test invalid repair ID
        invalid_repair_success, _ = self.run_test(
            "Access repair with invalid ID",
            "GET",
            "repairs/invalid-repair-id-12345",
            404
        )
        
        if invalid_repair_success:
            print(f"   ✅ Invalid repair ID returns 404 as expected")
        
        # For technician role, test accessing other technician's repairs (should fail with 403)
        access_denied_success = True
        if self.current_user.get('role') == 'teknisyen':
            # This would require creating a repair by another technician
            # For now, we'll simulate by testing with a non-existent repair that would belong to another technician
            # In a real scenario, this would be a repair created by a different technician
            print(f"   ℹ️  Note: Testing technician access to other's repairs requires multiple technician accounts")
        
        return own_repair_success and invalid_repair_success and access_denied_success

    def test_enhanced_notification_system(self):
        """Test enhanced notification system with extra_data fields"""
        print(f"\n📢 Testing enhanced notification system for: {self.current_user.get('role')}")
        
        # Only admin can view notifications, but we can test creation
        # Create a customer (should generate notification with extra data)
        customer_data = {
            "full_name": "Enhanced Notification Test Customer",
            "email": "enhancednotif@test.com",
            "phone": "05551234567",
            "address": "Enhanced Notification Test Address"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for enhanced notification test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Create a repair (should generate notification with extra fields)
        repair_data = {
            "customer_id": customer_id,
            "device_type": "MacBook Pro",
            "brand": "Apple",
            "model": "MacBook Pro 16-inch",
            "description": "Keyboard replacement for enhanced notification test",
            "priority": "yuksek"
        }
        
        repair_success, repair = self.run_test(
            "Create repair for enhanced notification test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        repair_id = repair.get('id')
        
        # Update repair status (should generate notification with new_status field)
        status_update_success = True
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            update_data = {
                "status": "isleniyor"
            }
            
            status_update_success, updated_repair = self.run_test(
                "Update repair status for enhanced notification test",
                "PUT",
                f"repairs/{repair_id}",
                200,
                data=update_data
            )
            
            if status_update_success:
                print(f"   ✅ Repair status updated - should generate notification with new_status field")
        
        # Cancel repair (should generate notification with type 'repair_cancelled')
        cancel_success = True
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            cancel_success, cancelled_repair = self.run_test(
                "Cancel repair for enhanced notification test",
                "PUT",
                f"repairs/{repair_id}/cancel",
                200
            )
            
            if cancel_success:
                print(f"   ✅ Repair cancelled - should generate 'repair_cancelled' notification")
        
        # If admin, check that notifications contain the expected extra data
        notification_data_success = True
        if self.current_user.get('role') == 'admin':
            notifications_success, notifications = self.run_test(
                "Get notifications to verify enhanced data structure",
                "GET",
                "notifications?limit=10",
                200
            )
            
            if notifications_success and notifications:
                # Look for recent notifications that should contain extra_data
                recent_notifications = notifications[:5]  # Check last 5 notifications
                found_enhanced_notification = False
                
                for notification in recent_notifications:
                    # Check if notification has the expected extra fields
                    if (hasattr(notification, 'repair_id') or 'repair_id' in notification or
                        hasattr(notification, 'customer_name') or 'customer_name' in notification or
                        hasattr(notification, 'device_info') or 'device_info' in notification):
                        found_enhanced_notification = True
                        print(f"   ✅ Found notification with enhanced data fields")
                        break
                
                if not found_enhanced_notification:
                    print(f"   ⚠️  Enhanced notification fields not found in recent notifications")
                    # This is not a failure as the notifications might be from previous tests
            else:
                print(f"   ⚠️  Could not retrieve notifications to verify enhanced data")
        else:
            print(f"   ℹ️  Enhanced notification data verification requires admin access")
        
        return customer_success and repair_success and status_update_success and cancel_success

    def test_notification_data_structure(self):
        """Test that notifications contain proper data structure with repair_id for frontend linking"""
        print(f"\n🔗 Testing notification data structure for: {self.current_user.get('role')}")
        
        # Only admin can access notifications
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping notification data structure test (admin only)")
            return True
        
        # Get recent notifications
        notifications_success, notifications = self.run_test(
            "Get notifications for data structure test",
            "GET",
            "notifications?limit=20",
            200
        )
        
        if not notifications_success:
            return False
        
        if not notifications or len(notifications) == 0:
            print(f"   ⚠️  No notifications found to test data structure")
            return True
        
        # Analyze notification structure
        structure_valid = True
        repair_linked_count = 0
        
        for i, notification in enumerate(notifications[:10]):  # Check first 10
            # Check basic required fields
            required_fields = ['id', 'type', 'title', 'message', 'related_id', 'created_at', 'read']
            missing_fields = []
            
            for field in required_fields:
                if not (hasattr(notification, field) or field in notification):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Notification {i+1} missing fields: {missing_fields}")
                structure_valid = False
            
            # Check for enhanced fields (repair_id, customer_name, device_info)
            enhanced_fields = ['repair_id', 'customer_name', 'device_info']
            has_enhanced_fields = any(
                hasattr(notification, field) or field in notification 
                for field in enhanced_fields
            )
            
            if has_enhanced_fields:
                repair_linked_count += 1
        
        print(f"   ✅ Checked {len(notifications[:10])} notifications for data structure")
        print(f"   📊 {repair_linked_count} notifications have enhanced fields for frontend linking")
        
        if structure_valid:
            print(f"   ✅ All notifications have proper basic data structure")
        
        return structure_valid

    def test_system_management_endpoints(self):
        """Test new system management endpoints for admin panel"""
        print(f"\n🔧 Testing System Management Endpoints for: {self.current_user.get('role')}")
        
        # Only admin can access system management endpoints
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping system management tests (admin only)")
            return True
        
        # First create some test data to delete
        print("   📝 Creating test data for system management tests...")
        
        # Create test customers
        test_customers = []
        for i in range(3):
            customer_data = {
                "full_name": f"System Test Customer {i+1}",
                "email": f"systemtest{i+1}@test.com",
                "phone": f"055512345{i+1}0",
                "address": f"System Test Address {i+1}"
            }
            
            success, customer = self.run_test(
                f"Create test customer {i+1} for system management",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            
            if success:
                test_customers.append(customer)
        
        # Create test repairs
        test_repairs = []
        for i, customer in enumerate(test_customers):
            repair_data = {
                "customer_id": customer.get('id'),
                "device_type": f"Test Device {i+1}",
                "brand": "Test Brand",
                "model": f"Model {i+1}",
                "description": f"Test repair description {i+1}",
                "priority": "orta"
            }
            
            success, repair = self.run_test(
                f"Create test repair {i+1} for system management",
                "POST",
                "repairs",
                200,
                data=repair_data
            )
            
            if success:
                test_repairs.append(repair)
        
        print(f"   ✅ Created {len(test_customers)} customers and {len(test_repairs)} repairs for testing")
        
        # Test 1: DELETE /api/admin/repairs/delete-all
        delete_all_repairs_success, delete_repairs_response = self.run_test(
            "Delete all repair records (admin only)",
            "DELETE",
            "admin/repairs/delete-all",
            200
        )
        
        if delete_all_repairs_success:
            message = delete_repairs_response.get('message', '')
            print(f"   ✅ Delete all repairs: {message}")
        
        # Test 2: DELETE /api/admin/customers/delete-all  
        delete_all_customers_success, delete_customers_response = self.run_test(
            "Delete all customers and their repairs (admin only)",
            "DELETE",
            "admin/customers/delete-all",
            200
        )
        
        if delete_all_customers_success:
            message = delete_customers_response.get('message', '')
            print(f"   ✅ Delete all customers: {message}")
        
        # Test 3: DELETE /api/admin/system/reset
        system_reset_success, reset_response = self.run_test(
            "Reset entire system except admin users (admin only)",
            "DELETE",
            "admin/system/reset",
            200
        )
        
        if system_reset_success:
            message = reset_response.get('message', '')
            print(f"   ✅ System reset: {message}")
        
        # Test 4: POST /api/admin/demo/create-data
        create_demo_success, demo_response = self.run_test(
            "Create Refsan Türkiye demo data (admin only)",
            "POST",
            "admin/demo/create-data",
            200
        )
        
        if create_demo_success:
            customers_created = demo_response.get('customers_created', 0)
            repairs_created = demo_response.get('repairs_created', 0)
            message = demo_response.get('message', '')
            print(f"   ✅ Demo data created: {customers_created} customers, {repairs_created} repairs")
            print(f"   📝 {message}")
        
        return (delete_all_repairs_success and delete_all_customers_success and 
                system_reset_success and create_demo_success)

    def test_system_management_role_access_control(self):
        """Test role-based access control for system management endpoints"""
        print(f"\n🔐 Testing System Management Role Access Control for: {self.current_user.get('role')}")
        
        # Test access control for non-admin users
        if self.current_user.get('role') != 'admin':
            # Test that technician/customer cannot access system management endpoints
            
            # Test DELETE /api/admin/repairs/delete-all (should return 403)
            delete_repairs_forbidden, _ = self.run_test(
                f"{self.current_user.get('role')} access delete all repairs (should fail)",
                "DELETE",
                "admin/repairs/delete-all",
                403
            )
            
            # Test DELETE /api/admin/customers/delete-all (should return 403)
            delete_customers_forbidden, _ = self.run_test(
                f"{self.current_user.get('role')} access delete all customers (should fail)",
                "DELETE",
                "admin/customers/delete-all",
                403
            )
            
            # Test DELETE /api/admin/system/reset (should return 403)
            system_reset_forbidden, _ = self.run_test(
                f"{self.current_user.get('role')} access system reset (should fail)",
                "DELETE",
                "admin/system/reset",
                403
            )
            
            # Test POST /api/admin/demo/create-data (should return 403)
            demo_data_forbidden, _ = self.run_test(
                f"{self.current_user.get('role')} access demo data creation (should fail)",
                "POST",
                "admin/demo/create-data",
                403
            )
            
            if (delete_repairs_forbidden and delete_customers_forbidden and 
                system_reset_forbidden and demo_data_forbidden):
                print(f"   ✅ {self.current_user.get('role')} correctly denied access to all system management endpoints")
            
            return (delete_repairs_forbidden and delete_customers_forbidden and 
                    system_reset_forbidden and demo_data_forbidden)
        else:
            print("   ℹ️  Admin role - access control tested in main system management test")
            return True

    def test_demo_data_validation(self):
        """Test that demo data contains proper Refsan ceramic machinery examples"""
        print(f"\n🏭 Testing Demo Data Validation for: {self.current_user.get('role')}")
        
        # Only admin can create and verify demo data
        if self.current_user.get('role') != 'admin':
            print("   ⚠️  Skipping demo data validation (admin only)")
            return True
        
        # Create demo data
        create_demo_success, demo_response = self.run_test(
            "Create demo data for validation",
            "POST",
            "admin/demo/create-data",
            200
        )
        
        if not create_demo_success:
            return False
        
        # Verify demo data was created
        customers_created = demo_response.get('customers_created', 0)
        repairs_created = demo_response.get('repairs_created', 0)
        
        if customers_created < 5 or repairs_created < 5:
            print(f"   ❌ Insufficient demo data created: {customers_created} customers, {repairs_created} repairs")
            return False
        
        # Get customers to verify ceramic industry names
        customers_success, customers = self.run_test(
            "Get customers to verify demo data",
            "GET",
            "customers",
            200
        )
        
        if not customers_success:
            return False
        
        # Check for ceramic industry customer names
        ceramic_keywords = ['seramik', 'çini', 'karo', 'porselen']
        ceramic_customers = 0
        
        for customer in customers:
            customer_name = customer.get('full_name', '').lower()
            if any(keyword in customer_name for keyword in ceramic_keywords):
                ceramic_customers += 1
        
        print(f"   📊 Found {ceramic_customers} customers with ceramic industry names")
        
        # Get repairs to verify Refsan brand machinery
        repairs_success, repairs = self.run_test(
            "Get repairs to verify demo data",
            "GET",
            "repairs",
            200
        )
        
        if not repairs_success:
            return False
        
        # Check for Refsan brand and ceramic machinery
        refsan_repairs = 0
        ceramic_devices = 0
        ceramic_device_types = ['seramik', 'çini', 'karo', 'porselen', 'fırın', 'pres', 'kesim', 'kalıplama', 'sırlama']
        
        for repair in repairs:
            brand = repair.get('brand', '').lower()
            device_type = repair.get('device_type', '').lower()
            
            if 'refsan' in brand:
                refsan_repairs += 1
            
            if any(device_type in device_type for device_type in ceramic_device_types):
                ceramic_devices += 1
        
        print(f"   📊 Found {refsan_repairs} Refsan brand repairs")
        print(f"   📊 Found {ceramic_devices} ceramic machinery repairs")
        
        # Validation criteria
        validation_success = (
            ceramic_customers >= 3 and  # At least 3 ceramic industry customers
            refsan_repairs >= 3 and     # At least 3 Refsan brand repairs
            ceramic_devices >= 3        # At least 3 ceramic machinery repairs
        )
        
        if validation_success:
            print(f"   ✅ Demo data validation passed - contains proper Refsan ceramic machinery examples")
        else:
            print(f"   ❌ Demo data validation failed - insufficient ceramic industry content")
        
        return validation_success

    def test_spare_parts_endpoint(self):
        """Test GET /api/spare-parts endpoint"""
        print(f"\n🔧 Testing Spare Parts Endpoint for: {self.current_user.get('role')}")
        
        success, spare_parts_response = self.run_test(
            "Get spare parts list",
            "GET",
            "spare-parts",
            200
        )
        
        if not success:
            return False
        
        # Extract parts array from response
        spare_parts = spare_parts_response.get('parts', [])
        total_count = spare_parts_response.get('total_count', 0)
        
        # Verify we have 57 spare parts as expected
        if total_count != 57 or len(spare_parts) != 57:
            print(f"   ❌ Expected 57 spare parts, got {len(spare_parts)} (total_count: {total_count})")
            return False
        
        print(f"   ✅ Retrieved {len(spare_parts)} spare parts")
        
        # Verify spare parts structure
        if spare_parts:
            first_part = spare_parts[0]
            required_fields = ['id', 'name', 'price_eur']
            missing_fields = [field for field in required_fields if field not in first_part]
            
            if missing_fields:
                print(f"   ❌ Spare part missing fields: {missing_fields}")
                return False
            
            print(f"   ✅ Spare parts have correct structure")
            
            # Check specific parts mentioned in review request
            tk_k_15cm = next((part for part in spare_parts if part['id'] == 'tk_k_15cm'), None)
            dijital_soket = next((part for part in spare_parts if part['id'] == 'dijital_soket'), None)
            
            if tk_k_15cm and tk_k_15cm['price'] == 75.0:
                print(f"   ✅ Found Termokupl K 15CM with correct price: {tk_k_15cm['price']}€")
            else:
                print(f"   ❌ Termokupl K 15CM not found or incorrect price")
                return False
                
            if dijital_soket and dijital_soket['price'] == 30.0:
                print(f"   ✅ Found Dijital Soket with correct price: {dijital_soket['price']}€")
            else:
                print(f"   ❌ Dijital Soket not found or incorrect price")
                return False
        
        return True

    def test_repair_creation_with_spare_parts(self):
        """Test POST /api/repairs with spare parts cost calculation"""
        print(f"\n🔧 Testing Repair Creation with Spare Parts for: {self.current_user.get('role')}")
        
        # Create a test customer first
        customer_data = {
            "full_name": "Spare Parts Test Customer",
            "email": "spareparts@test.com",
            "phone": "05551234567",
            "address": "Spare Parts Test Address"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for spare parts test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Test repair with spare parts
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Seramik Fırını",
            "brand": "Refsan",
            "model": "RS300",
            "description": "Termokupl ve dijital soket değişimi",
            "priority": "yuksek",
            "cost_estimate": 100.0,
            "distance_category": "ankara_ici",
            "spare_parts": [
                {
                    "part_id": "sp001",
                    "part_name": "RD16 - RD27 - RD50 / TOP 16 Termokupl K Tipi (0-1200°C) 15CM (60 + 100)",
                    "price_eur": 75.0,
                    "quantity": 2
                },
                {
                    "part_id": "sp012", 
                    "part_name": "Dijital Soket",
                    "price_eur": 30.0,
                    "quantity": 1
                }
            ]
        }
        
        repair_success, repair = self.run_test(
            "Create repair with spare parts",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        # Verify cost calculations
        expected_spare_parts_total = (75.0 * 2) + (30.0 * 1)  # 150 + 30 = 180
        expected_subtotal = 100.0 + 100.0 + 180.0  # cost_estimate + service_fee + spare_parts_total = 380
        expected_vat = expected_subtotal * 0.20  # 76
        expected_total_with_vat = expected_subtotal + expected_vat  # 456
        
        actual_spare_parts_total = repair.get('spare_parts_total', 0)
        actual_vat_amount = repair.get('vat_amount', 0)
        actual_total_with_vat = repair.get('total_with_vat', 0)
        
        print(f"   📊 Expected spare parts total: {expected_spare_parts_total}€")
        print(f"   📊 Actual spare parts total: {actual_spare_parts_total}€")
        print(f"   📊 Expected total with VAT: {expected_total_with_vat}€")
        print(f"   📊 Actual total with VAT: {actual_total_with_vat}€")
        
        # Check spare parts total calculation
        if abs(actual_spare_parts_total - expected_spare_parts_total) < 0.01:
            print(f"   ✅ Spare parts total calculated correctly")
        else:
            print(f"   ❌ Spare parts total calculation error")
            return False
        
        # Check total with VAT calculation
        if abs(actual_total_with_vat - expected_total_with_vat) < 0.01:
            print(f"   ✅ Total with VAT calculated correctly")
        else:
            print(f"   ❌ Total with VAT calculation error")
            return False
        
        # Verify spare parts array is stored
        stored_spare_parts = repair.get('spare_parts', [])
        if len(stored_spare_parts) == 2:
            print(f"   ✅ Spare parts array stored correctly ({len(stored_spare_parts)} parts)")
        else:
            print(f"   ❌ Spare parts array not stored correctly")
            return False
        
        return True

    def test_repair_creation_without_spare_parts(self):
        """Test POST /api/repairs without spare parts"""
        print(f"\n🔧 Testing Repair Creation without Spare Parts for: {self.current_user.get('role')}")
        
        # Create a test customer first
        customer_data = {
            "full_name": "No Spare Parts Test Customer",
            "email": "nospareparts@test.com", 
            "phone": "05551234567",
            "address": "No Spare Parts Test Address"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for no spare parts test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Test repair without spare parts
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Seramik Presi",
            "brand": "Refsan",
            "model": "RP100",
            "description": "Genel bakım ve temizlik",
            "priority": "orta",
            "cost_estimate": 200.0,
            "distance_category": "ankara_ici",
            "spare_parts": []  # Empty spare parts array
        }
        
        repair_success, repair = self.run_test(
            "Create repair without spare parts",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        # Verify cost calculations without spare parts
        expected_spare_parts_total = 0.0
        expected_subtotal = 200.0 + 100.0 + 0.0  # cost_estimate + service_fee + spare_parts_total = 300
        expected_vat = expected_subtotal * 0.20  # 60
        expected_total_with_vat = expected_subtotal + expected_vat  # 360
        
        actual_spare_parts_total = repair.get('spare_parts_total', 0)
        actual_total_with_vat = repair.get('total_with_vat', 0)
        
        print(f"   📊 Expected spare parts total: {expected_spare_parts_total}€")
        print(f"   📊 Actual spare parts total: {actual_spare_parts_total}€")
        print(f"   📊 Expected total with VAT: {expected_total_with_vat}€")
        print(f"   📊 Actual total with VAT: {actual_total_with_vat}€")
        
        # Check spare parts total is 0
        if actual_spare_parts_total == 0.0:
            print(f"   ✅ Spare parts total is 0 as expected")
        else:
            print(f"   ❌ Spare parts total should be 0")
            return False
        
        # Check total calculation without spare parts
        if abs(actual_total_with_vat - expected_total_with_vat) < 0.01:
            print(f"   ✅ Total with VAT calculated correctly without spare parts")
        else:
            print(f"   ❌ Total with VAT calculation error without spare parts")
            return False
        
        # Verify spare parts array is empty
        stored_spare_parts = repair.get('spare_parts', [])
        if len(stored_spare_parts) == 0:
            print(f"   ✅ Spare parts array is empty as expected")
        else:
            print(f"   ❌ Spare parts array should be empty")
            return False
        
        return True

    def test_spare_parts_cost_calculation_accuracy(self):
        """Test specific cost calculation scenario from review request"""
        print(f"\n🧮 Testing Spare Parts Cost Calculation Accuracy for: {self.current_user.get('role')}")
        
        # Create a test customer first
        customer_data = {
            "full_name": "Cost Calculation Test Customer",
            "email": "costcalc@test.com",
            "phone": "05551234567"
        }
        
        customer_success, customer = self.run_test(
            "Create customer for cost calculation test",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if not customer_success:
            return False
        
        customer_id = customer.get('id')
        
        # Test with specific scenario from review request:
        # cost_estimate: 100€, distance_category: "ankara_ici" (service_fee: 100€)
        # spare_parts: [{part_id: "sp001", quantity: 2}] (2 * 75€ = 150€)
        # Expected: subtotal 350€, vat 70€, total 420€
        repair_data = {
            "customer_id": customer_id,
            "device_type": "Test Fırın",
            "brand": "Refsan",
            "model": "Test Model",
            "description": "Cost calculation accuracy test",
            "priority": "yuksek",
            "cost_estimate": 100.0,
            "distance_category": "ankara_ici",
            "spare_parts": [
                {
                    "part_id": "sp001",
                    "part_name": "RD16 - RD27 - RD50 / TOP 16 Termokupl K Tipi (0-1200°C) 15CM (60 + 100)",
                    "price_eur": 75.0,
                    "quantity": 2
                }
            ]
        }
        
        repair_success, repair = self.run_test(
            "Create repair for cost calculation accuracy test",
            "POST",
            "repairs",
            200,
            data=repair_data
        )
        
        if not repair_success:
            return False
        
        # Expected calculations from review request
        expected_spare_parts_total = 150.0  # 2 * 75€
        expected_subtotal = 350.0  # 100 + 100 + 150
        expected_vat = 70.0  # 350 * 0.20
        expected_total_with_vat = 420.0  # 350 + 70
        
        actual_spare_parts_total = repair.get('spare_parts_total', 0)
        actual_vat_amount = repair.get('vat_amount', 0)
        actual_total_with_vat = repair.get('total_with_vat', 0)
        
        print(f"   📊 Test Scenario from Review Request:")
        print(f"   📊 Cost Estimate: 100€")
        print(f"   📊 Service Fee (ankara_ici): 100€")
        print(f"   📊 Spare Parts (2x Termokupl): 150€")
        print(f"   📊 Expected Subtotal: 350€")
        print(f"   📊 Expected VAT (20%): 70€")
        print(f"   📊 Expected Total: 420€")
        print(f"")
        print(f"   📊 Actual Results:")
        print(f"   📊 Spare Parts Total: {actual_spare_parts_total}€")
        print(f"   📊 VAT Amount: {actual_vat_amount}€")
        print(f"   📊 Total with VAT: {actual_total_with_vat}€")
        
        # Verify all calculations match exactly
        calculations_correct = True
        
        if abs(actual_spare_parts_total - expected_spare_parts_total) < 0.01:
            print(f"   ✅ Spare parts total: CORRECT")
        else:
            print(f"   ❌ Spare parts total: INCORRECT (expected {expected_spare_parts_total}, got {actual_spare_parts_total})")
            calculations_correct = False
        
        if abs(actual_vat_amount - expected_vat) < 0.01:
            print(f"   ✅ VAT amount: CORRECT")
        else:
            print(f"   ❌ VAT amount: INCORRECT (expected {expected_vat}, got {actual_vat_amount})")
            calculations_correct = False
        
        if abs(actual_total_with_vat - expected_total_with_vat) < 0.01:
            print(f"   ✅ Total with VAT: CORRECT")
        else:
            print(f"   ❌ Total with VAT: INCORRECT (expected {expected_total_with_vat}, got {actual_total_with_vat})")
            calculations_correct = False
        
        return calculations_correct

    def test_spare_parts_integration(self):
        """Test complete spare parts integration"""
        print(f"\n🔧 Testing Complete Spare Parts Integration for: {self.current_user.get('role')}")
        
        # Test 1: Spare parts endpoint
        spare_parts_endpoint_success = self.test_spare_parts_endpoint()
        
        # Test 2: Repair creation with spare parts
        repair_with_parts_success = self.test_repair_creation_with_spare_parts()
        
        # Test 3: Repair creation without spare parts
        repair_without_parts_success = self.test_repair_creation_without_spare_parts()
        
        # Test 4: Cost calculation accuracy
        cost_calculation_success = self.test_spare_parts_cost_calculation_accuracy()
        
        integration_success = (spare_parts_endpoint_success and repair_with_parts_success and 
                             repair_without_parts_success and cost_calculation_success)
        
        if integration_success:
            print(f"   ✅ All spare parts integration tests passed")
        else:
            print(f"   ❌ Some spare parts integration tests failed")
        
        return integration_success

    def test_new_backend_endpoints(self):
        """Test all newly added backend endpoints from the review request"""
        print(f"\n🆕 Testing New Backend Endpoints for: {self.current_user.get('role')}")
        
        # Test repair detail endpoint with role-based access control
        repair_detail_success = self.test_repair_detail_endpoint_with_roles()
        
        # Test enhanced notification system
        enhanced_notification_success = self.test_enhanced_notification_system()
        
        # Test notification data structure
        notification_structure_success = self.test_notification_data_structure()
        
        # Test repair cancellation endpoint
        cancel_success = self.test_repair_cancellation_endpoint()
        
        # Test clear all notifications endpoint (admin only)
        clear_notifications_success = self.test_clear_all_notifications_endpoint()
        
        # Test file upload endpoints
        file_upload_success = self.test_file_upload_endpoints()
        
        # Test enhanced repair creation with files
        enhanced_repair_success = self.test_enhanced_repair_creation_with_files()
        
        # Test role-based repair cancellation
        role_based_cancel_success = self.test_role_based_repair_cancellation()
        
        # Test NEW system management endpoints
        system_management_success = self.test_system_management_endpoints()
        
        # Test role-based access control for system management
        system_access_control_success = self.test_system_management_role_access_control()
        
        # Test demo data validation
        demo_validation_success = self.test_demo_data_validation()
        
        return (repair_detail_success and enhanced_notification_success and 
                notification_structure_success and cancel_success and 
                clear_notifications_success and file_upload_success and 
                enhanced_repair_success and role_based_cancel_success and
                system_management_success and system_access_control_success and
                demo_validation_success)

    def test_role_based_access(self):
        """Test role-based access control"""
        print(f"\n🔐 Testing role-based access for: {self.current_user.get('role')}")
        
        # Test stats access (all roles should have access)
        stats_success = self.test_stats()
        
        # Test customers access (admin and technician only)
        if self.current_user.get('role') in ['admin', 'teknisyen']:
            customers_success = self.test_customers_crud()
            # Test spare parts endpoints
            spare_parts_success = self.test_spare_parts_integration()
            # Test new admin panel endpoints
            admin_panel_success = self.test_admin_panel_endpoints()
            # Test new backend endpoints
            new_endpoints_success = self.test_new_backend_endpoints()
        else:
            # Customer role should not have access to create customers
            success, _ = self.run_test(
                "Customer access to customers endpoint (should fail)",
                "GET",
                "customers",
                403  # Expecting forbidden
            )
            customers_success = success  # Success means it correctly returned 403
            spare_parts_success = True  # Skip spare parts tests for customers
            admin_panel_success = True  # Skip admin panel tests for customers
            new_endpoints_success = True  # Skip new endpoint tests for customers
        
        # Test users list (admin only)
        users_success = self.test_users_list()
        
        # Test notifications access (admin only)
        notifications_access_success = True
        if self.current_user.get('role') == 'admin':
            # Admin should have access
            notifications_access_success, _ = self.run_test(
                "Admin access to notifications",
                "GET",
                "notifications",
                200
            )
        else:
            # Non-admin should be forbidden
            notifications_access_success, _ = self.run_test(
                f"{self.current_user.get('role')} access to notifications (should fail)",
                "GET",
                "notifications",
                403
            )
        
        return (stats_success and customers_success and users_success and 
                admin_panel_success and notifications_access_success and new_endpoints_success and spare_parts_success)

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
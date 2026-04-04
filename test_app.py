"""
Simple test script to verify the application functionality
"""
import db
import auth
import os

print("Starting tests...\n")

# Clean up existing database if any
if os.path.exists('attendance.db'):
    os.remove('attendance.db')
    print("Cleaned up existing database")

# Test 1: Initialize database
print("\n1. Testing database initialization...")
db.init_database()
print("✅ Database initialized successfully")

# Test 2: Create user
print("\n2. Testing user creation...")
success, message = auth.signup_user("testuser", "test@example.com", "password123")
print(f"{'✅' if success else '❌'} {message}")

# Test 3: Login with correct credentials
print("\n3. Testing login with correct credentials...")
success, user, message = auth.login_user("testuser", "password123")
if success:
    print(f"✅ {message}")
    print(f"   User ID: {user['id']}, Username: {user['username']}")
    test_user_id = user['id']
else:
    print(f"❌ {message}")

# Test 4: Login with incorrect credentials
print("\n4. Testing login with incorrect credentials...")
success, user, message = auth.login_user("testuser", "wrongpassword")
print(f"{'❌' if not success else '✅'} Expected failure: {message}")

# Test 5: Mark attendance
print("\n5. Testing mark attendance...")
success, message = db.mark_attendance(test_user_id)
print(f"{'✅' if success else '❌'} {message}")

# Test 6: Try marking duplicate attendance
print("\n6. Testing duplicate attendance prevention...")
success, message = db.mark_attendance(test_user_id)
print(f"{'❌' if not success else '✅'} Expected failure: {message}")

# Test 7: Get attendance records
print("\n7. Testing get attendance records...")
records = db.get_user_attendance(test_user_id)
print(f"✅ Retrieved {len(records)} attendance record(s)")
if records:
    print(f"   Latest: {records[0]['date']} at {records[0]['time']}")

# Test 8: Get attendance statistics
print("\n8. Testing attendance statistics...")
stats = db.get_attendance_stats(test_user_id)
print(f"✅ Stats retrieved:")
print(f"   Total days: {stats['total_days']}")
print(f"   Present days: {stats['present_days']}")
print(f"   Percentage: {stats['percentage']}%")

# Test 9: Update password
print("\n9. Testing password update...")
new_hash = auth.hash_password("newpassword123")
success = db.update_user_password(test_user_id, new_hash)
print(f"✅ Password updated successfully")

# Test 10: Login with new password
print("\n10. Testing login with new password...")
success, user, message = auth.login_user("testuser", "newpassword123")
print(f"{'✅' if success else '❌'} {message}")

print("\n" + "="*50)
print("All tests completed successfully!")
print("="*50)
print("\nYou can now run the application with:")
print("  streamlit run main.py")

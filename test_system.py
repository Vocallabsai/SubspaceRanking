"""
Test script to validate environment and database connection.
"""
import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup."""
    print("🔧 Testing Environment Setup")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    endpoint = os.getenv('HASURA_ENDPOINT')
    secret = os.getenv('HASURA_ADMIN_SECRET')
    
    if not endpoint:
        print("❌ HASURA_ENDPOINT not found in .env file")
        return False
    
    if not secret or secret == 'your_admin_secret_here':
        print("❌ HASURA_ADMIN_SECRET not configured in .env file")
        print("   Please update .env with your actual admin secret")
        return False
    
    print("✅ Environment variables configured")
    print(f"   Endpoint: {endpoint}")
    print(f"   Secret: {'*' * len(secret)}")
    
    return True

def test_imports():
    """Test Python package imports."""
    print("\n📦 Testing Package Imports")
    print("=" * 30)
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        import numpy as np
        print("✅ numpy imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_connection():
    """Test Hasura connection."""
    print("\n🌐 Testing Hasura Connection")
    print("=" * 30)
    
    try:
        from data_fetcher import HasuraClient
        
        client = HasuraClient()
        print("✅ HasuraClient initialized successfully")
        
        # Test a simple query
        test_query = """
        query {
          __schema {
            queryType {
              name
            }
          }
        }
        """
        
        result = client.execute_query(test_query)
        print("✅ GraphQL connection successful")
        print(f"   Schema accessible: {result.get('__schema', {}).get('queryType', {}).get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify HASURA_ADMIN_SECRET in .env file")
        print("3. Confirm Hasura endpoint is accessible")
        return False

def test_data_access():
    """Test data table access."""
    print("\n📊 Testing Data Table Access")
    print("=" * 30)
    
    try:
        from data_fetcher import AdminDataFetcher
        
        fetcher = AdminDataFetcher()
        
        # Test call data access (limit to 1 record for testing)
        call_data = fetcher.get_all_call_data(limit=1)
        print(f"✅ Call data access: {len(call_data)} records")
        
        # Test chat ratings access
        rating_data = fetcher.get_all_chat_ratings(limit=1)
        print(f"✅ Chat ratings access: {len(rating_data)} records")
        
        # Test leave requests access
        leave_data = fetcher.get_all_leave_requests()
        print(f"✅ Leave requests access: {len(leave_data)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Data access failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Admin Ranking System - Environment Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_environment():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    if test_connection():
        tests_passed += 1
    
    if test_data_access():
        tests_passed += 1
    
    print(f"\n📋 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main.py' for full ranking")
        print("2. Run 'python main.py top 5' for top 5 admins")
        print("3. Check README.md for more usage examples")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Update .env file with correct HASURA_ADMIN_SECRET")
        print("2. Check internet connection")
        print("3. Verify Hasura endpoint permissions")

if __name__ == "__main__":
    main()
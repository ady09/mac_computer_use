#!/usr/bin/env python3
"""
Test environment variable loading.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_env_loading():
    """Test .env file loading."""
    print("🧪 Testing .env file loading...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        with open('.env', 'r') as f:
            content = f.read()
            if 'ANTHROPIC_API_KEY' in content:
                print("✅ ANTHROPIC_API_KEY found in .env")
                
                # Check if it's a placeholder
                if 'your_api_key_here' in content:
                    print("⚠️ API key is still set to placeholder. Please update .env with your actual API key.")
                else:
                    print("✅ API key appears to be configured")
            else:
                print("❌ ANTHROPIC_API_KEY not found in .env")
    else:
        print("❌ .env file not found. Run ./setup_orcasheets.sh to create it.")
        return False
    
    # Test loading with utility function
    try:
        from orcasheets.utils import get_api_key, validate_api_key
        
        try:
            api_key = get_api_key()
            if validate_api_key(api_key):
                print("✅ API key loaded and validated successfully")
                print(f"   Key starts with: {api_key[:10]}...")
            else:
                print("⚠️ API key loaded but validation failed")
                print("   Make sure it starts with 'sk-ant-' and is the correct format")
        except ValueError as e:
            print(f"❌ {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def main():
    """Run the test."""
    print("🚀 Environment Loading Test")
    print("=" * 40)
    
    success = test_env_loading()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Environment loading test passed!")
        print("\nYou can now run the OrcaSheets framework:")
        print("  streamlit run orcasheets_streamlit.py")
    else:
        print("❌ Environment loading test failed.")
        print("\nPlease:")
        print("1. Run: ./setup_orcasheets.sh")
        print("2. Edit .env file and add your Anthropic API key")
        print("3. Run this test again")

if __name__ == "__main__":
    main()
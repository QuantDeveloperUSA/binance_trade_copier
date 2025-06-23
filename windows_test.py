#!/usr/bin/env python3
"""
Windows COM and Environment Tester
Tests various Windows-specific configurations that might affect Python server deployment
"""

import sys
import os
import platform
import subprocess
try:
    import winreg
except ImportError:
    print("Warning: winreg not available - Windows registry checks will be skipped")
    winreg = None
from pathlib import Path

def check_python_environment():
    """Check Python installation and environment"""
    print("=" * 50)
    print("PYTHON ENVIRONMENT CHECK")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[:3]}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check if running as admin
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        print(f"Running as administrator: {is_admin}")
    except:
        print("Admin check failed")

def check_windows_com():
    """Check Windows COM configuration"""
    print("\n" + "=" * 50)
    print("WINDOWS COM CONFIGURATION")
    print("=" * 50)
    
    if not winreg:
        print("Registry access not available - skipping COM checks")
        return
    
    try:
        # Check COM security settings
        key_path = r"SOFTWARE\Microsoft\Ole"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            try:
                auth_level = winreg.QueryValueEx(key, "DefaultAuthenticationLevel")[0]
                print(f"COM Authentication Level: {auth_level}")
            except FileNotFoundError:
                print("COM Authentication Level: Not configured (default)")
            
            try:
                impersonation = winreg.QueryValueEx(key, "DefaultImpersonationLevel")[0]
                print(f"COM Impersonation Level: {impersonation}")
            except FileNotFoundError:
                print("COM Impersonation Level: Not configured (default)")
                
    except Exception as e:
        print(f"COM configuration check failed: {e}")

def check_visual_cpp():
    """Check Visual C++ redistributables"""
    print("\n" + "=" * 50)
    print("VISUAL C++ REDISTRIBUTABLES")
    print("=" * 50)
    
    if not winreg:
        print("Registry access not available - skipping VC++ checks")
        return
    
    try:
        key_path = r"SOFTWARE\Microsoft\VisualStudio"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            subkeys = []
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    if "Redistributable" in subkey or "VC" in subkey:
                        subkeys.append(subkey)
                    i += 1
                except OSError:
                    break
            
            if subkeys:
                print("Found Visual C++ components:")
                for subkey in subkeys:
                    print(f"  - {subkey}")
            else:
                print("No Visual C++ redistributables found in registry")
                
    except Exception as e:
        print(f"Visual C++ check failed: {e}")

def check_asyncio_compatibility():
    """Test asyncio functionality"""
    print("\n" + "=" * 50)
    print("ASYNCIO COMPATIBILITY TEST")
    print("=" * 50)
    
    try:
        import asyncio
        
        async def test_async():
            print("✅ Basic async function works")
            await asyncio.sleep(0.1)
            print("✅ Async sleep works")
        
        # Test event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_async())
            loop.close()
            print("✅ Event loop creation and execution works")
        except Exception as e:
            print(f"❌ Event loop test failed: {e}")
            
    except ImportError:
        print("❌ Asyncio not available")

def check_server_dependencies():
    """Test server-specific dependencies"""
    print("\n" + "=" * 50)
    print("SERVER DEPENDENCIES TEST")
    print("=" * 50)
    
    dependencies = ["fastapi", "uvicorn", "binance", "pydantic", "jinja2"]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - MISSING")

def check_network_binding():
    """Test network binding capability"""
    print("\n" + "=" * 50)
    print("NETWORK BINDING TEST")
    print("=" * 50)
    
    try:
        import socket
        
        # Test localhost binding
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))  # Bind to any available port
        port = sock.getsockname()[1]
        sock.close()
        print(f"✅ Localhost binding works (tested port {port})")
        
        # Test 0.0.0.0 binding
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 0))
        port = sock.getsockname()[1]
        sock.close()
        print(f"✅ 0.0.0.0 binding works (tested port {port})")
        
        # Test port 8000 specifically
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', 8000))
            sock.close()
            print("✅ Port 8000 is available")
        except OSError as e:
            print(f"❌ Port 8000 binding failed: {e}")
            
    except Exception as e:
        print(f"Network binding test failed: {e}")

if __name__ == "__main__":
    print("Windows COM and Environment Tester")
    print("This script tests Windows-specific configurations for Python server deployment")
    print()
    
    check_python_environment()
    check_windows_com()
    check_visual_cpp()
    check_asyncio_compatibility()
    check_server_dependencies()
    check_network_binding()
    
    print("\n" + "=" * 50)
    print("TESTING COMPLETE")
    print("=" * 50)
    print("If any issues were found above, they may need to be resolved")
    print("for the server to run properly in Windows service mode.")

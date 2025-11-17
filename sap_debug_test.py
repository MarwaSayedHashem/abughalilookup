#!/usr/bin/env python3
"""
SAP API Debug Test Script
Run this independently to test the SAP API connection
"""

import requests
import urllib3
import xml.etree.ElementTree as ET

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
SAP_BASE_URL = "https://prd.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV"
CUSTOMER_MK = "18643"
SAP_SESSION_COOKIE = "hs_W2VvZMZDFqtRSKnJ2lsiIj4XD_RHwkJu1n9yMioQ%3d"


def test_method_1_with_cookies_param():
    """Test using requests cookies parameter"""
    print("\n" + "=" * 80)
    print("METHOD 1: Using requests cookies parameter")
    print("=" * 80)

    param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{CUSTOMER_MK}'"
    url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"

    headers = {
        "X-Requested-With": "X",
        "Authorization": "Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0"
    }

    cookies = {
        "SAP_SESSIONID_PS4_100": SAP_SESSION_COOKIE,
        "sap-usercontext": "sap-client=100"
    }

    print(f"URL: {url}")
    print(f"Cookies: {cookies}")

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.content)}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False


def test_method_2_with_cookie_header():
    """Test using Cookie header (like curl)"""
    print("\n" + "=" * 80)
    print("METHOD 2: Using Cookie header (curl style)")
    print("=" * 80)

    param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{CUSTOMER_MK}'"
    url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"

    headers = {
        "X-Requested-With": "X",
        "Authorization": "Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0",
        "Cookie": f"SAP_SESSIONID_PS4_100={SAP_SESSION_COOKIE}; sap-usercontext=sap-client=100"
    }

    print(f"URL: {url}")
    print(f"Cookie Header: {headers['Cookie']}")

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.content)}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            # Try to parse and extract Customer code
            try:
                root = ET.fromstring(response.content)
                namespaces = {
                    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices'
                }
                customer_elem = root.find('.//d:Customer', namespaces)
                if customer_elem is not None and customer_elem.text:
                    print(f"✅ SAP Customer Code Found: {customer_elem.text}")
                else:
                    print("⚠️ No Customer code in response")
            except Exception as e:
                print(f"⚠️ Could not parse XML: {str(e)}")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_method_3_with_session():
    """Test using requests Session object"""
    print("\n" + "=" * 80)
    print("METHOD 3: Using requests Session")
    print("=" * 80)

    param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{CUSTOMER_MK}'"
    url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"

    session = requests.Session()
    session.verify = False

    session.headers.update({
        "X-Requested-With": "X",
        "Authorization": "Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0"
    })

    session.cookies.set("SAP_SESSIONID_PS4_100", SAP_SESSION_COOKIE, domain="prd.sap.aboughalymotors.com")
    session.cookies.set("sap-usercontext", "sap-client=100", domain="prd.sap.aboughalymotors.com")

    print(f"URL: {url}")
    print(f"Session Cookies: {session.cookies}")

    try:
        response = session.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.content)}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False


def test_method_4_url_decoded_cookie():
    """Test with URL-decoded cookie value (= instead of %3d)"""
    print("\n" + "=" * 80)
    print("METHOD 4: Using URL-decoded cookie (= instead of %3d)")
    print("=" * 80)

    # Try with URL-decoded cookie
    cookie_decoded = SAP_SESSION_COOKIE.replace("%3d", "=").replace("%3D", "=")

    param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{CUSTOMER_MK}'"
    url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"

    headers = {
        "X-Requested-With": "X",
        "Authorization": "Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0",
        "Cookie": f"SAP_SESSIONID_PS4_100={cookie_decoded}; sap-usercontext=sap-client=100"
    }

    print(f"URL: {url}")
    print(f"Cookie (decoded): {cookie_decoded}")
    print(f"Cookie Header: {headers['Cookie']}")

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.content)}")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🔍 SAP API Connection Debug Tool")
    print("=" * 80)
    print(f"Testing connection to SAP with Customer MK: {CUSTOMER_MK}")
    print(f"Cookie: {SAP_SESSION_COOKIE[:30]}...")
    print("=" * 80)

    results = []

    # Test all methods
    results.append(("Method 1 (cookies param)", test_method_1_with_cookies_param()))
    results.append(("Method 2 (Cookie header)", test_method_2_with_cookie_header()))
    results.append(("Method 3 (Session)", test_method_3_with_session()))
    results.append(("Method 4 (URL decoded)", test_method_4_url_decoded_cookie()))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for method, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{method}: {status}")

    successful_methods = [m for m, s in results if s]
    if successful_methods:
        print(f"\n✅ Working method(s): {', '.join(successful_methods)}")
        print("\nUse the working method in your Django views.py!")
    else:
        print("\n❌ No methods worked. Possible issues:")
        print("   1. Cookie has expired - get a fresh one from Postman")
        print("   2. Network/firewall issue")
        print("   3. Cookie value copied incorrectly")
        print("\n💡 Try copying the cookie again from Postman Cookies section")
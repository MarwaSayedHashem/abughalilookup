from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import xml.etree.ElementTree as ET
import json
import urllib3
import sys
from typing import Optional, Tuple

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass  # If reconfiguration fails, continue anyway

# API Configuration
AUTOLINE_BASE_URL = "http://41.33.17.242:7050"
AUTOLINE_TOKEN = "6cktR-wnMWYTRM9Ys8wlwudEOjo-1Ox6wuLLQsF7dqwen2gxLlrZhXoQgXDtK9Vd59k2fpPT1Ts0uwcyb_HdMrEuSlxDcxzd-4LqD8oY-jT1mb7_jSmGre9UtntznE20hcT4Yoxua3BAbDKkqZv19fWdfI6n8-HpZ-Vddzh6aggzdrBMQTB9hM6at5np49rRDH0biFFX9QcJyqdh3D81RbSYF14ZBVUNVIb_TP6mOm0b-DRHPPdQis64ln0qVfMc"
SAP_BASE_URL = "https://prd.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV"

# Try to import SAP session cookie from config file
try:
    from sap_config import SAP_SESSION_COOKIE
except ImportError:
    SAP_SESSION_COOKIE = "hs_W2VvZMZDFqtRSKnJ2lsiIj4XD_RHwkJu1n9yMioQ%3d"


def index(request):
    """Main page"""
    return render(request, 'lookup/index.html')


@csrf_exempt
def search_customer(request):
    """API endpoint to search for customer"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        customer_mk = data.get('customer_mk', '').strip()
        is_corporate = data.get('is_corporate', False)

        if not customer_mk:
            return JsonResponse({'error': 'Customer MK is required'}, status=400)

        # Fetch Autoline data
        autoline_data = fetch_autoline_data(customer_mk, is_corporate)
        if not autoline_data:
            return JsonResponse({'error': 'Failed to retrieve Autoline data'}, status=500)

        # Fetch SAP data and extract Customer code
        sap_customer_code, sap_error, sap_status = fetch_sap_customer_code(customer_mk)

        # Add SAP_customer to Autoline data
        if isinstance(autoline_data, list) and len(autoline_data) > 0:
            if isinstance(autoline_data[0], dict):
                autoline_data[0]['SAP_customer'] = sap_customer_code if sap_customer_code else None
        elif isinstance(autoline_data, dict):
            autoline_data['SAP_customer'] = sap_customer_code if sap_customer_code else None

        # Prepare response with detailed SAP status
        response_data = {
            'success': True,
            'customer_data': autoline_data,
            'sap_customer_code': sap_customer_code,
            'has_sap_record': sap_customer_code is not None,
            'sap_status': sap_status
        }

        # Add error message if SAP lookup failed
        if sap_error:
            response_data['sap_error'] = sap_error

        return JsonResponse(response_data)

    except Exception as e:
        import traceback
        print(f"Error in search_customer: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def generate_sap_code(request):
    """API endpoint to generate SAP customer code"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        customer_mk = data.get('customer_mk', '').strip()

        if not customer_mk:
            return JsonResponse({'error': 'Customer MK is required'}, status=400)

        # TODO: Implement actual SAP code generation
        return JsonResponse({
            'success': True,
            'message': 'SAP code generation will be implemented here. This will create the customer in SAP under the Mercedes-Benz schema for both Sales and After-Sales.'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def fetch_autoline_data(customer_mk: str, is_corporate: bool) -> Optional[dict]:
    """Fetch customer data from Autoline API"""
    try:
        if is_corporate:
            url = f"{AUTOLINE_BASE_URL}/SpotFlow/salesLedger/byid/{customer_mk}"
        else:
            url = f"{AUTOLINE_BASE_URL}/SpotFlow/CustomerBySocialId/byid/{customer_mk}"

        headers = {
            "Authorization": f"Bearer {AUTOLINE_TOKEN}"
        }

        print(f"Fetching Autoline data from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        print(f"Autoline response: {json.dumps(data, indent=2)}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Autoline API Error: {str(e)}")
        return None


def fetch_sap_customer_code(customer_mk: str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Fetch SAP customer code from SAP API (returns XML, parse to get d:Customer)

    Returns:
        Tuple of (customer_code, error_message, status)
        - customer_code: The SAP customer code if found, None otherwise
        - error_message: Error message if any, None otherwise
        - status: Status string ('found', 'not_found', 'session_expired', 'error')
    """
    try:
        # Build SAP OData URL with parameters (matching exact format from API)
        param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{customer_mk}'"
        url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"

        print(f"\n{'=' * 80}")
        print(f"SAP API REQUEST DEBUG")
        print(f"{'=' * 80}")
        print(f"URL: {url}")
        print(f"Cookie value: {SAP_SESSION_COOKIE}")
        print(f"Cookie length: {len(SAP_SESSION_COOKIE)}")
        print(f"{'=' * 80}\n")

        # Match the exact working curl command with fresh credentials
        headers = {
            "X-Requested-With": "X",
            "Authorization": "Basic QWdtLmFiYXA6V2VsY29tZV8wNQ==",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Try both methods: Cookie header (curl style) and cookies parameter
        # First, try with cookies parameter (requests library handles encoding)
        import urllib.parse
        # URL-decode the cookie value if it's encoded
        cookie_value_decoded = urllib.parse.unquote(SAP_SESSION_COOKIE)
        print(f"Cookie value (encoded): {SAP_SESSION_COOKIE}")
        print(f"Cookie value (decoded): {cookie_value_decoded}")
        
        # Method 1: Use cookies parameter (requests handles encoding automatically)
        cookies_dict = {
            "SAP_SESSIONID_PS4_100": cookie_value_decoded,  # Use decoded value
            "sap-usercontext": "sap-client=100"
        }
        
        # Also set Cookie header as backup (curl style)
        cookie_header = f"SAP_SESSIONID_PS4_100={SAP_SESSION_COOKIE}; sap-usercontext=sap-client=100"
        headers["Cookie"] = cookie_header

        print(f"Full Request Headers:")
        for key, value in headers.items():
            if key == "Cookie":
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        print(f"Cookies Dict: {cookies_dict}")
        print(f"\n")

        # Try with both Cookie header AND cookies parameter
        response = requests.get(url, headers=headers, cookies=cookies_dict, timeout=30, verify=False)

        print(f"SAP API Status Code: {response.status_code}")
        print(f"SAP API Response Headers: {dict(response.headers)}")
        
        # Safely print response text (handle Unicode encoding errors)
        try:
            response_preview = response.text[:1000] if response.text else "[no text]"
            print(f"SAP API Response (first 1000 chars): {response_preview}\n")
        except UnicodeEncodeError:
            # Fallback: encode to ASCII with replacement
            try:
                safe_preview = response.text[:1000].encode('ascii', errors='replace').decode('ascii')
                print(f"SAP API Response (first 1000 chars, ASCII): {safe_preview}\n")
            except Exception:
                print(f"SAP API Response: [encoding error, length: {len(response.text) if response.text else 0}]\n")

        if response.status_code == 200:
            # Parse XML response
            try:
                xml_content = response.content
                print(f"SAP Response Length: {len(xml_content)} bytes")
                
                # Safely decode and print XML (handle Unicode errors)
                try:
                    xml_preview = xml_content[:1000].decode('utf-8', errors='replace')
                    print(f"SAP Response (first 1000 chars): {xml_preview}")
                except Exception as e:
                    print(f"SAP Response preview (encoding error): {str(e)}")

                # Check if response is empty
                if not xml_content or len(xml_content.strip()) == 0:
                    print("ERROR: SAP response is empty!")
                    return None, "SAP response is empty", 'error'

                root = ET.fromstring(xml_content)

                # Define namespaces
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
                    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices'
                }

                # Debug: Print all elements to see structure (safely handle Unicode)
                print("\n=== XML Structure Debug ===")
                customer_found_tags = []
                for elem in root.iter():
                    tag = elem.tag
                    text = elem.text if elem.text else ""
                    
                    # Safely encode text for printing
                    try:
                        safe_text = text.strip() if text else ""
                        safe_tag = tag
                    except Exception:
                        safe_text = "[encoding error]"
                        safe_tag = tag
                    
                    if 'Customer' in tag:
                        try:
                            customer_found_tags.append(f"Tag: {tag}, Text: '{safe_text}'")
                        except Exception:
                            customer_found_tags.append(f"Tag: {tag}, Text: [encoding error]")
                    
                    if safe_text and len(safe_text) < 50:  # Only print short values
                        try:
                            print(f"Tag: {safe_tag}, Text: {safe_text}")
                        except UnicodeEncodeError:
                            # Fallback: print with ASCII replacement
                            print(f"Tag: {safe_tag}, Text: {safe_text.encode('ascii', errors='replace').decode('ascii')}")
                
                if customer_found_tags:
                    print("\n=== Customer-related tags found ===")
                    for tag_info in customer_found_tags:
                        try:
                            print(tag_info)
                        except UnicodeEncodeError:
                            print(tag_info.encode('ascii', errors='replace').decode('ascii'))
                print("=== End XML Debug ===\n")

                # Try multiple approaches to find the Customer element
                customer_elem = None
                customer_value = None
                method_used = None

                # Method 1: Search in m:properties/d:Customer (most specific)
                customer_elem = root.find('.//m:properties/d:Customer', namespaces)
                if customer_elem is not None:
                    raw_text = customer_elem.text
                    if raw_text is not None:
                        customer_value = raw_text.strip()
                        if customer_value:
                            method_used = "method 1 (m:properties/d:Customer)"
                            print(f"✅ Found Customer using {method_used}: '{customer_value}'")

                # Method 2: Search for any Customer element with d namespace
                if not customer_value:
                    customer_elem = root.find('.//d:Customer', namespaces)
                    if customer_elem is not None:
                        raw_text = customer_elem.text
                        if raw_text is not None:
                            customer_value = raw_text.strip()
                            if customer_value:
                                method_used = "method 2 (.//d:Customer)"
                                print(f"✅ Found Customer using {method_used}: '{customer_value}'")

                # Method 3: Search without namespace prefix (iterate all elements)
                if not customer_value:
                    for elem in root.iter():
                        tag = elem.tag
                        if '}' in tag:
                            local_tag = tag.split('}')[1]
                        else:
                            local_tag = tag

                        if local_tag == 'Customer':
                            raw_text = elem.text
                            if raw_text is not None:
                                customer_value = raw_text.strip()
                                if customer_value:
                                    customer_elem = elem
                                    method_used = "method 3 (iter with local tag)"
                                    print(f"✅ Found Customer using {method_used}: '{customer_value}', Full tag: {tag}")
                                    break

                # Method 4: Search for any element containing "Customer" in tag
                if not customer_value:
                    for elem in root.iter():
                        if 'Customer' in elem.tag:
                            raw_text = elem.text
                            if raw_text is not None:
                                customer_value = raw_text.strip()
                                if customer_value:
                                    customer_elem = elem
                                    method_used = f"method 4 (contains 'Customer'): {elem.tag}"
                                    print(f"✅ Found Customer using {method_used}: '{customer_value}'")
                                    break

                # Final check - return the value if we found it
                if customer_value:
                    print(f"✅✅✅ Successfully extracted SAP Customer Code: '{customer_value}' using {method_used}")
                    return customer_value, None, 'found'
                else:
                    print("❌ Customer element not found or value is empty")
                    if customer_elem is not None:
                        print(f"   customer_elem found but text is: {repr(customer_elem.text)}")
                    return None, None, 'not_found'

            except ET.ParseError as e:
                error_msg = f"XML Parse Error: {str(e)}"
                print(error_msg)
                return None, error_msg, 'error'
            except Exception as e:
                error_msg = f"Unexpected error parsing XML: {str(e)}"
                print(error_msg)
                import traceback
                print(traceback.format_exc())
                return None, error_msg, 'error'

        elif response.status_code == 403:
            error_msg = "SAP session cookie has expired. Please update the cookie in sap_config.py"
            print(f"SAP API returned 403 Forbidden for MK: {customer_mk}")
            print(f"Current cookie: {SAP_SESSION_COOKIE[:50]}...")
            print(error_msg)
            return None, error_msg, 'session_expired'

        elif response.status_code == 404:
            print(f"SAP API returned 404 - Customer not found in SAP for MK: {customer_mk}")
            return None, None, 'not_found'

        else:
            error_msg = f"SAP API returned status {response.status_code}"
            print(f"{error_msg} for MK: {customer_mk}")
            print(f"Response: {response.text[:500]}")
            return None, error_msg, 'error'

    except requests.exceptions.RequestException as e:
        if "404" in str(e) or "Not Found" in str(e):
            print(f"SAP API - Customer not found for MK: {customer_mk}")
            return None, None, 'not_found'
        error_msg = f"SAP API Request Error: {str(e)}"
        print(error_msg)
        return None, error_msg, 'error'
    except Exception as e:
        error_msg = f"Unexpected error in fetch_sap_customer_code: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return None, error_msg, 'error'
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import xml.etree.ElementTree as ET
import json
import urllib3
import sys
import re
from typing import Optional, Tuple

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass  # If reconfiguration fails, continue anyway

# Load configuration from config.json
import os
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    """Load configuration from config.json file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"WARNING: config.json not found at {CONFIG_FILE}, using defaults")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        return None

# Load configuration
_config = load_config()

# API Configuration - with fallback to defaults
if _config:
    AUTOLINE_BASE_URL = _config.get('autoline', {}).get('base_url', 'http://41.33.17.242:7050')
    AUTOLINE_TOKEN = _config.get('autoline', {}).get('token', '')
    SAP_BASE_URL = _config.get('sap', {}).get('search_base_url', 'https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV')
    SAP_CREATE_BASE_URL = _config.get('sap', {}).get('create_base_url', 'https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZAUTOLINE_CUSTOMER_LAKE_CREATE_SRV')
    SAP_SEARCH_CLIENT = _config.get('sap', {}).get('search_client', '110')
    SAP_CREATE_CLIENT = _config.get('sap', {}).get('create_client', '110')
    SAP_SEARCH_AUTH = _config.get('sap', {}).get('search_authorization', 'Basic QWdtLmFiYXA6V2VsY29tZV8wNQ==')
    SAP_CREATE_AUTH = _config.get('sap', {}).get('create_authorization', 'Basic YWdtLmFiYXA6V2VsY29tZV8wNQ==')
    SAP_SEARCH_COOKIE = _config.get('sap', {}).get('search_cookie', '')
    SAP_CREATE_COOKIE = _config.get('sap', {}).get('create_cookie', '')
else:
    # Fallback defaults
    AUTOLINE_BASE_URL = "http://41.33.17.242:7050"
    AUTOLINE_TOKEN = "6cktR-wnMWYTRM9Ys8wlwudEOjo-1Ox6wuLLQsF7dqwen2gxLlrZhXoQgXDtK9Vd59k2fpPT1Ts0uwcyb_HdMrEuSlxDcxzd-4LqD8oY-jT1mb7_jSmGre9UtntznE20hcT4Yoxua3BAbDKkqZv19fWdfI6n8-HpZ-Vddzh6aggzdrBMQTB9hM6at5np49rRDH0biFFX9QcJyqdh3D81RbSYF14ZBVUNVIb_TP6mOm0b-DRHPPdQis64ln0qVfMc"
    SAP_BASE_URL = "https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV"
    SAP_CREATE_BASE_URL = "https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZAUTOLINE_CUSTOMER_LAKE_CREATE_SRV"
    SAP_SEARCH_CLIENT = "110"
    SAP_CREATE_CLIENT = "110"
    SAP_SEARCH_AUTH = "Basic QWdtLmFiYXA6V2VsY29tZV8wNQ=="
    SAP_CREATE_AUTH = "Basic YWdtLmFiYXA6V2VsY29tZV8wNQ=="
    SAP_SEARCH_COOKIE = ""
    SAP_CREATE_COOKIE = "ApplicationGatewayAffinity=ffb3d8af5d7e7d2d2b15ad8cfda5375cc03082a051c80b6207a0f6d1c3b22590; ApplicationGatewayAffinityCORS=ffb3d8af5d7e7d2d2b15ad8cfda5375cc03082a051c80b6207a0f6d1c3b22590; SAP_SESSIONID_DS4_110=Za6GnZKR755AXkoBEUryBaJT3oPEFRHwjVXFg8wvBYQ%3d; sap-usercontext=sap-client=110"

# Try to import SAP session cookie from legacy config file (for backward compatibility)
try:
    from sap_config import SAP_SESSION_COOKIE
    if not SAP_SEARCH_COOKIE:
        SAP_SEARCH_COOKIE = SAP_SESSION_COOKIE
except ImportError:
    pass


def index(request):
    """Main page"""
    # Load app name and company from config
    app_name = "SAP–Autoline Customer Lake"
    company_name = "Abou Ghaly Motors"
    
    if _config and 'app' in _config:
        app_name = _config['app'].get('name', app_name)
        company_name = _config['app'].get('company', company_name)
    
    context = {
        'app_name': app_name,
        'company_name': company_name
    }
    return render(request, 'lookup/index.html', context)


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
        
        # DO NOT automatically create - only create when user clicks "Generate SAP Code" button

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
        is_corporate = data.get('is_corporate', False)

        print(f"\n{'=' * 80}")
        print(f"GENERATE SAP CODE REQUEST")
        print(f"{'=' * 80}")
        print(f"Customer MK: {customer_mk}")
        print(f"Is Corporate: {is_corporate}")
        print(f"Request Data: {data}")
        print(f"{'=' * 80}\n")

        if not customer_mk:
            return JsonResponse({'error': 'Customer MK is required'}, status=400)

        # Fetch customer data from Autoline first
        print(f"Fetching Autoline data for customer MK: {customer_mk}, Corporate: {is_corporate}")
        autoline_data = fetch_autoline_data(customer_mk, is_corporate)
        
        if not autoline_data:
            return JsonResponse({'error': 'Failed to retrieve customer data from Autoline'}, status=500)

        print(f"Autoline data received: {json.dumps(autoline_data, indent=2, ensure_ascii=False)}")

        # Get customer object
        customer = None
        if isinstance(autoline_data, list) and len(autoline_data) > 0:
            customer = autoline_data[0]
        elif isinstance(autoline_data, dict):
            customer = autoline_data

        if not customer:
            return JsonResponse({'error': 'No customer data available'}, status=400)

        print(f"Customer object: {json.dumps(customer, indent=2, ensure_ascii=False)}")

        # Build request body for SAP customer creation API (different for corporate vs regular)
        if is_corporate:
            sap_create_body = build_sap_create_body_corporate(customer, customer_mk)
        else:
            sap_create_body = build_sap_create_body(customer, customer_mk)
        
        if not sap_create_body:
            return JsonResponse({'error': 'Failed to build SAP create body'}, status=500)
        
        # Call SAP customer creation API
        result = create_sap_customer(sap_create_body)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': result.get('message', 'SAP customer code generated successfully'),
                'sap_customer_code': result.get('sap_customer_code')
            })
        else:
            return JsonResponse({
                'error': result.get('error', 'Failed to generate SAP customer code')
            }, status=500)

    except Exception as e:
        import traceback
        print(f"Error in generate_sap_code: {str(e)}")
        print(traceback.format_exc())
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
        url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client={SAP_SEARCH_CLIENT}"

        print(f"\n{'=' * 80}")
        print(f"SAP API REQUEST DEBUG")
        print(f"{'=' * 80}")
        print(f"URL: {url}")
        search_cookie = SAP_SEARCH_COOKIE if SAP_SEARCH_COOKIE else ""
        if not search_cookie:
            try:
                from sap_config import SAP_SESSION_COOKIE
                search_cookie = SAP_SESSION_COOKIE
            except ImportError:
                pass
        print(f"Cookie value: {search_cookie}")
        print(f"Cookie length: {len(search_cookie)}")
        print(f"{'=' * 80}\n")

        # Match the exact working curl command with fresh credentials
        headers = {
            "X-Requested-With": "X",
            "Authorization": SAP_SEARCH_AUTH,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Try both methods: Cookie header (curl style) and cookies parameter
        # First, try with cookies parameter (requests library handles encoding)
        import urllib.parse
        # Use cookie from config, or fallback to legacy
        search_cookie = SAP_SEARCH_COOKIE if SAP_SEARCH_COOKIE else ""
        if not search_cookie:
            # Try legacy import
            try:
                from sap_config import SAP_SESSION_COOKIE
                search_cookie = SAP_SESSION_COOKIE
            except ImportError:
                pass
        
        # URL-decode the cookie value if it's encoded
        cookie_value_decoded = urllib.parse.unquote(search_cookie) if search_cookie else ""
        print(f"Cookie value (encoded): {search_cookie}")
        print(f"Cookie value (decoded): {cookie_value_decoded}")
        
        # Method 1: Use cookies parameter (requests handles encoding automatically)
        cookies_dict = {
            "SAP_SESSIONID_PS4_100": cookie_value_decoded,  # Use decoded value
            "sap-usercontext": f"sap-client={SAP_SEARCH_CLIENT}"
        }
        
        # Also set Cookie header as backup (curl style)
        cookie_header = f"SAP_SESSIONID_PS4_100={search_cookie}; sap-usercontext=sap-client={SAP_SEARCH_CLIENT}"
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
            error_msg = "SAP session cookie has expired. Please update the cookie in config.json"
            print(f"SAP API returned 403 Forbidden for MK: {customer_mk}")
            search_cookie = SAP_SEARCH_COOKIE if SAP_SEARCH_COOKIE else ""
            if search_cookie:
                print(f"Current cookie: {search_cookie[:50]}...")
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


def build_sap_create_body(customer: dict, customer_mk: str) -> dict:
    """
    Build the request body for SAP customer creation API from Autoline customer data
    
    Mapping:
    - NationalId: from SocialId
    - AutolineMk: from customer_mk parameter
    - Name: FirstName + SurName
    - Firstname: FirstName
    - Lastname: SurName
    - Gendertype: Sex
    - City: "Cairo" (fixed)
    - District: "cairo" (fixed)
    - Street: concatenated address (Address001-005)
    - Telephone: from Phone001 (or first available phone)
    - TelNo: same as Telephone
    - EMail: from email
    - FullArabicName: from Salute
    - RefUser: "SAP–Autoline Customer Lake" (fixed)
    """
    print(f"\n{'=' * 80}")
    print(f"BUILDING SAP CREATE BODY")
    print(f"{'=' * 80}")
    print(f"Customer MK: {customer_mk}")
    print(f"Customer data keys: {list(customer.keys())}")
    print(f"{'=' * 80}\n")
    
    # Get mobile number (check Phone001, Phone002, Phone003, Phone004)
    mobile_number = None
    for phone_key in ['Phone001', 'Phone002', 'Phone003', 'Phone004']:
        if phone_key in customer and customer[phone_key]:
            phone_value = str(customer[phone_key]).strip()
            if phone_value and phone_value != ' ' and phone_value != '':
                mobile_number = phone_value
                print(f"Found mobile number in {phone_key}: {mobile_number}")
                break
    
    if not mobile_number:
        print("WARNING: No mobile number found in customer data")
    
    # Concatenate address - only use Address001, Address002, Address003 for Street
    # Address004 and Address005 are typically City/Region and Country, not street address
    address_parts = []
    seen_values = set()  # Track seen values to avoid duplicates
    
    for addr_key in ['Address001', 'Address002', 'Address003']:
        if addr_key in customer and customer[addr_key]:
            addr_value = str(customer[addr_key]).strip()
            if addr_value and addr_value != ' ' and addr_value != '':
                # Normalize and check for duplicates
                normalized = addr_value.lower().strip()
                if normalized not in seen_values:
                    address_parts.append(addr_value)
                    seen_values.add(normalized)
                else:
                    print(f"Skipping duplicate address value: {addr_value}")
    
    # Join with single space and clean up multiple spaces
    street = ' '.join(address_parts) if address_parts else ''
    street = ' '.join(street.split())  # Remove extra spaces
    print(f"Concatenated address (Street): '{street}'")
    print(f"Street length: {len(street)} characters")
    
    # Build name - check both FirstName and first_name (case variations)
    first_name = customer.get('FirstName', '') or customer.get('first_name', '') or customer.get('FirstName', '')
    if first_name:
        first_name = str(first_name).strip()
    
    last_name = customer.get('SurName', '') or customer.get('sur_name', '') or customer.get('Surname', '')
    if last_name:
        last_name = str(last_name).strip()
    
    full_name = f"{first_name} {last_name}".strip()
    print(f"First Name: {first_name}, Last Name: {last_name}, Full Name: {full_name}")
    
    # Get other fields
    national_id = customer.get('SocialId', '') or customer.get('social_id', '')
    if national_id:
        national_id = str(national_id).strip()
    
    gender = customer.get('Sex', 'M') or customer.get('sex', 'M')
    if gender:
        gender = str(gender).strip()
    else:
        gender = 'M'
    
    # Validate email before including it
    email = customer.get('email', '') or customer.get('Email', '')
    if email:
        email = str(email).strip()
        # Basic email validation regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            print(f"WARNING: Invalid email format '{email}', not including in request")
            email = ''
        else:
            print(f"Valid email found: {email}")
    else:
        print("No email found in customer data")
    
    arabic_name = customer.get('Salute', '') or customer.get('salute', '')
    if arabic_name:
        arabic_name = str(arabic_name).strip()
    
    body = {
        "NationalId": national_id,
        "AutolineMk": str(customer_mk),
        "Name": full_name,
        "Firstname": first_name,
        "Lastname": last_name,
        "Gendertype": gender,
        "City": "Cairo",
        "District": "cairo",
        "Street": street,
        "Telephone": mobile_number if mobile_number else '',
        "TelNo": mobile_number if mobile_number else '',
        "EMail": email,
        "FullArabicName": arabic_name,
        "RefUser": "SAP–Autoline Customer Lake"
    }
    
    print(f"\n{'=' * 80}")
    print(f"SAP CREATE BODY (FINAL)")
    print(f"{'=' * 80}")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"{'=' * 80}\n")
    
    return body


def build_sap_create_body_corporate(customer: dict, customer_mk: str) -> dict:
    """
    Build the request body for SAP corporate customer creation API from Autoline customer data
    
    Mapping:
    - TaxRegister: from RegestreationNumber
    - AutolineMk: from customer_mk parameter
    - Name: from CustomerName
    - Firstname: from NAME 1 (FirstName + LastName concatenated in Arabic)
    - Lastname: from NAME 2 (EnglishFirstNmae + EnglishLastName concatenated in English)
    - City: "Cairo" (fixed)
    - District: "cairo" (fixed)
    - Street: concatenated from Address, District, Region, BuildingNumber
    - Telephone: from MobileNumber
    - TelNo: same as Telephone
    - EMail: from Email
    - FullArabicName: from CustomerName
    - RefUser: "SAP–Autoline Customer Lake" (fixed)
    """
    print(f"\n{'=' * 80}")
    print(f"BUILDING SAP CREATE BODY (CORPORATE)")
    print(f"{'=' * 80}")
    print(f"Customer MK: {customer_mk}")
    print(f"Customer data keys: {list(customer.keys())}")
    print(f"{'=' * 80}\n")
    
    # Get mobile number
    mobile_number = customer.get('MobileNumber', '') or customer.get('mobileNumber', '')
    if mobile_number:
        mobile_number = str(mobile_number).strip()
        print(f"Found mobile number: {mobile_number}")
    else:
        print("WARNING: No mobile number found in customer data")
    
    # Concatenate address from Address, District, Region, BuildingNumber
    address_parts = []
    seen_values = set()
    
    for addr_key in ['Address', 'District', 'Region', 'BuildingNumber']:
        if addr_key in customer and customer[addr_key]:
            addr_value = str(customer[addr_key]).strip()
            if addr_value and addr_value != ' ' and addr_value != '':
                normalized = addr_value.lower().strip()
                if normalized not in seen_values:
                    address_parts.append(addr_value)
                    seen_values.add(normalized)
                else:
                    print(f"Skipping duplicate address value: {addr_value}")
    
    street = ' '.join(address_parts) if address_parts else ''
    street = ' '.join(street.split())  # Remove extra spaces
    print(f"Concatenated address (Street): '{street}'")
    
    # Get NAME 1 (Arabic: FirstName + LastName)
    first_name_ar = customer.get('FirstName', '') or customer.get('first_name', '')
    last_name_ar = customer.get('LastName', '') or customer.get('last_name', '')
    name1_parts = []
    if first_name_ar:
        name1_parts.append(str(first_name_ar).strip())
    if last_name_ar:
        name1_parts.append(str(last_name_ar).strip())
    name1 = ' '.join(name1_parts).strip()
    print(f"NAME 1 (Arabic): '{name1}'")
    
    # Get NAME 2 (English: EnglishFirstNmae + EnglishLastName)
    first_name_en = customer.get('EnglishFirstNmae', '') or customer.get('EnglishFirstName', '') or customer.get('englishFirstNmae', '')
    last_name_en = customer.get('EnglishLastName', '') or customer.get('englishLastName', '')
    name2_parts = []
    if first_name_en:
        name2_parts.append(str(first_name_en).strip())
    if last_name_en:
        name2_parts.append(str(last_name_en).strip())
    name2 = ' '.join(name2_parts).strip()
    print(f"NAME 2 (English): '{name2}'")
    
    # Get other fields
    tax_register = customer.get('RegestreationNumber', '') or customer.get('regestreationNumber', '')
    if tax_register:
        tax_register = str(tax_register).strip()
    
    customer_name = customer.get('CustomerName', '') or customer.get('customerName', '')
    if customer_name:
        customer_name = str(customer_name).strip()
    
    # Validate email
    email = customer.get('Email', '') or customer.get('email', '')
    if email:
        email = str(email).strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            print(f"WARNING: Invalid email format '{email}', not including in request")
            email = ''
        else:
            print(f"Valid email found: {email}")
    else:
        print("No email found in customer data")
    
    body = {
        "TaxRegister": tax_register,
        "AutolineMk": str(customer_mk),
        "Name": customer_name,
        "Firstname": name1,
        "Lastname": name2,
        "City": "Cairo",
        "District": "cairo",
        "Street": street,
        "Telephone": mobile_number if mobile_number else '',
        "TelNo": mobile_number if mobile_number else '',
        "EMail": email,
        "FullArabicName": customer_name,  # From CustomerName
        "RefUser": "SAP–Autoline Customer Lake"
    }
    
    print(f"\n{'=' * 80}")
    print(f"SAP CREATE BODY (CORPORATE - FINAL)")
    print(f"{'=' * 80}")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"{'=' * 80}\n")
    
    return body


def create_sap_customer_from_autoline(autoline_data: dict, customer_mk: str, is_corporate: bool = False) -> dict:
    """
    Helper function to create SAP customer from Autoline data
    """
    customer = None
    if isinstance(autoline_data, list) and len(autoline_data) > 0:
        customer = autoline_data[0]
    elif isinstance(autoline_data, dict):
        customer = autoline_data
    
    if not customer:
        return {'success': False, 'error': 'No customer data available'}
    
    if is_corporate:
        body = build_sap_create_body_corporate(customer, customer_mk)
    else:
        body = build_sap_create_body(customer, customer_mk)
    
    return create_sap_customer(body)


def create_sap_customer(body: dict) -> dict:
    """
    Create customer in SAP using the customer creation API
    
    Returns:
        dict with 'success', 'message', 'sap_customer_code' (if successful), or 'error'
    """
    try:
        url = f"{SAP_CREATE_BASE_URL}/ENTITYSet?sap-client=110"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "X",
            "Authorization": "Basic YWdtLmFiYXA6V2VsY29tZV8wNQ==",
            "Cookie": "ApplicationGatewayAffinity=ffb3d8af5d7e7d2d2b15ad8cfda5375cc03082a051c80b6207a0f6d1c3b22590; ApplicationGatewayAffinityCORS=ffb3d8af5d7e7d2d2b15ad8cfda5375cc03082a051c80b6207a0f6d1c3b22590; SAP_SESSIONID_DS4_110=Za6GnZKR755AXkoBEUryBaJT3oPEFRHwjVXFg8wvBYQ%3d; sap-usercontext=sap-client=110"
        }
        
        print(f"\n{'=' * 80}")
        print(f"SAP CREATE API REQUEST")
        print(f"{'=' * 80}")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
        print(f"{'=' * 80}\n")
        
        # Send as JSON string in data parameter (like curl --data-raw)
        body_json = json.dumps(body, ensure_ascii=False)
        print(f"\n{'=' * 80}")
        print(f"FINAL REQUEST DETAILS")
        print(f"{'=' * 80}")
        print(f"URL: {url}")
        print(f"Body JSON (full): {body_json}")
        print(f"Body length: {len(body_json)} bytes")
        print(f"{'=' * 80}\n")
        
        # Make sure we're sending the body correctly
        response = requests.post(
            url, 
            headers=headers, 
            data=body_json.encode('utf-8'), 
            timeout=30, 
            verify=False
        )
        
        print(f"\n{'=' * 80}")
        print(f"REQUEST SENT - CHECKING RESPONSE")
        print(f"{'=' * 80}")
        print(f"Request URL: {response.request.url}")
        print(f"Request method: {response.request.method}")
        print(f"Request headers: {dict(response.request.headers)}")
        if response.request.body:
            print(f"Request body sent: {response.request.body.decode('utf-8', errors='ignore')[:500]}")
        else:
            print("WARNING: Request body is EMPTY!")
        print(f"{'=' * 80}\n")
        
        print(f"SAP CREATE API Status Code: {response.status_code}")
        print(f"SAP CREATE API Response (full): {response.text}\n")
        
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                print(f"Parsed JSON response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Try to extract customer code from response - check multiple possible structures
                sap_customer_code = None
                
                if isinstance(response_data, dict):
                    # Method 1: Check direct keys
                    for key in ['Customer', 'CustomerCode', 'BusinessPartner', 'CustomerNumber', 'AutolineMk']:
                        if key in response_data:
                            value = response_data[key]
                            if isinstance(value, (str, int)) and value:
                                sap_customer_code = str(value)
                                print(f"Found customer code in key '{key}': {sap_customer_code}")
                                break
                    
                    # Method 2: Check nested in 'd' key (OData format)
                    if not sap_customer_code and 'd' in response_data:
                        d_data = response_data['d']
                        if isinstance(d_data, dict):
                            for key in ['Customer', 'CustomerCode', 'BusinessPartner', 'CustomerNumber']:
                                if key in d_data:
                                    value = d_data[key]
                                    if isinstance(value, (str, int)) and value:
                                        sap_customer_code = str(value)
                                        print(f"Found customer code in d.{key}: {sap_customer_code}")
                                        break
                    
                    # Method 3: Check nested in 'results' or 'value' (array responses)
                    if not sap_customer_code:
                        for array_key in ['results', 'value', 'items']:
                            if array_key in response_data and isinstance(response_data[array_key], list):
                                for item in response_data[array_key]:
                                    if isinstance(item, dict):
                                        for key in ['Customer', 'CustomerCode', 'BusinessPartner', 'CustomerNumber']:
                                            if key in item:
                                                value = item[key]
                                                if isinstance(value, (str, int)) and value:
                                                    sap_customer_code = str(value)
                                                    print(f"Found customer code in {array_key}[].{key}: {sap_customer_code}")
                                                    break
                                        if sap_customer_code:
                                            break
                            if sap_customer_code:
                                break
                    
                    # Method 4: Recursively search for any field containing "Customer" or numeric value
                    if not sap_customer_code:
                        def find_customer_code(obj, path=""):
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    if 'customer' in k.lower() and isinstance(v, (str, int)) and v:
                                        # Check if it looks like a customer code (numeric or alphanumeric)
                                        val_str = str(v)
                                        if val_str.isdigit() or (len(val_str) > 5 and any(c.isdigit() for c in val_str)):
                                            return val_str
                                    result = find_customer_code(v, f"{path}.{k}")
                                    if result:
                                        return result
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    result = find_customer_code(item, f"{path}[{i}]")
                                    if result:
                                        return result
                            return None
                        
                        sap_customer_code = find_customer_code(response_data)
                        if sap_customer_code:
                            print(f"Found customer code via recursive search: {sap_customer_code}")
                
                if sap_customer_code:
                    print(f"✅ Successfully extracted SAP Customer Code: {sap_customer_code}")
                else:
                    print("⚠️ Could not extract customer code from response, but request was successful")
                
                return {
                    'success': True,
                    'message': 'SAP customer created successfully',
                    'sap_customer_code': sap_customer_code
                }
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                print(f"Response text: {response.text}")
                # Response might not be JSON, but status is success
                return {
                    'success': True,
                    'message': 'SAP customer creation request completed (response not in JSON format)',
                    'sap_customer_code': None
                }
        else:
            error_msg = f"SAP API returned status {response.status_code}: {response.text[:500]}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = f"SAP API Request Error: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Unexpected error in create_sap_customer: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        return {
            'success': False,
            'error': error_msg
        }
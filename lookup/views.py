from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import xml.etree.ElementTree as ET
import json
import urllib3
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        sap_customer_code = fetch_sap_customer_code(customer_mk)
        
        # Add SAP_customer to Autoline data
        if isinstance(autoline_data, list) and len(autoline_data) > 0:
            if isinstance(autoline_data[0], dict):
                autoline_data[0]['SAP_customer'] = sap_customer_code if sap_customer_code else None
        elif isinstance(autoline_data, dict):
            autoline_data['SAP_customer'] = sap_customer_code if sap_customer_code else None
        
        return JsonResponse({
            'success': True,
            'customer_data': autoline_data,
            'sap_customer_code': sap_customer_code,
            'has_sap_record': sap_customer_code is not None
        })
        
    except Exception as e:
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
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Autoline API Error: {str(e)}")
        return None


def fetch_sap_customer_code(customer_mk: str) -> Optional[str]:
    """Fetch SAP customer code from SAP API (returns XML, parse to get d:Customer)"""
    try:
        # Build SAP OData URL with parameters (matching exact format from API)
        param_string = f"BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='{customer_mk}'"
        url = f"{SAP_BASE_URL}/ENTITYSet({param_string})?sap-client=100"
        
        # Match the exact working curl command
        headers = {
            "X-Requested-With": "X",
            "Authorization": "Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0"
        }
        
        # Add cookies exactly as in the working curl command
        cookies = {
            "SAP_SESSIONID_PS4_100": SAP_SESSION_COOKIE,
            "sap-usercontext": "sap-client=100"
        }
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30, verify=False)
        
        if response.status_code == 200:
            # Parse XML response
            try:
                xml_content = response.content
                root = ET.fromstring(xml_content)
                
                # Define namespaces
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
                    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices'
                }
                
                # Try multiple approaches to find the Customer element
                customer_elem = None
                customer_value = None
                
                # Method 1: Search in m:properties/d:Customer
                customer_elem = root.find('.//m:properties/d:Customer', namespaces)
                if customer_elem is not None:
                    customer_value = customer_elem.text
                
                # Method 2: Search for any Customer element with d namespace
                if customer_elem is None:
                    customer_elem = root.find('.//d:Customer', namespaces)
                    if customer_elem is not None:
                        customer_value = customer_elem.text
                
                # Method 3: Search without namespace prefix
                if customer_elem is None:
                    for elem in root.iter():
                        tag = elem.tag
                        if '}' in tag:
                            local_tag = tag.split('}')[1]
                        else:
                            local_tag = tag
                        
                        if local_tag == 'Customer':
                            customer_elem = elem
                            customer_value = elem.text
                            break
                
                if customer_elem is not None and customer_value:
                    cleaned_value = customer_value.strip()
                    if cleaned_value:
                        return cleaned_value
                
                return None
                
            except ET.ParseError as e:
                print(f"XML Parse Error: {str(e)}")
                return None
            except Exception as e:
                print(f"Unexpected error parsing XML: {str(e)}")
                return None
        elif response.status_code == 403:
            print(f"SAP API returned 403 Forbidden for MK: {customer_mk}")
            print(f"Session cookie may be expired. Please update SAP_SESSION_COOKIE in sap_config.py")
            return None
        elif response.status_code == 404:
            return None
        else:
            print(f"SAP API returned status {response.status_code} for MK: {customer_mk}")
            return None
            
    except requests.exceptions.RequestException as e:
        if "404" in str(e) or "Not Found" in str(e):
            return None
        print(f"SAP API Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error in fetch_sap_customer_code: {str(e)}")
        return None

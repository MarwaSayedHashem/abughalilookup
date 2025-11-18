# SAP Session Cookie Setup

The SAP API requires a session cookie (`SAP_SESSIONID_PS4_100`) that may expire.

## How to Get a Fresh Session Cookie

1. Open **Postman**
2. Make a successful request to the SAP API:
   ```
   GET https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV/ENTITYSet(BusinessPartner='',MobileNumber='',NationalID='',AutolineMK='18643')?sap-client=110
   ```
   Headers:
   - `X-Requested-With: X`
   - `Authorization: Basic TUIuSU5URzpQQHNzdzByZEBBR00xMjM0`

3. After a successful request, go to **Cookies** in Postman
4. Find the cookie named `SAP_SESSIONID_PS4_100`
5. Copy its value
6. Open `sap_config.py` in this project
7. Update the `SAP_SESSION_COOKIE` variable with the new value
8. Restart the Flask application

## Alternative: Update in app.py

If you prefer, you can directly update the cookie value in `app.py` at line 123.

## Note

The session cookie typically expires after some time. If you get a 403 Forbidden error, you need to get a fresh cookie from Postman.


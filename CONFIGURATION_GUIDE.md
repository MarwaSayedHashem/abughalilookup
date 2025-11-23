# Configuration Guide

This guide will help you configure the Customer Lookup System without any programming knowledge.

## 📁 Configuration File Location

The configuration file is located at: **`config.json`** in the project root folder.

## 🔧 How to Edit Configuration

1. Open the `config.json` file with any text editor (Notepad, TextEdit, etc.)
2. Edit the values you need to change
3. Save the file
4. Restart the application

## 📋 Configuration Sections

### 1. Autoline API Settings

```json
"autoline": {
    "base_url": "http://41.33.17.242:7050",
    "token": "YOUR_TOKEN_HERE"
}
```

- **base_url**: The Autoline API server address
- **token**: Your Autoline API authentication token

### 2. SAP API Settings

```json
"sap": {
    "search_base_url": "https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV",
    "create_base_url": "https://dev.sap.aboughalymotors.com/sap/opu/odata/sap/ZAUTOLINE_CUSTOMER_LAKE_CREATE_SRV",
    "search_client": "110",
    "create_client": "110",
    "search_authorization": "Basic QWdtLmFiYXA6V2VsY29tZV8wNQ==",
    "create_authorization": "Basic YWdtLmFiYXA6V2VsY29tZV8wNQ==",
    "search_cookie": "YOUR_SEARCH_COOKIE_HERE",
    "create_cookie": "YOUR_CREATE_COOKIE_HERE"
}
```

#### SAP Search Settings:
- **search_base_url**: URL for searching customers in SAP
- **search_client**: SAP client number for search (usually "100" or "110")
- **search_authorization**: Authorization header (Basic Auth encoded)
- **search_cookie**: Session cookie for search API (get from Postman after successful request)

#### SAP Create Settings:
- **create_base_url**: URL for creating customers in SAP
- **create_client**: SAP client number for create (usually "100" or "110")
- **create_authorization**: Authorization header for create API
- **create_cookie**: Session cookie for create API

### 3. Application Settings

```json
"app": {
    "name": "SAP–Autoline Customer Lake",
    "company": "Abou Ghaly Motors"
}
```

- **name**: Application name (shown in header)
- **company**: Company name (shown in header)

## 🔑 How to Get SAP Cookies

### For Search API Cookie:

1. Open **Postman**
2. Make a successful request to the SAP Search API
3. Go to **Cookies** tab
4. Find cookie named `SAP_SESSIONID_PS4_100` (or similar)
5. Copy its value
6. Paste it in `search_cookie` field in `config.json`

### For Create API Cookie:

1. Open **Postman**
2. Make a successful request to the SAP Create API
3. Copy the entire Cookie header value
4. Paste it in `create_cookie` field in `config.json`

## ⚠️ Important Notes

1. **Always restart the application** after changing `config.json`
2. **Keep the JSON format correct** - don't remove commas or brackets
3. **Don't add extra spaces** in URLs or tokens
4. **Cookies expire** - you may need to update them periodically
5. **Backup your config.json** before making changes

## 🚨 Troubleshooting

### Application won't start after editing config.json
- Check that all quotes are properly closed
- Check that all commas are in place
- Use a JSON validator online to check your file

### API calls failing
- Verify URLs are correct (no extra spaces)
- Check that tokens/cookies are not expired
- Ensure client numbers match your SAP system

### Can't find config.json
- It should be in the same folder as `manage.py`
- If missing, create it using the template above

## 📞 Support

If you need help, contact your IT department with:
- The error message you're seeing
- What you were trying to change
- A copy of your `config.json` file (remove sensitive tokens before sharing)



# Customer Lookup System - AbuGhali Motors

A Python application for looking up customer information from Autoline and SAP systems. Available in two versions: **Desktop GUI** (tkinter) and **Web Interface** (Flask).

## Features

- **Customer Lookup**: Enter Customer MK to retrieve customer details
- **Corporate Customer Support**: Checkbox to toggle between regular and corporate customer lookup
- **Autoline Integration**: Fetches customer data from Autoline API
- **SAP Integration**: Searches for existing customer records in SAP
- **SAP Code Generation**: Button to generate SAP customer code when no record exists

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Desktop GUI Application (tkinter)

Run the desktop application:

```bash
python customer_lookup.py
```

### Option 2: Web Application (Flask)

Run the web server:

```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

**Templates Location:**
- HTML templates: `templates/index.html`
- CSS styles: `static/style.css`
- JavaScript: `static/script.js`

### How to Use

1. Enter the **Customer MK** in the input field
2. Check the **Corporate Customer** checkbox if applicable
3. Click **Go** to search for customer information
4. View the results:
   - **Autoline Customer Details**: Full response from Autoline API
   - **SAP Customer Details**: SAP customer record (if exists)
   - **SAP Customer Code**: Displays the SAP code if found
5. If no SAP record exists, click **Generate SAP Code** to create a new customer in SAP

## API Endpoints

### Autoline APIs

- **Regular Customer**: `GET /SpotFlow/CustomerBySocialId/byid/{CustomerMK}`
- **Corporate Customer**: `GET /SpotFlow/salesLedger/byid/{CustomerMK}`

### SAP API

- **Customer Search**: `GET /sap/opu/odata/sap/ZSD_SP_SEARCH_CUSTOMER_SRV/ENTITYSet(...)`

## Notes

- The application requires network access to Autoline and SAP servers
- API credentials are configured in the application
- SAP code generation functionality is ready for implementation


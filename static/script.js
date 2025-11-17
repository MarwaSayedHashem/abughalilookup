// Advanced JavaScript for Customer Lookup

// DOM Elements
const customerMkInput = document.getElementById('customer-mk');
const corporateCheckbox = document.getElementById('corporate-checkbox');
const searchBtn = document.getElementById('search-btn');
const resultsSection = document.getElementById('results-section');
const customerCard = document.getElementById('customer-card');
const customerDetails = document.getElementById('customer-details');
const sapCodeValue = document.getElementById('sap-code-value');
const generateSapBtn = document.getElementById('generate-sap-btn');
const statusBar = document.getElementById('status-bar');
const statusText = statusBar.querySelector('.status-text');
const statusIcon = statusBar.querySelector('.status-icon');
const toggleRawDataBtn = document.getElementById('toggle-raw-data');
const rawDataContent = document.getElementById('raw-data-content');
const rawJsonData = document.getElementById('raw-json-data');

let rawDataVisible = false;

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
customerMkInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});
generateSapBtn.addEventListener('click', handleGenerateSapCode);
toggleRawDataBtn.addEventListener('click', toggleRawData);

// Functions
function updateStatus(message, type = 'info') {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
        loading: '⏳'
    };
    statusIcon.textContent = icons[type] || icons.info;
    statusText.textContent = message;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function setLoading(isLoading) {
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        searchBtn.disabled = true;
        updateStatus('Searching for customer...', 'loading');
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        searchBtn.disabled = false;
    }
}

async function handleSearch() {
    const customerMk = customerMkInput.value.trim();
    
    if (!customerMk) {
        showToast('Please enter a Customer MK', 'error');
        customerMkInput.focus();
        return;
    }
    
    const isCorporate = corporateCheckbox.checked;
    
    // Reset UI
    resultsSection.style.display = 'none';
    customerDetails.innerHTML = '';
    rawDataContent.style.display = 'none';
    rawDataVisible = false;
    toggleRawDataBtn.classList.remove('active');
    toggleRawDataBtn.querySelector('.toggle-text').textContent = 'Show Raw JSON Data';
    
    setLoading(true);
    
    try {
        const response = await fetch('/api/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customer_mk: customerMk,
                is_corporate: isCorporate
            })
        });
        
        const data = await response.json();
        setLoading(false);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display customer data
        displayCustomerData(data.customer_data, data.sap_customer_code, data.has_sap_record);
        
        // Show raw JSON data
        rawJsonData.textContent = JSON.stringify(data.customer_data, null, 2);
        
        resultsSection.style.display = 'block';
        updateStatus('Customer lookup completed successfully', 'success');
        showToast('Customer data retrieved successfully!', 'success');
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
    } catch (error) {
        setLoading(false);
        showToast('Error: ' + error.message, 'error');
        updateStatus('Error: ' + error.message, 'error');
    }
}

function displayCustomerData(customerData, sapCode, hasSapRecord) {
    // Clear previous data
    customerDetails.innerHTML = '';
    
    // Update SAP badge
    const sapBadge = document.getElementById('sap-badge');
    if (hasSapRecord && sapCode) {
        sapCodeValue.textContent = sapCode;
        sapCodeValue.className = 'badge-value found';
        generateSapBtn.style.display = 'none';
        sapBadge.style.background = 'rgba(16, 185, 129, 0.1)';
        sapBadge.style.borderColor = 'var(--success)';
    } else {
        sapCodeValue.textContent = 'Not Found';
        sapCodeValue.className = 'badge-value not-found';
        generateSapBtn.style.display = 'block';
        sapBadge.style.background = 'rgba(239, 68, 68, 0.1)';
        sapBadge.style.borderColor = 'var(--danger)';
    }
    
    // Get the customer object (handle both array and object responses)
    let customer = null;
    if (Array.isArray(customerData) && customerData.length > 0) {
        customer = customerData[0];
    } else if (typeof customerData === 'object') {
        customer = customerData;
    }
    
    if (!customer) {
        customerDetails.innerHTML = '<p style="color: var(--danger); padding: 2rem; text-align: center;">No customer data available</p>';
        return;
    }
    
    // Create detail grid
    const detailGrid = document.createElement('div');
    detailGrid.className = 'detail-grid';
    
    // Define field mappings with labels
    const fieldMappings = {
        'CustomerNumber': 'Customer Number',
        'CustomerCode': 'Customer Code',
        'Status': 'Status',
        'Title': 'Title',
        'FirstName': 'First Name',
        'SurName': 'Surname',
        'Salute': 'Salutation',
        'Phone001': 'Phone 1',
        'Phone002': 'Phone 2',
        'Phone003': 'Phone 3',
        'Phone004': 'Phone 4',
        'Address001': 'Address Line 1',
        'Address002': 'Address Line 2',
        'Address003': 'Address Line 3',
        'Address004': 'City/Region',
        'Address005': 'Country',
        'Postcode': 'Postal Code',
        'email': 'Email',
        'CountryC': 'Country Code',
        'Sex': 'Gender',
        'SocialId': 'Social ID',
        'AccountCode': 'Account Code',
        'RegestreationNumber': 'Registration Number',
        'Address': 'Address',
        'District': 'District',
        'Region': 'Region',
        'BuildingNumber': 'Building Number',
        'CustomerName': 'Customer Name',
        'Email': 'Email',
        'EnglishFirstNmae': 'English First Name',
        'EnglishLastName': 'English Last Name',
        'MobileNumber': 'Mobile Number',
        'SAP_customer': 'SAP Customer Code'
    };
    
    // Create detail items for each field
    Object.keys(customer).forEach(key => {
        const value = customer[key];
        
        // Skip empty values or whitespace-only values
        if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
            return;
        }
        
        const label = fieldMappings[key] || key;
        const isHighlight = key === 'SAP_customer' || key === 'CustomerNumber' || key === 'CustomerCode';
        
        const detailItem = document.createElement('div');
        detailItem.className = 'detail-item';
        
        const detailLabel = document.createElement('div');
        detailLabel.className = 'detail-label';
        detailLabel.textContent = label;
        
        const detailValue = document.createElement('div');
        detailValue.className = 'detail-value' + (isHighlight ? ' highlight' : '');
        detailValue.textContent = value;
        
        detailItem.appendChild(detailLabel);
        detailItem.appendChild(detailValue);
        detailGrid.appendChild(detailItem);
    });
    
    customerDetails.appendChild(detailGrid);
}

function toggleRawData() {
    rawDataVisible = !rawDataVisible;
    
    if (rawDataVisible) {
        rawDataContent.style.display = 'block';
        toggleRawDataBtn.querySelector('.toggle-text').textContent = 'Hide Raw JSON Data';
        toggleRawDataBtn.classList.add('active');
    } else {
        rawDataContent.style.display = 'none';
        toggleRawDataBtn.querySelector('.toggle-text').textContent = 'Show Raw JSON Data';
        toggleRawDataBtn.classList.remove('active');
    }
}

async function handleGenerateSapCode() {
    const customerMk = customerMkInput.value.trim();
    
    if (!customerMk) {
        showToast('Please enter a Customer MK', 'error');
        return;
    }
    
    if (!confirm(`Generate SAP Customer Code for Customer MK: ${customerMk}?\n\nThis will create the customer in SAP under the Mercedes-Benz schema for both Sales and After-Sales.`)) {
        return;
    }
    
    updateStatus('Generating SAP Customer Code...', 'loading');
    generateSapBtn.disabled = true;
    generateSapBtn.innerHTML = '<span class="btn-icon">⏳</span><span>Generating...</span>';
    
    try {
        const response = await fetch('/api/generate-sap-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customer_mk: customerMk
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        showToast(data.message || 'SAP code generation initiated successfully', 'success');
        updateStatus('Ready', 'success');
        generateSapBtn.disabled = false;
        generateSapBtn.innerHTML = '<span class="btn-icon">✨</span><span>Generate SAP Code</span>';
        
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
        updateStatus('Error: ' + error.message, 'error');
        generateSapBtn.disabled = false;
        generateSapBtn.innerHTML = '<span class="btn-icon">✨</span><span>Generate SAP Code</span>';
    }
}

// Initialize
updateStatus('Ready', 'success');

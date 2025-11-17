// Advanced JavaScript for Customer Lookup with Enhanced Error Handling

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
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
    const toggleRawDataBtn = document.getElementById('toggle-raw-data');
    const rawDataContent = document.getElementById('raw-data-content');
    const rawJsonData = document.getElementById('raw-json-data');

    // Check if elements exist
    if (!customerMkInput || !searchBtn || !statusBar) {
        console.error('Required DOM elements not found');
        return;
    }

    const statusText = statusBar.querySelector('.status-text');
    const statusIcon = statusBar.querySelector('.status-icon');

    let rawDataVisible = false;

    // Event Listeners
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }
    if (customerMkInput) {
        customerMkInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    if (generateSapBtn) {
        generateSapBtn.addEventListener('click', handleGenerateSapCode);
    }
    if (toggleRawDataBtn) {
        toggleRawDataBtn.addEventListener('click', toggleRawData);
    }

    // Functions (moved inside DOMContentLoaded)
    function updateStatus(message, type = 'info') {
        if (!statusIcon || !statusText) return;
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
        if (container) {
            container.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
    }

    function setLoading(isLoading) {
        if (!searchBtn) return;
        const btnText = searchBtn.querySelector('.btn-text');
        const btnLoader = searchBtn.querySelector('.btn-loader');
        
        if (isLoading) {
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'flex';
            searchBtn.disabled = true;
            updateStatus('Searching for customer...', 'loading');
        } else {
            if (btnText) btnText.style.display = 'inline';
            if (btnLoader) btnLoader.style.display = 'none';
            searchBtn.disabled = false;
        }
    }

    async function handleSearch() {
        if (!customerMkInput) return;
        const customerMk = customerMkInput.value.trim();
        
        if (!customerMk) {
            showToast('Please enter a Customer MK', 'error');
            customerMkInput.focus();
            return;
        }
        
        const isCorporate = corporateCheckbox ? corporateCheckbox.checked : false;
        
        // Reset UI
        if (resultsSection) resultsSection.style.display = 'none';
        if (customerDetails) customerDetails.innerHTML = '';
        if (rawDataContent) rawDataContent.style.display = 'none';
        rawDataVisible = false;
        if (toggleRawDataBtn) {
            toggleRawDataBtn.classList.remove('active');
            const toggleText = toggleRawDataBtn.querySelector('.toggle-text');
            if (toggleText) toggleText.textContent = 'Show Raw JSON Data';
        }
        
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
            displayCustomerData(data.customer_data, data.sap_customer_code, data.has_sap_record, data.sap_status, data.sap_error);
            
            // Show raw JSON data
            if (rawJsonData) {
                rawJsonData.textContent = JSON.stringify(data, null, 2);
            }
            
            if (resultsSection) {
                resultsSection.style.display = 'block';
            }
            
            // Update status based on SAP result
            if (data.sap_status === 'found') {
                updateStatus('Customer lookup completed successfully with SAP code', 'success');
                showToast('Customer data retrieved successfully with SAP code!', 'success');
            } else if (data.sap_status === 'session_expired') {
                updateStatus('Customer found but SAP session expired', 'warning');
            } else if (data.sap_status === 'not_found') {
                updateStatus('Customer found in Autoline but not in SAP', 'warning');
                showToast('Customer found but no SAP code exists', 'warning');
            } else {
                updateStatus('Customer lookup completed with warnings', 'warning');
            }
            
            // Smooth scroll to results
            setTimeout(() => {
                if (resultsSection) {
                    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
            
        } catch (error) {
            setLoading(false);
            showToast('Error: ' + error.message, 'error');
            updateStatus('Error: ' + error.message, 'error');
            console.error('Search error:', error);
        }
    }

    function displayCustomerData(customerData, sapCode, hasSapRecord, sapStatus, sapError) {
        if (!customerDetails) return;
        
        // Clear previous data
        customerDetails.innerHTML = '';
        
        // Update SAP badge
        const sapBadge = document.getElementById('sap-badge');
        
        if (sapStatus === 'session_expired') {
            if (sapCodeValue) {
                sapCodeValue.textContent = 'Session Expired ⚠️';
                sapCodeValue.className = 'badge-value not-found';
            }
            if (generateSapBtn) generateSapBtn.style.display = 'none';
            if (sapBadge) {
                sapBadge.style.background = 'rgba(245, 158, 11, 0.1)';
                sapBadge.style.borderColor = 'var(--warning)';
            }
            
            // Add warning message
            const warningDiv = document.createElement('div');
            warningDiv.style.cssText = 'background: rgba(245, 158, 11, 0.1); border-left: 4px solid var(--warning); padding: 1rem; margin-bottom: 1rem; border-radius: 8px;';
            warningDiv.innerHTML = `
                <strong>⚠️ SAP Session Expired</strong><br>
                <span style="color: var(--text-muted); font-size: 0.9rem;">
                    The SAP session cookie has expired. Please update it in <code>sap_config.py</code> file.<br>
                    See <code>README_SAP_SESSION.md</code> for instructions on how to get a fresh cookie from Postman.
                </span>
            `;
            customerDetails.appendChild(warningDiv);
            
        } else if (hasSapRecord && sapCode) {
            if (sapCodeValue) {
                sapCodeValue.textContent = sapCode;
                sapCodeValue.className = 'badge-value found';
            }
            if (generateSapBtn) generateSapBtn.style.display = 'none';
            if (sapBadge) {
                sapBadge.style.background = 'rgba(76, 175, 80, 0.1)';
                sapBadge.style.borderColor = 'var(--success)';
            }
        } else {
            if (sapCodeValue) {
                sapCodeValue.textContent = 'Not Found';
                sapCodeValue.className = 'badge-value not-found';
            }
            if (generateSapBtn) generateSapBtn.style.display = 'block';
            if (sapBadge) {
                sapBadge.style.background = 'rgba(244, 67, 54, 0.1)';
                sapBadge.style.borderColor = 'var(--danger)';
            }
        }
        
        // Get the customer object (handle both array and object responses)
        let customer = null;
        if (Array.isArray(customerData) && customerData.length > 0) {
            customer = customerData[0];
        } else if (typeof customerData === 'object') {
            customer = customerData;
        }
        
        if (!customer) {
            customerDetails.innerHTML += '<p style="color: var(--danger); padding: 1.5rem; text-align: center; font-size: 0.875rem;">No customer data available</p>';
            return;
        }
        
        // Create detail grid
        const detailGrid = document.createElement('div');
        detailGrid.className = 'detail-grid';
        detailGrid.id = 'detail-grid';
        
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
            'SocialId': 'Social ID / National ID',
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
        Object.keys(customer).forEach((key, index) => {
            const value = customer[key];
            
            // Skip empty values or whitespace-only values
            if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
                return;
            }
            
            const label = fieldMappings[key] || key;
            const isHighlight = key === 'SAP_customer' || key === 'CustomerNumber' || key === 'CustomerCode';
            
            const detailItem = document.createElement('div');
            detailItem.className = 'detail-item';
            detailItem.draggable = true;
            detailItem.dataset.index = index;
            detailItem.dataset.key = key;
            
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
        
        // Initialize drag and drop
        initDragAndDrop();
    }

    // Drag and Drop functionality
    function initDragAndDrop() {
        const detailItems = document.querySelectorAll('.detail-item');
        const detailGrid = document.getElementById('detail-grid');
        
        if (!detailGrid || detailItems.length === 0) return;
        
        let draggedElement = null;
        
        detailItems.forEach((item) => {
            // Drag start
            item.addEventListener('dragstart', (e) => {
                draggedElement = item;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', item.innerHTML);
            });
            
            // Drag end
            item.addEventListener('dragend', (e) => {
                item.classList.remove('dragging');
                detailItems.forEach(i => i.classList.remove('drag-over'));
            });
            
            // Drag over
            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                
                const afterElement = getDragAfterElement(detailGrid, e.clientY);
                const dragging = document.querySelector('.dragging');
                
                if (afterElement == null) {
                    detailGrid.appendChild(dragging);
                } else {
                    detailGrid.insertBefore(dragging, afterElement);
                }
            });
            
            // Drag enter
            item.addEventListener('dragenter', (e) => {
                if (item !== draggedElement) {
                    item.classList.add('drag-over');
                }
            });
            
            // Drag leave
            item.addEventListener('dragleave', (e) => {
                item.classList.remove('drag-over');
            });
            
            // Drop
            item.addEventListener('drop', (e) => {
                e.preventDefault();
                item.classList.remove('drag-over');
            });
        });
        
        // Handle drop on grid
        detailGrid.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
    }

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.detail-item:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    function toggleRawData() {
        rawDataVisible = !rawDataVisible;
        
        if (rawDataVisible) {
            if (rawDataContent) rawDataContent.style.display = 'block';
            if (toggleRawDataBtn) {
                const toggleText = toggleRawDataBtn.querySelector('.toggle-text');
                if (toggleText) toggleText.textContent = 'Hide Raw JSON Data';
                toggleRawDataBtn.classList.add('active');
            }
        } else {
            if (rawDataContent) rawDataContent.style.display = 'none';
            if (toggleRawDataBtn) {
                const toggleText = toggleRawDataBtn.querySelector('.toggle-text');
                if (toggleText) toggleText.textContent = 'Show Raw JSON Data';
                toggleRawDataBtn.classList.remove('active');
            }
        }
    }

    async function handleGenerateSapCode() {
        if (!customerMkInput) return;
        const customerMk = customerMkInput.value.trim();
        
        if (!customerMk) {
            showToast('Please enter a Customer MK', 'error');
            return;
        }
        
        if (!confirm(`Generate SAP Customer Code for Customer MK: ${customerMk}?\n\nThis will create the customer in SAP under the Mercedes-Benz schema for both Sales and After-Sales.`)) {
            return;
        }
        
        updateStatus('Generating SAP Customer Code...', 'loading');
        if (generateSapBtn) {
            generateSapBtn.disabled = true;
            generateSapBtn.innerHTML = '<span class="btn-icon">⏳</span><span>Generating...</span>';
        }
        
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
            if (generateSapBtn) {
                generateSapBtn.disabled = false;
                generateSapBtn.innerHTML = '<span class="btn-icon">✨</span><span>Generate SAP Code</span>';
            }
            
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
            updateStatus('Error: ' + error.message, 'error');
            if (generateSapBtn) {
                generateSapBtn.disabled = false;
                generateSapBtn.innerHTML = '<span class="btn-icon">✨</span><span>Generate SAP Code</span>';
            }
        }
    }

    // Initialize
    updateStatus('Ready', 'success');
    console.log('Customer Lookup System initialized');
});
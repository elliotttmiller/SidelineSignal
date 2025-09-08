// SidelineSignal - Live Status Monitoring JavaScript
// Implements autonomous real-time polling for status updates

let isLoading = false;

/**
 * Fetches status data from the API and updates the table
 */
async function fetchStatuses() {
    if (isLoading) return; // Prevent concurrent requests
    
    isLoading = true;
    const statusTableBody = document.querySelector('.status-table tbody');
    
    try {
        // Show loading state
        statusTableBody.innerHTML = '<tr><td colspan="4" class="loading-state">Loading status updates...</td></tr>';
        
        // Fetch status data from concurrent API endpoint
        const response = await fetch('/api/statuses');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const statuses = await response.json();
        
        // Build the HTML for the table body
        let tableHTML = '';
        statuses.forEach(site => {
            const statusClass = site.status === 'Operational' ? 'status-operational' : 'status-offline';
            const latencyClass = getLatencyClass(site.response_time);
            const latencyText = `${site.response_time} ms`;
            const statusCodeText = getStatusCodeDisplay(site);
            
            tableHTML += `
                <tr>
                    <td class="website-name">${site.name}</td>
                    <td class="${statusClass}">${site.status}</td>
                    <td class="${latencyClass}">${latencyText}</td>
                    <td class="status-code">${statusCodeText}</td>
                </tr>
            `;
        });
        
        // Update the table with new data
        statusTableBody.innerHTML = tableHTML;
        
        // Update last updated timestamp
        updateLastRefreshTime();
        
        // Update page title with service status
        updatePageTitle(statuses);
        
    } catch (error) {
        console.error('Error fetching statuses:', error);
        // Show error state
        statusTableBody.innerHTML = '<tr><td colspan="4" class="error-state">Error loading status data. Retrying...</td></tr>';
    } finally {
        isLoading = false;
    }
}

/**
 * Gets the appropriate CSS class for latency color coding
 */
function getLatencyClass(responseTime) {
    if (responseTime < 500) {
        return 'latency-fast';
    } else if (responseTime <= 1500) {
        return 'latency-moderate';
    } else {
        return 'latency-slow';
    }
}

/**
 * Gets the display text for status code column
 */
function getStatusCodeDisplay(site) {
    if (site.status === 'Operational') {
        return site.status_code.toString();
    } else {
        // For offline services, show error reason instead of status code
        if (site.error) {
            return site.error;
        } else if (site.status_code === 0) {
            return 'Connection Failed';
        } else {
            return `HTTP ${site.status_code}`;
        }
    }
}

/**
 * Updates the page title with current system status
 */
function updatePageTitle(statuses) {
    const offlineCount = statuses.filter(site => site.status === 'Offline').length;
    
    if (offlineCount === 0) {
        document.title = 'SidelineSignal (All Systems Operational)';
    } else if (offlineCount === 1) {
        document.title = 'SidelineSignal (1 Service Offline)';
    } else {
        document.title = `SidelineSignal (${offlineCount} Services Offline)`;
    }
}

/**
 * Updates the last refresh timestamp display
 */
function updateLastRefreshTime() {
    const lastUpdateElement = document.getElementById('last-update');
    if (lastUpdateElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        lastUpdateElement.textContent = `Last updated: ${timeString}`;
    }
}

/**
 * Initialize the autonomous polling system
 */
function initializeRealTimePolling() {
    // Initial status fetch
    fetchStatuses();
    
    // Set up autonomous 15-second polling loop
    setInterval(fetchStatuses, 15000);
    
    console.log('SidelineSignal: Real-time autonomous monitoring initialized');
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', initializeRealTimePolling);
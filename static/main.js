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
        statusTableBody.innerHTML = '<tr><td colspan="2" class="loading-state">Loading status updates...</td></tr>';
        
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
            tableHTML += `
                <tr>
                    <td class="website-url">${site.url}</td>
                    <td class="${statusClass}">${site.status}</td>
                </tr>
            `;
        });
        
        // Update the table with new data
        statusTableBody.innerHTML = tableHTML;
        
        // Update last updated timestamp
        updateLastRefreshTime();
        
    } catch (error) {
        console.error('Error fetching statuses:', error);
        // Show error state
        statusTableBody.innerHTML = '<tr><td colspan="2" class="error-state">Error loading status data. Retrying...</td></tr>';
    } finally {
        isLoading = false;
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
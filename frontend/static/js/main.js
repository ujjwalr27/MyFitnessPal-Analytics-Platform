document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const statusMessage = document.getElementById('status-message');
    const grafanaLink = document.getElementById('grafana-link');
    const successSection = document.getElementById('success-section');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get the file
            const fileInput = document.getElementById('file');
            const file = fileInput.files[0];
            
            if (!file) {
                showMessage('error', 'Please select a file to upload.');
                return;
            }
            
            // Check file extension
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showMessage('error', 'Only CSV files are accepted.');
                return;
            }
            
            // Create FormData object
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading message
            showMessage('info', 'Uploading and processing your file... Please wait.');
            
            // Disable the submit button during upload
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            // Send AJAX request
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                // Check if the request was successful
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || `HTTP error! Status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showMessage('success', data.message);
                    
                    // Show success section if hidden
                    if (successSection) {
                        successSection.style.display = 'block';
                    }
                    
                    // Update Grafana link with user ID parameter if available
                    if (data.users_processed === 1 && grafanaLink) {
                        const userId = data.users_processed_details?.[0] || '';
                        const updatedHref = `http://localhost:3001/d/nutrition/nutrition-dashboard?var-userId=${userId}`;
                        grafanaLink.href = updatedHref;
                        
                        // Show a tooltip explaining the link has been updated
                        grafanaLink.setAttribute('data-bs-toggle', 'tooltip');
                        grafanaLink.setAttribute('data-bs-placement', 'top');
                        grafanaLink.setAttribute('title', `View dashboard for user ID: ${userId}`);
                        
                        // Initialize tooltip
                        const tooltip = new bootstrap.Tooltip(grafanaLink);
                    }
                    
                    // If multiple users were processed, show a selection dropdown
                    if (data.users_processed > 1 && data.users_processed_details) {
                        createUserSelection(data.users_processed_details);
                    }
                } else {
                    showMessage('error', data.error || 'An unknown error occurred.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('error', `Failed to upload file: ${error.message || 'Unknown error'}`);
            })
            .finally(() => {
                // Re-enable the submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Upload and Process';
            });
        });
    }
    
    // Function to create a user selection dropdown when multiple users are in the data
    function createUserSelection(userIds) {
        // Create a user selection element if it doesn't exist
        let userSelectionDiv = document.getElementById('user-selection');
        if (!userSelectionDiv) {
            userSelectionDiv = document.createElement('div');
            userSelectionDiv.id = 'user-selection';
            userSelectionDiv.className = 'mt-4 p-3 border rounded bg-light';
            statusMessage.after(userSelectionDiv);
        }
        
        // Clear any existing content
        userSelectionDiv.innerHTML = '';
        
        // Add heading
        const heading = document.createElement('h5');
        heading.textContent = 'Multiple users detected. Select a user to view:';
        userSelectionDiv.appendChild(heading);
        
        // Create dropdown
        const selectGroup = document.createElement('div');
        selectGroup.className = 'input-group mb-3 mt-3';
        
        const select = document.createElement('select');
        select.className = 'form-select';
        select.id = 'user-id-select';
        
        // Add options for each user
        userIds.forEach(userId => {
            const option = document.createElement('option');
            option.value = userId;
            option.textContent = `User ID: ${userId}`;
            select.appendChild(option);
        });
        
        // Add a button to view the selected user's dashboard
        const viewButton = document.createElement('button');
        viewButton.className = 'btn btn-success';
        viewButton.textContent = 'View Dashboard';
        viewButton.onclick = function() {
            const selectedUserId = document.getElementById('user-id-select').value;
            window.open(`http://localhost:3001/d/nutrition/nutrition-dashboard?var-userId=${selectedUserId}`, '_blank');
        };
        
        // Assemble the dropdown and button
        selectGroup.appendChild(select);
        selectGroup.appendChild(viewButton);
        userSelectionDiv.appendChild(selectGroup);
        
        // Make sure the user selection div is visible
        userSelectionDiv.style.display = 'block';
    }
    
    // Helper function to display status messages
    function showMessage(type, message) {
        // Define styles for different message types
        const styles = {
            'error': 'alert-danger',
            'success': 'alert-success',
            'info': 'alert-info',
            'warning': 'alert-warning'
        };
        
        // Clear existing messages
        statusMessage.innerHTML = '';
        
        // Set the message content
        statusMessage.innerHTML = `<div class="alert ${styles[type]} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
        
        // Show the message
        statusMessage.style.display = 'block';
        
        // Auto-hide success messages after 10 seconds (increased from 5)
        if (type === 'success') {
            setTimeout(() => {
                const alert = statusMessage.querySelector('.alert');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 10000);
        }
    }
}); 
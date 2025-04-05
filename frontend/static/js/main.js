document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const statusMessage = document.getElementById('status-message');
    const grafanaLink = document.getElementById('grafana-link');
    const successSection = document.getElementById('success-section');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('file');
            const file = fileInput.files[0];
            
            if (!file) {
                showMessage('error', 'Please select a file to upload.');
                return;
            }
            
         
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showMessage('error', 'Only CSV files are accepted.');
                return;
            }
            
            
            const formData = new FormData();
            formData.append('file', file);
            
            
            showMessage('info', 'Uploading and processing your file... Please wait.');
            
            
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                
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
                    
                    
                    if (successSection) {
                        successSection.style.display = 'block';
                    }
                    
                    
                    if (data.users_processed === 1 && grafanaLink) {
                        const userId = data.users_processed_details?.[0] || '';
                        const updatedHref = `http://localhost:3001/d/nutrition/nutrition-dashboard?var-userId=${userId}`;
                        grafanaLink.href = updatedHref;
                        
                       
                        grafanaLink.setAttribute('data-bs-toggle', 'tooltip');
                        grafanaLink.setAttribute('data-bs-placement', 'top');
                        grafanaLink.setAttribute('title', `View dashboard for user ID: ${userId}`);
                        
                       
                        const tooltip = new bootstrap.Tooltip(grafanaLink);
                    }
                    
                   
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
               
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Upload and Process';
            });
        });
    }
    
    
    function createUserSelection(userIds) {
        let userSelectionDiv = document.getElementById('user-selection');
        if (!userSelectionDiv) {
            userSelectionDiv = document.createElement('div');
            userSelectionDiv.id = 'user-selection';
            userSelectionDiv.className = 'mt-4 p-3 border rounded bg-light';
            statusMessage.after(userSelectionDiv);
        }
        
        userSelectionDiv.innerHTML = '';
        
        const heading = document.createElement('h5');
        heading.textContent = 'Multiple users detected. Select a user to view:';
        userSelectionDiv.appendChild(heading);
        
        const selectGroup = document.createElement('div');
        selectGroup.className = 'input-group mb-3 mt-3';
        
        const select = document.createElement('select');
        select.className = 'form-select';
        select.id = 'user-id-select';
        
        userIds.forEach(userId => {
            const option = document.createElement('option');
            option.value = userId;
            option.textContent = `User ID: ${userId}`;
            select.appendChild(option);
        });
        
        const viewButton = document.createElement('button');
        viewButton.className = 'btn btn-success';
        viewButton.textContent = 'View Dashboard';
        viewButton.onclick = function() {
            const selectedUserId = document.getElementById('user-id-select').value;
            window.open(`http://localhost:3001/d/nutrition/nutrition-dashboard?var-userId=${selectedUserId}`, '_blank');
        };
        
        selectGroup.appendChild(select);
        selectGroup.appendChild(viewButton);
        userSelectionDiv.appendChild(selectGroup);
        
        userSelectionDiv.style.display = 'block';
    }
    
    function showMessage(type, message) {
        const styles = {
            'error': 'alert-danger',
            'success': 'alert-success',
            'info': 'alert-info',
            'warning': 'alert-warning'
        };
        
        statusMessage.innerHTML = '';
        
        statusMessage.innerHTML = `<div class="alert ${styles[type]} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
        
        statusMessage.style.display = 'block';
        
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
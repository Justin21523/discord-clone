// frontend/assets/js/components/file_upload.js

// Function to show the file upload modal
export function showFileUploadModal(channelId, callback) {
    // Create the modal if it doesn't exist
    if (!document.getElementById('file-upload-modal')) {
        createFileUploadModal();
    }
    
    const modal = document.getElementById('file-upload-modal');
    modal.style.display = 'flex';
    
    // Store the channel ID and callback for when a file is uploaded
    window.currentFileUploadChannelId = channelId;
    window.fileUploadCallback = callback;
}

// Function to hide the file upload modal
export function hideFileUploadModal() {
    const modal = document.getElementById('file-upload-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Function to create the file upload modal
function createFileUploadModal() {
    const modalHTML = `
    <div id="file-upload-modal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="width: 500px; padding: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: white;">Upload File</h3>
                <button id="close-file-upload" class="btn-text" style="margin: 0; font-size: 20px;">&times;</button>
            </div>
            
            <div class="file-upload-container">
                <div id="file-drop-zone" class="file-drop-zone">
                    <div class="file-drop-content">
                        <i class="fas fa-cloud-upload-alt" style="font-size: 48px; color: var(--accent); margin-bottom: 16px;"></i>
                        <p>Drag and drop files here or click to browse</p>
                        <input type="file" id="file-input" style="display: none;" multiple>
                        <button id="browse-files-btn" class="btn-primary" style="margin-top: 16px;">Browse Files</button>
                    </div>
                </div>
                
                <div id="file-preview-container" class="file-preview-container" style="display: none; margin-top: 20px;">
                    <h4>Selected Files:</h4>
                    <div id="file-previews"></div>
                </div>
                
                <div class="file-upload-actions" style="display: flex; justify-content: flex-end; margin-top: 20px; gap: 10px;">
                    <button id="cancel-upload-btn" class="btn-text">Cancel</button>
                    <button id="upload-btn" class="btn-primary" disabled>Upload</button>
                </div>
            </div>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    addFileUploadEventListeners();
}

// Function to add event listeners to the file upload modal
function addFileUploadEventListeners() {
    // Close button
    document.getElementById('close-file-upload').addEventListener('click', hideFileUploadModal);
    
    // Cancel button
    document.getElementById('cancel-upload-btn').addEventListener('click', hideFileUploadModal);
    
    // Browse files button
    document.getElementById('browse-files-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });
    
    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileSelection);
    
    // Drag and drop events
    const dropZone = document.getElementById('file-drop-zone');
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent)';
        dropZone.style.backgroundColor = 'rgba(88, 101, 242, 0.1)';
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--bg-tertiary)';
        dropZone.style.backgroundColor = 'transparent';
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--bg-tertiary)';
        dropZone.style.backgroundColor = 'transparent';
        
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
    
    // Upload button
    document.getElementById('upload-btn').addEventListener('click', uploadFiles);
    
    // Close modal when clicking outside
    document.getElementById('file-upload-modal').addEventListener('click', (e) => {
        if (e.target.id === 'file-upload-modal') {
            hideFileUploadModal();
        }
    });
}

// Function to handle file selection
function handleFileSelection(e) {
    if (e.target.files.length) {
        handleFiles(e.target.files);
    }
}

// Function to handle selected files
function handleFiles(files) {
    const previewsContainer = document.getElementById('file-previews');
    const uploadBtn = document.getElementById('upload-btn');
    const previewContainer = document.getElementById('file-preview-container');
    
    // Clear previous previews
    previewsContainer.innerHTML = '';
    
    // Show preview container
    previewContainer.style.display = 'block';
    
    // Process each file
    Array.from(files).forEach(file => {
        const filePreview = createFilePreview(file);
        previewsContainer.appendChild(filePreview);
    });
    
    // Enable upload button if there are files
    uploadBtn.disabled = files.length === 0;
}

// Function to create a file preview element
function createFilePreview(file) {
    const preview = document.createElement('div');
    preview.className = 'file-preview';
    preview.style = `
        display: flex;
        align-items: center;
        padding: 12px;
        background-color: var(--bg-tertiary);
        border-radius: 6px;
        margin-bottom: 8px;
    `;
    
    // Determine file type icon
    let iconClass = 'fa-file';
    if (file.type.startsWith('image/')) {
        iconClass = 'fa-file-image';
    } else if (file.type.startsWith('video/')) {
        iconClass = 'fa-file-video';
    } else if (file.type.startsWith('audio/')) {
        iconClass = 'fa-file-audio';
    } else if (file.type.includes('pdf')) {
        iconClass = 'fa-file-pdf';
    } else if (file.type.includes('zip') || file.type.includes('compressed')) {
        iconClass = 'fa-file-archive';
    } else if (file.type.includes('text') || file.type.includes('javascript') || file.type.includes('json')) {
        iconClass = 'fa-file-alt';
    }
    
    // Format file size
    const fileSize = formatFileSize(file.size);
    
    preview.innerHTML = `
        <i class="fas ${iconClass}" style="font-size: 24px; color: var(--accent); margin-right: 12px;"></i>
        <div style="flex: 1;">
            <div style="font-weight: 500; color: var(--text-normal);">${file.name}</div>
            <div style="font-size: 12px; color: var(--text-muted);">${fileSize}</div>
        </div>
        <button class="remove-file-btn" data-file-name="${file.name}" style="background: none; border: none; color: var(--text-muted); cursor: pointer;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add event listener to remove button
    preview.querySelector('.remove-file-btn').addEventListener('click', function() {
        const fileName = this.getAttribute('data-file-name');
        removeFileByName(fileName);
    });
    
    return preview;
}

// Function to remove a file by name
function removeFileByName(fileName) {
    const fileInput = document.getElementById('file-input');
    const previewsContainer = document.getElementById('file-previews');
    
    // Remove the preview
    const previewToRemove = previewsContainer.querySelector(`[data-file-name="${fileName}"]`);
    if (previewToRemove) {
        previewToRemove.remove();
    }
    
    // Update the file input
    const dt = new DataTransfer();
    const files = Array.from(fileInput.files);
    const filteredFiles = files.filter(file => file.name !== fileName);
    
    filteredFiles.forEach(file => dt.items.add(file));
    fileInput.files = dt.files;
    
    // Disable upload button if no files remain
    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.disabled = dt.files.length === 0;
    
    // Hide preview container if no files remain
    if (dt.files.length === 0) {
        document.getElementById('file-preview-container').style.display = 'none';
    }
}

// Function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Function to upload files
async function uploadFiles() {
    const fileInput = document.getElementById('file-input');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select at least one file to upload');
        return;
    }
    
    if (!window.currentFileUploadChannelId) {
        alert('No channel selected for file upload');
        return;
    }
    
    // Show uploading status
    const uploadBtn = document.getElementById('upload-btn');
    const originalText = uploadBtn.textContent;
    uploadBtn.textContent = 'Uploading...';
    uploadBtn.disabled = true;
    
    try {
        const token = localStorage.getItem('token');
        
        // Upload each file individually
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Create FormData for the file
            const formData = new FormData();
            formData.append('file', file);
            formData.append('channel_id', window.currentFileUploadChannelId);
            
            // Add optional message if available
            // In a real implementation, you might want to add a caption field
            // formData.append('message', 'Uploaded file: ' + file.name);
            
            const response = await fetch('/api/files/', {
                method: 'POST',
                headers: {
                    // Don't set Content-Type header when using FormData - browser will set it with boundary
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Failed to upload ${file.name}`);
            }
            
            const result = await response.json();
            console.log(`File ${file.name} uploaded successfully:`, result);
        }
        
        // Call the callback if provided
        if (window.fileUploadCallback) {
            window.fileUploadCallback();
        }
        
        alert(`Successfully uploaded ${files.length} file(s)!`);
        
        // Reset the form
        fileInput.value = '';
        document.getElementById('file-previews').innerHTML = '';
        document.getElementById('file-preview-container').style.display = 'none';
        hideFileUploadModal();
    } catch (error) {
        console.error('Error uploading files:', error);
        alert(`Error uploading files: ${error.message}`);
    } finally {
        // Restore button state
        uploadBtn.textContent = originalText;
        uploadBtn.disabled = false;
    }
}

// Function to show a file preview in the chat
export function showFileInChat(fileInfo) {
    // Create a file attachment element
    const fileElement = document.createElement('div');
    fileElement.className = 'file-attachment';
    fileElement.style = `
        display: flex;
        align-items: center;
        padding: 8px 12px;
        background-color: var(--bg-tertiary);
        border-radius: 8px;
        margin-top: 8px;
        max-width: 400px;
    `;
    
    // Determine file type icon
    let iconClass = 'fa-file';
    let isImage = false;
    
    if (fileInfo.mime_type && fileInfo.mime_type.startsWith('image/')) {
        iconClass = 'fa-file-image';
        isImage = true;
    } else if (fileInfo.mime_type && fileInfo.mime_type.startsWith('video/')) {
        iconClass = 'fa-file-video';
    } else if (fileInfo.mime_type && fileInfo.mime_type.startsWith('audio/')) {
        iconClass = 'fa-file-audio';
    } else if (fileInfo.mime_type && fileInfo.mime_type.includes('pdf')) {
        iconClass = 'fa-file-pdf';
    } else if (fileInfo.mime_type && (fileInfo.mime_type.includes('zip') || fileInfo.mime_type.includes('compressed'))) {
        iconClass = 'fa-file-archive';
    } else if (fileInfo.mime_type && (fileInfo.mime_type.includes('text') || fileInfo.mime_type.includes('javascript') || fileInfo.mime_type.includes('json'))) {
        iconClass = 'fa-file-alt';
    }
    
    const fileSize = formatFileSize(fileInfo.file_size);
    
    if (isImage) {
        // For images, show a thumbnail
        fileElement.innerHTML = `
            <div style="flex: 1;">
                <a href="/api/files/download/${fileInfo.id}" target="_blank" style="text-decoration: none; color: inherit; display: block;">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <i class="fas ${iconClass}" style="font-size: 16px; color: var(--accent); margin-right: 8px;"></i>
                        <span style="font-weight: 500; color: var(--text-normal);">${fileInfo.original_filename}</span>
                    </div>
                    <div style="font-size: 12px; color: var(--text-muted);">${fileSize}</div>
                </a>
                <img src="/api/files/download/${fileInfo.id}" alt="${fileInfo.original_filename}" style="max-width: 100%; border-radius: 4px; margin-top: 8px;">
            </div>
        `;
    } else {
        // For other files, show an icon and details
        fileElement.innerHTML = `
            <i class="fas ${iconClass}" style="font-size: 24px; color: var(--accent); margin-right: 12px;"></i>
            <div style="flex: 1;">
                <a href="/api/files/download/${fileInfo.id}" target="_blank" style="text-decoration: none; color: inherit; display: block;">
                    <div style="font-weight: 500; color: var(--text-normal);">${fileInfo.original_filename}</div>
                    <div style="font-size: 12px; color: var(--text-muted);">${fileSize}</div>
                </a>
            </div>
        `;
    }
    
    return fileElement;
}
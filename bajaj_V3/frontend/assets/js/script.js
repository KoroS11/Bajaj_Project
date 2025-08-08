// Configuration
const API_URL = 'http://localhost:5000';

// Global variables
let uploadedFiles = [];
let currentQuery = '';
let isProcessing = false;

// DOM Elements - Main initialization
document.addEventListener('DOMContentLoaded', () => {
    initUploadArea();
    initQueryForm();
    addEventListeners();
    checkBackendConnection();
});

// Check if backend is running
function checkBackendConnection() {
    fetch(`${API_URL}/health`)
        .then(response => {
            if (response.ok) {
                showNotification('✅ Connected to backend server', 'success');
                return response.json();
            } else {
                throw new Error('Backend server not responding');
            }
        })
        .then(data => {
            console.log('Backend health status:', data);
        })
        .catch(error => {
            console.error('Backend connection error:', error);
            showNotification('⚠️ Backend server not responding. Please start the server.', 'warning');
        });
}
function initUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });

    // Click to select files
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

async function processQuery() {
    if (isProcessing) return;
    
    isProcessing = true;
    const processBtn = document.getElementById('submitQuery');
    const statusDiv = document.getElementById('enhancedStatusText');
    
    // Update UI
    processBtn.disabled = true;
    processBtn.innerHTML = '<div class="loading"></div> Processing with Intelligent System...';
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading and analyzing documents...';
    
    try {
        let fileId = null;
        
        // Step 1: Upload file if we have one
        if (uploadedFiles.length > 0) {
            const file = uploadedFiles[0].file;
            const formData = new FormData();
            formData.append('file', file);
            
            statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading document...';
            
            const uploadResponse = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                throw new Error(`Upload failed: ${uploadResponse.statusText}`);
            }
            
            const uploadResult = await uploadResponse.json();
            fileId = uploadResult.file_id;
            
            // Wait for processing to complete
            statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing document...';
            await waitForProcessing(fileId);
        }
        
        // Step 2: Send query to intelligent backend
        statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing query with intelligent system...';
        
        const queryData = {
            query: currentQuery,
            file_id: fileId || 'test_file_id'  // Use test file if no upload
        };
        
        const queryResponse = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(queryData)
        });
        
        if (!queryResponse.ok) {
            throw new Error(`Query failed: ${queryResponse.statusText}`);
        }
        
        const result = await queryResponse.json();
        
        // Display intelligent results
        displayIntelligentResults(result);
        
        // Update status
        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Intelligent analysis completed successfully!';
        
    } catch (error) {
        console.error('Processing error:', error);
        statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error: ' + error.message;
    } finally {
        isProcessing = false;
        processBtn.disabled = false;
        processBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Query';
        updateProcessButton();
    }
}

async function waitForProcessing(fileId) {
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        try {
            const response = await fetch(`${API_URL}/progress/${fileId}`);
            if (response.ok) {
                const status = await response.json();
                if (status.status === 'completed') {
                    return;
                } else if (status.status === 'error') {
                    throw new Error(status.error || 'Processing failed');
                }
            }
        } catch (error) {
            console.error('Progress check error:', error);
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
    }
    
    throw new Error('Processing timeout');
}

function displayIntelligentResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.querySelector('.results-content') || createResultsContainer();
    
    // Show the decision prominently
    const decision = result.decision;
    const decisionClass = decision === 'approved' ? 'approved' : decision === 'rejected' ? 'rejected' : 'pending';
    
    resultsContent.innerHTML = `
        <div class="result-card decision-card ${decisionClass}">
            <div class="decision-header">
                <i class="fas ${decision === 'approved' ? 'fa-check-circle' : decision === 'rejected' ? 'fa-times-circle' : 'fa-clock'}"></i>
                <h3>Decision: ${decision.toUpperCase()}</h3>
                <span class="confidence">Confidence: ${Math.round(result.confidence_score * 100)}%</span>
            </div>
            <div class="decision-content">
                <p class="natural-answer">${result.answer}</p>
                ${result.amount > 0 ? `<p class="amount">Coverage Amount: ₹${result.amount.toLocaleString()}</p>` : ''}
            </div>
        </div>
        
        <div class="result-card analysis-card">
            <h3><i class="fas fa-brain"></i> Intelligent Analysis</h3>
            <div class="analysis-content">
                <div class="entities">
                    <h4>Extracted Entities:</h4>
                    <ul>
                        ${Object.entries(result.parsed_entities).map(([key, value]) => 
                            `<li><strong>${key}:</strong> ${value}</li>`
                        ).join('')}
                    </ul>
                </div>
                <div class="reasoning">
                    <h4>Reasoning:</h4>
                    <ul>
                        ${result.justification.reasoning.map(reason => 
                            `<li>${reason}</li>`
                        ).join('')}
                    </ul>
                </div>
                <div class="clauses">
                    <h4>Document Clauses Used:</h4>
                    <ul>
                        ${result.justification.clauses_used.map(clause => 
                            `<li>${clause}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="result-card metadata-card">
            <h3><i class="fas fa-info-circle"></i> Query Analysis</h3>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="label">Query Type:</span>
                    <span class="value">${result.analysis.query_type}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Intent:</span>
                    <span class="value">${result.intent}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Entities Found:</span>
                    <span class="value">${result.analysis.entities_found}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Decision Factors:</span>
                    <span class="value">${result.analysis.decision_factors}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Source Pages:</span>
                    <span class="value">${result.source_pages.join(', ')}</span>
                </div>
                <div class="metadata-item">
                    <span class="label">Request ID:</span>
                    <span class="value">${result.request_id || 'N/A'}</span>
                </div>
            </div>
        </div>
    `;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createResultsContainer() {
    const resultsSection = document.getElementById('resultsSection');
    const container = document.createElement('div');
    container.className = 'results-content';
    resultsSection.appendChild(container);
    return container;
}
function initQueryForm() {
    const queryInput = document.getElementById('queryInput');
    const processBtn = document.getElementById('submitQuery');

    queryInput.addEventListener('input', (e) => {
        currentQuery = e.target.value;
        updateProcessButton();
    });

    processBtn.addEventListener('click', processQuery);
    
    // Enter key to process
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isProcessing && currentQuery.trim()) {
                processQuery();
            }
        }
    });
}

function addEventListeners() {
    // Clear files button
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-file')) {
            const index = parseInt(e.target.dataset.index);
            removeFile(index);
        }
    });
}

function handleFiles(files) {
    // Clear previous files
    uploadedFiles = [];
    
    files.forEach((file, index) => {
        if (file.type === 'application/pdf') {
            uploadedFiles.push({
                file: file,
                name: file.name,
                size: file.size,
                id: Date.now() + index
            });
        } else {
            showNotification(`${file.name} is not a PDF file`, 'error');
        }
    });

    updateFileDisplay();
    updateProcessButton();
}

function updateFileDisplay() {
    const fileList = document.getElementById('uploadedFiles');
    
    if (uploadedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <i class="fas fa-file-pdf"></i>
                <span class="file-name">${file.name}</span>
                <span class="file-size">${formatFileSize(file.size)}</span>
            </div>
            <button class="remove-file" data-index="${index}">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileDisplay();
    updateProcessButton();
}

function updateProcessButton() {
    const processBtn = document.getElementById('submitQuery');
    const hasQuery = currentQuery.trim().length > 0;
    
    processBtn.disabled = !hasQuery || isProcessing;
    
    if (uploadedFiles.length > 0) {
        processBtn.innerHTML = '<i class="fas fa-brain"></i> Process with Intelligent System';
    } else {
        processBtn.innerHTML = '<i class="fas fa-brain"></i> Process with Demo Policy';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="close-btn">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

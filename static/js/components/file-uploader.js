/**
 * SmartKeja - File Uploader Component
 * Handles image and video uploads with progress tracking
 */

export class FileUploader {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.uploadUrl = options.uploadUrl || '/api/upload/';
        this.maxFiles = options.maxFiles || 10;
        this.maxFileSize = options.maxFileSize || 20 * 1024 * 1024; // 20MB
        this.acceptedTypes = options.acceptedTypes || ['image/*', 'video/*'];
        this.files = [];
        this.onUploadComplete = options.onUploadComplete || null;
        this.onUploadProgress = options.onUploadProgress || null;
        this.init();
    }

    init() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`FileUploader container #${this.containerId} not found`);
            return;
        }

        container.innerHTML = `
            <div class="file-uploader">
                <div class="upload-area border border-2 border-dashed rounded p-4 text-center" 
                     id="${this.containerId}-dropzone">
                    <i class="bi bi-cloud-upload fs-1 text-primary mb-3 d-block"></i>
                    <p class="mb-2">Drag and drop files here or click to browse</p>
                    <small class="text-muted">Max ${this.maxFiles} files, ${this.formatFileSize(this.maxFileSize)} per file</small>
                    <input type="file" 
                           id="${this.containerId}-input" 
                           multiple 
                           accept="${this.acceptedTypes.join(',')}" 
                           style="display: none;">
                </div>
                <div class="file-list mt-3" id="${this.containerId}-list"></div>
                <div class="upload-progress mt-3" id="${this.containerId}-progress" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const dropzone = document.getElementById(`${this.containerId}-dropzone`);
        const fileInput = document.getElementById(`${this.containerId}-input`);

        // Click to browse
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(Array.from(e.target.files));
        });

        // Drag and drop
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('drag-over');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });
    }

    handleFiles(files) {
        const validFiles = files.filter(file => {
            // Check file size
            if (file.size > this.maxFileSize) {
                alert(`File ${file.name} is too large. Maximum size is ${this.formatFileSize(this.maxFileSize)}`);
                return false;
            }

            // Check file type
            const isValidType = this.acceptedTypes.some(type => {
                if (type.endsWith('/*')) {
                    return file.type.startsWith(type.slice(0, -1));
                }
                return file.type === type;
            });

            if (!isValidType) {
                alert(`File ${file.name} is not a supported type`);
                return false;
            }

            return true;
        });

        // Check max files limit
        if (this.files.length + validFiles.length > this.maxFiles) {
            alert(`Maximum ${this.maxFiles} files allowed`);
            return;
        }

        validFiles.forEach(file => {
            this.files.push({
                file: file,
                id: Date.now() + Math.random(),
                status: 'pending',
                progress: 0,
                url: null
            });
        });

        this.renderFileList();
        this.uploadFiles();
    }

    renderFileList() {
        const listContainer = document.getElementById(`${this.containerId}-list`);
        listContainer.innerHTML = '';

        this.files.forEach((fileItem, index) => {
            const fileCard = document.createElement('div');
            fileCard.className = `file-item card mb-2 ${fileItem.status}`;
            fileCard.innerHTML = `
                <div class="card-body p-2">
                    <div class="d-flex align-items-center">
                        <div class="file-preview me-3" style="width: 60px; height: 60px; overflow: hidden; border-radius: 4px;">
                            ${this.getFilePreview(fileItem.file)}
                        </div>
                        <div class="file-info flex-grow-1">
                            <div class="file-name fw-bold">${fileItem.file.name}</div>
                            <div class="file-size text-muted small">${this.formatFileSize(fileItem.file.size)}</div>
                            ${fileItem.status === 'uploading' ? `
                                <div class="progress mt-1" style="height: 4px;">
                                    <div class="progress-bar" style="width: ${fileItem.progress}%"></div>
                                </div>
                            ` : ''}
                            ${fileItem.status === 'completed' ? `
                                <span class="badge bg-success mt-1">
                                    <i class="bi bi-check-circle me-1"></i>Uploaded
                                </span>
                            ` : ''}
                            ${fileItem.status === 'error' ? `
                                <span class="badge bg-danger mt-1">
                                    <i class="bi bi-x-circle me-1"></i>Error
                                </span>
                            ` : ''}
                        </div>
                        <button class="btn btn-sm btn-outline-danger remove-file" data-index="${index}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;

            // Remove file button
            fileCard.querySelector('.remove-file').addEventListener('click', () => {
                this.removeFile(index);
            });

            listContainer.appendChild(fileCard);
        });
    }

    getFilePreview(file) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.querySelector(`[data-file-id="${file.name}"]`);
                if (preview) {
                    preview.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: cover;">`;
                }
            };
            reader.readAsDataURL(file);
            return `<div data-file-id="${file.name}" style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-image"></i>
            </div>`;
        } else if (file.type.startsWith('video/')) {
            return `<div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-camera-video"></i>
            </div>`;
        }
        return `<div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
            <i class="bi bi-file"></i>
        </div>`;
    }

    async uploadFiles() {
        const pendingFiles = this.files.filter(f => f.status === 'pending');
        
        for (const fileItem of pendingFiles) {
            await this.uploadFile(fileItem);
        }
    }

    async uploadFile(fileItem) {
        fileItem.status = 'uploading';
        this.renderFileList();

        const formData = new FormData();
        formData.append('file', fileItem.file);
        formData.append('csrfmiddlewaretoken', this.getCsrfToken());

        try {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    fileItem.progress = Math.round((e.loaded / e.total) * 100);
                    this.renderFileList();
                    
                    if (this.onUploadProgress) {
                        this.onUploadProgress(fileItem.id, fileItem.progress);
                    }
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    fileItem.status = 'completed';
                    fileItem.url = response.url || response.file_url;
                    
                    // Store GPS data if available
                    if (response.gps) {
                        fileItem.gps = response.gps;
                        console.log('GPS coordinates extracted from image:', response.gps);
                    }
                    
                    this.renderFileList();
                    
                    if (this.onUploadComplete) {
                        this.onUploadComplete(fileItem, response.gps);
                    }
                } else {
                    fileItem.status = 'error';
                    this.renderFileList();
                }
            });

            xhr.addEventListener('error', () => {
                fileItem.status = 'error';
                this.renderFileList();
            });

            xhr.open('POST', this.uploadUrl);
            xhr.send(formData);

        } catch (error) {
            console.error('Upload error:', error);
            fileItem.status = 'error';
            this.renderFileList();
        }
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.renderFileList();
    }

    getFiles() {
        return this.files.filter(f => f.status === 'completed').map(f => f.url);
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}



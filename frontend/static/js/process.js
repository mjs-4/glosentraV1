/**
 * Glosentra Image Processing JavaScript
 * Handles file uploads, API calls, and result visualization
 */

(function () {
    'use strict';

    // Configuration
    const CONFIG = {
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
        apiTimeout: 30000, // 30 seconds
        retryAttempts: 3,
        retryDelay: 1000
    };

    // State management
    let currentFile = null;
    let isProcessing = false;
    let retryCount = 0;

    /**
     * Initialize the processing system
     */
    function init() {
        setupFileHandlers();
        setupDropzone();
        setupFormHandlers();
        setupProgressTracking();

        console.log('🚀 Glosentra processing system initialized');
    }

    /**
     * Setup file input handlers
     */
    function setupFileHandlers() {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput) return;

        fileInput.addEventListener('change', handleFileSelect);
    }

    /**
     * Setup dropzone functionality
     */
    function setupDropzone() {
        const dropzone = document.getElementById('dropzone');
        if (!dropzone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight dropzone when dragging over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        dropzone.addEventListener('drop', handleDrop, false);
    }

    /**
     * Prevent default drag behaviors
     */
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Highlight dropzone
     */
    function highlight(e) {
        const dropzone = document.getElementById('dropzone');
        if (dropzone) {
            dropzone.classList.add('border-primary', 'bg-primary/5');
        }
    }

    /**
     * Remove highlight from dropzone
     */
    function unhighlight(e) {
        const dropzone = document.getElementById('dropzone');
        if (dropzone) {
            dropzone.classList.remove('border-primary', 'bg-primary/5');
        }
    }

    /**
     * Handle dropped files
     */
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFile(files[0]);
        }
    }

    /**
     * Handle file selection from input
     */
    function handleFileSelect(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    }

    /**
     * Handle file validation and preview
     */
    function handleFile(file) {
        // Validate file
        const validation = validateFile(file);
        if (!validation.valid) {
            showError(validation.message);
            return;
        }

        currentFile = file;

        // Show preview
        showFilePreview(file);

        // Update UI
        updateUIForFile(file);
    }

    /**
     * Validate uploaded file
     */
    function validateFile(file) {
        // Check file type
        if (!CONFIG.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: 'Please select a valid image file (JPG, PNG, or WebP)'
            };
        }

        // Check file size
        if (file.size > CONFIG.maxFileSize) {
            return {
                valid: false,
                message: `File size must be less than ${CONFIG.maxFileSize / (1024 * 1024)}MB`
            };
        }

        return { valid: true };
    }

    /**
     * Show file preview
     */
    function showFilePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const resultImage = document.getElementById('resultImage');
            const resultsDiv = document.getElementById('results');
            const noResultsDiv = document.getElementById('noResults');

            if (resultImage && resultsDiv && noResultsDiv) {
                resultImage.src = e.target.result;
                resultImage.alt = file.name;
                resultsDiv.classList.remove('hidden');
                noResultsDiv.classList.add('hidden');
            }
        };
        reader.readAsDataURL(file);
    }

    /**
     * Update UI for selected file
     */
    function updateUIForFile(file) {
        // Update dropzone text
        const dropzoneText = document.querySelector('#dropzone h3');
        if (dropzoneText) {
            dropzoneText.textContent = file.name;
        }

        // Show file info
        showFileInfo(file);
    }

    /**
     * Show file information
     */
    function showFileInfo(file) {
        const fileInfo = `
            <div class="mt-4 p-3 bg-glass border border-border rounded-lg">
                <div class="flex items-center justify-between text-sm">
                    <span class="text-text font-medium">${file.name}</span>
                    <span class="text-muted">${formatFileSize(file.size)}</span>
                </div>
                <div class="mt-1 text-xs text-muted">
                    Type: ${file.type} | Modified: ${new Date(file.lastModified).toLocaleDateString()}
                </div>
            </div>
        `;

        const dropzone = document.getElementById('dropzone');
        if (dropzone) {
            // Remove existing file info
            const existingInfo = dropzone.querySelector('.file-info');
            if (existingInfo) {
                existingInfo.remove();
            }

            // Add new file info
            const infoDiv = document.createElement('div');
            infoDiv.className = 'file-info';
            infoDiv.innerHTML = fileInfo;
            dropzone.appendChild(infoDiv);
        }
    }

    /**
     * Format file size
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Setup form handlers
     */
    function setupFormHandlers() {
        // Process button click
        const processBtn = document.querySelector('button[onclick="processImage()"]');
        if (processBtn) {
            processBtn.addEventListener('click', processImage);
        }

        // Model type change
        const modelSelect = document.getElementById('modelType');
        if (modelSelect) {
            modelSelect.addEventListener('change', updateModelType);
        }
    }

    /**
     * Process the uploaded image
     */
    async function processImage() {
        if (!currentFile) {
            showError('Please select an image file first');
            return;
        }

        if (isProcessing) {
            return;
        }

        isProcessing = true;
        retryCount = 0;

        // Show progress
        showProgress(true);

        // Get model type
        const modelType = getModelType();

        try {
            const result = await processImageWithRetry(currentFile, modelType);

            if (result.success) {
                displayResults(result);
                showSuccess('Image processed successfully!');
            } else {
                showError(result.error || 'Processing failed');
            }

        } catch (error) {
            console.error('Processing error:', error);
            showError('An error occurred while processing the image');
        } finally {
            isProcessing = false;
            showProgress(false);
        }
    }

    /**
     * Process image with retry logic
     */
    async function processImageWithRetry(file, modelType) {
        for (let attempt = 1; attempt <= CONFIG.retryAttempts; attempt++) {
            try {
                return await processImageAPI(file, modelType);
            } catch (error) {
                console.warn(`Attempt ${attempt} failed:`, error);

                if (attempt === CONFIG.retryAttempts) {
                    throw error;
                }

                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, CONFIG.retryDelay * attempt));
            }
        }
    }

    /**
     * Process image via API
     */
    async function processImageAPI(file, modelType) {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('model_type', modelType);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.apiTimeout);

        try {
            const apiBase = (window.GLOSENTRA_API_BASE || '').replace(/\/$/, '');
            const response = await fetch(`${apiBase}/api/process`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    /**
     * Display processing results
     */
    function displayResults(result) {
        // Update timing metrics
        updateTimingMetrics(result.timing);

        // Update detections
        updateDetections(result.predictions, result.task);

        // Draw visualizations
        drawVisualizations(result.predictions, result.task);

        // Log analytics
        logAnalytics(result);
    }

    /**
     * Update timing metrics display
     */
    function updateTimingMetrics(timing) {
        const inferenceTime = document.getElementById('inferenceTime');
        const fps = document.getElementById('fps');

        if (inferenceTime && timing.inference_ms) {
            inferenceTime.textContent = `${timing.inference_ms}ms`;
        }

        if (fps && timing.fps) {
            fps.textContent = timing.fps;
        }
    }

    /**
     * Update detections display
     */
    function updateDetections(predictions, task) {
        const detectionsDiv = document.getElementById('detections');
        if (!detectionsDiv) return;

        let detectionsHTML = '';

        if (task === 'classify' && predictions.predictions) {
            // Classification results
            detectionsHTML = predictions.predictions.map(pred => `
                <div class="detection-item">
                    <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 bg-primary rounded-full"></div>
                        <span class="text-sm text-text">${pred.class_name}</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="w-16 bg-glass rounded-full h-2">
                            <div class="bg-primary h-2 rounded-full" style="width: ${pred.confidence * 100}%"></div>
                        </div>
                        <span class="text-sm text-muted w-12 text-right">${(pred.confidence * 100).toFixed(1)}%</span>
                    </div>
                </div>
            `).join('');

        } else if (predictions.boxes && predictions.boxes.length > 0) {
            // Detection/segmentation results
            detectionsHTML = predictions.boxes.map((box, index) => {
                const confidence = predictions.confidences ? predictions.confidences[index] : 0;
                const className = predictions.class_names ? predictions.class_names[index] : `Class ${predictions.classes ? predictions.classes[index] : index}`;

                return `
                    <div class="detection-item">
                        <div class="flex items-center space-x-2">
                            <div class="w-2 h-2 bg-primary rounded-full"></div>
                            <span class="text-sm text-text">${className}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <div class="w-16 bg-glass rounded-full h-2">
                                <div class="bg-primary h-2 rounded-full" style="width: ${confidence * 100}%"></div>
                            </div>
                            <span class="text-sm text-muted w-12 text-right">${(confidence * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                `;
            }).join('');

        } else {
            detectionsHTML = '<div class="text-center py-8 text-muted text-sm">No objects detected</div>';
        }

        detectionsDiv.innerHTML = detectionsHTML;
    }

    /**
     * Draw visualizations on canvas
     */
    function drawVisualizations(predictions, task) {
        const canvas = document.getElementById('overlayCanvas');
        const resultImage = document.getElementById('resultImage');

        if (!canvas || !resultImage || !resultImage.complete) return;

        const ctx = canvas.getContext('2d');
        canvas.width = resultImage.naturalWidth;
        canvas.height = resultImage.naturalHeight;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (task === 'classify') {
            // Classification doesn't need visual overlay
            return;
        }

        if (predictions.boxes && predictions.boxes.length > 0) {
            // Draw bounding boxes
            predictions.boxes.forEach((box, index) => {
                const confidence = predictions.confidences ? predictions.confidences[index] : 0;
                const className = predictions.class_names ? predictions.class_names[index] : `Class ${predictions.classes ? predictions.classes[index] : index}`;

                if (confidence >= 0.25) { // Confidence threshold
                    drawBoundingBox(ctx, box, className, confidence);
                }
            });
        }

        if (task === 'segment' && predictions.masks) {
            // Draw segmentation masks
            predictions.masks.forEach((mask, index) => {
                const confidence = predictions.confidences ? predictions.confidences[index] : 0;
                if (confidence >= 0.25) {
                    drawMask(ctx, mask, index);
                }
            });
        }

        if (task === 'pose' && predictions.keypoints) {
            // Draw pose keypoints
            predictions.keypoints.forEach(keypoints => {
                drawPoseKeypoints(ctx, keypoints);
            });
        }
    }

    /**
     * Draw bounding box
     */
    function drawBoundingBox(ctx, box, className, confidence) {
        const [x1, y1, x2, y2] = box;

        // Draw box
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 2;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // Draw label
        const label = `${className} (${(confidence * 100).toFixed(1)}%)`;
        const textWidth = ctx.measureText(label).width;

        ctx.fillStyle = 'rgba(139, 92, 246, 0.8)';
        ctx.fillRect(x1, y1 - 20, textWidth + 8, 20);

        ctx.fillStyle = 'white';
        ctx.font = '12px system-ui';
        ctx.fillText(label, x1 + 4, y1 - 6);
    }

    /**
     * Draw segmentation mask
     */
    function drawMask(ctx, mask, index) {
        // This is a simplified mask drawing - in practice you'd need to handle the mask data properly
        const colors = ['#8b5cf6', '#f472b6', '#10b981', '#f59e0b', '#3b82f6'];
        const color = colors[index % colors.length];

        ctx.fillStyle = color + '40'; // 25% opacity
        // In a real implementation, you'd draw the actual mask data here
    }

    /**
     * Draw pose keypoints
     */
    function drawPoseKeypoints(ctx, keypoints) {
        const colors = ['#8b5cf6', '#f472b6', '#10b981', '#f59e0b'];

        keypoints.forEach((point, index) => {
            const [x, y] = point;
            const color = colors[index % colors.length];

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
    }

    /**
     * Update model type
     */
    function updateModelType() {
        const modelSelect = document.getElementById('modelType');
        if (modelSelect) {
            const modelType = modelSelect.value;
            updateUIForModelType(modelType);
        }
    }

    /**
     * Update UI for model type
     */
    function updateUIForModelType(modelType) {
        // Update button text
        const processBtn = document.querySelector('button[onclick="processImage()"]');
        if (processBtn) {
            const buttonTexts = {
                'detect': 'Run Detection',
                'segment': 'Run Segmentation',
                'classify': 'Run Classification',
                'pose': 'Run Pose Detection'
            };
            processBtn.textContent = buttonTexts[modelType] || 'Process Image';
        }
    }

    /**
     * Get current model type
     */
    function getModelType() {
        const modelSelect = document.getElementById('modelType');
        return modelSelect ? modelSelect.value : 'detect';
    }

    /**
     * Show progress indicator
     */
    function showProgress(show) {
        const progress = document.getElementById('progress');
        if (progress) {
            if (show) {
                progress.classList.remove('hidden');
            } else {
                progress.classList.add('hidden');
            }
        }
    }

    /**
     * Show error message
     */
    function showError(message) {
        console.error('Error:', message);
        // You could implement a toast notification system here
        alert(message);
    }

    /**
     * Show success message
     */
    function showSuccess(message) {
        console.log('Success:', message);
        // You could implement a toast notification system here
    }

    /**
     * Setup progress tracking
     */
    function setupProgressTracking() {
        // Track processing time
        window.addEventListener('beforeunload', () => {
            if (isProcessing) {
                return 'Image processing in progress. Are you sure you want to leave?';
            }
        });
    }

    /**
     * Log analytics data
     */
    function logAnalytics(result) {
        // Send analytics data to server
        if (result.timing) {
            const apiBase = (window.GLOSENTRA_API_BASE || '').replace(/\/$/, '');
            fetch(`${apiBase}/api/analytics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task: result.task,
                    timing: result.timing,
                    success: result.success
                })
            }).catch(error => {
                console.warn('Analytics logging failed:', error);
            });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose processImage function globally for onclick handlers
    window.processImage = processImage;

})();

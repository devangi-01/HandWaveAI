/**
 * Main JavaScript file for ASL Recognition application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add pulse animation when prediction changes
    const currentSign = document.getElementById('current-sign');
    if (currentSign) {
        // Store the initial value
        let lastSign = currentSign.textContent;
        
        // Create a MutationObserver to watch for changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    // If the sign has changed
                    if (currentSign.textContent !== lastSign && 
                        currentSign.textContent !== '--') {
                        // Add and then remove the pulse class
                        currentSign.classList.add('pulse');
                        setTimeout(() => {
                            currentSign.classList.remove('pulse');
                        }, 500);
                        
                        // Update the stored value
                        lastSign = currentSign.textContent;
                    }
                }
            });
        });
        
        // Start observing
        observer.observe(currentSign, { 
            characterData: true, 
            childList: true, 
            subtree: true 
        });
    }
    
    // Handle mobile navigation
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        const navMenu = document.querySelector('.nav-menu');
        
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('hidden');
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
        const videoFeed = document.getElementById('video-feed');
        const toggleCameraBtn = document.getElementById('toggle-camera');
        const currentSign = document.getElementById('current-sign');
        const confidence = document.getElementById('confidence');
        const historyContainer = document.getElementById('history-container');
        
        let cameraActive = false;
        let detectionInterval = null;
        let detectionHistory = [];
        
        // Initially hide the video feed
        videoFeed.style.display = 'none';
        
        // Toggle camera function
        toggleCameraBtn.addEventListener('click', function() {
            if (cameraActive) {
                // Stop the camera
                videoFeed.style.display = 'none';
                toggleCameraBtn.textContent = 'Start Camera';
                toggleCameraBtn.classList.add('btn-primary');
                toggleCameraBtn.classList.remove('btn-danger');
                cameraActive = false;
                
                // Clear detection interval
                if (detectionInterval) {
                    clearInterval(detectionInterval);
                    detectionInterval = null;
                }
            } else {
                // Start the camera
                videoFeed.style.display = 'block';
                videoFeed.src = "{% url 'video_feed' %}?" + new Date().getTime();
                toggleCameraBtn.textContent = 'Stop Camera';
                toggleCameraBtn.classList.remove('btn-primary');
                toggleCameraBtn.classList.add('btn-danger');
                cameraActive = true;
                
                // Start periodic detection
                startPeriodicDetection();
            }
        });
        
        // Start periodic detection of signs
        function startPeriodicDetection() {
            // Clear any existing interval
            if (detectionInterval) {
                clearInterval(detectionInterval);
            }
            
            // Detect signs every 2 seconds
            detectionInterval = setInterval(detectSign, 2000);
            
            // Detect immediately
            detectSign();
        }
        
        // Detect sign function
        async function detectSign() {
            if (!cameraActive) return;
            
            try {
                // Call the Django predict endpoint
                const response = await fetch("{% url 'sign_language:predict' %}");
                const data = await response.json();
                
                if (data.error) {
                    console.error("Error:", data.error);
                    return;
                }
                
                // Update the UI with the prediction
                currentSign.textContent = data.sign;
                confidence.textContent = `Confidence: ${data.confidence}%`;
                
                // Add to history if it's a new prediction
                if (detectionHistory.length === 0 || 
                    detectionHistory[0].sign !== data.sign || 
                    detectionHistory[0].confidence !== data.confidence) {
                    addToHistory(data.sign, data.confidence);
                }
                
            } catch (error) {
                console.error("Error detecting sign:", error);
            }
        }
        
        // Add detection to history
        function addToHistory(sign, confidence) {
            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            detectionHistory.unshift({
                sign: sign,
                confidence: confidence,
                time: timeString
            });
            
            // Keep only the last 5 detections
            if (detectionHistory.length > 5) {
                detectionHistory.pop();
            }
            
            // Update history display
            updateHistoryDisplay();
        }
        
        // Update history display
        function updateHistoryDisplay() {
            historyContainer.innerHTML = '';
            
            if (detectionHistory.length === 0) {
                historyContainer.innerHTML = '<div class="no-predictions">No predictions yet</div>';
                return;
            }
            
            detectionHistory.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.style.display = 'flex';
                historyItem.style.justifyContent = 'space-between';
                historyItem.style.padding = '0.5rem 0';
                historyItem.style.borderBottom = '1px solid #e5e7eb';
                
                historyItem.innerHTML = `
                    <div>
                        <span style="font-weight: 500;">${item.sign}</span>
                        <span style="color: #6b7280; font-size: 0.875rem; margin-left: 0.5rem;">(${item.confidence}%)</span>
                    </div>
                    <span style="color: #6b7280; font-size: 0.875rem;">${item.time}</span>
                `;
                
                historyContainer.appendChild(historyItem);
            });
        }
    });
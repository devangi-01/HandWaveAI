        // Toggle mobile menu
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');

        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
            });
        }

        // Toggle logout dropdown
        function toggleLogoutDropdown() {
            const dropdown = document.getElementById("logoutDropdown");
            dropdown.classList.toggle("show");
        }

        // Close dropdown when clicking outside
        window.addEventListener('click', function(event) {
            if (!event.target.matches('.username') && !event.target.closest('.logout-tab')) {
                const dropdown = document.getElementById("logoutDropdown");
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            }
        });

        // File upload name display
        const fileInput = document.getElementById('math-image');
        const fileName = document.getElementById('file-name');

        if (fileInput) {
            fileInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    fileName.textContent = this.files[0].name;
                } else {
                    fileName.textContent = 'No file chosen';
                }
            });
        }

        // Handle form submission
        const uploadForm = document.getElementById('upload-form');
        const aiOutput = document.getElementById('ai-output');
        const statusIndicator = document.getElementById('status-indicator');
        function getCSRFToken() {
            const cookieValue = document.cookie
                .split("; ")
                .find(row => row.startsWith("csrftoken="));
            return cookieValue ? cookieValue.split("=")[1] : "";
        }
        
        if (uploadForm) {
            uploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                
                // Update status
                statusIndicator.textContent = 'Processing...';
                statusIndicator.className = 'status-processing';
                
                // Clear previous results
                aiOutput.innerHTML = '<p class="loading-text"><i class="fas fa-spinner fa-spin"></i> Analyzing your math problem...</p>';
                
                fetch(uploadMathProblemURL, {
                    method: 'POST',
                    body: formData,
                    headers: {
                      'X-CSRFToken': getCSRFToken()
                    }
                  })
                  
                .then(response => response.json())
                .then(data => {
                    if (data.solution) {
                        statusIndicator.textContent = 'Solution found';
                        statusIndicator.className = 'status-success';
                        
                        // Format the solution with markdown-like syntax
                        const formattedSolution = formatSolution(data.solution);
                        aiOutput.innerHTML = formattedSolution;
                    } else if (data.error) {
                        statusIndicator.textContent = 'Error';
                        statusIndicator.className = 'status-error';
                        aiOutput.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
                    }
                })
                .catch(error => {
                    statusIndicator.textContent = 'Error';
                    statusIndicator.className = 'status-error';
                    aiOutput.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
                });
            });
        }

        // Poll for AI output from webcam gestures
        function pollAIOutput() {
            fetch(getAIOutputURL)
                .then(response => response.json())
                .then(data => {
                    if (data.output && data.output.trim() !== '') {
                        statusIndicator.textContent = 'Solution found';
                        statusIndicator.className = 'status-success';
                        
                        // Format the solution with markdown-like syntax
                        const formattedSolution = formatSolution(data.output);
                        aiOutput.innerHTML = formattedSolution;
                    }
                })
                .catch(error => console.error('Error polling AI output:', error));
        }

        // Format solution with basic markdown-like syntax
        function formatSolution(text) {
            // Replace markdown-style headers
            text = text.replace(/^# (.*$)/gm, '<h3>$1</h3>');
            text = text.replace(/^## (.*$)/gm, '<h4>$1</h4>');
            
            // Replace markdown-style bold
            text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            // Replace markdown-style italic
            text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            // Replace line breaks with <br>
            text = text.replace(/\n/g, '<br>');
            
            return text;
        }

        // Start polling for AI output
        setInterval(pollAIOutput, 10000);

        // Make header sticky on scroll
        window.addEventListener('scroll', function() {
            const header = document.querySelector('.header');
            if (window.scrollY > 10) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
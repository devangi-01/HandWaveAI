document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const video = document.getElementById("video")
  const videoOverlay = document.querySelector(".video-overlay")
  const detectedSignElement = document.getElementById("detected-sign")
  const confidenceScoreElement = document.getElementById("confidence-score")
  const confidenceFill = document.getElementById("confidence-fill")
  const detectBtn = document.getElementById("detect-btn")
  const deleteBtn = document.getElementById("delete-btn")
  const clearBtn = document.getElementById("clear-btn")
  const historyBody = document.getElementById("history-body")
  const emptyHistory = document.getElementById("empty-history")

  // State
  let detectionHistory = []
  const selectedRows = new Set()
  let isVideoPlaying = false
  const videoStream = null

  // Initialize
  initVideoFeed()
  updateHistoryUI()

  // Event Listeners
  detectBtn.addEventListener("click", detectSign)
  deleteBtn.addEventListener("click", deleteSelected)
  clearBtn.addEventListener("click", clearHistory)

  // Functions
  function initVideoFeed() {
    // Show loading state
    videoOverlay.style.display = "flex"
    videoOverlay.querySelector("p").textContent = "Starting camera..."

    // Create an image element to display the video feed from Django
    const videoFeed = document.createElement("img")
    videoFeed.style.width = "100%"
    videoFeed.style.height = "100%"
    videoFeed.style.objectFit = "cover"

    // Set the source to the Django video feed endpoint
    // videoFeed.src = "/sign_language/video_feed/"
    videoFeed.src = "{% url 'sign_language:video_feed' %}"
    videoFeed.alt = "Video Feed"

    // Replace the video element with the image
    video.parentNode.replaceChild(videoFeed, video)

    // Handle loading and errors
    videoFeed.onload = () => {
      isVideoPlaying = true
      videoOverlay.style.display = "none"
    }

    videoFeed.onerror = () => {
      console.error("Error loading video feed")
      videoOverlay.querySelector("p").textContent = "Error loading video feed"
      videoOverlay.querySelector(".spinner").style.display = "none"
    }
  }

  async function detectSign() {
    if (!isVideoPlaying) return

    // Show processing state
    detectBtn.disabled = true
    detectBtn.textContent = "Processing..."

    try {
      // Make request to the detect_sign endpoint (same as in the old template)
      const response = await fetch("{% url 'sign_language:detect_sign' %}")
      // const response = await fetch("/sign_language/detect_sign/")
      const data = await response.json()

      // Update UI with results
      if (data.result) {
        const sign = data.result.sign
        const confidence = data.result.confidence

        // Update detection result
        updateDetectionResult(sign, confidence)

        // Add to history
        addToHistory(sign, confidence)
      }
    } catch (error) {
      console.error("Error detecting sign:", error)
      detectedSignElement.textContent = "Error detecting sign"
    } finally {
      // Re-enable button
      detectBtn.disabled = false
      detectBtn.textContent = "Detect Sign"
    }
  }

  function updateDetectionResult(sign, confidence) {
    // Update the sign display
    detectedSignElement.textContent = sign

    // Update confidence display
    confidenceScoreElement.textContent = `${confidence}%`
    confidenceFill.style.width = `${confidence}%`

    // Change color based on confidence
    if (confidence >= 90) {
      confidenceFill.style.backgroundColor = "#10b981" // Green
    } else if (confidence >= 75) {
      confidenceFill.style.backgroundColor = "#4f46e5" // Primary color
    } else {
      confidenceFill.style.backgroundColor = "#f59e0b" // Orange
    }

    // Add highlight animation
    detectedSignElement.classList.add("highlight")
    setTimeout(() => {
      detectedSignElement.classList.remove("highlight")
    }, 300)
  }

  function addToHistory(sign, confidence) {
    const timestamp = new Date()
    const id = Date.now().toString()

    detectionHistory.unshift({
      id,
      sign,
      confidence,
      timestamp,
    })

    updateHistoryUI()
  }

  function updateHistoryUI() {
    if (detectionHistory.length === 0) {
      emptyHistory.style.display = "block"
      historyBody.innerHTML = ""
      deleteBtn.disabled = true
      return
    }

    emptyHistory.style.display = "none"
    historyBody.innerHTML = ""

    detectionHistory.forEach((item) => {
      const row = document.createElement("tr")
      row.dataset.id = item.id

      const timeFormatted = item.timestamp.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })

      row.innerHTML = `
        <td>
          <input type="checkbox" class="history-checkbox" data-id="${item.id}">
        </td>
        <td>${item.sign}</td>
        <td>
          <div class="confidence-bar" style="width: 100px; display: inline-block; margin-right: 10px;">
            <div class="confidence-fill" style="width: ${item.confidence}%; background-color: ${
              item.confidence >= 90 ? "#10b981" : item.confidence >= 75 ? "#4f46e5" : "#f59e0b"
            };"></div>
          </div>
          ${item.confidence}%
        </td>
        <td>${timeFormatted}</td>
      `

      historyBody.appendChild(row)
    })

    // Add event listeners to checkboxes
    document.querySelectorAll(".history-checkbox").forEach((checkbox) => {
      checkbox.addEventListener("change", handleCheckboxChange)
    })

    updateDeleteButtonState()
  }

  function handleCheckboxChange(e) {
    const id = e.target.dataset.id

    if (e.target.checked) {
      selectedRows.add(id)
    } else {
      selectedRows.delete(id)
    }

    updateDeleteButtonState()
  }

  function updateDeleteButtonState() {
    deleteBtn.disabled = selectedRows.size === 0
  }

  function deleteSelected() {
    if (selectedRows.size === 0) return

    detectionHistory = detectionHistory.filter((item) => !selectedRows.has(item.id))
    selectedRows.clear()

    updateHistoryUI()
  }

  function clearHistory() {
    if (detectionHistory.length === 0) return

    // Add confirmation for better UX
    if (confirm("Are you sure you want to clear all detection history?")) {
      detectionHistory = []
      selectedRows.clear()
      updateHistoryUI()
    }
  }

  // Add CSS for highlight animation
  const style = document.createElement("style")
  style.textContent = `
    @keyframes highlight {
      0% { transform: scale(1); }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); }
    }
    .highlight {
      animation: highlight 0.3s ease-in-out;
    }
  `
  document.head.appendChild(style)
})

  
const video = document.getElementById('videoElement');
const canvas = document.getElementById('canvasElement');
const context = canvas.getContext('2d');
const detectedSignElement = document.getElementById('detectedSign');
const quizQuestionElement = document.getElementById('quizQuestion');
const answerInput = document.getElementById('answerInput');
const submitButton = document.getElementById('submitAnswer');
const resultElement = document.getElementById('quizResult');

// Start video stream
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(error => {
    console.error('Error accessing webcam:', error);
  });

// Function to send frame to backend for sign detection
function detectSign() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(blob => {
    const formData = new FormData();
    formData.append('image', blob);

    fetch(detectSignUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken(),
      },
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      detectedSignElement.textContent = data.meaning || 'No sign detected';
    })
    .catch(error => {
      console.error('Error detecting sign:', error);
    });
  }, 'image/jpeg');
}

// Call detectSign every 2 seconds
setInterval(detectSign, 2000);

// CSRF token helper
function getCSRFToken() {
  let csrfToken = null;
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      csrfToken = value;
      break;
    }
  }
  return csrfToken;
}

// Quiz logic
submitButton.addEventListener('click', () => {
  const userAnswer = answerInput.value.trim().toLowerCase();
  const correctAnswer = detectedSignElement.textContent.trim().toLowerCase();

  if (userAnswer === correctAnswer) {
    resultElement.textContent = '✅ Correct!';
    resultElement.style.color = 'green';
  } else {
    resultElement.textContent = '❌ Incorrect. Try again!';
    resultElement.style.color = 'red';
  }
});

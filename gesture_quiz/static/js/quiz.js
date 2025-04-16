document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const landingPage = document.getElementById("landing-page")
  const quizSection = document.getElementById("quiz-section")
  const resultSection = document.getElementById("result-section")
  const startBtn = document.getElementById("start-btn")
  const restartBtn = document.getElementById("restart-btn")
  const questionText = document.getElementById("question-text")
  const currentQuestionEl = document.getElementById("current-question")
  const totalQuestionsEl = document.getElementById("total-questions")
  const progressBar = document.getElementById("progress")
  const finalScoreEl = document.getElementById("final-score")
  const totalScoreEl = document.getElementById("total-score")
  const scorePercentageEl = document.getElementById("score-percentage")
  const resultMessageEl = document.getElementById("result-message")
  const videoFeed = document.getElementById("video-feed")

  // Quiz State
  let quizState = {
      question_index: 0,
      correct_answers: 0,
      total_questions: 0,
  }

  // Poll for quiz state updates
  let pollInterval

  // Initialize Quiz
  function initQuiz() {
      // Show landing page
      showSection(landingPage)

      // Reset quiz state
      quizState = {
          question_index: 0,
          correct_answers: 0,
          total_questions: 0,
      }

      // Stop polling if it's running
      if (pollInterval) {
          clearInterval(pollInterval)
          pollInterval = null
      }
  }

  // Show a specific section
  function showSection(section) {
      // Hide all sections
      landingPage.classList.remove("active")
      quizSection.classList.remove("active")
      resultSection.classList.remove("active")

      // Show the specified section
      section.classList.add("active")

      // Add animation class
      section.classList.add("fade-in")

      // Remove animation class after animation completes
      setTimeout(() => {
          section.classList.remove("fade-in")
      }, 500)
  }

  // Start polling for quiz state
  function startPolling() {
      // Initial fetch
      fetchQuizState()

      // Set up polling interval (every 1 second)
      pollInterval = setInterval(fetchQuizState, 1000)
  }

  // Fetch quiz state from server
  function fetchQuizState() {
      fetch("/get_quiz_state/")
          .then((response) => response.json())
          .then((data) => {
              // Update quiz state
              quizState = data

              // Update UI
              updateQuizUI()

              // Check if quiz is over
              if (quizState.question_index >= quizState.total_questions && quizState.total_questions > 0) {
                  endQuiz()
              }
          })
          .catch((error) => {
              console.error("Error fetching quiz state:", error)
          })
  }

  // Update quiz UI based on current state
  function updateQuizUI() {
      // Update question number and total
      currentQuestionEl.textContent = quizState.question_index + 1
      totalQuestionsEl.textContent = quizState.total_questions

      // Update progress bar
      const progressPercentage = (quizState.question_index / quizState.total_questions) * 100
      progressBar.style.width = `${progressPercentage}%`
  }

  // End quiz and show results
  function endQuiz() {
      // Stop polling
      if (pollInterval) {
          clearInterval(pollInterval)
          pollInterval = null
      }

      // Fetch final score
      fetch("/get_final_score/")
          .then((response) => response.json())
          .then((data) => {
              const score = data.score

              // Update result elements
              finalScoreEl.textContent = quizState.correct_answers
              totalScoreEl.textContent = quizState.total_questions
              scorePercentageEl.textContent = `${Math.round(score)}%`

              // Set result message based on score
              let resultMessage = ""
              if (score >= 90) {
                  resultMessage = "Excellent! You have a deep understanding of the quiz topics."
              } else if (score >= 70) {
                  resultMessage = "Great job! You have a good grasp of the fundamentals."
              } else if (score >= 50) {
                  resultMessage = "Good effort! You have a basic understanding of the topics."
              } else {
                  resultMessage = "Keep learning! There's always room for improvement."
              }

              resultMessageEl.textContent = resultMessage

              // Show result section
              showSection(resultSection)
          })
          .catch((error) => {
              console.error("Error fetching final score:", error)
          })
  }

  // Event Listeners
  startBtn.addEventListener("click", () => {
      // Reset the Django session by making a request to reset endpoint
      fetch("/reset_quiz/", { method: "POST" })
          .then(() => {
              showSection(quizSection)
              startPolling()
          })
          .catch((error) => {
              console.error("Error resetting quiz:", error)
              // Continue anyway
              showSection(quizSection)
              startPolling()
          })
  })

  restartBtn.addEventListener("click", () => {
      initQuiz()
  })

  // Handle video feed errors
  videoFeed.addEventListener("error", () => {
      console.error("Video feed error")
      videoFeed.src = videoFeed.src // Try to reload
  })

  // Initialize quiz on page load
  initQuiz()
})

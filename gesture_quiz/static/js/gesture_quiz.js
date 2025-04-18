document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const currentQuestionEl = document.getElementById('current-question');
    const totalQuestionsEl = document.getElementById('total-questions');
    const progressFillEl = document.getElementById('progress-fill');
    const scoreValueEl = document.getElementById('score-value');
    const quizResultsEl = document.getElementById('quiz-results');
    const finalScoreValueEl = document.getElementById('final-score-value');
    const scoreMessageEl = document.getElementById('score-message');
    const restartQuizBtn = document.getElementById('restart-quiz');
    const quizOverlayEl = document.getElementById('quiz-overlay');
    const videoFeedEl = document.getElementById('video-feed');

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });
    }

    // Make header sticky on scroll
    window.addEventListener('scroll', function () {
        const header = document.querySelector('.header');
        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Quiz state variables
    let quizState = {
        questionIndex: 0,
        correctAnswers: 0,
        totalQuestions: 0
    };

    // Function to update quiz UI based on state
    function updateQuizUI() {
        // Update question counter
        currentQuestionEl.textContent = quizState.questionIndex + 1;
        totalQuestionsEl.textContent = quizState.totalQuestions;

        // Update progress bar
        let progressPercentage = 0;
        if (quizState.totalQuestions > 0) {
            progressPercentage = (quizState.questionIndex / quizState.totalQuestions) * 100;
        }
        progressFillEl.style.width = `${progressPercentage}%`;

        // Update score
        scoreValueEl.textContent = quizState.correctAnswers;

        // Check if quiz is complete
        if (quizState.questionIndex >= quizState.totalQuestions && quizState.totalQuestions !== 0) {
            showQuizResults();
        }
    }

    // Function to show quiz results
    function showQuizResults() {
        fetch('/gesture_quiz/get_final_score/')
            .then(response => response.json())
            .then(data => {
                const score = data.score;
                finalScoreValueEl.textContent = `${score.toFixed(1)}%`;

                if (score >= 90) {
                    scoreMessageEl.textContent = "Excellent! You're a gesture quiz master!";
                } else if (score >= 70) {
                    scoreMessageEl.textContent = "Great job! You've got good gesture skills!";
                } else if (score >= 50) {
                    scoreMessageEl.textContent = "Good effort! Keep practicing!";
                } else {
                    scoreMessageEl.textContent = "Nice try! Practice makes perfect!";
                }

                quizResultsEl.classList.add('active');
                quizOverlayEl.style.display = 'none';
                videoFeedEl.style.opacity = '0.5';
            })
            .catch(error => {
                console.error('Error getting final score:', error);
            });
    }

    // Function to restart quiz
    function restartQuiz() {
        fetch('/gesture_quiz/restart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error restarting quiz:', error);
            });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Poll for quiz state updates
    function pollQuizState() {
        fetch('/gesture-quiz/get_quiz_state/')
            .then(response => response.json())
            .then(data => {
                quizState.questionIndex = data.question_index;
                quizState.correctAnswers = data.correct_answers;
                quizState.totalQuestions = data.total_questions;
                updateQuizUI();
            })
            .catch(error => {
                console.error('Error polling quiz state:', error);
            });
    }

    // Start polling
    pollQuizState();
    const pollInterval = setInterval(pollQuizState, 1000);

    // Event listener for restart
    if (restartQuizBtn) {
        restartQuizBtn.addEventListener('click', restartQuiz);
    }

    // Stop polling on unload
    window.addEventListener('beforeunload', function () {
        clearInterval(pollInterval);
    });

    function reloadQuiz() {
        setTimeout(function() {
            location.reload();
        }, 100);
    }
});

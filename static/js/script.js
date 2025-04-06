import { Chart } from "@/components/ui/chart"

document.addEventListener("DOMContentLoaded", () => {
  // Set current year in footer
  const currentYearElement = document.getElementById("current-year")
  if (currentYearElement) {
    currentYearElement.textContent = new Date().getFullYear()
  }

  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector(".mobile-menu-toggle")
  const mobileMenu = document.querySelector(".mobile-menu")

  if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener("click", () => {
      mobileMenu.classList.toggle("active")
    })
  }

  // Theme toggle with localStorage
  const themeToggle = document.getElementById("theme-toggle")
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode")
      localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light")
    })
  }

  const savedTheme = localStorage.getItem("theme")
  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode")
  }

  // Header scroll effect
  const header = document.querySelector(".header")
  window.addEventListener("scroll", () => {
    if (window.scrollY > 10 && header) {
      header.classList.add("scrolled")
    } else if (header) {
      header.classList.remove("scrolled")
    }
  })

  // Smooth scrolling
  const navLinks = document.querySelectorAll(".nav-link, .mobile-nav-link")
  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault()

      if (mobileMenu) {
        mobileMenu.classList.remove("active")
      }

      const targetId = this.getAttribute("href")
      if (targetId === "#") {
        window.scrollTo({ top: 0, behavior: "smooth" })
        return
      }

      const targetElement = document.querySelector(targetId)
      if (targetElement && header) {
        const headerHeight = header.offsetHeight
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight
        window.scrollTo({ top: targetPosition, behavior: "smooth" })
      }
    })
  })

  // Highlight active nav link while scrolling
  const sections = document.querySelectorAll("section")

  function setActiveNavLink() {
    const scrollPosition = window.scrollY

    sections.forEach((section) => {
      const sectionTop = section.offsetTop - header.offsetHeight - 100
      const sectionBottom = sectionTop + section.offsetHeight
      const sectionId = section.getAttribute("id")

      if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
        navLinks.forEach((link) => link.classList.remove("active"))
        document.querySelectorAll(`a[href="#${sectionId}"]`).forEach((link) => link.classList.add("active"))
      }
    })

    if (scrollPosition < sections[0].offsetTop - header.offsetHeight - 100) {
      navLinks.forEach((link) => link.classList.remove("active"))
      document.querySelectorAll('a[href="#"]').forEach((link) => link.classList.add("active"))
    }
  }

  window.addEventListener("scroll", setActiveNavLink)

  // Contact form submission simulation
  const contactForm = document.getElementById("contactForm")
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const submitButton = this.querySelector('button[type="submit"]')
      const originalText = submitButton.innerHTML

      submitButton.disabled = true
      submitButton.innerHTML = "Sending..."

      setTimeout(() => {
        alert("Thank you for your message! We will get back to you soon.")
        contactForm.reset()
        submitButton.disabled = false
        submitButton.innerHTML = originalText
      }, 1500)
    })
  }

  // Accuracy Chart (Chart.js)
  const ctx = document.getElementById("accuracyChart")
  if (ctx) {
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Numbers", "Letters", "Math Symbols", "Sign Language", "Dynamic Gestures"],
        datasets: [
          {
            label: "Accuracy",
            data: [96.5, 92.3, 94.8, 91.2, 88.7],
            backgroundColor: "#4f46e5",
            borderRadius: 4,
          },
          {
            label: "Precision",
            data: [95.8, 91.7, 93.9, 90.4, 87.5],
            backgroundColor: "rgba(79, 70, 229, 0.7)",
            borderRadius: 4,
          },
          {
            label: "Recall",
            data: [94.2, 90.5, 92.7, 89.8, 86.9],
            backgroundColor: "rgba(79, 70, 229, 0.4)",
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 80,
            max: 100,
            ticks: {
              callback: (value) => value + "%",
            },
            grid: {
              drawBorder: false,
            },
          },
          x: {
            grid: {
              display: false,
              drawBorder: false,
            },
          },
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 20,
            },
          },
          tooltip: {
            callbacks: {
              label: (context) => `${context.dataset.label}: ${context.raw}%`,
            },
          },
        },
      },
    })
  }

  // Animation on scroll
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(".feature-card, .team-card, .step-card")
    elements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top
      const windowHeight = window.innerHeight
      if (elementPosition < windowHeight - 100) {
        element.style.opacity = "1"
        element.style.transform = "translateY(0)"
      }
    })
  }

  // Initial animation state
  const elementsToAnimate = document.querySelectorAll(".feature-card, .team-card, .step-card")
  elementsToAnimate.forEach((element) => {
    element.style.opacity = "0"
    element.style.transform = "translateY(20px)"
    element.style.transition = "opacity 0.5s ease, transform 0.5s ease"
  })

  window.addEventListener("scroll", animateOnScroll)
  window.addEventListener("load", animateOnScroll)
})

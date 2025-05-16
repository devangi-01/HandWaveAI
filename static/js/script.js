document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector(".mobile-menu-toggle");
  const mobileMenu = document.querySelector(".mobile-menu");

  if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener("click", () => {
      mobileMenu.classList.toggle("active");
    });
  }

  // Header scroll effect

  // Smooth scrolling for navigation links
  const navLinks = document.querySelectorAll(".nav-link, .mobile-nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      
      // Only apply smooth scroll to hash links
      if (href.startsWith("#")) {
        e.preventDefault();
        
        // Close mobile menu if open
        if (mobileMenu) {
          mobileMenu.classList.remove("active");
        }
        
        // Handle scroll to top
        if (href === "#") {
          window.scrollTo({ top: 0, behavior: "smooth" });
          return;
        }
        
        // Scroll to section
        const targetElement = document.querySelector(href);
        if (targetElement && header) {
          const headerHeight = header.offsetHeight;
          const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
          window.scrollTo({ top: targetPosition, behavior: "smooth" });
        }
      }
    });
  });

  // Highlight active nav link while scrolling
  const sections = document.querySelectorAll("section[id]");
  
  function setActiveNavLink() {
    if (!header || sections.length === 0) return;
    
    const scrollPosition = window.scrollY;
    const headerHeight = header.offsetHeight;

    sections.forEach((section) => {
      const sectionTop = section.offsetTop - headerHeight - 100;
      const sectionBottom = sectionTop + section.offsetHeight;
      const sectionId = section.getAttribute("id");

      if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
        navLinks.forEach((link) => link.classList.remove("active"));
        document.querySelectorAll(`a[href="#${sectionId}"]`).forEach((link) => link.classList.add("active"));
      }
    });

    // Handle case when at the top of the page
    if (scrollPosition < sections[0].offsetTop - headerHeight - 100) {
      navLinks.forEach((link) => link.classList.remove("active"));
      document.querySelectorAll('a[href="/"]').forEach((link) => link.classList.add("active"));
    }
  }

  window.addEventListener("scroll", setActiveNavLink);
  
  // Initialize active link on page load
  setActiveNavLink();

  // Animation on scroll for feature cards, steps, etc.
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(".feature-card, .step, .about-content");
    elements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top;
      const windowHeight = window.innerHeight;
      if (elementPosition < windowHeight - 100) {
        element.classList.add("animated");
      }
    });
  };

  // Set initial animation state
  const elementsToAnimate = document.querySelectorAll(".feature-card, .step, .about-content");
  elementsToAnimate.forEach((element) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";
    element.style.transition = "opacity 0.6s ease, transform 0.6s ease";
  });

  // Add animated class to show elements
  document.querySelectorAll(".animated").forEach(el => {
    el.style.opacity = "1";
    el.style.transform = "translateY(0)";
  });

  window.addEventListener("scroll", animateOnScroll);
  window.addEventListener("load", animateOnScroll);
  
  // Call once on initial load
  animateOnScroll();
});

// Logout dropdown functionality
function toggleLogoutDropdown() {
  const dropdown = document.getElementById("logoutDropdown");
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  }
}

// Close dropdown when clicking outside
document.addEventListener("click", function(event) {
  const userInfo = document.querySelector(".user-info");
  const dropdown = document.getElementById("logoutDropdown");
  
  if (userInfo && dropdown && !userInfo.contains(event.target)) {
    dropdown.style.display = "none";
  }
});

// Star Rating Functionality
document.addEventListener('DOMContentLoaded', function() {
  const stars = document.querySelectorAll('.star-rating i');
  let selectedRating = 0;
  
  stars.forEach(star => {
    // Hover effect
    star.addEventListener('mouseover', function() {
      const rating = this.getAttribute('data-rating');
      highlightStars(rating);
    });
    
    // Mouse leave - reset to selected rating
    star.addEventListener('mouseleave', function() {
      resetStars();
      if (selectedRating > 0) {
        highlightStars(selectedRating);
      }
    });
    
    // Click to set rating
    star.addEventListener('click', function() {
      selectedRating = this.getAttribute('data-rating');
      highlightStars(selectedRating);
    });
  });
  
  // Submit rating button
  const submitButton = document.querySelector('.rating-submit');
  if (submitButton) {
    submitButton.addEventListener('click', function() {
      const feedback = document.querySelector('.rating-feedback textarea').value;
      if (selectedRating > 0) {
        alert(`Thank you for your ${selectedRating}-star rating!`);
        // Here you would typically send this data to your server
        // Reset form after submission
        resetRatingForm();
      } else {
        alert('Please select a rating before submitting.');
      }
    });
  }
  
  // Helper functions
  function highlightStars(rating) {
    stars.forEach(star => {
      const starRating = star.getAttribute('data-rating');
      if (starRating <= rating) {
        star.classList.remove('far');
        star.classList.add('fas');
      } else {
        star.classList.remove('fas');
        star.classList.add('far');
      }
    });
  }
  
  function resetStars() {
    stars.forEach(star => {
      star.classList.remove('fas');
      star.classList.add('far');
    });
  }
  
  function resetRatingForm() {
    selectedRating = 0;
    resetStars();
    document.querySelector('.rating-feedback textarea').value = '';
  }
});

// Existing logout dropdown function
function toggleLogoutDropdown() {
  var dropdown = document.getElementById("logoutDropdown");
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

// Make toggleLogoutDropdown available globally
window.toggleLogoutDropdown = toggleLogoutDropdown;
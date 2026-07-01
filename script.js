/* ============================================
   SCRIPT.JS – DivorCEmate
   Handles: Navbar scroll, mobile menu,
            scroll animations, form validation
            & mailto submission
   ============================================ */

// ─── NAVBAR ─────────────────────────────────
const navbar = document.getElementById('navbar');
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');

window.addEventListener('scroll', () => {
  if (window.scrollY > 20) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
  updateActiveNav();
});

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  const isOpen = navLinks.classList.contains('open');
  spans[0].style.transform = isOpen ? 'translateY(7px) rotate(45deg)' : '';
  spans[1].style.opacity = isOpen ? '0' : '1';
  spans[2].style.transform = isOpen ? 'translateY(-7px) rotate(-45deg)' : '';
});

// Close mobile nav on link click
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    hamburger.querySelectorAll('span').forEach(s => {
      s.style.transform = '';
      s.style.opacity = '1';
    });
  });
});

// ─── ACTIVE NAV HIGHLIGHT ────────────────────
function updateActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const scrollY = window.scrollY + 100;
  sections.forEach(section => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.offsetHeight;
    const id = section.getAttribute('id');
    const navLink = document.querySelector(`.nav-link[href="#${id}"]`);
    if (navLink) {
      if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        navLink.classList.add('active');
      }
    }
  });
}

// ─── SCROLL ANIMATIONS ───────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right').forEach(el => {
  observer.observe(el);
});

// Add animation classes to elements after DOM is ready
function initAnimations() {
  const animateTargets = [
    { selector: '.about-text', cls: 'fade-in-left' },
    { selector: '.about-image', cls: 'fade-in-right' },
    { selector: '.dr-text', cls: 'fade-in-left' },
    { selector: '.dr-image', cls: 'fade-in-right' },
    { selector: '.service-card', cls: 'fade-in' },
    { selector: '.contact-info', cls: 'fade-in-left' },
    { selector: '.contact-form-wrapper', cls: 'fade-in-right' },
    { selector: '.consideration-item', cls: 'fade-in' },
    { selector: '.about-list li', cls: 'fade-in' },
  ];

  animateTargets.forEach(({ selector, cls }) => {
    document.querySelectorAll(selector).forEach((el, i) => {
      el.classList.add(cls);
      el.style.transitionDelay = `${i * 0.08}s`;
      observer.observe(el);
    });
  });
}

// ─── FORM VALIDATION & SUBMISSION ───────────
const contactForm = document.getElementById('contact-form');
const submitBtn = document.getElementById('submit-btn');
const formSuccess = document.getElementById('form-success');
const formErrorMsg = document.getElementById('form-error-msg');

// Flask backend URL
// Change to your production URL when deployed (e.g. 'https://yourdomain.com')
const BACKEND_URL = 'https://divorcemate.onrender.com';

function showError(fieldId, errorId, message) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  if (field) field.classList.add('error');
  if (error) error.textContent = message;
}

function clearError(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const error = document.getElementById(errorId);
  if (field) field.classList.remove('error');
  if (error) error.textContent = '';
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateForm() {
  let isValid = true;

  // First Name
  const firstName = document.getElementById('first-name').value.trim();
  if (!firstName) {
    showError('first-name', 'first-name-error', 'First name is required.');
    isValid = false;
  } else {
    clearError('first-name', 'first-name-error');
  }

  // Last Name
  const lastName = document.getElementById('last-name').value.trim();
  if (!lastName) {
    showError('last-name', 'last-name-error', 'Last name is required.');
    isValid = false;
  } else {
    clearError('last-name', 'last-name-error');
  }

  // Email
  const email = document.getElementById('email').value.trim();
  if (!email) {
    showError('email', 'email-error', 'Email address is required.');
    isValid = false;
  } else if (!validateEmail(email)) {
    showError('email', 'email-error', 'Please enter a valid email address.');
    isValid = false;
  } else {
    clearError('email', 'email-error');
  }

  // Subject
  const subject = document.getElementById('subject').value;
  if (!subject) {
    showError('subject', 'subject-error', 'Please select a topic.');
    isValid = false;
  } else {
    clearError('subject', 'subject-error');
  }

  // Message
  const message = document.getElementById('message').value.trim();
  if (!message) {
    showError('message', 'message-error', 'Please describe your situation.');
    isValid = false;
  } else if (message.length < 20) {
    showError('message', 'message-error', 'Message must be at least 20 characters.');
    isValid = false;
  } else {
    clearError('message', 'message-error');
  }

  // Consent
  const consent = document.getElementById('privacy-consent').checked;
  if (!consent) {
    document.getElementById('consent-error').textContent = 'You must agree to proceed.';
    isValid = false;
  } else {
    document.getElementById('consent-error').textContent = '';
  }

  return isValid;
}

// Real-time field validation
['first-name', 'last-name', 'email', 'subject', 'message'].forEach(id => {
  const field = document.getElementById(id);
  if (!field) return;
  field.addEventListener('input', () => {
    field.classList.remove('error');
    const errorEl = document.getElementById(`${id}-error`);
    if (errorEl) errorEl.textContent = '';
  });
});

contactForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  formSuccess.style.display = 'none';
  formErrorMsg.style.display = 'none';

  if (!validateForm()) return;

  // Gather form data
  const firstName = document.getElementById('first-name').value.trim();
  const lastName = document.getElementById('last-name').value.trim();
  const email = document.getElementById('email').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const subject = document.getElementById('subject').value;
  const message = document.getElementById('message').value.trim();

  // Show loading state
  const btnText = submitBtn.querySelector('.btn-text');
  const btnLoading = submitBtn.querySelector('.btn-loading');
  btnText.style.display = 'none';
  btnLoading.style.display = 'inline';
  submitBtn.disabled = true;

  try {
    const response = await fetch(`${BACKEND_URL}/send-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        name: `${firstName} ${lastName}`,
        email: email,
        phone: phone || 'Not provided',
        subject: subject,
        message: message
      })
    });

    if (response.ok) {
      // Success
      formSuccess.style.display = 'flex';
      contactForm.reset();
      document.querySelectorAll('.field-error').forEach(el => el.textContent = '');
      document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
      formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      // Formspree returned an error
      const data = await response.json();
      console.error('Formspree error:', data);
      formErrorMsg.style.display = 'flex';
    }
  } catch (err) {
    // Network or other error
    console.error('Submission error:', err);
    formErrorMsg.style.display = 'flex';
  } finally {
    btnText.style.display = 'inline';
    btnLoading.style.display = 'none';
    submitBtn.disabled = false;
  }
});

// ─── INIT ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initAnimations();

  // Trigger initial nav state check
  if (window.scrollY > 20) navbar.classList.add('scrolled');
  updateActiveNav();
});

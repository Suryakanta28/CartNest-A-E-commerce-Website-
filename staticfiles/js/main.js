/**
 * CartNest - Modern E-Commerce Store
 * Main Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const navActions = document.getElementById('nav-actions');

  if (menuToggle && navActions) {
    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      navActions.classList.toggle('open');
      const isExpanded = navActions.classList.contains('open');
      menuToggle.setAttribute('aria-expanded', isExpanded);
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!navActions.contains(e.target) && !menuToggle.contains(e.target) && navActions.classList.contains('open')) {
        navActions.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navActions.classList.contains('open')) {
        navActions.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 2. Dismissible Alerts with Auto-Fade
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        setTimeout(() => alert.remove(), 250);
      });
    }

    // Auto dismiss non-error alerts after 5 seconds
    if (!alert.classList.contains('alert-danger') && !alert.classList.contains('alert-error')) {
      setTimeout(() => {
        if (alert.parentNode) {
          alert.style.opacity = '0';
          alert.style.transform = 'translateY(-8px)';
          setTimeout(() => alert.remove(), 300);
        }
      }, 5000);
    }
  });

  // 3. Smooth scrolling for internal anchor links (#categories, #about, etc.)
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetElem = document.querySelector(targetId);
        if (targetElem) {
          e.preventDefault();
          targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
          // Close mobile menu if open
          if (navActions && navActions.classList.contains('open')) {
            navActions.classList.remove('open');
            if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
          }
        }
      }
    });
  });

  // 4. Form submission button loading state
  const submitForms = document.querySelectorAll('form[data-prevent-double-submit]');
  submitForms.forEach((form) => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span>Processing...</span>';
      }
    });
  });

  // 5. Sort select auto-submit
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('sort', sortSelect.value);
      currentUrl.searchParams.set('page', '1');
      window.location.href = currentUrl.toString();
    });
  }
});

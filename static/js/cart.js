/**
 * CartNest - Cart & Quantity Handler with Instant AJAX Add-To-Cart
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Instant AJAX Add to Cart for all quick-add forms on cards & catalog
  const addToCartForms = document.querySelectorAll('form.add-to-cart-form-ajax, form.quick-add-form');

  addToCartForms.forEach((form) => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalHtml = submitBtn ? submitBtn.innerHTML : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Adding...</span>';
      }

      const url = this.getAttribute('action');
      const formData = new FormData(this);

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      })
        .then((res) => {
          if (!res.ok) throw new Error('Network error');
          return res.json();
        })
        .then((data) => {
          if (data && data.success) {
            // Update cart counter in navigation
            const cartCountBadge = document.getElementById('nav-cart-count');
            if (cartCountBadge && data.cart_total_items !== undefined) {
              cartCountBadge.textContent = data.cart_total_items;
              cartCountBadge.style.transform = 'scale(1.35)';
              setTimeout(() => {
                cartCountBadge.style.transform = 'scale(1)';
              }, 250);
            }

            // Success feedback on button
            if (submitBtn) {
              submitBtn.classList.add('btn-success-state');
              submitBtn.innerHTML = `
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>Added!</span>
              `;
              setTimeout(() => {
                submitBtn.innerHTML = originalHtml;
                submitBtn.classList.remove('btn-success-state');
                submitBtn.disabled = false;
              }, 1800);
            }
          } else {
            // Fallback submit standard
            form.submit();
          }
        })
        .catch(() => {
          // Fallback to standard form submission if AJAX fails
          form.submit();
        });
    });
  });

  // 2. Quantity Stepper for Product Detail and Cart forms
  const quantityControls = document.querySelectorAll('.quantity-control');

  quantityControls.forEach((control) => {
    const input = control.querySelector('.quantity-input');
    const btnMinus = control.querySelector('.qty-minus');
    const btnPlus = control.querySelector('.qty-plus');
    const maxStock = parseInt(input.getAttribute('max') || '9999', 10);
    const minQty = parseInt(input.getAttribute('min') || '1', 10);

    if (btnMinus && input) {
      btnMinus.addEventListener('click', () => {
        let val = parseInt(input.value, 10) || 1;
        if (val > minQty) {
          input.value = val - 1;
          triggerChange(input);
        }
      });
    }

    if (btnPlus && input) {
      btnPlus.addEventListener('click', () => {
        let val = parseInt(input.value, 10) || 1;
        if (val < maxStock) {
          input.value = val + 1;
          triggerChange(input);
        }
      });
    }

    if (input) {
      input.addEventListener('change', () => {
        let val = parseInt(input.value, 10);
        if (isNaN(val) || val < minQty) {
          input.value = minQty;
        } else if (val > maxStock) {
          input.value = maxStock;
        }
        triggerChange(input);
      });
    }
  });

  function triggerChange(element) {
    const event = new Event('change', { bubbles: true });
    element.dispatchEvent(event);

    // If inside an auto-submit cart row form, submit the form
    const autoForm = element.closest('form.cart-update-form');
    if (autoForm) {
      autoForm.submit();
    }
  }

  // 3. Remove item confirm handler
  const removeButtons = document.querySelectorAll('.cart-remove-form');
  removeButtons.forEach((form) => {
    form.addEventListener('submit', (e) => {
      const confirmRemove = confirm('Are you sure you want to remove this item from your cart?');
      if (!confirmRemove) {
        e.preventDefault();
      }
    });
  });
});

// Register a user module
const REGISTER_USER = {

  init: function() {
    this.performRegistration();
    this.checkPasswordStrength();
  },

  /**
   * Handle registration form submission
   */
  performRegistration: function() {
    $('#registerForm').on('submit', function(e) {
      e.preventDefault();

      const email = $('#email').val();
      const username = $('#username').val();
      const password = $('#password').val();
      const confirmPassword = $('#confirmPassword').val();
      const $btn = $('#registerBtn');
      const $spinner = $('.loading-spinner');

      // Validation
      if (!email || !username || !password) {
        Swal.fire({
          icon: 'error',
          title: 'Validation Error',
          text: 'Please fill in all required fields'
        });
        return;
      }

      if (password !== confirmPassword) {
        Swal.fire({
          icon: 'error',
          title: 'Password Mismatch',
          text: 'Passwords do not match'
        });
        return;
      }

      if (password.length < 6) {
        Swal.fire({
          icon: 'error',
          title: 'Weak Password',
          text: 'Password must be at least 6 characters long'
        });
        return;
      }

      if (username.length < 3 || username.length > 20) {
        Swal.fire({
          icon: 'error',
          title: 'Invalid Username',
          text: 'Username must be 3-20 characters'
        });
        return;
      }

      // Show loading state
      $btn.prop('disabled', true);
      $spinner.show();

      AUTH.register(email, username, password)
        .done(function(response) {
          Swal.fire({
            icon: 'success',
            title: 'Account Created',
            text: 'Your account has been created successfully. Redirecting to login...',
            timer: 2000,
            didClose: function() {
              window.location.href = 'login';
            }
          });
        })
        .fail(function(error) {
          $btn.prop('disabled', false);
          $spinner.hide();

          let errorMessage = 'An error occurred during registration';
          if (error.responseJSON && error.responseJSON.detail) {
            errorMessage = error.responseJSON.detail;
          }

          Swal.fire({
            icon: 'error',
            title: 'Registration Failed',
            text: errorMessage
          });
        });
    });
  },

  /**
   * Monitor password strength
   */
  checkPasswordStrength: function() {
    /**
     * Password strength checker
     */
    function checkPasswordStrength(password) {
      let strength = 0;
      if (password.length >= 8) strength++;
      if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
      if (/[0-9]/.test(password)) strength++;
      if (/[^a-zA-Z0-9]/.test(password)) strength++;

      const $bar = $('#strengthBar');
      const $text = $('#strengthText');
      const widths = ['0%', '25%', '50%', '75%', '100%'];
      const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
      const classes = ['', 'strength-weak', 'strength-fair', 'strength-good', 'strength-strong'];

      $bar.css('width', widths[strength]).removeClass('strength-weak strength-fair strength-good strength-strong');
      if (strength > 0) {
        $bar.addClass(classes[strength]);
        $text.text(labels[strength]);
      } else {
        $text.text('');
      }
    }

    $('#password').on('input', function() {
      checkPasswordStrength($(this).val());
    });
  },

};

// Initialize the app when DOM is ready
$(document).ready(function() {
  // Initialize the app
  REGISTER_USER.init();
});
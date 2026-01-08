// Login module
const LOGIN = {

  init: function() {
    this.submitLogin();
  },

  /**
   * Perfrom login action
   */
  submitLogin: function() {
    $('#loginForm').on('submit', function(e) {
      e.preventDefault();

      const username = $('#username').val();
      const password = $('#password').val();
      const $btn = $('#loginBtn');
      const $spinner = $('.loading-spinner');

      if (!username || !password) {
        Swal.fire({
          icon: 'error',
          title: 'Validation Error',
          text: 'Please enter both username and password'
        });
        return;
      }

      // Show loading state
      $btn.prop('disabled', true);
      $spinner.show();

      AUTH.login(username, password)
        .done(function (response) {
          AUTH.storeToken(response.access_token);
          Swal.fire({
            icon: 'success',
            title: 'Login Successful',
            text: 'Redirecting to dashboard...',
            timer: 1500,
            didClose: function () {
              window.location.href = '/';
            }
          });
        })
        .fail(function (error) {
          $btn.prop('disabled', false);
          $spinner.hide();

          let errorMessage = 'An error occurred during login';
          if (error.responseJSON && error.responseJSON.detail) {
            errorMessage = error.responseJSON.detail;
          }

          Swal.fire({
            icon: 'error',
            title: 'Login Failed',
            text: errorMessage
          });

          // Clear password field
          $('#password').val('');
        });
    })
  },
};

// Initialize the app when DOM is ready
$(document).ready(function() {
  // Initialize the app
  LOGIN.init();
});
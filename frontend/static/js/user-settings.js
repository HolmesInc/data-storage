// User Settings module
const USER_SETTINGS = {
  telegramGatewayExists: false,

  init: function() {
    // Check authentication first
    if (!AUTH.isLoggedIn()) {
      window.location.href = 'login';
      return;
    }

    this.loadSettings();
    this.setupSectionNavigation();
    this.setupFormHandler();
  },

  /**
   * Load current settings from backend
   */
  loadSettings: function() {
    // Load telegram gateway if it exists
    this.loadTelegramGateway();
  },

  /**
   * Load telegram gateway settings
   */
  loadTelegramGateway: function() {
    API.userSettings.storageGateways.getTelegramGateways()
      .done(function(response) {
        console.log('Telegram gateway found:', data);
        this.telegramGatewayExists = true;

        // Populate the form with existing data
        if (data.chat_id) {
          $('#telegramChatId').val(data.chat_id);
        }
      })
      .fail(function(error) {
        if (error.status === 404) {
          console.log('Telegram gateway not found - will create new one on submit');
          this.telegramGatewayExists = false;
          $('#telegramChatId').val('');
        } else {
          console.error('Error loading telegram gateway:', error);
          Swal.fire({
            icon: 'error',
            title: 'Error Loading Settings',
            text: 'Failed to load telegram gateway settings',
            timer: 3000
          });
        }
      })
  },

  /**
   * Setup section navigation
   */
  setupSectionNavigation: function() {
    $('.settings-nav-link').click(function(e) {
      e.preventDefault();

      // Get the section to show
      const sectionId = $(this).data('section');

      // Remove active class from all links and sections
      $('.settings-nav-link').removeClass('active');
      $('.settings-section').removeClass('active');

      // Add active class to clicked link and corresponding section
      $(this).addClass('active');
      $('#' + sectionId).addClass('active');
    });
  },

  /**
   * Setup form submission handler
   */
  setupFormHandler: function() {
    $('#storageGatewaysForm').on('submit', (e) => {
      e.preventDefault();

      const telegramChatId = $('#telegramChatId').val();

      // Validate that chat ID is filled
      if (!telegramChatId) {
        Swal.fire({
          icon: 'warning',
          title: 'Validation Error',
          text: 'Please enter your Telegram chat ID'
        });
        return;
      }

      // Show loading state
      const $btn = $('[type="submit"]', '#storageGatewaysForm');
      const originalText = $btn.html();
      $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');

      const formData = {
        chat_id: telegramChatId
      };

      // Determine if we should POST (create) or PUT (update)
      const handler = this.telegramGatewayExists ? API.userSettings.storageGateways.updateTelegramGateways : API.userSettings.storageGateways.createTelegramGateways;

      handler(formData)
        .done(function(response) {
          this.telegramGatewayExists = true;

          Swal.fire({
            icon: 'success',
            title: 'Success',
            text: this.telegramGatewayExists && method === 'PUT' ?
              'Telegram gateway updated successfully' :
              'Telegram gateway created successfully',
            timer: 2000
          });
        })
        .fail(function(error) {
          let errorMessage = 'Failed to save settings';
          if (error.responseJSON && error.responseJSON.detail) {
            errorMessage = error.responseJSON.detail;
          }

          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: errorMessage
          });
        })
        .always(function() {
          $btn.prop('disabled', false).html(originalText);
        })
    });
  }
};

// Initialize the module when DOM is ready
$(document).ready(function() {
  // Initialize the module
  USER_SETTINGS.init();
});

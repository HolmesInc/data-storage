// Authentication module
const AUTH = {
  apiBaseUrl: BACKEND_URL + API_BASE_URL,

  init: function() {
    this.setupLogout();
  },

  login: function(username, password) {
    return $.ajax({
      url: this.apiBaseUrl + '/auth/login',
      type: 'POST',
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify({
        username: username,
        password: password
      })
    });
  },

  register: function(email, username, password) {
    return $.ajax({
      url: this.apiBaseUrl + '/auth/register',
      type: 'POST',
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify({
        email: email,
        username: username,
        password: password
      })
    });
  },

  setupLogout: function() {
    $('#logoutBtn').click(function(e) {
      e.preventDefault();
      Swal.fire({
        title: 'Logout?',
        text: 'Are you sure you want to logout?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, logout'
      }).then((result) => {
        if (result.isConfirmed) {
          AUTH.logout();
        }
      });
    });
  },

  storeToken: function(token) {
    localStorage.setItem('authToken', token);
  },

  getToken: function() {
    return localStorage.getItem('authToken');
  },

  logout: function() {
    localStorage.removeItem('authToken');
    window.location.href = 'login';
  },

  isLoggedIn: function() {
    return !!this.getToken();
  },

  getAuthHeader: function() {
    const token = this.getToken();
    if (token) {
      return 'Bearer ' + token;
    }
    return null;
  },

  // Check if 401 error means auth failed
  checkAuthError: function(jqXHR) {
    if (jqXHR.status === 401) {
      this.logout();
      return true;
    }
    return false;
  }
};
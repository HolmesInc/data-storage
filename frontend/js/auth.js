// Dynamic backend URL detection (same logic as api.js)
// TODO: use the common logic (with api.js) instead of duplicating it here
function getBackendUrl() {
  if (window.location.port === '5001') {
    return 'http://localhost:8000';
  }
  return window.location.protocol + '//' + window.location.host;
}

const BACKEND_URL = getBackendUrl();
console.log('Using backend URL for login/register:', BACKEND_URL);


// Authentication module
const AUTH = {
  apiBaseUrl: BACKEND_URL + '/api/v0',

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

  storeToken: function(token) {
    localStorage.setItem('authToken', token);
  },

  getToken: function() {
    return localStorage.getItem('authToken');
  },

  logout: function() {
    localStorage.removeItem('authToken');
    window.location.href = 'login.html';
  },

  isLoggedIn: function() {
    return !!this.getToken();
  }
};
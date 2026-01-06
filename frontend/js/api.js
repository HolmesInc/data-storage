/**
 * API Client Module
 *
 * This module handles all communication with the FastAPI backend.
 * It provides methods for CRUD operations on data rooms, folders, and files.
 * All authenticated requests automatically include the JWT token.
 *
 * When running locally with the proxy server (frontend/server.py),
 * API requests use relative paths and the proxy handles forwarding to the backend.
 */

// Detect backend URL dynamically
// If we're on the same origin as the backend (via proxy or direct),
// use relative paths. Otherwise, construct the full URL.
const API_BASE_URL = '/api/v0';

/**
 * Helper function to get the full backend URL
 * Used for public endpoints that bypass authentication
 */
function getBackendUrl() {
    // Check if we can detect the backend from window.location
    // In Docker: localhost:8000 (served by Nginx which includes both frontend and API)
    // Locally: localhost:5001 (served by proxy server which forwards to localhost:8000)

    // If the current origin is on port 5001, backend is on 8000
    if (window.location.port === '5001') {
        return 'http://localhost:8000';
    }

    // If on port 8000 or any other, use current origin (works for Docker and production)
    return window.location.protocol + '//' + window.location.host;
}

const BACKEND_URL = getBackendUrl();
console.log('Using backend URL for app operations:', BACKEND_URL);

/**
 * Authentication helper
 */
const AUTH_HELPER = {
    getToken: function() {
        return localStorage.getItem('authToken');
    },

    isLoggedIn: function() {
        return !!this.getToken();
    },

    logout: function() {
        localStorage.removeItem('authToken');
        window.location.href = 'login.html';
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

/**
 * API Client Object
 * Contains methods for all API endpoints
 */
const API = {
    /**
     * Make an authenticated AJAX request
     * Automatically adds Authorization header
     */
    request: function(options) {
        const authHeader = AUTH_HELPER.getAuthHeader();
        if (authHeader) {
            options.headers = options.headers || {};
            options.headers['Authorization'] = authHeader;
        }

        return $.ajax(options).fail(function(jqXHR) {
            AUTH_HELPER.checkAuthError(jqXHR);
        });
    },

    /**
     * Health check endpoint
     * Verifies the API server is running
     */
    healthCheck: function() {
        return $.ajax({
            url: '/health',
            type: 'GET',
            dataType: 'json'
        });
    },

    /**
     * Authentication Operations
     */
    auth: {
        /**
         * Login user
         * POST /api/v0/auth/login
         */
        login: function(username, password) {
            return API.request({
                url: API_BASE_URL + '/auth/login',
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({
                    username: username,
                    password: password
                })
            });
        },

        /**
         * Register new user
         * POST /api/v0/auth/register
         */
        register: function(email, username, password) {
            return API.request({
                url: API_BASE_URL + '/auth/register',
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({
                    email: email,
                    username: username,
                    password: password
                })
            });
        }
    },

    /**
     * Data Room Operations
     */
    dataroom: {
        /**
         * Get all data rooms
         * GET /api/v0/datarooms
         */
        list: function() {
            return API.request({
                url: API_BASE_URL + '/datarooms',
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Create a new data room
         * POST /api/v0/datarooms
         *
         * @param {Object} data - {name: string, description: string}
         */
        create: function(data) {
            return API.request({
                url: API_BASE_URL + '/datarooms',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Get a specific data room with all folders and files
         * GET /api/v0/datarooms/{id}
         *
         * @param {number} id - Data room ID
         */
        get: function(id) {
            return API.request({
                url: API_BASE_URL + '/datarooms/' + id,
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Update a data room
         * PUT /api/v0/datarooms/{id}
         *
         * @param {number} id - Data room ID
         * @param {Object} data - {name: string, description: string}
         */
        update: function(id, data) {
            return API.request({
                url: API_BASE_URL + '/datarooms/' + id,
                type: 'PUT',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Delete a data room and all its contents
         * DELETE /api/v0/datarooms/{id}
         *
         * @param {number} id - Data room ID
         */
        delete: function(id) {
            return API.request({
                url: API_BASE_URL + '/datarooms/' + id,
                type: 'DELETE',
                dataType: 'json'
            });
        }
    },

    /**
     * Folder Operations
     */
    folder: {
        /**
         * Get all folders, optionally filtered by data room
         * GET /api/v0/folders?dataroom_id={id}
         *
         * @param {number} dataroomId - Optional data room ID to filter
         */
        list: function(dataroomId) {
            const params = dataroomId ? '?dataroom_id=' + dataroomId : '';
            return API.request({
                url: API_BASE_URL + '/folders' + params,
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Create a new folder
         * POST /api/v0/folders
         *
         * @param {Object} data - {name: string, dataroom_id: number, parent_id: number|null}
         */
        create: function(data) {
            return API.request({
                url: API_BASE_URL + '/folders',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Get a specific folder with its contents
         * GET /api/v0/folders/{id}
         *
         * @param {number} id - Folder ID
         */
        get: function(id) {
            return API.request({
                url: API_BASE_URL + '/folders/' + id,
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Update a folder (rename)
         * PATCH /api/v0/folders/{id}
         *
         * @param {number} id - Folder ID
         * @param {Object} data - {name: string}
         */
        update: function(id, data) {
            return API.request({
                url: API_BASE_URL + '/folders/' + id,
                type: 'PATCH',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Delete a folder and all its contents
         * DELETE /api/v0/folders/{id}
         *
         * @param {number} id - Folder ID
         */
        delete: function(id) {
            return API.request({
                url: API_BASE_URL + '/folders/' + id,
                type: 'DELETE',
                dataType: 'json'
            });
        }
    },

    /**
     * File Operations
     */
    file: {
        /**
         * Get all files, optionally filtered by folder
         * GET /api/v0/files?folder_id={id}
         *
         * @param {number} folderId - Optional folder ID to filter
         */
        list: function(folderId) {
            const params = folderId ? '?folder_id=' + folderId : '';
            return API.request({
                url: API_BASE_URL + '/files' + params,
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Upload a file to a folder
         * POST /api/v0/files?folder_id={id}&name={name}
         *
         * @param {number} folderId - Folder ID
         * @param {string} fileName - Display name for the file
         * @param {File} fileObj - File object from input
         */
        upload: function(folderId, fileName, fileObj) {
            const formData = new FormData();
            formData.append('file', fileObj);
            const authHeader = AUTH_HELPER.getAuthHeader();

            return $.ajax({
                url: API_BASE_URL + '/files?folder_id=' + folderId + '&name=' + encodeURIComponent(fileName),
                type: 'POST',
                dataType: 'json',
                processData: false,
                contentType: false,
                data: formData,
                headers: authHeader ? { 'Authorization': authHeader } : {},
                error: function(jqXHR) {
                    AUTH_HELPER.checkAuthError(jqXHR);
                }
            });
        },

        /**
         * Get file details
         * GET /api/v0/files/{id}
         *
         * @param {number} id - File ID
         */
        get: function(id) {
            return API.request({
                url: API_BASE_URL + '/files/' + id,
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Update a file (rename)
         * PATCH /api/v0/files/{id}
         *
         * @param {number} id - File ID
         * @param {Object} data - {name: string}
         */
        update: function(id, data) {
            return API.request({
                url: API_BASE_URL + '/files/' + id,
                type: 'PATCH',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Delete a file
         * DELETE /api/v0/files/{id}
         *
         * @param {number} id - File ID
         */
        delete: function(id) {
            return API.request({
                url: API_BASE_URL + '/files/' + id,
                type: 'DELETE',
                dataType: 'json'
            });
        },

        /**
         * Download a file with authentication token
         * GET /api/v0/files/{id}/download
         *
         * @param {number} id - File ID
         */
        download: function(id) {
            const authHeader = AUTH_HELPER.getAuthHeader();
            const headers = authHeader ? { 'Authorization': authHeader } : {};
            window.location.href = API_BASE_URL + '/files/' + id + '/download?token=' + (authHeader ? authHeader.split(' ')[1] : '');
        },

        /**
         * Create a file share link
         * POST /api/v0/files/{id}/share
         *
         * @param {number} id - File ID
         * @param {Object} data - {expires_at: datetime}
         */
        createShare: function(id, data = {}) {
            return API.request({
                url: API_BASE_URL + '/files/' + id + '/share',
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data)
            });
        },

        /**
         * Get all shares for a file
         * GET /api/v0/files/{id}/shares
         *
         * @param {number} id - File ID
         */
        listShares: function(id) {
            return API.request({
                url: API_BASE_URL + '/files/' + id + '/shares',
                type: 'GET',
                dataType: 'json'
            });
        },

        /**
         * Delete a file share
         * DELETE /api/v0/files/share/{share_id}
         *
         * @param {number} shareId - Share ID
         */
        deleteShare: function(shareId) {
            return API.request({
                url: API_BASE_URL + '/files/share/' + shareId,
                type: 'DELETE',
                dataType: 'json'
            });
        },

        /**
         * Get the download URL for a shared file (PUBLIC - no auth)
         * This is a helper function that returns the FULL URL for downloading shared files
         * without authentication. Uses dynamically detected backend URL.
         *
         * @param {string} token - Share token
         */
        getShareDownloadUrl: function(token) {
            return BACKEND_URL + '/api/v0/files/share/' + token + '/download';
        }
    }
};

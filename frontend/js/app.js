/**
 * Data Room Application
 *
 * Main application logic for the jQuery-based Data Room frontend.
 * Handles user interactions, UI updates, and communication with the API.
 */

// Global application state
const APP = {
    currentDataRoom: null,
    currentFolder: null,
    dataroomList: [],
    folderBreadcrumb: [], // Track the path to current folder

    /**
     * Initialize the application
     * Runs when the page loads
     */
    init: function() {
        console.log('🚀 Initializing Data Room Application...');

        // Check authentication first
        if (!AUTH_HELPER.isLoggedIn()) {
            window.location.href = 'login.html';
            return;
        }

        // Load data rooms on startup
        this.loadDataRooms();

        // Attach event handlers
        this.attachEventHandlers();

        // Check API health
        this.checkHealth();

        // Setup logout
        this.setupLogout();

        console.log('✅ Application initialized!');
    },

    /**
     * Setup logout functionality
     */
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
                    AUTH_HELPER.logout();
                }
            });
        });
    },

    /**
     * Check API health status
     */
    checkHealth: function() {
        $('#healthCheck').click(function() {
            API.healthCheck()
                .done(function(data) {
                    Swal.fire({
                        icon: 'success',
                        title: 'API Healthy',
                        text: 'API is responding correctly!',
                        timer: 2000
                    });
                    console.log('Health check:', data);
                })
                .fail(function(error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'API Error',
                        text: 'API is not responding!'
                    });
                    console.error('Health check failed:', error);
                });
        });
    },

    /**
     * Show alert message using SweetAlert2
     *
     * @param {string} message - Message to display
     * @param {string} type - 'success', 'error', 'warning', 'info'
     */
    showAlert: function(message, type = 'info') {
        const iconMap = {
            'success': 'success',
            'danger': 'error',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };

        Swal.fire({
            icon: iconMap[type] || 'info',
            title: type === 'success' ? 'Success' : type === 'error' || type === 'danger' ? 'Error' : 'Info',
            text: message,
            timer: 3000
        });
    },

    /**
     * Attach all event handlers
     */
    attachEventHandlers: function() {
        // Create Data Room button
        $('#createDataRoomBtn').click(() => this.createDataRoom());

        // Create Folder button
        $('#createFolderBtn').click(() => this.createFolder());

        // Rename Folder button
        $('#renameFolderBtn').click(() => this.renameFolder());

        // Rename File button
        $('#renameFileBtn').click(() => this.renameFile());

        // // Handle form submissions
        // $('#createDataRoomForm').on('submit', function(e) {
        //     e.preventDefault();
        //     APP.createDataRoom();
        // });
        //
        // $('#createFolderForm').on('submit', function(e) {
        //     e.preventDefault();
        //     APP.createFolder();
        // });
    },

    /**
     * Load all data rooms and display them in the sidebar
     */
    loadDataRooms: function() {
        const $list = $('#dataroomList');
        $list.html('<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>');

        API.dataroom.list()
            .done(function(datarooms) {
                APP.dataroomList = datarooms;
                APP.renderDataRoomList(datarooms);
            })
            .fail(function(error) {
                console.error('Error loading datarooms:', error);
                if (error.status === 401) {
                    AUTH_HELPER.logout();
                } else {
                    APP.showAlert('Failed to load data rooms', 'error');
                    $list.html('<p class="text-danger">Failed to load data rooms</p>');
                }
            });
    },

    /**
     * Render data rooms in the sidebar list
     *
     * @param {Array} datarooms - List of dataroom objects
     */
    renderDataRoomList: function(datarooms) {
        const $list = $('#dataroomList');

        if (datarooms.length === 0) {
            $list.html('<p class="text-muted">No data rooms yet. Create one to get started!</p>');
            return;
        }

        let html = '';
        datarooms.forEach(room => {
            html += `
                <div class="dataroom-item ${APP.currentDataRoom && APP.currentDataRoom.id === room.id ? 'active' : ''}" data-id="${room.id}">
                    <i class="fas fa-folder-open"></i>
                    <span>${room.name}</span>
                </div>
            `;
        });

        $list.html(html);

        // Attach click handlers to data room items
        $('.dataroom-item').click(function() {
            const dataroomId = $(this).data('id');
            APP.selectDataRoom(dataroomId);
        });
    },

    /**
     * Select a data room and display its contents
     *
     * @param {number} dataroomId - ID of the data room to select
     */
    selectDataRoom: function(dataroomId) {
        const dataroom = APP.dataroomList.find(r => r.id === dataroomId);
        if (!dataroom) return;

        APP.currentDataRoom = dataroom;
        APP.currentFolder = null;
        APP.folderBreadcrumb = [];

        // Update UI
        $('.dataroom-item').removeClass('active');
        $(`.dataroom-item[data-id="${dataroomId}"]`).addClass('active');

        // Load and display dataroom contents
        API.dataroom.get(dataroomId)
            .done(function(dataroomData) {
                APP.renderDataRoomContent(dataroomData);
            })
            .fail(function(error) {
                console.error('Error loading dataroom:', error);
                APP.showAlert('Failed to load data room', 'error');
            });
    },

    /**
     * Navigate into a folder
     *
     * @param {Object} folder - Folder object
     */
    navigateToFolder: function(folder) {
        APP.currentFolder = folder;
        APP.folderBreadcrumb.push({ id: folder.id, name: folder.name });

        // Load and display folder contents
        API.folder.get(folder.id)
            .done(function(folderData) {
                APP.renderFolderContent(folderData);
            })
            .fail(function(error) {
                APP.showAlert('Failed to load folder', 'error');
                console.error('Error loading folder:', error);
            });
    },

    /**
     * Go back to parent folder or data room
     */
    navigateBack: function() {
        if (APP.folderBreadcrumb.length === 0) {
            // Go back to data room view
            APP.selectDataRoom(APP.currentDataRoom.id);
        } else {
            APP.folderBreadcrumb.pop();
            if (APP.folderBreadcrumb.length === 0) {
                // Back to data room root
                APP.currentFolder = null;
                APP.selectDataRoom(APP.currentDataRoom.id);
            } else {
                // Back to parent folder
                const parentFolder = APP.folderBreadcrumb[APP.folderBreadcrumb.length - 1];
                API.folder.get(parentFolder.id)
                    .done(function(folderData) {
                        APP.currentFolder = parentFolder;
                        APP.renderFolderContent(folderData);
                    })
                    .fail(function(error) {
                        APP.showAlert('Failed to load folder', 'error');
                        console.error('Error loading folder:', error);
                    });
            }
        }
    },

    /**
     * Render the content of a data room (folders and files at root level)
     *
     * @param {Object} dataroomData - Data room object with folders
     */
    renderDataRoomContent: function(dataroomData) {
        const uploadAreaId = 'uploadArea-' + dataroomData.id;
        const foldersListId = 'foldersList-' + dataroomData.id;

        let html = `
            <div class="breadcrumb-nav">
                <i class="fas fa-home"></i>
                <strong>${dataroomData.name}</strong>
                ${dataroomData.description ? `<br><small class="text-muted">${dataroomData.description}</small>` : ''}
            </div>
            
            <div class="row g-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <div class="d-flex justify-content-between align-items-center">
                                <h4 class="mb-0"><i class="fas fa-folder-open me-2"></i>${dataroomData.name}</h4>
                                <div>
                                    <button class="btn btn-sm btn-success me-2" data-bs-toggle="modal" data-bs-target="#createFolderModal">
                                        <i class="fas fa-folder-plus"></i> New Folder
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="APP.deleteDataRoom(${dataroomData.id})">
                                        <i class="fas fa-trash"></i> Delete
                                    </button>
                                </div>
                            </div>
                        </div>                      
                        <div class="card-body">
                            <div class="upload-area" id="${uploadAreaId}" data-folder-id="${dataroomData.id}">
                                <i class="fas fa-cloud-upload-alt"></i>
                                <p><strong>Drag & drop PDF files here</strong></p>
                                <p style="font-size: 12px; color: #999;">or click to browse</p>
                                <input type="file" class="fileInput" accept=".pdf" multiple>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Get root-level items (folders and files with no parent)
        const rootFolders = dataroomData.folders ? dataroomData.folders.filter(f => !f.parent_id) : [];
        const rootFiles = dataroomData.files ? dataroomData.files : [];
        const hasRootItems = rootFolders.length > 0 || rootFiles.length > 0;

        // Add folders and files section
        if (hasRootItems) {
            html += `
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0"><i class="fas fa-folder"></i> Folders & Files</h6>
                            </div>
                            <div class="card-body" id="${foldersListId}">
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>No folders created yet.</p>
                            <p style="font-size: 12px;">Click "New Folder" to create one.</p>
                        </div>
                    </div>
                </div>
            `;
        }

        $('#contentArea').html(html);

        // Render root-level folders and files only
        if (hasRootItems) {
            let itemsHtml = '';
            rootFolders.forEach(folder => {
                itemsHtml += APP.renderFolderItem(folder);
            });
            rootFiles.forEach(file => {
                itemsHtml += APP.renderFileItem(file);
            });
            $(`#${foldersListId}`).html(itemsHtml);
            APP.attachFolderFileHandlers();
        }

        // Setup upload area
        APP.setupUploadArea(uploadAreaId, null);
    },

    /**
     * Render the content of a folder
     *
     * @param {Object} folderData - Folder object with subfolders and files
     */
    renderFolderContent: function(folderData) {
        const uploadAreaId = 'uploadArea-' + folderData.id;
        const foldersListId = 'foldersList-' + folderData.id;

        // Build breadcrumb path
        let breadcrumbHtml = '<i class="fas fa-home"></i> <a href="#" onclick="APP.selectDataRoom(' + APP.currentDataRoom.id + '); return false;" style="text-decoration: none; color: #0c5dd6;">' + APP.currentDataRoom.name + '</a>';

        APP.folderBreadcrumb.forEach((crumb, index) => {
            breadcrumbHtml += ' <i class="fas fa-chevron-right"></i> ';
            if (index === APP.folderBreadcrumb.length - 1) {
                breadcrumbHtml += '<strong>' + crumb.name + '</strong>';
            } else {
                breadcrumbHtml += '<a href="#" onclick="APP.navigateToFolderByIndex(' + index + '); return false;" style="text-decoration: none; color: #0c5dd6;">' + crumb.name + '</a>';
            }
        });

        let html = `
            <div class="breadcrumb-nav">
                ${breadcrumbHtml}
            </div>
            
            <div class="row g-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-cloud-upload-alt"></i> Upload File</h6>
                            <button class="btn btn-sm btn-light" data-bs-toggle="modal" data-bs-target="#createFolderModal" onclick="APP.setFolderParentId(${folderData.id})">
                                <i class="fas fa-folder-plus"></i> New Subfolder
                            </button>
                        </div>
                        <div class="card-body">
                            <div class="upload-area" id="${uploadAreaId}" data-folder-id="${folderData.id}">
                                <i class="fas fa-cloud-upload-alt"></i>
                                <p><strong>Drag & drop PDF files here</strong></p>
                                <p style="font-size: 12px; color: #999;">or click to browse</p>
                                <input type="file" class="fileInput" accept=".pdf" multiple>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add subfolders and files section
        if ((folderData.subfolders && folderData.subfolders.length > 0) || (folderData.files && folderData.files.length > 0)) {
            html += `
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0"><i class="fas fa-folder"></i> Folders & Files</h6>
                            </div>
                            <div class="card-body" id="${foldersListId}">
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <div class="empty-state">
                            <i class="fas fa-inbox"></i>
                            <p>No folders or files yet.</p>
                            <p style="font-size: 12px;">Create a subfolder or upload a file.</p>
                        </div>
                    </div>
                </div>
            `;
        }

        $('#contentArea').html(html);

        // Render subfolders and files
        if ((folderData.subfolders && folderData.subfolders.length > 0) || (folderData.files && folderData.files.length > 0)) {
            let itemsHtml = '';

            if (folderData.subfolders && folderData.subfolders.length > 0) {
                folderData.subfolders.forEach(subfolder => {
                    itemsHtml += APP.renderFolderItem(subfolder);
                });
            }

            if (folderData.files && folderData.files.length > 0) {
                folderData.files.forEach(file => {
                    itemsHtml += APP.renderFileItem(file);
                });
            }

            $(`#${foldersListId}`).html(itemsHtml);
            APP.attachFolderFileHandlers();
        }

        // Setup upload area
        APP.setupUploadArea(uploadAreaId, folderData.id);
    },

    /**
     * Render a single folder item (not recursive)
     *
     * @param {Object} folder - Folder object
     */
    renderFolderItem: function(folder) {
        return `
            <div class="folder-item" data-folder-id="${folder.id}">
                <span class="folder-name" style="cursor: pointer; font-weight: 500; color: #0c5dd6; flex-grow: 1;">
                    <i class="fas fa-folder"></i> ${folder.name}
                </span>
                <div class="folder-actions">
                    <button class="btn btn-sm btn-warning rename-folder-btn" data-id="${folder.id}" data-name="${folder.name}" title="Rename">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-folder-btn" data-id="${folder.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render a single file item
     *
     * @param {Object} file - File object
     */
    renderFileItem: function(file) {
        return `
            <div class="file-item" data-file-id="${file.id}">
                <div class="file-info" style="flex-grow: 1;">
                    <div class="file-name">
                        <i class="fas fa-file-pdf"></i> ${file.name}
                    </div>
                    <div class="file-size">${APP.formatFileSize(file.file_size)}</div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-info download-file-btn" data-id="${file.id}" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-primary share-file-btn" data-id="${file.id}" title="Share">
                        <i class="fas fa-share-alt"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-file-btn" data-id="${file.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Attach event handlers to folder and file items
     */
    attachFolderFileHandlers: function() {
        // Folder click handler - navigate into folder
        $('.folder-item .folder-name').off('click').on('click', function() {
            const folderId = $(this).closest('.folder-item').data('folder-id');
            API.folder.get(folderId)
                .done(function(folder) {
                    APP.navigateToFolder(folder);
                })
                .fail(function() {
                    APP.showAlert('Failed to open folder', 'error');
                });
        });

        // Rename folder
        $('.rename-folder-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const folderId = $(this).data('id');
            const folderName = $(this).data('name');
            APP.showRenameFolderModal(folderId, folderName);
        });

        // Delete folder
        $('.delete-folder-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const folderId = $(this).data('id');
            APP.deleteFolder(folderId);
        });

        // Download file
        $('.download-file-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const fileId = $(this).data('id');
            API.file.createShare(fileId, {})
                .done(function(share) {
                    // Display the share link
                    const shareUrl = API.file.getShareDownloadUrl(share.token);
                    window.location.href = shareUrl;
                })
                .fail(function(error) {
                    APP.showAlert('Failed to create share', 'error');
                    console.error('Error creating share:', error);
                });
        });

        // Share file (newly added)
        $('.share-file-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const fileId = $(this).data('id');
            APP.showShareFileModal(fileId);
        });

        // Delete file
        $('.delete-file-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const fileId = $(this).data('id');
            if (confirm('Are you sure you want to delete this file?')) {
                APP.deleteFile(fileId);
            }
        });
    },

    /**
     * Navigate to folder by breadcrumb index
     */
    navigateToFolderByIndex: function(index) {
        const targetFolder = APP.folderBreadcrumb[index];
        APP.folderBreadcrumb = APP.folderBreadcrumb.slice(0, index + 1);

        API.folder.get(targetFolder.id)
            .done(function(folderData) {
                APP.currentFolder = targetFolder;
                APP.renderFolderContent(folderData);
            })
            .fail(function(error) {
                APP.showAlert('Failed to load folder', 'error');
                console.error('Error loading folder:', error);
            });
    },

    /**
     * Setup upload area with drag and drop support
     *
     * @param {string} uploadAreaId - Upload area element ID
     * @param {number} folderId - Folder ID to upload to (null for dataroom root)
     */
    setupUploadArea: function(uploadAreaId, folderId) {
        const $uploadArea = $(`#${uploadAreaId}`);
        const $fileInput = $uploadArea.find('.fileInput');

        // Click to select files
        $uploadArea.off('click').on('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                $fileInput.click();
            }
        });

        // File input change
        $fileInput.off('change').on('change', function() {
            if (this.files.length > 0) {
                APP.handleFileSelect(this.files, folderId);
            }
        });

        // Drag and drop
        $uploadArea.off('dragover').on('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $uploadArea.addClass('dragover');
        });

        $uploadArea.off('dragleave').on('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $uploadArea.removeClass('dragover');
        });

        $uploadArea.off('drop').on('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $uploadArea.removeClass('dragover');

            if (e.originalEvent.dataTransfer.files.length > 0) {
                APP.handleFileSelect(e.originalEvent.dataTransfer.files, folderId);
            }
        });
    },

    /**
     * Handle file selection and upload
     *
     * @param {FileList} files - Selected files
     * @param {number} folderId - Folder ID to upload to
     */
    handleFileSelect: function(files, folderId) {
        if (!folderId) {
            APP.showAlert('Please select a folder to upload to', 'warning');
            return;
        }

        Array.from(files).forEach(file => {
            // Validate PDF
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                APP.showAlert(`${file.name} is not a PDF file`, 'warning');
                return;
            }

            // Upload file
            const fileName = file.name.replace('.pdf', '');
            API.file.upload(folderId, fileName, file)
                .done(function(fileData) {
                    APP.showAlert(`File "${fileData.name}" uploaded successfully!`, 'success');

                    // Refresh current view
                    if (APP.currentFolder) {
                        API.folder.get(APP.currentFolder.id)
                            .done(function(folderData) {
                                APP.renderFolderContent(folderData);
                            });
                    } else {
                        APP.selectDataRoom(APP.currentDataRoom.id);
                    }
                })
                .fail(function(error) {
                    APP.showAlert(`Failed to upload "${file.name}"`, 'danger');
                    console.error('Upload error:', error);
                });
        });
    },

    /**
     * Set folder parent ID for modal
     */
    setFolderParentId: function(parentId) {
        $('#parentFolderId').val(parentId === null ? 'null' : parentId);
    },

    /**
     * Create a new data room
     */
    createDataRoom: function() {
        const name = $('#dataroomName').val().trim();
        const description = $('#dataroomDesc').val().trim();

        if (!name) {
            APP.showAlert('Please enter a data room name', 'warning');
            return;
        }

        API.dataroom.create({ name, description })
            .done(function(dataroom) {
                APP.showAlert('Data room created successfully!', 'success');
                $('#createDataRoomForm')[0].reset();

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createDataRoomModal'));
                modal.hide();

                // Reload list
                APP.loadDataRooms();
            })
            .fail(function(error) {
                APP.showAlert('Failed to create data room', 'danger');
                console.error('Error:', error);
            });
    },

    /**
     * Create a new folder
     */
    createFolder: function() {
        console.log('Creating folder...');
        const name = $('#folderName').val().trim();
        const parentFolderId = $('#parentFolderId').val() === 'null' ? null : parseInt($('#parentFolderId').val());

        if (!name) {
            APP.showAlert('Please enter a folder name', 'warning');
            return;
        }

        if (!APP.currentDataRoom) {
            APP.showAlert('Please select a data room first', 'warning');
            return;
        }

        API.folder.create({
            name,
            dataroom_id: APP.currentDataRoom.id,
            parent_id: parentFolderId
        })
            .done(function(folder) {
                APP.showAlert('Folder created successfully!', 'success');
                $('#createFolderForm')[0].reset();

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createFolderModal'));
                modal.hide();

                // Reload current view
                if (parentFolderId === null) {
                    // Created in dataroom root
                    APP.selectDataRoom(APP.currentDataRoom.id);
                } else {
                    // Created in a subfolder
                    API.folder.get(parentFolderId)
                        .done(function(folderData) {
                            APP.renderFolderContent(folderData);
                        });
                }
            })
            .fail(function(error) {
                console.error('Error creating folder:', error);
                APP.showAlert('Failed to create folder', 'error');
            })
            // .always(function() {
            //     $btn.prop('disabled', false);
            // });
    },

    /**
     * Show rename folder modal
     *
     * @param {number} folderId - Folder ID
     * @param {string} folderName - Current folder name
     */
    showRenameFolderModal: function(folderId, folderName) {
        $('#renameFolderId').val(folderId);
        $('#renameFolderInput').val(folderName);

        const modal = new bootstrap.Modal(document.getElementById('renameFolderModal'));
        modal.show();
    },

    /**
     * Rename a folder
     */
    renameFolder: function() {
        const folderId = $('#renameFolderId').val();
        const newName = $('#renameFolderInput').val().trim();

        if (!newName) {
            APP.showAlert('Please enter a new name', 'warning');
            return;
        }

        API.folder.update(folderId, { name: newName })
            .done(function(folder) {
                APP.showAlert('Folder renamed successfully!', 'success');

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('renameFolderModal'));
                modal.hide();

                // Reload current view
                if (APP.currentFolder) {
                    API.folder.get(APP.currentFolder.id)
                        .done(function(folderData) {
                            APP.renderFolderContent(folderData);
                        });
                } else {
                    APP.selectDataRoom(APP.currentDataRoom.id);
                }
            })
            .fail(function(error) {
                console.error('Error loading folder:', error);
                APP.showAlert('Failed to load folder', 'error');
            });
    },

    /**
     * Delete a folder
     *
     * @param {number} folderId - Folder ID
     */
    deleteFolder: function(folderId) {
        Swal.fire({
            title: 'Delete Folder?',
            text: 'All files in this folder will be deleted. This action cannot be undone.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Yes, delete'
        }).then((result) => {
            if (result.isConfirmed) {
                API.folder.delete(folderId)
                    .done(function() {
                        APP.showAlert('Folder deleted successfully!', 'success');
                        // Reload current view
                        if (APP.currentFolder) {
                            API.folder.get(APP.currentFolder.id)
                                .done(function(folderData) {
                                    APP.renderFolderContent(folderData);
                                });
                        } else {
                            APP.selectDataRoom(APP.currentDataRoom.id);
                        }
                    })
                    .fail(function(error) {
                        console.error('Error deleting folder:', error);
                        APP.showAlert('Failed to delete folder', 'error');
                    });
            }
        });
    },

    /**
     * Delete a file
     *
     * @param {number} fileId - File ID
     */
    deleteFile: function(fileId) {
        API.file.delete(fileId)
            .done(function() {
                APP.showAlert('File deleted successfully!', 'success');

                // Reload current view
                if (APP.currentFolder) {
                    API.folder.get(APP.currentFolder.id)
                        .done(function(folderData) {
                            APP.renderFolderContent(folderData);
                        });
                } else {
                    APP.selectDataRoom(APP.currentDataRoom.id);
                }
            })
            .fail(function(error) {
                APP.showAlert('Failed to delete file', 'danger');
                console.error('Error:', error);
            });
    },

    /**
     * Format file size in human-readable format
     *
     * @param {number} bytes - File size in bytes
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    },

    /**
     * Show share file modal
     *
     * @param {number} fileId - File ID
     */
    showShareFileModal: function(fileId) {
        $('#shareFileId').val(fileId);

        const modal = new bootstrap.Modal(document.getElementById('shareFileModal'));
        modal.show();

        // Load shares and create first share if needed
        APP.loadFileShares(fileId);
    },

    /**
     * Load and display file shares
     *
     * @param {number} fileId - File ID
     */
    loadFileShares: function(fileId) {
        API.file.listShares(fileId)
            .done(function(shares) {
                if (shares.length === 0) {
                    // No shares yet, create one automatically
                    APP.createFileShare(fileId);
                } else {
                    // Display existing shares
                    APP.renderSharesList(fileId, shares);
                }
            })
            .fail(function(error) {
                APP.showAlert('Failed to load shares', 'error');
                console.error('Error loading shares:', error);
            });
    },

    /**
     * Create a new file share
     *
     * @param {number} fileId - File ID
     */
    createFileShare: function(fileId) {
        API.file.createShare(fileId, {})
            .done(function(share) {
                // Display the share link
                const shareUrl = API.file.getShareDownloadUrl(share.token);
                $('#shareLinkInput').val(shareUrl);

                // Load and display all shares
                API.file.listShares(fileId)
                    .done(function(shares) {
                        APP.renderSharesList(fileId, shares);
                    });
            })
            .fail(function(error) {
                APP.showAlert('Failed to create share', 'error');
                console.error('Error creating share:', error);
            });
    },

    /**
     * Render the list of shares
     *
     * @param {number} fileId - File ID
     * @param {Array} shares - Array of share objects
     */
    renderSharesList: function(fileId, shares) {
        let html = '';

        if (shares.length === 0) {
            html = '<p class="text-muted">No shares yet</p>';
        } else {
            html = '<div class="list-group">';
            shares.forEach(share => {
                const shareUrl = API.file.getShareDownloadUrl(share.token);
                const createdDate = new Date(share.created_at).toLocaleDateString();
                const expiresInfo = share.expires_at
                    ? `<small class="text-warning">Expires: ${new Date(share.expires_at).toLocaleDateString()}</small>`
                    : '<small class="text-success">Never expires</small>';

                html += `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <small class="text-muted">Created: ${createdDate}</small><br>
                            ${expiresInfo}
                        </div>
                        <button class="btn btn-outline-secondary copy-existing-share-btn" type="button" data-share-url="${shareUrl}">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                        <button class="btn btn-sm btn-danger delete-share-btn" data-share-id="${share.id}">
                            <i class="fas fa-trash"></i> Revoke
                        </button>
                    </div>
                `;
            });
            html += '</div>';
        }

        $('#sharesList').html(html);

        // Attach delete share handlers
        $('.delete-share-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const shareId = $(this).data('share-id');
            APP.deleteFileShare(shareId, fileId);
        });
        // Attach copy existing share url handlers
        $('.copy-existing-share-btn').off('click').on('click', function(e) {
            e.stopPropagation();
            const shareUrl = $(this).data('share-url');
            if (shareUrl) {
                navigator.clipboard.writeText(shareUrl).then(function() {
                    APP.showAlert('Share link copied to clipboard!', 'success');
                }).catch(function(error) {
                    APP.showAlert('Failed to copy to clipboard', 'error');
                    console.error('Copy error:', error);
                });
            }
        });
    },

    /**
     * Delete a file share
     *
     * @param {number} shareId - Share ID
     * @param {number} fileId - File ID (for reloading shares)
     */
    deleteFileShare: function(shareId, fileId) {
        API.file.deleteShare(shareId)
            .done(function() {
                APP.showAlert('Share deleted successfully!', 'success');
                // Reload shares list
                APP.loadFileShares(fileId);
            })
            .fail(function(error) {
                APP.showAlert('Failed to delete share', 'error');
                console.error('Error deleting share:', error);
            });
    },

    /**
     * Delete a data room
     */
    deleteDataRoom: function(dataroomId) {
        Swal.fire({
            title: 'Delete Data Room?',
            text: 'All folders and files will be deleted. This action cannot be undone.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Yes, delete'
        }).then((result) => {
            if (result.isConfirmed) {
                API.dataroom.delete(dataroomId)
                    .done(function() {
                        APP.showAlert('Data room deleted successfully!', 'success');
                        APP.loadDataRooms();
                        $('#contentArea').html('<div class="alert alert-info"><i class="fas fa-arrow-left"></i> Select a Data Room to get started</div>');
                    })
                    .fail(function(error) {
                        console.error('Error deleting data room:', error);
                        APP.showAlert('Failed to delete data room', 'error');
                    });
            }
        });
    },
};

// Attach event handlers for share modal
$(document).ready(function() {
    // Copy share link to clipboard
    $('#copyShareLinkBtn').off('click').on('click', function() {
        const shareUrl = $('#shareLinkInput').val();
        if (shareUrl) {
            navigator.clipboard.writeText(shareUrl).then(function() {
                APP.showAlert('Share link copied to clipboard!', 'success');
            }).catch(function(error) {
                APP.showAlert('Failed to copy to clipboard', 'error');
                console.error('Copy error:', error);
            });
        }
    });

    // Create new share button in modal
    $('#createNewShareBtn').off('click').on('click', function() {
        const fileId = $('#shareFileId').val();
        APP.createFileShare(fileId);
    });
});

// Initialize the app when DOM is ready
$(document).ready(function() {
    if (!AUTH_HELPER.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    // Initialize the app
    APP.init();
});

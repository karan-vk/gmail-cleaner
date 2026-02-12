/**
 * Gmail Unsubscribe - UI Utilities Module
 */

window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.UI = {
    setupNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                this.showView(view);
            });
        });
    },

    showView(viewName) {
        GmailCleaner.currentView = viewName;

        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.add('hidden');
        });

        // Show requested view
        const viewId = viewName + 'View';
        const view = document.getElementById(viewId);
        if (view) {
            view.classList.remove('hidden');
        }

        // Update nav active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === viewName) {
                item.classList.add('active');
            }
        });

        // Special handling for unsubscribe view
        if (viewName === 'unsubscribe') {
            if (GmailCleaner.results.length === 0) {
                document.getElementById('noResults').classList.remove('hidden');
                document.getElementById('resultsSection').classList.add('hidden');
            } else {
                document.getElementById('noResults').classList.add('hidden');
                document.getElementById('resultsSection').classList.remove('hidden');
            }
        }

        // Refresh unread count when switching to Mark Read view
        if (viewName === 'markread') {
            GmailCleaner.MarkRead.refreshUnreadCount();
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    },

    // Format bytes to human-readable size
    formatSize(bytes) {
        if (!bytes || bytes === 0) return '';
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        return size.toFixed(unitIndex > 0 ? 1 : 0) + ' ' + units[unitIndex];
    },

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    },

    // Toast notification system - Delegates to Notifications module
    showToast(message, type = 'success', duration = 5000, tip = null) {
        if (window.Notifications) {
            // Map types if necessary, but they match (success, error, info, warning)
            // If tip is provided, append it to message
            const fullMessage = tip ? `<strong>${message}</strong><br>${tip}` : message;
            
            if (type === 'error') {
                Notifications.error(fullMessage, duration);
            } else if (type === 'success') {
                Notifications.success(fullMessage, duration);
            } else if (type === 'warning') {
                Notifications.warning(fullMessage, duration);
            } else {
                Notifications.info(fullMessage, duration);
            }
        } else {
            console.warn('Notifications module not loaded, falling back to console');
            console.log(`[${type}] ${message}`);
        }
    },

    // Convenience methods
    showSuccessToast(message, tip = null) {
        this.showToast(message, 'success', 5000, tip);
    },

    showErrorToast(message) {
        this.showToast(message, 'error', 6000);
    },

    showInfoToast(message) {
        this.showToast(message, 'info', 4000);
    }
};

// Global shortcuts
function showView(viewName) { GmailCleaner.UI.showView(viewName); }
function toggleSidebar() { GmailCleaner.UI.toggleSidebar(); }
function showToast(message, type, duration, tip) { GmailCleaner.UI.showToast(message, type, duration, tip); }

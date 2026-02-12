/**
 * Gmail Unsubscribe - Authentication Module
 */

window.GmailCleaner = window.GmailCleaner || {};

GmailCleaner.Auth = {
    currentStep: 1,

    async checkStatus() {
        try {
            const webStatusResp = await fetch('/api/web-auth-status');
            if (!webStatusResp.ok) {
                throw new Error(`Web auth status check failed: ${webStatusResp.status}`);
            }
            const webStatus = await webStatusResp.json();

            if (webStatus.needs_setup && !webStatus.has_credentials) {
                GmailCleaner.UI.showView('setup');
                this.initSetupWizard();
                return;
            }

            const response = await fetch('/api/auth-status');
            if (!response.ok) {
                throw new Error(`Auth status check failed: ${response.status}`);
            }
            const status = await response.json();
            this.updateUI(status);
        } catch (error) {
            console.error('Error checking auth status:', error);
            GmailCleaner.UI.showView('login');
        }
    },

    initSetupWizard() {
        this.currentStep = 1;
        this.updateStepIndicators();
        this.setupDragAndDrop();
        this.resetUploadZone();
    },

    updateStepIndicators() {
        document.querySelectorAll('.setup-step-indicator').forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.remove('active', 'completed');
            if (stepNum < this.currentStep) {
                indicator.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                indicator.classList.add('active');
            }
        });

        document.querySelectorAll('.setup-step-line').forEach((line, index) => {
            line.classList.toggle('completed', index < this.currentStep - 1);
        });
    },

    goToStep(step) {
        this.currentStep = step;
        this.updateStepIndicators();

        document.querySelectorAll('.setup-step').forEach(s => s.classList.remove('active'));
        document.getElementById(`setupStep${step}`).classList.add('active');
    },

    setupDragAndDrop() {
        const uploadZone = document.getElementById('uploadZone');
        if (!uploadZone) return;

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.toLowerCase().endsWith('.json')) {
                    document.getElementById('credentialsFile').files = files;
                    this.handleFileSelect(document.getElementById('credentialsFile'));
                } else {
                    GmailCleaner.UI.showToast('Please select a valid JSON file', 'error');
                }
            }
        });
    },

    resetUploadZone() {
        const uploadZone = document.getElementById('uploadZone');
        const uploadSuccess = document.getElementById('uploadSuccess');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (uploadZone) uploadZone.classList.remove('hidden');
        if (uploadSuccess) uploadSuccess.classList.add('hidden');
        if (uploadBtn) uploadBtn.disabled = true;
    },

    handleFileSelect(input) {
        const file = input.files[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.json')) {
            GmailCleaner.UI.showToast('Please select a valid JSON file', 'error');
            input.value = '';
            return;
        }

        document.getElementById('uploadedFileName').textContent = file.name;
        document.getElementById('uploadZone').classList.add('hidden');
        document.getElementById('uploadSuccess').classList.remove('hidden');
        document.getElementById('uploadBtn').disabled = false;
    },

    async uploadCredentials() {
        const input = document.getElementById('credentialsFile');
        const file = input.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        const btn = document.getElementById('uploadBtn');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" width="20" height="20" class="spinner">
                <path fill="currentColor" d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8z"/>
            </svg>
            Uploading...
        `;

        try {
            const response = await fetch('/api/setup', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            GmailCleaner.UI.showToast('Credentials uploaded successfully!', 'success');
            this.goToStep(3);
        } catch (error) {
            GmailCleaner.UI.showToast('Error: ' + error.message, 'error');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    },

    async signInFromSetup() {
        const signInBtn = document.querySelector('.btn-google');
        if (signInBtn) {
            signInBtn.disabled = true;
            signInBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="20" height="20" class="spinner">
                    <path fill="currentColor" d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8z"/>
                </svg>
                Signing in...
            `;
        }

        try {
            const signInResp = await fetch('/api/sign-in', { method: 'POST' });
            const signInResult = await signInResp.json();

            if (signInResult.error) {
                this.resetSetupSignInButton();
                GmailCleaner.UI.showToast('Sign-in error: ' + signInResult.error, 'error');
                return;
            }

            this.pollStatusFromSetup();
        } catch (error) {
            GmailCleaner.UI.showToast('Error signing in: ' + error.message, 'error');
            this.resetSetupSignInButton();
        }
    },

    async pollStatusFromSetup(attempts = 0) {
        const maxAttempts = 120;

        try {
            const response = await fetch('/api/auth-status');
            const status = await response.json();

            if (status.logged_in) {
                this.updateUI(status);
                GmailCleaner.UI.showToast('Successfully signed in!', 'success');
            } else if (attempts < maxAttempts) {
                setTimeout(() => this.pollStatusFromSetup(attempts + 1), 1000);
            } else {
                this.resetSetupSignInButton();
                GmailCleaner.UI.showToast('Sign-in timed out. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error polling auth status:', error);
            setTimeout(() => this.pollStatusFromSetup(attempts + 1), 1000);
        }
    },

    resetSetupSignInButton() {
        const signInBtn = document.querySelector('.btn-google');
        if (signInBtn) {
            signInBtn.disabled = false;
            signInBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2 12.545,2C7.021,2 2.543,6.477 2.543,12s4.478 10 10.002,10c8.396,0 10.249-7.85 9.426-11.748L12.545,10.239z"/>
                </svg>
                Sign in with Google
            `;
        }
    },

    updateUI(authStatus) {
        const userSection = document.getElementById('userSection');

        if (authStatus.logged_in && authStatus.email) {
            const safeEmail = GmailCleaner.UI.escapeHtml(authStatus.email);
            const initial = authStatus.email.charAt(0).toUpperCase();
            userSection.innerHTML = `
                <span class="user-email">${safeEmail}</span>
                <div class="user-avatar" onclick="GmailCleaner.Auth.showUserMenu()" title="${safeEmail}">${initial}</div>
                <button class="btn btn-sm btn-secondary" onclick="GmailCleaner.Auth.signOut()">Sign Out</button>
            `;
            GmailCleaner.Filters.showBar(true);
            GmailCleaner.UI.showView('unsubscribe');

            this.loadLabelsForFilter();
        } else {
            userSection.innerHTML = '';
            GmailCleaner.Filters.showBar(false);
            GmailCleaner.UI.showView('login');
        }
    },

    async loadLabelsForFilter() {
        try {
            const labels = await GmailCleaner.Labels.loadLabels();
            if (labels && labels.user) {
                GmailCleaner.Filters.populateLabelDropdown(labels.user);
            }
        } catch (error) {
            console.error('Error loading labels for filter:', error);
        }
    },

    async signIn() {
        const signInBtn = document.getElementById('signInBtn');

        if (signInBtn) {
            signInBtn.disabled = true;
            signInBtn.innerHTML = '<span>Signing in...</span>';
        }

        try {
            const statusResp = await fetch('/api/web-auth-status');
            const status = await statusResp.json();

            if (!status.has_credentials) {
                this.resetSignInButton();
                GmailCleaner.UI.showView('setup');
                this.initSetupWizard();
                return;
            }

            if (status.web_auth_mode) {
                const msg = `Docker detected! To sign in:

1. Check Docker logs for the authorization URL:
   docker logs cleanup_email-gmail-cleaner-1

2. Copy the URL and open it in your browser

3. After authorizing, you'll be signed in automatically.

(Or generate token.json locally and mount it)`;
                alert(msg);
            }

            const signInResp = await fetch('/api/sign-in', { method: 'POST' });
            const signInResult = await signInResp.json();

            if (signInResult.error) {
                this.resetSignInButton();
                alert('Sign-in error: ' + signInResult.error);
                return;
            }

            this.pollStatus();
        } catch (error) {
            alert('Error signing in: ' + error.message);
            this.resetSignInButton();
        }
    },

    async pollStatus(attempts = 0) {
        const maxAttempts = 120;
        const signInBtn = document.getElementById('signInBtn');

        try {
            const response = await fetch('/api/auth-status');
            const status = await response.json();

            if (status.logged_in) {
                this.updateUI(status);
            } else if (attempts < maxAttempts) {
                setTimeout(() => this.pollStatus(attempts + 1), 1000);
            } else {
                this.resetSignInButton();
                alert('Sign-in timed out. Please try again.');
            }
        } catch (error) {
            console.error('Error polling auth status:', error);
            setTimeout(() => this.pollStatus(attempts + 1), 1000);
        }
    },

    resetSignInButton() {
        const signInBtn = document.getElementById('signInBtn');
        if (signInBtn) {
            signInBtn.disabled = false;
            signInBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20">
                <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2 12.545,2C7.021,2 2.543,6.477 2.543,12s4.478 10 10.002,10c8.396,0 10.249-7.85 9.426-11.748L12.545,10.239z"/>
            </svg>
            Sign in with Google`;
        }
    },

    async checkWebAuthMode() {
        return;
    },

    async signOut() {
        if (!confirm('Sign out of your Gmail account?')) return;

        try {
            await fetch('/api/sign-out', { method: 'POST' });
            GmailCleaner.results = [];
            GmailCleaner.Scanner.updateResultsBadge();
            GmailCleaner.Scanner.displayResults();
            document.getElementById('selectAll').checked = false;
            this.checkStatus();
        } catch (error) {
            alert('Error signing out: ' + error.message);
        }
    },

    showUserMenu() {
        console.log('User menu clicked');
    }
};

function signIn() { GmailCleaner.Auth.signIn(); }
function signOut() { GmailCleaner.Auth.signOut(); }

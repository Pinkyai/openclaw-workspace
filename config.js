// Configuration Panel JavaScript

// API Key Configuration Management
class ConfigManager {
    constructor() {
        this.config = this.loadConfig();
        this.initializeForm();
        this.bindEvents();
    }

    loadConfig() {
        // Load from localStorage or use defaults
        const saved = localStorage.getItem('pinky-config');
        return saved ? JSON.parse(saved) : this.getDefaultConfig();
    }

    getDefaultConfig() {
        return {
            apiKeys: {
                claude: '',
                openai: '',
                kimi: ''
            },
            settings: {
                defaultModel: 'claude-3-haiku-20240307',
                thinkingMode: 'off',
                autoGit: true,
                heartbeatChecks: true,
                logLevel: 'info'
            }
        };
    }

    initializeForm() {
        // Populate form with current config
        document.getElementById('claude-key').value = this.config.apiKeys.claude;
        document.getElementById('openai-key').value = this.config.apiKeys.openai;
        document.getElementById('kimi-key').value = this.config.apiKeys.kimi;
        document.getElementById('default-model').value = this.config.settings.defaultModel;
        document.getElementById('thinking-mode').value = this.config.settings.thinkingMode;
        document.getElementById('auto-git').checked = this.config.settings.autoGit;
        document.getElementById('heartbeat-checks').checked = this.config.settings.heartbeatChecks;
        document.getElementById('log-level').value = this.config.settings.logLevel;
    }

    bindEvents() {
        // Save configuration
        document.querySelector('.save-button').addEventListener('click', () => this.saveConfig());
        
        // Test API keys
        document.querySelector('.test-button').addEventListener('click', () => this.testAPIs());
        
        // Reset configuration
        document.querySelector('.reset-button').addEventListener('click', () => this.resetConfig());

        // Auto-save on form changes
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => this.autoSave());
        });
    }

    saveConfig() {
        try {
            // Collect form data
            this.config.apiKeys.claude = document.getElementById('claude-key').value;
            this.config.apiKeys.openai = document.getElementById('openai-key').value;
            this.config.apiKeys.kimi = document.getElementById('kimi-key').value;
            this.config.settings.defaultModel = document.getElementById('default-model').value;
            this.config.settings.thinkingMode = document.getElementById('thinking-mode').value;
            this.config.settings.autoGit = document.getElementById('auto-git').checked;
            this.config.settings.heartbeatChecks = document.getElementById('heartbeat-checks').checked;
            this.config.settings.logLevel = document.getElementById('log-level').value;

            // Save to localStorage
            localStorage.setItem('pinky-config', JSON.stringify(this.config));

            // Apply configuration immediately
            this.applyConfig();

            this.showStatus('Configuration saved successfully!', 'success');
        } catch (error) {
            this.showStatus('Error saving configuration: ' + error.message, 'error');
        }
    }

    autoSave() {
        // Auto-save with debounce
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveConfig();
        }, 1000);
    }

    applyConfig() {
        // Apply configuration to the system
        console.log('Applying configuration:', this.config);
        
        // Here you would typically:
        // 1. Update environment variables
        // 2. Restart services if needed
        // 3. Update running configuration
        
        // For now, just log the changes
        if (this.config.apiKeys.claude) {
            console.log('Claude API key updated');
        }
        if (this.config.apiKeys.openai) {
            console.log('OpenAI API key updated');
        }
        if (this.config.apiKeys.kimi) {
            console.log('Kimi API key updated');
        }
    }

    async testAPIs() {
        this.showStatus('Testing API keys...', 'warning');
        
        const results = [];
        
        // Test Claude API
        if (this.config.apiKeys.claude) {
            try {
                // Simple API test - would need actual implementation
                results.push({ service: 'Claude', status: 'key configured' });
            } catch (error) {
                results.push({ service: 'Claude', status: 'error', error: error.message });
            }
        }

        // Test OpenAI API
        if (this.config.apiKeys.openai) {
            try {
                results.push({ service: 'OpenAI', status: 'key configured' });
            } catch (error) {
                results.push({ service: 'OpenAI', status: 'error', error: error.message });
            }
        }

        // Test Kimi API
        if (this.config.apiKeys.kimi) {
            try {
                results.push({ service: 'Kimi', status: 'key configured' });
            } catch (error) {
                results.push({ service: 'Kimi', status: 'error', error: error.message });
            }
        }

        // Display results
        const successCount = results.filter(r => r.status === 'key configured').length;
        const message = `API Test Results: ${successCount}/${results.length} keys configured successfully`;
        
        this.showStatus(message, successCount === results.length ? 'success' : 'warning');
    }

    resetConfig() {
        if (confirm('Are you sure you want to reset all settings to default? This will clear all API keys.')) {
            this.config = this.getDefaultConfig();
            this.initializeForm();
            this.saveConfig();
            this.showStatus('Configuration reset to default values', 'success');
        }
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.className = `status-message ${type}`;
        statusEl.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Utility functions
function toggleVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '🙈';
    } else {
        input.type = 'password';
        button.textContent = '👁';
    }
}

// Initialize the configuration manager
document.addEventListener('DOMContentLoaded', () => {
    new ConfigManager();
});
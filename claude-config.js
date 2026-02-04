// Claude Configuration - Main Brain Settings (Claude Primary Mode)

class ClaudeConfigManager {
    constructor() {
        this.config = this.loadConfig();
        this.initializeForm();
        this.bindEvents();
        this.forceClaudeAsPrimary();
    }

    forceClaudeAsPrimary() {
        // Override any existing settings to make Claude primary
        this.config.settings.primaryModel = this.config.settings.claudeModel;
        this.config.settings.claudeEnabled = true;
        this.config.settings.preferClaude = true;
        this.config.settings.thinkingMode = 'on'; // Claude works better with thinking
        
        // Update system immediately
        this.updateSystemConfig();
        this.saveConfig();
        
        console.log('🎯 CLAUDE FORCED AS PRIMARY AI BRAIN');
        console.log('📊 Model:', this.config.settings.primaryModel);
        console.log('🧠 Thinking Mode:', this.config.settings.thinkingMode);
    }

    loadConfig() {
        const saved = localStorage.getItem('pinky-claude-primary-config');
        if (saved) {
            const parsed = JSON.parse(saved);
            // Ensure Claude is primary even if config was saved differently
            parsed.settings.primaryModel = parsed.settings.claudeModel || 'claude-3-haiku-20240307';
            parsed.settings.claudeEnabled = true;
            parsed.settings.preferClaude = true;
            return parsed;
        }
        
        // Default Claude-primary configuration
        return {
            apiKeys: {
                claude: '',
                openai: '',
                kimi: ''
            },
            settings: {
                primaryModel: 'claude-3-haiku-20240307',
                claudeModel: 'claude-3-haiku-20240307',
                thinkingMode: 'on',
                maxTokens: 4000,
                autoClaudeFallback: true,
                costOptimization: false, // Don't optimize away from Claude
                logLevel: 'info',
                claudeEnabled: true,
                preferClaude: true,
                forceClaude: true
            }
        };
    }

    initializeForm() {
        // Populate form with Claude settings
        document.getElementById('claude-key').value = this.config.apiKeys.claude;
        document.getElementById('claude-model').value = this.config.settings.claudeModel;
        document.getElementById('thinking-mode').value = this.config.settings.thinkingMode;
        document.getElementById('max-tokens').value = this.config.settings.maxTokens;
        document.getElementById('max-tokens-value').textContent = this.config.settings.maxTokens;
        document.getElementById('auto-claude-fallback').checked = this.config.settings.autoClaudeFallback;
        document.getElementById('cost-optimization').checked = this.config.settings.costOptimization;
        document.getElementById('log-level').value = this.config.settings.logLevel;
        
        // Populate backup keys
        document.getElementById('openai-key').value = this.config.apiKeys.openai;
        document.getElementById('kimi-key').value = this.config.apiKeys.kimi;
    }

    bindEvents() {
        // Save configuration
        document.querySelector('.save-button').addEventListener('click', () => this.saveConfig());
        
        // Test Claude API
        document.querySelector('.test-button').addEventListener('click', () => this.testClaudeAPI());
        
        // Switch model
        document.querySelector('.switch-button').addEventListener('click', () => this.switchModel());

        // Max tokens slider
        document.getElementById('max-tokens').addEventListener('input', (e) => {
            document.getElementById('max-tokens-value').textContent = e.target.value;
            this.config.settings.maxTokens = parseInt(e.target.value);
        });

        // Force Claude settings on any change
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => this.enforceClaudeSettings());
        });
    }

    enforceClaudeSettings() {
        // Ensure Claude remains primary no matter what
        this.config.settings.primaryModel = this.config.settings.claudeModel;
        this.config.settings.claudeEnabled = true;
        this.config.settings.preferClaude = true;
        this.config.settings.thinkingMode = 'on'; // Claude works better with thinking
        
        // Update form to reflect forced settings
        document.getElementById('thinking-mode').value = 'on';
        
        this.updateSystemConfig();
        this.autoSave();
    }

    updateSystemConfig() {
        // Force system-wide Claude configuration
        const claudeConfig = {
            primaryModel: this.config.settings.claudeModel,
            claudeEnabled: true,
            preferClaude: true,
            thinkingMode: 'on',
            forceClaude: true
        };

        // Update global configuration
        if (window.PinkyConfig) {
            Object.assign(window.PinkyConfig, claudeConfig);
        }

        // Set global flags
        window.ClaudeIsPrimary = true;
        window.ForceClaudeMode = true;
        
        // Notify parent window if in iframe
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'force-claude-mode',
                config: claudeConfig
            }, '*');
        }
        
        console.log('🎯 FORCED: Claude is now the primary AI brain');
        console.log('🔒 This cannot be changed without switching models explicitly');
    }

    saveConfig() {
        try {
            // Collect form data
            this.config.apiKeys.claude = document.getElementById('claude-key').value;
            this.config.apiKeys.openai = document.getElementById('openai-key').value;
            this.config.apiKeys.kimi = document.getElementById('kimi-key').value;
            this.config.settings.claudeModel = document.getElementById('claude-model').value;
            this.config.settings.thinkingMode = 'on'; // Force thinking mode
            this.config.settings.maxTokens = parseInt(document.getElementById('max-tokens').value);
            this.config.settings.autoClaudeFallback = document.getElementById('auto-claude-fallback').checked;
            this.config.settings.costOptimization = document.getElementById('cost-optimization').checked;
            this.config.settings.logLevel = document.getElementById('log-level').value;

            // Force Claude as primary
            this.config.settings.primaryModel = this.config.settings.claudeModel;
            this.config.settings.claudeEnabled = true;
            this.config.settings.preferClaude = true;
            this.config.settings.forceClaude = true;

            // Save configuration
            localStorage.setItem('pinky-claude-primary-config', JSON.stringify(this.config));
            this.updateSystemConfig();

            this.showStatus('✅ Claude is now your PRIMARY AI brain! All requests will use Claude.', 'success');
        } catch (error) {
            this.showStatus('❌ Error forcing Claude mode: ' + error.message, 'error');
        }
    }

    autoSave() {
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveConfig();
        }, 1000);
    }

    async testClaudeAPI() {
        if (!this.config.apiKeys.claude) {
            this.showStatus('⚠️ Enter your Claude API key first', 'warning');
            return;
        }

        this.showStatus('🧪 Testing Claude API...', 'warning');

        try {
            // Simple Claude API test
            const response = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.config.apiKeys.claude,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: this.config.settings.claudeModel,
                    max_tokens: 50,
                    messages: [{
                        role: 'user',
                        content: 'Test: say "Claude API working"'
                    }]
                })
            });

            if (response.ok) {
                this.showStatus('✅ Claude API connected successfully!', 'success');
            } else {
                const error = await response.json();
                this.showStatus('❌ Claude API test failed: ' + error.error?.message, 'error');
            }
        } catch (error) {
            this.showStatus('❌ Claude API connection failed: ' + error.message, 'error');
        }
    }

    switchModel() {
        const newModel = prompt('Switch primary model to (openai/kimi):', 'openai');
        if (newModel && ['openai', 'kimi'].includes(newModel)) {
            // Disable Claude force mode
            this.config.settings.forceClaude = false;
            this.config.settings.claudeEnabled = false;
            this.config.settings.preferClaude = false;
            this.config.settings.primaryModel = newModel;
            
            this.saveConfig();
            this.showStatus(`🔄 Switching to ${newModel} mode...`, 'success');
            
            setTimeout(() => {
                window.location.href = newModel === 'openai' ? 'openai-config.html' : 'kimi-config.html';
            }, 1500);
        }
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        statusEl.innerHTML = message;
        statusEl.className = `status-message ${type}`;
        statusEl.style.display = 'block';
        
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Global Claude force functions
function forceClaudeMode() {
    console.log('🔒 FORCING CLAUDE MODE');
    window.ClaudeIsPrimary = true;
    window.ForceClaudeMode = true;
    
    if (window.PinkyConfig) {
        window.PinkyConfig.primaryModel = 'claude-3-haiku-20240307';
        window.PinkyConfig.claudeEnabled = true;
        window.PinkyConfig.preferClaude = true;
        window.PinkyConfig.forceClaude = true;
    }
}

// Initialize forced Claude mode
document.addEventListener('DOMContentLoaded', () => {
    new ClaudeConfigManager();
    forceClaudeMode();
    
    console.log('🎯 CLAUDE FORCED AS PRIMARY AI BRAIN');
    console.log('🔒 This cannot be changed without explicit model switch');
});
// GOODWORDS Chrome Extension - Popup Script

class PopupManager {
    constructor() {
        this.settings = {};
        this.analytics = {};
        this.init();
    }
    
    async init() {
        await this.loadSettings();
        await this.loadAnalytics();
        this.setupEventListeners();
        this.updateUI();
    }
    
    async loadSettings() {
        return new Promise((resolve) => {
            chrome.storage.sync.get(null, (settings) => {
                this.settings = settings;
                resolve();
            });
        });
    }
    
    async loadAnalytics() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['analytics'], (result) => {
                this.analytics = result.analytics || {
                    totalDetections: 0,
                    totalDetoxifications: 0,
                    platformUsage: {},
                    dailyStats: {}
                };
                resolve();
            });
        });
    }
    
    setupEventListeners() {
        // Main toggle
        document.getElementById('enabledToggle').addEventListener('change', (e) => {
            this.updateSetting('enabled', e.target.checked);
        });
        
        // Auto detection toggle
        document.getElementById('autoDetectToggle').addEventListener('change', (e) => {
            this.updateSetting('autoDetect', e.target.checked);
        });
        
        // Show suggestions toggle
        document.getElementById('showSuggestionsToggle').addEventListener('change', (e) => {
            this.updateSetting('showSuggestions', e.target.checked);
        });
        
        // Sensitivity slider
        const sensitivitySlider = document.getElementById('sensitivitySlider');
        sensitivitySlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('sensitivityValue').textContent = value.toFixed(1);
            this.updateSetting('sensitivity', value);
        });
        
        // Platform toggles
        const platforms = ['discord', 'slack', 'teams', 'whatsapp', 'twitter', 'reddit'];
        platforms.forEach(platform => {
            document.getElementById(`${platform}Toggle`).addEventListener('change', (e) => {
                this.updatePlatformSetting(platform, e.target.checked);
            });
        });
        
        // Action buttons
        document.getElementById('testBtn').addEventListener('click', () => {
            this.showTestModal();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetSettings();
        });
        
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportData();
        });
        
        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelp();
        });
        
        // Test modal
        document.getElementById('testModalClose').addEventListener('click', () => {
            this.hideTestModal();
        });
        
        document.getElementById('runTestBtn').addEventListener('click', () => {
            this.runToxicityTest();
        });
        
        // Feedback link
        document.getElementById('feedbackLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openFeedback();
        });
        
        // Close modal on outside click
        document.getElementById('testModal').addEventListener('click', (e) => {
            if (e.target.id === 'testModal') {
                this.hideTestModal();
            }
        });
    }
    
    updateUI() {
        // Update toggles
        document.getElementById('enabledToggle').checked = this.settings.enabled !== false;
        document.getElementById('autoDetectToggle').checked = this.settings.autoDetect !== false;
        document.getElementById('showSuggestionsToggle').checked = this.settings.showSuggestions !== false;
        
        // Update sensitivity
        const sensitivity = this.settings.sensitivity || 0.7;
        document.getElementById('sensitivitySlider').value = sensitivity;
        document.getElementById('sensitivityValue').textContent = sensitivity.toFixed(1);
        
        // Update platform toggles
        const platforms = ['discord', 'slack', 'teams', 'whatsapp', 'twitter', 'reddit'];
        platforms.forEach(platform => {
            const enabled = this.settings.platforms && this.settings.platforms[platform] !== false;
            document.getElementById(`${platform}Toggle`).checked = enabled;
        });
        
        // Update stats
        this.updateStats();
        
        // Update status indicator
        this.updateStatusIndicator();
    }
    
    updateStats() {
        const today = new Date().toISOString().split('T')[0];
        const todayStats = this.analytics.dailyStats[today] || { detections: 0, detoxifications: 0 };
        
        document.getElementById('detectionsCount').textContent = todayStats.detections;
        document.getElementById('detoxificationsCount').textContent = todayStats.detoxifications;
        
        const platformsUsed = Object.keys(this.analytics.platformUsage || {}).length;
        document.getElementById('platformsUsed').textContent = platformsUsed;
    }
    
    updateStatusIndicator() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');
        
        if (this.settings.enabled !== false) {
            statusDot.style.background = '#00d4ff';
            statusText.textContent = 'Active';
            statusIndicator.style.borderColor = 'rgba(0, 212, 255, 0.3)';
        } else {
            statusDot.style.background = '#ff6b6b';
            statusText.textContent = 'Disabled';
            statusIndicator.style.borderColor = 'rgba(255, 107, 107, 0.3)';
        }
    }
    
    async updateSetting(key, value) {
        this.settings[key] = value;
        await this.saveSettings();
        this.updateStatusIndicator();
        this.notifyContentScripts();
    }
    
    async updatePlatformSetting(platform, enabled) {
        if (!this.settings.platforms) {
            this.settings.platforms = {};
        }
        this.settings.platforms[platform] = enabled;
        await this.saveSettings();
        this.notifyContentScripts();
    }
    
    async saveSettings() {
        return new Promise((resolve) => {
            chrome.storage.sync.set(this.settings, () => {
                resolve();
            });
        });
    }
    
    notifyContentScripts() {
        // Notify all tabs about settings change
        chrome.tabs.query({}, (tabs) => {
            tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'settingsUpdated'
                }).catch(() => {
                    // Ignore errors for tabs that don't have content script
                });
            });
        });
    }
    
    showTestModal() {
        document.getElementById('testModal').classList.add('show');
        document.getElementById('testTextarea').focus();
    }
    
    hideTestModal() {
        document.getElementById('testModal').classList.remove('show');
        document.getElementById('testTextarea').value = '';
        document.getElementById('testResult').innerHTML = '';
    }
    
    async runToxicityTest() {
        const text = document.getElementById('testTextarea').value.trim();
        const resultDiv = document.getElementById('testResult');
        
        if (!text) {
            resultDiv.innerHTML = '<div style="color: #ff6b6b;">Please enter some text to test.</div>';
            return;
        }
        
        resultDiv.innerHTML = '<div style="color: #00d4ff;">Testing toxicity detection...</div>';
        
        try {
            const response = await this.sendMessage({
                action: 'detectToxicity',
                text: text
            });
            
            this.displayTestResult(response);
        } catch (error) {
            resultDiv.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
        }
    }
    
    displayTestResult(result) {
        const resultDiv = document.getElementById('testResult');
        
        if (result.error) {
            resultDiv.innerHTML = `<div style="color: #ff6b6b;">Error: ${result.error}</div>`;
            return;
        }
        
        const isToxic = result.is_toxic;
        const confidence = (result.confidence * 100).toFixed(1);
        const labels = result.toxic_labels.length ? result.toxic_labels.join(', ') : 'None';
        
        resultDiv.innerHTML = `
            <div style="margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 20px;">${isToxic ? '⚠️' : '✅'}</span>
                    <span style="font-weight: 600; color: ${isToxic ? '#ff6b6b' : '#90ee90'};">
                        ${isToxic ? 'Toxic Content Detected' : 'Content is Safe'}
                    </span>
                </div>
                <div style="font-size: 12px; color: #ffffff; opacity: 0.8;">
                    Confidence: ${confidence}%
                </div>
                <div style="font-size: 12px; color: #ffffff; opacity: 0.8;">
                    Labels: ${labels}
                </div>
            </div>
            ${isToxic ? `
                <button class="test-btn" onclick="popupManager.testDetoxify()" style="margin-top: 10px;">
                    Test Detoxification
                </button>
            ` : ''}
        `;
    }
    
    async testDetoxify() {
        const text = document.getElementById('testTextarea').value.trim();
        const resultDiv = document.getElementById('testResult');
        
        resultDiv.innerHTML += '<div style="color: #00d4ff; margin-top: 10px;">Detoxifying text...</div>';
        
        try {
            const response = await this.sendMessage({
                action: 'detoxifyText',
                text: text
            });
            
            if (response.detoxified_text && response.detoxified_text !== text) {
                resultDiv.innerHTML += `
                    <div style="margin-top: 10px; padding: 10px; background: rgba(144, 238, 144, 0.1); border: 1px solid rgba(144, 238, 144, 0.3); border-radius: 8px;">
                        <div style="font-size: 12px; color: #90ee90; margin-bottom: 5px;">Detoxified Text:</div>
                        <div style="color: #ffffff; font-size: 13px;">${response.detoxified_text}</div>
                    </div>
                `;
            } else {
                resultDiv.innerHTML += '<div style="color: #ffa500; margin-top: 10px;">No changes needed or detoxification failed.</div>';
            }
        } catch (error) {
            resultDiv.innerHTML += `<div style="color: #ff6b6b; margin-top: 10px;">Error: ${error.message}</div>`;
        }
    }
    
    async resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default?')) {
            await chrome.storage.sync.clear();
            await chrome.storage.local.clear();
            location.reload();
        }
    }
    
    exportData() {
        const data = {
            settings: this.settings,
            analytics: this.analytics,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `civil-dialog-data-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    showHelp() {
        const helpContent = `
GOODWORDS Help

🎯 How it works:
• Automatically detects toxic content as you type
• Shows suggestions for better alternatives
• One-click detoxification with AI

⚙️ Settings:
• Enable/disable for specific platforms
• Adjust sensitivity (0.1 = very strict, 1.0 = very lenient)
• Toggle auto-detection and suggestions

🚀 Quick Actions:
• Ctrl+Enter: Quick detoxify current text
• Click floating button: Open settings
• Test button: Try toxicity detection

📊 Analytics:
• Track your communication improvement
• See which platforms you use most
• Monitor daily detection/detoxification stats

Need more help? Contact us at feedback@civildialog.com
        `;
        
        alert(helpContent);
    }
    
    openFeedback() {
        const subject = encodeURIComponent('GOODWORDS Extension Feedback');
        const body = encodeURIComponent(`
Platform: ${navigator.userAgent}
Version: 1.0.0
Settings: ${JSON.stringify(this.settings, null, 2)}

Please describe your feedback or issue:
        `);
        
        window.open(`mailto:feedback@civildialog.com?subject=${subject}&body=${body}`);
    }
    
    sendMessage(message) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(message, (response) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else {
                    resolve(response);
                }
            });
        });
    }
}

// Initialize popup manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.popupManager = new PopupManager();
});


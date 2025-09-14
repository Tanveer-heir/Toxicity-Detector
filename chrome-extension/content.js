// Content script for GOODWORDS Chrome Extension
// Monitors text inputs across different platforms and provides toxicity detection

class GoodWordsMonitor {
  constructor() {
    this.settings = {};
    this.currentPlatform = this.detectPlatform();
    this.observedElements = new Set();
    this.toxicityOverlays = new Map();
    this.debounceTimers = new Map();
    
    this.init();
  }
  
  async init() {
    // Load settings
    await this.loadSettings();
    
    // Start monitoring if enabled
    if (this.settings.enabled && this.settings.platforms[this.currentPlatform]) {
      this.startMonitoring();
      this.createFloatingButton();
    }
    
    // Listen for settings changes
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'settingsUpdated') {
        this.loadSettings().then(() => {
          if (this.settings.enabled && this.settings.platforms[this.currentPlatform]) {
            this.startMonitoring();
          } else {
            this.stopMonitoring();
          }
        });
      }
    });
  }
  
  detectPlatform() {
    const hostname = window.location.hostname;
    if (hostname.includes('discord.com')) return 'discord';
    if (hostname.includes('slack.com')) return 'slack';
    if (hostname.includes('teams.microsoft.com')) return 'teams';
    if (hostname.includes('whatsapp.com')) return 'whatsapp';
    if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';
    if (hostname.includes('reddit.com')) return 'reddit';
    return 'unknown';
  }
  
  async loadSettings() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        this.settings = response || {};
        resolve();
      });
    });
  }
  
  startMonitoring() {
    // Monitor existing text inputs
    this.observeTextInputs();
    
    // Monitor for dynamically added inputs
    this.observeDOMChanges();
    
    // Add event listeners for real-time detection
    this.addInputListeners();
  }
  
  stopMonitoring() {
    // Remove all overlays
    this.toxicityOverlays.forEach(overlay => overlay.remove());
    this.toxicityOverlays.clear();
    
    // Remove floating button
    const floatingBtn = document.getElementById('civil-dialog-floating-btn');
    if (floatingBtn) floatingBtn.remove();
    
    // Clear debounce timers
    this.debounceTimers.forEach(timer => clearTimeout(timer));
    this.debounceTimers.clear();
  }
  
  observeTextInputs() {
    const selectors = this.getPlatformSelectors();
    
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        if (!this.observedElements.has(element)) {
          this.observedElements.add(element);
          this.setupElementMonitoring(element);
        }
      });
    });
  }
  
  getPlatformSelectors() {
    const selectors = {
      discord: [
        '[data-slate-editor="true"]',
        '[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        '.textArea-2CLwUE'
      ],
      slack: [
        '[data-qa="message_input"]',
        '[contenteditable="true"]',
        'textarea[placeholder*="message"]',
        '.ql-editor'
      ],
      teams: [
        '[data-tid="ckeditor-text-area"]',
        '[contenteditable="true"]',
        'textarea[placeholder*="Type a new message"]',
        '.cke_editable'
      ],
      whatsapp: [
        '[contenteditable="true"][data-tab="3"]',
        'div[contenteditable="true"]',
        '[data-testid="conversation-compose-box-input"]',
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][aria-label*="Type a message"]',
        'div[contenteditable="true"][title*="Type a message"]',
        '#main div[contenteditable="true"]',
        'div[contenteditable="true"][data-tab="10"]'
      ],
      twitter: [
        '[data-testid="tweetTextarea_0"]',
        '[contenteditable="true"]',
        'div[contenteditable="true"]',
        '[data-testid="tweetButtonInline"]'
      ],
      reddit: [
        '[data-test-id="post-content"]',
        '[contenteditable="true"]',
        'textarea[placeholder*="What are your thoughts"]',
        '.public-DraftEditor-content'
      ]
    };
    
    return selectors[this.currentPlatform] || ['[contenteditable="true"]', 'textarea', 'input[type="text"]'];
  }
  
  setupElementMonitoring(element) {
    // Add visual indicator
    element.style.position = 'relative';
    
    // Add event listeners
    element.addEventListener('input', (e) => this.handleInput(e));
    element.addEventListener('keydown', (e) => this.handleKeydown(e));
    element.addEventListener('blur', (e) => this.handleBlur(e));
  }
  
  observeDOMChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const selectors = this.getPlatformSelectors();
            selectors.forEach(selector => {
              const elements = node.querySelectorAll ? node.querySelectorAll(selector) : [];
              elements.forEach(element => {
                if (!this.observedElements.has(element)) {
                  this.observedElements.add(element);
                  this.setupElementMonitoring(element);
                }
              });
            });
          }
        });
      });
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  
  addInputListeners() {
    // Global listener for any text input
    document.addEventListener('input', (e) => {
      if (e.target.matches('[contenteditable="true"], textarea, input[type="text"]')) {
        this.handleInput(e);
      }
    });
    
    // Additional listener specifically for WhatsApp
    if (this.currentPlatform === 'whatsapp') {
      document.addEventListener('input', (e) => {
        // More aggressive detection for WhatsApp
        if (e.target.contentEditable === 'true' || e.target.tagName === 'DIV') {
          this.handleInput(e);
        }
      });
    }
  }
  
  handleInput(event) {
    const element = event.target;
    const text = this.getTextContent(element);
    
    if (!text || text.length < 3) {
      this.removeToxicityOverlay(element);
      return;
    }
    
    // Debounce the detection
    const timerKey = element;
    if (this.debounceTimers.has(timerKey)) {
      clearTimeout(this.debounceTimers.get(timerKey));
    }
    
    const timer = setTimeout(() => {
      this.detectToxicity(text, element);
    }, 500); // 500ms debounce
    
    this.debounceTimers.set(timerKey, timer);
  }
  
  handleKeydown(event) {
    // Handle Ctrl+Enter for quick detoxify
    if (event.ctrlKey && event.key === 'Enter') {
      const element = event.target;
      const text = this.getTextContent(element);
      
      if (text) {
        event.preventDefault();
        this.quickDetoxify(text, element);
      }
    }
  }
  
  handleBlur(event) {
    // Remove overlays when input loses focus
    setTimeout(() => {
      this.removeToxicityOverlay(event.target);
    }, 2000);
  }
  
  getTextContent(element) {
    if (element.contentEditable === 'true') {
      return element.innerText || element.textContent || '';
    }
    return element.value || '';
  }
  
  async detectToxicity(text, element) {
    try {
      console.log('GOODWORDS: Detecting toxicity for text:', text);
      const response = await this.sendMessage({
        action: 'detectToxicity',
        text: text
      });
      
      console.log('GOODWORDS: Detection response:', response);
      
      if (response.is_toxic && response.confidence >= this.settings.sensitivity) {
        console.log('GOODWORDS: Showing toxicity overlay');
        this.showToxicityOverlay(element, response);
        this.logAnalytics({ detections: 1, platform: this.currentPlatform });
      } else {
        this.removeToxicityOverlay(element);
      }
    } catch (error) {
      console.error('GOODWORDS: Toxicity detection error:', error);
    }
  }
  
  showToxicityOverlay(element, toxicityResult) {
    this.removeToxicityOverlay(element);
    
    const overlay = document.createElement('div');
    overlay.className = 'good-words-toxicity-overlay';
    overlay.innerHTML = `
      <div class="toxicity-warning">
        <div class="warning-icon">⚠️</div>
        <div class="warning-content">
          <div class="warning-title">Toxic content detected</div>
          <div class="warning-labels">${toxicityResult.toxic_labels.join(', ')}</div>
          <div class="warning-actions">
            <button class="detoxify-btn" data-text="${this.escapeHtml(this.getTextContent(element))}">
              ✨ Detoxify
            </button>
            <button class="dismiss-btn">✕</button>
          </div>
        </div>
      </div>
    `;
    
    // Position overlay
    const rect = element.getBoundingClientRect();
    overlay.style.position = 'absolute';
    overlay.style.top = `${rect.bottom + 5}px`;
    overlay.style.left = `${rect.left}px`;
    overlay.style.zIndex = '10000';
    
    // Better positioning for WhatsApp to avoid send button
    if (this.currentPlatform === 'whatsapp') {
      overlay.style.top = `${rect.top - 60}px`; // Above the input instead of below
      overlay.style.left = `${rect.left}px`;
      overlay.style.maxWidth = '300px';
    }
    
    // Add event listeners
    overlay.querySelector('.detoxify-btn').addEventListener('click', (e) => {
      const originalText = e.target.getAttribute('data-text');
      this.quickDetoxify(originalText, element);
      overlay.remove();
    });
    
    overlay.querySelector('.dismiss-btn').addEventListener('click', () => {
      overlay.remove();
    });
    
    // Add to page
    document.body.appendChild(overlay);
    this.toxicityOverlays.set(element, overlay);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (overlay.parentNode) {
        overlay.remove();
        this.toxicityOverlays.delete(element);
      }
    }, 10000);
  }
  
  removeToxicityOverlay(element) {
    const overlay = this.toxicityOverlays.get(element);
    if (overlay && overlay.parentNode) {
      overlay.remove();
      this.toxicityOverlays.delete(element);
    }
  }
  
  async quickDetoxify(text, element) {
    try {
      const response = await this.sendMessage({
        action: 'detoxifyText',
        text: text
      });
      
      if (response.detoxified_text && response.detoxified_text !== text) {
        this.setTextContent(element, response.detoxified_text);
        this.showSuccessMessage(element);
        this.logAnalytics({ detoxifications: 1, platform: this.currentPlatform });
      }
    } catch (error) {
      console.error('Detoxification error:', error);
    }
  }
  
  setTextContent(element, text) {
    if (element.contentEditable === 'true') {
      element.innerText = text;
      // Trigger input event to notify the platform
      element.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      element.value = text;
      element.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }
  
  showSuccessMessage(element) {
    const successMsg = document.createElement('div');
    successMsg.className = 'civil-dialog-success-message';
    successMsg.textContent = '✨ Message detoxified!';
    
    const rect = element.getBoundingClientRect();
    successMsg.style.position = 'absolute';
    successMsg.style.top = `${rect.top - 30}px`;
    successMsg.style.left = `${rect.left}px`;
    successMsg.style.zIndex = '10000';
    
    document.body.appendChild(successMsg);
    
    setTimeout(() => {
      if (successMsg.parentNode) {
        successMsg.remove();
      }
    }, 2000);
  }
  
  createFloatingButton() {
    // Remove existing button if it exists
    const existingBtn = document.getElementById('civil-dialog-floating-btn');
    if (existingBtn) {
      existingBtn.remove();
    }
    
    const button = document.createElement('div');
    button.id = 'civil-dialog-floating-btn';
    button.innerHTML = '💬';
    button.title = 'GOODWORDS - Toxicity Detector';
    
    // Better positioning for WhatsApp
    if (this.currentPlatform === 'whatsapp') {
      button.style.bottom = '80px'; // Above the message input
      button.style.right = '20px';
    }
    
    button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('GOODWORDS: Floating button clicked');
      
      // Test toxicity detection directly
      try {
        this.testToxicityDetection();
      } catch (error) {
        console.error('GOODWORDS: Error in button click:', error);
        // Show a simple alert if extension context is invalid
        alert('GOODWORDS: Extension needs to be reloaded. Please refresh the page.');
      }
    });
    
    // Add hover effect
    button.addEventListener('mouseenter', () => {
      button.style.transform = 'scale(1.1)';
    });
    
    button.addEventListener('mouseleave', () => {
      button.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(button);
  }
  
  sendMessage(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(response);
        }
      });
    });
  }
  
  logAnalytics(data) {
    chrome.runtime.sendMessage({
      action: 'logAnalytics',
      data: data
    });
  }
  
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  testToxicityDetection() {
    console.log('GOODWORDS: Testing toxicity detection...');
    this.detectToxicity('You are such an idiot and this is stupid', document.body);
  }
}

// Initialize the monitor when the page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new GoodWordsMonitor();
  });
} else {
  new GoodWordsMonitor();
}

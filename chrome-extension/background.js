// Background service worker for GOODWORDS Chrome Extension

// API endpoint configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Cache for toxicity detection results
const toxicityCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('GOODWORDS extension installed');
  
  // Set default settings
  chrome.storage.sync.set({
    enabled: true,
    autoDetect: true,
    showSuggestions: true,
    sensitivity: 0.7,
    platforms: {
      discord: true,
      slack: true,
      teams: true,
      whatsapp: true,
      twitter: true,
      reddit: true
    }
  });
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'detectToxicity':
      handleToxicityDetection(request.text, sendResponse);
      return true; // Keep message channel open for async response
      
    case 'detoxifyText':
      handleTextDetoxification(request.text, sendResponse);
      return true;
      
    case 'getSettings':
      chrome.storage.sync.get(null, (settings) => {
        sendResponse(settings);
      });
      return true;
      
    case 'updateSettings':
      chrome.storage.sync.set(request.settings, () => {
        sendResponse({success: true});
      });
      return true;
      
    case 'logAnalytics':
      logAnalytics(request.data);
      sendResponse({success: true});
      break;
  }
});

// Handle toxicity detection with caching
async function handleToxicityDetection(text, sendResponse) {
  try {
    // Check cache first
    const cacheKey = text.toLowerCase().trim();
    const cached = toxicityCache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      sendResponse(cached.result);
      return;
    }
    
    // Make API call
    const response = await fetch(`${API_BASE_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Cache the result
    toxicityCache.set(cacheKey, {
      result: result,
      timestamp: Date.now()
    });
    
    sendResponse(result);
    
  } catch (error) {
    console.error('Toxicity detection error:', error);
    sendResponse({
      is_toxic: false,
      confidence: 0,
      toxic_labels: [],
      scores: {},
      error: error.message
    });
  }
}

// Handle text detoxification
async function handleTextDetoxification(text, sendResponse) {
  try {
    const response = await fetch(`${API_BASE_URL}/detoxify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    sendResponse(result);
    
  } catch (error) {
    console.error('Text detoxification error:', error);
    sendResponse({
      detoxified_text: text, // Return original text if error
      error: error.message
    });
  }
}

// Log analytics data
function logAnalytics(data) {
  chrome.storage.local.get(['analytics'], (result) => {
    const analytics = result.analytics || {
      totalDetections: 0,
      totalDetoxifications: 0,
      platformUsage: {},
      dailyStats: {}
    };
    
    // Update analytics
    analytics.totalDetections += data.detections || 0;
    analytics.totalDetoxifications += data.detoxifications || 0;
    
    if (data.platform) {
      analytics.platformUsage[data.platform] = (analytics.platformUsage[data.platform] || 0) + 1;
    }
    
    const today = new Date().toISOString().split('T')[0];
    if (!analytics.dailyStats[today]) {
      analytics.dailyStats[today] = { detections: 0, detoxifications: 0 };
    }
    analytics.dailyStats[today].detections += data.detections || 0;
    analytics.dailyStats[today].detoxifications += data.detoxifications || 0;
    
    chrome.storage.local.set({ analytics });
  });
}

// Clean up old cache entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of toxicityCache.entries()) {
    if (now - value.timestamp > CACHE_DURATION) {
      toxicityCache.delete(key);
    }
  }
}, CACHE_DURATION);


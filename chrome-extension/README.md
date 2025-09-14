# GOODWORDS Chrome Extension

A powerful Chrome extension that transforms toxic messages into positive communication across multiple chat platforms in real-time.

## 🚀 Features

- **Universal Platform Support**: Works on Discord, Slack, Microsoft Teams, WhatsApp Web, Twitter, Reddit
- **Real-time Detection**: Analyzes messages as you type with AI-powered toxicity detection
- **One-tap Detoxify**: Single click to replace toxic text with polite alternatives
- **Smart Suggestions**: Context-aware alternative suggestions
- **Non-intrusive UI**: Subtle overlays that don't break existing interfaces
- **Privacy-focused**: All processing happens on your local backend
- **Analytics Dashboard**: Track your communication improvement over time

## 🛠️ Installation

### Prerequisites
1. **Backend Server**: Make sure your GOODWORDS backend is running on `http://localhost:8000`
2. **Chrome Browser**: Chrome 88+ with Manifest V3 support

### Setup Steps

1. **Load the Extension**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked" and select the `chrome-extension` folder

2. **Start Backend**:
   ```bash
   cd backend
   python app.py
   ```

3. **Configure Settings**:
   - Click the CivilDialog icon in your Chrome toolbar
   - Adjust sensitivity and platform settings as needed
   - Test the detection with the built-in test feature

## 🎯 Supported Platforms

- **Discord** (`discord.com`)
- **Slack** (`app.slack.com`)
- **Microsoft Teams** (`teams.microsoft.com`)
- **WhatsApp Web** (`web.whatsapp.com`)
- **Twitter/X** (`twitter.com`, `x.com`)
- **Reddit** (`reddit.com`, `www.reddit.com`)

## ⚙️ Configuration

### Settings Panel
- **Enable/Disable**: Toggle the extension on/off
- **Auto Detection**: Automatically detect toxic content as you type
- **Show Suggestions**: Display detoxification suggestions
- **Sensitivity**: Adjust detection strictness (0.1 = very strict, 1.0 = very lenient)
- **Platform Selection**: Enable/disable for specific platforms

### Quick Actions
- **Ctrl+Enter**: Quick detoxify current text
- **Floating Button**: Access settings from any page
- **Test Detection**: Try the toxicity detection with sample text

## 📊 Analytics

Track your communication improvement with built-in analytics:
- Daily detection and detoxification counts
- Platform usage statistics
- Communication pattern insights
- Export data for personal analysis

## 🔧 Development

### File Structure
```
chrome-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker for API communication
├── content.js            # Content script for platform monitoring
├── content.css           # Styles for overlays and UI elements
├── popup.html            # Settings popup interface
├── popup.css             # Popup styles
├── popup.js              # Popup functionality
├── icons/                # Extension icons
└── README.md             # This file
```

### Key Components

1. **Content Script** (`content.js`):
   - Monitors text inputs across platforms
   - Detects toxic content in real-time
   - Shows suggestion overlays
   - Handles one-tap detoxification

2. **Background Service Worker** (`background.js`):
   - Communicates with backend API
   - Manages caching and analytics
   - Handles settings storage

3. **Popup Interface** (`popup.html/js/css`):
   - Settings configuration
   - Analytics dashboard
   - Test functionality

## 🚨 Troubleshooting

### Common Issues

1. **Extension not working**:
   - Check if backend is running on `localhost:8000`
   - Verify extension is enabled in Chrome
   - Check browser console for errors

2. **Detection not triggering**:
   - Ensure platform is enabled in settings
   - Check sensitivity setting
   - Try the test feature to verify API connection

3. **Overlays not showing**:
   - Check if platform is supported
   - Verify content script is loaded
   - Try refreshing the page

### Debug Mode
- Open Chrome DevTools (F12)
- Check Console tab for error messages
- Use the test feature in popup to verify API connectivity

## 🔒 Privacy & Security

- **Local Processing**: All toxicity detection happens on your local backend
- **No Data Collection**: No personal messages are stored or transmitted
- **Open Source**: Full source code available for review
- **Minimal Permissions**: Only requests necessary permissions for functionality

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] Voice-to-text integration
- [ ] Advanced analytics and insights
- [ ] Team/group features
- [ ] Custom model training
- [ ] Mobile app companion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Feature Requests**: Submit via GitHub Discussions
- **Email**: feedback@civildialog.com

---

**Made with ❤️ for better online communication**


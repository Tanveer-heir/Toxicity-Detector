# Toxicity-Detector

An advanced AI-powered toxicity detection system with enhanced features for sarcasm detection, text normalization, and contextual analysis.

## 🚀 Enhanced Features (NEW)

This repository now includes advanced toxicity detection capabilities:

- **🎭 Sarcasm & Irony Detection**: Specialized detection for sarcastic and ironic content
- **📝 Text Normalization**: Handles emojis, slang, abbreviations, and spelling errors
- **🧠 Contextual Analysis**: Uses sequence labeling and contextual embeddings instead of bag-of-words
- **🔄 Multi-Task Learning**: Combines multiple analysis types for improved accuracy

See [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) for detailed documentation.

## Features

- Real-time toxicity detection using BERT-based models
- Text detoxification and content moderation
- Chrome extension for seamless integration
- Web interface for easy testing
- Enhanced normalization and contextual understanding
- Sarcasm and irony detection capabilities
- RESTful API with comprehensive endpoints

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

### Testing Enhanced Features

Test the new enhanced features:
```bash
python test_enhanced_features.py
```

Test the API endpoints:
```bash
python test_api.py
```

## API Endpoints

### Enhanced Detection
- `POST /api/detect` - Enhanced toxicity detection with sarcasm and normalization
- `POST /api/normalize` - Text normalization (emojis, slang, spelling)
- `POST /api/detect_sarcasm` - Sarcasm and irony detection
- `POST /api/analyze_context` - Contextual analysis with sequence labeling
- `GET /api/health` - System health and feature availability

### Original Endpoints
- `POST /api/detoxify` - Text detoxification
- `POST /api/ask` - Model information

## Technology Stack

- **Backend**: Flask, PyTorch, Transformers
- **Models**: 
  - `unitary/toxic-bert` for base toxicity detection
  - `s-nlp/mt0-xl-detox-mpd` for text detoxification
  - Custom sarcasm detection and text normalization
- **Frontend**: HTML, CSS, JavaScript
- **Extension**: Chrome Extension Manifest V3

## Enhanced Architecture

The system now uses a multi-task learning approach:

1. **Text Normalization**: Converts informal text to standard form
2. **Sarcasm Detection**: Identifies sarcastic and ironic content
3. **Contextual Analysis**: Token-level analysis with sequence labeling
4. **Score Aggregation**: Weighted combination of all analysis types

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details.